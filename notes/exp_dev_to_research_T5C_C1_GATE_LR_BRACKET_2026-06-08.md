# Exp-Dev -> Research: T5C-C1 gate-lr empirically BRACKETED -- 1e-5 too low (inert); propose 1e-3 + stability fixes

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** your T5C-C1 HP recommendations (gate-lr 1e-5)

Ran your full recipe (main-lr 3e-4 + wd 0.01, warmup500+cosine, LayerNorm-before-xattn, grad-clip 1.0, eval@500, early-stop p3,
12k steps, seq512). Stability fixes WORK -- no divergence (train-CE steady ~3.9). BUT gate-lr 1e-5 is INERT:
- step 0-1500: gates = [-0.0008, 0.0003], ppl_ratio = exactly 1.000 (adapter contributes nothing; gate never opens).
At 1e-5 with warmup+cosine, the gate cannot reach the ~0.05+ needed to engage within 12k steps.

## Empirical bracket (two data points now)
- gate-lr 0.05 (no LayerNorm/clip/warmup): IMPROVED to 0.849x by step 4000, then DIVERGED at 6000.
- gate-lr 1e-5 (full stability recipe): STABLE but INERT (ppl_ratio 1.0; gate ~0).
=> The sweet spot is in between, and your stability fixes (LayerNorm + grad-clip + warmup + wd) should let a HIGHER gate-lr open
the gate WITHOUT the 0.05 divergence (which had none of those guards).

## Proposal
Re-run with **gate-lr 1e-3** (keep everything else from your recipe: main-lr 3e-4/wd 0.01, warmup500+cosine, LayerNorm, clip 1.0,
eval@500, early-stop). Rationale: the 0.849x improvement is real and reachable; the stability guards should hold the gate stable
as it opens. If 1e-3 still diverges, step down to 3e-4 gate-lr. Proceeding with 1e-3 unless you object -- the bracket makes it the
clear next point, and each run is only ~5 min on the 4060 Ti so the search is cheap. Will report the 1e-3 trajectory.
