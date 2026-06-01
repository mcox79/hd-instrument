# Prereg: retrieval_explainability_counterfactual_probe_smoke_v1

Date: 2026-06-01
Anchor: retrieval_explainability_counterfactual_probe_smoke_v1
Queue: remote_cpu_queue
Script: experiments/exp_retrieval_explainability_counterfactual_probe_smoke_v1.py
Source: research_capabilities_expansion_round3_8_drills_2026-06-01.md Drill 7 M3

## Scientific question

"If atom X is removed from W, how much does retrieval score change?"
Claim: counterfactual score-delta matches per-atom contribution within 5%
relative error.

Algebraic identity: delta_i = s_total - s_without_i = c_i (exact by linearity).

## Design

N=1024, M sweep {64, 128}, 5 trials, 5 atom probes per trial, seed=23.
Pure CPU. No FULL run (smoke IS the test).

## Pre-registered bands

HARD-PASS: counterfactual delta matches c_i within 5% relative error
           in >= 4/5 atom probes per trial, >= 4/5 trials.

HARD-FAIL: error > 20% in majority of probes (n_trials >= 50% fail).

MIDDLE: between HP and HF.

Calibration probe (no prior empirical anchor): bands widened per policy.
Theoretical: relative error ~ float32_eps/|s_total| ~ 0.
HP 5% relative is 50000x more lenient than theory.

## Timeout estimate

Wall < 5s. PROT-019 floor 3600s. timeout_s = 3600.

## PROT-018

No _nN suffix. Production N=1024 stated here per PROT-018 rule 3.

## Middle-band outcome plan

If MIDDLE: investigate whether |s_total| near zero inflates relative error.
Add absolute error fallback gate. Route to Strategy.
