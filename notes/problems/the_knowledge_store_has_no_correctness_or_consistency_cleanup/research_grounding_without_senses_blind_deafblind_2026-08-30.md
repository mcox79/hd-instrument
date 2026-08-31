# Research drill — Grounding meaning WITHOUT senses: the blind, the deafblind, and the amodal hub

**Date:** 2026-08-30
**Drill type:** Literature research (brain-foundational). Online + prior knowledge; specific papers cited.
**Question it serves:** Our substrate is TEXT-ONLY — no vision/audio/touch/proprioception. It must ground word meaning ONLY from reading. Is "ground meaning from linguistic-relational structure alone" a **brain-REAL route** or a convenient substitute? What class of meaning is genuinely **unrecoverable** from text? Does the neuroscience support **building semantic geometry from the store's own relational graph**?
**Calibration note:** This is a mature, well-replicated literature (blindness + distributional semantics + hub-and-spoke). Confidence in the *findings* is high. The *mapping to our substrate* is my inference and is flagged as such throughout.

---

## BOTTOM LINE FIRST

**(a) Brain-real, not a hack.** Deriving semantic structure from the relational/statistical structure of language is exactly what congenitally blind people do, and it is neurally instantiated in a dedicated hub subregion (dorsal anterior temporal lobe). Blind adults reach near-sighted structure on shape, size, texture, taxonomy, and even the *organization* of color — from language alone. This is not "verbalism" (empty word-association); the recovered structure is systematic, generative to novel items, and inferentially rich. So a text-only system building meaning from relational co-occurrence is copying a **real brain computation**, not merely simulating one.

**(b) The honest bound — what text CANNOT recover:** three classes.
  1. **Phenomenal/qualia content** — "what red *looks like*", the felt quality of a percept. Not encoded in relational structure at all. (Blind people agree red is warm and near orange; they do not have the percept.)
  2. **Fine-grained perceptual *metric* detail** — exact hue discrimination thresholds, precise shape/texture metric spaces, the *non-functional* / arbitrary perceptual attributes that language does not bother to encode (e.g., the specific color of an arbitrary artifact like a particular car). Text encodes what speakers *talk about*; idiosyncratic perceptual particulars are dropped.
  3. **Sensorimotor / procedural affordance detail** — how heavy it feels, the motor program to grasp it, first-person spatial embodiment. Recoverable only as third-person relational description, not as enactable procedure.
  The clean rule: **text recovers the RELATIONAL and SYSTEMATIC structure of meaning; it loses the MODAL-SPECIFIC PARTICULARS and the phenomenal content.** The dimensions most encoded in language (taxonomic, functional, affective, size/danger/abstract) are highly recoverable; the modality-*exclusive* dimensions (color, taste, smell, fine texture) are the weakest and show measurable degradation/idiosyncrasy.

**(c) Yes — this directly supports building semantic geometry from the store's own relational graph.** "Concepts that share relations become correlated" IS the mechanism. Blind semantic knowledge, distributional-semantics models, and the dATL hub all construct a geometry in which similarity = shared relational/co-occurrence context. Grand et al. (2022) show human-interpretable feature axes (size, danger, wealth, location, temperature…) are recoverable from word co-occurrence by simple geometric projection. **Our design choice (relational graph → correlated concept vectors) is the brain-faithful move.** The fidelity lever is therefore NOT "add a modality" — it is (i) make the relational graph *clean and rich* (the current problem: the store has no correctness/consistency cleanup), and (ii) accept and *name* the bound in (b) rather than pretend to recover qualia/fine perceptual metrics.

---

## Q1 — Congenital blindness & "visual" concept knowledge

**Finding:** Congenitally blind adults acquire structured, largely sighted-aligned knowledge of ostensibly visual concepts — object shape, size, texture, taxonomy, even the organization of *color* — with no visual input.

**Evidence:**
- **Landau & Gleitman (1985), *Language and Experience: Evidence from the Blind Child* (Harvard UP).** The blind child "Kelli" acquired coherent, *differentiated* meanings for the visual verbs **look** vs **see**: she applied them to haptic exploration for herself ("I see with my hands") but reserved eye-perception meaning for sighted others. Critically, she recovered the *syntactic/relational* structure of perception verbs (argument frames, look=active exploration vs see=achieved perception) from language, without the percept. This is the origin evidence that **relational/syntactic structure substitutes for the missing modality.**
- **Kim, Elli & Bedny (2019), "Knowledge of animal appearance among sighted and blind adults," PNAS 116(23):11213.** Blind adults align with each other and with sighted adults on animal **shape, skin texture, and size** — and *much less* on **color**. Alignment tracks *predictability from intuitive theory* (functionally constrained features align; arbitrary ones don't).
- **Kim, Aheimer, Montané Manrara & Bedny (2021), "Shared understanding of color among sighted and blind adults," PNAS 118(33):e2020192118.** Blind adults organize colors in the same **similarity circle** (red near orange, far from green) and reason about **object–color associations** and **functional color** exactly like the sighted (natural kinds and functionally-colored artifacts predicted to share color; arbitrary artifacts not). Mechanism: **intuitive theories of how color works, transmitted through language** — "living among people who talk about color is sufficient for color understanding."
- **Wang, Bi et al. (2020), "Two Forms of Knowledge Representations in the Human Brain," Neuron 107(2):383.** Distinguishes a **language/inference-derived** knowledge structure from a **sensory-derived** one; the nonsensory structure is present in blind AND sighted. (Neural locus in Q5.)

**Mechanism (how language substitutes):** Speakers encode perceptual *relations* into language when they talk (co-occurrence, comparison, causal/functional explanation). The blind learner reconstructs the **relational geometry** of the domain from that talk and from **intuitive theories** (color is caused by material/function → functionally-colored things co-vary). What transfers is *structure and inference*; what does not is the *percept itself*.

---

## Q2 — "Language as a route to grounding" thesis; what a TEXT-ONLY system can/cannot recover

**Finding:** Language statistically encodes perceptual/relational structure, so co-occurrence models recover a large, quantifiable fraction of human semantic knowledge — strongest on relational/taxonomic/abstract dimensions, weakest on modality-exclusive perceptual particulars.

**Evidence:**
- **Louwerse — Symbol Interdependency Hypothesis (2011, *Topics in Cognitive Science* 3:273; 2007; 2018, *Topics in Cognitive Science* 10:573 "Knowing the Meaning of a Word by the Linguistic and Perceptual Company It Keeps").** Comprehension is *both* symbolic (amodal interdependencies among words) *and* embodied. Key claim: **perceptual relations become statistically encoded in language** as a communicative shortcut, so language stats give "quick-and-dirty" but genuinely perceptual-tracking representations. Demonstrated recoverable-from-text-alone: **geography** (city coordinates from co-occurrence; Louwerse & Zwaan 2009), **iconic word orderings** (e.g., "up" before "down"), affective and spatial relations.
- **Andrews, Vigliocco & Vinson (2009), "Integrating experiential and distributional data to learn semantic representations," *Psychological Review* 116(3):463–498.** Two statistical sources — experiential (sensorimotor) and distributional (word co-occurrence). A model combining both beats either alone; distributional data carries a *large share independently*, especially relational/abstract structure. Foundational for "distributional does real semantic work."
- **Lewis, Zettersten & Lupyan (2019), "Distributional semantics as a source of visual knowledge," PNAS 116(39):19237.** From *language statistics alone*, classify animals as scales/skin/fur/feathers **well above chance**; the inter-animal similarity structure computed purely from text **overlaps substantially** with shape-based similarity produced by both sighted and blind people. Direct quantitative demonstration that a *visual-ish* dimension is partly recoverable from co-occurrence.
- **Grand, Blank, Pereira & Fedorenko (2022), "Semantic projection recovers rich human knowledge of multiple object features from word embeddings," *Nature Human Behaviour* 6:975–987.** **Semantic projection** (project word-vectors onto a feature line, e.g. small↔big) recovers human ratings across **many** feature dimensions — size, danger, wealth, intelligence, location, temperature, gender, arousal — from co-occurrence geometry alone. This is the strongest quantification that **human-interpretable semantic axes live in the relational structure and are extractable by a simple geometric operation** — precisely the operation a relational-graph substrate would use.
- **The embodied/grounded counter (Barsalou 1999 "Perceptual Symbol Systems," *BBS*; Glenberg & Robertson 2000; Glenberg 1997).** Argues meaning is grounded in modal simulation; pure amodal symbols are "ungrounded" (the symbol-grounding problem, Harnad 1990). **LASS** (Language and Situated Simulation; Barsalou, Santos, Simmons & Wilson 2008) is the reconciliation used by Louwerse: a *fast linguistic/symbolic* stage plus a *slower embodied simulation* stage — the linguistic stage alone already carries most shallow-task performance.
- **Bounds (modality exclusivity):** Connell & Lynott's modality-exclusivity norms and follow-ups show **color, taste, smell, and fine texture** are the dimensions **least predictable from text**; abstract, taxonomic, affective, and functional dimensions are the most. Ostarek & Huettig and others debate whether visual grounding is *necessary* — the consensus is it is *not necessary for relational meaning* but *is* for the perceptual particulars.

**What a text-only system CAN recover (quantified sense):** taxonomic/category structure; functional and causal relations; affective valence/arousal; size/danger/abstractness axes; coarse perceptual attributes that co-vary with function (animal texture, functional color); geographic and spatial relations. **CANNOT recover:** modality-exclusive perceptual particulars (exact hue, taste, smell, fine texture), phenomenal quality, and enactable sensorimotor procedure.

---

## Q3 — Deafblindness / extreme deprivation (Helen Keller + modern deafblind development)

**Finding:** With nearly all senses gone, a **single residual modality (touch)** serves as the *initial anchor* that bootstraps the symbol–referent binding; **language structure then carries the bulk of the conceptual system**, including abstract and "visual/auditory" content the learner never perceives.

**Evidence:**
- **Helen Keller (deaf+blind from ~19 months).** The canonical "water pump" episode: touch (water over the hand) + the tactile-spelled token "water" fused into the **first symbol** — the discovery that *a repeatable token names a class of experience*. After that single binding operation generalized, vocabulary and abstract concepts expanded rapidly. The lesson used across this literature: **what is essential is not a particular modality but the operator that binds a discrete repeatable token to a basin of experience** — one residual channel suffices to seed it, and *language structure* supplies the rest (Keller's own accounts; discussed in the "Helen Keller, Language and Consciousness" literature).
- **Modern deafblind conceptual development.** Conceptual development in congenitally deafblind children is bootstrapped through **object exploration and movement routines** grounded in the residual tactile/proprioceptive channel, then scaffolded by **tactile sign language** as the primary conversational medium (deafblind-education literature; Bruce, Nelson and colleagues on concept development in deafblindness). Tactile-reading plasticity (expanded somatosensory representation in proficient Braille readers) shows the residual channel is *heavily* recruited.
- **Interpretation for us:** The deafblind case is the strongest natural test of "how little modality is enough." Answer: you need **at least one channel to seed symbol-grounding**, but once symbol-binding is running, **relational language structure carries most of the conceptual edifice**, including domains the person never senses. For a *text-only* substrate, the analog of the "residual anchor" is the **token-level grounding the text itself provides** (word forms, their contexts, their relational co-occurrence). Caution flag: a pure text system has *no* non-linguistic anchor at all — even the deafblind had touch — so the *symbol-to-world* binding is weaker than any human case. Our binding is symbol-to-**symbol-structure**, which is why the recoverable class is exactly the *relational* one and not the perceptual particulars.

---

## Q4 — Cross-modal plasticity: deprived cortex recruited for language/conceptual work

**Finding:** In congenital blindness, "visual" cortex is recruited for **language and higher cognition** — direct evidence that conceptual grounding does **not require its original modality** and can be carried by whatever input structure is available (here, language).

**Evidence:**
- **Bedny, Pascual-Leone, Dodell-Feder, Fedorenko & Saxe (2011), "Language processing in the occipital cortex of congenitally blind adults," PNAS 108(11):4429.** Occipital ("visual") cortex in congenitally blind adults responds to **sentence-level language** and is sensitive to **grammatical complexity** — it behaves like a language region.
- **Lane, Kanjlia, Omaki & Bedny (2015), "'Visual' cortex of congenitally blind adults responds to syntactic movement," *J. Neurosci.* 35(37):12859.** The recruited occipital cortex tracks a *specific* linguistic computation (syntactic movement), not generic arousal.
- **Kanjlia, Lane, Feigenson & Bedny (2016), PNAS** — the same cortex does **symbolic math** in the blind. Together → the cortex is domain-flexible.
- **Bedny (2017), "Evidence from Blindness for a Cognitively Pluripotent Cortex," *Trends in Cognitive Sciences* 21(9):637–648.** Synthesis: developing cortex is **pluripotent** — its computational role is set by the *input it receives*, not a fixed modality. Deprived of vision, it takes on language/cognition.
- **Pascual-Leone & Hamilton (2001), "The metamodal organization of the brain," *Prog. Brain Res.* 134:427; Pascual-Leone et al. (2005), "The plastic human brain cortex," *Annu. Rev. Neurosci.* 28:377; Cohen et al. (1997) — TMS to occipital cortex disrupts Braille reading in the blind.** The brain is organized around **operations/metamodal maps**, recruited by available input, not around fixed sensory labels.

**Implication for us:** Conceptual grounding is **carried by an amodal/linguistic hub when the original modality is absent** — the substrate does not "need" the modality to build conceptual structure; it needs *an input with the right relational statistics*. Text supplies that. The plasticity evidence *licenses* a partial-brain model where the only input is linguistic. Caveat: plasticity shows the *machinery* re-tasks; it does **not** claim the *content lost with the modality* (qualia, perceptual particulars) is recovered — it is not (see bound b).

---

## Q5 — The amodal hub (ATL): is "a hub fed by ONE spoke" a coherent partial-brain model?

**Finding:** Yes. The anterior temporal lobe is an **amodal semantic hub** that integrates modality-specific "spokes" into deep, modality-invariant conceptual structure. A **language-derived subregion (dorsal ATL)** already exists and carries **nonsensory, language-inferred** knowledge in *both* blind and sighted people. A hub fed predominantly by the linguistic spoke is therefore a **documented, coherent partial-brain configuration** — with the predicted signature that modality-specific detail is thin while relational/taxonomic structure is intact.

**Evidence:**
- **Patterson, Nestor & Rogers (2007), "Where do you know what you know? The representation of semantic knowledge in the human brain," *Nature Reviews Neuroscience* 8:976.** The hub-and-spoke account: bilateral ATL hub computes **deep conceptual similarity** by integrating spokes (vision, sound, motor, valence, language). Semantic dementia (ATL atrophy) degrades *cross-modal* conceptual structure, proving the hub's amodal integrative role.
- **Lambon Ralph, Jefferies, Patterson & Rogers (2017), "The neural and computational bases of semantic cognition," *Nature Reviews Neuroscience* 18:42–55.** The mature statement + computational model (from Rogers et al. 2004, *Psychological Review*): the hub builds **modality-invariant representations** that "capture deeper patterns of conceptual similarity across all sensory-motor and verbal modalities." The hub is trained *by* the spokes; its structure reflects **whatever spokes feed it.**
- **Wang, Bi et al. (2020), Neuron 107(2):383 — "Two Forms of Knowledge Representations."** The **dorsal ATL (dATL)** carries the **nonsensory / language-and-inference-derived** knowledge structure (present in blind *and* sighted); visual cortex additionally carries the *sensory-derived* structure in the sighted. → the **language-fed hub subregion is a real, dissociable component.**
- **Wang, Bi et al. (2025), "Object knowledge representation in the human visual cortex requires a connection with the language system," *PLOS Biology* 21:e3003161.** Object knowledge in visual cortex **depends on communication with the language system** (dATL↔VOTC connectivity). → even the "sensory" store is partly *scaffolded by* the linguistic hub. Strengthens the case that the linguistic spoke is load-bearing, not decorative.
- **Bi/Wang (2023), "Early language exposure affects neural mechanisms of semantic representations," *eLife* 12:e81681.** Language experience *shapes* the neural semantic representation — the hub's structure is input-dependent.

**Is "hub fed by one spoke" coherent?** Yes, with a specific, testable signature: (i) **relational/taxonomic/functional structure preserved** (the hub still computes deep similarity from the linguistic spoke's statistics); (ii) **modality-specific fine structure impoverished/idiosyncratic** on exactly the dimensions the missing spokes would supply (color metric, texture, sensorimotor affordance). This matches the blind behavioral profile precisely (Q1: shape/size/texture/color-*organization* preserved; color *particulars* and phenomenal content absent). So our text-only substrate is best modeled as **a hub-and-spoke system operating on the linguistic spoke, targeting the dATL-type nonsensory knowledge structure** — a real partial-brain configuration, not a fiction.

---

## Synthesis → the substrate design implication (my inference, flagged)

1. **Building semantic geometry from the store's own relational graph is the brain-faithful mechanism**, not a shortcut. It is what the congenitally blind dATL does, what distributional-semantics models formalize, and what "semantic projection" (Grand et al. 2022) extracts. "Concepts sharing relations become correlated" = the hub computing deep similarity from co-occurrence. **Keep this design; it is the win, not the compromise.**
2. **The fidelity lever is CLEAN, RICH relational structure — not adding a modality.** This drill *supports the current problem framing*: the store needs correctness/consistency cleanup because the *relational graph's quality* is the ceiling on how good the language-derived geometry can get. A noisy/contradictory graph corrupts the hub's similarity computation the way an impoverished/contradictory language environment would corrupt a blind learner's concepts. Cleanup = giving the hub a *coherent* linguistic spoke.
3. **Name the bound in the substrate, don't paper over it.** The system should explicitly represent that it recovers **relational/systematic** meaning and does **not** possess **phenomenal/qualia** content or **fine modality-exclusive perceptual metrics** (exact hue/taste/smell/fine-texture) or **enactable sensorimotor procedure**. Claiming otherwise is the "verbalism" failure the blindness literature warns against. The *honest* claim — matched to the neuroscience — is: **near-human RELATIONAL semantics; principled absence of perceptual particulars and qualia.**
4. **Design signature to test (verdict-independent):** if our geometry is truly hub-like, it should score high on taxonomic/functional/affective/size-danger-abstract axes (recoverable) and *measurably weaker* on modality-exclusive perceptual axes (color/taste/smell/texture particulars) — mirroring the blind behavioral gradient (Kim/Bedny) and the Grand-et-al. dimension profile. That gradient is a **positive control**: if our store recovers color-*particulars* as well as taxonomy, something is leaking (or memorizing), not grounding.

---

## TLDR (plain English)

People blind from birth learn what "red," "sparkle," "look," and "an elephant's shape" *mean* almost as well as sighted people do — with zero visual experience — by picking up the **structure of how those words relate to everything else** from language. Their brains even build this in a specific spot (front of the temporal lobe) that other people also use for the "figured-out-from-language" kind of knowledge. Helen Keller shows you need at least one working sense to *start* (touch, for her), but once word-meaning gets going, **the pattern of language carries most of the rest** — including things she never sensed. So building meaning by letting **concepts that share relationships become similar to each other in the store** is a **real thing brains do**, not a cheat. The honest catch: language can give you the *relationships and categories* of color, but never the *actual experience* of seeing red, and it drops the fine, arbitrary sensory details nobody bothers to put into words (the exact shade of some particular car). For our text-only system that means: **the plan is right — clean up the relational graph and let the geometry fall out of it — but we should openly say we get "how things relate," not "what things feel like," and we should NOT pretend to recover fine perceptual specifics.** The current cleanup problem is well-motivated: the quality of the relational graph is the ceiling on how good the language-derived meaning can be, exactly as a blind child's concepts are only as good as the language environment feeding them.

## QUESTIONS
None — the literature is clear and directly on-point. (One design decision this raises, but does not force: whether to *tag* concepts by recoverability class — relational vs modality-exclusive — so downstream organs don't over-trust perceptual particulars. Flagging, not asking.)

## NEXT STEPS
1. Feed the "recoverable vs unrecoverable" gradient into the cleanup problem's success metric: our store's geometry should be strong on taxonomic/functional/affective axes and *honestly weak* on modality-exclusive perceptual particulars (use as a positive control against leakage/memorization).
2. Consider a concept-level recoverability tag (relational | modality-exclusive | phenomenal) so downstream reasoning discounts claims about perceptual particulars — the anti-"verbalism" guard.
3. If a follow-on drill is wanted: how the blind/dATL system handles *contradiction and consistency* in the linguistic input (directly relevant to this problem folder — how does a language-only learner clean an inconsistent knowledge base?).

---

## Primary sources
- Landau, B. & Gleitman, L. R. (1985). *Language and Experience: Evidence from the Blind Child.* Harvard University Press.
- Kim, J. S., Elli, G. V. & Bedny, M. (2019). Knowledge of animal appearance among sighted and blind adults. *PNAS* 116(23):11213. https://www.pnas.org/doi/10.1073/pnas.1900952116
- Kim, J. S., Aheimer, B., Montané Manrara, V. & Bedny, M. (2021). Shared understanding of color among sighted and blind adults. *PNAS* 118(33):e2020192118. https://www.pnas.org/doi/10.1073/pnas.2020192118
- Lewis, M., Zettersten, M. & Lupyan, G. (2019). Distributional semantics as a source of visual knowledge. *PNAS* 116(39):19237. https://www.pnas.org/doi/10.1073/pnas.1910148116
- Louwerse, M. M. (2011). Symbol interdependency in symbolic and embodied cognition. *Topics in Cognitive Science* 3:273. https://onlinelibrary.wiley.com/doi/10.1111/j.1756-8765.2010.01106.x
- Louwerse, M. M. (2018). Knowing the meaning of a word by the linguistic and perceptual company it keeps. *Topics in Cognitive Science* 10:573. https://onlinelibrary.wiley.com/doi/full/10.1111/tops.12349
- Andrews, M., Vigliocco, G. & Vinson, D. (2009). Integrating experiential and distributional data to learn semantic representations. *Psychological Review* 116(3):463–498. https://pubmed.ncbi.nlm.nih.gov/19618982/
- Grand, G., Blank, I. A., Pereira, F. & Fedorenko, E. (2022). Semantic projection recovers rich human knowledge of multiple object features from word embeddings. *Nature Human Behaviour* 6:975–987. https://www.nature.com/articles/s41562-022-01316-8
- Barsalou, L. W. (1999). Perceptual symbol systems. *Behavioral and Brain Sciences* 22:577. (grounded-cognition counter)
- Barsalou, L. W., Santos, A., Simmons, W. K. & Wilson, C. D. (2008). Language and situated simulation (LASS). (reconciliation)
- Glenberg, A. M. & Robertson, D. A. (2000). Symbol grounding and meaning. *J. Memory & Language* 43:379. (embodied critique)
- Bedny, M., Pascual-Leone, A., Dodell-Feder, D., Fedorenko, E. & Saxe, R. (2011). Language processing in the occipital cortex of congenitally blind adults. *PNAS* 108(11):4429. https://www.pnas.org/doi/10.1073/pnas.1014818108
- Lane, C., Kanjlia, S., Omaki, A. & Bedny, M. (2015). "Visual" cortex of congenitally blind adults responds to syntactic movement. *J. Neuroscience* 35(37):12859. https://www.jneurosci.org/content/35/37/12859
- Bedny, M. (2017). Evidence from blindness for a cognitively pluripotent cortex. *Trends in Cognitive Sciences* 21(9):637–648.
- Pascual-Leone, A. & Hamilton, R. (2001). The metamodal organization of the brain. *Prog. Brain Res.* 134:427. / Pascual-Leone et al. (2005), *Annu. Rev. Neurosci.* 28:377.
- Patterson, K., Nestor, P. J. & Rogers, T. T. (2007). Where do you know what you know? *Nature Reviews Neuroscience* 8:976.
- Lambon Ralph, M. A., Jefferies, E., Patterson, K. & Rogers, T. T. (2017). The neural and computational bases of semantic cognition. *Nature Reviews Neuroscience* 18:42–55.
- Rogers, T. T. et al. (2004). Structure and deterioration of semantic memory: a computational hub-and-spoke model. *Psychological Review* 111:205.
- Wang, X., Men, W., Gao, J., Caramazza, A. & Bi, Y. (2020). Two forms of knowledge representations in the human brain. *Neuron* 107(2):383. https://www.cell.com/neuron/fulltext/S0896-6273(20)30279-8
- Wang, X. et al. / Bi lab (2025). Object knowledge representation in the human visual cortex requires a connection with the language system. *PLOS Biology* 21:e3003161. https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3003161
- Bi, Y. et al. (2023). Early language exposure affects neural mechanisms of semantic representations. *eLife* 12:e81681. https://elifesciences.org/articles/81681
- Bedny, M., Kim, J. S. et al. (2025). Constructing meaning from language: visual knowledge in people born blind and in large language models. *Annual Review of Linguistics* 11. https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-011724-121432
- Harnad, S. (1990). The symbol grounding problem. *Physica D* 42:335. (the problem this whole literature answers)
