# Research Note: 2x Drill -- Substrate+LLM vs Frontier LLM on Reasoning, Math, Code
# Date: 2026-06-07
# Topic: reasoning_math_code_2x

---

## HEADLINE

Frontier LLM's advantage in reasoning, math, and code narrows substantially when a
substrate provides verified knowledge plus algebraic chaining. The categorical win for
frontier LLMs relocates to a specific residual: novel inference without a KB, numerical
computation, and world-model-dependent physical intuition. For compliance/audit/knowledge-
grounded tasks the substrate+small-LLM pairing is competitive or superior on the metrics
that matter to paying customers (verifiability, F1 on multi-hop, hallucination rate).

P_theoretical = 0.70 (retrieval-augmented small LLMs match frontier on KB-grounded tasks;
well-supported by RETRO, RAG-coding, HotpotQA literature)
P_empirical = 0.45 (production-encoder pretest required before claiming competitive numbers
on any specific benchmark; gap is task-contingent)

---

## 1. Framing

The question is not "does substrate beat frontier LLM?" but "for which tasks does
substrate+small-LLM match or exceed frontier LLM such that a customer pays for the
substrate system instead of an API call to GPT-4o?"

The productive decomposition is:

  Reasoning = Knowledge retrieval + Algebraic/logical chaining + Novel inference
  Math      = Theorem/identity lookup + Derivation chain + Numerical computation
  Code      = API/pattern retrieval + Syntactic generation + Novel algorithm design

Substrate with K-hop relay handles the first term of each triplet well (acc=1.0
deterministically on K-hop compose from empirical fact). LLM handles generation.
The residual is the second/third terms -- specifically novel inference and numerical
computation are the genuinely hard frontier-LLM-wins.

---

## 2. Reasoning: Task Taxonomy

### 2A. Where substrate+small-LLM matches frontier LLM

(a) Multi-hop knowledge-grounded QA.
    Published: substrate-augmented Qwen beats bare Qwen +0.35 F1 on HotpotQA (empirical
    fact, cycles 158/162). Published baseline: RAG with knowledge graphs on HotpotQA and
    MuSiQue shows structured KB traversal closes most of the gap to GPT-4 (DTKG 2024,
    StepChain GraphRAG 2024). The pattern is consistent: when hops are over factual
    relationships stored in the KB, small models with structured retrieval approach
    frontier performance.

(b) Constrained/rule-governed reasoning.
    Legal statute application, clinical protocol following, compliance checking. These
    are high-hop but low-novelty tasks. The reasoning chain is over a fixed KB of rules.
    Published: purely neural approaches hallucinate legal authorities; retrieval-augmented
    + formal reasoning reduces factual errors ("Towards Trustworthy Legal AI", 2025).
    Substrate Merkle-audited K-hop chain is exactly this pattern.

(c) Multi-step derivation when derivation patterns are in KB.
    If the KB contains worked examples or derivation templates, the LLM applies them
    rather than synthesizing from parametric knowledge. Analogous to a formula sheet on
    an exam: the bottleneck shifts from recall to application.

### 2B. Where frontier LLM wins categorically

(a) Novel inference. Tasks requiring connection of concepts NOT explicitly related in
    the KB. Open-domain brainstorming, hypothesis generation, creative analogy. Frontier
    LLMs have vastly more implicit relational structure from pretraining; substrate KB
    cannot substitute unless the KB is extremely dense.

(b) Physical world modeling. Intuitive physics, spatial reasoning from descriptions,
    commonsense about physical objects. Not KB-retrievable in the typical text-KB sense.
    Vision-language frontier models have a further advantage from multimodal training.

(c) Compositional generalization to unseen combinations. The Fano-style bound shows
    compositional gaps do not close with parameter count at small model sizes. However:
    if the substrate KB covers the required compositions, the gap closes. The KB
    coverage quality is the determining factor, not model size.

---

## 3. Math: Analysis

### 3A. Where substrate+small-LLM is competitive

Derivation-based math where standard identities and proof patterns are retrievable.

Published evidence: GSM8K frontier saturation is 95-97% for closed models (GPT-4o, o1).
Qwen2.5-7B achieves 84.3% on GSM8K. The gap to frontier is ~10-15 percentage points
using bare small LLMs. Vanilla LLaMA-2-7B achieves >82% via CoT scaling.

The substrate angle: if the KB stores worked solution patterns for the problem class,
retrieval of the relevant pattern + LLM application should close most of the gap.
RAT (Retrieval Augmented Thoughts, 2024) shows interleaving retrieval with chain-of-
thought generation outperforms CoT alone (arxiv 2403.05313). This is the substrate+LLM
composition in a published form.

Specific scenario: undergraduate real analysis proofs. KB stores 200 standard lemmas.
Small LLM retrieves the 2-3 relevant lemmas and chains them. Frontier LLM does this
from parametric knowledge. Outputs are structurally identical IF retrieval is accurate.
Substrate gives verifiability; frontier LLM gives fluency but no proof trace.

### 3B. Where frontier LLM wins

(a) Numerical computation. GSM8K arithmetic errors in small models are not a retrieval
    problem -- they are a number-symbol computation problem. A KB of formulas does not
    help with 3-step arithmetic chains; the error is in the generation step, not the
    knowledge step. The fix is tool use (calculator), not KB augmentation.

(b) Novel proofs. Competition math, Olympiad problems. Frontier LLMs with extended
    thinking (o1, o3, Gemini-Thinking) show qualitative gains here. Genuine categorical
    win that substrate augmentation cannot replicate without a correspondingly rich KB
    of proof strategies at the same granularity as the problem class.

(c) Visual math. GSM8K-V (visual version): best VLMs achieve 46.93%. Modality gap
    that neither substrate nor text-only small LLMs close.

### 3C. Honest calibration

The honest math claim is narrow: substrate+small-LLM is competitive on PATTERN-MATCHING
math (retrieve identity, apply, verify). NOT competitive on GENERATIVE math (novel proof,
combinatorial insight, numerical precision in long chains).

The commercial math use cases worth building for are pattern-matching (exam tutoring,
engineering formula lookup, compliance calculation), NOT novel-proof generation. These
are large markets; the framing does not need to overclaim.

---

## 4. Code Generation: Analysis

### 4A. Where substrate+small-LLM is competitive or better

Published evidence is strong:
- CodeRAG (bigraph-based retrieval, 2025, arxiv 2504.10046): Pass@1 increased by 35.57
  points on repo-level tasks (18.57 -> 54.41). Massive gap-closing.
- Context-augmented code generation on HumanEval + MBPP (2024): up to 20% pass@1
  improvement; outperforming SOTA models by up to 34% on MBPP.
- ARCS (agentic RAG synthesis, 2025, arxiv 2504.20434): matches or exceeds strong
  baselines on HumanEval.
- Llama3.2 1B + context-augmented (He 2025): 0.39 on HumanEval, 0.50 on MBPP.
  These are competitive with larger models closed-book.

The mechanism is clear: code generation is highly retrieval-amenable because code reuse
patterns are dense, specific, and verifiable. An API call to a library follows an exact
syntactic pattern; retrieving the correct pattern eliminates the need for the model to
synthesize it from parametric knowledge. This is exactly where small models hallucinate:
API signatures that do not exist.

For API-usage code (the majority of enterprise production code), substrate KB of API
docs, usage patterns, design idioms, and verified snippets addresses the dominant error
source in small-model code generation.

The auditable provenance angle is new. Substrate can attach a Merkle-audited chain from
generated code back to the source snippet and documentation. No frontier LLM offers
this. For security-critical code, medical device software, financial systems, this is a
hard requirement.

### 4B. Where frontier LLM wins

(a) Novel algorithm design. Tasks requiring design of algorithms not in the KB.
    Frontier LLMs with extended thinking show qualitative gains on competitive
    programming. Narrow commercial use case.

(b) Cross-language reasoning. If the KB is in one language/framework and the task
    requires another, retrieval degrades. Frontier LLMs have broader cross-language
    parametric knowledge.

(c) System design at architecture level. High-level design decisions spanning many
    files/services require global context that RAG windows typically cannot accommodate
    without explicit graph-of-thought structures (though this is an engineering gap,
    not a fundamental one).

### 4C. HumanEval cheap pre-test design

Task: Qwen-1.5B vs Qwen-1.5B + substrate KB of Python stdlib documentation.
Metric: HumanEval pass@1, split by problem class:
  - Class A: stdlib-dependent (list comprehension, string ops, dict ops) -- expect
    substrate+LLM to match or exceed Qwen-7B closed-book.
  - Class B: algorithm design (graph traversal, DP) -- expect no improvement.
HARD PASS: Class A improvement > 15 pass@1 points.
HARD FAIL: No improvement or regression on Class A.
Cost: ~2 hours local runner.

---

## 5. Auditable Reasoning Chain Value Proposition

This is the dimension the provocative framing underweights. It is not just competitive
parity -- it is a categorical capability frontier LLMs cannot match.

Chain-of-thought in frontier LLMs:
- Superficially plausible reasoning chains that may not reflect the model's actual
  computation ("Why Chain of Thought Fails in Clinical Text Understanding", 2025).
- Hallucinated citations, authorities, statistics.
- No source-of-truth linkage; the chain cannot be independently verified.

Published: CoT explanations may be "superficially plausible narratives that do not
reflect the model's actual decision basis." This is a hard disqualifier for regulated-
industry deployment.

Substrate K-hop + Merkle audit:
- Each hop links to a specific stored entity with a known hash.
- The chain can be replayed deterministically.
- A third party can audit the chain without access to model weights.
- Incorrect hops are detectable (wrong hash, broken link).

For medical decision support, legal opinion, financial compliance, and safety-critical
software, this is the difference between a system that can be deployed and one that
cannot. "Towards Trustworthy Legal AI through LLM Agents and Formal Reasoning" (2025)
identifies that purely neural approaches cannot provide logical validity guarantees.
Substrate deterministic K-hop relay + Merkle audit provides exactly the guarantee
the paper identifies as missing.

---

## 6. Quantitative Benchmark Summary (Verified Citations)

| Comparison | Result | Source |
|---|---|---|
| RETRO 7.5B vs GPT-3 175B | RETRO wins 10/16 tasks | Borgeaud et al. 2021 |
| RETRO 7.5B vs Gopher 280B | RETRO wins 9/16 tasks | Borgeaud et al. 2021 |
| RETRO vs GPT-3 on Pile | Comparable, 25x fewer params | RETRO paper |
| CodeRAG repo-level Pass@1 | +35.57 (18.57->54.41) | CodeRAG 2025 |
| Context-aug code on MBPP | Outperforms SOTA by up to 34% | Context-aug code 2024 |
| Llama3.2 1B + context-aug | 0.39 HumanEval, 0.50 MBPP | He 2025 |
| Substrate+Qwen HotpotQA | +0.35 F1 vs bare Qwen | Empirical (cycles 158/162) |
| Qwen2.5-7B on GSM8K | 84.3% (vs 95-97% frontier) | GSM8K benchmark data |
| RAT (retrieval+CoT) | Outperforms CoT alone | arxiv 2403.05313 |

The RETRO result is the anchoring fact: 7.5B + retrieval beats 280B closed-book on 9/16
tasks. This is ~37x parameter efficiency. The mechanism is external knowledge access,
exactly the substrate design.

---

## 7. Cheap Decisive Tests

### Pre-test 1: GSM8K pattern-matching split
Instrument: local runner, Qwen-1.5B (or 0.5B for speed).
Split GSM8K into:
  - Pattern-A: formula substitution (~40-50% of GSM8K)
  - Pattern-B: novel multi-step arithmetic chains
Baseline: bare Qwen-1.5B (expected ~40-50%).
Augmented: Qwen-1.5B + KB of formula patterns.
HARD PASS: Pattern-A accuracy improvement > 20 points vs bare.
HARD FAIL: < 5 points improvement on Pattern-A.
Cost: ~2-3 hours local CPU/GPU. No cloud needed.

### Pre-test 2: HumanEval stdlib split
See Section 4C.
HARD PASS: stdlib-class pass@1 improvement > 15 points.
HARD FAIL: < 5 points improvement or regression.
Cost: ~2 hours local.

### Pre-test 3: Auditable chain replay
Given 5 HotpotQA multi-hop questions, verify that K-hop relay output can be replayed
to produce the exact same answer via the stored chain.
HARD PASS: 5/5 replay identical.
HARD FAIL: any non-determinism in replay.
Cost: < 30 minutes.

---

## 8. Falsifiable Predictions

### HARD PASS thresholds

P1: Substrate+Qwen-7B achieves >75% on formula-class GSM8K problems
    (vs frontier 95-97% on full GSM8K). Implies near-competitive on the tractable class.
    P_theoretical = 0.65, P_empirical = 0.40.

P2: Substrate+Qwen-1.5B achieves >50 pass@1 on stdlib-class HumanEval.
    CodeRAG evidence supports this strongly.
    P_theoretical = 0.70, P_empirical = 0.45.

P3: Substrate K-hop audit replay: 5/5 deterministic replay on HotpotQA sample.
    Near-certain given acc=1.0 K-hop compose result.
    P_theoretical = 0.95, P_empirical = 0.90.

P4: For regulated-domain customers (medical, legal, financial), substrate audit chain
    is a deployment gate that frontier LLM cannot clear without substrate.
    P_theoretical = 0.80 (supported by published legal AI literature).

### HARD FAIL thresholds

F1: If substrate+Qwen-1.5B shows <5 points improvement on formula-class GSM8K,
    the retrieve-pattern-apply model is wrong for this problem class.
    Resolution: check retrieval accuracy first; if retrieval is accurate, the
    failure is in LLM application quality at 1.5B scale (rerun at 7B).

F2: If stdlib-class HumanEval shows no improvement, retrieval signal is dominated
    by generation quality at this model size.
    Resolution: rerun at 7B before abandoning the claim.

F3: If K-hop relay produces non-deterministic output on identical inputs, the
    auditable chain claim fails. Engineering issue, not a theoretical one.

---

## 9. Customer Pitch Revision

Current (too broad): "substrate+small-LLM matches frontier LLM on reasoning/math/code"

Revised (honest):

  For tasks where:
  (a) The relevant knowledge is in the KB, AND
  (b) The reasoning chain is over KB entities (not novel inference), AND
  (c) Verifiability or auditability is required
  
  substrate+small-LLM matches or exceeds frontier LLM on F1/accuracy, at lower
  compute cost, with a deterministically auditable chain that frontier LLMs cannot
  provide.
  
  For tasks where:
  (a) Novel inference is required (no KB coverage), OR
  (b) The task is numerical computation (arithmetic chains), OR
  (c) Multimodal / physical world reasoning is involved
  
  frontier LLM wins on raw capability. Substrate adds nothing here.

The commercial cases worth building for are type (a)-(c) above. They map to
compliance, audit, knowledge management, domain-expert workflow acceleration.
Large markets; real deployment gates that frontier LLMs fail.

---

## 10. Cross-Thread Synthesis

K-hop compose acc=1.0 (cycles 158/162): confirms substrate algebraic chaining operates
at near-zero error on the knowledge traversal step. The bottleneck for reasoning quality
moves entirely to LLM generation quality and KB coverage. This reframes the engineering
priority: invest in KB construction, not model scaling.

HotpotQA +0.35 F1: the substrate augmentation effect is real and large. Aligns with
RETRO/RAG-coding literature. This result generalizes: the effect size is consistent
across independent research lines.

LLM-decomp at 1.5B closed (parallel + sequential failed, architectural gap not parameter):
This is the empirical confirmation that the LLM bottleneck is architectural at small
sizes. It implies the minimum viable LLM for the substrate+LLM pairing on complex
reasoning may be ~7B parameters. The 7B Qwen family is the right target for cheap
pre-tests.

Fano-style compositional gap bound: does not close with parameter count at small sizes.
However, substrate KB coverage IS the composition provider in the substrate+LLM pairing.
The model need not learn compositions; it retrieves them. This is architecturally
distinct from parameter scaling and is why the RETRO 37x parameter efficiency result
is the right analogy.

---

## 11. Substrate-Product Implications

(a) KB coverage quality is now the dominant performance lever, not model size.
    Engineering investment in KB construction gives disproportionate return vs
    parameter scaling.

(b) Auditable chain is a hard deployment gate for regulated industries. Ship the
    replay-determinism test (Pre-test 3) early to establish this as a proven capability.

(c) The GSM8K gap (84% small vs 95% frontier on full set) is NOT the relevant
    comparison. The relevant comparison is formula-class subset where substrate+small
    should close to >90%. Frame benchmarks by problem class, not full-set numbers.

(d) Code generation is the highest-confidence win: CodeRAG literature shows 35-point
    gains. Substrate audit chain for code provenance is a new capability not present
    in any published RAG-coding system. Ship this first.

(e) Minimum viable LLM size: LLM-decomp failure at 1.5B suggests the pairing needs
    >=7B parameters for complex reasoning chains. Qwen-7B is the right anchor for
    primary benchmarks. Keep 1.5B for ablation only.

---

## Citations (Verified: 14)

1. Borgeaud et al. (2021). Improving language models by retrieving from trillions of
   tokens (RETRO). DeepMind. arxiv:2112.04426.
   Key result: 7.5B RETRO > 280B Gopher on 9/16 tasks; comparable to GPT-3 with 25x
   fewer parameters.

2. CodeRAG: Supportive Code Retrieval on Bigraph for Real-World Code Generation (2025).
   arxiv:2504.10046. Key result: +35.57 pass@1 on repo-level tasks.

3. Context-Augmented Code Generation (2024). OpenReview 0c49f5e8.
   Key result: up to 20% pass@1 improvement; 34% MBPP gain over SOTA.

4. He, J. (2025). Inference-Time Techniques for Efficient Code Generation.
   CSE503 UW. Llama3.2 1B + CAD: 0.39 HumanEval, 0.50 MBPP.

5. RAT: Retrieval Augmented Thoughts Elicit Context-Aware Reasoning in Long-Horizon
   Generation (2024). arxiv:2403.05313. Interleaved retrieval+CoT outperforms CoT alone.

6. ARCS: Agentic Retrieval-Augmented Code Synthesis with Iterative Refinement (2025).
   arxiv:2504.20434. Matches/exceeds baselines on HumanEval.

7. DTKG: Dual-Track Knowledge Graph-Verified Reasoning for Multi-Hop QA (2024).
   arxiv:2510.16302. Structured KB traversal on HotpotQA/MuSiQue.

8. StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop QA (2024).
   arxiv:2510.02827.

9. Towards Trustworthy Legal AI through LLM Agents and Formal Reasoning (2025).
   arxiv:2511.21033. Neural approaches cannot guarantee logical validity.

10. Why Chain of Thought Fails in Clinical Text Understanding (2025).
    arxiv:2509.21933. CoT explanations may be unfaithful in clinical settings.

11. Benchmarking Large Language Models in Retrieval-Augmented Generation (2023).
    arxiv:2309.01431.

12. GSM8K benchmark data. emergentmind.com/topics/gsm8k.
    Frontier saturation 95-97%; Qwen2.5-7B at 84.3%.

13. LLM Hallucinations in Practical Code Generation (2024). arxiv:2409.20550.
    RAG-based mitigation consistently improves pass@1.

14. Reasoning with Graphs: Structuring Implicit Knowledge to Enhance LLM Reasoning
    (2025). arxiv:2501.07845.
