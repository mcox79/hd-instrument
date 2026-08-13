# System accounting: what exists, what runs, what is reachable (2026-08-13)

READ-ONLY census. No code modified, nothing committed, `data/exp_anchor_pool_expansion_v1/` untouched,
no process killed. Written to answer "what exists?" rather than "does the registry list match disk?" --
because two audits earlier today both missed a whole working subsystem by auditing compliance with a
list instead of asking what is on disk.

**Interpreter matters.** `python` on PATH is system Python 3.12.10 and LACKS `duckdb`; the repo `.venv`
has it (1.5.2). Under system Python, `pytest verification/` dies with 4 collection errors
(`test_algebra`, `test_reproducibility`, `test_semantic_trace`, `test_trace_faithfulness` -> `hdlab/store.py:9
import duckdb`). Everything below was run with `.venv/Scripts/python.exe`. Any audit that used bare
`python` produced false ERRORs.

Working tree: branch `dataprep/mcguffey-graded-corpus`, HEAD `19754614c`, many modified files
(mostly `data/**/metrics.json`); `hdlab/` itself is clean vs HEAD.

---

## 0. HEADLINE COUNTS

| quantity | value | how measured |
|---|---|---|
| `.py` files in `hdlab/` (excl. `__init__.py`) | **141** (58,083 lines) | `ls` + `wc -l` |
| ...plus subpackages | `hdlab/learner/` 8 files (745 lines), `hdlab/dashboard/` 4 files (483 lines) | `wc -l` |
| assigned to a subsystem below | **141 / 141**, no duplicates, no omissions | machine-checked, see S0 |
| import cleanly under `.venv` | **141 / 141** (zero import failures) | one-shot `importlib` sweep |
| reachable from the LIVE path | **35 / 141** (32 eager + 3 lazy) | runtime `sys.modules` trace |
| NOT reachable from the live path | **106 / 141** | same |
| have a `__main__` self-test | **81 / 141** | regex on `^if __name__` |
| registry rows | **123** | `data/capability_registry.jsonl` |
| hdlab modules WITH a registry row | **79 / 141** | path join |
| hdlab modules with NO registry row | **62 / 141** (incl. `grounding_acquisition_loop`, a live entry point) | path join |
| experiment cells | 5,745 `.py` in `experiments/` | `ls` |
| experiment result dirs with `metrics.json` | **7,551** | walk of `data/*/metrics.json` |
| `tools/` | 1,016 `.py` + 11 subdirs | `ls` |
| `verification/` | 72 scripts (45 `test_*`, 25 `verify_*`, 2 `witness_*`) + `oracle`/`theory`/`run_certification` | `ls` |

Registry status distribution (verbatim field values):

- `integration_status`: `WIRED` 72, `ISLAND` 25, `TRAPPED_SHARED` 24, `N_A_SHELVED` 2.
- `pipeline_status`: `WIRED_BUT_NOT_PIPELINE_REACHABLE` 57, `N_A` 55, `WIRED_AND_PIPELINE_USED` 11.

---

## S0. THE LIVE PATH, MEASURED

The live path is `hdlab/reading_grounding_loop.py` + `hdlab/grounding_acquisition_loop.py`.
Runtime trace (import both, list `sys.modules`), **not** grep:

```
.venv/Scripts/python.exe -c "import sys; import hdlab.reading_grounding_loop, hdlab.grounding_acquisition_loop;
                             print(sorted(k for k in sys.modules if k.startswith('hdlab')))"
-> 40 entries = 32 top-level modules + the `hdlab` package + 7 `hdlab.learner.*` entries
```

The 32 eager: `ablation, animacy_lexicon, atoms, binding, bundling, cleanup_family, closed_class_lexicon,
consequence_learning_loop, coreference_resolver, event_bundle, frame_induction, gap_detector, goal_typing,
grounded_similarity, grounding_acquisition_loop, hd_fact_store, iterative_attractor, lexical_similarity,
memory, modulators, reading_grounding_loop, role_slot_summarizer, self_improving_loop, semantic,
situation_model_accumulate, snapshots, state_of_mind, thematic_role_labeler, tracing, verb_lexical_similarity,
working_memory` (+ `hdlab.learner` and its 4 plugins).

Plus **3 LAZY** (imported inside `StructuralFrontEnd._load`, `reading_grounding_loop.py:300-303`, so they
are on the live path but invisible to an eager import trace): `pos_tagger`, `arc_parser`, `arc_labeler`.

**Data the live path actually opens** (only these):
- `data/frontend_assets/pos_tagger_ud_ewt_upos.json` (5.3 MB), `arc_parser_richfeat_ud_ewt.npz` (2.7 MB),
  `arc_labeler_hashed_ud_ewt.json` (16.1 MB) -- constants at `reading_grounding_loop.py:244-247`.
  (`arc_parser_hashed_ud_ewt.npz` and `arc_parser_mst_retrain_ud_ewt.npz` also exist and are NOT loaded.)
- `data/closed_class_lexicon_v1.json` (`closed_class_lexicon.py:65`).
- `nltk.corpus.wordnet`, for **morphy lemmatisation only** (`thematic_role_labeler.lemma_word`) and for
  `animacy_lexicon.lookup_animacy`. No gloss, no synset-as-meaning.

No KB, no corpus, and no external database is read at grounding time.

Subsystem assignment of all 141 modules was machine-verified (`scratch/census_taxonomy.txt`):
141 assigned, 0 duplicates, 0 unassigned, 0 bogus names.

---

## S1. Live reading-to-grounding loop -- 21 modules

**What it is.** Reads curriculum text sentence by sentence, notices words it does not know, accumulates
context traces for them, and during a "sleep" pass promotes the well-evidenced ones into a fact store.

**Modules (lines).** `reading_grounding_loop` 1998, `grounding_acquisition_loop` 827, `goal_typing` 2689,
`coreference_resolver` 801, `verb_lexical_similarity` 767, `lexical_similarity` 756, `hd_fact_store` 587,
`thematic_role_labeler` 581, `frame_induction` 570, `state_of_mind` 499, `consequence_learning_loop` 474,
`gap_detector` 326, `situation_model_accumulate` 313, `grounded_similarity` 274, `event_bundle` 275,
`closed_class_lexicon` 229, `role_slot_summarizer` 420, `animacy_lexicon` 178, `self_improving_loop` 169,
`working_memory` 116, `memory` 76.

**Does it RUN?** Self-tests executed this pass, `.venv`, `python -m hdlab.<mod>`:
`reading_grounding_loop` **PASS** (16.8s, "ALL SELF-TESTS PASSED"), `grounding_acquisition_loop` **PASS**
(25.6s), `gap_detector` **PASS** (7.5s), `hd_fact_store` **PASS** (11.3s), `closed_class_lexicon` **PASS**
(49.3s), `goal_typing` **PASS** (19.1s), `consequence_learning_loop` **PASS** (19.2s), `frame_induction`
**PASS** (28.5s), `lexical_similarity` **PASS** (20.5s), `grounded_similarity` **PASS** (17.7s),
`event_bundle` **PASS** (10.0s). This is **code that works**, not a design note.

**Reachable from the LIVE path?** It *is* the live path (runtime evidence above).

**Registry.** `reading_grounding_loop_definitional_reading_pipeline`: `integration_status "WIRED"`,
`pipeline_status "WIRED_BUT_NOT_PIPELINE_REACHABLE"` -- i.e. **the pipeline entry point is recorded as not
pipeline-reachable**. `grounding_acquisition_loop`, `consequence_learning_loop`, `role_slot_summarizer`,
`memory`, `modulators`, `snapshots`, `tracing`, `atoms`, `ablation` have **no registry row at all**.

**Verdict history.** `gap_detector_familiarity_gate` `validated_hard_pass_signal_detection_2026-08-12`.
Arc-level position (`MEMORY.md` banner, `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`):
definitional extraction on real text HARD_PASS at 64% MEANINGFUL hand-scored; context-conditioned sense
selection HARD_FAILED; PBV HARD_FAILED.

**Data assets owned.** `data/foundation/` (75 MB, 10 store dirs). Independently recomputed this pass:
`reading_grounding_v1/store/store_facts.json` = **7,966 facts** (`KNOWN_WORD` 4,422 + `GROUNDED_MEANING`
3,544), of which **2,328 / 3,544 = 65.7 % are self-referential** `(X, GROUNDED_MEANING, X)`. This
reproduces the tautology figure in `notes/landed_vet_foundation_validation_2026-08-12.md` exactly.
`reading_grounding_v2_qualityfix` = 2,146 facts. `data/foundation_provenance_v1/store` = 8,187 facts
(same 3,544 GROUNDED_MEANING + 69 `ENABLING_CONDITION`, 49 `ENABLING_CONDITION_AGENT`, 48 `PROCESS_ACTION`,
39 `PROCESS_PATIENT`). `data/foundation_snapshots/` 2 snapshots.

---

## S2. Definitional extraction + foundation persistence -- 5 modules

**What it is.** A symbolic pattern extractor that pulls "X is a Y" style definitions out of real text and
writes them as facts, plus deterministic save/reload of the resulting foundation.

**Modules.** `definitional_extraction` 2025, `definitional_predicate_v61` 992, `foundation_persistence` 671,
`random_indexing` 391, `low_information_filter` 214.

**Does it RUN?** `definitional_extraction` **PASS** (23.6s), `definitional_predicate_v61` **PASS** (18.9s,
"v6.2 self-test PASS"), `foundation_persistence` **PASS** (24.4s), `low_information_filter` **PASS** (30.9s),
`random_indexing` **PASS** (5.1s). All five **work**.

**Reachable from the LIVE path? NO -- and this is a finding.** `definitional_extraction` produced the
current arc's headline facts, yet it is not in the live closure. `hd_fact_store.py:70` mentions it only as
a trust-source *string constant* (`"DEFINITIONAL_EXTRACTOR"`), and `grounding_acquisition_loop.py:195`
mentions `foundation_persistence` only in a *comment*. Neither is an import. The extractor is driven
entirely by cells: `exp_definitional_grounding_v3/v4/v5.py`, `exp_definitional_predicate_v6/v61/v62.py`,
`exp_called_boundary_v7.py`, plus `tools/measure_definitional_*.py`.

**Registry.** `definitional_extraction_surface_patterns` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`,
verdict `structural_pass_pending_b3_2026-08-12`, gate `VET_PENDING`.
`low_information_filter_pmi_flatness_gate` same statuses, same VET_PENDING.
`foundation_persistence_roundtrip` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`,
`validated_hard_pass_at_scale_2026-08-12`. `random_indexing_open_vocab_encoder` `WIRED` /
`WIRED_BUT_NOT_PIPELINE_REACHABLE`, `VET_PENDING`, revival: *"A cell that imports
hdlab.random_indexing.RandomIndexingEncoder directly and lands HARD_PASS off it (not an inline
reimplementation) would justify WIRE."* `definitional_predicate_v61` has **no registry row**.

**Data assets owned.** `data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl`
**1,751 rows**; `..._v4_parsefix/definitional_facts_v4.jsonl` **1,956 rows**;
`..._v5_termboundary/definitional_facts_v5.jsonl` **2,092 rows** (the "2092 facts, 0 genuine verb
definitions" set). All three are written by cells and read by nothing live.

---

## S3. Multi-source knowledge lookup (three-tier) -- 5 modules

**What it is.** When a concept is missing, gather candidate facts from knowledge graphs, reason over them,
and gate the good ones into either a permanent foundation or a retain-forever middle tier.

**Modules.** `prelim_tier` 495, `gap_driven_reader` 450, `gather_reason` 298, `kg_traversal` 228,
`three_tier_loop` 214.

**Does it RUN?** `prelim_tier` **PASS** (13.3s), `gather_reason` **PASS** (12.8s), `gap_driven_reader`
**PASS** (41.6s), `three_tier_loop` prints "assembly module, no standalone self-test payload" (**N/A by
design**; its witness is `verification/test_three_tier_loop_e2e.py`). `kg_traversal` has no `__main__`
but 61 consumers. **Code that works.**

**Reachable from the LIVE path? NO.** None of the five appear in the runtime closure.

**Registry.** `three_tier_loop`, `gather_reason`, `prelim_tier`, `gap_driven_reader_self_directed_order`
all `"WIRED"` / `"WIRED_BUT_NOT_PIPELINE_REACHABLE"`. `kg_ingest` (`kg_traversal`) `WIRED` /
`WIRED_BUT_NOT_PIPELINE_REACHABLE`; `kgstore_hierarchical_candidate_retrieval_1_2M` `WIRED` / `N_A`,
verdict `candidate_retrieval_real_final_selection_abandoned_2026-08-10`, gate `SHELVE`.

**Verdict history.** Landed HARD_PASS: `exp_three_tier_loop_real_corpus_gap_stream_v1`,
`exp_three_tier_loop_concept_coherence_v1`, `exp_three_tier_loop_independence_weighted_confirm_v1`,
`exp_gap_driven_reader_controlled_v1`, `exp_state_of_mind_relevance_gather_reasoning_union_v1`.
Landed HARD_FAIL: `exp_three_tier_loop_genuine_cross_source_corroboration_v1`
(`HARD_FAIL_thin_cross_source_not_mechanism_failure`) -- **revival criterion is explicitly SOURCE
THINNESS, not mechanism**: needs more independent databases. Full prior treatment in
`notes/multisource_lookup_wiring_audit_2026-08-13.md` (verified against disk this pass and found accurate).

**Data assets owned.** `data/cskg_foundation_v1/`: **1,213,912 edges** across 16 shards (counted this
pass), `nodes.jsonl` **482,588 rows**, `heldout_edges.jsonl` **24,774 rows**, 258 MB total.
Read by experiment cells only; no `hdlab/` module opens it.

---

## S4. Director KB (build-time multi-source index) -- 7 modules

**What it is.** A large searchable index over notes, preregs, and external ontologies that the *agent*
queries; it is not consulted by the substrate while reading.

**Modules.** `director_kb` 1151, `director_kb_bio_sources` 778, `director_kb_math_sources` 697,
`director_kb_chunk_ingest` 551 (docstring says DEPRECATED 2026-07-02), `director_kb_query` 521,
`char_trigram_encoder` 131, `kb_encoder_registry` 72.

**Does it RUN?** None has a `__main__` self-test. `tools/director_kb_query.py --help` **OK**;
`tools/director_kb_freshness_check.py` exists. `char_trigram_encoder` has 63 consumers.
The index is **live**: `data/substrate_director_kb_v1/manifest.json` shows last ingest 2026-08-13 09:45.

**Reachable from the LIVE path? NO.** Zero of the seven are in the runtime closure.

**Registry.** `director_kb_query` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`; `char_trigram_encoder`
and `kb_encoder_registry` same. `director_kb`, `director_kb_bio_sources`, `director_kb_math_sources`,
`director_kb_chunk_ingest` have **no registry row**.

**Data assets owned.** `data/substrate_director_kb_v1/` **12 GB**: 1,288,991 entities / 2,643,704 triples /
167,384 chunks / 113 relations / `n_dim` 2048; `E.pt` 10.6 GB, `atoms.jsonl` 1.15 GB. Sources per manifest:
wordnet, verbnet, framenet, gene_ontology, kegg_pathway, neurolex, concept_relations, capability_registry,
cert_ledger, director_plan, fleet_state, atoms.

---

## S5. Goal / desire narrative organs -- 11 modules

**What it is.** Decides who wanted what in a story, and whether they got it.

**Modules.** `goal_achievement` 2176, `goal_owner_select` 981, `goal_outcome_relation` 739,
`goal_outcome_relation_grounded` 530, `result_type_induction` 506,
`selection_weighted_sharded_typer` 470, `outcome_event_extraction` 370,
`context_grounded_valence` 370, `quality_relation` 364, `parse_goal_extraction` 314,
`idiom_grounding` 258.

**Does it RUN?** All PASS except one: **`goal_achievement` FAILS** its own `python -m` self-test
(rc=1, 22.5s) with `AssertionError: channel 'relation:recur' != 'majority' for 'I met up with my friend.'`.
That is the collateral predicted in `notes/false_certification_goal_typing_2026-08-13.md` sec. 5
(`lemma_verb("met")` now returns `meet`, so the recurrence channel fires); the verdict itself is
unchanged and correct, only the pinned channel label is stale -- **but the self-test is RED on `main`
today**. Passing: `goal_owner_select` (18.5s), `goal_outcome_relation` (18.6s),
`goal_outcome_relation_grounded` (19.9s), `quality_relation` (17.9s), `idiom_grounding` (13.2s),
`outcome_event_extraction` (19.3s), `context_grounded_valence` (68.2s), `result_type_induction`,
`selection_weighted_sharded_typer` (see table in S13).

**Reachable from the LIVE path? NO** -- none of the 11 is in the runtime closure. (`goal_typing`, which
IS in the closure, is counted under S1.)

**Registry / mismatch.** `goal_owner_select` carries `pipeline_status "WIRED_AND_PIPELINE_USED"` on two
rows (`goal_owner_select_component5_directed_score`, `goal_owner_full_selector_enumerate_argmax_tiebreak`)
but is **not** in the live runtime closure. All the rest are `WIRED` /
`WIRED_BUT_NOT_PIPELINE_REACHABLE`. `outcome_event_extraction` and `goal_outcome_relation_grounded` have
**no registry row**.

**Verdict history.** `direction_b_union_oov_recovery_channel` `validated_hard_pass_wired_2026-08-09`;
`goal_achievement_three_channel_...`, `quality_relation_two_channel_opposition`,
`parse_goal_extraction_...`, `idiom_grounding_lexicon`, `result_type_induction_...`,
`utility_channel_grounded_architecture` all `promoted_wire_dont_island` 2026-08-08/09.
`selection_weighted_sharded_typer` `validated_hard_pass_scaling_n_train_40_5seeds`.
**Correction to today's `false_certification_goal_typing_2026-08-13.md`:** its central claim (that
`verify_goal_typing.py` is now 16/18 and the 18/18 certification was an artifact) is **superseded**.
Commit `eac20c620` "goal typing: structural dual-consumption fix + correction of a false certification"
is an ancestor of HEAD; measured this pass, `lemma_verb("missed") == "miss"` and
`frame_primary_role("miss", "subj") == EXPERIENCER` (i.e. the corrupting bug is genuinely gone), and
`verification/verify_goal_typing.py` **PASSES in 37.2s with its hard `assert acc == 1.0` intact**
(line 98, not relaxed to a floor). The note is correct about the history and wrong about the present.

---

## S6. Coreference / situation model (secondary track) -- 10 modules

**What it is.** Tracking which later mentions refer to which earlier entity, and holding a running model
of the described situation.

**Modules.** `situation_reader` 1082, `event_centrality_coref` 475, `coref_distractor_suppress` 432,
`scene_segment` 391, `bundle_focus_coref` 386, `coref` 681, `slot_attention_wm` 284, `situation_focus` 197,
`situation_model_multibank` 148, `entity_slot_gate` 159.

**Does it RUN?** `bundle_focus_coref` **PASS** (11.2s), `coref_distractor_suppress` **PASS** (7.5s),
`event_centrality_coref` **PASS** (10.5s), `situation_focus` / `situation_reader` / `slot_attention_wm`
see S13. **`situation_reader` costs 217.6 s merely to IMPORT** (measured) -- by far the heaviest module in
the repo and the reason two of this census's sweeps appeared to hang.

**Reachable from the LIVE path? NO** (S1's `situation_model_accumulate`, `state_of_mind`,
`coreference_resolver` are the live coref organs; this cluster is the parallel track).

**Registry.** `working_overlay_situation_reader` (`situation_focus`, `bundle_focus_coref`, `coref`,
`event_bundle`) `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`, gate **SHELVE**, revival: *"revive when a
narrative/multi-sentence reading pipeline is built, OR the self-learning-loop's STRUCTURED_EXTRACT arm."*
`slot_attention_wm_stateful_core` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`, gate SHELVE.
`entity_slot_gate_cross_boundary_v1` `TRAPPED_SHARED` / `N_A`, `landed_hard_fail_2026-07-28`.
`scene_segment`, `coref_distractor_suppress`, `event_centrality_coref`, `situation_model_multibank` have
**no registry row**.

---

## S7. Word / script acquisition loops -- 6 modules

**What it is.** Learning a new word's meaning from what happens after it in a story, optionally seeded by
a dictionary lookup; and the same idea at the level of multi-step scripts.

**Modules.** `script_grain_acquisition_loop` 515, `word_acquisition_loop` 466,
`wordnet_polarity_propagation` 310, `mcscript_extraction` 292, `dg_pattern_separation` 205,
`word_learning_tool` 113.

**Does it RUN?** `dg_pattern_separation` **PASS** (5.2s), `mcscript_extraction` **PASS** (31.9s); the
rest in S13. `wordnet_polarity_propagation.dictionary_lookup` is the only **live** dictionary call in the
repo (`nltk.corpus.wordnet`), and it returns a **polarity for an outcome verb, not a definition**.

**Reachable from the LIVE path? NO.** `word_learning_tool` has exactly **1** consumer repo-wide.

**Registry.** `grounded_word_acquisition_loop_increment1` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`,
verdict `built_measured_HARD_FAIL_shelved_2026-08-06`, gate **SHELVE**, with a two-condition numeric
revival criterion. `word_learning_tool`, `wordnet_polarity_propagation`, `script_grain_acquisition_loop`,
`mcscript_extraction`, `dg_pattern_separation` have **no registry row**.

**Verdict history.** `exp_combined_dictionary_consequence_word_learning_tool_v1` **HARD_FAIL**
(combined 0.1944 vs floor 0.6389; dictionary coverage 6/33 lemmas).

---

## S8. Encoders -- 10 modules

**Modules.** `concept_encoder` 1260, `composed_encoder_v3` 550, `vwfa` 390, `ppmi_sparse_encoder` 369,
`char_positional_encoder` 258, `gsbc_graded_encoder` 139, `late_combine` 343, `whitening` 133,
`token_vocab` 301, `encoder_retrain_persist` 113.

**Does it RUN?** `composed_encoder_v3` **PASS** (10.0s, 13 self-tests), `char_positional_encoder` **PASS**
(12.8s), `ppmi_sparse_encoder` **PASS** (5.4s), `late_combine` **PASS** (13.4s), `encoder_retrain_persist`
**PASS** (15.1s), `vwfa` see S13. **`concept_encoder` TIMED OUT at 180 s** -- the only module whose
self-test neither passed nor failed within the budget; its runtime cost is unmeasured, not zero.
`whitening`, `token_vocab`, `gsbc_graded_encoder` have no `__main__`.

**Reachable from the LIVE path? NO** -- for any of the ten.

**Registry / mismatch.** `composition` row lists `hdlab/concept_encoder.py` with
`pipeline_status "WIRED_AND_PIPELINE_USED"`, but `concept_encoder` is **not** in the live closure.
`hdlab_encoder_cluster_vwfa_ppmi_composed_v3` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`, verdict
`superseded_untouched_since_2026-07-03`, gate **SHELVE**, revival "only if the N400/late-combine mechanism
is needed by the frontier encoder". `encoder_retrain_persist_generalizing_lever_reusable_v1` `WIRED` /
`WIRED_BUT_NOT_PIPELINE_REACHABLE`, `vet_confirmed_chain_grade_generalizing_lever_2026-07-31`.

---

## S9. VSA/HDC core primitives, memory and reasoning -- 44 modules

**What it is.** The algebra the whole substrate is built on (bind, bundle, cleanup) plus a large library
of stand-alone brain-analog primitives promoted out of individual experiments.

**Modules (44).** `atoms` 68, `binding` 112, `bundling` 50, `cleanup_family` 393, `iterative_attractor` 234,
`modern_hopfield_readout` 383, `sequence_memory` 178, `multi_hop` 361, `predictive_coding` 325,
`lock_in_amp` 214, `int8_dense` 75, `k_cliff_scaling` 58, `additive_map` 307, `edge_importance` 306,
`excitability` 192, `ultrametric_clustering` 306, `compose_freq_routing` 307, `gated_fusion` 162,
`noise_channel` 356, `hippocampal_encoder` 846, `temporal_trace` 374, `cortex` 763, `continual` 209,
`schema_exemplar_bayes` 162, `generation` 138, `refuse_gate` 130, `layer_075_structural_slot_filter` 132,
`clarify_gate` 285, `context_retention` 630, `semantic_parser` 698, `intent_classifier` 114,
`action_selection` 607, `self_manager` 252, `atom_consultation` 978, `glass_box_loop` 349, `reasoner` 923,
`typed_rule_parser` 148, `conformal` 221, `bayesian_inference` 318, `perceptron` 253, `learning` 88,
`modulators` 93, `ablation` 90, `semantic` 121.

**Does it RUN?** Every one with a self-test that has completed so far **PASSED**: `cleanup_family`,
`iterative_attractor`, `modern_hopfield_readout`, `predictive_coding`, `lock_in_amp`, `edge_importance`,
`excitability`, `compose_freq_routing`, `gated_fusion`, `noise_channel`, `hippocampal_encoder` (14/14),
`cortex` (6 primitives composed), `clarify_gate`, `context_retention`, `atom_consultation`,
`glass_box_loop`, `conformal`, `bayesian_inference`, `perceptron`, `action_selection` (58.9s).

**Reachable from the LIVE path?** Only 8 of 44: `atoms, binding, bundling, cleanup_family,
iterative_attractor, modulators, ablation, semantic`. The other 36 are not.

**Registry.** Mostly `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE` with `triaged_2026-07-28` verdicts
(`readout`, `pattern_completion`, `cleanup_attractor`, `predictive_coding`, `sequence_binding`,
`intent_classification`, `schema_abstraction`, `hierarchical_structure`, `cortex_eTensor`, `generation`,
`catastrophic_forgetting`, `kg_ingest`, `cert_audit`). Explicitly SHELVED with revival criteria:
`capacity_scaling` (`k_cliff_scaling`, ISLAND) -- *"Revive when a SEQUENCE-BINDING capacity/phase-diagram
cell needs analytic sizing. Do NOT use it to size the situation-model register..."*;
`lock_in_amplifier` -- *"substrate hits a genuinely noisy-channel decode problem"*;
`excitability_tensor_promoted_zero_consumer` and `profiling_op_latency_zero_consumer` (ISLAND, zero
consumer); `self_manager_neuromodulatory_zero_consumer`; `compose_freq_routing_promoted_zero_consumer`.
`reasoner_composed_entry_arc_program` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`, verdict
`built_2026-07-25_then_abandoned_2026-07-27`, gate **SHELVE** -- a **disclosed dead end**; do not reuse
silently. Unregistered in this group: `atoms, ablation, modulators, learning, memory, multi_hop,
noise_channel, clarify_gate, context_retention, semantic_parser, atom_consultation, glass_box_loop,
bayesian_inference, perceptron, additive_map, int8_dense, temporal_trace, late_combine,
layer_075_structural_slot_filter, gsbc_graded_encoder, refuse_gate, dg_pattern_separation`.

---

## S10. Glass-box parser front-end -- 5 modules

**What it is.** The project's own POS tagger and dependency parser, trained in-repo, with no spaCy/NLTK
parser dependency.

**Modules.** `arc_labeler` 258, `arc_parser` 243, `candidate_generator` 153, `pos_tagger` 110,
`completeness_checker` 262.

**Does it RUN?** `arc_labeler` **PASS** (10.2s, "subject/object separated + persistence round-trips").
`pos_tagger`, `arc_parser`, `candidate_generator`, `completeness_checker` have no `__main__`, but
`pos_tagger` has 38 consumers and `arc_parser` 37.

**Reachable from the LIVE path? YES, LAZILY** -- `pos_tagger`, `arc_parser`, `arc_labeler` are imported
inside `StructuralFrontEnd._load` (`reading_grounding_loop.py:300-303`). An eager import trace misses
them; a grep-only audit would too. `candidate_generator` (40 consumers) and `completeness_checker` are NOT
on the live path.

**Registry.** All five: **no registry row**, except `completeness_checker` via the `cert_audit` row
(`WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`). The three assets they load are the only model files the
live path reads.

---

## S11. Infrastructure and measurement -- 16 modules

**Modules.** `experiment` 159, `store` 100, `harness` 120, `metrics` 94, `profiling` 59, `per_item_log` 243,
`session_log` 45, `tracing` 170, `snapshots` 52, `lm_eval_harness` 248, `bigram_gap_measurement` 214,
`reachability_audit` 249, `gpu_memory_budget` 233, `gpu_generated_streaming_attention` 501,
`streaming_attention` 259, `chunked_attention` 218.

**Does it RUN?** `harness` **PASS** (31.8s), `per_item_log` **PASS** (5.1s). `store` requires `duckdb`
(present only in `.venv`). `session_log` is the single most-imported module in the repo (**240**
consumers, 236 of them experiment cells).

**Reachable from the LIVE path?** Only `tracing` and `snapshots`.

**Registry.** `shared_harness_seed_checkpoint` `TRAPPED_SHARED` / `N_A`,
`de_facto_shared_infra_copy_pasted`. `profiling_op_latency_zero_consumer` `ISLAND` / `N_A`, SHELVE,
revival *"when Week-8-class hardware analysis actually begins"*. `cert_audit` covers `reachability_audit`.
The rest unregistered.

---

## S12. Dead / stale -- 1 module

`_scratch_orig_goal_owner_select` 889 lines. Self-test **PASSES** (39.9s) -- it is a live copy of a
superseded organ. Zero consumers. Registry `scratch_orig_goal_owner_select_stale_backup` `ISLAND` / `N_A`,
verdict `registered_2026-08-12_skunkworks_audit_DEAD_superseded`, revival: *"None, superseded.
Delete-candidate, not revival-candidate."*

---

## S13. FULL SELF-TEST SWEEP RESULT

All 81 modules carrying `if __name__ == "__main__"`, run as `.venv/Scripts/python.exe -m hdlab.<mod>`,
180 s timeout each. Raw log: `scratch/census_selftests_venv.txt`.

**Result: 78 PASS / 1 FAIL / 2 TIMEOUT (of 81).**

| module | status | detail |
|---|---|---|
| `goal_achievement` | **FAIL** rc=1, 22.5s | `AssertionError: channel 'relation:recur' != 'majority' for 'I met up with my friend.'` -- stale pinned channel label, consequence of `lemma_verb("met")` now correctly returning `meet`. Verdict itself (`Fulfilled`) is unchanged and correct. |
| `concept_encoder` | **TIMEOUT** at 180s | competitive-Hebbian training self-test; outcome unknown |
| `reasoner` | **TIMEOUT** at 180s | the disclosed dead-end derivation reasoner; outcome unknown |

The other 78 all printed a PASS line. Notable runtimes: `situation_reader` 179.2s (it costs 217.6s just
to `import`, measured separately), `context_grounded_valence` 68.2s, `action_selection` 58.9s,
`closed_class_lexicon` 49.3s, `gap_driven_reader` 41.6s.

The 60 modules WITHOUT a `__main__` self-test are not "broken" -- most are libraries with heavy consumer
counts (`session_log` 240, `perceptron` 151, `bayesian_inference` 150, `kg_traversal` 61, `pos_tagger` 38).
All 141 import cleanly.

---

## S14. VERIFICATION AND CERTIFICATION

**`verification/` contains 72 scripts.** `pyproject.toml:59` sets `python_files = ["test_*.py"]`, so
`pytest verification/` (which is exactly what `verification/run_certification.py:21-25` runs) collects
only the **45** `test_*.py` files. The **25 `verify_*.py` + 2 `witness_*.py` = 27** scripts are NOT
collected by the certification command. A concurrent agent found the same thing today
(`notes/uncollected_witness_audit_2026-08-13.md`) and landed
`verification/test_all_witnesses_exit_clean.py` (commit `c6279d2eb`), a `test_`-named driver that runs
each witness as a subprocess so `__main__` actually executes.

**`pytest verification/` under `.venv` (the certification command), run this pass:
`2 failed, 296 passed, 3 skipped in 1273.72s (21m13s)`, exit 1.** Both failures are
`verification/test_goal_achievement.py::test_mechanism_fires` and `::test_self_test_passes`, same single
root cause as the `goal_achievement` self-test failure above (`hdlab/goal_achievement.py:421`, pinned
channel `'majority'` vs actual `'relation:recur'`). **Certification is RED on `main` today, with exactly
2 failures, both cosmetic-pin, not mechanism.**

**I independently ran all 27 uncollected witnesses as subprocesses** (`scratch/census_witnesses.txt`,
300s budget each): **26 PASS, 1 TIMEOUT**. The single timeout,
`verify_integration_health_import_graph.py`, is a *budget* artifact, not a failure -- the in-repo driver's
own persisted record (`data/witness_exit_status/verify_integration_health_import_graph.json`, run_utc
2026-08-13T16:12:34Z) shows `returncode 0, passed true, secs 341.56, timeout_s 600`. **Effectively 27/27
witnesses PASS at HEAD.**

**This corrects `notes/uncollected_witness_audit_2026-08-13.md`, which reports "18 PASS / 9 FAIL".** That
measurement predates commits `eac20c620` (goal-typing structural dual-consumption fix) and `1421c21db`
("witness pins + certification honesty: stale pins converted to floors"), both ancestors of HEAD. Three
of its named failures were re-run by me and pass: `verify_goal_typing.py` (37.2s, with its hard
`assert acc == 1.0` at line 98 **intact**, not relaxed), `verify_grounded_result_class_tier.py` (43.9s),
`verify_grounded_word_acquisition_increment1b.py` (22.7s, message reads "primary=18/36 (floor 18; 16/36 at
this build)" -- visible evidence of the pin-to-floor conversion). All 27 persisted status files currently
record `passed: true`.

Consequence: the driver's docstring assertion that it "is EXPECTED to be RED (9 failures) on main as of
2026-08-13" is now stale; `test_all_witnesses_exit_clean.py` is among the 296 passing tests.

**Root `tests/` (5 files):** `.venv` pytest -> **2 failed, 104 passed in 379.5s**. Both failures are
`tests/test_runner_n_suffix_validator.py::test_prot019_passes_large_n_with_sufficient_timeout` and
`::test_prot019_passes_at_exactly_the_floor` (queue-dispatch PROT-019 timeout-tier validator, not a
substrate capability).

---

## S15. `tools/` -- 1,016 `.py` files, subsystem view

Overwhelmingly **historical one-off scripts, not durable tooling**. By first token:
`substrate_*` 273 (atom authoring / ratification / ingest batches, mostly dated 2026-06),
`gen_*` 163 (queue generators), `_`-prefixed scratch 150, `skunkworks_*` 145, `atomize_*` 85,
`capint_*` 15, `build_*` 14, `derive_*` 12, `cert_*` 8. Plus 11 subdirs
(`benchmark_trap_check/`, `orchestrator/`, `dashboard/`, `cloud/`, `remote_launchers/`,
`spawn_templates/`, `testbed/`, `tests/`, `hp12/`, `_local/`).

**Durable operational tools, `--help` smoke-checked this pass under `.venv`:**
`session_start_hook` OK, `capability_registry_query` OK, `director_kb_query` OK, `inflight_monitor` OK,
`exp_checkpoint` OK, `clear_scratch` OK, `verdict_lint` OK, `runner_status` OK, `queue_status` OK.
**`integration_health` did NOT return within 60 s** (`rc=124`) -- it performs a full-repo import-graph
scan on startup; that is cost, not breakage (its witness `verify_import_graph_scans_all_source_dirs.py`
passes in 206 s).

Registry rows pointing into `tools/`: `inflight_monitor` `WIRED` / `WIRED_BUT_NOT_PIPELINE_REACHABLE`;
`propara_official_eval_port` (`tools/benchmark_trap_check/propara_official_eval.py`) `ISLAND` / `N_A`,
gate WIRE, verdict *"VALIDATED reusable tool. Bit-exact vs official fixtures... it is a scorer."*

---

## S16. `experiments/` -- capability lines and landed verdicts

5,745 cells; 7,551 result directories carry a `metrics.json`. Verdict tally over **all** of them
(field `verdict`/`verdict_msg`/`status`, else regex over the JSON body):

| bucket | count |
|---|---|
| HARD_PASS | 2,683 |
| HARD_FAIL | 1,345 |
| MIDDLE_BAND | 1,235 |
| KILLED | 52 |
| generic FAIL | 49 |
| generic PASS | 19 |
| SATURATION | 7 |
| other verdict string | 1,971 |
| no verdict field | 190 |

Name-prefix clustering yields 4,181 families, which is too granular to be a capability list. **The
curated capability-line list is the registry itself (123 rows)**, whose verdicts and revival criteria are
quoted per subsystem above and dumped in full to
`C:\Users\marsh\.claude\projects\D--AI\...\tool-results\bijkpmvv9.txt` this pass. Distinct capability
lines with landed verdicts, grouped: three-tier multi-source lookup (5 HARD_PASS, 1 HARD_FAIL);
definitional reading/grounding (structural pass, VET_PENDING, hand-scored 64%); goal/desire narrative
(HARD_PASS, wired 2026-08-09); crutch-fade (HARD_FAIL x3, SHELVE); MAVEN-ERE convergence-gated relation
classification (CHAIN-GRADE, WIRE, 14.78 / 31.96 SOTA); ProPara bridging (NO-GO, revive only after the
reading/trigger-localization extraction wall); MCScript2 real-benchmark (HARD_FAIL extraction wall);
native VSA binding family (bounded, SHELVE); encoder retrain/entity-reid (CHAIN-GRADE, WIRE_CANDIDATE).

---

## S17. DATA ASSETS

| asset | path | size | rows / contents | LIVE reader? |
|---|---|---|---|---|
| Front-end parser assets | `data/frontend_assets/` | 28 MB | 5 files; 3 loaded | **YES** (only live model load) |
| Closed-class lexicon | `data/closed_class_lexicon_v1.json` | small | function words | **YES** |
| Reading-grounding foundation | `data/foundation/` | 75 MB | v1 store 7,966 facts (3,544 GROUNDED_MEANING, 65.7% tautological); v3 1,751 / v4 1,956 / v5 2,092 definitional facts | written by loop+cells; not re-read live |
| Foundation provenance | `data/foundation_provenance_v1/` | ~17 MB | 8,187 facts incl. 205 process/enabling relations | cells |
| Foundation snapshots | `data/foundation_snapshots/` | -- | 2 snapshots | no |
| CSKG foundation v1 | `data/cskg_foundation_v1/` | 258 MB | **1,213,912 edges**, 482,588 nodes, 24,774 heldout | cells only |
| Director KB index | `data/substrate_director_kb_v1/` | **12 GB** | 1,288,991 entities / 2,643,704 triples / 167,384 chunks; ingested 2026-08-13 09:45 | agent tool only |
| Canonical atom store | `data/substrate_index/` | 7.6 GB | concept 335,180 / math 75,024 / science 12,623 / meta 2,991 / school 128 / external 111 rows; history dirs 6,996 rows | `backend/substrate_index/partition.py` |
| Substrate capability registry (legacy) | `data/substrate_capability_registry.jsonl` | 6.1 MB | **7,515 rows** (distinct from the 123-row gate registry) | tools |
| ConceptNet 5.7 | `data/conceptnet/` | 492 MB | assertions gz + 20,219 heldout edges | one-shot ingester |
| ATOMIC v4 | `data/atomic_kb/` | 58 MB | `v4_atomic_all_agg.csv` | folded into CSKG at build |
| Corpora | `data/corpora/` | **6.1 GB**, 33 subdirs | see below | curriculum for cells |
| OpenStax textbooks | `data/corpora/textbook_*` | 522 MB | **117,642 cleaned sentences** total (anatomy 22,542 / biology 27,219 / chemistry 15,887 / microbiology 23,605 / psychology 28,389), definitional-pattern density 30.8-105.8 per 1,000 | **NOT yet ingested** |
| McGuffey graded | `data/corpora/mcguffey_graded/` | 9 MB | 6 graded readers g1-g6 | cells |
| SimpleWiki | `data/corpora/simplewiki/` | 577 MB | cleaned 251 MB txt | cells |
| OneStop / ARC / RACE / MCScript2 / SocialIQa / WIQA / LitBank / UD-EWT | `data/corpora/*` | 1.6 GB / 2.1 GB / 9 MB / 16 MB / 24 MB / 52 MB / 13 MB / 18 MB | benchmark corpora | cells |
| Datasets | `data/datasets/` | 79 MB | conceptnet5_en_100k, fb15k_237_train_50k, hotpot_qa_1k, medqa_500, nq_open_1k, pubmed_10k, wikipedia_smoke_500 | cells |
| Lexicons | `data/lexicons/`, `data/verbnet_affectedness_lexicon_v1_corrected/`, `data/wordnet_noun_semantics_kb_v{1,2}/` | 2.5 MB | gazetteer, verbnet affectedness, wordnet noun KB | cells |
| Grown breadth foundations | `data/breadth_foundation_grown{_v1,_mcguffey_v1}/` | 12 MB | foundation.json + escalation queues | cells |

**Summary: only ~28 MB of the ~26 GB of data assets is read by the live path.**

---

## S18. THE THREE QUESTIONS

### Q1. What else WORKS and is NOT wired?

Criterion: `python -m hdlab.<mod>` self-test **PASSES**, module is **absent from the live runtime
closure**, and the registry records `integration_status: "WIRED"`. **33 modules qualify.** The
three-tier lookup stack is one case among many; here is the rest.

| module | registry row | landed verdict |
|---|---|---|
| `definitional_extraction` | `definitional_extraction_surface_patterns` | `structural_pass_pending_b3_2026-08-12` (VET_PENDING) -- **produced the current arc's 2,092 facts and the 64% hand-score, and is not on the live path** |
| `low_information_filter` | `low_information_filter_pmi_flatness_gate` | `structural_pass_pending_b3_2026-08-12` |
| `foundation_persistence` | `foundation_persistence_roundtrip` | `validated_hard_pass_at_scale_2026-08-12` |
| `random_indexing` | `random_indexing_open_vocab_encoder` | VET_PENDING; revival = a cell that imports it directly and lands HARD_PASS |
| `three_tier_loop` / `gather_reason` / `prelim_tier` | own rows | 5 landed HARD_PASS cells; 1 HARD_FAIL whose revival criterion is **source thinness, not mechanism** |
| `gap_driven_reader` | `gap_driven_reader_self_directed_order` | `validated_hard_pass_full_2026-08-12`; row text itself says "NOT YET imported by hdlab/reading_grounding_loop.py" |
| `goal_owner_select` | `goal_owner_select_component5_directed_score` | promoted 2026-08-05; **row claims `WIRED_AND_PIPELINE_USED` yet it is not in the closure** |
| `quality_relation`, `goal_outcome_relation`, `idiom_grounding`, `result_type_induction` | 4 rows | all `promoted_wire_dont_island` 2026-08-08/09, all HARD_PASS-backed via `direction_b_union_oov_recovery_channel` |
| `context_grounded_valence` | `context_grounded_valence` | `promoted_wire_don't_island_2026-08-05` |
| `selection_weighted_sharded_typer` | own row | `validated_hard_pass_scaling_n_train_40_5seeds` |
| `action_selection` | `action_selection_basal_ganglia_gonogo` | `validated_hard_pass_trapped_shared_2026-08-05`; SHELVE with a named revival (re-point as Go/NoGo when the grounded appraisal->action layer is built) |
| `encoder_retrain_persist` | `..._generalizing_lever_reusable_v1` | `vet_confirmed_chain_grade_generalizing_lever_2026-07-31` |
| `hippocampal_encoder` | `hippocampal_encoder_dg_ca3_pipeline` | `registered_2026-08-10_disk_shows_real_consumers_not_island` |
| `situation_reader`, `situation_focus`, `bundle_focus_coref` | `working_overlay_situation_reader`, `frame_primary_role_assigner_v1` | validated 2026-08-03; gate SHELVE, revival = "when a narrative/multi-sentence reading pipeline is built" |
| `typed_rule_parser` | `typed_rule_parser` | `promoted_2026-07-25` |
| `word_acquisition_loop` | `grounded_word_acquisition_loop_increment1` | `built_measured_HARD_FAIL_shelved_2026-08-06` (works, but the capability FAILED) |
| `cortex`, `edge_importance`, `predictive_coding`, `ultrametric_clustering`, `lock_in_amp`, `compose_freq_routing`, `self_manager`, `composed_encoder_v3`, `ppmi_sparse_encoder`, `vwfa` | various | `triaged_2026-07-28` / SHELVE with revival criteria |

**Plus 24 modules that self-test PASS, are not live-reachable, and have NO registry row at all** -- i.e.
invisible to every registry-based audit: `atom_consultation, bayesian_inference, char_positional_encoder,
clarify_gate, conformal, context_retention, coref_distractor_suppress, definitional_predicate_v61,
dg_pattern_separation, event_centrality_coref, glass_box_loop, goal_outcome_relation_grounded,
late_combine, mcscript_extraction, modern_hopfield_readout, noise_channel, outcome_event_extraction,
per_item_log, perceptron, script_grain_acquisition_loop, semantic_parser, temporal_trace,
word_learning_tool, wordnet_polarity_propagation`.

Two of those deserve naming: **`wordnet_polarity_propagation` is the only live dictionary lookup in the
repo** (`nltk.corpus.wordnet`, `dictionary_lookup`), and `word_learning_tool` is its orchestration glue.
Both pass their self-tests; `word_learning_tool` has **1** consumer repo-wide; neither has a registry row;
their one landed evaluation (`exp_combined_dictionary_consequence_word_learning_tool_v1`) **HARD_FAILED**.

### Q2. What is registered WIRED but is NOT pipeline-reachable?

**47 registry rows** carry `integration_status: "WIRED"` while none of their `hdlab/` modules appear in
the live runtime closure (full list in `scratch/census_q2.txt`; every row's `pipeline_status` is
`"WIRED_BUT_NOT_PIPELINE_REACHABLE"` except four: `grounded_appraisal_sim_earned` `N_A`,
`kgstore_hierarchical_candidate_retrieval_1_2M` `N_A`, `thematic_role_labeler_cue_integration` `N_A`,
`bridge1_twostage_event_situation` `N_A`).

**More important: `pipeline_status` is unreliable in BOTH directions.** Measured against the live path:

- **(A) Claims used, measurably not used -- 3 (row, module) pairs:**
  `composition` / `concept_encoder`; `goal_owner_select_component5_directed_score` / `goal_owner_select`;
  `goal_owner_full_selector_enumerate_argmax_tiebreak` / `goal_owner_select`. All say
  `"WIRED_AND_PIPELINE_USED"`; none of those modules is in the closure.
- **(B) Claims unreachable, measurably reachable -- 19 (row, module) pairs**, including
  **`reading_grounding_loop_definitional_reading_pipeline` / `reading_grounding_loop`** -- the pipeline
  entry point itself is filed as not-pipeline-reachable. Also `hd_fact_store`, `gap_detector`,
  `closed_class_lexicon`, `goal_typing`, `lexical_similarity`, `grounded_similarity`, `animacy_lexicon`,
  `frame_induction`, `thematic_role_labeler`, `verb_lexical_similarity`, `cleanup_family`,
  `iterative_attractor`, `event_bundle`.
- **(C) In the closure with no registry row at all -- 13 modules:** `ablation, arc_labeler, arc_parser,
  atoms, consequence_learning_loop, grounding_acquisition_loop, learner, memory, modulators, pos_tagger,
  role_slot_summarizer, snapshots, tracing`. **`grounding_acquisition_loop` is one of the two live entry
  points and is entirely unregistered.**

So of the 11 rows marked `WIRED_AND_PIPELINE_USED`, 3 pairs are wrong; and 62 of 141 modules are outside
the registry altogether. A compliance audit against this field cannot see the live path.

### Q3. What exists as code that has NEVER successfully run?

Distinct from unwired. Measured, not inferred:

- **Zero modules fail to import.** All 141 import cleanly under `.venv` (0 failures). Under system
  Python, 8 modules transitively needing `duckdb` appear broken -- an interpreter artifact.
- **2 modules have neither a self-test nor a single consumer anywhere in the repo** -- nothing has ever
  demonstrably executed their bodies: **`hdlab/k_cliff_scaling.py`** (58 lines; registry `capacity_scaling`
  `ISLAND`/`N_A`, SHELVE, revival "when a SEQUENCE-BINDING capacity/phase-diagram cell needs analytic
  sizing", with an explicit warning not to use it to size the situation-model register) and
  **`hdlab/profiling.py`** (59 lines; registry `profiling_op_latency_zero_consumer` `ISLAND`/`N_A`,
  SHELVE, revival "when Week-8-class hardware analysis actually begins").
- **2 modules whose self-test never completed** and whose working state is therefore unknown:
  **`concept_encoder`** (1,260 lines) and **`reasoner`** (923 lines, itself a disclosed dead end,
  `built_2026-07-25_then_abandoned_2026-07-27`, gate SHELVE). Both TIMEOUT at 180s.
- **1 module whose self-test FAILS on `main`:** `goal_achievement` (2,176 lines) -- but it *has* run
  successfully in the past; this is a stale test pin, not dead code.
- **3 modules with a passing self-test but zero consumers anywhere:** `_scratch_orig_goal_owner_select`
  (889 lines, registry-declared DEAD delete-candidate), `excitability`, `harness`.
- **5 modules with neither self-test nor more than one consumer:** `ablation`, `kb_encoder_registry`,
  `metrics`, `snapshots`, `whitening`.

Everything else in `hdlab/` has either executed a self-test successfully this pass or has real consumers.
**Dead weight is small (~2-7 modules); the large number is unwired-but-working (33+24), not dead.**

### Correction to a third prior claim

`notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md` gap **G5** states the MDL
conjunctive gate "was never actually invoked (`mdl_gate_fn=None` at both call sites)". At HEAD that is
stale in a specific way: `hdlab/reading_grounding_loop.py:1278` **does** pass `mdl_gate_fn=gate`, but the
`gate` is `_make_grounding_gate` / `_make_pbv_grounding_gate` (the refusal gate), **not** the
`hdlab/learner` MDL gate. The hook is occupied; the learner MDL gate itself is exercised only by cells
(`exp_learner_mdl_gate_on_acquisition_traces_v1.py`,
`exp_crutch_fade_social_iqa_v2_semantic_cluster_key.py`, `exp_script_grain_acquisition_loop_v1.py`).

---

## S19. WHAT I COULD NOT VERIFY

1. **`hdlab/concept_encoder.py`'s and `hdlab/reasoner.py`'s self-test outcomes.** Both TIMED OUT at 180 s.
   I do not know whether they pass given more time. Neither is PASS nor FAIL in this census.
   Likewise `verify_integration_health_import_graph.py` exceeded my own 300 s budget; I did NOT re-run it
   myself at 600 s, I read the in-repo driver's persisted record showing it passes at 341.6 s.
2. **Whether any unwired-but-working subsystem would help the live path if wired.** Nothing tests those
   pairings; no cell imports both the reading loop and the three-tier loop. Stating a benefit in either
   direction would be speculation.
3. **The meaning of "pipeline" in the registry's `pipeline_status`.** I measured against the brief's
   definition of the live path (the two loops). If the field was written against a different pipeline,
   the mismatches in Q2 below are definitional rather than errors. The field's own rows argue for my
   reading (`gap_driven_reader_...gate_decision_target` says "NOT YET imported by
   hdlab/reading_grounding_loop.py itself"), but I did not find a written definition of the term.
4. **Per-arm recomputation of any landed experiment verdict.** I read `metrics.json` verdict strings;
   I re-ran no FULL cell (a detached run, PID 9260, is live).
5. **ConceptNet / Wikidata exact row counts.** The 498 MB gz and the Wikidata dumps were not decompressed.
   CSKG, foundation stores, substrate_index partitions and the textbook corpora WERE counted line by line.
6. **`tools/` beyond a `--help` smoke on 10 durable entry points.** 1,016 files were categorised by name,
   not executed. `tools/integration_health.py` in particular did not finish inside 60 s and its behaviour
   past startup is unmeasured.
7. **`backend/` (70 `.py`), `hdlab_service/` (17), `substrate/` (20), `substrate_router/` (6), `mvp/` (0).**
   Counted, not exercised; only `backend/substrate_index/partition.py` appears in the registry.
8. **Git history of the wiring.** I did not check whether any module was wired and later unwired, except
   for the `goal_typing` fix commit which I confirmed is an ancestor of HEAD.
9. **`Glob` was not used at all** (standing false-negative warning). All discovery used `Grep`, `ls`+`grep`
   on directory listings, `os.walk`, and live Python import traces. No permission denial occurred at any
   point in this census.
