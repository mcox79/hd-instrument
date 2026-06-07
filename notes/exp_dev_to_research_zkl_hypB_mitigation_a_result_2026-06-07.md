# Exp-Dev -> Research: Hyp B mitigation (a) attention-reweighting -- directionally works (only one that does), short of HIPAA

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_mitigation_a_authorize

Mitigation (a), attention-pool proxy of the forward hook (cap top-3 attended positions to the mean of the rest), calibrated
MarianMT harness, smoke n=60 k=16:
  attn-pool ORIG    ZKL(16) = 0.400  KEY-F1 = 1.000
  CAPPED-top3       ZKL(16) = 0.267  KEY-F1 = 1.000   (F1 drop = 0%)

## Read: (a) is the ONLY mitigation that helped -- mechanism confirmed causal
Capping the concentrated positions reduces ZKL ~33% relative (0.400 -> 0.267) at ZERO KEY-job cost. Every other mitigation
(manifold/Gram/earlier-layer/mean-pool) was flat or worse; (a) is the first to move ZKL down. This CONFIRMS Hyp B is not
just correlational -- the position-concentration causally drives the membership leak, and removing it lowers leakage.
BUT 0.267 is still >> 0.10 (and > 0.15), so per the threshold this is HARD_FAIL for absolute HIPAA. One round of top-3
capping is insufficient.

## Decision (your call) -- three honest options
1. TRUE forward hook (vs my attn-pool proxy): the proxy re-aggregates L15 hidden states with capped weights; a real hook
   that caps the attention probs INSIDE the layer (so the OV circuit + residual + MLP see the capped attention) may reduce
   ZKL further than the proxy shows. ~1-2 days eng. Worth it given (a) is the only lever that works.
2. Stronger capping in the proxy (cheap, ~30 min): cap top-k for k>3 (5/8/12) or ITERATE capping; if a larger-k cap reaches
   <=0.10 in the proxy, the true hook is clearly worth building. I can run this immediately.
3. Lock the QUALIFIED-privacy posture now: (a) at one round doesn't reach HIPAA; if you judge the marginal gain not worth
   the hook eng, lock audit + ZKP + rate-limit k<=5 as the standing story, absolute HIPAA via per-customer fine-tune (Path D).

Recommendation: run option 2 first (cheap, decides whether the hook is worth it). The qualified posture stands regardless
until a variant hits ZKL<=0.10. Queued: zkl_hypB_attn_reweight_v1 (full n=500, confirms 0.40->0.27 at scale).
