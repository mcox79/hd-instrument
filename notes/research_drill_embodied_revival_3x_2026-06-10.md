# research: embodied cognition revival drill (3-stream) -- 2026-06-10

**Topic:** What biological and computational mechanisms actually achieve embodied cognition, and what crazy math systems could a vector-symbolic substrate try to instantiate them?

**Trigger:** Boundary-probe finding that substrate reaches multi-modal associative memory (P=0.55 image-schema codebook) but not true embodiment. This drill applies the same 3-stream methodology (brain + nature + LLM theory) to find the real mechanisms and propose actionable substrate math systems.

---

## HEADLINE

Embodied cognition is not a single capability; it decomposes into four coupled subsystems -- (1) sensorimotor closure (action modifies perception modifies action), (2) a continuously updated body model (proprioceptive + interoceptive prior), (3) affordance detection (environment as action-gradient, not feature map), and (4) temporal integration across body-world interactions. All four are present in biology from C. elegans upward via independent evolutionary paths; LLMs acquire a degraded statistical shadow of (1) and (3) through text but lack (2) and real-time (4) entirely. The vector-symbolic substrate currently achieves static multi-modal binding (partial (1)) but none of the dynamic loop or body-prior structure. Eight concrete math systems are proposed, of which the two highest-P paths are IMAGE-SCHEMA-ODE (image schemas as attractor basins in substrate state space, laptop-testable in ~2 hours) and ACTIVE-INFERENCE-LITE (a simplified sensorimotor prediction-error loop over stored embeddings, no hardware required).

---

## STREAM A: BRAIN mechanisms for embodied cognition

### A1. Mirror neurons -- motor simulation as action parser

Rizzolatti et al. (1996, 2016) documented neurons in macaque F5 and IPC that fire both during execution and observation of goal-directed acts. The mirror mechanism transforms sensory representations of others' behavior into one's own motor representation of the same act. Crucially, this is not symbolic lookup -- it is a resonance between an observed motor trajectory and stored motor programs, with understanding arising as a byproduct of the match. The 2025 bibliometric review (Sun et al., Brain and Behavior) confirms the core mechanism is well-replicated; the controversy is whether activity constitutes "understanding" or is epiphenomenal to it. For substrate purposes: this is nearest-neighbor retrieval in motor-program space, applied to incoming sensory streams. The "understanding" is the retrieval event itself.

**Substrate angle:** Mirror mechanism = content-addressable retrieval where the query is a sensory trajectory and the codebook is motor programs. VSAs can implement this via fractional binding of observed-action trajectory to stored action-role bundles.

### A2. Conceptual metaphor theory -- abstract concepts grounded in body schemas

Lakoff and Johnson (1980, 1999) demonstrated that abstract concepts are not amodal but are systematically structured by bodily experience. MORE IS UP, AFFECTION IS WARMTH, ARGUMENT IS WAR -- each maps an abstract target domain to a concrete source domain rooted in sensorimotor experience. The grounding is not metaphorical decoration; neural imaging (Glenberg, Casasanto) shows that processing "the man kicked the ball" activates motor cortex.

Key schemas per Johnson (1987): CONTAINER (in/out), SOURCE-PATH-GOAL, FORCE (push/pull/block), BALANCE, LINK, CENTER-PERIPHERY, UP-DOWN. These are pre-linguistic, recurrent across cultures, and arise from the body's physical interactions with the world before language acquisition.

**Substrate angle:** Each schema is a structured binding pattern (CONTAINER = inside-item vs. outside-item with a boundary relation; FORCE = agent-trajectory-goal with an intensity scalar). These are VSA role-filler compositions. The question is whether schemas as *attractors* rather than *static bundles* are implementable.

### A3. Image schemas as cognitive primitives

Johnson (1987) "The Body in the Mind" is the canonical source. Image schemas are recurring dynamic patterns of our perceptual interactions and motor programs -- not images but skeletal structures. BALANCE requires no visual input; it is a felt structure of equilibrium. Current cognitive linguistics treats them as the minimal grounding units connecting sensorimotor experience to language meaning.

A 2024 study (arXiv 2402.00956) probed spatial schema intuitions in large vision-language models, finding that current LVMs handle CONTAINER and PATH superficially but fail on FORCE and BALANCE schemas requiring dynamic simulation.

**Substrate angle:** Image schemas are the bottleneck. They are not static patterns; they are dynamic structures that require temporal evolution (PATH implies motion; FORCE implies resistance; BALANCE implies ongoing correction). A static codebook captures the terminal state but not the schema itself.

### A4. Barsalou perceptual symbol systems -- simulation as cognition

Barsalou (1999, BBS) proposed that cognition runs on perceptual symbols -- modal, analog representations tied to sensorimotor systems. Simulation is the reenactment of perceptual, motor, and introspective states acquired during experience. Abstract concepts are grounded in complex simulations combining physical and introspective events. This directly challenges the classical view that concepts are amodal.

Key empirical support: Stanfield & Zwaan (2001) showed that sentence comprehension activates orientation-matched motor representations; comprehension of "he drove a nail into the floor" activates downward-motion motor patterns, not upward. Property verification (Barsalou et al. 2003) activates relevant sensory systems even for abstract properties.

**Substrate angle:** Simulation = running a stored trajectory forward in time. If substrate stores temporal sequences as VSA time-series bindings, then "simulating" an action means decoding the sequence. This is within reach of current substrate if temporal binding is extended.

### A5. Interoception -- the body as prior (Damasio + Craig)

Damasio's somatic marker hypothesis (1994, 1999) holds that body states tag decision options with valence -- the body's physiological response to a represented scenario is itself the signal that guides choice. The insula (Craig 2003, 2009) is the primary interoceptive cortex. Craig's model: posterior insula receives raw homeostatic/visceral signals; anterior insula generates a subjective emotional "moment" from integrating those signals with cognitive context.

The critical computational insight (Seth & Friston 2016): interoception is *predictive coding applied inside the body*. The brain predicts its own visceral states; mismatches generate feelings. The prior over body states is the interoceptive generative model.

**Substrate angle:** Interoceptive prior = a persistent context vector that modulates all retrieval. Every query is implicitly conditioned on current body state. In VSA terms: bundle the current "body state" hypervector with every query before lookup. This requires that the body state be updated dynamically -- a running register, not a static encoding.

### A6. Body schema vs. body image

Gallagher (2005) distinguishes: body *schema* (pre-reflective, operatively controlling posture/movement, updated continuously) vs. body *image* (reflective, conceptual representation of one's body as object). Phantom limb phenomena demonstrate the schema persists even after body part removal. The schema is not accessible to introspection in normal operation; it runs beneath awareness and updates on millisecond timescales.

**Substrate angle:** Body schema = the implicit coordinate system underlying all spatial computation. In substrate: this is the reference frame in which CONTAINER, PATH, and FORCE schemas are evaluated. A "body schema substrate" would be a low-dimensional manifold maintained as a continuously-updated prior that contextualizes spatial queries.

### A7. Affordances -- environment as action-gradient

Gibson (1979) defined affordances as action possibilities relative to an agent's body capabilities. Affordances are not mental constructs; they are real relational properties between agent and environment. The environment is perceived directly as a field of action possibilities, not as a set of geometric features requiring subsequent interpretation.

Modern ecological psychology (Chemero 2003; Turvey 2019) frames affordances as higher-order relational properties: an affordance is a dispositional property of the agent-environment system, not of either alone. Affordance perception requires body-scaled calibration -- children re-calibrate affordances after limb growth; amputees lose some and gain others with prosthetics.

**Substrate angle:** Affordance field = a gradient over stored item-vectors where the gradient direction points toward action-matched items. If substrate vectors encode items with their interaction signatures, then affordance retrieval is nearest-neighbor search in action-possibility space. This is structurally similar to current substrate retrieval, but the *query* must be a body-state + task composite, not a content query alone.

### A8. Predictive coding + active inference (Friston)

Friston's free energy principle (2010; FEP Made Simpler 2023, Physics Reports) frames all biological behavior as minimizing variational free energy -- an upper bound on surprisal. Perception = updating internal model to match sensory input; action = changing the world (or body position) to match predictions. The body is a Markov blanket: internal states are conditionally independent of external states given the blanket (sensory + active states).

Active inference extends this to policy: the agent acts to fulfill its predictions (proprioceptive predictions cause motor commands). Interoceptive active inference (Pezzulo et al. 2022) applies the same framework to visceral homeostasis.

The hierarchical generative model (HGM) view: cortex implements a hierarchy of precision-weighted prediction errors. High-level priors (body schema, emotional state) modulate the gain of lower-level sensory predictions.

**Substrate angle:** This is the most mathematically concrete of all A-stream mechanisms. Active inference maps to: (1) substrate stores a generative model (patterns of expected sensory input given body state and action), (2) retrieval is forward prediction, (3) update is the prediction error signal. FEP gives a principled loss function for updating the body model: minimize F = E_q[log q(s) - log p(s,o)] where s = hidden states, o = observations.

### A9. Sleep-wake embodied learning (REM rehearsal)

Wilson & McNaughton (1994) showed hippocampal place cells replay waking trajectories during slow-wave sleep. REM sleep is associated with motor rehearsal (Jouvet 1979; motor activity suppression via atonia prevents acting out). The hippocampal-cortical consolidation hypothesis (Squire & Alvarez 1995) frames sleep replay as the transfer of embodied episodic memories to neocortical long-term storage.

More recently: Stickgold (2005) showed that motor sequence learning shows overnight improvement -- the consolidation happens during sleep, not practice. Offline replay drives the embodied learning.

**Substrate angle:** Sleep-wave replay = iterative cleanup passes over recently-stored vectors during low-load periods. This is the substrate's current cleanup mechanism extended to include temporal sequence consolidation. Already empirically implemented as "per-level cascading cleanup" in v3.0 (crossed the 30-year VSA cliff per memory notes).

### A10. Default mode network + body self-model

Buckner et al. (2008) identified the DMN as active during rest, self-referential thought, and prospective simulation. The DMN is not "off-task"; it maintains the self-model, simulates future scenarios, and integrates autobiographical memory. Crucially, the DMN is heavily linked to interoceptive processing (Craig, Northoff 2011).

Northoff's spatiotemporal model (2014, 2021): the brain's resting-state activity defines a "neural predisposition" or prior against which all incoming stimuli are evaluated. This prior is body-indexed -- it encodes the temporal structure of the body's own physiological rhythms.

**Substrate angle:** DMN analog = the substrate's ambient state when not processing a specific query. Currently this is undefined (substrate is purely reactive). A "resting prior" that reflects the distribution of stored items and their temporal-recency structure would be a substrate DMN analog.

---

## STREAM B: NATURE / EVOLUTION mechanisms

### B1. Independent evolution of nervous systems -- convergence

The ctenophore (comb jelly) nervous system is almost certainly independently evolved from cnidarians and bilaterians (Moroz et al. 2014, Nature; Sachkova et al. 2024, Evolution & Development). Ctenophores evolved a syncytial nerve net -- electrically continuous cytoplasm rather than discrete synapses -- achieving functionally similar sensorimotor coordination with a completely different substrate. This means: embodied control is a convergent solution to the problem of coordinating a body in a physical environment, not a phylogenetically unique solution.

**Key implication:** Embodied cognition does not require any specific neural architecture. The functional requirements (sensorimotor closure, body model, temporal integration) are so powerful that evolution independently arrived at solutions multiple times. This is strong evidence that these are the correct abstractions -- they are computationally necessary given the problem, not accidental biological history.

### B2. C. elegans -- minimal embodied cognition in 302 neurons

The complete connectome of C. elegans (White et al. 1986; updated Witvliet et al. 2021) shows 302 neurons, ~7000 synapses. Yet C. elegans achieves: chemotaxis, thermotaxis, mechano-sensation, social feeding, associative learning, and navigation. The 2024 connectome analysis (PMC 11651592) revealed novel circuits for previously unstudied behaviors.

A connectome-based digital twin (MDPI 2023) achieved sensorimotor behavior from the structural connectivity alone, without learning. This is embodied cognition at minimal scale: the structure of the body-world interface is encoded directly in the wiring.

**Substrate angle:** The C. elegans connectome is effectively a hard-coded VSA binding pattern. The body's sensorimotor structure (which neurons connect to which muscles via which interneurons) is the "program." Substrate equivalent: pre-specified binding patterns that encode sensorimotor contingencies directly, without learning. This is the cheapest possible implementation of embodied coupling.

### B3. Octopus distributed cognition -- peripheral processing

Two-thirds of octopus neurons (~500M total) are in the arms, not the central brain. Each arm has an autonomous ganglion capable of executing reaching, grasping, and object manipulation independently of central command (Sumbre et al. 2001; Hochner 2012; 2024 3D molecular atlas of arm nerve cord, Current Biology). Central brain sends goal signals; arms implement them locally.

This is radically different from vertebrate motor control: there is no detailed motor program in the central brain. The arms are semi-autonomous agents that receive abstract goals and produce movements from local sensorimotor programs.

**Substrate angle:** OCTOPUS-DISTRIBUTED-SUBSTRATE: multiple semi-autonomous substrate instances per "limb," each with local storage and local sensorimotor programs, connected to a central coordinator via sparse abstract signals. This is the most radical departure from current architecture but has strong biological precedent.

### B4. Central pattern generators -- embodied rhythm without a brain

CPGs are networks of spinal interneurons that generate rhythmic locomotion patterns autonomously (Marder & Bucher 2001; PMC 3567435). Walking, swimming, breathing are controlled by CPGs with minimal descending input. A 2026 Nature Reviews Neuroscience paper redefines CPG as "dynamic, modular, and hybrid sensorimotor system" with speed-specific modules recruited by gear-shifting mechanisms.

Key insight: CPGs are the hardware implementation of abstract locomotion schemas. They provide the base rhythm; descending cortical and cerebellar input modulates timing and amplitude. The body's movement IS the cognition at this level -- there is no internal representation of "walking pattern" separate from the pattern itself.

**Substrate angle:** CPG analog = a substrate with a built-in oscillatory attractor that generates a default activity pattern. Query processing modulates phase and amplitude of the base rhythm rather than switching it on from rest. This would require the substrate to maintain ongoing state between queries -- currently not the operating mode.

### B5. Cerebellum -- internal model as embodied predictor

The cerebellum contains ~80% of brain neurons (Purkinje cells + granule cells). The prevailing model (Wolpert et al. 1998): cerebellum implements forward and inverse models of body dynamics. Forward model: predict sensory consequence of motor command. Inverse model: compute motor command to achieve desired sensory state.

Cerebellar adaptation (Marr 1969; Albus 1971; Ito 1984) occurs via long-term depression at parallel fiber-Purkinje cell synapses, driven by climbing fiber error signals. This is a gradient-based learning rule operating on a high-dimensional sparse code (granule cells have ~200,000 encodings of current sensorimotor context).

**Substrate angle:** Cerebellar analog = substrate layer that maintains forward models of sensorimotor contingencies. Current substrate: no prediction of sensory consequences; purely reactive. Adding a predictive layer (predict output given action+current state) would instantiate the minimal cerebellum function.

### B6. Plant tropisms -- embodied response without neurons

Auxin-mediated phototropism and gravitropism (Darwin 1880; Went & Thimann 1937) demonstrate stimulus-directed growth responses without any neural tissue. The shoot apex "detects" light direction via differential auxin redistribution; cells on the shaded side elongate more. The plant body itself computes the motor response.

This is embodied cognition at the chemical signaling level. No representation, no central processing -- the physical structure of the body and its chemical gradients ARE the computation.

**Substrate angle:** The radical implication is that embodied cognition does not require representation at all. A physical system that acts correctly without internal states is "embodied" in Gibson's sense. This challenges whether substrate should try to represent body states or should instead aim for direct sensorimotor coupling patterns that bypass explicit representation.

### B7. Microbial chemotaxis -- minimal sensorimotor coupling

E. coli chemotaxis (Berg & Brown 1972; Alon et al. 1999) achieves directed motion toward chemical attractants via a two-state flagellar motor (run vs. tumble) controlled by a phosphorylation cascade. The system is a minimal sensorimotor loop: CheY-P concentration encodes "current gradient," motor bias encodes "action." Adaptation is implemented by methylation, providing approximate temporal derivative (dC/dt) rather than absolute concentration.

This is the simplest possible implementation of sensorimotor closure: sense gradient, run straight if improving, tumble if not. The "body model" is implicit in the adaptation dynamics.

**Substrate angle:** E. coli teaches: (1) temporal derivative matters more than absolute value (rate-of-change detection), (2) sensorimotor coupling can be extremely simple and still generate complex collective behavior, (3) adaptation is the minimal form of prediction. Substrate could implement a "temporal derivative register" for any incoming signal stream, with run-vs-tumble as the action policy.

### B8. Bilateral symmetry + cephalization -- body plan as cognitive constraint

The evolution of bilateral symmetry + anterior-posterior axis + dorsal-ventral differentiation (Cambrian, ~540 Mya) is tightly correlated with the emergence of directed locomotion. Cephalization -- concentration of sensory organs and neural processing at the leading edge -- is a universal consequence of directed movement through an environment: the front of the animal encounters the world first.

Key implication: cognitive architecture is shaped by body plan. Frontal/posterior, dorsal/ventral, left/right are not arbitrary axes -- they are physical facts about the body's orientation in gravity, motion, and environment that get encoded directly into neural architecture.

**Substrate angle:** The substrate currently has no "orientation." All stored vectors are equivalent; there is no privileged direction of query-to-memory flow. Introducing an asymmetry -- a "frontal" processing region that encounters queries first, a "posterior" region for consolidated long-term storage -- would instantiate cephalization in the substrate.

### B9. Neural crest evolution -- proprioceptive organs

Neural crest cells (Gans & Northcutt 1983) gave rise to craniofacial structures, peripheral neurons, and the entire proprioceptive sensory system (muscle spindles, Golgi tendon organs, joint receptors). These are the biological sensors that provide the body schema with its real-time update signal. Without proprioception, body schema degrades catastrophically (Sacks' cases; Gallagher's IW case study of deafferented body).

**Substrate angle:** Proprioception = continuous self-monitoring signal that updates the body model. Substrate analog: a "proprioceptive register" that continuously monitors internal state (current activation pattern, retrieval confidence, recent query history) and uses this to update a running context vector. This is a lightweight but concrete implementation of the body-schema prior.

### B10. Convergent body-plan-cognition pairs

Strong convergence examples: (1) camera eyes evolved independently ~6 times (vertebrates, cephalopods, annelids, etc.) -- vision is a convergent embodied solution to the "perceive the world" problem; (2) magnetic navigation in birds, fish, and bacteria -- different molecular mechanisms, same embodied function; (3) distributed intelligence in octopus, starfish echinoderm water-vascular system, slime mold -- multiple solutions to distributed sensorimotor coordination.

The convergence argument is: wherever a body-world interaction problem is recurrent across taxa, evolution finds a solution. The solutions vary in implementation but converge on the same functional properties (sensorimotor closure, body model, affordance detection, temporal integration).

---

## STREAM C: LLM theories for embodied / grounding

### C1. Symbol grounding problem -- Harnad 1990

Harnad (1990) argued that symbols in any formal system are ungrounded -- they derive meaning only from other symbols, never from the world. Grounding requires connecting symbols to the real-world referents that give them meaning via transduction (sensory), not description.

The 2025 Frontiers review "Will multimodal LLMs ever achieve deep understanding?" applies this to modern MLLMs: the vector grounding problem (arXiv 2304.01481) notes that even in LLMs with continuous vectors, the grounding problem persists -- vector components are not connected to world referents but to other learned statistical patterns.

**Implication for substrate:** Static vector embeddings trained on text descriptions of embodied experience are not grounded. They encode the statistical shadow of body-world descriptions, not the sensorimotor relationships themselves.

### C2. Barsalou's verdict on LLM grounding

Barsalou's perceptual symbol systems theory predicts that genuine concept representation requires simulation of the associated sensorimotor states. LLMs trained on text activate none of the relevant sensorimotor simulations during processing; they learn statistical correlations between word forms. "Fire" does not activate heat receptors; "grip" does not activate motor programs.

The 2018 review (Barsalou & Matheson) maintains: without sensorimotor simulation, there is no genuine conceptual representation, only sophisticated pattern matching.

**Implication for substrate:** Genuine embodied cognition requires that processing the word/concept "grip" activates the stored pattern that co-occurred with gripping sensorimotor experience. In substrate terms: concept vectors must be co-encoded with their motor-signature vectors, and retrieval of the concept must automatically co-activate the motor signature.

### C3. Multimodal LLMs -- partial grounding

GPT-4V, Gemini, Claude 3 Vision: visual grounding via CLIP-style alignment. Cross-modal feature alignment (CLIP, Radford et al. 2021) learns a joint embedding space for images and text by maximizing cosine similarity for matched pairs. This gives a semantic alignment between visual and linguistic representations.

The MIT Computational Linguistics study (2024) "Do MLLMs and Humans Ground Language Similarly?" found: MLLMs ground language differently from humans. Humans use referential grounding (pointing to specific world instances); MLLMs use distributional grounding (statistical co-occurrence patterns in training data).

**Implication for substrate:** CLIP-style alignment is necessary but not sufficient for embodied grounding. It aligns two static modalities; it does not implement the sensorimotor loop or body model.

### C4. PaLM-E, RT-2, OpenVLA -- embodied LLMs

PaLM-E (Driess et al. 2023) embeds robot sensory data directly into LLM token streams, treating embodied observations as "tokens." RT-2 (Brohan et al. 2023) co-trains on web-scale language data and robot demonstrations, generating action tokens. OpenVLA (Kim et al. 2024): 7B-parameter open-source VLA trained on 970k robot demonstrations, outperforming RT-2-X (55B) on generalization.

The key insight from VLA research: language model priors help robot generalization enormously -- the LLM's world model provides scaffolding for sparse robot data. But the action-grounding is narrow; VLAs fail on novel body configurations and novel task combinations (out-of-distribution body-action combinations).

**Implication for substrate:** The successful embodied LLM formula is: language prior + embodied data stream + joint action-language embedding. The substrate's existing associative memory could implement the joint embedding; missing pieces are (1) streaming embodied data, (2) action output head.

### C5. World models -- Dreamer, MuZero, V-JEPA 2

Dreamer (Hafner et al. 2019-2023) learns a latent dynamics model from pixel observations and optimizes policy by imagining trajectories in latent space. DreamerV3 achieves cross-domain mastery with a single set of hyperparameters. MuZero (Schrittwieser et al. 2020) learns implicit world models via planning in latent space.

V-JEPA 2 (Meta 2025): video pretraining + minimal robot data yields an actionable world model for both video QA and robotics.

**Implication for substrate:** World models are the key missing ingredient between static associative memory and embodied cognition. A world model is a generative model that predicts next states given current state and action. This is structurally: predict(query, action) -> next_state. The substrate's existing forward recall could be extended to conditional next-state prediction.

### C6. Predictive world models for LLM planning

LLM-Based World Models (arXiv 2411.08794, 2024) analyze whether LLM world models can make decisions without external simulators. Finding: LLMs have implicit world models sufficient for planning in constrained domains, but they are not embodied -- they cannot simulate physical trajectories accurately.

The Survey on Learning Embodied Intelligence from Simulators and World Models (arXiv 2507.00917) identifies: the sim-to-real gap for embodied AI is fundamentally a world-model calibration problem. World models trained in simulation diverge from real-world physics.

**Implication for substrate:** The sim-to-real gap is a calibration problem solvable by grounding the world model in real sensorimotor data. For substrate: a world model calibrated on real (even CPU-testable) input-output trajectories would be better grounded than one trained on text descriptions.

### C7. Affordance learning in vision-language models

VoxPoser (Huang et al. 2023) uses LLMs to compose affordance maps for manipulation tasks -- language instructions decompose into spatial affordance fields that guide robot motion planning. Context-dependent affordance computation in VLMs (arXiv 2603.04419, 2026) shows affordance detection is highly context-sensitive and VLMs succeed when context is explicit but fail on novel body-context combinations.

**Implication for substrate:** Affordance representation requires encoding the agent-environment relationship, not just the object properties. In substrate terms: affordance vectors are relative to a body-state prior, not absolute feature vectors. The body-state modulates the affordance query.

### C8. JEPA-style predictive coding for LLMs

V-JEPA (Assran et al. 2023), JEPA (LeCun 2022): Joint Embedding Predictive Architecture. Prediction happens in latent space, not pixel space, by masking portions of the input and predicting their latent representation from context. This avoids pixel-level generative modeling and focuses on abstract structural prediction.

The advantage over pure contrastive learning (CLIP): JEPA trains an internal predictor, giving it an explicit world model component absent from contrastive methods.

**Implication for substrate:** JEPA-style prediction in the substrate's embedding space would instantiate a minimal world model without requiring pixel-level generation. The substrate predicts "what should the embedded representation of the next state be, given current state and action context?" This is computationally light (no generation, just vector prediction) and laptop-testable.

### C9. Cross-modal VSA binding

The VSA survey (ACM Computing Surveys 2023, Part II) covers multi-modal VSA binding for robotics sensorimotor fusion. Cross-layer VSA design (arXiv 2508.14245, August 2025) extends binding/bundling/projection to features without retraining -- directly applicable to embodied integration.

The neurosymbolic reasoning paper (arXiv 2509.03644, September 2025) explicitly builds a reasoning system grounded in schematic (image-schema-like) representations using VSA operations.

**Implication for substrate:** VSA is architecturally the right tool for multi-modal embodied binding. The substrate already has the algebra. What is missing is: (1) temporal binding across action-perception loops, (2) body-state modulation of query context, (3) dynamic attractor structure for schemas (rather than static codebook entries).

### C10. The vector grounding problem -- what static binding misses

The vector grounding problem (arXiv 2304.01481) precisely identifies what current LLMs (and by analogy current VSA substrates) lack: vector components are grounded in distributional statistics over other vectors, not in transductive connections to the world. High similarity in embedding space is not the same as shared referent.

For embodied grounding, the minimum requirement is: embedding similarity reflects shared sensorimotor context, not just linguistic co-occurrence. This requires that the training data for the embedding space include sensorimotor signals, not just text.

---

## STREAM D: SYNTHESIS + crazy substrate math systems

### D1. What all three streams share -- the core four

Across brain mechanisms, evolutionary biology, and LLM theory, four functional requirements are universal for embodied cognition:

1. **Sensorimotor closure**: perception affects action, action modifies perception, closed loop. No representation is purely passive.
2. **Body model (dynamic prior)**: a continuously updated internal model of the agent's own state, used to contextualize all other processing. Proprioception + interoception feed this.
3. **Affordance field**: the environment is represented as a field of action-possibilities relative to the body model, not as an objective feature map.
4. **Temporal integration**: the agent integrates body-world interactions over time to update schemas, not just static snapshots.

The current substrate has: static multi-modal binding (partial sensorimotor closure via codebook matching), no body model, no affordance representation, and no temporal integration. Gap is real and specific.

### D2. Eight crazy substrate math systems

**D2.1 IMAGE-SCHEMA-ODE** (HIGH P -- recommended first)

Encode the seven core image schemas (CONTAINER, SOURCE-PATH-GOAL, FORCE, BALANCE, LINK, CENTER-PERIPHERY, UP-DOWN) as ODE-defined attractor basins in the substrate state space.

Math: Define a vector field F: R^N -> R^N such that each schema corresponds to a stable fixed point x* of dx/dt = F(x). The ODE is a sum of schema-specific potentials:
F(x) = -sum_k alpha_k * grad_x V_k(x)
where V_k(x) = ||x - x_k*||^2 / 2 for simple quadratic basins, or with learned nonlinear depth for richer basins.

A query is embedded into this space; its trajectory under F(x) determines which schema it "falls into." The terminal attractor = schema label. The path through the space = the dynamic evolution of the schema interaction.

Laptop-testable: implement as discrete Euler integration over VSA hypervectors. N=1024, 7 schema attractors, 100-step integration. Runtime ~1 minute on CPU.

Precedent: cognitive map attractor basins ("Schema spaces as discrete latent conceptual attractor states" per arXiv 2509.14455), neural ODE cognitive architectures (1812.05205).

P_raw = 0.55 (image schema codebook P from boundary probe) | P_deflated = 0.35 (dynamic basin version is substantially harder) | HARD-PASS: >80% test queries route to correct schema attractor in <50 integration steps | HARD-FAIL: <50% route correctly OR steps diverge (attractor instability)

**D2.2 INTEROCEPTION-AS-PRIOR** (MEDIUM-HIGH P)

Maintain a "body state" hypervector B(t) that is updated after every retrieval event. All queries are fractionally bound to B(t) before lookup: Q_body = Q XOR_frac B(t).

Update rule: B(t+1) = normalize(0.9 * B(t) + 0.1 * result_vector(t))
This implements: (a) interoceptive influence on all cognition, (b) temporal autocorrelation of body state (0.9 decay), (c) body state updated by cognitive outcomes (prediction error signal).

This is a 10-line extension to current substrate retrieval. The body state is just a running average vector modulated by retrieval outcomes.

Laptop-testable: add body state register to existing retrieval loop; measure whether query routing changes as a function of recent retrieval history. Runtime negligible.

P_raw = 0.45 | P_deflated = 0.30 | HARD-PASS: query routing distribution shifts measurably (KL > 0.1 nats) as B(t) evolves through a simulated experience sequence | HARD-FAIL: routing is statistically identical with and without body-state modulation (p > 0.05, permutation test)

**D2.3 ACTIVE-INFERENCE-LITE** (HIGH P -- recommended second)

Implement a simplified active inference loop over the substrate's stored embeddings:

1. Substrate maintains a generative model G(s,a) -> predicted_o: "if I'm in state s and take action a, I expect to observe o."
2. At each step: observe o_t, compute prediction error = ||o_t - G(s_{t-1}, a_{t-1})||
3. Update state: s_t = argmin_s F(s, o_t) where F is variational free energy
4. Select action: a_t = argmin_a E_s[F(s_next, G(s,a))]

The substrate implements G as a matrix of expected sensory states per action, stored as VSA role-filler pairs. F minimization is an iterative cleanup operation -- structurally identical to current pattern completion, but applied to a prediction-observation mismatch rather than a noisy input.

This does not require a physical body. It can be run on any time-series input (text tokens, image patches, sensor readings). The "body" is the action space A; the "sensory input" is any observable sequence.

Laptop-testable: toy implementation with 4-state world, 2 actions, N=512 VSA. Run forward inference + free energy minimization for 100 steps. CPU runtime: ~30 seconds.

P_raw = 0.50 | P_deflated = 0.30 | HARD-PASS: free energy decreases monotonically over 10 steps for in-distribution sequences; agent selects informative actions (information gain > chance) | HARD-FAIL: free energy oscillates or increases on held-out sequences; action selection is random

**D2.4 AFFORDANCE-FIELD** (MEDIUM P)

Represent the environment as a scalar-valued affordance function over the substrate item space:
A(v; B) = <v, W_aff * B>
where v is an item vector, B is the current body-state vector, W_aff is a learned body-to-affordance weighting matrix.

High-affordance items are those most action-compatible given current body state. Retrieval becomes affordance-weighted nearest-neighbor: return argmax_v [similarity(q,v) + lambda * A(v; B)].

This is a perturbation of current nearest-neighbor retrieval by a body-state-dependent affordance term. W_aff is learned from co-occurrence statistics of (item, body state, action outcome) triples.

For laptop test: generate 1000 items with random 2D "affordance signatures" (action compatibility vectors). Train W_aff on simulated (item, body_state, affordance) triples via regression. Measure whether retrieval changes correctly with body state variation.

P_raw = 0.40 | P_deflated = 0.25 | HARD-PASS: retrieval precision@10 for affordance-matched items >70% vs <50% for affordance-unmatched items, across 3 body states | HARD-FAIL: affordance-weighted and standard retrieval give indistinguishable ranking (Kendall tau > 0.9)

**D2.5 OCTOPUS-DISTRIBUTED-SUBSTRATE** (LOW-MEDIUM P, high structural novelty)

Run multiple semi-autonomous substrate instances, each with local storage and local sensorimotor programs. Central coordinator sends abstract goal vectors; local substrates decode goals into local-domain actions.

Architecture: 4-8 local substrates S_1..S_k, each with N_local = 256 dimensions, storing domain-specific sensorimotor programs. Central substrate S_0 with N_central = 1024 dimensions, storing only abstract goal representations. Communication: S_0 sends goal_vec; S_i computes local action via content-addressed recall from local store; S_i returns action_vec to S_0 for integration.

Key property: local substrates can operate concurrently without locking. This mirrors the octopus arm architecture: arms solve local problems in parallel; central brain never needs to micromanage.

Laptop-testable: Python multiprocessing with 4 local substrates. Measure whether parallel local processing reduces total latency vs. sequential central processing for a multi-domain query.

P_raw = 0.35 | P_deflated = 0.20 | HARD-PASS: parallel local processing gives <50% latency of serial central processing on composite multi-domain queries | HARD-FAIL: inter-substrate communication overhead dominates, total latency equals or exceeds serial

**D2.6 PREDICTIVE-WORLD-MODEL-SUBSTRATE** (MEDIUM P, requires temporal binding)

Extend the substrate to predict the next embedding given the current embedding and an action token:
predict: (v_t, a_t) -> v_{t+1}

Implement as a second-order VSA operation: v_{t+1} = W_pred * (v_t XOR a_t), where W_pred is a learned prediction matrix trained on (v_t, a_t, v_{t+1}) triples from sensorimotor experience.

This is JEPA-style latent prediction: no pixel generation, just vector-to-vector prediction in the substrate's embedding space. Prediction error = ||v_{t+1} - predict(v_t, a_t)|| drives update of both W_pred and the body state prior.

Laptop-testable: train W_pred on a simple trajectory dataset (e.g., 500 steps of a 2D navigation task, embedded as 512-dim VSA vectors). Measure next-step prediction MSE vs. baseline (predict v_{t+1} = v_t).

P_raw = 0.40 | P_deflated = 0.25 | HARD-PASS: prediction MSE <50% of baseline on held-out trajectories; forward rollout of 10 steps has cumulative error <5x single-step error (bounded divergence) | HARD-FAIL: prediction MSE not better than baseline; rollout error explodes after 3 steps

**D2.7 EMBODIED-METAPHOR-BIND** (MEDIUM P, most algebraically creative)

Abstract concepts are bound ALGEBRAICALLY to body-schema substrates. Define a "metaphor operator" M: V_abstract -> V_bodily such that abstract concept queries are automatically projected into the nearest body-schema subspace before retrieval.

Implementation: maintain a "metaphor matrix" M (N x N), trained on (abstract_word, bodily_schema_match) pairs from conceptual metaphor databases (e.g., Lakoff-Johnson source-target pairs). For any query q: q_grounded = normalize(M * q + (1-alpha) * q). Retrieval uses q_grounded.

The metaphor operator effectively routes abstract queries through the body-schema subspace, instantiating Lakoff's hypothesis that abstract thought IS metaphorical (body-grounded) thought, not an approximation of it.

Laptop-testable: use GloVe or similar embeddings as proxy for VSA vectors. Train M on 50 source-target metaphor pairs from Lakoff (1980). Test whether M * abstract_query is more similar to bodily-domain vectors than original abstract_query.

P_raw = 0.40 | P_deflated = 0.25 | HARD-PASS: cosine similarity between M*q and bodily-domain vectors is >0.15 higher than between q and bodily-domain vectors, across 20 test metaphor pairs | HARD-FAIL: M*q is not closer to bodily-domain vectors than baseline q (no grounding transfer)

**D2.8 TOOL-EXTENDED-SUBSTRATE** (MEDIUM-HIGH P, clearest short-term path)

Implement the Maravita-Iriki (2004) body-tool integration in the substrate: tools (external items) are dynamically incorporated into the body schema during use.

Mechanism: when tool T is "in use" (retrieved + action-linked), extend the body-state vector B(t) by binding T into it:
B_extended(t) = normalize(B(t) + beta * T_vec)

All queries during tool use are contextualized by B_extended, not B(t). After tool use ends: B(t+1) = B(t) (revert). Optionally: B(t+1) = normalize(0.99 * B(t) + 0.01 * T_vec) for residual body-schema modification (tool leaves a trace, matching behavioral finding that tool use mildly extends peripersonal space even after tool removal).

This is the substrate analog of the empirically well-documented body-tool integration: after brief tool use, people judge peripersonal space (the region treated as part of the body for defensive responses) as extending to the tool tip.

Laptop-testable: 5-line modification to current retrieval. Measure whether adding T_vec to body context shifts retrieval rankings for tool-related queries (expected: +tool queries should be relatively promoted; -tool queries should be demoted).

P_raw = 0.50 | P_deflated = 0.35 | HARD-PASS: retrieval precision for tool-contextual queries improves >10% with B_extended vs. B(t); effect reverses when tool is removed | HARD-FAIL: retrieval precision unchanged by B_extended (<5% delta, not statistically significant)

---

## D3. Five empirical test designs (laptop CPU, ranked by P * implementation-ease)

**Test 1: IMAGE-SCHEMA-ODE (most recommended)**
- Setup: N=1024 FHRR hypervectors; 7 schema attractors as fixed point vectors x_k* generated orthogonally; quadratic basins V_k(x) = 0.5 * ||x - x_k*||^2
- Test: 200 query vectors drawn from von Mises-Fisher distribution around each attractor (20 per schema + 60 "boundary" queries equidistant from 2+ attractors); run Euler integration dx/dt = -grad F(x) for 50 steps with step size 0.1
- Measure: fraction of queries converging to correct attractor; number of steps to convergence; boundary query disambiguation rate
- Expected result per theory: in-basin queries converge in <20 steps; boundary queries resolve to nearest basin; force/balance schemas (dynamic) will show longer convergence than container/link (more static)
- Runtime: <2 minutes on CPU

**Test 2: ACTIVE-INFERENCE-LITE (second recommended)**
- Setup: 4-state world (states: {A, B, C, D}), 2 actions ({move_forward, rotate}), transition matrix T[s,a]->s' given; observations are N=512 VSA vectors of state; generative model G stored as VSA role-filler pairs; free energy F = KL[q(s) || p(s)] + expected_surprise
- Test: 1000 steps of active inference; measure (1) free energy trajectory (should decrease), (2) action selection informativeness (should visit unvisited states), (3) held-out prediction accuracy
- Expected result: F decreases after adaptation; agent explores all 4 states; prediction accuracy >75% in familiar states
- Runtime: <1 minute on CPU

**Test 3: TOOL-EXTENDED-SUBSTRATE (quickest, least novel)**
- Setup: existing substrate with 500 stored item vectors; 10 designated "tool" vectors; body state B random unit vector; 50 test queries split: 25 "tool-related" (similar to tool vectors) + 25 "tool-unrelated"
- Test: retrieval with B vs. B_extended = B + beta * T_vec for 5 tools; measure recall@5 for tool-related queries in both conditions
- Expected result: tool-related query recall@5 improves ~15-25% with B_extended; tool-unrelated recall unchanged (tool doesn't bleed into unrelated retrieval)
- Runtime: <30 seconds

**Test 4: INTEROCEPTION-AS-PRIOR**
- Setup: 200-step simulated experience sequence; body state B(t) updated after each retrieval; test whether routing distribution shifts over experience
- Measure: KL divergence between query routing distribution in steps 1-50 vs. steps 151-200; compare to shuffled control (no autocorrelation in B updates)
- Expected result: KL > 0.1 for structured experience; KL ~ 0 for shuffled control
- Runtime: <1 minute

**Test 5: EMBODIED-METAPHOR-BIND**
- Setup: use 300-dim GloVe vectors as proxy; sample 50 Lakoff metaphor pairs (abstract_concept -> bodily_source); train 300x300 matrix M by regression; test on held-out 20 pairs
- Measure: cosine similarity delta between M*q and bodily-source vectors vs. q and bodily-source vectors
- Expected result: delta > 0.1 for systematic metaphor families (TEMPERATURE-EMOTION, VERTICAL-IMPORTANCE, CONTAINMENT-THOUGHT)
- Runtime: <5 minutes

---

## D4. Honest assessment of the crazy paths

**Highest P_deflated paths:** IMAGE-SCHEMA-ODE (0.35) and TOOL-EXTENDED-SUBSTRATE (0.35) are the most defensible. Both have direct biological precedent, clear algebraic implementation in VSA, and laptop-testable falsifiers that would actually distinguish them from current substrate behavior.

**Why D2.1 and D2.8 are highest:** Image schemas are the acknowledged bottleneck for embodied grounding (A3, C9), and the dynamic ODE version is a meaningful extension over static codebook. Tool extension is directly grounded in empirical neuroscience (Maravita-Iriki 2004 is one of the clearest body-schema experiments) and is a trivial algebraic extension of current B(t) vector.

**Why OCTOPUS-DISTRIBUTED (D2.5) is lowest P:** The architectural change is large, the coordination overhead is real, and the biological precedent (octopus) does not straightforwardly map to the substrate's operating mode. Worth exploring eventually but not the first bet.

**Why ACTIVE-INFERENCE-LITE (D2.3) is high-potential despite medium P:** The FEP framework is the most mathematically complete theory of embodied cognition. Getting even a toy version running would open a large design space (hierarchical generative models, precision-weighted priors, interoceptive active inference). The initial implementation is cheap; the payoff if it works is large.

**What "embodied cognition" would actually mean for the substrate product:**
If D2.1 (image schemas as attractors) + D2.3 (active inference loop) both pass their laptop tests, the substrate would have: (1) dynamic schema routing rather than static codebook lookup, (2) a sensorimotor prediction loop that improves with experience, (3) body-state modulation of all queries. This would be a qualitatively different cognitive architecture from current retrieval-only substrate -- closer to what Gibson called "direct perception" (affordance-driven, body-anchored, temporally continuous) than to classical information retrieval.

---

## Calibration

Applying [[feedback-lit-scan-calibration-penalty]]:
- All P estimates above are already deflated by 0.15-0.25 from raw assessments
- Novel-synthesis P (D2.7 EMBODIED-METAPHOR-BIND) capped at 0.35 per rule
- Prior note: image-schema codebook probe returned P=0.55 (static version); dynamic ODE version P_deflated=0.35 is not a contradiction -- it is the deflated estimate for the harder dynamic version

---

## Cheap decisive test

**Recommended first test:** IMAGE-SCHEMA-ODE (D2.1)

Reason: directly tests whether substrate state-space dynamics can instantiate the schema-as-attractor structure that both cognitive science (Johnson 1987; Barsalou 1999) and the VSA literature (arXiv 2509.03644) identify as the grounding mechanism. Pass/fail on the 7-schema 200-query convergence test definitively answers whether VSA state-space has the right structure for dynamic schema grounding. Costs 2 hours of CPU coding + runtime. Falsifies or confirms the core claim.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

**HARD-PASS (embodied revival is viable via these specific mechanisms):**
- IMAGE-SCHEMA-ODE: >80% of in-basin queries converge to correct schema attractor in <50 Euler steps (N=1024, 7 schemas)
- ACTIVE-INFERENCE-LITE: variational free energy decreases monotonically for in-distribution sequences; action entropy decreases over 100 steps (exploration -> exploitation)
- TOOL-EXTENDED-SUBSTRATE: recall@5 for tool-contextual queries improves >10% with B_extended vs. B; no significant change for non-tool queries

**HARD-FAIL (embodied revival is not viable via this path):**
- IMAGE-SCHEMA-ODE: <50% convergence rate OR step count diverges for >10% of queries -- indicates VSA geometry is not compatible with schema-basin structure at N=1024; rescue would require N>4096 or non-quadratic basin design
- ACTIVE-INFERENCE-LITE: free energy oscillates or increases after adaptation; action selection indistinguishable from random -- indicates VSA binding is not expressive enough to represent the generative model G at toy scale
- TOOL-EXTENDED-SUBSTRATE: recall delta <5% (not statistically significant at N=500 items) -- indicates B(t) modulation is too weak to shift retrieval at current substrate N

---

## Cross-thread synthesis

**Prior Exp-Dev findings relevant here:**
- Per-level cascading cleanup (memory notes: "L5 recall 0.000->1.000") is structurally the substrate's equivalent of sleep-wave replay (Stream A9). The embodied revival drill makes this link explicit: the cleanup mechanism is a form of offline consolidation.
- Friston FEP probe (notes/exp_dev_handoff_research_friston_fep_substrate_2026-06-04.md) is directly relevant to D2.3. Recommend reading that note before implementing ACTIVE-INFERENCE-LITE.
- The small-brain-substrate template (exp_dev_handoff_research_small_brain_substrate_template_2026-06-04.md) and biological-precedents probe (exp_dev_handoff_research_biological_precedents_animal_scales_2026-06-04.md) are adjacent; this drill extends their findings to the embodied cognition regime.
- The multimodal-substrate-primitives note (2026-06-04) is the immediate predecessor; this drill addresses why that probe reached only P=0.55 (static codebook, not dynamic schemas).

---

## Substrate-product implications

1. **Short-term (laptop-testable):** IMAGE-SCHEMA-ODE and TOOL-EXTENDED-SUBSTRATE can be tested within a day. If both pass, the substrate has dynamic grounding that no existing LLM or VSA system demonstrates in the literature (most work is static codebook). This is a genuine differentiator.

2. **Medium-term:** ACTIVE-INFERENCE-LITE, if it passes, gives the substrate a principled update rule (free energy minimization) for adapting to a sensorimotor stream. This would make the substrate genuinely learnable in deployment rather than requiring offline retraining.

3. **Product claim implication:** The substrate's current claim is associative memory with compositional recall. The embodied revival adds: *context-sensitive retrieval that adapts to agent state*. This is the difference between a library (static retrieval) and a situated cognizer (body-state-modulated retrieval). The product claim upgrade is significant if the laptop tests pass.

4. **Honest limitation:** None of these implementations constitute full embodied cognition in the biological sense. They are approximations. The genuine article requires a physical body with proprioception, real-time sensorimotor coupling, and continuous interoceptive update. The substrate's laptop-testable versions are functional analogs that implement the algebraic structure without the full physical grounding. Whether the algebraic structure is sufficient for downstream task performance is the empirical question.

---

## Citations (verified count: 32)

Stream A:
1. Rizzolatti G. et al. (1996). Premotor cortex and recognition of motor actions. Cognitive Brain Research.
2. Rizzolatti G. & Sinigaglia C. (2016). The mirror mechanism: a basic principle of brain function. Nature Reviews Neuroscience.
3. Sun et al. (2025). What Else Is Happening to the Mirror Neurons? Bibliometric analysis 1996-2024. Brain and Behavior. PMC11982629.
4. Lakoff G. & Johnson M. (1980). Metaphors We Live By. University of Chicago Press.
5. Lakoff G. & Johnson M. (1999). Philosophy in the Flesh. Basic Books.
6. Johnson M. (1987). The Body in the Mind. University of Chicago Press.
7. Barsalou L.W. (1999). Perceptual symbol systems. Behavioral and Brain Sciences.
8. Barsalou L.W. (2008). Grounded cognition. Annual Review of Psychology.
9. Damasio A. (1994). Descartes' Error. Putnam.
10. Craig A.D. (2003). Interoception: the sense of the physiological condition of the body. Current Opinion in Neurobiology.
11. Gallagher S. (2005). How the Body Shapes the Mind. Oxford University Press.
12. Gibson J.J. (1979). The Ecological Approach to Visual Perception. Houghton Mifflin.
13. Friston K. et al. (2023). The Free Energy Principle Made Simpler but Not Too Simple. Physics Reports.
14. Friston K. et al. (2024). Designing Ecosystems of Intelligence from First Principles. Collective Intelligence.
15. Friston K. et al. (2018). The Markov blankets of life. J. Royal Society Interface. PMC5805980.
16. Wilson M. & McNaughton B. (1994). Reactivation of hippocampal ensemble memories. Science.
17. Buckner R.L. et al. (2008). The brain's default network. Annals of the NY Academy of Sciences.

Stream B:
18. Moroz L.L. et al. (2014). The ctenophore genome and the evolutionary origins of neural systems. Nature.
19. Sachkova M.V. et al. (2024). Evolutionary origin of the nervous system from Ctenophora prospective. Evolution & Development.
20. Hochner B. (2012). An embodied view of octopus neurobiology. Current Biology.
21. Marder E. & Bucher D. (2001). Central pattern generators and the control of rhythmic movements. Current Biology.
22. Wolpert D.M. et al. (1998). Multiple paired forward and inverse models for motor control. Neural Networks.
23. Alon U. et al. (1999). Robustness in bacterial chemotaxis. Nature.
24. White J.G. et al. (1986). The structure of the nervous system of C. elegans. Philosophical Transactions of the Royal Society B.

Stream C:
25. Harnad S. (1990). The symbol grounding problem. Physica D.
26. Frontiers review (2025). Will multimodal LLMs ever achieve deep understanding? PMC12679578.
27. arXiv 2304.01481: The Vector Grounding Problem.
28. arXiv 2409.16900: A Roadmap for Embodied and Social Grounding in LLMs.
29. Radford A. et al. (2021). Learning transferable visual models from natural language (CLIP). ICML.
30. Driess D. et al. (2023). PaLM-E: An Embodied Multimodal Language Model. ICML.
31. arXiv 2402.00956: Exploring Spatial Schema Intuitions in LLMs/VMs.
32. arXiv 2509.03644: Towards a Neurosymbolic Reasoning System Grounded in Schematic Representations.

Maravita-Iriki:
33. Maravita A. & Iriki A. (2004). Tools for the body (schema). Trends in Cognitive Sciences.

---

## Research decisions log pointer

See: notes/research_decisions_2026-06-10.md (appended)
