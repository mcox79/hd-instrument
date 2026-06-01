# Prereg: federated_deletion_cert_smoke_v1

Date: 2026-06-01
Anchor: federated_deletion_cert_smoke_v1
Queue: remote_cpu_queue
Script: experiments/exp_federated_deletion_cert_smoke_v1.py
Source: research_capabilities_expansion_round3_8_drills_2026-06-01.md Drill 5 M4

## Scientific question

In a multi-client federated substrate (k=5 clients, M_per_client=30):
(1) Valid deletion cert for client 0 post-write?
(2) Post-deletion retrieval of deleted client drops by >= 50%?
(3) Cross-tenant contamination_rate = 0.0?

Algebraic identity: W_del = W_total - W_c (exact, zero retraining).

## Design

N=1024, k=5 clients, M_per_client=30, seeds=[17, 23, 31].
Pure CPU. Expected wall: ~60s.

## Pre-registered bands

HARD-PASS: cert valid AND cert verified (hash match) AND
           acc_drop_frac >= 0.50 in >= 2/3 seeds AND
           contamination_rate = 0.0 in ALL seeds.

HARD-FAIL: cert invalid OR contamination_rate > 0.05 in any seed.

MIDDLE: cert valid but acc_drop < 0.50 in majority.

Calibration probe (no prior anchor): bands widened per policy.
Theoretical: acc_drop ~ 1.0 (near-complete loss post-deletion).
HP 50% is very conservative. HF contamination > 0.05 is clear failure.

## Timeout estimate

Wall ~60s. PROT-019 floor 3600s. timeout_s = 3600.

## PROT-018

No _nN suffix. Production N=1024 stated here per PROT-018 rule 3.

## Middle-band outcome plan

If MIDDLE (cert valid but acc_drop < 0.50): investigate whether the
remaining signal is from W_c's self-interference (high-M regime). Route
to Strategy: try lower M_per_client or explicit acc_pre baseline check.
