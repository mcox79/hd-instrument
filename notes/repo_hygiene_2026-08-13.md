# Repo search hygiene + reclaimable-space inventory (2026-08-13)

Scope: `D:/AI/hd-instrument`. Diagnose + propose only. **Nothing was deleted, moved, committed or
staged by this audit.** All numbers below are measured on disk today; commands are quoted so they
can be re-run.

Standing instruction applied throughout: *if something looks out of step with the documentation,
triple-check it.* Each claim below states what was checked.

---

## S1. HEADLINE: the "Glob false negatives" are not a tool defect

This is the finding that matters most, because it is a **correctness** bug, not a speed one, and it
is the mechanism behind an agent nearly reporting a real experiment as never-run.

**The tool working directory is `D:/AI`, not `D:/AI/hd-instrument`.** Every repo-relative path an
agent writes out of habit (`notes/...`, `data/exp_.../**`, `hdlab/...`) resolves against the PARENT
of the repo, where it does not exist.

Measured, both run within a minute of each other:

| call | result |
|---|---|
| `Glob(pattern="notes/*2026-08-13*.md")` | **`No files found`** |
| `Glob(pattern="hd-instrument/notes/*2026-08-13*.md")` | 27 files |
| `Glob(pattern="*2026-08-13*.md", path="D:\AI\hd-instrument\notes")` | 27 files |
| `ls -lat notes/*2026-08-13*` (from `cd /d/AI/hd-instrument`) | 27 files |

The directory is populated. The first call is a **silent false negative**.

**The dangerous asymmetry**, also measured:

| call | behaviour |
|---|---|
| `Grep(pattern=..., path="notes")` | **hard error**: `Path does not exist: notes. Note: your current working directory is D:\AI.` |
| `Glob(pattern="notes/*.md")` | **silent** `No files found` |

`Grep` fails loudly and self-diagnoses. `Glob` fails silently and is indistinguishable from a
genuine "this does not exist" answer. An agent that concludes "no such experiment / no such note"
from a bare `Glob` is reading a cwd artefact, not the filesystem.

**No index, cache or ignore rule is involved.** This is not fixed by an ignore file and was never a
ripgrep problem.

### Rule proposed

1. **Always anchor paths for `Glob`/`Grep`**: either prefix `hd-instrument/`, or pass an absolute
   `path=`. Never a bare repo-relative pattern.
2. **A single negative `Glob` is not evidence of absence.** Before concluding an artefact does not
   exist, confirm with an absolute-path `Glob`, or `ls`/`rg --files` from inside the repo.
3. Prefer `Grep` over `Glob` for existence questions where possible — it errors instead of lying.

---

## S2. WHAT IS ACTUALLY BIG (measured)

`du -sh` over the whole repo **times out** (>300 s) — that is the symptom, not a workaround
failure. File count is the better metric for search cost anyway, and it completes.

### By file count (`find <dir> -type f | wc -l`)

> **MEASUREMENT WARNING — read before trusting any `du` number in this repo.** Plain `du` here
> reports **512 KB for every file regardless of content**. `notes/STATUS.md` is 7,363 bytes and
> `stat` reports `512 blocks`; `data/substrate_director_kb_v1/E.pt` is 10,559,415,795 bytes and
> reports `10,312,192 blocks` (proportional). So MSYS/Git-Bash floors `st_blocks` at 512 — this is
> a **stat stub, not real NTFS allocation** (NTFS default cluster is 4 KB).
>
> **Consequence: plain `du` overstates any many-small-files directory by up to ~600x.** Always use
> `du --apparent-size` (or `find -printf '%s'`) in this repo. I initially reported
> `archive/watchdog_pings/` as "14 GB, the largest clean win in the repo". **It is 23 MB.** That
> claim was wrong and is corrected below; it is recorded here rather than silently fixed because it
> is the exact error class the standing triple-check rule exists to catch.

| dir | files on disk | `du` (WRONG) | **TRUE** (`--apparent-size`) | files `rg` lists | pruned cheaply? |
|---|---:|---:|---:|---:|---|
| `data/` | 47,114 | 172 G | **157 GB** | 8,983 | **NO** — see S3 |
| `.git/` | 16,158 | 12 G | **4.7 GB** | 0 | YES |
| `.venv/` | 44,579 | 23 G | **1.5 GB** | 0 | YES — `.gitignore:25` |
| `tools/` | 18,214 | 9.2 G | **578 MB** | 1,253 | YES — `.gitignore:86` |
| `experiments/` | 6,177 | 3.1 G | **168 MB** | 5,879 | n/a — searched, intentionally |
| `notes/` | 9,540 | 4.7 G | **109 MB** | 8,823 | n/a — searched, intentionally |
| `backups/` | 4 | 30 M | **29 MB** | 3 | n/a |
| `archive/watchdog_pings/` | 27,079 | 14 G | **23 MB** | 0 | YES — `.gitignore:136` |
| `preregs/` | 3,759 | 1.9 G | **16 MB** | 3,759 | n/a — searched, intentionally |
| `.tmp_scan/` | 31 | 21 M | **8.3 MB** | 31 | n/a |
| `hdlab/` | 310 | 155 M | **6.1 MB** | 155 | n/a |
| `verification/` | 164 | 83 M | **2.4 MB** | 76 | n/a |
| `scratch/` | 22 | 17 M | **911 KB** | 0 | YES — `.gitignore:79` |
| `lean_oracle/pythagoras_ip_v1/` | **121,688** | — | — | 11 | **YES** — nested `.gitignore:1:/.lake` |

**So: `data/` is 157 GB of the repo and essentially everything else is rounding error.** Outside
`data/` and `.git/`, the entire repo — all source, all notes, all experiments, all pre-registrations,
the venv — is under 2.5 GB.

### Largest `data/` subdirectories, TRUE size (`du --apparent-size`, re-measured after the artifact above)

These are dominated by genuinely large files, so allocated ≈ true here (unlike the table above).

| dir | TRUE size | refs in `notes experiments tools hdlab verification preregs` |
|---|---:|---:|
| `data/lambda_batch_results/` | **37 GB** | 28 |
| `data/cell2_results/` | **21 GB** | 10 |
| `data/skypilot_results/` | **13 GB** | **1** |
| `data/exp_substrate_director_kb_content_chunk_ingest_v1/` | **12 GB** | 4 |
| `data/substrate_director_kb_v1/` | 12 GB | canonical (live agent tool) |
| `data/llama_1b_results/` | 7.5 GB | 11 |
| `data/substrate_index/` | 7.4 GB | canonical |
| `data/testbed_pp8_week2/` | 4.3 GB | 43 |
| `data/exp_substrate_director_kb_language_trio_v1/` | 4.2 GB | — |
| `data/cornerstone_results/` | **4.0 GB** | **0** |
| `data/corpora/` | 3.6 GB | canonical |
| `data/gensim_cache/` + `data/gensim_cache_v2/` | 3.0 + 1.7 GB | 154 |

Largest single files: `data/substrate_director_kb_v1/E.pt` 9.83 GB; four **duplicate** `E.pt`
copies of 2.2-3.5 GB each inside `exp_substrate_director_kb_content_chunk_ingest_v1/` and
`_language_trio_v1/`; **15 x 1.00 GB Llama-3.1-8B probe checkpoints** in
`data/skypilot_results/exp_phase05_probe_training_v1/models/03jun/` differing only by
`val_sim=50%..60%`; `data/corpora/arc/ARC_Corpus.txt` 1.38 GB.

**Byte-identical duplicate confirmed:** `data/gensim_cache/word2vec-google-news-300/word2vec-google-news-300.gz`
and `data/gensim_cache_v2/.../word2vec-google-news-300.gz` are both exactly **1,743,563,840 bytes**
(mtimes 2026-06-23 14:35 and 20:01). Same-size/same-name; **I did not sha256 them** (2 x 1.6 GB on a
contended disk), so "duplicate" is high-confidence but not proven. ~1.6 GB reclaimable if confirmed.

**Triple-check on `lean_oracle`:** 121,688 files is the largest directory in the repo by a wide
margin and looked like an obvious offender. It is not. `git check-ignore -v` on a sampled deep file
returns `lean_oracle/pythagoras_ip_v1/.gitignore:1:/.lake` — it is the Lean/mathlib toolchain,
pruned at one directory node. `rg` never descends it. **Costs nothing to search. Not a problem.**

### By bytes actually read by a full-repo grep

Total: **596 MB across 29,558 files**, per grep.

| dir | bytes rg reads | note |
|---|---:|---|
| `data/` | **206.6 MB** | metrics/results JSON — un-ignored *by design*, see S3 |
| `experiments/` | 162.4 MB | 43.5 MB of it is `experiments/data/` corpora (conll2000, UD-EWT, ag_news) |
| `notes/` | 109.5 MB | 8,823 files |
| `extern/` | 79.8 MB | vendored `hyperprobe`; 33.5 MB is 22 `.xlsx` |
| `backups/` | 29.8 MB | 3 `.tar.gz` foundation snapshots |
| `tools/` | 18.4 MB | |
| `preregs/` | 16.0 MB | |

By extension: `.json` 170.7 MB / 7,677 files, `.py` 133.5 MB / 7,411, `.md` 111.3 MB / 12,622,
`.txt` 63.9 MB / 651.

Largest individual files a grep opens: `extern/hyperprobe/data/splitted_data.json` 19.0 MB,
`backups/foundation/2026-08-12/reading_grounding_v1_*.tar.gz` 15.5 MB,
`experiments/data/conll2000.json` 14.9 MB, `data/exp_wave14_continual_2N_10000edits/metrics.json`
**6.2 MB**, `notes/_mined_psych_candidates_raw.json` 8.8 MB, `notes/substrate_capability_map.md`
4.6 MB.

---

## S3. IS IT UNIGNORED BULK OR A TOOL-CONFIGURATION GAP? — **Unignored bulk, by design**

**Tool configuration is fine.** `rg` 14.1.1 respects `.gitignore` here, including nested ones
(proved by `lean_oracle`). There is **no `.rgignore` and no `.ignore`** in the repo. `.venv/`,
`archive/watchdog_pings/`, `tools/dashboard/.state/`, `__pycache__/`, `scratch/` are all correctly
pruned. Nothing is misconfigured.

**The cost is `data/`, and `.gitignore` un-ignores it deliberately** (lines 43-56, DECISION 220
"Tier-1 preservation sweep"):

```
data/*
!data/*/          <- forces rg to DESCEND into all 7,812 data subdirs
data/*/**
!data/*/metrics.json      !data/*/results.json
!data/*/provenance.json   !data/*/verdict.json   !data/*/recent_verdicts.json
```

The `!data/*/` negation is what makes `data/` expensive: 7,812 subdirectories (7,614 of them
`data/exp_*`) must each be opened, and 8,983 JSON files totalling 206 MB are then read on every
full-repo grep. This is *working as intended* — those JSON files are the tracked, permanent record
of every experiment.

### Measured cost of each strategy (3 runs, same pattern, warm cache)

| strategy | runs (ms) | speedup |
|---|---|---|
| full-repo `rg -l PATTERN` | 8506 / 8460 / 8831 | 1.0x |
| exclude binary+derived (`.tmp_scan`, `extern/*/outputs`, `backups`, `*.tar.gz`, `*.xlsx`) | 7824 / 9365 / 8511 | **1.0x — no gain** |
| exclude `data/**` | 1350 / 1650 / 1616 | **5.6x** |
| scope to `hdlab tools experiments verification notes` | 1231 / 1332 / 1297 | **6.5x** |

Cold-cache `rg --files` over the repo: 13.3 s.

---

## S4. NO IGNORE FILE WAS WRITTEN — and why that is the right call

I was prepared to add a purely-additive `.rgignore`. **I did not, because the measurement says it
buys nothing and the one exclusion that would help is unsafe.**

1. **Binary/derived exclusions gave zero measurable benefit** (row 2 above — within run-to-run
   noise, and slower on two of three runs). `rg` already binary-detects and abandons `.xlsx`,
   `.tar.gz`, `.npz`, `.pt` cheaply; adding `-g`/ignore rules adds per-file glob-matching cost that
   cancels the saving. Writing the file would add a config artefact every future agent has to reason
   about, in exchange for nothing.
2. **The only effective exclusion — `data/` — is exactly the one that must not be made.**
   `data/*/metrics.json`, `results.json` and `verdict.json` are **tracked in git** and are the
   record of whether an experiment ran. Hiding them from search is the *direct cause* of the
   failure mode this audit was commissioned to prevent: an agent grepping for an experiment,
   finding nothing, and reporting it as never-run. An `.rgignore` covering `data/` would make that
   failure permanent and silent.
3. I also checked for a subtler justification — derived **copies** of note text inflating results.
   There are none: `data/substrate_director_kb_v1/` and `data/substrate_index/` are **not
   rg-visible** (0 files in `rg --files`), and no file under `data/` contains prose from the notes
   (checked with a distinctive phrase). So there is no duplicate-hit problem to fix either.

**The fix is a convention, not a config file.**

### Proposed convention (documentation only, no behaviour change)

> **Default grep scope is `hdlab/ tools/ experiments/ verification/ notes/`.** That is 6.5x faster
> than a full-repo grep and covers all source, tooling and written findings.
>
> **Widen deliberately, not by default.** Add `data/` when you are looking for experiment
> *results* (metrics/verdict JSON) — and you must, before concluding an experiment did not run.
> Add `preregs/` for pre-registrations, `extern/` for vendored third-party code.
>
> **Never conclude "it does not exist" from a scoped or bare-relative search.** See S1.

---

## S5. RECLAIMABLE-SPACE INVENTORY — classification with per-item reference check

Reference check performed for every candidate:
`rg -l --fixed-strings "<name>" notes experiments tools hdlab verification preregs`.

### KEEP (canonical / cited / protected)

Sizes below are from the committed census in `notes/system_accounting_2026-08-13.md` S17, which
enumerates every data asset with its live reader. I did not re-measure these (`du` times out); I
cite it rather than assert independently.

| item | size | reference check | verdict |
|---|---|---|---|
| `data/substrate_director_kb_v1/` | 12 GB | census S17 row; queried by `tools/director_kb_query.py`; freshness-checked at session start | **KEEP** — live agent tool |
| `data/substrate_index/` | 7.6 GB | census S17; read by `backend/substrate_index/partition.py` | **KEEP** — canonical store, brief-protected |
| `data/corpora/` | 6.1 GB, 33 subdirs | census S17; OpenStax cited in 8+ notes dated 08-13 | **KEEP** — brief-protected |
| `data/conceptnet/` | 492 MB | census S17, one-shot ingester | **KEEP** |
| `data/cskg_foundation_v1/` | 258 MB | census S17, 1,213,912 edges; explicitly gitignored line 129 | **KEEP** |
| `data/foundation/`, `data/foundation_provenance_v1/` | 75 MB + 17 MB | census S17; underwrites the current arc's 2,092 facts | **KEEP** — brief-protected |
| `data/atomic_kb/`, `data/datasets/`, `data/lexicons/` | 58 / 79 / 2.5 MB | census S17 | **KEEP** |
| `lean_oracle/pythagoras_ip_v1/.lake/` | 121,688 files | Lean/mathlib toolchain, pruned by nested `.gitignore` | **KEEP** — costs nothing; regenerable via `lake` but no reason to touch |
| `.venv/` | 44,579 files | correctly ignored | **KEEP** |
| `data/exp_anchor_pool_expansion_v1/` | — | **live detached run, PID 9260 / worker 29624** | **KEEP — DO NOT TOUCH** |

### SAFE-TO-ARCHIVE (uncited, regenerable, summary preserved elsewhere)

| item | size / count | reference check result | verdict |
|---|---|---|---|
| `archive/watchdog_pings/` | **23 MB** (not 14 GB — see the measurement warning in S2), 27,079 files | **2 refs**, both describing its retirement, neither consuming it. Retired 2026-08-12; source disabled in `tools/hd_session_watchdog.py`; `.gitignore:136` guards regeneration. No note cites an individual ping. | **ARCHIVE, but DEPRIORITISED.** Safe to move, reclaims only 23 MB, and it already costs search nothing (pruned). The 27,079-file *count* is the real nuisance, not the bytes. Low priority. |
| `data/cornerstone_results/` | **4.0 GB** | **0 refs** across `notes experiments tools hdlab verification preregs`. The only multi-GB directory with zero citations. | **ARCHIVE candidate — now the best clean win by size.** >100 MB, listed for approval. Confirm provenance first; zero refs may mean "finished and forgotten" or "predates the notes corpus". |
| `data/skypilot_results/exp_phase05_probe_training_v1/models/03jun/` | ~15 GB within the 13 GB tree | **1 ref** for the whole `skypilot_results` tree. Contains **15 x 1.00 GB checkpoints** differing only by `val_sim=50%..60%` — a sweep where normally only the best is kept. | **ARCHIVE candidate (partial)** — keep the best-scoring checkpoint + `metrics.json`, archive the rest. Needs owner confirmation of which is canonical. |
| `data/gensim_cache_v2/` duplicate blob | 1.7 GB | 154 refs to `gensim_cache` generally; the **blob** is identical in name and byte-size to the one in `data/gensim_cache/` | **ARCHIVE candidate** — sha256 both first (not done here: 2 x 1.6 GB on a contended disk). Redownloadable model cache either way. |
| duplicate `E.pt` copies under `data/exp_substrate_director_kb_*` | 2.2-3.5 GB x 4 | 4 refs to `_content_chunk_ingest_v1` | **UNCLEAR-leaning-archive** — these are experiment reproductions of the 9.83 GB canonical `substrate_director_kb_v1/E.pt`. Determinism arms (`kb_a`/`kb_b`) may exist *because* the experiment compares them; do not assume redundancy. Read the cell before proposing. |
| `.tmp_scan/` | **8.3 MB** (21 MB by plain `du`), 31 files | **Triple-checked.** Contains OpenStax scouting intermediates (`col_osbooks-*.xml`, `tree_*.json`, `bio_before.txt`). **No file anywhere cites `tree_osbooks`/`col_osbooks`/`bio_test_out`/`bio_before` by name.** Regenerable: `data/corpora/openstax_common/fetch_openstax.py` re-fetches collection.xml + module CNXML from raw.githubusercontent.com, stdlib-only. Referenced only as a *skip-list entry* in `tools/integration_health.py:67` (`SKIP_DIR_NAMES`) — defensive, works whether or not the dir exists — and as "untracked scratch" in `notes/foundation_reproducibility_2026-08-13.md:158`. | **ARCHIVE** |

### S5a. STOP-THE-SWEEP FINDING: the DECISION 220 preservation contract has a 38% hole

Any archive proposal for `data/exp_*` rests on the assumption that *"the summary is safely committed
in git, so the bulk is disposable."* **I checked that assumption before relying on it, and it is
false for 38% of experiments.**

```
ls -d data/*/metrics.json | sort                                    -> 7,555 on disk
git ls-files data | grep -E '^data/[^/]+/metrics\.json$' | sort     -> 4,692 tracked
comm -23 (disk) (tracked)                                           -> 2,863 NOT tracked
git check-ignore --stdin < untracked_list                           -> 2 ignored by rule
```

So **2,861 `metrics.json` files are neither tracked nor ignored — they were simply never
committed.** They are untracked working-tree files that a commit pass would pick up.

*Triple-check on the method, because my first attempt got this backwards:* `git check-ignore -v`
prints a matching pattern **even when the match is a negation** (`!data/*/metrics.json`), so
"produced output" does not mean "ignored". Only the exit code distinguishes. Re-run with plain
`git check-ignore --stdin` (which lists only genuinely-ignored paths) the count is **2**, both under
`data/cskg_foundation_v1/` (`.gitignore:129`). The three big director-KB experiment dirs I spot-checked
(`_content_chunk_ingest_v1`, `_language_trio_v1`, `_bio_trio_ingest_v1`) all have `metrics.json` on
disk and **none is tracked**.

**Consequences, both material:**

1. **No `data/exp_*` archive sweep may run until those 2,861 files are committed.** Archiving the
   bulk first would destroy the only copy of the record for 2,861 experiments. Commit first, sweep
   second — in that order, non-negotiable.
2. This is a second, independent mechanism for **"a real experiment looks like it never ran."** An
   agent checking git history (rather than the working tree) for an experiment's result finds
   nothing for 38% of them. Combined with the S1 cwd trap, there are two distinct ways to get a
   false negative on the same question.

Recommended first action, ahead of any space reclamation: a review-and-commit pass over the 2,861
untracked `data/*/metrics.json`. That is a *preservation* action, costs ~no space, and is the
precondition for everything in S7 Tier 3.

### UNCLEAR (needs a decision, not an action)

| item | size | why unclear |
|---|---|---|
| `data/exp_*` bulk artefacts | **~166 GB across 7,614 dirs** | DECISION 220 *intends* `metrics.json` / `results.json` / `provenance.json` / `verdict.json` to be tracked and permanent, with everything else regenerable. **But see S5a: 2,861 of 7,555 `metrics.json` are not actually committed**, so the contract does not currently hold and the sweep is BLOCKED on a commit pass. Also 7,614 dirs cannot be adjudicated in one pass, and one is live. **Proposal: (1) commit the 2,861 untracked `metrics.json`; (2) only then, a per-directory sweep, oldest-first, keeping the four JSON files and archiving the rest. Not attempted here.** |
| `data/lambda_batch_results/` (36.5 GB), `data/cell2_results/` (20.8 GB), `data/llama_1b_results/` (10.4 GB), `data/testbed_pp8_week2/` (4.3 GB) | 72 GB combined | All **heavily cited** (28 / 10 / 11 / 43 refs respectively). These are the four largest reclaimable-looking directories and every one of them is referenced by working notes or code. **Do not archive on size alone.** Each needs a per-directory read of what still consumes it. |
| `backups/foundation/2026-08-12/*.tar.gz` | 28 MB, 3 files | Foundation snapshots from the day the grounding-quality arc was running. Cheap to keep; deleting a foundation backup while foundation validity is an open question is the wrong trade. **Recommend KEEP until the grounding arc closes.** |
| `extern/hyperprobe/outputs/` | 33.5 MB `.xlsx` + `.json` | Third-party experiment outputs from a vendored repo. Not cited by our notes, but it is someone else's artefact set inside a vendored tree; removing part of a vendored repo makes it non-reproducible against upstream. **Recommend KEEP.** |
| `data/` loose root files | 1,674 files | Not individually audited. Includes the two registry files in S6. |

---

## S6. THE 10 ORPHANED SCRATCH FILES

Source: `notes/subagent_denial_audit_2026-08-13.md` S3a — files whose deletion was attempted and
auto-denied (all 31 auto-denies contained an `rm`/`Remove-Item` token). **All 10 re-verified present
on disk today**, with real byte sizes (`stat -c%s`) and an individual reference check.

| # | path | size | referenced by | reference is... |
|---|---|---:|---|---|
| 1 | `hd-instrument/tools/_tmp_registry_triage_scan.py` | 5,455 B | `notes/registry_tighten_audit_2026-08-13.md:112`, denial audit | **Author explicitly authorises disposal**: *"read-only, stdout JSON. I could not delete it... It should be removed as part of the commit pass; it is throwaway, not a capability."* |
| 2 | `hd-instrument/_probe_corpus_count.py` (repo root) | 2,134 B | `notes/foundation_reproducibility_2026-08-13.md:158`, denial audit | Listed **as** untracked scratch, not as provenance of a number |
| 3 | `hd-instrument/notes/_forensics_scratch.py` | 8,389 B | denial audit only | no live citation |
| 4 | `hd-instrument/notes/_forensics_scratch2.py` | 2,123 B | denial audit only | no live citation |
| 5 | `hd-instrument/notes/_forensics_raw_output.json` | 12,243 B | denial audit; `notes/_forensics_scratch.py` (its own producer) | self-referential only |
| 6 | `hd-instrument/data/capability_registry.jsonl.bak_island_harvest` | 300,038 B | denial audit only | see triple-check below |
| 7 | `D:/AI/audit_script.py` (outside repo) | 9,254 B | denial audit only | no live citation |
| 8 | `D:/AI/audit_script2.py` (outside repo) | 7,541 B | denial audit only | no live citation |
| 9 | `hd-instrument/tools/_tmp_skunkworks_register_batch_2026-08-12.py` | 15,419 B | `tools/capability_registry_audit.py:623,715`; `notes/registry_tighten_audit_2026-08-13.md`; `notes/island_harvest_assessment_2026-08-12.md` | **prose only** — cited in a comment and a docstring as the *superseded* hand-rolled pattern that `append_rows()` replaces. **Not an import, not a runtime dependency.** |
| 10 | `hd-instrument/.tmp_scan/` (directory) | **8.3 MB**, 31 files | `tools/integration_health.py:67` (`SKIP_DIR_NAMES`) | **defensive skip-list entry, not a dependency** |

### Triple-check on #6, the stray registry copy — the denial audit's hazard claim is overstated

The denial audit flags this as *"a real hazard given the 'never `git add -A` on the canonical store'
standing rule."* Checked directly:

```
git check-ignore -v data/capability_registry.jsonl.bak_island_harvest
  -> .gitignore:43:data/*   (IGNORED)
git ls-files --error-unmatch data/capability_registry.jsonl
  -> data/capability_registry.jsonl   (TRACKED)
```

The `.bak` **is gitignored**; a `git add -A` would *not* pick it up. The hazard as stated does not
apply. Recording this correction so the claim is not propagated further.

It is, however, **not a redundant duplicate**: both files have 123 rows, but
`comm -23 <(sort bak) <(sort live)` returns **123** — every row differs. It is a genuine
pre-change snapshot (mtime 2026-08-12 15:46, before the island-harvest registration pass; live is
2026-08-13 05:15). sha256 live `b4cf5aaf...`, bak `afdc5940...`.

---

## S7. PROPOSED MOVES — pending approval, nothing done

Per the brief: move, never delete; nothing over 100 MB; nothing under `data/foundation*`,
`data/substrate_index*`, `data/corpora*` without listing for approval first. **`mv` is permitted but
I have executed none of it.**

**Tier 1 — uncited scratch, ~35 KB total, recommend approving as a batch.** Move to `scratch/`:

| from | to |
|---|---|
| `tools/_tmp_registry_triage_scan.py` | `scratch/` (author authorised disposal in writing) |
| `_probe_corpus_count.py` | `scratch/` |
| `notes/_forensics_scratch.py` | `scratch/` |
| `notes/_forensics_scratch2.py` | `scratch/` |
| `notes/_forensics_raw_output.json` | `scratch/` |
| `tools/_tmp_skunkworks_register_batch_2026-08-12.py` | `scratch/` — **caveat:** leaves two dangling prose citations in `tools/capability_registry_audit.py:623,715`. Either update those lines to say "(since moved to `scratch/`)" or leave the file where it is. Prefer updating the comment. |

Moving the three `notes/` files also removes them from the director-KB ingest surface, which scans
`notes/` — a small correctness win beyond the space.

**Tier 2 — needs an explicit yes:**

- `.tmp_scan/` (8.3 MB true) -> `scratch/`. Uncited and regenerable via `fetch_openstax.py`, but it is
  the provenance trail of the OpenStax corpus scouting pass and OpenStax is live in the current
  arc. Under 100 MB, so within the brief's limit, but I am not moving a corpus provenance trail on
  my own judgement.
- `D:/AI/audit_script.py`, `D:/AI/audit_script2.py` — **outside the repo**, in the parent working
  directory. Out of my declared scope; flagging only.
- `data/capability_registry.jsonl.bak_island_harvest` (300 KB) — a pre-change snapshot of the
  canonical registry. Sits under `data/`, adjacent to a canonical store. **Recommend renaming into
  a dated backups location rather than `scratch/`** (which is periodically wiped by
  `tools/clear_scratch.py`); a registry snapshot is worth more than scratch retention. Not moved.

**Tier 3 — LISTED FOR APPROVAL, all >100 MB so not moved by this audit.** Ranked by
(size x confidence), best first:

| candidate | reclaims (TRUE) | confidence | blocker |
|---|---:|---|---|
| 14 of 15 `val_sim=*` Llama probe checkpoints | **~14 GB** | medium-high — a sweep; only the best is normally canonical | which one is best/canonical |
| `data/cornerstone_results/` | **4.0 GB** | medium — 0 refs, but zero refs is ambiguous | confirm provenance |
| `data/gensim_cache_v2/` duplicate blob | **1.7 GB** | medium-high — identical name+size | sha256 both to prove it |
| `archive/watchdog_pings/` | **23 MB** | high confidence, negligible payoff | none; low priority |
| `data/exp_*` general sweep | up to ~100 GB | low until unblocked | **S5a commit pass first** |

Approximate total of the high/medium-high items: **~20 GB, without touching a single cited
artefact, a canonical store, `data/foundation*`, `data/substrate_index*` or `data/corpora*`.**

The four genuinely huge directories (`lambda_batch_results` 37 GB, `cell2_results` 21 GB,
`llama_1b_results` 7.5 GB, `testbed_pp8_week2` 4.3 GB — 70 GB combined) are **all heavily cited**
and are deliberately excluded from this list.

**Ordering matters:** do the S5a commit pass (preservation, ~0 space) *before* any Tier 3 move.

---

## S8. SUMMARY OF ACTIONS TAKEN

- Deleted: **nothing**. No `rm`/`Remove-Item` was attempted at any point.
- Moved: **nothing**.
- Committed / staged: **nothing**.
- Ignore files written: **none** — deliberately, see S4.
- Processes stopped: **none**. `data/exp_anchor_pool_expansion_v1/` was not read or written.
- Files written by this audit: **this file only.** Files owned by concurrent agents
  (`CLAUDE.md`, `notes/STATUS.md`, `notes/grounding_results_accounting_2026-08-13.md`,
  `notes/process_rules_2026-08-13.md`) were **read only, never written**.
- No tool call was denied during this audit.

### The three things that would actually change behaviour, in priority order

1. **S1 — the cwd trap.** `Glob` silently returns `No files found` for every bare repo-relative
   pattern because the working directory is `D:/AI`, not the repo. This is a live source of false
   "it does not exist" conclusions and costs nothing to fix (a convention, plus preferring `Grep`,
   which errors instead of lying).
2. **S5a — 2,861 uncommitted `metrics.json`.** The DECISION 220 preservation contract is 38% short.
   This blocks any space reclamation *and* is a second, independent way for a real experiment to
   look like it never ran. Fixing it costs no disk.
3. **S3/S4 — grep scope.** Scoping to `hdlab/ tools/ experiments/ verification/ notes/` is a
   measured **6.5x** speedup (8.5 s -> 1.3 s). No ignore file achieves this safely, because the only
   effective exclusion (`data/`) is precisely the content agents must be able to search.

### Corrections issued by this audit

- **`archive/watchdog_pings/` is 23 MB, not 14 GB.** Plain `du` in this environment reports 512 KB
  per file regardless of size (MSYS `st_blocks` floor). My own first-pass figure was wrong by ~600x
  and is corrected in S2. Any prior size claim in this repo derived from plain `du` on a
  many-small-files directory should be re-checked with `--apparent-size`.
- **The stray registry backup is NOT a `git add -A` hazard.**
  `data/capability_registry.jsonl.bak_island_harvest` is covered by `.gitignore:43 data/*`
  (verified with `git check-ignore -v`), contrary to the concern raised in
  `notes/subagent_denial_audit_2026-08-13.md` S3a. It is, separately, a genuine pre-change snapshot
  (123 rows, all differing from the live file) and worth keeping somewhere durable.
- **`lean_oracle/` is not a search problem** despite being the largest directory by file count
  (121,688). It is pruned at one node by a nested `.gitignore`.
