# Wave 14.B Pre-Registration

Pre-registered 2026-05-18. Hypothesis, setup, diagnostic gates, and falsification criterion fixed before running.

## Hypothesis

A resonator network can decompose a 2-element HDC bundle
`c = a ⊙ p1 + b ⊙ p2` into its constituent codebook atoms `(a, b)`
without knowing either, with recovery rate ≥ 50% under the
configuration below.

This is the HDC-native version of the Wave 14.A shuffle Hopf
deconcatenation idea. Instead of literal concatenation (which grows
dimension and is not standard HDC), we use Hadamard binding with
frozen positional codes — a standard HDC primitive — and ask the
resonator to recover both atoms via alternating projection.

## Setup (frozen before any runs)

- N = 4096 (vector dimensionality)
- K = 32 (codebook size)
- M = 2 (bundle size)
- Substrate: bipolar ±1 random vectors
- Binding: elementwise product (Hadamard)
- Bundling: integer addition (no clip, no normalization)
- Cleanup: codebook projection with soft attention (softmax over scores)
- Restarts per query: 8
- Trials per gate: 200
- Seed: 17 (with per-trial offsets)
- Convergence: max 100 resonator iterations or score change < 1e-6

Rationale for K = 32: empirical resonator phase transition for
M-element bundles is approximately K_crit ≈ sqrt(N / (M · const)).
For M=2 and N=4096, the threshold lies around 40-50. K=32 sits
comfortably below it (Frady-Kent 2020 operating regime).

## Information-theoretic check

For random bipolar atoms `a, b ∈ {-1,+1}^N` and random bipolar
positions `p1, p2 ∈ {-1,+1}^N`:

- `a ⊙ p1` and `b ⊙ p2` are themselves bipolar (component product
  of bipolars is bipolar).
- `c = a ⊙ p1 + b ⊙ p2` lives in `{-2, 0, +2}^N`.
- The number of distinct codebook pairs is `K × K = 1024`. The
  information content of c needed to identify the pair is
  `log2(1024) = 10 bits`.
- The component-wise entropy of c is approximately 1.5 bits per
  coordinate (3 levels, biased toward 0). Total information
  capacity of c is roughly `N × 1.5 = 6144 bits`, vastly exceeding
  the 10 bits required.
- Collision probability between two distinct pairs `(a,b) ≠ (a',b')`:
  the expected cosine overlap between their c-vectors is
  `(<a,a'> + <b,b'>) / (2N)`, which has standard deviation
  `O(1/sqrt(N)) ≈ 0.016` for N=4096. The probability that a wrong
  pair gives a c-vector indistinguishable from the right one (above
  noise) is exponentially small in N.

**Conclusion:** the information IS in c. The question is purely
algorithmic — can the resonator find it?

## Diagnostic gates (sequential, hard pass/fail)

Three gates run in order. Each must pass before the next is run.
If any gate fails, the program halts and reports which gate failed
and why. We do not proceed to the main test until Gates 1 and 2
both pass.

### Gate 1 — Binding invertibility (100% expected)

Given ground-truth `a`, compute `b̂ = (c - a ⊙ p1) ⊙ p2` and verify
that the nearest-codebook projection of `b̂` matches the true `b`
on 100% of trials.

**Pass condition:** 100% recovery (this is a deterministic
algebraic check on bipolars — anything less means the binding/
unbinding implementation is wrong).

### Gate 2 — Oracle resonator (≥ 95% expected)

Run the resonator with a HARD codebook projection (snap to nearest
codebook atom at every cleanup step). 200 trials, 8 restarts each.
The algorithm with perfect cleanup must converge on nearly all
trials.

**Pass condition:** ≥ 95% recovery (both atoms exactly correct).

A failure here means the alternating projection itself doesn't
converge for our setup — independent of any cleanup softness.

### Gate 3 — Full system (pre-registered: ≥ 50% to pass)

Standard resonator with SOFT codebook projection (softmax-weighted
superposition; temperature schedule starting at beta=1.0,
multiplied by 1.2 each iteration up to beta=20). 8 restarts.
200 trials.

**Pass condition (pre-registered):** ≥ 50% recovery (both atoms
exactly correct).

## Falsification criterion

**Gate 3 < 50% over 200 trials → HYPOTHESIS REJECTED.**

If rejected, do not proceed to:
- Longer bundles (M > 2)
- Larger codebooks (K > 32)
- Continual-learning combination
- Any downstream application

Instead, return to "which binding operation is right for HDC
decomposition?" — the resonator + Hadamard primitive will have
been ruled out and we need a different substrate choice.

If accepted (Gate 3 ≥ 50%), the next experiments are:
1. Sweep M ∈ {3, 4, 5} at K=32, N=4096 — find recovery curve.
2. Sweep K ∈ {16, 32, 64, 128} at M=2, N=4096 — find phase boundary.
3. Apply to continual-learning pool: decompose stored episode
   bundles into (atom, slot) parts and mine recurring components.

## What this experiment does NOT test

- Performance on actual byte-LM perplexity. That is a separate
  later experiment.
- Recovery under noise (atoms perturbed before bundling).
- Recovery when the bundle includes non-codebook contamination.
- Non-orthogonal codebooks.

These are deliberate scope cuts. Establish the cleanest base case
first; expand only after it works.

## Diagnostic ablations bundled into the script

The script `experiments/exp_wave14b_resonator_diagnostics.py`
prints, in this order:

1. Configuration block (N, K, M, restarts, seed).
2. Information-theoretic sanity print (mean overlap of c with c'
   for distinct pairs vs. identical pairs — should be O(1/sqrt(N))
   vs. 1.0).
3. Gate 1 result with halt-on-fail.
4. Gate 2 result with halt-on-fail.
5. Gate 3 result with formal pre-registered pass/fail printed.
6. metrics.json with all gate scores and per-trial outcomes for
   audit.

This makes the gate sequence visible and auditable rather than
hidden inside a results table.
