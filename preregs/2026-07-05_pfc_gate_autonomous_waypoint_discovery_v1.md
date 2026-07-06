# Pre-reg: pfc_gate_autonomous_waypoint_discovery_v1

Author: exp_dev (Opus 4.8 1M, agent-spawn) 2026-07-05
Cell: `experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py`
Anchor: `pfc_gate_autonomous_waypoint_discovery_v1`  (smoke: `_smoke`)

## Question
The ancestor `pfc_gate_branching_depth_entropy_grid_v1` proved hierarchical control is HARD_PASS at
FULL *given a correct decomposition* (oracle waypoints = true intermediate chain states):
MEASURED@data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json FOCUS=op4_V1200_d8(ent=16)
FLAT=0.082 HIER_ORACLE=0.861 ORACLE_EXEC=0.938 hier_closure=0.910. Those waypoints were
`oracle_trajectory_idx(...)` -- an assumed-optimal top-level option policy handed to the arm
(declared oracle-assist; ancestor docstring 34-39: "Autonomous waypoint DISCOVERY is an explicit
FOLLOW-ON, not claimed here"). THIS cell answers the follow-on: **can the substrate supply its OWN
sub-goal decomposition from what it already learned (E, W_ops, trained SR transport M), with NO
oracle trajectory?**

USER-LOCKED FRAMING: NARROW glass-box sub-goal-discovery PRIMITIVE step. NOT autonomous planning,
NOT self-improvement. HARD_PASS would mean only "given a trained SR over a small known state space,
the substrate can propose its own waypoints for control tasks in that space." Honest tier.

## Mechanism (TESTED, not assumed): SR-reach-matrix bisection
New near-zero-cost primitive -- the state-by-state REACH MATRIX from the already-trained SR M:
`Efwd = normalize_rows(E @ M); R = Efwd @ normalize_rows(E).T` => `R[i,j] == reach_value(E[i],E[j],M)`,
built once per (seed, V, n_ops) group.
PRIMARY arm = sequential greedy BISECTION over R (MPNet learned-midpoint-proposal analog;
meet-in-the-middle depth-reduction; Stachenfeld-2017 SR-predictive-map grounding scoped as a
computational metaphor, NOT confirmed neural algorithm): for each interior segment boundary,
`wp = argmax_{c not in {start,goal,chosen}} min(R[anchor,c], R[c,goal])`, anchor = prev wp.
SECONDARY arms restrict that same argmax to a spectrally/cluster-privileged candidate subset
(eigenoption sign-boundary / PCCA+-lite low-margin states). DOMAIN-FIT hypothesis (from the drill,
NOT assumed): random operator graphs at DENSITY=0.21 LACK true bottleneck structure -> restriction
expected NEUTRAL-to-HARMFUL vs open. CITED@Machado 2018 (deep-SR eigenoptions); Qureshi 2019 (MPNet);
Deuflhard-Weber 2005 (PCCA+); Stachenfeld-Botvinick-Gershman 2017; Holte 2016 (MM bidirectional).
Prior-work check: substrate director-KB/notes grep for waypoint|subgoal|eigenoption|bisect|bottleneck|
PCCA returns the arc ancestor + the 2026-06-27/28 BlocksWorld hierarchical-planning line (DIFFERENT
mechanism class: hand-defined I/pi/beta option channels, closed-form D-prediction, different domain).
The SR-reach-matrix bisection / eigenoption / PCCA mechanism is GENUINELY NOVEL in this lineage (not
a rediscovery). substrate-KB concept-query is encoder-native char-trigram (wordnet noise at 0.36); the
notes/director-KB grep is the load-bearing prior-work check here.

## Arms (9; paired -- share E, W_ops, M, R and the SAME test chains per (regime,seed))
flat_gonogo (FLOOR; collapses) | oracle_exec (perfect op execution; ceiling + FOCUS rail) |
hier_oracle (oracle waypoints; given-decomposition CEILING) | hier_shuffled (wrong-chain oracle
waypoints; neg control) | wp_bisect_open (PRIMARY autonomous) | wp_bisect_spectral (Cand a) |
wp_bisect_cluster_exit (Cand c) | wp_random_state (autonomous FLOOR: noise waypoints) |
wp_index_midpoint (structural-artifact guard; index-interpolated waypoints).
Waypoint SOURCE is the ONLY thing that differs across wp_*/hier_oracle/hier_shuffled arms; the
per-segment low-horizon EXECUTION loop (run_hier_arm_wp) is identical for all. oracle_trajectory_idx
is computed for hier_oracle/hier_shuffled/exact_match only; NOT visible to any wp_* decomposition.

## Grid + discriminators
GRID: n_ops {2,3,4} (branching) x depth {4,6,8} at FIXED gamma=0.85. entropy=log2(n_ops)*depth.
Per regime; best_wp = max(open, spectral, cluster):
  headroom_exec = oracle_exec - flat; headroom_decomp = hier_oracle - flat;
  autonomous_closure(a) = (a-flat)/headroom_exec   (frac of flat->perfect closed; cf ancestor 0.910)
  recovery_ratio(a)     = (a-flat)/headroom_decomp (frac of the oracle-DECOMPOSITION benefit recovered)
  lift_flat = a-flat; lift_random = a-wp_random; index_artifact_gap = wp_index-wp_random;
  degenerate_rate = P(UNMASKED bisection argmax == start OR goal); anti_tautology_corr =
  corr(balance, raw goal-cosine); exact_match_rate = P(discovered wp == true oracle wp) DIAGNOSTIC.
FOCUS = highest-entropy regime with oracle_exec>=0.90 AND headroom_exec>=0.10 AND headroom_decomp>=0.10.
Author note (autonomy over exact metric denominators): the drill formula line wrote autonomous_closure
with a hier_oracle denominator + a redundant recovery_ratio; I split them into DISTINCT well-posed
metrics (autonomous_closure vs oracle_exec, comparable to the ancestor 0.910; recovery_ratio vs
hier_oracle, product-facing). Both HP thresholds (0.15, 0.20) apply as the drill specified.

## PASS / FAIL bands (envelope-fail-bands; LOCKED before run; META_RULE_L strict floors)
- HARD_PASS (best_wp at FOCUS): autonomous_closure >= 0.15 AND recovery_ratio >= 0.20 AND
  lift_flat > 0.05 AND lift_random > 0.10 AND index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85
  AND degenerate_rate < 0.10 AND sign_p(best_wp vs flat) < 0.05 AND cv(best_wp) < 0.10 (FULL only)
  AND oracle_exec >= 0.90 AND headroom gates => the substrate can discover a partially-useful
  decomposition from its own trained SR, no oracle.
- HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION: lift_flat(best_wp) <= 0.05 OR
  lift_random(best_wp) <= 0.05 => control solvable GIVEN a decomposition (proven) but the substrate's
  own SR does not carry enough info to supply that decomposition at the FOCUS regime -- a real,
  informative, structural bound (guarded clean by index/anti-tautology/degenerate).
- MIDDLE_BAND_*: beats flat AND random by margins but recovery_ratio<0.20 (or closure<0.15), OR an
  honesty guard fails while accuracy margins pass.
- INCONCLUSIVE_NO_DISCRIMINATING_REGIME | INCONCLUSIVE_INDEX_ORDER_LEAK (index_artifact_gap>0.10 with
  sign_p(index vs random)<0.05 => genuine chain-generation structural leak; comparisons invalid).
Reported REGARDLESS: full entropy-grid table for every wp_* arm; spearman(recovery_ratio, entropy);
spectral_minus_open / cluster_minus_open at FOCUS (domain-fit sub-result); exact_match_rate;
AUTONOMOUS-CAPABILITY DEPTH FRONTIER (n_regimes_hp_ok, autonomous_capability_frontier, max_entropy_hp_ok
-- how far up the entropy ladder autonomous discovery clears the full per-regime HP bar; honest
enrichment that does NOT move the strict-FOCUS primary verdict).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_arms(9) * n_seeds(5) * n_regimes(9) = 405 (FULL). MEASURED@smoke:
  108/108 (9 arms * 3 seeds * 4 regimes).
- arms_differ_verified (AF): best_wp trace vs flat AND vs random per seed + hier_oracle vs hier_shuffled;
  waypoints differ by construction so a hash collision flags an impl bug. MEASURED@smoke: af_collision
  False all regimes (some regimes hp_ok in fix2sr require not-af).
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-gate: PASS (CLEAN, no bare
  except / BaseException). The eigh fallback except records failure_class + degrades spectral/cluster to
  open loudly (stderr + sr_diag), never silent-continues.
- baseline_in_band (META_RULE_AG): discriminator is FLAT-referenced; FOCUS gate = oracle_exec>=0.90 AND
  headroom_exec>=0.10 AND headroom_decomp>=0.10 (measurable room; substitute for additive-in-band, as
  the ancestor -- flat collapses by design at op4_d6/d8).
- calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + wp_random floor +
  wp_index structural-leak guard + anti_tautology_corr + degenerate_rate all logged per regime).
- crlb_n/a: accuracy-closure has no single closed-form noise floor; reachability by feasibility --
  ancestor hier_oracle=0.861 at op4_d8 proves the given-decomposition envelope; the open question is
  what fraction autonomous discovery recovers (0-1 achievable range; HP floors 0.15/0.20 are on the
  achievable side).
- effective_vs_nominal (Gate A): n_ops sets reach_rank chance + per-hop branching; depth sets chain
  length + n boundaries; SEG_LEN sets per-decision reach horizon + n interior waypoints to discover.
  sweep_alignment_verdict: ALIGNED.
- positive_control (Gate D): flat_gonogo reproduces the ancestor flat collapse AT TEST REGIME
  (op4_d6 flat MEASURED@smoke=0.056 canonical / 0.146 fix2sr -- collapsed, matches ancestor direction);
  hier_oracle reproduces the ancestor given-decomposition ceiling (op4_d6 hier_oracle=0.785 canonical /
  0.910 fix2sr, vs ancestor op4_d8 0.861). Both load-bearing reference arms reproduce at test regime.
- discriminating_fraction (Gate B): FULL grid spans entropy 4..16 (9 points); smoke 4/4 regimes have
  oracle_exec>=0.90 + headroom (discriminating). >= 0.30.
- signal_shape_compatibility (Gate C): all arms consume E/W_ops/M/waypoint-state identically; the new
  R is an [V,V] reach matrix over the SAME E-manifold; waypoint states are E-manifold vectors like
  goals; SHAPE_MATCH throughout.
- functional_requirements: (1) build a reachability model from trained SR -> reach matrix R (new prim,
  near-zero cost); (2) propose interior sub-goals with no oracle -> sequential bisection over R (new);
  (3) prove discovery > noise -> wp_random_state floor; (4) prove no structural leak -> wp_index_midpoint
  guard; (5) prove discovery is dynamics not tautology -> anti_tautology_corr; (6) execute given the
  discovered decomposition -> run_hier_arm_wp (inherited hierarchical gate, chain-grade).
- defensive_error_checking: passed_all_4 (start_marker, crash_diagnostic, heartbeat, chunked via
  resumable_seeds per-seed partial + fatal-flag).
- discriminator_survives_scale (option C): smoke holds N/V==FULL per (V,n_ops)=6.83 AND includes the
  focus op4_d6 at IDENTICAL depth. Scale expectation: at N=8192 + SR_STEPS=8000 the SR reach is far
  SHARPER (ancestor reach_rank 0.40->0.69 N2048->8192; THIS cell's FIX-2 probe already lifted focus
  reach_rank 0.396->0.521 and pushed the capability frontier from None to op4_d4 at only SR=2000/N=2048)
  -> autonomous discovery is EXPECTED to strengthen / push the frontier higher at FULL, while flat stays
  collapsed. The strict deepest FOCUS (op4_d8 at FULL) is DEEPER than the smoke focus, so a strict-FOCUS
  HARD_PASS is a minority outcome (P_deflated ~0.22 per drill); the entropy-surface + capability-frontier
  are the primary deliverable and land regardless.
- progress_logging: print_flush_true (line-buffered stdout + flush=True per line + per (seed,V,n_ops)
  heartbeat). FULL timeout_s >= 1800.

## Compute architecture
(a) batched-GPU. SR-TD training (gamma=0.85 fixed), operator application, cleanup, reach, R build,
bisection argmax, eigh = batched matmuls / one eigh per (V,n_ops) group on cuda-if-available. Chains
batched; within-chain hops sequential (genuine dependency). SR + R + spectral/cluster masks computed
once per group and shared across depths. Storage: sharded (each op its own W; M a learned value
operator; R a derived reach matrix). No bundled store. FULL strongly prefers overnight_queue (GPU).
FIX-2 SR-budget probe overrides (HDLAB_SR_STEPS / HDLAB_ROLLOUT_PER_V / HDLAB_ROLLOUT_CAP) leave every
canonical config UNCHANGED (defaults) and only activate when env vars are set.

## SMOKE RESULTS (N=2048, 3 seeds [7,17,23], grid {n_ops 2,4} x {depth 4,6}, focus op4_d6)

### Canonical smoke -- MEASURED@data/exp_pfc_gate_autonomous_waypoint_discovery_v1_smoke/metrics.json
SR_STEPS=250 rollout_per_V=8 (undertrained by design). 80s wall, cardinality 108/108. verdict=
HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION. CAP_FRONTIER=None n_hp_ok=0/4.
FOCUS op4_V300_d6(ent12): FLAT=0.056 OEXEC=0.917 HIER_ORACLE=0.785 RAND=0.049 IDX=0.056;
best_wp=open=0.104 auton_closure=0.056 recovery_ratio=0.067 lift_flat=0.049 lift_random=0.056;
index_gap=0.007 anti_taut=0.005 degen=0.007 exact=0.010 sign_p=0.108 spec-open=-0.042 clus-open=-0.049.
Grid (FLAT/OPEN/RAND/recov/exact): op2_d4 0.528/0.576/0.389/0.115/0.208; op2_d6 0.167/0.132/0.153/0/0.038;
op4_d4 0.215/0.229/0.125/0.022/0.014; op4_d6 0.056/0.104/0.049/0.067/0.010.

### FIX-2 better-SR probe -- MEASURED@data/exp_pfc_gate_autonomous_waypoint_discovery_v1_smoke_fix2sr/metrics.json
SR_STEPS=2000 rollout_per_V=30 rollout_cap=12000 (the drill's 2x-before-closure candidate at smoke-N).
250s wall, cardinality 108/108. verdict=HARD_FAIL (strict FOCUS op4_d6). CAP_FRONTIER=op4_V300_d4(maxE=8.0)
n_hp_ok=2/4. FOCUS op4_d6: FLAT=0.146 OEXEC=0.951 HIER_ORACLE=0.910 RAND=0.069; best_wp=open=0.167
recovery_ratio=0.027 lift_flat=0.021 lift_random=0.097; guards clean.
Grid (FLAT/OPEN/RAND/recov/lift_flat/lift_rand/exact/spec-open):
  op2_d4 0.861/0.882/0.368/0.214/0.021/0.514/0.833/-0.396
  op2_d6 0.431/0.549/0.160/0.236/0.118/0.389/0.139/-0.403   <- HP_OK
  op4_d4 0.514/0.667/0.181/0.400/0.153/0.486/0.569/-0.347   <- HP_OK (frontier)
  op4_d6 0.146/0.167/0.069/0.027/0.021/0.097/0.031/-0.076

## HONEST READS (depth-bounded, SR-quality-gated capability; NOT mechanism-death)
- The primary verdict is HARD_FAIL because it is gated on the strict highest-entropy FOCUS (op4_d6 at
  smoke; op4_d8 at FULL), which is the single deepest/highest-branching corner where flat ALSO collapses.
  The bands were LOCKED before running; I do NOT move the goalpost. But the strict-FOCUS verdict
  UNDERSELLS the finding, so the capability-frontier is reported regardless.
- The mechanism is REAL and fires with a well-trained SR: FIX-2 probe clears the FULL HP bar at 2/4
  regimes (op2_d6 recovery=0.236, op4_d4 recovery=0.400, both beating flat + random with all honesty
  guards clean), beats the random-waypoint floor DECISIVELY at every regime (op2_d4 0.88 vs 0.37;
  op4_d4 0.67 vs 0.18), and RECOVERS THE TRUE ORACLE WAYPOINTS (exact_match_rate 0.83 at op2_d4, 0.57
  at op4_d4). The SR-reach bisection is genuinely finding real intermediate states when the horizon is
  short enough.
- The bound is DEPTH/ENTROPY-specific: autonomous discovery collapses only at the deepest corner
  (op4_d6, and by extrapolation op4_d8) where the SR-reach signal over the required segments is too
  noisy to place useful waypoints. Undertrained SR (canonical smoke) fires nowhere (0/4); better SR
  (FIX-2) fires at 2/4 with frontier at entropy 8 -> the capability is SR-quality-gated, exactly the
  FIX-2 lever the drill flagged.
- DOMAIN-FIT CONFIRMED (strong, independent): spectral/cluster bottleneck-restriction HURTS vs open at
  EVERY regime (spec-open uniformly negative, up to -0.40 in fix2sr). The substrate's randomly-generated
  operator graphs lack exploitable community/bottleneck structure -- consistent with random-graph theory,
  a clean informative negative on candidates (a)/(c), exactly as the drill predicted (P~0.15-0.20 "helps").
- Machinery is CLEAN: index_artifact_gap ~0.007-0.021 (no structural index leak), anti_tautology_corr
  ~0.00-0.02 (balance score is genuine SR-dynamics, not target-cosine), degenerate_rate ~0.00-0.02 (no
  degeneration to start/goal). The HARD_FAIL is a real bound, not a machinery artifact.

## FULL config (staged; do NOT self-dispatch -- needs origin/main push, route via orchestrator to GPU)
N=8192, seeds [7,17,23,31,41], gamma=0.85, seg_len=2, cand_frac=0.10, grid {n_ops 2,3,4} x {depth 4,6,8}
(V: op2=800, op3=1000, op4=1200), SR_STEPS=8000, SR_BATCH=256, rollout_per_V=50, n_train=300, n_test=240.
EXPECTED_N_UNITS=405 (9 arms x 5 seeds x 9 regimes). Recommended queue: overnight_queue (GPU; regular
remote, NOT once-per-stage cloud). Recommended --timeout: 18000s (5h; expected ~2-3h on GPU; 3 SR
trains/seed x 8000 steps N=8192 + 9-regime x 9-arm grid incl depth-8; per-seed checkpoint/resume
protects partials on timeout-kill). FULL's SR (8000 steps, N=8192) is BETTER than the FIX-2 probe's
(2000, N=2048), so the capability frontier is expected to push HIGHER; the strict FOCUS op4_d8 is a
genuine minority coin-flip (P~0.22), but the canonical entropy-surface + frontier + domain-fit
confirmation are the primary deliverable and land regardless of the strict-FOCUS verdict.
