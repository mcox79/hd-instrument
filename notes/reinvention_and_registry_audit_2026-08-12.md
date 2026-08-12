# Reinvention check + registry repair (skunkworks audit, 2026-08-12)

## TASK A -- did we rebuild something we already own?

**Module under audit:** `hdlab/definitional_extraction.py` (built today, commit `b8b108a1d` initial,
`01093ac1f` guard-tightening, `7f57b5b84` wired into `exp_definitional_grounding_v3.py`).
5 surface patterns: COPULA, APPOSITIVE, GLOSSARY_COLON, CALLED, REFERS_TO -> `Definition(definiendum,
definiens, pattern, head, ...)`.

**Search performed (not assumed):**
- `git log -S"definiendum"` / `-S"appositive"` across full history -- only today's own commits.
- `grep -rl "copula\|appositive"` across `hdlab/` and `experiments/*.py` -- hits are unrelated modules
  using "copula"/"appositive" as linguistic vocabulary in docstrings/comments (e.g.
  `coref_distractor_suppress.py`, `goal_owner_select.py`), none implement a definitional extractor.
- `capability_registry.jsonl` blob search for `definit`/`extract` -- no row implements this job
  (`animacy_lexicon_wordnet_glassbox` matched only because "definitional" appears in prose, not as a
  capability).
- The "0.90 reading extractor" cited repeatedly in `notes/SUBSTRATE_CHARTER_read_first.md` and the
  BACKUP doc traced to its actual source: `experiments/exp_stated_entity_fate_reading_extractor_v2_
  highprecision.py` (commit `1226df078`, "filtered hand-checked precision 0.90 fresh independent
  100-sample"). That module extracts `(entity, fate_via_verb, FATE)` -- i.e. does a physical object get
  CREATED/MOVED/DESTROYED -- via SVO/passive argument-structure + a 66-verb fate lexicon. It is a
  **process/state-change extractor**, not a definitional ("X is a Y") extractor. DISJOINT job.
- MAVEN-ERE modules (`experiments/exp_maven_ere_convergence_gated_causal_v{1,2}.py`,
  `..._subevent_v1.py`) = causal/subevent RELATION classification (registry: F1 14.78 causal /
  13.63 subevent). DISJOINT job.
- `hdlab/thematic_role_labeler.py`, `hdlab/frame_induction.py` = thematic-role assignment /
  frame-primary-role, reused (not duplicated) by `definitional_extraction.py` for `lemma_word`.
  DISJOINT job.
- `hdlab/reading_grounding_loop.py` (concurrent-session file, read-only check) contains only a
  cross-reference comment to today's `notes/definitional_grounding_v3_2026-08-12.md`, no independent
  implementation.

**VERDICT: novel / DISJOINT.** No prior hdlab or experiments module implements copula/appositive/
glossary-colon/called/refers-to definitional-sentence extraction. The registry-query returning 0/107
was correct, not a symptom of registry incompleteness in this specific case -- the capability genuinely
did not exist before today. (The registry IS incomplete for other reasons -- see Task B.)

**Caveat (disclosed, not softened):** the underlying grounding-cell experiment
(`exp_definitional_grounding_v3`) is verdict `STRUCTURAL_PASS_PENDING_B3` -- the DEF-vs-DIST comparison
requires B3 hand-scoring not yet done. The extractor's own 12-case regression self-test passes; the
CELL's overall claim is not yet closed.

---

## TASK B -- registry repair

### B.1 True audit numbers (measured via `.venv/Scripts/python.exe tools/capability_registry_audit.py`,
full non-dry-run, ~3min; JSON dry-run cross-check also run)

- `n_rows` (before repair) = **107** (this figure WAS accurate; the stale figure was the
  "69 unregistered" count, not 107).
- `integration_status_counts`: WIRED=54, TRAPPED_SHARED=22, ISLAND=29, N_A_SHELVED=2, UNKNOWN=0.
- `pipeline_status_counts` (of the 54 WIRED hdlab-module rows): WIRED_AND_PIPELINE_USED=10,
  WIRED_BUT_NOT_PIPELINE_REACHABLE=44.
- **`unregistered_hdlab_modules` = 77** (NOT 69 -- the prior figure is stale/wrong; measured fresh
  this session against 141 total `hdlab/*.py` files, 141-77=64 covered by an existing registry `path`).
- `path_missing_flags` = 0 (no registered row points at a deleted/moved file).
- `undecided_validated_capabilities` (chain-grade families with no registry row) = 0.
- `stale_vet_pending` = 1 (`cls_discrete_budget_consolidate_v6_replay`, 15.0 days stale).
- `invisible_island_candidates_HIGH` (pass-shaped, unregistered, organ-keyword+real-cell or map-named)
  = 60 (informational; `invisible_island_candidates_ALL_count` = 3125 raw pass-shaped unregistered
  anchors, NOT an actionable alarm by design).

The full non-dry-run run ALSO refreshed `integration_status`/`used_by`/`last_audit_utc` on all 107
pre-existing rows (its documented job) -- this explains the large git diff on the registry commit
(113 insertions / 107 deletions is a full-file rewrite: 107 legitimately-refreshed rows + 6 new rows,
not corruption; spot-checked row 0 `gated_fusion_relation_inference` -> `integration_status`
correctly recomputed to `TRAPPED_SHARED`).

### B.2 Registered (6 rows appended, A5-gated: tmp+os.replace, verify-load, integrity check,
row-count assert, duplicate-id assert -- script: `tools/_tmp_register_6_modules.py`, run once,
left on disk untracked, not committed)

| id | path | gate_decision | target / evidence |
|---|---|---|---|
| `gap_detector_familiarity_gate` | hdlab/gap_detector.py | **WIRE** | live import in `hdlab/reading_grounding_loop.py:96` (GAP_FLOOR=0.625 gate), also imported by `gap_driven_reader.py`+`foundation_persistence.py`. `exp_gap_detection_autonomous_confidence_v1` HARD_PASS (4/4 axes, t1_auc=1.0, t1_dprime=5.15). |
| `gap_driven_reader_self_directed_order` | hdlab/gap_driven_reader.py | **WIRE** | `exp_gap_driven_reader_controlled_v1` HARD_PASS full ("all bands cleared >5% margin"). NOT yet imported by `reading_grounding_loop.py` (grep-verified zero hits) -- honestly flagged as validated-but-not-yet-wired-into-the-pipeline. |
| `foundation_persistence_roundtrip` | hdlab/foundation_persistence.py | **WIRE** | `exp_foundation_validation_harness_v1` HARD_PASS_foundation_validated (3/3 claims); consumed directly by `exp_reading_grounding_loop_cycle2_v1.py`/`cycle3_groundingfix_v1.py` (concurrent-session cells). Not yet imported inside `reading_grounding_loop.py`'s own module body -- persistence currently invoked at cell layer. |
| `closed_class_lexicon_function_word_gate` | hdlab/closed_class_lexicon.py | **WIRE** | live import in `reading_grounding_loop.py`, `definitional_extraction.py`, `low_information_filter.py`. Corpus-measured (UD EWT majority-tag + spaCy stopwords), not hand-listed. |
| `definitional_extraction_surface_patterns` | hdlab/definitional_extraction.py | **VET_PENDING** | verdict STRUCTURAL_PASS_PENDING_B3; do not WIRE into the grounding-object selector until B3 hand-scoring lands. |
| `low_information_filter_pmi_flatness_gate` | hdlab/low_information_filter.py | **VET_PENDING** | same parent cell, same pending status; PMI floor calibrated off closed-class reference distribution (p75=2.10, measured on 32,955 sentences). |

Verified post-write: all 6 disappear from `scan_unregistered_hdlab_modules()`; remaining count
107->113 rows, 77->71 unregistered hdlab modules. Registry file committed alone (targeted path,
no `git add -A`): commit `411d2fb6f` on branch `dataprep/mcguffey-graded-corpus`, local only, no push.

### B.3 Triage of the remaining 71 unregistered `hdlab/*.py` modules (NOT mass-registered)

Consumer counts computed directly from `integration_health.compute_import_graph()` (same graph the
audit tool uses), not assumed. Full ranked list (module: n_consumers, sample consumers) captured in
this session's tool output; key groups:

**Zero consumers anywhere (true islands, n=5):** `hdlab/_scratch_orig_goal_owner_select.py` (name
says "scratch" -- almost certainly a backup/working copy, recommend SHELVE or delete-candidate, not
register), `hdlab/compose_freq_routing.py`, `hdlab/excitability.py`, `hdlab/profiling.py`,
`hdlab/self_manager.py`. Recommend: SHELVE (revival criteria = "consumer needed" TBD) rather than WIRE
-- registering an island as WIRE would misrepresent status.

**Heavily-used but unregistered (top of the list, likely genuine registry gaps, not orphans) --
recommend WIRE on next pass with real evidence per row, not batch:**
`hdlab/session_log.py` (236 consumers), `hdlab/atoms.py` (76), `hdlab/tracing.py` (64),
`hdlab/candidate_generator.py` (39 -- the POS-tagger+arc-parser frontend `definitional_extraction.py`
itself depends on transitively), `hdlab/arc_parser.py` (35), `hdlab/experiment.py` (34),
`hdlab/pos_tagger.py` (34), `hdlab/arc_labeler.py` (29), `hdlab/grounding_acquisition_loop.py` (27),
`hdlab/int8_dense.py` (26), `hdlab/lexical_similarity.py` (23 -- notable: this is the module the
Director's spawn prompt described as "now available" post-concurrent-session-close; it is currently
UNREGISTERED despite 23 consumers, a real gap worth closing next).

**Possible DUPLICATE/overlap pairs flagged for inspection (not confirmed duplicates -- names
suggest overlap, contents not diffed this pass):**
- `hdlab/semantic.py` vs `hdlab/semantic_parser.py` -- both semantic-layer, different consumer sets
  (semantic.py: hdlab/__init__.py + hdlab/ablation.py; semantic_parser.py: hdlab/concept_encoder.py +
  1 exp cell). Needs a content diff before any consolidation call.
- `hdlab/grounded_similarity.py` vs `hdlab/lexical_similarity.py` -- both similarity-scoring, disjoint
  consumer sets so far; worth checking for logic overlap given today's grounding work touches both
  families.
- `hdlab/streaming_attention.py` vs `hdlab/gpu_generated_streaming_attention.py` vs
  `hdlab/chunked_attention.py` -- 3 attention-mechanism variants, likely legitimate GPU-scale variants
  (different consumer clusters: `_substrate_cortex_hippo_dense_commercial_M_*` cells), not an obvious
  duplicate, but same-family enough to warrant one row grouping them if WIRE'd.

**No registered-vs-disk disagreement found** among the 6 newly-registered modules or spot-checked
high-consumer modules (`path_missing_flags` = 0 project-wide).

Everything else in the 71 (roughly 55 modules) = mid-single-digit-to-teens consumer counts, mostly
legitimate but small/utility hdlab pieces (`director_kb_*`, `mcscript_extraction.py`,
`event_centrality_coref.py`, `role_slot_summarizer.py`, `outcome_event_extraction.py`, etc.) --
deferred to a future pass; recommend triaging in batches of ~10 with real WIRE/SHELVE evidence per
row rather than one bulk sweep, per the project's own no-blind-registration rule.

### B.4 Is the audit's own detection trustworthy?

**Yes, verified by direct test, not assumed.** Ran
`scan_unregistered_hdlab_modules()` against the live registry (flagged `hdlab/gap_detector.py` as
unregistered = True), then re-ran it against a synthetic copy of the rows list with one extra row
`{"id": "TEST_PROBE", "path": ["hdlab/gap_detector.py"]}` appended in memory only (no disk write) --
`gap_detector.py` correctly dropped out of the unregistered set. Detection mechanism (disk `glob(hdlab/
*.py)` diffed against every row's `path` list) is confirmed to work as designed, not merely assumed
from its docstring.
