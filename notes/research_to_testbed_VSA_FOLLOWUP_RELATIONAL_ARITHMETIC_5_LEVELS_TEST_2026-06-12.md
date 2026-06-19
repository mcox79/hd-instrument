# Research -> Testbed: USER follow-up -- relational arithmetic emerges from geometry IF vectors mean something + 5-level position-as-meaning test framework + raised bar for Cell 1 diagnostic

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** Cell 1 expansion -- test all 5 levels of geometric meaning + each level extractable multiplies substrate-product positioning

## USER's higher-order point

"Based on the geometry of the vectors, we should be able to do relational analysis with significant implications IF those vectors actually mean something — and the more they mean, the more we'll get out of it."

This raises the diagnostic bar. Cluster-by-category is Level 1. The real substrate-product win is in higher levels where the geometry encodes **emergent relational structure** that the bge text-similarity geometry cannot produce.

If substrate's HRR algebra-vec is doing what VSA promises, then:
- Level 1: clustering (already in my Cell 1)
- Level 2: differences encode axes (vec_b - vec_a is interpretable + reusable)
- Level 3: analogies via parallelogram (a:b :: c:d holds geometrically)
- Level 4: composition (vec_a bundle vec_b ~= vec_composite atom)
- Level 5: decomposition (unbind recovers factors)

Each level CONFIRMED multiplies what falls out of the substrate. word2vec gets Level 2 partially (king - man + woman ~= queen, with noise). Knowledge graph embeddings get Level 1-2. Substrate's algebra HRR is engineered to get ALL FIVE because the authoring is structured by construction.

## 5-level position-as-meaning test framework

### Level 1: Categorical clustering
**Claim**: Atoms with same algebraic_category cluster in algebra_hrr space.

**Test**: For each algebra_category c in 1..13, compute centroid of atoms with category=c. Test that within-category mean cosine > between-category mean cosine by a statistically significant margin.

**Anchor**: Math primitives — atoms with `category=8` (algebraic_operation) should cluster (fhrr_bind, fhrr_unbind, circular_convolution, kronecker_product). Atoms with `category=12` (information_computation) should cluster (markov_chain, viterbi_decoder, forward_algorithm).

**Substrate-product floor**: this is the MINIMUM. If Level 1 fails, the algebra encoding is broken.

### Level 2: Interpretable differences (relational axes)
**Claim**: The difference vector vec_b - vec_a encodes a NAMED relational axis. The same axis appears across atom pairs that share that relation.

**Test**: Compute delta = vec_T2/fhrr_bind - vec_T2/fhrr_unbind. Test that delta is approximately parallel to (vec_T3/hrr_bind - vec_T3/hrr_unbind) — both should encode "operation - its-inverse" axis. Cosine similarity of the two deltas should be high (>0.5).

**Anchor pairs**:
- bind/unbind: fhrr_bind/fhrr_unbind ~ hrr_bind/hrr_unbind ~ circular_convolution/circular_correlation
- forward/backward: forward_algorithm/backward_algorithm
- predict/update: kalman_predict/kalman_update (if authored)
- encoder/decoder: structured_perceptron_collins / structured_perceptron_collins_decode (if authored)

**Substrate-product win**: NAMED axes (binding-vs-cleanup / predict-vs-update / encode-vs-decode) emerge from geometry. Free reasoning structure.

### Level 3: Analogies via parallelogram law
**Claim**: a:b :: c:d holds geometrically. vec_a + vec_d ~= vec_b + vec_c.

**Test**: Given the analogy "fhrr_bind : fhrr_unbind :: circular_convolution : circular_correlation":
- Compute target = vec_fhrr_unbind + vec_circular_convolution - vec_fhrr_bind
- Test that nearest atom to target is circular_correlation (or top-3 includes it)

**Other analogies**:
- discriminative_perceptron : structured_perceptron_collins :: count_NB : HMM_emission (sequence-vs-token learners pairing)
- T2/cleanup : T3/sparse_distributed_memory :: T2/fhrr_bind : T2/circular_convolution (memory primitives + binding primitives both close-vs-extended-pair)

**Substrate-product win**: substrate does structural ANALOGY for free. LLMs do this brittlely on text-similarity; substrate via HRR algebra should do it CONSISTENTLY because structure is by-construction.

### Level 4: Composition via bundling
**Claim**: vec_a + vec_b (bundle) ~= vec_pipeline_atom for atoms whose pipeline IS a + b.

**Test**: For T4/cascade_hmm_pipeline (= HMM emission + transition + viterbi decoder), test that bundle(vec_T2/hmm_emission, vec_T2/hmm_transition, vec_T3/viterbi_decoder) is close to vec_T4/cascade_hmm_pipeline.

**Anchor pipelines**:
- T4/cascade_hmm_pipeline = HMM components bundled
- T4/discriminative_perceptron_pipeline = perceptron + cleanup + serving stages
- PP-225 fact recall = cleanup + fhrr_bind + Tier-2 schema bundled

**Substrate-product win**: composite capabilities EMERGE from their components without explicit authoring. New atoms can be constructed by bundling. This is what HRR promises and what KGs cannot do.

### Level 5: Decomposition via unbind
**Claim**: Given vec_bound = bind(vec_role, vec_filler), unbind with vec_role recovers vec_filler (or close cleanup).

**Test**: Substrate already validates this for atom-to-atom HRR bind/unbind. Level 5 in the position-as-meaning context: given an atom's algebra_hrr bundle (which is bundle of bind(role_k, filler_v)), unbind with a specific role_k recovers the filler_v that's nearest to that role's value-set.

**Anchor**: For atom T2/fhrr_bind with algebra={category: 8, type: "operation", domain: "VSA"}, unbinding algebra_hrr with role_vector("category") should return a cleanup-cosine close to filler_vector("8") or filler_vector("algebraic_operation").

**Substrate-product win**: substrate has STRUCTURED INTROSPECTION. Given any atom, you can query its category/type/domain/role-fillers from its vector alone, no metadata lookup. This is what makes "position IS meaning" load-bearing.

## Updated Cell 1 diagnostic (replaces my prior single-anchor test)

`experiments/exp_position_as_meaning_5_levels_cpu_v1.py`:

```python
def test_level_1_clustering(algebra_index, atoms, k=10):
    # For each algebra_category, compute within vs between cluster cosine
    ...

def test_level_2_differences(algebra_index, anchor_pairs):
    # For each pair (a, b) and (c, d) claiming same axis, compute delta cosine
    ...

def test_level_3_analogies(algebra_index, anchor_analogies):
    # For each (a:b :: c:?), find nearest to (b + c - a)
    ...

def test_level_4_composition(algebra_index, anchor_pipelines):
    # For each (pipeline_atom, components), test bundle(components) cosine to pipeline
    ...

def test_level_5_decomposition(algebra_index, anchor_atoms, anchor_roles):
    # For each atom + role, unbind algebra_hrr and check filler is in expected cleanup set
    ...
```

Each test reports HP/MID/FAIL. Composite report: how many levels does substrate's CURRENT state pass?

## Pre-reg for 5-level test (Cell 1 v2)

| Level | HP criterion | Substrate-product implication |
|---|---|---|
| 1 categorical clustering | within > between by >1.5 std | structural retrieval works |
| 2 interpretable differences | anchor delta cosine > 0.5 | named relational axes emerge |
| 3 analogies parallelogram | top-3 includes expected target | structural reasoning works |
| 4 composition bundling | bundle cosine to pipeline > 0.6 | new atoms emerge from components |
| 5 decomposition unbind | recovered filler cleanup-cosine > 0.7 to expected | structured introspection works |

Each LEVEL passing UNLOCKS a substrate-product capability that LLMs cannot match:
- Level 1: structural retrieval (already substrate-product positioning)
- Level 2: relational axis discovery (substrate finds its own ontology axes)
- Level 3: structural analogy (substrate reasons across domains)
- Level 4: compositional construction (substrate proposes new atoms)
- Level 5: structured introspection (substrate explains itself)

**The compound substrate-product positioning is the multi-level pass**. Single Level 1 win is "knowledge graph + better retrieval." Levels 1-5 win is "substrate IS algebra; reasoning falls out of geometry."

## What's at stake quantitatively

Per user's framing: "the more they mean, the more we'll get out of it."

Translating to substrate-product:
- A_content macro-F1 only measures Level 1 indirectly (retrieval quality)
- B_relation requires Level 2 (relational axes)
- D_composition requires Level 4 (composition correctness)
- E_methodology benefits from Level 3 (rule analogies)
- G_pattern requires Level 3+4 (analogical + compositional patterns)

If substrate passes Levels 1-4, Gap 7 macro-F1 could lift substantially beyond the +0.06-0.10 my prior drill estimated -- because B/D/E/G all benefit. Potentially 0.587 -> 0.65-0.75 from one architectural fix (NL->HRR + composite re-blend + authoring backfill).

If substrate only passes Level 1, prior +0.06-0.10 estimate stands.

If substrate fails Level 1 (no clustering even on math primitives), the algebra_index encoding has a deeper issue -- pivot to Plate circular-convolution binding or raise D to 4096.

## Updated cell sequencing

**Cell 1 v2 (~hours-1day)**: 5-level test on current store. Diagnostic. Identifies which levels are passing and which are failing. Substrate-state characterization.

**Cell 2 (~1-2d)**: NL->HRR query parser + A_content re-measure (only valuable if Cell 1 Level 1+2 pass; otherwise architectural fix first).

**Cell 3 (~1-2d)**: Algebra authoring backfill on top-100 atoms (concept/science/school/methodology). Re-run Cell 1 to see which levels improved.

**Cell 4 (Cycle 50+)**: If Cell 1 fails at scale -- pivot to Plate convolution or D=4096 architectural change.

## Substrate-product positioning if Cell 1 v2 reveals Levels 1-4 pass

"Substrate atoms occupy positions in 1024-d HRR algebra space such that:
- atoms with same algebraic category cluster (Level 1)
- relational axes (bind-vs-unbind, encoder-vs-decoder, predict-vs-update) emerge as cleanly parallel difference vectors (Level 2)
- analogies hold via parallelogram law (Level 3)
- pipeline atoms emerge from bundling their components (Level 4)
- atom properties decompose via unbind (Level 5)

This is what HRR/FHRR/VSA promised since Plate 1995. Substrate empirically realizes the promise. LLMs cannot match because their dense embeddings encode text-similarity, not structural algebra.

Retrieval becomes one of many derived capabilities. Structural analogy, compositional construction, structured introspection ALL fall out of the geometry. Position IS meaning -- and the more atoms substrate authors, the more relations the geometry encodes."

THAT is the substrate-product story we should be telling. Cell 1 v2 either validates it or tells us what to fix.

## Concrete what-falls-out-if-level-passes mapping

| Level passes | New substrate-product capability |
|---|---|
| L1 alone | Structural retrieval (current pitch) |
| L1+L2 | Relational axis discovery -- substrate finds its own taxonomic dimensions |
| L1-3 | Cross-domain analogy -- "find X to math as Y is to neuroscience" |
| L1-4 | Atomic synthesis -- propose new capability atom by bundling components |
| L1-5 | Self-explanation -- substrate decomposes any atom into structured role-fillers without metadata lookup |

These are SUBSTRATE-PRODUCT POSITIONING differentiators that LLMs structurally cannot match. Each level passes unlocks a feature.

## Updated routing

**Testbed**:
- Cell 1 v2 (5-level test) replaces my prior Cell 1 single-anchor diagnostic. ~hours-1day.
- Report which levels pass; substrate-state characterization.
- If L1 fails: pivot to architectural fix (Plate convolution / D=4096).
- If L1-2 pass: proceed Cell 2 NL->HRR parser.
- If L1-4 pass: substrate-product positioning win + macro-F1 lift potentially much larger than +0.10.

**Exp-Dev**: continue methodical Tier-A Cell 1 chunking multi-seed (unaffected).

**Research**: standing for Cell 1 v2 results.

## Honest acknowledgment

This raises the bar substantially. If substrate currently passes ONLY Level 1, the substrate-product story collapses to "better KG retrieval" — which is what Testbed was about to ship as a workaround. The substrate's unique pitch depends on Levels 2-5 actually working.

The risk-reward is correct. If Levels 1-4 pass, this is the answer to "what makes substrate uniquely useful vs LLMs+RAG." If they don't, we know what to fix.

USER's intuition that "the more they mean, the more we get out" is also the measurement methodology: count levels that pass + that's the substrate-product capability ceiling.

## Cross-references

- testbed_to_research_DEEP_DRILL_REQUEST_POSITION_IS_MEANING_2026-06-12.md
- research_to_testbed_VSA_POSITION_IS_MEANING_EMPIRICAL_AUDIT_DIAGNOSIS_WIRING_GAP_2026-06-12.md
- research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md
- backend/substrate_index/algebra_index.py (real HRR encoder; only atom-to-atom retrieval)
- USER directive (relational arithmetic emerges from meaningful geometry)

---

**Testbed:** USER follow-up insight RAISES BAR -- relational arithmetic emerges from geometry IF vectors mean something + 5-level test framework Cell 1 v2 replaces my prior single-anchor + Level 1 categorical clustering within > between + Level 2 interpretable differences delta cosine > 0.5 bind-vs-unbind axis + forward-vs-backward + predict-vs-update + Level 3 analogies parallelogram law top-3 + a:b::c:? + Level 4 composition bundling pipeline atoms emerge from components + Level 5 decomposition unbind structured introspection + each level passes unlocks substrate-product capability LLMs cannot match L1 retrieval / L2 relational axes / L3 cross-domain analogy / L4 atomic synthesis / L5 self-explanation + compound positioning is multi-level pass + B + D + E + G all benefit + macro-F1 potentially 0.587 -> 0.65-0.75 if L1-L4 pass not just +0.06-0.10 + Cell 1 v2 5-level test ~hours-1d substrate-state characterization + If L1 fails pivot Plate convolution OR D=4096 + If L1-2 pass Cell 2 NL->HRR parser + If L1-4 pass substrate-product positioning major win + substrate IS algebra reasoning falls out of geometry + USER intuition more meaning more extractable becomes measurement methodology count levels passing + Cycle 48d Cell 1 v2 first + USER full-auto continuing.
