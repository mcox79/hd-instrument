"""cortex_ultrametric_clustering_coarse_grain_v1 -- Cortex compositional-
abstraction primitive (Wave 2 ANCHOR 2 from 4x selective-abstraction drill).

PIVOT: per-atom-scalar importance (cortex E_tensor) triple-failed on
magnitude correlation. This cell tests a STRUCTURALLY DIFFERENT mechanism
class: cluster-level compositional abstraction. Atoms with high mutual
cosine (>=0.85, cluster size >=5) collapse into representative + residual
codes; substrate gains COMPRESSION CAPACITY by storing once per cluster
instead of once per atom.

Brain analog: schema-fast-track (Tse-Morris consolidated clusters); brain
shifts from per-instance to schema-level recall after consolidation.
Math analog: ultrametric distance from spin-glass theory; metastable
basin hierarchy.

Composition: builds on SEMANTIC concept learner chain-grade primitive
(data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json
CHAIN_GRADE). Atoms are generated as a mix of UNCORRELATED random concepts
(which should NOT cluster) and STRUCTURED concept families (atoms drawn
near k semantic centers; SHOULD cluster). This tests whether the mechanism
can DETECT cluster structure when present AND IGNORE noise (no false-positive
clustering of random atoms).

ARMS (3 mandatory minimum):
  ARM_NO_COLLAPSE                -- baseline; no clustering. Sanity rail.
  ARM_ULTRAMETRIC_COLLAPSE       -- proposed mechanism.
  ARM_RANDOM_CLUSTER_COLLAPSE    -- control; random equal-size clusters
                                    collapsed (tests STRUCTURE matters vs
                                    CAPACITY-REDUCTION alone).

INSTRUMENTATION:
  recall_clustered (atoms inside qualifying clusters; queried via centroid).
  recall_unclustered (atoms NOT in any cluster; queried directly).
  recall_all (combined sanity).
  effective_capacity (substrate slots used after collapse).
  capacity_drop_frac (fraction of capacity freed via clustering).
  n_clusters, n_clustered_atoms, n_unclustered_atoms.
  per-arm W_norm_pre / W_norm_post.
  min_within_cluster_cosine, max_between_cluster_cosine (verify ultrametricity).

PRE-REG BANDS (per Research handoff ANCHOR 2 + USER pivot):
  HARD_PASS: capacity_drop_frac >= 0.20 AND recall_clustered >= 0.80 AND
             recall_unclustered >= 0.85 AND cv <= 0.05.
  MIDDLE_BAND: capacity_drop_frac in [0.05, 0.20] AND
               recall_clustered in [0.50, 0.80].
  HARD_FAIL: recall_clustered < 0.50 (collapse destroyed info) OR
             no clusters detected (substrate has no ultrametric structure to
             exploit) OR ARM_ULTRAMETRIC indistinguishable from ARM_RANDOM
             on combined recall (selectivity-vs-random fails).

SUBSTRATE-ONLY DECODE GATE: n_llm_calls = 0 by structural guarantee.

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


ANCHOR_NAME = "cortex_ultrametric_clustering_coarse_grain_v1"
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

# Production constants.
# NOTE on FAMILY_NOISE: in N-dim random Gaussian noise, |noise|*sqrt(N) sets
# the angular deviation from the center. To keep within-cluster cosine clearly
# >= 0.85 (USER spec), we need noise * sqrt(N) << 1. Calibrated empirically:
#   N=512  noise=0.012 -> within-cluster cosine ~ 0.93
#   N=1024 noise=0.008 -> within-cluster cosine ~ 0.93
N_FULL = 1024
N_FAMILIES_FULL = 8        # number of semantic concept families
ATOMS_PER_FAMILY_FULL = 8   # cluster-size source; >= min_cluster_size=5
N_RANDOM_ATOMS_FULL = 200   # uncorrelated atoms (should NOT cluster)
FAMILY_NOISE_FULL = 0.008    # at N=1024 yields within-cluster cosine ~ 0.93
COSINE_THRESH = 0.85         # USER spec
MIN_CLUSTER_SIZE = 5         # USER spec
CLUSTER_DISTANCE = 0.15      # cluster atoms within cosine distance 0.15 (cos 0.85)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 100

if RUN_MODE == "smoke":
    N = 512
    N_FAMILIES = 4
    ATOMS_PER_FAMILY = 6
    N_RANDOM_ATOMS = 80
    FAMILY_NOISE = 0.012  # at N=512 yields within-cluster cosine ~ 0.93
    SEEDS = [7]
    N_QUERIES = 40
else:
    N = N_FULL
    N_FAMILIES = N_FAMILIES_FULL
    ATOMS_PER_FAMILY = ATOMS_PER_FAMILY_FULL
    N_RANDOM_ATOMS = N_RANDOM_ATOMS_FULL
    FAMILY_NOISE = FAMILY_NOISE_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

N_FAMILY_ATOMS = N_FAMILIES * ATOMS_PER_FAMILY
N_TOTAL_ATOMS = N_FAMILY_ATOMS + N_RANDOM_ATOMS
ALPHA = N_TOTAL_ATOMS / N

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},N_FAMILIES={N_FAMILIES},"
    f"ATOMS_PER_FAMILY={ATOMS_PER_FAMILY},N_RANDOM={N_RANDOM_ATOMS},"
    f"FAMILY_NOISE={FAMILY_NOISE},COSINE_THRESH={COSINE_THRESH},"
    f"MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE},CLUSTER_DISTANCE={CLUSTER_DISTANCE},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Substrate: bipolar HRR with cluster-structured + random atoms
# ---------------------------------------------------------------------------
def generate_atoms_with_families(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate W matrix with structured families + random atoms.

    Returns:
      W:              shape (n_atoms, N) -- atom row vectors (real-valued continuous)
      cluster_truth:  shape (n_atoms,) -- ground-truth cluster id; -1 for random
      keys:           shape (n_atoms, N) -- bipolar keys for retrieval

    Each family is centered on a random unit vector; family atoms = center +
    Gaussian noise of scale FAMILY_NOISE. Random atoms are unit-norm Gaussian.
    Keys are SIGN of atom rows (bipolar HRR-compatible retrieval).
    """
    rng = np.random.RandomState(seed)
    # Family centers (random unit vectors in N-dim).
    centers = rng.randn(N_FAMILIES, N)
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    atoms = []
    cluster_truth = []
    for fi in range(N_FAMILIES):
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

    # Keys: bipolar sign of W (so retrieval is well-defined under HRR cosine cleanup).
    keys = np.sign(W)
    keys[keys == 0] = 1.0
    return W, cluster_truth_arr, keys


def recall_via_lookup(
    W_query: np.ndarray,
    W_value_lookup: np.ndarray,
    query_idx: np.ndarray,
    cluster_lookup: np.ndarray | None = None,
) -> float:
    """Retrieve via cosine argmax against value lookup; CLUSTER-LEVEL hit rate.

    For atoms that share a cluster representative in W_value_lookup, multiple
    indices collapse to the same row -- exact-index recall is mechanically
    bounded by 1/cluster_size. The mechanism-appropriate test is CLUSTER-LEVEL:
    did the substrate retrieve a member of the SAME compositional category?

    W_query: atoms used as queries (shape (n, N)).
    W_value_lookup: lookup matrix; each row is the value-position retrieved against.
    query_idx: indices into W_query.
    cluster_lookup: shape (n_atoms,) cluster_id per atom; -1 for unclustered.
                    If None, falls back to exact-index recall.

    Returns hit rate.
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
    if cluster_lookup is None:
        return float(np.mean(argmax == query_idx))
    # CLUSTER-LEVEL recall: hit if argmax atom shares cluster with query atom,
    # OR (for unclustered atoms) argmax exactly equals query_idx.
    hits = 0
    for q_i, a_i in zip(query_idx, argmax):
        q_cluster = cluster_lookup[q_i]
        a_cluster = cluster_lookup[a_i]
        if q_cluster >= 0:
            # Clustered atom: hit if retrieved atom is in same cluster.
            if q_cluster == a_cluster:
                hits += 1
        else:
            # Unclustered atom: require exact-index match.
            if a_i == q_i:
                hits += 1
    return float(hits) / float(len(query_idx))


def random_clusters_matching_size(
    n_atoms: int,
    qualifying_clusters: List[List[int]],
    seed: int,
) -> List[List[int]]:
    """Build random equal-size clusters matching qualifying_clusters' sizes.

    This is the SELECTIVITY control: collapses the same NUMBER of atoms but
    grouped randomly (not by cosine similarity). If ARM_RANDOM beats or matches
    ARM_ULTRAMETRIC, selectivity does NOT matter -- any compression helps
    equally; selectivity fails.
    """
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
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int, shared: Tuple) -> Dict:
    t0 = time.time()
    W, cluster_truth, _keys = shared
    n_atoms = W.shape[0]
    cfg = UltrametricConfig(
        cosine_thresh=COSINE_THRESH,
        min_cluster_size=MIN_CLUSTER_SIZE,
        representative_mode="centroid",
    )

    # ALWAYS compute qualifying clusters first (needed for ARM_ULTRAMETRIC and
    # to size ARM_RANDOM).
    D = cosine_distance_matrix(W)
    raw_clusters = single_linkage_clusters(D, max_distance=CLUSTER_DISTANCE)
    qualifying = filter_qualifying_clusters(raw_clusters, W, cfg)
    n_qualifying = len(qualifying)
    n_clustered_atoms = sum(len(c) for c in qualifying)

    # Stats about the clusters themselves (verify ultrametricity).
    if qualifying:
        within_cosines = []
        for cl in qualifying:
            sub = W[cl]
            subn = sub / np.linalg.norm(sub, axis=1, keepdims=True).clip(min=1e-12)
            cm = subn @ subn.T
            np.fill_diagonal(cm, np.inf)
            within_cosines.append(float(np.min(cm)))
        min_within = float(np.min(within_cosines))
        # Between-cluster: distance between rep_i and rep_j.
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
    elif arm_name == "ARM_ULTRAMETRIC_COLLAPSE":
        if not qualifying:
            # No clusters; cannot operate -- fall back to no-op.
            W_after = W.copy()
            cluster_lookup = np.full(n_atoms, -1, dtype=np.int64)
            eff_cap = n_atoms
        else:
            W_after, _reps, cluster_lookup = collapse_W_via_clusters(W, qualifying, cfg)
            eff_cap = effective_capacity_used(cluster_lookup)
    elif arm_name == "ARM_RANDOM_CLUSTER_COLLAPSE":
        if not qualifying:
            # No qualifying clusters to size random against -> fall back to fixed
            # random cluster set: 5 clusters of size MIN_CLUSTER_SIZE.
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

    # Recall queries.
    # CLUSTERED-recall: atoms inside any cluster (their original index should
    # still retrieve correctly via centroid since collapse mapped them all to
    # same row).
    rng_eval = np.random.RandomState(seed + 503)
    in_cluster_atoms = np.where(cluster_truth >= 0)[0]
    unclustered_atoms = np.where(cluster_truth == -1)[0]

    n_q_in = min(N_QUERIES, len(in_cluster_atoms))
    n_q_un = min(N_QUERIES, len(unclustered_atoms))
    in_query = rng_eval.choice(in_cluster_atoms, size=n_q_in, replace=False)
    un_query = rng_eval.choice(unclustered_atoms, size=n_q_un, replace=False)
    all_query = np.concatenate([in_query, un_query])

    # The recall test: can the substrate retrieve atom i by querying with the
    # ORIGINAL W[i] vector? After collapse, atoms inside a cluster share the
    # representative row in W_after, so they may collide -- that's the cost
    # of compression. Recall is per the lookup matrix.
    recall_in_cluster = recall_via_lookup(W, W_after, in_query, cluster_lookup)
    recall_unclustered = recall_via_lookup(W, W_after, un_query, cluster_lookup)
    recall_all = recall_via_lookup(W, W_after, all_query, cluster_lookup)

    W_norm_pre = float(np.linalg.norm(W))
    W_norm_post = float(np.linalg.norm(W_after))

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
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
def _selftest_atom_generation_creates_known_families() -> bool:
    """Atoms generated with N_FAMILIES families should have N_FAMILIES * ATOMS_PER_FAMILY
    family atoms + N_RANDOM_ATOMS isolated atoms = N_TOTAL_ATOMS total."""
    W, truth, keys = generate_atoms_with_families(seed=7)
    assert W.shape == (N_TOTAL_ATOMS, N), f"W shape {W.shape}"
    assert truth.shape == (N_TOTAL_ATOMS,)
    n_in_families = int(np.sum(truth >= 0))
    n_random = int(np.sum(truth == -1))
    assert n_in_families == N_FAMILIES * ATOMS_PER_FAMILY
    assert n_random == N_RANDOM_ATOMS
    return True


def _selftest_clustering_detects_planted_structure() -> bool:
    """Run clustering on generated atoms; expect N_FAMILIES qualifying clusters."""
    W, truth, _keys = generate_atoms_with_families(seed=7)
    cfg = UltrametricConfig(
        cosine_thresh=COSINE_THRESH,
        min_cluster_size=MIN_CLUSTER_SIZE,
    )
    D = cosine_distance_matrix(W)
    raw = single_linkage_clusters(D, max_distance=CLUSTER_DISTANCE)
    qualifying = filter_qualifying_clusters(raw, W, cfg)
    # Should recover N_FAMILIES clusters (random atoms should NOT cluster).
    assert len(qualifying) == N_FAMILIES, (
        f"expected {N_FAMILIES} qualifying clusters; got {len(qualifying)} "
        f"(raw sizes={[len(c) for c in raw if len(c) >= MIN_CLUSTER_SIZE]})"
    )
    # Each qualifying cluster should contain only same-family atoms.
    for ci, cl in enumerate(qualifying):
        family_ids = truth[cl]
        unique_families = np.unique(family_ids[family_ids >= 0])
        assert len(unique_families) == 1, (
            f"cluster {ci} mixes families {unique_families}; atoms={cl}, truth={family_ids}"
        )
    return True


def _selftest_collapse_preserves_centroid_retrieval() -> bool:
    """After collapse, querying with a clustered atom's original vector should
    retrieve its position (which now points to the centroid row)."""
    W, truth, _keys = generate_atoms_with_families(seed=7)
    cfg = UltrametricConfig(
        cosine_thresh=COSINE_THRESH,
        min_cluster_size=MIN_CLUSTER_SIZE,
    )
    D = cosine_distance_matrix(W)
    raw = single_linkage_clusters(D, max_distance=CLUSTER_DISTANCE)
    qualifying = filter_qualifying_clusters(raw, W, cfg)
    if not qualifying:
        # Smoke regime might be too small; treat as N/A.
        return True
    W_col, reps, lookup = collapse_W_via_clusters(W, qualifying, cfg)
    # First atom of first cluster: query with its W[a], should argmax to itself
    # via lookup (since all cluster atoms share W_col[a]=rep, argmax may be any
    # cluster member; the centroid query test is symmetric).
    a = qualifying[0][0]
    q = W[a] / np.linalg.norm(W[a])
    vn = W_col / np.linalg.norm(W_col, axis=1, keepdims=True).clip(min=1e-12)
    sims = vn @ q
    argmax = int(np.argmax(sims))
    # argmax must be SOME atom in the same cluster as a.
    same_cluster = lookup[argmax] == lookup[a] and lookup[a] >= 0
    assert same_cluster, (
        f"after collapse, query for atom {a} (cluster {lookup[a]}) returned "
        f"atom {argmax} (cluster {lookup[argmax]})"
    )
    return True


def _instrumentation_selftest():
    _selftest_atom_generation_creates_known_families()
    _selftest_clustering_detects_planted_structure()
    _selftest_collapse_preserves_centroid_retrieval()
    print(
        f"[selftest] PASS  N={N}  N_FAMILIES={N_FAMILIES}  "
        f"ATOMS_PER_FAM={ATOMS_PER_FAMILY}  N_RANDOM={N_RANDOM_ATOMS}  "
        f"N_TOTAL={N_TOTAL_ATOMS}  noise={FAMILY_NOISE}  mode={RUN_MODE}",
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
    print(
        f"  [seed={seed}] generating substrate (N_TOTAL={N_TOTAL_ATOMS}, "
        f"N_FAMILIES={N_FAMILIES}, noise={FAMILY_NOISE})...",
        flush=True,
    )
    t_setup = time.time()
    shared = generate_atoms_with_families(seed)
    print(f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s", flush=True)

    arms = []
    for arm_name in [
        "ARM_NO_COLLAPSE",
        "ARM_ULTRAMETRIC_COLLAPSE",
        "ARM_RANDOM_CLUSTER_COLLAPSE",
    ]:
        out = run_arm(arm_name, seed, shared=shared)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"rec_cl={out['recall_clustered']:.3f} "
            f"rec_un={out['recall_unclustered']:.3f} "
            f"rec_all={out['recall_all']:.3f} "
            f"n_cl={out['n_qualifying_clusters']} "
            f"n_clust_atoms={out['n_clustered_atoms']} "
            f"cap_drop={out['capacity_drop_frac']:.3f} "
            f"min_within={out['min_within_cluster_cosine']:.3f} "
            f"max_between={out['max_between_cluster_cosine']:.3f} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "N_FAMILIES": N_FAMILIES,
        "ATOMS_PER_FAMILY": ATOMS_PER_FAMILY,
        "N_RANDOM_ATOMS": N_RANDOM_ATOMS,
        "N_TOTAL_ATOMS": N_TOTAL_ATOMS,
        "alpha": float(ALPHA),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES),
        "cosine_thresh": COSINE_THRESH,
        "min_cluster_size": MIN_CLUSTER_SIZE,
        "cluster_distance": CLUSTER_DISTANCE,
        "family_noise": FAMILY_NOISE,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (per-reg bands per Research handoff)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    arm_names = ["ARM_NO_COLLAPSE", "ARM_ULTRAMETRIC_COLLAPSE",
                 "ARM_RANDOM_CLUSTER_COLLAPSE"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_cl = [a["recall_clustered"] for a in per]
        rec_un = [a["recall_unclustered"] for a in per]
        rec_all = [a["recall_all"] for a in per]
        cap_drop = [a["capacity_drop_frac"] for a in per]
        n_cl = [a["n_qualifying_clusters"] for a in per]
        agg[name] = {
            "mean_rec_cl": float(np.mean(rec_cl)),
            "std_rec_cl": float(np.std(rec_cl)),
            "cv_rec_cl": float(np.std(rec_cl) / max(abs(np.mean(rec_cl)), 1e-9)),
            "mean_rec_un": float(np.mean(rec_un)),
            "mean_rec_all": float(np.mean(rec_all)),
            "mean_cap_drop": float(np.mean(cap_drop)),
            "mean_n_clusters": float(np.mean(n_cl)),
        }

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    u = agg["ARM_ULTRAMETRIC_COLLAPSE"]
    rnd = agg["ARM_RANDOM_CLUSTER_COLLAPSE"]
    base = agg["ARM_NO_COLLAPSE"]

    delta_rec_all = u["mean_rec_all"] - rnd["mean_rec_all"]

    summary = (
        f"ULTRA(rec_cl={u['mean_rec_cl']:.3f},rec_un={u['mean_rec_un']:.3f},"
        f"rec_all={u['mean_rec_all']:.3f},cap_drop={u['mean_cap_drop']:.3f},"
        f"n_cl={u['mean_n_clusters']:.1f},cv={u['cv_rec_cl']:.3f}); "
        f"RANDOM(rec_all={rnd['mean_rec_all']:.3f},cap_drop={rnd['mean_cap_drop']:.3f}); "
        f"NO_COLLAPSE(rec_cl={base['mean_rec_cl']:.3f},"
        f"rec_un={base['mean_rec_un']:.3f}); "
        f"d_ULTRA_vs_RND={delta_rec_all:+.3f}"
    )

    # ---- HARD_FAIL gates ----
    # No clusters detected: substrate has no ultrametric structure (or method
    # is too strict on the planted regime).
    if u["mean_n_clusters"] < 1.0:
        return ("HARD_FAIL",
                f"HARD_FAIL: no qualifying clusters detected. "
                f"mean_n_clusters={u['mean_n_clusters']:.1f}. "
                f"Substrate has no ultrametric structure to exploit at "
                f"COSINE_THRESH={COSINE_THRESH} / MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE} "
                f"in this regime. {summary}")

    # Collapse destroyed information.
    if u["mean_rec_cl"] < 0.50:
        return ("HARD_FAIL",
                f"HARD_FAIL: recall_clustered={u['mean_rec_cl']:.3f} < 0.50. "
                f"Collapse destroyed cluster-member information; centroid "
                f"representation insufficient. {summary}")

    # Selectivity-vs-random fail.
    if abs(delta_rec_all) < 0.02 and u["mean_cap_drop"] > 0.10:
        # Same recall AND substantial collapse: structure didn't matter, only
        # capacity-reduction did -> selectivity fails.
        return ("HARD_FAIL",
                f"HARD_FAIL: ARM_ULTRAMETRIC indistinguishable from "
                f"ARM_RANDOM on recall_all (delta={delta_rec_all:+.3f}); "
                f"structure-based collapse no better than random. "
                f"Selectivity fails. {summary}")

    # ---- HARD_PASS ----
    hp_cap = u["mean_cap_drop"] >= 0.20
    hp_rec_cl = u["mean_rec_cl"] >= 0.80
    hp_rec_un = u["mean_rec_un"] >= 0.85
    hp_cv = u["cv_rec_cl"] <= 0.05

    if all([hp_cap, hp_rec_cl, hp_rec_un, hp_cv]):
        return ("HARD_PASS",
                f"HARD_PASS: ultrametric clustering yields >=20% capacity drop, "
                f">=0.80 recall_clustered, >=0.85 recall_unclustered, cv<=0.05. "
                f"Compositional-abstraction primitive operational. {summary}")

    # MIDDLE_BAND
    if u["mean_cap_drop"] >= 0.05 and u["mean_rec_cl"] >= 0.50:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: clustering detects structure (cap_drop>=0.05, "
                f"rec_cl>=0.50) but full PASS band not cleared. "
                f"hp_checks=[cap={hp_cap},rec_cl={hp_rec_cl},rec_un={hp_rec_un},"
                f"cv={hp_cv}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: ultrametric does not clear PASS or MIDDLE. "
            f"hp_checks=[cap={hp_cap},rec_cl={hp_rec_cl},rec_un={hp_rec_un},"
            f"cv={hp_cv}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] ultrametric_clustering v1 N={N} N_FAMILIES={N_FAMILIES} "
        f"N_TOTAL={N_TOTAL_ATOMS} alpha={ALPHA:.3f} mode={RUN_MODE}...",
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
        f"n_seeds={len(all_results)} N={N} N_FAMILIES={N_FAMILIES} "
        f"ATOMS_PER_FAM={ATOMS_PER_FAMILY} N_RANDOM={N_RANDOM_ATOMS} "
        f"N_TOTAL={N_TOTAL_ATOMS} alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"cos_thresh={COSINE_THRESH} min_cl_size={MIN_CLUSTER_SIZE} "
        f"family_noise={FAMILY_NOISE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "N_FAMILIES": N_FAMILIES,
    "ATOMS_PER_FAMILY": ATOMS_PER_FAMILY,
    "N_RANDOM_ATOMS": N_RANDOM_ATOMS,
    "N_TOTAL_ATOMS": N_TOTAL_ATOMS,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "cosine_thresh": float(COSINE_THRESH),
    "min_cluster_size": int(MIN_CLUSTER_SIZE),
    "cluster_distance": float(CLUSTER_DISTANCE),
    "family_noise": float(FAMILY_NOISE),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
