# Pre-reg: grounding_rung2_loop_closer_v1 (RUNG-2b LOOP-CLOSER)

Filed 2026-07-10 (exp_dev). Cell: `experiments/exp_grounding_rung2_loop_closer_v1.py`.
Bands + discriminator picked BEFORE the FULL run. The LOW-stratum-positive decision and the ablation control are
load-bearing and are NOT loosened (Director contract).

## Claim
Consolidating the ConceptNet graph WITH the fused independence-selected MEASURED attributes (concreteness +
sensory-modality + AoA) produces an entity geometry that improves HELD-OUT RELATIONAL inference (predict a withheld
edge's target) DEGREE-INVARIANTLY -- turning the additive code's LOW-degree tail-collapse (LOW gap = -0.040
MEASURED@data/exp_grounding_additive_geometric_degree_control_v1/metrics.json:gates.strata.LOW.delta_transe_discrete)
into a POSITIVE tail lift. If yes, grounding is the relational lever and the arc closes. If no, grounding predicts
attributes but does not transfer to relational inference (a valid bounded negative).

## Apparatus (reused verbatim)
- Relational task = exp_grounding_additive_geometric_degree_control_retest_v1 (rt.*): COMPLETABLE reach@1 (filtered
  Hits@1 on held-out completable directed triples), degree strata LOW/MID/HIGH by true-tail visible degree, degree-only
  POPULARITY baseline, RANDOM (codes-necessary), ORACLE (oracle-leak / setup-works). HELDOUT_FRAC=0.30, N_RANK_NEG=99.
- Grounded geometry = exp_grounding_consolidation_loop_degree_invariant_v1 (eng.*): structural_features + exterior
  channel -> cross-channel agreement kNN graph -> normalized-Laplacian diffuse-with-restart (anti-collapse,
  degree-balancing) -> freeze entity codes -> fit additive relation offsets on visible edges -> score -||E_h+R_r-E_t||.
- Grounding source = exp_grounding_multiattribute_fusion_v1 (fus.*): data acquisition (curl to data/grounding_testbed/,
  provenance-tracked, NOT canonical store, NEVER git add -A) + candidate columns + independence selection.
- Node set = concreteness-covered + connected TYPED subgraph (attributes near-fully present there;
  MEASURED@data/exp_grounding_multiattribute_fusion_v1/metrics.json:subgraph_meta -> n_covered_connected=3262,
  attr coverage sensory ~0.999, aoa ~0.928). No mean-mask degeneracy.

## Arms (PAIRED: same split + completable subset + candidate negatives + degree strata per seed)
- GROUNDED: exterior = fused measured attributes (projected). agreement(struct, attr); anchor=cat(struct, attr).
- UNGROUNDED: exterior = 2nd structural view (struct2). agreement(struct, struct2); anchor=cat(struct, struct2).
  Dimension-matched single-variable ablation of GROUNDED (only the exterior half differs) = graph-alone.
- SCRAMBLED: exterior = same attributes, values permuted across concepts (must-fail values control; dim-matched).
- ONESHOT_CODE: one-shot TransE from scratch (the failed additive code; the -0.040 contrast).
- POPULARITY_DEGREE / RANDOM_CODES / TRANSE_TRANSDUCTIVE (oracle).

## THE finish-line number
LOW-stratum grounding lift = reach@1[GROUNDED,LOW] - reach@1[UNGROUNDED,LOW]. Does it go POSITIVE (>0) where the code's
LOW gap went -0.040?

## Pre-registered bands
- GROUND_MARGIN=0.03 (aggregate GROUNDED-UNGROUNDED lift), STRAT_MARGIN=0.02 (LOW & MID lift), TIE_EPS=0.0.
- SCRAMBLE_MAX=0.02 (SCRAMBLED-UNGROUNDED ceiling), SCRAMBLE_BEAT=0.02 (GROUNDED-SCRAMBLED floor).
- POP_GAP=0.03, POP_RECOVER_FRAC_MAX=0.60, POP_RECOVER_FRAC_HI=0.80.
- RANDOM_CEIL=0.15, ORACLE_FIRE_MARGIN=0.15, MIN_STRAT_Q=40, MIN_HELDOUT_COMPLETABLE=60.
- Collapse: grounded eff_rank <= 3.0 OR rep_var <= 0.02 -> HARD_FAIL_CONSOLIDATION_COLLAPSED.

## Decision
- HARD_PASS_GROUNDING_CLOSES_THE_LOOP = not collapsed AND aggregate lift>=GROUND_MARGIN AND (LOW & MID lift>=STRAT_MARGIN
  -> LOW positive) AND scramble control (S-U<=SCRAMBLE_MAX & G-S>=SCRAMBLE_BEAT) AND grounded beats popularity.
- HARD_FAIL_GROUNDING_DOESNT_TRANSFER = not collapsed AND (aggregate lift<=TIE_EPS OR LOW/MID lift<=TIE_EPS OR pop
  recovers OR scramble launders).
- MIDDLE_BAND_PARTIAL_TRANSFER_AMBIGUOUS otherwise. INCONCLUSIVE if too-few-completable / negatives-trivial / oracle
  did not fire.

## SCHEMA-VET fields
- cardinality_ok: True; EXPECTED_N_UNITS = n_seeds (3 FULL); HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short.
- arms_differ_verified: True (>=5 distinct arm sigs asserted per seed; self-test asserts 3 geometry sigs differ).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep gate clean.
- crlb: filtered Hits@1 chance floor = 1/(N_RANK_NEG+1) ~ 0.01 THEORETICAL@1/(99+1). HARD_PASS >= 0.03 aggregate + 0.02
  tail (>> tie 0.0). discriminator_reachability: True (self-test planted grounded arm reaches 0.158 MEASURED).
- baseline_in_band: RANDOM null <=0.15; ORACLE must-fire >=rand+0.15; UNGROUNDED = ablation reference (measured, not a
  null gate); POP = confound baseline (measured).
- discriminator survives scale: CONS_KNN/PASSES/ALPHA/REL_EPOCHS/DIM SHARED self-test<->smoke<->full; transfer
  discriminator + scramble control fire in self-test; real-graph transfer is the OPEN measurement.
- HP_SCOPE: transfer gate on GROUNDED vs UNGROUNDED + POP; SCRAMBLED must-fail control; RANDOM null; ORACLE must-fire;
  ONESHOT_CODE reported (degree-dependent, the -0.040 contrast).
- calibration_check: default_ok_for_this_regime (retest-inherited held-out + data-driven degree tertiles; consolidation
  /KGE hyperparams reused from the landed engine cell, not tuned on this cell's data).
- effective_vs_nominal_parameter_audit: no nominal-vs-effective sweep (single regime per run_mode). sweep_alignment: N/A.
- discriminating_fraction: N/A (not a parameter sweep; single degree-stratified comparison).
- composition_edges: struct/attr -> agreement (SHAPE_MATCH, both [n,DIM] L2 rows) -> consolidate -> fit_relation_offsets
  (SHAPE_MATCH, frozen [n,2*DIM] codes) -> rank_transe (SHAPE_MATCH). No SHAPE_MISMATCH_no_adapter.
- positive_control_arms: TRANSE_TRANSDUCTIVE (oracle >> random) + ONESHOT_CODE (reproduces the code's degree-dependent
  additive result on this graph). SHAPE_DRIFT audit: synthetic self-test vs real ConceptNet -> planted world mirrors the
  degree-contaminated-structure regime; real-graph outcome is the open measurement (declared risk).
- functional_requirements: (1) place rare + common entities degree-invariantly [consolidation restart + normalized
  Laplacian]; (2) inject exterior measured signal into the geometry [agreement channel + anchor cat]; (3) read off held
  relations [additive relation offsets, frozen codes]; (4) isolate that VALUES do the work [scrambled control].
- cell_chunked: false (>=3 arms trained per seed but each seed independent; single-file, per-seed write_partial).
- start_marker_written: True; crash_diagnostic_present: True; heartbeat_present: per-seed/per-arm/per-stratum flush
  prints (each seed ~1-2 min; run < 20 min FULL); defensive_error_checking: per-arm + per-seed try/except with
  failure_class, cardinality gate, SystemExit-before-Exception.
- progress_logging: print_flush_true (line_buffered stdout + flush=True per line).

## Compute + dispatch
class (c) mixed / CPU-fast; SHARDED storage. FULL routes to remote_cpu_queue (CPU; local is SMOKE-ONLY-LOCAL lock).
FULL = 3 seeds, n_nodes=5000 target (~3262 covered+connected). Estimated FULL wall ~10-20 min CPU; --timeout 3600s.
