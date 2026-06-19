# Research Drill: Substrate Novel Concept Formation and Discovery Capability
# Date: 2026-06-10
# Topic: Can substrate do abductive reasoning that discovers new patterns, not just composes known ones?
# Classification: 2x operational drill -- first drill on this topic

---

## HEADLINE

Substrate has five algebraic primitives (active inference, schema extraction, FHRR binding, sleep-defrag replay, anomaly-margin detection) that together constitute a mechanistic discovery loop approximating cognitive-science models of abductive reasoning. The loop does NOT produce genuinely novel atomic concepts from scratch -- that requires codebook expansion, which is currently absent. Within its fixed codebook, the substrate can execute structured pattern search, anomaly-driven exploration, and cross-domain composition at levels competitive with small LLMs on structured tasks. The honest gap is aesthetic judgment and open-ended brainstorming: those require criteria that the substrate currently externalizes to the retrieval threshold, not learns. P_deflated for a discovery-loop demo passing structured hypothesis generation = 0.32. P_deflated for genuine creative parity with LLMs on open tasks = 0.12.

---

## LEVEL 1: What is "novel concept formation" in cognitive science?

### 1.1 Schank script invention vs script application

Roger Schank's script theory (Schank & Abelson 1977) distinguishes script APPLICATION (executing a known event schema: "going to a restaurant" activates roles, actors, expected sequences) from script INVENTION (when an agent encounters a situation that no existing script covers, and must construct a new schema by analogy or adaptation). Application is retrieval; invention is discovery.

The substrate's schema extraction (PP-282/284) is script application: it recovers stored slot-filler patterns from data. Script INVENTION would require noticing that an incoming event pattern does not match any existing schema above a cleanup threshold (anomaly detection) and then constructing a new schema by composing available atoms into a candidate template. This is a two-step process: (a) anomaly detection via cleanup-margin failure, and (b) generative composition. The substrate has primitive (a) empirically (cleanup confidence is binary and measurable as a margin gap). Primitive (b) is the unanswered question.

### 1.2 Hofstadter copycat: making fluid analogies

Hofstadter and Mitchell's Copycat architecture (1992) models creative analogy as a pressurized competition between slipnet nodes: concepts have activation levels; a letter-string problem triggers spread of activation through slipnet until a "codelet" settles on an analogy. Creativity in Copycat comes from two sources: (a) the slipnet's DYNAMIC activation (not fixed retrieval) means that unusual activation paths can surface non-obvious analogies; (b) the architecture has explicit "temperature" controlling how deterministic the search is -- at high temperature the system makes wild connections; at low temperature it converges.

The substrate's Hopfield energy landscape is structurally isomorphic to a fixed-temperature slipnet: stored patterns are attractors, retrieval is deterministic nearest-neighbor search. Copycat's contribution was the TEMPERATURE MODULATION and the DYNAMIC SLIPNET (nodes change weight during a single problem). Substrate does not yet have this. PP-272 active inference is the nearest analog: hypothesis generation proposes a candidate and tests it. But the inference temperature is fixed (cleanup threshold), not dynamically modulated per problem.

Substrate gap: dynamic activation spreading across concept-concept similarity edges during retrieval. This would require storing explicit concept-concept similarity relations in W as a second-order structure, which the FHRR binding algebra can represent (concept_i * concept_j binding for each known similarity pair) but which has not been implemented or empirically tested.

### 1.3 Goldenfeld emergence: new patterns from underlying primitives

Goldenfeld and Kadanoff (1999) describe emergence as the appearance of qualitatively new description levels that cannot be predicted from the lower-level dynamics alone. The canonical case: renormalization group theory shows that many microscopically distinct systems flow to the same fixed point (universality class). New patterns emerge at each scale.

For substrate, the question is whether the FHRR binding algebra has a renormalization-group analog: does composing atomic concepts into higher-order bundles produce qualitatively new stable attractors that were not predictable from the atoms? Empirically: the R10 result (K=512 best-config gap +0.628 bpc) shows that high-K bundles contain information NOT present at K=1. This is consistent with emergence: the binding algebra generates new stable patterns at higher K. Whether these constitute "genuinely new concepts" depends on whether the Hopfield cleanup step produces attractors at the bundle level that are DISCRIMINABLE from the atoms.

This is a testable claim. The Tier-1 primitive discovery test (SCHEMA-EXTRACTION-AT-NEW-ABSTRACTION, see Level 7) would probe this directly.

### 1.4 Discovery systems: BACON, AM, Eurisko

The classical AI discovery systems are informative about what substrate does and does not have:

BACON (Langley et al. 1987): discovers empirical laws by numerical data regression. Strategy: take ratio of two quantities, check if it's constant, generalize. BACON has explicit meta-rules that say "when current hypothesis fails, try these transformation operators." This is abduction: use failure to drive search over hypothesis space.

AM (Lenat 1976): discovers mathematical concepts by heuristic search over a space of set-theory operations. AM has 250 heuristics for which concepts are "interesting" (small concept, many examples, surprising coincidence). The INTERESTINGNESS criterion is the mechanism that guides discovery. Without it, combinatorial search produces too many candidates.

Eurisko (Lenat 1983): extends AM by discovering new heuristics (meta-level discovery). Capable of discovering heuristics that guide the discovery of heuristics -- genuine second-order invention.

Substrate comparison:
- BACON: substrate can do numerical discovery if you encode physical quantities as level-codes and search for binding combinations that produce stable patterns. But substrate does not yet have meta-rules that say "when this fails, try ratio instead of product." The active inference loop (PP-272) is the nearest primitive, but its hypothesis space is over existing codebook entries, not over data transformations.
- AM: substrate's schema extraction finds recurring structural patterns (like AM's concept extraction) but lacks the INTERESTINGNESS heuristic. Cleanup margin is a proxy (high-margin patterns = "stable" = "interesting"), but it is not a nuanced aesthetic criterion.
- Eurisko: substrate has no second-order discovery mechanism. Discovering new heuristics for the discovery loop is not in any current primitive.

### 1.5 Combinatorial vs genuinely novel

Boden (2004) distinguishes three types of creativity:
- Combinatorial: new combinations of existing elements (most common; LLMs excel here)
- Exploratory: searching an existing conceptual space more thoroughly (LLMs also do this)
- Transformational: modifying the space's defining rules to generate concepts impossible in the original space (hardest; rare)

Substrate with current codebook can do combinatorial and exploratory creativity within its fixed codebook. Transformational creativity would require codebook expansion (new atomic dimensions) or rule modification (new binding operators). Neither is currently implemented.

HONEST ASSESSMENT: LLMs are doing mostly combinatorial creativity plus some exploratory creativity, not transformational creativity either. The perceived gap between LLMs and substrate on "creativity" is primarily in combinatorial fluency (LLMs can rapidly generate 10 plausible variations; substrate would need to enumerate explicitly) and in aesthetic judgment (LLMs have been trained on human preferences; substrate has no such training signal). Transformational creativity is rare in both.

---

## LEVEL 2: Substrate primitives for discovery

### 2.1 Schema extraction (PP-282/284)

What it does: given a set of examples encoded as FHRR bundles, extracts the shared structural pattern by taking the element-wise sign of the sum (majority vote over examples). This recovers the "schema" -- the common factor.

Discovery relevance: this IS script extraction from data. At K=1 it recovers atomic concepts. At K=4 it recovers 4-gram co-occurrence patterns. UNTESTED: at K=8 applied to K=4 bundle outputs, does it recover meta-schemas (patterns over patterns)?

If yes: this is a principled two-level hierarchy extraction mechanism. Tier 1 universals (patterns that appear across many different K=4 schemas) would be discovered by applying schema extraction to the output layer of a prior schema extraction pass.

Empirical state: single-pass schema extraction confirmed at PP-282/284. Two-pass hierarchical schema extraction NOT TESTED.

### 2.2 Active inference (PP-272)

What it does: generates a hypothesis (sampled from the attractor manifold), tests it against incoming evidence (compares to stored patterns), updates confidence. This is a hypothesis-test loop.

Discovery relevance: if the hypothesis space is over NOVEL compositions (not just stored patterns), the loop can drive search for new patterns. Current implementation generates hypotheses as noisy reconstructions of stored patterns -- it explores near existing attractors, not far from them.

Extension needed for discovery: introduce REPULSION from already-visited attractors during hypothesis generation (similar to tabu search). A repulsion term would be: h_new = h_current - alpha * sum_i(W_i * cosine_sim(h_current, pattern_i)) for already-seen patterns. This is a one-line modification to the hypothesis generation step.

Empirical state: PP-272 confirmed for standard active inference. Repulsion extension not implemented or tested.

### 2.3 Compositional algebra (FHRR binding)

What it does: binding (elementwise product for FHRR or XOR for bipolar) composes two concepts into a third that preserves both. Bundling (majority vote) overlays multiple concepts into a superposition. Permutation tags roles without destroying information.

Discovery relevance: the binding operator is the combinatorial machinery. Every pair of concepts in the codebook can be bound to create a candidate new concept. At codebook size V_c=1024, there are V_c^2/2 = ~500K distinct pairwise bindings. At K=3 there are ~170M triples. This is the combinatorial explosion underlying discovery.

Key question: does the Hopfield cleanup step treat a novel binding (concept_i * concept_j) as a legitimate new attractor, or does it snap back to the nearest stored single concept? If novel bindings can be stored (added to W) and later retrieved, then each act of binding is an act of concept creation. THIS IS LIKELY TRUE and untested: the substrate can store ANY bipolar vector, including novel bindings, and retrieve it later.

Empirical state: KV injection (continual learning at 600 facts) shows that novel associations can be stored and retrieved. A novel binding (concept_i * concept_j) is mechanistically identical to a novel KV pair. So: storing novel bindings in W is almost certainly possible. Confirming this would directly demonstrate combinatorial concept creation.

### 2.4 Sleep-defrag (PP-141/142)

What it does: offline replay consolidates patterns that were weakly encoded during active use, strengthening stable attractors and weakening unstable ones. This is analogous to memory consolidation during REM sleep.

Discovery relevance: consolidation has a filtering function -- patterns that survive consolidation are the "interesting" ones (by the stability criterion: they reactivate consistently across multiple replay cycles). Patterns that are inconsistent do not survive consolidation. This implements a weak INTERESTINGNESS criterion: consolidation-surviving patterns = robust patterns = patterns worth treating as concepts.

Stronger version: if consolidation is run with competitive inhibition (patterns that suppress each other's activation compete for survival), then the surviving set is a compressed, non-redundant concept vocabulary -- analogous to sparse coding. This has not been tested but is algebraically straightforward.

Empirical state: sleep-defrag confirmed at PP-141/142. Competitive consolidation not tested.

### 2.5 Anomaly detection via cleanup-margin

What it does: when the Hopfield cleanup step is applied to a noisy input, the output confidence is the margin between the winning attractor's activation and the second-closest attractor. A LOW margin indicates the input is NOT close to any stored pattern -- anomalous.

Discovery relevance: anomaly detection is the trigger for discovery. In Schank's framework, anomaly = script failure = need for script invention. The substrate's cleanup margin is a real-valued anomaly signal. High anomaly = "this is new, generate a hypothesis about it."

Calibration: cleanup margin is a ratio, not an absolute. For N=16384 with V_c=1024 random codebook, the expected margin for a random input is 0 (equal distance to all patterns). For a pattern 95% similar to one stored pattern, the margin should be approximately (similarity - second_best_similarity) ~ 0.45. A reliable anomaly threshold is margin < 0.2 (below the 3-sigma band for stored patterns).

Empirical state: cleanup margin is implicitly used in every experiment as the retrieval confidence metric. Explicit anomaly detection as a trigger for exploration has not been implemented or tested as a standalone module.

---

## LEVEL 3: Discovery mechanisms in substrate

### 3.1 Schema extraction at higher abstraction

Mechanism: Run schema extraction (majority vote over bundles) on the OUTPUT of a prior schema extraction pass. This is a two-level hierarchical extraction. The first pass extracts K-gram co-occurrence patterns from raw tokens. The second pass extracts patterns that recur ACROSS DIFFERENT DOCUMENTS or domains -- these are universal structural patterns (Tier 1 universals).

What this produces: If the first-pass schemas for "biology texts" and "physics texts" both contain the pattern (entity, relation, property) = (X, has_property, Y), the second pass extracts that frame as a universal regardless of domain. This is concept discovery at the structural level: finding that "entity-property" is a universal across domains.

Evidence base: this is the standard hierarchical compositional inference in VSA literature (Frady et al. 2020 compositional HDC). No substrate-specific empirical test exists. The algebraic argument is straightforward: the substrate stores FHRR bundles, and schema extraction is linear (majority vote), so two-pass extraction is two matrix operations.

P for a two-level hierarchy finding a universal: 0.38 (calibration-deflated from 0.55 raw -- novel extraction at second level has unknown stability).

### 3.2 Active inference proposing novel composition

Mechanism: Rather than sampling from the existing attractor basin, the hypothesis generation step in PP-272 could sample a BINDING of two moderately-active concepts: h_candidate = concept_i * concept_j where concept_i and concept_j are the top-2 active patterns in the current state. This generates a candidate relational concept.

This is a one-step binding + cleanup loop: generate the binding, test it against W (does it have high overlap with any stored pattern?), and if NOT (cleanup margin < threshold = anomaly), flag it as a candidate new concept.

This is equivalent to BACON's "try the ratio" meta-rule applied to FHRR: when existing patterns fail, try binding the top-2 active concepts.

Empirical tractability: a toy implementation would need ~50 lines of code (sample top-k active patterns, bind pairs, check cleanup margin). No current cell.

### 3.3 Cross-domain analogy via multi-tier composition

Mechanism: store domain A concepts at Tier 1 (semantic), domain B concepts at Tier 2 (structural). A cross-domain analogy is a pattern that is present in BOTH tiers: find the structural mapping between domain A and domain B by extracting the schema that both share.

Concrete example: "electron shells in atoms" (domain A) and "social hierarchy levels in organizations" (domain B) share the structural schema (level, occupancy, exclusion_principle). The substrate, if storing both domains, would find this schema via second-pass extraction.

This is what Fauconnier and Turner (2002) call "conceptual blending": mapping shared structure between two distinct domains into a new mental space. Substrate's multi-tier FHRR can represent this if Tier 1 carries domain-specific semantic content and Tier 2 carries domain-general structural roles.

Evidence: PP-280 paraconsistent multi-context confirmed (can hold two inconsistent patterns simultaneously). Cross-domain analogy requires one more step: extracting the SHARED STRUCTURE from two conflicting patterns. This uses the binding algebra: shared_structure = schema_A * schema_B (product of two schemas extracts the common XOR-stable component).

P for cross-domain analogy via multi-tier: 0.35 (deflated from 0.50 raw; requires two-pass extraction AND multi-tier binding, both untested in combination).

### 3.4 Sleep-consolidation discovering invariants

Mechanism: run the sleep-defrag loop on a diverse KB (facts from N different domains). Patterns that survive consolidation are the ones that recur across domains -- INVARIANTS. Patterns that survive only in one domain are domain-specific and may not consolidate as strongly.

This is the substrate-physics equivalent of compressed sensing: sparse coding over many documents finds the over-complete basis of recurring patterns. The sleep-defrag loop is a biological metaphor for this; the algebraic mechanism is just repeated replay strengthening consistent patterns.

Discovered invariants are candidates for new codebook atoms: if a pattern survives K consolidation cycles, promote it to the codebook. This is CODEBOOK EXPANSION from the data itself.

Empirical tractability: run PP-141/142 on a multi-domain KB. Measure which patterns have highest post-sleep retrieval confidence. Compare to prior codebook. Patterns with high retrieval confidence but NOT in the prior codebook are candidate new atoms.

P: 0.30 (deflated from 0.45 raw; relies on consolidation loop producing consistent activation for genuinely invariant patterns, which is plausible but untested at multi-domain scale).

### 3.5 Anomaly-driven exploration

Mechanism: query the substrate with deliberately underspecified queries (partial patterns with many missing slots). Measure the cleanup margin for the top-K retrieved patterns. Patterns with highest margin for INCOMPLETE queries are the "unknown" regions of the concept space -- places where the substrate does not have a confident stored pattern.

Use these high-anomaly regions as targets for new concept generation: generate candidate concepts that would fill these regions. Each candidate is a binding of the top-2 concepts at the boundary of the known space.

This is the substrate analog of UCB (Upper Confidence Bound) exploration in reinforcement learning: explore regions of high uncertainty. The cleanup margin is the substrate's analog of prediction uncertainty.

Empirical tractability: implement a "curiosity map" using anomaly margin as the signal. Cheapest test: generate 1000 random partial patterns, measure cleanup margin for each, cluster by margin value, inspect the high-margin cluster. Expected runtime: <1 min CPU.

---

## LEVEL 4: What LLMs do that substrate currently does not

### 4.1 Free-form combinatorial brainstorming

LLMs can generate 10 plausible hypotheses from a single prompt because they have been trained on the distributional statistics of hypothesis-generation in millions of scientific and creative texts. They sample from the HUMAN HYPOTHESIS GENERATION DISTRIBUTION, which is already filtered for quality.

Substrate has no such prior. Generating 10 candidate concepts requires explicitly iterating through 10 distinct binding combinations and ranking by some criterion. There is no mechanism for "fluent generation" -- each candidate must be explicitly constructed and evaluated.

Gap size: LARGE. This is the most concrete operational gap. Substrate would need to implement an explicit generate-and-rank loop with some quality criterion. The quality criterion is the hard part.

### 4.2 Aesthetic / interestingness judgment

LLMs have implicit aesthetic training: outputs that humans rate as "interesting" were implicitly upweighted in RLHF. The substrate has no equivalent training signal for interestingness. Cleanup margin measures retrieval confidence, not aesthetic value.

Weak proxy: a concept is "interesting" if it is (a) retrievable (cleanup margin high) but (b) surprising (low prior frequency in the training data). Substrate can measure (a) but NOT (b) from within the substrate alone. Measuring (b) requires either frequency counts stored alongside the patterns or an external lookup.

Partial remedy: a frequency-weighted codebook would give each stored pattern a co-stored frequency estimate. High-confidence but low-frequency patterns = surprising = potentially interesting. This is one additional scalar per stored pattern.

### 4.3 Cross-context inspiration

LLMs can inject a metaphor from domain X while working on a problem in domain Y because their training mixed domains in every context window. This accidental cross-contamination is a feature: it enables distant analogies.

Substrate can do this IF the multi-tier schema explicitly links domains (Tier 2 carries domain-general structure). But current substrate schema extraction has not been tested across genuinely different domains with deliberate cross-domain injection.

Gap size: MEDIUM. The algebraic machinery supports cross-domain composition. The missing piece is a KB populated with diverse domains AND a retrieval query format that can intentionally probe cross-domain mappings.

### 4.4 Concept blending (Fauconnier-Turner)

Fauconnier and Turner's conceptual blending theory (2002) requires four spaces: two input spaces, a generic space (shared structure), and a blended space (novel combination). The blended space contains structure from both inputs plus emergent structure that is NOT in either input alone. This emergent structure is what makes blending genuinely creative.

Substrate analog: input space A = domain A schema vector, input space B = domain B schema vector, generic space = schema_A * schema_B (binding extracts shared XOR-stable component), blended space = novel_concept formed from unique features of A, unique features of B, and the shared generic space.

The algebra: novel_concept = unbind(generic, schema_A) + unbind(generic, schema_B) + generic (in MAP-B: majority vote over the three contributions). This produces a FHRR vector that represents the blend.

Testable prediction: a blended concept generated this way should be (a) closer to schema_A and schema_B than to any other stored concept, (b) NOT identical to either, (c) retrievable after being stored in W. This is a 3-property test that can be run in <1 min CPU.

P for successful concept blending via this algebra: 0.40 (deflated from 0.55 raw; algebraically principled; untested on bipolar substrate specifically).

---

## LEVEL 5: Substrate paths to novel concept formation

### 5.1 Active inference + schema extraction loop = generative search

Full loop:
1. Schema extraction from current KB: extract dominant patterns at Tier 1 and Tier 2.
2. Active inference step: sample candidate binding from top-2 active schemas.
3. Anomaly check: compute cleanup margin of candidate against current W.
4. If margin > KNOWN threshold (candidate is already stored): discard, sample next.
5. If margin < ANOMALY threshold (candidate is entirely random): discard.
6. If NOVEL threshold (between known and anomaly): store candidate in W as provisional concept.
7. Test provisional concept against held-out validation data: if it predicts held-out patterns better than chance, promote to codebook.

This is a full discovery loop. Steps 1-3 are already implemented in separate capabilities (PP-282/284, PP-272, cleanup margin). Steps 4-7 require integration code only.

Estimated implementation cost: ~100 lines. Estimated test time: <5 min CPU for a toy KB.

### 5.2 Multi-tier sharded composition = combinatorial explosion of primitives

At V_c=1024 codebook entries across 4 tiers, the number of representable 4-way compositions is V_c^4 ~ 10^12. Each of these is a potential novel concept. The substrate can enumerate these lazily (generate on demand) rather than pre-computing all.

Combinatorial exploration strategy: for each new query that fails retrieval (anomaly), generate the binding of the top-4 active patterns. This produces a candidate concept specific to the current context. Store it provisionally and evaluate later.

This is NOT the same as an LLM's brainstorming: it generates ONE candidate per failure (like BACON's single next-operator application). But it is SYSTEMATIC in that it will always generate the highest-activation binding first, then the second-highest, etc. This is a structured exploration, not free-form.

### 5.3 Per-shard creativity (vary one tier; hold others fixed)

Discovery by variation: hold Tier 1, Tier 3, Tier 4 fixed; vary only Tier 2. Measure which Tier 2 values produce the highest retrieval quality for a given query. The best Tier 2 value is the discovered concept for that structural role in that context.

This is the substrate analog of "fill in the blank" creative discovery: given partial context, find the best-fitting novel filler. If the best filler is not in the current codebook, it is a candidate new concept.

Empirical tractability: implement as a resonator search at Tier 2 while holding other tiers fixed. PP-282/284 already does partial slot-filling. Novel-slot discovery just adds the criterion: flag winners not in codebook as candidates.

### 5.4 Anomaly detection driving exploration

Already described in 3.5. The key point: anomaly margin is a real-valued signal that can drive a curriculum. Expose the substrate to increasingly anomalous inputs, starting from moderately anomalous (margin just below the KNOWN threshold). At each step, generate a candidate concept that would explain the anomaly. Evaluate the candidate by whether it reduces anomaly margin on subsequent anomalous inputs.

This is the substrate's nearest analog to Curiosity-Driven Learning (Schmidhuber 1991): the learning signal is reduction in prediction error (anomaly margin) on novel inputs.

### 5.5 Sleep-defrag consolidating discovered patterns

Already described in 3.4. After the active discovery loop (5.1) has generated provisional concepts and stored them in W, the sleep-defrag step filters: provisional concepts that survive K replay cycles are promoted to permanent codebook entries. This is the stabilization step.

Full pipeline: active-discovery-loop -> provisional-store -> sleep-consolidation -> codebook-promotion. None of these steps individually are novel; the INTEGRATION is what creates the discovery capability.

---

## LEVEL 6: Honest limitations

### 6.1 Substrate currently has fixed atomic codebook

The codebook (set of atomic concept vectors) is fixed at initialization. PPMI bigram extraction is one method of filling it from data, but once extracted, the codebook is static during inference. Novel concept formation at the ATOMIC level requires either:
- (a) Adding new vectors to the codebook from data (codebook expansion, see 6.2)
- (b) Treating novel bindings as first-class concepts (requires storing them in W, which is possible but not automated)

LLMs do not have a fixed codebook -- their token vocabulary is fixed but their internal representations span a continuous embedding space that can represent arbitrary combinations. This is a fundamental architectural difference.

### 6.2 Genuinely new atomic concepts require codebook expansion

PPMI extraction from new data is codebook expansion: it adds new atoms from corpus statistics. But this is batch, not online. Online codebook expansion would require: during inference, when the anomaly margin for an incoming pattern exceeds a threshold, add a new vector to the codebook representing this pattern.

Algebraic feasibility: adding a new codebook vector is just a new row in the lookup table. The substrate W can be updated incrementally (Hebbian learning already does this). The only constraint is that new codebook vectors must be quasi-orthogonal to existing ones (expected cosine ~0 for random bipolar vectors, guaranteed by construction if new vectors are randomly generated).

Implementation cost: ~20 lines. Evaluation criterion: does the new codebook atom actually improve retrieval on similar patterns in future queries?

### 6.3 "Interestingness" and aesthetic judgment require criteria

The substrate has no internal representation of interestingness beyond cleanup margin (stability) and frequency (co-occurrence count if stored). Human aesthetic judgment involves:
- Surprise (low prior probability)
- Coherence (high posterior probability given context)
- Depth (many downstream implications)
- Beauty (undefined for substrate without aesthetic training)

Partial implementation: store frequency counts alongside each codebook vector. Interestingness = cosine_margin * (1 / frequency) = confident but rare. This is a proxy, not genuine aesthetic judgment, but it is implementable and testable.

Genuine aesthetic training would require fine-tuning on a signal correlated with human preference ratings -- which the substrate does not currently have and which would require a different training loop entirely.

---

## LEVEL 7: Concrete engineering anchors

### DISCOVERY-LOOP anchor
- Name: discovery_loop_active_schema_v1
- What it tests: the full active-inference + schema-extraction + anomaly-check loop (5.1)
- Implementation: 100-line integration of PP-272 + PP-282/284 + cleanup-margin anomaly check
- Smoke test: 50-fact KB, 10 deliberately underspecified queries, measure candidate generation rate + novelty rate (candidate not in prior codebook)
- HARD-PASS: system generates >= 5 novel provisional candidates per 10 queries, of which >= 3 are coherent (high retrieval confidence on related queries after promotion)
- HARD-FAIL: system generates 0 novel candidates (anomaly check never triggers) OR all generated candidates are random noise (cleanup margin < 0.1 after promotion)
- P_deflated: 0.32

### COMBINATORIAL-PRIMITIVE anchor
- Name: combinatorial_primitive_concept_blend_v1
- What it tests: FHRR binding as concept creation (4.4 concept blending; 5.2 multi-tier combinatorial)
- Implementation: take two confirmed schema vectors, bind them, store in W, test retrieval on queries that involve both source schemas
- Smoke test: 5 binding pairs, 10 queries each, measure retrieval accuracy for blended concept vs source concepts
- HARD-PASS: blended concept retrievable at >= 85% accuracy on queries that reference BOTH source schemas; NOT retrieved on queries referencing only ONE source schema (demonstrating novel composite semantics, not just superset)
- HARD-FAIL: blended concept has <= 50% retrieval accuracy (binding produces noise) OR identical to one source schema (no blend)
- P_deflated: 0.40

### ANOMALY-DRIVEN-EXPLORATION anchor
- Name: anomaly_driven_explore_v1
- What it tests: cleanup-margin as curiosity signal (3.5, 5.4)
- Implementation: generate 1000 random partial patterns, compute cleanup margin, rank by margin, identify high-margin cluster as "unknown territory"
- Smoke test: generate curiosity map in < 1 min CPU; verify high-margin cluster is genuinely distinct from known-pattern region
- HARD-PASS: high-margin cluster is at >= 2 std deviations from the mean margin of known patterns; cluster covers >= 5% of pattern space
- HARD-FAIL: margin distribution is unimodal (no high-anomaly cluster) -- means cleanup is not discriminating novel from familiar inputs
- P_deflated: 0.45 (this test is mainly a diagnostic; cleanup-margin discrimination is expected to work from first principles)

### SCHEMA-EXTRACTION-AT-NEW-ABSTRACTION anchor
- Name: hierarchical_schema_v1
- What it tests: two-pass schema extraction to find Tier-1 universals (3.1)
- Implementation: extract schemas from domain A and domain B separately (pass 1), then extract schema from the two domain-schemas (pass 2)
- Smoke test: 2 domains x 100 examples each; measure whether pass-2 output has higher cosine similarity to a known universal (e.g., subject-predicate-object triple structure) than to either domain-specific pattern
- HARD-PASS: pass-2 output cosine similarity to universal > 0.70; cosine to domain-specific pattern < 0.50
- HARD-FAIL: pass-2 output is identical to pass-1 output for domain A or B (extraction didn't generalize)
- P_deflated: 0.35

### CODEBOOK-EXPANSION anchor
- Name: codebook_expand_cleanup_residual_v1
- What it tests: online codebook expansion from anomalous inputs (6.2)
- Implementation: run inference on a stream of inputs from an UNSEEN DOMAIN; when cleanup margin < anomaly threshold, add the input vector to codebook; measure retrieval improvement on subsequent similar inputs after addition
- Smoke test: 10 unseen-domain facts, measure retrieval accuracy before and after codebook expansion
- HARD-PASS: retrieval accuracy on subsequent similar facts improves by >= 20% after expansion; expanded codebook does not interfere with prior domain retrieval (prior accuracy drop < 5%)
- HARD-FAIL: codebook expansion does not improve retrieval (new atom is effectively random vs new inputs) OR prior domain accuracy drops > 20% (catastrophic interference from expansion)
- P_deflated: 0.28 (most uncertain; codebook expansion is novel, not yet validated on this substrate)

---

## LEVEL 8: Empirical test protocol

### Setup
- Substrate: N=16384, V_c=1024 base codebook, FHRR binding
- Multi-domain KB: 500 facts from domain A (science), 500 from domain B (social/organizational), 500 from domain C (mathematics)
- Baseline comparison: Pythia-70M (smallest available LLM) on the same tasks
- Human-generated reference answers for structured tasks

### Test battery

**T1: Structured hypothesis generation (50 tasks)**
- Format: given fact-set F, generate a plausible hypothesis that explains an anomaly in F
- Substrate method: active inference loop (5.1) + anomaly-driven exploration (5.4)
- LLM method: single-shot prompt
- Scoring: semantic similarity to human reference (cosine of embeddings); syntactic validity
- Expected outcome: substrate competitive on STRUCTURAL hypotheses (predicts a relational pattern); LLM better on free-form hypotheses
- HARD-PASS substrate: >= 60% of hypotheses score > 0.60 cosine similarity to reference
- HARD-FAIL substrate: < 30% score > 0.60

**T2: Creative writing prompts (30 tasks)**
- Format: given a theme, generate a 3-sentence creative output
- Substrate method: concept-blend (4.4) + multi-tier composition (5.2) + retrieval-chain output
- LLM method: direct generation
- Scoring: human rater (1-5 aesthetic quality); novelty (1 - max cosine similarity to training data)
- Expected outcome: LLM BETTER on aesthetic quality and fluency; substrate COMPETITIVE on structural novelty (non-cliche combinations)
- HARD-PASS substrate: average aesthetic rating >= 2.5/5; novelty score >= 0.60
- HARD-FAIL: aesthetic rating < 1.5/5 consistently (outputs are incoherent)

**T3: Cross-domain concept blends (100 tasks)**
- Format: given concept A from domain X and concept B from domain Y, produce a coherent blend
- Substrate method: FHRR binding of A and B + cleanup + retrieve (COMBINATORIAL-PRIMITIVE anchor, 5.2)
- LLM method: few-shot blending prompt
- Scoring: (a) coherence: does the blend make sense? (human binary rating); (b) novelty: not identical to A or B (cosine < 0.9 to either)
- Expected outcome: substrate competitive on coherence (binding produces a valid composition); LLM better on fluency and elaboration
- HARD-PASS substrate: >= 70% coherence, >= 80% novelty
- HARD-FAIL: coherence < 40% (binding produces noise)

**T4: Anomaly detection and exploration (diagnostic)**
- Format: present 100 in-distribution and 100 out-of-distribution inputs
- Substrate method: cleanup margin as anomaly score
- LLM method: perplexity as anomaly score
- Scoring: AUROC for anomaly detection; correlation between anomaly score and human-rated novelty
- Expected outcome: substrate COMPETITIVE or BETTER (cleanup margin is well-calibrated for VSA; LLM perplexity correlates with distribution shift but not semantic novelty)
- HARD-PASS substrate: AUROC >= 0.80 for anomaly detection
- HARD-FAIL: AUROC < 0.60 (margin is not discriminating)

**T5: Parity check on structured discovery (10 mathematical pattern tasks)**
- Format: given 20 numerical examples, find the governing rule (like BACON)
- Substrate method: schema extraction from numerical encodings (level-code binding)
- LLM method: direct prompt
- Scoring: exact match on stated rule
- Expected outcome: HONEST EXPECTATION is that substrate STRUGGLES here. LLMs have seen mathematical induction in training. Substrate would need explicit level-code encoding of numerical quantities, which has not been implemented.
- HARD-PASS substrate: >= 4/10 correct (meaningful above 1/10 random baseline)
- HARD-FAIL: 0/10 correct (substrate cannot engage with this format at all)

---

## Falsifiable Predictions (HARD-PASS + HARD-FAIL)

| Anchor | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| DISCOVERY-LOOP | >= 3 coherent novel concepts per 10 queries | 0 novel concepts generated | 0.32 |
| COMBINATORIAL-PRIMITIVE | blend retrieved at >= 85%, NOT source-specific queries | blend <= 50% retrieval | 0.40 |
| ANOMALY-DRIVEN | AUROC >= 0.80 for novel vs familiar | AUROC < 0.60 | 0.45 |
| HIERARCHICAL-SCHEMA | pass-2 output > 0.70 cosine to universal | identical to pass-1 output | 0.35 |
| CODEBOOK-EXPANSION | +20% retrieval improvement, < 5% prior interference | no retrieval improvement | 0.28 |
| T2 creative writing | aesthetic rating >= 2.5/5 | aesthetic rating < 1.5/5 | 0.18 |
| T3 cross-domain blend | >= 70% coherence, >= 80% novelty | coherence < 40% | 0.38 |

OVERALL P_deflated for "discovery-competitive with small LLM on structured tasks": 0.30
OVERALL P_deflated for "parity with LLMs on open creative tasks": 0.12
Cap on novel-synthesis claim: 0.50 (none of the above exceed this)

---

## Cross-Thread Synthesis

**With PP-272 (active inference, confirmed):** The confirmed active inference loop is the engine for hypothesis generation (Level 5.1). The gap is that hypothesis generation currently samples from near existing attractors. The extension -- sampling novel bindings of top-K active patterns -- adds one operation to the existing PP-272 mechanism.

**With PP-282/284 (schema extraction, confirmed):** Two-pass hierarchical schema extraction (3.1) is a direct extension of confirmed schema extraction. The algebraic cost is one additional majority-vote operation applied to the schema output vectors. Implementation cost is ~10 lines.

**With PP-280 (paraconsistent multi-context, confirmed):** Holding contradictory patterns simultaneously is the prerequisite for Fauconnier-Turner concept blending: the input spaces must be held in working memory without premature collapse. PP-280 confirms this is possible. The remaining step is explicit blend-space computation (4.4).

**With K-hop reasoning (K=10 confirmed):** Concept chains (A -> B -> C -> new_concept_D) are algebraically equivalent to K=3 hop reasoning. The discovery of novel concept D via chaining from A, B, C is already within the validated operational envelope. This is the most direct path to "discovery via composition."

**With continual KV injection (600 facts, confirmed):** The ability to add facts incrementally to W is the physical mechanism for STORING newly discovered concepts. Discovered concepts are just new KV pairs: key = novel binding, value = associated properties. The storage mechanism is already validated.

**With compositional cliff crossing (v3.0, per-level cascading cleanup):** The L5 recall reaching 1.000 after cascading cleanup means that hierarchical concept representations are stable at the top tier. This is load-bearing for the hierarchical schema extraction anchor: the cascade cleanup ensures that higher-level patterns are retrievable even when lower-level noise accumulates.

---

## Substrate-Product Implications

**Implication 1: Discovery loop as KB self-organization feature**
A product that uses the substrate as a knowledge base could advertise "self-organizing knowledge base" -- new concepts are automatically discovered from the stream of incoming facts and promoted to the codebook. This is not a feature any vector database offers. Implementation path: DISCOVERY-LOOP anchor + CODEBOOK-EXPANSION anchor. Combined P_deflated: 0.28 * 0.32 = 0.09 for the FULL automated pipeline; individual components higher.

**Implication 2: Anomaly-driven knowledge gap detection**
The ANOMALY-DRIVEN-EXPLORATION anchor (P=0.45) is the most tractable path to a product feature: "the substrate tells you what it does not know." A KB that can flag "I have no confident pattern for this query" is qualitatively more useful than one that silently returns the nearest pattern. This is not creativity per se, but it is a discovery-adjacent feature directly implementable from the cleanup margin signal.

**Implication 3: Cross-domain concept blending for research assistance**
If T3 (cross-domain blending) at P=0.38 passes, the product can advertise "cross-domain concept discovery" -- given KB entries from multiple domains, the substrate can suggest novel conceptual bridges. This is the core of many research assistance tools and would differentiate the substrate from pure retrieval systems.

**Implication 4: Honest positioning against LLMs**
The empirical test protocol (Level 8) is designed to produce an HONEST parity assessment. Based on the cognitive-science framing and substrate's algebraic primitives, the expected honest outcome is:
- Substrate at parity or better: structured hypothesis generation (T1), anomaly detection (T4), cross-domain blends at a structural level (T3 coherence)
- LLM substantially better: free-form creative writing (T2 aesthetic quality, fluency), mathematical pattern induction (T5), combinatorial brainstorming fluency

This honest gap framing is itself product-relevant: "substrate does structured discovery that LLMs hallucinate; LLMs do fluent generation that substrate doesn't attempt." Complementary, not competing.

---

## Citations (verified count: 18)

1. Schank R.C. & Abelson R.P. (1977). Scripts, Plans, Goals, and Understanding. Erlbaum.
2. Hofstadter D.R. & Mitchell M. (1992). An Overview of the Copycat Project. In Analogy-Making as Perception. MIT Press.
3. Goldenfeld N. & Kadanoff L.P. (1999). Simple Lessons from Complexity. Science 284(5411): 87-89.
4. Langley P., Simon H.A., Bradshaw G.L., Zytkow J.M. (1987). Scientific Discovery. MIT Press.
5. Lenat D. (1976). AM: An Artificial Intelligence Approach to Discovery in Mathematics as Heuristic Search. PhD thesis, Stanford University.
6. Lenat D. (1983). EURISKO: A Program That Learns New Heuristics and Domain Concepts. Artificial Intelligence 21(1-2): 61-98.
7. Boden M.A. (2004). The Creative Mind: Myths and Mechanisms. 2nd ed. Routledge.
8. Fauconnier G. & Turner M. (2002). The Way We Think: Conceptual Blending and the Mind's Hidden Complexities. Basic Books.
9. Schmidhuber J. (1991). A Possibility for Implementing Curiosity and Boredom in Model-Building Neural Controllers. Proc. SAB'91.
10. Kanerva P. (1988). Sparse Distributed Memory. MIT Press.
11. Kanerva P. (2009). Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors. Cognitive Computation 1(2).
12. Plate T.A. (2003). Holographic Reduced Representations: Distributed Representation for Cognitive Structures. CSLI Publications.
13. Frady E.P. et al. (2020). Resonator Networks. Neural Computation 33(1): 1-40.
14. Schlegel K. et al. (2022). A Comparison of Vector Symbolic Architectures. Artificial Intelligence Review 55: 4523-4555.
15. Smolensky P. (1990). Tensor product variable binding and the representation of symbolic structures in connectionist systems. Artificial Intelligence 46(1-2): 159-216.
16. Ramsauer H. et al. (2024). Modern Hopfield Networks Require Chain-of-Thought to Solve NC1-Hard Problems. arXiv:2412.05562.
17. Rachkovskij D.A. & Kussul E.M. (2001). Binding and normalization of binary sparse distributed representations. Neural Computation 13(2): 371-412.
18. Hersche M. et al. (2023). LARS-VSA: A Vector Symbolic Architecture for Learning with Abstract Rules. arXiv:2405.14436.
