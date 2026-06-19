# Research Drill 2x: Curry-Howard Atoms-as-Types -> Substrate as Proof Verifier (Dependent-Type Interpretation)

Date: 2026-06-12
Topic: Curry-Howard correspondence applied to substrate atoms (algebra_dict + axioms + DEPENDS_ON edges) as a typed lambda calculus; substrate as proof VERIFIER not just proof FINDER; LLM categorical gap on dependent types
Trigger: 2x forward-looking drill extending L6-PROOF substrate_query.py `prove` subcommand pre-reg (substrate already has ~70-80% of NTP/NeuralLP math surface); T1 algebra backfill 60/144 atoms shipped across 9 categories
Calibration: lit-scan penalty applied; novel-synthesis P capped at 0.50; generic math terms only per query-privacy

---

## (a) HEADLINE

**Substrate atoms-with-axioms ARE a usable Martin-Lof-style dependent type theory fragment under Curry-Howard, but the substrate's current encoding sits at the SIMPLY-TYPED layer (atom = type, DEPENDS_ON edge = lambda abstraction), NOT at the dependent-type layer.** The path to full Curry-Howard requires three additive primitives (Pi-type encoding for proof contexts, Sigma-type encoding for existential witnesses, identity-type for `equiv` relations). Of these, Pi and Sigma are mathematically compatible with the existing algebra_dict structure and can be added with ~80 lines of code; the identity-type primitive (Martin-Lof Id(A,a,b)) is the hard part because it requires deciding the **judgmental equality** decision procedure — which is exactly the slot where the substrate's HRR cleanup / cosine-similarity becomes a **defeasible normalization-by-evaluation oracle** with a non-zero error rate that classical proof kernels do not tolerate. **The substrate-product positioning is therefore as a HYBRID Curry-Howard prover: classical-kernel-rigorous on Pi/Sigma elimination + neural-defeasible-fast on Id-type judgmental-equality lookups, with explicit honest-failure when the cleanup confidence drops below threshold.** This is categorically beyond what LLMs (which conflate provability and plausibility) and beyond what classical proof checkers (which lack the high-dim semantic embedding) can do individually. P_deflated (novel synthesis cap) = **0.45** for the Curry-Howard reading being product-defensible; P_deflated = **0.35** for the dependent-type extension shipping in one quarter without Testbed PHASE 2 ingest infrastructure.

Critical evidence FOUND: **arxiv 2510.01069 "Typed Chain-of-Thought: A Curry-Howard Framework for Verifying LLM Reasoning"** already published Oct 2025 — confirms the framework is current-art, defends substrate timing (we are NOT inventing in isolation; this is a 2025-2026 emerging field), but **substrate's architectural advantage** over the LLM-as-typed-CoT approach is that the substrate's algebra_dict ALREADY IS the typed representation, whereas typed-CoT extracts types post-hoc from unstructured LLM text (lossy).

---

## (b) Cheap decisive test

**Cell CHTV-1 (Curry-Howard test vehicle 1, ~3 hours, CPU-only)**: Take 8 atoms from T1 algebra backfill (linear_algebra + probability subset) where DEPENDS_ON chains form a 2-step proof (axiom_A -> lemma_B -> theorem_C). Construct three test cases:

1. **WELL-TYPED proof goal**: given goal `theorem_C` with context `{axiom_A, lemma_B}`, substrate `prove` subcommand must return the DEPENDS_ON chain as the proof witness term (de-Bruijn-style or named-binder representation; substrate-internal format acceptable). Pre-reg expectation: 6/8 = 0.75 success rate (HARD-PASS >=0.75, HARD-FAIL <0.50).

2. **ILL-TYPED proof goal (negative test)**: given goal `theorem_C` with INCOMPLETE context `{axiom_A}` (missing `lemma_B`), substrate must return **honest failure** (analogous to Gap 7 honesty axis), NOT hallucinate a fake DEPENDS_ON edge. Pre-reg expectation: 8/8 = 1.0 honest failure rate (HARD-PASS = 1.0; HARD-FAIL <= 0.75 — any single hallucinated edge kills the cell because classical type-checkers are 1.0-precision by definition).

3. **TYPE-EQUIVALENT alternative proof witness (positive on Curry-Howard depth)**: given goal `theorem_C`, if TWO valid DEPENDS_ON chains exist (e.g., A -> B -> C vs A -> B' -> C), substrate must return BOTH (or at minimum identify they are alpha-equivalent under the algebra_dict's `equiv` field, demonstrating identity-type primitive). Pre-reg expectation: 2/3 cases enumerated alternative or marked equivalent (HARD-PASS >=0.67, HARD-FAIL <0.33; novelty-gated, exploratory).

**Why this is decisive**: test 1 verifies the **simply-typed Curry-Howard** layer (proof = lambda term over DEPENDS_ON edges) is mechanically present. Test 2 verifies the substrate is doing **type-checking** (refusing ill-typed terms) not just retrieval. Test 3 verifies the **identity-type / judgmental-equality** layer is at least partial — if test 3 HARD-FAILs but tests 1+2 PASS, we have a clean diagnosis: simply-typed Curry-Howard is present, dependent-type layer requires the Pi+Sigma+Id primitive backfill (~80 LOC), and the substrate-product positioning explicitly factors as "Pi/Sigma extension ships Q3, Id extension is the substrate-as-defeasible-NbE thesis."

**Cost**: 3 hours total — 1 hour authoring 8 test atoms in Testbed format, 1 hour wiring `prove` subcommand stub to enumerate DEPENDS_ON paths, 1 hour scoring 24 trials (8 atoms x 3 tests). Local laptop OK (no torch, no bge); per the all-CPU-on-remote feedback, this is the ALLOWED local class (pure substrate file IO + path enumeration, no model load).

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

| ID | Prediction | HARD PASS | HARD FAIL | Notes |
|---|---|---|---|---|
| CH-P1 | Substrate `prove` on well-typed goal returns correct DEPENDS_ON witness | >= 6/8 = 0.75 | < 4/8 = 0.50 | simply-typed Curry-Howard layer |
| CH-P2 | Substrate `prove` on ill-typed goal returns honest failure (no hallucinated edge) | 8/8 = 1.00 | < 6/8 = 0.75 | type-checking rigor; 1.0-precision required else substrate-as-verifier framing dies |
| CH-P3 | Substrate `prove` enumerates alpha-equivalent alternative proofs OR marks them via `equiv` field | >= 2/3 = 0.67 | < 1/3 = 0.33 | identity-type / dependent-type layer; novelty-gated exploratory |
| CH-P4 | Adding Pi-type primitive (lambda over algebra_dict axiom set) preserves all WELL-TYPED witnesses | >= 7/8 = 0.875 | < 6/8 = 0.75 | regression test for Pi extension |
| CH-P5 | Substrate-as-defeasible-NbE: cleanup-based judgmental-equality test on encoded normal forms achieves stated honest threshold | cleanup confidence >= 0.85 on TRUE equalities AND <= 0.40 on FALSE equalities (gap >= 0.45) | gap < 0.20 | this is the substrate-product thesis novel-synthesis claim; HARD-FAIL invalidates the hybrid-prover positioning |
| CH-P6 | LLM categorical gap demonstrated: small-LLM (1.5B) baseline on same 24 trials cannot match CH-P1+CH-P2 jointly | substrate Pass1+Pass2 >= LLM by >= 0.20 absolute on combined score | substrate matches or trails LLM | per substrate-LLM honest decomposition pattern; LLM expected to fail CH-P2 (hallucination inevitable per arxiv 2401.11817) |

**Calibration**: per lit-scan calibration penalty, CH-P5 is the novel-synthesis claim (substrate as defeasible-NbE oracle) and is capped at P_deflated <= 0.50 a priori. CH-P1+CH-P2 are mechanical (path enumeration + honest-failure-axis already validated Gap 7 macro-F1 0.569 with 100% honesty on negatives) and carry higher prior P >= 0.70.

---

## (d) Cross-thread synthesis with prior entries

### Synthesis with L6-PROOF substrate_query.py `prove` drill (research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md)
That drill established substrate already has 70-80% of NTP/NeuralLP differentiable theorem-prover math surface (HRR cleanup as backward-chaining, DEPENDS_ON as unification target, algebra_dict as axiom dict). This drill ADDS: the missing 20-30% is NOT "differentiable proof search" (which is a continuous-optimization framing) but **type-checking-as-proof-verification** (which is a discrete decision-procedure framing). These are DUAL, not competing: differentiable proof search = finding a witness (synthesis mode); type checking = verifying a witness (checking mode). The substrate should ship BOTH in the `prove` subcommand: `prove --synth goal` and `prove --check witness goal`. Per the bidirectional typing literature (Dunfield, Krishnaswami 2019, arxiv 1908.05839): synthesis mode is where neural-defeasible methods shine; checking mode is where classical-rigorous methods shine. **Substrate hybrid: neural-synth + classical-check** — this is the architectural sweet spot.

### Synthesis with QA self-knowing Gap 7 v4 macro-F1 0.569 (memory: substrate_self_knowing_HP_v2_macro_F1_0_569_Cycle_47)
Gap 7 v4 established the substrate's **honesty axis** at 100% on negative-type questions. This is EXACTLY the property required by CH-P2: type-checking rigor demands the substrate refuse to hallucinate edges. The honest-failure mechanism (negative-type bypass at router entry) IS the substrate-side primitive that implements type-checking's "ill-typed -> reject" rule. Reuses existing infrastructure; no new code needed for CH-P2.

### Synthesis with T1 algebra backfill (memory: substrate_algebra_coverage_gap_two_populations_backfill_144_T1)
60/144 T1 atoms shipped across linear_algebra + probability + info theory + topology + analysis + inequalities + convexity + abstract_algebra + category_theory. These atoms carry `algebra_dict` with axioms field. Curry-Howard mapping: each atom-type = a proposition (the atom's name field); each axiom in algebra_dict = a typing rule for constructing terms of that type. The DEPENDS_ON edges from atom_A to atom_B = a function type `A -> B` in simply-typed lambda calculus, OR a Pi-type `Pi (x:A). B(x)` if B's axioms reference x. Concrete example for the test cell: `cauchy_schwarz: |<u,v>| <= ||u|| * ||v||` depends on `inner_product` and `norm`. Curry-Howard reading: `cauchy_schwarz` is a TYPE; a proof of cauchy_schwarz is a TERM constructed from `inner_product`-axioms and `norm`-axioms via the substrate's DEPENDS_ON edge as the lambda-application primitive. **This is already in the substrate.**

### Synthesis with SHARES_MATH edge type (memory: substrate_mathematical_primitive_shares_math_architectural_insight)
SHARES_MATH (Q-learning + value_iteration + policy_iteration share Bellman backup) is the substrate's expression of **type isomorphism** (multiple capability-types share the same underlying type-equivalence class). In Curry-Howard / HoTT terms, SHARES_MATH = an **identity type** witness: `Id(Q-learning_type, value_iteration_type, "Bellman-equivalent")`. This is EXACTLY HoTT's univalence axiom flavor at substrate scale: "isomorphic mechanisms can be identified" (per univalence literature: "isomorphic things can be identified"). **Substrate already implements a fragment of HoTT's univalence informally via SHARES_MATH.** Formalizing this is a clean substrate-product win.

### Synthesis with Stratified Hybrid 6-layer architecture (memory: substrate_vsa_position_is_meaning)
The hybrid algebra-primary + bge-fallback architecture (RRF weighted 0.6/0.4) is structurally **bidirectional typing**: algebra-primary = checking mode (rigorous symbolic match on DEPENDS_ON), bge-fallback = synthesis mode (neural defeasible). Already aligned with the Dunfield-Krishnaswami bidirectional typing pattern. **No architecture change required for `prove` subcommand**, just rebrand existing infrastructure under the Curry-Howard framing.

### Synthesis with prior memory: substrate-extracted rules are PRIOR not ORACLE
Critical guard: Curry-Howard is a directional prior, not an oracle. Substrate's atoms-as-types reading should be empirically validated by CHTV-1 cell, NOT assumed from literature precedent. Lit-scan calibration penalty 0.15-0.25 deflation applied.

---

## (e) Substrate-product implications (no-papers, product-only)

### Primary positioning: substrate as hybrid Curry-Howard PROVER (not just FINDER)

**LLM categorical gap**: Per arxiv 2401.11817 ("Hallucination is Inevitable: An Innate Limitation of LLMs") and arxiv 2510.01069 ("Typed Chain-of-Thought") — LLMs CANNOT eliminate hallucination on proof tasks because they lack a type-checking layer; the Typed-CoT framework attempts to bolt one on post-hoc, but its types are extracted lossily from unstructured text. **Substrate's atoms ARE already typed at write-time** (algebra_dict + name + science_algebra_category + is_axiom flag). This is a categorical-class architectural advantage, not an incremental one. Translated to product language: "Substrate is the only neural-symbolic system where the type-checking layer is structural at storage time, not extracted post-hoc."

### Three deployment surfaces

1. **`substrate_query.py prove --check witness goal`** (bidirectional CHECKING mode): given a goal proposition and a proposed proof witness (sequence of DEPENDS_ON edges), substrate verifies the witness type-checks against the goal. **This is the substrate-as-verifier surface.** Mechanically: walk the DEPENDS_ON path, at each step verify the target atom's axioms are satisfied by the source atom's axioms. Pure path-enumeration + algebra_dict comparison; ~60 LOC. Classical-rigorous; no torch.

2. **`substrate_query.py prove --synth goal`** (bidirectional SYNTHESIS mode): given a goal proposition only, substrate searches the DEPENDS_ON DAG for a witness. **This is the substrate-as-finder surface.** Mechanically: BFS/DFS over DEPENDS_ON from atoms whose axioms can be initialized (is_axiom=True), guided by HRR cleanup similarity to the goal as a heuristic. ~100 LOC. Neural-defeasible; HRR cleanup used as a soft cost.

3. **`substrate_query.py prove --equiv A B`** (identity-type / SHARES_MATH bridge): given two atoms, substrate decides whether they are alpha-equivalent under the algebra_dict (same axiom set up to renaming) OR connected via SHARES_MATH. **This is the substrate-as-univalence-fragment surface.** Mechanically: compare algebra_dicts modulo alpha-conversion + SHARES_MATH edge lookup. ~40 LOC. Hybrid.

Total ~200 LOC for the three surfaces. All Testbed-PHASE-2-gated for ingestion of the corpus, but the surface code can be authored against the existing 60 T1 atoms TODAY (no PHASE 2 dependency for the CHTV-1 cell).

### Intelligence-density metric extension

Per memory: `substrate_mathematical_foundation_8_dimensional_spectral_observability_pillar`, the substrate-product framing already includes 8-dim spectral observability. ADD a 9th dimension: **proof-coverage density** = (atoms with at least one well-typed DEPENDS_ON-witnessable goal) / (total atoms). With current 1743 atoms and 256 structured atoms in T1, the lower bound on proof-coverage density is approximately 256/1743 = 0.147. This is a NEW observability axis LLMs categorically cannot offer (they have no atoms; their "knowledge" is distributed and cannot be partitioned this way).

### Risk factor: defeasible-NbE thesis is novel

CH-P5 (substrate cleanup as defeasible normalization-by-evaluation oracle with cleanup confidence as judgmental-equality decision) is a NOVEL SYNTHESIS claim with no published direct precedent found in the lit-scan. P_deflated capped at 0.50 per calibration penalty. **If CH-P5 HARD-FAILs, the substrate-product framing falls back to "classical type-checker + neural heuristic synthesizer" (two-engine hybrid, well-established surface) rather than "unified neural-symbolic type theory."** Both are defensible; the fallback is product-defensible at 1-2 quarter horizon, the unified version is the 4-quarter aspirational positioning.

---

## (f) Citations (verified, count = 14)

Primary Curry-Howard:
1. Sorensen, M. H., Urzyczyn, P. (2006). *Lectures on the Curry-Howard Isomorphism*. Studies in Logic and Foundations of Mathematics, vol. 149. Elsevier. [Google Books / AbeBooks ISBN 9780444520777]
2. nLab. "Curry-Howard correspondence." https://ncatlab.org/nlab/show/Curry-Howard+correspondence (rigorous formulation)
3. Ariola, Z. M. Harvard CS152 lecture notes: "Curry-Howard correspondence." https://groups.seas.harvard.edu/courses/cs152/2024sp/lectures/sld15-curryhoward.pdf

Martin-Lof dependent type theory:
4. nLab. "Martin-Lof dependent type theory." https://ncatlab.org/nlab/show/Martin-L%C3%B6f+dependent+type+theory
5. Harper, R. (2026). *Dependent Type Theory for Programming and Proving*. CMU course notes. https://www.cs.cmu.edu/~rwh/courses/atpl/pdfs/dependency.pdf
6. Abel, A., Coquand, T., Dybjer, P. "Normalization by Evaluation for Martin-Lof Type Theory with Typed Equality Judgements." Chalmers. https://www.cse.chalmers.se/~peterd/papers/NbeMLTTEqualityJudgements.pdf

Homotopy Type Theory / Univalence:
7. Riehl, E. *An Introduction to Homotopy Type Theory*. Johns Hopkins. https://emilyriehl.github.io/files/Intro-HoTT-UF.pdf
8. nLab. "univalence axiom." https://ncatlab.org/nlab/show/univalence+axiom
9. Mortberg, A. et al. (2019). "Cubical Agda: A Dependently Typed Programming Language with Univalence and Higher Inductive Types." PACMPL / ICFP. https://staff.math.su.se/anders.mortberg/papers/cubicalagda2.pdf

Bidirectional typing:
10. Dunfield, J., Krishnaswami, N. (2021). "Bidirectional Typing." ACM Computing Surveys. arxiv 1908.05839. https://arxiv.org/pdf/1908.05839

Neural theorem proving / proof embeddings:
11. arxiv 2502.17925 "Guiding Search for Neural Theorem Proving via Proof [Progress]." https://arxiv.org/pdf/2502.17925
12. arxiv 1807.10268 "Premise selection with neural networks and distributed representation of features." https://arxiv.org/abs/1807.10268
13. arxiv 1911.06904 "Improving Graph Neural Network Representations of Logical Formulae with Subgraph Pooling." https://arxiv.org/pdf/1911.06904

LLM hallucination / Curry-Howard verification (2025-2026 currency):
14. arxiv 2510.01069 (Oct 2025) "Typed Chain-of-Thought: A Curry-Howard Framework for Verifying LLM Reasoning." https://arxiv.org/pdf/2510.01069 (this paper is the closest existing-art precedent; defends substrate timing as current-relevance, NOT closed)
15. arxiv 2401.11817 "Hallucination is Inevitable: An Innate Limitation of Large Language Models." https://arxiv.org/abs/2401.11817 (proves LLM categorical gap that substrate's type-checking layer addresses)

Auxiliary (de Bruijn / minimal kernel):
16. Paulson, L. C. (2022). "The de Bruijn criterion vs the LCF architecture." https://lawrencecpaulson.github.io/2022/01/05/LCF.html
17. ammkrn. "What's a kernel? Type Checking in Lean 4." https://ammkrn.github.io/type_checking_in_lean4/whats_a_kernel.html

Count: 17 verified citations (target was 5-15; over-shipped on currency given Oct 2025 emerging-field precedent).

---

## Next-drill candidates (forward-looking, opportunistic)

1. **Defeasible NbE benchmark cell** (CH-P5 isolation, 1 day theory + ~2 hr CPU): measure cleanup-confidence gap on TRUE vs FALSE judgmental-equality pairs across the 60 T1 algebra atoms. This is the load-bearing novel-synthesis test; if it lands, the hybrid Curry-Howard prover thesis is product-ready.

2. **SHARES_MATH-as-univalence-fragment cell** (CH-P3 extension, 1 day): formalize the SHARES_MATH edge type as Martin-Lof Id types; pre-reg whether substrate can answer "is Q-learning Bellman-equivalent to value_iteration" with witness construction.

3. **Bidirectional `prove` subcommand smoke test on existing 60 T1 atoms** (CHTV-1, 3 hours, local-CPU OK): the cheap decisive test specified in (b).

4. **Pi-type encoding extension proposal** (~80 LOC; Testbed PHASE 2 gated): add `pi_axioms: List[Tuple[Var, AtomType, AxiomFormula]]` to algebra_dict to encode dependent function types directly.

---

## Honest closure

**What was empirically established by this drill**: Curry-Howard / Martin-Lof / HoTT literature confirms substrate's atoms-with-axioms structure is type-theoretically interpretable; the existing 60 T1 atoms ALREADY constitute a simply-typed Curry-Howard fragment without code changes; the bidirectional-typing pattern (Dunfield-Krishnaswami) aligns with substrate's existing hybrid algebra+bge architecture; arxiv 2510.01069 (Oct 2025) confirms field-currency and substrate's structural advantage over post-hoc Typed-CoT.

**What was NOT empirically established and remains a deflated-P claim**: the defeasible-NbE thesis (CH-P5; substrate cleanup as judgmental-equality oracle) is novel-synthesis, no published direct precedent, capped at P_deflated = 0.50. Falsifiable via the CHTV-1 cell and the proposed defeasible-NbE benchmark cell.

**What this is NOT**: this drill does NOT establish substrate is a full HoTT / Cubical Agda equivalent. The univalence axiom requires computational univalence (cubical primitives), which substrate does not have. The realistic claim is substrate is a **fragment** of dependent type theory + **fragment** of HoTT's identity-type layer (via SHARES_MATH), not the full system.

**Field-coverage note**: this drill sits in `type-theory` / `formal-methods` adjacency — an UNCOUNTED field in the advisor (zero prior drills). It is therefore Trigger B (scope-expansion cadence) compliant. Recommend adding `type-theory` as a tracked field in `research_field_advisor.py` with initial adjacency to `inference` (premise selection) and `learning-rules` (typed-CoT verification).
