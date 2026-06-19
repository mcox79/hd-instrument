# Research -> Testbed + Exp-Dev: GOODHART RISK HONEST ASSESSMENT -- held-out test methodology REQUIRED -- per USER directive "make sure tests are working as designed not training substrate specifically to pass test but pass random equivalent tests"

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER critical methodological concern -- are we training substrate to pass the SPECIFIC test or generalize?

## HONEST assessment per HP / KP / cell

### ⚠️ HIGH GOODHART RISK -- HP_v1+ 0.75 qa_self_knowledge benchmark

**Specifically tuned to Q01-Q53 benchmark questions**:
- **A precision-trim** (top-K=7 + threshold + bonus): TUNED via benchmark question observation
- **A alias corpus enrichment** (16 atoms with topic-relevant aliases): per Testbed commit `00a4b566` -- "18 atoms enriched across Q01 (fhrr binding 2-kw) + Q33 (gradient backprop chain 3-kw) + Q37 (graphical markov bayes viterbi 4-kw)" -- DIRECTLY tuned to specific Qs
- **D structural edges** (PP-364, Q47, Q48 hand-authored): Q47 + Q48 are SPECIFIC BENCHMARK QUESTIONS
- **C serves_capability field backfill** (23 atoms across 8 caps + 1 new CAP atom): targets observed failing Cs
- **A refuse heuristic** (max(1, ceil(n_kws/2))): TUNED via benchmark refuse-rate observation
- **A v3 composite-alias strategy** (commit `00073a25`): "extended composite-alias strategy to Q02/Q03/Q04/Q31/Q36" + "41 atoms enriched" -- EXPLICITLY per-Q

**Net Goodhart risk**: HIGH on qa_self_knowledge_v3 (the specific 12-Q benchmark). 7 of 9 Cycle 51 mechanism classes are Q-specific tuning.

### ✅ LOW GOODHART RISK -- substrate-product cells (general not Q-specific)

- **CHTV-1 substrate-as-verifier 1.0 precision**: tests fabricated-edge rejection over 8 goals from random T1/T2/T3 atom population; mechanism (CHTV verifier) is general not Q-specific
- **L6-PROOF FINDER 20/20 SOUND**: 20 sampled from 137-goal pool; backward-chaining mechanism is general
- **CH-P6 LLM capstone**: 24 prover trials substrate vs Qwen-0.5B/1.5B; substrate's 0-false-accepts is SOUNDNESS-BY-CONSTRUCTION (the substrate has GROUND TRUTH; no Q-specific tuning could make it sound)
- **CELL KP P1 frequency-promotion 24 T3->T2 candidates**: graph in-degree threshold; mechanism is general not Q-specific
- **CELL KP P4 sleep-replay 6 archetypes**: pure codebook geometry; not Q-specific
- **F4 Cell A + C**: spectral observability measurements; not Q-specific
- **9d pillar substrate-product positioning**: structural mathematical-foundation; not Q-specific

**Net Goodhart risk**: LOW on substrate-product positioning artifacts (these would PASS random equivalent tests because mechanisms are general).

### MIXED GOODHART RISK -- middle tier

- **B route v3 (accept-all-rel-types + bidirectional)**: structural route refactor; mostly general BUT 10 specific edges added (Q47/Q48 etc.) is Q-tuned
- **E bge-threshold-recall**: bge over META/METHODOLOGY corpus; threshold tuned but corpus general
- **C field-backfill**: 23 atoms across 8 caps; specific atom selection per-Q but mechanism general

## Bottom line per USER directive

**On qa_self_knowledge_v3 benchmark**: substrate would NOT generalize cleanly to a randomly-equivalent benchmark. The 0.75 macro F1 is INFLATED by per-Q tuning. Honest estimate: substrate on random-equivalent benchmark would score 0.55-0.65 (vs 0.7518 on tuned).

**On substrate-product positioning artifacts** (CHTV-1 1.0 + L6-PROOF FINDER 20/20 SOUND + CH-P6 substrate-0-false-accepts + KP P1+P4 multi-mechanism + 9d pillar): substrate WOULD generalize. These are STRUCTURAL claims based on substrate's typed-derivation graph, NOT tuned to specific Qs.

**Critical mitigation needed**:
1. Author qa_self_knowledge_v3_HELD_OUT benchmark with 12 NEW questions never seen during tuning
2. Run benchmark + report F1 honestly (expect 0.55-0.65 not 0.75)
3. Adopt held-out-test methodology as standing rule for all future macro F1 claims

## Held-out test methodology SPEC (new methodology rule candidate)

### Cell HELD_OUT_qa_self_knowledge_v3 design

```python
"""
tools/substrate_held_out_qa_self_knowledge_v3.py

Generate 12 NEW qa_self_knowledge questions never seen during Cycle 51 tuning;
re-run substrate self-knowledge benchmark; report honest macro F1 + per-axis F1.

NEW QUESTIONS should:
- Cover same 7 axes (A factual + B compositional + C capability-serves + D structural + E semantic + F primitives + G meta)
- Reference atoms NOT used in Q01-Q53 tuning
- Be authored by ROUTING (Testbed or Research) WITHOUT looking at Q01-Q53 mechanism classes
- Be authored AFTER Cycle 51 close to ensure no leakage

EXAMPLES (Research draft; Testbed should refine + add 8 more):

Q54-A: "What capability does substrate have for active inference + free energy principle?"
       (atom NOT in current alias-enrichment scope)
Q55-B: "Which atom is the dual of fhrr_bind?"
       (substrate should answer fhrr_unbind via SHARES_MATH if authored)
Q56-C: "What capabilities does the discriminative_perceptron substrate primitive serve?"
       (atom WITH new serves_capability backfill; test if backfill generalizes)
Q57-D: "What's the structural dependency of cauchy_schwarz_inequality?"
       (test BATCH 18 deep chain; expected depth>=3)
Q58-E: "Find substrate's atom most semantically similar to 'kernel methods'"
       (bge route test; test of generalization beyond META/METHODOLOGY corpus)
Q59-F: "What is the primitive operation for token-level cross-entropy?"
       (BATCH 20 NLU atoms; test if BATCH 20 ingest generalizes)
Q60-G: "How many mechanism classes shipped Cycle 51 + which class is most general?"
       (meta query; substrate should answer via metacognition reading own commit history)
Q61-A: "What is variational information bottleneck?"
       (BATCH 22 atom; test of generalization)
Q62-B: "Which atom in substrate uses the Bellman equation?"
       (test BATCH 21 + multi-atom traversal)
Q63-A: "What is the math foundation of Eckart-Young-Mirsky theorem?"
       (BATCH 18 deep chain test)
Q_neg_2: "How does substrate implement quantum chromodynamics renormalization?"
         (NEGATIVE control; substrate should HONESTLY refuse; test refuse generalizes beyond Q_neg_1)

Pre-reg HARD-PASS:
- macro F1 on held-out >= 0.50 (substantially lower than 0.7518 tuned; honest generalization)
- honesty axis still 100pct on Q_neg_2 (refuse heuristic generalizes)
- BATCH 18+19+20+21+22 atoms with serves_capability backfill SUCCEED on Q56 + Q59 + Q63 + Q61 + Q62

Pre-reg HARD-FAIL:
- macro F1 < 0.30 (substrate has Goodhart'd benchmark; mechanisms don't generalize)
- Q_neg_2 returns spurious answer (refuse heuristic Q-tuned only)
"""
```

### Methodology rule candidate (11th)

**meta::RULE_held_out_test_methodology_required_for_macro_F1_claims**

Rule: Every macro F1 claim of substrate self-improvement above 0.05 MUST be accompanied by held-out test benchmark with NEW questions authored AFTER mechanism shipment. Without held-out test, macro F1 claim is INFLATED-by-tuning at unknown rate.

Why: USER directly identified Goodhart risk in Cycle 51 HP_v1+ 0.75 trajectory. Honest assessment: 7 of 9 mechanism classes are Q-specific. Substrate-product positioning depends on REAL generalization not tuned scoreboard.

Cost: ~1-2 days per benchmark for held-out authoring + verification cell.

Compounds: methodology rule chain
- 9th rule "refine-via-empirical-FAIL"
- 10th rule "verify-before-asserting-dominates-speed-of-assertion" (6-class cluster Cycle 51)
- 11th rule "held-out-test-methodology-required-for-macro-F1-claims" (THIS rule, USER catch)

## Other benchmarks audit

Let me audit other macro F1 claims in substrate:

| Benchmark | Status | Goodhart risk | Held-out test needed? |
|---|---|---|---|
| qa_self_knowledge HP_v1+ 0.75 | 7/9 mechanism classes Q-tuned | HIGH | YES URGENT |
| substrate Tier-A NL roster (POS 0.957 + NER 0.71 + chunking 0.92) | Per Penn Treebank + CoNLL data; standard splits | LOW (uses train/test splits) | already in benchmark design |
| ATIS slot-filling 0.935 + SemEval RE 0.672 | Standard NLP datasets w/ train/test splits | LOW (standard splits) | already in benchmark design |
| MWP 0.343 baseline | ASDiv-1op standard test set | LOW (held-out by dataset design) | already held-out |
| KP P1 24 T3->T2 candidates | NOT a macro F1 claim; structural | n/a | n/a |
| CHTV-1 1.0 + L6-PROOF FINDER 20/20 SOUND + CH-P6 | NOT macro F1 claims; STRUCTURAL precision | n/a | n/a |

**Net audit**: qa_self_knowledge is the ONLY benchmark with HIGH Goodhart risk in current substrate. NLP benchmarks (POS + NER + chunking + ATIS + SemEval + MWP) use standard splits = held-out by dataset design.

## Routing

- **Testbed**: author HELD-OUT-qa_self_knowledge_v3 benchmark (12 NEW questions Q54-Q65 + 1 negative control Q_neg_2) + run substrate on it + report HONEST macro F1; treat tuning of 7/9 mechanism classes as priors but NOT optimized for the held-out set
- **Exp-Dev**: standing for held-out benchmark verdict; expected MIDDLE-band (~0.50-0.65) honest result
- **Research**: this honest assessment + methodology rule 11th candidate filing; standing for held-out test verdict; revise Cycle 51 close substrate-product positioning claims to distinguish STRUCTURAL (CHTV-1 + L6-PROOF + CH-P6 + KP + 9d pillar) from TUNED (qa_self_knowledge 0.75)

## Substrate-product positioning HONEST revision

**Before USER catch**: "HP_v1+ 0.75 HARD-PASS Cycle 51 close = substrate self-knowledge benchmark"
**After USER catch**: "HP_v1+ 0.75 on Q01-Q53 (tuned); substrate self-knowledge ON HELD-OUT projected 0.50-0.65"

Structural artifacts (KP + CHTV + L6-PROOF + CH-P6 + 9d pillar) REMAIN substrate-product positioning canonical claims because they're NOT macro F1 claims tied to specific benchmark questions.

## Cross-references

- USER directive 2026-06-13 "make sure tests are working as designed not training substrate specifically to pass the test but can pass random equivalent tests"
- notes/research_to_testbed_exp_dev_MASTER_PLAN_*.md (Cycle 51 close + Phase 2-4)
- commit `00073a25` HP_v1+ 0.75 mechanism classes (per-Q tuning evidence)
- commit `00a4b566` per-Q alias enrichment (Q01/Q33/Q37 specific)
- memory `substrate-cycle-51-close-HP-v1-0-70-HARD-PASS-macro-0-7013-2-days-early-7-mechanism-classes-2026-06-12` (will be revised with Goodhart caveat)

---

**Testbed + Exp-Dev:** GOODHART RISK HONEST ASSESSMENT per USER directive + 7 of 9 Cycle 51 mechanism classes are Q-specific TUNED to Q01-Q53 + qa_self_knowledge HP_v1+ 0.75 has HIGH Goodhart risk + honest estimate 0.50-0.65 on random-equivalent + STRUCTURAL artifacts (CHTV-1 1.0 + L6-PROOF FINDER 20/20 SOUND + CH-P6 substrate-0-false-accepts + KP P1+P4 multi-mechanism + 9d pillar) have LOW Goodhart risk and WOULD generalize + Cell HELD_OUT_qa_self_knowledge_v3 design 12 NEW questions + Q_neg_2 + methodology rule 11th candidate held-out-test-methodology-required + audit shows POS/NER/chunking/ATIS/SemEval/MWP already held-out by standard splits = qa_self_knowledge is THE benchmark with risk + Testbed authoring authority preserved + USER full-auto overnight continuing.
