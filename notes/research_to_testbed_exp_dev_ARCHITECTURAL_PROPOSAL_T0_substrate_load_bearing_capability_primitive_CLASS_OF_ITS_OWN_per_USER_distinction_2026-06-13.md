# Research -> Testbed + Exp-Dev: ARCHITECTURAL PROPOSAL -- T0 substrate-load-bearing capability primitive CLASS OF ITS OWN -- per USER distinction "additive math + equivalence_relation + inner_product are TOOLS substrate uses; 1M-cited first-book is MATERIAL"

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER clarification "shouldn't there be a special class of foundational that defines how the substrate interacts with things? a book cited 1M times might just be the first book on a topic, but ADDITION is extraordinarily foundational. They're in different worlds right"

## Intuitive framing (craftsman analogy)

USER's distinction is sharper than current substrate architecture supports.

Think of substrate like a **craftsman**:
- **TOOLS** = hammer, saw, measuring tape; the craftsman USES these to DO WORK
- **MATERIALS** = wood, nails, finished furniture; the craftsman WORKS ON these

Both matter, but they're in totally different worlds:
- A craftsman without tools is useless
- A craftsman with tools but no materials has nothing to make

**Substrate's current architecture conflates these into one axis (T0-T3 tier ladder)**.

USER's examples clarify:
- `addition` = TOOL: substrate uses this to compute cosines + count + aggregate scores + everything
- `equivalence_relation` = TOOL: this DEFINES what SHARES_MATH bisimulation MEANS
- `inner_product` = TOOL: cosine similarity = inner product over normalized vectors; substrate cleanup + retrieval use this constantly
- `convolution` = TOOL: FHRR bind IS circular convolution; substrate's binding operation
- `axioms` (as a concept) = TOOL: terminal in L6-PROOF chains
- "First book on category theory" = MATERIAL: cited a lot but substrate doesn't USE it to do anything operational
- A specific theorem about prime numbers = MATERIAL: finished furniture sitting on shelf

## Two orthogonal axes (current vs proposed)

### Current substrate architecture (single axis)

- T0 axiom / bedrock (e.g. `axioms` concept itself)
- T1 foundational primitive (e.g. vector_space, jensen_inequality)
- T2 archetype / schema (e.g. cosine_cleanup, transformer_attention)
- T3 instance / specific (most ingested data)

Promotion: T3 -> T2 -> T1 -> T0 via KP P1 (frequency) + P4 (geometry) + P3 (bisimulation) + P5 (Curry-Howard derivability)

### Proposed substrate architecture (two orthogonal axes)

**Axis 1: Epistemic foundationality** (citation breadth, structural-graph centrality)
- T3 instance
- T2 archetype (cited / clustered)
- T1 foundational (foundationally-derivable + widely cited)

**Axis 2: Substrate-architectural foundationality** (capability-load-bearing for substrate's OPERATORS) -- NEW

Add a boolean attribute OR a new tier marker on Axis 2:

Option A: New T0 special class -- **T0_substrate_load_bearing_capability_primitive (TLBCP)**
- Distinct from T0 axiom (which is just epistemic-foundational)
- Examples: `addition`, `equivalence_relation`, `inner_product`, `convolution`, `axioms`, `vector_space`, `cosine_similarity`, `softmax_function`, `derivative`, `gradient`
- Properties: substrate's operators (KP + L6-PROOF + Pi/Sigma + SHARES_MATH + CHTV-1 + Stratified Hybrid routing + cleanup + recursive loop) USE these to define their behavior

Option B: Boolean attribute on existing tier `substrate_load_bearing: true`
- Cleaner; preserves T0-T3 tier ladder
- Atoms marked `substrate_load_bearing: true` are in a different epistemic class regardless of T0-T3 tier
- More flexible (T2 archetype atom could be load-bearing in some contexts; T1 atom could be informational but not load-bearing)

Option C: Both -- a NEW T-1 tier (above T0) for load-bearing capability primitives + keep T0 epistemic-foundational
- T-1 capability primitives (TLBCP) -- substrate's TOOLS
- T0 epistemic axioms -- foundational concepts substrate KNOWS ABOUT
- T1-T3 = epistemic content

## Recommended: Option B (boolean attribute) + Option C semantics

**Add boolean attribute `substrate_load_bearing: true/false`** to all atoms.

Atoms with `substrate_load_bearing: true` belong to a distinct architectural class regardless of T0-T3 epistemic tier:

```yaml
- canonical_name: addition
  tier: T0  # epistemic: irreducible math primitive
  substrate_load_bearing: true  # NEW: substrate uses this operationally
  serves_capability:
    - "substrate_operator_basis"  # NEW capability class
    - "arithmetic_primitive"
    - "score_aggregation_in_cleanup"
    - "FHRR_addition_in_bind"
    - "expectation_summation"

- canonical_name: inner_product
  tier: T1  # epistemic: foundational
  substrate_load_bearing: true  # NEW: substrate uses this in cleanup + cosine
  serves_capability:
    - "substrate_operator_basis"
    - "linear_algebra_foundation"
    - "embedding_geometry"
    - "cosine_similarity_definition"

- canonical_name: jensen_inequality
  tier: T1  # epistemic: foundational
  substrate_load_bearing: false  # NEW: substrate doesn't USE this; substrate KNOWS this
  serves_capability:
    - "variational_lower_bounds"
    - "KL_non_negativity_proof"
```

## Concrete substrate-load-bearing atom inventory (Research draft list; Testbed refines)

These atoms are TOOLS substrate uses to do work:

```yaml
# Arithmetic + algebraic primitives (substrate's basic operations)
- addition
- multiplication
- equivalence_relation
- order_relation_concept

# Linear algebra (substrate's representational substrate)
- vector_space
- inner_product
- norm_concept
- linear_independence
- orthogonality
- cosine_similarity
- matrix_decomposition (general)

# Information theory (substrate's metrics + losses)
- shannon_entropy
- kl_divergence
- cross_entropy
- softmax_function

# Calculus / optimization (substrate's training math)
- derivative
- gradient
- chain_rule_calculus

# Geometric / topological (substrate's similarity + cleanup)
- metric_space
- continuity (concept)

# VSA / HRR / FHRR primitives (substrate's binding operation)
- convolution
- circular_convolution
- fhrr_bind
- fhrr_unbind
- composite_hrr_alpha_05_blend

# Logical / categorical (substrate's typed-derivation graph)
- axioms (concept)
- category
- functor
- natural_transformation

# Algorithmic (substrate's data structures)
- recursion
- optimal_substructure
- fixed_point_iteration
- dynamic_programming
```

~35-50 atoms in this special class (Research-drafted; Testbed should refine + verify each is actually USED by substrate operators).

## How promotion changes per this proposal

**KP P1 frequency-promotion**: now promotes within epistemic axis only. Does NOT mark substrate_load_bearing.

**KP P4 sleep-replay**: now promotes within epistemic axis only. Does NOT mark substrate_load_bearing.

**NEW KP P6**: substrate-load-bearing detection mechanism. Operators ARE the dependency. If an atom appears in operator definitions (Stratified Hybrid routing code uses inner_product; cleanup uses cosine_similarity; L6-PROOF uses axioms) -> mark substrate_load_bearing: true. Otherwise mark substrate_load_bearing: false (default for ingested content).

KP P6 should be EXPLICITLY AUTHORED (curated list) not heuristically inferred. Substrate's operator code is small; manually identifying load-bearing primitives is feasible + correct.

## Why this matters for USER vision

USER strategic question: "we need a way to organize and handle different fields ... we may find that there is more or less a universal way to promote and interact with everything."

H3 hybrid drill verdict (2026-06-13): universal operators + field-specific signal extractors + first-class field partition routing.

**T0_substrate_load_bearing axis answers WHAT the universal operators USE**:
- Same load-bearing primitives across all fields (addition + inner_product + axioms + convolution + ...)
- Universal operators ARE BUILT FROM substrate-load-bearing primitives
- Field-specific signal extractors work over these same primitives

LLM categorical gap WIDENS:
"Substrate has explicit substrate-load-bearing capability primitives (~35-50 atoms) that DEFINE its operations. LLMs have implicit weights with no explicit class for which weights are operationally load-bearing vs informational content. Substrate can audit ITS OWN machinery; LLMs cannot."

## Substrate-product positioning artifact

NEW canonical claim (Cycle 51 close + post USER craftsman distinction):
"Substrate distinguishes between its TOOLS (substrate-load-bearing capability primitives like addition + inner_product + axioms) and its MATERIALS (all ingested content). The tools are a curated small class (~35-50 atoms) defining what substrate IS; the materials are a vast corpus defining what substrate KNOWS. LLMs cannot distinguish these — all weights are mixed without explicit operational annotation."

## 12th methodology rule extension

12th rule (1st appearance per Tier 5 framework just-filed):
**meta::RULE_universal_operators_with_field_local_signal_extractors_and_first_class_field_partition_routing**

USER's craftsman distinction adds dimension:
**meta::RULE_substrate_architecture_distinguishes_tools_from_materials_two_orthogonal_axes_epistemic_foundationality_vs_capability_load_bearing_primitive**

If sustained 2nd + 3rd appearance, promotes to 13th confirmed methodology rule.

## Routing

- **Testbed**: implement boolean attribute `substrate_load_bearing` on Atom schema; curate the ~35-50 atoms list (Research draft above is starting point; Testbed refines per actual operator code audit); update KP operator to preserve this attribute under promotions; report which atoms are CONFIRMED load-bearing per operator-code audit
- **Exp-Dev**: this proposal complements universal-vs-field-specific drill #3 (6 cells endorsed; FPRS + UOT first); KP P6 substrate-load-bearing detection mechanism could be 5th KP path candidate (alternative to P2 DRUM)
- **Research**: filing this proposal + memory entry for two-orthogonal-axes architecture; standing for Testbed verification of load-bearing atom audit; BATCH 25 information geometry continuing per priority queue

## Cross-references

- USER directive 2026-06-13 "shouldn't there be a special class of foundational that defines how the substrate interacts with things?"
- memory `substrate-methodology-rule-12th-universal-operators-field-specific-signal-extractors-first-class-field-partition-routing-H3-HYBRID-first-appearance-2026-06-13` (12th rule predecessor)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2-of-5-paths-multi-mechanism-validated-2026-06-13` (KP operator that PROMOTES epistemically; load-bearing axis is orthogonal)
- memory `feedback-always-include-intuitive-explanation-alongside-jargon-USER-LOCKED-2026-06-13` (craftsman analogy applied)

---

**Testbed + Exp-Dev:** ARCHITECTURAL PROPOSAL T0 substrate-load-bearing capability primitive CLASS OF ITS OWN per USER distinction + craftsman analogy substrate has TOOLS substrate USES vs MATERIALS substrate WORKS ON + two orthogonal axes epistemic foundationality (citation/centrality KP P1+P4) vs substrate-architectural foundationality (capability-load-bearing operators USE) + Recommended Option B boolean attribute substrate_load_bearing on atom schema + curated ~35-50 atom list (addition + inner_product + axioms + convolution + fhrr_bind + cosine_similarity + softmax + derivative + gradient + recursion + ...) + KP P6 substrate-load-bearing detection mechanism explicitly authored not heuristic + answers H3 hybrid drill what universal operators USE same load-bearing across fields + LLM categorical gap WIDENS substrate distinguishes tools from materials explicitly LLMs cannot + 13th methodology rule candidate distinguishes-tools-from-materials + Testbed implements + Exp-Dev verification + USER full-auto overnight continuing.
