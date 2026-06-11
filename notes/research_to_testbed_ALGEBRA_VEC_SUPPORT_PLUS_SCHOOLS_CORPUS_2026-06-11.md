# Research -> Testbed: algebra-vec Q1-Q6 research support + schools-of-thought corpus proposal

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL + user direction "represent schools of thought too"

## Endorsing schema extension

YES. Algebraic-vec extension is correct architectural direction. User's intuition matches HRR/VSA literature: math-as-descriptions encoding loses algebraic structure that LLM-embedding cannot recover. Substrate's commercial differentiation lives in algebra-vec, not semantic-vec.

Implementing the schema extension while I research is right call. Re-encode cost is cheap.

## Q1-Q6 research support (initial answers; 2x drill dispatched for deeper synthesis)

### Q1: Algebra taxonomy (10-15 categories)

**Recommended baseline (10 categories; covers substrate primitives):**
1. **group** (FHRR binding, role-filler binding, bipolar binding -- with inverse + identity)
2. **monoid** (bundling, cleanup-cascade -- no inverse)
3. **ring** (with addition + multiplication; algebraic structures)
4. **field** (R, C, GF(2) base sets)
5. **vector_space** (substrate vectors themselves)
6. **semiring** (max-plus tropical / probability semirings for Viterbi-like DP)
7. **category** (compositional with type constraints; substrate atoms as morphisms)
8. **lattice** (cleanup as join/meet over codebook)
9. **metric_space** (cleanup-distance + Hamming + cosine)
10. **partial_order** (substrate Tier hierarchy; specialization)

Expand to 12-15 only if drill returns lit-strong cases. 2x drill on algebra taxonomy + formal math systems prior art DISPATCHED (lands ~4 min).

### Q2: Domain encoding

Use TYPED STRING ENUM (forward-compatible):
- `"R"`, `"R+"`, `"C"`, `"C^*"` (unit-modulus complex), `"GF(2)"`, `"GF(p)"`, `"bipolar"`, `"phasor"`, `"probability_simplex"`, `"discrete_finite"`, `"discrete_combinatorial"`, `"spike_train"`, `"natural_numbers"`, `"unit_circle"`

Plus shape qualifier: `"R^N"`, `"C^N"`, `"R^{N x N}"` etc. for substrate vector/matrix types.

Simple type-tag string; substrate cleanup over domain tags gives structural retrieval.

### Q3: Signature encoding DSL

Recommend **structured JSON** (NOT Hindley-Milner -- overkill for substrate atoms and would balloon Atom size):

```json
"signature": {
  "input_arity": 2,
  "input_types": ["vec[N,phasor]", "vec[N,phasor]"],
  "output_type": "vec[N,phasor]",
  "preserves": {
    "dim": true,
    "norm": false,
    "unit_modulus": true,
    "associativity_input_order": true
  }
}
```

`input_types` as DSL strings parseable by substrate but human-readable. Compose substrate cleanup over types AND preserves to discover "operations sharing signature".

### Q4: Cross-domain equivalence catalog

2x drill on cross-domain equivalences catalog DISPATCHED (lands ~4 min). Will return ~30-50 equivalences organized by domain pair (FHRR <-> HRR via FFT, HMM Viterbi <-> Chu-Liu-Edmonds via DP-extension, etc.) with under_transformation and fidelity fields.

For now, ship batch 02 with these initial equivalences I know off-hand:
- T2/fhrr_bind EQUIVALENT_UNDER FFT T2/circular_convolution (exact)
- T3/forward_algorithm EQUIVALENT_UNDER time_reversal T3/backward_algorithm (exact)
- T3/hungarian_assignment EQUIVALENT_UNDER min_cost_flow_relaxation T1/convex_optimization (LP relaxation; exact when integer)
- T3/viterbi_decoding EQUIVALENT_UNDER sum_to_max_semiring T3/forward_algorithm (semiring shift; exact)
- T2/pca_whitening EQUIVALENT_UNDER rotation T2/zca_whitening (orthogonal transformation; exact)
- T3/em_algorithm EQUIVALENT_UNDER coord_descent T1/convex_optimization (specific form; approximate)

Drill will return more. Tag fidelity as exact / approximate / probabilistic.

### Q5: Prior art (Mathematica / Lean 4 / Coq / Magma)

2x drill on formal math systems DISPATCHED (combined with algebra taxonomy). Initial answers from familiarity:

- **Mathematica**: Head[expr] is the operator class; Attributes are HoldFirst/Listable/Orderless/Flat/OneIdentity for evaluation behavior; structural tagging is unstructured but rich
- **Lean 4 Mathlib**: type-class hierarchy (Group/Ring/Field/...) is rigorously typed; algebraic_structure morphisms first-class
- **Coq**: typeclasses + canonical structures + setoid_rewrite for ring/field tactics
- **Magma**: function attributes (Symmetric/Antisymmetric/Bilinear) + structure typing

**Lesson for substrate**: Lean's type-class hierarchy is most directly transferable. Structure tags as a partial order (group < ring < field) means substrate can retrieve "atoms in this algebra OR a richer extension" via tag-vector hierarchy.

### Q6: Validation plan

Endorsing your test set:
1. Inject FFT-dual + verify cross_domain_equivalences() surfaces it
2. Cluster T3 atoms by algebra_vec; check matches expert intuition
3. Run Q5 disclosed query on composite-vec vs semantic-only; substrate should beat by margin

ADD: Run Tracy-Widom / spectral observability (free-prob ~30-line primitive routed separately) on the composite-vec eigenvalue spectrum vs semantic-only spectrum. The composite spectrum should show different statistics if algebra-vec carries genuine structure.

## Schools-of-thought corpus proposal (per user direction)

User asked: "does testbed also have a representation of the different schools of thought that have contributed most significantly to our mathematical basis successfully? it might go hand in hand with the math representations but we'll want to use that information to dig into those and related fields"

YES this is the right extension. Proposing third corpus partition.

### Corpus C: SCHOOL

Atom kind: `school` (new AtomKind enum value)

Fields specific to school atoms:
- `school_name` (e.g., "VSA / HDC / FHRR lineage")
- `key_contributors` (list of names)
- `peak_period` (string; e.g., "1990s-2010s")
- `current_status` (active / quiet / dormant)
- `productivity_score` (0-1 normalized; how many substrate primitives trace to this school)
- `related_unexplored_fields` (list)
- `core_methods` (list of math atom ids)

Example:
```json
{
  "id": "school::VSA_FHRR_lineage",
  "name": "VSA / HDC / FHRR lineage",
  "corpus": "school",
  "tier": "T1",
  "kind": "school",
  "key_contributors": ["Tony Plate", "Pentti Kanerva", "Chris Eliasmith", "E. Paxon Frady"],
  "peak_period": "1990s-2020s active",
  "current_status": "active",
  "productivity_score": 0.95,
  "core_methods": ["math::T2/fhrr_bind", "math::T2/fhrr_unbind", "math::T2/cleanup", "math::T2/bundling", "math::T2/circular_convolution"],
  "related_unexplored_fields": ["operator-valued free probability", "resonator-network factoring at scale", "neuromorphic substrate implementation"]
}
```

### Cross-corpus relation type

Add `CONTRIBUTES_TO` (school -> math) and inverse `TRACES_TO` (math -> school).
Add `INFLUENCED_BY` (school -> school).

### Strategic value

The school corpus enables:
1. Tracing which schools contribute most to substrate capabilities (where to invest research focus)
2. Surfacing related schools/fields un-tapped (where to drill next)
3. Connecting math operations to their conceptual origins (provenance for product claims)
4. Reviving dormant schools whose intuitions might inform substrate
5. Substrate-self-index discovers cross-school structural similarities

### Schools to populate (initial ~30; 2x drill DISPATCHED for full ~50 catalog)

I'll deliver schools corpus JSONL Day 2 alongside concept corpus. Initial set:
- VSA/HDC/FHRR (Plate, Kanerva, Eliasmith)
- Cognitive architecture (Newell-Simon SOAR + Anderson ACT-R)
- Cognitive science analogy (Hofstadter slipnet + Gentner SME + Hummel-Holyoak LISA)
- Discrete optimization (Kuhn + Hungarian; Dijkstra; A*; Chu-Liu-Edmonds)
- HMM / Sequence (Baum-Welch + Viterbi + Rabiner)
- Information theory (Shannon + KL + Csiszar)
- Free probability / RMT (Voiculescu + Wigner + Tracy-Widom + Marchenko-Pastur)
- Probabilistic graphical models (Pearl + Lauritzen-Spiegelhalter)
- Structured prediction (Lafferty CRF + Tsochantaridis SSVM + Collins perceptron + LeCun EBM)
- Conformal prediction (Vovk + Shafer)
- Categorical AI (MacLane + Lambek-Coecke + Spivak)
- Compositional generalization (Lake + Baroni)
- KR (Sowa CG + Brachman DL + OWL/RDF)
- KGE (Bordes TransE + Lin + Trouillon ComplEx)
- Statistical NLP (Collins + McCallum + Manning)
- Neural-symbolic (Garcez + Lamb + Marcus)
- Bayesian non-parametrics (Ferguson + Teh + Blei)
- Causal inference (Pearl + Imbens-Rubin)
- Spectral graph theory (Chung + Spielman-Teng)
- Random graphs (Erdos-Renyi + Chung-Lu + Newman)
- Active inference (Friston FEP)
- Predictive coding (Rao-Ballard)
- Reservoir computing (Maass + Jaeger)
- Compressed sensing (Donoho + Candes)
- Variational methods (Jordan + Wainwright)
- Operator algebras (Murray-von Neumann; subfactor theory)
- Coding theory (Shannon + Reed-Solomon + LDPC)
- Optimization theory (Nesterov + Boyd)
- Hopfield / dense Hopfield (Hopfield + Ramsauer)

## What I'll ship

- Batch 02 tomorrow Day 1 EOB: math relations + 6 description refinements + 5 disclosed queries + 27-tag 5-super-group + substrate-CRF + conformal atoms + bundling/superposition sharpened + initial cross-domain equivalences + algebra-vec fields populated on the 60 batch-01 atoms (re-encode pass)
- Batch 03 Day 2: full sub-op decomposition + concept corpus + schools corpus initial ~30 atoms + cross-corpus relations
- 7 background drills landing tonight/tomorrow morning will inform refinements

## Drills dispatched in support

1. Algebra taxonomy + formal math systems prior art (Q1+Q5) -- ~4 min
2. Schools-of-thought lineage (~30-50 schools) -- ~5 min
3. Cross-domain equivalences catalog (~30-50 equivalences) (Q4) -- ~4 min
4. Substrate-only NL synthesis path -- ~4 min
5. Substrate continual-learning + RAG-backend -- ~5 min
6. RMT-beyond-free-probability -- ~4 min
7. Substrate vs larger LLM methodology -- ~4 min

Will refine batch 02 + 03 with drill findings.

## Cross-references
- Your proposal: notes/testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md
- Findings 01: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Findings 02: notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md

---

**Testbed:** Q1-Q6 endorsed with initial answers + 2x drills dispatched for refinement (lands ~4-5 min each). Schools-of-thought corpus proposal (new partition with CONTRIBUTES_TO + INFLUENCED_BY + TRACES_TO relations) per user direction. Implementing schema extension is right; will re-encode after drill refinements land. Batch 02 + 03 timeline holds.
