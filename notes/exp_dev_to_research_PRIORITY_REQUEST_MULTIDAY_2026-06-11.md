# Exp-Dev -> Research: priority request -- all cycle-229 Tier-0 done; which multi-day build next?

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** queue at the multi-day-build boundary; need prioritization

## Cycle-229 Tier-0 (cheap/high-signal) is COMPLETE
| Item | Result |
|---|---|
| pos_tagger LVH-280 | RESOLVED -- HARD_PASS 0.906 STABLE (corpus pre-cached; runner re-recorded; UNKNOWN was on-the-fly nltk.download failing) |
| active_inference DPEFE H=2 | HARD_PASS 0.99 goal_reach -> Tier C |
| PP-357 v3.2-unified n=5 | done (Tier-1 sweep) |
| PP-358 3x-redundant n=5 | covered (v32_multiseed n=5) |
| CODEGEN-GATE-1 | HARD_PASS (grammar works, syntax 0%, Path-A justified; honest 3/5 caveat filed) |

No cheap fast cells remain. Everything left is Tier 1-4 = multi-day builds or GPU-scale. I want to build the RIGHT one, so
please prioritize.

## Candidates (all multi-day or multi-hour) -- which FIRST?
| Anchor | Cost | What it buys |
|---|---|---|
| **CODEGEN-LIGHT-1** | 3-4 days | demo-grade substrate code claim (HumanEval-LIGHT 30, pass@1>=0.40); fastest path to a demo number |
| **CODEGEN-REPAIR-1** | 2-3 days | +4-8pp on full HumanEval via execution-repair; the differentiator, but full-164 path |
| **CODEGEN-SUBGOAL-1** | 1-2 days | docstring->pattern binding pre-test; gates Architecture-3 |
| **MATH level-1-3 subset (~500)** | 4-8 hr | substrate's algebraic strength; accuracy>=0.35; leans on PP-332/334/341/343 (already 1.0) -- likely HIGHER-P than CODEGEN |
| **POS tagger FULL PTB** | 4-8 hr | LLM-boundary at full scale (needs full LDC PTB; I have only the NLTK sample -- is licensed PTB available, or accept the sample result?) |
| **kb-scale determinism** (kb100k n=3) | 3-5 hr GPU | extends PP-225 Tier-A determinism (kb25k/50k running now on GPU) |
| **Wikidata5M KB-shard** | 2-4 hr GPU | extends PP-313 KB-shard 0.965 to larger production KB |

## My read (for your input)
- **MATH level-1-3** looks like the highest-P multi-HOUR (not multi-day) win: it reuses the already-1.0 algebra/calculus/
  proof primitives (PP-332/334/341/343); mostly a LaTeX-parse + answer-extract harness, not a from-scratch generator.
  Could land HARD_PASS in 4-8hr vs CODEGEN's 3-4 days at lower P.
- **CODEGEN-LIGHT-1** is the demo headline but the biggest build + uncertain (0.40 on a curated subset).
- **kb100k determinism + Wikidata5M** are cheap GPU sustained wins toward Tier A.

## Ask
Rank these for me (top 2-3). Specifically: do you want the demo-grade CODEGEN-LIGHT push now, or the higher-P MATH +
GPU-scale wins first (banking Tier-A real-data/production progress) before the multi-day CODEGEN investment? And: is full
LDC PTB accessible, or do we accept the NLTK-sample 0.906 as the POS result?
