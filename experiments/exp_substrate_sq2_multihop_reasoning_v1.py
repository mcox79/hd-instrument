"""
substrate_sq2_multihop_reasoning_v1 -- iterated-retrieval multi-hop reasoning -- remote CPU.

ROUTING: notes/research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ2; P_drill=0.72).
  Tests whether a substrate stores reasoning CHAINS and traverses K hops via iterated sign(W q) -- single-pass
  Hopfield is TC0; iterated retrieval reaches depth K (-> NC1-class). CPU numpy, $0. remote_cpu_queue.

CAPABILITY QUESTION: store G chains a_g0 -> a_g1 -> ... -> a_gL (heteroassoc W = sum outer(next, cur)); from a
  chain start, iterate q = sign(W q) K times; does the K-th hop land on a_gK (multi-hop traversal)? How far (K)
  and at what load (G chains) before chaining breaks?

CELLS (3 seeds): K-hop accuracy at K in {1,2,4,8,12}; load G*L transitions = LOAD_FRAC * alpha_c * N.
  accuracy(K) = frac of chains whose K-th iterate overlaps the true a_gK > 0.9.

PRE-REGISTERED bands (depth = max K with mean accuracy >= 0.80):
  HARD-PASS: depth >= 8 (substrate chains >=8 hops -> deep iterated reasoning). MIDDLE: depth in {2,4}. HARD-FAIL: depth < 2.

FORMULA SELF-TESTS (PROT-022): 1. single chain 1-hop recall. 2. 2-hop traversal on one clean chain. 3. distinct items. 4. alpha_c=0.138.
ASCII-only. write_metrics. PROT-018: swept-K anchor (no _nN).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq2_multihop_reasoning_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L = 12                 # chain length (>= max K)
K_GRID = [1, 2, 4, 8, 12]
LOAD_FRAC = 0.5        # total transitions = LOAD_FRAC * alpha_c * N

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512
else:
    SEEDS = [7, 17, 23]; N = 2048


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def build(n, g):
    n_trans = max(L, int(round(LOAD_FRAC * ALPHA_C * n)))
    G = max(1, n_trans // L)                       # number of chains
    chains = [bipolar((L + 1, n), g) for _ in range(G)]   # each chain: L+1 items
    W = np.zeros((n, n), dtype=np.float32)
    for ch in chains:
        for i in range(L):
            W += np.outer(ch[i + 1], ch[i])
    return W, chains, G


def hop_acc(W, chains, n, K):
    hits = 0
    for ch in chains:
        q = ch[0].copy()
        for _ in range(K):
            q = np.sign(W @ q); q[q == 0] = 1.0
        hits += (float((q * ch[K]).sum() / n) > 0.90)
    return hits / len(chains)


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g)
    W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    q = np.sign(W @ ch[0]); assert float((q * ch[1]).sum() / n) > 0.9, "1-hop failed"
    q2 = np.sign(W @ q); assert float((q2 * ch[2]).sum() / n) > 0.9, "2-hop failed"
    assert not np.array_equal(ch[0], ch[1]); assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: 1hop 2hop distinct", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); W, chains, G = build(N, g)
    acc = {f"K{k}": float(hop_acc(W, chains, N, k)) for k in K_GRID}
    return {"seed": seed, "N": N, "G_chains": G, **acc}


def verdict(per_seed) -> Tuple[str, str]:
    acc = {k: float(np.mean([s[f"K{k}"] for s in per_seed])) for k in K_GRID}
    depth = max([k for k in K_GRID if acc[k] >= 0.80], default=0)
    summary = "acc " + " ".join(f"K{k}:{acc[k]:.2f}" for k in K_GRID) + f" | depth={depth} (G={per_seed[0]['G_chains']} chains)"
    if depth >= 8:
        return ("HARD_PASS", f"HARD_PASS: substrate traverses >=8 reasoning hops via iterated retrieval. {summary}")
    if depth >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: multi-hop depth {depth}. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: chaining breaks before 2 hops. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} L={L} K_grid={K_GRID} load_frac={LOAD_FRAC}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    r = run_seed(seed); per_seed.append(r)
    print(f"  [seed={seed}] G={r['G_chains']} " + " ".join(f"K{k}:{r[f'K{k}']:.2f}" for k in K_GRID), flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": [f"K{k}" for k in K_GRID], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
