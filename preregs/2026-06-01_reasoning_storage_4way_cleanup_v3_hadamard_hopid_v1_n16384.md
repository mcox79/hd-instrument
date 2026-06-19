# Pre-registration: reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384

Date: 2026-06-01
Anchor: reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384
Queue: remote_cpu_queue (CPU)

## Hypothesis

v2 landed BORDERLINE-OVER-CLAIM (mean ratio 2.4pp above random, barely above 2.0pp HP gate).
Research routing identified hop_id codebook orthogonality as the open tuning question.
Hadamard-orthogonal hop codewords guarantee ZERO cross-correlation (vs O(sqrt(N)) for
random BSC), which should close the +0.4pp borderline deficit and achieve mean ratio >= 0.98.

## Configuration

- N = 16384 (PROT-018 binding)
- hop codebook: Hadamard-orthogonal D=10 rows of H_{16384} (entries {-1,+1}, h_i.h_j = 0 exact)
- 3 ablation arms: A (4-way alone), B (cleanup alone), C (4-way + cleanup combined)
- 500 reasoning chains, depth 3-5
- 5 seeds: [7, 17, 23, 31, 41]
- Device: cpu (PROT-022)

## Hadamard construction

H_N[i, j] = (-1)^popcount(i & j). First D=10 rows are exactly orthogonal.
4-way unbinding algebra: h_i^2 = 1 per entry (same as BSC) -> identical BSC algebra,
but cross-correlations h_i.h_j = 0 (exact) vs O(sqrt(N)) for random BSC.

## Single delta vs v2

Only change: hop codebook construction (random BSC -> Hadamard-orthogonal).
All other parameters, arm structure, verdict thresholds identical to v1/v2.

## Pre-registered bands (identical to v1/v2)

Arm C (combined 4-way + cleanup) -- PRIMARY:
  HARD-PASS  : mean structured-key accuracy ratio >= 0.98 (gap < 2%);
               ALL 5 seeds pass; cleanup verification rate >= 0.95.
  HARD-FAIL  : mean ratio < 0.96.
  MIDDLE-BAND: mean ratio 0.96-0.98 (partial closure).

Differential interpretation vs v2:
  If v3 >= HP and v2 was MIDDLE: Hadamard orthogonality was causal for gap closure.
  If v3 remains MIDDLE: gap source is elsewhere (capacity, chain depth, etc).
  If v3 is HF: Hadamard construction introduces interference (unexpected).

## OOM check

Identical to v1/v2. N=16384 W = 1 GB. Remote CPU 64 GB RAM. OK.
Hadamard construction: D x N = 10 x 16384 float32 = 0.6 MB. Trivial overhead.

## Timeout estimate

v2 elapsed ~5 min for 5 seeds. Hadamard adds trivial overhead (one matrix multiply, once).
Same budget as v2: ceil(1.5 * 180) = 270s. PROT-019 floor: 14400s.
timeout_s = 14400.

## N-suffix binding

_n16384: production N = 16384. Script assert N_FULL == 16384.
