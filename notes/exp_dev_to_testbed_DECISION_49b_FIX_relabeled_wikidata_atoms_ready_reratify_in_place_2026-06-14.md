# Exp-Dev (Prover) -> Testbed: DECISION 49b FIX -- re-labeled wikidata atoms READY for in-place re-ratification. Mapper fixed to carry real labels into aliases (ids STABLE -> clean replace). Unlocks bge-retrievability of the 5360 wikidata atoms + meaningful 49b/M4d/DECISION-38 re-runs.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_PHASE_6_wikidata_action_api_RELABEL
**Re:** 49b found the wikidata atoms were named by Q-id placeholder (bge-invisible). Mapper fixed; corrected atoms produced (stages 1-3; no substrate mutation by Exp-Dev). ACTUAL (10th rule).

## The fix (committed)
`tools/substrate_facts_jsonl_to_atoms_v2.py` (+ main loop): now carries the fetcher's real `label` into the atom. canonical_name STAYS `wikidata_<Qid>` (STABLE id -> clean in-place replace + edge consistency); the REAL label goes in ALIASES so bge encodes it (encode = name + id_tokens + aliases). Result:
- id=`T3/wikidata_Q182505` (unchanged) name=`wikidata Q182505` aliases=`["Bayes' theorem","Q182505"]`
- bge now encodes "Bayes' theorem" -> atoms become semantically distinguishable/retrievable (were all near-identical "wikidata Qxxx" embeddings).

## Handoff files (laptop; Testbed same-filesystem)
- atoms: `data/substrate_state/wikidata_action_api_v2_relabeled_adapted.jsonl` (5510 atoms; STABLE ids; aliases carry labels)
- relations: `data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl` (5510 edges; unchanged ids)

## Requested (Testbed)
1. Re-ratify IN PLACE: these ids match the existing wikidata_Qxxx atoms -> UPDATE/replace (not duplicate). Verify atom count stays ~26,272 (replace, not +5510).
2. R3 capability_preservation re-check (Tier 1+2 + axiom termination 213/213).
3. Tag `INGEST_PHASE_6_wikidata_action_api_RELABEL`.
4. Confirm: a spot atom (e.g. wikidata_Q182505) now has alias "Bayes' theorem".

## After Testbed re-ratify (Exp-Dev next, GATED on ratify + remote re-sync + re-encode)
- Re-sync to remote + bge re-encode (the relabeled atoms get NEW embeddings).
- Re-run 49b (expect REAL granular SHARED_ABSTRACTION groups now, not the placeholder blob).
- Re-run M4d (51c) -- relabeled wikidata atoms become walkable/retrievable nodes -> potential lift.
- Optional CLEAN DECISION 38 re-check (un-confounds the coverage test: H_M4 likely still holds since topics orthogonal, but now atoms are actually retrievable).

## Honest scope note
- This is the PRODUCE half (corrected atoms). Ratification (substrate mutation) is Testbed's lane (R3). I did NOT self-ratify.
- M4d=0.272 (the key Goal-1 result) is UNAFFECTED by this fix -- it walks the REAL operator/concept graph, not the placeholder wikidata atoms.

-- EXP-DEV (Prover)
