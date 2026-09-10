# RESEARCH: brain-foundational syntax ACQUISITION (learned-from-reading, no supervised treebank) — the staged map

**Dispatched by:** research session, 2026-09-09, on the pri-3 problem's deep sub-question ("how does the brain acquire
syntax without labelled trees, and how could the substrate replicate that"). 3 parallel Sonnet lit-scans (25 citations
verified) + full on-disk read of the substrate's own parser organs and TWO prior in-substrate experiments that already
ran variants of this exact question. Lit-scan calibration penalty applied throughout (deflate 0.15-0.25; novel-synthesis
P capped at 0.50).

## HEADLINE

**Two orthogonal defects hide inside "the parser is a frozen supervised hard-decode": (1) hard-decode vs graded-decode
of a GIVEN scorer — solvable NOW, no acquisition dependency, via the `graded_parser` route-through the problem already
targets; (2) supervised-gradient-trained vs self-taught scorer WEIGHTS — the acquisition question, genuinely open, and
the substrate has ALREADY RUN both halves of the answer once.** Category induction from prediction (Elman 1990's
mechanism) is a **verified in-substrate HARD_PASS** (`exp_srn_predict_category_v1`, delta-AMI +0.060 over static
counting, 3/3 seeds). Structure induction from pure co-occurrence (attach-to-best-predictor) is a **located ceiling
that reproduces a well-known field result**: `exp_predictive_selfsup_parser_v1` scored UAS 0.2716, BELOW its own
adjacency-right floor (0.2979) — this is not a bug, it is the field's documented "right-branching trap"
(Klein & Manning 2004: naive right-attachment gets 33.6% DDA on English WSJ10; the first system to beat it, DMV with
an EM-refined locality prior, only reached 43.2%). The fix the literature prescribes — a category-level structural
inductive bias (Naseem et al. 2010, already coded in the substrate's `prior_weight` parameter) refined by EM iteration,
not one-shot counting — was coded but **never run at scale or iterated** (the on-disk run used 3,000 training
sentences, a fraction of the ~12.5k-sentence UD-EWT train split, and zero EM iterations). That is the smallest,
cheapest, highest-leverage next build: not a new mechanism, a missing re-run of an existing one.

## PART 1 — the four mechanism clusters (PINNED / computational-model / OUR-INVENTION)

### 1. Statistical / distributional acquisition
| Mechanism | Status | What it actually buys | Ceiling |
|---|---|---|---|
| Transitional-probability word segmentation (Saffran, Aslin & Newport 1996, *Science*) | **PINNED**, replicated extensively | Segments a continuous stream into WORD-like units from local TP dips | Established ONLY at the word/syllable level. **No literature extends TP-minima to phrase/constituent boundaries** — do not claim this pathway gives syntactic structure; it gives lexical segmentation, a prerequisite, not structure. |
| Now-or-Never / chunk-and-pass (Christiansen & Chater 2016, *BBS* 39:e62) | Computational-level theory (target article + ~30 commentaries — contested in detail, not a single pinned number) | Bounded (4±1–7±2 item) working memory forces EAGER, INCREMENTAL commitment; already **PINNED and implemented** in `hdlab/incremental_parser.py` | Already the substrate's structure-BUILDING mechanism; not itself an acquisition mechanism (it says HOW to build online, not HOW WEIGHTS are learned) |
| Item-based / construction-grammar acquisition (Tomasello 2003 *Constructing a Language*; Brooks, Tomasello, Dodson & Lewis 1999 *Child Development*) | **PINNED**, well-replicated developmental finding | Verb-specific argument patterns learned first; overgeneralization errors concentrate on LOW-FREQUENCY verbs, reliably measurable; abstraction to general schemas is SLOW (age 2-4+) | The strong "zero abstraction before 3-4" reading is contested (Ninio and others argue partial earlier abstraction) |
| Frequent-frames category induction (Mintz 2003, *Cognition* 90:91-117; Redington, Chater & Finch 1998, *Cognitive Science* 22:425-470) | **PINNED**, with a real number: top-45 frames classify English CDS words at **91-98% category-accuracy** | The single strongest quantitative distributional-category-induction result in the literature | **Not language-general** — degrades sharply outside English/French/Spanish (cross-linguistic replications are a known limitation) |

**Substrate home for cluster 1:** `hdlab/reading_grounding_loop.py`'s `track_directional_context_counts` /
`directional_context_lemmas` (`_DIRECTIONAL_OFFSETS = (-1, 1, -2, 2)`, L1/R1/L2/R2-typed neighbours) IS a frame-based
distributional channel in the Mintz/Redington-Chater-Finch sense — direction+distance-typed context IS a generalized
"frame" (a1_X_a2 with typed slots instead of untyped adjacency), grown by reading with NO parser in the loop. It already
measurably beats the untyped bag (SEQ MRR 0.071→0.146 on +500k Simple-Wiki lines). This is the correct, already-landed
acquisition-track home for category-level structure.

### 2. PREDICTION-based structure
| Mechanism | Status | What it actually buys | Ceiling / caveat |
|---|---|---|---|
| Surprisal / expectation-based parsing (Hale 2001 NAACL; Levy 2008 *Cognition* 106:1126-1177) | **PINNED qualitatively** (more-surprising → longer RT); **exact functional form CONTESTED** (Smith & Levy 2013: logarithmic across 6 orders of magnitude, Dundee eye-tracking; Brothers & Kuperberg 2021, N=216+meta: linear) | Requires a GLOBALLY-NORMALIZED incremental parser maintaining a distribution over ALL derivations consistent with the prefix — exactly what `graded_parser`'s Matrix-Tree marginal computes, just not yet incrementally | Functional form still an open empirical dispute; do not over-claim precision on the RT-mapping |
| Left-corner incremental parsing (Abney & Johnson 1991; Resnik 1992 COLING) | Defensible **computational-level model** — memory-load argument (center-embedding hard, left/right-recursion easy) is well-established | The substrate's `incremental_build`'s left-corner bind IS this; **PINNED and already landed**, F1 +0.0352 CI-sep over batch on modern QA-SRL via a PRECISION gain (over-generation fix), not prediction | **Left-corner structure alone does NOT derive garden-path reanalysis cost** — needs pairing with a probabilistic/surprisal layer. This exactly matches the in-substrate finding: prediction/revision in `incremental_parser.py` are "~neutral on aggregate... the F1 win is eager bounded attachment, NOT prediction or revision." |
| Garden-path recovery / "good-enough" processing (Frazier & Rayner 1982 *Cog Psych* 14:178-210; Ferreira & Patson 2007) | Reanalysis-cost finding **PINNED**; "good-enough" persistence **well-evidenced, interpretive** | The substrate's revision path (default-OFF: "hurts clean edited prose") matches Ferreira & Patson's claim directly — humans frequently do NOT fully reanalyze; a shallow good-enough parse persists | — |
| N400/P600 as prediction-error/reanalysis (Kutas & Hillyard 1980; Osterhout & Holcomb 1992; DeLong, Urbach & Kutas 2005 — **contested**, a 2018 eLife mega-replication by Nieuwland et al. found the specific article-preactivation effect did NOT robustly replicate; Kuperberg dual-stream vs Brouwer/Fitz/Hoeks 2012/2017 single-stream Retrieval-Integration account; Frank et al. 2015 *Brain & Language* and Michaelov et al. 2024 *Neurobiology of Language* both directly regress LM surprisal against N400 amplitude and find a real, significant link) | N400-P600 dissociation **PINNED**; surprisal→N400 link **PINNED** (two independent direct-regression studies); which stream does WHAT is **contested** (multi-stream vs single-stream RI) | — | **Direct in-substrate cross-check: the already-SOLVED `the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise` problem tested a surprisal-gated reanalysis trigger and found it added NOTHING over a purely STRUCTURAL coverage-violation trigger** (a slot the parse left empty — a P600-like categorical "something's structurally wrong" signal, not an N400-like graded lexical-surprise signal). This is a genuine, substrate-measured data point suggesting the STRUCTURAL/categorical signal (P600-class) carries more of the acquisition-relevant load than the graded lexical-surprisal (N400-class) signal for STRUCTURE recovery, even though both are real neural phenomena. |

### 3. Self-supervised structure induction from raw text — the label-free routes and their KNOWN ceilings
| Mechanism | Status | Best number (English, gold-tree-free) |
|---|---|---|
| DMV — Dependency Model with Valence + harmonic (locality) initializer (Klein & Manning 2004, ACL) | **PINNED**, foundational result | **43.2% directed dependency accuracy** on WSJ10 (≤10-word sentences, gold POS only), beating the **33.6%** right-branching-baseline for the first time. Degrades substantially past WSJ10. |
| Right-branching / adjacent-attachment baseline for English | **PINNED**, one of the most-cited numbers in the subfield | Right-attach ≈33.4-33.6% directed / ≈56-57% undirected — unusually strong because English is heavily right-branching (local NP/PP attachment). **This is the exact wall the substrate's own `exp_predictive_selfsup_parser_v1` hit** (UAS 0.2716 < adjacency-right floor 0.2979 on UD-EWT test). |
| Yedetore, Linzen, Frank & McCoy 2023 (ACL) — poverty-of-the-stimulus test on CHILDES-scale data | **PINNED**, clean direct negative result | LSTMs/Transformers trained on realistic child-directed-speech volumes, with NO hierarchical bias, generalize subject-aux-inversion by a LINEAR-ORDER rule, not the hierarchical rule — despite good perplexity. **Prediction alone, at realistic data scale, is not sufficient; an additional structural inductive bias is required.** This directly explains why `exp_predictive_selfsup_parser_v1` needed (and coded, but under-ran) `UNIVERSAL_PRIOR`/`prior_weight`. |
| Neural grammar induction family: PRPN (Shen 2018), ON-LSTM (Shen 2019, 47.7 F1), compound PCFG (Kim/Dyer/Rush 2019, 60.1 solo / 66.9 combined, ACL), StructFormer (Shen 2021, 54.0 F1) | **PINNED empirical literature**; every one of these bakes in SOME hierarchical/tree-structural bias | SOTA fully-unsupervised WSJ constituency F1 tops out **~mid-60s**, vs **~92+ supervised**. Bias-free extraction from a pure-prediction LM (BERT attention probing / Perturbed Masking) scores well below the biased models. |
| Elman 1990 (*Cognitive Science* 14:179-211) — prediction-learning induces lexical category clusters | **PINNED qualitatively** (dendrogram); **no modern quantitative (NMI/AMI/purity) replication found in the external literature** | — the substrate's `exp_srn_predict_category_v1` appears to be a genuine, controlled, quantitative extension of this 35-year-old qualitative result: **HARD_PASS, delta-AMI +0.0602 (3/3 seeds), learner AMI 0.1585 vs static-PPMI AMI 0.0983 vs random ≈0** |

**Honest reading of the ceiling:** fully-unsupervised structure induction in the published literature caps in the
40-65% dependency-accuracy / mid-60s constituency-F1 range, well below supervised. This is a **field-level, PINNED
ceiling**, not a substrate implementation gap — the problem's own bar explicitly allows a rigorous located negative
here as a full PASS.

### 4. Globally-normalized probabilistic parsing (Matrix-Tree / edge marginals) as the graded posterior
Koo, Globerson, Carreras & Collins (2007, EMNLP-CoNLL), McDonald & Satta (2007, IWPT), Smith & Smith (2007,
EMNLP-CoNLL) — all **PINNED, verified** — independently converge on computing exact P(edge present) under a
globally-normalized log-linear distribution over spanning trees via ONE Laplacian-matrix inverse. This is EXACTLY what
`hdlab/graded_parser.py`'s `single_root_marginals` computes (Koo et al. 2007's single-root variant specifically,
brute-force-verified to 1e-6 against exhaustive enumeration). **Direct psycholinguistic-plausibility literature for
Matrix-Tree marginals specifically is thin** — but the adjacent, emerging "multipath parsing in the brain" line
(Franzluebbers, Dunagan, Stanojević, Buys & Hale, ACL 2024 — a single fMRI study, mark CONTESTED/single-study) found
that surprisal computed over MULTIPLE simultaneously-maintained parses fits bilateral STG timecourses better than
single-path surprisal, in both English and Chinese. That is direct, if young, empirical support for "the brain
maintains a graded distribution over structures, not one hard-decoded tree" — the core premise this whole problem is
built on, and the reason routing through the graded marginal is more brain-faithful **regardless of how the
acquisition question resolves.**

## PART 2 — mapping onto the substrate's existing organs (read on disk, this session)

| Organ | Role in the acquisition map | Status |
|---|---|---|
| `hdlab/graded_parser.py` (`GradedParse`, `single_root_marginals`, `chu_liu_edmonds`) | The TARGET graded representation — exact single-root Matrix-Tree posterior over a GIVEN arc-factored scorer's edge scores. Decode-side only; agnostic to how the scorer's weights were learned. | Landed, self-tested, math verified brute-force-exact |
| `hdlab/incremental_parser.py` (`incremental_build`) | The structure-BUILDING mechanism (Now-or-Never eager left-corner bind, bounded buffer). PINNED to Christiansen & Chater 2016 + Ferreira/Frazier. | Landed BF_SPIRIT, F1 +0.0352 CI-sep, structural-fidelity module — genuinely brain-faithful, orthogonal to the acquisition question |
| `hdlab/sequence_memory.py` (`SequenceMatrix`, S/S_back) | Ordered-pair Hebbian binding — the temporal-order substrate primitive the directional channel's L1/R1/L2/R2 typing borrows its principle from | Landed, orthogonal primitive (not currently wired to the parser acquisition path — a candidate substrate for a genuinely Hebbian, non-EM re-estimation of directional association, see Part 3 open question) |
| `hdlab/reading_grounding_loop.py` `track_directional_context_counts` / `directional_context_lemmas` | **The parser-free, direction+distance-typed IDENTITY/category channel that grows by reading** — just landed (pri-2). This is cluster-1's (distributional/frame-based category induction) home, and it is PURE — no supervised parser, no gold trees, in its loop. | Landed, default-OFF flag, proven (SEQ MRR +0.075) |
| `experiments/exp_srn_predict_category_v1.py` | In-substrate replication+extension of Elman 1990: prediction-LEARNING (order-sensitive VSA bundle+cleanup, error-driven SGD) induces POS-category structure significantly beyond static PPMI counting. | **HARD_PASS on disk**, full-scale run already exists |
| `experiments/exp_predictive_selfsup_parser_v1.py` | In-substrate self-supervised DEPENDENCY (attachment) induction: directional PMI-style co-occurrence (word+POS only, NO gold trees) + optional universal category-level structural prior (`prior_weight`, Naseem-2010-style). | **Located ceiling on disk** — sub-scale run (3,000/~12,500 train sentences, ZERO EM iterations), UAS 0.2716 below its own 0.2979 adjacency-right floor. NOT yet run at proper scale or with iteration — this is the gap, not a proven failure. |

## PART 3 — the STAGED proposal

**Stage 0 (do now, unblocked by acquisition):** route the reader's parse consumers through `graded_parser`'s marginals,
per the parent problem's own bar. This is independently justified by Part 1 cluster 4 (globally-normalized posterior =
more brain-faithful representation of what the brain maintains) and does not require resolving the acquisition
question — the scorer underneath can stay the current frozen averaged-perceptron OR a future self-taught one; the
graded DECODE is a strictly-better readout of either.

**Stage 1 — the smallest brain-foundational acquisition step, building on the directional channel (RECOMMENDED FIRST
BUILD):** `exp_predictive_selfsup_parser_v1.py` already has the correct SHAPE (directional co-occurrence → PMI-style
attachment score → decode, no gold trees) but was run at a fraction of scale with zero refinement iterations. The
literature (Klein & Manning 2004; Yedetore et al. 2023) says the missing ingredients are (a) FULL training scale
(≈12,500 UD-EWT train sentences, not 3,000) and (b) an EM-style **re-estimation loop**: decode the current corpus
with the current scores, re-accumulate directional co-occurrence WEIGHTED by the current decode's attachment
probabilities (exactly what `graded_parser`'s Matrix-Tree marginal gives you for free — feed the induced scorer's own
`single_root_marginals` back into the co-occurrence counter as soft counts), iterate 2-3 rounds. This is DMV's actual
mechanism (generative EM, not one-shot counting) reimplemented with the substrate's own directional-channel counting
primitive and its own graded-marginal decode — a genuine synthesis of an already-landed acquisition channel with an
already-landed graded decode, not a new organ.

**Stage 2 — strengthen the structural inductive bias:** properly tune/sweep `UNIVERSAL_PRIOR`/`prior_weight`
(Naseem-2010-style category-level head→dependent preferences; cited in-substrate, not independently re-verified this
pass — flag as substrate-cited, do not assume the citation is exact without checking the original) jointly with the
EM loop above, since Yedetore 2023 argues bias-free prediction at realistic data scale defaults to the linear-order
shortcut. Sweep, never adopt the prior's weight (per the phase-diagram discipline) — the reported figure of
`prior_weight=3.0` in the one on-disk run was a single point, not a swept optimum.

**Stage 3 (only if Stage 1-2 clear the floor):** feed the self-taught scorer's weights into `graded_parser` as an
ALTERNATIVE to the treebank-trained `arc_parser` asset, A/B the two as the input to the Matrix-Tree marginal on the
SAME downstream board dims, keep whichever wins CI-separated (or keep both — the treebank asset as a vetted offline
FOUNDATION per the problem's own admissibility clause, the self-taught one as the brain-foundational-acquisition
track, not mutually exclusive).

## Cheap decisive test

Re-run `experiments/exp_predictive_selfsup_parser_v1.py` at FULL scale (`--train-sents` default already requests
1,000,000, i.e. effectively the full ~12,500-sentence UD-EWT train split — the on-disk run used only 3,000, an
unexplained sub-scale invocation) with a 2-3 round EM re-estimation loop added (soft-count directional co-occurrence
weighted by the current decode's `single_root_marginals`, from `graded_parser`, instead of hard one-shot counts), and
a small sweep over `prior_weight` (0, 1, 2, 3, 5) x `lam` (0.3, 0.6, 0.9). This is CHEAP: the scorer is pure counting +
`chu_liu_edmonds` decode (no gradient training, no GPU); the harness, floors, info-free twin, and supervised upper
reference all already exist and just need the corpus swapped in and the EM loop bolted on. Expected wall-clock:
CPU-minutes, not hours.

## Falsifiable predictions

**HARD-PASS:** at full UD-EWT-train scale with ≥2 EM re-estimation rounds and a swept `prior_weight`, the
self-supervised inducer's UAS on held-out UD-EWT test beats the STRONGEST real floor (adjacency-right, currently
0.2979 on the small-scale run — recompute on full test) CI-separated (bootstrap by sentence, report half-width), AND
beats the info-free shuffled-pair twin CI-separated, on ≥3 seeds.

**HARD-FAIL (a legitimate, field-consistent located negative, NOT a substrate deficiency):** even at full scale with
EM iteration and a swept structural prior, UAS remains at or below the adjacency-right floor CI-separated. Per Part 1
cluster 3, this would exactly reproduce the field's own documented ceiling (English's right-branching bias makes the
trivial floor unusually hard to beat; DMV's own margin over it was only ~10 points absolute, and that was with
lexicalization/valence machinery this first pass does not yet have). If this is the outcome: name it precisely as
"the right-branching-trap ceiling, PINNED in Klein & Manning 2004 and reproduced here" and route to Stage 3 (keep the
treebank-trained scorer as an admissible offline FOUNDATION asset, adopt only the graded DECODE — Stage 0 — as the
brain-foundational win).

**Already-decided, do not re-test:** category induction from prediction (Part 1 cluster 1 + cluster 3's Elman thread)
is a standing HARD_PASS on disk (`exp_srn_predict_category_v1`, delta-AMI +0.0602, 3/3 seeds) — this question is
CLOSED; the open question is structure (attachment), not category.

## Cross-thread synthesis

Builds on / does not duplicate: `notes/research_MASTER_MAP_language_acquisition_biology_to_substrate_2026-07-09.md`
(the general acquisition thesis this drill specializes to the parser), `notes/research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md`
and `notes/research_incremental_stack_parsing_paradigm_2026-07-22.md` (the graded/incremental structure-BUILDING side,
already answered and landed as `incremental_parser.py`), `notes/research_earn_structure_extraction_vs_supply_parser_fork_2026-08-01.md`
(the "earn vs supply" framing this note's Part 2/Stage-3 answer directly resolves: BOTH, staged, not exclusive).
Directly informed by two already-SOLVED problems: `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment`
(graded competition's value is CALIBRATED UNCERTAINTY, not raw accuracy — a THEOREM that graded argmax equals discrete
argmax on accuracy; sets honest expectations for what Stage 0's route-through should be measured on: difficulty/AUC
signals, not accuracy lifts alone) and `the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise`
(surprisal-gated reanalysis added NOTHING; the STRUCTURAL coverage-violation trigger carried the whole win — informs
Part 1 cluster 2's honest weighting of N400-class vs P600-class signals for structure recovery).

## Substrate-product implications

Two separable product decisions, not one: **(1) Ship the graded route-through now** — it is justified independently of
acquisition (Part 1 cluster 4 + the multipath-parsing-in-the-brain evidence), it is cheap (the marginal is already
computed once per read for other consumers), and the prior `discrete_where_the_brain_is_graded` SOLVED result sets
honest expectations: measure it as a calibrated-uncertainty / hard-case-detection win first, an accuracy win only if
the data supports it. **(2) Treat learned-from-reading structure acquisition as a SEPARATE, parallel, genuinely open
track** — worth the cheap re-run above because if it clears even the modest field-level bar (DMV's own margin over
right-branching was only ~10 points), it removes the product's single largest scaling dependency: right now the
parser's quality is capped by treebank SUPPLY (a fixed, English-newswire-skewed, ~12.5k-sentence asset that already
demonstrably degrades on other registers — the 19c-prose parser degradation documented in the predict-and-revise
SOLVED note is the same asset-mismatch risk). A self-taught scorer that improves by READING MORE (any register, any
volume, free) is the only route off that ceiling. If the cheap test comes back HARD-FAIL, that is not wasted motion —
it is a real, citable, field-consistent located negative that settles the admissibility question stated in the parent
problem's bar: the treebank-trained scorer stays as a vetted offline FOUNDATION asset (letter of the invariant
satisfied: static, offline, glass-box, no external tool at inference) while the substrate is honest that the
TRAINING PROCEDURE behind it (supervised gradient descent on hand-labelled trees) is not itself a mechanism the brain
uses — a real, named, currently-unclosed fidelity gap, not a hidden one.

**What the brain does that we cannot yet replicate, honestly stated:** every mechanism in Part 1 that gets syntax
above the ~45-65% dependency-accuracy / mid-60s-F1 ceiling in the literature does so with additional signal a
text-only corpus does not carry — joint attention and pointing, prosodic phrasing (pitch/pause cues to constituent
boundaries), caregiver contingent feedback/recasts, and roughly 18-24 months of real-time embodied interaction before
productive syntax appears (the social/interactive acquisition track named in `notes/research_social_interactive_language_acquisition_5x_2026-07-09.md`,
not re-derived here). None of that is available from a text corpus, at any scale. This is the honest reason a
text-only self-supervised parser should be EXPECTED to plateau below the field's already-modest ceiling rather than
match human acquisition outright — and why the fallback (graded decode of a treebank-trained scorer, Stage 0) is not
a concession but the correct near-term product answer regardless of how Stage 1-2 resolve.

## Citations (verified count)

25 distinct citations independently verified this session across 3 parallel lit-scans (author+year+venue checked,
not taken from memory): Saffran/Aslin/Newport 1996; Saffran & Wilson 2003; Romberg & Saffran 2010; Christiansen &
Chater 2016; Tomasello 2003; Tomasello 1992 (verb-island diary study); Brooks/Tomasello/Dodson/Lewis 1999; Brooks &
Zizak 2002; Mintz 2003; Redington/Chater/Finch 1998; Klein & Manning 2004; Hale 2001; Levy 2008; Smith & Levy 2013;
Brothers & Kuperberg 2021; Abney & Johnson 1991; Resnik 1992; Frazier & Rayner 1982; Ferreira & Patson 2007; Kutas &
Hillyard 1980; Osterhout & Holcomb 1992; DeLong/Urbach/Kutas 2005 (+ Nieuwland et al. 2018 non-replication); Frank et
al. 2015; Michaelov et al. 2024; Koo/Globerson/Carreras/Collins 2007; McDonald & Satta 2007; Smith & Smith 2007;
Franzluebbers/Dunagan/Stanojević/Buys/Hale 2024; Yedetore/Linzen/Frank/McCoy 2023; Shen et al. 2018 (PRPN); Shen et
al. 2019 (ON-LSTM); Kim/Dyer/Rush 2019 (compound PCFG); Shen et al. 2021 (StructFormer); Wu/Chen/Kao/Liu 2020
(Perturbed Masking); Clark et al. 2019 (BERT attention); Elman 1990. Two additional in-substrate PINNED citations
(Christiansen & Chater 2016, Ferreira/Frazier) were already independently verified at land time in `incremental_parser.py`
and not re-verified here. One in-substrate citation (Naseem et al. 2010, universal structural prior) is cited in
`exp_predictive_selfsup_parser_v1.py`'s docstring but was NOT independently re-verified this pass — flag before
quoting it as PINNED.

**P_deflated (Stage 1-2 clearing the floor CI-separated at full scale):** 0.30 (base estimate ~0.45-0.55 given DMV
precedent; deflated 0.15-0.25 for uncharted-regime lit-scan calibration; capped at 0.50 for novel synthesis in any
case). **P_deflated (category induction, Part 1 cluster 1/3):** N/A — already a verified HARD_PASS on disk, not a
prediction.
