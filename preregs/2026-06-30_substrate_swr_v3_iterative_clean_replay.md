# Pre-registration: substrate_swr_v3_iterative_clean_replay (3-chunk)

**Filed:** 2026-06-30
**Parent design spec:** `notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md`
**Cell-author:** hdi_exp_dev
**Anchors (3-chunk; CHUNKED single-seed-per-cell):**
- `substrate_swr_v3_iterative_clean_replay_seed_7_v1_GPU`
- `substrate_swr_v3_iterative_clean_replay_seed_13_v1_GPU`
- `substrate_swr_v3_iterative_clean_replay_seed_19_v1_GPU`

**Shared core:** `experiments/_substrate_swr_v3_iterative_clean_replay_core.py`
**Queue:** overnight_queue (GPU; torch matmul + iterative cleanup loop)
**Tier:** MEASURED_MECHANISM (chain-grade eligible if all 3 seeds HARD_PASS at full M=8192)
**Seeds:** [7, 13, 19] (one per cell file)

## Lineage + framing

v1 (bundled outer product) — HARD_FAIL@smoke; K^2 cross-terms collapsed recall to 0.001.
v2 (parallel multipass clean replay) — HARD_PASS@full but suspected MM_BC_CEILING per
Skunkworks landed-VET (all N_REPLAY arms = 0.985 = DIRECT ceiling at v2's small-M
regime).

v3 (this cell) implements the brain-canonical SWR mechanism: TRUE iterative
SEQUENCE replay. At each replay step, walk the encoded sequence sequentially;
clean k via attractor; predict v; clean v against codebook; Hebbian rewrite.
Regime chosen at M >= 4096 (well above v2's 2048 BC-ceiling regime) so single-pass
clean is INSUFFICIENT and iterative refinement has room to lift.

## Brain mechanism (CITED@brain_lit_NREM3_SWR_iterative_sequence_replay)

In hippocampus, NREM3 replay is iterative SEQUENCE reactivation, not parallel
bundling. Each replay step reactivates a single time-slice in order; the
replay sequence as a whole transmits the memory trace to cortex. The
"compressed" aspect is TEMPORAL compression (10-20x faster than wake), not
capacity-bundling. Combined with intracellular attractor dynamics for cleanup
(CITED@Treves-Rolls pattern completion; Krotov-Hopfield 2016 modern dense
associative memory), each replay step both retrieves and writes back a
cleaned engram.

## Mechanism (THEORETICAL@spec_section_v3_design)

```
for pass_idx in range(n_replay_passes):
    for k, v in zip(seq_keys, seq_vals):
        k_clean   = iterative_cleanup(k, keys_codebook)
        v_predict = W_cortex @ k_clean
        v_clean   = iterative_cleanup(v_predict, vals_codebook)
        W_cortex  = DECAY * W_cortex + ETA_REPLAY * outer(v_clean, k_clean)
```

vs v1: writes are SINGLE items per step (not K-bundled) -> no K^2 cross-terms.
vs v2: replay is SEQUENTIAL across time-slices (not parallel attention over codebook).

## Arms (5 per seed; identical config across seeds per META_RULE_AW)

| Arm              | n_replay | Mechanism                                              |
|------------------|---------:|--------------------------------------------------------|
| ARM_NO_REPLAY    |        0 | Single batched Hebbian write; no iterative refinement |
| ARM_N_REPLAY_1   |        1 | Initial write + 1 iterative SEQUENCE replay pass      |
| ARM_N_REPLAY_5   |        5 | Initial + 5 iterative passes                          |
| ARM_N_REPLAY_20  |       20 | Initial + 20 iterative passes                         |
| ARM_DIRECT_UPPER |       -1 | Oracle: 10x eta direct clean write; ceiling reference |

## Regime

| Field          | Smoke | Full                                          |
|----------------|------:|-----------------------------------------------|
| M              |  4096 | 8192                                          |
| seq_len        |    50 | 100                                           |
| N_DIM          |  8192 | 8192                                          |
| N_CORTEX       |  2048 | 2048                                          |
| n_replay sweep | (0,1,5,20) | (0,1,5,20)                               |
| seeds (per chunk) | [SEED] | [SEED]                                    |

Total units per chunk: 5 arms x 1 seed = 5. Across 3 chunks: 15 arm-instances.

## Pre-registered bands (per-seed; chunk wrapper emits its own verdict)

Let R_X denote recall_cortex for arm X (single seed; chunk emits per-seed verdict).

**HARD_PASS (per-seed):**
- `R(N_REPLAY_20) - R(N_REPLAY_1) >= 0.20` (HARD_PASS_LIFT_MIN)
- AND `R(N_REPLAY_1) <= R(N_REPLAY_5) <= R(N_REPLAY_20)` (monotonic)
- AND `R(N_REPLAY_20) < R(DIRECT_UPPER) - 0.03` (not BC-ceiling)
- AND all 5 arms OK (no errors)
- AND `cardinality_ok == True`
- AND arms-must-differ by SHA-256 hash (META_RULE_AF)

**MIDDLE_BAND (per-seed):**
- `R(N_REPLAY_20) - R(N_REPLAY_1)` in `[0.10, 0.20)`

**HARD_FAIL (per-seed):**
- `R(N_REPLAY_20) - R(N_REPLAY_1) < 0.10` (no lift)
- OR `R(N_REPLAY_20) < R(N_REPLAY_1) - 0.05` (replay HURTS; cross-term accumulation like v1)
- OR `R(N_REPLAY_20) >= R(DIRECT_UPPER) - 0.03` AND `R(N_REPLAY_1) >= R(DIRECT_UPPER) - 0.03` (BC_CEILING)
- OR any arm produces error (failure_class set)
- OR cardinality breach (< 5 arms)
- OR META_RULE_AF arm-hash duplicate

**Chain-grade verdict (Skunkworks aggregates across 3 chunks):**
- HARD_PASS if all 3 seeds HARD_PASS AND `cv(R(N_REPLAY_20)) <= 0.10`
- MIDDLE_BAND if 2-of-3 HARD_PASS / MIDDLE_BAND
- HARD_FAIL otherwise

## DISCRIMINATOR-MUST-SURVIVE-SCALE check (META_RULE_AG)

Per spec + USER 2026-06-26 directive. Smoke runs at M=4096 (= 1/2 of chain-grade
M=8192). HYPOTHESIZED@spec: at M=4096 / seq_len=50 with N_CORTEX=2048
(capacity ratio M/N_c = 2.0; well above ceiling regime), single-pass
NO_REPLAY should score < 0.95 of DIRECT_UPPER, leaving room for iterative
lift to differentiate. If smoke shows all arms at ceiling (BC-saturation
preview), CELL_AUTHOR aborts dispatch and re-spec'es regime upward (larger M
or longer seq_len).

`baseline_in_band` (smoke gate): NO_REPLAY recall must be in (0.05, 0.95).

## META rules + SCHEMA-VET pre-reg fields

- cardinality_ok: true (5 arms x 1 seed per chunk = 5 units per cell)
- EXPECTED_N_UNITS: 5 (per chunk; verdict logic HARD_FAILs on != 5)
- arms_differ_verified: true (per-arm SHA-256 of cortex W state + recall; META_RULE_AF)
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH; per-cell atomic os.replace)
- crlb_n/a: "associative-memory capacity not Cramer-Rao bound; capacity-feasibility check via DIRECT_UPPER oracle arm instead"
- discriminator_reachability: true (R_NO_REPLAY < 0.7 expected at M=8192; gap to DIRECT_UPPER >= 0.2 expected; lift band is reachable)
- baseline_in_band: smoke-gate verifies 0.05 < R_NO_REPLAY < 0.95 (META_RULE_AG)
- calibration_check: "default_ok_for_this_regime" (TEMP_CLEANUP=4.0 + MAX_STEPS=6 = hdlab default for iterative_cleanup at D=2048+; matches Stage 2 NREM cells)
- cell_chunked: true (3 single-seed cells; runner death loses 1 seed not 3)
- start_marker_written: true (`_start_marker.json` per cell)
- crash_diagnostic_present: true (`_write_crash_metrics` + atomic replace per META_RULE_AH)
- heartbeat_present: true (`_heartbeat.jsonl` per-arm tick during run)
- defensive_error_checking: "passed_all_4_patterns" (chunked + start-marker + crash-diag + heartbeat)
- effective_vs_nominal_parameter_audit: aligned. nominal n_replay = effective n_replay; the iterative_cleanup at each step is the load-bearing operation (not a cosmetic pre-processor).
- bracket_includes_discriminating_band: n_replay in {0, 1, 5, 20} predicted to span (no-replay near floor) -> (mid lift) -> (saturated lift) covering >= 50% of recall span [R_NO, R_DIRECT].
- signal_shape_compatibility_audit: ALL edges SHAPE_MATCH. iterative_cleanup input/output is (N_CORTEX,) tensor; Hebbian outer-product write input is (N_CORTEX,) x (N_CORTEX,); cortex W is (N_CORTEX, N_CORTEX) matmul-compatible.
- HP_SCOPE: HARD_PASS lift gate applies to N_REPLAY arms only (NO_REPLAY = explicit baseline; DIRECT_UPPER = oracle ceiling; neither inherits the lift gate)

## META_RULE_AX (per-n_replay distinctness)

Per-arm `arm_hash` includes (arm_name, sample of W_cortex, recall) -> SHA-256.
At selftest, NO_REPLAY hash MUST differ from N_REPLAY_1 hash (verifies the
iterative-replay path actually mutates W beyond the initial write). At full
verdict, all 5 arm hashes must be distinct (META_RULE_AF + AX).

## META_RULE_Q (suspect-1.000)

The BC_CEILING gate (R_20 and R_1 both within 0.03 of DIRECT_UPPER) is the
suspect-1.000 check. If DIRECT_UPPER hits 1.000, the gate looks for whether
the mechanism arms also hit 1.000 -> regime too easy. v2 hit this at 0.985;
v3 chose M=8192 specifically to escape it.

## Dispatch destination + timeout

- Queue: overnight_queue (GPU; torch matmul + iterative cleanup inner loop)
- Timeout: 3600s/seed (per spec; cleanup loop dominates: seq_len * n_replay_total
  = 100 * (1 + 5 + 20) = 2600 cleanup calls per seed at full; ~1.5s each at
  D=2048 with sqrt(D) scaling gives ~65 min headroom; 1h cap leaves 4x margin)
- 3 chunks dispatch independently; each respects 3600s budget
- No PROT-018 _n suffix (M is the swept axis)
- PROT-019 not triggered (no _n4096 / _n8192 suffix)
- PROT-021 not triggered (3600s < 14400s threshold)

## Coordination

- Cell-author: hdi_exp_dev (this work)
- Dispatch: Director routes to hdi_orchestrator (push gate is harness-DENIED to cell-author)
- Landed-VET: hdi_skunkworks (aggregates 3-chunk metrics for chain-grade verdict)

## Notes for Skunkworks chain-grade aggregation

When all 3 seed chunks land:
- Read `data/exp_substrate_swr_v3_iterative_clean_replay_seed_{7,13,19}_v1_GPU/metrics.json`
- Per-seed verdict already computed by chunk wrapper
- Chain-grade promotion = all 3 seeds HARD_PASS + cv(R_20) <= 0.10
- BC_CEILING detection: any seed where R_1 >= DIRECT_UPPER - 0.03 -> demote to MM
- META_RULE_AX cross-seed: per-arm `arm_hash` differs across seeds (random codebook per seed)
