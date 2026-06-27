"""edge_importance_bound_pair_consolidation_v1 -- Cortex E_tensor alternative.

Wave 2 ANCHOR 5 from `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md`.

PIVOT: per-ATOM scalar importance was triple-falsified (cor(E,|W|)=0.984 on
Wave 1.6 RETEST v2). This cell moves importance to per-EDGE space H[i,j] on
bound-pair graph; derived per-atom E = row-sum or PageRank lives on a DIFFERENT
observability axis than |W|. Load-bearing test: cor(E_derived, |W|) < 0.30.

KEY METHODOLOGICAL ADDITION: composite-query workload. Prior cortex cells used
single-atom queries only; the H graph requires MULTI-ATOM bound queries to
populate. This cell generates synthetic composite queries (3-atom bundles) and
runs them as the retrieval workload during J cycles.

ARMS (3 mandatory minimum):
  ARM_BASELINE_NO_DOWNSCALE   -- rail; no pruning at all.
  ARM_EDGE_GATED_DOWNSCALE    -- prune atoms with E_derived<e_thresh AND
                                  max_edge<h_thresh.
  ARM_RANDOM_GATED            -- control; random pruning of same count
                                  (tests SELECTIVITY vs CAPACITY-REDUCTION).

INSTRUMENTATION (per arm):
  recall_old_RETRIEVED, recall_old_UNRETRIEVED, recall_recent (Fix A
    partition: RETRIEVED = atoms appearing in >=1 composite query during J).
  cor_E_derived_magnitude, n_downscaled, downscale_frac_actual,
  H_n_edges, H_total_mass, E_derived_min/max/mean,
  per-arm W_norm_pre/post.

LOAD-BEARING FAIRNESS CHECK:
  cor(E_derived_rowsum, |W @ key|) < 0.30 -- USER pre-reg gate.
  If cor >= 0.30, EDGE-derived importance has ALSO inherited the magnitude
  correlation; mechanism class structurally indistinguishable from per-atom-
  scalar and DIFFERENT structural pivot is required. STOP at smoke; route
  back to research.

SUBSTRATE-ONLY DECODE GATE:
  n_llm_calls = 0 by structural-guarantee. Decode is sign(W @ key) cosine
  cleanup against value matrix.

PROT-018: N=1024 (no _n suffix in anchor; capability-test cell).
PROT-019: no _n>=4096 suffix -> no PROT-019 floor.

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
from hdlab.edge_importance import EdgeImportance, HConfig, correlation_E_vs_magnitude


ANCHOR_NAME = "edge_importance_bound_pair_consolidation_v1"
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

# Production constants (mirror cortex_E_tensor_HARDER_REGIME / RETEST scale).
N_FULL = 1024
M_OLD_FULL = 600
M_RECENT_FULL = 400
N_COMPOSITE_QUERIES_FULL = 3000   # J cycles of composite-query workload
COMPOSITE_ARITY = 3                # atoms-per-composite-query
USE_FRAC_FULL = 0.40               # 40% of M_OLD seeded into composite-query
                                    # workload (RETRIEVED partition)
DOWNSCALE_SCALE = 0.20
E_THRESH = 2.0                     # atoms with E_derived < 2.0 candidate for prune
H_THRESH = 3.0                     # atoms with any edge >= 3.0 PROTECTED
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

if RUN_MODE == "smoke":
    N = 256
    M_OLD = 200
    M_RECENT = 150
    N_COMPOSITE_QUERIES = 1000
    USE_FRAC = 0.40
    SEEDS = [7]
    N_QUERIES = 50
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"J_composite={N_COMPOSITE_QUERIES},arity={COMPOSITE_ARITY},"
    f"USE_FRAC={USE_FRAC},DOWNSCALE_SCALE={DOWNSCALE_SCALE},"
    f"E_THRESH={E_THRESH},H_THRESH={H_THRESH},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation: bipolar keys/values
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


def build_W_from_pairs(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray,
                  query_idx: np.ndarray, all_values: np.ndarray) -> float:
    N_dim = keys.shape[1]
    if len(query_idx) == 0:
        return float("nan")
    n_hits = 0
    for i in query_idx:
        pred = predict(W, keys[i])
        sims = all_values @ pred / float(N_dim)
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(query_idx))


# ---------------------------------------------------------------------------
# Composite-query workload: substrate runs HRR-style bundles of atoms
# ---------------------------------------------------------------------------
def composite_query_bundle(keys: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """Bundle the given atoms' KEYS via bipolar sum + sign (substrate-native
    bundling, matches hdlab/bundling.py majority-vote bundle).

    Returns shape (N,) bipolar vector.
    """
    bundle = np.sum(keys[indices], axis=0)
    out = np.sign(bundle)
    out[out == 0] = 1.0
    return out


def setup_substrate_and_populate_H(
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, EdgeImportance,
           np.ndarray, np.ndarray]:
    """Build keys/values, ingest old, run J composite queries (populating H),
    then ingest recent.

    Returns:
      W, all_keys, all_values, edge_graph, retrieved_idx, unretrieved_idx.
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=E_THRESH, h_thresh=H_THRESH,
    )
    edge_graph = EdgeImportance(n_atoms=M_TOTAL, cfg=cfg)

    # Ingest OLD via Hebbian.
    W = build_W_from_pairs(keys_old, values_old)

    # Fix A: deterministic partition of OLD into RETRIEVED vs UNRETRIEVED.
    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    # J cycles of composite queries: draw uniform triples from RETRIEVED pool,
    # bundle keys, decode against W, increment H on success-pair atoms.
    rng_q = np.random.RandomState(seed + 1117)
    for _q in range(N_COMPOSITE_QUERIES):
        # Sample COMPOSITE_ARITY atoms from RETRIEVED.
        triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY, replace=False)
        # Bundle their keys -> composite query.
        bundled_key = composite_query_bundle(all_keys, triple)
        # Decode -> get composite read. We just need that the substrate is
        # ACTIVELY operating on these atoms; the H-increment is per the
        # BIND structure of the composite (which atoms participated).
        _read = predict(W, bundled_key)
        # Increment H for ALL unordered pairs in the composite.
        edge_graph.increment_query(triple)
        # Apply decay (no-op in default cfg, decay_step=0).
        edge_graph.decay_all()

    # Ingest RECENT into W (post composite workload).
    W = W + build_W_from_pairs(keys_rec, values_rec)

    return W, all_keys, all_values, edge_graph, retrieved_idx, unretrieved_idx


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: Tuple) -> Dict:
    t0 = time.time()
    W_base, all_keys, all_values, edge_graph, retrieved_idx, unretrieved_idx = shared
    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    E_derived = edge_graph.derive_E_rowsum()
    # Substrate-readback magnitude per atom (post-write, PRE-prune).
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_E_W = correlation_E_vs_magnitude(E_derived, atom_norms)

    n_downscaled = 0
    if arm_name == "ARM_BASELINE_NO_DOWNSCALE":
        n_downscaled = 0
    elif arm_name == "ARM_EDGE_GATED_DOWNSCALE":
        # Prune atoms with low E_derived AND no load-bearing edge.
        mask = edge_graph.downscale_mask(E_derived)
        prune_idx = np.where(mask)[0]
        n_downscaled = int(len(prune_idx))
        for idx in prune_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_RANDOM_GATED":
        # Match count to what EDGE_GATED would prune.
        mask = edge_graph.downscale_mask(E_derived)
        n_target = int(np.sum(mask))
        if n_target <= 0:
            # Fallback: random 30% if EDGE mechanism finds nothing.
            n_target = max(1, int(round(0.30 * M_TOTAL)))
        rng = np.random.RandomState(seed + 7777)
        rand_idx = rng.choice(M_TOTAL, size=n_target, replace=False)
        n_downscaled = n_target
        for idx in rand_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    W_norm_post = float(np.linalg.norm(W))

    # Recall measurement: RETRIEVED-old vs UNRETRIEVED-old + RECENT.
    rng_eval = np.random.RandomState(seed + 503)
    n_q_ret = min(N_QUERIES, len(retrieved_idx))
    n_q_unret = min(N_QUERIES, len(unretrieved_idx))
    n_q_rec = min(N_QUERIES, M_RECENT)
    ret_query = rng_eval.choice(retrieved_idx, size=n_q_ret, replace=False)
    unret_query = rng_eval.choice(unretrieved_idx, size=n_q_unret, replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_q_rec, replace=False) + M_OLD

    recall_old_retrieved = recall_subset(W, all_keys, ret_query, all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query, all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "recall_old_RETRIEVED": float(recall_old_retrieved),
        "recall_old_UNRETRIEVED": float(recall_old_unretrieved),
        "recall_recent": float(recall_recent),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "cor_E_derived_magnitude": float(cor_E_W),
        "n_downscaled": int(n_downscaled),
        "downscale_frac_actual": float(n_downscaled) / float(M_TOTAL),
        "wall_s": float(elapsed),
        "E_derived_min": float(np.min(E_derived)),
        "E_derived_max": float(np.max(E_derived)),
        "E_derived_mean": float(np.mean(E_derived)),
        "H_n_edges": int(edge_graph.n_edges()),
        "H_total_mass": float(edge_graph.total_mass()),
        "n_retrieved": int(len(retrieved_idx)),
        "n_unretrieved": int(len(unretrieved_idx)),
    }


# ---------------------------------------------------------------------------
# Self-tests (mechanism unit-tests; mandatory per Fix #28 + formula-selftests)
# ---------------------------------------------------------------------------
def _selftest_composite_query_increments_H() -> bool:
    """A single composite query of 3 atoms must produce 3 edges in H."""
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=10, cfg=cfg)
    triple = np.array([0, 3, 7])
    eg.increment_query(triple)
    assert eg.n_edges() == 3, f"3 edges expected; got {eg.n_edges()}"
    assert eg.total_mass() == 3.0
    return True


def _selftest_derived_E_separates_active_from_idle() -> bool:
    """After J composite queries on a subset, E_derived for active atoms >>
    E_derived for idle atoms."""
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=20, cfg=cfg)
    active_pool = np.arange(0, 10)
    rng = np.random.RandomState(0)
    for _ in range(100):
        triple = rng.choice(active_pool, size=3, replace=False)
        eg.increment_query(triple)
    E = eg.derive_E_rowsum()
    # Active atoms (0-9) should have high E; idle (10-19) should be 0.
    assert np.mean(E[:10]) > 10.0, f"active E mean {np.mean(E[:10])} should be >> 10"
    assert np.all(E[10:] == 0.0), f"idle E should be 0; got {E[10:]}"
    return True


def _selftest_composite_bundle_decoding() -> bool:
    """Bundled key produces a deterministic bipolar output of correct shape."""
    keys = np.random.RandomState(0).choice([-1.0, 1.0], size=(10, 32)).astype(np.float64)
    out = composite_query_bundle(keys, np.array([0, 3, 7]))
    assert out.shape == (32,)
    assert set(np.unique(out)).issubset({-1.0, 1.0})
    return True


def _selftest_fairness_orthogonality_synthetic() -> bool:
    """STRUCTURAL test: derived E (from edge graph) should be uncorrelated
    with random independent atom_norms."""
    rng = np.random.RandomState(0)
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=50, cfg=cfg)
    # Edge structure: clique on first 10 atoms only.
    for i in range(10):
        for j in range(i + 1, 10):
            eg.increment_pair(i, j)
    E = eg.derive_E_rowsum()
    atom_norms = rng.rand(50)  # INDEPENDENT random magnitudes
    cor = correlation_E_vs_magnitude(E, atom_norms)
    assert abs(cor) < 0.30, f"orthogonality: |cor|={abs(cor):.3f} should be < 0.30"
    return True


def _instrumentation_selftest():
    _selftest_composite_query_increments_H()
    _selftest_derived_E_separates_active_from_idle()
    _selftest_composite_bundle_decoding()
    _selftest_fairness_orthogonality_synthetic()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J_comp={N_COMPOSITE_QUERIES}  "
        f"arity={COMPOSITE_ARITY}  N_USE={N_USE}  mode={RUN_MODE}",
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
        f"  [seed={seed}] setup_substrate + populate H (J_comp={N_COMPOSITE_QUERIES}, "
        f"arity={COMPOSITE_ARITY}, N_USE={N_USE} of M_OLD={M_OLD})...",
        flush=True,
    )
    t_setup = time.time()
    shared = setup_substrate_and_populate_H(seed)
    print(
        f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
        f"H_edges={shared[3].n_edges()}  H_mass={shared[3].total_mass():.0f}",
        flush=True,
    )
    arms = []
    for arm_name in [
        "ARM_BASELINE_NO_DOWNSCALE",
        "ARM_EDGE_GATED_DOWNSCALE",
        "ARM_RANDOM_GATED",
    ]:
        out = run_arm(arm_name, seed, shared=shared)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
            f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
            f"rec_rec={out['recall_recent']:.3f} "
            f"cor_E_W={out['cor_E_derived_magnitude']:.3f} "
            f"n_down={out['n_downscaled']} ({out['downscale_frac_actual']:.2f}) "
            f"H_edges={out['H_n_edges']} "
            f"E_mean={out['E_derived_mean']:.2f} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "M_OLD": M_OLD,
        "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES),
        "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "e_thresh": E_THRESH,
        "h_thresh": H_THRESH,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "composite_arity": COMPOSITE_ARITY,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (pre-reg bands; LOAD-BEARING)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    arm_names = ["ARM_BASELINE_NO_DOWNSCALE", "ARM_EDGE_GATED_DOWNSCALE",
                 "ARM_RANDOM_GATED"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_retr = [a["recall_old_RETRIEVED"] for a in per]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_E_derived_magnitude"] for a in per]
        wnorm = [a["W_norm_post"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        agg[name] = {
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "std_rec_RETRIEVED": float(np.std(rec_retr)),
            "cv_rec_RETRIEVED": float(np.std(rec_retr) / max(abs(np.mean(rec_retr)), 1e-9)),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_E_W": float(np.mean(cor)),
            "mean_W_norm": float(np.mean(wnorm)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    e = agg["ARM_EDGE_GATED_DOWNSCALE"]
    rnd = agg["ARM_RANDOM_GATED"]
    base = agg["ARM_BASELINE_NO_DOWNSCALE"]

    delta_retrieved = e["mean_rec_RETRIEVED"] - rnd["mean_rec_RETRIEVED"]
    e_vs_base_retr = e["mean_rec_RETRIEVED"] - base["mean_rec_RETRIEVED"]

    summary = (
        f"EDGE(retr={e['mean_rec_RETRIEVED']:.3f},"
        f"unretr={e['mean_rec_UNRETRIEVED']:.3f},"
        f"rec={e['mean_rec_recent']:.3f},"
        f"cor={e['mean_cor_E_W']:.3f},"
        f"cv={e['cv_rec_RETRIEVED']:.3f},"
        f"n_down={e['mean_n_downscaled']:.0f}); "
        f"RANDOM(retr={rnd['mean_rec_RETRIEVED']:.3f}); "
        f"NO_DOWNSCALE(retr={base['mean_rec_RETRIEVED']:.3f}); "
        f"d_E_vs_RND={delta_retrieved:+.3f} "
        f"d_E_vs_BASE={e_vs_base_retr:+.3f}"
    )

    if not np.isfinite(e["mean_W_norm"]):
        return ("HARD_FAIL", f"HARD_FAIL: EDGE W_norm non-finite. {summary}")

    # ---- HARD_FAIL fairness gate (USER pre-reg; load-bearing) ----
    # If edge-derived E ALSO inherits magnitude correlation, mechanism class
    # is structurally same as per-atom-scalar -- pivot needed.
    if e["mean_cor_E_W"] >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: USER fairness gate fired. "
                f"cor(E_derived,|W|)={e['mean_cor_E_W']:.3f} >= 0.30. "
                f"Edge-derived importance has inherited magnitude correlation. "
                f"Mechanism structurally indistinguishable from per-atom-scalar "
                f"failure mode (Wave 1.6 cor=0.984). Route back to research for "
                f"structural alternative. {summary}")

    # H-graph must actually populate (mechanism must fire, not no-op).
    h_edges_seen = int(np.mean([
        _arm_by_name(r["arms"], "ARM_EDGE_GATED_DOWNSCALE")["H_n_edges"]
        for r in results
    ]))
    if h_edges_seen < 50:
        return ("HARD_FAIL",
                f"HARD_FAIL: H graph too sparse. n_edges={h_edges_seen} < 50. "
                f"Composite-query workload did not populate H meaningfully -- "
                f"mechanism is structurally inapplicable to substrate's "
                f"workload. {summary}")

    # ---- HARD_PASS bands ----
    # USER fairness PASS: cor < 0.30.
    hp_cor = e["mean_cor_E_W"] < 0.30
    # Preserve old at >=0.85 (Research handoff: "recall_old preservation >0.85
    # on RETRIEVED-old subset"). Use 0.85 as the user-specified floor.
    hp_recall_old = e["mean_rec_RETRIEVED"] >= 0.85
    # Recent ingest >=0.85 (USER handoff spec).
    hp_recall_recent = e["mean_rec_recent"] >= 0.85
    # Selectivity vs random: EDGE must beat RANDOM by >= 0.05 on RETRIEVED.
    hp_beats_rnd = delta_retrieved >= 0.05
    hp_cv = e["cv_rec_RETRIEVED"] <= 0.10

    if all([hp_cor, hp_recall_old, hp_recall_recent, hp_beats_rnd, hp_cv]):
        return ("HARD_PASS",
                f"HARD_PASS: edge-importance mechanism structurally orthogonal "
                f"(cor<0.30), preserves RETRIEVED old (>=0.85), preserves "
                f"recent (>=0.85), beats RANDOM by {delta_retrieved:+.3f}, "
                f"cv<=0.10. Cortex content-extraction unblocked via per-EDGE "
                f"importance. {summary}")

    # MIDDLE_BAND: USER fairness PASS (cor<0.50) AND some recall preservation
    # but full PASS not cleared.
    if e["mean_cor_E_W"] < 0.50 and e["mean_rec_RETRIEVED"] >= 0.65:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: edge-importance is structurally distinct from "
                f"per-atom-scalar (cor={e['mean_cor_E_W']:.3f}<0.50) but full "
                f"PASS band not cleared. hp_checks=[cor={hp_cor},"
                f"rec_old={hp_recall_old},rec_recent={hp_recall_recent},"
                f"beats_rnd={hp_beats_rnd},cv={hp_cv}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: edge-importance does not clear PASS or MIDDLE. "
            f"hp_checks=[cor={hp_cor},rec_old={hp_recall_old},"
            f"rec_recent={hp_recall_recent},beats_rnd={hp_beats_rnd},"
            f"cv={hp_cv}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
              "J": N_COMPOSITE_QUERIES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] edge_importance v1 N={N} alpha={ALPHA:.3f} "
        f"J_comp={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} "
        f"N_USE={N_USE} mode={RUN_MODE}...",
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
        f"n_seeds={len(all_results)} N={N} M_OLD={M_OLD} M_RECENT={M_RECENT} "
        f"alpha={ALPHA:.3f} J_comp={N_COMPOSITE_QUERIES} "
        f"arity={COMPOSITE_ARITY} N_USE={N_USE} mode={RUN_MODE} "
        f"e_thresh={E_THRESH} h_thresh={H_THRESH}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "M_OLD": M_OLD,
    "M_RECENT": M_RECENT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "n_use": int(N_USE),
    "n_composite_queries": N_COMPOSITE_QUERIES,
    "composite_arity": COMPOSITE_ARITY,
    "downscale_scale": float(DOWNSCALE_SCALE),
    "e_thresh": float(E_THRESH),
    "h_thresh": float(H_THRESH),
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
