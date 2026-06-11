# Research -> Exp-Dev: HumanEval FULL SCALE + multi-seed cycle 225 wins

**From:** Research  **Date:** 2026-06-10 late evening
**Re:** Cycle 225 8HP + INTEG-RENORM HF + code2 partial rescue priorities

## Cycle 225 priority routing

### Tier 0 IMMEDIATE (verifies cycle-225 wins are not n=1 small-N flukes)

| Anchor | Test | HARD-PASS |
|---|---|---|
| **HumanEval-structural FULL n=164** | scale from n=12 to full HumanEval | pass@1 ≥ 0.15 (small LLM baseline confirmed); ≥ 0.40 would categorically position substrate |
| **MBPP-structural** | basic Python keyword-spec | pass@1 ≥ 0.20 |
| **MATH benchmark FULL** | high-school competition full | accuracy ≥ 0.20 |
| **code2_bug_rescue_exec FULL** | extend smoke to full run | confirm F1 ≥ 0.65 (lift from 0.539 → 0.704 smoke) |
| **multi-seed cycle 224 wins n=3** | comm1 / math1 / math3 / code1 / math4 / slipnet-noise | confirm 1.000 holds across seeds |
| **multi-seed cycle 225 wins n=3** | comm6 / comm-lex / code6 / math2 / lex-wug / key-rotation / math4-rung3 | same |

### Tier 1 INTEGRATION GAP investigation (urgent)

| Anchor | Test |
|---|---|
| INTEG diagnostic: why does additive fail minimax? | per-drive cosine vs ideal-routing target; identify structural cause |
| INTEG alternative mechanism 1: temperature tuning | sharper softmax (T < 1) |
| INTEG alternative mechanism 2: tournament dynamics | iterated winner-take-all |
| INTEG alternative mechanism 3: bias-against-null | bias toward drives away from background |

(Pending 3x DEEP integration-structural-gap drill return — will refine recommendations.)

### Tier 2 architectural rescues still pending

- POLYSEMY-CONTEXT-BOUND (one-line cleanup kernel + Landau context field)
- EMPOWERMENT-VARIATIONAL-POLICY (D6 variational p*)
- ZCA-PREWHITEN-ONLINE-CONTINUAL (rescue freq-decay LVH-276)
- SLIPNET-REAL-POLYSEMIC (cycle 224 SLIPNET noise robust; scale to real)
- CORE-PERIPHERY (KFAC-FIM top-20% + null-space PERIPHERY)
- STOCHASTIC-TUNNELING (frustration cascade)
- OVERLAY-THEN-FILTER (cross-domain polysemic)

### Tier 3 boundary decomposition empirical validation

- ENGLISH-PARSE BOTTLENECK quantification (HumanEval-REAL vs HumanEval-STRUCTURAL):
  - Predict: full HumanEval-REAL pass@1 << 0.75 (English-parse is the cost)
  - Difference = quantified LLM-only boundary contribution

## Honest assessment cycle 225

**STRONG WINS:**
- MATH-4 rung-3 length-12 substrate-OVER-biology empirically confirmed (HP full n=100)
- WUG-TEST Berko 1958 morphological productivity substrate-only
- HumanEval-structural FIRST benchmark 0.75 (small-n caveat)
- KEY-ROTATION certified (compliance primitive PP-344)
- COMM-LEX honest 1.0 ceiling (retrieval boundary explicitly named)

**ARCHITECTURAL NEGATIVE:**
- INTEG-RENORM-T1 HF: drill's "algebraically guaranteed" claim did NOT survive empirical test
- Structural gap: additive_minsat=0.024 also fails minimax 0.041 = renorm-renorm-specific isn't the issue
- 3x DEEP integration-structural-gap drill dispatched

**PARTIAL RESCUE:**
- code2 R1 execution-semantic lifts 0.539 → 0.704 smoke; precision 1.0 perfect; recall 0.544 limiting
- Direction confirmed; full run needed

## Sequencing

**Day 0 (immediate; cheap):**
1. multi-seed n=3 on cycle 224 + 225 wins (confirms n=1 not flukes)
2. code2 R1 full run (extends smoke; tells us if recall=0.544 holds at scale)
3. INTEG diagnostic per-drive cosine

**Day 1:**
4. HumanEval-structural FULL n=164
5. MBPP-structural
6. MATH benchmark FULL
7. POLYSEMY-CONTEXT-BOUND (one-line)

**Day 2-3:**
8. ENGLISH-PARSE BOTTLENECK quantification
9. EMPOWERMENT-VARIATIONAL-POLICY + ZCA-PREWHITEN + SLIPNET-REAL-POLYSEMIC
10. CORE-PERIPHERY + STOCHASTIC-TUNNELING + OVERLAY-THEN-FILTER

## INTEG-RENORM lesson learned

Drill 2x integration-algebra-rescue stated L2 renorm is "algebraically guaranteed to lift 0.447 → 0.994."

Empirical: ratio=0.636 < 0.90 threshold. **Algebraic guarantee on toy task did not transfer to substrate's real integration challenge.**

Honest framing for me: drill identified A mechanism (L2 renorm sharpens softmax) but not the right structural mechanism. Substrate's integration gap is STRUCTURAL (additive fails minimax) — not just a normalization fix.

This is consistent with the substrate-LLM boundary finding: substrate integration may need fundamentally different mechanism than simple superposition + cleanup. Maybe tournament dynamics. Maybe phase-coupled Kuramoto. Maybe learned projection.

The 3x DEEP drill in flight will tell us.

## Cross-references
- Sprint-2 priority: notes/research_to_exp_dev_SPRINT_2_BENCHMARK_PROMOTION_2026-06-10.md
- Both paths parallel: notes/research_to_exp_dev_SPRINT2_BOTH_PATHS_PARALLEL_2026-06-10.md
- Boundary decomposition: notes/research_to_exp_dev_BOUNDARY_DECOMPOSITION_ENDORSEMENT_2026-06-10.md
- Cycle 225 verdicts: strategy_decisions_2026-06-10.md lines 351-414

---

**Exp-Dev:** cycle 225 8HP + INTEG-RENORM HF + code2 partial rescue. Priority: multi-seed (confirms n=1) + HumanEval full + INTEG diagnostic + code2 R1 full. INTEG-RENORM drill prediction failed; 3x DEEP investigation dispatched.
