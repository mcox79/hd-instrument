# Pre-registration: PARALOG_CRISPR_SL_DETECTION_AUC (v1)

- Anchor: `paralog_crispr_sl_detection_auc_v1`
- Cell: `experiments/exp_paralog_crispr_sl_detection_auc_v1.py`
- Date: 2026-07-15
- Author: exp_dev (spawned by Director/hdi_research)
- Queue (target): `remote_cpu_queue` (glass-box CPU; no GPU speedup on sub-ms matmuls). Timeout 1800s.
- Prior-work check (substrate-KB concept-query): top hit cosine=0.29 (< 0.30 threshold; a generic WordNet entity) -> NONE at
  cosine>0.30; cell is genuinely novel, not a rediscovery.

## Question (the CHEAP DECISIVE reframe test; VET skunkworks ac879338)

Is the paralog near-zero-singles UNREADABLE null (parent regression cell `exp_paralog_crispr_nearzero_singles_curated_ivf_v1`,
commit 651030f7e -- `readable_rel=0.00424`, IVF ratio 1.001, SYM hurts -0.386 on the continuous target,
MEASURED@data/exp_paralog_crispr_nearzero_singles_curated_ivf_v1/metrics.json) (i) a GENUINE dataset null, (ii) a HARNESS-TASK
MISMATCH -- a sparse synthetic-lethal DETECTION signal our continuous-MAE / variance-readability lens was blind to, or (iii)
STRUCTURALLY UNTESTABLE on this pocket because genes do not recur across pairs?

On the SAME curated Dede near-zero-singles pocket, reframe the readout from continuous-MAE regression to binary DETECTION /
RANKING: does ANY constituent readout rank the high-|zdLFC| (synthetic-lethal) pairs ABOVE the neutral pairs on HELD-OUT novel
pairs, materially above chance AND above the honest degree/popularity floor?

## Load-bearing structural fact (drives design; the LEADING expected outcome)

The parent's landed pocket is a NEAR-MATCHING: `n_curated=360` pairs across `n_tok_curated=704` genes -> avg gene pocket-degree
= 2*360/704 = **1.023** (MEASURED@ parent metrics; also `seen_cur_n=0` -> every pocket pair is unique -> every query pair is
NOVEL). A constituent-IDENTITY readout can only generalize to a NOVEL pair if BOTH genes RECUR in training pairs; at degree ~1
they do not, so ANY constituent method sits at chance for a TRIVIAL STRUCTURAL reason (NOT genuine-null, NOT harness-mismatch).
The cell therefore MEASURES the exact learnable sub-pocket (pairs whose both genes have pocket-degree >= MIN_DEG) and separates
STRUCTURAL_UNDERPOWER from the two substantive verdicts. Designed to REFUTE cleanly.

## Task / method

- CONSTITUENTS-ONLY binary detection from the two gene identities/codes; held out on NOVEL pairs (stratified split reserves
  before fitting; the label never enters the features -> no leakage). Arms REGRESS the 0/1 SL label on pocket-SEEN pairs, score
  = predicted SL-propensity on scorable-NOVEL pairs (both genes must appear in a training pair; untrained-gene pairs excluded).
- METRIC: ROC-AUC (Mann-Whitney rank-sum) + AUPRC (class imbalance) + precision@k. Headline = the DEGREE-MATCHED novel ROC-AUC.
- Multi-seed (8 full / 3 smoke); per-seed AUC then mean (multi-seed discipline: if mean AUC within 0.05 of chance -> not HP).

### Label source
- PRIMARY: Dede MOESM3 per-pair zdLFC (z-normalized dLFC, replicate-pooled, 3 cell lines) joined to pocket pairs by canonical
  gene-symbol key; SL positive if mean zdLFC <= -Z_SL (Z_SL=3.0 = Dede's published SL call; one-sided -- lethality is the
  depleted tail). The published zdLFC is a cleaner, INDEPENDENT label than our from-scratch CPM-DMF, so a detection win cannot
  be dismissed as thresholding our own noise. Requires the parser to expose token->symbol (added via `_parse_dede_syms`, a
  FAITHFUL copy of parent parse_dede_encas12a @651030f7e so the pocket is IDENTICAL; the parent is not edited -- module-2 lock).
- FALLBACK (MOESM3 absent or pocket join coverage < MIN_JOIN_FRAC=0.5): DMF robust-z within pocket (SL if z <= -Z_SL). In the
  near-zero-singles pocket both SMFs ~0, so DMF ~= the pairwise interaction and DMF-z <= -3 is the in-pocket SL equivalent.
- Label source USED is reported. Arms regress the binary label (features = codes) -> no circularity with either label.

### Arms (detection score; higher => more-SL)
`LEARN_SYM` (shared code + elementwise PRODUCT = substrate symmetric bind; pairwise-capable) ; `LEARN_ADD` (shared code + SUM =
per-gene additive main-effects) ; `ADD_RIDGE` (closed-form ridge on per-token count design = STRONG additive) ; `LEARN_ROLE`
(role-keyed product; asymmetric contrast) ; `DEGREE` (deg[a]+deg[b] marginal popularity = the honest floor; NO label info) ;
`CHANCE` (random) ; `MEMORIZE` (per-pair mean label -> constant base rate on novel -> ~0.5). best_constituent = max over
{SYM, ADD, ADD_RIDGE, ROLE}. In a near-zero-singles pocket the additive arms have no pairwise term (both SMFs ~0), so a
SYM-over-additive gap localizes an irreducibly-pairwise SL signal.

### Controls (must fire before real interpretation)
- POS: planted RECURRENT low-rank pocket (SL = threshold of u_a.u_b, rank 3 << EMB_D=32) -> best_constituent AUC >= POS_CTRL_AUC
  (0.90). Proves the detection readout CAN detect when a learnable signal exists AND genes recur.
- SCRAMBLE: real (planted) labels permuted -> MEAN constituent AUC in [SCRAMBLE_AUC_LO, HI]=[0.40,0.60] (mean, not max-of-4,
  is the stable-under-null statistic).
- DEGREE-MATCHED: evaluate on positives + degree-matched-subsampled negatives so marginal-popularity guessing carries NO AUC
  advantage. Validated on a heterogeneous-degree degree-confounded plant: raw DEGREE AUC >= 0.56 and degree-matched DEGREE AUC
  <= DEGREE_MATCHED_CEIL (0.58) and (raw - matched) >= 0.05. The HEADLINE real AUC is on the degree-matched eval.

## Pre-registered bands (fixed BEFORE running)

- `Z_SL=3.0`, `MIN_JOIN_FRAC=0.5`, `MIN_POCKET=50`, `MIN_DEG=2`, `MIN_LEARNABLE=40`, `MIN_POS_NOVEL=8`, `AUC_HP=0.65`,
  `MARGIN_OVER_DEGREE=0.10`, `AUC_NULL_CEIL=0.55`, `DEGREE_MATCHED_CEIL=0.58`, `POS_CTRL_AUC=0.90`,
  `SCRAMBLE_AUC in [0.40,0.60]`, `K_TOPK=10`, `QFRAC=0.40`, seeds full=(7,13,17,23,29,31,37,41) smoke=(7,13,17).

- **HARD_PASS_HARNESS_MISMATCH_SL_DETECTABLE**: learnable sub-pocket >= MIN_LEARNABLE AND scorable-novel positives >=
  MIN_POS_NOVEL AND controls fire AND best_constituent degree-matched novel AUC >= AUC_HP (0.65) AND (best_constituent AUC -
  degree-matched DEGREE AUC) >= MARGIN_OVER_DEGREE (0.10). => the reframe is ALIVE; SL IS detectable from constituents.
- **HARD_FAIL_GENUINE_NULL_SL_NOT_DETECTABLE**: learnable + power adequate AND controls fire AND best_constituent AUC <=
  AUC_NULL_CEIL (0.55) AND not above the degree floor by the margin. => genuine null; escalate to higher-N or drop.
- **STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR**: learnable sub-pocket < MIN_LEARNABLE (or scorable-novel positives < MIN_POS_NOVEL,
  or too few valid folds). => the reframe is UNTESTABLE on this near-matching pocket; escalate to a COMBINATORIAL screen where
  each gene is crossed against many partners (Horlbeck GSE / Perturb-seq all-by-all / harmonized compendium).
- **HARD_FAIL_UNDERPOWERED_POCKET_N**: near-zero-singles pocket < MIN_POCKET pairs (directional-only).
- **INCONCLUSIVE_CONTROL_GATE_INVALID**: pos/scramble/degree-match controls do not fire -> machinery invalid.
- **MIDDLE_BAND**: best_constituent AUC in (0.55, 0.65) or above chance but not above the degree floor by the margin.
- **ACQUIRE_FAILED / ESCALATE_NEED_RAW_CONSTITUENTS**: MOESM4 download or SMF-constituent parse failure.

### HONEST expected-outcome note (deflated; not a prediction that drives the verdict)
Given the parent's on-disk avg gene pocket-degree = 1.023 and readable_rel~0.004, the LEADING expected outcome is
STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR (constituent identity cannot generalize with no gene recurrence). The learnable-sub-pocket
SIZE and whether the higher-SNR published zdLFC reveals recurring SL structure are UNKNOWN from the average alone and require the
data (remote run) -- this is why the cell is a genuine measurement, not busy-work. If a learnable sub-pocket exists and shows
AUC>>0.5, that is the harness-mismatch win. Either way the verdict is decisive and honest.

## Compute architecture
- Class **(b) sequential-CPU with justification**: pocket is O(1e2) native gene-pairs x tiny (<=Nx32) Adam fits (ms each) +
  numpy solves + rank-sum AUCs; GPU yields no speedup on sub-ms matmuls; dominant cost = the (~1.5MB) MOESM4 + (~13KB) MOESM3
  download (cached after first run). torch thread-capped (HDI_TORCH_THREADS, default 2).
- Storage: `no_storage` / `no_composition` (single-hop readout).

## SCHEMA-VET fields
- `cardinality_ok`: true. `EXPECTED_N_UNITS` = n_seeds detection folds; detect_run counts len(valid folds); power/structural
  gates fire on low counts; controls report per-seed detail.
- `arms_differ_verified`: true (self-test hashes per-arm detection scores on the planted pocket; SYM/ADD/ADDR/ROLE/DEGREE differ).
- `final_metrics_atomicity`: `tmp_replace` (single-shot; metrics.json.tmp -> os.replace).
- `crlb_n/a`: detection ROC-AUC has no closed-form CRLB for the bilinear-readout arm; the pre-registered AUC>=0.65 + margin-over-
  degree + degree-matched-neutralization + scramble/pos controls substitute for a capacity-feasibility cap.
- `discriminator_reachability`: true. AUC_HP=0.65 is achievable (self-test POS control best_constituent AUC ~1.0 at plant scale)
  and strictly above chance (0.5) by 0.15 with a required 0.10 margin over the degree floor.
- `baseline_in_band`: DEGREE/CHANCE floors ~0.5 on the degree-matched eval (self-test asserts DEGREE neutralization; CHANCE and
  MEMORIZE are ~0.5 sanity contrasts).
- `discriminator survives scale`: self-test fires (a) POS best_constituent AUC ~1.0 on a planted RECURRENT low-rank pocket at
  plant scale, (b) SCRAMBLE mean-constituent AUC ~0.5, (c) degree-matched neutralizes a planted degree<->SL confound (raw DEGREE
  AUC beats chance -> matched DEGREE AUC ~0.5). Real discriminator = degree-matched best_constituent AUC vs 0.65 + margin.
- `HP_SCOPE`: HARD_PASS gates apply to best_constituent (SYM/ADD/ADD_RIDGE/ROLE) vs the degree-matched DEGREE floor only;
  CHANCE/MEMORIZE are ~0.5 sanity contrasts.
- `calibration_check`: `adaptive_with_discriminator_gate` -- units-adaptive near-zero-singles band (reused from parent) + the
  STRUCTURAL learnable gate + the degree-matched neutralization are the discriminator-still-fires verifications; MIN_LEARNABLE /
  MIN_POS_NOVEL are the insufficient-power guards; self-test fires POS/SCRAMBLE/degree-match on planted pockets and rejects a
  broken label.
- Gate A (`sweep_alignment_verdict`): ALIGNED / n/a (no nominal-vs-effective sweep axis; the "axis" is real-data structure).
- Gate B (`discriminating_fraction`): n/a (not a parameter sweep; discriminator is the real-vs-planted AUC contrast, validated
  by the controls firing on planted arenas).
- Gate C (`composition_edges`): SHAPE_MATCH (gene-codes -> product/sum -> linear readout; single-hop, no primitive->primitive
  adapter needed).
- Gate D (`positive_control_arms`): POS control = planted low-rank recurrent pocket; best_constituent AUC >= 0.90 reproduces the
  detection readout AT plant scale (self-test check `pos_ctrl_best_constituent_detects`).
- Gate E (`functional_requirements`): (1) detect SL minority from constituents on novel pairs -> LEARN_SYM/LEARN_ADD/ADD_RIDGE;
  (2) neutralize popularity confound -> degree-matched negatives; (3) certify machinery -> POS/SCRAMBLE controls; (4) certify
  testability -> learnable-sub-pocket structural gate.
- Gate F (`real_code_path_and_signature_preflight`): F.1 self-test runs a synthetic Dede MOESM4 (parent fixture) through the
  REAL `_parse_dede_syms` + a synthetic MOESM3 through the REAL `parse_zdlfc_moesm3` + the REAL `detect_run` (arms via parent
  `_train_reg`/`arm_add_ridge`) + `roc_auc`/`average_precision`/`degree_matched_negatives`; hd_bind exercised on complex64
  phasors. F.2/F.3: reuses parent BASE signatures (`_train_reg(Xtr,ytr,Xq,mode,seed,n_tok)`, `arm_add_ridge(Xtr,ytr,Xq,n_tok)`)
  verified by import-resolution locally. F.4: n/a (no control-beats-POP break-guard). F.5: `deterministic_seeding: true` --
  fixed int seeds + numpy default_rng(seed*prime) + sorted-set ordering; PROT-023 static source scan verified CLEAN locally.
- `cell_chunked`: false (single-seed-axis handled in one cell; the seed axis is cheap detection folds, not multi-seed heavy runs).
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED metrics.json + traceback; SystemExit
  raised before Exception). `heartbeat_present`: per-seed + per-control flush(True) log lines (cell < 15min; full heartbeat helper
  not required). `defensive_error_checking`: `passed_all_4_patterns` (start-marker, crash-diagnostic, per-unit failure-class
  verdicts, progress logging).
- `run_mode`: default (no flag) = FULL run to completion; `--smoke` = 3 seeds; `--self-test` = the gate (remote). Post-dispatch
  RUN_MODE verification: expect `run_mode=full`.
- `progress_logging`: `print_flush_true` (ACQUIRE + per-seed detect + per-control lines, all flush=True; timeout_s=1800).

## Determinism / hazards
- FIXED int seeds; numpy default_rng(seed*prime); sorted-set token ids + deterministic stratified split. No salted-hash-seeded
  RNG, no set-to-list dedupe ordering (PROT-023 static source scan clean).
- ALL COMPUTE REMOTE. Author + trivial static import check locally only (importlib exec_module; PROT-023 scan). The remote
  `--self-test` is the gate; NO local smoke/measurement.
