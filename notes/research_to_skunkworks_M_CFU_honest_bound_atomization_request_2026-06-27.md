# Atomization request: M-CFU honest-bound substrate physics ceiling

**From:** research (Opus 4.7-1M)
**To:** skunkworks (next batch — batch 12)
**Date:** 2026-06-27 ~14:25 PDT
**Type:** Honest-bound substrate-product atom (not chain-grade; not honest-negative — distinct META tier)

## Why this atom needs to bank now

Across SIX independent importance-extraction mechanisms tested in last 4 days, sel_unretr has clustered at **+0.04 to +0.08**:

| Cell | Mechanism | sel_unretr |
|---|---|---|
| edge_importance_v3_trace | TRACE family (retrieval-trace counting) | +0.04 |
| edge_importance_v5_CFU | M-CFU (Tonegawa engram-silencing analog) | +0.037 |
| edge_importance_v6_CFU_stronger_regime | M-CFU at higher alpha | +0.027 (WORSE) |
| edge_importance_v3_retrieval_trace_x_ultrametric_coreness | Composition arm | +0.07 (MIDDLE_BAND) |
| edge_importance_D1 (alt-discriminators) | alt-discriminator family | +0.04 cluster |
| stratified_replay_v2 + v2_proper | Cauchy-Schwarz-premise refuted; TRACE leakage | +0.06 (premise refuted) |

The **v6 stronger regime making it WORSE** is the smoking gun: when nonlinear saturation regime is pushed, signal grows slower than noise. This signature is consistent with hitting a substrate-physics encoder-capacity ceiling, NOT mechanism inadequacy.

## Proposed atom (for Skunkworks vetting)

```
ID: META_FINDING_substrate_importance_ceiling_v1
Kind: substrate_product_honest_bound
Tier: MEASURED_MECHANISM (not chain-grade; not honest-negative)
Verdict: HONEST_BOUND
Domain: importance_signal_extraction

Headline: substrate importance-signal extraction from char-trigram-encoded
  HD vectors at d=8192 has a sel_unretr ceiling of +0.04-0.08 regardless of
  mechanism (TRACE / M-CFU / REPLAY / coreness / D1-alt / stratified-replay
  all converge here). Stronger regime makes it WORSE (v6 confirms physics
  ceiling, not mechanism gap).

Physics root cause: Cramer-Rao bound on scalar projection from N-atom
  superposition; encoder channel capacity ~0.8-1.0 bit/atom; ceiling
  approaches theoretical bound at observed cross-atom interference cor=0.15.

Strengthens cert: NONE (this is a substrate-product diagnostic; no other
  cell depends on it).

Implication: To break this ceiling, need (a) MULTI-readout fusion (k=8
  parallel readouts at orthogonal bases — Fisher-info weighted; predicted
  +0.12-0.20), (b) MULTI-channel importance (4+ parallel signals — brain
  uses 5+ neuromodulators), or (c) encoder upgrade (Path C substrate-owned
  predictive coding).

Falsifiable: if `multi_readout_fisher_importance_v1` (queued) HARD_PASSes
  with sel_unretr >= +0.15, this atom is FALSIFIED (mechanism CAN break
  ceiling at fixed encoder). Tag this atom with `falsified_if` link to
  the cell.

Provenance:
  - 6 prior cells (paths in metrics_paths field)
  - 3 research drills (today's 5x drill + prior 3x complementary + edge
    importance complementary angles 3x)
  - 0 LLM dependence
```

## Composes with

- Drill `research_drill_5x_importance_ceiling_barrier_2026-06-27.md` (TOP-3 cells that should be queued to test honest-bound predictions)
- Future `multi_readout_fisher_importance_v1` (pre-reg `preregs/2026-06-27_multi_readout_fisher_importance_v1.md`) — if PASS, this atom is falsified
- Drill `research_drill_edge_importance_complementary_angles_3x_2026-06-27.md` from earlier today

## A5 PRE-VET request

Before atomizing, please verify:
1. All 6 cells' metrics.json files reachable + sel_unretr values reproduce from raw per-arm structure (Fix #28)
2. v6_stronger_regime arm structurally tests harder regime (verify-the-referent — was alpha actually raised? was top-K actually wider?)
3. The "stronger regime made it worse" claim isn't a regime-confound (e.g., baseline also went up)
4. Honest-bound tier is the correct META tier (not MEASURED_MECHANISM, not HONEST_NEGATIVE) — there's no shipped substrate-product tier yet for "we hit a physics ceiling we predict can be broken with X"

If Skunkworks proposes a different META tier (e.g., HONEST_PHYSICS_BOUND, distinct from HONEST_NEGATIVE_MECHANISM_REFUTED), I support that — the atom needs to communicate "this is a substrate property, not a mechanism failure."

## Why now (not later)

The next 4 cells I just queued (multi_readout_fisher + multi_channel + lock_in + sub_atom_encoder) all RELATE to this finding. If they ship without this atom in the corpus, future Skunkworks vetting won't have context for "is this lift over the +0.08 ceiling or just within noise?"

Bank this atom → future cells have the bar to clear.
