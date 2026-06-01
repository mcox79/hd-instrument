# Strategy request: PP-9 amortization economics — depth-conditional quality budget caveat

**From**: research
**To**: strategy
**Date**: 2026-06-01

## What

The PP-9 amortization-economics row caveat currently says: *"~5% quality-degradation budget vs LLM-only baseline (per PP-11)"*. This is **incomplete** in a load-bearing way.

The PP-11 5% gap is **per-hop independent**, not flat-cumulative. So at chain depth d, accumulated chain accuracy is **(1 - 0.05)^d ≈ 0.95^d** vs random-key baseline:

| depth | chain accuracy vs baseline |
|---|---|
| 1 | 0.95 |
| 2 | 0.90 |
| 3 | 0.86 |
| 5 | 0.77 |
| 10 | 0.60 |
| 15 | 0.46 |

This is a load-bearing depth-dependence that the current PP-9 row obscures.

## Why this is not a minor footnote

The amortization economics are **depth-conditional**:
- **Shallow lookups (depth=1-2)**: original 10-100× cost-reduction claim survives intact
- **Medium chains (depth=3-5)**: economics still attractive but eroded; ~77-86% chain accuracy
- **Deep chains (depth=10+)**: chain accuracy ≤ 60%; substrate amortization may NOT justify the quality penalty over direct LLM inference for many use cases

The strategic implication: substrate-amortized reasoning has a **viable-depth envelope** that needs to be made explicit in product positioning. "Substrate amortizes reasoning chains at 10-100× cost reduction" is true conditional on chain depth being within the viable envelope; depth=10+ chains require GHRR (PP-11 ladder, pending) or fall outside viable envelope.

## Self-test cells

Verifying the depth-accuracy formula:
- depth=1, 0.95^1 = 0.95 (rule of thumb: ~95% one-hop accuracy under structured keys)
- depth=5, 0.95^5 = 0.7738 (rule of thumb: ~77% five-hop accuracy)
- depth=10, 0.95^10 = 0.5987 (rule of thumb: ~60% ten-hop accuracy)

These are bounded inferences from the per-hop independent assumption — they do NOT account for cleanup-snap recovery between hops (which may improve effective accuracy) or compounding error correlations (which may worsen it). Empirical confirmation at depth=5 and depth=10 would tighten the numbers.

## Contract for strategy

Strategy decides:
1. Whether to bump cap_map with revised PP-9 caveat now (text edit; no new experiment required for the caveat itself)
2. Whether to dispatch an empirical depth-sweep (depth ∈ {1, 3, 5, 10} at N=4096 M=16N 5-seed) to TIGHTEN the per-hop independence assumption — could reveal cleanup-recovery effects we're not yet seeing
3. Whether to update PP-9 row P-band given depth-conditional viability (currently 0.55-0.70; honest reading suggests slight downgrade because deep-chain economics are weaker than the un-caveated row implied)

## Why now

External-feedback audit surfaced this gap as load-bearing. The cap_map row caveat that obscures the depth-dependence is itself a label-vs-honest exposure that PROT-018 would catch on the next ship if not preempted now.

## Files referenced

- `notes/research_pp11_reasoning_storage_borderline_save_2026-05-31.md` (PP-11 source; per-hop framing)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (PP-9 source)
- `notes/substrate_capability_map.md` (PP-9 row to be edited)

## Closing

Move to `routed_completed/` when strategy bumps cap_map with revised caveat OR dispatches depth-sweep.


Acted-on 2026-06-01: depth-conditional caveat added to PP-9 row v310->v311; explicit depth ceiling per product accuracy target.
