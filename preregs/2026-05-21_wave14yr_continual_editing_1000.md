# Pre-registration: wave14yr_continual_editing_1000

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yr_continual_editing_1000.py](../experiments/exp_wave14yr_continual_editing_1000.py)
Priority source: extends ym (500-edit stress passed) to 1000 edits
Author: experiment_dev session, pipeline tick 25

## Why

ym showed Kerdock holds at 500 edits. yr tests 1000. At 1000 edits over
M=4096 facts, ~24% of all facts are edited.

## Hypothesis

Kerdock holds 1000 edits.

## Verdict labels

- `CONTINUAL_1000_HOLDS`
- `CONTINUAL_1000_DECAYS_AT_<I>`
- `CONTINUAL_1000_INCONCLUSIVE`

## Operational definition

Reuses yc functions; N_EDITS=1000.

## Expected runtime: 3-7 min
