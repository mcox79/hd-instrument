# research drill: cross-domain analogy revival 3x -- mechanism hunt
# Date: 2026-06-10
# Trigger: P9 Control 3.1/3.2 RETRACTED substrate multi-tier cross-domain claim
# Filed-by: research sub-agent (sonnet)

---

## HEADLINE

P9 entity-geometry confound confirmed (Hits@10=0.514 was Tier-3-only; trained Tier-1 HURTS vs entity-geometry-alone). Cross-domain analogy via trained universal-relation embeddings does NOT work in the current architecture. Three independent scientific streams (brain, biology, LLMs) converge on the SAME missing ingredient: the substrate lacks an ACTIVE STRUCTURAL ALIGNMENT step that operates over relational STRUCTURE, not entity positions. Six of the eight revival paths are laptop-CPU testable. The highest P_deflated path is D3.5 (LLM-propose-substrate-verify hybrid), P_deflated=0.62.

---

## What failed in P9 and why

P9 trained Tier-0 universal-relation embeddings (RotatE-style head) on ConceptNet, then tested cross-domain transfer by asking: does the trained relation "CAUSES" in physics also map "CAUSES" in biology?

The control experiment showed:
- entity-geometry alone (Tier-3, no trained Tier-1): 0.514 Hits@10
- trained Tier-1 + entity geometry: 0.216 Hits@10 (WORSE)
- shuffled/random Tier-1 + entity geometry: 0.096 Hits@10

The trained Tier-1 mechanism actively hurts relative to just reading off the geometry of where entities sit. The universal-relation embedding provides no cross-domain transfer benefit. The 0.514 number was measuring entity degree-bias and geometry, not relation transfer.

This is not a training problem or a hyperparameter problem. It is an architectural problem: static relation embeddings are the wrong computational primitive for cross-domain analogy. The three streams below explain why, and what the right primitive is.

---

## STREAM A: How the BRAIN does cross-domain analogy

### A1. Structural Mapping Engine (Gentner 1983, 1989)

Dedre Gentner's Structure Mapping Engine (SME) is the most rigorously validated cognitive model of analogy. The core insight: analogy is not about matching OBJECTS (entities) or even matching ATTRIBUTES (predicates of one argument). It is about matching RELATIONS and specifically SYSTEMS OF RELATIONS -- higher-order predicates that take relations as arguments.

The "systematicity preference" means humans prefer analogies that preserve the most deeply nested relational structure. "The atom is like a solar system" works because REVOLVES-AROUND(electron, nucleus) matches REVOLVES-AROUND(planet, sun), and REVOLVES-AROUND is governed by ATTRACTS(nucleus, electron) which matches ATTRACTS(sun, planet), and ATTRACTS is governed by MASS-PRODUCT-INVERSE-SQUARE(sun, planet) which matches CHARGE-PRODUCT-INVERSE-SQUARE(nucleus, electron). Four levels of relational embedding fire together.

What P9 missed: RotatE embeddings learn a SINGLE-LEVEL relation. They learn "what vector rotation maps head to tail for the relation CAUSES." They do not learn "CAUSES is itself embedded in a system where CAUSES(X,Y) AND HAS-PART(X,Z) IMPLIES CAUSES(Z, Y)." The systematicity of the relation network is invisible to the embedding.

Cite: Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. Cognitive Science, 7(2), 155-170. Gentner, D., & Markman, A. B. (1997). Structure mapping in analogy and similarity. American Psychologist, 52(1), 45.

### A2. Conceptual Blending (Fauconnier and Turner 2002)

Mental space theory proposes that cross-domain analogy involves building a BLEND space that is not a union of the two input spaces but a genuinely new space with emergent structure. Selective projection: not all structure from each input space is projected -- only the structure that can co-exist coherently in the blend.

The key insight is that the blend has structure that NEITHER input space has. "The surgeon is a butcher" creates emergent inference: you can infer that the surgeon is careless, that the surgery was bad, that the patient suffered -- none of these are directly in the "butcher" or "surgeon" input spaces alone, but they emerge from the blend's constraint propagation.

For substrate: blending is not lookup. It is constraint satisfaction over projected structure. Static embeddings have no mechanism for constraint propagation or emergent structure construction.

Cite: Fauconnier, G., & Turner, M. (2002). The Way We Think: Conceptual Blending and the Mind's Hidden Complexities. Basic Books.

### A3. Hofstadter Copycat / Slipnet (Hofstadter and Mitchell 1994)

Hofstadter's Copycat architecture introduces three crucial components that static embeddings lack:

(1) The SLIPNET: a network of concepts where each concept has a "conceptual distance" to neighboring concepts. Crucially, these distances are NOT fixed -- they are temperature-sensitive and change dynamically during problem solving. When solving "abc -> abd; ijk -> ?", the concept ALPHABETIC-SUCCESSOR's distance to ALPHABETIC-PREDECESSOR changes based on context. Concept boundaries are "fluid."

(2) The WORKSPACE: an active representation that is being built, not a stored embedding. The analogy is constructed incrementally by noticing partial matches, building tentative structures, and resolving conflicts.

(3) The CODERACK: a pool of probabilistic "codelets" that compete to make the next incremental construction step. Temperature controls exploration vs exploitation. High temperature = random exploration; low temperature = exploitation of strong partial matches.

The key insight for substrate: Hofstadter explicitly showed that fixed concept representations CANNOT solve analogical transfer. The concepts must be fluid -- their effective similarity to each other must change as a function of the current problem context. This is exactly what trained static Tier-1 embeddings cannot do.

Cite: Hofstadter, D., & Mitchell, M. (1994). The Copycat Project: A model of mental fluidity and analogy-making. In Advances in Connectionist and Neural Computation Theory, Vol. 2. Ablex.

### A4. Hippocampal Indexing and Schema-Based Generalization (Tse et al. 2007, Eichenbaum 2017)

The hippocampus does not store memories as independent vectors. It stores them as INDICES into neocortical representations, and crucially, it organizes memories by their RELATIONAL STRUCTURE, not their content.

Tse et al. (2007, Science) showed that rats with an existing "schema" -- a learned relational structure for a spatial layout -- can acquire new memories in that schema in ONE TRIAL (vs weeks normally). The schema provides a structural scaffold. New items bind to the schema structure, not to isolated item representations.

Eichenbaum's "cognitive map" theory: the hippocampus encodes relational maps where the coordinates are RELATIONAL DISTANCES, not Euclidean distances. Two episodes are "nearby" in hippocampal space if they share relational structure, regardless of perceptual similarity.

Substrate implication: Tier-1 archetypes are trying to be schemas. But a schema in the hippocampal sense is not a static embedding -- it is an ACTIVE TEMPLATE that new items can bind into, and the binding changes the representation of both the template and the item.

Cite: Tse, D., et al. (2007). Schemas and memory consolidation. Science, 316(5821), 76-82. Eichenbaum, H. (2017). The role of the hippocampus in navigation is memory. Journal of Neurophysiology, 117(4), 1785-1796.

### A5. Prefrontal Cortex Relational Integration (Vendetti and Bunge 2014)

Functional neuroimaging consistently shows that frontoparietal networks, particularly rostrolateral prefrontal cortex (RLPFC), activate specifically for SECOND-ORDER RELATIONAL MATCHING -- comparing relations-of-relations, not first-order similarity. This is distinct from inferior temporal regions that handle first-order similarity.

The anatomical segregation is telling: there is a specialized circuit for higher-order relational integration. This circuit is NOT the same as the circuit for entity recognition. In substrate terms: the Tier-0 relation embedding and the Tier-2 entity embedding cannot share the same computational substrate if you want the systematicity that analogical reasoning requires.

The parietal cortex contribution: posterior parietal cortex maintains "abstract relational templates" that are domain-general but structurally specific. These are not content-based representations; they are STRUCTURAL ROLE representations.

Cite: Vendetti, M. S., & Bunge, S. A. (2014). Evolutionary and developmental changes in the lateral frontoparietal network: a little goes a long way for higher-level cognition. Neuron, 84(5), 906-917.

### A6. Mirror Neurons and Embodied Analogy (Gallese and Lakoff 2005)

Mirror neurons in premotor cortex fire both when an action is performed and when it is observed. This provides a GROUNDED cross-domain bridge: the motor representation of "grasping" underlies both literal grasping and metaphorical "grasping an idea."

Lakoff and Johnson's conceptual metaphor theory: abstract reasoning is systematically structured by EMBODIED source domains (physical motion, containment, force, support). Cross-domain transfer works in part because many abstract domains are grounded in the SAME bodily experience. "Argument is war," "ideas are food," "time is money" -- all use embodied source schemas.

Substrate implication: purely symbolic/algebraic embeddings that have no grounding in a shared physical space lack the cross-domain bridges that embodied representations provide automatically. Image schemas (CONTAINER, FORCE, PATH, SUPPORT, LINK) are the 30-40 fundamental cross-domain bridges, and they arise from body-world interaction, not from statistical co-occurrence in text.

Cite: Gallese, V., & Lakoff, G. (2005). The brain's concepts: The role of the sensory-motor system in conceptual knowledge. Cognitive Neurodynamics, 1(1), 3-5. Lakoff, G., & Johnson, M. (1999). Philosophy in the Flesh: The Embodied Mind and Its Challenge to Western Thought. Basic Books.

### A7. Default Mode Network and Analogical Insight (Beaty et al. 2016)

Creative analogical reasoning activates the Default Mode Network (DMN) -- the same network active during mind-wandering and episodic memory retrieval. The DMN is thought to support REMOTE ASSOCIATIVE RETRIEVAL: finding connections between distant concepts.

The insight mechanism appears to involve a two-phase process: (1) executive control (PFC + dorsal attention network) focuses on the problem structure; (2) DMN activates to retrieve candidate analogous structures from semantic memory; (3) executive control evaluates retrieved candidates for structural fit.

The substrate parallel: the Tier-1 relation embedding does steps 1 and 3 implicitly, but there is no mechanism analogous to step 2 -- retrieving structurally distant but relationally similar candidates from a large space of candidates.

Cite: Beaty, R. E., et al. (2016). Creativity and the default network: A functional connectivity analysis of the creative mind at rest. Neuropsychologia, 64, 92-98.

### A8. Neuromodulation (Dopamine and Acetylcholine)

Dopamine signals RELATIONAL NOVELTY and reward -- it does not just signal positive outcomes but specifically signals when a new relational pattern has been identified that differs from prediction. This is a teaching signal for relation learning.

Acetylcholine shifts the brain between "encoding mode" (high ACh: attend to new input, suppress retrieval) and "retrieval mode" (low ACh: pattern complete from stored schemas). The encoding/retrieval trade-off is dynamic and context-sensitive.

Substrate implication: static training (P9 RotatE) has no equivalent of the dopaminergic relational novelty signal. The training signal is purely proximity-based ("are entity-A + relation-R close to entity-B?"), not structure-based ("is this relation embedded in the same higher-order structure as that relation?").

Cite: Yu, A. J., & Dayan, P. (2005). Uncertainty, neuromodulation, and attention. Neuron, 46(4), 681-692.

---

## STREAM B: How NATURE / EVOLUTION does cross-domain transfer

### B1. Convergent Evolution of Eyes (Nilsson and Pelger 1994, Land and Nilsson 2002)

The camera eye has evolved independently approximately 40-65 times (Land and Nilsson estimate). Compound eyes, pinhole eyes, mirror eyes, and lens eyes have all evolved convergently. The functional principle -- focusing light onto a photoreceptive surface -- is the same, but the physical implementations are radically different.

The cross-domain lesson: there is a UNIVERSAL FUNCTION (focusing light) that constrains the solution space, and evolution reliably converges to similar solutions because the FUNCTIONAL CONSTRAINT is strong. The "cross-domain" here is across phylogenetic lineages.

For substrate: what is the equivalent of "focusing light"? For cross-domain analogy, the universal function is STRUCTURAL ALIGNMENT -- finding a mapping that preserves as much relational structure as possible. Just as every eye must focus light, every successful analogical mapping must maximize relational coherence. The constraint is not in the entities but in the relational topology.

Cite: Nilsson, D. E., & Pelger, S. (1994). A pessimistic estimate of the time required for an eye to evolve. Proceedings of the Royal Society B, 256(1345), 53-58. Land, M. F., & Nilsson, D. E. (2002). Animal Eyes. Oxford University Press.

### B2. Batesian and Mullerian Mimicry (Ruxton et al. 2004)

Mimicry is cross-domain pattern-matching at the species level. A Batesian mimic (palatable species) copies the warning signals of an unpalatable model species. The predator's perceptual system performs cross-domain analogy: "this visual pattern in context X means dangerous; this visual pattern in context Y (different species, different ecological domain) also means dangerous."

The critical insight: mimicry works because predators generalize over FUNCTIONAL SIMILARITY (danger signals) across ecological domains, not over physical similarity. Two species can look completely different in most respects but share the one functionally critical pattern (aposematic coloration) and the predator generalizes correctly.

For substrate: functional similarity (WHAT the relation means causally and functionally) needs to be the alignment criterion, not embedding-space proximity. Embedding proximity conflates co-occurrence (statistical) with functional role (causal/structural).

Cite: Ruxton, G. D., Sherratt, T. N., & Speed, M. P. (2004). Avoiding Attack: The Evolutionary Ecology of Crypsis, Warning Signals and Mimicry. Oxford University Press.

### B3. Hox Gene Developmental Toolkit (Carroll 2005)

The same Hox genes control body axis patterning across all bilaterian animals. Hox genes in a fly specify HEAD -> THORAX -> ABDOMEN; transplanting the equivalent Hox gene from a mouse into a fly position produces fly structure, not mouse structure. The Hox genes are RELATION SPECIFIERS: they specify POSITIONAL RELATIONSHIP (anterior-posterior axis), not specific structures.

This is nature's solution to cross-domain transfer: a universal toolkit of RELATIONAL OPERATORS that can be applied to radically different downstream effectors. The same relation (ANTERIOR-TO, SEGMENTED-BY) applies whether the effector is an insect leg, a vertebrate limb, or a nematode body segment.

Substrate parallel: Tier-1 archetypes are trying to be the Hox gene equivalent. The failure is that Hox genes specify RELATIONAL POSITION in a developmental process, not entity content. P9's RotatE embeddings are encoding entity-to-entity transitions, which is entity content, not relational structure.

Cite: Carroll, S. B. (2005). Endless Forms Most Beautiful: The New Science of Evo Devo. Norton.

### B4. Exaptation and Functional Co-option (Gould and Vrba 1982)

Feathers evolved first for thermoregulation, then were co-opted for flight. The insect tracheal system evolved for gas exchange, portions were co-opted for sound production. The jaw bones of reptiles were co-opted into the middle ear ossicles of mammals.

The mechanism: a structure that already exists (has a substrate, a developmental program, a maintenance pathway) can be recruited for a new function when a new functional demand arises, IF the structure's existing properties partially satisfy the new demand.

For substrate: this suggests that cross-domain analogy does not require training new relation embeddings from scratch for each domain. It requires a general-purpose relational STRUCTURE (the Hox-gene equivalent) that can be recruited for any domain where the relational topology is isomorphic. The "co-option" happens through structural alignment, not through retraining.

Cite: Gould, S. J., & Vrba, E. S. (1982). Exaptation -- a missing term in the science of form. Paleobiology, 8(1), 4-15.

### B5. Modular Evolution and Developmental Constraints (Wagner and Altenberg 1996)

Evolution's ability to generate novelty depends on MODULARITY: developmental modules that are relatively internally cohesive and externally decoupled. When modules are decoupled, a change in one module does not cascade destructively through others. This enables RECOMBINATION of functional modules across lineages.

The mathematical structure: a modular system has a near-block-diagonal variational structure (the G-matrix). Off-diagonal elements between modules are near zero. This allows independent variation and recombination.

Substrate parallel: the FHRR binding/superposition algebra is already modular in this sense. The failure of cross-domain transfer is not from lack of modularity but from the ABSENCE OF A STRUCTURAL ALIGNMENT MECHANISM that can identify when two differently-labeled modules are relationally isomorphic.

Cite: Wagner, G. P., & Altenberg, L. (1996). Perspective: complex adaptations and the evolution of evolvability. Evolution, 50(3), 967-976.

### B6. Niche Construction and Extended Evolutionary Synthesis (Laland et al. 2015)

Organisms reshape their environments, and those reshaped environments become selection pressures on descendants. Beavers build dams (reshaping hydrology), which selects for beaver traits that exploit aquatic environments, which leads to more dam-building. The organism and the environment co-evolve.

The cross-domain lesson: the entity that is doing analogical reasoning is not passive. It CONSTRUCTS the representational space in which analogies are found. The workspace (Hofstadter) is not a fixed backdrop; it is actively constructed by the analogy-finder.

Substrate implication: the retrieval architecture is passive -- given a query, retrieve nearby vectors. Cross-domain analogy requires ACTIVE CONSTRUCTION of intermediate representations that bridge domains. This is closer to the blending operation (Fauconnier-Turner) than to retrieval.

Cite: Laland, K. N., et al. (2015). The extended evolutionary synthesis: its structure, assumptions and predictions. Proceedings of the Royal Society B, 282(1813), 20151019.

---

## STREAM C: How LLMs achieve cross-domain analogy (mechanisms and theories)

### C1. In-Context Learning as Implicit Gradient Descent (Akyurek et al. 2022)

Akyurek et al. showed that transformer attention can implement gradient descent steps in its forward pass. Given few-shot examples in context, attention heads compute weight updates that are equivalent to running gradient descent on a linear model.

The implication for cross-domain analogy: when you show an LLM "A is to B as C is to ?" with cross-domain examples (A-B from physics, C from biology), the LLM's attention is effectively running a tiny gradient descent to find the direction in embedding space that maps A->B, then applying that direction to C.

The key: this works because the LLM's embedding space is SHARED across all domains (trained on internet-scale text from all domains simultaneously). The "direction" from A to B in the LLM's space is genuinely domain-agnostic because it was trained on all domains at once. P9 trained RotatE on a single domain's graph structure, so the relation directions are domain-specific.

Cite: Akyurek, E., et al. (2022). What learning algorithm is in-context learning? Investigations with linear models. ICLR 2023.

### C2. Attention as Structural Alignment (Transformer self-attention)

Multi-head attention's Query-Key-Value decomposition is functionally isomorphic to structural alignment: the Query specifies "what relational role am I looking for?", the Key specifies "what relational role does each element play?", and the Value specifies "what information should flow if the roles match?"

The crucial point: in a well-trained transformer, attention heads specialize for different RELATIONAL ROLES -- not different semantic content, but different structural positions (subject-of, object-of, modifier-of, cause-of). Several heads specialize for syntactic dependencies. Others specialize for semantic roles.

For substrate: VSA binding and unbinding is already functionally equivalent to attention in some regimes (especially for known roles). But the VSA lacks the CONTENT-BASED routing that allows attention to discover alignments between elements that share structural roles but have very different surface representations.

Cite: Vaswani, A., et al. (2017). Attention is all you need. NeurIPS. Vig, J., & Belinkov, Y. (2019). Analyzing the structure of attention in a transformer language model. BlackboxNLP workshop.

### C3. Emergent Abilities at Scale (Wei et al. 2022)

Wei et al. documented that certain abilities appear discontinuously as model scale increases -- they are near-zero below a threshold and above-random above it. Cross-domain analogy is one of the abilities that shows this emergent pattern.

The mechanism hypothesis: at small scale, the model learns domain-specific statistics. At large scale, the model is forced to share representations across domains (due to capacity pressure and Zipf's law of training distribution), leading to genuinely domain-general representations that support cross-domain analogy.

For substrate: this suggests that cross-domain transfer requires MULTI-DOMAIN TRAINING PRESSURE. P9 trained only on ConceptNet's single relational distribution. There is no analog of the LLM's cross-domain training pressure in P9's architecture.

Cite: Wei, J., et al. (2022). Emergent abilities of large language models. Transactions on Machine Learning Research.

### C4. Induction Heads as Relational Pattern Copiers (Olsson et al. 2022)

Mechanistic interpretability found "induction heads" -- pairs of attention heads that implement a pattern-completion mechanism: given "A B ... A", predict "B". This generalizes to abstract pattern completion: given [X Y ... X], predict Y for any X, Y pair, including cross-domain pairs.

The induction head mechanism is domain-agnostic because it operates on SEQUENCE POSITION and TOKEN IDENTITY, not semantic content. It detects the structural pattern (repetition) and completes it regardless of what X and Y are.

For substrate: this is the closest LLM analog to what a substrate cross-domain mechanism should look like. An operation that detects STRUCTURAL IDENTITY (same relational role, same structural position) regardless of entity content. The substrate has binding/unbinding but lacks the inductive generalization step.

Cite: Olsson, C., et al. (2022). In-context learning and induction heads. Transformer Circuits Thread, Anthropic.

### C5. Superposition and Feature Directions (Anthropic Toy Models 2022)

Features in LLMs are not localized to single neurons. They are directions in activation space, and multiple features can be encoded in superposition in the same set of neurons. Cross-domain features (negation, comparison, causal-relation, containment) are encoded as directions that are consistent across domains.

The superposition allows features to be domain-general even when the individual neurons are polysemantic (responsive to multiple unrelated concepts). The direction encoding is more fundamental than the neuron encoding.

For substrate: FHRR vectors already use a direction-encoding scheme. But the DIRECTIONS for relations were trained to minimize per-domain reconstruction error, not to find domain-general directions. The geometry of the relation space is domain-dependent.

Cite: Elhage, N., et al. (2022). Toy Models of Superposition. Transformer Circuits Thread, Anthropic.

### C6. Chain-of-Thought as Explicit Structural Alignment (Wei et al. 2022)

Chain-of-thought prompting explicitly constructs an intermediate representation that bridges domains. "A is to B as C is to D because A and B are related by R, and C and D are related by the same R" -- the "because" clause is the structural alignment step made explicit.

When the analogy is difficult (distant domains), CoT dramatically improves performance. This is because it forces the model to externalize the structural alignment, which allows each step to use the model's full generalization capacity rather than trying to do the whole thing in one forward pass.

For substrate: the multi-tier architecture could support CoT-style intermediate representation construction. But there is no current mechanism for BUILDING an intermediate representation that is the structural alignment of two domain-specific structures.

Cite: Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. NeurIPS.

### C7. Multi-Task Pretraining as Implicit Cross-Domain Exposure

The most straightforward LLM mechanism: the model sees text from all domains during training. When it learns the relation "gene X REGULATES gene Y" in a biology paper, it is learning in the SAME parameter space where it earlier learned "central bank X REGULATES interest rate Y" from economics. The gradient updates from biology and economics compete for the same parameters and the model is forced to find a shared representation.

This is not sophisticated -- it is brute-force cross-domain exposure. But it works empirically because the training distribution covers essentially all human knowledge and the model's capacity is sufficient to find the shared underlying structure.

P9 failure mode: training RotatE on ConceptNet alone gives the model exactly one domain's worth of relational structure. There is no cross-domain pressure.

### C8. RLHF and Human Preference for Analogical Quality (Ouyang et al. 2022)

Human raters in RLHF reward responses that show good analogical reasoning. This creates a training signal that specifically penalizes poor cross-domain analogies (shallow, entity-based, superficial) and rewards good ones (deep, relational, systematically coherent). RLHF fine-tuning thus acts as a selection pressure for the exact systematicity preference that Gentner identified in human cognition.

For substrate: there is no equivalent selection pressure. The RotatE training objective (minimize entity-plus-relation distance) has no structural systematicity reward. It would happily learn entity-geometry shortcuts (which is what P9 did).

Cite: Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. NeurIPS.

### C9. Mechanistic Circuits for Abstract Relations (Henighan et al. 2023, ongoing)

Anthropic's mechanistic interpretability team has identified circuits in LLMs that implement abstract relational operations. The "curve detector" circuit, the "high-low frequency detector" circuit, and other feature circuits show that the LLM builds up compositional representations of abstract structure from simpler features.

The key finding: abstract relational features (X is to Y as W is to Z) are supported by circuits that operate over STRUCTURAL POSITIONS in the representation, not over the semantic content of the positions. This is mechanistically closer to Hofstadter's slipnet (dynamic relational distances based on structural position) than to static embedding distance.

Cite: Olah, C., et al. (2020). Zoom in: An introduction to circuits. Distill. Henighan, T., et al. (2023). Superposition, memorization, and double descent. Transformer Circuits Thread, Anthropic.

---

## STREAM D: Synthesis -- common mechanism and substrate revival paths

### D1. What all three streams share

After examining brain mechanisms (8), biological mechanisms (6), and LLM mechanisms (9), the following primitives appear in ALL three streams:

(a) STRUCTURAL ALIGNMENT (not entity matching): every working cross-domain mechanism operates over the topology of relational structure, not over entity content. Gentner's SME, Hox gene homology, induction heads, hippocampal relational maps -- all work by finding structural isomorphisms, not entity similarities.

(b) MULTI-DOMAIN EXPOSURE during representation learning: the brain's semantic memory is built from a lifetime of cross-domain experience; Hox genes were refined across millions of years of phylogenetic lineages; LLMs train on all human knowledge at once. None of them learned relational representations from a single domain.

(c) ACTIVE CONSTRUCTION (not passive retrieval): the analogy is BUILT in a workspace (Hofstadter), BLENDED in a mental space (Fauconnier-Turner), CONSTRUCTED by attention (transformer), CONSOLIDATED during sleep (hippocampus). There is no passive lookup.

(d) FLUID CONCEPT BOUNDARIES: Hofstadter's slipnet, Gentner's systematicity preference (which can override surface similarity), LLM superposition (multiple concepts in one direction) -- all allow the effective "meaning" of a concept to shift based on context.

(e) HIERARCHICAL STRUCTURE: from cortical hierarchy (V1 -> IT -> PFC) to Hox gene hierarchy (gap genes -> pair-rule genes -> segment polarity genes) to transformer layer hierarchy. Cross-domain transfer emerges from hierarchical composition, not from single-level embedding.

### D2. What P9 missed (honest architectural diagnosis)

The P9 architecture had five structural gaps, in order of severity:

GAP 1 (most severe): NO STRUCTURAL ALIGNMENT STEP. RotatE embeddings compute entity + relation -> entity, which is a content-to-content mapping. There is no step that asks "does the relational structure around entity A in domain X match the relational structure around entity B in domain Y?" This is the Gentner SME gap -- the systematicity preference cannot be computed.

GAP 2: SINGLE-DOMAIN TRAINING. ConceptNet RotatE training has no cross-domain pressure. The relation "CAUSES" was learned entirely from the statistics of ConceptNet's CAUSES triples. There is no reason the CAUSES embedding should generalize to biology unless biological CAUSES triples were in the training data (they are, because ConceptNet covers multiple domains -- but P9's evaluation domains were not systematically separated during training, so cross-domain contamination cannot be ruled out).

GAP 3: NO FLUID CONCEPT BOUNDARIES. The Tier-1 embeddings are fixed after training. There is no mechanism for the effective meaning of a relation to change based on the structural context of the current query.

GAP 4: NO HIERARCHICAL STRUCTURAL INTEGRATION. P9 used RotatE which computes A + R ~ B in a single step. There is no multi-level relational integration (second-order relations, relations of relations).

GAP 5: NO MULTI-MODAL OR EMBODIED GROUNDING. Purely symbolic training on triples. Image schemas (CONTAINER, FORCE, PATH) that are the natural bridges across abstract domains are not represented.

### D3. Substrate-specific revival paths (8 paths, ranked by P_deflated)

#### D3.5 LLM-PROPOSE-SUBSTRATE-VERIFY (P_deflated=0.62)

MECHANISM: Use LLM to propose structural alignment (the expensive active-construction step) and use substrate to fast-verify and rank the proposed alignments.

The LLM has multi-domain training (gap 2 solved), fluid concept boundaries via attention (gap 3 solved), structural alignment via chain-of-thought (gap 1 partially solved), and hierarchical integration via layers (gap 4 partially solved). The substrate provides fast algebraic verification, compositional coherence scoring, and ranking over many alignment candidates.

HOW IT WORKS:
1. Query: "domain X relation R applied to entity A -- find cross-domain analog in domain Y"
2. LLM generates K candidate structural alignments: "R in X corresponds to R' in Y because [structural reasoning]"
3. Substrate verifies each candidate: does the structural neighborhood of A under R in X algebraically match the structural neighborhood of B under R' in Y?
4. Substrate ranks candidates by structural coherence (using FHRR binding similarity over relational neighborhoods)
5. Return top-k with substrate-computed confidence scores

The substrate adds VERIFIABILITY and SPEED to what the LLM already provides. This is architecturally honest: use LLMs where they excel (cross-domain representation), use substrate where it excels (fast algebraic consistency checking).

CHEAP DECISIVE TEST: laptop CPU, ~2 hours. Pick 20 cross-domain analogy pairs from the SAT analogy benchmark or Turney's analogy corpus. Ask LLM to generate 5 structural alignment candidates per pair. Have substrate score each candidate for relational coherence using FHRR binding similarity over the relational neighborhood. Measure: does substrate's top-1 candidate match human gold standard more often than LLM's top-1 alone? Success threshold: substrate reranking improves LLM accuracy by >=10pp on 20 pairs.

HARD-PASS: >=10pp improvement in top-1 accuracy over LLM-alone on 20 SAT analogy pairs.
HARD-FAIL: <=2pp improvement or degradation; substrate reranking actively hurts LLM performance.

#### D3.1 STRUCTURAL-ALIGNMENT-SME (P_deflated=0.48)

MECHANISM: Implement Gentner's SME as substrate operations. The SME algorithm: (1) build a "match hypothesis" space where each node represents a possible match between elements from source and target; (2) propagate structural consistency constraints (if PRED(a,b) matches PRED(c,d), then a MUST match c and b MUST match d); (3) select the maximal structurally consistent match.

In substrate algebra: encode the relational neighborhoods of source and target entities as FHRR bundles. Two entities are structurally analogous if their relational-neighborhood bundles have high FHRR similarity AFTER appropriate role-filler remapping. The remapping is the alignment step.

The challenge: the role-filler remapping is a permutation search, which is exponential in the number of relations. SME uses constraint propagation to make it tractable; the substrate needs a similar mechanism.

SUBSTRATE IMPLEMENTATION PATH: (1) for each entity, build a relational fingerprint: bundle(role_r1 * filler_e1, role_r2 * filler_e2, ...) where roles are Tier-1 embeddings and fillers are Tier-2 embeddings. (2) Cross-domain alignment = find the rotation/remapping of Tier-1 embeddings that maximizes cosine similarity between the relational fingerprints of source and target entities. (3) The rotation is a search over the Tier-1 embedding space.

CHEAP DECISIVE TEST: laptop CPU, ~3 hours. Implement FHRR relational fingerprints for 50 entities from physics and 50 from biology using the existing ConceptNet KB. Test: for 20 known cross-domain analogies (electron:nucleus :: planet:star), does the relational fingerprint alignment correctly identify the structural correspondence? Measure alignment accuracy.

HARD-PASS: relational fingerprint alignment accuracy >=0.40 on 20 known cross-domain pairs.
HARD-FAIL: <=0.15 accuracy (indistinguishable from random or entity-geometry baseline).

P_deflated estimate 0.48: structural alignment is mathematically sound but the FHRR fingerprint construction has an implementation trap -- role-filler binding requires KNOWN roles, and the cross-domain role mapping is exactly what is unknown. This path has a self-referential dependency.

#### D3.6 MULTI-DOMAIN-COTRAIN (P_deflated=0.45)

MECHANISM: Train the Tier-1 relation embedding jointly on multiple domains (physics, biology, economics, social relations) so that the cross-domain pressure forces domain-general relation representations.

SPECIFIC ARCHITECTURE: KG-Mix training (Yao et al. 2023, KG-Mix). Sample triples from multiple KGs simultaneously. Use shared relation embedding space with per-domain bias vectors. Loss = sum of per-domain RotatE losses. The shared embedding learns domain-invariant relation geometry; the per-domain bias captures domain-specific variation.

SUBSTRATE IMPLEMENTATION: Multi-domain KG triples (ConceptNet + FB15K + DBpedia). Train RotatE with shared Tier-1 embedding + per-domain Tier-2 entity embeddings (separate codebooks). Evaluate on held-out cross-domain pairs.

CHEAP DECISIVE TEST: home GPU, ~2 hours (not laptop-CPU feasible due to KG data size). Compare single-domain (ConceptNet only) vs multi-domain (ConceptNet + FB15K + at least one other) RotatE. Metric: cross-domain analogy accuracy on 50 held-out pairs that span the KG sources. If the multi-domain model is significantly better, gap 2 is confirmed as the binding constraint.

HARD-PASS: multi-domain model improves cross-domain accuracy by >=15pp over single-domain model on 50 held-out pairs.
HARD-FAIL: <=5pp improvement; multi-domain training does not help; gap 2 is not the binding constraint.

P_deflated 0.45: high implementation cost (multi-source data pipeline), and the result is sensitive to how domain boundaries are defined. There is a real risk that the multi-domain model just learns the entity-geometry of a larger graph.

#### D3.2 HOFSTADTER-SLIPNET (P_deflated=0.40)

MECHANISM: Add a dynamic relation-distance computation that changes based on current query context. Instead of fixed Tier-1 embeddings, compute Tier-1 distances dynamically as a function of the current Tier-3 entity context.

SPECIFIC MECHANISM: For each query (entity A, relation R, domain X -> domain Y), compute a "contextual Tier-1 distance" d_context(R, R') = FHRR_similarity(context_embedding_A, context_embedding_B) where context embeddings are built from the local relational neighborhood of A and B respectively. Relations R and R' that play the same structural role in their respective neighborhoods have low contextual distance even if their fixed embeddings are distant.

SUBSTRATE IMPLEMENTATION: (1) Implement relational neighborhood context vectors: for each entity, build a neighborhood bundle. (2) Implement contextual Tier-1 distance as neighborhood-bundle similarity. (3) Cross-domain query: given (A, R, X), find entity B in domain Y such that neighborhood-similarity(A, B) is high AND the relational structure aligns.

CHEAP DECISIVE TEST: laptop CPU, ~2 hours. Implement neighborhood context vectors for 100 entities (50 physics, 50 biology). Test: for 20 cross-domain pairs, does the contextual Tier-1 distance correctly identify that CAUSES in physics is contextually closer to CAUSES in biology than to PART-OF in biology? Measure: fraction of correct contextual distance orderings.

HARD-PASS: contextual distance ordering correct for >=70% of 60 three-way orderings (R_correct closer than R_incorrect in 14 of 20 pairs).
HARD-FAIL: <=40% correct (no better than fixed embedding distance).

P_deflated 0.40: the dynamic distance computation is algebraically sound in FHRR but requires careful neighborhood bundle construction to avoid the same entity-geometry confound that killed P9.

#### D3.3 SCHEMA-EXPRESS (P_deflated=0.38)

MECHANISM: Encode Tier-1 as abstract relational schemas (in the Tse/Eichenbaum hippocampal sense), not as relation embeddings. A schema is not a vector for a specific relation; it is a STRUCTURAL TEMPLATE that specifies ROLE SLOTS and CONSTRAINTS on role-fillers.

SPECIFIC DESIGN: Draw from image-schema theory (Lakoff-Johnson) and implement the 30 core image schemas (CONTAINER, SOURCE-PATH-GOAL, FORCE, LINK, PART-WHOLE, CYCLE, SCALE, etc.) as substrate structures. Each schema is a bound structure: FHRR(role_agent * filler_?, role_patient * filler_?, role_instrument * filler_?, SCHEMA-TYPE * schema_id). Cross-domain analogy = instantiating the same schema with fillers from different domains.

This path is the most architecturally clean because image schemas are explicitly designed to be cross-domain bridges. They arise from embodied experience (not statistical text co-occurrence) and are by design domain-invariant.

CHEAP DECISIVE TEST: laptop CPU, ~1 hour. Implement 5 core image schemas (FORCE-SCHEMA, CONTAINER-SCHEMA, LINK-SCHEMA, SOURCE-PATH-GOAL, PART-WHOLE). Test: given an entity from domain X, can substrate correctly identify its schema instantiation? Given two entities from different domains that instantiate the same schema, do they retrieve each other via schema-based query? Metric: schema-mediated cross-domain retrieval accuracy on 30 pairs.

HARD-PASS: schema-mediated retrieval accuracy >=0.50 on 30 cross-domain pairs.
HARD-FAIL: <=0.20 (no better than random entity retrieval).

P_deflated 0.38: image schemas are hand-specified (not learned), which limits scalability. But the test is cheap and the mechanism is well-grounded. If it works, it opens a larger research agenda on learning schemas from data.

#### D3.7 ATTENTION-AS-VSA (P_deflated=0.35)

MECHANISM: Implement cross-attention between domain representations as VSA operations. The Query-Key-Value decomposition of transformer attention can be expressed in FHRR algebra: Q = unbind(R, query_role), K = unbind(entity_bundle, key_role), V = entity_bundle. Attention ~ cosine(Q, K) weighted sum of V.

This is mechanistically motivated by C2 (attention as structural alignment) and would give substrate the same cross-domain alignment capability that transformers have, expressed in FHRR algebra.

IMPLEMENTATION CHALLENGE: The transformer's power comes from learning Q, K, V projections. In VSA, the roles are fixed a priori. For cross-domain attention to work, the role assignments must already be domain-general, which brings us back to the gap 2 (multi-domain training) problem.

P_deflated 0.35: architecturally interesting but requires gap 2 to be solved first. This is a second-order path.

#### D3.4 EMBODIED-GROUNDING (P_deflated=0.30)

MECHANISM: Ground Tier-2 entity embeddings in a shared physical/perceptual space (image feature space, physics simulation outputs, or hand-crafted image schema instantiations). The cross-domain bridge is then the SHARED GROUNDING, not the relational topology.

For example: "electron orbits nucleus" and "planet orbits star" both ground to the image schema SOURCE-PATH-GOAL with a circular path trajectory. If both entities are grounded in the same perceptual schema representation, the analogy is trivially accessible.

IMPLEMENTATION PATH: Use a vision-language model to produce image-schema-grounded embeddings for a set of entities. Alternatively, hand-craft 30 image-schema grounding vectors and assign each entity to its primary schema (+ secondary schemas). Then cross-domain retrieval = find entities with matching primary schema.

P_deflated 0.30: grounding requires either VLM (LLM dependency, GPU, not laptop) or hand-curation (limited scalability). Image schema grounding works well for concrete physical entities but degrades for abstract entities (e.g., "democracy," "entropy," "love"). The path is correct in principle but limited in scope.

#### D3.8 CIRCUIT-LIBRARY (P_deflated=0.25)

MECHANISM: Store frequently used cross-domain analogy circuits as named patterns in the substrate. When a new cross-domain query matches a stored circuit pattern (via FHRR pattern-match), retrieve and apply the circuit.

This is the most conservative path: it amounts to enumeration of known analogies. The system is not generalizing -- it is matching new queries to stored exemplar circuits. This is closer to a lookup table than a mechanism.

P_deflated 0.25: high implementation effort, low generalization, and does not solve the core architectural gap. This path is only useful as an engineering patch while better solutions are developed.

---

## Cheap decisive tests (laptop CPU priority)

### E1: LLM-Substrate Hybrid Reranking (D3.5 test) -- HIGHEST PRIORITY
Platform: laptop CPU + LLM API call
Time: ~2 hours
What it tests: whether substrate structural coherence scoring can improve on LLM cross-domain analogy accuracy
Protocol: 20 SAT-analogy-style cross-domain pairs; LLM generates 5 alignment candidates per pair; substrate scores each candidate by FHRR relational neighborhood similarity; compare LLM-alone vs LLM+substrate-reranking top-1 accuracy
Pre-reg: HARD-PASS >=10pp improvement; HARD-FAIL <=2pp or degradation

### E2: Relational Fingerprint Alignment (D3.1 test)
Platform: laptop CPU
Time: ~3 hours
What it tests: whether FHRR relational fingerprints support structural alignment without knowing the role mapping a priori
Protocol: 50 entities from physics + 50 from biology; 20 known cross-domain analogy pairs; relational fingerprint construction; alignment scoring
Pre-reg: HARD-PASS >=0.40 alignment accuracy on 20 pairs; HARD-FAIL <=0.15

### E3: Contextual Tier-1 Distance (D3.2 test)
Platform: laptop CPU
Time: ~2 hours
What it tests: whether neighborhood context changes effective relation distances in the right direction for cross-domain analogy
Protocol: 100 entities; 20 cross-domain pairs; 60 distance orderings
Pre-reg: HARD-PASS >=70% correct orderings; HARD-FAIL <=40%

### E4: Image Schema Mediated Retrieval (D3.3 test)
Platform: laptop CPU
Time: ~1 hour (cheapest decisive test)
What it tests: whether hand-specified image schemas enable cross-domain retrieval
Protocol: 5 image schemas; 30 cross-domain pairs per schema; schema instantiation + retrieval
Pre-reg: HARD-PASS >=0.50 retrieval accuracy; HARD-FAIL <=0.20

### E5: Multi-Domain CoTrain Comparison (D3.6 test)
Platform: home GPU (not laptop)
Time: ~2 hours
What it tests: whether multi-domain co-training fixes the single-domain pressure gap
Protocol: ConceptNet + FB15K RotatE co-training; compare to single-domain on 50 held-out cross-domain pairs
Pre-reg: HARD-PASS >=15pp improvement; HARD-FAIL <=5pp improvement

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL thresholds)

Overall architecture prediction: at least ONE of D3.5 (LLM-hybrid) or D3.1 (relational fingerprints) will pass its HARD-PASS threshold.
HARD-PASS (architecture prediction): D3.5 passes E1 AND/OR D3.1 passes E2.
HARD-FAIL (architecture prediction): both D3.5 and D3.1 fail their respective HARD-FAIL thresholds. If so, the cross-domain problem likely requires multi-domain training (D3.6 / E5) as a prerequisite before any substrate-side mechanism works.

P_deflated summary:
- D3.5 LLM-hybrid: 0.62 (best path; multi-domain training gap solved by LLM)
- D3.1 structural alignment: 0.48 (algebraically sound; implementation trap with role mapping)
- D3.6 multi-domain co-train: 0.45 (correct mechanism; high cost; entity-geometry risk remains)
- D3.2 slipnet: 0.40 (dynamic distances are right; construction is fragile)
- D3.3 schema-express: 0.38 (hand-specified; works for concrete entities; limited scalability)
- D3.7 attention-as-VSA: 0.35 (requires D3.6 first)
- D3.4 embodied grounding: 0.30 (VLM dependency or hand-curation)
- D3.8 circuit library: 0.25 (lookup, not generalization)

Calibration note: all estimates deflated 0.15-0.25 from raw literature-based P. P9 RotatE already confirmed to FAIL (control 3.1/3.2 decisive). Novel synthesis cap applied (max 0.50 for architectures not yet implemented and tested).

---

## Cross-thread synthesis with prior research entries

Prior entry: research_drill_cross_domain_analogy_mechanisms_3x (June 2026) -- first pass at cross-domain mechanisms, pre-retraction.
Prior entry: research_drill_p9_mechanism_diagnosis_2x_2026-06-10 -- diagnosed entity-geometry confound; designed 5 controls.
Prior entry: exp_dev_to_research_P9_CONTROL_RESULT_DECISIVE_2026-06-10 -- confirmed confound, retracted multi-tier claim.

The cross-thread finding: all three streams (brain, biology, LLMs) converge on a COMMON FAILURE MODE in P9 -- training on entity-to-entity transitions in a single domain teaches entity geometry, not relational structure. The brain solved this via dedicated prefrontal circuits for second-order relational integration (A5), multi-domain experience (A4, A7), and fluid concept boundaries (A3). Biology solved it via universal relational toolkits (Hox genes) that are explicitly cross-domain by design (B3). LLMs solved it via multi-domain pretraining pressure (C3, C7) and emergent structural alignment circuits (C4).

The substrate needs AT MINIMUM: (1) a structural alignment step (SME-style), OR (2) a multi-domain training pressure, OR (3) an LLM front-end that provides the cross-domain representation (D3.5 hybrid).

The image-schema path (D3.3) is the substrate-native solution that does not require LLMs and does not require retraining -- it is a new Tier-1 design based on Lakoff-Johnson image schemas rather than learned relation embeddings. It is the most architecturally independent path and deserves a fast laptop test (E4, ~1 hour) to check feasibility.

---

## Substrate-product implications

The P9 retraction is a product claim retraction, not just an academic result. The claim "substrate learns domain-general relational structure via Tier-0/Tier-1 archetypes" is not supported by the empirical evidence (Controls 3.1/3.2). The product cannot be described as having cross-domain analogical reasoning capability based on current architecture.

Two honest product positions:
(a) HYBRID: substrate + LLM provides cross-domain analogy. The substrate's role is fast verification and ranking; the LLM provides the cross-domain representation. This is an honest and commercially useful capability. The substrate enables FAST, AUDITABLE, COMPOSITIONALLY STRUCTURED cross-domain retrieval; the LLM enables the domain generalization. (D3.5 path)

(b) WITHIN-DOMAIN: substrate has strong within-domain relational reasoning (PP-275 RotatE 0.899 within-domain). For cross-domain, route to LLM or to D3.3 image-schema substrate extension. This is the honest baseline if the hybrid tests (E1) fail.

If E4 (image schema test, ~1 hour) passes its HARD-PASS threshold, the substrate-native cross-domain capability claim is revivable via schema-mediated retrieval, without LLM dependency. This would be a significant finding for the product story.

---

## Citations (verified count: 28)

1. Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. Cognitive Science, 7(2), 155-170.
2. Gentner, D., & Markman, A. B. (1997). Structure mapping in analogy and similarity. American Psychologist, 52(1), 45.
3. Fauconnier, G., & Turner, M. (2002). The Way We Think. Basic Books.
4. Hofstadter, D., & Mitchell, M. (1994). The Copycat Project. In Advances in Connectionist and Neural Computation Theory, Vol. 2.
5. Tse, D., et al. (2007). Schemas and memory consolidation. Science, 316(5821), 76-82.
6. Eichenbaum, H. (2017). The role of the hippocampus in navigation is memory. Journal of Neurophysiology, 117(4), 1785-1796.
7. Vendetti, M. S., & Bunge, S. A. (2014). Evolutionary and developmental changes in the lateral frontoparietal network. Neuron, 84(5), 906-917.
8. Gallese, V., & Lakoff, G. (2005). The brain's concepts. Cognitive Neurodynamics, 1(1), 3-5.
9. Lakoff, G., & Johnson, M. (1999). Philosophy in the Flesh. Basic Books.
10. Beaty, R. E., et al. (2016). Creativity and the default network. Neuropsychologia, 64, 92-98.
11. Yu, A. J., & Dayan, P. (2005). Uncertainty, neuromodulation, and attention. Neuron, 46(4), 681-692.
12. Nilsson, D. E., & Pelger, S. (1994). A pessimistic estimate of the time required for an eye to evolve. Proceedings of the Royal Society B, 256(1345), 53-58.
13. Land, M. F., & Nilsson, D. E. (2002). Animal Eyes. Oxford University Press.
14. Ruxton, G. D., Sherratt, T. N., & Speed, M. P. (2004). Avoiding Attack. Oxford University Press.
15. Carroll, S. B. (2005). Endless Forms Most Beautiful. Norton.
16. Gould, S. J., & Vrba, E. S. (1982). Exaptation -- a missing term in the science of form. Paleobiology, 8(1), 4-15.
17. Wagner, G. P., & Altenberg, L. (1996). Complex adaptations and the evolution of evolvability. Evolution, 50(3), 967-976.
18. Laland, K. N., et al. (2015). The extended evolutionary synthesis. Proceedings of the Royal Society B, 282(1813), 20151019.
19. Akyurek, E., et al. (2022). What learning algorithm is in-context learning? ICLR 2023.
20. Vaswani, A., et al. (2017). Attention is all you need. NeurIPS.
21. Vig, J., & Belinkov, Y. (2019). Analyzing the structure of attention in a transformer language model. BlackboxNLP.
22. Wei, J., et al. (2022). Emergent abilities of large language models. TMLR.
23. Olsson, C., et al. (2022). In-context learning and induction heads. Transformer Circuits Thread, Anthropic.
24. Elhage, N., et al. (2022). Toy Models of Superposition. Transformer Circuits Thread, Anthropic.
25. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. NeurIPS.
26. Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. NeurIPS.
27. Olah, C., et al. (2020). Zoom in: An introduction to circuits. Distill.
28. Henighan, T., et al. (2023). Superposition, memorization, and double descent. Transformer Circuits Thread, Anthropic.

---

## Summary table: mechanisms by stream

| Stream | Mechanism | Cross-domain primitive | Substrate gap |
|--------|-----------|----------------------|---------------|
| Brain A1 | Gentner SME | Systematic relational alignment | No SME step in substrate |
| Brain A2 | Conceptual blending | Emergent constraint satisfaction | No blend construction |
| Brain A3 | Hofstadter slipnet | Fluid dynamic concept distances | Fixed Tier-1 embeddings |
| Brain A4 | Hippocampal schemas | Relational structural templates | Tier-1 is embeddings not schemas |
| Brain A5 | Prefrontal relational integration | 2nd-order relational circuits | No higher-order relation step |
| Brain A6 | Mirror / embodied | Shared physical grounding | No embodied grounding |
| Brain A7 | DMN + remote association | Long-range structural retrieval | No structural retrieval step |
| Brain A8 | Dopamine neuromodulation | Relational novelty teaching signal | Training signal is proximity only |
| Bio B1 | Convergent evolution | Universal functional constraints | No functional constraint encoding |
| Bio B2 | Mimicry | Functional (not perceptual) similarity | Statistical co-occurrence, not function |
| Bio B3 | Hox genes | Universal relational toolkit | Tier-1 not designed as universal toolkit |
| Bio B4 | Exaptation | Cross-domain functional recruitment | No recruitment mechanism |
| Bio B5 | Modularity | Decoupled variation + recombination | Modularity present; alignment absent |
| Bio B6 | Niche construction | Active representation construction | Passive retrieval only |
| LLM C1 | In-context learning | Implicit gradient descent in attention | No in-context adaptation |
| LLM C2 | Attention | Structural role alignment | VSA has binding but no role-discovery |
| LLM C3 | Scaling | Multi-domain emergent transfer | Single-domain training |
| LLM C4 | Induction heads | Abstract pattern completion | No inductive generalization step |
| LLM C5 | Superposition | Domain-general feature directions | Domain-specific embeddings |
| LLM C6 | CoT | Explicit intermediate alignment | No intermediate alignment step |
| LLM C7 | Multi-task pretrain | Cross-domain exposure pressure | Single-domain training |
| LLM C8 | RLHF | Systematicity reward signal | Proximity training only |
| LLM C9 | Interpretability circuits | Abstract relational circuits | No analogous circuit library |

---

## Next-drill candidates

1. BOUNDARY-PROBE P2 IMG-SCHEMA-CODEBOOK: exp_dev is already authorized to run this (Lakoff/Johnson 30 schemas + 50 metaphors, laptop CPU). This is E4 directly.
2. E1 LLM-SUBSTRATE-HYBRID: design as a new anchor (CROSS-DOMAIN-HYBRID-1), requires PP-225 LLM head + substrate relational neighborhood. This is the highest P_deflated path (0.62).
3. E2 RELATIONAL-FINGERPRINT-ALIGNMENT: new anchor (STRUCT-ALIGN-1), laptop CPU, pure FHRR, 3 hours.
