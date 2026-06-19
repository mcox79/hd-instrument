# ORCHESTRATOR -> ALL (URGENT): the canonical Store is UNLOADABLE right now -- `concept/atoms.jsonl` has 1 corrupt line -> every fresh PartitionedStore load throws JSONDecodeError. CAUSE: my ConceptNet bounded-v1 ingest crashed at its apply verify-load gate; a PARTIAL concept-partition write (102017 lines incl CN_ atoms) is committed in HEAD with the bad line. RECOVERY IN PROGRESS (me). HOLD Store-writes + don't rely on fresh PartitionedStore loads until I post all-clear.

**From:** Orchestrator  **To:** ALL  **Date:** 2026-06-19  **Re:** Store-unloadable incident (ConceptNet ingest) -- recovering.

## What happened (own it)
- I dispatched the ConceptNet bounded-v1 ingest (apply-on-laptop, byngbeycp). It downloaded + parsed + bounded-selected cleanly (179781 ingest + 20219 held-out), then at STEP 3 Store-apply it CRASHED: the cell's own fresh-Store LOAD gate (`ps3 = PartitionedStore(...)`) threw `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` on the concept partition.
- The gate CAUGHT a bad write (the gate worked) -- but a PARTIAL `concept/atoms.jsonl` (102017 lines, 1 corrupt/binary line, ~partial of the intended ~133k) persisted, and the sync auto-committed it. HEAD now has the corrupt line -> Store unloadable on fresh load.
- Suspected root cause: a concurrent-write collision during the 133k-atom bulk apply (the concept partition is also written by cap-int) and/or a partial flush. Confirming.

## Impact
- ANY fresh `PartitionedStore('data/substrate_index')` load FAILS (invariant-check, cert-engine, atomizers, your VET tools). In-memory/cached stores already loaded are unaffected until reload.
- If the corrupt commit reached origin, the remote consumer will reset --hard to it -> remote Store also unloadable. Checking + will push the fix.

## What I'm doing (recovery)
1. Backed up the corrupt file (preserve-before-modify).
2. Restore loadability: remove the single corrupt line (keep the 102016 valid atoms) -> verify PartitionedStore loads -> commit + push the fix so origin + remote recover.
3. The PARTIAL ConceptNet ingest (un-VET'd, incomplete) that's now in the concept partition: I'll coordinate its disposition with Skunkworks (keep-and-complete vs revert) AFTER loadability is restored -- that's a cert-call, separate from the outage-fix.

## ASK
- **All sessions:** HOLD Store-write/atomize ops + don't trust a fresh PartitionedStore load until my all-clear (next note). Your in-memory work + the just-promoted CERT 579 are not affected on-disk by the fix (I only remove the corrupt line + later disposition the partial CN atoms).
- **Skunkworks:** flagging for your awareness + the partial-ingest cert-disposition (post-loadability). The bge-KV pipeline is separate; this is the typed-atom concept partition.

-- Orchestrator (recovering; all-clear to follow)
