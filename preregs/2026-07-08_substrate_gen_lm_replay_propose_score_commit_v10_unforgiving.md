# Pre-reg: substrate_gen_lm_replay_propose_score_commit_v10_unforgiving_n8192_gpu

- Date: 2026-07-08
- Cell: `experiments/exp_substrate_gen_lm_replay_propose_score_commit_v10_unforgiving_n8192_gpu.py`
- Predecessor: v9 (`preregs/2026-07-08_substrate_gen_lm_replay_propose_score_commit_v9.md`, commit 8a1f04836),
  which landed INCONCLUSIVE_NO_COMPOUNDING.
- Design note: `notes/research_native_glassbox_generation_brain_first_2026-07-08.md`
- Stage: 3 (higher-function generation MECHANISM on a synthetic structural regime; NOT Stage-4 language).
- Status: SMOKED 2026-07-08 (CPU, N=4096 + full-N=8192 preview). Verdict = INCONCLUSIVE (honest negative).
  NO FULL dispatch. Re-spec direction below.

## Prior-work check (KB dogfood)
`bash tools/substrate_query.sh "accumulator compounding drift unrecoverable mid-sequence error growing
superposition bundle depth degradation working memory overload"` -> top cosine 0.2832 (< 0.30 threshold);
top hits = algebra-taxonomy (monoid/bundling), R-GCN/CompGCN integration, permutation-role-binding. NONE is a
prior compounding-accumulator generation cell. Genuinely NOVEL (a re-aim continuation of v9), not a rediscovery.

## What v10 re-aims (why v9 was INCONCLUSIVE)
v9's must-fail ACCUMULATE did NOT compound (body_drift +0.087 < 0.10). Root cause (two mechanisms, both fixed here):
1. The old accumulator did `c = normalize(W @ c_prev)` each step -- a self-CORRECTING attractor (a good hetero-
   associative W re-projects to a clean codeword every step), so error did NOT accumulate.
2. The per-step goal-content gate `content_iv/GATE_TAU` (TAU=0.05 = 20x weight) is POSITION-INDEPENDENT
   (`cos(goal, R_goal[v])` needs only goal + candidate, not current position) -> it re-grounds navigation to the
   goal EVERY step regardless of drift == a clean external reference each step == the regenerative-repeater property
   that PREVENTS compounding (research_noise_compounding_bound_2026-07-07).

v10 fixes (prereg's named Lever 1 = weaken/remove R_goal rescue):
- ACCUMULATE is a GENUINE growing leaky-bundle accumulator: `c = LAMBDA_ACC * c + cb[nxt]` (LAMBDA_ACC=0.65),
  never resets to a clean codeword; position is decoded from the drifting bundle; next-token prediction is
  `normalize(W @ c)` over the whole bundle (crosstalk grows with depth).
- `ACC_CONTENT_W = 0.0`: the accumulator navigates by its LOCAL recency/traffic (freq) signal only -- NO
  position-independent goal oracle. (Fairness ladder: RANDOM_RESTART has neither freq nor content nor selection;
  ACCUMULATE has the local freq signal; REPLAY has content-guided proposal + offline whole-candidate goal-scoring.
  The single-forward-pass accumulator architecture structurally cannot use the goal oracle without per-step
  re-grounding -- which is exactly the anti-compounding property.)
- Discriminator upgraded: ACCUMULATE body compounds (body_drift>=DRIFT_MIN) AND REPLAY stays bounded
  (rep_body_drift<=REPLAY_FLAT_MAX; and D1b: accum compounds >= DRIFT_MIN MORE than replay) AND REPLAY beats
  RANDOM_RESTART. Full-N=8192 ACCUMULATE PREVIEW added (DISCRIMINATOR-MUST-SURVIVE-SCALE option C; bundle crosstalk
  is N-dependent so smoke's own N is not sufficient evidence for the N=8192 target).

## Arms (unchanged from v9 except ACCUMULATE re-design; PAIRED, matched compute)
ORACLE (readout positive control), REPLAY (arm under test), ACCUMULATE (v10 growing-bundle must-fail baseline),
RANDOM_RESTART (compute-matched redundancy control), REPLAY_PROPOSE_ONLY (scoring-value diagnostic).

## Metrics (unchanged): goal_reach, per_token_acc, body_token_acc (mid-sequence 1..L-1, excludes goal position).

## Compute architecture
mixed: batched-GPU numeric core (I*R walkers, one matmul per L step on cuda for FULL, cpu for smoke) + CPU numpy
peel/SIC readout. Sequential exemption: candidate WALKS have genuine step-L-depends-on-L-1 dependency; independent
axes (I x R) batched. Storage: sharded fragment edges bundled into W_trans (bundled IS the discriminator: its
capacity limit + the ACCUMULATE growing-bundle are the intended compounding sites). GPU-batching mandatory FULL.

## Bands (HYPOTHESIZED@this prereg)
HARD_PASS (HP_SCOPE REPLAY only): ACCUM body_drift>=DRIFT_MIN=0.10 AND REPLAY body_drift<=REPLAY_FLAT_MAX=0.06 AND
  (ACCUM body_drift - REPLAY body_drift)>=DRIFT_MIN AND REPLAY body>=ACCUM body at depth AND REP-ACCUM goal_reach
  >=MARGIN_ACCUM=0.20 AND REP-RANDOM goal_reach>=MARGIN_REDUNDANCY=0.15 AND body-gap grows with L AND sel_value>0
  AND ORACLE>=0.90 AND CV<=0.15.
HARD_FAIL: REP-RANDOM(goal_reach) <= NO_RECOMB_BAND=0.05 (win is redundancy) OR diversity < 0.10 OR REPLAY does not
  beat ACCUMULATE on goal_reach.
INCONCLUSIVE: readout unsound/NaN OR baseline out of band OR NO_COMPOUNDING (D1) OR compounding not accumulator-
  specific (D1b: REPLAY drifts as much as ACCUMULATE).
MIDDLE_BAND: beats both controls + scoring earns keep but misses a strict HARD_PASS gate.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(L_GRID); verdict counts len(per_unit)).
- arms_differ_verified: true (SHA256 of per-L curves + selftest arms-differ assert; MEASURED div>=0.46).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- except-ordering: except SystemExit: raise / KeyboardInterrupt: raise / Exception (no BaseException; no bare
  except). VERIFIED by grep gate (ok_no_baseexception / ok_no_bare_except).
- crlb_n/a: graph-walk + gate-select + peel/SIC readout has no closed-form CRLB; discriminator is the ARM-vs-ARM
  gap; chance floor = 1/WIDTH (THEORETICAL); readout floor certified by ORACLE positive control (MEASURED 1.000).
- discriminator_survives_scale: full-N=8192 ACCUMULATE PREVIEW (option C). MEASURED body_drift +0.132 at N=8192,
  bit-consistent with N=4096 (+0.132) -> compounding survives scale.
- baseline_in_band: ACCUMULATE goal_reach = 0.30-0.34 in (chance=0.167, 0.95) (D4). MEASURED.
- calibration_check: default_ok_for_this_regime (GATE_TAU=0.05, BETA=1.0 from v7/v8; LAMBDA_ACC=0.65 leaky-
  integrator time constant + ACC_CONTENT_W=0.0 set a priori by the anti-compounding-mechanism argument, NOT tuned
  per-L for PASS; the strict --self-test discriminator-fires gate is the health check).
- baseline_in_band / discriminating: ACCUMULATE 0.34 (goal_reach), 0.35-0.48 (body) -- in band; REPLAY 1.0
  goal_reach; RANDOM 0.18 goal_reach (floor control) -- all measurable.
- cell_chunked: false (3 seeds in-cell, per-seed checkpoint/resume). start_marker/crash_diag/heartbeat: true.
- progress_logging: print_flush_true (line-buffered stdout; all progress lines flush=True).
- HP_SCOPE: {REPLAY: [body_drift, replay_flat, accum_specific, accum_margin, redundancy_margin, body_gap_grows,
  sel_value, cv]; ORACLE: [readout_floor]}.

## SMOKE result (MEASURED@data/exp_substrate_gen_lm_replay_propose_score_commit_v10_unforgiving_n8192_gpu_smoke/metrics.json, 2026-07-08)
seed=7, N=4096, L_GRID=[4,14], WIDTH=6, OUT_DEG=4, N_INST=80, R_CAND=40, device=cpu. Full-N=8192 preview appended.
Per-L (MEASURED):
- ORACLE       body L4=1.000 L14=1.000 ; goal_reach 1.000/1.000 (readout + metric SOUND).
- REPLAY       body L4=0.404 L14=0.312 (drift +0.093) ; goal_reach 1.000/1.000 (FLAT, perfect generation success).
- ACCUMULATE   body L4=0.483 L14=0.351 (drift +0.132 COMPOUNDS) ; goal_reach 0.300/0.338 (in band).
- RANDOM_RESTART body L4=0.229 L14=0.215 ; goal_reach 0.263/0.175 (floor control).
- REPLAY_PROPOSE_ONLY body 0.242/0.238 ; goal_reach 1.000/1.000.
- REP-RANDOM goal_reach = +0.825 ; REP-RANDOM body = +0.096 ; sel_value(REP-PROPOSE_ONLY, body) = +0.073.
- REP-ACCUM goal_reach = +0.662 (REPLAY dominates generation SUCCESS at all depths).
- Full-N=8192 preview: ACCUM body L4=0.483 -> L14=0.351, body_drift = +0.132 >= 0.10 = FIRES (survives scale).

VERDICT = INCONCLUSIVE_COMPOUNDING_NOT_ACCUMULATOR_SPECIFIC (D1b).

## Honest reading (what fired, what did not)
FIRED (the re-aim's PRIMARY objective, achieved): the v10 growing-bundle ACCUMULATE now GENUINELY COMPOUNDS --
  body_token_acc drops +0.132 with depth, and this survives to the FULL N=8192 target (+0.132, N-consistent). v9's
  no-compounding root cause is fixed.
FIRED (separable positive, real + banked): REPLAY achieves PERFECT goal_reach (1.000) at ALL depths (bounded/flat
  generation success), dominates the accumulator on goal_reach (+0.662) and the compute-matched RANDOM_RESTART
  redundancy control (+0.825 goal_reach, +0.096 body), and scoring earns its keep over goal-gated proposal
  (sel_value +0.073). The recombination + scoring win is genuine, not redundancy.
DID NOT FIRE (why INCONCLUSIVE, not HARD_PASS): the strict "REPLAY stays flat while ACCUMULATE compounds ON THE
  SAME metric" claim is NOT established. body_token_acc (exact laid-down-path match) is CONFOUNDED in this
  multi-valid-path regime: (start,goal) does not uniquely determine the path, so REPLAY -- which optimizes
  goal_reach via OFFLINE whole-candidate scoring -- commits A valid goal-reacher that is not the exact laid-down
  path, so REPLAY's exact-path body is LOW (0.31-0.40) and ALSO declines with depth (+0.093). The accumulator,
  following high-traffic edges, stays NEARER the true backbone, so its body is actually HIGHER than REPLAY's at
  every depth (0.48>0.40 at L4, 0.35>0.31 at L14). Hence the only metric on which the accumulator degrades (body)
  is one where REPLAY does not beat it and also degrades -> the compounding is not cleanly accumulator-specific
  (gap +0.040 < DRIFT_MIN). Not a band-tuning miss -- a structural metric confound.

## Re-spec direction (route to Research)
Use a UNIQUE-PATH regime so body_token_acc has a clean ceiling for REPLAY:
- Construct the DAG so that for each (start, goal) there is exactly ONE valid route: from each node, exactly ONE
  out-neighbor keeps the goal reachable; all other out-neighbors are goal-dead-ends (`goal not in reach[v]`).
  Then ORACLE = REPLAY body ceiling ~1.0 (REPLAY, scoring by goal-reach, follows the unique route -> exact-path
  match), REPLAY body stays FLAT, while ACCUMULATE (traffic/drift navigation) takes goal-dead-end branches ->
  off the unique path -> body compounds. This removes the multiple-valid-path confound that made REPLAY's body
  decline.
- Keep the v10 growing-bundle accumulator + ACC_CONTENT_W=0 (already makes the accumulator compound; the fix is
  purely the graph/metric ceiling, not the accumulator).
- Alternative witness worth banking now: on goal_reach (generation SUCCESS), REPLAY is decisively + robustly
  better (1.000 vs 0.34, +0.66) at all depths and beats redundancy (+0.83) -- but that gap is depth-CONSTANT
  (the accumulator's failure is front-loaded), so it demonstrates "REPLAY generates successfully where the
  accumulator fails" but NOT "error COMPOUNDS with depth." The depth-compounding claim specifically needs the
  unique-path regime above.
