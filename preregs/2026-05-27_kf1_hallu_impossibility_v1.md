# Pre-registration: kf1_hallu_impossibility_v1

**Filed:** 2026-05-27  
**Anchor:** kf1_hallu_impossibility_v1  
**Queue:** overnight_queue (GPU)

## Scientific Question
Does the Kerdock outer-product substrate exhibit hallucination-impossibility:
out-of-set query confidence < HALLU_THRESHOLD=0.5 across M/N in {0.25,0.5,1.0,2.0,4.0}?

## Hypothesis
Kerdock 4-coset orthogonality ensures near-uniform output for unknown keys.

## Bands
- HARD_PASS: max_confidence < 0.5 in ALL cells ALL seeds
- HARD_FAIL: above_thresh_frac > 0.01 at M<=N (under-capacity)
- MIDDLE_BAND: clean at M<=N but degraded at M>N

## Timeout Estimate
smoke_wall_s=0.3, scale=8*3*1.67*10=400, timeout=ceil(1.5*0.3*400)=180 -> conservative 3600s
