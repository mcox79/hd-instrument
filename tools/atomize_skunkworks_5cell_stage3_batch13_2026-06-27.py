"""Atomize: Skunkworks 5-cell Stage 3 batch 13 landed-VET (2026-06-27).

Source request:
  Director batch dispatch covering 6 candidate cells from Stage 3 / counterfactual /
  encoder windows since batch 12 (commit 5e78b4c1).

VERIFY-OFF-DATA basis (.venv Python; each metrics.json Read end-to-end on disk;
per-arm cross-checked against Director's framings; refusals filed where claims did
not survive verification):

  Cell 1  TOM Sally-Anne nested HRR  v1  localsmoke  -> MEASURED_MECHANISM (smoke HP cleared; full pending)
  Cell 2  schema-exemplar-Bayes-K20  v1  smoke      -> MEASURED_MECHANISM (smoke HP cleared; full pending)
  Cell 3  schema-context-prior       v1  smoke      -> MEASURED_MECHANISM (informative-null vs exemplar)
  Cell 4  CF replay latency delta-stack v2 single   -> MEASURED_MECHANISM (smoke HP; AUTO-PROMOTE REFUSED)
  Cell 5  sub-atom encoder v2 Mathlib FULL          -> HONEST_NEGATIVE (Mathlib-as-corpus saturates baseline)

  + META candidate (1st occurrence atomized cleanly): META_RULE_AL substrate-cosine-kernel-
    pre-encodes-schema-prior  -- emergent from Cell 3 (Director flagged as 3rd occurrence
    of "substrate already does X" pattern today; this is the first clean atomization).

REFUSE (filed in landed-vet note; no atom):

  Cell 6  CF Cell 1 regret-comparison vmPFC v1 (claimed path
          exp_counterfactual_regret_comparison_vmpfc_v1/metrics.json)
          ROOT CAUSE: PATH DOES NOT EXIST ON DISK. Glob for *regret* / *vmpfc* /
          *counterfactual_regret* returns zero hits in data/. Director cited vmPFC R^2=0.984 /
          Spearman=0.986 / value_leak=0.028 / full-N preview R^2=0.987 -- all fabricated or
          referring to a cell never authored/landed. Cannot atomize; full landing pending
          OR cell-author confusion with another anchor.

REFUSE parent auto-promote:
  Cell 4 v2 cell-author flag claims parent_anchor = causal_counterfactual_replay_v1 should
  auto-promote MIDDLE_BAND -> chain-grade based on v2 evidence. METHODOLOGY REFUSAL:
  - Parent v1 metric was: 1 seed, intervention_ms=16.864ms, accuracy=1.000, run_mode=smoke
  - Parent v1 MIDDLE_BAND root cause: 1-seed AND intervention_ms > 10ms HP target
  - v2 ran a DIFFERENT cell (delta-stack architecture) with a DIFFERENT baseline arm
    (BASELINE_FULL_REWRITE at 11.497ms) achieving 2.103ms via delta-stack
  - The 5.47x speedup is real but it's v2's-own-baseline vs v2's-delta-arm, NOT a re-run
    of parent v1's exact configuration
  - Auto-promote of parent v1 would require re-running parent v1 with 2+ seeds AND
    demonstrating < 10ms; v2 evidence cannot retroactively satisfy parent v1's HP
  - File v2 as MEASURED_MECHANISM standalone; parent v1 remains MIDDLE_BAND pending
    parent-redispatch with multi-seed at < 10ms.

NET CERT delta: +0 (no chain-grade; 4 MM + 1 HN + 1 META; honest downward correction
vs Director framing of "+3-4 chain-grade -> 626 -> 630").

PRE CERT N (verified live): 626
POST CERT N (predicted; A5-gated): 626

LEDGER ROWS: 6 (4 measured_mechanism + 1 honest_negative + 1 discipline_meta)

A5 GATING: PRE/POST cert_n assertions on every window; round-trip pq check on every atom.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_stage3_batch13_2026-06-27.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_stage3_batch13_2026-06-27.py --apply    # WRITE
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_5cell_stage3_batch13_2026-06-27.md"
CELL_COMMIT = "n/a-2026-06-27-batch13-stage3-sweep"
ATOMIZED_BY = "skunkworks_atomize_5cell_stage3_batch13_2026-06-27"

METRICS_TOM = "data/exp_theory_of_mind_sally_anne_nested_hrr_v1_localsmoke/metrics.json"
METRICS_SCHEMA_EX = "data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json"
METRICS_SCHEMA_CTX = "data/exp_cortex_schema_instantiation_context_prior_v1_smoke/metrics.json"
METRICS_CF_V2 = "data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json"
METRICS_CF_V1_PARENT = "data/exp_causal_counterfactual_replay_v1/metrics.json"
METRICS_SUBATOM_MATHLIB = "data/exp_sub_atom_token_stream_encoder_v2_real_mathlib/metrics.json"


# ============================================================================
# ATOM 1 -- TOM Sally-Anne nested HRR MEASURED_MECHANISM (delta=0)
# ============================================================================

def build_atom1_tom_sally_anne_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_theory_of_mind_sally_anne_nested_hrr_v1_MEASURED_MECHANISM_smoke_"
            "Q2_false_belief_0p900_Q3_second_order_0p875_gap_0p725_cv_0p056_n_seeds_2_"
            "N2048_V_REL128_arms_distinct_full_pending_brain_TPJ_mPFC_Stage3_foundational"
        ),
        name=(
            "theory_of_mind_sally_anne_nested_hrr v1 MEASURED_MECHANISM at smoke: Q2_false_belief=0.900 "
            "Q3_second_order=0.875 gap_over_baseline=0.725 cv=0.056 n_seeds=2 N=2048 V_REL=128; "
            "full-dispatch pending for chain-grade promotion"
        ),
        description=(
            "MEASURED_MECHANISM TOM nested-HRR mechanism at smoke (delta=0; cert pathway clear).\n"
            "Sally-Anne false-belief + 2nd-order recursive ToM cleared HP floors at smoke regime\n"
            "(N=2048, V_REL=128, 2 seeds, 80 queries per arm-seed). Full-N dispatched but not\n"
            "yet landed; promotion to chain-grade gated on full-N evidence.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 2 seeds: 7, 17;\n"
            "5 arms = no_partition_baseline / partition_no_refuse / full_tom / ground_truth_oracle\n"
            "/ diag_tom_lite; per-arm per-question verified per-seed):\n"
            "  Cardinality: 720/720 OK (4 main arms x 80 queries x 2 seeds + diag 40 x 2 = 720).\n"
            "  Per-arm Q2 (false-belief task; HP_Q2 >= 0.65):\n"
            "    no_partition_baseline  {7: 0.20,  17: 0.15}  mean=0.175 cv=0.143\n"
            "    partition_no_refuse    {7: 0.00,  17: 0.00}  mean=0.000 cv=0.0\n"
            "    full_tom               {7: 0.85,  17: 0.95}  mean=0.900 cv=0.056\n"
            "    ground_truth_oracle    {7: 1.00,  17: 1.00}  mean=1.000 cv=0.0\n"
            "  Q3 second-order recursive (HP_Q3 >= 0.50):\n"
            "    full_tom               {7: 0.90,  17: 0.85}  mean=0.875 cv=0.029\n"
            "  Q1 world-state recall (HP_Q1 >= 0.65):\n"
            "    full_tom               {7: 0.95,  17: 0.85}  mean=0.900 cv=0.056\n"
            "  Discriminator: gap_Q2_over_baseline = 0.900 - 0.175 = 0.725 (HP >= 0.40); ARMS\n"
            "    DISTINCT pairwise verified (full_tom vs all non-oracle disagreement >= 0.62;\n"
            "    arms_distinct_all_seeds=True; baseline_in_band=True at 0.175 in [0.05, 0.50]).\n"
            "  Diag 5b (agent-partition recall): {7: 1.00, 17: 1.00}; 5a (no-partition): {0.35,\n"
            "    0.35}; diag gap = 0.65 (HP_diag_gap >= 0.30 cleared).\n\n"
            "SCOPE OF THE MEASURED_MECHANISM CLAIM:\n"
            "  CLAIM: 'Nested-HRR + agent-partition + refuse-gate mechanism achieves Q2 false-belief\n"
            "    accuracy 0.90 +/- 0.05 and Q3 2nd-order 0.875 +/- 0.025 at N=2048, V_REL=128,\n"
            "    with 4-arm discriminator (gap=0.725 over no-partition baseline; oracle ceiling=1.0).'\n"
            "  VERIFIED: per-seed numbers reproduce from per_arm Q2/Q3 values in metrics.json;\n"
            "    cv computed std/mean per-arm; baseline-in-band confirmed at 0.175.\n"
            "  SCOPE INCLUDES: smoke regime at N=2048, V_REL=128, 2 seeds, 80 queries/arm.\n"
            "  SCOPE EXCLUDES: full-N scaling (Director cited 'Q2=0.665-0.780' as preview but\n"
            "    those numbers are NOT in either on-disk metrics.json -- localsmoke shows 0.900\n"
            "    at N=2048; the other dir exp_theory_of_mind_sally_anne_nested_hrr_v1/ is\n"
            "    SELFTEST_OK with Q2=0.800 at N=1024 seed=[7] only); larger n_agents/n_objects.\n\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-default-conservatism):\n"
            "  Per Fix #28 + Skunkworks-overrides-Director discipline: smoke evidence at 2 seeds\n"
            "  with HP clearance is MEASURED_MECHANISM by default; full-dispatch with 3+ seeds\n"
            "  required for chain-grade tier. Director-cited full-N preview unverifiable on disk.\n"
            "  The smoke-N here IS substantial (N=2048 is production-scale per Director Fix #16\n"
            "  discriminator-must-survive-scale), so chain-grade pathway is clear; promotion\n"
            "  pending the full-N landing.\n\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Sally-Anne false-belief is the classical psych-developmental TOM probe (4-yr-old\n"
            "  threshold). Brain analogs: TPJ (temporo-parietal junction) for mentalizing /\n"
            "  agent-state tracking; mPFC (medial PFC) for self/other distinction. Nested-HRR\n"
            "  with agent-partition + refuse-gate is the substrate-native primitive realizing\n"
            "  these brain-region roles algebraically (agent role-binding partitions belief\n"
            "  states; cleanup-with-refuse separates known-from-unknown). Foundational M3-\n"
            "  capability building block.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 720/720 OK\n"
            "  META_RULE_J no-silent-except: smoke completed; no halts (hardening L1early+L2per\n"
            "    seed+L3outertry+L4importsentinel+META_RULE_AF+AH+AG per config_version)\n"
            "  META_RULE_K discriminator: full_tom (0.900) vs no_partition_baseline (0.175) gap\n"
            "    0.725; partition_no_refuse (0.000) demonstrates refuse-mechanism necessity;\n"
            "    oracle (1.000) ceiling; arms_differ_verified=True\n"
            "  META_RULE_L band: full_tom Q2 in [0.65, 0.95] active band; baseline 0.175 in\n"
            "    expected [0.05, 0.50] baseline-band; not saturated\n"
            "  META_RULE_AA fairness: oracle establishes ceiling at 1.0; full_tom legitimately\n"
            "    below oracle (0.9 vs 1.0) -- not at-cap; fair_baseline_ok\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; HRR nested-bind + cleanup + refuse).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "theory_of_mind_sally_anne_nested_hrr_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_TOM,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 2,
            "seeds": [7, 17],
            "N_DIM": 2048,
            "V_REL": 128,
            "n_agents": 3,
            "n_objects": 4,
            "n_locs": 4,
            "n_trials": 20,
            "Q2_false_belief_mean_MEASURED": 0.900,
            "Q2_false_belief_cv_MEASURED": 0.056,
            "Q3_second_order_mean_MEASURED": 0.875,
            "Q3_second_order_cv_MEASURED": 0.029,
            "Q1_world_mean_MEASURED": 0.900,
            "baseline_Q2_no_partition_MEASURED": 0.175,
            "gap_Q2_over_baseline_MEASURED": 0.725,
            "oracle_Q2_MEASURED": 1.000,
            "diag_5a_no_partition_MEASURED": 0.35,
            "diag_5b_with_partition_MEASURED": 1.0,
            "arms_distinct_all_seeds_MEASURED": True,
            "baseline_in_band_MEASURED": True,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "full_tom_Q2_0p900_in_active_band_baseline_0p175_in_expected",
            "full_dispatch_pending_HYPOTHESIZED": True,
            "full_n_preview_director_cited_NOT_ON_DISK": True,
            "scope_observed": "smoke_N2048_V_REL128_n_agents3_n_objects4_2_seeds_80q_per_arm",
            "scope_not_claimed": "full_N_scaling_OR_larger_n_agents_OR_chain_grade_tier",
            "brain_analog": "TPJ_mentalizing_plus_mPFC_self_other_distinction",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- schema-exemplar-Bayes MEASURED_MECHANISM (delta=0)
# ============================================================================

def build_atom2_schema_exemplar_bayes_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_cortex_schema_exemplar_bayes_importance_sample_v1_MEASURED_MECHANISM_smoke_"
            "K_NEAREST_K20_0p728_baseline_0p256_random_0p235_oracle_0p809_lift_over_base_0p472_"
            "cv_0p015_n_seeds_3_arms_distinct_K_sensitivity_K5_0p636_K20_0p728_K50_0p727_full_pending"
        ),
        name=(
            "cortex_schema_exemplar_bayes_importance_sample v1 MEASURED_MECHANISM at smoke: "
            "K-nearest exemplar Bayes K=20 recall=0.728 vs no-schema baseline=0.256 (lift +0.472) "
            "vs random-K=0.235 vs oracle=0.809; cv=0.015 n_seeds=3; full-dispatch pending for chain-grade"
        ),
        description=(
            "MEASURED_MECHANISM cortex schema-driven exemplar-Bayes K-nearest at smoke (delta=0).\n"
            "Importance-sampling K-nearest exemplar Bayes prior over schema slots achieves 0.728\n"
            "recall (lift +0.472 over no-schema baseline; lift +0.493 over random-K control) at\n"
            "smoke regime. Oracle ceiling 0.809 confirms no fairness-saturation. K-sensitivity\n"
            "fires correctly: K5 < K20 ~ K50 (importance-weighted, plateaus at K>=20).\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 7, 17, 23;\n"
            "6 arms = no_schema_baseline / random_K / K_nearest_K5 / K_nearest_K20 / K_nearest_K50\n"
            "/ oracle_true_schema; per-arm per-seed verified):\n"
            "  Cardinality: 12960/12960 OK (6 arms x 2160 events x 3 seeds = 38880 implicit;\n"
            "    expected_n_units=12960 matches metrics; events_per_arm_total=2160 = expected).\n"
            "  Per-arm recall (HP_floor >= 0.50; HP_lift_base >= 0.30; HP_lift_rand >= 0.30):\n"
            "    ARM_NO_SCHEMA_BASELINE  {7: 0.226, 17: 0.283, 23: 0.258}  mean=0.256 cv=0.091\n"
            "    ARM_RANDOM_K_EXEMPLARS  {7: 0.228, 17: 0.244, 23: 0.232}  mean=0.235 cv=0.030\n"
            "    ARM_K_NEAREST_K5        {7: 0.649, 17: 0.633, 23: 0.625}  mean=0.636 cv=0.015\n"
            "    ARM_K_NEAREST_K20       {7: 0.717, 17: 0.724, 23: 0.743}  mean=0.728 cv=0.015 *PRIMARY*\n"
            "    ARM_K_NEAREST_K50       {7: 0.717, 17: 0.721, 23: 0.743}  mean=0.727 cv=0.016\n"
            "    ARM_ORACLE_TRUE_SCHEMA  {7: 0.808, 17: 0.800, 23: 0.819}  mean=0.809 cv=0.010\n"
            "  Discriminator: primary 0.728 - baseline 0.256 = +0.472 lift (HP >= 0.30 cleared);\n"
            "    primary 0.728 - random_K 0.235 = +0.493 (HP >= 0.30 cleared); primary < oracle\n"
            "    0.809 by 0.081 (legitimate gap; not at-cap; fair_baseline_ok).\n"
            "  K-sensitivity: K5 (0.636) < K20 (0.728) ~ K50 (0.727) -- importance-weighting\n"
            "    plateaus at K>=20 confirming the mechanism rather than nearest-neighbor effect.\n\n"
            "SCOPE OF THE MEASURED_MECHANISM CLAIM:\n"
            "  CLAIM: 'K-nearest exemplar Bayes importance-sampling over substrate schema slots\n"
            "    achieves recall 0.728 +/- 0.011 at smoke regime (N=2048, VSLOT=8, MSLOTS=6,\n"
            "    KSCH=8, NEX=20, FN=0.20, MF=0.50, 3 seeds), lift +0.472 over no-schema baseline.'\n"
            "  VERIFIED: per-seed numbers reproduce from per_arm_recall_summary.per_seed arrays;\n"
            "    cv = std/mean per-arm matches metrics; lift = primary - baseline arithmetic.\n"
            "  SCOPE INCLUDES: smoke at N=2048, 3 seeds, 6 arms, 2160 events per arm.\n"
            "  SCOPE EXCLUDES: full-N scaling (cell-author flagged full dispatched remote pos 15;\n"
            "    not yet landed); larger NEX / KSCH / VSLOT sweeps.\n\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-default-conservatism):\n"
            "  Per Fix #28 + Skunkworks-overrides-Director: 3-seed smoke at HP-clearance lift\n"
            "  is MEASURED_MECHANISM by default; full-dispatch evidence required to tier up.\n"
            "  Discriminator is clean and arms genuinely distinct; mechanism IS proven to work\n"
            "  at this regime. Chain-grade pathway is clear pending full-N landing.\n\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Cortical schema-driven recall: hippocampus encodes episode-specific exemplars;\n"
            "  vmPFC / OFC retrieves schema-prior; convergence yields posterior over slot fillers.\n"
            "  K-nearest importance-sampling is the substrate-native realization of mixture-of-\n"
            "  experts schema prior over exemplar memories (analog: Tse-Morris 2007 schema-\n"
            "  facilitated consolidation; Preston-Eichenbaum 2013 schema-mediated memory).\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 12960/12960 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L4importsentinel+\n"
            "    CARDINALITY_OK+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR\n"
            "  META_RULE_K discriminator: primary vs baseline lift +0.472 (clean fire); K-\n"
            "    sensitivity K5/K20/K50 demonstrates mechanism dose-response\n"
            "  META_RULE_L band: primary 0.728 in [0.50, 0.80] active; baseline 0.256 in\n"
            "    [0.20, 0.30] expected-band; oracle 0.809 legitimate ceiling; not at cap\n"
            "  META_RULE_AA fairness: oracle 0.809 > primary 0.728 by 0.081; not at-cap;\n"
            "    arms_differ_verified=True\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; K-nearest cosine + Bayes update).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "cortex_schema_exemplar_bayes_importance_sample_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_SCHEMA_EX,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 2048,
            "VSLOT": 8,
            "MSLOTS": 6,
            "KSCH": 8,
            "NEX": 20,
            "primary_arm": "ARM_K_NEAREST_K20",
            "primary_recall_MEASURED": 0.728,
            "primary_cv_MEASURED": 0.015,
            "baseline_recall_MEASURED": 0.256,
            "random_k_recall_MEASURED": 0.235,
            "oracle_recall_MEASURED": 0.809,
            "lift_over_baseline_MEASURED": 0.472,
            "lift_over_random_k_MEASURED": 0.493,
            "K_NEAREST_K5_MEASURED": 0.636,
            "K_NEAREST_K20_MEASURED": 0.728,
            "K_NEAREST_K50_MEASURED": 0.727,
            "arms_differ_verified_MEASURED": True,
            "cardinality_ok_MEASURED": True,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "primary_in_active_band_baseline_in_expected_oracle_ceiling_legitimate",
            "full_dispatch_pending_HYPOTHESIZED": True,
            "scope_observed": "smoke_N2048_3_seeds_6_arms_2160_events_per_arm",
            "scope_not_claimed": "full_N_scaling_OR_larger_NEX_KSCH_OR_chain_grade_tier",
            "brain_analog": "hippocampus_exemplars_plus_vmPFC_OFC_schema_prior",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- schema-context-prior MEASURED_MECHANISM informative-null (delta=0)
# ============================================================================

def build_atom3_schema_context_prior_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_cortex_schema_instantiation_context_prior_v1_MEASURED_MECHANISM_informative_null_"
            "CONTEXT_BOUND_PRIOR_0p731_EXEMPLAR_BAYES_K20_0p728_lift_0p003_HYBRID_0p730_lift_negative_"
            "0p001_baseline_0p256_random_0p119_oracle_0p809_substrate_cosine_kernel_already_encodes_"
            "schema_prior_information_MEASURED_substrate_already_does_X_pattern_emergent_AL"
        ),
        name=(
            "cortex_schema_instantiation_context_prior v1 MEASURED_MECHANISM informative-null: "
            "CONTEXT_BOUND_PRIOR=0.731 vs EXEMPLAR_BAYES_K20=0.728 lift=+0.003; HYBRID=0.730 (no "
            "additive bonus); finding: substrate cosine kernel already encodes schema-prior info"
        ),
        description=(
            "MEASURED_MECHANISM cortex schema context-prior informative-null (delta=0).\n"
            "HRR-bound context-prior arm (CONTEXT_BOUND_PRIOR) achieves recall 0.731, but this\n"
            "is essentially tied with the exemplar-Bayes K-nearest baseline at 0.728 (lift only\n"
            "+0.003) and the additive HYBRID arm shows no marginal bonus (-0.001 vs primary).\n"
            "Substantive finding: the substrate's cosine kernel already encodes the schema-prior\n"
            "structure that the explicit vmPFC-context-prior mechanism claims to add. Mechanism\n"
            "is REAL (CONTEXT_BOUND_PRIOR 0.731 vs random_prior 0.119 = +0.612 lift over random)\n"
            "but does NOT compose additively with exemplar-Bayes -- both arms recover overlapping\n"
            "schema information via different operations.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 7, 17, 23;\n"
            "6 arms = no_schema_baseline / random_prior / exemplar_Bayes_K20 / context_bound_prior\n"
            "/ hybrid_prior_plus_exemplar / oracle; per-arm per-seed verified):\n"
            "  Cardinality: 12960/12960 OK.\n"
            "  Per-arm recall:\n"
            "    ARM_NO_SCHEMA_BASELINE        {7: 0.226, 17: 0.283, 23: 0.258}  mean=0.256 cv=0.091\n"
            "    ARM_RANDOM_PRIOR              {7: 0.118, 17: 0.125, 23: 0.113}  mean=0.119 cv=0.043\n"
            "    ARM_EXEMPLAR_BAYES_K20        {7: 0.717, 17: 0.724, 23: 0.743}  mean=0.728 cv=0.015\n"
            "    ARM_CONTEXT_BOUND_PRIOR       {7: 0.714, 17: 0.729, 23: 0.749}  mean=0.731 cv=0.019 *PRIMARY*\n"
            "    ARM_HYBRID_PRIOR_PLUS_EXEMPLAR{7: 0.717, 17: 0.728, 23: 0.744}  mean=0.730 cv=0.016\n"
            "    ARM_ORACLE_TRUE_SCHEMA        {7: 0.808, 17: 0.800, 23: 0.819}  mean=0.809 cv=0.010\n"
            "  HP_prior threshold was 0.80 (primary at 0.731 BELOW HP); cell-author classified\n"
            "    MIDDLE_BAND. The MEASURED_MECHANISM finding here is the lift-over-exemplar\n"
            "    discriminator: lift = 0.731 - 0.728 = +0.003 (essentially zero); hybrid lift\n"
            "    over primary = -0.001 (no additive composition).\n\n"
            "SUBSTRATE-ALGEBRA INTERPRETATION (the load-bearing finding):\n"
            "  Both ARM_EXEMPLAR_BAYES (K-nearest cosine retrieval + Bayes update) and\n"
            "  ARM_CONTEXT_BOUND_PRIOR (HRR-bind context vectors as prior, FFT-unbind for\n"
            "  retrieval) end up exploiting the SAME substrate structure: codebook entries\n"
            "  cluster in cosine-space along schema-aligned axes. K-nearest retrieves cluster\n"
            "  members; HRR-bind retrieves cluster-mean via algebraic projection. Both achieve\n"
            "  the same ~0.73 ceiling because the substrate cosine kernel is already 'schema-\n"
            "  aware' by virtue of how codebook training/encoding shapes the geometry.\n\n"
            "  This is the 3rd occurrence today of the 'substrate-already-does-X' pattern\n"
            "  (per Director context). META_RULE_AL is being atomized as the discipline\n"
            "  finding (separate atom below).\n\n"
            "BOUND CLAIM (the MEASURED_MECHANISM):\n"
            "  CLAIM: 'Adding explicit HRR-bound context-prior atop cosine-similarity retrieval\n"
            "    does not yield additive lift when the substrate cosine kernel already encodes\n"
            "    the schema-discriminative geometry. Both arms recover ~0.73 recall; hybrid\n"
            "    composition yields no marginal benefit (lift -0.001).'\n"
            "  VERIFIED: per-arm means from per_arm_recall_summary; lift-over-exemplar and\n"
            "    hybrid-lift-over-primary arithmetic confirmed against metrics fields.\n"
            "  SCOPE INCLUDES: smoke at N=2048, 3 seeds, schema-instantiation task with cosine\n"
            "    similarity backbone.\n"
            "  SCOPE EXCLUDES: encoder variants that disrupt cosine schema-clustering (could\n"
            "    re-create lift for context-prior); larger schema spaces; sequential-prior\n"
            "    composition.\n\n"
            "REVIVAL DESIGN (cell-author scope):\n"
            "  v2 context-prior should test on an encoder that does NOT pre-encode schema-\n"
            "  alignment (e.g. random projection or untrained encoder) to demonstrate that\n"
            "  context-prior mechanism CAN add lift when the kernel does not already encode it.\n"
            "  Without that arm, this is informative-null on current substrate.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 12960/12960 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L4importsentinel+\n"
            "    CARDINALITY_OK+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+HRR_FFT_BIND\n"
            "  META_RULE_K discriminator: random_prior 0.119 vs primary 0.731 = +0.612 lift\n"
            "    over random (mechanism IS firing); primary vs exemplar +0.003 (no marginal\n"
            "    novel info -- informative null)\n"
            "  META_RULE_L band: primary 0.731 in [0.50, 0.80] active; not at floor or cap\n"
            "  META_RULE_AA fairness: oracle 0.809 ceiling; arms_differ_verified=True\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "cortex_schema_instantiation_context_prior_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_SCHEMA_CTX,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 2048,
            "primary_arm": "ARM_CONTEXT_BOUND_PRIOR",
            "primary_recall_MEASURED": 0.731,
            "primary_cv_MEASURED": 0.019,
            "exemplar_bayes_recall_MEASURED": 0.728,
            "hybrid_recall_MEASURED": 0.730,
            "baseline_recall_MEASURED": 0.256,
            "random_recall_MEASURED": 0.119,
            "oracle_recall_MEASURED": 0.809,
            "lift_over_exemplar_MEASURED": 0.003,
            "hybrid_lift_over_primary_MEASURED": -0.001,
            "informative_null_finding": "substrate_cosine_kernel_already_encodes_schema_prior",
            "third_occurrence_substrate_already_does_X_pattern": True,
            "linked_meta_rule": "META_RULE_AL_substrate_cosine_kernel_pre_encodes_schema_prior",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires_partial": True,
            "META_RULE_L_band_check": "primary_in_active_band_lift_over_exemplar_essentially_zero",
            "scope_observed": "smoke_N2048_3_seeds_cosine_substrate_backbone",
            "scope_not_claimed": "non_schema_aware_encoder_arm_OR_larger_schema_space",
            "brain_analog": "vmPFC_context_prior_overlapping_with_hippocampal_exemplar_retrieval",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 4 -- CF replay latency delta-stack v2 MEASURED_MECHANISM (delta=0)
# ============================================================================

def build_atom4_cf_v2_latency_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_counterfactual_replay_latency_delta_stack_v2_single_intervention_MEASURED_MECHANISM_"
            "smoke_BASELINE_setup_11p497ms_DELTA_SHORT_2p103ms_AMORTIZED_2p104ms_query_1p977ms_"
            "accuracy_1p000_speedup_5p47x_RANDOM_acc_0p000_arms_distinct_n_seeds_2_n_cycles_200_"
            "parent_auto_promote_REFUSED_methodology_v2_baseline_differs_from_v1_config"
        ),
        name=(
            "counterfactual_replay_latency_delta_stack v2 MEASURED_MECHANISM at smoke: "
            "BASELINE setup=11.497ms -> DELTA_SHORT setup=2.103ms query=1.977ms acc=1.000 "
            "(5.47x speedup); AMORTIZED setup=2.104ms acc=1.000; RANDOM acc=0.000; parent-promote REFUSED"
        ),
        description=(
            "MEASURED_MECHANISM CF replay latency delta-stack v2 single-intervention (delta=0).\n"
            "Delta-stack rewrite mechanism (stack=1 for short; stack=5 with filler-hoist for\n"
            "amortized) clears HP latency targets (setup < 4ms, query < 10ms) at smoke regime\n"
            "with accuracy preserved at 1.000. Discriminator: RANDOM_DELTAS arm at acc=0.000\n"
            "demonstrates the delta-application mechanism IS load-bearing. ORACLE direct-lookup\n"
            "at setup ~0.004ms / query ~0.001ms establishes lower bound.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 2 seeds: 1, 2;\n"
            "5 arms = BASELINE_FULL_REWRITE / DELTA_STACK_SHORT(stack=1) / DELTA_STACK_AMORTIZED\n"
            "(stack=5,hoisted) / DIRECT_LOOKUP_ORACLE / RANDOM_DELTAS; 200 cycles per seed-arm):\n"
            "  Cardinality: 2000/2000 OK (5 arms x 200 cycles x 2 seeds).\n"
            "  Per-arm seed means (setup_latency_ms_mean / query_latency_ms_mean / accuracy):\n"
            "    BASELINE_FULL_REWRITE       seed=1 11.335/2.286/1.000  seed=2 11.658/2.333/1.000\n"
            "                                 -> mean setup=11.497ms query=2.309ms acc=1.000\n"
            "    DELTA_STACK_SHORT (s=1)     seed=1  2.132/2.042/1.000  seed=2  2.074/1.912/1.000\n"
            "                                 -> mean setup=2.103ms query=1.977ms acc=1.000\n"
            "    DELTA_STACK_AMORTIZED (s=5) seed=1  2.015/1.919/1.000  seed=2  2.193/2.104/1.000\n"
            "                                 -> mean setup=2.104ms query=2.011ms acc=1.000\n"
            "    DIRECT_LOOKUP_ORACLE        seed=1  0.0042/0.0013/1.000 seed=2  0.0041/0.0013/1.000\n"
            "                                 -> mean setup=0.004ms query=0.001ms acc=1.000\n"
            "    RANDOM_DELTAS               seed=1  2.329/2.181/0.000  seed=2  2.261/2.098/0.000\n"
            "                                 -> mean setup=2.295ms query=2.139ms acc=0.000\n"
            "  Discriminator: RANDOM arm acc=0.000 vs DELTA_SHORT acc=1.000 demonstrates\n"
            "    delta-mechanism is load-bearing (not just stack-overhead reduction); ORACLE\n"
            "    establishes physical lower bound; arms_signature_sha256=f0f4fbbf01349819\n"
            "    confirms distinct arm code-paths.\n"
            "  HP clearance: setup 2.103ms < HYPOTHESIZED-target 4ms; query 1.977ms < 10ms;\n"
            "    speedup 11.497 / 2.103 = 5.467x (matches verdict_msg 5.47x).\n\n"
            "PARENT-PROMOTE REFUSED (METHODOLOGY GROUND; Skunkworks load-bearing decision):\n"
            "  Cell-author flag: 'AUTO-PROMOTES parent causal_counterfactual_replay_v1\n"
            "    MIDDLE_BAND -> chain-grade'.\n"
            "  ROOT CAUSE OF REFUSAL: parent v1 metric on disk (data/exp_causal_counterfactual_\n"
            "    replay_v1/metrics.json) is: 1 seed, accuracy=1.000, intervention_ms=16.864ms,\n"
            "    run_mode=smoke. MIDDLE_BAND reason: 1-seed AND 16.864ms > 10ms HP latency target.\n"
            "  v2 cell ran a DIFFERENT architecture (delta-stack rewrite vs parent's full do-\n"
            "    operator) with its OWN baseline arm (BASELINE_FULL_REWRITE at 11.497ms). The\n"
            "    11.497ms baseline is NOT a replication of parent v1's 16.864ms measurement\n"
            "    (different code path, different cycle structure, different cycle count).\n"
            "  Auto-promote would require: (a) re-running parent v1 EXACT config with 2+ seeds,\n"
            "    AND (b) demonstrating intervention_ms < 10ms at that config. v2 evidence cannot\n"
            "    retroactively satisfy parent v1's HP.\n"
            "  RULING: v2 is atomized as MEASURED_MECHANISM standalone (this atom). Parent v1\n"
            "    atom remains MIDDLE_BAND (SMOKE_ONLY provenance_quality unchanged). Cell-author\n"
            "    should dispatch a parent-redispatch cell with multi-seed and verify < 10ms\n"
            "    for legitimate parent-promote.\n\n"
            "SCOPE OF THE MEASURED_MECHANISM CLAIM:\n"
            "  CLAIM: 'Delta-stack rewrite mechanism (stack=1 or stack=5-with-filler-hoist)\n"
            "    achieves counterfactual replay setup latency 2.103ms +/- 0.04 with accuracy\n"
            "    preserved at 1.000 across 2 seeds x 200 cycles, vs full-rewrite baseline\n"
            "    11.497ms (5.47x speedup). RANDOM_DELTAS control at acc=0.000 confirms delta-\n"
            "    application mechanism is load-bearing.'\n"
            "  VERIFIED: per-seed setup/query/accuracy reproduce from per_arm_seed_rows;\n"
            "    aggregates match per-arm-mean computed across seeds; speedup arithmetic\n"
            "    11.497/2.103 = 5.467 matches.\n"
            "  SCOPE INCLUDES: smoke at N=2048, 2 seeds, 200 cycles per arm, 5 arms, single-\n"
            "    intervention regime.\n"
            "  SCOPE EXCLUDES: chain-grade tier (default for 2-seed smoke); parent v1 auto-\n"
            "    promote (refused on methodology); multi-intervention regime; deeper stacks.\n\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-default-conservatism):\n"
            "  Per Fix #28: 2-seed smoke is MEASURED_MECHANISM by default. Mechanism IS\n"
            "  proven via RANDOM-control discrimination; numbers are tight (cv < 0.10 on\n"
            "  setup means); discriminator fires. Chain-grade pathway clear pending full\n"
            "  multi-seed landing or a substantively-different evidence regime.\n\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Counterfactual replay = hippocampal SWR-replay of episode-with-modified-action;\n"
            "  delta-stack architecture parallels how the brain reuses unchanged-episode-state\n"
            "  while injecting the counterfactual delta at the intervention point (rather than\n"
            "  full rewrite of episode memory). Latency improvement reflects amortization of\n"
            "  unchanged-filler computation across multiple counterfactual queries.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 2000/2000 OK\n"
            "  META_RULE_K discriminator: RANDOM acc=0.000 vs DELTA_SHORT acc=1.000 fires\n"
            "    cleanly; ORACLE provides physical lower bound\n"
            "  META_RULE_L band: DELTA_SHORT setup 2.103ms in active range (BASELINE 11.497ms\n"
            "    above HP-target; DELTA below HP-target; ORACLE near zero); legitimate dynamic\n"
            "    range\n"
            "  META_RULE_AA fairness: ORACLE establishes ~0ms physical floor; DELTA legitimately\n"
            "    above ORACLE by 2x; not at-cap\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "counterfactual_replay_latency_delta_stack_v2_single_intervention",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_CF_V2,
            "parent_metrics_path_REFERENCED": METRICS_CF_V1_PARENT,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 2,
            "seeds": [1, 2],
            "N_DIM": 2048,
            "n_cycles": 200,
            "short_stack": 1,
            "amortized_stack": 5,
            "BASELINE_setup_ms_MEASURED": 11.497,
            "BASELINE_query_ms_MEASURED": 2.309,
            "BASELINE_accuracy_MEASURED": 1.000,
            "DELTA_SHORT_setup_ms_MEASURED": 2.103,
            "DELTA_SHORT_query_ms_MEASURED": 1.977,
            "DELTA_SHORT_accuracy_MEASURED": 1.000,
            "AMORTIZED_setup_ms_MEASURED": 2.104,
            "AMORTIZED_query_ms_MEASURED": 2.011,
            "AMORTIZED_accuracy_MEASURED": 1.000,
            "ORACLE_setup_ms_MEASURED": 0.004,
            "ORACLE_query_ms_MEASURED": 0.001,
            "RANDOM_accuracy_MEASURED": 0.000,
            "speedup_vs_baseline_MEASURED": 5.47,
            "hp_target_setup_ms_HYPOTHESIZED": 4.0,
            "hp_target_query_ms_HYPOTHESIZED": 10.0,
            "auto_promote_parent_REFUSED": True,
            "auto_promote_refuse_reason": "v2_baseline_arm_differs_from_parent_v1_config_no_replication_evidence",
            "parent_v1_intervention_ms_on_disk": 16.864,
            "parent_v1_n_seeds_on_disk": 1,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "delta_below_HP_target_baseline_above_oracle_near_physical_floor",
            "scope_observed": "smoke_N2048_2_seeds_200_cycles_5_arms_single_intervention",
            "scope_not_claimed": "chain_grade_OR_parent_v1_promote_OR_multi_intervention",
            "brain_analog": "hippocampal_SWR_replay_with_delta_injection_amortizing_unchanged_filler",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 5 -- sub-atom encoder v2 Mathlib HONEST_NEGATIVE (delta=0)
# ============================================================================

def build_atom5_sub_atom_mathlib_hn() -> Atom:
    return Atom(
        id=(
            "T3/EXP_sub_atom_token_stream_encoder_v2_real_mathlib_HONEST_NEGATIVE_mathlib_corpus_"
            "saturates_baseline_RF_d3_0p997_Trig_d3_0p793_gap_0p204_HP_gap_0p30_NOT_cleared_"
            "fairness_trig_ceiling_violation_baseline_above_0p50_cap_rf_alpha_cos_0p945_codebook_"
            "disambig_1p000_cv_0p004_n_seeds_5_full_run_encoder_primitive_works_corpus_specific_fail"
        ),
        name=(
            "sub_atom_token_stream_encoder v2 Mathlib HONEST_NEGATIVE for Mathlib-as-test-corpus: "
            "RF_d3=0.997 (mechanism works) vs Trig_d3=0.793 (baseline saturates fairness ceiling 0.50); "
            "gap=0.204 < HP_gap=0.30; encoder primitive substantively works -- corpus-specific failure"
        ),
        description=(
            "HONEST_NEGATIVE sub-atom token-stream encoder v2 on Mathlib corpus (delta=0).\n"
            "Math-codebook role-filler encoder (RF) achieves d=3 unbind recall 0.997 (mechanism\n"
            "works robustly across 5 seeds; cv=0.004), but the char-trigram baseline scores 0.793\n"
            "on this corpus -- well above the FAIRNESS_trig_ceiling=0.50 threshold. The HP_gap\n"
            "(RF over Trig) requirement of >=0.30 is not cleared (observed gap=0.204).\n\n"
            "This is HONEST_NEGATIVE for Mathlib-as-test-corpus (baseline is too strong on this\n"
            "corpus for discriminator to fire), NOT for the encoder primitive itself (RF encoder\n"
            "achieves 0.997 d=3 recall which is near-ceiling). Other corpora (lean / matsci /\n"
            "oeis) and prior cell evidence on the v1 encoder establish the primitive works.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 5 seeds: 7, 17, 23, 31, 41;\n"
            "5 arms = char_trigram_baseline / math_codebook_token / math_codebook_var_rename /\n"
            "math_codebook_role_filler / diag_bind_depth; per-arm per-seed verified):\n"
            "  Cardinality: 75/75 OK (5 arms x 3 corpora x 5 seeds = 75 implicit units).\n"
            "  Per-arm d=3 unbind recall:\n"
            "    char_trigram_baseline        mean=0.793 std=0.029 cv=0.037  (FAIRNESS VIOLATION:\n"
            "                                  exceeds trig_ceiling=0.50; baseline saturates)\n"
            "    math_codebook_token          mean=0.856 std=0.027 cv=0.032\n"
            "    math_codebook_var_rename     mean=0.845 std=0.030 cv=0.036\n"
            "    math_codebook_role_filler    mean=0.997 std=0.004 cv=0.004 *PRIMARY (mechanism works)*\n"
            "    diag_bind_depth              mean=1.000 std=0.000 cv=0.000\n"
            "  Discriminator: RF gap over Trig = 0.997 - 0.793 = 0.204 < HP_gap=0.30 (NOT cleared).\n"
            "  RF alpha-equiv cosine: 0.945 (HP_alpha_cos >= 0.95 NOT cleared by 0.005).\n"
            "  RF codebook_disambig: 1.000 (HP >= 0.95 CLEARED).\n"
            "  fairness_trig_ceiling_violation=True, fairness_rf_gap_ok=False (cell-flagged).\n\n"
            "WHY HONEST_NEGATIVE for MATHLIB CORPUS (not encoder primitive):\n"
            "  The char-trigram baseline at 0.793 on Mathlib is far stronger than expected\n"
            "  (designed-for ceiling was 0.50). Mathlib text contains heavy character-n-gram\n"
            "  regularity (LaTeX command tokens, identifier conventions, structural markup)\n"
            "  that gives char-trigrams disproportionate purchase. This means Mathlib is NOT\n"
            "  a discriminating test corpus for the math-codebook mechanism: baseline already\n"
            "  captures most of the signal that the math-codebook claims to add.\n\n"
            "  This is a CORPUS-CHOICE finding: encoder primitive itself is sound (RF d=3 at\n"
            "  0.997 confirms; bind-depth diagnostic confirms binding algebra works). The cell\n"
            "  HARD_FAIL is on corpus-discriminator-strength, not on mechanism viability.\n\n"
            "BOUND CLAIM (the HONEST_NEGATIVE):\n"
            "  CLAIM: 'Math-codebook role-filler encoder achieves d=3 unbind recall 0.997 +/- 0.004\n"
            "    at full run (N=8192, 5 seeds, 200 test queries) but cannot demonstrate discriminating\n"
            "    lift over char-trigram baseline ON MATHLIB CORPUS because Mathlib char-trigram\n"
            "    baseline saturates above fairness ceiling (0.793 > 0.50).'\n"
            "  VERIFIED: per-seed numbers from per_arm dicts; mean/std/cv from per_arm_summary;\n"
            "    fairness flags from metrics.json.\n"
            "  SCOPE INCLUDES: Mathlib-as-corpus discriminator failure at full N=8192, 5 seeds.\n"
            "  SCOPE EXCLUDES: Encoder primitive viability (proven by RF at 0.997 d=3; bind-depth\n"
            "    diag confirms binding works); other corpora (lean/matsci/oeis); encoder v1\n"
            "    primitive results.\n\n"
            "REVIVAL DESIGN (cell-author scope):\n"
            "  v3 sub-atom encoder Mathlib should: (i) use a stricter character-n-gram-NULL\n"
            "  baseline (random projection or hash-trick) instead of char-trigrams to avoid\n"
            "  the LaTeX-regularity confound; (ii) probe on a corpus where char-trigram baseline\n"
            "  is < 0.50 (e.g. raw arXiv abstracts with stop-word stripping); (iii) compare to\n"
            "  encoder v1 + v2 directly on the SAME corpus where v1 already established lift,\n"
            "  to isolate v2's marginal contribution.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 75/75 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L3outertry+L4importsentinel\n"
            "  META_RULE_K discriminator: RF mechanism fires cleanly (0.997 vs diag bind-depth\n"
            "    1.000 confirms binding works); RF-vs-Trig discriminator does NOT fire due to\n"
            "    baseline saturation -- this is the HONEST_NEGATIVE finding\n"
            "  META_RULE_L band: RF at 0.997 is by-construction-saturation (near codebook-disambig\n"
            "    ceiling); Trig at 0.793 above fairness-baseline-ceiling; both arms at cap on\n"
            "    Mathlib -- arm-level legitimate measurement but discriminator-level inconclusive\n"
            "  META_RULE_AA fairness: VIOLATED (trig_ceiling_violation=True; cell-flagged); this\n"
            "    atom records the fairness violation as the finding\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "sub_atom_token_stream_encoder_v2_real_mathlib",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_SUBATOM_MATHLIB,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 5,
            "seeds": [7, 17, 23, 31, 41],
            "N_DIM": 8192,
            "codebook_size": 2000,
            "n_test": 200,
            "corpora": ["lean", "matsci", "oeis"],
            "RF_d3_MEASURED": 0.997,
            "Trig_d3_MEASURED": 0.793,
            "Token_d3_MEASURED": 0.856,
            "VarRename_d3_MEASURED": 0.845,
            "rf_alpha_cos_MEASURED": 0.945,
            "rf_codebook_disambig_MEASURED": 1.000,
            "rf_cv_MEASURED": 0.004,
            "RF_minus_Trig_d3_gap_MEASURED": 0.204,
            "HP_gap_required": 0.30,
            "HP_gap_cleared": False,
            "fairness_trig_ceiling_violation_MEASURED": True,
            "fairness_rf_gap_ok_MEASURED": False,
            "fairness_trig_ceiling_threshold": 0.50,
            "honest_negative_scope": "Mathlib_corpus_as_discriminator_NOT_encoder_primitive",
            "encoder_primitive_works_evidence": "RF_d3_0p997_diag_bind_depth_1p000",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AA_fairness_violation": True,
            "META_RULE_L_band_check": "RF_at_codebook_ceiling_Trig_above_fairness_ceiling_both_saturate",
            "scope_observed": "full_N8192_5_seeds_3_corpora_Mathlib_baseline_saturates",
            "scope_not_claimed": "encoder_primitive_failure_OR_failure_on_non_Mathlib_corpora",
            "revival_design_hint": "use_stricter_char_ngram_NULL_baseline_OR_low_trigram_corpus",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 6 -- META_RULE_AL substrate-cosine-kernel-pre-encodes-schema (META corpus; delta=0)
# ============================================================================

def build_atom6_meta_rule_al_substrate_cosine_pre_encodes_schema() -> Atom:
    return Atom(
        id=(
            "META_RULE_AL_substrate_cosine_kernel_pre_encodes_schema_prior_information_"
            "explicit_schema_prior_mechanisms_yield_no_additive_lift_when_cosine_geometry_"
            "already_aligned_evidence_schema_context_prior_v1_lift_0p003_HYBRID_negative_"
            "0p001_substrate_already_does_X_pattern_third_occurrence_today_meta_discipline"
        ),
        name=(
            "META_RULE_AL substrate-cosine-kernel pre-encodes schema-prior information: explicit "
            "schema-prior mechanisms (context-bound priors, vmPFC-prior, etc.) yield no additive "
            "lift when substrate cosine geometry already encodes the schema-discriminative axes"
        ),
        description=(
            "META_RULE_AL substrate-cosine-kernel pre-encodes schema-prior (discipline atom; delta=0).\n"
            "When the substrate codebook is trained or encoded such that schema-aligned items\n"
            "cluster along cosine-discriminative axes, explicit schema-prior mechanisms (e.g.\n"
            "HRR-bound context priors, sequential-prior composition) recover the SAME information\n"
            "via a different operation and yield no additive lift when composed with the implicit\n"
            "kernel-encoded prior.\n\n"
            "EVIDENCE (chain-of-occurrence; 3rd today per Director batch context):\n"
            "  Occurrence 3 (cleanly atomized in this batch -- ATOM 3 above):\n"
            "    cortex_schema_instantiation_context_prior_v1 [smoke; verified off data]\n"
            "      ARM_CONTEXT_BOUND_PRIOR  recall=0.731\n"
            "      ARM_EXEMPLAR_BAYES_K20   recall=0.728\n"
            "      lift_over_exemplar       =+0.003 (essentially zero)\n"
            "      ARM_HYBRID_PRIOR_PLUS_EXEMPLAR recall=0.730\n"
            "      hybrid_lift_over_primary =-0.001 (no additive composition)\n"
            "      ARM_RANDOM_PRIOR         recall=0.119 (control: mechanism IS firing)\n"
            "    -> CONTEXT_BOUND_PRIOR mechanism is real (vs random) but recovers same info as\n"
            "       EXEMPLAR_BAYES via different operation; HYBRID adds nothing.\n"
            "  Occurrences 1 + 2 (Director-reported earlier today; not yet atomized at this batch\n"
            "    layer): substrate-cosine-already-discriminates findings in prior smoke results;\n"
            "    cell anchors pending future batch consolidation.\n\n"
            "RULE STATEMENT:\n"
            "  IF substrate codebook is trained/encoded such that schema-aligned items cluster\n"
            "     along cosine-discriminative axes (cosine kernel is 'schema-aware'),\n"
            "  AND a candidate mechanism M aims to add explicit schema-prior information,\n"
            "  THEN M will show high recall (because it exploits the same underlying signal)\n"
            "     BUT M will NOT yield additive lift over a cosine-similarity baseline\n"
            "     (because the baseline already captures what M tries to add).\n"
            "  CORRECTIVE: test M on an encoder/codebook where cosine kernel is NOT schema-aware\n"
            "     (random projection, untrained encoder, hash-trick) to demonstrate M's marginal\n"
            "     contribution; OR design discriminator that fires only when explicit-prior beats\n"
            "     cosine-baseline by mechanistic margin (not just absolute recall).\n\n"
            "WHEN TO INVOKE:\n"
            "  - Pre-reg vetting: any cell claiming 'explicit schema-prior mechanism adds X'\n"
            "    on a cosine-similarity substrate must include the non-schema-aware-kernel arm\n"
            "    OR explicitly mark the expected-lift as cosine-vs-explicit not random-vs-explicit.\n"
            "  - Cert-tier review: an 'explicit schema-prior' result that shows lift only over\n"
            "    random-prior (not over cosine-baseline) is MEASURED_MECHANISM at best, not\n"
            "    chain-grade evidence for the explicit-prior mechanism.\n\n"
            "RELATIONSHIP TO PRIOR META_RULES:\n"
            "  - Complements META_RULE_AG (substrate-too-robust-for-mechanism-at-default-regime):\n"
            "    that rule covers substrate being above-ceiling for the mechanism to add lift;\n"
            "    THIS rule covers substrate cosine-kernel pre-encoding the mechanism's signal.\n"
            "    Both are 'substrate-already-does-X' findings; AG is regime-driven, AL is\n"
            "    kernel-geometry-driven.\n"
            "  - Composes with experiment-bias master checklist Q (suspect 1.000 results) +\n"
            "    P (anisotropy-hurts-retrieval Mu-Viswanath): cosine kernel that encodes schema\n"
            "    creates anisotropic structure that downstream mechanisms exploit.\n\n"
            "DISCIPLINE STATUS: NEUTRAL meta-rule (no cert increment). Tracked for application\n"
            "in future schema-prior / explicit-prior cell pre-reg vetting.\n"
        ),
        kind=AtomKind.METHODOLOGY,
        tier=Tier.TIER_2_PRIMITIVE,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "DISCIPLINE_META",
            "cert_status": "measured_mechanism",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AL",
            "rule_name": "substrate_cosine_kernel_pre_encodes_schema_prior",
            "evidence_cell_anchors": [
                "cortex_schema_instantiation_context_prior_v1",
            ],
            "evidence_metrics_paths": [
                METRICS_SCHEMA_CTX,
            ],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "occurrence_in_today_batch_chain": 3,
            "context_bound_prior_recall_MEASURED": 0.731,
            "exemplar_bayes_recall_MEASURED": 0.728,
            "lift_over_exemplar_MEASURED": 0.003,
            "hybrid_lift_over_primary_MEASURED": -0.001,
            "random_prior_recall_MEASURED": 0.119,
            "related_meta_rules": ["META_RULE_AG"],
            "applies_to_pre_reg_vetting": True,
            "applies_to_cert_tier_review": True,
            "neutral_meta_no_cert_increment": True,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# A5 helpers + ledger row builders (use cert_ledger_writer)
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )


def _total_count(store):
    return sum(1 for _ in store.all_atoms())


def build_ledger_rows(now_ts: float):
    """Build the 6 ledger rows for this batch."""
    rows = []

    # Row 1 -- TOM MM
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_theory_of_mind_sally_anne_nested_hrr_v1_MEASURED_MECHANISM_smoke',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 0,
        'cv': 0.056,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_TOM,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_TOM_smoke_MM_pending_full_dispatch_chain_grade_pathway',
        'ts': now_ts,
    })

    # Row 2 -- Schema-exemplar Bayes MM
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_cortex_schema_exemplar_bayes_importance_sample_v1_MEASURED_MECHANISM_smoke',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 0,
        'cv': 0.015,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SCHEMA_EX,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_schema_exemplar_bayes_smoke_MM_pending_full_dispatch',
        'ts': now_ts + 0.001,
    })

    # Row 3 -- Schema context-prior MM (informative null)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_cortex_schema_instantiation_context_prior_v1_MEASURED_MECHANISM_informative_null',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'MIDDLE_BAND',
        'cert_increment_delta': 0,
        'cv': 0.019,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SCHEMA_CTX,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_schema_context_prior_informative_null_substrate_already_does_X_3rd_today',
        'ts': now_ts + 0.002,
    })

    # Row 4 -- CF v2 latency delta-stack MM (parent-promote refused)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_counterfactual_replay_latency_delta_stack_v2_single_intervention_MEASURED_MECHANISM_smoke',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_CF_V2,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_CF_v2_latency_delta_stack_MM_parent_v1_auto_promote_REFUSED_methodology',
        'ts': now_ts + 0.003,
    })

    # Row 5 -- Sub-atom encoder Mathlib HONEST_NEGATIVE
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_sub_atom_token_stream_encoder_v2_real_mathlib_HONEST_NEGATIVE_mathlib_corpus',
        'cert_status': 'honest_negative',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'MIDDLE_BAND',
        'cert_increment_delta': 0,
        'cv': 0.004,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SUBATOM_MATHLIB,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_sub_atom_Mathlib_HN_corpus_saturates_baseline_encoder_primitive_works',
        'ts': now_ts + 0.004,
    })

    # Row 6 -- META_RULE_AL discipline meta
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'meta::META_RULE_AL_substrate_cosine_kernel_pre_encodes_schema_prior_information',
        'cert_status': 'measured_mechanism',
        'cert_class': 'discipline_meta',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'META_RULE_NEUTRAL',
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SCHEMA_CTX,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch13_META_RULE_AL_substrate_cosine_kernel_pre_encodes_schema_3rd_today_first_atomized',
        'ts': now_ts + 0.005,
    })

    return rows


# ============================================================================
# Main: A5-gated apply
# ============================================================================

def main(apply: bool):
    print(f'=== atomize_skunkworks_5cell_stage3_batch13_2026-06-27 (apply={apply}) ===')
    store_root = STORE_ROOT
    print(f'Store root: {store_root.resolve()}')

    # PRE snapshot
    ps_pre = PartitionedStore(store_root)
    pre_cert = _cert_count(ps_pre)
    pre_total = _total_count(ps_pre)
    print(f'PRE: cert_n={pre_cert}  total_atoms={pre_total}')
    assert pre_cert == 626, f'PRE CERT mismatch: expected 626, got {pre_cert}'

    # Build atoms
    atoms = [
        build_atom1_tom_sally_anne_mm(),
        build_atom2_schema_exemplar_bayes_mm(),
        build_atom3_schema_context_prior_mm(),
        build_atom4_cf_v2_latency_mm(),
        build_atom5_sub_atom_mathlib_hn(),
        build_atom6_meta_rule_al_substrate_cosine_pre_encodes_schema(),
    ]
    print(f'Built {len(atoms)} atoms.')
    for i, a in enumerate(atoms, 1):
        print(f'  ATOM {i}: {a.corpus.name}::{a.id[:100]}{"..." if len(a.id) > 100 else ""}')

    if not apply:
        print()
        print('DRY RUN -- not applying. Re-run with --apply to commit.')
        print(f'Planned: +0 chain-grade (predicted CERT N: {pre_cert} -> {pre_cert})')
        print(f'         +4 measured_mechanism, +1 honest_negative, +1 discipline_meta')
        return 0

    # APPLY -- one atom at a time, A5 per-window
    now_ts = float(time.time())
    rows = build_ledger_rows(now_ts)
    assert len(rows) == len(atoms), f'rows ({len(rows)}) != atoms ({len(atoms)})'

    for i, (atom, row) in enumerate(zip(atoms, rows), 1):
        print()
        print(f'--- Window {i}/{len(atoms)} -- {atom.corpus.name}::{atom.id[:80]}... ---')

        # PRE per-window
        ps = PartitionedStore(store_root)
        win_pre_cert = _cert_count(ps)
        win_pre_total = _total_count(ps)
        print(f'  WIN PRE: cert_n={win_pre_cert}  total={win_pre_total}')

        # Write atom (auto-flushes per Store.add_atom -> _flush_atoms)
        ps.add_atom(atom)

        # POST per-window (re-load)
        ps_post = PartitionedStore(store_root)
        win_post_cert = _cert_count(ps_post)
        win_post_total = _total_count(ps_post)
        print(f'  WIN POST: cert_n={win_post_cert}  total={win_post_total}')

        # Round-trip pq check (must find atom by ID)
        found = None
        for a in ps_post.all_atoms():
            if a.id == atom.id:
                found = a
                break
        assert found is not None, f'Round-trip FAIL: atom {atom.id} not found after add+flush'
        assert (found.metadata or {}).get('cert_status') == (atom.metadata or {}).get('cert_status'), \
            'Round-trip FAIL: cert_status mismatch'
        print(f'  ROUND-TRIP OK: cert_status={(found.metadata or {}).get("cert_status")}')

        # Cert delta must match (all rows have delta=0)
        delta_expected = row['cert_increment_delta']
        delta_actual = win_post_cert - win_pre_cert
        assert delta_actual == delta_expected, (
            f'CERT delta mismatch: expected {delta_expected} got {delta_actual} '
            f'(pre={win_pre_cert} post={win_post_cert})'
        )

        # Append ledger row (cert_ledger_writer does its own A5 gate)
        ledger_hash = append_cert_ledger_row(
            row,
            expected_cert_n_pre=win_post_cert,   # ledger PRE = our POST (atom already added)
            expected_cert_n_post=win_post_cert + row['cert_increment_delta'],
        )
        print(f'  LEDGER: appended row hash={ledger_hash}')

    # Final POST snapshot
    print()
    ps_final = PartitionedStore(store_root)
    post_cert = _cert_count(ps_final)
    post_total = _total_count(ps_final)
    print(f'=== FINAL: cert_n={post_cert} (PRE {pre_cert}, delta {post_cert - pre_cert})  '
          f'total={post_total} (PRE {pre_total}, delta {post_total - pre_total}) ===')

    assert post_cert == pre_cert + 0, f'OVERALL CERT delta wrong: expected +0, got {post_cert - pre_cert}'
    assert post_total == pre_total + 6, f'OVERALL TOTAL delta wrong: expected +6, got {post_total - pre_total}'

    print()
    print('A5-GATED APPLY COMPLETE.')
    print(f'  CERT N: {pre_cert} -> {post_cert} (delta +0)')
    print(f'  TOTAL:  {pre_total} -> {post_total} (delta +6)')
    print(f'  Ledger rows appended: 6')
    return 0


if __name__ == '__main__':
    apply = '--apply' in sys.argv[1:]
    sys.exit(main(apply))
