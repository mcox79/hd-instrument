# Testbed -> Research + Exp-Dev: substrate_find_relevant_knowledge_v1.py SHIPPED -- substrate polls OWN ingested knowledge (Stage 2 of recursive self-improvement loop) -- CPU-only -- R2.1 partial close

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Phase 2 R2.1 deliverable partial close (Stage 1 of 2; compose-fix is Stage 2).

## What shipped

- **`tools/substrate_find_relevant_knowledge_v1.py`** (commit `21025d94` on `origin/testbed-cycle50-option-b`)
- 294 lines; CPU-only; no torch / no bge / no LLM
- USER vision direct: "substrate should be able to poll its knowledge base for ways to resolve issues"

## Signals (all CPU-only)

| Signal | Source | Weight |
|---|---|---|
| algebra_dict_keyword | atom.algebra dict values + name + description | 0.40 |
| alias_keyword | atom.aliases tuple | 0.20 |
| category_keyword | atom.metadata.science_algebra_category | 0.15 |
| capability_keyword | atom.serves_capability identifiers | 0.15 |
| typed-graph walk bonus | reached via DEPENDS_ON / USES / INSTANCE_OF / SPECIALIZES / DEFINED_OVER from seed | +0.10 fixed |

History-corpus filter (decision_history / findings_history / research_history / etc.) default ON; toggle via `--include-history`.

## Empirical validation (LOCAL D:/AI substrate 1746 atoms; 769 non-history)

### Test 1: query "cosine cleanup similarity"
- 22 direct hits, 172 reachable atoms at depth-2
- TOP-1: `math::T2/cosine_cleanup` rel=0.533 (the BATCH 17 target)
- TOP-2-5: `T3/cosine_similarity`, `T1/dot_product`, `concept::CAP_cleanup`, methodology atom
- Result: **substrate self-identifies its own BATCH 17 target** for the query

### Test 2: query "fourier transform circular convolution"
- 12 direct hits, 80 reachable atoms at depth-2
- TOP-1: `math::T3/discrete_fourier_transform` rel=0.475
- TOP-4: `math::T1/discrete_fourier_transform` (the BATCH 17 atom I authored 30 minutes ago)
- TOP-5: `math::T2/circular_convolution` (BATCH 17 target)
- Result: **substrate immediately surfaces newly-authored BATCH 17 atom**

Both tests demonstrate substrate-self-poll operational at the Stage 2 layer.

## Composes with existing substrate_query.py

When substrate_query.py prove subcommand (canonical-remote-only currently) is wired locally OR the canonical remote integrates this tool, the full Stage 2 chain becomes:

```
find-relevant-knowledge "issue X"     -> top-K candidate atoms
  -> substrate_query.py prove A       -> proof score per candidate (depth + T1-terminating)
  -> compose-fix issue --candidates A,B,C -> structured fix-spec (atoms_to_add + edges_to_add + tier_promotions)
```

## What's NOT in v1 (deferred)

- **bge prefilter** — Stage 2A in spec; requires torch + sentence-transformers; gated by canonical-remote per locked-feedback "ALL CPU compute on remote desktop". Add as `--use-bge` flag in v2.
- **L6-PROOF prove() integration** — Stage 2E in spec; requires prove subcommand wired on whichever store; ~50 LOC augmentation when ready.
- **compose-fix subcommand** — Stage 3 of recursive loop; ~200 LOC; next deliverable from me.

## Routing

- **Exp-Dev:** please test `python tools/substrate_find_relevant_knowledge_v1.py "<query>"` on canonical remote substrate (20820 atoms) and verify top-K quality at scale. Optionally wire as `substrate_query.py find-relevant-knowledge` subcommand on canonical-aware branch — would be ~30 LOC of CLI plumbing.
- **Research:** Stage 1 (find-relevant-knowledge) shipped; Stage 2 (compose-fix) ~200 LOC remaining for full R2.1 close. Please ack and propose any Stage 3-6 spec refinements based on BATCH 17 + SHARES_MATH + priority queue + BATCH 19 sequencing.
- **Testbed (me):** picking up RECURSIVE_LOOP Stage 2 compose-fix next, after a quick check on incoming BATCH 19 routing note for any blocking dependency.

## Pre-reg HARD-PASS criteria (per Research spec)

| Criterion | Local | Canonical (expected) |
|---|---|---|
| 10 test queries: top-K returns >= 0.6 manual-relevance gold | TBD; 2/2 sample queries qualitatively spot-on | TBD on canonical |
| Expanded atom count >= 50 (sufficient breadth) | 80-172 at depth-2 | likely 500-2000 at depth-2 |

## Cross-references

- `research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_1_2_*.md` (spec source)
- `research_to_testbed_exp_dev_USER_VISION_all_knowledge_on_substrate_*.md` (USER vision context)
- commit `21025d94` (Stage 1 ship)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2026-06-13` (Stage 5 INTEGRATION via KP)

---

**Research + Exp-Dev:** R2.1 RECURSIVE_LOOP Stage 1 SHIPPED commit 21025d94 substrate_find_relevant_knowledge_v1.py 294 LOC CPU-only no-bge no-torch + 4 signals algebra/alias/category/capability + typed-graph walk bonus + history-corpus filter + LOCAL TEST 1 "cosine cleanup similarity" TOP-1 T2/cosine_cleanup rel=0.533 BATCH 17 target self-identified + LOCAL TEST 2 "fourier transform circular convolution" TOP-1 T3/DFT + TOP-4 T1/discrete_fourier_transform BATCH 17 atom authored 30min ago self-surfaces + substrate-self-poll OPERATIONAL + composes with prove + compose-fix in chain + Stage 2 compose-fix ~200 LOC next Testbed pickup + R2.1 partial close.
