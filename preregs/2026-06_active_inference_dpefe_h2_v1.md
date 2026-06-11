# Pre-registration: active_inference_dpefe_h2_cpu_v1
**Date:** 2026-06-11  **Anchor:** active_inference_dpefe_h2_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192  **Seeds:** 5
## Scientific question
Does DPEFE H=2 (horizon-2 free-energy Bellman lookahead) + a goal-distance gamma gate close the active_inference goal_reach gap
(E1+E2 was MIDDLE: error_drop 70%, goal_reach 0.63)? Per Research drill 1 (P=0.62, <1hr).
## Pre-registered bands
HARD-PASS error_drop > 30% AND goal_reach > 0.70. STRONG error_drop>50% AND goal_reach>0.85. MIDDLE one. HARD-FAIL error_drop<=20% OR goal_reach<=0.60.
## Calibration rationale
H=2 lookahead lets the agent see past the comfort basin (single-step E1 stalled); the goal-distance gamma gate (gamma ~ goal_dist)
cuts exploration near the goal so the agent settles within 0.1 (fixing the oscillation that capped goal_reach at 0.63). n=5 seeds.
## N-suffix section
N=8192 FPE; numpy CPU, ~1 min. Multi-seed n=5.
