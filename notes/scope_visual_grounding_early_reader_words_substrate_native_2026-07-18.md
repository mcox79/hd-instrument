# Scope: substrate-native visual grounding of concrete early-reader words

Date: 2026-07-18
Type: SCOPING + SOURCING drill (USER-elevated). Research/scoping only -- NO cell dispatch.
Calibration: novel-synthesis P capped 0.50; lit-scan deflation 0.15-0.25 applied.
Concept-query run first: top prior hits = research_drill_substrate_cross_modal_2x_2026-06-09
(cosine 0.34) + research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04. This note
BUILDS ON those two (credited throughout), does not re-derive them.

Prior arc work on this concept: YES -- cross-modal VSA drill (06-09) already cataloged the
vision precedents and ran the P-table; resonator-capacity drill (06-04) already bounded scene
factorization K_max. New here = (a) narrow the scope to EARLY-READER single-object images,
(b) the coherence-of-two-groundings question (perceptual vs relational/dictionary of the SAME
word), (c) license-checked staged data, (d) a design-gated minimal first cell.

---

## TOP-LINE

Images are the RIGHT grounding for concrete early vocab, and most of the machinery is already
ours. The DESCRIPTION/scene layer is substrate-native and validated: image = SUM(object BIND
location/attribute), queried by unbind + cleanup + resonator (Frady/Kent/Olshausen/Sommer 2020;
Renner et al. 2024). The ONLY open piece is the perceptual FRONT-END (pixels -> bindable object
features), and early-reader images are the easiest possible case: one clear object, the printed
word as a free label. The recommended front-end is a small PRETRAINED CLIP-class encoder used as
INGEST SCAFFOLDING (glass-box invariant preserved: encode at read time, runtime reasoning stays
glass) -- because a shared image+text space makes "cat"-text land near cat-images for FREE
supervised grounding, and our own cross-modal drill already put P(CLIP->FHRR recall@1>0.8) at
0.60. The genuinely novel, foundation-relevant question is NOT "can we encode an image" (low
risk, well-precedented) but "does the perceptual grounding of a word COHERE with its relational
(dictionary) grounding" -- that is our multimodal-concept build and is where a real, can-fail
first cell earns its keep. Clean data exists (Quick, Draw! CC-BY 4.0, staged). Honest risk:
QuickDraw sketches embed weakly vs photos, so perceptual quality is MEDIOCRE-to-GOOD not ceiling;
a photo upgrade (Open Images CC-BY / Wikimedia PD) is staged as the strengthening path.

---

## 1. APPROACH SCOPE (substrate-native lead; prior work credited + built on)

### 1a. What is already OURS (glass-box primitives, validated)
The scene/description layer needs NO new invention:
- SCENE AS BINDING: scene = SUM_i (location_i BIND object_i [BIND attribute_i]). A composite
  hypervector holding K bound pairs. This is Kanerva/Gayler/Plate VSA + Eliasmith SPA, and it is
  exactly our additive_map / bundle machinery.
- FACTOR IT BACK OUT: RESONATOR NETWORKS (Frady, Kent, Olshausen, Sommer 2020, Neural Computation)
  recover object x pose x location from a scene vector by iterated unbind + codebook cleanup.
  Renner et al. 2024 (Nature Machine Intelligence, Loihi K=3 hw / K=6 sim at N=16384) confirms
  M_max ~ N^2 and hardware viability. "Fuzzy but mostly accurate" degradation with scene
  complexity IS our crosstalk/capacity theory.
- CAPACITY IS ALREADY BOUNDED (our 06-04 drill): dense resonator K_max ~ 7-9 factors at N=4096;
  sparse (f=0.05) extends to K~20-30 (Cunningham et al. 2024, K=26 letters at N=5000);
  position-bound ~ sqrt(N). For EARLY-READER images this is the easy regime: usually ONE object
  per picture (K=1) -> trivially inside capacity. The capacity question that actually bites here
  is at the CONCEPT level (how many senses/modalities can superpose in one word-concept vector),
  not scene complexity -- see 1c.

Maturity for SIMPLE single-object images: MATURE for classification/factoring; the scene-rep
math is settled. What is NOT settled = grounding it to a relational KB (our foundation-build).

### 1b. FRONT-END options (pixels -> bindable features) -- honest maturity + effort
(a) PRETRAINED CLIP-CLASS ENCODER as ingest scaffolding  [RECOMMENDED]
    - Small open model (OpenCLIP ViT-B/32, ~150M params, CPU/laptop-scale -- the same
      "laptop-scale encoder as scaffolding" logic we accepted for Whisper on the audio side).
    - Shared image+text space: image_emb and text_emb of "cat" are already near each other, so
      grounding the word atom to the picture is a FREE supervised pairing (no training).
    - Project 512-d CLIP emb -> N-d FHRR via fixed random complex projection (zero training) or a
      small learned MLP (NVSA path). Reuses text-substrate plumbing entirely.
    - Precedent (strong): NVSA (Hersche et al., NMI 2023, 87.7% RAVEN) validates DNN-emb->FHRR at
      scale; geometric-world-model FHRR (2026); our own drill P(CLIP->FHRR recall@1>0.8)=0.60.
    - Maturity HIGH, effort LOW. Risk: frozen encoder quality on sketches (mediocre); shared
      space is CLIP's, not ours (fine -- it is scaffolding, discarded from the runtime path).
(b) HDC-NATIVE perceptual encoding (patch/feature hypervectors)  [SECOND ARM, more native]
    - Thermometer/level-encode pixels, BIND to position, BUNDLE (classic HDC image pipeline,
      Rahimi/Rabaey lineage; MNIST-class ~90%+ demonstrated). Fully glass-box, no external model.
    - BUT it yields an encoder, NOT a shared text-image space -- grounding to the word atom still
      needs a learned bridge (paired word<->image supervision). So it does not get grounding "for
      free" the way CLIP does.
    - Maturity MEDIUM for simple bitmaps, effort MEDIUM-HIGH for grounding. Honest: attractive
      long-game (native front-end, Frontier-2), weaker for the FIRST decisive test.
    - Recommendation: use (a) to get grounding working + the coherence result FIRST; hold (b) as
      the substrate-native replacement once the target metric is established (optimize-then-
      nativize discipline). Do NOT over-claim we can do a native visual front-end now.

### 1c. HOW it grounds into the substrate (the multimodal concept)
For word w:
  perceptual vector  p_w = Proj_FHRR( mean CLIP-image-emb over M exemplars of w )   [scaffolded]
  relational vector  r_w = existing dictionary/WordNet substrate vector for w        [ours]
A multimodal CONCEPT is either (i) a superposition  concept_w = bundle(r_w, p_w[, sense_i...]),
or (ii) a fact  word_atom BIND p_w  stored alongside  word_atom BIND r_w. Capacity: (i) is a
K-way superposition -> our C_FHRR / K-capacity chain-grade math bounds how many groundings/senses
coexist before crosstalk (this is the concept-level capacity question, distinct from scene K).
This directly connects visual grounding to the additive-map reasoning core we are already
improving -- perceptual grounding is one more constraint the readout can bring to bear
(reasoning-theory anchor: resolution scales with # constraints).

### 1d. Genuine literature GAP (honest)
- WELL-COVERED: image->embedding->FHRR projection; scene-as-binding; resonator factoring;
  HDC image classification. Low novelty, low risk.
- GAP (ours to fill): binding a perceptual grounding to a RELATIONAL/dictionary grounding of the
  SAME word to form an inspectable multimodal concept, and measuring whether the two grounding
  SOURCES cohere. NVSA is closed synthetic (no relational KB); CLIP has no glass-box KB. This is
  a foundation-build question, not answered off the shelf. P(coherence signal above shuffled +
  dictionary-only controls) = 0.50 (novel-synthesis cap; genuinely unknown whether sketch-CLIP
  grounding carries enough signal to beat the relational-only baseline).

---

## 2. DATA (staged, license-checked, OPEN/PD only)
Staged at: data/corpora/word_image_early_vocab/ (PROVENANCE.md + MANIFEST.json). Lightweight:
license-cleared fetch manifest, raw bitmaps pulled by the cell at ingest (kept the stage light).

- PRIMARY: Google Quick, Draw!  -- CC-BY 4.0 (CLEAN). 28x28 grayscale .npy per category, one
  clear object each, category = the word (free label). 22+ categories confirmed overlapping the
  McGuffey primer vocab (cat, dog, hat, fan, ball, sun, duck, bird, fish, tree, star, moon,
  apple, hand, book, key, cup, house, car, horse, pig). Caveat: abstract sketches -> weaker CLIP
  grounding than photos.
- PHOTO UPGRADE (staged, optional): Open Images V7 (images CC-BY 2.0 per-image, labels CC-BY 4.0)
  and Wikimedia Commons category harvest (PD/CC0/CC-BY per file). Cleaner grounding, more license
  bookkeeping. Fall-back for McGuffey nouns absent from QuickDraw (rat, cap, hen, nest, egg).
- McGUFFEY ILLUSTRATIONS: period-accurate to the exact lesson words but EXTRACTION-BLOCKED. PG
  #14640/#14642 (already staged as text) hold illustrations only as `[Illustration: <caption>]`
  TEXT placeholders -- no image files. Original engravings are PD but only as un-segmented page
  scans (Internet Archive). Flagged, not first-cell path. The captions ARE usable now (free
  word<->scene-description text pairs, extractable from the staged clean text).
- DELIBERATELY NOT STAGED: CIFAR-10 / COCO / Tiny-ImageNet -- permissive top license but murky
  underlying per-image (Google/Flickr scrape) licenses. Documented as a license hazard.

---

## 3. RECOMMENDED MINIMAL FIRST CELL

Name: PERCEPTUAL-RELATIONAL COHERENCE (glass-box visual grounding, single-object)
Smallest decisive test: does a PICTURE recover the RIGHT WORD in the substrate, above a shuffled
control and chance -- and does that perceptual grounding COHERE with the word's relational
(dictionary) grounding rather than just re-encoding it?

Setup (~20-30 concrete nouns present in BOTH QuickDraw AND our WordNet/dictionary substrate):
- Ingest (scaffolded): p_w = Proj_FHRR(mean CLIP-image-emb over 200 QuickDraw exemplars of w).
- Relational (ours): r_w = existing dictionary/WordNet substrate vector for w.
- CLIP-text bridge: t_w = Proj_FHRR(CLIP-text-emb("<w>")) as the word anchor in the shared space.

Arms / tests:
- T1 PERCEPTUAL RECOVERY: given held-out picture -> p_query, cleanup against {t_w} codebook ->
  recover the word atom. Metric: top-1 word accuracy over confusable set.
- T2 COHERENCE (the novel one): correlate the perceptual pairwise-similarity matrix (over p_w)
  with the relational one (over r_w). Do cat-dog / sun-moon / duck-bird come out close in BOTH?
  Metric: Spearman rho of the two similarity matrices.
- T3 SCENE-REP (exercises our primitives): scene = BIND(loc1,obj_cat)+BIND(loc2,obj_hat); unbind
  by loc -> cleanup against grounded object codebook -> recover cat/hat. Metric: 2-object recovery.

Design-gate (per the design-gate-before-full-run discipline):
- REAL baselines, not strawmen: (i) CHANCE = 1/|vocab|; (ii) SHUFFLED-GROUNDING control
  (permute p_w across words -> T1/T2 MUST collapse to chance -- guards saturation/telemetry);
  (iii) DICTIONARY-ONLY baseline (does relational structure alone already predict the coherence
  target? -- this is the load-bearing control: perceptual grounding must ADD signal, not merely
  re-encode dictionary co-occurrence, else it is redundant).
- CAN-FAIL: poor CLIP-on-sketch projection -> T1 ~ chance -> HARD_FAIL (real, not by-construction).
  If shuffled control passes, discriminator is saturated -> redesign. If dictionary-only baseline
  already saturates T2, the coherence metric is not measuring perceptual grounding -> redesign
  (use cross-space RETRIEVAL, picture->word, which dictionary-only cannot do, as the tiebreak).
- DIFFICULTY ON: force within-category discrimination via confusable pairs (cat/dog, cat/horse,
  hat/cup, ball/apple, sun/moon, duck/bird) -- no frac=0 easy set; recovery must separate visually
  and semantically near neighbors, not just far ones.
- ONE VARIABLE: first cell = arm (a) CLIP-scaffold only vs the three controls. Hold arm (b)
  HDC-native encoder as the SECOND cell (optimize-then-nativize), so the encoder is not confounded
  with the grounding question in the first run.
- Brain-check the design (mandatory-on-negative, pre-registered): concrete-noun visual grounding
  is exactly how children bootstrap early vocab (fast-mapping picture<->word); if T1/T2 fail, first
  ask whether the brain grounds THESE words perceptually at all (concrete nouns: yes -> a failure
  is an implementation/encoder bug, not a structural bound) before accepting the negative.

Scale/cost: CPU/laptop, ~1-2 hr. Smoke at full vocab (30 words, N=1024/4096) -- discriminator
must move under perturbation before any full claim. No cloud spend.

Why this cell and not "encode an image" (which is low-risk precedented): it targets the GAP
(perceptual+relational coherence = the multimodal-concept build) with a design that CAN fail
informatively and a control (dictionary-only) that prevents a construction-determined pass.

---

## Citations (built on, credited -- learn-from + build-on)
- Frady, Kent, Olshausen, Sommer (2020). Resonator Networks 1 & 2. Neural Computation 32(12).
- Renner, Supic, Strock et al. (2024). Neuromorphic Visual Scene Understanding with Resonator
  Networks. Nature Machine Intelligence. arXiv:2208.12880.
- Cunningham et al. (2024). Compositional Factorization of Visual Scenes with Convolutional Sparse
  Coding and Resonator Networks. arXiv:2404.19126.
- Hersche et al. (2023). A neuro-vector-symbolic architecture for solving Raven's progressive
  matrices. Nature Machine Intelligence. (DNN-emb -> FHRR at scale.)
- Eliasmith et al. (2013). How to Build a Brain (SPA / Spaun perceptual->pointer).
- Kanerva; Gayler; Plate -- VSA scene-as-binding foundations.
- Rahimi/Rabaey lineage -- HDC image classification (native front-end precedent).
- Google Quick, Draw! Dataset (CC-BY 4.0). Open Images V7 (CC-BY). Project Gutenberg #14640/#14642.
- Prior in-house: notes/research_drill_substrate_cross_modal_2x_2026-06-09.md;
  notes/research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md.
