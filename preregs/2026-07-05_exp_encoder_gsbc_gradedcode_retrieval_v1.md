# Prereg: exp_encoder_gsbc_gradedcode_retrieval_v1

Date: 2026-07-05
Author: exp_dev (cell author / prover)
Cell: `experiments/exp_encoder_gsbc_gradedcode_retrieval_v1_core.py`
Anchor: `encoder_gsbc_gradedcode_retrieval_v1`
Driver: Director hand-off. Attack the carry-through ship-metric's retrieval-agreement gap
(`exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_7` ret_agree10=0.1837
< 0.30) with a REPRESENTATION-side lever: graded/soft GSBC codes + STE-anneal, paired
against the hard block-STE the in-batch-RKD student currently deploys.

## Hypothesis
Hard block-STE quantization (one bipolar winner per block, no magnitude) loses the fine
rank ordering needed for top-10 retrieval agreement; graded/annealed GSBC codes (top-m
graded survivors per block, unit-L1 positive magnitudes for retrieval; block circular-conv
binding for algebra) preserve retrieval-relevant structure WITHOUT breaking bind/unbind.

## PRIOR-WORK CHECK (USER-locked concept-query + filesystem-verify Fix#28)
- substrate-KB concept-query "graded soft GSBC code straight-through estimator anneal
  temperature quantization retrieval agreement top-k" -> top hit cosine 0.2656 (Bengio-STE
  citation in a decode-side note); ALL hits <= 0.2656, NONE > 0.30. No prior arc CELL at
  threshold in the KB.
- FILESYSTEM (disk, not KB) shows the lever LARGELY LANDED. Both MEASURED on the SAME
  177899-concept teacher cache, FULL, 2 seeds each, HARD_PASS:
  - `exp_encoder_v11_gsbc_graded_sparse_v1` (graded GSBC top-3 + annealed soft->hard STE +
    listwise + absolute-cosine anchor). seed7 deployed BLOCK_LAST codes:
    - SIGN_BLOCK ret_agree10 = 0.2117, hi80_cos = 0.8290, keyed@J5 = 1.000
      MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/metrics.json:per_unit[SIGN_BLOCK_BLOCK_LAST]
    - GSBC_FULL  ret_agree10 = 0.3986, hi80_cos = 0.8338, keyed@J5 = 1.000
      MEASURED@ same :per_unit[GSBC_FULL_BLOCK_LAST]
    - LIFT = +0.1869; cosine PRESERVED (0.8338>=0.80); algebra PRESERVED (keyed@J5 1.000).
  - `exp_encoder_v12_gsbc_gwta_expansion_v1` (GSBC + FlyHash GWTA). seed7: GSBC_EXPAND2X
    ret_agree10 = 0.6027, hi80_cos = 0.8449, keyed@J8 = 1.000, keyed@J16 = 1.000.
- CONCLUSION: the task hypothesis is ALREADY CONFIRMED on disk. This cell is NOT a
  rediscovery of the lever. Its only genuine measurement gap vs the landed v11 is
  composed_roundtrip AT J10 for the GSBC_FULL graded code specifically (v11 gated keyed@J5
  only; v12 brackets J8=J16=1.0 but for the EXPAND2X code). This cell produces a single
  clean paired hard-vs-graded table in the carry-through ship regime with the stricter
  cosine>=0.80 + composed@J10>=0.95 gates. The Director can decide whether the confirming
  FULL GPU spend is warranted or whether landed v11/v12 already suffice (re-verdict path).
  Rediscovery-vs-novel: PAIRED CARRY-THROUGH of a proven lever into a stricter regime.

## Reuse (no shared-file edits)
Trainer/encode/keyed imported READ-ONLY from `v11` (the landed HARD_PASS code path):
`_train_student_v11`, `_encode_block_for_arm`, `_keyed_for_arm`, `_random_code_for_arm`,
`_reload_best_v11`, `_tau_at`, `_gsbc_code_from_z`, `_pin_determinism`. Semantic/charpos
units from `v3`. This cell is a THIN orchestrator; it does not reimplement graded machinery
and does NOT edit v3/v3c/v11.

## Arms (PAIRED; both via v11._train_student_v11; identical batch sampling)
- HARD_STE (baseline): mode=sign, kb=128, blk_l=32, m=1, recipe=rkd_only (== v11 SIGN_BLOCK
  == v3e in-batch-RKD hard block-STE). Algebra = SBC element circular-conv.
- GRADED (treatment): mode=gsbc, kb=32, blk_l=128, m=3, recipe=full (annealed soft->hard
  graded STE + soft/hard consistency MSE + listwise-rank ListNet + MANDATORY absolute-cosine
  anchor). Algebra = GSBC block circular-conv. (== v11 GSBC_FULL.)
Both N_DIM=4096, ~2-3% active, width 2048 (FULL) / 256 (smoke).

## Ship metric (measured on held concepts vs BGE teacher; same defs as carry-through)
- cosine_to_gold := hi80_cos = mean code cosine on teacher-highly-similar pairs (teacher_cos>=0.80)
- ret_agree10    := top-10 retrieval overlap with teacher's top-10 on held concepts
- composed_roundtrip := keyed bind/unbind roundtrip acc@1 at J_COMPOSED (harder composed load)

## Envelope-fail-bands (PAIRED; JOINT gate; per hand-off contract)
| Metric | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| ret_agree10 lift (graded - hard) | >= +0.05 | <= +0.02 | (0.02, 0.05) |
| graded cosine_to_gold (hi80) | >= 0.80 | < 0.80 | -- |
| graded composed_roundtrip @ J10 | >= 0.95 | < 0.95 | -- |
- HARD-PASS = lift >= +0.05 AND graded cosine >= 0.80 AND graded composed >= 0.95 AND baseline_in_band.
- HARD-FAIL = lift <= +0.02 OR graded cosine < 0.80 OR graded composed < 0.95 (a ret gain
  bought by wrecking calibration or algebra is a FALSE PASS -> HARD_FAIL, JOINT-gate discipline).
- MIDDLE = real but partial.
- Report ALL THREE for BOTH arms (per hand-off).
- HARD-PASS strictly above the +0.02 HARD-FAIL ceiling by > 5% band-width (META_RULE_L): the
  +0.05 floor is 3 band-widths above +0.02; the landed +0.1869 is far above.
- HP forecast: HARD_PASS (landed v11 +0.1869, cosine 0.8338, keyed@J5 1.000; the residual
  risk is composed@J10 specifically for GSBC_FULL, bracketed by v12 J8=J16=1.0). HYPOTHESIZED.

## Compute architecture
- Class: (a) batched-GPU. Substrate-primitive matmul-heavy (MLP forward, block/topk STE,
  Gram RKD, cosine retrieval, cleanup argmax). FULL routes to GPU (overnight_queue). Smoke
  runs CPU (local, no cuda). Per-phase-point wall > 10s => batching candidate: satisfied
  (single batched training loop per arm, not per-phase Python loop).
- Storage strategy: no_storage / no_composition of stored items (this is an encoder-quality
  cell; the keyed units are algebra roundtrip probes with per-trial fresh bundles, not a
  persistent sharded/bundled store). Sharded-vs-bundled default n/a.

## SCHEMA-VET gates
- cardinality_ok: True. EXPECTED_N_UNITS = 11 (per-arm {semantic, keyed@J_ISO,
  keyed@J_COMPOSED, shuffled@J_ISO, random-posctrl@J_ISO} = 5 x 2 arms + CHARPOS semantic).
  Verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if len(per_unit) < 11. (Not a sweep
  axis; fixed unit set.)
- effective_vs_nominal_parameter_audit (Gate A): n/a -- no parameter sweep (paired arms).
  sweep_alignment_verdict: ALIGNED (trivially; no swept param).
- discriminating_fraction (Gate B): n/a -- not a sweep. The single discriminator (ret lift)
  is in a measurable band by construction: landed hard baseline ret ~0.21, graded ~0.40
  (neither floor nor ceiling). discriminating_fraction: 1.0 (the one comparison is in band).
- composition_edges (Gate C): none. Each arm is a single primitive (BGE embedding -> MLP ->
  code); no primitive->primitive edge. SHAPE_MATCH n/a (no cross-primitive adapter needed).
- positive_control_arms (Gate D): the HARD_STE arm reproduces the prior chain-grade hard
  block-STE at the test regime.
  - arm: HARD_STE, primitive: in-batch-RKD hard block-STE (v11 SIGN_BLOCK / v3e)
  - cited_prior_metric: ret_agree10 = 0.2117 MEASURED@v11 seed7 SIGN_BLOCK_BLOCK_LAST
  - cited_prior_regime: {N: 4096, K_blocks: 128, teacher: bge 177899, in_batch RKD}
  - test_regime: SAME (177899 cache, N=4096, K=128). tolerance: 0.05.
  - regime_extension_audit: SHAPE_MATCH (identical trainer/geometry; only the eval is
    re-pointed at the ship gates). Additional pos-ctrl: RANDOM_HARD / RANDOM_GRADED keyed@J5
    (training-INDEPENDENT algebra machinery, expect ~1.0) -- the algebra discriminator.
- functional_requirements (Gate E):
  1. Preserve BGE semantic geometry on high-similarity pairs -> RKD/anchor backbone (v11).
  2. Preserve top-10 retrieval neighborhood vs teacher -> graded magnitudes + listwise-rank.
  3. Preserve bind/unbind algebra under composed load -> GSBC block circular-conv (format-
     preserved, zero-training per v11 fact 4); HARD-GATE keyed@J10 + no-leak.
  4. Not buy retrieval by wrecking absolute cosine -> absolute-cosine anchor (Lever 2c);
     hard-gate cosine_to_gold >= 0.80.
- CRLB / capacity-feasibility: crlb_floor_computed = 0.901 THEORETICAL
  (r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K), K=128; block channel). The
  discriminator here is a ret-agreement LIFT (not a noise-floor threshold), so crlb is a
  reference bound not a reachability gate. discriminator_reachability: True -- the +0.05
  HARD-PASS lift is far below the MEASURED@ landed +0.1869 lift.
- calibration_check: default_ok_for_this_regime -- identical hyperparameters to the landed
  v11 arms; only the eval is re-pointed at the carry-through ship gates.
- baseline_in_band (META_RULE_AG): CHARPOS ret_agree10 in (0.05, 0.95). At smoke charpos_ret
  = 0.11 -> in band. The paired arms are NOT saturating baselines (hard ~0.21, graded ~0.40).

## Discriminator-survives-scale (mandatory pre-flight)
Option (B) analytical + prior-landed. The ret-lift discriminator is a FULL-only question:
smoke V=20820 cache / 800 held / 200 steps / width 256 does not crystallize the retrieval
regime (smoke MEASURED lift = -0.0231, both arms ret ~0.46-0.49 -- same non-discriminating
behavior v11's own smoke showed). Smoke instead fires the ALGEBRA discriminator via the
training-independent random-code positive control (RANDOM_HARD/RANDOM_GRADED keyed@J5 = 1.000
for BOTH sbc and gsbc_circconv) + shuffled-key leak control (0.000) + arms-differ. The
FULL-scale lift is MEASURED@ landed v11 (+0.1869) and v12 (+0.16..+0.39): the discriminator
provably survives scale. FULL is the honest measurement of the paired lift under the stricter
ship gates.

## Defensive error-checking (all 4 patterns)
- cell_chunked: False (single-seed; multi-seed FULL via re-dispatch of --seed).
- start_marker_written: True. crash_diagnostic_present: True (Exception -> CELL_CRASHED +
  traceback, atomic tmp+os.replace, except SystemExit/KeyboardInterrupt re-raised first).
- heartbeat_present: True (_heartbeat.jsonl per unit + per train phase).
- No bare except / no except BaseException (grep gate CLEAN). Per-unit failure-class in _run_unit.
- final_metrics_atomicity: tmp_replace (write_metrics atomic).
- arms_differ_verified: sha256 over float32 code bytes (NOT int8 -- graded codes fractional).

## progress_logging (MANDATORY; FULL timeout_s >= 1800)
progress_logging: "print_flush_true" (sys.stdout line_buffering + flush=True on every
[graded]/[v11_gsbc] progress line; train prints every 200 steps + heartbeat). FULL cadence
< 60s between log lines during training.

## Dispatch plan
- SMOKE: local_cpu (CPU) -- DONE, HARD_PASS (SMOKE_MACHINERY_OK), 15.2s.
- FULL: GPU (overnight_queue), 2 training arms x 8000 steps on 177899 concepts. Estimated
  ~600-900s on GPU (v11 3-arm FULL landed 465-565s; this is 2 arms). Timeout: 3600s.
  Multi-seed: seeds {7, 13} (matches v11/v12 seed set for cross-comparability); each via
  separate --seed dispatch. HEAVY GPU -> staged, NOT self-dispatched (exp_dev cannot push;
  routes through Orchestrator). Director decides GPU-spend vs re-verdict of landed v11/v12.

## Self-test / smoke record (measured this cycle)
- --self-test: PASS (anneal-schedule monotone + graded-code unit-L1/top-m invariants +
  hard-block-STE one-per-block + BOTH-algebra roundtrip pos-ctrl + shuffled-leak + paired
  verdict bands HP/MB/HF/calib/algebra/posctrl/leak/cardinality/smoke), 0.10s.
- --smoke (CPU, seed 7): HARD_PASS SMOKE_MACHINERY_OK, 15.2s, 11/11 units, arms_differ,
  RANDOM_HARD/RANDOM_GRADED keyed@J5=1.000, shuffled 0.000. MEASURED@data/exp_encoder_gsbc_gradedcode_retrieval_v1_smoke/metrics.json
