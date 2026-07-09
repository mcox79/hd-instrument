# Pre-registration: autonomous-subgoal greedy goal-directed multi-hop traversal (MM -> CG)

- anchor_name: `grounding_multihop_autonomous_subgoal_greedy_v1`
- cell: `experiments/exp_grounding_multihop_autonomous_subgoal_greedy_v1.py`
- date: 2026-07-09
- builds on: fair-test goal-conditioning MM (`grounding_multihop_fair_test_unique_successor_goal_v1`)
- design note: `notes/research_autonomous_subgoal_derivation_goal_directed_traversal_CG_path_2026-07-09.md`

## Question
The goal-conditioning MM is certified: HANDING the query a ground-truth next waypoint lifts hop-1 reach and
reach@2 substantially. That is MM because the waypoint is SUPPLIED. This cell asks the CG question: can the
substrate DERIVE each intermediate hop ITSELF, given ONLY (start, relation-sequence, FINAL goal), never the
intermediate waypoints, and thereby recover the supplied-waypoint lift autonomously?

## Mechanism (no new primitive; reuse only)
Greedy goal-directed SELECTION among REAL local neighbors (brain-ground: Gupta 2010 replay SPLICES real
experienced fragments; ML generate-and-verify). At each hop with current node `cur` and final goal `G`:
`score(candidate v) = <l2(bind(role_r, Z[cur])), Z[v]> + AUTO_GAMMA * max(0, cos(Z[v], Z[G]))`; argmax over the
real local out-neighbors of `cur`; commit. Reuses local-neighborhood scoping (nbr table) for the candidate set +
the certified goal-conditioning combine for the guidance. Does NOT synthesize a waypoint code from nothing.

## Arms (paired: identical codes + general chains + seeds + graph + dim; only the query differs)
- `NO_CLEANUP` — global-cleanup-only chain; must-fail / anti-saturation control (collapses at reach>=2).
- `MEMORYLESS` — goal-blind local decoder = fair-test floor (positive-control repro).
- `SUPPLIED_WAYPOINT` — = fair-test `GOAL_WAYPOINT` MM ceiling; handed the true next waypoint each hop
  (positive-control repro).
- `AUTONOMOUS_GREEDY` — THE CG CANDIDATE (primary): goal-cosine argmax among real neighbors toward the FINAL
  goal only. Verdict is computed on this arm.
- `AUTONOMOUS_VERIFY` — secondary wrapper: restrict argmax to candidates whose goal-cosine strictly exceeds the
  current node's goal-cosine (generate-and-verify); fall back to memoryless pick when none improve. Reported,
  not gated (never swapped in to rescue a verdict).

## Pre-registered CG bands (verdict on AUTONOMOUS_GREEDY reach@2)
- `HARD_PASS_CG` (`HARD_PASS_CG_AUTONOMOUS`): `auto2 >= 0.85 * supplied2` AND `auto2 >= memoryless2 + 0.10`.
  Autonomous derivation ~matches the supplied ceiling -> autonomous goal-directed reasoning WORKS.
- `HARD_FAIL_CG` (`HARD_FAIL_CG_AUTONOMOUS_COLLAPSE`): `auto2 <= memoryless2 + 0.03`. Goal-cosine too weak at
  multi-hop distance -> derivation collapses to the goal-blind floor (next: landmark/betweenness precompute or
  resonator full-chain factorization).
- `MIDDLE_BAND_CG_PARTIAL`: autonomous beats memoryless materially but sits well below the supplied ceiling.
- Guard verdicts: `INCONCLUSIVE_HOP1_ABSENT`, `INCONCLUSIVE_BASELINE_DID_NOT_FAIL`,
  `INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE`, `INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT`.

The ratio bar self-calibrates to the SUPPLIED reach@2 MEASURED in the same run (robust to small config drift).

### Reference anchors (all MEASURED)
- MEMORYLESS reach@1 = 0.453, reach@2 = 0.121
  MEASURED@data/exp_grounding_multihop_fair_test_unique_successor_goal_v1/metrics.json:gates.reach.MEMORYLESS
- SUPPLIED (GOAL_WAYPOINT) reach@1 = 0.756, reach@2 = 0.500
  MEASURED@data/exp_grounding_multihop_fair_test_unique_successor_goal_v1/metrics.json:gates.reach.GOAL_WAYPOINT
- HARD_PASS bar reach@2 = 0.85 * 0.500 = 0.425  THEORETICAL@0.85*supplied2
- top-1 chance floor = 1/n_nodes ~ 0.0002 at n=5000  THEORETICAL@1/n_nodes

## Capability framing (3-part; CG claim, verify-able)
- DIFFERENT CHANNEL: downstream reach@2/@3 (top-1 commit chained).
- LIVE ALTERNATIVE: the goal-blind MEMORYLESS query genuinely fails on same-relation branch points.
- NECESSITY: autonomous goal-selection vs no-goal (MEMORYLESS) ablation, paired. Report autonomous-vs-supplied
  ratio + autonomous-vs-memoryless delta.

## Compute architecture
class: (c) mixed. Storage: SHARDED (each node its own code; compositional chaining). Within-hop scoring batched
matmul/einsum on GPU (cuda when available); across-hops genuinely SEQUENTIAL (inherent chain data-dependency,
same shape as the fair-test cell which ran 3 seeds FULL in 16.4s on cuda). No Python-loop matmul over
independent phase points.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (FULL 3). Each seed asserted to produce all 5 arms x depths 1-4.
- arms_differ_verified: true (AUTONOMOUS_GREEDY commit-sig != SUPPLIED != MEMORYLESS != NO_CLEANUP; per-seed).
- final_metrics_atomicity: tmp_replace (via `_seed_checkpoint.write_metrics` + `os.replace`).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except). Verified.
- crlb_floor_computed: 1/n_nodes ~ 0.0002; crlb_formula_reference: `top1_chance = 1/n_nodes`.
  discriminator_reachability: true (SUPPLIED already demonstrated reach@2=0.500 is reachable with a goal signal;
  HARD_PASS bar 0.425 is below that ceiling).
- baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (repro ~0.453). NO_CLEANUP@2 collapses (anti-saturation).
- discriminator_survives_scale: the MM discriminator (SUPPLIED >> MEMORYLESS, `supplied_fires`) is
  graph-structural and asserted to fire at smoke; the must-fail control NO_CLEANUP collapses AT smoke scale
  (SATURATION-VACUOUS guard). The CG measurement (autonomous-vs-supplied) is the RESULT; FULL (3 seeds) canonical.
- HP_SCOPE: `{AUTONOMOUS_GREEDY: [CG_HARD_PASS], SUPPLIED_WAYPOINT: [positive_control_repro],
  MEMORYLESS: [positive_control_repro, baseline_in_band], NO_CLEANUP: [must_fail_collapse],
  AUTONOMOUS_VERIFY: [reported_not_gated]}`.
- positive_control_arms (Gate D): MEMORYLESS + SUPPLIED reproduce the fair-test MEASURED anchors at the matched
  FULL regime (identical n_nodes=5000 / code_dim=2048 / feat_dim=8192 / epochs=140 / seeds / n_chains); tolerance
  0.10; drift -> `INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT`. regime_extension_audit: SHAPE_MATCH (verbatim reuse
  of the fair-test arms + identical chain sampler/rng offset).
- sweep_alignment_verdict: ALIGNED (hop-depth axis; the autonomous arm experiences the same depth axis it is
  scored on).
- discriminating_fraction: n/a for a fixed-arm comparison (not a parameter bracket); the discriminating question
  is auto-vs-supplied at fixed depths. discriminating_fraction_na: "fixed-arm paired comparison, not a sweep".
- composition_edges: local-neighborhood-scoping (nbr table) -> goal-cosine combine. verdict: SHAPE_MATCH (both
  are the fair-test combine applied to a self-generated candidate set; no adapter needed).
- functional_requirements: (1) generate a real candidate set at each hop -> nbr table (reused); (2) value
  candidates toward a stated goal -> goal-cosine combine (reused, certified); (3) commit + chain -> top-1 commit
  loop (reused). No new mechanism required.
- calibration_check: adaptive_with_discriminator_gate. AUTO_GAMMA = 1.5 PRE-REGISTERED (= certified GOAL_GAMMA),
  NOT tuned on real data. The mechanism self-test verifies gamma=1.5 lets AUTONOMOUS recover ~SUPPLIED on clean
  goal-ward planted codes, so a real-data collapse is a genuine signal-weakness negative, not a mis-set knob. A
  diagnostic gamma sweep {0.5,1.0,1.5,2.5} is logged but does NOT drive the verdict.
- cell_chunked: false (multi-seed within one cell; FULL is fast on GPU ~<2min; per-seed write_partial + failure-
  class instrumentation present; single-cell acceptable for this cheap GPU cell).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback, atomic).
- heartbeat_present: true (encoder emits `_heartbeat.jsonl` via `_cell_heartbeat.emit_heartbeat`).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed flush prints). timeout_s target
  3600 (>= 1800 so field required).
- run_mode default = `full` (argparse default); runner invokes `python -u cell.py` -> FULL. Post-dispatch
  RUN_MODE VERIFICATION expected: run_mode=full, size > 5KB.

## Config
- FULL: seeds [7,13,17], n_nodes 5000, epochs 140, batch 512, code_dim 2048, feat_dim 8192, temp 0.10, lr 0.008,
  n_chains 1200, chain_chunk 256 (IDENTICAL to fair-test FULL_CFG -> anchor reproduction).
- SMOKE: seeds [7,13], n_nodes 1800, epochs 60, code_dim 512, feat_dim 4096, n_chains 700 (matched fair-test smoke).

## Smoke result (MEASURED, CPU, 2 seeds, 29s wall)
- Gates fired: NO_CLEANUP@2=0.014 collapses; MEMORYLESS@1=0.499 in-band; SUPPLIED@2=0.499 fires (>> memoryless);
  positive-control repro OK (mem1/sup1/sup2 within tol); arms differ.
- CG preview: AUTONOMOUS_GREEDY reach@2=0.167; ratio-to-supplied 0.335; delta-over-memoryless +0.016;
  AUTONOMOUS_VERIFY does not help (delta +0.002). Smoke verdict = HARD_FAIL_CG_AUTONOMOUS_COLLAPSE.
- MEASURED@data/exp_grounding_multihop_autonomous_subgoal_greedy_v1_smoke/metrics.json
- HONEST NOTE: smoke previews a HARD_FAIL (raw goal-cosine to a distant final goal is a weak navigational signal
  on real learned codes). FULL at code_dim=2048 / 140 epochs is the canonical measurement (higher-dim codes may
  sharpen or confirm). Both outcomes are gold (design note: HARD-FAIL still valuable -> directs next mechanism).

## Dispatch
- queue: overnight_queue (GPU idle; canonical FULL). timeout_s: 3600.
- self-test PASS; smoke PASS (machinery/gates); positive control reproduces the MM anchors.
