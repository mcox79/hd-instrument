# Research -> Exp-Dev: Hyp B mitigation (a) attention-reweighting (last linear option)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypB_mitigation_b_result_2026-06-07.md

Authorize (a) attention-reweighting. It's the last mechanism-targeted linear option;
1-2 days engineering is bounded; the result either way is definitive.

## (a) Attention-reweighting via forward hook

Method:
- Implement forward hook on Llama-1B L15 attention layer
- For each input sentence: identify the top-3 attended positions (those receiving > X%
  of attention mass; default X=15%)
- CAP their attention weights to the per-head average (suppressing concentration)
- Re-aggregate L15 last-token output with re-weighted attention
- Apply production PCA whitening
- Run cycle-150 LiRA attack via calibrated MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 AND KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 1-2 days engineering for the hook + 2-3 hours CPU for the attack run.

## Why this might succeed where (b) failed

Mitigation (b) preserved the position-concentrated signal but SPREAD it via mean-pool.
Spreading made membership inference easier because the signal became diffuse but
present across the bundle.

(a) doesn't spread the signal. It CAPS the concentration mechanism at the source: the
attention weights themselves. If membership-inference exploits the fact that certain
input positions dominate the L15 output, capping those weights removes that domination.

Predicted: (a) has the highest probability of success of the three mitigations because
it directly targets the mechanism Hyp B identified, rather than averaging around it.
Still, P_actionable is modest (estimate 0.30-0.45) given the negative trajectory of
previous linear mitigations.

## Decision rules

(a) HARD-PASS:
- Absolute HIPAA-grade ZKL claim RECOVERED via attention-reweighting
- Engineering: ~5-7 days to integrate the forward hook into the production substrate
  pipeline (vs the 3-5 days for simpler whitening modifications)
- Customer pitch updates from qualified to absolute

(a) BORDER:
- Partial mitigation. Combine with other techniques (per-customer fine-tuning at smaller
  scale; rate-limit at k <= 3 instead of k <= 5).
- File to me for the engineering trade-off call.

(a) HARD-FAIL:
- Linear-method privacy mitigations on causal LMs are conclusively bounded.
- Qualified privacy posture is permanent for v1.
- Per-customer encoder fine-tuning (Path D from morning 3x drill) becomes the HIPAA
  premium tier (~1-2 weeks per customer; charged accordingly).
- The customer narrative becomes TIERED: qualified by default, absolute HIPAA via
  per-customer training.

## Honest trajectory acknowledgment

The morning's privacy 3x drill predicted linear methods would be bounded on causal LM
encoders. The empirical work today has progressively confirmed that prediction:
- Manifold confinement (the leading hypothesis): empirically wrong as mitigation
- Pairwise Gram structure: presumptive negative
- Layer selection: monotone wrong direction
- Position-mean subtraction collapsed under left-pad
- Debiased mean-pool: worsens leakage

(a) attention-reweighting is the one mechanism-targeted linear test remaining. If it
fails, we lock the qualified posture and the tiered HIPAA story. The bounded engineering
cost (1-2 days for the hook + 3 hours for the test) is well worth the definitive answer.

If you'd rather lock qualified posture now without testing (a), I understand the call;
the trajectory does favor that. But the 1-2 day cost is low and the definitive answer
is worth knowing.

## Customer claim implications

Best case ((a) HARD-PASS): substrate ships with absolute HIPAA-grade ZKL via
attention-reweighting + audit + EDPB-3 GDPR + bitemporal + causal. Categorical privacy
story.

Worst case ((a) HARD-FAIL): substrate ships with TIERED privacy:
- Default tier: qualified ZKL (rate-limit k<=5 + audit + ~2x relative vs RAG)
- Premium tier: per-customer encoder fine-tuning for HIPAA-grade absolute privacy
  (1-2 weeks per customer; charged accordingly)

Either outcome is a defensible commercial story. The HARD-PASS would just be cleaner
for the marketing pitch.

## Cross-references

- Mitigation (b) result: notes/exp_dev_to_research_zkl_hypB_mitigation_b_result_2026-06-07.md
- Mitigation (b) authorization: notes/research_to_exp_dev_zkl_hypB_mitigation_b_authorize_2026-06-07.md
- Hyp B supported: notes/exp_dev_to_research_zkl_hypB_supported_2026-06-07.md
- Privacy 3x drill (Path D = per-customer fine-tuning): notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Cycle-151 harness exact spec: notes/research_to_exp_dev_cycle151_zkl_harness_exact_spec_2026-06-07.md

---

**END.**

**Exp-Dev:** Authorize (a) attention-reweighting. Prototype the forward hook on
Llama-1B L15, run attack via calibrated harness, apply decision rules autonomously.
Definitive result either way; if HARD-FAIL we lock the tiered customer story.
