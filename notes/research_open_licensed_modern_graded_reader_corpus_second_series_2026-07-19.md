# Open-licensed modern graded-reader corpus: second series alongside McGuffey (identify + verify + plan)

Date: 2026-07-19. Research pass only -- NO download, NO staging, NO atoms banked, NO routing
files (per explicit task contract; ferry mechanism deprecated). 3 parallel Sonnet lit-scan
sub-agents dispatched (digital-library cluster / post-McGuffey PD readers / other-candidates
scan); this note is my synthesis + honest calibration on top of their raw findings.

## HEADLINE

No modern open-licensed source is a clean drop-in. The digital-library cluster (GDL,
StoryWeaver, African Storybook, Bloom, Let's Read) is real and bulk-accessible in one case
(**Bloom Library**, via the `sil-ai/bloom-lm` Hugging Face dataset -- ~2,633 English stories,
already plain text, per-item CC license metadata), but **every source in that cluster carries
unconfirmed-to-high translation-artifact risk** because they are all multilingual-authoring
platforms where English is frequently a translation target, not the origin language. The
"newer-than-McGuffey-but-still-PD" middle option (Elson/Beacon/Baldwin/Aldine/Winston) is
real but thin on Gutenberg (1-3 volumes per series; full ladders need Internet Archive OCR)
and **does not meaningfully deliver contemporary vocabulary** -- it is still 100-120-year-old
schoolbook prose, only modestly less archaic than McGuffey at best (Aldine's early volumes).
**Recommendation: do a near-zero-cost pilot pull of the Bloom English CC-BY/CC0 subset now
(it costs about an hour, is already on HF as clean text, and is genuinely useful for the
generalization-test goal), but DEFER the larger acquisition/staging lift** (StoryWeaver/GDL/
African Storybook scraping, Elson/Beacon/Baldwin OCR) until the parser's current 0.557
bottleneck is shown to be corpus-composition-limited rather than mechanism-limited -- right
now the bottleneck is squarely mechanism (structural-signals-work/semantic-fails per the
3x-VET-confirmed reading-axis finding), and a second corpus does not touch that.

## Cheap decisive test

Before committing to ANY staging effort: pull the `sil-ai/bloom-lm` English split via
`datasets.load_dataset`, and run three checks that are each <1 hour of work:
1. **License-mix check**: tabulate the per-item license field across the English split. What
   fraction is CC-BY / CC0 (unrestricted for our use) vs CC-BY-NC (fine for internal research,
   flag if we ever want to redistribute) vs CC-BY-ND (restricts derivative/modified
   redistribution -- may still be fine for *internal, non-redistributed* cleaning, but flag).
2. **Origin-language check**: inspect the dataset schema for an `originalLanguage` or
   `sourceLanguage` field (Bloom's authoring model records this per-book on bloomlibrary.org
   metadata). If present, filter to English-original only and re-measure size.
3. **Spot-check 20 stories** by hand for (a) translation-artifact phrasing (calques, unnatural
   collocations, non-native word order) and (b) contemporary vs stilted vocabulary, and run
   the SAME stdlib stats used for the McGuffey ladder (words/passage, mean/median sentence
   length, COMP-density, pronouns/100w) so it is directly comparable to the existing table in
   `notes/graded_reader_corpus_staging_mcguffey_2nd_3rd_4th_wild_text_composition_2026-07-18.md`.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS (stage it):** >=70% of the English split is CC-BY/CC0 (non-NC/ND) usable text
AND <=2 of 20 spot-checked stories show clear translation artifacts AND mean words/story >=80
(enough for multi-entity, multi-relation composition -- the same richness threshold that made
McGuffey 2nd Reader work over the Primer). If origin-language metadata exists and English-
original filtering still leaves >=500 stories, that is a genuine second independent series.

**HARD-FAIL (deprioritize the whole digital-library cluster, don't stage):** license mix is
predominantly NC/ND (<50% cleanly usable) OR >=30% of spot-checked stories show translation
artifacts OR mean words/story <40 (reproduces the McGuffey-Primer thinness problem that
already forced an authored test once). Either failure mode means the cluster fails on the
SAME axis the McGuffey ladder was staged specifically to fix (richness) or introduces a new
confound (non-native syntax) that would make a "generalization test" un-interpretable --
a parser failure on translated-English prose would be ambiguous between "doesn't generalize"
and "correctly flags non-native syntax," which defeats the test's purpose.

## Cross-thread synthesis

This connects directly to `notes/graded_reader_corpus_staging_mcguffey_2nd_3rd_4th_wild_text_composition_2026-07-18.md`
(the staging pattern this note is asked to mirror) and to the current reading-axis state
(reader true-stacked precision 0.500->0.557, structural-signals-WORK / semantic-signals-FAIL,
3x-VET-confirmed, clean structural levers EXHAUSTED). That finding matters for deliverable #4
below: the open question right now is a PARSER mechanism gap (semantic grounding), not a data
gap. A second corpus is a real, independent lever (de-risks McGuffey-overfitting, which is a
legitimate methodological concern for any single-author/single-era corpus), but it is a
LATER-STAGE lever relative to the mechanism work in flight.

## 1. Ranked shortlist (per-source detail)

License-verification confidence is reported per the sub-agents' actual fetch success --
several platform pages returned 403/empty-render, so some claims rest on secondary sourcing
(search snippets, third-party HF dataset docs) rather than a directly-fetched primary page.
Flagged UNCONFIRMED where that applies; do not treat UNCONFIRMED as false, but do not stage
before resolving it either.

### Rank 1 -- Bloom Library (SIL International), English subset via `sil-ai/bloom-lm` (HF)
- **License**: bloomlibrary.org Terms set community-contributed default to CC BY-NC 4.0, BUT
  the HF-redistributed dataset carries **per-item** license metadata (CC BY 4.0, CC BY-NC 4.0,
  CC BY-ND 4.0, others) -- varies per book, filterable. Verified at dataset-doc level:
  https://huggingface.co/datasets/sil-ai/bloom-lm , https://bloom.sil.org/terms .
- **Leveling**: no reading-level field found in the dataset docs -- UNCONFIRMED / likely
  absent. Not a graded series in the leveled sense; would need our own SL/word-count binning
  (same stdlib metric already used for the McGuffey ladder).
- **Genre**: narrative (dataset examples show fictional characters, plot) -- CONFIRMED.
- **Size**: English split ~2,107 train + 263 val + 263 test = ~2,633 stories. Total word count
  NOT confirmed by the sub-agent scan -- picture-book stories typically run 100-500 words, so a
  rough (UNCONFIRMED) estimate is 260K-1.3M words total; needs a direct count before relying on
  it for size planning.
- **Bulk mechanism**: BEST of all sources scanned -- already plain text, one HF
  `load_dataset` call, no scraping required.
- **Translation-artifact risk**: UNCONFIRMED severity but plausible -- Bloom's core authoring
  model is local-language-first with translation outward (including into English), and the
  dataset schema does not obviously disambiguate original-language per item in what the
  sub-agent could access. This is the single most important unresolved question before
  staging -- see cheap decisive test above.
- **Contemporary vocabulary**: plausible (modern platform, contemporary children's-book
  register) but NOT spot-checked against source text in this pass (fetch access issues) --
  UNCONFIRMED, first thing to check in the pilot.

### Rank 2 -- StoryWeaver (Pratham Books)
- **License**: CC BY and CC BY-SA, per-item, per Pratham's own CC page
  (https://prathambooks.org/cc/); the platform's own `/open-content` and `/reading-levels`
  pages returned 403 on direct fetch this session -- license CONFIRMED at a primary-adjacent
  source, exact leveling scheme UNCONFIRMED from primary page (secondary sourcing describes
  "six reading levels for Grades 1-3").
- **Genre**: narrative picture-book stories.
- **Size**: ~34,000+ stories, 300+ languages claimed by Pratham -- by far the largest scale
  of any candidate, UNCONFIRMED English-only count.
- **Bulk mechanism**: no official bulk API/dump found; independent researchers reportedly used
  "a mix of web scraping and public APIs" -- meaning acquisition would be nontrivial
  engineering effort, not a one-call pull. This is why it ranks below Bloom despite larger
  scale.
- **Translation-artifact risk**: real and unresolved -- StoryWeaver is bidirectionally
  multilingual (original-English and original-Indian-language-then-translated both exist);
  fraction of English titles that are translations is UNCONFIRMED.

### Rank 3 -- African Storybook Project (via GlotStoryBook HF dataset)
- **License**: varies per item -- CC BY, CC BY-NC, CC BY-NC-SA, and Public Domain all present
  in the GlotStoryBook per-file metadata (https://huggingface.co/datasets/cis-lmu/GlotStoryBook),
  corroborating the project's own "CC Attribution or Non-Commercial" framing
  (https://creativecommons.org/2017/05/22/african-storybook/). CONFIRMED varies-per-book.
- **Genre**: narrative (folktales, contemporary stories, poems, songs).
- **Size**: ~3,800 original titles + 7,266 translations across 236 languages as of March 2023
  (per Wikipedia citing project reporting) -- English-only count UNCONFIRMED.
- **Bulk mechanism**: second-best after Bloom -- GitHub mirror (`global-asp`) underlies the
  GlotStoryBook HF dataset, so a real bulk-text path exists.
- **Translation-artifact risk**: HIGHEST of all five digital-library sources. Authors are
  "mostly African educators" writing first in a local language, translated to/from English in
  both directions with no uniform direction and no verified per-title disambiguation. This is
  the source most likely to pollute a clean who-did-what syntax eval with non-native English
  phrasing -- deprioritize for the specific "clean eval corpus" use case even though bulk
  access is good.

### Rank 4 -- Global Digital Library (GDL)
- **License**: CC BY / CC BY-SA stated at https://digitallibrary.io/about/license/, varies
  per item, other Digital-Public-Goods-approved licenses also accepted -- CONFIRMED
  varies-per-book at a primary source.
- **Leveling**: numeric levels confirmed to exist (a "Level 2 = up to 600 words" topic page
  was found) but full range (commonly cited elsewhere as Levels 1-5) UNCONFIRMED from a
  primary page this pass.
- **Genre**: mixed narrative + thematic/informational -- not purely narrative.
- **Size / bulk mechanism**: book-count UNCONFIRMED; a developer/API page exists but returned
  no usable detail in this fetch -- bulk API existence UNCONFIRMED.
- **Note**: GDL is explicitly an aggregator and likely re-hosts Pratham/African-Storybook
  content, so there is real overlap/duplication risk with ranks 2-3 rather than fully
  independent material. Ranked below StoryWeaver/African-Storybook because its own bulk-access
  story is weaker and it probably isn't adding much genuinely new material.

### Rank 5 -- Let's Read (Room to Read / Asia Foundation)
- **License**: search-snippet evidence only (Terms/About pages rendered empty on direct
  fetch) suggests CC BY 4.0 is common per-book, with translations noted as user-submitted --
  **UNCONFIRMED at primary-source level** despite consistent secondary description.
- Leveling, size, bulk mechanism, translation-origin: all UNCONFIRMED -- this is the least
  independently verifiable source scanned. Do not rely on it without a follow-up direct-browser
  check (WebFetch was blocked by empty renders on multiple pages).

### "Newer-than-McGuffey-but-still-PD" middle option -- assessed, ranked below the modern cluster for the CONTEMPORARY-VOCAB goal, but genuinely useful for the SECOND-INDEPENDENT-SERIES goal with near-zero license/engineering risk
All five series pre-date 1929 (bar one ambiguous later edition) and are unambiguously PD-US;
Gutenberg coverage is thin (1-3 volumes per series), full ladders need Internet Archive
OCR:
- **Aldine Readers** (Spaulding/Bryce, 1906-1920s) -- PG #65323 (1st Reader), #68545 (2nd
  Reader) already available. **Best register of the five** -- child-centered, conversational,
  shorter sentences, a real (if modest) step away from McGuffey's diction. Still only 2 volumes
  on Gutenberg; 3rd Reader onward need Internet Archive OCR
  (https://archive.org/details/aldinereaders00brycgoog).
- **Elson Readers** (1909-1921) -- only Book 5 (PG #9106), Grammar School Lit. Book 4
  (PG #6963), and a follow-on Junior High Lit. Book 1 (PG #54825) on Gutenberg; Primer-Book 3
  are Internet Archive scans only. Note: the LATER "Elson-Gray Basic Readers" (1930/1936,
  the "Dick and Jane" precursor) has an unresolved copyright-renewal question for the 1936
  edition -- flag as ambiguous, do not assume PD without a renewal check.
- **Beacon Readers** (Fassett, 1912-1914) -- only Second Reader on PG (#15659); fairy-tale-
  heavy, less moralizing than McGuffey, register "somewhat less stilted" but still clearly
  early-1900s.
- **Baldwin Readers** (1897-1901) -- PG #51000 (5th Year), #36864 (6th Year), #30559 (8th
  Reader, distinct series w/ Ida C. Bender). Essentially SAME vintage/register as McGuffey's
  later editions -- does not meaningfully deliver "less archaic."
- **Winston Readers** (1918-1924) -- NOT found on Gutenberg or confirmed on Internet Archive
  at all; only bookseller/auction listings found. Would require original scanning effort --
  not a near-term option.
- **Honest read**: none of these is "contemporary vocabulary." They are 100-120-year-old
  schoolbook prose; Aldine is the one plausible register step down from McGuffey, and it's
  modest. Their real value is as a THIRD independent PD series (zero license risk, exact same
  proven acquisition pipeline as McGuffey) for the generalization test, not for modernizing
  vocabulary.

### Other candidates scanned and ruled OUT or flagged niche
- **Wikijunior / Simple English Wikipedia** -- CC BY-SA CONFIRMED, but expository not
  narrative -- disqualified for the narrative-preferred requirement (usable only as a
  secondary informational-text supplement, not this task's target).
- **Free Kids Books (FKB)** -- genuinely mixed: CC/PD-tagged subset exists and is
  self-labeled (https://freekidsbooks.org/license/), narrative, but modest scale (low
  hundreds of titles) and no bulk API -- real but small, niche candidate.
- **Children's Book Test (CBT, Facebook AI / Hill et al. 2016)** -- PD (built from Gutenberg
  classic children's literature -- Montgomery, Dickens, Andrew Lang fairy tales), bulk-
  available on HF, but NOT graded/leveled by design and NOT contemporary vocabulary (same
  archaic-classic-literature problem as the PD-reader cluster, arguably worse since it's adult-
  register literary prose, not schoolbook-simplified).
- **ajibawa-2023/Children-Stories-Collection (HF, Apache 2.0)** -- license genuinely open and
  scale is large (~0.9M stories), and vocabulary would be modern by construction -- BUT these
  are **LLM-generated synthetic stories, not human-authored text**. This directly conflicts
  with the motivating goal (the McGuffey staging note exists specifically to get RICH REAL
  passages after an authored/synthetic test had to be faked once already). Flag as
  DISQUALIFIED for this use case on epistemic grounds, not license grounds.
- **Unite For Literacy, ICDL, Newsela, CommonLit, ReadWorks, Reading A-Z/Learning A-Z,
  Fountas & Pinnell** -- all CONFIRMED copyrighted / access-restricted / NC-clause-limited at
  a primary source (Terms pages, licensing pages). These are the "free-to-read but not
  open-licensed" trap the task warned about. CommonLit is the partial exception (CC BY-NC-SA
  for original content) but most of its catalog is third-party licensed text explicitly
  excluded from that grant, and NC still disqualifies unrestricted use. **All OUT OF SCOPE.**
- **CK-12 Foundation** -- CC BY-NC (NC clause) and overwhelmingly STEM/informational content,
  weak at K-3 reading levels by the platform's own admission. Disqualified on genre + license.

## 2. Translation-artifact risk -- explicit per-source verdict

| Source | Original-English confidence | Risk verdict |
|---|---|---|
| Bloom Library | UNCONFIRMED (schema may have an origin-language field -- check before staging) | MODERATE, resolvable |
| StoryWeaver | UNCONFIRMED, bidirectional multilingual authoring | MODERATE-HIGH, unresolved |
| African Storybook | Authors "mostly African educators," local-language-first | HIGH -- deprioritize for clean eval |
| GDL | Aggregates the above, likely inherits their risk | HIGH (inherited) |
| Let's Read | Unverifiable this pass | UNKNOWN |
| Elson/Beacon/Baldwin/Aldine/Winston (PD) | Original English (US schoolbook authors) | NONE -- this is the one real advantage of the PD-reader cluster |
| CBT (Gutenberg classics) | Original English | NONE, but archaic register |

This table is the single most decision-relevant fact in this note: **the entire modern
digital-library cluster trades translation-artifact risk for contemporary vocabulary, while
the PD-reader cluster trades archaic vocabulary for zero translation risk.** No source in
either cluster gives BOTH contemporary vocabulary AND zero translation risk with confirmed
bulk access -- that combination does not exist among what was found. Bloom Library is the
closest approximation (bulk-ready, per-item-licensed, plausibly-original-English but
unconfirmed) and is why it ranks #1 despite the open translation question.

## 3. Acquire-and-stage plan for the top pick (Bloom Library English CC subset)

**Acquisition (can proceed independently of the reading-run safety pre-check):**
1. `pip install datasets`; `load_dataset("sil-ai/bloom-lm", "eng")` (or the correct config
   name -- verify exact HF config string at dataset-load time, the sub-agent scan did not
   confirm the precise `load_dataset` call signature).
2. Filter to license in {CC-BY, CC0} (exclude NC/ND for the cleanest redistribution posture;
   NC-only items can go in a clearly-marked separate pool if we want to retain them for
   internal-only use).
3. If an origin/source-language field exists in the schema, filter to English-original;
   record the drop-rate.
4. Dump to `data/corpora/bloom_english_cc/raw/` as one .txt per story, preserving per-story
   license + id + level(if any) in a sidecar `PROVENANCE.md`/manifest (same pattern as
   `data/corpora/graded_readers_graded/PROVENANCE.md`).

**Clean + level-normalize (mirrors `clean_gutenberg.py` pattern, needs a NEW small cleaner
since Bloom text has no PG boilerplate but may have front-matter/illustration captions to
strip -- different noise profile, same architecture):**
5. Write `clean_bloom.py` (stdlib): strip any illustration-caption markup, front-matter
   (title/author/publisher metadata rows if embedded in text field), normalize whitespace.
6. Run the SAME stdlib stats used for the McGuffey ladder (words/passage, mean/median SL,
   <=15w%, single-clause%, pnouns/100w, pronouns/100w, COMP-density) and place the resulting
   row in a comparison table alongside the existing McGuffey ladder.

**Stage location:** `data/corpora/bloom_english_readers/cleaned/`, mirroring
`data/corpora/graded_readers_graded/cleaned/`. LOCAL only -- no git-add, no origin push, no
remote-persist (same discipline as the McGuffey staging).

**Effort estimate:** the cheap decisive test (license/origin/spot-check) is <1 hour. Full
acquire+clean+stats for the CC-filtered subset is a half-day of scripting effort (new cleaner
is simpler than `clean_gutenberg.py` since there's no PG boilerplate, but the per-item license
filter and manifest bookkeeping adds some work). This is genuinely cheap relative to the
Elson/Beacon/Baldwin OCR path (which requires Internet-Archive-scan OCR + cleanup, a
materially larger lift) and relative to StoryWeaver/African-Storybook (scraping-heavy, no
confirmed bulk API).

**Note on USING it:** per task framing, foundation-growth (feeding this corpus into the
reader's knowledge-growth loop) waits on the reading-run safety pre-check already gating that
thrust. ACQUISITION and STAGING (this plan) do not touch that gate and can proceed
independently -- staging produces an inert corpus on disk, not a foundation-growth event.

## 4. Honest bottom line -- is this worth doing NOW?

**Deflated recommendation: acquire the Bloom pilot now (near-zero cost, <1 day), defer
everything else.** Reasoning:

- The reader is currently bottlenecked at 0.557 who-did-what precision by a MECHANISM gap
  (structural-signals-work / semantic-signals-fail, 3x-VET-confirmed, clean structural levers
  exhausted) -- this is a parser problem, not a corpus-composition problem. A second corpus
  cannot fix a semantic-grounding gap; it can only (a) give more contemporary vocabulary for
  whatever mechanism eventually reads it, and (b) provide a generalization-test SECOND SERIES
  to de-risk McGuffey-overfitting once the parser is good enough for that test to be
  informative.
- Goal (b) -- the generalization test -- is only actionable once the parser has a real
  precision number worth stress-testing for overfitting. At 0.557 on grade-2/3, running a
  cross-series generalization test now would mostly measure "does the parser transfer across
  ANY new text" rather than "does it overfit to McGuffey specifically" -- those are different
  questions and the current state is too early to cleanly separate them. So the FULL
  generalization-test use case is premature.
- However, the Bloom pilot is cheap enough (<1 day, no scraping, HF dataset already exists)
  that deferring ACQUISITION specifically (as opposed to the full ladder-widening effort)
  has no real justification -- it costs almost nothing to have the raw material staged and
  ready, and the license/translation-risk questions need answering regardless of when we use
  it. Acquiring now and using later is strictly better than acquiring later, given the
  marginal cost is near zero and the parser-improvement work is unaffected.
- Do NOT invest in StoryWeaver/African-Storybook/GDL scraping or Elson/Beacon/Baldwin OCR at
  this time -- those are real multi-day-to-multi-week efforts (scraping engineering or OCR
  cleanup) for sources that either carry unresolved translation risk (digital-library cluster)
  or don't meaningfully deliver contemporary vocabulary (PD-reader cluster). Revisit if/when
  (a) the parser mechanism gap closes enough that a real cross-series generalization test
  becomes informative, or (b) the Bloom pilot's spot-check comes back clean and we want more
  scale than ~2,600 stories provides.

P_deflated on "Bloom pilot clears the HARD-PASS bar": ~0.45 (lit-scan calibration penalty
applied; genuinely uncertain until the origin-language field is checked directly -- this is
not a novel-synthesis claim so the 0.50 cap doesn't bind, but confidence is capped by the
UNCONFIRMED translation-risk question, which is the dominant uncertainty).

## Citations (verified count)

Distinct primary/secondary sources cited across the three sub-agent scans and this synthesis:
**~35 URLs** (Gutenberg ebook pages, Internet Archive scans, Hugging Face dataset pages,
platform Terms/License pages, Wikipedia/CreativeCommons.org background, licensing pages for
the ruled-out commercial sources). Full URL list is inline above per-source; not
independently re-verified by the synthesizing pass beyond spot-checking that sub-agent URLs
resolve to the claimed domain (not re-fetched). Several platform pages (StoryWeaver
open-content/reading-levels, Let's Read Terms/About) returned 403/empty-render during the
scan and are marked UNCONFIRMED throughout rather than silently treated as verified.
