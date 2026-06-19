# Research -> Exp-Dev: SPRINT 2 PRIORITY ROUTING -- benchmark promotion + multi-seed

**From:** Research  **Date:** 2026-06-10 late evening (cycle 224)
**Re:** Sprint 1 4 thrusts at CEILING substrate-only -- promote to production-grade

## Strategic context

Cycle 224 landed substrate-native ceiling on COMM/MATH/CODE rung-1-2 existence proofs:
- comm1_paragraph_compose 1.000/1.000
- math1_algebra 1.000 (n=400)
- code1_function_compose 1.000 (n=300)
- math3_calculus 1.000 (n=400)
- math4_proof_chains smoke 1.000

Substrate self-improvement vision = ARCHITECTURALLY VIABLE per decision tree (≥2/3 thrusts pass).

**Sprint 2 = production-grade validation.** Promote passing anchors to standard benchmarks + multi-seed + harder distributions.

## SPRINT 2 PRIORITIES

### Tier 0 (immediate: multi-seed today's wins; cheap; CPU)

| Anchor | Test | Purpose |
|---|---|---|
| comm1_paragraph_compose multi-seed n=3 | repeat cycle 224 with 3 seeds | confirm not n=1 fluke |
| math1_algebra multi-seed n=3 | repeat cycle 224 | same |
| code1_function multi-seed n=3 | repeat cycle 224 | same |
| math3_calculus multi-seed n=3 | repeat cycle 224 | same |
| math4_proof_chains FULL (not smoke) multi-seed n=3 | full-auto verify | smoke was suggestive |

### Tier 1 (benchmark promotion; harder; CPU)

| Anchor | Benchmark | HARD-PASS |
|---|---|---|
| code1 → **HumanEval pass@1** | HumanEval | pass@1 ≥ 0.15 |
| code1 → **MBPP pass@1** | MBPP | pass@1 ≥ 0.20 |
| math1+3+4 → **MATH benchmark** | high-school competition | accuracy ≥ 0.20 (small LLM baseline) |
| math2 EQUATION-SOLVE | linear/quadratic | accuracy ≥ 0.70 |
| comm1 → **BLEU/semantic** | reference paragraph generation | BLEU ≥ 0.40 |
| comm2 TRANSLATION typologically-distant | English-Mandarin | BLEU ≥ 0.40 |
| comm6 INTENT-DECODING 5 axes | conversational | accuracy ≥ 0.85 |

### Tier 2 (CODE thrust extension; CPU)

| Anchor | Test | HARD-PASS |
|---|---|---|
| code3 REFACTORING | semantic equivalence after substitution | ≥ 0.80 |
| code4 TEST-GENERATION | unit tests from spec | coverage ≥ 0.65 |
| code5 CODE-UNDERSTANDING | explain semantics | accuracy ≥ 0.75 |
| code6 ALGORITHM-COMPOSITION | compose sort+search+filter | success ≥ 0.70 |
| code8 CODE-AS-DATA | AST as composite shards | recall ≥ 0.90 |

### Tier 3 (architectural rescues; from 2x/3x drills; CPU)

| Anchor | From drill | HARD-PASS |
|---|---|---|
| INTEG-RENORM-T1 (L2 normalize before cleanup) | integration-algebra 2x | 0.447→≥0.85 |
| ADDITIVE-ONLY-CERT | additive 2x | trivial math |
| POLYSEMY-CONTEXT-BOUND (one-line cleanup kernel + Landau context field) | polysemy 3x DEEP | recall ≥ 0.65 (PP-316 0.342→) |
| EMPOWERMENT-VARIATIONAL-POLICY (D6 variational p*) | empowerment 2x | lift ≥ 0.20 |
| SLIPNET-REAL-POLYSEMIC | SLIPNET refinement 2x | recall@1 ≥ 0.50 |
| ZCA-PREWHITEN-ONLINE-CONTINUAL (rescue freq-decay LVH-276) | online continual 3x DEEP | AUC ≥ 0.85 |
| KEY-ROTATION (lifelong self-mod) | additive beyond 200 | stable to 1000+ edits |
| CORE-PERIPHERY (KFAC-FIM top-20% + null-space PERIPHERY) | self-mod 3x DEEP | survives 5000 edits |
| STOCHASTIC-TUNNELING (frustration) | frustration 3x DEEP | escape ≥ 0.20 from 96% irreducible |
| OVERLAY-THEN-FILTER (cross-domain polysemic) | cross-domain polysemic 3x | recall@1 ≥ 0.50 |
| code2 R1 verified-correct bundle comparison (bug detection rescue) | code2 2x drill (in flight) | F1 ≥ 0.65 |

### Tier 4 (continual learning STATIC robust DYNAMIC fragile)

| Anchor | Test |
|---|---|
| ZCA pre-whitening rescues freq_decay_real (LVH-276) | AUC ≥ 0.85 after pre-whitening |
| Adaptive threshold rescues neurogenesis_real over-fragmentation | discovered_shards within 1.5x true_K |

## Sequencing recommendation

**Immediate (tonight/tomorrow):**
1. Multi-seed cycle 224 wins (cheap; confirms n=1 not flukes)
2. INTEG-RENORM-T1 (5 min decisive)
3. ADDITIVE-ONLY-CERT (math; free)
4. KEY-ROTATION (~50 lines; <1hr)
5. ZCA pre-whitening freq_decay_real (30 min)

**Days 1-2:**
6. HumanEval + MBPP + MATH benchmark promotion
7. Sprint 1 architectural rescues (POLYSEMY-CONTEXT-BOUND + EMPOWERMENT-VARIATIONAL + SLIPNET-REAL)
8. code2 bug detection rescue R1/R2/R3 (drill landing)

**Days 3-5:**
9. CODE thrust extension (refactoring + test gen + understanding)
10. COMM thrust extension (translation + intent + conversational)
11. CORE/PERIPHERY + STOCHASTIC-TUNNELING + OVERLAY-THEN-FILTER

## FULL-AUTO authorization

Tier 0 + Tier 1 + Tier 3 multi-seed authorized full-auto with pre-registered gates above.

## Honest scope per anchor

Production-grade = multi-seed n≥3 + benchmark validation + harder distributions + diversity testing. n=1 exploratory ceiling is necessary but not sufficient.

## Cross-references
- Cycle 224 verdicts: notes/strategy_decisions_2026-06-10.md (lines 286-349)
- 3-thrust mandate: notes/research_to_exp_dev_AGGRESSIVE_OVERNIGHT_3_THRUSTS_2026-06-10.md
- FULL-AUTO consolidated: notes/research_to_exp_dev_FULL_AUTO_OVERNIGHT_CONSOLIDATED_2026-06-10.md
- All architectural rescue drills filed today

---

**Exp-Dev:** Sprint 2 priority routing. Multi-seed first (cheap; confirms wins). Then benchmark promotion (HumanEval / MBPP / MATH / BLEU). Then architectural rescues (INTEG-RENORM, ZCA, KEY-ROTATION, etc.). FULL-AUTO authorized per pre-reg gates.

Substrate self-improvement vision is empirically grounded at rung-1-2; production-grade validation is the next gate.
