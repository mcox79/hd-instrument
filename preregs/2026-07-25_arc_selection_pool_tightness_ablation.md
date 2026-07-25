# Pre-reg: arc_selection_pool_tightness_ablation_v1

Filed 2026-07-25. Cell: `experiments/exp_arc_selection_pool_tightness_ablation_v1.py`.
Metrics: `data/exp_arc_selection_pool_tightness_ablation_v1/metrics.json`.

## Question (VET atom 29549)
7 consecutive selection HARD_FAILs. VET root-cause = (B) similarity != entailment (conf 0.72): from the
WIDE 100-fact pool EVERY answer choice greedily assembles an equally self-supporting set;
setmargin_points_correct 0.29 ~= chance despite gold_in_pool 0.91; correctness DECOUPLED from gold-reach.
The ONE thing the VET could NOT do off disk: run a tighter-POOL ablation (pool fixed at K_WIDE=100). So (C)
pool-too-wide/retrieval-granularity is DISFAVORED but NOT formally falsified. THIS CELL SETTLES IT.

Does making the candidate POOL tighter/higher-precision make selection INFORMATIVE (the correct answer's
support starts to stand out), or does 'every choice self-supports' persist wherever the gold is still
retained?

## ONE VARIABLE = pool tightness/precision
selection (A_TOPK) + combiner (agg.aggregate 'bundle') + TRAIN/TEST split are held FIXED (all imported
UNCHANGED). The WIDE re-retrieval pool machinery (mr.reformulate_seeds/_rownorm_scores + ppr, recall@100 =
0.69) is UNCHANGED. The ONLY change: `pool_members()` restricts WHICH retrieved facts are eligible
candidates for selection. The per-fact selection SCORE (learned/geometric) is precomputed ONCE on the
native wide pool; only membership varies.

POOL ARMS: POOL_100 (anchor) / POOL_50 / POOL_20 / POOL_10 (top-K by F_RR) + POOL_PREC (F_RR >= 0.5*max).
SELECTION METHODS re-run over each pool: LEARNED (PRIMARY; 29545 harness anchor) / GEO / RND (must-fail) +
ORACLE (pool-independent ceiling).

## Dual-track metric per pool arm (tracked TOGETHER = honesty guard)
1. gold-RECALL-in-pool: Q-level `gold_in_pool_frac` + fact-level `gold_retention_vs_wide` (does the gold
   fact survive the tightening?).
2. INFORMATIVENESS: `setmargin_points_correct` (of gold-reachable TEST-Chal Qs, does A_TOPK+combiner pick
   correct? = does the correct answer's support stand out?) + `mean_margin_correct` + end-to-end TEST
   Challenge.

## Bands (a priori; NO tuning). BOTH tracks = LIFT over POOL_100 wide baseline.
Absolute floors are a META_RULE_L artifact here (A_TOPK baseline setmargin_pc ~0.40, NOT the 0.29 of the
different B_SETLEVEL pipeline) -> both tracks measured as improvement over the wide baseline.
- `RECALL_RETAIN_FRAC = 0.90`: arm retains gold iff `gold_in_pool_frac[arm] >= 0.90 * gold_in_pool_frac[POOL_100]`.
- `C_LIFT_HP = 0.05` / `MB_LIFT = 0.02`: TEST-Chal Challenge lift over POOL_100.
- `INFORM_LIFT_HP = 0.08` / `INFORM_LIFT_MB = 0.03`: setmargin_points_correct lift over POOL_100.
- `RANDOM_MAX = 0.02`: per-pool RND lift over POOL_100 (must-fail).
- `ANCHOR_CHAL = 0.3663` (LEARNED@POOL_100 regression anchor; tol 0.05).
- `AG_BASELINE_SAT = 0.95` (POOL_100 challenge >= this -> vacuous).

## Decisive logic
- **C CONFIRMED** (cheap fix exists): SOME gold-retaining pool arm lifts Challenge >= C_LIFT_HP OR lifts
  setmargin_points_correct >= INFORM_LIFT_HP over POOL_100. Tightening makes the correct support stand out.
- **C FALSIFIED** (=> B confirmed; deep reframe justified): at EVERY gold-retaining arm neither track lifts;
  any Challenge lift coincides with recall COLLAPSE (flagged recall_collapse_false_positive) -- not a fix.
  'Every choice self-supports' persists wherever gold is retained: the wall is similarity!=entailment /
  thin meaning, not pool width.
- **C MIDDLE**: a gold-retaining arm clears MB but not HP -- tightening helps a little, not decisive.
- **HONESTY GUARD**: the max-Challenge-lift arm, if it lifts >= C_LIFT_HP but does NOT retain gold, is
  flagged `recall_collapse_false_positive` and does NOT confirm C.

Report STRAIGHT which way it lands. A C-FALSIFICATION (B confirmed) is the EXPECTED, fully-reportable
outcome (the VET prior favors B: the self-supporting decoys are topically-relevant real facts that
relevance-tightening should not remove).

## Controls / integrity
- Anchor: LEARNED@POOL_100 must reproduce ~0.3663 (== 29545 harness).
- Must-fail: RND per pool -> collapse (no lift over baseline).
- Discriminator-fires: pool arms must produce distinct pick vectors AND gold-recall must vary across the
  sweep AND pool sizes must shrink (else the ablation is a no-op -> POOL_TIGHTNESS_VACUOUS).
- Glass-box: at the tightest gold-retaining pool, on surface-trap lure TEST Qs, dump correct-vs-lure
  combiner support (does the correct answer now out-score the lures, or still tie?).
- Planted self-test: precision-filter drops low-F_RR lures, RETAINS gold -> A_TOPK flips to correct (proves
  C-confirm CAN fire; cell not can't-fail). Second unit test drives classify_c with a recall-collapse table
  -> asserts the honesty guard flags it and does NOT confirm C.

## Schema-vet fields
- `sweep_alignment_verdict`: ALIGNED (the swept param = pool membership; the metric measures selection over
  exactly that membership; no nominal-vs-effective gap).
- `discriminating_fraction`: the sweep spans 100->10 + precision-filter; gold-recall + informativeness are
  MEASURED per arm (not predicted-saturated) -> non-vacuous by the discriminator-fires gate.
- `positive_control_arms`: LEARNED@POOL_100 reproduces the 29545 anchor (~0.3663, tol 0.05) AT THE TEST
  REGIME; ORACLE = gold ceiling.
- `real_code_path_exercised`: [SemanticHDEncoder, arc._encode_store, ppr.topk_from_scores, pool_members,
  select_topk_local, combiner_scores] (self-test asserts all exercised).
- `deterministic_seeding`: true (fixed int seeds, numpy default_rng, sorted iteration; RND offset via
  hashlib.sha256 not builtin hash()).
- `final_metrics_atomicity`: tmp_replace. `progress_logging`: line_buffered_stdout.
- `storage_strategy`: sharded. `crlb_n_a`: geometric/learned selection, no learned noise floor; signals
  survive scale (~1/sqrt(N)); smoke at FULL n_dim=2048.
- `cell_chunked`: false (single-cell sweep, no seed axis). `start_marker_written` / `crash_diagnostic_present`
  / `heartbeat_present`: true.

## Contract
INLINE-LOCAL foreground-to-completion; NO push/remote-persist; NOT remote-portable (GloVe+WorldTree
git-ignored/large); ASCII-only; repo .venv; agent-reported VET-PENDING.

## Smoke result (2026-07-25, 150s wall, limit_easy=120 limit_chal=140)
Self-test PASS. Smoke discriminator fired: gold_in_pool 0.83->0.64 (100->10), pool sizes shrink, RND ok.
Anchor LEARNED@POOL_100 chal=0.40 (small slice; full expected ~0.366). Directional read (recalibrated
lift bands): at the ONE gold-retaining tighter arm (POOL_50), neither Challenge nor setmargin_pc lifts over
POOL_100 -> trending C_FALSIFIED. FULL confirms.
