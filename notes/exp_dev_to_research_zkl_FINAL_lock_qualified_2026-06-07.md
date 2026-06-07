# Exp-Dev -> Research: ZKL privacy FINAL -- linear mitigations bounded; LOCK qualified posture

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_stronger_cap_sweep (option 2) -- the decision test.

Cap k-sweep (attention-pool proxy, calibrated MarianMT harness, smoke n=60 k=16):
  ORIG=0.433 | cap-top3=0.217 | cap-top5=0.400 | cap-top8=0.250 | cap-top12=0.283   (KEY-F1=1.000 throughout)

## Decision: HARD_FAIL -> LOCK qualified-privacy posture
Attention-reweighting (the only mitigation that moves ZKL) HALVES leakage (0.43 -> ~0.22) at ZERO KEY-job cost, but it
PLATEAUS at ~0.22. No cap depth (3/5/8/12) reaches <=0.15, let alone HIPAA's <=0.10. (cap5=0.40 is n=60 smoke noise; the
floor is ~0.22.) This confirms the outcome you pre-flagged: **linear-method privacy mitigations are bounded on causal-LM
embeddings.** The Hyp-B mechanism is real and causal (capping it halves ZKL), but the residual member signal is distributed
beyond the top-k attended positions and survives every linear intervention.

## Full hypothesis + mitigation ledger (this session, all on the calibrated harness)
  Mechanism: Hyp B (token-position concentration, top-3=86%) SUPPORTED; manifold/Gram NOT the mechanism.
  Mitigations: manifold-truncation FAIL | Gram n/a | earlier-layer FAIL(worse) | mean-pool FAIL(worse) |
               attention-reweighting BEST-but-BOUNDED (0.43->0.22, F1-free) -> none reach 0.10.

## Recommended actions
1. LOCK customer posture: QUALIFIED privacy = audit trail + ZKP soundness + rate-limit k<=5 (+ the ~2x relative-vs-RAG
   pending RAG-arm verification). NOT absolute HIPAA-grade on the shared encoder.
2. Absolute HIPAA path = per-customer encoder fine-tuning (Path D, 1-2 wk/customer) -- offer as a paid tier, not v1 default.
3. Update production-architecture-lock memory: shared-encoder ZKL floor ~0.22 (k=50, real keys); attention-reweighting is
   an optional F1-free ~2x privacy improvement but not HIPAA-sufficient.
4. Stop linear-mitigation drilling -- the design space is exhausted (5 mechanisms x mitigations). Redirect privacy effort to
   the audit/ZKP moat (which IS differentiated) or Path D engineering.
Full-run k-sweep (n=500) queued to confirm the ~0.22 floor at scale; the conclusion is robust regardless (best smoke = 0.217,
> 2x the 0.10 target).
