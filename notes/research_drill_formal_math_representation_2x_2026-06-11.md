# Research Drill 2x DEEP -- Formal Mathematical-Knowledge Representation Systems

date: 2026-06-11
topic: how mature systems encode mathematical RELATIONS (not just facts), and what scales / fails
model: opus 4.7 synthesizer over 12 Sonnet-grade WebSearches
calibration: lit-scan penalty applied; novel-synthesis P capped at 0.50

---

## HEADLINE

Every successful formal-math representation system (Mathlib, Metamath, Isabelle, OEIS, TPTP, DisCoCat) encodes relations in ONE OF TWO WAYS: (a) typed inheritance graph (Mathlib `extends`, Isabelle `sublocale`, Bourbaki mother structures) -- a strict DAG of "X is-a Y" / "X extends Y" with axiom inheritance, OR (b) dependency-edge graph (Metamath axiom DAG, Mathlib import DAG, OEIS crossrefs) -- "theorem T uses lemma L" / "sequence A references sequence B". Genuine NEW mathematical relations have been surfaced empirically by OEIS crossrefs ("order-of-magnitude increase in combinatorics discoveries") and Ramanujan Machine (75 previously unknown constant-relations via integer-relation hypergraph). NO system at scale has demonstrated discovery via category-theoretic functorial unification -- DisCoCat etc. are descriptive frameworks, not discovery engines. For a substrate with ~80-100 math atoms, the empirically validated design is: (1) typed atoms with explicit inheritance edges (NOT just similarity), (2) a separate USES/COMPOSES dependency DAG, (3) lightweight categorical decorations (functor-tag pairs) for cross-cutting unifications but DO NOT treat category theory as the primary indexing axis -- it has not scaled as a discovery primitive in any system reviewed.

P_deflated (substrate-style relation-graph surfaces genuine cross-domain unifications) = 0.42
P_deflated (category-theory tagging adds discovery beyond inheritance + USES edges) = 0.22
P_deflated (~80-100 atoms is too coarse a granularity -- needs sub-atom decomposition for retrieval) = 0.55

---

## Cheap decisive test

Build a 30-atom prototype taxonomy with TWO relation channels: (i) typed inheritance (atom IS-A structural-family); (ii) USES/COMPOSES edges (operation X internally invokes operation Y). For each atom, store: name, signature (input/output types as substrate role-bound bundles), 2-3 known structural-family tags (e.g. "linear map", "bipartite-matching", "MAP-inference"). Run 5 retrieval queries that should surface KNOWN cross-domain unifications:
1. "What operations are dual to PCA?" (expect: CCA, ICA, LDA via "decorrelating linear projection" family)
2. "What operations compose to give Hungarian assignment?" (expect: bipartite-graph + min-cost-flow + LP-relaxation)
3. "What is the Viterbi-equivalent for non-HMM models?" (expect: max-product BP / Bellman-Ford / dynamic-programming-on-DAG)
4. "What operations are special cases of EM?" (expect: K-means, GMM, Baum-Welch, NMF)
5. "What operations preserve angles up to rotation?" (expect: orthogonal projection, rotation matrices, unitary maps, FHRR binding)

HARD-PASS: 4/5 queries surface the correct family WITHOUT requiring the family-tag to have been pre-written for that specific query (i.e. the inheritance DAG generalizes).
HARD-FAIL: <=2/5 queries surface the family; substrate cosine-on-bundle gives noise; need category-theoretic tagging on top.
MIDDLE: 3/5 -- relation-graph works but needs richer USES edges.

Cost: 1-2 days CPU + manual schema entry; no new training.

---

## Falsifiable predictions

### HARD-PASS thresholds
- 4/5 cross-domain unification queries surface correct family via 2-channel relation graph alone (inheritance + USES).
- Sub-atom decomposition (e.g. "Hungarian = bipartite-graph-construct + min-cost-flow + integer-extract") improves retrieval recall by >= 20% vs monolithic-atom encoding.
- Adding category-theoretic functor tags improves recall by < 5% over (inheritance + USES + family-tag) -- predicting category theory is NOT load-bearing for the substrate's discovery axis.

### HARD-FAIL thresholds
- <=2/5 queries succeed -- inheritance + USES are not sufficient; need richer relation types (DUAL, APPROXIMATES, OPTIMIZES as first-class edges) per OntoMath_PRO precedent.
- Sub-atom decomposition gives < 5% lift -- atoms are at the right granularity, problem is elsewhere (likely embedding quality / cleanup margin).
- ~80-100 atoms is fundamentally insufficient -- Mathlib has ~150k declarations, OEIS has 390k sequences, Metamath has 44k theorems; substrate at 100 atoms is at the "Bourbaki mother-structures" granularity which is too coarse for most retrieval queries.

### MIDDLE-band (most-likely outcome per lit-scan calibration)
3/5 surfacing, sub-atom helps modestly (10-15%), category tags help on niche queries (the 1-2 questions where DUAL is the right edge). Implies: ship 2-channel graph + sub-atom decomposition + selective category tags as decorations, NOT as the primary axis.

---

## Cross-thread synthesis with prior entries

### Convergent finding 1: Two-channel encoding (typed-inheritance + dependency-uses) is empirically the load-bearing pattern

ALL six mature systems converge on this:
- **Mathlib**: bundled structures with `extends` for inheritance (e.g. `comm_ring extends ring`) + import DAG for USES. Caveats: "competing inheritance paths in dependent type theory" is a known pain point (PMC article on functional analysis case study); the design choice to use `extends` rather than mixins was made specifically to avoid term blow-up.
- **Isabelle/HOL**: `locale` for parameterized specs + `sublocale` for is-a relations + import graph. Type-classes and locales were unified by Haftmann-Wenzel into a single relational substrate. `class_deps` graph visualization is the canonical relation surface.
- **Metamath set.mm**: explicit axiom-dependency DAG; every theorem proven only via axioms or prior theorems; 28,366 theorems with 12,151 used in major-compilation core. Pure USES-graph encoding.
- **Bourbaki**: three "mother structures" (algebraic / order / topological) + "multiple structures" combining them + "particular theories" at top. Strict hierarchical DAG; criteria = simplicity, generality, axiom count.
- **OEIS**: cross-references as the primary discovery surface; 390k sequences; single number 1729 belongs to 350+ sequences; cross-refs drove "order of magnitude" increase in combinatorics discovery rate.
- **TPTP**: problems indexed by syntactic features (formula count, operator types, quantifier depth, equality usage) -- a FEATURE GRAPH not a relation graph, used for selecting which prover handles which problem class.

Maps directly to substrate v3.2 ENGINEERED WRAPPER (per [[substrate_v32_engineered_wrapper_2026-06-11]]): the inheritance channel rides on per-tier importance / hierarchy; USES channel rides on stored-bundle cross-binding. Both already implementable as substrate primitives. The two-channel pattern is NOT a substrate-novel proposal; it is the lit-validated baseline.

### Convergent finding 2: Category-theoretic unification has scaled DESCRIPTIVELY, NOT as a discovery engine

DisCoCat (Coecke-Sadrzadeh-Clark 2010) is the most-cited applied-category-theory framework -- it formalizes that compositional-distributional semantics is a strong monoidal functor from a pregroup grammar to FinVect. Categorica (Wolfram 2024) builds applied category theory tooling in Wolfram Language. Applied Category Theory community (Baez, Spivak, Fong) has produced rich theory for chemistry, network theory, databases, control theory.

But: NONE of these have produced empirical new mathematical discoveries traceable to their categorical structure. The closest is the n-Lab / nLab encyclopedia which is descriptive (an "everything is a functor" tagging system) but does not surface new conjectures. Per [[research_principles_biology_materials_new_math_2026-06-10]]'s third principle (don't be afraid to invent new math), this opens an OPPORTUNITY but NOT a precedent.

Implication: do not bet the substrate's discovery axis on functor-tagging. Use it as decoration / sparse extra edges. Primary edges are inheritance + USES.

### Convergent finding 3: Granularity is empirically variable and depends on retrieval task

- Bourbaki: 3 mother structures + ~12 "multiple structures" -- extreme top-down, useful for textbooks, useless for retrieval at depth.
- Metamath: 44k theorems but each is essentially atomic (one substitution rule + dependencies). Granularity = "smallest verifiable step." This is THE finest reasonable level for axiomatic math.
- Mathlib: ~150k declarations spanning bundled structures + tactic-lemmas + computation rules. Mid-grain.
- OEIS: 390k sequences, each "one mathematical object" -- but sequences naturally decompose (A001 = 1,1,2,3,5,8,... is "Fibonacci" but ALSO "tilings of 2xn", "subsets without consecutive ints", etc. -- multi-tagged).
- TPTP: ~26k problems classified by SYNTACTIC features not semantic ones.
- OntoMath_PRO: 3 levels (basic metamath / field-specific / scientific-common) -- mid-grain with explicit level partition.

For substrate with 80-100 atoms: this is BOURBAKI-LEVEL granularity. Lit precedent says this is too coarse for serious retrieval at the level of "find me the operations dual to PCA". Sub-atom decomposition (e.g. each atom -> 3-5 sub-operations + glue) is empirically required.

This contradicts our initial framing: 80-100 atoms is NOT "rich taxonomy", it is "mother-structures level". The empirically-validated substrate target should be 300-500 sub-atom operations bundled into 80-100 named atoms. Per [[feedback-dont-parrot-drill-defeatism-2026-06-11]] this is not a defeatism claim but a granularity recalibration informed by 5 mature precedents.

### Convergent finding 4: Genuine discovery via relation graphs has happened -- in narrow domains, with specific edge types

EMPIRICAL discovery wins:
- **OEIS crossrefs**: order-of-magnitude lift in combinatorics-discovery rate. Edge type = "this sequence appears in the definition / theorem of that sequence." Cheap, high-recall, surfaced 350+ different facts about the number 1729.
- **Ramanujan Machine** (Raayoni et al., Nature 2021; Ramanujan Library 2024): 75 previously unknown formulas for fundamental constants discovered via hypergraph + PSLQ integer-relation algorithm. Edge type = "constant C participates in continued-fraction representation F."
- **AlphaTensor** (Fawzi et al. 2022): faster matrix-multiplication algorithms via RL over tensor-decomposition game. NOT a relation-graph discovery -- a search-game discovery. But the underlying representation IS a tensor (algebraic structure with implicit symmetry relations).
- **AlphaEvolve** (DeepMind 2025): matched state-of-the-art on ~75% of 50 open problems in analysis/geometry/combinatorics/number-theory. LLM + evolutionary search; relation graph is implicit in LLM training, not a curated structure.
- **AlphaGeometry** (Trinh et al. 2024): IMO-level geometry. LLM-as-hypothesizer + symbolic deduction engine. Hybrid; the relation graph is the symbolic deduction DB.

Pattern: discovery via curated relation graphs HAS happened (OEIS, Ramanujan) but in domains where edges are extremely specific (numerical-equality, sequence-membership). For abstract operation relations (DUAL, COMPOSES, APPROXIMATES), no system has empirically demonstrated discovery -- only retrieval / classification.

This is a strong calibration signal: the substrate proposal "surface structural unifications via retrieval" is FEASIBLE for retrieval, NOT YET demonstrated for discovery of novel unifications.

### Convergent finding 5: Symbolic brittleness is the universal failure mode

The lit (Welleck et al. 2021 "Symbolic Brittleness in Sequence Models") + general symbolic-AI critique converge: symbolic representations fail catastrophically on small perturbations, struggle to compose known solutions across distribution gaps, and require ever-more-rules to handle exceptions. Mathlib's porting experience (Lean 3 -> Lean 4, 2-year community effort) is concrete: 150k declarations could not be auto-translated; tactics required manual reimplementation; "an import which seemed sufficiently well ported in fact isn't" is the dominant failure mode.

For substrate: this directly maps to [[substrate_classical_NLP_methods_outperform_phasor_2026-06-11]] -- count-based statistical methods stored as substrate bundles beat phasor-only matching on real NL tasks. The lesson generalizes: store relation patterns as STATISTICAL bundles (with cleanup-margin / multi-candidate / soft match) not as rigid symbolic edges. The substrate's algebraic / continuous nature is an asset against brittleness PROVIDED edges are stored as soft / weighted / multi-instance.

---

## Substrate-product implications

### Immediate design lessons (1-2 week implementation)

1. **Two-channel relation graph as primary axis.** Inheritance DAG (`atom IS-A family`) + USES DAG (`atom_X invokes atom_Y in its expansion`). Both as stored substrate bundles with named role-fillers. This is mature-system-validated; no novel math required.

2. **Sub-atom decomposition is empirically required.** 80-100 atoms is mother-structures granularity. Target 300-500 sub-operations grouped into 80-100 named atoms. Each atom stores its decomposition as a bundle of sub-ops + glue. Maps to Tier-2 schema design (per [[research_drill_tier2_problem_schemas_2x_2026-06-11]]) -- the same multi-level encoding that worked there.

3. **Family-tag enumeration before category-theoretic tagging.** Build 20-30 "structural families" first: "linear projection family", "bipartite-matching family", "MAP-inference family", "EM-family", "max-product BP family", "dynamic-programming-on-DAG family", "convex-optimization family", etc. Each atom multi-tagged. THIS is the load-bearing relation axis per OEIS precedent. Category-theoretic functor tags as later decoration if helpful.

4. **Soft / weighted edges (not rigid).** Per symbolic-brittleness lit: store edges as bundles with cleanup-margin / multi-candidate fallback. Substrate's continuous nature is the natural defense; rigid IS-A is a regression to symbolic AI failure mode.

5. **Pre-register the granularity question as an empirical test.** Compare 100-atom vs 300-atom vs 500-atom on the 5 cross-domain queries. If 100 atoms hits the 4/5 HARD-PASS, ship. If only 300-500 hits HARD-PASS, that is data + a substrate-novel scaling claim.

### Strategic implication: discovery vs retrieval

The user-stated goal ("surface structural unifications via retrieval") splits into two product modes:
- **Retrieval-mode (FEASIBLE, lit-validated)**: given query Q, return atoms / families likely relevant. OEIS / Mathlib search / Isabelle Sledgehammer / Metamath proof-search all do this; substrate can compete.
- **Discovery-mode (HARDER, not yet demonstrated by any system using relation graphs alone)**: given partial pattern P, conjecture a new cross-domain unification. OEIS achieved this only via numerical-equality edges; Ramanujan via integer-relation algorithm. Both required a DOMAIN-SPECIFIC edge type. For substrate, the equivalent would be: an edge type tied to "operations producing same output distribution on input distribution X" -- empirical equivalence rather than structural-isomorphism. This is a specific actionable research direction with substrate-product value.

### Strategic implication: relation between this and Phase 3 reasoning routing

Per [[research_drill_reasoning_composition_routing_2x_2026-06-11]] Phase 3 used 6 problem classes mapped to substrate primitives. The math-relation graph proposed here is the SUBSTRATE for that routing: when slot-filled schema instance arrives, the router looks up "what atom-family is this instance asking for" via the inheritance DAG, then dispatches to the correct atom. The two-channel relation graph is a precondition for Phase 3 to work at scale.

---

## Citations (verified count: 14 + cross-references)

- The Lean Mathematical Library (mathlib paper, arXiv 1910.09336)
- Mathlib hierarchy_design docs (leanprover-community)
- Use and Abuse of Instance Parameters (J. Automated Reasoning 2024, Springer link)
- Competing Inheritance Paths in DTT (PMC 7324078, functional analysis case study)
- Growing Mathlib: maintenance (arXiv 2508.21593v2)
- Isabelle Typeclass_Hierarchy documentation (isabelle.in.tum.de)
- Type classes versus locales (Paulson, Machine Logic 2022)
- From LCF to Isabelle/HOL (arXiv 1907.02836)
- Metamath set.mm GitHub + Metamath Wikipedia
- Mathematical Knowledge Bases as Grammar-Compressed Proof Terms (arXiv 2505.12305)
- Generating Theorems by Generating Proof Structures (arXiv 2602.15511)
- Premise Selection by Deep Graph Embedding (Wang et al., arXiv 1709.09994)
- A Survey on Deep Learning for Theorem Proving (arXiv 2404.09939)
- REAL-Prover: Retrieval Augmented Lean Prover (arXiv 2505.20613)
- HolStep + Improving GNN Representations of Logical Formulae (arXiv 1911.06904)
- TPTP problem library + Characteristic Subsets of TPTP (Chvalovsky-Jakubuv, AITP 2021)
- DisCoCat / categorical compositional distributional semantics (nLab, Coecke-Sadrzadeh-Clark 2010 + Categorica arXiv 2403.16269)
- Applied Category Theory (Baez-Coecke eds., arXiv 1411.3827)
- OEIS overview + Sloane's Gap (arXiv 1101.4470) + arXiv 1805.10343
- Ramanujan Machine (Raayoni et al., arXiv 1907.00205) + Ramanujan Library (arXiv 2412.12361)
- AlphaTensor (Fawzi et al., Nature 2022, PMC 9534758)
- Bourbaki structure: Corry (TAU publications) + Marquis (philarchive) + Bell (UWO) + arXiv 1812.03867
- OntoMath_PRO ontology (arXiv 1407.4833)
- Symbolic Brittleness in Sequence Models (Welleck et al., arXiv 2109.13986)
- HDC/VSA Surveys Parts I & II (Kleyko et al., ACM Computing Surveys, arXiv 2111.06077 + 2106.05268)
- Boxology of Design Patterns for Hybrid Learning (arXiv 1905.12389)

---

## Pre-registered NEXT drill candidate

If 5-query test result lands in MIDDLE band (3/5), drill next:
- **Family-tag inventory expansion**: literature on "operator algebras of computational primitives" + "design pattern catalogs for algorithmic primitives" + Boxology (arXiv 1905.12389) -- to systematically enumerate the 20-30 family tags rather than pick them ad-hoc. Score 4.5 (tier-2 adjacent), ~1 day theory + 2 hr smoke.

If 5-query test result is HARD-FAIL (<=2/5):
- **Sub-atom decomposition study**: precedent from category theory's "string diagram" representations + Mathlib lemma-decomposition + Metamath proof-term grammar compression (arXiv 2505.12305). Score 5.0 (tier-1 by anchor).
