# Pre-registration: pb1_susceptibility_v1
**Filed:** 2026-05-27  
**Anchor:** pb1_susceptibility_v1  
**Queue:** remote_cpu_queue (CPU)

## Scientific Question
At N=4096 byte-LM substrate, does BPC have an interior minimum at beta=BETA_TRAIN=8?
Does training duration affect susceptibility?

## Bands
- HARD_PASS: susc_beta > 0.1 AND BPC has interior min in >= 1/2 seeds
- HARD_FAIL: BPC monotone, no interior min, susc_epoch < 0.01
- MIDDLE_BAND: partial

## Timeout Estimate
smoke_wall_s=2.0, conservative 1800s
