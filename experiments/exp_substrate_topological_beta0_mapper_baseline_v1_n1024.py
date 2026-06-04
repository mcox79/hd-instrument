"""
substrate_topological_beta0_mapper_baseline_v1_n1024 -- topological memory observables (Phase 1b).

ROUTING: notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1b.
  EXPLORATORY (not load-bearing): establish a baseline for "topological memory inspection" capability.

CAPABILITY QUESTION:
  Can topological observables on the substrate's stored patterns -- the beta_0 (connected-components)
  connectivity curve + a Mapper graph -- (a) detect a kappa_2-INVARIANT drift event that the second
  moment misses, and (b) produce non-trivial Mapper structure? If beta_0 detects a drift that kappa_2
  does NOT, that is NEW inspection information (topology sees what spectral moments cannot).

MODEL:
  Stored bipolar patterns Xi (M x N). beta_0(tau) = number of connected components of the graph whose
  edges are pattern pairs with cosine similarity > tau, swept over a tau grid (union-find). A drift event
  = swap a fraction of patterns for fresh random ones (kappa_2-approximately-invariant: same M, same
  per-coordinate variance, so Tr(W^2)/N is ~unchanged). Mapper: filter = 1st PCA coord; overlapping
  interval cover; single-linkage cluster per interval -> node count.

THREE CELLS (3 seeds each):
  A: M=500,  N=1024, clean.
  B: M=1000, N=1024, clean (scale check).
  C: M=500,  N=1024, drift injected (kappa_2-invariant pattern swap).

PRE-REGISTERED BANDS:
  HARD-PASS: beta_0 curve KS-detects drift (Cell C vs A, p < 0.05) AND the drift is kappa_2-invariant
    (delta_kappa2 < 0.10) AND Mapper produces >= 5 nodes at M=500 -> topology gives NEW info + structure.
  MIDDLE: beta_0 detects but delta_kappa2 >= 0.10 (kappa_2 also moved -> no new info) OR Mapper 2-4 nodes.
  HARD-FAIL: beta_0 insensitive to drift (KS p >= 0.05) OR Mapper collapses to 1 node.

FORMULA SELF-TESTS (PROT-022):
  1. union-find: a fully-connected threshold gives beta_0=1; an all-disconnected threshold gives beta_0=M.
  2. KS statistic of identical samples = 0.
  3. kappa_2 = Tr(W^2)/N > 0 for a non-trivial W.

PROT-018: anchor _n1024 -> N=1024. PROT-021: seed checkpoints keyed run_mode + seed.
QUEUE: remote_cpu_queue (CPU; pure numpy). TIMEOUT: 7200s. ASCII-only stdout.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, math, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_topological_beta0_mapper_baseline_v1_n1024"
_N_SUFFIX = 1024
N = 1024
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

DRIFT_FRAC = 0.20
TAU_GRID = [round(0.02 * i, 3) for i in range(1, 16)]   # cosine-sim thresholds 0.02..0.30
KAPPA2_INVARIANT = 0.10
MAPPER_INTERVALS = 6
MAPPER_OVERLAP = 0.30
MAPPER_LINK_TAU = 0.10

if RUN_MODE == "smoke":
    CELLS = [("A_M120_clean", 120, False), ("B_M200_clean", 200, False), ("C_M120_drift", 120, True)]
    N_DIM = 256
    SEEDS = [1, 2]
else:
    CELLS = [("A_M500_clean", 500, False), ("B_M1000_clean", 1000, False), ("C_M500_drift", 500, True)]
    N_DIM = N
    SEEDS = [7, 17, 23]


def build_patterns(M, n, drift, gen) -> np.ndarray:
    Xi = (gen.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    if drift:
        k = max(1, int(round(DRIFT_FRAC * M)))
        idx = gen.choice(M, size=k, replace=False)
        Xi[idx] = (gen.integers(0, 2, size=(k, n)) * 2 - 1).astype(np.float32)  # kappa_2-invariant swap
    return Xi


def _find(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def n_components(adj_pairs, M):
    parent = list(range(M))
    for a, b in adj_pairs:
        ra, rb = _find(parent, a), _find(parent, b)
        if ra != rb:
            parent[ra] = rb
    return len({_find(parent, i) for i in range(M)})


def beta0_curve(Xi):
    """beta_0(tau) over TAU_GRID using cosine-similarity edges (union-find)."""
    Xn = Xi / (np.linalg.norm(Xi, axis=1, keepdims=True) + 1e-8)
    S = Xn @ Xn.T
    M = Xi.shape[0]
    iu = np.triu_indices(M, k=1)
    sims = S[iu]
    curve = []
    for tau in TAU_GRID:
        mask = sims > tau
        pairs = list(zip(iu[0][mask].tolist(), iu[1][mask].tolist()))
        curve.append(n_components(pairs, M))
    return np.array(curve, dtype=np.float64)


def kappa2(Xi, n):
    W = (Xi.T @ Xi) / n
    return float(np.sum(W * W) / n)   # Tr(W^2)/N


def ks_stat(a, b):
    """Two-sample KS statistic (max CDF gap) on two 1-D arrays."""
    a = np.sort(a); b = np.sort(b)
    allv = np.concatenate([a, b])
    ca = np.searchsorted(a, allv, side="right") / len(a)
    cb = np.searchsorted(b, allv, side="right") / len(b)
    return float(np.max(np.abs(ca - cb)))


def ks_pvalue(d, n1, n2):
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * d
    s = 0.0
    for j in range(1, 101):
        s += (-1) ** (j - 1) * math.exp(-2.0 * j * j * lam * lam)
    p = 2.0 * s
    return float(min(max(p, 0.0), 1.0))


def mapper_nodes(Xi):
    """Mapper node count: filter=1st PCA coord; overlapping interval cover; single-linkage per interval."""
    Xc = Xi - Xi.mean(axis=0, keepdims=True)
    # 1st PCA coordinate via power iteration on covariance (cheap)
    v = np.random.default_rng(0).standard_normal(Xi.shape[1]).astype(np.float32)
    v /= np.linalg.norm(v) + 1e-8
    for _ in range(20):
        v = Xc.T @ (Xc @ v); v /= np.linalg.norm(v) + 1e-8
    f = Xc @ v
    lo, hi = float(f.min()), float(f.max())
    if hi - lo < 1e-9:
        return 1
    width = (hi - lo) / MAPPER_INTERVALS
    step = width * (1.0 - MAPPER_OVERLAP)
    nodes = 0
    start = lo
    while start < hi:
        end = start + width
        members = np.where((f >= start) & (f <= end))[0]
        if len(members) >= 2:
            Xm = Xi[members]
            Xn = Xm / (np.linalg.norm(Xm, axis=1, keepdims=True) + 1e-8)
            S = Xn @ Xn.T
            pairs = [(i, j) for i in range(len(members)) for j in range(i + 1, len(members))
                     if S[i, j] > MAPPER_LINK_TAU]
            nodes += n_components(pairs, len(members))
        elif len(members) == 1:
            nodes += 1
        start += step
    return int(nodes)


def _selftest():
    g = np.random.default_rng(0)
    Xi = (g.integers(0, 2, size=(10, 64)) * 2 - 1).astype(np.float32)
    # 1. union-find extremes
    assert n_components([(i, i + 1) for i in range(9)], 10) == 1, "chain should be 1 component"
    assert n_components([], 10) == 10, "no edges -> M components"
    # 2. KS of identical = 0
    a = np.array([1.0, 2.0, 3.0, 4.0])
    assert ks_stat(a, a.copy()) == 0.0, "KS of identical != 0"
    # 3. kappa2 > 0
    assert kappa2(Xi, 64) > 0
    print(f"[selftest] PASS: union-find extremes ok KS(identical)=0 kappa2={kappa2(Xi,64):.4f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = np.random.default_rng(seed)
    t0 = time.time()
    cells = {}
    curves = {}
    for name, M, drift in CELLS:
        Xi = build_patterns(M, n_dim, drift, gen)
        c = beta0_curve(Xi)
        k2 = kappa2(Xi, n_dim)
        mn = mapper_nodes(Xi)
        curves[name] = c
        cells[name] = {"M": M, "drift": drift, "beta0_curve": c.tolist(), "kappa2": k2, "mapper_nodes": mn}
        print(f"  [seed={seed} {name}] M={M} kappa2={k2:.4f} mapper_nodes={mn} "
              f"beta0[min..max]={int(c.min())}..{int(c.max())}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    names = [c[0] for c in CELLS]
    A, _, C = names[0], names[1], names[2]
    ks_ps, dk2s, mnodes = [], [], []
    for r in results:
        ca = np.array(r["cells"][A]["beta0_curve"]); cc = np.array(r["cells"][C]["beta0_curve"])
        d = ks_stat(ca, cc)
        ks_ps.append(ks_pvalue(d, len(ca), len(cc)))
        k2a, k2c = r["cells"][A]["kappa2"], r["cells"][C]["kappa2"]
        dk2s.append(abs(k2a - k2c) / (abs(k2a) + 1e-9))
        mnodes.append(r["cells"][A]["mapper_nodes"])
    mean_ksp = float(np.mean(ks_ps)); mean_dk2 = float(np.mean(dk2s)); mean_nodes = float(np.mean(mnodes))
    detects = mean_ksp < 0.05
    invariant = mean_dk2 < KAPPA2_INVARIANT
    summary = f"ks_p={mean_ksp:.4f} delta_kappa2={mean_dk2:.4f} mapper_nodes(A)={mean_nodes:.1f}"
    if not detects or mean_nodes < 1.5:
        return ("HARD_FAIL", f"HARD_FAIL: beta_0 insensitive to drift (ks_p>={0.05}) OR Mapper collapsed. {summary}")
    if detects and invariant and mean_nodes >= 5:
        return ("HARD_PASS", f"HARD_PASS: beta_0 detects a kappa_2-invariant drift (NEW topological info) "
                             f"AND Mapper>=5 nodes. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: detects but kappa_2 also moved (no new info) OR Mapper 2-4 nodes. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} mode={RUN_MODE} seeds={SEEDS} cells={[c[0] for c in CELLS]} "
      f"drift_frac={DRIFT_FRAC} tau_grid={len(TAU_GRID)}pts", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "cells": [c[0] for c in CELLS], "drift_frac": DRIFT_FRAC}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_DIM)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "drift_frac": DRIFT_FRAC,
    "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", {}), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
