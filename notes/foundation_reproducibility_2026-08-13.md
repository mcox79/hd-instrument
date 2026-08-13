# Foundation provenance store: reproducibility + exposure audit (2026-08-13)

READ-ONLY audit. No code, store, or git state was modified. All numbers/hashes computed off disk
with `.venv/Scripts/python.exe` at audit time.

Question: the 221 hand-scored facts were banked into `data/foundation_provenance_v1/` (16.6 MB,
incl. a 14.6 MB `store_tensors.npz`), and the store directory was deliberately NOT committed
(`.gitignore:49 data/*/**`). That is only acceptable if the store can be REBUILT from committed
inputs. This traces every input.

## 1. The input chain

The provenance store is built in two passes, both scripts living in the store directory itself:

```
PASS 1  data/foundation_provenance_v1/backfill_pipeline_provenance.py
        READS   data/foundation/reading_grounding_v1/store        (canonical, read-only)
        WRITES  data/foundation_provenance_v1/store               (7,966 rows, vectors copied
                                                                   bit-identically, pipeline tag
                                                                   added to the plaintext ledger)
        WRITES  backfill_manifest.json, quarantine_report.json

PASS 2  data/foundation_provenance_v1/bank_definitional_predicate_v62.py
        READS   data/foundation_provenance_v1/store               (asserts exactly 7,966 rows)
        READS   data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl   (221 lines)
        WRITES  data/foundation_provenance_v1/store               (8,187 rows)
        WRITES  bank_manifest_predicate_v62.json,
                definitional_predicate_v62_ledger.jsonl (221 lines),
                quarantine_report.json (overwrites pass-1 version)
```

Code dependencies: `hdlab/foundation_persistence.py` (save_store/load_store),
`hdlab/hd_fact_store.py` (HD encoding of the 221 new facts),
`hdlab/closed_class_lexicon.py` (report only).
Data dependency for the quarantine REPORT only (not the store):
`data/corpora/onestop/Texts-SeparatedByReadingLevel/{Ele,Int,Adv}-Txt` +
`data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`
(proper-noun table).

## 2. Per-input tracked status

| Input | Tracked? | Commit | Pushed to origin? |
|---|---|---|---|
| `data/foundation_provenance_v1/backfill_pipeline_provenance.py` | YES (force-added past `data/*/**`) | b8d98509e | NO |
| `data/foundation_provenance_v1/bank_definitional_predicate_v62.py` | YES | b8d98509e | NO |
| `data/foundation_provenance_v1/backfill_manifest.json` | YES | b8d98509e | NO |
| `data/foundation_provenance_v1/bank_manifest_predicate_v62.json` | YES | b8d98509e | NO |
| `data/foundation_provenance_v1/definitional_predicate_v62_ledger.jsonl` | YES | b8d98509e | NO |
| `data/foundation_provenance_v1/quarantine_report.json` | YES | b8d98509e | NO |
| `data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl` (221 facts) | YES | 5ea354285 | NO |
| `hdlab/hd_fact_store.py` | YES | b8d98509e | NO |
| `hdlab/foundation_persistence.py` | YES | b8d98509e | NO |
| `hdlab/closed_class_lexicon.py` | YES | 04b922c0e | YES |
| `data/foundation_provenance_v1/store/*` (the artifact) | **NO** — ignored by `.gitignore:49` | — | — |
| `data/foundation/reading_grounding_v1/store/*` (7,966 legacy rows) | **NO** — ignored by `.gitignore:49` | — | via backup tarball, YES |
| `backups/foundation/2026-08-12/reading_grounding_v1_2026-08-12.tar.gz` | YES | a37b8abeb | **YES** (`origin/dataprep/mcguffey-graded-corpus`) |
| `data/corpora/onestop/**` (report input) | **NO** (0 files tracked) | — | — |
| `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt` | **NO** | — | — |

Working tree: the only modified tracked file anywhere near this chain is
`hdlab/reading_grounding_loop.py` (not an input to either pass).

## 3. Backup currency check (the critical link)

`backups/foundation/2026-08-12/` exists in git (commit a37b8abeb, 2026-08-12 15:35, pushed —
`git branch -r --contains a37b8abeb` -> `origin/dataprep/mcguffey-graded-corpus`) and contains
three tarballs + `SHA256SUMS.txt`.

Tarball `reading_grounding_v1_2026-08-12.tar.gz` read straight out of git
(`git cat-file blob`, 16,287,086 bytes, sha256
`b61f6ab296202bfd539671c04ef7fed3c93531751ecead159c0218ea9d0aec93`, matching the committed
SHA256SUMS.txt) and every member hashed against the live directory:

| file | bytes | sha256 (live == backup) |
|---|---|---|
| `concept_space.npz` | 949,615 | `643703dae9a03589e473eabb640535d70708e80436b7f2cfbad74c0b47de48ac` |
| `library_pending.json` | 1,661,812 | `1a15f9d5fd2f910527fdf22c58f23eac3fa6f16f02bf24808634ba3d4179db76` |
| `library_pending_ctx.npz` | 1,055,218 | `0d5b9dfc237f3ce6df1646144b0b0801249c968897726f55ec7d01bd8a863dd1` |
| `manifest.json` | 558,065 | `8c473b11d8c98a164a8fa2f881901bc72ceae3d232b49ccc573853996412c007` |
| `store/store_facts.json` | 1,415,238 | `00aa8f1ac2c7c17837bf86f63a43762176b8ba9b837508e969e49dfeb8a8f22c` |
| `store/store_meta.json` | 240,234 | `97cd1db8b9ce1ba6aa5a50dd0053db29b6706cf383af628d956d476f5ad74b5c` |
| `store/store_tensors.npz` | 14,391,653 | `46b73cc21a96d5801fadcb48f06aadd120010e5dee77b0e2aa707a9aefcd226d` |

**All 7 files MATCH byte-for-byte. The backup is CURRENT, not stale.** The `store_facts.json`
hash also equals `source_store_sha256` recorded in `backfill_manifest.json` and
`canonical_store_per_file_sha256` in `bank_manifest_predicate_v62.json`, i.e. the backup is the
exact input the backfill consumed tonight.

Same check on the other two tarballs: `reading_grounding_v2_qualityfix` (10 files) and
`reading_grounding_v3_definitional` (2 files) also match live byte-for-byte.

Integrity of the artifact itself: the on-disk provenance store hashes equal the values recorded in
`bank_manifest_predicate_v62.json` (`store_facts.json` 1,727,317 B
`881939410ebd34e3476ffbfe1115e840ea29403c3c7a6433a50a4192f2b21747`; `store_meta.json` 245,938 B
`e5bb4237...`; `store_tensors.npz` 14,645,471 B `348beedf...`), so nothing has drifted since the
01:26 bank.

## 4. Verdict

**REPRODUCIBLE** — from committed artifacts alone, no input breaks the chain:

- legacy 7,966 rows: recoverable byte-identically from the committed+pushed tarball;
- 221 new facts: `predicate_facts_v62.jsonl` tracked (221 lines, matches the 221-line ledger);
- both build scripts + both manifests + the ledger: tracked;
- the hdlab code the encoding depends on: tracked, clean working tree.

Rebuild recipe: extract `reading_grounding_v1_2026-08-12.tar.gz` to
`data/foundation/reading_grounding_v1/`, run `backfill_pipeline_provenance.py`, then
`bank_definitional_predicate_v62.py`.

Byte-equivalence expectation (NOT empirically re-run — a rerun would write the store, out of scope
for this read-only audit): the pipeline is deterministic by construction —
`store_meta.json` materializes the symbol codebook in first-sight order, `store_tensors.npz`
persists the codec's `torch.Generator` state (`gen_state`) and the PIPELINE role key, both scripts
force `OMP/OPENBLAS_NUM_THREADS=1` and iterate sorted collections, and both scripts already
self-verify bit-identity of the 7,966 legacy vectors after save/reload. Residual risk is
torch/numpy version drift in float32 RNG, which would still be FACT-equivalent. Claim tier:
fact-equivalence certain, byte-equivalence expected-but-unverified.

Caveat on the quarantine REPORT (not the store): its proper-noun table is built from
`data/corpora/onestop/**` and `concepts_biology.clean.txt`, both UNTRACKED. Losing those
reproduces the store but not the report's PROPER/COMMON buckets.

## 5. Exposure — what exists ONLY on this machine

Branch `dataprep/mcguffey-graded-corpus` is **54 commits ahead of `origin/dataprep/mcguffey-graded-corpus`**.
"Committed" here does not mean "off-machine": if this disk died right now, everything in those 54
commits dies with it.

Unrecoverable-if-lost, concretely:

1. **The 54 unpushed commits**, which include the entire pass-1/pass-2 build chain:
   `bank_definitional_predicate_v62.py` (22 KB), `backfill_pipeline_provenance.py` (14 KB),
   `definitional_predicate_v62_ledger.jsonl` (142 KB), `quarantine_report.json` (48 KB), both
   manifests, `data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl` (the 221 hand-scored
   facts), `hdlab/hd_fact_store.py` + `hdlab/foundation_persistence.py` provenance changes, and
   tonight's notes. **Origin has the canonical-store backup but NOT the scripts or the 221 facts.**
   This is the single largest exposure and the reason the "store is rebuildable" argument is only
   half-true today: it is rebuildable ON THIS MACHINE.
2. `data/foundation_provenance_v1/store/` — 16.6 MB, untracked, no backup. Rebuildable (see above).
3. `data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl` — 1,829,021 B, and
   `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` — 1,193,900 B.
   Untracked AND absent from the 2026-08-12 backup (which covers v1/v2/v3 only). The v5 file is the
   term-boundary-fix output behind tonight's 64%/94% hand-scores.
4. `data/foundation/` variants not in the backup: `reading_grounding_v1_post_bootstrap_control_copy`
   (6.41 MB), `reading_grounding_v1_smoke` (3.59 MB),
   `reading_grounding_v1_smoke_post_bootstrap_control_copy` (2.15 MB),
   `reading_grounding_v2_qualityfix_smoke` (4.83 MB). Derived/smoke, low value.
5. `data/corpora/` — 3.79 GB on disk, only 59 files tracked. Untracked notables:
   `onestop` (400 MB, 2,685 files), `textbook_concepts_biology/cleaned/concepts_biology.clean.txt`
   (1.46 MB), `arc` (2.17 GB), `simplewiki` (603 MB), `worldtree` (257 MB). Mostly re-downloadable
   public corpora, but the CLEANED/derived variants are local work.
6. `data/` as a whole is 166.65 GB across 7,807 subdirs, essentially all untracked experiment
   output (`lambda_batch_results` 39.1 GB, `cell2_results` 22.1 GB, `skypilot_results` 13.8 GB,
   `substrate_director_kb_v1` 11.9 GB). Regenerable-in-principle, expensive-in-practice; not part
   of this chain.
7. 126 modified-but-uncommitted tracked files in the working tree (mostly `metrics.json` under
   `data/exp_*`), plus untracked scratch (`.tmp_scan/`, `_probe_corpus_count.py`,
   `cskg_frac_result.txt`) and many untracked `data/exp_*` result dirs.

No remedial action taken. Pushing the 54 commits requires USER authorization (NO ORIGIN PUSH
without in-session auth).
