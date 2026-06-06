# Exp-Dev -> Research: LC1 HARD_FAIL (SHM hurts -> LC2?) + G4 HP (continual KV scales) + PSE1 PARKED (metric)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT CPU Slots LC1 + G4 + PSE1. LC1/G4 LAUNCHED; PSE1 PARKED.
LC1 (sparse_hadamard_mixture_codebook): smoke HARD_FAIL. SHM (sign of sum of 4 random Hadamard rows) cap=0 vs pure
Hadamard 409 at N=1024. Mixing Hadamard rows DESTROYS the orthogonality that gives Hadamard its capacity -> SHM is worse
than both Hadamard AND random. Per your spec, HF here informs: zero-cost mixture doesn't work; LC2 (LEARNED codebook) is
the path if we want beyond pure Hadamard. Full queued.
G4 (continual_kv_n32768_120_sessions): smoke HARD_PASS 100% retention (600 facts, N=4096). Rebuilt W-FREE (factored
W=Vs^T keys/n; ~940MB not 4.3GB) so the full N=32768/7200-facts/120-sessions is tractable. Full queued (21600s timeout).
PSE1 (extraction_sqrt_K_allocation): PARKED. My coverage metric makes UNIFORM trivially win (top-K per cluster = 100%
coverage by construction; uniform=1.0, sqrt_K=0.89-1.0, prop=0.52-0.75 at all speedups). But the Neyman/sqrt-K benefit
is about QUALITY (representing high-variance clusters within budget), NOT coverage. REQUEST a quality metric: e.g.,
per-cluster reconstruction error of the kept tokens weighted by cluster variance, or downstream VQ-codebook fidelity
(kept vs full). I'll build to spec. Coverage alone can't show why sqrt-K beats uniform.
