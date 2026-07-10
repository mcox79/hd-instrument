# Pre-registration: Graph inductive-predictability CEILING (DECISIVE TEST #4)

- anchor_name: `graph_inductive_ceiling_v1`
- cell: `experiments/exp_graph_inductive_ceiling_v1.py`
- metrics: `data/exp_graph_inductive_ceiling_v1/metrics.json`
- date: 2026-07-09
- queue (FULL): `remote_cpu_queue` (pure-CPU; classic predictors + tiny GCN + phase-0 encoder)
- run_mode: FULL = 3 seeds [7,13,17], n_nodes target 5000 (loads ~4440), GCN 200 epochs, encoder 80 epochs

## Question
Held-out relational reasoning on the ConceptNet subgraph fails; neither a sharper encoder (#1) nor a stronger readout
(#3) rescues it (both canonically refuted). Surviving hypothesis (#4): the graph's structure is not inductively RICH
enough -- held-out edges cannot be predicted from structure by ANY method, so the limit is the KNOWLEDGE, not our
encoder/readout. Measure the BEST-POSSIBLE held-out edge-prediction AUC from RAW GRAPH STRUCTURE (independent of
substrate codes) = the inductive-predictability ceiling. Compare to code-based M5 ~0.70 and learned-SR reach 0.115.

## Construction (reuses phase-0 M5 held-out split VERBATIM -> apples-to-apples with codes 0.70)
Withhold 30% of edges (random permutation); train predictors on the VISIBLE graph; score WITHHELD edges (positives) vs
FAR non-edges (random pairs, not an edge, no common neighbor => hop>=3) as negatives (`sample_far_negatives`, same as
phase-0). AUC = P(pos ranks above neg), average-rank tie-corrected (essential: classic predictors tie many pairs at 0).
Hard-negative variant (random non-edges) reported. LP-Hits@1/@2 (tail-corruption ranking, N_RANK_NEG=99) reported.

## Method ladder (BEST over the ladder = the ceiling)
- Classic parameter-free: CN (common-neighbors), AA (Adamic-Adar), RA (resource-allocation), JC (Jaccard),
  PA (preferential-attachment = deg(u)*deg(v), degree-only control).
- GCN: 2-layer graph-conv link-predictor (structural features + learnable node embedding), trained on visible edges via
  BCE negative sampling; pure torch (no torch_geometric). The ML ceiling.
- CODE_COSINE: paired reproduction of phase-0 M5 (char-trigram + binding encoder on SAME visible edges; cosine AUC on
  SAME split). Positive control.

## Density axis (tests the USER 'thin-knowledge' hypothesis)
Recompute the ceiling on a DENSER subgraph = the k-core (largest k with >= MIN_CORE_NODES nodes; heap-peeling
decomposition) of the same subgraph (high-degree nodes -> higher mean-degree). Does the RELATIONAL ceiling RISE with
density?

## Discriminator (pre-registered bands; primary metric = best held-out AUC over the ladder, FAR-negative split)
- HARD_PASS_SIGNAL_EXISTS: `best_auc_sparse >= 0.85` (full ladder incl PA) -> a strong inductive signal EXISTS that our
  machinery misses -> back to #1/#3.
- HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT: `best_auc_sparse <= 0.75` (full ladder; no method beats codes 0.70 materially)
  AND relational ceiling rises with density (`best_rel_dense - best_rel_sparse >= 0.03`; relational = CN/AA/RA/JC/GCN,
  PA excluded as a degree/popularity artifact). -> KNOWLEDGE is the wall; richer ingest is the fix. (HARD_FAIL is the
  EXPECTED confirmation of the surviving hypothesis; naming follows the pre-reg, not desirability.)
- MIDDLE_BAND: otherwise (0.75 < best < 0.85, OR caps near 0.70 but relational ceiling does not rise with density).
- INCONCLUSIVE_TOO_FEW_HELDOUT if held-out edges < 60.

Bands: SIGNAL_EXISTS_AUC=0.85, CAP_NEAR_CODES_AUC=0.75, DENSITY_RISE_MARGIN=0.03, CODES_M5_REF=0.6945
(MEASURED@data/phase0_code_structure_precheck_result.json:per_size[1].M5_heldout_auc), CODE_REPRO_TOL=0.10.

Note (pre-dispatch, smoke-revealed confound-removal): on the sparse real graph PA (node popularity) is the strongest
predictor (~0.71) while relational predictors are ~0.64-0.68; PA is a degree/size artifact, not knowledge richness, so
the density-rise gate uses the relational subset (SIGNAL/CAP gates stay on the full ladder incl PA). Documented; not
threshold-chasing.

## Self-test (mechanism; assert_discriminator_fires)
Planted SBM (community structure, high clustering): ladder MUST hit AUC >= 0.85. Planted ER (matched avg degree, no
clustering): classic predictors must NOT beat chance (<= 0.65). Gap >= 0.20. Arms differ (>= 5 distinct sigs). If the
ladder cannot separate signal-rich from signal-poor graphs, the measurement is meaningless -> BLOCK_DISPATCH.
MEASURED@smoke: SBM best 0.925, ER classic 0.614, gap 0.31, arms differ -> PASS.

## Compute architecture
class: (b) sequential-CPU with justification. Classic predictors = parameter-free set-intersections (no matmul); GCN =
tiny 2-layer conv over dense normalized adjacency (n<=5000, ~0.1 GFLOP/layer); encoder reproduces phase-0 (~13s/seed at
n=4440 CPU). No Python-loop-over-independent-points matmul. Storage: no_storage/no_composition (graph-analysis probe).
Device-aware torch; CPU adequate.

## Schema-vet fields
- arms_differ_verified: true (>= 4 distinct structural sigs asserted per seed; smoke MEASURED >= 5).
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics + os.replace).
- except SystemExit: raise before except Exception; no bare/BaseException (grep-gate CLEAN).
- crlb_n/a: AUC chance floor = 0.50; SIGNAL bar 0.85 achievable (self-test SBM >= 0.85); no CRLB noise floor applies.
- baseline_in_band: ER-null (<=0.65) + SBM-fire (>=0.85) are the self-test in-band controls.
- discriminator survives scale: SIGNAL(>=0.85) vs CAP(<=0.75); self-test proves ladder separates SBM/ER by >=0.20;
  classic-predictor AUC deterministic given graph+split (no training); GCN re-verified at FULL.
- HP_SCOPE: SIGNAL/CAP gate = best over CN/AA/RA/JC/PA/GCN; density gate = best over CN/AA/RA/JC/GCN (rel);
  CODE_COSINE = positive control (reproduce M5); SBM/ER = self-test signal/null.
- positive_control (Gate D): CODE_COSINE reproduces phase-0 M5 0.6945 within 0.10 on the same construction
  (MEASURED@smoke CODE=0.719-0.722 -> OK).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce SPARSE + DENSE x all methods.
- per-unit failure-class instrumentation: GCN/CODE wrapped with explicit-Exception failure-class recording (no bare).
- calibration_check: default_ok_for_this_regime (HELDOUT_FRAC + far-negatives inherited VERBATIM from phase-0 M5;
  k-core threshold by fixed MIN_CORE_NODES rule, not tuned).
- cell_chunked: false (light cell; 3 seeds in-process, per-seed try/except + write_partial checkpoints).
- start_marker_written: true; crash_diagnostic_present: true (CELL_CRASHED + traceback); heartbeat_present: true
  (emit_heartbeat per regime); defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-seed/regime/method flush prints).
- run_mode default: cell defaults device=cpu and run-mode full; queue_add passes --run-mode full explicitly.

## SMOKE VERDICT (n=1525 reduced scale, 2 seeds) -- REAL verdict, HOLD mechanism-story until landed-VET
`HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT`. SPARSE best_struct=0.717 (PA), best_rel=0.677, CODE=0.721 (M5 repro OK);
DENSE(k=5) best_struct=0.754, best_rel=0.754, CODE=0.784; density_delta_rel=+0.078 (rises); best_minus_code=-0.004
(structural does NOT beat codes); SIGNAL_EXISTS=False; CAPS_NEAR_CODES=True. FULL n=4440 x3 seeds is canonical.
