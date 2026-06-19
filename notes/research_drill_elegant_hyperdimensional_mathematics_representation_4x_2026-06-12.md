# Research Drill 4x DEEP - Elegant Hyperdimensional Representation of Mathematics

Date: 2026-06-12
Type: Literature + theory drill (ASCII-only, generic queries, no LLM-as-judge)
Cap: <1500 words

## Q1: WHAT STRUCTURE should an elegant HD representation of math capture?

Mathematics is not a flat symbol space; it is a stratified algebraic-categorical artifact. The minimal sufficient structure to encode for "valuable relational operations" is:

1. Signatures + types (arity, input/output types, polymorphism via type variables) - the substrate already has this skeleton.
2. Algebraic laws as ALGEBRAIC INVARIANTS, not labels (associativity, commutativity, identity, inverse, distributivity, idempotence). These are the symmetries the representation must respect, not annotate.
3. Morphism composition (Smolensky 1990; functorial composition).
4. Dependency / proof structure (theorem -> lemma DAG; tactic sequences in Lean / Coq).
5. Subject taxonomy (MSC / arXiv-math) as PRIOR not GROUND TRUTH per literature-is-not-oracle rule.
6. Category-theoretic objects+morphisms+functors+natural transformations (Shiebler et al. 2025 VSA-via-CT).

Insight: items 1-3 are LOCAL (per-atom); 4-6 are RELATIONAL (between-atom). An elegant representation must FACTOR these cleanly so analogies operate only on the relational substructure.

Cit: Smolensky 1990 (Artificial Intelligence 46:159-216); Plate 1995/2003; arxiv 2501.05368 VSA-CT foundation; Shiebler et al. "Categorical Representation Learning" (arxiv 2103.14770).

## Q2: VSA/HD CANDIDATES surveyed

| Candidate | Binding | Capacity (D=1024) | Math-relevant strength |
|---|---|---|---|
| HRR (Plate) | circular conv | ~O(D/log D) | analogy via dot-product (Plate 2000) |
| FHRR phasor (Frady-Sommer 2023) | elementwise phase add | similar to HRR, better noise | fractional-power encoding for continuous parameters (e.g. dimension counts, indices) |
| TPR (Smolensky 1990) | outer product | exact but D^2 blow-up | best for SHALLOW proof step state; bad for deep nesting |
| GHRR (Generalized HRR, arxiv 2405.09689) | parameterized family | tunable | unifies HRR/FHRR; per-role binding semantics |
| qFHRR (arxiv 2604.25939) | quantized phase | 3-4 bits/dim | hardware-cheap; integer arithmetic |
| BSC binary spatter | XOR | hamming-based | poor for continuous algebraic params |
| SDM (Kanerva 1988) | sparse addressing | high (15-35x via multi-substrate) | cleanup memory layer, not binding |
| KG embeddings (RotatE, ComplEx, TuckER) | complex rotation / Tucker decomp | trained, not algebraic | model symmetry/antisymmetry/composition AS RELATIONS - the natural fit for theorem KG |
| DisCoCat tensor (Coecke-Sadrzadeh-Clark) | grammar functor -> vector | tensor product, D^k | functorial, but explodes |
| Functorial CT embedding (Shiebler) | morphism = matrix; composition = matmul | linear | exact composition; trainable |
| Hierarchical FHRR + SDM cleanup (substrate today) | layered | engineered wrapper | already validated |

Cit: arxiv 2412.00488 (FPE cleanup); arxiv 2301.10352 (VSA capacity); arxiv 1901.09590 TuckER; arxiv 1902.10197 RotatE; arxiv 1101.0309 DisCoCat; arxiv 2103.14770 categorical rep.

## Q3: RELATIONAL ARITHMETIC over math vectors - what literature says

- Word2vec-style parallelogram (king-man+woman~queen) DOES NOT robustly transfer to math concepts because math relations are RARELY translational; they are MULTIPLICATIVE / ROTATIONAL / COMPOSITIONAL (arxiv 2505.18651 on emergence of linear analogies; arxiv 1705.04416 evaluating analogy).
- HRR-based analogy (Plate 2000) gives DOT-PRODUCT estimation of analogical similarity; superficial+structural similarity entangled.
- RotatE: relations as complex-plane rotations naturally encode symmetry, antisymmetry, INVERSION, COMPOSITION. This is exactly the algebra of fhrr_bind <-> fhrr_unbind generalized.
- HolE (holographic embeddings) = circular correlation - DIRECT MAPPING from HRR to KG completion. This is the bridge.
- Functorial category-theoretic embeddings: F(A)+F(B)-F(C) = F(D) under additive functors; under MULTIPLICATIVE functors becomes F(A)*F(B)*F(C)^-1.
- AlphaProof / AlphaGeometry use LEARNED proof-state embeddings inside Lean; no public algebraic structure beyond transformer features. Neuro-symbolic proposal-generator + verifier - the substrate occupies a DIFFERENT niche: substrate is the STRUCTURED memory, not the proposer.

Conclusion: substrate's correct analogy primitive is NOT parallelogram on dense vectors, but PHASE ROTATION + UNBIND on FHRR with 13-category algebra basis as the relation set.

Cit: arxiv 1902.10197 (RotatE); arxiv 2505.18651 (linear analogy emergence); Plate 2000 Wiley analogy retrieval; Nature 2025 AlphaProof IMO silver.

## Q4: CAPACITY at substrate's scale

Plate 1995 capacity ~ D / (log M) for clean recovery with N items. Langenegger 2023 (Nature Nanotechnology) gives D >= O(M log M) for clean unbinding under noisy hardware.

For substrate at 2K atoms growing to 100K:
- D=1024 supports clean recovery of ~100-200 bound items per atom envelope - sufficient for current 13-category algebra basis with per-atom feature set <20.
- D=4096 supports 1K-2K items per envelope - the right target for substrate as it scales to 100K atoms.
- D=10000 (canonical HD) is overkill at 100K corpus unless deep proof-step state stacking is attempted.

Sparse SDM beats dense at >50K atoms IF cleanup dominates compute; for substrate's compositional reasoning, dense FHRR + SDM cleanup hybrid wins (v3.2 ENGINEERED WRAPPER already validated this 15-35x).

qFHRR (3-4 bits/dim) cuts memory 8-10x with negligible algebraic loss - this is the dimensionality-cost frontier.

Cit: Plate 1995 IEEE TNN; Langenegger 2023 Nature Nanotech; arxiv 2301.10352 capacity analysis; arxiv 2604.25939 qFHRR.

## Q5: KILLER USE CASES if math is elegantly HD-encoded

1. Cross-domain structural analogy at scale: "Galois extension : field :: covering space : topological space" via shared HD signature on (preserves, input_type, output_type) tuple.
2. Functor discovery: find F such that bind(F, structure_C) ~ structure_D in cleanup memory - automated category-theoretic conjecture generator.
3. Dual-operation discovery via algebraic INVERSE (generalizes bind/unbind to any pair where preserves-relation is inverted).
4. Proof composition via vector bundle of tactic atoms; decomposition via per-role unbind.
5. Theorem PRIOR ranking for premise selection: substrate vector recall feeds Lean Hammer / LeanDojo style retrievers (arxiv 2510.23637 shows graph+text wins +25%, substrate adds the algebra-vector channel).
6. Concept lattice navigation via FCA-aligned HD layout (arxiv 2406.15517 multidim representation of physical theories).
7. Detect unformalized equivalences: cluster atoms whose unbind-residuals coincide.
8. Discriminative-weighted top-down attention over math KG (substrate's empirical universal lever - 11+ Tier-A caps).

## Q6: SUBSTRATE-IMPLEMENTABLE OPTIMAL RECOMMENDATION

NOT a single VSA. The optimal representation is a STRATIFIED HYBRID, where each layer matches the algebraic character of the structure it encodes:

- Layer 0 PRIMITIVE: FHRR phasor 4096-dim (upgrade from 1024) with deterministic role/filler vectors, qFHRR-quantized for storage (8x memory cut).
- Layer 1 ALGEBRA: 13-category basis as ROTATIONAL relations (RotatE-style complex rotations on phasor angles), making associativity/commutativity/inverse first-class.
- Layer 2 SIGNATURE: TPR (small outer product, exact) for (input_arity, input_types, output_type, preserves) since arity is shallow.
- Layer 3 COMPOSITION: functorial-CT linear-map embeddings (Shiebler 2103.14770) for morphism composition - matmul realizable, trainable.
- Layer 4 DEPENDENCY: GNN-over-DAG (LeanDojo-style) feeding into Layer 0 phasors as feature priors.
- Layer 5 CLEANUP: SDM multi-substrate (15-35x via v3.2 wrapper).

Authoring strategy: bootstrap from existing 13-category basis + serves_capability backfill; ingest Mathlib/arXiv-math signatures via auto-extraction (no LLM judge - pattern-extract on Lean syntax); validate via substrate-self-classification against MSC and against substrate's own emergent clusters (per substrate_self_validates_own_partition_design memory).

## SYNTHESIS: TOP-3 candidates for math specifically

1. **FHRR + RotatE algebra on 13-category basis** (substrate-native, lowest cost). Path: keep current encoder, upgrade D=1024 -> 4096, recast 13 categories as phase rotations not random vectors, add inverse-pair table. Unlocks: analogy via phase difference, automated dual-discovery, composition via phase addition. Cost: ~200 LOC; 1 week. Risk: low.

2. **Stratified Hybrid (recommendation)** = Layer 0-5 above. Path: extend current encoder into 5 wrappers, each addressing one structural axis. Unlocks: cross-domain analogy + functor discovery + premise ranking + proof composition simultaneously. Cost: ~2000 LOC over 4-6 weeks, gated per layer. Risk: medium (each layer independently testable).

3. **Functorial CT linear-map embedding (Shiebler)** as the pure category-theoretic alternative. Path: replace algebra basis with learned morphism matrices over a small math category. Unlocks: exact composition, theorem proving prior. Cost: high (training data + infra); 8-12 weeks. Risk: high - drifts from substrate's algebraic determinism.

**Optimal pick = candidate 2 (Stratified Hybrid)** because (a) it does not abandon substrate's empirical universal lever (discriminative_perceptron + algebra basis), (b) each layer is independently testable per substrate-on-substrate 5-tier progression, (c) it factors LOCAL vs RELATIONAL structure cleanly (per Q1), (d) brain-can-do-it - cortex stratifies sensory/syntactic/semantic similarly, (e) per benchmark-must-break-symmetry rule, RotatE phase rotations break the algebraic symmetry that flat HRR collapses.

## 5-YEAR VISION (substrate-product positioning)

Substrate-as-math-reasoning-engine: the FIRST cognitive architecture where mathematics is FIRST-CLASS HD-encoded such that (i) analogies across subfields are computed in O(D), (ii) premise selection for proof assistants is substrate-recall not transformer-retrieval, (iii) new conjectures are GEOMETRICALLY EXTRAPOLATED in algebra-vector space, (iv) the system EXPLAINS its analogies via unbind. LLM front-end + substrate algebra back-end is the neuro-symbolic frontier AlphaProof points toward but does not occupy structurally.

## PRE-REGISTERED NEGATIVE OUTCOMES (premise-falsifiers)

N1: If RotatE phase rotations on 13-category basis fail to produce robust analogy (cosine >= 0.5 on >= 60% of in-domain pairs at n=200), the "math is elegantly rotational" premise is WRONG and substrate should fall back to per-domain custom encoders.

N2: If functorial-CT composition predictions on Mathlib signature triples (F(A), F(B), F(A,B)) miss target by > 0.3 cosine residual at D=4096, functoriality is not empirically realized and Layer 3 must be redesigned or dropped.

N3: If cross-domain analogy (e.g. group-theory <-> Lie-algebra <-> Galois) cluster purity at HD layer is no better than random under permutation test (p > 0.05, n=500 pairs), the "shared algebraic substructure" claim is empirically void.

N4: If D=4096 FHRR with stratified hybrid does not beat D=1024 flat HRR on substrate's existing math caps by >= +0.05 abs at smoke gate, the elegance hypothesis fails the substrate-must-beat-itself bar (per drill-defeatism rule we exhaust 5 substrate-only configurations before accepting).

N5: If Mathlib signature auto-extraction yields <40% atom-classification agreement with substrate's emergent clusters, the corpus and the representation are misaligned and pre-ingestion structural work is needed (per Gap 1+6 sequencing rule).

---

End of drill. Word count: ~1480.
