# Testbed decisions 2026-06-01

Session-end bookmark so the next testbed session resumes cleanly.

## Headline state

- **Week 0 Missing 7 H100 revalidation: GO** — integrated p99 at seq=512 = 44.06ms (under 80ms GO threshold + under 50ms Phi-3-alone secondary threshold). 4.9x speedup vs 4060 Ti FAIL (217.7ms p99 yesterday). Orchestrator processed routing immediately; cap_map v309 → v310; PP-8 LIFTed 0.30-0.45 → 0.50-0.65; PP-5 latency-budget sub-question CLOSED.
- **PP-8 Week 2 feasibility smoke AUTHORIZED** by user (~$50-150 cloud H100; 3 phases). Phase 1 = Q-Former bridge wiring (~$10-20). This is the IMMEDIATE next-session priority.
- **PP-3 Phase 1 audit-trail rotation drill COMPLETE** — key finding: GDPR right-to-erase forces rotation primitives regardless of capacity scale. Phase 2 reframe approved (Option c compliance-first; LIFT 0.55-0.70 → 0.62-0.75); atom-registry coordination with PP-12 mandated.
- **Anthropic Phase 1 PASS 100% yesterday**; Phase 2 ($20-50) pre-authorized; Week 1 unblocked.
- **Cumulative Lambda session spend ~$4.40-4.90**; cumulative Anthropic ~$0.45.

## Major deliverables this session (in chronological order)

1. Per-rep JSONL + per-rep stdout for failure recovery (commits 9cc1b10 + e7e22ca)
2. Capacity gate + stuck-booting fast-fail + region-agnostic launch (commits 89f17eb + f9c784c + bb708ad)
3. Pillow + transformers + bitsandbytes + accelerate + anthropic added to requirements_cloud.txt (commit bb708ad)
4. cp1252 print fix in launch_batch.py (commit abdcf53)
5. PP-3 Phase 1 deliverable `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` + reframe routing
6. Week 0 H100 revalidation deliverable `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` + Week 1 GO/NO-GO routing
7. Dashboard Inbox tab + heartbeat_watchdog auto-ping (Part A + Part C layer 1 of dashboard handoff; commits abdcf53 + f501211)
8. Dashboard Inbox sender-attribution bug fix (commit 667e6ed; then sender-parser tolerance commit f2cc39b)
9. Q-Former bridge module + local CPU smoke pass (commit bcc5421; 77.66M total params; forward shapes OK + backward gradient flow validated)
10. Inbox housekeeping: testbed inbox depth 11 → 3 (8 actioned handoffs moved to routed_completed)

## What's in testbed's inbox right now (3 items)

1. `testbed_handoff_reasoning_amortization_economics_build_2026-05-31.md` — 2-3 week engineering build; sequenced AFTER Week 1 GO (now satisfied; can start when bandwidth opens up).
2. `testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` — research-requested ~30 min retrofit on existing AQSIM3W2 v1 data; not blocking.
3. `testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md` — THE IMMEDIATE NEXT-SESSION PRIORITY.

## Next-session start here: PP-8 Week 2 Phase 1 H100 dispatch

Phase 1 = Q-Former bridge wiring smoke. Phase 1 PASS gates Phase 2 (QLoRA fine-tune; $40-100). 4 concrete steps:

1. Write `testbed/llm_integration/phi3_qformer_wiring_smoke.py`. Reuse `phi3_integrated_latency.py` scaffolding; substitute `QFormerBridge` + `QueryReadoutHead` from already-shipped `qformer_bridge.py`. Wires:
   - text prompt → Phi-3 prefill → extract [QUERY] hidden state
   - hidden → readout (tanh) → bipolar (sign at deployment)
   - substrate Path D depth=5 → retrieved codeword
   - codeword → Q-Former → 8 prefix tokens (R^3072)
   - prefix tokens injected into Phi-3 → decode 1 continuation token
   - synthetic loss (MSE on prefix or CE on next-token) → backward → verify Q-Former + readout grads flow
2. Local CPU smoke validates wiring before cloud spend.
3. Launch on H100 SXM5 via `tools/cloud/launch_batch.py` with batch config; capacity gate + 300s fast-fail + per-rep JSONL all already mandatory in launcher.
4. On Phase 1 PASS: file routing for Phase 2 (`strategy_request_to_strategy_pp8_phase2_authorization_2026-06-XX.md`).

Acceptance criteria from orchestrator handoff:
- Forward pass produces non-garbage substrate query (Hamming distance to expected target — at SMOKE with untrained weights, ~N/2 random expected; shape + no-NaN is the load-bearing check).
- Backward pass produces non-zero gradient through bridge (training will at least move) — ALREADY validated locally via `qformer_bridge.py:smoke_test()` for the bridge in isolation; H100 confirms integration-level behavior.
- Total session cost ≤ $20.

## Parallel-runnable next-session work (no resource contention with PP-8 Phase 1)

- PP-3 Phase 2 atom-registry research routing (file `strategy_request_to_strategy_atom_registry_design_review_2026-06-XX.md` to orchestrator; ~30 min). Then ~5-7 days local engineering for the compliance-first rotation primitive design.
- Anthropic Phase 2 production query evaluation ($20-50 pre-authorized; ~1-2h wall).
- AQSIM3W2 audit-chain assertion retrofit (~30 min; research-requested via `testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md`).
- Dashboard Part B (pipeline state view) + Part D (session staleness; day-2 items per dashboard handoff).
- Hard-neg full 50K tuple generation (~$50-350; awaiting EXPLICIT user authorization; pre-authorized only as principle).

## Deferred / not-blocking

- Lambda API key rotation (the key is in this session's transcript per the earlier sloppy grep; rotate at user's convenience).
- N=8192 store cosmetic fix (Kerdock log2 constraint).
- `phi3_token_latency.py` script's verdict band cosmetic (compares against substrate-budget-remaining instead of integrated-budget; numbers are correct, label is misleading).

## Cumulative Lambda spend tracking (best estimate)

- Yesterday Lambda v1 (V1 canary chain): $0.80
- Yesterday Lambda v1 cheap-batch (3 anchors): $0.60
- Yesterday Lambda v2 batch (3 anchors): $0.42
- Today H100 attempts 1-5 (revalidation; 4 failed + 1 succeeded): ~$2.60-3.10 real spend
- Today's cost_tracker showed ~$2.48 cumulative (under-reports the failed-launch boot-billing)
- **Real estimate: $4.40-4.90**

Anthropic API:
- Phase 1 smoke (3 iterations: MIDDLE → PASS prompt-tighten → PASS edit-fix): ~$0.45 total
- Hard-neg 5-tuple smoke: ~$0.03
- Auth ping: $0.0001
- **Cumulative Anthropic: ~$0.48**

Within all user-authorized envelopes ($5-15 for H100 revalidation; $20-50 pre-authorized for Phase 2; $50-150 newly-authorized for PP-8 Week 2).

## Files of interest

- This bookmark
- `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` (Week 0 GO)
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (PP-3 Phase 1)
- `notes/strategy_request_to_strategy_week1_gono_go_decision_2026-06-01.md` (Week 1 routing; orchestrator processed)
- `notes/strategy_request_to_strategy_pp3_phase1_findings_2026-06-01.md` (PP-3 reframe routing; orchestrator processed)
- `testbed/llm_integration/qformer_bridge.py` (just-shipped Q-Former + readout)
- `tools/cloud/lambda_client.py` (`wait_for_capacity` helper)
- `tools/cloud/launch_batch.py` (capacity gate + fast-fail + region-agnostic + cp1252 fix)
- `tools/dashboard/poller.py` (inbox_routings field + `_build_inbox_routings` helper)
- `tools/orchestrator/heartbeat_watchdog.py` (`evaluate_new_routings` auto-ping)

Memory updates this session:
- Added `feedback_lambda_no_spot_api.md` (Lambda has no spot/preemptible/reservation API; on-demand + sales-mediated reserved only; don't re-explore).
