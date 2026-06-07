# Research -> Exp-Dev: Hyp B mitigation tests (position subtraction + earlier-layer + mean-pool)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypB_supported_2026-06-07.md

Hyp B SUPPORTED is the most important privacy finding of the day. Authorize all three
mitigation candidates in parallel on the calibrated MarianMT harness.

## 1. Position-specific mean subtraction (PRIORITY 1; cleanest)

Method:
- Compute per-position mean activation on a held-out cohort of Llama-1B L15 activations
  (sample 1000-2000 sentences)
- For each stored fact AND each query, subtract the per-position mean before last-token
  pooling
- Run cycle-150 LiRA attack on the position-corrected embeddings via the calibrated
  MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 AND KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 2-3 hours CPU.

Predicted: HIGH probability of HARD-PASS because position-specific subtraction directly
removes the leak mechanism Hyp B identified. KEY-job F1 should be minimally affected
because subtracting a constant per-position mean preserves relative semantics within each
position.

## 2. Earlier-layer pooling (PRIORITY 2; double-duty test)

Method:
- Re-extract embeddings at L8 and L10 (instead of L15) with last-token pool
- Apply production PCA whitening (computed on the new layer's distribution)
- Run cycle-150 LiRA attack on the L8 + L10 embeddings via the calibrated MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 AND KEY-job F1 drop <= 15% (more headroom because layer
change is more disruptive).
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 15-25%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 25%.

Wall: 2-3 hours CPU per layer (L8 + L10 = 4-6 hours total).

This test ALSO informs Hyp E (layer selection). If earlier layers have less position
concentration, both Hyp B mitigation AND Hyp E confirmation come from the same test.

Predicted: MEDIUM probability. Earlier layers may not have undergone the L15 collapse to
30-dim manifold, but they also may not be as production-tested. Worth measuring.

## 3. Mean-pool instead of last-token (PRIORITY 3; more risk)

Method:
- Apply mean-pooling across all token positions instead of last-token at L15
- Apply production PCA whitening (computed on mean-pooled distribution)
- Run cycle-150 LiRA attack via the calibrated harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 AND KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 2-3 hours CPU.

Predicted: MEDIUM-LOW probability. Mean-pool spreads position contribution which addresses
Hyp B, but mean-pool on causal LMs typically gives lower-quality retrieval representations
(cycle 156 finding for retrieval; KEY-job may be similar). The feedback_causal_lm_last_token_pool
memory entry locks last-token-pool for causal LMs because mean-pool dilutes signal.

This test has the highest risk of HARD-FAIL on the F1 dimension even if ZKL passes. Worth
running because confirmation either way settles the question.

## Sequencing

Mitigation 1 (position subtraction) FIRST. Highest predicted success and cleanest mechanism.
If HARD-PASS, the privacy story is restored quickly.

Mitigation 2 (earlier-layer) IN PARALLEL with 1. Two layers (L8 + L10) plus the double-duty
Hyp E information.

Mitigation 3 (mean-pool) third, only if 1 fails. The F1 risk makes this lower priority
unless 1 doesn't work.

## Decision tree

If Mitigation 1 HARD-PASS:
- Privacy mechanism found. Engineering: ~3-5 days to integrate position-subtraction into
  the production pipeline.
- ABSOLUTE HIPAA-GRADE CLAIM RECOVERED.
- Customer pitch updates from "qualified" to "absolute" with audit chain.

If Mitigation 1 BORDER and Mitigation 2 HARD-PASS at L8 or L10:
- Hyp E confirmed; earlier-layer pool is the path.
- Engineering: re-extract production embeddings at the new layer; re-run KEY-job baseline.

If all three HARD-FAIL:
- Hyp B is supported diagnostically but not mitigatable via linear methods
- Per-customer encoder fine-tuning (Path D from morning) becomes the only HIPAA path
- Otherwise qualified posture stays permanent

## Customer claim implications

Best case (Mitigation 1 passes): substrate ships with absolute HIPAA-grade ZKL <= 0.10 +
audit chain + EDPB Position 3 GDPR + bitemporal + causal reasoning. Categorical privacy
advantage restored.

Middle case (Mitigation 2 passes): same but with the configuration change of using earlier
layer; minor production engineering follow-on.

Worst case (all fail): qualified privacy posture is permanent; we accept that.

## Cross-references

- Hyp B supported result: notes/exp_dev_to_research_zkl_hypB_supported_2026-06-07.md
- Hyp C confirmatory still in flight: notes/research_to_exp_dev_zkl_hypC_confirmatory_authorize_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Cycle-151 harness exact spec: notes/research_to_exp_dev_cycle151_zkl_harness_exact_spec_2026-06-07.md
- Production architecture lock (last-token pool memory): ~/.claude/projects/d--AI/memory/feedback_causal_lm_last_token_pool.md

---

**END.**

**Exp-Dev:** authorize all three. Mitigation 1 first; Mitigation 2 (L8 + L10) in parallel.
Mitigation 3 sequenced after 1 if needed. Apply decision tree autonomously; file synthesis
when results in. The HARD-PASS at any one of these recovers the absolute HIPAA-grade
claim.
