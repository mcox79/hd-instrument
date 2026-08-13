<!-- RESCUED VERBATIM SUB-AGENT OUTPUT. DO NOT EDIT THE BODY. -->
# Literature scan: cortical learning rule and code sparsity / format

- **Filed:** 2026-08-13
- **Question answered:** What learning rule builds the cortical semantic code, and what is that code's FORMAT (sparsity, distributedness, dimensionality)?
- **Fed into:** [notes/brain_drill_encoder_lexical_semantics_2026-08-13.md](brain_drill_encoder_lexical_semantics_2026-08-13.md) (the Opus synthesis drill on the ENCODER / lexical-semantic representation)
- **Provenance:** sub-agent `a88efcae93a84b5cd`, transcript
  `~/.claude/projects/D--AI/139818eb-7f83-457e-928d-a8db02a0214d/subagents/agent-a88efcae93a84b5cd.jsonl`
- **Rescued:** 2026-08-13, by extracting the final assistant message from that transcript.

> **This document is VERBATIM sub-agent output, preserved for citation. It was NOT re-derived,
> re-summarised, or re-checked when filed.** The per-claim evidence tags
> (ESTABLISHED / CONTESTED / SINGLE-STUDY / FAILED-REPLICATION) are the point of preserving it and
> are reproduced exactly as the scanning agent wrote them. The synthesis drill above is the
> INTERPRETATION; this is the underlying evidence with its statistics and citations. Where the two
> disagree, this file is the record of what the scan actually said.
>
> Standing caveat (lit-scan calibration): a scanning agent's tags are its own judgement, not an
> independent replication audit. Treat a tag as the scan's claim about the literature, and VET
> before any tagged claim becomes load-bearing.
>
> Non-ASCII characters and em dashes below are part of the verbatim text and are intentionally
> left unmodified.

---

# Cortical Semantic Code: Learning Rule and Format — Literature Report

## A. LEARNING RULE

### A1. The backprop-approximation research program (2018–2022)

**Lillicrap, Santoro, Marris, Akerman & Hinton (2020), "Backpropagation and the brain," Nature Reviews Neuroscience 21(6):335–346** — the field's touchstone theory paper. It does not claim cortex literally implements backprop, but argues feedback connections could induce neural activity differences ("NGRAD" — neural gradient representation) that locally approximate the error signals backprop requires, without needing symmetric weight transport. [ESTABLISHED as the standard framing of the hypothesis; the claim itself is theoretical/unproven]

**Whittington & Bogacz (2019), "Theories of Error Back-Propagation in the Brain," Trends in Cognitive Sciences 23(3):235–250** — reviews multiple concrete circuit models (predictive coding, target propagation, feedback alignment) that reach backprop-level performance using only local pre/postsynaptic Hebbian-type update rules, with feedback connections propagating error information layer-by-layer. [ESTABLISHED review]

**Whittington & Bogacz (2017), "An Approximation of the Error Backpropagation Algorithm in a Predictive Coding Network with Local Hebbian Synaptic Plasticity," Neural Computation 29(5):1229–1262** — mathematically shows a predictive-coding network trained with local Hebbian plasticity converges to backprop's weight updates under specific parameter regimes. [ESTABLISHED equivalence result, condition-dependent]

**Millidge, Tschantz & Buckley (2022), "Predictive Coding Approximates Backprop along Arbitrary Computation Graphs," Neural Computation 34(6):1329–1368** — generalizes the Whittington & Bogacz result to arbitrary architectures, strengthening the mathematical case that predictive coding is a general local approximation to gradient descent. [ESTABLISHED, extends prior proof]

**Sacramento, Costa, Bengio & Senn (2018), "Dendritic Cortical Microcircuits Approximate the Backpropagation Algorithm," NeurIPS 2018** — proposes multicompartment pyramidal-neuron microcircuits (apical vs. basal dendrites) where local dendritic prediction errors (mismatch between top-down feedback and lateral-interneuron predictions) drive continuous, phase-free error-driven plasticity. [SINGLE-STUDY, influential]

**Payeur, Guerguiev, Zenke, Richards & Naud (2021), "Burst-Dependent Synaptic Plasticity Can Coordinate Learning in Hierarchical Circuits," Nature Neuroscience 24:1010–1019 (Author Correction 2021)** — proposes that layer-5 pyramidal neuron high-frequency burst probability, rather than dendritic-compartment activity differences, encodes a top-down error/credit signal; burst-gated plasticity solves hierarchical credit assignment without requiring the two-phase or dual-compartment machinery earlier models needed. [SINGLE-STUDY, mechanistically distinct from Sacramento et al.]

**Net read of A1:** [CONTESTED as biological fact, ESTABLISHED as a live and mathematically serious research program] There is no direct empirical confirmation that cortex implements approximate backprop; the evidence is a convergent set of theoretical/simulation results showing *plausible circuit implementations exist*. All these models target feedforward sensory-processing hierarchies (visual/auditory streams), not lexical-semantic cortex specifically.

### A2. Counter-evidence: Hebbian/local-only learning does not scale

**Illing, Gerstner & Brea (2019), "Biologically Plausible Deep Learning — But How Far Can We Go with Shallow Networks?," Neural Networks 118:90–101** — tested unsupervised local rules (PCA, ICA, sparse coding) for hidden-layer weights plus a local supervised readout. Finding: unsupervised local learning of hidden weights did **not** outperform fixed random or Gabor-filter projections for large hidden layers; performance approached backprop only on MNIST with strongly localized receptive fields, not on harder tasks. [ESTABLISHED negative/limiting result]

**Bartunov, Santoro, Richards, Marris, Hinton & Lillicrap (2018), "Assessing the Scalability of Biologically-Motivated Deep Learning Algorithms and Architectures," NeurIPS 2018** — systematically scaled target-propagation and feedback-alignment variants to MNIST, CIFAR-10, and ImageNet. Finding: these alternatives matched backprop on MNIST but **degraded sharply** relative to real backprop on CIFAR/ImageNet, especially with local (non-fully-connected) receptive fields. [ESTABLISHED negative result — direct counter-evidence that pure local/Hebbian-flavored alternatives are drop-in replacements for error-driven learning at scale]

**Net read of A2:** [ESTABLISHED] Pure Hebbian/unsupervised/competitive learning alone cannot build the kind of deep, task-general hierarchical representations backprop builds — this is the strongest empirical argument *for* some form of error-driven signal being necessary in cortex-scale representation learning, and it is why the field's best current story is a **hybrid**: local Hebbian-style synaptic update rules, computing something that mathematically approximates a gradient, driven by circuit-level error signals (dendritic mismatch or burst-coded), rather than either "pure backprop" or "pure Hebb."

### A3. CRITICAL DISTINCTION: is lexical-semantic acquisition a different story from sensory learning?

Yes — the literature bifurcates cleanly, and this is the answer to your critical question.

**Davis & Gaskell (2009), "A Complementary Systems Account of Word Learning: Neural and Behavioural Evidence," Phil. Trans. R. Soc. B 364(1536):3773–3800** — extends McClelland/O'Reilly Complementary Learning Systems (CLS) theory specifically to spoken word learning. Two stages: (1) **rapid familiarization/acquisition** — hippocampally-mediated, fast, associative/pattern-separated binding of a novel wordform to meaning (essentially one-shot, Hebbian-like); (2) **slow lexical consolidation** — neocortical integration achieved via **offline (sleep-dependent) reactivation/replay**, not online error-driven training at time of exposure. [ESTABLISHED framework, now the standard reference for word learning]

**Sleep/lexicalization evidence:** Takashima, Bakker et al. (multiple studies, e.g. neural-representation studies of newly learned words modulated by overnight consolidation) and the review **"Something old, something new: A review of the literature on sleep-related lexicalization of novel words in adults," Psychonomic Bulletin & Review (2020)** — converge on the finding that cortical, word-like neural responses to a novel word only emerge **after a period of sleep**, not immediately after learning; hippocampal reactivation during slow-wave sleep is argued to "prime" and interleave new lexical items into existing cortical structure. [ESTABLISHED pattern across several studies, mechanism still under active study]

**McClelland, McNaughton & O'Reilly (1995)** and **O'Reilly et al. (2014) Cognitive Science** CLS framework — pre-2015 classic still the standard reference: hippocampus = sparse, pattern-separated, fast, essentially associative (Hebbian-flavored) one-shot encoder; neocortex = dense, overlapping, slow learner that extracts statistical/semantic structure only via many **interleaved** replayed exposures. [PRE-2015 CLASSIC, STILL STANDARD — flagged as instructed]

**Carey & Bartlett (1978)** "fast mapping" chromium study — the foundational one-shot word-referent binding demonstration. [PRE-2015 CLASSIC, STILL STANDARD REFERENCE — no 2015–2026 work has displaced this as the founding citation, though many follow-ups (e.g. Frontiers 2019 "Neurophysiological Correlates of Fast Mapping of Novel Words in the Adult Brain") extend it]

**Synthesis (my read, flagged CONTESTED/interpretive):** The initial act of getting a new word's meaning into the system is **not** gradient-descent-like at all — it looks like rapid hippocampal associative/Hebbian binding (fast mapping). What *might* approximate error-driven, gradient-like optimization is the **slow neocortical consolidation phase**, and even there the mechanism proposed (interleaved replay gradually reshaping distributed cortical weights) is closer to a Hebbian/statistical-learning process operating over replayed samples than to literal backpropagated error at encoding time. So: sensory/perceptual cortical hierarchies are the target of the backprop-approximation dendritic/burst theories (A1); lexical-semantic acquisition is much better described by CLS's two-system, replay-based account, which is neither pure backprop nor pure single-shot Hebb but a third, distinct mechanism (fast associative encoding + slow interleaved statistical consolidation).

---

## B. SPARSITY / CODE FORMAT

### B1. MTL concept-cell sparseness — Quian Quiroga's own numbers

**Quian Quiroga, Reddy, Kreiman, Koch & Fried (2005), "Invariant Visual Representation by Single Neurons in the Human Brain," Nature 435:1102–1107** — the founding "Jennifer Aniston neuron" paper; MTL neurons respond invariantly across drastically different depictions of one person/landmark, and in some cases even to the printed/spoken name. [ESTABLISHED, foundational]

**Waydo, Kraskov, Quian Quiroga, Fried & Koch (2006), "Sparse Representation in the Human Medial Temporal Lobe," J. Neuroscience 26(40):10232–10234** — the source of the actual sparseness estimate. Probabilistic analysis over 1,425 recorded MTL units across 34 sessions: assuming ~10⁹ neurons total in human MTL, they estimate **fewer than 2×10⁶ neurons (< ~0.2%)** are involved in representing a given percept/concept, and — running the calculation the other way, assuming a person recognizes 10,000–30,000 objects — **each neuron fires to roughly 50–150 different objects/concepts**. [ESTABLISHED — this is the precise figure behind the "~0.23%"/"~1M neurons" folk-summary; the actual number as published is <2 million out of ~10⁹, i.e. ~0.2%]

**Quian Quiroga (2012), "Concept Cells: The Building Blocks of Declarative Memory Functions," Nature Reviews Neuroscience 13:587–597** — review explicitly frames the finding as **"sparse but not grandmother-cell"**: coding is highly selective and abstract, invariant, and multimodal, but redundant (on the order of hundreds of thousands to low millions of neurons per concept, not one). [ESTABLISHED synthesis]

**Waydo/Quian Quiroga group, "Two-population model for MTL neurons: The vast majority are almost silent" (arXiv 1411.3917; PubMed 2015)** — refines the picture: sparseness is **not uniform** but strongly bimodal/skewed. In hippocampus, ~7% of cells show ~2.6% sparsity (moderately selective), while the remaining ~93% respond to only ~0.1% of stimuli (almost silent). A single-sparsity model fits the data poorly. [SINGLE-STUDY, refines rather than overturns the Waydo 2006 estimate]

### B2. MTL sparse coding IS different from neocortical semantic/object coding — this is established

Inferotemporal (neocortex) object-selectivity studies report **sparseness index values in the ~0.2–0.3 range** (Rolls/Treves-style lifetime/population sparseness metrics), i.e., substantially **less sparse/more distributed** than MTL concept cells. This matches the CLS prediction structurally: **hippocampus/MTL = sparse, pattern-separated code; neocortex = denser, overlapping, distributed code.** [ESTABLISHED directional finding, though exact IT sparseness numbers vary by study/metric — flagged as approximate]

### B3. Neocortical semantic code: dense-distributed, evidenced by fMRI

**Huth, Nishimoto, Vu & Gallant (2012), "A Continuous Semantic Space Describes the Representation of Thousands of Object and Action Categories across the Human Brain," Neuron 76(6):1210–1224** — voxelwise models over 1,705 categories; the **first ~4 group principal components** define a semantic space shared across subjects, while individual-subject PCs 6–9 explain more variance than stimulus PCs (finer idiosyncratic structure). This is the empirical basis for the "~4–12 dimensions" figure. [ESTABLISHED]

**Huth, de Heer, Griffiths, Theunissen & Gallant (2016), "Natural Speech Reveals the Semantic Maps that Tile Human Cerebral Cortex," Nature 532:453–458** — semantic information during naturalistic story listening is distributed across vast, overlapping cortical territories in continuous gradient maps, consistent across individuals. [ESTABLISHED, landmark]

**Mitchell et al. (2008), Science** — early distributed-code demonstration (predicting fMRI patterns from semantic features). [PRE-2015 CLASSIC, still cited as foundational for the distributed-decoding paradigm]

**Pereira, Lou, Pritchett, Ritter, Gershman, Kanwisher, Botvinick & Fedorenko (2018), "Toward a Universal Decoder of Linguistic Meaning from Brain Activation," Nature Communications 9:963** — decodes distributed semantic vectors from brain activity for sentences spanning concrete and abstract topics, and explicitly reports the decoder can **distinguish even semantically similar sentences** and recover fine-grained similarity structure. [ESTABLISHED, directly relevant to Part C]

**Fernandino, Tong, Conant, Humphries & Binder (2022), "A Distributed Network for Multimodal Experiential Representation of Concepts," J. Neuroscience 42(37):7121–7135** — searchlight RSA, 64 participants, 522 nouns, using Binder's 65-feature experiential model; concept representation is distributed across precuneus, posterior cingulate, angular gyrus, dmPFC, vlPFC, and lateral temporal cortex — multiple heteromodal hubs, not one localized population. [ESTABLISHED]

**Binder, Conant, Humphries, Fernandino, Simons, Aguilar & Desai (2016), "Toward a Brain-Based Componential Semantic Representation," Cognitive Neuropsychology 33(3-4):130–174** — proposes ~65 neurobiologically motivated experiential attributes (sensory, motor, spatial, temporal, affective, social, cognitive) as a componential feature basis, normed on large word sets. [ESTABLISHED framework, widely adopted]

**Fernandino et al. (2016), "Concept Representation Reflects Multimodal Abstraction," Cerebral Cortex** — precursor study using 5 specific sensory-motor attributes (color, shape, visual motion, sound, manipulation) across 900 words; I was **not able to confirm** a distinct "5-dimensional PCA-derived experiential space" claim matching your description — the well-documented Fernandino/Binder dimensionality claim is the **65-attribute** componential model, not an empirically-reduced 5-dimensional space. Flag this as an open discrepancy — I could not locate the specific "5-dimensional experiential space" result as you described it; it may be conflated with the 5-attribute stimulus design of the 2016 study, which is not the same as a PCA-derived low-dimensional space. [UNRESOLVED — do not treat as established]

**Stringer, Pachitariu, Steinmetz, Carandini & Harris (2019), "High-Dimensional Geometry of Population Responses in Visual Cortex," Nature 571:361–365** — mouse V1 population code is genuinely **high-dimensional** with a power-law eigenspectrum (nth PC variance ∝ 1/n), just below the threshold that would make the code non-differentiable/non-smooth. [ESTABLISHED — but note this is **early visual cortex**, not semantic cortex; the "smooth high-D code" story and the "~4-12-dimension semantic space" story describe different cortical systems and should not be conflated]

**Net read of B:** [ESTABLISHED] Population-level fMRI evidence strongly favors a **dense, distributed, low-effective-dimensionality (~4-12 shared dims, with much larger nominal attribute counts like 65) neocortical semantic code**, structurally distinct from the **sparse, high-redundancy MTL concept-cell code** (~0.2% / hundreds-of-thousands-to-low-millions of neurons per concept). These are two different coding regimes serving two different systems (episodic/declarative memory indexing vs. distributed semantic/conceptual knowledge), consistent with CLS.

---

## C. Near-synonyms: separable or collapsed in the semantic hub?

Evidence here is thinner and **CONTESTED**. The ATL (anterior temporal lobe) hub-and-spoke account (Patterson, Nestor & Rogers 2007, Nat Rev Neurosci — [PRE-2015 CLASSIC, still standard]) predicts a graded, transmodal convergence zone where related concepts increasingly overlap; ATL synonym-judgment fMRI studies support ATL's role as a graded hub for semantic similarity generally, but I found no study directly resolving whether near-synonym *pairs specifically* are represented as distinct-but-close points versus literally collapsed patterns. The best indirect evidence is **Pereira et al. (2018)**, whose decoder distinguishes "even semantically similar sentences," implying fine-grained, non-collapsed distributed codes persist for closely related meanings at the whole-cortex decoding level. A synonym-vs-antonym generation fMRI study found overlapping left-MFG activation for synonym generation, with only coarse (not word-pair-level) dissociation from antonym generation. [SINGLE-STUDY, indirect] **No direct single-unit or fine-grained RSA study of near-synonym separability in cortex was located** — this is a genuine evidence gap, not a resolved question; the two live hypotheses (continuous/graded space → separable-but-close, vs. hub-convergence → compressed/collapsed) have not been directly adjudicated against each other for near-synonyms specifically.
