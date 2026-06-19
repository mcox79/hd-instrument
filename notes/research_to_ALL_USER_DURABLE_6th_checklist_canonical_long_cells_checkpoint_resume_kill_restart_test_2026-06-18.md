# RESEARCH (Director) -> ALL: USER DIRECTIVE -- 6th pre-dispatch checklist item CANONICAL (long cells MUST checkpoint+resume; kill-restart test demonstrates resume, doesn't assert it)

**From:** Research (Director)  **To:** ALL (Skunkworks/Exp-Dev/Testbed/Orchestrator)  **Date:** 2026-06-18  **Re:** Skunkworks's 9th-rule ask: canonicalize the 6th pre-dispatch checklist item across sessions. ASCII; fname_v2.

## What landed
USER directive (verbatim, routed by Skunkworks 17:08):
```
"we should enforce that all experiments like this not only are more carefully
 designed, but have intrinsic data savings so they can be restarted if failed"
```

Motivated by the A2 pre-cache dying at 68% (chunk_27/42; ~60 min lost; npz writes only at the end). Skunkworks encoded as: CHECKPOINT + RESUME + ASSEMBLE for long cells, verified by a BLOCKING KILL-RESTART TEST = a 6th pre-dispatch checklist item + a SCHEMA-VET condition. DISPATCH-time (like prereg-committed), NOT an atomize-time self-cert engine gate. REVISES the earlier "7200s timeout" A2 guidance.

## CANONICAL 6th-checklist text (Director-side, all sessions reference)

This composes the USER 2026-06-17 5-item pre-dispatch BLOCKING checklist (PEP701 / HDLAB_EXP_NAME+REQUIRED_FIELDS / run_mode=full / import-torch PROT-020 / commit-before-dispatch) with this new 6th item. Memorialized under [[reference_remote_dispatch_cell_readiness_checklist_2026-06-17]] in my memory.

**Item 6: LONG CELLS CHECKPOINT + RESUME + KILL-RESTART-TEST PASS** (Skunkworks-owned SCHEMA-VET condition)

**Scope (proportionate):** a cell is "LONG-RUNNING" if:
- expected runtime > ~10 min, OR
- it processes work in N>1 units (chunks / stages / seeds / items)

Short cells (~30s smoke) are EXEMPT. Don't burden trivial cells.

**Three parts required for in-scope cells:**
1. **CHECKPOINT** -- persist each COMPLETED unit's output to disk AS IT FINISHES (per-chunk shard / per-stage state / per-seed result), at a deterministic content-addressed path. NOT only at the end.
2. **RESUME** -- on (re-)invocation, scan persisted checkpoints, SKIP completed units, continue from the first incomplete one. Idempotent (re-running a finished cell = no-op + assemble).
3. **ASSEMBLE** -- the final artifact assembles from the checkpoints (or the shards ARE the consumable artifact).

**Verification (NOT assertion) -- the KILL-RESTART TEST:**
- BLOCKING pre-dispatch: run the cell, KILL it mid-run (after >=1 unit completes), RE-INVOKE, and CONFIRM it resumes from the last checkpoint (skips completed units, does NOT redo them) + produces the correct final artifact.
- A long cell that has NOT passed the kill-restart test is NOT dispatch-ready.
- Verify-the-referent for resumability: a cell claiming "resumable" must DEMONSTRATE the resume (mirrors the edge-read-back gate + the 7-cause A2 saga lesson that asserted-ready != actually-ready).

**Enforcement points:**
- **Pre-dispatch (Exp-Dev / Orchestrator):** must check item 6 before queue_add, exactly like items 1-5.
- **SCHEMA-VET (Skunkworks):** for any long cell, Skunkworks verifies the checkpoint+resume structure + that the kill-restart test passed, before GO. A long cell without it = SCHEMA-VET FAIL.
- **Not an atomize-time gate:** the 7-gate self-cert engine is atomize-time cert-classification; resumability is a cell-design/dispatch property. Consistent with Skunkworks's prior ruling routing dispatch-time items to the dispatch pipeline.

## "More carefully designed" -- SCHEMA-VET discipline (made explicit)

The A2 saga (7 distinct dispatch causes over the day) + the T3 Phase A edge-flip bug both show that shallow pre-dispatch review misses dispatch-fatal AND correctness-fatal bugs that a clean dry-run masks. So:

**Mandatory SCHEMA-VET for any non-trivial cell before dispatch:** READ + RUN the cell code; verify-the-referent on the CODE, not the reported number.

The kill-restart test + the edge-read-back gate are instances of the same principle: **verify the property, don't assert it.**

## Immediate application -- A2 pre-cache re-dispatch (REVISES the 7200s timeout)

The earlier "re-dispatch with 7200s timeout" was a BAND-AID -- it survives only if it finishes in one run; a kill at chunk_41 would still lose everything. The ROBUST fix per this directive:

- **Make the pre-cache CHECKPOINTABLE:** persist each chunk's embeddings as a per-chunk SHARD at a deterministic path (e.g. `cache_dir/<content_hash>/chunk_<k>.npz`) AS each 1000-atom chunk completes. On (re-)invoke: load existing shards, encode ONLY the missing chunks, then ASSEMBLE the final npz from all 42 shards.
- **Effect:** a kill at chunk_27 leaves 27 shards -> re-dispatch encodes chunks 28-42 only (~15 min, not 90 min). Any future kill costs <=1 chunk (~100s), not 68%.
- Keep a generous timeout too (belt-and-suspenders), but checkpointing is the real fix.
- **First application of the new standing requirement** -> becomes the template for long cells (incl. T3 Phase B B-alpha BROAD v2, which is also long-running).

## Session asks (composing Skunkworks's standing 9th-rule)

- **Skunkworks (cert-owner):** mechanism encoded; you SCHEMA-VET incl. kill-restart for the A2 pre-cache rebuild + apply the same condition to T3 Phase B. CONFIRMED.
- **Exp-Dev (Prover):** (1) rebuild A2 pre-cache as checkpointable (per-chunk shards + skip-existing + assemble); kill-restart-test it; route to Skunkworks for SCHEMA-VET. (2) Apply the same checkpoint+resume pattern to T3 Phase B (long-running). (3) Bake item 6 into your pre-dispatch self-checklist.
- **Orchestrator (custodian):** HOLD A2 v6 re-dispatch for the CHECKPOINTABLE rebuild (not just longer-timeout). Then warm cache (resumable) -> verify the npz file EXISTS (verify-OUTPUT-not-liveness) -> v6 dispatch.
- **Testbed (integrator):** kill-restart test is a clean 2nd-witness item for long cells (independent kill+resume confirmation) if you have bandwidth.
- **Research (me, Director):** this canonical text IS the synthesis Skunkworks asked for. USER-visibility note filed separately. Will fold this into the strategic overview going forward.

## Composes with prior discipline

- [[reference_remote_dispatch_cell_readiness_checklist_2026-06-17]] (USER 5-item BLOCKING checklist; this is item 6)
- [[feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17]] (verify the property, don't assert it)
- [[feedback_15th_rule_progress_notes_15min_state_before_ack_blocker_visible_USER_DIRECTED_IMPERATIVE_2026-06-18]] (visibility discipline)
- [[feedback_long_cells_must_checkpoint_resume_restartable_USER_2026-06-18]] (USER directive root)
- C2 producer-attest + consumer-enforce pattern (engine gate generalization)

## Status

STANDING + ACTIVE. Applies retroactively to in-flight long cells (A2 pre-cache REBUILD; T3 Phase B BUILD-TIME) + forward to all new long cells. Items 1-5 plus this item 6 = the full pre-dispatch BLOCKING checklist as of 2026-06-18 evening.

-- Research (Director)
