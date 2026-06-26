# Pre-registration: substrate_working_memory_frequency_multiplexed_lock_in_v1

**Date:** 2026-06-25
**Anchor:** substrate_working_memory_frequency_multiplexed_lock_in_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [11, 13, 19], **K:** {32, 64, 128, 256}

## Why this cell exists

USER directly proposed this mechanism (verbatim Q3 2026-06-25): "if each
marker was in a different frequency and you used filters, you'd be able
to read a lot more than 32. And, if you flashed them at different
frequencies (lock-in) you'd also get way, way more"

The substrate's WM-HRR-slots PRODUCTION cell chain-grades at K=32 sigma=1.0
(recall 1.000) but degrades to ~0.95 at K=128 and ~0.55 at K=256 (today's
WM v2 cell). Adding cleanup-per-slot lifted K=128 only 0.014 (NAIVE 0.908
-> CLEANUP 0.922) -- the bind+bundle capacity is the bottleneck.

## Brain analog (load-bearing)

Theta-gamma multiplexing in PFC (Lisman-Buzsaki theory): each WM item is
bound to a different gamma sub-cycle within a theta cycle; read via gamma-
frequency-selective lock-in-style filter. The substrate has the chain-grade
lock-in amplifier primitive (HARD_PASS lock_in_amplifier_hd_frequency_v1_FULL
at sigma=64 -> 16.39x SNR lift with cv=0). Different k_signal roll offsets
at N>>k_signal are orthogonal (selftest_roll_orthogonality).

This cell tests: **frequency-multiplexed WM where each slot k uses a
different `roll(item, k * delta_k)` write offset, read via lock-in
demodulation at the slot's k_signal.**

NOT the same as Cell 6 v3 today (shared-W FDM-plasticity stacking which
went MIDDLE_BAND because the frequency-stacking COLLAPSED to unigram).
This cell stores DATA at different frequencies, not plasticity rules.

## Mechanism (untried)

For K slots, choose `delta_k = N // K`. Per slot k in 0..K-1, the carrier
offset = `k * delta_k`.

WRITE (NAIVE_HRR_WM, baseline):
  workspace = sum_k bind(item_k, slot_tag_k)
  (slot_tag_k is a random bipolar vector per slot)

WRITE (FREQUENCY_MULTIPLEXED, new):
  workspace = sum_k roll(item_k, k * delta_k)
  (item_k stored at a different roll offset; slot identity = roll offset)

READ slot k (NAIVE_HRR_WM):
  retrieve = workspace * slot_tag_k
  cleanup against codebook

READ slot k (FREQUENCY_MULTIPLEXED):
  retrieve = roll(noisy_workspace, -k * delta_k)
  cleanup against codebook

READ slot k (FREQUENCY_MULTIPLEXED + LOCK_IN):
  for p in 0..P-1:
    retrieve_p = roll(noisy_workspace, -k * delta_k + p * dk_fine)
                 * cos(2*pi*p/P)
    accumulated_p = (2/P) * retrieve_p
  cleanup accumulated against codebook
  (P-phase lock-in demodulation per slot for SNR lift; same primitive
   chain-grade-validated by lock_in_amplifier_hd_frequency_v1_FULL)

## Pre-registered bands

**HARD_PASS_CHAIN_GRADE_WM_K_EXTENSION:**
- FM_LOCK_IN_K128 sigma=1.0 >= 0.98 (vs NAIVE 0.908)
- FM_LOCK_IN_K256 sigma=1.0 >= 0.90 (vs NAIVE 0.555)
- cv <= 0.05 across 3 seeds
- AND cross-slot crosstalk (BIAS-INTERMOD check) < 0.10 per slot

**HARD_PASS_PARTIAL_LOCK_IN_LIFT:**
- FM_LOCK_IN beats NAIVE by >= 0.10 at K=128 OR K=256
- (substantial lift even if not at the 0.98/0.90 chain-grade bar)

**MIDDLE_BAND_FM_MARGINAL:**
- FM_LOCK_IN lift over NAIVE in [0.05, 0.10] at K=128 or K=256
- (mechanism present; not chain-grade)

**HARD_FAIL_FM_NO_LIFT:**
- FM_LOCK_IN <= NAIVE at K=128 AND K=256
- (frequency multiplexing doesn't help in substrate; the brain analog
   doesn't transport at this scale -- a clean negative)

**HARD_FAIL_INTERMOD:**
- FM_LOCK_IN cross-slot bleed > 0.10
- (FDM intermod kills the mechanism even when avg recall looks fine;
   per-slot purity required for chain-grade)

## Calibration rationale

- 0.98 / 0.90 targets at K=128 / K=256 reflect lock-in's chain-grade 16x
  lift at sigma=64; even half that lift would push NAIVE 0.908 -> ~1.000.
  We pre-register the FULL prediction, not a softened one.
- delta_k = N // K = 4096//256 = 16 at the hardest K. The roll-orthogonality
  selftest (run at N=8192) showed |roll(v, k) @ v / N| < 0.1 for k in
  {1, 127, 1023}. At N=4096 we need k>=16 for clean orthogonality, which
  is the smallest delta_k tested. Borderline.
- P=8 phases per lock-in demod chosen to match lock-in cell's
  ARM_LOCK_IN_P8 (chain-grade 1.000 at sigma=32 N_DIM=8192).
- cv <= 0.05 (tighter than typical 0.07) because the mechanism is
  deterministic up to noise seed.

## Q-discipline (BIAS-Q + intermod check)

Per Fix #28: read per-slot metrics, not aggregate. The verdict_msg includes:
- Per-K mean recall at sigma=1.0
- Per-K cross-slot bleed (each slot's READ retrieves slot k -- check that
  it does NOT preferentially retrieve any OTHER slot's stored item; bleed
  = max over j != k of P(read_k retrieves item_j))

If FM_LOCK_IN hits 1.000 at K=128 with cv=0, BIAS-Q saturation flag ->
verify the K=256 result independently; demote to MM if regime is too easy.

## Capacity-feasibility analysis

- WRITE complexity: K rolls per write = 128 rolls at N=4096 = 512K ops.
  Trivial.
- READ complexity per slot: P=8 lock-in phases * 1 roll + 1 cleanup
  (codebook argmax over 512 atoms at N=4096 = 2M ops per slot).
  Per query: K reads = 128 * 2M = 256M ops. Substantial but feasible.
- For K=256: 256 * 2M = 512M ops per query; N_ITEMS_PER_K=200/256 = 1
  trial. Per seed: ~1.0e9 ops. Wall ~5-15s per seed per arm. OK.

## Q-discipline cross-arm verification

Per Fix #28: verdict_msg includes per-arm per-K mean + cv + cross-slot
bleed. Do NOT propagate "FM solved it" from verdict_msg without reading
per-K + cross-slot metrics. Specifically:
- If FM_K128 = 0.99 but cross-slot bleed = 0.30, the mechanism is
  reading the wrong slot half the time -- aggregate hides it.
- If FM_K128 = 0.99 and FM_K256 = 0.50, the K extension is fake (just a
  coincidence at K=128).

## Smoke regime match

Smoke at K=128 + N=4096 + 3 seeds (no smoke-vs-full sign-flip risk -- the
FM mechanism does not depend on n_chains, which is the dimension that
flipped sign in 3 cells today). The capacity-sensitive dimension is K
itself; smoke includes K=128 so smoke result is informative.

Smoke gate: if FM_K128 >> 0.98 with cv=0, BIAS-Q flag; verify K=256
separately before full dispatch.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; PROT-018 does not apply.

## Timeout estimate

Smoke ~ 30-60s at K=128 + N=4096 + 3 seeds (no full K=256 yet).
FULL: K_grid=[32,64,128,256] + N=4096 + 3 seeds + 4 arms.
Scaling: lock-in adds P=8x per-read overhead; K_max=256.
formula: ceil(1.5 * 60 * 1.0 * (3/3) * (4 arms) * (256/128) * (8 phases))
       = ceil(1.5 * 60 * 4 * 2 * 8) = 5760s
budget timeout_s = 6000 (1.67 h).
timeout_s = 6000

## Provenance rail

ARM_NAIVE_HRR_WM_K128 reproduces WM v2 cell today's K=128 sigma=1.0 NAIVE
within +/- 0.03 of 0.908 (rail [0.88, 0.94]).
ARM_NAIVE_HRR_WM_K256 reproduces WM v2 cell today's K=256 sigma=1.0 NAIVE
within +/- 0.04 of 0.555 (rail [0.51, 0.60]).
If either rail breaches, verdict is RAIL_SANITY_BREACH.

## Cross-cell apples-to-apples

Seeds [11, 13, 19] match WM v2 cell today for direct apples-to-apples.
Per-arm reference values in verdict_msg:
- NAIVE_K128_sigma1.0 = 0.908 (from WM v2)
- NAIVE_K256_sigma1.0 = 0.555 (from WM v2)
- target: FM_LOCK_IN_K128 >= 0.98 + FM_LOCK_IN_K256 >= 0.90 for HARD_PASS
       OR FM_LOCK_IN beats NAIVE by >= 0.10 at K=128 OR K=256 for HARD_PASS_PARTIAL
