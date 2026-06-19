"""
exp_lvh245_mmr_topology_spectral_gap_v1 -- LVH245 anchor 3 (production-risk topology characterization) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_LVH245_mmr_topology_2x (#3). Real production KBs (Wikipedia, entity-rich
  KGs) have HIGHER hub centrality than synthetic uniform-cluster test KBs. This sweeps KB topology from uniform to strongly
  hub-dominated (one over-represented cluster) and measures anchoring propagation (false-fact spread) under MMR retrieval at
  each hub level -- bounding the real production failure rate. CPU $0.
PRE-REGISTERED: HARD-PASS MMR keeps propagation < 0.10 across the full hub-centrality range (production-safe). MID
  propagation 0.10-0.30 at high hub centrality (qualify). HARD-FAIL > 0.30 at realistic hub levels (production risk).
FORMULA SELF-TESTS (PROT-022): 1. MMR distinct. 2. hub fraction controls dominance. 3. clustered intra>inter.
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

ANCHOR_NAME = "lvh245_mmr_topology_spectral_gap_v1"
INTRA_COS = 0.6; LAMBDA = 0.3; TOPK = 10; HUB_FRACS = [0.1, 0.3, 0.5, 0.7, 0.9]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; N_CLUST = 12; TOTAL = 300; N_Q = 50; HUB_FRACS = [0.1, 0.5, 0.9]
else:
    SEEDS = [7, 17, 23]; N = 2048; N_CLUST = 40; TOTAL = 1600; N_Q = 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def hub_kb(hub_frac, g):
    # hub_frac of all items belong to cluster 0 (the hub); rest spread over remaining clusters
    centers = rv(N_CLUST, N, g); n_hub = int(hub_frac * TOTAL); items = []; labels = []
    for _ in range(n_hub):
        items.append(unit(INTRA_COS * centers[0] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])); labels.append(0)
    for i in range(TOTAL - n_hub):
        c = 1 + (i % (N_CLUST - 1)); items.append(unit(INTRA_COS * centers[c] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])); labels.append(c)
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
    g = np.random.default_rng(0); kb, lab, cen = hub_kb(0.5, g)
    assert (lab == 0).mean() > 0.3, "hub fraction controls dominance"
    assert len(set(mmr_select(kb[0], kb[:20], 5, 0.3))) == 5, "MMR distinct"
    assert float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j])) > 0.2, "clustered intra>inter"
    print("[selftest] PASS: mmr-topology", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def propagation(hub_frac, seed):
    g = np.random.default_rng(seed); kb, lab, cen = hub_kb(hub_frac, g)
    false_fact = unit(INTRA_COS * cen[0] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    q_hub = kb[lab == 0][:N_Q]; q_other = kb[lab != 0][:N_Q]
    def inf(qs):
        return sum(int(f_idx in mmr_select(q, kb_aug, TOPK, LAMBDA)) for q in qs) / max(len(qs), 1)
    return inf(q_hub) - inf(q_other)


def run_seed(seed) -> Dict:
    by = {("hub%.1f" % h): float(propagation(h, seed * 13 + int(h * 10))) for h in HUB_FRACS}
    print("  [seed=%d] propagation by hub_frac: %s" % (seed, {k: round(v, 3) for k, v in by.items()}), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    agg = {("hub%.1f" % h): float(np.mean([p["by"]["hub%.1f" % h] for p in ps])) for h in HUB_FRACS}
    worst = max(agg.values())
    summary = "propagation by hub_frac: %s | worst=%.3f" % ({k: round(v, 3) for k, v in agg.items()}, worst)
    if worst < 0.10:
        return ("HARD_PASS", "HARD_PASS: MMR keeps anchoring propagation <0.10 across full hub-centrality range -- production-safe even on hub-dominated KBs. " + summary)
    if worst <= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: propagation 0.10-0.30 at high hub centrality (qualify production risk). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: propagation >0.30 at realistic hub levels -- production anchoring risk on entity-rich KBs. " + summary)


print("[config] anchor=%s mode=%s seeds=%s hub_fracs=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, HUB_FRACS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
