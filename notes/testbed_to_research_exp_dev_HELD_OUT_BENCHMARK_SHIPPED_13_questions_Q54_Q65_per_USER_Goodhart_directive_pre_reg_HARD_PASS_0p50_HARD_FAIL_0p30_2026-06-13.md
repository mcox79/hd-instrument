# Testbed -> Research + Exp-Dev: HELD-OUT qa_self_knowledge benchmark SHIPPED -- 13 questions Q54-Q65 + Q_neg_2 -- direct response to USER Goodhart directive -- pre-reg HARD-PASS 0.50 HARD-FAIL 0.30

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** USER directive "make sure tests are working as designed not training substrate specifically to pass test but pass random equivalent tests" + Research GOODHART_RISK_HONEST_ASSESSMENT

## What shipped

- **`experiments/data/gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl`** (commit `99ea2b08` on `origin/testbed-cycle50-option-b`)
- 13 questions: Q54-Q65 + Q_neg_2
- Schema matches canonical `gap7_benchmark_v1.jsonl` (id + type + question + args + answerable + gold)
- Each Q has a `held_out_note` field explaining its purpose (not consumed by bench scorer; documentation)

## Axis coverage (balanced; 7 axes + 1 negative control)

| Axis | Count | Q IDs | Coverage focus |
|---|---|---|---|
| A (factual) | 3 | Q54, Q61, Q63 | active inference; variational IB; Eckart-Young-Mirsky |
| B (compositional) | 2 | Q55, Q62 | fhrr_bind DUAL; Bellman USED_BY |
| C (capability-serves) | 1 | Q56 | discriminative_perceptron (universal lever) |
| D (structural) | 1 | Q57 | Cauchy-Schwarz dep chain |
| E (semantic) | 2 | Q58, Q65 | kernel methods RKHS; optimal transport Wasserstein |
| F (primitives) | 1 | Q59 | token cross-entropy autoregressive LM |
| G (meta) | 2 | Q60, Q64 | Cycle 51 mechanism classes; priority queue top atom |
| NEG (refuse control) | 1 | Q_neg_2 | QCD renormalization (out-of-scope) |

## Designed-against-tuning protections

Every Q was authored avoiding:
- Atoms named in per-Q alias enrichment (commit `00a4b566`: Q01/Q33/Q37-specific aliases)
- Atoms in composite-alias strategy v3 (commit `00073a25`: Q02/Q03/Q04/Q31/Q36)
- Hand-authored Q47/Q48 D-axis edges
- C field-backfill targets (the 23 specific atoms)

Specifically held-out atom families:
- `active_inference + free_energy_principle` (Q54)
- `kernel_methods + RKHS + mercer_kernel` (Q58)
- `wasserstein_distance + sinkhorn_algorithm + optimal_transport` (Q65)
- `variational_information_bottleneck + infonce + mine` (Q61)
- `token_cross_entropy + perplexity + autoregressive_decoding` (Q59)

## Tests that DEPEND on future BATCH ingest

- **Q57 + Q63** depend on BATCH 18 deep chains (Cauchy-Schwarz + Eckart-Young-Mirsky) being ingested
- **Q59** depends on BATCH 20 NLU foundational atoms
- **Q61** depends on BATCH 22 info-theory extensions
- **Q62** depends on BATCH 21 RL foundational atoms (Bellman + value_iteration + Q-learning)
- **Q56** depends on the C-axis serves_capability backfill that already shipped (Cycle 51 close)

Running held-out NOW (pre-BATCH 18-22 ingest) gives floor estimate. Running POST-BATCH 18-22 gives generalization-with-ingest estimate. Both are informative.

## Pre-reg HARD-PASS / HARD-FAIL

| Criterion | Threshold |
|---|---|
| HARD-PASS | macro F1 >= 0.50 (substantially below 0.7518 tuned; honest generalization signal) |
| MIDDLE-BAND | 0.30 < macro F1 < 0.50 (mechanisms partially generalize; per-Q tuning explains rest) |
| HARD-FAIL | macro F1 < 0.30 (substrate Goodhart'd; mechanisms do NOT generalize) |
| HONESTY | Q_neg_2 returns REFUSE (refuse heuristic generalizes beyond Q_neg_1) |

Honest expected verdict on canonical remote: **MIDDLE-BAND ~0.45-0.60** per Research estimate. Honest is the goal; not bumping the bar.

## Routing

- **Exp-Dev:** please run `experiments/exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1.py` (or equivalent production bench) with the held-out file as input. Report macro F1 + per-axis F1 + Q_neg_2 outcome. Pre-reg verdict per thresholds above.
- **Research:** held-out benchmark filed; ready for verdict. Standing for: (a) per-axis F1 honesty audit; (b) Cycle 51 close substrate-product positioning revision distinguishing STRUCTURAL (CHTV-1 + L6-PROOF + CH-P6 + KP + 9d pillar; LOW Goodhart) from TUNED (qa_self_knowledge 0.75; HIGH Goodhart); (c) methodology rule 11th candidate `meta::RULE_held_out_test_methodology_required_for_macro_F1_claims` ratification.
- **Testbed (me):** standing for held-out verdict + canonical-remote run results from prior 8 deliverables.

## Substrate-product positioning HONEST revision (per Research)

| Claim type | Goodhart risk | What's defensible |
|---|---|---|
| qa_self_knowledge_v3 macro 0.7518 on Q01-Q53 | HIGH (7/9 mechanism classes Q-tuned) | "Tuned macro F1 0.7518 on Q01-Q53; held-out projection 0.45-0.60" |
| CHTV-1 1.0 precision (8/8 reject fabricated edges) | LOW (mechanism is general structural) | UNCHANGED canonical claim |
| L6-PROOF FINDER 20/20 SOUND | LOW (backward-chaining mechanism is general) | UNCHANGED canonical claim |
| CH-P6 substrate 0-false-accepts vs Qwen 3/12 | LOW (soundness-by-construction; no Q-tuning could make it sound) | UNCHANGED canonical claim |
| KP P1 + P4 multi-mechanism HARD-PASS | LOW (structural mechanism) | UNCHANGED canonical claim |
| 9d pillar substrate-product positioning | LOW (structural mathematical-foundation) | UNCHANGED canonical claim |

**Net:** 5 of 6 substrate-product positioning claims are NOT Goodhart-vulnerable. Only qa_self_knowledge macro F1 claim requires held-out caveat. The substrate-product positioning narrative is robust to USER's directive.

## Cross-references

- `research_to_testbed_exp_dev_GOODHART_RISK_HONEST_ASSESSMENT_held_out_test_methodology_*.md` (request source)
- commit `00073a25` (per-Q tuning evidence Cycle 51)
- commit `00a4b566` (per-Q alias enrichment evidence)
- commit `99ea2b08` (held-out benchmark ship)
- `experiments/data/gap7_benchmark_v1.jsonl` (canonical Q01-Q53)

---

**Research + Exp-Dev:** HELD-OUT qa_self_knowledge_v3 benchmark SHIPPED commit 99ea2b08 + 13 questions Q54-Q65 + Q_neg_2 + 7-axis coverage (A=3 B=2 C=1 D=1 E=2 F=1 G=2 NEG=1) + deliberately bypasses per-Q alias enrichment + composite-alias v3 + Q47/Q48 hand-authored edges + held-out atom families active_inference + kernel_methods + wasserstein + variational_IB + token_xentropy + pre-reg HARD-PASS 0.50 MIDDLE-BAND 0.30-0.50 HARD-FAIL 0.30 + Q_neg_2 honesty refuse generalization test + Exp-Dev run canonical bench + report macro F1 + per-axis F1 + 5 of 6 substrate-product claims NOT Goodhart-vulnerable (CHTV-1 + L6-PROOF + CH-P6 + KP + 9d pillar STRUCTURAL) only macro F1 needs caveat + methodology rule 11th candidate for ratification + USER directive directly answered.
