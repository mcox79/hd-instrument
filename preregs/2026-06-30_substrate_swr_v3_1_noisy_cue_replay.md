# Pre-registration: substrate_swr_v3_1_noisy_cue_replay (3-chunk)

**Filed:** 2026-06-30
**Parent spec:** Director Action 2 2026-06-30 (Option A: minimal spec change to v3)
**Lineage:**
- v3 design spec: `notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md`
- v3 honest-abort: commit `48be1bd7` (clean-cue retrieval -> BC_CEILING)
- v3.1 (this prereg): v3 mechanism + noisy-cue retrieval

**Cell-author:** hdi_exp_dev
**Anchors (3-chunk):**
- `substrate_swr_v3_1_noisy_cue_replay_seed_7_v1_GPU`
- `substrate_swr_v3_1_noisy_cue_replay_seed_13_v1_GPU`
- `substrate_swr_v3_1_noisy_cue_replay_seed_19_v1_GPU`

**Shared core:** `experiments/_substrate_swr_v3_1_noisy_cue_replay_core.py`
**Queue:** overnight_queue (GPU; torch matmul + iterative cleanup loop)
**Tier:** MEASURED_MECHANISM
**Seeds:** [7, 13, 19] (one per cell)

## v3 -> v3.1 delta (minimal)

v3 (clean-cue retrieval) BC_CEILING'd at every M / seq_len tested
(cell-author 2026-06-30 sanity probe: capacity_ratio 0.05 -> 2.93 all
NO_REPLAY = 1.000). Root cause: single-pass Hebbian outer-product write
with clean queries at retrieval is exact regardless of M scaling.

v3.1 = SAME mechanism (iterative SEQUENCE replay with attractor cleanup
at every step on key + value) + NEW retrieval protocol: inject
`sigma_query * randn` noise on the recall cue, then L2-renormalize.
This makes iterative cleanup at write time meaningful: each replay pass
hardens cortex W against retrieval noise.

## Noise-injection sanity probe (cell-author MEASURED@2026-06-30)

At M=8192 / seq_len=100, single-pass NO_REPLAY recall under different
sigma_query:

| sigma_query | NO_REPLAY recall |
|------------:|-----------------:|
|        0.00 |            1.000 |
|        0.30 |            0.620 |
|        0.50 |            0.340 |
|        0.80 |            0.070 |
|        1.50 |            0.020 |
|        3.00 |            0.000 |

`sigma_query = 0.50` chosen as preregistered value: places NO_REPLAY
solidly inside the discriminating band (0.20 < R_NO_REPLAY < 0.80) with
ample headroom for iterative cleanup to lift toward DIRECT_UPPER.

## Mechanism (THEORETICAL@v3_spec; unchanged from v3)

```
for pass_idx in range(n_replay_passes):
    for k, v in zip(seq_keys, seq_vals):
        k_clean   = iterative_cleanup(k, keys_codebook)
        v_predict = W_cortex @ k_clean
        v_clean   = iterative_cleanup(v_predict, vals_codebook)
        W_cortex  = DECAY * W_cortex + ETA_REPLAY * outer(v_clean, k_clean)
```

Retrieval (v3.1 KEY CHANGE):
```
noisy_keys = L2_normalize(keys_c + sigma_query * randn(keys_c.shape))
preds      = noisy_keys @ W_cortex.T
recall     = (argmax(L2(preds) @ vals_codebook.T) == seq_idx).mean()
```

## Arms (5 per seed; META_RULE_AW identical config across seeds)

| Arm              | n_replay | Mechanism                              |
|------------------|---------:|----------------------------------------|
| ARM_NO_REPLAY    |        0 | Single batched Hebbian write; no replay |
| ARM_N_REPLAY_1   |        1 | Initial + 1 iterative replay pass      |
| ARM_N_REPLAY_5   |        5 | Initial + 5 passes                     |
| ARM_N_REPLAY_20  |       20 | Initial + 20 passes                    |
| ARM_DIRECT_UPPER |       -1 | Oracle: 10x eta direct write; ceiling  |

All arms recall under sigma_query=0.5 noisy-cue protocol.

## Regime

| Field          | Smoke | Full                                          |
|----------------|------:|-----------------------------------------------|
| M              |  4096 | 8192                                          |
| seq_len        |    50 | 100                                           |
| N_DIM          |  8192 | 8192                                          |
| N_CORTEX       |  2048 | 2048                                          |
| sigma_query    |   0.5 | 0.5  (META_RULE_AW: smoke = full discriminator) |
| n_replay sweep | (0,1,5,20) | (0,1,5,20)                              |
| seeds (per chunk) | [SEED] | [SEED]                                   |

Total units per chunk: 5 arms x 1 seed = 5. Across 3 chunks: 15 arm-instances.

## Pre-registered bands (per-seed; v3.1 retuned)

Let R_X denote recall_cortex for arm X.

**HARD_PASS (per-seed):**
- `R(NO_REPLAY) <= 0.40`               (HYPOTHESIZED@sigma=0.5 probe: ~0.34; gate at 0.40)
- AND `R(N_REPLAY_20) - R(NO_REPLAY) >= 0.30` (lift gate)
- AND `R(NO_REPLAY) <= R(N_REPLAY_1) <= R(N_REPLAY_5) <= R(N_REPLAY_20)` (monotonic)
- AND `R(N_REPLAY_20) < R(DIRECT_UPPER) - 0.03` (not BC-ceiling)
- AND all 5 arms OK (no errors)
- AND `cardinality_ok == True`
- AND arms-must-differ by SHA-256 hash (META_RULE_AF)

**MIDDLE_BAND (per-seed):**
- `R(N_REPLAY_20) - R(NO_REPLAY)` in `[0.10, 0.30)`

**HARD_FAIL (per-seed):**
- lift_20_vs_no < 0.10                       (no lift)
- OR `R(N_REPLAY_20) < R(NO_REPLAY) - 0.05`  (replay HURTS; cross-term accumulation)
- OR BC_CEILING: both NO_REPLAY and N_REPLAY_20 within 0.03 of DIRECT_UPPER
- OR any arm error / cardinality breach / META_RULE_AF duplicate hash

**Chain-grade verdict (Skunkworks aggregates):**
- HARD_PASS if all 3 seeds HARD_PASS AND `cv(R(N_REPLAY_20)) <= 0.10`
- MIDDLE_BAND if 2-of-3 HARD_PASS / MIDDLE_BAND
- HARD_FAIL otherwise

## META rules + SCHEMA-VET pre-reg fields

- cardinality_ok: true (5 arms x 1 seed = 5 units per chunk)
- EXPECTED_N_UNITS: 5 per chunk
- arms_differ_verified: true (per-arm SHA-256 of cortex W state + recall)
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH)
- crlb_n/a: "associative-memory capacity not Cramer-Rao bound; DIRECT_UPPER oracle arm = capacity-feasibility ceiling under sigma_query=0.5"
- discriminator_reachability: true. HYPOTHESIZED@cell-author probe: R_NO_REPLAY ~0.34 at sigma=0.5; gap to plausible DIRECT_UPPER ~0.6-0.7 gives 0.30+ headroom for iterative-cleanup lift
- baseline_in_band: true (HYPOTHESIZED 0.20 < R_NO_REPLAY < 0.40 at sigma=0.5; smoke-gate verifies)
- calibration_check: "default_ok_for_this_regime" (TEMP_CLEANUP=4.0 + MAX_STEPS=6 = hdlab defaults at D=2048+)
- cell_chunked: true
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: "passed_all_4_patterns"
- effective_vs_nominal_parameter_audit: aligned. effective n_replay = nominal; sigma_query is a single scalar applied identically across arms
- bracket_includes_discriminating_band: n_replay in {0,1,5,20} spans no-replay -> full-replay; under sigma=0.5 NO_REPLAY in middle band; lift target [+0.30] is reachable per oracle probe
- signal_shape_compatibility_audit: ALL edges SHAPE_MATCH (unchanged from v3)
- HP_SCOPE: lift gate applies to N_REPLAY arms only; NO_REPLAY = explicit baseline; DIRECT_UPPER = oracle ceiling
- META_RULE_AY: verdict logic explicitly demotes to HARD_FAIL on META_RULE_AF arm-hash duplicate (selftest_core + compute_seed_verdict both check)

## DISCRIMINATOR-MUST-SURVIVE-SCALE check (META_RULE_AG)

Smoke at M=4096 / seq_len=50 / sigma_query=0.5 (= SAME sigma as full;
the noisy-cue protocol IS the discriminator). Smoke must show:
- R(NO_REPLAY) in (0.05, 0.95) — middle band (not BC-trap)
- R(N_REPLAY_20) > R(NO_REPLAY) + 0.10 — discriminator fires
- Per-arm hashes distinct

If smoke shows R(NO_REPLAY) > 0.80 or R(N_REPLAY_20) - R(NO_REPLAY) < 0.05,
ABORT full dispatch (regime tuning needed; possible alternatives: bump
sigma_query, longer seq_len, longer n_replay).

## Dispatch destination + timeout

- Queue: overnight_queue (GPU)
- Timeout: 3600s/seed (2600 cleanup calls/seed at full; ~1.5s each at D=2048 with GPU; 4x margin)
- 3 chunks dispatched independently
- No PROT-018 _n suffix
- PROT-021 not triggered (3600s < 14400s threshold)

## Coordination

- Cell-author: hdi_exp_dev (this work)
- Dispatch: Director -> hdi_orchestrator (push gate harness-DENIED to cell-author)
- Landed-VET: hdi_skunkworks (chain-grade aggregation)

## Notes for Skunkworks chain-grade aggregation

- Read `data/exp_substrate_swr_v3_1_noisy_cue_replay_seed_{7,13,19}_v1_GPU/metrics.json`
- Chain-grade promotion = all 3 seeds HARD_PASS + cv(R_20) <= 0.10
- BC_CEILING gate (if DIRECT_UPPER trivially hits 1.000 under sigma=0.5, this would be unexpected; likely indicates oracle write strength too high; demote)
- META_RULE_AX cross-seed: per-arm `arm_hash` differs across seeds (random codebook per seed)
