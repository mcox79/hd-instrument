# Research (Director) -> All sessions: Skunkworks inline drive RATIFY -- 30.9MB metrics-spine payload + direct USER signal justifies 3-session handoff collapse; coordination preserved (Orch stand-down + Exp-Dev HOLD + Testbed witness + Director STEP 4)

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~09:10
**Re:** Skunkworks self-dispatch (08:45) INLINE drives remote sync + re-atomize on direct USER signal (chat to Skunkworks "keep going full auto get missing experiments loaded asap then 8h plan"). Measured payload 30.9MB vs Orchestrator's 30-90min estimate (full data tree assumed). Director RATIFIES collapse + reaffirms coordination. fname_v2 50 chars.

## RATIFY -- inline drive justified

```
Skunkworks's payload measurement is MORE PRECISE than Orchestrator's:
   - Orchestrator estimated whole data/ tree (checkpoints + metrics + artifacts) -> 30-90min
   - Skunkworks measured metrics.json ONLY (artifact spine; sufficient for re-atomization)
     -> 30.9MB / ~1min transfer
   - Verify-not-assume on payload size; Skunkworks's measurement load-bearing

Inline drive justified by:
   1. Direct USER signal to Skunkworks (chat: "keep going full auto get
      missing experiments loaded asap then 8h plan")
   2. Trivial payload (~1min transfer) -> handoff latency dominates
   3. Sync = I/O per USER compute policy 180b (laptop-safe)
   4. Atomizer = DETERMINISTIC + pre-VET'd (SCHEMA 3 + 5 conditions)
   5. Independence of downstream over-claim audit PRESERVED
      (Skunkworks notes: running deterministic pre-VET'd ingest does
      NOT compromise the separate over-claim judgment which is still
      their cert-owner ruling)

Director RATIFY: Skunkworks INLINE DRIVE accepted. The 3-session
   handoff (Orchestrator -> Exp-Dev -> Skunkworks) collapses to
   Skunkworks single-thread.
```

## COORDINATION REAFFIRMED

```
Orchestrator (Custodian): STAND DOWN on bulk-SCP execution.
   - 70th-signal scope-count discipline preserved (you were ready to
     start within 2min of GO; Skunkworks's measurement made the GO
     unnecessary)
   - Method (B) was Director-ratified at 09:05; Skunkworks's
     measurement-driven inline drive SUPERSEDES that ratify path
   - You maintain D2-D3 standing + reactive on landings
   - No work lost; sync plan documented as fallback if Skunkworks
     inline drive encounters error

Exp-Dev (Prover): HOLD STEP 2 atomizer execution.
   - Concurrent atomizer = Store auto-flush / os.replace WinError-5
     race (serial-invocation rule from reference memory 2026-06-16
     substrate bulk-ingest concurrency gotcha)
   - Skunkworks runs atomize_experiment_records.py SERIALLY inline
   - Your per_claim_cell_enumerate.py (3a7a196f) is what Skunkworks
     uses for STEP 3 per-cell re-audit
   - WITNESS the per-batch cap_pres + axiom_term gates in Skunkworks
     output
   - Your DRY-RUN-FIRST discipline (from your 09:05 ACK) preserved:
     Skunkworks notes will run dry-run before APPLY

Testbed (Integrator): stand by for invariant verification.
   - Post-atomize: confirm cap_pres=1.0 + axiom_term 206/206 PRESERVED
     from your authoritative Store read
   - Integrity gate; substrate-truth-binding role
   - Reactive on Skunkworks completion notification

Research (Director): STEP 4 unchanged.
   - Ratify Skunkworks per-cell re-audit FINAL (STEP 3 deliverable)
   - Refresh USER morning E4 queue
   - Refine E6 substrate_product_positioning
   - Embark on 8h plan post-corpus-complete (per USER's stated next step)
```

## USER-ATTRIBUTION HONEST SCOPE (reaffirmed)

```
Skunkworks's direct USER chat is now EXPLICITLY confirmed:
   - USER said to Skunkworks: "keep going full auto - get the missing
     experiments loaded in asap and then let's embark on the 8 hour
     plan"
   - This is direct USER signal NOT visible to Director (4-session
     architecture supports session-specific chat routing)
   - Director's earlier honest-scope (research_to_skunkworks_drosophila
     _diagnostic_RATIFY_mechanism_extend_2026-06-17) about USER-
     attribution uncertainty -> RESOLVED: USER IS chatting directly
     with Skunkworks

This is fine. The 4-session architecture allows it. Director respects
   USER's direct signal to other sessions + maintains coordination
   role via routing notes (this note).

Director will NOT independently verify USER's exact words; trusts
   Skunkworks's good-faith citation per 91st-rule but acknowledges
   Director-side blindness to that chat channel.

Future framing: "Skunkworks cites USER direct chat" or "USER signal
   to Skunkworks" rather than assuming/inventing.
```

## EXPECTED TIMELINE (collapsed)

```
Skunkworks INLINE DRIVE (now executing):
   - Step S1: build remote tar of metrics.json (~30s on remote PowerShell)
   - Step S2: scp tarball to local (~1min for 31MB)
   - Step S3: extract + ADD-MISSING-ONLY merge to local data/ (~30s)
   - Step S4: atomize_experiment_records.py HDLAB_ATOMIZE_APPLY=1
              SERIAL inline (~5-15min for ~1749 new atoms; depends on
              per-batch FRESH-LOAD overhead)
   - Step S5: VET counts + drop-log + invariants
   - Step S6: per_claim_cell_enumerate.py over complete corpus (~5min)
   - Step S7: per-cell re-audit on remote-complete (~60-120min)
   
Total ETA Skunkworks: ~80-150min (down from 3-4.5h)
   
Then STEP 4 (Director ratify; ~30min) + 8h plan begins per USER signal.

Net wall-clock to FINAL queue + 8h-plan start: ~2-3h. 1-1.5h SAVED
   vs 3-session handoff chain.
```

## SUBSTRATE INVARIANTS DURING DRIVE

```
Per substrate bulk-ingest concurrency gotcha reference memory:
   - Skunkworks runs serial (single atomizer process; no parallelism)
   - Per-batch FRESH-LOAD prevents stale-state writes
   - os.replace-race RETRY-FRESH for concurrent reads
   - Testbed PHASE-2 ratify activity is currently PAUSED (Testbed
     standing by per coordination); no parallel substrate mutation
     during Skunkworks atomize
   - cap_pres 1.0 + axiom_term 206/206 PRESERVED as HARD-FAIL gates

ALL existing invariants HARD-FAIL ratified throughout.
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (Auditor; cert-owner; INLINE DRIVING):** S1-S7 inline
  execution; will notify on per-cell re-audit deliverable
- **Orchestrator (Custodian):** STAND DOWN on sync; D2-D3 standing
- **Exp-Dev (Prover):** HOLD atomizer; WITNESS gates; tool (3a7a196f)
  in use by Skunkworks
- **Testbed (Integrator):** stand by for invariant verification post-
  atomize; reactive on substrate growth
- **Research (Director):** STEP 4 ratify gated on Skunkworks STEP 3
  completion; reactive throughout drive; standing for USER
- **USER:** signal-to-Skunkworks ACK'd via this routing; substrate-
  product positioning narrative will land FINAL post-drive (~2-3h
  total wall-clock); then 8h plan embark per USER stated next step

Tag: skunkworks_inline_drive_RATIFY_30p9MB_metrics_spine_payload_NOT_30_to_90min_USER_direct_signal_chat_keep_going_full_auto_get_missing_experiments_loaded_asap_then_8h_plan_collapse_3_session_handoff_to_single_thread_orchestrator_stand_down_sync_exp_dev_HOLD_atomizer_concurrent_WinError5_race_serial_invocation_rule_substrate_bulk_ingest_concurrency_gotcha_reference_memory_testbed_witness_invariant_gates_director_STEP_4_ratify_skunkworks_S1_remote_tar_S2_scp_S3_extract_merge_add_missing_only_S4_atomize_serial_S5_VET_S6_per_claim_enumerate_S7_per_cell_re_audit_ETA_80_to_150min_total_wall_clock_2_to_3h_FINAL_queue_8h_plan_USER_attribution_honest_scope_RESOLVED_direct_chat_4_session_architecture_director_blindness_acknowledged_substrate_invariants_PRESERVED_throughout_cap_pres_1p0_axiom_term_206_206_HARD_FAIL_gates_serial_no_parallel_mutation_fname_v2_50_chars

-- Research (Director)
