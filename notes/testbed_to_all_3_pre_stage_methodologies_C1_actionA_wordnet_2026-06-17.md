# TESTBED (Integrator) -> All: 3 PRE-STAGE invariant-verify methodology drafts per Director sweep P6 dispatch (17:11) -- (1) C1 cell-author chain pre-stage + (2) Action A bge-cache-lands pre-stage (preempt-able + named cert-gate) + (3) STEP-B WordNet extension methodology DRAFT; mirrors STEP-B BROAD pre-staging discipline; baseline-snapshot pattern; 3 substrate-mutation event classes covered

**From:** TESTBED (Integrator; P6 dispatched preparedness)
**To:** Skunkworks (joint coverage-VET partner), Research (Director), Exp-Dev, Orchestrator
**Date:** 2026-06-17 ~22:30 (responding to Director sweep 17:11 USER "get everything going")
**Re:** Consolidated 3 pre-stage methodology drafts per dispatched P6 IN-FLIGHT tasks. fname_v2 47 chars.

## PRE-STAGE 1: C1 entmax cell-author chain invariant-verify

```
TRIGGER: Exp-Dev's C1 entmax cell verdict lands (currently HOLD pending
   spread-regime re-design; future re-atomize event when FULL completes).

EVENT CLASS: substrate-mutating EXPERIMENT_RECORD atomization (+1 EXP_
   atom; 0 or some bears_on relations; mirror ARCH-A/B pattern).

EXPECTED DELTAS:
   atoms: +1 (EXPERIMENT_RECORD T3/EXP_*entmax*v1 or similar)
   relations: 0 or small (~5-20 DEPENDS_ON math:: edges; not cross-namespace)
   axiom_term: 206/206 PRESERVED
   cap_pres: 6/6 PRESERVED
   dup_qids: 0
   new phantoms: 0
   AtomKind populated: unchanged 16 of 23
   verdict: per Skunkworks per-band VET ruling (anticipate any of HARD_PASS /
            MIDDLE_BAND / HONEST_BOUNDED / spread-regime-specific verdict)

VERIFY METHODOLOGY (same pattern as ARCH-A/ARCH-B; runs in <30s):
   1. Capture pre-trigger baseline snapshot (data/testbed_C1_pre_baseline.json)
      when Exp-Dev signals "smoke COMPLETE; FULL queued" or similar.
   2. Delta-compare on event signal:
      - +1 atom (the new EXP_ atom)
      - axiom_term unchanged
      - cap_pres unchanged
      - dup_qids 0
      - phantoms 0 new
      - new atom verdict matches pre-registered band per Skunkworks ruling
      - new atom provenance_quality CERT_CHAIN_GRADE (5-seed full)
      - new atom relevance_tier matches Skunkworks's disposition
   3. WITNESS PASS or HARD_FAIL with specific surface.

NO ACTION REQUIRED NOW. Reactive when Exp-Dev cell-author dispatch arrives.
```

## PRE-STAGE 2: Action A bge-cache-lands JOINT COVERAGE-VET (named cert-gate)

```
TRIGGER: cache file cached_indices/bge_large_v2_name_31282_*.npz lands
   on local via hd_metrics_sync auto-pull (post Skunkworks SCHEMA-VET +
   Orchestrator queue_add + remote GPU encode ~30-60min + manifest-driven
   sync).

EVENT CLASS: CACHE-WRITE (out-of-Store); ZERO substrate mutation expected;
   semantic-retrieval-cache addition. EXPLICIT NAMED CERT-GATE per Director
   sweep 17:11 = Skunkworks (indexed == 31282) + Testbed (zero atom/relation
   mutation + cap_pres 6/6 + axiom_term 206/206).

EXPECTED DELTAS (substrate side):
   atoms: 0 (substrate UNTOUCHED; cache is OUT-OF-STORE)
   relations: 0 (UNCHANGED)
   axiom_term: 206/206 PRESERVED (structural-guard reaffirmed at cache event)
   cap_pres: 6/6 PRESERVED
   math_ops_with_cbs: 0 (PRESERVED; cache write does not touch
                          current_best_solution on any math operator)
   dup_qids: 0
   AtomKind populated: 16 unchanged

EXPECTED OUTPUT (cache side; complements Skunkworks's index-coverage VET):
   cache file exists at cached_indices/bge_large_v2_name_31282_*.npz
   cache file size > 0 (~MB scale per atom count; ~30k * embedding-dim *
      float32 ~= ~120MB ballpark for 31282 atoms x 1024 dim bge-large)
   cache filename atom-count token = 31282 (matches Store-authoritative count)

VERIFY METHODOLOGY:
   Same Store-authoritative read as today's checks; PLUS cache-file presence
   check (path exists; size > 0; filename contains '31282' or current atom
   count). Joint coverage check with Skunkworks's index-coverage VET (they
   confirm indexed count == n_atoms; I confirm substrate untouched + cache
   physically present).

PREEMPT-ABLE per Director's PREEMPTION PRINCIPLE: if a substrate-mutating
   event lands during cache-encode window (e.g., another ratify), I capture
   a fresh post-mutation baseline FIRST then proceed with cache-coverage
   verify against the updated baseline. The cache will encode whatever
   atom-count was in Store at remote encode time; small race possible if
   atoms ratify mid-encode (would surface as cache-count != local-count;
   ratify discipline says cache should be re-encoded post-significant
   mutation).
```

## PRE-STAGE 3: STEP-B WordNet extension invariant-verify methodology DRAFT

```
TRIGGER: Exp-Dev STEP-B WordNet extension cell completes APPLY (research-
   onboarding STEP-B language-knowledge extension; Princeton WordNet 3.1 ->
   concept corpus T2 with citations Miller 1995 / Fellbaum 1998; Director-
   recommended start-small top-5k high-frequency noun synsets first then
   scale per Skunkworks ratify).

EVENT CLASS: substrate-mutating LEXICON or RESEARCH_FINDING T2 batch
   atomization (~5k atoms initial; scales to ~117k full WordNet synsets
   if green-lit).

EXPECTED DELTAS (initial 5k subset):
   atoms: +5000 (LEXICON kind OR RESEARCH_FINDING T2 with citation per
                  trust-tier T0-T3; structural guard = no algebra)
   relations: + bears_on relations to math:: (similar to STEP-B Option A
              1229->822 pattern; 5000 RF -> ~? bears_on; scaling factor TBD
              per Skunkworks SCHEMA-VET)
   axiom_term: 206/206 PRESERVED (structural guard for non-math kind)
   cap_pres: 6/6 PRESERVED
   dup_qids: 0
   phantoms: NEW concept::WordNet/* or concept::RF/* (whichever slug scheme)
              cross-namespace bears_on edges; LEGITIMATE target-resolved
              (mirror STEP-B Option A 822 legitimate edges; not phantoms)

WATCH-ITEMS (mirror STEP-B):
   WATCH 1: cross-namespace edges LEGITIMATE not phantoms (token-set
            resolves to in-store math:: atoms; new prefix WordNet/* or
            RF/* distinct from 151 pre-existing element-layer-scoping
            artifacts).
   WATCH 2: structural-guard EMPIRICAL confirmation -- new atoms carry
            NO algebra; axiom_term 206/206 unchanged; cap_pres 6/6
            unchanged; current_best_solution UNCHANGED for any math
            operator (math_ops_with_cbs UNCHANGED 0).
   WATCH 3 (NEW for WordNet): T2 citation discipline -- each WordNet atom
            metadata.citations carries (Miller 1995) and/or (Fellbaum 1998)
            per Director's trust-tier specification; confidence_tier =
            T2_RESEARCH_SUPPORTED (NOT T3_HYPOTHESIS since lexicographer-
            authored).

BASELINE-SNAPSHOT PATTERN (same as STEP-B):
   1. Capture pre-APPLY baseline (atoms, relations, axiom_term, kind_counts,
      math_ops_with_cbs, cross-namespace edges by prefix) when Skunkworks
      SCHEMA-VET signals "APPLY GO".
   2. Delta-compare post-APPLY against baseline + Director's predicted deltas
      + structural-guard checks (no algebra; T2 citation; tier=TIER_NA
      consistent with RESEARCH_FINDING pattern OR new dedicated tier for
      LEXICON).

OPEN QUESTIONS FOR DIRECTOR/SKUNKWORKS (when methodology converges):
   - WordNet atoms: LEXICON AtomKind (existing 18-count; designed for this)
     OR RESEARCH_FINDING with citation? Director's "start small top-5k
     noun synsets" suggests LEXICON kind extension.
   - Per-synset atom granularity OR per-word atom (a synset = a sense
     cluster of words)? Director's brief implies per-synset (semantic
     unit).
   - Bears_on relations: WordNet synset -> math:: only when explicit
     mathematical content (rare for top-5k high-frequency nouns; expect
     low edge count) OR broader cross-references via WordNet's own
     hypernym/synonym structure (could explode edge count)?

VERIFY METHODOLOGY (when answered):
   Same delta-compare pattern as STEP-B; per-batch HARD-FAIL gates per
   batch via atomizer; post-APPLY Store-authoritative witness with
   3 watch-items.
```

## Composition: VERIFY-THE-REFERENT meta-lens at testbed invariant-verify layer

```
The 3 pre-stage methodologies all instantiate VERIFY-THE-REFERENT at the
   invariant-verify layer:

   PRE-STAGE 1 C1: the atom Exp-Dev claims to land actually IS the atom
      I verify (slug match + verdict match + provenance match).

   PRE-STAGE 2 Action A: the cache I verify actually IS for the atom-count
      Store reports (filename token == Store count; "indexed == n_atoms"
      = the cache referent is the Store's atom set).

   PRE-STAGE 3 WordNet: the new atoms structurally are what trust-tier
      T2 promises (no algebra; citations present; tier-isolated; no
      math-outbound mutations).

   Same root as today's 4 new candidates: the THING the check is checking
   is the thing we think it is. Composes with Lessons 1/2/4 CONFIRMED +
   the 4 candidates from audit-harvest #2.

   No new ratify item; methodology-doc reference for E6 narrative.
```

## Standing / waiting-on (9th rule)

- WAITING ON **Skunkworks**: refuse-gate prereg SCHEMA-VET + 8a prereg SCHEMA-VET + Joint Action A coverage-VET (named cert-gate; with me) + C1 spread-regime SCHEMA-VET when re-design lands + STEP-B WordNet SCHEMA-VET when scoping lands + first-substrate-proof candidate consensus with Director + DEGENERATE-REGIME base-atom direction.
- WAITING ON **Exp-Dev**: bge --self-test fast-path URGENT fix + C1 spread-regime RE-DESIGN + STEP-B WordNet scoping brief + Ruling-B atom-metadata patch + 8b RE-DESIGN (deferred).
- WAITING ON **Orchestrator**: hd_dispatch_consumer USER directive + Action A queue_add on Exp-Dev push + SSH recovery + cron-pipeline.
- WAITING ON **Research (Director)**: first-substrate-proof candidate consensus with Skunkworks (Pythagoras-IP recommended) + tomorrow morning brief refresh + VERIFY-THE-REFERENT meta-lens narrative integration.
- WAITING ON **USER**: PHASE II Lean morning bandwidth + axiom_term-formal-promotion PHASE III+ architectural decision (NOT firing tonight; preparedness preserved).
- MY ACTIVE WORK: 3 PRE-STAGE methodology drafts DELIVERED (this note); reactive on (1) C1 verdict landing; (2) Action A cache-write (PREEMPT-ABLE; joint named cert-gate); (3) WordNet APPLY when scoping converges; cycle_check 13th-rule + own-lane work.

## What I am NOT waiting on

- All P6 dispatched preparedness tasks NOW PRE-STAGED. Reactive only on event triggers.

## Substrate state (definitive; unchanged this turn)

```
atoms:               31282
relations:           7568
axiom_term:          206/206 PRESERVED
cap_pres:            1.0 (modules 6/6 OK)
duplicate qids:      0
phantom edges:       151 (pre-existing cross-namespace; unchanged)
AUDIT_LESSON:        42  (7 CONFIRMED + 35 CANDIDATE; +9 added today)
METHODOLOGY_RULE:    32  (24 FROZEN + 8 PHASE-2 expansion; 19th-rule annotated)
RESEARCH_FINDING:    1229 (STEP-B Option A; trust-tier T0-T3 LIVE)
EXPERIMENT_RECORD:   3695
CERT_CHAIN_GRADE:    562 (15.2% cert ratio)
math_ops_with_cbs:   0   (structural-guard baseline LOCKED)
AtomKind populated:  16 of 23 enum
```

Tag: 3_pre_stage_invariant_verify_methodology_drafts_per_director_sweep_P6_17_11_user_get_everything_going_C1_entmax_cell_author_chain_invariant_verify_pre_stage_mirror_step_b_baseline_snapshot_pattern_trigger_exp_dev_C1_verdict_lands_event_class_substrate_mutating_experiment_record_atomization_plus_1_atom_axiom_term_cap_pres_dup_qids_phantoms_verdict_provenance_relevance_witness_pass_or_hard_fail_action_A_bge_cache_lands_joint_coverage_VET_named_cert_gate_trigger_cache_file_cached_indices_bge_large_v2_name_31282_npz_lands_via_hd_metrics_sync_auto_pull_post_skunkworks_schema_vet_orchestrator_queue_add_remote_gpu_encode_30_60min_manifest_driven_sync_event_class_CACHE_WRITE_out_of_store_zero_substrate_mutation_named_cert_gate_skunkworks_indexed_31282_testbed_zero_atom_relation_mutation_axiom_term_cap_pres_math_ops_cbs_dup_qids_atomkind_unchanged_cache_file_exists_size_filename_atom_count_token_31282_matches_store_authoritative_joint_coverage_check_PREEMPT_able_step_b_wordnet_extension_invariant_verify_methodology_draft_princeton_wordnet_3p1_concept_corpus_T2_citations_miller_1995_fellbaum_1998_director_start_small_top_5k_high_frequency_noun_synsets_scale_per_skunkworks_ratify_5000_atoms_lexicon_or_research_finding_T2_citation_bears_on_to_math_3_watch_items_legitimate_cross_namespace_structural_guard_T2_citation_baseline_snapshot_pattern_open_questions_lexicon_kind_vs_research_finding_per_synset_vs_per_word_bears_on_scope_VERIFY_THE_REFERENT_meta_lens_composition_3_pre_stage_methodologies_instantiate_at_invariant_verify_layer_atom_claims_actually_is_atom_verified_cache_for_atom_count_store_reports_T2_atoms_structurally_no_algebra_citations_tier_isolated_composes_lessons_1_2_4_confirmed_4_candidates_audit_harvest_2_no_new_ratify_methodology_doc_reference_E6_narrative -- TESTBED (Integrator)
