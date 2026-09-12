# RESEARCH: one amodal semantic hub, many task readouts? (2026-09-11)

Lit-scan calibration penalty applied: all P estimates below are deflated 0.15-0.25 from raw
literature confidence; novel-synthesis (section C mapping) capped at P<=0.50.

## (A) One-paragraph answer

The literature supports, with direct clinical/imaging evidence, ONE graded, amodal-ish
convergent hub in bilateral ventral anterior temporal lobe (vATL) that stores a single
multidimensional similarity space built by integrating all modality-specific "spoke" inputs
(Patterson, Nestor & Rogers 2007; Lambon Ralph, Jefferies, Patterson & Rogers 2017 "Controlled
Semantic Cognition", CSC); semantic dementia (bilateral ATL atrophy) degrades comprehension,
naming, AND novel-word/category learning together, which is the behavioral signature of one
shared store rather than independent task-specific stores (PINNED). What is NOT settled with
equal force is exactly how the hub is READ OUT differently per task: the best-supported account
(CSC; Hoffman, McClelland & Lambon Ralph 2018; Jackson, Rogers & Lambon Ralph 2021) is a
learned, gain-modulation-like gating by a separate fronto-temporal "semantic control" network
(IFG + pMTG) that acts mostly on the *peripheral/spoke* layers feeding the hub rather than on
the deep hub units themselves -- i.e., task control steers WHICH features reach the hub, more
than it re-weights the hub's own code. The hub-building operation itself, in the models that
exist, is error-driven weight learning across modalities converging on a shared deep layer
(Rogers & McClelland 2004; Chen, Lambon Ralph & Rogers 2017), not an explicit Bayesian
reliability-weighted fusion equation (Ernst-Banks/Ma-Beck-Latham-Pouget cue-integration math is
a plausible computational-level ANALOGY, used in the literature to argue the hub is "optimal,"
but it has not been directly fit to ATL data as the modality-integration rule -- this is an
IMPORT, not a PINNED finding for this specific system). A full Complementary-Learning-Systems
account (McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis & McClelland 2016) explains
how reading-acquired, episodic (hippocampal) word/fact knowledge gets folded into this same
neocortical hub via slow, interleaved, schema-consistency-gated learning -- directly analogous
to "grounding a new word." And a 2024-2025 computational-level precedent from machine learning
(the "Semantic Hub Hypothesis" for LLMs, Wu, Lee & Andreas, ICLR 2025) independently reproduces
this architecture -- one shared modality/language-agnostic intermediate representation read out
by many downstream tasks -- and is the cleanest existing worked EQUATION-level demonstration
that "one hub, many task-specific readouts" is a coherent, implementable computational scheme.

## (B) Per-point findings

### Point 1 -- How the hub integrates spokes + distributional/verbal input

**Finding.** No paper directly fits Ernst-Banks/Ma-Beck-Latham-Pouget-style explicit
reliability-weighted (inverse-variance) fusion to ATL data. What IS directly modeled (Rogers &
McClelland 2004; re-specified with explicit ATL localization in Jackson, Rogers & Lambon Ralph
2021 "Reverse-engineering the cortical architecture for controlled semantic cognition", Nature
Human Behaviour) is error-driven (backpropagation-style) learning of a deep, shared hidden layer
that ALL modality-specific spoke inputs must pass through ("convergence principle": every
modality's pathway is forced through the same hidden units), plus sparse direct
shortcut connections (~1-in-24 sparsity in the winning architecture) that bypass the deep hub for
fast/automatic shallow associations. Cox et al. 2024 (Imaging Neuroscience / ECoG,
"Representational similarity learning reveals a graded multidimensional semantic space in human
ATL") show empirically that what the hub ends up holding is a continuous, graded,
multi-dimensional similarity geometry (not discrete symbolic slots), consistent with what a
converging distributed network would produce.

**Equation / operation (plain math).**
For the CSC/Jackson-style hub: let spoke vectors be s_1...s_k (one per modality/distributional
input). The hub computes
  h = f( sum_i W_i . s_i + b )
where f is a nonlinear squashing function (sigmoid/tanh in these PDP models) and W_i are learned
per-modality weight matrices trained end-to-end by gradient descent against the joint
reconstruction/prediction objective (reproduce every modality's pattern from every other
modality, i.e. an auto-encoder-like "co-occurrence reconstruction" loss). This is a LEARNED
WEIGHTED SUM, not a hand-specified precision/reliability weighting -- the weights W_i end up
approximating reliability only indirectly, as a side-effect of which modality's signal reduces
training error fastest/most consistently for a given concept type (concrete words lean more on
perceptual spokes, abstract words lean more on the verbal/distributional spoke -- Binder & Desai
2011). Ernst-Banks-style explicit 1/variance weighting (w_i = (1/var_i) / sum_j(1/var_j)) is a
USEFUL ANALOGY/upper-bound ideal that the learned system would converge toward under stable
noise statistics, but it is not how any of these semantic models is actually specified.

**Status: COMPUTATIONAL-LEVEL** (Rogers & McClelland 2004; Jackson, Rogers & Lambon Ralph 2021,
Nature Human Behaviour 5:847-860). The reliability-weighting framing (Ernst & Banks 2002,
Nature; Ma, Beck, Latham & Pouget 2006, Nature Neuroscience) is OPEN as applied to this specific
system -- cited by the field as the normative ideal, not fit to ATL directly.

### Point 2 -- How task control gates readout of the shared hub

**Finding.** Jefferies (2013, Cortex review) and the TMS work (Whitney, Kirk, O'Sullivan,
Lambon Ralph & Jefferies 2011, Cerebral Cortex 21:1066-1075) localize a distributed "semantic
control" network to left IFG + posterior MTG (+ dmPFC/precuneus in later meta-analysis,
Jackson 2021 meta-analysis of 925 peaks). Hoffman, McClelland & Lambon Ralph 2018 (Psychological
Review 125:293-328, "Concepts, Control, and Context") give the actual computational mechanism:
a "controlled retrieval" pathway that sends top-down input INTO the hub-and-spoke network to
amplify weak/task-relevant semantic relationships, plus a context "buffer" that holds recent
state so retrieval is sequentially dependent on what was just retrieved. Jackson, Rogers &
Lambon Ralph 2021 then ask WHERE in a multi-layer hub this control should act and find, by
lesioning/ablating control connections at different depths, that control units wired to the
*peripheral spoke layer or the first (shallow) hidden layer* produce better task-appropriate,
context-sensitive behavior than control wired directly into the deep hub -- and that the learned
control-to-hub weights were smaller in magnitude than control-to-shallow-layer weights. In other
words: task control is implemented as extra, learned top-down INPUT/bias into early layers
(functionally a gain/gate on which spoke features get through), not as a direct re-scaling of the
deep hub code itself.

**Equation / operation (plain math).**
Let the network's feed-forward activation without control be h_spoke = f(W.s + b). With control
input c (task/context vector) arriving mainly at the spoke/shallow layer:
  h_spoke' = f(W.s + U.c + b)
i.e. control is an additive, learned bias/gain term (U.c) injected upstream of the hub, which
then changes what pattern reaches the (unchanged-in-architecture) deep hub -- a "controlled
retrieval" amplification of weak associations, per Hoffman 2018's explicit framing, rather than a
multiplicative gain directly on hub units. A small multiplicative/gating reading is also
compatible with the data (amplifying SOME spoke features over others acts like a soft attention
gate over the spoke layer) but the papers describe it operationally as added top-down drive, not
as a literal multiplicative mask.

**Status: PINNED (network localization: IFG/pMTG, TMS double-dissociation evidence) +
COMPUTATIONAL-LEVEL (mechanism: top-down additive/amplifying input mainly at peripheral layers,
Hoffman McClelland Lambon Ralph 2018; Jackson Rogers Lambon Ralph 2021).** Whether the real
cortical implementation is literally additive-bias vs multiplicative-gain is OPEN -- the models
are agnostic/underspecified on this distinction at the biophysical level.

### Point 3 -- CLS account of reading-grown (hippocampal) knowledge consolidating into the hub

**Finding.** McClelland, McNaughton & O'Reilly 1995 (Psychological Review 102:419-457): the
hippocampus does fast, sparse, pattern-separated encoding of individual episodes; the neocortex
(here: the ATL hub + spokes) learns slowly via small weight changes, with hippocampal replay
interleaving new items among old so that new knowledge gets woven into structure rather than
overwriting it (catastrophic-interference avoidance is the reason interleaving is necessary, not
optional). Kumaran, Hassabis & McClelland 2016 (Trends in Cognitive Sciences 20:512-534, "What
Learning Systems do Intelligent Agents Need? CLS Theory Updated") extend this: replay can be
goal/value-weighted (not uniform), and neocortical learning CAN be fast when new information is
already schema-consistent (the "fast mapping" extension: McClelland 2013; Sharon, Moscovitch &
Gilboa 2011 rapid neocortical acquisition of schema-consistent arbitrary associations,
independent of hippocampus). Davis & Gaskell's "complementary systems account of word learning"
(Phil Trans R Soc B 364:3773-3800) applies this directly to lexical acquisition: a new word is
initially hippocampus-dependent and lexically "isolated" (can be used but not yet integrated with
neighbors -- e.g. it doesn't yet compete with existing words in spoken recognition); only after
an offline consolidation period (classically linked to sleep) does it integrate into the
neocortical lexical-semantic network and start behaving like an old word.

**Equation / operation (plain math).**
Per-item neocortical weight update is small and interleaved across many items per step (gradual,
distributed, structure-sensitive learning):
  dW = eta_slow * sum_over_replayed_items ( target_i - f(W.x_i) ) . x_i^T
with eta_slow << eta_hippocampal, and the replay set drawn from a MIX of new + old items
(interleaving), optionally weighted by reward/goal relevance (Kumaran et al. 2016 extension).
The hippocampal fast store does a one-shot, high-learning-rate, pattern-separated write:
  dW_hpc = eta_fast * (target - f(W_hpc.x)) . x^T , eta_fast >> eta_slow
and "grounding a new word" = write fast into the hippocampal store immediately (usable same-day,
isolated), then slowly fold it into the neocortical hub via many interleaved replay-driven small
updates until it is no longer hippocampus-dependent.

**Status: PINNED at the computational/behavioral level** (interleaving prevents catastrophic
interference is mathematically demonstrated in the original connectionist simulations;
schema-consistency fast-mapping is behaviorally/lesion-demonstrated in Sharon et al. 2011). The
exact replay SCHEDULE (how much interleaving, what triggers consolidation, sleep-dependence
strength for word learning specifically) is OPEN/contested (Davis & Gaskell review flags
inconsistent sleep-effect replication across studies).

### Point 4 -- Same hub serves comprehension, production, AND grounding

**Finding.** Semantic dementia (bilateral ATL atrophy) produces a SINGLE graded deficit that
cuts across comprehension (word-picture matching degrades, concept becomes coarser -- "dog" ->
"animal"), production (picture naming fails the same items in the same order of severity), AND
new-concept acquisition/learning, with deficit severity correlating across all three within a
patient and across patients with atrophy extent (Patterson, Nestor & Rogers 2007, Nature Reviews
Neuroscience 8:976-987, "Where do you know what you know?"). This graded, correlated, cross-task
co-degradation is the classical argument FOR one shared store: if comprehension and production
used separate semantic stores, differential (not correlated) impairment across patients would be
expected/possible; it is not observed. Binder & Desai 2011 (Trends in Cognitive Sciences
15:527-536) reconcile this with embodied/modality-specific findings via "embodied abstraction":
the ATL hub is a genuinely transmodal convergence zone, but it sits atop (not instead of)
modality-specific spokes that remain partially active and necessary for fine-grained/concrete
content — so the hub is shared across tasks, while the full concept representation at any moment
is hub + currently-active spokes together.

**Status: PINNED** (Patterson, Nestor & Rogers 2007 is the canonical synthesis of decades of SD
case evidence; correlated multi-task decline is a direct clinical/behavioral finding, not a
model). Binder & Desai 2011's embodied-abstraction reconciliation is an interpretive synthesis
(COMPUTATIONAL-LEVEL framing) rather than itself a new direct finding.

### Point 5 -- Computational models: one representation, many task-specific readouts

**Finding.** Rogers & McClelland 2004 (MIT Press "Semantic Cognition: A PDP Approach") is the
foundational demonstration: a single hidden (hub) layer trained to predict ALL attributes
(perceptual, verbal, categorical) from all inputs, with different "readout" pathways (different
output layers) used per judgement type -- the same hidden code supports naming, categorization,
and property-verification via different linear readouts off the same hub. Chen, Lambon Ralph &
Rogers 2017 (Nature Human Behaviour 1:0039, "A unified model of human semantic knowledge and its
disorders") extends this with a deep network whose connectivity is fit to measured cortical
connectivity, showing graded domain-specificity EMERGES from the joint effect of a shared deep
hub plus differential spoke connectivity -- reconciling domain-specific and domain-general
accounts inside one architecture rather than needing separate stores. Jackson, Rogers & Lambon
Ralph 2021 adds explicit task-control read-out (see Point 2). The most directly relevant
2020s-era computational precedent from OUTSIDE neuroscience is the "Semantic Hub Hypothesis"
(Wu, Lee & Andreas, ICLR 2025, arXiv:2411.04986): in multilingual/multimodal transformer language
models, intermediate layers converge to a SHARED, modality/language-agnostic representation
(semantically equivalent inputs in different languages/modalities land in nearly the same
intermediate vector), and interventions on that shared intermediate representation for one
input type (e.g. text) predictably change model behavior for a DIFFERENT input type (e.g. code
or arithmetic) read out downstream -- i.e., one intermediate hub, many task/modality-specific
readout heads acting on it, functionally identical in computational shape to the
hub-and-spoke + task-control proposal, independently (re)discovered in a completely different
substrate. This is the cleanest available EQUATION-level existence proof that "one hub read by
many task heads" is implementable and produces the right qualitative signature (shared geometry +
cross-task transfer via the shared layer).

**Status: COMPUTATIONAL-LEVEL, well-established for the neuro models (Rogers & McClelland 2004;
Chen, Lambon Ralph & Rogers 2017; Jackson, Rogers & Lambon Ralph 2021), and
COMPUTATIONAL-LEVEL/cross-domain-analogous for the 2024-2025 LLM result** (Wu, Lee & Andreas
2025 is evidence the SCHEME works in an artificial system, not direct evidence about biological
implementation -- import, not pinned transfer).

## (C) Implications for the substrate's ~6 lexical-semantic stores

Current substrate stores (as given): (1) curated 200-d word2vec sense-signature table,
(2) WordNet definitional-feature bag, (3) McRae feature lexicon, (4) grown directional
co-occurrence store, (5) 12-d sensorimotor norm table, (6) directed typed-relation store.

Mapping onto the brain's architecture (P_deflated=0.40, novel-synthesis cap applied; this is
MY synthesis, not a literature finding):

- **Candidates to fold into ONE hub-with-spokes (graded, distributed, similarity-geometry
  stores):** (1) word2vec sense-signatures, (3) McRae feature lexicon, (4) grown co-occurrence
  store, (5) sensorimotor norms. All four are exactly the kind of thing the brain's spokes feed
  into a converging hub: each is a distributional-or-perceptual "modality" (word2vec/co-occurrence
  ~ linguistic-distributional spoke; McRae ~ a crowd-sourced proxy for experiential-feature
  spokes; sensorimotor norms ~ perceptual-motor spokes). The brain-supported INTEGRATION RULE
  (Point 1) is a LEARNED weighted convergence (not hand-set precision weights): concretely, this
  argues for training (or at minimum fitting) a single shared low-dimensional hub representation
  h = f(sum_i W_i . spoke_i) from these four sources jointly, rather than keeping four separate
  flat tables queried independently per task. The practical substrate-level analogy to "reliability
  weighting" is to let whichever spoke most reduces reconstruction/prediction error for a given
  word dominate that word's hub code (concrete/sensorimotor-rich words lean on norms+McRae;
  abstract words lean on co-occurrence/word2vec) -- this falls out of joint training, it should
  NOT be hand-coded as a fixed per-word mixture weight.
- **Legitimately SEPARATE structures (the brain does not claim these are the same kind of
  object as graded similarity):** (2) WordNet definitional-feature bag and (6) directed
  typed-relation store are structurally TYPED/relational (is-a, part-of, agent-of) rather than
  graded-similarity spokes. Nothing in this literature puts typed taxonomic/relational edges
  inside the ATL hub's graded similarity space as a first-class citizen -- the hub is consistently
  described as continuous/graded-multidimensional (Cox et al. 2024 is explicit on this: "graded,
  multidimensional... not discrete symbolic slots"). This is independently consistent with this
  project's own already-DONE finding that type-level is-a/taxonomic channels are REFUTED as a
  meaning-lever over a strong SEQ floor (see MEMORY: taxonomic-isa-lever-is-a-pre-seq-artifact,
  2026-09-10) -- i.e., both the outside literature AND this project's internal evidence point the
  same direction: typed-relational knowledge is a separate, symbolic bookkeeping structure, not
  something to merge into the graded hub. Keep (2) and (6) as separate typed stores; they should
  be consulted as DISCRETE constraints/edges alongside hub similarity, not folded into it.
- **Task control reading of the hub:** per Point 2, different tasks (word-sense selection,
  coreference typing, grounding, next-word prediction, similarity judgement) should NOT each get
  their own copy of semantic content; they should each get their own lightweight READOUT
  function over the SAME hub vector, with task-identity acting as an upstream gating/bias signal
  into which spoke features dominate the hub computation for that query (e.g., a next-word-
  prediction task biases toward the distributional/co-occurrence spoke; a grounding task biases
  toward sensorimotor+McRae spokes) -- mirroring control-acts-on-shallow-layers, not
  control-rewrites-the-hub.

## (D) What the literature does NOT settle

- No paper gives an explicit, fitted mathematical form for HOW MUCH weight each modality/spoke
  gets in the human ATL hub under task demand (the Ernst-Banks/Ma-Beck-Latham-Pouget reliability
  math is an analogy imported by the field, not a measured fit to ATL data).
- Whether task control is implemented biologically as additive top-down bias, multiplicative
  gain, or a mix is unresolved; models use additive/amplifying framing but are agnostic at the
  biophysical level.
- The replay schedule and sleep-dependence for word-learning consolidation specifically (vs.
  general declarative memory) has inconsistent empirical support (Davis & Gaskell review).
- Whether typed/relational (taxonomic, thematic-role) knowledge has ANY shared neural substrate
  with the graded ATL hub, or is fully separate (e.g., parietal/hippocampal relational systems),
  is not directly addressed by the CSC literature reviewed here -- this project's own internal
  result (is-a refuted as a meaning lever) is suggestive but is not itself brain-localization
  evidence.
- The exact number/identity of "spokes" is not fixed by theory -- the literature uses whatever
  modalities a given study measured (vision, audition, sensorimotor, praxis, verbal/distributional
  input); there's no principled derivation of "exactly N spokes," so the substrate's choice of
  4-5 spoke-like stores is a reasonable engineering mapping, not a brain-dictated count.

## Citations (verified count: 14 primary sources directly retrieved/confirmed via search or fetch)

1. Patterson, Nestor & Rogers 2007, Nature Reviews Neuroscience 8:976-987.
2. Lambon Ralph, Jefferies, Patterson & Rogers 2017, Nature Reviews Neuroscience 18:42-55 (CSC).
3. Rogers & McClelland 2004, "Semantic Cognition: A PDP Approach", MIT Press.
4. Hoffman, McClelland & Lambon Ralph 2018, Psychological Review 125:293-328.
5. Jackson, Rogers & Lambon Ralph 2021, Nature Human Behaviour 5:847-860.
6. Cox, Fernandino et al. 2024, Imaging Neuroscience ("graded multidimensional semantic space in
   ATL").
7. Ernst & Banks 2002, Nature 415:429-433.
8. Ma, Beck, Latham & Pouget 2006, Nature Neuroscience 9:1432-1438.
9. Jefferies 2013, Cortex 49:611-625 (semantic control review); Whitney, Kirk, O'Sullivan,
   Lambon Ralph & Jefferies 2011, Cerebral Cortex 21:1066-1075 (TMS).
10. McClelland, McNaughton & O'Reilly 1995, Psychological Review 102:419-457.
11. Kumaran, Hassabis & McClelland 2016, Trends in Cognitive Sciences 20:512-534.
12. Davis & Gaskell 2009, Phil Trans R Soc B 364:3773-3800; Sharon, Moscovitch & Gilboa 2011,
    PNAS (schema-consistent fast neocortical learning).
13. Binder & Desai 2011, Trends in Cognitive Sciences 15:527-536.
14. Chen, Lambon Ralph & Rogers 2017, Nature Human Behaviour 1:0039.
15. Wu, Lee & Andreas 2025, ICLR 2025 / arXiv:2411.04986, "The Semantic Hub Hypothesis".

All citations above were confirmed present via direct web search result titles/abstracts in this
session (2026-09-11); two (Hoffman 2018, Jackson 2021) were additionally confirmed via direct
PDF/HTML fetch of architecture details. None were taken from memory alone.

## TLDR

The brain very likely keeps ONE shared "meaning hub" (a region at the front-bottom of the
temporal lobe, both sides) that every task -- picking the right sense of a word, figuring out who
a pronoun means, learning a brand-new word, guessing the next word, judging how similar two
things are -- reads from, the same way several different apps can all read the same shared file
instead of each keeping its own copy. What differs per task is not the stored meaning itself but
a separate "control" system (front and side brain regions) that leans on different input channels
before they reach that shared hub, and a second, slower memory-consolidation process (the classic
fast-hippocampus/slow-cortex split) that is how a newly learned word gets folded into that shared
hub over time rather than staying in a separate quick scratch-pad. For the system we're building:
four of its six separate meaning-lookup tables (word-vector senses, word-feature lists,
co-occurrence counts, sensorimotor ratings) look like the brain's "spokes" and are good
candidates to be merged into one shared hub space that different tasks read differently; two of
them (the dictionary-style definitions table and the labeled-relationship store, e.g. "X is a
kind of Y") look like a genuinely different, separate kind of knowledge the brain keeps apart
from plain similarity -- which matches something this project already found the hard way.

## QUESTIONS
None.

## NEXT STEPS
1. Cheap decisive test (pre-registered here, not yet run): fit a small shared hidden layer
   (8-32 dims) trained to jointly reconstruct/predict word2vec signature + McRae features +
   sensorimotor norms + co-occurrence vector for a held-out word sample; HARD-PASS if the
   resulting single hub space beats each SEPARATE store at a downstream similarity-judgement or
   grounding task (CI-separated over the strongest single-store floor); HARD-FAIL if the merged
   hub underperforms the best individual store on its own best task (would indicate premature
   forced convergence, i.e. the stores are not actually redundant/complementary in the way the
   brain's spokes are).
2. Keep WordNet-definitional-bag and directed-typed-relation store as separate symbolic
   structures per (C); do not attempt to merge them into any hub-training objective.
3. Route this note's mapping to whichever cell-author is working lexical-semantic representation
   consolidation; no separate hand-off file is written (findings are fully actionable from this
   note directly).
