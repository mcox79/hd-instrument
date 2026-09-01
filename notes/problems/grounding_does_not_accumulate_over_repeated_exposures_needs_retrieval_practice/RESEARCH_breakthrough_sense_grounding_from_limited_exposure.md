# RESEARCH DRILL -- breaking the ~0.45 plateau: grounding a hard sense by RELATION to the KNOWN lexicon, not from sparse context

Lead-with-biology deep drill for the SOLVER on
`grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice`.
Generic-terms-only scan. Lit-scan calibration penalty applied (expected lifts deflated 0.15-0.25;
novel-synthesis confidence capped at P<=0.50). Date: 2026-09-01.

**Fourth drill. Do NOT duplicate the three on disk:**
- `RESEARCH_sense_selection_mechanism.md` -- pinned the COMBINATION RULE (reliability-weighted == product-of-experts) + per-word running prototype.
- `RESEARCH_accumulation_and_cross_situational_learning.md` -- accumulation is second-order here; carry MULTIPLE senses; morphology.
- `RESEARCH_toward_ceiling_sense_selection.md` -- ceiling ~0.85; context-gating is the pinned lever BUT (crucially) it was PROTOTYPED TWO WAYS and it FAILED on this population (context DILUTES not SHARPENS, because these words' contexts are low-coherence 0.09-0.13).

This drill attacks the axis the first three left open: **all three assumed grounding is built by SELECTING over feature-vector cosines computed FROM the occurrence's context. This drill argues the missing ingredient is a change in KIND -- grounding a hard word by placing it into a RELATIONAL structure of ALREADY-KNOWN grounded concepts (a graph), not by averaging or cosine-matching feature vectors read off sparse context.** That reframe is what makes the recommendation new rather than a re-run of the failed context-gating.

---

## 0. THE DECISIVE FRAME (from the on-disk evidence, restated so the biology can bite)

Established on disk, do NOT re-derive:
1. The correct anchor is RETRIEVABLE (top-10 ~85%) but NOT SELECTABLE by any distributional read-out (nearest/bg-subtract/distilled/supervised all ~0.21-0.24). The signal separating the correct SENSE from the topical ASSOCIATE is **genuinely absent from distributional co-occurrence**.
2. A grounded (feature-vector) re-rank roughly DOUBLES selection to ~0.45 -- our best -- but it is a static per-word **sense-BLEND** and it **plateaus at ~0.45** (within-set ceiling ~0.85).
3. Occurrence-context grounding (context-gating; mean-Binder of the actual context words) LOSES to the static blend, because averaging a hard word's neighbours' experiential features is BLURRIER than the word's own grounding.
4. Occurrence-CLUSTERING sense-induction (split a word's 4 occurrences into senses) is seed-UNSTABLE (recovery 0.4-4%).

The single fact that reorganises the whole problem: **the on-disk failure is exactly the syntagmatic-vs-paradigmatic split -- and that split is a PINNED, doubly-dissociated brain fact with a name.** whisky~wedding (the nearest distributional neighbour) is a THEMATIC relation; whisky~brandy (the correct anchor at rank ~3) is a TAXONOMIC relation. **Our distributional channel is a thematic machine; the correct-sense signal lives in the taxonomic system.** Everything below is scored against that, and it is what makes the recommendation decisive.

---

## TOPIC 3 FIRST (it is the load-bearing pin) -- TAXONOMIC vs THEMATIC: the correct-sense signal is RELATIONAL, in a different store than distributional context

### What the biology PINS

- **Two parallel, complementary, doubly-dissociated semantic systems.** Taxonomic relations = similarity/shared-feature relations (dog~bear, whisky~brandy, mole~cat); thematic relations = contiguity/co-occurrence-in-an-event relations (dog~leash, whisky~wedding, mole~earth) (Mirman, Landrigan & Britt 2017, *Psych Bulletin*, "Taxonomic and thematic semantic systems"). They are two DIFFERENT organisations of meaning, not two ends of one scale.
- **They are neuroanatomically dissociated -- the DUAL-HUB account.** Anterior temporal lobe (ATL) supports TAXONOMIC relations (shared colour/shape/experiential features); temporoparietal cortex (TPJ / posterior MTG / angular gyrus) supports THEMATIC relations (action/location/co-occurrence) (Schwartz, Kimberg, Walker et al. 2011, *PNAS*, "Neuroanatomical dissociation for taxonomic and thematic knowledge"; Jackson/Lambon Ralph dual-hub; confirmed fMRI/MEG/iEEG/lesion, Mirman review). Taxonomic errors localise to left ATL; thematic errors to left TPJ.
- **The feature basis differs, and it names our fix.** Taxonomic relatedness is driven by **visual/experiential shared features**; thematic relatedness by **verbal/co-occurrence and action/location**. This is the precise reason our GROUNDED (Binder/sensorimotor) re-rank worked at all where distributional failed: grounded features are the TAXONOMIC substrate, distributional co-occurrence is the THEMATIC substrate.

### Why this both EXPLAINS our ~0.45 and shows the way THROUGH it

Our grounded cascade already reached into the taxonomic system -- that is the ~0.24 -> ~0.45 doubling. **But it did so with a FLAT FEATURE-VECTOR COSINE, which is a weak, lossy proxy for what the ATL taxonomic system actually is: a RELATIONAL STRUCTURE (an is-a / shares-features graph).** Two words can be taxonomically close (same superordinate, share defining features) while their 65-dim Binder cosines are only middling, and two words can have high Binder cosine by accident of a few loud dimensions without being the same KIND. The plateau at ~0.45 is the ceiling of *cosine-over-a-static-blend*, not the ceiling of *taxonomic selection*.

**The pinned computational upgrade is STRUCTURED / RELATIONAL disambiguation over a taxonomic graph.** This is a mature, unsupervised, glass-box family in NLP and it uses exactly the resource we already hold (WordNet is a taxonomic is-a graph):
- **Structural Semantic Interconnections (SSI)** (Navigli & Velardi 2005, *IEEE TPAMI*): build the structural specification of each candidate sense and select the hypothesis whose relational interconnections to the context best satisfy a grammar of semantic relations. Performance rises with the RICHNESS of the knowledge base's relations; higher than flat knowledge-based methods.
- **Personalized-PageRank / random-walk WSD (UKB)** (Agirre, Lopez de Lacalle & Soroa 2014, *Computational Linguistics*, "Random Walks for Knowledge-Based WSD"; Agirre & Soroa 2009): insert the CONTEXT words as seed nodes into the WordNet graph, run a personalized random walk, and the candidate synset that accumulates the most probability mass IS the selection. Unsupervised, uses the full relational graph, beats flat graph methods.
- **Extended-gloss overlap** (Banerjee & Pedersen 2003; Lesk 1986): score a candidate sense by the relational-neighbourhood overlap of its gloss with the context -- a relational, not cosine, match.

The move: **replace "argmax cosine(candidate_feature_vector, target_feature_vector)" with "argmax relational-coherence(candidate_sense, {known grounded anchors observed in this occurrence}) over the WordNet taxonomic graph."** The selection signal becomes graph connectivity in the taxonomic store, which is the ATL mechanism, not a feature average.

**This is NOT the failed context-gating.** Context-gating AVERAGED the feature vectors of context words (blurry -> lost). The relational move uses context words only to IDENTIFY SEED NODES (which known grounded anchors are present), then lets the GRAPH do the disambiguation by walking from those seeds. Different operation; the negative does not transfer.

---

## TOPIC 1 -- how the brain grounds a NEW/hard sense from limited exposure: NOT from context, BY RELATION to the known network

### What the biology PINS

- **Fast mapping is only a provisional first step; durable meaning is EXTENDED/SLOW mapping** (Carey & Bartlett 1978; Carey 1978; Swingley 2010, "Fast mapping and slow mapping in children's word learning"; Horst & Samuelson 2008). Slow mapping = "encoding, consolidation, retrieval, and re-encoding across multiple experiences" that gradually REFINES a representation. Our 4-exposure regime is the fast-map stage, which is *expected* to be provisional -- see Topic 4.
- **The mechanism of the fast/slow map is INTEGRATION INTO AN EXISTING NETWORK, not construction from scratch.** Fast mapping recruits the ATL and integrates the novel item into EXISTING semantic networks, and it does so via SCHEMA: when a relevant associative schema already exists, a single trial becomes assimilated and rapidly hippocampal-independent (Tse, Langston, Kakeyama et al. 2007, *Science*, "Schemas and memory consolidation"; Sharon, Moscovitch & Gilboa 2011, *PNAS*, rapid neocortical acquisition via fast mapping; Coutanche & Thompson-Schill). The predictor of fast-map success is ATL (taxonomic hub), NOT hippocampus. **The known lexicon IS the schema.**
- **Grounding-by-RELATION / structure-mapping is a pinned route to meaning.** Analogical alignment underlies word learning: children infer a new word's meaning by ALIGNING it with known structure (Gentner structure-mapping; Gentner & Namy analogical word learning; Gleitman's structure-mapping in verb learning). **RELATIONAL grounding** -- acquiring a word's meaning from its intralinguistic relations to KNOWN words ("bachelor" grounded as unmarried + male) -- is an explicit, pinned grounding route (Ramscar 2003, *Cognitive Science*, "Semantic grounding in models of analogy"). Meaning is partly DETERMINED by relations to other words.

### The reframe this forces on our failure

We have been trying to ground a hard word FROM its sparse, low-coherence contexts (context-gating, occurrence-clustering) -- and it fails because those contexts are genuinely thin. **The brain does not primarily ground a hard word from its sparse contexts; it grounds it by RELATING it to the already-known grounded network.** Our anchor pool of known grounded words is not merely a candidate list to cosine-match against -- it is the RELATIONAL SCHEMA into which the new sense is placed, and the new sense's POSITION relative to those anchors (its graph neighbourhood) IS its grounding. This is Topic 3's mechanism seen from the learning side: select/ground the sense by its relational fit to the known anchors, not by a feature read off context.

---

## TOPIC 2 -- the situation model: STRUCTURED, not a bag -- but honest about the regime

### What the biology PINS

- **The situation model is a STRUCTURED, relational event representation, integrated by ARGUMENT OVERLAP -- not a bag of words.** Event-indexing model (Zwaan, Langston & Graesser 1995; Zwaan & Radvansky 1998, *Psych Bulletin*): each clause forms an EVENT representation, integrated with working memory along FIVE dimensions -- **time, space, entity/protagonist, causation, intentionality/motivation** -- by overlap on each dimension. Disambiguation happens because the word must fit the WHO-DID-WHAT-TO-WHOM structure, not because it is near some average.
- **Those five dimensions MAP onto the experiential dimensions we already hold.** Space, Time, Causal, Social, Cognition are Binder-2016 domains. So the structured situation model is expressible in our grounded feature space -- but as a STRUCTURE over roles, not a flat mean.
- **Structure disambiguates via the sentence FRAME (syntactic bootstrapping).** Word-world co-occurrence is provably insufficient for verb meaning; the argument-structure frame constrains the meaning (Gleitman 1990 syntactic bootstrapping; Landau & Gleitman; Naigles). "Who did what to whom" is a relational constraint a bag-of-words throws away.

### The HONEST verdict for our population (this is where the on-disk fact bites, again)

A richer situation model built over the SAME thin contexts is unlikely to break the wall here, and the disk already shows it: **the full SYNTACTIC/dependency-parse encoder did NOT beat the incumbent** (still ~0.27; every encoder retrieves the anchor to top-10 ~85% and none selects it). And the two context-gating prototypes that DID try to use the occurrence context lost to static grounding. **On a 4-exposure, split-half-coherence-0.09-0.13 corpus, there is not enough structured event material in the target's own contexts to build a disambiguating situation model.** The brain's situation model works because it is fed by WORLD KNOWLEDGE, INFERENCE, working memory, and a rich pre-existing grounded network -- not by four thin text windows.

**So the situation-model insight is best cashed NOT as a richer bag, but as STRUCTURED SEEDING of the relational selector (Topic 3):** use the occurrence's argument structure / co-arguments to pick WHICH known grounded anchors are the relational seeds (the target's syntactic neighbours, the entities it is predicated of), and seed the graph walk from THOSE -- a structured, role-filtered seed set, rather than an average over all neighbours. This is the one place the parser/structure earns its keep, and it is second-order to the relational selector itself.

---

## TOPIC 4 -- episodic->semantic + THE REGIME QUESTION (the most important honest finding)

### What the biology PINS

- **Complementary Learning Systems + schema-facilitated consolidation** (McClelland, McNaughton & O'Reilly 1995; Tse 2007; Kumaran, Hassabis & McClelland 2016): a sense is EXTRACTED slowly across episodes into a neocortical schema -- and if a schema already exists, integration is fast. Confirms Topic 1: the durable representation is the one INTEGRATED INTO the existing network.
- **The exposure REGIME is decisive, and 4 thin text exposures is NOT the brain's regime.** Incidental meaning-learning from text is ~15%/exposure (Nagy & Anderson; Swanborn & de Glopper 2000); full learning needs many exposures -- English learners need **up to ~14 exposures**, and the number required is dominated by the QUALITY/supportiveness of the context (joint attention, book reading, sophisticated-vocabulary settings) (Weizman & Snow 2001, "Lexical input as related to children's vocabulary acquisition"). Repeated exposure helps most in the FIRST few, and MULTIMODAL exposure accelerates it.
- **"A definition (relational scaffold) can substitute for many observed contexts."** Borman & Lupyan (Evolang, "How many words is a picture or definition worth?"): more ostensive/observational experiences are NOT necessarily more effective than indirect learning of how a word is used -- a DEFINITION (a relational, structured specification) is a high-value grounding source. This is the pinned licence for the offline-foundation route: a clean relational gloss beats N noisy contexts.

### The honest conclusion the regime forces

The brain grounds these words because it has (i) far more + higher-QUALITY + MULTIMODAL exposures and (ii) a rich pre-existing grounded relational network into which to integrate. We have neither the exposures nor (yet) the relational network turned ON. **Squeezing more from four low-coherence text windows is fighting the regime.** The brain-faithful move is to supply the pre-existing relational structure OFFLINE -- which our project's FOUNDATION pivot explicitly permits (a static, offline-built asset from external tools is admissible; NO external LLM at inference). We already hold that asset (WordNet taxonomic graph + glosses + the grounded anchor pool); we are just not using its STRUCTURE.

---

## PINNED vs OUR-INVENTION -- one-glance table

| Design element | Status | Anchor |
|---|---|---|
| Taxonomic vs thematic are two dissociated semantic systems | PINNED | Mirman, Landrigan & Britt 2017 |
| Correct-sense (paradigmatic) = TAXONOMIC (ATL); distributional context = THEMATIC (TPJ) | PINNED (dual-hub) | Schwartz 2011 PNAS; Jackson/Lambon Ralph |
| Taxonomic relatedness driven by shared experiential/visual features; thematic by co-occurrence/action | PINNED | Mirman review; fMRI meta-analysis |
| Structured/relational graph disambiguation over a taxonomic KB (SSI / personalized-PageRank / extended-gloss) | PINNED (computational, unsupervised, mature) | Navigli & Velardi 2005; Agirre et al. 2014; Banerjee & Pedersen 2003 |
| Grounding a new word = INTEGRATE into existing network via schema; predicted by ATL not hippocampus | PINNED | Tse 2007; Sharon 2011; Coutanche |
| Fast map is provisional; durable meaning is slow extended mapping | PINNED | Carey 1978; Swingley 2010; Horst & Samuelson 2008 |
| Grounding-by-relation / structure-mapping (bachelor = unmarried+male) | PINNED | Gentner; Ramscar 2003; Gleitman |
| Situation model is STRUCTURED (5 dims, argument overlap), not a bag | PINNED | Zwaan & Radvansky 1998; Zwaan/Langston/Graesser 1995 |
| Sentence FRAME constrains meaning (syntactic bootstrapping) | PINNED | Gleitman 1990; Naigles |
| A richer situation model over OUR thin 4-exposure contexts will select better | NOT SUPPORTED for our case (on-disk: full parser did not beat incumbent; context-gating lost) | on-disk |
| Regime: durable meaning needs many QUALITY + MULTIMODAL exposures; ~4 thin text windows is fast-map only | PINNED | Nagy & Anderson; Weizman & Snow 2001 |
| A definition/relational scaffold is worth many observed contexts | PINNED | Borman & Lupyan (Evolang) |
| Gloss-grounded per-sense prototype (ground each WordNet sense by its gloss, offline) | OUR-INVENTION, tightly constrained by LMMS + the above | Loureiro & Jorge 2019 (LMMS) analogue |
| Relational selection SEEDED BY GROUNDED anchors (grounded-relational hybrid) | OUR-INVENTION, constrained by dual-hub + PPR-WSD | -- |

---

## DECISIVE RECOMMENDATION -- the ONE mechanism most likely to break ~0.45

**Build a STRUCTURED, RELATIONAL, GLOSS-GROUNDED sense selector: ground each candidate sense OFFLINE from its WordNet gloss (not from the target's blended context), then SELECT by relational coherence to the KNOWN GROUNDED ANCHORS present in the occurrence -- over the WordNet taxonomic graph -- instead of by cosine over a static per-word feature blend.**

Two moves, both offline, both from assets we already hold, both glass-box, NO external LLM at inference:

1. **Per-sense grounding from GLOSSES (sidesteps the sense-induction wall).** For each candidate synset in the distributional top-K shortlist, take its WordNet gloss + synonyms + direct relational neighbours (hypernym, key co-hyponyms), look up their predicted-Binder-65, and aggregate into a per-SENSE grounded prototype. This replaces the static per-WORD sense-BLEND (the ~0.45 ceiling's cause) with a clean per-SENSE vector -- **without** the unstable occurrence-CLUSTERING that recovers only 0.4-4%. The senses and their glosses come from WordNet offline (stable, free); we never have to induce senses from 4 noisy occurrences. This is the LMMS idea, but built from glosses (offline) rather than from occurrence clusters (unstable) -- the key improvement over the prior drills' per-sense fallback.

2. **RELATIONAL selection seeded by grounded anchors (supplies the taxonomic signal).** From the occurrence, collect the KNOWN grounded anchor words present (the anchor pool -- already BUILT, default-off: `exp_anchor_pool_expansion_v1`, `process_sentence(anchor_pool=...)`). Seed those into the WordNet graph and run a personalized random walk (UKB-style) OR score each gloss-grounded candidate by relational-coherence to the seed set. The candidate sense that is most relationally coherent with the known grounded anchors wins. Use the occurrence's argument structure (Topic 2) only to WEIGHT which anchors are the relational seeds (co-arguments > distant neighbours) -- structured seeding, not averaging.

**Is the break-through (a) a better mechanism, (b) a richer offline foundation, or (c) both? -- (c) BOTH, and they are one move.** The mechanism change (relational selection + gloss-grounded senses) is what ACTIVATES a relational foundation that is already on disk but currently used only as a flat lookup: WordNet is treated as a candidate list + a relatedness scorer, never as the taxonomic GRAPH that carries the selection signal; the anchor pool exists but is default-off. The single highest-value build is the mechanism that turns the already-present offline foundation into the selector. The DEEPER limiter -- the 4-exposure low-coherence REGIME -- argues that the residual beyond this needs a still-richer offline foundation (attach a definitional gloss / multimodal grounding to each hard word), but that is the SECOND build; the relational-gloss selector is the first and it needs nothing new bought.

**Why this over the three prior directions, decisively:**
- **over the static grounded cascade (~0.45):** it changes the selection signal from FLAT COSINE over a per-word blend to RELATIONAL coherence over the taxonomic graph with PER-SENSE grounded candidates -- the two specific weaknesses that cap ~0.45.
- **over context-gating (failed):** it never averages context feature vectors; context only picks seed nodes, the graph disambiguates. The dilution failure does not apply.
- **over occurrence-clustering sense-induction (unstable 0.4-4%):** per-sense structure comes from OFFLINE GLOSSES, not from clustering 4 noisy occurrences. The unstable step is removed.
- **over a richer situation-model encoder (refuted head-to-head):** the parser did not help selection on this population; structure is used only to weight seeds, second-order.

**Mandatory controls before believing any lift (standing discipline; this design has a real circularity risk -- flag it loudly):**
- The gold scorer is WordNet-relatedness and the selector walks the WordNet graph -- **grade-by-what-you-ground-by risk.** Guard: (1) seeds are the GROUNDED ANCHORS OBSERVED IN READING, never the gold synset and never WordNet graph-centrality; (2) **info-free seed shuffle** (seed from a random other occurrence's anchors) MUST drop to the MFS/chance floor; (3) beat the **Most-Frequent-Sense baseline** explicitly (a graph walk that only recovers MFS is just frequency, not relational selection); (4) hold out the exact target synset from the walk so the graph cannot trivially point at the gold; (5) report CI half-width + null p95 beside the margin; (6) reachability check -- the same word in two occurrences with different anchor sets must produce a materially different selection, or the relational seeding never reached the scorer.
- Measure specifically on the HARD polysemous / low-coherence slice.

**Realistic ceiling (deflated, honest):** from ~0.45, aim for **~0.55-0.65 near-term** (knowledge-based relational WSD sits above flat methods but below supervised; deflate hard for the low-coherence slice), with **~0.85 the asymptote** for this scoring regime -- the last 0.85->1.0 is the shortlist-recall problem (a different lever), not selection. If the relational selector does NOT beat the static cascade + MFS under these controls, that is itself a strong located result: the taxonomic RELATIONAL structure is not recoverable for these words from WordNet at this granularity, and the residual is a foundation-coverage problem (build richer per-word definitional/multimodal grounding offline), not a selection-algorithm problem.

---

## TLDR (plain English)

The machine keeps trying to work out a hard word's meaning by looking at the handful of sentences it appears in and averaging the "feel" of the neighbouring words. That keeps failing, and brain science says why: the clue that tells you two words MEAN THE SAME KIND OF THING (whisky and brandy) is a different kind of knowledge, stored in a different part of the brain, than the clue that two words just TURN UP TOGETHER (whisky and weddings) -- and plain reading only gives you the second kind. The machine's best trick so far reaches a little into the first kind but does it crudely (comparing lists of features), which is why it stalls at about 45% right. The brain does something structurally different: it works out a new word by slotting it into the WEB of words it ALREADY knows well -- "this new thing is a kind of X, related to Y, unlike Z" -- rather than building it up from scratch out of thin context. We already own that web (a dictionary-style network of known words and their definitions), but we only use it as a lookup list, never as a web. The break-through is to USE it as a web: describe each candidate meaning from its DICTIONARY DEFINITION (clean and free, done offline), and pick the meaning that best CONNECTS to the known words actually present in the sentence -- following the links in the network, not averaging features. And the honest big-picture point: four skimpy sentences is simply not how a child learns a hard word; children get many good, multi-sense exposures plus a rich web of known meanings to hang the new word on. So the real fix is to bring that rich web in from the shelf, not to squeeze harder on four thin sentences.

## QUESTIONS

None blocking. One judgement call for the solver: whether to implement the relational selection as a full personalized-PageRank walk over WordNet (most faithful, heavier) or as a lighter relational-coherence score (gloss-grounded candidate vs seed-anchor graph-distance). Recommendation: start with the LIGHT version (gloss-grounded per-sense prototype + graph-distance-to-anchors), because it isolates the two independent levers (per-sense gloss grounding; relational-vs-cosine selection) so each can be ablated; escalate to full PPR only if the light version clears MFS but plateaus below ~0.6.

## NEXT STEPS (for the solver)

1. **Gloss-grounded per-sense prototypes (offline, free):** for each shortlist synset, ground it from its WordNet gloss + synonyms + hypernym/co-hyponyms via predicted-Binder-65; ablate this ALONE vs the static per-word blend (does per-SENSE grounding beat per-WORD grounding?). This isolates lever 1 and removes the unstable occurrence-clustering step.
2. **Relational selection seeded by grounded anchors:** collect the known grounded anchors in the occurrence (wire the BUILT default-off anchor pool); score each candidate by relational coherence / graph-distance to those seeds over the WordNet graph; argmax. This isolates lever 2 (relational vs cosine).
3. **Run the control battery FIRST:** MFS baseline (must beat it); info-free seed-shuffle (must drop to MFS/chance); hold out the target synset from the graph; reachability check (two occurrences -> different selection); CI + null p95; measure on the hard polysemous slice.
4. **Use situation structure only to weight seeds** (co-arguments > distant neighbours); do NOT rebuild a richer bag-of-words situation encoder (refuted head-to-head).
5. **If it clears MFS but plateaus below ~0.6:** the residual is foundation-coverage -- build richer per-word definitional/multimodal grounding OFFLINE (the FOUNDATION pivot; a definition is worth many contexts), which is the second build, not a re-run of selection.
6. **Quote the ceiling honestly:** ~0.55-0.65 near-term (deflated), ~0.85 asymptote for this scoring regime; the 0.85->1.0 gap is a shortlist-recall problem, not a selection problem.
7. **Honest (a)/(b)/(c) verdict for the writeup:** the break-through is BOTH a better mechanism (relational selection + gloss-grounded senses) AND activation of a richer offline foundation (WordNet taxonomic graph + glosses + anchor pool), and they are the SAME move -- turning an on-disk flat lookup into a structured relational selector.

---

## Sources

- Mirman, Landrigan & Britt (2017), *Psychological Bulletin* -- "Taxonomic and thematic semantic systems." https://pubmed.ncbi.nlm.nih.gov/28333494/
- Schwartz, Kimberg, Walker et al. (2011), *PNAS* -- "Neuroanatomical dissociation for taxonomic and thematic knowledge in the human brain." https://www.pnas.org/doi/10.1073/pnas.1014935108
- Navigli & Velardi (2005), *IEEE TPAMI* -- "Structural Semantic Interconnections: a knowledge-based approach to WSD." https://ieeexplore.ieee.org/document/1432741/
- Agirre, Lopez de Lacalle & Soroa (2014), *Computational Linguistics* -- "Random Walks for Knowledge-Based Word Sense Disambiguation." https://aclanthology.org/J14-1003.pdf
- Tse, Langston, Kakeyama et al. (2007), *Science* -- "Schemas and Memory Consolidation." https://www.science.org/doi/10.1126/science.1135935
- Sharon, Moscovitch & Gilboa (2011), *PNAS* -- "Rapid neocortical acquisition of long-term arbitrary associations independent of the hippocampus" (fast mapping). https://www.pnas.org/doi/10.1073/pnas.1005238108
- Coutanche & Thompson-Schill (2015) -- rapid consolidation via fast mapping. https://www.sciencedirect.com/science/article/abs/pii/S1364661315001266
- Swingley (2010) -- "Fast Mapping and Slow Mapping in Children's Word Learning." https://www.sas.upenn.edu/~swingley/papers/swingley_LLD10_fastmap.pdf
- Ramscar (2003), *Cognitive Science* -- "Semantic grounding in models of analogy: an environmental approach" (relational grounding). https://dx.doi.org/10.1016/S0364-0213(02)00113-1
- Zwaan, Langston & Graesser (1995) / Zwaan & Radvansky (1998) -- the event-indexing model / situation models. https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.1995.tb00513.x
- Syntactic bootstrapping (Gleitman 1990; overview). https://en.wikipedia.org/wiki/Syntactic_bootstrapping
- Weizman & Snow (2001), *Developmental Psychology* -- "Lexical Input as Related to Children's Vocabulary Acquisition" (quality of context). https://childes.talkbank.org/access/Eng-NA/0docs/Weizman2001.pdf
- Borman & Lupyan (Evolang XV) -- "How many words is a picture (or definition) worth?" https://par.nsf.gov/biblio/10547761
- Banerjee & Pedersen (2003) extended gloss overlap; Lesk (1986) -- gloss-based WSD (relational match).
