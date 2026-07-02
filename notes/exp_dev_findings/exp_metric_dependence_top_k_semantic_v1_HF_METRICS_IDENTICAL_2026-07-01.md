# HF_METRICS_IDENTICAL Hand-Off — metric_dependence_top_k_semantic_v1 (Dim S)

**Filed:** 2026-07-01
**Cell-author:** hdi_exp_dev
**Director decision:** HALT_ATOMIZE (do NOT dispatch full)
**Anchor:** `metric_dependence_top_k_semantic_v1`
**Commit:** `60ef3279` (cell files + prereg landed)
**Discipline halt reason:** META_RULE_AG (baseline-in-band) + DISCRIMINATOR-MUST-SURVIVE-SCALE — correctly halted at smoke gate before burning ~3-6 CPU-hr on saturated-substrate full dispatch.

## Verdict + Physics Finding

**Verdict:** `HARD_FAIL` (smoke; interpreted by Director as valid HF substrate physics finding, atomize as measured null).

**verdict_msg** (from `data/exp_metric_dependence_top_k_semantic_v1_seed_7_smoke/metrics.json`):

> `HF_METRICS_IDENTICAL: metric-axis flat; top10-top1@0.20=+0.000(HP>=0.15) cos05-top1@0.20=+0.000(HP>=0.20) max_spread=0.000 top1@0.30=1.000 top50@0.30=1.000`

**Measured (all MEASURED@`d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v1_seed_7_smoke/metrics.json`):**

| alpha | M    | top1  | top5  | top10 | top50 | cos>=0.5 | cos>=0.8 | beta  | wall_s |
|-------|------|-------|-------|-------|-------|----------|----------|-------|--------|
| 0.10  | 819  | 1.000 | 1.000 | 1.000 | 1.000 | 1.000    | 1.000    | 10.14 | 15.9   |
| 0.20  | 1638 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000    | 1.000    | 11.19 | 26.9   |
| 0.30  | 2458 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000    | 1.000    | 11.81 | 12.3   |
| 0.30 preview | 2458 | 1.000 | (as above) | | | | | | 8.3 |

**Wall-probe extension (out-of-prereg diagnostic; wall_probe MEASURED direct-Python invocation, dir cleaned):**

| alpha | M       | metrics                | wall_s |
|-------|---------|------------------------|--------|
| 0.50  | 4096    | all 1.000              | 20.1   |
| 1.00  | 8192    | all 1.000              | 46.6   |
| 2.00  | 16384   | all 1.000              | 111.1  |
| 4.00  | 32768   | all 1.000              | 152.0  |
| 8.00  | 65536   | all 1.000              | 240.3  |
| 16.00 | 131072  | NaN (OOM at 8.6 GB attn matrix) | 279.5 |

## Physics Reading

**Metric-axis flat because substrate is in the UNDERLOADED regime.** Cell D v2 dense-Hopfield READ-REPLACE with adaptive-beta softmax attention has **exponential capacity in N** (Krotov-Hopfield 2016 / Ramsauer 2020 "Hopfield networks is all you need"). At N_c=8192 with bipolar-iid keys and adaptive beta ~ log2(M)/margin, the substrate stores AT LEAST 8x N (65k patterns) with perfect recall on the 6-metric family.

**In this regime the 6 metrics collapse to one number because the readout `p_n` is essentially equal to `V[target]`.** When readout is (near-)perfect:
- argmax hits target -> top1 = 1
- target is trivially in top-K for any K >= 1 -> top5/10/50 = 1
- sim(p_n, V[target]) ~= 1 >= 0.8 -> cos05 = cos08 = 1

The 6-metric spread is a function of readout DEGRADATION. In an underloaded regime there is no degradation to differentiate.

**Metric-dependence hypothesis (Dim S, P_deflated=0.45) is FALSIFIED for THIS mechanism-class at THIS regime.** Dense-Hopfield READ-REPLACE at N=8192 with iid keys shows no metric-axis structure below the interference wall.

## Hidden-Dim References

- **Dim S (this cell):** `d:/AI/hd-instrument/notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S (P_deflated=0.45; top-1 vs top-K vs semantic-similarity vs downstream-task-quality). Prediction that different metrics reveal different capacity boundaries falsified at underloaded dense-Hopfield.
- **Dim H (twin HF today):** `d:/AI/hd-instrument/notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim H (P_deflated=0.38; distributional-shape power-law vs uniform). Director notes twin falsification at underloaded dense-Hopfield today; same physics regime.
- **Sparse-coding / AMP hard-phase drill (needed for v2 regime respec):** `d:/AI/hd-instrument/notes/research_sparse_coding_compressed_sensing_2026-07-01.md`. The Amit-Gutfreund / AMP hard-phase prediction is that metric-differentiation bites in the INTERFERENCE-EXPLOSION regime above the substrate's storage-capacity wall (over-Amit-Gutfreund). Under-Amit-Gutfreund all readout metrics report the same number.

## Convergent Meta-Finding

**Twin HF today (Dim H + Dim S) both falsify at underloaded dense-Hopfield.** Cell D v2 architecture at N=8192, alpha<=0.30 is so noise/skew/metric robust that discriminator-heavy Dim-X tests need to push INTO the interference regime to elicit differentiation.

**Load-bearing for M3 architecture:**
- **Positive:** substrate is enormously robust in its designed operating regime; expected M3 workloads (M/N well below 1.0) will exhibit uniform recall quality across metric choices; no need to worry about metric-axis pathology in cortex layer.
- **Negative:** harder to elicit CG discrimination in Stage 1 base — sweeps designed at "reasonable" M/N loads will saturate and produce null-findings. Discriminator-heavy tests must be dispatched at over-Amit-Gutfreund loads OR use degraded queries.

## Recommended v2 Regime Respec

**Suggested pre-reg slug:** `metric_dependence_top_k_semantic_v2_overload_sweep`

**v2 arm expansion:** push loads INTO overload where top-1 collapses but top-K may survive (canonical metric-differentiation prediction):

- alpha in {0.5, 1.0, 1.5} at N_c=8192 (M in {4096, 8192, 12288}).
- Note: probe showed alpha=0.5-1.0 still saturates at 1.000 with adaptive beta and iid keys. May need to ALSO:
  - **Add query noise** (e.g., query with `keys[i] + 0.3-1.0*randn`; sweep noise sigma). Real M3 queries are noisy.
  - OR **correlated keys** (low-rank + noise). Interference explodes near-target.
  - OR **fix beta below adaptive value** (e.g., beta=8.0 minimum floor; forces harder attention that degrades under load).
- Alternative: skip Cell D v2 primitive entirely and use CLASSICAL Hopfield (no softmax; storage rule = sum-of-outer-products) at alpha above 0.14 wall to guarantee interference regime; but this loses the "same primitive family" property that made Dim S CG-relevant.

**Follow-up questions for Research:**
1. Is Dim S question about "which mechanism-class shows metric-axis structure" (test multiple substrate variants including classical Hopfield) OR "at what regime does dense-Hopfield metric-axis emerge" (single primitive, sweep into overload)?
2. Should v2 hold N_c fixed at 8192 and push M, or also sweep N_c to find "the capacity wall as a function of N" to cite AMP theory prediction?
3. Are the six metrics `{top1, top5, top10, top50, cos>=0.5, cos>=0.8}` the right family, or should we add downstream-task-quality (e.g., compositional-recall accuracy, refuse-gate margin) that is closer to M3 workload?

## Files (absolute paths)

- Cell + prereg (this atomization): `d:/AI/hd-instrument/experiments/_substrate_metric_dependence_top_k_semantic_v1_core.py` + `exp_metric_dependence_top_k_semantic_v1_seed_{7,13,19}.py` + `preregs/2026-07-01_metric_dependence_top_k_semantic_v1.md`
- Smoke landing: `d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v1_seed_7_smoke/metrics.json` (HARD_FAIL_metric_axis_flat)
- Dim S source: `d:/AI/hd-instrument/notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`
- Sparse-coding / AMP source: `d:/AI/hd-instrument/notes/research_sparse_coding_compressed_sensing_2026-07-01.md`

## Atomization Guidance for Store

**Atom-class:** substrate-physics-null (measured HF).
**Atom-key concept:** "dense-Hopfield READ-REPLACE at N=8192 underloaded regime: 6-metric family (top1/5/10/50, cos>=0.5, cos>=0.8) collapses to single number 1.000 across load alpha in [0.10, 8.0]. Metric-dependence hypothesis (Dim S P_def=0.45) falsified for this mechanism-class at underloaded regime. Above interference wall (alpha > 8.0 at N=8192, adaptive beta) computation OOMs at ~131k items; interference-regime remains untested."
**Chain-grade elevation:** NONE (measured null; not chain-grade).
**Meta-tag:** convergent-with-Dim-H-falsification-2026-07-01 (twin HF at underloaded dense-Hopfield same day).
**Downstream implication:** Any Dim-X (X in {S, H, and possibly others}) sweep on this substrate class needs regime-check gate BEFORE full dispatch — either push into overload OR use degraded queries OR switch to classical-Hopfield primitive.
