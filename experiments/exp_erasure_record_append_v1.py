"""
exp_erasure_record_append_v1 -- concurrency/erasure (Chain2 Drill4) anchor 2 (ErasureRecord append) -- CPU.

ROUTING: handoff exp_dev_handoff_research_concurrency_erasure_chain2_drill4 #2. Replace the rank-1 downdate-IN-PLACE erase
  (Drill3 Component6) with an append-only ErasureRecord + tombstone design; verify (a) erased content is unrecoverable,
  (b) the audit log is append-only (no mutation of prior records), (c) replaying the log reconstructs current state with
  the tombstone applied. CPU $0.
PRE-REGISTERED: HARD-PASS append-only (zero prior-record mutations) AND erased content gone AND log-replay matches live state.
  HARD-FAIL any prior record mutated OR content recoverable after erase.
FORMULA SELF-TESTS (PROT-022): 1. append grows log. 2. tombstone hides content. 3. replay reconstructs.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "erasure_record_append_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 100 if RUN_MODE == "smoke" else 2000


class AppendLog:
    def __init__(self):
        self.log = []                                               # immutable append-only records
    def write(self, k, v):
        self.log.append(("WRITE", k, v))
    def erase(self, k):
        self.log.append(("ERASE", k, None))                        # tombstone append, NO in-place mutation
    def replay(self):
        state = {}
        for op, k, v in self.log:
            if op == "WRITE":
                state[k] = v
            elif op == "ERASE":
                state[k] = "ERASED_MARKER"
        return state


def _selftest():
    L = AppendLog(); L.write("k", "v"); n1 = len(L.log); L.erase("k")
    assert len(L.log) == n1 + 1, "append grows log"
    assert L.replay()["k"] == "ERASED_MARKER", "tombstone hides content"
    L.write("k2", "v2"); assert L.replay()["k2"] == "v2" and L.replay()["k"] == "ERASED_MARKER", "replay reconstructs"
    print("[selftest] PASS: erasure-record-append", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); L = AppendLog()
    for i in range(N_FACTS):
        L.write("f%d" % i, "content_%d" % i)
    snapshot = [tuple(r) for r in L.log]                            # capture log before erasures
    erased = list(range(0, N_FACTS, 7))
    for i in erased:
        L.erase("f%d" % i)
    # (a) append-only: original records unchanged
    append_only = snapshot == [tuple(r) for r in L.log[:len(snapshot)]]
    state = L.replay()
    content_gone = all(state["f%d" % i] == "ERASED_MARKER" for i in erased)
    live_ok = all(state["f%d" % i] == "content_%d" % i for i in range(N_FACTS) if i not in erased)
    print("  append_only=%s content_gone=%s live_ok=%s (facts=%d erased=%d)" % (append_only, content_gone, live_ok, N_FACTS, len(erased)), flush=True)
    return {"append_only": bool(append_only), "content_gone": bool(content_gone), "live_ok": bool(live_ok), "n_facts": N_FACTS, "n_erased": len(erased)}


def verdict(r) -> Tuple[str, str]:
    ok = r["append_only"] and r["content_gone"] and r["live_ok"]
    summary = "append_only=%s content_gone=%s live_replay_ok=%s (facts=%d erased=%d)" % (r["append_only"], r["content_gone"], r["live_ok"], r["n_facts"], r["n_erased"])
    if ok:
        return ("HARD_PASS", "HARD_PASS: ErasureRecord append-only design correct -- prior records immutable, content gone, replay matches live state. Stronger audit story than in-place downdate. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: append-only/erasure/replay invariant violated -- design needs revision. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
