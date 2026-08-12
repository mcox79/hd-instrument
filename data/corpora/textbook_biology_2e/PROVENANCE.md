# Biology 2e (OpenStax) -- provenance

## Note on sequencing
Acquired LAST per the director's explicit ordering: same-domain volume in a domain already
represented (`textbook_concepts_biology`) is the lowest-value addition for subject DIVERSITY,
even though it is the safest integration (same collection family, same repo even --
`osbooks-biology-bundle` also contains `concepts-biology.collection.xml`, already in use).

## Source
- Repo: https://github.com/openstax/osbooks-biology-bundle (branch `main`, CNXML source) --
  same repo as `textbook_concepts_biology`, different collection.
- Collection: `collections/biology-2e.collection.xml` (mirrored as
  `raw/biology-2e.collection.xml`). The repo bundle also contains `concepts-biology.collection.
  xml` (already fetched, see `textbook_concepts_biology/`) and `biology-ap-courses.collection.
  xml` (NOT fetched -- AP-level reordering of largely the same content, out of scope).
- 259 module files fetched via `raw.githubusercontent.com/openstax/osbooks-biology-bundle/main/
  modules/<id>/index.cnxml` (mirrored as `raw/modules/<id>.cnxml`). Comprehensive/2-3x the module
  count of Concepts of Biology (107 modules), as the expansion plan anticipated.
- Fetched: 2026-08-12, via `data/corpora/openstax_common/fetch_openstax.py`.
- Book landing page: https://openstax.org/details/books/biology-2e

## License
**CC BY-NC-SA 4.0**, confirmed directly: `collections/biology-2e.collection.xml` metadata
contains `<md:license url="http://creativecommons.org/licenses/by-nc-sa/4.0/">`. Same license as
`concepts-biology` (both in the same repo/collection family), checked directly rather than
inherited by assumption.

## Required attribution
> Access for free at https://openstax.org/books/biology-2e/pages/1-introduction

## Pipeline
Same generic fetch (`data/corpora/openstax_common/fetch_openstax.py`) + the existing,
minimally-parameterized `textbook_concepts_biology/clean_cnxml.py` (no logic changes). 259/259
modules parsed with 0 errors.

## Directory layout
- `raw/biology-2e.collection.xml`, `raw/collection_structure.json`, `raw/modules/<id>.cnxml`
  (259 files).
- `cleaned/biology_2e.clean.txt` -- final plain-text corpus (~3.44 MB).
- `cleaned/module_report.json` -- 0/259 parse errors.
- `density_report.json` -- definitional-construction density measurement.

## Overlap with `textbook_concepts_biology` (flagged, not resolved here)
Biology 2e and Concepts of Biology are different books (comprehensive vs. concepts-level intro)
but cover substantially overlapping subject matter, likely with many near-duplicate or
restated definitions of the same core terms (cell, mitosis, DNA, etc.). This acquisition pass
does NOT deduplicate against the existing bio_new segment -- that is an ingestion-time decision,
out of scope for acquisition + cleaning. Flagging here so the overlap is visible before any
future ingestion call.

## Measurement (2026-08-12, `data/corpora/openstax_common/measure_density.py`)
Same sentence-split + `sentence_has_definitional_pattern` proxy as the other new titles (see
`textbook_psychology_2e/PROVENANCE.md` for full methodology + caveat).

- n_sentences: 27219
- definitional-pattern density: **86.9 per 1000 sentences**
- vs recalibrated bio baseline (same proxy, full Concepts of Biology corpus): 100.0/1000
- Close to (slightly below) the Concepts of Biology figure, as expected for the same subject at
  greater comprehensiveness/depth -- confirms the two biology titles are consistent with each
  other, not an outlier either direction.

## Not committed to git (yet -- pending director sign-off, targeted commit)
