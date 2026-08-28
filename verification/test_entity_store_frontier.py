"""Scaffold-free witness for the FRONTIER pushes on `the_entity_store_is_a_dense_bundle_that_fans`
(beyond the SOLVED bar): the schema/gist systems-level fix (Radvansky 2017) and the graded
multi-timescale temporal context (Q1/Q2), which show WHERE the SOLVED fix is still the cheap version.

  .venv/Scripts/python.exe verification/test_entity_store_frontier.py
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from experiments.exp_entity_store_graded_temporal_v1 import (  # noqa: E402
    test_contiguity, test_completion,
)
from experiments.exp_entity_store_schema_gist_v1 import _make_entity, _run_arm  # noqa: E402
from experiments.exp_entity_store_unified_v1 import (  # noqa: E402
    test_race_stop, test_contiguity as unified_contiguity, test_graceful, test_semantic_intrusions,
    test_event_boundary_effect, test_relational_transfer, test_sr_predicts,
)

PASS = []


def ok(name, cond, detail=""):
    if not cond:
        raise AssertionError(f"FAIL: {name} :: {detail}")
    PASS.append(name)
    print(f"  PASS {name} {detail}")


def test_graded_context_has_temporal_contiguity():
    """The brain's temporal key is a GRADED drift (Howard&Kahana 2002; time cells): nearby times must be
    graded-similar (temporal contiguity, Kahana 1996). The cheap orthogonal sub-slot key has NONE."""
    c = test_contiguity(T=150)
    ok("graded_has_contiguity_gradient", c["GRADED"]["contiguity_gradient"] > 0.15,
       f"gradient={c['GRADED']['contiguity_gradient']}")
    ok("orthogonal_has_no_contiguity", abs(c["ORTHOG"]["contiguity_gradient"]) < 0.03,
       f"gradient={c['ORTHOG']['contiguity_gradient']}")
    lags = c["GRADED"]["lag_similarity_1_to_10"]
    ok("graded_similarity_decays_with_lag", lags[0] > lags[-1] + 0.2, f"lag1={lags[0]} lag10={lags[-1]}")


def test_graded_errors_are_temporally_local():
    """Under a degraded WHEN-cue, GRADED errors are TEMPORALLY LOCAL (misremember when by a little --
    the brain-faithful signature) while ORTHOG errors are random -- at a small EXACT-recall cost. This
    is the separation-vs-contiguity tradeoff that motivates FACTORIZATION (TEM)."""
    comp = test_completion(T=400, dim=128, noise=0.8)
    ok("graded_errors_temporally_local",
       comp["GRADED"]["mean_temporal_error"] < 0.75 * comp["ORTHOG"]["mean_temporal_error"],
       f"graded dt={comp['GRADED']['mean_temporal_error']} orthog dt={comp['ORTHOG']['mean_temporal_error']}")
    ok("info_free_when_cue_at_chance", comp["GRADED"]["info_free_twin"] < 0.05,
       f"twin={comp['GRADED']['info_free_twin']}")


def test_schema_gist_concentrates_in_coherent_entities():
    """Radvansky 2017: routing ROUTINE events to a per-entity gist keeps the ATYPICAL (memorable) events
    recoverable by un-crowding the episodic store -- gain CONCENTRATED in high-routine entities, NULL at
    zero coherence, and an info-free (random-route) twin LOSES. Light check (few entities, N=600)."""
    N = 800
    # high-coherence entity: gist helps, twin loses
    rng = np.random.default_rng(1)
    ev, vv, aty = _make_entity(N=N, coherence=0.9, n_typical=3, rng=rng)
    all_ep = _run_arm(ev, vv, aty, "ALL_EPISODIC", 1, np.random.default_rng(2))
    gist = _run_arm(ev, vv, aty, "SCHEMA_GIST", 1, np.random.default_rng(2))
    twin = _run_arm(ev, vv, aty, "RANDOM_ROUTE_TWIN", 1, np.random.default_rng(2))
    ok("gist_beats_all_episodic_high_coherence", gist > all_ep, f"gist={gist:.3f} all_ep={all_ep:.3f}")
    ok("gist_beats_random_route_twin", gist > twin + 0.3, f"gist={gist:.3f} twin={twin:.3f}")
    # zero-coherence entity: nothing routine -> ~no gain (gain concentrated, not uniform)
    ev0, vv0, aty0 = _make_entity(N=N, coherence=0.0, n_typical=3, rng=np.random.default_rng(3))
    all0 = _run_arm(ev0, vv0, aty0, "ALL_EPISODIC", 1, np.random.default_rng(4))
    gist0 = _run_arm(ev0, vv0, aty0, "SCHEMA_GIST", 1, np.random.default_rng(4))
    ok("gain_is_null_at_zero_coherence", abs(gist0 - all0) < 1e-9, f"gain={gist0 - all0:.4f}")


def test_unified_store_race_stop_without_oracle_m():
    """The MAXIMALLY brain-foundational store (factorized content x graded-context x order, D=4096):
    race-to-stop (CMR) recovers the co-moment SET without being told how many events happened -- close to
    the oracle-m ceiling, beating naive fixed-k, and the wrong-time info-free twin loses."""
    r = test_race_stop(N=90)
    ok("race_stop_near_oracle_ceiling", r["F1_race_stop"] >= r["F1_oracle_m_ceiling"] - 0.10,
       f"race={r['F1_race_stop']:.3f} oracle={r['F1_oracle_m_ceiling']:.3f}")
    ok("race_stop_beats_fixed_k", r["F1_race_stop"] > r["F1_fixed_k2"],
       f"race={r['F1_race_stop']:.3f} fixed_k2={r['F1_fixed_k2']:.3f}")
    ok("race_stop_wrong_time_twin_loses", r["F1_race_stop"] > r["F1_info_free_twin_wrong_time"] + 0.5,
       f"race={r['F1_race_stop']:.3f} twin={r['F1_info_free_twin_wrong_time']:.3f}")


def test_unified_store_keeps_contiguity_and_degrades_gracefully():
    """The factorized store recovers exact events AND preserves TEMPORAL CONTIGUITY (the cheap fix had
    none), and under a jittered WHEN-cue its errors stay TEMPORALLY LOCAL (brain-faithful)."""
    c = unified_contiguity(N=90)
    ok("unified_preserves_contiguity", c["gradient_lag0_minus_lag7"] > 0.4,
       f"gradient={c['gradient_lag0_minus_lag7']}")
    g = test_graceful(N=90)
    ok("unified_exact_at_zero_jitter", g["jitter=0.0"]["mean_temporal_error"] < 0.5,
       f"err={g['jitter=0.0']['mean_temporal_error']}")
    ok("unified_errors_temporally_local", g["jitter=3.0"]["mean_temporal_error"] < 6.0,
       f"jitter3 err={g['jitter=3.0']['mean_temporal_error']}")


def test_unified_store_is_reconstructive_semantic_errors():
    """RECONSTRUCTIVE MEMORY (the deepest frontier fix): with GROUNDED semantic content the store's
    retrieval ERRORS land on SEMANTIC NEIGHBORS far above chance (DRM intrusion; Roediger & McDermott
    1995) -- the brain's failure mode; with random content (info-free) errors are unstructured."""
    s = test_semantic_intrusions(N=150)
    ok("semantic_content_gives_drm_intrusions", s["semantic_enrichment_x"] > 2.5,
       f"enrichment={s['semantic_enrichment_x']}x P_sem={s['P_within_cluster_error_SEMANTIC']} chance={s['chance']}")
    ok("random_content_errors_unstructured", s["P_within_cluster_error_RANDOM_twin"] < 3 * s["chance"],
       f"P_random={s['P_within_cluster_error_RANDOM_twin']} chance={s['chance']}")


def test_unified_store_event_boundary_effect():
    """EVENT SEGMENTATION (Baldassano 2017; DuBrow & Davachi 2013): the event-segmented clock CUTS
    temporal contiguity across event boundaries (within-event >> across-boundary), the uniform clock has
    no boundary structure, and a shuffled-boundary twin does not reproduce it (the effect tracks TRUE
    event structure)."""
    e = test_event_boundary_effect(horizon=120)
    ok("event_clock_cuts_contiguity_at_boundaries", e["boundary_gap_EVENT"] > 0.15,
       f"gap_event={e['boundary_gap_EVENT']}")
    ok("uniform_clock_no_boundary_structure", abs(e["boundary_gap_UNIFORM"]) < 0.05,
       f"gap_uniform={e['boundary_gap_UNIFORM']}")
    ok("boundary_effect_tracks_true_structure", e["boundary_gap_EVENT"] > e["boundary_gap_SHUFFLED_twin"] + 0.1,
       f"event={e['boundary_gap_EVENT']} shuffled={e['boundary_gap_SHUFFLED_twin']}")


def test_handmade_path_integration_relational_transfer():
    """HANDMADE (zero-training) path-integration scaffold: addresses events by RELATIONAL POSITION, so an
    event stored via one route is retrievable via a different route/time (grid-cell path-independence;
    Burak & Fiete 2009) -- which the absolute-time clock and a random context CANNOT do."""
    rt = test_relational_transfer()
    ok("path_integration_addresses_by_position", rt["recall_PATH_INTEGRATION_diff_route"] > 0.5,
       f"recall={rt['recall_PATH_INTEGRATION_diff_route']}")
    ok("absolute_time_cannot_transfer", rt["recall_PATH_INTEGRATION_diff_route"] > rt["recall_ABSOLUTE_TIME_diff_time"] + 0.4,
       f"path={rt['recall_PATH_INTEGRATION_diff_route']} abs={rt['recall_ABSOLUTE_TIME_diff_time']}")
    ok("random_ctx_twin_cannot_transfer", rt["recall_PATH_INTEGRATION_diff_route"] > rt["recall_RANDOM_ctx_twin"] + 0.4,
       f"path={rt['recall_PATH_INTEGRATION_diff_route']} rand={rt['recall_RANDOM_ctx_twin']}")


def test_sparse_dg_sharp_store_capacity_at_scale():
    """The capstone optimization (Treves & Rolls 1994; Willshaw 1969): the SHARP exact-recall store should be
    a DG expand+k-WTA SPARSE conjunctive code. At FIXED dimension, on CORRELATED content, a sparser code holds
    exact-recall to far higher scale than the dense bundle (superlinear capacity), info-free twin at chance."""
    from experiments.exp_entity_store_sparse_capacity_v1 import run as cap_run
    r = cap_run(scales=(2000, 8000), sparsities=(1.0, 0.02), n_seeds=2)
    v = r["verdict"]
    ok("sparse_dg_holds_recall_at_scale", v["SPARSE_HOLDS_BETTER_AT_SCALE"],
       f"dense@8000={v['dense_recall_at_largest_scale']} sparse@8000={v['best_sparse_recall_at_largest_scale']}")
    ok("sparse_capacity_twin_at_chance", v["twin_at_chance"], f"twin={r['twin_at_largest_scale']}")


def test_trained_successor_representation_predicts():
    """TRAINED (but brain-foundational, local-TD, freezable) Successor Representation scaffold LEARNS an
    unknown transition structure and PREDICTS the next event -- the capability the handmade addressing
    scaffold lacks (Stachenfeld 2017; Fang et al. 2023). Info-free shuffled-transition twin cannot."""
    sr = test_sr_predicts()
    ok("sr_predicts_next_event", sr["SR_next_event_pred_acc"] > 0.8,
       f"acc={sr['SR_next_event_pred_acc']} chance={sr['chance']}")
    ok("sr_beats_shuffled_transition_twin", sr["SR_next_event_pred_acc"] > sr["SR_shuffled_twin_acc"] + 0.5,
       f"sr={sr['SR_next_event_pred_acc']} twin={sr['SR_shuffled_twin_acc']}")


if __name__ == "__main__":
    test_graded_context_has_temporal_contiguity()
    test_graded_errors_are_temporally_local()
    test_schema_gist_concentrates_in_coherent_entities()
    test_unified_store_race_stop_without_oracle_m()
    test_unified_store_keeps_contiguity_and_degrades_gracefully()
    test_unified_store_is_reconstructive_semantic_errors()
    test_unified_store_event_boundary_effect()
    test_handmade_path_integration_relational_transfer()
    test_trained_successor_representation_predicts()
    test_sparse_dg_sharp_store_capacity_at_scale()
    print(f"\nALL {len(PASS)} FRONTIER CHECKS PASSED")
