# metrics.json worktree-vs-HEAD forensics, 2026-08-13

READ-ONLY. No metrics file modified, nothing restored, nothing deleted, nothing committed.
`data/exp_anchor_pool_expansion_v1/` untouched; no process signalled.
All numbers recomputed off disk with `.venv/Scripts/python.exe` against `git show HEAD:<path>`.

## Headline: the framing in the request is wrong on its central claim

There was **no sweep, and nothing re-ran today.** The dirty metrics files are a **month-long
accumulation of run-after-commit drift**, one cell at a time, from 2026-07-03 to 2026-08-12.
Of 102 modified files only **25** differ in anything but a timestamp, and only **5** are worse
than HEAD.

## 1. Scope

`git diff --name-only --diff-filter=M -- 'data/*/metrics.json'` -> **102** files
(plus 3 deletions, below; plus 2 non-metrics JSON: `exp_causal_link_comprehension_fuller_v2/_start_marker.json`,
`exp_r1_multihop_iterative_cleanup_v1/partial_seed23_full.json`).

| class | count | evidence |
|---|---|---|
| CRLF-only (LF -> CRLF, byte-identical otherwise) | 18 | `git diff -w` empty; `od -c` shows `{\n` in HEAD vs `{\r\n` on disk |
| differ ONLY in `ts_iso` / `elapsed_s` | 59 | full recursive key-by-key compare, no other key differs |
| substantive change | 25 | see section 3 |

## 2. mtime clusters -- and why they exonerate today's commits

The 18 CRLF files are one tight cluster: **2026-07-03 14:28:08-10** (a bulk text-mode rewrite;
this is the documented CRLF hazard already carried in memory).

Everything else is **scattered across 24 separate days**, 1-16 files per day, each matching that
day's own experiment activity:

```
07-03:19  07-04:2  07-14:3  07-16:7  07-17:7  07-18:16 07-19:2  07-20:7
07-21:7   07-22:3  07-23:4  07-25:2  07-28:1  07-29:1  07-30:5  07-31:3
08-01:2   08-02:1  08-03:2  08-04:1  08-05:1  08-09:1  08-11:4  08-12:1
```

**Newest modified metrics.json mtime = 2026-08-12 10:21:26 -0400.**
`7d6036bca` (lemma_verb) committed **2026-08-13T03:03:20-04:00**; `eac20c620` (goal typing)
**2026-08-13T03:03:30-04:00**. Every mtime **precedes** both by at least 17 hours. Today's fixes
cannot be the cause. Zero files bear a 2026-08-13 mtime.

mtimes are trustworthy: `ctime == mtime` on every sample and `birth < mtime`, i.e. plain in-place
writes, not a `cp -p` restore that would preserve mtime while advancing ctime.

## 3. Cause: run-after-commit, not a sweep

Direction is unanimous and decisive: of the 73 files carrying `ts_iso` on both sides,
**73/73 have a worktree timestamp LATER than HEAD's; zero earlier.** The pattern is one cell at a
time: a cell is run, its metrics committed, then the same cell is re-run minutes to days later and
the re-run output is never staged.

Worked example, `exp_cold_placement_usefulness_v1` (times EDT / UTC):

```
11:03:05  _start_marker.json written, pid 33480, host FrameworkMPC
11:03:09  run finishes -> metrics.json (ts_iso 2026-07-14T15:03:09Z)
11:05:57  commit 3144bc27d captures THAT file
11:10:26  *_selftest/metrics.json rewritten
11:10:32  metrics.json rewritten (ts_iso 2026-07-14T15:10:31Z)  <- current on-disk content
```

No sweep driver, cron, or scheduled task was found that would touch 100 cells at once, and the
mtime scatter rules one out on its own. **Attribution: normal per-cell re-runs (queue runner /
agent-launched single cells) whose outputs were never re-committed.** Not attributable to any
single actor.

## 4. Classification of the 25 substantive changes

### DEGENERATE -- 1

**`data/exp_cold_placement_usefulness_v1/metrics.json`** (mtime 2026-07-14 11:10:32).
35 keys became `NaN`, 7 stratum counts collapsed to 0.

| key | HEAD | worktree |
|---|---|---|
| `gates.pred2` | `MIDDLE_BAND_PARTIAL_GLOSS_LIFT` | `INCONCLUSIVE_TOO_FEW_GLOSS_SOURCED` |
| `taxonomic.opaque_gloss_sourced.n` | 157 | 0 |
| `...opaque_gloss_sourced.exact_match_rate` | 0.03822 | NaN |
| `taxonomic.opaque_no_anchor.n` | 72 | 292 |
| `taxonomic.name_transparent.n` | 121 | 58 |
| `arbitrary.mechanism_opaque_gloss_sourced.n` | 21 | 0 |
| `population.well_pool_size` | 32251 | 32277 |

Graph invariants are **identical** across both runs (`n_nodes` 141511, `n_edges` 189654,
`n_degree1_total` 83538, `n_taxonomic_pool` 71389, `n_arbitrary_pool` 12149), so the substrate did
not change. What changed is that the second run saw **no glosses at all**.

Mechanism, read off the cell: line 164
`PROVENANCE_PATH = _REPO/data/exp_grounded_ingest_text_spoke_v1/provenance.json`, and
`load_provenance_glosses()` (line 519) **returns `({}, [])` silently when the file is absent** --
no warning, no verdict change. With `provenance_order` empty, `_prioritized_sample()` falls back
entirely to `rng.choice` over the unprioritised pool, which is exactly what the numbers show:
a different, gloss-free population (transparent 121 -> 58, gloss-sourced 157 -> 0,
no-anchor 72 -> 292).

The file itself is intact **in this checkout** (`data/exp_grounded_ingest_text_spoke_v1/provenance.json`,
mtime 2026-07-14 10:17, 500 `sample_order` entries, 416 with a gloss, tracked and clean) and its
mtime predates BOTH runs -- so the local repo would have found it. `_REPO` is
`dirname(dirname(__file__))`, so a copy of the cell staged outside this tree (remote/queue runner)
resolves `PROVENANCE_PATH` to a directory that does not exist there. Corroborating: the 11:10 run
wrote **no** `_start_marker.json` and appended **no** heartbeat line -- `_heartbeat.jsonl` and
`_start_marker.json` in that output dir both still stop at 11:03. The 11:10 metrics.json arrived in
that directory without the local run scaffolding around it.

**Diagnosis: a silent missing-input degradation on a run whose gloss dependency was not shipped
with it -- a real defect in the cell (absent input must hard-fail, not return `{}`), dated
2026-07-14.** The underlying data is not corrupt; HEAD holds the valid measurement.

### DEGRADED -- 4 (a real run overwritten by a later SELF-TEST stub)

In each case the on-disk file is a ~10-key self-test stub and the full result blocks
(`per_seed`, `results_by_unit`, `bands`, `params`, `construction_audit`) are **gone from disk**.

| file | HEAD verdict / mode | worktree | keys lost |
|---|---|---|---|
| `exp_situation_model_assembly_learned_identity_head_v1` | `HARD_FAIL` / lite | `SELFTEST_PASS` / self_test | -506 |
| `exp_situation_model_assembly_encoder_backed_v1` | `LOCALIZED_WALL` / lite | `SELFTEST_PASS` / self_test | -266 |
| `exp_situation_model_assembly_encoder_retrain_lite_v1` | `MIDDLE` / lite | `SELFTEST_PASS` / self_test | -253 |
| `exp_syntactic_role_agent_patient_voice_probe_v1` | `ENCODER_POSITION_ONLY` / full | `SELFTEST_PASS` / self_test | -99 |

Concretely lost from disk (still in git): the cross-voice failure numbers
`{'active_to_passive': 0.17916666666666667, 'passive_to_active': 0.1625}`; the REF_SPAN clean-loop
span `{'a_name_maintenance': 0.98, 'b_competitive_coref': 1.0, 'c_overwrite': 0.9838}`; the held-out
`q_agree 0.737->0.788` / `tuned loop 0.474->0.534`; the memorization evidence
`ef_consistency 0.672 held-out vs 1.000 train`.

This is the one genuinely damaging pattern found. Note the direction: **HEAD is right, disk is
wrong**, and the loss is of a NEGATIVE/FAIL result -- three HARD_FAIL/WALL/MIDDLE verdicts now read
`SELFTEST_PASS` on disk. A self-test run must not share an output path with the full run.

### IMPROVED -- 8 (worktree is the fuller or the only real run)

| file | change |
|---|---|
| `exp_depparse_v2_mst_cpu_v1` | `UNKNOWN: corpus_load_failed`, 1 seed, `uas=0.0` -> `MIDDLE_BAND`, 3 seeds, `uas=0.7895` |
| `exp_encoder_teacher_sparsifier_bypass_v1` | `CELL_CRASHED (RuntimeError: Expected all tensors...)` -> `DIAGNOSTIC_COMPLETE`, +135 keys |
| `exp_selective_overwrite_recall_nl_wm_readcond_v1` | self_test -> full, `WM_NL_PROVEN_VIA_READ_CONDITIONING`, +615 keys |
| `exp_wm_addressing_dg_precheck_v1` | self_test -> full, `PRECHECK_FAIL` (a real negative), +438 keys |
| `exp_compgen_native_bind_desaturation_sweep_v1` | smoke -> full: epochs 25->60, n_train 700->1400, n_heldout 140->280, +869 keys; verdict `GRACEFUL_EROSION` unchanged |
| `exp_counterfactual_do_operator_v1` | `run_mode` label smoke -> full; every number identical |
| `exp_cortex_integration_end_to_end_v1_smoke` | +37 keys of detail; `HARD_PASS` unchanged |
| `exp_scale_meaning_learn_arc_heldout_v3_relobj_selftest` | cpu -> cuda re-run; `SMOKE_PASS` unchanged, AUCs move in the 4th decimal |

### NEUTRAL -- 12

- **pid-only** (6): `exp_event_outcome_density_patient_signal_probe_v2_smoke`,
  `exp_learner_implicative_sign_supplied_generalization_v1`,
  `exp_relation_inference_gold_hardening_recheck_v1`, `exp_frame_primary_role_assigner_v1`,
  `exp_grounded_meaning_wire_lexical_fallback_v1_selftest`,
  `exp_fuzzy_shard_router_attractor_stage12_v1` (pid + wall-clock means only).
- `exp_coref_flag_fix_loop_principle_b_v1` -- pid + drive-letter casing `D:\` -> `d:\`.
- `exp_selective_overwrite_recall_nl_wm_novel_filler_composition_v1` -- final loss differs at 1e-9.
- `exp_stateful_core_situation_model_v1_selftest` -- self-test RNG swing (arm_a 0.50<->0.75), verdict unchanged.
- `exp_syntactic_role_agent_patient_voice_probe_v1__ckpt_seed_7_ARM_LPC_CAUSAL` -- 0.9583 -> 0.95, verdict unchanged.
- `exp_codex_claimvalidity` -- 26 AUROC/AUPRC shift by 0.01-0.02; **arm ordering preserved**
  (combo_structural_plus_frequency still best 0.6509->0.6707; frequency_baseline still worst
  0.5112->0.4962), `HARD_PASS` unchanged.
- `exp_wm_addressing_dg_fixed_projection_v1` -- +3/-1 keys, no numeric change.

## 5. Was the lemmatiser stem-mismatch the cause? NO

`notes/measurement_layer_drift_2026-08-13.md` documents the real mechanism: the store holds
over-stemmed keys (`appl`, `babi`, `cal`, `allel`, `apparatu`) minted by the OLD `lemma_verb`;
the fixed `lemma_verb` maps corpus text correctly (`apples -> apple`), the proper-noun table loses
1193 keys, and lookups on the frozen bad keys miss -> UNKNOWN 19 -> 131.

It does **not** explain anything here:

- **Date.** That mechanism dates to 2026-08-13 ~05:21Z. `exp_cold_placement_usefulness_v1` was
  written 2026-07-14 15:10Z, a month earlier. No modified metrics file has an 08-13 mtime.
- **Code path.** The mechanism runs through `hdlab/closed_class_lexicon.py::is_closed_class` and
  the corpus-derived proper-noun table over `data/foundation/reading_grounding_v1/store/`.
  `exp_cold_placement_usefulness_v1.py` imports neither; it reads
  `data/substrate_index/concept/relations.jsonl` and cached WordNet glosses from
  `data/exp_grounded_ingest_text_spoke_v1/provenance.json`, and does its own tokenisation.
- **Signature.** A stem mismatch thins a lookup table (drift note: 1193 keys lost, counts move).
  Here the gloss dictionary is empty (0 of 416) and the *sampling order* changed too -- an
  absent-file signature, not a key-space signature.

## 6. The deletions

Three tracked files deleted from the worktree, all under one anchor, all recoverable
(`git show HEAD:<path>`, none gitignored -- `git check-ignore` returns rc=1):

| path | HEAD content |
|---|---|
| `data/exp_lexicon_coverage_audit_barrier2_v1/metrics.json` | `HARD_PASS \| coverage_union_vn_pb_token=0.9893 \| type_level_frac(n=120)=0.9833 \| PREDICTION_2_lexicon_distinct_from_foundation_size=SUPPORTED` |
| `..._v1_smoke/metrics.json` | same HARD_PASS payload |
| `..._v1_selftest/metrics.json` | `SELFTEST_PASS`, ts 2026-07-17T11:28:08Z |

Context: `experiments/exp_lexicon_coverage_audit_barrier2_v1.py` and its prereg are also dirty, with
a matching edit that **moves the hand-judgments input out of the output dir**:

```
-HAND_JUDGMENTS_PATH = REPO / "data" / f"exp_{ANCHOR_NAME}" / "hand_judgments_v1.json"
+HAND_JUDGMENTS_PATH = REPO / "experiments" / f"exp_{ANCHOR_NAME}_hand_judgments_v1.json"
```

reason given in the diff: `.gitignore` only allowlists metrics/results/provenance/verdict under
`data/exp_*/` and would silently drop it. So the deletion looks **deliberate** -- the output dir was
cleared as part of relocating the input. It was left half-finished:

- `experiments/exp_lexicon_coverage_audit_barrier2_v1_hand_judgments_v1.json` exists (51076 bytes)
  but is **UNTRACKED** (`git ls-files` -> `??`). A load-bearing committed INPUT the cell
  integrity-checks against is currently not in git.
- The cell was never re-run, so the HARD_PASS has no on-disk artifact.
- The `.py`/prereg edits are themselves uncommitted for the same reason as the metrics: commit
  `48c0080ca` landed 2026-07-17T07:29:15, the file was edited at 07:29:58 (43s later) and never
  re-staged.

Nothing cites the anchor: 0 hits across `notes/`, `data/capability_registry.jsonl`, `PROGRESS.md`,
`data/cap_map.json`, `data/orchestrator_status_log.jsonl`.

(A 4th, unrelated tracked deletion exists: `prereqs/2026-06-23_substrate_continuous_tanh_attractor_dynamics_v1.md`
-- note the misspelled `prereqs/` directory, distinct from `preregs/`. Out of scope; recorded here
so it is not lost.)

## 7. Blast radius -- cited numbers that changed underneath

Every substantively-changed anchor was swept against `notes/` (9175 files),
`data/capability_registry.jsonl`, `PROGRESS.md`, `data/cap_map.json`,
`data/orchestrator_status_log.jsonl`.

**No claim is unsupported, because in every damaging case git still holds the cited value.** The
exposure is the inverse: a reader who opens the on-disk `metrics.json` as the evidence pointer for
a note will find a contradicting `SELFTEST_PASS`.

Affected pointers (all four DEGRADED cases):

| anchor | cited by | what the citation asserts | what disk now says |
|---|---|---|---|
| `syntactic_role_agent_patient_voice_probe_v1` | `notes/director_POST_COMPACTION_BACKUP_2026-07-30_NIGHT.md`, `notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`, `notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md`, `notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md`, `notes/interactive_extraction_situation_model_loop_design_and_first_probe_2026-08-01.md`, `data/orchestrator_status_log.jsonl` | cross-voice role transfer FAILS (0.179 / 0.1625) | `SELFTEST_PASS` |
| `situation_model_assembly_encoder_backed_v1` | `notes/director_POST_COMPACTION_BACKUP_2026-07-30_NIGHT.md`, `notes/research_cross_frame_entity_stability_lever_2026-07-31.md`, `data/capability_registry.jsonl` | `LOCALIZED_WALL` | `SELFTEST_PASS` |
| `situation_model_assembly_encoder_retrain_lite_v1` | `data/capability_registry.jsonl` (`encoder_retrain_minimal_unfreeze_top1_entity_reid_situation_model`, `WIRE_CANDIDATE`) | `MIDDLE`, q_agree 0.737->0.788 | `SELFTEST_PASS` |
| `situation_model_assembly_learned_identity_head_v1` | none found | `HARD_FAIL` (memorization) | `SELFTEST_PASS` |
| `cold_placement_usefulness_v1` | **none found** | -- | degenerate |

Mitigating: the registry entries key on the `.py` path, not on `metrics.json`, so no registry
witness dereferences a changed file. Cross-checked `notes/STATUS.md` -- none of the 25 appear in it.

## 8. Recommendation (NOT acted on)

**Split by class. Do not do one blanket thing.**

1. **RESTORE from git (5 files)** -- the 4 self-test-clobbered results plus
   `exp_cold_placement_usefulness_v1`. In all five HEAD is the real measurement and disk is a stub
   or a missing-input artifact, and three of the five are negative results that now falsely read
   `SELFTEST_PASS`. Highest value, lowest risk.
2. **COMMIT the worktree (8 IMPROVED + 12 NEUTRAL)** -- these are genuine later runs, several
   strictly more informative than HEAD (`depparse_v2` `UNKNOWN/uas=0.0` -> `MIDDLE_BAND/uas=0.7895`
   is the clearest). Committing them stops the drift recurring.
3. **NORMALISE the 18 CRLF files** -- either commit as-is or add a `.gitattributes` rule.
   No information content either way.
4. **RESTORE the 3 deleted barrier2 metrics AND track
   `experiments/exp_lexicon_coverage_audit_barrier2_v1_hand_judgments_v1.json`** -- the relocation
   is half-done and the load-bearing input is currently outside git.
5. **RE-RUN only `exp_cold_placement_usefulness_v1`** -- and only after the cell is fixed to
   hard-fail on a missing `PROVENANCE_PATH` instead of returning `({}, [])`. Restoring HEAD gives a
   valid number today; the re-run is for confidence, not recovery.

Two defects worth fixing regardless of what is done with the files:

- `load_provenance_glosses()` degrades silently on a missing input. Any absent load-bearing input
  must produce a hard verdict, not a quietly emptier population.
- A `self_test` run can overwrite a `full`/`lite` run's `metrics.json`. `get_output_dir` documents
  "SH-5 run-mode isolation" -- these four files show it did not hold for them.

## What was checked to rule out looking at the wrong thing

- **Wrong file** -- ruled out: every comparison is `git show HEAD:<exact path>` against the same
  path on disk, in one process, and the diffs were also read raw via `git diff`.
- **Wrong metric key** -- ruled out: comparison is a full recursive flatten of both JSON documents,
  not a hand-picked key list. An earlier pass under-reported because an over-broad ignore substring
  (`"_s"`) was silently swallowing `opaque_gloss_sourced`; the filter was narrowed to exact leaf
  names and the analysis re-run. The corrected pass is what section 4 reports.
- **Whitespace masquerading as change** -- ruled out and quantified: `git diff -w` plus `od -c`
  isolate 18 files as pure LF->CRLF.
- **Timestamp churn masquerading as change** -- ruled out and quantified: 59 files differ in
  `ts_iso`/`elapsed_s` and nothing else.
- **A legitimately changed code path (today's lemma_verb / goal_typing)** -- ruled out three ways:
  mtimes all precede the commits by >=17h; the cells do not import the changed modules; the
  numeric signature is absent-input, not stem-mismatch.
- **A different corpus** -- ruled out for the degenerate case: `n_nodes`, `n_edges`,
  `n_degree1_total` and both pool sizes are identical across the two runs;
  `relations.jsonl` mtime is 2026-06-19, before both.
- **A deliberate re-run** -- confirmed as the cause for most files (73/73 later timestamps,
  9 deliberate run_mode transitions) and treated as legitimate, not corruption. The deletions are
  likewise deliberate, with the motivating diff quoted.
- **A sweep** -- ruled out: mtimes span 24 days; no driver, cron, or scheduled task found that
  writes many cells at once.
