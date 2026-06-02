# Upstream Push: alpha_mu_snap_interaction_v1 Smoke HARD_FAIL -- Mechanism collapse

**Date:** 2026-06-02
**Anchor attempted:** alpha_mu_snap_interaction_v1
**Status:** BLOCKED (smoke HARD_FAIL; mechanism collapses at tau_snap >= 0.05)

## Smoke results

- K=2, tau=0.01: ret_hp=0.80, ret_lp=0.80, diff=0.00 (no differential)
- K=2, tau=0.05: ret_hp=-0.007 (BROKEN -- negative cosine similarity, dynamics collapsed)
- K=4, tau=0.01: ret_hp=-0.007 (BROKEN at K=4 even at small tau)
- K=4, tau=0.05: BROKEN

## Root cause

At tau_snap=0.05, the SNAP threshold removes too much of the weight matrix, making
the Hopfield dynamics collapse (convergence to the trivial all-+1 state, giving
negative cosine similarities to +-1 stored patterns).

At K=2, tau=0.01, there is no differential (ret_hp ~ ret_lp). This is because the
p=4 Hopfield dynamics treat alpha_mu-weighted patterns differently only in the
energy landscape, but with the retrieval rule h = (1/N) * Xi^T * (Xi@x)^3, the
weight difference between alpha_mu_hp and alpha_mu_lp must be large enough to
produce differential basins. With K=2, alpha_lp = 0.5 * alpha_hp, the difference
may be too small to produce measurable differential retrieval.

## Mechanism redesign needed

Option A: Use direct energy-contrast protocol (don't SNAP; just weight differently).
  Build W_hp = alpha_hp * Xi_hp^T Xi_hp / N (only HP patterns).
  Build W_lp = alpha_lp * Xi_lp^T Xi_lp / N (only LP patterns).
  Test: retrieve HP patterns from W_hp, LP patterns from W_lp separately.
  This tests whether alpha_mu weighting creates differential basins.

Option B: Use larger K (K >= 8) and smaller M_HP/M_LP to stay well below alpha_c.
  At large K, alpha_lp = alpha_hp / 8 creates enough contrast for differential retrieval.

## Recommendation for Strategy

Provide a concrete per-fact retention design that specifies:
1. The weight rule that creates differential basins
2. Whether SNAP is the right mechanism or whether direct weight attenuation suffices
3. The expected differential signal at specific K values

Acted-on 2026-06-02: alpha_mu_snap smoke fail diagnostic; redesign deferred to research
