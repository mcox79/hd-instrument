"""
A5-gated LOCAL-ONLY atomize: exp_pivot_selectional_independent_kb_2afc_v1.
tier=MEASURED_MECHANISM / proven-bound / CERT +0. Independent-KB RIGOR TEST of 29471.
Independent .venv off-disk recompute (2AFC reimplemented, thin rebuilt on real corpus,
scramble over the 10 pre-committed seeds) reproduces every headline number bit-exact.
BINARY-SAFE write (newline="") + dynamic count gate + seq continuity.
LOCAL WRITE ONLY -- no origin push, no remote persist.
"""
import json, os, time, tempfile, datetime, hashlib
os.chdir(r"D:\AI\hd-instrument")
ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate (dynamic counts; serialize-safe) ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
N_ATOMS = len(parsed)
existing_ids = {o.get("id") for o in parsed if o.get("id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"
with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
NEW_SEQ = last_seq + 1
print(f"PRE-GATE: {N_ATOMS} atoms load-valid; ledger last seq {last_seq}; NEW_SEQ={NEW_SEQ}")

# ---- off-disk recompute confirmation (re-assert numbers off metrics.json) ----
m = json.load(open("data/exp_pivot_selectional_independent_kb_2afc_v1/metrics.json", encoding="utf-8"))
assert m["verdict"] == "MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY"
assert abs(m["acc_thin"] - 0.4746) < 1e-9
assert abs(m["acc_indep_kb"] - 0.5678) < 1e-9
assert abs(m["gap_kb_vs_thin"] - 0.0932) < 1e-9
assert abs(m["acc_indep_kb_scrambled_mean"] - 0.5339) < 1e-9
assert abs(m["scramble_margin"] - 0.0339) < 1e-9
assert abs(m["acc_llm_rich"] - 0.8136) < 1e-9
assert abs(m["acc_random"] - 0.4915) < 1e-9
assert abs(m["frac_of_llm_lift_recovered"] - 0.2749) < 1e-9
assert m["baseline_in_band"] and m["random_is_chance"] and m["arms_differ_verified"] and m["cardinality_ok"]
assert m["acc_indep_kb_scrambled_all_seeds"] == [0.6864, 0.4746, 0.4576, 0.5254, 0.5593, 0.5254, 0.5085, 0.4661, 0.5678, 0.5678]
n_match_or_beat = sum(1 for a in m["acc_indep_kb_scrambled_all_seeds"] if a >= 0.5678 - 1e-9)
assert n_match_or_beat == 3, n_match_or_beat
print("OFF-DISK OK: thin=0.4746 kb=0.5678 gap=+0.0932 scr_mean=0.5339 margin=+0.0339 (3/10 perms match/beat) llm=0.8136 recov=0.2749")

cell_path = "experiments/exp_pivot_selectional_independent_kb_2afc_v1.py"
cell_sha = hashlib.sha256(open(cell_path, "rb").read()).hexdigest()[:16]

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::pivot_selectional_independent_kb_2afc_v1_MEASURED_MECHANISM_INDEPENDENT_KB_RIGOR_TEST_of_29471_"
    "swaps_ONLY_the_knowledge_SOURCE_from_LLM_self_built_rich_table_to_a_local_symbolic_ontology_VerbNet_"
    "selrestrs_plus_curated_EXAMPLE_sentences_scored_by_WordNet_wup_similarity_ZERO_corpus_attestation_"
    "LEAKAGE_IMPOSSIBLE_BY_CONSTRUCTION_build_never_opens_gold_or_mining_files_verified_by_source_result_"
    "PARTIAL_recovery_acc_thin_0p4746_to_indep_kb_0p5678_gap_plus0p0932_equals_27p5pct_of_the_LLM_lift_"
    "0p475_to_0p814_MIDDLE_BAND_knowledge_driven_IN_MEAN_only_scramble_10seed_mean_0p5339_margin_plus0p0339_"
    "clears_0p03_floor_by_only_0p0039_THIN_3of10_permutations_0p6864_0p5678_0p5678_MATCH_or_BEAT_real_std_"
    "0p064_gt_margin_HALF_the_lift_rides_on_n3_cross_class_items_thin_0p000_kb_0p833_on_the_HARD_same_class_"
    "regime_n56_lift_only_plus0p0536_kb_0p5536_vs_thin_0p5000_CONSTRUCTION_gap_INVARIANT_to_top_k_1_2_3_5_all_"
    "backoff_plus0p0932_vs_avg_plus0p0763_BOTH_MIDDLE_BAND_verdict_ROBUST_headline_construction_favorable_"
    "LEAKAGE_vs_COVERAGE_is_COVERAGE_where_KB_has_example_signal_n49_lifts_0p480_to_0p582_where_none_n10_"
    "chance_NO_HARM_does_NOT_fail_where_it_has_data_BUT_selrestrs_DONT_drive_score_example_wup_does_score_eq_"
    "example_for_all_58_dual_signal_recs_so_30of59_empty_selrestr_TRUE_but_RED_HERRING_real_coverage_limit_"
    "20_neutral_recs_9_verbs_continue_finish_forget_have_hear_meet_obey_put_say_recovery_limited_by_BOTH_"
    "sparsity_AND_proxy_weakness_where_present_majority_73pct_of_LLM_lift_NOT_reproduced_by_pure_taxonomy_"
    "bounds_leakage_question_NARROWS_not_CLEARS_informs_foundation_sourcing_LLM_built_then_KB_vetted_hybrid_"
    "over_pure_symbolic_ontology_runtime_pure_glassbox_dict_lookup_NO_LLM_composes_29471_CERT_plus0_LOCAL_"
    "ONLY_2026-07-23")
assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; CERT +0; INDEPENDENT-KB RIGOR TEST of the 29471 selectional "
    "pivot). CLAIM: swapping ONLY the knowledge source of 29471's rich-table 2AFC -- from an LLM-self-built "
    "table to a fully INDEPENDENT local symbolic ontology (VerbNet selectional restrictions + VerbNet curated "
    "EXAMPLE-sentence object nouns scored by WordNet wup_similarity; ZERO access to the gold/mining corpus, "
    "leakage-impossible BY CONSTRUCTION) -- reproduces a PARTIAL, coverage-limited fraction of the lift. On "
    "the identical 59-item set/split/thin-mechanism/2AFC scorer: acc_thin=0.4746 -> acc_indep_kb=0.5678 "
    "(gap=+0.0932) = 27.5% of the LLM's +0.339 lift (thin 0.475 -> LLM-rich 0.814). MIDDLE_BAND: knowledge-"
    "driven only IN THE MEAN -- the 10-seed scramble control mean is 0.5339 (margin +0.0339) clearing the "
    "pre-registered 0.03 floor by only +0.0039; 3 of the 10 individual value-permutations (0.6864, 0.5678, "
    "0.5678) MATCH OR BEAT the real assignment and the scramble std (0.064) EXCEEDS the margin -- a genuinely "
    "THIN anti-cheat margin (cell disclosed this honestly). The lift is also concentrated/fragile: HALF of it "
    "(2.5 of 5.5 flipped items) rides on just n=3 cross_class items where thin catastrophically scores 0.000 "
    "and KB 0.833; on the HARD same_class regime (n=56, the target) the lift is only +0.0536 (kb 0.5536 vs "
    "thin 0.5000, ~3 items). LEAKAGE-vs-COVERAGE = COVERAGE not leakage: where the KB has example signal "
    "(n=49) it lifts (thin 0.480 -> kb 0.582); where it has none (n=10 neutral 0.5) it is chance and does no "
    "harm -- it does NOT fail where it has data. Majority (73%) of the LLM advantage is NOT reproduced by the "
    "pure taxonomy -> the leakage question is NARROWED, not cleared.")

PLAIN = ("This is the honest follow-up rigor test to a prior win (cell 29471). There, an LLM wrote a table of "
    "how plausible each noun is as the object of each verb, and that table let a simple lookup pick the right "
    "object 81% of the time versus 47% for the thin knowledge the substrate had mined from a tiny corpus -- a "
    "big jump. But the LLM rated pairs for a system that is itself LLM-adjacent, so the fair worry was: did the "
    "LLM's knowledge really help, or was it a kind of self-reference? This cell answers by rebuilding the same "
    "table from a completely INDEPENDENT, inspectable, hand-built linguistic resource (VerbNet + WordNet, "
    "sitting locally, that never touched the test data), and re-running the exact same task. RESULT: the "
    "independent resource recovers only PART of the lift -- accuracy goes from 0.475 (thin) to 0.568, which is "
    "about 27% of the way to the LLM's 0.814. Is that 0.568 real? It reproduces exactly off disk, but it is "
    "FRAGILE in three honest ways: (1) the anti-cheat test -- shuffle the table's numbers and see if accuracy "
    "collapses -- only barely passes: averaged over 10 shuffles the real table beats the shuffles by +0.034, "
    "but 3 of the 10 shuffles actually TIE OR BEAT the real one, and the shuffle-to-shuffle spread (0.064) is "
    "bigger than that margin; so the signal is real on average but weak. (2) Half of the whole improvement "
    "comes from just 3 unusual items. (3) On the hard items that the task is really about, the gain is only "
    "about 3 items out of 56. IS IT LEAKAGE OR COVERAGE? Coverage. Where the resource actually has information "
    "the accuracy goes up (0.48 -> 0.58); where it has nothing it just sits at chance and does no damage -- it "
    "never fails on items it has data for. So the reading is: a pure hand-built ontology is simply too SPARSE "
    "and too COARSE to capture most of what the LLM knows, NOT that the LLM was cheating. One important "
    "correction to the cell's own story: it emphasises that VerbNet's selectional restrictions are empty for "
    "30 of the 59 verbs, but those restrictions are almost never what actually drives the score -- the real "
    "signal is WordNet similarity to VerbNet's example sentences, and only 20 pairs (9 verbs) truly fall back "
    "to no-signal. So the limit is both sparsity AND the weakness of the example-similarity proxy even where "
    "it exists. STRATEGIC TAKEAWAY for building the knowledge foundation: a pure symbolic ontology recovers "
    "only a modest slice, so the right foundation is an LLM-built-then-independently-vetted hybrid, not a pure "
    "VerbNet/WordNet construction. CITATION GUARDRAIL: do NOT cite '+0.093' as a robust independent-KB "
    "recovery -- cite it as '+0.076 to +0.093 depending on the combine rule, a MIDDLE_BAND partial recovery "
    "(~27% of the LLM lift) that is knowledge-driven only in the mean, with a thin anti-cheat margin.'")

CERT_CLASS = ("pivot_selectional_independent_kb_2afc_v1_MEASURED_MECHANISM_independent_symbolic_ontology_"
    "VerbNet_selrestrs_plus_curated_examples_WordNet_wup_recovers_PARTIAL_27p5pct_of_29471_LLM_lift_thin_"
    "0p4746_to_kb_0p5678_gap_plus0p0932_MIDDLE_BAND_scramble10seed_0p5339_margin_plus0p0339_only_plus0p0039_"
    "over_floor_3of10_perms_match_or_beat_std0p064_gt_margin_half_lift_on_n3_crossclass_thin0p000_kb0p833_"
    "same_class_n56_lift_only_plus0p0536_gap_invariant_topk_backoff_plus0p0932_vs_avg_plus0p0763_both_middle_"
    "band_verdict_robust_headline_construction_favorable_COVERAGE_not_leakage_example_signal_n49_0p480to0p582_"
    "neutral_n10_chance_no_harm_selrestr_never_drives_score_eq_example_all58_dual_recs_30of59_empty_selrestr_"
    "red_herring_real_limit_20_neutral_recs_9_verbs_sparsity_AND_proxy_weakness_majority_73pct_not_reproduced_"
    "leakage_NARROWED_not_cleared_leakage_impossible_by_construction_glassbox_dict_runtime_composes_29471_"
    "cert_plus0")

RECOMPUTE = {
    "acc_thin": 0.4746, "acc_indep_kb": 0.5678, "gap_kb_vs_thin": 0.0932,
    "acc_llm_rich": 0.8136, "frac_of_llm_lift_recovered": 0.2749, "acc_random": 0.4915,
    "scramble_mean_10seed": 0.5339, "scramble_std": 0.064, "scramble_margin": 0.0339,
    "scramble_all_seeds": [0.6864, 0.4746, 0.4576, 0.5254, 0.5593, 0.5254, 0.5085, 0.4661, 0.5678, 0.5678],
    "n_scramble_perms_match_or_beat_real": 3,
    "strat_cross_class": {"n": 3, "kb": 0.8333, "thin": 0.0000, "delta_items": 2.5},
    "strat_same_class": {"n": 56, "kb": 0.5536, "thin": 0.5000, "delta_items": 3.0, "lift_pp": 0.0536},
    "signal_has_example": {"n": 49, "kb": 0.5816, "thin": 0.4796, "delta_items": 5.0},
    "signal_both_neutral": {"n": 10, "kb": 0.5000, "thin": 0.4500, "delta_items": 0.5},
    "construction_topk_sweep_gap": {"top1": 0.0932, "top2": 0.0932, "top3_LANDED": 0.0932, "top5": 0.0932, "all": 0.0932},
    "construction_combine_gap": {"backoff_LANDED": 0.0932, "avg": 0.0763},
    "construction_combine_both_MIDDLE_BAND": True,
    "scramble_margin_alt_rules_clear_0p03": {"top1_backoff": 0.0364, "top3_backoff": 0.0339, "top5_backoff": 0.0390},
    "records_total": 117, "records_example_signal": 97, "records_selrestr_signal": 58, "records_neutral_backoff": 20,
    "records_dual_signal_score_eq_example": "58/58",
    "items_verb_empty_selrestr": "30/59", "verbs_no_selrestr": 21, "verbs_no_example": 9,
    "verbs_no_example_list": ["continue", "finish", "forget", "have", "hear", "meet", "obey", "put", "say"],
    "recompute_method": ("independent 2AFC REIMPLEMENTED (not P._2afc); items via P.build_items; KB scores loaded "
        "from independent_kb_table.json artifact; thin rebuilt via P.build_thin_gfit('full') on the real mining "
        "corpus; scramble over the same 10 pre-committed seeds. ALL headline numbers reproduce bit-exact."),
}

atom = {
    "id": AID, "name": NAME, "corpus": "math", "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet", "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("HIGH (this is the load-bearing rigor test for the foundation-ingestion pivot -- it bounds "
        "how much of 29471's LLM-self-built selectional win is reproducible from an INDEPENDENT, leakage-"
        "impossible symbolic KB). VALUE: (1) narrows (does NOT clear) the leakage question on 29471: a pure "
        "local ontology recovers ~27% of the lift, and does so as COVERAGE (lifts where it has signal, chance "
        "where it doesn't -- never fails on data it has), so the majority of the LLM's advantage is broader "
        "associative knowledge a taxonomy lacks, not self-reference. (2) Directly informs foundation sourcing: "
        "pure VerbNet/WordNet is too sparse+coarse -> an LLM-built-then-KB-vetted hybrid is indicated. LIMIT of "
        "value / CITATION GUARDRAIL: the +0.0932 headline is CONSTRUCTION-FAVORABLE (the disclosed backoff-vs-"
        "avg tuning choice moves it +0.0763 -> +0.0932; both stay MIDDLE_BAND) and FRAGILE (scramble margin "
        "+0.0339 within 1 std; 3/10 perms match/beat; half the lift on n=3 cross_class items). MUST be cited "
        "as a RANGE (+0.076..+0.093, ~27% partial recovery, knowledge-driven-in-mean), NEVER as a robust point "
        "estimate. +0 CERT (MIDDLE_BAND cell verdict; proven partial bound)."),
    "description": NAME,
    "aliases": [
        "independent VerbNet+WordNet KB recovers only ~27% of 29471's LLM selectional lift (thin 0.475 -> kb 0.568, gap +0.093)",
        "MIDDLE_BAND: knowledge-driven IN MEAN only -- scramble margin +0.034 within 1 std, 3/10 perms match/beat, thin anti-cheat",
        "leakage-vs-coverage = COVERAGE: lifts where KB has example signal (0.480->0.582 n=49), chance where none (n=10), never fails on data it has",
        "selrestrs DO NOT drive the score (score==example for all 58 dual-signal recs); 30/59 empty-selrestr is TRUE but a red herring; real limit = 20 neutral recs / 9 verbs",
        "half the lift rides on n=3 cross_class items (thin 0.000 kb 0.833); hard same_class regime lift only +0.054 (~3 of 56)",
        "verdict ROBUST to construction (top-k invariant; backoff +0.093 vs avg +0.076 both MIDDLE_BAND) but the +0.093 HEADLINE is construction-favorable -> cite as +0.076..+0.093",
        "leakage NARROWED not cleared; leakage-impossible BY CONSTRUCTION (build never reads gold/mining, verified by source); glass-box dict runtime",
        "foundation-sourcing implication: pure symbolic ontology too sparse+coarse -> LLM-built-then-KB-vetted hybrid over pure VerbNet/WordNet",
    ],
    "ts_iso": ts_iso, "ts": ts,
    "serves_capability": ("independent_symbolic_KB_partially_recovers_and_bounds_the_LLM_self_built_selectional_"
        "knowledge_win_leakage_narrowed_not_cleared_recovery_is_coverage_limited_pure_ontology_too_sparse_"
        "informs_foundation_should_be_LLM_built_then_KB_vetted_hybrid"),
    "metadata": {
        "seq": NEW_SEQ, "verdict": "MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY", "grade": "MEASURED_MECHANISM",
        "cell": cell_path, "cell_commit": "1394cf469", "cell_content_sha256_16": cell_sha,
        "metrics_path": "data/exp_pivot_selectional_independent_kb_2afc_v1/metrics.json",
        "verified_off_data": True, "composes_seq": [29471],
        "recompute": RECOMPUTE,
        "framing_correction": [
            ("CITATION GUARDRAIL (load-bearing -- this atom WILL be cited in the foundation-ingestion narrative): "
             "do NOT cite '+0.093' / '0.568' as a robust independent-KB recovery number. It reproduces exactly "
             "off disk BUT is construction-favorable (the disclosed backoff-vs-avg combine choice inflates "
             "+0.0763 -> +0.0932; both remain MIDDLE_BAND) and fragile (scramble margin +0.0339 is within 1 std "
             "0.064; 3/10 value-permutations match/beat; half the lift rides on n=3 cross_class items). Correct "
             "citation: 'a pure independent symbolic ontology recovers ~27% of the LLM lift (gap +0.076..+0.093, "
             "MIDDLE_BAND), knowledge-driven only in the mean.'"),
            ("The cell/verdict frames the 73% unrecovered gap as VerbNet selrestr SPARSITY ('empty for 30/59 "
             "verbs give/admire/build/find/hire'). The 30/59 count is TRUE (independently confirmed) but it is a "
             "RED HERRING for what drives the score: selrestr_score is essentially never used -- the backoff "
             "always prefers example_score, and score==example_score for ALL 58 records that have both signals. "
             "The actual signal is WordNet wup-similarity to VerbNet example-sentence objects. The real coverage "
             "limit is 20 neutral records / 9 verbs (continue/finish/forget/have/hear/meet/obey/put/say). AND the "
             "recovery is limited not only by sparsity but by the WEAKNESS of the example-wup proxy even where "
             "present (same_class lift only +0.054). So the honest read is 'ontology sparse AND weak-where-"
             "present', not purely 'sparse selrestrs'."),
            ("Half the +0.093 gap (2.5 of 5.5 flipped items) comes from just n=3 cross_class items where thin "
             "scores 0.000. On the HARD same_class regime (n=56 -- where the mapped ceiling actually lives) the "
             "lift is only +0.0536 (kb 0.5536 vs thin 0.5000). The recovery on the regime that matters is ~3 "
             "items, barely above chance."),
        ],
        "leakage_assessment": ("LEAKAGE-IMPOSSIBLE BY CONSTRUCTION, confirmed by source inspection: "
            "build_indep_kb_table touches ONLY nltk.corpus.verbnet + nltk.corpus.wordnet (static local corpora); "
            "it never opens gold_mcguffey_lccp_argstruct_v1.json or any mining file. The recovery pattern is "
            "COVERAGE not leakage: KB lifts where it has example signal (n=49: 0.480->0.582), is chance where it "
            "has none (n=10 neutral), and NEVER fails on items it has data for. So the majority (73%) of 29471's "
            "LLM advantage is broader associative knowledge a taxonomy lacks, not self-reference. This NARROWS "
            "the 29471 leakage question (a modest, knowledge-driven, coverage-limited fraction IS reproducible "
            "independently) but does NOT clear it the way a HARD_PASS would have."),
        "honest_scope": ("Full run, n=59 items, identical set/split/thin-mechanism/2AFC scorer as 29471 (imported "
            "verbatim). MIDDLE_BAND = a POSITIVE-but-partial mechanism with a real bound, honestly banked; NOT a "
            "clean leakage-cleared PASS and NOT a negative. Deterministic (fixed seeds). Runtime is pure "
            "glass-box dict lookup, NO LLM/network/autograd at inference (build-time uses only local nltk corpus "
            "readers)."),
        "metrics": {
            "acc_thin": 0.4746, "acc_indep_kb": 0.5678, "gap_kb_vs_thin": 0.0932,
            "acc_llm_rich": 0.8136, "acc_llm_rich_scrambled": 0.4661,
            "frac_of_llm_lift_recovered": 0.2749, "acc_random": 0.4915,
            "acc_indep_kb_scrambled_mean_10seed": 0.5339, "acc_indep_kb_scrambled_std": 0.064,
            "scramble_margin": 0.0339, "scramble_floor": 0.03,
            "scramble_all_seeds": [0.6864, 0.4746, 0.4576, 0.5254, 0.5593, 0.5254, 0.5085, 0.4661, 0.5678, 0.5678],
            "strat_acc_indep_kb": {"cross_class": 0.8333, "same_class": 0.5536},
            "strat_acc_thin": {"cross_class": 0.0, "same_class": 0.5},
            "strat_n": {"cross_class": 3, "same_class": 56},
            "coverage_curve": {"0.00": 0.4746, "0.25": 0.5, "0.50": 0.4831, "0.75": 0.5424, "1.00": 0.5678},
            "n_items": 59, "baseline_in_band": True, "random_is_chance": True,
            "arms_differ_verified": True, "cardinality_ok": True, "verdict": "MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY",
        },
        "over_reads_corrected": [
            ("DO NOT promote this to HARD_PASS or 'leakage CLEARED'. acc_indep_kb=0.568 is far below the HARD_PASS "
             "acc>=0.65 gate and the gap +0.093 is below the +0.20 gate; the pre-registered MIDDLE_BAND is the "
             "honest verdict. It NARROWS the leakage question, it does not close it."),
            ("DO NOT cite the exact +0.093 as robust. It is construction-favorable and fragile (see "
             "framing_correction #1). Cite the range +0.076..+0.093 and the ~27% partial-recovery framing."),
            ("DO NOT attribute the 73% unrecovered gap purely to VerbNet selrestr sparsity. selrestrs do not "
             "drive the score (example-wup does); the limit is sparsity AND proxy-weakness (see framing #2)."),
            ("DO NOT read this as a negative on the pivot. It is a genuine PARTIAL positive (a real, independent, "
             "leakage-impossible KB recovers a knowledge-driven-in-mean 27% of the lift) that redirects "
             "foundation sourcing toward an LLM-built-then-KB-vetted hybrid."),
        ],
        "cross_arc_overlap_check": ("substrate_query 'independent KB VerbNet WordNet selectional restriction "
            "recovers LLM lift symbolic ontology' -> top hit cosine 0.2656 (a research note), then Weil-"
            "restriction / restriction_site / a meta composition atom, all <0.27; NONE is a prior EXPERIMENT "
            "cell above the 0.30 concept-overlap threshold. CONFIRMED genuinely novel in the arc: this is the "
            "independent-KB RIGOR TEST of 29471 (its intended lineage), not a rediscovery. No July-1-style "
            "duplicate-rediscovery pattern."),
        "composes_with": [
            ("29471 (pivot_selectional_knowledge_richness_2afc_v1, MM): the LLM-self-built rich-table win "
             "(thin 0.475 -> rich 0.814, +0.339) that THIS cell rigor-tests by swapping ONLY the knowledge "
             "source to an independent symbolic ontology. 29471 is NOT superseded -- this atom AMENDS it with "
             "the independent-replication bound: ~27% of its lift is reproducible from a leakage-impossible "
             "local KB (coverage-driven), 73% is not -> its leakage question is narrowed not cleared, and the "
             "LLM's remaining advantage is broader associative knowledge a taxonomy lacks."),
        ],
        "revival_criteria": [
            ("PATH TO A STRONGER (HARD_PASS-class) INDEPENDENT RECOVERY: replace the pure taxonomic proxy with a "
             "DISTRIBUTIONAL / corpus-scale independent KB (e.g. a large-corpus selectional-preference model or "
             "a distributional thematic-fit resource) that is still leakage-independent of the test set; test "
             "whether it recovers >>27% of the lift with a robust scramble margin (>=0.10, not within-1-std)."),
            ("Validate the LLM-built-then-KB-vetted HYBRID foundation the strategic implication points to: an "
             "LLM-generated table cross-checked/pruned against VerbNet+WordNet, tested for both lift AND leakage-"
             "robustness on a held-out slice."),
            ("If re-run: report the recovery as a RANGE over the combine rule (backoff vs avg) and a per-stratum "
             "breakdown, not a single headline, given the demonstrated construction-favorability and n=3 "
             "cross_class fragility."),
        ],
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "substrate_kb_concept_overlap_check_on_schema_vet_and_atomize_USER",
            "design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
            "vet_every_base_ingredient_fair_correct_brain_faithful_USER",
            "PIVOT_build_ideal_knowledge_foundation_from_existing_tools_USER_AUTHORIZED",
        ],
        "strategic_implication": ("The foundation-ingestion pivot's leakage risk (29471's rich table was LLM-"
            "self-built) is NARROWED but not eliminated: a fully independent, leakage-impossible local symbolic "
            "ontology (VerbNet+WordNet) reproduces ~27% of the selectional lift as a coverage-driven, knowledge-"
            "driven-in-mean effect. The majority (73%) is not recoverable from pure taxonomy -> a pure symbolic-"
            "ontology foundation is too sparse and too coarse. The indicated foundation-sourcing strategy is an "
            "LLM-built-then-independently-KB-vetted HYBRID, not a pure VerbNet/WordNet construction and not an "
            "unaudited LLM table. When this result is cited, use the +0.076..+0.093 range and the coverage-not-"
            "leakage framing, never the bare +0.093."),
        "auditor": "hdi_skunkworks", "atomized_date": "2026-07-23",
        "cross_arc_overlap": "top hit note 0.2656; NO experiment cell >0.30; novel rigor-test of 29471",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE newline="") ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling in atoms.jsonl"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == N_ATOMS + 1, (len(v), N_ATOMS)
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: {N_ATOMS} -> {len(v)} atoms; new atom verified; no CRLF doubling.")

# ---- ledger entry ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "atom_id": AID, "anchor_name": "pivot_selectional_independent_kb_2afc_v1",
    "cell": cell_path, "cell_commit": "1394cf469", "cell_content_sha256_16": cell_sha,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "cert_delta": 0, "net_cert_delta": 0, "composes_seq": [29471],
    "decision": ("landed_vet_atomize MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY -> MM (proven-bound; independent-KB "
        "RIGOR TEST of the 29471 selectional pivot). Independent off-disk recompute: 2AFC REIMPLEMENTED by the "
        "auditor (not P._2afc), items via P.build_items, KB scores loaded from the landed independent_kb_table."
        "json artifact, thin rebuilt via P.build_thin_gfit('full') on the real mining corpus -- reproduces "
        "EXACTLY: acc_thin=0.4746, acc_indep_kb=0.5678, gap=+0.0932, scramble_mean(10-seed)=0.5339 margin "
        "+0.0339, acc_random=0.4915, frac_recovered=0.2749. (1) +0.093 REAL y: reproduces bit-exact. FRAGILE: "
        "scramble margin +0.0339 clears the 0.03 floor by only +0.0039, 3/10 value-permutations (0.6864/0.5678/"
        "0.5678) MATCH-OR-BEAT the real assignment, std 0.064 > margin; HALF the lift (2.5/5.5 items) rides on "
        "n=3 cross_class items (thin 0.000 kb 0.833); on the hard same_class regime (n=56) lift only +0.0536. "
        "(2) OVERFIT: the disclosed mean-of-top-3 is NOT an overfit lever -- gap is INVARIANT to top-k (1/2/3/5/"
        "all all give +0.0932 because 2AFC only ranks). The backoff-vs-avg IS a disclosed tuned choice (avg "
        "gives +0.0763) but BOTH stay MIDDLE_BAND and scramble clears 0.03 under top-1/3/5 -> VERDICT robust; "
        "the +0.093 HEADLINE is construction-favorable and must be cited as a range +0.076..+0.093. (3) LEAKAGE-"
        "vs-COVERAGE = COVERAGE: leakage-impossible BY CONSTRUCTION (build_indep_kb_table touches only nltk "
        "verbnet/wordnet, never gold/mining -- source-verified); KB lifts where it has example signal (n=49 "
        "0.480->0.582), is chance where it has none (n=10 neutral), NEVER fails on data it has. CORRECTION: the "
        "'30/59 empty selrestrs' framing is TRUE but a red herring -- selrestr never drives the score (score=="
        "example for all 58 dual-signal recs); real coverage limit is 20 neutral recs / 9 verbs, and recovery "
        "is limited by sparsity AND example-wup proxy weakness. (4) BANDS honest y: pre-registered in prereg + "
        "docstring BEFORE full (anti-cheat collapse folded into every non-FAIL band); MIDDLE_BAND not floor-"
        "hugged, not over-claimed (correctly NOT HARD_PASS: acc 0.568 << 0.65). Cross-arc overlap: top hit note "
        "0.2656, NO experiment cell >0.30 -> novel rigor-test of 29471. Grade MM (partial positive + proven "
        "coverage bound). CERT +0. Composes/amends 29471 (not superseded). LOCAL-ONLY needs orchestrator sync."),
    "note": ("INDEPENDENT-KB RIGOR TEST banked MM. Pure local symbolic ontology (VerbNet+WordNet, leakage-"
        "impossible by construction) recovers ~27% of 29471's LLM selectional lift (thin 0.475 -> kb 0.568, gap "
        "+0.093) as a COVERAGE-driven, knowledge-driven-IN-MEAN effect. FRAGILE headline: scramble margin +0.034 "
        "within 1 std, 3/10 perms match/beat, half the lift on n=3 items -> CITE AS RANGE +0.076..+0.093 not "
        "bare +0.093. Leakage NARROWED not cleared; 73% of LLM advantage not reproducible by pure taxonomy -> "
        "foundation should be LLM-built-then-KB-vetted hybrid. Composes 29471. MM not CG. LOCAL-ONLY."),
    "cross_arc_overlap": "top hit note 0.2656; NO experiment cell >0.30; novel rigor-test of 29471",
    "ts_iso": ts_iso, "ts": ts,
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
}
json.loads(json.dumps(ledger))
new_led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in new_led_line and "\n" not in new_led_line
new_ledger_text = "\n".join(ledger_lines + [new_led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_ledger_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
with open(LEDGER, "rb") as f:
    rawl = f.read()
assert b"\r\n" not in rawl, "CRLF doubling in cert_ledger.jsonl"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == last_seq, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq {last_seq} -> {NEW_SEQ}; ts matches; no CRLF.")
print("ATOM_ID_TAIL:", AID[-70:])
print("DONE. LOCAL-ONLY; no origin push; no remote persist. needs_orchestrator_store_sync=True")
