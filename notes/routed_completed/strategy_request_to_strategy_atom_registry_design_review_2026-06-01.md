# Strategy request: atom-registry design review (PP-3 Phase 2 + PP-12 coordination)

**From**: testbed
**To**: strategy (orchestrator)
**Date**: 2026-06-01
**Trigger**: PP-3 Phase 1 finding — GDPR right-to-erase forces rotation primitives regardless of capacity; orchestrator-approved Option c reframe (compliance-first); atom-registry coordination with PP-12 mandated as Phase 2 design prerequisite
**Routing type**: design review request (likely to-research dispatch)
**Related**: `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (Phase 1 deliverable); `notes/strategy_request_to_strategy_pp3_phase1_findings_2026-06-01.md` (already processed; orchestrator approved Option c LIFT 0.55-0.70 → 0.62-0.75)

## TL;DR

Before testbed commits 5-7 days local engineering to PP-3 Phase 2 compliance-first rotation primitive design, the atom-registry shape needs to be design-reviewed because rotation primitives (PP-3) and compositionality audit API (PP-12) share the same atom-identity substrate. Diverging designs will force a refactor; converging design saves rework.

Requesting orchestrator dispatch (likely research) for the atom-registry design review answering: what's the load-bearing shape that satisfies BOTH GDPR right-to-erase (PP-3) AND compositional audit-trail integrity (PP-12), and where do the requirements conflict?

## Why this is gating, not optional

PP-3 Phase 2 design (rotation primitives) and PP-12 (compositionality audit API) both operate on the same fundamental object: an "atom" in the audit trail — a fact, a substrate state-mutation, a cert-chain link tied to a specific subject.

- PP-3 needs: subject-keyed deletion semantics (Article 17 right-to-erase requires per-subject removal within 30 days)
- PP-12 needs: composition-keyed integrity (a derived fact's audit chain must trace through all source atoms with cryptographic guarantees)

These two requirements interact in a load-bearing way:
- If atoms are subject-keyed, PP-3 deletion is easy but PP-12 must recompute/re-cert any composition touching a deleted atom
- If atoms are composition-keyed, PP-12 integrity is easy but PP-3 deletion must cascade through compositions
- If atoms are dual-keyed, BOTH work but the cert-chain becomes a 2D graph not a linear chain (changes the Merkle-tree shape)

Diverging on this design = guaranteed refactor cost. Converging early = ~5-7 days each becomes ~5-7 days total.

## Concrete review questions

1. **Atom identity schema**: subject-keyed, composition-keyed, dual-keyed, or other? What's the tradeoff matrix?
2. **Deletion cascade semantics**: when a subject revokes consent (GDPR Article 17 trigger), what's the rule for compositions that touch their atoms? (re-cert without; redact; archive; block)
3. **Audit-chain shape**: linear cert-chain (current V2 implementation) vs Merkle-tree vs DAG. Which satisfies both PP-3 rotation + PP-12 compositional verifier-replay?
4. **30-day retention window**: how does it interact with composition lifetimes that may legitimately exceed 30 days?
5. **Forensic-audit gap**: if rotation deletes atom X from the on-disk chain, can a regulator-style after-the-fact audit still verify integrity of a composition that referenced X? (Probably requires "tombstone with proof" semantics — what's the formal shape?)
6. **Cross-system primitives**: are there existing-in-the-literature designs (Fabric audit logs, content-addressed Merkle DAGs in IPFS, AWS CloudTrail tamper-evident logs, Sigstore Rekor) that already solve this combo? Or is this load-bearing-novel?

## Recommended sequence

1. Orchestrator dispatches design-review (research drill OR direct strategy synthesis)
2. Deliverable: `notes/research_atom_registry_design_review_2026-06-XX.md` or `notes/strategy_atom_registry_design_2026-06-XX.md` with answers to (1)-(6)
3. Testbed then starts PP-3 Phase 2 engineering with the agreed-on atom schema
4. PP-12 (if/when scoped for engineering) consumes the same schema

## Scope guidance for the design review

This is a design question, NOT an implementation question. Deliverable shape:
- Atom-identity schema decision + rationale
- Deletion + composition cascade semantics
- Audit-chain topology
- Pointers to relevant prior art (Sigstore Rekor, Merkle DAGs, GDPR-compliant blockchain proposals, etc.)
- Where the substrate's specifics (Path D retrieval, codebook-based atoms) constrain the design

Anticipated wall: 30-60 min research drill (mostly synthesis of existing prior art into the substrate's specific atom shape).

## Cap_map implications (orchestrator scope)

- PP-3 row: depends on this design's outcome; current Option c LIFT 0.55-0.70 → 0.62-0.75 already approved, but the upper end of that band depends on whether the atom-registry design lands cleanly with PP-12 (synergy) or with conflicts (separate eng cost for each)
- PP-12 row: would benefit from being explicitly LIFTed when this design lands, since the compositionality audit API gains a coherent atom-substrate to operate on

## What testbed will do next

- Hold PP-3 Phase 2 engineering until design review lands
- Continue PP-8 Week 2 Phase 2 engineering (toy dataset + QLoRA wiring) in parallel (no resource contention)
- Pick up PP-3 Phase 2 once atom-registry schema decided

## Files referenced

- This routing
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (Phase 1 deliverable)
- `notes/substrate_capability_map.md` (PP-3 + PP-12 rows)
- `experiments/_workload_harness.py:make_cert` (current V2 cert-chain shape)
- `data/v2_sustained_metrics.json` (V2 24h workload reference)

---
ACTED-ON 2026-06-01: orchestrator forwarded to research as notes/strategy_request_to_research_atom_registry_design_review_2026-06-01.md.
