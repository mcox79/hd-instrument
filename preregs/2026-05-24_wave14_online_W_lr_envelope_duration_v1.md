# Prereg: wave14_online_W_lr_envelope_duration_v1

**Date**: 2026-05-24
**Author**: exp_dev (sonnet)
**Queue**: remote_cpu_queue
**ETA**: 18-30 min CPU
**Script**: `experiments/exp_wave14_online_W_lr_envelope_duration_v1.py`

## Brain-inspired anchor

Gong, Martell, Dudman, Coddington (2026), *Science* DOI 10.1126/science.aeb0813,
report that large rewards accelerate mouse learning by EXTENDING DOPAMINE DURATION
(not magnitude). Authors confirmed via optogenetic extension of standard-magnitude
rewards: same accelerated learning.

Cap 5 substrate (Online W Robbins-Monro + SNAP, ✅ at FULL per v153, noise envelope
✅ to p=0.30 per v159) uses an explicit per-step lr schedule. The article's
duration-vs-magnitude distinction is **1-edge to Cap 5** and directly testable
at fixed integral (∫ lr dt = const).

## Hypothesis (one-line)

At fixed discrete sum Σ_t lr(t) = 10.0 (within ±5%) across 50 sequential writes,
wider-shorter lr envelopes ("extended dopamine") yield strictly better online-W
retention under noise p ∈ {0.30, 0.40} than taller-narrower envelopes ("brief
spike"), holding seed, n_writes, SNAP threshold, and pattern statistics constant.

## Design

| Envelope | Shape | Peak | Nonzero steps |
|---|---|---|---|
| E1 baseline Robbins-Monro (τ=10) | lr(t) = c₁/(1+t/10) | ~2.1 | 50 |
| E2 brief-spike rectangular | lr=5 for t∈[0,1], 0 else | 5.0 | 2 |
| E3 extended rectangular | lr=1 for t∈[0,9], 0 else | 1.0 | 10 |
| E4 optogenetic-extended (τ=40) | lr(t) = c₄/(1+t/40) | ~0.5 | 50 |

All envelopes have Σ_t lr(t) = 10.0 ± 5% (scaling constants `c₁`, `c₄` chosen
so RM schedules hit the target sum exactly; E2 and E3 hit 10.0 by construction).

**Substrate**: N=4096 bipolar BSC (matches Cap 5 v153/v159 reference impl).
**Update rule**: SNAP-guarded outer product, threshold 1.0 (Cap 5 v153 config).
**Sweep**: 4 envelopes × noise p ∈ {0.20, 0.30, 0.40} × 3 seeds = 36 cells.
**Metric**: `min_acc` across all writes (catastrophic-forgetting resistance);
acc per write = fraction of stored (key, value) pairs successfully retrieved
under bit-flip noise on the query key. Retrieval passes if mean component
overlap > 0.7.

## Verdicts

### HARD PASS — `LR_DURATION_BEATS_MAGNITUDE`

Both conditions must hold at p ∈ {0.30, 0.40}:
1. **Extended dominates**: E3 OR E4 retention ≥ E1 retention + 0.05.
2. **Brief-spike ties or underperforms**: E2 retention ≤ E1 retention + 0.02.

Implication: dopamine-duration mechanism transfers; opens Cap 5 envelope
expansion drill (τ-vs-noise dose-response, SNAP × τ interaction).

### HARD FAIL — `LR_ENVELOPE_NEUTRAL`

All 4 envelopes within ±0.02 retention across ALL p ∈ {0.20, 0.30, 0.40}
(max-min spread ≤ 0.02 at every noise level).

Implication: at fixed integral, substrate is shape-insensitive; dopamine-
duration analogy was vibes-only. File as orthogonal at Cap 5 operating point;
close the brain-inspired path (do NOT propose Cap 5a sub-cap).

### MIDDLE BAND — `LR_ENVELOPE_MIXED`

Differentiation exists but predicted direction not met (e.g., brief-spike E2
WINS, or E3/E4 dominate but E2 also dominates E1). Substrate-novel pattern.
Trigger 2x level-2 drill on envelope dose-response per
[[feedback-negative-results-2x-research]] (mixed counts as falsification of the
specific transfer claim, even though some structure emerged).

### `LR_ENVELOPE_INCONCLUSIVE`

cell_table missing required (envelope, p) pairs. Re-run.

## Self-tests (mandatory per [[feedback-strategy-spec-formula-selftests]])

Script `--self-test` invokes:
1. `self_test_envelopes(n_writes=50)` — asserts each envelope's discrete sum
   is within ±5% of 10.0, prints (sum, peak, nonzero_steps) for each.
2. `self_test_verdict()` — asserts HARD PASS / HARD FAIL / MIDDLE BAND / INCONCLUSIVE
   verdict mapping across 4 synthetic cell tables.

## Smoke gate

Local pre-run at N=64, n_writes=5, n_seeds=1, p=0.30 only. Gate:
- Envelope integrals computed and within tol at n_writes=5 (sums printed)
- All 4 envelopes evaluated; cell_table populated
- metrics.json written with valid `verdict`, `verdict_msg`, `elapsed_s`,
  `summary`, `config` keys

## Memory / wallclock budget

- W per cell: 4096 × 4096 × float32 ≈ 64 MB (CPU)
- Retrieval cost per write: O(n_writes_so_far × N²) for matvec — dominant cost
- 36 cells × ~30s/cell ≈ 18 min wallclock on remote CPU; budget 30 min timeout

## Filing on outcome

- HARD PASS → cap_map: propose Cap 5a "Online W lr-envelope duration mode"
  (or expand Cap 5 envelope row); trigger 2x drill on dose-response.
- HARD FAIL → cap_map: NO change; file as orthogonal; close brain-inspired path.
- MIDDLE BAND → cap_map: 🔬 row for envelope-shape sensitivity; trigger 2x drill.

All outcomes → status_log entry with importance=HIGH (per Strategy direction:
brain-inspired Cap 5 envelope test, positive result = direct paper-to-substrate mapping).
