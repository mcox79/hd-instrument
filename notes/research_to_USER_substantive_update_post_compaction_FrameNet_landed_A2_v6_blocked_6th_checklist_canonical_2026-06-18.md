# RESEARCH (Director) -> USER: substantive update -- FrameNet ingest LANDED clean / A2-v6 BLOCKED honestly on pre-cache 68% failure / your directive encoded as durable 6th pre-dispatch checklist item (Skunkworks SCHEMA-VET-owned)

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18 (post-compaction)  **Re:** post-compaction state + your "checkpoint/restart-if-failed" directive landed + canonicalized. ASCII; fname_v2.

## Bottom line (one sentence)

Substrate state cleanly progressed across the compaction boundary: **FrameNet ARC-3 ingest LANDED CLEAN** (1221 SEMANTIC_FRAME atoms + 2070 typed frame-to-frame edges; exact-match-declared; integrity preserved) + **your "must restart if failed" directive landed mid-window and is now ENCODED** as a durable **6th pre-dispatch BLOCKING checklist item** (Skunkworks-owned SCHEMA-VET condition: kill-restart test demonstrates resume, doesn't assert it) + **A2-v6 honestly BLOCKED** (the same A2 pre-cache that motivated your directive died at 68% chunk_27/42; rebuilding it CHECKPOINTABLE is the first application of the new standing rule).

## What landed cleanly post-compaction

**FrameNet v1 ARC-3 ingest -- LANDED clean.**
- Atom count: 41,330 -> **42,551 (+1,221 exact)** matching declared SEMANTIC_FRAME atoms
- Concept-dir relations: +2,070 FRAME_* typed edges (Inheritance / Using / Subframe / Perspective_on / Precedes / Inchoative_of / Causative_of / See_also / ReFraming_Mapping / Metaphor) -- 10 rel_types data-driven from nltk, not 8 as our scaffold initially guessed (Exp-Dev caught + fixed pre-ingest)
- 0 ID-collisions, declared==actual edge-readback gate PASS, RESEARCH_FINDING tier (CERT unchanged)
- Schema-add commit f775fc01 (SEMANTIC_FRAME AtomKind + 10 FRAME_* rel_types verify-loads OK)
- ARC-3 substrate-autonomy direction OPEN: substrate now has a frame-semantic shell (predicate/argument-structure ontology) alongside WordNet's hypernym/PART_OF lexical-relation shell. Orthogonal axis from depth-cliff investigation.

**Testbed 2nd-witness still PENDING** for FrameNet landed-verify (clean substrate-side; integrator-side independent count incoming when bandwidth frees).

## Your "restart-if-failed" directive -- ENCODED as canonical 6th checklist item

You said (verbatim, routed by Skunkworks):
```
"we should enforce that all experiments like this not only are more carefully
 designed, but have intrinsic data savings so they can be restarted if failed"
```

**Encoded form (now DURABLE across sessions):**

**Item 6** of the pre-dispatch BLOCKING checklist (joining items 1-5 from 2026-06-17): **LONG CELLS CHECKPOINT + RESUME + KILL-RESTART-TEST PASS.**

Scope (proportionate): in-scope = cells expected to run >~10 min OR processing work in N>1 units (chunks/stages/seeds). Short cells exempt. Required parts:
1. **CHECKPOINT** per completed unit (per-chunk shard / per-stage state) at a deterministic path -- NOT only at the end.
2. **RESUME** -- on re-invoke, scan checkpoints, skip completed, continue. Idempotent.
3. **ASSEMBLE** final artifact from checkpoints.

**Verification = the KILL-RESTART TEST (BLOCKING pre-dispatch):** run cell, kill mid-run after >=1 unit completes, re-invoke, confirm it resumes from last checkpoint (skips completed; doesn't redo) + produces correct artifact. **A long cell that hasn't passed the kill-restart test is NOT dispatch-ready.**

This is **verify-the-referent for resumability** -- the same principle as our edge-read-back gate. We demonstrate the property; we don't assert it. Skunkworks's tightening (SCHEMA-VET-owned + dispatch-time, not atomize-time): correct -- the 7-gate self-cert engine is atomize-time cert-classification; resumability is a cell-design/dispatch property. Routes correctly to the dispatch pipeline.

The "more carefully designed" half of your ask is also explicit now: **mandatory SCHEMA-VET (READ + RUN the cell code; verify-referent on the CODE not the reported number) for any non-trivial cell before dispatch.** The A2 saga (7 distinct dispatch causes over today) + T3 Phase A edge-flip bug both show shallow review masks dispatch-fatal bugs even with clean dry-runs.

## A2-v6 honestly BLOCKED (and that's the right state)

The A2 pre-cache run that motivated your directive **failed at 68% / chunk_27/42** -- the npz writes only at the end, so all ~60 min of prior work was lost. Orchestrator self-caught and reported BLOCKED (commit 9de33b9e).

Skunkworks's pre-directive guidance was "re-dispatch with 7200s timeout" -- but Skunkworks has now REVISED that as a band-aid (survives one run; a kill at chunk_41 still loses everything). The robust fix per your directive: **rebuild as checkpointable** (per-chunk shards at `cache_dir/<content_hash>/chunk_<k>.npz` as each 1000-atom chunk completes). Effect: any future kill costs <=1 chunk (~100s), not 68%.

**Sequence now:**
1. Exp-Dev rebuilds A2 pre-cache as checkpointable + kill-restart-tests it
2. Skunkworks SCHEMA-VETs incl. the kill-restart test
3. Orchestrator dispatches the resumable warm-cache build
4. v6 finally runs -> Skunkworks verdict-VET (B-beta gate)

This is the FIRST APPLICATION of the new standing requirement and becomes the template for T3 Phase B B-alpha BROAD v2 (also long-running) and every future long cell.

## What this means for the 20h plan you ratified

- **FrameNet landed:** Skunkworks's ORTHOGONAL #2 toggle now in substrate.
- **T3 Phase A APPLY:** STILL QUEUED (1339 LEXICON completeness atoms + 2219 HYPERNYM edges; SERIAL same-Store after FrameNet's Testbed 2nd-witness or directly per the re-VET PASS). When it lands: atoms 42,551 -> 43,890. Completeness-only ruling (Skunkworks's tighter rule per by-construction trap mitigation).
- **T3 Phase B BUILD-TIME:** now gets the checkpoint+resume condition applied. SCHEMA-VET will verify before dispatch -- which is healthy slowdown that prevents losing 90-min runs.
- **A2-v6:** delayed by ~the rebuild time (probably <1 hour), but the rebuild is gain-of-substrate-discipline that pays back across all long cells forever after.

**Honest framing:** your directive turned a frustrating one-off failure (A2 chunk_27 death) into a durable discipline upgrade. Trading ~1 hour today for never-losing-a-long-run-this-way again is a clean trade. Composes with the C2 producer-attest + consumer-enforce pattern (the engine grows from its own catches; this catch grew the dispatch-discipline).

## Cert-discipline arc (today's pattern continuing)

The 6th-checklist-item-from-a-failure is structurally the same as the 5 of 7 self-cert engine gates we LIT today from our own catches:
- gate0-both-ends bootstrap (run-completeness)
- discrimination-regime (audit-79)
- working-baseline-cliff (B-delta v1)
- corpus-completeness (A2 over-flag)
- multi-hop-provenance (A1/ARC-1 HARD_FAIL hallucinated reasoning-path)
- verdict-mappable (190c lesson)
- phantom-dependency (audit 2+4)

Each gate = a catch that became a permanent guard against the same failure class. The 6th pre-dispatch item = the dispatch-discipline analog. **Substrate-autonomy at the meta-layer**: our integrity catches its own custodians; our process catches its own gaps. You've now seen this pattern work end-to-end in one session day.

## What I'm waiting on / who's blocking

- **Exp-Dev:** (1) A2 pre-cache CHECKPOINTABLE rebuild + kill-restart-test (Prover-lane). (2) T3 Phase A APPLY (if not auto-routing post-FrameNet 2nd-witness). (3) Apply checkpoint+resume pattern to T3 Phase B.
- **Skunkworks:** (1) FrameNet landed-verify (post-Testbed 2nd-witness). (2) SCHEMA-VET A2 pre-cache rebuild incl. kill-restart. (3) T3 Phase A landed-verify (next).
- **Testbed:** FrameNet ingest 2nd-witness (independent count + integrity check). Kill-restart test for long cells if bandwidth.
- **Orchestrator:** hold A2 v6 dispatch until checkpointable rebuild + SCHEMA-VET land; then dispatch + verify-OUTPUT-not-liveness on the npz file.
- **USER (you):** nothing currently gated on your sign-off. 6th checklist canonicalization is a Director-Skunkworks operational decision under the discipline-encoding mandate you've already given us. Heads-up on the next visibility moment: T3 Phase A landed-verify (after which T3 Phase B build kicks off and starts the depth-cliff verdict run; that's the centerpiece deliverable of the 20h plan).

## Memory pointers

- USER directive memorialized: [[feedback_long_cells_must_checkpoint_resume_restartable_USER_2026-06-18]] (already-locked in my durable index)
- 5-item base checklist: [[reference_remote_dispatch_cell_readiness_checklist_2026-06-17]] (now extended with item 6 in the canonical note filed separately to ALL)
- Pattern: this is the 9th USER-locked discipline rule encoded this session

-- Research (Director)
