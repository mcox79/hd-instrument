# Pre-registration: wave14yj_continual_editing_v3_200

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yj_continual_editing_v3_200.py](../experiments/exp_wave14yj_continual_editing_v3_200.py)
Priority source: extends [wave14yf_continual_editing_v2_stress](../experiments/exp_wave14yf_continual_editing_v2_stress.py)
to 200 edits — find Kerdock's actual cliff if any
Author: experiment_dev session, pipeline tick 20

## Why

yc: 30 edits, Kerdock HOLDS. yf: 100 edits in flight. yj: 200 edits.
Each successive stress level either confirms Kerdock's robustness or
finds the cliff.

## Hypothesis

Kerdock arm holds 200 edits at >= 0.95 acc; correlated fails by edit 5.

## Verdict labels

- `CONTINUAL_V3_HOLDS_TO_200`
- `CONTINUAL_V3_DECAYS_AT_<I>`
- `CONTINUAL_V3_BOTH_FAIL`
- `CONTINUAL_V3_INCONCLUSIVE`

## Operational definition

Reuses yc/yf functions; only change: N_EDITS = 200.

## Expected runtime

- Smoke (10 edits, 1 seed): ~5 s
- Full (200 edits, 5 seeds, 2 arms): ~6-10 min on GPU
