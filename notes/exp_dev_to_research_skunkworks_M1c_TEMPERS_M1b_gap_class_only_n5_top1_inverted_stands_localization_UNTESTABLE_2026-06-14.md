# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): M1c TEMPERS M1b (10th-rule self-correction). At n=55 the gate-relevant signal (top1) stays INVERTED so M1 death holds -- but "all 8 features inverted" was small-n; flatness/peak weakly favor in-coverage. Gap class is only n=5 (structural ceiling); localization test UNTESTABLE.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (M1c)
**Re:** I tried to STRENGTHEN M1b (n=13) to n~65 by measuring confidence-vs-coverage AUC across tuned (v3_60q) + held-out. Verify-before-asserting on my OWN finding. ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_m1c_confidence_coverage_separability_fullset_cpu_v1.py` (remote; bge cache).

## What I found (and what it corrects)

77 questions loaded; 55 coverage-labeled: **in-coverage=50, coverage-gap=5** (no-gold/neg skipped).

Overall AUC (in-coverage vs gap; >0.5 correct, <0.5 inverted):
| feature | AUC |
|---|---|
| flatness | 0.622 |
| peak | 0.594 |
| margin | 0.502 |
| **top1** | **0.434** |
| mass080 | 0.412 |
| mean5 | 0.398 |
| mass070 | 0.366 |
| mean20 | 0.278 |

## Three honest conclusions

### 1. M1 death STANDS (the gate-relevant signal is still inverted)
top1 AUC=0.434 overall (0.286 on held-out alone) and mean5/mean20 < 0.5. A tau-gate thresholds the TOP score; that signal is inverted/uninformative. So M1/M2 confidence-gating on bge cosine remains dead. No walk-back here.

### 2. SELF-CORRECTION: M1b's "all 8 features inverted" was partly small-n
At n=13 all 8 features had AUC<0.5. At n=55, flatness (0.622) and peak (0.594) WEAKLY FAVOR in-coverage -- they are NOT inverted. So my M1b framing "the substrate is most confident exactly when it is most wrong" was OVERSTATED: it holds for the peak/mean confidence (top1, mean) but NOT for distribution flatness/peakedness. Correcting the record per 10th rule.

### 3. The gap class is n=5 -- a STRUCTURAL ceiling; M4-necessity is directional, not "firm"
Critically: the tuned set has **n_gap=0** (all tuned gold is ingested by construction). The ONLY coverage-gap questions in existence are the 5-6 held-out ones. So:
- I could NOT enlarge the gap class. Both M1b and M1c rest on the SAME ~5 gap questions. "n=55" added in-coverage examples, not gap examples.
- The LOCALIZATION test (does tuned confidence correctly track coverage? -> would validate M4 as precisely-targeted) is **UNTESTABLE** with current data: no gap class in the tuned set to contrast against (tuned top1 AUC=0.500 is the degenerate no-class default, not a measurement).

## Revised input for the USER M4 decision (tempering my prior turn)
- My prior note said "M4-necessity HARD-confirmed." That was too strong. Corrected: **M4-necessity is DIRECTIONALLY supported** -- the gate-relevant top1 confidence is inverted on the available held-out gap questions (n=5), and M1 is genuinely dead -- but the gap class is undersampled (n=5) and the localization hypothesis is currently untestable.
- To make the M4 case ROBUST before a large M4 investment, the cheapest enabler is MORE GAP QUESTIONS: either author more held-out questions on un-ingested topics, OR run a partial ingest then re-author. This is a Testbed/USER ingest-cycle dependency -- which also happens to be Cause-1 work already queued. So the ingest cycle is a precondition for ROBUSTLY justifying M4, not just for closing coverage.
- Net: the evidence ORDER may favor INGEST CYCLE first (closes Cause 1 + enlarges the gap class to robustly test the M4 premise) THEN the M4 investment decision -- rather than committing to M4 now on n=5 gap evidence.

## Discipline note
This is the 10th-rule verify-before-asserting catching MY OWN over-strong M1b claim -- 9th->10th honest correction this session, and the first this session against my own prior-turn framing rather than a fresh mechanism. The direction (M1 dead) is robust; the magnitude/universality and the M4-firmness were over-claimed and are now tempered.

-- EXP-DEV (Prover)
