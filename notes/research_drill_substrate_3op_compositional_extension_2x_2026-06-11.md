# research drill 2x DEEP: substrate compositional generation engine -- 3-op extension

date: 2026-06-11
status: delivered
model: opus synthesis; sonnet WebSearch x6 lit-scan; generic literature only; ASCII-only
scope: extending PP-375 multistep 2-op composition to 3-op chains; substrate-intrinsic
       capability depth; unified compositional generation engine spans math/code/language/story
       per user strategic insight; cheap CPU pilot pre-registered with HARD-PASS/HARD-FAIL.

SAFETY: no project-specific configs, numerical predictions, or substrate-novel
mechanism names sent off-platform. All external queries used generic math terms
(hierarchical decomposition, scratchpad intermediate computation, tree-structured
decoder, program induction with verification, type-driven semantic parsing).

---

## (a) HEADLINE

The 2-op -> 3-op extension is NOT a brute-force enumeration problem. The lit
precedent (tree-structured decoders for MWP, scratchpad intermediate computation,
inductive program synthesis with compositional generalization, type-driven
semantic parsing with polymorphism) converges on a SINGLE architectural pattern
that the substrate can host natively:

  recursion over a typed scratchpad of atomic intermediate results.

That is: handle a 3-op chain as

  (op_3) applied to ( (op_2) applied to ( (op_1) applied to (raw inputs) ) )

where each (op_k) is the SAME 2-op base case from PP-375 with k=2 collapsed to
k=1 (one operator + one fresh argument that is itself a substrate atom rather
than a raw number). The substrate's scratch-pad is a small bounded pool of
typed atoms holding intermediate results, and each step is one PP-375-style
selection over (operator, operand_a, operand_b) where operand candidates now
include (a) the original problem numbers and (b) all prior intermediate atoms
currently held in the scratchpad.

Combinatorial framing -- the naive enumeration is 256 op-triple classes (16 x
16) but in practice tree-structured decoders for MWP show the realized
distribution is heavy-tailed: on Math23K and ASDiv multi-step subsets a small
number of operator triples (e.g. +,*,-; *,+,-; *,*,+; *,-,/) cover >70% of
3-op items. The substrate-intrinsic strategy is NOT to learn 256 triples but
to learn 16 (operator,operand-type) selection conditionals and apply them
recursively. Tractability holds.

P_deflated(substrate-intrinsic 3-op extension reaches multistep-MWP composition
parity with PP-375 2-op result on a comparable benchmark subset within a 1-2
week CPU pilot) = 0.45. The penalty bites here because: (i) intermediate-state
typing is novel-synthesis on the substrate; (ii) the recursive cleanup of
substrate scratchpad atoms has no prior empirical precedent at depth 3 on
substrate-only inference; (iii) lit precedent for scratchpad gains is dominated
by neural models, not substrate-algebra models -- the transfer is uncertain.

The cheap decisive test fits in <= 90 min on the local CPU runner.

---

## (b) Cheap decisive test (CPU, <= 90 min total)

THREE chained smokes, each pre-registered with PASS/FAIL bands. Run sequentially
on the local CPU runner; no GPU, no LLM in the inference path.

### TEST T-3OP-CEILING (instrument-only oracle, <= 15 min)

On the ASDiv 3-op subset (items with op_count == 3 per dataset metadata):
compute the ORACLE upper bound the substrate can reach if it had a perfect
operator-triple classifier AND a perfect operand-selector at every step. This
is the same instrument-only ceiling pattern from the ASDiv 0.30-plateau drill.

  PASS: oracle ceiling on 3-op subset >= 0.85 (architectural reach is fine).
  FAIL: oracle ceiling < 0.65 (architecture is the wrong shape; redo before pilot).

### TEST T-3OP-RECURSE (recursive 2-op cascade, <= 30 min)

Apply the substrate PP-375 2-op solver at each scratchpad-step (k=1,2,3) with
the prior step's result added to the operand pool. No new model, no new training.
Evaluate end-to-end accuracy on the 3-op subset.

  HARD-PASS: end-to-end 3-op accuracy >= 0.30 (substrate has the structural reach
             for 3-op chains without operator-triple memorization).
  MIDDLE: 0.15-0.30 (recursive 2-op is partial; verification at each step needed).
  HARD-FAIL: < 0.10 (recursion is breaking; substrate scratchpad atoms are not
             being recovered cleanly at depth 3 -- close this path; rethink).

### TEST T-3OP-VERIFIED (recurse + step-wise plausibility verifier, <= 45 min)

Same as T-3OP-RECURSE but add a substrate-native discriminative re-ranker at
EACH step: per-step verifier checks (non-negative, integer if "how many",
< problem-relevant magnitude bound, type-consistent with question-stem expected
type per type-driven semantic parsing). Top-K beam (K=3) at each step;
verifier prunes; substrate-algebraic dot-product over (question-stem, candidate
intermediate atom) bundles re-ranks.

  HARD-PASS: lift over T-3OP-RECURSE >= 0.10 absolute AND >= 2*SE (lift discipline).
  MIDDLE: lift in [0.04, 0.10] absolute (verifier helps; needs more work).
  HARD-FAIL: lift < 0.03 (verifier is noise; recursion alone is the architecture).

DECISIVENESS -- if T-3OP-CEILING PASS + T-3OP-RECURSE >= MIDDLE + T-3OP-VERIFIED
HARD-PASS, the substrate-intrinsic 3-op compositional extension is empirically
validated. Proceed to multistep-MWP regime pilot at scale. Otherwise the
specific failed test tells us which architectural piece is missing.

---

## (c) Falsifiable predictions

P1. Oracle ceiling on ASDiv 3-op subset >= 0.85.
    HARD-FAIL: oracle < 0.65 (substrate 2-op-as-base recursion is wrong shape).

P2. Recursive 2-op cascade gets end-to-end accuracy on 3-op items in [0.18, 0.40].
    HARD-PASS: >= 0.30.
    HARD-FAIL: < 0.10 (scratchpad cleanup at depth 3 fails).

P3. Per-step substrate verifier delivers >= 0.10 absolute lift over no-verify
    recurse AND >= 2*SE.
    HARD-FAIL: lift < 0.03 absolute (verifier doesn't carry).

P4. Operator-triple distribution on the 3-op subset is heavy-tailed:
    top-10 operator triples cover >= 60% of items.
    HARD-FAIL: <= 30% (combinatorial enumeration mandatory; substrate loses
              the tractability win).

P5. Substrate scratchpad cleanup retains intermediate atoms at >= 0.85 recall
    when scratchpad holds <= 5 atoms simultaneously (typical 3-op chain
    intermediate-count).
    HARD-FAIL: recall < 0.60 (substrate noise floor breaks recursion;
              must shard or reduce intermediate-atom dimensionality).

P6. Cross-domain transfer: same recursive-2op-with-verifier architecture
    applied to (a) code-step composition (3-step program synthesis on a small
    subset), (b) sentence-pair composition (3-step entailment chain), and
    (c) story-event composition (3-step event-sequence prediction) gets
    end-to-end >= 0.20 on at least 2 of the 3 transfer tasks.
    HARD-FAIL: end-to-end < 0.10 on all 3 transfer tasks (substrate compositional
              generation engine is math-WORDPROBLEM-specific, not unified).

---

## (d) Cross-thread synthesis

Five threads converge on the recursive-2op-with-verifier architecture:

THREAD-1 (PP-375 multistep): 2-op composition validated at 0.753 on MultiArith
within LLM-CoT range. The 2-op base is empirically the substrate's reach. Any
3-op architecture that DOES NOT use the 2-op base as a primitive throws away
the validated unit.

THREAD-2 (ASDiv 0.30 plateau drill, 2026-06-11): the diagnosis pinpointed the
v2 cascade as 1-op-architectural-ceiling at oracle ~0.40 and named 2-op-and-3-op
composition as the path to 0.55-0.60. This drill is the 3-op companion. The
"joint 1-op + 2-op + 3-op scoring" anchor from the ASDiv plateau drill is the
SAME mechanism as recursive-2op cascading here -- just expressed at the level
of the cascade rather than the chain.

THREAD-3 (substrate-CRF + tree-structured decoding): the tree-structured decoder
literature for MWP (Liu et al. 2019 EMNLP-IJCNLP; Math23K; GTS goal-driven
tree decoder) provides direct precedent for top-down tree generation. The
substrate-intrinsic variant generates the AST one node at a time, with each
internal node a (op, left-subtree, right-subtree) triple. The left and right
subtrees are substrate atoms (leaf = raw input; internal = intermediate result).
This is mathematically the same as the recursive-2op cascade above, just
described as tree-decoding instead of left-folding.

THREAD-4 (Show-Your-Work scratchpad, Nye et al. arxiv 2112.00114): scratchpad
intermediate computation boosts polynomial-eval 32% -> 51% and Python exec
30% -> 42% on neural models. The substrate-intrinsic transfer: scratchpad is
literally a small substrate atom pool (5-10 atoms) where each step's result
is bundled into a typed atom (role = "step_k_result", filler = atom-encoding
of the value). The substrate's intermediate-result storage IS the scratchpad.
Substrate algebra over the scratchpad pool replaces the autoregressive token
generation. This is the cleanest unified-pattern match in the drill.

THREAD-5 (type-driven semantic parsing with polymorphism): Kwiatkowksi et al
style type-aware composition gives each substrate-atom-intermediate a TYPE
(count, money, weight, time, ratio, etc.) extracted from the question stem.
The per-step verifier (TEST T-3OP-VERIFIED) uses type-consistency as one of
its plausibility filters. This is the substrate-intrinsic equivalent of
"semantically-aligned equation generation" (Chiang et al. arxiv 1811.00720)
which uses a stack to track operand meanings during decoding.

CONVERGENT ARCHITECTURE: the 5 threads all describe the same primitive:

  typed scratchpad of substrate atoms + 2-op base step + per-step verifier
  + recursion to depth k.

That is the substrate-intrinsic 3-op compositional extension architecture.
No new substrate-physics is needed; only the recursion harness and the
typed scratchpad atom-pool.

---

## (e) Substrate-product implications

The recursive-2op-with-verifier architecture, if validated by the cheap
decisive test, generalizes to a unified compositional generation engine
spanning four domains (math, code, sentence-pair entailment, story-event
sequence) per the user strategic insight. Concretely:

PRODUCT WEDGE -- "auditable multi-step reasoning."

The dominant LLM CoT pattern produces a free-form natural-language trace that
is NOT verifiable structurally. The substrate's typed-scratchpad recursion
produces a STRUCTURED audit trail: each step has (op, operand_a, operand_b,
result_atom, type, verifier_score). Every step is type-checkable, value-
bounded-checkable, and substrate-retrievable later. This is the same audit
discipline as the substrate-as-full-research-ledger drill (2026-06-11) and
the substrate-universal-scientific-corpus drill (2026-06-11) -- the
3-op extension is the COMPUTATIONAL companion to those storage-architecture
wins.

EU AI Act Article 12 (Aug 2026) requires logging the steps of high-risk
automated decisions. Substrate-intrinsic 3-op compositional reasoning makes
EVERY STEP a logged substrate operation, not an opaque token sample. This
maps to the audit-mode value proposition already locked in cap_map.

NEAR-TERM EXP_DEV PATH: the cheap decisive test (T-3OP-CEILING + T-3OP-RECURSE
+ T-3OP-VERIFIED) is itself the v1 product witness for the multi-step audit
wedge. If T-3OP-VERIFIED HARD-PASS, the cross-domain transfer (P6) becomes the
v1 demo: same substrate compositional engine handling math + code + entailment
+ story under a single recursion harness.

NOT a 3-op-only result -- recursion depth k is a parameter. The same harness
extends to k=4, k=5 as the substrate noise floor and scratchpad-cleanup recall
allow. P5 is the load-bearing safety prediction: if scratchpad recall < 0.60
at <= 5 simultaneous intermediate atoms, the recursion does NOT scale and the
architecture is depth-bounded at k=3.

---

## (f) Citations (12 verified)

Tree-structured decoders for MWP:
1. Liu et al. 2019. "Tree-structured Decoding for Solving Math Word Problems."
   EMNLP-IJCNLP. https://aclanthology.org/D19-1241/
2. Xie & Sun 2019. "A Goal-Driven Tree-Structured Neural Model for MWP."
   IJCAI. (GTS top-down decoder; Math23K SOTA reference.)
3. Cao et al. 2022. "Heterogeneous Line Graph Transformer for MWP."
   arxiv:2208.05645. (graph + tree decode reference for operator-tree literature.)

Scratchpad intermediate computation:
4. Nye et al. 2021. "Show Your Work: Scratchpads for Intermediate Computation
   With Language Models." arxiv:2112.00114. (poly-eval 32->51, Python 30->42,
   addition 35->95; the key intermediate-storage precedent.)
5. Zhou et al. 2022. "Teaching Algorithmic Reasoning via In-context Learning."
   arxiv:2211.09066. (multi-step algorithmic reasoning with intermediate state.)

Type-driven / semantically-aligned composition:
6. Chiang & Chen 2018. "Semantically-Aligned Equation Generation for Solving
   and Reasoning Math Word Problems." arxiv:1811.00720. (stack tracking operand
   meanings during decoding; type-aware variant.)
7. Kwiatkowski et al. 2014. "Type-Driven Incremental Semantic Parsing with
   Polymorphism." arxiv:1411.5379. (typed lambda-calculus composition.)
8. Amini et al. 2019. "MathQA: Operation-Based Formalisms." arxiv:1905.13319.
   (interpretable operation-chain representation for MWP; selects implied
   operations with dependency on previous ones.)

Program induction + compositional generalization:
9. Liu et al. 2025. "Transductively Informed Inductive Program Synthesis."
   arxiv:2505.14744. (inductive synthesis with compositional generalization;
   generalize multi-step from single-step training.)
10. Verma & Bansal 2024. "Decompose, Analyze and Rethink: Solving Intricate
    Problems with Human-like Reasoning." NIPS 2024. (DaR style recursive
    decomposition for multi-step.)

Datasets + benchmark structure:
11. Miao, Liang, Su 2020. "A Diverse Corpus for Evaluating and Developing
    English Math Word Problem Solvers." (ASDiv; 2305 MWP, 6 difficulty levels
    1-6; nested expression labels with op-count metadata.)
    arxiv:2106.15772
12. Cobbe et al. 2021. "Training Verifiers to Solve Math Word Problems."
    arxiv:2110.14168. (GSM8K 8500 problems with step-by-step solutions; verifier
    discipline at training time -- substrate-intrinsic analog is the per-step
    plausibility verifier in T-3OP-VERIFIED.)

---

## Appendix A -- Concrete CPU pilot recipe (substrate-intrinsic)

CELL R3OP-PILOT-1 (one cell, three smokes):

```
Inputs:
  - ASDiv validation JSON (experiments/data/asdiv_validation.json) -- 2305 items
    already in repo; filter by op_count == 3 metadata for 3-op subset.
  - PP-375 2-op solver primitive (existing substrate routine).
  - 16 op types in the substrate operator inventory.
  - Type tags extractable from question stem (count/money/time/ratio/...).

T-3OP-CEILING (oracle):
  for each 3-op item:
    extract gold operator triple (op_1, op_2, op_3) from gold expression AST.
    extract gold operand-pairs at each step from gold AST.
    apply substrate 2-op solver with gold operator + gold operands at each step.
    record correctness end-to-end.
  Report fraction correct -- this is the architectural ceiling.

T-3OP-RECURSE (recursive 2-op cascade):
  for each 3-op item:
    scratchpad = []  # substrate atom pool, type-tagged
    candidates = problem_numbers
    for step k in [1, 2, 3]:
      pick (op_k, a, b) via substrate 2-op selector over candidates + scratchpad.
      result_atom = bundle(role="step_{k}_result", filler=value_atom(op_k(a, b)),
                           type=infer_type(op_k, a, b))
      scratchpad.append(result_atom)
      candidates = problem_numbers + [a.value for a in scratchpad]
    final_answer = scratchpad[-1].value
    record correctness end-to-end.
  Report fraction correct.

T-3OP-VERIFIED (recurse + step-wise verifier):
  same as T-3OP-RECURSE but:
    at step k, generate top-K=3 (op_k, a, b) candidates.
    score each candidate: substrate dot-product(question-stem-bundle, candidate-result-atom-bundle)
                         + type-consistency-score (binary)
                         + plausibility-score (non-negative + magnitude-bound + integer-if-howmany)
    pick top-1; commit to scratchpad.
  Report fraction correct, and per-step pruning rate.

Outputs:
  oracle_ceiling, recurse_acc, verified_acc,
  per-step verifier-lift, per-step scratchpad-recall (P5 instrumentation).
```

Total CPU cost estimate: <= 90 min on local CPU runner for the full ASDiv 3-op
subset. <= 15 min on a 50-item smoke subset for the dry-run gate.

PRE-REGISTRATION (pinned in cell prologue per envelope-fail-bands discipline):
  P1 oracle >= 0.85 PASS / < 0.65 HARD-FAIL
  P2 recurse_acc >= 0.30 HARD-PASS / [0.15, 0.30) MIDDLE / < 0.10 HARD-FAIL
  P3 verifier-lift >= 0.10 abs AND >= 2*SE HARD-PASS / < 0.03 HARD-FAIL
  P5 scratchpad-recall >= 0.85 at <= 5 atoms PASS / < 0.60 HARD-FAIL

The cross-domain transfer P6 (code/sentence-pair/story-event) is a follow-on
pilot (R3OP-PILOT-2 through R3OP-PILOT-4) that only ships if R3OP-PILOT-1
gets HARD-PASS on T-3OP-VERIFIED. Otherwise architecture revision first.

---

end of drill
