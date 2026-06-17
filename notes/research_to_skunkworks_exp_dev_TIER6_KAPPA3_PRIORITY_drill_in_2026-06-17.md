# Research (Director) -> Skunkworks + Exp-Dev + All sessions: USER directive PRIORITY Tier-6 char-LM + kappa_3 drift -- drill in and prove them out FIRST; ARCH-B continues as Tier-6's paired strategic experiment (shared nonlinear-readout lever); other tracks lower priority

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~16:00
**Re:** USER directive (chat): "go on all. it seems like tier 6 char LM and kappa_3 are the most important. let's drill in on those and prove them out with priority." fname_v2 50 chars.

## USER directive ACK + priority push

```
USER signal (direct chat):
   "go on all. it seems like tier 6 char LM and kappa_3 are the most
    important. let's drill in on those and prove them out with priority"

Director honest read:
   - ACK my R4 3-track plan ("go on all")
   - PRIORITIZE: Tier-6 char-LM + kappa_3 are most important
   - DRILL IN on those two with priority

USER's priority signal ALIGNS with Skunkworks's importance ranking:
   - Tier-6 char-LM = TIER 1 FRONTIER (substrate-AS-LM-with-audit
     paradigm)
   - kappa_3 reframed = TIER 1b DIFFERENTIATOR (audit/safety pillar)
   - Both have load-bearing strategic significance

USER is reinforcing strategic priority. Director updates execution
   focus accordingly.
```

## PRIORITY EXECUTION ORDER (updated)

```
PRIORITY 1 (top focus; "drill in" per USER):

   PRIORITY 1A: Tier-6 char-LM R3-proper prereg
      - Lead: Exp-Dev (R3 framework + R1.2 drill 5 anchors)
      - Composes with: ARCH-B Drosophila (shared nonlinear-readout lever)
      - 5 anchors per R1.2 drill:
        1. vanilla trunk-stack (decisive trunk-vs-HD-seam test)
        2. length-curriculum
        3. HD-as-chunk-pooler (architectural reposition)
        4. resonator-decoder auxiliary loss
        5. N-sweep / binding-variant rescue
      - Trunk-stack diagnosis: ~2.5 BPC gap from SOTA likely trunk-
        stack-dominated NOT HD seam
      - Deeper-dive per USER: also explore (a) does substrate have
        any prior BPC-improving cells in 3699 corpus that should
        inform design? (b) recapture-of provenance fields per ARCH-A
        precedent
      - SCHEMA-VET pipeline: Skunkworks Ask 1-N
      - Compute: HEAVY -> R4 remote tomorrow (Day 1)
      - ETA: prereg draft tonight; SCHEMA-VET tomorrow morning; R4
        run tomorrow

   PRIORITY 1B: kappa_3 reframed R3-proper prereg
      - Lead: Exp-Dev (R3 framework + R1.4 drill diagnosis)
      - DIAGNOSIS (drill R1.4): kappa is label-coupled NOT rep-coupled
        (explains llama HARD_FAIL); fix = depth-normalized activations
        + MMD/Frechet two-sample test
      - REFRAME: test drift-detection CAPABILITY via robust metric
        (NOT rescue kappa_3 directly which is structurally backbone-
        fragile)
      - Candidate methods (P_deflated per drill):
        * MMD-on-depth-normalized (P=0.45; Gretton 2012 + Platonic
          Representation Hypothesis Huh 2024 + Layers-at-Similar-Depths
          2025)
        * Frechet-on-Procrustes-aligned (P=0.35)
        * LID-stability Tulchinskii 2023 (P=0.40)
      - Deeper-dive per USER: also explore (a) what backbone families
        the substrate currently runs on (b) cross-backbone activation
        extraction infra exists or needs building
      - SCHEMA-VET pipeline: Skunkworks Ask 1-N
      - Compute: HEAVY remote (multi-backbone activation extraction)
      - ETA: prereg draft tonight/tomorrow morning; SCHEMA-VET; R4
        Day 1 with Tier-6 OR Day 2 depending on capacity

   PRIORITY 1 SHARED: ARCH-B Drosophila (already LOCKED earlier today)
      - Composes with Tier-6 char-LM at the nonlinear-readout level
      - If ARCH-B HARD_PASS recapture: validates nonlinear-readout
        lift -> informs Tier-6 design (use same readout family)
      - If ARCH-B SPARSITY_NEUTRAL: still a real readout finding ->
        informs Tier-6 hybrid design
      - If ARCH-B HONEST_BOUNDED: next fork ARCH-C; Tier-6 charLM
        design narrows
      - ARCH-B verdict TODAY/TONIGHT informs Tier-6 design tomorrow

PRIORITY 2 (deprioritized per USER focus):

   PRIORITY 2A: efficiency-cluster (8a + 8b + 18) batched
      - Lead: Exp-Dev (3 R3-proper preregs batched as one track)
      - Tier-2 economics; capacity-management at scale
      - Honest bar: "good-enough efficiency"
      - Compute: HEAVY remote
      - ETA: R4 Day 2 OR Day 3 (deferred behind Tier-1)

PRIORITY 3 (skip):

   PRIORITY 3A: B8 logit-residual R4
      - SKIP per Skunkworks resolution (memory-recon NOT LM frontier)
      - Optional future quality-optimization phase

PHASE V1 GLOBAL VERIFICATION (continues parallel):
   - Exp-Dev: 5/6 modules GREEN exact-reproduction (just landed)
   - Skunkworks: 9-KEEP cert-grade per-claim enumeration MEDIUM
     priority under PROVE-6 VETs (now PROVE-2 priority VETs)
   - Converge at V2; Director ratifies dispositions
```

## DEEPER-DIVE BRIEFS FOR TIER-6 + KAPPA_3 (drill-in per USER)

```
TIER-6 CHAR-LM DEEPER DIVE (Skunkworks lane; supplements R1.2 drill):

   Verify-both-directions per today's symmetric discipline:
   - SEARCH for hidden wins: any cells in 3699 corpus with BPC < 3.62
     not yet identified? Variant char-LM experiments? Tokenizer
     variations? RoPE/ALiBi cells?
   - SEARCH for additional weakness signals: any partial char-LM
     cells with worse BPC that fold into the strategic question?
   - SEARCH for mechanism: any substrate-architecture cells (linear
     readout / nonlinear readout / hybrid attention) that bear on
     the design choice?
   - SEARCH for benchmarks: what SOTA char-LM baselines should the
     R4 target? Shakespeare BPC + enwik8 + per-character perplexity
     references?

   Output: refined R4 design with explicit benchmark targets +
     candidate cells informing each anchor choice.
   ETA: Skunkworks-paced; integrates with R3-proper SCHEMA-VET.

KAPPA_3 DRIFT DEEPER DIVE (Skunkworks lane; supplements R1.4 drill):

   Verify-both-directions:
   - SEARCH for any robust drift-detection cells in 3699 corpus
     (MMD/Wasserstein/depth-normalized/Procrustes-aligned/LID-based)
   - SEARCH for cross-backbone activation-extraction infrastructure
     in hdlab/ codebase
   - SEARCH for substrate's own deletion-cert + audit-preserving
     reasoning cells that might compose with drift detection
   - SEARCH for any backbone families substrate currently supports
     (pythia + GPT-2 + llama mentioned; what else?)

   Output: refined R4 design with infrastructure-readiness check +
     candidate-method ranking informed by 3699 corpus.
   ETA: Skunkworks-paced.
```

## V1 PROGRESS UPDATE (Exp-Dev just delivered)

```
Exp-Dev PHASE V1 increment 2 LANDED:
   - 5/6 production modules: GREEN exact-reproduction
   - 1 module: pending re-run OR YELLOW disposition (will check)

This is the discipline producing real results:
   - V1 increment 1: 50/2 cert suite + 6 module entry-points LIVE
   - V1 increment 2: 5/6 modules reproduce EXACT claimed metric

5 GREEN modules at exact-reproduction means:
   - HMM viterbi 0.9028 -> reproduces today on .venv
   - Perceptron 0.9149 -> reproduces today
   - NER 0.9307 -> reproduces today
   - EM 1.0 -> reproduces today
   - Intent 0.9125 OR Refuse-gated -> reproduces today

This is the "meeting or exceeding the results we identified" baseline
   USER asked for. 5 of 6 substrate production modules verified
   meeting claimed metrics TODAY. Substantive substrate-product
   positioning healthy at production layer.

Director ACK + standing for Exp-Dev next V1 increment + Skunkworks
   9-KEEP enumeration.
```

## SUBSTRATE STATE

```
atoms:               30044
relations:           6746
EXP_ atoms:          3699
CERT_CHAIN_GRADE:    561
axiom_term:          206/206 (PRESERVED)
cap_pres:            1.0 (PRESERVED; 6/6 modules)
methodology FROZEN:  24

V1 disposition (so far):
   GREEN: substrate core-algebra (50/2 cert) + 5/6 production modules
     reproducing exact claimed metrics
   LIVE: 6/6 entry-points
   PENDING: 1 module re-run + 9 cert-grade KEEP claim enumeration
     (Skunkworks)
   FOUND: 1 process-integrity gap (cert needs .venv; resolved)
   NO RED / NO GAP yet
```

## STANDING / who I'm waiting on (9th rule)

- **Exp-Dev (Prover):** PRIORITY 1A Tier-6 char-LM R3-proper prereg
  draft (TONIGHT) + PRIORITY 1B kappa_3 reframed prereg draft
  (TONIGHT/TOMORROW) + ARCH-B cell-author + smoke + FULL (laptop
  tonight) + V1 last module re-run
- **Skunkworks (Auditor; cert-owner):** ARCH-B per-band SCHEMA-VET +
  Tier-6 char-LM deeper-dive + R3-proper SCHEMA-VET + kappa_3 deeper-
  dive + R3-proper SCHEMA-VET (PRIORITY 1) + 9-KEEP enumeration
  (MEDIUM under PROVE-2 VETs) + ARCH-B result-VET
- **Testbed (Integrator):** standing for re-atomize invariant verify
  on PRIORITY 1 R4 verdicts
- **Orchestrator (Custodian):** PHASE R4 readiness TIER-1 PRIORITY
  (Tier-6 + kappa_3 + ARCH-B Day 1 + spillover Day 2 if needed)
- **Research (Director):** reactive on ARCH-B verdict + PRIORITY 1
  prereg LOCKs + V1 dispositions; standing for USER continued guidance
- **USER:** PRIORITY 1 focus locked in (Tier-6 + kappa_3); ARCH-B
  paired strategic; PRIORITY 2 efficiency-batch + PRIORITY 3 B8
  deprioritized per directive; substantive narrative landing post-
  R4 Day 1 + Day 2

Tag: USER_directive_PRIORITY_Tier_6_charLM_kappa_3_drift_drill_in_prove_first_R4_3_track_plan_REVISED_focus_priority_1_top_focus_tier6_R3_proper_prereg_exp_dev_R1_2_drill_5_anchors_vanilla_trunk_decisive_test_curriculum_HD_chunk_pooler_resonator_aux_loss_N_sweep_2p5_BPC_gap_trunk_stack_dominated_kappa_3_reframed_R1_4_drill_label_coupled_diagnosis_MMD_on_depth_normalized_Frechet_LID_robust_metric_NOT_rescue_backbone_fragile_REFRAME_ARCH_B_paired_shared_nonlinear_readout_lever_verdict_tonight_informs_tier6_design_tomorrow_priority_2_efficiency_batch_8a_8b_18_deferred_priority_3_B8_skip_memory_recon_PHASE_V1_5_of_6_modules_GREEN_exact_reproduction_HMM_0p9028_perceptron_0p9149_NER_0p9307_EM_1p0_intent_0p9125_OR_refuse_gated_substrate_product_positioning_healthy_production_layer_meeting_exceeding_baseline_skunkworks_9_KEEP_enumeration_MEDIUM_under_prove_2_VETs_deeper_dive_tier_6_search_hidden_wins_BPC_below_3p62_substrate_architecture_benchmark_targets_SOTA_baselines_kappa_3_search_robust_drift_cells_cross_backbone_extraction_infra_substrate_backbone_families_substrate_state_30044_6746_3699_561_206_206_cap_pres_1p0_methodology_24_frozen_directors_USER_continued_guidance_remaining_E4_carryover_research_onboarding_trust_tier_held_out_retrieval_E6_amendment_v2_fname_v2_50_chars

-- Research (Director)
