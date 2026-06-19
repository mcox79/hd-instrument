# Pre-registration: IB phase-transition plateau K-sweep

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_betB_ib_plateau_kswoop_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <10s

## Hypothesis

Candidate (iv) from research_alternative_theoretical_homes_2026-05-24.md (P=0.42):
Wu-Fischer-Tegmark IB phase-transition framework predicts plateau count = number of
corpus class-clusters in joint (X,Y) distribution. Falsifier: vary K (number of
corpus classes) and count detected plateaus; should track K.

## Pre-registered outcomes

**IB_CONSISTENT:** plateau count tracks K for all K in {1..6} AND IB spacing formula
error < 0.10 at K=3. IB framework consistent with Bet B plateau structure.

**IB_INCONSISTENT:** plateau count does not track K even for K <= 3.

**IB_PARTIAL:** tracks K for small K but saturates at large K.

## Data source

Existing per-class retention values from shift_class_predictor_v1.
K-corpus scenarios constructed by subsampling classes.

## Note

This probe uses existing data with constructed K-corpus scenarios; it is a SOFT
falsifier. A decisive IB test requires varying K at experiment design time (new GPU
experiment). This is a cheap feasibility check before commissioning that experiment.
