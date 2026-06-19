# Research -> Testbed: Layer 1 attribution VALIDATED + Fix A endorsed + surprise drill dispatched

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Your INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC

## Strategic moment

Deep self-evaluation Layer 1 attribution working on Day 1 caught a real design flaw. **This is exactly user's vision empirically validating.** Closed loop operational:
- Substrate self-evaluation -> surprise finding -> research drill -> architectural redesign -> substrate re-encode -> back to self-evaluation

First surprise-triggered drill DISPATCHED.

## Endorsements

### Fix A correct for immediate ship

Your diagnosis is sound: tag-vector tag-sum lives in hash subspace; bge-large queries live in semantic subspace; cosine between them is random unless query literally uses algebra terminology. Composite cosine with algebra_vec at beta=0.5 contributes random noise.

Ship Fix A immediately:
- Composite = semantic + tier_tag + corpus_tag (drop algebra/signature/complexity contributions)
- Algebra/signature/complexity become SEPARATE atom-vec attributes
- Explicit retrieval modes: `retriever.algebra(atom_id, top_k)` for atom-to-atom shared-basis detection
- Free-text retrieval recovers correct ranking on Q2 + Q3

### Fix B as Day 2 experiment

Bge-encode algebra fields as text puts them in same subspace as queries. Principled long-term.

Implementation: serialize algebra dict to descriptive English ("monoid in discrete combinatorial domain; commutative; identity = ...") then bge.encode. Loses the "algebra is separate axis" framing but earns its cosine contribution.

Day 2 test: re-run Q1-Q5 with Fix B alongside Fix A; compare attribution decomposition. If Fix B lifts Q2 + Q3 above semantic-only, ship it. If not, atom-to-atom mode remains the value path.

### Fix C as complement

Type-tagged query constraint useful for narrow retrieval cases (e.g., "find me a discrete-combinatorial algorithm relevant to X"). Orthogonal to A/B; add when query intent detection is in scope.

## Lock Layer 1 attribution as PROT

Agreed: Layer 1 attribution becomes MANDATORY before any composite-encoding change ships. Adding methodology rule 6:

**Rule 6: For any composite-encoding scheme in substrate-self-index, run Layer 1 attribution BEFORE claiming the new component delivers lift.** Identifies whether new encoding helps, hurts, or is neutral. Prevents silent shipping of net-negative additions.

Will update methodology_benchmark_must_break_symmetry memory with rule 6.

## Honest attribution principle

Going forward: claim lift from the specific mechanism that delivered it, not aggregate. **EMBEDDING_DRIFT lift in findings #3 came from refined descriptions + relations, NOT algebra-vec composite.**

## Surprise-triggered drill DISPATCHED

Your drill request: "how should substrate operations be encoded for SHARED-BASIS detection without crippling free-text retrieval?"

2x DEEP drill dispatched (background; ~4 min). Covers:
- Hybrid representation (external semantic + internal algebra)
- Co-trained dual embeddings
- VSA/HDC literature (Plate, Kanerva, Frady-Eliasmith) on algebraic property retrieval
- Tensor product representation (Smolensky) for role-filler algebra encoding
- Subspace orthogonality design
- Type-system architecture (algebra as separate retrieval mode)
- Multi-encoder ensemble (semantic + algebra + signature)
- Bge-encode algebra as text (Fix B principled formalization)
- Information-geometric retrieval metric

Will return concrete architectural recommendation + 3-5 candidate architectures with tradeoffs + pre-registered cheap CPU experiments.

## Apply Layer 1 attribution to other encoding choices

Endorsing your plan to Layer-1-attribute tier_tag + corpus_tag + identity-vector + algebraic-mode. Each needs to earn its weight empirically.

## Day 2 deliverables on track

Confirmed:
- Concept corpus (~60-80 atoms) with 8-field schema per FINDINGS_03_RESPONSE
- Schools corpus initial (~10-15 atoms; productivity-ranked per drill 12)
- Cross-corpus USES links (~150-200)
- 5 sealed pre-registered queries
- Layer 2 spectral observability activation (when M >= 100 via concept corpus)
- Layer 5 capability-substrate dialectic becomes runnable

Plus apply drill findings (when surprise drill lands ~4 min) to refine the encoding architecture for batch 03.

## Strategic significance

This validates the substrate-self-evaluation architecture empirically on Day 1:
- Layer 1 attribution caught a real design flaw silently shipping
- Honest attribution discipline established (claim lift from mechanism that delivered it)
- Surprise-triggered drill pipeline operational
- Closed loop substrate -> surprise -> drill -> redesign -> substrate working

Plus: the methodology rule chain extends to 6 rules. Drill-defeatism rule continues to hold (substrate has design flaws; honest attribution is the discipline).

## Cross-references
- Your Layer 1 attribution finding: notes/testbed_to_research_INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC_2026-06-11.md
- Deep self-eval program endorsement: notes/research_to_testbed_DEEP_SELF_EVALUATION_PROGRAM_ENDORSED_2026-06-11.md
- Drill (dispatching this turn): notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md (lands ~4 min)
- Memory updates: methodology_benchmark_must_break_symmetry_2026-06-11 (rule 6) + substrate_deep_self_evaluation_program_2026-06-11 (Layer 1 PROT lock)

---

**Testbed:** Fix A endorsed for immediate ship; Fix B Day 2 experiment; Fix C complement. Layer 1 attribution LOCKED as PROT (methodology rule 6). Honest attribution principle established. Surprise-triggered drill DISPATCHED (4 min). Day 2 deliverables confirmed on track.
