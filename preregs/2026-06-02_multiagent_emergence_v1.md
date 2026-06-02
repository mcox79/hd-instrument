# Prereg: multiagent_emergence_v1 (BLOCKED -- smoke HARD_FAIL, reroute to Strategy)

## Scientific question
Multiagent emergent coordination via shared substrate without explicit consensus.

## Pre-registered thresholds
- HARD-PASS: All of A (cos_joint >= 0.70), B (contamination <= 0.20), C (improvement >= 0.10).
- HARD-FAIL: HF-A (cos_joint < 0.35) OR HF-B (contamination > 0.50).
- MIDDLE: 2/3 cells.

## Smoke result
HARD_FAIL: cos_joint=0.484 (below HP=0.70, above HF=0.35). contamination=0.018 (excellent, HP).
improvement=-0.008 (negative, below HP=0.10).
Cell B passes (contamination=0.018). Cells A and C fail.
BLOCKED per suspicious-result gate: 2/3 cells fail. Not a HARD_FAIL condition (cos>HF=0.35).
This is a DESIGN_FAULT: LAMBDA_SHARED=0.5 dilutes the shared signal too much.
Rescue: increase LAMBDA_SHARED to 0.7 or use direct encoding of shared component.
