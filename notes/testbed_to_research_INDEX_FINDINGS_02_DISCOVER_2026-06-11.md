# Testbed -> Research: substrate self-index discovery findings #2

**From:** Testbed  **Date:** 2026-06-11 evening
**Re:** First discovery run; substrate self-index surfaced a redundancy candidate
       in your own batch-01 corpus that warrants your inspection before batch 02

## Headline

The substrate self-index's `discover.cluster_unification()` module flagged
**math::T2/bundling and math::T2/superposition** as semantically near-identical
(pairwise cosine similarity = **0.863** in bge-large embedding space, threshold
0.85). They are both members of the family-tag `T2_FAM/superposition_aggregation`.

This is the substrate analyzing its own corpus and surfacing a likely
redundancy/merge candidate -- exactly the "help us find better solutions"
capability the user asked for.

## Your call

Two options:
1. **Merge**: collapse the two atoms into one with the better description and
   alias set, and re-point any future relations to the survivor
2. **Distinguish**: sharpen both descriptions so they encode a genuine
   distinction (e.g., bundling = sum-then-normalize; superposition = sum-only
   weighted-by-count, no implicit normalization)

I suspect (2) is correct -- HRR literature distinguishes them -- but the
current descriptions don't capture the distinction sharply enough for bge-large.

## Total discoveries this run

- 81 findings (30 warnings, 36 suggestions, 15 info)
- The bulk (warnings + most suggestions) are `structural_gap` flagging that
  atoms have no outgoing typed-edge relations of any kind -- this is expected
  because batch 02 with relations hasn't landed yet. They'll auto-resolve once
  relations ship.
- The structural_gap findings are still useful as a baseline -- they tell you
  which atoms NEED edges by next batch.

## Full structural-gap breakdown (will auto-resolve when relations land)

- Cross-corpus orphan math atoms: ~25 (every T2/T3/T4 atom has no concept
  user yet, as expected -- concept corpus delivers Day 2)
- Atoms missing USES out-edges: ~25 (same root cause)
- Atoms missing DUAL out-edges: 5 (substrate primitives that should have
  algebraic duals -- fhrr_bind/fhrr_unbind pair will validate this once you
  ship the DUAL relation)
- Atoms missing COMPOSES out-edges: 8 (mostly T1 foundational; expected)
- Underutilized relation types: ALL 13 relation types currently have 0 edges
  (expected pre-relations-batch)
- Tier imbalance: T3 has 25 atoms, design intent ~400; T2 has ~25, intent ~30
  -> T3 under-filled per refinement-1 granularity (will resolve with batch 03)

## Specific discoveries that AREN'T expected gaps

### 1. bundling / superposition redundancy (already discussed above)

The cluster_unification finding above. Highest-priority signal in this run.

### 2. Cross-corpus orphans = next-build candidates list (for after concept corpus lands)

Once your concept corpus drops, these math atoms will tell us which substrate
primitives have no current concept-level capability exercising them. Each
one is a "potential next concept to build" candidate. From batch 01 we can
already pre-list the strongest candidates (T3 sub-ops with rich algorithmic
content that don't yet have a substrate-architecture concept attached):
- T3/hungarian_assignment (no concept user yet -- candidate for a
  bipartite-matching capability concept)
- T3/jonker_volgenant (same)
- T3/chu_liu_edmonds (graph MST -- candidate for dependency-tree concept)
- T3/em_algorithm (no concept user -- candidate for clustering/mixture
  capability concept)
- T3/forward_algorithm / T3/backward_algorithm (no users -- candidate for
  HMM-state-inference concept)

The discover engine flagged them automatically with confidence 0.65 each
plus a suggested_action template.

## Mechanism check

The discover engine `cluster_unification` did the following autonomously:

1. Loaded all 60 atoms via PartitionedStore.math
2. For each FAMILY_TAG atom, looked up its `members` metadata list
3. Fetched semantic vectors for each member via AtomEncoder cache
4. Computed pairwise cosine similarity within the family
5. Flagged any pair >= 0.85

This is substrate-grounded discovery, NOT an LLM "look at these and decide
if they're similar" -- the similarity score is the bge embedding cosine, and
the threshold is hand-coded. The substrate's recommendation to merge/sharpen
is structurally derivable.

## What's next from me

- I keep building Day 4-8 modules in parallel (meta.py, evolve.py, report.py)
- When batch 02 with relations lands, I re-run discover -- the structural_gap
  findings will mostly go away, and second-order findings (cluster gaps within
  the relation graph, transitive shortcut candidates, etc.) become visible
- When the 10 pre-registered queries land, I run the bench command and
  generate the comparative-vs-LLM report per Refinement 2's CLUTRR/SME/MIRB
  pre-registered harness

## Cross-references

- Batch 01 corpus: data/substrate_index/math_corpus_batch01.jsonl
- Discover engine: backend/substrate_index/discover.py (commit 37c7658e)
- First findings (semantic queries): notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Smoke runner: tools/substrate_index_discover_run.py
