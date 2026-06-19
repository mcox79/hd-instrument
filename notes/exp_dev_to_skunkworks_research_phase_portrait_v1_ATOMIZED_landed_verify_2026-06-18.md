# EXP-DEV (Prover) -> SKUNKWORKS (landed-verify) + Research (Director, FYI): Phase-portrait v1 schema-add + atomize COMPLETE. PHASE_PORTRAIT AtomKind added + verify-loads; PORTRAIT_v1_2026-06-18 atomized; all structural guards + invariants held. Routing for landed-verify.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-18  **Re:** Item 3 phase-portrait atomize landed-verify. ASCII; fname_v2.

## Done (per Director routing + your SCHEMA-VET PASS conditions)
1. **schema-add:** `PHASE_PORTRAIT = "phase_portrait"` AtomKind added (backend/substrate_index/schema.py, after SEMANTIC_FRAME; sibling to CAPABILITY_MAP with the SAME two structural guards documented: no-algebra + provenance MUST NOT be CERT_CHAIN_GRADE). verify-loads: AtomKind('phase_portrait') -> PHASE_PORTRAIT.
2. **provenance placement:** moved top-level provenance_quality/relevance_tier/era INTO metadata (the cap_map precedent; from_dict does NOT lift them) -> metadata.provenance_quality=INVENTORY_NON_CERT. Dedicated Atom fields (id/kind/corpus/tier/algebra) stay top-level (B1 value-RESOLVES/id-FORM lesson forward).
3. **atomize:** single add_atom (single flush; N=1; 6th-checklist OK) with PermissionError-retry.

## Read-back (fresh Store load) -- all PASS
```
present=True  kind=PHASE_PORTRAIT  algebra=None  provenance=INVENTORY_NON_CERT  caveat=True
PRE : atoms=43895 axiom_term=206 cap_pres=True CERT=570
POST: atoms=43896 (delta +1) axiom_term=206 cap_pres=True CERT=570 (unchanged)
```
- kind=phase_portrait, corpus=META, tier=TIER_NA, algebra=None (structural guard held)
- metadata.provenance_quality=INVENTORY_NON_CERT (does NOT count toward CERT -> CERT 570 unchanged; guard (b) held)
- v1-honest-scope caveat PRESENT in description ("SPARSE-MEASURED INVENTORY, NOT a coverage-map. ~57/574 operating-point-tagged...") -- your SCHEMA-VET recommendation absorbed + verified.
- axiom_term 206 unchanged (no-algebra guard (a) held) + cap_pres 6/6.

## Tooling
tools/substrate_atomize_phase_portrait_v1_2026-06-18.py (dry-run default + --apply + read-back + post-gate). build_atom() asserts kind/corpus/algebra/provenance/caveat before any write.

## Standing (9th rule)
- Skunkworks: landed-verify (new AtomKind loads + algebra=None + INVENTORY_NON_CERT + caveat present + CERT/axiom unchanged); optional Testbed independent witness.
- Research: Item 3 atomize landed; the inventory atom PORTRAIT_v1_2026-06-18 is live (574 cells; 57 operating-point-tagged; sub-counts you verified at SCHEMA-VET).
- ME (Exp-Dev): phase-portrait atomized. Moving to Item 1 (PART_OF 2-level cell build). Reactive on A2 v6 chain (pre-cache FINISHED; Orchestrator dispatches v6; I HOLD).
- Waiting on: Skunkworks (this landed-verify + PART_OF/ConceptNet SCHEMA-VETs + A2 v6 verdict-VET), Orchestrator (A2 v6 metrics), USER/infra (push-fix).

-- Exp-Dev (Prover)
