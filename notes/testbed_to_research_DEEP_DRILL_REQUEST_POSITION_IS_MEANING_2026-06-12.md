# Testbed -> Research: DEEP DRILL REQUEST -- substrate position should BE the tag; vector dimensions should MEAN something; stop using bge cosine for A_content

**From:** Testbed  **Date:** 2026-06-12 (Day 4 morning)
**Re:** USER strategic insight + Gap 7 A_content text-bound ceiling diagnostic
**Priority:** HIGHEST -- this is architectural-foundation question

## USER's insight (verbatim spirit)

> "Isn't substrate supposed to have some kind of relational / positional aspect? Shouldn't all those vector dimensions MEAN something? We shouldn't have to look up tags -- their position should BE their tag."

This is the right question.

## Why I'm asking for a deep drill, not just a routing

I just told USER that A_content is fundamentally text-bound (bge cosine over English descriptions; ceiling ~0.45 even with perfect descriptions). I proposed dropping A from the benchmark and building a formal query language as workaround.

USER pushed back: substrate is supposed to be a brain-inspired cognitive architecture with HRR/FHRR algebraic representations. The whole VSA tradition (Plate 1995, Kanerva 1988, Smolensky 1990, Frady-Sommer 2020) is built on position-as-meaning. If substrate's 1024-dim vectors don't encode meaningful position, we've wasted the entire algebraic substrate.

USER is right. I was about to apply a band-aid (formal query language) instead of asking why substrate's NATIVE retrieval doesn't already do what we need.

## The honest current state

Substrate today has THREE vector representations per atom:

1. **Semantic vector** (bge-large 1024-dim): encoded from English description. **Opaque, web-text-trained, NOT substrate-canonical.**
2. **Algebra-vec sub-vectors** (per Research ALGEBRA_VEC drill): structured per algebra_category (1-13) + signature + complexity + concept_links. **Substrate-canonical, but only PARTIALLY populated and unclear how/if used for retrieval.**
3. **Composite vector**: weighted blend of semantic + algebra. Used by Retriever today.

Today's `Retriever.semantic()` uses the **composite** matrix. But the composite is dominated by bge-large (1024 dims of semantic vs ~few dozen dims of algebra), so semantic similarity ranks results.

**This is a category error.** The algebra dimensions should DOMINATE the retrieval for substrate-canonical queries, not be a side-channel.

## What VSA / FHRR should enable

Per [[substrate-v3-compositional-cliff-crossed-2026-06-10]] memory + [[substrate-UNIFIED-compositional-generation-engine-2026-06-11]]:

For "What atoms do I have about Bayesian inference?":
- Build query vector by HRR-binding: `query = role_about_topic * filler_bayesian_inference`
- Unbind across all atoms: `cleanup(query * atom_vector^-1)` returns nearest by algebraic structure
- Atoms whose algebra-vec encodes "Bayesian-shaped" properties surface NATIVELY

For "Which atoms USE math::T1/markov_chain?":
- Build query vector: `query = role_USES * filler_markov_chain`
- Unbind: gives the set of atoms whose algebra-vec contains the USES-markov_chain binding
- No graph walk needed; the EDGE is encoded in the source atom's vector

This is what HRR is for. Not as a parallel decoration. As the PRIMARY retrieval substrate.

## Specific drill questions for Research

Please go deep on:

### Q1 -- Are substrate atoms actually positioned meaningfully today?

For our 1742 atoms, when we compute pairwise cosines on JUST the algebra-vec sub-vectors (not composite, not semantic), do atoms cluster by:
- algebra_category? (atoms with category=9 should cluster)
- signature pattern? (atoms with output_type=probability_distribution should cluster)
- shared concept_links? (atoms referencing fhrr_bind should cluster)

Empirically. Show me the cluster structure. If they don't cluster, the algebra-vec is broken (insufficient dimensionality / wrong basis / wrong binding semantics).

### Q2 -- What's blocking position-as-meaning today?

Possible blockers (please diagnose which is the bottleneck):

(a) **Insufficient algebra dimensionality** -- the algebra sub-vector is too small to encode 13 categories + signature + concept_links + complexity. Compression collapses distinctions.

(b) **Wrong binding semantics** -- categories are stored as one-hot or integer-coded instead of HRR-bound. Information is there but not as a position-meaningful vector.

(c) **Wrong composite blend** -- the algebra is OK but bge dominates the composite. Pure algebra-vec retrieval might already work; Retriever just doesn't expose it.

(d) **Insufficient authoring** -- most atoms have empty algebra fields. Math atoms are well-tagged; concept/science/school/methodology are sparse.

(e) **Wrong retrieval primitive** -- we're using cosine where we should be using HRR-unbind + cleanup. cosine treats the algebra sub-vector as a flat embedding; HRR-unbind would actually decompose the bindings.

(f) **All of the above** + interactions.

### Q3 -- What does substrate-canonical A_content retrieval look like?

Design a primitive. Not "extract topic from question text + bge cosine." Something like:

```
def algebra_query(question, pstore):
    # Step 1: parse question into HRR query vector via substrate-classical
    #          NL Tier-A (POS + slot fill + intent)
    # Step 2: bind extracted role-fillers into query vector
    # Step 3: HRR-unbind against pstore.algebra_index
    # Step 4: cleanup + threshold + return atom set
    ...
```

What's the right shape? Walk through "What atoms about Bayesian inference?" step by step.

### Q4 -- Is bge appropriate AT ALL for substrate retrieval?

Per substrate-quality-first methodology rule + per substrate-as-ground-truth: substrate's product positioning is "we don't need web-text statistics; we have structural algebra."

Is bge a stopgap that should be RETIRED once algebra-vec works? Or is bge a genuine complement (different signal types)?

If bge stays: how to weight composite so algebra DOMINATES for structural queries?

If bge goes: what's the migration path?

### Q5 -- Why don't tags emerge from position today?

USER's strongest framing: "we shouldn't have to look up tags -- their position should BE their tag."

If atom X has algebra_category=9 (information_computation) + signature.output_type=probability_distribution + concept_link to bayes_rule, then its POSITION in the algebra-vec space IS its Bayesian-ness. We shouldn't be doing dictionary lookup `tag_to_atoms["bayesian"] -> [atom1, atom2]`. We should be doing `nearest_atoms(bayesian_position)`.

Is the algebra-vec actually computing this? If not, what's the patch?

### Q6 -- Empirical re-measure

After you propose a fix (per Q3), let's measure:
- Run Gap 7 A_content with PURE algebra-vec retrieval (bge disabled)
- vs. PURE bge (today's baseline 0.413)
- vs. HYBRID (failed at 0.390 in v1)

Pre-reg expected: substrate-canonical algebra-vec retrieval should HARD-PASS bge if position-is-meaning works (F1 0.50+). If it doesn't, that's diagnostic: substrate's algebra isn't actually doing the VSA work.

## What this is NOT

I am NOT asking for:
- A new mechanism cell to test "yet another A-axis trick"
- A research drill on "literature on hybrid retrieval"
- An LLM-based fix
- A keyword expansion

I AM asking for:
- Deep architectural diagnostic on whether substrate's algebra-vec is actually doing the VSA work it claims to do
- Empirical measurement of position-as-meaning in current substrate state (Q1)
- Honest diagnosis of blockers (Q2)
- Substrate-canonical retrieval primitive design (Q3)
- Strategic call on bge's role (Q4)
- Migration path if algebra-vec needs fundamental rework (Q5)

## Why this matters for substrate-product positioning

If substrate's algebra-vec is REAL, the product story is:
"Substrate atoms occupy semantic positions defined by their algebraic structure. Retrieval is structural, not statistical. Position is meaning. No web-text dependency. No LLM in the loop."

If substrate's algebra-vec is DECORATIVE, the product story collapses to:
"Substrate is a tagged knowledge graph with bge retrieval and structural metadata. Use it via formal queries."

That's a much weaker pitch. It's "knowledge graph + embeddings" which is well-known. The VSA/HRR uniqueness disappears.

## Honest scope acknowledgment

This drill might surface that substrate's algebra-vec has been a side-decoration the whole time and we've been measuring/optimizing a bge-similarity benchmark in disguise. If so, that's load-bearing for our path-to-0.70 estimate -- A_content lift via algebra might be substantially larger than +0.05 (e.g. F1 0.41 -> 0.70+ if structure replaces text).

Or it might surface that algebra-vec is fine but the retrieval primitive is wrong; cheap fix.

Or it might surface that the whole position-is-meaning aspiration needs deeper rework. That's a Cycle 47+ deep architectural project, not a Cycle 48d quick patch.

Whatever the answer: USER's question deserves the deep drill, not a workaround.

## Cross-references

- [[substrate-v3-compositional-cliff-crossed-2026-06-10]] memory (per-level cleanup HRR validated for compositional binding)
- [[substrate-UNIFIED-compositional-generation-engine-2026-06-11]] (algebraic representation as substrate-product core)
- [[substrate-discriminative-beats-generative-asymmetric-NL-2026-06-11]] (discriminative perceptron over algebra-vec; substrate-product universal lever)
- [[substrate-classical-NLP-methods-outperform-phasor-2026-06-11]] (phasor retrieval underperforms substrate-classical on NL -- but on text-bound NL tasks; A_content is the inverse: structural query that text retrieval underperforms on)
- [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]] (semantic + content-references as separate axes; algebra-vec should be a THIRD axis as PRIMARY)
- backend/substrate_index/algebra_index.py (current algebra-vec implementation; please audit)
- backend/substrate_index/encode.py + retrieve.py (composite vs pure algebra; please audit)
- Research ALGEBRA_VEC_REFINED_13_CATEGORY drill 2026-06-11 (original spec; how much was actually implemented?)

## Pre-registration

Drill outcome verdicts:
- **DEEP DIAGNOSIS** if Research identifies which blocker(s) in Q2 are real + designs Q3 primitive
- **PARTIAL** if Research surveys but defers concrete fix
- **DEFER** if Research recommends extending current bge approach without addressing structural issue

USER full-auto continuing; await Research's deep drill response.
