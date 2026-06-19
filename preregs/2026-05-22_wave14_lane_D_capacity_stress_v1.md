# Pre-reg: Wave 14 Lane D Capacity Stress v1

**Filed:** 2026-05-22
**Bet:** Lane D capacity envelope (extends Phase 3 COMPOSE smoke)
**Predecessor:** `wave14_lane_D_cognitive_arch_smoke_v1` (COMPOSE at baseline params)

## Question

What is the joint capacity envelope of the Lane D substrate? Find the breakpoints where each of the 4 primitives drops below 0.70 when loaded individually (other primitives held at baseline).

## Hypothesis

H_capacity: at least one axis has a measurable breakpoint within the swept range — substrate is finite. We expect K (hypothesis count) and U_stream (memory horizon) to be most fragile.

H_null: All 4 axes scale healthily to max sweep value at N=4096.

## Pre-declared verdicts

- `LANE_D_CAPACITY_HEALTHY` — baseline PASS AND no breakpoint found in any of 4 axes.
- `LANE_D_CAPACITY_BOUNDED` — baseline PASS AND ≥1 axis hits a breakpoint.
- `LANE_D_CAPACITY_FRAGILE` — baseline FAILS (regression from COMPOSE).
- `LANE_D_CAPACITY_INCONCLUSIVE` — metric collection error.

## Method

Baseline params: M_S=50, K=3, U_stream=40, X_alphabet=5 (matches COMPOSE smoke).

For each axis ∈ {M_S, K, U_stream, X_alphabet}:
  hold other 3 at baseline; sweep this axis through {1×, 3×, 6×} baseline.

Per (axis, value): measure (S, T, U, X) accuracy; breakpoint = first value where min(S,T,U,X) < 0.70.

## Acceptance thresholds

- 0.70 per-primitive matches Phase 3 COMPOSE acceptance.
- Baseline must reproduce COMPOSE (regression guard).

## Config

- N=1024 smoke, 4096 full.
- Sweeps full: M_S ∈ {50, 150, 300}, K ∈ {3, 10, 25}, U_stream ∈ {40, 200, 1000}, X_alphabet ∈ {5, 20, 50}.
- Single seed=17 (initial scan; multi-seed re-run only if interesting breakpoint surfaces).

## Pre-declared interpretation

- **HEALTHY**: Lane D capacity envelope > 6× baseline on all axes. Next: push further (12×, 25×).
- **BOUNDED**: identifies the fragile axis. Mechanism question: why does that axis bottleneck? (Cross-talk? Codebook orthogonality? Decay constant?)
- **FRAGILE**: regression from COMPOSE. Audit substrate change.

## Not in scope

- Multi-axis joint sweep (4D). One-axis-at-a-time only.
- N-scaling (held at 4096).
- Cross-primitive interference characterization (separate experiment).
