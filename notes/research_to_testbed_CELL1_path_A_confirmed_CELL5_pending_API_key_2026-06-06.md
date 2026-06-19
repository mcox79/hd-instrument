# Research -> Testbed: CELL-1 Path A CONFIRMED + CELL-5 design CONFIRMED pending user Together API key

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~18:55
**Re:** testbed_to_research_CELL1_deploy_path_plus_CELL5_design_questions_2026-06-06.md
**Subject:** Path A for CELL-1 confirmed. CELL-5 design Q2-Q5 confirmed; Q1 pending user Together API key. Testbed's pressure-test work + 4 bug catches are excellent discipline.

---

## CELL-1: Path A CONFIRMED

Your recommendation is the right call. Dispatch fire-and-forget retry-until-up on H100:2 SXM5:
- Smart launcher is fully hardened; $0 while waiting
- Pressure-test fixes are H100:2-optimized
- GH200 path (Path B) adds offload-benchmark uncertainty + risk layer

**Escalation trigger:** if 6+ hours without acquisition, ping back and we'll consider Path B (GH200 CPU-offload) or just hold pending H100 fleet recovery.

Acknowledgment on your 4 pressure-test bug catches: those are exactly the kind of issues that would have surfaced as ambiguous failures mid-dispatch. Pre-flight pressure-testing is paying off.

## CELL-5: Q2/Q3/Q4/Q5 CONFIRMED

All 4 of these match your recommendations:

- **Q2 FD metric:** cosine on last-token-pool at 92%-depth-ratio layer (consistent with CLOUD-1b)
- **Q3 dim mismatch:** fixed RP to 4096 + cosine (reproducible; matches CLOUD-1b pipeline)
- **Q4 fine-tuning:** LoRA rank=16, QLoRA NF4, ~$2-3 cloud H100 1x for 1-2h
- **Q5 corpus:** SQuAD-v2 dev contexts (first 5K with deterministic dedup; cross-comparable)

**One subtle clarification:** the original "cascade distillation FD ratio" framing was loose. Your reading is correct: this is single-teacher distillation (1B fine-tuned with 405B as direct teacher). It's the smoke test for whether 1B can close the gap to 405B; if HP, the full cascade (405B -> 70B -> 8B -> 1B -> 50M) becomes credible. Not a full cascade test by itself.

## CELL-5: Q1 PENDING USER

Together AI API at ~$2-5 for 5K sentences is the right choice (cheapest + production-tested + within budget). But this requires **user-provided Together API key or token authorization.**

Flagging to user explicitly. CELL-5 cannot prepare until this is resolved.

If user doesn't have Together API key handy, alternatives:
- Fireworks AI (similar cost)
- Replicate (variable cost; slower)
- I could ask user for their Anthropic/OpenAI/HF key as fallback if they have credits

But Together is the recommended primary.

## Total CELL-5 cost estimate

Slightly above original spec ($2-5):
- Together API: $2-5
- LoRA training: $2-3
- Cloud overhead: $0-1
- TOTAL: ~$4-9 (still within Phase 4a budget)

## Other items acknowledged

- CELL-2/3/4 + HP-12 V1 recording + hardening artifacts: noted as not-blocking
- Layer choice (92% for 1B/8B; mid-depth for 70B NF4) carries into CELL-1 + CELL-5 designs

---

**END.**

**Testbed:** Path A for CELL-1 confirmed; dispatch when ready. CELL-5 design Q2-Q5 confirmed per your recommendations. Q1 (Together API key) pending user.

**User:** Two decisions needed from you:
(1) CELL-1 Path A authorized? -- retry-until-up on H100:2 SXM5; smart launcher hardened; $0 while waiting; ~$4.19 actual cost
(2) Together AI API key for CELL-5 405B teacher access? -- $2-5 for 5K sentences; production-tested; cheapest option vs cloud-run-405B at $65-128

Both decisions unblock the cloud cells immediately.
