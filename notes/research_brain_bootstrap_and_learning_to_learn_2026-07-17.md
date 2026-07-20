# How the brain bootstraps from near-nothing, and learns to learn better (2026-07-17)

Deep drill, developmental neuroscience + cognitive science, biology-led. Dispatched as a direct topic
statement (no routing file); grounded against `research_field_advisor.py` output (physics/spin-glass
adjacency map — not directly relevant to this biology drill, noted for completeness) and against
same-day threads `research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md`,
`research_discourse_state_of_mind_situation_model_2026-07-17.md`,
`consolidation_to_structure_implementable_algorithm_2026-07-14.md`,
`exp_dev_handoff_research_gap3_brain_slow_schema_mechanism_2026-06-26.md`, and
`exp_dev_handoff_research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md`. 4 parallel Sonnet
lit-scan sub-agents dispatched (one per angle below); this doc is the Opus synthesis.

## HEADLINE

The brain does not bootstrap from a blank slate and does not have one "learn to learn" mechanism — it
runs roughly EIGHT distinct, independently-evolved sub-mechanisms that compose into two families: (1)
bootstrap family — a small number of encapsulated INNATE core-knowledge kernels (Spelke) get
STAGED/THROTTLED exposure (Elman starting-small, Hensch critical periods) driven by SELF-SUPERVISED
prediction error (Friston/VOE) and a domain-general STATISTICS TRACKER (Saffran), with the child's own
body (Smith/Adolph) and caregiver (Vygotsky/Fernald) actively generating/shaping the training-data
curriculum; (2) learn-to-learn family — a NESTED hierarchy of learning-rate-of-the-learning-rate
controllers (BCM metaplasticity at the synapse, Behrens/Yu-Dayan volatility-tracking at the systems
level, Tse/van Kesteren schema-match gating at the systems-consolidation level) sits ON TOP OF a
structure/content-factorized memory architecture (McClelland CLS, Whittington/Behrens TEM grid-code)
that is what actually lets compressed abstractions (Lake/Tenenbaum, Bernardi geometry) transfer
zero-shot and makes EACH SUCCESSIVE learning problem cheaper (Harlow learning-sets, Baxter's formal
inductive-bias-learning bound). The compounding/"gets better at learning" effect is not mystical — it
is the literal, measurable shrinking of hypothesis space / sample complexity as structure accumulates.
Directly convergent with two already-banked substrate threads: `consolidation_to_structure` (07-14,
independently arrived at CLS+TEM as the manufacture-structure algorithm) and the gap3 BCM hand-off
(06-26, already proposed BCM sliding-threshold as the write-rule) — this drill supplies THREE new load-
bearing levers those threads did not yet have: (i) volatility-ADAPTIVE learning rate as a first-class
control signal distinct from the BCM local rule, (ii) a contested-not-settled curriculum/starting-small
principle directly testable on the substrate's own construction-inventory growth, and (iii) Carey's
Quinian-bootstrapping mechanism for genuinely NEW representational primitives (relevant to any future
quantity/number handling).

## Part 1 — Developmental bootstrap (near-nothing -> competent)

### 1a. Critical/sensitive periods (Hensch; Hubel & Wiesel)
Hubel & Wiesel's monocular-deprivation paradigm (1963-70s) is the founding empirical result: a defined
plasticity window (peak ~4 wk in kittens) during which brief deprivation permanently reallocates
cortical territory; closure is normally irreversible. Hensch (Nat Rev Neurosci 2005 +) identified the
OPENING trigger as maturation of parvalbumin-positive GABAergic circuits crossing an inhibition
threshold, and the CLOSING mechanism as accumulating molecular "brakes" — Lynx1, perineuronal nets,
PSA-NCAM loss, NogoR/myelin inhibitors. Critically, closure is a MAINTAINED, REMOVABLE lock, not lost
capacity: chondroitinase ABC (degrading perineuronal nets), Lynx1 blockade, or Otx2-disruption
demonstrably reopen juvenile-like plasticity in adult cortex.
**Transferable principle:** gate plasticity via an explicit, addressable "lock" state that is applied
AFTER structure stabilizes and can be deliberately released — not an unrecoverable architecture change.
Separates "decision to stop learning" from "capacity to learn."

### 1b. Starting small / curriculum (Elman 1993; contested by Rohde & Plaut 1999; Bengio 2009)
Elman's simple-recurrent-network result: networks given full-capacity working memory from the start
FAILED to learn complex embedded-clause grammar; networks whose memory span (or whose training-data
complexity) was throttled early and relaxed on a schedule succeeded. Bengio et al. (ICML 2009)
generalized this into modern curriculum learning (easy-to-hard example ordering), explicitly citing
Elman, framing it as a continuation method that avoids poor local optima in non-convex loss landscapes.
**This is a live, NOT-settled debate**: Rohde & Plaut (1999) directly replicated and found full-capacity-
from-the-start networks did BETTER, arguing the original result was an artifact of premature training
termination. The principle survives in modern ML curriculum learning generally but the original
"immaturity helps" developmental claim is contested.
**Transferable principle:** constrain capacity/complexity early and relax on a schedule — CONTESTED,
must be tested per-architecture, not assumed.

### 1c. Prediction as the infant learning engine (Friston; VOE paradigms)
Free-energy / predictive-processing accounts argue infants use self-supervised next-observation
prediction error, before any reward/supervision exists — evidenced by violation-of-expectation
looking-time paradigms (infants look longer at physically/statistically impossible outcomes) and EEG/
theta-band work showing neural response magnitude scales with stimulus unexpectedness by ~12 months.
**Caveat:** recent work (2026, Developmental Science) found no domain-general violation-of-expectation
effect in pupillary response at 9-10 months — the "one unified prediction-error mechanism" claim may be
too strong; effects may be domain/paradigm-specific.
**Transferable principle:** use prediction-error magnitude as BOTH the sole pre-supervision training
signal AND an attention/resource-allocation gate (surprising events get more processing).

### 1d. Statistical/distributional learning (Saffran, Aslin & Newport 1996/1998)
8-month-olds extract word boundaries from 2 minutes of continuous, cue-free synthetic speech using only
transitional-probability differences (higher within- than between-word syllable pair statistics) —
genuine conditional-probability computation, not raw frequency (Aslin/Saffran/Newport 1998). Generalizes
beyond speech: visual sequential statistical learning from 2-5 months, cross-situational word-object
mapping. Known limits: pure transitional-probability tracking under-performs on longer/naturalistic
words and does not by itself explain full vocabulary growth without social/interactive input; infants
sometimes chunk holistically rather than via raw TP.
**Transferable principle:** a domain-general, modality-agnostic co-occurrence/transitional-probability
tracker bootstraps segmentation/structure discovery from minimal unsupervised exposure — a generic
first-pass chunker, with known ceiling effects that require a second mechanism to clear.

### 1e. Core knowledge + Quinian bootstrapping (Spelke; Carey 2009)
Spelke's core-knowledge systems (~5, each fast/automatic/domain-restricted, validated via VOE): objects
(cohesion/continuity/solidity), number (small-N exact parallel-individuation via the object-tracking
system, max ~3-4, PLUS a separate large-N approximate ratio-scaled magnitude system — a genuine double
system, not one unified magnitude code), geometry/navigation, agents/goal-directedness, social partners.
Carey's *Origin of Concepts* (2009) mechanism for how genuinely NEW concepts (e.g. exact integers) arise
from these encapsulated kernels — "Quinian bootstrapping": build an externally-imposed PLACEHOLDER
structure with purely relational content (the count-list "one, two, three..." meaningful only via its
stable order), then iteratively INFUSE it with content by binding placeholders onto core-system outputs
(object-tracking supplies the first few exact cardinalities) via explicit analogy-construction,
abduction, and mutual-consistency checking, until the placeholder structure's content outstrips what any
one core system alone could represent (the successor function generalizes past the object-tracking
system's ~4-item ceiling). **Debate:** the "deviant interpretation" problem (Rips, Beck) — nothing
in the mapping process guarantees the numeral list gets bound to CARDINALITY specifically rather than
some other invariant of the parallel-individuation states — is not fully resolved.
**Transferable principle:** to genuinely EXCEED an existing core primitive's ceiling, don't extend the
primitive — build a separate relational-only placeholder scaffold and bind it to the primitive via
explicit analogy/consistency operators until it inherits and then exceeds the primitive's content.

### 1f. Poverty of stimulus (Chomsky vs Tomasello; corpus-statistics rebuttals)
Chomsky's poverty-of-stimulus argument for innate Universal Grammar vs Tomasello's usage-based
construction-grammar account (bottom-up, item-based constructions via intention-reading/joint
attention/analogy) vs the connectionist reframing (Elman/Bates/Karmiloff-Smith, *Rethinking
Innateness* 1996 — innateness as emergent from architectural/timing constraints, not symbolic content).
Empirically, Pullum & Scholz (2002) showed child-directed corpora contain far more disambiguating
sentence types than Chomsky assumed; Perfors, Tenenbaum & Regier (~2011) showed Bayesian model-selection
over realistic corpora recovers structure-dependence without an innate rule. **Live synthesis position**
(Yang, Ambridge and others): some abstract mild bias (e.g. a preference for hierarchical/compact
structure) plus mostly usage-derived construction-level grammar — a hybrid "constrained statistical
learner," not a clean win for either pole.
**Transferable principle:** before positing an innate architectural bias, first measure whether generic
statistical learning over the REALISTIC (not idealized-sparse) input distribution already suffices —
the poverty-of-stimulus premise is frequently an artifact of underestimating the input's richness.

### 1g. Sensorimotor grounding as curriculum generation (Smith; Adolph)
Smith, Jayaraman, Clerkin & Yu (2018, head-camera studies): infant posture/reach/gaze control physically
determines which visual data reach the learner, producing a skewed, self-selected training curriculum
(massive repeated close-up single-object views) unlike a generic fixed corpus. Adolph's causal-
manipulation locomotion studies (crawling->walking transition) show a NEW motor milestone causally
changes visual access, object-interaction rate, and caregiver language input — independent of age.
**Transferable principle:** the acting/querying component of a learner is a first-class DATA-GENERATING
component (it determines the curriculum), not merely a downstream consumer of a fixed dataset.

### 1h. Scaffolding (Vygotsky ZPD; Wood/Bruner/Ross 1976; Fernald)
Vygotsky's Zone of Proximal Development + Wood/Bruner/Ross's 1976 operationalization ("scaffolding": a
More Knowledgeable Other provides contingent, graduated support withdrawn as competence grows). Fernald's
cross-linguistic infant-directed-speech (IDS) work: exaggerated F0/pitch range, slower rate, longer
pauses across languages; ERP work shows IDS specifically enhances statistical word-segmentation
learning relative to adult-directed speech. **Caveat:** whether the benefit is attentional/affective vs
genuinely statistical-learning-enhancing is still debated.
**Transferable principle:** an external teacher can boost effective sample efficiency by adaptively
EXAGGERATING/AMPLIFYING discriminative signal statistics and difficulty-matching to current competence —
a distinct lever from the learner simply getting more raw data.

## Part 2 — Learning to learn better (meta-learning IN the brain)

### 2a. Metaplasticity: BCM sliding threshold (Bienenstock-Cooper-Munro 1982; Kirkwood/Rioult/Bear 1996)
BCM theory: a synapse's own LTP/LTD threshold slides as a function of the neuron's RECENT time-averaged
postsynaptic activity (high recent activity -> raised threshold, harder to potentiate further; low
recent activity -> lowered threshold, easier to potentiate). Experimentally confirmed in rat visual
cortex (dark-rearing lowers the threshold and facilitates subsequent LTP exactly as predicted).
**Transferable principle:** effective learning rate/threshold should be a per-unit STATE VARIABLE,
continuously re-estimated from a LOCAL running average of recent activity — a homeostatic, purely
local meta-learning-rate mechanism requiring no global signal.

### 2b. Volatility-adaptive learning rate (Behrens et al. 2007; Yu & Dayan 2005)
Behrens et al. (Nat Neurosci 2007): humans behave like Bayesian learners whose effective learning rate
tracks estimated environmental VOLATILITY (rate of contingency change) — anterior cingulate BOLD signal
tracked estimated volatility and predicted each subject's learning rate. Yu & Dayan (Neuron 2005)
proposed the neuromodulatory split: acetylcholine signals "expected uncertainty" (known within-context
stochasticity, boosts ordinary learning), norepinephrine signals "unexpected uncertainty" (context
change/outlier, triggers a fast belief-and-learning-rate RESET) — a Kalman-filter view of learning rate
as inferred process noise. **Caveat:** whether ACh/NE genuinely implement this clean dichotomy is
debated; NE may reflect broader arousal/surprise.
**Transferable principle:** a SYSTEM-LEVEL (not per-unit) running estimate of environmental change-rate
should independently scale the effective learning rate — a second, non-local meta-learning-rate signal
distinct from BCM's local-activity-history signal.

### 2c. Schema-accelerated learning / fast-track gating (Tse et al. 2007/2011; van Kesteren SLIMM)
Tse et al. (Science 2007): once rats learn a flavor-place paired-associate SCHEMA over weeks, genuinely
NEW schema-consistent pairs consolidate to neocortex- (hippocampus-independent) in as little as 48
hours instead of the normal weeks-long timescale, sometimes in one trial. Tse et al. (Science 2011):
schema-consistent learning drives rapid immediate-early-gene expression and dendritic remodeling
specifically in prelimbic mPFC; pharmacological block of that region prevents both the new learning and
recall of even recently-consolidated schema memories — mPFC is CAUSALLY necessary, not merely
correlated. Van Kesteren et al.'s SLIMM model: schema-CONGRUENT input activates mPFC, which SUPPRESSES
hippocampal engagement and routes to fast neocortical encoding; schema-INCONGRUENT input fails to
activate mPFC and must take the slow hippocampal route. **Caveat:** rodent-scale effect (48h) is much
larger than reported human replications; whether mPFC pre-activation PREDICTS vs merely facilitates
fast consolidation is still debated.
**Transferable principle:** a match-detector compares incoming information against the existing
generative model; MATCH routes to a fast/high-instantaneous-learning-rate path (conditionally gated by
top-down predictive fit), MISMATCH routes to a slow high-capacity buffer for gradual replay-based
integration. This is a THIRD, distinct meta-learning-rate mechanism — gated by content-model fit, not
activity history (2a) or environmental change-rate (2b).

### 2d. Reward/novelty tagging (Frey & Morris 1997 synaptic tagging-and-capture; Lisman & Grace 2005)
A weak learning event sets a transient synaptic "tag" that can later CAPTURE plasticity-related proteins
triggered by an unrelated strong/salient/novel event within a time window, converting a transient trace
into a persistent one ("behavioral tagging"). Lisman & Grace's hippocampal-VTA loop: hippocampal novelty
detection disinhibits VTA dopamine release back into hippocampus, retroactively boosting persistence of
recently-tagged material.
**Transferable principle:** a delayed, broadcast, GLOBAL novelty/reward signal can retroactively boost
persistence of memory traces tagged as significant within a time window — a third-factor (eligibility-
trace-style) rule distinct from 2a-2c.

### 2e. Unifying account (Wang et al. 2018 meta-RL; Khorsand & Soltani 2017)
Wang, Kurth-Nelson, Kumaran et al. (Nat Neurosci 2018): training a recurrent PFC-like network with SLOW
dopaminergic RL gives rise to an EMERGENT fast learning algorithm implemented purely in the network's
activity dynamics — reproducing volatility-adaptive rates and multi-task speedup without any explicit
meta-learning-rate module being hand-built. Khorsand & Soltani formalize an optimal metaplastic
"reservoir vs buffer" state-machine resolving the fast-adaptability/precision tradeoff — structurally
identical to CLS's fast-cortical-schema vs slow-hippocampal-buffer split (Part 3 below). No single
confirmed formal theory spans 2a-2d yet — this is a cross-literature synthesis, not one established
result: in every case, a SLOWER process learns the hyperparameters (rate/threshold/gate) governing a
FASTER process — a genuine nested learning-rate-of-the-learning-rate architecture.

## Part 3 — Abstraction, structure/content factorization, and the compounding effect

### 3a. Abstraction/compression enabling one-shot transfer (Lake/Salakhutdinov/Tenenbaum 2015; Bernardi et al. 2020)
Bayesian Program Learning (Lake et al., Science 2015): handwritten characters represented as generative
programs composed from REUSED primitive strokes plus a learned prior over composition, achieving
human-level one-shot classification/generation where contemporary deep nets needed hundreds of examples.
Bernardi et al. (Cell 2020): PFC/hippocampal populations encode task variables in a specific geometry
where a linear decoder trained on SOME conditions generalizes to UNTRAINED condition combinations
("cross-condition generalization performance," CCGP) — a concrete, measurable computational signature
of what "abstraction enabling transfer" looks like at the population level, while the SAME population
retains high-dimensional flexible (nonlinear mixed-selectivity) coding elsewhere.
**Transferable principle:** data efficiency comes from decomposing novel input into previously-learned
reusable primitives plus a generative prior over composition; CCGP-style cross-condition decodability
is a concrete test for whether a representation has actually achieved this.

### 3b. Cognitive maps / structure-content factorization (Whittington/Behrens TEM 2020; Constantinescu et al. 2016)
The Tolman-Eichenbaum Machine: entorhinal grid-like cells encode a domain-general STRUCTURAL/relational
code (learned once, content-independent) that hippocampal place cells then bind to sensory CONTENT;
TEM formally derives grid-like coding as the OPTIMAL factorization for generalizing relational structure
across different content. Constantinescu, O'Reilly & Behrens (Science 2016): the same hexagonal grid
signature appears in fMRI during purely CONCEPTUAL 2D navigation (not physical space) — direct evidence
the structural code is genuinely domain-general, not spatial-specific.
**Transferable principle:** learn structure ONCE as a reusable, content-independent scaffold; new
content sharing the same relational structure only needs to be BOUND to the existing scaffold, not
relearned from scratch — zero-shot transfer to new content within a known structure class. This is the
direct biological precedent for "reusable scaffold separate from content," already the substrate's
09-14 primary framing.

### 3c. Complementary Learning Systems / systems consolidation (McClelland/McNaughton/O'Reilly 1995; Kumaran/Hassabis/McClelland 2016)
Hippocampus = fast, sparse, one-shot episodic learner; neocortex = slow learner extracting statistical
structure ONLY when new items are interleaved with old during replay (rapid neocortical learning of new
material alone causes catastrophic interference in connectionist models). Kumaran/Hassabis/McClelland's
AI update explicitly identifies deep-RL experience-replay buffers as a direct computational
implementation of hippocampal replay solving catastrophic interference, notes replay can be
prioritized/reweighted by reward or novelty. **Caveat:** whether biological replay is literally uniform
random-interleaved vs prioritized/generative/schema-based is actively debated; interference-avoidance
and structure-extraction may be more separable objectives than the 1995 model assumed.
**Transferable principle:** catastrophic forgetting is a DATA-SCHEDULING problem (fast orthogonal store
decoupling acquisition timing from integration timing, interleaved slow consolidation) — not merely a
learning-rate problem.

### 3d. Compounding / representational readiness (Harlow 1949; Carey & Bartlett 1978; Baxter 2000)
Harlow's classic "learning set" result: monkeys solving 344 sequential two-object discrimination
problems went from near-chance to near-ceiling performance on NOVEL problems by the ~200th problem —
they extracted a general win-stay/lose-shift STRATEGY, literally becoming better learners from
cumulative experience (not learning any single discrimination better). Carey & Bartlett's fast-mapping
study: a large-enough existing lexicon lets a NEW word be inferred by exclusion/contrast in one
incidental exposure rather than requiring full ostensive teaching — though follow-up work (Horst &
Samuelson 2012) shows the fast-mapped trace is initially FRAGILE and needs further slow consolidation
("fast mapping, slow learning" — reconciles with 3c). Baxter (2000, formal ML theory): when a learner
samples from an environment of RELATED tasks and selects a shared hypothesis space, the sample
complexity required for each NEW task provably DECREASES as the number of already-learned tasks
increases (a formal inductive-bias-learning bound, not just an empirical trend).
**Transferable principle:** earlier learning episodes are not merely stored facts — they get folded
into a reusable higher-order object (a strategy, a contrast set, a constrained hypothesis space) that
provably shrinks the sample complexity of the NEXT problem. This is the literal, formalizable mechanism
behind "gets better at learning over time," not a vague analogy.

## Cheap decisive test

Directly pluggable onto the substrate's ACTIVE construction-inventory / entrenchment-driven parser
growth (07-17 thread): test the CONTESTED starting-small/curriculum principle (1b) on the substrate's
own foundation-builder, since it is (i) cheap — a training-ORDER change on existing machinery, no new
component, (ii) genuinely undecided in the literature (Elman positive vs Rohde & Plaut negative), so
not a foregone conclusion, and (iii) directly informs the imminent "textbook ingestion" waypoint (does
ingestion ORDER matter, or is it exposure-count-only?).

Design sketch (exp_dev to own the exact spec): three arms over the same corpus and same total exposure
budget — (A) UNRESTRICTED: full corpus complexity + full working-memory/context span from pass 1;
(B) STARTING-SMALL: restrict sentence/construction complexity (or context span) early, relax on a
schedule to match (A) by the final pass; (C) REVERSE-ORDER control (hard-to-easy) to rule out "any
non-uniform ordering helps" as a confound. Measure held-out construction-inventory quality (coverage +
compositional-generalization delta) at matched total exposure.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

All P estimates deflated 0.15-0.25 per lit-scan calibration penalty; novel-synthesis items capped at 0.50.

**Prediction 1 (curriculum/starting-small transfers to the substrate parser).**
HARD-PASS: arm (B) beats arm (A) on held-out compositional-generalization by >=15% at matched total
exposure, AND arm (C) does not (ruling out "any ordering helps"). HARD-FAIL: (A) >= (B) within noise,
or (C) matches (B) (ordering-agnostic). MIDDLE: (B) beats (A) but (C) also beats (A) comparably.
P_deflated = 0.30 (genuinely contested in source literature — Rohde & Plaut is a real, unresolved
counter-finding, not a weak caveat).

**Prediction 2 (schema-match gating speeds integration of congruent facts — extends gap3 anchor).**
HARD-PASS: routing schema-congruent new facts through a fast/high-eta path (vs uniform slow
consolidation) achieves equivalent retrieval accuracy in <=1/5 the consolidation passes, with NO
degradation on schema-incongruent material routed to the existing slow path. HARD-FAIL: fast-path
congruent routing shows no pass-count advantage, or degrades incongruent-material handling (cross-talk).
P_deflated = 0.40 (mechanism already partially anchored in gap3 hand-off as MEASURED_MECHANISM-eligible;
this drill adds the SLIMM congruent/incongruent GATE as the missing routing rule, not a new primitive).

**Prediction 3 (volatility-adaptive eta_slow beats fixed eta_slow under regime change).**
HARD-PASS: on a stream with a stable period then an abrupt regime change, a volatility-estimator-scaled
eta_slow reaches the new-regime steady-state accuracy in <=1/2 the passes of best fixed-eta_slow,
without degrading stable-period accuracy by more than 10%. HARD-FAIL: volatility-adaptive eta shows no
speed advantage after the regime change, or costs >10% stable-period accuracy for that speed.
P_deflated = 0.30 (capped: this is a genuinely novel-synthesis composition — no direct precedent
combines Behrens/Yu-Dayan volatility-tracking with the substrate's existing BCM write-rule).

## Cross-thread synthesis

- **Strong convergence, not contradiction:** `consolidation_to_structure_implementable_algorithm_2026-07-14`
  independently arrived at CLS (McClelland 1995) + TEM (Whittington 2020) as the "manufacture structure"
  algorithm; this drill's Part 3 supplies the SAME two anchors from a fresh lit-scan with two additional
  named results (Constantinescu 2016 fMRI hexagonal-in-concept-space, Bernardi 2020 CCGP measurement
  criterion) that give that thread a concrete, testable operationalization of "abstraction" it did not
  have (CCGP as the abstraction signature).
- **Extends gap3 (`exp_dev_handoff_research_gap3_brain_slow_schema_mechanism_2026-06-26`):** that
  hand-off already proposed BCM sliding-threshold as the write-rule (ANCHOR_1). This drill's 2c (Tse/
  van Kesteren SLIMM) supplies the missing GATING rule (congruent vs incongruent routing) that ANCHOR_1
  did not fully specify, and 2b (Behrens volatility) supplies an entirely separate, ADDITIONAL lever
  (system-level adaptive eta) that composes with, rather than replaces, the local BCM rule — three
  nested meta-learning-rate mechanisms (2a local, 2b systems-volatility, 2c schema-gate), not one.
- **Extends `exp_dev_handoff_research_innate_scaffolding_core_knowledge_kernel_2026-07-09`:** that note
  already drilled Spelke's number double-dissociation as anchor 1. This drill adds Carey's Quinian-
  bootstrapping MECHANISM (1e) for how a system could exceed a core primitive's ceiling via an
  externally-imposed placeholder + analogy-binding — relevant if/when the substrate needs a genuinely
  NEW representational primitive (e.g., exact-quantity handling beyond a fixed small-N pointer array).
- **Feeds the roadmap** (`project_roadmap_to_conversational_substrate...2026-07-17`): curriculum/
  starting-small (1b) bears directly on textbook-ingestion ORDER; sensorimotor-grounding-as-curriculum
  (1g) reframes the substrate's OWN query/parse policy as a curriculum-generating component once
  discourse "state of mind" exists (the substrate's attention/parse choices determine what training
  signal it receives next — same principle Smith documented for infant gaze control).

## Substrate-product implications

(Per no-papers-product-only: framed as build decisions, never as publication targets.)

1. **Plasticity lock/unlock as an explicit state, not implicit decay** (1a): once a construction-
   inventory region stabilizes, freeze it deliberately (addressable lock) rather than letting gradient
   updates silently keep drifting it — but keep an explicit UNLOCK path for deliberate major schema
   revision, mirroring Hensch's removable molecular brakes rather than true architectural loss.
2. **Curriculum/exposure-order as a first-class textbook-ingestion hyperparameter** (1b, cheap decisive
   test above) — currently an implicit afterthought; the literature says it MAY matter a lot or not at
   all (contested), so it needs an actual test before the textbook-ingestion waypoint scales up, not an
   assumption either way.
3. **A schema-match gate at write time** (2c) — route congruent new facts through a fast high-LR path,
   incongruent facts through the existing slow interleaved-replay path; directly buildable on top of the
   existing gap3 BCM write-rule as the missing routing layer.
4. **A volatility estimator driving eta_slow** (2b) — a genuinely new, second control signal (distinct
   from BCM's local-activity-history signal) worth prototyping once the schema-gate (item 3) exists,
   since the two compose (schema-match decides WHICH path; volatility decides HOW FAST within a path).
5. **Quinian-bootstrapping placeholder mechanism** (1e) — held in reserve for whenever the substrate
   needs a representational primitive that must genuinely EXCEED an existing core module's ceiling
   (e.g., exact large-quantity handling beyond a fixed small-N pointer array); not immediately actionable
   but worth naming now so it isn't rediscovered from scratch later.
6. **Treat the substrate's own query/parse policy as a curriculum generator** (1g), once discourse
   state-of-mind exists — what the substrate chooses to attend to/query next determines its own future
   training data, exactly as infant gaze/posture control does; this is a design lever, not just an
   observation, once the substrate has any autonomous read/query loop.
7. **CCGP (cross-condition generalization performance) as a concrete abstraction metric** (3a) — a
   ready-made, literature-grounded test for whether the additive-map / construction codes have actually
   achieved reusable abstraction, usable immediately without waiting on any new build.

## Citations (verified count)

48 distinct named findings/papers surfaced across 4 parallel Sonnet lit-scan sub-agents, each returning
live WebSearch/WebFetch-sourced URLs (not fabricated) — Hensch critical-period reviews; Hubel & Wiesel;
Elman 1993; Bengio et al. 2009; Rohde & Plaut 1999; Friston/predictive-processing-infancy reviews;
Saffran/Aslin/Newport 1996 + 1998; visual/cross-situational statistical-learning studies; Spelke core-
knowledge (2000/2007/2022); Baillargeon VOE paradigms; Carey 2009 + 2021; Rips/Beck critiques; Chomsky
1980; Tomasello 2003; Elman/Bates/Karmiloff-Smith 1996; Pullum & Scholz 2002; Reali & Christiansen 2005;
Perfors/Tenenbaum/Regier ~2011; Smith et al. 2018; Adolph et al. 2012/Kretch et al.; Wood/Bruner/Ross
1976; Fernald & Kuhl 1987; Fernald et al. 1989; Thiessen et al. 2005; IDS-ERP 2016; BCM 1982; Kirkwood/
Rioult/Bear 1996; Behrens et al. 2007; Yu & Dayan 2005; Tse et al. 2007 + 2011; van Kesteren et al.
2012/2013 (SLIMM); Frey & Morris 1997; Lisman & Grace 2005; Wang et al. 2018; Khorsand & Soltani 2017;
Lake/Salakhutdinov/Tenenbaum 2015; Bernardi et al. 2020; Whittington et al. 2020 (TEM); Constantinescu/
O'Reilly/Behrens 2016; McClelland/McNaughton/O'Reilly 1995; Kumaran/Hassabis/McClelland 2016; Harlow
1949; Carey & Bartlett 1978; Horst & Samuelson 2012; Baxter 2000. All verified as real, dated,
attributable results by the sub-agents' own tool calls (WebSearch + WebFetch against primary/secondary
sources); none invented by the synthesizing (Opus) pass. No substrate-specific terms were sent to any
external query (generic developmental-neuroscience/cognitive-science search terms only), consistent
with query-privacy decomposition.
