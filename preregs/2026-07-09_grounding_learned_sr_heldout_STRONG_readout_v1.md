# Pre-registration: READOUT-vs-ENCODER separation on learned-SR held-out reasoning

- cell: `experiments/exp_grounding_learned_sr_heldout_STRONG_readout_v1.py`
- anchor_name: `grounding_learned_sr_heldout_STRONG_readout_v1`
- date: 2026-07-09
- author: exp_dev
- complements (do NOT overlap files): a235164e (trains NEW structure-aware codes = tests the ENCODER, #1).
  THIS cell keeps codes FIXED and varies the READOUT (#3).

## Question
The audit of `grounding_learned_sr_heldout_reasoning_v1` (HARD_FAIL_CG_MEMORIZED_SEARCH) found "it's the encoder"
OVER-ATTRIBUTED: the proven negative is the COMPOSITE (current codes + a WEAK kNN-softmax smoothing readout) failing
together, yet the codes carry weak-but-real held-out structure (Phase-0 M5 held-out edge AUC ~0.69-0.73) the weak
readout cannot convert. Does a STRONG readout on the SAME current codes rescue held-out reasoning?

Instantiates META_residual_gap_decomposition (substrate KB, 2026-07-07): AGGREGATION-LOSS (recoverable by a smarter
read-out) vs REACHABILITY-CEILING (needs a better encoder). Readout-was-the-limit vs encoder-is-the-wall.

## Codes held FIXED
Z_vis reproduced DETERMINISTICALLY (same seed + same `train_binding_encoder_dev` code path + same cfg as the anchor).
No encoder change. Every readout consumes the SAME Z_vis; only the WITHHELD-row reachability estimate differs.

## Arms (paired; held-out subset; identical Z_vis base + seeds + graph + chains + split)
- WEAK_LEARNED / WEAK_RANDOM: anchor kNN-softmax smoothing (reproduces the anchor codes_necessary=False).
- KERNEL_LEARNED / KERNEL_RANDOM: dual RBF-cosine kernel ridge (PRIMARY strong readout).
- RIDGE_LEARNED / RIDGE_RANDOM: primal linear ridge (secondary strong readout; "which won").
- HELDOUT_MEMCTRL: punched-hole floor (no re-estimation).
- General anchors (Gate-D + anti-sat): NO_CLEANUP (must-fail), MEMORYLESS (floor), SUPPLIED_WAYPOINT (MM ceiling),
  KNOWN_T_FULL (full-map SEARCH baseline). KNOWN_T_FULL on held-out also defines the completable subset + ceiling.

All strong/weak readouts train ONLY on VISIBLE (code -> visible reachability); withheld nodes never appear in
training -> no leakage.

## Fair-test refinements (baked in)
- reach@1 (un-compounded) = PRIMARY; reach@2 secondary.
- margins on the DETERMINATE COMPLETABLE subset = held-out chains KNOWN_T_FULL solves at hop-1.
- reciprocal-necessity margin = strong-readout(learned) - strong-readout(random) at reach@1.

## Discriminator (pre-registered; strong_margin1 = best over {KERNEL,RIDGE}; on completable subset)
- HARD_PASS_READOUT_WAS_THE_LIMIT: `strong_margin1 >= 0.05` AND `weak_margin1 < 0.05` AND
  `strong_margin1 >= weak_margin1 + 0.03` AND `readout_adds_signal` (best strong-learned reach@1 >= MEMCTRL floor
  + 0.05). -> it was the READOUT; codes carry usable structure; encoder NOT the sole wall.
- HARD_FAIL_ENCODER_CONFIRMED: `best_strong_margin1 < 0.02` -> even the best strong readout ties random -> encoder
  is the wall (supports a235164e encoder-sharpening).
- MIDDLE_BAND_PARTIAL_READOUT_RESCUE: `0.02 <= strong_margin1 < 0.05`.
- MIDDLE_BAND_WEAK_ALREADY_SEPARATES: `weak_margin1 >= 0.05` on the completable subset (the restriction, not the
  strong readout, surfaced usable codes).

## Bands (picked BEFORE the run)
- READOUT_MARGIN_HP = 0.05; READOUT_MARGIN_MID = 0.02; WEAK_MARGIN_MAX = 0.05; STRONG_OVER_WEAK_MIN = 0.03;
  NEC_MARGIN = 0.05; MIN_COMPLETABLE_CHAINS = 40.
- Strong-readout knobs (PRE-REGISTERED, NOT tuned on real data; validated on the planted self-test):
  KRR_ELL = 0.25; KRR_LAM = 0.1; RIDGE_LAM = 1.0.
- Reused fixed: WITHHELD_FRAC = 0.30; SMOOTH_K = 8; SMOOTH_TEMP = 0.10; SR_GAMMA_PRIMARY = 0.85; SR_BOOST = 1.5.

## Reference numbers
- anchor LEARNED_HELDOUT reach@1 = 0.362, reach@2 = 0.115  MEASURED@data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json:gates.reach.LEARNED_HELDOUT
- anchor CODEALIAS reach@1 = 0.332, reach@2 = 0.104  MEASURED@same:gates.reach.HELDOUT_CODEALIAS
- anchor codes_necessary (weak) = False (delta@2 = 0.011)  MEASURED@same:gates.cg.codes_necessary
- Phase-0 M5 held-out edge AUC = 0.694-0.731  MEASURED@data/phase0_code_structure_precheck_result.json:per_size[*].M5_heldout_auc
- Gate-D anchors: mem1=0.453, sup1=0.756, sup2=0.500, knownT2=0.434  MEASURED@same anchor metrics
- top-1 chance floor = 1/n_nodes ~ 0.0002  THEORETICAL

## SCHEMA-VET
- cardinality_ok: true (EXPECTED_N_UNITS = n_seeds; per-seed arm-depth cardinality gate + HARD_FAIL_CARDINALITY_BREACH_META_RULE_H)
- arms_differ_verified: true (WEAK_L!=WEAK_R, KERNEL_L!=KERNEL_R, RIDGE_L!=RIDGE_R, KERNEL_L!=WEAK_L per seed)
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace)
- except SystemExit: raise BEFORE except Exception; no bare/BaseException (grep-gated clean)
- crlb_n/a: "discriminator is a learned-vs-random MARGIN; 0.05 bar clears the 0.02 FAIL side; no closed-form noise floor"
- discriminator_reachability: true (self-test: strong readouts reach margin ~0.74 on planted recoverable structure)
- baseline_in_band: MEMORYLESS@1 in (0.05,0.95); NO_CLEANUP@2 collapses (anti-saturation; RANDOM-code control fails at self-test scale)
- HP_SCOPE: {KERNEL_LEARNED/RIDGE_LEARNED: [readout_was_the_limit vs own random control]; WEAK_*: [reproduce anchor]; NO_CLEANUP: [must-fail]; MEMORYLESS/SUPPLIED/KNOWN_T_FULL: [Gate-D repro]; HELDOUT_MEMCTRL: [hole floor]}
- positive_control (Gate D): mem1/sup1/sup2/knownT2 + WEAK_LEARNED reach@2 ~0.115 + WEAK_RANDOM reach@2 ~0.104 at FULL; drift>0.10 -> INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT
- calibration_check: adaptive_with_discriminator_gate (knobs pre-registered; planted self-test proves recover-on-structure + collapse-on-random)
- effective_vs_nominal_parameter_audit: no swept nominal-vs-effective parameter (fixed WITHHELD_FRAC condition; hop-depth d in {1..4} reported); sweep_alignment_verdict: ALIGNED
- bracket_includes_discriminating_band: the discriminator is a margin around 0; anchor weak margin 0.03 (below 0.05); the strong-readout margin is the measurement; self-test shows the mechanism CAN reach 0.74 -> discriminating band reachable
- composition_edges: strong readout (code->reachability regressor) -> run_sr_arm routing loop; A_output = per-node reachability column [n,U]; B_input = sr_p [C,n+1] via _norm_columns_to_sr_p (VERBATIM anchor normalization); verdict: SHAPE_MATCH
- positive_control_arms: KNOWN_T_FULL / MEMORYLESS / SUPPLIED reproduce anchor at test regime; WEAK arms reproduce anchor readout; tolerance 0.10
- functional_requirements: (1) estimate withheld-node reachability from codes -> strong readout (kernel/linear ridge); (2) route by reachability -> certified run_sr_arm (VERBATIM); (3) reciprocal necessity -> learned-vs-random paired arms; (4) fair denominator -> completable-subset restriction
- cell_chunked: false (multi-seed loop with per-seed try/except + write_partial + cardinality gate; anchor ran this shape 35s FULL)
- start_marker_written: true; crash_diagnostic_present: true; heartbeat_present: false (short cell; per-seed flush logs)
- defensive_error_checking: "per-seed try/except with failure_class capture + write_partial + start/crash markers + cardinality gate; short cell (anchor 35s FULL cuda)"
- progress_logging: print_flush_true (line_buffering + per-seed/per-arm flush)
- run_mode default: full (explicit --smoke / --self-test flags; queue passes no flag -> full)

## Dispatch
- SMOKE: local_cpu_queue (smoke-only per USER-lock) OR direct local run (done).
- FULL: remote_cpu_queue (matmul/dense-solve; codes retrained deterministically; anchor ran cuda 35s -> remote CPU
  minutes). 3 seeds. exp_dev hands the queue_add line to the orchestrator (remote dispatch not run by exp_dev).
