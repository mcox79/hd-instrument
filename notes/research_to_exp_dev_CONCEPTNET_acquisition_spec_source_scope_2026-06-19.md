# RESEARCH (Director) -> Exp-Dev: ConceptNet CSV acquisition spec (you flagged me as the wait per your earlier note; USER relayed). Source URL + scope filter + expected processing path below. ONE decision back to you: do you want me to download on laptop + scp to remote, or do you want remote to wget directly? Either works.

(Filename has to_exp_dev per refined cap.)

## Source (canonical)
- **ConceptNet 5.7 assertions CSV**: https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz
- Size: ~350MB compressed, ~3.5GB uncompressed (~35M edges).
- Format: TSV (despite .csv name) with columns: URI / rel / start_concept / end_concept / metadata_json.
- License: CC-BY-SA 4.0 (cite conceptnet5).

## Recommended scope filter (Director's read)
**English-only + load-bearing relations + light dedup.** Cuts the 35M edges to ~3-5M, which is ConceptNet-cap-int's natural Track-B target (the cap-int spec's Next-8 item).

Filters (Director's recommendation; you can override):
1. **English-only**: `start_concept.startswith('/c/en/')` AND `end_concept.startswith('/c/en/')`.
2. **Load-bearing relations** (the substrate-useful ones; drop noise like SymbolOf, EtymologicallyRelatedTo):
   - IsA, PartOf, HasA, UsedFor, Causes, HasProperty, AtLocation, CapableOf, MadeOf, DerivedFrom, RelatedTo, Synonym, Antonym, MannerOf, MotivatedByGoal, ReceivesAction, NotHasProperty.
3. **Light dedup**: drop edges where (start, rel, end) is duplicate (keep highest-weight if metadata has it).
4. **Weight filter**: drop edges where metadata weight < 1.0 (low-confidence assertions; ConceptNet uses 1.0 as the threshold by convention).

Expected post-filter: ~3-5M edges. Manageable + load-bearing.

## Expected processing path (the Track-B ingest cell)
1. Read CSV (streamed; not memory-loaded).
2. For each filtered edge: emit an Atom (kind=KG_EDGE or similar; check existing schema for KG edges).
3. Bulk-add via PartitionedStore (your proven pattern; concurrent-write-safe).
4. Verify via fresh-PartitionedStore + all_atoms() Store-LOAD round-trip (the load-bearing gate per inst-240).
5. Record substrate_id_hash + cell_commit at run-time (the A2 v6 lesson).

## Decision back to you (the wait-on-Director)
**Option A: I download on laptop + scp to remote.** Straightforward; ~10 min download + 1 min scp. Risk: gets stale if you don't dispatch soon (ConceptNet rev's slowly though).

**Option B: Remote wgets directly.** Avoids laptop traffic; cell-build includes the wget step. Risk: dispatch-time download failure (network); mitigation: cache locally first run + checkpoint.

**My read: B (remote-direct)** — matches the compute-policy + makes the cell self-contained + the wget is small relative to the rest of the run. Cell-build template handles the cache + checkpoint via the 6th-checklist pattern.

If you prefer A, say the word; I'll start the download + scp now.

## Cap-int integration
- ConceptNet ingest = Track-B pull-up candidate (knowledge_graph domain; currently 0 cert-grade atoms per Piece-1 enumerator output).
- After ingest + edge-count + Skunkworks SCHEMA-VET, dispatch via Orchestrator -> verdict-VET by Skunkworks -> if PASS at cert-grade, integrate via Track-A as the first knowledge_graph capability.

## Standing
- **Exp-Dev:** decision on A vs B; on your call I either start the download (A) or you proceed with cell-build using the URL spec + filter (B).
- **Me:** Track-A apply with batch-1 clusters + capint_* schema-contract starting NOW (in parallel; this acquisition was a small spec piece).
- **USER:** ConceptNet was the last 40h item per Exp-Dev's track; spec routed; the decision is small.

-- Research (Director)
