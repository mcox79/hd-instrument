# Pre-registration: kinetic_proofreading_refuse_envelope_smoke_v1

**Date:** 2026-06-23
**Anchor:** kinetic_proofreading_refuse_envelope_smoke_v1
**Queue:** local_cpu_queue
**N:** N_DIM=4096, M=200, N_EVAL=200, N_OOD=50, **Seeds:** [7, 17, 23], **sigmas:** [0.0, 0.5, 1.0, 1.5, 2.0] + sanity-extreme 10.0
**Source:** notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md (Gap 4 substrate-product strategy)

## Scientific question

USER framing (lock-in-amplifier / Hopfield 1974): biological ribosomes hit ~0.001% error despite thermal
noise that would give ~10% single-shot. Mechanism: two sequential energetic gates in coherence; mismatched
tRNAs fall off between steps; error_eff = error_0^2 at cost of accept_rate. Substrate analog: argmax twice
with INDEPENDENT noise realizations + agreement-gate. Does the kinetic-proofreading mechanism, composed
with the already-shipped refuse_gate primitive, give "envelope OR refuse; never confidently wrong" across
production-regime noise sigmas (typical 0.5, stress 1.5)?

## Pre-registered bands

**HARD-PASS (refuse-aware envelope META becomes chain-grade-eligible; ALL three must fire):**
- ARM_KP_2STEP silent_error_rate at sigma=1.5 <= 0.05 (KP doubles the agreement gate; wrong-but-accepted at stress)
- ARM_KP_2STEP recall_at_1_accepted at sigma=0.5 >= 0.80 (substrate still WORKS in typical regime on accepted subset)
- ARM_REFUSE_GATED ood_refuse_rate at sigma=1.5 >= 0.90 (refuse_gate detects OOD honestly under stress)

**MIDDLE_BAND:** 1 or 2 of 3 HARD-PASS gates fire (HF not tripped). Tune-then-revisit (Mondrian per-sigma stratified tau OR widen KP step count to 4-step).

**HARD-FAIL (refuse-aware strategy refuted; substrate must descope to strict sigma<=1.0 envelope):**
- ARM_KP_2STEP silent_error_rate at sigma=1.5 > 0.20 (KP gate insufficient at high noise; confidently-wrong rate too high) OR
- ARM_REFUSE_GATED ood_refuse_rate at sigma=1.5 < 0.50 (tau calibration breaks at high noise; cannot distinguish OOD from in-dist).

**Sanity self-tests (mandatory; FAIL on either => HARD_FAIL with implementation-bug message, NOT mechanism conclusion):**
- sigma=0.0: ALL arms accept_rate >= 0.99 AND recall_at_1_accepted >= 0.99 (clean-cue endpoint by construction).
- sigma=10.0 (sanity-extreme): ARM_REFUSE_GATED accept_rate <= 0.10 (substrate refuses under overwhelming noise; tau-correctness check).

## Calibration rationale

- HARD-PASS bands tighten the parent 5x-deeper drill's bands by adding the KP-2STEP composition on top of REFUSE alone:
  silent_error_rate@1.5 <= 0.05 (was <= 0.05 for REFUSE alone in the source drill; KP further squeezes via error^2 within
  accepted subset). recall_accepted@0.5 >= 0.80 matches the source drill's HP1. ood_refuse@1.5 >= 0.90 matches HP3.
- HARD-FAIL trip-wires: silent_err > 0.20 = source drill's HF1 (substrate confidently wrong); ood_refuse < 0.50 = HF2
  (calibration broken). These are the binary kill-criteria for refuse-aware framing.
- tau calibrated on sigma=0.5 in-dist + OOD random_bipolar score distributions (the typical-noise regime where calibration
  data is realistically available); held-out 0.5-split per refuse_gate.calibrate_refuse_threshold contract.
- OOD generation: random_bipolar(N_DIM) cues — zero codebook overlap by construction; tests substrate's geometric
  confidence-detection (max-cosine on OOD random vector should be ~1/sqrt(N_DIM) under null).
- KP arms (KP_2STEP / KP_3STEP) deliberately ZERO ood_refuse_rate by design: agreement-gate has no OOD-detection signal
  for raw-random OOD cues (single-shot is deterministic on a deterministic cue; both samples pick the same spurious atom).
  KP's role is silent_error_rate compression INSIDE the accepted in-dist subset; OOD detection is REFUSE_GATED's job.
  This is the composition position: KP + REFUSE together cover both axes.

## N-suffix section

Anchor name does NOT include _n<N> suffix because this is the smoke-v1 entry-point cell; production N_DIM=4096 enforced
by RUN_MODE='full' (HDLAB_RUN_MODE env var). Smoke override (HDLAB_RUN_MODE='smoke' or --self-test) drops to N_DIM=1024,
M=50, N_EVAL=50, single seed [7] for ~30-60s validation. If HARD_PASS at this entry-point cell, follow-up cell will
sweep N_DIM in {2048, 4096, 8192, 16384} with the same KP+REFUSE composition to test the envelope-OR-refuse META across
N_DIM (composes with rows 675-678 Shannon-floor evidence across the N_DIM axis).

## Timeout estimate

Smoke wall (N_DIM=1024, M=50, N_EVAL=50, N_OOD=20, 1 seed, 6 sigmas) measured: ~30-60s (matmul-dominated:
N_EVAL * (3 * (M @ N_DIM)) per sigma per arm = ~150 matmuls/sigma/seed at smoke; well under 1s of cb@cue work each).

FULL wall (N_DIM=4096, M=200, N_EVAL=200, N_OOD=50, 3 seeds, 6 sigmas):
- per-sigma matmul cost scales: O(N_EVAL * M * N_DIM) per arm; KP_2STEP and KP_3STEP need additional argmax passes (3x base).
- Smoke total ~ 50 evals * 6 sigmas * (1 + 2 + 1) calls * (50 * 1024) flops ~ 1.2e8 ops/seed -> ~5s/seed numpy.
- Full ~ 200 evals * 6 sigmas * 4 arm-calls * (200 * 4096) flops ~ 3.9e9 ops/seed -> ~150s/seed numpy.
- 3 seeds: ~450s base. Add OOD cal (~50 evals * 4096 * 200) ~ +60s/seed = +180s. Total ~ 630s.
- formula: ceil(1.5 * 60 * (4096/1024)^1.0 * (3/1)) = ceil(1.5 * 60 * 4 * 3) = ceil(1080) = 1080
- TIMEOUT chosen: **1800s** (30 min) — generous laptop CPU headroom; covers smoke gate + full run + cleanup. Under PROT-019 floor 600s + well under cap 14400s.
- timeout_s = 1800

## Routing

- local_cpu_queue (laptop CPU; numpy-only; ~10-15min target wall per USER spec).
- Composition rationale: USER framed as "smoke-only ~10min CPU" entry-point; no GPU need at this scale.
- Cell-author smoke gate runs LOCALLY before queue dispatch (per Fix #17 + cell-author smoke discipline).
