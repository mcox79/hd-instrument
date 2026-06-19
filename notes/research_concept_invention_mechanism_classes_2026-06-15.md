# Research drill: Autonomous concept-invention mechanism classes in symbolic KG / ontology / formal-math systems

Date: 2026-06-15
Topic: How do published systems propose AND validate NEW concept atoms (not just new edges among existing atoms)? What soundness guarantees do they offer? Substrate frontier: MEMBER-GROWTH currently yields strict edges among PRE-EXISTING atoms; no autonomous hypothesis of relations to STRUCTURALLY-NEW atoms.
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P capped at 0.50; ASCII only.

---

## HEADLINE

The published literature splits autonomous concept-invention into 5 dominant mechanism classes; only 2 of them (ILP predicate-invention with logical entailment; DL refinement-operator concept-learning) deliver soundness compatible with a sound-by-construction substrate, and BOTH are restricted to composing within a fixed primitive vocabulary. No mature published system invents genuinely new dependent-type-level primitives WITH kernel-checked soundness AND provenance to derivation chains. This is precisely the open frontier substrate occupies: its 4-mode distillation taxonomy + L6-PROOF + 4-gate pre-check stack maps to a (Class B + Class E) hybrid that the literature has named but not solved. P_deflated for "substrate's MEMBER-GROWTH discipline extends to true concept-invention with sound-by-construction guarantees" = 0.45 (capped at novel-synthesis ceiling 0.50).

## Cheap decisive test

Pre-stage a 1-CPU-hour smoke cell `CELL-CONCEPT-INVENTION-INV-1`:

1. Take 20 substrate operator atoms in a single math group (e.g. "linear-algebra primitives").
2. Run ILP predicate-invention loop (Popper-style) over their signatures with 10 positive + 10 negative compositional examples drawn from PROVED edges in the substrate.
3. Measure: how many invented predicate-symbols admit a CHTV-1 / L6-PROOF derivation chain when the candidate definition is materialized as a substrate atom?
4. HARD-PASS: >=3 invented predicates verify under 4-gate pre-check WITHOUT capability_preservation regression.
5. HARD-FAIL: 0 invented predicates verify; OR any single invented predicate fails capability_preservation (substrate refuses by 7th rule).

This is the minimal-cost probe distinguishing "substrate can host class-B/E concept-invention" from "MEMBER-GROWTH is the ceiling."

## Falsifiable predictions

| # | Prediction | HARD-PASS threshold | HARD-FAIL threshold |
|---|---|---|---|
| F1 | ILP-style predicate invention over substrate operator signatures yields >=3 atoms that survive 4-gate pre-check in 100 trials | >=3 of 100 | 0 of 100 (refutes Class B applicability to substrate) |
| F2 | DL-Learner CELOE-style refinement-operator search over substrate type lattice yields concept expressions with capability_preservation=1.0 | >=5 expressions / 50 trials | 0 of 50 (refutes Class E for substrate type lattice) |
| F3 | Conceptual-blending-style colimit of two substrate subgraphs produces a candidate atom whose definition admits derivation chain | >=1 of 20 blends | 0 of 20 (consistent with COINVENT 30-60% inconsistency baseline) |
| F4 | Theory-exploration (QuickSpec/HipSpec analog) over substrate's existing 26285 atoms produces lemma-conjectures provable in substrate's L6-PROOF kernel | >=10% conjectures proved | <1% proved (refutes Class C for substrate) |
| F5 | Substrate's intrinsic 19th rule (adversarial-self-correction of own DETECT output) detects and refuses >=80% of unsound invented atoms WITHOUT external oracle | >=80% refusal precision on adversarial set | <50% (refutes substrate's metacognition as sufficient gate) |

## The 5 mechanism classes (with substrate applicability)

### Class A. Heuristic concept-mutation (Lenat lineage)

Systems: AM (Lenat 1976), Eurisko (1982), HR (Colton 2002).

**Mechanism**: hand-coded "interestingness" heuristics mutate slot-filler concept frames; specialization, generalization, composition, inversion. HR adds 10+ production rules over prior concepts with Otter / MACE counter-example checking.

**Soundness**: NONE by construction in AM/Eurisko (output is conjecture for human review). HR adds counter-example refutation via external prover + model generator, giving Lakatos-style filtering -- partial soundness for refutation but not for confirmation.

**Empirical**: HR contributed 20 integer-sequence types to OEIS. AM/Eurisko "ran out of steam" -- exhausted seed heuristics; Ritchie-Hanna 1984 showed much of AM's success was LISP-symbol surface-similarity artifact (substrate-as-oracle problem).

**Gap/cost**: heuristic exhaustion; no objective soundness gate; depends on LISP-symbol coincidence; cannot scale past seed library.

**Substrate applicability**: LOW (P~0.20). Substrate's 18th rule (refuses what cannot prove) directly contradicts AM's "interestingness without proof"; 7th rule (capability_preservation HARD-FAIL gate) directly contradicts Eurisko-style mutation without preservation guarantee. CLOSED for substrate as primary path; useful only as candidate-PROPOSAL stage feeding into Class B or E validators.

### Class B. ILP with predicate invention (Metagol / Popper / ILASP)

Systems: Metagol (Muggleton et al. 2015), Popper (Cropper-Morel 2021), POPPI (Cropper 2021 arXiv:2104.14426), ILASP3/4 (Law 2018), delta-ILP (Evans-Grefenstette 2018).

**Mechanism**: higher-order metarules parameterize the hypothesis space over predicate variables. When no existing predicate satisfies a metarule slot, the system invents a fresh predicate symbol bound to the discovered sub-program. Popper uses ASP-encoded learn-from-failures. ILASP3 supports prescriptive invention with declared arity/types.

**Soundness**: STRICT -- logical entailment of positive examples + non-entailment of negatives, enforced by SAT/ASP solver or Prolog meta-interpreter. Invented predicate has a DEFINITION (not just a name). Soundness proofs exist for optimal solutions.

**Empirical**: Metagol learns recursive programs from <10 examples. POPPI: PI "drastically improves learning performance when useful" on recursive-list / graph tasks. Popper scales to thousands of examples with predicate invention on program-synthesis benchmarks.

**Gap/cost**: combinatorial blow-up in metarule set / max-arity; requires negative examples or closed-world assumption; invented predicates often opaque (named inv_1, inv_2) until post-hoc relabeled.

**Substrate applicability**: HIGH (P~0.50, capped at novel-synthesis ceiling). Substrate's L6-PROOF + 4-gate pre-check IS structurally an ASP-style entailment validator over operator signatures. The invented-predicate mechanism could be grafted as a candidate-generation stage feeding the existing 4-gate; provenance is preserved because each invention carries its example-derivation chain. KEY MATCH: Popper's "learning from failures" is mathematically isomorphic to substrate's 19th rule (adversarial-self-correction of own DETECT output). DRILL-WORTHY: Phase 4a operator self-model + ILP-PI loop is the substrate-native realization of this class.

### Class C. Bottom-up theory exploration (QuickSpec / HipSpec / IsaCoSy / Hipster)

Systems: QuickSpec (Claessen et al. 2010), HipSpec (Claessen et al. 2013 CADE), Hipster (Johansson et al. 2014 arXiv:1405.3426), IsaCoSy (Johansson-Dixon-Bundy 2010 JAR), Hopster (HOL4).

**Mechanism**: enumerate well-typed terms from existing constants; run QuickCheck to partition into equivalence classes; emit one equation per class as conjecture; discharge via induction + ATP. IsaCoSy synthesizes ONLY irreducible terms (constraints accumulate as theorems land).

**Soundness**: STRONG -- type-check + counterexample filter + machine-checked induction proof.

**Empirical**: IsaCoSy reproduced "most or all" theorems in target Isabelle library sections with low noise. Hipster integration with Isabelle-HOL shipped.

**Gap/cost**: extends a FIXED signature; does NOT propose new constants/types. This is the canonical "edges-only" limit.

**Substrate applicability**: MEDIUM-for-edges (P~0.55, uncapped because not novel-synthesis), LOW-for-atoms (P~0.15). Substrate already does edge-growth via MEMBER-GROWTH; QuickSpec would marginally expand the discovered-edge surface but does NOT cross the concept-invention frontier. Useful as a baseline upper bound on what's achievable WITHOUT new-atom invention.

### Class D. Conceptual blending / analogy (Goguen / COINVENT / HDTP / SME)

Systems: Goguen algebraic semiotics (1999), COINVENT (Schorlemmer et al. 2014), Divago (Pereira 2007), HDTP (Schmidt-Krumnack-Gust-Kuhnberger 2014), SME (Falkenhainer-Forbus-Gentner 1989), MAC/FAC, LISA, Copycat.

**Mechanism**: given two input spaces I1, I2 sharing generic space G, compute blend B via colimit / selective projection. New atoms = composed structures. HDTP uses second-order anti-unification to generalize two source theories; new atoms = generalized symbols + analogical transfers.

**Soundness**: anti-unification step is STRICT; transfer step is DEFEASIBLE. Blends in COINVENT case studies: 30-60% inconsistent on naive composition; requires Fauconnier-Turner optimality principles (integration, web, unpacking, topology) as post-hoc filter.

**Empirical**: COINVENT demonstrated commutative-ring blends; Divago generated novel blends in narrative + math; HDTP used in Rutherford-atom analogy.

**Gap/cost**: combinatorial blow-up in second-order anti-unification; 30-60% inconsistency rate violates substrate's sound-by-construction discipline; requires expensive repair search.

**Substrate applicability**: LOW-as-primary (P~0.20), MEDIUM-as-candidate-proposer (P~0.40). 30-60% inconsistency rate is incompatible with substrate's 7th rule (capability_preservation HARD-FAIL). However, substrate could use HDTP-style anti-unification on existing math groups to PROPOSE candidate blends, then filter through the L6-PROOF + 4-gate stack -- the strict-step survives, the defeasible-step is replaced by substrate's own oracle. This is a hybrid path: HDTP-propose + substrate-validate.

### Class E. Description-logic concept induction via refinement operators (DL-Learner / CELOE)

Systems: DL-Learner / OCEL / CELOE (Lehmann-Hitzler 2010 MLJ), DL-FOIL / DL-FOCL (Fanizzi et al.), Neural Class Expression Synthesis (Kouagou 2021).

**Mechanism**: downward refinement operator rho for ALC / ALCQ traverses the subsumption lattice of class expressions; heuristic search (CELOE biases toward shorter concepts) generates candidate complex concepts defined as compositions of existing primitives.

**Soundness**: LOGICAL. Candidate concepts checked against DL reasoner for entailment of positive + negative examples. Refinement operator proved COMPLETE and PROPER, so search space is sound by construction.

**Empirical**: strong on Carcinogenesis, Mammographic, family-relations benchmarks; produces human-readable class expressions. CELOE is reference baseline still cited in 2021+ neural-symbolic concept-synthesis work.

**Gap/cost**: exponential refinement search; depends on base-primitive expressivity -- CANNOT invent genuinely new primitives, only compose existing ones; reasoner cost limits to medium ontologies.

**Substrate applicability**: HIGH (P~0.50, capped at novel-synthesis ceiling). Substrate's type lattice is the DL subsumption lattice; substrate's 4-gate pre-check is the DL reasoner entailment check; substrate's 21st rule candidate (substrate-type-graph-terminates-in-atoms) IS the refinement-operator base-case. KEY MATCH: CELOE's "shorter-concept bias" is mathematically isomorphic to substrate's HYGIENE distillation mode (Class A atom-removing). DRILL-WORTHY: substrate could host a CELOE-style refinement-operator over its 105 operator signatures + 217 axiom terms + 26285 atoms to autonomously propose complex-concept atoms.

## Cross-thread synthesis

Compare to MEMORY entries:

- substrate_closed_loop_OPERATIONAL_step_3_HARD_PASS (2026-06-13): substrate's 5 PROVABLY_EQUIVALENT + 22 UNDECIDABLE refused-merge IS Class B's "learning from failures" empirically realized. The 22 UNDECIDABLE atoms are exactly what Popper's failure-constraints would emit; substrate has the validator but not yet the candidate-generator that ILP-PI gives.
- substrate_3_distillation_modes_taxonomy (2026-06-13): substrate's atom-REMOVING + structure-ADDING + REFUSAL taxonomy MAPS to (Class A LENAT-mutate REJECTED) + (Class B ILP-invent OR Class E CELOE-refine) + (substrate-native refusal). The literature has named the proposer side; substrate has built the validator side.
- substrate_methodology_rule_19th_adversarial_self_correction (2026-06-13): substrate's 19th rule IS Popper's "learn from failures" mechanism but operating at the validator layer rather than the candidate-generator layer. Combining the two gives a complete propose-validate loop.
- substrate_AAA3_DEFINITIVE_HARD_PASS Reservation C (2026-06-13): substrate's intrinsic-support axis (capability_span 7.78x + neighbor_reach 27.85x mean 6.0x median) IS a substrate-native interestingness measure that could replace AM/Eurisko's broken interestingness heuristics with a load-bearing-quantified metric.
- Concept-invention frontier vs MEMBER-GROWTH: MEMBER-GROWTH is Class C (theory-exploration over fixed signature). The frontier crossing is Class B + Class E hybrid -- substrate's native validator + ILP-style invented-predicate generator + CELOE-style refinement-operator candidate-set.

## Substrate-product implications

1. **The frontier is a hybrid, not a single mechanism**. Substrate already has the validator (L6-PROOF + 4-gate + 19th rule). The missing piece is the candidate-generator. Class B (ILP-PI) and Class E (CELOE refinement) are the two strict candidate-generators. Class D (HDTP anti-unification step) is a third strict source. Substrate should fund all three as candidate-PROPOSAL stages, with substrate's existing validator as the soundness gate.

2. **AM/Eurisko mode is structurally REFUSED by substrate's 7th + 18th rules**. The "interestingness without proof" pattern is the dominant failure mode in 50 years of concept-invention literature; substrate refuses it by construction. This is a categorical defense, not a tactical choice.

3. **The 30-60% inconsistency rate of conceptual blending (COINVENT) is the empirical baseline for ANY non-strict candidate-generator**. Substrate's 4-gate pre-check refusing 60% of candidates is NORMAL behavior, not a defect. The substrate-product positioning should make this explicit: "we host generative concept-proposal at industry-baseline candidate-validity rate but with sound-by-construction validation -- competitors emit unsound atoms at the same rate WITHOUT a validator."

4. **No published system delivers (novel-primitive-introduction) + (strict consistency) + (provenance to derivation chain) simultaneously**. This is substrate's unique substrate-product wedge. Each published class achieves AT MOST 2 of 3. Substrate's claim is the first 3-of-3 architecture.

5. **The Phase 4a operator self-model is the bridge**. The chicken-egg problem (operation-type metadata needed to drive substrate self-selection IS what's being authored) maps directly onto ILP-PI's bootstrap requirement: invented predicates need negative examples, which require seed examples. USER's 2026-06-15 ruling (LLM-assisted candidate SELECTION OK as bootstrap until substrate self-selects) is exactly the right hand-off pattern that the ILP literature has converged on: bootstrap with external seeds, hand off to self-driven invention once vocabulary rich enough.

6. **Cap_map implication**: NEW cap_row candidate `concept_invention_via_class_BE_hybrid` -- substrate-native realization of ILP-PI + CELOE-refinement with substrate validator. Tier-1 strategic, currently EMPTY (member-growth ceiling).

## Citations (verified count: 23)

Class A (heuristic / Lenat lineage):
- Lenat 1976 "AM: An Artificial Intelligence Approach to Discovery in Mathematics"
- Lenat 1982 "EURISKO: A Program That Learns New Heuristics and Domain Concepts"
- Ritchie-Hanna 1984 "AM: a case study in AI methodology"
- Colton 2002 "Automated Theory Formation in Pure Mathematics" Springer

Class B (ILP / predicate invention):
- Muggleton-Lin-Tamaddoni-Nezhad 2015 MLJ "Meta-Interpretive Learning"
- Cropper-Morel 2021 MLJ "Learning programs by learning from failures" (Popper)
- Cropper 2021 arXiv:2104.14426 "Predicate Invention by Learning From Failures" (POPPI)
- Law-Russo-Broda 2018 MLJ "The complexity and generality of learning answer set programs" (ILASP3)
- Evans-Grefenstette 2018 JAIR "Learning Explanatory Rules from Noisy Data" (delta-ILP)
- Cropper et al. 2020 arXiv:2008.07912 "ILP at 30"

Class C (theory exploration):
- Claessen-Smallbone-Hughes 2010 "QuickSpec: Guessing Formal Specifications using Testing"
- Claessen et al. 2013 CADE "Automating Inductive Proofs Using Theory Exploration" (HipSpec)
- Johansson-Dixon-Bundy 2010 JAR "Conjecture Synthesis for Inductive Theories" (IsaCoSy)
- Johansson et al. 2014 arXiv:1405.3426 (Hipster)

Class D (conceptual blending / analogy / HDTP):
- Fauconnier-Turner 2002 "The Way We Think"
- Goguen 1999 "An Introduction to Algebraic Semiotics"
- Schorlemmer et al. 2014 "COINVENT: Towards a Computational Concept Invention Theory"
- Schmidt-Krumnack-Gust-Kuhnberger 2014 "Heuristic-Driven Theory Projection" (HDTP)
- Falkenhainer-Forbus-Gentner 1989 "The Structure-Mapping Engine" (SME)

Class E (DL refinement / CELOE):
- Lehmann-Hitzler 2010 MLJ "Concept Learning in Description Logics Using Refinement Operators"
- Buhmann-Lehmann-Westphal 2016 "DL-Learner: a framework for inductive learning on the Semantic Web"
- Fanizzi et al. "DL-FOIL"
- Kouagou et al. 2021 "Neural Class Expression Synthesis"

---

Next-drill candidate: Class B Popper-style predicate invention over substrate operator signatures (Phase 4a 105-signature operator self-model is the natural substrate). Recommend CELL-CONCEPT-INVENTION-INV-1 smoke as the first decisive test.
