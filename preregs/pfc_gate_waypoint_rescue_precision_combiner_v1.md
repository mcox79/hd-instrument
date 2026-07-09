# pfc_gate_waypoint_rescue_precision_combiner_v1 -- precision-preserving combiner for the compounding-drift rescue

## Cell
`experiments/exp_pfc_gate_waypoint_rescue_precision_combiner_v1.py`
Parent (verbatim reuse): `experiments/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py` (landed HARD_FAIL_STACKING_REDUNDANT).

## Purpose (the stacked-corrections VET's ENDORSED corrected lever)
The 6th-attempt OR-gate stack HARD_FAILed at FULL: the OR-UNION of the two channels' admission sets
RE-ADMITS candidates that the strict KB channel had correctly filtered, so the balance-argmax within the
union re-picks selector-only candidates and `stacked == selector` exactly, `stacked_over_kb` NEGATIVE in
all 5 regimes. Diagnosis (landed VET): an ADMISSION-PRECISION leak, NOT a channel-strength / coverage
problem. VET's endorsed direction: NOT more channels / not grow-KB-coverage, but a COMBINER THAT
PRESERVES PRECISION. This cell tests whether any of three precision-preserving combiners recovers rescue
where the naive OR-gate could not.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "precision-preserving combiner stacked corrections OR-gate union admission
precision KB channel rescue"` 2026-07-09: top hit `precision` cosine=0.4531 (WordNet dictionary sense of
the word, not a prior cell); no prior precision-preserving-combiner / admission-set-operator arc work at
cosine>=0.30. NOVEL as a mechanism; direct continuation of the pfc_gate waypoint-rescue arc
(kb_grounded_check -> stacked_corrections -> this). Not a rediscovery.

## Arms (17; paired -- share E/W_ops/M/M_long/M_rev/R_*/reach_cum/selector-model + SAME test chains per
##   (regime,seed); everything except the WAYPOINT SOURCE is identical across arms)
- flat_gonogo, oracle_exec (rail >=0.90), hier_oracle (given-decomp ceiling), hier_shuffled (neg control)
- wp_bisect_open / _verify / _coarse2fine / _combo / _replay_generate_select  (legacy failing baselines)
- wp_kb_grounded_gate         = KB-ALONE, the single-best channel the combiner must ADD over (reference)
- wp_calibrated_selector_gate = channel B alone (cross-fit calibrated correctness-selector)
- wp_stacked_kb_plus_selector = B0 OR-gate union -- the CONFIRMED NEGATIVE / must-stay-dilutive control
- wp_and_gate                 = C1 INTERSECTION (admit iff BOTH channels confirm; tightest precision)
- wp_kbpriority_union         = C2 CONFIDENCE-WEIGHTED / KB-PRIORITY union (defer to KB; selector fills
                                only KB's coverage holes; never dilutes a KB-confirmed pick)
- wp_calibrated_gate_combiner = C3 CORRECTNESS-CALIBRATED gate over the union (admit (KB|SEL) AND
                                calibrated P(correct) >= tau_hi = 85th-pctl, stricter than the 70th-pctl
                                selector tau; filters the union's re-admitted low-precision candidates)
- wp_random_state (floor), wp_index_midpoint (structural-artifact guard)

## Discriminator (FOCUS = op4_V1200_d8, chain_steps=3; best_combiner = max over C1/C2/C3, NOT max-over-all)
- recovery(a) = (a - flat) / (hier_oracle - flat)  = fraction of oracle-decomposition benefit recovered
- combiner_over_kb(cX) = recovery(cX) - recovery(kb_alone)
- best_combiner_over_kb = max over {C1, C2, C3} of combiner_over_kb  <-- HEADLINE margin over KB-alone
- or_gate_over_kb = recovery(B0 OR-gate) - recovery(kb_alone)  <-- must stay <= 0 (confirmed-negative)
- paired sign-test = the WINNING combiner vs KB-alone (does it genuinely ADD over the single best channel)

## Bands (BOTH pre-registered; strictly-above-floor per META_RULE_L)
### HARD_PASS (a precision-preserving combiner recovers rescue where the OR-gate could not)
`best_combiner_over_kb >= 0.05` (HP_COMBINER_OVER_KB_MIN; pre-registered depth margin over KB-alone)
AND `recovery(best_combiner) >= 0.35` (HP_RECOVERY_RATIO_FLOOR; materially above KB-alone's landed 0.2444)
AND `or_gate_over_kb <= 0.0` (OR_GATE_DILUTIVE_MAX; B0 stays dilutive = the fair-contrast control reproduced)
AND `flatness_ratio >= 0.50` (recovery(best,d8)/recovery(best,d4); stays flat, not accelerating collapse)
AND kb_confirm non-vacuous (0.05 < kb_confirm_mean < 0.95) AND selector non-vacuous (0.05 < acc_frac < 0.98)
AND lift_flat > 0.05 AND lift_random > 0.10 AND index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85
AND degenerate_rate < 0.10 AND sign_p(winner vs KB) < 0.05 AND cv < 0.15 (FULL only) AND no AF collision
AND oracle_exec >= 0.90 AND headroom_exec >= 0.10 AND headroom_decomp >= 0.10.
=> the OR-gate's failure was an ADMISSION-SET-OPERATOR artifact specifically; a precision-preserving
   combination rule recovers real autonomous-decomposition capability the naive union diluted away.

### HARD_FAIL (single-best-channel is FINAL)
`best_combiner_over_kb <= 0.02` (HF_COMBINER_OVER_KB_CEIL) at FOCUS, with B0 dilutive.
=> NO combiner (intersection, KB-priority, calibrated-gate) beats KB-alone => the second channel is too
   weak to help under ANY combination rule => the single-best-channel conclusion is FINAL, a clean
   scope-bound (the strongest closure of this arc to date). Redirect to bounded-depth-budget framing.

### MIDDLE_BAND (real but partial / a guard trips)
best_combiner_over_kb in (0.02, 0.05) => MIDDLE_BAND_PARTIAL_COMBINER_OVER_KB; OR recovery < 0.35;
OR flatness in trouble; OR selector/kb vacuous; OR sign-test NS; OR CV too high (FULL).

### INCONCLUSIVE
- `or_gate_over_kb > 0` at FOCUS => INCONCLUSIVE_OR_GATE_NOT_DILUTIVE (the confirmed-negative control did
  NOT reproduce -> the combiner-vs-OR contrast is not fair; re-anchor the negative before tiering).
- index-order leak; no discriminating regime.

## SCHEMA-VET pre-dispatch fields
- cardinality_ok: EXPECTED_N_UNITS = n_arms(17) * n_seeds * n_regimes (FULL = 17*5*5 = 425); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if completed < expected.
- arms_differ_verified: op_trace hash-check per seed (winning combiner vs verify/open/flat/random; hier_oracle
  vs hier_shuffled); AF-collision forces not-HP.
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json + start-marker + partials).
- except SystemExit: raise BEFORE except Exception (no BaseException) -- present in main + selftest.
- crlb_n/a: accuracy-closure discriminator; reachability by feasibility -- hier_oracle=0.906 at op4_d8
  proves the given-decomposition envelope; KB-alone collapses to 0.2444; the open question is how much of
  that headroom a PRECISION-PRESERVING combiner recovers over KB-alone. HP margin (>=0.05 over KB) sits
  inside the envelope.
- baseline_in_band (META_RULE_AG): the KEY baseline is KB-alone (recovery 0.2655 at smoke corner, NOT
  saturated, NOT floored); oracle_exec >= 0.90 rail + headroom >= 0.10 gates ensure measurable room.
- discriminator survives scale: smoke = op4 x {d4,d6,d8} at V=300 N=2048 (BLUNTER reach than FULL N=8192;
  KB reachability is EXACT/N-independent, only execution blunts, so a positive smoke best_combiner_over_kb
  is a LOWER bound on FULL -- option C directional preview). Smoke MUST show B0 OR-gate dilutive
  (or_gate_over_kb <= 0) at the corner (the confirmed-negative control) AND arms differ AND KB non-vacuous.
- calibration_check: adaptive_with_discriminator_gate (KB confirm = EXACT raw-graph reachability, no tunable
  threshold; selector tau = 70th-pctl of fold-B calibrated scores; C3 tau_hi = 85th-pctl; discriminator =
  best_combiner_over_kb + flatness + OR-dilutive control, none tuned-for-PASS).
- HP_SCOPE: HP margin gates apply to the winning combiner (C1/C2/C3) vs KB-alone at FOCUS; oracle_rail(>=0.90)
  to oracle_exec; recovery references hier_oracle; index guard to wp_index vs wp_random; OR-dilutive control
  to wp_stacked_kb_plus_selector vs KB-alone.
- effective_vs_nominal_parameter_audit: no swept parameter (fixed regime grid); ALIGNED.
- discriminating_fraction: 3/5 FULL regimes (d6/d8 x op4, op3_d8) predicted in the discriminating band
  (KB-alone collapse gives room to add); >= 0.30.
- composition_edges: KB-confirm mask (reach_cum) -> masked bisection argmax = SHAPE_MATCH; selector accept
  mask (calibrated P) -> masked bisection argmax = SHAPE_MATCH; combiners are boolean-mask set operators over
  the two masks (AND / KB-priority conditional / calibrated-AND) -> SHAPE_MATCH.
- positive_control_arms: wp_kb_grounded_gate reproduces the parent KB-alone (same E/M/R/reach_cum by
  construction); wp_stacked_kb_plus_selector reproduces the parent OR-gate (must stay dilutive) AT THE TEST
  REGIME. flat/oracle_exec/hier_oracle reproduce ancestors by construction.
- functional_requirements: (1) preserve KB's admission precision -> C1 intersection / C2 KB-priority never
  admit a selector-only candidate over a KB-confirmed one; (2) recover recall in KB's coverage holes -> C2
  gap-fill + C3 calibrated union; (3) filter re-admitted low-precision candidates -> C3 calibrated gate.

## Compute architecture
(a) batched-GPU. SR-TD training (M/M_long/M_rev), operator application, cleanup, reach, R build, reach_cum
boolean matrix powers, selector logistic fit, masked bisection + confirm-fn masks = batched matmuls /
gathers / argmax on cuda-if-available. Chains batched; within-chain hops sequential (genuine dependency).
Storage: sharded (each operator its own W; M/M_long/M_rev learned operators; R_* derived; reach_cum RAW-graph
boolean reachability; selector = raw-graph features only). No bundled store. FULL prefers overnight_queue
(GPU). Extra cost vs the stacked parent: 2 more masked-bisection passes (AND + calibrated-gate) + the
per-combiner paired counts; linear, no quadratic blowup.

progress_logging: print_flush_true (flush=True on every progress line + per (seed,V,n_ops) heartbeat; FULL
timeout_s >= 1800).

## Self-test (formula correctness; run BEFORE dispatch)
`.venv/Scripts/python.exe experiments/exp_pfc_gate_waypoint_rescue_precision_combiner_v1.py --self-test`
ST1-ST13 all PASS incl. ST9L (AND=kb&sel; KB-priority=where(kb,kb,kb|sel); calibrated-gate=union&(P>=tau_hi);
subset-ordering AND<=KB-priority) and ST13 precision-combiner verdict wiring (HARD_PASS combiner-beats-kb +
OR-dilutive; HARD_FAIL single-best-channel-final; INCONCLUSIVE or-not-dilutive / index-leak / no-regime;
MIDDLE partial-over-kb / selector-vacuous / recovery-below-35).
