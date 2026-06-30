# Pre-registration: substrate_seqbind_binding_operation_family_phase_diagram_v2

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive 2026-06-30 — drill all MIDDLE_BAND negatives 2x. Parent cell `substrate_pc_binding_operation_family_phase_diagram_v1` landed MIDDLE_BAND (3-seed FULL; n_disc=8/48; 4 of 6 binding-op pairs differ above 30%). Binding-op axis NOT at chain-grade at PC regime; substantive open negative. Not yet 2x-drilled.

## Anchor

`substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_{7,13,19}` (3 sibling files; chunked-per-seed per META_RULE §13).

Shared core: `experiments/_substrate_seqbind_binding_operation_family_phase_diagram_v2_core.py`.

## Routing

- **Smoke queue:** local laptop (`.venv/Scripts/python.exe` direct invocation) at smoke-N parameters; FULL-N preview at K_SEQ=1000 for discriminator-survives-scale audit.
- **Full queue:** `overnight_queue` (GPU) — complex matmul-bound for HRR-conv + tensor product at N=8192; 5 ops × 5 K_SEQ × 50 queries × 3 seeds = matmul-heavy.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via completion report post-smoke).
- **Timeout:** 1800s per seed (3 seeds × 25 phase points × ~30s/point at GPU; with margin).

## Why this cell exists (the gap)

PC v1 swept 4 binding ops at the PATTERN COMPLETION regime: corruption ∈ {0.10, 0.25, 0.40, 0.475} × N ∈ {1024, 4096, 8192} × M=100 role-filler pairs. Result MEASURED@`d:/AI/hd-instrument/data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_7/metrics.json:verdict`: MIDDLE_BAND_BINDING_DIFFERS_BUT_LOW_DISC (n_disc=8/48; n_pairs_differ=6/6; n_ops_above_30pct=0).

**Open question:** is binding-op axis truly substrate-invariant, or just regime-conditional?

PC regime tests SINGLE-PATTERN recovery (one bind-unbind round-trip per query). Sequence binding tests SEQUENCE recovery — bundle of K bind-pairs, query at one position. Different cliff axis (K_SEQ vs corruption), different attractor dynamics (sequence vs single-pattern), different load shape (additive K vs multiplicative M).

**Hypothesis:** binding-op family may discriminate at sequence regime even though it doesn't at PC. If TRUE, finding is `binding op = REGIME-CONDITIONAL not substrate-invariant` — substantive substrate finding. If FALSE (binding ops converge here too), the cross-regime convergence is itself a substantive substrate-uniform finding (binding-op axis truly invariant).

**Compositional bridge:** theta-gamma v2 (CG; 2026-06-30 atomized as CG primitive) showed FHRR phase binding contributes to sequence binding cliff. v2 tests whether *discrete* binding-op choice (Hadamard / circ-conv / tensor / XOR / sum-mod-N) discriminates similarly at sequence regime — composes axes I+J with the new axis K (binding-op family).

## Binding operations (5 ARMs)

| Arm | Encoder family | bind+bundle | unbind | Code dim |
|---|---|---|---|---|
| `HADAMARD_BIND` | binary_bipolar | sum_k (p_k * i_k) on +/-1 | bundle * q_pos (self-inverse) | N=8192 |
| `CIRCULAR_CONV_HRR` | hrr_real | sum_k ifft(fft(p_k)*fft(i_k)) | ifft(conj(fft(q))*fft(bundle)) | N=8192 |
| `TENSOR_PRODUCT` | binary_bipolar_outer (N_outer=90) | sum_k outer(p_k,i_k).flatten() | q @ bundle_2d / N_outer | N_outer^2=8100 |
| `XOR_BSC` | binary_01 | sum_k (p_k XOR i_k) | centered_bundle * sign(q) | N=8192 |
| `SUM_MOD_N` (META_RULE_BC) | integer_mod_N | sum_k (p_k + i_k) mod N | (bundle - q) mod N | 1 |

`SUM_MOD_N` is the **positive control / additive baseline**: lossy additive bind with no proper unbind. MUST clear floor `top1 >= 0.05` at K=50 (well above 1/V=0.0008 chance) — otherwise regime is too hard OR test rig broken per META_RULE_BC.

## Sweep axes

- **N_DIM:** 8192 (fixed)
- **K_SEQ (inner sweep):** {50, 100, 200, 500, 1000}
- **Seeds:** {7, 13, 19}
- **n_queries per phase point:** 50 FULL / 5 SMOKE
- **V_ITEMS:** 1200 (>= max K_SEQ + slack)
- **V_POS:** 1200

Smoke K_SEQ: {50, 200, 1000} — spans SAT (low-K), TRANSITION/MB (mid-K), FLOOR (high-K).

## Cardinality

- **FULL per seed:** 5 ops × 5 K_SEQ = **25 phase points** (75 total across 3 seeds)
- **SMOKE per seed:** 5 ops × 3 K_SEQ = **15 phase points**

`cardinality_ok` field set true iff `observed_n_units == expected_n_units`. CARDINALITY_OK mandatory per META_RULE_H.

## Bands (LOCKED)

For per-(op, K_SEQ) `top1_substrate` recall:

- **SAT band:** `top1 >= 0.90` — op is above cliff at this K
- **MB band:** `0.30 <= top1 <= 0.70` — op is on cliff at this K
- **FLOOR band:** `top1 <= 0.10` — op is below cliff at this K
- **TRANSITION:** rest (0.10 < top1 < 0.30 OR 0.70 < top1 < 0.90)
- **SUSPECT_SATURATION:** `top1 >= 0.9995` flagged per META_RULE_Q

`K_cliff[op]` = smallest K in sweep where SUBSTRATE drops below SAT (0.90). If no cliff in sweep, set to `max(K_SEQ)+1` (=1001).

`log2_K_cliff_separation(op_a, op_b) = abs(log2(K_cliff_a) - log2(K_cliff_b))`.

## CRLB / capacity-feasibility analysis (THEORETICAL@var(unbind_noise)~K/N)

For VSA bundle of K bind(R,F) pairs with random codes: `Var(unbind_noise) ≈ K/N`, so `SNR ≈ sqrt(N/K)`. Top1 cleanup over V=1200 items via cosine:

| K_SEQ | K/N | SNR | predicted top1 (Hadamard / HRR) | predicted band |
|---|---|---|---|---|
| 50 | 0.006 | 12.8 | ~1.00 | SAT |
| 100 | 0.012 | 9.1 | ~1.00 | SAT |
| 200 | 0.024 | 6.4 | ~1.00 | SAT |
| 500 | 0.061 | 4.0 | ~0.95 | SAT/edge |
| 1000 | 0.122 | 2.9 | ~0.70 | MB top |

All K below CRLB capacity `K_max ≈ N/3 ≈ 2700` at N=8192. For HARD_PASS reachable, ops must differentiate by NON-CRLB-uniform mechanisms — TENSOR has only N_outer=90 effective DoF (much earlier cliff predicted); SUM_MOD_N collapses sharply (no real unbind); XOR has integer-substrate noise differences. Predicted K_cliff per op:

- `CIRCULAR_CONV_HRR`: cliff between K=500-1000
- `HADAMARD_BIND`: cliff between K=500-1000 (similar to HRR)
- `TENSOR_PRODUCT`: cliff at K=50-100 (only 90 effective DoF; saturates early)
- `XOR_BSC`: cliff between K=200-500 (binary substrate noise)
- `SUM_MOD_N`: cliff IMMEDIATELY (K=50 already MB or FLOOR; no proper unbind)

`discriminator_reachability: True` — predicted K_cliff spread is ~5-20× (log2 sep ~2-4); HARD_PASS threshold (>=0.3 log2 sep, >=3 distinct ops) reachable.

## Discriminator (LOCKED)

`n_distinct_cliff_ops` := number of ops whose K_cliff is >= 0.3 log2-separated from EVERY other op's K_cliff.

- **HARD_PASS:** `n_distinct_cliff_ops >= 3` AND `n_pairs_differ == 10/10` (all 10 op-pairs distinct mechanism_hash; META_RULE_AF) AND `n_suspect_saturation == 0`. Verdict tag: `BINDING_DISCRIMINATES_AT_SEQUENCE_REGIME`.
- **MIDDLE_BAND:** `n_distinct_cliff_ops == 2` AND `n_pairs_differ == 10/10`. Verdict tag: `PARTIAL_DISCRIMINATION`.
- **HARD_FAIL:** `n_distinct_cliff_ops <= 1`. Verdict tag: `BINDING_INVARIANT_ACROSS_REGIMES` (substantive substrate-uniform finding).

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok` mandatory (META_RULE_H): FULL=25 / SMOKE=15
- [x] Per-unit failure-class instrumentation (META_RULE_J): `except Exception` (NOT BaseException), with `_traceback` recorded
- [x] Discriminator-fires gate (META_RULE_K): smoke gate verifies SAT@K=50 AND (cliff observable at K=1000 OR ABORT)
- [x] Strictly-above-floor (META_RULE_L): HARD_PASS requires n_distinct >= 3, not >=2
- [x] HP_SCOPE per-arm: gate applies to HARD_PASS across all 5 ops as a group (cliff-localization metric is cell-wide, not per-arm)
- [x] Calibration check (META_RULE_M): `default_ok_for_this_regime` — CRLB formula applies to all 5 ops; no adaptive tuning
- [x] ARMS-MUST-DIFFER (META_RULE_AF): selftest asserts 5 op bundle hashes distinct at K=1; run aggregator verifies 10/10 op-pair mechanism_hash distinct
- [x] Final-metrics atomicity (META_RULE_AH): per-seed checkpoint via `_seed_checkpoint.write_partial_key` (per-iter distinct paths)
- [x] `except SystemExit: raise` BEFORE `except Exception` (§8): all wrapper outer-try blocks satisfy this
- [x] CRLB / capacity-feasibility: `discriminator_reachability: True` (predicted K_cliff spread ~5-20x)
- [x] Substrate-too-robust check (META_RULE_AG): smoke gate aborts if ALL 5 ops SAT at K_max=1000
- [x] Defensive error-checking (META_RULE §13 patterns): L1 start_marker + L2 crash-diag + L3 checkpoint + L4 heartbeat-via-print; CHUNKED 1 seed per cell file
- [x] Pre-reg fields below

```yaml
sweep_alignment_verdict: ALIGNED        # K_SEQ is the EFFECTIVE parameter every op sees
discriminating_fraction: 1.0            # 5/5 K_SEQ values predicted to land in 0.10-0.99 band per CRLB
composition_edges: []                   # No multi-primitive composition; each binding op is monolithic
positive_control_arms:
  - arm: SUM_MOD_N
    primitive: additive_bind_floor
    test_regime: {N_DIM: 8192, K_SEQ: 50}
    cited_prior_atom: NONE              # No prior CG result for SUM_MOD_N additive
    cited_prior_metric: NA
    tolerance: 0.05                     # min top1 >= 0.05 (well above 1/V=0.0008 chance)
    if_outside_tolerance: HARD_FAIL_META_RULE_BC_CONTROL_FAIL
    regime_extension_audit: SHAPE_MATCH # SUM_MOD_N is by-construction in this regime
functional_requirements:
  - req: "bundle K position-item pairs into single vector substrate"
    primitive: per-op bind+sum (registered in _BINDING_REGISTRY)
  - req: "recover item from bundle given query position"
    primitive: per-op unbind + cosine cleanup against item codebook
  - req: "discriminate binding-op choice via K_cliff localization differences"
    primitive: per-op K_cliff localization + log2 separation pair-wise
cardinality_ok: TRUE
final_metrics_atomicity: per_iter_paths
arms_differ_verified: TRUE              # selftest asserts; FULL aggregator re-verifies
crlb_floor_computed: 0.0008             # 1/V_ITEMS
crlb_formula_reference: "SNR = sqrt(N/K); top1 ~ 1.0 at SNR >= 3"
discriminator_reachability: TRUE
calibration_check: default_ok_for_this_regime
baseline_in_band: TRUE                  # SUM_MOD_N is positive control; substrate-saturation at K=50 not expected because TENSOR_PRODUCT predicted to cliff early
cell_chunked: TRUE
start_marker_written: TRUE
crash_diagnostic_present: TRUE
heartbeat_present: TRUE                 # print-flush per phase point (acceptable per existing v1 pattern; canonical CellHeartbeat available)
defensive_error_checking: passed_all_4_patterns
```

## Workflow (Dispatch)

1. **Pre-flight smoke (laptop CPU):** dispatch each seed via local invocation `python experiments/exp_substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_7.py --smoke` → verify smoke gate passes → returns HARD_PASS_SMOKE or HARD_FAIL_SMOKE per smoke_gate_predicate.
2. **Smoke gate must pass** (cardinality + 5-op-distinct + positive_control + SAT@K=50 + cliff_observable_or_separation):
   - If smoke HARD_FAIL: ABORT FULL dispatch; iterate cell or return to Research.
3. **Commit cells + prereg:** `git add experiments/exp_substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_*.py experiments/_substrate_seqbind_binding_operation_family_phase_diagram_v2_core.py preregs/2026-06-30_substrate_seqbind_binding_operation_family_phase_diagram_v2.md`
4. **Dispatch FULL via Orchestrator** (harness push DENIED to exp_dev): request to Orchestrator via completion report — `overnight_queue` × 3 seeds × `--timeout 1800`.

## Predicted runtime

- Per-phase-point GPU wall: ~5-30s (HRR FFT batched on CUDA; TENSOR_PRODUCT at N_outer=90 is light; HADAMARD_BIND is matmul-light)
- Per-seed FULL: 25 pts × ~20s avg = ~500s; with overhead and 50 query loop ≈ 800-1500s
- Timeout: 1800s/seed × 3 seeds = 5400s overnight_queue wall total

## Composition with theta-gamma v2 CG

theta-gamma v2 (CG axes I+J) showed FHRR phase binding contributes to sequence binding cliff. This cell adds axis K (binding-op family); composes by testing whether discrete binding-op choice discriminates at the SAME regime where phase binding does. If v2 HARD_PASS, the substantive composition is `binding-op + phase-binding both regime-conditional within sequence binding cliff dynamics`. If v2 MIDDLE_BAND/HARD_FAIL, the substantive composition is `phase binding (continuous) discriminates but discrete op-choice does NOT` — suggesting phase encoding is the load-bearing axis, not bind primitive choice.

## Pointers to v1

- v1 cell triplet: `experiments/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}.py`
- v1 core: `experiments/_substrate_pc_binding_operation_family_phase_diagram_v1_core.py`
- v1 prereg: `preregs/2026-06-28_substrate_pc_binding_operation_family_phase_diagram_v1.md`
- v1 results (per-seed): `data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` (verdict: MIDDLE_BAND_BINDING_DIFFERS_BUT_LOW_DISC; n_disc=8/48)
