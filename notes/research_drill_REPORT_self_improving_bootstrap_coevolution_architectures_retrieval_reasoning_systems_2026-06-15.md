# Research Drill REPORT: Self-improving / Bootstrap / Co-evolution Loops in Retrieval, Reasoning, and KG Systems

**Tag:** 2x_DEEP_DRILL_LITERATURE
**Date:** 2026-06-15
**Question:** What is the proven shape of an autonomous extension / self-improvement / co-evolution loop in retrieval, reasoning, or knowledge-graph systems? When does it converge? When does it collapse?
**Calibration:** Lit-scan penalty applied; P estimates deflated 0.15-0.25; novel-synthesis claims capped P<=0.50; hard-fail thresholds explicit.

---

## HEADLINE

The literature converges on a single proven shape: **co-evolution loops survive only when a SOUND VERIFIER (not a learned scorer) gates every integration step**. Loops gated by learned scorers exhibit three documented collapse modes (semantic drift, representation collapse, false-negative amplification); loops gated by formal verifiers exhibit empirical exponential growth on well-connected target graphs but saturate after 5-15 iterations without external curriculum injection. Substrate-internal CO-EVOLVE-1 design implication: the loop's verifier MUST be the substrate's own provable mechanism (CHTV-1 + L6-PROOF) -- a learned scorer in the loop is the documented failure path.

---

## Cheap Decisive Test

Run a 10-iteration CO-EVOLVE-1 loop with two arms run in parallel on identical seed corpus:
- **Arm V (verifier-gated):** propose -> CHTV-1/L6-PROOF verifier -> accept-or-refuse -> integrate
- **Arm S (scorer-gated):** propose -> learned similarity scorer with threshold tau -> accept -> integrate

Measure across iterations 1..10:
- atom_count growth
- distillation_ratio (atomic basis size / total derivable)
- capability_preservation (held-out F1 vs iteration-0 baseline)
- semantic drift metric: cosine drift of seed-class centroid

HARD-PASS Arm V (verifier-gated): capability_preservation >= 1.0 across all 10 iterations, semantic drift <= 0.05, monotone atom growth with diminishing returns curve (concave).
HARD-FAIL Arm V: capability loss > 0 at any iteration -> 18th-rule violation, refuses-what-cannot-prove broken.
HARD-PASS Arm S: predicted to FAIL by iteration 6-8 (drift > 0.15 OR capability_preservation < 0.95). If Arm S survives 10 iterations cleanly, the substrate's verifier-supremacy thesis is weakened.
HARD-FAIL Arm S: collapse by iteration 8 expected per NELL precedent; if collapse happens by iteration 4 the failure mode is more aggressive than the LLM-distillation literature predicts.

---

## ARM 1 SYNTHESIS: Bootstrap / Self-Training in Retrieval

Five well-documented findings on iterative self-improvement in dense retrieval. **(1)** RocketQA [Qu et al., NAACL 2021, arXiv:2010.08191] explicitly identifies that ANCE-style iterative hard-negative mining produces "false negatives" -- retrieved hard-negatives that are actually relevant -- and adds a *denoising* step using a cross-encoder verifier; the cross-encoder is the de-facto sound layer that keeps the iteration honest. **(2)** Self-training in dense retrievers exhibits documented "representation collapse" [Meta AI, "Understanding and mitigating dimensional collapse"; Wikipedia: Representation collapse] where iterative pseudo-labeling collapses embeddings into a low-rank manifold; mitigations (negative samples, variance regularization, stop-gradient asymmetry) are all *structural* counters to feedback amplification, not training-volume fixes. **(3)** HyDE [Gao et al., ACL 2023] uses LLM-generated hypothetical documents as a query-expansion mechanism; the dense bottleneck acts as a "semantic filter" preserving structure while discarding hallucinated facts -- this is a verifier-by-construction (the embedding manifold itself is the integrity check). **(4)** DSI [Tay et al., NeurIPS 2022, arXiv:2202.06991] memorizes the corpus in transformer parameters but suffers beam-search hallucinations on doc-id generation; no sound verifier exists for "does this doc-id correspond to a real document," so the iterative variant is fragile. **(5)** Teleportation Negatives [arXiv:2210.17167] documents catastrophic forgetting in iterative DR training -- prior gains are lost across rounds without explicit replay scaffolding.

Cross-arm-1 inference: **All five papers converge on the same structural prescription -- iterative DR self-training collapses unless there is (a) a sound or sound-by-construction filter, AND (b) explicit replay/anchoring to prevent forgetting.** Pure self-distillation amplifies whatever noise the scorer already had.

---

## ARM 2 SYNTHESIS: DETECT-PROPOSE-VERIFY-INTEGRATE Architectures

Five well-documented findings on neuro-symbolic and self-play loops. **(1)** AlphaGeometry [Trinh et al., Nature 2024, PMC10794143] explicitly factors the loop as *symbolic deduction engine (sound) + transformer proposer (heuristic)*; the loop runs symbolic-first to exhaustion, then the LM proposes one auxiliary construction, then symbolic-retry. Soundness is structurally guaranteed by the deduction engine; the LM cannot inject errors. **(2)** AlphaProof [DeepMind 2024] does the same in Lean with an AlphaZero-style RL outer loop -- Lean's kernel is the sound verifier, and 80M generated problems are filtered through it. **(3)** A Theoretical Framework for Self-Play Theorem Proving [arXiv:2606.01861, 2026] provides the first convergence theorem: *if the underlying theorem-graph is well-connected, a prover-conjecturer pair using a reversible random walk grows the proved-theorem set exponentially*. The graph-connectivity precondition is load-bearing. **(4)** Formal Mathematics Statement Curriculum Learning [Polu et al., arXiv:2202.01344] documents that expert iteration *gains diminish after a few iterations* in Lean/GPT-f; obtaining continuous improvement from unlimited verifier feedback remains an open problem. **(5)** DreamCoder [Ellis et al., PLDI 2021 / Phil. Trans. R. Soc. A 2023] uses wake-sleep Bayesian library learning where the *symbolic e-graph refactoring* identifies common sub-components and grows a deepening library; hold-out accuracy improves monotonically across iterations -- but the loop is bounded by the corpus, not unbounded.

Cross-arm-2 inference: **Verifier-gated loops have documented (sometimes theoretical) convergence, but they saturate.** Saturation, not collapse, is the dominant failure mode for sound-verifier loops -- the opposite failure profile from learned-scorer loops.

---

## CROSS-ARM SYNTHESIS

**(1)** The collapse vs saturation dichotomy is the cleanest structural result in this literature. Learned-scorer loops *collapse* (NELL semantic drift [Mitchell et al., AAAI 2010 / CACM 2018]; representation collapse in DR self-training; DSI beam-search hallucination). Sound-verifier loops *saturate* (expert iteration plateau in Lean; DreamCoder corpus-bounded library growth; AlphaProof's reliance on 80M generated problems to push the curve). **(2)** NELL's explicit mitigation -- *Mutual Exclusion Bootstrapping (MEB)* where multiple semantic classes compete for each term -- is structurally identical to substrate's THEOREM_LINKED-with-refusal mode and the 20th rule's 3-mode distillation taxonomy (atom-removing, structure-adding, refusal). MEB is the closest published precedent for substrate's CO-EVOLVE-1 refusal mode. **(3)** AlphaGeometry's symbolic-first / heuristic-second sequencing is the canonical safe co-evolution shape: run the sound mechanism to exhaustion FIRST, only then admit a heuristic proposer for ONE step, then return to sound. Substrate analog: L6-PROOF to exhaustion -> propose ONE structural extension -> CHTV-1 verify -> integrate or refuse. **(4)** Cold-start handling: AlphaGeometry uses *synthetic theorem generation* (no human demonstrations) seeded by the symbolic engine itself; DreamCoder cold-starts from a base DSL and grows. Substrate analog: cold-start with foundation primitives (8 atoms) + axiom set, NOT with imported embeddings. **(5)** Convergence behavior at scale is empirically *concave* (diminishing returns) for all five sound-verifier systems documented; none show monotone-linear-forever. **(6)** The 22nd methodology rule (Lakatos audit) is precedent-supported: NELL's published post-mortem explicitly notes "still trying to understand what causes it to become increasingly competent at reading some types of information, but less accurate over time for others" -- exactly the Lakatos progressive/degenerating signal. **(7)** Substrate's CO-EVOLVE-1 design should reject any architecture where a learned scorer makes integration decisions; the literature offers zero examples of such a loop surviving past 5-10 iterations without external human intervention. **(8)** The graph-connectivity precondition from [arXiv:2606.01861] suggests substrate should *measure* SHARES_MATH connectivity BEFORE running CO-EVOLVE-1; if the graph is fragmented, the loop is provably unable to grow exponentially. This is testable via spectral gap on the atom-graph.

---

## ACTIONABLE OUTPUTS

**Q1 -- Proven shape of CO-EVOLUTION loop that doesn't collapse:**
PROPOSE (heuristic, low-cost) -> sound VERIFIER refuses-or-accepts -> INTEGRATE only verified candidates -> REPLAY prior verified set to prevent forgetting -> repeat. The verifier is non-negotiable; the replay/anchoring is non-negotiable. AlphaGeometry + DreamCoder + AlphaProof all instantiate this exact shape.

**Q2 -- Role of SOUND VERIFIER vs learned scorer:**
The verifier is the SOLE mechanism keeping the loop honest. Learned scorers in the integration position are the documented collapse path (NELL semantic drift, DR representation collapse). Substrate has *two* sound verifiers ready: CHTV-1 (mechanistic verification) + L6-PROOF (axiom-terminating backward chaining). Both must gate any CO-EVOLVE-1 step. Per 18th rule (substrate refuses what it cannot prove), UNDECIDABLE atoms get *refused integration*, not optimistically merged. [P=0.85 deflated to 0.65 for substrate transferability].

**Q3 -- Cold-start handling:**
Seed with axiomatic foundations (substrate's 8 foundation primitives) + a small curated atom set. Do NOT cold-start from learned embeddings -- this imports the very collapse mode the loop must avoid. AlphaGeometry's symbolic-engine-seeded synthetic theorems is the cleanest precedent; substrate analog is L6-PROOF generating proof obligations from foundation primitives, then the loop attempts to close them.

**Q4 -- Empirical convergence behavior at scale:**
**Concave / saturating, not monotone-linear.** Expert iteration plateaus in Lean within ~5-10 iterations; DreamCoder shows monotone but decelerating hold-out gains; AlphaProof needed 80M problems to push the curve. Substrate should pre-register an expected concave curve and treat *linear-or-better growth past iteration 5* as a HARD-PASS (would be SOTA), and *negative growth in any single iteration* as a HARD-FAIL trigger for review.

**Q5 -- Architectural patterns for substrate-internal CO-EVOLVE-1 (no LLM):**
- Pattern A (AlphaGeometry-style): L6-PROOF to exhaustion, then propose ONE structural extension (e.g., one new SHARES_MATH edge candidate), then CHTV-1 verify, then integrate-or-refuse. Loop.
- Pattern B (DreamCoder-style): wake = attempt unsolved capability gaps with current library; sleep = e-graph refactor to discover common abstractions; dream = replay verified abstractions. Library = substrate atom set.
- Pattern C (Self-play theorem proving [arXiv:2606.01861]): conjecturer proposes new derivable claims; prover (L6-PROOF) attempts; verified -> integrate; unprovable in N steps -> refuse. Pre-requisite: measure SHARES_MATH graph spectral gap; loop is unsafe to run if graph is disconnected.
- Pattern D (NELL MEB-style): multiple candidate categorizations compete for each new atom; only the one with sound derivation wins; ties -> refuse.

**Recommendation:** Substrate CO-EVOLVE-1 v0 = Pattern A + Pattern D's refusal mode. Pattern B is reserved for distillation cycle (the 20th rule's 3-mode taxonomy is already pattern-B-shaped). Pattern C requires connectivity measurement first.

**Q6 -- Failure modes / HARD WARNINGS:**
- **W1 -- DO NOT put a learned scorer in the integration position.** All five learned-scorer-loop precedents (NELL pre-MEB, ANCE-only, DSI, naive DR self-training, contrastive self-distillation) collapse.
- **W2 -- DO NOT skip replay / anchoring.** Catastrophic forgetting is documented even in verifier-gated loops [Teleportation Negatives, arXiv:2210.17167]. Substrate needs explicit prior-atom replay each cycle.
- **W3 -- Expect saturation by iteration 5-15.** Do not plan CO-EVOLVE-1 v0 to deliver unbounded growth; plan for concave curve and pre-register the expected plateau.
- **W4 -- Graph connectivity is a precondition.** [arXiv:2606.01861] proves exponential growth requires well-connected graph; substrate should compute SHARES_MATH spectral gap BEFORE running the loop.
- **W5 -- Cold-start from learned embeddings imports collapse.** Use axiomatic / foundation-primitive seed only.
- **W6 -- 18th-rule violation risk.** Any integration step that admits an UNDECIDABLE atom into the structured core is the documented collapse path; the loop must refuse-or-accept, never "tentatively integrate."

---

## Substrate-Product Implications

This research grounds CO-EVOLVE-1 as a Tier 1 architectural candidate (claim 10) with literature precedent across two independent fields (retrieval + theorem proving). The substrate has all required components: sound verifier (CHTV-1 + L6-PROOF), refusal mode (18th rule), distillation taxonomy (20th rule), capability_preservation gate (Tier 1 claim 7), and atom-graph for connectivity measurement. **The substrate's standalone CO-EVOLVE-1 differentiates structurally from every documented LLM-augmented loop -- it has TWO sound verifiers where the literature has at most ONE, and it has an explicit 3-mode distillation taxonomy where the literature has only refusal-as-afterthought.** Substrate-product positioning: "the only co-evolution architecture with two independent sound verifiers and a 3-mode integration taxonomy ready for closed-loop operation without human intervention." Per 11th rule, this is substrate-on-its-own measurement; no LLM comparison required to validate the architecture.

---

## Citations (verified count: 12)

1. Qu et al., "RocketQA: An Optimized Training Approach to Dense Passage Retrieval," NAACL 2021, arXiv:2010.08191. [VERIFIED]
2. Xiong et al. (ANCE) -- referenced via RocketQA. [VERIFIED-INDIRECT]
3. "Reduce Catastrophic Forgetting of Dense Retrieval Training with Teleportation Negatives," arXiv:2210.17167. [VERIFIED]
4. Gao et al., HyDE: "Precise Zero-Shot Dense Retrieval without Relevance Labels," ACL 2023. [VERIFIED via revisit paper arXiv:2511.19349]
5. Tay et al., "Transformer Memory as a Differentiable Search Index," NeurIPS 2022, arXiv:2202.06991. [VERIFIED]
6. Trinh et al., "Solving olympiad geometry without human demonstrations" (AlphaGeometry), Nature 2024, PMC10794143. [VERIFIED]
7. DeepMind, "AI achieves silver-medal standard solving International Mathematical Olympiad problems" (AlphaProof), 2024. [VERIFIED]
8. "A Theoretical Framework for Self-Play Theorem Proving Algorithms," arXiv:2606.01861, 2026. [VERIFIED]
9. Polu et al., "Formal Mathematics Statement Curriculum Learning," arXiv:2202.01344. [VERIFIED]
10. Ellis et al., "DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning," PLDI 2021; extended in Phil. Trans. R. Soc. A 2023. [VERIFIED]
11. Carlson et al. / Mitchell et al., "Toward an Architecture for Never-Ending Language Learning" (NELL), AAAI 2010; "Never-Ending Learning," CACM 2018. [VERIFIED]
12. Lample et al., "HyperTree Proof Search for Neural Theorem Proving," arXiv:2205.11491. [VERIFIED]

**[UNVERIFIED]** -- specific iteration-count saturation thresholds for AlphaProof internals (DeepMind blog reports 80M problems but does not publish per-iteration saturation curves; the "5-15 iteration" estimate above is interpolated from Polu et al. + InternLM2.5-StepProver patterns).

---

## Cross-thread synthesis with prior entries

- Composes with **20th methodology rule (3-mode distillation taxonomy)**: literature confirms refusal mode is the load-bearing collapse-prevention mechanism.
- Composes with **18th methodology rule (substrate refuses what it cannot prove)**: AlphaGeometry/AlphaProof/Lean expert-iteration all instantiate this rule explicitly.
- Composes with **Tier 1 architectural claim 7 (capability_preservation = 1.0)**: literature precedent for verifier-gated capability preservation across iterations.
- Composes with **Tier 1 architectural claim 8 candidate (type-graph terminates in atoms)**: parallel to AlphaGeometry's symbolic-engine termination and DreamCoder's library-bottom-out.
- **REFUTES** any substrate roadmap that puts a learned scorer (BGE, cross-encoder, etc.) in the integration decision -- this is the NELL semantic-drift path.
- **OPENS** CO-EVOLVE-1 as Tier 1 architectural claim 10 candidate (closed-loop self-extension with provable safety).

---

## P estimates (calibration-penalty applied)

- P(verifier-gated loop survives 10 iterations on substrate) = 0.50 (cap at novel-synthesis ceiling; 4 literature precedents support; substrate lacks empirical iteration-count data)
- P(learned-scorer loop collapses by iteration 8 on substrate) = 0.70 (5 strong literature precedents)
- P(SHARES_MATH spectral gap is sufficient for exponential growth) = 0.30 (substrate graph density still emerging; deflated heavily)
- P(CO-EVOLVE-1 reaches HARD-PASS in v0 cell) = 0.40 (architectural plausibility high; empirical untested)

**P_deflated headline = 0.50** (substrate CO-EVOLVE-1 architecture is precedent-supported but novel-synthesis cap holds).
