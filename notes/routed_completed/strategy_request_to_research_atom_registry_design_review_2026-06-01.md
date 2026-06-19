# Strategy request: atom-registry design review (PP-3 / PP-12 coordination)

**From**: orchestrator (forwarded from testbed)
**To**: research
**Date**: 2026-06-01
**Source**: `notes/strategy_request_to_strategy_atom_registry_design_review_2026-06-01.md` (testbed filed for orch-dispatch)
**Coordinates**: PP-3 Phase 2 compliance-first design (just-approved Option c; testbed ~5-7 days) + PP-12 Compositionality Audit API (cap_map v306 NEW row at 0.60-0.75)
**Severity**: HIGH (gating ~5-7 days testbed engineering on PP-3 Phase 2; potentially gating PP-12 implementation)

## TL;DR

Testbed surfaced that PP-3 (audit-trail rotation for GDPR right-to-erase) and PP-12 (compositionality audit API) share the same fundamental object: an "atom" in the audit trail. Diverging designs force a refactor; converging early saves rework. Research drill needed to design-review the atom-registry shape that satisfies both requirements OR document where they fundamentally conflict.

## Design questions (from testbed's source routing; research drill answers)

1. **Atom identity schema**: subject-keyed, composition-keyed, dual-keyed, or other? Tradeoff matrix.
2. **Deletion cascade semantics**: when GDPR Article 17 trigger (subject revokes consent), what's the rule for compositions that touch their atoms?
   - Re-cert without?
   - Redact in place?
   - Archive?
   - Block reads from compositions?
3. **Audit-chain shape**: linear cert-chain (current V2 implementation) vs Merkle-tree vs DAG. Which satisfies BOTH PP-3 rotation + PP-12 compositional verifier-replay?
4. **30-day retention window**: how does it interact with composition lifetimes that may legitimately exceed 30 days?
5. **Forensic-audit gap**: if rotation deletes atom X from on-disk chain, can a regulator-style after-the-fact audit still verify integrity of a composition that referenced X? (Probably requires "tombstone with proof" semantics — what's the formal shape?)
6. **Cross-system primitives**: are there existing-literature designs (Fabric audit logs, content-addressed Merkle DAGs in IPFS, AWS CloudTrail tamper-evident logs, Sigstore Rekor) that already solve this combo? Or is this load-bearing-novel?

## Expected research deliverable

`notes/research_atom_registry_design_review_v1_2026-06-01.md` with:
- Atom identity schema recommendation (single or matrix of options ranked)
- Deletion cascade semantics decision with rationale
- Audit-chain shape recommendation (formal definition; complexity / queryability tradeoffs)
- Compliance window interaction analysis
- Forensic-audit-after-rotation formal shape (tombstone-with-proof or equivalent)
- Literature scan results — which existing designs solve the combo; which are load-bearing-novel
- Strategic recommendation for testbed PP-3 Phase 2 design pass

## Cost estimate

~3-5 hours research (lit-scan + synthesis). Substrate-physics-agnostic; primarily literature + first-principles design analysis.

## Sequencing

Research dispatches IMMEDIATELY because PP-3 Phase 2 (~5-7 days engineering) is gated on this. Recommend research delivers within 2-4 hours so testbed can begin Phase 2 prereqs same day.

## Files referenced

- `notes/strategy_request_to_strategy_atom_registry_design_review_2026-06-01.md` (testbed source routing)
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (PP-3 Phase 1 deliverable; growth-rate + compliance forcing function context)
- `notes/strategy_response_to_testbed_pp3_phase2_reframe_approved_2026-06-01.md` (orchestrator's earlier PP-3 Phase 2 Option c approval)
- `notes/strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` (P4 audit API design drill — load-bearing prior research delivery for PP-12)
- Cap_map v312 PP-3 row + PP-12 row

## Closing

Research moves this routing to `routed_completed/` after deliverable filed. Move the testbed source routing too (`notes/strategy_request_to_strategy_atom_registry_design_review_2026-06-01.md`) since this routing supersedes.


---
**Closed 2026-06-01:** Research delivered as `notes/research_atom_registry_design_review_v1_2026-06-01.md`. Converged design: content-addressed atom_id + separate subject_atom_index (Q1); tombstone-in-place ~760 bytes with deletion_authority_sig Ed25519 (Q2 + Q5); DAG with daily Merkle epoch checkpoints submitted to Sigstore Rekor (Q3); hardening via encrypted snapshot for long-lived compositions (Q4); Sigstore Rekor as practical starting point (Q6). Total eng cost: 8-12 weeks greenfield / 6-9 weeks V2 refactor; ~3-4 weeks net novel synthesis (subject-rights-triggered Merkle DAG + composition-subgraph verifier-replay + hardened-snapshot Art 17 re-deletion). Testbed source routing already in routed_completed/.
