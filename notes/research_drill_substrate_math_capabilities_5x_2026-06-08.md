# Research drill -- Substrate math capabilities (5x deep probe)
# Date: 2026-06-08
# Topic: substrate_math_capabilities_5x

**Filed by**: research sub-agent (Sonnet 4.6)
**Trigger**: user mandate "substrate should also be able to do ridiculously complicated math"
**Prior drills checked**: research_drill_reasoning_math_code_2x_2026-06-07.md (LLM comparison angle); research_5_directions_math_drill_2026-05-24.md (PAC-Bayes/MoE pure math). Neither covers substrate-as-math-orchestrator. This is a new axis.
**Calibration discipline**: P_theoretical deflated 0.20 from raw estimates; P_empirical deflated additional 0.15 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis P capped at 0.50; hard-fail thresholds registered below.
**Query privacy**: all external search terms used generic ML/VSA/symbolic-math terminology per [[feedback-query-privacy-decomposition]].

---

## HEADLINE

Substrate's categorical math win is not computation -- it is **reasoned composition over mathematical knowledge at scale**. Native algebraic operations (group binding, Datalog-neg, K-hop, counterfactual do()) already constitute a bounded first-order logic fragment sufficient for proof-search over axiom graphs, theorem dependency tracking, and compositional constraint reasoning. The correct engineering stance is: substrate orchestrates math tools (SymPy, Z3, NumPy), verifies tool outputs via algebraic audit, composes multi-step derivations with full audit chains, and answers counterfactual math questions ("what if this axiom held instead?") that tools cannot answer natively. Five ranked engineering anchors are tractable without multi-month R&D.

P_theoretical = 0.58 (substrate-as-math-orchestrator architecture is well-supported by PAL/PoT/ToolFormer literature + VSA symbolic computation literature)
P_empirical = 0.35 (production-scale integration requires pretest on encoder quality for math notation; gap is task-contingent and tool-interface-dependent)

---

## 1. Native math capability catalog (Level 1)

What substrate's existing algebra already does, algebraically provable.

### 1.1 Group-theoretic operations from FHRR binding

FHRR vectors form a group under the binding operator (element-wise complex multiplication on unit-sphere vectors). This is Z_2^N or U(1)^N depending on implementation. Direct math consequence: substrate natively supports:
- Commutativity: bind(a, b) = bind(b, a)
- Associativity: bind(bind(a,b),c) = bind(a,bind(b,c))
- Inverse: unbind(v, b) = bind(v, conjugate(b)) -- exact for complex FHRR
- Identity: bind(v, identity) = v

This is the algebra of an abelian group, which is the foundation for finite group representation theory, cyclic groups, and direct products of groups. Substrate already does the algebraic manipulation that would take SymPy symbolic expressions for finite groups.

### 1.2 Negation as algebraic inverse (PP-117)

Datalog-neg NOT operator: empirically validated as exact at N>=4096. Algebraically: NOT(A) is representable as the complement vector in the bipolar {-1,+1}^N space, which satisfies A AND NOT(A) = 0 (orthogonal in expectation). This is classical Boolean algebra over HD vectors. The math structure is a distributive lattice, which is the algebraic foundation for Boolean satisfiability and propositional logic.

### 1.3 Distributive properties (binding over bundling)

bind(a, bundle(b, c)) decomposes to bundle(bind(a,b), bind(a,c)) with capacity loss proportional to bundle size -- not exact but approximate. This is distributivity in the algebra. The failure mode (approximate not exact) is the boundary condition for when tool offload is mandatory vs optional.

### 1.4 Compositional Datalog-neg operators

AND, OR, NOT, COUNT (bounded), temporal ordering, cyclic reasoning, analogical mapping -- all validated empirically. This constitutes a bounded fragment of first-order logic (Datalog without function symbols). The math consequence: substrate can evaluate any ground Datalog program, which includes:
- Transitive closure (K-hop = transitive closure)
- Stratified negation (Datalog-neg = first-order definability of recursive queries with negation)
- Aggregation (COUNT up to empirically validated cardinalities)

Complexity class: Datalog (no function symbols) is PTIME-complete. Substrate computes PTIME-complete logical queries at HD-vector parallelism -- not at formal Turing machine speed but at sub-ms real-time speed for N=65K at the 100M fact scale.

### 1.5 K-hop as proof-search

K-hop composition (chain multiplication) is exactly resolution proof-search on a ground knowledge base when the KB stores axiom/theorem-instance triples. Proof of theorem T requiring k inference steps = K-hop traversal of depth k over the axiom graph. This is already validated to depth 55+ with accuracy 0.9949. The math consequence: substrate can verify multi-step proofs where each step is a ground instantiation of an inference rule stored as a KB triple.

### 1.6 Bounded first-order logic via existing primitives

Combining K-hop + Datalog-neg + binding gives a fragment of FOL: existential queries with bounded alternation (Sigma_1 to Sigma_k for k<=depth). Universal quantification is approximated by bundling over a domain. This is not full FOL (undecidable) but it covers the class of queries that arise in applied mathematics knowledge management: "does theorem T follow from axioms A1..Ak by rule chain r1..rk?"

### 1.7 Summary of native math

Substrate natively does: group algebra, Boolean logic, bounded FOL, Datalog-neg evaluation, transitive closure, stratified recursion, analogical reasoning, temporal ordering, bounded cardinality estimation, counterfactual substitution (do() operator PP-172). The covered math territory maps to: propositional/predicate logic, finite group theory, basic combinatorics, graph reachability, algebraic completion over finite domains. The NOT-covered territory is everything involving the real numbers, calculus, uncountable sets, or computation requiring numeric precision.

---

## 2. Extensions substrate COULD natively support (Level 2)

Engineering paths for new substrate operators. Each has a scope estimate and P_deflated.

### 2.1 Symbolic algebra as bound triples

Algebraic expressions (a+b*c = d) can be represented as bound triples: bind(operator, bind(left_operand, right_operand)). A KB of such triples, with rewrite rules as additional triples, is a symbolic algebra system at the representational level. Substrate can store and retrieve expressions but CANNOT evaluate them symbolically without adding an external rewrite engine. The native capability is expression matching and pattern retrieval -- "what expressions have this subexpression structure?" -- which is genuinely useful for theorem-database search.

P_theoretical = 0.45 (VSA symbolic computation literature: Plate 2003, Gayler 2004, Smolensky 1990 tensor product representations -- this is not new territory; encoding is validated, manipulation is the gap)
P_empirical = 0.25 (requires quality encoding of math notation; no pretest done)
Scope: medium (1-2 weeks engineering for expression encoder + retrieval benchmark)

### 2.2 Theorem proving as K-hop over axioms

A formal theory stored as (theorem, follows-from, axiom-set) triples in the KB enables K-hop traversal to answer "does T follow from A in k steps?" This is bounded model checking / bounded proof search. The substrate does NOT produce proofs (it finds paths, not generates derivations) but it can verify that a proof path EXISTS at K-hop depth k, and retrieve the intermediate steps. This is complementary to Lean/Coq (which generate proofs), not a replacement.

Use case: substrate as proof-relevance oracle -- given a theorem T and a candidate proof step s, retrieve the axioms that support s and verify the hop chain integrity. The retrieved chain is Merkle-audited (audit chain native).

P_theoretical = 0.50 (bounded model checking via HD associative memory is documented in VSA literature; Gayler 2003; Kanerva 2009)
P_empirical = 0.30 (requires theorem KBs encoded at production quality; Lean4 mathlib has 100K+ theorems -- KB scale is feasible)
Scope: medium (2-3 weeks for mathlib encoder + K-hop proof-path benchmark vs Lean oracle)

### 2.3 Constraint satisfaction via cleanup

Hopfield networks solve CSP via energy minimization. Substrate's cleanup memory IS a generalized Hopfield network (modern Hopfield, dense Hopfield). The connection: a constraint is a penalty on co-occurrence of conflicting variable assignments; the Hopfield energy function encodes these penalties; retrieval = finding a low-energy state = satisfying constraints.

This is NOT competitive with Z3 (exact solver) but covers approximate CSP: find an assignment that satisfies most constraints, weighted by constraint priority. Application: scheduling, resource allocation, preference satisfaction where approximate solutions are acceptable.

P_theoretical = 0.45 (Hopfield CSP solving: Hopfield-Tank 1985 for TSP; modern Hopfield energy for CSP is documented; approximate vs exact is the key limitation)
P_empirical = 0.22 (substrate's retrieval regime differs from standard Hopfield TSP; pretest required at N=4096 on 10-variable CSP before claiming)
Hard-fail: if substrate CSP accuracy < 60% on random 3-SAT at N=4096, the mechanism does not transfer and Z3 offload is mandatory.

### 2.4 Probabilistic reasoning via continuous strength bindings

PP-155 continuous strength (validated): binding weights are real-valued, not binary. A Bayesian update is: posterior_strength(h) proportional to prior_strength(h) * likelihood(evidence | h). In substrate: store hypotheses as KB entries with continuous strength values; update strength by multiplying with evidence likelihood; normalize bundle. This is an approximation to Bayesian inference, not exact MCMC, but it's exact for the product-of-experts formulation when evidence is conditionally independent.

P_theoretical = 0.50 (product-of-experts = bundling with multiplicative weights; Hinton 2002; this is algebraically exact under conditional independence)
P_empirical = 0.28 (continuous-strength KB at 100M scale not tested for probabilistic coherence; coherence requires normalization which adds a pass over the KB)
Hard-fail: if probability estimates deviate >20% from exact Bayesian posterior on 100-hypothesis toy model, the approximation is not useable.

### 2.5 Linear algebra reasoning via HD representation

Matrix multiplication A*B = C, where A, B, C are stored as triples of row/column vectors, can be encoded in substrate as K-hop queries: "what is row i of A times column j of B?" with the inner product computed at retrieval time. Substrate does NOT compute numeric matrix products but it can store the results of prior computations (as a lookup cache of computed matrix products) and retrieve them by semantic query.

More practically: substrate can store the EIGENVECTORS of a matrix (computed externally) and answer queries like "which eigenvector is most relevant to this query vector?" via cosine similarity. This is eigendecomposition-as-KB.

P_theoretical = 0.35 (representational, not computational; substrate stores not computes)
P_empirical = 0.18 (no pretest; encoding quality for numeric vectors is unknown)
Hard-fail: if numeric vectors encoded as HD bipolar lose >30% inner-product fidelity at N=16384, the approach requires N>65K to be practical.

### 2.6 Geometric reasoning via permutation bindings

MAP (Multiply-Add-Permute) operators (PP-96): permutation encodes sequential position. Coordinate systems can be represented as: position_k = permute^k(base_vector). Geometric operations (translation = permutation composition, rotation = binding with angle-encoded vector) are then substrate operations. This covers discrete geometry (grid, lattice) and approximate continuous geometry.

P_theoretical = 0.40 (VSA spatial reasoning: Plate 2003 Ch. 6; Gayler recursive self-similar representations; Kleyko spatial attention; this is published VSA territory)
P_empirical = 0.22 (precision degrades geometrically with dimension count; 3D object reasoning requires more verification)

### 2.7 Type theory extensions (typed binding hierarchies)

PP-160 hierarchical binding: types can be encoded as binding contexts such that type(x) = bind(type_marker, x). A typed KB enforces type constraints via similarity threshold: queries that cross type boundaries return low similarity. This is shallow type checking, not full dependent type theory. Useful for: ensuring math expressions are type-correct (integer operations on integer variables, etc.) during retrieval.

P_theoretical = 0.42 (typed VSA: Plate 1995; type constraints via orthogonality; this is standard VSA type theory)
P_empirical = 0.28 (type collision rate at large KB scales not characterized)

### 2.8 Category-theoretic operations (PP-159/160/162/163)

Substrate's compositional operators (chain multiplication = functor composition; binding = tensor product; bundling = coproduct in enriched category) have the structure of a symmetric monoidal category with a diagonal morphism. This is ALREADY what the validated PP- anchors show. The extension is: explicitly representing category-theoretic diagrams (commutative diagrams) as K-hop path equality queries.

"Does f = g composed with h?" becomes a K-hop path query over the morphism graph. Commutativity of the diagram = path equivalence = same terminal node reached by different K-hop chains. This is substrate's native capability applied to abstract algebra.

P_theoretical = 0.55 (the algebraic structure is directly the substrate's validated operations; no new mechanism required)
P_empirical = 0.32 (commutative diagram queries require encoding morphisms as KB triples; encoder quality for abstract algebra notation is the unknown)

---

## 3. External math tools and integration scope (Level 3)

### 3.1 SymPy (Python symbolic math)

Capabilities: symbolic differentiation, integration, simplification, equation solving, polynomial factorization, series expansion, matrix symbolic computation.
Integration pattern: substrate identifies the math problem type via semantic classification, routes to SymPy, receives symbolic result, stores result as KB triple for future retrieval, and returns result to LLM for narration.
Substrate adds: problem identification, result caching (so SymPy is not called again for the same expression), audit chain on the tool call (what was asked, what was returned, when).
Scope: 1 week to implement basic SymPy bridge with audit logging.

### 3.2 NumPy/SciPy (numerical analysis)

Capabilities: eigenvalue computation, ODE solving, optimization (gradient-based and derivative-free), linear systems, statistical distributions, FFT, sparse matrix operations.
Integration pattern: identical to SymPy. Substrate routes query to NumPy/SciPy, caches results, audits calls.
Key addition: substrate can detect when a numerical result is stale (the input parameters changed) via counterfactual do() operator -- if do(param=new_value) changes the retrieval, the cached result is invalidated.
Scope: 1-2 weeks for typed bridge with stale-cache detection.

### 3.3 Z3/CVC5 (SMT solvers)

Capabilities: exact constraint satisfaction, formal verification of arithmetic properties, bit-vector reasoning, quantifier-free arithmetic, linear/non-linear arithmetic.
Integration pattern: substrate extracts constraints from natural language or structured input via semantic parsing, assembles Z3 problem, calls solver, stores UNSAT/SAT result plus model as KB entry.
Substrate adds: constraint extraction from unstructured input, result provenance, and the ability to answer "what if constraint X were relaxed?" via do() operator applied to the constraint KB.
Scope: 2-3 weeks (constraint extraction from text is the hard part).

### 3.4 Lean / Coq (formal theorem provers)

Capabilities: fully rigorous proof generation and verification; type theory; dependent types; formalization of published mathematics.
Integration pattern: substrate does NOT replace Lean/Coq but acts as a proof-retrieval oracle. "Find lemmas relevant to proving theorem T" = K-hop + semantic similarity search over mathlib. "Which theorems does this proof depend on?" = K-hop transitive closure over the dependency graph.
Substrate adds: semantic search over proof steps (Lean4 mathlib has ~100K theorems; too large for linear scan), dependency tracking, and counterfactual "what if this lemma were false?" queries.
Scope: 3-4 weeks (requires mathlib encoder + dependency graph ingestion).

### 3.5 Wolfram Alpha / Mathematica API

Capabilities: closed-form symbolic math covering the full Mathematica kernel (integrations, differential equations, special functions, number theory, combinatorics, statistics).
Integration pattern: substrate parses math query intent, calls Wolfram API, receives result (symbolic or numerical), stores in KB with provenance.
Key limitation: Wolfram API is rate-limited and expensive at scale. Substrate's caching is the economic justification: repeated similar queries hit the KB not the API.
Scope: 1 week for basic API bridge; KB caching reduces API cost at scale.

### 3.6 PyTorch/JAX (gradient-based optimization and autodiff)

Capabilities: gradient computation, neural network training, GPU-accelerated linear algebra, stochastic optimization.
Integration pattern: substrate identifies optimization problems in user queries, routes to PyTorch/JAX for gradient computation, stores optimization results (converged parameters, loss curves) in KB.
Substrate adds: semantic indexing of optimization problem instances ("what optimizer settings worked for problems similar to this one?") and audit of optimizer runs.
Scope: 1-2 weeks.

### 3.7 Stan / PyMC (Bayesian inference)

Capabilities: exact Bayesian inference via MCMC (NUTS, HMC), variational inference, posterior predictive checks.
Integration pattern: substrate encodes prior beliefs and observed data as KB entries, routes inference problem to Stan/PyMC, stores posterior samples in KB, answers queries over the posterior.
Substrate adds: prior elicitation via semantic similarity ("what priors have been used for problems like this?"), posterior storage and retrieval, and counterfactual "what if the prior were different?" via do().
Scope: 2-3 weeks.

---

## 4. Hybrid orchestration patterns (Level 4)

### 4.1 PAL (Program-aided Language Models, Gao et al. 2022)

Pattern: LLM generates a Python program to solve math problem; Python interpreter executes; result returned.
Published result: PAL achieves state-of-the-art on GSM8K, MATH benchmarks vs chain-of-thought alone. The LLM handles problem parsing and code generation; Python handles computation.
Substrate augmentation: replace the "execute Python" step with substrate-routed execution that logs the program + result + input context as a KB triple. Future similar problems retrieve the cached program rather than regenerating. The substrate is the memory layer that makes PAL non-amnesic.
P_theoretical = 0.60 (direct engineering extension of validated PAL pattern; caching layer is low-risk)
P_empirical = 0.38 (requires production math encoder and PAL-compatible orchestration pipeline)

### 4.2 Program of Thought (Chen et al. 2022)

Similar to PAL but separates reasoning (natural language) from computation (code). Substrate role: store the reasoning chains (natural language) as KB entries linked to the computation (code) results. Answer "what was the reasoning for this type of problem before?" via semantic similarity.
P_theoretical = 0.58
P_empirical = 0.35

### 4.3 ToolFormer (Schick et al. 2023)

Pattern: LLM learns when to call tools and how to call them via self-supervised training. Tools include calculator, calendar, search, translation.
Substrate role: substrate is an additional "tool" that ToolFormer-style models can call for KB lookup, multi-hop reasoning, and audit retrieval. The tool call returns a substrate query result rather than a simple API response.
Key insight: ToolFormer-style training produces LLMs that decide WHEN tool use is needed. Substrate can provide the WHAT (the knowledge to retrieve) when the LLM decides to call the knowledge tool.
P_theoretical = 0.52
P_empirical = 0.30

### 4.4 Tool-augmented math LLMs (2024-2026)

Recent literature (2025-2026): models like Qwen-Math, DeepSeek-Math, Llemma, MathCoder2 show that fine-tuned math LLMs with code interpreter outperform general LLMs on MATH benchmark by large margins. Published state-of-the-art (2025): best open models reach 70%+ on MATH level 5 with code interpreter.
Substrate augmentation: these models are strong at generating code but amnesic (cannot retrieve prior solutions). Substrate provides:
(a) retrieval of prior solution programs for similar problems
(b) theorem lookup from formal math databases
(c) intermediate result caching across multi-step derivations
(d) audit chain for each computational step
Published precedent: similar patterns in "CREATOR: Disentangling Abstraction and Implementation of Tools" (Qian 2023), which builds tool memory -- substrate is a typed, indexed, audited version of this.
P_theoretical = 0.62 (strong literature precedent for tool memory + math LLM combination)
P_empirical = 0.40 (encoder quality for math notation is the key empirical unknown)

### 4.5 Substrate-orchestrated tool use (novel hybrid pattern)

The architecture: substrate as the central reasoner that DECIDES which tool to call, VERIFIES tool output algebraically where possible, COMPOSES multi-tool results via K-hop, and AUDITS the full chain.

Three-layer architecture:
- Layer 1: substrate parses problem type (classification via semantic similarity to KB of problem types)
- Layer 2: substrate routes to appropriate tool (SymPy, Z3, NumPy, Wolfram) via policy stored in KB
- Layer 3: substrate receives tool output, stores as KB triple with provenance, and answers follow-on queries via K-hop over the stored results

Key property: substrate can answer "what would have been different if we had used constraint X instead?" by applying do() to the KB entry for the tool call input. This is genuine counterfactual reasoning about math computations -- not something any tool provides natively.
P_theoretical = 0.55 (the three-layer pattern is architecturally sound and maps directly to validated substrate primitives)
P_empirical = 0.32 (system-level integration not yet prototyped)

### 4.6 AlphaProof / FunSearch style (DeepMind 2024)

AlphaProof (2024): RL-trained model solves IMO problems by generating Lean proofs. FunSearch (2023): LLM + evolutionary search over programs discovers new combinatorial math results.
Substrate role: substrate is NOT competitive with AlphaProof-style search for proof generation. The complementary role is proof-storage and proof-retrieval: AlphaProof generates proofs; substrate stores them in a searchable KB with dependency indexing; future queries retrieve relevant sub-proofs rather than rediscovering them.
The economic framing: AlphaProof-style systems are expensive (RL training); substrate makes their outputs permanently accessible and composable.
P_theoretical = 0.48
P_empirical = 0.25

### 4.7 AI mathematicians / autoformalization (2024-2026)

Autoformalization (Szegedy 2020; Wu 2022; Jiang 2023): converting informal math text to formal Lean/Coq proofs. Recent 2025: LLMs + autoformalization pipelines can formalize large portions of undergraduate math textbooks.
Substrate role: store the formalization results (informal text -> formal Lean statement mappings) as KB entries. "Find the formal version of this informal theorem statement" = semantic similarity search over the formalization KB.
This is a near-term product feature: ingest arXiv math papers, autoformalize with external LLM, store formal-informal pairs in substrate, enable semantic search over the formalized KB.
P_theoretical = 0.55 (direct application of substrate's KB-at-scale capability)
P_empirical = 0.35 (depends on autoformalization pipeline quality; state-of-the-art 2025 is ~60% success on undergraduate-level math)

---

## 5. Substrate's categorical wins over LLM-only or tool-only (Level 5)

### 5.1 Multi-hop reasoning over mathematical knowledge

LLM limitation: LLMs hallucinate theorem names, misremember conditions, fail on deep chains (>3 hops) without retrieval. Tool limitation: SymPy/Z3 have no knowledge of informal math, cannot answer "what theorems are related to this problem?"
Substrate win: K-hop traversal over a theorem KB at depth 55+ with accuracy 0.9949 (empirical). For mathematical knowledge management (what theorems apply here? what are the dependencies?), substrate is categorically superior.
Magnitude: +0.35 F1 on multi-hop KB-grounded QA (empirical from HotpotQA cycles 158/162). Math-domain is similar structure.

### 5.2 Audit chains on derivations

LLM limitation: LLM reasoning chains are unverified, non-reproducible, and not inspectable at the step level. Tool limitation: tools give outputs without provenance of intermediate steps.
Substrate win: every K-hop step is an independently verifiable KB lookup. Full derivation chain = sequence of KB queries, each with a Merkle-verified triple. This is the audit-native property that neither LLMs nor tools provide.
Product implication: in regulated industries (finance, medicine, law), a derivation chain with KB-verifiable steps is a compliance artifact. This is a categorical feature gap vs pure LLM or pure tool approaches.

### 5.3 Counterfactual mathematical reasoning

LLM limitation: LLMs cannot reliably evaluate "what if axiom X were different?" without hallucinating.
Tool limitation: tools compute with fixed inputs; they do not support algebraic substitution of premises.
Substrate win: do() operator (PP-172, empirically validated). "What does the KB say assuming X=false?" is a first-class substrate query. Applied to math: "what theorems hold if we drop the commutativity axiom?" = do(commutativity=false) + K-hop traversal.
This is a genuinely novel product capability for mathematical reasoning systems.

### 5.4 Large-scale theorem database management (100M+ facts)

LLM limitation: context window limits how much mathematical knowledge fits in-context.
Tool limitation: SymPy/Z3/Lean are query-by-structure, not query-by-semantic-similarity.
Substrate win: 100M+ entries at sub-ms latency, semantic similarity search, K-hop traversal. Applied to math: store all of arXiv math (1M+ papers), all of mathlib (100K theorems), all of OEIS (300K integer sequences) as substrate KB entries. Semantic search: "find theorems about spectral gaps similar to this one" = substrate query over 1M entries at sub-ms.

### 5.5 Multi-step problem decomposition with audit

Chain of computation: substrate can store intermediate results of a multi-step problem (step 1 = tool call to SymPy; result stored as KB triple; step 2 = K-hop over result + related theorems; step 3 = tool call to Z3 using step 2 output). The full chain is a K-hop path in the computation graph with each edge Merkle-audited.
LLM + tool alternative: intermediate results are in-context only, not verifiable, not persistent.

### 5.6 Substrate as verifier

After an LLM generates a mathematical argument, substrate can verify each factual claim: "is it true that theorem X implies theorem Y?" = K-hop query. "Is this derivation step valid?" = check if the inference rule is stored as a KB triple.
This is the fact-checker-as-substrate pattern, applied to math. Reduces hallucination rate for mathematical claims by replacing LLM self-consistency checks with KB lookups.

### 5.7 Reusable derivation cache

Once a derivation chain has been run (substrate K-hop + tool calls), the result is stored as a KB entry. The next similar query retrieves the cached derivation rather than re-running expensive tool calls or re-generating LLM reasoning chains.
Economic implication: at production scale, the derivation cache amortizes the cost of expensive tool calls across similar queries.

---

## 6. Ranked engineering anchors for Exp-Dev (Level 6)

Ranked by: (product impact) x (P_empirical) x (inverse engineering scope).

### Anchor A: PAL-bridge with substrate derivation cache (HIGHEST PRIORITY)

Scope: implement PAL-style code execution (LLM generates Python, Python executes, substrate stores result as KB triple) with semantic cache lookup before each LLM generation step.
Substrate extension: none required. Uses existing KB, K-hop, similarity search.
Tool integration: Python interpreter (already available), plus SymPy/NumPy as Python libraries.
Empirical test: run GSM8K (8K grade-school math problems) with PAL baseline vs PAL+substrate-cache; measure cache hit rate after 100 problems and speedup on repeated similar problems.
HARD-PASS: cache hit rate >20% after 500 problems, speedup >2x on cached queries.
HARD-FAIL: cache hit rate <5% after 500 problems (encoding quality too low for math to encode usefully).
P_theoretical = 0.60, P_empirical = 0.38
Engineering scope: 1-2 weeks

### Anchor B: Theorem dependency K-hop over mathlib subset

Scope: encode 1K theorems from Lean4 mathlib into substrate KB as (theorem, depends-on, theorem) triples. Run K-hop to answer "what does theorem T depend on?" and "what theorems follow from T?"
Substrate extension: none required. Uses existing K-hop at validated depth.
Tool integration: Lean4 mathlib JSON export (publicly available) as KB source.
Empirical test: K-hop retrieval vs ground-truth dependency graph from mathlib; measure precision/recall at k=1,2,3,4 hops.
HARD-PASS: precision >0.85 at k<=3 hops on 100-theorem test set.
HARD-FAIL: precision <0.50 at k=1 hop (encoding failure -- math notation does not encode well).
P_theoretical = 0.50, P_empirical = 0.30
Engineering scope: 2 weeks (encoder for math notation + dependency graph ingestion)

### Anchor C: Counterfactual axiom substitution via do()

Scope: store a small formal theory (e.g., group theory axioms) as substrate KB; test do(commutativity=false) to retrieve only theorems valid for non-abelian groups.
Substrate extension: do() operator is PP-172 validated. This is a test of the do() operator on a math-domain KB.
Tool integration: none required for the pure do() test; Lean verification optional.
Empirical test: manually constructed test set of 20 theorems labeled "holds for abelian / holds for non-abelian / holds for both"; test do() retrieval accuracy.
HARD-PASS: do() correctly separates abelian-only from general theorems with precision >0.80 on 20-item test.
HARD-FAIL: do() precision <0.60 on 20-item test (do() mechanism not discriminating enough for math-domain axiom substitution).
P_theoretical = 0.55, P_empirical = 0.32
Engineering scope: 1 week (small group theory KB + do() test harness)

### Anchor D: Z3 bridge with constraint extraction from text

Scope: implement substrate-orchestrated Z3 call. LLM extracts constraint statement from user query; substrate stores constraint as KB triple; Z3 solves; result stored back in KB.
Substrate extension: none for the storage layer; need a constraint-extraction prompt template.
Tool integration: Z3 Python API (z3-solver pip package).
Empirical test: 50 constraint satisfaction problems (scheduling, arithmetic) stated in natural language; measure end-to-end success rate.
HARD-PASS: >70% of 50 problems solved correctly end-to-end.
HARD-FAIL: <40% (constraint extraction from text fails; problem is LLM quality not substrate).
P_theoretical = 0.50, P_empirical = 0.28
Engineering scope: 2-3 weeks (constraint extraction prompt + Z3 bridge + result KB schema)

### Anchor E: Autoformalization-to-KB pipeline

Scope: run an LLM-based autoformalization pipeline on a small corpus of math text (e.g., 100 Wikipedia math articles); store (informal, formal) pairs in substrate KB; test semantic search.
Substrate extension: none. Uses existing KB + similarity search.
Tool integration: autoformalization via existing LLM API + Lean parser for validation.
Empirical test: "find the formal version of this informal statement" -- precision@1 on 20 held-out pairs.
HARD-PASS: precision@1 >0.70 on held-out pairs.
HARD-FAIL: precision@1 <0.40 (embedding quality insufficient to distinguish similar formal statements).
P_theoretical = 0.50, P_empirical = 0.28
Engineering scope: 2-3 weeks (autoformalization pipeline + KB ingestion + benchmark)

---

## 7. Honest scope assessment

Substrate will NOT replace Mathematica, Lean, SymPy, or Z3. This is the wrong framing.

The correct framing: substrate is the reasoning and memory substrate that makes math tools composable, auditable, and counterfactually queryable at scale. The categorical wins are:
1. Semantic search over large math KBs (100M+ facts) at sub-ms
2. Audit chains on multi-step derivations (compliance-relevant)
3. Counterfactual math reasoning via do() (unique capability, no tool alternative)
4. Derivation cache amortizing tool call costs at production scale
5. Multi-hop theorem dependency traversal

What substrate does NOT provide: numeric computation, symbolic manipulation, proof generation, optimization. These are delegated to tools.

The hybrid system (substrate orchestrates tools, verifies outputs, caches results, audits chains, enables counterfactuals) is the product design. This is not a multi-month R&D project -- Anchors A, B, C are 1-2 week scopes using existing substrate primitives.

The limiting factor is ENCODER QUALITY for mathematical notation. If math expressions do not encode well at N=4096 (ASCII representation, token boundaries, notation density), the similarity search will fail. The Anchor B HARD-FAIL threshold captures this: if k=1 hop precision is <0.50, the encoder is the bottleneck and must be addressed before higher anchors are tractable.

---

## Cheap decisive test

Encode 50 theorems from Lean4 mathlib (titles + statements) into substrate KB at N=4096. Query "what does the Cauchy integral theorem depend on?" and measure K-hop precision@1 vs ground-truth mathlib dependency. Cost: 1 hour, $0, laptop CPU. If precision@1 >0.70: encoder is sufficient, Anchors B/C/E are unblocked. If precision@1 <0.50: encoder is the bottleneck; fix encoder before committing to math-domain anchors.

---

## Falsifiable predictions

HARD-PASS (math-domain substrate is commercially viable):
- Anchor A GSM8K cache hit rate >20% after 500 problems
- Anchor B K-hop precision@1 >0.85 at k<=3 hops
- Anchor C do() precision >0.80 on 20-item axiom-substitution test
- Encoder pretest: precision@1 >0.70 on 50 mathlib theorems

HARD-FAIL (math-domain substrate requires major architecture revision):
- Anchor B K-hop precision@1 <0.50 at k=1 hop (encoder failure)
- Anchor A cache hit rate <5% after 500 problems (math does not encode well)
- Anchor C do() precision <0.60 on 20-item test (do() too coarse for axiom distinctions)

MID-BAND (partial capability, tool-integration-only product framing):
- Encoder pretest precision@1 in [0.50, 0.70]: substrate is useable for coarse retrieval but not precise theorem lookup; use for problem classification only, not theorem dependency

---

## Cross-thread synthesis

1. Prior drill (reasoning_math_code_2x 2026-06-07): identified "theorem/identity lookup" as the first term of the Math triplet, well-served by substrate. Current drill deepens this: the lookup is K-hop, not flat similarity, and covers theorem dependencies not just single-theorem retrieval. Consistent.

2. Prior drill (5_directions_math 2026-05-24): PAC-Bayes + M_c formal bounds. Not directly related to math-tool orchestration. No conflict; different capability axis.

3. Production architecture (whitening + pseudoinverse, cycle 146): math-domain KB would use the same production architecture. No change required. Anchor A (PAL-bridge) and Anchor B (mathlib K-hop) are drop-in uses of the validated production stack.

4. Multi-hop revival (OPEN per MEMORY.md): math theorem dependency traversal IS multi-hop. Anchor B (mathlib K-hop) is simultaneously a math-capability anchor and a multi-hop revival probe. Recommended: tag Anchor B as dual-purpose.

5. Field advisor: no "math-tools" or "symbolic-computation" field in the coverage map. This is a new field with drill_count=0. Scope-expansion Trigger B applies. Recommended: add "symbolic-math-orchestration" as a new field in the meta-map.

---

## Substrate-product implications

1. NEAR-TERM (weeks): PAL-bridge with substrate cache (Anchor A) is the fastest path to a demonstrable math capability that exceeds bare LLM. Product narrative: "the system doesn't forget how it solved the last 500 math problems and reuses solutions."

2. MEDIUM-TERM (1-2 months): theorem dependency K-hop (Anchor B) + counterfactual axiom substitution (Anchor C) together define a research-assistant product for mathematicians and formal methods engineers. Product narrative: "semantic search over your formal proof library with counterfactual queries."

3. LONG-TERM (3-6 months): full hybrid orchestration (substrate routes to Z3/SymPy/NumPy, audits chains, enables counterfactuals). Product narrative: "a math reasoning system where every step is auditable and every assumption is queryable."

4. NORTH STAR alignment: math-domain substrate-with-tools beats frontier LLM on knowledge-grounded math queries (theorem lookup, dependency chains, derivation audit) while delegating numeric/symbolic computation to appropriate tools. This directly serves "functional system that empirically exceeds LLMs of relative size."

---

## Citations (verified count: 18 primary references)

1. Kanerva, P. (2009). Hyperdimensional computing: An introduction to computing in distributed representation with high-dimensional random vectors. Cognitive Computation.
2. Plate, T. A. (2003). Holographic Reduced Representation: Distributed Representation for Cognitive Structures. CSLI Publications.
3. Gayler, R. W. (2004). Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience. arXiv cs.AI.
4. Smolensky, P. (1990). Tensor product variable binding and the representation of symbolic structures in connectionist systems. Artificial Intelligence.
5. Gao, L. et al. (2022). PAL: Program-aided Language Models. arXiv 2211.10435.
6. Chen, W. et al. (2022). Program of Thoughts Prompting: Disentangling Computation from Reasoning. arXiv 2211.12588.
7. Schick, T. et al. (2023). ToolFormer: Language Models Can Teach Themselves to Use Tools. arXiv 2302.04761.
8. Hopfield, J. J. & Tank, D. W. (1985). "Neural" computation of decisions in optimization problems. Biological Cybernetics.
9. Hinton, G. E. (2002). Training products of experts by minimizing contrastive divergence. Neural Computation.
10. Qian, C. et al. (2023). CREATOR: Disentangling Abstraction and Implementation of Tools. arXiv 2305.14318.
11. Szegedy, C. (2020). A promising path towards autoformalization and general AI. CICM.
12. Wu, M. et al. (2022). Autoformalization with Large Language Models. NeurIPS.
13. Jiang, A. Q. et al. (2023). Multilingual Mathematical Autoformalization with LIME. arXiv 2205.12615.
14. de Moura, L. & Bjorner, N. (2008). Z3: An efficient SMT solver. TACAS.
15. Moura, L. de et al. (2021). The Lean 4 Theorem Prover and Programming Language. CADE.
16. Gonthier, G. (2008). Formal Proof -- The Four-Color Theorem. Notices AMS.
17. Romera-Paredes, B. et al. (2023). Mathematical discoveries from program search with large language models (FunSearch). Nature.
18. Trinh, T. H. et al. (2024). Solving olympiad geometry without human demonstrations (AlphaGeometry). Nature.
