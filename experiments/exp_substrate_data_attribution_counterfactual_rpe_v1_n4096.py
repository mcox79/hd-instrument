"""
substrate_data_attribution_counterfactual_rpe_v1_n4096 -- CPE-vs-TracIn attribution on
a Hebbian AM substrate with KNOWN per-example influence structure.

PLAIN-LANGUAGE WHAT/WHY:
  Tests whether substrate counterfactual prediction error (CPE) -- computed via
  rank-1 weight substitution on a Hebbian associative memory -- can identify
  which training examples contributed to which test predictions, at lower
  compute cost than TracIn (the standard published-best data-attribution
  baseline).

  Synthetic ground truth: 5 influence groups x n_per_group examples; each
  group has a fixed bipolar "concept" pattern; group examples are noisy copies
  of that concept. Each test query is a noisy copy of one specific group's
  concept; the ground-truth most-influential train examples for that query
  are EXACTLY the n_per_group examples in that same group.

  Substrate "model" = sign(W @ query) where W = (1/N) Xi^T Xi (Hebbian write).

  Attribution methods:
    CPE: 1 - cos(sign(W q), sign(W_minus q)) where W_minus = W - (1/N) xi_e xi_e^T
    TracIn (Hebbian-linear relaxation): <-(q - W q) q^T, -(e - W e) e^T>
            = (q - W q)^T (e - W e) * (q^T e)

  For each query we compute the attribution score against every training
  example, then measure Spearman rho between the rank-ordering of attribution
  scores and the ground-truth in-group binary indicator (1 if example is in
  the query's group, 0 otherwise).

PRE-REGISTERED BANDS (per routing batch 2026-06-03 Experiment A):
  HARD-PASS: mean Spearman rho > 0.80 across all 5 seeds (CPE matches ground truth)
  MIDDLE:    mean rho in [0.50, 0.80] OR HP partial (3-4/5 seeds)
  HARD-FAIL: mean rho < 0.30 across 3+/5 seeds (CPE provides no attribution signal)

  TracIn is reported as secondary observable (no band; product-differentiation
  metric via wall-time ratio).

FORMULA SELF-TESTS (PROT-022) -- handled inside data_attribution._selftest():
  1. CPE on a stored bipolar pattern: deleting that pattern substantially
     changes sign(W @ pattern) -> high CPE.
  2. CPE of an unrelated random pattern on the same query: ~0 CPE.
  3. Vectorized CPE matches scalar CPE per row.
  4. TracIn same train/query is positive.
  5. Vectorized TracIn matches scalar TracIn per row.
  6. spearman_rho matches scipy on toy case (perfect +/-1 corr; random data).

PROT-018: anchor has _n4096; FULL N MUST = 4096. SMOKE N=512 documented.
PROT-021: per-seed checkpoint with run_config={N, n_per_group, n_queries, run_mode}.
PROT-022: formula selftests above; instrument-self-test below.

QUEUE: local CPU; <10 min wall at FULL.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from testbed.llm_integration.substrate_audit import build_W_from_patterns
from testbed.llm_integration.data_attribution import (
    compute_cpe_batch,
    compute_tracin_batch,
    spearman_rho,
)

ANCHOR_NAME = "substrate_data_attribution_counterfactual_rpe_v1_n4096"

_N_SUFFIX = 4096
N_FULL = 4096

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Number of influence groups (fixed; the core "5 concepts" structure)
N_GROUPS = 5

# Per-group noise: how many bits of the group concept are flipped to make each example
NOISE_FRAC_TRAIN = 0.20   # 20 percent bits flipped per train example
NOISE_FRAC_QUERY = 0.30   # 30 percent bits flipped per query (a bit harder)

if RUN_MODE == "smoke":
    N = 512
    N_PER_GROUP = 20
    N_QUERIES = 10
    SEEDS = [7, 17]
else:
    N = N_FULL
    N_PER_GROUP = 100
    N_QUERIES = 100
    SEEDS = [7, 17, 23, 31, 41]

M_TOTAL = N_GROUPS * N_PER_GROUP   # total train examples

# Pre-registered bands
HP_RHO_MIN = 0.80
HF_RHO_MAX = 0.30
MID_RHO_LOW = 0.50


def _instrumentation_selftest() -> None:
    """Tiny end-to-end smoke at very small scale, asserts metrics non-NaN."""
    rng = np.random.default_rng(0)
    n = 128
    n_per_group_t = 8
    n_queries_t = 4

    Xi_train, group_ids = build_corpus(rng, n, N_GROUPS, n_per_group_t, NOISE_FRAC_TRAIN)
    queries, q_groups = build_queries(rng, n, N_GROUPS, n_queries_t, NOISE_FRAC_QUERY,
                                       group_concepts=Xi_train[::n_per_group_t])
    W = build_W_from_patterns(Xi_train)

    cpe_rhos = []
    ti_rhos = []
    for qi in range(n_queries_t):
        q = queries[qi]
        gt = (group_ids == q_groups[qi]).astype(np.float64)
        cpe_scores = compute_cpe_batch(W, Xi_train, q)
        ti_scores = compute_tracin_batch(W, Xi_train, q)
        cpe_rhos.append(spearman_rho(cpe_scores, gt))
        ti_rhos.append(spearman_rho(ti_scores, gt))

    assert all(not np.isnan(r) for r in cpe_rhos), f"CPE rhos contain NaN: {cpe_rhos}"
    assert all(not np.isnan(r) for r in ti_rhos), f"TracIn rhos contain NaN: {ti_rhos}"
    print(f"[selftest] PASS: instrumentation smoke n={n} cpe_rho_mean="
          f"{float(np.mean(cpe_rhos)):.3f} ti_rho_mean={float(np.mean(ti_rhos)):.3f}",
          flush=True)


def build_group_concepts(rng: np.random.Generator, n_dim: int,
                         n_groups: int) -> np.ndarray:
    """Return (n_groups, n_dim) bipolar concept patterns -- one per group."""
    return rng.choice([-1.0, 1.0], size=(n_groups, n_dim)).astype(np.float32)


def _noisy_copy(concept: np.ndarray, noise_frac: float,
                rng: np.random.Generator) -> np.ndarray:
    """Bipolar pattern = concept with `noise_frac` of its bits flipped."""
    n = concept.shape[0]
    out = concept.copy()
    if noise_frac > 0:
        flip = rng.random(n) < noise_frac
        out[flip] *= -1.0
    return out


def build_corpus(rng: np.random.Generator, n_dim: int, n_groups: int,
                 n_per_group: int, noise_frac: float
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (Xi_train shape (M, N), group_ids shape (M,))."""
    concepts = build_group_concepts(rng, n_dim, n_groups)
    M = n_groups * n_per_group
    Xi = np.empty((M, n_dim), dtype=np.float32)
    group_ids = np.empty(M, dtype=np.int32)
    idx = 0
    for g in range(n_groups):
        for _ in range(n_per_group):
            Xi[idx] = _noisy_copy(concepts[g], noise_frac, rng)
            group_ids[idx] = g
            idx += 1
    return Xi, group_ids


def build_queries(rng: np.random.Generator, n_dim: int, n_groups: int,
                  n_queries: int, noise_frac: float,
                  group_concepts: np.ndarray = None
                  ) -> Tuple[np.ndarray, np.ndarray]:
    """Return (queries shape (Q, N), query_group_ids shape (Q,)).

    Each query is a noisy copy of one specific group concept.
    For test-train alignment, queries are derived from the SAME group concepts
    used to build the train corpus -- we expect the caller to pass them in via
    group_concepts. If group_concepts is None, fresh ones are drawn (used only
    by the instrument self-test).
    """
    if group_concepts is None:
        group_concepts = build_group_concepts(rng, n_dim, n_groups)
    # Round-robin: query g goes to group g % n_groups
    q_groups = (np.arange(n_queries) % n_groups).astype(np.int32)
    Q = np.empty((n_queries, n_dim), dtype=np.float32)
    for i in range(n_queries):
        Q[i] = _noisy_copy(group_concepts[q_groups[i]], noise_frac, rng)
    return Q, q_groups


def run_seed(seed: int, n_dim: int, n_per_group: int, n_queries: int) -> Dict:
    t0 = time.time()
    rng = np.random.default_rng(seed)

    # Build group concepts FIRST so queries and corpus share them
    concepts = build_group_concepts(rng, n_dim, N_GROUPS)

    # Train corpus
    M = N_GROUPS * n_per_group
    Xi_train = np.empty((M, n_dim), dtype=np.float32)
    group_ids = np.empty(M, dtype=np.int32)
    idx = 0
    for g in range(N_GROUPS):
        for _ in range(n_per_group):
            Xi_train[idx] = _noisy_copy(concepts[g], NOISE_FRAC_TRAIN, rng)
            group_ids[idx] = g
            idx += 1

    # Queries
    queries, q_groups = build_queries(rng, n_dim, N_GROUPS, n_queries,
                                       NOISE_FRAC_QUERY, group_concepts=concepts)

    # Substrate
    t_W = time.time()
    W = build_W_from_patterns(Xi_train)
    t_W_elapsed = time.time() - t_W

    # CPE
    t_cpe_start = time.time()
    cpe_rhos = np.empty(n_queries, dtype=np.float64)
    for qi in range(n_queries):
        q = queries[qi]
        gt = (group_ids == q_groups[qi]).astype(np.float64)
        cpe_scores = compute_cpe_batch(W, Xi_train, q)
        cpe_rhos[qi] = spearman_rho(cpe_scores, gt)
    t_cpe = time.time() - t_cpe_start

    # TracIn
    t_ti_start = time.time()
    ti_rhos = np.empty(n_queries, dtype=np.float64)
    for qi in range(n_queries):
        q = queries[qi]
        gt = (group_ids == q_groups[qi]).astype(np.float64)
        ti_scores = compute_tracin_batch(W, Xi_train, q)
        ti_rhos[qi] = spearman_rho(ti_scores, gt)
    t_ti = time.time() - t_ti_start

    mean_cpe_rho = float(np.mean(cpe_rhos))
    min_cpe_rho = float(np.min(cpe_rhos))
    max_cpe_rho = float(np.max(cpe_rhos))
    mean_ti_rho = float(np.mean(ti_rhos))
    min_ti_rho = float(np.min(ti_rhos))
    max_ti_rho = float(np.max(ti_rhos))

    wall_ratio_cpe_over_tracin = float(t_cpe / max(t_ti, 1e-9))

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim} M={M} Q={n_queries}] "
          f"CPE rho mean={mean_cpe_rho:.4f} min={min_cpe_rho:.4f} max={max_cpe_rho:.4f} "
          f"({t_cpe:.2f}s) | "
          f"TracIn rho mean={mean_ti_rho:.4f} min={min_ti_rho:.4f} max={max_ti_rho:.4f} "
          f"({t_ti:.2f}s) | "
          f"wall_ratio CPE/TI={wall_ratio_cpe_over_tracin:.2f} | "
          f"elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed,
        "N": n_dim,
        "n_per_group": n_per_group,
        "n_queries": n_queries,
        "n_groups": N_GROUPS,
        "M": M,
        "run_mode": RUN_MODE,
        "noise_frac_train": NOISE_FRAC_TRAIN,
        "noise_frac_query": NOISE_FRAC_QUERY,
        "cpe_rho_mean": mean_cpe_rho,
        "cpe_rho_min": min_cpe_rho,
        "cpe_rho_max": max_cpe_rho,
        "cpe_rho_per_query": cpe_rhos.tolist(),
        "tracin_rho_mean": mean_ti_rho,
        "tracin_rho_min": min_ti_rho,
        "tracin_rho_max": max_ti_rho,
        "tracin_rho_per_query": ti_rhos.tolist(),
        "wall_W_build_s": float(t_W_elapsed),
        "wall_cpe_s": float(t_cpe),
        "wall_tracin_s": float(t_ti),
        "wall_ratio_cpe_over_tracin": wall_ratio_cpe_over_tracin,
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    cpe_means = [r["cpe_rho_mean"] for r in results]
    ti_means = [r["tracin_rho_mean"] for r in results]
    wall_ratios = [r["wall_ratio_cpe_over_tracin"] for r in results]

    mean_cpe = float(np.mean(cpe_means))
    min_cpe = float(np.min(cpe_means))
    mean_ti = float(np.mean(ti_means))
    mean_wall_ratio = float(np.mean(wall_ratios))
    n_seeds = len(results)

    n_above_hp = sum(1 for v in cpe_means if v > HP_RHO_MIN)
    n_below_hf = sum(1 for v in cpe_means if v < HF_RHO_MAX)

    summary = (
        f"CPE rho: mean={mean_cpe:.4f} min={min_cpe:.4f} (HP>{HP_RHO_MIN} HF<{HF_RHO_MAX}) "
        f"n_above_HP={n_above_hp}/{n_seeds} n_below_HF={n_below_hf}/{n_seeds} | "
        f"TracIn rho mean={mean_ti:.4f} | "
        f"wall ratio CPE/TracIn={mean_wall_ratio:.2f} | "
        f"N={results[0]['N']} M={results[0]['M']} Q={results[0]['n_queries']}"
    )

    # Capability implication for verdict_msg
    if mean_ti > 1e-6:
        cheap_factor = 1.0 / mean_wall_ratio if mean_wall_ratio > 0 else float("nan")
        impl = (f"CPE attribution rho={mean_cpe:.3f} "
                f"({cheap_factor:.2f}x wall vs TracIn baseline rho={mean_ti:.3f}) -> "
                "substrate-native data attribution")
    else:
        impl = (f"CPE attribution rho={mean_cpe:.3f} -> "
                "substrate-native data attribution")

    # HP requires every seed above HP threshold (per spec)
    if n_above_hp == n_seeds and min_cpe > HP_RHO_MIN:
        return ("HARD_PASS",
                f"HARD_PASS: {impl} viable. All {n_seeds} seeds > {HP_RHO_MIN}. {summary}")

    # HF requires majority below HF
    if n_below_hf >= max(1, (n_seeds + 1) // 2 + (1 if n_seeds > 2 else 0)):
        # Above is "3+/5" rule generalized: ceil(0.6 * n_seeds)
        pass
    n_below_hf_for_hf = sum(1 for v in cpe_means if v < HF_RHO_MAX)
    hf_threshold_seeds = 3 if n_seeds >= 5 else max(1, (n_seeds + 1) // 2)
    if n_below_hf_for_hf >= hf_threshold_seeds:
        return ("HARD_FAIL",
                f"HARD_FAIL: {impl} non-viable. {n_below_hf_for_hf}/{n_seeds} seeds below "
                f"{HF_RHO_MAX}. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: {impl} partial. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


print(f"[config] PROT-018 anchor_N={_N_SUFFIX} run_N={N} M={M_TOTAL} "
      f"n_per_group={N_PER_GROUP} n_queries={N_QUERIES} "
      f"n_groups={N_GROUPS} mode={RUN_MODE} seeds={SEEDS}", flush=True)
_prot018_startup_check(N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {
    "N": N,
    "n_per_group": N_PER_GROUP,
    "n_queries": N_QUERIES,
    "run_mode": RUN_MODE,
}

done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N, N_PER_GROUP, N_QUERIES)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

verdict, verdict_msg = compute_verdict(all_results)
elapsed_total = time.time() - t_sweep

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] total={elapsed_total:.2f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "M": M_TOTAL,
    "n_groups": N_GROUPS,
    "n_per_group": N_PER_GROUP,
    "n_queries": N_QUERIES,
    "noise_frac_train": NOISE_FRAC_TRAIN,
    "noise_frac_query": NOISE_FRAC_QUERY,
    "run_mode": RUN_MODE,
    "seeds": SEEDS,
    "n_seeds": len(all_results),
    "elapsed_s": elapsed_total,
    "pre_reg_bands": {
        "HARD_PASS_rho_min": HP_RHO_MIN,
        "MIDDLE_rho_low": MID_RHO_LOW,
        "HARD_FAIL_rho_max": HF_RHO_MAX,
    },
    "per_seed": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
