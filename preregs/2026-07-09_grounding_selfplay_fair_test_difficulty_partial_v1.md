# Pre-registration: grounding_selfplay_fair_test_difficulty_partial_v1

Anchor: `grounding_selfplay_fair_test_difficulty_partial_v1`
Cell: `experiments/exp_grounding_selfplay_fair_test_difficulty_partial_v1.py`
Date: 2026-07-09
Gates: master-map BUILD (internal self-play referential grounding) -- FAIRNESS AUDIT of the corr(failmask)
~0.38 self-play "wall" (the grounding analog of the reader multihop fair-test that dissolved barrier #1).
Reused game machinery: `exp_selfplay_message_channel_ablation_v1.py` (train_arm/eval_masks/Channel/ARM_MODE/
_arm_K), `exp_selfplay_dg_pattern_separation_xfit_v1.py` (failure_mask_corr/neighborhood_augment/
build_candidate_sets), `exp_teacher_free_relational_encoder_cn_subgraph_v1.py` (load_cn_subgraph/
char_trigram_features/build_adjlist).
Prior-work check (substrate_query.sh): NONE at cosine>0.30 (top hits generic wordnet/math "partial
correlation" concept nodes, cosine 0.44 -- dictionary entries, not prior arc cells). Genuinely novel: first
difficulty-partialled measurement of the self-play failmask correlation.

## Question
Three consecutive independent decorrelation mechanisms plus a cross-fit and a channel ablation ALL plateaued
at corr(failmask) ~0.38 (DG 0.377; B1 crossfit 0.393; B1+EXOG 0.382 -- MEASURED, prior cells). The grounding
fairness audit (off-disk) argues this is not a residual mechanism-coupling but a SHARED-ITEM-DIFFICULTY floor:
analytically, for two binary fail masks with per-item fail probability = a shared intrinsic difficulty d_i,
`phi(fail_s, fail_l) ~= Var_i(d_i) / [p(1-p)]` (THEORETICAL) -- a floor forced by items DIFFERING in intrinsic
difficulty, INVARIANT to any encoder/anchor/active mechanism. Two decisive tells (MEASURED, ablation cell) put
the substrate AT this floor: A1_wide (8x channel capacity) RAISES corr 0.386->0.509 (a real bottleneck would
DROP); A5_cap1 (zero channel info) drives corr->0.012 while grounding->chance (correlation is carried BY the
shared signal, not a residual coupling). **Is the residual ~0.38 a REAL substrate coupling, or a broken
measurement forced by shared per-item difficulty?** Decided by CONTROLLING difficulty.

## Task construction (self-play referential naming game; REUSED verbatim -- calibration continuity)
Referents = ConceptNet subgraph nodes. Speaker: PRIVILEGED info (neighborhood-augmented `Xn`); Listener: BARE
`X`. The CROSSFIT arm is the B1_crossfit self-play (separate Enc_S/Enc_L, disjoint referent folds, shared
discrete K-symbol channel) == the ~0.38 anchor. The cells are `no_storage` (per-item masks/difficulty NOT
persisted) so this cell RE-RUNS an ENSEMBLE of independent B1_crossfit self-plays to regenerate per-item
failure + difficulty, then computes the fair scores. **This cell PERSISTS per-item masks + difficulty to a
sidecar `per_item_masks.npz` (fixes the no_storage gap -> re-auditable off-disk).**

## Difficulty estimators
- **d_ensemble (PRIMARY):** leave-model-out ensemble fail-fraction. Train N_ens independent crossfit models;
  for a target model m, d_i^{-m} = mean fail over the OTHER members' 2*(N_ens-1) competences (speaker+listener
  each). Leakage-free estimate of the item's intrinsic difficulty. Directly the `d_i` the analytical floor
  references.
- **d_collision (SECONDARY, structural, encoder-free):** max distractor-target char-trigram cosine per item.
  Higher = a distractor closely resembles the target = harder. Cross-check independent of any encoder.

## Fair scorings (the three fair ways)
1. **Difficulty-partialled corr:** residualize fail_s and fail_l each on a basis `[1, d, d^2]` of d_i (linear
   partial correlation), then Pearson of residuals. Reported under BOTH d_ensemble (primary) and d_collision.
2. **Within-difficulty-bin corr:** Q quantile bins of d_i; residualize both fail masks on the bin one-hot
   (== demean within bin) then Pearson (pooled within-bin corr); plus per-bin phi. Removes between-bin
   difficulty variance.
3. **Determinacy-fraction (DIAGNOSTIC, reported):** fraction of eval items with 0 distractor collisions
   (max distractor-target trigram cosine < tau) at tau in {0.3,0.5,0.7}, primary tau=0.5. Analog of the
   reader's unique-successor fraction. If most items are NOT uniquely separable, the task is underdetermined.

## Positive control (real-data must-fire; SATURATION-VACUOUS discipline)
**MIRROR arm** (tied encoder, both halves share the SAME representation) has a GENUINE coupling beyond
difficulty (raw ~0.77-0.79). Its partial corr MUST STAY high after difficulty-partialling. If the partialling
ALSO nukes the mirror, the estimator is over-removing (broken) -> every reading void. Proves partialling
removes shared difficulty WITHOUT destroying a known genuine coupling.

## PRE-REGISTERED BANDS (BOTH; LOCKED PROSPECTIVE; primary difficulty = leave-model-out ensemble)
- **HARD_PASS_FAIRNESS_ARTIFACT:** CROSSFIT `partial_corr <= 0.15` AND `within_bin_corr <= 0.15` (BOTH collapse
  toward ~0) WHILE `raw_corr` reproduces ~0.38 (in [0.28,0.50]) AND the MIRROR control STAYS (partial_mirror
  >= 0.40, raw_mirror >= raw_crossfit + 0.20). => the grounding "wall" is a BROKEN MEASUREMENT (shared-item-
  difficulty); the whole self-play arc is a fairness artifact; the substrate is fine.
- **HARD_FAIL_REAL_BOUND:** CROSSFIT `partial_corr >= 0.25` AND `within_bin_corr >= 0.25` (BOTH stay materially
  >0) after controlling difficulty, MIRROR control valid. => 0.38 is a GENUINE residual substrate coupling;
  the grounding HFs STAND.
- **MIDDLE_BAND_PARTIAL_COLLAPSE:** one measure collapses but not the other, or values in (0.15,0.25).
- **Void states:** ANCHOR_NOT_REPRODUCED_VOID (raw out of [0.28,0.50]); DIFFICULTY_DEGENERATE_VOID (Var(d)<1e-3
  or <3 varying bins); MIRROR_CONTROL_FAILED_VOID (mirror partial does not stay >=0.40 or raw not >crossfit+0.2);
  BASELINE_OUT_OF_BAND (crossfit fail rates outside 0.05..0.95); MACHINERY_SELFTEST_FAILED.

## Self-test (machinery must-fire; ALWAYS runs; telemetry-sensitivity)
Two controlled cases with KNOWN answers, difficulty estimated from a matched-noise synthetic ensemble sized to
FULL's leave-model-out size (E=7): (case 1) PURE shared difficulty + conditionally-independent failures ->
partial AND within-bin MUST land in the collapse band (<=0.15; finite-ensemble attenuation floor sits below);
(case 2) REAL coupling (fail_l==fail_s on half the items) -> partial AND within-bin MUST land in the stays band
(>=0.25), case-2 exceeding case-1 by >=0.15 (clean separation). Proves the bands sit on the correct sides of
the estimator's behavior. MEASURED@selftest: case1 partial=0.046 within_bin=0.048 (collapses); case2
partial=0.522 within_bin=0.524 (stays); separation clean. Machinery selftest ok=True.

## Compute architecture
(c) mixed sequential-CPU with justification. Self-play training loops sequential over epochs (genuine
dependency); shallow ProjHeads (code_dim<=192) + K x code channel matrix; per-step batched matmuls /
gumbel-softmax / candidate scoring. N_ens+N_mir independent trainings (11 at FULL). Not GPU-batching-mandatory
(small nets, loop sequential-dependent). Storage: `no_substrate_store` (no PartitionedStore writes) but
PERSISTS a `per_item_masks.npz` sidecar (re-auditability; not a store write). progress_logging:
print_flush_true (line-buffered stdout + flush=True progress + per-(role,seed) heartbeat; FULL timeout>=1800).

## Profiles
- SELFTEST: n_nodes=300, N_ens=3, N_mir=1, epochs=12, code_dim=32, feat=512, K=8, n_eval=150.
- SMOKE: n_nodes=1500, N_ens=4, N_mir=2, epochs=80, code_dim=96, feat=4096, K=12, n_eval=700, n_bins=8.
- FULL: n_nodes=8000, N_ens=8 (seeds 7..41), N_mir=3, epochs=220, code_dim=192, feat=8192, K=24, n_eval=3000,
  n_bins=10.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = N_ens + N_mir trainings; verdict counts per_model records; cardinality
  breach -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: all model (spk,lis) mask-pair digests must differ (META_RULE_AF assert).
- final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag + sidecar atomic os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep CLEAN.
- crlb_n/a: discriminator is a partial correlation vs a within-cell MIRROR must-stay control + two-case
  synthetic self-test, not a closed-form noise floor. Reachability by construction validated at selftest.
- baseline_in_band: CROSSFIT spk_fail + lis_fail in 0.05..0.95 (gate).
- discriminator_survives_scale: smoke = FULL branches at smaller scale; decision is a FULL multi-seed call
  (HOLD-mechanism-story: smoke reports VERDICT-vs-BANDS only).
- calibration_check: adaptive_with_discriminator_gate (difficulty non-degeneracy floor + mirror-stays control
  + anchor-in-band + two-case machinery self-test).
- effective_vs_nominal_parameter_audit: no sweep axis (ensemble of seeds); ALIGNED.
- discriminating_fraction: n/a (not a sweep); the discriminator is the collapse-vs-stays partial correlation.
- composition_edges: n/a (single self-play game reused verbatim; no new primitive composition).
- positive_control_arms: MIRROR reproduces the known tied-encoder high-corr regime (~0.77-0.79) AT THE TEST
  REGIME and its partial must stay high; CROSSFIT reproduces the ~0.38 anchor AT THE TEST REGIME.
- functional_requirements: (1) reproduce ~0.38 crossfit anchor -> CROSSFIT arm; (2) estimate per-item
  difficulty independently -> LOMO ensemble; (3) remove shared difficulty from the correlation -> partial +
  within-bin; (4) prove the removal preserves a genuine coupling -> MIRROR control; (5) report task
  determinacy -> collision determinacy-fraction.
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ above.

## Dispatch
Smoke: local (SMOKE-only on local_cpu per USER lock). FULL: remote_cpu_queue (self-play cells were remote_cpu;
CPU-bound sequential trainings). timeout FULL: 10800s (11 trainings x n_nodes=8000 x 220 epochs, heartbeat
every model).
