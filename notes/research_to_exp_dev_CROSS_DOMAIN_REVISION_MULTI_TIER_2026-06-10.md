# Research -> Exp-Dev: CROSS-DOMAIN ANALOGY REVISION (multi-tier sharding architecture)

**From:** Research  **Date:** 2026-06-10
**Re:** Cross-domain analogy negative finding (STRETCH4-2 0.244) — drill diagnosis was incomplete; multi-tier sharding is the correct architecture

## User insight that corrects the drill

**Analogies work because shared abstractions live at a HIGHER TIER than specific entities.**

The drill tested flat single-relation RotatE rotation. That's NOT substrate's architecture for analogy. Substrate's compositional algebra (FHRR binding + per-level cleanup; cliff crossed via COMP-DEPTH P0) supports **multi-tier decomposition** that is the correct cross-domain mechanism.

## The four-tier architecture

| Tier | Content | Count | Examples |
|---|---|---|---|
| Tier 1 (universal) | Physics/math laws, abstract patterns, relation primitives | ~15-30 | cause-of, part-of, contained-flow, similar-to, opposite-to, central-force, hierarchical-containment |
| Tier 2 (domain-archetype) | Domain instantiations of universal patterns | ~100-500 | fluid-dynamics, electromagnetism, gravitation, social-roles |
| Tier 3 (entity-specific) | Concrete instances per domain | ~1M+ | water, electricity, planets, kings |
| Tier 4 (atomic) | Token-level codebook entries | ~10K-100K | individual concept atoms |

**Each tier has its own cleanup memory** (per-level cleanup mandatory per COMP-DEPTH P0 finding).

## Why this beats LLMs cross-domain

**LLMs:** entangled representations. King = bundle of royalty + gender + power + crown + history — all blended via attention. Cannot decompose.

**Substrate:** algebraic decomposition. King = gender⊗male ⊕ role⊗royal ⊕ ... — FHRR binding lets you unbind any component, swap it, recompose.

**Plate 1995 FHRR is exactly designed for this.** Cross-domain analogy via:
1. Decompose source pair (A, B) into tier components
2. Identify Tier 1 universal pattern shared
3. Find Tier 2 archetype in target domain
4. Instantiate Tier 3 entity in target

**LLMs do this implicitly via attention; substrate does it explicitly via algebra.**

## What already exists (validated tonight)

- **PP-282 (220 schemas) + PP-284 (1000 schemas cross-domain)** ARE Tier 1 + Tier 2 mechanism (auto-extracted from ConceptNet at ceiling)
- **PP-275 RotatE within-domain Hits@1=0.899** is Tier 3 entity-relation rotation (works WITHIN single embedding space)
- **PP-265 cultural conventions (30 scripts)** ARE Tier 2 archetypes
- **COMP-DEPTH P0 per-level cleanup** is the mechanism that preserves fidelity across tiers
- **Per-predicate sharding (production)** is Tier 3/4 mechanism

**Substrate already has all the primitives. The test setup didn't use them at the right tier.**

## P9 ELEVATED TO T1 PRIORITY (revised from T3)

### P9-REVISED: MULTI-TIER-SHARDED-CROSS-DOMAIN-ANALOGY

**Architecture:**
- Tier 1: Train universal relation primitives (15-30) over ConceptNet relation vocabulary
- Tier 2: Auto-extract domain archetypes via schema-extraction (PP-282/284 mechanism)
- Tier 3: Per-domain entity embeddings (FB15K + Wikidata + ConceptNet entities)
- Cross-tier composition via FHRR binding
- Per-tier cleanup memory (mandatory per COMP-DEPTH P0)

**Test query example:** "water is to pipe as electricity is to ?"
1. Extract Tier 1 pattern from (water, pipe) → "contained-flow"
2. Decompose source: water = (substance: water-atoms) ⊗ (state: liquid) ⊗ (flow-medium: pipe)
3. Tier 1 cleanup → "contained-flow" pattern
4. Find Tier 2 archetype matching electricity domain → "electromagnetism"
5. Apply "contained-flow" pattern to "electromagnetism" archetype
6. Cleanup → wire

**HARD-PASS gate:** cross-domain Hits@1 ≥ 0.55 (parity with small LLMs) on 100-query cross-domain test
**STRETCH gate:** Hits@1 ≥ 0.70 (above small LLMs)

**Training data:**
- ConceptNet 458K facts (already loaded in Testbed)
- FB15K-237 14K entities + 237 relations (already trained PP-275)
- Wikidata Q-statements (Stage A ingest running)
- WordNet hierarchy (cheap to add)

**P_deflated REVISED:** 0.50-0.60 (higher than original 0.22 multi-domain training estimate because architecture is structurally right)

**Time:** 1 week + 6-12h GPU

## Why P_deflated is higher than original estimate

Original drill assumed flat embedding space learning. Multi-tier architecture is structurally right — leverages substrate's strengths:
- FHRR binding/unbinding (Plate 1995 native)
- Per-level cleanup (COMP-DEPTH P0 validated)
- Schema extraction (PP-282/284 validated at 1000 schemas)
- RotatE-style rotations work WITHIN tier
- Cross-tier composition is what FHRR algebra is FOR

## P6 LLM-HYBRID DEMOTED (was T2; now T3)

LLM-hybrid is still useful but no longer the fastest path. Multi-tier sharded substrate should match/exceed LLMs cross-domain via the architectural mechanism.

Keep as fallback if multi-tier training underperforms.

## P2 STRUCTURAL-ALIGNMENT remains T1 (still 1-day cheap test)

Structural alignment (Gentner) IS what multi-tier composition is doing. Both are valid; structural alignment is the cheapest pre-test before committing to multi-tier training.

## Sequencing revision

**Day 1 (immediate):**
- P1 BUNDLE-SPLIT C=4 (2x capacity free)
- P2 STRUCTURAL-ALIGNMENT (cross-domain to 0.40+; 1 day)

**Days 2-3:**
- P3 COMP-OVERCOME-BARRIER P1 sweep (in flight)
- P4 TRAINED-CONFIDENCE-HEAD

**Week 1 (multi-tier training — ELEVATED PRIORITY):**
- **P9-REVISED MULTI-TIER-SHARDED-CROSS-DOMAIN** (was T3; now T1; 1 week + GPU)
- P5 SPARSE-WILLSHAW or P7 MODERN-HOPFIELD

**Week 2-3:**
- P6 LLM-HYBRID (now fallback)
- P8 POPULATION-CONFIDENCE-N100

## Strategic implications

**If multi-tier sharded substrate matches/exceeds LLMs cross-domain:**
- Algebraic compositional architecture validated as cross-domain mechanism
- LLM attention is NOT the only cross-domain solution
- Substrate's interpretable + auditable + decomposable advantages compose with cross-domain capability
- 16 capabilities unlocked (per v3.0 compositional cognitive architecture) extend to cross-domain naturally

**If multi-tier fails too:**
- Then LLM-hybrid P6 is the empirical answer
- Drill's structural-theorem framing was correct

**Either result is decisive.** Test must use the multi-tier architecture, not flat RotatE.

## Cross-references
- Original cross-domain 3x drill: notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md
- Cross-domain 2x: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md
- COMP-DEPTH P0 (per-level cleanup; cliff crossed): notes/exp_dev_to_research_COMP_P0_DECISIVE_RESULT_2026-06-10.md
- Schemas PP-282/PP-284: notes/strategy_decisions_2026-06-09.md
- Original priority routing: notes/research_to_exp_dev_NEGATIVE_RESOLUTION_PRIORITIES_2026-06-10.md (P9 ELEVATED)

---

**Exp-Dev:** revised cross-domain mechanism is multi-tier sharded architecture, not flat RotatE. Elevate P9 to T1. The structural advantage substrate has (algebraic decomposition vs LLM entangled attention) is the actual mechanism.

This is the user's architectural insight: analogies work via shared higher-tier abstractions; substrate's compositional algebra IS the right mechanism; per-tier cleanup (validated via COMP-DEPTH P0) maintains fidelity.

**The cross-domain 0.244 result tested the wrong architecture. Multi-tier sharded test is the decisive empirical question.**
