# DESIGN -- the cross-modal referent hub with a PURE-VISUAL (DINOv2) spoke (2026-09-10)

The referent-grounding DATA build (item 1 of PLAN_referent_grounding_data_build). Adds a REAL, non-text
visual referent modality at vocabulary scale and tests, brain-foundationally, whether real referent grounding
lifts meaning-identity where text-derived signals could not. Design is grounded in four literature drills run
2026-09-10 (findings summarized inline with citations). Scope unchanged: write only experiments/, verification/,
this problem folder + own data dir; NO hdlab writes (Q111); NO external model at runtime (frozen foundation
transducer at INGEST only); every load-bearing claim gets an info-free twin LOSING + a CI.

## THE FOUR RESEARCH PILLARS (what "right, not easy" means here)

R1 -- THE HUB IS A CORRELATED SHARED SUBSPACE, NOT CONCATENATION (ATL hub-and-spoke).
  The ATL hub is a learned shared latent whose geometry tracks the CROSS-MODAL FEATURE-CORRELATION (covariance)
  structure of features pooled across modalities -- not lexical co-occurrence (Patterson-Nestor-Rogers 2007;
  Lambon Ralph-Jefferies-Patterson-Rogers 2017; Rogers-McClelland 2004; Chen-Lambon Ralph-Rogers 2017 NHB;
  Rogers-Cox et al. 2021 eLife). Cox-Rogers 2024 operationalizes hub similarity as: pooled cross-modal feature
  matrix X (concepts x features) -> column mean-center -> cosine of centered rows = the hub RSM; SVD of centered
  X gives the low-D amodal coordinates. Naive concatenation is specifically ruled out by the semantic-dementia
  double-dissociation + feature-integration-deficit data (Hoffman-Evans-Lambon Ralph 2014). Fusion is two-stage:
  (A) learn the shared correlated subspace offline; (B) per-concept PRECISION-WEIGHTED combination online
  (Ma-Beck-Latham-Pouget 2006; Ernst-Banks 2002): weight each spoke by inverse-variance reliability.

R2 -- USE DINOv2, NOT CLIP, AS THE VISUAL SPOKE (the crux "right not easy" call).
  CLIP's image embeddings are trained to match CAPTIONS, so a CLIP-visual spoke would largely RE-MEASURE text --
  the redundancy trap that killed the componential lever (W33). DINOv2 is vision-only (zero caption exposure),
  a defensible ventral-stream/IT stand-in (goal-driven-DNN paradigm: Yamins-DiCarlo 2014; self-supervised parity:
  Konkle-Alvarez 2022; at matched scale DINOv2 matches/beats CLIP on ventral-stream predictivity without the
  language tether: Raugel et al. 2024/25; Conwell et al. 2024 -- diet matters more than the language objective).
  It is engineered to be used FROZEN -> matches our "foundation asset, called once at ingest" invariant.
  CLIP-visual is retained ONLY as a diagnostic "text-shadow upper bound" arm (never a trusted second spoke).

R3 -- THINGS IS THE IMAGE SOURCE; PHOTOS OVER SKETCHES; + AN INDEPENDENT GOLD.
  THINGS (Hebart et al. 2019 PLoS ONE; THINGS-data Hebart et al. 2023 eLife): 1854 concrete object concepts,
  curated natural single-object photos, one folder/concept. We use the CC0 subset (unrestricted, ~1 curated
  photo/concept). Natural photos beat sketches for a photo-trained DINOv2 (and developmentally: realistic
  pictures ground word-object reference better -- Ganea-Pickard-DeLoache 2008; Markman whole-object; Landau-Smith-
  Jones shape-bias supports multi-exemplar averaging). BONUS: THINGS-behavior (4.7M human odd-one-out triplets +
  a 66-dim behavioral embedding over the same 1854 concepts) is a GENUINE INDEPENDENT similarity gold (human
  perceptual judgments, no text, no SimLex) -- see the coverage pivot below.

R4 -- PRECISION GATE = LANCASTER Visual.mean (not concreteness, not imageability).
  Modality-specific perceptual strength beats both concreteness (conflates vision+touch) and imageability (an
  uncontrolled vision proxy) at predicting lexical processing -- the "strongest-sense hypothesis" (Connell-Lynott
  2012); attribute-strength predicts real fMRI signal for concrete words but CHANCE for abstract (Fernandino et
  al. 2015) -- exactly the reliability signature a precision weight should exploit. On disk: Lancaster
  Visual.mean (0..5 -> /5), join by lowercased word.

## THE SPOKES (all vocabulary-scale)
- TEXT spoke: SEQ (parser-free directional PPMI) -- the thematic/verbal channel (existing, grown by reading).
- SENSORIMOTOR spoke: grounded (Lancaster 11-dim perceptual/action strengths) -- existing perceptual-referent spoke.
- VISUAL REFERENT spoke (NEW): DINOv2 embedding of THINGS photo(s), per concept -> the pure, non-text object code.
- DIAGNOSTIC only: CLIP-visual (text-shadow upper-bound arm, R2).

## THE HUB COMPUTATION (Cox-Rogers correlated subspace + Ma-Pouget precision)
Stage A (offline, foundation): pool the per-concept spoke features into X; column mean-center; the hub RSM is the
  cosine of centered rows; SVD(X_centered) -> amodal hub coordinates (variance-retained rank r). This is the
  feature-CORRELATION geometry, not co-occurrence.
Stage B (per concept, online fusion): reliability-weighted combination h(c) = sum_m pi_m(c) P_m(f_m(c)) / sum_m
  pi_m(c); pi_visual(c) = Lancaster Visual.mean(c) (down-weights the visual spoke where the referent is not
  visual); pi_text, pi_grounded from earned gain / uniform as in the existing convergent-cue fusion. similarity =
  cosine(h(c1), h(c2)). Compared head-to-head against FLAT CONCATENATION (the R1 falsifier).

## COVERAGE FINDING + THE POWERED-TEST PIVOT (measured on disk 2026-09-10)
Of 1349 pooled high-sim SimLex+SimVerb pairs, only 23 (19 SimLex, 4 SimVerb) have BOTH words as THINGS concepts
-> the visual spoke can bite on only ~23 pairs: UNDERPOWERED on the SimLex/SimVerb headline gold. Moreover the
covered pairs are mostly CO-HYPONYMS (cat/lion, bird/hawk, rat/mouse) where visual similarity may HURT synonymy.
INTERPRETATION (a real result): the SimLex synonym-identity residual is dominated by abstract/relational/verb
pairs that NO visual referent data can ground -> for the SimLex gold specifically, the visual lever is
structurally data-bound (confirms the PLAN's data-ceiling hypothesis on that gold).
THE STRONGER TEST (test it before concluding, per discipline): THINGS-behavior -- human perceptual similarity
over all 1854 concepts, where visual coverage is 100% and power is ample. This is where the visual-referent
contribution is actually MEASURABLE. We run BOTH and report both honestly.

## DECISIVE GATES (pre-registered; twin-controlled)
G1 (R2 non-redundancy): RSA/CKA(DINOv2, text-spoke) is measurably LOWER than RSA(CLIP-visual, text-spoke), AND
   DINOv2 adds unique variance over text -> confirms we measure real visual grounding, not a text shadow.
G2 (core, powered, THINGS-behavior gold): does the DINOv2 visual spoke, fused via the hub, lift prediction of
   human perceptual similarity over text+grounded, with the KNOWLEDGE-SHUFFLED (shuffled-visual-rows) twin
   LOSING, CI-separated? (r vs human 66-dim embedding / triplet-consistent similarity.)
G3 (R1 fusion form): reliability-weighted precision fusion beats FLAT CONCATENATION (mechanism check).
G4 (headline gold, honest): on the 23-pair SimLex/SimVerb visual-covered subset -- report the number and its
   (wide) CI; do not over-claim. This is the coverage-limited headline result.
A CI-separated G2 with twin losing = the visual referent lever is REAL (on the concrete-object slice), and the
path is scale the coverage. A null G2 = the pure-visual referent adds nothing over text+grounded even where fully
measurable -> the definitive close of the data-ceiling question for this modality.

## BF STATUS
Every rung stays BF/BF_SPIRIT: DINOv2 = frozen foundation transducer at ingest (ventral-stream/IT stand-in,
vision-only), analogous to Lancaster/Brysbaert curated norms; hub = Cox-Rogers correlated subspace + Ma-Pouget
precision (PINNED computations); precision gate = Lancaster Visual.mean (curated norm); cosine readout
(Georgopoulos). NO external model at runtime. THINGS/THINGS-behavior = curated foundation assets, non-circular
w.r.t. SimLex (human perceptual/image data, not text).

## TLDR
The brain builds word meaning by blending what a thing looks/feels/sounds like into one shared code, trusting
each sense more for words it fits (sight for "apple", not for "justice"). We are adding a real "what it looks
like" signal from photographs, read once by a vision-only AI (DINOv2 -- deliberately NOT CLIP, because CLIP
secretly learned from captions and would just echo the text we already have). We found that our word-pair answer
key only overlaps our photo database on ~23 pairs -- too few to test there -- so we will run the real test on a
large set of human "which two look most alike" judgments over ~1850 everyday objects, where the picture signal
can actually be measured, and report the small answer-key result honestly alongside it.

## QUESTIONS
None -- proceeding under "make it happen" authorization; the SimLex-underpowered -> THINGS-behavior pivot is a
full-auto design call, reported for visibility not decision.

## NEXT STEPS
STEP A: download THINGS CC0 photos + THINGS-behavior gold; DINOv2-embed -> per-concept visual referent vectors.
STEP B: build the hub (correlated subspace + Visual.mean-precision fusion) vs flat-concatenation control.
STEP C: run gates G1-G4 twin-controlled; add cell(s) to the witness; update SOLVED.md (ASCII, ledger-clean).
