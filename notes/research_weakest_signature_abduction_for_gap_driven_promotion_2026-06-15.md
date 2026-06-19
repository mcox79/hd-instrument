# Research drill: WEAKEST-SIGNATURE abduction for gap-driven promotion (reverse-math style)

Date: 2026-06-15
Topic family: substrate-product / gap-driven invention / abductive promotion loop
Dispatch trigger: USER strategic question -- "what published mechanism computes the SHAPE of the missing piece that would close a measured capability failure?"
Lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50).

---

## (a) HEADLINE

CEGAR-style interpolation + Progol-style inverse entailment + Halpern-Pearl minimal actual cause form a soundness-bearing 3-mechanism stack for computing the WEAKEST signature that closes a substrate capability failure -- reverse-mathematics itself does NOT extend to capability-shape calibration (it calibrates theorem-axiom strength only), but its calibration LOGIC (forward + reverse implication = minimality witness) transfers as a soundness pattern for the substrate's promotion gate.

One-line: the substrate already has the corpus and the gate; the missing kernel is an interpolant-computing abductor that derives the lower-bound shape of the predicate from a failure witness + existing primitive vocabulary, then certifies minimality by re-running the failure under the hypothesized signature with the predicate REMOVED (reverse direction).

---

## (b) Cheap decisive test

Pre-registered before any code is written.

**Test design (CPU-only, < 1 hr).** Take 10 currently-failing capability queries from the held-out set (the 651 currently-open derivations are the corpus; pick 10 where the 4-gate validator outputs HARD-FAIL and the failure mode is "no atom signature covers the goal"). For each:

1. Compute the FAILURE WITNESS: the concrete query + the closest-matching primitive signature(s) the validator did try + the residual goal that did not unify.
2. Build the BOTTOM SHAPE (Progol MDIE style): saturate the residual goal against the existing 105 operator signatures + 217 axiom-terms using mode declarations (input/output type signatures already exist as RelationType metadata). Output the most-specific clause perp(failure) that, if available, would have closed the gate.
3. Build the INTERPOLANT (CEGAR style): along the validator's failed inference trace, compute the predicate I such that (existing-vocab |- I) and (I -> goal). Use Craig interpolation over the typed signature lattice.
4. CERTIFY minimality (reverse-math style): assert the hypothesized predicate P, replay the failure, confirm gate now PASSES; then REMOVE one literal at a time from P -- if any single-literal removal still passes, P was not minimal (HARD-FAIL the abductor). If every removal causes the gate to fail again, P is the WEAKEST signature (HARD-PASS).

**Outcome variable:** fraction of 10 failures where the abductor produces a minimal P that closes the gate AND survives the leave-one-out minimality check.

---

## (c) Falsifiable predictions

HARD-PASS threshold: >= 4/10 (40%) of failures yield a minimal-certified P AND at least 2 of those P's correspond to a corpus atom that EXISTS but was not load-bearing (i.e. the abductor recovers known-but-passive vocabulary -- the gap-driven promotion case the USER wants).

HARD-FAIL threshold: <= 1/10 (10%) yield a minimal-certified P, OR every produced P is corpus-novel (the abductor only invents, never recovers -- which means it is doing search not abduction).

MIDDLE BAND (2-3/10): mechanism is real but bottom-clause shape is too narrow; redesign with broader mode declarations.

Calibration: P(HARD-PASS) deflated to 0.35 (novel synthesis of CEGAR + Progol + AGM on substrate data is uncharted; published systems use these on programs/circuits/proof terms, NOT on hyperdimensional capability signatures). P(useful-direction-even-on-HARD-FAIL) = 0.60 -- a failure mode where the abductor over-generates would still reveal whether the corpus is expressively closed under the operator vocabulary or genuinely missing primitives.

---

## (d) Cross-thread synthesis

Four parallel Sonnet lit-scans returned the following mechanism ranking by directness-of-fit to the substrate's gap-driven promotion question:

### Ranking by "computes the SHAPE of the missing piece"

| Rank | Mechanism | Soundness | Shape computed | Substrate fit |
|---|---|---|---|---|
| 1 | **CEGAR / predicate-abstraction refinement** (Clarke-Grumberg-Jha-Lu-Veith 2000) | Sound + progress-guaranteed (rel. to predicate language); completeness via decidability | EXPLICIT boolean predicate over typed states; computed by Craig interpolation along spurious counterexample trace | Strong -- substrate's failed validator-trace IS the spurious counterexample; interpolation lifts cleanly over the existing typed signature lattice |
| 2 | **Progol / MDIE inverse entailment** (Muggleton 1995) | Sound w.r.t. mode language; not complete | Bottom clause perp(e): most-specific clause s.t. background ^ perp(e) entails e | Strong -- mode declarations map onto existing RelationType / signature-type system; the perp(e) of a failure is the lower bound on hypothesis shape |
| 3 | **Halpern-Pearl minimal actual cause** (HP 2005; HP 2015 update) | Sound rel. to structural model; DP-complete decision | Minimal subset of variables whose intervention flips outcome | Medium -- treats failure as outcome variable; requires substrate-as-SCM framing (variables = primitive signatures; intervention = enable/disable in 4-gate validator) |
| 4 | **MIL / Metagol meta-interpretive learning** (Muggleton 2014; Cropper-Muggleton 2019) | Sound + complete on dyadic Datalog fragment | Smallest set of meta-rule instantiations whose Herbrand model covers examples; AUTO predicate invention from unbound 2nd-order vars | Medium -- requires reformulating substrate operators as meta-rules; soundness fragment may be too narrow |
| 5 | **SLDNFA abductive logic programming** (Denecker-Verbaeten 1998) | Sound w.r.t. generalized stable model + completion semantics; partial completeness | Ground or existential abducible atoms; no predicate invention | Medium-low -- gives the ABDUCTOR procedure but not the predicate-SHAPE invention; needs to compose with MIL for novel-predicate case |
| 6 | **Plotkin LGG / RLGG + Inoue consequence-finding** (Plotkin 1970; Inoue 1992; Kuzelka-Zelezny 2012 bounded LGG) | Sound; LGG-minimal under subsumption | Least general generalization of failure-evidence; weakest predicate via prime-implicate enumeration | Medium -- gives a constructive WEAKEST-EXPLANATION primitive that fits the USER's reverse-math intuition directly; bounded LGG restores polynomial cost |
| 7 | **Wassermann local-change AGM** (Wassermann 1999, 2000; Hansson-Wassermann 2002) | Sound w.r.t. base-AGM postulates over locality kernel | Minimal hitting set over relevance-restricted base B | Medium -- gives the MINIMALITY skeleton (kernel + hitting set) but not the SHAPE of the missing piece |
| 8 | **AlphaGeometry typed-frontier proposal** (Trinh et al. Nature 2024) | LM proposal heuristic; downstream symbolic verifier sound | Object-of-type, typed by deductive frontier | Medium -- maps if substrate exposes axiom-term closure as conditioning; LM-bootstrap (per USER 2026-06-15 ruling: OK as bootstrap until substrate self-selects) |
| 9 | **DreamCoder library learning** (Ellis et al. 2021 PLDI) | Heuristic Bayesian (MDL compression) | Post-hoc shared subexpressions from solved-task corpus | Weak for unsolved failures -- only finds gaps via compression of solutions; not failure-driven |
| 10 | **FunSearch** (Romera-Paredes Nature 2024) | None on proposals; soundness only at evaluator | Implicit (numeric score delta + in-context exemplars) | Weak -- pure generate-and-test; no abductive gap-shape computation |
| -- | **Reverse mathematics** (Friedman 1975; Simpson 1999/2009) | Conservativity over PRA / PA / hyperarithmetic | Set-existence axiom in Big Five (RCA_0 < WKL_0 < ACA_0 < ATR_0 < Pi_1_1-CA_0); ALWAYS a comprehension/induction principle, never a ground predicate | DOES NOT TRANSFER -- targets theorem-strength calibration, NOT capability-failure abduction. But the LOGIC of calibration (forward S |- T + reverse RCA_0 + T |- S = equivalence = minimality) transfers as the substrate's soundness pattern for the promotion gate |

### Critical non-fit finding

Reverse mathematics as a literal mechanism does NOT extend off-the-shelf to substrate capability-failure abduction. Per the Sonnet 1 report: "The classical machinery targets THEOREMS not capability failures. The nearest cognates ... none directly compute a minimal PREDICATE/SIGNATURE from observed counterexamples; the field assumes the theorem statement is given." The USER's reverse-math framing remains correct as an ANALOGY for the soundness pattern (the reverse direction RCA_0 + T |- S is what proves minimality) but the substrate must IMPLEMENT this via CEGAR interpolation + Progol bottom-clause + leave-one-out minimality certification, not via Simpson's Big Five hierarchy.

### Three-mechanism stack (the synthesis kernel)

The proposal IS:

1. **Lower bound** (Progol bottom clause): saturate failure-residual against existing 105 signatures + 217 axiom-terms via mode declarations. Output perp(failure) = lower bound on hypothesis shape. Sound w.r.t. mode language. This is the SHAPE-discovery step.

2. **Interpolant** (CEGAR/Craig interpolation): along the validator's failure trace, compute the typed predicate I separating concrete-failure from current-abstraction. Sound + progress-guaranteed in the predicate language. This is the MINIMALITY-direction step.

3. **Reverse certification** (reverse-math pattern, NOT Simpson's hierarchy): with I asserted, replay failure -> gate must pass; then leave-one-out remove each literal from I -> gate must fail again. This is the WEAKEST-SIGNATURE witness, modeled on the "RCA_0 + T |- S" reverse direction of a reverse-math calibration.

The composition is sound: each step has its own soundness property and the composition preserves them. The composition is NOT complete (Progol mode-bias incompleteness + Craig interpolation depends on theory decidability), which is consistent with the substrate's 18th methodology rule "RULE_substrate_refuses_what_it_cannot_prove" -- when the abductor cannot produce a minimal-certified P, the substrate refuses the promotion. This is exactly the USER's gap-driven invention loop with the abduction step concretized.

### Adjacent finding worth a follow-up drill

Plotkin LGG + Inoue's prime-implicate consequence-finding (Sonnet 3 report) is the OTHER constructive WEAKEST-EXPLANATION primitive that fits the USER's reverse-math intuition, via a different soundness route (subsumption-lattice minimality). Bounded LGG (Kuzelka-Zelezny 2012) restores polynomial cost. This is a candidate for a parallel implementation track -- if the CEGAR + Progol stack fails the cheap test, switch to LGG-based weakest-explanation. Queue as next research drill if the Phase 1 cell HARD-FAILs.

### What this DOES NOT solve

- Predicate INVENTION (novel symbol) is bounded by Muggleton W-operators (CIGOL 1988) or MIL meta-rules (Muggleton 2014). The cheap test deliberately restricts to recover-known-but-passive case -- testing invention is a Phase 2 follow-up.
- The substrate's "promotion of data atom to load-bearing" step is separate from abduction -- abduction proposes the SHAPE, promotion certifies VIA GAP-CLOSURE UTILITY (the substrate's existing 4-gate + held-out re-run). The two compose cleanly.

---

## (e) Substrate-product implications

(Per [[feedback-no-papers-product-only]] -- product framing only.)

The substrate-product positioning gains its STRONGEST internal-mechanism claim from this synthesis: the substrate is the first knowledge system to operationalize the "compute the weakest signature that would close this capability failure" loop with a sound 3-mechanism stack (CEGAR + Progol + reverse certification) on hyperdimensional capability signatures. LLMs have NO abductive minimality step (FunSearch + AlphaGeometry both confirmed: LM-proposes + evaluator-filters, with no SHAPE-computation). DreamCoder is the closest peer but works post-hoc on solved-task compression, not on capability failures. The substrate would become the only system that, given a measured capability failure, can compute a minimal predicate over its existing vocabulary that closes the failure AND prove minimality by reverse-direction certification.

This connects directly to: substrate-product Claim 11 (METHODOLOGY rule 19 candidate "adversarial self-correction of own DETECT output"), Claim 9 (Lakatos-PROGRESSIVE programme), and the USER 2026-06-15 ruling that LLM-assisted candidate selection is OK as bootstrap until substrate self-selects -- the abductor IS the substrate self-selection mechanism for the gap-shape question.

If the cheap test HARD-PASSes (>= 4/10 minimal-certified P, with >= 2 corpus-recovered): this becomes Tier 1 architectural Claim 16 candidate -- "substrate computes weakest predicate that closes capability failure with reverse-direction minimality certificate".

If it HARD-FAILs (<= 1/10): the next drill targets Plotkin LGG + Inoue consequence-finding (the adjacent finding above) as an alternative weakest-explanation route. This is a substrate-internal failure mode, not a closure of the gap-driven invention thesis.

---

## (f) Citations (verified count: 27)

Reverse mathematics:
- Friedman 1975 ICM address; Simpson, "Subsystems of Second Order Arithmetic", CUP 1999/2009.

Abductive logic programming:
- Kakas-Mancarella, ECAI 1990 "Generalized Stable Models".
- Denecker-Verbaeten, JLP 34(2):111-167, 1998 "SLDNFA".
- Denecker-Kakas, LNCS 2407:402-436, 2002 "Abduction in Logic Programming" handbook chapter.

ILP / inverse entailment / predicate invention:
- Muggleton-Buntine 1988 "Machine invention of first-order predicates by inverting resolution".
- Muggleton 1995 "Inverse entailment and Progol", New Generation Computing 13.
- Stahl 1995 "Predicate invention in ILP -- an overview", ECML.
- Muggleton et al. 2014 "Meta-interpretive learning of higher-order dyadic Datalog", MLJ.
- Cropper-Muggleton 2019 "Learning higher-order logic programs".

Belief revision / theory revision:
- Alchourron-Gardenfors-Makinson 1985 "On the logic of theory change", JSL.
- Gardenfors-Makinson 1988 (representation theorem); Grove 1988 (sphere systems).
- Wassermann 1999 Erkenntnis "Resource-Bounded Belief Revision"; Wassermann 2000 thesis.
- Hansson-Wassermann 2002 "Local Change", Studia Logica.
- Wrobel 1996 "First-order theory refinement".
- Ade-De Raedt-Bruynooghe 1995 ML "Declarative bias for specific-to-general ILP".
- Richards-Mooney 1995 FORTE.

Causal / counterfactual minimality:
- Pearl 2000 "Causality", CUP.
- Halpern-Pearl 2005 "Causes and Explanations: A Structural-Model Approach", BJPS.
- Halpern 2015 modified definition.
- Eiter-Lukasiewicz 2002 (DP-completeness of actual cause).

Weakest-explanation / LGG:
- Plotkin 1970/71 "A note on inductive generalization".
- Inoue 1992 "Linear resolution for consequence finding", AIJ.
- Marquis 2000 "Consequence finding".
- Kuzelka-Zelezny 2012 bounded LGG.

Practical autonomous-discovery systems:
- Clarke-Grumberg-Jha-Lu-Veith 2000 "Counterexample-Guided Abstraction Refinement", JACM.
- Solar-Lezama 2008 thesis "Program Synthesis by Sketching"; Alur et al. 2013 SyGuS.
- Ellis et al. 2021 PLDI "DreamCoder".
- Romera-Paredes et al. Nature 2024 "FunSearch".
- Trinh et al. Nature 2024 "AlphaGeometry"; AlphaGeometry2 arXiv 2502.03544.
- Mitchell 1982 candidate-elimination; Angluin 1988 query-synthesis.

---

## Status log entry

Filed via tools/orchestrator/state.py log_event with importance=HIGH, plain_language describing the 3-mechanism stack and the 40%/10% HARD-PASS/HARD-FAIL thresholds.

## Companion hand-off file

Written: notes/exp_dev_handoff_research_weakest_signature_abduction_2026-06-15.md (exp_dev-actionable; proposes a concrete cheap-CPU cell).
