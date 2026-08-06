# Deep brain-foundational audit: SEMANTIC REPRESENTATION + LEXICAL SIMILARITY

**Filed by:** research (Sonnet), 2026-08-06. Audits `hdlab/lexical_similarity.py` +
`hdlab/verb_lexical_similarity.py` (the FHRR-bundle-of-hand-supplied-feature-tags + cosine organ,
WIRE-DONT-ISLAND-promoted this same date) against the primary neuroscience literature on how the
brain represents word/concept meaning and computes graded similarity. Three parallel Sonnet
lit-scan sub-agents covered (1) the ATL hub-and-spoke representational format, (2) the exact
similarity computation + context-modulation, (3) the learned-vs-supplied acquisition mechanism.
This note is the Opus synthesis + the precise gap-mapping against our own code (read directly,
not assumed).

Per [[feedback-lit-scan-calibration-penalty]]: raw confidence on the core diagnostic claims below
is HIGH (convergent, partly-causal evidence: intracranial ECoG, lesion-deficit, connectionist
mechanistic models) but is deflated 0.15-0.25 for this note's synthesis-level claims, and any
NEW proposed test/combination is capped at P<=0.50.

---

## HEADLINE

**The brain's semantic-similarity computation (cosine/correlation over a feature-composed,
graded population pattern in ventral ATL) is structurally the SAME OPERATION our
FHRR-bundle-cosine organ performs, and this is not a coincidence — the organ's own docstring
already cites the decisive 2024 paper (Cox/Rogers/Shimotake et al.) that licenses exactly this
choice of metric over a co-occurrence/distributional alternative. The gap is not in the
similarity OPERATION or in the graded/distributed OUTPUT FORMAT (both are fair approximations);
the gap is concentrated almost entirely in the FEATURE SOURCE — our tags are hand-named and
hand-assigned by a human reading definitions, where the brain's hub dimensions are unnamed,
emergent, and forced into existence by error-driven learning over grounded multimodal
spoke-convergence (Rogers & McClelland 2004; Chen, Lambon Ralph & Rogers 2017) — plus two
secondary, currently wholly-absent gaps: no context/task reweighting layer (semantic CONTROL,
IFG/pMTG/AG/dmPFC) and no modality-grounding pathway (spokes) at all.** A load-bearing corollary
falls out of the literature that the substrate should NOT act on naively: swapping in a
pretrained distributional/co-occurrence embedding (word2vec/BERT-style) as a shortcut "learned"
feature source would very likely be brain-INFIDELIOUS, not brain-faithful — Carota, Bozic &
Marslen-Wilson (2017, *Cerebral Cortex*) found distributional/co-occurrence similarity predicts
LIFG/pMTG/motor-cortex activity (control/lexical-access regions) with a **null effect in ATL
itself**, while feature-norm-cosine similarity (McRae-style, what our organ already computes) is
what tracks ATL. The correct learning signal for closing the feature-source gap is grounded
**property/feature correlation learned across modality-specific spokes**, not raw corpus
co-occurrence — which is exactly the direction of the already-open 2026-08-03 "build the ~6yo
grounded foundation" project, not a distributional-embedding bolt-on (which would also violate
the standing [[feedback_no_bolt_on_existing_reader_earn_comprehension_own_mechanism_2026-07-27]]
discipline).

---

## 1. Brain mechanism: SHAPE / POSITION / METRIC

| Axis | Brain (vATL hub-and-spoke, controlled semantic cognition) | Confidence |
|---|---|---|
| **SHAPE** | A continuous-valued, graded, distributed population-activity PATTERN, not a discrete symbolic feature list. Cox, Rogers, Shimotake, Kikuchi, Kunieda, Miyamoto, Takahashi, Matsumoto, Ikeda & Lambon Ralph (2024, *Imaging Neuroscience*; preprint bioRxiv 2022.10.27.514039) decoded vATL ECoG during picture naming with representational-similarity-**learning** (RSL): continuous multidimensional target matrices fit vATL patterns 6-13x better than binary present/absent feature matrices, and multiple orthogonal semantic dimensions are decodable simultaneously per concept. This is the direct evidence the code that "amodal, graded, multidimensional" is not just a review-paper slogan. | HIGH (direct, this is the named 2024 paper) |
| **POSITION** | Modality-specific "spokes" (fusiform/inferotemporal=visual form, STG=auditory/word-form, motor/premotor=praxis/action) converge onto ventral ATL (~200-400 ms post-stimulus per Cox et al. 2024) as a transmodal integration hub, which then interacts with a *separate* semantic CONTROL network (IFG pars triangularis/orbitalis, posterior MTG, dorsomedial PFC, angular gyrus) that gates/reweights retrieval for the current task (Lambon Ralph, Jefferies, Patterson & Rogers 2017, *Nat Rev Neurosci* 18:42, "The neural and computational bases of semantic cognition"). The representation-vs-control split is independently confirmed by a lesion double dissociation: semantic dementia (degraded hub/store: consistent, frequency/typicality-sensitive errors across tasks) vs. semantic aphasia (degraded control: inconsistent, cue- and context-sensitive errors) — Jefferies & Lambon Ralph (2006, *Brain* 129:2132). | HIGH for architecture; MEDIUM for exact wiring/timing |
| **METRIC** | Similarity = correlation/distance (RSA: typically 1-Pearson-r, sometimes crossnobis) between the two concepts' population-activity patterns (Kriegeskorte, Mur & Bandettini 2008, *Front. Syst. Neurosci.*, the foundational RSA method paper). Decisively, this pattern-similarity tracks **shared/correlated FEATURE structure** (McRae, Cree, Seidenberg & McNorgan 2005, *Behav. Res. Methods* 37:547, feature-norm cosine), evidenced directly in ATL/pMTG/angular-gyrus RSA (Devereux, Clarke, Marouchos & Tyler 2013, *J. Neurosci.* 33:18906), NOT corpus co-occurrence/distributional (LSA/associative) similarity — Carota, Bozic & Marslen-Wilson (2017, *Cerebral Cortex*, PMC6044349) found distributional similarity predicts LIFG/posterior-MTG/precentral-motor patterns (control/lexical-access regions) but is **null in ATL specifically**. | MEDIUM-HIGH (the feature-vs-co-occurrence dissociation is a single-study result, authors flag ATL null as partly power-limited — treat as converging/suggestive, not airtight) |
| **CONTEXT-MODULATION** | Similarity structure is NOT fixed. A relatively stable hub geometry is dynamically reweighted by the prefrontal/pMTG/AG control network depending on task ("watermelon is like a basketball" in a shape context, "like an apple" in a food context). Direct neural evidence: Gao, Zheng, Gouws, Krieger-Redwood, Wang, Varga, Smallwood & Jefferies (2022, *Cerebral Cortex* 33:152), contextualized conceptual similarity structure emerges specifically in IFG/MFG/dmPFC/precentral gyrus, only when context was actually integrated. Object-level: Bracci, Daniels & Op de Beeck (2017, *Cerebral Cortex* 27:310) — parietal representational content flips to whatever the task demands while ventral-temporal stays category-dominant. Behavioral root: Barsalou (1983, *Mem. Cogn.*) "ad hoc categories," Yee & Thompson-Schill (2016, *Psych. Bull. Rev.*) feature-set shifting by context. | HIGH |

---

## 2. Exact similarity operation, and how it is learned/emergent (not supplied)

**Operation.** The dominant, directly-evidenced neural operationalization of similarity is
population-pattern correlation/distance (RSA), applied to a representation that is itself
composed from feature/property co-activation, not raw associative co-occurrence. An
attractor/Hebbian-energy-overlap framing exists in the computational-modeling literature
(Rogers, Lambon Ralph et al. 2004's attractor networks reproducing semantic-dementia
deterioration) but has not been empirically dissociated from linear pattern-correlation in
cortex — the two are largely observationally equivalent under current RSA methods (LOW-MEDIUM
confidence on this sub-point, largely theoretical).

**Learned, not supplied.** Rogers & McClelland (2004, *Semantic Cognition: A Parallel
Distributed Processing Approach*, MIT Press; précis in *Behav. Brain Sci.* 31:689, 2008) is the
central computational reference: their network's item-identity INPUT units are **localist**
(arbitrary, orthogonal — carry zero built-in feature or similarity content); training is
backpropagation predicting properties/relations from item+context across many exemplars. Because
the input encodes no shared structure, ALL of the model's graded typicality, hierarchical
category differentiation, illusory correlations, and category-specific deficits are byproducts of
one general error-driven learning algorithm discovering unnamed, distributed hidden-layer
structure — no symbolic feature list, no taxonomy, no hand-assigned tags anywhere in the model.
Chen, Lambon Ralph & Rogers (2017, *Nat. Hum. Behav.* 1:0039) extend this to a hub-and-spoke
architecture whose connectivity mirrors measured cortical wiring: the amodal hub representation
is not a stipulated layer, it is *whatever the network converges to* as the bottleneck sufficient
to translate between disparate modality-specific spokes — **convergence forces abstraction**.
Developmentally, infants extract word-referent mappings from raw cross-situational co-occurrence
statistics with no supplied feature list (Yu & Smith 2007, *Psych. Sci.*; Smith & Yu 2008,
*Cognition*), and even the canonical "shape bias" in early word learning is itself a *learned*
second-order statistical regularity distilled from the child's own early vocabulary (Smith,
Samuelson, Colunga program), not an innate feature primitive.

**Are hand-authored feature norms (McRae-style) a legitimate proxy, then?** Partially, and this
is the crux for judging our own organ. McRae-style norms (collected via explicit human
introspection/production) correlate well with neural RSA structure in ATL/pMTG/AG (Devereux et
al. 2013) and with connectionist-model output when fed in as training/probe data (McRae, de Sa &
Seidenberg 1997, *JEP:General*) — so they are a genuine, validated **evaluation target /
behavioral readout**, not a vacuous human artifact. But they are NOT mechanistically equivalent
to the learned representation: they are static, don't update via prediction error, are biased
toward salient/verbalizable properties, and (unlike a trained PDP hub) do not by themselves
reproduce graded typicality, developmental coarse-to-fine differentiation, or the exact
double-dissociation-under-damage pattern without the additional machinery of an error-driven
learning dynamic layered on top. **Bottom line the mainstream literature is unambiguous on:** the
brain's representation is LEARNED-AND-EMERGENT; a hand-built discrete feature list is a coarse,
useful **proxy/validation target**, never a mechanistic account of the acquisition process.

---

## 3. The precise gap vs. our FHRR-bundle-cosine organ (read directly from `hdlab/lexical_similarity.py` + `hdlab/verb_lexical_similarity.py`)

Our implementation: `CONCEPT_FEATURES: Dict[word -> frozenset[str]]` (hand-authored discrete tags,
e.g. `"boat": {NAUTICAL, WATERCRAFT, HAS_HULL, CARRIES_PEOPLE}`), each tag mapped to one
deterministic random unit-phase complex64 vector, a concept's vector = `bundle()` (FHRR
superposition) of its tags' vectors, similarity = `Re(sum(conj(a)*b))/d` cosine, gated by a fixed
`SIMILARITY_LINK_THRESHOLD = 0.50`. Verb module adds two disjoint feature namespaces (outcome
polarity, goal/aspect modality) with the SAME mechanism, and its own docstring already correctly
flags — citing Muraki, Pexman & Binney (2025) — that the amodal-ATL-hub story does NOT cleanly
extend to mental-state/desiderative verbs (which recruit the mentalizing network, mPFC/TPJ,
instead), which is why it kept the namespaces separate rather than force a false unification. That
is itself a brain-fidelity-correct design decision, not a gap.

| Axis | Brain | Ours | Verdict |
|---|---|---|---|
| **SHAPE** | Continuous population pattern; dimensions are UNNAMED, emergent from error-driven learning, high-dimensional and densely co-active (not sparse discrete membership in a handful of named bins) | Discrete, hand-NAMED symbolic tags (2-5 per concept) bundled via FHRR superposition into a continuous-cosine concept vector at N_DIM=8192 | **PARTIAL MATCH.** The concept-LEVEL output is genuinely graded/continuous (cosine values like 0.634 for vessel/ferry vs. 0.398 for sister/rival are not binary) — that structural analog of a distributed population code is fair. The per-feature INPUT layer is where the mismatch lives: a handful of hand-named, hand-assigned symbolic tags is nothing like a high-dimensional emergent hidden layer. This is a feature-SOURCE gap, not a format gap. |
| **POSITION** | Spokes (vision/action/sound) feed a convergence hub; a separate semantic CONTROL network reweights active dimensions per task | No spokes (no modality-grounding pathway of any kind — features are asserted, not derived from any input signal); no control layer (the 0.50 threshold is a single global constant, same for every task/context) | **GAP, currently unaddressed.** Both the grounding pathway and the context-reweighting layer are simply absent from the architecture, not approximated by anything. |
| **METRIC** | Correlation/distance between feature-composed population patterns; decisively feature-correlational, NOT co-occurrence/associative (Carota et al. 2017 ATL-null-for-distributional-similarity finding) | Cosine over a bundle of hand-tagged features | **GOOD MATCH, and already brain-grounded on purpose** — the module docstring explicitly cites Cox/Rogers/Shimotake 2024 for exactly this choice. Computing cosine-of-shared-feature-vectors is structurally the SAME operation class the decisive ATL dissociation evidence says the hub's currency is. This axis should be KEPT, not "fixed." |
| **LEARNED vs. SUPPLIED (the crux)** | Emergent from error-driven statistical learning over grounded, cross-modal experience; hub dimensions are discovered, never hand-named | 100% hand-supplied: a human reads each word's definition and manually assigns named tags per a written rubric (documented, non-circular, but still 100% human-authored) | **THE dominant gap.** This is also honestly self-flagged in both modules' own docstrings ("General open-vocabulary feature coverage... is a separate, missing-LEARNING follow-up, not claimed here"). It is also the mechanism behind the scaling ceiling: the organ cannot classify a genuinely novel word without a human first tagging it — exactly the OOV failure mode that motivated this promotion in the first place (praise/accept/invited never firing in `hdlab/goal_typing.py` until manually added). |

**Direct answer to "is the gap only in feature source, or also representation format + similarity
operation":** Mostly the former. The similarity OPERATION (cosine/correlation over a
feature-composed vector) and the concept-level representational FORMAT (graded, continuous,
distributed via superposition) are both fair, brain-motivated approximations and should be
retained as-is. The gap is concentrated in the feature SOURCE (hand-named/hand-assigned vs.
learned/emergent/unnamed) plus two structurally absent layers (grounding spokes, context-control
reweighting) that the current architecture doesn't even attempt.

---

## 4. Cheap decisive test

**Auto-induced feature substitution probe.** Take the SAME held-out tier-labeled triples the
organ's own `self_test()` already uses as ground truth (`vessel/ferry` = true near-synonym,
`vessel/dock` = related-not-synonym domain-tag-only overlap, `sister/rival` = over-link-guard
analog). Instead of the hand-authored `CONCEPT_FEATURES` tags, induce a feature basis for these
SAME concepts from an unsupervised, non-distributional-associative signal — e.g., sparse
context-window co-occurrence CLUSTERED and filtered for property-sharing rather than raw
co-occurrence strength (the two are dissociable per Carota et al. 2017: raw distributional
similarity predicts the WRONG, non-ATL regions). Run the induced vectors through the identical
`bundle()` + cosine machinery, no human touching the induced tags.

- **HARD-PASS:** induced-feature cosine reproduces the same rank ordering (synonym > related >
  unrelated) with delta >= 0.20 on >=80% of a held-out triple set (roughly half the hand-tagged
  margins: 0.9655 ordered_frac from exp_n11c, 0.634 vs. 0.398/0.279 from self_test), AND a
  scramble-control collapse of >=0.30 delta under label permutation (same convention as the
  existing self_test) — demonstrating the tier-separating structure survives removing the human
  from the naming step.
- **HARD-FAIL:** induced-feature cosine fails to separate synonym from related-not-synonym pairs
  above chance (delta < 0.10), OR the induced basis over-links frequently-co-occurring-but-
  unrelated pairs (e.g. "sailor"/"ship," which co-occur constantly but are related-not-synonym) —
  this would be the direct, predicted signature of accidentally reproducing the ATL-null
  distributional-similarity metric instead of the ATL-tracking feature-correlational one, and
  would falsify "cheap corpus-co-occurrence clustering closes the feature-source gap,"
  redirecting effort toward the grounded-multimodal-experience route instead (per the open
  2026-08-03 "6yo grounded foundation" project) rather than a corpus-stats shortcut.
- Secondary/independent test (context-control layer, lower priority — currently a total absence
  rather than a partial approximation, so any signal here is informative): a small constructed
  probe set of one word in two different task-frames (e.g. "bank" in a river-context sentence vs.
  a finance-context sentence) — HARD-PASS if a simple task-conditioned tag-reweighting scheme
  changes which of two candidate similarity targets wins; HARD-FAIL if reweighting makes no
  measurable difference on any constructed pair, suggesting the fixed-threshold design is
  already adequate for the substrate's current task range and a control layer is not yet the
  priority investment.

---

## 5. Cross-thread synthesis

**Directly antecedent, same-day thread found on a later check of this note (should have been
surfaced before drafting Section 4 -- flagged honestly rather than silently folded in):**
`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` is the design doc that led to the
`hdlab/lexical_similarity.py` promotion this audit examines (its "Option (a) -- SUPPLY a feature
lexicon, EARN the composition" is exactly what shipped). That note already independently reached
two conclusions this audit re-derives from a different literature angle: (i) shared-feature
correlation is the hub's actual metric (it directly fetched and read the same Cox et al. 2024
paper), and (ii) pure linear-window distributional/co-occurrence methods systematically conflate
similarity with relatedness (SimLex-999 vs. WordSim-353 distinction; word2vec skip-gram on ~1B
words reaches only SimLex-999 rho~0.37) -- independent corroboration, via a different citation
path, of this note's Section 4 warning that a naive distributional-embedding swap would target the
wrong metric. That note ALSO already named a concrete, disk-grounded technique for the induced-
feature route this note's Section 4 cheap test calls for in the abstract: **Murphy, Talukdar &
Mitchell (2012, COLING, "Learning Effective and Interpretable Semantic Models using Non-Negative
Sparse Embedding," NNSE)** -- non-negative sparse dictionary learning run DIRECTLY on the
substrate's own (already-built, currently-closed-for-a-different-task) `ppmi_sparse_encoder.py`
co-occurrence matrix, reported to jump human-rated dimension-interpretability from 46% (SVD) to
92% while matching SVD on behavioral-prediction tasks -- i.e. a concrete, previously-identified
algorithm for producing feature dimensions that are induced (not hand-named) yet still
individually inspectable/nameable after the fact, which is a closer match to Section 4's cheap
test than an unspecified "cluster and filter" step. Anchor 1 in the companion exp_dev handoff is
updated to point at this specific precedent rather than reinvent it. That note also flags the same
honest coverage-scaling risk this audit's Section 3 LEARNED-vs-SUPPLIED row makes the dominant
gap: published feature-norm lexicons (McRae ~541 concepts, CSLB ~638) are themselves nowhere near
open-vocabulary scale, so "supply a bigger hand lexicon" was never going to fully close this gap
either -- reinforcing that an induction mechanism (NNSE-on-PPMI, or the grounded-experience route)
is the right target, not a bigger hand table.

This audit also directly builds on and CONFIRMS (rather than contradicts) three further
already-filed threads:

- `notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md` (research/Sonnet, same date):
  that drill already independently reached the "reuse the ATL-hub shared-feature-cosine
  mechanism, extend the feature basis per word class" design and flagged its own P at 0.45
  (capped, novel-synthesis). This audit adds the missing piece that drill didn't cover: the
  precise SHAPE/POSITION/METRIC accounting against the brain, and the explicit warning against a
  distributional-embedding shortcut (which that drill did not raise).
- Both `hdlab/lexical_similarity.py` and `hdlab/verb_lexical_similarity.py` docstrings ALREADY
  cite Cox/Rogers/Shimotake 2024 and the McRae 2005 norms as the justification for the
  cosine-over-hand-tags design, and already self-flag the missing-LEARNING scope limitation.
  This audit independently re-derives and confirms both of those choices were correct, via three
  fresh lit-scans that did not have the code's docstrings as a starting point (query-privacy
  discipline: sub-agents searched generic academic terms, not our implementation specifics).
- MEMORY.md's 2026-08-03 foundational pivot ("BUILD THE ~6yo GROUNDED FOUNDATION reading builds
  on") and the 2026-08-04 "missing-LEARNING" error-flavor discipline both anticipated exactly
  this diagnosis in the abstract; this audit supplies the concrete neural mechanism (spoke
  convergence forces abstraction) and the concrete falsifiable reason a cheaper distributional
  shortcut would NOT satisfy it (the Carota et al. 2017 ATL-null dissociation).

---

## 6. Substrate-product implications

- **Do not swap in a pretrained distributional/co-occurrence embedding model (word2vec, BERT,
  etc.) as an open-vocab shortcut for this organ.** The literature gives a specific, falsifiable
  reason this would be the WRONG fix, not just an inelegant one: distributional/associative
  similarity is carried by non-ATL regions (LIFG, pMTG, motor cortex) in the brain, and produces
  a qualitatively different similarity metric (association/co-occurrence) than the
  feature-correlational one our organ (correctly) approximates. This is also consistent with the
  standing no-bolt-on-reader discipline.
- **The similarity OPERATION and concept-level graded output format are validated — invest
  further effort in the feature SOURCE, not in re-architecting the cosine/bundle mechanism.**
  Any follow-up build should keep `bundle()` + FHRR cosine exactly as-is and change only how
  `CONCEPT_FEATURES`-equivalent tags are populated.
- **The scaling blocker (open-vocabulary coverage) and the brain-fidelity gap are the SAME gap**,
  not two separate problems — closing the missing-LEARNING gap (an automatic, grounded,
  error-driven feature-induction mechanism) would simultaneously fix both the "doesn't scale past
  hand-tagged words" limitation the docstrings already flag AND bring the organ closer to the
  brain's actual acquisition mechanism. This makes it a higher-leverage target than most
  candidate next-builds.
- **A context/task-reweighting control layer is a real, currently-total absence, but is
  secondary** — nothing in the current substrate use cases (goal-owner attribution, outcome
  valence, verb-class membership) obviously requires task-dependent feature reweighting yet; flag
  as a known future gap, not an immediate build priority, pending the secondary cheap test above.

---

## 7. Citations (verified count)

Distinct sources cited across the three sub-agent lit-scans (WebSearch-sourced by the sub-agents;
NOT independently re-fetched/re-verified paper-by-paper by this synthesizing agent — treat
citation accuracy as lit-scan-standard, not primary-source-checked):

1. Cox, Rogers, Shimotake, Kikuchi, Kunieda, Miyamoto, Takahashi, Matsumoto, Ikeda & Lambon Ralph (2024) *Imaging Neuroscience* / bioRxiv 2022.10.27.514039
2. Shimotake, Matsumoto, Ueno, Kunieda, Saito, Hoffman, Kikuchi, Fukuyama, Miyamoto, Takahashi, Ikeda & Lambon Ralph (2015) *Cerebral Cortex* 25:3802
3. Bruffaerts et al. (2021) *eLife* 66276 (animacy code, vATL)
4. Patterson, Nestor & Rogers (2007) *Nature Reviews Neuroscience* 8:976
5. Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson (2004) *Psychological Review* 111:205
6. Jefferies & Lambon Ralph (2006) *Brain* 129:2132
7. Clarke & Tyler (2014) *J. Neuroscience* (perirhinal cortex object-specific coding)
8. Lambon Ralph, Jefferies, Patterson & Rogers (2017) *Nature Reviews Neuroscience* 18:42
9. Kriegeskorte, Mur & Bandettini (2008) *Frontiers in Systems Neuroscience*
10. Devereux, Clarke, Marouchos & Tyler (2013) *J. Neuroscience* 33:18906
11. Gao, Zheng, Gouws, Krieger-Redwood, Wang, Varga, Smallwood & Jefferies (2022) *Cerebral Cortex* 33:152
12. Yee & Thompson-Schill (2016) *Psychonomic Bulletin & Review*
13. Bracci & Op de Beeck (2016) *J. Neuroscience*
14. Bracci, Daniels & Op de Beeck (2017) *Cerebral Cortex* 27:310
15. Barsalou (1983) *Memory & Cognition* ("Ad hoc categories")
16. Hebart, Kaniuth et al. FR-RSA (2022-23, bioRxiv/NeuroImage)
17. McRae, Cree, Seidenberg & McNorgan (2005) *Behavior Research Methods* 37:547
18. Kumar (2021) *Psychonomic Bulletin & Review* 28:40
19. Mandera, Keuleers & Brysbaert (2017) *Journal of Memory and Language*
20. Carota, Bozic & Marslen-Wilson (2017) *Cerebral Cortex* (PMC6044349)
21. Rogers & McClelland (2004) *Semantic Cognition: A Parallel Distributed Processing Approach*, MIT Press; précis *Behavioral and Brain Sciences* 31:689 (2008)
22. Chen, Lambon Ralph & Rogers (2017) *Nature Human Behaviour* 1:0039
23. Yu & Smith (2007) *Psychological Science*; Smith & Yu (2008) *Cognition*
24. Smith, Samuelson, Colunga shape-bias program (multiple; no single canonical review pinned)
25. Yu, Smith & Pereira, "Grounding word learning in multimodal sensorimotor interaction"
26. Binder, Conant, Humphries et al. (2016) *Cognitive Neuropsychology*
27. McRae, de Sa & Seidenberg (1997) *Journal of Experimental Psychology: General*
28. Devereux et al. (2014) CSLB property norms
29. Muraki, Pexman & Binney (2025) — already cited in `hdlab/verb_lexical_similarity.py`'s own docstring (mental-state verbs, mentalizing network vs. vATL)

**29 distinct sources.** Confidence per-claim flagged inline in Sections 1-2 above (mix of HIGH /
MEDIUM-HIGH / MEDIUM / LOW-MEDIUM); no claim in this note rests on a LOW-confidence source alone.

---

## P estimates (calibrated)

- P_deflated = **0.62** that the core diagnostic (feature-source is the dominant gap; cosine
  operation + graded format are fair approximations; distributional-embedding shortcut would be
  brain-infidelious) is correct as stated — raw convergent-evidence confidence ~0.85, deflated
  0.23 per lit-scan calibration discipline.
- P_deflated = **0.40** (capped near novel-synthesis 0.50, further deflated) that the specific
  proposed cheap-decisive-test (auto-induced feature substitution via co-occurrence clustering
  filtered for property-sharing) will HARD-PASS rather than HARD-FAIL — this is genuinely
  untested, and the Carota et al. 2017 dissociation gives a real, non-trivial chance the induced
  basis reproduces the wrong (associative) similarity structure, which is exactly why the test is
  informative either way.
