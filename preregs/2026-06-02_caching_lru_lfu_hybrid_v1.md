# Prereg: caching_lru_lfu_hybrid_v1

## Scientific question
Caching-Policy Tier 2: LRU+LFU hybrid score correlation with substrate eigenvalue score.

## Pre-registered thresholds
- HARD-PASS: All of A (rho_hybrid >= 0.70), B (rho_hybrid > rho_lru + 0.05), C (n_pos_sign >= 3/5).
- HARD-FAIL: HF-A (rho_hybrid <= 0.30) OR HF-C (n_pos_sign <= 1).
- MIDDLE: 2/3 cells.

## Calibration note
First LRU+LFU hybrid substrate measurement. Bands +-50% per calibration-probe policy.

## Smoke result
HARD_FAIL on cell B: rho_hybrid=0.806 but rho_lru=0.806 (hybrid == pure LRU).
Cell A passes (rho >= 0.70). Cell C passes (both seeds positive).
Scientific interpretation: substrate eigenvalue score correlates well with recency (LRU)
but adding frequency weight does NOT improve correlation -- the frequency information
is NOT additively encoded in the substrate score. This is a boundary result.
Ship to FULL to confirm with 5 seeds whether B=0 is consistent (GENUINE MIDDLE_BAND result).

## Timeout estimate
Smoke wall: 0.3s, N=512->1024, seeds=2->5. Linear.
timeout = ceil(1.5 * 0.3 * 2 * 2.5) = ceil(2.25) = 3s.
timeout=120s (overhead dominated).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
