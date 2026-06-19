# Strategy response: PP-8 Phase 2.5 Path A AUTHORIZED (substrate-in-loop training + key resolver)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/strategy_request_to_strategy_pp8_phase2_middle_verdict_path_decision_2026-06-01.md`
**Authorization**: USER (via orchestrator) per the pre-approval scope in `notes/testbed_handoff_pp8_phase2_dispatch_preapproved_2026-06-01.md` (within remaining $50-150 PP-8 Week 2 envelope; non-architectural-pivot diagnostic continuation)

## TL;DR

**Path A APPROVED.** Build Phase 2.5 (substrate-in-loop training with key resolver + STE/Gumbel through Path D); re-run Phase 2 on H100. ~1-2h engineering + ~$2-5 H100. Testbed dispatches autonomously when engineering is done; no further explicit go.

## Why Path A over B / C

- **Path B** (redesign toy task to not need substrate): defeats the substrate-LLM coupling question; useful only as a control IF Path A's gradient flow turns out to be intractable. Don't dispatch unless that contingency triggers.
- **Path C** (accept MIDDLE; defer to bandwidth opens): leaves the load-bearing PP-8 question (does substrate contribute to bridge usefulness) unresolved. Phase 2 deliverable is empirically informative but PP-8 row band stays unchanged at 0.55-0.65 without Phase 2.5 evidence. Pause vs. progress tradeoff favors Phase 2.5.
- **Path A**: cheap ($2-5), cleanly diagnostic (5-10% val accuracy = 50-100x random = first empirical evidence of substrate utility in the LLM output path), architectural change is the natural continuation not a pivot.

## Strategic rationale for "this is within pre-approval"

The earlier dispatch pre-approval (commit ad38d09; `notes/testbed_handoff_pp8_phase2_dispatch_preapproved_2026-06-01.md`) explicitly STILL GATES:
- Phase 3 dispatch (Rescue C multi-hop smoke)
- Architectural pivots (e.g., switching to VQ-Bottleneck Tier 1.5)
- Cost overruns (Phase 2 cost > $100 mid-engineering; actuals > $150)
- Total daily cumulative > $200

Phase 2.5 is NONE of these:
- It's a re-run of Phase 2 with corrected pipeline (substrate-in-loop), not Phase 3
- It's the natural continuation of the Phase 2 finding, not an architectural pivot (Q-Former + Phi-3 + LoRA + Path D core architecture unchanged; only training-time substrate-coupling added)
- Cost ($2-5) is far under any threshold
- Daily cumulative ($6.29 + $2-5 = ~$11-15) is well under $200

Therefore Phase 2.5 is in the spirit of the pre-approval. Testbed dispatches autonomously.

## Cap_map implications (will be applied in next strategy_scribe bump)

Per testbed's read: PP-8 row stays at 0.55-0.65 from Phase 2 alone. Phase 2.5 verdict will move the band:

- **PASS** (val top-1 >= 5% on held-out): PP-8 LIFT 0.55-0.65 → 0.60-0.75 (first empirical evidence of substrate contribution; substantial)
- **MIDDLE** (val top-1 in [1%, 5%]): PP-8 stays 0.55-0.65 + caveat "substrate contributes but training pipeline needs further refinement; Phase 2.6 or alternative gradient-flow design likely needed"
- **FAIL** (val top-1 < 1%): PP-8 P-band DROPS toward 0.45-0.60 + caveat "substrate-in-loop training fails to extract substrate signal; investigates whether Q-Former representation is fundamentally lossy OR whether STE/Gumbel through Path D has unfixable gradient pathology"

The Phase 2.5 verdict IS the substantive PP-8 read; that's why dispatching it is high-priority.

## What testbed does next

1. Begin Phase 2.5 engineering (~1-2h):
   - Add bipolar → codebook-index resolver (`argmax(codebook @ bipolar.T)`)
   - Replace soft-tanh → bridge with sign → resolve → Path D → codeword → bridge
   - Handle non-differentiability: STE on argmax (first attempt) OR Gumbel-softmax relaxation (fallback)
2. Dispatch H100 Phase 2.5 session whenever engineering is complete (per pre-approval autonomy)
3. Same progress-tracking + checkpoint-upload + SCP-back-on-completion discipline as Phase 2
4. Status_log entry HIGH at dispatch + at completion
5. File deliverable + Phase 2.5 verdict routing post-completion

## Gradient-flow risk + contingency

Testbed flagged: "STE/Gumbel through Path D may not gradient cleanly; if so, need iterative experimentation on the gradient flow design (additional engineering)."

Pre-authorize the contingency: if STE attempts fail to converge and Gumbel-softmax also fails, testbed has the engineering bandwidth to iterate (~2-3 additional 1-2h engineering cycles) WITHIN the existing PP-8 Week 2 envelope before escalating to user for architectural-pivot decision. Each cycle = additional $2-5 H100 + ~1-2h engineering; if cumulative cycles exceed 3 OR cumulative cost exceeds $30 OR cumulative wall exceeds 1 working-day, escalate to user.

If STE/Gumbel fundamentally don't work for Path D (gradient-pathology proven via 3 iterations), THAT is the architectural-pivot trigger that the pre-approval gates. At that point testbed surfaces to user with the empirical evidence + proposed pivot (VQ-Bottleneck Tier 1.5 OR alternative gradient-routing design).

## Parallel work that can sequence ahead of / alongside Phase 2.5 engineering

Per testbed's "default if no Path direction" list, these can run in parallel since they don't compete for the same testbed-engineering bandwidth:

- **PP-3 Phase 2 atom-registry status check** (waiting on research; ETA ~2-4h per atom-registry research routing)
- **AQSIM3W2 cert-chain engineering** (per the AQSIM end-to-end audit chain assertion deliverable testbed just filed at 12:25; ties to today's strategic 3-way HARD_PASS claim)
- **Anthropic Phase 2 production query eval** (pre-authorized $20-50; different resource pool entirely)

## Files referenced

- `notes/strategy_request_to_strategy_pp8_phase2_middle_verdict_path_decision_2026-06-01.md` (source routing; CLOSE after testbed reads this)
- `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (Phase 2 deliverable; STAYS in notes/ as audit trail)
- `notes/testbed_handoff_pp8_phase2_dispatch_preapproved_2026-06-01.md` (the pre-approval this response invokes; ALREADY in notes/ as orchestrator-issued)
- `data/lambda_batch_results/pp8_w2_p2_qlora_finetune_h100_v1_n4096_b31a433d/` (Phase 2 full results)
- Cap_map v312 PP-8 row at 0.55-0.65

## Closing this response

Move both this response AND source routing to `routed_completed/` after testbed reads + begins Phase 2.5 engineering.
