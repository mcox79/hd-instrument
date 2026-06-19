"""
exp_h4_cluster_density_confidence_calibration_v1 -- Batch H4 (G8 cluster-density confidence) -- CPU.

ROUTING: Batch H RESCUE-D (G8 anchoring 2x drill). Lowest-cost mitigation: even without changing retrieval, expose an
  observable cluster_density_score per query that PREDICTS whether that query is at risk of anchoring contamination -- a
  client-facing propagation_risk flag. Measures whether the density score predicts contamination (AUC + Brier) on the
  G8-equivalent clustered KB. CPU $0.
PRE-REGISTERED: HARD-PASS density-score contamination-prediction AUC >= 0.75 (ship as propagation_risk flag). MID 0.60-0.75.
  HARD-FAIL < 0.60 (score not predictive).
FORMULA SELF-TESTS (PROT-022): 1. intra cosine high. 2. AUC bounds. 3. deps.
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

ANCHOR_NAME = "h4_cluster_density_confidence_calibration_v1"
INTRA_COS = 0.6; TOPK = 10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; N_CLUST = 20; PER = 30; N_Q = 60
else:
    SEEDS = [7, 17, 23]; N = 8192; N_CLUST = 60; PER = 60; N_Q = 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g):
    centers = rv(N_CLUST, N, g); items = []; labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(INTRA_COS * centers[c] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])); labels.append(c)
    return np.stack(items), np.array(labels), centers


def auc_of(risk, lab):
    pos = risk[lab == 1]; neg = risk[lab == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))); return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g)
    assert float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j])) > 0.3, "intra cosine high"
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0, "AUC bounds"
    print("[selftest] PASS: h4-confidence", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); kb, lab, cen = clustered_kb(g); tgt = 0
    false_fact = unit(INTRA_COS * cen[tgt] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    qs = np.vstack([kb[lab == tgt][:N_Q], kb[lab != tgt][:N_Q]])
    risk = []; contaminated = []
    for q in qs:
        risk.append(float(((kb_aug @ q).clip(0)).mean()))            # observable cluster-density score
        contaminated.append(int(f_idx in np.argsort(kb_aug @ q)[-TOPK:]))
    risk = np.array(risk); contaminated = np.array(contaminated)
    rn = (risk - risk.min()) / (risk.max() - risk.min() + 1e-9)
    auc = auc_of(rn, contaminated); brier = float(np.mean((rn - contaminated) ** 2))
    print("  [seed=%d] risk_pred_AUC=%.3f brier=%.3f contamination_rate=%.3f" % (seed, auc, brier, contaminated.mean()), flush=True)
    return {"seed": seed, "risk_auc": auc, "brier": brier}


def verdict(ps) -> Tuple[str, str]:
    auc = float(np.mean([p["risk_auc"] for p in ps])); brier = float(np.mean([p["brier"] for p in ps]))
    summary = "cluster-density risk: contamination-pred AUC=%.3f brier=%.3f" % (auc, brier)
    if auc >= 0.75:
        return ("HARD_PASS", "HARD_PASS: cluster-density score PREDICTS contamination (AUC>=0.75) -- ship as client-facing propagation_risk flag. " + summary)
    if auc >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: density score partially predictive (0.60-0.75). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: density score not predictive (<0.60). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d k=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
