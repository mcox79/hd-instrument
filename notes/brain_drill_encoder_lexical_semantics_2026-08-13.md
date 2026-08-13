# Brain drill — the ENCODER: how the brain builds and stores lexical-semantic representations

Filed: 2026-08-13. Role: research (Opus synthesis + 5 parallel Sonnet lit-scans, ~180 sources touched).
Scope: READ-ONLY on code. No experiments run. HEAD = `7b4d8654f`.
Trigger: USER standing directive — "every time you look into a component, do a drill to deeply
understand EXACTLY how the brain does it, and that should be your first goal to duplicate that."

---

## HEADLINE

**The brain does not separate near-neighbours by having a better encoder. It separates them with
DISTINCTIVE features — features present in FEW concepts — which are privileged, fast, and
structurally fragile; and with a semantic-control system that dynamically up-weights exactly those
fragile features when the task needs them. Our comparator has NEITHER: `concept_similarity` is an
UNWEIGHTED shared-feature overlap (a tag shared by 8 concepts counts exactly as much as a tag
shared by 1), which is the precise INVERSE of the brain's privileging, and it has no context port
at all for control-gain to act through. The literature independently confirms the USER's
recollection that trained encoders were the wrong lever: dense trained embeddings score 0.41
Spearman on the benchmark purpose-built for this exact synonym/sibling distinction, and what
closes most of the gap to human agreement (0.67) is INJECTING EXPLICIT RELATIONAL STRUCTURE
(0.41 -> 0.58 -> 0.74), not more or better training.**

---

## PART 1 — THE BIOLOGY (led with, before any code was read)

### 1.1 The pathway and what the hub actually computes

Orthographic input -> VWFA (left mid-fusiform) -> superior/ventral temporal -> **ATL amodal hub**
<-> modality-specific spokes. The hub is bilateral, graded, with a ventrolateral (vATL) center of
gravity.

The 2017 baseline statement (Lambon Ralph, Jefferies, Patterson & Rogers, *Nat Rev Neurosci*
18:42-55) is that the hub pools spoke inputs into representations capturing cross-modal similarity
structure absent from any single modality (grouping "dolphin" with mammals, not fish).

**The 2020-2026 literature has sharpened this considerably, and the sharpening matters for us.**
The hub is **not** a similarity space and **not** a feature-averaging device. Per Jackson, Rogers &
Lambon Ralph 2021 (*Nat Hum Behav* 5:774+) and the Jackson/Orban/Tiesinga 2026 synthesis
(*Neurobiology of Language*), it performs a **deep, recurrent, nonlinear transformation whose core
operation is PATTERN COMPLETION via a compact abstract "label"** that feeds back onto unimodal
feature representations held in shallower layers. Empirically: Rogers, Cox, Lu, Shimotake et al.
2021 (*eLife* 10:e66276), direct ECoG in 8 patients, found the vATL animacy code is not a stable
feature detector but changes dynamically and nonlinearly with processing time (decodable ~200 ms;
representational-geometry breakpoint ~473 ms; anterior-posterior electrode position predicted
degree of dynamic change, r^2=0.73, p<0.002). [ESTABLISHED]

Graded, not uniform: Rice, Lambon Ralph & Hoffman 2015 (*Ann NY Acad Sci* 1359:84-97); Binney,
Hoffman & Lambon Ralph 2016 (*Cereb Cortex* 26:4227-4241). [ESTABLISHED] Which subregion is the
DEEPEST convergence point (ventrolateral "VL" vs temporal-pole tip "Tip") is a live 2023-2026
dispute (Tiesinga et al. 2023 *Sci Rep* sEEG vs the prior fMRI/ECoG consensus). [CONTESTED]

Spokes are not passive: white-matter work (*Brain* 2020) shows semantic-deficit severity tracks
BOTH ATL grey-matter atrophy AND reduced hub-spoke connectivity. Whether modality-specific info is
retrieved *via* the hub or accessible in parallel is the sharpest live fault line. [CONTESTED]

Serious challenges to hub-and-spoke, stated fairly: Huth/Gallant continuous semantic tiling
(*Nature* 2016, 532:453-458; Popham et al. 2021 *Nat Neurosci*) and Fernandino/Binder distributed
experiential-attribute accounts (*Cereb Cortex* 2016; *J Neurosci* 2022). Lambon Ralph's reply
("Semantic tiles or hub-and-spokes?", *TiCS* 2022) frames reconciliation as open, not settled. The
2024-2026 center of gravity treats these as **complementary**, not mutually exclusive.

### 1.2 Is it gradient-descent-like, or Hebbian/competitive? — the answer BIFURCATES

This is the question I expected to be a hedge and it is not. **The literature splits cleanly by
what is being learned.**

- **Sensory/perceptual hierarchies**: the backprop-approximation program is live and mathematically
  serious (Lillicrap, Santoro, Marris, Akerman & Hinton 2020 *Nat Rev Neurosci* 21:335-346;
  Whittington & Bogacz 2019 *TiCS*; Millidge et al. 2022 *Neural Computation* 34:1329-1368;
  Sacramento et al. NeurIPS 2018; Payeur et al. 2021 *Nat Neurosci* 24:1010-1019). No direct
  empirical confirmation; plausible circuit implementations exist. [CONTESTED as biological fact]
- **Pure local/Hebbian alternatives do NOT scale** — this is the strongest argument that SOME
  error-driven signal is needed: Bartunov, Santoro, Richards, Marris, Hinton & Lillicrap (NeurIPS
  2018) found target-prop/feedback-alignment match backprop on MNIST but degrade sharply on
  CIFAR/ImageNet; Illing, Gerstner & Brea 2019 (*Neural Networks* 118:90-101) found unsupervised
  local learning of hidden weights did not beat FIXED RANDOM projections at scale. [ESTABLISHED]
- **BUT lexical-semantic acquisition is a THIRD mechanism, neither of those.** Complementary
  Learning Systems (McClelland, McNaughton & O'Reilly 1995 — pre-2015 classic, STILL the standard
  reference; Davis & Gaskell 2009 *Phil Trans R Soc B* 364:3773-3800; Kumaran, Hassabis &
  McClelland 2016 *TiCS* 20:512-534): a new word is ingested by **fast hippocampal
  associative/relational binding**, and only becomes a competitive lexical entry through **slow,
  offline, sleep-gated cortical consolidation via replay**. [ESTABLISHED]

The consolidation evidence is decisive on timing. Dumay & Gaskell 2007 (*Psychol Sci* 18:35-39):
novel words show NO lexical-competition effect immediately, but do after a 12-h interval containing
sleep; matched waking interval does not produce it. 2021 meta-analysis (*Psychon Bull Rev*, ~25
studies, ~1,396 participants): g=0.50 overall, g=0.57 recall, g=0.52 recognition. Bakker et al.
2015: N400 shifts from MTL/hippocampal to neocortical engagement after consolidation.
[ESTABLISHED]

**The strong "fast mapping writes straight to cortex" story has COLLAPSED under replication** and I
report it as such rather than citing the headline result: Coutanche & Thompson-Schill 2014
(*JEP:Gen* 143:2296-2303) and Sharon, Moscovitch & Gilboa 2011 (*PNAS*) are both contradicted by
Warren & Duff 2014 (*Hippocampus* 24:920-933), Cooper, Greve & Henson 2019 (*Cognitive
Neuroscience* 10:196-209), and a 2023 *Cognitive Neuropsychology* replication failure.
[FAILED-REPLICATION]

**Net: at exposure time the brain is NOT running gradient descent. It writes an index. The
structured representation is built later, offline.**

### 1.3 Sparsity and code format

Two regimes, and conflating them is a trap:

- **MTL / hippocampal concept cells: SPARSE.** Waydo, Kraskov, Quian Quiroga, Fried & Koch 2006
  (*J Neurosci* 26:10232-10234) is the source of the real number: from 1,425 units over 34
  sessions, fewer than **2x10^6 of ~10^9 MTL neurons (~0.2%)** per percept; run the other way,
  each neuron fires to ~50-150 different concepts. Quian Quiroga 2012 (*Nat Rev Neurosci*
  13:587-597): "sparse but NOT grandmother-cell." A two-population refinement (arXiv 1411.3917)
  shows sparseness is bimodal, not uniform. [ESTABLISHED]
- **Neocortical semantic code: DENSE-distributed, LOW effective dimensionality.** Huth et al. 2012
  (*Neuron* 76:1210-1224): first ~4 group principal components define the shared semantic space.
  Huth et al. 2016 (*Nature* 532:453-458): continuous overlapping gradient maps tiling cortex.
  Binder et al. 2016 (*Cogn Neuropsychol* 33:130-174): ~65 experiential attributes across 14
  domains. Tiesinga et al. 2023 sEEG: ~**two-thirds** of temporal-pole electrode populations
  activated per single exemplar — distributed, explicitly NOT sparse. IT-cortex sparseness indices
  run ~0.2-0.3, markedly denser than MTL. [ESTABLISHED]

**Shape implication:** the semantic hub is a dense, low-effective-dimensional, GRADED code — not a
sparse binary tag set, and not a high-dimensional near-orthogonal code. Note also Stringer et al.
2019 (*Nature* 571:361-365) power-law spectra are **early visual cortex**, a different system; do
not import that story into semantics.

### 1.4 Grounding: constitutive or associated?

The field has moved decisively to **hybrid / dual-coding**, away from strong embodiment.
[ESTABLISHED shift]

- TMS causal evidence has WEAKENED: Solana & Santiago 2022 (*Neurosci Biobehav Rev*) p-curved 43
  TMS/tDCS studies, estimated power <30%, publication-bias signatures, "cannot yet assert beyond
  reasonable doubt that they explore real effects." Montero-Melis et al. 2022 preregistered
  replication failure. Lesion evidence (Argiriis et al. 2020): sensorimotor-cortex lesions produce
  no significant action-verb comprehension deficit. [CONTESTED, converging negative]
- **The decisive natural experiment**: Wang, Men, Gao, Caramazza & Bi 2020, "Two Forms of Knowledge
  Representations in the Human Brain," *Neuron* 107:383-393 — congenitally blind adults' object-
  colour knowledge. Most colour-representing regions were sighted-only, BUT **left dorsal ATL
  represented colour knowledge in BOTH groups**: a sensory-independent, language-derived coding
  system coexists with the sensory-derived one. Synthesised as dual coding in Bi 2021 (*TiCS*
  25:883-895). Bedny-lab work shows congenitally blind adults distinguish see/look/peek/stare with
  sighted-like structure. [ESTABLISHED]
- **The most load-bearing recent result for us**: Xu, Peng, Nastase, Chodorow, Wu & Li 2025,
  "Large language models without grounding recover non-sensorimotor but not sensorimotor features
  of human concepts," *Nature Human Behaviour* — ~4,442 concepts against Glasgow (829 raters) and
  Lancaster (3,500 raters) norms. Alignment is high for non-sensorimotor dimensions, **drops
  sharply into sensory, and is minimal for motor**. [SINGLE-STUDY but large-scale and directly
  on-topic]
- Abstract concepts: Borghi's words-as-social-tools / multiple-representation view; Vigliocco et al.
  2014 emotion; Connell & Lynott interoception; Dove 2016 (*Psychon Bull Rev* 23:1109-1121) and
  2019 arguing language is a genuine additional representational format, not a workaround.
- **Norms are necessary but demonstrably insufficient.** Lancaster (Lynott, Connell, Brysbaert,
  Brand & Carney 2020, 39,707 words, 11 dims) + Brysbaert, Warriner & Kuperman 2014 (40k words).
  Johns et al. 2023 (*Behav Res Methods*) tested sensorimotor distance directly against human
  similarity across three benchmarks: consistently among the best-fitting predictors but **"never
  the overall best predictor" in any single dataset**. The specific claim that sensorimotor norms
  COLLAPSE near-synonyms is theoretically well-motivated in that literature but **empirically
  untested** — flagged as a genuine literature gap.

  **WE HAVE THE MISSING MEASUREMENT.** `hdlab/grounded_similarity.py`'s own docstring records it:
  sofa/couch 0.968, happy/joyful 0.962 (TRUE SYNONYMS) versus apple/orange 0.952, dog/cat 0.932
  (DISTINCT SIBLINGS) — statistically inseparable, and percentile-normalising against a 2,000-pair
  random background does not rescue it (both classes sit at/above p95-p99.9, fully overlapping).
  This is a real, owned, substrate-side empirical contribution to an open question in the norms
  literature.

### 1.5 FOCAL QUESTION — separating synonyms from siblings

**The brain's answer, and it is specific.**

**(a) The discriminating information is DISTINCTIVE FEATURES — features present in FEW concepts.**
Cree, McNorgan & McRae (*JEP:LMC*, PMC3226832): "Distinctive Features Hold a Privileged Status in
the Computation of Word Meaning" — distinctive features are verified FASTER and weighted more
diagnostically than shared features in healthy processing. [ESTABLISHED] Tyler & Moss's Conceptual
Structure Account (*TiCS* 2001; Taylor, Devereux & Tyler 2011; Devereux et al. 2014 CSLB norms):
two statistical properties govern a feature's fate — **distinctiveness** (how few concepts share
it) and **correlational strength**. Distinctive features are typically WEAKLY correlated with a
concept's other features, which makes them **computationally fragile**, because attractor settling
is driven by correlational structure. [ESTABLISHED, actively maintained]

**(b) The brain's own natural experiment proves near-neighbour discrimination is the FIRST thing to
break.** Semantic dementia (Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson
2004, *Psychol Rev* 111:205-235 — canonical): as the ATL hub degrades, errors appear FIRST as
**coordinate confusions within a category** (couch -> "chair", goat -> "sheep"), and only later as
cross-category/superordinate errors. Atypical exemplars and their distinctive features go first;
shared features survive; the result is simultaneous over- and under-generalisation, drift toward
the prototype. [ESTABLISHED] **This is exactly our failure mode, and the brain tells us its cause:
loss of the low-redundancy distinctive features, not loss of the category.**

**(c) Semantic control does NOT select from a candidate list — it applies GAIN.** Chiou & Lambon
Ralph 2018 (*Cortex*, PMC6006425), DCM: IFG's effective connectivity to the spoke holding the
currently task-relevant feature dimension was selectively boosted (F(2,34)=3.86, p=.03). Control
"dynamically heightens its connectivity with relevant components of the representation system."
The double dissociation (Jefferies & Lambon Ralph 2006, *Brain* 129:2132-2147) is the strongest
evidence in the literature: **SD** = coordinate/superordinate errors, CONSISTENT across sessions,
phonemic cueing does NOT help (knowledge gone); **semantic aphasia** = associative errors
(squirrel -> "nuts") SD patients never make, INCONSISTENT across sessions, cueing DOES help,
selectively impaired when a weak target must beat a strong competitor (knowledge intact,
inaccessible). Meta-analyses: Noonan et al. 2013 (*JOCN* 25:1824-1850, 53 studies); Jackson 2021
(*NeuroImage*, 925 peaks / 126 contrasts) — the latter finds NO consistent angular-gyrus
involvement, contradicting the former. [CONTESTED on AG; ESTABLISHED on IFG/pMTG]

Gao et al. 2022 (*eLife*): retrieving a NON-DOMINANT association recruits a **higher-dimensional**
coding regime; dominant associations use a lower-dimensional one (dimensionality change mediated
51.7% of the gradient-cognition relationship). Computational instantiation: Hoffman, McClelland &
Lambon Ralph 2018 (*Psychol Rev* 125:293-328) — the SAME hub weights plus different control
settings reproduce context-dependent behaviour. [ESTABLISHED]

**(d) A possible second, hippocampal discriminator — flagged, not relied on.** "The human
hippocampus can pattern separate memories by meaning," *PNAS* 2026 (10.1073/pnas.2603114123):
hippocampal patterns orthogonalise as a function of SEMANTIC similarity. Sits atop an unresolved
dispute (Quian Quiroga, "No Pattern Separation in the Human Hippocampus," *TiCS* 2020, and the 2021
rebuttal). [SINGLE-STUDY, contested foundation — do NOT build on this yet]

**(e) Synonyms specifically: thin, and I report the thinness.** No dedicated fMRI-RSA study
isolating synonym pairs was located. Best available: Edmonds & Hirst 2002 (*Computational
Linguistics* 28:105-144) — near-synonyms are a **shared core denotation plus differentiated
periphery** (register, expressive, collocational), NOT identical meanings with different labels;
and the N400 literature, where couch/sofa is the textbook case of a violated LEXICAL but not
SEMANTIC expectation. Prediction from CSC: synonyms should show minimal ATL representational
distance and differ mainly in control-weighted register dimensions. [Largely UNTESTED directly]

**(f) The ML mirror is exact and quantitative — this is the load-bearing number.** Distributional
models conflate synonyms, antonyms and co-hyponyms because symmetric co-occurrence cannot
distinguish them ("the water is hot/cold" — same frame). On SimLex-999 (Hill, Reichart & Korhonen
2015, *Comput Ling* 41:665-695; human inter-annotator agreement ~0.67), from Mrkšić et al. 2016
Table 2 (arXiv:1603.00892):

| representation | SimLex-999 Spearman |
|---|---|
| GloVe (trained, distributional) | **0.41** |
| GloVe + retrofitting (Faruqui et al. 2015) | 0.53 |
| GloVe + counter-fitting (explicit syn/ant constraints) | **0.58** |
| Paragram-SL999 | 0.69 |
| Paragram-SL999 + retrofitting | 0.68 (no gain) |
| Paragram-SL999 + counter-fitting | **0.74** (above human IAA) |

Levy, Goldberg & Dagan 2015 (*TACL* 3:211-225) independently show that once hyperparameters are
matched, count-based PPMI+SVD and neural embeddings have **no consistent significant advantage**
either way — and Levy & Goldberg 2014 prove SGNS is implicitly factorising a shifted-PMI matrix,
i.e. the same object the count method builds explicitly. [ESTABLISHED]

### 1.6 CRITICAL: trained encoder, or simple ingestion + machinery? — the literature's answer

**The literature does not support "word meaning = one trained encoder producing a rich static
vector."** Converging, from four independent directions:

1. **Acquisition** is fast hippocampal indexing, not gradient descent at exposure. Teyler & Rudy
   2007 (*Hippocampus* 17:1158-1169): "the hippocampus itself does not contain the content of an
   experience but it does provide an index." Modern mechanistic revival: Goode, Tanaka, Sahay &
   McHugh 2020 (*Neuron* 107:805-820). CA3 completion / DG separation directly measured:
   Neunuebel & Knierim 2014 (*Neuron* 81:416-427). Treves & Rolls CA3 capacity ~36,000 patterns.
2. **Structure** is built OFFLINE by replay-driven consolidation, hours-to-days later (§1.2).
3. **Read-out is reconstructive, not a static lookup.** Yee & Thompson-Schill 2016 (*Psychon Bull
   Rev* 23:1015-1027) — conceptual activation is graded and context-modulated at every timescale;
   a concept is a RETRIEVAL EVENT shaped jointly by a stored substrate and control processes.
   (Honest caveat: this is a claim about flexible ACCESS; it does not prove the stored substrate is
   simple. Casasanto & Lupyan's stronger "all concepts are ad hoc concepts" is theoretical, not
   data-driven. [CONTESTED])
4. **The ML evidence points the same way**: knowledge injection beats training (§1.5f); RAG vs
   parametric neither dominates.

**Counter-case, stated honestly:** semantic dementia's graceful, damageable degradation proves a
genuine, stable, distributed cortical STORE exists. Context modulates access to it; it does not
manufacture it. And the working computational model of the hub (Jackson et al. 2021) IS a
gradient-trained recurrent network — so "the brain is not a trained encoder" must not be
over-read into "training is never the right tool." The correct reading is narrower and sharper:
**training is not where the near-neighbour distinction comes from. Explicit relational/distinctive
structure is.**

---

## PART 2 — PER-COMPONENT COMPARISON (SHAPE / POSITION / METRIC)

Read at HEAD `7b4d8654f`, `.venv` interpreter, files as listed. Triple-check disclosures at end.

| # | Brain element | SHAPE (brain -> ours) | POSITION (brain -> ours) | METRIC, judged on the BRAIN'S metric | GAP |
|---|---|---|---|---|---|
| E1 | **Distinctive-feature privileging** (Cree/McRae; Tyler & Moss CSA) | Graded weights; rare features weighted UP | Intrinsic to the hub code | Brain's metric: can it tell coordinates apart? SD says this is the FIRST thing that breaks | **`_concept_vector_from` bundles feature vectors UNWEIGHTED** (`hdlab/lexical_similarity.py:542-546`); `bundle()` is a plain sum + per-component magnitude renorm (`hdlab/bundling.py:34-39`). A tag in 8 concepts counts exactly as one in 1. **Precise INVERSE of the brain's privileging.** LOAD-BEARING #1 |
| E2 | **Feature SUPPLY for open vocabulary** | Lifetime multimodal + linguistic experience, ~65 experiential dims + language-derived channel | Continuous, always-on | Coverage of the vocabulary actually encountered | **~230 hand-typed concepts** (`CONCEPT_FEATURES`, incl. a mechanically KB-generated ProPara block). Everything else -> Lancaster/Brysbaert sensorimotor, which **provably cannot separate synonyms from siblings** (module's own measured numbers). LOAD-BEARING #2 |
| E3 | **Dual coding: sensorimotor AND language-derived** (Wang/Bi 2020; Bi 2021; Xu 2025) | Two complementary channels | Both feed the hub | Xu 2025: text-only recovers non-sensorimotor, fails sensorimotor | Our OOV fallback has the **sensorimotor channel ONLY** — precisely the half that Xu 2025 shows is NOT the one language gives you, and that our own numbers show collapses siblings. No language-derived channel is wired into `concept_similarity` |
| E4 | **Semantic control gain** (IFG/pMTG; Chiou 2018) | Task-conditioned up-weighting of the relevant dimension | Acts ON the hub, conditioned by task | SA/SD dissociation: weak-target-beats-strong-competitor | `concept_similarity(a, b)` is a **bare 2-arg pure function** — no task/context port exists for gain to act through. The brain never computes context-free word-word similarity. POSITION gap |
| E5 | **Hub = deep recurrent pattern completion** (Jackson 2021; Rogers 2021 eLife) | Nonlinear, recurrent, dynamic | Deep, multi-layer | Cross-modal generalisation | Ours is a **single linear bundle + one cosine**. No recurrence, no completion, no depth. Note: we DO own CA3-style completion (`cleanup_family.iterative_attractor`) and DG separation (`dg_pattern_separation.py`) — **built, but not in this path** |
| E6 | **Code format: dense, graded, low effective dim** | ~4-12 effective dims, dense | Hub | — | Ours: 8192-dim FHRR bundle of **2-5 binary tags**. Neither dense-graded nor brain-sparse; a near-orthogonal sparse-set code. Mismatch is real but I rank it BELOW E1-E3 (it is a consequence of E2's supply thinness, not an independent defect) |
| E7 | **Acquisition = fast index + slow offline consolidation** (CLS) | Hippocampal index, then replay | Two systems | Lexical competition emerges only after sleep | `CONCEPT_FEATURES` is a **static hand-authored dict** — no ingestion, no consolidation. We DO own `hippocampal_encoder.py` (DG->CA3->CLS replay), unwired to this path |
| E8 | **Trained encoder** | NOT the near-neighbour mechanism (§1.6) | — | — | `encoder_retrain_persist.py` is correctly **OPT-IN and unwired by default** — and per §1.6 that is the BRAIN-CORRECT default, not a shortfall. See §3.2 |

**Owned organs that a build MUST reuse rather than duplicate** (standing rule: a mechanism sharing
an already-built process reuses that organ):
- `hdlab/low_information_filter.py` — **already a distinctiveness/informativeness measure**: PMI of
  a candidate against subjects, with the floor READ OFF the closed-class lexicon (measured on
  32,955 sentences: closed-class reference PMI p50=0.96 / p75=2.10 / p90=3.33). It is currently a
  binary GATE on grounding objects, not a graded WEIGHT in the similarity computation. **This is
  the organ E1 should reuse.**
- `hdlab/definitional_extraction.py` — extracts `definiendum` + `definiens` + genus `head`. A
  definition is genus + **differentia**, and the differentia IS the distinctive feature. Directly
  serves E2/E3 as a **language-derived** feature channel.
- `hdlab/hd_fact_store.py` (relational (s,r,o) + `_sr_key` content-hash index),
  `hdlab/cleanup_family.py`, `hdlab/dg_pattern_separation.py`, `hdlab/hippocampal_encoder.py`,
  `hdlab/coreference_resolver.py`.

**DEAD, correctly excluded:** `hdlab/concept_encoder.py` — grep-confirmed **zero live importers**
(the only hdlab hits are a docstring cross-reference in `temporal_trace.py:30` and a comment in
`late_combine.py:18`). Not generalised from, per instruction.

---

## PART 3 — THE BUILD TARGET

### 3.1 Ranking the gaps

Ranked by (a) load-bearing for synonym-vs-sibling, (b) do we already own an organ:

1. **E1 distinctive-feature weighting** — maximally load-bearing (it IS the brain's mechanism per
   §1.5a-b), and we own the measure (`low_information_filter` PMI). SHAPE fix, no re-plumbing.
2. **E2/E3 language-derived feature supply** — equally load-bearing but larger; we own
   `definitional_extraction`. Coupled to E1: weighting is worthless without features to weight.
3. **E4 control gain** — real and brain-correct, but **blocked**: a bare word-pair similarity call
   has no task context to condition on. Requires adding a context port to the API first.
4. **E5/E6/E7** — real, but downstream of 1-3.

### 3.2 Weighing the USER's hypothesis (trained solutions were INFERIOR)

**The evidence supports it, and I verified it on disk rather than trusting recollection.**

- Literature: GloVe 0.41 -> counter-fitted 0.58 -> 0.74 (§1.5f). Levy et al. 2015: matched
  hyperparameters erase the trained-vs-count advantage. Acquisition is indexing, not gradient
  descent (§1.6).
- **Our own disk, verified this drill**: `data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json`
  = **HARD_FAIL**, `"ARM_CONCEPT_ENCODER recall@5_mean=0.1600 < max(baseline)=0.2800"` — the
  trained competitive-Hebbian concept encoder LOST to a **char-trigram surface encoder** on WordNet
  synonym retrieval (delta -0.120). That is the USER's recollection, confirmed, on the synonym task
  specifically.
- **Deflating my own read**: `encoder_retrain_persist` is genuinely certified (metrics.json
  HARD_PASS, 3 seeds, reload deviation 0.0) — for **entity-addressed** comprehension, a different
  capability. "Trained was inferior" is licensed for **lexical near-neighbour separation**; it is
  NOT licensed as a general claim, and the hub's own working computational model IS gradient-
  trained (§1.6). Do not over-read.

### 3.3 THE ONE BUILD TARGET — can-fail experiment

**`exp_distinctiveness_weighted_lexical_similarity_v1`**

**Mechanism (brain-faithful, zero training, glass-box, deterministic):** weight each feature vector
by its **distinctiveness** before bundling — reusing `low_information_filter`'s existing PMI
informativeness measure rather than inventing a new IDF. One change at
`lexical_similarity._concept_vector_from`. This duplicates Cree/McRae distinctive-feature
privileging and Tyler & Moss's low-redundancy criterion directly.

**MEASURED:** Spearman rho against **SimLex-999** — the public benchmark purpose-built for exactly
this synonym-vs-sibling distinction (it exists BECAUSE distributional models conflate them),
restricted to covered pairs, **with coverage reported openly, not hidden**.

**Why SimLex and not our own lexicon — this is the trap and it must be pre-registered:**
`CONCEPT_FEATURES` is CONSTRUCTED so synonyms share nearly all tags and siblings share only the
domain tag (the file's own documented convention, lines 78-82). Distinctiveness weighting is
**near-guaranteed to "win" on it** — a construction-determined result, exactly the failure the
project's own discipline warns about. **Any HARD-PASS measured on the hand lexicon is VOID.**

**Controls (ALL required — per the layered-self-correcting-controls discipline):**
1. **Grounded floor**: `grounded_similarity` raw cosine on the same pair subset (our current live
   OOV mechanism).
2. **Uniform-weight control** — THE one-variable isolation: identical feature supply, distinctive-
   ness weights set uniform. If uniform ~= weighted, the SHAPE hypothesis is dead.
3. **Scramble control**: permute word -> feature-set assignment; must collapse.
4. **Public calibration** (reference, not a bar): GloVe 0.41 / counter-fitted 0.58 / human IAA 0.67.

**HARD-PASS (all four):** weighted rho >= 0.35 on covered pairs; (weighted - uniform) >= +0.08;
(weighted - grounded floor) >= +0.15; scramble <= 0.05.

**HARD-FAIL (either):** (weighted - uniform) < +0.03 — distinctiveness is NOT the lever; the SHAPE
hypothesis is refuted and the next drill goes to E4 control-gain or the episodic/situational
discriminator. OR: coverage < 20% of SimLex pairs — the wall is **supply (E2), not metric (E1)**,
which redirects the build to `definitional_extraction` differentia harvesting.

**Note the HARD-FAIL is a genuinely useful outcome either way**: it cleanly partitions "our metric
shape is wrong" from "our feature supply is empty," which we currently cannot distinguish.

**P_deflated = 0.45.** Raw ~0.70 given the strength of the counter-fitting precedent and the
distinctive-feature literature; deflated 0.20 per the lit-scan calibration penalty (novel synthesis
onto our FHRR bundle, no direct precedent for this exact composition), capped below the 0.50
novel-synthesis ceiling. The dominant risk is **coverage**, not mechanism.

---

## CROSS-THREAD SYNTHESIS

- **2026-08-12 read-out brain-fidelity audit** (`notes/brain_fidelity_audit_readout_2026-08-13.md`)
  found `canonicalize_fast` uses cosine-of-bag-of-content-words for BOTH propose and verify, so
  verification is not independent. **This drill finds the same disease one layer down**: the
  comparator itself is an unweighted-overlap similarity proxy sitting where the brain applies
  distinctiveness privileging + control gain. Same root cause, two sites.
- **65.7% tautological grounding** (`notes/landed_vet_foundation_validation_2026-08-12.md`):
  consistent with E2 — a feature supply that is mostly self-reference cannot carry distinctive
  features.
- **GAP == GROUNDING** (USER 08-12): a distinctive feature is precisely the shortest RELATIONAL
  BRIDGE that separates a new concept from its nearest grounded neighbour. E1 and the gap metric
  are the same quantity measured from two directions.
- **Sensorimotor-collapse finding is publishable-grade evidence we own** and the norms literature
  lacks (§1.4). Do not lose it.

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Do not train a bigger encoder for this.** Both the literature (0.41 -> 0.74 by constraint
   injection, not training) and our own HARD_FAIL disk evidence say the lever is explicit
   distinctive/relational structure. `encoder_retrain_persist` staying opt-in is brain-CORRECT.
2. **The near-neighbour failure is a product risk, not a benchmark curiosity.** A knowledge
   substrate that merges couch with chair merges customer records, part numbers, and drug names.
   SD tells us this is the FIRST failure mode of any degrading semantic store — it is the canary.
3. **`GROUNDED_CAP = 0.45` is the right engineering call and should stay** until E1/E2 land. It is
   an honest structural refusal to assert identity on evidence that provably cannot support it.
4. **`low_information_filter` is under-deployed.** It already computes the brain's distinctiveness
   quantity, but only as a binary gate on one path. Promoting it to a graded weight in the
   comparator is reuse, not new build.

## TRIPLE-CHECK DISCLOSURES

Checked before asserting any gap: **right file** (paths as cited, read in full or by line range);
**right version** (HEAD `7b4d8654f`; `lexical_similarity.py` last touched `01093ac1f`,
`grounded_similarity.py` `584a69eb5`); **right environment** (`.venv/Scripts/python.exe` for all
reads of metrics.json); **right metric** (encoder comparison read from `verdict_msg` recall@5, not
from a summary note); **right arm** (`ARM_CONCEPT_ENCODER` vs `ct`=char-trigram / `cp` baselines,
named explicitly in the verdict string).

**Honest limits of this drill:**
- I did NOT run `concept_similarity` to confirm the unweighted-overlap claim empirically. It is
  derived ANALYTICALLY from `_concept_vector_from` (line 545: `torch.stack([feature_vecs[t] for t
  in sorted(features)])`, no weights) plus `bundle()` (plain sum, magnitude renorm). Stated as an
  analytic reading of code, not a measurement, per the no-experiments constraint.
- `lexical_similarity.py` is 757 lines; I read lines 1-483 and 515-640 in full. The unread span
  484-515 is continuation of the same auto-generated ProPara `CONCEPT_FEATURES` block; no function
  definitions exist there (`grep -n "^def "` confirms first def is line 521).
- Section 1.5(d) hippocampal semantic pattern separation and 1.5(e) synonym representation are
  flagged SINGLE-STUDY / UNTESTED and are deliberately NOT load-bearing for the build target.
- No tool call was denied during this drill.

## CITATIONS (verified count)

**~52 distinct sources** surfaced across 5 parallel lit-scans (~176 tool-uses). Of these, **41 are
cited above with author + year + venue**; every quantitative claim in Parts 1 and 3 traces to a
named paper or to a disk-verified file in this repo. Two claims are explicitly flagged as
NOT independently verified by the scanning agent: the Fernandino "5-dimensional experiential space"
figure (could not be confirmed; the confirmable Binder/Fernandino claim is the 65-attribute model)
and the *Cerebral Cortex* 2022 semantic-dimension-orienting study (paywalled, title-level only).
Neither is load-bearing.
