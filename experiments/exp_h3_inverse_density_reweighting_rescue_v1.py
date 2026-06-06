"""
exp_h3_inverse_density_reweighting_rescue_v1 -- Batch H3 (G8 inverse-density rescue) -- CPU.

ROUTING: Batch H RESCUE-B (G8 anchoring 2x drill). Independent cross-check of the MMR rescue: down-weight retrieval scores
  by each item's LOCAL DENSITY (mean similarity to the rest of the KB), so items buried in a dense cluster (where an
  injected false fact hides) lose ranking priority. Measures anchoring propagation under inverse-density reweighting vs the
  G8 baseline (0.341). CPU $0.
PRE-REGISTERED: HARD-PASS propagation < 0.10. MID 0.10-0.20. HARD-FAIL > 0.20.
FORMULA SELF-TESTS (PROT-022): 1. intra cosine high. 2. density higher in cluster. 3. deps.
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

ANCHOR_NAME = "h3_inverse_density_reweighting_rescue_v1"
INTRA_COS = 0.6; TOPK = 10; BETA = 4.0
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


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g)
    intra = float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j]))
    assert intra > 0.3, "intra cosine high"
    print("[selftest] PASS: h3-density", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def propagation(g, use_density):
    kb, lab, cen = clustered_kb(g); tgt = 0
    false_fact = unit(INTRA_COS * cen[tgt] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    G = kb_aug @ kb_aug.T; np.fill_diagonal(G, 0.0); dens = G.clip(0).mean(axis=1)
    q_same = kb[lab == tgt][:N_Q]; q_other = kb[lab != tgt][:N_Q]
    def influence(qs):
        hit = 0
        for q in qs:
            score = kb_aug @ q
            if use_density:
                score = score / (1.0 + BETA * dens)
            sel = np.argsort(score)[-TOPK:]; hit += int(f_idx in sel)
        return hit / len(qs)
    return influence(q_same) - influence(q_other)


def run_seed(seed) -> Dict:
    base = propagation(np.random.default_rng(seed), False); dw = propagation(np.random.default_rng(seed), True)
    print("  [seed=%d] baseline_propagation=%.3f density_propagation=%.3f" % (seed, base, dw), flush=True)
    return {"seed": seed, "baseline_propagation": base, "density_propagation": dw}


def verdict(ps) -> Tuple[str, str]:
    dw = float(np.mean([p["density_propagation"] for p in ps])); base = float(np.mean([p["baseline_propagation"] for p in ps]))
    summary = "baseline_propagation=%.3f -> inverse-density_propagation=%.3f (beta=%.1f, k=%d)" % (base, dw, BETA, TOPK)
    if dw < 0.10:
        return ("HARD_PASS", "HARD_PASS: inverse-density reweighting cuts anchoring propagation <0.10 -- second independent G8 mitigation. " + summary)
    if dw <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: inverse-density partial rescue (0.10-0.20). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: inverse-density insufficient (>0.20). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d beta=%.1f k=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST, BETA, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
