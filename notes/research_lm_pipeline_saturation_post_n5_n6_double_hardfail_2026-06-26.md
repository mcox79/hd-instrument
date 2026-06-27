# RESEARCH: Substrate-LM pipeline saturation — post n5_trigram + n6_V_C_4096 double HARD_FAIL

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Two independent structural extensions of the K-means + count-prop + JM pipeline have empirically failed in the same week. exp_dev correctly HELD n6_optimal_V_C_sweep_v1 (2026-06-26 10:37) and routed to Research. While the HOLD recommendation was "dispatch n5_trigram instead," n5_trigram landed HARD_FAIL today (`data/exp_n5_trigram_concept_lm_v1/metrics.json`). Both proposed closure paths are now empirically dead on the current pipeline. This is a structural-saturation event, not a single-lever miss.
**Discipline:** 0.20 deflation; novel-synthesis cap P_deflated=0.50; Fix #28 default under-claim; substrate-mine FIRST.

---

## HEADLINE

**The K-means concept-codebook + count-prop transition + Jelinek-Mercer pipeline has saturated at ~4.95 BPC on text8 at N=16384 V_C=1024.** The two "obvious" extensions both produce STRICTLY WORSE BPC:

| Lever | Mechanism | Result |
|---|---|---|
| V_C=4096 capacity extension (n6_v1) | larger K-means codebook | sub_bpc rises 0.65 bits; codebook_utilization 0.67-0.72 (30% dead bins); ceiling RISES not drops |
| HRR-bind trigram context-depth (n5) | bind 2 prior concepts into query vector | sub_bpc rises 1.7 bits; concept_top1 collapses 4x (0.54 → 0.13); cv=0.002 (rock-solid signal) |

Both findings are per-seed reproducible across 3 seeds. n5's depth_gain is consistently -1.6 to -1.9 bits across seeds — the HRR crosstalk dominates whatever count-stat lift trigram context would provide.

**Diagnosis (per-lever):**
- **n6 dead-bin collapse:** K-means on text8's Zipf-distributed tokens cannot allocate V_C=4096 distinct clusters; head tokens dominate >60% of mass; tail 30% of bins die. Per-bin transition counts become noise → ceiling RISES not drops as V_C grows.
- **n5 HRR crosstalk:** binding 2 prior concepts via HRR-bind produces a query vector whose cosine to the trained transition keys is at f=0.006 / k_active=98 crosstalk floor. The bound query carries the 2-prior context as ~3-bit signal in an N=16384 vector with ~8x N-noise. Cleanup-attractor cannot recover the trigram lookup; the readout falls back to noise-decode (concept_top1=0.13).

Both diagnoses are mechanism-grounded, not test-design artifacts. The current pipeline's mathematical ceiling has been hit.

**Recommendation: RETIRE both levers as currently formulated. Re-orient closure path to mechanisms that AVOID HRR-bind for trigram + AVOID K-means capacity extension.** Three ranked replacement candidates below.

---

## What's been ruled out (cumulative as of 2026-06-26)

| Cell | Verdict | Notes |
|---|---|---|
| n2_capacity_scaling (N=4096 → 16384, V_C=1024) | floor at 4.96 BPC | N-scaling saturated |
| n3_mkn_smoothing | +0.068 bits only | smoothing alone insufficient |
| n3_vq_alignment_simvq | no win | encoder VQ-alignment doesn't lift |
| n4_kwta_soft_decode | HARD_FAIL | k-WTA encoder doesn't help |
| n10_whitening_projection | HARD_FAIL | ZCA-whiten doesn't help |
| n5_trigram_concept_lm (HRR-bind context) | HARD_FAIL | depth_gain NEGATIVE; HRR crosstalk dominates |
| n5_vc_4096_frontier_v1 (V_C=4096 sweep) | HARD_FAIL | dead-bin collapse |
| n5_vc_4096_frontier_v2_anchor_fix | HARD_FAIL | harness drift; can't reproduce V_C=1024 baseline |

Cumulative wall-time burned on this lever class: ~12 CPU-hr. Bayesian-update on "this pipeline can close the bigram-gap by tuning V_C and context-depth" is now <0.10.

---

## Three structural-reframing alternatives (rank-ordered)

### ANCHOR_1 (rank-1, AVOIDS HRR crosstalk; composes with chain-grade partition routing)

- **Pointer:** `n9_partition_routed_trigram_lm_v1`
- **Substrate-product reading:** "substrate-native trigram LM via PARTITION-ROUTED transitions: (c_{t-2}, c_{t-1}) pair is the partition KEY (not HRR-bound into a query vector); each observed context-pair gets its own count-prop transition table; chain-grade partition primitive (M=10M=0.978 on substrate ledger) handles the sparse-context indexing natively"
- **Why this avoids both failures:** No HRR-bind → no crosstalk dilution. No K-means capacity extension → no dead-bin collapse. The substrate's sparse-context allocation is NATURAL: n5 measured n_unique_trigram_contexts=5437-5600 per seed in a V_C^2=1M context-space — partition routing trivially indexes this density.
- **Tier hint:** MEASURED_MECHANISM expected at first land; chain-grade-eligible IF substrate_bpc <= 4.50 (closes >= 0.46 of 1.13-bit gap) AND cv <= 0.05 AND backoff_rate ≤ 0.50 (most contexts seen ≥ once during training).
- **Arms (3 mandatory):** ARM_BIGRAM_BASELINE (rail; reproduces 4.95 BPC); ARM_PARTITION_TRIGRAM (1 partition per observed (c_{t-2}, c_{t-1}) pair; per-partition count-prop with WB backoff to bigram); ARM_PARTITION_TRIGRAM_PLUS_HASH_FALLBACK (unseen contexts hash to nearest-2 observed partitions, weighted by partition-density; deflate-with-evidence smoothing).
- **Pre-reg bands:** HARD_PASS substrate_bpc <= 4.50 (P=0.30); MIDDLE_BAND in (4.50, 4.90] (P=0.45); HARD_FAIL > 4.90 OR depth_gain negative (P=0.25). Sums to 1.00. Distinguishing-regime gate: ARM_PARTITION_TRIGRAM must beat ARM_BIGRAM_BASELINE by ≥ 0.10 bits AND retain concept_top1 ≥ 0.40 (not collapse like n5).
- **Smoke gate:** sigma=0 sanity (bigram baseline reproduces 4.96 BPC exactly); per-partition transition tables build correctly; 5500 partitions allocated as predicted from n5 measurement; backoff_rate ≤ 0.50.
- **Cost estimate:** ~5 min smoke / ~3-5 hr local_cpu (3 seeds; text8 100k docs; N=16384; V_C=1024). Cheaper than n5 because no HRR-bind matmul; just partition-table lookups.
- **Composition:** uses chain-grade `partition_routing` primitive directly (M=10M=0.978 ledger) + n1v3 concept codebook + count-prop + WB backoff. Zero HRR usage on the transition lookup. NO encoder change vs n1v3.
- **P_deflated:** 0.40 (chain-grade primitive backing + clear avoidance of both n5/n6 failure modes; deflated 0.20 from raw 0.60 because pipeline has 5+ recent HARD_FAILs in close-region).

### ANCHOR_2 (rank-2, addresses dead-bin diagnosis from n6; orthogonal to ANCHOR_1)

- **Pointer:** `n11_frequency_stratified_VQ_lm_v1`
- **Substrate-product reading:** "frequency-stratified VQ: bin tokens by frequency band (top-1k / 1k-10k / 10k+); allocate V_C=1024 K-means codebook per band → V_C_total=3072 with each subbook in well-allocated regime; bigram count-prop over the stratified codebook"
- **Why this addresses dead-bin:** the n6 dead-bin collapse was K-means' inability to allocate V_C=4096 distinct clusters under Zipf distribution. Stratifying by frequency first ensures each subbook's data distribution is closer to uniform → K-means allocation efficient at V_C=1024 per band.
- **Tier hint:** MEASURED_MECHANISM expected; chain-grade-eligible IF substrate_bpc <= 4.50 AND codebook_utilization per band ≥ 0.85 AND no single band's transition-table dominates >70% of test mass.
- **Arms (4 mandatory):** ARM_BIGRAM_BASELINE (rail; n1v3-equivalent at V_C=1024); ARM_STRATIFIED_V_C_3072 (3 bands × V_C=1024); ARM_STRATIFIED_V_C_6144 (3 bands × V_C=2048; tests scaling within stratified regime); ARM_STRATIFIED_V_C_3072_PLUS_BOUNDARY (boundary tokens at band-edges get dual-bin membership; tests whether stratification artifacts hurt).
- **Pre-reg bands:** HARD_PASS substrate_bpc <= 4.50 at some V_C_total (P=0.25); MIDDLE_BAND <= 4.80 (P=0.45); HARD_FAIL > 4.80 OR per-band utilization < 0.70 (P=0.30).
- **Smoke gate:** per-band token assignment is mutually exclusive (no token in 2 bands except boundary arm); per-band K-means converges within 50 iterations; bigram baseline reproduces 4.96.
- **Cost estimate:** ~10 min smoke / ~6-8 hr local_cpu (3 seeds; 3 K-means runs per seed instead of 1; otherwise same as n2).
- **P_deflated:** 0.30 (addresses one specific failure-mode but doesn't unlock context-depth; the gap is unlikely to close from V_C-stratification alone — Mikolov adaptive-softmax precedent suggests ~10-20% perplexity improvement, which maps to ~0.30-0.50 BPC if all else equal; bigram-gap is 1.13 bits).

### ANCHOR_3 (rank-3, deferred; requires backprop plumbing not currently in substrate)

- **Pointer:** `n12_vq_vae_uniformity_prior_lm_v1` (DEFER)
- **Substrate-product reading:** VQ-VAE codebook with commitment loss + entropy regularization term forcing uniformity over codes. Gradient-trained; substrate doesn't currently do backprop encoders.
- **Tier hint:** Phase-2; defer unless ANCHORS 1 + 2 both HARD_FAIL.
- **Cost estimate:** ~3 days build (backprop plumbing) + 6-8 hr CPU.
- **Order:** dispatch ONLY IF ANCHOR_1 and ANCHOR_2 both fail to close ≥ 0.30 bits of the gap.

---

## Why partition-routing (ANCHOR_1) is the strongest substrate-product lever

The HRR-bind crosstalk diagnosis from n5 is the MOST consequential finding of this cycle: **the substrate's HRR primitive cannot be used to carry trigram context for LM prediction.** This refutes the entire family of "deeper-context via deeper HRR-bind" mechanisms (n8 5-gram HRR, n9 4-prior HRR, etc.) that would have been the natural follow-ups.

But the substrate has a SECOND mechanism for carrying multi-token context: **partition routing**. This is chain-grade at M=10M (substrate ledger). The trigram-LM use case is a NATURAL fit: each observed (c_{t-2}, c_{t-1}) pair becomes a partition key, with its own count-prop transition table. Sparse contexts are handled via WB backoff to bigram. There is NO HRR-bind on the lookup path → NO crosstalk dilution.

This reframes the substrate-LM closure problem from "make HRR carry more context" (which n5 refutes) to "use partition-routing for context-depth, reserve HRR for compositional binding tasks where the crosstalk dominates the right answer not the noise." That is a clean separation of substrate primitives by use-case, which composes correctly with the rest of the substrate's chain-grade portfolio.

**If ANCHOR_1 HARD_PASSes with substrate_bpc <= 4.50, this becomes the first cell that decisively closes >40% of the bigram-gap on a substrate-native pipeline.** That's the load-bearing test.

---

## Falsifiable predictions

- **P1 (ANCHOR_1 mechanism):** ARM_PARTITION_TRIGRAM concept_top1 ≥ 0.40 (does NOT collapse like n5's 0.13). If concept_top1 < 0.30, the partition-routing approach is also crosstalk-limited (would be surprising; would need re-think).
- **P2 (ANCHOR_1 bgp_close):** ARM_PARTITION_TRIGRAM substrate_bpc < ARM_BIGRAM_BASELINE substrate_bpc by ≥ 0.10 bits. Sign-discriminator: any depth_gain ≥ 0 falsifies the n5 trap.
- **P3 (ANCHOR_1 backoff_rate):** backoff_rate ≤ 0.50 at 100k docs (most contexts seen). Backoff_rate > 0.70 indicates context-sparsity is the limiter.
- **P4 (ANCHOR_2 mechanism):** per-band codebook_utilization ≥ 0.85 at V_C=1024 per band. If utilization is similar to n6 (<0.75), stratification did NOT fix dead-bin collapse.
- **P5 (composition):** if ANCHOR_1 closes 0.10-0.30 bits AND ANCHOR_2 closes 0.10-0.30 bits, composing them via partition-routed trigram OVER stratified codebook should close 0.20-0.50 bits (sub-additive due to shared count-prop dependence).

---

## Context pointers (file paths, not summaries)

- **n5 trigram metrics (the new HARD_FAIL evidence):** `data/exp_n5_trigram_concept_lm_v1/metrics.json`
- **n6 HOLD note (exp_dev's correct call):** `notes/exp_dev_predispatch_hold_n6_optimal_V_C_sweep_v1_routes_to_research_2026-06-26.md`
- **Prior n5_vc_4096 v1 metrics (dead-bin evidence):** `data/exp_n5_vc_4096_frontier_v1/metrics.json`
- **Drill 1 hand-off (where n5 + n6 were both Anchor candidates):** `notes/exp_dev_handoff_research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
- **N1 v3.1 DEFINITIVE anchor:** `notes/orchestrator_to_skunkworks_N1_DEFINITIVE_substrate_LM_beats_unigram_not_bigram_2026-06-21.md`
- **Chain-grade partition routing primitive (M=10M):** substrate cert_ledger.jsonl + hdlab partition_routing primitive
- **N2 capacity metrics (4.96 BPC floor):** `data/exp_n2_capacity_scaling_v1/metrics.json`
- **HRR crosstalk theory:** Plate 1995 + Frady-Sommer 2018 (per-position capacity bound at f=0.006 / N=16384 ≈ 100 bits/position; trigram needs 2 × log2(V_C=1024) = 20 bits at the SAME position → predicts crosstalk if no fan-out; n5 confirms)

---

## What I'm NOT recommending

- **NOT re-dispatching n6 as written** (exp_dev's HOLD is correct; V_C-sweep on K-means pipeline is empirically dead).
- **NOT n5 v2 with bigger N** (the failure is HRR-bind crosstalk on bound queries, not capacity; bigger N doesn't help).
- **NOT n8 5-gram HRR or any deeper-HRR extension** (n5 refutes the HRR-bind-for-context mechanism class).
- **NOT VQ-VAE backprop encoder** (defer until simpler ANCHORS 1+2 verdicts inform whether the gap is closeable on count-prop pipeline at all).

---

-- Research (Opus 4.7-1M)
