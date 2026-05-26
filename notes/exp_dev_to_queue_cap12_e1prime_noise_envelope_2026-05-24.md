# exp_dev → queue: Cap 12 E1' noise-envelope sweep (sub-probe)

**Date**: 2026-05-24
**Driver**: verdict_handler pre-registered follow-up to E1 MIDDLE-BAND verdict
**Pause flag**: ABSENT (cleared by user before dispatch)

## Anchor

Single anchor: noise-envelope sweep at fixed tau=0.20, sweeping eta to identify eta_critical (the noise level at which Cap 12 routing accuracy drops below 4/5). Pre-registered HARD PASS / HARD FAIL / MIDDLE BAND per [[feedback-envelope-expansion-fail-bands]].

## Queue entries (Schema B: markdown table)

| queue            | name                                   | script                                                        | prereg                                                              | timeout(s) |
|------------------|----------------------------------------|---------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_mp_ks_noise_envelope_sweep_v1   | experiments/exp_wave14_mp_ks_noise_envelope_sweep_v1.py       | preregs/2026-05-24_wave14_mp_ks_noise_envelope_sweep_v1.md          | 3600       |

## Smoke

- 13/13 self-tests passed locally.
- 2 codebooks × 2 etas × 1 seed at N=64; produced valid metrics.json; sub-second wallclock.
- Remote `--self-test` gate passed in 7.5s; queue_add returned OK with queue pending now=1.

## Notes

- Inherits machinery from `exp_wave14_mp_ks_noisy_substrate_v1.py` (signflip noise, MP-KS, AMP/VAMP loops, codebook builders).
- Different sweep axis: fix tau=0.20, sweep eta ∈ {0.0, 0.01, 0.025, 0.05, 0.075, 0.10}.
- 5 codebooks × 5 seeds × 6 eta values = 150 SVD/AMP/VAMP runs at N=1024. ETA ~30-45 min on remote CPU (~2× E1 cost).
