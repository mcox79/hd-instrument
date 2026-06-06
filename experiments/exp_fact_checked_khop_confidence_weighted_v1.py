"""
exp_fact_checked_khop_confidence_weighted_v1 -- Batch D1 Rank 1 (cheapest lift): confidence-weighted chain verification -- CPU.

ROUTING: Research Batch D. Replace the BINARY per-hop fabrication flag with continuous confidence: C_h = per-hop grounding
  (max cosine to KB). Chain scores: C_min = min_h C_h, C_chain = prod_h C_h. Adversarial test = clean chains vs chains
  with one fabricated hop; AUC of the chain score discriminating them. Compares confidence-weighted (C_min, C_chain) vs the
  binary-flag AUC. Cheapest adversarial-signal lift (zero added inference compute). Tests at K up to 20 where the binary
  ceiling (1 - K*(1-AUC_hop)) bites.
PRE-REGISTERED: HARD-PASS best confidence-weighted AUC >= binary-flag AUC + 0.02 at K=10/20. MID equal but tighter. HARD-FAIL worse.
FORMULA SELF-TESTS (PROT-022): 1. clean grounded. 2. fabricated low. 3. AUC bounds.
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

ANCHOR_NAME = "fact_checked_khop_confidence_weighted_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 600; CHAINS = 200; KS = [5, 10]
else:
    SEEDS = [7, 17, 23]; N = 8192; V_C = 3000; CHAINS = 500; KS = [5, 10, 20]


def bp(M, n, g):
    x = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    g = np.random.default_rng(0); C = bp(50, 256, g); assert np.max(C @ C[3]) > 0.99, "clean grounded"
    assert np.max(C @ bp(1, 256, g)[0]) < 0.5, "fabricated low"
    assert auc([1, 1, 1], [0, 0, 0]) == 1.0, "AUC bounds"
    print("[selftest] PASS: conf-weighted", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def chain_scores(K, fabricate, C, g, V_C, N):
    seq = list(g.choice(V_C, K, replace=False)); hops = [C[j] for j in seq]
    if fabricate:
        hops[g.integers(0, K)] = bp(1, N, g)[0]
    conf = np.array([float(np.max(C @ hops[i])) for i in range(K)])
    flag = int(np.any(conf < 0.5))                                   # binary: any hop below grounding threshold
    return flag, float(conf.min()), float(np.prod(np.clip(conf, 1e-3, 1.0)))


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g); out = {}
    for K in KS:
        bf_p, bf_n, cm_p, cm_n, cc_p, cc_n = [], [], [], [], [], []
        for _ in range(CHAINS):
            f, cmin, cchain = chain_scores(K, True, C, g, V_C, N); bf_p.append(f); cm_p.append(-cmin); cc_p.append(-cchain)
            f, cmin, cchain = chain_scores(K, False, C, g, V_C, N); bf_n.append(f); cm_n.append(-cmin); cc_n.append(-cchain)
        binary = auc(bf_p, bf_n); cmin_auc = auc(cm_p, cm_n); cchain_auc = auc(cc_p, cc_n)
        out["K%d" % K] = {"binary": binary, "c_min": cmin_auc, "c_chain": cchain_auc, "best_conf": max(cmin_auc, cchain_auc)}
        print("  [seed=%d K=%d] binary=%.3f c_min=%.3f c_chain=%.3f" % (seed, K, binary, cmin_auc, cchain_auc), flush=True)
    return {"seed": seed, "by_K": out}


def verdict(ps) -> Tuple[str, str]:
    Kmax = "K%d" % KS[-1]
    binv = float(np.mean([p["by_K"][Kmax]["binary"] for p in ps])); confv = float(np.mean([p["by_K"][Kmax]["best_conf"] for p in ps]))
    lift = confv - binv
    summary = "at K=%d: binary_AUC=%.3f best_conf_AUC=%.3f lift=%+.3f" % (KS[-1], binv, confv, lift)
    if lift >= 0.02:
        return ("HARD_PASS", "HARD_PASS: confidence-weighted aggregation lifts adversarial AUC >=0.02 at production K -- cheapest killer-demo robustness gain. " + summary)
    if lift >= -0.005:
        return ("MIDDLE_BAND", "MIDDLE_BAND: confidence ~ binary (no clear lift). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: confidence-weighted worse than binary flag (calibration issue). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
