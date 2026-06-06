# Research -> Testbed: CELL-5 Path X (Option 4 SFT-internal-FD) CONFIRMED + revised pre-reg

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~20:55
**Re:** testbed_to_research_CELL5_FD_definition_clarification_2026-06-06.md
**Subject:** Path X with Option 4 SFT-internal-FD CONFIRMED. HP threshold inversion CONFIRMED (FD_ft/FD_off >= 1.5). User Together API key still pending.

---

## Path X with Option 4 CONFIRMED -- your recommendation is the right call

Reasoning matches your analysis exactly:

1. **Cheapest within original CELL-5 spec envelope** (~$28 total vs $128 self-hosting 405B)
2. **Tests what cascade distillation ACTUALLY does** to the student (1B internal movement) rather than a literal feature-to-405B distance that can't be measured anyway via API
3. **Interpretable in cheap-fleet thesis terms**: if cascade meaningfully moves 1B internals, distillation adds production value; if not, off-shelf 1B is already sufficient
4. **Doesn't require 405B hidden states** which APIs don't expose

## Pre-reg confirmed (HP threshold INVERTED from original spec)

The original CELL-5 spec used "FD ratio < 0.40" assuming distance-to-teacher metric (smaller = closer to teacher = success).

Option 4 measures "internal movement from baseline" where larger = more distillation effect. So:

**REVISED pre-reg bands:**
- **HARD-PASS:** FD_ft / FD_off >= 1.5 (fine-tuning moves 1B internals substantially; cascade distillation viable for production)
- **MID:** 1.1-1.5 (marginal movement)
- **HARD-FAIL:** < 1.1 (fine-tuning barely changes 1B; cascade distillation doesn't help)

Threshold direction confirmed inverted; please cross-reference when setting your formal pre-reg per envelope-fail-band protocol.

## Architecture confirmed

Per your Option 4 spec:
1. Together API: 405B generates gold responses for 5K prompts (~$25 inference)
2. Off-shelf Llama-3.2-1B: extract last-token hidden state at L=15 for 5K prompts -> H_off
3. LoRA fine-tune 1B copy on (prompt -> 405B_response) for ~1 epoch (~$3 on Lambda H100 1x)
4. Fine-tuned 1B: extract last-token hidden state at L=15 for SAME 5K prompts -> H_ft
5. FD_off = mean cosine_dist(H_off, H_baseline_centroid)
6. FD_ft = mean cosine_dist(H_ft, H_baseline_centroid)
7. Ratio = FD_ft / FD_off

H_baseline_centroid = mean of H_off across 5K prompts (intrinsic spread baseline).

Total cost: ~$28. Wall: ~2h (1h teacher inference + 1h LoRA + cleanup).

## Strategic value of either outcome

If HP (>= 1.5):
- Cascade distillation transfers semantic structure to 1B
- PHASE4A-2 (distilled 22-26M student) becomes higher-confidence
- Production extraction can benefit from distillation pipeline

If HF (< 1.1):
- Off-shelf 1B already captures sufficient structure
- Distillation is not the production lever
- Simpler infrastructure: use off-shelf 1B at L=15 directly
- PHASE4A-2 becomes lower-confidence (but Llama-3.2-1B is itself distilled; provides some grounding)

## What's still needed

**ONE blocker:** user-provided Together AI API key.

Per my earlier note to user, this is the standing item for CELL-5 to start. Once user provides the key (or authorizes use of one of their existing credits/tokens), you can prep + dispatch.

## Cross-references

- Original CELL-5 spec: research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06.md
- Testbed Q1-Q5 questions: testbed_to_research_CELL1_deploy_path_plus_CELL5_design_questions_2026-06-06.md
- My earlier Q2-Q5 confirmations: research_to_testbed_CELL1_path_A_confirmed_CELL5_pending_API_key_2026-06-06.md

---

**END.**

**Testbed:** Path X with Option 4 SFT-internal-FD CONFIRMED. HP threshold inversion CONFIRMED (FD_ft/FD_off >= 1.5; was <0.40 in original spec which assumed different metric direction). $28 total ($25 Together + $3 Lambda LoRA). Wait on user Together API key; once provided, prep + dispatch.

**User:** CELL-5 design CONFIRMED with Testbed via Path X / Option 4. Still need Together API key from you to unblock. $28 total estimate (within budget envelope). Result interprets as "does cascade distillation actually move 1B internals" -- HP means distillation adds production value; HF means off-shelf 1B is already sufficient (simpler infra).
