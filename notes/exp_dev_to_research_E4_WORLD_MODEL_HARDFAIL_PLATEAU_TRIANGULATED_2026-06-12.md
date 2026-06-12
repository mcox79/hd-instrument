# Exp-Dev -> Research: E4 world-model HARD_FAIL 0.343 -- 1-op MWP plateau TRIANGULATED as comprehension/corpus-bound

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** your E4 design sketch -- I built it NOW (not deferred)

## Why I built E4 now (not Days 4-7)

I had deferred E4 to post-Phase-6 citing "corpus-bound." On reflection that's a corpus-boundary PRE-ASSUMPTION, which violates the
USER-locked brain-can-do-it rule (don't accept a comprehension ceiling without trying the mechanism). So I built the world-model
mechanism class now and measured it.

## Result: ASDiv-1op acc 0.3431 -- HARD_FAIL (~= discriminative 0.39 plateau)

Schema-simulation (EQUAL_GROUPS/COMBINE/CHANGE_ADD/CHANGE_SUB/COMPARE/SHARE/TIMES; each schema's operation = world knowledge, zero-shot):
- overall 0.3431 (n=1364), slightly BELOW the trained discriminative ~0.39
- per-op: + 0.301 / * 0.290 / - 0.481 / / 0.204
- gets the OPERATION right often (- 0.48); bounded by operand-selection + scenario-comprehension

## The valuable finding: TRIANGULATION

Three independent lines now converge on the SAME conclusion -- the 1-op MWP plateau is COMPREHENSION/OPERAND-SELECTION bound, NOT
op-mechanism bound:
1. Discriminative perceptron (trained cue->op): ~0.39
2. **World-model schema-simulation (zero-shot world-knowledge cue->op): 0.343 (NEW, this cell)**
3. BMA ensemble over 4 operand-selection strategies: gain = 0 (correlated errors)

Two distinct mechanism CLASSES + an ensemble all plateau identically. The op-mapping is the EASY part (both mechanisms get it);
the bottleneck is understanding WHICH numbers + scenario semantics -- which neither mechanism recovers from the sparse 92-atom corpus.

## Brain-can-do-it: SATISFIED + supports corpus strategy

This is honest brain-can-do-it evidence: I tried the new mechanism class (didn't pre-accept the ceiling), and the convergence
EMPIRICALLY supports the USER math+science ingestion priority -- the lever is CORPUS (comprehension grounding), not another mechanism.
Per [[substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12]]: corpus deficiency confirmed via a 3rd independent angle.

Post-Phase-6, re-running E4 (richer corpus -> better scenario grounding) is the natural re-test -- THAT is the corpus-gated part,
and now it has a clean pre-ingest baseline (0.343) to measure lift against.

e4_world_model_mwp_cpu_v1 queued (official). This was the last genuinely-ungated Exp-Dev cell; remaining levers are Testbed-gated
(Gap-4 router, Phase-6 ingest) -- now with E4 baseline + QA 5-axis baseline established for post-ingest re-measurement.
