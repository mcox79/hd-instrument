# Pre-registration: wave14anneal_selective

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14anneal_selective.py](../experiments/exp_wave14anneal_selective.py)

## Why

wave14z showed GLOBAL anneal destroys everything (factory reset). For GDPR
selective forgetting, need LOCAL anneal: targeted noise on (v_e ⊗ k_e^T)
subspace. Materials analog: laser annealing in semiconductor manufacturing.

## Hypothesis

There exists noise_amp in [0, 5] that gives leak_argmax<=10%, rank>=0.3*n_facts,
norm_ratio<=0.30, cosine<=0.25, kept_recall>=80%, paraphrase_leak<=20% --
ALL multi-probe metrics simultaneously.

## Operational

N=4096, n_facts=400, n_erase=100, rank_L=100, 10 seeds.
Sweep noise_amps {0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0}.

## Expected runtime

Smoke: ~5 sec
Full: ~10-15 min on GPU
