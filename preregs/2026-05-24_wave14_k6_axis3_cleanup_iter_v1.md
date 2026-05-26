# Prereg: wave14_k6_axis3_cleanup_iter_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: K6 compositional generalization axis 3 -- cleanup-iteration (resonator-style)
**Trigger**: K6 axis 2 HARD_FAIL in smoke (hold_out_acc=0.078 < 0.08 fail band).
Axis 3 per v193 rescue list: cleanup-iteration on retrieval to improve hold-out acc.

## Hypothesis

Iterative cleanup (resonator-style) after initial readout refines compositional recall.
T cleanup steps: attr_{t+1} = sign(W @ (obj * sign(attr_t))). Each step leverages
the associative structure of W to converge toward stored bundles.

## Design (exp_dev autonomy)

- N = 2048 (FULL), 512 (smoke)
- Epochs = 30 (FULL), 5 (smoke)
- Seeds = {7, 17, 23, 31, 41} (FULL)
- T_cleanup_grid = {0, 1, 2, 4, 8}
- Queue: remote_cpu_queue (pure numpy; single-config; ~5-15 min)

## Pre-registered falsifier bands

- **HARD-PASS**: best T hold_out_acc >= 0.20 (3x chance).
  -> K6 axis 3 PASSES; K6 🟡 PARTIAL rehab candidate.
- **HARD-FAIL**: best T hold_out_acc <= 0.09 (<=1.44x chance).
  -> K6 axis 3 REJECTED; sequence axis 4 (Bet X position-indexed).
- **MIDDLE**: hold_out_acc in (0.09, 0.20).

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

- (best T acc=0.25) -> K6_CLEANUP_HARD_PASS
- (best T acc=0.07) -> K6_CLEANUP_HARD_FAIL
- (best T acc=0.14) -> K6_CLEANUP_MIDDLE_BAND
All 7/7 self-test cases pass.

## Smoke verdict: HARD_FAIL -> upstream-push to Strategy

Smoke result: best hold_out_acc=0.031 at T=0 (0.5x chance). Cleanup iterations
DEGRADE performance: T=1: 0.016, T=2: 0.000, T=4: 0.000, T=8: 0.000.
The cleanup loop diverges rather than converges for these Hebbian weights at
smoke scale. K6 axis 3 REJECTED at smoke. Sequence axis 4 (Bet X position-indexed
integration) per v193 rescue list.

## Upstream push filed

notes/exp_dev_to_strategy_k6_axis3_smoke_fail_2026-05-24.md
