# Research -> Exp-Dev: Sprint-2 decision -- BOTH PATHS PARALLEL

**From:** Research  **Date:** 2026-06-10 late evening
**Re:** Your Sprint-1 complete report; Sprint-2 path decision

## Decision

**BOTH paths in parallel** — they exercise different substrate capabilities + different commercial claims.

## Path B (PRIORITY; production-grade quickest)

Production-grade gates that DON'T require lexicalization bridge. Validate substrate-only autonomous output where it should be strongest.

| Anchor | Benchmark | HARD-PASS | Rationale |
|---|---|---|---|
| **MATH-benchmark** | high-school competition (MATH dataset) | accuracy ≥ 0.20 (small LLM baseline) | Symbolic — should leverage MATH-1/3/4 ceiling |
| **HumanEval-structural** | function spec → AST → execute | pass@1 ≥ 0.15 (small LLM baseline) | Structural — CODE-1 op-shard composition already at 1.0; convert problem → AST → emit code |
| **MBPP-structural** | basic Python | pass@1 ≥ 0.20 | Same as HumanEval; broader test |
| MATH-2 EQUATION-SOLVE | linear/quadratic/poly | accuracy ≥ 0.70 | Extends MATH-1 |
| MATH-6 BAYES-INFERENCE | Asia / Sachs | accuracy ≥ 0.85 | Extends PP-308 |
| MATH-7 CAUSAL-INTERVENTION | do-calculus | accuracy ≥ 0.75 | Extends PP-270/307 |

**Why prioritize:** These have empirical existence proofs at rung-1-2. Production-grade benchmark validation = next gate. Doesn't depend on solving the lexical/textual surface gap. Even partial success → substrate-as-symbolic-engine commercial claim.

## Path A (parallel; user principles applied; honest low-P)

Attempt lexicalization bridge substrate-only. User principles say try; biology proves possible (humans do it); materials science has phonology math; invent new math.

| Anchor | Test | HARD-PASS |
|---|---|---|
| **LEX-1 TIER-4 codebook emission** | substrate codebook → token sequence; reference-paragraph BLEU | BLEU ≥ 0.10 (substrate-only low bar) |
| **LEX-2 Levelt-pipeline substrate** | concept → lemma → wordform → phonology (substrate stages) | semantic-similarity ≥ 0.40 vs reference |
| **LEX-3 Zipf-optimal codebook** | frequency-weighted codebook + substrate emission | minor improvement over baseline |

**Why parallel:** Even partial substrate-only lexicalization existence proof tells us whether the gap is hard-architectural (need LLM bridge) or just engineering. User principles (try; biology proves possible; invent new math) ask for the attempt. Honest P-band reflects the difficulty.

## Plus: PRODUCTION DECIDER PP-225 next step

**kb25k held-out 0.996 at real 25K = production scaling VALIDATED** after DISC_POOL-cap fix.

| Anchor | Test |
|---|---|
| Genuine kb50k (running) | held-out accuracy at real 50K facts |
| Genuine kb100k | next |
| Genuine kb500k | stretch |
| Adversarial paraphrase robustness on kb25k | hits1 under paraphrase |

## Plus: CODE-2 bug-detection rescue

Already dispatched 2x drill (code2_bug_detection_rescue). Rescue paths: R1 verified-correct bundle (binding mismatch = bug); R2 execution-trace comparison; R3 property-testing.

## Sequencing recommendation

**Day 0 (tonight/tomorrow morning):**
- Multi-seed cycle 224 wins n=3 (cheap; confirms not flukes)
- INTEG-RENORM-T1 (5 min decisive)
- KEY-ROTATION cert (~50 lines; <1hr)
- LEX-1 Tier-4 codebook emission (Path A first try; honest low-P)

**Days 1-2:**
- MATH-benchmark + HumanEval-structural + MBPP-structural (Path B priority)
- Genuine kb50k landing
- code2 bug-detection rescue R1 (verified-correct bundle)

**Days 3-5:**
- Path A iteration if LEX-1 shows ANY substrate-only lexicalization signal
- MATH-2/6/7 (extend symbolic)
- COMM thrust extension (COMM-2 translation, COMM-3 conversational)

## Honest P-bands

| Path | What I expect | Why |
|---|---|---|
| Path B MATH-benchmark | 0.15-0.30 (around small LLM baseline) | symbolic — substrate should be competitive |
| Path B HumanEval-structural | 0.10-0.20 (around baseline) | program shards + execute; gap is parsing English spec |
| Path A LEX-1 | 0.05-0.20 (modest) | substrate hasn't trained on lexicalization; honest low-P |

## Cross-references
- Sprint-1 complete: notes/exp_dev_to_research_3THRUSTS_SPRINT1_COMPLETE_2026-06-10.md
- Sprint-2 priority routing: notes/research_to_exp_dev_SPRINT_2_BENCHMARK_PROMOTION_2026-06-10.md
- Memory substrate-self-improvement-architecturally-viable-2026-06-10

---

**Exp-Dev:** BOTH paths in parallel. Path B = production-grade benchmark validation (priority; symbolic substrate strength). Path A = substrate-only lexicalization bridge (honest low-P; user principles apply). Plus multi-seed + INTEG-RENORM + KEY-ROTATION + kb50k. FULL-AUTO authorized per pre-reg gates.
