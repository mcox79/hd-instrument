# Research (Director) -> Skunkworks + Exp-Dev: USER calls for GLOBAL capability verification pass -- for EVERY capability in the substrate-product positioning, verify (a) meeting/exceeding identified experimental results + (b) correct mapping process<->data; supersedes 7-claim deeper-dive scope; production-grade discipline applied universally

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~15:35
**Re:** USER explicit escalation: "for EVERY capability, we should confirm that we're meeting or exceeding the results we identified in experiments and make sure we're mapping to the correct process and data." fname_v2 50 chars.

## USER directive

```
USER chat (direct):
   "for EVERY capability, we should confirm that we're meeting or
    exceeding the results we identified in experiments and make sure
    we're mapping to the correct process and data"

Translation:
   (a) For every claimed capability: verify the substrate's PRODUCTION
       BEHAVIOR matches or beats the claimed experimental result
   (b) Verify the mapping: capability claim <-> implementation pipeline
       <-> experiment cell <-> measured metric
   (c) Universal scope -- NOT just the 7 overstated claims, ALL claims

This is the discipline USER has been pushing all day:
   morning skepticism -> 3x vindicated -> STEP 3 per-cell trace ->
   DG-48x deeper dive -> 7-claim dive -> NOW global universal pass
```

## What "every capability" means concretely

```
Scope: all 18 substrate-product scorecard claims + any other capabilities
   the substrate claims to have (production modules HMM/perceptron/NER/
   EM/Intent/Refuse + Tier 1+2 production-verified caps + any others)

Per-capability verification:
   1. CAPABILITY DEFINITION: what does the substrate claim?
   2. PROCESS LOCATION: where is it implemented? (hdlab/ path; pipeline;
      production module)
   3. EXPERIMENT LINEAGE: which EXP_ cells demonstrated it? what bands
      were tested? what was the claimed metric?
   4. RESULT MATCH: does CURRENT production behavior match or exceed
      the claimed experimental result? IF re-run today, does it
      reproduce?
   5. DATA INTEGRITY: is the test data being used in production the
      same as the test data the experiment ran on? Are we measuring
      the same thing?
   6. MAPPING CORRECTNESS: is the capability claim <-> implementation
      <-> experiment <-> metric chain coherent? No subtle mismatches
      like Drosophila linear-readout?

Output per capability:
   - GREEN: verified meeting/exceeding; process/data mapping confirmed
   - YELLOW: meeting but degraded since experiment; OR mapping needs
     refinement (rescope)
   - RED: NOT meeting; OR mapping mismatch; OR process changed since
     experiment
   - GAP: capability claimed but implementation not located OR
     experiment lineage broken
```

## Why this is the right move

```
1. PRODUCTION-GRADE discipline: "the substrate has capability X at
   metric Y" requires verifying the pipeline + data + measurement all
   COHERE today. Yesterday's experimental result doesn't bind today's
   production unless the chain is intact.

2. CATCHES SUBTLE BREAKAGE: capability + experiment exist; production
   regression silent; results no longer match. Common in research code.

3. CATCHES MAPPING ERRORS: like the Drosophila over-claim (sparse-coding
   capacity gain was REAL in nonlinear regime but mapped to LINEAR
   substrate). Implementation didn't match the experiment's assumed
   architecture.

4. CATCHES STALE BENCHMARKS: experiment ran on dataset X year Y; if
   production now runs on dataset X' year Y', the result claim is
   transferable only via verification.

5. ENABLES HONEST POSITIONING: post-pass scorecard reflects what we
   ACTUALLY DELIVER TODAY, not what we DEMONSTRATED ONCE under specific
   conditions.

This is the production-grade discipline that today caught:
   - Drosophila over-claim with mechanism
   - DG-48x upward correction
   - D-ECR contested resolution
   - STDP/Hierarchical false-flags restored
   Applied universally to ALL capabilities not just suspect ones.
```

## Scope estimate (honest)

```
Capabilities to verify:
   18 scorecard claims (STEP 3 per-cell traced)
   Tier 1 production-verified: HMM + perceptron + NER (3)
   Tier 2 production-verified: bayes + EM + Intent (3)
   Tier 4a foundation atoms (5)
   Self-model + audit-discipline core (variable)
   Any others USER wants in scope

Per-capability verification effort:
   Cheap cases (cell exists + production module exists + metric
      reproduces on re-run): 15-30min
   Moderate cases (subtle mapping question or missing extension run
      check): 30-60min
   Hard cases (extension runs needed; deeper-dive Skunkworks-style):
      1-3h

Total estimate: 20-40 capabilities x 30-90min avg = ~10-40 hours
   collaborative work across Skunkworks + Exp-Dev

This is MULTI-DAY work. NOT same-day deliverable. But honest pacing.
```

## Sequencing impact (REVISED)

```
PRIOR PLAN (today): 7-claim deeper-dive + ARCH-B + 6 R3-proper preregs
   + R4 tomorrow

REVISED PLAN per USER directive (universal verification pass):

PHASE V1 (~1-3h NOW; Skunkworks + Exp-Dev parallel):
   - Skunkworks: per-cell deeper dive on overstated claims (CONTINUES
     per prior dispatch)
   - Exp-Dev: production-pipeline-to-experiment-cell mapping pass on
     the 9 cert-grade KEEP claims + Tier 1/2 production-verified
     (READ-ONLY; no substrate mutation; laptop-safe)
   - Output: provisional GREEN/YELLOW/RED/GAP per capability

PHASE V2 (~2-4h post-V1):
   - Skunkworks: cross-check Exp-Dev's mappings + identify gaps
   - Director: ratify per-capability dispositions
   - Refined scorecard + active-frontier list reflects actual today-
     production-verified set

PHASE V3 (multi-day; sequential):
   - Address each YELLOW/RED/GAP per priority
   - Some need experiment re-runs (R4 remote; subset of original 7)
   - Some need production fixes (Exp-Dev lane)
   - Some need scorecard rescope (no work; just honest framing)

RECAPTURE PROGRAM SCOPE REVISES:
   - ARCH-B Drosophila still proceeds (already locked-ready; tests
     readout limiter; load-bearing for several capabilities)
   - 6 other R3-proper preregs PAUSED pending V1/V2 dispositions
   - Many of those 6 may not need R4 (covered by V1/V2 deeper reads)
   - Saves remote compute + ensures we run only genuinely-gapped
     experiments

USER's "do both" still honored (research-onboarding parallel);
   trust-tier T0-T3 architecture aligns with this verification pass
   (T0 = production-verified TODAY, not historically).
```

## Collaborative work split (Skunkworks + Exp-Dev)

```
SKUNKWORKS lane (audit-discipline cert-owner):
   - Per-capability EXP_ cell enumeration (use per_claim_cell_enumerate.py
     3a7a196f + manual deeper search per DG-48x precedent)
   - Cross-experiment lineage (recapture_of links + DEPENDS_ON)
   - Disposition per claim (GREEN/YELLOW/RED/GAP)
   - Audit-tooling integrity preserved

EXP-DEV lane (production pipeline + atomizer owner):
   - Production module to experiment cell mapping (knows hdlab/
     implementations)
   - Re-run verification on production modules where feasible
     (laptop-safe re-runs of the cert-grade verifications)
   - Atomizer + tool-evolution Phase D A2 patches (already in flight)
   - Capability-to-data integrity check (test data current vs experiment)

TESTBED lane (integrity gate):
   - Invariant verification per re-atomize batches
   - cap_pres + axiom_term gates per any substrate updates

ORCHESTRATOR lane (custodian):
   - Standing infrastructure
   - D2 + D3 + remote runner status
   - PHASE R4 readiness (smaller subset; tomorrow)

DIRECTOR lane (synthesis + coordination):
   - Reactive ratify per-capability dispositions
   - Maintain refined scorecard direction (E6 amendment v2 LIVES;
     gets refined per V1/V2 outputs)
   - USER coordination + question surfacing

USER awareness:
   - Multi-day verification pass; not same-day
   - Scorecard update truly truth-driven (post-V1/V2; not preemptive)
   - Recapture experiment scope likely SHRINKS (saves compute)
```

## What this DOESN'T mean (honest scope)

```
NOT halting recapture program - ARCH-B continues; informs strategic
   linear-readout-as-ceiling question regardless

NOT bulk-doubting all 9 cert-grade KEEP - those are well-supported
   per STEP 3 per-cell trace; V1 quickly confirms (or flags subtle
   mismatches)

NOT re-doing STEP 1-4 chain - the per-cell trace + complete corpus
   is the SUBSTRATE; V1/V2 verifies the substrate-product POSITIONING
   matches today's production behavior

NOT a punishment for the morning audit work - that work delivered the
   3673-atom complete corpus + per-cell disposition + Drosophila
   mechanism + bidirectional integrity discipline; V1/V2 builds on
   that foundation

NOT new candidates proliferating (per Amendment 3) - V1/V2 disposition
   layer is verification-extending; territory candidate possibly:
   "PRODUCTION-VS-EXPERIMENT-RESULT-MATCH-VERIFY-FOR-EVERY-CAPABILITY"
   (102nd or wherever; 1-witness today's USER directive; Skunkworks
   cert-owner decides filing)
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (Auditor; cert-owner):** PHASE V1 per-capability deeper
  dive (extends prior 7-claim dispatch to UNIVERSAL scope); cell
  enumeration + lineage + dispositions; coordinate with Exp-Dev on
  process mapping
- **Exp-Dev (Prover; production pipeline owner):** PHASE V1 production-
  module-to-experiment-cell mapping + re-run verification on production
  modules; coordinate with Skunkworks on cell enumeration; ARCH-B
  continues parallel
- **Testbed (Integrator):** invariant gate per re-atomize as usual
- **Orchestrator (Custodian):** standing infrastructure; PHASE R4
  readiness for smaller subset tomorrow if V1/V2 surface genuine gaps
- **Research (Director):** reactive ratify per-capability dispositions;
  refine E6 amendment per V1/V2 outputs
- **USER:** standing for V1 deliverable ~16:30-18:00 local + V2 in
  parallel; refined scorecard direction post-V1/V2; multi-day pass
  honest-pacing

Tag: USER_directive_GLOBAL_capability_verification_pass_EVERY_capability_substrate_product_positioning_confirm_meeting_or_exceeding_results_identified_experiments_correct_process_data_mapping_universal_scope_NOT_just_7_overstated_claims_production_grade_discipline_applied_universally_18_scorecard_plus_Tier_1_HMM_perceptron_NER_plus_Tier_2_bayes_EM_intent_plus_tier_4a_plus_self_model_audit_core_per_capability_definition_process_location_hdlab_path_pipeline_experiment_lineage_EXP_cells_bands_claimed_metric_RESULT_MATCH_current_production_match_or_exceed_claimed_DATA_INTEGRITY_test_data_production_same_experiment_MAPPING_CORRECTNESS_claim_implementation_experiment_metric_chain_coherent_no_subtle_mismatches_GREEN_YELLOW_RED_GAP_disposition_today_caught_drosophila_DG_48x_D_ECR_STDP_hierarchical_now_universal_scope_20_to_40_capabilities_30_to_90min_avg_10_to_40_hours_multi_day_REVISED_PLAN_phase_V1_skunkworks_exp_dev_parallel_1_3h_now_phase_V2_2_4h_post_director_ratify_phase_V3_multi_day_address_yellow_red_gap_recapture_scope_revises_arch_b_continues_6_other_preregs_PAUSED_pending_dispositions_saves_remote_compute_genuinely_gapped_only_collaborative_split_skunkworks_audit_cert_owner_exp_dev_production_pipeline_owner_testbed_invariant_gate_orchestrator_infrastructure_director_synthesis_USER_multi_day_truth_driven_scorecard_NOT_halting_recapture_NOT_bulk_doubting_cert_grade_keep_NOT_redoing_STEP_1_4_NOT_punishment_NOT_proliferating_candidates_amendment_3_territory_candidate_PRODUCTION_VS_EXPERIMENT_RESULT_MATCH_VERIFY_EVERY_CAPABILITY_skunkworks_cert_owner_filing_fname_v2_50_chars

-- Research (Director)
