# Prereg — wave14_compositional_holdout_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch for triage-A anchors)
**Routing**: strategy_untested_rows_triage_2026-05-24.md Priority A #1 K6/U8 KILLER T2 (Compositional generalization hold-out probe)
**Script**: `experiments/exp_wave14_compositional_holdout_v1.py`
**Queue**: remote_cpu_queue (CPU; N<=4096; clean Hebbian outer-product test)

## Hypothesis

The substrate uses Hebbian outer-product bindings to associate objects with attributes. If the substrate is COMPOSITIONAL it should generalize from seen (obj, attr) pairs to UNSEEN (obj, attr) compositions because the underlying mechanism is linear in the binding atoms. K6/U8 KILLER T2 asks whether 75%-coverage training is sufficient for the substrate to read out novel held-out compositions at well-above-chance accuracy.

## Design

- N_OBJECTS = 16, N_ATTRS = 16; 256 total compositions
- Training: 192 of 256 (75%) compositions
- Hold-out: 64 of 256 (25%) compositions never seen at training
- W is a Hebbian outer-product W = sum_i attr_i (outer) obj_i with delta rule + decay
- Query: W @ obj_v, score against all 16 attr atoms, pick argmax
- Accuracy: how often the predicted attr matches the ground-truth attr

Parameters: N=4096, EPOCHS=30, SEEDS=[7,17,23,31,41].

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: hold_out_acc >= 0.50 across 5 seeds (chance = 1/16 ~0.0625, so 0.50 = 8x chance). Substrate compositionally generalizes. Substrate-product implication: K6/U8 KILLER closed-PASS; new ✅ row "compositional generalization" opens in cap_map.
- **HARD-FAIL**: hold_out_acc <= 0.10 (within 2x chance). Substrate does NOT compositionally generalize. Substrate-product implication: K6 closed-FAIL.
- **MIDDLE**: 0.10 < hold_out_acc < 0.50. Partial compositional structure but bounded.

## Comparison anchors

- Chance: 1/16 = 0.0625
- Train accuracy: expected ~0.85-1.0 (memorization baseline)

## Self-test

`python experiments/exp_wave14_compositional_holdout_v1.py --self-test` verifies 7 verdict cases.

## Pre-reg routing impact

- HARD-PASS → cap_map v188 NEW ✅ "compositional generalization" row
- HARD-FAIL → cap_map v188 K6/U8 closed-FAIL annotation; substrate is bound-only not compositional
- MIDDLE → annotation; partial structure; routes to higher-N or different binding scheme
