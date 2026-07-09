# Pre-registration: pfc_gate_waypoint_rescue_kb_grounded_check_v1

Date: 2026-07-09
Author: exp_dev (cell author)
Cell: `experiments/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1.py`
Design source: `notes/research_compounding_error_bound_5x_drill_new_mechanism_class_cross_domain_2026-07-09.md`
Ancestors (verbatim primitive reuse + already-measured control arms):
- `experiments/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1.py` (PARENT; FULL landed
  HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL; source of all reused primitives + control arms)
- `experiments/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py` (grandparent; FULL HARD_FAIL)
- `experiments/exp_community_routed_glassbox_reasoning_scale_v1.py` (sibling HARD_PASS this session:
  ARM_C_FRESH slope=0.0010 vs COMPOUND slope=0.0976 = same structural principle, already certified)

## Question
BARRIER #2 (long reasoning chains drift / compounding error). FOUR autonomous-decomposition rescue
variants (verify-gate, coarse2fine, replay-bidirectional, lookahead-bisection) have now landed
HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL at the identical corner op4_V1200_d8. The 5x cross-domain drill's
diagnosis: all four share ONE precise defect -- the correction signal at each hop was recomputed FROM THE
SAME NOISY DERIVED ESTIMATOR (SR reach matrix M/R) being corrected, never from anything outside it. Five
fields converge (DAgger external oracle; DNA-polymerase kinetic proofreading = physically separate
exonuclease; Kalman: innovation must be ORTHOGONAL to the state estimate for bounded error covariance;
RG/info-bottleneck; pop-genetics): bound drift with an INFORMATIONALLY-INDEPENDENT correction channel.
Does an EXOGENOUS, KB-GROUNDED per-hop check -- verifying each waypoint pick against the RAW ingested KB
edge table directly, with ZERO shared parameters with the SR estimator -- recover real autonomous-
decomposition capability where four self-derived / weakly-independent variants could not?

## Mechanism under test (rank 1 in the drill; NEW class; NOT autonomous decomposition)
EXOGENOUS KB-GROUNDED CHECK (kinetic-proofreading checkpoint):
(1) Build, once per (V,n_ops) group, RAW-KB reachability-within-<=k-hops boolean matrices reach_cum[k]
    DIRECTLY from the raw edge table (per_op / adjacency = the substrate's raw ConceptNet-style edges).
    reach_cum[k][a,c]=True iff an ACTUAL path of length in [1,k] exists a->c in the union multigraph.
    ZERO shared parameters / ZERO shared training with M/R (TD-trained on random walks). Exogenous
    ground-truth channel = the raw graph itself, not a derived statistic of it.
(2) At each bisection hop (pos=(j+1)*seg_len, anchor=prev discovered boundary, span rem=depth-pos to
    goal): compute the SAME open R-balance min(R[anchor,c],R[c,goal]) but MASK to only KB-CONFIRMED
    candidates: reach_cum[seg_len][anchor,c] AND reach_cum[rem][c,goal]. Re-pick argmax WITHIN the
    confirmed subset.
(3) Empty-confirmed rows RESET FRESH: recompute the confirmed set re-anchored at the immutable START
    (span=pos), never carrying the unconfirmed intermediate anchor forward (ARM_C_FRESH-style). Still-
    empty rows fall back to the open argmax (counted as unconfirmed).
(4) COMMIT the KB-confirmed pick. Execution loop run_hier_arm_wp identical to all ancestors for every arm.
CITED@Hopfield 1974 / Ninio 1975 (kinetic proofreading); CITED@Ross-Bagnell 2010 (DAgger O(T^2)->O(T));
CITED@Kalman innovation-orthogonality / algebraic-Riccati observability.

## MANDATORY INDEPENDENCE SCREEN (this drill's load-bearing pre-registered claim)
Per (chain,hop) unit collect two scalars from DISJOINT sources:
- kb_confirm_signal = whether R's OPEN argmax pick is KB-reachability-confirmed (raw graph)
- m_error = SR estimator per-hop reach error to the TRUE oracle boundary = 1 - unit(R[anchor,true_bnd])
  (from R + oracle ONLY; disjoint from the raw-graph confirm computation)
independence_corr = corr(kb_confirm_signal, m_error) over all units. Predict |corr| ~ 0 (Kalman
innovation orthogonality). Reported REGARDLESS and GATED (see bands). If |corr| is high the KB signal is
NOT independent of the estimator's own error and will compound like the four prior variants.
Non-vacuity guard: kb_confirm_mean must be in (0.05, 0.95) (some open picks confirmed, some not) or the
screen is uninformative and the gate does nothing distinct from open.

## Arms (12; paired)
flat_gonogo (FLOOR), oracle_exec (rail/ceiling; POSITIVE CONTROL must clear ~0.90), hier_oracle (given-
decomp ceiling; positive control), hier_shuffled (neg control), wp_bisect_open (parent failing baseline),
wp_bisect_verify (KEY comparator: SELF-DERIVED-correction MUST-FAIL control, ~0.10 wall reproducer),
wp_bisect_coarse2fine + wp_bisect_combo (already-failed self-ref controls, re-run for continuity),
wp_replay_generate_select (already-failed independent-ish control, re-run VERBATIM), wp_kb_grounded_gate
(NEW mechanism under test), wp_random_state (autonomous floor), wp_index_midpoint (structural guard).

best_rescue = wp_kb_grounded_gate (FIXED, not a max-over-arms). KEY comparator = wp_bisect_verify.

## FOCUS regime
op4_V1200_d8 (chain_steps=3), the exact 4x HARD_FAIL corner. Flatness reference = op4_V1200_d4
(chain_steps=1). MEASURED PARENT @data/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1/metrics.json:
op4_V1200_d8 flat=0.081 oracle_exec=0.918 hier_oracle=0.906 wp_bisect_open=0.097 wp_bisect_verify=0.096
recovery_verify=0.0182 recovery_replay=0.0283 delta=0.0101 (HARD_FAIL bound-real).

## Bands (LOCKED before running; envelope-fail-bands)
recovery(a) = (a - flat) / (hier_oracle - flat).  delta_recovery = recovery(kb) - recovery(verify)
[KEY, vs the SELF-DERIVED control].  flatness_ratio = recovery(kb, FOCUS d8) / recovery(kb, d4).
independence_corr = corr(kb_confirm_signal, m_error).

HARD_PASS (exogenous-grounding hypothesis confirmed; 5th attempt succeeds for a structurally sound reason):
- recovery(kb) >= 0.20 AND
- delta_recovery(vs verify) >= 0.15 AND
- flatness_ratio >= 0.50 AND
- |independence_corr| <= 0.15 AND kb_confirm non-vacuous (0.05 < kb_confirm_mean < 0.95) AND
  not independence_degenerate AND
- lift_flat > 0.05 AND lift_random > 0.10 AND
- index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85 AND degenerate_rate < 0.10 AND
- sign_p(kb vs verify) < 0.05 AND cv(kb) < 0.15 (FULL only) AND
- oracle_exec >= 0.90 AND headroom_exec >= 0.10 AND headroom_decomp >= 0.10.
=> The compounding-error bound was an artifact of SELF-REFERENTIAL correction specifically; a genuinely
exogenous, zero-shared-param ground-truth channel (raw KB edge table) recovers real capability where four
prior self-derived / weakly-independent variants could not.
Binding constraint (given parent shallow recovery ~0.70): recovery(kb) at d8 >= ~0.35.

HARD_FAIL (strongest possible closure to date):
- delta_recovery <= 0.05 (recovery(kb) <= recovery_verify + 0.05, ~0.068 at FOCUS: no material lift over
  the self-derived control despite a rigorously exogenous channel) -- HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL; OR
- |independence_corr| > 0.40 (the KB signal is NOT independent after all -- e.g. R's error tracks KB
  sparsity, contaminating the "exogenous" channel; premise void) -- HARD_FAIL_KB_SIGNAL_NOT_INDEPENDENT; OR
- flatness_ratio < 0.20 (accelerating, not bounded, collapse) -- HARD_FAIL_ACCELERATING_COLLAPSE.
=> Accept the bound as fundamental for autonomous no-oracle waypoint discovery at chain_steps>=3,
entropy=16; redirect to bounded-depth-budget framing.

MIDDLE_BAND: delta_recovery in [0.05, 0.15) OR flatness_ratio in [0.20, 0.50) OR |independence_corr| in
(0.15, 0.40] (partial independence) OR kb_confirm vacuous (screen uninformative) OR (delta>=0.15 &
flatness>=0.5 but recovery(kb)<0.20) OR any honesty guard fails while margins pass. Sub-reasons emitted:
PARTIAL_RESCUE_DELTA_BELOW_15 / FLATNESS_BELOW_50 / RECOVERY_BELOW_20 / PARTIAL_INDEPENDENCE /
KB_CONFIRM_VACUOUS / DEGENERATE_GUARD / ANTI_TAUTOLOGY_GUARD / INDEX_ARTIFACT_GUARD / LIFT_RANDOM_BELOW /
SIGN_TEST_NS / CV_TOO_HIGH / SUBTHRESHOLD.

INCONCLUSIVE: no discriminating regime (oracle rail / headroom gates fail) OR index_artifact_gap > 0.10
with idx_sign_p < 0.05.

Honest either way: if KB-grounding does NOT beat the bound, that is a real, informative NEGATIVE (the drift
bound survives a rigorously exogenous channel = strongest closure yet, and the honest read shifts to
"insufficient KB coverage at this entropy/depth OR a genuine information-theoretic floor"). P_deflated
~0.20 for MIDDLE-or-better, ~0.15-0.18 full HARD_PASS (5th attempt on the same wall; structurally distinct).

## SCHEMA-VET mandatory fields
cardinality_ok: true  (EXPECTED_N_UNITS = n_arms(12) * n_seeds * n_regimes; verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if completed < expected)

sweep_alignment_verdict: ALIGNED
  swept_params: dd (chain depth) in {4,6,8} at op4; secondary n_ops/V regimes for entropy dissociation.
  effective_params_per_primitive: recovery/delta_recovery/flatness are measured on the SAME dd the
  execution loop experiences; chain_steps = n_boundaries(dd,SEG_LEN)-1 is the effective decision-count.
  KB reach_cum[k] is EXACT (N-independent), so the independence screen and gate are not blunted by N.
  No partition-routing indirection.

discriminating_fraction: >= 0.5 (FULL grid op4 {d4,d6,d8} + op3_d8 + op2_d8). d4 = open/verify already
  recover (~0.70, shallow already solved, NOT saturated at 1.0); d6/d8 = collapse corners (recovery
  ~0.0-0.1). MEASURED parent: d4 recovery_verify~0.70, d8 recovery_verify=0.018 -- both in measurable
  band. >= 3/5 regimes land in a discriminating band for the kb-vs-verify contrast.

composition_edges (signal_shape_compatibility_audit): SHAPE_MATCH throughout.
  - raw per_op edges -> build_kb_reach_cum: boolean [V,V] adjacency + float matmul powers. MATCH.
  - reach_cum[k] masks -> R-balance argmax: elementwise boolean mask on [n_chains,V] balance. MATCH.
  - kb-selected boundaries -> _boundaries_to_hops -> run_hier_arm_wp: identical schedule shape to every
    other wp_* arm (VERBATIM ancestor path). MATCH.

positive_control_arms (Gate D; composing prior chain-grade primitives):
  - arm: wp_bisect_open_REPRODUCE_AT_TEST_REGIME + wp_bisect_verify_REPRODUCE
    primitive: parent open bisection + self-referential verify-gate (SR reach + balance argmax exec loop)
    cited_prior_atom: exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1 op4_V1200_d8
    cited_prior_metric: wp_bisect_open=0.097, wp_bisect_verify=0.096, hier_oracle=0.906, oracle_exec=0.918
    cited_prior_regime: {N:8192, V:1200, op4, dd8, seeds 7/17/23/31/41}
    test_regime: IDENTICAL (this cell trains M/R with the SAME sr_gen seed formula -> reproduces
      M/R/wp_bisect_open/flat/hier_oracle/verify BY CONSTRUCTION). tolerance: 0.10.
    if_outside_tolerance: positive-control drift flag (downstream kb comparison suspect).
    regime_extension_audit: SHAPE_MATCH (same synthetic-bipolar regime, same primitives, additive only).
  - hier_oracle POSITIVE CONTROL must clear oracle_rail >= 0.90 (task solvable given decomposition).

functional_requirements (Gate E):
  - FR1 "an exogenous ground-truth channel with zero shared params with the estimator" -> build_kb_reach_cum
    on RAW per_op edges (NEW; raw-graph transitive closure).
  - FR2 "verify each candidate against that channel at inference time" -> _discover_kb_grounded_boundaries
    KB-confirm mask on the R-balance argmax (NEW).
  - FR3 "never carry an unconfirmed intermediate forward" -> fresh-reset re-anchored at immutable START
    (NEW; ARM_C_FRESH principle).
  - FR4 "measure the channel's independence from the estimator's error" -> kb_independence_screen (NEW).
  - FR5 "execute the committed decomposition" -> run_hier_arm_wp (VERBATIM ancestor; certified CG loop).
  - FR6 "denoise each candidate's constituent vectors" -> cleanup_batched inside run_hier_arm_wp (VERBATIM).

final_metrics_atomicity: tmp_replace (os.replace on metrics.json; _atomic_write_metrics).
crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor. Reachability by
  feasibility: parent hier_oracle=0.906 at op4_d8 proves the given-decomposition envelope; open+verify
  collapse to ~flat -> the open question is how much of the 0.906 headroom the EXOGENOUS KB check recovers
  over verify's 0.018. HP bar (recovery>=0.20 AND flatness>=0.5, binding ~0.35 absolute) sits inside the
  0.906 envelope. discriminator_reachability: true.
baseline_in_band: true. KEY baseline = wp_bisect_verify, collapsed to ~flat at FOCUS (0.096 vs flat 0.081;
  recovery 0.018). Discriminator = kb-vs-verify, both measurable. oracle_exec >= 0.90 rail + headroom >=
  0.10 gates guarantee room to recover; d4 (verify recovers ~0.70) proves baseline NOT saturated.
discriminator_survives_scale: option C directional preview. Smoke holds op4 x {d4,d6,d8} at V=300, N=2048
  (BLUNTER EXECUTION than FULL N=8192; KB reachability is EXACT/N-independent so only execution blunts ->
  a POSITIVE kb-minus-verify at smoke is a LOWER bound on FULL). Smoke that shows open+verify collapse +
  oracle success + non-vacuous kb_confirm variance + any positive kb-minus-verify + kb trace differs gates
  the GPU FULL. HARD_PASS at FULL is the canonical verdict (not smoke).
HP_SCOPE:
  wp_kb_grounded_gate: [recovery>=0.20, delta_recovery>=0.15, flatness>=0.5, |indep_corr|<=0.15,
    kb non-vacuous, lift_flat, lift_random, sign_p, cv, guards]
  oracle_exec: [oracle_rail >= 0.90]
  hier_oracle: [headroom_decomp reference]
  wp_index_midpoint vs wp_random_state: [index-order-leak guard]
  independence screen: [|corr(kb_confirm, m_error)| gate]
  (bare-baseline / neg-control arms do NOT inherit the chain-grade HP gates.)

arms_differ_verified: true (smoke gate; kb op-trace hash != verify/open/flat/random per seed; hier_oracle
  != hier_shuffled). AF collision -> hp_ok=False.
calibration_check: adaptive_with_discriminator_gate. KB confirm = EXACT raw-graph reachability (NO tunable
  threshold); verify-gate tau = 70th-pctl of R off-diagonal on the control arm; N_CAND=5 fixed (replay
  control). Discriminator = delta-over-verify + flatness + |indep_corr|, NOT tuned-for-PASS.

## Defensive error-checking (MANDATORY)
cell_chunked: false  (multi-seed within one cell via _seed_checkpoint resumable_seeds/write_partial_key;
  per-seed crash sets fatal-flag + writes failure_class partial + demotes HP->MIDDLE; restartable).
start_marker_written: true  (_write_start_marker at main() entry).
crash_diagnostic_present: true  (except SystemExit: raise BEFORE except Exception; _write_crash_metrics
  writes CELL_CRASHED + traceback atomically). No bare except / BaseException in main flow (grep-verified).
heartbeat_present: true  (_heartbeat per seed; per (seed,V,n_ops) SR-diag print).
defensive_error_checking: passed_all_4_patterns.
progress_logging: print_flush_true  (flush=True on every progress line; per-seed + per-regime).

## Compute architecture
(a) batched-GPU. SR-TD training (M @0.85, M_long @0.95, M_rev @0.85 on reversed transitions), operator
application, cleanup, reach, R build, bisection + perturbed candidate generation + bidirectional scoring
+ KB reach_cum boolean matrix powers = batched matmuls / gathers / argmax on cuda-if-available. Chains
batched; within-chain hops sequential (genuine dependency). M/M_long/M_rev/R_*/reach_cum computed once per
(V,n_ops) group and shared across depths. Storage strategy: sharded (each operator its own W; M/M_long/
M_rev learned operators; R_* derived reach matrices; reach_cum raw-graph boolean reachability powers). No
bundled store. FULL strongly prefers overnight_queue (GPU). Extra cost vs replay ancestor: reach_cum =
depth boolean VxV matmuls (~8 x 1200^2, trivial) once per group + one masked re-bisection + one
independence-screen pass; linear, no quadratic blowup.

## Config
SMOKE: N=2048, seeds [7,17,23], op4 {d4,d6,d8} V=300, SR_STEPS=2500, local_cpu (smoke only).
FULL:  N=8192, seeds [7,17,23,31,41], regimes op4 {d4,d6,d8} V=1200 + op3_d8 V=1000 + op2_d8 V=800,
  SR_STEPS=8000. Route: overnight_queue (GPU) OR remote_cpu_queue.

## MEASURED/HYPOTHESIZED/THEORETICAL/CITED tags
- recovery_verify FOCUS op4_V1200_d8 = 0.0182 MEASURED@data/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1/metrics.json
- recovery_replay FOCUS op4_V1200_d8 = 0.0283 MEASURED@ (same file)
- hier_oracle op4_V1200_d8 = 0.906, oracle_exec = 0.918 MEASURED@ (same file)
- community-routed ARM_C_FRESH slope=0.0010 vs COMPOUND slope=0.0976 MEASURED@data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json
- HARD_PASS binding constraint recovery(kb,d8) >= ~0.35 THEORETICAL@(flatness>=0.5 * shallow~0.70)
- |independence_corr| ~ 0 THEORETICAL@Kalman-innovation-orthogonality
- P_deflated MIDDLE-or-better ~0.20, full HP ~0.15-0.18 HYPOTHESIZED@this prereg (drill (c))
