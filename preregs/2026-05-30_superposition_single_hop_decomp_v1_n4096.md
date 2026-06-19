# Pre-registration: superposition_single_hop_decomp_v1_n4096

Date: 2026-05-30
Anchor: superposition_single_hop_decomp_v1_n4096
Track: A (parallel multi-hop) Phase 1 of 3 (single-hop superposition gate)
Script: experiments/exp_superposition_single_hop_decomp_v1_n4096.py
Queue: overnight_queue (GPU)
Timeout: 21600s (PROT-019 _n4096 floor + headroom for 40 cell-seeds)
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding contract)

## Scientific question

Given K facts (k_i, v_i) stored in a substrate W, form a superposition query
q = sum_i beta_i k_i with known coefficients beta_i. The raw substrate
response r = W q is then decomposed in the codebook basis:
  alpha_c = <r, c> / N   for each codeword c.
Does the ranking and magnitude of alpha_c isolate the K stored components
from the C-K spurious codewords cleanly enough to enable parallel multi-hop
operations downstream?

## Decision context (msg 1 staging)

Per user's msg 1 staging: this single-hop test is the single most decisive
of the multi-hop tests. If single-hop superposition decomposition does not
work, multi-hop superposition cannot work. HARD_PASS -> ship T1 P2 (two-hop
superposition). HARD_FAIL -> coherent multi-hop closes for the substrate;
LLM-orchestration remains the only multi-hop path (user-stated fallback).
MIDDLE_BAND -> drill into which patterns fail and which work.

## Design

- N=4096, BSC-equivalent Kerdock_4coset codebook (PROT-018 binding;
  consistent with phase-region batch, Track-A/B siblings).
- K=10 main test (matches msg 1 spec).
- 4 beta patterns:
  - P1 uniform: all beta_i = 1/K
  - P2 peaked:  one beta_i = 1.0, rest = 0.1
  - P3 random:  beta_i ~ U(0,1), normalized so sum_i beta_i = 1
  - P4 sparse:  3 of K beta_i = 1/3, rest = 0
- 5 seeds: [7, 17, 23, 31, 41]
- Main: 4 patterns x 5 seeds = 20 cell-seeds at K=10.
- K-scaling sub-test (P1 uniform only): K in [5, 10, 15, 20] x 5 seeds
  = 20 additional cell-seeds.
- Total expected at FULL: 40 cell-seeds.

## Metrics (per cell)

1. per_component_accuracy: fraction of stored value indices i where
   |alpha_{v_i} - beta_i| / ||r|| < 0.1.  Range [0, 1].
2. cross_talk: max |alpha_c| over codewords c NOT in stored value set,
   normalized by mean |alpha_{v_i}| over stored value indices.  Range [0, inf).
3. decomp_correlation: cos(reconstructed_r_from_top_K_alphas, r).  Range [-1, 1].

## Pre-registered bands

HARD_PASS:
  per_component_accuracy >= 0.90
  AND cross_talk <= 0.10
  AND >= 3/5 seeds satisfying both clauses
  in ALL 4 patterns at K=10
  AND linear K-scaling (max(per_component_accuracy) - min over K in [5,10,15,20] <= 0.15).

HARD_FAIL:
  per_component_accuracy <= 0.50 OR cross_talk >= 0.30
  in >= 50% of main cells.

MIDDLE_BAND:
  Anything else. Partial signal: some patterns or K-values work; others don't.

## Formula self-tests (verified in `_instrumentation_selftest`)

1. N == 4096 (PROT-018 binding).
2. main count = 4 patterns x 5 seeds = 20.
3. kscale count = 4 K-values x 5 seeds = 20.
4. Total = 40 cell-seeds at FULL.
5. P1 betas sum to 1.0 (uniform); P3 normalized to 1.0; P4 sparse sums to 1.0.
6. Kerdock codeword auto-norm: <k_i, k_i>/N = 1 (unit-norm rows from v3 generator).
7. Verdict gates: HARD_PASS fixture (all patterns 5/5 + K-scaling tight),
   HARD_FAIL fixture (all HF), MIDDLE_BAND fixture (mixed) all classify
   correctly via `compute_verdict`.

## Smoke result (CPU, N=1024, 2 patterns x 1 seed + 2 K-values x 1 seed)

  main_P1_uniform_K10_seed17:  per_comp_acc=1.000  cross_talk=0.283  decomp_corr=0.993
  main_P2_peaked_K10_seed17:   per_comp_acc=1.000  cross_talk=0.303  decomp_corr=0.989
  kscale_P1_uniform_K5_seed17: per_comp_acc=1.000  cross_talk=0.123
  kscale_P1_uniform_K10_seed17: per_comp_acc=1.000 cross_talk=0.283

  smoke wall: 0.38s (CPU). Verdict: SUP_DEC_HARD_FAIL because cross_talk
  exceeds the HP threshold (0.10) at N=1024. Per-component accuracy is
  perfect; cross_talk is the borderline metric.

  Theoretical expectation: cross_talk scales as 1/sqrt(C); codebook
  C ~ N^2/log2(N), so at N=4096 vs N=1024, expect ~2x improvement in
  cross_talk (smoke 0.28 -> FULL ~0.14). Still possibly over HP_CROSSTALK_MAX
  but in MIDDLE_BAND range. PROCEEDING TO SHIP per gate-test mandate; the
  FULL outcome IS the answer to "does single-hop superposition work at
  production scale".

## OOM check

W: N*N*4 = 64MB. Codebook: C*N*4 = O(N^3 / log2 N * 4) -> ~256MB at N=4096.
K facts (max 20) keys + values: <2MB. Total < 1GB. Well under 6GB ceiling.

## Timeout estimate

smoke_wall_s = 0.38 (CPU, 4 cell-seeds smoke).
FULL has 40 cell-seeds (10x), N=4096 vs N=1024 (4x). Matrix ops are
N^2 dominant; scaling_exp = 1.5.
  ceil(1.5 * 0.38 * 4^1.5 * 10) = ceil(1.5 * 0.38 * 8 * 10) = ceil(45.6) = 46s CPU
GPU is ~50-200x faster on these matmuls; expected GPU wall < 60s typical.

User-specified timeout: 21600s (6h). Generous; satisfies PROT-019 _n4096
floor (14400s) with margin for tail-latency and OOM-recovery retry of cells.

## Outcome handlers (post-verdict)

- HARD_PASS -> file strategy_request_to_exp_dev for T1 P2 (two-hop
  superposition); cap_map row "parallel multi-hop" advanced.
- HARD_FAIL -> close Track-A; cap_map row marked X with the specific failure
  mode (per_component_acc fail OR cross_talk fail).
- MIDDLE_BAND -> diagnostic: which patterns pass / fail; ship rescue
  variant (e.g., codebook-tuned cross_talk reduction) before deciding.
