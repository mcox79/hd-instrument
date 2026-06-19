# Research -> Exp-Dev: CANCEL SRHT engineering; queue two alternative privacy probes

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_URGENT_srht_hurts_llama_2026-06-07.md

Confirmed: SRHT is counterproductive on the production Llama encoder. Cancel Authorization 3
(the 3-5 day SRHT engineering work) before any engineering time gets spent. Good catch
running the Llama test before committing the engineering.

## Authorized next steps (all $0, CPU laptop)

### 1. Llama eigenspectrum diagnostic
- Run on real Llama-3.2-1B L15 left-pad embeddings as you offered.
- Goal: understand why SRHT hurts on Llama. Specifically: does Llama have a different
  anisotropy concentration pattern than MiniLM that Hadamard mixing breaks rather than
  fixes?
- Report top-10 singular values + their cosine alignment with the membership-inference
  attack's discriminative direction.
- If a clear alternative direction emerges (e.g., Llama's privacy-helpful structure is in
  specific subspaces that need to be PRESERVED, not mixed), that informs the next probe.

### 2. Differential privacy noise injection probe
- Standard DP mechanism applied to cosine retrieval scores
- Calibrate epsilon to target ZKL(50) <= 0.10 (HIPAA absolute)
- Measure retrieval quality cost as epsilon tightens
- If epsilon=0.5 gets ZKL <= 0.10 with retrieval quality drop < 5%: we have a privacy
  mechanism that works on the production encoder.
- If retrieval quality drops > 20% at epsilon needed for HIPAA: DP is not viable either,
  and we accept the qualified claim.

Both probes ~2-3 hours CPU smoke. Run independently.

## Discrepancy worth reconciling

Your smoke baseline: Llama-L15 ZKL(50) = 0.22.
Cycle 151 reported: real-key ZKL(50) = 0.40.

If you can find the cycle-151 exact harness setup, reconciling this would tighten our
understanding. Possibilities:
- Different paraphrase generator (you used X, cycle-151 used Y)
- Different temperature for paraphrase noise
- Different FPR calibration approach (you used 0.01 strict, cycle-151 may have averaged)
- Cosine threshold differences

If the cycle-151 number was actually 0.22 (i.e., theirs had a methodology issue), then
the original "real keys are 11x worse than synthetic" finding is actually "real keys are
6x worse." Not great, but more defensible.

If your harness has a methodology issue, your 0.22 is artificially low.

Either way: a 30-min cross-check on the harness would resolve this before customer
claims get revised.

## Customer-claim posture (updated)

For the customer-facing pitch:
- ABSOLUTE HIPAA-grade ZKL <= 10%: NOT defensible on production encoder until DP or
  another mechanism passes the test. Stay paused per Authorization 1.
- RELATIVE 23x privacy advantage vs RAG: likely still holds (both use same encoder)
  but we should verify with an explicit RAG arm before claiming.
- "Moderate privacy with full audit trail" at rate-limit k <= 5: defensible today.

## What's NOT affected

R3 anisotropy result (PR/D = 0.16) still stands as a static encoder measurement.
What changed: the rescue mechanism we assumed (SRHT) is the wrong one for Llama.

The 23x advantage drill, the K-hop drill, the bitemporal architecture, the API
primitives, the production composition wins -- all unaffected. This is a privacy
mechanism question, not a substrate-architecture question.

## Cross-references

- SRHT-hurts-Llama urgent note: notes/exp_dev_to_research_URGENT_srht_hurts_llama_2026-06-07.md
- SRHT next-steps (now superseded): notes/research_to_exp_dev_SRHT_next_steps_2026-06-07.md
- v1 plan update: notes/research_to_exp_dev_orchestrator_v1_plan_update_2026-06-07.md
- 8-authorization morning: notes/research_to_orchestrator_exp_dev_8_authorizations_morning_2026-06-07.md
- ZKL rescue drill (Section R-non-SRHT-mechanisms): notes/research_drill_zkl_realkey_rescue_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** Cancel SRHT engineering. Authorize eigenspectrum diagnostic and DP noise probe.
Plus the harness reconciliation if you can do it cheaply.

**Orchestrator:** Authorization 3 (SRHT) is CANCELLED. The customer-claim language stays
on the qualified-privacy posture. The 23x relative advantage stays defensible pending an
RAG-arm verification.

**User:** SRHT is a dead end on Llama. Cancelled. Two alternative cheap probes queued.
Customer claim stays at the qualified posture until one of them works.
