# Research -> Exp-Dev: brain-can-do-it rule EMPIRICALLY VINDICATED + ASDiv solver next + SVAMP Path 2/4 + NER 4 remaining paths + POS data-efficiency revision

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** math-WK LEX atoms ASDiv +0.114 STRONG validation + SVAMP gap is SELECTION not WK + NER continuing

## TL;DR

- **ASDiv "0.68 world-knowledge boundary" EMPIRICALLY REFUTED** via substrate-self-referential LEX_constant atoms. 3-op +0.114 lift (0.671 -> 0.785). Brain-can-do-it rule VINDICATED on first empirical test.
- SVAMP: gap is SELECTION not WK (revealed by Path 1 isolating WK lever); pivot to Path 2 multi-hop role-binding + Path 4 subset-sum
- NER: gazetteer +0.007 saturates at full data; 4 more substrate-only paths remain (multi-seed + substrate-CRF + Cycle #5 mechanism atoms + Tier-2 schema)
- POS data-efficiency: moderate (0.75@100, 0.81@250, 0.90@2500); revise aux-features-shrink memory to reflect substrate is COMPETITIVE in low-data not extreme-dominant
- Tier 4 second-appearance candidate: substrate-self-referential approach (rule 8) empirically validated
- Memory worthy: ASDiv +0.114 vindicates user's pushback against my drill-defeatism pattern

## ASDiv vindication memory + framing

The earlier "world-knowledge boundary" was a MEASUREMENT ARTIFACT of base oracle missing substrate's semantic memory. NOT an architectural ceiling.

Substrate-self-referential math-WK LEX atoms (rule 8 us-or-substrate):
- 1-op +0.033 (0.679 -> 0.712)
- 2-op +0.047 (0.814 -> 0.861)
- **3-op +0.114 (0.671 -> 0.785)**

3-op lift LARGEST = where world-knowledge matters most (most items need non-text constants). Substrate semantic memory closes the gap.

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] standing rule: this is FIRST EMPIRICAL VINDICATION today. Memory entry filing.

Remaining gap (0.785 to 1.0) = multi-fact / non-adjacent constants. Path forward: multi-hop world-knowledge (LEX atom chain decoding via HRR binding).

## SVAMP -- gap is SELECTION not WK (informative HARD_FAIL)

Path 1 result: -0.003 lift = WK doesn't apply to SVAMP. Adjacency restriction prevented over-trigger. Honest isolation of mechanism.

SVAMP failure mode = operand-pair SELECTION (multi-number cross-entity pairing: "290 bananas / 2 groups", "each group has 5 bananas"). This is binding chain composition, NOT semantic memory.

### SVAMP Path 2: multi-hop role-binding selector

Per substrate-product enumeration: role-filler chain via HRR binding.

```
Problem: "Bob has 290 bananas in 2 groups. Each group has 5 bananas. How many groups of 5?"

Substrate decomposition:
  bind(role=total, filler=290)
  bind(role=group_count, filler=2)
  bind(role=per_group, filler=5)
  unbind chain: total / per_group = answer
```

Mechanism: discriminative perceptron over role-binding chain (substrate-product Tier 3 algorithm). Substrate has HRR/FHRR bind + unbind + cleanup primitives. Wiring exists; chained-decoder for SVAMP NOT yet built.

Expected lift: 5-15pp on SVAMP. Target: 0.40+. Cell pre-reg per drill-defeatism: HARD-PASS >= 0.42 / MIDDLE 0.40-0.42 / FAIL < 0.40.

### SVAMP Path 4: subset-sum search

Alternative substrate-product mechanism: instead of pair-selection + op-classifier, search subset {n1, ..., nk} + ops {+,-,*,/} for subset summing/diffing to answer-shape. Like text-to-arithmetic-program over substrate algebra.

Cell pre-reg: HARD-PASS >= 0.42 / MIDDLE 0.38-0.42 / FAIL < 0.38.

Path 2 first (binding-chain). Path 4 if Path 2 HARD_FAIL.

## ASDiv solver -- realize +0.114 ceiling into actual accuracy

Path 1+2 oracle = +0.114 ceiling. Current ASDiv solver accuracy 0.22 << oracle ceiling 0.785. Build ASDiv solver realizing the WK-augmented ceiling:

```
ASDiv solver pipeline:
  1. Extract text-numbers + WK-constants (via concept partition lookup)
  2. Number pool = text + WK ∪ pruned for plausibility
  3. Selector picks operand subset (1-3 numbers)
  4. Op-classifier predicts operation chain
  5. Execute + validate via verifier
```

Cell pre-reg: HARD-PASS >= 0.32 (from 0.22 baseline; matches earlier Math-WK pre-reg) / MIDDLE 0.28-0.32 / FAIL < 0.28.

Run alongside SVAMP Path 2.

## NER -- 4 substrate-only paths remaining (boundary still NOT accepted)

Per brain-can-do-it rule: 5 paths must FAIL before architectural claim. Gazetteer = 1/5 paths run. 4 remaining:

1. **Multi-seed n=5** on NER baseline + best lever (Path 2 or 3) -- promote single-seed Tier B numbers to multi-seed Tier-A confidence
2. **Substrate-CRF universal Tier-1 shared features** -- per substrate-CRF drill: build shared feature extractor library (Brown + phrase + morphology + gazetteer + position + context-window) -- not yet built
3. **Cycle #5 newly accepted atoms as features** -- CAP_em_algorithm + CAP_bayesian_inference + CAP_discriminative_perceptron present as substrate atoms but NOT WIRED to NER feature extractor; substrate-self-referential
4. **Tier-2 schema construction grammar** -- per construction grammar drill: entity-type recognition via Tier-2 schema-matching; substrate has Tier-2 schemas

Execute in cheapest order:
1. NER multi-seed (cheapest)
2. Cycle #5 mechanism atoms as features (cheap)
3. Substrate-CRF Tier-1 shared features (moderate)
4. Tier-2 schema construction grammar (moderate)

Cell pre-reg each: HARD-PASS lift >= +0.03 / MIDDLE 0-+0.03 / FAIL <= 0.

## POS data-efficiency revision

Per Exp-Dev's data points: 0.75@100 sents / 0.81@250 sents / 0.90@2500 sents.

This is MODERATE data-efficiency, not extreme. Substrate competitive in low-data not dominant.

Revising [[substrate-aux-features-shrink-with-data-2026-06-11]] memory framing: substrate features ARE more valuable in low-data but the regime is BROADER than "small corpora". Substrate competitive across 100-2500 sentence range; standard NLP benchmarks at 5K-50K sents likely closer to saturation.

Refined substrate-product positioning:
- OLD: "substrate features LOW-DATA REGIME OPTIMAL (small corpora)"
- NEW: "substrate features MORE EFFICIENT per training example than lexical-only baselines; competitive across 100-2500 sentence range; standard 5K+ sent benchmarks closer to feature saturation"

Filing memory update.

## Tier 4 second-appearance candidate

Findings 13 was Tier 4 first appearance (substrate-extracted methodology rule). Today's ASDiv +0.114 vindication = Tier 4 second-appearance candidate (substrate-self-referential approach via rule 8 empirically validated).

5-tier progression: Tier 3 -> Tier 4 sustained measurement begins; 2 candidates Day 1+. Need 1+ per week sustained.

## Cycle #9 candidate

Cycle #9 Type A (extended): substrate-self-referential LEX atom approach validated empirically + transferable across capabilities (math-WK pattern generalizes to:
- Date/time word problems (LEX_constant_time)
- Geometry word problems (LEX_constant_geometry)
- Body-parts word problems (LEX_constant_body_parts)
- Money word problems (LEX_constant_money)

Each closes corresponding domain-knowledge gap. Sustained generalization signal Type A.

## Recommended next priorities

| Priority | Cell | Cost | Gate |
|---|---|---|---|
| 1 | ASDiv solver realize +0.114 ceiling | 2-3 hr CPU | HARD-PASS >=0.32 |
| 2 | SVAMP Path 2 multi-hop role-binding selector | 3-4 hr CPU | HARD-PASS >=0.42 |
| 3 | NER multi-seed n=5 (cheapest remaining substrate path) | 1-2 hr CPU | HARD-PASS lift >=+0.03 |
| 4 | NER Cycle #5 mechanism atoms as features | 2 hr CPU | HARD-PASS lift >=+0.03 |
| 5 | SVAMP Path 4 subset-sum (if Path 2 HARD_FAIL) | 2-3 hr CPU | HARD-PASS >=0.42 |

Multi-seed promotions stack alongside priorities 1-4.

## Cross-references

- ASDiv vindication: data/exp_asdiv_math_wk_oracle_cpu_v1/metrics.json
- SVAMP isolating WK: data/exp_svamp_math_wk_lex_cpu_v1/metrics.json
- USER-locked rule: feedback_brain_can_do_it_no_boundary_acceptance_2026-06-11
- Boundary-rejection routing: notes/research_to_exp_dev_BOUNDARIES_REJECTED_BRAIN_CAN_DO_IT_FULL_PATH_ENUMERATION_2026-06-11.md
- Math-WK routing: notes/research_to_testbed_MATH_WK_LEX_ATOMS_READY_2026-06-11.md
- Aux-features-shrink memory (revision pending)

---

**Exp-Dev:** ASDiv 3-op +0.114 lift VINDICATES brain-can-do-it rule -- "world-knowledge boundary" was MEASUREMENT ARTIFACT of base oracle missing substrate semantic memory NOT architectural ceiling + SVAMP gap CORRECTLY ISOLATED as SELECTION not WK pivot to Path 2 multi-hop role-binding + NER 4 paths still NOT YET RUN multi-seed + Cycle #5 mechanism atoms + substrate-CRF Tier-1 + Tier-2 schema NO boundary acceptance + POS data-efficiency moderate revise aux-features-shrink memory framing + Recommended priority order ASDiv solver realize +0.114 ceiling 0.22->0.32 + SVAMP Path 2 multi-hop + NER multi-seed + NER Cycle #5 mechanism + SVAMP Path 4 subset-sum + memory ASDiv vindication filing.
