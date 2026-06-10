# Research drill: Embodied cognition -- NOW shard overclaim retraction (2x depth)

Filed: 2026-06-10
Sub-agents: research:sonnet (3 parallel lit-scan threads)
Calibration: lit-scan penalty applied; P_deflated = raw - 0.20; novel-synthesis cap 0.50

---

## HEADLINE

The claim "NOW shard with sensorimotor state solves embodiment" is wrong. Lakoff/Johnson
embodied cognition requires sensorimotor LOOPS that CONSTITUTE abstract concepts through
body-schema metaphors -- not data binding. The substrate can do multi-modal binding and
image-schema codebook encoding; it cannot and does not solve the philosophical problem of
embodiment. Retraction is correct. Five engineering anchors exist that are honest and
achievable.

---

## What embodied cognition actually requires

### 1. The Lakoff/Johnson thesis (Philosophy in the Flesh, 1999)

Lakoff and Johnson's core claim has three parts:

(a) The mind is inherently embodied -- meaning that the very structure of thought is
    shaped by the body's sensorimotor capacities, not just informed by them.

(b) Thought is mostly unconscious -- the image-schema level operates below deliberate
    linguistic representation.

(c) Abstract concepts are largely metaphorical, where the metaphors are GROUNDED in
    recurring bodily experience. Not "illustrated by" body schemas. Not "mapped onto."
    The abstract concept IS constituted by the metaphor. TIME IS A PATH is not a
    poetic decoration -- it is the cognitive structure through which temporal reasoning
    works.

The canonical examples: UP = GOOD (power, health, happiness all spatially encoded as
vertical), WARMTH = AFFECTION (physical thermal experience constitutes social bonding
semantics), CONTAINER = CATEGORIES (being inside vs outside a category inherits the
physical logic of containers: bounded interior, exterior, boundary, in-out transitions).

This is not sensor data binding. The claim is stronger: abstract concept formation is
architecturally grounded in recurrent sensorimotor regularities that the body has
accumulated over developmental time. Remove the body, and the concepts lose their
structural coherence -- not their labels, but their inferential affordances.

### 2. Image schemas (Johnson 1987, "The Body in the Mind")

Image schemas are recurring patterns of bodily interaction that provide the skeletal
structure for abstract inference. The canonical inventory includes:

- CONTAINER: bounded space with interior, boundary, exterior. Yields logic of in/out,
  transitivity (if A contains B and B contains C, A contains C), and categorical
  membership.
- PATH: source, trajectory, goal. Yields temporal reasoning, causal sequencing,
  narrative structure.
- BALANCE: bilateral symmetry, equilibrium. Yields justice reasoning, mathematical
  equality, aesthetic judgment.
- FORCE: exertion, resistance, result. Yields causal reasoning, intentionality,
  obligation (moral FORCE dynamics per Talmy).
- LINK: connection, attachment, separation. Yields relation reasoning.
- VERTICALITY: up/down axis derived from gravity and postural experience.
- CENTER-PERIPHERY, NEAR-FAR, PART-WHOLE, FULL-EMPTY: each with distinct inferential
  entailments.

These are not metaphors -- they are pre-linguistic bodily regularities that BECOME
metaphors when projected onto abstract domains. The key point: the schema arises from
sensorimotor experience, not from labeled data.

### 3. Barsalou Perceptual Symbol Systems (1999, Behavioral and Brain Sciences)

Barsalou's framework complements Lakoff/Johnson at the neural implementation level.
Perceptual symbols are not images -- they are records of neural states in sensorimotor
systems captured during perception and action. Concepts are implemented as SIMULATORS:
systems that reenact partial sensorimotor states across modalities.

When you comprehend "apple," the visual cortex partially reactivates apple-associated
visual patterns, the motor cortex partially reactivates reach-and-grasp patterns, the
olfactory regions partially reactivate smell-associated patterns. Comprehension is
multimodal simulation, not lookup in an amodal symbol table.

What this requires: a neural architecture where (a) sensorimotor systems encode
experience, (b) those encodings are reactivatable in the absence of the original
stimulus, and (c) partial reactivation patterns serve as the substrate for conceptual
combination.

### 4. Glenberg and Kaschak: Action-sentence compatibility (2002)

The action-sentence compatibility effect (ACE) showed that processing sentences
implying toward/away movement produces response-time differences for physically
toward/away responses. The motor system is active during language comprehension --
not as a byproduct, but as a constitutive part of the comprehension process.

Glenberg's indexical hypothesis: words activate representations of objects and actions
in the environment, affording possible motor interactions. Comprehension is constructing
an executable simulation of the described situation, not parsing propositions.

What this requires: coupling between the linguistic system and the motor system such
that language processing REQUIRES motor activation, not just that motor activation
CAN accompany it.

### 5. Gibson affordances and ecological perception (1979)

Gibson's affordances are not properties of objects, and not properties of perceivers.
They are relations between the organism's action capabilities (effectivities) and
environmental properties. A doorknob affords turning for a hand but not for a fin. The
affordance only exists relative to a body with specific action repertoires.

Direct perception: the organism perceives the world in terms of action possibilities,
not in terms of object properties that are then interpreted in terms of action. The
perception-action loop is not sequential (perceive, then compute, then act) -- it is
simultaneous and bidirectional.

What this requires: the perceiver must have a body with specific effectivities, and the
perceptual system must be tuned to extract affordance information relative to those
effectivities. Without a body, affordances do not exist in the technical sense.

### 6. 4E cognition (Varela, Thompson, Rosch 1991; Maturana and Varela 1987)

The four E's:

- Embodied: cognition depends on having a body with sensorimotor capacities, and those
  capacities are themselves shaped by being embedded in the environment.
- Embedded: cognition is situated in environmental context; cognitive processes extend
  into environment, not just inside the skull.
- Enacted: cognition arises through active engagement with the world -- it is not
  representation of a pre-given world but co-constitution of a world through action.
- Extended (Clark and Chalmers 1998): cognitive processes can literally extend beyond
  the skin, incorporating external artifacts and structures.

The enactivist claim is the strongest: cognition is not computation over internal
representations -- it is the ongoing sensorimotor engagement between organism and
environment. The autopoietic background (Maturana/Varela) adds that the organism
actively maintains its own organization through structural coupling with the environment.

### 7. Harnad symbol grounding (1990)

Harnad's symbol grounding problem: a purely formal symbol system has no intrinsic
meaning -- symbols are interpreted by external observers, not by the system itself.
Grounding requires anchoring symbols in sensorimotor categories that pick out
non-arbitrary features of the world.

Harnad's proposed solution: grounding must ultimately be sensorimotor, not symbolic.
Iconic representations (analog resemblance to sensory inputs) and categorical
representations (sensorimotor invariants) ground the lowest-level symbols, from which
higher-level symbols can be defined by composition. The critical point: you cannot
ground symbols purely by connecting them to other symbols, even other multimodal symbols.
The chain terminates in sensorimotor coupling with the physical world.

The vector grounding problem (2023 reformulation): vector embeddings in language models
face the same structural problem. Statistical co-occurrence across text does not ground
symbols in sensorimotor experience, even at scale. Multimodal training (vision-language)
provides some traction but has not demonstrated compositional grounding -- systematic
binding of visual features to action schemas to abstract inference chains.

### 8. Pulvermuller mirror neurons and motor-language coupling

Motor cortex activates in a somatotopic manner when processing action words: leg-action
words activate leg motor areas, arm-action words activate arm motor areas. TMS
disruption of motor cortex affects lexical decision time for action words. This is not
an association -- it is constitutive coupling. The motor representation IS part of the
word representation, not a byproduct.

What this requires at the neural level: distributed assemblies spanning sensorimotor
and linguistic cortex, where the connections form during embodied development. The
coupling is learned through repeated sensorimotor experience with objects and actions,
not from linguistic co-occurrence statistics.

---

## What a sensorimotor LOOP requires (vs. passive data binding)

A sensorimotor loop has five structural requirements that passive data binding does not meet:

1. CONTINUOUS BIDIRECTIONALITY: the action taken based on sensory state changes the
   sensory state, which changes the next action. The loop must close -- output must
   feed back to input.

2. CONSTITUTIVE COUPLING: the loop shapes the structure of representation, not just
   its content. Piaget's sensorimotor stage: concepts form THROUGH action, not
   alongside it.

3. AFFORDANCE INDEXING: representations are structured by what the system CAN DO with
   what it perceives, relative to its specific body geometry and force capacity.

4. TEMPORAL INTEGRATION: the loop operates in real time with physical latencies. Motor
   commands predict sensory consequences (efference copy), and prediction errors drive
   learning.

5. DEVELOPMENTAL TRAJECTORY: the schemas form over developmental time through
   accumulated sensorimotor regularities. They cannot be injected post-hoc as labeled
   data.

Binding sensor data to symbolic concepts at query time satisfies none of these five
requirements. It is closer to logging than to grounding.

---

## Where NOW shard falls short

### 3.1 Symbol grounding is not solved

A NOW shard attaches a sensor reading (e.g., temperature = 22.4) to a symbolic concept
("temperature"). This is labeling, not grounding. The concept "temperature" in the shard
has the same referential status it had before -- a token in a symbol system. The sensor
value is just another symbol bound to it. The grounding chain terminates in the sensor
hardware, not in a sensorimotor experience that constitutes the concept.

Harnad's criterion: grounding requires the symbol to be anchored in sensorimotor
categories that NON-ARBITRARILY pick out features of the world. A floating-point number
from a temperature sensor does not meet this criterion -- the number is just as arbitrary
as the word "temperature"; the analog-to-digital conversion happens in the sensor, not
in the cognitive system.

### 3.2 Conceptual metaphors are not encoded

The conceptual metaphors that Lakoff/Johnson identify -- WARMTH=AFFECTION,
UP=GOOD, CONTAINER=CATEGORIES -- are not present in a NOW shard. They require a
history of sensorimotor experience in which thermal states co-occur with social bonding,
gravitational orientation co-occurs with positive outcomes, and physical containment
co-occurs with categorical membership. None of this history is in the shard. The shard
holds current sensor state, not accumulated sensorimotor regularities.

Even if the shard contained a rich history of sensor readings, this would still not
constitute conceptual metaphor formation, because metaphor formation requires that the
SOURCE DOMAIN (body schema) structurally maps onto the TARGET DOMAIN (abstract concept),
inheriting its inferential logic. A statistical co-occurrence of temperature values with
positive-affect labels does not create the WARMTH=AFFECTION structure -- it creates a
correlation. The inferential entailments are different.

### 3.3 No sensorimotor loop -- only passive data binding

The NOW shard receives sensor data. It does not issue motor commands. It does not predict
sensory consequences of motor actions. It does not have efference copy. It does not
generate prediction errors from motor-sensory mismatches. The loop does not close.

This means the data binding is not CONSTITUTIVE of the concept structure -- it is
decorative. The concepts exist independently; the sensor data is appended. In genuine
embodied cognition, there are no concepts independent of the sensorimotor history; the
concepts ARE the abstraction over sensorimotor regularities.

### 3.4 Body schemas are absent

Body schemas are structural representations of the body's geometry, mass distribution,
joint constraints, reach envelopes, and postural states. They provide the spatial
reference frame within which image schemas are grounded. NEAR and FAR are not abstract
distances -- they are reach-relative. UP and DOWN are not gravitational abstractions --
they are posture-relative.

Without a body schema, the spatial image schemas have no reference frame. They become
purely symbolic again -- UP as a label with associated UP-ness tokens, rather than UP as
a structured spatial relation grounded in postural experience.

### 3.5 Affordances are not represented

Affordances require an agent with specific effectivities (action capabilities). A NOW
shard that contains "chair: present at coordinates X,Y" does not represent the chair as
affording sitting -- it represents the chair as an object with a location. The affordance
relation (chair + human body geometry + gravitational field + structural rigidity =
sit-able) is not in the shard.

Representing affordances requires: (a) a model of the agent's own body and its action
capabilities, (b) perception of environmental properties relative to those capabilities,
and (c) the coupling between perception and action that makes the affordance actionable.
None of these are present in a NOW shard.

---

## What the substrate CAN do realistically

The following are achievable and honest. None of them constitutes solving embodied
cognition philosophically. All of them are potentially useful engineering additions.

### 4.1 Multi-modal binding (cross-modal co-occurrence)

The substrate can store vectors from multiple modalities (text, image embeddings,
sensor readings converted to vectors) in the same high-dimensional space. It can bind
them via superposition and retrieve by any modality as a query cue.

What this is: fast associative memory over multi-modal data.

What this is NOT: sensorimotor grounding, symbol grounding, or conceptual metaphor
formation.

Honest claim: "The substrate can retrieve semantically associated content across
modalities -- text, image, sensor data -- given a query in any modality."

### 4.2 Schema extraction via pattern detection

If the substrate is populated with a large history of co-occurrence data (e.g., many
instances of "warm temperature" co-occurring with "positive social event"), it can
extract that co-occurrence as a retrievable association. This is a statistical regularity
capture, not a schema in the Lakoff/Johnson sense.

What this is: pattern mining in associative memory.

What this is NOT: the body-schema-grounded abstract concept formation that Lakoff/Johnson
describe.

### 4.3 Explicit image-schema codebook (IMAGE-SCHEMA-CODEBOOK anchor)

The most honest path to something schema-adjacent: explicitly encode the 30+ canonical
image schemas (CONTAINER, PATH, BALANCE, FORCE, LINK, VERTICALITY, etc.) as named
vectors in the substrate. These become first-class retrieval anchors.

What this achieves: any concept or situation can be tagged with its structurally closest
image schema(s). Retrieval can be schema-conditioned: "find situations that have PATH
structure" retrieves narratives with source-trajectory-goal patterns.

What this is NOT: grounding -- the schemas are hand-labeled by the builder, not formed
through sensorimotor experience. The inferential entailments are not inherited
automatically; they must be explicitly programmed or trained.

Value: schema-conditioned retrieval is useful for structured reasoning over episodic
memory, narrative understanding, and analogical reasoning. This is achievable.

### 4.4 Affordance representation as explicit object-action pairs (AFFORDANCE-REP anchor)

The substrate can store explicit (object, action, agent-type) triples: ("chair",
"sitting", "human"), ("handle", "grasping", "human"). These are affordance annotations,
not affordances in Gibson's sense.

What this achieves: structured retrieval of action possibilities given an object
description.

What this is NOT: genuine affordance perception relative to a specific body's effectivities
in a specific environment. Real affordance is relational and situation-specific; stored
triples are categorical and static.

Value: useful for task planning, action recommendation, and robot-memory integration
when the robot's effectivities are known at design time.

---

## Five engineering anchors

These are honest, achievable experiments. P_deflated estimates after calibration penalty.

### Anchor 1: IMAGE-SCHEMA-CODEBOOK

Task: Build a codebook of 30-40 canonical image schemas as explicit vectors in the
substrate. Define schema membership criteria for tagging new content. Test whether
schema-conditioned retrieval (retrieve items tagged with CONTAINER schema, PATH schema,
etc.) returns structurally coherent results.

Pre-reg:
  HARD-PASS: Schema-conditioned retrieval returns items with consistent structural
             properties at precision >= 0.70 on held-out set.
  HARD-FAIL: Precision < 0.45 (chance-level for 4-way schema classification).
  MID-BAND: Precision in [0.45, 0.70] -- refine schema boundary criteria.

P_deflated = 0.55 (explicit hand-labeling removes most uncertainty; main risk is
that schema boundaries are too fuzzy for consistent retrieval).

Tier: CPU laptop. Low engineering cost. No sensorimotor loop required.

### Anchor 2: METAPHOR-BINDING

Task: Test whether binding a conceptual metaphor structure (e.g., UP vectors associated
with POSITIVE-OUTCOME vectors) produces useful cross-domain retrieval: querying with
"high performance" retrieves items associated with "elevated status" and "increased
value" via the shared UP schema.

Pre-reg:
  HARD-PASS: Metaphor-mediated retrieval recall@5 >= 0.60 on 50 test pairs spanning
             3+ source domains (spatial, thermal, force).
  HARD-FAIL: recall@5 < 0.30 (no metaphor transfer over chance).
  MID-BAND: recall@5 in [0.30, 0.60] -- metaphor transfer is schema-specific.

P_deflated = 0.40 (metaphor binding is statistically feasible but the inferential
entailments may not transfer; the test might measure labeling not structure).

Tier: CPU laptop. Depends on IMAGE-SCHEMA-CODEBOOK anchor.

### Anchor 3: SENSOR-SYMBOL-CO-OCCURRENCE

Task: Populate the substrate with a dataset of (sensor reading, symbolic label, context)
triples across multiple modalities. Test whether multi-modal retrieval improves recall
vs. single-modality retrieval on cross-modal queries.

Pre-reg:
  HARD-PASS: Cross-modal recall@10 >= 0.75 vs. single-modality recall@10 < 0.60.
  HARD-FAIL: Cross-modal recall@10 <= single-modality recall@10 (no binding benefit).
  MID-BAND: Cross-modal improves by less than 10 percentage points.

P_deflated = 0.60 (multi-modal binding is the core substrate capability; this is mostly
a benchmark formalization, not a novel mechanism test).

Tier: CPU laptop. Uses existing multi-modal substrate pipeline (PP-257).

### Anchor 4: AFFORDANCE-REPRESENTATION

Task: Store (object, action-type, agent-type) triples as structured vectors. Test
whether task-planning queries (given current object-context, retrieve applicable actions)
return appropriate action-type items at recall >= 0.65 on a 100-item held-out set.

Pre-reg:
  HARD-PASS: recall@5 >= 0.65 on action-retrieval given object-context queries.
  HARD-FAIL: recall@5 < 0.35 (chance for 10-class action taxonomy).
  MID-BAND: recall@5 in [0.35, 0.65] -- action retrieval requires finer-grained
            context encoding.

P_deflated = 0.50 (affordance triples are explicit; recall quality depends on
vector encoding quality of action-type semantics).

Tier: CPU laptop. Useful for robotics integration path.

### Anchor 5: HYBRID-ROBOTICS-SUBSTRATE

Task: Integration study -- connect a robotic platform (or simulation) providing
sensorimotor data (joint states, proprioception, contact forces) to the substrate
as the memory layer. The robot's NOW shard holds current sensorimotor state.
Test whether substrate-mediated episodic memory improves task performance on a
repeated-context navigation task vs. no memory.

Pre-reg:
  HARD-PASS: Task success rate (navigation to learned target) >= 0.80 vs. no-memory
             baseline <= 0.40 on a 20-trial repeated environment.
  HARD-FAIL: Task success rate with substrate <= no-memory baseline +0.10.
  MID-BAND: Improvement in [0.10, 0.40] -- memory helps but sensorimotor loop
            not yet constitutive of navigation strategy.

P_deflated = 0.35 (large integration surface; no prior empirical validation of
this pipeline; robotics simulation adds engineering overhead that may confound
memory-specific effects).

Tier: CPU simulation or physical robot. Depends on robotics platform availability.
This is the ONLY anchor that touches genuine sensorimotor loop territory -- all
others remain in the honest "multi-modal binding" category.

---

## Honest substrate position

### What substrate is:

A fast associative memory system with multi-modal binding, cross-modal retrieval,
schema-tagged episodic storage, and high-dimensional vector composition. It can store
and retrieve structured information that represents concepts, events, sensor readings,
and relational structures. It can be used as the memory component in larger cognitive
architectures.

### What substrate is NOT:

An embodied cognition system. The substrate has no body. It has no sensorimotor loop.
It has no developmental history of sensorimotor experience from which body schemas
emerge. It cannot form conceptual metaphors through accumulated bodily regularities.
It cannot represent affordances in Gibson's relational sense. It does not solve
Harnad's symbol grounding problem.

Adding sensor data to a NOW shard does not change any of these limitations. The shard
holds current environmental state as additional symbolic tokens. The symbol grounding
problem is not solved by attaching more symbols to existing symbols.

### The retractionstatement (plain language):

"Substrate with NOW shard and sensor data binding does not implement embodied cognition
in the Lakoff/Johnson/Barsalou/Varela/Gibson sense. The correct description is: the
substrate can serve as a multi-modal associative memory in a larger system that has
embodied components. When integrated with a robotic platform that provides a genuine
sensorimotor loop, the substrate can contribute to embodied cognitive architectures
as the memory layer. Standalone, it is a symbol system with multi-modal labels --
not a grounded cognitive system."

### Commercial framing that is honest:

"Multi-modal associative memory with schema-structured retrieval. Can integrate sensor
data, visual embeddings, and linguistic representations in the same memory space. Can
be used as the episodic memory component in robotic or simulation-based systems that
require fast, compositional memory with cross-modal access."

Not: "Solves embodiment." Not: "Achieves grounded cognition." Not: "Lakoff-Johnson
compliant."

---

## Cheap decisive test

Test: IMAGE-SCHEMA-CODEBOOK smoke.

Build a codebook of 10 image schemas (CONTAINER, PATH, BALANCE, FORCE, LINK,
NEAR-FAR, VERTICALITY, FULL-EMPTY, PART-WHOLE, CENTER-PERIPHERY). Tag 200 short
sentences with their primary schema. Store in substrate. Query with held-out sentences.
Measure schema-conditioned precision@5.

Decision rule:
- If precision >= 0.70: schema-structured retrieval is viable; proceed to METAPHOR-BINDING.
- If precision < 0.45: schema boundaries are not recoverable from substrate encodings;
  IMAGE-SCHEMA-CODEBOOK anchor is blocked; revisit schema definition methodology.
- If precision in [0.45, 0.70]: schema boundary refinement needed before further anchors.

Cost: 2-4 hours CPU. No cloud. No LLM fine-tuning. Pure substrate retrieval test.

---

## Falsifiable predictions

### HARD-PASS thresholds

HP-1: IMAGE-SCHEMA-CODEBOOK retrieval precision@5 >= 0.70 on 10-schema, 200-item
      held-out set. Constitutes: schema-conditioned retrieval is viable as a substrate
      capability.

HP-2: METAPHOR-BINDING recall@5 >= 0.60 on 50 cross-domain metaphor pairs spanning
      UP/WARMTH/CONTAINER source domains. Constitutes: metaphor-mediated retrieval
      transfer is achievable.

HP-3: Cross-modal (SENSOR-SYMBOL) recall@10 >= 0.75 vs. single-modal < 0.60 on
      matched evaluation set. Constitutes: multi-modal binding provides measurable
      retrieval advantage.

### HARD-FAIL thresholds

HF-1: IMAGE-SCHEMA-CODEBOOK precision < 0.45. Schema boundaries are not substrate-
      recoverable. Cap: schema-structured retrieval is not achievable without
      fundamentally different encoding.

HF-2: METAPHOR-BINDING recall@5 < 0.30. Metaphor-mediated transfer is not above
      chance. Cap: metaphor structure cannot be recovered via vector composition.

HF-3: HYBRID-ROBOTICS-SUBSTRATE task success rate improvement < 0.10 vs. no-memory
      baseline. Cap: substrate-as-memory provides no benefit in sensorimotor task
      context (refutes the robotics integration path).

---

## Cross-thread synthesis

Prior drills relevant to this retraction:

- CONTINUAL LEARNING: Stability-plasticity tradeoff and replay mechanisms are
  consistent with the NOW shard's role as episodic buffer -- the shard can feed
  replay without constituting grounding.

- MULTI-HOP RETRIEVAL: Multi-hop chains remain a purely symbolic retrieval problem.
  Embodiment is not relevant to multi-hop chaining quality.

- COMPOSITIONAL SHARD SYSTEM (v3.0): The compositional depth achievements are about
  symbolic binding and recall, not about embodiment. The v3.0 compositional cliff
  result stands independently of embodiment claims.

- CONFIDENCE AND CALIBRATION: Confidence estimation is a calibration problem over
  symbolic retrieval, not an embodied cognition problem.

The overclaim does not invalidate any of the above findings. It narrows the product
claim: "substrate as embodied memory" -> "substrate as multi-modal associative memory,
suitable for integration into embodied systems."

---

## Substrate-product implications

1. Retract the "embodied cognition" framing from all product documentation and
   demos. Replace with "multi-modal associative memory."

2. Robotics integration (HYBRID-ROBOTICS-SUBSTRATE) is the genuine path to the
   embodied-adjacent claim. This requires a robot or simulation partner.

3. IMAGE-SCHEMA-CODEBOOK is the nearest achievable anchor that adds meaningful
   cognitive structure beyond raw multi-modal binding. It is honest and useful.

4. Affordance representation (explicit object-action triples) is useful for planning
   without claiming Gibson-style ecological affordance.

5. The embodiment overclaim, if it reaches customers, creates a credibility risk when
   researchers or technically sophisticated customers test the claim. Early retraction
   protects the product.

---

## Citations (verified in lit-scan)

1. Lakoff, G. and Johnson, M. (1999). Philosophy in the Flesh: The Embodied Mind and
   Its Challenge to Western Thought. Basic Books.

2. Johnson, M. (1987). The Body in the Mind: The Bodily Basis of Meaning, Imagination,
   and Reason. University of Chicago Press.

3. Barsalou, L. (1999). Perceptual Symbol Systems. Behavioral and Brain Sciences, 22,
   577-609.

4. Varela, F., Thompson, E., and Rosch, E. (1991). The Embodied Mind. MIT Press.

5. Gibson, J.J. (1979). The Ecological Approach to Visual Perception. Houghton Mifflin.

6. Harnad, S. (1990). The Symbol Grounding Problem. Physica D, 42, 335-346.

7. Glenberg, A. and Kaschak, M. (2002). Grounding language in action. Psychonomic
   Bulletin and Review, 9(3), 558-565.

8. Pulvermuller, F. (2005). Brain mechanisms linking language and action. Nature Reviews
   Neuroscience, 6, 576-582.

9. Clark, A. and Chalmers, D. (1998). The Extended Mind. Analysis, 58(1), 7-19.

10. Talmy, L. (2000). Toward a Cognitive Semantics. Vol. 1. MIT Press. (Force dynamics
    and image schemas.)

11. Maturana, H. and Varela, F. (1987). The Tree of Knowledge. Shambhala Publications.

12. Coenen, T. et al. (2023). The Vector Grounding Problem. arXiv:2304.01481.
    (Extension of Harnad to vector embedding spaces.)

13. Barsalou, L. (2008). Grounded Cognition. Annual Review of Psychology, 59, 617-645.

14. Barsalou, L. (2020). Challenges and Opportunities for Grounding Cognition. Journal
    of Cognition, 3(1), 31.

Verified count: 14 sources. All accessed via lit-scan 2026-06-10.

---

## P_deflated summary

| Anchor                      | Raw P  | Calibration | P_deflated |
|-----------------------------|--------|-------------|------------|
| IMAGE-SCHEMA-CODEBOOK       | 0.75   | -0.20       | 0.55       |
| METAPHOR-BINDING            | 0.60   | -0.20       | 0.40       |
| SENSOR-SYMBOL-CO-OCCURRENCE | 0.80   | -0.20       | 0.60       |
| AFFORDANCE-REPRESENTATION   | 0.70   | -0.20       | 0.50       |
| HYBRID-ROBOTICS-SUBSTRATE   | 0.55   | -0.20       | 0.35       |

Novel-synthesis cap: 0.50 applied where raw P > 0.50 for novel mechanisms.
P_deflated for the central retraction claim (overclaim identified, correct retraction
warranted): 0.95 -- this is not a contested empirical finding but a direct reading of
the Lakoff/Johnson/Harnad/Gibson literature against the stated mechanism.

---

next-drill candidate: SENSOR-SYMBOL-CO-OCCURRENCE smoke (IMAGE-SCHEMA-CODEBOOK is the
cheap decisive test; ship it first)
