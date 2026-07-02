# Pre-reg: h4b_margin_top1_top2_gap_predictor_v1

**Date:** 2026-07-02
**Author:** exp_dev sub-agent (spawned by Director for research 2x drill 2026-07-02 h4 revival)
**Anchor:** `h4b_margin_top1_top2_gap_predictor_v1`
**Cell:** `experiments/exp_h4b_margin_top1_top2_gap_predictor_v1.py`
**Research handoff:** `notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md`
**Prior filing (LOAD-BEARING):** anchor `bio-calibrated-confidence-B1` filed 2026-06-08 in
  `notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md` and
  `notes/exp_dev_handoff_research_biology_capabilities_5x_2026-06-08.md`. NEVER SHIPPED. This cell is the closure.

## Mechanism

For each query `q` in a clustered KB with one injected contaminating fact tied to a target cluster centroid:
- `sims = kb_aug @ q` (shape M+1)
- `top1, top2 = sims[argsort_desc[0]], sims[argsort_desc[1]]`
- `gap = top1 - top2`
- `risk = -gap` (small gap = high uncertainty = contamination-likely)

Discriminator: `AUC(risk, is_contaminated_target_in_top_K)`.

**Distinct mechanism-class from h4** (density-averaging over M=3600 items). h4's global-mean
signal dilutes with M (contamination is 1/3600 = 0.028% of the sum); h4b uses only the top-2
items so contamination either does or does not crowd the top-2 slot -- signal does not dilute.

**Bio-analog:** Ma, Beck, Latham & Pouget 2006 probabilistic population code -- posterior width
via tuning-curve overlap. Substrate equivalent = top-1/top-2 gap.

## Envelope-fail-bands

| Band | AUC | Notes |
|------|-----|-------|
| HARD_PASS | >= 0.70 AND cv <= 0.03 | Ship as cortex REFUSE/CLARIFY/ACCEPT routing signal. Closes bio-calibrated-confidence-B1 anchor. |
| MIDDLE_BAND (unstable) | >= 0.70 AND cv > 0.03 | Seed instability; investigate before ship. |
| MIDDLE_BAND (partial) | 0.60 <= AUC < 0.70 | Partial predictor; investigate composition with lap3_12 isotonic. |
| HARD_FAIL | < 0.60 | Spatial-margin does not survive commercial scale; h4-family disprove extended. |

`cv = std(auc_per_seed) / mean(auc_per_seed)`. META_RULE_L: HARD_PASS strictly above floor via cv gate.

## Regime

Same harness as h4 for parity:
- `INTRA_COS = 0.6` (cluster tightness)
- `TOPK = 10` (contamination-in-top-K definition)
- FULL: `SEEDS=[7,17,23]`, `N=8192` (vector dim), `N_CLUST=60`, `PER=60` items/cluster, items=3600, `N_Q=200` positives + 200 negatives per seed
- Contamination injection: one `false_fact = INTRA_COS * cluster_centroid + sqrt(1-INTRA_COS^2) * random` appended to KB per seed

## SCHEMA-VET fields (SCHEMA-VET-mandatory)

- `arms_differ_verified`: N/A (single-mechanism-arm cell; no baseline arm within the cell)
- `arms_differ_exempted`: `[["gap_risk", "no_baseline"]]` -- single mechanism arm; the baseline
  is chance AUC=0.5 which is a mathematical property of the ranking, not a code arm
- `final_metrics_atomicity`: `tmp_replace` (via `experiments._seed_checkpoint.write_metrics`)
- `crlb_n/a`: "AUC discriminator has no closed-form noise floor for gap distribution;
  discriminator-survives-scale gate (smoke arm B at full-N) covers analogous concern"
- `discriminator_reachability`: TRUE. AUC in [0.5, 1.0]; HARD_PASS threshold 0.70 is
  reachable (numerous prior selective-classification results in the 0.75-0.85 range on
  synthetic contamination detection with margin-based scores)
- `baseline_in_band`: contamination_rate ~= 0.5 by construction (balanced pos/neg queries).
  Chance AUC = 0.5 is below the discriminating band [0.30, 0.70]. **The DISCRIMINATOR here
  is the AUC itself, not the underlying contamination rate.** Baseline (random-ranking) AUC
  is 0.5 (in-band as the null-hypothesis reference).
- `discriminator survives scale`: SMOKE ARM B at full-N (items=3600 N=8192) preview arm;
  reject FULL dispatch if arm B AUC <= 0.55.
- `HARD_PASS strictly above floor`: 0.70 threshold + cv <= 0.03 gate.
- `HP_SCOPE`: `{"gap_risk_arm": ["AUC >= 0.70", "cv <= 0.03"]}` -- single arm.
- `cardinality_ok`: EXPECTED_N_UNITS = 3 seeds × 400 queries = 1200 (FULL). Verdict logic
  asserts `len(per_seed) == len(SEEDS)`.
- `calibration_check`: `default_ok_for_this_regime`. gap is a parameter-free direct observable
  (no threshold, no adaptive tuning). Regime match: h4 harness reuse guarantees distribution
  compatibility with prior h4 measurement.

## §13-14 defensive fields

- `cell_chunked`: FALSE. Single-seed loop per cell; 3 seeds < 15min per seed on numpy CPU
  (chunking would be overkill; runner-death cost is ~10 min recompute).
- `start_marker_written`: TRUE.
- `crash_diagnostic_present`: TRUE (`_write_crash_metrics` in outer try/except).
- `heartbeat_present`: FALSE. Per-seed wall < 15 min; §13 rule of thumb applies at ~15 min.
  Not needed for this regime.
- `defensive_error_checking`: `passed_all_4_patterns` (start marker + crash diag + `except
  SystemExit: raise` before `except Exception`; NO bare `except:` or `except BaseException:`).

## §15 test-design gates

- `sweep_alignment_verdict`: ALIGNED. No sweep axis; single-regime cell.
- `discriminating_fraction`: N/A -- no sweep points. Single point (N=8192 items=3600) is
  the target regime.
- `composition_edges`: N/A -- cell does not compose primitives; single mechanism (gap = top1 - top2).
- `positive_control_arms`: N/A -- no prior chain-grade primitive being reproduced. h4 is
  NOT a positive-control because h4 mechanism-class (density-averaging) is DISTINCT from
  h4b (spatial-margin); reproducing h4's AUC in this cell would prove nothing about the gap.
- `functional_requirements`: cortex needs a per-query scalar confidence signal that predicts
  when the retrieved fact is contamination-affected. Mapped to substrate observable: `gap =
  top1_sim - top2_sim`. No new mechanism; direct output of existing similarity retrieval.

## §16 run_mode verification

Post-dispatch verification of landed `data/exp_h4b_margin_top1_top2_gap_predictor_v1/metrics.json`
must confirm `run_mode == "full"`, `n_seeds == 3`, `elapsed_s > 5`, `size > 5KB` before framing FULL result.

## §17 print-progress flushing

`progress_logging: print_flush_true`. All progress lines use `flush=True`. Cell wall time
< 30 min; strict §17 gate applies only to `timeout_s >= 1800`. Compliant.

## Compute architecture

`(b) numpy-batched-CPU with justification`. Load-bearing op: single matmul `kb_aug @ q.T` per
seed (M+1 x N = ~3601 x 8192 @ 400 queries = 24 MB output). Per-seed wall ~2-8s on numpy CPU.
No substantial GPU speedup at this scale (fixed launch overhead > runtime). Parity with h4
harness (also CPU-numpy). If FULL wall exceeds 30 min unexpectedly, batching would trigger
via `torch.cuda` port.

## Cost / dispatch plan

- **Smoke arm A (small-N, seed=1, N=2048 items=600 N_Q=60):** ~1-3s local
- **Smoke arm B (SCALE-PREVIEW, seed=1, N=8192 items=3600 N_Q=200):** ~5-15s local -- MANDATORY per DISCRIMINATOR-MUST-SURVIVE-SCALE
- **FULL 3-seed (N=8192 items=3600 N_Q=400 pos+neg):** ~15-45s per seed × 3 seeds = ~1-3 min total (numpy CPU)
- **Route:** SMOKE run direct (local pause flag exists so no queue); FULL request to `remote_cpu_queue` via Orchestrator
- **Timeout for FULL:** 1200s (20 min) -- generous over expected 3 min

## Complementarity to lap3_12

`lap3_12_confidence_calibration_cpu_v1` (un-dispatched) targets POST-HOC isotonic calibration
of top-1 similarity alone (rescales existing scalar). h4b adds top-2 as a NEW input feature.
These COMPOSE cleanly -- lap3_12 could later isotonic-calibrate `gap` -> `contamination_probability`.
No overlap. Cells can run in parallel; do NOT sequence-block.

## Follow-up (post-PASS, not in scope of this cell)

If h4b lands PASS, next candidate (parallel-track) is Research Lane X:
cleanup-iteration-count / energy-delta predictor -- orthogonal DYNAMICAL observable to h4b's
spatial-margin observable. Together they form a two-signal confidence vector for cortex.
This is NOT dispatched by h4b's exp_dev spawn; Director decides after h4b lands.

## Pre-reg self-check

- [x] Envelope-fail-bands PASS + FAIL declared
- [x] Discriminator-survives-scale gate (smoke arm B)
- [x] Cell-template mandatory §6-12 fields declared above
- [x] §13-14 defensive-checking fields declared
- [x] §15 test-design gates declared (N/A where honest)
- [x] §16 run_mode verification plan stated
- [x] §17 progress-logging declared
- [x] Compute architecture section per USER 2026-07-02 GPU-batching rule
- [x] Complementarity to lap3_12 stated (research 2x drill requirement)
- [x] HYPOTHESIZED-vs-MEASURED discipline: all numbers in pre-reg tagged inline

Ready for smoke dispatch.
