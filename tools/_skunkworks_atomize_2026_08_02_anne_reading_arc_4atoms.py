"""
A5-gated atomization: Anne of Green Gables reading arc (curriculum-pivot first
real-book reading). AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute
off the raw data files listed per-atom below (gender_coref_density_report.json,
causal_adjacency_report.json, anne_of_green_gables.meta.json,
exp_read_anne_glassbox_v1/ledger.json before/after commits ba1136f1e/18a0341b8,
exp_read_anne_glassbox_v2_honest_ledger/{ledger.json,comparison_salience_vs_strict_cb.json}),
NOT off verdict_msg or spawn-prompt summary. Also independently reran
verification/verify_coreference_resolver.py (.venv pytest, 8/8 green,
tracing=False) rather than trusting the commit-message claim.

Writes FOUR atoms (seq 29627-29630; 3 in math, 1 in meta) + 4 matching
cert_ledger.jsonl entries, atomically (tmp -> os.replace) per file, then
verify-loads all files and runs an integrity check. LOCAL-ONLY: no origin
push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
META_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_DIFFICULTY = 29627
SEQ_READS_USABLY = 29628
SEQ_CONSOLIDATION = 29629
SEQ_MASKING_BUGS_META = 29630

ATOM_DIFFICULTY = {
    "atom_id": (
        "math::anne_of_green_gables_curriculum_difficulty_verified_real_download_not_"
        "local_syntax_harder_38of38_chapters_ge2_female_named_mean5p61_ge3_34of38_89pct_"
        "exceeds_mcguffey_handmined_dense_3p67_by_construction_no_mining_needed_"
        "causal_automated_miner_245of245_gap1_uninformative_property_of_connective_grammar_"
        "manual_spotcheck_n4_3of4_nonadjacent_gap_up_to_23_chapters_anne_gilbert_arc_"
        "curriculum_pivot_validated_29d8696b0_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_DIFFICULTY,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "REAL-DIFFICULTY-CONFIRMED for Anne of Green Gables (PG #45) as the curriculum's first "
        "genuinely-hard book, with an honest correction to the original selection-note framing. "
        "Independent recompute off the raw MEASURED report JSONs (not the summary doc) exactly "
        "reproduces every headline number. Anne is NOT harder than McGuffey 4th on local "
        "sentence-syntax metrics (shorter mean sentence length, MORE simple-sentence fraction, "
        "slightly LOWER adjacent-sentence entity continuity) -- difficulty comes from cast "
        "density and narrative structure, not syntax. Same-gender coref density materially "
        "exceeds McGuffey's hand-mined dense gold, present BY CONSTRUCTION across the whole book "
        "(no mining needed). Non-adjacent causation is real (manual spot-check) but the automated "
        "explicit-connective miner that caught McGuffey's collapse is UNINFORMATIVE here -- "
        "correctly diagnosed as measuring connective-grammar locality (true in any text), not "
        "narrative structure; a causal-inference cell on Anne needs a narrative situation-model "
        "gold, not a connective-mining gold."
    ),
    "anchor": "anne_of_green_gables_difficulty_verification",
    "anchor_name": "anne_of_green_gables_difficulty_verification_2026_08_02",
    "cell": (
        "data/corpora/anne_of_green_gables/cleaned/{gender_coref_density_report.json,"
        "causal_adjacency_report.json,anne_of_green_gables.meta.json}; commit 29d8696b0"
    ),
    "headline": (
        "Anne of Green Gables difficulty is REAL and MEASURED on the actual downloaded text "
        "(not local syntax; cast density + narrative structure): 38/38 chapters (100%) have "
        ">=2 co-present named female characters, 34/38 (89%) have >=3, mean 5.61/chapter "
        "(max 10) -- exceeds McGuffey's hand-mined dense gold (3.67/passage) by construction. "
        "Automated causal-connective adjacency check is 245/245 (100%) gap=1, same as McGuffey, "
        "but this is diagnosed as a property of connective grammar not narrative causation; "
        "manual spot-check (n=4) found 3/4 genuine non-adjacent narrative payoffs (one at "
        "23-chapter gap, the Anne/Gilbert reconciliation arc)."
    ),
    "key_metrics": {
        "n_words_measured": 105601,
        "n_chapters": 38,
        "mean_sentence_len": 17.17,
        "mean_sentence_len_mcguffey4th": 20.92,
        "pct_sentences_le15w": 54.9,
        "pct_sentences_le15w_mcguffey4th": 44.1,
        "pct_sentences_simple_le1connector": 44.9,
        "pct_sentences_simple_le1connector_mcguffey4th": 31.5,
        "proper_noun_density_per100w": 5.89,
        "proper_noun_density_per100w_mcguffey4th": 4.76,
        "pronoun_density_per100w": 6.17,
        "pronoun_density_per100w_mcguffey4th": 6.67,
        "n_recurring_names": 307,
        "n_recurring_names_mcguffey4th": 291,
        "composition_density_est": 0.509,
        "composition_density_est_mcguffey4th": 0.552,
        "coref_density_chapters_ge2_female_named": 38,
        "coref_density_chapters_total": 38,
        "coref_density_chapters_ge3_female_named": 34,
        "coref_density_mean_per_chapter": 5.605,
        "coref_density_max_in_one_chapter": 10,
        "coref_density_mcguffey_dense_mined_baseline": 3.67,
        "causal_automated_n_instances": 245,
        "causal_automated_pct_gap1_adjacent": 100.0,
        "causal_automated_n_cross_chapter": 0,
        "causal_manual_spotcheck_n": 4,
        "causal_manual_spotcheck_nonadjacent": 3,
        "causal_manual_spotcheck_max_chapter_gap": 23,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent .venv recompute: (1) gender_coref_density_report.json per_chapter[].distinct_"
        "female_named recomputed from the raw per-chapter array (not the summary block) -> ge2=38/38, "
        "ge3=34/38, mean=5.605, max=10, exactly matching the note's summary block (cross-check that "
        "the summary wasn't hand-typed independent of the per-chapter data). (2) causal_adjacency_"
        "report.json summary: n_instances=245, gap_distribution={'1':245}, pct_gap1_adjacent=100.0, "
        "n_cross_chapter_links=0 -- reproduces exactly. (3) anne_of_green_gables.meta.json: all 8 "
        "cited stats (n_words, mean_sentence_len, pct_sentences_le15w, pct_sentences_simple, "
        "proper_noun_density, pronoun_density, n_recurring_names, composition_density_est) reproduce "
        "byte-exact against the note's table. (4) Manual n=4 spot-check verified by reading the note's "
        "cited verbatim anchors and chapter numbers directly (not independently re-mined -- this is a "
        "small hand sample, deflated accordingly in honest_scope)."
    ),
    "composes_seq": [],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_DIFFICULTY - 1,
    "honest_scope": (
        "The same-gender coref density and sentence-syntax comparisons are fully MEASURED (report "
        "JSONs recomputed independently). The non-adjacent-causation claim rests on a SMALL manual "
        "sample (n=4, not the recommended n=15-25) -- genuine and correctly time-boxed/flagged as such "
        "in the source note, but not yet a distribution. The automated causal miner's 245/245 100%-"
        "adjacent result is real but explicitly NOT evidence against non-adjacent causation existing "
        "(it measures a different, uninformative-here property) -- this atom preserves that correction "
        "rather than reporting the raw 100%-adjacent number without context, which would be a false-"
        "negative trap. Definite-description bridging (52 instances) is noted but not verified against "
        "actual named-character resolution."
    ),
    "framing_correction": (
        "None vs the source note -- the note itself already self-corrected the naive read of its "
        "own automated causal-adjacency measurement (245/245 gap=1 does NOT mean 'no non-adjacent "
        "causation', it means the miner can't detect narrative-level unmarked payoffs); this atom "
        "preserves that correction rather than flattening it into a headline 100%-adjacent number."
    ),
    "revival_criteria": "n/a (this is a corpus-difficulty verification gate, not a build-now/HF cell).",
    "primitive_assessment": (
        "No new primitive; reusable methodology: verify claimed corpus-difficulty properties on the "
        "REAL downloaded text via the SAME stdlib measurement tools used on the prior corpus (here: "
        "McGuffey's compute_stats() + causal-adjacency miner reused verbatim) before building any "
        "mechanism on the new corpus -- catches selection-note claims that don't survive contact with "
        "the actual text (the McGuffey collapse precedent this session is explicitly guarding against)."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM verification gate, not an HF cell).",
    "fairness_verdict": (
        "FAIR: recompute is off the raw per-chapter/per-instance JSON arrays, not the note's own "
        "summary blocks, and every cited number reproduces exactly. The note itself already applies "
        "symmetric anti-negativity (does not overclaim the causal-adjacency 245/245 result as evidence "
        "of narrative simplicity)."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check (concept: same-gender coreference / situation model / curriculum "
        "difficulty) returns top hits at cosine<=0.295 (coherence-schema-fit-gate note, situation-model-"
        "harder-construction-generalization metrics, discourse-topic-thread-coherence note) -- below the "
        "0.30 dup-check threshold. Genuinely novel: first difficulty-verification gate run on a real "
        "narrative novel rather than a curated graded-reader corpus."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_READS_USABLY = {
    "atom_id": (
        "math::anne_reads_usably_named_character_tracking_v1_supplied_data_extraction_not_"
        "bolt_on_parser_gazetteer_pronoun_clausesplit_feeds_earned_coref_plus_situation_model_"
        "before_37_entities_noise_inflated_avonlea_placename_absorbs_615_mentions_604_pronoun_"
        "ambiguous_pronoun_87pct_decode_selfconsistency_89p8pct_after_4_datafixes_9_entities_"
        "clean_avonlea_contamination_zero_ambiguous_pronoun_38pct_decode_selfconsistency_"
        "regresses_67p2pct_diagnosed_slot_capacity_not_coref_bug_fallback_unresolvable_rises_"
        "80_to_298_honest_exposure_not_regression_ba1136f1e_18a0341b8_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_READS_USABLY,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "READS-USABLY (honestly scoped to NAMED-CHARACTER identity tracking, not full comprehension): "
        "the reader pipeline reads raw Anne of Green Gables ch.1-3 prose end-to-end through a "
        "supplied-DATA extraction layer (name gazetteer + pronoun list + clause-split -- DATA per the "
        "no-bolt-on-parser lock, not an added reading mechanism) feeding the already-earned coref "
        "resolver (hdlab.coreference_resolver.run_match_or_allocate) and situation-model accumulator "
        "(hdlab.situation_model_accumulate.AccumulateRegister). The first pass (ba1136f1e) was "
        "diagnosed as DATA-QUALITY-BLOCKED, not mechanism-blocked: a naive gazetteer mined the "
        "place-name 'Avonlea' as a wildcard-gender magnet that silently absorbed 604 of 639 pronoun "
        "mentions (615 total mentions on a single false entity), driving 87% of pronouns into "
        "ambiguous-resolution status despite the underlying coref mechanism being sound. Four targeted "
        "DATA/lexical fixes (curly-quote handling, contraction-tokenizer fix, person-context gazetteer "
        "filter, gender-backfill pass) collapsed the false entity to zero and cut ambiguous-pronoun "
        "rate to 38%, with 9 correctly-distinguished named entities (Matthew/Marilla/Rachel/Anne/"
        "Cordelia/Diana/Barry/Jane/Spencer) replacing 37 noise-inflated ones."
    ),
    "anchor": "read_anne_glassbox_v1",
    "anchor_name": "read_anne_glassbox_v1_extraction_dataquality_fix",
    "cell": "data/exp_read_anne_glassbox_v1/ledger.json; commits ba1136f1e -> 18a0341b8",
    "headline": (
        "Anne of Green Gables ch.1-3 reads usably for named-character tracking after 4 supplied-DATA "
        "extraction fixes (not a bolt-on parser): entities 37 (noise-inflated) -> 9 (clean); Avonlea "
        "place-name contamination 615 mentions (604 pronoun) -> 0; ambiguous-pronoun rate 87% (555/639) "
        "-> 38% (263/693); in_quote deixis flag 0/1031 -> 16/1031 (curly-quote bug fixed). Honest "
        "residual: situation-model decode self-consistency REGRESSED 89.8%->67.2%, diagnosed as a "
        "bounded-register slot-capacity interaction (max_event_slots=8) exposed by mention-count "
        "concentration on the now-correctly-tracked real entities, not a coref/gender regression; "
        "fallback_no_compatible_candidate RISES 80->298, which is HONEST exposure of previously-"
        "silently-mismatched unresolvable pronouns (mostly unextracted generic NPs), not a new failure."
    ),
    "key_metrics": {
        "before_n_entities_tracked": 37,
        "after_n_entities_tracked": 9,
        "before_avonlea_mention_count": 615,
        "before_avonlea_pronoun_absorbed": 604,
        "after_avonlea_present": False,
        "before_ambiguous_pronoun_count": 555,
        "before_n_pronoun_mentions": 639,
        "before_ambiguous_pronoun_rate": 0.8686,
        "after_ambiguous_pronoun_count": 263,
        "after_n_pronoun_mentions": 693,
        "after_ambiguous_pronoun_rate": 0.3795,
        "before_n_mentions_flagged_in_quote": 0,
        "after_n_mentions_flagged_in_quote": 16,
        "n_mentions_total_slice": 1031,
        "curly_unicode_quote_char_count_in_slice": 326,
        "straight_ascii_quote_char_count_in_slice": 0,
        "before_situation_model_decode_self_consistency": 0.8978,
        "after_situation_model_decode_self_consistency": 0.6721,
        "before_fallback_no_compatible_candidate": 80,
        "after_fallback_no_compatible_candidate": 298,
        "role_unassigned_fraction_before": 0.3143,
        "role_unassigned_fraction_after": 0.2826,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent .venv recompute pulling BOTH commit states off git (git show ba1136f1e:...ledger.json "
        "for before, current HEAD data/exp_read_anne_glassbox_v1/ledger.json for after): entities list "
        "recomputed from ledger['entities'] (37 items before with canonical_name_guess including "
        "'Avonlea' mention_count=615, name_forms={'Avonlea':11} so 615-11=604 non-name-form (pronoun/"
        "gazetteer) absorptions; 9 items after, Avonlea absent from the list). ambiguous_pronoun_"
        "resolutions/n_pronoun_mentions pulled from ledger['flagged_gaps'] and ledger['extraction_"
        "description'] respectively: before 555/639=0.8686 (~87%), after 263/693=0.3795 (~38%) -- both "
        "reproduce the commit-message claim exactly. deixis_diagnosis.n_mentions_flagged_in_quote: 0 "
        "before, 16 after (denominator 1031 independently recomputed as sum of per_chapter[c].n_mentions "
        "across ch.1-3: 316+487+228=1031, matching the '0/1031' framing exactly). consolidation.situation_"
        "model_decode_self_consistency: 0.8978 before, 0.6721 after -- reproduces the claimed 89.8%->67.2% "
        "regression exactly (this is the honest DOWNWARD number, not smoothed over)."
    ),
    "composes_seq": [29613, 29614, 29615],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_READS_USABLY - 1,
    "honest_scope": (
        "Scoped strictly to NAMED-CHARACTER identity tracking on a 3-chapter slice, NOT full "
        "comprehension and NOT pronoun-level accuracy at scale (38% of pronouns are still ambiguous "
        "after the fix -- this is coverage removal of a false-positive magnet, not a coref-accuracy "
        "win). The decode-self-consistency regression (89.8%->67.2%) is a REAL number that must be "
        "carried forward, not silently dropped in favor of the more flattering before-number -- the "
        "diagnosis (bounded max_event_slots=8 register overflow from correctly-tracked mention "
        "concentration, not a gender/coref bug) is PLAUSIBLE given the mechanism but was not "
        "independently re-derived by this audit (would require rerunning with max_event_slots swept, "
        "not done this pass) -- flagged as diagnosed-not-reproven."
    ),
    "framing_correction": (
        "The task input's framing ('tracking named characters ... with self-consistent event "
        "trajectories') OVER-STATES the current state: event-trajectory self-consistency is the metric "
        "that REGRESSED (67.2%, down from 89.8%) as an honest side effect of fixing the extraction "
        "bugs. This atom certifies the extraction/identity-tracking win (entities, contamination, "
        "ambiguous-pronoun-rate, in_quote deixis) as READS-USABLY, and separately flags the decode-"
        "self-consistency number as a REAL regression requiring its own follow-up (slot-capacity sweep), "
        "not folded into the same 'reads usably' claim uncorrected."
    ),
    "revival_criteria": (
        "Follow-up (not yet run): sweep max_event_slots upward and re-measure situation_model_decode_"
        "self_consistency on the after-fix extraction stream to confirm the slot-capacity diagnosis "
        "(would predict consistency recovering as slot count rises); if it does NOT recover, escalate "
        "back to a coref/gender-attribution bug hypothesis rather than accepting the capacity story."
    ),
    "primitive_assessment": (
        "No new primitive. Reusable lesson: when an 'extraction wall' diagnosis is made (as flagged "
        "in the 07-31 wall-broken over-read correction precedent), verify it's genuinely a DATA-quality "
        "issue (fixable with supplied lexical/gazetteer data, staying inside the no-bolt-on-parser lock) "
        "before concluding the underlying earned mechanism (coref/situation-model) is deficient -- here "
        "the mechanism was sound throughout; only the extraction DATA was the wall."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR, with an honest downward correction applied (symmetric anti-negativity): the audit "
        "surfaces and keeps the decode-self-consistency regression and the fallback-rise number "
        "in the headline rather than reporting only the ambiguous-pronoun-rate improvement, which "
        "would have been a one-sided positive-only summary."
    ),
    "cross_arc_overlap": (
        "Composes directly with 29613 (earn_coref_match_or_allocate_dense_v1), 29614 (earn_coref_"
        "pronoun_strict_cb_v1), 29615 (wire_coref_accumulate_situation_model_v1) -- this atom is the "
        "first application of those wired mechanisms to a genuinely-hard real book rather than "
        "McGuffey/synthetic gold. substrate_query.sh concept-overlap check returned cosine<=0.295 on "
        "all top hits (no dup)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_MASKING_BUGS_META = {
    "atom_id": (
        "meta::two_masking_bugs_caught_on_anne_extraction_discriminator_must_survive_scale_"
        "curly_quote_bug_hdlab_quote_spans_ascii_only_0of1031_in_quote_silenced_deixis_on_"
        "real_prose_326_curly_0_straight_fixed_plus_regression_test_pronoun_seeded_entity_"
        "none_none_wildcard_gender_never_recorded_absorbed_every_later_pronoun_masked_the_"
        "honesty_fixes_own_discriminator_0of514_vs_161of514_force_attaches_before_after_"
        "both_fixed_plus_wired_eed674401_CERT_NEUTRAL_METHODOLOGY_LOCAL_ONLY"
    ),
    "seq": SEQ_MASKING_BUGS_META,
    "op": "insert",
    "corpus": "meta",
    "tier": "CERT_NEUTRAL_METHODOLOGY",
    "cert_status": "n/a (CERT-neutral methodology atom)",
    "grade": "META",
    "verdict": (
        "Two independent MASKING bugs were caught during the Anne of Green Gables extraction/coref "
        "hardening arc, both of the same failure class: a discriminator or fix silently reads as "
        "'working' because the specific condition that would exercise it never actually fires on the "
        "test data used to validate it -- the discriminator-must-survive-scale / discriminator-must-"
        "be-telemetry-sensitive lesson (2026-07-08) recurring in a new guise (ASCII-only assumption; "
        "wildcard-default gender). Both were caught only because the fix was measured on REAL prose "
        "(curly Unicode quotes, genuinely gender-ambiguous pronoun streams) rather than synthetic/"
        "McGuffey-style ASCII-clean text, and both are now fixed + wired into the shared hdlab module "
        "(not left as local tool-only patches)."
    ),
    "anchor": "anne_masking_bugs_curly_quote_and_pronoun_seed_gender",
    "anchor_name": "anne_masking_bugs_curly_quote_and_pronoun_seed_gender_2026_08_02",
    "cell": (
        "hdlab/coreference_resolver.py (_quote_spans fix, verify_coreference_resolver.py regression "
        "test); tools/read_anne_glassbox_v2_honest_ledger.py (pronoun-seed gender fix); commits "
        "18a0341b8, 2944a14f4, eed674401"
    ),
    "headline": (
        "Bug A (curly-quote): hdlab.coreference_resolver._quote_spans matched only straight ASCII "
        "'\"', so on Anne's prose (326 curly-quote chars, 0 straight, MEASURED) enrich_dialogue's "
        "in_quote flag fired 0/1031 mentions before the fix, silently disabling speaker-deixis on ANY "
        "real-book text using typographic quotes -- would have silently passed forever on ASCII-only "
        "test/synthetic corpora. Fixed (handles curly open/close directionally + straight toggle, "
        "unchanged behavior on ASCII text) with a regression test added; full verification suite green. "
        "Bug B (pronoun-seed gender): a pronoun-seeded entity (created when no entities exist yet) "
        "never recorded the seeding pronoun's own gender/number, staying a None/None wildcard that "
        "silently absorbed every later pronoun of every gender via gn_compatible's None-is-compatible "
        "rule -- this MASKED the honesty-fix's own discriminator (measured 0/514 force-attaches "
        "flagged before this second fix, 161/514 after; the honesty fix alone, without this second fix, "
        "would have reported near-zero force-attach activity and looked like a non-issue). Fixed by "
        "recording seeding-pronoun gender/number on entity creation (same treatment name-seeded "
        "entities already got via _observe_nominal)."
    ),
    "key_metrics": {
        "bug_a_curly_quote_chars_in_slice": 326,
        "bug_a_straight_ascii_quote_chars_in_slice": 0,
        "bug_a_in_quote_flags_before_fix": 0,
        "bug_a_in_quote_flags_after_fix": 16,
        "bug_a_denominator_n_mentions": 1031,
        "bug_b_force_attaches_measured_before_fix": 0,
        "bug_b_force_attaches_measured_after_fix": 161,
        "bug_b_denominator_n_pronoun_mentions": 514,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Bug A: independently reran `python -m pytest verification/verify_coreference_resolver.py -q` "
        "in .venv (not system Python) -- 8 passed, 8 warnings (return-not-None style warnings only, no "
        "failures), confirming test_quote_spans_curly_and_straight_and_mixed and the other 7 tests are "
        "green with tracing=False, matching the commit's '8/8 tests pass' claim exactly. Cross-checked "
        "326/0 curly/straight counts and 0/1031 -> 16/1031 in_quote flags directly off ledger.json "
        "deixis_diagnosis blocks (before=git show ba1136f1e, after=current HEAD). Bug B: 0/514 -> "
        "161/514 force-attach counts read directly off data/exp_read_anne_glassbox_v2_honest_ledger/"
        "ledger.json honesty_fix block (n_force_attach_would_have_fired_under_baseline=161, "
        "n_pronoun_mentions_total=514); the '0/514' before-state is the commit-message's own reported "
        "pre-second-fix measurement, not independently re-run this pass (the buggy intermediate state "
        "was not preserved on disk as a separate commit to recompute against -- flagged in honest_scope)."
    ),
    "composes_seq": [SEQ_READS_USABLY, SEQ_CONSOLIDATION],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_MASKING_BUGS_META - 1,
    "honest_scope": (
        "Bug A's before/after in_quote counts and the 8/8 pytest rerun are independently reproduced "
        "off disk this pass. Bug B's '0/514' pre-fix number is taken from the commit message's own "
        "reported measurement (the buggy intermediate ledger state was not committed separately, so "
        "this audit could not independently re-run the buggy code path) -- the '161/514' post-fix "
        "number IS independently reproduced off the current ledger.json. This is a CERT-neutral "
        "methodology/discipline atom (bug-catching pattern), not a capability claim."
    ),
    "framing_correction": "None vs the source commits -- both bugs are described accurately and honestly there.",
    "revival_criteria": "n/a (methodology atom).",
    "primitive_assessment": (
        "Reusable discipline: an extraction/discriminator fix validated only on a narrow or synthetic "
        "test slice can be silently masked by a SECOND, independent bug that prevents the fix's own "
        "trigger condition from ever firing (Unicode-quote-blind parsing; wildcard-default gender/None-"
        "is-compatible rules). The fix for the second-order masking bug is itself required before the "
        "first fix's claimed metric can be trusted -- when a fix's activity count reads suspiciously "
        "near-zero, audit for a masking bug UPSTREAM of the discriminator before accepting the near-"
        "zero reading as 'the condition rarely occurs'."
    ),
    "hf_attribution": "n/a.",
    "fairness_verdict": (
        "FAIR: both bugs are real, both fixes are wired into the shared hdlab module (not left as "
        "local-only patches), and the verification suite (8/8, independently rerun this pass) confirms "
        "no regression to existing straight-ASCII-quote behavior."
    ),
    "cross_arc_overlap": (
        "Extends the existing 'discriminator must survive scale / must be telemetry-sensitive' "
        "discipline (2026-07-08) to a new bug shape (Unicode-quote-blindness; wildcard-default-gender "
        "masking); no prior atom captures these two specific bug instances (cosine<=0.295 on "
        "substrate_query.sh check, see composed atom 29628)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}

ATOM_CONSOLIDATION = {
    "atom_id": (
        "math::anne_coref_consolidation_ledger_honest_mode_works_ch6_9_16_v1_flag_dont_"
        "fabricate_unresolved_pronouns_it_its_136of136_correctly_flagged_zero_fabrication_"
        "false_consolidation_vs_pending_unverified_gold_20pct_11of55_salience_to_14p5pct_"
        "8of55_strict_cb_minus27pct_relative_8_flips_correct_incl_blewett_absorbed_by_marilla_"
        "5_new_overcorrections_net_win_not_clean_masculine_gender_surnamebridge_fix_0_to_"
        "22of22_he_him_clean_residual_14p5pct_all_samegender_female_to_female_the_genuine_"
        "coref_frontier_not_fabrication_promoted_wired_eed674401_verification_8of8_green_"
        "gold_UNVERIFIED_pending_director_spotcheck_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_CONSOLIDATION,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "HONEST-MODE coref consolidation (flag zero-compatible-candidate and near-tie pronouns as "
        "unresolved instead of force-attaching to most-recent/most-salient entity) WORKS as a "
        "discipline: on Anne ch.6/9/16 (the 6 candidate gold coref scenes), the it/its inanimate flag "
        "pile is 136/136 correctly flagged with zero fabricated consolidation in BOTH pick modes "
        "(salience and strict_cb), and the mechanism materially reduces false consolidation against a "
        "PENDING (gold_verified=False on all 6 scenes) evaluation set: 20.0% (11/55) under the existing "
        "salience-frequency pick rule, improving to 14.5% (8/55, -27% relative) under a resolver-pick-"
        "rule swap to literal-Centering strict_cb (hdlab._pick_strict_cb, imported unchanged) -- a net "
        "win (8 of the original 11 disagreements flip correct, including the target Blewett-she-"
        "absorbed-by-Marilla cases) but NOT a clean fix (5 new overcorrections appear elsewhere, a "
        "mirror-image recency artifact). A masculine-gender surname-bridge fix independently closed a "
        "coverage gap (Matthew's gender was previously unresolved entirely because only 'Mr. Cuthbert' "
        "is directly titled in-text, not 'Matthew'), taking he/him/his binding from unresolved to "
        "22/22 clean under strict_cb. The residual 14.5% false-consolidation is uniformly SAME-GENDER "
        "female->female mis-merge -- a real, honestly-scoped coref frontier requiring discourse/verb-"
        "level cues, not a fabrication or force-attach artifact. Both gains promoted into the shared "
        "hdlab.coreference_resolver module as an opt-in flag_unresolved param (default byte-identical "
        "to prior behavior), with 8/8 new scaffold-free verification tests passing (independently "
        "rerun this pass, tracing=False, pytest-clean)."
    ),
    "anchor": "read_anne_glassbox_v2_honest_ledger",
    "anchor_name": "anne_coref_honest_mode_consolidation_ledger_ch6_9_16",
    "cell": (
        "data/exp_read_anne_glassbox_v2_honest_ledger/{ledger.json,comparison_salience_vs_strict_cb.json}; "
        "commits 2944a14f4 -> 9a0734bf4 -> eed674401"
    ),
    "headline": (
        "Anne coref honest-mode consolidation, ch.6/9/16 (n=514 pronoun mentions, 801 total mentions): "
        "161/514 pronouns that the OLD force-attach behavior would have silently mismatched are now "
        "correctly flagged unresolved (0/514 measured before the pronoun-seed-gender fix, masking the "
        "honesty fix itself). Against the 6 PENDING-gold scenes, false-consolidation rate is 20.0% "
        "(11/55) under salience pick, 14.5% (8/55) under strict_cb pick (-27% relative, net win not "
        "clean). he/him/his binding: 19/22 (86%) salience -> 22/22 (100%) strict_cb after the "
        "masculine-gender surname-bridge fix (was fully unresolved before that fix). it/its honesty "
        "flag pile: 136/136 correctly flagged, 0 fabricated, in both pick modes. Promoted + wired into "
        "hdlab.coreference_resolver (eed674401), 8/8 verification tests independently reconfirmed green."
    ),
    "key_metrics": {
        "n_pronoun_mentions_total": 514,
        "n_mentions_total": 801,
        "n_force_attach_would_have_fired_under_baseline": 161,
        "n_low_confidence_ambiguous_flagged": 0,
        "n_consolidated_mentions": 640,
        "false_consolidation_rate_salience": 0.2,
        "false_consolidation_total_before": 11,
        "false_consolidation_rate_strict_cb": 0.14545,
        "false_consolidation_total_after": 8,
        "total_consolidated_matched_mentions": 55,
        "disagreements_flipped_correct_under_strict_cb": 8,
        "disagreements_newly_broken_under_strict_cb": 5,
        "he_him_his_n_mentions": 22,
        "he_him_his_bound_salience": 19,
        "he_him_his_bound_strict_cb": 22,
        "it_its_flagged_count_both_modes": 136,
        "decode_self_consistency_salience": 0.8193,
        "decode_self_consistency_strict_cb": 0.7667,
        "n_entities_tracked_comparison_run": 14,
        "gold_scenes_n": 6,
        "gold_verified_count": 0,
        "verification_tests_passed": 8,
        "verification_tests_total": 8,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent .venv recompute off three raw JSON files (not the commit-message summaries): "
        "(1) data/exp_read_anne_glassbox_v2_honest_ledger/ledger.json['honesty_fix'] -> "
        "n_pronoun_mentions_total=514, n_force_attach_would_have_fired_under_baseline=161, "
        "n_consolidated_mentions=640, n_mentions_total=801 -- reproduces exactly. ['false_consolidation_"
        "vs_gold'] -> overall_false_consolidation_rate=0.2, total_consolidated_matched_mentions=55, "
        "total_false_consolidations=11, note field explicitly states 'gold_verified=false on all 6 "
        "scenes ... this rate is PENDING, not certified' -- carried into this atom's honest_scope "
        "verbatim rather than dropped. (2) comparison_salience_vs_strict_cb.json -> false_consolidation_"
        "rate.salience_before=0.2, strict_cb_after=0.14545454545454545 (rounds to 14.5%), total_false_"
        "before=11, total_false_after=8, disagreements_flipped=8 entries listed, disagreements_newly_"
        "broken=5 entries listed, he_him_his_binding.salience={19 bound,3 flagged}, strict_cb={22 bound, "
        "0 flagged}, flag_pile_still_honest_check.it_its_flagged_count=136 both modes -- reproduces "
        "exactly. (3) data/eval_gold_mention_role_mcguffey_v1/gold_anne_coref_scenes_v1.jsonl -> parsed "
        "all 6 lines, gold_verified=False on every row, flags=['needs_director_verification', "
        "'novel_generalization_sanity_check'] on every row -- confirms the gold-pending framing is "
        "accurate, not softened. (4) Independently reran `python -m pytest verification/verify_"
        "coreference_resolver.py -q` in .venv: 8 passed, 0 failed (pytest-return-warning noise only), "
        "confirming eed674401's '8/8 tests pass, tracing=False, pytest-clean' claim rather than trusting "
        "the commit message alone."
    ),
    "composes_seq": [29613, 29614, 29615, SEQ_READS_USABLY],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_CONSOLIDATION - 1,
    "honest_scope": (
        "GOLD IS UNVERIFIED: all 6 candidate scenes have gold_verified=False with flags explicitly "
        "marking them 'needs_director_verification' and 'novel_generalization_sanity_check' -- the "
        "false-consolidation rates (20.0%/14.5%) are MEASURED against this pending gold and must be "
        "reported as PENDING, not certified, until a Director spot-check confirms the gold labels "
        "themselves (source commit notes ch.6 spot-checked as structurally sound by Director, but the "
        "full 6-scene set is not yet fully verified). The strict_cb pick-rule swap is a NET but NOT "
        "CLEAN win (8 flips correct, 5 new overcorrections) -- this atom does not claim strict_cb is "
        "unconditionally better, only that it trades one recency-bias failure mode for a smaller one on "
        "this sample (n=55 matched mentions is small; a materially different sample could flip the "
        "net direction). The residual false-consolidation (14.5%) is uniformly same-gender female-"
        "female mis-merge per the source commit's Director-adjudicated disagreement list -- a genuine, "
        "not-yet-solved coref frontier requiring discourse/verb-level cues beyond gender/number/salience."
    ),
    "framing_correction": (
        "Preserves (does not soften) the source commits' own honest framing: 'gold_verified=false still "
        "applies (pending Director spot-check)' and 'net win, not a clean fix' are carried forward "
        "verbatim into this atom rather than reported as a clean, certified 20%->14.5% improvement."
    ),
    "revival_criteria": (
        "Full Director gold-verification pass on all 6 scenes (only structural ch.6 spot-check done so "
        "far) before this atom's false-consolidation numbers can be promoted from MEASURED_MECHANISM "
        "(honestly-pending-gold) to a fully cert-backed claim. Same-gender female-female residual "
        "(14.5%) is the next frontier: revive as a build-now target once a discourse/verb-cue signal is "
        "identified that measurably discriminates the Blewett-vs-Marilla-class disagreements beyond "
        "recency/salience."
    ),
    "primitive_assessment": (
        "Promotes a genuinely-new resolver behavior (opt-in flag_unresolved param + pick-mode swap "
        "support) into the shared hdlab.coreference_resolver module -- reusable across future real-book "
        "reading arcs, not a one-off tool-local patch. Composes atoms 29613-29615 (the earned coref + "
        "situation-model organs) by exercising them for the first time on a genuinely-hard real book "
        "under an honesty discipline (flag-don't-fabricate) rather than the always-attach baseline."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, not an HF cell).",
    "fairness_verdict": (
        "FAIR: every headline number reproduces exactly off the raw JSON files, and the gold-pending "
        "caveat plus the 'net win, not clean' honest qualifier on strict_cb are both preserved rather "
        "than smoothed into an uncaveated improvement claim (symmetric anti-negativity applied to a "
        "measurement that could easily have been reported as a clean win)."
    ),
    "cross_arc_overlap": (
        "Composes 29613 (earn_coref_match_or_allocate_dense_v1), 29614 (earn_coref_pronoun_strict_cb_v1), "
        "29615 (wire_coref_accumulate_situation_model_v1), and this arc's own 29628 (reads-usably "
        "extraction fix) -- first real-book application + honesty-mode hardening of those wired "
        "mechanisms. substrate_query.sh concept-overlap check returned cosine<=0.295 on all top hits "
        "(no dup; genuinely novel same-gender-consolidation measurement)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}


def atomic_append_jsonl(path, record):
    line = json.dumps(record, ensure_ascii=True) + "\n"
    dir_ = os.path.dirname(path)
    with open(path, "rb") as f:
        existing = f.read()
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(existing)
            tmp.write(line.encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def verify_load(path, expect_seq=None, expect_atom_id=None):
    found = False
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            count += 1
            d = json.loads(raw.decode("utf-8"))
            if expect_seq is not None and d.get("seq") == expect_seq:
                found = True
            if expect_atom_id is not None and d.get("atom_id") == expect_atom_id:
                found = True
    return found, count


def make_ledger_entry(seq, atom, corpus, decision, note):
    now = time.time()
    return {
        "seq": seq,
        "atom_id": atom["atom_id"],
        "corpus": corpus,
        "decision": decision,
        "note": note,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now)),
        "ts_day": time.strftime("%Y-%m-%d", time.gmtime(now)),
    }


def main():
    now = time.time()
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ts_day = time.strftime("%Y-%m-%d", time.gmtime(now))

    for atom in (ATOM_DIFFICULTY, ATOM_READS_USABLY, ATOM_MASKING_BUGS_META, ATOM_CONSOLIDATION):
        atom["ts"] = now
        atom["ts_iso"] = ts_iso
        atom["ts_day"] = ts_day

    ledger_difficulty = make_ledger_entry(
        SEQ_DIFFICULTY, ATOM_DIFFICULTY, "math",
        "MEASURED_MECHANISM CERT +0 (corpus difficulty verification gate). Independent recompute off "
        "gender_coref_density_report.json/causal_adjacency_report.json/anne_of_green_gables.meta.json "
        "reproduces every cited number exactly: 38/38 chapters ge2 female-named, 34/38 ge3, mean 5.605, "
        "245/245 causal-connective gap=1 (100%, diagnosed uninformative for narrative causation), manual "
        "n=4 spot-check 3/4 non-adjacent up to 23-chapter gap. Anne is NOT harder on local syntax; "
        "difficulty is cast-density + narrative-structure, matching the curriculum-pivot's premise.",
        "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off the raw report JSONs, NOT off the "
        "verification note's own summary tables. Commit 29d8696b0. LOCAL-ONLY.",
    )
    ledger_reads_usably = make_ledger_entry(
        SEQ_READS_USABLY, ATOM_READS_USABLY, "math",
        "MEASURED_MECHANISM CERT +0 (reads-usably milestone, honestly scoped to named-character "
        "identity tracking). Independent recompute off both commit states (git show ba1136f1e vs HEAD) "
        "confirms: entities 37->9, Avonlea contamination 615(604 pronoun)->0, ambiguous-pronoun 87%->38%, "
        "in_quote flags 0/1031->16/1031. HONEST regression carried forward: situation-model decode "
        "self-consistency 89.8%->67.2% (diagnosed slot-capacity interaction, not independently re-"
        "verified this pass), fallback_no_compatible_candidate 80->298 (honest exposure not new failure).",
        "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off ledger.json before/after, NOT off "
        "commit-message claims alone. Commits ba1136f1e -> 18a0341b8. LOCAL-ONLY.",
    )
    ledger_masking_bugs = make_ledger_entry(
        SEQ_MASKING_BUGS_META, ATOM_MASKING_BUGS_META, "meta",
        "CERT-neutral methodology atom. Two masking bugs caught+fixed+wired: (A) curly-quote-blind "
        "_quote_spans (0/1031 -> 16/1031 in_quote flags, 8/8 verification tests independently rerun "
        "green); (B) pronoun-seeded-entity None/None gender wildcard masking the honesty fix's own "
        "discriminator (161/514 force-attaches independently reproduced post-fix; 0/514 pre-fix taken "
        "from commit message, buggy state not separately committed to re-run).",
        "AUDIT-ONLY (hdi_skunkworks). Commits 18a0341b8, 2944a14f4, eed674401. LOCAL-ONLY.",
    )
    ledger_consolidation = make_ledger_entry(
        SEQ_CONSOLIDATION, ATOM_CONSOLIDATION, "math",
        "MEASURED_MECHANISM CERT +0 (honest-mode consolidation ledger, GOLD PENDING/unverified). "
        "Independent recompute off ledger.json + comparison_salience_vs_strict_cb.json reproduces "
        "exactly: false-consolidation 20.0%(11/55)->14.5%(8/55) net win not clean (8 flips, 5 new "
        "overcorrections); he/him/his 19/22->22/22; it/its 136/136 both modes, zero fabrication. "
        "gold_anne_coref_scenes_v1.jsonl confirmed gold_verified=False on all 6 rows (PENDING, not "
        "softened). 8/8 verification tests independently rerun green post-promotion (eed674401).",
        "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute + independent pytest rerun, NOT off "
        "commit-message claims alone. Commits 2944a14f4 -> 9a0734bf4 -> eed674401. LOCAL-ONLY.",
    )

    # A5-gate: atomic write, math atoms first, then meta atom, then all 4 ledger entries.
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_DIFFICULTY)
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_READS_USABLY)
    atomic_append_jsonl(META_ATOMS_PATH, ATOM_MASKING_BUGS_META)
    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_CONSOLIDATION)

    atomic_append_jsonl(LEDGER_PATH, ledger_difficulty)
    atomic_append_jsonl(LEDGER_PATH, ledger_reads_usably)
    atomic_append_jsonl(LEDGER_PATH, ledger_masking_bugs)
    atomic_append_jsonl(LEDGER_PATH, ledger_consolidation)

    # Verify-load + integrity check
    results = []
    for path, seq, atom_id in (
        (MATH_ATOMS_PATH, SEQ_DIFFICULTY, ATOM_DIFFICULTY["atom_id"]),
        (MATH_ATOMS_PATH, SEQ_READS_USABLY, ATOM_READS_USABLY["atom_id"]),
        (META_ATOMS_PATH, SEQ_MASKING_BUGS_META, ATOM_MASKING_BUGS_META["atom_id"]),
        (MATH_ATOMS_PATH, SEQ_CONSOLIDATION, ATOM_CONSOLIDATION["atom_id"]),
    ):
        found, count = verify_load(path, expect_seq=seq, expect_atom_id=atom_id)
        assert found, f"FAIL: atom seq={seq} not found in {path} after write"
        results.append((path, seq, count))

    for seq in (SEQ_DIFFICULTY, SEQ_READS_USABLY, SEQ_MASKING_BUGS_META, SEQ_CONSOLIDATION):
        found, count = verify_load(LEDGER_PATH, expect_seq=seq)
        assert found, f"FAIL: ledger entry seq={seq} not found in {LEDGER_PATH} after write"

    for path, seq, count in results:
        print(f"OK: atom seq={seq} written to {path} ({count} total lines)")
    print(f"OK: 4 ledger entries written to {LEDGER_PATH}")
    print(f"atom_ids:")
    for atom in (ATOM_DIFFICULTY, ATOM_READS_USABLY, ATOM_MASKING_BUGS_META, ATOM_CONSOLIDATION):
        print(f"  seq={atom['seq']} corpus={atom['corpus']} -> {atom['atom_id'][:100]}...")


if __name__ == "__main__":
    main()
