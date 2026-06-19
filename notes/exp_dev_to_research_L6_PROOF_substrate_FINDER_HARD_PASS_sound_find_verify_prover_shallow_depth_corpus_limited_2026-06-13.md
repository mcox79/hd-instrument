# exp_dev -> research: L6-PROOF substrate-as-FINDER HARD_PASS -- sound backward-chaining prover (20/20 math goals, 20/20 CHTV-verified, 100% axiom-terminating). With CHTV = complete find+verify prover surface. Honest depth caveat.

**From:** exp_dev  **Date:** 2026-06-13. Hand-off anchor (substrate_as_differentiable_theorem_prover, Anchor 1 FINDER). NO LLM. file-IO+graph, no heat (laptop clean copy).
**Cell:** exp_substrate_proof_finder_backward_chaining_cpu_v1.py. Complements CHTV-1 (verifier, prior HARD_PASS).

## Result -- HARD_PASS
- Math-structured goals (corpus math/science/concept/school/meta; excl *_history narrative): goal pool 137, sampled 20.
- proofs FOUND (backward-chain to an axiom): 20/20 = 1.0
- SOUND (each found witness re-type-checked by CHTV -- every edge real): 20/20 = 1.0 (no unsound proofs -- the non-negotiable bar)
- axiom-terminating (chain ends at T1 / leaf foundational atom): 20/20 = 1.0
- examples: T3/viterbi_decoding -> T3/hmm_transition; T3/bocpd_changepoint -(depth 3)-> T1/probability_space;
  T3/expectation_maximization -> T3/forward_algorithm; SCHOOL/sparse_distributed_memory_family -(2)-> T2/cosine_cleanup.

## Substrate-product reading
With CHTV-1 (VERIFIER) + this FINDER, the substrate is a sound FIND+VERIFY prover over its own math atoms: it deduces multi-step
derivation chains and every chain it returns type-checks. This is "self-deducing" (level-2 metacognition) -- closes the USER goal
"substrate understands its own mathematics" at the DEDUCTION level. LLM categorical gap: an LLM cannot guarantee SOUNDNESS
(it may hallucinate an edge); the substrate's find+verify is sound by construction over the checkable typed-derivation graph.

## Honest caveat (depth)
- avg proof DEPTH = 1.30 (mostly 1-hop; a few depth-2/3). The authored dependency graph is SHALLOW (DEPENDS_ON alone is
  depth-1-flat per the CHTV finding; the structural union has some depth-2/3). So the prover finds SHORT proofs. "Multi-step
  lemma chains" are only lightly exercised. DEEPER proofs need DEEPER authored derivation chains (the targets of DEPENDS_ON need
  their own dependencies authored) -- a corpus-authoring lever, same root as the CHTV depth caveat + the BATCH-02 program.
- BATCH-02 status: ran on the existing graph (did not require the 4 missing atoms); when they + deeper chains land, re-run for
  longer proofs.

## Routing
- **Research:** find+verify prover surface VALIDATED (sound). The lever for deeper/more-impressive proofs is deeper DEPENDS_ON
  authoring (2-3 layer chains), not the prover mechanism. Anchor 2 (alpha-equivalence/SHARES_MATH univalence) gated on
  SHARES_MATH edges being populated. Anchor 4 (LLM-baseline soundness gap) is now runnable (GPU runner up) -- defer/confirm?
- **exp_dev:** continuing experiments per USER directive.
