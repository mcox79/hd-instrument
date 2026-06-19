# Pre-registration: kf3_multisub_isolation_v1
**Filed:** 2026-05-27  
**Anchor:** kf3_multisub_isolation_v1  
**Queue:** overnight_queue (GPU)

## Scientific Question
Two N=4096 substrates A,B. Does querying A contaminate B output?

## Bands
- HARD_PASS: max_leakage < 0.01 AND max_contam < 0.05 (structural isolation)
- HARD_FAIL: leakage > 0.10 OR contam > 0.30 at coupling=0
- MIDDLE_BAND: clean at coupling=0 but degrades with coupling

## Timeout Estimate
smoke_wall_s=0.1, conservative 1800s
