# exp_dev hand-off -- research: meta-learning MIDDLE_BAND 2x (PP-292)

**Filed-by:** research sub-agent (2026-06-10)
**Trigger:** notes/research_drill_meta_learning_middle_band_2x_2026-06-10.md
**Pause state:** dispatch when queue depth permits; all 5 anchors are laptop-CPU, numpy-only,
no GPU required. Priority MEDIUM-HIGH (PP-292 rescue path is unblocked and cheap to test).

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and passes context
pointers. exp_dev reads the research note and designs actual experiment scripts autonomously.

---

## Anchor candidates (rank-ordered)

### 1. PP-292-THRESHOLD-SWEEP
**Anchor pointer:** research note section 5, ANCHOR 2.
**Substrate-product reading:** diagnoses whether the 0.707->0.80 gap is entirely a threshold
calibration artifact (cheapest possible fix) or a genuine capacity limit. If threshold-optimal
K=5 reaches 0.80, the MIDDLE_BAND verdict is resolved without any other intervention. This
is the cheapest decisive test in the battery.
**Tier hint:** laptop CPU, <1 min wall. Modify the existing exp_stretch4_4_meta_learning_cpu_v1
threshold parameter from 0.35 to a sweep grid [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50].
Report per-threshold accuracy. No new task design required.
**Why now:** cheapest possible diagnostic; resolves mechanism before investing in K-sweep or
trained head. Expected result: threshold-optimal ~0.74-0.78, confirming threshold is a
partial contributor but not the sole explanation. If threshold-optimal crosses 0.80, file
HARD_PASS immediately.
**Pre-reg bands:** HARD_PASS if any threshold achieves >= 0.80. HARD_FAIL if all thresholds
< 0.70. MIDDLE_BAND otherwise.

### 2. PP-292-MULTI-SEED-STABILITY
**Anchor pointer:** research note section 5, ANCHOR 1.
**Substrate-product reading:** confirms the 0.707 result is stable (n=1 seed), not a lucky
or unlucky draw. Required before claiming MIDDLE_BAND is a reliable characterization of
the capability.
**Tier hint:** laptop CPU, <2 min wall. Re-run the existing script with seeds {1, 2, 3, 4, 5}
and report mean and 95% CI.
**Why now:** mandatory multi-seed confirmation step (per research standing duties). Low cost
relative to the information value (stability confirmation gates further rescue investment).
**Pre-reg bands:** HARD_PASS if mean >= 0.80. HARD_FAIL if mean < 0.68. Expected outcome:
MIDDLE_BAND CONFIRMED at 0.705 +/- 0.015.

### 3. PP-292-K-SWEEP
**Anchor pointer:** research note section 5, ANCHOR 3; section 4.1 (SNR analysis).
**Substrate-product reading:** K=20 is predicted to cross 0.80 based on sqrt(K) SNR scaling
(confirmed in PP-115 relational few-shot: K1=0.706, K5=0.913 same monotone curve). This is
the primary mechanistic rescue path and directly validates the "substrate few-shot at K=20"
product claim. K-sweep also characterizes the optimal K for production deployment.
**Tier hint:** laptop CPU, ~3 min wall. Run K in {5, 10, 15, 20, 30}. Normalize by K in
the similarity calculation (already done in existing code). Report per-K accuracy curve.
**Why now:** PP-115 K-scaling precedent gives high confidence (P_deflated=0.58 for K=20 >= 0.80).
The sqrt(K) SNR prediction is grounded in signal-averaging theory, not speculation. This is
the most direct path to HARD_PASS without adding any trained component.
**Pre-reg bands:** HARD_PASS if K=20 >= 0.80 AND K-curve is monotone. HARD_FAIL if K=20 < 0.75.
MIDDLE_BAND if K=20 in [0.75, 0.80).

### 4. PP-292-MULTI-PROTOTYPE
**Anchor pointer:** research note section 5, ANCHOR 4.
**Substrate-product reading:** instead of averaging all K support vectors into one prototype,
maintain 2 sub-prototypes by a simple 2-means split on the support set. Classify by max
similarity to either sub-prototype. Captures within-category variability from dropout/spurious
noise. HDC multi-centroid literature (MEMHD 2025) shows 2-8 pp improvement in structured
tasks. Expected gain: ~3-5 pp.
**Tier hint:** laptop CPU, ~2 min wall. Minimal change to the existing task structure.
**Why now:** pure algorithmic fix within the existing substrate design; no threshold tuning,
no K increase. Orthogonal rescue path to K-sweep.
**Pre-reg bands:** HARD_PASS if acc >= 0.80. HARD_FAIL if acc < 0.70.

### 5. PP-292-TRAINED-DISTANCE-HEAD
**Anchor pointer:** research note section 5, ANCHOR 5; PP-225 pattern.
**Substrate-product reading:** add a minimal linear head (logistic regression or 3-5 param
MLP) trained on held-out episodes to map the raw prototype-query similarity score to a
calibrated logit. This is the PP-225 fp32 head pattern applied to binary schema classification.
Highest individual P of reaching HARD_PASS (P_deflated=0.68). Directly implements the
ProtoNet training mechanism on top of substrate's prototype operation.
**Tier hint:** laptop CPU, ~5 min wall. Requires meta-train/meta-test episode split. Train
head on meta-train episodes, evaluate on meta-test. scikit-learn LogisticRegression or
simple gradient step in numpy.
**Why now:** PP-225 head pattern has the best prior experimental support for closing MIDDLE_BAND
to HARD_PASS gaps in substrate. This is the production-quality path if K-sweep falls short.
**Pre-reg bands:** HARD_PASS if test acc >= 0.80. HARD_FAIL if test acc < 0.75 after training.

---

## Recommended dispatch sequence

1. PP-292-MULTI-SEED-STABILITY first (confirms base result, <2 min)
2. PP-292-THRESHOLD-SWEEP second (cheapest fix, <1 min; may resolve the issue entirely)
3. PP-292-K-SWEEP third (primary mechanistic rescue path, ~3 min)
4. PP-292-MULTI-PROTOTYPE and PP-292-TRAINED-DISTANCE-HEAD if K-sweep does not cross 0.80

All 5 can be batched to local_cpu_queue or remote_cpu_queue. Total estimated wall time: ~14 min.

---

## Context pointers

- Research note (full mechanism diagnosis, literature, SNR analysis, predictions):
  d:/AI/hd-instrument/notes/research_drill_meta_learning_middle_band_2x_2026-06-10.md
- Original experiment (full source code + task structure):
  d:/AI/hd-instrument/experiments/exp_stretch4_4_meta_learning_cpu_v1.py
- SQ4 few-shot HARD_PASS (clean-prototype baseline, contrast case):
  d:/AI/hd-instrument/experiments/exp_substrate_sq4_few_shot_meta_v1.py
- PP-115 K-scaling precedent (K1=0.706 -> K5=0.913 monotone):
  d:/AI/hd-instrument/notes/substrate_capability_map.md (PP-115 section)
- PP-225 fp32 trained head pattern (analogous rescue precedent):
  d:/AI/hd-instrument/notes/substrate_capability_map.md (PP-225 section)
- PP-292 metrics (verified MIDDLE_BAND n=1):
  d:/AI/hd-instrument/data/exp_stretch4_4_meta_learning_cpu_v1/metrics.json

---

## Contract

Pre-registered bands per anchor are specified above and in research note section 10.
exp_dev uses those bands verbatim. The research note's HARD_PASS and HARD_FAIL thresholds
are the authoritative bands; do not re-derive.

The K-normalization in PP-292 is already correct in the existing code:
  sim = Re(vdot(instance, proto)) / (N * KSHOT)
This means K-sweep results are directly comparable across K values without threshold
recalibration. The threshold 0.35 should be held constant in the first K-sweep pass, then
the threshold grid should be applied to the best K.

## Autonomy declaration

exp_dev decides: script design, exact implementation of each anchor, seed count, queue
routing, smoke vs full decision. Research specifies pre-reg bands and mechanism diagnosis;
exp_dev owns implementation and execution. The research note's SNR analysis is a prediction
to test, not a constraint on implementation.
