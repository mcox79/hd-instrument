# Prereg: ordinal_magnitude_encoding_vs_combination_v1

Filed-by: exp_dev. Date: 2026-07-14. Trigger: notes/exp_dev_handoff_research_ordinal_magnitude_coding_bestinclass_2026-07-14.md
Script: experiments/exp_ordinal_magnitude_encoding_vs_combination_v1.py
Clusters (on-disk, reused; NO generation): data/foundation_clusters/{animals,foods}_ordinal_conjunction_v1.json
Dispatch: remote_cpu_queue (CPU-only, self-contained; only hdlab.binding.bind + numpy/torch). Multi-seed (7,13,17,23,29).

## Scientific question
Our monotone/additive ordinal code reads ordinal conjunctions but beats a frequency/homophily null only modestly
(animals CLEAN-novel top1 0.573 vs freq 0.511, +0.062). Is the residual bottleneck the ENCODING (linear-uniform level
spacing vs log/Weber-compressed spacing) or the COMBINATION RULE (fixed learned global weights vs per-cue
reliability-weighted linear averaging, Ernst-Banks)? Everything (mechanism, split, FREQ_NULL fair baseline,
ARBITRARY/SHUFFLE must-fails, seeds) is held IDENTICAL; each anchor changes exactly one lever so the delta isolates it.

## Baseline reproduced FIRST (correctness gate)
MONO_WEIGHT under UNIFORM encoding must recover the prior-session animals CLEAN-novel learned-weight top1 =
0.573 +/- 0.06 (else verdict REPRODUCTION_MISMATCH). [Local smoke: measured 0.5725, freq_null 0.5108 -- reproduces.]

## Arms
MONO_WEIGHT (learned non-neg softplus weights) x {uniform, log=Weber log(1+k), power=Stevens k^0.5, quantile=train
empirical density} ; MONO_THERM (equal-weight uniform) ; RELIABILITY (per-(constituent,level) inverse-variance
cue integration, uniform level indices held fixed) ; FREQ_NULL=max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE.
Headline stratum = NOVEL combinations (top1 acc; chance 1/L=0.20; NOT tuned).

## Pre-registered bands (fixed BEFORE running)
ANCHOR 1 (encoding; headline = log vs uniform on animals, foods reported too):
- HARD_PASS : MONO_WEIGHT_log_novel - MONO_WEIGHT_uniform_novel >= +0.05 (animals >= ~0.62), must-fails firing.
- MIDDLE_BAND: delta in [0.02, 0.05).
- HARD_FAIL : delta < 0.02 (either direction) -> uniform binning NOT the bottleneck; do NOT iterate more bin variants;
  the additive regime is (data/frequency)-capped on this axis. power/quantile are pre-registered siblings (reported,
  not iterated-on-fail).

ANCHOR 2 (combination rule; reliability vs fixed learned weights):
- HARD_PASS : closes >= 30% of the learned-weight arm's CLEAN-novel failure cases with new_failures <= closed
  (net localized), must-fails firing.
- MIDDLE_BAND: global-average novel acc improves >= 0.02 but closed_frac < 0.30 (diffuse gain).
- HARD_FAIL : closed_frac <= 0.10 (failure overlap >= 90%) -> fixed weights not the bottleneck; gap is upstream in
  the per-constituent encoding.

CORRECTNESS GATES (non-negotiable, gate any PASS): reproduction (above) ; ARBITRARY + SHUFFLE must-fails fire for
every real arm (gap <= 0.05) ; ORACLE ceiling >= every arm.

## Fairness / validity disciplines (enforced inline in self_test on a planted arena, at self-test scale)
1. Positive control: learned-weight arm solves + generalizes on NOVEL and beats freq (mono_gap >= 0.15).
2. Metric-moves: log encoding changes >= 1 novel prediction vs uniform + explicit compressive-ordering witness
   (log makes (2,2) outrank (4,0) though uniform ties) -> the encoding lever is provably live, not absorbed.
3. Negative control fires with margin: ARBITRARY must-fail gap <= 0.10.
4. Determinism self-guard: identical re-run -> identical signatures (fixed per-regime salts; no PYTHONHASHSEED hashing).
Plus: guard-vs-arena-floor (freq_null <= 0.85, not saturated) ; real hd_bind homomorphism (live substrate signature) ;
genuine conjunction (mi_margin >= 0.30, dominance_ratio <= 0.55). [Local self-test PASSED.]

## Weak-point localization
Anchor 2 reports per-instance CLEAN-novel failure-case overlap (n_base_fail, closed, new_fail, closed_frac) pooled
across seeds -> pinpoints WHETHER reliability weighting fixes a localized subset of the fixed-weight arm's errors or
just shifts the global average. Anchor 1 reports per-encoding deltas (log/power/quantile) -> localizes whether ANY
compressive scheme moves the encoding axis.

## Compute
CPU-only, self-contained, deterministic. Local FULL wall 0.78s (both clusters, 5 seeds). Timeout 600s (generous
headroom for remote CPU). metrics.json at data/exp_ordinal_magnitude_encoding_vs_combination_v1/metrics.json.

## Honest-negative commitment
If Anchor 1 HARD_FAILs (it does at smoke: log_delta +0.006 animals, -0.031 foods), report plainly that uniform
binning was NOT the active bottleneck and do NOT iterate further bin variants -- a valuable negative (the additive
encoding is not the lever). Smoke Anchor 2 = HARD_PASS on animals / HARD_FAIL on foods -> combination-rule lever is
cluster-dependent, NOT a universal win; hold the mechanism-story until landed-VET (telemetry can invert at scale).
