# Research drill: L3 DisCoCat functorial composition + AG2 architectural parallel (Cycle 53 design, 2x deep)

Date: 2026-06-12
Drill type: 2x DEEP architectural-design drill (level-2 operational synthesis)
Topic: L3 Stratified Hybrid layer -- functorial DisCoCat composition + AG2-style verifier
Scope: literature scan (12 generic queries across 2 rounds) + synthesis for substrate L3 cell pre-reg
Calibration penalty applied: yes (P deflated 0.15-0.25; novel-synthesis cap 0.50)

## HEADLINE

DisCoCat provides a mature, classically-implementable functorial recipe (pregroup/CCG grammar -> compact closed category of tensors via a strong monoidal functor) that maps cleanly onto substrate's existing composition primitives; combined with an AG2-style symbolic verifier loop (deduction-database forward chaining + verifier-in-the-loop), it yields a coherent L3 architecture where substrate's algebraic foundation (L0/L1 HRR + RotatE) lifts to a CATEGORICAL foundation. Substrate-product positioning: substrate becomes a BROADER AG2 (geometry+math+physics+ML+methodology) with substrate-classical verifier (no LLM in the loop). P(architecture viable as designed) = 0.45 after calibration penalty (novel synthesis cap 0.50, deflated 0.05 for uncharted compositional-generalization regime at substrate scale).

## Cheap decisive test

A single-cell L3 prototype on a SCAN-like compositional-generalization benchmark using:
1. lambeq-style pregroup/CCG parser on substrate's existing dep-parse output (PP-401 reuse)
2. functorial map: grammar diagram -> tensor diagram over substrate's two-vector encoder (PP-410)
3. compositional contraction via substrate's Cell A algebra-HRR primitives
4. AG2-style symbolic verifier: forward-chain a small substrate-classical deduction database over SHARES_MATH equivalence classes; reject compositions whose output capability-surface assignment violates a derived predicate

Pre-registered metric: macro-F1 on held-out novel-combination split of a SCAN-like task adapted to substrate's capability surfaces. 24-48 hour CPU smoke budget. Reuses existing primitives; no new model training required for the smoke (verifier ablation is the load-bearing piece).

## Falsifiable predictions

HARD-PASS (P=0.45 after deflation):
- L3 prototype macro-F1 >= 0.70 on SCAN-like novel-combination split
- Verifier rejection reduces hallucinated compositions by >= 30 percentage points vs no-verifier ablation
- No regression on Cell A composition baseline (no-cliff property preserved on training distribution)
- At least one substrate-classical compositional rule (e.g., a SHARES_MATH-derived inference) fires on >= 5% of test items and contributes >= +0.05 macro-F1

HARD-FAIL (P=0.25):
- macro-F1 < 0.55 on SCAN-like novel split (below current Cell A composition baseline, indicating L3 categorical lift NEGATES existing primitives)
- Verifier rejects > 80% of compositions (verifier mis-calibrated; deduction database under-specified)
- Any regression on Cell A no-cliff property (architectural lift destroys existing capability)

MIDDLE-BAND (P=0.30): 0.55 <= macro-F1 < 0.70. Treat as partial; document verifier-rule-coverage gap and queue follow-up drill into specific compositional construction (relative-pronoun Frobenius, distributive-coordination, quantifier-bialgebra) that under-performed.

## Round 1 findings (compact)

R1.1 DisCoCat foundations (Coecke-Sadrzadeh-Clark 2010, refined through 2021+): pregroup grammar is a compact closed category (rigid monoidal); FdVect is also compact closed; meaning composition is a STRONG MONOIDAL FUNCTOR F: Preg -> FdVect mapping atomic types to vector spaces, composite types to tensor products. Transitive verb meaning lives in N (x) S (x) N. Strong monoidality preserves adjoints/cups-caps -- grammatical reductions become tensor contractions automatically.

R1.2 Functorial tensor network composition: every grammatical type-reduction corresponds to a linear map; sentence meaning emerges from a tensor network whose topology is dictated by the parse. Two main tensor-network shapes documented in the literature: (a) Compact (Maillard et al.) -- per-word distinct tensor; (b) Tree-tensor-network -- shared composition tensor at internal nodes. Tree variant is substantially more parameter-efficient and parallels substrate's reuse-of-primitives discipline.

R1.3 Pregroup vs CCG grammar substrate: pregroup is minimal and category-theoretically cleanest; CCG (Steedman) has broader empirical coverage and an established type-driven tensor semantics (Maillard-Clark). lambeq library implements BOTH and reduces them to a common string-diagram representation. CCG-based DisCoCat (Yeung-Kartsaklis 2021) is the recommended pragmatic entry point.

R1.4 Quantum NLP (QNLP) literature is the dominant carrier of DisCoCat development (Quantinuum/lambeq), but the CLASSICAL pipeline is fully supported: TensorAnsatz functorially maps pregroup diagrams to tensor diagrams evaluated via NumPy/JAX/PyTorch. Substrate does NOT need quantum hardware.

R1.5 AlphaGeometry / AG2 architecture: neuro-symbolic, with (a) a neural language model proposing auxiliary constructions, (b) a Deductive Database Arithmetic Reasoning (DDAR) engine implementing forward-chaining over ~70 human-crafted geometric inference rules with arithmetic-reasoning sub-engine. AG2 adds double-points, faster DDAR2 in C++ (300x speedup), and SKEST parallel beam search. The verifier IS the deduction-closure computation.

R1.6 SCAN compositional generalization: Neural-Symbolic Stack Machines (Chen et al. 2020) and Neural-Symbolic Recursive Machines achieve 100% on SCAN by combining neural controllers with symbolic execution. Pure neural sequence models fail; the WIN comes from the symbolic verifier component. Substrate-classical analogue is natural -- substrate already has structured primitives that can play the symbolic role.

## Round 2 findings (compact)

R2.1 Strong monoidal functor preservation: the passage Preg -> FdVect via a strong monoidal functor automatically preserves compact-closed structure (cups, caps, adjoints). This is the LOAD-BEARING mathematical guarantee: any compositional construction proven sound in the grammar category transfers to the semantic category without re-proof. Substrate-product implication: substrate's existing SHARES_MATH equivalence classes (algebraic) can be lifted to functorial equivalences in the categorical setting.

R2.2 CCG tensor composition (Maillard-Clark): forward/backward application = tensor contraction along type-matched indices; type-raising = tensor reshape. The tree-tensor-network variant uses a SHARED order-3 tensor at each internal node -- this is structurally identical to substrate's algebra-HRR bind/unbind primitives reused across the parse tree. Confirms substrate's Cell A primitives are categorically appropriate.

R2.3 lambeq classical pipeline: pregroup/CCG -> string diagram -> TensorAnsatz -> PyTorch tensor network -> trainable end-to-end. SpiderAnsatz decomposes high-arity tensors into chains of lower-arity tensors -- substrate analogue would be the L1 HRR rotational decomposition. This is the production-ready reference implementation; substrate L3 cell should explicitly reference and benchmark against lambeq classical mode.

R2.4 AG2 DDAR mechanics: forward-chaining over typed predicates (collinear, concyclic, equal-length, parallel) with Gaussian-elimination arithmetic sub-engine for linear relations. ~70 rules. Hard-coded essential-rule search reduces AR query cost to cubic. The KEY architectural lesson: deduction database is SMALL (70 rules) and HAND-CRAFTED, with deduction closure being the verification primitive. Substrate analogue: a SMALL deduction-database (target 20-50 substrate-classical rules over SHARES_MATH + capability-surface predicates) is sufficient; verification is closure-computation, not exhaustive search.

R2.5 Neuro-symbolic verifier loops (2025 literature): the dominant successful pattern is RECURSIVE LOOP of generation + verification + correction (VLAgent, ProofNet++). The verifier is in-the-loop, not post-hoc. Substrate-product implication: L3 cell must structure inference as a LOOP not a feed-forward pass -- propose composition -> verify against deduction-database -> if rejected, retry with substrate's next-best proposal from algebra-primary scoring.

R2.6 Frobenius algebras in DisCoCat: model relative pronouns, intonation, quantifiers, conversational negation via internal-wiring spiders. Frobenius spiders implement copy/merge/discard operations that pure compact-closed cannot. CRITICAL substrate addition: substrate's two-vector encoder (PP-410) has structural + identity vector pairs that naturally support Frobenius copy/merge -- the identity vector is the "deletable" component, structural vector is the "wired" component. This is the substrate-novel categorical primitive worth pre-registering.

## Synthesis -- proposed L3 architecture

L3 cell architecture (Cycle 53 pre-registration):

Stage 1 -- Grammar parse: reuse existing dep-parse (PP-401) output; convert to CCG derivation via standard projection (Bos et al. parsers, or direct CCG parser if available). Output: string diagram in compact closed category.

Stage 2 -- Functorial map F: Preg/CCG -> SubstrateCat. SubstrateCat is the compact closed category whose objects are substrate capability-surface vector spaces (algebra-HRR codebook spaces) and whose morphisms are substrate's bind/unbind/cleanup/discriminative-perceptron primitives. F is strong monoidal: maps atomic grammar types to capability surfaces, composite types to tensor products thereof, type reductions to substrate's algebra primitives. Two-vector encoder (PP-410) provides Frobenius-spider implementations for relative pronouns/quantifiers/coordination.

Stage 3 -- Compositional contraction: evaluate the tensor diagram via substrate's Cell A composition primitives (already HARD-PASS no-cliff). This is the bulk computation.

Stage 4 -- AG2-style verifier loop: a substrate-classical deduction database with ~30 hand-crafted rules over SHARES_MATH predicates + capability-surface type predicates + LEX_T constants. Forward-chaining computes deduction closure of the composition's output predicates. Verifier ACCEPTS if closure consistent with target predicate; REJECTS if contradiction. On reject, retry with substrate's algebra-primary scoring's next-best filler proposal (loop, max 5 retries).

Stage 5 -- Output: highest-scoring verified composition; if all retries rejected, fall back to bge OOV-fallback (preserves hybrid RRF discipline).

Key substrate-specific lifts:
- SHARES_MATH equivalence -> functorial natural-equivalence between capability surfaces (free)
- PP-410 two-vector pair -> Frobenius copy/merge spider (substrate-novel)
- Algebra-HRR bind/unbind -> compact-closed cup/cap (already isomorphic)
- Discriminative perceptron -> verifier-acceptance scoring head (reuse universal-lever)
- Solution-history methodology rules -> seed for deduction-database authoring

## Cross-thread synthesis

This drill connects: Cell A composition HARD-PASS no-cliff (algebraic foundation ready); PP-410 two-vector encoder (Frobenius-ready structural+identity split); Phase-6 corpus ingest (provides math/science predicates for deduction-database authoring); substrate-as-metacognition engine (already extracts methodology rules -- same machinery can author deduction-database rules); brain-can-do-it rule (categorical composition IS brain-plausible per Lambek + cognitive linguistics).

Prior cap_map context: Cycle 50+ substrate has 9 Tier-A capabilities with discriminative-weighting + structural-binding; L3 categorical lift is the natural unification layer above these as substrate-classical primitives.

Prior research-thread context: 110 drills, 22 fields, none directly previous on DisCoCat or categorical compositional semantics -- this is a NEW field for substrate's adjacency map. Adjacency anchors: closest prior drills are PP-369/PP-371/PP-375 NL pipelines (two-stage decomposition rule) and Cell A composition. No saturation risk; first-appearance in field "categorical-compositional-semantics".

## Substrate-product implications

POSITIONING -- substrate as broader AG2:
- AG2 = geometry only, LLM-neural proposer + symbolic verifier
- substrate L3 = geometry + math + physics + ML + methodology + NL, substrate-classical proposer (algebra-primary + bge fallback) + substrate-classical verifier (deduction-database over SHARES_MATH + capability-surface predicates). NO LLM in the loop.
- This is the substrate-novel architectural claim: BROADER scope + LLM-free verifier loop. Defensible positioning vs AG2's geometry-only scope and vs LLM neuro-symbolic systems' LLM-dependent proposer.

LLM categorical gap:
- LLMs use attention (essentially soft-bilinear); they have NO categorical-functor representation of composition
- LLMs cannot expose strong-monoidal-functor structure; their composition is implicit and opaque
- Substrate L3 EXPOSES the functor explicitly -- categorical composition with verifier is structurally interpretable
- Substrate-product framing: "substrate has categorical composition + symbolic verifier; LLMs have neither"

Categorical foundation lift:
- L0/L1 = algebraic (HRR + RotatE; linear/rotational)
- L3 = categorical (compact closed category + strong monoidal functor; STRICTLY MORE GENERAL than linear algebra)
- L3 subsumes L0/L1 as the FdVect-restricted case; adds Frobenius spiders + verifier loop on top
- Substrate-product framing: "substrate is the only system that has BOTH algebraic and categorical foundations as a coherent stack"

## Honest scope

STRONG (lit-grounded, multiple independent sources):
- DisCoCat functorial recipe is mathematically sound (Coecke-Sadrzadeh-Clark 2010, Lambek-vs-Lambek 2013, lambeq 2021)
- AG2 architecture works empirically (gold-medal IMO geometry, JMLR 2025)
- Neural-symbolic stack machines achieve 100% on SCAN (Chen 2020)
- Classical lambeq pipeline is production-ready (Quantinuum 2024+)

MODERATE (synthesis warranted, not directly precedented):
- Substrate's algebra-HRR primitives as categorical morphisms (structurally appropriate; no published substrate-specific precedent)
- PP-410 two-vector pair as Frobenius spider (substrate-novel; requires explicit construction)
- Deduction-database authoring from solution-history methodology rules (substrate already extracts rules; transition to deduction-database format is new)

SPECULATIVE (substantial substrate-novelty; primary calibration penalty applies):
- Categorical L3 lift preserves Cell A no-cliff property at scale (Cycle 53 cell will measure; HARD-FAIL gates this)
- Substrate-classical verifier loop achieves >= 30pp hallucination reduction (no precedent for substrate-classical verifier; AG2's symbolic verifier is the analogue but operates over different predicate type)
- Substrate L3 macro-F1 >= 0.70 on SCAN-like split (NeSS achieves 100% but uses neural controller; substrate is fully classical -- this is the load-bearing uncertainty)

## Pre-registered Cycle 53 cell

Cell: L3-DisCoCat-prototype-v1
HARD-PASS: macro-F1 >= 0.70 on SCAN-like novel-combination split AND no Cell A regression AND verifier reduces hallucinations >= 30pp
HARD-FAIL: macro-F1 < 0.55 OR Cell A regression detected OR verifier rejects > 80% of compositions
MIDDLE-BAND: 0.55 <= macro-F1 < 0.70
Compute: ~24-48 hours CPU; reuses Cell A primitives + PP-410 encoder + new ~30-rule deduction database
Reporting: per-construction breakdown (transitive verb, relative pronoun, coordination, quantifier) to localize categorical-vs-algebraic gain

## Citations (verified count: 12 distinct sources)

1. Coecke, Sadrzadeh, Clark 2010 -- foundational DisCoCat paper (referenced via Wikipedia + nLab)
2. Wikipedia: DisCoCat -- framework overview
3. nLab: categorical compositional distributional semantics -- formal mathematical treatment
4. arXiv 1605.04013 -- Corpus-based toy model for DisCoCat
5. arXiv 2105.07720 -- CCG-Based Version of DisCoCat (Yeung-Kartsaklis 2021)
6. arXiv 2110.04236 -- lambeq library paper
7. Quantinuum lambeq classical pipeline docs (docs.quantinuum.com)
8. arXiv 2502.03544 / JMLR 2025 -- AlphaGeometry2 paper
9. DeepMind blog: AlphaGeometry (Nature paper PMC10794143)
10. arXiv 2008.06662 -- Neural-Symbolic Stack Machines (Chen et al. 2020)
11. arXiv 1505.00138 -- Compositional Distributional Semantics with Compact Closed Categories and Frobenius Algebras
12. arXiv 1302.0393 -- Lambek vs. Lambek: Functorial Vector Space Semantics

Plus secondary syntheses: arXiv 2406.17583 (Compositional Interpretability for XAI), arXiv 2308.04519 (DisCoCat for Donkey Sentences), Maillard-Clark Type-Driven Tensor-Based Semantics for CCG.

## Next-drill candidate

After L3 cell ships (Cycle 53), next research drill should be one of:
(a) Frobenius algebra constructions for substrate-novel composition (relative pronoun, coordination, quantifier) -- deepen the Frobenius substrate-mapping for PP-410 specifically
(b) Deduction-database authoring methodology -- how to systematically generate substrate-classical inference rules from solution-history (substrate-self-improvement applied to L3)
(c) Categorical adjacency: operads / props / symmetric monoidal categories beyond compact-closed -- broader algebraic foundation if L3 reveals compact-closed limitations
