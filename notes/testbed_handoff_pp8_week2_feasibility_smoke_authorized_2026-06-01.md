# Testbed handoff: PP-8 Week 2 feasibility smoke AUTHORIZED ($50-150 cloud H100)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Trigger**: Week 1 GO/NO-GO H100 revalidation = DECISIVE GO (cap_map v309→v310 PP-8 LIFT 0.30-0.45 → 0.50-0.65 + PP-5 latency-budget CLOSED at H100 scope); 7-8 week PP-8 build COMMITTED
**Authorization**: USER EXPLICIT 2026-06-01 ~10:35 ET; budget ~$50-150
**Related handoffs**:
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (the parent build spec; ALL weeks 2-6 derive from this)
- `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` (Week 0 H100 verdict; deliverable)

## TL;DR

User authorized PP-8 Week 2 feasibility smoke at ~$50-150 cloud H100 budget. Week 1 GO is decisive; this is the first concrete step of the committed 7-8 week build. ~2-3 days work landing 1-2 cloud H100 sessions to validate the actual deep-integration architecture (Q-Former bridge + QLoRA fine-tune + Rescue C multi-hop autonomy) end-to-end at production scope.

## What to build

Per parent handoff `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`, Week 2 feasibility smoke is the first concrete validation of the architecture. The Week 0 H100 result validated LATENCY at the integrated-stack level (44ms p99 at seq=512). Week 2 smoke validates QUALITY at the integrated-stack level with the actual deep-integration components.

### Phase 1: Q-Former bridge wiring smoke (~3-5h cloud H100; ~$10-20)

- Wire the Q-Former bridge architecture (Tier 1 from the parent handoff — VQ-Bottleneck fallback is Tier 1.5 if Q-Former training instability emerges per external-reviewer Update 1)
- Validate forward path: query → Phi-3-mini-4bit prefix → Q-Former bridge → substrate codeword space → Path D retrieval → back through bridge → Phi-3 continuation
- Validate backward path: gradient signal flows through bridge (training viability check)
- Single-cloud H100 SXM5 session; ~30-60min wall

Acceptance criteria:
- Forward pass produces non-garbage substrate query (codeword Hamming distance to expected target < threshold)
- Backward pass produces non-zero gradient through bridge (training will at least move)
- Total session cost ≤ $20

### Phase 2: QLoRA fine-tune smoke (~12-24h cloud H100; ~$40-100)

- Apply QLoRA on a small toy dataset (5K-10K paired examples of "query + expected substrate retrieval + LLM continuation")
- Validate the bridge converges (loss decreases monotonically; no NaN/Inf; checkpoint saves cleanly)
- This is a smoke not a full train — first 100-500 steps with a defined validation eval at end
- Single H100 session, longer wall

Acceptance criteria:
- Loss decreases by ≥30% over first 200 steps (training is doing something)
- Validation eval at end shows >random retrieval quality (Q-Former actually produces useful queries)
- No NaN/Inf crashes
- Total session cost ≤ $100

### Phase 3 (optional, if Phase 1+2 land cleanly): Rescue C multi-hop smoke (~3-5h cloud H100; ~$10-30)

- Validate Path D depth=5 autonomous multi-hop with Q-Former-produced queries (not human-crafted)
- Tests whether the bridge produces queries that work at multi-hop depth, not just single-hop
- This is the Rescue C from the parent handoff — substrate retrieves chains via its own autonomous Path D, LLM consumes the results

Acceptance criteria:
- Multi-hop accuracy ≥ 0.5 (substrate-produced queries chain to non-random retrieval over 5 hops)
- No bridge-training-induced collapse (loss didn't go negative or diverge)
- Total session cost ≤ $30

### Total budget estimate

Phase 1: $10-20
Phase 2: $40-100
Phase 3 (optional): $10-30
**Cumulative envelope: $60-150** — within authorized $50-150 budget; if Phase 3 stretches, escalate before starting it.

## Mandatory: progress tracking + failure recovery (same as Week 0 H100 revalidation)

These are non-negotiable per yesterday + today's Lambda discipline:

1. **`generic_progress_wrapper.py` with `--total-cells` set per phase** — live cell-by-cell streaming in dashboard
2. **Per-step JSONL writes** — checkpoint after every training step (for Phase 2 QLoRA) and every validation eval (for Phases 1+3); SCP-back regardless of exit code
3. **Pre-launch snapshot + 5xx retry + orphan reconcile** per `feedback_cloud_launch_snapshot_reconcile` memory
4. **Always-verbose remote dispatch** per `feedback_always_verbose_remote_dispatch` memory
5. **Region-agnostic launch** + `wait_for_capacity` + `--stuck-booting-max-s 300` from today's improved cloud-dispatch toolkit
6. **Auto-terminate on session-completion regardless of result; verify 0 active instances after**
7. **If any phase wall exceeds 6 hours OR instance cost exceeds $150 OR daily cumulative exceeds $200, force-terminate and surface to user**

## Sequencing within this multi-phase smoke

- **Phase 1 dispatches first** (cheap; gates Phase 2 + 3)
- **Phase 2 dispatches after Phase 1 PASS** (or escalate to user if Phase 1 FAIL — could be Q-Former architectural issue; consider VQ-Bottleneck Tier 1.5 fallback)
- **Phase 3 dispatches after Phase 2 PASS** (or escalate to user if Phase 2 FAIL — could be QLoRA hyperparameter or dataset issue; design follow-on)

Phase outcomes feed forward; don't run Phase 2 without Phase 1 PASS.

## Verdict criteria for PP-8 Week 3 commitment

After this Week 2 smoke lands:

- **PASS all phases**: PP-8 Week 3+ build dispatchable; cap_map LIFT toward 0.55-0.70 (or higher); Week 3 builds Q-Former training proper + Phase-2 QLoRA at production scope
- **MIDDLE (Phase 1 or 2 lands borderline)**: PP-8 stays at 0.50-0.65; surface to user for "continue at scale or pivot to VQ-Bottleneck Tier 1.5" decision
- **FAIL (Phase 1 fundamentally broken)**: PP-8 P-band drops; pivot to VQ-Bottleneck Tier 1.5 OR re-scope toward Pattern B production-LLM as primary product
- **Total cost overrun (>$200)**: force-terminate; escalate

## Cost discipline (cumulative session tracking)

Today's cumulative Lambda spend ~$4.40-4.90 + this Week 2 budget ~$60-150 = ~$65-155 total day-end estimate.

Daily Lambda cap: $10 (per cost_tracker config); EXCEEDED today as expected for the strategic Week 0 + Week 1 work. Cap is informational not blocking; testbed already operates per user-authorized envelope.

## Coordination with PP-3 Phase 2

PP-3 audit-rotation Phase 2 (just-approved earlier this turn; ~6-9 days local engineering) and PP-8 Week 2 smoke can run in PARALLEL — PP-3 is local CPU work; PP-8 is cloud H100. Different resource pools; no contention.

Anthropic Phase 2 production query eval (~$20-50 pre-authorized) can ALSO run in parallel; no contention with either.

## What testbed will do next

- Move this handoff file to `routed_completed/` when Phase 1 dispatches (not when complete)
- Status_log entry HIGH for each phase outcome
- File deliverable `notes/testbed_pp8_week2_feasibility_smoke_v1_2026-06-01.md` when full multi-phase landing complete
- File routing back to orchestrator for the Week 3+ commitment decision (post-phase-3 outcome)

## Files referenced

- This handoff
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (parent spec)
- `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` (Week 0 H100 verdict)
- `notes/strategy_request_to_strategy_week1_gono_go_decision_2026-06-01.md` (Week 1 GO recommendation; closed by today's verdict)
- Cap_map v310 PP-8 row + PP-5 row
- `tools/cloud/launch_experiment.py` + `tools/cloud/generic_progress_wrapper.py` + `tools/cloud/cost_tracker.py` (mandatory infra)

## Closing this routing

Testbed moves to `routed_completed/` when Phase 1 dispatches (initiate, not complete).
