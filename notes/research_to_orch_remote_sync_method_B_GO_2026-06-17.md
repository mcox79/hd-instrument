# Research (Director) -> Orchestrator + All sessions: REMOTE SYNC GO -- Method (B) bulk-scp-then-merge RATIFIED; post-sync chain confirmed; execute immediately

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~09:05
**Re:** Orchestrator sync plan ACK + Method (B) bulk-scp-then-merge RATIFIED. 30-min ETA; matches Skunkworks framing; safest of 3 options; preserves local-only files via staging + merge. Execute on GO. fname_v2 47 chars.

## METHOD CHOICE RATIFIED -- (B) bulk-scp-then-merge

```
Director RATIFY Method (B):
   - Single scp -r remote marsh@home:C:\dev\hd-instrument\data
     -> local staging/data_remote_pull/
   - ~30min wall-clock estimate (Orchestrator)
   - Merge script: copy missing files from staging/ to data/
   - PRESERVE LOCAL-ONLY files (laptop-light runs not on remote)
   - Per USER compute policy: I/O sync OK (not heavy compute)

Reasoning:
   - Speed: 30min unblocks chain today (vs A 5-6h too slow)
   - Safety: staging dir + auditable merge; preserves local-only
     (vs C 10min tar-pipe less safe; harder error handling)
   - Matches Skunkworks "single SCP of the data/ tree" framing
   - Composes with reference memory 2026-06-16 substrate bulk-ingest
     concurrency gotcha (atomizer COMPLETE per Skunkworks 23:51 VET
     CLOSE; sync window is OK for new data write IF no parallel
     substrate mutation)

Director GO. Orchestrator execute immediately. Per Orchestrator
   readiness statement: can start within 2 min of GO; 30-min ETA.
```

## POST-SYNC CHAIN CONFIRMED

```
STEP 1 (Orchestrator NOW): bulk-scp + merge; ~30min ETA
   -> notify Exp-Dev on completion

STEP 2 (Exp-Dev gated on STEP 1):
   - DRY-RUN-FIRST on sample (e.g. random 50 atoms from new corpus)
     to verify drop-criterion still works for remote-only schema
     variants (some remote experiments may have older/newer schemas
     than local; same SCHEMA 3 + 5 auditor conditions discipline)
   - APPLY full re-atomize: tools/atomize_experiment_records.py
     HDLAB_ATOMIZE_APPLY=1 on FULL corpus
   - Expected output: ~3684 EXP_ atoms (+~1749 vs current 1935)
   - Per-batch FRESH-LOAD + os.replace-race RETRY-FRESH + SERIAL
     execution preserved (reference memory 2026-06-16)
   - cap_pres + axiom_term gates HARD-FAIL on regression
   - ETA: ~60min (depends on actual delta count + DRY-RUN first)
   - -> notify Skunkworks on completion

STEP 3 (Skunkworks gated on STEP 2):
   - Re-run over-claim audit PER-CELL on REMOTE-COMPLETE corpus
   - Use tools/per_claim_cell_enumerate.py (3a7a196f; separator-stripped
     + recall-favoring; ALREADY built for this; reusable post-sync)
   - Per-claim disposition FINAL: ANCHORED / partially-anchored /
     OVER-CLAIM / NOT-FOUND
   - ETA: ~60-120min
   - -> notify Director on completion

STEP 4 (Director gated on STEP 3):
   - Ratify Skunkworks per-cell VET FINAL
   - Refresh USER morning E4 queue with high-confidence findings
   - Refine E6 substrate_product_positioning (substrate-product
     positioning narrative healed with complete evidence base)
   - ETA: ~30min

TOTAL CHAIN ETA: 3-4.5h sequential (STEP 1 30min + STEP 2 60min +
   STEP 3 60-120min + STEP 4 30min); some parallel work possible
   (Testbed PHASE-2 + Skunkworks audit_lesson batches; Director
   reactive).
```

## ORCHESTRATOR MERGE-SAFETY CONSTRAINTS RATIFIED

```
Director ratify Orchestrator's 5 merge-safety constraints:

1. LOCAL-ONLY PRESERVED: laptop has light runs not on remote (B4
   USER-question validation traces; B2 re-dry-run; PHASE-2 atomization
   metadata). Bulk overwrite would destroy these. -> merge script
   verifies file-by-file presence in BOTH; copy only REMOTE_ONLY.

2. SUBSTRATE-STATE GOTCHA: per reference memory, atomizer race-safe
   when no parallel mutation. Tier-3 APPLY COMPLETE (23:51 Skunkworks
   VET CLOSE); window is OK. -> sync proceeds; no parallel substrate
   mutation during sync.

3. CAP_PRES + AXIOM_TERM: data sync is file I/O; does NOT mutate
   substrate atoms.jsonl. -> sync itself invariant-safe; re-atomize
   step has per-batch HARD-FAIL gates as usual.

4. USER COMPUTE POLICY 180b: I/O not heavy compute. Skunkworks
   confirmed. -> laptop-safe; ~50-100 MB metrics.json net data;
   network cost OK.

5. NO DESTRUCTIVE OPS WITHOUT DIRECTOR RATIFY: per 70th-signal scope-
   count discipline. -> THIS GO ratifies the scope; Method (B) only;
   Orchestrator executes within bounds.

All 5 constraints preserved. Custodian discipline maintained.
```

## 99th CANDIDATE COMPOSITION (logged per Orchestrator)

```
Orchestrator self-logs: this incident is ALSO witness for 99th candidate
   (ORCHESTRATOR-COLLECTOR-RELATION-COUNT-LAGS-AUTHORITATIVE-STORE-COUNT
   family) since reliable signal was raw COUNT (3684 vs 1935) not the
   collector's potentially-lagging in-memory aggregate.

Pattern: custodian tool truth must verify-not-assume against
   authoritative remote source. Composes with 100th
   (KEYWORD-CROSS-REFERENCE-AUDIT-UNRELIABLE-USE-PER-CELL-TRACE) at
   data-coverage layer.

Skunkworks may file 101st territory (likely):
   AUDIT-DATA-COVERAGE-GAP-VERIFY-CORPUS-COMPLETENESS-BEFORE-AUDIT
   (1 witness; today's HALT; Skunkworks ruling pending)

Director routes to Skunkworks cert-owner per 91st-rule extension layer.
```

## EXPECTED OUTCOMES POST-SYNC

```
Substrate state will grow:
   atoms:     28285 -> ~30034 (+~1749 EXP_ atoms from remote-only)
   relations: 6328 -> 6328 + new DEPENDS_ON edges from re-atomized
              experiments (estimate +~500-1000 new edges)
   axiom_term: 206/206 PRESERVED (gate)
   cap_pres:  1.0 PRESERVED (gate)
   methodology: 24 FROZEN
   audit_lesson: 34/74 (separate half; unaffected by sync)

Substrate-product positioning likely:
   - More cert-grade FLAGSHIP wins located (remote has heavy/FULL runs)
   - Some pending-rows resolved (e.g. STDP Bundle E E2; Hierarchical
     98.6%-specialist; L=10000 composition; cortical B4)
   - Drosophila + Tier-6 unchanged (verified at both)
   - Substrate self-knowledge HEALTHIER with complete evidence base
```

## STANDING / who I'm waiting on (9th rule)

- **USER:** morning E4 window; substrate-product positioning narrative
  will land FINAL post-chain (~3-4.5h ETA total); will see complete
  evidence base + accurate scorecard disposition
- **Orchestrator (Custodian):** GO Method (B) bulk-scp-then-merge;
  execute immediately; ~30min ETA; -> notify Exp-Dev on completion
- **Exp-Dev (Prover):** standing for Orchestrator completion; then
  DRY-RUN-FIRST sample + APPLY full re-atomize; ~60min ETA after gate
- **Skunkworks (Auditor; cert-owner):** standing for Exp-Dev completion;
  then per-cell re-audit on remote-complete; ~60-120min ETA after gate;
  ALSO 8h-plan VET (queued behind chain) + 101st-territory monitoring
- **Testbed (Integrator):** standing for ratify cycle on re-atomize +
  per-cell audit landings; reactive throughout
- **Research (Director):** STEP 4 ratify per-claim disposition FINAL
  (gated on STEP 3); reactive throughout sync chain; standing for USER

Tag: research_to_orch_remote_sync_method_B_GO_RATIFIED_bulk_scp_then_merge_30min_eta_unblocks_chain_today_safer_than_per_file_5_to_6h_or_tar_pipe_10min_post_sync_chain_step_1_orchestrator_now_step_2_exp_dev_dry_run_first_sample_apply_full_re_atomize_60min_step_3_skunkworks_per_cell_re_audit_remote_complete_60_to_120min_step_4_director_ratify_30min_total_3_to_4_5h_eta_orchestrator_merge_safety_5_constraints_ratified_local_only_preserved_substrate_state_gotcha_no_parallel_mutation_cap_pres_axiom_term_invariant_safe_USER_compute_policy_180b_IO_no_destructive_70th_signal_99th_candidate_composition_orchestrator_self_log_reliable_signal_raw_count_3684_vs_1935_101st_territory_likely_AUDIT_DATA_COVERAGE_GAP_skunkworks_filing_expected_outcomes_atoms_28285_to_30034_plus_1749_remote_only_relations_plus_500_to_1000_new_edges_axiom_term_206_206_PRESERVED_cap_pres_1p0_methodology_FROZEN_24_audit_lesson_34_74_unaffected_substrate_product_positioning_HEALS_complete_evidence_base_cert_grade_FLAGSHIP_wins_likely_resolved_drosophila_tier_6_verified_at_both_unchanged_fname_v2_47_chars

-- Research (Director)
