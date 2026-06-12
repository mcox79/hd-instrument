# Pre-registration: External-gazetteer NER ablation (L-B mechanism deepening, Ablation 3)

**Date:** 2026-06-12 (Day 4)
**Cell:** experiments/exp_ner_gazetteer_external_cpu_v1.py
**Routing:** research_to_exp_dev_L_B_REROUTE...MECHANISM_DEEPENING (substrate-quality-first; NO LLM frame)
**Lane:** local_cpu_queue (laptop CPU; dashboard-visible)

## Hypothesis
An EXTERNAL discrete feature library (curated PER/LOC/ORG name lists -- prior knowledge the model
cannot learn from sparse labels) lifts the LOW-DATA regime of substrate-classical NER, with a
low-data-win shape (largest lift at 5pct, shrinking to ~flat at 100pct, per substrate-aux-features-
shrink-with-data). The existing self-gazetteer cannot do this: at 5pct data it is as sparse as the
training set it is derived from. This is the discrete-feature-library low-data-win substrate-product claim.

## Design
PAIRED comparison at train fractions {5pct, 10pct, 100pct} x 3 seeds. Same train subset trained TWICE
(same seed): baseline emit-features vs baseline + binary external-gazetteer membership features
(token in PER / LOC / ORG list, for prev/cur/next token). 4-type CoNLL collapse -> directly comparable
to the L-B few-shot curve (5pct=0.404, 10pct=0.501, 100pct=0.644). Reports baseline F1, gaz F1, lift/fraction.
External lists: PER=198, LOC=207, ORG=129 single lowercase tokens (curated, not derived from train).

## Pre-registered verdict bands (substrate-property; no LLM comparison)
- **HARD-PASS:** gaz F1@5pct >= 0.50 (+0.10 over L-B baseline 0.404) AND lift@5pct > lift@100pct (low-data-win shape)
- **MIDDLE:** gaz F1@5pct in 0.45-0.50
- **HARD-FAIL:** gaz F1@5pct < 0.45 (external gazetteer does not meaningfully lift low-data NER -- coverage too thin or shape features already subsume)
- **UNKNOWN:** data load fails

## Substrate-product artifact (stands alone, no LLM frame)
Whether a curated discrete external feature library is a usable low-data lever for substrate-classical
structured-prediction NER, and the shape of its marginal contribution as labeled data scales.
