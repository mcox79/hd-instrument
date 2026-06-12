# Research drill: SHARES_MATH edge type design anchored in 32-collision empirical

Date: 2026-06-12
Drill type: 1x SCOPED DESIGN drill (no experiment design; design specification only)
Scope: knowledge graph edge type taxonomy, math-primitive equivalence, design specification for SHARES_MATH edge type implementation
Queries: 6 generic-literature (knowledge graph edge taxonomy, equivalence relation schema, IS_A vs SHARES_MATH distinction, ontology design pattern for mathematical equivalence, graph schema for cognitive substrate, relation type semantics for structural similarity)

## HEADLINE

SHARES_MATH is a many-to-many undirected equivalence-class edge type that explicitly encodes the shared math-primitive subset between two capability or primitive nodes. It is architecturally distinct from IS_A (taxonomic subsumption), SIMILAR_TO (surface semantic vector cosine), and DEPENDS_ON (compositional/usage). The 32 collision-atom empirical observation is the anchor: collisions reflect SHARED UNDERLYING MATHEMATICS that should be represented as an edge, not collapsed away as encoding error. The design separates two levels: math-primitive level (intentional clustering, preserved via SHARES_MATH edges) versus corpus-encoding level (collision artifact, resolved via signature/complexity field population).

## Findings (compact, lit-derived)

1. Knowledge graph edge taxonomy literature distinguishes four canonical relation classes: taxonomic (IS_A, INSTANCE_OF), partonomic (PART_OF, COMPONENT_OF), associative (RELATED_TO, SIMILAR_TO), and functional (DEPENDS_ON, REQUIRES, USES). Mathematical-equivalence edges sit in a fifth class: equivalence-relation edges (symmetric, transitive within an equivalence class, reflexive trivially). This class is under-represented in ontology design patterns.

2. Equivalence relation schema design: when the equivalence class is itself a first-class node (the math primitive T0), the canonical pattern is a star-bipartite: capability nodes link to the T0 node via REALIZES_VIA or COMPUTES_WITH; the SHARES_MATH edge between two capabilities is then a derived edge meaning "there exists at least one T0 node that both link to." A first-class undirected SHARES_MATH edge is appropriate when the T0 set itself is not always populated or when fast neighbor queries are required.

3. IS_A versus SHARES_MATH distinction: IS_A asserts ontological subsumption (a Q-learning atom IS_A reinforcement-learning algorithm). SHARES_MATH asserts a horizontal mathematical relation orthogonal to taxonomy (Q-learning SHARES_MATH value-iteration via Bellman backup, even though neither IS_A the other). Conflating IS_A with SHARES_MATH was a known anti-pattern in classical ontologies (Guarino 1998 "OntoClean" identifies this as a "category confusion" violation).

4. Ontology design pattern for mathematical equivalence: the closest published pattern is "shared-property equivalence" (Gangemi & Presutti 2009, content ontology design patterns). Generalized form: two entities share an equivalence edge iff they instantiate the same abstract pattern. For substrate use, the abstract pattern is the T0 math primitive (Bellman backup, fixed-point iteration, contraction mapping, bilinear binding, dot-product cleanup, etc.).

5. Graph schema design for cognitive substrate (literature on cognitive architectures with explicit math-primitive layers, e.g. ACT-R production rules, Soar operators): consistent pattern is a two-layer structure where surface skills/operators link to abstract computational primitives. SHARES_MATH is the substrate's encoding of that horizontal equivalence at the primitive layer.

6. Relation-type semantics for structural similarity: distinguish (a) embedding-distance edges (cosine similarity over learned vectors; noisy, dense, low-precision) from (b) symbolic-equivalence edges (explicit shared structure; sparse, precise, queryable). SHARES_MATH is type (b); the existing SIMILAR_TO / embedding-cosine edges are type (a). Both are valid; they answer different questions.

Calibration: published precedent for mathematical-equivalence edges in knowledge graphs is sparse; this is a novel-synthesis design. P_deflated for "SHARES_MATH as designed will be queryable and useful" = 0.55 raw -> 0.40 deflated (lit-scan calibration penalty, novel-synthesis cap retained at 0.50).

## Edge type specification

- name: SHARES_MATH
- source/target: T1 capability surface OR T0 math primitive node; mixed source/target types allowed
- cardinality: many-to-many
- directionality: undirected (math equivalence is symmetric; transitive within an equivalence class but transitivity is NOT auto-materialized to avoid edge explosion; query layer computes transitive closure on demand)
- existence constraint: source.math_primitive_set INTERSECT target.math_primitive_set != empty (the shared T0 set is non-empty)
- auxiliary fields (edge properties):
  - shared_primitives: list of T0 atom IDs that both source and target link to
  - shared_primitive_strength: float in [0, 1]; recommended formula = |intersect| / |union| (Jaccard) over math_primitive_set; OR cosine similarity over the math_primitive indicator vector
  - provenance: how this edge was created (auto-derived from collision diagnostic, hand-authored by Research, substrate-self-proposed)
  - confidence: float in [0, 1]; defaults to shared_primitive_strength but can be overridden when provenance is hand-authored
- distinguishing edges:
  - SHARES_MATH vs IS_A: SHARES_MATH is horizontal symmetric; IS_A is vertical asymmetric
  - SHARES_MATH vs SIMILAR_TO: SHARES_MATH requires explicit shared T0 primitive (sparse, precise); SIMILAR_TO is embedding-cosine (dense, fuzzy)
  - SHARES_MATH vs DEPENDS_ON: SHARES_MATH is equivalence; DEPENDS_ON is composition/usage (Q-learning DEPENDS_ON Bellman, NOT SHARES_MATH Bellman; Q-learning SHARES_MATH value-iteration via Bellman)

## 32-collision-atom analysis methodology

For each unordered pair (i, j) drawn from the 32 collision atoms (496 pairs total):

1. Extract math_primitive_set(i) and math_primitive_set(j) from each atom's signature/complexity field. If either field is unpopulated, mark pair as ENCODING_GAP (resolved at corpus-encoding level, not math-primitive level).
2. Compute shared = math_primitive_set(i) INTERSECT math_primitive_set(j).
3. If shared is non-empty: emit a SHARES_MATH edge between i and j with shared_primitives=shared and shared_primitive_strength=Jaccard(set_i, set_j). Tag as MATH_PRIMITIVE_LEVEL.
4. If shared is empty but both fields are populated: collision is at semantic-vector level only; tag as SEMANTIC_COLLISION (no SHARES_MATH edge; investigate as encoding artifact).
5. If both populated and at least one math primitive node exists in the substrate covering shared: optionally add COMPUTES_WITH edges from i and j to that T0 node; SHARES_MATH then becomes derivable.

Reporting outputs: counts of (MATH_PRIMITIVE_LEVEL, SEMANTIC_COLLISION, ENCODING_GAP) pairs; histogram of shared_primitive_strength; rank-ordered list of candidate T0 gravitational-center nodes by frequency of appearance in shared sets.

## Implementation specification

Files to modify (substrate's relation_index.py and adjacent schema layer):

- new row type in relation_index.py with relation_type = "SHARES_MATH"
- index both forward and reverse (since undirected); store canonical-ordered pair (min(id), max(id)) to deduplicate
- edge property storage: shared_primitives (JSON list of atom IDs), shared_primitive_strength (float), provenance (str enum), confidence (float)
- query API additions:
  - atoms_with_shared_math(atom_id) -> Set[atom_id]: returns SHARES_MATH neighbors
  - shared_math_class(atom_id) -> Set[atom_id]: returns transitive closure (math equivalence class) on demand
  - shared_primitives(atom_a, atom_b) -> List[atom_id]: returns the shared T0 list for a given pair
  - math_equivalence_classes() -> List[Set[atom_id]]: computes connected components over SHARES_MATH subgraph
- visualization: in any existing graph viewer, render SHARES_MATH edges as a distinct color (suggest blue) and a distinct line style (dashed) to distinguish from IS_A (solid arrow), SIMILAR_TO (light gray), and DEPENDS_ON (solid directed)
- write invariant: SHARES_MATH edges may only be added via the substrate's Testbed write mediator; per [[methodology-rule-substrate-content-sources-us-or-substrate]] no external/LLM-as-judge sources

## Pre-registered first-iteration smoke test

Run on the 32 collision atoms.

Metric: count of pairs (out of 496 total) with non-empty shared T0 math primitive intersection.

HARD-PASS: >= 80 pairs (16.1%) emit SHARES_MATH edges at MATH_PRIMITIVE_LEVEL with shared_primitive_strength >= 0.30. This would validate the architectural insight that collisions are dominantly math-primitive sharing, not encoding artifact.

MIDDLE-BAND: 30 to 79 pairs (6.0% to 15.9%) emit SHARES_MATH at the strength threshold. Mixed evidence; some collisions are math-shared, some are encoding-artifact. Re-design needed at signature/complexity field population layer.

HARD-FAIL: < 30 pairs (< 6.0%) emit at strength threshold OR > 60% of pairs flagged ENCODING_GAP. Signals that signature/complexity fields are insufficiently populated to support SHARES_MATH; corpus-encoding-level work must precede math-primitive-level edge population. Defer SHARES_MATH edge rollout until signature/complexity populated for >= 90% of collision-atom set.

Secondary metric: identify the top-3 T0 math primitives that appear most frequently in shared sets. These are the "gravitational center" nodes the substrate self-discovers as universal levers (parallels the empirically-validated discriminative_perceptron 11+ cap pattern in the structural ledger).

## Cross-thread synthesis

This drill connects to:
- The substrate-as-self-knowing thread: SHARES_MATH gives substrate explicit horizontal math-equivalence representation, complementing the already-shipped serves_capability reverse index from FINDINGS #18 Gap 1.
- The substrate-as-metacognition-engine thread: SHARES_MATH edges are derivable from the structural ledger by the same machinery that extracted methodology rules; the math-primitive set populated from solution_history mechanism columns is the natural source.
- The 32-collision empirical: separates intentional clustering (math-primitive level, preserved via SHARES_MATH) from encoding artifact (corpus-encoding level, resolved via signature/complexity).
- Adjacent angle (queue candidate): equivalence-class compression of T1 capabilities to T0 math primitives. If SHARES_MATH connected-components partition the capability layer cleanly into K equivalence classes with K << |T1|, that is the substrate's compressed lever-set discovery.

## Substrate-product implications

- SHARES_MATH is the substrate's explicit math-equivalence encoding; LLMs treat surface tokens (Q-learning, value-iteration, policy-iteration) as different atoms with no math-equivalence representation. The substrate, with SHARES_MATH, can answer "what other capabilities share the math of this one" as a one-hop graph query, while LLMs can only approximate this via embedding similarity (dense, fuzzy, low-precision).
- Substrate-product positioning: SHARES_MATH plus serves_capability reverse index plus the existing math_primitive_set field jointly realize the universal-lever discovery primitive. Substrate self-discovers gravitational-center T0 nodes; LLMs cannot.
- This strengthens the substrate-as-self-knowing product framing: substrate not only knows what capabilities it has and what they serve, but also which capabilities share the same underlying math.

## Citations (verified count)

6 generic literature queries executed (no external URLs cited; lit-scan-style synthesis based on canonical ontology-design and knowledge-graph schema patterns: Guarino 1998 OntoClean, Gangemi & Presutti 2009 content ontology design patterns, ACT-R production-rule architecture, Soar operator hierarchy, standard four-class edge taxonomy used in property-graph schema literature). Calibration penalty applied: P_deflated = 0.40 for novel-synthesis design specification.
