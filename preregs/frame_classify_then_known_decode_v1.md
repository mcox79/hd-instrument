# Pre-registration: frame_classify_then_known_decode_v1

**Filed-by:** exp_dev
**Filed-at:** 2026-07-05
**Cell:** `experiments/exp_frame_classify_then_known_decode_v1.py`
**Metrics path:** `data/exp_frame_classify_then_known_decode_v1/metrics.json`
**Source research:** `notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md`
+ hand-off `notes/research_comprehension_frame_classify_then_decode_experiment_proposal_2026-07-05.md`

**Prior-work check (substrate-KB concept-query, USER-locked):** `bash tools/substrate_query.sh "frame recognition classify then decode role filler parse unknown structure comprehension"` -> top hit `recognition` (wordnet) cosine=0.294 (< 0.30 threshold); `comprehension` (wordnet) 0.282. NO prior arc cell at cosine>0.30. GENUINELY NOVEL: frame-UNKNOWN classify-then-decode has no prior substrate atom (the block-local decoder is frame-KNOWN; the dense blind resonator is a different algebra). Not a rediscovery.

---

## Capability / question

OPEN the COMPREHENSION capability: parse an UNKNOWN bound proposition into its role-filler structure with NO external position cue. The frame-UNKNOWN blind factorization has only ever been tried with the DENSE multiply-bind algebra (exact_ordered = 0.000 twice). This cell tests whether the sparse-block geometry, plus a cheap non-learned frame-recognition step, recovers the frame from the bound vector ALONE on REAL correlated GSBC fillers, then decodes via the already-proven block-local decoder (Helmholtz-machine recognition+generation split; Hickok-Poeppel dual-stream).

## Arms (PAIRED -- same propositions + same true frames across arms)

- **sparse_block** (PRIMARY, new): matched-filter occupancy classifier (non-learned, per-block L2 energy) -> block-local per-block argmax decode.
- **dense_ctrl** (negative control, LIVE): SAME real fillers, DENSE multiply-bind; occupancy classify ONLY (decode collapse is CITED 0.000, not rerun). Expected frame_class ~ chance 1/F.
- **known_frame_posctrl** (positive control, Gate D): block-local decode with the TRUE frame given (no classification) -> reproduces the cited ceiling AT the test regime.

**Frame definition:** a frame = a distinct sorted D-subset of B_TOTAL=8 blocks; role d -> the d-th smallest block. F candidate frames drawn deterministically (FRAME_SET_SEED). Permutation-within-a-fixed-subset frames (occupancy-degenerate; need a content-based classifier) are OUT OF SCOPE for this first attempt -- deferred.

## Regime (apples-to-apples with the cited baselines)

- N=8192, GSBC_DIM=8192, F_SPARSE=0.02 (matches `exp_generation_decoder_gsbc_native_blocklocal_v1`).
- B_TOTAL=8 -> bs=1024 (clean); D_ROLES=3; V=1024 (anchor). k = round(0.02*1024) = 20 active/block.
- C(8,3)=56 >= F (F=8 smoke, F=16 FULL).
- Native GSBC fillers from `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` (real cos-cone; untracked npz -- SCP to remote before FULL; queue_add does NOT auto-ship it).

## Metric (report SEPARATELY per Fix #28 -- never collapse to one aggregate)

- `frame_classification_accuracy` = mean[ frame_pred == frame_true ]
- `conditional_decode_accuracy` = mean over {frame_pred==frame_true} of [ exact_ordered_decode == 1 ]
- `parse_accuracy` (chained) = mean[ frame_pred == frame_true AND exact_ordered_decode == 1 ]

## Pre-registered bands (LIFTED VERBATIM from the research note)

- **HARD-PASS:** frame_classification_accuracy >= 0.90 (F=8-16) AND chained parse_accuracy >= 0.75, cv <= 0.05, >= 3 seeds.
- **HARD-FAIL:** frame_classification_accuracy <= 0.40 OR parse_accuracy <= 0.15.
- **MIDDLE/PARTIAL (informative, non-gating):** frame classification succeeds but chained decode underperforms (error-propagation / wrong-frame poisoning downstream); OR frame accuracy degrades sharply with candidate count (that is Arm 4, deferred).
- **Default tier MIDDLE** (Fix #28; let cert-owner tier up).
- P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.42 / 0.33 / 0.25 (research lit-scan calibrated; novel-synthesis cap 0.50).

**HONEST framing of the expected result (BIAS-13/BIAS-S guard, USER-locked):** sparse_block frame_classification is expected HIGH (~1.0) and is occupancy-robust BY CONSTRUCTION (each used block holds exactly one filler, per-block energy = k regardless of filler identity -> correlation-independent). This is the MECHANISM (sparse-block exposes structure the dense algebra entangles), made EXPLICIT and AUDITED, NOT a hidden saturation. It is PROVEN load-bearing by the live dense_ctrl negative control (dense binding -> occupancy ~uniform -> frame_class collapses to chance). The correlation-stressed quantity that CAN fail is the DECODE (parse) -- HARD-FAIL is reachable via decode collapse. At the anchor V=1024/D=3 regime the cited known-frame decode is 1.000, so parse ~1.0 is the pre-registered expectation; the genuine decode-correlation stress lives at the boundary (@V8192D26 -> 0.856), deferred to the scaling arm.

## Discriminator-fires gates (smoke MUST satisfy; META_RULE_K)

1. `sparse_frame_class - dense_frame_class >= FRAME_GAP_MIN (0.50)` -- occupancy carries frame ONLY under sparse-block geometry (paired negative control). MEASURED@smoke: gap=0.625. FIRES.
2. `known_frame_posctrl decode >= POS_CTRL_DECODE_FLOOR (0.90)` -- Gate D: block-local decode reproduces the cited ceiling AT the test regime. MEASURED@smoke: 1.000. REPRODUCES (no bs bump needed).

## CITED baselines (do NOT rerun -- already on disk)

- dense blind decode = 0.000  MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms['dense_gsbc_fullreso@V1024D3'].exact_ordered_mean
- dense blind roundtrip = 0.000  MEASURED@data/exp_generation_decoder_roundtrip_v1/metrics.json:arms.real_fullreso_hi.exact_ordered_mean
- known-frame ceiling = 1.000 (@V1024D3) / 0.856 (@V8192D26)  MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms['blocklocal_gsbc@...']

## SCHEMA-VET mandatory fields

- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds * n_arms (FULL = 3 * 3 = 9; smoke = 1 * 3 = 3). Verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short.
- `arms_differ_verified`: true (cb_gsbc vs dense_lex hash-distinct; sparse vs dense composites hash-distinct; F frame templates pairwise-distinct).
- `arms_differ_exempted`: none.
- `final_metrics_atomicity`: tmp_replace.
- `crlb_floor_computed`: n/a. `crlb_n_a`: block-local decode on disjoint blocks has NO within-block superposition noise (each used block holds exactly one filler); frame-classification via occupancy is deterministic set-matching. The only noise channel is cross-code overlap in the per-block cleanup, bounded empirically by known_frame_posctrl (MEASURED 1.000 at regime). `discriminator_reachability`: true (HARD-FAIL parse<=0.15 reachable if decode collapses under correlation).
- `baseline_in_band`: dense_ctrl frame_class ~ chance (0.375 smoke small-sample / ~0.0625 at F=16), NOT saturated; it is the negative control expected at chance. sparse_block is the mechanism arm (not a baseline); its ~1.0 is the result, and the discriminator is the sparse-vs-dense GAP (not the absolute value).
- `discriminator_survives_scale`: option A + C. Smoke runs AT full N=8192 and full anchor V=1024 (only trials/seeds/F reduced). Discriminator gates fire in smoke (gap=0.625; posctrl=1.000).
- `HP_SCOPE`: {sparse_block: [HP_frame_class, HP_parse, cv_max], dense_ctrl: [negative_control_expected_at_chance], known_frame_posctrl: [pos_ctrl_decode_floor]}.
- `calibration_check`: default_ok_for_this_regime (non-learned matched filter; no tuned thresholds; occupancy energy is parameter-free; codebook construction reused verbatim from the cited HARD_PASS cell).
- `cell_chunked`: false (3 seeds in-cell; cell wall < 60s, single-seed loss risk negligible; start-marker + crash-diagnostic + heartbeat present).
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED, SystemExit/KeyboardInterrupt re-raised). `heartbeat_present`: true. `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: print_flush_true (line_buffered stdout + flush prints; cell wall << 1800s so heartbeat cadence not gating).
- `run_mode_verification`: cell asserts written run_mode == mode; defaults to full (explicit --self-test / --smoke).

## §15 composition/sweep gates

- `sweep_alignment_verdict`: ALIGNED (no parameter sweep in this cell; F fixed per mode; Arm 4 frame-count sweep DEFERRED).
- `discriminating_fraction`: n/a (no sweep axis). The single test point is discriminating by the sparse-vs-dense gap + parse-vs-dense-0.000.
- `composition_edges`: frame_classifier (output: predicted frame index) -> block_local_decoder (input: frame index). verdict: SHAPE_MATCH (frame index is exactly the decoder's position-cue input).
- `positive_control_arms`: known_frame_posctrl REPRODUCES the block-local decoder at the TEST regime (bs=1024/V=1024). cited_prior_atom: blocklocal_gsbc@V1024D3=1.000. tolerance: 0.10. MEASURED@smoke: 1.000 (in tolerance). regime_extension_audit: SHAPE_MATCH (same N/GSBC_DIM/F_SPARSE/pool; only bs=1024 vs cited 2730 -- bigger V-way headroom, verified reproduces).
- `functional_requirements`: (1) recover the frame (which role -> which block) from the bound vector without a cue -> occupancy matched filter; (2) decode fillers given the frame -> block-local argmax (proven); (3) prove the frame signal requires sparse-block geometry -> dense_ctrl collapse.

## Compute architecture

- Class: (b) sequential-CPU with justification. The matched-filter classifier is NOT a trained net; per-trial work is O(V*bs) block-argmax + O(F*B_TOTAL) matched filter. Full wall < 60s CPU (smoke 4.3s MEASURED). No GPU speedup available/warranted; no matmul-in-loop hot path beyond the single (V,bs) cleanup gemv per block. Storage strategy: no_storage (synthetic-per-trial compositions; read-only on substrate; native filler pool is a fixed offline cache). No composition/chained-retrieval -> sharded/bundled N/A.

## Dispatch plan

- SMOKE: local (direct `--self-test` + `--smoke`). MEASURED HARD_PASS (see smoke results in report).
- FULL: F=16, 3 seeds (7,13,19). Per USER-lock SMOKE-ONLY-on-local + canonical-run-is-remote, FULL routes to **remote_cpu_queue** via Orchestrator (exp_dev cannot push). Pool npz must be verified present on remote (untracked; already SCP'd for the cited gsbc cell -- VERIFY).
- Arm 4 (frame-count scaling sweep 8/16/32/64...) DEFERRED until this lands (per hand-off).
- `--timeout` FULL: 600s (measured full ~10s; 60x margin for slow remote CPU + pool load).
