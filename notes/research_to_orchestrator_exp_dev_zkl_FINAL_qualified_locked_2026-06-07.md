# Research -> Orchestrator + Exp-Dev + Testbed: ZKL privacy FINAL -- qualified posture locked

**From:** Research session
**To:** Orchestrator (primary) + Exp-Dev + Testbed
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_FINAL_lock_qualified_2026-06-07.md

## Settlement

The ZKL privacy investigation is settled. Linear-method privacy mitigations on Llama-1B
L15 shared encoder are bounded at ZKL(50) ~ 0.22. The 0.10 HIPAA-grade threshold is
not reachable via embedding-level interventions on the shared encoder.

## Customer-claim posture (LOCKED)

### Default tier (substrate v1)

- Audit (Merkle proofs per stored fact + per retrieval)
- ZKP soundness (zero-knowledge verification of retrieval correctness)
- GDPR EDPB Position 3 erasure (HMAC keystore closes hash-relinkage gap)
- Bitemporal as-of queries
- Rate-limit k <= 5 queries per session
- Qualified privacy: about 2x relative privacy improvement vs comparable RAG (pending
  RAG-arm verification)
- Optional FREE upgrade: attention-reweighting reduces ZKL ~2x at zero F1 cost (worth
  shipping as a default enhancement)

NOT absolute HIPAA-grade under aggressive membership inference attack. The qualified
posture is what we sell at default tier.

### Premium HIPAA tier (paid)

- Per-customer encoder fine-tuning (Path D from privacy 3x drill)
- 1-2 weeks engineering per customer
- Restores absolute HIPAA-grade ZKL by training encoder without Llama L15's position-
  concentrated geometry
- Charged accordingly

## Production architecture lock update (memory)

The production-architecture-lock memory entry should add:
- Llama-1B L15 left-pad shared-encoder ZKL floor ~0.22 (k=50, real keys, MarianMT
  paraphrase attack)
- Attention-reweighting (cap top-3 attended positions) is optional F1-free ~2x privacy
  improvement; offer as default enhancement
- Linear-method privacy mitigations on shared encoder are bounded (5 hypotheses x 5
  mitigations exhausted this session)
- Absolute HIPAA-grade requires per-customer encoder fine-tuning (Path D, 1-2 weeks
  per customer)

I will update the memory entry after this routing.

## What stops + what redirects

STOP:
- Linear-method privacy mitigation drilling (design space exhausted; conclusive result)
- Searching for shared-encoder ZKL <= 0.10 (not reachable)

REDIRECT TO:
- Audit/ZKP moat strengthening (this IS uniquely differentiated vs LLMs; lean on it)
- Path D engineering planning for the paid HIPAA tier (customer onboarding playbook,
  per-customer encoder training pipeline, cost model)
- RAG-arm verification of the ~2x relative privacy claim (still pending)

## What this means for the v1 demo

The v1 demo (substrate-augmented Qwen2.5-1.5B vs bare Qwen) DOES NOT depend on absolute
HIPAA-grade privacy. The +0.35 F1 north-star result holds regardless. The privacy story
in the v1 demo is the qualified posture + audit chain + GDPR + bitemporal + causal cluster.

The customer pitch for the v1 demo:
- "Substrate-augmented small LLM beats bare small LLM at multi-hop QA (+0.35 F1)"
- "Substrate provides cryptographic audit, GDPR EDPB Position 3 erasure, bitemporal
  queries, causal reasoning with counterfactual replay, qualified privacy with rate-limit"
- "For HIPAA-required deployments, premium tier provides per-customer encoder
  fine-tuning"

## Engineering items unblocked

- Production engineering for v1 substrate deployment proceeds with the qualified-privacy
  posture as baseline
- Attention-reweighting (option (a)) is a cheap optional enhancement; queue for v1.1
  if time allows after v1 ships
- Path D engineering planning queues separately for the premium HIPAA tier
- RAG-arm verification cell queued separately

## Cross-references

- ZKL FINAL result: notes/exp_dev_to_research_zkl_FINAL_lock_qualified_2026-06-07.md
- Cap k-sweep (decisive): exp_dev built; ZKL plateaus at 0.22 across k=3/5/8/12
- Full ladder summary in exp_dev_to_research_zkl_FINAL note
- Privacy 3x drill (Path D = per-customer fine-tuning): notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Hyp B supported: notes/exp_dev_to_research_zkl_hypB_supported_2026-06-07.md
- Cycle 151 attack methodology: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md

---

**END.**

**Orchestrator:** lock customer-claim posture per above. Update strategy decisions log.

**Exp-Dev:** stop linear-mitigation drilling. Queue RAG-arm verification cell for the
relative-vs-RAG claim. Path D engineering planning is a separate dispatch from me
when scoped.

**Testbed:** no immediate action; the v1 demo path doesn't change.

**User:** privacy investigation settled. Qualified posture locked. Tiered customer story
(default + premium HIPAA). v1 demo north-star result unaffected. Customer pitch updates
to lead with audit/ZKP/GDPR moat features over absolute-privacy claim.
