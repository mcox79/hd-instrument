# Pre-reg: joint_path_execution_v1_n4096

**Date:** 2026-05-30
**Anchor:** joint_path_execution_v1_n4096 (S14, E6.5 baseline)
**Script:** experiments/exp_joint_path_execution_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Joint vs sequential execution baseline for
multi-path composition.

## Hypothesis

Joint execution (B+D+E in parallel within one process, sharing substrate
state + codebook) achieves >=70% speedup vs sequential AND memory <=2x
AND accuracy preserved (delta <=0.05).

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | mean speedup >=70% AND max mem amp <=2 AND max acc delta <=0.05          |
| HARD_FAIL    | mean speedup <=0 OR max mem amp >=5                                       |
| MIDDLE_BAND  | otherwise                                                                |

## Joint vs sequential

- Sequential: B then D then E (current default).
- Joint: shared W-traversal for Path B; D + E reuse pos/neg path sampling;
  share codebook tensor + relation dict in scope.

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=64 produces seq_total_ns AND joint_total_ns AND
  mem_amp non-null.

## Timeout estimate

5 seeds at fixed config. Per seed ~30s (both seq + joint). ~150s
baseline + GPU compile + memory reset overhead. **timeout_s = 14400**
per user spec.

## Production config

N=4096, M=2048, depth=5, K_paths=500, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
