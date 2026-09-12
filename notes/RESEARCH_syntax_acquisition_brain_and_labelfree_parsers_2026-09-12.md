# RESEARCH — how the brain acquires/computes syntactic structure, and which label-free models replicate it (2026-09-12)

Research drill dispatched by strategy (Opus agent, 58 web/literature lookups) after the owner asked "have you tried all the high
potential fixes? research how the brain does it and replicate as closely as you can". Kept verbatim in substance; numbers cited.

## 1. The acquisition SIGNAL — what has quantitative support for STRUCTURE
- **Distributional frames (Mintz 2003, Cognition 90)** give categories, not structure: the 45 most frequent `a_x_b` frames classify
  the middle word at 0.98 token / 0.93 type accuracy but 0.08–0.10 type completeness — high precision, near-zero coverage. That is
  the profile of our four hand-written item-based constructions (large gain, narrow reach) → lexically anchored frames, not
  category n-grams.
- **Prosodic bootstrapping (Pate & Goldwater, TACL 2013):** word duration in a lexicalised DMV beats words-only baselines and is the
  first DMV result to beat uniform branching without POS or punctuation; gains mostly on constituency. Text has no duration —
  punctuation is the only proxy, and a much stronger one than we use (§3).
- **Semantic bootstrapping (Abend, Kwiatkowski, Smith, Goldwater & Steedman 2017, Cognition 164):** CCG learned from 5,831 Eve
  utterances + logical forms learns SVO order, pre-nominal determiners and prepositions with no head-direction parameter, but
  reports no UAS → meaning teaches ORDER/DIRECTION parameters, not arcs (matches our probe v21 negative).
- **Prediction error (Elman; Hale 2001; Levy 2008)** is pinned as a PROCESSING signal, not as the structure-learning signal (Brennan
  et al. 2020: parser step-count beats surprisal in posterior temporal lobe). **Christiansen & Chater 2016 (BBS 39)** pin the
  constraint that matters: the acoustic trace is gone in ~100 ms → chunk-and-pass, each level chunking the level below.

## 2. Representation — PINNED vs computational-level
PINNED: concurrent cortical tracking of word/phrase/sentence timescales (Ding, Melloni, Zhang, Tian & Poeppel 2016, Nat Neurosci);
phrase-structure building intracranially (Nelson et al. 2017, PNAS); memory-limited cue-based retrieval with interference (Lewis &
Vasishth 2005); multiple-constraint integration (MacDonald et al. 1994); dependency-length minimisation cross-linguistically
(Futrell, Mahowald & Gibson 2015, PNAS). MODEL-level: Matrix-Tree exact marginals, surprisal as linking function, soft-count EM.

## 3. Label-free inducers, with numbers (directed dependency accuracy, WSJ §23, ≤10 / all lengths; Han, Jiang & Tu COLING 2020 survey)
Klein & Manning 2004 46.2/34.9; Berg-Kirkpatrick feature-DMV 63.0/–; Headden 2009 68.8/–; Naseem universal rules 71.9/– (HAND-
AUTHORED, barred for us); Spitkovsky baby steps 56.2/44.1; Viterbi EM 65.3/47.9; **punctuation 69.5/58.4**; lateen EM –/55.6; count
transforms 72.0/64.4; Blunsom & Cohn 67.7/55.7; Jiang neural DMV 72.5/57.6; Han lexicalised+BLLIP 75.1/59.5; Cai CRF-autoencoder
71.7/55.7; He invertible projections 60.2/47.9 (no gold POS); Han D-NDMV 75.6/61.4; Le & Zuidema 73.2/65.8 (extra data).
**The field's label-free ceiling on all-length English is ~0.65, not 0.9. Our 0.5303 is ~0.10 short of the best ever published.**
- **Smith & Eisner 2006 (ACL), Table 3, WSJ10 F1:** EM 41.6 → fixed dependency-length penalty δ=−0.6 DURING LEARNING ONLY **61.8**
  (+20.2) → annealed δ 53.8 → breakage bias 55.6 → annealed 58.4 → CE 57.4 → δ+CE 63.5. The largest single number in the
  literature, from a cue we already have (locality) — but applied at LEARNING time, not decode.
- **Seginer 2007 CCL (plain text, no POS):** WSJ10 UF1 75.9, WSJ40 57.4 (right-branching 61.7; +punctuation 65.8).
- **Ponvert, Baldridge & Erk 2011 (raw text):** cascaded chunking WSJ F 69.5, NPs 76.7; removing phrasal punctuation costs CCL
  −14.1 precision / −13.5 recall.
- **Mareček & Žabokrtský 2012 (EMNLP) REDUCIBILITY:** a POS n-gram is reducible if deleting an occurrence leaves a sequence attested
  elsewhere in a large raw corpus: English 64.1 (≤10) / 49.2 (all) vs Spitkovsky 45.2; label-free, no hand grammar.
- **Cao, Kitaev & Klein 2020 constituency tests** (replace a span, score acceptability): 62.8 F1 PTB, +7.6 over Compound PCFG.
- **Lexical attraction:** Yuret 1998 MI alone on 100M words: 60% P / 50% R on content relations. **Futrell et al. 2019 (Depling):**
  wordform MI is still biased at 320M tokens, while POS/cluster-level MI converges by ~10⁵ tokens → our "lexical cue too sparse"
  is a REPRESENTATION choice (use cluster-level MI), not a data verdict.
- **Categories (Spitkovsky et al. 2011):** punctuation system 58.4 with gold tags → 58.2 with monosemous induced clusters → **59.1
  with context-dependent (polysemous) induced tags** (+0.7 over gold). Type-level clusters in a simple DMV: Clark 47.8, Brown 48.0,
  gold 50.7, oracle 78.0.

## 4. Synthesis — ranked by expected jump, with the brain computation each copies
1. **Strong locality bias applied in LEARNING, dropped at decode, + a sentence-length curriculum** (activation decay in cue-based
   retrieval; the child's short-utterance input). +20.2 (Smith & Eisner); baby steps 44.1 from no initialisation. Our λ is learned
   → converges to the decode-optimal value and cannot express a learning-time bias: add a separate annealed δ on dependency length
   INSIDE the E-step; train rounds over length-capped subsets. Most likely route to the ~0.10 the banned prior was carrying.
2. **Punctuation as HARD fragment segmentation with a two-stage join** (parse inter-punctuation fragments independently, then the
   sequence of fragment heads; looser at inference) — prosodic closure / chunk-and-pass. 58.4 WSJ∞; 10–14 precision points. Our β
   arc penalty bought +0.006 — ~5% of the signal.
3. **A real constituency test for the construction cue — REDUCIBILITY over induced categories** (substitutability/omissibility;
   label-free; converges at our scale). Our induced-construction negatives (n-grams, transition dips) never performed a
   constituent test — consistent with the literature, not a refutation of chunking.
4. **Cluster-level, distance-conditioned MUTUAL INFORMATION as the lexical-attraction cue** (Hebbian co-occurrence): Yuret 60/50;
   estimable at 10⁵ tokens.
5. **Context-dependent (token-level) categories** instead of a type-level inventory: 59.1 > 58.4 gold — aligns with the substrate's
   token-level-meaning pivot.

**Flagged as wrong in our current design:** punctuation as a soft penalty instead of a segmentation; one learned λ doing both
learning bias and decode scoring; type-level category inventory and the consumer-guided-coarsening effort (the literature's fix
is POLYSEMY, not coarseness); treating flat volume as a general verdict when lexical statistics are the one thing that needs
volume; batch Matrix-Tree decoding where brain-fidelity evidence favours incremental left-corner (fidelity, no UAS number).

## 5. Next steps (being executed)
(1) learning-only dependency-length penalty (swept, annealed) with the decode penalty at zero + sentence-length curriculum, on the
knowledge-free bootstrap; (2) punctuation as hard fragment segmentation with a head-sequence join; (3) the reducibility statistic
over induced categories from the reading corpus as the construction cue's value; (4) the lexical cue as cluster-level
distance-conditioned MI.

Sources: Han, Jiang & Tu (COLING 2020 survey); Smith & Eisner (ACL 2006); Seginer (ACL 2007); Ponvert, Baldridge & Erk (ACL 2011);
Spitkovsky et al. (EMNLP 2011; punctuation); Mareček & Žabokrtský (EMNLP 2012); Pate & Goldwater (TACL 2013); Futrell et al.
(Depling 2019); Abend et al. (Cognition 2017); Mintz (Cognition 2003); Cao, Kitaev & Klein (EMNLP 2020); Ding et al. (Nat
Neurosci 2016); Nelson et al. (PNAS 2017); Christiansen & Chater (BBS 2016); Lewis & Vasishth (2005); Futrell, Mahowald & Gibson (PNAS 2015).
