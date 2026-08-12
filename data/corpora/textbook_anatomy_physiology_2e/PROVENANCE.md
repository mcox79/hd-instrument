# Anatomy and Physiology 2e (OpenStax) -- provenance

## Source
- Repo: https://github.com/openstax/osbooks-anatomy-physiology (branch `main`, CNXML source)
- Collection: `collections/anatomy-and-physiology-2e.collection.xml` (mirrored as
  `raw/anatomy-and-physiology-2e.collection.xml`)
- 198 module files fetched via `raw.githubusercontent.com/openstax/osbooks-anatomy-physiology/
  main/modules/<id>/index.cnxml` (mirrored as `raw/modules/<id>.cnxml`).
- Fetched: 2026-08-12, via `data/corpora/openstax_common/fetch_openstax.py`.
- Book landing page: https://openstax.org/details/books/anatomy-and-physiology-2e

## License
**CC BY-NC-SA 4.0**, confirmed directly: `collections/anatomy-and-physiology-2e.collection.xml`
metadata contains `<md:license url="http://creativecommons.org/licenses/by-nc-sa/4.0/">`. Checked
per-title, not assumed from the sibling biology license.

## Required attribution
> Access for free at https://openstax.org/books/anatomy-and-physiology-2e/pages/1-introduction

## Pipeline
Same generic fetch (`data/corpora/openstax_common/fetch_openstax.py`) + the existing,
minimally-parameterized `textbook_concepts_biology/clean_cnxml.py` (no logic changes). 198/198
modules parsed with 0 errors.

## Directory layout
- `raw/anatomy-and-physiology-2e.collection.xml`, `raw/collection_structure.json`,
  `raw/modules/<id>.cnxml` (198 files).
- `cleaned/anatomy_physiology_2e.clean.txt` -- final plain-text corpus (~3.24 MB).
- `cleaned/module_report.json` -- 0/198 parse errors.
- `density_report.json` -- definitional-construction density measurement.

## Measurement (2026-08-12, `data/corpora/openstax_common/measure_density.py`)
Same sentence-split + `sentence_has_definitional_pattern` proxy as the other new titles (see
`textbook_psychology_2e/PROVENANCE.md` for full methodology + caveat).

- n_sentences: 22542
- definitional-pattern density: **105.8 per 1000 sentences**
- vs recalibrated bio baseline (same proxy, full Concepts of Biology corpus): 100.0/1000
- Highest of all six titles measured (including Concepts of Biology itself) -- consistent with
  A&P being extremely terminology-dense (systematic anatomical/medical naming), i.e. the added
  vocabulary is real medical/anatomical terminology, not a density loss for the added diversity.

## Not committed to git (yet -- pending director sign-off, targeted commit)
