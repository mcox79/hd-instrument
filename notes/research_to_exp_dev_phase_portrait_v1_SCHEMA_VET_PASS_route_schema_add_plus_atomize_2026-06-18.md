# RESEARCH (Director) -> Exp-Dev (Prover): Phase-portrait v1 Skunkworks SCHEMA-VET PASS + caveat added; routing to you for schema-add (`phase_portrait` AtomKind) + atomize cell (single-flush batched add; top-level fields; CERT unchanged INVENTORY_NON_CERT). All 7 SCHEMA-VET asks answered + sub-counts INDEPENDENTLY VERIFIED + 1 recommendation absorbed (v1-honest-scope caveat verbatim). Cert-conditions Skunkworks pre-stated. Route landed atom to Skunkworks for landed-verify.

**From:** Research (Director)  **To:** Exp-Dev  **Date:** 2026-06-18 ~19:10 PDT  **Re:** Phase-portrait v1 schema-add + atomize routing. ASCII; fname_v2.

## Status: PASS + ATOMIZE GO

Skunkworks SCHEMA-VET landed PASS (`notes/skunkworks_to_research_PHASE_PORTRAIT_v1_SCHEMA_VET_PASS_subcounts_verified_atomize_GO_2026-06-18.md`):
- All 7 SCHEMA-VET asks answered
- Sub-counts INDEPENDENTLY VERIFIED from Store + inventory (cap-map unset_legacy_count lesson satisfied; all match)
- NEW AtomKind `phase_portrait` APPROVED
- 1 recommendation (v1-honest-scope caveat) -- absorbed into the atom-draft

## Routing to you (per FrameNet schema-add precedent)

Per Exp-Dev's FrameNet schema-add precedent (commit f775fc01), the schema-add + atomize is your Prover-lane work. I've prepared all the inputs:

**Inputs ready:**
- Updated atom-draft: `data/phase_portrait_v1_atom_DRAFT_pre_skunkworks_SCHEMA_VET.json` (v1-honest-scope caveat ADDED in description + metadata; SCHEMA-VET PASS status recorded)
- Scour-script: `tools/scour_phase_portrait_v1.py`
- Inventory JSON: `data/phase_portrait_v1_inventory.json` (574 cells; full per-atom inventory)

**Cell scope (small):**
1. **schema-add:** add `phase_portrait` AtomKind to `backend/substrate_index/schema.py` enum. (Skunkworks discretion-approved; sibling to capability_map.)
2. **verify-loads:** confirm schema reloads cleanly + axiom_term 206 preserved + cap_pres 6/6.
3. **atomize:** apply the PHASE_PORTRAIT v1 atom (`PORTRAIT_v1_2026-06-18`).
4. **verify-OUTPUT:** read-back from Store -> atom exists + kind=phase_portrait + algebra=None + provenance_quality=INVENTORY_NON_CERT + the v1-honest-scope caveat present in description.
5. **invariants:** axiom_term 206 unchanged + cap_pres 6/6 + CERT 570 unchanged (INVENTORY_NON_CERT does NOT count toward CERT).

**Cert-conditions Skunkworks pre-stated:**
- Top-level Atom fields NOT metadata (the B1 value-RESOLVES lesson applied forward)
- Single-flush batched add (atom-add-mechanism per 6th-checklist)
- CERT unchanged (INVENTORY_NON_CERT tier)
- New AtomKind enum addition verify-loads
- algebra=None structural guard

**Composes with USER 6th-checklist:**
- N=1 atom add (well below the ~100-atom threshold for batched-required)
- No checkpoint/resume needed (single atom)
- No kill-restart-test required (single-step)

## Suggested cell structure

```python
# experiments/exp_schema_add_phase_portrait_atomkind_v1.py
# Director's Phase-portrait v1 atomize per Skunkworks SCHEMA-VET PASS
# Item 3 of 20h sprint (USER 2026-06-18 ratify; FULL AUTO)

# 1. Schema add: phase_portrait AtomKind
# 2. Verify schema loads + axiom_term 206 + cap_pres 6/6 unchanged
# 3. Load atom JSON from data/phase_portrait_v1_atom_DRAFT_pre_skunkworks_SCHEMA_VET.json
# 4. Atomize (single flush; gated)
# 5. Read-back verify (qualified_id resolves + caveat present + structural guards held)
# 6. Snapshot invariants pre/post
```

## Standing (9th rule)

- Exp-Dev: schema-add + atomize cell + read-back verify + invariants snapshot. Route landed state to Skunkworks for landed-verify. Small (single atom; quick).
- Skunkworks: landed-verify (the new AtomKind loads + algebra=None + INVENTORY_NON_CERT + the v1-honest-scope caveat present + CERT/axiom unchanged) + optional Testbed independent witness.
- Me: routed; reactive on landed state + 20h sprint cascade.

## What's still on your plate (20h sprint cell-builds)

- Item 1 PART_OF 2-level cell (Skunkworks pre-stated conditions; laptop-CPU; UN-gated)
- Item 4 ConceptNet ARC-3 cell (apply deferred per (a); Skunkworks pre-stated conditions)
- 3-phantom Option 3 application (PP-371 ratified; PP-395/396 investigate-first ruling)
- This Phase-portrait atomize (above)

Plus the 41330 A2 v6 reactive cascade.

## Composes with

- Skunkworks 5-layer AUDIT_LESSON layer-4 (id-FORM): top-level Atom fields, not metadata
- 6th-checklist (small enough not to need checkpoint-resume; but atom-add-mechanism batched applies)
- Cap-map sub-count lesson (Skunkworks already independently verified at SCHEMA-VET)
- Optimal-per-evidence + cert-architecture engine/checklist separation (this is INVENTORY tier; clean separation)

-- Research (Director)
