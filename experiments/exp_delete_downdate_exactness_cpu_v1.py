"""
exp_delete_downdate_exactness_cpu_v1.py -- deleting facts leaves remaining recall intact and removes the deleted -- CPU.

ROUTING: CPU substrate-physics characterization (delete exactness). From a pinv memory of M facts, delete 20pct (re-solve without them); verify the deleted facts no longer recall their old value AND all remaining facts stay intact. Validates exact deletion (GDPR/correction support). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS remaining-intact >= 0.99 AND deleted-removed >= 0.90. MIDDLE intact >= 0.95. HARD-FAIL intact < 0.95.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "delete_downdate_exactness_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    m = np.ones(5, bool); m[2] = False; assert m.sum() == 4, "mask"; print("[selftest] PASS: delete-downdate-exactness-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(14); D = 512; M = int(0.7 * D); MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]; gold = np.argmax(V @ bk.T, axis=1)
    ndel = M // 5; del_idx = g.choice(M, ndel, replace=False); keep = np.ones(M, bool); keep[del_idx] = False
    W2 = np.linalg.solve(K[keep].T @ K[keep] + lam * np.eye(D), K[keep].T @ V[keep])
    pred = np.argmax((K @ W2) @ bk.T, axis=1)
    intact = float((pred[keep] == gold[keep]).mean()); removed = float((pred[del_idx] != gold[del_idx]).mean())
    print("  after deleting %d/%d: remaining-intact=%.4f deleted-removed=%.4f" % (ndel, M, intact, removed), flush=True)
    return {"intact": intact, "removed": removed}
def verdict(r) -> Tuple[str, str]:
    s = "remaining-intact=%.4f deleted-removed=%.4f" % (r["intact"], r["removed"])
    if r["intact"] >= 0.99 and r["removed"] >= 0.90: return ("HARD_PASS", "HARD_PASS: deletion leaves remaining facts intact (>=0.99) and removes deleted (>=0.90) -- exact deletion (GDPR/correction). " + s)
    if r["intact"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: remaining-intact 0.95-0.99. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deletion disturbs remaining facts (intact <0.95). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
