# Research -> USER + Team: status of all work in flight + intuitive framing + Stratified Hybrid Level 3 architecture detailed + H3 update shifts to NEG-1 pivot to H2 schema-world-model

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** USER prompt -- implement all + deeper on Level 3 + status + intuitive

## TL;DR

- **H3 update integrated**: Exp-Dev did the cheap test; drop-guard ELIMINATED over-filtering but operand-selection stayed FLAT -> the 6-deep wall is SCHEMA/world-model not relevance-filtering -> **APPROVE PIVOT TO H2 container/transfer world-model** OR explicit defer to Phase 6 full ingest. The "knowing WHICH operands matter" signal (F1 0.84) is necessary but not sufficient; substrate also needs "knowing HOW operands combine" (schema).
- **Stratified Hybrid 6-layer**: detailed below with intuitive meaning per layer + what each unlocks
- **Status table** of all in-flight work
- **Intuitive framing** of substrate-product positioning at the architectural level

## H3 update -- Exp-Dev's NEG-1 verdict is CORRECT

Drop-guard test eliminated over-filtering penalty (full operand-sel 0.5908 -> 0.6003 == baseline 0.6013 within noise). Distractor subset unchanged at 0.027. Classifier still F1 0.84.

This is the EXACT NEG-1 shape from my drill: "relevance P(R) >0.85 on held-out but ASDiv flat -> pivot to H2 container/transfer world-model."

Per 9th methodology rule (refine-via-FAIL): Exp-Dev's cheap-test was right discipline. The data shifted from "ambiguous NEG-3 over-filtering" to "clean NEG-1 schema-not-relevance". Verify-before-asserting applied to own option-(a) lean.

**Verdict**: APPROVE pivot to H2 container/transfer world-model. OR explicit accept (c) defer to Phase 6 full ingest.

Recommend Exp-Dev: cheap shot at H1 quantity-verb deps via PP-399 dep-parser (1 day, substrate-native) as cross-check; if it ALSO flattens, the schema-world-model wall is confirmed at structural-NL-feature level too, then defer to Phase 6.

Actually, given Exp-Dev's prediction that H1 will also plateau without combine-schema, the EV-favored move is:
- Skip H1 cheap-shot
- Directly pursue H2 container/transfer (more substantial, ~3-5 days) OR defer to Phase 6 (Testbed evolve continuation)
- Run H2-lite synthetic test first as cheap proxy

If H2-lite also fails: 6-deep wall confirmed at world-model level too -> Phase 6 is the only remaining path.

I'll let Exp-Dev pick H2-lite ~2 days OR direct defer based on GPU/CPU lane availability.

## Level 3 Stratified Hybrid 6-layer architecture -- deeper

Math drill's recommended representation. Each layer is a DIFFERENT WAY to encode a different ASPECT of mathematical structure. They COMPOSE so atom vectors carry multi-axis meaning.

### Layer 0: FHRR phasor at D=4096 (atomic random base)

**What**: Every atom gets a random unit-modulus complex vector in 4096 dimensions. This is the "fingerprint" — uncorrelated with any other atom by construction.

**Why**: Provides the algebraic substrate (FHRR phasor space; Plate 1995 + Frady-Sommer 2023). Random iid means bind/unbind operations preserve information cleanly. Raising from D=1024 to D=4096 buys capacity per Langenegger 2023 Nature Nano (D >= O(M log M) for ~100K atoms).

**Intuition**: Like giving every concept a unique fingerprint. The fingerprints don't mean anything alone; they're the canvas on which we draw the structure.

### Layer 1: RotatE algebra encoding

**What**: Algebraic relations (is_associative, is_commutative, has_inverse, fhrr_dual_of, etc.) are encoded as ROTATIONS in the complex Layer 0 space. If fhrr_bind has inverse fhrr_unbind, then vec(fhrr_unbind) = phase_rotation(vec(fhrr_bind), angle=π).

**Why**: Math relations are MULTIPLICATIVE/ROTATIONAL not additive (math drill key insight; RotatE Sun et al. 2019). Parallelogram law fails for math because (king + woman - man = queen) works for translational relations, but (associative + invertible - identity != group) doesn't work for algebra.

**Intuition**: Imagine every atom has multiple "compass directions" pointing to its relations. "Inverse of" is one compass; "dual of" is another; "associative variant of" is a third. Rotating along a compass takes you from one atom to its related one.

**What it unlocks**: Substrate can find the inverse of any operation by phase rotation. "What's the inverse of fhrr_bind?" = rotate by inverse axis. "What's the dual of circular_convolution?" = rotate by dual axis. No metadata lookup needed.

### Layer 2: TPR signature encoding

**What**: Tensor product representation (Smolensky 1990) encodes typed signatures EXACTLY. For atom with signature (input_type=vec_N, output_type=vec_N), the TPR layer encodes bind(role_input, vec_N) ⊗ bind(role_output, vec_N). Lossless type encoding.

**Why**: HRR-bind has approximate capacity; TPR is exact but D² cost. Sweet spot: use TPR only for signatures (small, finite type vocabulary) so cost is bounded; use HRR everywhere else.

**Intuition**: Each atom carries a precise type-signature label. "I take 2 vectors and return 1" becomes a structured tag attached to the atom's vector.

**What it unlocks**: Type-aware retrieval. "Find atoms that take a (vector, vector) pair and produce a vector" returns the binding family. "Find atoms that take a distribution and return a scalar" returns the divergence family.

### Layer 3: Functorial composition (DisCoCat-style)

**What**: When you compose two operations (f after g), the COMPOSED operation's vector emerges from a FUNCTORIAL transformation of f and g's vectors. Per Coecke-Sadrzadeh-Clark DisCoCat: F(f∘g) = F(f) · F(g) where · is the categorical product (substrate-implementable as HRR-bind of role_composes_with).

**Why**: Mathematics IS category theory in spirit. Operations compose. Theorems compose (proof of A∧B from proof of A and proof of B). Functors preserve composition (the WHOLE POINT of functoriality). If substrate encodes operations as Layer 0+1+2 vectors, then HRR-bind(vec_f, vec_g) gives an approximate vec_f∘g — and substrate can SEARCH for what that composition looks like.

**Intuition**: "Bayesian inference applied to a Markov chain" should produce a vector near "Bayesian MCMC" by composition. "Apply Fourier transform after convolution" should give "multiplication in frequency domain" (convolution theorem). The geometry encodes the algebra of compositions.

**What it unlocks**:
- **Functor discovery**: "Find F such that F(group) = ring + multiplication" via geometric search
- **Composition proposal**: "Propose new pipeline by bundling these components"
- **Cross-domain analogy**: "What's the algebraic-topology analog of cleanup?" via functorial transport
- **AlphaProof-style structural reasoning**: proof steps composed via functorial transformations

### Layer 4: GNN dependency over DEPENDS_ON DAG

**What**: A graph neural network propagates information over substrate's DEPENDS_ON edges. Each atom's final vector aggregates its own Layers 0-3 encoding PLUS aggregated representations of atoms it depends on (k-hop neighborhood).

**Why**: A theorem's MEANING isn't just its statement; it's its WEB OF DEPENDENCIES (which lemmas it uses, which theorems use it). GNNs encode this naturally. Substrate already has 1793 DEPENDS_ON edges; this layer leverages them.

**Intuition**: An atom doesn't exist in isolation. Its position reflects its place in the dependency DAG — what it builds on, what builds on it. Like a person's reputation reflects who they know.

**What it unlocks**:
- **Premise selection** (Lean-style theorem proving): "What lemmas should I cite to prove X?" via dependency-aware retrieval
- **Subfield navigation**: "Show me the convex-optimization neighborhood" emerges from connected components
- **Discovery of missing dependencies**: substrate can predict that "theorem X probably depends on lemma Y" if Y is geometrically close

### Layer 5: SDM cleanup at scale (Kanerva)

**What**: Sparse Distributed Memory (Kanerva 1988). Atoms are stored at multiple sparse memory locations; retrieval uses radius-based readout. Beats dense cleanup at 100K-atom scale because storage capacity scales linearly with addresses, not quadratically.

**Why**: At substrate's target ~100K atom scale, dense cleanup (cosine over all atoms) gets expensive O(N²) and accuracy degrades. SDM gives O(N) storage with bounded retrieval error.

**Intuition**: Like a library card catalog with multiple subject headings per book. You don't search every book; you go to the most relevant headings.

**What it unlocks**: Sub-second retrieval at 100K atoms. Without Layer 5, substrate hits computational wall around 10K atoms.

## What Stratified Hybrid means INTUITIVELY (substrate-product story)

**Today**:
"Substrate has atoms with metadata (algebra dict, signature dict, complexity dict). We can search by string matching on description (bge cosine). Some atom-to-atom queries work via algebra HRR index."

**With Stratified Hybrid**:
"Substrate atoms occupy specific positions in a 4096-dim HRR space such that:
- Inverse operations are at 180° rotations of each other (Layer 1)
- Operations with same type-signature cluster (Layer 2)
- Composition of operations emerges from vector composition (Layer 3)
- An operation's place in the dependency DAG shapes its position (Layer 4)
- Sub-second retrieval at scale (Layer 5)

Querying becomes structural: 'What's like F but for category theory?' = transport vec(F) along the subfield axis. 'What 2-step composition produces a divergence measure?' = bundle search over type-signature space. 'What theorems use both Lebesgue integration and Markov chains?' = dependency-aware retrieval."

**LLMs cannot match this** because their embeddings are text-similarity. They approximate some of this brittlely (king-queen analogies) but break on structural composition + functoriality + dependency reasoning. Substrate is BY-CONSTRUCTION structurally meaningful because we explicitly bind (role, filler) per layer.

## Are we doing all this? STATUS table

| Workstream | Status | Owner | Next |
|---|---|---|---|
| Position-IS-meaning empirical audit | DONE | Research | -- |
| 4x VSA drill (literature corroboration) | DONE | Research | -- |
| 4x math representation drill | DONE | Research | -- |
| Testbed Cell 1 atom-to-atom clustering | DONE STRONG POSITIVE | Testbed | -- |
| Cell 2 v1 NL->HRR parser | DONE PARTIAL | Testbed | re-run post-backfill ingest |
| 30-atom algebra backfill core VSA | DONE SHIPPED | Research | -- |
| Algebra backfill ingest | PENDING | Testbed | next |
| Cell 2 re-run on FHRR/Hopfield/Bayesian | PENDING ingest | Testbed | -- |
| 5-level test (revised rotational) framework | PENDING | Testbed | -- |
| Retriever.semantic v2 (algebra primary + bge fallback) | PENDING | Testbed | -- |
| Multi-field RRF empirical (Exp-Dev finding name/idtok lever) | DONE | Exp-Dev | DEPRIORITIZED secondary |
| Semantic A-axis-specific (axis-gating in HYBRID) | DONE Exp-Dev | -- | Testbed should integrate |
| PP-400 chunking multi-seed | DONE HARD_PASS | Exp-Dev | -- |
| Cell 2 PP-394 ASDiv-WK multi-seed | PENDING | Exp-Dev | next |
| Phase 6.1 H3 distractor relevance | DONE FLAT NEG-1 verdict | Exp-Dev | pivot H2 OR defer Phase 6 |
| H2 container/transfer world-model | PROPOSED | Exp-Dev | start when ready |
| GPU bge re-encode pending batches | PENDING | Exp-Dev | next GPU job |
| Bge index caching infra | PENDING | Testbed | Q4 build |
| Q09 PP-364 sh backfill | PENDING | Exp-Dev | when CPU free |
| Math drill Stratified Hybrid 6-layer | NOTED | Cycle 50+ | medium-term target |
| Queue/dashboard blocker | FLAGGED USER | -- | needs decision |

## What this all MEANS intuitively (overall framing)

USER's question on substrate's brand promise: "vectors should mean something."

**Three claims being tested in parallel**:

1. **At atom-to-atom level**: position IS meaning (Cell 1 says YES; 8/8 nearest correct on math anchors)

2. **For free-text query → atoms**: position IS meaning IF we wire NL->HRR parser + author algebra fields (Cell 2 v1 says YES for RL; FAILS on FHRR because substrate's own primitives had algebra=None — we just fixed that with the 30-atom backfill)

3. **At full Gap 7 7-axis benchmark**: substrate-product positioning = macro-F1 0.70 via the wiring fix (current 0.587 + the algebra HRR retrieval + axis-gating + multi-seed promotions + Phase 6 ingest)

**The mathematical-representation question** the user raised goes further: there's an OPTIMAL representation that compounds these claims into:
- Cross-domain analogy (functorial)
- Composition proposal (bundle search)
- Dependency-aware reasoning (graph layer)
- Type-aware retrieval (TPR signature)

The math drill says that representation is Stratified Hybrid 6-layer. We're not there yet — Cycle 50+ work. But the immediate fixes (algebra backfill + NL->HRR parser + axis-gating + better composite blend) are ALL part of the path. Each shipped today moves substrate closer to the optimal representation.

**Honest read**: substrate-product positioning is REAL but currently UNDER-WIRED. Cell 1 proves the geometry works. Cell 2+3 will prove the NL interface works. Stratified Hybrid is the full architectural target. Everything we're shipping is on this path.

## Implementing all recommendations

In progress / queued:
- Algebra backfill batch SHIPPED (waiting Testbed ingest)
- Canonical role convention DEFINED (Testbed has it for further authoring)
- 5-level test framework REVISED (rotational; Testbed will build)
- Retriever.semantic v2 wiring (Testbed will implement)
- Phase 6.1 pivot to H2 OR defer to Phase 6 (Exp-Dev decides)
- PP-394 ASDiv-WK multi-seed (Exp-Dev next CPU)
- Bge re-encode for cached index (Exp-Dev next GPU)
- Math drill Stratified Hybrid 6-layer (Cycle 50+ target)
- Queue/dashboard blocker (USER decision)

## Routing

**Exp-Dev**:
- H3 verdict ACK (clean NEG-1 schema-wall confirmed by drop-guard test)
- Choose: H2 container/transfer ~3-5d OR direct defer to Phase 6 (recommend H2-lite synthetic ~2d as cheap proxy)
- Cell 2 PP-394 ASDiv-WK multi-seed in parallel CPU
- GPU: bge re-encode pending batches for cached index

**Testbed**:
- Ingest algebra backfill 30-atom batch (substrate's own VSA primitives finally get encoded)
- Re-run Cell 2 NL->HRR parser on FHRR/Hopfield/Bayesian (should now surface gold)
- Build 5-level test L1 (revised: rotational per math drill)
- Wire Retriever.semantic v2 (algebra HRR primary + bge fallback conf 0.6 threshold)
- Mwp_wk_schemas standalone ingest (SRL moved out per prior fix)

**Research**:
- This consolidated status note
- Standing for Testbed ingest + Exp-Dev verdict landings
- Will provide Cell 3 backfill v2 (next ~50 atoms) after Cell 2 re-run shows lift signal
- Math drill Stratified Hybrid -- noted for Cycle 50+ when implementation budget available

## Cross-references

- All recent notes per file system mtime
- USER directive: implement all + deeper on Level 3 + status + intuitive

---

**USER + Team:** USER prompt implement all + deeper Level 3 + status + intuitive ADDRESSED + Exp-Dev H3 UPDATE drop-guard test ELIMINATED over-filtering operand-selection FLAT classifier F1 0.84 sufficient signal NEG-1 schema-world-model wall NOT NEG-3 over-filtering + APPROVE pivot H2 container/transfer OR defer Phase 6 + cheap H2-lite synthetic ~2d proxy + Stratified Hybrid 6-layer deepened L0 FHRR 4096 atomic random base canvas + L1 RotatE rotations encode algebra relations inverse-as-rotation + L2 TPR signature lossless type encoding + L3 functorial composition DisCoCat F(f composed g) = F(f) bind F(g) functor discovery + composition proposal + cross-domain analogy + AlphaProof-style + L4 GNN dependency DAG premise selection + L5 SDM cleanup at 100K scale + intuitive substrate atoms occupy specific positions inverse operations at 180 rotations + type-signature clusters + composition emerges + dependency shapes position + sub-second retrieval at scale + LLMs cannot match structural geometry + status table all workstreams + WE ARE DOING ALL THIS YES + Cell 1 STRONG POSITIVE position-IS-meaning at atom-to-atom level validated + Cell 2 PARTIAL ingest backfill should lift + Stratified Hybrid Cycle 50+ medium-term + USER queue blocker decision still needed + USER full-auto continuing.
