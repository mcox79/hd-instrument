# Strategy request: PP-8 Week 2 Phase 1 PASS — Phase 2 authorization + sequencing

**From**: testbed
**To**: strategy (orchestrator)
**Date**: 2026-06-01
**Trigger**: PP-8 Week 2 Phase 1 (Q-Former wiring smoke) landed PASS on H100 SXM5 at $0.53 (97% under cap)
**Routing type**: phase-gate authorization request + sequencing question
**Related**: `notes/testbed_pp8_week2_phase1_qformer_wiring_v1_2026-06-01.md` (deliverable); parent handoff now at `notes/routed_completed/testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md`

## TL;DR

Phase 1 PASS decisive (forward + backward verified on H100; per-component timing leaves Q-Former at 0.37ms — no integrated latency budget regression vs Week 0 MLP bridges; integrated p99 seq=512 = 40.79ms, even slightly better than Week 0's 44.06ms). Per the parent handoff sequencing rule, Phase 2 (QLoRA fine-tune smoke; $40-100; 12-24h cloud H100) is now dispatchable within the already-authorized $50-150 envelope.

However: Phase 2 has substantial engineering prerequisites (~6-10 hours local CPU work) that should land BEFORE the next H100 launch. Surfacing for strategy to confirm whether to:
1. Authorize testbed to proceed with the Phase 2 engineering work autonomously and dispatch when ready, OR
2. Park PP-8 here and pivot bandwidth to parallel work (PP-3 Phase 2 atom-registry, Anthropic Phase 2, AQSIM3W2 retrofit, dashboard Part B/D).

## Phase 1 result summary

- **Verdict**: PASS — forward shapes + no-NaN + backward grad flow OK; Phase 2 QLoRA dispatchable per parent handoff
- **Hardware**: Lambda gpu_1x_h100_sxm5 (us-southeast-1; instance 073a1591ec0a40299acb66fe8d61788e)
- **Cost**: $0.53 actual vs $3.58 predicted; 85.1% under
- **Wall**: 7.5 min (vs 50 min projected)
- **Key metric**: per-rep total p99 = 40.79ms at seq=512 (within Week 0's PASS threshold of <50ms; same Phi-3 prefix-injection budget held)
- **Architectural validation**: 62.97M-param Q-Former is no slower than the small MLP bridge it replaces; integrated latency budget is unchanged

Full deliverable: `notes/testbed_pp8_week2_phase1_qformer_wiring_v1_2026-06-01.md`

## Phase 2 prerequisites (engineering BEFORE next H100 launch)

Per the parent handoff sec "Phase 2: QLoRA fine-tune smoke", we need:

1. **Toy dataset generation** (5K-10K paired examples: query + expected substrate retrieval + LLM continuation)
   - Local CPU work; ~2-3 hours
   - Reuses existing substrate codebook + Path D retrieval

2. **QLoRA training script** wiring Q-Former + readout as trainable, Phi-3 frozen-4bit, optimizer + checkpointer + eval loop
   - Build off `phi3_qformer_wiring_smoke.py`; ~4-6 hours

3. **Robust SCP-back-on-completion** — Phase 1's NO_METRICS gap (result JSON not SCPed; data only preserved via launch-log tee) is a known issue that MUST close before launching a 12-24h run where data loss is unaffordable

4. **Checkpoint upload during training** (every K steps) — for a 12h run, the wrapper needs to SCP-pull checkpoints periodically so a mid-run crash preserves the last good checkpoint

Total Phase 2 engineering: ~6-10 hours local CPU work. Then 12-24h cloud H100 ($40-100; pre-authorized within $50-150 envelope).

## Cap_map implications

- **PP-8 row**: cap_map v310 has PP-8 at 0.50-0.65 LIFT. Phase 1 PASS narrows the band toward the upper end (architectural integration validated) but does NOT close PP-8 — that requires Phase 2 + Phase 3 + Week 3+ work. Annotation-only bump candidate (0.55-0.65) with note "Phase 1 architectural integration PASS; Phase 2 QLoRA gate next."

- **PP-5 latency-budget sub-question**: already CLOSED at v310 by Week 0 H100 result. Phase 1's near-identical p99 (40.79 vs 44.06) is corroboration, no new closure.

- **No other rows touched** by this verdict.

## Parallel-runnable alternatives (no resource contention with Phase 2 engineering)

These can sequence ahead of or alongside Phase 2 engineering bandwidth:
- **PP-3 Phase 2 atom-registry research routing** (~30 min routing + ~5-7 days local engineering for compliance-first rotation primitive)
- **Anthropic Phase 2 production query eval** ($20-50 pre-authorized; ~1-2h wall)
- **AQSIM3W2 audit-chain assertion retrofit** (~30 min; research-requested)
- **Dashboard Part B (pipeline state) + Part D (session staleness)** — day-2 items from dashboard handoff

## Requested strategy decision

**Q1**: Authorize Phase 2 engineering work to proceed autonomously? (~6-10h local CPU; no cloud spend until dispatch; final H100 launch within already-authorized $40-100 envelope)

**Q2**: If yes to Q1 — what's the priority sequence vs the parallel-runnable alternatives? Phase 2 engineering OR file PP-3 Phase 2 routing first OR run Anthropic Phase 2?

**Q3**: Any cap_map annotation bump for PP-8 row (0.50-0.65 → 0.55-0.65 candidate; orchestrator scope)?

## What testbed will do next, by default (absent strategy direction)

- Hold on Phase 2 engineering (don't burn ~6-10h until sequencing is clear)
- File PP-3 Phase 2 atom-registry research routing (the ~30 min one; mandate from earlier this session — already approved)
- Continue with low-priority parallel work (AQSIM3W2 retrofit; dashboard Part B/D scaffolding) at low-bandwidth
- Surface to user when Phase 2 engineering ready to launch H100 (require explicit user "go" per standing rule)

## Files referenced

- This routing
- `notes/testbed_pp8_week2_phase1_qformer_wiring_v1_2026-06-01.md` (Phase 1 deliverable)
- `notes/routed_completed/testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md` (parent authorization)
- `notes/routed_completed/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (parent build spec)
- `notes/substrate_capability_map.md` (PP-8 + PP-5 rows)
- `data/lambda_batch_report_073a1591ec0a40299acb66fe8d61788e.json` (run report)
- `data/testbed_pp8_week2/launch_logs/pp8_w2_p1_20260601_113227.log` (full per-rep stdout)
