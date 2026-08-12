"""
A5-gated atomization: exp_settling_fix_learned_recurrent_v1 (committed 6eb8d86fc, local-only)
-> ONE atom (2026-07-20). MEASURED_MECHANISM (mechanism rehabilitated, readout refuted).

CELL AUTHOR VERDICT: HARD_FAIL_3_GRADED_BUT_NOT_MEANINGFUL_NULL_GOLD_CORRELATION (full power, 368s).
AUDITOR TIER: MEASURED_MECHANISM -- the settling MECHANISM is genuinely rehabilitated (a real, bounded
positive residue) while the residual-of-change-as-parse-plausibility READOUT is refuted at this substrate
maturity (the clean negative). Not a pure HARD_FAIL (that discards the real mechanism sub-win); not
chain-grade (no capability). A proven boundary -- counts toward CERT N.

INDEPENDENT OFF-DISK RECOMPUTE (.venv Scripts/python; NOT verdict_msg; Fix #28):
  metrics.json has no raw per-item trajectories; verification is (a) gate-arithmetic recompute from the
  reported per-arm aggregates and (b) internal-consistency + referent audit. All 8 HP/HF gates reproduce
  EXACT from agg_full/agg_eval:
    oom_above_floor = log10(var/floor_var(A)): B=log10(2.9118e-8/7.4612e-10)=1.5914; C=log10(8.3380e-9/
      7.4612e-10)=1.0483; D=log10(6.7365e-7/7.4612e-10)=2.9556. (match 1.59/1.05/2.96 verdict_msg.)
    HP1 oomC>=3 -> 1.05>=3 = False. HP2 (rhoC_eval>=0.3 or accC_eval-g3_eval>=0.10) -> (-0.128>=0.3 F) or
      (0.583-0.625=-0.042>=0.10 F) = False. HP3 (accC>accA and accC-accD>=0.10) -> (0.583>0.5 T) and
      (0.583-0.5=0.083>=0.10 F) = False. HP4 (beta<20 and multistep>1_2step) -> (3.0<20 T) and (96>0 T)=True.
    HF1 oomC<1 -> 1.05<1 = False (NOT pinned at floor). HF2 accC<=accD -> 0.583<=0.5 = False.
    HF3 (oomC>=1 and |rhoC_eval|<0.15 and accC_eval-g3_eval<0.10) -> (1.05>=1 T)(0.128<0.15 T)(-0.042<0.10 T)
      = True. HF4 beta>=20 -> 3.0>=20 = False (NOT refit to ceiling).
    Verdict cascade (cardinality_ok, arms_differ, not HF1, not HF2, not HF4, HF3) -> HARD_FAIL_3. CONFIRMED.
  Mechanism rehabilitation (the positive residue), all off-disk:
    fitted_beta=3.0 << 20 (grid genuinely beta-sensitive: fit_grid_results 0.5->0.625,1.0->0.625,2.0->0.667,
      3.0->0.667,5.0->0.625,8.0->0.583,12.0->0.542,20.0->0.542 -- accuracy PEAKS at low-mid beta, DEGRADES
      toward the ceiling; NOT flat, NOT collapsing to the 0.5 global-average 3rd-fixed-point-class). Tie at
      best-acc 0.667 is beta {2.0,3.0}; margin tie-break picked 3.0 -- both deep in the graded regime.
    C convergence-class (full pooled n=96): 1-2step=0, multi-step=96, nonconvergent=0 -> genuine multi-step.
    oom_C=1.05 above the freshly-measured A floor (var 8.34e-9 vs 7.46e-10) -> graded, above floor.
    HF1 (residual pinned at floor) = False AND HF4 (beta refits to ceiling) = False -> BOTH structural
      codebook-collapse failure modes the drill feared (P_deflated 0.40 was largely this risk) STAYED CLEAR.
      => the graded regime EXISTS for this exact codebook; beta_c sits in the ~2-3 neighborhood, NOT above 20.
      This is NOT the codebook-geometry structural limit.
  Readout refutation (the clean negative), all off-disk:
    C EVAL rho vs gold = -0.128 (null / slightly negative; |rho|<0.15). C full rho = +0.107 (still null).
    C EVAL acc = 0.583 < STATIC thematic-fit G3 EVAL 0.625 -> the zero-settle static endpoint-style readout
      BEATS the settled trajectory residual. (Consistent with the parent HF atom's already-banked finding
      "settling ADDS NOTHING vs static readout".)
    C beats must-fail random-recurrent D by only +0.083 (0.583 vs 0.500) < the +0.10 pre-registered bar --
      a WEAK below-bar positive (learned direction does slightly better than random, not enough).
  Integrity: cardinality_ok (n_units_done=192 == 4*48); arms_differ 6/6 pairs on RAW residual trajectories;
    must_fail_D_fires=True (D eval acc 0.500, all-nonconvergent -> genuinely non-discriminating, so the
    C-vs-D comparison is trustable); per_unit_failures={}.

Q1 (HF3 right interpretation / readout-choice confound?): YES HF3 is right. The mechanism-rehabilitated /
  no-content SPLIT is real: graded multi-step beta-sensitive settling now works (HF1+HF4 clear), yet the
  residual-of-change readout is null (rho -0.128) and loses to static G3. No readout-choice confound
  RESCUES C: the static zero-settle thematic-fit (G3=0.625) is already the ceiling here and the residual
  simply carries no ADDITIONAL signal; the endpoint>trajectory direction REINFORCES the negative rather
  than flipping it. The untested alternative (reading the FINAL SETTLED STATE's thematic-fit instead of the
  residual-of-change) is a DIFFERENT readout the cell does not test -- noted, but it is NOT the pre-registered
  Rabovsky SU/N400 residual hypothesis, and G3 (a static thematic-fit) already occupies that endpoint-readout
  ceiling. HF3 stands as a genuine substantive negative on the residual-as-coherence hypothesis.
Q2 (p-hack?): NO. The HP/HF BANDS are byte-verbatim from the drill's Falsifiable-predictions and match the
  cell gate code EXACTLY (recomputed above) -- not retuned toward a pass. The one pre-reg/impl discrepancy is
  the FIT-split tie-break rule (pre-reg text said "smallest beta"; cell uses "largest FIT margin among
  accuracy-tied betas"), documented in _fit_beta's docstring as a mid-SMOKE authoring-bug correction to avoid
  walking past beta_c into the uninformative global-average fixed-point class. This changes only WHICH beta
  is selected on a tie, biases TOWARD discrimination/pass (larger margin), was fixed BEFORE the full run, and
  C STILL HARD_FAILED with its best-margin beta -- so it is exculpatory, not a fail-ward hack. Author reported
  HF3 explicitly rather than silently re-tuning. No p-hack.
Q3 (BRAIN-CHECK): CONFIRMED brain-consistent. The brain's Sentence-Gestalt N400-residual (Rabovsky/Hansen/
  McClelland 2018) is INFORMATIVE only because the whole recurrent net's WEIGHTS are TRAINED on graded
  comprehension (no one-hot target; "shift of labour from activation to connection weights"). Our settling
  runs over a FIXED PPMI/SVD codebook whose geometry encodes distributional co-occurrence, NOT per-instance
  thematic plausibility -- so a settling DYNAMIC can only surface signal that is REPRESENTED; it cannot
  manufacture a signal that was never written into the geometry. The brain solves it DIFFERENTLY (train the
  recurrent weights on a comprehension signal) and that mechanism IS the redirect (fix-3). SAME WALL as the
  affectedness-MM (text-derivation of the per-instance patient/affectedness signal FAILED; only an INJECTED
  curated signal tracks correctness) and the CPCL forensic (patient-selection residual has NO text-internal
  self-supervised signal): a text-internal computation over a static distributional codebook does not track
  per-instance thematic/plausibility correctness -- it needs a TRAINED/GROUNDED/injected signal. Cross-arc
  connection CONFIRMED (framed to the affectedness+CPCL cluster, which is what the "29375" prose index names).
Q4 (redirect right?): YES. Because HF1 (pinned) and HF4 (beta-to-ceiling) BOTH stayed clear, the fix is NOT
  more beta/damping tuning (that regime already works) and NOT codebook pattern-separation reconstruction
  (the graded dynamic already works -- the missing thing is CONTENT, not geometric separation). The remaining
  gap is that the codebook does not ENCODE plausibility, which a TRAINED similarity/energy function on
  coherent-vs-corrupted pairs (the drill's held-in-reserve fix-3, contrastive-divergence/EBM) would install.
  This is also exactly the brain's mechanism. Correct redirect.

POSITIVE-CONTROL / TEST-DESIGN attribution (HF_STRUCTURAL_BOUND, not HF_TEST_DESIGN_FAILURE): the item set is
  NOT degenerate -- static G3 = 0.625 > chance 0.5 proves a real plausibility signal EXISTS in the data; and
  the beta-grid is genuinely sensitive (0.542-0.667), proving the settling machinery is LIVE and CAN
  discriminate. So the residual readout's null is a genuine substantive property of the residual readout over
  this codebook, not a dead test. HF genuinely substantive.

FRAMING CORRECTION vs the parent HARD_FAIL: this cell AMENDS (does not supersede) the parent settling_parse_
  selector HF. The parent labeled the whole thing HF_STRUCTURAL; this cell splits it: the RESIDUAL-PINNING leg
  (residual at float32 noise floor) was a beta=20 ARTIFACT and is REHABILITATABLE (graded regime exists) --
  a modest UPWARD correction on that leg -- while the READOUT-NULL leg is the REAL structural bound and is
  confirmed MORE robustly here (null even at the rehabilitated graded regime). Symmetric anti-negativity:
  mechanism sub-win preserved, readout negative sharpened.

LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist; no git add -A.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = ("skunkworks_landed_vet_settling_fix_learned_recurrent_v1_MM_mechanism_rehabilitated_graded_"
               "regime_exists_beta_3p0_readout_of_change_refuted_rho_neg0p128_loses_to_static_G3_same_wall_"
               "affectedness_cpcl_brain_sentence_gestalt_trained_weights_2026-07-20")
ATOMIZED_DATE = "2026-07-20"
ANCHOR = "settling_fix_learned_recurrent_v1"
CELL_COMMIT = "6eb8d86fc"

# referents verified off-disk (exact IDs pulled from math/atoms.jsonl)
PARENT_SETTLING_HF = ("math::HARD_FAIL_settling_parse_selector_richness_v1_kintsch_CI_settling_residual_"
                      "coherence_NOT_a_usable_parse_selection_signal_pooled_0p5000")  # prefix-match; the HF being rehabilitated
XARC_AFFECTEDNESS = ("math::MM_affectedness_change_of_state_patient_selection_design_gate_v1")  # prefix-match; text-derivation FAILS, only injected tracks
XARC_CPCL = ("math::HF_FORENSIC_cpcl_v2_entity_recurrence_reader_loop_component_audit_HONEST_NEGATIVE")  # prefix-match; no text-internal self-sup patient signal

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "Cross-arc overlap check (substrate KB, mechanism = 'settling residual coherence parse plausibility "
    "static PPMI codebook'): the top prior cells are the DIRECT lineage -- the parent HARD_FAIL "
    "settling_parse_selector_richness_v1 (this cell is its commissioned rehabilitation) and the two source "
    "research notes (both cosine>0.30, both read in full, being built on not rediscovered). The affectedness-MM "
    "and cpcl-v2 forensic surface as the SAME-WALL cluster (text-internal signal over a distributional codebook "
    "does not track per-instance thematic correctness) and are cited as cross-arc composition, NOT duplication. "
    "This is a targeted mechanism extension of a named prior HF, not a full rediscovery."
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_settling_fix_learned_recurrent_v1_settling_MECHANISM_REHABILITATED_graded_regime_"
    "EXISTS_for_static_ppmi_svd_codebook_fitted_beta_3p0_FAR_below_ceiling_20_beta_grid_GENUINELY_sensitive_fit_"
    "acc_peaks_0p667_at_beta_2_3_drops_0p542_at_beta_12_20_C_convergence_96of96_MULTI_STEP_0_one_two_step_0_"
    "nonconv_oom_above_floor_C_1p05_B_1p59_var_8p3e9_vs_A_floor_7p5e10_HF1_pinned_at_floor_FALSE_HF4_beta_refit_"
    "to_ceiling_FALSE_so_NOT_the_codebook_collapse_STRUCTURAL_limit_feared_by_drill_Pdefl_0p40_BUT_the_"
    "rehabilitated_RESIDUAL_of_CHANGE_readout_carries_NO_per_instance_plausibility_signal_C_eval_rho_neg0p128_"
    "NULL_C_eval_acc_0p583_LOSES_to_STATIC_thematic_fit_G3_0p625_beats_must_fail_random_recurrent_D_by_only_"
    "plus0p083_BELOW_0p10_bar_HARD_FAIL_3_graded_but_not_meaningful_verdict_REPRODUCED_offdisk_ALL_8_gates_"
    "recompute_EXACT_cardinality_192of192_arms_differ_6of6_must_fail_D_fires_acc_0p500_POSITIVE_CONTROL_G3_0p625_"
    "above_chance_AND_beta_sensitivity_prove_test_LIVE_so_HF_STRUCTURAL_BOUND_not_test_design_failure_NO_PHACK_"
    "bands_byte_verbatim_from_drill_tie_break_fix_biases_toward_pass_and_C_still_failed_BRAIN_SentenceGestalt_"
    "N400_residual_informative_ONLY_because_recurrent_WEIGHTS_TRAINED_on_graded_comprehension_our_FIXED_ppmi_"
    "codebook_never_encodes_per_instance_plausibility_dynamic_CANNOT_manufacture_absent_signal_SAME_WALL_as_"
    "affectedness_MM_and_cpcl_forensic_text_internal_signal_over_distributional_codebook_does_NOT_track_per_"
    "instance_thematic_correctness_REDIRECT_fix3_TRAINED_similarity_energy_function_coherent_vs_corrupted_pairs_"
    "NOT_more_beta_damping_tuning_NOT_codebook_reconstruction_AMENDS_parent_settling_parse_selector_HF_residual_"
    "pinning_leg_was_beta_ARTIFACT_not_structural_readout_null_leg_IS_the_real_bound_LOCAL_ONLY_2026-07-20"
)

PLAIN = (
    "An earlier attempt to read 'how coherent a parse is' by watching how much a settling process KEEPS "
    "CHANGING across steps failed flat -- the process snapped to its answer in one step (high-gain beta=20), so "
    "there was no ongoing change left to measure. A brain-grounded drill diagnosed this as the 'zero-noise' end "
    "of a well-known family (Hopfield/energy/diffusion) and prescribed a fix: slow the process down (a damped "
    "step) and learn the right 'temperature' from data. This cell ran that fix at full power. GOOD NEWS (a real, "
    "modest sub-win): the fix WORKED at the mechanism level -- the process now genuinely settles over many steps "
    "(96 of 96 cases), the learned temperature landed at 3 (far below the old 20) and the data clearly prefers "
    "that graded setting, and two feared structural dead-ends (the codebook forcing an instant snap; the best "
    "temperature actually being the sharp one) BOTH did NOT happen. So a graded, multi-step settling regime "
    "really does exist for this codebook. BAD NEWS (the honest negative, which is the point): even with the "
    "mechanism fixed, the change-across-steps signal carries NO real information about which parse is more "
    "plausible -- it does not correlate with the right answer, and it LOSES to a plain static one-shot readout "
    "that does no settling at all. WHY (brain-consistent): the brain's version of this signal is informative "
    "only because the whole network was TRAINED on comprehension; ours settles over a FIXED word-embedding "
    "codebook that never learned per-sentence plausibility, so no amount of clever settling can read out a "
    "signal that was never written in. This is the SAME wall we hit with the 'who-is-affected' signal and the "
    "recurrence signal: a text-internal computation over a distributional codebook cannot invent per-instance "
    "meaning. The fix is NOT more temperature tuning and NOT rebuilding the codebook -- it is to TRAIN a "
    "similarity/energy function on coherent-vs-corrupted examples (learn the plausibility landscape). So: the "
    "settling machine is repaired and that is banked; the 'settling residual = coherence' idea is refuted at "
    "this substrate maturity."
)

IMPORTANCE = (
    "MEDIUM-HIGH. Two durable results in one clean full-power negative. (1) A real (bounded) mechanism sub-win: "
    "the graded, multi-step, beta-sensitive settling regime EXISTS for the static PPMI/SVD codebook (fitted "
    "beta=3, 96/96 multi-step, HF1+HF4 both clear) -- this REFUTES the drill's biggest deflation risk (that "
    "beta_c sits above 20 / the codebook forces collapse) and rehabilitates the settling DYNAMIC as a usable "
    "graded coherence trace for the self-monitoring layer. (2) A clean, brain-consistent NEGATIVE: the "
    "residual-of-change readout carries no per-instance plausibility signal (rho null, loses to static G3), "
    "because a fixed distributional codebook does not encode per-instance plausibility and a settling dynamic "
    "cannot manufacture absent signal. This is the SAME wall as the affectedness-MM and CPCL forensic -- a "
    "recurring, now cross-mechanism-confirmed boundary (text-internal self-supervised signal over a static "
    "codebook does not track per-instance thematic correctness). It sharpens the redirect for the whole "
    "grounded-signal thrust: the missing ingredient is a TRAINED/GROUNDED plausibility landscape (fix-3, or "
    "grounding), NOT more settling-dynamics tuning. Importance is bounded: the mechanism sub-win is plumbing, "
    "NOT a capability; do not inflate 'the settling machine works' into 'coherence readout works'."
)

ATOM_CLAIM = (
    "MATH MEASURED_MECHANISM. TWO-FACED clean full-power negative (author verdict HARD_FAIL_3, CONFIRMED). "
    "MECHANISM REHABILITATED (bounded positive residue): the learned-recurrent settling fix (hand-set damped "
    "step alpha=0.25 + grid-fit effective-beta on a held-out FIT split) restores a GRADED, MULTI-STEP settling "
    "regime over the SAME static PPMI/SVD codebook that the parent settling_parse_selector cell collapsed at "
    "beta=20. Off-disk: fitted_beta=3.0 (<<20); beta grid genuinely sensitive (FIT acc 0.625/0.625/0.667/0.667/"
    "0.625/0.583/0.542/0.542 across beta 0.5..20 -- peaks low-mid, degrades toward ceiling); variant C "
    "convergence-class full pooled n=96 is 96 multi-step / 0 one-two-step / 0 non-convergent; oom_C=1.05 above "
    "the freshly-measured A floor (var 8.34e-9 vs 7.46e-10). Decisively, HF1 (residual pinned at float32 floor) "
    "= False AND HF4 (beta refits back to the ceiling) = False -- BOTH structural codebook-collapse failure "
    "modes the drill feared (the P_deflated=0.40 risk) STAYED CLEAR, so the graded regime EXISTS for this "
    "codebook and beta_c is in the ~2-3 neighborhood, NOT the codebook-geometry structural limit. "
    "READOUT REFUTED (the clean negative): the rehabilitated RESIDUAL-OF-CHANGE readout (Rabovsky SU / N400 "
    "analog, pref_score = tail_residual_V - tail_residual_N) carries NO per-instance plausibility signal -- "
    "C EVAL Spearman rho vs gold = -0.128 (null; full rho +0.107 also null); C EVAL selection acc = 0.583 which "
    "LOSES to the STATIC zero-settle thematic-fit baseline G3 EVAL = 0.625; and C beats the must-fail random-"
    "recurrent control D by only +0.083 (< the +0.10 pre-registered bar) -- a weak below-bar positive. Hence "
    "HARD_FAIL_3 (graded-but-not-meaningful). All 8 HP/HF gates recompute EXACT off-disk from the reported "
    "per-arm aggregates (oom via log10(var/floor); HF3 True; HF1/HF2/HF4 and every HP except HP4 False). "
    "Integrity clean: cardinality 192/192 (4x48), arms_differ 6/6 on raw residual trajectories, must_fail_D_"
    "fires (D EVAL acc 0.500, all-nonconvergent -> genuinely non-discriminating, so C-vs-D is trustable). "
    "ATTRIBUTION HF_STRUCTURAL_BOUND (not HF_TEST_DESIGN_FAILURE): the positive control clears its own floor -- "
    "static G3=0.625 > chance proves the item set carries real plausibility signal, and the live beta-grid "
    "sensitivity proves the machinery can discriminate -- so the residual readout's null is a genuine "
    "substantive property, not a dead test."
)

ATOM_RECOMPUTE = (
    "INDEP off-disk recompute (.venv Scripts/python; NOT verdict_msg; Fix #28). metrics.json stores no raw "
    "per-item trajectories, so verification = gate-arithmetic recompute from the reported per-arm aggregates + "
    "internal-consistency + referent audit. "
    "(A) oom_above_floor = log10(variance/floor_variance(A,full=7.4612e-10)): B=log10(2.9118e-8/7.4612e-10)="
    "1.5914; C=log10(8.3380e-9/7.4612e-10)=1.0483; D=log10(6.7365e-7/7.4612e-10)=2.9556 -- match 1.59/1.05/2.96. "
    "(B) Gates: HP1 (1.05>=3)=F; HP2 ((-0.128>=0.3)or(0.583-0.625=-0.042>=0.10))=F; HP3 ((0.583>0.5)and"
    "(0.083>=0.10))=F; HP4 ((3.0<20)and(96>0))=T. HF1 (1.05<1)=F; HF2 (0.583<=0.5)=F; HF3 ((1.05>=1)and"
    "(0.128<0.15)and(-0.042<0.10))=T; HF4 (3.0>=20)=F. Cascade -> HARD_FAIL_3. CONFIRMED. "
    "(C) Mechanism: fitted_beta=3.0; FIT grid acc {0.5:0.625,1.0:0.625,2.0:0.667,3.0:0.667,5.0:0.625,8.0:0.583,"
    "12.0:0.542,20.0:0.542} (peaks at 2-3, degrades to ceiling -> genuinely beta-sensitive, not global-average "
    "collapse); best-acc 0.667 tie {2.0,3.0} -> margin tie-break to 3.0, both deep graded. C convergence 96 "
    "multi / 0 one_two / 0 nonconv. HF1=F and HF4=F -> both structural-collapse fears clear. "
    "(D) Readout: C EVAL rho=-0.128 (full +0.107); C EVAL acc=0.583 < G3 EVAL 0.625; C-D=+0.083<0.10. "
    "(E) Integrity: n_units_done=192==4*48 cardinality_ok; arms_differ 6/6 pairs (raw trajectories); "
    "must_fail_D_fires=True (D eval acc 0.500); per_unit_failures={}. "
    "(F) Positive-control/test-design: G3=0.625>chance and beta-grid sensitivity => test is LIVE => "
    "HF_STRUCTURAL_BOUND not test-design failure."
)

ATOM_SCOPE = (
    "Single richest codebook regime (matches the parent cell's floor-measurement level EXACTLY): vocab_size="
    "12000, N_DIM=1024, 17M tokens, min_count=5, seed=7, 48 class-balanced PP-attachment items (24 FIT / 24 "
    "EVAL), 4 variants A(one-shot beta=20)/B(damped beta=20)/C(damped+fit-beta)/D(random-recurrent must-fail). "
    "LOAD-BEARING BOUNDS: "
    "(a) MECHANISM SUB-WIN IS PLUMBING, NOT A CAPABILITY: 'the graded multi-step settling regime exists for "
    "this codebook (beta_c~3)' is a real, bounded rehabilitation of the settling DYNAMIC -- it does NOT mean the "
    "coherence readout works. Do not inflate. "
    "(b) THE READOUT IS REFUTED AT THIS SUBSTRATE MATURITY: residual-of-change carries no per-instance "
    "plausibility signal over a FIXED distributional codebook (rho null; loses to static G3). This is the "
    "durable negative. "
    "(c) SAME WALL, CROSS-MECHANISM: the affectedness-MM (text-derivation of the patient/affectedness signal "
    "FAILED; only injected curated signal tracks correctness) and the CPCL forensic (patient-selection residual "
    "has NO text-internal self-supervised signal) show the same boundary from different mechanisms -- a text-"
    "internal computation over a static distributional codebook does NOT track per-instance thematic/plausibility "
    "correctness. A settling dynamic is a third mechanism confirming it. "
    "(d) NO READOUT-CHOICE CONFOUND RESCUES C: reading the final-settled-state thematic-fit (rather than the "
    "residual-of-change) is an untested alternative, but the static zero-settle thematic-fit (G3=0.625) already "
    "occupies that endpoint-readout ceiling and the residual carries no additional signal (endpoint>trajectory "
    "reinforces, not flips, the negative; consistent with the parent HF's 'settling adds nothing vs static'). "
    "BRAIN-CHECK (mandatory-on-negative, CONFIRMED): the brain's Sentence-Gestalt N400-residual (Rabovsky/"
    "Hansen/McClelland 2018) is informative ONLY because the recurrent WEIGHTS are TRAINED on graded "
    "comprehension (no one-hot target; 'shift of labour from activation to connection weights'). Our settling "
    "runs over a FIXED PPMI/SVD codebook that encodes distributional co-occurrence, not per-instance "
    "plausibility; a dynamic can surface only REPRESENTED signal, not manufacture absent signal. The brain "
    "solves it DIFFERENTLY (train the weights on a comprehension signal), and that mechanism IS the redirect. "
    "REDIRECT: fix-3 -- a TRAINED similarity/energy function on coherent-vs-corrupted composed-vector pairs "
    "(contrastive-divergence / EBM = learn the plausibility landscape), NOT more beta/damping tuning (that "
    "regime already works) and NOT codebook pattern-separation reconstruction (HF1 clear -> the graded dynamic "
    "already works; the missing thing is CONTENT, not geometric separation). This is also the brain's mechanism."
)

ATOM_METRICS = {
    "run_mode": "full", "elapsed_s": 368.24, "cell_verdict": "HARD_FAIL_3_GRADED_BUT_NOT_MEANINGFUL",
    "auditor_tier": "MEASURED_MECHANISM_mechanism_rehabilitated_readout_refuted",
    "fitted_beta": 3.0, "beta_grid": [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0],
    "fit_grid_acc": {"0.5": 0.625, "1.0": 0.625, "2.0": 0.667, "3.0": 0.667, "5.0": 0.625,
                     "8.0": 0.583, "12.0": 0.542, "20.0": 0.542},
    "fit_acc": 0.6667, "fit_best_acc_tie_betas": [2.0, 3.0],
    "oom_above_floor_full": {"B": 1.5914, "C": 1.0483, "D": 2.9556},
    "floor_variance_A_full": 7.4612e-10, "variance_C_full": 8.3380e-09,
    "C_convergence_full_pooled_n96": {"one_two_step": 0, "multi_step": 96, "nonconvergent": 0},
    "eval_acc": {"A": 0.500, "B": 0.625, "C": 0.583, "D": 0.500, "G3": 0.625},
    "eval_rho_vs_gold": {"A": -0.108, "B": 0.063, "C": -0.128, "D": -0.030},
    "full_rho_vs_gold_C": 0.107, "C_minus_D_eval_acc": 0.083, "C_minus_G3_eval_acc": -0.042,
    "hard_pass_gates": {"HP1_oom_ge_3": False, "HP2_rho_or_beats_g3": False,
                        "HP3_beats_A_and_D": False, "HP4_beta_below_ceiling_and_multistep": True},
    "hard_fail_gates": {"HF1_pinned_at_floor": False, "HF2_does_not_beat_D": False,
                        "HF3_graded_not_meaningful": True, "HF4_beta_refits_to_ceiling": False},
    "cardinality_ok": True, "n_units_done": 192, "expected_n_units": 192,
    "arms_differ_6of6": True, "must_fail_D_fires": True, "d_eval_acc": 0.500,
    "positive_control_test_live": {"static_G3_eval": 0.625, "chance": 0.5, "beta_grid_sensitive": True},
    "attribution": "HF_STRUCTURAL_BOUND_not_HF_TEST_DESIGN_FAILURE",
}

COMPOSES = [
    ("AMENDS (does NOT supersede) the parent " + PARENT_SETTLING_HF + " ... (settling_parse_selector_richness_v1 "
     "HARD_FAIL, the cell being rehabilitated). The parent banked the whole result as HF_STRUCTURAL: pooled "
     "0.5000 exact chance, residual pinned at the float32 floor (~2.3e-5), settling adds nothing vs the static "
     "0.594 thematic-fit readout. THIS cell SPLITS that HF: (i) the RESIDUAL-PINNING leg was a beta=20 ARTIFACT "
     "and is REHABILITATABLE -- a graded multi-step regime exists at beta_c~3 (modest UPWARD correction on that "
     "leg; the parent's implied 'residual pinning is structural' framing is refined to 'residual pinning was a "
     "high-gain artifact'); (ii) the READOUT-NULL leg is the REAL structural bound and is confirmed MORE "
     "robustly (null even at the rehabilitated graded regime, and still loses to static G3). Parent's readout-"
     "null conclusion STANDS and is strengthened; its residual-pinning=structural leg is amended."),
    ("SAME-WALL cross-mechanism composition with " + XARC_AFFECTEDNESS + " ... (affectedness_change_of_state_"
     "patient_selection MM: text-DERIVATION of the per-instance patient/affectedness signal FAILED, only an "
     "INJECTED curated Dowty-proto-patient x Levin-change-of-state signal tracks correctness) and " + XARC_CPCL +
     " ... (cpcl-v2 forensic: patient-selection residual has NO text-internal self-supervised signal; the target "
     "is uncorrelated with per-instance patient correctness). THIS cell is a THIRD mechanism (settling residual) "
     "confirming the same boundary: a text-internal computation over a static distributional PPMI/SVD codebook "
     "does NOT track per-instance thematic/plausibility correctness. Does NOT supersede either (different "
     "mechanisms); COMPOSES as cross-mechanism corroboration that the missing ingredient is a TRAINED/GROUNDED "
     "signal, not a cleverer text-internal readout."),
    ("credit / build-on: Rabovsky, Hansen & McClelland (2018, Nature Human Behaviour) Sentence-Gestalt N400-as-"
     "update (the residual-of-change readout AND the brain-check for WHY it stays informative: trained recurrent "
     "weights, no one-hot target); Ramsauer et al. (2020/2021) modern-Hopfield beta-as-fixed-point-class; "
     "arXiv:2311.18434 fittable data-dependent beta_c (variant C's grounding -- CONFIRMED beta_c~3 is in-range, "
     "NOT above 20 as feared); arXiv:2506.05178 Hopfield/EBM/diffusion zero-noise-limit unification (the damped-"
     "step trick, which WORKED). The cell AUTHOR (exp_dev) CREDITED for a clean honest full-power negative: "
     "bands byte-verbatim from the drill, must-fail D control fires, arms-differ on raw trajectories, HF3 "
     "reported explicitly not silently re-tuned, and the mid-smoke tie-break fix (documented as an authoring-bug "
     "correction) biases TOWARD a pass yet C still failed -- exculpatory, not a p-hack."),
]

OVER_READS = [
    ("Do NOT inflate the mechanism sub-win into a capability. 'The graded multi-step settling regime exists for "
     "this codebook (beta_c~3, 96/96 multi-step, HF1+HF4 clear)' is real and banked, but it is PLUMBING -- it "
     "does NOT mean the coherence/plausibility READOUT works. The residual-of-change readout is REFUTED "
     "(rho -0.128, loses to static G3). Report as 'settling dynamic rehabilitated, coherence readout refuted', "
     "not 'settling coherence works'."),
    ("Do NOT read this as merely re-confirming the parent HARD_FAIL. It ADDS a genuine upward correction on the "
     "parent's residual-pinning leg (that pinning was a beta=20 artifact, NOT the structural codebook-collapse "
     "the drill feared -- HF1 and HF4 both stayed clear). The novelty is the mechanism/readout SPLIT."),
    ("Do NOT claim C's learned direction is worthless: C beats the random-recurrent control D by +0.083 (a weak, "
     "below-the-0.10-bar positive), so the learned direction does slightly better than random -- just not enough "
     "to clear the bar or to beat the static baseline. The negative is 'below-bar / not meaningful', not "
     "'exactly zero information'."),
    ("Do NOT redirect toward more beta/damping tuning or codebook pattern-separation reconstruction. HF1 clear "
     "means the graded dynamic already works; the missing ingredient is CONTENT (per-instance plausibility is "
     "not encoded in the fixed codebook), which needs a TRAINED similarity/energy function (fix-3) or grounding "
     "-- the brain's own mechanism -- NOT geometry tuning."),
]

REVIVAL = [
    ("fix-3 (the drill's held-in-reserve, and the brain's mechanism): TRAIN a similarity/energy function on "
     "coherent-vs-corrupted composed-vector pairs (contrastive-divergence / EBM) so the settling energy "
     "landscape ENCODES per-instance plausibility rather than only distributional co-occurrence. This is the "
     "correct next cut because HF1 (pinned) and HF4 (beta-to-ceiling) both stayed clear -- the graded dynamic "
     "already works; only the content is missing. Revival criterion: the trained energy function's settled "
     "readout must correlate with gold at rho>=0.3 OR beat the static G3 baseline by >=0.10 on the held-out "
     "EVAL split (the same bars this cell failed)."),
    ("GROUNDING route (per the session's grounded-signal thrust): supply the per-instance plausibility signal "
     "from a grounded event-plausibility source (perception or a richer grounded corpus) rather than deriving it "
     "text-internally -- the same conclusion the affectedness-MM and CPCL forensic reached. If a grounded signal "
     "makes the settling residual informative, that jointly revives this cell AND the affectedness/patient-"
     "selection thread."),
    ("The rehabilitated graded settling dynamic (beta_c~3, multi-step, inspectable per-iteration residual "
     "trajectory) is itself a reusable component: it can serve as the graded coherence-trace INPUT to the "
     "metacognition/reliability-gate self-monitoring machinery ONCE the readout carries real signal (i.e. after "
     "fix-3 or grounding). Bank the dynamic for reuse; do not re-derive it."),
]

GENUINE_POS = (
    "GENUINE positive preserved (symmetric anti-negativity): the settling MECHANISM rehabilitation is a REAL, "
    "bounded sub-win and I do NOT dilute it. The fix (damped step + grid-fit effective-beta) genuinely restored "
    "a graded, multi-step, beta-sensitive settling regime over the SAME static codebook the parent cell "
    "collapsed at beta=20: fitted_beta=3.0 (<<20), FIT grid accuracy peaks at beta 2-3 and degrades toward the "
    "ceiling (genuinely beta-sensitive), variant C converges multi-step in 96/96 cases with variance 1.05 oom "
    "above the fresh floor, and -- decisively -- BOTH structural codebook-collapse failure modes the drill "
    "feared (residual pinned at floor / beta refitting back to the ceiling) STAYED CLEAR. That refutes the "
    "drill's biggest deflation risk (P=0.40 was largely 'beta_c may sit above 20') and proves the graded regime "
    "EXISTS for this codebook (beta_c~3). This is worth banking as a reusable, inspectable graded coherence-trace "
    "component for the self-monitoring layer. What it is NOT (the scope that keeps it honest): the residual-of-"
    "change READOUT carries no per-instance plausibility signal (rho -0.128, loses to a static one-shot readout, "
    "beats the random control by only +0.083 below the 0.10 bar), so 'settling residual = coherence' is refuted "
    "at this substrate maturity. The negative is brain-consistent (the brain's N400-residual is informative only "
    "because trained recurrent weights encode the signal; our fixed codebook does not) and is the SAME wall as "
    "the affectedness-MM and CPCL forensic. The auditor's tiering (MEASURED_MECHANISM) preserves the mechanism "
    "sub-win as a proven bound while keeping the readout refutation clean; it neither inflates the plumbing into "
    "a capability nor discards the real rehabilitation into a bare HARD_FAIL."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "MEASURED_MECHANISM",
        "kind": "experiment_landed_vet",
        "cert_status": "measured_mechanism",
        "cert_class": ("settling_mechanism_rehabilitated_graded_regime_exists_static_codebook_beta_3p0_multistep_"
                       "96of96_HF1_HF4_clear_NOT_codebook_collapse_BUT_residual_of_change_readout_refuted_rho_"
                       "neg0p128_loses_to_static_G3_0p625_HARD_FAIL_3_brain_consistent_fixed_codebook_no_per_"
                       "instance_plausibility_SAME_WALL_affectedness_MM_cpcl_forensic_redirect_fix3_trained_"
                       "energy_function_or_grounding_NOT_beta_tuning"),
        "plain_language": PLAIN,
        "importance": IMPORTANCE,
        "description": (ATOM_CLAIM + "\n\nPLAIN LANGUAGE: " + PLAIN + "\n\nRECOMPUTE (off-disk .venv, Fix #28): "
                        + ATOM_RECOMPUTE + "\n\nHONEST SCOPE + BRAIN-CHECK + REDIRECT: " + ATOM_SCOPE),
        "aliases": [
            "settling-fix learned-recurrent v1 (MEASURED_MECHANISM)",
            "settling mechanism rehabilitated: graded regime exists for static PPMI codebook, beta_c~3, 96/96 multi-step",
            "residual-of-change readout refuted: rho -0.128, loses to static thematic-fit G3 0.625 (HARD_FAIL_3)",
            "HF1 pinned + HF4 refit-to-ceiling BOTH clear: NOT the codebook-collapse structural limit",
            "same wall as affectedness-MM + CPCL forensic: fixed distributional codebook encodes no per-instance plausibility",
            "brain-check: N400 residual informative only via trained recurrent weights; redirect fix-3 trained energy function or grounding",
            "amends parent settling_parse_selector HF: residual-pinning leg was a beta artifact, readout-null leg is the real bound",
        ],
        "ts_iso": _iso, "ts": _ts,
        "serves_capability": "learning_and_self_monitoring_layer_graded_coherence_trace_readout_bound",
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_gate_arithmetic_recompute_from_per_arm_aggregates_"
                                   "all_8_HP_HF_gates_reproduce_exact_plus_internal_consistency_plus_referent_"
                                   "audit_parent_HF_and_affectedness_cpcl_ids_verified_offdisk_no_raw_"
                                   "trajectories_stored_so_gate_recompute_is_the_verification_basis"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "amends_atom_id_prefix": PARENT_SETTLING_HF,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/settling_fix_learned_recurrent_v1/metrics.json",
            "prereg_path": "preregs/2026-07-20_settling_fix_learned_recurrent_v1.md",
            "drill_path": "notes/research_brain_learned_recurrent_settling_sentence_gestalt_2026-07-20.md",
            "plain_language": PLAIN, "importance": IMPORTANCE,
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "hf_attribution": ("HF_STRUCTURAL_BOUND (not HF_TEST_DESIGN_FAILURE). Positive control clears its "
                               "own floor: static G3=0.625 > chance 0.5 proves the item set carries real "
                               "plausibility signal; the beta-grid is genuinely sensitive (0.542-0.667) proving "
                               "the settling machinery is live and CAN discriminate. So the residual readout's "
                               "null is a genuine substantive property of the residual-of-change readout over a "
                               "fixed distributional codebook, not a dead/degenerate test."),
            "brain_check": ("CONFIRMED brain-consistent. Rabovsky/Hansen/McClelland 2018 Sentence-Gestalt "
                            "N400-residual is informative ONLY because the recurrent WEIGHTS are TRAINED on "
                            "graded comprehension (no one-hot target; shift of labour activation->weights). Our "
                            "settling runs over a FIXED PPMI/SVD codebook that encodes distributional "
                            "co-occurrence, not per-instance plausibility -- a dynamic surfaces only REPRESENTED "
                            "signal, cannot manufacture absent signal. The brain solves it DIFFERENTLY (train "
                            "the weights on a comprehension signal); that mechanism IS the redirect (fix-3). "
                            "Same wall as affectedness-MM + CPCL forensic."),
            "p_hack_check": ("NONE. HP/HF bands byte-verbatim from the drill's Falsifiable-predictions and match "
                             "cell gate code exactly (recomputed). The only pre-reg/impl discrepancy is the "
                             "FIT-split tie-break rule (pre-reg 'smallest beta' vs cell 'largest FIT margin among "
                             "accuracy-tied betas'), documented in _fit_beta as a mid-smoke authoring-bug "
                             "correction; it biases TOWARD discrimination/pass, was fixed before the full run, "
                             "and C STILL failed with its best-margin beta -- exculpatory, not a fail-ward hack. "
                             "HF3 reported explicitly, not silently re-tuned."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "every_negative_check_how_the_brain_does_it_proactively_USER",
                "positive_control_must_clear_its_own_floor_before_trusting_a_negative",
                "HF_structural_bound_vs_test_design_failure_attribution",
                "construction_proof_not_capability_win_do_not_inflate_plumbing",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "clean_negative_do_not_relitigate_confirm_tier_interpretation_brain_check_and_bank",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


def ledger_row(atom):
    return {
        "op": "cert_ruling", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "supersedes_atom_id": None, "amends_atom_id_prefix": PARENT_SETTLING_HF,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "author_verdict": "HARD_FAIL_3_GRADED_BUT_NOT_MEANINGFUL",
        "verdict": ("MEASURED_MECHANISM_settling_mechanism_REHABILITATED_graded_regime_exists_beta_3p0_multistep_"
                    "96of96_HF1_HF4_clear_NOT_codebook_collapse_BUT_residual_of_change_readout_REFUTED_rho_neg0p128_"
                    "loses_to_static_G3_0p625_beats_random_D_only_plus0p083_below_0p10_bar_HARD_FAIL_3_CONFIRMED_"
                    "all_8_gates_recompute_exact_offdisk_HF_STRUCTURAL_BOUND_positive_control_G3_above_chance_test_"
                    "live_brain_consistent_fixed_codebook_no_per_instance_plausibility_SAME_WALL_affectedness_MM_"
                    "cpcl_forensic"),
        "cert_increment_delta": 1,
        "decision": (
            "MEASURED_MECHANISM. Author verdict HARD_FAIL_3 CONFIRMED off-disk (.venv, Fix #28: all 8 HP/HF gates "
            "recompute EXACT from the per-arm aggregates -- oom_C=1.0483 via log10(8.338e-9/7.461e-10), HF3=True, "
            "HF1/HF2/HF4=False, every HP except HP4=False). TWO-FACED clean full-power negative. (1) MECHANISM "
            "REHABILITATED (bounded positive residue): damped-step + grid-fit effective-beta restored a graded, "
            "multi-step, beta-sensitive settling regime over the same static PPMI/SVD codebook the parent cell "
            "collapsed at beta=20 -- fitted_beta=3.0 (<<20), FIT grid peaks at beta 2-3 and degrades to the "
            "ceiling, C converges 96/96 multi-step, oom_C=1.05 above the fresh floor, and DECISIVELY HF1 (pinned "
            "at floor) AND HF4 (beta refits to ceiling) BOTH stayed clear -> the graded regime EXISTS for this "
            "codebook (beta_c~3), refuting the drill's biggest deflation risk (P=0.40 that beta_c sits above 20); "
            "this is NOT the codebook-geometry structural limit. (2) READOUT REFUTED (the clean negative): the "
            "rehabilitated residual-of-change readout carries no per-instance plausibility signal -- C EVAL rho "
            "-0.128 (null), C EVAL acc 0.583 LOSES to static thematic-fit G3 0.625, beats random-recurrent D by "
            "only +0.083 (<0.10 bar). ATTRIBUTION HF_STRUCTURAL_BOUND not test-design failure: positive control "
            "clears its floor (G3=0.625>chance; beta-grid genuinely sensitive -> test is LIVE). NO P-HACK: bands "
            "byte-verbatim from the drill; the mid-smoke tie-break fix biases toward a pass and C still failed. "
            "BRAIN-CHECK CONFIRMED: N400 residual is informative only because trained recurrent weights encode "
            "the signal; our fixed codebook encodes distributional co-occurrence not per-instance plausibility, "
            "and a dynamic cannot manufacture absent signal -- SAME WALL as the affectedness-MM and CPCL forensic "
            "(text-internal signal over a distributional codebook does not track per-instance thematic "
            "correctness). REDIRECT: fix-3 (trained similarity/energy function on coherent-vs-corrupted pairs) or "
            "grounding, NOT more beta/damping tuning (regime works) and NOT codebook reconstruction (HF1 clear). "
            "Counts toward CERT as a proven boundary (+1 MM). Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed this as a clean full-power HARD_FAIL_3 (mechanism rehabilitated, readout carries no "
            "parse-plausibility signal) and asked me to confirm tier + interpretation + brain-check, not "
            "re-litigate. CONFIRMED on all counts, with two framing refinements (symmetric): (i) I tier the "
            "landing MEASURED_MECHANISM rather than bare HARD_FAIL, so the REAL mechanism sub-win (the graded "
            "regime EXISTS -- HF1+HF4 both clear -- which refutes the drill's structural-collapse fear) is banked "
            "as a proven bound and reusable component, not discarded; the readout refutation stays clean. "
            "(ii) This AMENDS (not supersedes) the parent settling_parse_selector HF: its residual-pinning leg "
            "was a beta=20 ARTIFACT (modest upward correction -- not the structural collapse it implied), while "
            "its readout-null leg is the real structural bound, now confirmed more robustly at the rehabilitated "
            "graded regime. The cell AUTHOR is CREDITED for a clean honest full-power negative (bands verbatim, "
            "must-fail control fires, arms-differ on raw trajectories, HF3 explicit, tie-break fix documented and "
            "pass-biased). Brain-check + same-wall-as-affectedness/CPCL cross-arc connection CONFIRMED accurate. "
            "Do NOT inflate the mechanism plumbing into a coherence-readout capability."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 MM (proven boundary: settling MECHANISM rehabilitated -- graded multi-step "
                           "beta-sensitive regime exists for the static codebook, HF1+HF4 clear, NOT the "
                           "codebook-collapse structural limit -- while the residual-of-change READOUT is refuted "
                           "as a parse-plausibility signal, rho null and losing to static G3. Brain-consistent "
                           "(fixed codebook encodes no per-instance plausibility); SAME WALL as affectedness-MM "
                           "and CPCL forensic. Redirect = fix-3 trained energy function or grounding)."),
        "supersedes": None,
        "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": atom["id"],
    }


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    atom = build_atom()
    ledger = ledger_row(atom)
    print("=== A5 atom-write: settling_fix_learned_recurrent_v1 -> MEASURED_MECHANISM (mechanism rehabilitated, readout refuted) (2026-07-20) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id/id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store:", atom["id"]); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True; no origin push; no remote persist) ===")
    print("ATOM (MEASURED_MECHANISM):", atom["id"][:120], "...")


if __name__ == "__main__":
    main()
