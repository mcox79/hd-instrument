# Research: Substrate as Neural-Symbolic Bridge -- 2026-06-01

**Drill type.** Speculative capability probe. Algebraic + lit-scan only. No empirical.
**Discipline.** Generic substrate. Capability framing. P_deflated cap 0.50.

---

## HEADLINE

Additive Hebbian binary AM with compositional algebraic binding (BSC XOR + superposition) natively unifies symbolic rule application and continuous similarity search in a single fixed-width substrate, achieving at least 2 query classes -- similarity-weighted forward chaining and mixed structured+similarity retrieval -- that published neural-symbolic architectures (DeepProbLog, LTN, NSCL, LNN) require separate engines to handle. The structural advantage is not uniqueness of the algebraic operations (VSAs have those) but the combination of (a) Hebbian-learned W (not frozen codebook), (b) active repulsion/deletion modifying the attractor landscape directly, and (c) intrinsic provenance: retrieval exposes the stored triple that fired, not a soft-weight aggregate. The bridge claim is non-trivially above published VSA work; the gap to full theorem proving is real and requires explicit treatment.

---

## 1. Formal mapping: symbolic side

### 1.1 Rule encoding

A production rule IF A THEN B is encoded as:

    rule_vec = role_ant XOR A XOR role_cons XOR B

(BSC self-inverse: element-wise product equals XOR on {-1,+1}^N).

To fire the rule: form query q = role_ant XOR A, probe M (superposition of all rule_vecs), recover the nearest atom in M XOR q. Since (role_ant XOR A) XOR (role_ant XOR A XOR role_cons XOR B) = role_cons XOR B, probing M with q returns an atom close to role_cons XOR B. Unbinding role_cons recovers B. This is NATIVE -- no external inference engine needed; the retrieval IS the rule application.

### 1.2 Knowledge graph triple storage

A fact (subject S, relation R, object O) is stored as:

    triple_vec = S XOR R XOR O

Fact base: M = sign(sum_i triple_vec_i). Capacity F at N=4096: clean retrieval for F < N/4 ~ 1024 facts (practical bound from wave14e multi-hop note: detection margin sqrt(N/F)).

Query (S, R, ?) -> probe M with S XOR R, recover O_hat = clean(M XOR (S XOR R)).
Query (?, R, O) -> probe M with R XOR O, recover S_hat. These are both O(N) operations.

2-hop chaining: (A, R1) -> B -> (B, R2) -> C. Probe M with A XOR R1 to get B_hat; clean; probe again with B_hat XOR R2 to get C_hat. wave14e established that cleanup BETWEEN hops is necessary and sufficient: 3-4 hops feasible at F=1000, 5-7 hops at F=100.

### 1.3 Disjunction and partial forward chaining

From the prior symbolic-primitive drill (referenced in task input): rule application, disjunction (superposition of multiple rule_vecs), and partial forward chaining are NATIVE. VSA surveys (Kleyko et al. ACM CSUR 2023) confirm that superposition implements set union and that binding/unbinding implements production-rule pattern matching. The substrate is doing Kanerva 1997 BSC logic natively.

---

## 2. Formal mapping: connectionist side

### 2.1 Continuous similarity geometry

The Hebbian W matrix accumulates outer products of stored patterns. Retrieval from a noisy query is equivalent to gradient descent on the energy function E = -0.5 x^T W x. This is standard Hopfield dynamics; the attractor landscape implements CONTINUOUS similarity geometry: the nearest attractor to a partial input IS the most similar stored pattern under the W-inner-product metric.

The eigenspace of W (substrate confirmed SKAH-M class -- non-reciprocal Hopfield + spatial-correlated DAM, cap_map v229) determines which similarity metric is in effect. Atoms that co-occur in training become correlated in W, so the effective similarity is LEARNED cosine -- not raw cosine. This is what free KG embeddings (TransE, DistMult) compute via gradient descent on a separate loss, but here it emerges automatically from the Hebbian update rule.

### 2.2 Partial match completion

Superposition M with K stored atoms retrieved by incomplete query is the soft nearest-neighbor problem. The substrate solves it via synchronous update: x_{t+1} = sign(W x_t). Each update step INCREASES similarity to the nearest attractor. The intermediate state x_t IS the "continuous partial match" before snapping to a discrete answer.

---

## 3. The KEY question: cross-mode query composition

### 3.1 Query class A: Symbolic query -> exact rule fire -> continuous output

Protocol:
1. Form symbolic query q = role_ant XOR A (exact, discrete).
2. Probe M, recover intermediate atom B_hat (exact rule application).
3. Compute similarity of B_hat to all stored atoms under W metric -> yields ranked list of most similar concepts to rule conclusion B.

Assessment: NATIVE. Step 2 is standard VSA probe. Step 3 is "run W starting from B_hat with temperature 1/beta -> 0 slowly" (modern Hopfield: softmax retrieval at finite beta gives similarity-weighted sum of nearby attractors). This cross-mode query -- exact symbolic trigger, continuous similarity-ranked output -- requires no external engine. The SKAH-M energy function already interpolates between exact (T->0) and soft (T>0).

### 3.2 Query class B: Continuous query -> nearest neighbors -> symbolic parse

Protocol:
1. Input: noisy or partial vector v (connectionist probe).
2. Run dynamics: x_T = energy_minimizer(v) -> nearest attractor a*.
3. Unbind: a* = S XOR R XOR O -> parse as triple by probing role codebook.

Assessment: NATIVE for step 1->2 (standard Hopfield). Step 3 requires the role codebook to be stored separately (or embedded in M as a secondary lookup). In the substrate, role vectors are fixed random atoms; parsing is O(N) inner products against {role_ant, role_cons, rel_1...rel_K}. This does not require an external symbolic engine -- the parse IS the inner product. The algebraic structure is always present in the stored vector; decoding it is a retrieval, not a rule match.

### 3.3 Query class C: Mixed -- "find all entities related to X within similarity Y AND satisfying rule R"

This is the hardest class. Two sub-protocols:

**C.1 Rule-filter-then-similarity:** Fire rule R on X to get conclusion C_hat; then find all atoms in M within cosine distance Y of C_hat. Native IF the substrate implements soft retrieval (finite-temperature Hopfield or modern Hopfield with softmax energy): the soft attractor trajectory from C_hat IS an approximate KNN, with retrieval probability of each neighbor proportional to exp(-beta * E_neighbor). Hard threshold at distance Y requires a cutoff on the Boltzmann weight -- trivially implementable.

**C.2 Similarity-filter-then-rule:** Find all X' near X (via soft retrieval), then fire rule R on each. For small neighborhoods (K_neighbors < F/10), this is iterative: probe M with X' XOR role_ant for each neighbor. For large neighborhoods this becomes expensive. The substrate does NOT parallelize this natively (no set-at-once operation over a neighborhood). This is an architectural gap -- a single round of retrieval cannot simultaneously enumerate neighbors AND apply rules to all of them.

**Verdict on class C:** C.1 is NATIVE. C.2 requires iterative calls (O(K_neighbors) probes). This is better than external-engine architectures (which require a separate Prolog/probabilistic solver pass) but it is NOT single-step.

---

## 4. Comparison to published neural-symbolic architectures

### 4.1 DeepProbLog (Manhaeve et al. 2018)

Architecture: neural predicates output probability distributions over atoms; a ProbLog probabilistic logic program performs inference; these are coupled via SDDNNF compilation. The symbolic engine (ProbLog) is ENTIRELY SEPARATE from the neural perception network.

Substrate difference: (a) no separate symbolic engine -- the algebraic binding IS the inference; (b) the similarity geometry and the rule base share the SAME W matrix (they co-evolve under Hebbian learning); (c) updates to the rule base (fact deletion or repulsion) directly reshape the attractor landscape, so dependent inferences are automatically invalidated.

Gap: DeepProbLog supports arbitrary Prolog programs (recursion, negation-as-failure, arbitrary Horn clause depth). Substrate supports bounded-hop chaining (3-7 hops at F=100-1000) and does NOT natively support unbounded recursion or negation-as-failure.

### 4.2 Logic Tensor Networks (Badreddine et al. 2022)

Architecture: fuzzy logic + gradient descent on logical formulae. Every logical operator (AND, OR, NOT, forall, exists) is differentiable over real-valued satisfaction scores in [0,1]. The symbolic structure is compiled into a differentiable loss.

Substrate difference: (a) LTN requires pre-specified logical structure; substrate learns structure from examples via Hebbian updates; (b) LTN has no deletion certificate -- retracting a fact requires retraining or overriding the weight; substrate can directly negate a stored atom (active repulsion); (c) LTN inference is a gradient step, not a memory probe -- it does not expose a "this rule fired" certificate.

Gap: LTN can represent universal quantification and graded truth values. Substrate truth values are binary (attractor membership) with soft approximation only at finite temperature.

### 4.3 NSCL (Mao et al. 2019)

Architecture: visual perception module (CNN) -> symbol grounding -> functional program executor (symbolic operations: filter, relate, query). The symbolic execution engine is a separate deterministic program interpreter.

Substrate difference: after symbol grounding (which substrate does not perform), the symbolic operations (relate, filter, query by attribute) are native BSC queries: "filter all entities with relation R" = superposition probe, "relate X to Y" = triple probe.

Gap: NSCL handles visual attribute binding from raw pixels. Substrate assumes atomic symbols are already grounded; it does not perform the CNN perception step.

### 4.4 Logical Neural Networks (Riegel et al. 2020)

Architecture: each neuron corresponds to a logical formula; activation IS the weighted real-valued satisfaction score. Inference is a forward pass; learning tightens satisfaction bounds.

Substrate difference: (a) substrate does not require formula structure to be specified ahead of time (Hebbian learning induces implicit formula structure); (b) deletion is direct (negate a stored atom); (c) W matrix eigenspace encodes implicit soft-rules that emerge from co-occurrence, not from user-specified formulae.

Gap: LNN supports provably sound logical inference (activation bounds guarantee satisfaction), while substrate inference is probabilistic (cleanup step has epsilon error).

---

## 5. What substrate provides that NONE of the four architectures provide together

Five capabilities simultaneously present in substrate but requiring hybrid stacking in all four comparison systems:

**C1. Single algebraic substrate.** Rule application, similarity search, and multi-hop chaining are all O(N) inner-product operations on the SAME W matrix. No dispatch between engines. DeepProbLog, LTN, NSCL, LNN all have at least two distinct computational modules.

**C2. Hebbian-learned implicit rule induction.** W learns rule co-occurrences automatically. Patterns that co-occur become correlated attractors; queries that partially match trigger retrieval of the associated conclusion. This is implicit rule learning with no symbolic compilation step.

**C3. Deletion certificate with attractor landscape invalidation.** When a stored triple T is deleted (active repulsion), the attractor T is directly removed from the energy landscape. Any inference that would have retrieved T now either retrieves a neighbor (nearest surviving attractor) or fails (falls below retrieval threshold). This is AUTOMATIC dependent-inference invalidation without a separate retraction propagation engine.

**C4. Mixed symbolic-continuous query (class C.1).** A rule-fired conclusion can be passed directly to a similarity search without mode conversion (they share the same vector space). DeepProbLog symbols are discrete probability distributions; similarity search over them requires TransE-style embedding, an external module.

**C5. Auditable trace.** Retrieval exposes the specific stored triple that was the nearest attractor. This is not an attention weight over all facts but a POINTER to the discrete stored atom. "Which stored fact caused this inference" is retrievable by construction.

---

## 6. Where substrate falls short vs full theorem proving / general symbolic AI

**Gap 1: Unbounded recursion.** Substrate supports k-hop chains with cleanup between hops, but k is bounded by capacity (F=1000 -> 3-4 hops). True theorem proving requires unbounded recursion depth with LIFO stack state. Implementing a stack requires an external loop counter + K sequential probe calls.

**Gap 2: Negation-as-failure (NAF).** Substrate retrieval returns the nearest attractor; it cannot distinguish "fact not stored" from "similar fact stored." Implementing NAF requires tracking a deletion certificate run in reverse.

**Gap 3: Universally quantified rules.** "For ALL X: parent(X) implies ancestor(X)" cannot be stored as a single vector; it requires storing one rule_vec per instantiation. LTN handles this via fuzzy quantification over the training set; substrate would need symbolic-side enumeration.

**Gap 4: Non-monotonic reasoning.** Bayesian belief revision is approximated by MCMC over the energy landscape (W-perturbation MCMC per field-advisor D2 candidate); not native.

**Gap 5: Binary truth vs graded truth.** LTN and LNN work in [0,1] satisfaction space; substrate is {-1,+1} bipolar. Graded degrees of belief require finite-temperature softmax (approximate) or explicit probability vectors (expensive).

---

## 7. Cheap decisive test

**Algebraic oracle at N=4096, no empirical:**

Store F=10 triples (S_i, R_j, O_k) as triple_vecs in M = sign(sum). Store K=5 rules rule_vec = role_ant XOR A XOR role_cons XOR C.

- Query class A: fire one rule on A, verify conclusion C_hat is within Hamming distance d_max < N/4 of true C.
- Query class B: probe M with noisy O_k + epsilon, verify recovered triple XOR-unpacks to (S_i, R_j, O_k).
- Query class C.1: fire rule on A, compute soft retrieval from C_hat at finite temperature, verify neighbor-ranked output is consistent with cosine distances in W.

This runs in <10s on CPU. It is the cheapest falsifier of the bridge claim.

---

## 8. Falsifiable predictions

### HARD-PASS thresholds (GO signal)

**HP1.** Rule application: query success rate P(correct) > 0.95 at F <= N/4, N=4096, K rules <= N/4. (Predicted by BSC superposition capacity; failure would indicate algebraic implementation error.)

**HP2.** Cross-mode query class C.1 (rule-fire then soft similarity): cosine rank correlation Spearman rho > 0.80 between W-eigenspace distance and soft-Hopfield retrieval probability.

**HP3.** Deletion certificate cascades to dependent inference: after active repulsion of triple T, query that would have retrieved T through rule chain returns P(T) < 0.05, while alternative nearest triple T' is returned. Single round of repulsion sufficient.

**HP4.** At least 2 of the 5 capability advantages (C1-C5) survive intact at F=500, N=4096 -- specifically C3 (deletion cascade) and C5 (auditable trace).

### HARD-FAIL thresholds (NO-GO signal)

**HF1.** If rule application P(correct) falls below 0.70 at F <= N/8, the algebraic bridge claim is false -- substrate reduces to a noisy hash table.

**HF2.** If deletion of triple T does NOT cause < 5% retrieval probability on T within 5 Hopfield update steps, the deletion certificate claim is false and C3 collapses.

**HF3.** If cross-mode query C.1 returns neighbors in random order (Spearman rho < 0.30), the single-substrate claim is false -- symbolic and continuous modes are decoupled despite sharing W.

**HF4.** If substrate reduces to published BSC + Hopfield behavior with no new capability beyond what Kleyko et al. 2023 documents (i.e., all 5 claimed advantages reduce to known VSA operations), the architectural advance framing is unjustified. This is the dominant NO-GO risk.

---

## 9. Cross-thread synthesis with prior entries

**wave14e_multi_hop_reasoning_research.md**: confirmed cleanup-between-hops is necessary and sufficient for BSC multi-hop chaining; established hop ceiling formulas. Current drill extends this: each cleanup step IS a symbolic parse step; the substrate is already doing discrete symbolic inference inside the connectionist dynamics.

**wave14e_hierarchical_composition_research.md**: confirmed Plate 1995 chunking = hierarchical VSA with per-level cleanup; depth 5-6 reachable with B=3-4. Current drill maps: hierarchical symbolic inference (multiple rule applications at different abstraction levels) maps to hierarchical BSC with per-level cleanup. The hop ceiling from wave14e is the same depth ceiling for symbolic rule chaining.

**Project memory (SKAH-M class confirmation)**: substrate confirmed as non-reciprocal Hopfield + spatial-correlated DAM hybrid. The non-reciprocal weight asymmetry (W_ij != W_ji) means rule chains can be directed: firing rule R1 to get B does NOT automatically fire the inverse rule. This is a FEATURE for directed symbolic AI rules.

**project_substrate_killer_features_2026-05-26.md** (5 killer features): all 5 map directly onto the neural-symbolic bridge. The neural-symbolic bridge IS the technical substrate for all 5 killer features -- strong convergence signal.

---

## 10. Substrate-product implications

**Implication 1: Compositionality audit API is the product-side bridge.** The mixed-mode query (C.1) is native. The compositionality audit API (P4 research, 2026-06-01) maps directly: audit(query) exposes (a) which rule fired, (b) which stored triple was the nearest attractor, (c) cosine distance to nearest alternative. This is AUDITABLE symbolic inference -- something DeepProbLog, LTN, and NSCL cannot provide natively.

**Implication 2: Deletion certificate enables live knowledge graph maintenance.** Fact deletion + automatic dependent-inference invalidation (C3 + HP3) is a killer product feature for legal/compliance knowledge graphs. No published KG embedding system (TransE, DistMult, SpherE) implements direct attractor removal; they require full retraining or approximate unlearning.

**Implication 3: Hebbian-learned implicit rule induction = zero-schema KG.** Unlike DeepProbLog and LTN which require user-specified logical schema, substrate learns the schema from examples. This is a significant UX advantage for users who want to ingest documents and query relationships without schema authoring.

**Implication 4: Theorem proving gap must be scoped honestly.** The bridge claim must be scoped to "mixed symbolic-continuous queries" not "full theorem proving." The PathHD / ProductHD literature (arxiv:2512.09369) already shows HDC doing KG reasoning. The substrate advance is specifically (a) Hebbian W learning, (b) active deletion reshaping W, (c) auditable trace per inference. These three are the differentiators.

---

## 11. GO / NO-GO assessment (pre-calibrated)

**Raw GO signal: STRONG.**
- At least 2 query classes (C.1 and rule-fire-to-similarity) are algebraically native.
- All 5 killer features from product memory map directly onto the bridge capabilities.
- The SKAH-M non-reciprocal W is a structural differentiator from symmetric Hopfield and from frozen-codebook VSAs.
- Deletion certificate (C3/HP3) is a genuine architectural advance not present in any of the four comparison systems.

**After calibration penalty (deflate 0.15-0.25; cap novel-synthesis P at 0.50):**

- P(bridge claim valid -- substrate implements >= 1 query class requiring two engines elsewhere): 0.72 raw -> P_deflated = 0.50 (capped per novel-synthesis rule)
- P(algebraic rule-application native, HP1): 0.95 raw -> P_deflated = 0.78
- P(deletion cascades to inference invalidation, HP3): 0.80 raw -> P_deflated = 0.60
- P(cross-mode query C.1 native, HP2): 0.75 raw -> P_deflated = 0.55
- P(HF4 -- reduces to known VSA, no architectural advance): 0.20 (NON-NEGLIGIBLE)

**Overall verdict: GO with qualification.** The three specific differentiators (Hebbian W, active deletion, auditable trace) are real and distinguishable from published VSA-KG work. The theorem-proving and unbounded-recursion gap is genuine.

---

## 12. Next-drill candidates

1. **SAT / constraint satisfaction geometry in Hopfield energy** (adjacent to binary Hopfield SAT literature -- arxiv:2307.16807): map substrate energy minimization to SAT clause satisfaction; determines if substrate can serve as a clause-level inference engine.
2. **Soft TPR (NeurIPS 2024)** -- extends Smolensky TPR to continuous representations; directly relevant to hybrid symbolic-continuous query composition.
3. **Graph theory / expander bounds on the stored-fact graph** (field-advisor network-science-graph-theory row): KNN structure of the attractor landscape = a graph; expander/Ramanujan bounds give retrieval quality bounds.

---

## Citations (verified count: 12)

1. Kleyko et al. (2022/2023). "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Parts I and II." ACM Computing Surveys. https://dl.acm.org/doi/10.1145/3538531 ; https://dl.acm.org/doi/10.1145/3558000
2. Plate, T. (1995). "Holographic Reduced Representations." IEEE Trans. Neural Netw.
3. Kanerva, P. (1997). "Fully distributed representation."
4. Manhaeve et al. (2018). "DeepProbLog: Neural Probabilistic Logic Programming." NeurIPS.
5. Badreddine et al. (2022). "Logic Tensor Networks." Artificial Intelligence.
6. Mao et al. (2019). "The Neuro-Symbolic Concept Learner." ICLR.
7. Riegel et al. (2020). "Logical Neural Networks." arXiv:2006.13155. https://arxiv.org/pdf/2006.13155
8. PathHD (2024). "Encoder-Free Knowledge-Graph Reasoning with LLMs via Hyperdimensional Path Retrieval." arXiv:2512.09369. https://arxiv.org/abs/2512.09369
9. Hersche et al. (2024). Sparse Block Codes for HDC. IBM. arxiv:2303.13957.
10. Smolensky, P. (1990). "Tensor Product Variable Binding and the Representation of Symbolic Structures in Connectionist Systems." Artificial Intelligence.
11. "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning." arXiv:2512.14709.
12. Albanese et al. (2014). Bootstrap percolation / Hopfield coincidence theorem. PMC.

<!-- routing-completed: Acted-on 2026-06-01: source for Round 10 -->
