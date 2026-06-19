# Research drill: Algebra taxonomy + formal-systems operator catalogs (2x DEEP combined)

**Date:** 2026-06-11 (evening)
**Topic:** (Q1) algebra taxonomy for substrate atoms + (Q5) prior art in formal math systems' operator catalogs.
**Mode:** 2x DEEP combined (level-2 operational drill on substrate-self-index Level-A taxonomic encoding open questions)
**Output type:** concrete recommendation for taxonomy + operator-field list

---

## (a) HEADLINE

A 13-category algebra taxonomy organized along three axes (algebraic-kind + dynamics-kind + signature-kind) maximally separates the substrate's ~80-atom math layer; a 14-field operator-record schema (drawn from converging Mathematica + Lean Mathlib + Coq MathComp + Isabelle locale conventions, with two substrate-specific extensions) gives both query-time and decoration-time tags.  The four formal systems agree on a core record { name, arity, domain_sorts, codomain_sort, attributes-bag } and disagree only on hierarchy mechanism (bundled vs unbundled), which we resolve by carrying BOTH a single category tag (primary classification) AND a flat property-bag (Mathematica-style Attributes) for query.

---

## (b) Cheap decisive test

Tag 20 candidate substrate atoms by hand using the proposed 13-category taxonomy and 14-field schema; check three properties:

1. **No-collision:** no two structurally distinct atoms get identical (category, attributes) tuples (target: >= 18 / 20).
2. **Query-discriminative:** at least 6 named queries ("all idempotent binary substrate-native ops", "all unary operators that preserve cosine similarity", "all ternary operators with poly-time complexity", etc.) each return a non-empty proper subset (target: 6 / 6 return 2 to 8 atoms, never 0 and never all 20).
3. **Tier separability:** Tier-1 foundational vs Tier-2 substrate-primitive vs Tier-3 algorithm atoms are at-least-partially separated by the (category, complexity_class) projection (target: at least one category appears only in one tier).

Cost: ~30 minutes manual tagging + ~10 lines of pandas filter queries. Hard-pass means the taxonomy is ready for substrate-self-index pilot ingestion; hard-fail means the schema is either under-specified (collisions) or over-specified (queries return empty).

---

## (c) Falsifiable predictions

### HARD-PASS thresholds (must hit all three to ship taxonomy to pilot)

- **Predicate-coverage:** >= 18/20 hand-tagged atoms get a non-default value for at least 6 of 14 fields. If most atoms collapse to {category: "other", attributes: []}, the schema is decoration-only and useless for query.
- **Query non-degeneracy:** 6/6 named query types return between 2 and 8 atoms (never 0, never all 20). Confirms each query axis actually carves the space.
- **No-collision:** >= 18/20 atoms have unique (category, top-3-attributes) tuples. Confirms structural distinguishability.

### HARD-FAIL thresholds (any one triggers schema revision)

- **Single-category dominance:** > 12/20 atoms share the same category tag (taxonomy not discriminating).
- **Empty-query rate:** >= 2/6 named queries return 0 atoms (axis is dead weight).
- **All-query degeneracy:** >= 2/6 named queries return all 20 atoms (axis is constant).
- **Lean-Mathlib precedent violation:** any of the 13 proposed categories has zero structural-named precedent in Mathlib's `Mathlib/Algebra/` hierarchy (validates we are not inventing structures that mathematicians do not use).

### Adversarial probes (run if HARD-PASS marginal)

- Re-tag 10 of 20 atoms after 1 hour without looking at first pass; inter-rater agreement (self vs self) must be >= 8/10 on category and >= 7/10 on attribute bag. Tests schema stability.
- Have a non-substrate algorithm (e.g. classical Strassen matmul, classical Kalman filter) tagged with the same schema; if it cannot be tagged without inventing a new category, the schema is substrate-overfit.

---

## Drill 1 synthesis: Algebra taxonomy (13 categories along 3 axes)

### Design principles (from converged formal-systems lit)

1. **Single primary category + flat property-bag.** All four formal systems (Mathematica, Lean Mathlib, Coq MathComp, Isabelle/HOL) factor the operator description into (a) a primary type / structure / locale membership + (b) a separate attributes / instance / parameter set. This avoids combinatorial explosion of the primary hierarchy (Mathlib comm_monoid already depends on 7 ancestors in a diamond per Mathlib hierarchy_design docs) while keeping query power via the flat bag.
2. **Three orthogonal axes, not one ladder.** The mathematician's canonical ladder (Semigroup -> Monoid -> Group -> Ring -> Field) is the algebraic-structure axis only. Substrate atoms also need a dynamics axis (deterministic / stochastic / iterative / fixed-point) and a signature axis (binary-internal / endomorphism / projection / functorial). The HDC/VSA literature confirms binding + superposition + permutation are three structurally different operation classes; one axis cannot tag them well.
3. **Mathlib + MathComp + Isabelle agree on universal-algebra signature schema.** All three converge on the universal-algebra (signature, arity, domain-sort, codomain-sort) framing. Magma's "variety" concept maps directly: a category = same operator signature + common axioms. The substrate should adopt this as the structural base of the record.

### The 13-category taxonomy

Axis A: algebraic structure (which classical structure axioms an operator instantiates)

1. **monoid** -- associative + identity, no inverse required. Covers: bundling (superposition), Plus-style associative ops, string concat, sequence composition.
2. **group / abelian-group** -- monoid + inverse. Covers: FHRR binding (complex-multiply unit-modulus is abelian group), XOR (BSC binding), permutation composition (non-abelian).
3. **semiring / tropical-semiring** -- two operations linked by distributivity, additive idempotent allowed (max-plus / min-plus, probability-semiring, max-product). Covers: HMM Viterbi (max-plus path algebra), Dijkstra (min-plus), beam-search top-k accumulation.
4. **ring / field / vector-space-over-field** -- full ring structure with both additive inverse and multiplicative identity (and field if mult inverse present). Covers: PCA / ZCA (linear algebra over R), inner-product spaces, complex-field FHRR ambient space.
5. **module / algebra-over-field** -- vector space + bilinear multiplication. Covers: tensor-product representations (TPR), tensor algebras, Clifford-style structures.
6. **lattice / semilattice** -- idempotent + commutative + associative; absorption law if full lattice. Covers: max-pool, min-pool, set-union for shard merging, idempotent cleanup at saturation.
7. **metric-space / similarity-space** -- not a classical algebraic structure per se, but a sort with a binary R^+-valued operation (distance / similarity). Covers: cosine, Hamming, edit-distance, KL-divergence (asymmetric, so technically pre-metric / divergence).
8. **probability-space / measure** -- sigma-algebra + measure; sort-level membership. Covers: probability distributions, posteriors, count-NB likelihood, MAP/MLE.
9. **partial-order / poset** -- transitive antisymmetric reflexive; weaker than lattice (no join/meet guaranteed). Covers: dominance relations, DAG topo-sort, ranking, tier ordering.
10. **graph / category** -- objects + morphisms; covers categorical operations and graph algorithms with morphism-composition semantics. Covers: Chu-Liu-Edmonds MST, Hungarian bipartite matching (bipartite graph + cost morphism), Jonker-Volgenant.
11. **operator-algebra / hilbert-space-operator** -- bounded operator on Hilbert space, possibly with C*-algebra structure. Covers: phasor algebra (unitary operators on C^N), unitary permutations, projection cleanup operators.
12. **dynamical-system / fixed-point** -- a system with state + transition + termination criterion; covers iterative / convergent algorithms. Covers: cleanup iteration, fast-marching, Glauber dynamics, MCMC, EM iteration.
13. **substrate-native / phasor-bundle** -- explicit substrate-specific category for operators that do not cleanly factor through any classical structure because their axioms include both algebraic and approximate-orthogonality components (binding + superposition jointly defined per HDC/VSA Survey Part I). Covers: FHRR binding-superposition composite, Tier-2 schemas (count-weighted superposition), context-binding with approximate-orthogonality guarantee.

### Why 13 (not 10 and not 20)

- 10 collapses semiring vs lattice (both idempotent-semigroup descendants but semiring has two ops with distributivity, lattice has two ops with absorption -- structurally distinct per nLab + Mathlib).
- 10 collapses graph/category and dynamical-system (Hungarian is graph-algorithmic, EM is dynamical-iterative -- different time-axis semantics).
- 20 over-splits abelian vs non-abelian groups (handled by `commutative: true` flag in attributes), and over-splits free / finitely-presented / matrix groups (handled by `representation` field).
- 13 is roughly Mathlib's top-level partition of `Mathlib/Algebra/` directories: Group, Ring, Field, Order, Module, Lattice, Category, Hom -- plus our three substrate-specific extensions (similarity-space, dynamical-system, substrate-native).

### Tier separability (from Q1 design constraint)

- Tier-1 foundational: categories 1-7 + 11 dominate (groups, rings, fields, vector spaces, lattices, metrics).
- Tier-2 substrate primitive: category 13 dominates (substrate-native) plus 2 and 11 (FHRR is an abelian group of unit-modulus complex numbers under elementwise multiplication, and also lives in the unitary operator algebra).
- Tier-3 algorithms: categories 3, 6, 9, 10, 12 dominate (semirings drive Viterbi/Dijkstra, graph-category drives Hungarian/MST, dynamical-system drives EM/MCMC).
- Tier-4 composed methods: predominantly category 13 (substrate-native) over a backbone of Tier-3 algorithmic ops.

This is the empirical tier-discriminator: category 13 (substrate-native) only appears in Tier-2 and Tier-4 -- precisely the levels where substrate-specific approximate-orthogonality joint axioms exist.

---

## Drill 2 synthesis: Prior-art operator-record schemas

### What the four systems converge on

| Aspect | Mathematica | Lean 4 Mathlib | Coq MathComp | Isabelle/HOL |
|---|---|---|---|---|
| Primary classification mechanism | Head + Attributes bag | Typeclass extension chain | Canonical structure / mixin | Locale + axclass |
| Arity tracking | argument-pattern in DownValues | type signature in Pi-binder | record field types | locale parameter list |
| Algebraic axioms | declared as separate Attributes (Flat, Orderless, OneIdentity) | inherited via `extends` in class hierarchy | mixin records (e.g. AssocLaw, CommLaw) | locale assumption clauses |
| Identity / inverse | OneIdentity + explicit identity-element rule | `1` / `0` and `mul_one` lemmas in monoid | `idm` field on monoid mixin | identity element axiom in monoid locale |
| Hierarchy mechanism | flat + attribute composition | bundled diamond inheritance | bundled canonical structures (the SSReflect approach) | locale interpretation graph |
| Domain / type constraints | Pattern conditions (`_Real`, `_?NumericQ`) | dependent types | type parameter of structure | locale type parameter |
| User-facing query mechanism | Attributes[f], Information[f] | `#check`, `whnf`, mathlib search | `Print Canonical Projections` | `find_theorems`, `print_locale` |

### Convergent core record (load-bearing across all 4 systems)

Every formal-systems operator entry minimally contains:

- `name` (string identifier)
- `arity` (nullary / unary / binary / n-ary)
- `domain_sorts` (input types / sort tuple)
- `codomain_sort` (output type / sort)
- `axioms_or_attributes` (a flat property bag with named entries)
- `primary_category` (Mathlib class / Mathematica Head / Isabelle locale)
- `representation` (data-level: matrix, function, AST, vector)

### Divergence and which side substrate should take

- **Bundled (Lean/MathComp) vs unbundled (Mathematica/HOL plain class):** bundled gives compositional theorem reuse, unbundled gives easier ad-hoc tagging. Substrate-self-index pilot is closer to unbundled because we ingest existing math atoms post-hoc and want flat queries; reserve bundled-hierarchy for if/when we move to Level B (algebraic substrate-math with proof obligations).
- **Pattern-attributes (Mathematica Flat / Orderless / OneIdentity) as separable boolean flags vs single category membership:** Mathematica's separable flags are the right model for substrate, because a single op may simultaneously be Flat + Orderless + OneIdentity, and these flags drive different downstream rewrite rules. Adopt all three as named boolean attributes.

### What fields get used in QUERIES vs DECORATION (from lit + experience)

Query-load-bearing (the 7-8 fields that user queries actually filter on, observed across Mathlib `#find`, Mathematica `Information`, Isabelle `find_theorems`):

1. `arity`
2. `primary_category` (the 13-cat tag)
3. `commutative` (binary boolean)
4. `associative` (binary boolean)
5. `idempotent` (binary boolean)
6. `domain_sorts` (vector / scalar / discrete / continuous / probability / graph / dynamical-state)
7. `codomain_sort` (same enumeration)
8. `complexity_class` (constant / log / poly / NP-hard / EXP)

Decoration-only (the rest -- shown when inspecting an atom but rarely filtered on):

9. `identity_element` (string or symbol)
10. `inverse_element_or_op` (string or symbol)
11. `distributes_over` (list of other operator names)
12. `preserves` (list of named invariants: cosine_sim, norm, orthogonality, entropy)
13. `representation` (matrix / function / vector / AST / generator-set)
14. `references` (citations / mathlib paths / drill notes)

---

## Recommendation: substrate-self-index operator record schema

```yaml
# Schema for each substrate math atom (Level-A taxonomic, ~80 atoms target)
name: <unique short id, e.g. "fhrr_bind">
display_name: <human-readable, e.g. "FHRR binding (elementwise complex multiply)">
arity: <0 | 1 | 2 | n>            # universal-algebra signature
domain_sorts: [<sort>, ...]         # one per input position
codomain_sort: <sort>               # single sort
                                    # sort enum: phasor_vec | bipolar_vec | real_vec | complex_vec |
                                    #            scalar_real | scalar_complex | prob_dist | graph |
                                    #            permutation | dyn_state | shard_id | bundle
primary_category: <one of 13>       # monoid | group | abelian_group | semiring | tropical_semiring |
                                    # ring | field | vector_space | module | lattice |
                                    # similarity_space | probability_space | partial_order |
                                    # graph_category | operator_algebra | dynamical_system |
                                    # substrate_native
                                    # (collapse-merge to 13 by listing variants as the same primary)
commutative: <bool>
associative: <bool>
idempotent: <bool>
identity_element: <symbol or null>
inverse_element_or_op: <symbol or null>
distributes_over: [<other op names>]
preserves: [<invariant names>]      # e.g. cosine_sim, norm, orthogonality, total_prob, det
complexity_class: <O(1)|O(log N)|O(N)|O(N log N)|O(N^2)|O(N^3)|NP-hard|EXP>
representation: <matrix|elementwise|function|AST|generator_set|sampler>
references: [<mathlib-path>, <drill-note-path>, <wikipedia-or-arxiv-id>]
concept_links: [<PP row>, <drill name>, ...]   # back-edge to Corpus B (concept layer)
```

### Why this is the right surface area

- 14 fields exactly: matches the converged query-load-bearing 8 + decoration 6 partition.
- The substrate-novel field `concept_links` is the cross-corpus bridge from Corpus A (math) to Corpus B (concept) per the pilot design -- not in any formal system because they don't have a concept layer.
- `primary_category` is the 13-cat tag; `commutative/associative/idempotent` are the Mathematica-style separable attribute flags so an op like FHRR binding can carry (primary=abelian_group, commutative=true, associative=true, idempotent=false) all in one record.
- `domain_sorts` + `codomain_sort` adopt the universal-algebra signature framing (per UniMath survey + groupprops variety definition).
- No `proof_obligations` field: we are at Level A (taxonomic) not Level B (algebraic substrate-math); when/if Level B happens, add a `theorems_satisfied: [<lemma names>]` field then.

---

## (d) Cross-thread synthesis

- **vs substrate_v32_engineered_wrapper memory:** the engineered wrapper Sprint-4 sits at Level B (algebraic substrate-math); this drill's Level-A taxonomy is the prerequisite indexing layer so the wrapper's primitives can be queried structurally ("all operators that preserve orthogonality under bundling" returns the safe set).
- **vs substrate_classical_NLP memory (POS 0.906, slot 0.871, intent 0.834):** the count-NB + HMM-Viterbi + context-window-emission ops that beat phasor on NL all sit in category 3 (semiring / tropical-semiring) -- this confirms the semiring category is load-bearing for substrate-NL, not just a theoretical placeholder.
- **vs drill_pattern_temporal_contextual memory:** the empirically-VALIDATED drill pattern is TEMPORAL+CONTEXTUAL; categories 12 (dynamical-system, time axis) and 13 (substrate-native with context-binding) are the two categories most aligned with that pattern. Categories 9-11 (poset / graph / operator-algebra) are the FIXED-ARCHITECTURE side and should carry deflated P_deflated when proposing new atoms in those buckets.
- **vs slipnet_polysemic memory (WN18RR 20.2x chance refutes "clean ceiling"):** the slipnet relation-types are graph_category ops with morphism-composition semantics; tagging them in the new schema as (primary=graph_category, preserves=[relation_type, semantic_locality]) makes the ceiling-discriminator explicit and queryable.
- **vs research_field_advisor top-5:** none of the top-5 candidates (free-cumulants, Glauber, M-H, FFS, Wigner-edge) is closed by this drill; this is an indexing-infrastructure drill, not a fruit-bearing-field drill. It enables more efficient subsequent drills by making operator-overlap queryable.

---

## (e) Substrate-product implications

- **Self-index pilot can ingest 80-100 atoms in ~30 mins manual tagging** using the 14-field schema -- this is the LOAD-BEARING piece for the pilot timeline (2-3 days laptop CPU).
- **Cross-corpus bridge (concept_links field) is the differentiator** vs Mathematica / Lean / Coq / Isabelle: none of them link math atoms back to capability claims and drill outcomes. This is the substrate-product moat.
- **Query mechanism MVP:** pandas filter expressions over the YAML/JSON dump for the 8 query-load-bearing fields. No graph database required at Level A.
- **Calibration risk:** the substrate_native (category 13) bucket may absorb too many atoms if we tag conservatively. Mitigation: require that any atom tagged substrate_native be additionally tagged with the best-approximating classical category in a secondary `nearest_classical_category` field. This forces explicit articulation of WHICH classical structure the substrate-native op deviates from.

---

## (f) Citations (verified count: 12 sources)

Drill 1 (taxonomy):
1. "Tropical semiring" -- nLab, https://ncatlab.org/nlab/show/tropical+semiring (idempotent semiring axioms, max-plus = max-min isomorphism, parallel running theories)
2. "Outline of algebraic structures" -- Wikipedia (semigroup-monoid-group ladder, lattice via absorption law, ringoid via distributivity)
3. "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I" -- ACM Computing Surveys, https://dl.acm.org/doi/10.1145/3538531 (binding + superposition + permutation as three distinct algebraic operation classes; approximate orthogonality joint axiom)
4. "On the classification problem for C*-algebras" -- arXiv 1002.4711 (factor types I, II_1, II_inf, III; projection-based classification)
5. "Variety of algebras" -- Groupprops subwiki (universal-algebra signature = set of operator symbols + arity function)
6. "Universal Algebra" -- MathWorld, https://mathworld.wolfram.com/UniversalAlgebra.html (multi-sorted signature with domain/codomain functions)

Drill 2 (formal-systems):
7. "Mathlib.Algebra.Group.Defs" -- Lean Mathlib4 docs (Semigroup -> Monoid -> Group -> Ring -> Field hierarchy; bundled inheritance; diamond ancestor pattern)
8. "Use and abuse of instance parameters in the Lean mathematical library" -- arXiv 2202.01629 (bundled vs unbundled trade-offs)
9. "Attributes" guide -- Wolfram Language Documentation, https://reference.wolfram.com/language/guide/Attributes.html (Flat = associative, Orderless = commutative, OneIdentity = identity-pattern equivalence)
10. "Typeclasses and Canonical Structures" -- Coq wiki + Garillot PhD thesis (canonical structures key on terms not types; MathComp ringType extends zmodType bundled)
11. "Reasoning about Algebraic Structures with Implicit Carriers in Isabelle/HOL" -- Guttmann, https://www.csse.canterbury.ac.nz/walter.guttmann/publications/0063.pdf (locales support multiple type parameters; carrier-set per locale)
12. "Magma Computational Algebra System I: The User Language" -- Bosma/Cannon/Playoust, JSC 1997 (variety = common operator set + common axioms; category = variety + common representation)

---

## P_deflated estimate

For "the 13-category taxonomy + 14-field schema works for >= 18/20 hand-tagged substrate atoms":

- Raw lit-scan agent estimate (4 systems converge on near-identical record schema): P_raw ~ 0.78
- Calibration penalty (substrate atoms include substrate-native category 13 that has NO direct precedent): -0.20
- Substrate-novel synthesis cap: 0.50
- **P_deflated = min(0.78 - 0.20, 0.50) = 0.50**

The 0.50 ceiling acknowledges this is novel-synthesis: no published formal system has needed a category like "substrate_native" because none of them grapple with approximate-orthogonality joint axioms. The HARD-PASS cheap test (~30 min effort) is the empirical decider.

## Next-drill candidate (deferred)

`free-probability F4 (Voiculescu free cumulants kappa_n)` -- top-ranked by field advisor (score 5.5), Tier-1 fruit-bearing field, gives substrate-novel observability beyond mean+variance for P(h) histogram. Not closed here; this drill was indexing-infrastructure not capacity-bound.
