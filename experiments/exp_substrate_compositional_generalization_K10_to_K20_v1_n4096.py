"""
substrate_compositional_generalization_K10_to_K20_v1_n4096 -- NEW EXP 2: novel-chain composition -- remote CPU.

ROUTING: research_to_exp_dev_3_drill_synthesis_priority_experiments (NEW EXP 2). Substrate stores INDIVIDUAL link
  facts (A->B, B->C, ...) shuffled (never as a contiguous chain); query "traverse K hops from A" -> tests whether
  iterated retrieval COMPOSES a NOVEL multi-hop chain from individually-stored links (compositional generalization;
  necessary for NOVEL questions, not just stored ones). CPU numpy, $0. remote_cpu_queue.

MODEL: G chains (length L=20) over distinct bipolar concept nodes; store each consecutive link A_i->A_{i+1} as a
  Hebbian transition (links SHUFFLED across chains -> no chain ever seen as a unit). Iterated retrieval q=sign(W@q)
  from A_0; success at hop K iff lands on A_K. Low load (0.3*alpha_c) to admit K up to 20. Measure K=10/15/20.

PRE-REGISTERED bands: HARD-PASS >=70% success at K=15 (novel chain composed). MIDDLE 50-70%. HARD-FAIL <50%
  (substrate only recalls stored chains, doesn't compose).

FORMULA SELF-TESTS (PROT-022): 1. composed 3-hop from shuffled links. 2. chain nodes distinct. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_compositional_generalization_K10_to_K20_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; L = 20; LOAD_FRAC = 0.3; K_TEST = [10, 15, 20]
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def build(n, g):
    n_trans = max(L, int(round(LOAD_FRAC * ALPHA_C * n))); G = max(1, n_trans // L)
    chains = [bipolar((L + 1, n), g) for _ in range(G)]
    links = [(ci, i) for ci in range(G) for i in range(L)]; g.shuffle(links)   # shuffle: no chain seen as a unit
    W = np.zeros((n, n), dtype=np.float32)
    for (ci, i) in links:
        W += np.outer(chains[ci][i + 1], chains[ci][i])
    return W, chains


def hop_success(W, chains, n, K):
    if L < K:
        return None
    hits = 0
    for ch in chains:
        q = ch[0].copy()
        for _ in range(K):
            q = np.sign(W @ q); q[q == 0] = 1.0
        hits += (float((q * ch[K]).sum() / n) > 0.90)
    return hits / len(chains)


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((6, n), g); links = [(0, i) for i in range(5)]; g.shuffle(links)
    W = np.zeros((n, n), dtype=np.float32)
    for (_, i) in links:
        W += np.outer(ch[i + 1], ch[i])
    q = ch[0]
    for _ in range(3):
        q = np.sign(W @ q)
    assert float((q * ch[3]).sum() / n) > 0.9, "composed 3-hop from shuffled links"
    assert N == 4096; print("[selftest] PASS: composed_3hop", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); W, chains = build(N_DIM, g)
    out = {"seed": seed, "N": N_DIM, "G_chains": len(chains)}
    for K in K_TEST:
        s = hop_success(W, chains, N_DIM, K); out["K%d" % K] = float(s) if s is not None else -1.0
    return out


def verdict(ps) -> Tuple[str, str]:
    k15 = float(np.mean([p["K15"] for p in ps]))
    summary = " ".join("K%d=%.2f" % (K, float(np.mean([p["K%d" % K] for p in ps]))) for K in K_TEST) + (" (G=%d)" % int(np.mean([p["G_chains"] for p in ps])))
    if k15 >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate composes NOVEL chains (>=70% at K=15). " + summary)
    if k15 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial novel-chain composition. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate does not compose novel chains (<50% at K=15). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d L=%d load=%.1f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, L, LOAD_FRAC), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("K%d=%.2f" % (K, r["K%d" % K]) for K in K_TEST), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
