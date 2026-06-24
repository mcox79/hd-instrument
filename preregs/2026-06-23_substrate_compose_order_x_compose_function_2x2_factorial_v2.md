# Pre-reg: substrate_compose_order_x_compose_function_2x2_factorial_v2

filed: 2026-06-23
anchor: substrate_compose_order_x_compose_function_2x2_factorial_v2
script: experiments/exp_substrate_compose_order_x_compose_function_2x2_factorial_v2.py
queue: remote_cpu_queue
rescue-of: substrate_compose_order_x_compose_function_2x2_factorial_v1
rescue-reason: v1 timed out at 1200s wall (hit timeout before completing all 3 seeds at full scale)

## Scientific question

Does the INTERACTION of (compose order) x (compose function) discriminate arms as
the taxonomy predicts? Specifically: does CANONICAL ORDER + SIGMOIDAL_ADDITIVE_HETEROGENEOUS
beat ALL other factorial cells by >= +0.20 BPC, confirming BOTH axes are load-bearing?

## Design

2x2 factorial: 4 arms + 1 vehicle = 5 arms total.
N=4096, V=4000, N_TRAIN=100k text8 tokens, N_HELD=20k, 3 seeds.
Pure numpy; no GPU required. char-trigram encoder (no gensim dependency).

AXIS_1 (compose ORDER):
  CANONICAL: sparse-encode FIRST -> HRR bind context -> read
  REVERSED: HRR bind context on DENSE embed FIRST -> sparse-encode AFTER

AXIS_2 (compose FUNCTION):
  MULTIPLICATIVE_SHARED_TARGET: two separate W matrices on same E_sparse target,
    log-linear combined (= product of probs; shared target = rank-1 by Levy-Horn-Ruppin)
  SIGMOIDAL_ADDITIVE_HETEROGENEOUS: sigmoid(alpha*hrr_keys + beta*lockin_keys) gated
    combined key -> single W -> single readout; additive saturation + heterogeneous inputs

## HARD bands (IMMUTABLE; pre-registered before any FULL run; same as v1)

HARD_PASS: ARM_CANONICAL_SIGMOID beats ALL other 4 arms by >= +0.20 BPC
           AND cv < 0.05 across 3 seeds.
           Taxonomy confirmed; canonical order + sigmoid-add are BOTH load-bearing.
           Sets defaults for all subsequent cells.

CHAIN_GRADE_BONUS: above + ARM_CANONICAL_SIGMOID lifts >= +0.30 BPC vs ARM_VEHICLE
                   (breaks +0.44 BPC envelope at N=4096; chain-grade-eligible).

MIDDLE_BAND: ARM_CANONICAL_SIGMOID wins best-other by +0.05 to +0.20 BPC
             (one axis partially confirmed; interaction ambiguous; route v3 cell).

HARD_FAIL: ARM_CANONICAL_SIGMOID margin <= +0.05 BPC over best-other
           OR all 4 compose arms collapse to vehicle BPC (+/- 0.05).
           Taxonomy axes NOT load-bearing in this regime;
           route to research re-drill with evidence totality note.

cv_max = 0.05 required for HARD_PASS verdict.

## Smoke gate result (v2)

smoke_N=512, N_TRAIN=2000, V=200, 1 seed.
EXIT_CODE=0. All 9 self-tests PASS.
All metrics finite and non-sentinel.
Script elapsed 1.4s (wall, laptop; includes all 9 self-tests).
Arms differ: sigmoid arms 5.3134 vs vehicle/mult 5.2988 -- instrument distinguishes arms.
Smoke HARD_FAIL is expected (N_TRAIN=2000 is insufficient signal at any N_DIM).
This is documented in v1 prereg and confirmed expected behavior.
NOT INSTRUMENTATION_SUSPECT.

Multi-scale check (4x N_DIM=2048): vectorized sparsify + HRR bind validated at 4x scale.
No overflow or OOM pattern at intermediate scale.

## N-suffix declaration (PROT-018)

No _nN suffix in anchor name.
Production N = 4096.
Rationale: remote_cpu_queue run; N=4096 is this cell's production scale
(not the GPU-harness N=8192 baseline scale).

## Performance optimizations vs v1

1. Vectorized sparsify_bipolar: numpy batch argpartition over all rows simultaneously
   instead of Python for-loop over V rows. At V=4000, N_DIM=4096: ~50-100x faster.

2. Vectorized REVERSED key building: same batch argpartition pattern replaces
   Python for-loop over n_eval ~10k rows. At n_eval=10k, N_DIM=4096: ~50-100x faster.

3. Vectorized build_reversed_src_keys: same pattern for N_TRAIN=100k rows.

These optimizations do NOT change the mathematical computation, only the
execution speed. Results are identical to v1 at identical scale.

## Timeout estimate

v1 timed out at 1200s wall (full scale, remote_cpu_queue).
v2 uses timeout=3600s (3x v1 timeout = reasonable engineering multiple).

Analytical estimate:
  Dominant op: build_rank1_W = O(N_TRAIN * N_DIM^2).
  At N_DIM=4096, N_TRAIN=100k, 7-8 W matrices, 3 seeds:
  ~400-600s total for W builds + logit computations.
  3600s provides ~6x safety margin over analytical estimate.
  Well under 14400s (4h) cap.

## WHAT THIS DOES NOT SHOW

- Does NOT test K > 2 modules; only two composed (lockin + HRR context bind)
- Does NOT generalize to word2vec or pretrained encoders (uses char-trigram only)
- Does NOT test composition of all 5 chain-grade primitives
- Effect size may differ at N=8192 (fair-harness baseline scale)
- Does NOT measure GPU utilization (pure numpy, CPU-only)
