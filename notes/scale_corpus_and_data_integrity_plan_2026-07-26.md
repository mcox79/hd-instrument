# Scale-corpus + data-integrity plan — feed the encoder real experience at scale

Filed by: research (Sonnet lit-scan + on-disk empirical measurement, this session). READ-ONLY scoping — no cells built, no training run launched.

## HEADLINE

The AI2 **ARC_Corpus.txt** (`data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt`) is **already on disk, unzipped, ready to use**: 1.4GB, 14,621,856 sentences, **237.7M measured alpha tokens**. Measured THIS SESSION against the exact 24,275-concept single-token vocabulary pulled from `cskg_foundation_v1` (degree>=2, matches the charter's "~25k grounded single-token concepts," 53.7% cross-referenced against Lancaster experiential norms): **median 376 mentions/concept**, 68.1% of concepts at >=100 mentions, only 2.33% at zero. The prior data-starved deep-text run (`exp_deep_text_encoder_self_teacher_heldout_new_v1`) trained on **265,273 tokens total / mean 3.07 mined sentences per concept** — this corpus is a **~900x token-count increase and ~100x+ mentions-per-concept increase over the exact failure point**, obtainable with zero download step. Recommend it as the FIRST scale-up corpus.

## 1. Corpus options

### Already on disk (measured this session unless flagged)

| Corpus | Path | Size / tokens | Domain | Cleanliness | License | Verdict |
|---|---|---|---|---|---|---|
| **ARC_Corpus** | `data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt` | 1.4GB, 14.62M lines, **237.7M alpha tokens (measured)** | Broad elementary/middle-school science (search-engine results for science search terms + Wiktionary defs + Simple-Wikipedia science pages tagged by AI2) | MODERATE — sentences are individually shuffled out of source documents ("randomly sorted" per README), no paragraph coherence; contains junk fragments (bibliographic stubs like `Paleoceanography, 8(2): 193-208.`) and noise lines | **AI2 ARC Corpus (Clark et al. 2018)** — non-commercial research use only, no redistribution, no extracting individual documents. Fine for this internal research project; NOT fine to redistribute or ship externally. | **RECOMMENDED FIRST CORPUS** |
| `textbook_concepts_biology` (OpenStax Concepts of Biology) | `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt` | 224,656 words | Coherent biology-textbook prose, real paragraph structure | HIGH — already cleaned from CNXML | CC BY-NC-SA 4.0 (verified in PROVENANCE.md; NOT CC BY as originally assumed) | Small alone (same order as the failed run) but HIGH-QUALITY coherent context — good phase-2 supplement for paragraph-level discourse ARC_Corpus lacks |
| `mcguffey_readers` | `data/corpora/mcguffey_readers/` | ~378,644 words | 19th-c. graded primers, grade 1-6 | HIGH, public domain | Public domain | Small; useful for curriculum-order (grade progression), not scale |
| `onestop` (OneStopEnglish) | `data/corpora/onestop/` | 1.6GB on disk but mostly CoreNLP/parser output bloat; raw text is ~150-190 articles x 3 reading levels (not separately measured — flag for follow-up) | News articles at 3 simplification levels | HIGH | CC BY-SA 4.0 (verified LICENSE.markdown) | Same content x3 levels — good for curriculum/leveled-difficulty, weak scale driver (measure raw-text-only word count before relying on it) |
| `graded_readers_grade1` / `graded_readers_graded` | `data/corpora/graded_readers_*` | ~26.7k / ~208k words | Graded reading material | HIGH | Not verified this session | Small, curriculum-order use only |
| `race` | `data/corpora/race/` | test splits only present (middle_test.jsonl, high_test.jsonl); ~1.5M words incl. JSON overhead | Exam reading-comprehension passages (RACE benchmark) | Copyrighted academic benchmark, typically non-commercial-research license | Small, eval-only value (comprehension probe), not a training-scale source |
| `worldtree` (WorldTree Explanation Corpus v2.1) | `data/corpora/worldtree/` | curated tablestore of short explanatory facts (thousands, not millions, of rows) | Science-QA explanation sentences | HIGH — curated, vetted | AI2 (non-commercial research, per EULA doc in the dir) | Small, high-precision; domain-matched anchor sentences, not a scale driver |
| CSKG `sentence` column | `data/grounding_testbed/cskg.tsv.gz` | up to ~1.24M edges -> up to ~1.24M short **templated** sentences (`"[[0]] is the [[empty set]]."`) | Template-generated FROM the relational KB itself | Not natural prose — synthetically generated, zero linguistic variety | Inherits CSKG source licenses (mixed CN/ATOMIC/VG, research use) | Useful ONLY as a text<->KB fusion bridge; training on it is partially training on the KB restated as prose — must NOT be counted toward the "real text experience" scale claim (see integrity check 2f) |
| WordNet gloss + example caches | `data/wordnet_gloss_cache_v1.json` (25,312 lemma->gloss, ~2MB), `data/wordnet_examples_cache_v1.json` (~1.5MB) | ~500k-700k tokens total (1-2 clean sentences/concept) | Dictionary-quality single definitions | HIGHEST precision, zero noise | WordNet license (permissive) | Same order of magnitude as the FAILED run — confirms this alone was never going to be enough; use as a per-concept anchor/floor, not the scale source |

### Would need download (not verified on-disk; sizes web-checked this session, hedge as approximate)

| Corpus | Rough size | Domain | Cleanliness | License | Obtain |
|---|---|---|---|---|---|
| **Simple English Wikipedia** | Small subset of full Wikipedia (~100-200M tokens, not independently verified) | Simplified encyclopedic prose across all topics | HIGH after WikiExtractor cleaning | CC BY-SA 3.0/4.0 + GFDL, fully permissive/redistributable | `dumps.wikimedia.org/simplewiki` + WikiExtractor | **Strong phase-2 candidate**: same simplified register ARC_Corpus itself partly draws from, broader topic coverage than science-only, clean license |
| Full English Wikipedia | ~16GB uncompressed raw wikitext (verified via GitHub/evanjones.ca sources this session); commonly-cited clean-extracted scale is several billion tokens | Full encyclopedic breadth | HIGH after extraction, needs WikiExtractor pipeline | CC BY-SA + GFDL, permissive | `dumps.wikimedia.org/enwiki` | Bigger than needed for this step; keep as phase-3 scale reserve |
| Project Gutenberg (full/"Standardized PG Corpus") | Tens of thousands of books, commonly-cited ~3B+ words for large subsets | Narrative/literary English, general vocabulary | HIGH, cleanest license of any option | US public domain | gutenberg.org bulk mirrors | Best GENERAL-vocabulary source, but domain-mismatched to the WorldTree/ARC science concept set; good for a later general-vocabulary phase |
| OpenWebText | ~38GB, ~9B tokens (web-checked) | Mixed web register (Reddit-linked pages) | Noisy, heterogeneous | Ambiguous/gray-area (not an explicit redistribution grant) | huggingface/openwebtext mirrors | Not recommended first — noisy + license friction for a product-facing project |
| C4 | ~750GB, ~170-220B tokens (web-checked, wide variance by tokenizer) | Heterogeneous Common Crawl web text | Cleaned but still noisy relative to curated sources | ODC-BY (AllenAI TFDS release) | TFDS `c4` dataset | Overkill scale for this step; reserve for a later industrial-scale phase if ever needed |
| BookCorpus | ~7,000 books, ~985M words (web-checked) | Fiction/narrative | Moderate | **LEGALLY CONTESTED** — scraped from Smashwords without author permission, original take-down, later reproductions carry legal risk | avoid direct download | **DO NOT USE** for a product-facing project |
| News dumps (CC-News etc.) | Varies, GBs-scale | News register | Moderate, heavy duplication (wire-service syndication) | Usually copyright-restricted | Various | Not recommended — licensing friction, register mismatch |

**Recommendation:** ARC_Corpus.txt now (zero download, on-disk, domain-matched, license fine for internal research), textbook_concepts_biology + worldtree + mcguffey/graded-readers as a small coherent-prose supplement (fixes ARC_Corpus's shuffled-sentence lack of discourse structure), and Simple English Wikipedia as the natural phase-2 download if phase-1 beats the starvation wall and more scale/breadth is wanted.

## 2. The data-integrity analysis (the crux)

### (a) Dedup / near-duplicate detection
ARC_Corpus's README states source *documents* were deduplicated before sentence-extraction, but the released artifact is single sentences pulled from many documents and randomly re-sorted — sentence-level near-duplicates (boilerplate, repeated citation stubs, template headers/footers) are NOT guaranteed removed. Preflight: exact-line-hash dup-rate on the full file (cheap, one pass) + MinHash/5-gram-shingle Jaccard near-dup rate on a sample (standard C4/GPT-3-pipeline technique). Collapse anything above a chosen Jaccard threshold (e.g. >=0.8) before it inflates any concept's apparent mention count with copy-pasted junk.

### (b) Quality filtering (boilerplate/junk/non-English removal)
- Length filter: drop lines under ~4 tokens (kills list-fragments).
- Character-heuristic filter (the standard C4-pipeline heuristics): drop lines with excessive digit/symbol ratio, no terminal punctuation, or matching junk patterns.
- Citation-fragment filter: regex-flag `Author, Year; Vol(Issue): pages`-shaped lines — we directly observed one in the raw sample (`Paleoceanography, 8(2): 193-208.`); ARC_Corpus was built from search-indexed science documents, which routinely include bibliography fragments.
- Language-ID filter as a backstop (fastText langid or a stopword-ratio heuristic) even though the corpus is nominally English-only.
- Cheap sanity signal already run: the corpus's top-20 most frequent tokens are all ordinary English function words (`the, and, a, to, in, is, for, are, with, it, ...`) — a good sign the corpus is not junk-dominated, but this alone does not substitute for line-level filtering.

### (c) Coverage — mentions-per-concept (THE CENTRAL CHECK, already measured this session)
Method: vocab = single-token surface forms in `data/cskg_foundation_v1/nodes.jsonl` with `degree>=2` (24,275 concepts, matches the charter's "~25k grounded" figure; 53.7% independently cross-referenced against `Lancaster_sensorimotor_norms_for_39707_words.csv`, confirming this is substantially the same set the grounding layer already covers). Tokenize the corpus lowercase, alpha-only, count per-concept frequency.

**Measured result (ARC_Corpus.txt, single streaming pass, 82s):**
```
vocab_size: 24275
total_corpus_alpha_tokens: 237,666,846
zero_mentions: 566 (2.33%)
median_mentions_per_concept: 376
mean_mentions_per_concept: 6506 (skewed by high-frequency generic-noun concepts)
pct concepts with <5 mentions: 6.94%
pct concepts with <20 mentions: 15.74%
pct concepts with >=100 mentions: 68.14%
```
Inspected the zero-mention tail: `limnocryptes, vendicated, disraught, choriotis, xenorhyncus, rabbitwood, cyrilliaceae, aulacorhyncus, ...` — long-tail taxonomic Latin genus names and misspellings, i.e. genuine long-tail vocabulary gaps, not core-concept failures. This cross-validates that the foundation's own lexical-dilution cleanup left some genuine long-tail noise, an incidental but useful finding.

**Compare directly to the failure point:** the prior run (`exp_deep_text_encoder_self_teacher_heldout_new_v1/metrics.json`) mined `mean_mined_per_concept=3.07` sentences, `total_tokens_used=265,273` across 5,000 concepts (mean 53 tokens/concept) and scored near-chance (`raw_deeptext_alone=0.519`). ARC_Corpus alone gives a **~100x+ increase in median mentions/concept** and each mention carries a full-sentence context window, not a truncated 53-token ceiling.

Remaining gap: the bottom ~7% (<5 mentions) will stay undertrained on ANY single corpus of this kind — recommend excluding them from the primary held-out eval slice (evaluate separately, expected-low, not counted against the main hypothesis; conflating them would violate the fair-test discipline).

### (d) Tokenization from scratch (no borrowed vocab)
Train a BPE/unigram tokenizer (e.g. sentencepiece, ~8k-16k vocab, matching the scale the prior encoder used) FROM the training corpus itself, AFTER the held-out-concept scrub (below) is applied — the tokenizer must not see held-out concepts' text either, since subword-merge statistics learned from held-out text are a subtle leak channel (a held-out concept's characteristic segmentation could itself encode frequency/context information even if the encoder never sees surrounding tokens). This matches the brain-true framing: all statistics, sub-word AND semantic, come from the SAME exposure stream.

### (e) Train/eval leakage prevention — held-out-NEW-concept quarantine
This is the most important structural design point given this session's own circular-eval lesson (`WHERE_WE_ARE_NOW`: the apparent "+0.20 relational learning" result was a leak — the held-out concept's input context-set was bit-identical to its eval positive-set; degree-matching alone did not catch it).

1. **Concept-level, not edge-level, holdout.** Verified this session: `cskg_foundation_v1`'s existing split (`heldout_edges.jsonl`, 24,774 edges) is EDGE-level — its 15,728 unique subject-concepts still appear in the TRAINING edge shards under other relations. **This split cannot be reused as-is for a text-corpus run.** Build a NEW, disjoint concept-level holdout: pick N concepts (500-1000), stratified by mention-frequency bucket (avoids the "0-shared-neighbours pins metric by construction" bug that downgraded v3), and scrub EVERY corpus line mentioning that concept's surface form (and lemmatized/inflected variants — plain string match under-scrubs) from the training stream entirely.
2. **Verified-zero-overlap gate at build time**, in the same style as the leakproof relational-inference win's "no-overlap witness 0/22299": count, post-filter, how many training context windows contain a held-out surface form. Must be exactly 0 before any training run starts.
3. The held-out concept's own reserved sentences become the untouched eval-context source (consistent with the analogy/relational win's "context-given inference" scope), or, for a stronger zero-context bar, withheld entirely to test pure cross-modal transfer (relational KB + grounding norms, zero text exposure).
4. **The CSKG templated `sentence` column inherits the same exclusion list.** It is generated directly from the held-out edges already reserved in `cskg_foundation_v1` — if used as extra training text it silently reopens a closed leak channel unless it obeys the identical concept-level scrub.

### (f) Detecting construction-determined / contaminated results
Reuse the exact control battery that worked for the VET-confirmed relational-inference win (`leakproof_relational_inference_heldout_v1`):
- Context-shuffle control (shuffle which sentences are attributed to which concept slot, preserving corpus statistics) — a genuine text-meaning signal must COLLAPSE under this.
- Popularity/frequency-only baseline (predict from mention-COUNT alone) must be beaten.
- Random-init encoder baseline.
- Frequency-stratified eval (not just degree-stratified) to avoid a low-mention-biased eval slice mechanically favoring or disfavoring one arm.
- **CSKG-templated-sentence ablation**: run with and without the templated CSKG sentences in the training mix. If a win is driven mostly by the templated sentences (which are literally the KB restated as prose) rather than the freeform ARC_Corpus/textbook prose, that is a knowledge-restated-as-text artifact, not a genuine "learned from real experience" result — flag and downgrade accordingly.

## 3. Training-data shape

- **Context-window extraction**: for each concept mention surviving dedup/quality-filter/held-out-scrub, extract a symmetric sentence-boundary-respecting window (e.g. +/-32-64 tokens) as the concept's positive-context set for a predict-context / masked-token objective — the raw-text generalization of THE_PLAN's R3 "positives from the KB's own relational/gloss co-occurrence."
- **Three complementary signals to fuse**, per THE_PLAN's coupling and this session's VET-confirmed division of labor: (i) TEXT co-occurrence (this corpus) — untried at scale, the candidate fix for the "encoder earns ~0 beyond raw grounding on category/semantic" null; (ii) relational-foundation neighbourhood (`cskg_foundation_v1` edges) — VET-confirmed +0.108 over homophily on connection-inference; (iii) experiential grounding norms (Lancaster/Brysbaert/Warriner/Kuperman) — confirmed sufficient statistic for category placement. Text-context is the one signal not yet tested at real scale.
- **Architecture starting point**: reuse `exp_deep_text_encoder_self_teacher_heldout_new_v1`'s from-scratch transformer (n_layers=2, n_heads=4) as the baseline config, but pre-register model-capacity scaling as a joint variable with data scale — do not conflate an under-sized model with a data-integrity failure if the full run underperforms.
- **Curriculum ordering** (optional, cheap, brain-relevant): stage exposure by grade level (graded-readers -> mcguffey -> onestop-elementary -> ARC_Corpus mixed-grade) as a testable curriculum-order variable, not required for the primary test.

## 4. Success / can-fail

Reuse the exact leak-proof held-out-NEW-concept bar from `leakproof_relational_inference_heldout_v1`, now with concept-level text-holdout (2e) and a third TEXT-context arm evaluated on the identical held-out set for apples-to-apples comparison against the existing relational (+0.108) and grounding-homophily (0.546) numbers.

**Must-beat baselines** (unchanged from the existing pattern): raw-grounding-homophily, non-learned 2-hop relational, popularity/frequency-only, random-init, context-shuffle collapse control.

**HARD-PASS**: text-context arm beats raw-grounding-homophily by >= the same +0.03 margin already used in the prior deep-text prereg (`hp_margin_over_raw=0.03`), the shuffle-control collapses to within noise of the popularity baseline, holds across >=2 seeds, AND the text+relational+grounding fusion beats every single signal alone (proves genuine complementarity, not restatement).

**HARD-FAIL**: if the WELL-COVERED majority (concepts with >=100 mentions, 68.1% of the vocab per the measured coverage table) still shows <=0 margin over raw grounding at ~240M-token scale, that is strong evidence the null result from the 07-26 arc is OBJECTIVE-level (the encoder-migration geometry-collapse-at-scale problem named in THE_PLAN's "encoder migration HARD_FAILED") and NOT data-level. The data-scale hypothesis would then be REFUTED for this substrate, and effort should redirect fully to the R1 objective fix rather than sinking more budget into ever-larger corpora. Pre-register this fork explicitly before the full run.

**Expected mentions-per-concept scale to beat the starvation wall**: treating ~50-100 mentions/concept as a reasonable floor for a masked-context objective to differentiate a concept's distributional profile (a rule-of-thumb drawn from standard word2vec/GloVe minimum-frequency practice, not a substrate-proven number — hedge accordingly), ARC_Corpus already clears that floor for 68% of the vocabulary and gives partial signal (5-99 mentions) for a further ~25%; only the bottom ~7% (<5 mentions) remains genuinely under-covered and should be excluded from the primary eval slice, evaluated separately as an expected-low control.

## Cheap decisive test

Before committing to a full training run: (1) re-run the coverage-check script (already written and validated this session; portable, one CPU pass, ~82s on this corpus) as a formal preflight gate; (2) exact-dup + sampled near-dup rate check on the corpus, must be below a chosen threshold; (3) verified-zero-overlap leak check on the held-out-concept scrub (must report exactly 0 leaked context windows, same pattern as the existing "0/22299" witness); (4) a CPU-only qualitative canary — train the from-scratch tokenizer + a tiny 1-2-layer encoder on a 5-10M-token subsample for a few hundred steps and spot-check that nearest-neighbours of a handful of known concepts are semantically plausible. A failure at ANY of these four gates blocks the full run — cheap (CPU, minutes-to-an-hour) and decisive (catches contamination/leakage/under-coverage before spending the real compute budget).

## Cross-thread synthesis

- **Data-starved deep-text finding** (`WHERE_WE_ARE_NOW`): 265,273 tokens total, 53 tokens/concept mean, near-chance 0.519 raw-deeptext-alone. This plan's ARC_Corpus option is a ~900x token-count increase and ~100x+ mentions-per-concept increase, directly targeting the diagnosed "brain-difference = DATA SCALE" gap.
- **Circular-eval lesson** (bit-identical leak; degree-matching alone insufficient to catch it): directly shaped section 2e — concept-level scrub + a verified-zero-overlap build-time gate, not degree/frequency-matching alone.
- **VET-confirmed relational-inference win** (+0.108 over homophily, collapses under neighbour-context-shuffle, no-overlap witness 0/22299): the exact control-battery pattern (shuffle / popularity / random-init / collapse) is reused verbatim for the text arm in section 2f, and its "context-given inference, modest absolute AUC 0.65" scope-honesty is the template for how this plan states its own bar.
- **`cskg_foundation_v1`'s existing held-out split is edge-level, not concept-level** (measured this session: 15,728 unique held-out-edge subjects still present in training shards) — this plan cannot piggyback on that split; a new concept-level split is a required, non-optional build step, not a reuse.

## Substrate-product implications

If the coverage-driven hypothesis holds (text-context arm clears HARD-PASS on the well-covered majority), this closes THE_PLAN's front-line BLOCKER (encoder migration to real vocabulary) without any borrowed embedding — directly serves the north-star brain-true, no-shortcut meaning acquisition, and unblocks layer-1 REPRESENTATION to feed layer-3 REASONING. If it HARD-FAILs even at ~240M-token scale on the well-covered majority, that is a cheap, decisive way to REDIRECT effort fully to the R1 objective-geometry fix rather than continuing to spend budget on ever-larger corpora — the fork is pre-registered so the outcome is actionable either way, not just informative. Independent of outcome, the measured 24,275-concept x mentions-per-concept coverage table is a reusable substrate asset (same class as the prior `definitional_meaning_foundation_scale_audit`) for scoping every future "do we have enough real text for concept X" question.

## Calibration (per lit-scan calibration-penalty discipline)

P(text-scale hypothesis clears HARD-PASS on the well-covered majority) = **0.35** (deflated from a naive higher read; the prior encoder-migration HARD_FAILs at scale were diagnosed as OBJECTIVE-level, not data-level, so more data does not guarantee fixing an independent objective defect — this is the honest reason the HARD-FAIL fork above is pre-registered as a live, not token, outcome). This is a novel-synthesis design note, not a framework-P claim, so no cap-violation.

## Citations (verified count: 15)

**On-disk, measured this session (9):**
1. `data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt` + `README.txt` (size, line count, token count, license/terms-of-use, construction method — all read/measured this session)
2. `data/cskg_foundation_v1/nodes.jsonl` (482,588 nodes; 24,275-concept single-token vocab derived)
3. `data/cskg_foundation_v1/heldout_edges.jsonl` (24,774 edges / 15,728 unique subjects, edge-level-not-concept-level confirmed)
4. `data/cskg_foundation_v1/edges_shard_00.jsonl` (schema sample)
5. `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv` (53.7% vocab overlap measured)
6. `data/grounding_testbed/cskg.tsv.gz` (templated sentence-column sample)
7. `data/wordnet_gloss_cache_v1.json` / `data/wordnet_examples_cache_v1.json` (25,312 entries)
8. `data/corpora/textbook_concepts_biology/PROVENANCE.md` (license correction: CC BY-NC-SA 4.0, not CC BY)
9. `data/corpora/onestop/README.md` + `LICENSE.markdown` (CC BY-SA 4.0 confirmed)
10. `data/exp_deep_text_encoder_self_teacher_heldout_new_v1/metrics.json` (prior data-starved run: 265,273 tokens, 3.07 mined sents/concept, 0.519 raw-deeptext AUC)

**Prior notes (read this session):**
11. `notes/WHERE_WE_ARE_NOW_2026-07-26.md`
12. `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md`

**External, web-verified this session:**
13. AI2 ARC dataset / ARC Corpus construction (Clark et al. 2018), cited in the on-disk README
14. Vajjala & Lučić, "OneStopEnglish corpus..." ACL Anthology W18-0535 (2018)
15. Wikipedia-dump size + C4/OpenWebText/BookCorpus token-count figures (WikiExtractor GitHub / evanjones.ca; C4 documentation / Stanford CS324 data lecture / BookCorpus overview) — hedged as approximate, not substrate-critical
