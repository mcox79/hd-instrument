# Pre-registration: substrate_order_binding_family_v1

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research phase-diagram gap analysis hand-off #2 (`notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` §2). Axis J (order-binding-family) untested at chain-grade for 2 of 3 candidates (permutation / phase-rotation); CYCLIC_SHIFT is the ONLY order-binding primitive at CG via seqbind K-cliff v3.

## Anchor

`substrate_order_binding_family_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per META_RULE §13).

Shared core: `experiments/_substrate_order_binding_family_v1_core.py`.

## Routing

- **Smoke queue:** local laptop CPU (numpy path; `.venv/Scripts/python.exe` direct invocation). Full grid = smoke grid (9 pts/seed).
- **Full queue:** `remote_cpu_queue` — cell is CPU-eligible (pure numpy). Not matmul-heavy at N=8192 x K=200 x V=1200 — expected fast.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via completion report post-smoke).
- **Timeout:** 900s per seed (3 seeds x 9 phase points x ~30s/point conservative estimate; numpy N=8192 x V=1200 cosine is O(N*V) = O(10M) per query x 50 queries x 9 pts ~ 4.5B flops per seed; laptop CPU ~4GFLOP/s -> ~19min per seed at worst; 900s = 15min covers typical).

## Why this cell exists (the gap)

CYCLIC_SHIFT is currently the ONLY order-binding primitive at chain-grade (seqbind K-cliff v3). Random-permutation and phase-rotation-based position encodings are UNTESTED. Cross-domain support exists (hippocampal theta-phase precession supports phase-rotation; reservoir-computing literature supports permutation as order-preserving).

**Open question:** does order-binding capability generalize across the family, or is CYCLIC_SHIFT a load-bearing choice? If K*(op) differs materially across the family, order-binding is CAPABILITY-CONDITIONAL. If K* is invariant, cyclic-shift is a substrate-invariant capability (positive substrate finding).

**Risk (per Research):** phase-rotation and cyclic-shift may produce mechanism_hash-identical outputs at N=8192 if theta commensurate (rotational aliasing). Cell-author uses theta = 2*pi*(golden_ratio-1)/N ~ 2*pi*0.618/N to avoid trivial aliasing to shift; smoke gate verifies BOTH bundle_hash AND positions_hash distinct across all 3 op pairs (META_RULE_AF+AX; below).

## Order-binding operations (3 ARMs)

| Arm | Encoder family | Position encoding | Item bind + bundle | Unbind |
|---|---|---|---|---|
| `CYCLIC_SHIFT` (baseline; CG) | bipolar | P_k = roll(P_0, k) | Hadamard sum_k p_k * i_k | bundle * q_pos |
| `RANDOM_PERMUTATION` (untested) | bipolar | P_k = perm^k(P_0), perm fixed random | (same Hadamard) | (same Hadamard) |
| `PHASE_ROTATION` (untested) | HRR-real | P_k = ifft(fft(P_0) * exp(1j*k*theta*freqs)); theta=2*pi*0.618/N | (same Hadamard) | (same Hadamard) |

All 3 ops share the SAME bundle + unbind mechanism (Hadamard on the position-item product). The ONLY axis varied is HOW position k is encoded into vector P_k. This isolates the order-binding effect from the bind/unbind operator effect (which is tested separately in v2 binding-op family cell).

## Sweep axes

- **N_DIM:** 8192 (fixed)
- **K (inner sweep):** {50, 500, 2000} (K range extended from initial {50,100,200} after seed=7 smoke observed all-3-ops-SAT-at-K=200 -- META_RULE_AG ITERATE_REGIME triggered; K=500 hits transition region; K=2000 into FLOOR; verified 2026-07-01 03:36Z) — CRLB SNR = sqrt(N/K) gives predicted SAT band across all 3 K; K*(op) differential is the discriminator
- **Seeds:** {7, 13, 19}
- **n_queries per phase point:** 50 FULL / 5 SMOKE
- **V_ITEMS:** 2500 (>= max K=2000 + slack)
- **V_POS:** 2500

Smoke and FULL grids identical (9 pts/seed each). Smoke uses fewer queries (5 vs 50) but same K sweep.

## Cardinality

- **FULL per seed:** 3 ops x 3 K = **9 phase points** (27 total across 3 seeds)
- **SMOKE per seed:** 3 ops x 3 K = **9 phase points** (small enough for full grid at smoke)

`cardinality_ok` field set true iff `observed_n_units == expected_n_units`. CARDINALITY_OK mandatory per META_RULE_H.

## Bands (LOCKED)

For per-(op, K) `top1_substrate` recall:

- **SAT band:** `top1 >= 0.90` — op is above cliff at this K
- **MB band:** `0.30 <= top1 <= 0.70` — op is on cliff at this K
- **FLOOR band:** `top1 <= 0.10` — op is below cliff at this K
- **TRANSITION:** rest (0.10 < top1 < 0.30 OR 0.70 < top1 < 0.90)
- **SUSPECT_SATURATION:** `top1 >= 0.9995` flagged per META_RULE_Q

`K*(op)` = smallest K in sweep where SUBSTRATE drops below SAT (0.90). If no cliff in sweep, set to `max(K)+1 = 201` (UPPER_BOUND ceiling).

`log10_K_star_separation(op_a, op_b) = abs(log10(K*_a) - log10(K*_b))`.

## CRLB / capacity-feasibility analysis (THEORETICAL@Var(unbind_noise)~K/N)

For any order-binding that preserves random-code independence: `Var(unbind_noise) ~ K/N`; `SNR ~ sqrt(N/K)`. Top1 cleanup over V=2500 items via dot product:

| K | K/N | SNR | Predicted top1 (well-preserved op) | Predicted band |
|---|---|---|---|---|
| 50 | 0.006 | 12.8 | ~1.00 | SAT |
| 500 | 0.061 | 4.05 | ~0.90-0.95 | SAT / edge |
| 2000 | 0.244 | 2.02 | ~0.30-0.55 | MB / cliff |

**Iteration history (META_RULE_AG applied):** initial K sweep {50,100,200} triggered baseline-saturated-above-0.95 at K=200 across all 3 ops (seed=7 smoke 2026-07-01 03:32Z; verified all top1=1.000). K range EXTENDED to {50, 500, 2000} to push into cliff regime per META_RULE_AG ITERATE_REGIME. Re-verified smoke 2026-07-01 03:36Z: CYCLIC_SHIFT at K=500 -> 0.80 (transition); RAND_PERM/PHASE_ROT at K=500 -> 0.60 (MB); all 3 ops FLOOR at K=2000. Cliff clearly observable; K*(op) differential reachable at 50-query FULL.

For PHASE_ROTATION with theta=2*pi*0.618/N: rotation-aliasing requires k*theta close to integer multiple of 2*pi, which at K<=200 and this theta means k*0.618 must be near integer -- happens at k in {2, 3, 5, 8, 13, ...} approximately (Fibonacci-like near-alignments). We do NOT expect exact bundle_hash collision at any K<=200 with this theta choice; smoke gate verifies distinctness empirically.

`discriminator_reachability: True` -- IF ops differ in K*, log10 separation is measurable via K-mean scan; IF ops all >= K=200, upper-bound ceiling flag applies.

## Discriminator (LOCKED)

`n_ops_distinct_from_baseline` := number of NON-BASELINE ops (i.e. RANDOM_PERMUTATION and PHASE_ROTATION; 2 candidates) whose K*(op) is >= 0.15 log10-separated from CYCLIC_SHIFT baseline's K*.

- **HARD_PASS:** `n_ops_distinct_from_baseline >= 1` AND all 3 op pairs distinct in BOTH bundle_hash AND positions_hash (META_RULE_AF+AX) AND `n_suspect_saturation < len(phase_map)` (not ALL points suspect-1.000). Verdict tag: `ORDER_BINDING_DISCRIMINATES`.
- **MIDDLE_BAND:** `n_ops_distinct_from_baseline == 0` but at least ONE non-baseline op has log10 sep > 0.05 AND < 0.15 (partial signal). Verdict tag: `PARTIAL`.
- **HARD_FAIL:** all 3 ops K* within +/-0.05 log10 (invariant). Verdict tag: `ORDER_BINDING_INVARIANT`.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok` mandatory (META_RULE_H): FULL=9 / SMOKE=9
- [x] Per-unit failure-class instrumentation (META_RULE_J): `except Exception` (NOT BaseException), with `_traceback` recorded
- [x] Discriminator-fires gate (META_RULE_K): smoke gate verifies 3-op-distinct AND SAT@K=50 for all ops AND positive-control-pass
- [x] Strictly-above-floor (META_RULE_L): HARD_PASS requires n_ops_distinct >= 1 with sep >= 0.15 log10 (STRICTLY above 0.05 noise floor)
- [x] HP_SCOPE per-arm: HARD_PASS gate applies cell-wide (K* differential is cross-op metric)
- [x] Calibration check (META_RULE_M): `default_ok_for_this_regime` -- CRLB formula applies to all 3 ops; no adaptive tuning
- [x] ARMS-MUST-DIFFER (META_RULE_AF+AX): selftest asserts 3 op bundle hashes distinct at K=5 AND 3 op positions hashes distinct at K=5; run aggregator verifies 3/3 pair-distinctness BOTH bundle AND positions
- [x] Final-metrics atomicity (META_RULE_AH): per-seed checkpoint via `_seed_checkpoint.write_partial_key` (per-iter distinct paths)
- [x] `except SystemExit: raise` BEFORE `except Exception` (§8): all wrapper outer-try blocks satisfy this
- [x] CRLB / capacity-feasibility: `discriminator_reachability: True` conditional on K* differential; smoke gate detects and flags CEILING case (all-SAT-at-K_max) honestly
- [x] Substrate-too-robust check (META_RULE_AG): smoke gate emits `smoke_gate_pass_with_ceiling` if all 3 ops SAT at K=200 (honest ceiling flag; FULL verdict handles)
- [x] Defensive error-checking (META_RULE §13 patterns): L1 start_marker + L2 crash-diag + L3 checkpoint + L4 heartbeat-via-print; CHUNKED 1 seed per cell file
- [x] Per META_RULE_AX arm-distinctness ACROSS FAMILY AXIS: mechanism_hash distinct at smoke pre-tier (both bundle_hash AND positions_hash)
- [x] Pre-reg fields below

```yaml
sweep_alignment_verdict: ALIGNED        # K is the EFFECTIVE parameter every op sees
discriminating_fraction: 1.0            # 3/3 K values predicted to land in [0.85, 1.00] band per CRLB; discriminator is K* CLIFF LOCATION not per-point band
composition_edges: []                   # No multi-primitive composition; each order-op is monolithic position encoder
positive_control_arms:
  - arm: CYCLIC_SHIFT
    primitive: order_binding_via_roll
    test_regime: {N_DIM: 8192, K: 50}
    cited_prior_atom: seqbind_K_cliff_v3_CG   # CYCLIC_SHIFT baseline chain-grade
    cited_prior_metric: 1.000                  # perfect recall at K=50 predicted
    tolerance: 0.20                            # min top1 >= 0.80 (well above 1/V=0.0004 chance)
    if_outside_tolerance: HARD_FAIL_META_RULE_BC_CONTROL_FAIL
    regime_extension_audit: SHAPE_MATCH        # same regime as CG source
functional_requirements:
  - req: "encode sequence position k as substrate vector P_k derived from base P_0"
    primitive: per-op position encoder (roll / perm^k / phase_rotate)
  - req: "bundle K position-item pairs into single substrate vector"
    primitive: Hadamard sum shared across all 3 arms
  - req: "recover item at position k from bundle given query position"
    primitive: Hadamard unbind + dot-product cleanup against item codebook
  - req: "discriminate order-binding choice via K* localization differences"
    primitive: per-op K* localization + log10 separation from CYCLIC_SHIFT baseline
cardinality_ok: TRUE
final_metrics_atomicity: per_iter_paths
arms_differ_verified: TRUE              # selftest asserts BOTH bundle+positions distinct; FULL aggregator re-verifies
crlb_floor_computed: 0.0004             # 1/V_ITEMS (V=2500)
crlb_formula_reference: "SNR = sqrt(N/K); top1 ~ 1.0 at SNR >= 3"
discriminator_reachability: TRUE_conditional_on_K_star_below_200_ceiling
calibration_check: default_ok_for_this_regime
baseline_in_band: TRUE                  # CYCLIC_SHIFT at K=50 is well-inside SAT (SNR~12.8); positive control anchors the mechanism
cell_chunked: TRUE
start_marker_written: TRUE
crash_diagnostic_present: TRUE
heartbeat_present: TRUE                 # print-flush per phase point
defensive_error_checking: passed_all_4_patterns
```

## Workflow (Dispatch)

1. **Pre-flight selftest (laptop CPU):** `python experiments/exp_substrate_order_binding_family_v1_seed_7.py --self-test` -> verify per-op K=5 round-trip AND 3-op bundle+positions distinctness.
2. **Pre-flight smoke (laptop CPU):** `python experiments/exp_substrate_order_binding_family_v1_seed_7.py --smoke` -> verify smoke gate passes. Smoke = FULL grid; primary difference is 5 queries vs 50 (~10x faster).
3. **Smoke gate must pass** (cardinality + 3-op-distinct-bundle-and-positions + positive_control + SAT-at-K=50 for all ops + cliff-observable-OR-ceiling-flag):
   - If smoke HARD_FAIL: ABORT FULL dispatch; iterate cell (regime nudge; theta adjustment; harder K sweep) or return to Research.
   - If smoke HARD_PASS_WITH_CEILING: dispatch FULL anyway; FULL verdict will demote to MIDDLE_BAND if ceiling persists at 50 queries (per META_RULE_AG); this is HONEST.
4. **Commit cells + prereg:** `git add experiments/exp_substrate_order_binding_family_v1_seed_*.py experiments/_substrate_order_binding_family_v1_core.py preregs/2026-07-01_substrate_order_binding_family_v1.md`
5. **Dispatch FULL via Orchestrator** (harness push DENIED to exp_dev): request to Orchestrator via completion report -- `remote_cpu_queue` x 3 seeds x `--timeout 900`.

## Predicted runtime

- Per-phase-point CPU wall (numpy): dot product I_codebook @ unbound (V=1200 x N=8192) x 50 queries per point = ~500ms per point at typical laptop rates. Plus PHASE_ROTATION rfft overhead per K.
- Per-seed FULL: 9 pts x ~1s avg = ~9s + overhead ~30-60s (defensive; will be faster in practice).
- Timeout: 900s/seed (15 min) x 3 seeds provides massive margin.

## Composition with seqbind K-cliff v3 CG

Seqbind K-cliff v3 CG established CYCLIC_SHIFT as the load-bearing position encoder for sequence-binding capability. This cell tests whether that capability generalizes across the order-binding FAMILY (permutation / phase-rotation) or is CYCLIC-SHIFT-specific. If v1 HARD_PASS with 1+ non-baseline op K*-distinct, order-binding is CAPABILITY-CONDITIONAL (substantive positive finding). If v1 HARD_FAIL, capability is family-invariant at WM regime (substantive negative -- CYCLIC_SHIFT alone is not privileged).

## Pointers

- Research hand-off doc: `d:/AI/hd-instrument/notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` §2
- CYCLIC_SHIFT CG prior atom: seqbind K-cliff v3 (CG per Research §2)
- Template cell: `experiments/_substrate_seqbind_binding_operation_family_phase_diagram_v2_core.py` (v2 binding-op family; structurally analogous)
