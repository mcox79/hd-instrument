# RESEARCH — lexical categories induced from reading (the TOP rung of the reading chain), 2026-09-12

**Owner direction (2026-09-12):** start at the TOP of the chain and make it 100% brain-foundational by position, not by loss
share; nothing frozen (plastic, online); move on the phase diagram before calling anything a ceiling; label every algorithm
PINNED / MODEL / REFUTED; trace what each downstream consumer needs as signal.

## 1. What the brain does (the computation we copy)
- **Substitution classes (PINNED, computational level).** A word's syntactic category is the class of words that fill the same
  immediate frames (Harris 1954). Infants/children acquire categories with no labels from distributional statistics of the
  immediate context: **frequent frames** `a_X_b` (Mintz 2003: 91–98% category accuracy on child-directed speech), left/right
  neighbour vectors over the most frequent context words, clustered (Redington, Chater & Finch 1998), and next-element
  PREDICTION learning that organises hidden states into category clusters (Elman 1990; the substrate's own
  `exp_srn_predict_category_v1` HARD_PASS: prediction-learning adds +0.06 AMI over static counts on Brown).
- **Learning is incremental and exposure-driven (PINNED).** Every token heard is one learning event; frequent words dominate
  category formation (frequent frames ARE the frequent words). Categories form from modest input (children have them from a
  few million words) and keep adapting (plasticity).
- **MODEL (defensible stand-ins, labelled as such):** k-means = the batch form of Hebbian **competitive learning**
  (Rumelhart & Zipser 1985; MacQueen online k-means is its online form); PPMI + low-rank SVD = a compressed association code
  (Hebbian PCA, Oja 1982) over the accrued counts; the token-level readout P(c | w, left, right) ∝ P(c|w)·P(c_left|c)·P(c_right|c)
  = local message passing over cluster bigrams.
- **Orthographic form classes (PINNED as pre-lexical):** punctuation marks and numerals are recognised by visual form (VWFA /
  orthographic route), not by distribution → separated before clustering.
- **Form cue for unknown words (MODEL):** Taft–Forster morphological decomposition as a category cue — P(c | suffix_3/2/1,
  digit) learned from the induced clusters over the known vocabulary (no labels).

## 2. What we built — `experiments/exp_reading_induced_categories_v1.py`
Reads modern Simple-Wikipedia (`data/corpora/simplewiki/simplewiki_clean_v1.txt`, up to 1M lines ≈ 20M tokens) with a glass-box
orthographic tokenizer; accrues word × {L2, L1, R1, R2} × top-M context-word counts; PPMI → rank-r code → exposure-weighted
competitive clustering (k clusters + 2 form classes); Mintz frequent-frame reference; token-level graded readout; a PLASTIC
online learner (`OnlineCategoryLearner`: observe → consolidate; Hebbian accrual + competitive centroid updates). Gold UPOS
(UD-EWT test) is used for EVALUATION ONLY (many-to-one, V-measure, per-class recall); never in acquisition.

## 3. Results (all label-free; majority floor ≈ 0.15; shuffled twin 0.3–0.48)
| setting (lines / k / weighting / extras) | type-level m2o | token readout (100% cov) |
|---|---|---|
| prior attempt (exp_parser_fully_bf_chain_v1): 8k UD sentences, k=17, log weights | 0.323 | — |
| 20k / 34 / log | 0.542 | 0.514 |
| 20k / 34 / sqrt | 0.641 | 0.600 |
| 20k / 34 / **exposure (linear)** | 0.669 | 0.615 |
| 20k / 34 / exposure + **orthographic form classes** | 0.707 | 0.653 (with form cue) |
| 50k / 17 / exposure | 0.577 | 0.548 |
| 50k / 34 / exposure | 0.693 | 0.652 |
| 200k / 17 · 34 · 68 / exposure | 0.618 · 0.684 · 0.699 | 0.591 · 0.652 · 0.663 |
| 1M / 34 · 68 / exposure (pre-form-class code) | 0.645 · 0.706 | 0.614 · 0.678 |
| **1M / 68 + 2 form classes / exposure / form cue (FINAL)** | **0.745** (V 0.592) | **0.722** |
| Mintz frequent frames alone: 20k → 0.529; 1M (88k frames) → 0.410 | | |
| PLASTIC online learner, 20k in 4 consolidations, η=0.05 | 0.677 → 0.654 → 0.689 → 0.670 (cov 0.79) | |
Per class at the final setting: PRON .87, NOUN .85, DET .85, AUX .83, ADP .83, ADJ .80, VERB .78, PART .74, NUM .66, PROPN .54;
ADV .05, CCONJ / SCONJ 0. Supervised tagger reference on the same gold: 0.944.

**Levers, in order of effect:** (1) exposure weighting (+0.13), (2) cluster count (17 → 68: +0.08), (3) orthographic form
classes (+0.04), (4) form cue for unknown words (+0.01 token-level). The reading budget saturates early (50k ≈ 1M at k=34) —
consistent with children forming categories from modest input.

## 4. Refuted / null (do not re-run as-is)
- **Ward hierarchical clustering** on the unit-normalised code: 0.395 = its shuffled twin (spends clusters on rare-word
  outliers); no brain story. REFUTED.
- **The nominal's raw 70-way induced category as a cue in the ROLE competition:** held-out role accuracy 0.9235 → 0.9115
  (SUBJ .941 → .898): too fine for the per-configuration counts. REFUTED-AS-BUILT at this granularity (flag kept off); the
  stronger version is a coarser induced class or per-cue shrinkage once the categories themselves improve.
- **Tag-marginalised role read** (labeler reads the CRF tagger's posterior for the head's category): 0.8063 → 0.8064 on the
  UD-EWT deployment parse = null there (the tagger's home domain); untested on GUM where the tagger costs 0.064.

## 5. Why the closed classes score 0 (cluster inspection, 1M/k68)
The clusters are coherent substitution classes coarser than UD's tagset: {of, and, in, for, as, on, by, with, from, or} =
connectives (ADP 1685 / CCONJ 625 / SCONJ 137 → named ADP); {that, can, but, when, because, if, will, would, however, while} =
clause introducers + modals; {are, be, also, not, were, have, only, often, usually, now} = the auxiliary field with its adverbs;
{the, a, an, its, each, every, X's} = DET (0.99 pure); {it, they, this, which, there, you, we} = PRON. Not a bug — the brain's
categories are not UD's. Open: more clusters (k=136 run), within-cluster refinement by finer frames, or accept the coarser
inventory where the consumer (parser / role competition) reads SUBJ/OBJ configurations rather than CCONJ-vs-ADP.

## 6. Landing form (owner: plastic, never frozen) and hand-down
- The landed organ is the ONLINE learner (observe → consolidate), persisted as a grown asset the way the SEQ store is grown by
  reading; the batch fit only measures its equilibrium. Inventory growth (new words after the first consolidation) is the next
  plasticity step (coverage 0.79 vs 0.83 batch).
- Hand-down: the token-level posterior P(c | w, left, right) is the graded category signal for the parser and the role
  competition (which today read the supervised tagger's hard tag). The current type-level asset
  (`data/frontend_assets/induced_categories_simplewiki_1m_k68.json`) is consumed experimentally by
  `graded_role_assigner.induced_category` (flag off, see §4).

## 7. Downstream repairs this pass exposed (same day, same principle)
Making the role rung BF (Competition-Model labeler live) moved the board 0.6408 → 0.6377 (affected-entity rows UP, patient/state
DOWN). Owner: a downstream regression after a more-BF upstream is NOT failure — trace what the consumer needs. The trace found
UPSTREAM cue gaps (recipient folded into object; two redundant post-verbal cues double-counting) → IOBJ class + animacy +
verb-frame + one slot coalition cue → standalone patient 0.8088 → 0.8207, state 0.8148 → 0.8280 (previous 0.8303 / 0.8333);
596-item pronoun-undergoer decision +0.0268 CI-sep. Full board re-run recorded in `notes/STATUS.md`.

## 8. Sources
Harris 1954 (distributional structure); Mintz 2003 Cognition (frequent frames); Redington, Chater & Finch 1998 Cognitive Science;
Elman 1990 (SRN); Rumelhart & Zipser 1985 (competitive learning); Oja 1982 (Hebbian PCA); Taft & Forster 1975 (morphological
decomposition); Saffran 1996 (statistical segmentation); the substrate's `exp_srn_predict_category_v1`, `exp_parser_fully_bf_chain_v1`.
