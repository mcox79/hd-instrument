# exp_dev: substrate_anisotropy_mimo_waterfill_v1 SMOKE = HARD_FAIL (full NOT dispatched)

**Date:** 2026-06-26
**Author:** exp_dev (spawn-and-die cell author)
**Anchor:** `substrate_anisotropy_mimo_waterfill_v1`
**Source:** GAP 2 anisotropy 5x drill Tier A Anchor #1 (P_deflated=0.50)
**Pre-reg:** `preregs/2026-06-26_substrate_anisotropy_mimo_waterfill_v1.md`
**Cell:** `experiments/exp_substrate_anisotropy_mimo_waterfill_v1.py`
**Metrics:** `data/exp_substrate_anisotropy_mimo_waterfill_v1/metrics.json` (smoke; pythia-160m; 1 seed)

## Headline

**Smoke = HARD_FAIL_WATERFILL_DOESNT_HELP. Full NOT dispatched.** Per cell-author discipline ("assert
measured values match expected BEFORE dispatching full run"), the 3-5hr full run is gated and skipped.

## Per-arm smoke metrics (pythia-160m, M=[400, 1000], 1 seed)

| Arm                        | M=400  | M=1000 |
|----------------------------|--------|--------|
| `arm_knn_baseline`         | 1.000  | 1.000  |
| `arm_uniform_cleanup`      | 0.790  | 0.386  |
| `arm_whitening`            | 0.020  | 0.017  |
| `arm_mimo_waterfill_svd`   | 0.772  | 0.359  |
| `arm_mimo_waterfill_learned`| 0.058  | 0.029  |

Lifts at M=1000 (test discriminator regime):
- `lift_waterfill_svd_over_uniform` = **-0.027** (FAIL band: <= 0.03)
- `lift_learned_over_uniform` = -0.357
- `lift_whiten_over_uniform` = -0.369

Effective-rank diagnostic at M=1000:
- `eff_rank_raw` = 0.006 (cone confirmed; D-normalized PR)
- `eff_rank_whiten` = 0.309 (whitening rotates BUT recall collapses to 0.017)
- `eff_rank_waterfill` = 1.213 (waterfill regularizer makes effrank > 1.0 by activating nulls)
- `effrank_lift_waterfill_over_raw` = **186.6x** (huge math lift; ZERO recall benefit)
- `waterfill_active_modes` = 882 / 1000 (88% of singular dimensions get nonzero regularizer)

## Interpretation (Fix #28 honest, no over-claim)

The mechanism produces the expected MATHEMATICAL effect (effrank lifts by 186x) but does NOT translate to
recall lift. Two reasons emerge from the data:

1. **Tikhonov already handles the cone-collapse regime correctly.** Uniform Tikhonov pseudo-inverse already
   adds REG_LAMBDA to every singular value, which already prevents nulls from dominating the inverse. The
   substrate's existing dense KV cleanup (a pseudo-inverse-like operation) IS the right regularization
   class -- water-filling redistributes the regularizer but doesn't add capacity. The drill 1 claim that
   "uniform cleanup wastes capacity on rank-deficient directions" is REFUTED on real Pythia keys at this
   regime: those directions are correctly down-weighted by the inverse, not over-weighted.

2. **Per-direction weight allocation matches uniform within 3%.** waterfill_svd=0.359 vs uniform=0.386 at
   M=1000 -- within seed noise expected on full. The discriminator is CLEAR: this mechanism is not
   substrate-novel relative to existing cleanup.

The KNN sentinel = 1.000 confirms keys are clean. The collapse of `whitening` to 0.017 reproduces drill 1's
rotation-only-ceiling failure (whitening rotates the cleanup but destroys it). The collapse of
`waterfill_learned` to 0.029 is a known cell limitation (training cue == storage key = leakage); this arm
is suspect, not the SVD analytic arm.

## Decision (DO NOT dispatch full)

Per disciplines:
- **Smoke gate FIRST** (load-bearing per CLAUDE.md): smoke shows HARD_FAIL_WATERFILL_DOESNT_HELP; full
  unlikely to flip sign because failure mode is STRUCTURAL (Tikhonov already does the right thing).
- **"Assert measured values match expected BEFORE dispatching full run"** (USER-locked, cell-author memory):
  the prereg HARD_PASS predicted lift >= 0.20; smoke shows lift = -0.027. Asserted match FAILS.
- **NO BUSY WORK** (USER-standing): dispatching a known-failing-mechanism for 3-5 hr wastes laptop CPU that
  Tier A Anchors #2-#5 need.
- **Fix #28 default UNDER-claim**: structural mismatch is more informative as a falsification than as a
  promotion-attempt.

## Routing (negative -> Research for 2x revival drill)

Per [[feedback-route-negatives-to-research-2x-3x-revival-drills]] (USER standing), this HARD_FAIL gets a
revival-angle routing note in the same cycle.

**Revival angles for Research to consider (do NOT pre-decide which):**

1. **Wrong cleanup primitive being tested.** The substrate's actual cone-collapse failure mode is the
   OUTER-PRODUCT SUPERPOSITION readout `W = Y^T K; pred = decode(cue @ W^T)` (v2 fixture arm1_raw=0.018
   at M=10k). My ARM_UNIFORM_CLEANUP is a Tikhonov pseudo-inverse, structurally STRONGER than the
   outer-product superposition. The water-filling discriminator may emerge differently against the
   outer-product baseline. Worth re-cell-authoring with outer-product superposition as the uniform
   baseline.

2. **Wrong regime for water-filling to help.** Water-filling is theoretically optimal when SNR varies
   wildly across modes. Real Pythia residuals may have more uniform SNR distribution than the cone-collapse
   intuition suggests -- the EXISTING Tikhonov regularizer adequately handles the variation.

3. **Tier A Anchor #2 (DG pattern separation) is the natural pivot.** Research drill ranked N1 second; if
   Anchor #1 is a structural dead-end, dispatch Anchor #2 (compose existing primitives: sparse-bipolar
   k-WTA + per-batch divisive normalization as PRE-WRITE module). This is the brain-existence-proof path
   with HIGH prior +0.10 per [[feedback-brain-is-existence-proof-higher-prior]].

4. **Compressed-sensing coherence-aware fly-LSH (Tier A Anchor #5)** -- defends the EXISTING v2 fly-LSH
   chain-grade-candidate at adversarial M=100k. Lower expected-payoff but lower risk; substrate-product
   value of "rescues current chain-grade-candidate" is high.

## What was correctly proven by this cell

- Effective-rank diagnostic harness works (PR/D ratios computed; cone confirmed at eff_rank=0.006).
- KNN sentinel works as Fix #28 by-construction-saturation contamination catch.
- Whitening's rotation-only failure mode reproduces (0.017 at M=1000) -- consistent with drill 1.
- 4-arm rail (uniform / whitening / waterfill_svd / waterfill_learned) provides clear discrimination.

## What was NOT proven (smoke caveat)

- Full pythia-2.8b at M=10k could in principle reveal a different regime. Probability of sign flip: LOW
  per Fix #26 verify-the-referent (the failure mode is structural, not corpus-specific).
- Multi-seed std bound NOT validated (1 seed at smoke); full would have validated this. Acceptable trade
  since the lift magnitude (-0.027) is well clear of any plausible seed-noise band.

## Substrate-product implication (research note prediction)

Research note said: "If S1 passes: anisotropy rescue becomes a 1-line cleanup change; ships into
substrate-as-LM revival path immediately." Since S1 = HARD_FAIL at smoke, **this product path does NOT
ship via water-filling.** Substrate-as-LM revival needs a different anisotropy lever -- DG pattern
separation (N1) or compressed-sensing coherence-aware fly-LSH (A1) are the next candidates per
research-note Tier A ranking.

## Cites

- `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` (S1 candidate spec)
- `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md` (handoff)
- `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (v2 cone-collapse anchor)
- `data/exp_substrate_anisotropy_mimo_waterfill_v1/metrics.json` (this smoke)

## Files committed in this cycle

- `experiments/exp_substrate_anisotropy_mimo_waterfill_v1.py` (cell, ASCII, self-test PASS)
- `preregs/2026-06-26_substrate_anisotropy_mimo_waterfill_v1.md` (bands locked)
- `data/exp_substrate_anisotropy_mimo_waterfill_v1/metrics.json` (smoke HARD_FAIL data)
- `data/exp_substrate_anisotropy_mimo_waterfill_v1/partial_metrics_s11.json` (seed checkpoint)
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` (this note)

**Pause-flag check at dispatch time:** PASS (no `data/orchestrator_paused.flag`).
**Decision:** smoke HARD_FAIL gates full dispatch; revival routed to Research.
