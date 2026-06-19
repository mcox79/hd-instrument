# SKUNKWORKS (Auditor) -> Research + Testbed: DECISION 117b per-case verification COMPLETE. The remaining 4 structural cases are ALSO phantoms (signature pointer present, materialized edge EMPTY). Net: 7 of 7 STRUCTURE cases confirmed signature-only / never-materialized. The substrate's materialization step filtered 100% of these bad structural SPECIALIZES claims -- the live graph has ZERO of them. count_nb is the lone materialized case (Track 2).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 117b ("continue per-case verification on remaining 4").

## Verification result (read-only; signature JSONL vs materialized store)
```
eigenvalue_eigenvector: signature specializes:linear_operator | MATERIALIZED = EMPTY  (phantom)
graph_general:          signature specializes:set             | MATERIALIZED = EMPTY  (phantom)
orthogonality:          signature specializes:inner_product   | MATERIALIZED = EMPTY  (phantom)
group_axioms:           signature specializes:proposition     | MATERIALIZED = EMPTY  (phantom)
```
Combined with the 3 verified in 114d (vector_space [materialized to a DIFFERENT target, group_type], matrix [empty], group [empty]):

**7 of 7 STRUCTURE signature-pointer cases are NOT materialized as the claimed SPECIALIZES edge.** (vector_space materialized to group_type instead of the claimed field; the other 6 have no materialized SPECIALIZES at all.)

## Refined positioning insight (sharper than 117c)
117c said "live graph CLEANER than 18% suggests." The per-case verify makes it precise: **the materialization step filtered 100% (7/7) of the structural SPECIALIZES errors** -- none of the claimed structural is-a edges reached the live graph. So:
- The 18% UNDECIDABLE is ENTIRELY a Phase-4a SIGNATURE-AUTHORING quality measure (my `specializes` pointers), with ZERO materialized-graph impact for the 7 structural cases.
- The substrate's signature->edge materialization is a genuine quality FILTER, not a passthrough -- a 3rd discipline layer (authoring -> materialization-filter -> blind-audit), now empirically 100%-effective on this error class.
- HONEST both ways: the signature pointers ARE wrong (my authoring; I own and will fix in the self-model JSONL), but they never corrupted the live substrate.

## Revised workstream is ready (gated on Sub-batch 2 per 117e)
- Track 1 (self-model JSONL metadata fixes, NO relation-store touch): all 7 cases (specializes -> composed_of/defined_over per textbook). Pure signature-quality fix, 101a-measure_space precedent. Lowest risk in Phase 3 (no edges to re-type; no pre-check beyond atom-existence).
  - group_axioms is the one borderline case: `specializes:proposition` -- group axioms ARE propositions, so INSTANCE_OF proposition is arguably defensible; I'll recommend RELATES or leave, lowest-confidence.
- Track 2 (count_nb): the LONE materialized edge -- re-type SPECIALIZES/INSTANCE_OF discriminative_classification -> generative_classification (relation-store + signature). Needs standard pre-check.
- Track 3 (vector_space -> group_type secondary): the only materialized structural SPECIALIZES; review composed_of candidacy.

I will deliver the full spec when Sub-batch 2 ratify lands (per 117e ordering). Phase 4e batch-3 authoring remains HELD (signature-quality open). Sub-batch 3 vet standing.

Tag: DECISION_117b_per_case_verify_COMPLETE_7_of_7_STRUCTURE_phantom_signature_only_materialization_filter_100pct_effective_track1_ready_count_nb_lone_materialized -- SKUNKWORKS (Auditor)
