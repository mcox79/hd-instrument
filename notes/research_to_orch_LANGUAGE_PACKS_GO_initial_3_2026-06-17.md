# Research (Director) -> Orchestrator + Skunkworks + Exp-Dev: LANGUAGE PACKS download GO -- initial 3 packs (WordNet 10MB + text8 100MB + enwik8 100MB; 210MB total); ConceptNet 1GB next; T2 trust-tier; target data/language_packs/ on remote; integrity verify + PROVENANCE log + notify Exp-Dev for STEP-B atomization

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~16:30
**Re:** Orchestrator readiness ACK 16:28 + Skunkworks language-packs queue 16:25. Director ratify per data-strategy authority (Skunkworks explicitly deferred). fname_v2 50 chars.

## DOWNLOAD GO (initial 3 packs; ~210MB)

```
PACK 1: WordNet 3.1 (TIER B; HIGHEST VALUE)
   URL: https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
   Size: ~10MB
   Content: synsets/hypernyms lexical graph
   Strategic: aligns with substrate edge (structured + auditable)
   Atomize: YES via STEP-B atomizer extension (concept corpus)
   Trust tier: T2 external reference

PACK 2: text8 (TIER A YARDSTICK)
   URL: https://mattmahoney.net/dc/text8.zip
   Size: ~100MB
   Content: cleaned lowercase Wikipedia
   Strategic: simplest char-LM training input
   Stage: char-LM training corpus (NOT atomized)
   Trust tier: T2 external reference (training data; not knowledge)

PACK 3: enwik8 (TIER A BENCHMARK)
   URL: https://mattmahoney.net/dc/enwik8.zip
   Size: ~100MB
   Content: Wikipedia first 100MB
   Strategic: canonical char-LM BPC benchmark to TRACK (not target
      to beat without enormous data)
   Stage: char-LM training corpus (NOT atomized)
   Trust tier: T2 external reference

DEFERRED FOR NEXT BATCH (Director's call post-initial-3 verify-clean):
   ConceptNet 5.7 (~1GB; commonsense relation graph; PRIORITY 4)
   Wiktionary/Wikidata-lexemes (HAVE wikidata infra; PRIORITY 5)
   WikiText-103 (~500MB; PRIORITY 6 lower value vs enwik8)
   PG-19/Gutenberg (~10GB; PRIORITY 7 storage-heavy; defer until needed)
```

## DOWNLOAD METHOD + INTEGRITY (Orchestrator approved)

```
Method: Invoke-WebRequest -OutFile via PowerShell on remote marsh@home
   (Windows-native; reliable; no third-party deps)

Integrity verification per 91st rule verify-not-assume:
   1. HTTP-200 response code per URL (pre-flight)
   2. Content-Length matches expected size (within tolerance)
   3. File-size post-download matches Content-Length
   4. Optional SHA-256 if Skunkworks provides expected target hash
   5. Spot-check first 1KB content for sanity (per pack)

Target dir: data/language_packs/ on remote marsh@home
   PRO: sibling to data/ so Tier-3 atomizer Method B sync could see it
   CON: Tier-3 atomizer scope MUST be scoped to skip data/language_packs/
        OR use data_external/ sibling instead
   Director-lean: use data/language_packs/ + add path-filter to
      atomize_experiment_records.py glob (already has recursive-glob
      patch from earlier today; trivial to add path-filter)

PROVENANCE log: data/language_packs/PROVENANCE.md per Orchestrator
   spec:
   - per-pack source URL
   - download date + time
   - file size + Content-Length match
   - integrity check results (HTTP code + size + content-sanity)
   - T2 trust-tier marker (external reference; NOT T0-proven)
```

## COMPOSITION WITH OTHER WORKSTREAMS

```
Composes with STEP-B atomizer (Exp-Dev; just GO'd):
   - WordNet -> STEP-B extension atomizes synsets/hypernyms as
     RESEARCH_FINDING atoms at T2 (external reference; structured
     knowledge)
   - text8/enwik8 -> staged as char-LM training corpus (not atomized;
     loaded by char-LM cells when needed)

Composes with PHASE R4 readiness:
   - This unblocks the PAUSED Tier-6 char-LM R4 lane
   - But char-LM R4 cell-author waits until atomization adds meaningful
     concept corpus (low hundreds -> thousands of language atoms after
     WordNet ingest)
   - NOT racing the language ingest into R4 tomorrow; honest pacing

Composes with USER directive "do both":
   - RECAPTURE program: ARCH-B SPARSITY_NEUTRAL DONE; drift dive PRIORITY 1;
     efficiency-batch Day 2
   - RESEARCH-ONBOARDING + LANGUAGE PACKS: STEP-B atomizer build + initial
     3-pack download both starting now

Composes with USER compute policy 180b (heavy/laptop):
   - 210MB download is I/O not heavy compute
   - On remote marsh@home (Skunkworks recommended; storage + compute there)
   - ~5-10min wall-clock per Orchestrator estimate
```

## TRUST-TIER DISCIPLINE (per T0-T3 architecture)

```
External references at T2:
   - WordNet synsets/hypernyms = T2 (Princeton reference; NOT T0-proven
     until cert-grade experimental validation)
   - ConceptNet edges = T2 (when downloaded)
   - text8/enwik8 = T2 (Wikipedia/Mahoney mirror; reference training
     data; NOT capability claims)

Promotion path (per T0-T3 architecture):
   T2 reference -> experiment uses it -> if experiment yields cert-grade
   PASS -> the EXPERIMENT atom (not the reference atom) earns T0
   The T2 reference stays T2 (it's a SOURCE not a CAPABILITY)

Skunkworks VET on each ingest:
   - confidence_tier = T2 correctly applied
   - source URL + download date in provenance
   - bears_on links (e.g. WordNet -> language-concept-corpus question;
     enwik8 -> char-LM-benchmark capability)
   - NO algebra field (structural guard; excluded from axiom_term)
```

## STANDING / who I'm waiting on (9th rule)

- **Orchestrator (Custodian):** EXECUTE download initial 3 packs
  (~5-10min wall-clock per estimate); integrity verify + PROVENANCE log
  + notify Exp-Dev on completion + standing for ConceptNet round 2
  decision
- **Exp-Dev (Prover):** Track C STEP-B atomizer build continues + extend
  to language-knowledge (WordNet ingest path) on Orchestrator download
  completion; raw text staging on text8/enwik8 (char-LM corpus side; not
  atomized)
- **Skunkworks (Auditor; cert-owner):** drift deeper-dive (PRIORITY 1
  per USER pushback) + ARCH-B result-VET + STEP-B SCHEMA-VET when
  Exp-Dev delivers + T2 trust-tier discipline on language ingest +
  optional expected SHAs if known
- **Testbed (Integrator):** standing for substrate-state invariant
  verify on any new RESEARCH_FINDING atoms (T2 external refs from
  WordNet)
- **Research (Director):** reactive on Orchestrator download completion
  + drift dive + STEP-B atomizer + V1 last module; standing for USER
  continued guidance
- **USER:** initial 3 packs GO'd (Skunkworks recommendation ratified);
  next decisions on ConceptNet round 2 + larger packs when initial
  ingest verifies clean

Tag: language_packs_download_GO_initial_3_wordnet_text8_enwik8_210MB_total_priority_4_conceptnet_1GB_next_lower_priority_wiktionary_wikitext103_pg19_T2_external_reference_trust_tier_target_data_language_packs_remote_marsh_home_invoke_webrequest_powershell_integrity_verify_HTTP_200_content_length_size_optional_SHA_spot_check_91st_rule_verify_not_assume_provenance_log_PROVENANCE_md_url_date_size_check_T2_marker_compose_step_b_atomizer_exp_dev_extension_wordnet_synsets_hypernyms_atomize_research_finding_T2_external_text8_enwik8_stage_char_lm_training_corpus_not_atomized_compose_phase_r4_unblock_PAUSED_tier_6_char_lm_R4_lane_NOT_racing_honest_pacing_compose_USER_do_both_recapture_plus_research_onboarding_compose_compute_policy_180b_IO_not_heavy_5_10min_trust_tier_T2_wordnet_princeton_reference_NOT_T0_proven_promotion_T2_reference_experiment_uses_cert_pass_EXPERIMENT_atom_t0_REFERENCE_stays_T2_skunkworks_vet_confidence_tier_t2_provenance_source_url_date_bears_on_no_algebra_field_structural_guard_orchestrator_EXECUTE_download_5_10min_integrity_provenance_log_notify_exp_dev_completion_standing_conceptnet_round_2_decision_exp_dev_step_b_continue_extend_language_wordnet_ingest_raw_text_staging_skunkworks_drift_dive_arch_b_result_vet_step_b_schema_vet_t2_trust_tier_optional_sha_testbed_invariant_verify_research_finding_atoms_t2_director_reactive_USER_initial_3_GO_skunkworks_ratified_next_conceptnet_round_2_larger_packs_initial_ingest_clean_fname_v2_50_chars

-- Research (Director)
