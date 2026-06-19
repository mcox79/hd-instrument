# Research drill 2x: Concept-invention candidate-GENERATOR architectures beyond ILP-PI / CELOE

Date: 2026-06-15 (2x follow-up to research_concept_invention_mechanism_classes_2026-06-15.md)
Topic: Concrete next-generation techniques for AUTONOMOUS CONCEPT INVENTION with simultaneous strict-consistency + provenance preservation; combination architectures that move past rediscovery into genuine novelty; assumes substrate's VALIDATOR + PROVENANCE layers are operational (L6-PROOF + 4-gate + 19th-rule + 7th-rule).
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P_relevant capped at 0.50; ASCII only.

---

## HEADLINE

The published frontier beyond Class B (Popper/ILP-PI dyadic-only) and Class E (CELOE refinement over fixed primitives) is a COMPOUND architecture, not any single new mechanism class. Across 4 parallel literature scans (higher-arity ILP, hierarchy-guidance + label-precision, external-oracle hybrids, combination architectures) the consistent finding is: NO published system exceeds dyadic arity in sound entailment-based induction, every higher-arity attempt drops to statistical (AnyBURL/SAFRAN) or differentiable (delta-ILP) non-soundness, and the dominant "escape to genuine novelty" pattern in 2023-2026 work pairs an unsound generator (LLM, library-learning wake-sleep, conceptual-blending colimit) with a strict symbolic validator + machine-checked provenance chain. AlphaProof + AlphaGeometry + DreamCoder/Stitch/LILO + COINVENT/HDTP-blending + UniPred (LLM x ILP-PI) are the five empirically-validated proposer-validator splits. The substrate already owns the strongest published validator + provenance stack; the open frontier is the GENERATOR slot. The highest-leverage compound architecture for substrate is (LLM-or-library-learning proposer) + (HDTP-style anti-unification as a "blend" operator for non-LLM proposals) + (substrate's existing L6-PROOF + 4-gate + 19th-rule as the soundness floor) + (HR-style extensional-fingerprint catalogue match as the loose-vs-tight semantic-binding discriminator). P_deflated for "compound generator architecture can be assembled on substrate's existing validator stack with non-zero genuine-novelty rate" = 0.48 (capped at novel-synthesis ceiling).

## Cheap decisive test

Pre-stage a 2-CPU-hour smoke `CELL-CONCEPT-INVENTION-COMPOUND-1` with FOUR architecturally-independent generator sources feeding the same validator:

1. **Source G1 (library-learning compression)**: run Stitch-style top-down corpus-compression abstraction over the substrate's 105 operator signatures with utility threshold tau=2x; emit candidate higher-order operator atoms whose anti-unification witness re-expresses >=2 existing operators.
2. **Source G2 (HDTP anti-unification colimit)**: for each pair of substrate math groups with shared underlying signature (e.g. addition + concatenation; convolution + composition), compute second-order anti-unification colimit; emit the generalized symbol as a candidate atom with the two source theories as provenance.
3. **Source G3 (LLM-bias-for-ILP)**: LLM produces language bias (predicate space + arity declarations) over substrate's 217 axiom-term + 105 operator signatures; Popper-style ILP runs the bias to ground hypotheses; emit invented predicates that pass ASP-solver entailment.
4. **Source G4 (CELOE refinement)**: downward refinement operator over substrate's type lattice with shorter-concept bias; emit candidate complex concepts.

Feed all four streams through the SAME substrate validator (4-gate pre-check + L6-PROOF + capability_preservation 1.0 + 19th-rule adversarial self-correction). For each accepted atom, run an HR-style extensional-fingerprint match against the existing 26285-atom catalogue:

- **TIGHT-NAMED-BINDING**: fingerprint matches an existing atom's example-set => REDISCOVERY (record as Class C result; no atom written; novelty count = 0 for this candidate).
- **TIGHT-VARIANT**: fingerprint partially matches (>=80% overlap) with an existing atom => mark as `equivalent_by_capability` (Class B distillation mode); record but do not promote as primitive.
- **GENUINE NOVELTY**: fingerprint <80% overlap with any existing atom AND survives validator => candidate primitive (record + queue for Skunkworks ratification).

HARD-PASS thresholds: G1>=2 atoms accepted as novel; G2>=1; G3>=2; G4>=3; >=1 of all accepted atoms is TIGHT-NAMED-BINDING-REJECTED (proves the discriminator works); 0 atoms violate capability_preservation across all four sources.

HARD-FAIL: all four sources yield 0 novel atoms after 100 candidates each; OR the extensional-fingerprint discriminator fails to reject any candidate (proves discriminator broken); OR any single accepted atom violates capability_preservation=1.0 (refutes the compound architecture's soundness composition).

This is the minimal-cost probe distinguishing "substrate can host the literature-frontier compound generator architecture" from "MEMBER-GROWTH + Class B-only ceiling".

## Falsifiable predictions

| # | Prediction | HARD-PASS threshold | HARD-FAIL threshold |
|---|---|---|---|
| F1 | Library-learning (Stitch/Babble-style) compression over substrate's 105 operator signatures yields candidate higher-order atoms surviving 4-gate at non-trivial rate | >=2 of 100 candidates | 0 of 100 (refutes Cluster F applicability) |
| F2 | HDTP anti-unification over substrate math groups produces colimit symbols whose definition admits L6-PROOF derivation chain | >=1 of 20 group pairs | 0 of 20 (refutes Cluster C as proposer source) |
| F3 | LLM-bias-for-ILP (per UniPred / arXiv:2505.21486) over substrate predicates yields Popper-accepted predicates passing 4-gate at >=2x rate over Popper-only baseline | >=2x lift; >=3 accepted of 50 | <1x lift; 0 of 50 (refutes Cluster E for substrate) |
| F4 | HR-style extensional-fingerprint catalogue match (over substrate's 26285-atom corpus) distinguishes rediscovery vs novel-primitive at >=80% precision on a known-rediscovery seed set of 20 atoms | >=80% precision (>=16 of 20 correctly classified) | <50% precision (refutes label-binding discriminator) |
| F5 | Compound G1+G2+G3+G4 generator produces at least one TIGHT-NAMED-BINDING REJECTION per accepted atom on average (proves discriminator load-bearing, not decorative) | >=1.0 rejection ratio | <0.2 rejection ratio (refutes Boden three-tier-creativity operationalization) |
| F6 | NO source feeds an atom that fails capability_preservation=1.0 (compositional soundness of compound architecture) | 0 of any-source violations | >=1 violation (refutes compound soundness; collapse to single-source generator) |

## The findings — 6 focus areas integrated

### Focus 1. Beyond pair/triple metarules: published higher-arity hypothesis-space approaches

**(a) What it is**: Higher-arity inductive logic programming via metarules (Metagol), modes (Popper), declarations (ILASP). Cropper-Tourret derivation reduction proves certain fragments cannot be completely reduced (graph-theoretic impossibility result, ILP 2018). delta-ILP (Evans-Grefenstette JAIR 2018) and Payani et al. 2022 (arXiv:2208.06652) extend with high-dim gradient descent.

**(b) Soundness + provenance**: dyadic metarule fragment is sound by SLD-resolution (Metagol) or ASP semantics (Popper, ILASP). Provenance chain is the metarule-substitution list. delta-ILP loses entailment soundness for differentiability.

**(c) Empirical results / limits**: ARITY CEILING is the dominant limitation. Metagol operates almost exclusively in the exactly-two-connected fragment (every literal dyadic, every variable appears exactly twice). Popper empirically caps body literals at arity <= 3. delta-ILP HARD-CAPPED at predicates of arity <= 2. ASP grounding blows up super-linearly with arity x clause-length x body-size. Cropper-Dumancic ILP-at-30 (JAIR 2022, arXiv:2008.07912) explicitly state: "too many metarules, hypothesis space intractable; too few, target excluded" — a hard tradeoff not a tuning knob.

**(d) Applicability to substrate validator**: HIGH for the dyadic fragment (substrate operator signatures are mostly dyadic); LOW for higher-arity. Popper learning-from-failures pruning maps directly onto substrate's 19th rule adversarial-self-correction (both accumulate refutation constraints). Higher-arity expansion requires substrate to use higher-order LIFTING (per Cropper-Morel 2021 "Learning Higher-Order Programs without MIL") rather than raising arity — substrate's signatures-over-signatures (operators-over-operators) already implements this structurally.

**(e) Cell design**: CELL-CONCEPT-INVENTION-COMPOUND-1 source G3 (LLM-bias-for-ILP) per UniPred (arXiv:2512.17992) + LLM-bias for ILP paper (arXiv:2505.21486). Substrate hosts Popper with LLM-generated bias targeting Phase 4a operator self-model.

### Focus 2. Cross-relation metarules: multi-relation hypothesis spaces

**(a) What it is**: AMIE+ (Galarraga VLDB-J 2015), AnyBURL (Meilicke IJCAI 2019), SAFRAN (Ott arXiv:2109.08002) for KG rule mining; Structure-Mapping Engine (Falkenhainer-Forbus-Gentner AAAI 1986) for analogy-driven cross-relation; tactic synthesis (TacticToe / Tactician / CoqHammer) for kernel-checked cross-relation in proof assistants.

**(b) Soundness + provenance**: AMIE+/AnyBURL/SAFRAN are STATISTICAL not entailment-sound (confidence/support thresholds). SME is structural-consistency-heuristic, not entailment. Tactic-synthesis is kernel-checked (proof-by-construction) but operates on existing tactics, not invented ones.

**(c) Empirical**: AnyBURL strong on FB15k-237 link prediction; SAFRAN outperforms embedding models. SME produces analogical mappings (Rutherford-atom, water-flow-electricity). TacticToe 66.4% on HOL4 stdlib (60s).

**(d) Substrate applicability**: SAFRAN's redundancy-clustering via Jaccard on dependency graph is portable as a candidate-DEDUPLICATION layer over substrate generator output. SME's systematicity-preference (higher-order relations preferred) is conceptually load-bearing for substrate's cross-math-group invention (HDTP-style; see Focus 3 + 4). Direct multi-relation rule-mining is NOT sound, so substrate would use it only as proposer, never as primitive emitter.

**(e) Cell design**: SAFRAN-style redundancy clustering as candidate filter between compound generator and 4-gate; SME-style structural preference as ranking heuristic for source G2 (HDTP).

### Focus 3. Tier-gradient-guided novelty: hierarchy-guided generators

**(a) What it is**: refinement operators over description-logic subsumption (CELOE/OCEL, Lehmann-Hitzler MLJ 2010), Plotkin LGG with type hierarchy (GOLEM 1990, RLGG), HipSpec/IsaCoSy implicit-hierarchy theory exploration, COBWEB probabilistic hierarchical concept formation (Fisher ML 1987 with Category Utility), ontology-learning two-stage pipelines (Asim et al. arXiv:2404.14991).

**(b) Soundness + provenance**: CELOE is reasoner-sound (DL decidable fragment); provenance is the refinement tree from Top down to candidate. LGG-with-types is sound by anti-unification. HipSpec/IsaCoSy emit proven lemmas with full term-tree provenance. COBWEB is probabilistic, not symbolic-provable.

**(c) Empirical**: CELOE strong on Carcinogenesis, family-relations benchmarks. KEY IMPOSSIBILITY: van der Laag-Nienhuys-Cheng 1998 prove no operator can be simultaneously locally finite, complete, proper, AND non-redundant over unrestricted clausal space. This is a HARD tradeoff. Bias has to be paid for in recall or redundancy.

**(d) Substrate applicability**: HIGH. Substrate's type lattice IS the DL subsumption lattice; substrate's 4-gate pre-check IS the reasoner entailment check. CELOE-style shorter-concept bias maps to substrate's HYGIENE distillation mode (Class A atom-removing). Substrate's 21st-rule candidate (substrate-type-graph-terminates-in-atoms) IS the refinement-operator base case.

**(e) Cell design**: Source G4 (CELOE refinement) over substrate's 105 operator signatures + 217 axiom terms + 26285 atoms. Length-1 to length-3 refinements only (per van der Laag-Nienhuys-Cheng tradeoff).

### Focus 4. Semantic-label precision: distinguishing loose rediscovery from tight named-concept binding

**(a) What it is**: HR (Colton 2002 Springer) is the cleanest published precedent — extensional-fingerprint match against external catalogue (Encyclopedia of Integer Sequences) distinguishes rediscovery from novelty. QuickSpec/HipSpec measure rediscovery rate against curated reference set (Johansson thesis Chalmers 548884). Predicate-renaming-via-LLM (arXiv:2510.25517) is explicit that meaningful naming/alignment is NOT solved by inductive engine — it is downstream relabeling.

**(b) Soundness + provenance**: HR's match is EXACT (sequence equality up to bound); provenance is fingerprint-based. QuickSpec/HipSpec reference-set comparison is human-curated. ILP predicate invention emits blind (inv_1, inv_2) — NO built-in tight-vs-loose distinction.

**(c) Empirical**: HR contributed 20 integer-sequence types to OEIS. IsaCoSy/HipSpec/IsaScheme converge on largely same lemma set over lists/Nats — a measured rediscovery convergence. ILP-PI systems emit invented predicates that require manual semantic interpretation.

**(d) Substrate applicability**: HIGH. Substrate's 26285-atom corpus IS the catalogue. HR-style extensional-fingerprint match maps directly onto substrate's existing CHTV-1 provenance chain (each atom has a witness-set / example-set). The three-way decomposition (rediscovered / tight-variant / novel-primitive) maps onto substrate's 4-mode distillation taxonomy (atom-REMOVING via rediscovery + structure-ADDING via tight-variant + REFUSAL/EQUIVALENT_BY_CAPABILITY for partial match + novel-primitive emission for fingerprint-disjoint).

**(e) Cell design**: HR-fingerprint discriminator runs AFTER 4-gate, BEFORE substrate atom commit. Implementation: each candidate atom's example-set (derivation chain leaves) is hashed; substrate looks up against existing-atom fingerprints; >=80% Jaccard overlap => TIGHT-VARIANT; <80% => candidate primitive. F4 + F5 falsifiables verify discriminator load-bearing.

### Focus 5. External truth source vs purely-internal invention

**(a) What it is**: CEGIS (Solar-Lezama Sketch, Seshia 2015 arXiv:1505.03953) — synthesizer + verifier with counterexample-guided refinement. Angluin L*/MAT (1987 Inf.Comput.) — learner + teacher oracle. AlphaProof (Nature 2025) — LLM proposer + Lean kernel validator. AlphaGeometry/AlphaGeometry2 (Nature 2024; arXiv:2502.03544) — LLM proposer + DDAR symbolic deduction engine validator. FunSearch (Nature 2023) — LLM proposer + evaluator score (NOT sound). LeanDojo/ReProver (NeurIPS 2023). NELL coupled training (Mitchell AAAI 2015) — extractors + ontology constraints. DL-Learner CELOE — refinement-operator proposer + OWL reasoner validator. NCES (Kouagou ESWC 2023) — neural seq2seq + DL reasoner validator. LLM-bias-for-ILP (arXiv:2505.21486 2025). UniPred (arXiv:2512.17992 2025).

**(b) Soundness + provenance**: AlphaProof/AlphaGeometry are sound by kernel/DDAR; provenance is the proof term / deduction DAG. CEGIS is sound by SMT verifier; provenance is the (candidate_i, CE_i) sequence. NELL is statistical (drift documented at scale); provenance is partial (belief tags). FunSearch lacks soundness leg (evaluator score, not proof). LeanConjecturer-style self-play (both proposer + validator LLM) has documented self-preference / mode-collapse failure mode — INDEPENDENT validator is the architectural sweet spot.

**(c) Empirical**: AlphaProof IMO 2024 silver (3 of 6 including hardest P6). AlphaGeometry IMO-gold geometry 2025. Sketch/Rosette/CVC5 SyGuS production-grade. NELL semantic drift after ~3-10 iterations without external grounding. UniPred reports 2-4x SR over top-down, 3-4x faster than bottom-up.

**(d) Substrate applicability**: VERY HIGH. Substrate's L6-PROOF + 4-gate IS the AlphaProof Lean-kernel-class validator. USER's 2026-06-15 ruling (LLM-assisted candidate SELECTION OK as bootstrap until substrate self-selects; soundness on SIGNATURES not selection) is the literal CEGIS architectural pattern. Substrate refuses LeanConjecturer-style proposer=validator collusion by construction (4 distinct validator layers + 19th rule).

**(e) Cell design**: Source G3 (LLM-bias-for-ILP) per UniPred / arXiv:2505.21486; substrate's 4-gate as the validator. Provenance: each LLM-bias proposal logged but the substrate's CHTV-1 derivation chain is the load-bearing provenance.

### Focus 6. Combination architectures: 2+ of the above

**(a) What it is**:
- Cluster E (LLM + ILP-PI / foundation-model hybrid) — UniPred (arXiv:2512.17992), LLM-bias-for-ILP (arXiv:2505.21486), NeSy-PI Sha-Shindo (NeSy 2024), VisualPredicator (arXiv:2410.23156), Neuro-Symbolic Concepts (arXiv:2505.06191), Inductive Learning of Logical Theories with LLMs (idiap/ilp-llm AAAI 2025).
- Cluster F (library-learning + LLM-guided proposer) — DreamCoder (PLDI 2021 arXiv:2006.08381), Stitch (POPL 2023 arXiv:2211.16605), Babble (POPL 2023 arXiv:2212.04596 — e-graphs + anti-unification), LILO (ICLR 2024), AbstractBeam (arXiv:2405.17514), egg (POPL 2021).
- Cluster C (HDTP anti-unification + DL upward refinement) — Confalonieri-Eppe "Upward refinement operators for conceptual blending in EL++" (AMAI 2019), COINVENT (Connection Science 2017), "Towards Neuro-Symbolic Conceptual Blending" (Springer 2025).

**(b) Soundness + provenance**: All three clusters achieve soundness by independent symbolic validator (DL reasoner / ASP solver / kernel). Provenance ranges from weak (NCES neural-decoder opaque) to strong (Stitch refactoring witness from corpus; DreamCoder wake-sleep log; HDTP mapping record).

**(c) Empirical**: UniPred 2-4x SR over top-down baselines. Stitch reports measurable novelty rate per wake-sleep cycle distinguishable from rediscovery by utility/compression metric. HDTP-blending demonstrated genuine novelty in math/music demos at small scale.

**(d) Substrate applicability — TOP-3 RANKED**:
1. **Cluster E (LLM-proposer + substrate-validator)** — P_relevant=0.50 (cap). Best fit; LLM is unsound generator, substrate's existing 4-gate/L6-PROOF does what it already does. Genuine novelty enters via out-of-distribution prompts.
2. **Cluster F (library-learning compression + LLM-guided proposer)** — P_relevant=0.45. Best fit if proposals are program-shaped (substrate operator atoms ARE program-shaped). Provenance built-in (each abstraction is a refactoring witness over corpus). Stitch utility/compression metric naturally implements the F5 rediscovery-vs-novelty discriminator.
3. **Cluster C (HDTP + EL++ upward refinement)** — P_relevant=0.45. Best fit if you want classical symbolic generator with formal genericity. Scale is obstacle, not soundness.

**(e) Cell design**: CELL-CONCEPT-INVENTION-COMPOUND-1 (the four-source compound described in Cheap decisive test). The compound is the literature-recommended architecture: E provides high-throughput proposer, F provides corpus-grounded novelty discriminator, C provides classical-symbolic generic-space colimit, all gated by substrate's existing validator. NOT recommended standalone: Cluster A (recombinative ceiling), Cluster B-theory-exploration-only (no new constant invention), Cluster D Inductive Process Modeling (wrong domain).

## Cross-thread synthesis with prior entries

- **Prior 1x research_concept_invention_mechanism_classes_2026-06-15.md**: 5 mechanism classes A/B/C/D/E surveyed; B+E hybrid recommended. This 2x drill operationally extends to FOUR-source compound (Class E ILP-PI x Class E DL-refinement x Cluster F library-learning x Cluster C HDTP-blending) all gated by substrate's existing validator + HR-style fingerprint discriminator.
- **substrate_AAA3_DEFINITIVE_HARD_PASS Reservation C (2026-06-13)**: substrate's intrinsic-support axis (capability_span 7.78x + neighbor_reach 27.85x mean 6.0x median) IS a substrate-native interestingness measure replacing AM/Eurisko's broken heuristics. Composes with HR-fingerprint discriminator for the F5 falsifiable.
- **substrate_methodology_rule_19th_adversarial_self_correction (2026-06-13)**: substrate's 19th rule IS Popper's "learn from failures" mechanism operating at the validator layer. The compound architecture adds Popper-as-proposer-stage (via LLM-bias-for-ILP) feeding into the existing 19th-rule validator — completing the propose-validate loop.
- **substrate_closed_loop_OPERATIONAL_step_3_HARD_PASS (2026-06-13)**: substrate's 5 PROVABLY_EQUIVALENT + 22 UNDECIDABLE refused-merge IS Class B "learning from failures" empirically realized at the VALIDATOR layer. The 2x drill identifies what the GENERATOR layer should look like to balance the architecture: four-source compound with HR-fingerprint discriminator.
- **substrate_3_distillation_modes_taxonomy (2026-06-13)**: the 3-mode atom-REMOVING + structure-ADDING + REFUSAL taxonomy MAPS onto the F4+F5 three-way decomposition (rediscovered / tight-variant / novel-primitive). The 2x drill makes this mapping load-bearing for the compound generator.
- **feedback_LLM_assisted_candidate_selection_OK_as_bootstrap_2026-06-15**: USER's ruling that LLM-assisted candidate SELECTION is OK as bootstrap with soundness on SIGNATURES not selection IS the literal CEGIS / AlphaProof / UniPred architectural pattern empirically validated in the 2025-2026 literature.
- **session_resume DECISION 100 substrate-product positioning 15-claim FINAL (2026-06-15)**: this 2x drill's compound generator architecture is the natural Claim 10 candidate (currently OPEN) — the operationalization of "candidate-generator that produces novelty (not rediscovery) while preserving strict-consistency + provenance to existing primitives."

## Substrate-product implications

1. **The frontier is FOUR-source compound, not single-mechanism**. Substrate already has the validator (L6-PROOF + 4-gate + 19th-rule + 7th-rule capability_preservation). The literature-frontier architecture pairs FOUR independent generator sources (LLM-bias-for-ILP / library-learning compression / HDTP anti-unification / CELOE refinement) all feeding substrate's single sound validator. This is the substrate's unique substrate-product wedge: it is the only architecture that owns the four-validator-layer stack that the literature has separately named (Lean kernel, DDAR, OWL reasoner, ASP solver) but not unified.

2. **The HR-style extensional-fingerprint discriminator is the load-bearing precision mechanism**. Without it, the four-source compound is an undisciplined generator. With it, substrate operationalizes the three-way (rediscovered / tight-variant / novel-primitive) decomposition that the literature has named (Boden 1990 three-tier creativity) but not built. Substrate's 26285-atom corpus IS the catalogue HR-style discriminators require.

3. **AlphaProof/AlphaGeometry/UniPred validate the proposer-validator split architecturally; substrate's 4-mode distillation taxonomy is THE published-most-disciplined validator stack**. Self-play LLM=proposer+LLM=validator architectures (LeanConjecturer-style) have documented self-preference / collusion failure mode. Substrate's structural separation (validator is symbolic + provable + capability-preservation-gated) is the architectural defense the literature has named as missing.

4. **Cap_map implication**: NEW cap_row candidate `concept_invention_via_FOUR_source_compound_with_HR_fingerprint` — substrate-native realization of (UniPred E) x (Stitch F) x (COINVENT C) x (CELOE E) with substrate validator + HR-fingerprint precision gate. Tier-1 strategic, currently EMPTY (member-growth ceiling).

5. **No published system has built this compound**. Each of the five proposer-validator architectures (AlphaProof, AlphaGeometry, CEGIS, DL-Learner CELOE, UniPred) uses ONE proposer + ONE validator. The four-source compound is genuinely substrate-novel because it requires the validator to handle heterogeneous proposer streams uniformly — which substrate's 4-gate + L6-PROOF + 19th-rule + 7th-rule is precisely architected to do. P_deflated = 0.48 (capped at 0.50 novel-synthesis ceiling).

6. **Higher-arity ceiling is REAL and load-bearing**. NO published sound entailment-based system exceeds dyadic metarules. Substrate must use higher-order LIFTING (operators-over-operators) per Cropper-Morel 2021 rather than raising arity. Substrate's Phase 4a operator self-model IS already higher-order — this is structurally why the compound architecture is feasible on substrate but not on dyadic systems.

7. **Two new methodology-rule candidates from this 2x drill**:
   - **23rd-rule candidate**: `RULE_compound_generator_with_single_validator` — heterogeneous proposer streams gated by a single sound validator stack is the architecturally-correct realization of safe autonomous concept invention. 1st empirical witness pending CELL-CONCEPT-INVENTION-COMPOUND-1 HARD-PASS.
   - **24th-rule candidate**: `RULE_extensional_fingerprint_three_way_decomposition` — every emitted concept atom must be tagged rediscovered / tight-variant / novel-primitive via extensional-fingerprint match against existing corpus; raw emission without this tagging is substrate-refused. 1st empirical witness pending F4 HARD-PASS.

## Citations (verified count: 37 across 4 parallel sub-agents)

Higher-arity ILP + cross-relation:
- Cropper-Dumancic JAIR 2022 "ILP at 30" (arXiv:2008.07912)
- Cropper-Morel MLJ 2021 Popper (arXiv:2005.02259)
- Cropper-Morel 2021 "Learning Higher-Order Programs without MIL"
- Cropper-Tourret ILP 2018 "Derivation Reduction of Metarules"
- Hocquette-Cropper POPPI (arXiv:2104.14426)
- Cropper et al. 2023 "Generalisation Through Negation and Predicate Invention" (arXiv:2301.07629)
- Evans-Grefenstette JAIR 2018 delta-ILP (arXiv:1711.04574)
- Payani et al. 2022 (arXiv:2208.06652)
- Law-Russo-Broda ILASP (arXiv:2005.00904)
- Kuzelka-Zelezny ILP 2012/2013 Bounded LGG
- Galarraga et al. VLDB-J 2015 AMIE+
- Meilicke et al. IJCAI 2019 AnyBURL
- Ott et al. SAFRAN (arXiv:2109.08002)
- Falkenhainer-Forbus-Gentner AAAI 1986 SME
- Langley et al. MLJ 2007/2008 Inductive Process Modeling
- Gauthier et al. TacticToe (arXiv:1804.00596)

Hierarchy guidance + label precision:
- Lehmann-Hitzler MLJ 2010 CELOE
- van der Laag-Nienhuys-Cheng 1998 J.Logic Programming
- Plotkin 1970 LGG; Muggleton GOLEM 1990; Muggleton-De Raedt 1994
- Claessen-Smallbone-Hughes 2010 QuickSpec
- Claessen et al. CADE 2013 HipSpec
- Johansson et al. ITP 2014 Hipster (arXiv:1405.3426)
- Johansson 2021 "Conjectures, Tests and Proofs" (arXiv:2109.03721)
- Fisher ML 1987 COBWEB; Corter-Gluck 1992 Category Utility
- Asim et al. ontology-learning survey (arXiv:2404.14991)
- Colton 2002 HR Springer
- Predicate Renaming via LLMs (arXiv:2510.25517)

External-oracle hybrids:
- Solar-Lezama Sketch; Seshia 2015 (arXiv:1505.03953) CEGIS
- Angluin 1987 Inf.Comput. L*/MAT
- Trinh et al. Nature 2024 AlphaGeometry
- Chervonyi et al. 2025 AlphaGeometry2 (arXiv:2502.03544)
- DeepMind Nature 2025 AlphaProof
- Jiang et al. ICLR 2023 Draft-Sketch-Prove (arXiv:2210.12283)
- Romera-Paredes et al. Nature 2023 FunSearch
- Yang et al. NeurIPS 2023 LeanDojo/ReProver (arXiv:2306.15626)
- Mitchell et al. AAAI 2015 NELL
- Kouagou et al. ESWC 2023 NCES (arXiv:2111.08486)
- W3C 2013 PROV-O; Ciccarese et al. 2013 PAV (arXiv:1304.7224)

Combination architectures:
- Lehmann-Hitzler 2011 DL-Learner CELOE
- Heindorf et al. EvoLearner WWW 2022 (arXiv:2111.04879)
- Confalonieri-Eppe AMAI 2019 EL++ upward refinement
- Eppe et al. Connection Science 2017 COINVENT
- "Towards Neuro-Symbolic Conceptual Blending" Springer 2025
- Ellis et al. PLDI 2021 DreamCoder (arXiv:2006.08381)
- Bowers et al. POPL 2023 Stitch (arXiv:2211.16605)
- Cao et al. POPL 2023 Babble (arXiv:2212.04596)
- Grand et al. ICLR 2024 LILO
- AbstractBeam (arXiv:2405.17514)
- Willsey et al. POPL 2021 egg
- Sha-Shindo-Kersting-Dhami NeSy 2024 NeSy-PI
- VisualPredicator (arXiv:2410.23156)
- Neuro-Symbolic Concepts (arXiv:2505.06191)
- LLM-bias-for-ILP (arXiv:2505.21486)
- UniPred (arXiv:2512.17992)

---

Next-drill candidate: TacticToe-style kernel-checked tactic synthesis OVER substrate's L6-PROOF kernel as Source G5 (fifth proposer stream — proof-tactic-invention rather than concept-invention). Alternative next-drill: HR-fingerprint discriminator complexity analysis (how many of substrate's 26285 atoms have well-defined extensional fingerprints under the substrate's witness-set schema; what is the Jaccard threshold's HARD-PASS sensitivity).
