# Pre-registration: substrate_synaptic_homeostasis_global_downscale_v1

**Date:** 2026-06-25
**Anchor name:** substrate_synaptic_homeostasis_global_downscale_v1
**Script:** experiments/exp_substrate_synaptic_homeostasis_global_downscale_v1.py
**Queue:** local_cpu_queue
**Authority:** USER directive 2026-06-25 ("build the 3 missing brain-consolidation primitives. Full auto. NREM replay -> synaptic homeostasis -> cortical schema-extraction")
**Composes with:** substrate_continual_NREM_replay_v1 (replay primitive; pillar 1); a8_continual_writes baseline cliff
**Brain pillar:** 2 of 3 (sleep consolidation; Tononi-Cirelli REM synaptic homeostasis hypothesis)

---

## Scientific question

Tononi-Cirelli synaptic homeostasis hypothesis: during REM sleep, ALL synapses are
globally downscaled by a uniform multiplicative factor. Preserves relative strengths;
prevents runaway potentiation that causes saturation.

Substrate analog: at every N_DOWNSCALE_INTERVAL cycles, multiply ALL W matrix entries
by a uniform factor in (0,1). Question: does periodic global downscaling prevent
saturation in substrate's continual-write regime WITHOUT destroying older facts?

Risk: too-aggressive downscaling forgets old patterns faster than the no-downscale
baseline. The HARD_FAIL band guards this.

## Pre-registered bands (LOCKED via module-init assert)

| Band | Condition |
|------|-----------|
| HARD_PASS_HOMEOSTASIS_PREVENTS_SATURATION | best_downscale_arm.final_forget <= 0.05 AND min_integrity >= 0.95 AND cv <= 0.07 AND strictly better than baseline |
| HARD_PASS_PARTIAL_HOMEOSTASIS_REDUCES_DRIFT | drift_reduction >= 0.20 absolute |
| MIDDLE_BAND | drift_reduction in (0.05, 0.20) |
| HARD_FAIL_DOWNSCALE_DESTROYS_OLDER | any downscale arm has forget > baseline + 0.05 (over-aggressive killed old facts) |

Sacrosanct both ways.

## Arms (4)

| Arm | factor | interval | Mechanism |
|-----|--------|----------|-----------|
| ARM_BASELINE_NO_DOWNSCALE | 1.0 | None | rail |
| ARM_DOWNSCALE_0_99_EVERY_100 | 0.99 | 100 | gentle frequent |
| ARM_DOWNSCALE_0_95_EVERY_500 | 0.95 | 500 | stronger infrequent |
| ARM_DOWNSCALE_0_999_EVERY_50 | 0.999 | 50 | very gentle very frequent |

## Config (FULL)

- N = 4096 (reduced from 8192 per Fix #17 timing; O(N^2) Hopfield)
- N_CYCLES = 2500 (alpha = 0.61; 4.4x Hopfield capacity)
- RECALL_PROBE_M = 100
- CHECKPOINT_INTERVAL = 250
- 3 seeds [11, 13, 19]
- Substrate-only (numpy + Hopfield sign() cleanup; W is outer-product accumulator;
  downscale = multiplicative on W). Zero LLM forward calls.

Timing: smoke wall ~20s. Full extrapolated ~1-2h. Fits local_cpu_queue 4h cap.

## Self-tests (4 formula + bands lock)

1. downscale_W by 0.95 -> all entries 0.95x (numerical)
2. 0.95 downscale once does NOT collapse recall (|delta_acc| < 0.10)
3. 0.5 aggressive downscale at past-cliff alpha is non-NaN (sanity)
4. Bands locked at module init

## Smoke result (script-validity gate; 2026-06-25)

- N=1024, 500 cycles, 1 seed, 4 arms; wall ~20s
- VERDICT: HARD_FAIL_DOWNSCALE_DESTROYS_OLDER at smoke regime (ARM_DOWNSCALE_0_99_EVERY_100
  forget=0.53 vs baseline 0.40); the cell correctly fires its guard band.
- This is an HONEST signal at smoke scale: at N=1024 / 500 cycles, frequent downscaling
  is dominant over the modest baseline drift (alpha=0.49). At full N=8192 / 5000 cycles
  (alpha=0.61, baseline drift larger), downscaling may have room to help.
- Script + bands operational; full run discriminates at 8x N + 10x cycles where the
  saturation-prevention regime is more pronounced.

## Honest scope

REM-homeostasis primitive over 5000 cycles N=8192; 4 arms ((factor, interval) tuples);
forget + cleanup_integrity metrics on first 100 atoms; substrate-only Hopfield.

DOES NOT show: brain-grain REM duration, neuromodulator coupling, downstream task transfer.

## Q-discipline saturation guard

If best_downscale_arm.cv=0.0000 AND drift_reduction at metric-cap, flag as
by-construction-saturation. Skunkworks tiers.
