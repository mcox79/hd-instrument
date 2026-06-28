#!/usr/bin/env python3
"""Atomize: hierarchical_planning_substrate_native_closed_three_failures_2026-06-28.

Third-failure-gate closure for hierarchical-planning mechanism class. Three smoke
HARD_FAILs across three distinct mechanism classes (closed-form D_macro pseudoinverse;
state-conditioned + disjoint-block revival; Sutton-Precup 1999 options pi/beta/I)
all collapsed near-floor at substrate's bipolar-HRR encoding regime. Pre-reg
THIRD-FAILURE GATE clause locked closure (no 4th iteration without USER consensus).

Cell:          experiments/exp_substrate_hierarchical_options_v1.py
Pre-reg:       preregs/2026-06-28_substrate_hierarchical_options_v1.md
Metrics:       data/exp_substrate_hierarchical_options_v1_smoke/metrics.json
Verdict:       HARD_FAIL | THIRD_FAILURE_GATE
Closure tier:  capability_closed_three_mechanism_failures
Cert delta:    0 (honest_negative; closure aggregates 3 prior HF cells)

Atomizes:
  1) The capability-closed result atom (math::T3, experiment_record, HONEST_NEGATIVE)
  2) META_RULE_AO capability-closure-after-3-mechanism-class-HF (meta corpus)

Auditor: skunkworks (cert-owner; A5-gated write + round-trip verify + cert_ledger row).
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
)

STORE_ROOT = REPO / 'data' / 'substrate_index'


def build_capability_closed_atom() -> Atom:
    """Closure atom: hierarchical planning, 3 mechanism classes HARD_FAILed."""
    return Atom(
        id=(
            "T3/EXP_substrate_hierarchical_options_v1_HONEST_NEGATIVE_"
            "CAPABILITY_CLOSED_three_mechanism_class_failures_closed_form_"
            "Dmacro_state_cond_disjoint_options_pi_beta_I_substrate_bipolar_HRR_"
            "cannot_preserve_compositional_partial_progress_signal_at_depth6"
        ),
        name=(
            "Hierarchical planning capability CLOSED at substrate bipolar-HRR "
            "regime: 3 mechanism classes HARD_FAILed (closed-form D_macro / "
            "state-cond+disjoint / Sutton-Precup options)"
        ),
        description=(
            "Third-failure-gate closure for hierarchical-planning capability "
            "class at substrate's current bipolar-HRR encoding regime. "
            "Three consecutive smoke HARD_FAILs across three distinct "
            "mechanism classes converge on the same diagnosis: substrate's "
            "sum-encoded HRR cosine landscape over BlocksWorld state-encodings "
            "does NOT preserve compositional partial-progress signal at "
            "composite-depth >= 6. Greedy goal-cosine primitive selection "
            "yields null progress; the substrate cannot 'see' intermediate "
            "sub-goals as useful waypoints. "
            "Cells (3): (1) substrate_hierarchical_subgoal_planner_v1 "
            "(closed-form D_macro pseudoinverse; TREE=0.000 FLAT=0.133); "
            "(2) substrate_hierarchical_planner_state_conditioned_disjoint_v1 "
            "(state-conditioned + disjoint-block; SC=0.000 DJ=0.000 BOTH=0.000); "
            "(3) substrate_hierarchical_options_v1 (Sutton-Precup 1999 "
            "options pi/beta/I; OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 "
            "CF=0.100 RAND=0.000; arms_distinct=True; cardinality_ok=True; "
            "chance_floor=2.143e-05). "
            "All three cells: arms_distinct=True (SHA-256 per-arm seq trace), "
            "cardinality_ok=True, discriminator-must-survive-scale at "
            "N=8192 + composite-depth=6 with full options active. "
            "Per pre-reg THIRD-FAILURE GATE locked at module init: "
            "capability box CLOSED; no 4th iteration at this regime without "
            "USER + research consensus on a fundamentally new mechanism class "
            "(e.g. pretrained-encoder swap-in; substrate-product pivot, NOT "
            "a hierarchical-planning iteration). "
            "M3 implications: USER concern #5 (hierarchical goal-decomposition) "
            "DEFERRED at current regime; M3 demo must reframe around "
            "substrate's chain-grade strengths (audit-device, KG-traversal, "
            "refuse-gate, multi-hop iter_cleanup). "
            "M4 implications: substrate-as-research-director Director-options "
            "framing with beta termination per-option DEFERRED -- "
            "cosine-termination falsified at composite depth in this cell. "
            "Composes Three-Smoke-Disciplines (2026-06-26), "
            "discriminator-must-survive-scale (USER 2026-06-26), "
            "META_RULE_AG un-saturated band, META_RULE_AF arms-must-differ, "
            "META_RULE_AH atomic-write + cardinality_ok, "
            "META_RULE_AL 3-channel-encoding-before-readout."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "capability_closed_three_mechanism_failures",
            "record_class": "experiment_record",
            "term_class": "CAPABILITY_CLOSED",
            "metric_type": "solve_rate_composite_depth6",
            "verdict": "HARD_FAIL",
            "verdict_raw": (
                "HARD_FAIL | THIRD_FAILURE_GATE (options=0.000 <= 0.20; "
                "3rd consecutive HARD_FAIL on hierarchical-planning "
                "mechanism class; close capability box) | "
                "OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 "
                "RAND=0.000 | OPTS-POLICY=0.000 OPTS-CF=-0.100 "
                "OPTS-RAND=0.000 cv=inf arms_distinct=True "
                "chance_floor=2.143e-05"
            ),
            "run_mode": "smoke",
            "experiment_path": "experiments/exp_substrate_hierarchical_options_v1.py",
            "prereg_path": "preregs/2026-06-28_substrate_hierarchical_options_v1.md",
            "metrics_path": "data/exp_substrate_hierarchical_options_v1_smoke/metrics.json",
            "closure_note_path": "notes/exp_dev_capability_closed_hierarchical_planning_2026-06-28.md",
            "cell_sha": None,
            "remote_run_id": None,
            "hypothesis": (
                "Sutton-Precup 1999 options pi/beta/I as separate substrate "
                "channels (NOT bundled HRR) would dissolve the D_macro "
                "averaging problem and lift solve_rate to >= 0.55 at "
                "composite-depth=6 BlocksWorld."
            ),
            "metrics_headline": (
                "OPTS=0.000 (mechanism); POLICY=0.000 (pi-only); "
                "INIT=0.050 (pi+I); TERM=0.000 (pi+beta); CF=0.100 "
                "(prior D_macro baseline; replicates HF); RAND=0.000 (floor)"
            ),
            "key_metrics": {
                "options_full_solve_rate": 0.000,
                "policy_only_solve_rate": 0.000,
                "init_only_solve_rate": 0.050,
                "term_only_solve_rate": 0.000,
                "closed_form_baseline_solve_rate": 0.100,
                "random_solve_rate": 0.000,
                "chance_random_floor": 2.143347050754458e-05,
                "n_goals_smoke": 20,
                "n_arms": 6,
                "n_seeds_complete": 1,
                "cardinality_ok": True,
                "expected_n_units": 120,
                "completed_units": 120,
                "elapsed_s": 7.8,
                "arms_distinct": True,
            },
            "relevance_tier": "PROGRAM_LOAD_BEARING_CLOSURE",
            "closure_mechanism_classes": [
                "closed_form_Dmacro_pseudoinverse",
                "state_conditioned_disjoint_block",
                "Sutton_Precup_1999_options_pi_beta_I",
            ],
            "closure_prior_cells": [
                "data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json",
                "data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json",
                "data/exp_substrate_hierarchical_options_v1_smoke/metrics.json",
            ],
            "third_failure_gate_triggered": True,
            "discriminator_survived_scale": True,
            "regime_at_smoke": "N=8192,composite_depth=6,blocks=4,pos=3,actions=6,options=3",
            "arm_sha256_per_seed7": {
                "options_full": "844c39be87e482be",
                "policy_only": "5af55a8ce229a3cd",
                "init_only": "4fb8e25dd1736b12",
                "term_only": "2c12489aebaa53d3",
                "closed_form_baseline": "8a4191653c4588b0",
                "random": "63216b3711925ef1",
            },
            "root_diagnosis": (
                "substrate sum-encoded HRR does NOT preserve compositional "
                "partial-progress signal at composite depth >= 6; greedy "
                "goal-cosine primitive selection yields null progress; "
                "ALL three mechanism classes fail for the same encoding "
                "reason, not for mechanism-specific reasons"
            ),
            "implications": {
                "M3": (
                    "USER concern #5 hierarchical goal-decomposition DEFERRED; "
                    "reframe demo around substrate chain-grade strengths "
                    "(audit-device, KG-traversal, refuse-gate, "
                    "multi-hop iter_cleanup)"
                ),
                "M4": (
                    "substrate-as-research-director Director-options framing "
                    "DEFERRED; cosine-termination falsified at composite depth"
                ),
                "user_substrate_plans_all_day": (
                    "documented KNOWN GAP; deferred to future capacity-extension"
                ),
            },
            "no_4th_iteration_without_consensus": True,
            "atomization_session": "skunkworks_2026-06-28_post-third-failure-gate",
            "composes_with": [
                "feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26",
                "feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26",
                "META_RULE_AF",
                "META_RULE_AG",
                "META_RULE_AH",
                "META_RULE_AL",
                "META_RULE_AN",
            ],
        },
    )


def build_meta_rule_ao_atom() -> Atom:
    """META_RULE_AO: 3-mechanism-class-HF closure rule."""
    return Atom(
        id=(
            "T_methodology/META_RULE_AO_capability_closure_after_3_mechanism_"
            "class_HF_when_three_consecutive_smoke_HARD_FAILs_on_same_"
            "capability_across_distinct_mechanism_classes_close_capability_box_"
            "file_capability_closed_atom_no_4th_iteration_without_USER_and_"
            "research_consensus_on_new_mechanism_class_witness_hierarchical_"
            "planning_closed_form_Dmacro_then_state_cond_disjoint_then_Sutton_"
            "Precup_options_all_HF_at_substrate_bipolar_HRR_regime_2026-06-28"
        ),
        name=(
            "META_RULE_AO -- capability-closure after 3 mechanism-class HARD_FAILs"
        ),
        description=(
            "When three consecutive smoke HARD_FAILs land on the same "
            "capability across DISTINCT mechanism classes (not iterations of "
            "the same mechanism), the capability box at the current substrate "
            "regime closes. File a capability-closed atom; do not iterate a "
            "4th time without USER + research consensus on a fundamentally "
            "new mechanism class (typically a substrate-product pivot like "
            "pretrained-encoder swap-in or block-sparse codes, NOT another "
            "variation on the same encoding). The closure is OFFICIAL at "
            "the 3rd HF if (a) all 3 cells satisfy arms_distinct + "
            "cardinality_ok + discriminator-survives-scale, and (b) the 3 "
            "cells span distinct mechanism classes (e.g. closed-form vs "
            "iterative-policy vs option-framework), and (c) the diagnoses "
            "converge on a substrate-encoding root cause rather than "
            "mechanism-specific failure. Pre-reg the THIRD-FAILURE GATE in "
            "the 3rd cell so closure triggers at smoke time without "
            "requiring full dispatch. "
            "Witness 2026-06-28: hierarchical-planning closed across "
            "closed-form D_macro pseudoinverse + state-conditioned+disjoint "
            "+ Sutton-Precup 1999 options pi/beta/I; all 3 cells "
            "arms_distinct + cardinality_ok + N=8192 + composite-depth=6; "
            "all converge on substrate sum-encoded HRR not preserving "
            "compositional partial-progress signal. "
            "Discipline extends Three-Smoke-Disciplines (2026-06-26) at the "
            "MULTI-CELL layer: smoke-discipline catches per-cell failures; "
            "META_RULE_AO catches a CAPABILITY-LEVEL failure pattern that "
            "single-cell smoke gates cannot see."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": None,
            "confirmed_or_candidate": "CONFIRMED",
            "rule_id": "META_RULE_AO",
            "rule_class": "capability_closure_multi_cell_aggregate",
            "first_witness_date": "2026-06-28",
            "first_witness_capability": "hierarchical_planning_at_substrate_bipolar_HRR",
            "first_witness_cells": [
                "exp_substrate_hierarchical_subgoal_planner_v1_smoke",
                "exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke",
                "exp_substrate_hierarchical_options_v1_smoke",
            ],
            "preconditions_for_closure": [
                "3 consecutive smoke HARD_FAILs",
                "distinct mechanism classes (not iterations of same)",
                "all cells arms_distinct=True",
                "all cells cardinality_ok=True",
                "all cells discriminator-survives-scale at full N regime",
                "diagnoses converge on substrate-encoding root (not mech-specific)",
            ],
            "closure_action": (
                "file capability-closed atom (math::T3 experiment_record "
                "HONEST_NEGATIVE); no 4th iteration without USER + research "
                "consensus on new mechanism class; recommend program-level "
                "pivot (e.g. substrate-product encoder swap)"
            ),
            "composes_with": [
                "META_RULE_AF",   # arms-must-differ
                "META_RULE_AG",   # un-saturated band
                "META_RULE_AH",   # atomic-write + cardinality_ok
                "META_RULE_AL",   # encoding-before-readout
                "META_RULE_AN",   # cone-collapse extrapolation
            ],
            "supersedes": None,
            "atomized_by": "skunkworks",
            "atomized_session": "2026-06-28_post-third-failure-gate",
        },
    )


def main():
    apply_mode = "--apply" in sys.argv
    if not apply_mode:
        print("USAGE: python tools/atomize_hierarchical_planning_capability_closed_2026-06-28.py --apply")
        print()
        print("Will atomize:")
        a1 = build_capability_closed_atom()
        a2 = build_meta_rule_ao_atom()
        print(f"  1. {a1.id[:90]}...")
        print(f"     kind={a1.kind.value} tier={a1.tier.value} corpus={a1.corpus.value}")
        print(f"     pq={(a1.metadata or {}).get('provenance_quality')}")
        print(f"     cert_status={(a1.metadata or {}).get('cert_status')}")
        print(f"  2. {a2.id[:90]}...")
        print(f"     kind={a2.kind.value} tier={a2.tier.value} corpus={a2.corpus.value}")
        return 0

    # A5 PRE-snapshot
    ps = PartitionedStore(STORE_ROOT)
    cert_n_pre = sum(
        1 for a in ps.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )
    print(f"A5 PRE: CERT_N={cert_n_pre}")

    # Atom 1: capability-closed result
    a1 = build_capability_closed_atom()
    qid1 = f"{a1.corpus.value}::{a1.id}"
    if ps.get_atom(qid1) is not None:
        print(f"SKIP a1 (idempotent): {a1.id} already present.")
    else:
        print(f"ADDING a1: {a1.id[:90]}...")
        ps.add_atom(
            a1,
            source="skunkworks_atomize_hierarchical_planning_capability_closed_2026-06-28",
            note=(
                "Third-failure-gate closure for hierarchical-planning capability "
                "class at substrate bipolar-HRR regime; 3 mechanism classes "
                "HF-converged on substrate-encoding root diagnosis; HONEST_NEGATIVE "
                "cert_class=capability_closed_three_mechanism_failures. "
                "Anchor: data/exp_substrate_hierarchical_options_v1_smoke/metrics.json. "
                "Cell + pre-reg + closure-note pointers in atom.metadata. "
                "Composes Three-Smoke-Disciplines + discriminator-must-survive-scale + "
                "META_RULE_AF/AG/AH/AL/AN."
            ),
        )

    # Atom 2: META_RULE_AO
    a2 = build_meta_rule_ao_atom()
    qid2 = f"{a2.corpus.value}::{a2.id}"
    if ps.get_atom(qid2) is not None:
        print(f"SKIP a2 (idempotent): {a2.id[:90]}... already present.")
    else:
        print(f"ADDING a2: {a2.id[:90]}...")
        ps.add_atom(
            a2,
            source="skunkworks_atomize_meta_rule_AO_capability_closure_after_3_mechanism_class_HF_2026-06-28",
            note=(
                "META_RULE_AO -- capability-closure after 3-mechanism-class HF. "
                "Extends Three-Smoke-Disciplines at MULTI-CELL layer (single-cell "
                "smoke gates can't see capability-level failure patterns). First "
                "witness: hierarchical-planning closed 2026-06-28 across "
                "closed-form D_macro / state-cond+disjoint / Sutton-Precup options."
            ),
        )

    # Fresh-Store round-trip verify (inst-240 gate)
    ps2 = PartitionedStore(STORE_ROOT)
    all_atoms = list(ps2.all_atoms())
    found1 = next((a for a in all_atoms if a.id == a1.id), None)
    found2 = next((a for a in all_atoms if a.id == a2.id), None)
    assert found1 is not None, "a1 round-trip FAILED -- not found post-add"
    assert found1.tier == a1.tier, f"a1 tier mismatch: {found1.tier} != {a1.tier}"
    assert found1.kind == a1.kind, f"a1 kind mismatch: {found1.kind} != {a1.kind}"
    assert found2 is not None, "a2 round-trip FAILED -- not found post-add"
    assert found2.tier == a2.tier, f"a2 tier mismatch: {found2.tier} != {a2.tier}"
    assert found2.kind == a2.kind, f"a2 kind mismatch: {found2.kind} != {a2.kind}"
    print(f"PASS: a1 + a2 round-trip survival OK (Atom.from_dict clean)")

    # A5 POST-snapshot
    cert_n_post = sum(
        1 for a in ps2.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )
    expected_delta = 0  # honest_negative => CERT N unchanged
    actual_delta = cert_n_post - cert_n_pre
    print(f"A5 POST: CERT_N={cert_n_post} (delta={actual_delta}, expected={expected_delta})")
    assert actual_delta == expected_delta, (
        f"A5 violation: cert_n delta {actual_delta} != expected {expected_delta} "
        f"(honest_negative should not change CERT N)"
    )

    # Cert-ledger row (honest_negative; delta=0)
    ledger_row = build_honest_negative_row(
        atom_id=f"math::{a1.id}",
        cell_commit=None,
        notes_path="notes/exp_dev_capability_closed_hierarchical_planning_2026-06-28.md",
        metrics_path="data/exp_substrate_hierarchical_options_v1_smoke/metrics.json",
        verdict="HARD_FAIL",
        note=(
            "third_failure_gate_capability_closed_hierarchical_planning_"
            "3_mechanism_classes_HF_substrate_bipolar_HRR_encoding_root"
        ),
    )
    print(f"Appending cert-ledger row: op={ledger_row.get('op')} status={ledger_row.get('cert_status')} delta={ledger_row.get('cert_increment_delta')}")
    row_h = append_cert_ledger_row(
        ledger_row,
        expected_cert_n_pre=cert_n_pre,
        expected_cert_n_post=cert_n_post,
    )
    print(f"Ledger row appended; row_hash={row_h}")

    print()
    print("=" * 80)
    print("ATOMIZE COMPLETE")
    print(f"  CERT_N: {cert_n_pre} -> {cert_n_post} (delta=0; honest_negative)")
    print(f"  Closure atoms: 2 (capability-closed result + META_RULE_AO)")
    print(f"  Ledger row hash: {row_h}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
