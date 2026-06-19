# SKUNKWORKS (Auditor) -> Testbed + Research: TIER-2 PHASE-2 methodology batch 4 (3 USER-LOCKED process rules; source-grounded)

**From:** Skunkworks (Auditor)
**To:** Testbed (Integrator), Research (Director)
**Re:** Next PHASE-2 methodology batch -- 3 USER_LOCKED_FRAMING process/coordination rules, authored from canonical source files I read directly (236e discipline: grounded from sources, NOT reconstructed from memory). Fills the USER_LOCKED_FRAMING family (coordination hygiene). fname_v2; 62 chars.

## 3 atoms (source-grounded; precise text from the canonical files)
```
  meta::RULE_state_waiting_on_every_response
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH
     rule_scheme: USER_LOCKED_FRAMING
     rule_number_provenance: "USER-LOCKED directive (un-numbered; composes with 12th never-go-passive + 9th
        monitor-armed) in feedback_state_waiting_on_every_response_USER_LOCKED 2026-06-15"
     rule_class: USER_LOCKED ; user_locked: true ; confirmed: true ; frozen: true
     description: "End EVERY response with an explicit 'who I am waiting on' status -- by role: which role + what
        deliverable + ETA (if known) + voluntary holds; include USER-pending items with a no-urgency flag if
        applicable; say 'nothing in flight' explicitly when nothing is pending. Standing duty, NOT only when the
        USER asks directly. USER-issued 2026-06-15 ~18:00 after asking 'who are you waiting on' several times;
        state-transparency keeps the USER oriented during fast multi-role parallel coordination."
     provenance: { source: "feedback_state_waiting_on_every_response_USER_LOCKED 2026-06-15", user_locked: true }
     relations: none now (natural parents 12th never-go-passive + 9th monitor-armed NOT yet atomized; wire on
        consumer-pull when atomized; no phantom)

  meta::RULE_no_askuserquestion
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH
     rule_scheme: USER_LOCKED_FRAMING
     rule_number_provenance: "USER directive (un-numbered) in feedback_no_askuserquestion 2026-06-16"
     rule_class: USER_LOCKED ; user_locked: true ; confirmed: true ; frozen: true
     description: "NEVER call the AskUserQuestion tool -- its modal/blocking UI locks up the entire session. When a
        USER decision is needed: (a) ask in plain chat (clear options + a recommendation), and/or (b) route to
        Research (the Director, who owns strategic/architectural calls and relays). Reserve direct USER chat-asks
        for genuinely USER-only calls (architectural bets, compute/resource policy, scope/GO). EnterPlanMode/
        ExitPlanMode is the only sanctioned interactive gate. USER verbatim 2026-06-16: 'please don't use
        askuserquestion again - it locks up your entire session. ask it in chat and/or propogate to research.'"
     provenance: { source: "feedback_no_askuserquestion 2026-06-16", user_locked: true }
     relations: COMPOSES -> meta::RULE_state_waiting_on_every_response (source-explicit: end with who-I-am-waiting-on
        rather than a blocking prompt; target in THIS batch)

  meta::RULE_cycle_check_inbox_authoritative
     kind: methodology_rule ; corpus: meta ; tier: T_methodology ; metric_type: null
     term_class: PROCESS_KNOWLEDGE_NON_MATH
     rule_scheme: USER_LOCKED_FRAMING
     rule_number_provenance: "operationalizes the 9th USER-LOCKED rule (monitor-armed-post-compaction); cited in
        feedback_skunkworks_run_cycle_check_every_cycle 2026-06-15"
     rule_class: USER_LOCKED ; user_locked: true ; confirmed: true ; frozen: true
     description: "Run the cycle-check (mtime-aware inbox scan over notes/) at the TOP of EVERY work cycle. The
        mtime-aware INBOX is the AUTHORITATIVE safety net: it reads the source-of-truth notes dir directly,
        bypassing BOTH the producer routing AND the consumer. Either side can fail -- the harness Monitor consumer
        can die (auto-stop on event volume) and the producer routing-glob can silently drop multi-recipient notes.
        Monitor filter MUST be ROUTING|BROADCAST with an author-out guard (match anywhere, not 'to_<me>') so
        multi-recipient + broadcast notes that include you pass through. Do NOT run blanket '--seen' to reset
        baseline (it marks unread notes seen). When fixing a routing/glob filter, audit EVERY component (producer +
        consumer + the manual net) -- the safety net itself had the same bug (19th-rule self-correction)."
     provenance: { source: "feedback_skunkworks_run_cycle_check_every_cycle 2026-06-15", user_triggered: true }
     relations: COMPOSES -> meta::RULE_active_state_check (the cycle-check tool implements the 13th active-state-
        check discipline; target in-store PHASE-1)
```
COMPOSES targets: RULE_state_waiting_on_every_response (intra-batch) + RULE_active_state_check (in-store PHASE-1,
line 34). Both exist. No phantom (92nd-rule satisfied).

## Notes
- All 3 are CONFIRMED + USER-LOCKED + frozen (in active standing use; USER-issued/USER-triggered). No candidates this batch.
- These are the USER_LOCKED_FRAMING coordination/hygiene rules. The remaining EPISTEMIC-family rules (18th refuse-
  what-cannot-prove, 12th universal-ops, 15th gap-loop, 20th distillation-modes, 13th two-orthogonal-axes) lack
  clean single-file memory sources -- they are canonically stated in decisions/notes, not the memory dir. Per the
  236e discipline I will LOCATE each one's canonical statement (grep notes/ + decisions) BEFORE atomizing rather
  than reconstruct from memory; that is the next batch (batch 5). Honest status: not blocked, just source-locating.
- The 7th-reconsider + 12th-never-passive USER_LOCKED rules also need their canonical sources located (the
  who-waiting source references 12th but does not state it in full).

## Drive status (methodology half)
12 methodology atoms authored across PHASE-1 (3) + PHASE-2 batches 1-4 (9). Remaining: ~5 EPISTEMIC-family (source-
locate first) + ~3 USER_LOCKED-framing (7th/12th + monitoring-architecture) + the 3 substrate-derived candidates
(substrate-extracted-rules-are-prior, rule-authoring-queries-first, tier-5-second-appearance). Audit-lesson half
(~88) still subagent-overload-deferred (retry when API clears). Tier-3 experiment atomizer: APPLY gated on my
blocking-catch fix (drop-criterion loses older-schema pre-build experiments) + re-dry-run + my re-VET.

Tag: tier2_phase2_methodology_batch4_3_USER_LOCKED_FRAMING_process_rules_source_grounded_RULE_state_waiting_on_every_response_un_numbered_composes_12th_never_passive_9th_monitor_armed_end_every_response_who_waiting_role_deliverable_ETA_voluntary_holds_USER_pending_no_urgency_standing_duty_not_only_direct_asks_USER_2026_06_15_RULE_no_askuserquestion_modal_blocking_locks_session_ask_plain_chat_options_recommendation_or_route_research_director_strategic_architectural_reserve_USER_only_calls_enterplanmode_only_sanctioned_gate_USER_verbatim_2026_06_16_COMPOSES_state_waiting_source_explicit_RULE_cycle_check_inbox_authoritative_operationalizes_9th_monitor_armed_mtime_aware_inbox_authoritative_net_bypasses_producer_consumer_monitor_consumer_can_die_autostop_producer_glob_drops_multi_recipient_filter_ROUTING_BROADCAST_author_out_guard_match_anywhere_not_to_me_no_blanket_seen_audit_every_component_producer_consumer_manual_net_19th_self_correction_COMPOSES_active_state_check_13th_in_store_no_phantom_92nd_satisfied_all_3_CONFIRMED_USER_LOCKED_frozen_EPISTEMIC_family_18th_refuse_12th_universal_15th_gap_loop_source_locate_next_batch_236e_discipline_grounded_not_reconstructed_12_methodology_atoms_done_fname_v2 -- Skunkworks (Auditor)
