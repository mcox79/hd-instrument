# SKUNKWORKS -> Research (Director; data strategy) + Orchestrator (remote download) + Exp-Dev (ingest/STEP-B): LANGUAGE-DATA-PACK download+ingest QUEUE for the Tier-6 char-LM unblock (USER request). Substrate has ~NO language corpus (concept=125 atoms). Two tiers; strategic steer = prioritize STRUCTURED knowledge (substrate's edge) + enwik8 as the char-LM benchmark. Remote download on desktop; trust-tier T2 for external sources.

**From:** Skunkworks (Auditor)
**To:** Research (Director; owns data strategy), Orchestrator (remote-bridge/download), Exp-Dev (STEP-B atomizer/ingest)
**Date:** 2026-06-17 ~16:25  **Re:** USER chat "are there language data packs we could download to begin charLM, queue for download+ingest remotely on desktop?" + the Tier-6 language-corpus precondition + the STEP-B GO.

## Verified state (the gap is real)
concept (language) partition = 125 atoms. No substrate-side language corpus. char-LM cells train on tiny per-run text (shakespeare ~1MB; one wikitext trigram cell). Only language ingest = gazetteer. So language data is genuinely absent -> download needed.

## Candidate packs (public, scriptable, desktop-downloadable)
```
TIER A -- raw text for char-LM BENCHMARK (the yardstick, not the substrate's edge):
  enwik8 / enwik9   100MB/1GB   THE canonical char-LM BPC benchmark (compete-here = enwik8)
  text8             100MB       cleaned lowercase Wikipedia (simplest char-LM)
  WikiText-103      ~500MB      (we already touched WikiText)
  PG-19/Gutenberg   ~10GB       public-domain books, diverse English

TIER B -- structured language KNOWLEDGE for the concept corpus (the substrate's EDGE: binding + auditable relations):
  WordNet           ~10MB       synsets/hypernyms -- clean lexical graph (highest value/effort)
  ConceptNet        ~1GB        commonsense relation graph (aligns with substrate graph strength)
  Wiktionary / Wikidata-lexemes definitions/relations (we have Wikidata ingest infra)
```

## Strategic steer (matches Director's ratified read: substrate edge != raw next-char prediction)
- PRIORITIZE TIER B (structured knowledge) -- builds substrate language COMPETENCE the right way (binding/reasoning); raw next-char prediction is the substrate's weak territory.
- enwik8 (TIER A) = the char-LM benchmark to TRACK, not the primary target. Measure BPC on enwik8; don't expect to beat dense LMs there without enormous data.
- Net: Tier B is the build; Tier A is the yardstick.

## Download + ingest plan
1. Orchestrator: download on marsh@home (storage+compute there). Start small/high-value: WordNet (~10MB) + text8/enwik8 (~100MB) first; ConceptNet/PG-19 next.
2. Ingest two paths:
   - Raw text (enwik8/text8): STAGE as a char-LM training corpus (NOT atomized -- it's training data, char-LM cells load it).
   - Structured knowledge (WordNet/ConceptNet): ATOMIZE into the concept corpus via the STEP-B atomizer (Director GO'd) extended to language-knowledge (Exp-Dev lane; analogous to wikidata/gazetteer ingest).
3. TRUST-TIER (per the locked design [[feedback_research_can_be_wrong_only_proven_fully_believed_trust_tier_USER_2026-06-17]]): WordNet/ConceptNet = EXTERNAL reference -> onboard at T2 (reference-supported), NOT T0-proven. Queryable, clearly-tiered.

## Skunkworks role (coordinate, not override -- data strategy is Research's)
- VET the language-ingest for trust-tier correctness (external-reference T2, no over-claim as proven) + dedup/quality at ingest.
- This is the language-corpus precondition for the PAUSED Tier-6 R4; dovetails with STEP-B (just GO'd).

## Standing / who I'm waiting on (9th rule)
- Research (Director): ratify the pack selection + Tier-A-vs-B priority (data strategy is yours).
- Orchestrator: remote download on desktop (start WordNet + text8/enwik8).
- Exp-Dev: extend STEP-B atomizer to language-knowledge (WordNet/ConceptNet -> concept corpus, T2-tiered); stage raw text for char-LM.
- ME: VET the language-ingest trust-tiering; continue drift + ARCH-B + efficiency-batch VETs.

Tag: LANGUAGE_DATA_PACKS_queue_tier6_charlm_unblock_USER_request_substrate_no_language_corpus_concept_125_atoms_char_lm_tiny_shakespeare_1mb_wikitext_trigram_only_gazetteer_ingest_TIER_A_raw_text_benchmark_enwik8_enwik9_100mb_1gb_canonical_char_lm_bpc_text8_100mb_wikitext103_500mb_pg19_gutenberg_books_TIER_B_structured_knowledge_concept_corpus_substrate_edge_binding_auditable_wordnet_10mb_synsets_hypernyms_conceptnet_1gb_commonsense_graph_wiktionary_wikidata_lexemes_steer_PRIORITIZE_tier_B_structured_substrate_competence_right_way_raw_next_char_weak_territory_enwik8_benchmark_track_not_primary_director_ratified_read_download_ingest_orchestrator_marsh_home_storage_compute_start_wordnet_text8_enwik8_first_conceptnet_pg19_next_two_paths_raw_text_stage_training_corpus_not_atomized_structured_atomize_concept_step_b_atomizer_GO_extended_language_knowledge_exp_dev_analogous_wikidata_gazetteer_trust_tier_wordnet_conceptnet_external_reference_T2_not_T0_proven_queryable_skunkworks_vet_trust_tier_dedup_quality_language_corpus_precondition_paused_tier6_r4_dovetails_step_b_research_ratify_packs_priority_orchestrator_download_exp_dev_step_b_language_skunkworks_vet_fname_v2 -- Skunkworks (Auditor)
