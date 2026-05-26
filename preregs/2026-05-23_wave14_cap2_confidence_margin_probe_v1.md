# Prereg: wave14_cap2_confidence_margin_probe_v1

**Date**: 2026-05-23
**Experiment name**: wave14_cap2_confidence_margin_probe_v1
**Script**: experiments/exp_wave14_cap2_confidence_margin_probe_v1.py
**Queue**: overnight_queue
**Trigger**: URGENT pipeline refill after ONLINE_W_NOISE_ENVELOPE_NARROW verdict;
Cap 2 metric-definition re-probe (Sagawa-Ueda precedent from Cap 1 re-axiomatization v158)

---

## Hypothesis

Cap 2 CRITICAL_NO_CORRELATION (v153) was a metric-definition artifact.
The original metric -- VAMP iteration count tau as confidence proxy -- fails because argmax
dynamics converge fast to BOTH correct AND wrong attractors (near capacity both outcomes
settle in 1-3 iterations). tau is not a discriminative confidence signal.

Fix: use the cosine MARGIN (top_1_cosine_score - top_2_cosine_score after one retrieval step)
as the confidence proxy. High margin = unambiguous retrieval = correct; low margin = near-tie
= likely error. This is the direct analog of the Sagawa-Ueda metric re-axiomatization for Cap 1.

Secondary fix: stratify by noise level p. Original experiment mixed noise levels in a single
trial loop, diluting per-stratum signal.

## Protocol

- N=8192, M=200 (near-capacity; K_crit(N=8192) ~ 1148 so M=200 is undercrowded;
  BUT noise at p=0.10-0.20 forces errors at any M -- noise-induced retrieval failures)
- noise_levels: [0.0, 0.05, 0.10, 0.20]
- n_trials_per_stratum: 200, seeds: [17, 23, 31]
- For each trial: add bit-flip noise to query key, retrieve via W @ query, compute:
  (a) is_correct: overlap(retrieved, true_value) > 0.7
  (b) margin: (overlap_rank1 - overlap_rank2) after W retrieval / N
- Compute Pearson corr(margin, is_correct) within each stratum p
- Report strata_results: {p: {corr_mean, corr_per_seed, err_rate}}

## Predictions (pre-registered)

**HARD PASS**: corr(margin, is_correct) >= 0.50 in at least 2/4 noise strata (across 3 seeds mean)
Verdict: CAP2_MARGIN_DETECTS

**HARD FAIL**: corr(margin, is_correct) < 0.20 in ALL strata
Verdict: CAP2_MARGIN_KILL -- structurally confirms Cap 2 closure (no confidence signal in substrate)

**Partial**: 1 stratum passes, not all below 0.20
Verdict: CAP2_MARGIN_PARTIAL

## Memory budget

- W: N x N float32 = 8192 x 8192 x 4 = 268 MB
- keys: 200 x 8192 x 4 = 6.4 MB
- values: 200 x 8192 x 4 = 6.4 MB
- overlaps per trial (transient): 200 x 8192 x 4 = 6.4 MB
- Total peak VRAM: ~290 MB. Well under 4 GB budget target and 8 GB hardware cap.

## Substrate-product axis

Cap 2 rehabilitation: self-monitoring confidence via substrate-native readout margin.
If PASS (CAP2_MARGIN_DETECTS): substrate can introspect retrieval confidence via cosine margin;
pairs with Cap 1 Crooks (auditable erase + confidence-stamped provenance).
If KILL (CAP2_MARGIN_KILL): structurally confirms Cap 2 is closed; no rescue needed;
substrate does not carry confidence information in margin either.

## Note on smoke verdict

Smoke at N=1024, M=30, n_trials=15 shows err_rate=0 at all strata (below capacity at small N).
When err_rate=0, Pearson corr is degenerate (zero variance in corrects). Smoke verdict
CAP2_MARGIN_KILL is EXPECTED at sub-capacity smoke; this is not a script failure.
FULL at N=8192 M=200 with noise p in {0.05, 0.10, 0.20} will have genuine retrieval errors.

## Runtime estimate

3 seeds x 4 strata x 200 trials = 2400 retrieval steps at N=8192 on GPU.
Estimated < 5 min GPU. Timeout: 900 s.

## References

- Cap 2 original: exp_wave14_critical_slowing_down_self_monitor_v1.py (REFUTED v153)
- Cap 1 Sagawa-Ueda precedent: v158 re-axiomatization (delta_S metric fix)
- Original CRITICAL_NO_CORRELATION verdict (v153): tau iteration count as proxy fails
- Prompt: "Cap 2 critical slowing down self-monitor -- could try a re-analysis or fresh probe"
