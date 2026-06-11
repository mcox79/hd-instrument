# exp_dev hand-off -- research: polysemy resolution guarantees (3x depth)

**Filed:** 2026-06-10 by research sub-agent (Sonnet, 3x operational drill).

**Trigger:** notes/research_drill_polysemy_deep_3x_2026-06-10.md -- PP-316 image-schema grounding HARD_FAIL 0.342 on real ConceptNet polysemic abstract concepts. Three formal guarantees now identified; concrete experiment anchors are ready. Prior 2x drill (notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md) established mechanism viability; this 3x drill adds proven math and implementation paths.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue items. Annotation reads allowed while paused; queue adds require ACTIVE state.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, lambda, alpha, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary

Three convergent formal guarantees for polysemy resolution identified:

1. **Landau ordered-phase guarantee** (textbook, Landau-Lifshitz): In the ordered phase (storage load alpha << alpha_c), ANY nonzero context field h = dot(context, sense_A) - dot(context, sense_B) selects sense_A. No threshold. Mathematically guaranteed for standard storage loads. PP-316 fails at 0.342 because h = 0 currently -- the cleanup step ignores context entirely.

2. **SAE exact recovery theorem** (arxiv 2506.14002, June 2026): Under sparsity + incoherence conditions, exact recovery of monosemantic features from polysemantic superpositions is proven. Conditions plausible for ConceptNet (sense vectors near-orthogonal; relation types sparse per concept).

3. **GHRR quasi-orthogonality bound** (arxiv 2405.09689, May 2024): Non-commutative binding residual noise is O(1/sqrt(N*m)), proven. For N=1024, residual < 0.02 -- below cleanup threshold. Clean algebraic disambiguation for nested sense hierarchies.

Additionally: DMHN energy function E(x,u) = -(1/2)*Phi(x)^T*[W_S + W_D(u)]*Phi(x) - Phi(x)^T*[I_S + I_D(u)] + leak_term is now fully extracted from arxiv 2506.01303. W_D(u) = (uW_wcue)^T*(uW_wcue) is PSD -- adding context ALWAYS increases depth of context-aligned attractor basin. No-training baseline: replace W_wcue with identity, giving score(i) = cos(query, atom_i) + alpha * dot(context, atom_i)^2.

---

## Anchor candidates (rank-ordered; exp_dev picks based on queue depth and tier policy)

### Anchor 1 -- PP-316 Landau context bias rescue (HIGHEST PRIORITY)
- **Anchor pointer:** Research note notes/research_drill_polysemy_deep_3x_2026-06-10.md, mechanism #3 (Landau field selection), Section "Cheap Decisive Test."
- **Substrate-product reading:** The Landau guarantee says ANY nonzero context signal disambiguates in the ordered phase (alpha << alpha_c). The PP-316 accuracy of 0.342 is almost certainly a zero-context-field failure, not a representation failure. One-line cleanup kernel change: add lambda * dot(context, atom_i) to similarity score. Context vector = mean of ConceptNet relation-type neighbor atoms for the target sense. Test on 50 polysemic abstract concepts from PP-316 failure set.
- **Tier hint:** CPU (pure numpy, no GPU needed). 2-4 hours estimated. Local queue appropriate.
- **Why now:** Landau guarantee is the strongest path (P_deflated = 0.44). Zero architectural change required. If it works, PP-316 is rescued immediately and the product gets context-aware abstract concept retrieval as a direct capability.
- **Hard-pass / hard-fail pre-reg:** Research note section "Falsifiable Predictions" (HP1: accuracy >= 0.60 with lambda=0.5; HF1: accuracy < 0.50 across all lambda).

### Anchor 2 -- PP-316 DMHN quadratic context bias
- **Anchor pointer:** Research note notes/research_drill_polysemy_deep_3x_2026-06-10.md, Stream E / mechanism #4 (DMHN PSD guarantee). DMHN energy function section.
- **Substrate-product reading:** DMHN quadratic context term score(i) = cos(query, atom_i) + alpha * dot(context, atom_i)^2. PSD guarantee: adding this term always increases the depth of context-aligned attractor basin. No W_wcue training needed (use identity). Compare against Anchor 1 (linear vs quadratic context term); one experiment tests both.
- **Tier hint:** CPU (same 50-concept test set). Can batch with Anchor 1 as a 2-condition experiment.
- **Why now:** DMHN has strongest empirical precedent (64% vs 13% at 2N storage per arxiv 2506.01303). Linear + quadratic terms are two hyperparameter conditions, not two experiments.
- **Hard-pass / hard-fail pre-reg:** HP2 in research note (accuracy >= 0.62 with quadratic term).

### Anchor 3 -- PP-316 neuromodulation gating capacity probe
- **Anchor pointer:** Research note notes/research_drill_polysemy_deep_3x_2026-06-10.md, Stream E mechanism E2 (neuromodulation gating). PMC12723791 source.
- **Substrate-product reading:** Sigmoid gating g_i = sigmoid(dot(context, atom_i) * beta) multiplied into cleanup score. Bypasses spin-glass transition without narrowing basins. If abstract concepts fail because local alpha exceeds alpha_c (too many senses per concept), gating is the fix -- it extends reliable retrieval to alpha > 2*alpha_c. Probe: count senses per polysemic concept; test gated cleanup vs ungated on concepts with high sense count.
- **Tier hint:** CPU. Can batch with Anchor 1/2 as a third condition. Low additional cost.
- **Why now:** If Anchor 1/2 fail (HF1), this is the immediate follow-up. Can run in parallel.

### Anchor 4 -- PP-316 GHRR re-indexing (sense-key binding)
- **Anchor pointer:** Research note notes/research_drill_polysemy_deep_3x_2026-06-10.md, Stream E mechanism E3 (GHRR quasi-orthogonal unbinding). arxiv 2405.09689 source.
- **Substrate-product reading:** Store each sense as K_s * V_s where K_s is the relation-type key vector (quasi-random unit vector in N-dim space). Retrieve using K_s^{-1} = K_s^* (conjugate, for FHRR; unitary inverse for GHRR). Residual noise O(1/sqrt(N)) proven. This is the highest-P_deflated path for multi-sense concepts with clear relation-type structure. Requires re-indexing ConceptNet atoms by relation type -- 4-8 hours engineering.
- **Tier hint:** CPU. Preprocessing pass over ConceptNet extract + accuracy test. Higher engineering cost than Anchor 1/2/3.
- **Why now:** Strongest algebraic guarantee (exact unbinding). Required if Anchor 1/2/3 all fail. Also the path that unlocks NESTED sense hierarchies (future product capability).

---

## Context pointers (file paths, not summaries)

- Research note (3x drill): d:/AI/hd-instrument/notes/research_drill_polysemy_deep_3x_2026-06-10.md
- Prior 2x drill: d:/AI/hd-instrument/notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md
- PP-316 image-schema experiment results: search data/exp_PP316*/metrics.json (or equivalent anchor name)
- ConceptNet extract: data/ directory (458K facts from ConceptNet 8M, loaded during testbed overnight chain)
- DMHN source: arxiv 2506.01303 (HTML version available at arxiv.org/html/2506.01303)
- GHRR source: arxiv 2405.09689
- SAE exact recovery source: arxiv 2506.14002

---

## Contract

exp_dev owns ALL of: anchor naming, N/lambda/alpha/seed/threshold choices, queue routing, smoke gate design, pre-reg band specification, and scheduling order. Research has named the mechanisms and provided the mathematical grounding; experiment design is exp_dev's domain.

Anchors 1/2/3 can be batched as a single experiment (three cleanup kernel conditions: linear context, quadratic context, sigmoid gating) on the same 50-concept held-out test set. This is the recommended batching.

Anchor 4 requires a preprocessing pass and should be scheduled as a separate experiment after Anchors 1/2/3 produce a verdict.

---

## Autonomy declaration

exp_dev decides:
- Whether to treat Anchors 1/2/3 as one experiment or three
- Lambda, alpha, beta hyperparameter ranges
- Whether to use the 50-concept set from PP-316 or a freshly sampled set
- Queue placement (local_cpu_queue preferred; no GPU needed)
- Smoke gate design and threshold bands
- Whether to dispatch Anchor 4 before or after Anchors 1/2/3 verdict
