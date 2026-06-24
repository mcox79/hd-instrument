# Pre-reg: substrate_compose_order_x_compose_function_2x2_factorial_v1

filed: 2026-06-23
anchor: substrate_compose_order_x_compose_function_2x2_factorial_v1
script: experiments/exp_substrate_compose_order_x_compose_function_2x2_factorial_v1.py
queue: remote_cpu_queue
routed-from: notes/exp_dev_handoff_research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md

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

## HARD bands (IMMUTABLE; pre-registered before any FULL run)

HARD_PASS: ARM_CANONICAL_SIGMOID beats ALL other 4 arms by >= +0.20 BPC
           AND cv < 0.05 across 3 seeds.
           Taxonomy confirmed; canonical order + sigmoid-add are BOTH load-bearing.
           Sets defaults for all subsequent cells.

CHAIN_GRADE_BONUS: above + ARM_CANONICAL_SIGMOID lifts >= +0.30 BPC vs ARM_VEHICLE
                   (breaks +0.44 BPC envelope at N=4096; chain-grade-eligible).

MIDDLE_BAND: ARM_CANONICAL_SIGMOID wins best-other by +0.05 to +0.20 BPC
             (one axis partially confirmed; interaction ambiguous; route v2 cell).

HARD_FAIL: ARM_CANONICAL_SIGMOID margin <= +0.05 BPC over best-other
           OR all 4 compose arms collapse to vehicle BPC (+/- 0.05).
           Taxonomy axes NOT load-bearing in this regime;
           route to research re-drill with evidence totality note.

cv_max = 0.05 required for HARD_PASS verdict.

## Smoke gate result

smoke_N=512, N_TRAIN=2000, V=200, 1 seed.
EXIT_CODE=0. All 9 self-tests PASS.
All metrics finite and non-sentinel. Script elapsed 8.3s.
Arms differ (SIGMOID arms 5.3134 vs MULT/VEHICLE 5.2988) -- instrument is working.
Smoke effect size is near-zero because N_TRAIN=2000 is insufficient for any substrate signal.
This is expected at smoke scale; NOT INSTRUMENTATION_SUSPECT.
The instrument correctly distinguishes arms (sigmoid vs multiplicative differs even at 2000 tokens).

## N-suffix declaration (PROT-018)

No _nN suffix in anchor name.
Production N = 4096.
Rationale: local_cpu_queue run; N=4096 is this cell's production scale (not the GPU-harness N=8192).

## Timeout estimate

smoke_wall_s = 8.3s
FULL_N / smoke_N = 4096/512 = 8
FULL_seeds / smoke_seeds = 3/1 = 3
scaling_exp = 1.5 (vector operations; HRR FFT + lock-in per arm)
timeout_s = ceil(1.5 * 8.3 * 8^1.5 * 3) = ceil(1.5 * 8.3 * 22.63 * 3) = ceil(845) = 900s

Using 1200s (1.3x safety margin; HRR FFT at N=4096 is faster than scaling_exp=1.5 predicts
but lock-in P=32 carrier phase loop adds O(P * N) = O(32 * 4096) = 131k ops per batch).
Note: well under 7200s (2h) visibility flag.

## WHAT THIS DOES NOT SHOW

- Does NOT test K > 2 modules; only two composed (lockin + HRR context bind)
- Does NOT generalize to word2vec or pretrained encoders (uses char-trigram only)
- Does NOT test composition of all 5 chain-grade primitives
- Effect size may differ at N=8192 (fair-harness baseline scale)
- Does NOT measure GPU utilization (pure numpy, CPU-only)
