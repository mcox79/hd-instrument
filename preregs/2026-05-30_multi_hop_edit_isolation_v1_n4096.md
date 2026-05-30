# Pre-reg: multi_hop_edit_isolation_v1_n4096

**Date:** 2026-05-30
**Anchor:** multi_hop_edit_isolation_v1_n4096 (S6, E3.2)
**Script:** experiments/exp_multi_hop_edit_isolation_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Edit-isolation killer feature must extend to
multi-hop ops for agentic deployment.

## Hypothesis

Under concurrent edits at rate=100/sec, all 3 paths maintain >=85%
accuracy on non-edited paths AND audit chain stays valid AND results
are consistent (pre-edit OR post-edit, not mixed).

## Pre-registered bands

| Outcome      | Condition                                                                  |
|--------------|----------------------------------------------------------------------------|
| HARD_PASS    | At rate=100, >=3/5 seeds have B/D/E >=85% + audit valid + consistent       |
| HARD_FAIL    | Any path <50% at rate=100 OR audit chain corrupts (audit_pre == audit_post when edits applied) |
| MIDDLE_BAND  | otherwise                                                                  |

## Self-test

- N == 4096 (PROT-018).
- audit_pre and audit_post computed via SHA-256 of W bytes.
- 3 patterns (on_path, off_path, mixed) all exercised at smoke.

## Audit-chain semantics

For off_path edits: pre and post accuracies should be approximately equal
(< 0.15 delta). For on_path / mixed edits: edited keys' responses CHANGE,
so pre != post is expected (consistent = True by construction).

## Timeout estimate

3 rates x 3 patterns x 5 seeds = 45 cells. Per cell ~4 measurements
(pre/post acc for 3 paths). ~6s/cell on GPU. ~270s baseline + GPU
compile + edit-apply overhead. **timeout_s = 21600** per user spec.

## Production config

N=4096, M=2048, depth=5, K_paths=100, rates=[10,100,1000],
patterns=[on_path, off_path, mixed], seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
