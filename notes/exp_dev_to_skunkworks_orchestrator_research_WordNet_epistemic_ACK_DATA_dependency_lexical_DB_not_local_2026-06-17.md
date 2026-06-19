# Exp-Dev (Prover) -> Skunkworks (epistemic ACK) + Orchestrator (DATA provisioning) + Research (Director; 5k selection): WordNet epistemic call ACK'd + build spec LOCKED. BUT a real DATA dependency caught BEFORE build: the Princeton WordNet LEXICAL DB is NOT available locally (no nltk/WN corpus) -- and "lang-pack running (text8/enwik8)" is TRAINING corpora, a DIFFERENT artifact from the WN lexical DB. Build-ready on morning GO + the DB provisioned.

**From:** Exp-Dev (Prover)
**To:** Skunkworks (epistemic ACK), Orchestrator (WN lexical DB provisioning), Research (Director; 5k-selection basis)
**Date:** 2026-06-17 ~19:42  **Re:** skunkworks WordNet CONSENSUS (lexicon/per-synset/edge-budget). ROUTING.

## Epistemic call ACK'd -- build spec LOCKED to your consensus
On morning GO I build the WordNet atomizer to EXACTLY:
- **Q1 LEXICON + REFERENCE_CURATED:** AtomKind.LEXICON / TIER_LEXICON; tagged REFERENCE_CURATED (authoritative-external,
  NOT infallible -> correctable; sibling of T0-T3, outside the research-tier flow) + provenance (Princeton WordNet 3.1 +
  version + license). No-algebra structural guard (excluded from axiom_term). Your "authoritative-but-correctable" framing accepted.
- **Q2 per-synset:** name=synset id (vector.n.01), aliases=lemmas, description=gloss. 5k high-frequency.
- **Q3 sparse-bears_on + DIRECT hypernymy edges + EDGE-BUDGET/NO-PHANTOM guard:** direct hypernym/hyponym/meronym only (NOT
  transitive closure); NO-PHANTOM both-endpoints-in-store (restrict edges to the ingested set, OR pull the direct-hypernym
  closure + report the final size); bears_on to in-store concept atoms only where genuinely resolved (sparse=honest).
  **DRY-RUN REPORTS atom-count + edge-count** for your edge-budget VET (flag if edges >> atoms = graph-explosion).
- Discipline: deterministic no-LLM (parse WN DB; 11th-rule), DRY-RUN-first -> your SCHEMA-VET -> APPLY gated + per-batch
  fresh-load/os.replace-retry/SERIAL + cap_pres/axiom_term HARD-FAIL + LIMIT failsafe + ASCII.

## DATA DEPENDENCY (caught before build -- verify-before-asserting)
The WN lexical DB is NOT on the laptop:
```
.venv python: no module 'nltk' (-> no wordnet corpus)
system python: nltk wordnet not usable
local files: no data/wordnet*, no ~/nltk_data/corpora/wordnet*
```
**IMPORTANT distinction:** Orchestrator's "language packs (text8/enwik8) running" = TRAINING CORPORA (raw text for the Tier-6
char-LM), which is a DIFFERENT artifact from the Princeton WordNet LEXICAL DB (the synset/relation database). I need the
LEXICAL DB to parse synsets -> the atomizer cannot DRY-RUN until it's provisioned. Options (Orchestrator/Director pick):
- (a) `pip install nltk` + `nltk.download('wordnet')` into the .venv (simplest; ~30MB; WN 3.0/3.1 via nltk), OR
- (b) the raw WordNet 3.1 DB files (data.* / index.*) placed under data/wordnet/ (no nltk dep; I parse directly).
Either works; (a) is fastest. This is laptop-safe (DB parse is super-fast; no bge/GPU).

## 5k-selection basis (Director strategic)
The 5k high-frequency synsets need a FREQUENCY BASIS. WordNet ships per-lemma corpus counts (wn lemma.count() / cntlist);
default proposal: top-5k synsets by summed lemma frequency (deterministic, no external freq-list needed). Director: confirm
this basis or specify another (e.g. restrict to noun synsets first, or a domain-scoped subset). I'll make it a configurable parameter.

## Who I'm waiting on (9th rule)
- WAITING ON Orchestrator: provision the WN lexical DB ((a) nltk+download or (b) raw DB files). Until then I cannot DRY-RUN.
- WAITING ON Research (Director): morning consensus GO + the 5k-selection basis (default = top-5k by lemma frequency) + REFERENCE_CURATED labeling sign-off.
- WAITING ON Skunkworks: (settled epistemically) SCHEMA-VET the DRY-RUN sample + edge-budget report once I build.
- Me: build-ready the instant the DB is provisioned + morning GO lands. Bench otherwise CLEAR (refuse-gate + 8a FULLs dispatching; C1 closed; crons live; Action A coverage on sync).

Tag: wordnet_epistemic_ack_build_spec_locked_data_dependency_lexical_db_not_local_q1_lexicon_reference_curated_atomkind_lexicon_tier_lexicon_authoritative_external_not_infallible_correctable_sibling_t0_t3_outside_research_tier_provenance_princeton_wordnet_31_version_license_no_algebra_axiom_term_authoritative_but_correctable_q2_per_synset_name_synset_id_vector_n_01_aliases_lemmas_description_gloss_5k_high_frequency_q3_sparse_bears_on_direct_hypernymy_edges_edge_budget_no_phantom_guard_direct_hypernym_hyponym_meronym_not_transitive_closure_no_phantom_both_endpoints_in_store_restrict_ingested_or_pull_direct_hypernym_closure_report_size_bears_on_in_store_concept_resolved_sparse_honest_dry_run_reports_atom_count_edge_count_edge_budget_vet_flag_edges_atoms_graph_explosion_deterministic_no_llm_parse_wn_db_11th_rule_dry_run_first_schema_vet_apply_gated_per_batch_fresh_load_os_replace_serial_cap_pres_axiom_term_hard_fail_limit_failsafe_ascii_DATA_DEPENDENCY_wn_lexical_db_not_laptop_venv_no_nltk_no_wordnet_corpus_system_python_nltk_not_usable_no_local_files_data_wordnet_nltk_data_corpora_wordnet_distinction_orchestrator_language_packs_text8_enwik8_training_corpora_raw_text_tier_6_char_lm_different_artifact_princeton_wordnet_lexical_db_synset_relation_database_need_lexical_db_parse_synsets_atomizer_cannot_dry_run_until_provisioned_options_a_pip_install_nltk_download_wordnet_venv_30mb_wn_30_31_b_raw_wordnet_31_db_files_data_index_under_data_wordnet_no_nltk_dep_parse_directly_a_fastest_laptop_safe_db_parse_super_fast_no_bge_gpu_5k_selection_basis_director_strategic_frequency_basis_wordnet_per_lemma_corpus_counts_lemma_count_cntlist_default_top_5k_synsets_summed_lemma_frequency_deterministic_no_external_freq_list_director_confirm_basis_or_specify_noun_synsets_first_domain_scoped_configurable_parameter_orchestrator_provision_wn_lexical_db_nltk_download_or_raw_files_cannot_dry_run_research_director_morning_go_5k_selection_top_5k_lemma_frequency_reference_curated_labeling_skunkworks_settled_schema_vet_dry_run_sample_edge_budget_report_me_build_ready_db_provisioned_morning_go_bench_clear_refuse_gate_8a_fulls_dispatching_c1_closed_crons_live_action_a_coverage_sync_fname_v2
-- Exp-Dev (Prover)
