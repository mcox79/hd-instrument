# Pre-registration: Density PAYOFF -- does richer knowledge measurably enable the substrate's OWN held-out reasoning?

- anchor_name: `grounding_density_payoff_relational_reasoning_v1`
- cell: `experiments/exp_grounding_density_payoff_relational_reasoning_v1.py`
- metrics: `data/exp_grounding_density_payoff_relational_reasoning_v1/metrics.json`
- date: 2026-07-09
- queue (FULL): `overnight_queue` (GPU; encoder retrain per density level -> 3 seeds x 2 densities x 2 encoders = 12 InfoNCE binding trains at code_dim=2048/feat_dim=8192/epochs=140)
- run_mode: FULL = 3 seeds [7,13,17], n_nodes target 5000, code_dim=2048, feat_dim=8192, epochs=140, k-core min_core=250

## Question
The session's resolved conclusion (5-hypothesis elimination): the reasoning wall is KNOWLEDGE-THINNESS, not machinery.
Test #4 (`graph_inductive_ceiling_v1`, HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT) showed the graph's inductive CEILING (best
held-out link-prediction AUC) RISES +0.078 with density (5-core, mean-deg 5.6->8.7,
MEASURED@data/exp_graph_inductive_ceiling_v1_smoke/metrics.json:gates.density_delta_relational_GATE). That is a
CEILING. This cell tests the DIRECT payoff: does the substrate's OWN learned-SR HELD-OUT routing reach FOLLOW the
ceiling up when knowledge is denser -- and is any rise a RELATIONAL gain (the substrate's own codes) rather than a pure
DEGREE/popularity artifact?

## Construction (reuse the certified learned-SR held-out harness VERBATIM + a density ladder + a degree confound arm)
Reuse `exp_grounding_learned_sr_heldout_reasoning_v1` held-out construction + code-smoothing arms VERBATIM
(LEARNED_HELDOUT / HELDOUT_MEMCTRL / HELDOUT_CODEALIAS + KNOWN_T_FULL + MEMORYLESS + SUPPLIED anchors), and run it on a
DENSITY LADDER of the SAME subgraph:
- SPARSE = the full ConceptNet typed subgraph (mean-deg ~5.4-6.6).
- DENSE  = the k-core (largest k with >= min_core nodes; heap-peeling decomposition, reused VERBATIM from #4) = a
  high-degree-induced subgraph (mean-deg ~8.5-12).
At each density level, a disjoint contiguous BFS-ball of non-goal nodes is WITHHELD from BOTH the transition matrix AND
the encoder (leakage-safe). Held-out chains = hop-1 correct successor is a withheld node (first routing decision needs a
withheld-candidate reachability estimate). LEARNED re-estimates withheld reachability by code-space smoothing over the
VISIBLE-trained codes; CODEALIAS = random codes; MEMCTRL = leaves the hole. Identical seeds/chains/graph/withheld-split
per level; only density (which subgraph) and the reachability signal differ (PAIRED).

## CRITICAL CONFOUND CONTROL (the #4 agent flagged it; do NOT skip)
A denser subgraph of high-degree hubs can look "easier" via pure DEGREE/popularity (preferential-attachment), NOT via
richer RELATIONAL structure. So we add DEGREE_ONLY: an identical routing arm whose reachability column is the FULL-graph
node DEGREE (popularity), not the SR resolvent or the learned codes. Under run_sr_arm's within-candidate normalization
this is exactly PA-routing (route toward the highest-degree local neighbor); using FULL-graph degree makes it a STRONG
baseline (withheld hub successors keep their true popularity -> the relational gain is CONSERVATIVE).
- The number that COUNTS = RELATIONAL GAIN = LEARNED_HELDOUT reach@2 minus DEGREE_ONLY reach@2, per density level.
- The density payoff that counts = whether the RELATIONAL GAIN RISES with density (dense minus sparse), NOT raw reach.
- Also tracked: codes-beat-random margin = LEARNED - CODEALIAS, and whether IT rises with density (the substrate's own
  codes benefiting, degree-blind).

## Discriminator (pre-registered bands; primary = LEARNED_HELDOUT reach@2 on held-out chains, per density level)
- HARD_PASS_RICHER_KNOWLEDGE_ENABLES_REASONING: `rel_gain_rise (= rel_gain_dense - rel_gain_sparse) >= 0.10`
  OR `codes_margin_rise >= 0.05 AND codes_margin_sparse <= 0.05` (codes-beat-random crosses up from ~0)
  -> richer knowledge measurably enables the substrate to reason inductively (RELATIONAL, degree-independent).
- HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER: `rel_gain_rise <= 0.03 AND codes_margin_rise <= 0.02`
  -> density does NOT help the substrate reason relationally (no help at all, OR raw gain is a pure-degree artifact
  captured by DEGREE_ONLY). Knowledge-density alone is not the enabler; the wall is deeper.
- MIDDLE_BAND_PARTIAL_DENSITY_PAYOFF: otherwise (0.03 < rel_gain_rise < 0.10 and no codes-margin crossing).
- INCONCLUSIVE guards: HOP1_ABSENT / BASELINE_DID_NOT_FAIL / SUPPLIED_MM_DID_NOT_FIRE (SPARSE anti-sat) /
  TOO_FEW_HELDOUT_CHAINS (either level < 25) / POSITIVE_CONTROL_REPRO_DRIFT (FULL sparse only).

Bands: REL_GAIN_RISE_HP=0.10, CODES_MARGIN_RISE_HP=0.05, CODES_MARGIN_NEAR_ZERO=0.05, REL_GAIN_RISE_FLAT=0.03,
CODES_MARGIN_RISE_FLAT=0.02, NEC_MARGIN=0.05, MIN_HELDOUT_CHAINS=25. Held-out/smoothing knobs imported VERBATIM from the
certified learned-SR cell: WITHHELD_FRAC=0.30, SMOOTH_K=8, SMOOTH_TEMP=0.10, SR_GAMMA_PRIMARY=0.85, SR_BOOST=1.5.

Reported (never gated): per-density LEARNED/DEGREE/MEMCTRL/CODEALIAS/MEMORYLESS/KNOWN_T reach@1/@2, raw reach_rise,
degree_rise (pure-popularity component), rel_gain per level, codes_margin per level, mean-degree + k-core per level,
held-out chain counts.

## Self-test (mechanism; assert_discriminator_fires; proves the relational gain is DEGREE-INDEPENDENT)
One planted graph, two held-out chain families (all hop-1 successors withheld):
- REL family: true withheld successor's code planted near a VISIBLE onward node reaching the goal (code-smoothing
  recoverable); ALL same-relation siblings equal-degree -> DEGREE cannot separate them, LEARNED can.
- DEG family: true withheld successor is a HUB (high full-graph degree) with a RANDOM code (no recoverable signal);
  off-siblings are low-degree dead-ends -> DEGREE recovers, LEARNED (smoothing a random code) ties ~1/KSR.
Gate: `rel_gain(REL) >= 0.20 AND rel_gain(DEG) <= 0.05 AND gap(REL - DEG) >= 0.15`. NO_CLEANUP collapses; the four
held-out reachability arms differ. If the metric cannot separate a relational density signal from a pure-degree one, the
confound control is meaningless -> BLOCK_DISPATCH.
MEASURED@self-test (venv, 2.6s): rel_gain(REL)=+0.792 (LEARNED@1=1.000 vs DEGREE@1=0.208); rel_gain(DEG)=-0.731
(LEARNED@1=0.269 vs DEGREE@1=1.000); gap=1.523; NO_CLEANUP ran; arms differ; n_ho_rel=n_ho_deg=130 -> PASS.

## Compute architecture
class: (c) mixed with justification. Storage: SHARDED (multi-hop compositional chaining, per META_STORAGE_STRATEGY).
GPU-heavy: two InfoNCE binding encoders (full + visible) retrained PER DENSITY LEVEL PER SEED (2 densities x 2 encoders
x 3 seeds = 12 trains at code_dim=2048/feat_dim=8192/epochs=140) -> overnight_queue (GPU). Two dense LU multi-RHS
resolvent solves per level (full T + visible T), factored once per gamma. Code-smoothing = one [W,V] cosine matmul +
top-k + [W,V]x[V,U] matmul, batched. Within a hop all chains + candidates scored by batched einsum; ACROSS hops the
chain is inherently SEQUENTIAL (data dependency, not a batching flaw). No Python-loop matmul over independent points.
Device-aware torch (cuda if available, else cpu; default --device auto).

## Schema-vet fields
- arms_differ_verified: true (LEARNED/MEMCTRL/CODEALIAS/DEGREE distinct commit sigs asserted per seed per density level;
  smoke CLEAN).
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics + os.replace).
- except SystemExit: raise before except Exception; no bare/BaseException (grep-gate CLEAN).
- crlb: top-1 chance floor = 1/n_nodes; the RELATIONAL GAIN is a paired difference of two reach@2 on the same held-out
  chains -> chance floor of the difference = 0.0; HARD_PASS rel_gain_rise 0.10 strictly above HARD_FAIL flat 0.03 + 5%
  band-width. discriminator_reachability: OK.
- baseline_in_band (META_RULE_AG): MEMORYLESS@1 in (0.05,0.95) on SPARSE (smoke MEASURED 0.501); NO_CLEANUP@2 collapses
  (smoke MEASURED 0.008). 0.05 < baseline < 0.95 verified.
- discriminator survives scale: the RELATIONAL-vs-DEGREE discriminator is proven degree-INDEPENDENT by the planted
  self-test (fires on REL, null on DEG, gap 1.52) at self-test scale (SATURATION-safe). Smoke previews the real
  sparse/dense gain; FULL (3 seeds, dense k-core >= 250 nodes, code_dim=2048) is canonical.
- HP_SCOPE: density-payoff gate applies to the RELATIONAL GAIN (LEARNED - DEGREE) rise + codes-margin crossing.
  LEARNED_HELDOUT = mechanism; DEGREE_ONLY = confound control; CODEALIAS/MEMCTRL = necessity controls;
  KNOWN_T_FULL/MEMORYLESS/SUPPLIED = positive-control reproductions (SPARSE FULL only); NO_CLEANUP = must-fail.
- positive_control (Gate D): MEMORYLESS/SUPPLIED/KNOWN_T_FULL reproduce the certified anchors (REPRO_MEM1=0.453,
  REPRO_SUP1=0.756, REPRO_SUP2=0.500, REPRO_KNOWNT2=0.434, tol 0.10) at the matched FULL sparse regime; drift > 0.10 ->
  INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT. Not applied to DENSE (different graph). Smoke (not gated) MEASURED
  mem1/sup1/sup2/knownT2 all within tol.
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (3); each seed asserted to produce SPARSE + DENSE x all 4 held-out arms x 4
  depths (regime/arm/depth cardinality); < expected seeds -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- per-unit failure-class instrumentation: per-seed try/except records failure_class; no bare except.
- calibration_check: adaptive_with_discriminator_gate. Smoothing knobs imported VERBATIM (not re-tuned); k-core
  threshold by fixed MIN_CORE_NODES rule (not tuned for the density verdict); self-test proves degree-independence.
- PAIRED: per density level all arms share identical codes-per-condition + roles + seeds + graph + chains + withheld
  split; sparse and dense computed per seed on the same loaded subgraph.
- cell_chunked: false (3 seeds in-process; per-seed try/except + write_partial checkpoints; GPU FULL is fast).
- start_marker_written: true; crash_diagnostic_present: true (CELL_CRASHED + traceback); heartbeat_present: n/a
  (short GPU cell; per-seed/per-arm flush logging is the progress trace); defensive_error_checking:
  start_marker+crash_diagnostic+per-seed-failure-class+flush-logging.
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-regime/per-arm flush prints).
- run_mode default: cell defaults --device auto (cuda on the GPU runner) and --run-mode full; queue_add passes
  --run-mode full explicitly.

## SMOKE VERDICT (reduced scale: n=1152 loaded, code_dim=384, epochs=40, 2 seeds; dense k-core only 115 nodes) -- REAL smoke verdict, HOLD mechanism-story until landed-VET
`HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER` at smoke scale.
SPARSE(deg=5.40, n_ho=477): LEARNED@1=0.372 @2=0.127 | DEGREE@1=0.534 @2=0.069 | MEMCTRL@2=0.045 | CODEALIAS@2=0.124;
rel_gain=+0.058, codes_margin=+0.003.
DENSE(k=5, deg=8.50, n_ho=370): LEARNED@1=0.151 @2=0.040 | DEGREE@1=0.257 @2=0.035 | MEMCTRL@2=0.018 | CODEALIAS@2=0.038;
rel_gain=+0.005, codes_margin=+0.003.
PAYOFF: rel_gain_rise(GATE)=-0.053, reach_rise=-0.087, degree_rise=-0.034, codes_margin_rise=-0.001.
Anti-sat CLEAN (NO_CLEANUP collapses 0.008; MEMORYLESS in-band 0.501; SUPPLIED fires 0.442). NOTE: the dense k-core at
smoke is only 115 nodes -- FULL (dense k-core >= 250 nodes, code_dim=2048, epochs=140, 3 seeds) is canonical; the smoke
is a preview, not the decision.
