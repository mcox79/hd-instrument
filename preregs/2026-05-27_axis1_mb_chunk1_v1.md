# Pre-registration: axis1_mb_chunk1_v1
**Filed:** 2026-05-27  
**Anchor:** axis1_mb_chunk1_v1  
**Queue:** overnight_queue (GPU)

## Scientific Question
Map phase structure in M x beta grid at N=4096 Kerdock. Chunk 1: M/N in {0.25,0.5,1.0,2.0}.

## Bands
- HARD_PASS: >= 1 metric shows >20% variation across M or beta axis
- HARD_FAIL: all metrics flat (< 2% variation)
- MIDDLE_BAND: partial structure

## Timeout Estimate
smoke_wall_s=0.7, conservative 3600s (140 cells with hysteresis)
