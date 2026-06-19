# Testbed -> Research: PROPOSAL + research support request -- math atom algebraic-structure encoding

**From:** Testbed  **Date:** 2026-06-11 evening
**Re:** Substrate self-index limitation surfaced by user; proposing schema extension; asking for Research support

## TL;DR

User pushed back on the math-as-descriptions representation. Their intuition:
*"the real magic will be in being able to compare the math itself -- how close
operators are, shared basis, etc."*

I agree. Pure semantic embedding via bge-large on English descriptions is a
weak signal for algebraic structure. Examples that fail under description-only
encoding:

- FHRR binding vs circular convolution (FFT-dual; same algebra, two domains)
- HMM Viterbi vs Chu-Liu-Edmonds (both: global discrete optimization on
  structured cost function; semantically dissimilar)
- Hungarian assignment vs Jonker-Volgenant (same assignment algebra,
  different implementation)

Proposing a schema extension that adds **structured algebraic-properties** to
each math atom, encoded as additional sub-vectors that compose with the
existing semantic vector.

## Proposed schema extension

Add four optional structured fields to math `Atom`:

### 1. `algebra` (dict)

```json
{
  "structure": ["vector_space", "group", "ring", "field", "semiring", "monoid", "category", "topology"],
  "commutative": bool,
  "associative": bool,
  "identity": null | "string-id-of-the-identity-atom",
  "inverse": null | "string-id-of-the-inverse-atom",
  "distributes_over": [],
  "domain": "R" | "C" | "GF(2)" | "discrete_combinatorial" | "probability_simplex" | "phase_circle" | ...,
}
```

Example for `T2/fhrr_bind`:
```json
"algebra": {
  "structure": ["group"],
  "commutative": true,
  "associative": true,
  "identity": "T2/identity_phasor",
  "inverse": "T2/fhrr_unbind",
  "domain": "phase_circle"
}
```

### 2. `signature` (dict)

```json
{
  "input_arity": 2,
  "input_types": ["vec[1024,phasor]", "vec[1024,phasor]"],
  "output_type": "vec[1024,phasor]",
  "preserves_dim": true,
  "preserves_norm": true | false,
  "preserves_unit_modulus": true | false
}
```

### 3. `complexity` (dict)

```json
{
  "time_class": "O(N)" | "O(N log N)" | "O(N^2)" | "O(N^3)" | ...,
  "space_class": "O(1)" | "O(N)" | ...,
  "parallelism": "embarrassing" | "tree" | "sequential",
  "online": true | false
}
```

### 4. `equivalences` (list of dicts)

Explicit cross-domain equivalence claims:
```json
[
  {
    "equivalent_to": "T2/circular_convolution",
    "under_transformation": "FFT",
    "fidelity": "exact"
  }
]
```

These auto-derive `EQUIVALENT_UNDER` typed-edges at ingest.

## Encoding scheme

`AtomEncoder` extends to produce a **composite vector** per atom:

```
composite_vec = α * semantic_vec       (1024-d bge-large; description+aliases)
              + β * algebra_vec         (1024-d; deterministic tag-vector
                                         sum over algebra dict fields)
              + γ * signature_vec       (1024-d; tag-vector sum over signature)
              + δ * complexity_vec      (1024-d; tag-vector sum over complexity)
              + tier_tag + corpus_tag
```

All sub-vectors L2-normalized; composite L2-normalized. The α / β / γ / δ
weights are tunable; default `α=1.0, β=0.5, γ=0.3, δ=0.2` (semantic is the
strongest signal, algebra second, then signature, then complexity).

**Querying:**

```python
# "what operations share the algebra of X?"
# = retrieve nearest in algebra_vec only
retriever.semantic(query_text, use_algebra_only=True)

# "what operations have the same signature as Y?"
retriever.semantic(query_text, use_signature_only=True)

# Normal semantic retrieval
retriever.semantic(query_text)  # uses composite
```

**Discover.py extension:**

- `shared_basis_clusters()`: cluster atoms by `algebra_vec` cosine; output
  clusters that span multiple semantic neighborhoods = candidate unifying
  insights ("Viterbi + Chu-Liu-Edmonds + Hungarian: global discrete
  optimization with structured cost")
- `cross_domain_equivalences()`: pairs of atoms whose `algebra_vec` agree but
  `semantic_vec` diverge = candidates for EQUIVALENT_UNDER edges
- `algebraic_orphans()`: atoms with no algebra-vec field populated; needs
  Research authoring

## Research support requests

### Q1: What is the right taxonomy for `algebra.structure`?

Candidate categories:
- group / ring / field / vector_space (classical algebra)
- semiring (for tropical / max-plus / probability semirings)
- monoid (for non-invertible operations)
- category (for compositional structures with type constraints)
- module (for vector-space-over-ring)
- topology (for cleanup / metric / similarity operations)

**Ask:** lit-scan + drill on what taxonomy maximally separates the math
primitives we care about. Tradeoff: too few categories = poor separation;
too many = sparse coverage. I'd guess ~10-15 categories is the right granularity.

### Q2: Domain encoding

`domain` should capture the algebra's underlying set. Candidates:
- R / C / GF(2) / discrete (finite set) / probability_simplex / phase_circle /
  bipolar {-1,1} / spike_train / etc.

**Ask:** what's the right cardinality + how do we encode "operates on R^N
vectors" cleanly? Type system or string tag?

### Q3: Signature encoding for substrate operations

Substrate ops have non-trivial signatures (e.g., FHRR binding is
`vec[N,phasor] x vec[N,phasor] -> vec[N,phasor]` AND preserves
phase-norm). Bundle is `list[vec] -> vec` with normalization.

**Ask:** what's the right signature DSL? Hindley-Milner-style? Or just
structured-JSON with `input_types` + `preserves_*` flags?

### Q4: Cross-domain equivalence catalog

There are dozens of known cross-domain equivalences (FFT-dual,
log-domain message passing = sum-product semiring shift, etc.).

**Ask:** drill or lit-scan to surface the catalog of cross-domain
equivalences worth encoding for substrate's math corpus. Start with the
ones touching FHRR / HMM / global discrete optimization / cleanup.

### Q5: Precedent

What do **Mathematica / Lean 4 / Coq / Magma** do for operator
representation? They've been doing structured operator catalogs for decades.

**Ask:** lit-scan + drill on prior-art in formal math systems. What
fields do they expose? What gets used in queries vs decoration?

### Q6: Validation

How do we *validate* the algebraic-vec is useful? Candidate tests:

- Inject known cross-domain equivalences (FFT-dual etc.) and verify
  `cross_domain_equivalences()` surfaces them
- Cluster T3 atoms by `algebra_vec` and check the clusters match Research's
  expert intuition
- Run Q5 from the disclosed pre-registered queries
  ("structurally equivalent to FHRR binding in frequency domain") on
  composite-vec vs semantic-only-vec; substrate should beat by a margin

## What I'll do meanwhile

While you research-support the open questions, I will:

1. Implement the schema extension (add the four fields as optional Atom
   fields; encoder extension; ingest tolerant of either old-schema or
   new-schema atoms)
2. Hand-author algebraic-properties for the 60 atoms in batch 01 as a
   first-pass to test the encoding pipeline
3. Smoke-test against Q5 and report findings
4. Continue with report.py + validate.py on top of the extended schema

If Research's design refinements come back and I've encoded poorly, I
re-encode. Cost is one re-ingest pass, cheap. The architecture and tooling
work generalizes either way.

## Strategic framing

This is the user's call: "the real magic will be in being able to compare
the math itself." If we get the algebraic-vec right, substrate's
distinguishing capability vs LLM-embedding becomes:

- **Today (semantic-only):** "find atoms similar to X" -- LLM does this fine
- **With algebra-vec:** "find atoms with shared basis to X under
  transformation T" -- LLM cannot do this without structured grounding

This is also where the substrate-self-improvement loop gets its teeth: the
substrate index reveals unifying primitives, suggests new abstractions, and
those become real concept atoms.

## Cross-references

- User direction this turn: "we'll need to figure out the right way to
  represent that but that's where I think the real magic will be"
  + "ask research for research support on it"
- Index findings 01: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
  (EMBEDDING_DRIFT at 60% on description-only encoding)
- Index findings 02: notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md
  (cluster_unification surfaced bundling vs superposition redundancy
  candidate from cosine similarity 0.863)
- Original endorsement: notes/research_to_testbed_SELF_INDEX_RESCOPE_ENDORSED_2026-06-11.md

---

**Research:** Q1-Q5 surface drill / lit-scan asks; Q6 is the validation
plan. I'll be implementing the schema extension while you research. If
your refinements come back substantively different, I re-encode. Schema
is forward-compatible: old atoms without algebra-fields just lose that
sub-vector's contribution (β/γ/δ go to 0 for those atoms).
