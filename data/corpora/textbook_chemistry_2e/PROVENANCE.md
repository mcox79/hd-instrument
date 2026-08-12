# Chemistry 2e (OpenStax) -- provenance

## License question (resolved before download, per director's instruction)
The prior plan doc (`notes/corpus_expansion_plan_2026-08-12.md`) flagged Chemistry as
"not yet checked directly" and only assumed CC BY-NC-SA 4.0 by extension of sibling titles.
Checked directly BEFORE downloading module content: `collections/chemistry-2e.collection.xml`
metadata contains `<md:license url="http://creativecommons.org/licenses/by-nc-sa/4.0/">`, and
in-book prose (module m68662, credits/preface) states: "Chemistry 2e is licensed under a
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA) license." **Confirmed:
same CC BY-NC-SA 4.0 as the other titles**, not a different/stricter license as the plan's
uncertainty flagged as a live possibility.

## Source
- Repo: https://github.com/openstax/osbooks-chemistry-bundle (branch `main`, CNXML source)
- Collection: `collections/chemistry-2e.collection.xml` (mirrored as
  `raw/chemistry-2e.collection.xml`). Note: this repo bundle also contains a second collection
  (`chemistry-atoms-first-2e`, an alternate ordering of largely the same modules) -- NOT fetched,
  out of scope (would be duplicate content, not new subject diversity).
- 149 module files fetched via `raw.githubusercontent.com/openstax/osbooks-chemistry-bundle/
  main/modules/<id>/index.cnxml` (mirrored as `raw/modules/<id>.cnxml`).
- Fetched: 2026-08-12, via `data/corpora/openstax_common/fetch_openstax.py`.
- Book landing page: https://openstax.org/details/books/chemistry-2e

## License
**CC BY-NC-SA 4.0** (see above -- verified directly, not assumed).

## Required attribution
> Access for free at https://openstax.org/books/chemistry-2e/pages/1-introduction

## Pipeline
Same generic fetch (`data/corpora/openstax_common/fetch_openstax.py`) + the existing,
minimally-parameterized `textbook_concepts_biology/clean_cnxml.py` (no logic changes). 149/149
modules parsed with 0 errors.

## Directory layout
- `raw/chemistry-2e.collection.xml`, `raw/collection_structure.json`, `raw/modules/<id>.cnxml`
  (149 files).
- `cleaned/chemistry_2e.clean.txt` -- final plain-text corpus (~1.86 MB).
- `cleaned/module_report.json` -- 0/149 parse errors.
- `density_report.json` -- definitional-construction density measurement.

## Measurement (2026-08-12, `data/corpora/openstax_common/measure_density.py`)
Same sentence-split + `sentence_has_definitional_pattern` proxy as the other new titles (see
`textbook_psychology_2e/PROVENANCE.md` for full methodology + caveat).

- n_sentences: 15887
- definitional-pattern density: **58.6 per 1000 sentences**
- vs recalibrated bio baseline (same proxy, full Concepts of Biology corpus): 100.0/1000
- Chemistry sits BETWEEN the biology cluster (86.9-105.8/1000) and psychology (30.8/1000) --
  physical/natural science but less glossary-definitional in running prose than the life-science
  titles.

## Not committed to git (yet -- pending director sign-off, targeted commit)
