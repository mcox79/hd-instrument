# Failure Diagnosis: a4_audit_during_training_v1
**Date:** 2026-06-02  
**Exit code:** null (KILLED by timeout at 120s)  
**Queue:** remote_cpu_queue  

## Root cause
Script is pure numpy CPU. 20 baseline runs each building an N=1024 outer-product accumulation matrix (1M element NxN float32). No GPU. Routed to remote_cpu_queue. Killed by 120s timeout; exit_code=null = runner-level SIGKILL.

## Evidence
- Script has no torch.cuda calls; numpy-only.
- N_BASELINE_RUNS=20; each run: ~N^2 outer product ops at N=1024.
- Elapsed exactly 120s = runner timeout wall.

## Remedy options (for Strategy)
1. GPU port: move kappa_3 parallel monitor to GPU; expected <5s at N=1024.
2. Reduce N_BASELINE_RUNS from 20 to 3-5 for proof-of-concept.
3. Increase timeout to 600s if the CPU run is scientifically needed.

## Routing
Strategy: decide if A4 kappa_3 parallel monitor is still needed after wave4/wave5 COMBO audits. If yes, request GPU port or timeout increase. Not re-shipped in Cycle 11.
