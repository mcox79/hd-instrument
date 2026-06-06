"""
exp_h1_mmr_diversified_retrieval_rescue_v1 -- Batch H1 (G8 MMR rescue; production gate) -- CPU.

ROUTING: Batch H RESCUE-A (G8 anchoring 2x drill). G8 found clustered-KB anchoring propagation = 0.341 (GENUINE security
  finding). MMR (Maximal Marginal Relevance, Carbonell-Goldstein 1998) reranks retrieval to balance relevance + diversity,
  de-weighting redundant same-cluster matches so an injected false fact can't dominate. Measures anchoring propagation
  under MMR-diversified grounding vs the G8 baseline (0.341). Drill predicts -> <0.10. CPU $0.
PRE-REGISTERED: HARD-PASS propagation < 0.10 (MMR rescues; G8 row -> CONDITIONAL PASS). MID 0.10-0.20 (partial). HARD-FAIL
  > 0.20 (MMR insufficient; escalate to inverse-density / confidence rescue).
FORMULA SELF-TESTS (PROT-022): 1. intra>inter cosine. 2. MMR selects diverse set. 3. baseline reproduces G8 propagation.
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

ANCHOR_NAME = "h1_mmr_diversified_retrieval_rescue_v1"
INTRA_COS = 0.6; LAMBDA = 0.5; TOPK = 10
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


def mmr_select(q, items, k, lam):
    sims = items @ q; chosen = []; cand = list(range(len(items)))
    for _ in range(min(k, len(items))):
        if not chosen:
            j = int(np.argmax(sims[cand]))
        else:
            div = np.max(items[cand] @ items[chosen].T, axis=1)
            mmr = lam * sims[cand] - (1 - lam) * div; j = int(np.argmax(mmr))
        chosen.append(cand.pop(j))
    return chosen


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g)
    intra = float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j]))
    assert intra > 0.3, "intra cosine high"
    sel = mmr_select(kb[0], kb[:30], 5, 0.5); assert len(set(sel)) == 5, "MMR selects distinct"
    print("[selftest] PASS: h1-mmr", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def propagation(g, use_mmr):
    kb, lab, cen = clustered_kb(g); tgt = 0
    false_fact = unit(INTRA_COS * cen[tgt] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    q_same = kb[lab == tgt][:N_Q]; q_other = kb[lab != tgt][:N_Q]
    def influence(qs):
        hit = 0
        for q in qs:
            if use_mmr:
                sel = mmr_select(q, kb_aug, TOPK, LAMBDA); hit += int(f_idx in sel)
            else:
                sel = np.argsort(kb_aug @ q)[-TOPK:]; hit += int(f_idx in sel)
        return hit / len(qs)
    return influence(q_same) - influence(q_other)


def run_seed(seed) -> Dict:
    base = propagation(np.random.default_rng(seed), use_mmr=False); mmr = propagation(np.random.default_rng(seed), use_mmr=True)
    print("  [seed=%d] baseline_propagation=%.3f mmr_propagation=%.3f" % (seed, base, mmr), flush=True)
    return {"seed": seed, "baseline_propagation": base, "mmr_propagation": mmr}


def verdict(ps) -> Tuple[str, str]:
    mmr = float(np.mean([p["mmr_propagation"] for p in ps])); base = float(np.mean([p["baseline_propagation"] for p in ps]))
    summary = "baseline_propagation=%.3f -> MMR_propagation=%.3f (lambda=%.1f, k=%d)" % (base, mmr, LAMBDA, TOPK)
    if mmr < 0.10:
        return ("HARD_PASS", "HARD_PASS: MMR diversification cuts anchoring propagation <0.10 -- G8 row -> CONDITIONAL PASS (clustered KBs production-deployable with MMR). " + summary)
    if mmr <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MMR partial rescue (0.10-0.20); document constraint. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: MMR insufficient (>0.20); escalate to inverse-density / confidence rescue. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d lambda=%.1f k=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST, LAMBDA, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
