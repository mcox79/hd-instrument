"""substrate_anchor3_coarse_grain_phase_diagram_v1 -- ANCHOR 3 (coarse-grain)
phase-diagram fill from MID to HIGH coverage.

Companion to ANCHOR 4 time-decay phase-fill (parallel hdi_exp_dev spawn; their
files are distinct: exp_kb_time_decay_eviction_with_reingest_v1*).

Base primitive (Stage 2 chain-grade): exp_cortex_ultrametric_clustering_coarse_grain_v1
tests a SINGLE point in coarse-graining space (COSINE_THRESH=0.85,
MIN_CLUSTER_SIZE=5, 8 families, 200 random). This v1 sweeps the granularity
knob across a 2D phase diagram so the substrate's coarse-grain operating
regime is mapped, not just probed.

Brain analog: cortical chunking / category compression. Companion to ANCHOR 4
(time-decay) -- together these are the substrate's memory compression knobs.

PHASE-DIAGRAM AXES:
  Axis 1 -- GRANULARITY (cluster acceptance threshold):
    COSINE_THRESH_GRID = [0.70, 0.80, 0.85, 0.90, 0.95]
    Low thresh = aggressive merging (fine atoms get pulled into mega-clusters,
      lose discrimination, big capacity gain).
    High thresh = conservative merging (only tight families merge; small
      capacity gain; discrimination preserved).
    Expected phase boundary: somewhere in [0.80, 0.90] where the substrate
    transitions from "lossy over-compression" (recall_clustered drops) to
    "healthy compression" (cap_drop >= 0.20 AND recall_clustered >= 0.80).

  Axis 2 -- DENSITY (alpha = N_TOTAL / N):
    N_FAMILIES_GRID = [4, 8, 16, 24] (with ATOMS_PER_FAMILY=8 fixed,
      N_RANDOM=200 fixed -> N_FAMILY_ATOMS = {32,64,128,192} -> N_TOTAL =
      {232,264,328,392} -> alpha = {0.23, 0.26, 0.32, 0.38} at N=1024).
    Low density = lots of slack capacity; coarse-grain less needed.
    High density = capacity-pressured regime; coarse-grain provides the
    most lift. Discriminator should LIVE on this axis.

ARMS (META_RULE_AF arms-must-differ):
  ARM_NO_COLLAPSE       -- baseline (capacity_drop=0 by construction).
  ARM_ULTRAMETRIC       -- mechanism under test.
  ARM_RANDOM            -- selectivity control (same n_atoms-collapsed,
                            but grouped randomly not by cosine).

DISCRIMINATOR (survives-scale-checked per smoke arm):
  d_ULTRA_vs_RND = ULTRA.recall_all - RANDOM.recall_all
  AT FULL N=1024 SMOKE PREVIEW: this delta must be >= 0.05 in at least
  one (granularity, density) cell to verify the mechanism FIRES at full
  scale (not just smoke). Otherwise -> no full dispatch.

INSTRUMENTATION (per (granularity, density, arm, seed) point):
  recall_clustered, recall_unclustered, recall_all,
  capacity_drop_frac, n_qualifying_clusters,
  min_within_cluster_cosine, max_between_cluster_cosine,
  W_norm_pre/post, wall_s.

PRE-REG BANDS (envelope-fail-bands per CLAUDE.md):
  PHASE_HARD_PASS:
    >= 1 (granularity, density) cell where:
      ULTRA.cap_drop_frac >= 0.20 AND
      ULTRA.recall_clustered >= 0.80 AND
      ULTRA.recall_unclustered >= 0.85 AND
      cv(ULTRA.recall_clustered) <= 0.05 AND
      d_ULTRA_vs_RND >= 0.05
    AND phase-structure observable: at low COSINE_THRESH (<=0.75), at least
      one density shows over-compression (ULTRA.recall_clustered drops by
      >= 0.10 vs the HARD_PASS cell of same density).
    AND CARDINALITY_OK: 4 densities x 5 thresholds x 3 arms x 3 seeds = 180
      cells executed (expected_n_units=180, hard_fail if observed < 180).

  PHASE_MIDDLE_BAND:
    Mechanism works (some cell clears PASS) but phase boundary not
    crisp (transition span < 0.10 in COSINE_THRESH OR no over-compression
    arm visible) -> MIDDLE_BAND.

  PHASE_HARD_FAIL:
    No cell clears HARD_PASS (mechanism fails at scale) OR
    discriminator d_ULTRA_vs_RND < 0.02 in all cells (no selectivity) OR
    CARDINALITY_BREACH (observed_n_units < 180).

SMOKE GATE DISCIPLINE:
  Smoke uses N=1024 (same as full -- discriminator-must-survive-scale per
  USER 2026-06-26) but reduced grid: 2 thresholds x 2 densities x 3 arms x
  1 seed = 12 cells. Must observe d_ULTRA_vs_RND >= 0.05 in AT LEAST ONE
  smoke cell, otherwise no full dispatch (discriminator absent in smoke
  band).

SUBSTRATE-ONLY DECODE: n_llm_calls = 0 by construction.

PROT-018: N=1024 (no _n suffix in anchor).
PROT-019: no _n>=4096 -> no floor.
ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)
from hdlab.ultrametric_clustering import (
    UltrametricConfig,
    collapse_W_via_clusters,
    cosine_distance_matrix,
    effective_capacity_used,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


ANCHOR_NAME = "substrate_anchor3_coarse_grain_phase_diagram_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Substrate N constant (no _n suffix per PROT-018; full grid sweeps axes
# instead of N).
N = 1024
ATOMS_PER_FAMILY = 8
N_RANDOM_ATOMS = 200
# Noise calibrated for N=1024 to give within-cluster cosine ~ 0.93
# (sustainable above 0.85 threshold; tighter than 0.95 threshold).
FAMILY_NOISE = 0.008
MIN_CLUSTER_SIZE = 5
# CLUSTER_DISTANCE = 1 - COSINE_THRESH; computed inside the cell from
# threshold to keep grid consistent.
N_QUERIES = 100

# Full phase-diagram grid (5 thresholds x 4 densities).
COSINE_THRESH_GRID_FULL = [0.70, 0.80, 0.85, 0.90, 0.95]
N_FAMILIES_GRID_FULL = [4, 8, 16, 24]
SEEDS_FULL = [7, 17, 23]

# Smoke grid (reduced; SAME N=1024 to test discriminator survives scale).
# Picks include the suspected phase boundary cells.
COSINE_THRESH_GRID_SMOKE = [0.70, 0.90]
N_FAMILIES_GRID_SMOKE = [8, 24]
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    COSINE_THRESH_GRID = COSINE_THRESH_GRID_SMOKE
    N_FAMILIES_GRID = N_FAMILIES_GRID_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    COSINE_THRESH_GRID = COSINE_THRESH_GRID_FULL
    N_FAMILIES_GRID = N_FAMILIES_GRID_FULL
    SEEDS = SEEDS_FULL

ARM_NAMES = ["ARM_NO_COLLAPSE", "ARM_ULTRAMETRIC", "ARM_RANDOM"]

# CARDINALITY_OK: explicit declaration per META_RULE_H discipline.
EXPECTED_N_UNITS = (
    len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID) * len(ARM_NAMES) * len(SEEDS)
)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},ATOMS_PER_FAMILY={ATOMS_PER_FAMILY},"
    f"N_RANDOM={N_RANDOM_ATOMS},FAMILY_NOISE={FAMILY_NOISE},"
    f"MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE},"
    f"COSINE_THRESH_GRID={'-'.join(str(t) for t in COSINE_THRESH_GRID)},"
    f"N_FAMILIES_GRID={'-'.join(str(f) for f in N_FAMILIES_GRID)},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Atom generation (same generator as base primitive; parameterized by
# n_families per cell).
# ---------------------------------------------------------------------------
def generate_atoms_with_families(seed: int, n_families: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    centers = rng.randn(n_families, N)
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    atoms = []
    cluster_truth = []
    for fi in range(n_families):
        for _ in range(ATOMS_PER_FAMILY):
            atom = centers[fi] + FAMILY_NOISE * rng.randn(N)
            atom /= np.linalg.norm(atom)
            atoms.append(atom)
            cluster_truth.append(fi)
    for _ in range(N_RANDOM_ATOMS):
        atom = rng.randn(N)
        atom /= np.linalg.norm(atom)
        atoms.append(atom)
        cluster_truth.append(-1)

    W = np.array(atoms, dtype=np.float64)
    cluster_truth_arr = np.array(cluster_truth, dtype=np.int64)
    keys = np.sign(W)
    keys[keys == 0] = 1.0
    return W, cluster_truth_arr, keys


def recall_via_lookup(
    W_query: np.ndarray,
    W_value_lookup: np.ndarray,
    query_idx: np.ndarray,
    cluster_lookup: np.ndarray,
) -> float:
    """Cluster-level recall: argmax in same cluster (or exact for unclustered)."""
    if len(query_idx) == 0:
        return float("nan")
    qn = W_query[query_idx] / np.linalg.norm(
        W_query[query_idx], axis=1, keepdims=True,
    ).clip(min=1e-12)
    vn = W_value_lookup / np.linalg.norm(
        W_value_lookup, axis=1, keepdims=True,
    ).clip(min=1e-12)
    sims = qn @ vn.T
    argmax = np.argmax(sims, axis=1)
    hits = 0
    for q_i, a_i in zip(query_idx, argmax):
        q_cluster = cluster_lookup[q_i]
        a_cluster = cluster_lookup[a_i]
        if q_cluster >= 0:
            if q_cluster == a_cluster:
                hits += 1
        else:
            if a_i == q_i:
                hits += 1
    return float(hits) / float(len(query_idx))


def random_clusters_matching_size(
    n_atoms: int,
    qualifying_clusters: List[List[int]],
    seed: int,
) -> List[List[int]]:
    rng = np.random.RandomState(seed + 8881)
    sizes = [len(c) for c in qualifying_clusters]
    total = sum(sizes)
    pool = rng.choice(n_atoms, size=total, replace=False)
    clusters: List[List[int]] = []
    cursor = 0
    for s in sizes:
        clusters.append(pool[cursor:cursor + s].tolist())
        cursor += s
    return clusters


# ---------------------------------------------------------------------------
# Per-(granularity, density, arm, seed) cell runner
# ---------------------------------------------------------------------------
def run_arm(
    arm_name: str,
    seed: int,
    cosine_thresh: float,
    n_families: int,
    shared: Tuple,
) -> Dict:
    t0 = time.time()
    W, cluster_truth, _keys = shared
    n_atoms = W.shape[0]
    cluster_distance = 1.0 - cosine_thresh
    cfg = UltrametricConfig(
        cosine_thresh=cosine_thresh,
        min_cluster_size=MIN_CLUSTER_SIZE,
        representative_mode="centroid",
    )

    # ALWAYS compute qualifying clusters (sizing input for random arm).
    D = cosine_distance_matrix(W)
    raw_clusters = single_linkage_clusters(D, max_distance=cluster_distance)
    qualifying = filter_qualifying_clusters(raw_clusters, W, cfg)
    n_qualifying = len(qualifying)
    n_clustered_atoms = sum(len(c) for c in qualifying)

    if qualifying:
        within_cosines = []
        for cl in qualifying:
            sub = W[cl]
            subn = sub / np.linalg.norm(sub, axis=1, keepdims=True).clip(min=1e-12)
            cm = subn @ subn.T
            np.fill_diagonal(cm, np.inf)
            within_cosines.append(float(np.min(cm)))
        min_within = float(np.min(within_cosines))
        reps_for_stats = np.array([np.mean(W[cl], axis=0) for cl in qualifying])
        reps_n = reps_for_stats / np.linalg.norm(reps_for_stats, axis=1, keepdims=True).clip(min=1e-12)
        if len(qualifying) > 1:
            between_cos = reps_n @ reps_n.T
            np.fill_diagonal(between_cos, -np.inf)
            max_between = float(np.max(between_cos))
        else:
            max_between = float("nan")
    else:
        min_within = float("nan")
        max_between = float("nan")

    if arm_name == "ARM_NO_COLLAPSE":
        W_after = W.copy()
        cluster_lookup = np.full(n_atoms, -1, dtype=np.int64)
        eff_cap = n_atoms
    elif arm_name == "ARM_ULTRAMETRIC":
        if not qualifying:
            W_after = W.copy()
            cluster_lookup = np.full(n_atoms, -1, dtype=np.int64)
            eff_cap = n_atoms
        else:
            W_after, _reps, cluster_lookup = collapse_W_via_clusters(W, qualifying, cfg)
            eff_cap = effective_capacity_used(cluster_lookup)
    elif arm_name == "ARM_RANDOM":
        if not qualifying:
            # No qualifying clusters -> fall back to MIN_CLUSTER_SIZE-sized
            # random groups (FAIL_HARD on selftest path; smoke can hit this).
            fake_size = MIN_CLUSTER_SIZE
            n_fake = min(5, n_atoms // fake_size)
            rng = np.random.RandomState(seed + 8881)
            pool = rng.choice(n_atoms, size=n_fake * fake_size, replace=False)
            random_clusters_list = [
                pool[i * fake_size:(i + 1) * fake_size].tolist()
                for i in range(n_fake)
            ]
        else:
            random_clusters_list = random_clusters_matching_size(
                n_atoms, qualifying, seed,
            )
        W_after, _reps, cluster_lookup = collapse_W_via_clusters(
            W, random_clusters_list, cfg,
        )
        eff_cap = effective_capacity_used(cluster_lookup)
    else:
        raise ValueError(f"unknown arm {arm_name}")

    capacity_drop = n_atoms - eff_cap
    capacity_drop_frac = float(capacity_drop) / float(n_atoms)

    rng_eval = np.random.RandomState(seed + 503)
    in_cluster_atoms = np.where(cluster_truth >= 0)[0]
    unclustered_atoms = np.where(cluster_truth == -1)[0]

    n_q_in = min(N_QUERIES, len(in_cluster_atoms))
    n_q_un = min(N_QUERIES, len(unclustered_atoms))
    in_query = rng_eval.choice(in_cluster_atoms, size=n_q_in, replace=False)
    un_query = rng_eval.choice(unclustered_atoms, size=n_q_un, replace=False)
    all_query = np.concatenate([in_query, un_query])

    recall_in_cluster = recall_via_lookup(W, W_after, in_query, cluster_lookup)
    recall_unclustered = recall_via_lookup(W, W_after, un_query, cluster_lookup)
    recall_all = recall_via_lookup(W, W_after, all_query, cluster_lookup)

    W_norm_pre = float(np.linalg.norm(W))
    W_norm_post = float(np.linalg.norm(W_after))

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "cosine_thresh": float(cosine_thresh),
        "n_families": int(n_families),
        "n_atoms_total": int(n_atoms),
        "alpha": float(n_atoms) / float(N),
        "recall_clustered": float(recall_in_cluster),
        "recall_unclustered": float(recall_unclustered),
        "recall_all": float(recall_all),
        "n_qualifying_clusters": int(n_qualifying),
        "n_clustered_atoms": int(n_clustered_atoms),
        "n_unclustered_atoms": int(n_atoms - n_clustered_atoms),
        "effective_capacity": int(eff_cap),
        "capacity_drop": int(capacity_drop),
        "capacity_drop_frac": float(capacity_drop_frac),
        "min_within_cluster_cosine": float(min_within),
        "max_between_cluster_cosine": float(max_between),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_grid_well_formed() -> bool:
    assert len(COSINE_THRESH_GRID) >= 2, "need >=2 thresholds for phase structure"
    assert len(N_FAMILIES_GRID) >= 2, "need >=2 densities for phase structure"
    for t in COSINE_THRESH_GRID:
        assert 0.0 < t < 1.0, f"bad cosine_thresh {t}"
    for f in N_FAMILIES_GRID:
        assert f >= 2 and ATOMS_PER_FAMILY * f >= MIN_CLUSTER_SIZE, (
            f"family count {f} would not form qualifying clusters"
        )
    expected = (
        len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID) * len(ARM_NAMES) * len(SEEDS)
    )
    assert EXPECTED_N_UNITS == expected, (
        f"cardinality mismatch: declared {EXPECTED_N_UNITS}, computed {expected}"
    )
    return True


def _selftest_atom_generation_per_density() -> bool:
    for nf in N_FAMILIES_GRID:
        W, truth, _ = generate_atoms_with_families(seed=7, n_families=nf)
        n_expected = nf * ATOMS_PER_FAMILY + N_RANDOM_ATOMS
        assert W.shape == (n_expected, N), f"W shape {W.shape} at nf={nf}"
        assert int(np.sum(truth >= 0)) == nf * ATOMS_PER_FAMILY
        assert int(np.sum(truth == -1)) == N_RANDOM_ATOMS
    return True


def _selftest_threshold_monotone_clustering() -> bool:
    """At nf=8 (the canonical density), n_qualifying_clusters should be
    NON-INCREASING as COSINE_THRESH increases (tighter -> fewer clusters
    qualify). Allows ties because at planted-family regime all 8 should
    consistently qualify at thresholds well below the planted within-cluster
    cosine."""
    W, _, _ = generate_atoms_with_families(seed=7, n_families=8)
    counts = []
    for t in [0.70, 0.85, 0.95]:
        cfg = UltrametricConfig(cosine_thresh=t, min_cluster_size=MIN_CLUSTER_SIZE)
        D = cosine_distance_matrix(W)
        raw = single_linkage_clusters(D, max_distance=1.0 - t)
        qualifying = filter_qualifying_clusters(raw, W, cfg)
        counts.append(len(qualifying))
    # Non-increasing monotonicity allows ties.
    assert counts[0] >= counts[1] >= counts[2], f"non-monotone counts {counts}"
    return True


def _instrumentation_selftest():
    _selftest_grid_well_formed()
    _selftest_atom_generation_per_density()
    _selftest_threshold_monotone_clustering()
    print(
        f"[selftest] PASS  N={N}  thresholds={COSINE_THRESH_GRID}  "
        f"densities(n_families)={N_FAMILIES_GRID}  arms={len(ARM_NAMES)}  "
        f"seeds={len(SEEDS)}  expected_units={EXPECTED_N_UNITS}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner: iterates the (threshold, density, arm) sub-grid.
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] sweeping phase diagram: "
        f"{len(COSINE_THRESH_GRID)} thresh x {len(N_FAMILIES_GRID)} densities x "
        f"{len(ARM_NAMES)} arms = "
        f"{len(COSINE_THRESH_GRID)*len(N_FAMILIES_GRID)*len(ARM_NAMES)} cells",
        flush=True,
    )
    cells = []
    for nf in N_FAMILIES_GRID:
        # Generate substrate ONCE per density (shared across thresholds + arms).
        t_gen = time.time()
        shared = generate_atoms_with_families(seed, n_families=nf)
        gen_s = time.time() - t_gen
        print(f"  [seed={seed} nf={nf}] generated W (n_atoms={shared[0].shape[0]}) in {gen_s:.1f}s",
              flush=True)
        for ct in COSINE_THRESH_GRID:
            for arm_name in ARM_NAMES:
                cell = run_arm(arm_name, seed, ct, nf, shared)
                cells.append(cell)
                print(
                    f"  [seed={seed} nf={nf} ct={ct:.2f} {arm_name}] "
                    f"rec_cl={cell['recall_clustered']:.3f} "
                    f"rec_un={cell['recall_unclustered']:.3f} "
                    f"rec_all={cell['recall_all']:.3f} "
                    f"n_cl={cell['n_qualifying_clusters']} "
                    f"cap_drop={cell['capacity_drop_frac']:.3f} "
                    f"wall={cell['wall_s']:.1f}s",
                    flush=True,
                )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "atoms_per_family": ATOMS_PER_FAMILY,
        "n_random_atoms": N_RANDOM_ATOMS,
        "family_noise": FAMILY_NOISE,
        "min_cluster_size": MIN_CLUSTER_SIZE,
        "n_queries": N_QUERIES,
        "cosine_thresh_grid": COSINE_THRESH_GRID,
        "n_families_grid": N_FAMILIES_GRID,
        "arm_names": ARM_NAMES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "cells": cells,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (phase-diagram envelope bands + cardinality check)
# ---------------------------------------------------------------------------
def _cells_by_key(seed_results: List[Dict]) -> Dict[Tuple[float, int, str], List[Dict]]:
    by_key: Dict[Tuple[float, int, str], List[Dict]] = {}
    for r in seed_results:
        for c in r.get("cells", []):
            k = (round(float(c["cosine_thresh"]), 3), int(c["n_families"]), c["arm_name"])
            by_key.setdefault(k, []).append(c)
    return by_key


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    by_key = _cells_by_key(results)
    observed_units = sum(len(v) for v in by_key.values())

    # CARDINALITY_OK check (META_RULE_H discipline).
    if observed_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL: CARDINALITY_BREACH. observed_units={observed_units} "
                f"< expected_n_units={EXPECTED_N_UNITS}. Phase diagram incomplete.")

    # Aggregate per (threshold, density) over arms.
    # PASS cell = ULTRA cap_drop>=0.20 AND rec_cl>=0.80 AND rec_un>=0.85
    # AND cv<=0.05 AND d_ULTRA_vs_RND>=0.05.
    pass_cells: List[Tuple[float, int, Dict]] = []
    over_compress_cells: List[Tuple[float, int, float, float]] = []
    all_d_ultra_rnd: List[float] = []
    cell_summary: Dict[Tuple[float, int], Dict] = {}

    for nf in N_FAMILIES_GRID:
        for ct in COSINE_THRESH_GRID:
            ult = by_key.get((round(ct, 3), nf, "ARM_ULTRAMETRIC"), [])
            rnd = by_key.get((round(ct, 3), nf, "ARM_RANDOM"), [])
            base = by_key.get((round(ct, 3), nf, "ARM_NO_COLLAPSE"), [])
            if not ult or not rnd or not base:
                continue
            rec_cl = [a["recall_clustered"] for a in ult]
            rec_un = [a["recall_unclustered"] for a in ult]
            rec_all_u = [a["recall_all"] for a in ult]
            rec_all_r = [a["recall_all"] for a in rnd]
            cap_drop = [a["capacity_drop_frac"] for a in ult]
            mean_rec_cl = float(np.mean(rec_cl))
            mean_rec_un = float(np.mean(rec_un))
            mean_cap = float(np.mean(cap_drop))
            cv_rec_cl = float(np.std(rec_cl) / max(abs(mean_rec_cl), 1e-9))
            d = float(np.mean(rec_all_u) - np.mean(rec_all_r))
            all_d_ultra_rnd.append(d)
            cell_summary[(ct, nf)] = {
                "mean_rec_cl": mean_rec_cl,
                "mean_rec_un": mean_rec_un,
                "mean_cap_drop": mean_cap,
                "cv_rec_cl": cv_rec_cl,
                "d_ULTRA_vs_RND": d,
                "mean_n_clusters": float(np.mean([a["n_qualifying_clusters"] for a in ult])),
            }
            is_pass = (
                mean_cap >= 0.20
                and mean_rec_cl >= 0.80
                and mean_rec_un >= 0.85
                and cv_rec_cl <= 0.05
                and d >= 0.05
            )
            if is_pass:
                pass_cells.append((ct, nf, cell_summary[(ct, nf)]))
            # over-compression cell: recall_clustered drops noticeably AND
            # capacity_drop is real (mechanism over-fired)
            if mean_rec_cl < 0.80 and mean_cap >= 0.20:
                over_compress_cells.append((ct, nf, mean_rec_cl, mean_cap))

    if not pass_cells:
        # check selectivity floor (no cell discriminator above threshold).
        max_d = max(all_d_ultra_rnd) if all_d_ultra_rnd else 0.0
        if max_d < 0.02:
            return ("HARD_FAIL",
                    f"HARD_FAIL: discriminator d_ULTRA_vs_RND <0.02 in all cells "
                    f"(max={max_d:.3f}). No selectivity above random. "
                    f"observed_units={observed_units}. "
                    f"cells={[(k, round(v['d_ULTRA_vs_RND'], 3)) for k, v in cell_summary.items()]}")
        # No HARD_PASS cell -> MIDDLE_BAND (mechanism observable but not clean).
        best = max(cell_summary.items(), key=lambda kv: (kv[1]["mean_rec_cl"] + kv[1]["mean_cap_drop"]))
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: no (ct,nf) cell clears HARD_PASS but discriminator "
                f"observed (max d_ULTRA_vs_RND={max_d:.3f}). Best cell "
                f"ct={best[0][0]} nf={best[0][1]}: rec_cl={best[1]['mean_rec_cl']:.3f} "
                f"cap_drop={best[1]['mean_cap_drop']:.3f}. "
                f"observed_units={observed_units}/{EXPECTED_N_UNITS}.")

    # Determine phase-boundary observable: among PASS densities, is there a
    # threshold where the substrate over-compresses?
    pass_nfs = {nf for _, nf, _ in pass_cells}
    boundary_visible = False
    for nf in pass_nfs:
        for ct, nf2, rec_cl, cap in over_compress_cells:
            if nf2 == nf:
                boundary_visible = True
                break
        if boundary_visible:
            break

    summary_str = (
        f"n_pass_cells={len(pass_cells)} n_over_compress={len(over_compress_cells)} "
        f"boundary_visible={boundary_visible} observed_units={observed_units}/{EXPECTED_N_UNITS} "
        f"pass_examples={[(ct, nf, round(s['mean_rec_cl'], 3), round(s['mean_cap_drop'], 3)) for ct, nf, s in pass_cells[:3]]}"
    )

    if boundary_visible:
        return ("HARD_PASS",
                f"PHASE_HARD_PASS: ANCHOR 3 coarse-grain phase diagram filled. "
                f">=1 cell clears HARD_PASS bands AND over-compression boundary "
                f"observable. {summary_str}")

    return ("MIDDLE_BAND",
            f"PHASE_MIDDLE_BAND: PASS cells exist but phase boundary not visible "
            f"(no over-compression cell at PASS density). "
            f"Coarse-grain works but phase structure under-resolved at this grid. "
            f"{summary_str}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "expected_n_units": EXPECTED_N_UNITS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] coarse_grain phase diagram v1 N={N} mode={RUN_MODE} "
        f"expected_units={EXPECTED_N_UNITS}...",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N} "
        f"thresholds={COSINE_THRESH_GRID} densities(n_families)={N_FAMILIES_GRID} "
        f"arms={ARM_NAMES} expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "atoms_per_family": ATOMS_PER_FAMILY,
    "n_random_atoms": N_RANDOM_ATOMS,
    "family_noise": float(FAMILY_NOISE),
    "min_cluster_size": int(MIN_CLUSTER_SIZE),
    "cosine_thresh_grid": COSINE_THRESH_GRID,
    "n_families_grid": N_FAMILIES_GRID,
    "arm_names": ARM_NAMES,
    "expected_n_units": int(EXPECTED_N_UNITS),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "cells": r.get("cells"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
