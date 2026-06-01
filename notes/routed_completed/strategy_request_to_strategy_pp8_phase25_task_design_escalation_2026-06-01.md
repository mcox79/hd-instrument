# Strategy request: PP-8 Phase 2.5 — task-design escalation (3-point convergence on 0% val)

**From**: testbed
**To**: strategy (orchestrator) + user
**Date**: 2026-06-01
**Trigger**: 3rd iteration of Phase 2 family (Phase 2.5 soft-substrate) lands MIDDLE with val=0%, identical to STE iteration + Phase 2 baseline. Pattern points to task design, not gradient pathology — exceeds the pre-approval scope's "gradient pathology" trigger
**Related**: `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md` (full deliverable with diagnosis)

## TL;DR

The 3-data-point convergence on val=0% across radically different gradient strategies (bypass / STE / soft-attention) is too clean to be gradient pathology. The bottleneck is the toy task design itself: my dataset has no learnable signal connecting "Key {idx}: " text to the substrate's randomly-built bipolar codeword for that key index. Even infinite training-set memorization wouldn't extend to held-out val keys because the mapping is random by construction.

Surfacing for user/strategy decision before consuming iteration 3 of the contingency budget on what would likely be another 0% result.

## The 3-point pattern

| Variant | Mode | Loss decrease | Val top-1 | Cost |
|---|---|---|---|---|
| Phase 2 | substrate bypassed | 44.5% | 0.000% | $1.36 |
| Phase 2.5 STE | argmax + STE backward | 37.8% | 0.000% | $1.30 |
| Phase 2.5 soft | softmax-attention | 42.7% | 0.000% | $0.85 |

3 distinct gradient pathways. 3 distinct loss decreases. 1 identical val accuracy: zero.

## Why I'm escalating instead of running iteration 3

The orchestrator's pre-approval explicitly trigger for architectural-pivot was "STE attempts fail to converge and Gumbel-softmax also fails." That assumed gradient pathology was the bottleneck. The empirical finding is now stronger: even the cleanest differentiable variant (soft-attention; same loss-decrease pattern as bypass) does NOT improve val. The bottleneck is upstream of gradient design — it's the task itself.

Iteration 3 (Gumbel-softmax hard-ST) would likely produce another 0% val. Cost: ~$1-2 + 1-2h engineering. Marginal information gain: very low (probably confirms the pattern; doesn't change diagnosis).

I'd rather use the remaining contingency budget on Path 1c (sanity-check the architecture without held-out keys) and Path 1a (principled task redesign with Phi-3-hidden-state-derived key codewords). Both are within remaining ~$22 budget.

## Three paths forward (full disposition in deliverable)

### Path 1: Redesign the task to be substrate-substantive

- **1c (cheap sanity)**: train on overlapping train+val keys; verify ANY val signal achievable. ~30 min eng + ~$1-2.
- **1a (principled redesign)**: key codewords derived from Phi-3 hidden states; substrate stores hidden-state-keyed facts; LLM can in-principle learn to retrieve via the alignment. ~3-4h eng + ~$2-5.
- 1b (orthogonal): substrate built from training-data dictionary; less aligned with current architecture but possible. ~2-3h eng.

### Path 2: Concede the toy task; move to Phase 3 (Rescue C multi-hop)

Phase 3 is INDEPENDENT measurement: substrate's autonomous multi-hop retrieval + LLM consumption. Doesn't require held-out generalization the toy task was attempting. $10-30 per parent handoff.

### Path 3: Accept Phase 2.5 result; document; defer

Cap_map caveat: "Phase 2 + 2.5 (3 iterations) produced identical 0% val on the toy associative-recall task. The bottleneck is empirically demonstrated to be the toy task design (random key_text-to-token mapping). Bridge trainability validated (loss decreases 37-44%)."

PP-8 P-band unchanged. Continue Week 3+ build with substrate-substantive task design.

## My recommendation

**Path 1c first (cheap sanity check)**, then **Path 1a (principled redesign)**.

- Path 1c (sanity check) protects against "there's an additional bug I haven't identified" before committing to redesign. Worst case: confirms architecture is fine; cost $1-2.
- Path 1a (principled redesign with Phi-3-hidden-derived key codewords) is the proper Phase 2 design that actually tests the strategic claim. Cost $2-5.

Total: ~$3-7 within remaining contingency budget. Net cumulative session Lambda would still be under $14.

Alternative: if user thinks Phase 2's bridge-trainability finding is already sufficient empirical signal for PP-8 (loss decreases are clean across 3 modes; substrate-utility-on-this-task is unmeasured but the bridge IS architecturally sound), Path 3 (defer) is cleanest.

## Cap_map implications (orchestrator scope)

Regardless of path:
- PP-8 row stays at 0.55-0.65 (Phase 1 architectural integration PASS already booked it there)
- Caveat addition: see Path 3 phrasing

If Path 1c+1a returns substrate-substantive val>random: PP-8 LIFT possible to 0.60-0.75
If Path 1c fails (architecture bug exists): PP-8 P-band drops; architectural debugging needed
If Path 1a returns 0% even with proper task design: PP-8 P-band drops; substrate-LLM coupling story is empirically weaker than hoped

## Cost state

- Cumulative today: $6.53
- Remaining contingency budget: ~$22 / 1 iteration
- Path 1c: ~$1-2
- Path 1a: ~$2-5
- All paths within budget

## What testbed will do, by default if no direction lands

- Hold autonomously; do NOT consume iteration 3 of the STE/Gumbel budget on what's likely a 4th 0% data point
- Pick up Anthropic Phase 2 production query eval (different resource pool; pre-authorized $20-50) as parallel work
- Move other pending items as bandwidth permits

## Files referenced

- This routing
- `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md` (full deliverable)
- `notes/testbed_pp8_week2_phase25_ste_v1_2026-06-01.md` (STE iteration deliverable)
- `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (Phase 2 baseline deliverable)
- `data/lambda_batch_results/pp8_w2_p25_soft_substrate_h100_v1_n4096_8b8d49a3/` (soft-substrate full results)


---
**ROUTED-COMPLETED**: Acted-on 2026-06-01: Path 1c AUTHORIZED + Path 1a research drill filed in parallel; testbed response filed (strategy_response_to_testbed_pp8_phase25_path_1c_authorized_2026-06-01.md)
