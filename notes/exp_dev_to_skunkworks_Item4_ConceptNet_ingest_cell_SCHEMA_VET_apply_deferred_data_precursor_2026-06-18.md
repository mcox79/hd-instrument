# EXP-DEV (Prover) -> SKUNKWORKS (pre-dispatch SCHEMA-VET) + Research (data-acquisition precursor) + Orchestrator (FYI): Item 4 ConceptNet ARC-3 ingest cell BUILT (apply DEFERRED). schema-add (CONCEPT_NODE + 29 CN_* first-class rel_types) verify-loads OK; self-test + kill-restart-test PASS. Requesting SCHEMA-VET; flagging the ConceptNet-data-acquisition precursor.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (data precursor), Orchestrator (FYI)  **Date:** 2026-06-18  **Re:** Item 4 ConceptNet cell SCHEMA-VET. ASCII; fname_v2. Cell: tools/substrate_conceptnet_ingest_v1.py

## Built per the assignment conditions
- **CONCEPT_NODE AtomKind** added (backend/substrate_index/schema.py; sibling structural guards = SEMANTIC_FRAME/SCIENCE_CONCEPT: NO algebra -> excluded from axiom_term; provenance_quality=RESEARCH_FINDING ingest tier). verify-loads OK; axiom_term 206 preserved.
- **FIRST-CLASS rel_types** (NEVER metadata-on-RELATES; the edge-metadata-drop lesson): IsA->IS_A + PartOf->PART_OF reuse existing; the other 29 ConceptNet relations are new CN_* rel_types (CN_RELATED_TO/CN_USED_FOR/CN_CAPABLE_OF/CN_AT_LOCATION/CN_CAUSES/...). REL_MAP = 33 ConceptNet relations -> rel_types; unmapped relations SKIP (counted), NOT coerced.
- **Namespaced** (id=CN_<concept>) -> 0 cross-corpus collision; lemma-overlap with WN_/LEXICON is EXPECTED not collision (a 0-collision gate halts if a CN_ id already exists under a different kind).
- **algebra=None** structural guard.
- **Tier**: RESEARCH_FINDING (ingest tier; FrameNet precedent).
- **6th-checklist (ConceptNet is large/long-running):**
  - BATCHED atom-add (accumulate -> single save_atoms; NOT per-atom add_atom O(n^2)) -- at ASSEMBLE time.
  - CHECKPOINT/RESUME/ASSEMBLE: process CSV in CHUNK-row blocks -> per-chunk SHARD files + progress; restart SKIPS existing shards; assemble loads all shards -> dedup -> single-flush. Both resumable AND single-flush (the pre-cache item-6 pattern adapted).
  - KILL-RESTART-TEST (--resume-test): mock 5 chunks; write 2 shards; "die"; re-run; confirmed RESUME skip-2 + process-3 + assemble (15 edges). DEMONSTRATED, not asserted.
- **--self-test** PASS (parse/map/en-filter/unmapped-skip/low-weight-drop/atom-id on synthetic triples; no data, no Store).
- **Gates on --apply**: edge-budget readback (intended.issubset) + 0-phantom (every edge endpoint a CN_ atom we add -> self-consistent) + 0-collision + axiom 206 + cap_pres 6/6 + CERT unchanged.

## DATA-ACQUISITION PRECURSOR (Research / infra lane)
The cell reads the canonical ConceptNet 5.7 english assertions CSV (conceptnet-assertions-5.7.0.csv[.gz]; TSV /a/.. /r/Rel /c/en/start /c/en/end {json}). It is NOT present locally (data/conceptnet/assertions.csv). The existing backend/kb/conceptnet_ingest.py uses HF datasets streaming (peterwilli/conceptnet5) but targets a DIFFERENT (bge-KV) store; for the typed-atom ingest a local CSV dump is the clean offline source (matches the WordNet/FrameNet nltk-offline precedent + the held-out firewall). **Routing the data-need to Research/infra:** acquire conceptnet-assertions-5.7.0.csv.gz -> data/conceptnet/. (Apply is DEFERRED until push-fix anyway, so this is not blocking the sprint; the cell logic is verified without data via self-test + resume-test.)

## APPLY DEFERRED (USER lean (a) ratified)
Build now (done; productive parallel work); apply when (1) push-pipeline restored AND (2) the ConceptNet CSV is acquired. Until then the schema-add stands (enum additions, non-destructive, verify-loads OK) and the cell is SCHEMA-VET-ready.

## Standing (9th rule)
- Skunkworks: Item 4 ConceptNet cell SCHEMA-VET (CONCEPT_NODE + the 29 CN_* rel_type granularity OK? checkpoint-resume/assemble sound? gates sufficient? unmapped-skip-not-coerce OK?). + the Item 1 tier-call + A2 v6 cert-call still pending.
- Research: ConceptNet data-acquisition precursor (the CSV dump) -- the research/infra-lane input for the deferred apply.
- ME (Exp-Dev): Item 4 cell built + routed. All 20h-sprint un-gated build work for me is now done (Items 1/2/3 + A2 v6 VET + Item 4 cell). Reactive on the cert-VET/tier-call queue.
- Waiting on: Skunkworks (Item 4 SCHEMA-VET + Item 1 tier-call + A2 v6 cert-call), Testbed (Item 1 2nd-witness), Research/infra (ConceptNet data), USER/infra (push-fix -> C/43892 + ConceptNet apply).

-- Exp-Dev (Prover)
