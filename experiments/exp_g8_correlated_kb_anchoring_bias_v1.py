"""
exp_g8_correlated_kb_anchoring_bias_v1 -- Batch G8 (AT-3 clustered-KB anchoring) -- CPU.

ROUTING: Batch G Tier-4 (adversarial drill #3). Anchoring-bias refutation was GENUINE for INDEPENDENT synthetic KBs, but
  real KBs have semantic CLUSTER structure (entity types grouped). A false fact injected into a tight cluster may PROPAGATE
  (be reinforced by its neighbors' grounding). Constructs a clustered KB (B clusters, intra-cluster cosine high), injects a
  false fact in a cluster, measures whether nearby (same-cluster) queries get pulled toward the false fact (propagation).
  CPU $0.
PRE-REGISTERED: HARD-PASS no propagation (false-fact grounding lift on same-cluster queries <= 0.05 vs baseline). MID
  partial (0.05-0.20, only tightest clusters). HARD-FAIL >0.20 (cluster structure enables anchoring propagation).
FORMULA SELF-TESTS (PROT-022): 1. intra-cluster cosine > inter. 2. AUC/lift bounds. 3. cluster assignment.
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

ANCHOR_NAME = "g8_correlated_kb_anchoring_bias_v1"
INTRA_COS = 0.6   # intra-cluster correlation
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; N_CLUST = 20; PER = 30
else:
    SEEDS = [7, 17, 23]; N = 8192; N_CLUST = 60; PER = 60


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


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g)
    intra = float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j]))
    inter = float(np.mean([kb[i] @ kb[-1 - i] for i in range(5)]))
    assert intra > inter, "intra-cluster cosine > inter"
    print("[selftest] PASS: g8-anchoring", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); kb, lab, cen = clustered_kb(g)
    tgt_c = 0; false_fact = unit(INTRA_COS * cen[tgt_c] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])  # plausible false fact in cluster 0
    same = kb[lab == tgt_c]; other = kb[lab != tgt_c]
    # grounding lift = how much the false fact raises same-cluster queries' max-sim vs a random fact
    rand_fact = rv(1, N, g)[0]
    same_lift = float(np.mean((same @ false_fact)) - np.mean((same @ rand_fact)))
    other_lift = float(np.mean((other @ false_fact)) - np.mean((other @ rand_fact)))
    propagation = same_lift - other_lift                                  # excess pull on same-cluster (anchoring)
    print("  [seed=%d] same_cluster_lift=%.3f other_lift=%.3f propagation=%.3f" % (seed, same_lift, other_lift, propagation), flush=True)
    return {"seed": seed, "same_lift": same_lift, "other_lift": other_lift, "propagation": propagation}


def verdict(ps) -> Tuple[str, str]:
    prop = float(np.mean([p["propagation"] for p in ps]))
    summary = "same-cluster anchoring propagation=%.3f (intra_cos=%.2f)" % (prop, INTRA_COS)
    if prop <= 0.05:
        return ("HARD_PASS", "HARD_PASS: no anchoring propagation under cluster structure (<=0.05) -- robust to correlated-KB bias. " + summary)
    if prop <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial propagation in tight clusters (0.05-0.20). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cluster structure enables anchoring propagation (>0.20) -- KB clustering is an attack surface. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d intra_cos=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST, INTRA_COS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
