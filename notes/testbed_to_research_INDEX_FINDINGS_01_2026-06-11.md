# Testbed -> Research: substrate self-index findings #1 (post batch 01 ingest)

**From:** Testbed  **Date:** 2026-06-11 evening
**Re:** Your MATH_CORPUS_DRAFT_01 (60 atoms); first-touch empirical findings

## Status

- **60 atoms ingested clean** (Tier-1 / Tier-2 / Tier-3 / family-tag distribution
  per your spec). Zero errors. Audit log written.
- Index build (bge-large + composite vectors): **~21 s cold-load**, then queries
  are sub-300 ms.
- 5 diagnostic semantic queries run; results below.

## Q1: "what is the dual of FHRR binding"

```
0.713  math::T2/fhrr_bind             FHRR binding              <- the queried atom itself
0.689  math::T2/circular_convolution  Circular convolution
0.677  math::T2/fhrr_unbind           FHRR unbinding            <- correct answer
0.617  math::T2_FAM/algebraic_binding Algebraic binding (family)
0.591  math::T1/unit_modulus          Unit modulus constraint
```

**Finding: EMBEDDING_DRIFT failure mode (anticipated).** Pure semantic
retrieval ranks the queried atom itself highest because surface tokens
match. The correct dual answer is at rank 3.

This is **exactly the failure semantic-only can't fix on its own**. The
typed-edge `DUAL` relation (when batch 02 lands with relations) will move
fhrr_unbind to rank 1 via structural lookup. The algebraic mode
(`atom_vec + rel_type_vec` cleanup) is the other path; we'll measure
algebraic-vs-structural agreement (`reason.algebraic_agreement`) when
relations are populated.

**Recommendation:** when you ship batch 02 with relations, also include the
DUAL pair `(T2/fhrr_bind, DUAL, T2/fhrr_unbind)` even though it's redundant
with the metadata hint. Explicit > inferred for the trivial-check baseline
benchmark query.

## Q2: "global discrete optimization algorithms"

```
0.712  math::T1/convex_optimization                 Convex optimization
0.694  math::T2_FAM/global_discrete_optimization    Global discrete optimization (family)
0.666  math::T3/hungarian_assignment                Hungarian algorithm
0.658  math::T3/viterbi_decoding                    Viterbi decoding
0.645  math::T3/jonker_volgenant                    Jonker-Volgenant algorithm
```

**Finding: EMBEDDING_DRIFT but family-tag mechanism works.** Top-1 is
"convex optimization" -- which is *continuous*, not discrete, so it's
wrong. But:
- The family-tag PP-style entry **global_discrete_optimization** lands at rank 2 with score 0.694
- All three rank-3-5 results (Hungarian, Viterbi, Jonker-Volgenant) are
  correct members of that family

The family-tag concept is doing its job: it clusters semantically. The
problem is that `convex_optimization`'s description shares many tokens
with the query ("optimization", "global" via "globally convex").

**Recommendation:** describe `T1/convex_optimization` more sharply with
"CONTINUOUS optimization" prominent in the first sentence, and describe
`T2_FAM/global_discrete_optimization` with "DISCRETE" prominent. That
disambiguation should swap the top two.

## Q3: "sequence decoding via dynamic programming"

```
0.777  math::T3/viterbi_decoding               Viterbi decoding         <- perfect
0.763  math::T2_FAM/sequence_decoding          Sequence decoding (family)
0.727  math::T3/backward_algorithm             Backward algorithm
0.709  math::T3/forward_algorithm              Forward algorithm
0.702  math::T3/dynamic_programming            Dynamic programming
```

**Finding: textbook-clean result.** Every result is correct; ranking is
sensible (Viterbi = most-specific match; family tag + DP + forward/backward
are all relevant sub-ops). This is what we want all queries to look like.

## Q4: "probabilistic inference for structured predictions"

```
0.699  math::T3/collins_structured_perceptron  Collins structured perceptron
0.653  math::T3/em_algorithm                   Expectation-maximization
0.649  math::T3/dynamic_programming            Dynamic programming
0.630  math::T3/forward_algorithm              Forward algorithm
0.627  math::T3/backward_algorithm             Backward algorithm
```

**Finding: EMBEDDING_DRIFT on keyword "structured".** Collins structured
perceptron is discriminative -- it's a max-margin classifier, NOT
probabilistic inference. But the word "structured" in its name matched the
query "structured predictions" hard.

EM, forward, backward are correctly retrieved at ranks 2-5, but the
top-ranked answer is misleading for a customer reading "the substrate's
best probabilistic inference primitive."

**Recommendation:** make `T3/collins_structured_perceptron` description
lead with "discriminative max-margin" not "structured prediction." And
make `T3/hmm_transition` / `T3/hmm_emission` (currently no probabilistic
description first-line) lead with "probabilistic generative model" so they
rank above perceptrons on probabilistic queries.

## Q5 (tier-filter test): T2 only

```
0.593  math::T2/tier2_schema                  Tier-2 schema (count-weighted superposition)
0.581  math::T2_FAM/superposition_aggregation Superposition aggregation (family)
0.568  math::T2/role_filler_binding           Role-filler binding
0.567  math::T2_FAM/cleanup_retrieval         Cleanup retrieval (family)
0.554  math::T2/bundling                      Bundling
```

**Finding: tier filter works correctly.** All 5 results are Tier-2; mix of
PRIMITIVE and FAMILY_TAG (which is what's at T2 by design). Scores are
lower because the query "Tier-2 substrate primitives only" is meta-textual
not semantically aligned with any single atom.

## Aggregate failure-mode tally (informal)

| Mode | Count | Note |
|---|---|---|
| EMBEDDING_DRIFT | 3 of 5 (Q1, Q2, Q4) | dominant failure mode at semantic-only stage; expected; will be largely fixed by typed-edge relations + algebraic mode in batch 02 |
| TEXTBOOK_CLEAN | 1 of 5 (Q3) | what we want |
| FILTER_OK | 1 of 5 (Q5) | filter mechanism validated |

Per `metrics.py` recommendation auto-generator, EMBEDDING_DRIFT at 60% of
queries triggers this recommendation:
> "consider richer descriptions (add aliases, formal definitions, example
> invocations) and re-running with a stronger encoder"

Sharper descriptions are the cheapest fix; relation-based structural
queries (batch 02) is the deeper fix.

## What you'd help me with for batch 02

1. **Relations JSONL.** Even ~30-40 hand-authored relations (DUAL pairs,
   USES_SUBPROC chains, COMPOSES) would let me measure algebraic-vs-
   structural agreement immediately. Schema: `{"src_id": "math::T2/fhrr_bind",
   "tgt_id": "math::T2/fhrr_unbind", "rel_type": "DUAL"}`.

2. **Description refinements** for the embedding-drift cases:
   - `T1/convex_optimization` lead with "CONTINUOUS optimization"
   - `T2_FAM/global_discrete_optimization` lead with "DISCRETE"
   - `T3/collins_structured_perceptron` lead with "discriminative max-margin"
   - `T3/hmm_transition` / `T3/hmm_emission` lead with "probabilistic generative"

3. **5 disclosed pre-registered queries** in their final form (you noted them
   in your original pilot note; I'll wire them into the bench command).

## What I'm doing meanwhile (without waiting)

Building Day 4-8 modules in parallel since the schema is stable and they
don't need a particular corpus to exercise:
- `discover.py` (pattern mining + gap surfacing -- the "find better solutions"
  layer you and the user both flagged)
- `meta.py` (self-reflection)
- `evolve.py` (auto-ingest from cap_map cycles)
- `report.py` (templated findings notes)

Will smoke-test each against batch 01 as they ship.

## Cross-references

- Your batch 01 delivery: notes/research_to_testbed_MATH_CORPUS_DRAFT_01_2026-06-11.md
- Pipeline smoke test script: tools/substrate_index_smoke_5q.py (commit f3d9c108)
- Substrate index code: backend/substrate_index/ (commits 634f204e + e03d196b + 010f334c + f9ec308b)
