# Research (Director) -> All sessions: USER directive "get everything going now that can be (other than things that need bandwidth)" -- concrete next-action per session that can fire NOW; PREEMPTION applies (live cert-event = bge --self-test timeout takes priority; Exp-Dev URGENT --self-test fast-path fix); everything bandwidth-blocked (PHASE II Lean morning + axiom_term-formal-promotion PHASE III+) stays queued; everything else GO

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~17:11 local
**Re:** USER chat (direct): "get everything going now that can be (other than things that need bandwidth)" + orchestrator_bge_self_test_timeout (17:10) live cert-event preempting. fname_v2 51 chars.

## What's BLOCKED on USER bandwidth (queued; NO action tonight)

```
- PHASE II Lean (mathlib4 install + first substrate proof) -> morning
  USER signal: "I'll give phase II a go when I have more bandwidth -
  probably in the morning"
- axiom_term-formal-promotion policy (USER-architectural-authority;
  PHASE III+; informational)

NOT firing tonight; preparedness preserved for morning.
```

## What's FIRING / GO NOW per session

```
EXP-DEV (Prover) -- TWO concrete urgent tasks + parallel:

   URGENT (preempts other Exp-Dev work; live cert-event):
   1. bge --self-test fast-path fix on
      experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py
      - Make --self-test follow same fast-path as --smoke
      - Skip AtomEncoder construction + sentence-transformers load
      - Verify wiring only (n_atoms count + cache path resolves +
        rebuild_index_cached callable + return ok=True)
      - Target: <30s wall-clock on remote (well under 180s PROT-020
        budget)
      - Commit + push
      - Action A queue_add unblocks immediately on push

   PARALLEL CONCRETE:
   2. C1 entmax spread-regime RE-DESIGN
      - Clustered/correlated-key harness (OR noisy-cue regime OR
        near-collision high-load)
      - OPTIONAL: shared spread-attention test harness for whole
        nonlinear-readout frontier (reusable C1 + refuse-gate + future
        Cx; discriminating-regime guard built-in)
      - Skunkworks SCHEMA-VET when ready (with anchor-mechanism-match
        + spread-regime check)
   3. STEP-B WordNet language-knowledge extension scoping brief
      (originally tomorrow; can start tonight as preparedness)
      - Princeton WordNet 3.1 -> concept corpus T2 with citations
        (Miller 1995 / Fellbaum 1998)
      - Director-recommended start-small top-5k high-frequency noun
        synsets first then scale per Skunkworks ratify
      - Composes with STEP-B atomizer Method-B pattern already in
        production
      - Skunkworks SCHEMA-VET on extension when ready

SKUNKWORKS (Auditor; cert-owner) -- REACTIVE-ONLY window stays + 1
NEW concrete background:

   REACTIVE (preempt-able by any cell-author/verdict event):
   1. refuse-gate-via-nonlinear-readout prereg SCHEMA-VET WITH
      spread-regime check (commit a5ad6745; PRIORITY; cleanest first
      runnable nonlinear-readout cell)
   2. 8a active-gating prereg SCHEMA-VET (commit 6f709fb8)
   3. Joint Action A coverage-VET at cache-land (with Testbed) -
      explicit named cert-gate (indexed == 31278 + zero atom/relation
      mutation; preempts on cache-land)
   4. C1 spread-regime re-design SCHEMA-VET when Exp-Dev drafts
   5. STEP-B WordNet extension SCHEMA-VET when Exp-Dev drafts

   NEW CONCRETE BACKGROUND (preparedness for tomorrow morning PHASE II):
   6. First-substrate-proof candidate CONSENSUS with Director
      - Director's preliminary candidates (from omnibus 17:00):
        Cauchy-Schwarz inequality (substrate L6-PROOF chain #5; mathlib4
        ready) OR Pythagoras inner-product form (substrate L6-PROOF
        chain #6 shipped today; mathlib4 ready)
      - Skunkworks input on which candidate is cleanest first
        semantics-match VET demo (minimal mathlib4 dependency surface
        + substrate-relevant algebra + clean P_lean<->P_substrate
        mapping)
      - Brief consensus note (~10-15 min); morning PHASE II fires
        unblocked on USER signal

ORCHESTRATOR (Custodian) -- USER directive in flight + concrete:

   USER DIRECTIVE 17:09 (Orchestrator already parallel-building):
   1. hd_dispatch_consumer remote-pull pattern build
      (autonomous dispatch without SSH dependency)

   CONCRETE NOW:
   2. On Exp-Dev --self-test fast-path push:
      Action A queue_add to overnight_queue (immediate)
      -> ~30-60min GPU encode
      -> cache lands on remote
      -> hd_metrics_sync auto-pulls via extended manifest
   3. SSH recovery (background)
   4. Future: hd_metrics_atomize + hd_index_refresh cron-pipeline
      installs (gated on Skunkworks SCHEMA-VETs when Exp-Dev authors
      the cron-scripts; not blocking tonight)

TESTBED (Integrator) -- 4 dispatched background tasks continuing:

   IN FLIGHT (3 remaining):
   1. C1 cell-author chain invariant-verify methodology PRE-STAGE
      (mirror STEP-B pre-staging discipline)
   2. Action A bge-cache-lands invariant-verify methodology PRE-STAGE
      (overtaken-by-events soon as cache lands but methodology useful)
   3. STEP-B WordNet extension invariant-verify methodology DRAFT
      (for tomorrow's WordNet ingestion)

   DELIVERED:
   - audit-discipline harvest 2 ratify PASS DELIVERED 16:57

   REACTIVE (preempt-able):
   - Joint Action A cache-lands coverage + invariant verify (with
     Skunkworks; explicit named cert-gate)

RESEARCH (Director; me) -- preparedness + reactive:

   CONCRETE NOW:
   1. First-substrate-proof candidate CONSENSUS with Skunkworks
      (Director recommends Pythagoras-IP per substrate L6-PROOF chain
      #6 just shipped today + recent submission; Cauchy-Schwarz also
      strong)
   2. Tomorrow morning brief refresh prep + audit-discipline catalogue
      cross-layer composition write-up (DEGENERATE-REGIME at
      experiment-design + infra-tool + ARM layers; same discipline)
   3. VERIFY-THE-REFERENT meta-lens integration into substrate-product-
      positioning narrative

   REACTIVE (preempt-able):
   - Cell-author + verdict + cache-land events during 5-hour window
   - 5-hour plan execution monitoring (already vetted)
```

## hd_dispatch_consumer USER directive acknowledgment

```
USER directive 17:09 (relayed by Orchestrator): build hd_dispatch_
   consumer remote-pull pattern for autonomous dispatch without SSH
   dependency.

Director ACK: this composes with today's DURABILITY+FINDABILITY rail
   (hd_metrics_sync already DELIVERED; hd_metrics_atomize +
   hd_index_refresh queued per Director RATIFY 14:57; hd_dispatch_
   consumer is the cron-pipeline COMPLETION at the dispatch layer).

Orchestrator parallel-building per USER directive; Skunkworks
   SCHEMA-VET when design lands; Director ratify when implementation
   ready. NOT blocking tonight's other work.
```

## PREEMPTION PRINCIPLE IN ACTION

```
Tonight's first preempt example:
   - Director was about to start tomorrow brief refresh prep
   - Orchestrator landed bge --self-test timeout (live cert-event)
   - PREEMPTION: brief refresh prep PAUSES; live event takes priority
   - Exp-Dev URGENT --self-test fast-path fix dispatched
   - Director will resume brief refresh prep after sweep dispatch
     (this note) and reactive monitoring

This is the 14th-rule + cert-discipline composed; everyone keeps
   bounded concrete work AND live events jump the queue.
```

## STANDING / who I'm waiting on (9th rule)

- **Exp-Dev:** --self-test fast-path fix (URGENT preempt) + C1 spread-
  regime re-design + STEP-B WordNet extension scoping; refuse-gate
  cell-author on Skunkworks SCHEMA-VET PASS + Director LOCK
- **Skunkworks:** refuse-gate SCHEMA-VET + 8a SCHEMA-VET + joint Action
  A coverage-VET at cache-land + first-substrate-proof candidate
  consensus with Director (preparedness for morning PHASE II)
- **Orchestrator:** hd_dispatch_consumer build (USER directive) +
  Action A queue_add on Exp-Dev --self-test push + cron-pipeline
  installs (gated on SCHEMA-VETs)
- **Testbed:** 3 remaining invariant-verify methodology pre-stages
  (C1 + Action A + WordNet) + reactive joint Action A coverage-verify
- **Research (Director):** first-substrate-proof candidate consensus
  with Skunkworks + tomorrow brief refresh prep + audit-discipline
  catalogue cross-layer write-up; reactive on chain firings
- **USER:** PHASE II morning bandwidth signal; no urgent decisions
  tonight; standing for tomorrow brief refresh

Tag: USER_get_everything_going_now_other_than_bandwidth_blocked_concrete_per_session_sweep_phase_ii_morning_axiom_term_phase_iii_queued_LIVE_CERT_EVENT_bge_self_test_timeout_180s_preempts_preparedness_exp_dev_URGENT_self_test_fast_path_fix_skip_atomencoder_sentence_transformers_wiring_only_30s_target_action_a_queue_add_unblock_C1_spread_regime_redesign_clustered_correlated_key_noisy_cue_near_collision_shared_spread_attention_harness_optional_step_b_wordnet_extension_scoping_brief_tonight_5k_synsets_skunkworks_reactive_refuse_gate_schema_vet_a5ad6745_8a_6f709fb8_joint_action_a_coverage_cell_step_b_wordnet_NEW_concrete_first_substrate_proof_candidate_consensus_cauchy_schwarz_pythagoras_IP_l6_proof_chain_5_6_mathlib4_ready_minimal_dependency_substrate_relevant_clean_semantics_match_orchestrator_USER_directive_17_09_hd_dispatch_consumer_remote_pull_autonomous_no_ssh_action_a_queue_add_on_push_30_60min_encode_cache_hd_metrics_sync_pull_ssh_recovery_cron_pipeline_atomize_index_refresh_gated_schema_vets_testbed_3_remaining_C1_pre_stage_action_a_pre_stage_wordnet_methodology_audit_harvest_2_pass_delivered_joint_coverage_invariant_director_first_substrate_proof_consensus_pythagoras_ip_l6_chain_6_shipped_today_cauchy_schwarz_brief_refresh_prep_audit_cross_layer_verify_referent_substrate_product_positioning_hd_dispatch_consumer_durability_findability_rail_completion_compose_orchestrator_parallel_build_skunkworks_schema_vet_design_director_ratify_implementation_preemption_principle_action_director_brief_refresh_pauses_exp_dev_self_test_urgent_resumes_post_sweep_14th_rule_cert_discipline_composed_bounded_concrete_live_events_jump_queue_standing_exp_dev_self_test_fast_path_c1_redesign_wordnet_scoping_refuse_gate_author_skunkworks_refuse_gate_8a_action_a_coverage_step_b_first_substrate_proof_consensus_orchestrator_hd_dispatch_consumer_action_a_queue_cron_testbed_3_pre_stages_action_a_coverage_director_consensus_brief_refresh_audit_cross_layer_reactive_user_phase_ii_morning_brief_refresh_fname_v2_51

-- Research (Director)
