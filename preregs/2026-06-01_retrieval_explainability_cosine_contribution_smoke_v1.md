# Prereg: retrieval_explainability_cosine_contribution_smoke_v1

Date: 2026-06-01
Anchor: retrieval_explainability_cosine_contribution_smoke_v1
Queue: remote_cpu_queue
Script: experiments/exp_retrieval_explainability_cosine_contribution_smoke_v1.py
Source: research_capabilities_expansion_round3_8_drills_2026-06-01.md Drill 7 M2

## Scientific question

Does the substrate expose per-atom cosine contributions that sum to the total
retrieval score within numerical precision (float32), AND does atom-wise cosine
ranking correlate with retrieval-influence ranking r >= 0.95?

Algebraic identity: s(q,j) = sum_i c_i where c_i = (q.k_i)(v_j.v_i)/N^2.

## Design

N=1024, M sweep {64, 128, 256}, 5 probe queries per M, seed=17.
Pure CPU. No FULL run (smoke IS the test).

## Pre-registered bands

HARD-PASS: per-atom contributions sum to total within tol=1e-4 (float32)
           AND Spearman r(atom_cosine_rank, retrieval_influence) >= 0.95
           in >= 4/5 probe trials per M value.

HARD-FAIL: sum error > 1e-2 OR r < 0.70 in majority of trials.

MIDDLE: between HP and HF.

Calibration probe (no prior empirical anchor): bands widened per policy.
Theoretical prediction: sum error ~ float32_eps * M ~ 1.3e-5 at M=128.
HP tol=1e-4 is 7x theoretical -- generous.

## Timeout estimate

Wall < 10s (algebraic, no training). PROT-019 floor for CPU: 3600s.
timeout_s = 3600.

## PROT-018

No _nN suffix. Production N=1024 stated here per PROT-018 rule 3.
N is not the primary axis; M is.

## Middle-band outcome plan

If MIDDLE: check which M values pass HP and which fail. If only M=256 fails,
cap_map row gains "works at M<=128" annotation. Route to Strategy for
envelope specification.
