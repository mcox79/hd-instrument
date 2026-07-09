# Pre-reg: substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu

- Date: 2026-07-08 (authored/recovered 2026-07-09 UTC)
- Cell: `experiments/exp_substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu.py`
- Routing/design note: `notes/research_native_glassbox_generation_brain_first_2026-07-08.md`
- Stage: 3 (higher-function generation MECHANISM on a synthetic structural regime; NOT Stage-4 language)
- Status: RECOVERED + SMOKED 2026-07-09. Smoke verdict = INCONCLUSIVE_NO_COMPOUNDING. NO FULL dispatch.

## Prior-work check (KB dogfood)
`bash tools/substrate_query.sh "replay propose score commit generation competitive queuing peel decoder bounded
plan vector"` -> top cosine 0.2803 (below 0.30 threshold); top hits = Foldiak-DG competitive-Hebbian prereg,
compositional-reasoning coverage note, "Competition" FrameNet/WordNet atoms. NONE is a prior replay-propose-
score-commit GENERATION cell. This cell is genuinely NOVEL, not a rediscovery.

## Mechanism (brain-first)
REPLAY-PROPOSE-SCORE-COMMIT (barrier #1 generation, the last open Stage-4 barrier's mechanism half): generate
whole candidate plans OFFLINE by hippocampal-SWR-style replay that recombines already-learned local fragments
(Pfeiffer & Foster 2013; Mattar & Daw 2018 gain x need), score each WHOLE candidate by the certified content-vs-
recency combined gate (v5-v8), commit the best, and read the committed bounded plan out ONE ITEM AT A TIME via
the already-built competitive-queuing peel/SIC decoder (`hdlab.cleanup_family.peel_sic_readout`, mode='proj').
No accumulator -> nothing compounds by construction. Contrast: the substrate's 4x-failed step-wise ACCUMULATE
pattern (carry raw running state, read off own drift) and PREDICT_RESIDUAL_TD (self-referential correction).

## Task regime (synthetic, clean, explicitly structural; NOT natural language)
Layered DAG, WIDTH tokens/layer (disjoint ids), G=N_INST target paths laid down start(layer0)->goal(layerL) with
preferential-reuse (skewed traffic -> shared fragments -> genuine recombination library). Instance=(start,goal).
Stores: W_trans (N,N bundled hetero-associative context->next, capacity-limited); R_goal (V,N learned goal-
reachability). Gate: logit(v)=content_rel(v,g)/GATE_TAU + BETA*freqcos(v), softmax over out-neighbors.

## Arms (PAIRED, matched compute R candidates x L steps + 1 peel/SIC readout)
- ORACLE (positive control: readout of TRUE path; certifies readout + metric; HP_SCOPE = readout-fidelity only)
- REPLAY (arm under test: gain x need proposal, SCORE whole candidate by combined-gate coherence incl. freq, commit best)
- ACCUMULATE (must-fail drift baseline: raw carried context, reads off own drifting state, no clean reset)
- RANDOM_RESTART (compute-matched redundancy control: uniform proposal + uniform selection)
- REPLAY_PROPOSE_ONLY (diagnostic: gain x need proposal but UNIFORM selection -> isolates SCORING value)

## Metrics
- goal_reach = [emitted[L]==g] : route-generation SUCCESS.
- per_token_acc : exact laid-down path match (LOW ceiling; (start,goal) does not uniquely determine the path).
- body_token_acc : mean over MID-SEQUENCE positions 1..L-1 EXCLUDING the goal position = ARTIFACT-FREE COMPOUNDING
  WITNESS (goal position is content-gate-rescued for every arm; including it manufactures a spurious depth-varying-
  weight drift in per_token_acc). THEORETICAL chance = 1/WIDTH per position.

## Compute architecture
mixed: batched-GPU numeric core (I*R walkers advanced one matmul per L step on cuda for FULL, cpu for smoke) +
CPU numpy peel/SIC readout (1 committed plan/instance/arm; reuses hdlab.cleanup_family.peel_sic_readout).
Sequential exemption: candidate WALKS have genuine step-L-depends-on-L-1 dependency; independent axes (I x R)
are batched. Storage: sharded fragment edges bundled into W_trans (bundled IS the discriminator: its capacity
limit is the intended source of ACCUMULATE drift). GPU-batching mandatory for FULL (N=8192).

## Discriminator-fires (compounding witness = body_token_acc)
- D1: ACCUMULATE body_token_acc(L_lo) - body_token_acc(L_max) >= DRIFT_MIN=0.10 (accumulator compounds).
- D2: REPLAY goal_reach - RANDOM_RESTART goal_reach >= MARGIN_REDUNDANCY=0.15 (redundancy control underperforms).
- D3: ORACLE per_token_acc >= ORACLE_FLOOR=0.90 (readout + metric sound).
- D4: ACCUMULATE goal_reach in (chance, 0.95); RANDOM_RESTART is the floor control (~chance).
- Selection value: REPLAY body_token_acc - REPLAY_PROPOSE_ONLY body_token_acc > 0 (SCORE step earns its keep).

Two-tier self-test: import-time = validity only (readout/telemetry/arms-differ) so --smoke completes and lands an
honest verdict; DISCRIMINATOR-FIRES asserted only under explicit --self-test (pre-dispatch gate).

## Bands (HYPOTHESIZED@this prereg)
PASS band (HARD_PASS, HP_SCOPE REPLAY only): body_drift >= 0.10 AND REPLAY-ACCUMULATE(goal_reach) >= 0.20 AND
  REPLAY-RANDOM_RESTART >= 0.15 AND body-gap grows with L AND sel_value > 0 AND ORACLE >= 0.90 AND CV(seeds) <= 0.15.
FAIL band (HARD_FAIL): REPLAY-RANDOM_RESTART <= NO_RECOMB_BAND=0.05 (win is redundancy) OR committed-path
  diversity < 0.10 (candidate collapse) OR REPLAY does not beat ACCUMULATE.
INCONCLUSIVE: readout unsound OR baseline out of band OR NO_COMPOUNDING (body_drift < 0.10).
MIDDLE_BAND: beats both controls + scoring earns its keep but misses a strict HARD_PASS gate.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(L_GRID); verdict counts len(per_unit)).
- arms_differ_verified: true (SHA256 of per-L per_token_acc curves + selftest arms-differ assert).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- except-ordering: except SystemExit: raise / except KeyboardInterrupt: raise / except Exception (no BaseException; no bare except). VERIFIED by grep gate.
- crlb_n/a: graph-walk + gate-select + peel/SIC readout has no closed-form CRLB; discriminator is the ARM-vs-ARM
  gap; chance floor = 1/WIDTH (THEORETICAL); readout floor certified by ORACLE positive control.
- baseline_in_band: ACCUMULATE goal_reach in (chance, 0.95) checked (D4).
- discriminator_survives_scale: body_drift empirically N-INDEPENDENT (N=512 == N=1024 per-position curves,
  MEASURED). Caveat: measured body_drift ~0.087 < 0.10 -> does NOT fire (see recovery finding).
- calibration_check: default_ok_for_this_regime (GATE_TAU=0.05 from v7/v8, BETA=1.0, peel/SIC mode='proj'; fixed a priori).
- cell_chunked: false (3 seeds in-cell, per-seed checkpoint/resume via _seed_checkpoint; light per-seed wall).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- progress_logging: print_flush_true (line-buffered stdout; all progress lines flush=True).
- HP_SCOPE: {REPLAY: [body_drift, accum_margin, redundancy_margin, body_gap_grows, sel_value, cv]; ORACLE: [readout_floor]}.

## SMOKE result (MEASURED@data/exp_substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu_smoke/metrics.json, 2026-07-09)
seed=7, N=1024, L_GRID=[4,10], WIDTH=5, N_INST=60, R_CAND=32, device=cpu.
- ORACLE per_token_acc = 1.000 (readout + metric sound).
- goal_reach @L10: REPLAY=1.000, ACCUMULATE=0.733, RANDOM_RESTART=0.217, REPLAY_PROPOSE_ONLY=1.000.
- body_token_acc @L10: REPLAY=0.346, ACCUMULATE=0.402, RANDOM_RESTART=0.204, REPLAY_PROPOSE_ONLY=0.278.
- REP-RANDOM = +0.783 (goal_reach) / +0.143 (body); sel_value (REP - PROPOSE_ONLY, body) = +0.069.
- ACCUMULATE body_drift (L4=0.489 -> L10=0.402) = +0.087 < DRIFT_MIN=0.10.

VERDICT = INCONCLUSIVE_NO_COMPOUNDING. The must-fail ACCUMULATE baseline does NOT compound in this regime (the
goal content-gate rescues the final position for every arm, so mid-sequence error is depth-flat), so the headline
"REPLAY beats a compounding accumulator" claim is UNTESTED. Empirically N-independent -> will not self-correct at
FULL N=8192. NO FULL dispatch. SEPARABLE POSITIVE (real, banked): the recombination+scoring win fires cleanly --
REPLAY beats the redundancy control (RANDOM_RESTART) and the scoring step earns its keep over goal-gated proposal
(REPLAY > REPLAY_PROPOSE_ONLY).

## Re-spec direction (route to Research)
To test the no-compounding half, need a regime where mid-sequence errors are UNRECOVERABLE (no goal-attractor
rescue): e.g. remove/weaken R_goal so a wrong intermediate branch cannot be salvaged toward the goal; OR score
the FULL emitted route (not just goal-reach); OR a task with no single terminal attractor. The recombination+
scoring positive can be hardened separately (regime where a single goal-gated walk often MISSES the goal, so
selection among R candidates is load-bearing on goal_reach too, not only body).
