# Pre-registration: alpha2_codebook_variation_n4096

**Date:** 2026-05-29
**Anchor:** alpha2_codebook_variation_n4096
**Script:** experiments/exp_alpha2_codebook_variation_n4096.py
**Queue:** remote_cpu_queue
**Trigger:** alpha-2 codebook-axis parametric variation (5 codebooks x 3 seeds)

## Hypothesis
Parametric orthogonality variation in codebooks (sparse_ternary at 3 densities,
structured_hadamard, random_gaussian) produces measurable differences in bpc AND
multi-hop accuracy. Codebook orthogonality is a real design parameter.

## Config
- N_FULL = 4096 (PROT-018: _n4096 suffix binding)
- Seeds: [7, 17, 23]
- Codebooks: sparse_d01, sparse_d025, sparse_d05, hadamard, gaussian
- Fixed: beta=8, M_frac=4

## N-suffix
_n4096 suffix; production N = 4096. PROT-018 satisfied.

## Pre-registered bands
- HARD_PASS: bpc_range > 0.30 bits AND multi_hop_range > 0.10 across codebook types.
- HARD_FAIL: bpc_range < 0.05 AND multi_hop_range < 0.02.
- MIDDLE_BAND: only one metric varies.

Calibration probe. "no prior parametric orthogonality sweep anchor."

## Timeout estimate
Per cell: ~30s CPU. 5 codebooks x 3 seeds = 15 cells. Total = 15 * 30 * 1.5 = 675s.
PROT-019 floor 14400s. timeout_s = 14400.

## Smoke result
SELFTEST PASS. bpc_range=0.56 at smoke (above HP threshold). mh_range=0.052 (above HF).
Valid non-null metrics. 3 codebooks tested at smoke scale. Ship allowed.
