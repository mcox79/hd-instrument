# Corpus composition audit -- is McGuffey (or any historical text) in the foundation?

USER concern (verbatim): "mcguffey is very old (like 200 years) so while we can use it to see
if our system works well on 200 year old prose, we shouldn't use it as a primary". Working
branch is literally named `dataprep/mcguffey-graded-corpus`. This audit reads the actual loader
code (not filenames/branch names) to settle it.

## Verdict, up front

**CONFIRMED: the director's working assumption is correct.** Zero McGuffey sentences (and zero
other pre-20th-century text) fed the v1-v4 reading-grounding-loop foundation (current head:
3544 GROUNDED_MEANING concepts, `data/exp_reading_grounding_loop_cycle2_v1/metrics.json`). The
branch name is a stale artifact from a data-prep task (`data/corpora/mcguffey_graded/` built
2026-07-31) that predates an explicit standing USER directive
(`feedback_stop_mcguffey_use_modern_sources_USER_2026-08-08`, verbatim "STOP USING MCGUFFEY -
IT'S FROM 200 YEARS AGO") which the reading-grounding-loop cell **already discloses and obeys**
in its own pre-reg -- this is not a fresh discovery, it's a documented, already-resolved
substitution that this audit independently re-verified from the code.

## 1. data/corpora/ enumeration (size, era, provenance evidence)

| dir | size | era | evidence |
|---|---|---|---|
| onestop | 1.6G | MODERN (2018 paper; Guardian-derived news, 3 levels) | `data/corpora/onestop/README.md`: OneStopEnglish corpus paper (Vajjala & Lučić 2018, ACL W18-0535), CC BY-SA 4.0 |
| textbook_concepts_biology | 58M | MODERN (2013 open textbook) | `PROVENANCE.md`: OpenStax "Concepts of Biology" (Fowler/Roush/Wise 2013), CC BY-NC-SA 4.0, fetched 2026-07-17 from `osbooks-biology-bundle` |
| process_articles_v1 | 512K | MODERN (curated science-process descriptions, prior task) | `process_articles.json`, no historical-era markers |
| base_vocabulary | 11M | MODERN (frequency list, not prose) | SUBTLEX+Dolch+Ogden+AoA frequency-ordered word list, used only as SEED not reading text |
| mcguffey_graded | 9.0M | **HISTORICAL** (~200 yr, McGuffey Eclectic Readers) | own `PROVENANCE.md`/manifest; built 2026-07-31 (BEFORE the 08-08 stop directive) |
| mcguffey_readers | 4.5M | **HISTORICAL** (same source, earlier prep) | same corpus, earlier (2026-07-21) prep pass |
| alice_in_wonderland, little_women, tom_sawyer, sherlock_holmes, wizard_of_oz, anne_of_green_gables | 1-5.5M each | **HISTORICAL** (1865-1915 Gutenberg classics) | dir names + content are the well-known public-domain novels |
| tinyshakespeare.txt | 1.1M | **HISTORICAL** (~1600s) | Shakespeare corpus, plain file at corpora root |
| litbank_coref_conll, litbank_ic_derived_v1 | 13M, 1.5M | **HISTORICAL** (LitBank = 100 classic English literary texts, coref-annotated) | standard LitBank release |
| agreement, arc, binder, breadth_v1, graded_readers_grade1/graded, mcscript2, race, simplewiki, social_iqa, ud_english_ewt, wiqa, word_image_early_vocab | 4M-2.1G each | MODERN (NLP benchmark/eval corpora: ARC, RACE, WIQA, SocialIQA, SimpleWiki, UD-EWT, McScript2, image-grounded vocab) | standard modern NLP dataset names/structure |

## 2. Segment-to-corpus map (read from `load_corpus()` in
`experiments/exp_definitional_grounding_v3.py` -> `build_curriculum_pool` in
`experiments/exp_reading_grounding_loop_cycle1_v1.py` + `SEGMENT_POOL_LOADERS` in
`experiments/exp_reading_grounding_loop_cycle2_v1.py`, cross-checked against MEASURED
`n_sentences` in `data/exp_reading_grounding_loop_cycle2_v1/metrics.json:segment_summaries`)

| segment | n_sentences (measured) | source corpus (from loader code, not filename) | era |
|---|---|---|---|
| bootstrap | 4640 | `onestop/.../Ele-Txt` files[0:50] + `Int-Txt` files[50:100] + ALL of `process_articles_v1/process_articles.json` | modern |
| ele_cont | 4623 | `onestop/.../Ele-Txt` files[50:189] | modern |
| int_cont | 4952 | `onestop/.../Int-Txt` files[0:50] + files[100:189] | modern |
| adv_new | 7408 | `onestop/.../Adv-Txt` files[0:189] | modern |
| bio_new | 4500 | `textbook_concepts_biology/cleaned/concepts_biology.clean.txt` (OpenStax) | modern (2013) |
| **total** | **26123** | -- | -- |

None of the four `SEGMENT_POOL_LOADERS` functions (`load_ele_continuation`,
`load_int_continuation`, `load_adv_new`, `load_biology_sentences`) nor `build_curriculum_pool`
reference `mcguffey_graded`, `mcguffey_readers`, or any other historical-corpus path. Grepped
and read line-by-line to confirm -- no inference from names.

## 3. McGuffey / pre-20th-century contribution to v1-v4 foundation: ZERO

- Sentences: 0 / 26123 (0%).
- GROUNDED_MEANING facts tracing to McGuffey via provenance: 0 / 3544 (0%) -- structurally
  impossible, since provenance (`source_sentences` on each fact) only ever contains sentences
  drawn from the pools above.
- The reading-grounding-loop cell's own pre-reg (`preregs/2026-08-12_reading_grounding_loop_
  cycle1_v1.md`, section "Corpus deviation from the spawning task's named corpora") states this
  explicitly: the SPAWNING TASK originally named `mcguffey_graded` /
  `graded_readers_grade1` / `graded_readers_graded` as the foundations-first corpora; the cell
  author substituted OneStopEnglish Ele/Int + process_articles_v1 instead, citing
  `feedback_stop_mcguffey_use_modern_sources_USER_2026-08-08` by name, and closes with:
  "McGuffey corpora are untouched by this cell."

## 4. Actual date/character of what IS in the foundation

- **OneStopEnglish** (bootstrap/ele_cont/int_cont/adv_new, 21623/26123 = 82.8% of sentences):
  Guardian-derived news articles, simplified into Elementary/Intermediate/Advanced reading
  levels for the 2018 ACL readability-assessment paper (Vajjala & Lučić). This matches the
  director's own prior sample observation (Bowie, NSA, Apple, Pluto/Charon, e-bikes are exactly
  the kind of 2010s Guardian news topics this corpus contains).
- **OpenStax Concepts of Biology** (bio_new, 4500/26123 = 17.2%): a 2013 open-license
  undergraduate biology textbook, CNXML-parsed and cleaned, CC BY-NC-SA 4.0.
- Era of everything actually read into the foundation: **2013-2018 publication, describing
  present-day (2010s) subject matter.** Not a single 19th/early-20th-century sentence.

## 5. Modern-sources-rule check

Historical corpora ARE present on disk (section 1 table) but confirmed NOT consumed by the
reading-grounding-loop foundation segments (section 2/3). Two known consumers of
`mcguffey_graded` remain, both explicitly demoted/held-out by design, not primary:
- `experiments/exp_interactive_loop_real_gold_mcguffey_v1.py` (gold-eval data for an
  interactive-loop mention/role probe, dated 2026-08-01 -- BEFORE the 08-08 stop directive;
  worth a follow-up check that nothing newer still dispatches this as a live/primary cell).
- `tools/build_mention_role_eval_mcguffey.py` / `notes/research_mcguffey_construction_density_
  grade_progression_2026-07-31.md` -- construction-density analysis tooling, same pre-08-08
  vintage.
No rule violation found in the CURRENT foundation-building path. The other classic-literature
corpora (alice/little_women/tom_sawyer/sherlock_holmes/wizard_of_oz/anne_of_green_gables/
tinyshakespeare/litbank) were not traced to any consumer in this audit's scope (only the
reading-grounding-loop + exp_definitional_grounding_v3 loaders were read) -- a full
consumer-sweep of those is a separate follow-up if the USER wants full disk hygiene, not this
audit's mandate.

## 6. Branch name recommendation

`dataprep/mcguffey-graded-corpus` is misleading against current reality: it names a corpus that
contributed 0 sentences to the live foundation and was explicitly rejected by a later
standing directive. One-line recommendation: rename (or note in the branch's own README/PR
description) to something reflecting what's actually staged now (e.g.
`dataprep/onestop-openstax-modern-corpus` or similar) before merge, so a future reader doesn't
draw the same (reasonable) inference the USER just did.
