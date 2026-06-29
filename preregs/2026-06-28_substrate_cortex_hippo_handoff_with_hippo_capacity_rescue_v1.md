# Pre-registration: substrate_cortex_hippo_handoff_with_hippo_capacity_rescue_v1

**Date:** 2026-06-28
**Anchor base:** substrate_cortex_hippo_handoff_with_hippo_capacity_rescue_v1
**Chunks (planned):** 3 single-seed cells {seed_7, seed_13, seed_19}
**Script (seed_7):** experiments/exp_substrate_cortex_hippo_handoff_with_hippo_capacity_rescue_v1_seed_7.py
**Queue (planned):** overnight_queue (GPU; remote@home) — FULL only if smoke fires discriminator
**Lineage:**
- experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_7.py (CLOSED-neg)
- experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py (CLOSED-neg)
- experiments/exp_substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1_seed_7.py (SMOKE 3-way COLLAPSE)
**Drill source:** USER 2026-06-28 — diagnostic probe asking which (if any) hippo-readout-fidelity
rescue opens up Stage 2 NREM consolidation at chain-grade M=8192. The spaced-rep NREM smoke
just established that the hippo READOUT FIDELITY is the floor, NOT the consolidation schedule.

## Tier

**DIAGNOSTIC PROBE — default tier MEASURED_MECHANISM, not chain-grade promotion.**

If discriminator FIRES at any swept N_h (rescued closes >= 0.50 of DIRECT-STANDARD
gap), that is a RESEARCH SIGNAL not a chain-grade claim. Skunkworks may
re-tier upward based on the per-N_h profile.

## Hypothesis (testable)

At chain-grade M=8192, the standard `sign(W_h @ cue)` hippo readout is the
limiting factor (not consolidation schedule). A substrate-only readout-
fidelity rescue (here: 2-step Hopfield cleanup `sign(W_h @ sign(W_h @ cue))`)
can close some fraction of the (DIRECT - STANDARD) recall gap, OPENING the
regime in which consolidation testing (incl. spaced-rep NREM) becomes
honest.

The sweep over N_h tells us at which capacity regime the rescue helps:
- Small N_h (very saturated, alpha_h >> 1): cleanup likely cannot help —
  W_h is too dense / random.
- Medium N_h (saturated, alpha_h ~ 1): cleanup may or may not help —
  classical Hopfield "1-step cleanup" regime.
- Large N_h (sub-capacity, alpha_h << 0.138): DIRECT and STANDARD should
  CONVERGE, and the rescue becomes moot (no bottleneck to fix).

If the discriminator profile is monotonic (rescue helps more as N_h grows)
that re-confirms the readout-fidelity diagnosis. If non-monotonic (peaks
at intermediate N_h), the rescue is finding a specific Hopfield basin
regime — itself interesting.

If rescue NEVER helps across the full sweep, that closes the
"two-step-Hopfield" rescue arm and points future research at richer
mechanisms (BCM/anti-Hebbian cleanup, multi-iteration cleanup, larger
non-Hopfield encoders).

## Mechanism (v1 hippo capacity rescue)

Common across all arms:
- Sparse-DG hippo, 10% active, k-WTA pattern separator (P_in @ x then top-k)
- Hippo encode: one-shot Hebbian outer product `W_h += vals_h_i (X) keys_h_i`
- Dense cortex (N_c=8192 fixed), L2-normalized cortex queries/values
- One replay pass per item (N_REPLAY_PER_ITEM=1; we are isolating the readout
  question, not the consolidation schedule)
- Cortex write: `W_c += eta * vals_c_react (X) cues_c`
- Recall: `sign(W_c @ keys_c[i])` then cosine-match to vals_c

Arms differ in HOW vals_c_react is produced:

### ARM_DIRECT_NO_HIPPO
- Bypass hippo readout entirely.
- `vals_c_react = vals_c[i]` (the encoded cortex value).
- No noise floor; reference ceiling for given (M, N_c, eta_c).

### ARM_STANDARD_HIPPO
- `vals_react_h = sign(W_h @ cue_h)`
- `vals_c_react = L2-normalize(P_hc @ vals_react_h)`
- Standard substrate baseline. Noisy when alpha_h > 0.138 (Hopfield-strict).

### ARM_RESCUED_HIPPO
- Two-step cleanup: `step1 = sign(W_h @ cue_h)`; `step2 = sign(W_h @ step1)`
- `vals_c_react = L2-normalize(P_hc @ step2)`
- Cell-author chose 2-step Hopfield cleanup over BCM or multi-readout-averaging
  because:
  1. SUBSTRATE-ONLY (no learning-rule changes; reuses same W_h)
  2. CHEAP (one extra N_h^2 matmul + sign per replay; FFlops ~2x standard)
  3. CLASSICAL HOPFIELD ONE-STEP CLEANUP (Hopfield 1982; well-documented
     either converges to a better basin or oscillates near saturation —
     never strictly worse than 1-step in expectation).
  4. Stage 1 SUBSTRATE EVIDENCE (per USER 2026-06-26 stage progression
     discipline: prove the substrate-native path FIRST, then optimize).

## Sweep

- M = 8192 (FULL; chain-grade) / 2048 (SMOKE)
- N_c = 8192 (FULL; chain-grade) / 2048 (SMOKE)
- N_h_grid (FULL) = [1024, 2048, 4096, 8192, 16384, 32768]
- N_h_grid (SMOKE) = [512, 2048, 8192]
- alpha_hopfield = M / (2 * N_h * log(N_h)) ranges from ~0.59 (N_h=1024) to
  ~0.012 (N_h=32768) at FULL.
- 3 arms x 6 N_h = 18 units per FULL seed.
- 3 arms x 3 N_h = 9 units per SMOKE.

## Pre-registered fairness disciplines

1. SAME encoded keys_h / vals_h / P_in / P_hc per (seed, N_h) across all
   3 arms.  Per-N_h fresh projection matrices (seed-stable via rng_nh
   seeded with seed + 1000 + N_h).
2. SAME M items across arms.  SAME replay permutation across arms within
   a given (seed, N_h, rep).
3. Hippo readout differs ONLY by single vs two-step cleanup (or bypassed
   entirely for DIRECT).
4. Per Fix #24: FULL would use torch+cuda; overnight_queue routing
   justified.
5. META_RULE_AF: STANDARD and RESCUED arms must produce distinct readouts
   when alpha_h > 0.4 (selftest verifies on tiny saturated world).
6. META_RULE_AH: atomic metrics.json write (.tmp + os.replace).
7. META_RULE_H: cardinality_ok = (n_units == 3 * len(N_H_GRID)).
8. PROT-021 checkpointed via _seed_checkpoint helper.

## Discriminator + pre-registered thresholds

Per (seed, N_h) we compute:
- gap_dir_std = DIRECT - STANDARD recall (positive = readout bottleneck real)
- gap_dir_rsc = DIRECT - RESCUED recall (positive = bottleneck partially survives)
- rescued_closes_fraction = (gap_dir_std - gap_dir_rsc) / gap_dir_std
  - +1.0 = perfect close (RESCUED matches DIRECT)
  - +0.0 = no help (RESCUED matches STANDARD)
  - negative = RESCUED HURTS (cleanup oscillates worse than 1-step)

best_close_frac = max over N_h of rescued_closes_fraction.

- **HARD_PASS (diagnostic)**:
  any_discriminator_fired (some N_h has |gap_dir_std| > 0.05) AND
  best_close_frac >= 0.25
- **MAJOR_UNLOCK** (verdict tag):
  best_close_frac >= 0.50 — substrate-only readout rescue OPENS chain-grade
  Stage 2 NREM closure with a regime-conditional amendment.
- **HARD_FAIL**:
  META_RULE_AF (STANDARD bit-identical to RESCUED while differing from
  DIRECT — cleanup is no-op when it should be active) OR
  cardinality breach (n_units != EXPECTED_N_UNITS).
- **MIDDLE_BAND**:
  - No N_h had discriminator fire (|gap_dir_std| < 0.05 across full sweep):
    readout bottleneck is not the failure mode in this regime; rescue
    hypothesis cannot be tested.  Honest INCONCLUSIVE.
  - Discriminator fired but best_close_frac < 0.25: cleanup is insufficient.
    Honest negative.

## DISCRIMINATOR-SURVIVES-SCALE smoke gate (USER 2026-06-26 LOCKED)

Smoke at M=2048 N_c=2048 sweeps N_h = [512, 2048, 8192]:
- N_h=512:  alpha_h = 2048 / (2 * 512 * log(512)) = 0.320 (saturated)
- N_h=2048: alpha_h = 2048 / (2 * 2048 * log(2048)) = 0.0657 (sub-capacity)
- N_h=8192: alpha_h = 2048 / (2 * 8192 * log(8192)) = 0.0139 (well sub-capacity)

At smoke, ARM_DIRECT must exceed ARM_STANDARD by >= 0.05 at SOME N_h to
prove the readout bottleneck is real before chasing fidelity rescue at
FULL.  If smoke shows DIRECT ~= STANDARD across all 3 N_h points,
chain-grade dispatch is BLOCKED (the bottleneck framing doesn't hold at
this regime).

Conversely, if smoke shows RESCUED meaningfully closing the gap at any
N_h, FULL dispatch is AUTHORIZED to characterize the per-N_h profile at
chain-grade.

## Pre-registered MANDATORY §15 envelope-fail-bands

1. **Sweep alignment:** ALIGNED — N_h is the swept knob (M held).
   sweep_alignment_verdict = ALIGNED.

2. **Discriminating fraction:** discriminating_fraction >= 0.30 predicted
   per N_h (some N_h must show clear arm separation).

3. **Signal-shape audit (META_RULE_AP_v3):**
   - hippo state: sparse_N_h, bipolar +-1, 10% active.
   - hippo->cortex projection P_hc: R^{N_h} -> R^{N_c} (dense Gaussian).
   - cortex query/value: dense_N_c, L2-normalized.
   - readout path differs ONLY in cleanup-iteration count (0, 1, or 2).

4. **Positive control at sub-capacity:**
   - selftest `_selftest_positive_control_small` verifies DIRECT at
     M=200 / N_h=256 / N_c=512 returns >= 0.95 recall.
   - Catches encode/write/recall pipeline bugs before the diagnostic
     sweep runs.

5. **Functional-requirement decomposition:**
   - (a) Sparse-DG k-WTA pattern separator — selftest `_selftest_sparse_pattern_separator`.
   - (b) Single-step hippo readout — `hippo_readout_standard`.
   - (c) Two-step cleanup readout — `hippo_readout_rescued_two_step`;
     selftest `_selftest_rescued_vs_standard_distinct_when_noisy` verifies
     non-no-op on saturated regime.
   - (d) Cortex Hebbian write + recall — selftest `_selftest_positive_control_small`.
   - (e) Torch batched matmul matches numpy loop — selftest
     `_selftest_torch_batched_matches_numpy`.

## Pre-reg fields (required)

- `expected_n_units = 3 * len(N_h_grid)` (18 FULL / 9 SMOKE)
- `cardinality_ok` mandatory in metrics.json
- `HARD_FAIL_CARDINALITY_BREACH` when observed != expected
- `HARD_FAIL_META_RULE_AF` when STANDARD bit-identical to RESCUED while
  differing from DIRECT
- `per_nh_rows[]` array of {N_h, direct, standard, rescued,
  gap_direct_minus_standard, gap_direct_minus_rescued,
  rescued_closes_fraction, alpha_hopfield, alpha_simple}
- `discriminator_survives_scale` -- smoke demonstrates bottleneck exists
  BEFORE FULL dispatch
- §13 patterns: start_marker + crash_diagnostic (fatal.log) + per-seed
  checkpoint + heartbeat

## Smoke result (2026-06-28, exp_dev cell-author) — COMPLETED

Smoke config: M=2048, N_c=2048, N_h_grid=[512, 2048, 8192],
n_replay_per_item=1, eta_c=0.005, seed=7.

Smoke wall: 31.9 seconds (batched-numpy path; replaces per-item Python loop
that had hit a 30+ min wall on first attempt and timed out).

| N_h  | alpha_h | ARM_DIRECT | ARM_STANDARD | ARM_RESCUED | gap(D-S) | close_frac |
|------|---------|------------|--------------|-------------|----------|------------|
|  512 | 0.3206  | 0.659      | 0.113        | 0.000       | +0.546   | **-0.208**  |
| 2048 | 0.0656  | 0.947      | 0.176        | 0.000       | +0.771   | **-0.228**  |
| 8192 | 0.0139  | 0.989      | 0.226        | 0.000       | +0.763   | **-0.296**  |

**Smoke verdict: MIDDLE_BAND (diagnostic).**

Verdict rationale:
- Discriminator FIRED at all 3 N_h points (|D-S| >> 0.05 everywhere).
- best_close_frac = -0.208 at N_h=512, far below HARD_PASS threshold (0.25).
- RESCUED actively HURTS: 2-step cleanup converges to a zero-signal
  fixed point at every N_h, producing recall=0.000.

## Honest diagnosis

The smoke produces a clean, important DIAGNOSTIC NEGATIVE for the
2-step-Hopfield-cleanup rescue hypothesis:

1. **The readout bottleneck is REAL and persists down to alpha_h=0.014**
   (well-sub-capacity).  At M=2048 N_h=8192 the substrate's Hopfield-strict
   capacity is alpha_h_max=0.138, yet STANDARD recall = 0.226 vs DIRECT
   = 0.989.  The readout-noise floor is NOT explained by Hopfield capacity
   alone -- there is a structural noise source intrinsic to
   `sign(W_h @ cue)` at this hippo encoder / sparsity / scale.
2. **2-step Hopfield cleanup is the WRONG substrate-only rescue.** It
   converges to an information-free fixed point at every regime tested.
   Mechanism: after the first sign(), the cue is replaced with a vector
   that has lost the per-item information; the second sign() reads out
   the average of all M stored vals, not the i-th val.
3. **DIRECT scales healthily with N_h** (0.659 -> 0.947 -> 0.989).  The
   cortex Hebbian writer is NOT the bottleneck.  Whatever rescue mechanism
   eventually works has to target the readout path, not the consolidation
   path.

## Decision

**NO FULL dispatch.** Smoke result is conclusive at this scale -- the
proposed rescue mechanism makes things WORSE.  FULL dispatch would burn
~6 GPU-hours per seed to confirm the negative; the smoke evidence is
already structurally identical to what FULL would produce (the close_frac
is dominantly negative across the full alpha_h sweep, including the
well-sub-capacity regime).

## Research signals (for Director / Skunkworks consumption)

Three concrete next-step directions are OPENED by this honest negative:

**(A) The readout-noise floor is NOT Hopfield-capacity-driven.**  Smoke at
alpha_h=0.014 still shows DIRECT >> STANDARD by 0.76.  This contradicts
the "alpha_h > 0.138 is the bottleneck" framing inherited from
spaced-rep NREM smoke.  The bottleneck is structural to the sparse-DG
+ sign-readout combination.  Possible root causes worth probing:
   - Interference from sparse-overlapping keys (10% activity, 410 of 4096
     bits on at N_h=4096; non-orthogonal across items)
   - Sign quantization noise (every bit thresholded individually)
   - L2-norm-after-sign destroys magnitude info that smooths recall

**(B) The 2-step Hopfield cleanup converges to an information-free basin.**
This is itself a substrate finding -- it implies the W_h Hopfield landscape
is dominated by spurious attractors at this sparsity (10% k-WTA hippo).
A follow-up cell could test:
   - Single-iteration cleanup with thresholded magnitude (preserves info)
   - Damped iteration (alpha*sign(W_h @ x) + (1-alpha)*x)
   - BCM-style synaptic gain modulation (anti-Hebbian on noise floor)
   - Multi-readout averaging with stochastic key perturbation

**(C) The cortex Hebbian writer is healthy.**  DIRECT recall 0.989 at
M=2048 / N_c=2048 / N_h=8192 confirms that if a clean read can be
provided, the dense cortex can store and retrieve chain-grade-scale
items.  This re-frames the closure problem: substrate-only rescue must
fix the READ-OUT, not the WRITE-IN.

## Cap-map rows (proposed, conditional on smoke negative)

- "2-step Hopfield cleanup `sign(W_h @ sign(W_h @ cue))` is CLOSED-NEGATIVE
  as a substrate-only readout-fidelity rescue at all swept N_h (smoke 2026-06-28).
  Mechanism converges to zero-signal fixed point."
- "Hippo readout noise floor is NOT explained by Hopfield-strict capacity
  alone -- STANDARD recall ~ 0.18-0.23 even at alpha_h = 0.014 (smoke
  evidence).  Structural noise from sparse-DG + sign-readout combination."
- "Dense cortex Hebbian writer SCALES to recall = 0.989 at M=2048 / N_c=2048
  given a clean direct-encoded value path (ARM_DIRECT smoke).  Future
  rescue mechanisms target the read path not the write path."

## Coordination

- Cell-author: exp_dev (this dispatch; SMOKE MIDDLE_BAND, NOT shipped to FULL).
- Landed-VET: skunkworks (audits smoke metrics + verdict logic + per-N_h rows).
- Research / Director: review smoke profile; consider follow-up rescue
  variants from (B) above.  Track (A) as standalone bottleneck-class probe.

## Cap-map rows (proposed; conditional on results)

- If MIDDLE_BAND (no discriminator fired):
  "Substrate readout-fidelity bottleneck is NOT the failure mode at this
  M / N_h regime; rescue hypothesis moot at smoke. Re-test at chain-grade
  before closing."
- If MIDDLE_BAND (discriminator fired, rescue insufficient):
  "2-step Hopfield cleanup is NOT sufficient as a substrate-only readout
  fidelity rescue at this regime. Try BCM cleanup / multi-step iteration /
  larger N_h / non-Hopfield encoder."
- If HARD_PASS / MAJOR_UNLOCK:
  "Substrate-only 2-step Hopfield cleanup rescues hippo readout fidelity
  at <N_h=X>; OPENS Stage 2 NREM consolidation testing at chain-grade.
  Follow-up: re-run spaced-rep NREM cell on top of the rescued readout."

## GPU rationale (planned)

Per Fix #24: FULL would use torch.cuda with batched cleanup matmul.
- Largest N_h = 32768 -> W_h fp32 = 4.3 GB
- W_c (8192x8192 fp32) = 268 MB
- keys_h bank (8192x32768 fp32) = 1.0 GB
- vals_h bank (8192x32768 fp32) = 1.0 GB
- Per arm peak ~6.6 GB; fits 8GB cards but borderline. Per-arm streaming
  (free large N_h tensors between arms) recommended.
- Per arm: encode (M x N_h matmul) + 1 replay pass (M x N_h matmul + cleanup
  iteration). For N_h=32768 with M=8192: ~270 GFlop encode + 270 GFlop
  per replay step. 18 arms total. Estimated 1-2h/seed on RTX 4060 Ti.

Timeout estimate: ceil(1.5 * smoke_wall * (FULL_size / smoke_size) * 1) with
scaling exp 1.5 (matrix ops). Conservative budget: 21600s (6h) per PROT-019
floor for _n>=8192-class workloads.

Note: anchor name does NOT contain `_n8192` literal token (uses `_v1_seed_7`),
but to be safe under PROT-019 we'll set --timeout 21600 explicitly.

## Coordination

- Cell-author: exp_dev (this dispatch). Smoke gates FULL.
- Landed-VET: skunkworks audits per-arm per-N_h breakdown + verdict logic.
- Research / Director: review smoke profile; if MAJOR_UNLOCK signal, file
  follow-up spaced-rep-on-rescued-readout cell.

## Risk + mitigations

- META_RULE_AF risk: at very sub-capacity N_h (e.g. 32768), W_h is sparse
  and well-defined; sign(W_h @ cue) likely matches sign(W_h @ sign(W_h @ cue))
  on most items (cleanup converges instantly). This is NOT a META_RULE_AF
  violation by intent (the cells are identical only when the regime is
  unsaturated). Verdict logic explicitly guards: META_RULE_AF only fires
  when STANDARD ~ RESCUED but BOTH differ from DIRECT — i.e. when the
  bottleneck exists but cleanup is silently no-op.
- Memory pressure at N_h=32768: W_h alone is 4.3GB fp32. Per-arm streaming
  + W_h.zero_() between arms prevents accumulation.
- POSITIVE CONTROL: selftest verifies DIRECT @ M=200/N_h=256 returns >=0.95;
  catches encode/write/recall pipeline bugs before sweep.
