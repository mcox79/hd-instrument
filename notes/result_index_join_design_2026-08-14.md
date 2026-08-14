# Joining the result indexes: design + measured residue (2026-08-14)

Tool: `tools/result_index_join.py` (`--scan`, `--hook`, `--json`, `--self-test`).
Wired into `tools/session_start_hook.py` as the `result-index-join` probe.

## 1. The join key: the result-directory name `data/<dir>`

Chosen by measurement, not assumption. Candidates tested:

| candidate | measured join | verdict |
|---|---|---|
| `data/<dir>` result-dir name | ledger -> disk **1001/1038 = 96.4%** | **CHOSEN** |
| content-addressed `atom_id` | ledger -> registry **0 / 1925** | rejected |
| `anchor_name` inside metrics.json | equals dir name **66 / 7623** | rejected raw; used as ALIAS |
| registry `path[]` code paths | **189/189 exist on disk** | healthy, but a DIFFERENT plane |

Two structural facts fell out of the measurement and reframe the whole problem:

**(a) The registry and the ledger index DISJOINT UNIVERSES.** Their intersection on data-dirs is
**0**. `capability_registry.jsonl` indexes *code* (100 `hdlab/` paths, 96 `experiments/` paths);
`cert_ledger.jsonl` indexes *results* (`data/<dir>/metrics.json`). They were never two views of one
thing, so "make them agree" was never the right goal. There is no single key across all four
sources because there are two planes. The **result** plane joins on the dir name (3 of the 4
sources); the **code** plane joins on the repo-relative path. The bridge between planes is the
registry's `experiments/<stem>.py`, whose stem IS a result key: **74 of 89 stems are a real
`data/<dir>`** (the 15 misses are `_helper.py` shared cores and per-seed variants, correctly not
results).

**(b) `anchor_name` is systematically the dir name minus a leading `exp_`.** Hence
`key_aliases()`, which bridges that one prefix. Keying on `anchor_name` raw would have lost 99% of
the join; this is exactly the kind of near-miss that makes an index look empty and a real result
look never-run.

## 2. Where enforcement goes: the session-start hook, reporting a PERSISTED scan

`CLAUDE.md` is explicit that the durable anchor is the session-start read, not an OS cron: 11 `hd_*`
tasks disabled ~12 days unnoticed, the KB ingest 6 days unnoticed. A cron is one silent disable from
not existing. But a *read* depends on the agent choosing to do it. The hook depends on neither, which
is why the hook is the right home.

The scan costs **288s** (7885 dirs), far over the hook's <10s budget, so it is split exactly like the
already-proven `registry_report()`: `--scan` computes and persists to
`data/result_index_reports/`; `--hook` reads the newest persisted report and reports its **age**
(**0.6s**). Staleness of the checker is itself reported, so the checker going quiet is visible.

## 3. Making a result impossible to land unregistered

The honest answer is to **stop requiring registration at all**. 6566 results are unindexed because
registration is a manual step, and manual steps get skipped. This index is **DERIVED FROM DISK**
every run: there is nothing to remember to do, so there is nothing to forget. This is also
`CLAUDE.md` Evidence-discipline sec 2 ("enumerate from the filesystem, then reconcile to the
registry, never the reverse") applied as an implementation rather than as advice.

What transfers from industry practice, and what does not:

- **MLflow/W&B run registries** -- transfers: capture at the WRITE point, and one run = one
  content-addressed directory. Does NOT transfer: a tracking server, a daemon, a mutable UI-owned
  database. We already have the good half by accident: every cell writes `data/<dir>/metrics.json`
  atomically. That convention IS the run registry; it only lacked a reader.
- **Content-addressed artifact stores (DVC/git-annex)** -- transfers: identity by content hash so a
  rename does not orphan a result. Does NOT transfer: a second object store beside `data/`.
- **Model cards** -- does NOT transfer. Hand-written prose that must be remembered is precisely the
  failure mode here; `notes/capability_map.md` and `promotion_backlog.md` already rotted this way.
- **W3C-PROV provenance graphs** -- the `supersedes` edge transfers and is the one thing worth
  saving from the ledger (sec 5). The RDF machinery does not.

## 4. Tolerating the NEXT convention change

Any scheme keyed on today's verdict strings breaks exactly as this one did: verdict vocabulary went
13 distinct strings in June to 444 in July, and "scramble" appears ZERO times in June.

So floors are detected **by shape first, vocabulary second**, and the two detectors are *compared*:

- `shape_arms_dict` -- >=2 sibling dicts sharing >=1 common numeric key. The shape of every
  per-arm/per-seed block regardless of what the arms are called.
- `shape_token_pair` -- >=2 sibling numeric keys differing in exactly one token position at equal
  token length (`sem_gate` vs `sem_zavg`). A comparison leaves a symmetry in the NAMES; the symmetry
  survives renaming the arms.
- `FLOOR_TOKENS` -- broad, expandable, and **never used as a filter**.

The output that matters is **`STRUCT_ONLY`**: a result with a comparison shape but no recognised
token. That count IS the drift alarm. Measured now: **2009 of 7623 (26.4%)**. The tool raises this
as a defect rather than silently under-counting, which is the behaviour the old scheme lacked.

The self-test proves this end-to-end, including on a June-style blob with no modern vocabulary. It
also caught a bug in its own fixture: the first draft used `quuxfloor` as "unknown vocabulary", which
contains the known token `floor`, so the lexical detector fired and the test failed correctly.

## 5. Measured residue (scan 2026-08-14T16:47Z, 288.4s)

```
ON DISK (authoritative)   7623 results with metrics.json in 7885 data dirs
  dated 2487   UNDATED 5136  (67.4% -- bucketed, never dropped)
  floor shape  BOTH=4056  STRUCT_ONLY=2009  LEX_ONLY=398  NEITHER=1160

IN INDEX, NOT ON DISK     ledger 53   registry 13
ON DISK, NOT IN INDEX     6566 (86.1% of disk)
hdlab modules unregistered 61 of 143
```

The 53 dangling ledger keys are mostly **unexpanded shell brace patterns** written literally into
the index (`exp_..._seed_{7,13,19}`) plus one path bug where a `metrics.json` filename was stored as
a directory. Those are write-side bugs in whatever produced the rows, now visible.

### Corrections to the received account

- The ledger's **file mtime** is 2026-08-03, but its newest **row timestamp** is
  **2026-07-25T09:50Z (21 days)**. The last write was not a last *result*.
- Only **157 of 2031 ledger rows carry a string `ts` at all** (92% undated) -- worse than the 68%
  figure quoted for results generally.
- Unregistered `hdlab` modules measure **61 of 143** here (the standing figure is 62 of 141);
  consistent, but state the count with its date.

## 6. The dead ledger: SALVAGE THE EDGES, RETIRE THE ROWS

Recommendation: **do not revive it, and do not merge it wholesale. Extract the `supersedes` graph
into the derived index and let the rest go.**

Reasons, measured:

- Its per-row payload is **already reproducible from disk** -- `verdict`, `metrics_path` and cell
  identity all live in `metrics.json`, which the join reads directly. Reviving hand-written rows
  recreates the manual step that killed it.
- Its coverage is **1038 of 7623 results (13.6%)** and frozen 21 days ago. As an index it is
  strictly dominated by the filesystem.
- Its `supersedes` graph is genuinely the most valuable structure we own AND it is **partly broken
  in a way nobody had noticed**: 67 edges, 66 distinct targets, and only **14 resolve to any
  `atom_id` in the same file**. Targets are 16-hex digests (`0162ed34f9d0dd18`); `atom_id`s are
  qualified strings (`math::T3/EXP_...`); they match neither `cell_commit` nor `id`. **52 of 66
  edges dangle.** Merging as-is would import 52 broken edges into a healthy index.

So: harvest the **14 resolving edges** (they encode real "this result replaced that one" judgements
that exist nowhere else), re-express them keyed on the result-dir name, and record the 52 dangling
ones as an open triage item rather than silently dropping them. Then freeze
`cert_ledger.jsonl` read-only with a superseded-by pointer to the derived index, per the
"add a superseded-by line when you find something stale" rule.

Deliberately NOT done here: this note **proposes, it does not migrate**. Neither index was rewritten.
Note that `notes/cert_ledger_triage_2026-08-14.md` is owned by a parallel agent and may reach a
different conclusion on the same rows; reconcile before acting.
