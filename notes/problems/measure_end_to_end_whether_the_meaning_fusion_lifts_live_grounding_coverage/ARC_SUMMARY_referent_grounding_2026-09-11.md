# ARC SUMMARY -- the referent-grounding data build (2026-09-11)

Final documentation for the visual/cross-modal referent arc (item 1 of PLAN_referent_grounding_data_build + the
honing of fusion (#1) and expansion (#2) + the three optional extensions). Detail lives in SOLVED.md (W37-W40) and
DESIGN_visual_referent_hub_2026-09-10.md; this file is the component + BF-status + next-steps index. reverify:
`.venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py` (37/37; W37-W39 are this arc).

## HEADLINE (what the arc established)
A REAL, non-text VISUAL referent modality (DINOv2 over THINGS photos) adds meaning-similarity signal that our text +
sensorimotor channels miss -- on BOTH a perceptual gold (THINGS-behavior, +0.027 unique R2) and, once denoised by
~14-exemplar volume, a powered SEMANTIC gold (MEN 391 pairs, +0.086 unique R2, CI-separated, shuffled-visual twin
losing, seed-stable). The recovery-gated per-concept precision fusion makes the FUSED hub beat its best single channel
(MEN 0.72 vs 0.64, CI-sep) and cannot dilute by construction. All three optional extensions were then exhausted with
MEASURED reasons (2 located-negatives + 1 data-block), converging on: the referent lever is real and MAXES at the
concrete-depictable slice; the fusion is the brain's convergent-cue (separate pools). Every component brain-foundational.

## COMPONENTS CREATED / INTERACTED -- with mathematical BF status
BF = PINNED brain computation (we copy the operation). BF_SPIRIT = defensible computational-level model or admissible
frozen foundation asset (implementation unpinned, computation faithful). OUR-INVENTION = a labeled choice we do not
claim the brain makes. NOT_BF = a defect (none introduced this arc).

### Created (experiments/ -- solver scope; NO hdlab writes, Q111)
| component | what it computes | BF status |
|---|---|---|
| exp_meaning_fusion_visual_referent_ingest_v1.py | DINOv2 (+CLIP diagnostic) embed of THINGS CC0 photos, 1/concept -> referent vectors | BF_SPIRIT: frozen ventral-stream/IT transducer at INGEST only (Yamins-DiCarlo goal-driven DNN; Konkle-Alvarez self-supervised parity); glass-box numpy preprocessing; NO model at runtime |
| exp_meaning_fusion_visual_referent_ingest_v2.py | MULTI-exemplar embed (full THINGS ~14/concept) -> per-concept CENTROID + exemplar DISPERSION | BF: centroid = prototype abstraction (Posner-Keele 1968; Rosch). BF_SPIRIT: dispersion = per-concept reliability (Shi-Jain). Resumable/checkpointed |
| exp_meaning_fusion_visual_referent_hub_v1.py | cross-modal hub v1 (Cox-Rogers correlated subspace + concreteness precision) + gates G1-G4 | BF_SPIRIT hub geometry; SUPERSEDED as a FUSION step (SVD-over-concat = fuse-one-pool, diluted -- see v2 correction) |
| exp_meaning_fusion_visual_referent_hub_v2.py | recovery-gated per-concept precision CONVERGENT-CUE fusion + MEN semantic gold + G5/G6/G7 + shared-latent control + --multi (dispersion precision) | BF: convergent-cue = Ma-Beck-Latham-Pouget 2006 / Ernst-Banks 2002, separate pools (double dissociation). OUR-INVENTION (labeled): the recovery-gate weight grid, calibrated offline (Ernst-Banks calibration). Carries __bf_corrections__ (v1 SVD fusion was not a precision combiner) |
| verification/test_meaning_fusion_live_coverage.py (W37-W39 added) | scaffold-free witnesses for the visual referent hub, honed fusion, multi-exemplar + shared-latent control | witness harness (asserts load-bearing claims; 37/37) |
| DESIGN_visual_referent_hub_2026-09-10.md + SOLVED.md (W37-W40) | the 8-drill research design + running record + substrate-incorporation manifest | documentation |

### Foundation assets built/acquired (data/ -- offline, admissible; research/non-commercial where noted)
| asset | role | BF/circularity status |
|---|---|---|
| DINOv2 facebook/dinov2-base (frozen) | VISUAL referent transducer (the trusted spoke) | BF_SPIRIT foundation; vision-only, NOT text-contaminated (R2: Raugel/Conwell/Konkle-Alvarez) |
| CLIP openai/clip-vit-base-patch32 (frozen) | DIAGNOSTIC "text-shadow upper bound" arm ONLY | admissible; NEVER a trusted spoke (R2: caption-trained) |
| THINGS images (CC0 + full research set) + concepts-metadata | 1854 concept photos -> referent vectors | curated foundation asset; non-circular w.r.t. golds |
| THINGS-behavior SPoSE 66-d (spose_embedding_66d_sorted.txt) | INDEPENDENT perceptual-similarity gold (human odd-one-out) | non-circular (human judgments; no text, no SimLex) |
| MEN men_3k.txt (Bruni-Tran-Baroni 2014) | powered concrete-noun SEMANTIC gold (391 covered pairs) | non-circular human judgments; relatedness-leaning (distinct-claim) |
| referent_vectors.npz / referent_vectors_multi.npz | single / multi-exemplar per-concept DINOv2+CLIP vectors (+dispersion) | derived cache |

### hdlab organs INTERACTED WITH (read/reused-pattern; NOT modified -- Q111)
| organ | relation to this arc | BF status (as-landed) |
|---|---|---|
| convergent_cue_reader.py | THE match for our fusion: separate-pool, precision-weighted-at-read (Ma-Pouget); confirmed we implement the brain's rule | BF (PINNED operation; weight OUR-INVENTION-calibrated, labeled) |
| hub_spoke_word.py | the PINNED hub-and-spoke architecture (double dissociation) + spoke EXTENSION property; the vehicle for adding modalities as separate pools | BF (hub-and-spoke PINNED); FHRR binding OUR-INVENTION-tagged (kept per owner 08-26) |
| gated_fusion.py | recovery-gate PATTERN reused (VAL-grid incl best-single fallback -> no dilution by construction) | landed HARD_PASS |
| typed_spokes.py / composed_hub_predictor.py / grounded_similarity.py / reading_grounding_loop.py | ATL typed-spoke hub, distributional hub, Lancaster spoke, the live loop's ROUTE-B taps | BF / BF_SPIRIT (per FULL_CHAIN_BF_AUDIT) |

## FULL-CHAIN MATHEMATICAL BF STATUS
Every rung raw-input -> similarity remains BF or BF_SPIRIT; this arc introduced NO NOT_BF atom.
- Visual: pixels -> DINOv2 (BF_SPIRIT transducer at ingest) -> multi-exemplar centroid (BF prototype) -> cosine (BF, Georgopoulos).
- Text: directional PPMI SEQ (BF; Levy-Goldberg) -> TruncatedSVD densify (BF_SPIRIT, phase-diagram move).
- Sensorimotor: Lancaster norms (BF_SPIRIT curated).
- Fusion: convergent-cue, separate pools, precision-weighted, recovery-gated (BF; recovery-weight OUR-INVENTION-labeled).
- REFUTED anti-pattern (correctly NOT adopted): fuse-one-pool shared latent / autoencoder hub -- loses to separate pools.
- DEEPEST RESIDUAL (pre-existing, unchanged this arc): the WordNet-morphy lemmatizer (BF in computation, not glass-box in
  implementation; W30 glass-box prototype exists, needs a curated non-WordNet base-form lexicon). Non-circular w.r.t. SimLex.

## HIGH-PRIORITY NEXT STEPS
1. OWNER DECISION (highest): mark owner_verdict when reviewed. On DONE, the INCORPORATION MANIFEST (SOLVED W37-W40) applies:
   INCORPORATE the multi-exemplar denoised centroid (not single-photo) + convergent-cue precision fusion; AS-DURABLE-
   NEGATIVE the fuse-one-pool hub, object-photo coverage-fill, and ESC-50 sound spoke.
2. GLASS-BOX LEMMATIZER (the one open BF-purity residual, pipeline-wide): replace WordNet-morphy with the W30 glass-box
   morphology + a curated non-WordNet base-form lexicon. Q111/strategy. (Predates this arc; not introduced here.)
3. WIRE (if owner wants the referent spoke live): the referent spoke is validated on similarity golds, NOT on the live
   reading-grounding loop (which is SimLex-coverage-bound, ~18 pairs, for this modality) -- a documented limit, not a bug.
4. DE-PRIORITIZED (measured dead-ends, do NOT re-tread without new data): fuse-one-pool/autoencoder hub; object-photo
   coverage-fill; ESC-50 sound spoke. A COMPREHENSIVE sound spoke (broad AudioSet corpus) remains the only unbuilt
   path, for a niche (~5-11%) modality -- a major data build, owner's call.
5. UNRELATED FRONTIER (different arc): the generative situation/world-model (token-level in-context meaning) -- the
   project's flagged main event, orthogonal to referent grounding.
