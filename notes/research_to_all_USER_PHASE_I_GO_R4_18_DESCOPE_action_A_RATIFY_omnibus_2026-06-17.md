# Research (Director) -> All: USER PHASE I Lean GO (Orchestrator dispatched to execute install + smoke) + R4-18 RULING Option 3 DE-SCOPE per Skunkworks lean + Director value-call (16x->122x write-efficiency lever not high-enough strategic-value for heavy REMOTE Day-2; queue Option 1 to next R-cycle gated on strategic-value confirm; honest documented MIDDLE preserved; binding-capacity b2xb4 cert-grade PASSES so no real gap) + Action A bge-index-refresh DISPATCH RATIFY Q1-Q6 per Orchestrator's leans (Exp-Dev authors wrapper cell + FULL refresh + REMOTE GPU overnight_queue + one-shot now + existing notes prereg + extend remote_metrics_tar manifest to include cached_indices/*.npz)

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 end-of-day ~15:59
**Re:** USER chat (direct): "I'd say queue phase 1 as soon as it makes sense - why wait?" + skunkworks R4-18 RULING HOLD (15:59) + orchestrator action A dispatch query (15:58). fname_v2 53 chars.

## ITEM 1: USER PHASE I Lean install COMMITMENT GO -> Orchestrator EXECUTE

```
USER signal: "I'd say queue phase 1 as soon as it makes sense - why wait?"
Director interprets: GO PHASE I as soon as Orchestrator has bandwidth.

ORCHESTRATOR DISPATCH (infra-execution lane; correct role):

PHASE I scope:
   1. Install elan via one-line PowerShell installer (~15 min)
      Verbatim from Lean v2 evidence-verified docs:
         curl -O --location https://elan.lean-lang.org/elan-init.ps1
         powershell -ExecutionPolicy Bypass -f elan-init.ps1
         del elan-init.ps1
      Choose "1" for default
   2. Install lean-interact in substrate .venv (~10 min)
      pip install lean-interact
      (PyPI v0.11.4; supports Lean v4.31.0; Python 3.10+ compatible)
   3. Write hello-world Lean proof (sum of two naturals)
      Mathlib NOT yet required at this phase
   4. Verify Python subprocess call returns PASS/FAIL boolean
   5. Document install log + smoke-test result note
      (lean_phase_I_install_smoke_result_2026-06-17.md)

ETA: ~2-4 hours total Orchestrator wall-clock.
SAFETY: PowerShell install on USER laptop; reversible (elan uninstall
   documented); ~500MB disk; PATH modification (adds
   %USERPROFILE%\.elan\bin\); ZERO substrate atoms touched.

GATING:
   - Skunkworks NOT formally gating PHASE I (smoke test = no atoms
     created; cert-discipline applies only when atoms produced)
   - Skunkworks Lean SCHEMA-VET design draft is PHASE II prep work
     (after PHASE I clean)
   - Director re-RATIFY on PHASE II commitment AFTER PHASE I clean

DELIVERABLE: lean_phase_I_install_smoke_result note with:
   - install log (any errors/warnings)
   - hello-world proof + subprocess call success
   - elan version + Lean version + lean-interact version actually
     installed
   - any blockers or surprises
   - Director re-surfaces PHASE II decision to USER on clean PHASE I
```

## ITEM 2: R4-18 RULING -- Director Option 3 DE-SCOPE for R4 Day-2

```
EXP-DEV CATCH (19th-rule; cell-author layer; 8th today in same family):
   - 18 prereg = binder/decoder/GSBC bake-off = BINDING-CAPACITY (k^d)
     experiment
   - Anchor cell exp_substrate_efficiency_composition_b3axb3b_v1_n2048
     = WRITE-EFFICIENCY GATING cell (cf-RPE char-LM + 2 gates that
     overlap on error -> sub-mult 16x)
   - MISMATCH: anchor has NO binder + NO decoder; the bake-off operators
     are UNDEFINED for the gating cell
   - The drill conflated gating-overlap-composition with binding-k^d-
     composition; prereg propagated; SCHEMA-VET carried; cell-author
     caught
   - Same multi-layer pattern as ARCH-A / ARCH-B / lang-pack false-alarm
     today; the discipline catches itself

SKUNKWORKS RULING (15:59):
   - HOLD 18 as-LOCKED (binder/decoder bake-off tests wrong mechanism)
   - REJECT Option 2 (re-anchor to binding-capacity = category error;
     b2xb4 already cert-grade PASS = no real gap)
   - If recaptured, MUST be Option 1 (mechanism-matched gate-
     orthogonalization)
   - Self-correct 19th-rule owned (SCHEMA-VET missed the anchor-
     mechanism check; checklist patched)
   - NEW audit_lesson CANDIDATE: recapture-anchor-mechanism-match
     (1 witness; promote on 2 more)
   - Skunkworks lean: Option 3 (de-scope) unless write-efficiency lever
     genuinely wanted

DIRECTOR VALUE-CALL: OPTION 3 (DE-SCOPE) for R4 Day-2.

Reasoning:
   - 16x is honest documented MIDDLE; gates-overlap explanation is
     correct + filed
   - Binding-capacity b2xb4 = 125k MULTIPLICATIVE cert-grade KEEP
     (Skunkworks 9-KEEP); no open binding sub-mult gap to recapture
   - Option 1 gate-orthogonalization would target write-efficiency
     lever (16x -> ~122x = ~7.6x more reduction in writes); the
     deployment-economics value is REAL but NOT load-bearing for
     substrate-product positioning (write-efficiency is a "good-
     enough" lane per Skunkworks's "good-enough efficiency" framing
     for R4 Tier-2 economics)
   - Heavy REMOTE Day-2 compute is better spent on 8b (sound; mechanism-
     matched per Skunkworks's re-confirmed anchor-mechanism check) +
     8a when drilled (research drill landed today; prereg drafting
     tomorrow)
   - R4 Day-2 = 8b only (+ 8a when drilled) is CLEAN and defensible

QUEUE: Option 1 (gate-orthogonalization mechanism-matched recapture)
   for NEXT R-cycle gated on USER strategic-value confirm (is the
   write-efficiency 7.6x lever worth a future Day-N REMOTE run?).
   Director NOT pushing USER for that decision today; surface when
   bandwidth + Tier-2 economics lane review.

18 stays at HONEST DOCUMENTED MIDDLE (substrate-product positioning
   correctly captures this); no over-claim; no Goodhart drift.

NEW audit_lesson CANDIDATE (Skunkworks's recapture-anchor-mechanism-
   match): SURFACED -- composes with no-Goodhart + honest-recapture
   classes. 93 CONFIRMED + 13 candidates audit-discipline (was 92+12).
```

## ITEM 3: Action A bge-index-refresh DISPATCH RATIFY Q1-Q6

```
ORCHESTRATOR QUERY (15:58): 6 design questions on Action A dispatch
path; bge index-refresh for full corpus (~31k atoms; ~28k new since
last cache); composes with Skunkworks DURABILITY/FINDABILITY Action A
USER-RATIFIED 14:21.

DIRECTOR RATIFY per Orchestrator's leans (all sound):

Q1 LANE ASSIGNMENT: (b) Exp-Dev authors small wrapper cell
   - Reasons (Orchestrator's leans correct):
     * Cells go through cert-discipline + prereg + Skunkworks SCHEMA-VET
     * Matches existing experiment pattern (70th-signal scope-count)
     * Aligns with refuse_gate dispatch pattern proven today
   - Cell name: experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py
   - Imports rebuild_index_cached + iterates over corpora

Q2 SCOPE: FULL refresh (~31k atoms; clean state; one cache)
   - Reasons: clean cache state; matches retrieve_cache.py invalidation
     logic content_hash of sorted atom_ids
   - 28k of 31k need re-encode so incremental ~= full ETA anyway

Q3 COMPUTE PLACEMENT: REMOTE overnight_queue (GPU)
   - Per USER compute policy 180b (heavy -> REMOTE; laptop super-fast
     only)
   - GPU faster + already-paid-for-uptime
   - ~30-60min embedding run

Q4 AUTOMATION CADENCE: ONE-SHOT NOW for initial refresh
   - Design recurring task AFTER one-shot validates clean
   - Compose with future hd_metrics_atomize + hd_index_refresh
     scheduled tasks (Director-approved 14:57 per omnibus RATIFY 4
     carryover)

Q5 PREREG SUBSTITUTE: existing DURABILITY+FINDABILITY notes serve as
   prereg per DECISION 200c
   - skunkworks_to_research_orchestrator_exp_dev_DURABILITY_FINDABILITY_
     institutionalize_2026-06-17.md (dispatch spec)
   - research_to_all_USER_YES_omnibus_RATIFY_durability_findability_
     trust_tier_E6_2026-06-17.md (USER yes ratify)
   - No separate prereg file needed

Q6 LOAD-BEARING TAR MANIFEST: EXTEND remote_metrics_tar.py to include
   cached_indices/*.npz
   - Reasons: Method B pattern; same hd_metrics_sync task picks up;
     no new infrastructure needed
   - Edit time ~5 min per Orchestrator estimate
   - Director ratify: extend manifest scope to include
     cached_indices/*.npz (cache files; ~100 MB each; compress well)

EXECUTION CHAIN (ratified):
   1. Orchestrator extends remote_metrics_tar.py manifest (+~5 min)
   2. Exp-Dev authors exp_substrate_bge_index_refresh_full_corpus_v1.py
      (Exp-Dev lane; cert-discipline applies)
   3. Skunkworks SCHEMA-VET on cell (cert-owner)
   4. Orchestrator queue_adds to overnight_queue (GPU REMOTE)
   5. Cell runs; writes cached_indices/bge_large_31k_*.npz on remote
   6. hd_metrics_sync auto-pulls new cache file via extended manifest
   7. Local substrate retrieval now semantic for full corpus
   8. ANY anomaly -> Skunkworks SCHEMA-VET catches at gate

After clean one-shot: Director ratifies recurring hd_index_refresh
   task design (Skunkworks SCHEMA-VET; Orchestrator implements).
```

## Composition with today's substrate-product-positioning narrative

```
Today's narrative gains 3 more concrete commitments:
   - PHASE I Lean install = first concrete substrate-system change
     toward substrate-autonomy directive (formal oracle primitive)
   - R4-18 honest documented MIDDLE preserved = NEGATIVITY-BIAS rule
     applied (don't over-claim recapture; don't manufacture a gap
     where binding-capacity already PASSES)
   - Action A bge-index-refresh = DURABILITY+FINDABILITY rail
     completion (findability for the 1229 RF atoms STEP-B atomized
     today; semantic retrieval surface fills the "easy to find"
     directive)

8th catch today (cell-author layer); cumulative today:
   1. Remote-experiments gap (1749 missing)
   2. Half-data audit (DECISION 239 chain)
   3. Research-recorded undercount
   4. DG-48x bar-vs-actual
   5. Fuzzy-retrieval discrete/hybrid
   6. Orchestrator v1 training-data-recall (Director slipped)
   7. Research lane assignment (USER directive to do research here)
   8. R4-18 mechanism-mismatch (drill -> prereg -> SCHEMA-VET ->
      cell-author caught)

The discipline catches itself (multi-layer pattern; ARCH-A/B precedent
today). 8th catch validates the discipline operationally; USER
patience appreciated.
```

## STANDING / who I'm waiting on (9th rule)

- **Orchestrator (Custodian):**
  - PHASE I Lean install + smoke test (~2-4h on USER GO landing now;
    deliverable lean_phase_I_install_smoke_result note)
  - Action A: extend remote_metrics_tar.py manifest (+~5 min);
    queue_add Exp-Dev's bge-refresh cell when shipped
  - + ongoing: SSH recovery + R4 Day-2 remote slot (now 8b + 8a only)
    + refuse_gate auto-land + cron-pipeline installs
- **Exp-Dev (Prover):**
  - HOLD 18 (Skunkworks RULING; Director value-call = Option 3
    de-scope; Option 1 queued for next R-cycle on strategic-value
    confirm)
  - AUTHOR 8b (sound; Skunkworks re-confirmed anchor-mechanism match)
    -> smoke (laptop) -> FULL REMOTE Day-2
  - AUTHOR Action A bge-refresh wrapper cell
    (exp_substrate_bge_index_refresh_full_corpus_v1.py)
  - + 8a prereg drafting (drill delivered today; primary HARD-PASS =
    break-even regime boundary; secondary mechanism = Bayesian-surprise)
  - + V1 last module disposition standing (YELLOW landed earlier;
    Director read pending)
  - + STEP-B WordNet extension scoping (tomorrow)
- **Skunkworks (Auditor; cert-owner):**
  - SCHEMA-VET on Exp-Dev's Action A bge-refresh wrapper cell
  - Per-batch VETs on 8b smoke + FULL when run
  - Lean SCHEMA-VET design draft AFTER PHASE I clean (PHASE II prep)
  - Audit-discipline 93 CONFIRMED + 13 candidates (recapture-anchor-
     mechanism-match NEW candidate; 1 witness; promote on 2 more)
- **Research (Director; me):**
  - Reactive on Orchestrator PHASE I result (will surface PHASE II
    decision to USER on clean result)
  - Reactive on Exp-Dev 8b smoke results + Action A wrapper
  - Reactive on V1 last module disposition (read pending)
  - All future research = via Sonnet sub-agents from this session with
    SAFE evidence-of-search discipline
- **Testbed (Integrator):**
  - Action A invariant verify (when cache lands)
  - 8b re-atomize verify (when verdict lands)
  - Audit-discipline ratify recapture-anchor-mechanism-match candidate
    (when 2 more witnesses)
- **USER:**
  - PHASE I GO landed; standing for clean install result
  - PHASE II decision after PHASE I clean
  - Optional future: Option 1 (R4-18 gate-orthogonalization) strategic-
    value-confirm question (deferred; not urgent)

Tag: USER_PHASE_I_GO_omnibus_director_3_items_orchestrator_dispatch_install_smoke_2_4h_elan_powershell_lean_interact_pip_hello_world_proof_subprocess_pass_fail_documented_install_log_500mb_disk_reversible_zero_atoms_R4_18_ruling_director_value_call_option_3_descope_r4_day_2_8b_only_8a_drilled_skunkworks_lean_option_3_recapture_anchor_mechanism_match_candidate_19th_rule_self_correct_owned_skunkworks_schema_vet_checklist_patched_anchor_mechanism_match_step_exp_dev_caught_mismatch_anchor_b3axb3b_write_efficiency_gating_cell_NO_binder_decoder_prereg_binder_decoder_gsbc_binding_capacity_undefined_operators_drill_conflated_gating_overlap_binding_kd_8th_catch_today_multi_layer_pattern_arch_a_b_precedent_discipline_catches_itself_b2xb4_passing_no_open_binding_gap_option_2_category_error_reject_16x_honest_documented_middle_preserved_substrate_product_correctly_captures_no_overclaim_no_goodhart_drift_option_1_gate_orthogonalization_queue_next_R_cycle_strategic_value_confirm_user_not_pushing_today_tier_2_economics_lane_review_action_A_bge_index_refresh_dispatch_ratify_Q1_Q6_orchestrator_leans_correct_Q1_lane_b_exp_dev_authors_wrapper_cell_cert_discipline_prereg_skunkworks_70th_signal_refuse_gate_pattern_Q2_full_refresh_clean_state_one_cache_content_hash_sorted_atom_ids_Q3_remote_overnight_queue_gpu_180b_compute_policy_paid_uptime_Q4_one_shot_now_recurring_after_validates_compose_hd_metrics_atomize_index_refresh_Q5_existing_notes_prereg_decision_200c_no_separate_file_Q6_extend_remote_metrics_tar_cached_indices_npz_method_b_pattern_no_new_infrastructure_5min_edit_execution_chain_extend_manifest_5min_exp_dev_authors_cell_skunkworks_schema_vet_orchestrator_queue_add_overnight_queue_gpu_cell_writes_bge_large_31k_npz_hd_metrics_sync_pulls_extended_manifest_local_semantic_retrieval_31k_corpus_anomaly_schema_vet_gate_after_clean_recurring_hd_index_refresh_design_skunkworks_orchestrator_implements_composition_substrate_product_positioning_3_commitments_phase_I_lean_substrate_autonomy_R4_18_negativity_bias_no_overclaim_action_A_findability_rail_completion_1229_rf_findable_8th_catch_today_cumulative_remote_gap_half_data_research_undercount_dg_48x_fuzzy_retrieval_orchestrator_training_recall_research_lane_R4_18_mismatch_8_USER_catches_today_patience_appreciated_fname_v2_53

-- Research (Director)
