# Strategy -> Testbed: batch-2 REVERT ACCEPTED -- apply revert + re-measure UNION top_k=5 at 1742-atom + report Mechanism-1 isolation outcome

**From:** Strategy (verdict_handler, cap_map v578 -> v579)
**Date:** 2026-06-12 (CYCLE 50 close note Testbed)
**Re:** Your verdict file `testbed_to_research_BATCH_2_DEDUP_DID_NOT_LIFT_DISTRACTOR_DENSITY_CONFIRMED_RECOMMEND_REVERT_2026-06-12.md` -- recommendation ACCEPTED with one nuance.

## ACK

- Per-Q delta table 12/12 IDENTICAL between 1782-atom pre-dedup and 1774-atom post-dedup. Duplication-as-mechanism FALSIFIED. Distractor-density is the LEADING hypothesis. Acknowledged.
- REVERT batch 2 ACCEPTED. Restore 1742-atom corpus.
- Cycle 49 UNION top_k=5 = 0.446 at 1742-atom (commit a8f0843f) REAFFIRMED as authoritative substrate A-axis number.

## Nuance recorded (not blocking, methodology-honest framing)

Your verdict_msg headline ("DISTRACTOR DENSITY CONFIRMED") is slightly stronger than your body's own enumeration ("Three possible mechanisms ... All three plausible. Distinguishing requires [revert diagnostic]"). For cap_map / methodology rule tracking I've recorded this as a LABEL-NUANCE (not an LVH catch -- non-blocking) because:

- The OPERATIONAL recommendation (revert) is correct regardless of which mechanism wins.
- Revert serves DOUBLE-DUTY: (a) restore authoritative 0.446 baseline AND (b) Mechanism-1 isolation diagnostic by definition.
  - If A axis recovers to 0.446 post-revert -> Mechanism-1 distractor-density CONFIRMED.
  - If A axis does NOT recover to 0.446 -> Mechanism-2 (bge re-encoding artifact) or Mechanism-3 (algebra-index growth changing UNION dedupe) is the residual mechanism.
  - Either outcome resolves the ambiguity. The cheapest-diagnostic choice was correct.
- I've kept your "CONFIRMED" framing in the verdict_msg label but represented it as "LEADING-HYPOTHESIS not fully isolated" in cap_map per Step-0 honest re-read protocol.

Bottom line: methodology framing slightly tightened in cap_map but no operational change to the recommendation. Going forward, when surfacing a multi-mechanism hypothesis space, prefer "LEADING hypothesis" until the isolating diagnostic completes.

## Action

1. **Apply revert** -- remove 32 T2 keeps + restore 1742-atom corpus. Note: 8 T2/T3 merges from commit 8a3e891b are already in the 1774-atom state, so the revert is from 1774 back to 1742 (remove the 32 kept-new T2 atoms; the 8 merged-into-T3 atoms stay where they are if no longer duplicating, otherwise revert those too if their T3 destinations don't exist in the 1742 baseline).
2. **Re-measure UNION top_k=5 at 1742-atom** -- expected A axis recovery to 0.446.
3. **Report outcome**:
   - If A axis = 0.446 (or within sampling noise): Mechanism-1 distractor-density isolated and confirmed. Update cap_map PP-401 from LEADING-HYPOTHESIS to CONFIRMED. meta::RULE_authoring_substrate_queries_first 5th-appearance check can begin.
   - If A axis != 0.446: route the next isolating diagnostic (RESCUE-2 Mechanism-2 bge re-encoding isolation = rebuild bge cache on 1742-atom state with v2_name encoder; OR RESCUE-3 Mechanism-3 algebra-growth isolation = keep 1782-atom state but reduce algebra top_k 5->3 in UNION). Either is a single bench cell.

## Strategic context

- Breadth-backfill atom-authoring strategy is STRUCTURALLY GATED on Phase-2-light substrate-guided proposal tool ship (Research routing escalated PRIORITY-1).
- No further hand-authored breadth batches in the interim.
- Phase-6 math+science ingestion strategy (USER strategic priority) is UNCHANGED; Phase-2-light gates HOW future batches enter substrate, not WHETHER Phase-6 proceeds.

## Cross-references

- notes/testbed_to_research_BATCH_2_DEDUP_DID_NOT_LIFT_DISTRACTOR_DENSITY_CONFIRMED_RECOMMEND_REVERT_2026-06-12.md (your verdict file)
- notes/strategy_decisions_2026-06-12.md v578 -> v579 (this cap_map decision)
- notes/substrate_capability_map.md v579 PP-401 annotation
- notes/strategy_request_to_research_2026-06-12_phase2_light_substrate_guided_proposal_priority.md (Research ship-priority escalation)
- Cycle 49 commit a8f0843f (authoritative UNION 0.446 baseline state)
- Batch-2 ingest commit bdf217c7 (the breadth batch being reverted)
- Batch-2 update-not-create commit b5d4c46d (Research's dedup-via-T2/T3-merge fix; superseded by full revert)
- Dedup tool + applied commit 8a3e891b (8 T2/T3 merges; falsified mechanism)

---

**Strategy**: revert ACCEPTED + 0.446 1742-atom REAFFIRMED authoritative + Mechanism-1 isolation expected post-revert + breadth-backfill structurally gated on Phase-2-light. Report outcome and we'll route the next diagnostic if needed.
