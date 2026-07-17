# Pre-registration: substrate_phase_diagram_subsystem_decoupling_v3

RESOLUTION cell (exp_dev task 2026-07-17), promoting v2 (3c71a79aa, landed
MEASURED_MECHANISM/mixed). Full pre-reg embedded in the cell docstring:
`experiments/exp_substrate_phase_diagram_subsystem_decoupling_v3.py` (top).
This file is the pointer + condensed summary for queue_add.sh provenance.

## Question

v2 closed claim(a) [capacity reconciliation, HARD_PASS, 30.00x error
reduction] but left the NEW Part-B decoupling-regime characterization at
MIDDLE (mean|genuine-pred|=0.133 > 0.10 band; mean|genuine-misaligned|=0.050
at the 0.05 band edge) -- the ONLY thing blocking full chain-grade. Is the
regime SOFT_GRACEFUL (theta-gamma brain-parity) or HARD_ZERO (orthogonal-
subspace substrate-native beat-the-brain), or genuinely MIDDLE?

## BUG FOUND (MEASURED, disclosed) -- root cause of v2's MIDDLE, not just resolution

v2's Part-B "combined-load graceful prediction" computed
`s_pred = sqrt(N/total_load)` -- the SAME uncorrected/naive sensitivity
formula that claim(a) already showed under-predicts capacity by up to 30x.
v2's own docstring stated the intended formula includes C_FHRR
(`s=sqrt(C_FHRR*N/(w_wm+B_extra))`); the code never applied it. Recomputed at
v3 module-load time: naive (v2's actual code) predicts the 0.5-recall
crossing at total_load~=188.6 (B~=176.6); the RECONCILED formula (C_FHRR
included, same constant already validated HARD_PASS in claim-a) predicts
total_load~=375.96 (B~=364.0) -- identical to the claim-a calibration anchor
itself (same N=1024, same D=V_VAL_WM=64). v2 was testing GENUINE against an
already-refuted prediction. This is exactly the task's design-gate
instruction: "predict-then-verify against the reconciled formula, not naive
Plate."

## v3 changes (ONE VARIABLE: the regime-discriminating measurement; Part-A/legacy-b/c UNCHANGED)

1. **Formula fix**: Part-B prediction now uses `s_pred = sqrt(C_FHRR*N/total_load)`.
2. **Finer B-grid**: 10 -> 21 points, densified 150-620 around the corrected
   crossing B~=364 (v2's grid had only B=200/400 bracketing the OLD, wrong
   crossing at B~=177).
   `[0, 12, 50, 100, 150, 200, 250, 300, 330, 364, 400, 450, 500, 550, 620, 750, 862, 1000, 1200, 1500, 1728]`
3. **More seeds**: Part-B seeds 3 -> 9 (`[7,13,19,31,47,53,61,71,89]`),
   directly targeting the seed-noise-driven flat-prefix flip v2 exhibited (a
   single seed-noisy point at B=100 made MISALIGNED's flat-prefix outlast
   GENUINE's by 1 -- backwards from a hard-zero signature).
4. **Noise-robust flat-prefix locator**: `_robust_flat_prefix_len` requires
   TWO CONSECUTIVE below-threshold points to end a flat run (a lone blip that
   recovers next point no longer ends the region) -- replaces v2's
   single-point break rule.
5. **Regime classifier extracted + unit-tested**: `classify_decoupling_regime()`
   is a standalone function, exercised in `_selftest()` against synthetic
   SOFT_GRACEFUL / HARD_ZERO / MIDDLE curves PLUS two perturbation checks
   (crossing the soft_pred_band boundary flips SOFT->MIDDLE; widening the
   flat-prefix gap flips MIDDLE->HARD_ZERO) -- satisfies the task's
   CAN-FAIL / "verify at smoke it can distinguish them" design gate.

**Decision bands themselves are UNCHANGED from v2** (HARD_ZERO:
flat_prefix_genuine > flat_prefix_misaligned+1; SOFT_GRACEFUL: mean_pred_diff
<=0.10 AND mean_genuine_vs_misaligned <=0.05; else MIDDLE) -- only the inputs
feeding them are corrected/densified, per instruction not to redefine
pre-registered bands.

## Falsifiable bands (same as v2, restated)

CLAIM (a): unchanged from v2, HARD_PASS already landed (30.00x, not re-tested
by v3 -- Part-A code is byte-identical to v2).

CLAIM (b, regime): HARD_ZERO / SOFT_GRACEFUL / MIDDLE per the classifier
above. SOFT_GRACEFUL = brain-parity (theta-gamma, Lisman & Idiart 1995 /
Lisman & Jensen 2013), NOT a failure. HARD_ZERO = Frontier-2 (beat-the-brain).
MIDDLE = neither cleanly fires (a real, honest outcome, not a design failure).

## Schema-vet gates

Identical structure to v2 (storage_strategy=mixed; cardinality_ok;
deterministic_seeding=fixed ints; discriminator survives scale = smoke uses
SAME real N/V/B values, fewer points/seeds; arms_differ_verified;
final_metrics_atomicity=tmp_replace; progress_logging=print_flush_true).
NEW: `regime_classifier_can_fail_verified: true` (3 synthetic regimes + 2
perturbation checks, all in `_selftest()`, run BEFORE any measurement).

## Compute architecture

(b) sequential-CPU with justification: unchanged from v2 for Part-A/legacy
(vectorized numpy matmuls); Part-B genuine/misaligned per-seed loop (small,
O(total_load) per seed, total_load <= 1740) -- now instrumented to capture
per-seed values (not just the mean) for a SEM diagnostic field
(`genuine_vs_misaligned_sem` per B point), used for VET transparency only,
not gating logic. Measured wall time: smoke=8.3s, FULL=71.7s (faster than
v2's 128.8s despite 2.1x more Part-B measurement calls -- Part-A dominates
total cost and is unchanged). No GPU needed. Local numpy only; no remote
queue-push / GPU / atoms / origin push.

## Measured (landed locally; both smoke and FULL)

SMOKE (3 seeds, 4-cell grid + 1 restricted, 5 Part-B points, elapsed 8.3s):
cardinality_ok=True (91/91). claim(a) MIDDLE-scale HARD_PASS-analog
(17.27x reduction, n_at_risk=4 -- smaller grid). legacy(c) fired=False
(known v2-documented smoke-only 2-seed-noise artifact around the c2=0.333
boundary, unrelated to v3's changes -- legacy code byte-identical to v2).
**Part-B regime = SOFT_GRACEFUL at smoke** (mean|genuine-pred|=0.054,
mean|genuine-misaligned|=0.039) -- confirms the discriminator fires
correctly (non-MIDDLE) even at reduced smoke scale, using the SAME real
N_WM=1024/V_VAL_WM=64 values (discriminator-survives-scale option A).

FULL (9 seeds Part-B / 3 seeds Part-A, 9-cell grid + 2 restricted, 21 Part-B
points, elapsed 71.7s): cardinality_ok=True (697/697).
  claim(a): n_at_risk=10, mean_err_naive=0.861, mean_err_corrected=0.029,
    error_reduction=30.00x -> HARD_PASS (identical to v2, byte-identical code).
  legacy(b): DECOUPLED (identical to v2).
  legacy(c): fired=True (c2=0.3333, EXACTLY reproduces v2/v1's landed value,
    same unchanged mechanism+config+seeds).
  **Part-B (RESOLVED): mean|genuine-pred|=0.033 (was 0.133 in v2 -- 4.0x
    tighter after the formula fix), mean|genuine-misaligned|=0.039 (was
    0.050 in v2), flat_prefix(genuine)=3 vs flat_prefix(misaligned)=4 ->
    decoupling_regime = SOFT_GRACEFUL.** Both SOFT_GRACEFUL bands clear with
    real margin (not floor-hugging): mean_pred_diff 0.033 vs 0.10 band
    (67% margin), mean_genuine_vs_misaligned 0.039 vs 0.05 band (22% margin).
  OVERALL TIER: **chain-grade (reconciled; CLAIM, VET-PENDING)** -- all four
    gates now clear: claim(a)=HARD_PASS, legacy(b)=DECOUPLED,
    legacy(c)=fired, regime=SOFT_GRACEFUL (in {HARD_ZERO, SOFT_GRACEFUL}).

## Interpretation (honest, CLAIM/VET-PENDING)

The regime resolves to SOFT_GRACEFUL -- matching the pre-committed
prediction stated in the docstring BEFORE running ("this construction has no
orthogonal-subspace partition between subsystems ... predicts GRACEFUL/SOFT,
brain-parity, NOT a substrate-native hard-zero win"). This is brain-parity
(theta-gamma-style graceful multiplexing, Lisman & Idiart 1995 / Lisman &
Jensen 2013), NOT a Frontier-2 beat-the-brain result -- reported as such, not
oversold. The MIDDLE outcome in v2 was a measurement artifact (a formula bug
plus under-resolved grid/seeds), not a genuine finding of "neither regime
fires" -- v3's correction is a resolution fix, not a re-definition of the
pre-registered bands, and the result is not floor-hugging (real margin on
both bands).
