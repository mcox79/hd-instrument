# Research advisory — test-design alternatives to prototype-classification for 6-channel importance cell

**Date:** 2026-06-27
**Author:** Research (Director)
**For:** cell-author `exp_importance_6channel_brain_analog_v1` (agent aa569dd1) and any v2 follow-up
**Trigger:** Wave 2H meta-finding (prototype-classification saturates) + USER 2026-06-27 ~17:50 PDT: "task-class-mismatch sounds like a big barrier let's not do that"

## 1. Why prototype-classification is the wrong readout for multi-channel importance

A 6-channel importance signal (novelty/attention/coreness/success/consensus/effort) is a **memory-gating** mechanism. Its job is to decide *what gets consolidated, retained, and protected from interference*. Prototype-classification asks "given a noisy query, which class wins?" — that question doesn't load on the gating axis at all. With M=4096 / N_DIM=16384, classification accuracy is at substrate ceiling regardless of which channel weights are used; the discriminator is dead. We need readouts where retention/selectivity is the dependent variable.

## 2. Four alternative test-designs (concrete metrics + HARD_PASS thresholds)

### A. capacity@retrieval-quality
**Setup:** Stream M_stream = 50,000 items at substrate; each arm uses its own 6-channel importance score to gate consolidation (top-X% retained). After streaming, query 1,000 held-out probes (mix of retained + evicted items + foils).
**Metric:** `retrieved_fraction_at_cosine>=0.85` — what fraction of probes the substrate can recover above a fixed similarity threshold.
**Compare:** uniform-gating baseline vs each importance channel vs full 6-channel weighted blend.
**HARD_PASS:** 6-channel blend retains >=1.30x baseline retrieved_fraction at matched compute budget AND each channel arm separates from uniform by >=2sigma over seeds. Discriminator survives because at M=50k>>4096 the substrate IS capacity-bound.

### B. interference-fraction-measured
**Setup:** Bind N=2000 cue->target pairs serially. Measure cue-recall accuracy at intervals (after 500, 1000, 1500, 2000 bindings). Each arm uses its importance signal to weight consolidation strength per binding.
**Metric:** `interference_fraction = 1 - recall(old_cue, time=now) / recall(old_cue, time=just_bound)` — how much each new binding degrades old ones.
**Compare:** uniform-weight bindings vs importance-weighted bindings (each channel, then blend).
**HARD_PASS:** 6-channel arm shows interference_fraction <=0.70x uniform-baseline AND the *important* pairs (top-quartile by ground-truth importance) show interference <=0.50x uniform. Discriminates because selective consolidation should protect high-importance items asymmetrically.

### C. signal-to-crosstalk ratio (SCR)
**Setup:** Bind target atom T_i with importance-weighted strength alpha_i(channel). For each target, generate K=100 confuser atoms cosine-near T_i. Query with noisy cue.
**Metric:** `SCR = cos(query, T_i) / mean(cos(query, confuser_k))` — how cleanly the importance-weighted target separates from acoustically-similar distractors.
**Compare:** flat-weight vs each channel vs blend, measured over 500 target atoms.
**HARD_PASS:** 6-channel blend SCR >=1.5x flat-weight AND channel rank-order matches ground-truth importance (Spearman rho >=0.6). Discriminator: importance should sharpen retrieval contrast, not just shift mean cosine.

### D. ranking-fidelity at K=100 / K=1000
**Setup:** Build importance-ranked priority queue from substrate state. Query with held-out "what mattered most?" probe — does substrate return ground-truth-important items in correct rank order?
**Metric:** `precision@100` and `nDCG@1000` against ground-truth importance ranking (synthesized from controlled stream).
**Compare:** uniform retrieval baseline vs each channel vs blend.
**HARD_PASS:** 6-channel blend nDCG@1000 >=0.75 AND precision@100 >=0.40 (vs uniform expected ~0.10). Independent of classification — pure ranking-quality metric.

## 3. Recommendation

- **Let current `exp_importance_6channel_brain_analog_v1` complete as-is.** Cheap baseline data point; even a saturated classification result tells us the channels CAN be encoded together without collapse, which is non-trivial information for v2.
- **If v1 MIDDLE_BANDs or HARD_FAILs** (likely, per Wave 2H meta-finding) → author **v2 on capacity@retrieval-quality (design A)** as the primary readout, with SCR (design C) as secondary discriminator. Both are cheap to implement on existing primitives (no new infrastructure beyond a 50k stream + held-out probe set), both scale-discriminate at M>>4096, and both have clean ground-truth comparators.
- Designs B and D are stronger discriminators but cost more to set up (interference protocol requires controlled binding schedule; ranking-fidelity requires ground-truth importance synthesis). Hold as v3 if v2 lands chain-grade-eligible.

## 4. Predicted channel winners by design

- **Design A (capacity@retrieval):** *coreness* and *consensus* should dominate — both index "this item is structurally important across many contexts," which is exactly what selective consolidation should preserve. *Novelty* should help moderately (gating novel-but-important from novel-but-noise).
- **Design B (interference-fraction):** *attention* and *success* should dominate — attended/successfully-used items deserve interference protection. *Effort* may also matter (high-effort encodings should be defended).
- **Design C (signal-to-crosstalk):** *novelty* and *attention* should dominate — these are the channels that say "make this item stand out from the cloud." *Coreness* may HURT (averages toward category centroid, lowering SCR).
- **Design D (ranking-fidelity):** *consensus* and *coreness* should dominate — these align directly with ground-truth importance synthesis.

**Cross-design prediction:** the 6-channel blend should beat each individual channel on at least 3 of 4 designs. If a single channel beats the blend on 3+ designs, that's evidence channels are redundant rather than complementary — important meta-finding worth its own follow-up.

## Estimated cost

v2 on design A: ~2-4 GPU-hr (50k stream + 1k probes x 6 arms x 3 seeds). v3 expanding to A+C: ~6-10 GPU-hr. Both well within overnight_queue budget.
