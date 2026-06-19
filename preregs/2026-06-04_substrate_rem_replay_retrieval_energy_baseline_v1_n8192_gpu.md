# Prereg: substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu

## Anchor
substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu

## Routing
notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1c. Routed to
the owned GPU (N=8192 NxN Hopfield matmuls; keeps GPU occupied per user directive).

## Scientific question
Does Crick-Mitchison (1983) REM unlearning consolidate substrate memory (reduce retrieval energy) at
N>=8192, and is it CONDITIONAL on N (null at N=4096, below the bipolar quantization floor)? Auto-assoc
Hopfield (diagonal-zeroed), alpha=0.12, energy = 1 - overlap(xi, sign(W xi)). Replay = R*=10 cycles of
TOPK=20 random probes settled to spurious attractors then unlearned (W -= lambda/N outer(S,S)). 5 seeds.
Cells: A N=8192 no-replay; B N=8192 replay; C N=4096 replay (control).

## Pre-registered bands (reduction% = (e_init - e_final)/e_init * 100)
HARD-PASS: Cell B reduction > 30% AND Cell C reduction < 10% (N>=8192 conditional confirmed).
MIDDLE: Cell B in [10,30]% OR Cell C also > 10% (conditional unclear).
HARD-FAIL: no cell reduces > 10% (replay does not consolidate).

## Formula self-tests (PROT-022)
1. single-pattern perfect recall (energy~0). 2. energy in [0,2]. 3. unlearning step modifies W.
NOTE: self-test asserts MECHANICS only, NOT that replay reduces energy (that is the empirical question).
[ALL PASS]

## Smoke gate
Smoke PASSED (N=1024/2048, 2 seeds): unlearning reduces energy (B 75-78%, C 94-96%); control not null at
tiny N (-> MIDDLE, correctly). The N=8192-vs-N=4096 conditional is the full-scale empirical question.

## PROT-018 / 019 / 021
_n8192 -> headline cells N=8192 (control C=4096 by design). timeout floor 21600s. 5 seeds.

## Queue
overnight_queue (GPU).
