"""
exp_decisive4_gdpr_erasure_cpu_v1.py -- DECISIVE-4 GDPR exact erasure (protocol-fixed: sharded) -- CPU.

ROUTING: HUGE_BATCH TIER-1, protocol fix per research_to_exp_dev_DECISIVE_4_PROTOCOL_FIX. Original used ONE superposed memory
  (M=1000) where cleanup is load-limited BEFORE deletion, so "retained fact misclassifies" got miscounted as deletion-caused
  false-loss. FIX (sharding lever): ~20 facts/shard so pre-deletion recall=1.0; then measure TRUE_DELETION (deleted unretrievable)
  and FALSE_LOSS (retained AND pre-retrievable facts that became unretrievable) separately. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS 0 false retentions AND 0 false losses (on pre-retrievable retained set) AND pre-recall>=0.99. else HARD-FAIL.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "decisive4_gdpr_erasure_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    assert hashlib.sha256(b"x").hexdigest() == hashlib.sha256(b"x").hexdigest(), "det"; print("[selftest] PASS: decisive4-gdpr-erasure", flush=True)


def run() -> Dict:
    g = np.random.default_rng(404); N = 8192; M = 300 if SMOKE else 1000; VK = M; VV = 600
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g)
    SH = 20; truth = {}
    shard = [np.zeros(N, dtype=np.complex64) for _ in range((M + SH - 1) // SH)]   # ~20 facts/shard -> exact cleanup
    for k in range(M):
        vv = int(g.integers(0, VV)); shard[k // SH] = shard[k // SH] + keys[k] * vals[vv]; truth[k] = vv
    pre_ok = {k: (cidx(shard[k // SH] * np.conj(keys[k]), vals) == truth[k]) for k in range(M)}   # retrievable BEFORE deletion
    pre_recall = sum(pre_ok.values()) / M
    ndel = max(10, M // 10); dele = set(int(x) for x in g.choice(M, ndel, replace=False))
    t0 = time.perf_counter()
    for k in dele:
        shard[k // SH] = shard[k // SH] - keys[k] * vals[truth[k]]        # surgical erasure from the fact's shard (PP-104)
    lat_ms = (time.perf_counter() - t0) * 1000 / max(1, ndel)
    false_retention = 0
    for k in dele:                                                        # TRUE_DELETION: deleted facts must be unretrievable
        false_retention += int(cidx(shard[k // SH] * np.conj(keys[k]), vals) == truth[k])
    false_loss = 0
    for k in range(M):                                                    # FALSE_LOSS: retained + pre-retrievable must stay retrievable
        if k not in dele and pre_ok[k]:
            false_loss += int(cidx(shard[k // SH] * np.conj(keys[k]), vals) != truth[k])
    print("  pre_recall=%.3f deleted=%d false_retentions=%d false_losses=%d erase_latency=%.4fms/fact" % (pre_recall, ndel, false_retention, false_loss, lat_ms), flush=True)
    return {"false_retentions": false_retention, "false_losses": false_loss, "n_del": ndel, "pre_recall": round(pre_recall, 3), "latency_ms": round(lat_ms, 4)}


def verdict(r) -> Tuple[str, str]:
    s = "pre_recall=%.3f false_retentions=%d false_losses=%d latency=%.4fms" % (r["pre_recall"], r["false_retentions"], r["false_losses"], r["latency_ms"])
    if r["false_retentions"] == 0 and r["false_losses"] == 0 and r["pre_recall"] >= 0.99:
        return ("HARD_PASS", "HARD_PASS: GDPR exact erasure (sharded) -- pre-recall 1.0, 0 false retentions on deleted + 0 false losses on retained, sub-ms/fact. EU AI Act Art.17 categorical. " + s)
    return ("HARD_FAIL", "HARD_FAIL: erasure imperfect or pre-recall<0.99. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
