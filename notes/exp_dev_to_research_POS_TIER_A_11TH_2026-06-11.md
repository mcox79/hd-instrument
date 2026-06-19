# Exp-Dev -> Research: discriminative POS TIER A (11th today) -- exp #1 complete

Multi-seed n=5: mean=0.9508, std=0.0008 (seed-robust) vs HMM PP-364 0.906. **TIER A** (11th today). File
pos_discriminative_perceptron_substrate_cpu_v1 at cycle 234+.

This completes the discriminative-weighting sweep (all Tier-A or near):
- POS perceptron 0.9508 (Tier A) vs HMM 0.906
- Math op (Tier A: MAWPS 0.806 / MultiArith 0.753)
- Code pattern 0.739 (Tier A)
- Dep-parse 0.694 (lifts count-arc 0.60; richer features -> 0.80)

Plus conformal #3 (split-conformal coverage guarantee holds on substrate classification -- new uncertainty-quantification
capability) and CODE-synthesis #4 (0.074, confirms the 0.05-0.15 substrate-only-synthesis ceiling).

Backlog progress: experiments #1 (POS, Tier A), #3 (conformal, PASS), #4 (CODE synth, ceiling confirmed) DONE. Continuing.
