# Literature source cache

## Purpose

Every literature scan this project has run has re-fetched its sources from the web. Nothing was
kept. That has two costs:

1. **We repeat work.** The same paper gets looked up again by the next scan, at full latency and
   full token cost, with no memory that we already read it.
2. **Landed findings are not reproducible from disk.** When a note says a result is
   `[ESTABLISHED]` and cites a number, the evidence behind that number lives on someone else's
   web server. If the page moves, the claim becomes unauditable.

This cache fixes both. It is a **register of what we have already consulted**, plus the stored
artifact where storing one is legal. It is deliberately small and boring: one JSONL index, one
tool, one directory of files.

Measured on 2026-08-13, before this cache existed: the repo held 54 PDFs, of which 34 were
`dashboard.pdf` experiment renders and the rest were plot outputs. Exactly 3 were real papers
(the two WorldTree LREC papers and `sap2019atomic.pdf`), and all 3 arrived incidentally inside a
downloaded corpus, not through any deliberate practice.

## Directory layout

```
data/literature_cache/
  README.md      this file
  index.jsonl    one row per source; the authoritative record. ALWAYS present.
  files/         stored artifacts. Only open-access PDFs / author manuscripts. May be empty.
```

`index.jsonl` is the source of truth. `files/` is an optimisation. A row with
`local_path: null` is a perfectly normal, expected row.

## Naming convention

Index key: `<firstauthor_surname_lowercase>_<year>_<venue_or_topic_slug>`, ASCII, lowercase,
underscores only. Examples:

```
lambon_ralph_2017_nat_rev_neurosci_semantic_cognition
quian_quiroga_2020_tics_no_pattern_separation
hill_2015_simlex999
```

Stored files are named `files/<key>.<ext>`, so the file and its index row are trivially paired.
The tool does this automatically; do not hand-name files.

## LEGAL / ACCESS RULE

This is the part that must not be got wrong.

- **`access: "open"`** - store the full artifact under `files/`. Permitted **only** for
  open-access publications (CC-BY, CC-BY-NC, other explicit open licences), author-posted
  manuscripts, preprints (arXiv, bioRxiv, PsyArXiv), and public-domain works. Check the licence
  on the landing page, not the PDF.
- **`access: "metadata_only"`** - store the **metadata, the abstract, and the specific
  quantitative claims we actually rely on**. Do **not** store the full text. This is the correct
  and expected setting for paywalled journal articles. Most rows in this index are, and should
  be, `metadata_only`.
- **Never store anything whose licence forbids it.** If the licence is unclear, it is
  `metadata_only`. There is no scenario in which finishing a scan faster justifies redistributing
  a publisher's PDF.

The `claims_used` field exists precisely so that a paywalled source is still useful offline: we
keep the number and the tag we depend on, attributed to its source, without keeping the article.

Recording a claim here is **not** a verification of that claim. A claim carries whatever evidence
tag the scanning agent assigned it, and that tag is the scan's judgement, not an independent
replication audit. VET before a tagged claim becomes load-bearing.

## Index schema

One JSON object per line, keys in this fixed order:

| field | meaning |
| --- | --- |
| `key` | stable identifier, naming convention above |
| `title` | article title |
| `authors` | `Surname I; Surname I; ...` |
| `year` | publication year, integer or null |
| `venue` | journal / conference, with volume:pages when known |
| `doi_or_url` | DOI preferred, URL acceptable, empty string if neither |
| `sha256` | hex digest of the stored file, or null |
| `local_path` | repo-relative path to the stored file, or null |
| `access` | `open` or `metadata_only` |
| `claims_used` | the specific numbers/claims WE cite from this source |
| `cited_by` | our notes that cite it |
| `retrieved_utc` | when we consulted it |

Rows are serialised canonically (fixed key order, sorted `claims_used` / `cited_by`), so a
repeated `add` of the same source produces a byte-identical line. This is enforced by the
self-test.

## Usage

Check before fetching. This is the whole point:

```
python tools/literature_cache.py find --author lambon --year 2017
python tools/literature_cache.py find --keyword "pattern separation"
python tools/literature_cache.py find --doi 10.1038/nrn.2016.150
```

Register after fetching:

```
python tools/literature_cache.py add --key hill_2015_simlex999 \
    --title "SimLex-999: evaluating semantic models with (genuine) similarity estimation" \
    --authors "Hill F; Reichart R; Korhonen A" --year 2015 \
    --venue "Computational Linguistics 41(4):665-695" --doi 10.1162/COLI_a_00237 \
    --access open --file /path/to/paper.pdf \
    --claim "human inter-annotator agreement ~0.67 Spearman" \
    --cited-by notes/brain_drill_encoder_lexical_semantics_2026-08-13.md
```

`add` refuses to overwrite an existing key unless `--force` is passed, and refuses to write
anywhere outside this directory. Verify both guards at any time:

```
python tools/literature_cache.py --self-test
```

The self-test is written to FAIL if a guard is removed. This was confirmed by mutation on
2026-08-13: neutering the path guard, the no-clobber guard, or the canonical-ordering guard each
made the self-test report a specific failure and exit 1, while the unmodified tool exited 0.

## Relationship to substrate ingestion

This corpus is the eventual target for substrate ingestion, but ingestion is **gated** and
currently **closed**. See `notes/research_persistence_policy_2026-08-13.md` for the gate and the
concrete revival criterion. Storing now and ingesting later is deliberate.
