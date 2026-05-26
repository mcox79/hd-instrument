# Pre-registration: wave14yf_continual_editing_v2_stress

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yf_continual_editing_v2_stress.py](../experiments/exp_wave14yf_continual_editing_v2_stress.py)
Priority source: extends [wave14yc_continual_editing_kerdock](../experiments/exp_wave14yc_continual_editing_kerdock.py)
(CONTINUAL_KERDOCK_HOLDS at 30 edits) — stress to 100+ edits
Author: experiment_dev session, pipeline tick 17

## Why

yc showed Kerdock holds 30 sequential edits at 100% accuracy. Production
use is unbounded; the operating envelope question is: at what edit count
(if any) does the Kerdock arm degrade? Per yc's verdict_msg: "30 edits
may not be sufficient load; stress-extend in v2 (100+ edits)."

v2 runs 100 sequential edits and reports the accuracy trajectory.

## Hypothesis

Kerdock arm: min_edited_acc ≥ 0.95 AND min_kept_acc ≥ 0.95 across all 100
edits. Correlated arm: fails by edit 5 (it failed at edit 1 with 30 edits).

## Multi-probe success criteria (per arm)

- min_edited_acc ≥ 0.95
- min_kept_acc ≥ 0.95

## Verdict labels

- `CONTINUAL_V2_KERDOCK_HOLDS_TO_100` — Kerdock passes all 100 edits
- `CONTINUAL_V2_KERDOCK_DECAYS_AT_<I>` — Kerdock cliff at edit I
- `CONTINUAL_V2_BOTH_FAIL_FAST` — both fail by edit 10
- `CONTINUAL_V2_CORRELATED_HOLDS` — correlated unexpectedly passes
- `CONTINUAL_V2_INCONCLUSIVE`

## Pre-mortem

1. Runtime: 100 edits × 2 arms × full M-query each = ~3-5x yc's 21s
   = 60-100s on GPU. Within target.
2. Numerical drift across 100 anti-Hebbian updates: float32 precision
   ~7 digits. With ~100 multiplicative updates, residual drift bounded.
3. Edit indices sampled without replacement: 100 distinct facts edited;
   M=4096 has plenty of unused capacity for this.

## Operational definition

Reuses yc functions; only changes:
- N_EDITS_FULL = 100 (vs yc's 30)
- N_EDITS_SMOKE = 10 (vs yc's 5)

## Expected runtime

- Smoke (N=1024, M=512, 10 edits, 1 seed, 2 arms): ~5-10 s
- Full (N=4096, M=4096, 100 edits, 5 seeds, 2 arms): ~3-6 min on GPU
