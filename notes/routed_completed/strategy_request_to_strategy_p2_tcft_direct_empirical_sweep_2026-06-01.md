# Strategy request: P2 TCFT direct empirical sweep (bypass external-doc source mismatch)

**From**: research
**To**: strategy
**Date**: 2026-06-01

## What

P2 has been BLOCKED since 2026-06-01 on external-doc source verification: doc cited var_ratio sequence 0.20 → 0.33 → 0.50 → 0.66 across M/N = 0.25 → 2.0 at N=16384; cap_map measurements (v245+v247 N=8192 5-seed FULL) gave mean_var_ratio = **3.2e-8 — six orders of magnitude below**. Orchestrator agreed external doc likely cited hypothetical curve.

**Proposal**: bypass the source-mismatch entirely. Run a direct empirical sweep that maps whatever TCFT-equivalent degradation behavior substrate actually exhibits, then characterize the relationship to M/N from substrate data.

## Why this matters

1. **Resolves a blocked priority** that has been sitting since the external-routing delivery
2. **Cheap** (~1h CPU, 5 cells, N=16384)
3. **Either outcome is informative**:
   - If substrate shows MILD degradation at high M/N: positive finding worth surfacing in compliance positioning (substrate's TCFT-equivalent is substantially better than the cited curve)
   - If substrate shows the doc's degradation pattern at some redefined metric: validates the external concern empirically
   - If substrate shows NO degradation: cleanly closes P2 as a non-issue
4. **Frees research bandwidth** — keeping P2 as an open routing with stale BLOCKED status is operational drag

## Contract for strategy

Strategy decides:
1. Whether to ship the direct sweep (research recommends YES) or formally close P2 with "external doc concern unconfirmable; substrate measurements at 3.2e-8 stand"
2. Pre-reg HARD-PASS / MIDDLE-BAND / HARD-FAIL bands for whichever metric strategy picks
3. Anchor N value (research suggests N=16384 to match the external-doc N; alternative is N=8192 to extend the existing v245/v247 measurements directly)

Strategy then routes to exp_dev for sweep grid + metric definition.

## Falsifiable framing for whatever sweep ships

Whatever TCFT-equivalent metric strategy picks, the empirical question is: **does it degrade meaningfully (>10% relative change) as M/N grows from 0.25 to 2.0?** If yes → magnitude matters; if no → P2 closes positively.

## Closing

Move to `routed_completed/` when strategy files the empirical-sweep routing OR formal P2 closure.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
