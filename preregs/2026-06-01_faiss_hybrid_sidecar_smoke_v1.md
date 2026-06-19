# Prereg: faiss_hybrid_sidecar_smoke_v1

Date: 2026-06-01
Anchor: faiss_hybrid_sidecar_smoke_v1
Queue: remote_cpu_queue
Script: experiments/exp_faiss_hybrid_sidecar_smoke_v1.py
Source: research_capabilities_expansion_round3_8_drills_2026-06-01.md Drill 4 A5

## Scientific question

Can substrate act as an audit-certificate sidecar alongside FAISS ANN?
(1) recall@10 within 2pp of FAISS-alone baseline?
(2) Audit cert generated per retrieval hit?
(3) p99 cert generation latency <= 50ms?

Note: FAISS mocked as brute-force ANN (no faiss-gpu required for smoke).

## Design

N=256, M=512, n_queries=50, K=10.
Seeds=[17, 23]. Pure CPU.
Expected wall: < 5 min.

## Pre-registered bands

HARD-PASS: recall gap <= 2pp AND cert_per_query >= 1 AND p99 <= 50ms.

HARD-FAIL: recall_hybrid < 80% of baseline OR p99 > 500ms.

MIDDLE: between HP and HF.

Calibration probe (no prior anchor): bands widened per policy.
Theoretical: recall gap = 0.00pp (same ANN); cert latency O(M*N) ~ 0.1ms.
HP 2pp and 50ms are 200x/500x more lenient than theory respectively.

## Timeout estimate

Wall < 5 min. PROT-019 floor 3600s. timeout_s = 3600.

## PROT-018

No _nN suffix. Production N=256 stated here per PROT-018 rule 3.
N=256 chosen for cert latency SLA; M is the primary scaling axis.

## Middle-band outcome plan

If MIDDLE (cert latency > 50ms but <= 500ms): profile whether latency is
O(M) or O(M*N) and set SLA based on empirical curve. Route to Strategy
for eng optimization scope.
