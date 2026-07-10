# Pre-reg: LEARNED-SR HELD-OUT-SUBGRAPH reasoning (CG search-vs-reasoning discriminator)

Cell: `experiments/exp_grounding_learned_sr_heldout_reasoning_v1.py`
Anchor: `grounding_learned_sr_heldout_reasoning_v1`
Metrics path: `data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json`
Author: exp_dev. Stage 5 (compositional / grounding arc). Depends on Phase-0 code-structure pre-check (PASSED, judgment).

## Question
Does routing by a reachability signal DERIVED FROM THE SUBSTRATE'S OWN LEARNED CODES (code-space-smoothed successor
representation), with a disjoint subgraph WITHHELD from both the transition matrix T AND the encoder, GENERALIZE to
route through structure it never saw (= REASONING / CG) -- or does it only work on visited structure and collapse on
held-out (= memorized SEARCH / MM)? This directly targets the VET-settled critique of the certified SR cell
(reach@2=0.434 but proven to be closed-form graph SEARCH over a fully-known T).

## Phase-0 gate (passed, judgment call)
MEASURED@data/phase0_code_structure_precheck_result.json: learned codes carry graph structure at n=1237/4440/7895 --
1-hop edge-detection AUC=0.980/0.874/0.818; code-kNN neighbors 8-16x enriched for graph-proximity vs random;
leakage-safe HELD-OUT edge AUC=0.731/0.695/0.681 (codes generalize proximity to edges the encoder never saw). SIZE
axis: held-out AUC FLAT across sizes (deltaM5=-0.050) => "substrate too small" is NOT the blocker; signal present at
every size. Honest caveat: seen-edge AUC (0.842-0.990) >> held-out (0.681-0.731) => generalization is PARTIAL; a
MIDDLE_BAND held-out routing result is the realistic expectation, not a runaway HARD_PASS.

## Arms (paired: identical seeds/chains/nbr-table/graph; only the per-goal reachability signal differs)
- NO_CLEANUP        : global-cleanup must-fail control (collapses at reach>=2). Anti-saturation.
- MEMORYLESS        : goal-blind local decoder floor. Gate-D positive control (repro ~0.453 @1).
- SUPPLIED_WAYPOINT : MM ceiling (handed the true waypoint). Gate-D positive control (repro ~0.756 @1 / 0.500 @2).
- KNOWN_T_FULL      : the certified full-map SR (resolvent over the FULLY-KNOWN T). The SEARCH baseline. Gate-D
                      positive control (repro certified reach@2=0.434 on the general population).
- LEARNED_HELDOUT   : THE CG CANDIDATE. A contiguous BFS-ball W of NON-goal nodes is withheld from T AND encoder
                      (leakage-safe). M = resolvent over VISIBLE T; withheld-candidate rows re-estimated by
                      code-space smoothing (softmax-cosine kNN over VISIBLE-trained codes). Route by M_hat.
- HELDOUT_MEMCTRL   : necessity control -- visible-T, NO smoothing (withheld rows ~0 = hole-in-map). LEARNED must
                      beat this by >= NEC_MARGIN (smoothing necessary).
- HELDOUT_CODEALIAS : reciprocal-necessity control -- smoothing weights from RANDOM codes. LEARNED must beat this by
                      >= NEC_MARGIN (codes necessary; guards against leakage/artifact).

Discriminator subset: HELD-OUT chains = chains whose hop-1 correct successor is a WITHHELD node (so the FIRST routing
decision requires estimating a withheld candidate's reachability). reach = TOP-1 COMMIT accuracy on this subset.

## Pre-registered bands (picked BEFORE the run; from research note + Phase-0)
- CG_HARD_PASS = LEARNED_HELDOUT reach@2 >= 0.32 (~80% of certified full-graph 0.434) AND >= HELDOUT_MEMCTRL + 0.05
  AND >= HELDOUT_CODEALIAS + 0.05  -> routing GENERALIZES to held-out structure via the substrate's own codes = CG.
- CG_HARD_FAIL = LEARNED_HELDOUT reach@2 <= 0.20 OR |LEARNED - CODEALIAS| < 0.05 (codes not doing the work) OR
  LEARNED <= HELDOUT_MEMCTRL (smoothing adds nothing).
- MIDDLE_BAND  = 0.20 < LEARNED reach@2 < 0.32 with LEARNED > both controls -> partial generalization (Phase-0
  realistic expectation).
NEC_MARGIN=0.05. WITHHELD_FRAC=0.30, SMOOTH_K=8, SMOOTH_TEMP=0.10, SR_GAMMA=0.85, SR_BOOST=1.5 (all pre-registered,
NOT tuned on real data). MIN_HELDOUT_CHAINS=40 (else INCONCLUSIVE_TOO_FEW_HELDOUT_CHAINS).

## Numbers (tagged)
- certified full-map SR reach@2 = 0.434  MEASURED@data/exp_grounding_multihop_sr_reachability_routing_v1/metrics.json
- MEMORYLESS@1 ~0.453, SUPPLIED@1 ~0.756, SUPPLIED@2 ~0.500  MEASURED@fair-test/greedy-cell metrics.json
- CG_HARD_PASS 0.32  HYPOTHESIZED@this prereg (~80% retention of the 0.434 full-map anchor, per research note)
- Phase-0 held-out edge AUC 0.681-0.731  MEASURED@data/phase0_code_structure_precheck_result.json
- top-1 chance floor 1/n_nodes ~0.0002  THEORETICAL@uniform argmax over n nodes

## SCHEMA-VET fields
- Compute architecture: (c) mixed; SHARDED storage; two dense resolvent LU solves + code-smoothing matmul; hops
  inherently sequential (data dependency, not a batching flaw). CPU laptop -> remote_cpu_queue for FULL.
- arms_differ_verified: True (LEARNED != MEMCTRL != CODEALIAS on held-out subset; KNOWN_T != MEMORYLESS; asserted/seed)
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace)
- except SystemExit: raise before except Exception; no bare/BaseException (grep-gated, clean)
- crlb_reachability: OK (0.32 achievable; 0.434 demonstrated with full T; question is retention under held-out)
- baseline_in_band: MEMORYLESS@1 in (0.05,0.95); NO_CLEANUP@2 collapses (anti-saturation)
- discriminator_survives_scale: planted self-test proves LEARNED >> MEMCTRL when codes carry recoverable structure and
  LEARNED ~ MEMCTRL (~1/KSR) when codes random (CODEALIAS); smoke previews on real graph; FULL (3 seeds) canonical
- HP_SCOPE: CG win gate applies to LEARNED_HELDOUT only; KNOWN_T/MEMORYLESS/SUPPLIED = positive controls; NO_CLEANUP =
  must-fail; MEMCTRL/CODEALIAS = necessity controls (LEARNED must beat both)
- positive_control (Gate D): MEMORYLESS+SUPPLIED+KNOWN_T_FULL reproduce certified anchors at matched FULL regime;
  drift>0.10 -> INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT
- cardinality_ok: EXPECTED_N_UNITS = n_seeds; arm x depth cardinality asserted per seed
- per-unit failure-class instrumentation: yes (META_RULE_J; no bare except)
- calibration_check: adaptive_with_discriminator_gate (all knobs pre-registered; self-test verifies discriminator fires)
- PAIRED trials: all arms share codes-per-condition + roles + seeds + graph + chain population
- cell_chunked: false (per-seed loop with write_partial; single-file multi-seed)
- start_marker_written: true; crash_diagnostic_present: true; heartbeat_present: true (via train_binding_encoder_dev)
- defensive_error_checking: passed_all_4_patterns
- run_mode: full (default; --self-test / --smoke explicit); RUN_MODE VERIFICATION post-dispatch required
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints)
- effective_vs_nominal: no swept parameter (withheld_frac fixed); sweep_alignment_verdict: ALIGNED (n/a)
- discriminating_fraction: n/a (not a parameter sweep; single held-out condition with pre-registered bands)
- composition_edges: SR-resolvent -> argmax hop-selection (SHAPE_MATCH; reuses certified run_sr_arm verbatim)
- functional_requirements: (1) derive reachability without a handed T -> code-space-smoothed visible-T resolvent;
  (2) generalize to unseen structure -> code-kNN smoothing of withheld rows; (3) distinguish reasoning from search ->
  held-out subgraph + two necessity ablations

## Dispatch
FULL -> remote_cpu_queue (CPU cell; dense resolvent at n~4440 is sub-second; 3 seeds ~ minutes). Timeout 5400s.
