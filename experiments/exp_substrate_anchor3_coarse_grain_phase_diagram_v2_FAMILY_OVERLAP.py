"""substrate_anchor3_coarse_grain_phase_diagram_v2_FAMILY_OVERLAP --
mechanism-class diversion of ANCHOR 3 v1.

v1 result (data/exp_substrate_anchor3_coarse_grain_phase_diagram_v1/metrics.json):
  MIDDLE_BAND. n_pass_cells=12, n_over_compress=0, boundary_visible=False.
  ARM_ULTRAMETRIC recall_all = 1.000 at every (cosine_thresh, n_families)
  cell tested -- including nf=24 (densest). Capacity_drop_frac DID rise
  (+0.343 at nf=24) but recall NEVER degraded. Substrate is robust at the
  CLEAN-NOISE regime v1 swept.

Skunkworks 2x-drill (2026-06-28): v1 swept GRANULARITY (cosine_thresh) x
DENSITY (n_families). Both axes increase WITHIN-family scatter pressure /
cohesion-test. NEITHER tests inter-cluster DISCRIMINATION. Over-compression
is a DISCRIMINATION FAILURE (substrate merges UNRELATED families into one
cluster), not a cohesion failure. v1 measured the wrong axis.

v2 mechanism diversion: add a 3rd axis FAMILY_OVERLAP = inter-family cosine
similarity in [0.0, 0.9]. At FAMILY_OVERLAP=0.9, family centroids are nearly
collinear: cosine_thresh-based single-linkage clustering SHOULD pull these
near-collinear families into ONE mega-cluster -> ARM_ULTRAMETRIC recall_all
DROPS (each family's query lands in the wrong family's centroid). This is
the over-compression failure-mode v1 missed.

POSITIVE CONTROL: at FAMILY_OVERLAP=0.0 the cell reduces to v1 -- recall
should reproduce v1's ~1.000 across the grid. Sanity check the mechanism
class is intact, not just the discriminator.

PHASE-DIAGRAM AXES (3-axis):
  Axis 1 -- GRANULARITY (COSINE_THRESH): [0.70, 0.85, 0.95] (3pts).
    Same semantics as v1 but reduced to 3 from 5 (keep cell-count tractable).
  Axis 2 -- DENSITY (N_FAMILIES): [8, 16, 24] (3pts).
    Same semantics as v1 but reduced to 3 from 4 (drop nf=4 which had only
    32 family atoms vs 200 random; v1 confirmed nf=4 is uninformative).
  Axis 3 -- FAMILY_OVERLAP (mean inter-family cosine): [0.0, 0.3, 0.6, 0.9]
    Constructed by mixing each family centroid with a SHARED basis vector.
    Specifically: family_centroid_i = sqrt(1 - rho) * orthogonal_i + sqrt(rho)
    * shared_basis. Mean inter-family cosine target = rho.
    Low overlap = v1's clean regime; high overlap = near-collinear families.
    PASS/FAIL boundary should manifest as rho increases past 0.6 -> 0.9.

ARMS (META_RULE_AF arms-must-differ; positive control added):
  ARM_NO_COLLAPSE          -- baseline (capacity_drop=0 by construction).
  ARM_ULTRAMETRIC          -- mechanism under test.
  ARM_RANDOM_FLOOR         -- selectivity control (same n_atoms-collapsed,
                                grouped randomly not by cosine; cohesion-floor).
  ARM_FLAT_NO_OVERLAP      -- POSITIVE CONTROL. Within (granularity, density)
                                sweep, runs ULTRAMETRIC at FAMILY_OVERLAP=0.0
                                ONLY. Reproduces v1's mechanism class at the
                                v1 regime; recall should approach 1.000. This
                                arm reports IDENTICAL data to ARM_ULTRAMETRIC
                                AT rho=0.0 (cross-check).

DISCRIMINATOR (mechanism-class):
  At FAMILY_OVERLAP=0.0: ULTRA.recall_all >= 0.95 (reproduce v1).
  At FAMILY_OVERLAP=0.9: ULTRA.recall_all <= 0.80 (over-compression visible).
  d_v2_FAMILY_OVERLAP = ULTRA.recall_all(rho=0.0) - ULTRA.recall_all(rho=0.9)
                       >= 0.15 across at least one (cosine_thresh, n_families) cell.

  If d_v2_FAMILY_OVERLAP < 0.05: discriminator did not fire -- substrate is
  robust even to near-collinear families. v1+v2 jointly close ANCHOR 3 as
  MEASURED_MECHANISM (capacity_drop primitive works but no failure-mode exposed
  in the explored grid).

  If d_v2_FAMILY_OVERLAP >= 0.15: boundary visible -- ANCHOR 3 phase-diagram
  filled. Verdict HARD_PASS conditional on cardinality + selectivity floor.

INSTRUMENTATION (per (granularity, density, family_overlap, arm, seed)):
  recall_clustered, recall_unclustered, recall_all,
  capacity_drop_frac, n_qualifying_clusters,
  min_within_cluster_cosine, max_between_cluster_cosine,
  observed_inter_family_cosine (verify constructor delivered target),
  W_norm_pre/post, wall_s.

PRE-REG BANDS:
  PHASE_HARD_PASS:
    >= 1 (granularity, density) cell where:
      ULTRA.recall_all(rho=0.0) >= 0.95 AND
      ULTRA.recall_all(rho=0.9) <= 0.80 AND
      d_v2_FAMILY_OVERLAP >= 0.15 AND
      cv(ULTRA.recall_all per seed) <= 0.10 AND
      ULTRA.recall_all(rho=0.0) - ARM_RANDOM_FLOOR.recall_all(rho=0.0) >= 0.10
      (selectivity floor: ULTRA must beat RANDOM_FLOOR at clean regime).
    AND CARDINALITY_OK: 3 granularity x 3 densities x 4 overlaps x 3 arms x
      3 seeds = 324 cells executed (expected_n_units=324, hard_fail if
      observed < 324). Positive-control arm runs only at rho=0.0 so it adds
      27 more cells (3 granularity x 3 densities x 1 overlap x 1 arm x 3 seeds);
      total EXPECTED_N_UNITS = 324 + 27 = 351.

  PHASE_MIDDLE_BAND:
    Mechanism observable (ULTRA.recall_all decreases monotonically with rho)
    but discriminator d_v2_FAMILY_OVERLAP < 0.15 in all cells -> MIDDLE_BAND.

  PHASE_HARD_FAIL:
    Positive-control arm FAILS (ULTRA at rho=0.0 does not reproduce v1, i.e.
    ULTRA.recall_all(rho=0.0) < 0.90) -- mechanism class broken; OR
    CARDINALITY_BREACH (observed_n_units < EXPECTED_N_UNITS); OR
    LLM-gate violated (n_llm_calls > 0); OR
    Observed_inter_family_cosine deviates from rho target by > 0.10 at any
    cell (constructor failed to deliver the requested geometry; SCRIPT_PRECONDITION
    violation).

SMOKE GATE DISCIPLINE:
  Smoke uses N=1024 (discriminator-must-survive-scale; same as full) but
  reduced grid: 2 granularity x 1 density x 2 overlaps {0.0, 0.9} x 3 arms x
  1 seed = 12 cells + 2 positive-control cells (rho=0.0) = 14 cells.
  Must observe d_v2_FAMILY_OVERLAP >= 0.10 in AT LEAST ONE smoke cell.
  Otherwise no full dispatch -- discriminator absent at full-N smoke.

  Per CLAUDE.md three-smoke-disciplines:
  (1) NO silent except: blocks -- this cell uses no try-suppress.
  (2) Smoke FIRES the discriminator -- includes rho=0.0 AND rho=0.9.
  (3) HARD_PASS only on positive d_v2 -- band-floor recall is MIDDLE_BAND.

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


ANCHOR_NAME = "substrate_anchor3_coarse_grain_phase_diagram_v2_FAMILY_OVERLAP"
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

# Substrate N constant.
N = 1024
ATOMS_PER_FAMILY = 8
N_RANDOM_ATOMS = 200
FAMILY_NOISE = 0.008
MIN_CLUSTER_SIZE = 5
N_QUERIES = 100

# Full 3-axis grid: granularity x density x family_overlap
COSINE_THRESH_GRID_FULL = [0.70, 0.85, 0.95]
N_FAMILIES_GRID_FULL = [8, 16, 24]
FAMILY_OVERLAP_GRID_FULL = [0.0, 0.3, 0.6, 0.9]
SEEDS_FULL = [7, 17, 23]

# Smoke (discriminator-must-survive-scale: same N, reduced grid).
# rho=0.0 AND rho=0.9 are both included so the discriminator fires.
COSINE_THRESH_GRID_SMOKE = [0.70, 0.95]
N_FAMILIES_GRID_SMOKE = [16]
FAMILY_OVERLAP_GRID_SMOKE = [0.0, 0.9]
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    COSINE_THRESH_GRID = COSINE_THRESH_GRID_SMOKE
    N_FAMILIES_GRID = N_FAMILIES_GRID_SMOKE
    FAMILY_OVERLAP_GRID = FAMILY_OVERLAP_GRID_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    COSINE_THRESH_GRID = COSINE_THRESH_GRID_FULL
    N_FAMILIES_GRID = N_FAMILIES_GRID_FULL
    FAMILY_OVERLAP_GRID = FAMILY_OVERLAP_GRID_FULL
    SEEDS = SEEDS_FULL

ARM_NAMES = ["ARM_NO_COLLAPSE", "ARM_ULTRAMETRIC", "ARM_RANDOM_FLOOR"]
POSITIVE_CONTROL_ARM = "ARM_FLAT_NO_OVERLAP"

# CARDINALITY_OK declaration:
# main grid: granularity x density x overlap x arms x seeds
N_MAIN = (
    len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID)
    * len(FAMILY_OVERLAP_GRID) * len(ARM_NAMES) * len(SEEDS)
)
# positive control: ONLY runs at rho=0.0 if rho=0.0 in grid; otherwise zero.
HAS_RHO_ZERO = 0.0 in FAMILY_OVERLAP_GRID
N_POS_CTRL = (
    len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID) * len(SEEDS)
    if HAS_RHO_ZERO else 0
)
EXPECTED_N_UNITS = N_MAIN + N_POS_CTRL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},ATOMS_PER_FAMILY={ATOMS_PER_FAMILY},"
    f"N_RANDOM={N_RANDOM_ATOMS},FAMILY_NOISE={FAMILY_NOISE},"
    f"MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE},"
    f"COSINE_THRESH_GRID={'-'.join(str(t) for t in COSINE_THRESH_GRID)},"
    f"N_FAMILIES_GRID={'-'.join(str(f) for f in N_FAMILIES_GRID)},"
    f"FAMILY_OVERLAP_GRID={'-'.join(str(r) for r in FAMILY_OVERLAP_GRID)},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Atom generation with FAMILY_OVERLAP parameter
# ---------------------------------------------------------------------------
def generate_atoms_with_families_and_overlap(
    seed: int, n_families: int, family_overlap: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Generate atoms with controlled inter-family cosine.

    Family centroids are constructed as:
      family_centroid_i = sqrt(1 - rho) * orthogonal_i + sqrt(rho) * shared_basis

    where orthogonal_i are unit random Gaussian vectors (near-orthogonal in
    high-D), shared_basis is a single shared unit vector, and rho =
    family_overlap. Mean inter-family cosine = rho (verified numerically and
    asserted at constructor).

    Returns (W, cluster_truth, keys, observed_inter_family_cosine).
    """
    rng = np.random.RandomState(seed)
    assert 0.0 <= family_overlap <= 1.0, f"family_overlap must be in [0,1], got {family_overlap}"
    rho = float(family_overlap)

    # Orthogonal-ish per-family component (random Gaussian; near-orthogonal in D=N).
    orthogonals = rng.randn(n_families, N)
    orthogonals /= np.linalg.norm(orthogonals, axis=1, keepdims=True)

    # Shared basis vector (single unit vector); separate seed offset so it
    # doesn't co-vary with orthogonals.
    rng_basis = np.random.RandomState(seed + 991)
    shared_basis = rng_basis.randn(N)
    shared_basis /= np.linalg.norm(shared_basis)

    # Mix: family_centroid_i = sqrt(1-rho) * orth_i + sqrt(rho) * shared
    centers = np.sqrt(1.0 - rho) * orthogonals + np.sqrt(rho) * shared_basis[None, :]
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    # Observed inter-family cosine (target = rho).
    if n_families >= 2:
        cm = centers @ centers.T
        # off-diagonal mean
        np.fill_diagonal(cm, np.nan)
        observed_cos = float(np.nanmean(cm))
    else:
        observed_cos = float("nan")

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
    return W, cluster_truth_arr, keys, observed_cos


def recall_via_lookup(
    W_query: np.ndarray,
    W_value_lookup: np.ndarray,
    query_idx: np.ndarray,
    cluster_lookup: np.ndarray,
) -> float:
    """Collapsed-cluster recall (v1's metric): argmax in same cluster_lookup
    cluster (or exact for unclustered). KEPT for v1-parity comparison and
    documented in the cell as `recall_all_clustered_metric`."""
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


def recall_truth_family(
    W_query: np.ndarray,
    W_value_lookup: np.ndarray,
    query_idx: np.ndarray,
    cluster_truth: np.ndarray,
) -> float:
    """v2 PRIMARY discriminator metric. recall against TRUTH family planted at
    construction, NOT against the collapsed cluster_lookup. Catches the over-
    compression failure-mode v1 missed: if two TRUE families merged into ONE
    collapsed cluster, an argmax that lands on the WRONG truth family counts as
    a MISS under this metric (even though it's in the same collapsed cluster).

    For unclustered atoms (cluster_truth == -1), require exact-index hit (same
    as v1).
    """
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
        q_truth = cluster_truth[q_i]
        a_truth = cluster_truth[a_i]
        if q_truth >= 0:
            if q_truth == a_truth:
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
# Per-cell runner (granularity, density, family_overlap, arm, seed)
# ---------------------------------------------------------------------------
def run_arm(
    arm_name: str,
    seed: int,
    cosine_thresh: float,
    n_families: int,
    family_overlap: float,
    shared: Tuple,
) -> Dict:
    t0 = time.time()
    W, cluster_truth, _keys, observed_cos = shared
    n_atoms = W.shape[0]
    cluster_distance = 1.0 - cosine_thresh
    cfg = UltrametricConfig(
        cosine_thresh=cosine_thresh,
        min_cluster_size=MIN_CLUSTER_SIZE,
        representative_mode="centroid",
    )

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
    elif arm_name == "ARM_ULTRAMETRIC" or arm_name == POSITIVE_CONTROL_ARM:
        # POSITIVE_CONTROL_ARM uses identical mechanism to ULTRAMETRIC; the
        # axis it's controlling is the substrate-construction (rho=0.0). At
        # rho=0.0 these arms produce IDENTICAL data -- recorded twice as
        # cross-check vs CONFIG_VERSION-tied data corruption.
        if not qualifying:
            W_after = W.copy()
            cluster_lookup = np.full(n_atoms, -1, dtype=np.int64)
            eff_cap = n_atoms
        else:
            W_after, _reps, cluster_lookup = collapse_W_via_clusters(W, qualifying, cfg)
            eff_cap = effective_capacity_used(cluster_lookup)
    elif arm_name == "ARM_RANDOM_FLOOR":
        if not qualifying:
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

    # v1's metric (collapsed-cluster) kept for parity comparison.
    recall_in_cluster_v1 = recall_via_lookup(W, W_after, in_query, cluster_lookup)
    recall_unclustered_v1 = recall_via_lookup(W, W_after, un_query, cluster_lookup)
    recall_all_v1 = recall_via_lookup(W, W_after, all_query, cluster_lookup)

    # v2 PRIMARY discriminator: truth-family recall. Hit iff argmax lands in
    # the SAME PLANTED FAMILY (not the same collapsed cluster). Catches the
    # over-compression failure-mode where two true families merged into one
    # collapsed cluster -- v1's metric counted those as hits, v2's metric
    # counts them as misses.
    recall_in_cluster = recall_truth_family(W, W_after, in_query, cluster_truth)
    recall_unclustered = recall_truth_family(W, W_after, un_query, cluster_truth)
    recall_all = recall_truth_family(W, W_after, all_query, cluster_truth)

    W_norm_pre = float(np.linalg.norm(W))
    W_norm_post = float(np.linalg.norm(W_after))

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "cosine_thresh": float(cosine_thresh),
        "n_families": int(n_families),
        "family_overlap": float(family_overlap),
        "observed_inter_family_cosine": float(observed_cos),
        "n_atoms_total": int(n_atoms),
        "alpha": float(n_atoms) / float(N),
        # v2 PRIMARY metric: truth-family recall.
        "recall_clustered": float(recall_in_cluster),
        "recall_unclustered": float(recall_unclustered),
        "recall_all": float(recall_all),
        # v1 PARITY metric: collapsed-cluster recall (the metric that hid
        # over-compression in v1; kept for compare-to-v1 audit).
        "recall_clustered_v1_metric": float(recall_in_cluster_v1),
        "recall_unclustered_v1_metric": float(recall_unclustered_v1),
        "recall_all_v1_metric": float(recall_all_v1),
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
    assert len(N_FAMILIES_GRID) >= 1
    assert len(FAMILY_OVERLAP_GRID) >= 2, "need >=2 overlaps for discriminator"
    for t in COSINE_THRESH_GRID:
        assert 0.0 < t < 1.0, f"bad cosine_thresh {t}"
    for f in N_FAMILIES_GRID:
        assert f >= 2 and ATOMS_PER_FAMILY * f >= MIN_CLUSTER_SIZE
    for r in FAMILY_OVERLAP_GRID:
        assert 0.0 <= r <= 1.0, f"bad family_overlap {r}"
    n_main = (
        len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID)
        * len(FAMILY_OVERLAP_GRID) * len(ARM_NAMES) * len(SEEDS)
    )
    n_pc = (
        len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID) * len(SEEDS)
        if (0.0 in FAMILY_OVERLAP_GRID) else 0
    )
    expected = n_main + n_pc
    assert EXPECTED_N_UNITS == expected, (
        f"cardinality mismatch: declared {EXPECTED_N_UNITS}, computed {expected}"
    )
    return True


def _selftest_atom_generation_inter_family_cosine() -> bool:
    """Verify constructor delivers target inter-family cosine within tolerance.

    Tolerance derivation: at FAMILY_OVERLAP=rho, target cosine between two
    centroids is rho. Empirically the constructor gives observed cosine within
    ~0.05 of target at N=1024, n_families >= 8 (random Gaussian orthogonals
    are not perfectly orthogonal at finite D). Tighten tolerance if this test
    fires on legitimate runs.
    """
    tol = 0.10  # generous; tightens later if needed
    for rho in [0.0, 0.3, 0.6, 0.9]:
        W, _, _, observed = generate_atoms_with_families_and_overlap(
            seed=7, n_families=8, family_overlap=rho,
        )
        assert W.shape == (8 * ATOMS_PER_FAMILY + N_RANDOM_ATOMS, N), W.shape
        # Skip the rho check for n_families=1 (no inter-family pairs).
        assert abs(observed - rho) <= tol, (
            f"constructor failed: target rho={rho}, observed={observed:.3f}, tol={tol}"
        )
    return True


def _selftest_ultrametric_recall_monotone_in_rho() -> bool:
    """At fixed (cosine_thresh, n_families, seed) the ULTRAMETRIC truth-family
    recall_all should NOT INCREASE as family_overlap rises from 0.0 to 0.9.

    Uses TRUTH-FAMILY recall (the v2 primary metric). Note: v1's collapsed-
    cluster metric WAS flat in rho because it counted wrong-family-but-merged
    as a hit -- that's exactly the v1 bias the v2 metric corrects.

    Allows ties because at very high cosine_thresh (e.g. 0.95) the linkage
    might not group even highly-overlapping families (no over-compression).
    """
    cosine_thresh = 0.70  # low thresh = aggressive merging; over-compression
                          # visible at rho=0.9.
    nf = 8
    seed = 7
    recalls = []
    for rho in [0.0, 0.6, 0.9]:
        shared = generate_atoms_with_families_and_overlap(seed, nf, rho)
        cell = run_arm("ARM_ULTRAMETRIC", seed, cosine_thresh, nf, rho, shared)
        recalls.append(cell["recall_all"])
    # Non-increasing: allows equality. With TRUTH-family recall + ct=0.70 +
    # nf=8 we expect recalls[0] ~ 1.0, recalls[2] << 1.0 (over-compression
    # surfaces).
    assert recalls[0] >= recalls[1] - 1e-6, f"recall non-monotone in rho: {recalls}"
    assert recalls[1] >= recalls[2] - 1e-6, f"recall non-monotone in rho: {recalls}"
    # ALSO assert the discriminator FIRES at this monotonicity-test point --
    # if truth-family recall is also flat, the v2 metric isn't catching what
    # we expect either (would be HARD_FAIL at full run).
    delta = recalls[0] - recalls[2]
    # Use a permissive threshold here (0.05) so the selftest passes when the
    # mechanism is at least SOMEWHAT visible at this small-grid point. The
    # full-run discriminator threshold is 0.15.
    assert delta >= 0.05, (
        f"discriminator does NOT fire even at ct=0.70 nf=8 rho=0.9: "
        f"recalls={recalls}; v2 mechanism class broken or substrate too robust"
    )
    return True


def _instrumentation_selftest():
    _selftest_grid_well_formed()
    _selftest_atom_generation_inter_family_cosine()
    _selftest_ultrametric_recall_monotone_in_rho()
    print(
        f"[selftest] PASS  N={N}  thresholds={COSINE_THRESH_GRID}  "
        f"densities(n_families)={N_FAMILIES_GRID}  overlaps={FAMILY_OVERLAP_GRID}  "
        f"arms={len(ARM_NAMES)} (+pos_ctrl)  seeds={len(SEEDS)}  "
        f"expected_units={EXPECTED_N_UNITS}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    n_main = (
        len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID)
        * len(FAMILY_OVERLAP_GRID) * len(ARM_NAMES)
    )
    n_pc = (
        len(COSINE_THRESH_GRID) * len(N_FAMILIES_GRID)
        if (0.0 in FAMILY_OVERLAP_GRID) else 0
    )
    print(
        f"  [seed={seed}] sweeping 3-axis phase diagram: "
        f"{len(COSINE_THRESH_GRID)} thresh x {len(N_FAMILIES_GRID)} densities x "
        f"{len(FAMILY_OVERLAP_GRID)} overlaps x {len(ARM_NAMES)} arms "
        f"= {n_main} main cells + {n_pc} pos-ctrl cells = {n_main + n_pc}",
        flush=True,
    )
    cells = []
    for nf in N_FAMILIES_GRID:
        for rho in FAMILY_OVERLAP_GRID:
            t_gen = time.time()
            shared = generate_atoms_with_families_and_overlap(seed, nf, rho)
            gen_s = time.time() - t_gen
            print(f"  [seed={seed} nf={nf} rho={rho}] generated W "
                  f"(n_atoms={shared[0].shape[0]}, observed_cos={shared[3]:.3f}) "
                  f"in {gen_s:.1f}s",
                  flush=True)
            for ct in COSINE_THRESH_GRID:
                for arm_name in ARM_NAMES:
                    cell = run_arm(arm_name, seed, ct, nf, rho, shared)
                    cells.append(cell)
                    print(
                        f"  [seed={seed} nf={nf} rho={rho:.1f} ct={ct:.2f} {arm_name}] "
                        f"rec_all={cell['recall_all']:.3f} "
                        f"n_cl={cell['n_qualifying_clusters']} "
                        f"cap_drop={cell['capacity_drop_frac']:.3f} "
                        f"obs_cos={cell['observed_inter_family_cosine']:.3f} "
                        f"wall={cell['wall_s']:.1f}s",
                        flush=True,
                    )
                # POSITIVE CONTROL: only at rho=0.0
                if rho == 0.0:
                    cell = run_arm(POSITIVE_CONTROL_ARM, seed, ct, nf, 0.0, shared)
                    cells.append(cell)
                    print(
                        f"  [seed={seed} nf={nf} rho=0.0 ct={ct:.2f} POS_CTRL] "
                        f"rec_all={cell['recall_all']:.3f} cap_drop={cell['capacity_drop_frac']:.3f}",
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
        "family_overlap_grid": FAMILY_OVERLAP_GRID,
        "arm_names": ARM_NAMES + [POSITIVE_CONTROL_ARM],
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "cells": cells,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _cells_by_key(
    seed_results: List[Dict],
) -> Dict[Tuple[float, int, float, str], List[Dict]]:
    by_key: Dict[Tuple[float, int, float, str], List[Dict]] = {}
    for r in seed_results:
        for c in r.get("cells", []):
            k = (
                round(float(c["cosine_thresh"]), 3),
                int(c["n_families"]),
                round(float(c["family_overlap"]), 3),
                c["arm_name"],
            )
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

    if observed_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL: CARDINALITY_BREACH. observed_units={observed_units} "
                f"< expected_n_units={EXPECTED_N_UNITS}.")

    # Constructor health: any cell where observed_inter_family_cosine deviates
    # by > 0.10 from target rho is SCRIPT_PRECONDITION violation.
    constructor_violations: List[str] = []
    for k, cells_list in by_key.items():
        ct, nf, rho, arm = k
        for c in cells_list:
            obs = c.get("observed_inter_family_cosine", float("nan"))
            if np.isnan(obs):
                continue
            if abs(obs - rho) > 0.10:
                constructor_violations.append(
                    f"(ct={ct},nf={nf},rho={rho},arm={arm}): observed_cos={obs:.3f}"
                )
    if constructor_violations:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCRIPT_PRECONDITION_VIOLATION. Constructor delivered "
                f"wrong inter-family cosine in {len(constructor_violations)} cells; "
                f"first 3: {constructor_violations[:3]}")

    # Positive control health: ARM_FLAT_NO_OVERLAP at rho=0.0 must reproduce
    # ULTRAMETRIC behavior in the clean regime (recall_all >= 0.90 at some cell).
    if 0.0 in FAMILY_OVERLAP_GRID:
        pc_recalls = []
        for ct in COSINE_THRESH_GRID:
            for nf in N_FAMILIES_GRID:
                pc_cells = by_key.get(
                    (round(ct, 3), nf, 0.0, POSITIVE_CONTROL_ARM), []
                )
                if pc_cells:
                    pc_recalls.extend([c["recall_all"] for c in pc_cells])
        if pc_recalls:
            best_pc = max(pc_recalls)
            if best_pc < 0.90:
                return ("HARD_FAIL",
                        f"HARD_FAIL: positive-control arm at rho=0.0 failed to "
                        f"reproduce v1 mechanism class. best_pc_recall={best_pc:.3f} "
                        f"< 0.90. Mechanism class BROKEN.")

    # Per-(ct,nf) cell analysis: compute d_v2_FAMILY_OVERLAP = ULTRA(rho=0.0) - ULTRA(rho=0.9)
    cell_summary: Dict[Tuple[float, int], Dict] = {}
    pass_cells: List[Tuple[float, int, Dict]] = []
    over_compress_cells: List[Tuple[float, int, float]] = []
    all_d_v2: List[float] = []

    for nf in N_FAMILIES_GRID:
        for ct in COSINE_THRESH_GRID:
            # ULTRA at rho=0.0 (clean) and rho=0.9 (worst overlap).
            ult_0 = by_key.get((round(ct, 3), nf, 0.0, "ARM_ULTRAMETRIC"), [])
            ult_9 = by_key.get((round(ct, 3), nf, 0.9, "ARM_ULTRAMETRIC"), [])
            rnd_0 = by_key.get((round(ct, 3), nf, 0.0, "ARM_RANDOM_FLOOR"), [])
            if not ult_0 or not ult_9 or not rnd_0:
                continue
            ult_0_recall = float(np.mean([a["recall_all"] for a in ult_0]))
            ult_9_recall = float(np.mean([a["recall_all"] for a in ult_9]))
            rnd_0_recall = float(np.mean([a["recall_all"] for a in rnd_0]))
            ult_0_recall_per_seed = [a["recall_all"] for a in ult_0]
            cv_ult_0 = (
                float(np.std(ult_0_recall_per_seed)
                      / max(abs(ult_0_recall), 1e-9))
            )
            d_v2 = ult_0_recall - ult_9_recall
            sel = ult_0_recall - rnd_0_recall
            all_d_v2.append(d_v2)
            cell_summary[(ct, nf)] = {
                "ult_0_recall": ult_0_recall,
                "ult_9_recall": ult_9_recall,
                "rnd_0_recall": rnd_0_recall,
                "d_v2_FAMILY_OVERLAP": d_v2,
                "selectivity_at_0": sel,
                "cv_ult_0": cv_ult_0,
            }
            is_pass = (
                ult_0_recall >= 0.95
                and ult_9_recall <= 0.80
                and d_v2 >= 0.15
                and cv_ult_0 <= 0.10
                and sel >= 0.10
            )
            if is_pass:
                pass_cells.append((ct, nf, cell_summary[(ct, nf)]))
            if ult_9_recall <= 0.80:
                over_compress_cells.append((ct, nf, ult_9_recall))

    max_d_v2 = max(all_d_v2) if all_d_v2 else 0.0

    summary_str = (
        f"n_pass_cells={len(pass_cells)} n_over_compress={len(over_compress_cells)} "
        f"max_d_v2_FAMILY_OVERLAP={max_d_v2:.3f} "
        f"observed_units={observed_units}/{EXPECTED_N_UNITS} "
        f"pass_examples={[(ct, nf, round(s['d_v2_FAMILY_OVERLAP'], 3)) for ct, nf, s in pass_cells[:3]]} "
        f"cell_summary_sample={[(k, {kk: round(vv, 3) for kk, vv in v.items()}) for k, v in list(cell_summary.items())[:3]]}"
    )

    if pass_cells:
        return ("HARD_PASS",
                f"PHASE_HARD_PASS_v2: ANCHOR 3 v2 over-compression boundary "
                f"VISIBLE. {summary_str}")

    if max_d_v2 < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: discriminator d_v2_FAMILY_OVERLAP < 0.05 in all "
                f"cells (max={max_d_v2:.3f}). Substrate is robust even to "
                f"near-collinear families; v1+v2 jointly close ANCHOR 3 as "
                f"MEASURED_MECHANISM. {summary_str}")

    return ("MIDDLE_BAND",
            f"PHASE_MIDDLE_BAND_v2: mechanism observable (max_d_v2={max_d_v2:.3f}) "
            f"but no cell clears HARD_PASS bands. {summary_str}")


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
        f"[seed={seed}] coarse_grain phase diagram v2_FAMILY_OVERLAP N={N} "
        f"mode={RUN_MODE} expected_units={EXPECTED_N_UNITS}...",
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
        f"overlaps={FAMILY_OVERLAP_GRID} arms={ARM_NAMES + [POSITIVE_CONTROL_ARM]} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}"
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
    "family_overlap_grid": FAMILY_OVERLAP_GRID,
    "arm_names": ARM_NAMES + [POSITIVE_CONTROL_ARM],
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
