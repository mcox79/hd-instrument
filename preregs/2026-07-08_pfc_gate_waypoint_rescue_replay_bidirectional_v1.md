# Pre-registration: pfc_gate_waypoint_rescue_replay_bidirectional_v1

Date: 2026-07-08
Author: exp_dev (cell author)
Cell: `experiments/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1.py`
Design source: `notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md`
Ancestors (verbatim primitive reuse + already-measured control arms):
- `experiments/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py` (PARENT; FULL landed
  HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL)
- `experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py` (grandparent; original HARD_FAIL)
- `experiments/exp_pfc_gate_cfrpe_trained_v2.py` (certified SR/M + Go/NoGo gate + execution loop lineage)

## Question
BARRIER #2 (long reasoning chains drift / compounding error). Two ML-precedented single-channel fixes
(coarse-to-fine, verify-gate) ALREADY FAILED on this exact regime, each returning ~zero lift over the
already-failed open bisection. The brain-first drill's diagnosis: both failed fixes correct a noisy
estimate using MORE OF THE SAME noisy estimate (self-referential). Does a BRAIN-FIRST, informationally-
INDEPENDENT correction -- replay-generate-then-select with bidirectional (forward/reverse) agreement
scoring -- recover real autonomous-decomposition capability where the self-referential fixes could not?

## Mechanism under test (rank 1 in the drill; additive, brain-precedented)
REPLAY-GENERATE-THEN-SELECT: (1) generate N_CAND=5 COMPLETE candidate trajectories (candidate 0 = the
unperturbed open bisection; 1..4 = independently gaussian-perturbed argmax tie-breaks; no retrain);
(2) train a REVERSE SR (M_rev/R_rev on cur<->nxt-swapped transitions) as an informationally-INDEPENDENT
second channel; (3) score each COMPLETE candidate by forward-vs-reverse AGREEMENT (harmonic mean of mean
forward-leg reach over R_fwd and mean reverse-leg reach over R_rev, each cosine mapped to [0,1]);
(4) commit the single best-scoring WHOLE candidate. Execution loop identical to both ancestors for every
arm -- the waypoint SOURCE is the only thing that differs.
CITED@Pfeiffer-Foster 2013 (full-path pre-commitment); CITED@Foster-Wilson 2006 (reverse replay);
CITED@Ross-Bagnell 2010 (O(T^2) compounding).

## Arms (11; paired)
flat_gonogo (FLOOR), oracle_exec (rail/ceiling), hier_oracle (given-decomp ceiling), hier_shuffled
(neg control), wp_bisect_open (parent failing baseline), wp_bisect_verify (KEY comparator: already-failed
SELF-REFERENTIAL control), wp_bisect_coarse2fine + wp_bisect_combo (already-failed self-ref controls,
re-run for paired continuity), wp_replay_generate_select (NEW mechanism under test),
wp_random_state (autonomous floor), wp_index_midpoint (structural-artifact guard).

best_rescue = wp_replay_generate_select (FIXED, not a max-over-arms). KEY comparator = wp_bisect_verify.

## FOCUS regime
op4_V1200_d8 (chain_steps=3), the exact parent HARD_FAIL corner. Flatness reference = op4_V1200_d4
(chain_steps=1). MEASURED ancestor @data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json:
op4_V1200_d8 recovery_verify=0.0182; op4_V1200_d4 recovery_verify=0.7029.

## Bands (LOCKED before running; envelope-fail-bands)
recovery(a) = (a - flat) / (hier_oracle - flat).  delta_recovery = recovery(replay) - recovery(verify)
[KEY, vs the SELF-REFERENTIAL control].  flatness_ratio = recovery(replay, FOCUS d8) /
recovery(replay, d4).

HARD_PASS (independent-signal hypothesis confirmed):
- recovery(replay) >= 0.20 AND
- delta_recovery >= 0.15 AND
- flatness_ratio >= 0.50 AND
- lift_flat > 0.05 AND lift_random > 0.10 AND
- index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85 AND degenerate_rate < 0.10 AND
- sign_p(replay vs verify) < 0.05 AND cv(replay) < 0.15 (FULL only) AND
- oracle_exec >= 0.90 AND headroom_exec >= 0.10 AND headroom_decomp >= 0.10.
=> The compounding-error bound was an artifact of SELF-REFERENTIAL correction specifically; a brain-first
independent (bidirectional) signal recovers real autonomous-decomposition where two ML fixes could not.
Binding constraint (given ancestor shallow recovery ~0.70): recovery(replay) at d8 >= ~0.35.

HARD_FAIL (bound survives even independent-signal correction; doubly confirmed structural):
- delta_recovery <= 0.05 (recovery(replay) <= recovery_verify + 0.05, ~0.068 at FOCUS) -- verdict
  HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL; OR
- flatness_ratio < 0.20 (accelerating, not bounded, collapse) -- verdict HARD_FAIL_ACCELERATING_COLLAPSE.
=> Accept the bound as fundamental for this domain/training-budget; keep deployment chains SHORT; redirect
replay/cerebellar effort to the GENERAL reasoning loop.

MIDDLE_BAND: delta_recovery in [0.05, 0.15) OR flatness_ratio in [0.20, 0.50) OR
(delta>=0.15 & flatness>=0.5 but recovery(replay)<0.20) OR any honesty guard fails while margins pass.
Sub-reasons emitted: PARTIAL_RESCUE_DELTA_BELOW_15 / FLATNESS_BELOW_50 / RECOVERY_BELOW_20 /
DEGENERATE_GUARD / ANTI_TAUTOLOGY_GUARD / INDEX_ARTIFACT_GUARD / LIFT_RANDOM_BELOW / SIGN_TEST_NS /
CV_TOO_HIGH / SUBTHRESHOLD.

INCONCLUSIVE: no discriminating regime (oracle rail / headroom gates fail) OR index_artifact_gap > 0.10
with idx_sign_p < 0.05 (genuine chain-generation structural leak).

Honest either way: if replay does NOT beat the bound, that is a real, informative NEGATIVE (the drift
bound is deeper than independent-signal correction). P_deflated ~0.25-0.30 any real lift over verify,
~0.15-0.20 full HARD_PASS (per the drill's two-prior-failures sober update).

## SCHEMA-VET mandatory fields
cardinality_ok: true  (EXPECTED_N_UNITS = n_arms(11) * n_seeds * n_regimes; verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if completed < expected)

sweep_alignment_verdict: ALIGNED
  swept_params: dd (chain depth) in {4,6,8} at op4; secondary n_ops/V regimes for entropy dissociation.
  effective_params_per_primitive: the discriminator (recovery, delta_recovery, flatness_ratio) is
  measured on the SAME dd the execution loop experiences; chain_steps = n_boundaries(dd,SEG_LEN)-1 is
  the effective decision-count each arm faces. No partition-routing indirection (unlike multihop_v3).

discriminating_fraction: >= 0.5 (FULL grid op4 {d4,d6,d8} + op3_d8 + op2_d8). d4 = open/verify already
  recover (~0.70, shallow already solved, NOT saturated at 1.0); d6/d8 = collapse corners (recovery
  ~0.0-0.1). MEASURED ancestor: d4 recovery_verify=0.703, d8 recovery_verify=0.018 -- both in
  measurable band, neither saturated >0.90 nor floored at the mechanism ceiling. >= 3/5 regimes land in
  a discriminating band for the replay-vs-verify contrast.

composition_edges (signal_shape_compatibility_audit): SHAPE_MATCH throughout.
  - open_bisection -> perturbed_candidate_generation: same [n_chains, n_bnd] boundary tensor. MATCH.
  - forward_R + reverse_R -> score_bidirectional: both are [V,V] reach matrices; gather is shape-safe.
    MATCH.
  - selected_boundaries -> _boundaries_to_hops -> run_hier_arm_wp: identical schedule shape to every
    other wp_* arm (VERBATIM ancestor path). MATCH.

positive_control_arms (Gate D; composing prior chain-grade primitives):
  - arm: wp_bisect_open_REPRODUCE_AT_TEST_REGIME
    primitive: parent open bisection (SR reach + balance argmax execution loop)
    cited_prior_atom: exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1 op4_V1200_d8 wp_bisect_open=0.097
    cited_prior_metric: 0.097 ; cited_prior_regime: {N:8192, V:1200, op4, dd8, seeds 7/17/23/31/41}
    test_regime: IDENTICAL (this cell trains M/R with the SAME sr_gen seed formula as the ancestor ->
      reproduces M/R/wp_bisect_open/flat/hier_oracle/verify BY CONSTRUCTION). tolerance: 0.10.
    if_outside_tolerance: positive-control drift flag (downstream replay comparison suspect).
    regime_extension_audit: SHAPE_MATCH (same synthetic-bipolar regime, same primitives, additive only).
  - Also re-runs wp_bisect_verify (the KEY comparator) IN-CELL on identical seeds -- the delta is a
    within-cell paired contrast, not a cross-regime citation.

functional_requirements (Gate E):
  - FR1 "generate multiple complete candidate routes, not one greedy per-hop pick" -> perturbed
    open-bisection candidate generator (NEW; reuses open bisection machinery).
  - FR2 "correcting signal independent of the forward accumulator" -> reverse SR M_rev/R_rev (NEW;
    reuses train_sr_transport verbatim on swapped transitions).
  - FR3 "score whole candidates by forward/reverse agreement" -> score_bidirectional harmonic mean (NEW).
  - FR4 "execute the committed decomposition" -> run_hier_arm_wp (VERBATIM ancestor; certified CG loop).
  - FR5 "denoise each candidate's constituent vectors" -> cleanup_batched inside run_hier_arm_wp
    (VERBATIM; representation-fidelity layer, unchanged).

final_metrics_atomicity: tmp_replace (os.replace on metrics.json; _atomic_write_metrics).
crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor. Reachability by
  feasibility: ancestor hier_oracle=0.906 at op4_d8 proves the given-decomposition envelope; open+verify
  collapse to ~flat -> open question is how much of the 0.906 headroom the INDEPENDENT-signal replay
  recovers over verify's 0.018. HP bar (recovery>=0.20 AND flatness>=0.5, binding ~0.35 absolute) sits
  well inside the 0.906 envelope. discriminator_reachability: true.
baseline_in_band: true. KEY baseline = wp_bisect_verify, collapsed to ~flat at FOCUS
  (0.096 vs flat 0.081; recovery 0.018). Discriminator = replay-vs-verify, both measurable. oracle_exec
  >= 0.90 rail + headroom >= 0.10 gates guarantee room to recover; d4 (verify recovers ~0.70) proves the
  baseline is NOT saturated at the mechanism ceiling.
discriminator_survives_scale: option C directional preview. Smoke holds op4 x {d4,d6,d8} at V=300,
  N=2048 (BLUNTER reach than FULL N=8192; ancestor reach_rank d8 0.27 smoke -> 0.445 full). A POSITIVE
  replay-minus-verify at smoke is a LOWER bound on FULL. Smoke that shows open+verify collapse + oracle
  success + any positive replay-minus-verify + replay trace differs gates the GPU FULL. HARD_PASS at
  FULL is the canonical verdict (not smoke).
HP_SCOPE:
  wp_replay_generate_select: [recovery>=0.20, delta_recovery>=0.15, flatness>=0.5, lift_flat, lift_random,
    sign_p, cv, guards]
  oracle_exec: [oracle_rail >= 0.90]
  hier_oracle: [headroom_decomp reference]
  wp_index_midpoint vs wp_random_state: [index-order-leak guard]
  (bare-baseline / neg-control arms do NOT inherit the chain-grade HP gates.)

arms_differ_verified: true (smoke gate; replay op-trace hash != verify/open/flat/random per seed;
  hier_oracle != hier_shuffled). AF collision -> hp_ok=False.
calibration_check: adaptive_with_discriminator_gate. verify-gate tau = 70th-pctl of R off-diagonal;
  replay perturbation = PERTURB_FRAC(0.60) * per-row balance std (principled scale-relative noise);
  N_CAND=5 fixed. Discriminator = delta-over-verify + flatness, NOT tuned-for-PASS.

## Defensive error-checking (MANDATORY)
cell_chunked: false  (multi-seed within one cell via _seed_checkpoint resumable_seeds/write_partial_key;
  per-seed crash sets fatal-flag + writes failure_class partial + demotes HP->MIDDLE; restartable).
start_marker_written: true  (_write_start_marker at main() entry).
crash_diagnostic_present: true  (except SystemExit: raise BEFORE except Exception; _write_crash_metrics
  writes CELL_CRASHED + traceback atomically).
heartbeat_present: true  (_heartbeat per seed; per (seed,V,n_ops) SR-diag print).
defensive_error_checking: passed_all_4_patterns.
progress_logging: print_flush_true  (flush=True on every progress line; per-seed + per-regime).

## Compute architecture
(a) batched-GPU. SR-TD training (M @0.85, M_long @0.95, M_rev @0.85 on reversed transitions), operator
application, cleanup, reach, R build, bisection + perturbed candidate generation + bidirectional scoring
= batched matmuls / gathers / argmax on cuda-if-available. Chains batched; within-chain hops sequential
(genuine dependency). M/M_long/M_rev/R_* computed once per (V,n_ops) group and shared across depths.
Storage strategy: sharded (each operator its own W; M/M_long/M_rev learned operators; R_* derived reach
matrices). No bundled store. FULL strongly prefers overnight_queue (GPU). Extra cost vs coarse2fine
ancestor: one 3rd SR train (M_rev) + N_CAND=5 cheap re-bisections + one vectorized scoring pass; linear
in N_CAND, no quadratic blowup.

## Config
SMOKE: N=2048, seeds [7,17,23], op4 {d4,d6,d8} V=300, SR_STEPS=2500, local_cpu (smoke only).
FULL:  N=8192, seeds [7,17,23,31,41], regimes op4 {d4,d6,d8} V=1200 + op3_d8 V=1000 + op2_d8 V=800,
  SR_STEPS=8000. Route: overnight_queue (GPU).

## MEASURED/HYPOTHESIZED/THEORETICAL/CITED tags
- recovery_verify FOCUS op4_V1200_d8 = 0.0182 MEASURED@data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json
- recovery_verify op4_V1200_d4 = 0.7029 MEASURED@ (same file)
- hier_oracle op4_V1200_d8 = 0.906 MEASURED@ (same file)
- HARD_PASS binding constraint recovery(replay,d8) >= ~0.35 THEORETICAL@(flatness>=0.5 * shallow~0.70)
- P_deflated any lift ~0.25-0.30, full HP ~0.15-0.20 HYPOTHESIZED@this prereg (drill (c))
