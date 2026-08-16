# DRILL: how a human acquires the meaning of a new word from a small grounded core plus experience

**2026-08-16, Director (research role). BIOLOGY DRILL + DESIGN. No experiment cell authored, no
experiment run, no `hdlab/` or `experiments/` file modified, no `metrics.json` touched, no subagent
spawned.**

Companion deliverable: `.claude/scan-out/phase2-grounding-drill.json` (same content, machine-readable).
Governing frame: `notes/LONG_TERM_PLAN.md` section 8 -- the capability is DEMONSTRATED by the brain;
the only open question is whether OUR reconstruction of a given organ is faithful enough yet.
Nothing below concludes that bootstrapping meaning is impossible or intrinsically limited.

---

## 0. DISCLOSURES, METHOD, AND WHAT IS NEW HERE

**No tool call was denied during this drill.** One tool ERROR occurred and is disclosed rather than
worked around: `bash tools/substrate_query.sh "<q>"` (which passes `--chunk-content`) died on the
first query with

```
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 5.00 GiB for an array with
shape (1309797, 2048) and data type float16
  at hdlab/director_kb_query.py:267 _load_or_build_e_unit
```

Queries 2-4 in the same batch ran (10.2-10.8 s each) against the v1 filename-index KB. So the
content-chunk KB is currently un-queryable on this machine at its present size; the standing
"substrate-KB concept-query before dispatch" discipline is satisfiable only through the v1 index
until that is fixed. **This is an infra finding, not a denial, and nothing was retried as a variant
to hide it -- the fallback path is a different KB and is reported as such.**

**Prior-work check was done by ENUMERATION, not by search** (MEMORY.md: an absence claim requires an
enumeration). `os.walk` over `notes/` = **11,320** `.md` files, `preregs/` = **3,805** `.md`,
`experiments/` = **5,834** `.py`, keyword-matched on a 20-term regex covering bootstrap / propagate /
snowball / frontier / bridge / fast-map / one-shot / acquisition / ZPD / proximal / curriculum /
norms / inherit / label-prop / transitive / word-learn / AoA / vocab-growth / semantic-neighbour /
hub-spoke. **117 note hits, 79 prereg hits, 120 experiment hits.** The substrate KB, queried in
parallel, returned mostly generic WordNet nodes (`propagation` 0.4785, `propagate` 0.4111) and one
genuinely useful hit (`notes/frontier_distance_2026-08-13.md::chunk000`, 0.3125). **The enumeration
found the load-bearing prior work; the KB did not.** Record that: for this concept class the
filesystem enumeration is the stronger instrument.

**Every claim about our own code below is RUNTIME evidence** (imported and called under
`.venv/Scripts/python.exe`), not grep. Probe scripts are in `scratch/` (`phase2_runtime_probe.py`,
`phase2_assets_probe.py`, `phase2_power_probe.py`, `phase2_registry_reconcile.py`); nothing they
produced is cited as durable provenance for a landed number, so they stay in `scratch/` per the
CLAUDE.md corollary -- the numbers they produce are reported here in full and are reproducible from
the scripts as written.

**Calibration.** The standing lit-scan penalty is applied: every probability estimate below is
deflated 0.15-0.25 and no novel-synthesis confidence exceeds 0.50.

---

# PART A -- THE BIOLOGY

Each answer names a NEURAL STRUCTURE where one is known, and each claim is marked
**[PINNED]** (evidence fixes it) or **[UNPINNED]** (ours to choose and test). Where the field is in
open dispute the dispute is reported rather than adjudicated.

---

## A1. THE GROUNDED CORE -- what is grounded first, and by what

**STRUCTURE: modality-specific sensorimotor and perceptual cortices, plus interoceptive cortex
(anterior insula), converging on the anterior temporal lobe.** [PINNED as an architecture]

- **Hub-and-spoke is pinned.** Damage the anterior temporal hub and semantic impairment is
  category-general and modality-general; damage a spoke and one facet is lost. This is the strongest
  architectural claim in the whole drill and it is already carried in `notes/ORGAN_MAP.md` B1/B5 with
  citations (Lambon Ralph / Rogers / Patterson lineage; Jackson, Rogers & Lambon Ralph 2021
  *Nat Hum Behav* 5:774+; Rogers, Cox, Lu, Shimotake et al. 2021 *eLife* 10:e66276).
- **The EARLY core is concrete and sensorimotor, and this is measured behaviourally.** Children
  comprehend and produce words that are more frequent AND higher in concreteness first, and both
  effects grow with age; abstractness emerges progressively over the second year. Sensorimotor
  information dominates early word learning and linguistic experience becomes relatively more
  important with age. [PINNED as a developmental regularity]
- **SIZE.** This is the number the plan needs and the literature does not hand it over cleanly.
  What IS pinned: productive vocabulary at 24 months is on the order of a few hundred words
  (MacArthur-Bates CDI norms), and by school entry receptive root vocabulary is in the low
  thousands to ~10k depending on whether derived forms are counted (Anglin's method dispute). The
  honest statement: **the early grounded core is O(10^3), not O(10^4) and not O(10^5)** -- and that
  is the number that matters for us, because it says a core of a few thousand hand-rated words is
  the RIGHT ORDER OF MAGNITUDE for a bootstrap, not a shortfall. **[PINNED to an order of magnitude;
  UNPINNED as an exact count.]**
- **CRITICAL, and it reframes our own coverage panic:** a core of a few thousand grounded words is
  the biological starting condition, not a failure state. We hold **36,810** normed words. The
  problem was never that the core is too small. **The problem is that we have no operation that
  extends it.**

**What this pins for us:** the core's SIZE is not our bottleneck. Its EXTENSION OPERATOR is.

---

## A2. FAST MAPPING / ONE-SHOT WORD LEARNING

**STRUCTURE: hippocampus (relational binding), with the perirhinal/entorhinal input.** [PINNED, and
the contest around it is itself informative]

- **The mechanism the behavioural literature actually supports is PROPOSE-BUT-VERIFY, not
  cross-situational intersection.** [PINNED] A learner commits to ONE referent hypothesis, carries
  it, and at the next informative encounter either confirms it or abandons it and re-proposes. No
  partial credit is given to alternatives; switching is abrupt, not a smooth convergence
  (Medina et al. 2011 *PNAS*; Trueswell et al. 2013 *Cogn Psychol*; Woodard 2016). Siskind-1996-style
  intersection over surviving candidate sets has essentially no human behavioural support.
  **This is already established in-house -- `notes/brain_fidelity_audit_word_learning_2026-08-12.md`
  section G.2 -- and that audit RETRACTED its own earlier proposal to build per-situation candidate
  sets on exactly these grounds. Do not re-propose intersection.**
- **Most exposures are useless.** Medina's exposure census: ~90% of natural exposures are
  uninformative and ~7% are highly informative. [PINNED] So an informative-encounter SELECTOR is not
  a workaround bolted beside the mechanism -- it is a REQUIRED upstream component of it.
- **The frame beats the scene.** Gillette & Gleitman 1999: verbs are identified 15% from the scene
  alone and 51.7% from syntax alone. [PINNED] Syntactic bootstrapping carries the dominant signal.
- **What is retained, and what decays.** A single fast-mapping episode yields a FRAGILE hypothesis
  that needs re-exposure to become durable (Horst & Samuelson 2008). [PINNED] Lexical competition --
  the signature that a new word has been integrated into the lexicon rather than merely remembered --
  is ABSENT immediately and PRESENT after a 12-hour interval containing sleep (Dumay & Gaskell 2007
  *Psych Sci* 18:35). [PINNED]
- **THE CONTEST, reported not adjudicated.** Sharon, Moscovitch & Gilboa 2011 *PNAS* reported that
  amnesic patients acquired arbitrary word-object associations rapidly under a fast-mapping
  procedure, implying hippocampus-independent direct cortical learning. **That has largely collapsed
  under replication** -- Warren & Duff 2014 (*Hippocampus*, "Not so fast"); Cooper, Greve & Henson
  2019 ("Fast mappers, slow learners: word learning without hippocampus is slow and sparse
  irrespective of methodology"); and a 2019 review finding little evidence for fast mapping as a
  distinct route in adults. **Current reading: rapid word learning in adulthood is
  hippocampus-dependent and relational regardless of encoding format.** [PINNED enough to build on;
  the contrary claim is on the record and is losing.]

**What this pins for us:** the fast arm is a one-shot RELATIONAL bind in hippocampus, its output is
a FRAGILE single hypothesis, and it does not become meaning until consolidation (A6). A Phase-2
design that treats a bridged code as immediately durable is unfaithful on the retention axis --
though that is a Phase-5 concern, not a Phase-2 blocker.

---

## A3. BOOTSTRAPPING FROM THE GROUNDED FRONTIER -- how abstract or unseen words get grounded

**STRUCTURE: contested. Report the contest.** This is the least-pinned question in the drill and
also the one the plan's central bet sits on.

Three live positions, none of which has won:

1. **Multiple-representation / refined embodiment.** Abstract concepts are constituted by
   representations distributed across experiential systems -- sensory, motor, EMOTIONAL,
   INTEROCEPTIVE, MENTALIZING (mPFC/TPJ) and SOCIAL-INTERACTION networks -- not by a single
   sensorimotor spoke. On this view "abstract" does not mean "ungrounded"; it means "grounded in
   different spokes". Recent reviews explicitly frame it as a multiple-representation framework.
2. **Indirect / linguistic grounding.** Modal representations are EXTRAPOLATED from
   distributional language-based representations, which are themselves mapped onto pre-existing
   modal representations. Concept similarities for abstract words in INFERIOR PARIETAL CORTEX are
   predicted by distributional-semantics models (Modelling brain representations of abstract
   concepts, 2022). A 2025 *Sci Rep* result finds semantic similarity of abstract SCIENTIFIC
   concepts reflected in activity patterns in visual and motor cortex -- "indirect experiential
   grounding".
3. **Amodal/verbal.** The traditional position that abstract concepts, lacking perceivable
   referents, are represented amodally or verbally. Weakened but not dead.

**What is PINNED across all three:** abstract-concept representation recruits a DIFFERENT and MORE
DISTRIBUTED set of regions than concrete-concept representation, with a reliable inferior-parietal /
temporo-parietal contribution that concrete concepts do not require to the same degree.

**What is UNPINNED:** the combination rule. Nothing in this literature gives an equation for how a
grounded neighbour's representation is transformed into an ungrounded word's representation. **That
operation is OURS to invent and test, and it must be labelled as invention.**

**The load-bearing consequence for us, stated plainly:** our 12-dimensional Lancaster+Brysbaert code
is a CONCRETE-SPOKE code. Position 1 predicts it will fail on abstract vocabulary not because
bridging fails but because the target space has no dimensions for the spokes abstract words actually
use (emotion, interoception, social). We ALSO hold `Ratings_Warriner_et_al.csv`
(valence/arousal/dominance) on disk, unused -- that is the EMOTION spoke, and adding it is a
brain-motivated, cheap, testable widening of the target space. Flagged as a design option, not
smuggled into the primary arm.

---

## A4. THE ROLE OF RELATIONS

**STRUCTURES: anterior temporal lobe (taxonomic/entity features) and angular gyrus (event,
thematic, and combinatorial relations) -- a DIVISION OF LABOUR, not one hub.** [PINNED as a
division; the equations are UNPINNED]

- **ATL vs AG division of labour is pinned.** AG is implicated in EVENT concepts and combinatorial
  semantics (noun+noun, verb+noun composition); ATL encodes conceptual features of ENTITIES and more
  general semantic combination. A representation-of-event-and-object-concepts study puts event
  concepts in AG and object concepts in vATL. An fMRI meta-analysis finds temporo-parietal regions
  reliably more activated by THEMATIC than TAXONOMIC relations.
- **Combination strengthens ATL-AG COUPLING.** Processing composable-but-low-typicality meanings
  (relative to both prototypical and anomalous ones) increases positive coupling between anterior
  temporal cortex and angular gyrus; left AG activity correlates with combinatorial strength across
  items (Price et al. 2015 *J Neurosci* 35:3276 and the companion *Cortex* 2015 coupling paper).
  [PINNED as a coupling effect]
- **This directly supports the GAP == GROUNDING framing.** The brain has a dedicated structure whose
  job is to compute a meaning FROM the relational combination of already-known meanings, and its
  engagement scales with how much combining is required. That is the neural existence proof for
  "ground a new word by its relational position to known ones".
- **BUT the transformation is UNPINNED.** No source gives the function that takes (known neighbour
  representation, relation type) to (new word representation). The one adjacent PINNED sub-fact we
  own is that LATL conceptual combination is approximately ADDITIVE (Baron & Osherson 2011
  *NeuroImage*) -- which licenses a WEIGHTED MEAN over normed neighbours as the default bridging
  operator and forbids presenting a learned projection as brain-pinned.
- **Relation TYPE matters and we currently ignore it.** The thematic-vs-taxonomic dissociation is
  pinned; `notes/frontier_distance_2026-08-13.md` explicitly treats `ISA` and `ENABLING_CONDITION`
  as the same hop. That is a named, cheap, brain-motivated refinement.

---

## A5. ORDER EFFECTS -- is nearest-frontier learning better than arbitrary order?

**YES, and there is a mechanism with a neural structure. This is the strongest single result in the
drill and it was not in our notes.**

- **STRUCTURE: medial prefrontal cortex (schema representation / congruency detection) interacting
  with medial temporal lobe.** [PINNED]
- **Tse et al. 2007 *Science* 316:76 -- schema-dependent rapid consolidation.** In rats with a
  pre-established flavour-place schema, NEW paired associates trained for a SINGLE TRIAL became
  assimilated and hippocampus-independent within ~48 hours, versus the weeks required without a
  schema. Schemas play a causal role in creating lasting associative representations from one-trial
  learning. **[PINNED]** This is precisely "learn what is one step from what you already know, and it
  sticks in one shot"; learn something unconnected and it costs weeks of consolidation.
- **SLIMM (van Kesteren, Ruiter, Fernandez & Henson 2012; van Kesteren et al. 2013
  *Neuropsychologia*).** mPFC encoding-related activity increases LINEARLY with congruency; MTL shows
  the OPPOSITE, increasing with INcongruency. mPFC "resonates" with congruent information and
  inhibits MTL to drive semantic integration. **[PINNED as the congruency gradient; the model is a
  MODEL]** -- and note the honest contest: a 2026 *Phil Trans R Soc B* paper is titled
  "two fMRI paradigms provide slim pickings for SLIMM". Report the gradient; do not build the model's
  specific inhibition equation as though it were measured.
- **Behavioural / network-growth evidence, and it is directly about VOCABULARY.**
  Hills, Maouene, Riordan & Smith 2009 *Psychological Science*, "Longitudinal analysis of early
  semantic networks: preferential attachment or preferential acquisition?" -- three growth
  mechanisms contrasted. **"Lure of the associates"** (new words are favoured in proportion to their
  connections to ALREADY-KNOWN words) **best predicted overall word acquisition and noun
  acquisition**; preferential acquisition (connectivity in the LEARNING ENVIRONMENT, regardless of
  what is known) best predicted verbs and function words; none predicted adjectives. **[PINNED,
  with the noun/verb split as a real and important scope condition]**
- **Corroborating:** semantic-network connectivity relates to vocabulary GROWTH RATE in children;
  children on slower trajectories do not show the small-world properties that emerge early in typical
  development (Beckage & Hills). Knowledge gaps in the early growth of semantic feature networks
  (Sizemore et al. 2018 *Nat Hum Behav*) treats the growing network's topological GAPS as the object
  of study -- the closest published analogue to our own framing.

**What this pins for us:** the ZPD intuition is not a metaphor here. It has (i) a one-trial-versus-
weeks consolidation consequence with a rodent causal result behind it, (ii) an mPFC/MTL congruency
gradient, and (iii) a vocabulary-growth model that beat its competitors on nouns. **The
nearest-frontier ordering arm in Phase 2 is testing something the biology positively predicts, and
the noun/verb asymmetry gives it a built-in falsifier: if our bridging gain is uniform across POS,
it is not the lure-of-the-associates mechanism.**

---

## A6. CONSOLIDATION -- fast bind to stable cortical representation

**STRUCTURE: hippocampal sharp-wave ripples during slow-wave sleep driving neocortical integration
(complementary learning systems).** [PINNED]

Most of this is already drilled in-house and CORRECTED twelve ways in
`notes/drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md`; that document supersedes
recollection and is not re-derived here. The parts that bear on Phase 2:

- **Timescale for WORDS specifically:** lexical integration requires an interval CONTAINING SLEEP;
  it is absent immediately (Dumay & Gaskell 2007). [PINNED]
- **Effect size, stated honestly:** Schimke, Angwin, Cheng & Copland 2021 *Psychon Bull Rev*
  28:1811 (25 studies, k=29, n=1,396) reports omnibus sleep-vs-WAKE `g=0.50` for novel word
  learning; recall `g=0.57`, recognition `g=0.52`, and **lexical INTEGRATION -- the measure that
  actually indexes the CLS claim -- is "a small effect", the WEAKEST in the analysis.** Do not quote
  `g=0.50` as an integration effect.
- **Replay is selective at the EVENT level** (large-SWR subset only); **only REVERSE replay scales
  with reward** (Ambrose, Pfeiffer & Foster 2016 *Neuron* 91:1124, NOT Foster & Wilson 2006); replay
  COUNT per experience is UNSOURCED and must be swept as a free parameter, not asserted.
- **The selection function -- which traces get replayed -- is UNPINNED**, and its leading normative
  candidate (Mattar & Daw 2018, `priority = GAIN x NEED`) computes NEED from the successor
  representation, an organ we do not have (ORGAN_MAP D7).
- **Interleaving:** CLS pins the PRINCIPLE (interleave old with new to avoid catastrophic
  interference), not a ratio. [PINNED principle, UNPINNED number]
- **AND THE SCHEMA RESULT FROM A5 IS A CONSOLIDATION RESULT.** Tse 2007 is the bridge between A5 and
  A6: near-frontier material consolidates in one trial, far material does not consolidate at all on
  that timescale. Order effects and consolidation are ONE mechanism, not two.

**Scope note for Phase 2:** consolidation is Phase 5 in the plan and correctly so. Phase 2 measures
whether a bridged code CARRIES MEANING, not whether it PERSISTS. State that boundary in the prereg
so a null on retention is not read as a null on bridging.

---

## A7. WHAT THE BRAIN DOES NOT DO -- is there evidence AGAINST pure distributional learning?

**This is the question the brief asked to be answered plainly, and the plain answer is
uncomfortable: the evidence does NOT support a blanket refusal of distributional structure as a
meaning source. Our refusal, as currently WORDED in the plan, is partly biologically wrong. What
survives is a narrower and better-founded refusal.**

**Evidence AGAINST "distributional co-occurrence alone is the mechanism":**

1. **Symmetric co-occurrence cannot separate synonymy from antonymy from co-hyponymy.** "the water is
   hot" and "the water is cold" are the same frame. This is not a scale problem; it is a
   representational one. What closes the SimLex gap is INJECTING EXPLICIT RELATIONAL STRUCTURE:
   GloVe 0.41 -> retrofitting 0.53 -> **counter-fitting 0.58**; Paragram-SL999 0.69 -> retrofitting
   0.68 (no gain) -> **counter-fitting 0.74** (Mrksic et al. 2016; Levy & Goldberg 2014; Levy,
   Goldberg & Dagan 2015 *TACL* 3:211). Already recorded at ORGAN_MAP STEP 3. **[PINNED, and it is a
   pro-RELATIONS result, i.e. pro-Phase-2]**
2. **Grounding is causally load-bearing for concrete vocabulary.** The developmental ordering
   (concreteness predicts early acquisition, abstractness emerges over year 2) and the modality-
   specific spoke lesion evidence both say sensorimotor experience does real work that text does not
   replace.
3. **A sensory-independent code exists ALONGSIDE the sensory-derived one.** Left dorsal ATL
   represents object-colour knowledge in congenitally blind and sighted alike (Wang, Men, Gao,
   Caramazza & Bi 2020 *Neuron* 107:383). [PINNED]
4. **Text-only channels recover meaning UNEVENLY by modality:** non-sensorimotor meaning well,
   sensory poorly, **motor minimally** (Xu et al. 2025 *Nat Hum Behav*). [PINNED] So distribution
   does not reach everything.

**Evidence FOR distributional/linguistic structure as a real acquisition channel, which we must not
suppress:**

5. **Congenitally blind adults acquire the STRUCTURE of colour knowledge from language.** Blind and
   sighted adults share in-depth understanding of object colour, make similar predictions for NOVEL
   objects, and organise colour terms into a trichromatic-like space; the conclusion in the
   literature is that "living among people who talk about colour is sufficient for colour
   understanding" (Kim, Elli & Bedny 2019/2021 *PNAS*). **[PINNED]** A learner with ZERO experience
   of a modality acquires that modality's similarity structure through language.
6. Result 5 and result 3 are the SAME phenomenon seen from two sides, and together they say
   something precise: **language transports RELATIONAL STRUCTURE into a spoke the learner cannot
   experience, anchored on the spokes the learner CAN.** That is not "distribution instead of
   grounding". **That is bridging from the grounded frontier -- Phase 2's exact thesis, with a human
   existence proof.**

**THE HONEST RULING, and it changes one line of the plan:**

- **Refusing DISTRIBUTIONAL STRUCTURE AS A MECHANISM is biologically WRONG.** The brain uses it, and
  in the blind-colour case it is the ONLY channel available and it works.
- **Refusing an EXTERNAL PRETRAINED CO-OCCURRENCE TABLE remains correct, but the reason must be
  restated.** The reason is NOT that distribution is unbiological. The reason is that adopting
  someone else's fitted table (i) imports an answer we did not derive and so teaches us nothing about
  the mechanism, (ii) violates the glass-box/no-external-model charter in spirit, and (iii) is
  precisely the "clear the floor by adopting the shortcut" failure the standing bar exists to
  prevent. That is a METHODOLOGICAL refusal, and it is defensible on its own terms.
- **Practical consequence:** our own distributional encoders (`ASSET_RI_WINDOW`, `ASSET_V2_CTX`,
  `ASSET_RETRAIN_*`) failing is NOT evidence that distribution is the wrong mechanism. They failed by
  collapsing off the frequent vocabulary (CI-separated drops of +0.17 to +0.25), which is a DATA-SCALE
  failure. The plan's line "a pretrained co-occurrence table is a CEILING REFERENCE for us and never
  our meaning source" should keep its conclusion and change its justification.

---

# PART B -- MAP TO US

Enumerated from disk FIRST, then reconciled to `data/capability_registry.jsonl`. Never the reverse.

## B1. DISK ENUMERATION

`os.walk` over `hdlab/`: **160 `.py` files** (147 at package root, 13 in `learner/` + `dashboard/`).
`ORGAN_MAP.md` recorded 155 on 2026-08-15; the tree has grown by 5 since (`ca3_completer`,
`hub_spoke_word` and neighbours are newer than that audit).
`data/capability_registry.jsonl`: **200 rows.** The registry keys on `capability_id`, not on module,
so there is no 1:1 module-to-row mapping in either direction -- several modules resolve to the same
row and several rows name several modules. **A registry-first audit of this question would have been
structurally blind; the modules that matter most for Phase 2 are among the least well-represented.**

## B2. THE ORGANS PHASE 2 NEEDS -- VERIFIED BY RUNTIME

| organ the biology names | our module | RUNTIME finding | registry |
|---|---|---|---|
| A1 grounded core (spokes) | `hdlab/grounded_similarity.py` | `coverage_stats()` = **36,810 words x 12 dims**; `SENSORIMOTOR_COLS` = 11 Lancaster means; `CONCRETENESS_COL` = `Conc.M`; `GROUNDED_CAP` = **0.45** | WIRE / WIRED / PIPELINE_USED |
| A2 fast bind, one-shot | `hdlab/hippocampal_encoder.py` | `CA3AutoAssociator.settle` source read verbatim: **one step, `sign(W @ cue)`**, docstring says "One-step settling". Not an iterative completer. | VET_PENDING / ISLAND |
| A2 completion | `hdlab/modern_hopfield_readout.py` | 383 lines, **0 `while`, 0 `max_steps`, 0 occurrences of "converg"** -- confirms there is no settling loop. | WIRE / WIRED / NOT_PIPELINE_REACHABLE |
| A3/A4 bridging by relation | `hdlab/wordnet_polarity_propagation.py` | **This IS a bridging organ** -- seed anchor set (52 verbs) propagated to an unrated lemma over WordNet path-similarity + antonymy, returning polarity + confidence, converted to Bayesian pseudo-counts. RUNS. But: `dictionary_lookup("squander")` (its own docstring's motivating example) **ABSTAINS**, vote_margin **0.0141** against `VOTE_MARGIN` **0.15**, n_neighbors 42; `dictionary_lookup("photosynthesis")` abstains with n_neighbors **0** (verb-only). | WIRE / WIRED / NOT_PIPELINE_REACHABLE |
| A3 acquisition orchestration | `hdlab/word_acquisition_loop.py`, `hdlab/word_learning_tool.py` | Full PROPOSE / CROSS-CHECK / GROUND / WRITE-BACK loop exists, for genuinely novel words, with zero human seed-authoring for the targets. **Scope: ONE binary axis (outcome-verb RESULT_VALENCE POS/NEG), not the 12-dim norm space.** | `grounded_word_acquisition_loop_increment1` = **SHELVE** (HARD_FAIL) |
| A4 relational position | `hdlab/gap_detector.py` | `familiarity(subject, relation, obj, *, use_confidence_signal)` -- a TRIPLE-level familiarity margin. Source contains **"distance" 0, "frontier" 0, "hop" 0, "bridge" 0**. | WIRE / WIRED / PIPELINE_USED |
| A5 order / what to read next | `hdlab/gap_driven_reader.py` | `rank_material(state, target_lemma, candidate_docs)`, `next_read_target(state, tracker, primary_lemma, *, use_gap_signal)`. Source contains **"distance" 0, "frontier" 0, "hop" 0, "bridge" 0, "grounded_set" 0**. | WIRE / WIRED / NOT_PIPELINE_REACHABLE |
| A5 what to read next (MVT) | `hdlab/information_foraging.py` | Exists, 807 lines, Charnov/Constantino-Daw/Hayden/Wittmann cited in-module, `ForagingController` + `RhoTracker` + `DepletionEstimator` + `oracle_mvt_optimum`. | WIRE / WIRED / NOT_PIPELINE_REACHABLE |
| the shelf | `hdlab/corpus_registry.py` | `enumerate_corpora()` runs and returns **36 entries, 28 `READABLE_PROSE`**, incl. the 251 MB simplewiki. | WIRE / WIRED / NOT_PIPELINE_REACHABLE |
| grounding evaluation | -- | **There is no single "grounding evaluation" module.** The evaluation lives in cells: `exp_meaning_asset_*` (rho instrument) and `tools/orthographic_floor_vet_v1.py` + `experiments/exp_grounding_readout_known_answer_v1.py` (open-vocab hit@1 instrument). | n/a |

**THE PLAN'S PREMISE, CHECKED: "unify the gap detector, the gap-driven reader and grounding
evaluation onto ONE distance-to-frontier metric."** Runtime says **none of the three currently
computes a distance to anything.** `gap_detector` computes a per-triple familiarity margin;
`gap_driven_reader` counts prerequisite-lemma occurrences in candidate documents; grounding
evaluation is a Spearman rho over a fixed pair list. **The distance metric is not a unification of
three existing metrics -- it does not exist and must be built.** That is not a criticism of the plan;
it is a correction to the estimate of what "unify" costs.

## B3. THREE RUNTIME TRAPS FOUND THIS PASS

**TRAP 1 -- `hdlab.grounded_similarity.grounded_similarity` IS SATURATED AND MUST NOT BE USED AS A
SCORER.** Measured on all 999 SimLex pairs:

```
n pairs 999   distinct values 229
  654 pairs at exactly 0.45   (the GROUNDED_CAP)
  107 pairs at exactly 0.0
  = 76.2% of ALL SimLex pairs sit at one of two values
dog/cat      grounded_similarity = 0.45   raw cosine on grounded_vector = 0.9317
sofa/couch   grounded_similarity = 0.45   raw cosine on grounded_vector = 0.9677
apple/orange grounded_similarity = 0.45   raw cosine on grounded_vector = 0.9522
freedom/justice = 0.0                     raw cosine = -0.4401
```

`hdlab.lexical_similarity.concept_similarity("dog","cat")` likewise returns exactly **0.45**. The
`ASSET_NORMS12` arm scored 0.2701 because it used `grounded_vector` + raw cosine, NOT this function.
**Any Phase-2 cell that scores through `grounded_similarity()` would be computing a Spearman rho over
a two-valued variable and would report a spurious null.** This is a live, unflagged design trap and
it is now on the record.

**TRAP 2 -- the bridging organ we own abstains on its own example.** See B2. The mechanism is right;
the operating point does not fire. `VOTE_MARGIN = 0.15` against an observed margin of 0.0141 on
`squander` says WordNet path-similarity voting over a 52-word anchor set produces margins an order of
magnitude below the abstention threshold for a mid-frequency verb. **Expect low bridge YIELD, not
bridge failure** -- and design the Phase-2 arms to measure yield separately from quality.

**TRAP 3 -- confirmed, both modules the brief flagged.** `modern_hopfield_readout` has no settling
loop (0 `while`, 0 `max_steps`, 0 "converg" in 383 lines). `CA3AutoAssociator.settle` is one step and
says so in its own docstring. Neither is load-bearing for Phase 2, but both are now runtime-verified
rather than inherited.

---

# PART C -- DEDUP: WHAT HAS ALREADY BEEN RUN

**This is the most important section for whoever authors the cell. Four prior results bound the
design, and one of them is nearly the same experiment.**

### C1. `exp_grounding_snowball_transitive_inheritance_v1` -- THE NEAREST PRIOR ART

`preregs/2026-07-09_grounding_snowball_transitive_inheritance_v1.md`, commit `89a088469`, atomized
**MEASURED_MECHANISM (proven boundary)** at
`tools/_skunkworks_atomize_2026_07_09_grounding_snowball_transitive_inheritance_v1_MEASURED_MECHANISM.py`.

FULL, 5 seeds (7/13/17/23/29), ConceptNet 2-core n=10,577 E=34,659 med_deg 3, 120 ground-seeds.
A grounded scalar attached to 120 seed atoms is read off NON-seed atoms by cosine k=7 label
propagation over relational codes, binned by graph distance to nearest seed:

```
near_acc(d1)     0.6073  (HP 0.60)     far_acc(d4+) 0.5252     decay 0.0821 (HP 0.08)
genuine_margin (smooth - SHUFFLED) 0.0965 (HP 0.06)
SHUFFLED must-fail control FLAT AT CHANCE 0.5108, all bins ~0.50
margin by distance:  d1 0.0965 | d2 0.0434 | d3 0.0228 | d4+ 0.0318
```

**Bounds it sets on Phase 2, and they are the design's most useful input:**
- Relational grounding-inheritance is **REAL** (shuffled control flat, all 5 seeds positive) and
  **SHALLOW -- essentially one hop.** Signal is gone by d2 and at noise by d3.
- **FULL was roughly HALF of smoke** on every headline. Deflate accordingly.
- Its grounded attribute was a **SYNTHETIC graph-smooth scalar**, explicitly an honest stand-in, not
  real perceptual grounding. Its graph was ConceptNet, not our own extracted relations.
- Co-training the encoder on the seed attribute did **NOT** deepen propagation (+0.007, null).

**PHASE 2 MUST DIFFER ON THREE AXES OR IT IS A REDISCOVERY:** (i) the propagated quantity must be the
REAL 12-dim Lancaster+Brysbaert norm vector, not a synthetic smooth scalar; (ii) the scorer must be
the Phase-1 instrument (human SimLex gold), not attribute-read accuracy on a planted field; (iii) the
graph must include our OWN extracted definitional relations, so the result speaks to the reading loop.

### C2. `notes/frontier_distance_2026-08-13.md` -- THE DISTANCE MEASUREMENT IS ALREADY DONE

Do not re-measure it. Headlines, off `data/exp_frontier_distance/`:

```
frontier = 1,261 lemmas (887 seed UNION 374 grounded); corpus 16,812 distinct content lemmas
d0 1,159 | d1 371 | d2 113 | d3 68 | d4+ 65 | UNREACHABLE 15,036 = 89.4%
of the unreachable, 14,314 (95.2%) are the subject of ZERO extracted fact
most permissive variant (all 4 fact files, undirected) still leaves 83.1% unreachable
frequency is the dominant predictor (39.6% unreachable at f>=100 -> 98.8% at f=1)
concreteness does NOT predict distance; proper nouns are NOT the story
hub `process` carries 12.7% of bridge links; removing it costs only 10.5% of d1
```

**The correct reading, and it is a supply statement, not a ceiling:** 95.2% of unreachable words are
unreachable because our EXTRACTOR produced no fact with them as subject -- relational bridging has
literally nothing to work with, which is a statement about extraction yield, not about bridging. The
note's own honest limit stands: **reachability is not correctness** (`fruit --COPULA--> agent` is a
distance-1 edge and is not a usable definition), and nothing in it was hand-scored.

### C3. `notes/brain_fidelity_audit_word_learning_2026-08-12.md` -- ALREADY DRILLED, AND IT RETRACTS THINGS

Section G supersedes its own sections B.3/D/E. Load-bearing for Phase 2:
- **PROPOSE-BUT-VERIFY is the supported mechanism; intersection is retracted.** `canonicalize`'s
  single-winner argmax is CLOSER to the brain than a candidate-set intersection would be. **Do not
  re-propose per-situation candidate sets.**
- The measured error profile of the current path is **8% MEANINGFUL / 26% RELATED / 66% NOISE** -- the
  fingerprint of a RELATEDNESS metric where the brain uses REFERENCE.
- The banked population is crammed against its own refusal threshold: median `best_cos` 0.4922 against
  `SENSE_MATCH_THRESH` 0.45; **55.5% of banked facts beat "nothing matched" by less than 0.05.**
- The perceptual and ATL organs are present, registered, and **absent from the reading path's import
  closure** -- islanding, measured not suspected.

### C4. `.claude/scan-out/meaning-assets-verdict.json` (commit `84b8f00d5`) -- THE PHASE-1 BASELINE

Do not re-derive. The numbers Phase 2 must beat and be compared against:

```
ASSET_NORMS12 frequent-322  rho +0.2701 [+0.1604,+0.3712]
              rarer-677     rho +0.2289 [+0.1517,+0.3014]   drop +0.0412 NOT_SEPARATED
              SimLex-999    rho +0.2449  margin over strongest floor +0.2621 [+0.1739,+0.3484] ABOVE
              WordSim-353   rho +0.4093  margin +0.2758 [+0.1213,+0.4259] ABOVE
              on the instrument's own 322: misses its OWN scramble floor by 0.0071 at the lower bound
GloVe known-answer arm      margin +0.3511 [+0.2012,+0.4957] n=322, permutation p 5.0e-04
floors on the rho instrument: HARDENED_FREQUENCY_FREQ_MIN 0.0797 | A_ORTHOGRAPHIC 0.0169-0.0647
                              | SCRAMBLE_NULL_P95 0.0932-0.0943
open-vocab hit@1 instrument: A1_BASE 0.0480 [0.0413,0.0548] | A6_TRIGRAM_ONLY 0.0870 [0.0783,0.0960]
                             A7_PREFIX_ONLY 0.05875 | A8_MAXORTHO 0.0610; n=4000 items, 5491 anchors
                             A2_NORMS wired into the C3 harness: 0.07125 at w=0.50, BELOW 0.0870
```

**Also do not re-propose:** `exp_meaning_asset_ctx_readout_variants_v1` = `NO_READOUT_VARIANT_CLEARS_
THE_FLOOR`, and `exp_hub_spoke_word_g3_cleanup_rescore_v1` showed reading through cleanup changed the
vector by 1.192e-07. **"The read-out was the problem" is ruled out.**

---

# PART D -- THE PHASE 2 EXPERIMENT DESIGN

**Working anchor name: `exp_bridged_grounding_from_core_v1`. This is a DESIGN, not a pre-registration
and not a dispatch. No cell was authored.**

## D0. THE ONE-SENTENCE DESIGN

Hide the hand-rated norms for a held-out set of words; reconstruct each held-out word's 12-dim
grounded code ONLY by an additive bridge from its relational neighbours that still have norms; score
the reconstructed codes on the identical Phase-1 instrument, against the identical floors, with a
degree-preserving edge shuffle as the null and a same-stratum own-norms arm as the known-answer.

## D1. THE MEASUREMENT, STATED EXACTLY

> **PRIMARY.** Spearman rho between (a) cosine similarity of the 12-dim grounded vectors and
> (b) the SimLex-999 human gold rating, computed on the **BRIDGED-ENDPOINT STRATUM** -- the subset of
> SimLex-999 pairs in which **exactly one** endpoint is a held-out word whose 12-dim code was produced
> ONLY by bridging and never by hand rating, and the other endpoint retains its hand-rated code.
> The verdict quantity is the **paired-bootstrap margin of that rho over
> `max(A_ORTHOGRAPHIC, HARDENED_FREQUENCY_FREQ_MIN, SCRAMBLE_NULL_P95)` computed on the identical
> stratum, identical scorer, identical gold**, and the arm PASSES only if the 95% CI of that margin
> excludes zero.

Three properties this phrasing buys, each of which a looser phrasing has cost this project before:
- **"exactly one endpoint"** keeps n usable (measured below) and makes the contrast a ONE-VARIABLE
  swap: the same pair, the same partner, the same gold, one code replaced.
- **"identical stratum"** forbids comparing a bridged rho against a floor computed on the full 999.
- **"max of three floors"** forbids the `calibrated_floor_verdict_v1` defect the auditor caught, where
  a single "strongest" floor was chosen by highest floor-rho and the frequency channel was skipped.

## D2. THE STRATA, MEASURED, NOT ASSUMED

Measured this pass (`scratch/phase2_power_probe.py`, `.venv`), definitional graph built from
`definitional_facts_v5.jsonl` (2,092 rows) + `definitional_facts.jsonl` v3 (1,751) +
`definitional_facts_v4.jsonl` (1,956) = **5,799 rows, 2,450 nodes, treated UNDIRECTED (the most
permissive reading)**:

```
SimLex-999: 999 pairs, 1,028 distinct words, 1,028 / 1,028 have norms (100% coverage)
SimLex words with >=1 definitional edge                            261 / 1,028
   ... of which >=1 neighbour is IN the norms table (d=1 bridgeable)  220
SimLex pairs with BOTH endpoints bridgeable                          66
SimLex pairs with >=1 endpoint bridgeable                           392
```

**n = 392 for the primary stratum; n = 66 if both endpoints are bridged.** A Spearman CI half-width
scales as ~1.96/sqrt(n-3): **0.099 at n=392 versus 0.247 at n=66.** The known-answer GloVe margin at
n=322 was +0.3511 with a CI half-width of ~0.148. **At n=66 even a GloVe-strength effect would barely
separate.** So the both-endpoints design is UNDERPOWERED BY CONSTRUCTION and must not be the primary.
This is stated up front because an underpowered primary is how a real effect gets banked as a null.

**THE GROUNDED CORE, defined developmentally rather than arbitrarily.** `data/grounding_testbed/
AoA_51715_words.csv` (Kuperman AoA, column `AoA_Kup_lem`) is on disk and unused. Measured:

```
51,715 rows, 51,695 parsable AoA; 26,129 of them also have norms
AoA <=  4.0 y : 523 normed words        AoA <=  8.0 y :  6,728
AoA <=  5.0 y : 1,486                   AoA <= 10.0 y : 12,788
AoA <=  6.0 y : 2,838   <-- the developmentally-motivated CORE
```

**AoA <= 6.0 intersected with the norms gives 2,838 words -- the right order of magnitude for the
biological early core (A1), arrived at from an independent asset.** Defining CORE = {AoA <= 6.0} and
HELD-OUT = everything else makes the split a claim about development rather than a convenience, and it
gives the ordering arm (D5) a principled sequence.

## D3. THE ARMS

| arm | what it is | role |
|---|---|---|
| **K1_OWN_NORMS** | held-out words keep their real hand-rated 12-dim code | **KNOWN-ANSWER / harness reproduction.** Must reproduce the Phase-1 stratum number bit-identically. If it does not, nothing else in the cell is readable. This is the `A1_BASE reproduces 0.0480` discipline applied here. |
| **K2_ORACLE_BRIDGE** | held-out word takes the norms of the CORE word with the highest GOLD similarity to it (self excluded) | **SECOND KNOWN-ANSWER, and the most valuable arm in the design.** It answers: can a single-neighbour additive bridge carry meaning AT ALL in this geometry, given a perfect choice of neighbour? If K2 fails, the null is about the ARITHMETIC of bridging and not about our relations -- a dissociation this project has repeatedly lacked. |
| **B1_BRIDGE_DEF** | held-out code = unweighted mean of the 12-dim codes of its d=1 neighbours in OUR definitional graph that are in CORE | **PRIMARY, and the charter-compliant one.** Operator additive per Baron & Osherson 2011; **labelled OURS-INVENTION-UNDER-TEST**, because A4 leaves the transformation UNPINNED. |
| **B2_BRIDGE_DEF_TYPED** | same, but neighbours weighted by relation family (taxonomic ISA/COPULA vs thematic ENABLING/OCCURS_WHEN) | tests the pinned ATL-vs-AG taxonomic/thematic dissociation (A4). Secondary. |
| **B3_BRIDGE_CN** | same operator, edges from ConceptNet 5.7 / CSKG instead of our own extraction | **CEILING REFERENCE ONLY, exactly like GloVe.** A hand-curated relation graph is an external asset. It answers "is our graph the limiter or is the operator?" It is NOT a wiring recommendation and must be labelled so in the metrics. |
| **N1_SHUFFLE_DEGREE** | bridge targets permuted among held-out words preserving each source's degree and each target's in-degree (configuration model) | **NULL ARM.** Kills "any bridge to any core word returns something near the core centroid, which correlates with gold because gold pairs are topically clustered." The snowball cell's equivalent control sat flat at 0.5108, so this null is known to be capable of firing. |
| **N2_RANDOM_TARGET** | bridge to a uniformly random CORE word | second null, weaker, reported for shape |
| **F_ORTHO / F_FREQ / F_SCRAMBLE** | the three floors, recomputed ON THIS STRATUM | the bar |

**Every floor is recomputed on the bridged stratum. No floor is imported from another population.**

## D4. LEAKAGE CONTROLS -- the brief's hardest question

The specific worry: **a spelling channel already beats our whole system 8.70% to 4.80%.** Two things
must be said, in order.

**FIRST, A CROSS-INSTRUMENT CORRECTION THAT MUST TRAVEL WITH THIS DESIGN.** The 8.70%-versus-4.80%
result lives on the **open-vocabulary hit@1** instrument (`exp_orthographic_floor_vet_v1`, n=4000
items, 5,491 anchors, argmax hit@1). On the **rho** instrument -- the one Phase 1 gates on and the one
Phase 2's gate names -- the orthographic floor is `A_ORTHOGRAPHIC` at **0.0169 to 0.0647**, and the
norms clear it comfortably (+0.2054 [+0.0544,+0.3536] on the instrument 322). **Quoting the 8.70%
spelling floor as the bar for a rho-instrument arm would be exactly the cross-run conflation
CLAUDE.md names.** The right statement is: on the rho instrument the binding floor is the SCRAMBLE
floor, not spelling; on the hit@1 instrument spelling is the binding floor and a 12-dim norm code has
never been shown to drive that read-out at all (`A2_NORMS` = 0.07125, BELOW the 0.0870 spelling
floor). **Phase 2's verdict-bearing instrument is the rho one; the hit@1 instrument is run as a
labelled diagnostic with NO verdict weight.**

**SECOND, THE ACTUAL CONTROLS.** A bridged code can inherit spelling or frequency through the EDGE,
which is a channel the norms themselves do not have. Five controls, in decreasing order of how much
they decide:

1. **MORPHOLOGY-BLOCKED EDGE DELETION (the decisive one).** Delete every bridge edge whose endpoints
   share a normalised prefix of >= 4 characters, or whose character-trigram cosine exceeds a
   pre-registered threshold, or where one is a substring of the other. `biology -> bio*`,
   `reproduction -> production`, `photosynthesis -> synthesis` all die. **Re-report the primary margin
   on the surviving edges.** If the margin survives, spelling did not carry it, and that is a positive
   demonstration rather than a partial-correlation argument. Report the edge count before and after.
2. **FREQUENCY-AND-DEGREE-MATCHED SHUFFLE.** `N1_SHUFFLE_DEGREE` already preserves degree; extend it
   to also match log corpus frequency of the bridge TARGET within a band. If the real bridge does not
   beat the frequency-and-degree-matched shuffle CI-separated, the signal is frequency and degree.
3. **HARDENED FREQUENCY FLOOR, all four channels.** `FREQ_NEG_ABS_DIFF`, `FREQ_SUM`, `FREQ_MIN`,
   `FREQ_MIN_OVER_MAX`, take the max, on this stratum. The auditor's finding that two of three
   "clearing" arms in `calibrated_floor_verdict_v1` were not CI-separated from a frequency channel is
   the reason this is not optional.
4. **HUB CENSORING.** `process` alone carries 12.7% of distance-1 bridge links. Report (i) the number
   of DISTINCT bridge targets used, (ii) the primary margin with all targets of in-degree >= 10
   removed. If the margin lives on three hubs it is a hub artefact.
5. **IDENTITY AND SELF-LEMMA EXCLUSION.** A held-out word may never bridge to itself, to a normalised
   spelling variant of itself, or to its own SimLex partner. Reuse the exact eligibility construction
   already used by `tools/orthographic_floor_vet_v1.py` and `exp_meaning_supply_separation_v1`, which
   is known to reproduce the C3 pool bit-identically.

**And one control against ourselves:** the held-out words' norms must be removed from the CORE table
BEFORE any bridge is computed, and the cell must assert that the held-out rows are absent from the
table it reads. State the assertion in metrics. A silent fallback that returns the real norms for a
"held-out" word would produce a beautiful, meaningless pass.

## D5. THE ORDER-EFFECTS ARM (tests A5 directly, and it is the plan's own thesis)

Three arms, matched on the NUMBER of words admitted to the frontier:

- **O1_ONESHOT_D1** -- bridge every held-out word from the frozen CORE in one pass. No newly bridged
  word ever becomes a bridge source.
- **O2_ITER_NEAREST** -- iterate: bridge the held-out words at distance 1, ADMIT them to the frontier,
  recompute distances, bridge the new distance-1 set, and so on. Ties broken by AoA (earliest first).
  This is the ZPD / lure-of-the-associates arm.
- **O3_ITER_ARBITRARY** -- identical iteration and identical admission COUNT, order randomised.

**Pre-registered prediction, deflated:** on the snowball prior (margin d1 0.0965 -> d2 0.0434 ->
d3 0.0228), **O2 will beat O3 by little and may not beat O1 at all**, because our graph is too sparse
for a second hop to be informative. **P(O2 CI-separated above O3) <= 0.35.** If O2 does not win, the
honest conclusion is **"nearest-frontier ordering is not supported AT THIS GRAPH DENSITY"** -- a scoped
negative about our relation supply, NOT a refutation of the ZPD, which has one-trial-versus-weeks
rodent evidence behind it (Tse 2007).

**Built-in falsifier from the biology.** Hills et al. 2009 found lure-of-the-associates predicts NOUN
acquisition and preferential acquisition predicts VERBS. **Stratify every arm by SimLex POS (A/N/V).
If the bridging gain is uniform across POS, it is not the mechanism the biology names** -- report that
as a mechanism failure even if the headline margin is positive. This is the same discipline as
G.4.4's "a uniform lift across concrete and abstract would indicate a topical artefact".

## D6. WHAT A PASS AND A FAIL EACH MEAN

- **PASS** = `B1_BRIDGE_DEF` margin over `max(ortho, hardened-freq, scramble)` on the bridged stratum
  has a 95% CI excluding zero, AND survives morphology-blocked edge deletion, AND is CI-separated
  above `N1_SHUFFLE_DEGREE`, AND `K1_OWN_NORMS` reproduces the Phase-1 stratum number. **That is the
  thesis: a word grounded only by bridging carries measurable meaning.**
- **FAIL with K2 PASSING** = our RELATIONS are the limiter, not the bridging idea. Next step is
  extraction yield (95.2% of unreachable words are the subject of zero extracted fact), not a
  different operator.
- **FAIL with K2 ALSO FAILING** = additive single-hop bridging cannot carry meaning in the 12-dim
  space even with a perfect neighbour. Next step is the TARGET SPACE (A3: add the Warriner
  emotion/interoception spoke) or the OPERATOR, not the graph.
- **PASS on B3_BRIDGE_CN only** = the operator works and our graph is too sparse. Report it as a
  ceiling reference. **Do not wire ConceptNet in on the strength of it** -- same rule as GloVe.

**A secondary quantity that should be reported whatever the verdict, because it is what decides
whether scaling bridging is worth anything: the RETENTION FRACTION** rho(bridged) / rho(own-norms) on
the SAME held-out words, with a paired CI on the DIFFERENCE. "How much of a hand-rated word's signal
survives one bridge hop" is the number the whole Phase-2 route lives or dies on, and it is estimable
even in a floored null.

## D7. HONEST PROBABILITY ESTIMATES (deflated 0.15-0.25; novel synthesis capped at 0.50)

| claim | P |
|---|---|
| `K1_OWN_NORMS` reproduces the Phase-1 stratum number | 0.85 |
| `K2_ORACLE_BRIDGE` clears the floor CI-separated (n=392) | 0.45 |
| `B1_BRIDGE_DEF` clears the floor CI-separated | **0.30** |
| ... and survives morphology-blocked edge deletion | 0.22 |
| `B3_BRIDGE_CN` clears (ceiling reference, denser graph) | 0.50 |
| `O2_ITER_NEAREST` CI-separated above `O3_ITER_ARBITRARY` | 0.35 |
| bridging gain is POS-stratified as Hills et al. predict | 0.30 |

**These are low on purpose.** The prior most like this experiment (C1) produced a real but ~1-hop
effect that HALVED between smoke and full, on a graph an order of magnitude denser than ours, with a
synthetic target. A 0.30 on the primary is not pessimism; it is what the prior supports.

## D8. WHAT THIS DESIGN DELIBERATELY DOES NOT DO

- **No per-situation candidate sets / intersection scoring.** Retracted in-house on biology grounds
  (C3, section G.2).
- **No settling / CA3 completion in the scorer.** Floored three times, buys between -0.020 and +0.005
  over argmax and never widens the basin (ORGAN_MAP 10.1/D2).
- **No read-out variant hunting.** `NO_READOUT_VARIANT_CLEARS_THE_FLOOR`; cleanup changes the vector
  by 1.192e-07.
- **No per-raw-dimension reweighting of the bridged code.** Four nulls, all wrong-basis (ORGAN_MAP G3).
- **No use of `grounded_similarity()` as the scorer.** TRAP 1: 76.2% of SimLex pairs collapse onto two
  values. Use `grounded_vector` + raw cosine.
- **No wiring decision.** Phase 2 answers whether bridged codes carry meaning. WIRE-or-SHELVE is a
  separate act at land time.

---

# PART E -- WHAT I COULD NOT VERIFY

- **That any bridge is a CORRECT meaning.** Same limit as `frontier_distance`: nothing was
  hand-scored, here or there. `fruit --COPULA--> agent` remains a distance-1 edge and a bad definition.
- **ConceptNet / CSKG edge coverage of the SimLex vocabulary.** The files exist
  (`conceptnet-assertions-5.7.0.csv.gz` 498 MB, `cskg.tsv.gz` 112 MB) but I did not decompress and
  index them; the `B3_BRIDGE_CN` stratum size is UNKNOWN and must be measured before that arm is
  costed.
- **The multi-word-subject head-lemma reduction.** My graph reproduces the prior note's method
  (reduce to the last alphabetic token) and therefore inherits its bias: it COLLAPSES distinct terms
  (`dead zone` and `abyssal zone` both become `zone`), which INFLATES connectivity and so OVERSTATES
  my 220 / 66 / 392 counts. Treat them as upper bounds.
- **Whether the reading loop could mechanically traverse these edges.** This is a measurement over
  fact FILES. The live read-out's candidate set is `space.anchor_matrix()`, which these facts do not
  populate. I did not run the loop.
- **The citations in PART A were retrieved this pass and are not a replication audit.** Per the
  ORGAN_MAP provenance rule, treat each as a pointer to check before it becomes load-bearing. Two are
  flagged as actively contested in the text (fast mapping in amnesia; SLIMM).
- **The content-chunk substrate KB.** Un-queryable at present size (5 GiB allocation failure); the
  prior-work check leaned on filesystem enumeration instead, which is the stronger method anyway but
  is a different method than the standing discipline names.
- **Exact size of the human early grounded core.** Reported to an order of magnitude only; the
  literature's own counts depend on an unsettled root-vs-derived-form convention.
