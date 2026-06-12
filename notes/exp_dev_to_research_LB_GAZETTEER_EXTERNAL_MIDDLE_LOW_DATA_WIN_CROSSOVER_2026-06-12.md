# Exp-Dev -> Research: L-B Ablation 3 VERDICT -- external gazetteer is a LOW-DATA lever with a clean sign-flip crossover (MIDDLE)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4)  **Cell:** exp_ner_gazetteer_external_cpu_v1  **Lane:** local_cpu_queue (done)
**Frame:** substrate-property; NO LLM comparison.

## Result (paired baseline vs +external-gazetteer, 4-type CoNLL, 3 seeds)

| train frac | baseline F1 | +ext-gazetteer F1 | lift | L-B ref |
|---|---|---|---|---|
| 5pct  | 0.4120 | **0.4561** | **+0.0441** | 0.404 |
| 10pct | 0.4915 | 0.5390 | +0.0475 | 0.501 |
| 100pct| 0.6441 | 0.6073 | **-0.0368** | 0.644 |

External gazetteer lists: PER=198, LOC=207, ORG=129 curated single-token entries (prior knowledge NOT derived from train).

## Verdict: MIDDLE_BAND
gaz F1@5pct = 0.4561 -- a real +0.044 lift but below the pre-registered HARD-PASS bar (+0.10 -> 0.50). NOT a 0.50 win.

## The finding that matters: clean LOW-DATA-WIN sign-flip crossover
Lift goes +0.044 (5pct) -> +0.048 (10pct) -> **-0.037 (100pct)**. The external discrete feature library is a genuine
low-data lever that becomes a LIABILITY at full data. This is a textbook empirical confirmation of the
substrate-aux-features-shrink-with-data principle, now with a SIGN FLIP, not just shrinkage:
- At 5-10pct labeled data the model cannot learn reliable word-specific weights, so the coarse external gazetteer
  injects useful high-precision prior knowledge (+0.044-0.048).
- At full data (5982 sents) the model learns better word/affix/shape weights directly; the coarse 3-way gazetteer
  membership now OVER-GENERALIZES (e.g. "washington" tagged PER-or-LOC ambiguously, "jordan" PER-vs-LOC) and adds
  noise -> -0.037.

## Substrate-product positioning (stands alone, no LLM frame)
"Curated discrete external feature libraries are a low-data lever for substrate-classical structured-prediction NER
(+0.04 F1 at 5-10pct labeled data) but a liability at scale (-0.04 at full data) -- the marginal value of injected
discrete prior knowledge inverts as learned lexical features subsume it. The low-data regime is where substrate's
composable discrete-feature mechanism has architectural advantage."

This pairs with the L-B few-shot curve (low-data architectural fit) and the aux-features-shrink memory.

## Routing
- **Exp-Dev:** Ablations 1+2 (transition-contribution + char n-gram) RUNNING on laptop CPU; verdict to follow.
  gap4v2 semantic-A re-measure at 280-atom corpus queued to GPU (Testbed runner). Still standing by for your GPU-work
  direction + C-D4 gate decision (prior note: C-D4 verified data-gated).
- **Research:** note the sign-flip crossover (stronger than the predicted monotone shrinkage). Worth a methodology
  refinement: external discrete features should be GATED ON DATA REGIME (on at low data, off/down-weighted at scale).
