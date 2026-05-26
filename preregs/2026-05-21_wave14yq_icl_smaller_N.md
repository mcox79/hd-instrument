# Pre-registration: wave14yq_icl_smaller_N

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yq_icl_smaller_N.py](../experiments/exp_wave14yq_icl_smaller_N.py)
Priority source: extends ICL Bet 1 to N=2048 to characterize the
N-dependence of ICL saturation
Author: experiment_dev session, pipeline tick 24

## Why

yw (wave14w_icl_extended) showed SOFT_SATURATION at N=4096 with ICTX up
to 65536. yq tests at N=2048 — does the saturation point scale with N?
If substrate width is the bottleneck for ICL, smaller N saturates earlier.

## Hypothesis

At N=2048, ICTX in {1024, 4096, 16384, 32768}: ICL saturates at ICTX
proportional to N (so ICTX=8192 or so).

## Verdict labels (mirror yw)

- `ICL_SMALLER_N_NO_SATURATION`
- `ICL_SMALLER_N_SOFT_SATURATION`
- `ICL_SMALLER_N_SATURATION_AT_<I>`
- `ICL_SMALLER_N_DECAY_AT_HIGH_ICTX`
- `ICL_SMALLER_N_POOL_COLLAPSE_AT_<I>`
- `ICL_SMALLER_N_CORPUS_TOO_SMALL`
- `ICL_SMALLER_N_INCONCLUSIVE`

## Operational definition

Reuses v3/yw infrastructure. N=2048, ICTX in {1024, 4096, 16384, 32768},
3 seeds. Verdict logic copied from yw.

## Expected runtime: 3-7 min
