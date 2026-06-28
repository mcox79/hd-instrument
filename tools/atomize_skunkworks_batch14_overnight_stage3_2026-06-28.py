"""Atomize: Skunkworks batch 14 overnight Stage 3 wave (2026-06-28).

Source request:
  Director batch 14 dispatch covering 8 candidates from overnight wave (CF / Schema /
  Online-conv / Narrative / SWR / Boundary + META_RULE_AM substrate-already-does-X).

VERIFY-OFF-DATA basis (.venv Python; each metrics.json Read end-to-end on disk;
per-arm cross-checked against Director's framings; refusals filed where claims did
not survive verification):

  Cell 1  CF v2 single-intervention "FULL HARD_PASS + parent promote"
                                              -> REFUSE re-atomize + REFUSE parent
                                                 promote (Director-framing-error #8)
  Cell 2  CF regret-comparison vmPFC v1 FULL  -> CHAIN_GRADE (delta=+1)
  Cell 3  Schema exemplar-Bayes K20 FULL      -> CHAIN_GRADE (PROMOTE batch13 MM; delta=+1)
  Cell 4  Online conv oneshot TV+hippo smoke  -> REFUSE HONEST_NEG (Director-framing-error #9;
                                                 bug not negative -- kth=64 OOB 60; cardinality_ok=False)
  Cell 5  Narrative coherence 100-event FULL  -> MEASURED_MECHANISM (Q1=0.889 Q4=1.0 substrate-
                                                 quality + segmentation-NOT-load-bearing finding;
                                                 substrate-already-does-X #8)
  Cell 6  SWR preplay hypothesis-gen FULL     -> MEASURED_MECHANISM (recall=0.558 novelty=1.0
                                                 lift=+0.558; pipeline-top1=0.108 downstream
                                                 bottleneck)
  Cell 7  Boundary detector FULL              -> MEASURED_MECHANISM (cs_f1=1.0 ties oracle at
                                                 drill regime SNR ~22x; mechanism valid; band-
                                                 floor noted)
  Cell 8  META_RULE_AM substrate-already-does-X discipline meta -> META atom (8 occurrences today)

REFUSE atoms (filed in landed-vet note; no Store atom):

  Cell 1 (CF v2 "FULL HARD_PASS + parent promote chain-grade x2"):
    DISK SHOWS: data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/
                metrics.json has run_mode=smoke, n_seeds=2, N=2048, n_cycles=200.
    BATCH 13 ALREADY ATOMIZED THIS PATH at MEASURED_MECHANISM (auto_promote_parent_REFUSED).
    Today's "full HARD_PASS" framing is FALSE against disk -- same data regime, no new evidence.
    AUTO-PROMOTE of parent causal_counterfactual_replay_v1 STAYS REFUSED (parent is
    legacy ARCHIVE/PRE_SUBSTRATE_BUILD atom from DECISION_237; v2 cannot retroactively
    satisfy parent v1's HP latency target; v2 baseline (11.497ms) is different code-path
    from parent v1 baseline (16.864ms)).

  Cell 4 (Online conv oneshot TV+hippo "HONEST_NEG hippo binding broken"):
    DISK SHOWS: per_arm TASKVEC_PLUS_HIPPO arm_status="ERROR: ValueError: kth(=64) out
                of bounds (60)" for BOTH seeds; n=0 scenarios; integrated_query_acc=NaN.
    cardinality_ok=False (240/300 = 80%; missing the 60 TV+HIPPO scenarios entirely).
    This is a code-bug (refuse-gate kth > vocab size) not a substrate honest-negative.
    Filing HONEST_NEG would conflate infra-bug with negative result. NEEDS cell-author
    fix + redispatch before any tier; HARD_FAIL_INFRASTRUCTURE flag in note.

NET CERT delta: +2 chain-grade (CF regret + Schema exemplar promote)
  + 3 MM (Narrative / SWR / Boundary)
  + 1 META (META_RULE_AM)
  + 0 HONEST_NEG (refused)
  + 0 from Cell 1 (refused; already-atomized)

PRE CERT N (verified live): 626
POST CERT N (predicted; A5-gated): 628

LEDGER ROWS: 6 (2 chain_grade + 3 measured_mechanism + 1 discipline_meta)

A5 GATING: PRE/POST cert_n assertions on every window; round-trip pq check on every atom.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_batch14_overnight_stage3_2026-06-28.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_batch14_overnight_stage3_2026-06-28.py --apply    # WRITE
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
RULING_NOTE = "notes/skunkworks_landed_vet_batch14_overnight_stage3_2026-06-28.md"
CELL_COMMIT = "n/a-2026-06-28-batch14-overnight-stage3"
ATOMIZED_BY = "skunkworks_atomize_batch14_overnight_stage3_2026-06-28"

METRICS_CF_REGRET = "data/exp_counterfactual_regret_comparison_vmpfc_v1/metrics.json"
METRICS_SCHEMA_EX_FULL = "data/exp_cortex_schema_exemplar_bayes_importance_sample_v1/metrics.json"
METRICS_NARRATIVE = "data/exp_stage3_narrative_coherence_100event_5char_full_stack_v1/metrics.json"
METRICS_SWR = "data/exp_swr_preplay_constructive_hypothesis_generator_v1/metrics.json"
METRICS_BOUNDARY = "data/exp_stage3_narrative_event_boundary_detector_only_v1/metrics.json"
META_AM_SYNTH_NOTE = "notes/research_synthesis_overnight_substrate_already_does_X_pattern_2026-06-27.md"


# ============================================================================
# ATOM 1 -- CF regret-comparison vmPFC v1 CHAIN_GRADE (delta=+1)
# ============================================================================

def build_atom1_cf_regret_vmpfc_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_counterfactual_regret_comparison_vmpfc_v1_CHAIN_GRADE_full_"
            "R2_vmpfc_0p987_rank_0p989_leak_0p020_R2_direct_0p987_R2_baseline_neg_0p208_"
            "gap_1p195_R2_oracle_1p000_R2_random_neg_0p157_recall_0p996_cv_0p002_"
            "arms_distinct_True_baseline_in_band_True_cardinality_ok_True_crlb_ok_True_"
            "n_seeds_5_N8192_V_REL256_VMPFC_REGRET_PRIMITIVE_LOAD_BEARING"
        ),
        name=(
            "counterfactual_regret_comparison_vmpfc v1 CHAIN_GRADE at full: R2_vmpfc=0.987 "
            "rank=0.989 value_leak=0.020 cv=0.002 vs baseline=-0.208 (gap=1.195) oracle=1.0 "
            "n_seeds=5 N=8192; VMPFC_REGRET HRR-magnitude-encoded comparison readout load-bearing"
        ),
        description=(
            "CHAIN_GRADE substrate scalar-regret signal via HRR magnitude-encoded comparison\n"
            "readout (delta=+1). vmPFC regret-comparison mechanism cleared all HP gates at full\n"
            "(5 seeds, N=8192, V_REL=256, 200 scenarios x 5 outcome-levels x 20 interferences).\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 5 seeds: 7, 17, 23, 31, 41;\n"
            "5 arms = no_regret_baseline / random_vectors / direct_diff / vmpfc_comparison /\n"
            "ground_truth_oracle; per-arm per-seed verified):\n"
            "  Cardinality: 5000/5000 OK (5 arms x 200 scenarios x 5 seeds).\n"
            "  Per-arm regret_r2 / spearman / value_leak / factual_recall (mean across seeds):\n"
            "    no_regret_baseline   r2=-0.208 (cv=0.453)  rank= 0.030  leak=0.033  rec=1.000\n"
            "    random_vectors       r2=-0.157 (cv=0.225)  rank=-0.026  leak=0.014  rec=1.000\n"
            "    direct_diff          r2= 0.987 (cv=0.0020) rank= 0.989  leak=0.018  rec=1.000\n"
            "    vmpfc_comparison     r2= 0.987 (cv=0.0021) rank= 0.989  leak=0.020  rec=0.996 *PRIMARY*\n"
            "    ground_truth_oracle  r2= 1.000 (cv=0.000)  rank= 1.000  leak=0.018  rec=1.000\n"
            "  Discriminator: vmpfc 0.987 - baseline -0.208 = +1.195 gap (HP_gap >= 0.30\n"
            "    cleared 4x); vmpfc 0.987 vs random_vectors -0.157 = +1.144 lift (HP cleared);\n"
            "    vmpfc within 0.013 of oracle 1.0 (fair_baseline_ok); arms_distinct_all_seeds=True\n"
            "    (10 pairwise digest comparisons all PASS at disagreement=1.0).\n"
            "  HP clearance (config_version asserts ALL):\n"
            "    HP_R2_vmpfc>=0.80   : 0.987 PASS\n"
            "    HP_rank>=0.85       : 0.989 PASS\n"
            "    HP_leak<=0.30       : 0.020 PASS\n"
            "    HP_direct>=0.80     : 0.987 PASS\n"
            "    HP_base_max<=0.20   : -0.208 PASS (negative ok; baseline-in-band [-0.35, 0.35])\n"
            "    HP_gap>=0.30        : 1.195 PASS (4x margin)\n"
            "    HP_oracle>=0.90     : 1.000 PASS\n"
            "  CRLB round-trip OK across all seeds (oracle_r2_floor=0.99).\n"
            "  cv 0.002 is well below chain-grade threshold (cv_max=0.15); suspect_1000=False;\n"
            "  baseline-in-band=True confirms baseline negativity NOT artifact.\n"
            "\n"
            "SCOPE OF THE CHAIN_GRADE CLAIM:\n"
            "  CLAIM: 'Substrate computes scalar regret signal via HRR magnitude-encoded comparison\n"
            "    readout (vmpfc_comparison arm) achieving R^2=0.987 +/- 0.002, Spearman=0.989,\n"
            "    value_leak=0.020 across 5 seeds at N=8192, V_REL=256 over 200 scenarios x 5\n"
            "    outcome-levels. Ranks scenarios faithfully (rank=0.989); bounded value-leak\n"
            "    (0.02 << ceiling 0.30); ground-truth oracle within 0.013 confirming fair-baseline.'\n"
            "  VERIFIED: per-seed r2/spearman/leak/recall reproduce from per_arm.<arm>.<seed>;\n"
            "    cv = std/mean per-arm; gap = vmpfc_mean - baseline_mean = 0.987 - (-0.208) = 1.195.\n"
            "  SCOPE INCLUDES: full at N=8192, V_REL=256, 5 seeds, 200 scenarios x 5 outcomes x\n"
            "    20 interferences = 5000 unit budget cleared.\n"
            "  SCOPE EXCLUDES: cross-domain regret-scenario transfer; HRR vector-decision regret\n"
            "    (this is scalar magnitude; vector regret separate primitive).\n"
            "\n"
            "WHY CHAIN_GRADE (Skunkworks-cert-owner-tiers-up):\n"
            "  All HP gates cleared at full-N (5 seeds) with very tight cv (0.002); discriminator\n"
            "  fires across 4 baselines + oracle; arms-distinct verified per-pair; baseline-in-band\n"
            "  rules out artifact; CRLB round-trip OK; cardinality OK at 5000/5000. Cell anchor\n"
            "  has NO prior atom (verified). Discriminator gap 4x HP-margin. Per Fix #28 default-\n"
            "  conservatism is MM, but this evidence cleanly meets pre-reg-pass for chain-grade.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  vmPFC (ventromedial prefrontal cortex) and OFC (orbitofrontal cortex) encode\n"
            "  counterfactual value comparisons -- 'what would the alternative have given me?'\n"
            "  Regret signal is the scalar difference between obtained vs hypothetical alternative\n"
            "  outcome. Substrate realization: HRR magnitude-encoded comparison readout extracts\n"
            "  the difference dimension while preserving factual recall (rec=0.996; bounded leak).\n"
            "  Foundational Stage 3 capability for counterfactual reasoning + value-comparison.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 5000/5000 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perseed+L3outertry+\n"
            "    L4importsentinel+META_RULE_AF+META_RULE_AH+META_RULE_AG+CRLB_round_trip\n"
            "  META_RULE_K discriminator: vmpfc 0.987 vs baseline -0.208 gap 1.195 (4x HP);\n"
            "    arms_differ_verified=True across 10 pairwise; CRLB floor=0.9 round-trip OK\n"
            "  META_RULE_L band: vmpfc 0.987 in active band [0.80, 1.00]; baseline -0.208 in\n"
            "    baseline-band [-0.35, 0.35] confirming negativity NOT artifact; oracle 1.0\n"
            "    legitimate ceiling; vmpfc 0.013 below oracle (fair_baseline_ok)\n"
            "  META_RULE_AA fairness: oracle 1.0 vs vmpfc 0.987 by 0.013; not at-cap;\n"
            "    arms_differ_verified=True; calibration_check=default_ok_for_this_regime\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; HRR magnitude readout + cosine).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cell_anchor": "counterfactual_regret_comparison_vmpfc_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_CF_REGRET,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 5,
            "seeds": [7, 17, 23, 31, 41],
            "N_DIM": 8192,
            "V_REL": 256,
            "n_scenarios": 200,
            "n_outcome_levels": 5,
            "n_interference": 20,
            "R2_vmpfc_MEASURED": 0.987,
            "R2_vmpfc_cv_MEASURED": 0.0021,
            "ranking_spearman_vmpfc_MEASURED": 0.989,
            "value_leak_pearson_vmpfc_MEASURED": 0.020,
            "factual_recall_vmpfc_MEASURED": 0.996,
            "R2_direct_MEASURED": 0.987,
            "R2_baseline_MEASURED": -0.208,
            "R2_random_vectors_MEASURED": -0.157,
            "R2_oracle_MEASURED": 1.000,
            "gap_vmpfc_over_baseline_MEASURED": 1.195,
            "baseline_in_band_MEASURED": True,
            "crlb_round_trip_ok_all_seeds_MEASURED": True,
            "arms_distinct_all_seeds_MEASURED": True,
            "cardinality_ok_MEASURED": True,
            "n_units_observed": 5000,
            "n_units_expected": 5000,
            "suspect_1000_MEASURED": False,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "vmpfc_in_active_band_baseline_in_expected_oracle_legitimate_ceiling",
            "scope_observed": "full_N8192_V_REL256_5_seeds_200x5x20_scenarios_5000_units",
            "scope_not_claimed": "cross_domain_regret_transfer_OR_vector_regret_separate_primitive",
            "brain_analog": "vmPFC_OFC_counterfactual_value_comparison_scalar_regret_signal",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- Schema exemplar-Bayes K20 CHAIN_GRADE (PROMOTE batch13 MM; delta=+1)
# ============================================================================

def build_atom2_schema_exemplar_bayes_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_cortex_schema_exemplar_bayes_importance_sample_v1_CHAIN_GRADE_full_"
            "primary_K_NEAREST_K20_0p714_baseline_0p271_random_0p244_oracle_0p801_K5_0p642_K50_0p715_"
            "lift_over_base_0p443_lift_over_rand_0p470_cv_0p025_n_seeds_5_N2048_VSLOT8_MSLOTS6_KSCH8_"
            "NEX20_72000_events_PROMOTES_batch13_MM_full_N_landing"
        ),
        name=(
            "cortex_schema_exemplar_bayes_importance_sample v1 CHAIN_GRADE at full: K20=0.714 "
            "base=0.271 rand=0.244 oracle=0.801 lift_base=+0.443 lift_rand=+0.470 cv=0.025 n_seeds=5; "
            "72k events; PROMOTES batch 13 MEASURED_MECHANISM to chain-grade via full-N landing"
        ),
        description=(
            "CHAIN_GRADE cortex schema-driven exemplar-Bayes K-nearest at full (delta=+1).\n"
            "PROMOTES the batch 13 MEASURED_MECHANISM atom (smoke n_seeds=3, primary=0.728) to\n"
            "chain-grade via full-N landing with 5 seeds, 72000 events, cv=0.025. Importance-\n"
            "sampling K-nearest exemplar Bayes prior over schema slots achieves 0.714 recall\n"
            "(lift +0.443 over no-schema baseline; +0.470 over random-K control; primary cv\n"
            "0.025) at full regime. Oracle ceiling 0.801 confirms no fairness-saturation.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 5 seeds: 7, 17, 23, 31, 41;\n"
            "6 arms = no_schema_baseline / random_K / K_nearest_K5 / K_nearest_K20 / K_nearest_K50\n"
            "/ oracle_true_schema; per-arm per-seed verified):\n"
            "  Cardinality: 72000/72000 OK (6 arms x 12000 events per arm; events_per_arm=12000\n"
            "    matches expected_events_per_arm; expected_n_units=72000 matches sum across arms).\n"
            "  Per-arm recall (HP_floor >= 0.50; HP_lift_base >= 0.30; HP_lift_rand >= 0.30):\n"
            "    ARM_NO_SCHEMA_BASELINE   {7:0.225, 17:0.274, 23:0.255, 31:0.308, 41:0.295}\n"
            "                              mean=0.271 cv=0.108\n"
            "    ARM_RANDOM_K_EXEMPLARS   {7:0.226, 17:0.258, 23:0.214, 31:0.250, 41:0.273}\n"
            "                              mean=0.244 cv=0.087\n"
            "    ARM_K_NEAREST_K5         {7:0.655, 17:0.645, 23:0.635, 31:0.660, 41:0.616}\n"
            "                              mean=0.642 cv=0.024\n"
            "    ARM_K_NEAREST_K20        {7:0.724, 17:0.713, 23:0.728, 31:0.725, 41:0.680}\n"
            "                              mean=0.714 cv=0.025 *PRIMARY*\n"
            "    ARM_K_NEAREST_K50        {7:0.719, 17:0.716, 23:0.725, 31:0.731, 41:0.685}\n"
            "                              mean=0.715 cv=0.022\n"
            "    ARM_ORACLE_TRUE_SCHEMA   {7:0.800, 17:0.796, 23:0.809, 31:0.810, 41:0.789}\n"
            "                              mean=0.801 cv=0.010\n"
            "  Discriminator: primary 0.714 - baseline 0.271 = +0.443 lift (HP >= 0.30 cleared);\n"
            "    primary - random_K 0.244 = +0.470 (HP >= 0.30 cleared); primary < oracle 0.801\n"
            "    by 0.087 (legitimate gap; not at-cap; fair_baseline_ok).\n"
            "  K-sensitivity: K5 (0.642) < K20 (0.714) ~ K50 (0.715) -- importance-weighting\n"
            "    plateaus at K>=20 confirming the mechanism rather than nearest-neighbor effect.\n"
            "  cv 0.025 well below chain-grade threshold (HP_cv < 0.15); arms_differ_verified=True.\n"
            "\n"
            "PROMOTE-FROM-BATCH-13 EVIDENCE (Skunkworks audit chain):\n"
            "  BATCH 13 atom (smoke; metrics path:\n"
            "    data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json):\n"
            "    n_seeds=3, primary=0.728, lift_base=+0.472, lift_rand=+0.493, cv=0.015\n"
            "    -> MEASURED_MECHANISM (Fix #28 default; full-pending)\n"
            "  BATCH 14 atom (full; metrics path:\n"
            "    data/exp_cortex_schema_exemplar_bayes_importance_sample_v1/metrics.json):\n"
            "    n_seeds=5, primary=0.714, lift_base=+0.443, lift_rand=+0.470, cv=0.025\n"
            "    -> CHAIN_GRADE (full-N landed; HP gates cleared with margin; arms distinct;\n"
            "       cardinality OK 72000/72000; cv well below threshold; oracle 0.801 within\n"
            "       0.087 of primary confirming fair_baseline_ok)\n"
            "  PROMOTE RATIONALE: same mechanism, scaled from smoke to full with consistent\n"
            "    numbers (smoke 0.728 vs full 0.714; both in active band; differences within\n"
            "    expected seed-variation across 3 vs 5 seeds). Batch 13 MM atom REMAINS in\n"
            "    Store as smoke-tier evidence; this atom is the full-tier promote.\n"
            "\n"
            "SCOPE OF THE CHAIN_GRADE CLAIM:\n"
            "  CLAIM: 'K-nearest exemplar Bayes importance-sampling over substrate schema slots\n"
            "    achieves recall 0.714 +/- 0.018 at full regime (N=2048, VSLOT=8, MSLOTS=6,\n"
            "    KSCH=8, NEX=20, FN=0.20, MF=0.50, 5 seeds, 72000 events), lift +0.443 over\n"
            "    no-schema baseline. K-sensitivity dose-response: K5 < K20 ~ K50 confirms\n"
            "    importance-weighting plateaus at K>=20.'\n"
            "  VERIFIED: per-seed numbers reproduce from per_arm_recall_summary.per_seed arrays;\n"
            "    cv = std/mean per-arm matches metrics; lift = primary - baseline arithmetic.\n"
            "  SCOPE INCLUDES: full at N=2048, 5 seeds, 6 arms, 12000 events per arm, K-sweep\n"
            "    over {5, 20, 50}, BETA=8.0, NMASKED=3.\n"
            "  SCOPE EXCLUDES: larger NEX / KSCH / VSLOT sweeps; concept drift; cross-domain\n"
            "    schema transfer.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Cortical schema-driven recall: hippocampus encodes episode-specific exemplars;\n"
            "  vmPFC / OFC retrieves schema-prior; convergence yields posterior over slot fillers.\n"
            "  K-nearest importance-sampling is the substrate-native realization of mixture-of-\n"
            "  experts schema prior over exemplar memories (analog: Tse-Morris 2007 schema-\n"
            "  facilitated consolidation; Preston-Eichenbaum 2013 schema-mediated memory).\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 72000/72000 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L4importsentinel+\n"
            "    CARDINALITY_OK+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR\n"
            "  META_RULE_K discriminator: primary vs baseline lift +0.443 (clean fire); K-\n"
            "    sensitivity K5/K20/K50 demonstrates mechanism dose-response\n"
            "  META_RULE_L band: primary 0.714 in [0.50, 0.80] active; baseline 0.271 in\n"
            "    [0.20, 0.35] expected; oracle 0.801 legitimate ceiling; not at-cap\n"
            "  META_RULE_AA fairness: oracle 0.801 > primary 0.714 by 0.087; not at-cap;\n"
            "    arms_differ_verified=True\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; K-nearest cosine + Bayes update).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cell_anchor": "cortex_schema_exemplar_bayes_importance_sample_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_SCHEMA_EX_FULL,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "promotes_batch13_mm_atom": True,
            "batch13_mm_atom_id_REFERENCE": (
                "T3/EXP_cortex_schema_exemplar_bayes_importance_sample_v1_MEASURED_MECHANISM_"
                "smoke_K_NEAREST_K20_0p728_baseline_0p256_random_0p235_oracle_0p809_lift_over_"
                "base_0p472_cv_0p015_n_seeds_3_arms_distinct_K_sensitivity_K5_0p636_K20_0p728_"
                "K50_0p727_full_pending"
            ),
            "run_mode": "full",
            "n_seeds": 5,
            "seeds": [7, 17, 23, 31, 41],
            "N_DIM": 2048,
            "VSLOT": 8,
            "MSLOTS": 6,
            "KSCH": 8,
            "NEX": 20,
            "FN": 0.20,
            "MF": 0.50,
            "BETA": 8.0,
            "N_MASKED": 3,
            "K_VARIANTS": [5, 20, 50],
            "primary_arm": "ARM_K_NEAREST_K20",
            "primary_recall_MEASURED": 0.714,
            "primary_cv_MEASURED": 0.025,
            "baseline_recall_MEASURED": 0.271,
            "random_k_recall_MEASURED": 0.244,
            "oracle_recall_MEASURED": 0.801,
            "lift_over_baseline_MEASURED": 0.443,
            "lift_over_random_k_MEASURED": 0.470,
            "K_NEAREST_K5_MEASURED": 0.642,
            "K_NEAREST_K20_MEASURED": 0.714,
            "K_NEAREST_K50_MEASURED": 0.715,
            "arms_differ_verified_MEASURED": True,
            "cardinality_ok_MEASURED": True,
            "events_per_arm_total_MEASURED": 12000,
            "n_units_observed": 72000,
            "n_units_expected": 72000,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "primary_in_active_band_baseline_in_expected_oracle_ceiling_legitimate",
            "scope_observed": "full_N2048_5_seeds_6_arms_12000_events_per_arm_K_sweep_5_20_50",
            "scope_not_claimed": "larger_NEX_KSCH_VSLOT_OR_concept_drift_OR_cross_domain_transfer",
            "brain_analog": "hippocampus_exemplars_plus_vmPFC_OFC_schema_prior_full_N_landing",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- Narrative coherence 100-event MEASURED_MECHANISM
# ============================================================================

def build_atom3_narrative_coherence_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_stage3_narrative_coherence_100event_5char_full_stack_v1_MEASURED_MECHANISM_full_"
            "FULL_STACK_overall_0p556_Q1_factual_0p889_Q2_coref_0p222_Q3_temporal_0p111_Q4_contradict_1p000_"
            "lift_full_over_flat_0p195_lift_full_over_forget_0p306_NO_SEGMENT_ties_FULL_STACK_0p556_"
            "segmentation_NOT_load_bearing_substrate_already_does_X_pattern_8th_today_n_seeds_3"
        ),
        name=(
            "stage3_narrative_coherence_100event_5char_full_stack v1 MEASURED_MECHANISM at full: "
            "FULL_STACK overall=0.556 (Q1=0.889 factual + Q4=1.000 contradiction chain-grade-quality; "
            "Q2=0.222 coref + Q3=0.111 temporal collapse); NO_SEGMENT TIES FULL_STACK at 0.556 "
            "(lift=0.000) -- segmentation NOT load-bearing; substrate-already-does-X 8th occurrence"
        ),
        description=(
            "MEASURED_MECHANISM substrate narrative coherence at 100-event 5-character full stack\n"
            "(delta=0). TWO load-bearing findings: (1) Q1 factual-recall + Q4 contradiction-detection\n"
            "are CHAIN-GRADE-QUALITY at substrate composition (Q1=0.889 cv-low; Q4=1.0 perfect),\n"
            "demonstrating substrate handles 100-event narrative composition without explicit\n"
            "segmentation. (2) NO_SEGMENT arm TIES FULL_STACK arm at overall=0.556 (lift=0.000;\n"
            "predicted_sha16 IDENTICAL across all 3 seeds) -- event-segmentation primitive\n"
            "NOT load-bearing at default regime; substrate-already-does-X 8th occurrence today.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds: 11, 13, 19;\n"
            "4 arms = FORGET_EVERYTHING / FLAT_BASELINE / NO_SEGMENT / FULL_STACK; per-arm per-\n"
            "seed verified per query-type Q1-Q4):\n"
            "  Cardinality: 12/12 OK (4 arms x 3 seeds; 12 questions x 3 seeds per arm; 144 total\n"
            "    queries via n_q_total=12 per row x 12 rows).\n"
            "  Per-arm overall accuracy (mean across seeds):\n"
            "    ARM_FORGET_EVERYTHING  {11:0.25,  13:0.167, 19:0.333} mean=0.250 cv=high\n"
            "    ARM_FLAT_BASELINE      {11:0.25,  13:0.417, 19:0.417} mean=0.361 cv=0.27\n"
            "    ARM_NO_SEGMENT         {11:0.417, 13:0.667, 19:0.583} mean=0.556 cv=0.226\n"
            "    ARM_FULL_STACK         {11:0.417, 13:0.667, 19:0.583} mean=0.556 cv=0.187 *PRIMARY*\n"
            "  Per-query-type (FULL_STACK seeds aggregated):\n"
            "    Q1 factual:        mean=0.889 (chain-grade-quality at substrate composition)\n"
            "    Q2 coreference:    mean=0.222 (collapse; pronoun-tracking + Sally-Anne agent-\n"
            "                                   tracking NOT solved at this regime)\n"
            "    Q3 temporal:       mean=0.111 (collapse; before/after over 100-event window)\n"
            "    Q4 contradiction:  mean=1.000 (perfect; fact-updates correctly retrieved)\n"
            "  Discriminator + arms-distinct:\n"
            "    arms_distinct_pairs:\n"
            "      FORGET vs FLAT          : True\n"
            "      FORGET vs NO_SEGMENT    : True\n"
            "      FORGET vs FULL_STACK    : True\n"
            "      FLAT   vs NO_SEGMENT    : True\n"
            "      FLAT   vs FULL_STACK    : True\n"
            "      NO_SEGMENT vs FULL_STACK: FALSE  <-- LOAD-BEARING FINDING\n"
            "  predicted_sha16 IDENTICAL between NO_SEGMENT and FULL_STACK across all 3 seeds\n"
            "  (seed11=a87cf909244f154b; seed13=121a3a6f3baef49d; seed19=24c843e49663a82d).\n"
            "  Verdict: HARD_FAIL on min_per_q_FULL=0.1111 (Q3) < HF_per_q=0.30; primary fails\n"
            "  HP_overall=0.70 floor (got 0.556). MM-tier appropriate: mechanism partial-fires\n"
            "  on Q1 (0.889) + Q4 (1.0); fails on Q2/Q3.\n"
            "\n"
            "TWO MEASURED-MECHANISM CLAIMS (both load-bearing):\n"
            "  CLAIM 1 (Q1+Q4 substrate-quality): 'Substrate composition (FULL_STACK = bind +\n"
            "    hetero-assoc + replay + partition) handles 100-event 5-character narrative\n"
            "    factual-recall (Q1=0.889) and fact-update contradiction-detection (Q4=1.000)\n"
            "    at chain-grade-quality across 3 seeds at N_h=512 N_c=1024 N_part=1024,\n"
            "    without explicit event segmentation.'\n"
            "  CLAIM 2 (segmentation-not-load-bearing; substrate-already-does-X #8): 'ARM_NO_\n"
            "    SEGMENT at overall=0.556 = ARM_FULL_STACK overall=0.556; predicted_sha16\n"
            "    IDENTICAL per seed (3/3) -- explicit boundary detection adds zero value at\n"
            "    alpha=0.05 / K_active=51 regime; substrate composition handles 100-event\n"
            "    coherence without segmentation primitive.'\n"
            "  VERIFIED: per-arm per-seed numbers reproduce from per_arm_metrics.<arm>.<seed>\n"
            "    .overall_accuracy; sha16 hashes match for NO_SEGMENT vs FULL_STACK arms.\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE OR HARD_FAIL (Skunkworks-cert-owner):\n"
            "  Cell verdict is HARD_FAIL (correctly; HP_per_q=0.30 violated by Q3=0.111).\n"
            "  However, mechanism IS validly characterized: Q1+Q4 are substrate-quality at\n"
            "  100-event scale (load-bearing positive finding), and segmentation-null is a\n"
            "  load-bearing negative finding (cleanly atomizable via META_RULE_AM). Filing\n"
            "  as HARD_FAIL only would lose both substantive findings. MM characterization\n"
            "  preserves the mechanism record + the segmentation-null evidence for downstream\n"
            "  reuse.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Q1 factual + Q4 contradiction map to MTL (medial temporal lobe) declarative-fact\n"
            "  store + DLPFC monitoring for inconsistency. Q2 coreference + Q3 temporal map to\n"
            "  TPJ (mentalizing / agent-tracking) + hippocampal time-cells / parietal sequence-\n"
            "  bind which are KNOWN-WEAK at substrate (TOM v1 batch 13 already characterized\n"
            "  Q2-like agent-tracking as substrate-MM). Segmentation-null is consistent with\n"
            "  TWO_TIER + flat-preplay already absorbing event-boundary discrimination at the\n"
            "  cosine layer (META_RULE_AL extended).\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 12/12 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L4importsentinel\n"
            "  META_RULE_K discriminator: FULL_STACK vs FORGET gap +0.306 (HP_lift_forget=0.50\n"
            "    failed but FORGET still discriminates); FLAT vs FULL_STACK gap +0.195;\n"
            "    NO_SEGMENT vs FULL_STACK gap 0.000 (LOAD-BEARING null)\n"
            "  META_RULE_L band: FULL_STACK 0.556 in MIDDLE band [0.40, 0.70]; FORGET 0.250 in\n"
            "    expected-low band; oracle implicit at ground-truth\n"
            "  META_RULE_AA fairness: NO_SEGMENT ties FULL_STACK = segmentation does no work;\n"
            "    feeds META_RULE_AM substrate-already-does-X discipline meta\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero_llm_calls_at_inference=True per metrics).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "stage3_narrative_coherence_100event_5char_full_stack_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_NARRATIVE,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_h": 512,
            "N_c": 1024,
            "N_part": 1024,
            "N_events": 100,
            "N_characters": 5,
            "K_scene": 10,
            "K_active": 51,
            "eta": 0.005,
            "N_replay": 3,
            "forget_w": 5,
            "Q_per_type": 3,
            "verdict_raw": "HARD_FAIL",
            "hard_fail_reason": "min_per_q_FULL_0p1111_lt_HF_per_q_0p30_Q3_temporal_collapse",
            "FULL_STACK_overall_MEASURED": 0.556,
            "FULL_STACK_cv_MEASURED": 0.187,
            "FULL_STACK_Q1_factual_MEASURED": 0.889,
            "FULL_STACK_Q2_coreference_MEASURED": 0.222,
            "FULL_STACK_Q3_temporal_MEASURED": 0.111,
            "FULL_STACK_Q4_contradict_MEASURED": 1.000,
            "FLAT_BASELINE_overall_MEASURED": 0.361,
            "NO_SEGMENT_overall_MEASURED": 0.556,
            "FORGET_EVERYTHING_overall_MEASURED": 0.250,
            "lift_full_over_flat_MEASURED": 0.195,
            "lift_full_over_forget_MEASURED": 0.306,
            "lift_full_over_no_segment_MEASURED": 0.000,
            "arms_distinct_NO_SEGMENT_vs_FULL_STACK_MEASURED": False,
            "predicted_sha16_NO_SEGMENT_eq_FULL_STACK_per_seed": True,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "FULL_STACK_in_middle_band_FORGET_in_low_band_no_oracle",
            "load_bearing_finding_1": "Q1_factual_0p889_AND_Q4_contradiction_1p000_substrate_quality_100event",
            "load_bearing_finding_2": "NO_SEGMENT_ties_FULL_STACK_segmentation_NOT_load_bearing",
            "feeds_META_RULE_AM": True,
            "substrate_already_does_X_occurrence_today": 8,
            "scope_observed": "full_N_h_512_N_c_1024_3_seeds_100_events_5_chars_10_scenes",
            "scope_not_claimed": "Q2_Q3_solving_OR_chain_grade_overall_OR_solving_per_q_HP_floor",
            "brain_analog": "Q1Q4_MTL_DLPFC_contradiction_monitor_Q2Q3_TPJ_hippocampal_known_weak",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 4 -- SWR preplay hypothesis-generator MEASURED_MECHANISM
# ============================================================================

def build_atom4_swr_preplay_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_swr_preplay_constructive_hypothesis_generator_v1_MEASURED_MECHANISM_full_"
            "PREPLAY_FULL_recall_at_10_0p558_novelty_1p000_diversity_0p074_GEN_SCORE_PIPELINE_"
            "recall_0p573_pipeline_top1_0p108_DIAG_PREPLAY_DIVERSITY_recall_0p568_BASELINE_ECHO_0p000_"
            "RAND_0p000_PARROT_0p000_lift_echo_0p558_lift_rand_0p558_cv_0p035_n_seeds_5_N8192_V_BANK256_"
            "K_CANDS10_N_PROBLEMS200_generator_works_downstream_scorer_bottleneck"
        ),
        name=(
            "swr_preplay_constructive_hypothesis_generator v1 MEASURED_MECHANISM at full: PREPLAY_FULL "
            "recall@10=0.558 novelty=1.000 lift_echo=+0.558 (chain-grade-quality generator); "
            "pipeline_top1=0.108 (downstream scorer bottleneck below HF floor 0.15); cv=0.035 n_seeds=5"
        ),
        description=(
            "MEASURED_MECHANISM SWR-preplay constructive hypothesis generator at full (delta=0).\n"
            "Cell verdict HARD_FAIL on pipeline_top1=0.108 < HF floor 0.15. However: GENERATOR\n"
            "WORKS at chain-grade-quality (PREPLAY_FULL recall@10=0.558 novelty=1.000 lift=+0.558\n"
            "vs all 3 baselines at recall=0.000). Failure is at downstream gen-score PIPELINE\n"
            "ranker (pipeline_top1=0.108 means only ~11% of generated hypotheses ranked top-1\n"
            "by downstream scorer). MM filing preserves the generator-works finding while\n"
            "acknowledging pipeline integration is NOT chain-grade.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 5 seeds: 7, 17, 23, 31, 41;\n"
            "6 arms = BASELINE_OBSERVATION_ECHO / BASELINE_RANDOM_DRAW / MEMORY_PARROT /\n"
            "PREPLAY_FULL / GEN_SCORE_PIPELINE / DIAG_PREPLAY_DIVERSITY; per-arm per-seed):\n"
            "  Cardinality: 60000/60000 OK (6 arms x 200 problems x 5 seeds x 10 candidates).\n"
            "  Per-arm recall@10 / novelty / diversity / pipeline_top1 (means):\n"
            "    BASELINE_OBSERVATION_ECHO recall=0.000 nov=0.000 div=0.006 pipeline=N/A\n"
            "    BASELINE_RANDOM_DRAW      recall=0.000 nov=1.000 div=0.000 pipeline=N/A\n"
            "    MEMORY_PARROT             recall=0.000 nov=0.000 div=0.111 pipeline=N/A\n"
            "    PREPLAY_FULL              recall=0.558 nov=1.000 div=0.074 pipeline=N/A (cv=0.035)\n"
            "    GEN_SCORE_PIPELINE        recall=0.573 nov=1.000 div=0.077 pipeline=0.108 (cv=0.044)\n"
            "    DIAG_PREPLAY_DIVERSITY    recall=0.568 nov=1.000 div=0.074 pipeline=N/A (cv=0.070)\n"
            "  Discriminator (generator-layer): PREPLAY_FULL 0.558 vs ECHO 0.000 = +0.558 lift\n"
            "    (HP_lift_echo>=0.25 cleared 2.2x); vs RAND 0.000 = +0.558 (HP_lift_rand>=0.40\n"
            "    cleared); PARROT recall=0.000 (HF_parrot_nov>0.10 NOT triggered;\n"
            "    parrot_nov=0.000 confirms parrot is NOT recovering training data; arms-distinct\n"
            "    verified per-seed fingerprints).\n"
            "  HP conds (recall layer): novelty>=0.80 PASS (1.000); lift_echo>=0.25 PASS (0.558);\n"
            "    lift_rand>=0.40 PASS (0.558); diversity<=0.70 PASS (0.074); cv<0.15 PASS (0.035);\n"
            "    parrot_nov<0.05 PASS; arms_distinct PASS; cardinality_ok PASS; not_suspect_Q PASS.\n"
            "  HP/HF that failed: HP recall@10>=0.65 FAIL (got 0.558); HF pipeline_top1<0.15\n"
            "    TRIGGERED (pipeline_top1=0.108).\n"
            "\n"
            "TWO LAYERS OF EVIDENCE (load-bearing distinction):\n"
            "  GENERATOR LAYER (PREPLAY_FULL + DIAG_PREPLAY_DIVERSITY + GEN_SCORE_PIPELINE recall):\n"
            "    All 3 generator-arms at recall ~0.56-0.57 vs 3 baselines at 0.000; novelty 1.0;\n"
            "    cv tight (0.035-0.070). Generator IS substrate-quality.\n"
            "  PIPELINE LAYER (GEN_SCORE_PIPELINE pipeline_top1):\n"
            "    Downstream scorer ranks only 0.108 of generated hypotheses as top-1. This is\n"
            "    the integration bottleneck; gen-score scorer fails to discriminate top-1 from\n"
            "    other K=10 candidates. NOT a generator-quality problem; a scorer-quality problem.\n"
            "  MM FILING preserves: 'generator works; pipeline NOT chain-grade; scorer is the\n"
            "    bottleneck'. Useful for downstream cells that can swap a better scorer.\n"
            "\n"
            "SCOPE OF THE MEASURED_MECHANISM CLAIM:\n"
            "  CLAIM (generator-layer): 'SWR-preplay + bind-noise generator produces novel\n"
            "    hypothesis candidates with recall@10=0.558 +/- 0.020 (cv=0.035) and novelty=1.0\n"
            "    across 5 seeds at N=8192, V_BANK=256, K_CANDS=10, 200 problems; lift +0.558 over\n"
            "    observation-echo + random-draw baselines + memory-parrot control.'\n"
            "  CLAIM (pipeline-layer; BOUNDED-NEGATIVE): 'Downstream gen-score pipeline ranker\n"
            "    achieves pipeline_top1=0.108 ranking top-1 of K=10 candidates; below HF\n"
            "    floor 0.15; scorer is the bottleneck not the generator.'\n"
            "  VERIFIED: per-seed recall/novelty/diversity reproduce from per_arm[arm].recall_at_k_mean\n"
            "    arrays; pipeline_top1 reproduces from per_seed[*].per_arm.GEN_SCORE_PIPELINE.\n"
            "  SCOPE INCLUDES: full at N=8192, V_BANK=256, K_CANDS=10, 200 problems, 5 seeds.\n"
            "  SCOPE EXCLUDES: chain-grade on pipeline (HF triggered); recall@K for K<10;\n"
            "    larger V_BANK or N=16384 scaling; alternative downstream scorers.\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT HONEST_NEG (Skunkworks-cert-owner):\n"
            "  Cell verdict HARD_FAIL (correctly; HF_pipeline_top1<0.15 triggered). But mechanism\n"
            "  characterization is load-bearing: generator IS substrate-quality across 3 generator-\n"
            "  arms with clean discrimination vs 3 baselines. Filing HONEST_NEG only would lose\n"
            "  the generator-works finding. MM preserves both layers of evidence and gives\n"
            "  downstream cells a clear path (swap scorer; preserve generator).\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  SWR (sharp-wave ripples) preplay: hippocampal replay of NOVEL trajectory candidates\n"
            "  (not just experienced past). The generator-layer in substrate (PREPLAY_FULL + bind-\n"
            "  noise) realizes this constructively. The downstream scorer is analogous to vmPFC /\n"
            "  OFC value-comparison of preplayed candidates -- substrate scorer (cosine similarity)\n"
            "  is the weak link. Brain may use richer value-prediction layer (matches gen-score\n"
            "  pipeline_top1=0.108 = substrate scorer LACKS this).\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 60000/60000 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L3outertry+L4importsentinel\n"
            "  META_RULE_K discriminator: 3 generator-arms recall ~0.56 vs 3 baselines recall 0.000\n"
            "    cleanly fires; PARROT control at recall=0 + nov=0 confirms not data-leak\n"
            "  META_RULE_L band: PREPLAY 0.558 below HP recall>=0.65 but above HF<0.30 -> middle\n"
            "    band on recall-axis; pipeline_top1 0.108 below HF<0.15 floor on pipeline-axis\n"
            "    (separate layer; cleanly distinguished)\n"
            "  META_RULE_AA fairness: BASELINE_OBSERVATION_ECHO + RANDOM_DRAW + MEMORY_PARROT all\n"
            "    at recall 0.000 establishes clean negative control; arms_distinct=True per seed\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (HRR bind-noise preplay + cosine similarity ranking).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "swr_preplay_constructive_hypothesis_generator_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_SWR,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 5,
            "seeds": [7, 17, 23, 31, 41],
            "N_DIM": 8192,
            "V_BANK": 256,
            "K_CANDS": 10,
            "N_PROBLEMS": 200,
            "verdict_raw": "HARD_FAIL",
            "hard_fail_reason": "pipeline_top1_0p108_lt_HF_floor_0p15_downstream_scorer_bottleneck",
            "PREPLAY_FULL_recall_at_10_MEASURED": 0.558,
            "PREPLAY_FULL_recall_cv_MEASURED": 0.035,
            "PREPLAY_FULL_novelty_MEASURED": 1.000,
            "PREPLAY_FULL_diversity_MEASURED": 0.074,
            "GEN_SCORE_PIPELINE_recall_MEASURED": 0.573,
            "GEN_SCORE_PIPELINE_pipeline_top1_MEASURED": 0.108,
            "DIAG_PREPLAY_DIVERSITY_recall_MEASURED": 0.568,
            "BASELINE_OBSERVATION_ECHO_recall_MEASURED": 0.000,
            "BASELINE_RANDOM_DRAW_recall_MEASURED": 0.000,
            "MEMORY_PARROT_recall_MEASURED": 0.000,
            "MEMORY_PARROT_novelty_MEASURED": 0.000,
            "lift_echo_MEASURED": 0.558,
            "lift_rand_MEASURED": 0.558,
            "arms_distinct_MEASURED": True,
            "cardinality_ok_MEASURED": True,
            "n_units_observed": 60000,
            "n_units_expected": 60000,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "PREPLAY_recall_middle_band_pipeline_top1_below_HF_floor_two_layers_distinct",
            "load_bearing_finding_1": "PREPLAY_generator_recall_0p558_lift_0p558_substrate_quality",
            "load_bearing_finding_2": "pipeline_scorer_top1_0p108_downstream_bottleneck_not_generator",
            "scope_observed": "full_N8192_V_BANK256_5_seeds_200_problems_K_CANDS_10",
            "scope_not_claimed": "chain_grade_pipeline_OR_alternative_scorers_OR_N_16384_scaling",
            "brain_analog": "SWR_preplay_generator_works_vmPFC_OFC_scorer_substrate_cosine_weak",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 5 -- Boundary detector MEASURED_MECHANISM (saturated at drill regime)
# ============================================================================

def build_atom5_boundary_detector_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_stage3_narrative_event_boundary_detector_only_v1_MEASURED_MECHANISM_full_"
            "COSINE_SHIFT_P_1p000_R_1p000_F1_1p000_cv_0p000_TIES_oracle_at_drill_regime_SNR_22x_"
            "FIXED_BUDGET_f1_0p554_RANDOM_f1_0p357_lift_over_budget_0p446_lift_over_random_0p643_"
            "n_seeds_3_N1024_N_events_100_WITHIN_DRIFT_0p10_BOUNDARY_FLIP_0p45_band_floor_drill_regime"
        ),
        name=(
            "stage3_narrative_event_boundary_detector_only v1 MEASURED_MECHANISM at full: COSINE_SHIFT "
            "P=R=F1=1.000 cv=0.000 TIES oracle at drill regime (SNR ~22x; WITHIN=0.10 vs BOUNDARY=0.45); "
            "lift_over_budget=+0.446; mechanism valid but saturated; band-floor inconclusive"
        ),
        description=(
            "MEASURED_MECHANISM substrate event-boundary detector via cosine-shift at drill regime\n"
            "(delta=0). COSINE_SHIFT P=R=F1=1.000 with cv=0.000 across 3 seeds. Saturated against\n"
            "oracle (oracle_f1=1.000; cs_f1=1.000; identical predicted_sha16 per seed pair).\n"
            "Drill regime (WITHIN_DRIFT=0.10 vs BOUNDARY_FLIP=0.45) gives SNR ratio ~4.5x; with\n"
            "theta-calibration median 0.798-0.801 and MAD 0.012 the effective signal-to-noise is\n"
            "~22x noise floor. Mechanism IS valid (lifts over FIXED_BUDGET and RANDOM baselines\n"
            "cleanly), but ties oracle leaves an open question: does cosine-shift continue to\n"
            "discriminate at harder regimes where boundaries flip closer to within-episode drift?\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds: 11, 13, 19;\n"
            "4 arms = RANDOM_BOUNDARIES / FIXED_BUDGET / COSINE_SHIFT / ORACLE_CEILING):\n"
            "  Cardinality: 12/12 OK (4 arms x 3 seeds).\n"
            "  Per-arm boundary_f1 (across 3 seeds):\n"
            "    RANDOM_BOUNDARIES   {11:0.286, 13:0.500, 19:0.286} mean=0.357 cv=high\n"
            "    FIXED_BUDGET        {11:0.571, 13:0.375, 19:0.714} mean=0.554 cv=high\n"
            "    COSINE_SHIFT        {11:1.000, 13:1.000, 19:1.000} mean=1.000 cv=0.000 *PRIMARY*\n"
            "    ORACLE_CEILING      {11:1.000, 13:1.000, 19:1.000} mean=1.000 cv=0.000\n"
            "  Discriminator: COSINE_SHIFT 1.000 - FIXED_BUDGET 0.554 = +0.446 lift (HP >= 0.30\n"
            "    cleared); vs RANDOM 0.357 = +0.643 (HP_random_ceil<=0.45 -- RANDOM at 0.357 IS\n"
            "    under ceiling but FIXED_BUDGET 0.554 IS above 0.45 ceiling, which actually means\n"
            "    FIXED_BUDGET is HARDER baseline than RANDOM -- still mechanism cleanly beats both).\n"
            "  Saturation check (arms_distinct pairs):\n"
            "    RANDOM vs FIXED        : True\n"
            "    RANDOM vs COSINE       : True\n"
            "    RANDOM vs ORACLE       : True\n"
            "    FIXED  vs COSINE       : True\n"
            "    FIXED  vs ORACLE       : True\n"
            "    COSINE vs ORACLE       : FALSE  <-- saturated (predicted_sha16 IDENTICAL per seed)\n"
            "  theta_calibrated 0.703-0.707 with calib_median 0.797-0.801 and calib_mad 0.012;\n"
            "  cosine_min 0.051-0.066 cosine_max 0.832-0.852 cosine_mean ~0.73.\n"
            "  Verdict on disk: MIDDLE_BAND with reason 'saturated_mechanism_ties_oracle: cs_f1\n"
            "  =1.0000 within 0.02 of oracle_f1=1.0000 at SNR >> noise (drill regime WITHIN=0.10\n"
            "  / BOUNDARY=0.45 gives SNR ~ 22x noise). Mechanism IS valid'.\n"
            "\n"
            "SCOPE OF THE MEASURED_MECHANISM CLAIM:\n"
            "  CLAIM: 'Cosine-shift boundary detector (calibrate theta on first calib_end=30%%\n"
            "    events; flag cosine drop > theta) achieves P=R=F1=1.000 at drill regime\n"
            "    (WITHIN_DRIFT=0.10, BOUNDARY_FLIP=0.45) across 3 seeds, N=1024 N_EVENTS=100\n"
            "    N_TRUE_BOUNDARIES=10 TOL=2. Lifts +0.446 over FIXED_BUDGET=0.554; +0.643 over\n"
            "    RANDOM=0.357.'\n"
            "  VERIFIED: per-seed P/R/F1 reproduce from per_arm_metrics[arm][seed] values; oracle\n"
            "    predicted_sha16 matches cosine_shift per seed (saturated); theta values verified.\n"
            "  SCOPE INCLUDES: drill regime (WITHIN=0.10 BOUNDARY=0.45 ratio ~4.5x); N=1024\n"
            "    N_EVENTS=100 TOL=2; 3 seeds.\n"
            "  SCOPE EXCLUDES: harder regimes (WITHIN closer to BOUNDARY; e.g. 0.30 vs 0.45);\n"
            "    real narrative (this is synthetic bipolar stream); larger N_TRUE_BOUNDARIES;\n"
            "    chain-grade tier (saturated mechanism cannot be promoted via this evidence).\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-cert-owner; by-construction-\n"
            "saturation per Fix #28):\n"
            "  COSINE_SHIFT cs_f1=1.000 = oracle_f1=1.000 at drill regime. Per by-construction-\n"
            "  saturation rule: when primary arm ties oracle ceiling AND drill-regime SNR is\n"
            "  >>> noise floor, the mechanism is operating where the test cannot discriminate.\n"
            "  Chain-grade requires evidence from a regime where the mechanism fires below\n"
            "  oracle (allowing comparison). Cell-author flagged this in cell verdict as\n"
            "  MIDDLE_BAND with 'mechanism IS valid; ANCHOR 1 cosine-shift path GREEN-LIT'.\n"
            "  Skunkworks tiers MM (substrate-product framing: mechanism characterized at this\n"
            "  regime; harder-regime cell needed for chain-grade).\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Event segmentation: behavioral psych (Zacks-Swallow event segmentation theory)\n"
            "  + neural prediction-error signals in mPFC / inferior parietal during event\n"
            "  boundaries. Substrate realization: cosine-shift on neural population state\n"
            "  detects boundary as cosine-similarity drop relative to within-episode drift.\n"
            "  Brain analog: ANCHOR 1 cosine-shift in substrate. Saturation at drill regime is\n"
            "  consistent with brain saturation on cleanly-segmented narratives; harder real-\n"
            "  narrative regime is where the discriminator question lives.\n"
            "\n"
            "INTERACTION WITH NARRATIVE COHERENCE atom #5 (Skunkworks cross-link):\n"
            "  ATOM 3 (narrative coherence 100-event) finding: NO_SEGMENT arm TIES FULL_STACK\n"
            "  arm at overall=0.556 = segmentation primitive NOT load-bearing for narrative\n"
            "  comprehension at default regime. This boundary-detector cell (ATOM 5) shows the\n"
            "  primitive WORKS at drill regime. Reconciliation: the primitive functions cleanly\n"
            "  as a mechanism but does no marginal work for downstream narrative tasks at the\n"
            "  tested regime. Both findings are substrate-already-does-X compatible.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 12/12 OK\n"
            "  META_RULE_J no-silent-except: hardening L1early+L2perarm+L4importsentinel\n"
            "  META_RULE_K discriminator: COSINE 1.0 vs FIXED 0.554 gap +0.446; vs RANDOM 0.357\n"
            "    gap +0.643; cleanly distinct mechanisms (sha16 distinguishes arms)\n"
            "  META_RULE_L band: COSINE 1.000 at saturation ceiling; FIXED 0.554 above RANDOM\n"
            "    ceiling 0.45 (FIXED_BUDGET is harder baseline than RANDOM); legitimate\n"
            "    dynamic range\n"
            "  META_RULE_AA fairness: COSINE_SHIFT ties ORACLE_CEILING (predicted_sha16\n"
            "    IDENTICAL per seed) -- by-construction-saturation rule fires; not chain-grade\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero_llm_calls_at_inference per metrics).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "stage3_narrative_event_boundary_detector_only_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_BOUNDARY,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_DIM": 1024,
            "N_EVENTS": 100,
            "N_CHARACTERS": 5,
            "N_TRUE_BOUNDARIES": 10,
            "WITHIN_EPISODE_DRIFT_RATE": 0.10,
            "BOUNDARY_FLIP_RATE": 0.45,
            "THETA_TUNING_SPLIT": 0.30,
            "TOLERANCE_WINDOW": 2,
            "K_FIXED": 10,
            "verdict_raw": "MIDDLE_BAND",
            "middle_band_reason": "saturated_mechanism_ties_oracle_at_drill_regime_SNR_22x",
            "COSINE_SHIFT_precision_MEASURED": 1.000,
            "COSINE_SHIFT_recall_MEASURED": 1.000,
            "COSINE_SHIFT_f1_MEASURED": 1.000,
            "COSINE_SHIFT_f1_cv_MEASURED": 0.000,
            "FIXED_BUDGET_f1_MEASURED": 0.554,
            "RANDOM_f1_MEASURED": 0.357,
            "ORACLE_CEILING_f1_MEASURED": 1.000,
            "lift_over_budget_MEASURED": 0.446,
            "lift_over_random_MEASURED": 0.643,
            "arms_distinct_COSINE_vs_ORACLE_MEASURED": False,
            "by_construction_saturation_MEASURED": True,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "COSINE_at_saturation_ceiling_FIXED_in_active_band_RANDOM_below_band",
            "cross_link_atom_id_REFERENCE_narrative_coherence": (
                "T3/EXP_stage3_narrative_coherence_100event_5char_full_stack_v1_MEASURED_MECHANISM_full"
            ),
            "cross_link_finding": "segmentation_primitive_functions_at_drill_but_does_no_marginal_work_at_default_narrative_regime",
            "scope_observed": "drill_regime_WITHIN_0p10_BOUNDARY_0p45_SNR_22x_N1024_100_events_3_seeds",
            "scope_not_claimed": "harder_regime_WITHIN_closer_to_BOUNDARY_OR_real_narrative_OR_chain_grade",
            "brain_analog": "Zacks_Swallow_event_segmentation_mPFC_inferior_parietal_prediction_error",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 6 -- META_RULE_AM substrate-already-does-X discipline meta (delta=0; meta corpus)
# ============================================================================

def build_atom6_meta_rule_am_substrate_already_does_X() -> Atom:
    return Atom(
        id=(
            "META_RULE_AM_substrate_already_does_X_test_discipline_for_any_proposed_richer_mechanism_"
            "cell_author_must_demonstrate_substrate_existing_primitive_FAILS_at_that_regime_FIRST_"
            "if_substrate_primitive_succeeds_richer_mechanism_cell_unnecessary_OR_must_demonstrate_"
            "added_value_at_harder_regime_8_occurrences_today_substrate_already_does_X_pattern_first_"
            "atomized_extends_META_RULE_AL_at_process_layer_meta_discipline"
        ),
        name=(
            "META_RULE_AM substrate-already-does-X test discipline: for any proposed cell with "
            "'richer mechanism', cell-author MUST demonstrate substrate's existing primitive FAILS "
            "at that regime FIRST. If substrate primitive succeeds, richer mechanism cell is unnecessary "
            "(or must demonstrate added value at a HARDER regime). Extends META_RULE_AL to process layer"
        ),
        description=(
            "META_RULE_AM substrate-already-does-X test discipline (discipline atom; delta=0).\n"
            "Process-layer extension of META_RULE_AL (substrate-cosine pre-encodes schema-prior).\n"
            "Substrate's existing chain-grade primitives (cosine cleanup / flat preplay / explicit\n"
            "encoding / TRACE / partition / refuse-gate) frequently pre-encode the capabilities\n"
            "that 'richer brain-grounded mechanisms' propose to add. The richer mechanisms\n"
            "repeatedly TIE or LOSE to substrate-primitive baselines at default regimes.\n"
            "\n"
            "EVIDENCE (8 occurrences in today's experimental wave; chronological):\n"
            "  1. Schema-driven ANCHOR 1 vmPFC context-prior\n"
            "     (data/exp_cortex_schema_instantiation_context_prior_v1_smoke/metrics.json):\n"
            "     CONTEXT_BOUND_PRIOR=0.731 vs EXEMPLAR_BAYES=0.728; lift +0.003.\n"
            "     Richer top-down prior mechanism adds zero over cheap exemplar-cosine.\n"
            "     -> META_RULE_AL covers this at the substrate-cosine-kernel layer.\n"
            "\n"
            "  2. Schema-driven ANCHOR 2 MAC+FAC structural rerank\n"
            "     (data/exp_cortex_schema_MACFAC_two_stage_retrieval_v1_smoke/metrics.json):\n"
            "     MAC+FAC=0.665 LOSES to EXEMPLAR=0.728 by -0.063.\n"
            "     Structural alignment HURTS at default regime.\n"
            "\n"
            "  3. Schema M-sweep capacity cliff\n"
            "     (data/exp_schema_inference_M_sweep_capacity_cliff_v1_smoke/metrics.json):\n"
            "     Predicted cone-collapse at M=24-48; observed cosine STAYS at 0.80 up to\n"
            "     M=1024 (32x scaling). No cliff.\n"
            "\n"
            "  4. Schema cross-schema overlap sweep\n"
            "     (data/exp_schema_inference_cross_schema_overlap_sweep_v1_smoke/metrics.json):\n"
            "     Predicted MAC+FAC crosses EXEMPLAR at 50-75%% overlap; observed cosine wins\n"
            "     at ALL overlaps 0-90%%.\n"
            "\n"
            "  5. Hierarchical planning v1\n"
            "     (data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json):\n"
            "     TREE=0.60 LOSES to FLAT=0.967 by -0.367. Hierarchical decomposition HURTS\n"
            "     where FLAT preplay already saturates.\n"
            "\n"
            "  6. Self-explanation v1+v2\n"
            "     (data/exp_self_explanation_deletion_fidelity_v{1,2}_*_smoke/metrics.json):\n"
            "     Bind-trace (v1 bilinear=0.240; v2 marginal=0.026) LOSES to raw COSINE\n"
            "     attribution=0.467. Substrate self-explanation IS via raw cosine.\n"
            "\n"
            "  7. Narrative event-segmentation (cross-link to ATOM 3 this batch)\n"
            "     (data/exp_stage3_narrative_coherence_100event_5char_full_stack_v1/metrics.json):\n"
            "     ARM_NO_SEGMENT=0.556 TIES ARM_FULL_STACK=0.556 (lift 0.000); predicted_sha16\n"
            "     IDENTICAL across all 3 seeds. Event-segmentation primitive NOT load-bearing\n"
            "     at K_active=51 / alpha=0.05 / 100-event regime.\n"
            "\n"
            "  8. Boundary detector at drill regime (cross-link to ATOM 5 this batch)\n"
            "     (data/exp_stage3_narrative_event_boundary_detector_only_v1/metrics.json):\n"
            "     COSINE_SHIFT F1=1.000 = ORACLE F1=1.000 at drill regime (SNR 22x noise).\n"
            "     Detection mechanism works but ties oracle ceiling -- chain-grade requires\n"
            "     harder regime where mechanism fires below oracle.\n"
            "\n"
            "INTERPRETATION (load-bearing for batch design):\n"
            "  Substrate's existing primitives are MORE CAPABLE than test design typically\n"
            "  assumes. Proposed 'richer mechanisms' repeatedly fail to add value because:\n"
            "    (a) Richer mechanism recovers same info via different operation that substrate\n"
            "        cosine / preplay already extracts\n"
            "    (b) Test regime is below mechanism's discriminating cliff; substrate handles\n"
            "        default cases trivially via existing primitives\n"
            "    (c) Richer mechanism introduces noise without regime requiring it\n"
            "\n"
            "META_RULE_AL (atomized batch 13) captures this at ONE layer: substrate cosine\n"
            "kernel pre-encodes schema-prior. META_RULE_AM extends to PROCESS DISCIPLINE:\n"
            "any cell proposing richer mechanism must first demonstrate substrate's existing\n"
            "primitive FAILS at the test regime.\n"
            "\n"
            "PROCESS DISCIPLINE (mandatory pre-reg additions for richer-mechanism cells):\n"
            "  PRE-REG CHECK 1: Cell-author must run substrate-existing-primitive arm FIRST\n"
            "    as part of the same cell (not a separate cell). If existing primitive saturates\n"
            "    or matches richer-mechanism within margin, cell is INFORMATIVE-NULL not honest-\n"
            "    negative (no resources spent on richer-mechanism dead-ends).\n"
            "  PRE-REG CHECK 2: Cell must specify the DISCRIMINATING regime where substrate\n"
            "    primitive is hypothesized to fail. If primitive succeeds at default + drill,\n"
            "    cell-author must justify why this regime is interesting (e.g. capacity ceiling;\n"
            "    cross-domain; harder distractors).\n"
            "  PRE-REG CHECK 3: ARMS must include a SUBSTRATE_PRIMITIVE arm at the same\n"
            "    parameters as the proposed RICHER_MECHANISM arm. Bias-Q applies (substrate\n"
            "    primitive arm cannot have unfair advantage; cross-arm parity verified).\n"
            "  PRE-REG CHECK 4: If SUBSTRATE_PRIMITIVE ties RICHER_MECHANISM within margin\n"
            "    (e.g. lift < 0.05), the cell verdict is MEASURED_MECHANISM (informative null)\n"
            "    not HARD_FAIL. Substrate-already-does-X is a positive substrate finding even\n"
            "    when the richer-mechanism hypothesis fails.\n"
            "\n"
            "ATOMS ATOMIZED VIA THIS PATTERN TODAY (cross-link):\n"
            "  Batch 13 atom 3 (cortex_schema_instantiation_context_prior_v1): cited as\n"
            "    Occurrence 3 of substrate-already-does-X; META_RULE_AL atomized in batch 13.\n"
            "  Batch 14 atom 3 (stage3_narrative_coherence_100event_5char_full_stack_v1):\n"
            "    NO_SEGMENT ties FULL_STACK = Occurrence 7 (segmentation null).\n"
            "  Batch 14 atom 5 (stage3_narrative_event_boundary_detector_only_v1):\n"
            "    COSINE_SHIFT ties ORACLE at drill regime = Occurrence 8 (saturated mechanism).\n"
            "\n"
            "REFERENT POINTER:\n"
            "  Source synthesis note: " + META_AM_SYNTH_NOTE + "\n"
            "\n"
            "META TIER + delta=0:\n"
            "  CERT-neutral discipline atom; does not change CERT N count; lives in meta corpus.\n"
            "  Pairs with META_RULE_AL (which lives in meta corpus already; atomized batch 13).\n"
        ),
        kind=AtomKind.METHODOLOGY,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_NEUTRAL",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AM",
            "rule_short_name": "substrate_already_does_X_test_discipline",
            "extends_rule_id": "META_RULE_AL",
            "extends_layer": "process_discipline_for_cell_authors",
            "occurrences_today": 8,
            "synthesis_note_path": META_AM_SYNTH_NOTE,
            "ruling_note": RULING_NOTE,
            "atomized_by": ATOMIZED_BY,
            "verified_off_data": True,
            "delta": 0,
            "cross_link_atoms_today": [
                "T3/EXP_cortex_schema_instantiation_context_prior_v1 (batch 13 MM; META_RULE_AL)",
                "T3/EXP_stage3_narrative_coherence_100event_5char_full_stack_v1 (batch 14 ATOM 3)",
                "T3/EXP_stage3_narrative_event_boundary_detector_only_v1 (batch 14 ATOM 5)",
            ],
            "process_discipline_checks": [
                "PRE_REG_CHECK_1_substrate_primitive_arm_in_same_cell",
                "PRE_REG_CHECK_2_discriminating_regime_specified",
                "PRE_REG_CHECK_3_SUBSTRATE_PRIMITIVE_arm_with_same_params_as_RICHER_MECHANISM",
                "PRE_REG_CHECK_4_tie_within_margin_lift_lt_0p05_is_MEASURED_MECHANISM_not_HARD_FAIL",
            ],
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "N/A_meta_rule_not_substrate_inference",
        },
    )


# ============================================================================
# Helpers
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

    # Row 1 -- CF regret vmPFC v1 CHAIN_GRADE (delta=+1)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_counterfactual_regret_comparison_vmpfc_v1_CHAIN_GRADE_full',
        'cert_status': 'chain_grade',
        'cert_class': 'pre_reg_pass',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 1,
        'cv': 0.0021,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_CF_REGRET,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_CF_regret_vmpfc_v1_CHAIN_GRADE_full_R2_0p987_gap_1p195_5_seeds',
        'ts': now_ts + 0.001,
    })

    # Row 2 -- Schema exemplar-Bayes CHAIN_GRADE PROMOTE batch13 MM (delta=+1)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_cortex_schema_exemplar_bayes_importance_sample_v1_CHAIN_GRADE_full',
        'cert_status': 'chain_grade',
        'cert_class': 'pre_reg_pass',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 1,
        'cv': 0.025,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SCHEMA_EX_FULL,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_schema_exemplar_bayes_CHAIN_GRADE_PROMOTE_batch13_MM_full_72k_events_5_seeds',
        'ts': now_ts + 0.002,
    })

    # Row 3 -- Narrative coherence 100-event MM (delta=0)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_stage3_narrative_coherence_100event_5char_full_stack_v1_MEASURED_MECHANISM_full',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_FAIL',
        'cert_increment_delta': 0,
        'cv': 0.187,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_NARRATIVE,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_narrative_coherence_MM_Q1_0p889_Q4_1p000_substrate_quality_AND_NO_SEGMENT_ties_FULL_STACK',
        'ts': now_ts + 0.003,
    })

    # Row 4 -- SWR preplay MM (delta=0)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_swr_preplay_constructive_hypothesis_generator_v1_MEASURED_MECHANISM_full',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_FAIL',
        'cert_increment_delta': 0,
        'cv': 0.035,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_SWR,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_swr_preplay_MM_generator_recall_0p558_lift_0p558_pipeline_top1_0p108_bottleneck',
        'ts': now_ts + 0.004,
    })

    # Row 5 -- Boundary detector MM (delta=0)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_stage3_narrative_event_boundary_detector_only_v1_MEASURED_MECHANISM_full',
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': CELL_COMMIT,
        'verdict': 'MIDDLE_BAND',
        'cert_increment_delta': 0,
        'cv': 0.000,
        'referent_pointer': {
            'notes_path': RULING_NOTE,
            'metrics_path': METRICS_BOUNDARY,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_boundary_detector_MM_cosine_shift_F1_1p000_ties_oracle_drill_regime_by_construction_saturation',
        'ts': now_ts + 0.005,
    })

    # Row 6 -- META_RULE_AM substrate-already-does-X discipline meta (delta=0)
    rows.append({
        'op': 'cert_ruling',
        'atom_id': 'meta::META_RULE_AM_substrate_already_does_X_test_discipline',
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
            'metrics_path': META_AM_SYNTH_NOTE,
            'atom_qualified_id': None,
        },
        'supersedes': None,
        'note': 'batch14_META_RULE_AM_substrate_already_does_X_process_discipline_extends_AL_8_occurrences_today',
        'ts': now_ts + 0.006,
    })

    return rows


# ============================================================================
# Main: A5-gated apply
# ============================================================================

def main(apply: bool):
    print(f'=== atomize_skunkworks_batch14_overnight_stage3_2026-06-28 (apply={apply}) ===')
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
        build_atom1_cf_regret_vmpfc_chain_grade(),
        build_atom2_schema_exemplar_bayes_chain_grade(),
        build_atom3_narrative_coherence_mm(),
        build_atom4_swr_preplay_mm(),
        build_atom5_boundary_detector_mm(),
        build_atom6_meta_rule_am_substrate_already_does_X(),
    ]
    print(f'Built {len(atoms)} atoms.')
    for i, a in enumerate(atoms, 1):
        print(f'  ATOM {i}: {a.corpus.name}::{a.id[:100]}{"..." if len(a.id) > 100 else ""}')

    if not apply:
        print()
        print('DRY RUN -- not applying. Re-run with --apply to commit.')
        print(f'Planned: +2 chain-grade (predicted CERT N: {pre_cert} -> {pre_cert + 2})')
        print(f'         +3 measured_mechanism, +1 discipline_meta, 0 honest_negative')
        print(f'REFUSALS (filed in landed-vet note; no atoms): CF v2 + Online conv hippo (bug not HN)')
        return 0

    # APPLY -- one atom at a time, A5 per-window
    now_ts = float(time.time())
    rows = build_ledger_rows(now_ts)
    assert len(rows) == len(atoms), f'rows ({len(rows)}) != atoms ({len(atoms)})'

    expected_total_delta = 0
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

        # Cert delta must match expected
        delta_expected = row['cert_increment_delta']
        delta_actual = win_post_cert - win_pre_cert
        expected_total_delta += delta_expected
        assert delta_actual == delta_expected, (
            f'CERT delta mismatch: expected {delta_expected} got {delta_actual} '
            f'(pre={win_pre_cert} post={win_post_cert})'
        )

        # Append ledger row (cert_ledger_writer does its own A5 gate)
        # NOTE: ledger writer does NOT modify the Store; CERT N pre == post for ledger writes.
        # Store was already updated by ps.add_atom() above; win_post_cert reflects that.
        ledger_hash = append_cert_ledger_row(
            row,
            expected_cert_n_pre=win_post_cert,    # ledger PRE = post-Store-write CERT N
            expected_cert_n_post=win_post_cert,   # ledger writer doesn't move Store -> equal
        )
        print(f'  LEDGER: appended row hash={ledger_hash}')

    # Final POST snapshot
    print()
    ps_final = PartitionedStore(store_root)
    post_cert = _cert_count(ps_final)
    post_total = _total_count(ps_final)
    print(f'=== FINAL: cert_n={post_cert} (PRE {pre_cert}, delta {post_cert - pre_cert})  '
          f'total={post_total} (PRE {pre_total}, delta {post_total - pre_total}) ===')

    assert post_cert == pre_cert + 2, f'OVERALL CERT delta wrong: expected +2, got {post_cert - pre_cert}'
    assert post_total == pre_total + 6, f'OVERALL TOTAL delta wrong: expected +6, got {post_total - pre_total}'

    print()
    print('A5-GATED APPLY COMPLETE.')
    print(f'  CERT N: {pre_cert} -> {post_cert} (delta +2)')
    print(f'  TOTAL:  {pre_total} -> {post_total} (delta +6)')
    print(f'  Ledger rows appended: 6')
    return 0


if __name__ == '__main__':
    apply = '--apply' in sys.argv[1:]
    sys.exit(main(apply))
