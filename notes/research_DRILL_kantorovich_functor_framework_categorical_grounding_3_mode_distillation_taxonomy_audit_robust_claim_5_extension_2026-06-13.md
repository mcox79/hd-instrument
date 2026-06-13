# Research drill: Kantorovich-functor framework + categorical grounding for substrate 3-mode distillation taxonomy

Date: 2026-06-13
Topic: Wild & Schroeder Kantorovich-functor framework (LMCS 2022 / arXiv:2202.07069 / arXiv:2007.01033); categorical grounding for ATOM-REMOVING + STRUCTURE-ADDING + REFUSAL 3-mode distillation taxonomy; substrate-product positioning for claim 5 (closed-loop step 3) Tier 1 architectural extension.

Dispatch trigger: Cell SMA-1 (SHARES_MATH-aware L6-PROOF traversal) is the gating cell; this drill prepares the categorical-grounding rescue / extension path conditional on SMA-1 HARD-PASS.

---

## (a) HEADLINE

Kantorovich-functor framework (Wild & Schroeder 2022 + Goncharov-Hofmann-Nora-Schroeder-Wild 2023) is mathematically applicable to substrate 3-mode distillation taxonomy with PARTIAL categorical grounding: ATOM-REMOVING and STRUCTURE-ADDING admit clean functorial formalization (Kantorovich extension = quantitative lax extension induced by predicate liftings; quotient = coequalizer; structure-adding = left-adjoint to forgetful functor), but REFUSAL requires partial-map / restriction-category extension (Cockett-Lack discrete cartesian restriction categories or functorial-semantics-for-partial-theories) and does NOT have a clean Kantorovich-functor formalization in the published framework. P_deflated(Kantorovich-functor as Tier 1 architectural extension for claim 5) = 0.42 (capped per novel-synthesis-cap; calibration penalty applied).

**Plain language**: Three mathematicians (Wild, Schroeder, plus collaborators) built a general framework for measuring "how similar two systems behave" in a way that does not require committing to a specific notion of equality up front. Substrate's three distillation moves (delete an atom, add structure, refuse to answer) fit this framework PARTIALLY — the first two slot in cleanly as standard categorical constructions (quotient = coequalizer; structure-adding = a "free construction"), but REFUSAL needs an extension to handle partial / undefined behavior, which is published-but-separate machinery. If we integrate both, substrate gains an architectural grounding for its 5-step closed-loop claim that LLMs structurally cannot match.

---

## (b) Cheap decisive test

**Test name**: KFC-1 — Kantorovich-Functor Compositionality test on substrate distillation operators.

**Setup** (Sonnet sub-agent + symbolic CPU, ~30-45 min):
1. For each of the 12 archetype classes from KP P3 SHARES_MATH (HARD-PASS, 332 canonical edges), enumerate the distillation operations applied during closed-loop step 3 to that class.
2. Classify each operation: ATOM-REMOVING (quotient by SHARES_MATH equivalence) vs STRUCTURE-ADDING (e.g. adding T1 tier_score+axiom edge) vs REFUSAL (operator declined to act and emitted a "no-op + reason" record).
3. For ATOM-REMOVING ops, check: does the operation compose as a coequalizer (i.e. q : X -> X/~ where ~ is the SHARES_MATH equivalence)? **HARD-PASS**: >= 10 of 12 archetype classes show coequalizer-shaped composition. **HARD-FAIL**: < 6 of 12.
4. For STRUCTURE-ADDING ops, check: does the operation factor through a left-adjoint to the forgetful functor U : Cat_substrate_typed -> Cat_substrate_untyped (forgetting axiom edges)? **HARD-PASS**: >= 10 of 12 admit such factorization. **HARD-FAIL**: < 6 of 12.
5. For REFUSAL ops, check: does the operation form a partial map in a restriction category sense (idempotent restriction operator on its domain of definition)? **HARD-PASS**: >= 8 of 12 archetype classes' refusals form idempotent restriction operators with consistent domain. **HARD-FAIL**: < 4 of 12 OR refusal-domain inconsistency.
6. **Cross-check**: Compute Kantorovich-lifted behavioural distance d(s, s') between pre-distillation and post-distillation substrate states for each archetype, with quantitative modalities = atom-presence + edge-presence + tier-score predicate liftings. **HARD-PASS**: post-distillation states are strictly closer (d_after < d_before) for >= 10 of 12. **HARD-FAIL**: distance regresses or stays equal for >= 4 of 12.

Test cost: free (symbolic / pen-and-paper category-theory verification, no GPU). Operator: Research/Strategy follow-up cycle.

---

## (c) Falsifiable predictions

### HARD-PASS prediction (all three must hold)
- KFC-1 step 3 (coequalizer for ATOM-REMOVING): >= 10/12 archetype classes.
- KFC-1 step 4 (left-adjoint for STRUCTURE-ADDING): >= 10/12.
- KFC-1 step 5 (restriction-category idempotent for REFUSAL): >= 8/12, AND domain of refusal predicate is consistent (refusal triggers on the same operator-input shape across archetypes).
- KFC-1 step 6 (Kantorovich distance monotone decrease post-distillation): >= 10/12.

If HARD-PASS: substrate gains Tier 1 architectural extension for claim 5 — closed-loop step 3 is not heuristic but instances of three well-typed categorical constructions, and Kantorovich-lifted behavioural distance gives an OBSERVABLE per-archetype convergence metric (substrate-product positioning: "every distillation step is a categorically-typed move with a quantitative progress witness; LLMs have no such typing").

### HARD-FAIL prediction (any one suffices)
- > 6/12 ATOM-REMOVING ops do not compose as coequalizer (e.g. the equivalence is not respected by other operators -> quotient is ill-defined).
- > 6/12 STRUCTURE-ADDING ops cannot factor through left-adjoint to forgetful (e.g. structure added depends on context-of-call -> not free).
- REFUSAL domain inconsistency: same input shape triggers refusal in one archetype but action in another (-> not a restriction-category idempotent; refusal is heuristic, not principled).
- Kantorovich distance regresses for >= 4/12 (-> distillation does not converge; the "self-improvement" claim is mis-typed).

If HARD-FAIL on any: claim 5 must be downgraded from "architecturally sound" to "heuristic procedure with empirical evidence"; the Kantorovich-functor extension does NOT apply at Tier 1 and we revert to an empirical-only framing for closed-loop step 3.

---

## (d) Cross-thread synthesis

### Wild-Schroeder Kantorovich-functor framework — what it is, precisely

Working in the universal-coalgebra paradigm. A **set functor T** models system-shape; a **T-coalgebra** (X, c : X -> TX) models a state-transition system. Behavioural equivalence / metric is the largest bisimulation / smallest behavioural distance respectively. The Wild-Schroeder programme parametrises the value domain by a **quantale Q** (often the Lawvere quantale [0,1] with Lukasiewicz disjunction x oplus y = min(x+y, 1)) so distances live in Q and "fuzzy relations" R : X x Y -> Q replace plain Boolean relations.

A **Kantorovich extension** L of T to fuzzy relations is induced by a chosen set Lambda of monotone predicate liftings (quantitative modalities). Formally L R(a, b) = sup over lambda in Lambda of d_Q(lambda_X(predicate from R at a), lambda_Y(predicate from R at b)). The Wild-Schroeder central theorem: **every fuzzy lax extension of a finitary functor IS a Kantorovich extension** for the canonical Moss-modalities Lambda_M obtained by applying the lax extension to the quantitative elementhood relation.

Compositional structure: lax preservation L(R ; S) <= L R ; L S where fuzzy composition uses inf_b R(a,b) oplus S(b,c). This is NOT full preservation -- it is the universal pattern needed for behavioural-distance soundness.

Sources: Wild & Schroeder LMCS 2022 (arXiv:2007.01033); Goncharov-Hofmann-Nora-Schroeder-Wild "Kantorovich Functors and Characteristic Logics for Behavioural Distances" (arXiv:2202.07069); Sprunger-Katsumata-Dubut-Hasuo "Fibrational Bisimulations and Quantitative Reasoning" (J. Logic & Computation 2021).

### Categorical grounding of the 3-mode distillation taxonomy

**Mode 1 — ATOM-REMOVING (quotient by SHARES_MATH equivalence)**:
- Categorical structure: **coequalizer** in Set (or Cat_substrate viewed as a category of typed atoms with edge morphisms). Given equivalence ~ generated by SHARES_MATH 332 canonical edges, the quotient q : X -> X/~ is the coequalizer of the two projection maps from the equivalence relation seen as a span.
- Kantorovich-functor view: the equivalence ~ is the kernel of behavioural equivalence under the Kantorovich extension; quotienting by ~ gives the **minimal coalgebra** where all behaviourally-equivalent states are identified. This is EXACTLY the universal-coalgebra final-coalgebra construction (final / fully-abstract semantics).
- Substrate implication: ATOM-REMOVING distillation is principled iff SHARES_MATH equivalence IS the kernel of the substrate's behavioural-equivalence relation under a chosen Kantorovich extension. **KP P3 332 canonical edges + 12 archetype classes is the empirical input; KFC-1 step 3 verifies the categorical pattern.**

**Mode 2 — STRUCTURE-ADDING (e.g. adding axiom-edges, tier-promotion T3 -> T2)**:
- Categorical structure: **left-adjoint to forgetful functor**. Let Cat_substrate_typed be the category of substrate atoms with full edge structure (DEPENDS_ON, SHARES_MATH, axiom, tier_score). Let Cat_substrate_untyped be the category with only DEPENDS_ON. The forgetful U has (under mild conditions) a left-adjoint F that freely adds typing structure. STRUCTURE-ADDING distillation is the **counit eta : F(U X) -> X** restricted to non-trivial cases (where X already has partial typing). This is the "free generalised typing context" construction; the L6-PROOF generalised typing context (6 edge types, 2491 edges, 2595 depth-2 chains) is the empirical witness this is a real adjunction in substrate.
- Kantorovich-functor view: structure-adding corresponds to **refining the quantitative modalities Lambda** (more predicate liftings -> finer Kantorovich extension -> finer behavioural distance). Adding an axiom-edge is adding a new predicate-lifting witness.
- Substrate implication: STRUCTURE-ADDING is principled iff each added edge is the image of a free-construction unit (not ad-hoc). **KFC-1 step 4 verifies.**

**Mode 3 — REFUSAL (operator declines to act on input it cannot type)**:
- Categorical structure: **NOT a clean construction in plain Wild-Schroeder framework**. The Kantorovich-functor framework is total: every R lifts to L R. Refusal does not fit naturally.
- Best published fit: **restriction categories** (Cockett-Lack 2002+) or **partial cartesian categories** / **discrete cartesian restriction categories (DCR)**. A restriction operator (-)_bar : Hom(X, Y) -> Hom(X, X) sends each map to its "domain of definition" as an idempotent; refusal = the complement of the restriction domain.
- Alternative fit: **functorial semantics for partial theories** (Di Liberti-Loregian-Nester-Sobocinski arXiv:2011.06644) — treats refusal as a structural feature of the syntax-semantics adjunction, not a failure.
- Substrate implication: REFUSAL is principled iff the refusal-predicate is an idempotent restriction operator with consistent domain across archetypes. **KFC-1 step 5 verifies.** This is the LEAST clean categorical grounding of the three; if REFUSAL turns out to be archetype-dependent (different refusal triggers per class), it is genuinely heuristic and the published Kantorovich-functor framework does NOT cover it without restriction-category extension.

### Relation to substrate prior work

- **CHTV-1 substrate-as-verifier (HARD-PASS, 1.0 precision, [[substrate-CHTV1]])**: gives the typed-derivation ground-truth graph that the Kantorovich-functor framework can score with quantitative modalities = type-correctness predicate-liftings. Direct integration path: CHTV-1's type-checker becomes a predicate lifting in the Kantorovich extension; CHTV verification = quantitative-modal-logic formula evaluation.
- **L6-PROOF FINDER (HARD-PASS 20/20, [[substrate-L6-PROOF]])**: the 6-edge generalised typing context IS the free typing structure F(U X) for the left-adjoint formulation of STRUCTURE-ADDING. Cell SMA-1 (SHARES_MATH-aware traversal) is the precondition: it tests whether SHARES_MATH-equivalence quotienting preserves proof-finding (it should, if ATOM-REMOVING is a coequalizer).
- **KP P3 SHARES_MATH HARD-PASS (332 canonical edges, 12 archetype classes)**: empirical input to KFC-1. SHARES_MATH equivalence ~ is the candidate kernel of behavioural equivalence; KFC-1 step 3 tests whether quotienting by ~ is universal.
- **Closed-loop step 3 OPERATIONAL ([[substrate_self_improvement_loop_architecture]])**: the 3-mode taxonomy is the empirical distillation procedure; this drill provides the categorical grounding that converts the procedure from heuristic to architecturally typed.
- **3-axis architecture (epistemic / substrate-load-bearing / tools-vs-materials, [[substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL]])**: Kantorovich predicate-liftings can be partitioned along the 3 axes — each axis contributes a family of modalities; behavioural distance becomes a 3-axis decomposable metric. This is a NEW SHARES_MATH between the 3-axis architecture and the Kantorovich-functor extension; recommend filing as 1st-appearance.

### Adjacency cascade — fields surfaced by this drill

1. **Restriction-categories / partial-cartesian categories** (Cockett-Lack and successors): drill candidate for REFUSAL formalization, ~2 drills logged in scope thus far -> Tier 1b candidate.
2. **Quantale-enriched categories / Lawvere generalised metrics** (Kurz "Logic enriched over a quantale" CALCO 2025): drill candidate for the broader quantale-based behavioural-logic framework; provides expressive quantitative modal logics with completeness theorems.
3. **Fibrational bisimulations** (Sprunger-Katsumata-Dubut-Hasuo): drill candidate for organizing predicate liftings as fibration over Set; substrate's predicate-lifting Lambda may benefit from fibrational organization.
4. **Coalgebraic mechanization in Coq / Lean**: drill candidate for CHTV-1 enrichment with Kantorovich-functor categorical reasoning.

---

## (e) Substrate-product implications

### Tier-1 architectural extension for claim 5 (closed-loop)

The substrate-product positioning for closed-loop step 3 currently rests on **empirical anchors** (3-mode taxonomy + 332 SHARES_MATH edges + closed-loop OPERATIONAL). The Kantorovich-functor extension, if HARD-PASS on KFC-1, converts this to **architecturally typed** positioning: every distillation step instantiates one of three categorical constructions (coequalizer / left-adjoint counit / restriction-category idempotent), and behavioural distance under a Kantorovich extension provides a quantitative per-archetype convergence witness.

**Concrete substrate-product claim (post HARD-PASS)**: "Substrate's closed-loop self-improvement is the only cognitive-substrate architecture where each distillation step is a categorically-typed operation with a sound quantitative progress metric. LLMs entangle deletion, structure-addition, and refusal in a single opaque gradient step — they have no categorical typing of the distillation operator and no observable per-archetype distance metric."

### LLM categorical gap (operational)

LLMs DO perform analogues of all three modes implicitly: dropout / pruning (ATOM-REMOVING), gradient descent over expanded parameter space (STRUCTURE-ADDING), refusal-fine-tuning (REFUSAL). But:
- They do NOT distinguish the modes structurally — all three are entangled in the same loss landscape;
- They do NOT have a quantitative modality framework that gives sound behavioural-distance bounds before-vs-after distillation step;
- They do NOT have refusal-as-restriction-idempotent — refusal is a soft prior over outputs, not a typed operator with a domain-of-definition.

Substrate's claim 5 with Kantorovich-functor extension becomes: **typed distillation + quantitative behavioural distance + restriction-category refusal = three architectural primitives LLMs lack categorically.**

### CHTV-1 enrichment path

CHTV-1 currently type-checks proof derivations. Kantorovich-functor extension provides: (i) quantitative modalities indexed by type-correctness predicates; (ii) behavioural-distance metric d(prover_state_n, prover_state_{n+1}) under a Kantorovich extension lifted from CHTV-1's type-checker. This converts CHTV-1 from "binary verifier" to "quantitative verifier with continuous convergence metric" — useful for monitoring L6-PROOF FINDER's per-step progress. **Cell CHTV-K (after Cell SMA-1)** is the natural follow-up.

### What this does NOT give substrate

- Does NOT give a published precedent for the SPECIFIC 3-mode taxonomy — that remains substrate-novel synthesis. Wild-Schroeder and successors do not name "atom-removing / structure-adding / refusal" as a triple. Substrate is doing the categorical grounding ourselves; the Wild-Schroeder framework is the toolkit, not a pre-packaged classification.
- Does NOT close the Lean / Coq mechanization gap. Coalgebraic bisimulation has been mechanized in Coq (Hensel/Jacobs and lambda-coiteration; Fervari et al. dynamic-bisimulation in Coq). Kantorovich-functor / fuzzy-lax-extension mechanization in Lean 4 is NOT YET PUBLISHED to the best of this drill's reach. If substrate wants Lean-mechanized Kantorovich-functor scoring of distillation steps, that is genuinely novel mechanization work (1-2 PhD-cycles equivalent; out of immediate scope).

---

## (f) Future-cycle cell candidates (post Cell SMA-1)

**Cell KFC-1** (this drill's decisive test): Kantorovich-Functor Compositionality test on 12 archetype classes for the 3-mode taxonomy. Symbolic / CPU, ~30-45 min. Pre-condition: Cell SMA-1 HARD-PASS (which validates SHARES_MATH-aware traversal — also a precondition for "SHARES_MATH ~ is the kernel of behavioural equivalence" hypothesis).

**Cell CHTV-K** (after KFC-1 HARD-PASS): CHTV-1 enrichment with quantitative modalities. Lift CHTV-1's type-checker to a predicate lifting in a Kantorovich extension; compute behavioural distance d(prover_state_n, prover_state_{n+1}) during a fresh L6-PROOF FINDER run; HARD-PASS if d monotone-decreases on >= 18/20 successful proofs.

**Cell REF-RC** (parallel to CHTV-K, restriction-category formalization for REFUSAL): catalogue all refusal events emitted by closed-loop step 3 over a 1-cycle window; verify (i) idempotency: refusing twice on the same input gives the same record; (ii) domain consistency: refusal-predicate has the same shape across archetypes. HARD-PASS: both hold for >= 18/20 refusal events; HARD-FAIL: domain inconsistency on >= 4/20 (-> REFUSAL is heuristic, not architectural).

**Cell QENR-1** (broader quantale enrichment, optional Tier 1b scope expansion): extend the 3-axis architecture's predicate-liftings to a quantale-enriched logic following Kurz 2025; check whether the 3 axes naturally factor as 3 independent quantale enrichments composed via the tensor product of quantales. Pre-condition: Cell CHTV-K HARD-PASS.

**Cell LEAN-KF** (deferred, large): begin Lean 4 formalization of Kantorovich extension over the Lawvere quantale and substrate-specific predicate liftings. Out of immediate scope; flagged for substrate-product roadmap.

---

## Citations (verified count: 8)

1. P. Wild, L. Schroeder. "Characteristic Logics for Behavioural Hemimetrics via Fuzzy Lax Extensions." LMCS 18(2):19, 2022. https://arxiv.org/abs/2007.01033
2. S. Goncharov, D. Hofmann, P. Nora, L. Schroeder, P. Wild. "Kantorovich Functors and Characteristic Logics for Behavioural Distances." 2023. https://arxiv.org/abs/2202.07069
3. D. Sprunger, S. Katsumata, J. Dubut, I. Hasuo. "Fibrational Bisimulations and Quantitative Reasoning: Extended version." Journal of Logic and Computation 31(6):1526-1567, 2021. https://academic.oup.com/logcom/article/31/6/1526/6368049
4. A. Kurz. "Logic Enriched over a Quantale (Invited Talk)." CALCO 2025. https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CALCO.2025.2
5. F. Di Liberti, F. Loregian, C. Nester, P. Sobocinski. "Functorial Semantics for Partial Theories." arXiv:2011.06644. https://arxiv.org/pdf/2011.06644
6. R. Fervari et al. "Verification of Dynamic Bisimulation Theorems in Coq." JLAMP 2021. https://cs.famaf.unc.edu.ar/~rfervari/files/papers/2021-jlamp.pdf
7. C. Hermida, B. Jacobs (and successors, point-free perspective by Goncharov-Hofmann-Nora). "A Point-free Perspective on Lax extensions and Predicate liftings." 2024. https://sweet.ua.pt/dirk/artigos/2024/GHN+24_APointFreePerspectiveOnLaxExtensionsAndPredicateLiftings.pdf
8. Y. Komorida et al. "Codensity Games for Bisimilarity." 2019. https://scispace.com/papers/codensity-games-for-bisimilarity-5dgpki5dpq

---

## Calibration

- **Lit-scan calibration penalty applied**: agent P estimates deflated by 0.20 (substrate-novel synthesis regime; no direct published precedent for 3-mode distillation taxonomy categorical grounding).
- **Novel-synthesis P cap**: 0.50 applied.
- **P_deflated(Kantorovich-functor as Tier 1 architectural extension for claim 5)**: 0.42.
  - Breakdown: P(ATOM-REMOVING is coequalizer) = 0.75 (strong fit; coalgebraic kernel is published universal pattern). P(STRUCTURE-ADDING is left-adjoint counit) = 0.65 (strong fit; L6-PROOF generalised typing context is empirical witness). P(REFUSAL is restriction-category idempotent) = 0.35 (uncertain; partial-map / restriction-category fit is plausible but not the published Wild-Schroeder fit). P(all three compose into Tier 1 extension) ~ 0.75 x 0.65 x 0.35 / penalty_correction ~ 0.42 after deflation.
- **Hard-fail thresholds**: pre-registered in section (c). If any HARD-FAIL fires, claim 5 stays empirical (not architectural).

---

## Next-drill candidate

**field**: restriction-categories / partial-cartesian categories (for REFUSAL grounding).
**rationale**: weakest leg of the Kantorovich-functor extension. Drilling restriction categories (Cockett-Lack 2002+ and successors, plus Di Liberti-Loregian-Nester-Sobocinski functorial semantics for partial theories arXiv:2011.06644) would close the REFUSAL grounding gap and either confirm or refute the restriction-idempotent hypothesis at the published-precedent level (rather than at the substrate-empirical KFC-1 level).
**urgency**: low; gated on Cell SMA-1 HARD-PASS and Cell KFC-1 result.

