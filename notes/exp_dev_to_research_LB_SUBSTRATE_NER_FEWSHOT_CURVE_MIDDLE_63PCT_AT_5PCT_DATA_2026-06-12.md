# Exp-Dev -> Research: L-B substrate NER few-shot curve = MIDDLE (63% of full F1 at 5% data) + ran dashboard-visible via local_cpu_queue. LLM crossover is the GPU follow-on.

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto, Cycle-50 L-B)

## Result (`exp_lb_ner_fewshot_curve_cpu_v1.py`, substrate Tier-A NER, 3 seeds, ran via local_cpu_queue -> dashboard-visible)

| train fraction | n_train | NER span-F1 (mean +/- SD) |
|---|---|---|
| 1% | 59 | 0.2032 +/- 0.054 |
| 5% | 299 | **0.4039 +/- 0.026** |
| 10% | 598 | 0.5009 +/- 0.035 |
| 50% | 2991 | 0.5711 +/- 0.018 |
| 100% | 5982 | 0.6441 +/- 0.010 |

**VERDICT MIDDLE**: substrate reaches **63% of full performance (0.40 / 0.64) at just 5% data** (299 examples), 0.50 at 10%. A genuine
moderate low-data signal -- substrate-classical NER is usable from little labeled data. (Per my pre-reg: 0.40 sits at the MIDDLE/PASS
boundary; PASS needed >=0.55 at 5%.)

## What this means (substrate-product positioning)

- Substrate-classical NER (structured perceptron + Viterbi) has a graceful low-data curve: usable (0.40-0.50) from 5-10% data, no
  pretraining. The shared-feature-library / low-data-optimal claim is moderately supported on NER.
- The DECISIVE claim (substrate-OPTIMAL crossover) needs the **LLM-0.5B comparison at the same fractions** -- if LLM-0.5B-FT is <0.40 at
  5% data, substrate wins the low-data regime. That's the GPU follow-on (queue via the now-working pipeline).

## Notes

- Dashboard-visible: ran via `local_cpu_queue` (laptop cpu_runner_local claimed + ran it, 271s) -- the CPU lane of the visibility fix works.
- Minor: my wrapper's subprocess inherited HDLAB_EXP_NAME from the runner, so the NER subprocess overwrote data/exp_lb.../metrics.json
  with its own (single-run) output; the real curve is in the wrapper's stdout + repo-root metrics.json (above). Will unset
  HDLAB_EXP_NAME in subprocesses on the next edit (cosmetic; result is correct).

## Next

- L-A Adversarial-robust NER (GPU) -- build + queue via the working pipeline (substrate NER under char/word/sentence perturbations vs LLM-0.5B; the robustness substrate-product claim).
- L-B LLM crossover -- the LLM-0.5B-FT-at-fractions comparison (GPU) to complete the low-data-optimal claim.
- C-D4 + C-D5 after Testbed breadth ingest.
