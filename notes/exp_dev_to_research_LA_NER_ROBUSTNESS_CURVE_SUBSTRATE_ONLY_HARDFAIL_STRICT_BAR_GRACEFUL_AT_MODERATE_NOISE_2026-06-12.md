# Exp-Dev -> Research: L-A substrate NER adversarial-robustness curve (SUBSTRATE-ONLY, no LLM frame per USER directive) = HARD_FAIL on strict 20%-noise bar, but moderate graceful degradation (83% retention @10%, 63% @20%)

**Date:** 2026-06-12 (Day 4, Cycle 50)  **From:** Exp-Dev (full-auto)

## Result (`exp_la_ner_adversarial_robustness_cpu_v1.py`, substrate Tier-A NER, 3 seeds, ran dashboard-visible via local_cpu_queue)

| char-noise | NER span-F1 (mean +/- SD) | retention vs clean |
|---|---|---|
| 0% | 0.6441 +/- 0.010 | 100% |
| 5% | 0.5764 +/- 0.009 | 89% |
| 10% | 0.5330 +/- 0.013 | 83% |
| 20% | 0.4064 +/- 0.008 | 63% |

**VERDICT: HARD_FAIL** on my strict pre-reg (HP needed F1 >= 0.55 at 20% noise; got 0.41).

## Honest substrate-property reading (NO LLM comparison -- the curve IS the artifact)

This is a substrate-only robustness curve (substrate-quality-first per USER directive; LLM reference frame dropped). Substrate-classical
NER (structured perceptron + Viterbi):
- Degrades GRACEFULLY at MODERATE noise: 89% retention at 5% char-noise, 83% at 10%.
- Degrades more steeply at HEAVY noise: 63% at 20% (1-in-5 chars perturbed -- aggressive).
- The intrinsic-property claim: "substrate-classical NER retains 83% of clean F1 under 10% char-level corruption via structured-prediction
  + Viterbi consistency; falls to 63% under 20% corruption." Char-shape/affix features carry signal under moderate noise; heavy noise
  erodes the lexical features the emitter relies on.

The strict 20%-bar HARD_FAIL is honest: substrate is robust-ish at moderate noise, not at heavy noise. The curve is the substrate-product
artifact regardless of the threshold.

## Possible mechanism-deepening connection

L-A's heavy-noise drop (lexical features erode) motivates the **char-CNN ablation** (Research mechanism-deepening cell 2): sub-word
morphology features should help robustness under char-noise specifically. So the mechanism-deepening ablations (char-CNN especially)
could ALSO be measured under noise -> a robustness-via-mechanism-extension story. Flag for the ablation design.

## Status / compaction
- L-A done (committed). Both queue lanes dashboard-visible confirmed (graph-prop GPU + L-B/L-A CPU).
- NEXT: substrate-only NER mechanism-deepening ablations (gazetteer / CRF transitions / char-CNN) at 5%/10%/100% data -- per your reroute.
- Post-compaction brief written: notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-12_cycle50.md (+ MEMORY.md pointer).
