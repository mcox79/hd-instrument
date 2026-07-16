# Research: graded early-reader corpora + a from-zero language-acquisition curriculum plan

**Date:** 2026-07-16. **Filed by:** research (Sonnet lit-scan x3, Opus synthesis). **Trigger:** scoping drill — scope the concrete graded early-reader LANGUAGE (vocabulary + grammar) acquisition corpus and a from-zero curriculum plan for the language module. Distinct from `research_curriculum_prerequisite_datasets_2026-07-16.md` (that drill scoped FACT-ORDER datasets — TQA/Junyi — for the ingestion-order ablation; this drill scopes VOCAB+GRAMMAR acquisition specifically). Feeds the early-reader glass-box probe conditionally on passing the cheap decisive test below.

**Method:** 3 parallel Sonnet lit-scan sub-agents, live WebSearch+WebFetch, one lane each: (1) CHILDES/AoA-norms/statistical-learning, (2) graded readers/sight-word lists/Simple Wikipedia, (3) grammar-acquisition-order/SLA-sequencing/statistical-learnability-thresholds. All returned live-verified reports; explicit unverified items flagged per-lane rather than smoothed over (per calibration discipline).

---

## (a) HEADLINE

**A genuinely usable "from-zero" curriculum is buildable TODAY entirely from free, open, machine-readable public resources — no licensing negotiation, no scraping proprietary graded-reader series required — but it must be ASSEMBLED from ~5 separate sources, because no single dataset ships vocabulary progression + grammar progression + real child-acquisition ordering + attached readable text all at once.** The cleanest split found: **Dolch/Fry + CEFR-J give the vocabulary ladder** (public-domain / open-license, pre-graded by level); **Kuperman AoA + Wordbank/CDI give the empirical child-acquisition ordering signal** to validate or re-rank that ladder; **Simple English Wikipedia's own house style (`Wikipedia:HOW`) gives an already-articulated grammar progression** (SVO → SV+IO → one-subordinate-clause-max, no compound-complex, no passive, no contractions) that is a ready-made rung-ladder, not something we'd have to derive; **the Basic English 850-word list (Ogden) + VOA Special English (~1500 words) are the two best-documented real-world "controlled simple English" systems** and are the single cheapest concrete starting vocabulary+grammar combination; **Processability Theory's implicational processing hierarchy** (lexical-morphology → phrasal-agreement → inter-phrasal/S-procedure → subordinate-clause) is the one finding in the whole scan that gives a genuine prerequisite-DAG for grammar (not just a flat empirical sequence like Brown's morphemes) and is the best gating logic for "when has this rung been mastered, advance." The **BabyLM Challenge corpus composition** (an active NLP research community's already-validated "developmentally-plausible acquisition corpus," mixing CHILDES/CBT/Gutenberg/Simple-Wikipedia/subtitles in named ratios) is direct precedent that this exact assembly approach works and has already been vetted by others attempting the same goal.

---

## (b) Cheap decisive test

Before committing engineering time to build the full 5-source assembly, run ONE cheap test on the SMALLEST starting corpus (see section 4 below):

- **Arm CURRICULUM-ORDER:** ingest the Dolch Pre-K→3rd-grade word tiers + Simple-Wikipedia-style SVO-only sentences, in the graded order (Pre-K sight words + SVO present-tense first, then Kindergarten tier, then 1st/2nd/3rd, adding tense/clauses per the SVO→SV+IO→one-clause Simple-Wikipedia grammar ladder).
- **Arm SCRAMBLED:** identical word/sentence pool, randomized ingest order, matched budget.
- Measure: (i) does the glass-box probe's schema-fit / additive_map signal show cleaner (lower premature-rejection) uptake on CURRICULUM-ORDER than SCRAMBLED — this reuses the exact metric already instrumented in `research_developmental_curriculum_permissive_to_selective_gate_schedule_2026-07-16.md`; (ii) does a held-out probe on the NEXT tier's sight words show measurably better zero-shot uptake when the probe has seen the prior tier's words first (a direct within-domain replication of the Tolerance-Principle-style "does mastering rung N help rung N+1" question, but on real graded vocabulary instead of synthetic).

**HARD-PASS:** CURRICULUM-ORDER beats SCRAMBLED by >=10 points on premature-rejection rate AND/OR next-tier zero-shot uptake, at matched budget.
**HARD-FAIL:** statistically indistinguishable (within ~3 points) — would indicate Dolch/Fry grade-tiers (built for HUMAN pedagogical pacing, not validated dependency structure) are too weak a proxy to move the needle on THIS substrate's specific gate signal, mirroring the exact honest-gap finding already logged for TQA in the sibling fact-order note.

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 — the Dolch/Fry grade-tier vocabulary order + Simple-Wikipedia SVO-first grammar order reproduces the curriculum-order-beats-scrambled advantage already predicted for fact-order datasets, on the VOCAB+GRAMMAR axis specifically.**
P estimate: **P=0.32** (deflated per lit-scan calibration; slightly above the TQA fact-order estimate of P=0.30 because Dolch/Fry grade-tiers were built and validated over decades of direct classroom pedagogical use specifically for word-acquisition sequencing — a narrower, more direct match to "vocabulary order" than a science-textbook's chapter sequence is to "concept prerequisite order" — but still capped low because grade-tiers reflect human pedagogical convention, not a mechanistically validated dependency graph, and no published study has tested this specific curriculum-order-vs-scrambled question on a computational substrate).

**Prediction 2 — Processability Theory's implicational processing hierarchy (lexical-morphology before phrasal-agreement before inter-phrasal-agreement before subordinate-clause structures) gates grammar-rung advancement better than Brown's flat morpheme-order or an ungated flat grammar corpus.**
HARD-PASS: gating rung-advancement on PT's hierarchy (never introducing an agreement/embedding structure until the substrate's own probe shows mastery of the prerequisite processing stage) reduces error/rejection rate on the NEXT grammar rung by >=15 points vs. introducing all grammar rungs in a flat/ungated sequence. HARD-FAIL: no measurable difference, or ungated flat sequencing performs equally well (would suggest the substrate's own gate mechanism already discovers the same implicational structure without needing PT baked in as a prior).
P estimate: **P=0.30** (deflated; PT is the most structurally rigorous finding in the scan — a genuine implicational DAG, not just an empirical sequence — but transferring a human sentence-processing-architecture theory onto a non-human substrate's own gate mechanism is an untested leap).

**Prediction 3 — CDS-frequency-derived word order (from CHILDES/childes-db, the words infants actually hear most, per Jones et al. 2023) outperforms adult-corpus-frequency order (SUBTLEX) as a curriculum ordering signal, since CDS-frequency tracks true child acquisition order more closely than adult-directed-speech frequency does.**
P estimate: **P=0.28** (deflated; the underlying human-development finding — CDS frequency > adult frequency as an acquisition-order predictor — is fairly well-established in the child-language literature per the lit-scan, but whether that same ordering advantage transfers to THIS substrate's ingestion mechanism is, as always, the untested step).

---

## (d) Cross-thread synthesis

- **Directly complements, does not duplicate, `research_curriculum_prerequisite_datasets_2026-07-16.md`.** That note scoped FACT-prerequisite datasets (TQA linear textbook sequence, Junyi validated DAG) for the concept-ordering ablation. This note scopes VOCAB+GRAMMAR datasets for the language-module-specific ladder. Both land on the identical taxonomic split independently: **datasets with real ORDER but thin content** (Junyi DAG / PT implicational hierarchy / Brown's morpheme order) vs. **datasets with real CONTENT but only implicit/pedagogical order** (TQA chapter sequence / Dolch-Fry grade tiers / Simple Wikipedia's house-style grammar rules). This is now a 2x-confirmed structural pattern across two independent domains (facts and language) — worth carrying forward as a general principle for future curriculum-sourcing drills: **real order and real content are almost never co-located in one off-the-shelf public dataset; expect to assemble, not find.**
- **Converges with `research_MASTER_MAP_language_acquisition_biology_to_substrate_2026-07-09.md`'s Finding #2 (curriculum order recipe):** the master map's biology-derived recipe — pure distributional/statistical bootstrapping (Saffran) -> small grounded seed set -> vocabulary-SIZE threshold (not age) -> combinatorial/relational training — now has concrete DATA to instantiate each stage: Bernstein-Ratner phonemicized CDS (stage 1, statistics-only segmentation, real ground-truth benchmark with decades of published baselines), Dolch Pre-K/K tier + Basic-English-850 (stage 2, small grounded seed), Fry/CEFR-J bands + CDI/Wordbank vocabulary-size milestones (stage 3, the vocabulary-threshold gate itself is empirically measurable — Wordbank's ~50-word and ~200-300-word milestones map exactly onto the master map's cited onset/grammar-burst thresholds), Simple-Wikipedia grammar ladder + PT hierarchy (stage 4, combinatorial/relational).
- **Converges with `research_developmental_curriculum_permissive_to_selective_gate_schedule_2026-07-16.md`'s schema-fit premature-rejection metric:** exactly the same instrumentation applies here; this note supplies the vocab+grammar-specific real data to run it against, parallel to how the sibling note supplied TQA for the fact-order case.
- **New finding this drill adds:** the **Tolerance Principle** (Yang) gives a genuinely quantitative, falsifiable formula (`e <= N/ln(N)`) for "how many distinct exemplars does a rung need before a rule generalizes" — this is more operational than anything in either prior curriculum note and directly answers a design question (rung SIZE, not just rung ORDER) that neither the fact-order nor the prior language-curriculum notes addressed. It should be treated as a candidate gate-threshold formula for rung-advancement decisions generally, not just for this language module.
- **BabyLM Challenge is a load-bearing external validation** that this entire assembly strategy (CHILDES + CBT + Gutenberg + Simple Wikipedia + subtitles, in named mixture ratios) is already a live, actively-researched approach to "developmentally-plausible acquisition corpus" construction by an outside NLP community — reduces novel-synthesis risk on the ASSEMBLY question specifically (though says nothing about whether ORDER, as opposed to mere composition, matters — BabyLM's stated goal is data-efficiency from realistic scale/mixture, not an order ablation).

---

## (e) Substrate-product implications

1. **Immediate, near-zero-friction starting point (see section 4 below for full detail): Dolch sight-word list (315 words, public domain, pre-graded Pre-K through 3rd) + Simple-English-Wikipedia-style SVO sentence templates.** Zero licensing friction, zero scraping friction (short enough to transcribe directly from any of several mirror sites), immediately gradeable, immediately glass-box-tractable.
2. **Near-term second step: CEFR-J Wordlist v1.5 (open CSV on GitHub, `openlanguageprofiles/olp-en-cefrj`) for the vocabulary ladder beyond Dolch/Fry's ~1000-1300 words**, since CEFR-J already ships word+CEFR-level+POS fields in a directly ingestible format — no transcription needed, unlike Dolch/Fry.
3. **Grammar ladder: adopt Simple English Wikipedia's own house style (`Wikipedia:HOW`) as the literal rung sequence** — it is already articulated as an explicit progression (SVO declarative -> SV+indirect-object -> one subordinate clause max -> no compound-complex/no passive/no contractions) by a real editorial community optimizing for exactly this kind of simplicity gradient, and its example sentences are directly available (Simple Wikipedia dumps) as training material at each rung.
4. **Validate/re-rank vocabulary order against Kuperman AoA (30,121 words, years-based) and Wordbank/CDI (per-word %-producing-by-month curves, the gold-standard empirical child-acquisition-order signal for the earliest ~400 words)** once the Dolch/CEFR-J assembled list is built — this is the empirical cross-check that keeps the curriculum developmentally-faithful, not just pedagogically-conventional.
5. **Gate rung-advancement using Processability Theory's implicational hierarchy** (lexical-morphology before phrasal-agreement before S-procedure before subordinate-clause) rather than a flat sequential list — this is the one finding in the scan with genuine prerequisite-DAG structure for grammar, directly analogous to how Junyi's DAG was flagged as the highest-fidelity (if highest-friction) option in the sibling fact-order note.
6. **Use the Tolerance Principle (`e <= N/ln(N)`) as a candidate quantitative gate formula** for "has this rung been mastered" — i.e., don't advance the curriculum to the next vocabulary/grammar tier until the number of exceptions/errors on the current tier's probe falls under this threshold relative to total exemplars seen. This is a concrete, computable, substrate-agnostic formula worth wiring directly into the gate-schedule mechanism already being built per the sibling curriculum notes.
7. **CHILDES/childes-db and Bernstein-Ratner remain the correct source for the STATISTICS-ONLY bootstrapping first rung** (matches Saffran's transitional-probability finding — pure distributional segmentation, zero semantic grounding, zero labels) — this is genuinely rung ZERO, prior to any vocabulary/grammar content at all, and has decades of published baseline segmentation-accuracy numbers to sanity-check the substrate's own statistics-only mechanism against.
8. **Do NOT budget engineering time toward Oxford Reading Tree, Reading A-Z, or Lexile** — all three confirmed proprietary/paywalled this cycle (level TAXONOMIES are public, actual book TEXT and the underlying corpus are not); their only useful contribution is as a naming/reference scale for communicating levels to the USER, not as an ingestible data source.

---

## 1. Graded early-reader corpora (ranked, real, accessible)

| Rank | Source | Grading/level structure | Vocab progression | Sentence-complexity progression | Size | Access/licensing friction |
|---|---|---|---|---|---|---|
| 1 | **Dolch sight-word list** | Yes — Pre-K(40)/K(52)/1st(41)/2nd(46)/3rd(41) + 95-noun list | Yes, IS the vocab progression | No (word list only) | 315 words | Public domain (1936/1948); no canonical CSV found, transcribe from PDF/HTML |
| 2 | **Fry sight-word list** | Yes — 25 lists x 40 words, frequency-ranked, ~grade1-9 | Yes | No | 1,000 words | Freely reproduced everywhere; PD status unconfirmed (not as clean as Dolch) |
| 3 | **CEFR-J Wordlist v1.5** | Yes — CEFR A1-C2 + POS tags | Yes | No | full word+level+POS coverage | Open CSV on GitHub, free incl. commercial use w/ citation |
| 4 | **Simple English Wikipedia (+ house-style grammar rules)** | Implicit (vocab-restricted register) + explicit grammar-simplicity house style | Basic English 850/1500 tiers referenced | **Yes** — explicit SVO->SV+IO->1-clause-max progression in `Wikipedia:HOW` | ~171MB plaintext (2024 snapshot) | Fully open, CC BY-SA, Wikimedia dumps |
| 5 | **Basic English 850 (Ogden)** | Tiered (850 core / 1500 extended) | Yes | Documented rule-based grammar (18 verbs + preposition combinators) | 850 words | Public domain (1930), full text at archive.org |
| 6 | **VOA Special English word book** | Single tier (~1500 words) | Partial (flat list, not sub-graded) | Documented simplicity rules (1 idea/sentence, no idioms) | ~1,500 words | Freely published (manythings.org, Simple Wikipedia mirror) |
| 7 | **CHILDES (raw) + childes-db** | No native grading (MLU calculator as proxy) | No direct list, but derivable | No | 436 corpora / 48 languages (2024) | Free but login-gated (raw); childes-db (tabular) no login found; CC BY-NC-SA |
| 8 | **Bernstein-Ratner (Brent&Cartwright phonemicized CDS)** | N/A — segmentation benchmark, not vocab curriculum | N/A | N/A | 9,790 utterances / 33,399 words | Free, CHILDES derived corpus |
| 9 | **Kuperman AoA norms 2012** | Yes — AoA-in-years is itself the order key | Yes (30,121 words) | No | 30,121 words | Free, CC BY 4.0, canonical bare CSV link unconfirmed this cycle |
| 10 | **Wordbank / MacArthur-Bates CDI** | Yes — per-word %-producing-by-month curve | Yes, esp. earliest ~400 words | No | 92,771 children / 105,290 administrations | Free via `wordbankr`, no login found |
| 11 | **Children's Book Test (CBT)** | No (POS-category tagged, not level-tagged) | No | No | ~600K+ examples | Open, GFDL, HF/GitHub — but text is upper-tier (Anne of Green Gables-era), not primer-level |
| 12 | **WikiLarge/WikiSmall/TurkCorpus/ASSET** | No native grammar-stage tagging | No | Implicit (simplification pairs), needs post-hoc complexity scoring | 100K-2M+ sentence pairs | Open, GitHub/HF |
| — | Oxford Reading Tree | Yes (Levels 1-20, public taxonomy) | Yes | Yes | proprietary | **Book text PAYWALLED — confirmed, do not budget** |
| — | Reading A-Z | Yes (29 levels) | Yes | Yes | 1,500+ titles | **Fully paywalled, no API — confirmed, do not budget** |
| — | Lexile Framework | Yes (continuous scale) | No (frequency-based, proprietary) | No | ~600M-word private corpus | **Proprietary — only sample-title map public** |

---

## 2. The from-zero curriculum plan (the ladder rungs)

Synthesizing the developmentally-faithful biology (Saffran, Brown, PT, CDI milestones) with the statistically-learnable literature (Tolerance Principle, type-frequency productivity):

**Rung 0 — statistics-only bootstrapping (no vocabulary, no grammar, no labels).** Pure distributional/transitional-probability segmentation over a raw phoneme/character stream. Validate against the Bernstein-Ratner benchmark (real infant-directed speech, ground-truth word boundaries, decades of published baseline scores). Exit criterion: segmentation accuracy within known baseline range on held-out Bernstein-Ratner data.

**Rung 1 — smallest grounded vocab seed + simplest grammar.** ~50-100 words = Dolch Pre-K+K tiers (92 words) or Basic English's tightest core, paired with SVO declarative present-tense sentences only (Simple Wikipedia's own floor). Matches Wordbank's ~50-word productive-vocabulary milestone (the master map's cited onset threshold) and PT's canonical-SVO-as-axiomatic-starting-point. Exit criterion (Tolerance Principle candidate gate): error rate on held-out rung-1 probes falls under `e <= N/ln(N)` relative to exemplars seen.

**Rung 2 — vocabulary scale-up + single-constituent morphology.** Add Dolch 1st/2nd-grade tiers (+87 words) and Fry's next frequency bands; introduce plural -s, present progressive -ing, articles a/the (Brown's earliest morphemes, PT's "category procedure" stage) — still no cross-constituent agreement. Matches Wordbank's ~200-300-word grammar-burst milestone.

**Rung 3 — cross-constituent agreement + tense expansion.** 3rd-grade Dolch/Fry tiers + CEFR-J A1-A2 band; introduce subject-verb agreement, past tense -ed/irregular, possessive 's (Brown's later morphemes, PT's "S-procedure" stage — explicitly gated on rung 2's category-procedure mastery per Pienemann's implicational hierarchy, not just age/volume).

**Rung 4 — clause embedding + adjectives + broader vocabulary.** CEFR-J A2-B1 band; introduce one subordinate clause max (Simple Wikipedia's own ceiling before graduating out of "simple" register), comparative/superlative adjectives (Basic English's -er affix rule), prepositional/adverbial combinators (Basic English's 18-verb + preposition compositional pattern as a design template for a constrained-then-expanding verb inventory).

**Rung 5+ — open-ended expansion.** CEFR-J B1-C2 bands, compound-complex sentences, full open grammar — past this point the ladder converges with general-purpose text (Gutenberg, general Wikipedia), no longer needing a controlled progression.

This ladder is explicitly a PRIOR to validate, not a fixed truth — Prediction 1/2/3 above are exactly the tests that check whether following it (vs. scrambled) measurably helps the substrate's own gate signal.

---

## 3. Glass-box fit (which corpus supports the early glass-box/VSA-native rungs vs. which is too noisy)

**Best fit for the earliest, cleanest, rule-tractable rungs (0-2):**
- Dolch/Fry word lists — flat, closed, small, exactly-enumerable sets; trivially glass-box (finite vocabulary, countable exemplars, deterministic grading).
- Basic English 850 — closed verb set (18 operators) + compositional preposition rule = maximally rule-tractable grammar, by design (Ogden built it to be teachable via a small explicit rule list).
- Simple English Wikipedia's house-style grammar rules — an explicit, small, enumerable rule list (no passive, no contractions, one clause max) rather than emergent statistical regularity; ideal for a glass-box rung because the "rule" IS the corpus's construction principle, not something to be inferred.
- Bernstein-Ratner phonemicized CDS — clean because it isolates ONE mechanism (transitional-probability segmentation) with zero confounding semantic content, matching a rule-tractable statistics-only rung.

**Progressively noisier / less glass-box-tractable (rungs 3+):**
- CEFR-J B1+ bands — real, richly attached content, but grammar variety broadens past simple enumerable rules.
- CBT — genuinely noisy relative to a primer: Anne-of-Green-Gables-era prose vocabulary/syntax is closer to independent middle-grade reading than an emergent-reader rung; useful as a LATER, not a FIRST, rung.
- CHILDES raw transcripts — real, richly naturalistic, but disfluent/fragmentary conversational speech (interruptions, ellipsis, false starts) is harder to grade cleanly than curated written text; best used for the statistics-only Rung 0 (where naturalism is the point) rather than for vocab/grammar rungs 1+ (where clean enumerable structure is the point).
- WikiLarge/TurkCorpus/ASSET — useful only after post-hoc syntactic-complexity scoring (no native grammar-stage tags); an assembly cost, not a plug-and-play fit.

---

## 4. The smallest starting corpus

**The single cheapest concrete starting point: Dolch Pre-K + Kindergarten sight-word tiers (92 words total) + a small hand-built (or Simple-Wikipedia-style) SVO present-tense sentence template set.**

Why this over CEFR-J or Basic English 850 as the literal FIRST artifact: Dolch's Pre-K/K tiers are the smallest (92 words vs. 850), already exactly match Wordbank's ~50-100-word early-productive-vocabulary milestone (the master map's own cited onset threshold), require zero transcription-format decisions (short enough to hand-encode directly), and zero licensing question (unambiguously public domain since 1936/1948, unlike Fry's ambiguous status).

**First 2-3 rungs concretely:**
1. **Rung 1a:** the 92 Dolch Pre-K+K words + Simple-Wikipedia-style SVO present-tense sentences only ("The dog runs.", "I see the cat."). No morphology beyond bare present tense and plural where the word list requires it.
2. **Rung 1b (bridge):** add the 95 Dolch nouns list (concrete, high-imageability content words — natural grounding-seed candidates, pairs with the master map's "small grounded seed set" stage) while holding grammar constant at SVO-present.
3. **Rung 2:** add Dolch 1st-grade tier (41 words) + introduce present progressive -ing and plural -s morphology (Brown's earliest two morphemes / PT's category-procedure stage), still no cross-constituent agreement.

This gives an immediately buildable, zero-friction, fully-public-domain starting artifact that plugs directly into the early-reader glass-box probe if Prediction 1's cheap decisive test (section b) passes.

---

## Deflated P estimates (capped 0.50 per novel-synthesis rule)

- Prediction 1 (Dolch/Fry+Simple-Wikipedia curriculum order beats scrambled on vocab+grammar axis): **P=0.32**
- Prediction 2 (PT implicational hierarchy gates grammar-rung advancement better than flat sequencing): **P=0.30**
- Prediction 3 (CDS-frequency order beats adult-frequency order): **P=0.28**

**Headline composite P (a real graded-corpus assembly materially strengthens the language-curriculum test over ad hoc/synthetic ordering): P=0.35** (deflated per lit-scan calibration penalty; matches the sibling fact-order note's composite exactly, and for the identical honest reason — real content/order artifacts here are pedagogically-conventional rather than mechanistically-validated dependency structures, so the ordering signal's strength relative to a carefully hand-built synthetic curriculum remains a genuinely open, untested question).

---

## (f) Citations (verified count: 3 parallel live lit-scans, ~40+ distinct sources/repos/papers cross-checked)

**CHILDES / AoA / statistical learning:** MacWhinney, CHILDES/TalkBank (talkbank.org/childes); childes-db (childesr/childespy packages); Kuperman, Stadthagen-Gonzalez & Brysbaert 2012, Behavior Research Methods 44(4) (30,121-word AoA norms, NORARE/CLDF hosting); 2024/2025 extension paper (PMC12500800); 44k test-based AoA norms paper; SUBTLEX-US (Brysbaert & New, expsy.ugent.be); Wordbank (Frank et al., wordbank.stanford.edu; wordbankr GitHub); MacArthur-Bates CDI; Saffran, Aslin & Newport 1996 Science; Aslin, Saffran & Newport 1998; Brent & Cartwright 1996 phonemicized Bernstein-Ratner corpus (talkbank.org derived corpora); Goldwater et al. Bayesian segmentation; Jones et al. 2023, Journal of Child Language (CDS-frequency vs adult-frequency as acquisition predictor).

**Graded readers / sight words:** Hill et al. 2016 arXiv:1511.02301 (CBT, "Goldilocks Principle"); HF cam-cst/cbt, cbt datasets; Oxford Owl / Oxford Reading Tree level documentation; Learning A-Z (Reading A-Z); MetaMetrics Lexile whitepaper + Lexile Map; Standardized Project Gutenberg Corpus (PMC7516435); Bensaid et al. 2021 Children's Stories Text Corpus; BabyLM Challenge findings (arXiv:2504.08165) and BabyBabelLM (arXiv:2510.10159); Dolch 1936 Elementary School Journal ("A Basic Sight Vocabulary"), Wikipedia Dolch word list, sightwords.com, dolchsightwords.org; Fry word list (various educator-site PDFs); Simple English Wikipedia `Wikipedia:HOW`, `Wikipedia:Basic_English_ordered_wordlist`, Category:Basic English 850 words; Ogden Basic English (archive.org); Kaggle Plain-text-Wikipedia-SimpleEnglish; Xu et al. ASSET (arXiv:2005.00481); jantrienes/text-simplification-datasets GitHub (WikiLarge/WikiSmall/TurkCorpus).

**Grammar order / SLA sequencing:** Brown 1973 (14-morpheme order); Cazden 1968; de Villiers & de Villiers 1973 ("approximately invariant?", J. Psycholinguistic Research); Rice et al. 2010, Pavelko & Owens 2017 (SUGAR norms); Dulay & Burt 1973/1974; Krashen Natural Order Hypothesis (critiques via SSLA L1-influence paper, McLaughlin 1987); Pienemann Processability Theory + Teachability Hypothesis (Wikipedia summary pages, Pienemann & Lenzing 2020/2024, Dyson 2009 longitudinal PT study); English Vocabulary Profile / CEFR-J Wordlist v1.5 (Tono, openlanguageprofiles/olp-en-cefrj GitHub); Maximax67/Words-CEFR-Dataset GitHub; Bybee 2013 usage-based theory; Goldberg 2006 construction grammar; Charles Yang Tolerance Principle (Frontiers in Psychology 2023, PMC10643500; De Gruyter critique); VOA Special English word book (manythings.org, americanenglish.state.gov); Ogden Basic English grammar rules (archive.org, Britannica).

---

## Status

Written per research-agent contract. No cap_map or strategy files modified. No `exp_dev_handoff_*` / `strategy_request_to_*` routing files written (USER-locked discipline: ferry mechanism deprecated; this note IS the deliverable — the Director reads this directly and dispatches cell-authors).
