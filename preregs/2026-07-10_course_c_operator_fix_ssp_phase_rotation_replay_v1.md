# Pre-reg: Course C operator-fix -- phase-rotation / SSP-FPE replay-consolidation on a KNOWN-compositional testbed

- anchor_name: `course_c_operator_fix_ssp_phase_rotation_replay_v1`
- cell: `experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py`
- metrics: `data/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1/metrics.json`
- date: 2026-07-10
- queue: overnight_queue (GPU) FULL; local self-test + local CPU smoke are the pre-flight gates (matmul-heavy FPE
  ranking + coord fits x 5 seeds; local is smoke-only, USER-locked). device=auto (cuda on the GPU host).
- seeds FULL: [7, 13, 17, 23, 31] (5); EXPECTED_N_UNITS = n_seeds
- design: `notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md`
- companion (pre-registered SSP_FRACTIONAL arm + back-door check): `notes/research_ssp_fractional_binding_degree_invariant_relational_code_2026-07-10.md`
- controls scaffold: `notes/research_offline_consolidation_multiview_degree_invariance_prior_art_2026-07-10.md`

## Question
The reasoning wall is knowledge+representation (ranker line closed, 2 fair HARD_FAILs). Course C = a map-builder that
turns relations into a GEOMETRIC generalizing code so held-out relations fall out of the geometry. Prereq
`stage3_hrr_involutive` HARD_FAIL (heldout_acc=0.0067=chance) was diagnosed as a CONFIG/METHOD limit (wrong primitive =
real/bipolar HRR; one global fact bundle = 1/sqrt(500) crosstalk; similarity-DESTROYING i.i.d. entity codes), not a
wall. The de-risked sub-claim (P~0.40): does phase-rotation binding (FHRR complex, RotatE-equivalent, |r|=1 exact
unitary) + FPE/SSP CONTINUOUS entity encoding, factorized per-relation-TYPE, GENERATE held-out compositional relations
(never-seen but derivable edges, incl. transitive A->C) degree-invariantly, BEATING frequency, where the
discrete-binding baseline (the stage3 failure mode) does NOT? Tested on a self-contained KNOWN-compositional synthetic
testbed so it isolates the OPERATOR, independent of the CSKG-corpus VET (separate/in-flight
`grounding_additive_geometric_degree_control_v1`).

## Testbed (self-contained; no substrate corpus)
k-dim integer grid [0,L)^k. Entities = grid points; relation TYPES = fixed integer translations; a TRUE edge (h,r,t)
exists iff x_t = x_h + delta_r (in-grid). GENUINELY compositional: translations compose additively so a composite
relation r1.r2 has delta = delta_r1 + delta_r2, and a NEVER-OBSERVED composite edge A->C (A->B via r1, B->C via r2) is
DERIVABLE by geometry (transitive inference). Border-vs-interior gives a real tail-degree gradient -> data-driven
LOW/MID/HIGH tertiles (degree-invariance is the whole point). Info-ceiling ~1.0 (fully derivable) -> the win bar is
fair/high; achieved/ceiling reported. FREQ-GUESSABLE control corpus = star graph (tails = Zipf popularity, NO
translation law) = the must-fail-#4 anti-manufacture check.

## Arms (PAIRED: same held-out split + candidate set + degree strata per seed)
- DISCRETE_BIND (stage3 failure-mode baseline): i.i.d. random complex64 unit-phasor entity codes (NO coordinate) +
  per-relation-TYPE learned diagonal unitary rotation R_r = circular-mean(z_t*conj(z_h)); predict argmax_t
  Re<z_h*R_r, z_t>. Similarity-destroying -> cannot generalize to an unseen (h,r) pair -> chance. MUST FAIL.
- ONESHOT_ROTATE (SSP_FRACTIONAL, one-shot): continuous coords X + displacements D fit by TransE margin-ranking
  (additive in coord space; negative sampling prevents collapse), single pass; FPE phasor readout S(x)=exp(i X@W),
  W~N(0,ell^-2), predicted tail phasor S(x_h)(.)T_r=S(x_h+delta_r) scored by BOUNDED kernel Re<S_hat,S(x_t)>/dim.
- REPLAY_CONSOLIDATED (same operator; NEW ingredient): coords/displacements fit by iterative interleaved replay with a
  per-relation RECALL-CONSISTENCY gate (commit delta_r only if two disjoint replay minibatch estimates agree,
  cosine>=REPLAY_GATE) + per-relation VALIDATION EARLY-STOP (halt consolidating r once its held-back val error rises).
- SCRAMBLE_REPLAY (must-fail #1): identical replay but relation labels shuffled each pass. MUST NOT beat ONESHOT.
- BASELINE_POP (frequency incumbent): score(candidate) = visible-graph degree. No geometry. The bar.
- RANDOM_CODES (null / geometry-necessary): random coords + identical FPE kernel machinery -> near-chance.
- ORACLE_TRANSDUCTIVE (must-fire): ONESHOT coords fit WITH held-out visible -> MUST recover (>> random) or setup broken.

## Primary metric
reach@1 = filtered Hits@1 on the held-out completable subset, PLUS per-degree-stratum reach@1 (LOW/MID/HIGH tertiles of
the TRUE-TAIL visible-graph degree), PLUS composite-relation (transitive A->C) reach@1. Also MRR, achieved/ceiling.

## Pre-registered bands (picked BEFORE the run)
- OP_MARGIN=0.20 (OPERATOR_FIX aggregate: oneshot - discrete); POP_GAP=0.10 (oneshot beats POP);
  DISCRETE_CEIL=0.15 (discrete at stage3 floor); RANDOM_CEIL=0.15; ORACLE_FIRE_MARGIN=0.20; TIE_EPS=0.03.
- SCRAMBLE_EPS=0.05 (scramble - oneshot); FREQ_MANUFACTURE_EPS=0.05 (freq-corpus oneshot - pop).
- CONSOL_REL=0.15 (replay LOW >= oneshot LOW * 1.15); REGRESS_REL=0.05; FLAT_EPS=0.10 (|reach_HIGH - reach_LOW|);
  R_BACKDOOR=0.20 (coord-precision-vs-degree |r|). MIN_STRAT_Q=20; MIN_HELDOUT=30.
- FPE bandwidth FPE_ELL=0.55 (PRE-REGISTERED before the run; post-hoc kernel tuning would make the degree-invariance
  verdict untrustworthy by construction -- companion-note requirement). KGE: margin=1.0, neg=10, wd=1e-3, lr=0.02.

## Decision (both bands, before running)
- **OPERATOR_FIX_CONFIRMED** (the P~0.40 sub-claim; SMOKE-GATED headline) = oneshot - discrete >= OP_MARGIN AND
  oneshot - pop >= POP_GAP AND discrete <= DISCRETE_CEIL AND random <= RANDOM_CEIL AND oracle - random >=
  ORACLE_FIRE_MARGIN AND scramble - oneshot <= SCRAMBLE_EPS AND freq-corpus(oneshot - pop) <= FREQ_MANUFACTURE_EPS
  -> phase-rotation/SSP is off the stage3 floor; operator-fix real.
- **CONSOLIDATION_HELPS** (the P~0.20-0.25 sub-claim; REPORTED at smoke, decided at FULL landed-VET -- telemetry may
  wash at scale, HOLD the mechanism story) = replay LOW >= oneshot LOW * (1+CONSOL_REL) AND replay agg no-regress >
  REGRESS_REL AND |reach_HIGH - reach_LOW|(replay) <= FLAT_EPS AND |backdoor_r| < R_BACKDOOR.
- **OPERATOR_FIX_FAILS_WALL_BELOW_BINDING_PRIMITIVE** = oneshot - discrete <= TIE_EPS OR oneshot - pop <= TIE_EPS ->
  substrate inductive-generalization wall is BELOW binding-primitive choice; redirect to Course B / Course D.
- **MIDDLE_BAND_OPERATOR_FIX_PARTIAL** = otherwise.
- Verdict labels: HARD_PASS_OPERATOR_FIX_AND_CONSOLIDATION (both) / OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE
  (operator-fix only) / OPERATOR_FIX_FAILS_WALL_BELOW_BINDING_PRIMITIVE / MIDDLE_BAND_OPERATOR_FIX_PARTIAL.

## Diagnostics (folded in per companion notes; reported; some gate consolidation-trust)
- COORD-PRECISION-VS-DEGREE back-door (companion HARD-PASS #7): per-entity coord instability across seed refits vs
  degree; |r| must be < R_BACKDOOR for a trusted consolidation win (else the same estimation-quality channel as TransE
  laundered through a kernel). CROSS-CHANNEL INDEPENDENCE pre-flight (geometry score vs degree channel). LEAKAGE AUDIT
  (Sun 2019): synthetic grid asserts NO inverse-duplicate translation + NO near-Cartesian relation. EFFECTIVE-RANK
  anti-collapse (coord SVD participation ratio) tracked for oneshot + replay.

## Self-test (proves the discriminators FIRE) -- MEASURED@ local self-test 2026-07-10, SELFTEST_PASS 9.2s
Planted grid: oneshot=0.718 recovers held-out + beats DISCRETE=0.0256 (margin 0.69 >= 0.20) + beats POP=0.0256;
DISCRETE at chance; RANDOM=0.0; ORACLE=1.0 fires; SCRAMBLE=0.0256 does not beat oneshot; composite A->C oneshot=0.511
generates never-seen transitive edges. Planted freq-star: POP=0.594 FIRES + oneshot=0.500 does NOT beat POP
(manufacture_margin=-0.094). 7 distinct arm sigs. VacuousSmokeError guard fires if DISCRETE passes the operator-fix bar.

## Smoke preview (2 seeds, k=2 L=9, fpe_dim=1024; REPORT-ONLY, telemetry may wash at FULL -- HOLD mechanism story)
MEASURED@data/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1_smoke/metrics.json 2026-07-10 (9.9s):
verdict OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE. reach@1 oneshot=0.912 discrete=0.007 (margin=0.905>=0.20)
pop=0.010 scramble=0.045 random=0.000 oracle=1.000 replay=0.835. ALL 7 operator-fix gates True. freq-corpus
manufacture_margin=-0.238 (no manufacture). Composite A->C: oneshot=0.871 replay=0.855 discrete=0.102 (SSP generates
never-seen transitive edges; discrete fails). Degree strata (ONESHOT): LOW=0.895 MID=0.915 HIGH=0.938 (nearly FLAT =
degree-invariant). CONSOLIDATION inconclusive (consolidation_helps=False; replay 0.835 <= oneshot 0.912 -- oneshot
near-saturates the ~1.0 ceiling on this clean derivable grid, leaving no headroom for replay; backdoor_r=-0.588). The
consolidation ingredient may need a HARDER/noisier/sparser regime (where oneshot does not saturate) to show benefit --
this is the FULL landed-VET question, NOT decided by smoke.

## Compute architecture
class: (a) batched-GPU. Coord fit = TransE margin-ranking over edge minibatches (vectorized); FPE encode = one [N,k]@[k,
dim] matmul then complex exp; ranking = single batched Re(S_hat @ conj(S_all).T)/dim per arm on a SHARED candidate
tensor (PAIRED). Storage strategy: SHARDED (each entity its own code/coord; relation operators factorized per TYPE,
NEVER one global fact bundle -- the explicit fix for stage3 crosstalk). Grid N<=1728 (k=3 L=12), fpe_dim<=4096,
seeds=5. Routes to overnight_queue (GPU); local = SMOKE-ONLY.

## SCHEMA-VET fields
- cardinality_ok: True (EXPECTED_N_UNITS = n_seeds; each seed asserts all 7 arms produce >= 5 distinct sigs; smoke
  measured 7 distinct sigs)
- arms_differ_verified: True (7 distinct held-out score signatures among 7 arms; MEASURED at smoke)
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics + os.replace; write_partial per seed)
- crlb: filtered Hits@1 chance floor = 1/n_candidates (THEORETICAL; ~1/1728 at FULL); DISCRETE_CEIL/RANDOM_CEIL set
  above it; OP_MARGIN 0.20 on the achievable side (self-test + smoke demonstrate margin 0.69-0.905).
  discriminator_reachability: OK.
- baseline_in_band: DISCRETE + RANDOM are the anti-triviality nulls (<= ceilings, MEASURED 0.007/0.000 at smoke);
  ORACLE must-fire (1.000); POP measured confound-baseline. (AG note: DISCRETE is intentionally at-floor by design =
  the stage3 failure mode being reproduced; ONESHOT is the mechanism arm, in-band at 0.912, not saturated vs its own
  degree strata which vary 0.895-0.938.)
- discriminator_survives_scale: OPERATOR_FIX fires at the planted self-test scale AND the 2-seed smoke; the SAME arm
  code path runs FULL (k=3, L=12, 5 seeds). DISCRETE stays at chance (1/n_candidates) at any scale so the margin
  survives. CONSOLIDATION margin is REPORTED (FULL landed-VET decides; smoke shows it neutral on the clean grid).
- HP_SCOPE: OPERATOR_FIX applies to ONESHOT vs DISCRETE + POP + SCRAMBLE + freq-corpus + oracle/random controls;
  CONSOLIDATION applies to REPLAY vs ONESHOT (rare stratum + flatness + backdoor); RANDOM=null; ORACLE=must-fire.
- positive_control (Gate D): ORACLE_TRANSDUCTIVE reproduces transductive recovery (>> random, MEASURED 1.000); the FPE
  kernel + coord-fit machinery is validated by ONESHOT clearing the planted grid before any inductive/degree claim.
- effective_vs_nominal_parameter_audit: swept axis = ARM x seed x degree-stratum x {single-hop, composite}; every
  primitive experiences the nominal grid scale (no partition routing); sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: N/A (not a threshold sweep; arms are methods). The discriminating band is the
  arm CONTRAST (oneshot vs discrete), demonstrated 0.905 apart at smoke.
- composition_edges: coord-fit (R^k additive) -> FPE encode (R^k -> C^dim phasor) -> kernel score; SHAPE_MATCH at each
  edge (additive displacement composes with phase addition by construction; transitive A->C = D[r1]+D[r2]).
- positive_control_arms: ORACLE_TRANSDUCTIVE (transductive recovery must-fire); regime_extension_audit: synthetic
  grid is the NATIVE regime for the SSP/FPE construction (continuous coords exist by construction) -- SHAPE_MATCH, not
  a synthetic-to-narrative drift; the clean-derivable-grid is explicitly a SUFFICIENT-CONDITION probe of the operator,
  not a claim it transfers to a noisy discrete KG (that is the separate CSKG VET).
- functional_requirements: (1) generalize to held-out entity-PAIRS under seen relation types -> continuous FPE coords +
  per-type phase-rotation operator; (2) transitive/composite inference A->C -> displacement/phase addition; (3)
  degree-invariance -> bounded unit-modulus kernel readout blocking the norm-blowup channel; (4) not-a-popularity-
  shortcut -> POP baseline + freq-guessable corpus + coord-precision-vs-degree back-door.
- calibration_check: default_ok_for_this_regime (grid side / n_rel / held-out frac / degree tertiles are structural
  data-driven quantiles, not tuned for PASS; FPE bandwidth ell PRE-REGISTERED; KGE hyperparams standard regularized
  defaults)
- progress_logging: print_flush_true (line-buffered stdout + per-seed flush prints); cells run <30min on GPU
- cell_chunked: False (5 seeds in one cell with per-seed write_partial checkpointing + cardinality gate; per-seed
  failure recorded with failure_class, does not lose other seeds)
- start_marker_written: True; crash_diagnostic_present: True (Exception -> CELL_CRASHED metrics + traceback);
  heartbeat_present: per-seed flush log lines (cells short on GPU); defensive_error_checking: passed_4_patterns
  (start-marker + crash-diagnostic + per-seed failure-class + arms-differ; heartbeat = per-seed flush given short GPU
  runtime)
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep-verified clean
- HYPOTHESIZED vs MEASURED: all smoke/self-test numbers tagged MEASURED@ paths above; band values are pre-registered
  thresholds.
