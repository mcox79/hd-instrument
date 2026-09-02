# Brain-foundational fidelity audit of the LEARNED-graph mechanism + adjacent-component map

Written 2026-09-01 by the solver, while the smoke run executes. Two research drills (below) sharpened the
design and surfaced ONE honest self-critique. Tags: [PINNED] brain-fixed | [MODELLED] a specific model of a
pinned mechanism | [OUR-INVENTION] swept | [BORROW-TO-REEXAMINE] a label we inherited that may not fit.

## A. Fidelity audit of MY mechanism, component by component

| component (in the cell) | brain mechanism | status | fidelity note / wall |
|---|---|---|---|
| **E-step = soft, top-k, context-weighted sense responsibilities** (one PPR/sentence) | **Reordered Access** (Duffy/Rayner; Twilley): ALL senses activate, ORDER set by dominance + context | **PINNED, validated** | Drill 2 confirms: multiple meanings activate, context reorders. **Refinement to test:** reordered access says the soft responsibility = dominance-reweighted-by-context, i.e. the log-linear **blend (prior + λ·PPR)**, NOT pure context. I currently use pure-context PPR. Blending in the resting-level prior is the more faithful E-step. |
| **PPMI surprise-weighting of edges** | **N400 = lexical prediction error; larger surprise → stronger encoding** (Rabovsky 2018) | **PINNED (lever), MODELLED (PPMI form)** | Proven the decisive lever in `does_learning_from_reading` (RAW→PPMI flips the result). Its own caveat: that win was on similarity ratings and did NOT transfer to a different scorer — so **transfer to WSD is the thing I am measuring, not assuming.** |
| **Cross-situational gate** (support ≥ MIN_COOC) | **Cross-situational statistical word learning** (Yu & Smith 2007) | **PINNED** | The evidence gate before a link crystallizes. |
| **Schema-gate** (edge fast if endpoints already neighbours, slow/down-weighted if novel) | **Schema-gated cortical learning** (Tse 2007; McClelland 2013) | **[BORROW-TO-REEXAMINE]** | ⚠️ HONEST SELF-CRITIQUE. The brain needs CLS/schema-gating because cortex is a **gradient/Hebbian net that catastrophically interferes**. My accumulator is **additive PPMI counts — inherently non-forgetting** (adding an edge never overwrites another). So the schema-gate's real job here is NOT anti-interference; it is **PRECISION** — refusing spurious novel edges. That is a *different* brain function: **semantic control (LIFG/pMTG precision-weighting)**, not hippocampal CLS. I should relabel it and test it as precision-control, and NOT claim CLS anti-interference credit unless a gradient-learner variant needs it. |
| **Interleaved replay = iterate E/M** (re-disambiguate as the graph improves) | **NREM replay / interleaving** (McClelland 1995; Kumaran 2016) | **PINNED (mechanism), REFRAMED (function)** | Same critique: replay's classic function (protect old memories) is moot for a count-accumulator. Its REAL value here is **bootstrapping** — a better graph gives better E-step disambiguation, which gives better edges (Srinivasan: use one sense to acquire the next). That IS worth iterating; I just shouldn't sell it as anti-interference. |
| **Split/merge of senses** (ultrametric clustering of context vectors) | **Semantic chaining** (Xu/Malt/Srinivasan; PNAS 2025 word-sense acquisition) — a new sense CHAINS from an existing one by similarity | **PINNED, DEFERRED** | Drill 1: chaining is the pinned mechanism for GROWING NEW senses. But it **cannot help WSD scored against fixed WordNet gold** (the gold IS the WordNet inventory). It is the core of the **novel-sense / OOV branch**, not the primary bar. Correctly deferred. |
| **Discrete weighted edges on the WordNet graph** | **Continuous, distributed, overlapping semantic space** (Huth 2012; Nat Commun 2020) | **[OUR-INVENTION substrate]** | ⚠️ THE DEEPEST TENSION. The brain's representation is a *continuous* space; WordNet-with-edges is a lossy discretization. My grown edges *approximate* continuous distributional structure on a discrete scaffold. If growth walls, the faithful fix may be **continuous node embeddings fused at read** (meaning_fusion already builds these), not more discrete edges. This is the top adjacent opportunity (§C). |

**Net fidelity verdict:** the *learning signal* (reordered-access disambiguation + surprise-weighting + cross-situational gate) is PINNED and well-grounded. The *consolidation framing* (CLS/schema-gate/replay) is partly a **category-borrow** — for a count-accumulator its true function is **precision-control + bootstrapping**, not anti-interference. I will (a) test the schema-gate honestly as precision-control (does it raise WSD by refusing spurious edges?), (b) test the reordered-access blend E-step, and (c) keep the continuous-space fix as the named fallback if discrete edges wall.

## B. The walls I can already see, and how the research resolves each

1. **WordNet++ saturation (edges already there).** The static `cn_syn` graph already has 88k *manual* SyntagNet syntagmatic edges. My learned edges may be REDUNDANT with those. **Discriminator (build it in):** grow on `base` (no SyntagNet) vs grow on `cn_syn`. If growth helps `base` but not `cn_syn`, that is a POSITIVE result stated correctly — *"reading re-derives, unsupervised, the syntagmatic structure that SyntagNet supplied by hand"* — which is exactly the north-star (grow your own foundation). If it helps neither, the signal isn't there.
2. **Transfer (PPMI representation → WSD edges).** Understood as the `does_learning` cross-scorer caveat. Measuring on the actual bar.
3. **Discrete vs continuous (§A last row).** If discrete edges wall, the brain says the representation is continuous — the fix is node embeddings (meaning_fusion), a different substrate → a clean next problem, not a dead end. *"If the brain can do it we can too, once we understand"* — the understanding here is: the brain isn't adding edges to a dictionary, it is deforming a continuous space; a discrete-edge wall would be evidence FOR the continuous substrate, not against growth.

## C. Adjacent-component evaluation → candidate next problems (capability / limitation / brain-status / opportunity)

Derived from the substrate map (Explore sweep, 2026-09-01). Each seeds a verdict-independent next problem.

1. **`hdlab/meaning_fusion.py`** — fuses a learned distributional spoke + grounded sensorimotor spoke (ATL hub-and-spoke).
   - CAP: WordSim ~0.45; the right *architecture* (Patterson/Lambon Ralph, PINNED). LIM: offline, **unwired into the live reader**; no per-context sense selection. BRAIN: hub-and-spoke PINNED. OPP (high): this IS the **continuous-space** substrate my §A tension points to — the grown graph could carry meaning_fusion node vectors and fuse them at read. **NEXT PROBLEM: wire meaning_fusion into the reader as the continuous node-content of the semantic graph (fixes the "meaning islands" debt).**
2. **`hdlab/distributional_meaning_channel.py`** — PPMI+SVD over the separable co-occurrence store.
   - CAP: substitutability AUC 0.84. LIM: "actively bad" at general relatedness (WordSim −0.24); idle island. BRAIN: distributional spoke, but narrow. OPP: it is the ready-made PPMI engine my growth needs; reuse its `ppmi_svd` rather than my hand PPMI at scale. **NEXT PROBLEM: reconcile the two PPMI paths (mine on synsets, its on words) into one sense-resolved distributional channel.**
3. **`hdlab/cls_growth.py` + `hdlab/continual.py`** — the CLS kit (`align_and_fuse` slow-anchor EMA, `rollback_gate`, NREM `replay_cycle`).
   - CAP: validated drift-mitigators. LIM: **islands** (docstring: "no live organ calls it"); torch. BRAIN: replay PINNED. OPP: needed IF growth moves to a **gradient/embedding** learner (where interference is real — see §A critique). **NEXT PROBLEM: only becomes load-bearing once node embeddings are learned online; pin it to that.**
4. **`hdlab/cortical_recall.py` + `hdlab/substrate.py`** — the consolidated ("cleaned") store, **written-but-never-read** (`substrate.py:47`).
   - CAP: `cortical_recall` is a finished read organ. LIM: not on the default retrieval path (episodic route wins). BRAIN: systems consolidation. OPP: **the flagged real completion** — but note it is the *fact/identity* store, a DIFFERENT store from my *semantic-graph* edges. My growth wires the graph; this wires the fact store. **NEXT PROBLEM (independent of mine): route the default read through the consolidated store.** I should NOT conflate the two in SOLVED.md.
5. **`hdlab/ultrametric_clustering.py`** — single-linkage cosine clustering; sense split/merge substrate.
   - CAP: RG coarse-graining, pure numpy. LIM: island. BRAIN: **semantic chaining** substrate (§A). OPP: the engine for the novel-sense branch. **NEXT PROBLEM: usage-based sense induction (split/merge) evaluated on novel-sense / OOV, where fixed-WordNet WSD can't score it.**
6. **`hdlab/semantic_control.py`** — LIFG/pMTG conflict-gated precision (from the parent).
   - CAP: PINNED precision gate; trigger AUC ~0.79. LIM: island. BRAIN: PINNED. OPP: **this is what my schema-gate actually is** (§A) — the precision control that refuses spurious edges. **NEXT PROBLEM: unify the write-time precision gate (my schema-gate) with the read-time precision gate (semantic_control) — one LIFG precision mechanism for read AND write.**

## D. THE WALL UNIFICATION (drill of ALL context-conditioned-sense-selection negatives, 2026-09-01)

Every negative in this area is ONE fidelity gap. Drilled: parent naive-learning NEGATIVE; `schema_gated`
HARD_FAIL (shared topic vocab); `does_learning` cross-scorer caveat; **`the_prior_swamps_the_channel`
[REFUTED]**; **`context_conditioned_sense_selection` [HARD_FAIL x2]**; the parent's three-mechanism
convergence (PPR/blend/settling all hit "context-signal strength").

**What the two new negatives establish (on disk):**
- prior_swamps: on subordinate senses a MONOTONE prior+context blend cannot beat context-alone (oracle
  monotone 0.4748 = channel 0.4811, no headroom); only SIGNED SUPPRESSION wins (->0.767) but see-saws
  and crashes dominant items; and **no gold-blind detector for when-to-suppress exists (all AUC ~0.51)
  because the bag-of-words context channel is itself frequency-biased** (95.65% of its errors land on a
  higher-frequency sense).
- context_conditioned HARD_FAIL: sense selection **did not survive same-segment TOPIC control** -- the
  co-occurring words are topic-related, not sense-diagnostic.

**The brain's mechanism (research-confirmed), step by step:**
1. All senses activate, ORDERED by frequency -- a BOTTOM-UP, CONTEXT-INDEPENDENT stream in a widespread
   cortical network (MIT Neurobiol Lang 2022; reordered access, Duffy/Rayner).
2. IN PARALLEL, a SEPARATE top-down constraint from SYNTAX + SELECTIONAL PREFERENCES (verb-argument, head-
   dependent) -- FREQUENCY-INDEPENDENT because syntax is orthogonal to frequency (Lin; Wilks preference
   semantics). [LIFG/pMTG semantic-control network, left-lateralized.]
3. SELECT by INHIBITION: subordinate-biasing context -> LIFG suppresses the dominant competitor (biased
   competition, Desimone-Duncan); dominant-biasing context needs NO inhibition (pure surplus activation) --
   the asymmetry the neuro confirms. Right hemisphere maintains alternates for revision.
4. The when-to-suppress DETECTOR = the PRECISION/reliability of the syntactic constraint vs the prior
   (precision-weighting, Feldman-Friston).

**WHERE WE DIFFER -- the precise gaps:**
| brain | us (current) | consequence |
|---|---|---|
| frequency + context = SEPARATE streams | we BLEND them (log-linear) | prior_swamps: monotone blend swamps subordinate |
| context = SYNTACTIC/selectional (freq-independent) | BAG-OF-WORDS (now windowed = partial fix) | topic-contaminated -> no detector (HARD_FAIL) |
| SELECT by inhibition (suppress competitor) | linear PPR can only ADD | can't do subordinate override |
| detector = syntactic-constraint precision | no frequency-independent detector | all detectors AUC ~0.51 |

**THE ACTIONABLE UNIFICATION:** the win condition for context-conditioned sense selection is
(a) a FREQUENCY-INDEPENDENT syntactic/selectional context signal + (b) INHIBITORY competitive selection
gated by that signal's reliability. **Both selection organs already exist** -- `_settle` (competitive
attractor settling, built in the parent) and `hdlab/semantic_control.py` (LIFG precision gate). They were
"negatives for argmax-WSD" in the parent BECAUSE the signal they were gating was bag-of-words (frequency-
biased). **The missing piece is the syntactic signal, not the selection machinery.** Cheap proxy added now
(windowed co-occurrence); the full lever is dependency-parsed selectional edges (needs a parser; the next
rung if the windowed run walls on the subordinate subset -- which prior_swamps predicts it will).

## Research drills (sources)
- Continuous, distributed semantic space (not discrete regions): Huth et al., *A continuous semantic space...*, and cortical semantic-relation mapping. Word-sense acquisition by **semantic chaining** (new senses extend from existing by similarity), PNAS 2025-26. GPT-2 embeddings predict association-cortex (not sensorimotor) semantics — supports fuse-don't-choose.
- **Reordered Access** (all senses activate; dominance + context set the order; dominance persists even under subordinate-biasing context) — validates soft multi-sense responsibilities AND argues the E-step should blend dominance with context.

Sources:
- [A continuous semantic space describes the representation of thousands of object and action categories across the human brain (Huth et al.)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3556488/)
- [Connecting concepts in the brain by mapping cortical representations of semantic relations (Nat Commun 2020)](https://www.nature.com/articles/s41467-020-15804-w)
- [Discovering regularity and mechanisms of word sense acquisition in childhood (PNAS)](https://www.pnas.org/doi/abs/10.1073/pnas.2525788123)
- [Dominance and context effects on activation of alternative meanings (Memory & Cognition)](https://link.springer.com/article/10.3758/MC.36.7.1306)
- [Information-Restricted Neural Language Models Reveal Different Brain Regions' Sensitivity to Semantics/Syntax/Context (Neurobiology of Language)](https://direct.mit.edu/nol/article/4/4/611/117823/Information-Restricted-Neural-Language-Models)
- [Lexical Frequency and Sentence Context Influence the Brain's Response to Single Words (Neurobiology of Language 2022) -- frequency processed independently of context](https://direct.mit.edu/nol/article/3/1/149/107293/Lexical-Frequency-and-Sentence-Context-Influence)
- [Sentence context and lexical ambiguity resolution by the two hemispheres -- LH selects, RH maintains alternates](https://www.sciencedirect.com/science/article/abs/pii/S0028393298000426)
- [A knowledge-based WSD algorithm utilizing syntactic dependency relation (Lin-style) -- subject/object of a verb beat random nearby words](https://ieeexplore.ieee.org/document/8117155)
