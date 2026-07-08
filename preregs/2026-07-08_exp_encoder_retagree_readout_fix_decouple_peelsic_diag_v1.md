# Pre-reg: encoder ret_agree10 readout-fix diagnostic (decouple / peel-SIC)

- anchor_name: `encoder_retagree_readout_fix_decouple_peelsic_diag_v1`
- date: 2026-07-08
- author: exp_dev
- core: `experiments/exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1_core.py`
- seed wrappers: `_seed_7.py` / `_seed_13.py` / `_seed_23.py`
- class: DIAGNOSTIC / MEASUREMENT ONLY. NO re-ingest, NO KB mutation, NO
  operational default change. Writes only to its own `data/exp_<anchor>/metrics.json`
  and an isolated artifact dir (`data/substrate_retagree_diag_v1{_smoke}_seed<S>/`).

## Question
The trained INBATCH-RKD SBC block encoder has strong POINTWISE fidelity but fails
TOP-10 retrieval agreement:
- cosine_to_gold(hi80) = 0.8611 (>=0.80 PASS)  MEASURED@data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_7/metrics.json:ship.cosine_to_gold
- composed_roundtrip = 0.9833 (>=0.95 PASS)     MEASURED@ same :ship.composed_roundtrip
- spearman_all = 0.8969                          MEASURED@ same :ship.spearman_all
- ret_agree10 = 0.1837 (<0.30 FAIL)              MEASURED@ same :ship.ret_agree10

Do our OWN certified retrieval mechanisms close ret_agree10 as a READOUT-time fix
(no re-ingest)?
- arm A (decouple law): ZCA-whitened / decorrelated retrieval codes
  (reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval).
- arm B (peel/SIC): certified `peel_sic_readout` mode='proj' matching-pursuit top-10
  (CG: commit 916e6f7cb / c2f65e53d).

## Arms (all compute ret_agree10 on the SAME held queries vs the SAME held corpus,
matching v3._semantic_unit top-10 overlap contract)
- baseline    raw student code cosine top-10   [DISCRIMINATOR: must FAIL <0.30]
- armA_whiten ZCA-whitened retrieval codes
- armB_peelsic peel/SIC matching-pursuit readout

## Bands (declared BEFORE run; strict per META_RULE_L)
- HP_RET_AGREE10 = 0.30 (gate floor; HYPOTHESIZED@Director hand-off contract)
- HARD_PASS  max(armA,armB) >= 0.315 AND >= baseline + 0.02
- HARD_FAIL  max(armA,armB) < 0.30 (neither readout fix lifts -> gap is elsewhere)
- MIDDLE_BAND 0.30 <= max(armA,armB) < 0.315 (at-floor; inconclusive)
- discriminator_fires: baseline ret_agree10 < 0.30 (else SMOKE_GATE_FAIL)

## Compute architecture
- class: (a) batched-GPU. FULL trains the INBATCH-RKD MLP student (matmul-heavy) and
  runs top-10 retrieval matmuls over the held corpus + a 4096x4096 cov-eigh whitening
  + batched matching-pursuit; all GPU-batched. SMOKE is CPU (synthetic, no training).
- storage strategy: no_storage / no_composition (this is a retrieval-READOUT
  diagnostic over a fixed code set; no items are stored/bundled/chained).

## Discriminator-must-survive-scale
- Path B (analytical) + SMOKE preview. The failing baseline is intrinsic to the
  SBC quantization + BGE neighborhood crowding, both of which are present at every
  scale. SMOKE (synthetic random-proj+SBC of the REAL teacher) reproduces the
  regime: baseline=0.1944 (near the real 0.184), teacher_margin=0.0509 (near the
  real ~0.056). FULL measures on the REAL trained codes.

## Positive control (Gate D)
- The baseline arm IS the reproducer: at the test regime it must reproduce the
  shipmetric ret_agree10 ~= 0.184 (tolerance ~0.05). If baseline deviates far,
  the code path is wrong. cited_prior_metric=0.1837, test_regime=matched.

## SMOKE RESULT (LOCAL CPU, seed 7) -- MEASURED@data/exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1_smoke/metrics.json
- baseline_ret_agree10 = 0.1944 (< 0.30 -> DISCRIMINATOR FIRES; matches real 0.184)
- armA_whiten_ret_agree10 = 0.0976 (HURTS vs baseline)
- armB_peelsic_ret_agree10 = 0.1058 (HURTS; torch-SIC == certified numpy
  peel_sic_readout parity 0.1050)
- diagnostics: teacher_margin_top1_top10=0.0509 (crowded neighborhood, near-ties);
  code_mean_nnz=128 (SBC sparse); code_offdiag_corr_abs=0.0112 (SBC already
  near-decorrelated -> the DECOUPLE law has little to act on at readout).
- SMOKE verdict = HARD_FAIL. Machinery validated; discriminator fires; parity ok.
- INTERPRETATION (preview, synthetic): neither readout fix lifts ret_agree10; both
  hurt. The gap is a QUANTIZATION-RESOLUTION vs neighborhood-crowding problem, not a
  code-correlation (whitening no-op on already-sparse code) or bundle-decomposition
  (query is a single vector, not a member-sum; SIC deflation suppresses the
  genuinely-similar true neighbors in a crowded cluster) problem. This REINFORCES
  routing to the graded-code / STE-anneal (finer-quantization) lever that the
  shipmetric MIDDLE_BAND verdict itself pointed to.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS=3 = baseline+armA+armB; verdict counts len)
- arms_differ_verified: true (baseline vs whitened code hashes differ; armB is a
  distinct matching-pursuit algorithm)
- final_metrics_atomicity: write_metrics (tmp + os.replace)
- calibration_check: default_ok_for_this_regime (SMOKE_NOISE calibrated so synthetic
  baseline approximates the real 0.184 failing regime; not tuned for a PASS)
- crlb: n/a (retrieval-agreement diagnostic; no capacity noise-floor estimator)
- discriminator_reachability: true (baseline provably below gate at scale)
- baseline_in_band: true (0 < baseline < 0.30)
- except SystemExit: raise BEFORE except Exception (no BaseException) -- verified
- cell_chunked: true (single-seed-per-cell wrappers 7/13/23)
- start_marker_written / crash_diagnostic_present / heartbeat_present: true
- defensive_error_checking: passed_all_4_patterns
- progress_logging: print_flush_true (line_buffered stdout + flush=True)
- HP_SCOPE: {armA_whiten: [ret_agree10], armB_peelsic: [ret_agree10]}

## Functional requirements
- FR1 measure WHY ret_agree10 fails -> diagnostics (neighborhood margin, code
  sparsity, code-dim correlation).
- FR2 test the decouple law at readout -> armA_whiten (ZCA).
- FR3 test peel/SIC at readout -> armB_peelsic (certified peel_sic_readout proj).
- FR4 discriminator: baseline must fail like the real encoder.

## FULL dispatch (GPU; hand off to orchestrator; do NOT dispatch from exp_dev)
- queue: overnight_queue (GPU)
- seeds: 7, 13, 23 (3 seed wrappers)
- timeout: 1800 s per seed (teacher load 1.35GB + mining + train ~112s + arms)
- NOTE to Director: SMOKE (faithful synthetic) strongly predicts FULL HARD_FAIL for
  BOTH readout arms. The FULL is a lever-CLOSING real-code measurement (not
  busy-work): it definitively answers whether decouple/peel-SIC READOUT transforms
  can rescue ret_agree10 on the real trained encoder, or whether the fix must be the
  graded-code (training-time, finer-quantization) lever already in motion.
