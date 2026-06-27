# 2x research drill: hierarchical_3_tier_W revival

**Date:** 2026-06-27
**Trigger:** Skunkworks HONEST_NEG_REGIME_BOUNDED on `hierarchical_3_tier_W_v1` smoke
**Parent cert:** `data/exp_hierarchical_3_tier_W_v1_smoke/metrics.json`
**Source pre-reg:** `preregs/2026-06-27_hierarchical_3_tier_W_v1.md`

## Honest re-read of smoke (verify the referent)

verdict_msg actually reports `lift_over_base = -0.020` (NEGATIVE, not +0.020). Task brief inverted the sign. `3tier_stab_new = 3tier_stab_old = 3tier_no_stab = 2tier = 0.600` exactly — every consolidation-active arm collapses to the identical accuracy. baseline=0.650 (boundary of [0.40,0.65] fairness band). drift ratios: fast/slow=21.5, slow/ultra=316. ultraslow drift = 9.8e-7. transition_slow_to_ultraslow_frac = 0.548 (gate DID fire on ~55% of cycles). N_PULSES=10. 2 seeds.

Bottom line: ultraslow tier RECEIVED ~5-6 stability-gated update opportunities over 10 pulses, but each update was so small (eta_ultra=1e-3 * delta) that the cumulative Frobenius change is 9.8e-7 — three orders of magnitude below slow tier. Ultraslow W is effectively zero. At this budget the cell cannot tell us anything about the 3-tier hypothesis; it can only tell us the gate machinery wires correctly.

## ANGLE A — N_PULSES sweep + ultraslow timescale physics

**Threshold-of-utility analysis.** For ultraslow tier to MATTER (contribute to readout), `||W_ultra @ q||` must exceed read noise. Read noise scales with `1/sqrt(N_DIM) * proto_noise = 1/sqrt(512) * 0.6 = 0.026`. Current ultraslow drift after 10 pulses = 9.8e-7. Linear extrapolation: need ~26,500 pulses to reach noise floor. Even at 1000 pulses ultraslow contribution is ~1e-4, still 260x below noise. Brain-side, synaptic-tag-and-capture cortical consolidation works on ~hours-to-days = 10^4-10^6 spike events; substrate is correctly mimicking the timescale but at 10 pulses we're at minute-zero of the analog.

**Three concrete fixes (Angle A):**

A1. **Adaptive eta_ultraslow schedule.** Start at eta_ultra = 5e-2 (10x slow), decay as `eta_ultra(t) = eta_ultra(0) * exp(-t/tau_ultra)` with tau_ultra = N_PULSES/3. Brain analog: early CLS "consolidation" gain is high before schema stabilizes (Tse 2007 schema-formation curve: fast schema gain in first ~3 events, slow refinement after). This compresses the meaningful update window from ~10^4 pulses down to ~10^2 — testable at N_PULSES=100.

A2. **Raw N_PULSES sweep at fixed eta.** Run N_PULSES ∈ {10, 50, 200, 1000} with eta_ultra=1e-3. Predicted threshold-of-utility: ultraslow tier contributes detectable lift (>0.02 over 2-tier) at N_PULSES ≈ 500. If cell shows ZERO lift even at 1000 pulses, the third-tier mechanism is genuinely null (not just under-budgeted).

A3. **Per-pattern integrated update (not per-pulse).** Replace pulse-counted eta with `eta_ultra_effective = eta_ultra * sum_of_stable_visits(pattern)`. Pattern visited 5 times stably → 5x the update. This decouples ultraslow physics from N_PULSES and lets the tier learn fast IF the stability gate fires consistently. Brain analog: dendritic spine stabilization is proportional to coincidence count, not wall-clock.

## ANGLE B — alternative stability gates

Current gate (sign-stability of slow_history over N=5 cycles) fires at 54.8% — high enough that the gate isn't the limiter; the eta is. But the deeper question: is sign-stability the RIGHT criterion? Bipolar sign on HD vectors is noisy at the per-component level; a single bit-flip from noise breaks the gate without meaningful info loss.

**Three concrete alternatives (Angle B):**

B1. **Variance-stability with bandpass.** Gate fires when `var(slow_W[t-N:t]) < var_threshold AND mean(|slow_W[t-N:t]|) > mag_threshold`. Bandpass: must be stable AND non-trivial in magnitude. Catches the "pattern is robust" semantic without per-bit fragility. Predicted fire rate: ~30-40% (more selective than sign-stability), higher signal-to-noise on what reaches ultraslow.

B2. **Replay-confirmed stability (composes with atom 588 NREM replay).** Gate fires when a replay cycle re-activates a slow-W pattern AND the post-replay slow_W cosine-sim to pre-replay slow_W > 0.85. This is the Tse-Morris "schema integration via re-exposure" criterion. Substrate-native rail: hdlab.continual.replay_cycle already provides the replay primitive. Predicted: fire rate ~20-30%, but each firing is high-confidence schema material.

B3. **Predicted-vs-actual error reduction (free-energy minimization).** Gate fires when adding the pattern to ultraslow REDUCES `predicted_W @ q vs actual q_target` error over the next M cycles by > epsilon. This is hierarchical-attention-style: ultraslow only accepts patterns that demonstrably improve downstream prediction. Risk: requires forward simulation of M cycles per candidate; ~Mx compute cost per gate decision. Brain analog: predictive-coding-driven consolidation (Friston).

## TOP-2 cell candidates for v2

**Candidate 1: `hierarchical_3_tier_W_v2_adaptive_eta`** (combines A1 + A2 partial)

- Discriminator: ARM_THREE_TIER_ADAPTIVE (eta_ultra schedule per A1) shows `old_pattern_acc - 2tier_old >= 0.05` at N_PULSES=100, AND drift_ultra reaches >= 0.1 * drift_slow by pulse-50 (real signal accumulation). N_PULSES sweep 25/50/100/200 as diagnostic. Predicted lift at N=100: 0.04-0.08 over 2-tier baseline.
- CPU-hr: smoke ~30min CPU, full ~2-3hr CPU at 5 seeds, N_DIM=2048. GPU-eligible at N_PULSES=200 (~6hr CPU vs ~1hr GPU per Fix #24 — real GPU usage via torch.cuda.matmul on the per-pulse W update). Recommend remote_cpu first; route GPU only if N_PULSES sweep extends to 1000.
- P_deflated = 0.35 (substrate-native + brain-grounded + smoke proves wiring + adaptive-eta is the smallest substantive change; novel-synthesis cap 0.50, deflated for "just changing a hyperparameter schedule" risk).
- Fairness: baseline MUST stay in [0.40, 0.65] (not the boundary 0.65 from v1 — re-tune proto_noise to land at 0.45-0.55); all 4 arms read same surface (W_fast + W_slow + W_ultra) @ q; probe regime first per Skunkworks discipline.

**Candidate 2: `hierarchical_3_tier_W_v2_replay_gated`** (Angle B2; composes with atom 588)

- Discriminator: ARM_THREE_TIER_REPLAY_GATED vs ARM_THREE_TIER_SIGN_GATED (head-to-head) at N_PULSES=200. Replay-gated arm shows >= 0.05 better old_pattern_acc AND fire-rate <= 35% (selectivity). Failure if replay-gated arm < sign-gated arm OR fire-rate near 100% (gate too permissive).
- CPU-hr: ~3-4hr CPU at 5 seeds; replay calls add ~30% overhead. GPU-eligible at N_PULSES=500+.
- P_deflated = 0.30 (combines two mechanisms — third tier + replay-gating; each individually unproven; brain-grounded but novel composition; deflated harder per "two simultaneous mechanism changes" risk).
- Fairness: baseline in [0.40, 0.65]; gate fire-rate logged as diagnostic arm; sign-gated arm serves as ablation control.

## Sequencing recommendation

Ship Candidate 1 FIRST (smaller change; cleaner discriminator; isolates "is eta_ultra the limiter?" question). If C1 HARD_PASS → 3-tier mechanism is real, retire 2-tier as degenerate. If C1 MIDDLE_BAND → ship C2 (replay-gating). If C1 HARD_FAIL → 3-tier mechanism is genuinely null at substrate scale; retire and feed back to skunkworks for B3-barrier capability map update.
