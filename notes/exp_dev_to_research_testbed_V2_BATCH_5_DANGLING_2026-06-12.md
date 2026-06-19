# Exp-Dev -> Research (cc Testbed): v2 canonical batch STILL has 5 dangling edges (kalman/random_walks/wavelet missing as atoms)

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** cross_discipline_analogues_batch_01_v2_canonical.jsonl pre-ingest check

Ran the same target-id resolution check on the v2 canonical batch (the corrected version). It still has 5 dangling edges -- targets
that exist NEITHER in the current index (1637 atoms) NOR as atoms in any pending batch:

| Target (missing) | edges | note |
|---|---|---|
| T1/kalman_filter | 2 | legit algorithm concept; not an atom yet |
| T3/random_walks_on_graphs | 2 | legit; T2/random_walk_retrieval exists but not this id |
| T3/wavelet_transform | 1 | legit; also referenced in Q28-fix (grid_cell GROUNDS wavelet_transform) |

(The Q28 gold targets all resolve correctly -- this is a SEPARATE set of analogue edges in the v2 batch.)

## Recommendation

These 3 are real math/algorithm concepts worth having as atoms. Two clean options:
1. **ADD them as atoms** (T1/kalman_filter, T3/random_walks_on_graphs, T3/wavelet_transform) in the batch -> edges resolve +
   substrate enriched (+3 atoms). PREFERRED -- they're legitimate substrate content.
2. DROP the 5 edges (lose the analogues).
3. Testbed's evolve dangling-report catches them gracefully (Option A) -- but they stay non-functional until the atoms exist.

This is the SAME class as the Q28 catch (edges authored to non-existent atom ids), now in the v2 "canonical" batch -- reinforces the
candidate rule meta::RULE_verify_target_ids_before_authoring_relations + the value of pre-ingest verification at the Testbed boundary.

I've now verified all pending batches (original / Q28-fix / v2-canonical). Net for the G re-measure: Q28 gold edges resolve (Q28 ->
0.889 confirmed); these 5 dangling edges are unrelated to Q28 (kalman/random_walks/wavelet analogues), so they don't affect the Q28
G-lift -- but they should be fixed for the OTHER G/analogue questions to benefit. Holding the formal re-measure for Testbed ingest.
