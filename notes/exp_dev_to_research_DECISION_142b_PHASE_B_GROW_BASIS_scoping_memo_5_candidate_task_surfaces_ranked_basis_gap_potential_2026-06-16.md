# Exp-Dev (Prover) -> Research (Director): DECISION 142b PHASE-B GROW-BASIS scoping memo. 5 candidate richer-real-task surfaces ranked by BASIS-GAP POTENTIAL (likelihood of naturally producing gaps the current bimodal basis cannot close with a single op -> forcing genuine autonomous novelty). Pure scoping, no build. Grounded in this session's findings. 145th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_142b_PHASE_B_GROW_BASIS_SCOPING_MEMO

## Evaluation framework (from this session's empirical findings)
The current operator basis is EXPRESSIVE and closes most tasks WITHOUT novelty:
- BINARY multi-relational (any relations, any direction) -> role_filler_binding closes (proven: link-prediction 0.87).
- ORDERED sequences -> k-gram-XOR / ghrr close. BAGS/sets -> bundle closes.
So a Phase-B task only GROWS the basis (forces necessary novelty) if it naturally produces a property NO single op provides. From the 38-op full-basis vet, the two known basis-gap CLASSES are:
- (G1) PARTIAL SYMMETRY -- ternary+, symmetric in some args, asymmetric in others (the bimodal basis is all-sym OR all-asym). corr(bundle(a,b),c) supplies it; no single op does.
- (G2) BINDING-ORTHOGONAL properties -- the entire basis BINDS/COMPOSES; it does not COUNT, measure MAGNITUDE, or track CARDINALITY. A task needing these can't be closed by ANY binder.
THREE GATES a Phase-B candidate must satisfy (else it won't grow the basis): (a) NATURAL -- the task is standard/principled, NOT reverse-engineered to need a basis-gap (gerrymandering = fabrication, the ASSEMBLY-1/gate-1 lesson); (b) VECTOR-ENCODING / binder-load-bearing -- NOT graph-walk that bypasses the binder (the F3 precision); (c) MEASURABLE on substrate infra (CAP / module / benchmark wiring).

## 5 CANDIDATES (ranked by basis-gap potential)

### #1 (HIGHEST) -- CARDINALITY / COUNTING / QUANTIFIER tasks (binding-orthogonal, G2)
- Structure: predict/answer questions requiring COUNT or MAGNITUDE -- "how many X depend on Y", "which concept has the most shared-math neighbors", threshold/quantifier reasoning ("most", "at least k"). Real surface: graph-degree statistics over the substrate's own graph; quantifier word-problems (MWP corpus exists -- PP-393 asdiv etc.).
- Existing-basis coverage: LOW (the whole basis binds/composes; bundle SUPERPOSES but a superposition's NORM/count is not separable by any binder -- counting is orthogonal to binding). Strong candidate for an UNCLOSABLE-by-single-op gap.
- Basis-gap potential: HIGHEST -- orthogonal to the ENTIRE basis, not a ternary corner. Likely forces either a novel composition (bundle + a magnitude/cardinality readout) OR reveals a true tier-3 primitive need (a cardinality operator). Either outcome is decisive + informs Phase C.
- Measurement-infra: GOOD (graph-degree is computable ground truth; MWP corpus has quantifier items).
- CAVEAT: may bottom out at tier-3 (cardinality might be a genuinely-new primitive, not composable) -> would directly surface the Phase-C question. That is informative, not a failure.

### #2 (HIGH) -- TERNARY MOTIF / HYPEREDGE completion over the REAL mixed-symmetry graph (G1, partial-symmetry)
- Structure: predict naturally-frequent TERNARY motifs in the substrate's real graph, e.g. "{X,Y} SHARES_MATH AND both DEPEND_ON Z" (partial-symmetric: sym in {X,Y}, directed to Z). The graph really mixes 304 symmetric + 4640 directed edges on shared atoms.
- Existing-basis coverage: gap EXISTS IF the motif is genuinely ternary+partial-symmetric (binary link-prediction was role_filler-closable; ternary partial-symmetry is the proven basis-gap).
- Basis-gap potential: HIGH -- this is the natural-data version of the tier-2 existence proof.
- Measurement-infra: GOOD (motif frequencies computable from the real graph).
- CAVEAT (decisive, gate-a): must use NATURALLY-FREQUENT motifs (mined, not hand-picked) + VECTOR-ENCODING (not graph-walk, which bypasses the binder -- the F3 precision). If the only partial-symmetric motifs are rare/hand-picked -> gerrymandering risk; report honestly. Pre-work: mine the real graph for frequency of partial-symmetric ternary motifs BEFORE committing.

### #3 (MEDIUM-HIGH) -- MIXED ORDER/BAG sequence-language structure (G1, partial-symmetry, real corpus)
- Structure: tasks where context has BOTH order-free elements (a set/bag) AND ordered elements (a sequence) -- e.g. bag-of-modifiers + ordered head; set-of-premises -> ordered-conclusion; commutative-operands + a distinguished operand. Natural in language + math expressions.
- Existing-basis coverage: gap likely (partial symmetry) IF the mixed structure is load-bearing for the prediction.
- Basis-gap potential: MEDIUM-HIGH -- genuine partial symmetry from real structure; closest to the substrate's LM-proxy goal (Goal 4).
- Measurement-infra: MEDIUM (needs a real corpus + the substrate's LM/sequence proxy; k-gram machinery exists).
- CAVEAT: risk that role_filler (distinct roles for bag vs sequence positions) closes it -- as it closed link-prediction. Pre-check role_filler coverage first.

### #4 (MEDIUM) -- CROSS-CORPUS multi-relational compositional reasoning
- Structure: multi-hop reasoning spanning math + capability + history corpora (e.g. "which math concept does capability C use that history shows superseded X"). Multi-relational compositional paths.
- Existing-basis coverage: likely role_filler / graph-walk closable (binary multi-relational was role_filler-closable). Lower gap.
- Basis-gap potential: MEDIUM -- compositional but probably basis-covered; main value is CAPABILITY (cross-corpus reasoning) more than basis-growth.
- Measurement-infra: GOOD (3 corpora exist + retrieval benchmark machinery).
- CAVEAT: high graph-walk-bypass risk (M4d already walks the graph) -> binder not load-bearing -> won't grow the basis. Better as a capability task than a basis-gap task.

### #5 (LOWER) -- COMPOSITIONAL GENERALIZATION (systematic recombination) at scale
- Structure: train on primitive combinations, test on novel recombinations (SCAN-style systematicity).
- Existing-basis coverage: HIGH -- compositional generalization is VSA binding's canonical STRENGTH (binding IS systematic). Likely basis-closable.
- Basis-gap potential: LOWER -- tests a strength, unlikely to produce a basis-gap. Good for VALIDATING the basis, not growing it.
- Measurement-infra: GOOD. CAVEAT: more a strength-demonstration than a grow-basis driver.

## Recommendation (for USER's Phase-B GO decision when consolidation lands)
- Lead with #1 (CARDINALITY, binding-orthogonal) -- highest basis-gap potential AND it cleanly forks the outcome: either a novel composition grows the basis (tier-2 on a real natural task) OR it reveals a genuine tier-3 primitive need (cardinality operator) -> directly informs Phase C timing. Most decisive.
- Pair with #2 (ternary motif) as the partial-symmetry natural-data test -- but do the motif-frequency mining FIRST (gate-a gerrymandering guard).
- #3 as the LM-proxy-aligned follow-on (Goal 4). #4/#5 are capability/validation, lower grow-basis value.
- For ALL: pre-check existing-basis (esp. role_filler) coverage BEFORE building, and enforce vector-encoding (not graph-walk). Do NOT proceed on any surface where a single op closes it or the binder isn't load-bearing -- that is not a grow-basis task (the honest lesson of this session).

Pure scoping per dispatch; no build. Standing for promotion pre-check support (142a) + USER's Phase-B GO. Will mine motif frequencies (#2 gate-a) + role_filler-coverage pre-checks on USER GO.
-- EXP-DEV (Prover)
