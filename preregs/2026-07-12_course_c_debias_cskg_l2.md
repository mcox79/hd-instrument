# Pre-reg: DEGREE-DEBIASED fair re-scoring of the Course-C glass-box rotation win (CSKG L2-genuine)

Date: 2026-07-12. Author: exp_dev. Status: pre-registered BEFORE the run (bands fixed below).

Cells:
- Core: `experiments/_course_c_debias_core_v1.py`
- FULL (per-seed process isolation, REMOTE CPU): `experiments/exp_course_c_debias_cskg_l2_seed_{7,17,23}_cpu_v1.py`
- SMOKE (2-seed small CSKG core, REMOTE CPU): `experiments/exp_course_c_debias_cskg_l2_smoke_cpu_v1.py`

## Question
The landed multi-seed FULL `data/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_gpu1024_v1/metrics.json` is
MIDDLE_BAND_PARTIAL: the fair (low+mid gold-degree) WIN margin holds 3/3 seeds (oneshot_fair - POP_fair =
+0.033 seed17 / +0.035 seed7 / +0.045 seed23) while `g_backdoor` FAILS (pooled cross_channel_geom_vs_poprank_r
= 0.3118 / 0.2806 / 0.2795 vs R_BACKDOOR=0.15). Does the +0.033 fair margin SURVIVE the field's standard
leakage remedy -- a degree-matched candidate pool + within-stratum / partial correlation -- and is the pooled
0.28-0.31 correlation a genuine within-degree shortcut or a third-variable (gold-tail degree) CONFOUND?
Mechanism basis CITED@ Aiyappa et al. ICML2025 arXiv:2405.14985 + Shomer et al. WWW2023 arXiv:2302.05044
(see notes/research_degree_debiased_fair_evaluation_2026-07-12.md).

## What the cell does (faithful reproduction, one re-scoring pass)
Per seed in {7,17,23}: rebuild the IDENTICAL split (`build_cskg_core_triples` -> `build_ids` -> `mine_rules`
-> `extract_l2_genuine` -> `build_true_by_hr_int` -> `stratify_by_tail_degree`, same FULL_CFG: k_core=12,
n_eval=6000, min_support=10, min_conf=0.10, seed); REFIT ONLY ONESHOT_ROTATE (`fit_kge_rotate`, k=24,
epochs=250, n_neg=128, batch=8192, neg_chunk=16 -- the exact `_fit_and_score` recipe); recompute POP (frequency
count, no fit). Then:
- Debias A (de-confound the pooled r): pooled cross-channel r (reproduce), WITHIN each low/mid/high degree
  tertile, and a PARTIAL correlation controlling continuously for log(node_degree+1) (residualize each channel
  vs [1, log(deg+1)] via OLS, correlate residuals).
- Debias B (degree-match the candidate side): for the fair (low+mid) queries, restrict the ranking CANDIDATE
  COLUMNS to entities with global node_degree <= q2 (= tert_bounds[1]) for BOTH ONESHOT and POP; report the new
  fair margin oneshot_degmatched - POP_degmatched.

## Verification (DEVICE-HONEST; the note's P3 adapted for the mandated REMOTE CPU)
The archived fit was on CUDA; this cell is CPU-forced (task lock: no GPU). Cross-device SGD arithmetic precludes
bit-identical ONESHOT arm_sig. So:
- SPLIT_IDENTITY (HARD): reproduced strata_counts + tert_bounds must equal the archived per-seed values (exact
  ints; tert within 0.5). Proves the degree-stratification apparatus that degree-matching depends on is
  reproduced. Device-INDEPENDENT. Checked BEFORE the expensive fit -> a non-reproducing split fails fast.
- POP_FAITHFUL (HARD): reproduced fair-POP hits@10 within 0.002 of archived (POP is pure numpy -> near-exact).
  POP arm_sig recomputed + reported (exact-match noted).
- ONESHOT_FAITHFUL (REPORT/WARN, NOT hard-fail): reproduced pooled backdoor_r within 0.05 AND fair-oneshot
  within 0.02 of archive = faithful regime (CPU refit reproduces the CUDA fit's regime; debias numbers trusted).
  If it drifts, numbers are reported as an INDEPENDENT CPU refit (valid fit; debias verdict stands on its own).

## Reference values (archived, MEASURED@ the three gpu1024 metrics.json; embedded because those files are NOT
## git-tracked -> absent on the remote host)
- seed7:  POP_sig=611e7fef0f1f65ef, fair_oneshot=0.0917, fair_pop=0.0563, pooled_r=0.2806, tert=[100.0,358.0], strata=low2009/mid1991/high2000
- seed17: POP_sig=f7fe67bfd8c3af18, fair_oneshot=0.0772, fair_pop=0.0442, pooled_r=0.3118, tert=[99.0,347.0], strata=low2020/mid1985/high1995
- seed23: POP_sig=8ced24b6b93aa961, fair_oneshot=0.0949, fair_pop=0.0500, pooled_r=0.2795, tert=[100.0,344.0], strata=low2024/mid1980/high1996

## Bands (pre-registered BEFORE the run; 3-seed headline aggregated downstream over the 3 metrics files)
Reported per seed + 3-seed mean: pooled_r, within_{low,mid,high}_r, within_max_abs_r, partial_r_logdeg,
degmatched_fair_margin, plus fair_unmatched margin (reproduce) and the three verification flags.

P1 (is the pooled 0.28-0.31 a degree CONFOUND, not a within-degree leak?) -- decided by the PARTIAL correlation
(continuous log-degree control = the field-standard de-confounder; within-stratum r is a coarse LOCALIZER,
reported, expected to stay elevated relative to partial when the tertiles are wide):
- P1 HARD-PASS: |partial_r_logdeg| < R_BACKDOOR (0.15), 3-seed mean.  (the g_backdoor FAIL was a degree confound)
- P1 HARD-FAIL: |partial_r_logdeg| >= R_LEAK (0.25).  (a genuine within-degree geometry-vs-popularity leak)
- P1 MIDDLE: |partial_r_logdeg| in [0.15, 0.25).

P2 (does the fair WIN margin SURVIVE a degree-matched candidate pool?):
- P2 HARD-PASS: degmatched_fair_margin >= DEG_MARGIN_PASS (0.02), 3-seed mean, sign consistent 3/3.
  (relaxed vs the original POP_GAP=0.03 because a degree-matched pool is a strictly HARDER test)
- P2 HARD-FAIL: degmatched_fair_margin <= DEG_MARGIN_TIE (0.00) -- ties/reverses => the original WIN was a
  candidate-pool degree artifact, not relational reasoning.
- P2 MIDDLE: degmatched_fair_margin in (0.00, 0.02).

HEADLINE (3-seed):
- REDEEMED_WIN (HARD-PASS): P1 HARD-PASS AND P2 HARD-PASS -> the glass-box rotation win survives the field's
  decisive debiasing; upgrade MIDDLE_BAND -> clean WIN candidate, unblock the map-builder direction.
- LEAK_REAL (HARD-FAIL): P1 HARD-FAIL OR P2 HARD-FAIL -> the win/backdoor was (partly) a degree artifact; the
  shared fair-stratum apparatus across the course-C family has a candidate-pool blind spot to re-audit.
- MIDDLE_BAND otherwise (escalate a 4th/5th seed or a k/epoch sweep before closing).
- INCONCLUSIVE_VERIFICATION: SPLIT_IDENTITY or POP_FAITHFUL hard gate fails -> reproduction not faithful; no
  debias number is trustworthy (distinct from a substrate verdict).

DO NOT report a redeemed margin as a clean win without the degree-matched number attached (task lock).

## Info-ceiling / fairness / weak-point-localization (standing disciplines)
- Info-ceiling: the degree-matched pool is a strictly harder, fairer test than the original all-25752-candidate
  pool; the WIN bar is RELAXED to 0.02 accordingly (fair, not moved-goalpost). Partial r is bounded by the same
  Pearson [-1,1] range; R_BACKDOOR=0.15 is the same object used by the parent gate.
- Weak-point localization: within-stratum r pinpoints WHICH degree band carries any residual coupling; the
  degree-matched vs unmatched margin pinpoints how much of the win was candidate-composition freebie. Both are
  first-class per [[feedback-fairness-plus-weak-point-localization-first-class]] (USER 2026-07-10).
- Does-not-over-correct on the g_backdoor FAIL alone (partial r may show the pooled r was mismeasured) NOR
  dismiss the candidate-pool gap; holds both open until measured [[feedback-dont-over-correct-on-raw-full-either]].

## 4 validity-preflight checks (DECLARED; validated in the self-test, run LOCALLY, synthetic, seconds)
- positive_control_passes: on a planted CONFOUND arena (both channels driven only by log-degree) the estimator
  gives pooled_r high (0.94) but partial_r ~ 0 (-0.04); on a planted LEAK arena (extra degree-independent shared
  signal) partial_r stays high (0.94). The estimator SEPARATES confound from leak.  [MEASURED@ selftest]
- metric_moves: degree-matched candidate masking changes POP hits (pop_full=0.0 -> pop_degmatched=1.0 on a
  planted arena where masking removes >10 high-degree freebies) -> the masking is not structurally frozen.
- negative_control_fails_with_margin: the LEAK arena is detected as a leak (partial_r >= 0.25 with margin).
- full_gates_exercised_at_selftest: the seed_verdict gate machinery fires SEED_HARD_PASS on a synthetic pass
  and SEED_HARD_FAIL on a synthetic fail at self-test scale.
LOCAL self-test result: SELFTEST_PASS, all 4 checks True, run_mode=self_test verified (seed_7 wrapper).

## Compute architecture
class (c) MIXED: symbolic split build (mine_rules / extract_l2_genuine / stratify = sequential-CPU graph
traversal, no matmul) + ONE rotation SGD refit (minibatch, CPU-forced) + query-chunked direct readout (matmul,
SCORE_CHUNK=256 so the (nq,N) map is never whole) + degree-matched re-ranking (column-masked reuse of the same
score matrix, cheap). NO FPE-median secondary readout (not needed for debias -> drops the N x fpe_dim complex
OOM driver). Storage SHARDED (per-entity phase code). device=CPU FORCED (HDLAB_DEVICE=cpu in each wrapper; the
remote host also has a GPU, so auto would wrongly pick cuda -> forced off per the no-GPU task lock). Per-seed
PROCESS isolation: 3 separate seed wrappers. Wall estimate: ~1-2h/seed on CPU (1 rotate fit at ep250 over ~920k
augmented edges + readout); timeout 14400s (4h) per FULL seed. Batched-GPU is NOT used by design (task: CPU-only
re-scoring; and cross-device consistency with the CUDA archive is deliberately traded for the no-GPU lock, with
POP/split as the device-independent HARD verification).

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = len(seeds) per process; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if <).
- arms_differ_verified: n/a in the classic sense (2 recomputed arms ONESHOT/POP with distinct sigs by
  construction; the discriminator here is the debias ESTIMATOR, validated positive+negative in the self-test).
- final_metrics_atomicity: tmp_replace (_seed_checkpoint.write_metrics / write_partial + os.replace; crash path
  writes metrics.json.tmp -> os.replace).
- except SystemExit: raise before except KeyboardInterrupt before except Exception (no BaseException / no bare
  except) -- grep-clean (verified).
- crlb_n/a: this is a re-scoring/estimator cell, not a capacity cell. The relevant reachability is: R_BACKDOOR
  (0.15) and DEG_MARGIN_PASS (0.02) are both on the achievable side (the archived pooled r is 0.28-0.31, partial
  can range to 0; the unmatched margin is +0.033..+0.045, degree-matched is a bounded perturbation of it).
- baseline_in_band: POP is the confound baseline (device-independent, reproduced exactly). ONESHOT is the mechanism.
- calibration_check: default_ok_for_this_regime (k-core / MIN_SUPPORT / MIN_CONF / degree tertiles / mine params
  MATCH the archived FULL_CFG bit-for-bit; the partial-correlation bandwidth is OLS on log(deg+1), not tuned).
- discriminator survives scale: the debias estimator IS the discriminator; it FIRES on synthetic ground-truth
  in the self-test (confound -> partial~0; leak -> partial~0.94; masking moves POP) through the IDENTICAL code
  path used at FULL. Real-data plumbing exercised by the REMOTE SMOKE (small CSKG core) before the FULL seeds.
- sweep_alignment_verdict: ALIGNED (arm x seed x stratum; no nominal-vs-effective mismatch; the degree-matched
  candidate universe is the effective pool the metric ranks over -- explicitly the parameter under test).
- discriminating_fraction: n/a (not a parameter sweep; a fixed 2-diagnostic re-score).
- positive_control_arms: the self-test's CONFOUND + LEAK planted arenas reproduce the known separation before any
  CSKG claim. regime_extension_audit: synthetic estimator-validation -> real CSKG scores is SHAPE_MATCH (the
  estimator consumes (gold_geo, pop_rank, degree) arrays identically in both).
- functional_requirements: (a) de-confound the pooled r -> partial correlation vs log(deg); (b) localize residual
  coupling -> within-stratum r; (c) degree-match the candidate side -> column-masked filtered ranking for both
  arms; (d) prove faithful reproduction -> SPLIT_IDENTITY + POP_FAITHFUL device-independent gates.
- cell_chunked: true (single-seed-per-cell FULL wrappers). start_marker_written: true. crash_diagnostic_present:
  true (Exception -> CELL_CRASHED + traceback via wrapper_run). heartbeat: the FULL fit reuses the parent's
  fit-loop; per-seed process isolation + start-marker + per-seed _partial writes give progress visibility.
  defensive_error_checking: SystemExit/KeyboardInterrupt re-raised, per-seed failure-class captured, cardinality
  gate, crash-diagnostic outer try.
- progress_logging: print_flush_true (line_buffering reconfigure + per-seed flush prints; the reused fit loop
  flushes). timeout_s (14400) >= 1800 -> flushing mandatory: satisfied.
- run_mode verification: FULL wrappers default run_mode=full; SMOKE wrapper defaults smoke; self_test isolates to
  a _selftest dir. Post-dispatch: verify landed metrics.json run_mode == expected before claiming FULL landed.

## Dispatch plan (REMOTE CPU; queue_add.sh SCP-based, no origin push needed)
1. REMOTE SMOKE first (remote_cpu_queue): `exp_course_c_debias_cskg_l2_smoke_cpu_v1` (2-seed small CSKG core;
   proves the on-DATA debias plumbing runs on real degree distributions; no archive identity gate). Timeout 3600.
2. On smoke enqueued clean -> 3 FULL seeds (remote_cpu_queue), per-seed process isolation: seed_7/17/23_cpu_v1,
   timeout 14400 each. Each FULL fast-fails on SPLIT_IDENTITY BEFORE the expensive fit if the split does not
   reproduce, so a bad reproduction wastes minutes not hours.
