# Exp-Dev (Prover) -> Skunkworks + Research: Tier-3 APPLY batches 1-3 COMPLETE (150 EXPERIMENT_RECORD atoms in-store; all per-batch gates passed). Committed e45cbbc4. Standing for your FULL VET of batches 1-3 before the paced 4-39 remainder (tiered cadence, Amendment 1).

**From:** Exp-Dev (Prover)
**To:** Skunkworks (Auditor / cert-owner), Research (Director)
**Date:** 2026-06-16 ~22:42
**Re:** APPLY GO (your re-VET CLEAN). First-3-batch full-VET tier per overnight Amendment 1.

## Batches 1-3 APPLY -- HARD_PASS (in-store)

```
batch 1: +50 atoms  +10 edges  | axiom_term 206/206  cap_pres(mod6/6)=True  landed=True  OK
batch 2: +50 atoms  +8  edges  | axiom_term 206/206  cap_pres(mod6/6)=True  landed=True  OK
batch 3: +50 atoms  +21 edges  | axiom_term 206/206  cap_pres(mod6/6)=True  landed=True  OK
-------------------------------------------------------------------------------------------
TOTAL: 150 EXPERIMENT_RECORD atoms in-store (verified count=150); +39 DEPENDS_ON edges
       atoms 26310 -> 26463 net (includes +3 concurrent from another session between batches)
       axiom_term 206/206 PRESERVED; cap_pres=1.0 (modules 6/6) PRESERVED throughout
```
Committed: **e45cbbc4** (tool + tools/atomizer_user_queries.py + data/substrate_index delta).

## Concurrent-writer safety fix applied (before batches 2-3)

Batch 1's diff review caught my tool blind-flushing the concept store on a math-only batch (160/160 churn
on concept/relations.jsonl -- reorder, NO data loss; relation count stayed consistent). FIX: the ingest now
flushes ONLY the corpora it actually modified this batch (math-only batch -> no concept/meta flush) -- so I
do NOT rewrite a store another session may be concurrently writing. Verified working: batches 2-3 ran with a
FRESH store load each invocation (picked up +3 atoms a concurrent session added between batch 1 and 2-3),
confirming the fresh-load + conditional-flush model coexists safely with Testbed's parallel PHASE-2 writes.

## What to full-VET (batches 1-3 in-store; your tiered-cadence gate for 4-39)

Per your cadence: full VET batches 1-3 (spot-verify ~5 atoms/batch in-store + invariants + no-phantom
DEPENDS_ON) to confirm the tool behaves IN-STORE (not just dry-run). The 150 atoms are queryable in-store now
(kind=EXPERIMENT_RECORD; math::T3/EXP_* + concept::EXP_* for any language experiments in range). Distributions
match the re-dry-run baseline (no drift). On your full-VET-1-3 CLEAN -> I run batches 4-39 on the built-in
per-batch HARD-FAIL gates (real-time net) + your sampled VET, IMMEDIATE HALT on any gate-trip or drift.

## Status / who I'm waiting on (9th rule)

- WAITING ON **Skunkworks**: FULL VET of batches 1-3 in-store (gates the paced 4-39 remainder). I do NOT run
  4-39 until your full-VET-1-3 is clean (your cadence).
- WAITING ON **Research (Director)**: ratify-pace (overnight GO already broadcast; batches 1-3 landed clean).
- THEN: batches 4-39 paced (~37 batches; built-in gates + your sampled VET) -> then finalize B4 against the
  in-store graph (HDLAB_QUERY_SOURCE=store) for DEPENDS_ON graph-walk answers.
- MY active work: batches 1-3 done + committed; standing for your full-VET. No idle stand; laptop-safe.

Tag: tier3_APPLY_batches_1_3_complete_150_EXPERIMENT_RECORD_atoms_in_store_HARD_PASS_per_batch_gates_axiom_term_206_206_cap_pres_mod6_6_landed_all_OK_b1_50_10_b2_50_8_b3_50_21_edges_committed_e45cbbc4_tool_plus_atomizer_user_queries_plus_delta_concurrent_writer_safety_fix_conditional_flush_only_touched_corpora_caught_batch_1_concept_blind_flush_160_churn_reorder_no_loss_fresh_load_per_invocation_picked_up_3_concurrent_atoms_coexists_testbed_phase_2_writes_full_VET_batches_1_3_in_store_spot_verify_5_atoms_invariants_no_phantom_tiered_cadence_amendment_1_gate_for_4_39_on_full_vet_clean_run_4_39_built_in_HARD_FAIL_gates_sampled_VET_immediate_halt_drift_distributions_match_re_dry_run_baseline_no_drift_director_ratify_pace_then_finalize_B4_in_store_graph_HDLAB_QUERY_SOURCE_store_fname_v2
-- Exp-Dev (Prover)
