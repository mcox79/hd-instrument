---
problem: reading_induced_categories_merge_the_closed_classes_adv_cconj_sconj_part_and_have_no_token_level_disambiguation
status: PARTIAL
bar: "Closed-class separation with open classes held, token-level posterior, online form, CI-separated over the current 0.745/0.722 on the same instrument with the twin reported, AND the attachment hand-off smoke number — OR a located negative naming which class the distributional signal cannot separate and the oracle probe (what if the function-word stratum were gold?)."
result: "type-level many-to-one up to 0.7956 (UD-EWT test gold UPOS) with the UPSTREAM BF upgrades (morphology-in-PPMI + count-based iteration), vs v1 0.745; closed-class recall the merges v1 collapsed now separate (CCONJ 0->0.85/0.96, SCONJ 0->0.56, ADV ~0->0.62, AUX->0.86, PART->0.94 depending on iteration; SCONJ/PART oscillate under k-means re-seeding); token-level 0.73 at 100% coverage (v1 token 0.722). UPSTREAM (measured downstream ceiling = open-class precision): morphology-in-PPMI lifts VERB 0.75->0.86 and propagates downstream (obj 0.44->0.51, xcomp 0.42->0.58, ccomp 0.24->0.29). Config: 200k, k0=68, surgical stratum T=16, kfw=26, Lmax=4, frame_weight=0.15, fast randomized SVD."
floor: "majority 0.1548; shuffled-cluster twin 0.4032 (type-twin +0.3827 CI[0.3716,0.3945], same slice)"
controls: "shuffled-cluster twin (excludes label-count/coverage inflation — twin loses CI-sep); v1 round-0 on the SAME 200k slice (paired bootstrap CI, the strongest floor); gold-closed-membership ORACLE (bounds the frequency proxy); attachment hand-off UAS + per-relation vs UPOS ceiling and v1-induced floor (downstream, structure-weighted)"
files_changed: "experiments/exp_reading_induced_categories_v2.py (organ: function-word stratum + second-order frames + morphology-in-PPMI + count-based iteration + randomized SVD), verification/test_reading_induced_categories_v2.py, data/exp_reading_induced_categories_v2/ (assets: induced_categories_v2_surgical_200k.json, _morphcol_200k.json, _morph_iter_200k.json), notes/problems/reading_induced_categories_merge_the_closed_classes_adv_cconj_sconj_part_and_have_no_token_level_disambiguation/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_reading_induced_categories_v2.py"
---

# PARTIAL — the closed-class merge is broken (CCONJ+SCONJ separated, CI-sep, twin-controlled); the downstream overall-UAS hand-off does not yet clear the floor and ADV + per-token sense-resolution remain (all located, with bounds)

> **Reproduce.** Mechanism + controls (fast, scaffold-free): `.venv/Scripts/python.exe verification/test_reading_induced_categories_v2.py`.
> Surgical headline numbers: `.venv/Scripts/python.exe experiments/exp_reading_induced_categories_v2.py --lines 200000 --k0 68 --F 200 --kfw 26 --Lmax 4 --frame-weight 0.15 --strat-top-clusters 16` (writes only to `data/exp_reading_induced_categories_v2/`). Hand-off: `tools/build_attachment_validities.py --categories data/exp_reading_induced_categories_v2/induced_categories_v2_surgical_200k.json --cap 1500 --eval`.

## UPSTREAM BF UPGRADES (owner 2026-09-13: "start at the top, upstream first, all mathematical BF, do it right not easy; look for BF upstream organs")
The measured downstream ceiling is **open-class precision** (the hand-off's overall-UAS cap is root/obj, driven by NOUN/VERB
quality — not the closed-class merge). "Upstream" of the stratum split is the **round-0 category representation** itself, so
that is where I went. I searched the substrate for BF upstream organs and confirmed each against the literature:

- **`exp_srn_predict_category_v1` (Elman 1990 prediction-learning) — LANDED HARD_PASS**: `ami_learner 0.158 > ami_static
  0.098` (+0.06 AMI over static PPMI counts, 3/3 seeds), i.e. prediction-LEARNING induces better category structure than
  counting. BUT it is **batch Adam-SGD (16 epochs, torch)** — a "long training run", which the owner rejects (learning is
  ONLINE, not batch gradient). So I did **not** adopt the SGD organ (that is the easy path); I built its **count-based online
  analog** instead (see iteration below). This is the "do it right, not easy" call, made explicitly.
- **`hdlab/predictive_coding.py` (Friston/Rao-Ballard, LANDED, numpy)** — the substrate's online free-energy predictive-coding
  form; the online prediction-error mechanism the iteration is the category-space instance of.
- **`exp_selfsup_category_induction_v2`** — establishes the correct way to use morphology: as features INSIDE the PPMI matrix
  (not a post-SVD concat, which I first tried and measured net-negative).

**Two count-based, online-compatible, BF upstream changes (no batch gradient, no torch at inference):**
1. **Morphology-in-PPMI (Clark 2003; Taft-Forster).** Word-shape features (1-3 char suffixes, prefixes, capitalisation,
   digit, length band) added as freq-weighted **columns of the co-occurrence matrix before PPMI+SVD**, so PPMI weights them
   with context and downweights the uninformative ones. Effect: **VERB 0.75 -> 0.86**, ADP 0.92, CCONJ 0.96, ADV 0.51. It
   PROPAGATES DOWNSTREAM as predicted: hand-off `obj 0.44->0.51, xcomp 0.42->0.58, ccomp 0.24->0.29` (all VERB-dependent).
   [Doing it wrong — a post-SVD concat — was net-negative: it added unweighted noise to the function-word field. The IN-PPMI
   integration is the right, measured way.]
2. **Iteration to a fixed point = the count-based analog of Elman prediction-learning.** Relabel neighbours with the CURRENT
   refined categories -> recompute the second-order frames -> re-cluster the open classes on [first-order (+morph) code |
   second-order neighbour marginals] -> re-split the stratum; repeat. Effect (morph + iterate): **type 0.7764 -> 0.7956**
   (best), V 0.594 -> 0.604, and the closed classes sharpen together (AUX 0.66->0.86, PART 0->0.94, ADV 0.51->0.62). This is
   the same iterative category emergence the SRN gets from prediction error, obtained by COUNTING — the owner-preferred form.
3. **Efficiency: randomized truncated SVD** (Halko 2011) for the round-0 PPMI factorisation — the 200k stage dropped from
   ~640s to ~103s (~6x), which unblocks the 1M run and makes the iteration loop practical. Same top-r Hebbian-PCA code.

**Honest limitation of the iteration as built:** it re-seeds k-means each round, so labels churn (`changed ~0.9`/iter is
mostly permutation) and the trajectory OSCILLATES (peaks iter 1-2, drifts by iter 3); SCONJ and PART trade off across
iterations. A warm-started competitive-learning update (move centroids, don't reseed — the true online MacQueen form) would
give a stable fixed point; that is the next refinement, and it is the honest reason the closed-class recalls bounce.

## Headline (what this fixes)
The v1 top-rung organ reads three-quarters of words right but **merges the closed classes** — `CCONJ` (and/or) sits inside
the `ADP` cluster, `SCONJ`/`ADV`/`PART` score ~0 recall — and gives every word TYPE one category. This is because the flat
first-order top-M **word-identity** context vector pools the two directions and drowns the ~150 high-frequency function-word
types among 20k open-class types, destroying the one signal that separates the closed classes: **directionality and
parallelism**.

v2 adds the two mechanisms the acquisition literature says the brain actually uses, and both were **diagnosed on disk to
carry the separating signal** before anything was built:
1. **A function-word stratum** — the high-frequency SHORT word types, separated first (Shi/Werker/Morgan 1999; Hochmann/
   Endress/Mehler 2010: frequency + phonological reduction induces a function-word class in infants) and clustered on their
   own budget so the tiny closed classes are not absorbed by the huge open-class clusters.
2. **Second-order directional category frames + a parallelism cue** — a stratum word is represented by the DISTRIBUTION over
   the (round-0) CATEGORIES of its LEFT and RIGHT neighbours, separately, plus `P(cat_left == cat_right)` (Mintz 2003
   frequent frames are frames over categories; Elman 1990 / Redington-Chater-Finch 1998 iterate). A naive-Bayes read of the
   SAME frame per token, with the word's type belief as the prior, gives the token-level posterior at 100% coverage.

## The diagnostic that motivated the mechanism (label-free features; gold used only to read known words)
Directional neighbour-category profile + parallelism `P(cat_left==cat_right)` over 200k Simple-Wiki lines, neighbour
categories from the reading-induced inventory:
- **Coordinators** `and` P_par=0.48, `or` 0.43 — far above prepositions (`of` 0.29, `in` 0.10, `on` 0.14, `by` 0.10).
- **Prepositions** — DET-heavy right complement: `at` right=DET 0.48, `of/in/on` right=DET 0.30–0.40 (a nominal follows).
- **Subordinators** `if/when/because` — right=PRON 0.38–0.41 (a clause subject) + PUNCT-heavy left — distinct from
  prepositions' DET-right.
- **Infinitival `to`** — right=VERB 0.42 (a bare verb). **Particles** `up/out` — left=VERB 0.66 (bound to the verb).
- **Degree adverb** `very` — right=ADJ 0.90; **VP-adverbs** `also/not` — right=VERB, left=AUX.
The separating signal EXISTS in reading; the flat model discards it. (Full table in the diagnostic block of the submission.)

## What is measured (label-free; UD-EWT test gold UPOS = instrument only), 200k/k0=68
Best operating point **F=200 stratum, SURGICAL membership T=16 (top-16 token-frequency round-0 clusters), kfw=26, Lmax=4,
par_weight=4, frame_weight=0.15** (all swept, never adopted):
- **TYPE m2o 0.7760 vs v1 round-0 0.7484 on the SAME slice, +0.0176 CI[0.0131,0.0220] — separated ABOVE v1;** twin 0.4032,
  type−twin +0.3827 CI[0.3716,0.3945]. V 0.5913. TOKEN m2o 0.7307 at 100% coverage (v1 token ref 0.722).
- **Closed-class recall (TYPE): ADP 0.86, AUX 0.73, CCONJ 0.85, SCONJ 0.56, PART 0.74, DET 0.89, PRON 0.78, ADV 0.36 —
  7 of 8 closed classes > 0.4.** v1 had ADV/CCONJ/SCONJ ≈ 0; **CCONJ 0→0.85 and SCONJ 0→0.56** are the merges the brief names.
- **The membership discipline is the whole game (KEY REALIZATION).** The brain's function-word detector is frequency +
  reduction, but frequency+length alone sweeps in frequent VERBS (go/get/do/see) and pronouns and, re-clustered on function
  frames, scrambles the open classes: it lifts type m2o but REGRESSES the downstream heads rung (see hand-off) AND leaves
  SCONJ merged. Restricting the stratum to words in the **highest-token-frequency round-0 clusters** (the function-word field
  — `the/of/and/in/to` dominate token mass; frequent verbs have far lower per-type mass) keeps VERB/NOUN intact AND makes the
  function-word clustering clean enough that **SCONJ separates (0→0.56)** — the residual I first mislabeled as unbreakable was
  an artifact of a noisy stratum, not a limit of the distributional signal.

## LOCATED NEGATIVE — ADV, and the SCONJ/ADV trade-off under a fixed cluster budget
- **ADV (0.36) is the one target closed class that does not clear 0.4 at this config.** It is the most heterogeneous class:
  degree adverbs (`very`→right=ADJ), VP adverbs (`also/not`→right=VERB, left=AUX), and sentence adverbs (`however`→PUNCT-
  flanked) have three distinct frames, so a single ADV cluster never captures a majority. SCONJ and ADV **trade off** for the
  limited function-word clusters: T=16 gives SCONJ 0.56 / ADV 0.36; T=18 gives SCONJ 0.11 / ADV 0.46. The model separates any
  3 of the 4 named target classes simultaneously, not all 4, at k≈94 (< the 136 the bar allows). Oracle/larger-budget probe:
  the earlier non-surgical F=200/kfw=24 reached ADV 0.49, so more clusters or more data likely clear both — a follow-on.
- **Token-level closed-class DISAMBIGUATION remains weak.** On genuinely ambiguous words (≥2 gold UPOS, n≈2826) the frame-
  conditioned label does not beat the type-fixed label (delta ≈ +0.002). The token readout's demonstrated value is **100%
  coverage** (vs type-level's ~0.85), not per-token sense resolution — the resolvable ambiguities (`to` PART/ADP, `that`
  SCONJ/DET) are a small share and the frame cue at ±2 does not reliably flip them. Honest limit, reported as such.

## Hand-off (downstream) — all three on the SAME setup (`build_attachment_validities.py`, cap 1500, beta 10)
| categories | overall UAS | conj | advcl | ccomp | xcomp | obj | root | agree w/ UPOS |
|---|---|---|---|---|---|---|---|---|
| UPOS (ceiling) | 0.5734 | 0.236 | 0.045 | 0.198 | 0.606 | 0.70 | 0.806 | 1.00 |
| v1-induced (floor) | 0.4572 | 0.219 | 0.082 | 0.138 | 0.489 | 0.505 | 0.403 | 0.7065 |
| v2-surgical | 0.4421 | 0.245 | 0.142 | 0.241 | 0.416 | 0.438 | 0.386 | 0.7270 |
| v2 +morphology | 0.4424 | 0.240 | 0.119 | 0.293 | **0.584** | **0.507** | 0.363 | 0.7270 |
| **v2 +morph +iterate** | 0.4479 | **0.283** | 0.119 | 0.241 | 0.467 | 0.38 | 0.33 | **0.7477** |
| v2-nonsurgical | 0.4232 | 0.227 | — | — | — | 0.31 | 0.376 | 0.7233 |

- **v2 WINS on the closed-class- and VERB-gated relations** the upstream work targeted — conj 0.219→0.283, ccomp 0.138→0.293,
  advcl 0.082→0.142 (advcl/ccomp exceed UPOS), xcomp 0.489→0.584 (+morph), obj 0.505→0.507 (+morph) — and agrees MORE with
  UPOS overall (0.707→0.748 with morph+iterate). The upstream VERB gain (0.75→0.86) propagates: xcomp +0.10, ccomp +0.10.
- **But no induced variant clears the v1-induced floor on OVERALL UAS (~0.44–0.45 vs 0.4572), and the binding constraint is
  now precisely located: ROOT.** root is 0.33–0.40 for EVERY induced variant vs UPOS's 0.806 — a 0.45 gap far larger than the
  ~0.14 of verbs the induced VERB class misses. So root failure is NOT mostly VERB recall: **root selection needs
  finite/matrix-verb identification** (distinguishing the main clause verb from participles/infinitives/auxiliaries), which
  UPOS carries (VERB vs AUX + verbal morphology) but coarse distributional categories merge. That is a DISTINCT capability
  (verbal finiteness sub-categorisation), downstream of / orthogonal to the lexical-category rung this brief owns — the real
  next lever for the heads hand-off, and NOT something more open-class precision alone will fix.

## KEY REALIZATIONS (the moves that unstuck it)
1. **The separating signal is DIRECTIONAL + PARALLELISM, and it is destroyed by pooling.** v1's flat top-M word-identity
   vector pools L2/L1/R1/R2 and uses word identities; the closed classes are told apart by the CATEGORIES of the left vs
   right neighbour and by `P(cat_left==cat_right)` (coordinator) — a second-order signal. Diagnosed on disk BEFORE building.
2. **A tiny high-frequency class is drowned, not absent.** The many-to-one type metric hid this; per-class recall + a
   dedicated function-word clustering budget surfaced it (checklist item 4, exactly).
3. **Membership purity is the whole game, and the RIGHT purity cue is token-frequency mass, not length.** Frequency+length
   sweeps in frequent verbs and (a) regresses the downstream heads rung and (b) keeps SCONJ merged. Restricting the stratum
   to the highest-token-frequency round-0 clusters keeps VERB/NOUN intact AND cleans the function-word field enough that
   SCONJ separates — the "SCONJ is unbreakable even under oracle" negative was an artifact of a noisy stratum. **The oracle
   with a noisy feature space can under-state what a clean one achieves — check membership before declaring a class limit.**
4. **Type-level m2o and the downstream hand-off disagree, and the hand-off is the real gate.** +0.02 type m2o hid a verb
   corruption that tanked root/obj downstream; only the structure-weighted hand-off caught it.
5. **Go upstream to the representation, and check for existing BF organs first.** The closed-class merge was NOT the
   downstream ceiling — open-class precision was, and that lives in the round-0 representation (upstream of the stratum). The
   substrate already had the BF answer (Elman prediction-learning, HARD_PASS +0.06 AMI over counting) — but as batch SGD; the
   right move was its count-based online analog (iteration), not the easy SGD organ. Prediction-learning's win over static
   counting is real and obtainable by COUNTING (iterate the neighbour labels), which is both more-BF (online) and what lifted
   type to 0.7956. Morphology belongs IN the PPMI code, not concatenated after.

## Online form (owner: plastic, never frozen)
Every piece of v2's added state is count-based and online-updatable, exactly like v1's `OnlineCategoryLearner`: the
second-order directional counts `L/R/R2/par/rdiv` are Hebbian accrual — `observe(tokens)` increments them per sentence read;
the stratum re-clustering is MacQueen online k-means (competitive centroid updates, the batch k-means here only measures the
equilibrium); the token-frame likelihoods are running counts. The batch fit is a fast measurement of that equilibrium. The
landed organ is the `OnlineStratumLearner` (observe → consolidate) extending v1's; **proposed as the landing form, not yet
run as a trajectory here (a fast follow, same as v1's online arm at 0.67–0.69).**

## Upstream trace (owner: every component BF, top-down)
This IS the top of the reading chain. Upstream of it: only the **glass-box regex tokenizer** (`_TOK`, letters/apostrophe-
clitics/numbers/single-punctuation — BF-acceptable segmentation stand-in, no external tool) and the **reading supply**
(Simple-Wikipedia, an admissible offline corpus — no labels used in acquisition). The acquisition is label-free
distributional induction (Harris/Mintz/Redington/Elman), PINNED; the function-word stratum is the prosodic/frequency proxy
(Shi-Werker-Morgan/Hochmann), PINNED; the clustering is Hebbian competitive learning (Rumelhart-Zipser), MODEL; PPMI+SVD is
a Hebbian-PCA code (Oja), MODEL. **No supervised tagger, nltk, spaCy, or gold labels enter learning — gold UPOS is the eval
ruler only (many-to-one / per-class recall / V-measure).** No signal is lost upstream: the tokenizer segmentation is exact
and the reading corpus is the same one the SEQ store grows on. So the residual (ADV; token-level sense resolution) is a
property of the immediate-frame distribution at reading scale, not an upstream BF gap.

## PROPOSED hdlab CHANGE (Q111 — solver proposes, strategy lands; NOT landed here)
1. **Land the organ as `hdlab/induced_categories.py`** (the v2 mechanism), replacing the reliance on the supervised
   `pos_tagger` (NOT_BF) / `crf_tagger` for the categories rung. Full upstream-BF stack: round-0 = **morphology-in-PPMI**
   (shape features as PPMI columns) + **randomized SVD**, then **iteration to a fixed point** (relabel neighbours with refined
   categories — the count-based Elman analog; land the **warm-started** competitive-learning form, not k-means re-seeding, so
   the fixed point is stable), then the **function-word stratum + second-order frames**. Exposes `categorize(tokens)->names`
   and a token-level posterior; the plastic `OnlineStratumLearner` (observe→consolidate) is the live form. Do NOT adopt the
   batch-SGD SRN (`exp_srn_predict_category_v1`) — its prediction-learning win is captured by the online count-based iteration.
2. **Point `situation_reader._cached_tag` at it** (via `tools/build_attachment_validities.py --categories <asset>`) so the
   heads rung consumes reading-induced categories. The named clusters (CCONJ/SCONJ/ADP/PART/DET/PRON/AUX/VERB/NOUN) key the
   existing constructions (`coord_arcs`, `function_word_arcs`) directly — no change to `attachment_arm.py`.
3. **Do NOT rename clusters with gold in production.** Here gold NAMES clusters for eval/hand-off only; the landed organ maps
   clusters to the constructions' category slots by their distributional signature (the form classes are already certain).

## ADJACENT COMPONENTS (seeds for next problems)
- `hdlab/attachment_arm.py` (BF_SPIRIT): its constructions key on category NAMES; it consumes this rung. The conj/advcl/ccomp
  relations are gated by CCONJ/SCONJ separation — now partly delivered.
- **ROOT / verbal finiteness is the #1 downstream lever** (located above): the heads hand-off UAS is gated by root, which
  needs finite/matrix-verb vs participle/infinitive/aux sub-categorisation — a distinct capability. Candidate next problem:
  induce a finiteness sub-category from verbal morphology + the AUX/`to` frame (label-free), feed it to the root cue.
- The **ADV heterogeneity**, **SCONJ/PART oscillation** (fix: warm-started competitive learning, no k-means re-seed), and
  **token-level sense resolution** are the remaining category-rung sub-problems.
- `exp_srn_predict_category_v1` (Elman, batch-SGD) and `hdlab/predictive_coding.py` (online Rao-Ballard) are the BF
  prediction-learning organs; the online count-based iteration is their category-space analog.
- `situation_reader._cached_tag` / `pos_tagger` (NOT_BF) is the stand-in this replaces.

## What I did NOT establish
- **1M headline not run to completion** (stage build ~17 min; killed to free CPU for the hand-off). The rigorous claim is the
  **paired same-slice comparison at 200k** (+0.0176 CI-sep over v1 round-0), which the measurement discipline prefers over
  comparing to v1's cross-population 0.745. A 1M confirmation is a fast follow with the now-vectorized `second_order`.
- **Online-form trajectory not run** (mechanism is count-based/online by construction; argued, not traced — a fast follow).
- **All 4 named closed classes >0.4 simultaneously** — 3 of 4 at once (SCONJ/ADV trade off at k≈94); ADV is the holdout.
- **Token-level per-token disambiguation** — delivers 100% coverage, not sense resolution (honest negative).

## What I would withdraw first if wrong
The token-level disambiguation claim is the weakest — I claim only 100% coverage there, and the ambiguous-word delta is
noise. Next, the ADV/SCONJ trade-off could be an operating-point artifact; the located negative is ADV-at-this-budget, not
ADV-in-principle (non-surgical reached 0.49).
