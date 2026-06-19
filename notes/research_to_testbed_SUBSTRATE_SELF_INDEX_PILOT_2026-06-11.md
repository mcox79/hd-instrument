# Research -> Testbed: Substrate-self-index pilot AUTHORIZED (~2-3 days)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** User-authorized substrate-self-index pilot with MATH-first + concept-linked design

## Pilot scope (user-locked design)

**Start with math (load-bearing layer); map math clusters -> concepts via bidirectional cross-corpus links. No math-in-a-vacuum.**

Level A taxonomic encoding (NOT Level B algebraic substrate-math; NOT Level C proof engine). Tight scope: 2-3 days laptop CPU.

## Two corpora, cross-linked

### Corpus A: MATH layer (~80-100 atoms)

**Tier-1 foundational (~15-20 atoms)**:
- vector spaces, inner products, complex/real fields
- probability distributions, entropy, KL divergence
- group/ring/field axioms
- optimization (convex / discrete / combinatorial)
- graph topology

**Tier-2 substrate primitives (~10-15 atoms)**:
- FHRR binding (element-wise complex multiplication)
- FHRR unbinding (conjugate multiplication)
- cleanup (nearest neighbor in cosine/Hamming)
- bundling (sum + normalize)
- Tier-2 schemas (count-weighted superposition)
- context-binding
- role-filler binding

**Tier-3 algorithms (~25-30 atoms)**:
- HMM Viterbi, count-NB, Hungarian assignment
- Chu-Liu-Edmonds MST, PCA whitening, ZCA
- phasor embeddings, Bayesian inference, MAP estimation
- beam search, dynamic programming, fast marching
- Dijkstra, A*, Jonker-Volgenant

**Tier-4 composed methods (~15-20 atoms)**:
- substrate POS tagger, substrate slot-filler, substrate intent classifier
- substrate schema-retrieval, substrate reasoning-routing
- substrate cross-domain analogy, FHRR Reed-Solomon parity

### Corpus B: CONCEPT layer (~60-80 atoms)

**PP rows (~30)**: PP-225, PP-217, PP-226-228, PP-364, PP-367-372, plus key reasoning primitives (PP-343/348/360)

**Drill outcomes (~20)**: drill-defeatism rule applications + 6 today's drills + 2x drills from cycle 232 negatives

**Capability assertions (~10)**: Tier A capabilities (7), Tier B candidates (slot-filling), substrate-classical NLP pattern, drill-defeatism rule

### CROSS-CORPUS LINKS (the load-bearing part)

Every math atom has reverse-link to concepts that USE it:
- FHRR binding -> [PP-225, PP-364, PP-369, PP-370, PP-371, PP-372]
- Count-NB -> [PP-364, PP-369, PP-370]
- HMM Viterbi -> [PP-364, PP-369]
- Hungarian assignment -> [] (gap; Phase 4 bipartite-matching candidate)
- Schema retrieval -> [PP-371, PP-372]

Every concept has forward-link to math operations it employs:
- PP-364 (POS tagger) -> [HMM emission, HMM transition, Viterbi, FHRR binding, count-NB]
- PP-370 (intent) -> [count-NB, train-bootstrap, FHRR binding, Tier-2 schemas]
- PP-371 (reasoning routing) -> [substrate-as-classifier, prototype-bundle cleanup, FHRR binding]

## Relation types (~8-10)

**Within math corpus:**
- COMPOSES (A then B = C)
- SPECIALIZES (A is specific case of B)
- DUAL (binding/unbinding pair)
- USES (A invokes B as subprocedure)
- PRESERVES (A maintains property P)
- OPTIMIZES (A solves optimization problem P globally/locally)
- APPROXIMATES (A approximates B with error bound E)
- EQUIVALENT_UNDER (A and B equivalent under transformation T)
- COST_FUNCTION_TYPE (additive / multiplicative / discrete / continuous)
- COMPLEXITY_CLASS (P / NP / polynomial / exponential)

**Within concept corpus:**
- ENABLES (A makes B possible)
- VALIDATES (A confirms B)
- REFUTES (A contradicts B)
- DEPENDS_ON (A requires B)

**Cross-corpus:**
- USES (concept -> math operation)
- HAS_USERS (math operation -> concepts) [reverse of USES; auto-derived]

## Build sequence

### Day 1: Testbed builds encoding schema + ingest infrastructure
- Tier-1/2/3/4 atom encoding pattern (per existing substrate Tier hierarchy)
- Relation encoding pattern (typed edges between atoms)
- Cross-corpus link encoding (USES + HAS_USERS bidirectional)
- Ingest tool (Python script accepting structured input -> substrate)
- Retrieval interface (substrate query -> ranked atoms + relations)

### Day 1-2: Research populates corpora
- Populate math corpus first (~80-100 atoms) with structural relations
- Populate concept corpus (~60-80 atoms)
- Hand-author cross-corpus USES links (Research subject expertise; ~150-200 links total)
- Validate encoding faithfulness (sanity-check substrate retrieves known-related items)

### Day 2: Testbed builds comparative-vs-LLM validation harness
- Same queries run against substrate AND against Claude/GPT on same corpora
- Comparative scoring: does substrate tie or beat LLM on cross-corpus structural queries?
- Critical: queries pre-registered Day 1, no cherry-picking post-hoc

### Day 2-3: Joint validation
- Run 10 test queries (5 math, 5 concept, with cross-corpus elements)
- Substrate vs LLM comparative scoring
- Honest writeup: where substrate beats LLM, where LLM beats substrate, where both miss

## Pre-registered test queries (5 of 10; rest sealed)

**Math queries:**
1. "Find math operations structurally similar to FHRR cleanup" -> expected: Hungarian assignment + HMM Viterbi + MST decode (all global discrete optimization)
2. "What math operations preserve the property of cardinality?" -> expected: substrate primitives that map vectors to vectors of same dimension
3. "What's the dual of FHRR binding?" -> expected: FHRR unbinding (trivial check; validates encoding)

**Cross-corpus queries:**
4. "What concepts share count-NB as a math foundation?" -> expected: PP-364, PP-369, PP-370 (substrate-classical NLP cluster confirmation)
5. "What math operations have NO concept users?" -> expected: Hungarian assignment + bipartite matching (gap detection; confirms Phase 4 priority)

5 sealed queries set Day 1 before pilot starts.

## Success criteria

| Outcome | Implication |
|---|---|
| Substrate ties or beats LLM on >=3/10 queries | Pilot SUCCESS; substrate-self-index has empirical value; consider Level B (algebraic substrate-math) as future direction |
| Substrate beats LLM on 1-2/10 + ties on others | Marginal value; consider scope refinement before scaling |
| Substrate underperforms LLM on >7/10 | Substrate-relational on messy NL corpus NOT yet at production grade; informs Phase 4B-FULL design priorities |

NO pre-registered architectural defeat threshold per drill-defeatism rule.

## Expected surfacings (honest predictions)

**LIKELY (high probability):**
- Substrate-classical NLP cluster confirmed via math-grounded retrieval (count-NB + HMM + Tier-2 schemas all link to PP-364/369/370)
- Hungarian assignment and HMM Viterbi cluster as "global discrete optimization"
- FHRR binding/unbinding DUAL relation validates trivially

**POSSIBLE (medium probability):**
- NON-OBVIOUS unification: Viterbi + Chu-Liu-Edmonds = "globally-optimal tree-structured DP" (suggests Phase 4B's MST tree-decode is same primitive as Viterbi extended)
- CAPABILITY GAP: continuous-relaxation primitive missing (Hungarian/MST/Viterbi are all discrete; no continuous-cost analog encoded)

**UNLIKELY but POSSIBLE (low probability, high value):**
- Structural unification across distinct families (FHRR cleanup + Hungarian + softmax as instances of unified projection problem)
- 1 new mathematical question

**UNLIKELY (don't bet on):**
- Genuinely new theorems

## What this is NOT

- NOT a replacement for human-readable docs (MEMORY.md, strategy_decisions, capability_inventory_tracking.md remain canonical)
- NOT auto-modification of substrate from its own self-index
- NOT Level B (algebraic substrate-math) or Level C (proof engine)
- NOT a multi-week build; this is a 2-3 day pilot

## Strategic placement

Pilot runs in parallel with Phase 4 revised sequence (v2.5 + bipartite-matching). NO blocking on Phase 4. Testbed laptop CPU; Research provides corpus.

If pilot lands well: Level B (algebraic substrate-math) becomes a real future direction; substrate-self-index becomes ongoing maintenance artifact alongside MEMORY.md.

If pilot lands poorly: we learn substrate-relational on messy corpus isn't strong enough yet; informs Phase 4B-FULL and all subsequent NL pipeline work.

## Cross-references
- User authorization: this turn
- Substrate self-improvement architecturally viable: memory substrate_self_improvement_architecturally_viable_2026-06-10
- Substrate-classical NLP pattern: memory substrate_classical_NLP_methods_outperform_phasor_2026-06-11
- Phase 4 revised sequence: notes/research_to_exp_dev_PHASE4_REVISED_SEQUENCE_BIPARTITE_FIRST_2026-06-11.md
- v2.5 confidence-gated rescue: notes/research_to_exp_dev_PHASE4_V25_CONFIDENCE_GATED_RESCUE_2026-06-11.md

---

**Testbed:** substrate-self-index pilot AUTHORIZED. 2-3 days. Encoding schema + ingest infra + retrieval interface + comparative-vs-LLM validation harness. Math layer first (~80-100 atoms) + concept layer (~60-80 atoms) + cross-corpus USES links (~150-200). 10 pre-registered test queries (5 disclosed, 5 sealed Day 1). Success = substrate ties or beats LLM on >=3/10 queries. Research populates corpora in parallel.
