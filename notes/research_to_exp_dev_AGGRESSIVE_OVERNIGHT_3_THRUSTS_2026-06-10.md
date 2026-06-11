# Research -> Exp-Dev: AGGRESSIVE OVERNIGHT BATCH -- 3 dominance thrusts (COMMUNICATE + MATH + CODE)

**From:** Research  **Date:** 2026-06-10 evening
**Re:** New strategic direction -- barriers to clear dominance; 3 thrusts overnight

## Mandate (per user)

"Genuinely aggressive new direction to fill out tests overnight. 3 main thrusts. Make sure substrate can COMMUNICATE as first focus. Plus do MATH and CODE."

This is strategic pivot: from validating primitives to PRODUCING USEFUL OUTPUT in the 3 most-asked-of-AI domains. All substrate-native (no LLM hybrid). Apply user principles (biology proves; materials math; invent new math).

## THRUST 1: COMMUNICATE (FIRST FOCUS)

Substrate's ability to convey meaning between systems. Substrate-only (no LLM).

### Anchors (laptop CPU)

| Anchor | Test | HARD-PASS |
|---|---|---|
| **COMM-1 PARAGRAPH-COMPOSE** | Substrate composes 100-token coherent paragraph on topic via Tier 1-4 pipeline (Levelt) | semantic_similarity >= 0.65 vs reference |
| **COMM-2 TRANSLATION-PAIRS-DIFFICULT** | English ↔ Mandarin / Arabic / Japanese (typologically distant) on 200 concepts | BLEU >= 0.40 on test set |
| **COMM-3 CONVERSATIONAL-RESPONSE** | Substrate generates context-appropriate response to query (substrate-only) | human_pref >= 0.50 vs random baseline |
| **COMM-4 QUESTION-ANSWERING** | Substrate answers structured questions from KB (extends PP-290 query compiler) | F1 >= 0.85 on factoid QA |
| **COMM-5 SUBSTRATE-TO-SUBSTRATE-PROTOCOL** | Two substrate instances exchange compressed information; recipient reconstructs | reconstruction >= 0.80 |
| **COMM-6 INTENT-DECODING** | Substrate decodes intent from user surface form (5 conversational axes; PP-232..236) | accuracy >= 0.85 |
| **COMM-7 ABSTRACTION-LEVEL-ADAPTATION** | Substrate generates same content at 3 abstraction levels (expert / lay / child) | coherence + appropriate |

### Mechanism (apply user principles)

- Biology: animals communicate via signals + structure; humans add compositional language
- Materials science: information theory (Shannon); signal-to-noise channel theory
- LLM theory: Levelt pipeline + Zipf-optimal codebook + Tier 1-2-3 hierarchical composition
- Substrate-native math: top-down hierarchical compose + cleanup + emission via PP-225-style projection (without LLM)

## THRUST 2: MATH

Substrate as symbolic + numerical mathematics engine. Substrate-only.

### Anchors

| Anchor | Test | HARD-PASS |
|---|---|---|
| **MATH-1 ALGEBRA-SIMPLIFY** | Substrate simplifies algebraic expressions via stored rules + composition | accuracy >= 0.75 on 100 problems |
| **MATH-2 EQUATION-SOLVE** | Substrate solves linear / quadratic / simple polynomial equations | accuracy >= 0.70 |
| **MATH-3 CALCULUS-DERIVATIVE** | Substrate computes derivatives via chain rule + composition | accuracy >= 0.80 |
| **MATH-4 PROOF-CHAINS** | Substrate composes elementary proof chains (modus ponens; substitution) | accuracy >= 0.65 on 50 theorems |
| **MATH-5 NUMERICAL-COMPUTATION** | Substrate orchestrates numpy/linalg (extends PP-240) at production scale | recall >= 0.95 on 100 tasks |
| **MATH-6 BAYES-INFERENCE** | Substrate executes Bayes net queries (extends PP-308) on real Bayesian networks (Asia / Sachs) | accuracy >= 0.85 |
| **MATH-7 CAUSAL-INTERVENTION** | Substrate applies do-calculus (extends PP-270/307) on real causal graphs | accuracy >= 0.75 |
| **MATH-8 BENCHMARK-MATH** | Substrate on MATH benchmark (high-school competition) | accuracy >= 0.20 (small LLM baseline) |

### Mechanism

- Biology: humans do math via composition of rules + working memory
- Materials science: algebraic rules ARE substrate's binding operations
- LLM theory: chain-of-thought for math
- Substrate-native: stored algebraic rules as schemas + compositional application + cleanup verification

## THRUST 3: CODE

Substrate as code generation + understanding engine. Substrate-only.

### Anchors

| Anchor | Test | HARD-PASS |
|---|---|---|
| **CODE-1 FUNCTION-GENERATION** | Substrate generates Python function from spec via program-shard composition (extends PP-311) | pass@1 >= 0.15 on HumanEval |
| **CODE-2 BUG-DETECTION** | Substrate identifies bugs in code via anomaly margin (PP-263 extended) | F1 >= 0.70 on 100 bugs |
| **CODE-3 REFACTORING** | Substrate refactors code via substitution of program shards | semantic equivalence >= 0.80 |
| **CODE-4 TEST-GENERATION** | Substrate generates unit tests from function spec | coverage >= 0.65 |
| **CODE-5 CODE-UNDERSTANDING** | Substrate explains code semantics (composition decomposition) | accuracy >= 0.75 on 100 functions |
| **CODE-6 ALGORITHM-COMPOSITION** | Substrate composes algorithms from primitives (sort + search + filter) | success rate >= 0.70 |
| **CODE-7 BENCHMARK-MBPP** | Substrate on MBPP (basic Python problems) | pass@1 >= 0.20 |
| **CODE-8 CODE-AS-DATA** | Substrate represents AST as composite shards; manipulation correctness | recall >= 0.90 |

### Mechanism

- Biology: humans plan code via decomposition + assembly
- Materials science: program structures map to substrate composition algebra
- LLM theory: HumanEval / MBPP benchmarks; Codex/Copilot
- Substrate-native: program shards (already validated PP-311) + compositional generation + execution orchestration (PP-241) + bug-as-anomaly (PP-263)

## RESOURCE ESTIMATE

| Thrust | Anchors | CPU-hr |
|---|---|---|
| COMMUNICATE | 7 | 15-25 |
| MATH | 8 | 20-30 |
| CODE | 8 | 25-40 |

**Total ~60-95 CPU-hr over 1-2 nights.** Laptop CPU + desktop CPU (after Stage A); maybe GPU for code execution sandboxing.

## SEQUENCING

### Tonight (Sprint 1; cheapest gates first)

| Order | Anchor | Cost | Decisive |
|---|---|---|---|
| 1 | COMM-1 PARAGRAPH-COMPOSE | 2hr | does substrate emit coherent text? |
| 2 | MATH-1 ALGEBRA-SIMPLIFY | 2hr | does substrate apply stored rules? |
| 3 | CODE-1 FUNCTION-GENERATION | 3hr | does substrate compose code? |
| 4 | COMM-6 INTENT-DECODING | 1hr | conversational primitive extension |
| 5 | MATH-3 CALCULUS-DERIVATIVE | 2hr | substrate chain rule |

Sprint 1 = ~10 hr CPU; tells us if 3 thrusts have substrate-native existence proofs.

### Tomorrow (Sprint 2; pass-to-benchmark)

After Sprint 1, promote passing anchors to standard benchmarks:
- HumanEval (CODE-1 → CODE-7)
- MATH benchmark (MATH-1 → MATH-8)
- BLEU / human eval (COMM-1 → COMM-2)

## STRATEGIC SIGNIFICANCE

**This converts substrate from "validated primitives" → "produces useful output in 3 high-demand AI domains."**

If even 2 of 3 thrusts show substrate-native PASS:
- Substrate has demonstrable autonomous output capabilities
- Categorical commercial pitch extends from infrastructure → producing
- Customer-facing use cases multiply

If all 3 FAIL:
- Substrate position narrows to infrastructure + LLM-hybrid for output
- Honest scope correction

**Either result is decisive for substrate's autonomous-output commercial claim.**

## Apply USER PRINCIPLES throughout

1. Biology proves possible (animals communicate; brains do math + planning)
2. Materials science has 100 years of relevant math (information theory + algebra + symbolic logic)
3. Don't be afraid to invent new math

## Cross-references
- Substrate-native revival routing (no LLM hybrid)
- 5X architectural innovation consolidated
- User principles biology + materials + new math
- Substrate static-robust dynamic-fragile (continual learning revision)
- PP-273 haiku constrained creative + PP-273-PP-290 conversational + PP-240 math orchestrator + PP-241 code orchestrator + PP-311 program shards

---

**Exp-Dev:** AGGRESSIVE overnight batch. 3 thrusts × 7-8 anchors each. Sprint 1 = 5 cheapest gates (~10 hr CPU). Sprint 2 = standard benchmark promotion.

This is the test of substrate's autonomous output capability. Production-grade results enable categorical autonomous-cognition commercial claim. Substrate-only.
