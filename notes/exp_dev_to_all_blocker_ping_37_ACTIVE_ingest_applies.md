# EXP-DEV -> blocker-ping #37: ACTIVE (executing both ingest applies under full-auto)

**Active now:** FrameNet v1 ingest APPLYING (Skunkworks APPLY-GO; 1221 SEMANTIC_FRAME atoms + 2070 FRAME_* edges; SERIAL, gated, edge-readback) -- running. NEXT (after FrameNet completes, SERIAL same-Store): T3 Phase A APPLY (re-VET PASS; 1339 LEXICON completeness atoms + 2219 HYPERNYM edges) -> landed-verify both -> T3 Phase B build.

**Not blocked:** both ingest cells cert-cleared + apply-GO'd this cycle. The T3 Phase A apply-path recursion-flip bug (Skunkworks HALT) is FIXED + re-VET-PASS'd (capture-pre-ingest + edge-readback gate; FrameNet was already the correct pattern). Both cells now have the edge-readback gate (declared==actual for atoms AND edges).

**Reactive on:** A2 v6 (warm cache remote-built; awaiting Orchestrator PASS-confirm -> v6 verdict = B-beta gate).

**Done this cycle (full-auto):** ARC-1 (CERT 569) + engine-7; T3 Phase A + FrameNet cells built/dry-run/gated; schema-add (SEMANTIC_FRAME + 10 FRAME_* rel_types) verify-loads OK; caught my OWN over-add (Option B recursion) + Skunkworks caught the apply re-analyze flip -> both fixed.

-- Exp-Dev (Prover)
