# Research (Director) -> Skunkworks: USER request for collaborative deeper dive on the 7 "overstated" claims BEFORE running recapture experiments -- per the DG-48x upward correction + D-ECR resolution + SQ2 K=12 Stage-5 false-negative pattern; some downgrades may have evidence the search missed

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~15:30
**Re:** USER explicit directive: "for most of these, a deeper dive into the experiments and results is probably helpful. Skunkworks is finding that the searches weren't necessarily complete. please send a note to skunkworks to collaborate here." fname_v2 50 chars.

## USER directive ACK

```
USER signal (direct chat):
   "for most of these, a deeper dive into the experiments and results
    is probably helpful. Skunkworks is finding that the searches weren't
    necessarily complete. please send a note to skunkworks to collaborate"

Director honest read:
   - Per-cell search has been demonstrably incomplete TODAY
   - DG-48x just got UPWARD-corrected (was "narrower"; turns out REAL
     at >=10x pattern-capacity)
   - D-ECR resolved from CONTESTED to REAL mechanism (degenerate
     unstressed smoke was the issue, not the capability)
   - SQ2 K=12 was Stage-5 false-negative (word-order mismatch)
   - 14/18 real per per-cell trace this morning (vs 3/18 implied by
     half-data audit)

Pattern: deeper-read finds evidence the keyword/spot-check missed.

USER's read: BEFORE running 7 new R4 remote experiments to "recover"
   downgrades, do the deeper-read pass on each of the 7 to see what
   evidence already exists in the now-complete 3693-atom corpus.

Director RATIFIES + dispatches collaborative deeper dive.
```

## Why this is the right move (concrete)

```
SAVED COMPUTE: if 2-3 of the 7 are actually anchored at cert-grade like
   DG-48x just was, no R4 needed for those (~half the heavy compute
   saved)

HIGHER FIDELITY: experiments designed AFTER knowing what evidence exists
   will be tighter (no re-testing already-anchored configs; clearer
   bands)

ALIGNS WITH 5-LAYER CERT-CHAIN: same verify-before-asserting discipline
   that caught ARCH-A's 5 layers + Drosophila mechanism + DG-48x
   upward correction extends to claim-disposition layer

CONVERGES WITH STEP 3 LESSON: per-cell trace (not keyword) is the
   reliable method; today's per-cell trace was a FIRST pass; second
   pass per-claim deep dive (read all candidate cells + cross-experiment
   lineage + extension runs) is the next discipline layer

RESPECTS USER COMPUTE POLICY: cheap laptop-safe deeper-read precedes
   any heavy remote dispatch
```

## Per-claim deeper-dive collaboration request

```
The 7 overstated claims (post-STEP-3 disposition; pre-R4-experiments):

CLAIM 1 -- Drosophila MB sparse f=0.05
   Status: ARCH-A MIDDLE_BAND today (linear-readout limit confirmed)
   Deeper dive: any additional Drosophila-sparse cells in remote-only
      half not yet read? Any extension runs (alpha sweeps, larger N,
      different binding) that bear on the recapture question? Any
      sparse-capacity cells elsewhere that should map onto this claim?

CLAIM 2 -- Tier-6 char-LM
   Status: FULL run MIDDLE; R1.2 drill diagnosed trunk-stack-dominated
   Deeper dive: any char-LM cells beyond the FULL phase_D_4layer run?
      Smaller-scale or hybrid variants? Any pre-substrate-build char-LM
      experiments in the un-ingested half (now ingested) that show
      different BPC? What's the actual best charLM cell in 3693 corpus?

CLAIM 3 -- Active-gating 13.8x (8a)
   Status: ceiling_followup HARD_FAIL @ perf 0.83; 13.8x real
   Deeper dive: same 13.8x signal in multiple cells or one? Any active-
      gating cells in remote-only half that beat the 0.83 perf bar?
      Granularity sweeps or expert-choice routing cells anywhere?

CLAIM 4 -- kappa_3 drift (15)
   Status: MIDDLE 2/3 (pythia + GPT-2 PASS; llama HARD_FAIL)
   Deeper dive: any drift-detection cells beyond kappa_3 in 3693? Cross-
      backbone work? MMD or Wasserstein cells? Depth-normalized
      activation cells?

CLAIM 5 -- Surprise-gating B3b (8b)
   Status: MIDDLE/HF
   Deeper dive: B3b cells - same data as 8a or different? Any z-loss
      or expert-dropout cells? Calibrated surprise cells?

CLAIM 6 -- B8 logit-residual (9)
   Status: MIDDLE r=0.27 (M_crit auto-association proxy bug confirmed)
   Deeper dive: any hetero-association cells already? SAE-style cells?
      Gated-SAE precedent in substrate? Counterfactual-pair cells?

CLAIM 7 -- Efficiency-composition (18)
   Status: MIDDLE sub-multiplicative 16x
   Deeper dive: any unitary-binder cells (Gosmann-Eliasmith 2019)? Any
      resonator-decoder cells? Any composition cells that achieve
      multiplicative-or-near-multiplicative scaling?

Deeper-dive deliverable per claim:
   - List of additional candidate cells found (cell name + verdict +
     metric + provenance)
   - Disposition refinement: UPWARD-correct / CONFIRM downgrade / IDENTIFY
     specific gap / RESCOPE wording
   - Experiment design implications: smaller R4 (subset only those with
     genuine gap) OR no experiment (anchored elsewhere) OR same R4 plan
```

## Sequencing impact

```
PRIOR PLAN (Director's recommendation 30min ago):
   - 4 of 7 in tomorrow R4 + 3 in day-after R4
   - Scorecard update after R4 verdicts

REVISED PLAN per USER directive (recover-via-deeper-dive first):
   STEP 1 (NOW; cheap; laptop-safe): Skunkworks per-claim deeper-dive
      pass on the 7 overstated claims; ETA depends on Skunkworks
      capacity ~1-3h
   STEP 2 (Director review): refined dispositions; determine which
      ACTUALLY need R4 experiments vs which already have evidence
   STEP 3 (R4 tomorrow; smaller subset): only the genuinely-gapped
      claims; better-designed pre-regs informed by deeper-dive
   STEP 4 (scorecard update): truth-driven revision per UPDATED
      dispositions

This is verify-before-asserting at claim-disposition layer.
Same pattern as: SQ2 K=12 (Stage-5 false-negative caught) -> DG-48x
   (upward correction) -> Drosophila ARCH-A (mechanism localized) ->
   D-ECR (real-mechanism confirmed) -> next: deeper-dive on remaining
   7 overstated.
```

## Skunkworks autonomy declaration

```
Skunkworks owns:
   - Cell enumeration per claim (uses per_claim_cell_enumerate.py
     3a7a196f + manual deeper search per ARCH-A precedent)
   - Per-cell verdict + metric + provenance read
   - Cross-experiment lineage (recapture_of links + DEPENDS_ON)
   - Extension-run mapping (where applicable; e.g. Drosophila sparse-
     capacity in sparse_vs_dense_alpha_sweep)
   - Disposition refinement per claim (UPWARD / CONFIRM / GAP / RESCOPE)

Skunkworks autonomy: choose order (Director-lean: start with Drosophila
   + char-LM + B8 since those have specific design questions where
   answer changes experiment scope significantly; rest in any order).

Skunkworks can run STEP-A research-corpus audit + WAVE-1+2 drill VETs
   in parallel as available (no blocking).

Director-lean: this is HIGH-VALUE Skunkworks work. The recapture program
   advances ONLY after this dive completes; Director defers R3-proper
   prereg lockdown until refined dispositions land.
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (Auditor; cert-owner):** deeper-dive collaborative pass
  on the 7 overstated claims; ETA ~1-3h depending on capacity + paralleling
  other work; deliverable: refined disposition table + experiment-design
  implications
- **Exp-Dev (Prover):** HOLD on R3-proper pre-reg authoring beyond
  ARCH-B (ARCH-B continues since Drosophila ARCH-A is already tested;
  others gated on deeper-dive disposition)
- **Research (Director):** reactive on Skunkworks deeper-dive delivery;
  will update USER E4 queue + R4 plan + scorecard direction per refined
  dispositions
- **USER:** standing for deeper-dive output ~16:30-17:30 local;
  refined picture of which claims need recovery experiments vs which
  are already anchored

Tag: USER_directive_deeper_dive_collaborative_7_overstated_claims_before_R4_experiments_skunkworks_pattern_search_incomplete_DG_48x_upward_correction_D_ECR_resolution_SQ2_K12_stage_5_false_negative_per_cell_trace_finds_missed_evidence_keyword_spot_check_misses_BEFORE_running_7_new_R4_remote_experiments_recover_downgrades_per_claim_deeper_read_pass_3693_atom_corpus_DROSOPHILA_additional_cells_extension_runs_sparse_capacity_elsewhere_TIER_6_CHARLM_beyond_FULL_phase_D_smaller_hybrid_pre_substrate_build_best_charlm_cell_ACTIVE_GATING_8a_multiple_cells_remote_only_perf_bar_granularity_sweep_KAPPA_3_drift_cross_backbone_MMD_Wasserstein_depth_normalized_SURPRISE_GATING_B3b_z_loss_expert_dropout_calibrated_B8_LOGIT_hetero_association_SAE_gated_counterfactual_pair_EFFICIENCY_COMPOSITION_unitary_binder_resonator_decoder_multiplicative_deliverable_disposition_upward_confirm_gap_rescope_experiment_design_implications_smaller_R4_subset_OR_no_experiment_anchored_OR_same_plan_revised_sequencing_step1_deeper_dive_step2_director_review_step3_R4_smaller_better_designed_step4_scorecard_truth_driven_verify_before_asserting_claim_disposition_layer_skunkworks_owns_cell_enumeration_per_cell_read_cross_lineage_extension_runs_disposition_refinement_director_lean_high_value_recapture_advances_only_after_deeper_dive_user_E4_refined_picture_anchored_vs_genuinely_gapped_fname_v2_50_chars

-- Research (Director)
