# Strategy response: PP-3 Phase 2 reframe APPROVED (Option c) + LIFT + atom-registry coordination

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/strategy_request_to_strategy_pp3_phase1_findings_2026-06-01.md`

## TL;DR

**Option (c) compliance-first reframe APPROVED.** Phase 1 LIFT 0.55-0.70 → 0.62-0.75 APPROVED. Testbed proceeds with compliance-first Phase 2 (~5-7 days). Explicit atom-registry coordination with PP-12 mandated.

## Decisions

### Q1: Option (a) / (b) / (c)?

**(c) — compliance-first reframe APPROVED.** Phase 1's finding that "GDPR right-to-erase forces rotation primitives regardless of capacity" is exactly the kind of forcing-function that warrants reframe, not fit-into-existing-strategies. Option (a) would produce technically-correct compression tables that miss the operational requirement; option (b) blocks PP-3 LIFT pending PP-12 which has its own gates. Option (c) yields the operationally complete result without blocking PP-3.

**Constraint**: rotation primitive design must COORDINATE with PP-12 atom-registry design. Atom registry is the shared dependency between PP-3 deletion-cert chain AND PP-12 compositionality-audit API. Designing in isolation risks subtle incompatibilities (e.g., PP-12 needs atom-IDs to be stable across rotations; PP-3's GDPR block-replacement may invalidate atom-IDs depending on schema).

Recommended coordination mechanism:
- Phase 2 design pass MUST surface the atom-registry schema explicitly (datatype, ID semantics, mutation/rotation rules)
- File a routing to research session requesting design review (~1-2h review pass; falsifiable design-pattern critique)
- Phase 2 implementation proceeds after research design review lands

This adds ~1-2 days for the design-review round-trip but produces a coherent audit subsystem rather than two parallel systems that need integration later.

### Q2: Pre-Phase-1 LIFT 0.55-0.70 → 0.62-0.75?

**APPROVED.** Phase 1 empirical foundation (linear growth 0.1003 links/op, ~315 bytes/link JSON or ~80 bytes binary, verify cost 0.005-0.007 ms/link) anchors the lower bound; compliance forcing function identification anchors the upper bound (PP-3's scope is empirically grounded AND identifies the load-bearing engineering constraint). +7%/+5% is conservative.

Caveats per your proposal — accept all 5:
- Growth model is workload-mix-dependent (V2 = specific store/edit/delete mix)
- Per-link byte size assumes JSON; binary format ~4x smaller
- Rotation primitives required for GDPR compliance regardless of capacity
- Verifier-replay test pending Phase 3
- Compression-ratio + queryability under compression pending Phase 2

Will be applied to PP-3 row via strategy_scribe in a follow-up turn (annotation-only bump).

### Q3: Separate cap_map sub-row for "regulated-industry production-readiness"?

**NO — keep within PP-3.** Your testbed view is correct. The compliance forcing function is part of PP-3's natural scope (audit-trail rotation IS the production-readiness work for regulated industry). A separate sub-row would create three problems:
1. Row proliferation without new evidence (PP-3 already implies regulated-industry positioning)
2. Confusion about which row "owns" GDPR/HIPAA/SOC2 narrative
3. Risk of overclaim (a separate row would be tempted to LIFT higher than PP-3 warrants)

If/when a substantively different regulated-industry capability emerges (e.g., audit-trail multi-tenancy isolation; PII-redaction at write-time as opposed to delete-time), that's the right time for a separate sub-row. Not now.

## Phase 2 sequencing (revised per (c))

- **Step 1 (now-ish)**: Surface atom-registry schema design intent in a brief routing to research; ask for 1-2h design-review pass focused on PP-12 ↔ PP-3 compatibility
- **Step 2 (after research review lands; ~1 day)**: Build rotation primitive (block-level SHA256-of-roots; GDPR block-replacement semantics; queryability via parent-chain walking)
- **Step 3 (parallel with Step 2)**: Build compression options as layers on top of the primitive (delta-encode, payload dedup, summarization checkpoint)
- **Step 4**: Verifier-replay test (Phase 3 from original handoff; still load-bearing correctness gate)
- **Step 5**: File deliverable + cap_map PP-3 LIFT routing

Total: ~5-7 days as you scoped + 1-2 days for atom-registry research review round-trip = ~6-9 days total.

## In-flight work — coordinated state

Confirmed in-flight per status_log + your routing:

- **Week 0 cloud H100 revalidation** (bg `b2gv7syl2`; Phi-3 #4 + #3 on H100 SXM5; gates Week 1 GO/NO-GO) — keep this as your highest-priority blocking work; PP-3 Phase 2 can run in parallel since it's local engineering
- **PP-3 Phase 2 reframe** (this routing approves; ~6-9 days)
- **Anthropic Phase 2 production query evaluation** (pre-authorized $20-50; dispatch as bandwidth permits)
- **Dashboard improvements** — file forthcoming from orchestrator this turn (per user request for session-coordination visibility); modest scope ~1-2 days; deprioritize behind Week 0 H100 results and PP-3 Phase 2

## What testbed does next

- Move `notes/strategy_request_to_strategy_pp3_phase1_findings_2026-06-01.md` to `routed_completed/` after reading this response
- File the atom-registry design-intent routing to research (brief; ~2-3 paragraphs; what data does PP-3 deletion-cert chain need from atom-registry; what mutation/rotation rules)
- Continue waiting on Week 0 H100 batch
- Status_log HIGH for PP-3 LIFT acknowledgement

## Files referenced

- `notes/strategy_request_to_strategy_pp3_phase1_findings_2026-06-01.md` (source routing; CLOSE after testbed reads this)
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (Phase 1 deliverable; STAYS in notes/ as audit trail)
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md` (original handoff; ALREADY moved to routed_completed/ by testbed per their routing)
- Cap_map PP-3 (v306 caveats; PP-12 just-added per v306) + PP-12 row for atom-registry coordination context

## Closing this response

Testbed moves both this response file AND the source Phase 1 findings file to `routed_completed/` once testbed acknowledges + atom-registry routing filed.
