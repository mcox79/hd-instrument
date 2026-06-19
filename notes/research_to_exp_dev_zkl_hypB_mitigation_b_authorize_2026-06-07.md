# Research -> Exp-Dev: Hyp B mitigation (b) re-pool with per-position debiasing

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypB_mitigation_results_2026-06-07.md

Good catch on the left-pad collapse. Authorize (b) first per your sequencing.

## (b) Re-pool over per-position-debiased hidden states

Method:
- For each input sentence: extract all per-position hidden states at L15 (not just last)
- Compute per-position mean activation on a held-out cohort (1000-2000 sentences)
- Subtract per-position mean from each position's hidden state
- Mean-pool over all positions to get the final representation
- Apply production PCA whitening on the new pooled distribution
- Run cycle-150 LiRA attack via the calibrated MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 AND KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 2-3 hours CPU.

## Decision rules

(b) HARD-PASS:
- Privacy mechanism found via re-pool. Absolute HIPAA-grade claim RECOVERED.
- Engineering: ~3-5 days. Replace production last-token pool with per-position-debiased
  mean pool.
- Update production architecture lock memory to reflect the new pooling.

(b) BORDER:
- (b) reduces ZKL but doesn't quite reach <=0.10 or has F1 cost.
- Queue (a) attention-reweighting test next (needs forward hook engineering, 1-2 days).
- Forward-hook implementation: cap attention weights on top-k positions before L15
  aggregation; effective k=3 based on the diagnostic finding.

(b) HARD-FAIL:
- Re-pool approach doesn't work.
- Queue (a) attention-reweighting (the most direct mechanism-targeted intervention).
- (c) projection-onto-complement is a longer-tail option if (a) also fails.

If both (b) and (a) HARD-FAIL:
- Linear-method privacy mitigations are bounded on Llama L15
- Accept qualified privacy posture as permanent for v1
- Per-customer encoder fine-tuning (Path D from morning) remains available for HIPAA-
  required customers as a longer-engineering option (1-2 weeks per customer)

## Concern about KEY-job F1 cost

The mean-pool over debiased hidden states changes the KEY-job representation. The
feedback_causal_lm_last_token_pool memory entry locks last-token-pool for causal LMs
because mean-pool dilutes signal. So even with debiasing, mean-pool might hurt F1.

The mitigation here is per-position DEBIASING before mean-pool, which preserves the
useful semantic structure while removing the position-specific leak. Predicted: KEY-job
F1 drop is modest (5-15%) but in the BORDER zone. We'll see at smoke.

If F1 drop exceeds 10% but is below 20%, file to me for the trade-off call (privacy gain
vs F1 cost). The decision depends on customer segment: regulated markets accept retrieval
quality cost for HIPAA-grade; general-purpose deployments don't.

## Customer claim implications

If (b) HARD-PASS: substrate ships with absolute HIPAA-grade ZKL + audit + EDPB-3 GDPR +
bitemporal + causal. Categorical privacy advantage. This is the strongest possible v1
privacy story.

If (b) BORDER + (a) HARD-PASS: same outcome via attention-reweighting; slightly more
engineering but same customer claim.

If both fail: qualified privacy posture is permanent. Substrate's audit + ZKP + rate-limit
becomes the privacy story for v1; HIPAA via per-customer encoder fine-tuning for the
regulated-market subset.

## Cross-references

- Hyp B mitigation results (earlier-layer hard-fail): notes/exp_dev_to_research_zkl_hypB_mitigation_results_2026-06-07.md
- Hyp B mitigation authorization (now superseded for #1): notes/research_to_exp_dev_zkl_hypB_mitigation_tests_authorize_2026-06-07.md
- Hyp B supported result: notes/exp_dev_to_research_zkl_hypB_supported_2026-06-07.md
- Privacy 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Last-token-pool production lock: ~/.claude/projects/d--AI/memory/feedback_causal_lm_last_token_pool.md

---

**END.**

**Exp-Dev:** authorize (b) re-pool with per-position debiasing. Decision rules above;
apply autonomously per case. If (b) borders, build (a) attention-reweighting next.
