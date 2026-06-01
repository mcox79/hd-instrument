# Strategy response: PP-3 drill sequencing CONFIRMED (5 answers)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/strategy_request_to_strategy_pp3_drill_sequencing_verification_2026-06-01.md`

## TL;DR

All 5 of testbed's sequencing questions confirmed as proposed. Testbed proceeds with Phase 1 scoping pass. One clarification needed: Anthropic Phase 2 IS already authorized (commit `2fae636` 2026-05-31); the testbed handoff that's in flight already noted it as "pre-authorized but not yet spent." So PP-3 Phase 1 has the floor right now, but Anthropic Phase 2 can also dispatch in parallel without new auth.

## Answers to questions 1-5

### Q1: Early-exit gate at Phase 1 acceptable?

**YES — confirm.** The "rotation is OPTIONAL not REQUIRED at production scope" verdict IS an acceptable Phase 1 deliverable when the data supports it. The point of the drill is to inform PP-3's row state with empirical data; if the data says rotation is compliance-optimization not capacity-optimization, that's the correct verdict and warrants the cap_map LIFT shape you proposed.

Default behavior you outlined ("surface the early-exit and wait for orchestrator on whether to design anyway for compliance-optimization") is exactly right. If Phase 1 surfaces early-exit, file the deliverable + a routing back to orchestrator with the empirical numbers and a recommendation; orchestrator decides whether to dispatch Phase 2 design anyway for the compliance-optimization narrative.

### Q2: Compliance window mapping?

**YES — confirm testbed's read.**
- GDPR right-to-erase = 30-day max retention (Article 17; effective response window is "without undue delay" which case law interprets as ~30 days)
- HIPAA = 6-year audit-record retention (45 CFR § 164.530(j); covered-entity policies + documentation)
- SOC 2 CC7 = 7-year audit-trail retention (industry standard; AICPA TSC v2017 + later)

Add to PP-3 row caveats: "EU AI Act Article 50 (transparency obligations) may add a 7th year window for AI-system audit-trails depending on high-risk classification; if your work surfaces this as a 4th window it can be added to the deliverable."

### Q3: Verifier-replay scope?

**YES — scope to verifier-replay only initially.** The "rotated state still validates against original substrate baseline" test IS the load-bearing correctness gate; if that fails, rotation is broken regardless of any other capability.

GDPR-specific audit-trail reconstruction (the "show me everything you knew about subject X and when you knew it" test) is a separate capability — file as a follow-on testbed engineering routing after Phase 3 verifier-replay confirms.

### Q4: Cap_map LIFT shape if Phase 1 early-exit?

**YES — confirm.** PP-3 row LIFT 0.55-0.70 → 0.65-0.80 if Phase 1 shows production-scope growth is tractable.

Annotate the caveat list with the specific numbers (cert-chain bytes/hour at V2 baseline; projected MB/month at 1M-ops/day; projected GB/month at 100M-ops/month). The empirical fit anchors the LIFT; without numbers in caveats, the LIFT is over-claim.

If full design path produces compression-ratio + queryability evidence in Phase 2/3, file a separate follow-on routing for an additional LIFT (e.g., 0.65-0.80 → 0.75-0.90 if compression is >5x with verifier-replay passing).

### Q5: Sequencing relative to other in-flight items?

**Clarification: Anthropic Phase 2 IS authorized** per `notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md` (commit `2fae636` 2026-05-31). Phase 2 = production query evaluation (~$20-50). The PP-3 handoff noted it as "pre-authorized but not yet spent" — that's the same authorization, just hasn't been spent yet. So you don't need new orchestrator/user approval for Phase 2; you can sequence as bandwidth permits.

Given that:
- PP-3 Phase 1 (this drill) has the floor for the next ~3-4 hours
- Anthropic Phase 2 can run in parallel ($20-50; pre-authorized; spec in `notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md`)
- Anthropic Phase 3 (~$10-20) gates on Phase 2 PASS
- Phase 1 cloud H100 Week 0 revalidation (just-authorized today; `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md`) is the OTHER simultaneous testbed work; ~$5-15 spend; gates the Week 1 GO/NO-GO decision

You can run all three in parallel — PP-3 Phase 1 is local CPU/analysis (no compute contention), Anthropic Phase 2 is API (no GPU), Week 0 H100 revalidation is cloud (no local resource contention).

## Strategic context for the work

Cap_map state when this routing lands (v305 currently; strategy_scribe updating to v306 in parallel this turn):
- **PP-3 row**: 🔬 0.55-0.70 — your drill is the empirical anchor for the next LIFT
- **PP-2 row LIFTED v303** to 0.75-0.85 — compression × audit-rotation composition is the natural next-step after PP-3 lands
- **New compositional sub-row "c_quant/bits8 × Path D" at 0.70-0.85** (v303+v304) — audit-rotation under compression is in-scope for completing the production deployment stack
- **NEW PP-12 row "Compositionality audit API" at 0.60-0.75** landing this turn from research P4 delivery — depends on atom registry; testbed engineering routing pending

The audit-trail rotation and the compositionality audit API are complementary; PP-3 closes the storage / rotation question; PP-12 closes the queryability / certification question. Both are testbed-owned engineering tracks (after design phase).

## Files referenced

- `notes/strategy_request_to_strategy_pp3_drill_sequencing_verification_2026-06-01.md` (source routing; CLOSE after testbed reads this response)
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md` (the original handoff)
- `notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md` (Anthropic auth)
- `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md` (today's cloud H100 auth)

## Closing this response

Testbed proceeds with Phase 1 as proposed. Move both this response file AND the source verification request to `routed_completed/` after testbed reads.
