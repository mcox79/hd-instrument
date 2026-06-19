# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 120 FOUR PARALLEL ratifies ALL HARD_PASS; Track 1 (6 signature metadata fixes) + Ratify 2 (kl-backwards 3 REMOVE + 1 upward ADD) + Ratify 3 (count_nb SIMPLE PATH SPECIALIZES->RELATES) + Ratify 4 (vector_space SPECIALIZES->group_type REMOVE); R3 PRESERVED; 5 STRUCTURE-error class cases resolved via two-layer pattern (signature + materialized)

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 120 + Skunkworks ALL-UNBLOCKED specs (Track 1 + Track A/B/C).

## Ratification result -- 4 parallel ratifies

### Ratify 1 -- Track 1 signature metadata fixes (self-model JSONL only)

| Atom | Before | After |
|---|---|---|
| T1/vector_space | specializes:field | defined_over:field + composed_of:[abelian_group, scalar_action] |
| T1/matrix | specializes:vector_space | represents:linear_map + defined_over:field |
| T1/group | specializes:set | composed_of:[set, binary_operation, group_axioms] |
| T1/eigenvalue_eigenvector | specializes:linear_operator | defined_over:linear_operator |
| T1/graph_general | specializes:set | composed_of:[vertex_set, edge_set] |
| T1/orthogonality | specializes:inner_product | defined_via:inner_product |
| T1/group_axioms | (DEFENSIBLE AS-IS per 120b) | LEFT UNCHANGED |
| T1/measure_space | (cross-check) | composed_of:[set, sigma_algebra, measure] verified (101a fix landed) |

6 fixes applied; self-model JSONL at 110 lines unchanged.

### Ratify 2 -- kl-canonical backwards-edge review (DECISION 113b)

```
REMOVED 3 backwards consumer DEPENDS_ON edges:
  math::T1/kullback_leibler_divergence -DEPENDS_ON-> math::T3/bocpd_changepoint
  math::T1/kullback_leibler_divergence -DEPENDS_ON-> math::T3/em_algorithm
  math::T1/kullback_leibler_divergence -DEPENDS_ON-> math::T3/mp_bulk_kl

ADDED 1 upward edge (verify_upward_edges):
  math::T3/em_algorithm -USES-> math::T1/kullback_leibler_divergence (was missing)
  (mp_bulk_kl and bocpd_changepoint already had USES/RELATES upward)

T1->T3 tier-monotone inversion fix
Leaf-strand SAFE (kl retains DEPENDS_ON integral + metric_space)
```

### Ratify 3 -- Track 2 count_nb SIMPLE PATH (DECISION 120-RULE)

```
REMOVED: math::T3/count_nb -SPECIALIZES-> math::T2_FAM/discriminative_classification (wrong; NB is GENERATIVE)
ADDED:   math::T3/count_nb -RELATES-> math::T2_FAM/discriminative_classification (contrast; siblings)

Defer (per Director ruling + Phase 4e hold):
  - generative_classification T2_FAM family atom authoring
  - signature fix (count_nb signature pointer in self-model)
```

### Ratify 4 -- Track 3 vector_space -> group_type RE-TYPE

```
REMOVED: math::T1/vector_space -SPECIALIZES-> math::T1/group_type

Notes:
  - composed_of NOT in RelationType enum
  - Track 1 signature fix (above) already encodes composed_of structure at metadata layer
  - REMOVE-only preserves substrate correctness without inventing relation type
  - vector_space retains DEPENDS_ON to other components (field_axioms, group_axioms per pre-state)
  - Per 18th rule + DECISION 92a/93/94 precedent: refuse to invent relation type;
    let signature-level structure carry the semantic
```

## State + R3 verification

| Counter | Pre | Post | Delta |
|---|---|---|---|
| Atoms | 26271 | 26271 | 0 (no atom changes) |
| Relations | 5222 | 5220 | -2 (5 removes + 2 explicit adds + 1 auto-reverse = -2) |
| Self-model lines | 110 | 110 | 6 in-place metadata corrections |
| Axiom termination | 205/205 | 205/205 | PRESERVED |
| Capability_preservation | 1.0 | 1.0 | PRESERVED |
| Tier 1+2 modules | 6/6 OK | 6/6 OK | preserved |
| Rollback | not needed | not needed | -- |

## Substrate-product positioning -- STRUCTURE-error class systematically resolved at two layers

The 18% UNDECIDABLE pattern I surfaced in 110a audit is now resolved across signature + materialized layers:

| Atom | Signature fix (Track 1) | Materialized fix (Tracks A/B/C) |
|---|---|---|
| vector_space | composed_of + defined_over | REMOVE wrong SPECIALIZES group_type |
| matrix | represents + defined_over | (was phantom; no materialized) |
| group | composed_of | (was phantom; no materialized) |
| eigenvalue_eigenvector | defined_over | (was phantom; no materialized) |
| graph_general | composed_of | (was phantom; no materialized) |
| orthogonality | defined_via | (was phantom; no materialized) |
| count_nb | (deferred; Phase 4e resume) | REMOVE wrong SPECIALIZES + ADD RELATES |
| measure_space | (already 101a-corrected) | (was phantom) |

7 of 7 STRUCTURE-error signature-layer cases addressed (including measure_space cross-check). 2 materialized-layer cases resolved (vector_space SPECIALIZES wrong remove; count_nb SPECIALIZES wrong remove + RELATES add). Pattern generalized from 101a (single case) to systematic Phase 3 cleanup.

## kl-canonical now textbook-clean

Post-Ratify 2: kullback_leibler_divergence is no longer backwards-dependent on its consumers. The T1->T3 tier-monotone inversion is corrected. Foundational KL retains DEPENDS_ON to integral + metric_space (axiom path) while losing the backwards DEPENDS_ON to bocpd/em_algorithm/mp_bulk_kl. The upward em_algorithm USES kl edge that was missing is now present.

## Substrate state (post DECISION 120)

```
Atoms:     26271
Relations: 5220 (was 5222; -2)
Self-model signatures: 110 (6 STRUCTURE-error class signature corrections in-place)
Axiom termination: 205/205 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 19 attempts
  Phase 3 complete: 7 sub-batches + 4 parallel Ratifies
  All HARD_PASS except 87c + 84a (both recovered via retry)
  0 unrecovered
```

## Cross-references

- DECISION 120 dispatch: `notes/research_to_testbed_skunkworks_exp_dev_DECISION_120_*`
- Skunkworks ALL-UNBLOCKED-SPECS delivery: `notes/skunkworks_to_research_testbed_exp_dev_SUBBATCH_2_VET_PASS_*`
- Track 1 spec: `data/substrate_index/skunkworks_phase3_track1_structure_signature_metadata_fixes_spec_2026-06-15.jsonl`
- Track A/B/C spec: `data/substrate_index/skunkworks_phase3_kl_backwards_plus_track2_count_nb_plus_track3_vector_space_specs_2026-06-15.jsonl`
- DECISION 101a measure_space precedent: prior commit
- DECISION 113a Sub-batch 2 (kl_divergence MERGE): commit `0564ef0a`
- DECISION 116a Sub-batch 3 (collins MERGE): commit `eb404dfb`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused to invent relation type (composed_of not in enum; signature-layer carries semantic instead)
- 19th rule: STRUCTURE-error class pattern generalized from single 101a measure_space case to 7 cases
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 120 FOUR PARALLEL ratifies ALL HARD_PASS + Track 1 signature metadata (6 STRUCTURE-class fixes + 1 measure_space cross-check) + Ratify 2 kl-backwards (3 REMOVE + 1 upward em_algorithm USES kl ADD; T1->T3 tier-monotone inversion fixed) + Ratify 3 count_nb SIMPLE PATH (SPECIALIZES wrong REMOVE + RELATES contrast ADD; generative_classification family + signature fix deferred per Phase 4e hold) + Ratify 4 vector_space SPECIALIZES group_type REMOVE (composed_of carried by signature layer; refuse to invent relation type per 18th rule) + R3 PASS (205/205 axiom + 6/6 modules + cap_pres=1.0) + STRUCTURE-error class systematically resolved at two layers + 110a audit's 18% UNDECIDABLE pattern empirically addressed.

Tag: DECISION_120_FOUR_PARALLEL_RATIFIES_HARD_PASS
