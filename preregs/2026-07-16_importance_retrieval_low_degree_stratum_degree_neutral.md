# Pre-reg: importance -> retrieval-relevance WITHIN the low-degree periphery stratum, DEGREE-NEUTRAL

- **Anchor:** `importance_retrieval_low_degree_stratum_degree_neutral_real_codex_v1`
- **Cell:** `experiments/exp_importance_retrieval_low_degree_stratum_degree_neutral_real_codex_v1.py`
- **Date:** 2026-07-16
- **Class:** local CPU single-shot run-to-completion (structural re-score; NOT a queue dispatch). Compute-proportional: a directional/correlation question answered by cheapest decisive method (re-score already-fitted betweenness) -- not a training fit.

## Question (the decisive close on the 4th axis / importance for our substrate)
The pooled importance->retrieval test HARD_FAILED (pc_btwn=0.100, tert_btwn=0.035) but the per-degree-bin
breakdown showed a SIGN-FLIP: the lowest-degree quartile (bin0, n=718) gave a top-vs-bottom-importance
appearance-gap of +0.335 while higher bins reversed, cancelling to ~0 pooled. Does importance predict
retrieval-relevance AMONG the low-degree periphery stratum, DEGREE-NEUTRAL WITHIN the stratum (is the
+0.335 a residual-degree artifact INSIDE the low-degree bin, or a genuine stratified periphery signal)?

## Dataset honesty note
CoDEx-claimvalidity is a filtered/dense KG: MINIMUM entity degree = 10. The "low-degree periphery"
stratum = the RELATIVELY lowest-degree quartile (train degrees 10-15), NOT absolute-sparse deg 1-3. The
classical-IR "bridges among sparse entities" intuition is tested on the lowest-degree stratum available.

## Stratum definition (principled, NOT tuned-to-pass)
PRIMARY stratum = bin0 of the pre-existing quantile-of-log1p(degree) scheme at n_bins=4 (identical to the
parent cell's bin0 where +0.335 lives). Robustness: bin0 at n_bins in {3 (tertile), 5 (quintile)}.

## Degree-neutralization WITHIN the stratum (the load-bearing control)
- PART A (PRIMARY): within-stratum partial rank-corr(betweenness, tqc | [log_deg, log_inc]) over stratum
  entities only -> residual within-stratum degree + incidence controlled directly.
- PART B: EXACT-degree-matched tertile gap -- within each exact degree value (deg==11, 12, 13, 14, 15
  groups of >= MIN_DEG_GROUP=12), top-vs-bottom within-stratum-re-orthogonalized-importance tertile
  appearance gap, size-weighted. Exact-degree matching = perfect within-stratum degree neutralization.
- PART C (diagnostic): raw non-degree-matched within-stratum tertile on the GLOBALLY-orthogonalized
  importance -> reproduces the reported +0.335; the delta vs PART B = the residual-degree artifact.

## Arms
importance (within-stratum re-orthogonalized betweenness) vs degree-matched-scramble control (permute
importance WITHIN each exact-degree group) vs full-random null. arms_differ hash-checked (META_RULE_AF).

## Info-ceiling gate (FIRST, mandatory)
(a) stratum appearance rate in (0.05, 0.98); (b) stratum tqc variance > 0; (c) n_stratum >= 100;
(d) |spearman(log_deg, tqc)| >= 0.10 within stratum (degree carries target-relevant structure, sign-
agnostic -> the degree-neutral test is meaningful). Any fail -> VACUOUS.

## Metrics (separate; do not blob)
- PART A: pc (within-stratum partial corr), pc_boot_p05 (600 boots over stratum entities).
- PART B: tert (exact-degree-matched gap), tert_boot_p05, n_degree_groups_fired, per-group.
- PART C: raw_global_within_stratum_gap (should reproduce ~+0.335), degree_matched_gap (PART B).
- controls: scramble + random pc & tert (must be < 0.05).
- n_stratum (real, not noise).

## Bands (fixed a-priori)
- PC_HP=0.15, PC_HF=0.05 (within-stratum partial corr, PRIMARY).
- TERT_HP=0.15, TERT_HF=0.05 (exact-degree-matched tertile gap).
- NEUTRAL_CTRL_MAX=0.05 (scramble + random nulls).
- CEIL_DEG_PREDICTS_MIN=0.10.

## Verdicts
- **HARD_PASS** `IMPORTANCE_STRATIFIED_PERIPHERY_RETRIEVAL_SIGNAL`: info-ceiling PASS AND pc>=0.15 AND
  tert>=0.15 AND pc_boot_p05>0 AND tert_boot_p05>0 AND controls near-zero -> importance's CORRECT function
  = a STRATIFIED periphery-retrieval signal; pooled fail was a Simpson's-paradox / wrong-calc artifact;
  the +0.335 SURVIVES degree-neutralization. Role = periphery/sparse-entity retrieval prioritization.
- **HARD_FAIL** `IMPORTANCE_LOW_VALUE_PLUS0335_IS_WITHIN_STRATUM_DEGREE_ARTIFACT`: info-ceiling PASS AND
  NOT hard_pass AND (pc<0.05 OR tert<0.05) -> the +0.335 is a within-stratum residual-degree artifact /
  doesn't survive degree-neutralization -> importance is genuinely LOW-VALUE for our substrate (order,
  pooled-retrieval, stratified-retrieval all fail). HONEST + FINAL: the SEPARABILITY finding still stands
  as a real measured quantity; what closes is any predictive value for retrieval-priority beyond
  popularity. Do NOT manufacture a role.
- **MIDDLE_BAND**: info-ceiling PASS, controls clean, pc/tert between FAIL and PASS floors -> weak within-
  stratum periphery signal; route to heavier bounded-width variant before any capability claim.
- **BLOCK_BROKEN_DEGREE_CONTROL**: scramble/random null not near-zero (exact-degree grouping leaks).
- **VACUOUS_METRIC_INFO_CEILING_FAIL** / **HARD_FAIL_STRATUM_TOO_SMALL**: info-ceiling fails / n<100.

## Compute architecture
Sequential-CPU justified: structural graph algorithm (sampled Brandes betweenness) + rank statistics, not
matmul; the cell IS a structural measurement; wall < ~60s. Storage: no_storage / no_composition.
Determinism: numpy default_rng(fixed int seeds); no hash()-derived seeds; sorted() set ops.
final_metrics_atomicity: tmp_replace. crlb_n/a: parameter-free structural rank score, no noise floor.
calibration_check: default_ok_for_this_regime (thresholds pre-registered; raw held-out count target).
