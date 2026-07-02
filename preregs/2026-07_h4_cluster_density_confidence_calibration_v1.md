# Prereg: h4_cluster_density_confidence_calibration_v1

## Anchor
h4_cluster_density_confidence_calibration_v1

## Routing
Batch H4 (G8 anchoring-contamination rescue). CPU.

## Queue
remote_cpu_queue

## Purpose
Sonnet failure-taxonomy drill 2026-07-02 flagged this as HIGHEST-LEVERAGE CHEAP CELL among 9 conversational failure modes.
Confidence calibration is load-bearing for M3 cortex: substrate needs to KNOW when its retrieval is uncertain so cortex
can route to CLARIFY / refuse-gate / re-query. This cell measures whether an observable per-query cluster_density_score
(mean positive-cosine of KB against the query) predicts contamination on a G8-equivalent clustered KB. Ship-target is a
client-facing `propagation_risk` flag.

## Envelope-fail-bands (META_RULE_L: strict >= floor+5%)
- HARD_PASS: mean risk_auc >= 0.75 (ship as propagation_risk flag)
- MIDDLE_BAND: 0.60 <= mean risk_auc < 0.75 (partially predictive; needs refinement)
- HARD_FAIL: mean risk_auc < 0.60 (density-score not predictive; abandon this signal)
Band-width HP-vs-MB = 0.15 -> 5% strict floor = 0.7575 (cell uses >=0.75; MB-adjacent HPs flagged as MIDDLE_BAND per §L).

## Discriminator (META_RULE_K: fires-check)
Class = SELECTIVITY (score should separate contaminated queries from clean queries). AUC != 0.5 fires the discriminator.
Smoke asserts positive-arm AUC > 0.55 as fires-check (below is trivial-random).

## Baseline-in-band (META_RULE_AG)
No adversarial baseline arm; the discriminator IS the AUC of the single density-score. Positive-control = query set
constructed with known contamination structure (positives = queries near target cluster where false_fact is planted).
`baseline_in_band` interpretation: AUC in (0.5, 1.0) exclusive; smoke rejects AUC == 1.0 (by-construction saturation)
and AUC ~ 0.5 (no signal from planted false_fact).

## Compute architecture (USER-LOCKED 2026-07-02)
Class: **(b) sequential-CPU with justification**.
Justification: cell iterates N_Q=200 queries per seed, 3 seeds. Per query: one (M=3601, N=8192) @ (N=8192,) matvec
(~30M FLOPs) + one argsort of 3601 elements. Total per seed ~ 3600 x 200 = ~7.2E11 FLOPs matvec + 200 argsorts of 3601.
Wall-time estimate: ~5-15s per seed on numpy CPU; total per cell ~15-45s. Substantially below 10s per-phase-point
batching threshold — no material speedup from GPU batching. GPU startup cost (~1s cuda-init) would dominate. Sequential
numpy is correct choice.
Wall-time sanity: single-seed smoke on N=2048, N_CLUST=20, PER=30, N_Q=60 -> ~1-3s. Confirmed appropriate.

## CRLB / capacity-feasibility (META_RULE_L §9)
crlb_n/a: AUC is a rank-statistic over 400 queries (200 pos + 200 neg) per seed; not noise-floor-limited by
Cramer-Rao. AUC floor determined by mutual information between cluster-density score and contamination event,
which is empirical property of clustered-KB geometry. Discriminator-reachability: HP threshold 0.75 is achievable in
principle (density-score is theoretically well-correlated with false_fact leakage since both scale with intra-cluster
cosine INTRA_COS=0.6).

## Arms-must-differ (META_RULE_AF)
arms_differ_verified: n/a — cell has NO parallel arms (single density-score per query per seed). Only across-seed
variation. Exempt.

## Final-metrics atomicity (META_RULE_AH)
final_metrics_atomicity: `tmp_replace` (uses `experiments/_seed_checkpoint.write_metrics` which writes tmp+os.replace).

## Except-SystemExit ordering (§8)
Cell does NOT wrap `main()` in outer try/except. main() logic is top-level (no `def main()`). Selftest raises via
`sys.exit(0)` when `--self-test` passed. No `except BaseException:` anywhere. No bare `except:` — the two `except
Exception:` blocks (stdout.reconfigure fallback; auc_of empty-set guard) are narrow and don't swallow SystemExit.

## Cardinality (META_RULE_H)
No sweep axis. n_seeds=3 (SEEDS=[7,17,23]) at FULL; expected_n_units=3. `cardinality_ok`: n/a for non-sweep.

## Discriminating-fraction (Gate B)
Single-point regime, not a sweep. `discriminating_fraction`: n/a.

## Sweep-alignment (Gate A)
No sweep. n/a.

## Composition-edges (Gate C)
No primitive composition. Cell computes ad-hoc cluster-density metric directly from KB cosine geometry. n/a.

## Positive-control (Gate D)
No cited chain-grade primitive being reproduced. Novel discriminator. n/a.

## Functional-requirements (Gate E)
1. Substrate must expose an OBSERVABLE per-query signal (no oracle knowledge; only KB cosines).
   Cell impl: `((kb_aug @ q).clip(0)).mean()` — mean positive cosine of query against augmented KB. Fully observable.
2. Signal must correlate with CONTAMINATION risk (top-K retrieval contains planted false_fact).
   Cell impl: AUC of normalized density-score vs binary contamination label.

## Defensive-error-checking (§13)
- cell_chunked: False (single-file; 3 seeds in-cell; per-seed loop is <1s each, runner-death loses at most 1 seed)
- start_marker_written: False (cell is <30s total; low value)
- crash_diagnostic_present: False (no outer try/except; short cell)
- heartbeat_present: False (cell is <30s; heartbeat unnecessary)
- defensive_error_checking: "exempt_short_cell (<60s total wall)"

## Progress-logging (§17)
progress_logging: `print_flush_true` — every `print()` uses `flush=True`. Runner also invokes with `python -u`.
timeout_s target 300 (well below 1800 threshold; still flush-true throughout).

## Calibration-check (META_RULE_M)
calibration_check: `default_ok_for_this_regime` — INTRA_COS=0.6 is a standard clustered-KB regime (matches other
substrate cluster cells including anisotropy/entity-cluster experiments). No adaptive tuning; discriminator threshold
0.75 declared a priori.

## Timeout
Smoke: 60s. FULL: 300s (per-seed ~15-45s x 3 seeds + 10s buffer).

## Prior-work check
Substrate-KB concept query "confidence calibration cluster density conformal isotonic" returned:
- Rank 1-2: this cell's own prereg (cosine 0.57)
- Rank 3: "Confidence calibration" from anisotropy_drill_1 (cosine 0.49; different topic — anisotropy geometry, not
  contamination prediction)
- Rank 5: BATCH_H_authorized note (cosine 0.46; original H-batch authorization from 2026-06-07)
No prior arc collision at cosine > 0.30 for a distinct cell. Genuinely novel: this is a NEW observable-signal cell
targeting M3 cortex confidence routing.

## Selftest formulas (PROT-022)
1. `intra_cosine_high`: mean pairwise cosine within cluster > 0.3 (with INTRA_COS=0.6, expected ~0.36)
2. `auc_bounds`: auc_of on perfect separation returns 1.0
3. `deps`: numpy import + rng seed reproducibility (implicit)
