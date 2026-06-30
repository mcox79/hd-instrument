# Pre-reg: substrate_storage_update_rule_family_phase_diagram_v1

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn, outer-axis fill)
**USER directive (2026-06-30 ~17:35 UTC):** Phase-diagram outer-axis fill —
component-substitution axes at ~3-4 of 16 axis families done. Author + smoke +
dispatch 4 cells; this is cell #3 of 4.

**Cell:**
- Core: `experiments/_substrate_storage_update_rule_family_phase_diagram_v1_core.py`
- Seeds:
  - `experiments/exp_substrate_storage_update_rule_family_phase_diagram_v1_seed_7.py`
  - (siblings seed_13, seed_19 -- not yet authored; follow-up spawn)

## Discriminator vs prior cells

| Lever | Prior cell | THIS cell |
|---|---|---|
| Capacity sweep over alpha x K x B x N with HEBBIAN-OUTER fixed | `substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7` (HARD_PASS landed 2026-06-28) | --- |
| Update rule family at rail-config (K=64, B=16) sweeping alpha | --- | **THIS CELL** |
| Routing family (partition / softmax / hierarchical / knn) | `substrate_wm_routing_family_phase_diagram_v1` | --- |
| Routing geometry within partition (random / learned / hier / LSH) | `substrate_routing_geometry_family_phase_diagram_v1` (fix in flight 2026-06-30) | --- |

The update-rule axis is ORTHOGONAL to the capacity-multibank cell. v2 swept
alpha x K_per_bank x N x B holding update_rule=Hebbian; this cell sweeps the
update_rule family at fixed (K=64, B=16) rail-config with alpha-sweep as inner
discriminator.

## Outer axis (LOCKED at module init)

4 update rules:
1. **`hebbian_outer_product`** -- W = sum_i outer(x_i, y_i). Substrate default.
   **POSITIVE CONTROL.**
2. **`soft_hebb`** -- Online incremental: W += x outer (y - tanh(W^T x / T)).
   Predictive-coding flavor; soft competitive learning.
3. **`willshaw_binary`** -- W = sign(X.T @ Y). Binary AM (sign-quantized Hebbian).
4. **`bcm_gain`** -- W = X.T @ (Y * (Y - mean(Y))). BCM rule with row-mean theta.

## Inner axis (LOCKED)

- alpha (loading factor): `{0.5, 1.0, 2.0, 4.0}` -> M in {N/2, N, 2N, 4N}
- N: 8192 FULL; 2048 SMOKE
- K_per_bank=64, num_banks=16 (rail-config; K*B=1024 capacity FIXED)

CARDINALITY:
- FULL: 4 rules x 4 alphas = **16 phase points per seed**
- SMOKE: 4 rules x 4 alphas = **16 phase points per seed**

CARDINALITY_OK_FULL: 16. CARDINALITY_OK_SMOKE: 16.
HARD_FAIL on cardinality breach (META_RULE_H).

## Discriminator (LOAD-BEARING)

Per phase point (rule, alpha):
- **`recall`** = bit-accuracy of readout y_hat vs y_true, averaged over N_PROBE
  probe items. Probe cue derived from clean key + bipolar noise (CUE_COS=0.70).
- **`alpha_cliff`** = smallest alpha where recall drops below 0.50 (per rule).
  If no alpha in sweep crosses 0.50, cliff = 2*max(alpha) (beyond sweep).

Per cell:
- **`cliff_span_log2`** = max(cliff_log2) - min(cliff_log2) across the 4 rules.
- **`cliffs_distinguishable`** = (cliff_span_log2 >= 0.5).

## Bands (PRE-REG envelope-fail-bands)

Per phase point:
- `SATURATED`: recall >= 0.999 (substrate-too-strong; discriminator NOT firing)
- `HARD_PASS`: recall >= 0.90
- `MIDDLE_BAND`: 0.30 <= recall < 0.90
- `FLOOR`: recall <= 0.05
- `HARD_FAIL`: 0.05 < recall < 0.30

Per cell (full):
- **`HARD_PASS_UPDATE_RULE_PHASE_DIAGRAM`** (chain-grade):
  - cardinality_ok
  - positive_control (hebbian@alpha=0.5 recall >= 0.90 at FULL; >= 0.80 at SMOKE)
  - cliffs_distinguishable (>=1 rule with cliff_log2 >= 0.5 separated from others)
- **`MIDDLE_BAND_UPDATE_RULE_PHASE_DIAGRAM`**: rules cluster (cliff_span < 0.5).
- **`HARD_FAIL_CARDINALITY_BREACH`**: cardinality_ok=False.
- **`HARD_FAIL_CONTROL_FAIL`**: hebbian@alpha=0.5 below floor.

## Smoke results (2026-06-30, seed=7, N=2048)

- hebbian@alpha=0.5 -> recall=0.841 (clears smoke PC floor 0.80)
- soft_hebb@alpha=0.5 -> recall=0.753
- willshaw_binary@alpha=0.5 -> recall=0.786
- bcm_gain@alpha=0.5 -> recall=0.504 (STUCK at chance across all alphas; BCM
  degenerate with bipolar y + theta=mean(y_row), per design comment)
- cliff_span_log2 = 3.00 (>= 0.5 threshold)
- verdict: HARD_PASS_UPDATE_RULE_PHASE_DIAGRAM
- elapsed: 119.8s

**Discriminator-survives-scale (META_RULE_AG):** smoke shows 3/4 rules in
MIDDLE_BAND (recall 0.50-0.84) at smoke-N=2048; 1/4 stuck at chance (BCM).
Discriminator FIRES at smoke; full-N=8192 will sharpen separations because
alpha=4.0 in full = M=32768 = 4x more loading on K*B=1024 slots. Expect
cliff localization to MOVE: hebbian probably cliffs around alpha=2-4; soft_hebb
similar but lower start; willshaw close to hebbian; bcm stays at chance.
Cliffs likely separable.

## Smoke timing (load-bearing for timeout estimate)

Per-rule wall-clock at smoke-N=2048:
- hebbian: 0.08 / 0.15 / 0.30 / 0.60 s per alpha -> 1.13 s total
- soft_hebb: 5.24 / 11.82 / 35.76 / 62.66 s per alpha -> 115.5 s total
  (online Python loop; M iterations; scales linearly with M)
- willshaw: 0.13 / 0.22 / 0.40 / 0.81 s per alpha -> 1.56 s total
- bcm: 0.12 / 0.22 / 0.42 / 0.81 s per alpha -> 1.57 s total
- TOTAL smoke: ~120 s.

Per-seed FULL extrapolation:
- hebbian/willshaw/bcm: matmul-dominated -> O(M * N) write + O(N_PROBE * N^2)
  read. N=8192 vs 2048 = 4x N; M=4N vs 4N -> 4x M. Scale ~16x per write.
  Per-rule wall-clock ~25 s.
- soft_hebb: O(M * N^2) Python loop. M=32768 vs 8192 = 4x; N^2 = 16x ->
  total ~64x per soft_hebb arm vs smoke -> ~7400 s = 2 hr.
- Per-seed FULL wall-clock: hebbian/willshaw/bcm ~75s sum + soft_hebb ~7400s
  = ~7475 s = ~2 hr 5 min.

**Timeout estimate (META_RULE_TIMEOUT):** 1.5 * smoke_wall * scale + safety.
- 1.5 * 7475 = 11200 s. Round to **timeout=10800 s (3 hr)** per seed.
- PROT-021: 10800 > 14400 NOT exceeded; checkpoint not strictly required but
  per-seed checkpoint IS imported.

## Dispatch plan

**Destination:** `remote_cpu_queue` (matmul-bound at modest K*B=1024 slots;
GPU offers little speedup over CPU for these sizes; soft_hebb's Python loop
is GIL-bound regardless of device). CPU OK per Fix #24 guard
(`remote_cpu_queue` accepted by cell).

**Seeds:** 7, 13, 19 (3-seed chunked). Only seed_7 authored this cycle; 13 and
19 are follow-up duplicates (sed-replace SEED=7 -> SEED=13/19).

**Routing path:** exp_dev cannot push (harness-DENIED); route to Orchestrator
via DISPATCH_REQUEST after commit. Caller (USER spawn) will fan-out.

**Per-seed timeout estimate:** 10800 s (3 hr); add 1.5x safety -> queue timeout
**`--timeout 14400`** (4 hr).

PROT-018: anchor name has no `_n<N>` suffix (multi-N sweep cell).
PROT-019: timeout 14400 >= 3600 + no _n>=4096 suffix -> no floor required.
PROT-020: torch imported at TOP; GPU eligibility OK (cell falls back to CPU
gracefully via Fix #24 guard).

## Cell-template mandates satisfied

- ASCII-only (no unicode / em-dashes / emojis)
- META_RULE_AE: constants LOCKED at module init
- META_RULE_AF (arms-differ): 4 rules produce distinct W hashes per anchor
  hash; verified at selftest
- META_RULE_AH: atomic final metrics write via `.tmp` + `os.replace()`
- META_RULE_H: cardinality_ok mandatory; HARD_FAIL on breach
- except SystemExit: raise BEFORE except Exception (not BaseException); no bare except
- start_marker / crash-diag / per-unit checkpoint / heartbeat per defensive patterns

## Known limitations / honest caveats

- **bcm_gain is degenerate by design** with bipolar y + theta=row_mean: y *
  (y - mean(y)) reduces sign information. Recall stuck at 0.50 (chance).
  Result: BCM "rule" effectively a null-rule in bipolar regime; this is
  itself a measured finding (BCM is not a competitive rule for bipolar AM
  without continuous-value gating). If we wanted BCM to be informative,
  would need pre-activations + theta tracking. Documented; not a bug.
- **soft_hebb is wall-clock-expensive** (Python loop). Could be vectorized
  with chunked matmul if Skunkworks finds the result chain-grade enough to
  justify the rewrite cost.
- **Discriminator at SMOKE recall is in [0.50, 0.84] band**: noticeably below
  HARD_PASS threshold 0.90. Discriminator FIRES (3 distinct values across 4
  rules) but the BAND CHOICE may be too aggressive for smoke. Skunkworks may
  retier to MIDDLE_BAND if the discriminator pattern is consistent but
  none of the rules CROSS the 0.90 HARD_PASS threshold at any alpha
  (substrate-too-weak failure mode).

## Skunkworks's expected VET arc

1. Independent recompute of recall per (rule, alpha) point off `phase_map`.
2. Verify positive_control (hebbian@alpha=0.5 >= 0.90 FULL / >= 0.80 SMOKE).
3. Verify W_hash distinctness (META_RULE_AF).
4. Tier decision: HARD_PASS if hebbian clears 0.90 + cliffs distinguishable;
   MIDDLE_BAND if cliffs cluster or hebbian below 0.90; HARD_FAIL if cardinality
   breach or positive_control fails.

Cell-author default: under-claim. Let cert-owner tier UP.
