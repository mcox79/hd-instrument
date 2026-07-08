# Pre-registration: substrate_acc_evc_adaptive_halting_v1

**Date:** 2026-07-08
**Author:** exp_dev (Opus 4.8 1M, agent-spawn)
**Cell:** experiments/exp_substrate_acc_evc_adaptive_halting_v1.py
**Anchor:** substrate_acc_evc_adaptive_halting_v1
**Drill source:** notes/research_neuromodulatory_self_manager_controller_2026-07-08.md sec5 (self-manager channel #1: ACC/EVC adaptive halting -- cheapest/most de-risked dial). Division-of-labor context: notes/research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md.
**Reuses (unchanged):** experiments/exp_pfc_gate_cfrpe_trained_v2.py (Go/NoGo value-gate actor + cfrpe RPE SR). The value-gate's frozen hop-depth knob is the thing modulated.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory)
`bash tools/substrate_query.sh "adaptive halting marginal value cost per reasoning depth step early exit ACC EVC controller"` -> top hits (cosine>0.30: NONE; closest below):
1. `pfc_controller_depth_adaptive_argmax_v3` (cosine 0.287) -- **read in full.** This is adaptive **TEMPERATURE** (softmax sharpness T(k) per hop) at a **FIXED full depth** (never varies the hop budget). Distinct mechanism. Its FULL never landed (metrics.json = SELFTEST_OK only, 2026-06-27). My cell is adaptive **HALTING** (variable per-item hop budget via an EVC marginal-cost rule); orthogonal knob.
2. `research_drill_2x_pfc_v2_depth12_cv_collapse_2026-06-27.md` (cosine 0.273) -- establishes the depth-decay law P(chain)=(1-eps)^k (eps~0.14/hop). This is the physics my heterogeneous-length regime exploits: over-running past a reached goal drifts away (the drift the halting reflex fixes). Built ON, not duped.
3-5. FrameNet/WordNet "Reasoning" entries (generic; not substrate work).
**Verdict: genuinely novel** relative to the corpus. It is NOT a rediscovery of the temperature-schedule cell (that dial = per-hop mixing sharpness at fixed depth; this dial = when to STOP). The 06-23 neuromodulator drills (dual-trace / LR modulation) and the 07-04 coarse-vs-fine metric drill are unrelated channels.

## Hypothesis
The value-gate runs a FIXED number of hops DD (hand-set, frozen). Under a heterogeneous per-instance difficulty distribution, a fixed depth OVER-computes easy items (drifting past an already-reached goal, since the actor has no STAY action) and UNDER-computes hard items. Layering a content-free scalar ACC/EVC controller -- a per-item LOCAL reflex "halt once arrival-confidence a_t=cos(state,goal) >= theta" whose single aggregate knob theta is tuned on TRAIN by accuracy-per-compute (the EVC value-per-effort objective) then FROZEN -- will match-or-beat fixed-DD task quality at LOWER average compute (reallocation, not trimming). Controls (RANDOM_DEPTH, SCRAMBLED_HALT) must confirm the arrival SIGNAL, not mere depth variance, drives the gain.

## Contract (envelope-fail-bands)
accpc == accuracy / mean_hops_used (accuracy-per-compute). Discriminators computed on TEST, aggregated (mean) over seeds.

- **HARD_PASS**: adaptive_vs_fixed_rel >= 0.15 AND adaptive_vs_random_rel >= 0.10 AND scramble_rel_gap >= 0.15 AND realloc_corr >= 0.30 AND (realloc_corr - scramble_corr) >= 0.20 AND hop_spread >= 0.5 AND acc(ADAPTIVE) >= acc(FIXED_DD) - 0.02 AND reach_rank > 0.30 AND all guards.
- **MIDDLE_BAND**: adaptive_vs_fixed_rel in [0.05,0.15) OR (beats fixed >=0.15 but adaptive_vs_random_rel < 0.10) OR scramble_rel_gap in [0.05,0.15).
- **HARD_FAIL_ADDS_NOTHING**: |adaptive_vs_fixed_rel| < 0.05 (dial adds nothing over the frozen value).
- **HARD_FAIL_SIGNAL_NOT_LOADBEARING**: accpc(ADAPTIVE) <= accpc(RANDOM_DEPTH) (depth variance alone matched it).
- **HARD_FAIL_COLLAPSED_TO_FIXED**: hop_spread < 0.5 (adaptive matched fixed only by collapsing to a single depth -- no reallocation). This is the task-specified HARD-FAIL: "matches fixed-DD only by collapsing to it."
- **INCONCLUSIVE_TAUTOLOGICAL_METRIC**: scramble_rel_gap < 0.05 (scramble did NOT collapse -> discriminator analytically pinned; reported inconclusive, NOT a clean negative).
- **INCONCLUSIVE_NAV_BROKEN**: acc(ORACLE_HALT) < 0.55 (routing broken; halting untestable).
- **INCONCLUSIVE_NO_HALTING_PRESSURE**: accpc(ORACLE_HALT) <= accpc(FIXED_DD)*1.10 (perfect halting can't beat fixed -> corpus does not force halting; regime miss).
- **INCONCLUSIVE_BASELINE_OOB**: FIXED_DD acc outside (0.05,0.95).
- **INCONCLUSIVE_ORACLE_REPRO_MISMATCH**: FIXED_DD acc on L==FROZEN_DD subset outside [0.35,0.90] (Gate D reproduce band, cfrpe v2 V1200_d4 gonogo=0.653).

## Arms (6; paired; differ ONLY by halt policy)
FIXED_DD (baseline, frozen value) | FIXED_DD_CEIL (fixed-high diagnostic) | ADAPTIVE_EVC (mechanism) | RANDOM_DEPTH (variance control) | SCRAMBLED_HALT (telemetry-sensitivity control) | ORACLE_HALT (perfect-halting ceiling / closure denominator / nav rail).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS) (FULL 5x6=30; smoke 2x6=12; selftest 1x6=6). Verdict counts completed (seed x arm).
- arms_differ_verified: true (SHA256 of per-arm (correct,hops_used)). arms_differ_exempted: [(ADAPTIVE_EVC, ORACLE_HALT)] -- clean-state arrival detection approximates the ground-truth arrival oracle; near-identity is the success signal not a bug (distinct code paths cos-threshold vs node-identity). Load-bearing contrast set {FIXED_DD, FIXED_DD_CEIL, ADAPTIVE_EVC, RANDOM_DEPTH, SCRAMBLED_HALT} must all differ.
- final_metrics_atomicity: tmp_replace.
- except-ordering: SystemExit/KeyboardInterrupt re-raised before `except Exception`; no BaseException. (grep gate: clean.)
- crlb_n/a: accuracy-per-compute gap; no single closed-form noise floor. Reachability by feasibility -- cfrpe v2 MEASURED gonogo=0.653 at V1200_d4 + reach_rank>1/n_ops => value-gate routes through the goal often => arrival-halting has signal.
- discriminator_reachability: true (selftest MEASURED adaptive_vs_fixed_rel=+3.2, scramble_rel_gap=0.73, corr[A=1.00 S=-0.13] -- all HP gates cleared with wide margin at reduced scale).
- baseline_in_band: FIXED_DD acc guarded to (0.05,0.95); selftest MEASURED FIXED=0.211/0.244 (in band).
- calibration_check: adaptive_with_discriminator_gate -- theta* tuned on TRAIN by acc-per-compute (EVC objective); discriminator still fires (scramble collapses + random beaten); theta*, theta->{acc,mean_hops} curve, both correlations logged.
- discriminator survives scale: smoke holds N/V==FULL (6.83) + SR trained to near-FULL informativeness (option C preview). Guards (nav rail, baseline, pressure, repro) are scale-checked in every run.
- HP_SCOPE: relative-gates -> ADAPTIVE_EVC vs {FIXED_DD, RANDOM_DEPTH, SCRAMBLED_HALT}. ORACLE_HALT -> nav rail + closure/pressure denominator only. FIXED_DD -> baseline-in-band + Gate-D reproduce. FIXED_DD_CEIL -> no gate (diagnostic).

### §15 composition/sweep gates
- sweep_alignment_verdict: ALIGNED. Not a nominal-vs-effective parameter sweep; the cardinality axis is (seed x arm). theta is an internally-tuned scalar (not a reported sweep axis); L is a corpus-heterogeneity axis, reported via per-L accuracy.
- discriminating_fraction: predicted per-arm acc -- FIXED~0.20-0.45, ADAPTIVE~0.85-0.93, RANDOM~0.25, SCRAMBLED~0.30, ORACLE~0.85-0.93; >=5/6 in (0.10,0.95). MEASURED@selftest matches. >= 0.30. PASS.
- composition_edges: halting reflex reads a_t=cos(state,goal) (goal_sim), a scalar already produced by the actor's own cleanup; SHAPE_MATCH (scalar-in). No new primitive.
- positive_control_arms: ORACLE_HALT reproduces value-gate nav at perfect arrival; FIXED_DD@(L==FROZEN_DD) reproduces cfrpe gonogo@dDD in the band [0.35,0.90] (Gate D, tolerance widened +/-0.20 for heterogeneous corpus). reach_rank probe (reach informative > 1/n_ops).
- functional_requirements: (1) "spend more depth only where marginal value justifies it" -> per-item halt reflex on arrival-confidence (LOCAL, parameter-free). (2) "set the halting budget from an aggregate marginal-value/cost stat" -> theta* = argmax_train accuracy-per-compute (scalar controller; NO per-item map). (3) "prove the signal, not variance, drives it" -> RANDOM_DEPTH + SCRAMBLED_HALT controls. (4) "reallocate, not just trim" -> hop_spread>0 + realloc_corr(adaptive,oracle-arrival) high while scramble ~0.

### §13 defensive error-checking
- cell_chunked: false (multi-seed loop with resumable_seeds + write_partial_key per seed -> runner death resumes remaining seeds; per-seed fatal-flag demotes HP).
- start_marker_written: true. crash_diagnostic_present: true (Exception->CELL_CRASHED atomic metrics + traceback). heartbeat_present: true (_heartbeat.jsonl per seed). defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + flush=True on every per-seed/arm line; FULL timeout_s>=1800).

## Compute architecture
(a) batched-GPU. SR-TD training, operator application, cleanup, reach, goal_sim are batched matmuls on cuda-if-available; the per-item halt mask is a cheap elementwise op inside the batched hop loop (within-chain hops are a genuine sequential dependency). SR trained ONCE per seed. Storage: sharded (each operator its own W; M a learned value operator); no composition store. FULL requires cuda (raises otherwise) -> overnight_queue.

## Regime
- FROZEN_DD=4; L_SUPPORT=[2,3,4,5,6] (mean-centered on FROZEN_DD so the frozen value is the mean-optimal fixed choice -- strongest baseline); D_MAX=6, D_MIN=2, MIN_HOPS=1.
- FULL: N=8192, V=1200 (N/V=6.83), seeds=[7,17,23,31,41], 300 train / 240 test chains, SR_STEPS=8000 batch 256.
- SMOKE (local CPU): N=2048, V=300, seeds=[7,17], 120/120 chains, SR_STEPS=1500 batch 96.
- SELFTEST: N=1024, V=40, L_SUPPORT=[2,4,6], SR_STEPS=900.

## Selftest result (MEASURED@ run 2026-07-08, --self-test on .venv, device=cpu)
SELFTEST_OK. acc[F=0.211 CEIL=0.367 A=0.933 R=0.267 S=0.311 O=0.933]; accpc[F=0.0528 A=0.3373 R=0.0684 S=0.0927 O=0.3373]; corr[A=1.000 S=-0.133]; spread=1.17; theta*=0.15; reach_rank=0.467. ST-CORPUS/ARRIVAL/MECHANISM/SIGNAL/TELEMETRY/REALLOCATION/DRIFT/ARMS-DIFFER/PIPELINE all pass.

## Honesty flags
- ADAPTIVE ~ ORACLE_HALT by design: on clean codebook states, arrival (cos-to-goal) is near-perfectly detectable, so the adaptive detector approaches the ground-truth arrival oracle. The load-bearing, non-trivial claim is that the FROZEN depth knob DISCARDS this available signal (over/under-running), and making it adaptive RECOVERS it; the RANDOM/SCRAMBLE controls prove the gain is signal-driven, not by-construction. The harder regime -- imperfect cleanup / graded (noisy) arrival confidence where the detector is non-trivial -- is the natural follow-up dial (and the note's channels 2-6). Expected honest tier: MEASURED_MECHANISM for a first de-risked dial; Skunkworks owns landed-VET.
