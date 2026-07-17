# Pre-reg: importance / downstream-reach CORRECT function -- RETRIEVAL-RELEVANCE (not acquisition-order)

- **Cell:** `experiments/exp_importance_retrieval_relevance_query_centrality_real_codex_v1.py`
- **Anchor:** `importance_retrieval_relevance_query_centrality_real_codex_v1`
- **Date:** 2026-07-16
- **Compute:** local CPU, single-shot run-to-completion (NOT a queue dispatch). ~30s full.
- **Hand-off:** `notes/exp_dev_handoff_research_importance_retrieval_relevance_2026-07-16.md`
- **Drill:** `notes/research_importance_correct_function_retrieval_vs_active_learning_2026-07-16.md`

## Question
The prior cell (`exp_importance_downstream_reach_ingest_prioritization_real_codex_v1`, HARD_FAIL) tested
importance/downstream-reach as an ACQUISITION-ORDER signal -- it lost to random + frequency order (the
BatchBALD/coreset redundancy anti-pattern). Separability still held (`importance_btwn_unique_variance
=0.867`, `max_pop_corr=0.220`, SEPARABLE). This cell tests the UNTESTED correct function per the drill:
does a train-graph entity's IMPORTANCE (degree-orthogonalized node value-of-information) predict how
often it is NEEDED to answer HELD-OUT TEST QUERIES (retrieval-relevance / query-centrality), POPULARITY-
NEUTRAL (must beat degree-matched; must add beyond raw degree/frequency)?

## Operationalization
- **IMPORTANCE (per entity, train-graph-only, label-free):** PRIMARY `imp_btwn_orth` = degree-
  orthogonalized sampled VERTEX betweenness centrality (per-node analog of the prior cell's degree-
  decorrelated edge betweenness; 192 Brandes sources full). DIAG `imp_reach_orth` = degree-orthogonalized
  k-hop reachable-mass (hub-aligned; diagnostic only).
- **TARGET (per entity, held-out):** `test_query_count` (tqc) = appearances as head or tail across the
  n_test_pos=1828 held-out test positives (test.txt). test-appearance = (tqc>0). Robustness variant:
  test+valid positives combined.
- **POPULARITY CONTROLS:** log1p(train unique-neighbor degree), log1p(train incidence).
- Decision scalar **pc** = partial rank-correlation(imp_btwn_orth, tqc | [log_deg, log_inc]).
  **tert** = size-weighted degree-matched top-vs-bottom-importance-tertile test-appearance-rate gap.

## Info-ceiling gate (FIRST, mandatory)
Target must be non-vacuous: `CEIL_APPEAR_LO(0.05) < appearance_rate < CEIL_APPEAR_HI(0.98)` AND
`spearman(log_deg, tqc) >= CEIL_DEG_PREDICTS_MIN(0.10)` (degree resolves the target -- expected KGQA
popularity bias) AND tqc std > 0. If any fails -> VACUOUS.

## Pre-reg bands (FIXED a-priori)
- **HARD_PASS**: info-ceiling PASS AND `pc >= 0.15` AND `tert >= 0.15` AND `pc_boot_p05 > 0` AND
  `tert_boot_p05 > 0` AND degree-matched-scramble control near-zero (`pc_scramble < 0.05` AND
  `tert_scramble < 0.05`). => importance's correct function found = retrieval/attention relevance,
  popularity-neutral.
- **HARD_FAIL**: info-ceiling PASS AND NOT hard_pass AND (`pc < 0.05` OR `tert < 0.05`). => importance
  predicts retrieval no better than popularity (residualized corr null OR degree-matched arms show no
  separation) = predicts NEITHER acquisition-order NOR retrieval-relevance = genuinely low-value for our
  unbounded-store substrate. HONEST + IMPORTANT (follow-the-evidence): separability finding still stands;
  do NOT manufacture a role.
- **MIDDLE_BAND**: info-ceiling PASS AND real-but-modest (pc/tert between the FAIL and PASS floors) ->
  route to heavier bounded-width retrieval-ranking-accuracy v2.
- **BLOCK_BROKEN_DEGREE_CONTROL**: the degree-matched-scramble null is NOT near-zero (binning leaks) ->
  cannot trust PART B.
- **VACUOUS_METRIC**: info-ceiling FAIL.

## Deviation flag (per hand-off contract)
The research note labels the HARD-PASS 0.15 bar "partial R^2" but its MIDDLE band is "partial correlation
0.05-0.15" and its HARD-FAIL is "residualized correlation < 0.05". These are only mutually consistent if
the decision scalar is the PARTIAL (residualized) CORRELATION on a 0.05/0.15 scale (a partial-R^2 of 0.15
would be corr ~0.39, inconsistent with the same-note MIDDLE upper edge). This cell adopts that consistent
reading: primary scalar = partial rank-correlation, bands PC_HF=0.05 / PC_HP=0.15; incremental rank-R^2
reported as a companion, not the gate. Faithful reconciliation, not a loosening.

## Discipline
Determinism (fixed int seeds, sorted set ops, no hash()-seeds); ASCII-only; atomic tmp+os.replace;
except SystemExit-first; arms-differ; hardened self-test constructs the REAL loader + real node-
betweenness path and asserts the info-ceiling on real CoDEx. Degree-matched-scramble + full-shuffle null
controls must fire (~0). No queue/GPU/atoms/push.

## RESULT (MEASURED@data/exp_importance_retrieval_relevance_query_centrality_real_codex_v1/metrics.json)
- run_mode=full, elapsed 29.4s. info-ceiling PASS (appear=0.683, deg_predicts_tqc=0.317).
- PART A pc_btwn=0.1004 (p05=+0.069, incrR2=0.0089) -- MIDDLE-ish but weak. pc_reach_diag=-0.1016.
- PART B tert_btwn=0.0355 (p05=-0.006, crosses zero); scramble(pc=0.012 tert=0.016) / random(pc=0.010
  tert=0.022) -> controls near-zero (fire correctly). Per-bin gap: bin0(low-deg)=+0.335 (n=239),
  bin1=-0.025, bin2=-0.148, bin3(hubs)=-0.185 -> sign FLIPS across degree strata, pools to ~0.
- **VERDICT: HARD_FAIL** (tert_btwn=0.0355 < TERT_HF=0.05 -> degree-matched arms show no separation).
- Honest read: importance predicts retrieval-relevance no better than popularity in the POOLED degree-
  neutral test, so it is a HARD_FAIL by the pre-registered bands -- importance is genuinely low-value as
  a single pooled retrieval-priority signal for this substrate. NUANCE (not over-read): a real, large
  periphery-bridge signal exists in the low-degree stratum (bin0 +0.335) but reverses among hubs -> a
  future STRATIFIED (low-degree-targeted) v2 could exploit it; as one pooled signal it does not survive.
