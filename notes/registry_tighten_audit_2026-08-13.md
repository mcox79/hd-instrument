# Capability-registry tightening audit -- 2026-08-13

PROPOSE-ONLY. Nothing in `data/capability_registry.jsonl` was mutated by this pass (the audit
was run with `--dry-run`). Registry edits must be serialized; Director rules on dispositions first.

Fresh audit report: **`data/capability_registry_reports/registry-audit-20260813T020832Z.json`**
(supersedes the stale `registry-audit-20260812T224613Z.json`).

---

## 0. What `--dry-run` gates, and how to turn the island scan ON

`tools/capability_registry_audit.py` has TWO independent flags. The prior report's
"island scan skipped" was **not** caused by `--dry-run`.

| flag | what it gates |
|---|---|
| `--dry-run` | ONLY the final `write_registry(rows)` call at the end of `run_audit()` (line ~894). Every scan still runs; the report is still written to `data/capability_registry_reports/`. It suppresses the rewrite of the auto-computed fields `integration_status`, `used_by`, `last_audit_utc`, `pipeline_status`. |
| `--skip-hard-pass-scan` | The invisible-island scan (`scan_unregistered_hard_pass_anchors`, `data/exp_*/metrics.json` sweep). When set, `island_scan = {"candidates_high": [], "skipped": True}`. |

**To turn the island scan ON: simply omit `--skip-hard-pass-scan`.** It is ON by default.
Command used for this pass (no registry mutation, full island scan):

```
.venv/Scripts/python.exe tools/capability_registry_audit.py --dry-run
```

Runtime note: the scan is mtime-cached in `data/capability_registry_reports/hard_pass_anchor_index.json`.
This run scanned **8 fresh + 7474 cached** dirs and finished in well under a minute; the ">3 min"
cost is only paid on a cold cache.

---

## 1. Fresh numbers vs stale

| metric | stale 20260812T224613Z | fresh 20260813T020832Z |
|---|---|---|
| rows | 123 | 123 |
| WIRED | 65 | 65 |
| TRAPPED_SHARED | 28 | 28 |
| ISLAND | 28 | 28 |
| N_A_SHELVED | 2 | 2 |
| UNKNOWN | 0 | 0 |
| WIRED_AND_PIPELINE_USED | - | 10 |
| WIRED_BUT_NOT_PIPELINE_REACHABLE | - | 55 |
| unregistered hdlab modules | 61 | **61** (the mission brief said 62; disk says 61) |
| declared paths missing on disk | 0 | 0 |
| stale VET_PENDING | 1 (`cls_discrete_budget_consolidate_v6_replay`, 15.2 d) | 1 (same, 15.3 d) |
| island-candidate scan | **SKIPPED** | **RAN** |
| pass-shaped unregistered anchors (informational) | n/a | **3126** |
| HIGH-signal invisible islands (the alarm set) | n/a | **60** |

The 60 HIGH-signal invisible islands are listed verbatim in the fresh report under
`invisible_island_candidates_HIGH`. Cluster shape: `schema` (13), `situation` (12), `vamp` (6),
`coherence` (5), `valence` (4), `narrative` (4), `tom` (3), `appraisal` (3), plus 4 map-named.

Denominator note: `hdlab/` holds **140** `.py` modules (excl. `__init__.py`); 79 registered,
61 unregistered = **44% of the library has never been through the wire-or-shelve gate.**

---

## 2. THE EMBARRASSING GAPS -- load-bearing and unregistered (read this first)

### 2a. The registry GATE tooling is not in the registry

Only **three** `tools/` paths appear anywhere in `data/capability_registry.jsonl`:
`tools/benchmark_trap_check/propara_official_eval.py`, `tools/inflight_monitor.py`,
`tools/read_anne_glassbox_v2_honest_ledger.py`. Everything below is absent.
(`capability_registry_audit` / `capability_registry_query` / `integration_health` DO appear as
free text inside other rows' `provenance` strings -- that is a mention, not a row.)

| module | LOC | py importers | mandated by | why load-bearing |
|---|---|---|---|---|
| `tools/capability_registry_audit.py` | 1199 | 3 (incl. `verification/test_capability_registry_concurrency.py`) | CLAUDE.md "Capability tracking", SESSION STARTUP RITUAL | **THE wire-or-shelve gate itself.** It scans for unregistered hdlab modules but has no row for itself. |
| `tools/capability_registry_query.py` | 115 | 0 (CLI-only) | CLAUDE.md "Query it before building anything that might already exist" | the query-before-build surface. Not even a CLAUDE.md text mention, so the audit's own composed-entry fallback cannot rescue it. |
| `tools/integration_health.py` | 198 | 2 | -- | the import-graph engine BOTH registry tools depend on. If this is wrong, every WIRED/ISLAND verdict is wrong. |
| `tools/session_start_hook.py` | 187 | 0 (hook) | CLAUDE.md "SessionStart hook (enforcement, not advice)"; wired in `D:/AI/.claude/settings.json` | the enforcement mechanism for the whole durability regime. |
| `tools/director_kb_freshness_check.py` | 174 | 0 (CLI) | CLAUDE.md "Run at SESSION START (alongside capability_registry_audit.py)" | the other half of the session-start durability gate. |
| `tools/exp_checkpoint.py` | 141 | **126** | CLAUDE.md "Multi-unit cell checkpoint/resume (MANDATORY)" | highest-import tool in the repo; mandated by a MUST rule. |
| `tools/safe_queue.py` | 213 | 6 (incl. `capability_registry_audit.py`) | -- | the cross-platform lock backend `RegistryLock` depends on; the registry's own concurrency safety rests on it. |
| `tools/substrate_capability_registry.py` | 592 | 0 | audit docstring calls it a sibling system | one of the three capability-tracking systems the audit docstring documents. |
| `tools/substrate_capabilities_aggregate.py` | 301 | 0 | audit `--check-undecided` reads its output | produces `data/substrate_capabilities_view.json`, an INPUT to the audit. |

### 2b. Top 5 load-bearing UNREGISTERED hdlab modules

1. **`hdlab/tracing.py`** (170 LOC, 69 strict importers, 21 of them other `hdlab/` modules) --
   in the ACTIVE_PIPELINE closure. The trace event bus every public op emits into; CLAUDE.md's
   verification discipline is stated in terms of it ("Verification tests must pass with `tracing=False`").
2. **`hdlab/session_log.py`** (45 LOC, **245** strict importers) -- the single most-imported
   module in the repo, and it has never seen the gate.
3. **`hdlab/atoms.py`** (68 LOC, 82 importers, 7 in `verification/`) -- FHRR/HRR atom generation,
   the base VSA primitive. `hdlab/bundling.py` and `hdlab/binding.py` (its peers) ARE registered.
4. **`hdlab/modulators.py`** (93 LOC, 20 importers) -- in the ACTIVE_PIPELINE closure and listed
   by the audit's own `pipeline_reachable_hdlab_modules` output, yet unregistered.
5. **`hdlab/situation_model_multibank.py`** (148 LOC) -- in the ACTIVE_PIPELINE closure; the
   multi-bank capacity fix for the flat-bundle wall that MEMORY.md/notes treat as a landed organ.
   Its own docstring cites "capability_registry" while it has no registry row.

(Runners-up: `hdlab/grounding_acquisition_loop.py` 827 LOC / 27 importers; `hdlab/director_kb.py`
1151 LOC / 16 importers; `hdlab/atom_consultation.py` 978 LOC, real import in `hdlab/cortex.py`.)

---

## 3. Triage table -- all 61 unregistered hdlab modules

**Method (reproducible).** Consumer counts are STRICT-IMPORT ONLY: real `from hdlab.X import` /
`import hdlab.X` / `from hdlab import X` statements, plus `from .X import` and sibling bare
imports inside `hdlab/`. Scanned `tools/ hdlab/ experiments/ verification/ backend/ scripts/`
(13,395 `.py` files). Bare `hdlab.X` attribute TEXT matches were deliberately excluded -- see
section 5 (D3) for why that matters. LOC = physical lines.

Scratch tool used: `tools/_tmp_registry_triage_scan.py` (read-only, stdout JSON). I could not
delete it -- file deletion was blocked by the permission layer this session. **It should be
removed as part of the commit pass; it is throwaway, not a capability.**

**Disposition rule (explicit, so it can be argued with).**
- **REGISTER-AS-WIRED** = at least one strict importer in `hdlab/`, `tools/`, or `verification/`,
  OR a verified real import in a composed entry point, OR membership in the ACTIVE_PIPELINE
  import closure. I.e. reachable from library / CLI / certification code, not only from cells.
- **REGISTER-AS-ISLAND** = strict importers are `experiments/`-only. Real capability, trapped in
  the experiment layer, never reaches the library or the pipeline.
- **DEAD** = a named successor exists, with textual evidence.

Note on mapping to the file: `integration_status` is AUTO-COMPUTED and cannot be set by hand.
For `kind: "hdlab-module"` rows the audit returns WIRED on ANY consumer, so all 61 would
auto-compute WIRED once registered. The dispositions above are therefore proposals for
**`gate_decision`** (WIRE / ALREADY_WIRED vs SHELVE) plus the honest reachability tier, not for
`integration_status`.

### A. REGISTER-AS-WIRED (43)

| module | LOC | strict importers | evidence |
|---|---|---|---|
| `hdlab/tracing.py` | 170 | 69 | ACTIVE-PIPELINE closure; 21 hdlab/; 4 verification/; 44 experiments/ |
| `hdlab/modulators.py` | 93 | 20 | ACTIVE-PIPELINE closure; 5 hdlab/; 5 verification/; 9 experiments/; 1 other |
| `hdlab/situation_model_multibank.py` | 148 | 3 | ACTIVE-PIPELINE closure; 1 hdlab/; 1 verification/; 1 experiments/ |
| `hdlab/atoms.py` | 68 | 82 | 3 hdlab/; 7 verification/; 71 experiments/; 1 other |
| `hdlab/grounding_acquisition_loop.py` | 827 | 27 | 5 hdlab/; 2 verification/; 20 experiments/ |
| `hdlab/role_slot_summarizer.py` | 420 | 19 | real import in hdlab/cortex.py; 5 hdlab/; 1 verification/; 13 experiments/ |
| `hdlab/candidate_generator.py` | 153 | 38 | 4 hdlab/; 1 tools/; 33 experiments/ |
| `hdlab/session_log.py` | 45 | 245 | 4 tools/; 236 experiments/; 5 other |
| `hdlab/script_grain_acquisition_loop.py` | 515 | 14 | 2 hdlab/; 2 verification/; 10 experiments/ |
| `hdlab/consequence_learning_loop.py` | 474 | 13 | 3 hdlab/; 1 verification/; 9 experiments/ |
| `hdlab/learning.py` | 88 | 11 | 4 verification/; 7 experiments/ |
| `hdlab/store.py` | 100 | 4 | 3 hdlab/; 1 verification/ |
| `hdlab/arc_parser.py` | 243 | 31 | 2 hdlab/; 1 tools/; 28 experiments/ |
| `hdlab/pos_tagger.py` | 110 | 30 | 2 hdlab/; 1 tools/; 27 experiments/ |
| `hdlab/director_kb.py` | 1151 | 16 | 1 hdlab/; 2 tools/; 13 experiments/ |
| `hdlab/memory.py` | 76 | 16 | 1 hdlab/; 2 verification/; 12 experiments/; 1 other |
| `hdlab/multi_hop.py` | 361 | 6 | 2 tools/; 1 verification/; 3 experiments/ |
| `hdlab/clarify_gate.py` | 285 | 15 | real import in hdlab/cortex.py; 1 hdlab/; 1 verification/; 13 experiments/ |
| `hdlab/director_kb_chunk_ingest.py` | 551 | 11 | 1 hdlab/; 1 tools/; 9 experiments/ |
| `hdlab/refuse_gate.py` | 130 | 11 | real import in hdlab/cortex.py; 2 hdlab/; 9 experiments/ |
| `hdlab/chunked_attention.py` | 218 | 11 | real import in hdlab/cortex.py; 1 hdlab/; 1 verification/; 9 experiments/ |
| `hdlab/coref_distractor_suppress.py` | 432 | 7 | 2 hdlab/; 5 experiments/ |
| `hdlab/scene_segment.py` | 391 | 7 | 2 hdlab/; 5 experiments/ |
| `hdlab/wordnet_polarity_propagation.py` | 310 | 7 | 2 hdlab/; 5 experiments/ |
| `hdlab/context_retention.py` | 630 | 5 | real import in hdlab/cortex.py; 1 hdlab/; 1 verification/; 3 experiments/ |
| `hdlab/gsbc_graded_encoder.py` | 139 | 4 | 1 hdlab/; 1 verification/; 2 experiments/ |
| `hdlab/noise_channel.py` | 356 | 4 | real import in hdlab/cortex.py; 1 hdlab/; 1 verification/; 2 experiments/ |
| `hdlab/ablation.py` | 90 | 3 | 2 hdlab/; 1 experiments/ |
| `hdlab/experiment.py` | 159 | 35 | 1 verification/; 34 experiments/ |
| `hdlab/char_positional_encoder.py` | 258 | 15 | 1 hdlab/; 14 experiments/ |
| `hdlab/additive_map.py` | 307 | 15 | 1 verification/; 14 experiments/ |
| `hdlab/int8_dense.py` | 75 | 10 | 1 verification/; 9 experiments/ |
| `hdlab/event_centrality_coref.py` | 475 | 9 | 1 hdlab/; 7 experiments/; 1 other |
| `hdlab/glass_box_loop.py` | 349 | 7 | 1 verification/; 6 experiments/ |
| `hdlab/atom_consultation.py` | 978 | 6 | real import in hdlab/cortex.py; 1 hdlab/; 5 experiments/ |
| `hdlab/lm_eval_harness.py` | 248 | 4 | 1 verification/; 3 experiments/ |
| `hdlab/director_kb_bio_sources.py` | 778 | 3 | 1 hdlab/; 2 experiments/ |
| `hdlab/perceptron.py` | 253 | 3 | 1 hdlab/; 1 experiments/; 1 other (`backend/substrate_index/sequence_labeler.py`) |
| `hdlab/bigram_gap_measurement.py` | 214 | 3 | 1 verification/; 2 experiments/ |
| `hdlab/token_vocab.py` | 301 | 3 | 1 verification/; 2 experiments/ |
| `hdlab/goal_outcome_relation_grounded.py` | 530 | 2 | 1 hdlab/; 1 experiments/ |
| `hdlab/snapshots.py` | 52 | 2 | 1 hdlab/; 1 experiments/ |
| `hdlab/layer_075_structural_slot_filter.py` | 132 | 2 | 1 verification/; 1 experiments/ |

### B. REGISTER-AS-ISLAND (17) -- experiments/-only importers

| module | LOC | strict importers | evidence |
|---|---|---|---|
| `hdlab/arc_labeler.py` | 258 | 28 | 28 experiments/ -- de-facto shared, never reaches hdlab/tools/verification |
| `hdlab/mcscript_extraction.py` | 292 | 7 | 7 experiments/ |
| `hdlab/bayesian_inference.py` | 318 | 5 | 5 experiments/ |
| `hdlab/per_item_log.py` | 243 | 5 | 5 experiments/ |
| `hdlab/conformal.py` | 221 | 4 | 4 experiments/ |
| `hdlab/gpu_generated_streaming_attention.py` | 501 | 3 | 3 experiments/ |
| `hdlab/gpu_memory_budget.py` | 233 | 3 | 3 experiments/ |
| `hdlab/director_kb_math_sources.py` | 697 | 2 | 2 experiments/ |
| `hdlab/late_combine.py` | 343 | 2 | 2 experiments/ |
| `hdlab/temporal_trace.py` | 374 | 2 | 2 experiments/ |
| `hdlab/dg_pattern_separation.py` | 205 | 1 | 1 experiments/ |
| `hdlab/metrics.py` | 94 | 1 | 1 experiments/ (`exp_a1_recovery.py`) |
| `hdlab/modern_hopfield_readout.py` | 383 | 1 | 1 experiments/ |
| `hdlab/outcome_event_extraction.py` | 370 | 1 | 1 experiments/ |
| `hdlab/semantic_parser.py` | 698 | 1 | 1 experiments/ |
| `hdlab/whitening.py` | 133 | 1 | 1 experiments/ |
| `hdlab/word_learning_tool.py` | 113 | 1 | 1 experiments/ |

### C. DEAD (1)

| module | LOC | strict importers | superseded by (evidence) |
|---|---|---|---|
| `hdlab/streaming_attention.py` | 259 | 1 (`experiments/_substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v3_chunked_upload_core.py`) | `hdlab/gpu_generated_streaming_attention.py`. Successor's own docstring: *"Extends hdlab.streaming_attention: instead of pre-materializing (M, N) keys ... v3 chunked streaming attention was correct ... but wall_s was CPU-dominated ... v4 eliminates that entirely ... MEASURED@v4 M=100k REPL wall=0.30s (15-25x speedup)."* Note the successor does NOT import it -- the reference is docstring-only, so v3 is genuinely orphaned except by the historical v3 cell. |

Proposed DEAD handling = register with `gate_decision: SHELVE` + `supersedes` pointing at v4,
**not** file deletion (the v3 cell still imports it and cells are historical artifacts).

Only ONE module earned a DEAD call. Tempting-but-unsupported candidates I deliberately did NOT
call dead, because no successor is named anywhere on disk: `hdlab/metrics.py`, `hdlab/memory.py`,
`hdlab/experiment.py`, `hdlab/snapshots.py`, `hdlab/ablation.py`, `hdlab/learning.py` (the
original Phase-1 scaffold layer). Several still carry `verification/` importers.

---

## 4. Duplicates / stale versions (ONE CANONICAL VERSION rule)

### 4a. Confirmed duplicate FILE pair

| stale copy | canonical | evidence |
|---|---|---|
| `hdlab/_scratch_orig_goal_owner_select.py` | `hdlab/goal_owner_select.py` | The scratch file's own line 1 docstring literally reads `"""hdlab/goal_owner_select.py -- Component-5 goal-owner DIRECTED coherence-score organ (promotion, 2026-08-05).` -- it names the OTHER file as its own path, i.e. it is a copy. Already registered as `scratch_orig_goal_owner_select_stale_backup`, `gate_decision: SHELVE`, `integration_status: ISLAND`, 0 importers. **Registry already handles this one correctly; the FILE is the leftover.** Proposal: delete the file and mark the row `path_missing` / retire it. |

### 4b. Registry-ROW duplication (same path set, multiple rows)

The tightening rule's inverse problem: 15 paths appear in more than one row. Most are legitimate
(one file hosting several distinct capabilities). These are NOT legitimate -- identical path
lists, identical provenance string, generic "triaged 07-28" names:

| rows | shared path list | proposal |
|---|---|---|
| `readout`, `pattern_completion`, `cleanup_attractor` (3 rows, all `ALREADY_WIRED`) | `["hdlab/cleanup_family.py", "hdlab/iterative_attractor.py"]` -- byte-identical in all three | collapse to ONE canonical row (`readout`) listing the three sub-capabilities in `current_best_for`; the three rows differ only in `name`/`current_best_for` and share provenance "hdi_skunkworks triage 2026-07-28". |
| `superposition`, `composition` | both include `hdlab/bundling.py` | borderline: `composition` also covers `binding.py`+`concept_encoder.py`. Keep both, but `superposition` should declare `bundling.py` as its sole path (it does) -- no action, logged for completeness. |
| `kg_ingest`, `kgstore_hierarchical_candidate_retrieval_1_2M` | both include `hdlab/kg_traversal.py` | legitimate (ingest vs. sharded retrieval). No action. |
| `goal_typing.py` x4 rows, `goal_achievement.py` x3, `goal_owner_select.py` x2, `state_of_mind.py` x2, `frame_induction.py` x2, `self_improving_loop.py` x2, `coreference_resolver.py` x2 | -- | legitimate multi-capability-per-file. Flagged only so a future audit does not re-discover them as "duplicates". |

### 4c. Stale `_v2`/`_v3` siblings in `tools/` (unregistered, outside the gate entirely)

| versioned file | original beside it |
|---|---|
| `tools/backfill_registry_events_v2.py` | `tools/backfill_registry_events.py` |
| `tools/substrate_alias_enrichment_a_axis_v2.py` | `tools/substrate_alias_enrichment_a_axis.py` |
| `tools/substrate_alias_enrichment_a_axis_v3.py` | `tools/substrate_alias_enrichment_a_axis.py` (so v1/v2/v3 all coexist) |
| `tools/substrate_backfill_serves_capability_v1.py` | `tools/substrate_backfill_serves_capability.py` |

Also present: `tools/_tmp_skunkworks_register_batch_2026-08-12.py` -- a leftover one-off
registration script the audit's own docstring cites as the exact hand-rolled pattern
`append_rows()` was built to replace.

### 4d. Investigated and CLEARED (not duplicates -- recorded so they are not re-flagged)

| pair | why it is NOT a duplicate |
|---|---|
| `hdlab/director_kb_query.py` (521 LOC) vs `tools/director_kb_query.py` (169 LOC) | only same-basename pair across `hdlab/`+`tools/`. The tools one is a thin CLI: `from hdlab.director_kb_query import DirectorKBQuery, load_default_kb`. Both canonical in their own layer. |
| `hdlab/goal_outcome_relation.py` vs `hdlab/goal_outcome_relation_grounded.py` | the `_grounded` docstring states it is a *"CLEAN ABLATION ... reusing goal_outcome_relation.py's TRAIN_EXAMPLES / ... STRUCTURALLY UNCHANGED (imported, not reimplemented)"*. It imports the original; both are live. |
| `hdlab/chunked_attention.py` vs `hdlab/streaming_attention.py` vs `hdlab/gpu_generated_streaming_attention.py` | a genuine v-lineage, but `chunked_attention` is the base primitive with a REAL import in `hdlab/cortex.py`. Only the middle version (v3, `streaming_attention.py`) is superseded -- see section 3C. |
| `hdlab/situation_model_accumulate.py` vs `hdlab/situation_model_multibank.py` | accumulate imports multibank via a deferred `from .situation_model_multibank import MultiBankAccumulateRegister`; multibank is the declared capacity upgrade, not a copy. |
| `hdlab/composed_encoder_v3.py` | version-suffixed name but no v1/v2 on disk; already covered by row `hdlab_encoder_cluster_vwfa_ppmi_composed_v3`. |
| `hdlab/store.py` vs `hdlab/hd_fact_store.py` | `store.py` docstring: *"Persistent trace storage backed by DuckDB"* -- trace store, not fact store. Different capabilities. |

---

## 5. Two audit-tool defects found while doing this (propose fixing before the next mass registration)

**D1 -- `COMPOSED_ENTRY_PATHS` is 40% stale.** Of the five declared entries, `hdlab/substrate.py`
and `hdlab/pipeline.py` **do not exist on disk**. Only `hdlab/reasoner.py`, `hdlab/cortex.py`
and `CLAUDE.md` are real. The list is silently short two entries.

**D2 -- the composed-entry check is a bare substring match, so short generic stems get FALSE
WIRED.** `compute_integration_status` does `if base in src` where `base` is the module stem. Verified
false positives (substring present, real import absent) in `hdlab/cortex.py` / `hdlab/reasoner.py`:

| stem | substring hit | real import |
|---|---|---|
| `memory` | cortex.py, CLAUDE.md | NONE |
| `store` | cortex.py, reasoner.py, CLAUDE.md | NONE |
| `atoms` | cortex.py | NONE |
| `metrics` | reasoner.py, CLAUDE.md | NONE |
| `experiment` | reasoner.py, CLAUDE.md | NONE |
| `multi_hop` | reasoner.py | NONE |
| `tracing` | CLAUDE.md | NONE |
| `director_kb` | CLAUDE.md | NONE |

Real composed-entry imports (verified) are only: `role_slot_summarizer`, `refuse_gate`,
`clarify_gate`, `chunked_attention`, `context_retention`, `noise_channel`, `atom_consultation`
-- all into `hdlab/cortex.py`. Because a composed hit SHORT-CIRCUITS to `WIRED` ahead of every
other test, this defect can only ever *inflate* the WIRED count. **Some of the existing 65 WIRED
rows may be false WIRED for this reason -- I did not re-derive all 65 (see section 7).**

**D3 (related, in `integration_health.py`) -- `RE_HDLAB_ATTR` text-matches `hdlab.X` inside string
literals.** `hdlab/perceptron.py` and `hdlab/bayesian_inference.py` each read as **145 `tools/`
consumers** under the text proxy. Ground truth: 1 and 0. The 145 are atomize/cert-ledger scripts
containing data literals like `("hdlab.perceptron", "StructuredPerceptron")`. Under strict
imports both drop to 3 and 5 total. Every count in section 3 uses the strict measure.

---

## 6. Proposed order of operations (NOT executed)

1. Fix D1 + D2 + D3 first -- otherwise 61 new rows get registered against a known-inflating
   WIRED computation.
2. Register the 9 gate/infra `tools/` modules from section 2a (`kind: "tool"`; the registry
   already has 2 rows of that kind, so the schema supports it).
3. Register the 43 WIRED + 17 ISLAND + 1 DEAD hdlab modules from section 3, in ONE
   `--append-json` batch through `append_rows()` (the locked transaction), never a hand-rolled
   load+write script.
4. Collapse the 3 `cleanup_family`/`iterative_attractor` rows to one.
5. Delete `hdlab/_scratch_orig_goal_owner_select.py`; retire its row.
6. Rule on the 60 HIGH-signal invisible islands (separate pass -- experiments/-layer, not hdlab/).
7. Rule on the stale VET_PENDING row `cls_discrete_budget_consolidate_v6_replay` (15.3 days).

---

## 7. What I could NOT verify

- **I did not re-derive the existing 65 WIRED / 28 TRAPPED_SHARED / 28 ISLAND verdicts from
  scratch.** Given defects D2 and D3, an unknown number of those 65 WIRED rows may be false
  WIRED. I proved the defects exist and are load-bearing; I did not quantify how many current
  rows they affect. That is a follow-up pass.
- **`hdlab/reading_grounding_loop.py` and `experiments/exp_grounding_quality_readout_v1.py` were
  not opened** -- a concurrent agent owns them. `reading_grounding_loop.py` does not appear in
  the unregistered-61 list, so it is registered; I did not check its status.
- **Sub-package modules are outside the audit's blind spot check.** `scan_unregistered_hdlab_modules`
  uses `os.listdir(hdlab)` (top level only), so `hdlab/dashboard/*.py` and any other subpackage is
  never scanned for registration at all. I noted this but did not enumerate those files.
- **Dynamic / string-keyed dispatch is invisible to every measure used here.** A module loaded via
  `importlib` or a registry-of-names would read as 0 importers. The audit docstring claims a
  zero-hit `importlib|__import__` grep over the 5 pipeline entry points as of 2026-08-02; I did
  not re-run that grep repo-wide.
- **"Real capability" in the ISLAND bucket is a read of the docstring + LOC, not a validation.**
  I did not run or test any of the 17 ISLAND modules. Some may be broken.
- **The 3126 pass-shaped unregistered anchors were not triaged**; I report only the count the
  tool produced and the 60-item HIGH-signal subset it flagged. The tool's own comment concedes
  the collapse heuristic is conservative and may over- or under-merge lineages.
- **`hdlab/` module count of 140 excludes `__init__.py`** and any file in a subdirectory.
- **No claim about whether any ISLAND module SHOULD be wired.** That is a Director judgment; this
  pass only establishes what is and is not reachable today.
