# Pre-registration: successor-representation (SR) reachability-routing autonomous multi-hop traversal (MM -> CG)

- anchor_name: `grounding_multihop_sr_reachability_routing_v1`
- cell: `experiments/exp_grounding_multihop_sr_reachability_routing_v1.py`
- date: 2026-07-09
- builds on: greedy autonomous (`grounding_multihop_autonomous_subgoal_greedy_v1`, MIDDLE_BAND 0.181) +
  landmark routing (`grounding_multihop_landmark_routing_v1`, HARD_FAIL 0.111) + goal-conditioning MM
  (`grounding_multihop_fair_test_unique_successor_goal_v1`, SUPPLIED ceiling 0.499)
- design note: `notes/research_successor_representation_reachability_autonomous_traversal_2026-07-09.md`

## Question
Two prior autonomous attempts fell short with proximity heuristics: greedy goal-cosine (single-step static
embedding distance) reach@2=0.181; landmark/hub routing (goal-agnostic centrality) reach@2=0.111 (HARD_FAIL).
This cell asks: does hop-selection by a closed-form SUCCESSOR-REPRESENTATION / resolvent reachability score toward
the FINAL goal -- the ONE signal that is both MULTI-STEP and GOAL-CONDITIONED -- recover the supplied-waypoint
ceiling (0.499) that both prior attempts missed?

## Mechanism (no new retrieval primitive; one new scoring function + one knob)
SR/resolvent = personalized PageRank (Dayan 1993; Millidge arXiv 2512.24722 states the equivalence directly). The
KB graph is static + fully known, so closed-form model-based SR (no TD-learning). For each final goal `G` solve
`(I - gamma*T) x = e_G` (dense LU multi-RHS at n~4440; sub-second) -> `x[v] = M[v,G]` = expected discounted
occupancy of `G` from `v` = "how strongly candidate v leads TOWARD G", multi-step + goal-conditioned. `T` =
row-normalized adjacency of the SAME symmetric typed subgraph the traversal walks (SR reachability is PURE GRAPH
STRUCTURE, SEED-INVARIANT -> LU factored once per gamma, reused across seeds). At each hop, among the real local
out-neighbors (nbr table reused VERBATIM), `score(v) = <l2(bind(role_r, Z[cur])), Z[v]> + SR_BOOST * srn[v]` where
`srn` = WITHIN-CANDIDATE min-max normalization of the raw SR reachability (implements "pick the neighbor maximizing
x[v]" at a scale comparable to the base term; degrades gracefully to the memoryless floor when SR is
uninformative/smeared, never steering below it). argmax; commit; chain.

## Arms (paired: identical codes + general chains + seeds + graph + dim; only the scoring differs)
- `NO_CLEANUP` -- global-cleanup-only chain; must-fail / anti-saturation control (collapses at reach>=2).
- `MEMORYLESS` -- goal-blind local decoder = fair-test floor (positive-control repro).
- `SUPPLIED_WAYPOINT` -- = fair-test `GOAL_WAYPOINT` MM ceiling; handed the true next waypoint (positive-control).
- `AUTONOMOUS_GREEDY` -- the plain-greedy autonomous arm (~0.181 @2); the anchor SR_SEEDED must BEAT (positive-ctrl).
- `SR_SEEDED` -- THE CG CANDIDATE (primary): SR reachability at `SR_GAMMA_PRIMARY`=0.85. Verdict on this arm.
- diagnostic (logged, not gated): SR gamma sweep {0.70, 0.85, 0.95} on the general chains (the smearing curve).

## Pre-registered CG bands (verdict on SR_SEEDED reach@2)
- `HARD_PASS_CG` (`HARD_PASS_CG_SR_REACHABILITY`): `sr2 >= 0.40` AND `sr2 > autonomous_greedy2`. Reachability
  recovers >=59% of the gap greedy left (0.318); materially > greedy 0.181 AND > landmark 0.111 -> autonomous
  reasoning WORKS via multi-step goal-conditioned reachability.
- `HARD_FAIL_CG` (`HARD_FAIL_CG_SR_VACUOUS`): `sr2 <= 0.20`. No better than greedy/landmark; SR smears (gamma too
  high) OR graph reachability structure insufficient (diagnose via the gamma-sweep curve + non-degeneracy telemetry).
- `MIDDLE_BAND_CG_SR_PARTIAL`: 0.20 < sr2 < 0.40. Beats greedy but short of the recover-the-gap bar.
- Guard verdicts: `INCONCLUSIVE_HOP1_ABSENT`, `INCONCLUSIVE_BASELINE_DID_NOT_FAIL`,
  `INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE`, `INCONCLUSIVE_SR_COLUMN_DEGENERATE`,
  `INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT`.
- Band width 0.40-0.20=0.20; HARD_PASS 0.40 clears HARD_FAIL+5%band (0.21) and sits below the SUPPLIED ceiling
  0.499 (achievable side). Reported (never gated): SR-vs-greedy delta, SR-vs-supplied ratio, winning gamma.

### Reference anchors (all MEASURED)
- MEMORYLESS reach@2 = 0.121; SUPPLIED (GOAL_WAYPOINT) reach@2 = 0.500
  MEASURED@data/exp_grounding_multihop_fair_test_unique_successor_goal_v1/metrics.json:gates.reach
- AUTONOMOUS_GREEDY reach@2 = 0.181
  MEASURED@data/exp_grounding_multihop_autonomous_subgoal_greedy_v1/metrics.json:gates.cg.autonomous_greedy_reach2
- LANDMARK_SEEDED reach@2 = 0.111 (HARD_FAIL)  MEASURED@landmark cell verdict (per task hand-off)
- top-1 chance floor = 1/n_nodes ~ 0.0002 at n=5000  THEORETICAL@1/n_nodes
- SR = personalized PageRank / resolvent M=(I-gamma*T)^-1  CITED@Dayan 1993; Millidge arXiv 2512.24722

## Capability framing (3-part; CG claim, verify-able)
- DIFFERENT CHANNEL: downstream reach@2/@3 (top-1 commit chained).
- LIVE ALTERNATIVE: greedy goal-cosine AND landmark routing genuinely fall short at multi-hop range
  (0.181 / 0.111 vs 0.499).
- NECESSITY: SR-reachability vs plain-greedy ablation, paired. Report SR-vs-supplied ratio + SR-vs-greedy delta.

## Compute architecture
class: (c) mixed. Storage: SHARDED (each node its own code; compositional chaining). SR reachability = a DENSE
closed-form linear solve `(I - gamma*T) x = e_G`, batched multi-RHS over all unique goals (LAPACK/cuSOLVER LU
factored once per gamma, reused across seeds because T is graph-only / seed-invariant). Within-hop scoring batched
matmul/einsum on GPU (cuda when available); across-hops genuinely SEQUENTIAL (inherent chain data-dependency, same
shape as greedy/fair-test cells which ran 3 seeds FULL in ~16s on cuda). No Python-loop matmul over independent
phase points.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (FULL 3). Each seed asserted to produce all 5 arms x depths 1-4.
- arms_differ_verified: true (SR_SEEDED commit-sig != AUTONOMOUS_GREEDY != SUPPLIED != MEMORYLESS != NO_CLEANUP;
  per-seed).
- final_metrics_atomicity: tmp_replace (via `_seed_checkpoint.write_metrics` + `os.replace`).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except). Verified
  (grep-gate clean).
- crlb_floor_computed: 1/n_nodes ~ 0.0002; crlb_formula_reference: `top1_chance = 1/n_nodes`.
  discriminator_reachability: true (SUPPLIED demonstrated reach@2=0.500 reachable; HARD_PASS bar 0.40 below ceiling).
- baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (repro ~0.453). NO_CLEANUP@2 collapses (anti-saturation).
- discriminator_survives_scale: the MM discriminator (SUPPLIED >> MEMORYLESS, `supplied_fires`) is graph-structural
  and asserted to fire at smoke; NO_CLEANUP collapses AT smoke scale (SATURATION-VACUOUS guard); mechanism CAN-fire
  proven by the clean planted self-test (SR_SEEDED ~ SUPPLIED, disc_frac=1.0, column non-degenerate). The CG
  measurement (SR-vs-greedy-vs-supplied) is the RESULT; FULL (3 seeds) canonical.
- HP_SCOPE: `{SR_SEEDED: [CG_HARD_PASS], AUTONOMOUS_GREEDY: [positive_control_repro], SUPPLIED_WAYPOINT:
  [positive_control_repro], MEMORYLESS: [positive_control_repro, baseline_in_band], NO_CLEANUP: [must_fail_collapse],
  gamma_sweep: [reported_not_gated]}`.
- positive_control_arms (Gate D): MEMORYLESS + SUPPLIED + AUTONOMOUS_GREEDY reproduce the greedy-cell/fair-test
  MEASURED anchors at the matched FULL regime (identical n_nodes=5000 / code_dim=2048 / feat_dim=8192 / epochs=140 /
  seeds / n_chains); tolerance 0.10; drift -> `INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT`. regime_extension_audit:
  SHAPE_MATCH (verbatim reuse of the fair-test/greedy arms + identical chain sampler/rng offset).
- sweep_alignment_verdict: ALIGNED (hop-depth axis; the SR arm experiences the depth axis it is scored on).
- discriminating_fraction_na: "fixed-arm paired comparison (SR vs greedy vs supplied), not a parameter bracket".
- composition_edges: local-neighborhood-scoping (nbr table) -> SR-reachability combine. verdict: SHAPE_MATCH (SR
  column lookup replaces the goal-cosine term in the same fair-test combine; no adapter needed).
- functional_requirements: (1) generate a real candidate set each hop -> nbr table (reused); (2) value candidates
  by multi-step goal-conditioned reachability -> closed-form SR column (new scoring fn, no learning); (3) commit +
  chain -> top-1 commit loop (reused). No new retrieval mechanism.
- calibration_check: adaptive_with_discriminator_gate. `SR_GAMMA_PRIMARY`=0.85 and `SR_BOOST`=1.5 (=certified
  GOAL_GAMMA) PRE-REGISTERED, NOT tuned on real data. The clean planted self-test verifies these let SR_SEEDED
  recover ~SUPPLIED (disc_frac=1.0) with a non-degenerate column, so a real-data collapse is a genuine graph-
  structure/smearing negative, not a mis-set knob. Diagnostic gamma sweep {0.70,0.85,0.95} logged, NOT verdict.
- SR non-degeneracy gate: mean per-goal normalized-column std >= 1e-4 (else `INCONCLUSIVE_SR_COLUMN_DEGENERATE`;
  guards against a smeared/uniform resolvent auto-passing).
- cell_chunked: false (multi-seed within one cell; FULL fast on GPU; per-seed write_partial + failure-class
  instrumentation present).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback, atomic).
- heartbeat_present: true (encoder emits `_heartbeat.jsonl` via the shared trainer); per-seed/per-gamma flush prints.
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed/per-gamma flush prints). timeout_s
  1800.
- run_mode default = `full` (argparse default); runner invokes `python -u cell.py` -> FULL. Post-dispatch RUN_MODE
  VERIFICATION expected: run_mode=full, size > 5KB.

## Config
- FULL: seeds [7,13,17], n_nodes 5000, epochs 140, batch 512, code_dim 2048, feat_dim 8192, temp 0.10, lr 0.008,
  n_chains 1200, chain_chunk 256 (IDENTICAL to greedy/fair-test FULL_CFG -> anchor reproduction).
- SMOKE: seeds [7,13], n_nodes 1800, epochs 60, code_dim 512, feat_dim 4096, n_chains 700 (matched sibling smoke).

## Self-test result (MEASURED, CPU, 1.5s) -- SR DISCRIMINATES ON THE CLEAN GRAPH: YES
- clean planted branch graph (aliased same-relation siblings, true successor forward-connected to G, off-path
  siblings structural dead-ends): NO_CLEANUP collapses; MEMORYLESS aliased @1=0.382 (~1/3); SUPPLIED recovers
  @1-3=1.0; SR_SEEDED reach@[1..4]=[1.0,1.0,1.0,1.0] ~= SUPPLIED (>= at hop-4).
- `sr_disc_frac = 1.0` (the resolvent ranks the on-path node above every off-path dead-end in 100% of chains).
- `sr_not_degenerate = True` (col_std=0.0276, col_peak=1027 -> sharply peaked, NOT uniform/smeared). arms_differ.
- MEASURED@data/exp_grounding_multihop_sr_reachability_routing_v1_selftest/metrics.json

## Smoke result (MEASURED, CPU, 2 seeds, 18.5s wall)
- Gates fired: NO_CLEANUP@2=0.014 collapses; MEMORYLESS@1=0.499 in-band; SUPPLIED@2=0.499 fires (>> memoryless);
  AUTONOMOUS_GREEDY@2=0.167 (reproduces the greedy 0.181 anchor); SR non-degenerate (col_std 0.031, col_peak 295);
  arms differ. Smoke = PASS (all discriminators fire).
- CG preview: SR_SEEDED reach@2=0.366; ratio-to-supplied 0.734; delta-over-greedy +0.199; delta-over-memoryless
  +0.215; gamma sweep reach@2 {0.70:0.364, 0.85:0.366, 0.95:0.372} (near-flat, winning=0.95 at smoke scale).
  Smoke verdict = MIDDLE_BAND_CG_SR_PARTIAL (0.366 in [0.20,0.40); just under the 0.40 HARD_PASS bar).
- MEASURED@data/exp_grounding_multihop_sr_reachability_routing_v1_smoke/metrics.json
- HONEST NOTE: smoke previews MIDDLE_BAND -- SR_SEEDED (0.366) materially beats BOTH prior autonomous attempts
  (greedy 0.167, landmark 0.111) but sits just below HARD_PASS at reduced n=1525/code_dim=512. FULL at
  code_dim=2048 / 140 epochs / n~4440 is the canonical measurement (higher-dim codes + larger graph may sharpen
  reachability). Verdict HELD to the FULL run per smoke-inverts-at-scale discipline.

## Dispatch
- queue: overnight_queue (GPU idle; canonical FULL). timeout_s: 1800.
- self-test PASS (SR discriminates on clean graph); smoke PASS (machinery/gates); positive controls reproduce
  the anchors.
