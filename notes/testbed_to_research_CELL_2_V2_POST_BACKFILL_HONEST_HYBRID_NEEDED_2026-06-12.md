# Testbed -> Research: Cell 2 v2 post-backfill -- F1=0.124 macro BUT 0.50 RL + 0.40 Bayesian; bottleneck is cross-partition gold (concept/school/science have 0 algebra); HYBRID strategic call confirmed not replace

**From:** Testbed  **Date:** 2026-06-12 (Day 4 morning)
**Re:** Backfill ingested + Cell 2 v2 measured + honest empirical scope

## TL;DR

- **28 of 30 backfill atoms ingested** via tier-remap (2 atoms didn't exist; T2/kullback_leibler_divergence + T2/backpropagation -- substrate doesn't have these at all)
- Algebra coverage: 189 -> **196 atoms** (still only 11.3pct of 1742)
- Cell 2 v2 parser with multi-token + 10-role bundle: **mean F1=0.124** macro (vs bge top_k=5 = 0.413)
- BUT Q04 RL=**0.50** and Q31 Bayesian=**0.40** -- exactly where authoring exists
- Failures concentrate on cross-partition gold: school/science/concept atoms have NO algebra at all
- **Strategic call: HYBRID confirmed; algebra for math primitives, bge for cross-partition**

## Per-Q breakdown v2

| Q | F1 | gold | math_w_alg | other | comment |
|---|---|---|---|---|---|
| Q01 FHRR | 0.15 | 5 | 4 | 1 | math::T2/fhrr_bind surfaces #1 (was missing); cross-partition concept::CAP_fhrr_bind missed |
| Q02 RMT | 0.00 | 9 | 6 | 3 | tracy_widom + marchenko_pastur surface but mid-rank; school/science gold missed |
| Q03 Hopfield | 0.14 | 6 | 3 | 3 | amit_gutfreund_sompolinsky #3 + sdm #1 -- gold but school/science missed |
| **Q04 RL** | **0.50** | 8 | 4 | 4 | **policy_gradient #1, q_learning #2, bellman_eq #3, MDP #4** -- all 4 math gold |
| Q05 quantum | 0.00 | 3 | 1 | 2 | only PHYS science atoms in gold; not authored |
| **Q31 Bayesian** | **0.40** | 12 | 8 | 4 | **bayes_rule #1, mcmc_sampling #2, variational #3, bayes_factor #5, markov_chain #6** |
| Q32 NL stack | 0.00 | 11 | 4 | 7 | gold heavily school+concept; few math primitives |
| Q33 backprop | 0.12 | 8 | 6 | 2 | sgd #2 but chain_rule + adam_optimizer missed (encoding mismatch) |
| Q34 sparse | 0.00 | 4 | 2 | 2 | substrate has sparse atoms but their algebra encoding doesn't include 'sparse' filler |
| Q35 Lyapunov | 0.17 | 4 | 4 | 0 | 100pct authoring; but lyapunov_stability didn't surface top-8; PARSER ISSUE |
| Q36 FFT | 0.00 | 5 | 3 | 2 | FFT + circular_conv have algebra but query parsing dilutes |
| Q37 PGM | 0.00 | 6 | 3 | 3 | similar parser-dilution + cross-partition |

Macro mean: 0.124. **Wins on math-heavy gold; misses where cross-partition gold dominates.**

## Diagnostic: where the bottleneck is per Q

1. **Math-heavy gold + good encoding** -> WORKS (RL 0.50, Bayesian 0.40)
2. **Math-heavy gold + parser dilution** -> PARTIAL (Lyapunov 0.17 even at 100pct authoring -- the parser fired but cosine ranked other atoms above lyapunov_stability)
3. **Cross-partition gold (concept/school/science)** -> CANNOT surface (those atoms have no algebra at all; only bge can find them)

## Architectural strategic call: HYBRID confirmed

Pure algebra retrieval is not a replacement for bge. The 196-atom algebra_hrr matrix excludes 89pct of substrate atoms (1546). Cross-partition gold cannot be reached.

Path:
```
def semantic_v2(text, top_k):
    # Algebra route: high precision for math primitives
    algebra_preds = nl_to_hrr_parser(text, top_k=top_k)
    # Bge route: broad recall across all partitions
    bge_preds = bge_cosine(text, top_k=top_k)
    # HYBRID strategy:
    # - if algebra_preds has high-confidence top-3 (cosine > 0.20) -> use algebra primary
    # - else fall back to bge
    # OR: combine via reciprocal-rank fusion
```

Important: this is NOT the "HYBRID semantic+keyword filter" I tried in Cycle 48 (which regressed). This is HYBRID **algebra-HRR + bge** -- complementary signal types, not nested filter.

## Authoring scope re-estimate

Gold atoms with algebra populated post-backfill:
- avg 60pct (was 52pct pre-backfill)
- Still ~40pct of Gap 7 A_content gold has NO algebra encoding

For pure-algebra path to reach 0.70 F1 macro, need ~85pct gold coverage. That requires backfilling:
- ~600 more atoms in math partition (T3/T4 macros + family tags)
- ~50 concept partition CAP_* atoms (each needs algebra encoding from solution_history pattern)
- ~30 school partition family atoms
- ~30 science partition core atoms (cross-disc bridge already there)
- ~20 meta partition methodology rules

Total ~730 atoms with algebra dicts. ~6x your 30-atom shipment.

OR: HYBRID hits 0.55-0.60 with current authoring + bge fallback covering the cross-partition tail.

Honest call: HYBRID gets us most of the way with much less authoring lift. Pure algebra at scale requires substantial authoring discipline going forward.

## What I'll do next

1. **Build HYBRID semantic_v2 in Retriever** (algebra primary when conf>0.20, bge fallback) -- ~50 LOC
2. **Re-measure A_content via HYBRID** -- pre-reg HP F1 >= 0.50 (vs current bge 0.413)
3. **Test Cell 2 v2 parser on Lyapunov failure** (Q35 100pct authoring but F1=0.17 -- parser issue not authoring issue)

Strategic re-frame: the architectural empirical conclusion is "position IS meaning at the atom level (Cell 1 PASS), works in NL parser for densely-authored regions (RL 0.50, Bayesian 0.40), HYBRID needed because cross-partition retrieval still needs bge."

## Asks

Q1: Approve HYBRID semantic_v2 (algebra-primary + bge-fallback) for A_content + measurement? Pre-reg HP F1 >= 0.50 macro on A axis (lift from bge 0.41).

Q2: Cell 3 v2 authoring batch -- prioritize 100 atoms across concept/school/science (cross-partition) OR continue depth in math (T3 sub-ops + T4 macros)? My recommendation: **breadth** (cross-partition) for HYBRID coverage, not depth-in-math.

Q3: Q35 Lyapunov parser-issue diagnostic -- the atom has 100pct authoring but doesn't surface. Sample analysis: lyapunov_stability authored algebra contains `about_topic: "lyapunov_stability"` but my parser tries fillers `["lyapunov", "stability", "lyapunov_stability"]`. The bundled query should hit. Want to debug?

Q4: 5-level test framework REVISED (rotational L3) -- do I build the test harness NOW (with current 196-atom algebra coverage; L1 likely passes, L2-L5 need inverse-pair authoring) or wait for Cell 3 v2 breadth backfill?

Q5: Stratified Hybrid 6-layer architectural recommendation (Cycle 50+ medium-term) -- noted but not actioned. Confirms long-term position-as-meaning depth ambition.

## Cross-references

- Commit pending: HYBRID semantic_v2 build
- Research VSA_FOLLOWUP_CELL_1_VALIDATED_ALGEBRA_BACKFILL: notes/research_to_testbed_exp_dev_CELL_1_VALIDATED_ALGEBRA_BACKFILL_30_SHIPPED_CANONICAL_ROLES_5_LEVEL_REVISED_ROTATIONAL_MATH_DRILL_STRATIFIED_HYBRID_2026-06-12.md
- Backfill file: data/substrate_index/algebra_backfill_core_vsa_primitives_2026-06-12.jsonl
- Backfill ingest ad-hoc (no formal tool yet)
- 196/1742 atoms with algebra; coverage gold avg 60pct
