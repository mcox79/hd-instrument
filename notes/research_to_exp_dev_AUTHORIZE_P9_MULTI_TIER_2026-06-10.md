# Research -> Exp-Dev: AUTHORIZE P9-REVISED multi-tier cell (decisive cross-domain test)

**From:** Research  **Date:** 2026-06-10
**Re:** Authorization for P9-REVISED multi-tier sharded cross-domain test

## Authorization: YES, draft the multi-tier cell

P2 STRUCT-ALIGN INSUFFICIENT result (Hits@1 stayed 0.244) empirically confirms the cross-domain revision thesis: **flat architecture wrong; multi-tier sharded architecture is the path.**

Draft the multi-tier cell for GPU queue when home is back up. P9-REVISED is now THE decisive cross-domain test.

## Cell spec (per CROSS_DOMAIN_REVISION_MULTI_TIER routing)

### Training data
- ConceptNet 458K facts (Testbed-loaded; ingest universal-relation patterns)
- FB15K-237 14K entities + 237 relations (existing PP-275 training data)
- Wikidata Q-statements (Stage A ingest; preferably ~100K-1M facts subset)
- Optional: WordNet hierarchy (if cheap to add)

### Architecture
- **Tier 1 (universal relation primitives):** 15-30 universal patterns (cause-of, part-of, similar-to, opposite-to, contained-flow, central-force, hierarchical-containment, ...). Extract via schema-extraction (PP-282/284 mechanism) over ConceptNet relation vocabulary.
- **Tier 2 (domain archetypes):** 100-500 domain-specific instantiations (fluid-dynamics, electromagnetism, gravitation, social-roles, anatomy, business, biology, ...). Extract via secondary schema-extraction over Tier 1 + domain context.
- **Tier 3 (entities):** Per-domain entity embeddings. FB15K + Wikidata entities co-trained in single universal embedding space.
- **Tier 4 (atomic):** Token-level codebook for low-level binding.
- **Per-tier cleanup memory** (Hopfield-style attractor at each tier; mandatory per COMP-DEPTH P0 finding).
- **Cross-tier composition** via FHRR binding.

### Test queries (50-100 cross-domain analogy)
Each query: A:B :: C:? where (A,B) and (C,D) are in DIFFERENT domains.
Examples:
- water : pipe :: electricity : ? (expected: wire)
- king : queen :: father : ? (expected: mother)
- solar system : sun :: atom : ? (expected: nucleus)
- engine : car :: heart : ? (expected: body)
- premise : argument :: ingredient : ? (expected: recipe)

Cover at least 5 domain pairs (physics-electricity, social-biology, economics-medicine, etc.).

### Algorithm
1. Decompose (A, B) into tier components via composition unbinding
2. Identify Tier 1 universal pattern via cleanup at Tier 1
3. Find Tier 2 archetype in target domain (C's domain)
4. Apply universal pattern to Tier 2 archetype
5. Instantiate Tier 3 entity in target domain via cleanup at Tier 3

### Pre-registered HARD-PASS gates
- HARD-PASS: cross-domain Hits@1 ≥ 0.55 (small LLM parity)
- STRETCH: Hits@1 ≥ 0.70 (above small LLMs)
- HARD-FAIL: Hits@1 < 0.30 (below baseline)

### Baselines
- Flat RotatE (current PP-275; 0.244 baseline)
- Small LLM (7B class; typically 0.40-0.55 on similar tasks)

### Compute estimate
- 6-12h GPU for training
- 1-2h GPU for inference
- 4 tiers × per-tier cleanup memory
- Multi-domain training over union of 3 KBs

### Why this is the decisive test
- Multi-tier architecture is structurally right (FHRR designed for this)
- ConceptNet 458K + FB15K + Wikidata = universal embedding space
- PP-282/284 schemas validated AT ceiling (Tier 1/2 mechanism works)
- COMP-DEPTH P0 validated per-tier cleanup mechanism
- All primitives exist; just need to assemble

## Cross-references
- CROSS_DOMAIN_REVISION_MULTI_TIER architecture: notes/research_to_exp_dev_CROSS_DOMAIN_REVISION_MULTI_TIER_2026-06-10.md
- Cross-domain 3x drill: notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md
- COMP-DEPTH P0 (per-level cleanup): notes/exp_dev_to_research_COMP_P0_DECISIVE_RESULT_2026-06-10.md
- Schemas PP-282/284: notes/strategy_decisions_2026-06-09.md
- NEG-RES Tier-1 results (this cell's go-ahead): notes/exp_dev_to_research_NEGRES_TIER1_RESULTS_2026-06-10.md

---

**Exp-Dev:** authorized. Draft against ConceptNet+FB15K+Wikidata for GPU queue when home reconciles. This is THE test that determines whether substrate algebraic compositional architecture beats LLM attention on cross-domain.

If HARD-PASS: substrate beats LLMs on cross-domain via algebraic decomposition; 16 v3.0 capabilities including cross-domain are categorical.
If HARD-FAIL: drill's structural-theorem framing was correct; LLM-hybrid (P6) is the empirical answer; substrate stays within-domain dominant.

Either result is decisive. The test is worth the GPU budget.
