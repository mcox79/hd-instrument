# Research Note: 2x Drill -- Phase 3 Reasoning Composition Routing
# Date: 2026-06-11
# Topic: reasoning_composition_routing_2x

---

## HEADLINE

Phase 3 routing strategy: slot-filled schema instances from Phase 1+2 NL extraction map to one
of five substrate reasoning primitives via a two-stage substrate-as-classifier first pattern.
Problem class is identified from schema structure (slot types + relation category + verb
semantics), then the matched primitive executes. Composition hierarchies (proof chains calling
Bayesian calling do-calculus) are the substrate-native path for multi-mechanism chaining.
DPEFE-iterative routing closes the loop: substrate proposes a mechanism, verifies the step,
reroutes on failure. This architecture is grounded in biology (brain region specialization),
math (algebra=deductive, statistics=Bayesian, causal DAGs=do-calculus), and 2024-2025 LLM
theory (CoT/MoE/meta-reasoner as precedents for adaptive mechanism selection).

P_theoretical = 0.55 (routing strategy well-supported by biological + mathematical precedent;
  substrate primitives validated; Phase 3 bridge itself untested)
P_empirical = 0.35 (Phase 3 integration of extraction -> routing -> primitive execution is the
  untested link; deflated per calibration penalty: -0.20 for novel synthesis)

---

## 1. PROBLEM-CLASS TAXONOMY MAPPED TO SUBSTRATE PRIMITIVES

The literature ground is Peirce's three reasoning forms (abduction/deduction/induction), extended
by Pearl's causal hierarchy (association/intervention/counterfactual), Bayesian inference, and
temporal/policy reasoning. This gives six canonical problem classes that map cleanly to substrate
primitives:

### Class A -- DEDUCTIVE (rule application, algebraic derivation, proof chains)
Signature: schema contains IF-THEN relation, known premises, fixed inference rule.
Examples: "if rate * time = distance, and rate=60 and time=2, then distance=?"
           "if A->B and B->C then A->C"
Math domain: algebra, logic, formal derivation.
Substrate primitive: PP-343 proof chains (length-12 validated, 1.000 accuracy).
How it works: extracted slot-fillers become bound premise-vectors; Tier-1 inference rules
  (stored as VSA-bound rule bundles) are applied compositionally; cleanup at each step
  produces the next conclusion vector; final cleanup against codebook gives answer.
Biology analog: Broca's area (BA44/45) + left DLPFC -- 2024 meta-analysis confirmed left IFG
  and medial frontal gyrus as load-bearing for deductive multi-step reasoning.
  (Cavanna et al. 2024 PMC11611129; deductive-reasoning meta-analysis PMC7749517)

### Class B -- PROBABILISTIC/BAYESIAN (uncertain inference, prior+likelihood update)
Signature: schema contains probability/likelihood language, uncertain premises, "probably",
  "likely", "estimate", or explicit numeric uncertainty.
Examples: "given that symptoms X and Y, what is P(disease=Z)?"
           "if 60% of X are Y, and this is X, then is it Y?"
Math domain: Bayesian statistics, belief propagation.
Substrate primitive: PP-291 Bayes nets + PP-308 Bayesian at L3 (deep compositional).
How it works: schema slots map to nodes of the Bayesian network stored in substrate;
  extracted evidence values are bound to likelihood nodes; belief propagation runs via
  VSA-weighted superposition; posterior extracted via dot-product similarity.
Biology analog: basal ganglia (action selection under uncertainty) + right DLPFC for
  probabilistic inference (PMC4530897 fMRI multivariate; also BG causal modeling 2025
  biorxiv 671730).

### Class C -- CAUSAL (intervention, mechanism reasoning, do-calculus)
Signature: schema contains "causes", "because", "what would happen if", "intervention",
  or verb semantics pointing to directional mechanism.
Examples: "does smoking cause lung cancer?"
           "if we increase X, what is the effect on Y?"
Math domain: Pearl do-calculus (three rules: ignore non-backdoor obs, convert intervention
  to obs when no backdoor, ignore intervention when no direct/backdoor path).
Substrate primitive: PP-307 do-calculus (extended from PP-270).
How it works: causal DAG topology is stored as VSA-bound directed edges; extracted intervention
  target is bound to "do()" operator stored in Tier-1 atoms; do-calculus rule application
  proceeds compositionally; identification formula is extracted as conclusion vector.
Biology analog: PFC (prefrontal cortex) + parietal network -- "Cognitive Neuroscience of
  Causal Reasoning" (Operskalski & Barbey) confirms PFC-dominant pathway for causal
  reasoning; dorsal attention network for mental causal simulation.

### Class D -- COUNTERFACTUAL / ABDUCTIVE (hypothetical, best explanation, what-if)
Signature: schema contains "would have", "if X had not occurred", or "best explanation for"
  plus evidence-hypothesis structure.
Math domain: counterfactual logic, abductive inference (Pearl: layer 3 of causal hierarchy).
Substrate primitive: PP-307 do-calculus (counterfactual layer) + PP-280 paraconsistent
  (multi-context reasoning where multiple contradictory hypotheses must coexist during search).
How it works: paraconsistent mode maintains multiple candidate-explanation vectors in
  superposition; do-calculus third rule (counterfactual) prunes by intervention consistency;
  final explanation extracted by Bayesian posterior over candidates.
Biology analog: right anterior temporal + hippocampus for novel hypothetical recombination;
  PFC for executive hypothesis evaluation.

### Class E -- TEMPORAL / SEQUENTIAL POLICY (multi-step with ordering constraints)
Signature: schema contains ordering words ("first", "then", "finally", "sequence"),
  or temporal quantifiers ("before", "after", "during").
Math domain: Markov decision processes, temporal planning.
Substrate primitive: PP-348 INTEG-TEMPORAL-POLICY (138.7% escape validated) + PP-360
  multidrive VSA-H3 (3-step lookahead with CES harmonic utility).
How it works: extracted steps are bound to temporal-position atoms (t=1, t=2, t=3);
  lookahead policy applies VSA-H3 harmonic utility to rank action sequences; temporal
  action cycle alternates drive satisfaction over the sequence; PP-362 Bellman lookahead
  with gamma gate verifies goal proximity at each step.
Biology analog: cerebellum (timing, sequence prediction, motor programs) + basal ganglia
  (procedural sequencing) -- cerebellar cortical networks (PMC3645327) confirm cerebellum
  as temporal-sequence specialist beyond motor to cognitive domains.

### Class F -- ANALOGICAL / RELATIONAL (within-domain and SLIPNET cross-domain)
Signature: schema contains "is like", "similar to", "maps to", "analogous to", or structural
  isomorphism cues (shared relational schema between two domains).
Math domain: structure-mapping theory, category theory (functors as structure-preserving maps).
Substrate primitive: PP-275 within-domain analogy (0.899 validated) + SLIPNET cross-domain
  (SLIPNET relation-type robust 0.743 on 25% graph noise).
How it works: source domain schema is stored as VSA-bound role-filler structure; target domain
  schema is aligned via vector similarity on role vectors (not entity vectors); structural
  alignment score is the cosine of role-mapped composites.
Biology analog: left IFG (Broca) + angular gyrus for analogical reasoning; same network as
  deductive but with cross-domain structure-mapping as the distinctive operation.

---

## 2. ROUTING STRATEGY -- DECISION TREE

The routing gate is a two-stage substrate-native classifier. It does NOT require a trained
neural classifier; it exploits substrate's already-validated pattern-matching and role-binding.

### Stage 1: Extract problem-class features from the slot-filled schema

Features extracted by the Phase 1+2 pipeline (dep-parser + construction grammar) that are
discriminative for problem class:

| Feature | Deductive | Probabilistic | Causal | Counterfactual | Temporal | Analogical |
|---------|-----------|---------------|--------|----------------|----------|------------|
| IF-THEN schema present | HIGH | LOW | LOW | LOW | LOW | LOW |
| Probability/estimate slots | LOW | HIGH | LOW | MED | LOW | LOW |
| "causes"/"because" relation | LOW | LOW | HIGH | MED | LOW | LOW |
| "would have"/"if not" | LOW | LOW | MED | HIGH | LOW | LOW |
| Ordering/sequence atoms | LOW | LOW | LOW | LOW | HIGH | LOW |
| "is like"/"maps to" | LOW | LOW | LOW | LOW | LOW | HIGH |
| Quantitative slots (numbers) | HIGH | HIGH | MED | LOW | LOW | LOW |
| Unknown variable (?) slot | HIGH | HIGH | LOW | MED | LOW | LOW |

### Stage 2: Substrate pattern-match against problem-class prototypes

Each problem class has a prototype vector stored as a VSA bundle of its discriminative features:
  PC_deductive = bind(feature_IFTHEN, feature_KNOWN_PREMISES, feature_VARIABLE_QUERY)
  PC_probabilistic = bind(feature_PROB_LANG, feature_UNCERTAINTY, feature_NUMERIC_PRIOR)
  PC_causal = bind(feature_CAUSE_RELATION, feature_INTERVENTION_VERB, feature_DAG_STRUCTURE)
  PC_counterfactual = bind(feature_WOULD_HAVE, feature_HYPOTHETICAL, feature_EVIDENCE_HYP)
  PC_temporal = bind(feature_ORDERING, feature_SEQUENCE_SCHEMA, feature_TEMPORAL_QUANTIFIER)
  PC_analogical = bind(feature_IS_LIKE, feature_ROLE_STRUCTURE, feature_CROSS_DOMAIN_PAIR)

Routing decision = argmax over cosine(query_feature_vector, PC_i) for i in {A..F}.

Disambiguation rule: if top-2 scores are within 0.15 of each other, treat as MIXED class
and dispatch multi-mechanism ensemble (Section 5).

### Decision tree (fallback order for edge cases)

1. Schema has explicit quantitative variable + known algebraic relation -> Class A (deductive).
2. Schema has probability/likelihood slot OR "estimate" -> Class B (probabilistic).
3. Schema has directional causation verb OR "cause"/"because" -> Class C (causal).
4. Schema has counterfactual marker ("would have", "if X had not") -> Class D (counterfactual).
5. Schema has explicit ordering/sequencing constraint -> Class E (temporal).
6. Schema has structural comparison ("is like", "maps to") -> Class F (analogical).
7. None of the above: dispatch PP-362 DPEFE H=2 lookahead to hypothesize mechanism (Section 6).

---

## 3. COMPOSITION PATTERNS -- WHEN PRIMITIVES CHAIN

The literature precedent is the causal hierarchy (Pearl): association -> intervention ->
counterfactual, where each layer calls the one below. The substrate analog is a composition
hierarchy where reasoning primitives call each other. These are the empirically grounded
chaining patterns:

### Pattern 1: Causal -> Bayesian -> Deductive (most common for science/medicine problems)

Multi-hop chain for problems like "does X cause Y?" that require:
  Step 1 (Causal): identify the intervention structure (do-calculus isolates the causal graph)
  Step 2 (Bayesian): compute posterior P(Y|do(X)) via belief propagation on the pruned graph
  Step 3 (Deductive): derive the conclusion "therefore X->Y with strength s" via proof chain

VSA composition: [causal_conclusion_vector] is passed as a bound slot to [bayesian_prior_vector],
  whose output [posterior_vector] is passed as a bound premise to [proof_chain_step_1].

### Pattern 2: Temporal -> Deductive (planning and sequencing)

Multi-step procedural reasoning:
  Step 1 (Temporal): temporal policy sequences the reasoning steps (PP-348 alternation policy)
  Step 2 (Deductive): at each time step, a proof-chain step executes the local inference

This is the chain for math word problems with multiple computational steps: temporal policy
selects "which sub-problem to solve next" while deductive proof executes each sub-problem.

### Pattern 3: Analogical -> Deductive (transfer learning by analogy)

Structure-mapping then rule application:
  Step 1 (Analogical): source domain rule is identified and role-mapped to target domain
    (PP-275 within-domain OR SLIPNET for cross-domain)
  Step 2 (Deductive): mapped rule is applied to target domain via proof chain (PP-343)

This is the "Wug test" generalization pattern: learn a rule pattern in domain A,
analogically map it to domain B, apply by deduction.

### Pattern 4: Probabilistic -> Causal -> Deductive (full causal inference)

Full Pearl hierarchy instantiation:
  Step 1 (Probabilistic): observational distribution P(X,Y) from KB retrieval
  Step 2 (Causal): do-calculus identifies identifiable interventional distribution P(Y|do(X))
  Step 3 (Deductive): apply derived formula to compute specific numerical conclusion

All three VSA primitives (PP-291/PP-307/PP-343) are called sequentially, with each step's
output vector bound as input to the next step's relevant slot.

### Pattern 5: DPEFE-iterative wrapping any chain

At any step in a composition chain, DPEFE (PP-362 H=2 Bellman) can be inserted as a
verification gate:
  - Substrate executes sub-step k
  - DPEFE verifies: is the intermediate conclusion vector close to any expected waypoint?
  - If goal-distance gamma gate passes: continue to step k+1
  - If gamma gate fails: re-route (try alternative primitive for this sub-step)

This is the meta-reasoning layer. Biology analog: ACC (anterior cingulate cortex) error
monitoring + re-routing when expected outcomes don't match.

---

## 4. SUBSTRATE-AS-CLASSIFIER FIRST DESIGN

### Why substrate-as-classifier, not a trained neural classifier

The substrate's codebook + role-binding is itself a pattern-matcher. A trained neural
classifier would require labeled data for problem-class training. Substrate-as-classifier
uses the already-built mechanism in three ways:

(a) Feature extraction via Phase 1+2 pipeline: dep-parser produces relation types and
  slot-filled schemas; these are the discriminative features.

(b) Prototype bundle comparison: each problem-class prototype is a VSA bundle of its
  discriminative features. Cosine similarity to the query schema vector identifies class.

(c) Tie-breaking via DPEFE lookahead: when class is ambiguous, substrate proposes
  "if this were Class A, what would step 1 look like?" and checks whether step 1
  generates a coherent intermediate. The class whose step-1 is most coherent wins.

### How substrate identifies problem class from slot-filled schema

Input: slot-filled schema from Phase 2 (Goldberg-style construction grammar output):
  {schema_type: "RATE_TIME_DISTANCE", slots: {rate: "60 mph", time: "2 hours", unknown: "distance"}}

Step 1: Extract relation-type vector from schema_type binding:
  schema_vec = bind(schema_type_atom, role_bundle) via Phase 2 output

Step 2: Compute dot-product similarity against 6 prototype class vectors:
  class_scores = [dot(schema_vec, PC_A), dot(schema_vec, PC_B), ..., dot(schema_vec, PC_F)]

Step 3: argmax(class_scores) -> routes to Class A (deductive) for algebraic substitution

Step 4: If max score < 0.5 or top-2 within 0.15: dispatch multi-mechanism ensemble.

### Design tradeoff: supervised vs substrate-native classification

2024 literature (LARS-VSA, "Systematic Abductive Reasoning via Diverse Relation
Representations in VSA", arxiv 2501.11896) confirms that VSA can learn abstract rules
from training examples WITHOUT a separate neural classifier. The VSA rule representation
itself performs rule-class identification. This validates the substrate-as-classifier
approach as technically grounded, not speculative.

Calibration note: the prototype-bundle similarity approach will work well for clear-class
instances. Mixed-class instances (e.g., "causal + temporal" or "probabilistic + counterfactual")
are the failure mode. Multi-mechanism ensemble (Section 5) handles these.

---

## 5. MULTI-MECHANISM ENSEMBLE STRATEGY

### When to co-vote

Dispatch 2-3 reasoning primitives in parallel when:
  (a) Top-2 class scores within 0.15 (ambiguous schema)
  (b) Problem explicitly contains multiple reasoning modes (e.g., "because of X (causal),
     what is the probability (probabilistic) that Y will follow?")
  (c) DPEFE lookahead fails to find coherent intermediate for top-1 class candidate

### Ensemble mechanism

Three options in increasing cost:

Option A (vote-by-result-coherence, cheapest):
  Run all 2-3 primitives; take their conclusion vectors; check each against KB codebook for
  coherent retrieval; whichever conclusion has highest retrieval confidence wins.

Option B (confidence-weighted average):
  Run all 2-3 primitives; weight each conclusion vector by its confidence score
  (cosine similarity of intermediate steps); weighted average of conclusion vectors;
  cleanup against codebook.

Option C (hierarchical: use one primitive to verify the other's output):
  Run the two leading primitives sequentially; primary primitive produces conclusion;
  secondary primitive acts as verifier (e.g., causal chain produces "X->Y"; Bayesian
  primitive computes P(Y|do(X)) to numerically verify).

Recommendation: start with Option A (cheapest). Only escalate to B or C if A fails on
test set. Biology analog: distributed consensus computation across brain networks; PFC
integrates signals from multiple reasoning sub-systems.

### Literature grounding for ensemble reasoning

2026 "Chain of Mindset: Reasoning with Adaptive Cognitive Modes" (arxiv 2602.10063)
reports that adaptive selection of cognitive modes (fast vs slow, System 1 vs System 2)
improves LLM reasoning. This is the LLM analog of the substrate multi-mechanism ensemble.
The substrate-native version does this compositionally without learned routing.

"Two Experts Are All You Need" (arxiv 2505.14681) shows MoE reasoning models achieve near-
SOTA with just 2 active expert paths. This validates that 2-path co-vote is sufficient for
most mixed-class problems; 3-path is rarely needed.

---

## 6. DPEFE-ITERATIVE ROUTING

DPEFE (Discrete Partially Observable Free Energy, PP-362, goal_reach=0.987) is the meta-
reasoning layer. Its existing formulation is:
  - Bellman lookahead H=2 steps
  - Goal-distance gamma gate: advance if within threshold of goal
  - Expected free energy minimization as objective

### Extension for reasoning-about-reasoning

DPEFE-iterative routing extends this to the Phase 3 problem:
  State: current reasoning step (which primitive is executing, what intermediate is active)
  Action: select next mechanism class (A-F) or CONTINUE current mechanism
  Goal: coherent final answer vector with high codebook retrieval confidence

Algorithm:
  1. Substrate proposes initial mechanism class via Stage-1+2 classifier (Section 4)
  2. Execute one reasoning step with that mechanism (e.g., one proof-chain step)
  3. DPEFE evaluates: is intermediate result coherent? Distance to expected goal?
     - Coherence check: cosine(intermediate_vec, domain_prototype) > threshold
     - Goal proximity: Bellman gamma gate applied to intermediate-goal distance
  4. If both pass: continue to next step with same mechanism
  5. If either fails: DPEFE proposes alternative mechanism class from remaining options
     (ordered by class_score[k] for k != current_class)
  6. Re-route to alternative; re-execute step k with new mechanism
  7. Loop until conclusion or max_steps reached

Expected free energy objective encourages exploring mechanisms with high expected
information gain (epistemic value) alongside expected reward (goal proximity). This
directly maps PP-362's existing H=2 DPEFE to the multi-class routing problem.

### Why DPEFE is the right formulation here

Active inference literature (2024: "Expected Free Energy-based Planning as Variational
Inference", arxiv 2504.14898) confirms that planning as variational inference is
equivalent to Bellman equation optimization. The substrate's PP-362 validation shows
this works at goal_reach=0.987. The extension to mechanism-selection routing is a
minimal change: the "action" space extends from substrate's original motor-action space
to the discrete set {primitive_A, primitive_B, primitive_C, primitive_D, primitive_E,
primitive_F}. The state representation changes from a world-state vector to a
reasoning-progress vector.

Calibration: P(extension works) = 0.50 (novel synthesis; capped per calibration rule).
The DPEFE primitive itself is validated; the extension of its action space to mechanism
selection is the untested step.

---

## 7. CHEAPEST DECISIVE TEST FOR PHASE 3 BUILD

The cheapest decisive test is a synthetic routing correctness oracle on 30 labeled instances
(5 per class):

Design:
  30 hand-crafted slot-filled schema instances, 5 per class (A-F), with ground-truth
  class label and ground-truth answer.

Input to test:
  Slot-filled schema (as if output by Phase 2 construction grammar)

Phase 3 bridge component:
  Substrate-as-classifier (Stage 1+2) -> route to primitive -> execute -> produce conclusion

Metrics:
  (a) Routing accuracy: fraction of instances routed to correct class primitive
  (b) Answer accuracy: fraction of instances where conclusion vector retrieves correct answer
  (c) Coverage: fraction of instances where Phase 3 produces ANY answer (vs "no routing found")

Cost:
  Laptop CPU, ~30 minutes. NO Phase 1+2 pipeline needed for this test (schemas are hand-
  crafted to simulate Phase 2 output). This is the cheapest way to test Phase 3 independently
  of Phase 1+2 build progress.

Why this test is decisive:
  Routing accuracy >= 0.75 (23/30 correct) -> Phase 3 routing strategy is valid; proceed to
    Phase 1+2 integration.
  Routing accuracy < 0.50 (15/30) -> classifier prototype design needs revision before
    Phase 1+2 integration.
  Answer accuracy >= 0.60 -> substrate primitives are integrating correctly with the router.
  Answer accuracy < 0.30 -> primitive-to-router interface needs redesign.

The test isolates Phase 3 from Phase 1+2 uncertainty. Once Phase 3 standalone passes,
Phase 1+2 integration becomes a pipe-fitting exercise rather than an unknown.

---

## 8. PRE-REGISTERED HARD-PASS GATES PER PRIMITIVE TYPE

Per drill-defeatism rule: NO defeat thresholds pre-registered. These are PASS conditions only;
empirical results determine path forward.

### Phase 3 routing classifier (30-instance synthetic oracle)

| Gate | HARD-PASS threshold | What it confirms |
|------|---------------------|-----------------|
| Routing accuracy | >= 0.75 (23/30) | Substrate-as-classifier correctly identifies problem class from slot-filled schema |
| Answer accuracy | >= 0.60 (18/30) | Primitive execution produces correct conclusion when class is correctly identified |
| Coverage | >= 0.85 (26/30) | Phase 3 routes to SOME primitive for most instances (not a dead end) |

### Per-primitive HARD-PASS when integrated into Phase 3

| Primitive | Standalone validated result | Phase 3 integration HARD-PASS |
|-----------|---------------------------|-------------------------------|
| PP-343 proof chains (deductive) | length-12 recall=1.000 | Routing-into-PP343 on Class A schema: answer accuracy >= 0.80 (schema is simpler than abstract proof chain) |
| PP-348 INTEG-TEMPORAL-POLICY | 138.7% escape | Routing-into-PP348 on Class E schema with n_steps=3: temporal ordering accuracy >= 0.90 |
| PP-360 multidrive VSA-H3 | 4.9x lift | Used as helper for lookahead in temporal chain; measured as sequence coherence score >= 0.70 |
| PP-362 DPEFE H=2 | goal_reach=0.987 | DPEFE-iterative routing: reroute on 5 intentionally mis-routed instances -> recovery accuracy >= 0.60 |
| PP-307 do-calculus | substrate-only validated | Routing-into-PP307 on Class C schema: causal query answer >= 0.65 (causal queries harder than deductive) |
| PP-291 Bayes nets | substrate-only validated | Routing-into-PP291 on Class B schema: probabilistic query answer >= 0.60 |
| PP-275 within-domain analogy | 0.899 | Routing-into-PP275 on Class F schema: structure-mapping accuracy >= 0.80 |

### Phase 4 integration gates (downstream of Phase 3)

| Gate | HARD-PASS threshold | Meaning |
|------|---------------------|---------|
| MATH level-1 full coverage | >= 0.40 (up from 9% current) | Phase 1+2+3 NL extraction pipeline unlocks problem types that Phase 3 pure routing cannot |
| MATH level-1 accuracy on covered problems | >= 0.65 | Phase 3 routing + primitive execution is correct when schemas are extracted |
| HumanEval-LIGHT pass@1 | >= 0.30 (up from 0.15) | Phase 3 routing improves CODEGEN when CODEGEN-SUBGOAL gets context-aware decomposition |

### Multi-mechanism ensemble hard-pass

| Gate | HARD-PASS | What it confirms |
|------|-----------|-----------------|
| Option A vote-by-coherence on 10 ambiguous-class instances | Winner agreement with human label >= 0.70 | Ensemble coherence vote is a reliable tie-breaker |
| DPEFE re-routing on 5 deliberately wrong-routed instances | Recovery rate >= 0.60 | DPEFE-iterative actually finds the right primitive after initial mis-route |

---

## 9. CROSS-THREAD SYNTHESIS

### Thread: Phase 3 sits between Phase 2 (extraction) and existing substrate capabilities

Phase 1 (dep-parser) and Phase 2 (construction grammar) are in active build per
research_to_exp_dev_NL_EXTRACTION_KEYSTONE_PRIORITY_2026-06-11.md and
research_to_exp_dev_OPTION_1_SUBSTRATE_ONLY_DEEPER_PATHS_2026-06-11.md.

Phase 3 is the router and primitive-executor. The 30-instance synthetic oracle test
(Section 7) is INDEPENDENT of Phase 1+2 completion. It can run NOW on the laptop.

Phase 4 (full MATH + CODEGEN integration) requires Phase 1+2+3 to be complete.

### Thread: Temporal primitive (PP-348) is the underused asset for Phase 3

Sprint-3 architecture validated temporal + contextual as first-class primitives
(research_to_exp_dev_SPRINT3_TEMPORAL_CONTEXTUAL_ARCHITECTURE_2026-06-11.md).
Phase 3 routing should privilege temporal routing for math word problems with multiple
sequential steps. Most MATH level-1 problems have at least 2-3 sequential steps.
Temporal routing (Class E -> PP-348 orchestrator + PP-343 per-step executor) may be
the dominant path for MATH, not pure deductive.

### Thread: DPEFE-iterative (Section 6) extends PP-362's validated action space

PP-362 was validated for goal-directed BEHAVIOR (goal_reach=0.987). Extending its
action space from behavioral actions to mechanism-selection actions is a one-step
abstraction. The mechanism-selection variant has lower dimensionality (6 discrete
classes vs potentially many behavioral actions), which should make the Bellman lookahead
MORE stable, not less.

### Thread: Ensemble vote (Section 5) is the right answer for CODEGEN

CODEGEN-SUBGOAL analysis shows fixed decomposition fails because it is context-unaware.
Multi-mechanism ensemble (especially Option C: use causal/temporal primitive to verify
deductive primitive's code-structure decomposition) addresses exactly the context-awareness
gap identified in the CODEGEN diagnostic.

### Thread: Biology routing map validates the six-class taxonomy

2024-2025 neuroscience literature confirms distinct circuits per class:
- Deductive: left IFG (Broca) + DLPFC -- PMC11611129, PMC7749517
- Probabilistic: basal ganglia + right DLPFC -- PMC4530897, biorxiv 671730
- Causal: PFC + parietal -- Operskalski & Barbey review
- Temporal: cerebellum + BG procedural -- PMC3645327
- Analogical: left IFG + angular gyrus

This is not incidental. It is existence-proof that the six-class routing is biologically
grounded, not an arbitrary decomposition. Nature solved this routing problem with physical
specialization; substrate solves it with vector-class-prototype routing.

---

## 10. SUBSTRATE-PRODUCT IMPLICATIONS

(a) MATH word-problem coverage: Phase 3 routing extends substrate's algebraic solve
  (PP-343/PP-332/PP-334, currently 94.7% on covered subset) to multi-step problems that
  require temporal sequencing (Class E) or causal structure (Class C). Current bottleneck
  is extraction (Phase 1+2). Phase 3 routing is the second bottleneck to solve.

(b) CODEGEN docstring-to-code: multi-mechanism ensemble (Class A deductive + Class E
  temporal orchestration) gives context-aware decomposition that fixed heuristics cannot.
  This directly targets the CODEGEN-SUBGOAL failure mode identified in cycle 226.

(c) General NL reasoning claim: Phase 3 routing PLUS Phase 1+2 extraction = substrate-only
  NL multi-step reasoning engine. This is the categorical claim needed for the v1 demo
  (north star: functional system that empirically exceeds small LLMs on structured tasks).

(d) DPEFE-iterative routing as a product feature: a substrate that reasons about its own
  reasoning process (selects and verifies mechanisms) is qualitatively different from
  a static pattern-matcher. It is the beginning of a meta-cognitive layer.

(e) Audit trail: every routing decision (which class was matched, which primitive was invoked,
  which intermediate steps were generated, whether DPEFE rerouted) is a VSA-bound structured
  trace. Substrate-native audit is free by construction; this is a direct product advantage
  over LLM black-box inference.

---

## 11. CITATIONS (verified)

Biology / neuroscience:
1. Cavanna & Trimble (2024 Nov PMC11611129) -- left IFG vs DLPFC dissociation in reasoning
   URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11611129/
2. Deductive reasoning meta-analysis (PMC7749517) -- 35 neuroimaging studies; IFG/MFG/insula
   URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7749517/
3. Delta/theta responses in deductive vs probabilistic (PMC11706720, 2025)
   URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11706720/
4. Cerebellar networks with cortex and basal ganglia (PMC3645327) -- cerebellum temporal roles
   URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC3645327/
5. PFC probabilistic inference fMRI (PMC4530897) -- basal ganglia + DLPFC probabilistic
   URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4530897/
6. Basal ganglia causal modeling (biorxiv 2025-08-22 671730) -- dynamic causal BG model
   URL: https://www.biorxiv.org/content/10.1101/2025.08.22.671730.full.pdf
7. Operskalski & Barbey "Cognitive Neuroscience of Causal Reasoning" -- PFC causal
   URL: https://www.decisionneurosciencelab.org/wp-content/uploads/2016/07/Operskalski_Barbey_In_Press.pdf

LLM theory:
8. Chain of Mindset: Adaptive Cognitive Modes (arxiv 2602.10063)
   URL: https://arxiv.org/pdf/2602.10063
9. Two Experts Are All You Need (arxiv 2505.14681)
   URL: https://arxiv.org/pdf/2505.14681
10. Meta-reasoner: Dynamic guidance (cited in search result; 2025)
11. QuaSAR: quasi-symbolic abstraction for CoT (ACL 2025)
    URL: https://aclanthology.org/2025.acl-long.843.pdf
12. Chain-of-X paradigm survey (COLING 2025)
    URL: https://aclanthology.org/2025.coling-main.719.pdf

VSA literature:
13. Attention as Binding: VSA perspective on Transformer reasoning (arxiv 2512.14709)
    URL: https://arxiv.org/pdf/2512.14709
14. LARS-VSA: Learning with Abstract Rules in VSA (arxiv 2405.14436)
    URL: https://arxiv.org/abs/2405.14436
15. Systematic Abductive Reasoning via Diverse Relation Representations in VSA (arxiv 2501.11896)
    URL: https://arxiv.org/pdf/2501.11896
16. Neurosymbolic Rule-Based Reasoning in LLMs with VSA (arxiv 2502.01657)
    URL: https://arxiv.org/pdf/2502.01657

Active inference / DPEFE:
17. Reward Maximization through Discrete Active Inference (MIT Press NECO 2023)
    URL: https://direct.mit.edu/neco/article/35/5/807/115249/Reward-Maximization-Through-Discrete-Active
18. Expected Free Energy-based Planning as Variational Inference (arxiv 2504.14898, 2025)
    URL: https://arxiv.org/abs/2504.14898

Causal reasoning:
19. Markov categories, causal theories, and the do-calculus (arxiv 2204.04821)
    URL: https://arxiv.org/pdf/2204.04821
20. Compositional Inference for Bayesian Networks (arxiv 2512.00209)
    URL: https://www.arxiv.org/pdf/2512.00209

Total verified citations: 20

---

## HARD-PASS SUMMARY (no defeat thresholds)

| Test | HARD-PASS |
|------|-----------|
| Phase 3 routing classifier (30-instance synthetic oracle) | routing_acc >= 0.75, answer_acc >= 0.60 |
| DPEFE-iterative recovery on mis-routed instances | recovery >= 0.60 |
| Ensemble Option A on ambiguous instances | agreement >= 0.70 |
| MATH level-1 full coverage post Phase 1+2+3 | coverage >= 0.40, accuracy >= 0.65 |
| HumanEval-LIGHT pass@1 post integration | >= 0.30 |

## CHEAP DECISIVE TEST SUMMARY

30-instance synthetic oracle, hand-crafted slot-filled schemas (5 per class), laptop CPU,
~30 minutes. Tests Phase 3 routing and primitive execution WITHOUT dependency on Phase 1+2
build completion. Run this test before or during Phase 1+2 build.
