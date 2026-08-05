# Pre-reg: forward_projection_affect_isolate_v1 (C-D part 2)

Date: 2026-08-05
Author: hdi_exp_dev
Cell: experiments/exp_forward_projection_affect_isolate_v1.py
Metrics: data/exp_forward_projection_affect_isolate_v1/metrics.json
Runner: LOCAL, in-process, no origin push.

## Goal
Add the PREDICTION / FORWARD-PROJECTION step to the situation-model affect layer: from the
maintained per-entity affect/situation state up to clause t, generate a FORWARD valence expectation
for the UNSTATED outcome, via hdlab/predictive_coding. Prove it with the ISOLATE-PREDICTION gate:
a STATIC no-projection arm MUST FAIL forward-expectation items while the predictive arm passes.

## Motivation
C-D part 1 (exp_maintained_affect_grounded_narrative_v1) maintains a PRESENT-STATE grounded affect
trajectory. Its documented miss is grapp_irony_005 (Tom Sawyer fake-deathbed): the window contains
the deception SETUP (supporting_span 1772-1777, "he wished he was sick ... stay home from school ...
No ailment was found, and he investigated again") but NO present-tense HARM event -> grounded_state
=NA -> POS (WRONG). The negative valence is a FORWARD EXPECTATION to an unstated outcome. Brain
(Kuperberg&Jaeger predictive coding): valence is PRE-ACTIVATED before the next clause.

## Mechanism (REUSE, not rebuild)
hdlab/predictive_coding (Rao-Ballard residual-gated associative memory): a learned transition map W
from a situation-state key (present grounded-affect features from C-D part 1 + recent-setup cue
features over a 60-line window) to an outcome-valence codeword {NEG_CODE, POS_CODE}. Trained on a
DISJOINT, balanced, glass-box per-feature episode grid (armc.build_arm_c_training_episodes pattern;
never reads gold). predict(W, state_key) projects the expected forward valence. Integration is a
brain-faithful GAP-FILLER: the projection supplies valence ONLY when the present-state maintainer is
silent (grounded_state==NA and static reads POS); a present determination always dominates.

DEFLATION (declared): the setup->outcome KNOWLEDGE is SUPPLIED via the training grid. This is an
ARCHITECTURE/MECHANISM proof (associative forward-projection recovers a forward-only item a static
maintainer provably cannot), NOT a data-discovery result. 2/3 forward-NEG items are SYNTHETIC;
grapp_irony_005 is the only real-corpus forward anchor (N=1 real).

## Arms
- STATIC = C-D part 1 present-state grounded reader (grounded_pred). No forward projection.
- FORWARD = STATIC + predictive_coding gap-filler (override POS->NEG only when NA + projection NEG).

## Item sets
- FORWARD-NEG isolate set (true=NEG, forward-only): grapp_irony_005 (real) + synth_fwd_neg_1/2.
- FORWARD-POS controls (true=POS, benign anticipation): synth_fwd_pos_1/2 (constant-NEG guard).
- REGRESSION set: all 10 real grapp items (FORWARD must not break STATIC-correct items).

## Pre-registered bands
- HARD_PASS: FORWARD recovers >=2/3 forward-NEG incl irony_005 AND STATIC fails them (isolate gap
  >= 15pt) AND scramble-future collapses the gain AND POS-guard holds AND predictive_coding
  non-degenerate AND leak-clean AND no regression break.
- PARTIAL_ISOLATE_PROVEN_REGRESSION_FP: isolate gate all pass, but FORWARD false-fires on real
  present-correct items (lexical setup detector too noisy) -> missing-component flag.
- PARTIAL: predictive helps + recovers irony_005 but a band condition (scramble/gap/2of3) missed.
- HARD_FAIL_NO_PROJECTION: predictive degenerate OR no better than static.

## Controls
- SCRAMBLE-FUTURE: random-relabel training outcomes over 64 seeds; mean forward-NEG accuracy must
  collapse toward chance (>=0.25 below the real projector) -> proves real forward structure used.
- POS-guard: benign-anticipation forward items must stay POS under FORWARD (no constant-NEG).
- Leakage: setup window must not contain an explicit outcome-valence label (LEAK_TOKENS check).
- Degeneracy: predict() must differentiate a NEG-cue key (->NEG) from a benign key (->POS) with
  margin > 0.02 (guards the applied_frac=0.9996 pass-through failure class).

## Result (MEASURED 2026-08-05)
VERDICT = PARTIAL_ISOLATE_PROVEN_REGRESSION_FP.
- forward-NEG predictive 3/3 vs STATIC 0/3 (isolate gap 100pt); irony_005 recovered (True).
- scramble collapsed: mean 0.47 (chance) vs real 1.00 over 64 seeds.
- POS-guard True; predictive non-degenerate (neg-probe margin 0.973, applied_frac 1.0); leak-clean.
- Regression: 2/10 real items broken (grapp_sincere_003, grapp_sincere_004) -- both NA-state where
  the lexical setup detector false-fired NEG cues. Missing component: a grounded intent/deception
  detector (the same fix pattern C-D part 1 applied to present-state) -> C-D part 3.
