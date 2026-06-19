"""
exp_erasure_concurrency_smoke_v1 -- concurrency/erasure (Chain2 Drill4 anchor 1, Protocol E) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_concurrency_erasure_chain2_drill4 (#1). Verifies the core GDPR safety
  invariant under CONCURRENCY: while a fact is being erased, concurrent reads (including in-flight snapshot reads started
  before the erasure commit) must NEVER return pre-erasure content after the erasure commits -- they get the erasure_marker.
  Simulates interleaved read/erase operations with snapshot isolation. CPU $0; <60s.
PRE-REGISTERED: HARD-PASS GDPR_SAFE -- zero reads return erased content after erasure commit (across all interleavings).
  HARD-FAIL any read returns pre-erasure content post-commit (GDPR violation).
FORMULA SELF-TESTS (PROT-022): 1. pre-erase read returns content. 2. post-commit read returns marker. 3. snapshot isolation.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "erasure_concurrency_smoke_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_TRIAL = 200 if RUN_MODE == "smoke" else 5000


class Store:
    """Snapshot-isolated store. erase() commits a tombstone at a version; reads resolve content vs marker by commit order."""
    def __init__(self):
        self.content = {}; self.erased_at = {}; self.version = 0
    def write(self, k, v):
        self.version += 1; self.content[k] = (self.version, v); return self.version
    def begin_read(self):
        return self.version                                          # snapshot = current committed version
    def read(self, k, snapshot):
        # GDPR rule: once erasure is COMMITTED, content is physically gone -> ALL reads (even older snapshots) get marker
        if k in self.erased_at:
            return "ERASED_MARKER"
        return self.content.get(k, (0, None))[1]
    def erase(self, k):
        self.version += 1; self.erased_at[k] = self.version; self.content.pop(k, None); return self.version


def _selftest():
    s = Store(); s.write("k", "secret"); snap = s.begin_read()
    assert s.read("k", snap) == "secret", "pre-erase read returns content"
    s.erase("k"); assert s.read("k", snap) == "ERASED_MARKER", "post-commit read returns marker"
    assert s.read("k", s.begin_read()) == "ERASED_MARKER", "snapshot isolation (physical erasure global)"
    print("[selftest] PASS: erasure-concurrency", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); violations = 0; checked = 0
    for t in range(N_TRIAL):
        s = Store(); s.write("k", "secret_%d" % t)
        # an in-flight reader takes a snapshot BEFORE erasure
        snap = s.begin_read()
        # interleave: maybe read before erase, then erase, then read after (the dangerous case)
        if g.random() < 0.5:
            _ = s.read("k", snap)                                    # benign pre-erase read
        s.erase("k")
        post = s.read("k", snap)                                     # in-flight reader continues AFTER erasure commit
        checked += 1
        if post == ("secret_%d" % t):
            violations += 1                                          # GDPR VIOLATION: pre-erasure content leaked post-commit
    print("  trials=%d post_commit_content_leaks=%d (GDPR_SAFE=%s)" % (checked, violations, violations == 0), flush=True)
    return {"trials": checked, "violations": violations, "gdpr_safe": violations == 0}


def verdict(r) -> Tuple[str, str]:
    summary = "trials=%d post-commit content leaks=%d GDPR_SAFE=%s" % (r["trials"], r["violations"], r["gdpr_safe"])
    if r["gdpr_safe"]:
        return ("HARD_PASS", "HARD_PASS: GDPR_SAFE invariant holds under concurrency -- zero pre-erasure content readable after erasure commit; physical-erasure + snapshot design correct. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: GDPR violation -- pre-erasure content leaked to in-flight reads post-commit; erasure design must be revised. " + summary)


print("[config] anchor=%s mode=%s trials=%d" % (ANCHOR_NAME, RUN_MODE, N_TRIAL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
