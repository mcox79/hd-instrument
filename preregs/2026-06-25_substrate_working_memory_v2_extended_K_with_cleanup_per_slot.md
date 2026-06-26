# Pre-registration: substrate_working_memory_v2_extended_K_with_cleanup_per_slot

**Date:** 2026-06-25
**Anchor:** substrate_working_memory_v2_extended_K_with_cleanup_per_slot
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [11, 13, 19]

## Why this cell exists

Research drill 2026-06-25 EXT-6: working memory K>32 with cleanup-per-slot.

The WM-HRR-slots PRODUCTION cell (`exp_working_memory_hrr_slots_PRODUCTION_v1`)
is chain-grade at K=32 sigma=1.0 (recall 1.000); degrades at K=128 (0.95) and
K=256 (0.64). Production WM needs K > 32 reliably. P=0.65 per Research drill.

## Mechanism

Compare two ARMs at the same N=4096, codebook=512, sigma sweep [0.0, 0.5, 1.0]:

- **ARM_NAIVE** (current PRODUCTION):
  - Write: workspace = sum_i bind(item_i, slot_tag_i) (bipolar elementwise)
  - Read: r = noisy_workspace * slot_tag_i; argmax against codebook

- **ARM_CLEANUP_PER_SLOT** (new mechanism):
  - Same write
  - Read: r1 = noisy_workspace * slot_tag_i; argmax against codebook to find
    candidate atom; mix r1 toward candidate (0.5/0.5); re-quantize bipolar;
    final argmax cleanup. This is one extra iterated-cleanup pass at READ time
    (brain analog: theta-gamma double cleanup; substrate's bipolar
    quantization concentrates toward codebook attractor).

K-sweep: {32 (rail), 64, 128, 256, 512} sigma-sweep {0.0, 0.5, 1.0}.
200 items per (K, sigma, arm, seed) -> ceil(200/K) trials, each with K distinct
items drawn without replacement.

## Scientific question

Does adding one iterated-cleanup pass at READ time lift the K-ceiling of
the HRR-slot WM primitive from K=32 to K>=128 at sigma=1.0?

## Pre-registered bands

**HARD_PASS_CLEANUP_LIFTS_K_TO_128:**
- ARM_CLEANUP_PER_SLOT recall at K=128, sigma=1.0 >= 0.95
- AND cv <= 0.07 across seeds
  (chain-grade WM primitive holding ~16x Miller capacity at meaningful noise)

**CHAIN_GRADE_K_EXTENSION_X (subordinate to HP):**
- ARM_CLEANUP_PER_SLOT lifts K-ceiling by 2x or more
  (CLEANUP K-ceiling at sigma=1.0 >= 2 * NAIVE K-ceiling)

**MIDDLE_BAND:**
- ARM_CLEANUP_PER_SLOT recall at K=128 sigma=1.0 in [0.80, 0.95)
  (some lift but not chain-grade)

**HARD_FAIL_NAIVE_IS_OPTIMAL:**
- ARM_CLEANUP_PER_SLOT <= ARM_NAIVE at K=128 sigma=1.0
  (extra cleanup doesn't help; NAIVE is at K-ceiling intrinsically)

**SANITY (selftest):**
- K=2 sigma=0.0 both arms recall = 1.0

## Calibration rationale

- 0.95 floor at K=128 sigma=1.0 because PRODUCTION cell already shows NAIVE
  at 0.95 at K=128 (per WM-HRR-slots-PRODUCTION_v1 results). The chain-grade
  bar is for CLEANUP to either match (K=128 still works under iterated
  cleanup) or extend (K=256 holds at 0.95 with cleanup).
- cv <= 0.07 because substrate is deterministic per-seed; cross-seed
  variability above 7% indicates seed-dependent codebook crosstalk.
- MIDDLE_BAND [0.80, 0.95) catches partial lift; below 0.80 = cleanup
  actively confuses the readout (HARD_FAIL).

## Q-discipline (BIAS-Q: suspect 1.000 results)

K=32 sigma=0.0 should produce 1.000 by construction; verify by inspecting
per-seed and per-K-per-sigma values; this is expected saturation. The
load-bearing measurement is K=128 sigma=1.0 (not saturated by construction).

## Capacity-feasibility analysis

- HRR-superposition K bound items in N=4096; crosstalk SNR ~ sqrt(N/(K-1)).
  K=128 -> SNR ~ 5.7. K=256 -> SNR ~ 4.0. K=512 -> SNR ~ 2.8.
- Cleanup against 512-atom codebook needs SNR above codebook crosstalk
  (sqrt(N) = 64 -> ~7 sigma; codebook intra-crosstalk between random bipolar
  atoms is sqrt(N)). K=128 has SNR 5.7 / 6.4 ~ 0.9 (marginal); cleanup-per-
  slot iterated step is the additional lift expected to push it above the
  threshold.
- K=256 has SNR 4.0 / 6.4 ~ 0.6 (sub-threshold); cleanup-per-slot may
  rescue if the codebook attractor concentration is strong enough.

Capacity feasible; iterated cleanup is the load-bearing mechanism.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; PROT-018 does not apply.

## Timeout estimate

Smoke ~ 60s estimated at N=4096, 1 seed, K_VALUES=[32, 64, 128],
SIGMAS=[0.0, 0.5, 1.0], 50 items per K, 2 arms.
FULL: N=4096, 3 seeds, K=[32, 64, 128, 256, 512], 200 items per K, 2 arms.
Scaling: dominated by K * codebook_size cleanup; scaling_exp = 1.5.
formula: ceil(1.5 * 60 * (512/128)^1.5 * (3/1) * 2_arms)
       = ceil(1.5 * 60 * 8 * 3 * 2) = 4320s
budget timeout_s = 4500 (1.25 h).
timeout_s = 4500

## Provenance rail

ARM_NAIVE at K=32 sigma=1.0 must reproduce WM-HRR-slots-PRODUCTION_v1's
recall (within +/- 0.05 of 1.000). If breaches, raises method-skew flag
(but does not auto-fail the verdict since the regime is documented).

## META_M6 baseline derivation

NAIVE baseline is derived from CURRENT cell's regime (not copied from prior).
Each seed runs both arms with the SAME codebook + slot tags + item draws;
the only difference is the read-time cleanup step.
