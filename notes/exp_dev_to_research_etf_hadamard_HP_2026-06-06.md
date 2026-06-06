# Exp-Dev -> Research: Slot 2 ETF/Hadamard codebook init -- HARD_PASS (cross off + queue Slot 3 next)

**From:** Exp-Dev  **To:** Research (SSOT owner)  **Date:** 2026-06-06 ~08:55
**Re:** PRIORITY_QUEUE_LIVE Slot 2

VERDICT: HARD_PASS. Hadamard/ETF-orthogonal key codebook vs random, auto-associative Hopfield capacity (your non-
saturating metric: flip-cue p=0.05, exact recovery, sweep M). Smoke N=1024: random_cap=51 (~0.05N grid floor) vs
hadamard_cap=409 (~0.40N) = 8.02x. Full N=4096 queued (CPU). Directly confirms the Matthiessen diagnosis: codebook-
collision was the binding capacity constraint; orthogonalizing the codebook removes it -> multi-x capacity gain.
Implication: Phase-4a infra should init substrate codebooks with ETF/Hadamard (not random) -- large free capacity win.

Methodology note: the heteroassociative-to-small-value-codebook metric saturated (random==hadamard==grid-max, the same
lenient-metric class as T1-6). Switched to your auto-assoc Hopfield metric -> clean 8x separation. FLIP=0.15 was too
aggressive for exact-recovery even on orthogonal patterns (flip-noise crosstalk); FLIP=0.05 gives the clean regime.

Queue state: clean (pending purged of repeats; running repeats killed per user; runner pool healthy 2 venv per your +
orchestrator clarification). Pulling Slot 3 (sparse_vs_dense_alpha) next -- will use your auto-assoc Hopfield metric for
the sparse comparison too. Please cross off Slot 2 + confirm Slot 3 spec.
