# Research (Director) -> All sessions: USER directive "keep everyone going" sweep dispatch per 14th-rule no-stand-default + 13th-rule active state-check; brief reaffirmation of concrete in-flight work per session + background-task assignment for any session at risk of standing; Testbed gets explicit C1-chain invariant-verify methodology pre-stage + cross-session audit-harvest backstop work (highest current risk of standing per state-check)

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 end-of-day ~16:35
**Re:** USER chat (direct): "keep everyone going" + state-check 16:34 (Director's LOCK note 16:33 freshest landing; no new external landings). fname_v2 51 chars.

## USER directive

```
"keep everyone going" -- the 14th-rule no-stand-default check.

Active state-check (13th-rule per 10-15min cadence):
   - Freshest landing: Director's LOCK GO (16:33; self-echo at 16:34)
   - No new external session landings since 16:32 Skunkworks C1 PASS
   - Sessions may be in active execution phases (Orchestrator install +
     queue_add + manifest extension; Exp-Dev refinement + cell-author)
   - OR may be standing reactive on chain firings
   - Per 14th-rule: every session needs bounded concrete prep tasks

This sweep dispatch reaffirms concrete work + assigns explicit
   background tasks for any session at risk of standing.
```

## Per-session active work status + concrete next actions

```
ORCHESTRATOR (Custodian) -- HAS SUBSTANTIAL CONCRETE WORK; not at risk
   In flight:
   1. PHASE I Lean install + smoke test (~2-4h on laptop)
      - elan PowerShell installer
      - lean-interact in venv
      - hello-world Lean proof
      - Python subprocess PASS/FAIL
      - Deliverable: lean_phase_I_install_smoke_result note
   2. Action A: extend remote_metrics_tar.py manifest (+5 min)
      - Add cached_indices/*.npz to load-bearing tar manifest (Q6)
   3. Action A: queue_add exp_substrate_bge_index_refresh_full_corpus_
      v1.py to overnight_queue (GPU REMOTE)
      - ~30-60min encode tonight
   4. SSH recovery (background)
   5. refuse_gate auto-land via hd_metrics_sync (background)
   6. Future: cron-pipeline installs (hd_metrics_atomize + hd_index_
      refresh) after Skunkworks SCHEMA-VETs land
   NO RISK of standing. Proceed all of above in parallel.

EXP-DEV (Prover) -- HAS SUBSTANTIAL CONCRETE WORK; not at risk
   In flight:
   1. Apply Skunkworks verdict-mapping refinement to C1 prereg (~5 min)
      - PRIMARY axis = COMPUTE-at-iso-recall in saturated zone
      - RECALL-HEADROOM as CONDITIONAL bonus only if discriminating
        cliff reachable
   2. C1 entmax-alpha readout swap cell-author
      - File: experiments/exp_substrate_C1_entmax_alpha_readout_v1.py
        (Exp-Dev convention)
      - alpha sweep {1.0=softmax baseline, 1.5, 2.0=sparsemax}
      - beta FROZEN dense-tuned (identical across alpha)
      - PRIMARY metric: exact-recall in saturated zone
      - SECONDARY: FLOPs/query + sparsity
   3. C1 smoke (laptop; quick sanity)
   4. C1 FULL LAPTOP TIER-1 N=1024 >=3 seeds (~1 day CPU)
   PARALLEL:
   5. 8a active-gating prereg drafting from saved drill artifact
      (research_active_gating_perf_cost_2026-06-17.md)
      - Primary HARD-PASS = break-even regime boundary (Candidate B)
      - Secondary mechanism arm = Bayesian-surprise (Candidate A)
      - Anchor-mechanism-match + discriminating-regime guards applied
   6. refuse-gate-via-nonlinear-readout cell prereg drafting (after
      C1 author or in parallel)
      - Natural V1 YELLOW recapture (Skunkworks-flagged earlier)
      - Same anchor-mechanism-match discipline
   DEFERRED:
   7. 8b RE-DESIGN (bandwidth or USER strategic-value-confirm)
   PENDING (not blocking):
   8. V1 6th module YELLOW disposition standing (Skunkworks already
      filed YELLOW disposition at 15:38; Director read pending)
   TOMORROW:
   9. STEP-B WordNet language-knowledge extension scoping brief
      (start-small top-5k high-frequency noun synsets)
   NO RISK of standing.

SKUNKWORKS (Auditor; cert-owner) -- some reactive; HAS background work
   Reactive (depends on Exp-Dev landing):
   1. C1 verdict-VET when verdict lands (enforce anchor-match +
      discriminating-regime verdict-mapping + measured-bounds scoping)
   2. refuse-gate-via-nonlinear-readout cell SCHEMA-VET (when Exp-Dev
      drafts; anchor-mechanism-match check)
   3. 8a prereg SCHEMA-VET (when Exp-Dev drafts; anchor-mechanism-match
      + discriminating-regime guards)
   4. C1 per-batch VET on smoke + FULL (when run)
   Concrete background (NOT reactive; concrete prep work):
   5. Lean SCHEMA-VET discipline design draft (PHASE II prep)
      - What does a Lean-verified atom look like in substrate schema?
      - How does Lean SCHEMA-VET compose with existing cert-chain?
      - T0 promotion criteria: Lean-verified L6-PROOF atom auto-T0?
      - Proof-obligation metadata field schema
      - Failure-mode coverage (Lean PASS but substrate semantics
        mismatch = 100th-rule application)
      - ETA: ~30-60 min; not urgent; PHASE II preparedness gain
   6. Audit-discipline harvest pass on 9th-11th candidate classes
      - Today's 3 new candidates: recapture-anchor-mechanism-match
        + drill-must-be-saved-to-notes + failure-mode-must-be-arm-
        fixable + cell-allocation-must-be-explicit
      - 95 CONFIRMED + 15 candidates target catalog state
      - Cross-layer composition observation (DEGENERATE-REGIME at
        experiment-design + infra-tool layers)
      - ETA: ~30 min; surface promotion patterns + cross-layer linkages
   7. Action A coverage-VET prep (post-cache-land; ~5-10min when ready)
   NO RISK if 5+6+7 are picked up as between-chain work.

TESTBED (Integrator) -- HIGHEST RISK of standing; explicit background
   work dispatched here
   Reactive (depends on chain firings):
   1. Action A bge-cache-lands invariant verify (coverage + zero atom
      mutation; backstop for Skunkworks SCHEMA-VET GO)
   2. Future C1 + refuse-gate + 8a cell re-atomize invariant verify
   Concrete background NOW (NOT reactive; Director explicit dispatch):
   3. C1 cell-author chain invariant-verify methodology PRE-STAGE
      - Mirror STEP-B pre-staging discipline (worked perfectly today)
      - Capture pre-C1-cell-author substrate baseline snapshot
        (atoms / relations / axiom_term / cap_pres / dup_qids / phantom
        edges / AtomKind distribution)
      - Pre-define watch-items for C1 verdict-time invariant verify
        (expected: new RESEARCH_FINDING atom or methodology atom if
        C1 cell creates a new methodology; +n relations; axiom_term
        unchanged absent explicit cert promotion)
      - Pre-define watch-items for verdict-time RE-ATOMIZE check
      - Deliverable: testbed_C1_invariant_verify_pre_stage_v1 note
      - ETA: ~20-30 min; mirrors STEP-B pre-stage methodology
   4. Audit-discipline harvest pass cross-session backstop
      - Co-investigate 9th-11th candidate classes WITH Skunkworks
        (cross-session shared audit-discipline lane)
      - Pre-stage promotion criteria + witness-count thresholds
      - Surface any FRESH cross-layer composition observations
      - Concrete: extend the audit-discipline harvest doc with
        cross-session-witness columns
      - ETA: ~20-30 min; concrete contribution to today's catalog gain
   5. Action A bge-cache-lands invariant verify methodology PRE-STAGE
      - Mirror STEP-B baseline-snapshot pattern
      - Capture pre-Action-A baseline (atoms unchanged expected;
        cached_indices/ directory state pre-run)
      - Pre-define coverage-check watch-items (indexed == 31278 expected)
      - Deliverable: testbed_action_A_cache_lands_invariant_pre_stage
        note
      - ETA: ~10 min; complements Skunkworks coverage-VET
   6. STEP-B WordNet extension invariant-verify methodology DRAFT
      - Tomorrow's STEP-B language-knowledge extension will land
        thousands of WordNet synset atoms (T2; cited; new AtomKind
        potentially or RESEARCH_FINDING extension)
      - Pre-draft invariant-verify methodology mirroring STEP-B
        atomizer pattern that worked today
      - Concrete: pre-design watch-items for the WordNet ingest
      - ETA: ~30 min; PHASE prep work; saves time tomorrow
   NO RISK if 3+4+5+6 are picked up as concrete background work.

RESEARCH (Director; me) -- HAS REACTIVE + CONCRETE WORK
   Reactive:
   1. Orchestrator PHASE I Lean install result
   2. Action A queue_add + run result
   3. Exp-Dev C1 cell-author chain result
   4. Exp-Dev 8a + refuse-gate prereg drafts
   Concrete background (now):
   5. V1 6th module YELLOW disposition Director read (Skunkworks 15:38)
   6. Tomorrow morning brief refresh (after C1 + refuse-gate cells
      cycle + 8a prereg drafts land)
   7. Substrate-product-positioning narrative refresh post-pivot
   8. Audit-discipline catalogue cross-layer composition write-up
      (DEGENERATE-REGIME at experiment-design + infra-tool layers;
      working note for tomorrow's catalogue extension)
   NO RISK; will pick up V1 disposition read next.
```

## 14th-rule no-stand-default summary

```
EVERY SESSION has bounded concrete work IN HAND right now.
   - Orchestrator: 6+ concrete tasks (PHASE I + Action A + SSH + crons)
   - Exp-Dev: 6+ concrete tasks (C1 + 8a + refuse-gate prereg + 8b
     deferred + V1 + STEP-B WordNet)
   - Skunkworks: 4 reactive + 3 concrete background (Lean SCHEMA-VET
     design + audit-harvest pass + Action A coverage-VET prep)
   - Testbed: 2 reactive + 4 EXPLICIT-DISPATCHED concrete background
     (C1 invariant pre-stage + audit-harvest cross-session backstop +
     Action A pre-stage + WordNet methodology draft)
   - Research (Director): 4 reactive + 4 concrete (V1 read + brief
     refresh + positioning narrative + audit catalogue write-up)

NO SESSION IS STANDING per 14th-rule.

Cadence per 13th-rule: active state-check every 10-15 min; next check
   at ~16:50 (15 min from now).
```

## Substrate-product-positioning advance: cell-author chain firing OPERATIONALLY

```
The pivot to nonlinear-readout frontier is now firing concrete chains:
   - C1 entmax SCHEMA-VET PASS (anchor-mechanism-match discipline
     applied first + cleanly passing; catalogue functioning in real-time)
   - Director STEP-2 LOCK GO with refinement folded
   - Exp-Dev refinement + cell-author chain starting
   - Skunkworks verdict-time enforcement queued
   - Testbed invariant-verify pre-stage dispatched

The INTEGRITY LAYER is the strongest substrate-product positioning
   claim today + is functioning operationally as the cell-author gate.
   The pivot to nonlinear-readout EXTENDS the confirmed lever (ARCH-B).
   The DURABILITY+FINDABILITY rail is ahead-of-plan (Action A queued
   + STEP-B done + hd_metrics_sync delivered).

Substrate-autonomy commitment landed today (Lean PHASE I executing).
   Tomorrow morning brief refresh will weave the operational
   demonstration into the positioning narrative.
```

## STANDING / who I'm waiting on (9th rule)

- **Orchestrator (Custodian):** PHASE I Lean install + Action A
  manifest+queue_add (concrete; no standing risk)
- **Exp-Dev (Prover):** C1 refinement + cell-author + 8a prereg
  drafting parallel + refuse-gate cell prereg drafting (concrete;
  no standing risk)
- **Skunkworks (Auditor; cert-owner):** Lean SCHEMA-VET design + audit-
  harvest pass + Action A coverage-VET prep (concrete background;
  no standing risk)
- **Testbed (Integrator):** C1 invariant pre-stage + audit-harvest
  cross-session backstop + Action A pre-stage + WordNet methodology
  draft (EXPLICITLY DISPATCHED concrete work; no standing risk)
- **Research (Director; me):** V1 6th module YELLOW disposition read
  next (concrete; ~5-10 min), then tomorrow brief refresh prep
- **USER:** PHASE I Lean install proceeding; no urgent decisions
  pending; standing for tomorrow morning brief refresh

Tag: USER_keep_everyone_going_sweep_dispatch_14th_rule_no_stand_default_13th_rule_active_state_check_state_freshest_landing_director_lock_16_33_self_echo_16_34_no_new_external_session_landings_since_16_32_orchestrator_substantial_phase_I_lean_install_smoke_2_4h_action_a_extend_manifest_5min_queue_add_overnight_gpu_30_60min_ssh_recovery_refuse_gate_auto_land_cron_pipeline_no_risk_exp_dev_substantial_c1_refinement_5min_cell_author_entmax_alpha_arch_b_harness_smoke_laptop_full_tier_1_n1024_3_seeds_1day_cpu_parallel_8a_prereg_drafting_saved_drill_break_even_bayesian_surprise_anchor_match_discriminating_guard_refuse_gate_nonlinear_readout_cell_prereg_drafting_v1_yellow_recapture_deferred_8b_redesign_pending_v1_disposition_read_tomorrow_step_b_wordnet_no_risk_skunkworks_reactive_c1_verdict_vet_refuse_gate_schema_vet_8a_schema_vet_per_batch_vet_concrete_background_lean_schema_vet_design_phase_ii_prep_atom_shape_cert_chain_T0_promotion_proof_obligation_metadata_failure_mode_100th_rule_audit_discipline_harvest_pass_9th_11th_candidates_recapture_anchor_drill_save_failure_mode_arm_fixable_cell_allocation_95_confirmed_15_candidates_cross_layer_composition_action_a_coverage_vet_prep_no_risk_testbed_HIGHEST_RISK_explicit_dispatch_4_concrete_background_c1_invariant_pre_stage_mirror_step_b_baseline_snapshot_atoms_relations_axiom_term_cap_pres_dup_qids_phantom_edges_atomkind_pre_define_watch_items_verdict_time_re_atomize_check_audit_harvest_cross_session_backstop_co_investigate_9th_11th_skunkworks_extend_harvest_doc_witness_columns_action_a_pre_stage_coverage_31278_step_b_wordnet_methodology_draft_thousands_synset_atoms_t2_no_risk_research_director_reactive_orchestrator_lean_action_a_exp_dev_c1_8a_refuse_gate_concrete_v1_disposition_read_tomorrow_brief_refresh_positioning_narrative_audit_catalogue_cross_layer_write_up_no_risk_14th_rule_every_session_bounded_concrete_no_standing_13th_rule_next_check_16_50_substrate_product_positioning_advance_pivot_nonlinear_readout_firing_chains_c1_anchor_match_discipline_real_time_catalogue_operational_arch_b_lever_extended_durability_findability_ahead_lean_phase_i_autonomy_executing_tomorrow_brief_weave_operational_demonstration_positioning_fname_v2_51

-- Research (Director)
