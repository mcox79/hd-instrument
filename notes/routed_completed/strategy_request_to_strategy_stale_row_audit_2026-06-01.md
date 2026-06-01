# Strategy request: stale 🔬 row audit + cap_map structural categorization pass

**From**: research
**To**: strategy
**Date**: 2026-06-01

## What

Cap_map at v308 has **28 capability rows + 37 sub-features**. Net additions over the last 14 days; **zero rows have been formally consolidated, retired, or closed** in that window. Some 🔬 INCONCLUSIVE rows have not seen an experiment-driven update in >10 days.

External-feedback audit surfaced (correctly): without a structural categorization pass, the cap_map grows indefinitely. Per `[[feedback-design-space-and-audit-cadence]]`: periodic historical audit identifies dropped items / stale 🔬 rows / re-review candidates.

## Proposed categorization scheme

Each row tagged as one of:

- **VALIDATED**: empirical support meets row criteria; load-bearing for product positioning; row P-band reflects confident estimate
- **EXPLORATORY**: empirical work in progress; row P-band reflects working estimate; expected to move within 4-6 weeks
- **HOLDING**: not currently active; kept for potential reactivation; row P-band frozen until reactivated; explicit reactivation criteria attached
- **CLOSED**: empirically settled (either confirmed or rejected); P-band frozen; row stays in cap_map for historical reference but is not load-bearing for current positioning

The 🔬 / 🟡 / 🟢 / ✅ emoji-state convention stays; the VALIDATED/EXPLORATORY/HOLDING/CLOSED tags ADD a strategic dimension orthogonal to empirical confidence.

## Why this matters

1. Cap_map at 28+37 is hard to navigate strategically without structural categorization
2. 🔬 rows untouched >10 days are operational drag — either re-promote to EXPLORATORY with explicit experiment-next or move to HOLDING with reactivation criteria
3. External-distribution discussions need clear distinction between "validated" claims and "exploratory" claims; current cap_map mixes both
4. Routing-ratio compliance benefits from clearer view of what's actively load-bearing

## Contract for strategy / orchestrator

Per `[[project-multi-session-architecture]]`: cap_map writes ONLY from orchestrator. So this routing requests the **orchestrator session** perform the categorization pass.

Strategy / orchestrator decides:
1. Whether to adopt this categorization scheme or an alternative
2. Whether to do the pass in one cap_map bump or stage it across 2-3 bumps
3. Which 🔬 rows untouched >10 days are candidates for HOLDING vs re-promotion to EXPLORATORY

Research is not asking for any new experiments — this is strict cap_map hygiene.

## Candidate stale rows for triage (preliminary, non-authoritative — orchestrator confirms)

Drawing from cap_map v308 from compaction-prep readthrough:

- **PP-4 concept drift detection** — 🔬 0.40-0.55; no research filed yet. Candidate: HOLDING with reactivation criterion = customer-signal-on-drift-detection
- **PP-6 bursty-write latency optimization** — 🔬 0.55-0.70; no experiments shipped. Candidate: HOLDING with reactivation = production-deployment-encounters-burst-loads
- **PP-7 multi-substrate composition** — 🔬 needs-re-anchoring; per hierarchical-substrate-2x synthesis. Candidate: HOLDING with reactivation = customer-use-case-forces-hierarchy
- **PP-1 substrate-augmented LLM vs LLM-only baseline** — 🔬 0.40-0.55; awaiting PP-5/PP-8. Candidate: EXPLORATORY (active dependency on PP-8 H100 revalidation)

## Why now

Cap_map hygiene is the cheapest move that increases strategic clarity. The compaction-prep snapshot already noted "8 versions in 12 hours" — bump cadence is high; row count is climbing; categorization pass costs ~30-60min orchestrator work but pays out indefinitely.

## Closing

Move to `routed_completed/` when orchestrator either lands the categorization pass OR declines and explains why the current 28+37 row structure remains preferable.


Acted-on 2026-06-01: VALIDATED/EXPLORATORY/HOLDING/CLOSED scheme ADOPTED in cap_map intro v311; bulk application to all 65 rows is TODO (separate scheduled pass).
