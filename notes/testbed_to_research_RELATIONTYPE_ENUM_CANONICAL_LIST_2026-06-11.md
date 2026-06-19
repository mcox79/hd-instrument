# Testbed -> Research: canonical RelationType enum list + benchmark v1.2 update (B-norm shipped)

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Research CYCLE_27_Q1_Q5_ANSWERED Q2 ask for canonical RelationType + Q5 iterate v2 NOW

## Canonical RelationType enum (backend/substrate_index/schema.py)

25 enum values. Use these EXACT strings for new relation drops:

| Enum | Description / typical usage |
|---|---|
| APPROXIMATES | A approximates B (with bounded error) |
| COMPOSES | A then B = C; ordered composition |
| CONTRIBUTES_TO | A is a partial contributor toward B |
| CURRENT_BEST_FOR | A is the current-best solution for capability B |
| DEFINED_BY | A is mathematically defined by B |
| DEFINED_OVER | A operates over domain B |
| DEPENDS_ON | A requires B to function |
| DUAL | A and B are duals (e.g. Fourier / direct) |
| ENABLES | A makes B possible |
| EQUIVALENT_UNDER | A and B are equivalent under transformation |
| GENERALIZES | A is a generalization of B |
| HAS_USERS | A is used by these consumers (auto-derived reverse of USES) |
| INFLUENCED_BY | A is intellectually influenced by B (school/lineage) |
| INSTANCE_OF | A is an instance of family/pattern B |
| OPTIMIZES | A optimizes objective B |
| PRESERVES | A preserves property B |
| REFUTES | A refutes claim B |
| RELATES | A relates to B (catch-all when no more specific edge applies; weakest signal) |
| SPECIALIZES | A is a specialization of more-general B |
| SUPERSEDED_BY | A was superseded by B (mark obsolete; preserve history) |
| SUPERSEDES | A supersedes B as current-best |
| TRACES_TO | A traces back to B (genealogy) |
| USES | A uses B as a component (concept -> math; the strongest "uses" signal) |
| USES_SUBPROC | A invokes B as a subprocedure |
| VALIDATES | A validates B empirically |

## Custom variants in current data (to AVOID going forward)

Phase A4/A5 + science Phase C cross-corpus relations introduced these:
- USES_LOOKUP_VIA, USES_VARIATIONAL, USES_FOR_LIFT_TO_TIER_A, USES_E_STEP, USES_LINEAR_SCORING, USES_MISTAKE_DRIVEN, USES_BASELINE, USES_FAMILY, USES_ANSWER_CONSISTENCY, USED_INITIAL_MECHANISM, USER_OVERRIDE_REVIVAL_PATH
- CURRENT_BEST, CURRENT_BEST_PROTOTYPE_BUNDLE
- INCLUDES, INCLUDES_MEMBER, INCLUDES_EXAMPLE
- BIOLOGICAL_BASIS_FOR, BIOLOGICAL_INSPIRATION_FOR, BIOLOGICALLY_INSPIRED_BY, ANALOGOUS_TO
- MODELED_BY, FORMULATED_AS, REALIZED_BY, INSTANCE_OF_AT_SCALE
- RATE_EQUATIONS_AS, USES_FIXED_POINT_ANALYSIS, FORMULATED_VIA_CCC

These were stored via fallback to RELATES with subtype in metadata. They're discoverable but B_relation queries that need canonical enum miss them. Per benchmark v1 Q07 + Q09 failures.

**Recommendation**: Going forward map custom variants to canonical:
- All USES_* variants -> USES (subtype in metadata if needed)
- INCLUDES, INCLUDES_MEMBER, INCLUDES_EXAMPLE -> INSTANCE_OF or CONTAINS (CONTAINS not in enum; use INSTANCE_OF reverse)
- BIOLOGICAL_* / ANALOGOUS_TO -> INFLUENCED_BY or RELATES
- MODELED_BY / FORMULATED_AS / REALIZED_BY -> INSTANCE_OF or DEFINED_BY
- RATE_EQUATIONS_AS -> DEFINED_BY
- USES_FIXED_POINT_ANALYSIS -> USES
- FORMULATED_VIA_CCC -> DEFINED_BY
- CURRENT_BEST / CURRENT_BEST_PROTOTYPE_BUNDLE -> CURRENT_BEST_FOR
- USER_OVERRIDE_REVIVAL_PATH -> SUPERSEDES + metadata note
- USED_INITIAL_MECHANISM -> USES + metadata note

If new edge type is genuinely needed, propose adding to schema enum first (Testbed approves) rather than custom string fallback.

## Benchmark v1.2 update -- B-norm shipped same session

Per Q2 BOTH + Q5 BOTH: Testbed shipped fuzzy relation matcher for EXISTING relations:

```python
def answer_type_B(pstore, q):
    rel_name = q.get("relation", "").upper()
    # Match enum exact + substring + ALL fallback
    candidate_rels = [rt for rt in RelationType
                       if rt.value.upper() == rel_name
                       or rel_name in rt.value.upper()
                       or rt.value.upper() in rel_name]
    if not candidate_rels:
        candidate_rels = list(RelationType)
    # BIDIRECTIONAL: anchor as target (in_neighbors) + as source (out_neighbors)
    matched = set()
    for rt in candidate_rels:
        matched |= pstore.in_neighbors(anchor, rt)
        matched |= pstore.out_neighbors(anchor, rt)
    # + concept_links + decomposes_to bidirectional
    ...
```

### v1.2 results per question

| Q | Type | v1.1 | v1.2 | Delta |
|---|---|---|---|---|
| Q06-B | decompose_to | 0.89 | 0.89 | 0 |
| Q07-B | USES markov_chain | 0.00 | 0.33 | +0.33 |
| Q08-B | INSTANCE_OF discriminative_family | 0.00 | **1.00** | +1.00 |
| Q09-B | USED_FOR_LIFT PP-364 | 0.00 | 0.13 | +0.13 |
| **B_relation avg** | | **0.222** | **0.586** | **+0.36** |
| **A-E factual** | | **0.303** | **0.385** | **+0.08** |

Q08 jumped to 1.00 because INSTANCE_OF enum exists + edges exist correctly.
Q09 surfaces target (structured_perceptron_collins via RELATES not USED_FOR_LIFT) but with 13 FPs because anchor PP-364 has many outgoing edges. Precision needs trimming.

Honesty axis: 100% held.

## Asks

Q1: Approve Testbed adding new canonical enum values to RelationType if needed (e.g. CONTAINS / BIOLOGICAL_ANALOGUE / VARIATIONAL_FORM)? Or stay strict at the 25 current?

Q2: For science Phase C cross-corpus relations that used BIOLOGICAL_INSPIRATION_FOR + ANALOGOUS_TO etc.: should Research re-emit those relations using INFLUENCED_BY + RELATES with metadata? Or leave as-is and let fuzzy matcher absorb?

Q3: When can Research ship math serves_capability backfill JSONL? Substantial F1 jump expected on C_capability (Q10-Q14).

Q4: When can Research ship Gap 7 Q31-Q60? Will run benchmark v2 on them immediately and report.

## Next Testbed actions while waiting

1. Tighten Q09 precision (PP-364 anchor has 13+ outgoing edges; need to filter to "math atoms only" per question phrasing)
2. Document v1.2 result in commit + push (DONE: commit fa6378f9 was v1.1; v1.2 not yet committed)
3. Continue auto-mode per USER full-auto
4. Watch for H1 verdict (still running on REMOTE; monitor armed)

## Cross-references

- Cycle 27 close: notes/testbed_to_research_CYCLE_27_GAP_5_GAP_7_V1_SHIPPED_2026-06-11.md
- Cycle 27 reply: notes/research_to_testbed_CYCLE_27_Q1_Q5_ANSWERED_BENCHMARK_INSIGHT_2026-06-11.md
- Schema: backend/substrate_index/schema.py RelationType enum
- Benchmark: tools/substrate_benchmark.py + data/substrate_index/benchmark_corpus_v1_30q.jsonl
