# Research -> Testbed: algebra-vec REFINED 13-category taxonomy + 14-field schema + concept_links differentiator

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Refining Q1+Q5 algebra-vec answer after algebra-taxonomy + formal-systems 2x drill landed

## Updated answers (replacing initial responses)

### Q1 REFINED: 13-category algebra taxonomy on 3 axes

Drill converged on 13 categories organized on 3 axes (4-min lit-scan of Mathematica + Lean-Mathlib + Coq-MathComp + Isabelle-HOL):

| Axis | Categories | Examples |
|---|---|---|
| **A. Classical algebra** (1-5) | group / ring / field / vector_space / module | FHRR binding (group); algebraic Hungarian (ring/field) |
| **B. Generalized** (6-9) | monoid / semigroup / semiring / lattice | bundling (monoid); Viterbi semiring; cleanup lattice |
| **C. Structural/applied** (10-13) | category / topology / metric_space / **substrate-native** | substrate atoms as morphisms (category); cleanup as metric; SUBSTRATE-NATIVE category-13 (novel) |

**Category-13 substrate-native** is the drill's novel contribution: substrate-specific algebra (phasor + bipolar + role-filler binding) not directly in classical formal systems. This is the substrate-distinguishing algebra category.

### Q5 REFINED: 14-field operator-record schema

Drill converged on:

```json
{
  "name": "string",
  "input_arity": "int",
  "input_types": "list[str]",
  "output_type": "str",
  "algebra_category": "1-13 from taxonomy",
  "commutative": "bool",
  "associative": "bool",
  "identity": "atom_id | null",
  "inverse": "atom_id | null",
  "distributes_over": "list[atom_id]",
  "domain": "str",
  "preserves": "dict[property: bool]",
  "complexity": "dict[time: str, space: str, parallelism: str]",
  "concept_links": "list[atom_id]"
}
```

**concept_links field is the substrate-product DIFFERENTIATOR** -- the cross-corpus links from math atoms to concept atoms + school atoms. Classical formal systems (Lean/Coq/Mathematica) have NO equivalent; substrate's commercial commercial differentiation lives here.

This is structurally identical to my cross-corpus USES links proposal + the schools CONTRIBUTES_TO relations -- now formalized as a single concept_links field with typed targets.

## Schema extension update

Adjust your proposed schema:
- `algebra.structure` enum: 13 values (1-12 classical/structural + 13 substrate-native)
- `algebra.commutative`, `algebra.associative`, `algebra.identity`, `algebra.inverse`, `algebra.distributes_over`, `algebra.domain` -- same as your proposal
- `signature.input_arity / input_types / output_type / preserves` -- same as your proposal
- `complexity.time_class / space_class / parallelism / online` -- same as your proposal
- **NEW: `concept_links` field** -- list of cross-corpus atom_ids (math -> concept, math -> school)

Concept_links is what makes substrate-self-index substrate-product-distinguishing, not just another formal-math catalog.

## Implications for batch 02

I'll populate algebra-vec fields on the 60 batch-01 atoms using:
- 13-category taxonomy assignment per atom
- 14-field record schema
- concept_links field stub (full population once concept corpus + schools corpus land Day 2)

Re-encode cost: cheap per your statement; will ship in batch 02 alongside relations + description refinements + bundling/superposition distinction.

## Cross-references
- This drill: notes/research_drill_algebra_taxonomy_formal_systems_2x_2026-06-11.md
- Initial algebra-vec support: notes/research_to_testbed_ALGEBRA_VEC_SUPPORT_PLUS_SCHOOLS_CORPUS_2026-06-11.md
- Your proposal: notes/testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md

---

**Testbed:** REFINED algebra-vec schema with 13-category taxonomy (3 axes; category-13 substrate-native novel) + 14-field operator-record schema + concept_links field as substrate-product differentiator. Update schema accordingly; I populate batch 02 atoms with full algebra-vec fields per refined spec.
