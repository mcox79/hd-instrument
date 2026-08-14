# Research persistence policy (2026-08-13)

Written after the USER asked: "can you confirm we're saving this so we don't have to repeat it?
We've also done a TON of research before - do we track this? Is it tracked in substrate as well?
... perhaps if we download papers we should store them so we don't need to pull again. Eventually,
we'll want to ingest all of those into substrate anyways."

This note answers all four questions from disk, and states the standing rules that follow.

---

## 1. What gets saved, and where

| artifact | destination | how it is found again |
|---|---|---|
| literature scan (the full report, with per-claim evidence tags) | `notes/lit_scan_<topic>_<date>.md` | `tools/director_kb_query.py` |
| brain-fidelity drill (biology -> per-component gap -> build target) | `notes/brain_drill_<component>_<date>.md` | same |
| a source we cited (paper, preprint, dataset) | `data/literature_cache/` + a row in `index.jsonl` | `tools/literature_cache.py find` |
| experiment result | `data/<cell>/metrics.json` | KB `metrics` class (7,501 indexed) |
| pre-registration | `preregs/<date>_<cell>.md` | KB `prereg` class (3,689 indexed) |
| a capability + its WIRE/SHELVE decision | `data/capability_registry.jsonl` | `tools/capability_registry_query.py --serves` |
| a refuted route / earned discipline | `notes/STATUS_LESSONS.md` (uncapped, never-trim) | stubbed in `notes/STATUS.md` |

**The synthesis is not a substitute for the report.** The 2026-08-13 encoder drill produced a 33 KB
synthesis from four sub-scans. The synthesis kept the citations but dropped the per-claim
ESTABLISHED / CONTESTED / SINGLE-STUDY / FAILED-REPLICATION tags, which are the part that decides
how much weight a claim can carry. The five full reports were rescued from transient subagent
transcripts (`ce2e99388`) with hours to spare before cleanup. Rule: **a literature scan's full
report is persisted as its own note, verbatim, at the time it lands** -- not summarised and
discarded.

## 2. Check before you scan (the standing rule this note exists to create)

This mirrors the existing query-before-build gate on the capability registry, and exists for the
same reason: work already done is being done again.

Before dispatching ANY research drill or literature scan:

1. `python tools/director_kb_query.py "<the question>"` -- 9,197 notes, 3,689 preregs and 7,501
   metrics files are indexed. Narrow or skip the drill on a high-cosine hit.
2. `python tools/literature_cache.py find "<author|year|keyword|doi>"` -- if we already pulled the
   source, cite the cached row instead of re-fetching.

And when the scan returns, register every source it leaned on with `literature_cache.py add`, so
the next scan finds it.

## 3. The source cache

`data/literature_cache/` (created 2026-08-13, `4fbe50f91`). Before it existed, the repo held 65
PDFs and **every one was an experiment dashboard -- zero stored papers**. Every scan re-fetched
from the web, so the evidence behind a landed finding was not reproducible from disk.

- `index.jsonl` -- one row per source: key, title, authors, year, venue, doi/url, sha256, local
  path, access, the specific claims WE cite, which of our notes cite it, retrieval timestamp.
  Seeded with 65 rows from the 2026-08-13 scans.
- `tools/literature_cache.py` -- `add` and `find`. `--self-test` proves the guard (refuses writes
  outside the cache directory, refuses to clobber a key without an explicit flag, byte-identical
  row on repeated add). Verified PASS on 2026-08-13.
- **Access rule:** store open-access PDFs and author manuscripts. For paywalled work store metadata
  + abstract + the extracted quantitative claims we rely on, never the full text. Nothing whose
  licence forbids it.

## 4. Is it tracked in the substrate? No -- and that distinction matters

The `director_kb` is a **Director-facing search index**, not the substrate. Per
`notes/system_accounting_2026-08-13.md`, nothing on the live reading path reads it. Answering "have
we already done this?" and "does the substrate know this?" are different questions with different
machinery today.

What the KB actually indexes (measured 2026-08-13 from
`data/director_kb_continuous_state.json`): note 9,197 | metrics 7,501 | prereg 3,689 | memory 653 |
kegg_pathway 25 | atoms 12 | neurolex 4 | capability_registry, cert_ledger, concept_relations,
director_plan, fleet_state, framenet, gene_ontology, verbnet, wordnet 1 each | proofwiki 0.

**Experiment results ARE searchable.** This corrects a same-day claim of mine that they might not
be. With 7,501 metrics files indexed, "have we already run this?" is a query.

Its retrieval encoder is `char_trigram_v1` -- worth noting alongside
`notes/lit_scan_trained_encoder_vs_simple_ingestion_2026-08-13.md`: the retrieval layer we depend
on daily runs on the simple ingestion mechanism that every within-cell head-to-head on disk says
ties or beats a trained encoder.

## 5. Substrate ingestion: deliberately gated, not forgotten

The literature corpus IS the eventual target for substrate ingestion -- it is the knowledge layer
the architecture exists to build. It is **not** being ingested yet, and that is a decision, not an
oversight.

Reason: the reading loop currently yields **1-3% MEANINGFUL** grounded meanings (three blind
hand-scores), and 65.7% of the 3,544 existing `GROUNDED_MEANING` rows are self-referential
tautologies. Ingesting a large corpus now would manufacture tens of thousands more of them and bury
the real ones. This is exactly why the 117,642-sentence OpenStax corpus already on disk remains
un-ingested.

**Revival criterion for ingestion** (concrete, so this does not become a permanent excuse): the
reading loop clears **>= 10% MEANINGFUL on a blind hand-score against a recorded floor arm**, with
the tautology rate below 10%. At that point ingest the cached corpus, starting with the segment
whose groundings were densest (biology/technical), and re-measure before widening.

Store now, ingest when it is worth ingesting. The corpus will be waiting the moment it is usable,
rather than needing to be gathered again.

## 6. Two tooling defects found while verifying this note

Both are the silent-failure class that has already cost this project 12 days of disabled scheduled
tasks and 6 days of a stale KB. Recorded here rather than fixed, because the ingest is owned
elsewhere and was live at the time.

**(a) `director_kb_continuous_ingest.py --once` exits 0 while doing nothing.** Run at
2026-08-13T23:15Z it returned exit code 0 with `{"ingested": false, "skipped_locked": true,
"changed": true, "n_files_scanned": 21135}`. It correctly detected changed files and correctly
deferred to a lock -- but **a caller checking only the exit code concludes the ingest succeeded**.
The freshness check afterwards still reported STALE with an unchanged scan timestamp. Recommended:
exit non-zero (or print an unmissable banner) when `changed` is true and `ingested` is false.

**(b) `director_kb_freshness_check.py` prints an ACTION that cannot work in this state.** Its
advice is to check whether the scheduled task is Disabled "and/or run
`director_kb_continuous_ingest.py --once`". Measured at the time: the task
`hd_director_kb_continuous_ingest` was **Running**, holding the lock (PID 21904, `pythonw`, alive
23 minutes) -- so `--once` was a guaranteed no-op. The correct advice when the lock is held by a
live owner is "an ingest is already running, wait." Recommended: have the freshness check read the
lock and report the owner's liveness before advising.

Also observed: `n_failed_ingests=4`, all one error --
`OSError: [WinError 1450] Insufficient system resources` on
`data/gate_log_exp_slipnet_noise_cpu_v1_self-test.txt`. An environment fault rather than a design
fault, but it is silently absorbed and worth a retry path.

---

Governs alongside `notes/STATUS_SPEC.md` (STATUS discipline) and `CLAUDE.md` (capability tracking,
evidence discipline).
