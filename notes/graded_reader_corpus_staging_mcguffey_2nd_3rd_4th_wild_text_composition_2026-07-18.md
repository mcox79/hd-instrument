# Graded-reader corpus staging: McGuffey 2nd/3rd/4th -- richer real passages for a fair wild-text composition test

Date: 2026-07-18. Sourcing + staging only (NO cell dispatch). All data PD (US) via
Project Gutenberg; staged LOCAL only (no git-add / push / remote-persist).

## Why (the data-poverty limit this closes)
The reader arc has VERIFIED machinery (learned role-sensitive extractor RELF1~0.72 on real
primer; maintained-salience coref; composition machinery where frequency can't win) but the
composition test had to be AUTHORED: grade-1 PRIMER passages are ~3 sentences (~67 words),
too short/thin, so frequency trivially wins on real text. We need RICHER REAL passages
(longer, multi-entity, natural 2-relation composition, natural competitive coref) that are
STILL simple enough for a glass-box SVO extractor. This stages exactly that, and starts the
"read progressively harder real books" progression.

## Staged inventory (all PD-US, Project Gutenberg)
Paths under `data/corpora/graded_readers_graded/cleaned/`. Cleaner: `clean_gutenberg.py`
(stdlib, adapted from the grade1 pipeline: strips PG boilerplate + adult front-matter +
per-lesson DEFINITIONS/EXERCISES/NOTES apparatus + phonics vocab rows + running headers;
KEEPS all reading prose, names, possessives).

| Book | PG# | Level | file (.clean.txt) | words | passages | words/passage | mean SL | median SL | <=15w | simple(<=1 clause) | pnouns/100w | pronouns/100w | recurring names | COMP-density |
|------|-----|-------|-------------------|-------|----------|---------------|---------|-----------|-------|--------------------|-------------|---------------|-----------------|--------------|
| McGuffey 2nd Reader | 14668 | Grade 2 | mcguffey_second_reader | 13,366 | 71 | **188** | 14.2 | 12 | 64.7% | 43.1% | 5.0 | 8.4 | 124 | 0.501 |
| McGuffey 3rd Reader | 14766 | Grade 3 | mcguffey_third_reader | 24,499 | 78 | 314 | 16.0 | 14 | 55.9% | 38.8% | 5.1 | 7.8 | 157 | 0.498 |
| McGuffey 4th Reader | 14880 | Grade 4 | mcguffey_fourth_reader | 51,380 | 89 | 577 | 20.9 | 18 | 44.1% | 31.5% | 4.8 | 6.7 | 291 | 0.552 |

Reference rungs already staged (`../graded_readers_grade1/`), same metric:
| McGuffey Primer | 14642 | Pre-K/K | 2,898 | 43 | **67** | 10.2 | - | 84.5% | 69.7% | 5.1 | 6.7 | 31 | 0.403 |
| McGuffey 1st Reader | 14640 | Grade 1 | 5,652 | 58 | 97 | 12.5 | - | 75.2% | 59.7% | 5.9 | 7.5 | 57 | 0.466 |

- COMP-density (rough, defined below) = fraction of adjacent sentence-pairs where BOTH carry
  an entity+verb AND share a recurring name OR continue via a pronoun -- i.e. natural
  2-relation composition about the same entity.
- Metric def: proper nouns = capitalized tokens not sentence-initial or recurring; pronoun
  set = he/she/it/they/... ; "simple" = <=1 clause-connector (and/but/which/that/because/
  when/... + commas). Rough stdlib heuristics, NOT a parser -- read as relative signal.

## Top-line reading
1. **Passage RICHNESS is the decisive fix, and it lands.** Words/passage jumps 67 (primer)
   -> 188 (2nd) -> 314 (3rd) -> 577 (4th). The primer's ~67-word passages are why frequency
   trivially won; the 2nd reader's ~188-word passages are ~2.8x richer -- long enough that a
   passage carries multiple entities and multiple relations per entity, so frequency alone
   can't resolve composition. This is precisely the property the authored test had to fake.
2. **COMP-density rises monotonically primer->4th (0.40 -> 0.47 -> 0.50 -> 0.50 -> 0.55)** and
   competitive coref is present (7-8 pronouns/100w against 120-290 recurring names) -- natural,
   not constructed.
3. **SVO-tractability degrades monotonically with grade** -- exactly the escalation we want to
   control. 2nd: 64.7% short + 43% single-clause = squarely in the glass-box simple-SVO regime.
   4th: 44% short, 31.5% single-clause, mean 20.9w, AND it mixes in POETRY (semicolon verse
   merges into 182-word pseudo-sentences) and literary multi-clause prose from named authors
   -- this is the approach to the ~0.44 tangled-prose wall, NOT a clean SVO test.

## RECOMMENDATION -- first wild-text composition test = McGuffey SECOND Reader
`data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt`

It is the sweet spot: RICHER than the primer (188 vs 67 words/passage, 71 didactic-narrative
passages with families of recurring characters -- Mr./Mrs. Brown, Harry, Kate, etc.), with
natural competitive coref (8.4 pronouns/100w) and COMP-density 0.50, yet STILL in the
glass-box-tractable regime (mean 14.2w, 64.7% <=15w, 43% single-clause, didactic not literary).
Frequency should NOT trivially win here, but the extractor is not yet facing tangled prose.

- **3rd Reader = the next rung** once 2nd passes: 314 words/passage, mean 16w, some literary
  prose creeping in -- harder but still largely tractable.
- **4th Reader = a STRESS rung / caution, not the first test.** Use it to probe where the
  glass-box SVO regime breaks (poetry + multi-clause literary prose ~ the 0.44 wall). For a
  prose-only run, filter the poem lessons.

## Escalation ladder (the read-progressively-harder path toward the textbook goal)
Primer (67 w/passage) -> 1st (97) -> **2nd (188) -> 3rd (314) -> 4th (577)** -> [Baldwin /
Elson / Beacon graded readers] -> ... -> textbook ingestion. The 2nd->4th McGuffey rungs are
now staged and stats-characterized; grade escalates vocabulary, sentence length, and clause
complexity in controlled steps, which is exactly the curriculum for a learned self-improving
reader (knowledge guides comprehension; comprehension grows knowledge).

## Other PD graded readers -- assessed, NOT yet staged (all PD-US, ready as next rungs)
Confirmed open/available, same PG pipeline applies; deferred to keep this sourcing bounded
(the McGuffey ladder fully covers the immediate need):
- **Baldwin, "School Reading by Grades"** (James Baldwin) -- PG (e.g. Fifth Year #51000,
  Sixth Year #36864; Eighth Reader #30559 w/ Ida C. Bender). LITERARY-NARRATIVE prose (stories),
  likely HIGHER composition density than McGuffey's didactic lessons -- a strong parallel/
  alternative ladder. Lower years (1st-4th) available via Internet Archive (PD).
- **Elson Grammar School Reader / Elson Readers** -- pre-1929 US, PD; available (PG/Archive).
- **Beacon Second Reader** (Fassett) -- pre-1929 US, PD; available.
All are pre-1929 US publications = public domain in the US. NONE are license-blocked. Stage
with the same `clean_gutenberg.py` pattern when the ladder needs widening or cross-source
variety (recommended after the McGuffey ladder is validated on the reader).

## License / provenance
All items PD (US) via Project Gutenberg; the PG trademark applies only to the packaged
header/footer, which the cleaner strips. No license-blocked items staged. Credit: Project
Gutenberg (www.gutenberg.org); authors William Holmes McGuffey (and, for the deferred set,
James Baldwin et al.). Full per-book provenance:
`data/corpora/graded_readers_graded/PROVENANCE.md`. Staged LOCAL only -- no git-add, no
origin push, no remote-persist.
