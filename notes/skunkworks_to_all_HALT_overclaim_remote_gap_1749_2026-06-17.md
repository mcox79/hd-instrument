# SKUNKWORKS (Auditor) -> ALL: HALT the over-claim audit + DECISION 239 downgrades + the per-claim cell-trace -- the Tier-3 atomization is HALF-DATA. REMOTE marsh@home has 3684 results; we atomized only the LOCAL 1935. ~1749 experiments NEVER ingested. Sync remote + re-atomize FIRST.

**From:** Skunkworks (Auditor; cert-owner)
**To:** ALL (Research, Testbed, Exp-Dev, Orchestrator)
**Date:** 2026-06-17 ~08:35
**Re:** USER-directed coverage audit. MEASURED counts (not assumed). fname_v2.

## MEASURED (decisive)
- REMOTE marsh@home C:\dev\hd-instrument\data: **3684 metrics.json** (3790 dirs) -- via ssh count.
- LOCAL data/: 1946 metrics.json / 1969 dirs.
- ATOMIZED: 1935 EXP_ atoms.
- => **~1749 experimental results on the REMOTE were NEVER atomized.** The Tier-3 atomizer read LOCAL data/ only; local is ~HALF the remote corpus. The USER's "~3000 experiments" = the remote count.

## CONSEQUENCE -- HALT these (all run on half-data):
1. The over-claim audit (C4 5-confirmed + my skunkworks_overclaim_scan.py + DECISION 239 queue) is **INVALID/INCOMPLETE** -- it judged claims against ~half the results. Apparent over-claims (STDP, Tier-6, hierarchical, kappa_3, etc.) may have their backing in the ~1749 un-ingested REMOTE results (the heavy/FULL runs execute on remote per compute policy).
2. The per-claim cell-trace (Exp-Dev F1.X1) -- HALT: tracing LOCAL-only cells repeats the half-data error.
3. Scorecard downgrades (DECISION 239) -- HOLD (already HOLD-RATIFIED; now firmer: do NOT downgrade; backing is likely in the un-ingested remote half).

## THE FIX (sequence)
1. **Orchestrator (custodian; owns remote-bridge):** bulk-SCP remote C:\dev\hd-instrument\data (3684 results) -> local. Single SCP of the data/ tree (the get_remote_metrics per-file path is 12s each; bulk SCP is the efficient sync). Per USER compute policy this is I/O not compute = OK.
2. **Exp-Dev:** re-run tools/atomize_experiment_records.py (HDLAB_ATOMIZE_APPLY=1) over the FULL synced corpus -> ~3684 EXP_ atoms (+~1749). Drop-criterion fix already in place; same per-batch cap_pres + axiom_term gates.
3. **Skunkworks (me):** re-run the over-claim audit PER-CELL (not keyword) on the REMOTE-COMPLETE corpus. Only THEN are over-claim verdicts valid.

## What STANDS (independently verified, not half-data)
- Drosophila MB sparse: genuine HARD_FAIL (remote==local; my capacity diagnostic showed sparse mismatched to linear heteroassoc). Real over-claim.
- SQ2 K=12: real cert-grade win (b6_x_sq2 acc@12=1.00) -- audit FALSE-flagged it. Real win.
- Methodology half (24 atoms), 92nd promotion, ledger v1, substrate invariants (cap_pres 1.0 / 206/206): unaffected; STAND.

## Verify-not-assume note (for the record)
Two of my own audit tools misled me tonight: keyword-scan (case/hyphen/substring noise) + a remote-stale hypothesis the probe REFUTED (remote==local for SYNCED experiments; the gap is remote-ONLY ones). The reliable signal was the raw COUNT (3684 vs 1935). Audit tooling must be verified before its output is trusted; the substrate's claims are likely largely REAL (in the un-ingested half) -- the USER's skepticism was correct.

## Status / who I'm waiting on (9th rule)
- Orchestrator: bulk-SCP remote data/ -> local (the unblocking step).
- Exp-Dev: re-atomize full corpus post-sync; HALT the local-only per-claim trace.
- Research (Director): HALT/supersede DECISION 239 over-claim downgrades + the F1.X1 trace dispatch pending remote-complete re-atomization; the 8h-plan F1 mechanism-diagnostics should be re-scoped around this.
- Testbed: hold scorecard reconciliation; re-run post-sync.
- USER: answered (we missed ~1749 remote results; audit was half-data; fix = sync+re-atomize). Memory captured for compaction.
- ME: preparing for compaction (USER directive); this finding + state durably saved to memory. On resume: drive the sync->re-atomize->re-audit sequence.

Tag: HALT_overclaim_audit_HALF_DATA_remote_marsh_home_3684_results_local_1946_atomized_1935_1749_remote_NEVER_ingested_USER_3000_experiments_confirmed_atomizer_read_local_only_heavy_full_runs_on_remote_overclaim_audit_INVALID_per_claim_trace_HALT_scorecard_downgrades_HOLD_fix_orchestrator_bulk_SCP_remote_data_exp_dev_re_atomize_full_3684_skunkworks_re_audit_per_cell_drosophila_genuine_HARD_FAIL_stands_SQ2_K12_real_win_false_flagged_methodology_24_92nd_ledger_invariants_STAND_verify_not_assume_keyword_scan_remote_stale_hypothesis_refuted_probe_raw_count_reliable_USER_skepticism_CORRECT_compaction_memory_saved_fname_v2 -- Skunkworks (Auditor)
