# Microbiology (OpenStax) -- provenance

## Source
- Repo: https://github.com/openstax/osbooks-microbiology (branch `main`, CNXML source)
- Collection: `collections/microbiology.collection.xml` (mirrored as
  `raw/microbiology.collection.xml`)
- 159 module files fetched via `raw.githubusercontent.com/openstax/osbooks-microbiology/main/
  modules/<id>/index.cnxml` (mirrored as `raw/modules/<id>.cnxml`).
- Fetched: 2026-08-12, via `data/corpora/openstax_common/fetch_openstax.py`.
- Book landing page: https://openstax.org/details/books/microbiology
- Authors (from collection XML `authors` attribute): Nina Parker, Mark Schneegurt,
  Anh-Hue Thi Tu, Brian M. Forster, Philip Lister.

## License
**CC BY-NC-SA 4.0**, confirmed directly: `collections/microbiology.collection.xml` metadata
contains `<md:license url="http://creativecommons.org/licenses/by-nc-sa/4.0/">`. Checked
per-title, not assumed from the sibling biology license.

## Required attribution
> Access for free at https://openstax.org/books/microbiology/pages/1-introduction

## Pipeline
Same generic fetch (`data/corpora/openstax_common/fetch_openstax.py`) + the existing,
minimally-parameterized `textbook_concepts_biology/clean_cnxml.py` (no logic changes). 159/159
modules parsed with 0 errors.

## Directory layout
- `raw/microbiology.collection.xml`, `raw/collection_structure.json`, `raw/modules/<id>.cnxml`
  (159 files).
- `cleaned/microbiology.clean.txt` -- final plain-text corpus (~2.86 MB).
- `cleaned/module_report.json` -- 0/159 parse errors.
- `density_report.json` -- definitional-construction density measurement.

## Measurement (2026-08-12, `data/corpora/openstax_common/measure_density.py`)
Same sentence-split + `sentence_has_definitional_pattern` proxy as the other new titles (see
`textbook_psychology_2e/PROVENANCE.md` for full methodology + caveat).

- n_sentences: 23605
- definitional-pattern density: **62.6 per 1000 sentences**
- vs recalibrated bio baseline (same proxy, full Concepts of Biology corpus): 100.0/1000
- Biology-adjacent as expected, but notably below both Concepts of Biology and A&P -- more
  procedural/mechanism prose (infection process, lab technique) than terse glossary-style
  definition in places.

## Not committed to git (yet -- pending director sign-off, targeted commit)
