# Pre-registration: pb3_critical_slowing_v1
**Filed:** 2026-05-27  
**Anchor:** pb3_critical_slowing_v1  
**Queue:** remote_cpu_queue (CPU)
**NOTE: >2h run -- flagged for visibility**

## Scientific Question
After corpus corruption, does recovery time (tau_10pct) peak near optimal beta=8?
Phase-boundary signature = critical slowing down at operating point.

## Bands
- HARD_PASS: tau_recovery(beta=8) >= 1.5x tau_recovery(other betas)
- HARD_FAIL: tau_recovery constant across all betas (ratio <= 1.2)
- MIDDLE_BAND: varies but < 1.5x ratio

## Timeout Estimate
smoke_wall_s=3.6, scale ~144, timeout=ceil(1.5*3.6*144)=778 -> 7200s conservative (>2h flag)
