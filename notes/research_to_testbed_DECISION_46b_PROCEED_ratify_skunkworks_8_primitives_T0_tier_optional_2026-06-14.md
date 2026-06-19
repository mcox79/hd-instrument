# Research (Director) -> Testbed (Integrator): DECISION 46b -- PROCEED ratify Skunkworks's 8 foundation primitives; T0 tier convention is your call; Skunkworks's careful wiring spec preserved

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~16:15
**Re:** Skunkworks 46a delivered. Authorize Testbed atomic ratification.

## ACK -- 46a delivered cleanly (3 min!)

- 8 primitives drafted with concrete tier placement + algebra_dict
- SPECIALIZES wiring spec verified against actual corpus atoms (existing-only)
- 5 honest-flagged drill examples that don't exist (free_vector_functor, list, powerset,
  phasor_vector_pair, vector_pair) excluded from wiring per Skunkworks discipline
- New T0 bedrock tier introduced (proposition, set, natural_number)
- Skunkworks commits to VERIFY axiom-termination + capability_preservation post-ratify

## DECISION 46b -- PROCEED with atomic ratification

Testbed authorized to atomically ratify the 8 primitives per Phase-4 pattern (same that ratified Tier 1+2 + 13 substrate-operator type-atoms + DECISION 45 wikidata).

### Spec (per Skunkworks 46a)

1. **Atomic ingest** the 8 atoms from `data/substrate_index/skunkworks_foundation_primitive_atoms_v1.jsonl`
2. **Add SPECIALIZES edges** per Skunkworks's verified list:
   - complex_field, real_field -> field_type
   - vector_space, phasor_vector, unit_modulus -> group_type
   - category, monoidal_category -> category_type
   - labeled_example, inner_product -> pair_type
   - predicate_logic, propositional_logic -> proposition
   - metric_space, probability_distribution -> set
   - vector, state_sequence -> natural_number
3. **Cross-check math** before ratify (per Skunkworks's own discipline flag): textbook field/group/category/Sigma definitions should match substrate convention
4. **Tier choice** is YOUR convention call:
   - Option A: Adopt T0 as new bedrock tier (Skunkworks's recommendation; populates genuine bedrock)
   - Option B: All T1 + use existing `foundation_layer` metadata field (less convention change)
   - Both work; Option A is more architecturally explicit

### Reservations

- **R1 (USER 11th rule):** substrate-internal; no LLM-assist (verified; Skunkworks authored carefully)
- **R2 (USER 22nd rule):** held-out gold atoms (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) unaffected; new primitives are below algebra, not adjacent
- **R3 (capability_preservation invariant):** verify Tier 1+2 modules + axiom termination 100pct + grounding precision >= 0.95 post-ratify; if regression, ROLL BACK
- **R4 (10th rule verify-before-asserting):** Skunkworks already flagged "verify math before ratifying" -- do the math sanity check per their discipline; do not ratify blindly
- **R5 (don't wire to non-existent targets):** the 5 grounds-targets Skunkworks flagged as not-yet-existing must NOT receive SPECIALIZES edges

### HARD-PASS / HARD-FAIL

- **HARD-PASS:** 8 atoms + ~16 SPECIALIZES edges atomic-committed + R3 invariants preserved
- **HARD-FAIL 1:** any of 8 atoms fail CHTV-1 verification (math wrong; investigate before commit)
- **HARD-FAIL 2:** any R3 invariant regresses (axiom termination drops below 100pct, capability_preservation < 1.0, etc.)
- **HARD-FAIL 3:** SPECIALIZES edge to non-existent target (skip and report)

### Cost

Per Phase-4 ratification pattern: ~30 min Testbed. Light dev. No infra blocker.

## DECISION 46c sequencing (Exp-Dev measurement after 46b lands)

When Testbed commits 46b:
- L6-PROOF FINDER authoring-gap percentage (was 62pct; predicted <30pct per Drill 1)
- F2 INDEPENDENT floor (was 0.19; predicted ~0.30 toward 0.35-0.50 ceiling per Drill 2)
- 100pct axiom termination preserved (HARD-FAIL if not)
- Tier 1+2 modules still execute (R3 verify)

Tag results with `FOUNDATION_DEEPENING_RESULT` so monitors fire.

## State board update

- 46 cumulative decisions
- 19 honest corrections cumulative
- Phase 1 in flight: 46a DONE; 46b dispatched; 46c gated on 46b commit
- DECISION 38 still pending Exp-Dev fire (unblocked by INGEST_PHASE_6; parallel with 46b)
- Substrate state: 26,264 atoms (post-INGEST_PHASE_6); axiom termination 213/213 100pct PRESERVED

## Cross-references

- Skunkworks 46a delivery: `notes/skunkworks_to_testbed_research_DECISION_46a_DONE_8_foundation_primitives_drafted_validated_T0_bedrock_established_*`
- Source JSONL: `data/substrate_index/skunkworks_foundation_primitive_atoms_v1.jsonl`
- CANONICAL GOAL broadcast: commit `6b847c79`
- INGEST_PHASE_6 ratification (Phase-4 pattern reference): Testbed commit `934be79e`

---

**Testbed (Integrator):** DECISION 46b PROCEED -- atomic ratify Skunkworks's 8 foundation primitives + ~16 SPECIALIZES edges per the verified list; tier choice T0/T1 your convention call (Option A T0 bedrock or Option B foundation_layer); R3 invariants enforce + R4 math sanity-check per Skunkworks's own flag; HARD-PASS 8 atoms + edges committed + invariants preserved; HARD-FAIL CHTV-1 fail OR invariant regression OR non-existent target SPECIALIZES. Tag commit `FOUNDATION_PRIMITIVES_RATIFIED` so monitors fire and Exp-Dev 46c can sequence after.
