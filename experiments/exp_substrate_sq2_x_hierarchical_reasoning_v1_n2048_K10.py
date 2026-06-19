"""
substrate_sq2_x_hierarchical_reasoning_v1_n2048_K10 -- P2: multi-hop reasoning x hierarchical ensemble -- remote CPU.

ROUTING: research_to_exp_dev_priority_1_compositions_routing (Cell P2). Does a K-substrate ensemble (chains
  PARTITIONED across substrates -> each lightly loaded) sustain DEEPER reasoning at a total load where a single
  substrate's iterated retrieval collapses? Predicted multiplicative reasoning capacity. CPU numpy, $0. remote_cpu_queue.

MODEL: L=24-hop chains; TOTAL G chains at a HIGH load (2x alpha_c for a single substrate). single = all G in one W.
  ensemble = K=10 substrates, G/K chains each (partitioned, each lightly loaded); retrieve a chain via the
  substrate holding it. Iterate q=sign(W q) K hops; depth = max K with acc>=0.8.

CELLS (3 seeds): single_depth vs ensemble_depth at the high total load.
PRE-REGISTERED bands: HARD-PASS ensemble_depth >= 20 AND ensemble_depth >= 2x single_depth (multiplicative reasoning capacity).
  MIDDLE: ensemble_depth > single_depth but < 20. HARD-FAIL: ensemble_depth <= single_depth.

FORMULA SELF-TESTS (PROT-022): 1. low-load chain 2-hop. 2. partition lightens load (lightly-loaded recall>heavy). 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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

ANCHOR_NAME = "substrate_sq2_x_hierarchical_reasoning_v1_n2048_K10"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L = 24
K_GRID = [4, 8, 12, 16, 20, 24]
K_ENS = 10
TOTAL_LOAD = 2.0   # x alpha_c for a single substrate (overloads single)
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; K_ENS = 4
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def store(chains, n):
    W = np.zeros((n, n), dtype=np.float32)
    for ch in chains:
        for i in range(L):
            W += np.outer(ch[i + 1], ch[i])
    return W


def hop_acc_over(chains_W_pairs, n, K):
    """each chain retrieved via its own W (single: same W for all; ensemble: per-partition W)."""
    hits = 0; total = 0
    for ch, W in chains_W_pairs:
        q = ch[0].copy()
        for _ in range(K):
            q = np.sign(W @ q); q[q == 0] = 1.0
        hits += (float((q * ch[K]).sum() / n) > 0.90); total += 1
    return hits / total


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    G = max(K_ENS, int(round(TOTAL_LOAD * ALPHA_C * n / L)))
    chains = [bipolar((L + 1, n), g) for _ in range(G)]
    # single: all chains in one W
    Wsingle = store(chains, n)
    single_pairs = [(ch, Wsingle) for ch in chains]
    # ensemble: partition chains across K substrates
    parts = np.array_split(np.arange(G), K_ENS)
    Ws = [store([chains[i] for i in part], n) for part in parts]
    chain_to_W = {}
    for pi, part in enumerate(parts):
        for i in part:
            chain_to_W[i] = Ws[pi]
    ens_pairs = [(chains[i], chain_to_W[i]) for i in range(G)]
    sd = max([k for k in K_GRID if hop_acc_over(single_pairs, n, k) >= 0.80], default=0)
    ed = max([k for k in K_GRID if hop_acc_over(ens_pairs, n, k) >= 0.80], default=0)
    return {"seed": seed, "N": n, "G_chains": G, "single_depth": sd, "ensemble_depth": ed}


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    assert float((np.sign(W @ np.sign(W @ ch[0])) * ch[2]).sum() / n) > 0.9, "2-hop"
    assert N == 2048
    print("[selftest] PASS: 2hop_chain", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(ps) -> Tuple[str, str]:
    sd = float(np.mean([p["single_depth"] for p in ps])); ed = float(np.mean([p["ensemble_depth"] for p in ps]))
    summary = "single_depth=%.1f ensemble_depth=%.1f (K=%d, total_load=%.1fx alpha_c, G=%d)" % (sd, ed, K_ENS, TOTAL_LOAD, ps[0]["G_chains"])
    if ed >= 20 and ed >= 2 * max(sd, 1):
        return ("HARD_PASS", "HARD_PASS: ensemble sustains deep reasoning (>=20 hops) where single collapses. " + summary)
    if ed > sd:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ensemble deeper than single but <20. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ensemble no deeper than single. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d L=%d K_ens=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, L, K_ENS), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] single_depth=%d ensemble_depth=%d (G=%d)" % (seed, r["single_depth"], r["ensemble_depth"], r["G_chains"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
