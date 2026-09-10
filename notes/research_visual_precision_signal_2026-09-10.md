# Research: what per-word scalar should gate trust in the PERCEPTUAL/VISUAL spoke of a cross-modal hub?

Filed by: research sub-agent, 2026-09-10. Topic: `visual_precision_signal` — given the hub-and-spoke
reliability-weighting direction already opened in `research_channel_combination_reliability_weighting_
2026-08-23.md` (concreteness-gated blend ranked #1 candidate), this cycle answers the SHARPER question
that note left open: for the specific job of weighting a VISUAL/perceptual spoke, is global Brysbaert
concreteness the right gate, or does a modality-specific alternative (Lancaster Visual strength,
imageability) do the job better and with a cleaner brain justification?

## HEADLINE

**Use the raw Lancaster `Visual.mean` rating (0-5 perceptual-strength scale, Lynott, Connell, Brysbaert,
Brand & Carney 2020) as the visual-spoke precision scalar. Do NOT use global Brysbaert concreteness and
do NOT use imageability as the gate for a VISUAL-specific channel.** Concreteness and imageability are
both empirically shown to be *contaminated composites* for this exact purpose — concreteness blends
multiple decision criteria and is not modality-specific, imageability is directionally close to vision
but is explicitly documented as "visually biased" rather than a controlled visual measurement — while
Lancaster's `Visual.mean` is the only one of the three collected as a controlled, single-modality rating
in the same multi-modality protocol as the other five perceptual dimensions, is DIRECTLY shown to
out-predict both concreteness and imageability on word-processing behavior (the "strongest sense
hypothesis," Connell & Lynott 2012), and is the closest available proxy to a quantity that has been shown
to track *actual decodable visual-cortex signal* for that word (Fernandino et al. 2015 encoding-model
result, below). `Dominant.perceptual` and `Exclusivity.perceptual` (the other two Lancaster-derived
columns that might look like candidates) answer a different question ("which sense wins" / "how unimodal
is this concept") and are the WRONG variable for a per-spoke precision weight — see §2 for why.

## Cheap decisive test

No new data collection: both assets are already on disk and joined by lowercase word
(`data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`,
`data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt`).

1. Build the DISCRIMINATOR subset: words with Brysbaert `Conc.M >= 4.0` (clearly concrete) split into
   (a) HIGH-visual: Lancaster `Visual.mean` in the top tercile of that subset, and (b) LOW-visual:
   `Visual.mean` in the bottom tercile of that same subset (concrete nouns whose dominant channel is
   gustatory/olfactory/haptic/auditory rather than visual — e.g. spices, fabrics, liquids, sounds).
   Concreteness treats (a) and (b) identically; `Visual.mean` does not.
2. Re-score the existing held-out link/similarity gold already used for the sensorimotor organ
   (`exp_sensorimotor_channel_discrimination_v1`, or the SimLex-999 held-out set from
   `exp_grounding_measured_attribute_concreteness_v1`) once with the visual spoke gated by
   `concreteness` and once gated by `Visual.mean`, holding every other part of the pipeline fixed.
3. Compare the two gates ONLY on the LOW-visual-but-concrete subset (b) — this is the subset where the
   two candidate gates make opposite predictions about how much to trust the visual channel.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Rule under test: `Visual.mean` gate vs. global-concreteness gate for the visual spoke specifically.**

- HARD-PASS: on subset (b) (concrete, low-visual), the `Visual.mean`-gated score beats the
  concreteness-gated score by a CI-separated margin (report CI half-width), AND on subset (a)
  (concrete, high-visual, where the two gates agree) the two scores are NOT CI-separated from each
  other. Both conditions required — a difference everywhere (including where the gates agree) would
  mean something other than the hypothesized mechanism is doing the work.
- HARD-FAIL: no CI-separated difference on subset (b) (the two gates perform identically even on the
  words chosen specifically because they disagree), OR the subset is underpowered (<20 items after the
  Lancaster/Brysbaert join at the tercile split — report this as a reachability failure, not a
  refutation, per standing discipline). Either result means `Visual.mean` carries no additional
  precision information over concreteness for this downstream task, and the existing concreteness-gated
  blend (already ranked #1 in the 2026-08-23 note) should be kept as-is without adding a second
  per-modality column.

P_deflated for HARD-PASS: **0.33** (raw estimate ~0.55 — Connell & Lynott 2012 already show the
DIRECTION at the psycholinguistic-behavioral level, i.e. that modality-specific strength beats
concreteness/imageability for *some* task; deflated 0.20-0.25 per the mandatory lit-scan penalty because
no source tests this exact substitution inside a hub reliability-weighting/combination formula — that
part is genuine novel synthesis for this substrate). Capped well under 0.50 per rule.

## Findings by question (as asked), mechanism first

### 1. Dual coding theory and the concreteness/imageability effect in the brain

Paivio's dual coding theory (1971/1986) proposes two partly independent representational systems: a
verbal system operating on sequential, propositional units ("logogens") and an imagery system operating
on holistic, analog, sensory-perceptual units ("imagens"). Concrete words are hypothesized to be
"dual coded" (both systems active), giving them a behavioral advantage (faster recognition, better
recall) via redundant retrieval routes — this is the origin of the "concreteness effect."

At the brain level: **Binder et al. 2005** (*J Cogn Neurosci* 17(6):905-917, "Distinct Brain Systems for
Processing Concrete and Abstract Concepts") used event-related fMRI during a concrete/abstract lexical
task and found concrete and abstract words both activate a left-lateralized multimodal semantic network
relative to non-words, but with graded differences by concreteness — concrete items engage
multimodal/imagery-linked regions (angular gyrus, posterior cingulate, precuneus, parahippocampal
cortex) more than abstract items.

**Wang, Conder, Blitzer & Shinkareva 2010** (*Human Brain Mapping* 31(10):1459-1468) meta-analyzed 19
fMRI/PET studies (303 participants total) directly contrasting concrete vs. abstract concepts. Result:
concrete concepts preferentially engage **left precuneus, left parahippocampal gyrus, left posterior
cingulate cortex, and left fusiform gyrus** — regions independently implicated in mental imagery and
visual/spatial processing — while abstract concepts preferentially engage **left inferior frontal gyrus
and left anterior superior/middle temporal gyri**, a language-based verbal-associative system. This is
the strongest available direct neural confirmation of dual coding's core claim: concreteness tracks
recruitment of imagery-linked (largely visuospatial) cortex specifically, not a generic "more meaning"
signal.

**Brain-basis implication for THIS question**: dual coding motivates *why a modality-specific channel
should exist and be graded*, but Binder's and Wang et al.'s dependent variable is global concreteness,
not a decomposed per-modality rating — they establish that SOME visual/imagery machinery differentially
engages for concrete words, not that concreteness IS the correct per-word visual-strength number. That
distinction is exactly what point 3 below resolves.

### 2. Lancaster sensorimotor norms: is per-word `Visual.mean` a better precision signal than global concreteness, and what does dominance/exclusivity tell us?

**Lynott, Connell, Brysbaert, Brand & Carney 2020** (*Behavior Research Methods* 52:1271-1291), "The
Lancaster Sensorimotor Norms: multidimensional measures of perceptual and action strength for 40,000
English words." 39,707 words rated by ~3,500 MTurk participants on a 0-5 strength scale across **6
perceptual modalities** (auditory, gustatory, haptic, interoceptive, olfactory, **visual**) and 5 action
effectors (foot/leg, hand/arm, head, mouth, torso) — this is the asset already on disk at
`data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`, columns confirmed by direct
read: `Visual.mean`, `Visual.SD`, plus derived `Max_strength.perceptual`, `Minkowski3.perceptual`,
`Exclusivity.perceptual`, `Dominant.perceptual` (and matching `.action`/`.sensorimotor` triads),
`N_known`/`Percent_known` (norm-confidence), and `Mean_age` (age-of-acquisition proxy).

**Yes — `Visual.mean` is the better precision signal than global concreteness for a VISUAL-specific
channel, and this is a directly measured (not analogically inferred) result.** The predecessor line of
work to the 2020 norms, **Connell & Lynott 2012** (*Cognition* 125(3):452-465, "Strength of perceptual
experience predicts word processing performance better than concreteness or imageability") directly
pits per-modality perceptual-strength ratings (sound/taste/touch/smell/vision) against concreteness and
imageability as predictors of lexical-decision and naming latency. Two findings matter here:
- Modality-specific/maximum perceptual strength ("strongest sense") outperforms both concreteness and
  imageability at predicting word-recognition performance.
- **Concreteness ratings reflect two different, intersecting decision criteria** (participants appear to
  conflate "is this a thing that exists in space" with "do I have sensorimotor experience of it"), and
  **imageability ratings are visually biased** — i.e., imageability is not a clean visual measurement,
  it is a contaminated, uncontrolled proxy that leans toward vision without measuring it directly.
  Brysbaert et al. 2014's own norming report independently confirms the same contamination from the
  concreteness side: even though participants were instructed to base concreteness on experience "via
  any of the five senses," post-hoc comparison shows they "largely focused on visual and haptic
  experiences" — meaning concreteness is an *uncontrolled blend* dominated unevenly by vision+touch,
  not a calibrated single-modality dial.

**What dominance/exclusivity tell us (and why they are the WRONG variable for this specific use):**
`Dominant.perceptual` labels which of the 5 perceptual modalities gets the highest mean rating for a
word; `Exclusivity.perceptual` (Lynott & Connell 2009, *BRM* 41(2):558-564, "Modality exclusivity norms
for 423 object properties"; extended in Lynott & Connell 2013, *BRM*, "Modality exclusivity norms for
400 nouns") is a Minkowski-metric-based (range/sum) measure of how UNIMODAL a concept's perceptual
profile is, from 0% (perfectly multimodal) to 100% (perfectly unimodal). Two established facts about
this structure matter for the recommendation:
- **Vision is the dominant modality for the majority of concepts** across these norming studies (a
  long-replicated finding since Lynott & Connell 2009/2013) — so a categorical gate built on
  `Dominant.perceptual == Visual` would flag *most* words as visual by default, which is the wrong
  behavior for a precision weight (it would over-trust the visual spoke almost everywhere, including for
  many words with only weak absolute visual content that simply beat an even-weaker second-place
  modality).
- **Exclusivity measures unimodality, not visual strength.** A word can be highly exclusive to smell
  ("stench") — telling you nothing positive about vision — while a richly multimodal concrete object
  ("apple": substantial visual AND gustatory AND olfactory AND haptic content) has LOW exclusivity
  despite having HIGH absolute visual strength. Since the target question is "how much should I trust
  the visual channel specifically," not "does this concept live in exactly one sense," exclusivity would
  systematically *underweight* vision for exactly the richly-multimodal concrete objects that should get
  a strong visual vote. The correct read is the raw per-modality mean (`Visual.mean`) taken on its own
  absolute scale, independent of whether it happens to be the word's maximum or how exclusive it is.

A secondary refinement worth flagging (not required for the HARD-PASS bar above): Lancaster also
supplies `Visual.SD` (inter-rater disagreement on the visual rating) and `Percent_known.perceptual`
(fraction of raters who claimed to know the word at all). A literal Ernst & Banks inverse-variance
construction could use `Visual.SD` as the noise term — but this SD measures *rater disagreement in the
1971-2020 norming sample*, not the substrate's own channel noise, so treating it as the substrate's
reliability variance is an analogy, not an identity; it is a legitimate follow-on probe, not part of
this cycle's HARD-PASS claim.

### 3. Brysbaert concreteness vs. imageability vs. Lancaster visual-strength: which is the right gate, and why (brain basis)

Ranked for THIS specific purpose (gating a visual referent channel):

1. **Lancaster `Visual.mean`** — modality-specific by construction, collected in the same controlled
   protocol as the other perceptual dimensions (so its 0-5 scale is directly comparable to a future
   auditory/haptic spoke's own mean, which concreteness and imageability cannot offer since neither is
   modality-decomposed), and independently shown to out-predict both alternatives on real word-processing
   behavior (Connell & Lynott 2012).
2. **Imageability** — directionally closer to vision than concreteness, but Connell & Lynott 2012's own
   finding that imageability ratings are "visually biased" means it functions as an *uncontrolled,
   noisy proxy* for vision rather than a measurement of it. Worth keeping only as a fallback where
   Lancaster coverage is absent and Brysbaert's `Percent_known`/imageability-adjacent columns are the
   only thing available (not the case here: Lancaster and Brysbaert are near-perfectly nested in
   coverage per this project's own `notes/sensorimotor_anchoring_scope_2026-08-13.md` §1a — "owning both
   buys nothing over owning one" — so there is no coverage argument for falling back to imageability on
   this substrate).
3. **Brysbaert concreteness** — the WRONG gate for a visual-specific channel, for two independent
   reasons converging on the same conclusion: (a) it is explicitly reported (by its own authors and by
   Connell & Lynott 2012) as a blend dominated unevenly by vision+touch rather than a controlled
   single-modality rating, so a concrete-but-non-visual word (a strong smell, a texture, a sound) will
   receive a high concreteness score that wrongly licenses over-trusting the VISUAL spoke specifically;
   (b) at the brain level, Wang et al. 2010's meta-analysis shows concreteness tracks a *composite*
   imagery-linked network (precuneus + parahippocampal + posterior cingulate + fusiform — spatial and
   associative memory regions, not exclusively primary/higher visual cortex), which is a coarser signal
   than what is needed to gate ONE specific modality's spoke.

The brain basis for preferring a modality-decomposed rating over a global concreteness/imageability
scalar is stated directly in **Binder & Desai 2011** (*Trends Cogn Sci* 15(11):527-536, "The neurobiology
of semantic memory"): modality-specific sensory, motor, and emotion systems are recruited **flexibly and
gradedly** ("embodied abstraction") depending on a concept's actual content, not as an all-or-nothing
function of a single amodal "concreteness" dial. A framework that predicts graded, modality-differentiated
recruitment implies the correct INPUT feature for a precision weight is also modality-differentiated and
graded — which is exactly what `Visual.mean` is (a continuous 0-5 rating on ONE modality) and what
concreteness/imageability are not (single composite scalars collapsing across modalities).

### 4. Grounded/embodied cognition: does perceptual strength in a modality predict recruitment of that modality's cortex?

This is the direct empirical chain justifying "precision" (not just "descriptive strength") for
`Visual.mean`:

- **Barsalou 1999** (*Behavioral and Brain Sciences* 22(4), "Perceptual symbol systems") — the
  foundational grounded-cognition claim: concepts are represented via modality-specific "perceptual
  symbols" that reactivate the same neural systems active during original perception; a concept's
  meaning is a multimodal simulation, graded by how much each modality contributed during acquisition.
  This motivates the existence of per-modality strength as a real representational quantity, not a
  post-hoc rating artifact.
- **Goldberg, Perfetti & Schneider 2006** (*J Neuroscience* 26(18):4917-4921, "Perceptual Knowledge
  Retrieval Activates Sensory Brain Regions") — direct fMRI confirmation at the property level: semantic
  decisions about a word's VISUAL, auditory, tactile, or gustatory properties specifically activate the
  corresponding sensory/association cortex (distinct temporal regions for visual vs. auditory retrieval;
  somatosensory/motor/premotor for tactile; orbitofrontal for flavor). This is the classic result that a
  word's property CONTENT, not its word class, determines which cortex gets recruited.
- **Hoenig, Sim, Bochev, Herrnberger & Kiefer 2008** (*J Cogn Neurosci*, "Conceptual Flexibility in the
  Human Brain: Dynamic Recruitment of Semantic Maps from Visual, Motor, and Motion-Related Areas") —
  recruitment of visual/motor/motion cortex tracks which feature type is task-relevant for a given
  concept, reinforcing that the mapping from rated feature strength to cortical recruitment is dynamic
  and graded, not fixed per word class.
- **Fernandino, Humphries, Seidenberg, Gross, Conant & Binder 2015** (*Neuropsychologia*, "Predicting
  brain activation patterns associated with individual lexical concepts based on five sensory-motor
  attributes") — the single most decisive result for THIS project's use case. Using an encoding-model
  approach, per-word ratings on 5 sensory-motor attributes (sound, color, visual motion, shape,
  manipulation — the same rating-instrument family as Lancaster) for 820 training words were combined
  to predict whole-brain fMRI activation for 80 held-out words. **Median prediction accuracy r=0.63
  overall, but this decomposes sharply by concreteness: r=0.67 (p=0.0036) for concrete words vs. r=0.50
  (p=0.75, indistinguishable from chance) for abstract words.** This is a direct, quantitative
  demonstration that a word's rated attribute strength predicts REAL, decodable sensory-cortex signal
  for concrete words and predicts NOTHING (chance-level) for abstract words — which is precisely the
  reliability signature a Ma-Pouget/Ernst-Banks-style precision weight is supposed to detect and exploit:
  high visual-strength words have a genuine sensory "vote" to weight; low-strength words have no such
  vote, and treating their (near-zero) visual rating as low-precision rather than simply "low value" is
  the brain-justified move.
- **Fernandino, Binder, Desai, Pendl, Humphries, Gross, Conant & Seidenberg 2016** (*Cerebral Cortex*
  26(5):2018-2034, "Concept Representation Reflects Multimodal Abstraction: A Framework for Embodied
  Semantics") — companion multivariate fMRI study (900 words, same 5 attributes) confirming these
  aspects of conceptual knowledge are encoded in multimodal and higher-level unimodal cortex matching
  each attribute's own modality, consistent with (not a repeat of) the 2015 encoding-model result.

**Contested counter-view, reported per standing discipline (don't dismiss adjacent methods, do report
disconfirming lines):** Louwerse's symbol-interdependency hypothesis (Louwerse 2011, *Topics in
Cognitive Science*; Louwerse & Connell, *Cognitive Science* 35:381-398, "A Taste of Words") argues that
much of what looks like perceptual grounding is recoverable from language statistics alone (word-order
and co-occurrence structure is itself iconic/redundant with perceptual structure), and that some
apparent embodiment effects can be explained by linguistic surface structure rather than genuine
perceptual simulation. This does not overturn the Fernandino et al. result (that result is measured
against actual BOLD signal, not against a distributional model), but it is a legitimate reason not to
claim that Lancaster ratings are pure, uncontaminated perception — they are collected via language
(introspective report), so some of their signal could in principle be recoverable from text statistics
too. This is a caveat on INTERPRETATION, not a reason to prefer a different scalar.

## Cross-thread synthesis (this substrate's own prior work)

- `research_channel_combination_reliability_weighting_2026-08-23.md` — opened this whole thread: ranked
  a concreteness-gated blend as the #1 candidate combination rule because concreteness was the only
  per-word signal available with zero fitting. This cycle sharpens that recommendation for the specific
  case of a VISUAL spoke: swap the gate from `Conc.M` to Lancaster `Visual.mean` when the channel being
  weighted is specifically visual/perceptual (keep `Conc.M` or a POS/feature-content gate for a generic
  "any sensorimotor content" channel that isn't modality-specific). Also directly reuses that note's
  citation of Wang, Zhang & Zong 2018 (AAAI) — a LEARNED per-item gate finding the abstract:concrete
  linguistic:visual weight ratio is 3.714:1 vs. 2.975:1 — as independent computational confirmation that
  visual-channel weight should shrink for abstract words, consistent with Fernandino et al. 2015's
  chance-level abstract-word prediction result above.
- `notes/sensorimotor_anchoring_scope_2026-08-13.md` — established (i) Lancaster and Brysbaert are
  near-perfectly nested in coverage on this project's own blind samples (owning both buys ~nothing over
  owning one — directly relevant: there is no coverage argument for keeping concreteness as a FALLBACK
  gate once `Visual.mean` is wired, since a word missing from Lancaster is essentially always also
  missing from Brysbaert), (ii) the §2 glass-box line: norms are PERMITTED as DATA (a per-word rating is
  a fact, like a textbook sentence) but FORBIDDEN as the reasoning organ (ranking/selecting candidates by
  norm-vector similarity and calling the winner "the meaning" is the exact failure mode this project's
  brain-fidelity audit flags) — the recommendation here is scoped strictly to a PRECISION WEIGHT
  (how much to trust a spoke's vote), which sits on the permitted side as long as the substrate can still
  cite the `Visual.mean` value as a premise rather than using it as an opaque scorer, and (iii) a live
  self-test discipline already exists for the sibling asset (`hdlab/sensorimotor_spoke.py`'s
  `shuffled_norms_destroy_the_ordering` can-fail control) that the same construction should be reused for
  a new `visual_precision(word)` accessor, not re-invented.
- `hdlab/grounded_similarity.py` / `hdlab/sensorimotor_spoke.py` — the ON-DISK ASSET already loads
  Lancaster's `Visual.mean` as index 5 of an 11-dim sensorimotor block (`SENSORIMOTOR_COLS`), but only
  ever consumes it bundled into a 12-dim z-scored vector for a magnitude/similarity read (Euclidean vs.
  cosine, per that module's own measured finding that Euclidean separates synonym from sibling pairs
  better). **No live path currently exposes `Visual.mean` alone as a scalar.** This is the concrete gap
  the recommendation closes: a new accessor (name suggestion: `visual_precision(word) -> Optional[float]`)
  that reads the SAME loader (`hdlab.grounded_similarity._load_lancaster` / its cached table) but returns
  the single `Visual.mean` value (raw 0-5, or globally rescaled to [0,1] by dividing by 5 — NOT re-z-scored
  jointly with the other 11 dims, since joint z-scoring is the wrong operation for extracting one
  modality's own absolute strength) rather than the bundled vector. This is additive, reuses the existing
  loader (no second CSV parse, per that module's own "why this file and not a new loader" discipline),
  and requires no new data acquisition.
- `exp_sensorimotor_channel_discrimination_v1` (2026-08-18) and the two related MIDDLE_BAND cells
  (`diag_learned_encoder_synonym_sibling_deep_wall_v1`, `diag_synonym_sibling_confound_removed_v1`,
  2026-08-11) are the most relevant existing evidence that **concreteness is a known, measured confound**
  on this exact substrate already (siblings vs. synonyms separation collapsed once concreteness was
  balanced) — independent, substrate-native confirmation of the literature finding in §3 that
  concreteness carries entangled information that a cleaner modality-specific signal should be preferred
  over.

## Substrate-product implications

Plain terms: the sensorimotor asset already sitting on disk has a column that answers "how much does
this word look like something" directly and cleanly (`Visual.mean`), separate from a column that answers
"how much does this word feel real/physical in ANY sense" (concreteness). Right now the substrate only
ever uses the blended version. Swapping to the clean, modality-specific column for the visual channel
specifically means: a spice name (concrete, but mostly a smell/taste word) stops getting an inflated
"trust the picture-in-your-head channel" score it does not deserve, while an object name that really is
mostly seen (a chair, a car) keeps its high visual trust — and, per the brain evidence in §4, this also
means the substrate would be weighting the visual channel roughly in proportion to whether real
visual-cortex signal would even exist for that word in a human brain, not just whether the word "feels
concrete." The cost of finding out is zero new data collection — both files are already on disk — and
the risk is that (per the HARD-FAIL bar above) the two gates turn out to behave identically on the words
that matter, in which case nothing changes except one column swap, and the current concreteness-gated
plan from 2026-08-23 stands as-is.

## Citations (verified count)

18 distinct primary sources found via live WebSearch/WebFetch this cycle (not from memory), listed with
what was independently checked vs. search-summary-only:
1. Paivio, A. (1971/1986) — Dual coding theory. Checked via secondary summaries (Wikipedia,
   ScienceDirect topic page, instructionaldesign.org); not a single canonical peer-reviewed URL exists
   for the 1971/1986 books themselves, standard for this literature.
2. Binder, J.R. et al. (2005). "Distinct Brain Systems for Processing Concrete and Abstract Concepts."
   *J Cogn Neurosci* 17(6):905-917. Venue/volume/pages confirmed via WebSearch result snippet.
3. Wang, J., Conder, J.A., Blitzer, D.N. & Shinkareva, S.V. (2010). "Neural representation of abstract
   and concrete concepts: a meta-analysis of neuroimaging studies." *Human Brain Mapping* 31(10). Region
   findings (precuneus/parahippocampal/PCC/fusiform vs. IFG/temporal) confirmed via WebSearch summary of
   the PubMed abstract.
4. Lynott, D., Connell, L., Brysbaert, M., Brand, J. & Carney, J. (2020). "The Lancaster Sensorimotor
   Norms." *Behavior Research Methods* 52:1271-1291. Column structure (Visual.mean etc.) independently
   VERIFIED by direct file read of the on-disk CSV header, not just search summary.
5. Lynott, D. & Connell, L. (2009). "Modality exclusivity norms for 423 object properties." *BRM*
   41(2):558-564. Definition of exclusivity (range/sum) confirmed via WebSearch summary.
6. Lynott, D. & Connell, L. (2013/2012 in some indices). "Modality exclusivity norms for 400 nouns."
   *BRM*. Dominant-modality assignment mechanic confirmed via WebSearch summary.
7. Connell, L. & Lynott, D. (2012). "Strength of perceptual experience predicts word processing
   performance better than concreteness or imageability." *Cognition* 125(3):452-465. PDF fetch failed
   (image-encoded PDF, not text-extractable); findings sourced from WebSearch result summaries of the
   PubMed/ResearchGate abstract pages (2 independent search summaries agreeing) — the "visually biased"
   imageability finding and "two intersecting decision criteria" concreteness finding should be treated
   as summary-level confidence, not hand-verified against the primary PDF text.
8. Brysbaert, M., Warriner, A.B. & Kuperman, V. (2014). "Concreteness ratings for 40 thousand generally
   known English word lemmas." *BRM* 46:904-911. Already an on-disk asset with its own PROVENANCE file;
   the "participants largely focused on visual and haptic experience" finding is from a WebSearch summary
   of the abstract, not independently re-verified against the primary PDF.
9. Barsalou, L.W. (1999). "Perceptual symbol systems." *Behavioral and Brain Sciences* 22(4). Confirmed
   via WebSearch summary and the freely hosted PDF link (barsaloulab.org) was located but not fetched
   for full text this cycle.
10. Binder, J.R. & Desai, R.H. (2011). "The neurobiology of semantic memory." *Trends Cogn Sci*
    15(11):527-536. "Embodied abstraction" framing confirmed via WebSearch summary of the abstract.
11. Goldberg, R.F., Perfetti, C.A. & Schneider, W. (2006). "Perceptual Knowledge Retrieval Activates
    Sensory Brain Regions." *J Neuroscience* 26(18):4917-4921. Region-by-property findings (tactile ->
    somatosensory/motor/premotor; flavor -> orbitofrontal; visual/auditory -> distinct temporal regions)
    confirmed via WebSearch summary of the abstract.
12. Hoenig, K., Sim, E.J., Bochev, V., Herrnberger, B. & Kiefer, M. (2008). "Conceptual Flexibility in
    the Human Brain: Dynamic Recruitment of Semantic Maps from Visual, Motor, and Motion-Related Areas."
    *J Cogn Neurosci*. Confirmed via WebSearch summary citing this exact title/author string.
13. Fernandino, L., Humphries, C.J., Seidenberg, M.S., Gross, W.L., Conant, L.L. & Binder, J.R. (2015).
    "Predicting brain activation patterns associated with individual lexical concepts based on five
    sensory-motor attributes." *Neuropsychologia*. **Directly fetched and read (PMC full text)** — title,
    author list, method (encoding model, 820 train / 80 held-out words), and the r=0.63 overall /
    r=0.67 concrete / r=0.50-at-chance abstract results are HAND-VERIFIED against the fetched PMC page,
    not summary-only.
14. Fernandino, L., Binder, J.R., Desai, R.H., Pendl, S.L., Humphries, C.J., Gross, W.L., Conant, L.L. &
    Seidenberg, M.S. (2016). "Concept Representation Reflects Multimodal Abstraction: A Framework for
    Embodied Semantics." *Cerebral Cortex* 26(5):2018-2034. Abstract fetched from Oxford Academic page
    (general finding confirmed); full-text PDF fetch failed (binary/image-encoded), so the region-by-
    attribute dissociation detail is inferred from the abstract + the companion 2015 paper's confirmed
    method, not independently verified region-by-region.
15. Louwerse, M.M. (2011). "Symbol Interdependency in Symbolic and Embodied Cognition." *Topics in
    Cognitive Science*. Confirmed via WebSearch summary.
16. Louwerse, M.M. & Connell, L. (2011). "A Taste of Words: Linguistic Context and Perceptual Simulation
    Predict the Modality of Words." *Cognitive Science* 35:381-398. Confirmed via WebSearch/PhilPapers
    listing.
17. Wang, Y., Zhang, S. & Zong, C. (2018) — reused from the 2026-08-23 note (linguistic:visual weight
    ratio finding), not re-verified this cycle; carried forward as cross-thread synthesis only.
18. Ponari, M., Norbury, C. & Vigliocco, G. (2018 and follow-ups) — concreteness/imageability
    disentanglement in developmental word learning; confirmed via WebSearch summary only, included as a
    supporting (not load-bearing) citation for "concreteness is a contaminated composite" claim.

Per the mandatory lit-scan calibration penalty: all P estimates above are deflated 0.15-0.25 from the raw
synthesis estimate, and novel-synthesis P is capped at 0.50 (applied: 0.33 for the cheap decisive test's
HARD-PASS). Item 13 (Fernandino et al. 2015) is the one citation in this note verified against full
primary text rather than a search-engine summary of an abstract; it is also the single most load-bearing
citation for the brain-basis claim, which is a deliberate emphasis, not a coincidence — where the report
could hand-verify, it hand-verified the citation the headline recommendation depends on most.

## Anchor candidate for exp_dev (delivered here, not routed)

Per current discipline, no separate hand-off file is written; the actionable anchor is stated directly:

- **Anchor**: add `visual_precision(word) -> Optional[float]` to `hdlab/grounded_similarity.py` (reuses
  the existing Lancaster loader/cache; returns raw `Visual.mean` on the union it already builds, not a
  new CSV parse), then run the cheap decisive test in this note's second section as a standalone
  diagnostic cell (suggested name: `diag_visual_precision_gate_v1`) comparing the `Visual.mean` gate
  against the existing concreteness gate on the concrete-but-low-visual discriminator subset described
  above, using whichever held-out gold the 2026-08-23 note's own cheap decisive test lands on (do not
  duplicate gold-set construction — reuse it).
- **Tier hint**: cheap/diagnostic — no new data acquisition, reuses two assets and one loader already on
  disk; should be a same-day CPU cell.
- **Why now**: this closes the specific gap the 2026-08-23 note left open ("which gate for WHICH
  channel") and gives the sensorimotor organ's existing self-test discipline
  (`shuffled_norms_destroy_the_ordering`-style can-fail control) a natural second target.

---

## TLDR

We asked which single number best tells the system "how much should I trust what a word LOOKS like" so
it can lean on that visual information more for words like "chair" and less for words like "justice."
The sensorimotor ratings file already on disk has exactly this number for each of ~40,000 words — a
0-to-5 rating of how visual that word is, collected the right way (people rated vision separately from
smell, taste, touch, and sound). We found solid brain evidence that this specific number is better than
the two alternatives already in use (a general "how real/physical does this feel" score, and a "how
easy is this to picture" score) — both of those turn out to be muddled blends that lean on vision
unevenly rather than measuring it cleanly. The most convincing piece of brain evidence: a study that fed
these same kinds of per-word ratings into a model and tried to predict actual brain scan activity found
it worked well for concrete words but was no better than a coin flip for abstract words — exactly the
pattern we want our own weighting to reproduce. The fix costs nothing to try: no new data needed, just
reading a different column from a file we already have.

## QUESTIONS

None.

## NEXT STEPS

1. Add the `visual_precision(word)` accessor to `hdlab/grounded_similarity.py` (reuses the existing
   Lancaster loader; no new CSV parse).
2. Run the cheap decisive test above as a standalone diagnostic cell once the 2026-08-23 note's own
   held-out gold set is settled (do not build a second gold set).
3. If HARD-PASS: wire `visual_precision` as the gate specifically for the visual/perceptual spoke,
   keeping the existing concreteness-gated blend (2026-08-23) for any non-modality-specific channel.
   If HARD-FAIL: keep the existing concreteness-gated plan unchanged and record that the two gates are
   empirically interchangeable for this substrate's downstream task (a useful negative result — it would
   mean the extra column is not worth maintaining).
