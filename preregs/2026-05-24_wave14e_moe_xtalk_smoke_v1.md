# Prereg: wave14e_moe_xtalk_smoke_v1

**Date**: 2026-05-24
**Author**: orchestrator main thread (under FULL AUTONOMY from research_15_angles_triage)
**Queue**: overnight_queue (GPU)
**ETA**: 30-60 min GPU at N=4096
**Script**: `experiments/exp_wave14e_moe_xtalk_smoke_v1.py`

## Source

Tier-1 candidate A2 from `notes/research_15_angles_triage_2026-05-24.md`:
Mixture of Experts (MoE) for cross-talk reduction. Multiple substrate
capabilities are cross-talk-bounded (capacity ceiling at N=4096 saturates
near M_stored ~ N/2 for naive outer-product memory). MoE partitions the
binding space into K disjoint expert blocks; cross-talk per item should
scale with M/K rather than M.

## Mechanism

Instead of one W (NxN) accumulating M outer-product (key, value) pairs,
partition into K disjoint expert blocks W_1..W_K each of size NxN with M/K
pairs each. Gating g(key) = bsc-sign-binned-mod-K, computed via random BSC
projection of key onto a single direction, binned uniformly into K buckets.

At retrieval, pick expert by gate and read out only that expert's W_k.
Cross-talk noise for any item scales with the expert load M/K, not M.

## Hypothesis (one-line)

At fixed M_stored (especially M_stored >> N/2 where single-W saturates),
mean cosine(recall, target) for K=4 MoE exceeds single-W cosine by ratio
>= 1.30x; the lift grows with M.

## Design

| Config | N | M_grid | K | seeds |
|---|---|---|---|---|
| Full | 4096 | {500, 2000, 8000, 32000} | {4, 8} | {7, 17, 23, 31, 41} |

For each (M, K) cell:
- Generate M random (key, value) BSC pairs at dim N
- Single-W baseline: W = sum_i v_i k_i^T / N
- MoE: gate keys into K bins; build K disjoint W_k; recall picks correct
  W_k by gate, reads out
- Measure mean cosine over all M items between recall and true value

Cosine ratio = mean_moe_cosine / mean_single_cosine. Pass if ratio >= 1.30
at the saturating M cell (M=32000 for N=4096).

## Verdicts

### HARD PASS - `MOE_PASS`

At any (M, K) cell:
- mean MoE cosine >= 1.30 * mean single-W cosine
- mean MoE cosine > 0.5 (not both at noise floor)

Implication: MoE is a capacity multiplier on the substrate; opens new
sub-capability "MoE-partitioned binding memory" with K-fold capacity lift;
candidates for 13th portfolio capability IF mechanism transfers to non-
synthetic retrieval (next-cycle drill).

### HARD FAIL - `MOE_KILLED`

Best (M, K) cell has MoE cosine <= single-W cosine (ratio < 1.0).
Implication: gating function is destructive; close path or file rescue
sketches (alternative gates: orthogonal-random-features / learned gate /
content-addressable hash).

### PARTIAL - `MOE_PARTIAL`

Best ratio in [1.05, 1.30). Implication: mechanism works but lift is
sub-canonical; trigger 2x Research drill on alternative gating
(top-K MoE, soft gating, expert-balance penalty).

### INCONCLUSIVE - `MOE_INCONCLUSIVE`

per_seed missing or all ratios in (1.00, 1.05). No row movement.

## Self-tests (passed locally 2026-05-24)

`--self-test`: 4/4 verdict synthetic cells pass.

## Smoke gate (passed locally 2026-05-24)

`--smoke` (N=512, M_grid {200, 800, 2000}, K=4, 1 seed):
- M=200: single=0.848 moe=0.940 ratio=1.109
- M=800: single=0.625 moe=0.800 ratio=1.279
- M=2000: single=0.452 moe=0.652 ratio=1.442
- VERDICT: MOE_PASS

Ratio grows with M as predicted by mechanism (1.11 at M=200 -> 1.44 at
M=2000). At M >> N (saturating regime) MoE pulls ahead more.

## Memory / wallclock budget

- Per cell: K x N x N float32 = K x 64 MB at N=4096
- K=8 cell at N=4096 M=32000: 8 x 64 MB = 512 MB W storage
- 4 M-values x 2 K-values x 5 seeds = 40 cells
- GPU runtime estimate: ~30-60 min (cell dominated by storage and one
  mat-vec per item)
- Timeout: 5400s (1.5 hr safety budget)

## Filing on outcome

- HARD PASS: cap_map adds 🔬 candidate row "MoE-partitioned binding"
  (Cap candidate); v182 bump; status_log importance=CRITICAL; trigger 2x
  Research drill on non-synthetic transfer + gating-design choices.
- HARD FAIL: file 5 rescue sketches (PROT-004); cap_map: nothing added;
  status_log MEDIUM.
- PARTIAL: 🔬 candidate with explicit "mechanism present but sub-canonical"
  annotation; trigger 2x Research drill on gating alternatives.
- INCONCLUSIVE: no row movement.

## Notes / caveats

- The mechanism's success at smoke (smoke ratio 1.44 at M=2000) is encouraging
  but smoke is at N=512 not N=4096. At N=4096 with K=4, the per-expert load is
  M/4 = 8000 at the M=32000 cell - which is well into the saturating regime
  for single-W. The mechanism *should* still work but the lift may be smaller
  if N=4096 single-W has more headroom than N=512 single-W did.
- This is a CAPACITY-LIFT result, not a new capability class. Promotion to
  13th portfolio capability requires transfer to non-synthetic retrieval
  (next-cycle drill, not in this prereg).
- Source-15-angles synthesis flagged P=0.50; smoke result moves the probe
  upward but full result is still in band.
- GPU routed because storage K x N x N is 512MB at K=8 N=4096 - faster on
  CUDA than CPU.
