# Psychology 2e (OpenStax) -- provenance

## Why this title, and why first (director's ordering, 2026-08-12)
Picked over Astronomy 2e as the first non-biology acquisition specifically because it is the
MORE different domain: a social/behavioral science rather than another physical/natural science.
Astronomy risked re-confirming "hard science textbooks are definitional" without testing whether
the pipeline and the density effect generalize to a genuinely different register (more narrative
explanation, case studies, research description; fewer glossary-style operational definitions).
It is also the smallest of the six candidate titles by raw CNXML bytes (3.21 MB / 105 modules),
making it the cheapest first test of "does the cleaner even work on a non-biology book."

## Source
- Repo: https://github.com/openstax/osbooks-psychology (branch `main`, CNXML source)
- Collection definition: `collections/psychology-2e.collection.xml`
  (mirrored here as `raw/psychology-2e.collection.xml`)
- 105 module files fetched via `raw.githubusercontent.com/openstax/osbooks-psychology/main/
  modules/<id>/index.cnxml` (mirrored here as `raw/modules/<id>.cnxml`)
- Fetched: 2026-08-12, via `data/corpora/openstax_common/fetch_openstax.py`.
- Book landing page: https://openstax.org/details/books/psychology-2e

## License
**CC BY-NC-SA 4.0**, confirmed directly from `<md:license url="http://creativecommons.org/
licenses/by-nc-sa/4.0/">` in the collection XML metadata, and independently from in-book prose
(module m82103, the credits/preface module): "Psychology 2e is licensed under a Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA) license." Same license family as
`textbook_concepts_biology` -- not assumed, checked directly per the director's instruction to
treat every title as uncertain until verified.

## Required attribution
> Access for free at https://openstax.org/books/psychology-2e/pages/1-introduction

Content lead: Rose M. Spielman (per in-book credits, module m82103), plus a large
contributing/review team (OpenStax, Rice University).

## Pipeline
Identical to `textbook_concepts_biology`: `data/corpora/openstax_common/fetch_openstax.py`
(generic collection.xml parser + raw module fetcher, new script, stdlib-only) produced
`raw/collection_structure.json` in the same shape the existing cleaner expects, then the
existing, minimally-parameterized `textbook_concepts_biology/clean_cnxml.py` (via `--struct
--mod-dir --out-txt --out-stats`, no logic changes -- see that file's 2026-08-12 parameterization
note and the bit-identical-biology-output verification) produced the cleaned text. 105/105
modules parsed with 0 errors.

## Directory layout
- `raw/psychology-2e.collection.xml`, `raw/collection_structure.json`, `raw/modules/<id>.cnxml`
  (105 files, as fetched, unmodified).
- `cleaned/psychology_2e.clean.txt` -- final plain-text corpus (~2.08 MB).
- `cleaned/module_report.json` -- per-module block counts (0/105 parse errors).
- `density_report.json` -- definitional-construction density measurement (see below).

## Measurement (2026-08-12, `data/corpora/openstax_common/measure_density.py`)
Sentence count and definitional-pattern density, using the SAME sentence-split recipe as the
existing bio_new segment loader and the same `hdlab.definitional_extraction.
sentence_has_definitional_pattern` detector used in `tools/measure_definitional_pattern_
association_v1.py`'s M3 segment-density check (read-only reuse, no writes to hdlab/experiments/
data/foundation).

- n_sentences: 28389
- definitional-pattern density: **30.8 per 1000 sentences**
- Recalibrated bio baseline (same proxy, full Concepts of Biology corpus, 11332 sentences):
  **100.0 per 1000 sentences**
- Psychology is ~3.2x LESS definitional-pattern-dense than biology by this proxy, and lands close
  to OneStop news-prose territory (22.5-28.6 facts/1000 in the original pipeline metric) rather
  than the biology cluster. See caveat in `measure_density.py` docstring: this proxy (raw
  sentence-pattern hit rate) is not numerically the same measure as the 304.7 facts/1000 v5
  pipeline number (that number is post-canonicalization GROUNDED_MEANING facts from the full
  reading-grounding loop, which this acquisition-only pass deliberately does not run) -- it is a
  same-methodology yardstick for cross-title comparison, not a plug-in replacement.

## Not committed to git (yet -- pending director sign-off, targeted commit)
