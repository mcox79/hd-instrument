# Pool Size and the Inverted-U: Theory Synthesis

Drafted 2026-05-19 from unbiased pool-size theory survey. Empirical
observation: BWT improved with pool size up to P=4096, then DEGRADED
at P=16384. The math has a clean explanation.

## The headline result

**Softmax-weighted retrieval has an inverted-U in pool size P with
sweet spot at P* ≈ exp(mu_S² / 2·sigma_D²)** when beta is fixed and
the fraction of useful entries is constant.

Mechanism: extreme-value statistics. The maximum distractor logit
grows as `sigma_D · sqrt(2·ln(P-k))`. Once P passes the threshold
where max_distractor_logit catches mu_S, retrieval CE grows
logarithmically in P.

This is **softmax-specific** — hard nearest-neighbor retrieval is
monotone non-decreasing in P (argmax invariant to worse entries).
The inverted-U is a softmax artifact, fixable by temperature
scheduling.

## What the math predicts for our setup

Per the survey's `P* ≈ exp(mu_S² / 2·sigma_D²)` formula:
- mu_S ≈ 4 (cosine ~0.4 times beta=10), sigma_D ≈ 1: predicts
  P* ≈ exp(8) ≈ 3000 — "suggestively close" to our 4096 observation.
  The form matches; exact value depends on measured mu_S, sigma_D.

The survey explicitly flags this as "numerologically consistent
but should be verified with measured kernel statistics."

## Four candidate explanations for our P=4096 sweet spot

(a) **Softmax distractor bias** (the survey's primary explanation):
    fixed beta becomes too low as P grows; max-distractor catches
    signal. Predicted by Veličković et al. 2024 "Softmax is not Enough."

(b) **FIFO eviction effect**: at large P, buffer can hold more new-
    domain entries during continual training, diluting old-domain
    content.

(c) **Capacity matching**: P* equals the intrinsic complexity of the
    old domain (clean buffer assumption, GEM/A-GEM bounds).

(d) **Compute confound or temperature mis-calibration** at fixed beta.

The candidates can be discriminated. Survey's recommended diagnostic:

> "Re-run P=16384 with beta scaled by sqrt(ln 16384 / ln 4096) ≈ 1.08x.
> If BWT recovers, you've isolated (a). If not, vary the buffer
> composition next."

## Predicted beta scaling for our pool sizes

Optimal beta scales as `sqrt(log P)`:
- P=256:   sqrt(log 256)   = 2.36
- P=1024:  sqrt(log 1024)  = 2.63
- P=4096:  sqrt(log 4096)  = 2.88
- P=16384: sqrt(log 16384) = 3.11

Normalized so beta(P=1024) = 8 (our default):
- P=256:   beta = 7.18
- P=1024:  beta = 8.00 (baseline)
- P=4096:  beta = 8.78
- P=16384: beta = 9.46

These are small scalings. The diagnostic experiment will tell us
whether they're sufficient.

## Diagnostic experiment design

**Wave 14.B Pool-size sweep with annealed BETA_RETRIEVAL** — same as
`exp_wave14b_phase_b2_pool_size_sweep.py` but BETA_RETRIEVAL scales
with sqrt(log P) for each pool size. BYTE_BETA stays at 16.

**Pre-registered prediction:**
- If softmax bias is the cause: BWT at P=16384 should recover to
  match or beat P=4096.
- If FIFO is the cause: beta scaling won't help. BWT remains worse.
- If capacity matching: beta scaling won't help. BWT remains worse.

## Why this matters for the product

The agent-memory deployment target is pools of 1M+ entries (per the
"persistent cognitive layer" vision). If the math says fixed-beta
softmax retrieval has an inverted-U at P ≈ 3000-5000, then production
deployment REQUIRES one of:
- Temperature scheduling: beta = beta_0 · sqrt(log P)
- Hard nearest-neighbor retrieval (gives up the soft-blend aggregation
  but recovers monotone-in-P quality)
- Bandwidth/sigma_D engineering (sharper kernel)

This is a real engineering constraint we'd need to handle. The
diagnostic experiment tells us if it's tractable with simple scaling.

## Other directly-relevant 2024-26 work

- **Veličković et al. 2024** "Softmax is not Enough (for Sharp Size
  Generalisation)" — the core math result for our phenomenon.
- **Fang et al. 2024** "Scaling Laws for Dense Retrieval" —
  empirical confirmation that corpus-size scaling saturates without
  re-calibration.
- **Li et al. 2025** "Retrieval Robustness of LLMs" — degradation
  past small k, steeper for high-recall retrievers.
- **Wu et al. 2025** "Heads collapse, features stay" — large
  buffers needed for head re-calibration, small ones preserve features.

## Implementation status

Diagnostic experiment script: building now as
`exp_wave14b_phase_b2_pool_size_sweep_annealed.py`. Same architecture
as the original sweep + temperature schedule. Will queue on GPU
watchdog. Expected runtime ~8 min (4 pool sizes × ~2 min each).
