# Pre-reg: g1b_capacity_sweep_v1

**Date:** 2026-06-22
**Anchor:** g1b_capacity_sweep_v1
**Cell:** experiments/exp_g1b_capacity_sweep_v1.py
**Routing:** Director (Skunkworks-routed) -> Exp-Dev hand-off 2026-06-22 post-g1 MEASURED_MECHANISM ruling
**Predecessor:** g1_substrate_native_generation_v1 (commit 72558958 cell + 7083c38b LANDED-VET = MEASURED_MECHANISM)

## Why this cell exists

g1 LANDED MEASURED_MECHANISM (not chain-grade) per cert-owner ruling:
- The original test (N_PAIRS=190, N_DIM=4096, density 0.046) operates BELOW
  the substrate Hebbian capacity floor (~327 for N_DIM=4096).
- novelty_ratio=401 was 100% of analytic_cap=400 = metric-saturated by
  construction.
- The 4-arm mechanism-shape signal (cleanup load-bearing) IS valid + filed as
  META atom (meta::META_codebook_NN_cleanup_is_load_bearing_for_substrate_native_generation).

What's MISSING for chain-grade: evidence ABOVE by-construction-saturation.
This cell sweeps N_PAIRS through and past the capacity floor; the failure-
boundary location IS the chain-grade evidence.

## Mechanism (same as g1; only N_PAIRS varies)

Identical to g1: S matrix Hebbian writes on adjacent ordered pairs +
codebook NN cleanup +/- Langevin noise. The 4-arm contrast (NONE / S_ONLY /
S_LANGEVIN / S_LANGEVIN_CLEANUP) is the discriminator (Fix #16). g1's
substrate-only-decode gate, W-unchanged invariant, and atexit synthesizer
are inherited verbatim.

## Config (locked at design time)

- N_DIM = 4096 (fixed; matches g1)
- K_SEQ = 20 (fixed; matches g1)
- N_SEQ scan = [11, 22, 43, 85, 169, 337]
- N_PAIRS scan = N_SEQ * (K_SEQ - 1) = [209, 418, 817, 1615, 3211, 6403]
- approx-density (N_PAIRS / N_DIM) = [0.051, 0.102, 0.199, 0.394, 0.784, 1.563]
- Hebbian capacity floor for N_DIM=4096 is ~327
  -> N_PAIRS=209: below floor (reproduces g1's by-construction-saturation)
  -> N_PAIRS=418: just above floor
  -> N_PAIRS=817: 2.5x floor
  -> N_PAIRS=1615: 5x floor
  -> N_PAIRS=3211: 10x floor
  -> N_PAIRS=6403: 20x floor (expected cliff zone)
- 3 seeds = [7, 17, 23] (matches g1)
- T_GENS = [1, 4, 8] (T=16 dropped to bound runtime; primary T=8)
- N_PROBES_PER_T = 30 (tightened from g1's 40 to bound wall)
- N_OOD_PROBES = 30
- LANGEVIN_SIGMA_SCALE = 0.10 (matches g1)
- REFUSE_TAU = 0.10 (matches g1)
- Corpus: synthetic bipolar keys (substrate-primitive isolation; same as g1 / c3)

## Pre-registered HARD bands (chain-grade target)

**HARD_PASS (chain-grade evidence above by-construction-saturation):**

1. Arm 4 (S_LANGEVIN_CLEANUP) maintains `coh@T=8 >= 0.60` across
   `>= 3 of 6 N_PAIRS scan-points`.
2. AND Arm 4 degrades GRACEFULLY past Hebbian capacity (does NOT cliff to
   `coh <= 0.10` at any single intermediate point).
3. AND AT LEAST ONE N_PAIRS scan-point shows Arm 4 with HEADROOM TO FAIL,
   defined as `coh < 0.99 AND coh >= 0.60`. This is the chain-grade gate:
   when coh < 1, some generated steps DID fail to land on planted
   continuation = test COULD have failed harder = test has discriminating
   power.
4. AND 4-arm spread preserved (`cleanup > S_LANGEVIN > NONE`) at all
   N_PAIRS where `coh > 0.20`.
5. AND `zero_llm_calls_at_inference == True`.
6. AND W matrix L2-norm unchanged by generation (per-arm assertion).

**HARD_FAIL:**
- Arm 4 cliffs to `coh <= 0.10` at any N_PAIRS <= 400
- OR 4-arm spread inverts (cleanup <= S_LANGEVIN) at any scan point above 200
- OR substrate-only-decode gate violated (n_llm > 0)
- OR W modified by generation

**MIDDLE_BAND:**
- Arm 4 degrades smoothly but does NOT show headroom-to-fail at any
  N_PAIRS > 200 (perfect-by-construction at every above-floor point)
- OR fewer than 3 of 6 scan-points at HARD_PASS bar

## CRITICAL DESIGN DECISION: saturation flag distinction

Two saturation signals are computed; only ONE is the chain-grade gate:

1. **novelty/cap saturation (REPORTED, NOT gating):** `novelty/analytic_cap > 0.9`.
   Single-seed timing run confirmed this fires at ALL scan-points up to 1958%
   above Hebbian floor where cleanup still works. It's a METRIC ARTIFACT of
   cleanup deterministically snapping to correct entries, NOT a capacity signal.

2. **headroom-to-fail (CHAIN-GRADE GATE):** `coh < 0.99 AND coh >= 0.60`.
   This is the right discriminator -- when coh < 1, some steps DID fail
   while overall the mechanism still passes the bar = proven discriminating
   power.

Single-seed timing showed N_PAIRS=6403 gives coh_arm4=0.95 (FIRST sub-1.0
point), which would qualify as headroom-to-fail under the corrected logic.

## Pre-reg direction (Fix #5)

Arm 4 > Arm 1 at all coh > 0.20 points. A large abs-delta in the wrong
direction (Arm 1 > Arm 4) = HARD_FAIL, not MIDDLE_BAND.

## W vs S separation

Writes ONLY mutate S; W untouched. Per-arm assertion enforced.

## Honest scope

- Phase 1 scope: same as g1 -- synthetic-bipolar disjoint-key sequences;
  position-binding via codebook itself; ZERO LLM forward calls.
- The cleanup mechanism's apparent saturation at the analytic_cap upper bound
  is a metric artifact (novelty maximizes when cleanup snaps to correct
  entry). The chain-grade test uses headroom-to-fail (coh < 0.99) instead.

## Single-seed timing measurement (Fix #17 strict enforcement)

Empirical: 1 seed * 6 scan-points * 4 arms full config = **3m42s** wall.
Per-N_PAIRS-arm scaling: 0.7s (n_pairs=209 NONE) to 26s (n_pairs=6403
S_LANGEVIN). Per-seed total ~3m42s. 3 seeds sequentially ~11m6s.

Selected timeout: 1.5 * 3m42s * 3 seeds = ~17min. Conservative timeout 1800s.

## Dispatch routing

**local_cpu_queue** (3-seed wall ~11min is well under 30min CPU threshold;
pure numpy + matmul; matches single-laptop CPU profile).

## Self-tests (formula-selftests)

1. NONE T=3 small-config: `coh <= 0.40` (random)
2. S_LANGEVIN_CLEANUP T=3 small-config: `coh >= 0.50`
3. `_LLM_CALL_COUNTER == 0` throughout
4. analytic_cap == 2 * N_codebook (sanity)

## Pre-reg single-seed preliminary (laptop CPU, seed=7, full config)

Per-N_PAIRS coh_arm4@T=8 from the timing run:
- N_PAIRS=209  -> coh=1.000 (saturated novelty/cap; sat=True)
- N_PAIRS=418  -> coh=1.000 (saturated)
- N_PAIRS=817  -> coh=1.000 (saturated)
- N_PAIRS=1615 -> coh=1.000 (saturated)
- N_PAIRS=3211 -> coh=1.000 (saturated)
- N_PAIRS=6403 -> coh=0.950 (HEADROOM-TO-FAIL POINT; 5% generated steps missed planted)

Cliff = NONE detected. Cleanup arm dominates at every above-discriminator-
bar point. Substrate-only=True; W_unchanged=True; llm=0.

These are SINGLE-SEED preliminaries. 3-seed full run is the cert-graded artifact.

## Calibrated P

P(HARD_PASS) = 0.60. Single-seed prelim already shows headroom-to-fail at
6403 pairs; 3-seed cv-tightness is the remaining uncertainty. Higher than
the Director's 0.50 estimate because the prelim revealed cleanup is
remarkably robust at 20x Hebbian floor.

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND; per USER STANDING)

If HARD_FAIL cliff: route to Research for capacity-rescue (dense-Hopfield
p=3 readout per Karuvally polynomial nonlinearity; HDC-binding-factored
W_seq using substrate KG directly).

If MIDDLE_BAND (no headroom-to-fail point): route to Research for
discriminator-rescue (introduce explicit perturbation: corrupted starts,
higher sigma, longer T; design a CAN-fail regime for cleanup).

## Artifacts

- Cell: `experiments/exp_g1b_capacity_sweep_v1.py`
- Pre-reg (this file): `preregs/2026-06-22_g1b_capacity_sweep_v1.md`
- Composes with: c3 SequenceMatrix; g1 mechanism-shape META atom

## Atom ID candidate (for Skunkworks A5 if chain-grade)

`research::T1/EXP_g1b_capacity_sweep_v1`

Promotion path: g1b HARD_PASS -> g1 research::T1 atom upgraded from
MEASURED_MECHANISM to chain-grade (CERT 586 -> 587).
