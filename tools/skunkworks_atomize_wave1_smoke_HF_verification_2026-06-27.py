#!/usr/bin/env python3
"""Skunkworks verify-off-data audit on the 4 Wave 1 SMOKE_HARD_FAILs of 2026-06-27.

USER directive: skunktest every negative for verification, then 2x verified negatives.

VERDICTS (verified off raw per-arm metrics; NOT framing-from-verdict-msg):

1. exp_pfc_controller_per_step_operator_select_v1_smoke -> TEST_DESIGN_FAILURE_CONFIRMED
   - run_arm_single_baseline computes W_avg = np.mean(np.stack(W_ops, axis=0))
     literally averaging all 4 operator matrices. That IS an implicit uniform-mixture
     controller. Research's framing (baseline ate ~57% of oracle's lift via avg-of-ops)
     is structurally correct.
   - Per-arm at depth=3: PFC=0.59 / Single=0.56 / Random=0.01 / Oracle=0.99. depth=2
     uniformly 0 (chain too short). Smoke only has 2 depths.
   - Counter-evidence vindicates: pfc_softmax_v2_smoke d=6 SOFTMAX=0.383 SINGLE_FIXED=
     0.0056 RANDOM=0.000 (lift +0.378 over a NON-averaged single-op baseline);
     verified directly from data/exp_pfc_controller_softmax_margin_abstain_v2_smoke/
     metrics.json. Mechanism works; v1 baseline was rigged.
   - NO 2x drill needed (pfc_softmax_v2 already HARD_PASS).

2. exp_multi_readout_fisher_importance_v1_smoke -> TEST_DESIGN_FAILURE_CONFIRMED
   (UNDERSAMPLED_SMOKE_NOT_CEILING)
   - Verified per-arm seed-17 wins exist in raw metrics:
       eight_readout_pca_basis seed=17 sel_unretr = 0.1436 (CONFIRMS +0.144 claim)
       diag_k_sweep            seed=17 sel_unretr = 0.2999 (CONFIRMS +0.300 claim)
                                                   cor_with_W = 0.0  (perfect orthog)
       eight_readout_fisher cv_sel = 1.230 (CONFIRMS undersampling claim)
       eight_readout_pca_basis cv_sel = 1.065 (also wildly undersampled)
   - At n=2 with cv > 1, +0.089 mean lift could be +0.20 or -0.05 at population
     scale -- the smoke is statistically powerless to rule the mechanism null.
   - Per-arm wins above the +0.15 chain-grade bar exist (one arm at +0.144 just
     below bar; another at +0.300 well above). Substrate ceiling NOT confirmed.
   - Revival lock_in_amp_pca_readout_fisher_v1 in flight (directory exists);
     gives fair-power answer.
   - NO 2x drill needed (revival captures the fair test).

3. exp_btsp_binary_synapse_one_shot_v1_smoke -> FIX_28_VIOLATION_HALLUCINATED_HEADLINE
   - CRITICAL: Research cited 'ContHeb=0.954 BTSP=0.020' as the v1 smoke result. These
     numbers DO NOT EXIST in the on-disk metrics.json. The metrics file shows
     verdict='RUNNING' verdict_msg='RUNNING: seed=7 (1/2)' -- the cell never
     completed. No partial seed files exist. The headline was fabricated (likely
     hallucinated from the pre-reg HP_SATURATION_LO=0.95 + a downstream what-if).
   - This is the WORST form of Fix #28 violation: not just verdict-msg framing
     drift but fully invented per-arm numbers that anchor a META rule + a revival
     drill design.
   - The v1 cell IS test-design-saturated-IN-PRE-REG (HP_SATURATION_LO=0.95 fires
     HARD_FAIL_SATURATION if ContHeb >= 0.95; alpha=0.0488 is in safe band but
     N_TRAIN=10 + proto_noise=0.85 is still tight) -- BUT we don't know that
     happened because the cell didn't finish. The v2_regime_probed cell (now
     RUNNING_PROBE) IS the appropriate revival regardless.
   - Tier disposition: NOT TEST_DESIGN_FAILURE (we don't have data to call it
     that), NOT HONEST_NEGATIVE_SUBSTRATE (cell didn't run), NOT a ceiling claim.
     It's an INCONCLUSIVE_CELL_DID_NOT_COMPLETE + a FIX_28_HALLUCINATED_HEADLINE
     atom. 2x drill = re-dispatch v1 to actually complete OR wait for v2_regime
     _probed (preferred -- v1 framing is broken; v2 is the right cell).
   - NO 2x drill of v1 (replaced by v2_regime_probed already in flight).

4. exp_sub_atom_token_stream_encoder_v1_smoke -> TEST_DESIGN_FAILURE_CONFIRMED
   (DISCRIMINATOR_VACUOUS_REDESIGN_REQUIRED)
   - Per-arm verified: at depth=3+ all 5 arms = 1.000 on the unbind_d3 proxy
     (including char_trigram_baseline). But at depth=1 there IS signal:
       char_trigram_baseline d1 = 0.0
       math_codebook_token  d1 = 1.0
       math_codebook_var_rename d1 = 1.0
       math_codebook_role_filler d1 = 1.0
       diag_bind_depth d1 = 1.0
     Codebook arms beat trigram 1.0 vs 0.0 at d=1.
   - Root cause confirmed in source: trigram_unbind_proxy uses cos(whole, arg0) >
     0.30 -- at depth>=3 the synthetic expressions are short enough that whole
     and arg0 char-trigrams overlap with cos > 0.30 essentially always (no actual
     unbinding tested; it's a permissive similarity proxy on short overlapping
     strings).
   - alpha_equiv_cos at 1.0 confirms the role-filler arms work -- but the
     discriminator at d=3 doesn't FIRE because trigram saturates.
   - Research's framing (synthetic too short/repetitive -> trigram saturated ->
     discriminator vacuous; redesign with real Mathlib pretty-prints) is correct
     in structure though the depth=1 signal is a partial-positive hidden in the
     MIDDLE_BAND verdict that Research's framing didn't surface.
   - NO 2x drill needed of v1 (corpus is the broken thing; need redesign with
     real corpus per Research's lean_mathlib_ingest_v1 plan).

META_RULE_AA atomized: FAIRNESS-BEFORE-TIER. The 3 verified TEST_DESIGN_FAILURE cells
support the rule's first 3 clauses (rigged baseline / undersampled smoke / vacuous
discriminator on broken corpus). The BTSP case is a SEPARATE failure mode (cite-
without-data) handled by Fix #28 + the dedicated audit atom.

DIRECTOR OVERRIDE (cert-owner authority per role separation):
- Research stated 'ContHeb=0.954 BTSP=0.020' for the BTSP v1 smoke result; this is
  REFUTED -- the metrics file shows the cell never completed. Research's META
  pattern note is HALF-CORRECT (3 of 4 cells confirmed; BTSP entry must be
  removed or corrected to 'cell did not complete; v2_regime_probed dispatched').

NO 2X DRILLS TRIGGERED (no honest-negative-substrate verdicts in the 4):
- pfc v1: revival pfc_softmax_v2 already HARD_PASS
- multi_readout v1: revival lock_in_amp_pca_readout_fisher_v1 in flight
- btsp v1: revival btsp_v2_regime_probed in flight (RUNNING_PROBE state)
- sub_atom v1: needs real-corpus redesign (lean_mathlib_ingest_v1 prereq)

ATOMIZATION PLAN (this script, idempotent, A5-gated):

1. TEST_DESIGN_FAILURE_pfc_controller_v1 (audit_lesson; pq=None; META corpus)
2. TEST_DESIGN_FAILURE_multi_readout_fisher_v1 (audit_lesson; pq=None)
3. TEST_DESIGN_FAILURE_sub_atom_encoder_v1 (audit_lesson; pq=None)
4. FIX_28_HALLUCINATED_HEADLINE_btsp_v1 (audit_lesson; pq=None)
5. META_RULE_AA_FAIRNESS_BEFORE_TIER (methodology_rule; T_methodology)

NO cert_ledger appends (none of these are chain-grade results; all are
methodology / discipline atoms).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


STORE_ROOT = Path("d:/AI/hd-instrument/data/substrate_index")
SOURCE_TAG = "skunkworks_verify_off_data_wave1_smoke_HF_audit_2026-06-27"


def _add_safely(atom: Atom, note: str) -> bool:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"SKIP (idempotent): {atom.id[:80]}")
        return True
    print(f"ADDING: {atom.id[:90]}")
    ps.add_atom(atom, source=SOURCE_TAG, note=note)
    ps2 = PartitionedStore(STORE_ROOT)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: not present post-add")
        return False
    if found.tier != atom.tier or found.kind != atom.kind:
        print(f"  FAIL: tier/kind drift on round-trip")
        return False
    print(f"  PASS: round-trip clean")
    return True


def atom_pfc() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_pfc_controller_per_step_operator_select_v1"
            "_baseline_avg_of_4_ops_IS_implicit_uniform_mixture_router"
            "_run_arm_single_baseline_literally_computes_W_avg_np_mean_np_stack_W_ops"
            "_axis_0_axis_0_verified_pfc_0p59_single_0p56_random_0p01_oracle_0p99_depth_3"
            "_revival_pfc_softmax_v2_HARD_PASS_lift_0p378_2026-06-27"),
        name=("TEST_DESIGN_FAILURE pfc_controller_v1: SINGLE_BASELINE = avg of 4 W_ops "
              "= implicit uniform-mixture routing (verified in source); revival "
              "pfc_softmax_v2 with single_fixed_baseline HARD_PASSed lift +0.378"),
        description=(
            "Wave 1 SMOKE_HARD_FAIL (PFC=0.59 Single=0.56 lift +0.03 at depth=3). "
            "Verify-off-data finding: run_arm_single_baseline in experiments/"
            "exp_pfc_controller_per_step_operator_select_v1.py (line 289-301) "
            "literally computes `W_avg = np.mean(np.stack(W_ops, axis=0), axis=0)` "
            "and applies W_avg at every hop. This IS an implicit uniform-mixture "
            "controller -- the baseline does ~57% of the routing job (Single 0.56 / "
            "Oracle 0.99 = 0.566). The mechanism arm vs averaged-ops baseline measures "
            "the wrong thing. Per-arm at depth=3 verified from raw metrics.json: "
            "single_operator_baseline=0.560 (cv 0.107), pfc_controller_cosine_argmax="
            "0.590 (cv 0.085), random_router=0.010 (cv 1.0), diag_oracle_router=0.990 "
            "(cv 0.010). depth=2 uniformly 0 across all arms (chains too short). "
            "Revival counter-evidence: exp_pfc_controller_softmax_margin_abstain_v2_"
            "smoke verified at depth=6 SOFTMAX=0.383 / SINGLE_FIXED=0.0056 / RANDOM="
            "0.000 / ARGMAX=0.344 (lift +0.378 over a NON-averaged single-op baseline) "
            "n=3 seeds cv=0.061. Mechanism works cleanly when baseline is a single "
            "fixed operator instead of mean-of-ops. Test design fail confirmed; "
            "mechanism status: works at depth>=6 with margin/abstain. No 2x drill of "
            "v1 needed (v2 already HARD_PASS)."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 244,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "baseline_implicitly_does_mechanism",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_pfc_controller_per_step_operator_select_v1_smoke/metrics.json",
            "source_code_line": "experiments/exp_pfc_controller_per_step_operator_select_v1.py:293",
            "revival_cell": "exp_pfc_controller_softmax_margin_abstain_v2_smoke",
            "revival_verdict": "HARD_PASS",
            "revival_lift": 0.378,
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_multi_readout() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_multi_readout_fisher_importance_v1_smoke"
            "_undersampled_n_eq_2_cv_eq_1p23_NOT_substrate_ceiling"
            "_per_arm_seed_17_wins_eight_readout_pca_basis_sel_0p1436_diag_k_sweep_sel_0p2999"
            "_revival_lock_in_amp_pca_readout_fisher_v1_in_flight_2026-06-27"),
        name=("TEST_DESIGN_FAILURE multi_readout_fisher_v1: undersampled smoke (n=2 cv=1.23) "
              "hid per-arm seed-17 wins (PCA-basis +0.144 / diag_k_sweep +0.300); revival "
              "lock_in_amp_pca_readout_fisher_v1 in flight"),
        description=(
            "Wave 1 SMOKE_HARD_FAIL (Fisher=+0.039 lift=+0.089 cv=1.23 at n=2). "
            "Verify-off-data finding: per-arm raw values from metrics.json confirm "
            "Research's per-seed wins. eight_readout_pca_basis seed 17 sel_unretr = "
            "0.1436 (just below +0.15 chain-grade bar); diag_k_sweep seed 17 sel_unretr "
            "= 0.2999 with cor_with_W = 0.0 (perfect orthogonality + strong signal). "
            "eight_readout_fisher arm cv_sel = 1.230 (the headline cv); eight_readout_"
            "pca_basis arm cv_sel = 1.065. At n=2 with cv > 1, the +0.089 mean lift could "
            "be anywhere in roughly [-0.05, +0.20] at population scale -- the smoke "
            "lacks statistical power to rule the mechanism null. Substrate ceiling NOT "
            "confirmed. Revival cell directory exp_lock_in_amp_pca_readout_fisher_v1 "
            "exists (in-flight); will give fair-power answer at n>=3 seeds M>=300 to "
            "drive cv below 0.30 before any mechanism claim. No 2x drill of v1 needed "
            "(revival cell IS the fair test). Note: this is also the IMMEDIATE cause "
            "of the M-CFU honest-bound PAUSE (the substrate physics ceiling claim was "
            "anchored on this underpowered smoke)."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 245,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "undersampled_smoke_hides_per_arm_wins",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_multi_readout_fisher_importance_v1_smoke/metrics.json",
            "key_per_arm_values": {
                "eight_readout_pca_basis_seed_17_sel": 0.1436,
                "diag_k_sweep_seed_17_sel": 0.2999,
                "diag_k_sweep_seed_17_cor": 0.0,
                "eight_readout_fisher_cv_sel": 1.230,
                "eight_readout_pca_basis_cv_sel": 1.065,
            },
            "revival_cell": "exp_lock_in_amp_pca_readout_fisher_v1",
            "revival_state": "in_flight",
            "downstream_impact": "M_CFU_honest_bound_PAUSE_anchored_on_this_smoke",
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
            ],
        },
    )


def atom_sub_atom_encoder() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_sub_atom_token_stream_encoder_v1_smoke"
            "_discriminator_vacuous_unbind_d3_proxy_cos_gt_0p30_saturates_at_1p0"
            "_for_trigram_baseline_AND_codebook_arms_on_short_synthetic_exprs"
            "_depth_1_partial_positive_hidden_codebook_arms_1p0_vs_trigram_0p0"
            "_redesign_with_lean_mathlib_corpus_2026-06-27"),
        name=("TEST_DESIGN_FAILURE sub_atom_encoder_v1: unbind_d3 proxy cos > 0.30 "
              "saturates trigram AND codebook to 1.0 on short synthetic; depth=1 hidden "
              "partial-positive (codebook 1.0 vs trigram 0.0); redesign w/ Mathlib corpus"),
        description=(
            "Wave 1 SMOKE MIDDLE_BAND (all metrics at 1.000 depth=3; cv=0). Verify-off-"
            "data finding: per-arm raw at depth=3 confirms all 5 arms = 1.000 on "
            "unbind_d3 (char_trigram_baseline INCLUDED). Source line "
            "experiments/exp_sub_atom_token_stream_encoder_v1.py:478-484 (trigram_unbind"
            "_proxy / encoded.py) uses `cos > 0.30` threshold on whole-encoding vs "
            "arg0-encoding -- on short synthetic expressions the whole and arg0 "
            "char-trigrams have heavy overlap, so cos>0.30 is essentially always true "
            "regardless of arm. NOT actual unbinding being tested. Hidden partial-"
            "positive at depth=1 (not surfaced by Research's MIDDLE_BAND framing): "
            "char_trigram d1 = 0.0; math_codebook_token d1 = 1.0; var_rename d1 = 1.0; "
            "role_filler d1 = 1.0; diag_bind_depth d1 = 1.0. Codebook arms beat trigram "
            "1.0 vs 0.0 at d=1, which IS a real discrimination -- but the d>=3 proxy "
            "is broken. alpha_equiv_cos = 1.0 across all role-filler-bearing arms "
            "(working), trigram=0 (no concept of alpha-equiv). codebook_disambig = "
            "1.0 for codebook arms, 0.0 for trigram (working). So 2-of-5 discriminator "
            "signals work; the unbind-by-depth signal is the broken one. Research's "
            "redesign-with-Mathlib framing is correct; lean_mathlib_ingest_v1 prereq "
            "in prereg directory. No 2x drill of v1 needed (corpus IS the broken "
            "thing; redesign required). Composes META_RULE_K (smoke must FIRE "
            "discriminator) -- this is the canonical case of discriminator not "
            "firing due to baseline saturation."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 246,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "discriminator_vacuous_on_short_synthetic",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_sub_atom_token_stream_encoder_v1_smoke/metrics.json",
            "source_code_line": "experiments/exp_sub_atom_token_stream_encoder_v1.py:478-484 (trigram_unbind_proxy cos>0.30)",
            "hidden_partial_positive_at_depth_1": {
                "char_trigram_d1": 0.0,
                "math_codebook_token_d1": 1.0,
                "math_codebook_var_rename_d1": 1.0,
                "math_codebook_role_filler_d1": 1.0,
            },
            "working_discriminator_signals": ["alpha_equiv_cos", "codebook_disambig"],
            "broken_discriminator_signal": "unbind_d3 / d5 (proxy too permissive on short synthetic)",
            "revival_prereq": "lean_mathlib_ingest_v1 (real corpus required)",
            "composes_with": [
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
            ],
        },
    )


def atom_btsp_fix28() -> Atom:
    return Atom(
        id=("AUDIT_FIX_28_HALLUCINATED_HEADLINE_btsp_binary_synapse_one_shot_v1_smoke"
            "_research_cited_ContHeb_0p954_BTSP_0p020_numbers_DO_NOT_EXIST_in_metrics_json"
            "_actual_state_verdict_RUNNING_seed_7_1_of_2_cell_never_completed_no_partial_files"
            "_director_override_per_role_separation_v2_regime_probed_appropriate_revival_2026-06-27"),
        name=("FIX_28 HALLUCINATED HEADLINE btsp_v1: Research cited ContHeb=0.954 BTSP=0.020 "
              "as v1 smoke result; numbers DO NOT EXIST in metrics.json (verdict=RUNNING, "
              "cell never completed); cert-owner OVERRIDE -- v2_regime_probed is the revival"),
        description=(
            "CRITICAL FIX #28 violation found during verify-off-data audit of the 4 "
            "Wave 1 SMOKE_HARD_FAILs. Research's META_FAIRNESS_PATTERN note "
            "(notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md) "
            "cited specific BTSP v1 smoke per-arm numbers: 'ContHeb=0.954 saturation "
            "rail; BTSP itself collapsed to 0.020'. These numbers DO NOT EXIST anywhere "
            "in the on-disk artifacts. The actual state of data/exp_btsp_binary_"
            "synapse_one_shot_v1_smoke/metrics.json (verified 2026-06-27 by Skunkworks): "
            "verdict='RUNNING', verdict_msg='RUNNING: seed=7 (1/2)', _phase='seed_"
            "running'. The cell crashed or was killed mid-seed-7 and never wrote final "
            "metrics. Zero partial seed files exist in the smoke directory or its "
            "non-smoke sibling. The headline numbers Research cited were FABRICATED "
            "(likely hallucinated by interpolating from the pre-reg HP_SATURATION_LO=0.95 "
            "+ a downstream 'BTSP collapsed because binary+tag-only-5% retains too little "
            "signal' narrative). This is the WORST form of Fix #28 violation: not just "
            "verdict-msg framing drift but fully invented per-arm numbers that anchor a "
            "META rule, a revival drill design, and the structural framing of one of "
            "the 4 'test design failure' cells. CERT-OWNER OVERRIDE (per role-separation): "
            "the BTSP entry in Research's META_FAIRNESS pattern note must be corrected to "
            "'INCONCLUSIVE_CELL_DID_NOT_COMPLETE' (NOT TEST_DESIGN_FAILURE, NOT "
            "HONEST_NEGATIVE_SUBSTRATE). The v2_regime_probed cell (currently "
            "RUNNING_PROBE in data/exp_btsp_binary_synapse_one_shot_v2_regime_probed_"
            "smoke/) IS the appropriate revival regardless of v1's failure mode; the "
            "v2 pre-reg explicitly probes for a regime where baseline_hebbian sits in "
            "[0.40, 0.65] BEFORE running BTSP, which is the correct fairness recipe. "
            "But the framing 'v1 was test-design failure because Skunkworks recipe "
            "insufficient' is unsupported -- we have no v1 data to support OR refute "
            "that claim. No 2x drill of v1 (replaced by v2_regime_probed in flight)."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 247,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "fix28_hallucinated_per_arm_numbers_no_data_to_cite",
            "verified_off_data": True,
            "actual_metrics_state": {
                "verdict": "RUNNING",
                "verdict_msg": "RUNNING: seed=7 (1/2)",
                "_phase": "seed_running",
            },
            "research_claimed_but_nonexistent_numbers": {
                "ContHeb": 0.954,
                "BTSP": 0.020,
            },
            "research_framing_corrected_to": "INCONCLUSIVE_CELL_DID_NOT_COMPLETE",
            "appropriate_revival": "exp_btsp_binary_synapse_one_shot_v2_regime_probed",
            "revival_state": "RUNNING_PROBE",
            "director_override_applied": True,
            "composes_with": [
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "Fix28_violation_count_internalize_harder",
                "META_RULE_V_USER_pushback_on_framing_or_limit_claim_triggers_verification",
                "feedback_skunkworks_correctly_overrides_director_via_by_construction_saturation",
            ],
        },
    )


def atom_meta_rule_aa() -> Atom:
    return Atom(
        id=("T_methodology/META_RULE_AA_FAIRNESS_BEFORE_TIER_HARD_FAIL_cells_must_have"
            "_fairness_audited_before_filed_as_honest_negative_baselines_must_not_implicitly"
            "_do_mechanism_smoke_n_and_cv_must_distinguish_lift_from_noise_regime_must"
            "_actually_exercise_mechanism_discriminator_must_FIRE_or_verdict_is_TEST_DESIGN"
            "_FAILURE_not_HONEST_NEGATIVE_USER_directive_2026-06-27_witness_4_cell_wave1"),
        name=("META_RULE_AA FAIRNESS-BEFORE-TIER: HARD_FAIL cells must have fairness "
              "audited before being filed as honest-negative -- 4 fairness gates "
              "(baseline / smoke power / regime / discriminator)"),
        description=(
            "META RULE AA (CERT-neutral; discipline_meta):\n\n"
            "A cell that HARD_FAILs MUST have its FAIRNESS audited before the result "
            "is filed as honest-negative. Specifically:\n"
            "  (a) BASELINES MUST NOT IMPLICITLY DO THE MECHANISM we're testing. "
            "      A baseline arm that already incorporates some fraction of the "
            "      mechanism (e.g. averaging the very operators a router would pick "
            "      between; ensembling readouts a Fisher selector would gate; "
            "      smoothing trajectories an attractor would correct) gives a rigged "
            "      comparison and the mechanism may be working without the lift "
            "      showing up.\n"
            "  (b) SMOKE SEEDS AND N MUST BE LARGE ENOUGH to distinguish lift from "
            "      noise. Per-arm cv_sel < 0.30 is the gate (with cv > 1.0 at n=2 the "
            "      mechanism status is UNKNOWN, not NULL). Per-arm seed-level wins "
            "      hidden by aggregate means must be surfaced.\n"
            "  (c) THE REGIME MUST ACTUALLY EXERCISE THE MECHANISM. Baselines that "
            "      saturate (>=0.95) make any mechanism arm look like null; "
            "      preconditions that fail (e.g. tag fraction too low for BTSP, "
            "      sequence depth too short for chains) starve the mechanism. "
            "      Pre-flight regime probe required when pre-reg specifies baseline "
            "      target band.\n"
            "  (d) THE TEST DATA MUST ALLOW THE DISCRIMINATOR TO FIRE (META_RULE_K). "
            "      A discriminator that saturates all arms (top-1=1.0 across the "
            "      board) is vacuous regardless of cell.\n\n"
            "If any of (a)-(d) is violated the verdict is NOT HONEST_NEGATIVE_"
            "SUBSTRATE -- it is TEST_DESIGN_FAILURE. Re-author + re-smoke before "
            "tiering. The mechanism status remains UNKNOWN.\n\n"
            "WITNESS (2026-06-27 wave-1 smoke audit, 3 of 4 cells confirmed by "
            "verify-off-data):\n"
            "  - pfc_controller_v1: baseline = avg of 4 operator matrices = implicit "
            "    uniform-mixture router (violation of (a)). Revival pfc_softmax_v2 "
            "    with single_fixed_baseline showed lift +0.378 at depth=6 -- "
            "    mechanism works cleanly.\n"
            "  - multi_readout_fisher_v1: smoke n=2 cv=1.23 hid per-arm seed-17 "
            "    wins (eight_readout_pca_basis +0.144; diag_k_sweep +0.300) "
            "    (violation of (b)).\n"
            "  - sub_atom_encoder_v1: unbind_d3 proxy uses cos > 0.30 threshold on "
            "    short synthetic expressions -- trigram baseline saturates 1.0 along "
            "    with codebook arms (violation of (d)); depth=1 partial-positive "
            "    (codebook 1.0 vs trigram 0.0) hidden by MIDDLE_BAND framing.\n"
            "  - btsp_v1: cell did not complete (cert-owner override; Research's "
            "    framing 'regime saturated baseline' relied on hallucinated numbers; "
            "    inconclusive, not test-design-failure).\n\n"
            "ENFORCEMENT:\n"
            "  (1) Skunkworks landed-VET MUST run the 4 fairness gates before "
            "      tiering any HARD_FAIL as honest-negative-substrate. The default "
            "      tier for an unverified HARD_FAIL is TEST_DESIGN_FAILURE_PENDING "
            "      until gates pass.\n"
            "  (2) Research META framing notes that anchor multi-cell patterns "
            "      MUST verify per-arm metrics OFF DATA before invoking the cells "
            "      as witnesses (Fix #28 again).\n"
            "  (3) Pre-reg authors should include a 'fairness self-check' section "
            "      addressing (a)-(d) before dispatch.\n\n"
            "USER directive 2026-06-27 ~15:00 PDT (anchor): 'Make sure we don't "
            "accept a ceiling just because we get bad results, and make sure our "
            "tests are actually fairly testing.' This rule operationalizes that "
            "directive.\n\n"
            "COMPOSES-WITH:\n"
            "  - META_RULE_K (smoke must FIRE discriminator): gate (d)\n"
            "  - META_RULE_W (alpha M/N safe band 0.03-0.20): gate (c) for plasticity\n"
            "  - META_RULE_T (per-arm metric verification before META atomization): "
            "    upstream of (a)/(b) verification\n"
            "  - META_RULE_V (USER pushback on framing triggers verification): "
            "    this rule was authored under that trigger\n"
            "  - Fix #28 (verify per-arm not summary verdict text): structural prereq"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 248,
            "confirmed_or_candidate": "CONFIRMED",
            "rule_letter": "AA",
            "rule_class": "fairness_before_tier",
            "user_directive_anchor": "2026-06-27_~15_00_PDT",
            "witnesses_count": 3,
            "witness_cells": [
                "exp_pfc_controller_per_step_operator_select_v1_smoke",
                "exp_multi_readout_fisher_importance_v1_smoke",
                "exp_sub_atom_token_stream_encoder_v1_smoke",
            ],
            "witness_inconclusive": ["exp_btsp_binary_synapse_one_shot_v1_smoke"],
            "fairness_gates": ["baseline_no_implicit_mechanism", "smoke_power_cv_below_0p30",
                               "regime_exercises_mechanism", "discriminator_fires"],
            "composes_with": [
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "META_RULE_W_pre_dispatch_alpha_M_over_N_in_0p03_to_0p20_gate",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
                "META_RULE_V_USER_pushback_on_framing_or_limit_claim_triggers_verification",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def main() -> int:
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print(__doc__)
        print("\nUse --dry-run to preview, --apply to write.")
        return 1

    atoms = [
        (atom_pfc(), "TEST_DESIGN_FAILURE pfc_v1 verified"),
        (atom_multi_readout(), "TEST_DESIGN_FAILURE multi_readout_fisher_v1 verified"),
        (atom_sub_atom_encoder(), "TEST_DESIGN_FAILURE sub_atom_encoder_v1 verified"),
        (atom_btsp_fix28(), "FIX_28 HALLUCINATED HEADLINE btsp_v1 (cert-owner override)"),
        (atom_meta_rule_aa(), "META_RULE_AA fairness-before-tier (4-cell wave1 witness)"),
    ]

    if "--dry-run" in sys.argv:
        for a, note in atoms:
            qid = f"{a.corpus.value}::{a.id}"
            print(f"DRY: {note}")
            print(f"  qid: {qid[:120]}")
            print(f"  kind={a.kind.value} tier={a.tier.value}")
            print()
        return 0

    ok_count = 0
    for a, note in atoms:
        if _add_safely(a, note):
            ok_count += 1
        else:
            print(f"  HALT: failed to add {a.id[:80]}")
            return 1
    print(f"\nDONE: {ok_count}/{len(atoms)} atoms added (idempotent).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
