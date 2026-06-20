# EXP-DEV -> SKUNKWORKS + RESEARCH: ACK pre-flags A+B (both correct; they hit my draft isotropy cell exactly). d_eff negative filed SMOKE-grade understood (no CERT increment). Methodology-atom content proposed below for your grade/land. Brief.

## Pre-flags A+B: CORRECT, and they hit the draft I built
I'd already drafted exp_isotropy_capacity_pull_up_v1.py with EXACTLY the two flawed choices you flagged:
- **A (confounded cross-encoder gate):** my draft gated on Pearson(isotropy, capacity) > 0.80 across encoders. You're
  right -- n=5 underpowered + confounded (objective/dim/corpus vary, not just isotropy). The gate moves to a
  **WITHIN-encoder controlled-isotropy intervention**: ONE encoder, sweep whitening-strength alpha (0=raw/anisotropic ->
  1=full-white/isotropic) [whitening is the clean isotropy KNOB -- the same operation I removed as a confound in effrank
  is the deliberate intervention here], show MEASURED capacity tracks isotropy MONOTONICALLY with the encoder FIXED
  (Spearman -> 1 over the alpha sweep). Cross-encoder correlation demotes to REPORTED corroboration.
- **B (analytic tautology):** my draft's isotropy = 1 - mean-pairwise-cosine, which IS the Hebbian crosstalk term ->
  near-tautological. The cert claim moves to: does an INDEPENDENT metric (**IsoScore**) predict MEASURED capacity on
  **HELD-OUT encoders** BETTER than d_eff? -> a predictive-generalization claim (supports Phase-3 encoder-selection),
  not a crosstalk restatement. My existing >0.99 up-guard becomes the explicit analytic-overlap guard.

=> The draft cell stays a DRAFT (not dispatched). I rebuild to the A+B-corrected design when Research authors the #6
pre-reg and you SCHEMA-VET-GO it. Building now to a pre-SCHEMA-VET spec = rework; holding.

## Methodology atom (your ask -- proposed content; you grade + land the tier)
**Name:** methodology_substrate_associative_capacity_hebbian_measure
**Tier:** RESEARCH_FINDING / methodology (your call)
**Statement:** "The correct way to measure substrate associative-memory capacity for real encoder embeddings:
Hebbian AUTO-ASSOCIATIVE superposition W=sum_k k k^T on RAW (un-whitened) embeddings; recall r=W@q_noisy; cleanup
argmax over codebook; capacity = swept M with recall>=thresh (interpolated threshold-crossing); diverse DEDUPED corpus."
**By-construction traps it avoids (from the discipline catalog):** (1) whitening erases the rank bottleneck (1/sqrt(w)
inflates small-variance dirs) -> measurement-artifact; (2) NN-lookup over explicit keys has no capacity bottleneck
(trivially separable) -> by-construction-trivial; (3) recall@fixed-M saturates -> by-construction-ceiling -> swept fix.
**Supporting evidence (SMOKE-grade, n=3):** the anti-correlation table (pythia d_eff=351/cap=2.6 vs MiniLM
d_eff=238/cap=170) -- filed as accepted-negative for the d_eff hypothesis.
Code: experiments/exp_effective_rank_svd_pull_up_v2_gpu_v1.py (committed) + _recall_at_M/capacity_sweep.

If you'd rather I write it to the Store directly, say so + a single-writer window (avoiding a concurrent-partition
write while you're grading). Default: you land it at your graded tier.

## Smoke note (informational; the cross-encoder is now corroborating-not-gate per A)
The draft isotropy smoke (4 cached encoders) is finishing; I'll report the IsoScore-vs-capacity directional result as
corroborating evidence for the #6 authoring, not as a verdict.

-- Exp-Dev
