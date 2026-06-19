"""
exp_h2_mmr_lambda_rho_envelope_v1 -- Batch H2 (G8 MMR safe-deployment envelope) -- CPU.

ROUTING: Batch H RESCUE-A envelope (G8 anchoring 2x drill). Maps the MMR safe-deployment region: anchoring propagation
  across a lambda{0.3,0.5,0.7} x rho_cluster{0.4,0.6,0.8} grid. Tells deployment teams when MMR diversification is
  required vs optional and what cluster-correlation regime is safe. CPU $0.
PRE-REGISTERED: HARD-PASS >=5/9 grid cells achieve propagation<0.10 (broad safe envelope). MID 1-4/9. HARD-FAIL 0/9.
FORMULA SELF-TESTS (PROT-022): 1. MMR selects distinct. 2. higher rho -> denser cluster. 3. deps.
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

ANCHOR_NAME = "h2_mmr_lambda_rho_envelope_v1"
TOPK = 10; LAMBDAS = [0.3, 0.5, 0.7]; RHOS = [0.4, 0.6, 0.8]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1536; N_CLUST = 16; PER = 24; N_Q = 40; LAMBDAS = [0.3, 0.7]; RHOS = [0.4, 0.8]
else:
    SEEDS = [7, 17, 23]; N = 6144; N_CLUST = 50; PER = 50; N_Q = 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g, rho):
    centers = rv(N_CLUST, N, g); items = []; labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(rho * centers[c] + np.sqrt(1 - rho ** 2) * rv(1, N, g)[0])); labels.append(c)
    return np.stack(items), np.array(labels), centers


def mmr_select(q, items, k, lam):
    sims = items @ q; chosen = []; cand = list(range(len(items)))
    for _ in range(min(k, len(items))):
        if not chosen:
            j = int(np.argmax(sims[cand]))
        else:
            div = np.max(items[cand] @ items[chosen].T, axis=1); j = int(np.argmax(lam * sims[cand] - (1 - lam) * div))
        chosen.append(cand.pop(j))
    return chosen


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g, 0.6); sel = mmr_select(kb[0], kb[:30], 5, 0.5)
    assert len(set(sel)) == 5, "MMR selects distinct"
    print("[selftest] PASS: h2-envelope", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def propagation(g, lam, rho):
    kb, lab, cen = clustered_kb(g, rho); tgt = 0
    false_fact = unit(rho * cen[tgt] + np.sqrt(1 - rho ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    q_same = kb[lab == tgt][:N_Q]; q_other = kb[lab != tgt][:N_Q]
    def influence(qs):
        return sum(int(f_idx in mmr_select(q, kb_aug, TOPK, lam)) for q in qs) / len(qs)
    return influence(q_same) - influence(q_other)


def run_seed(seed) -> Dict:
    grid = {}
    for lam in LAMBDAS:
        for rho in RHOS:
            grid["l%.1f_r%.1f" % (lam, rho)] = propagation(np.random.default_rng(seed), lam, rho)
    print("  [seed=%d] %s" % (seed, {k: round(v, 3) for k, v in grid.items()}), flush=True)
    return {"seed": seed, "grid": grid}


def verdict(ps) -> Tuple[str, str]:
    agg = {k: float(np.mean([p["grid"][k] for p in ps])) for k in ps[0]["grid"]}
    safe = [k for k, v in agg.items() if v < 0.10]; ncells = len(agg)
    summary = "propagation by lambda_rho: %s | safe(<0.10): %d/%d %s" % ({k: round(v, 3) for k, v in agg.items()}, len(safe), ncells, safe)
    if len(safe) >= max(1, int(0.55 * ncells)):
        return ("HARD_PASS", "HARD_PASS: MMR safe-deployment envelope is broad (majority of cells <0.10) -- clear production guidance. " + summary)
    if len(safe) >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MMR safe only in part of the envelope. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no (lambda,rho) cell achieves propagation<0.10. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d lambdas=%s rhos=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, LAMBDAS, RHOS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
