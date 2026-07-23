"""A5-gated LOCAL-ONLY atomize: exp_depparse_transition_valency_subcat_cpu_v1 (FIXED re-run).
tier=MEASURED_MECHANISM / proven-bound / CERT +0. Cell verdict HARD_FAIL (clean substantive negative).
CLAIM: correctly-integrated (bug-fixed, dev-mode deviation) LEARNED verb-valency/subcat features do NOT
break the ~0.81 arc-eager UAS ceiling (overall tie); they help their narrow SEEN-verb target only; the
ceiling is a DISTRIBUTED/SEMANTIC limit (PP+coord+clausal attachment = 42% of error). Composes 29451, 29458.
Independent .venv off-disk recompute confirms all headline numbers AND an auditor error-breakdown recompute
(base seed-1 UAS=0.8103 bit-reproduces disk). BINARY-SAFE write (newline=''), LOCAL ONLY, git-commit after.
"""
import json, os, time, tempfile, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29459, f"expected 29459 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("id") for o in parsed if o.get("id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
assert last_seq == 29459, f"expected ledger last seq 29459, got {last_seq}"
NEW_SEQ = 29460
print("PRE-GATE: 29459 atoms load-valid; ledger last seq 29459.")

# ---- off-disk recompute confirmation (re-assert key numbers off metrics.json) ----
m = json.load(open("data/exp_depparse_transition_valency_subcat_cpu_v1/metrics.json", encoding="utf-8"))
assert m["verdict"] == "HARD_FAIL"
assert m["base_uas_mean"] == 0.8109 and m["base_uas_vals"] == [0.8103, 0.8104, 0.8119]
assert m["valency_uas_mean"] == 0.8088 and m["valency_uas_vals"] == [0.8072, 0.8107, 0.8085]
assert m["real_lift"] == -0.0021 and m["real_lift_2se_clean"] == -0.0038
assert m["shuffle_uas"] == 0.811 and m["shuffle_lift"] == 0.0001
assert m["base_verbarg_uas_mean"] == 0.8601 and m["valency_verbarg_uas_mean"] == 0.8652 and m["verbarg_lift"] == 0.0051
assert m["valency_held_verbarg_uas_mean"] == 0.8194 and m["base_held_verbarg_uas_mean"] == 0.8457
assert m["held_linearprev_baseline_mean"] == 0.1122
assert m["n_verbarg"] == 4193 and m["n_verbarg_held"] == 419 and m["n_lemma_keys"] == 6032
assert m["gate_d_positive_control_ok"] is True and m["arms_differ_base_vs_valency"] is True
# hand-recompute aggregates
_bm = round(sum([0.8103, 0.8104, 0.8119]) / 3, 4)
_vm = round(sum([0.8072, 0.8107, 0.8085]) / 3, 4)
assert _bm == 0.8109 and _vm == 0.8088 and round(_vm - _bm, 4) == -0.0021
print("OFF-DISK OK: base=0.8109 valency=0.8088 real_lift=-0.0021(2SE-clean=-0.0038) shuffle=0.8110 "
      "verbarg_lift=+0.0051 held valency=0.8194<base_held=0.8457 verdict=HARD_FAIL; aggregates re-derived.")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::depparse_transition_valency_subcat_cpu_v1_MEASURED_MECHANISM_FIXED_rerun_correctly_integrated_"
    "LEARNED_verb_valency_subcategorization_features_dev_mode_lemma_vs_POS_deviation_encoding_do_NOT_break_the_"
    "0p81_arceager_UAS_ceiling_ONE_variable_valency_feature_block_same_parser_split_3seed_BASE_0p8109_vals_"
    "0p8103_0p8104_0p8119_reproduces_cited_29451_gateD_ok_VALENCY_0p8088_vals_0p8072_0p8107_0p8085_SE_0p0008_"
    "real_lift_neg0p0021_2SE_clean_neg0p0038_overall_TIE_SHUFFLE_frame_0p8110_shuffle_lift_plus0p0001_BUG_"
    "TRULY_FIXED_not_masked_buggy_first_run_abs_mode_valency_0p7930_0p7935_0p7942_hurt_neg0p017_fixed_dev_mode_"
    "deviation_recovers_to_tie_FEATURE_ACTIVE_not_zeroed_verbarg_lift_plus0p0051_distinct_arms_differ_bit_true_"
    "shuffle_arm_0p8110_ne_valency_0p8088_so_real_frames_fire_valency_HELPS_its_TARGET_but_target_TOO_SMALL_"
    "seen_lemma_verbarg_plus0p0086_aggregate_verbarg_base_0p8601_valency_0p8652_plus0p0051_on_4193_arcs_but_"
    "backoff_does_NOT_generalize_to_unseen_verbs_heldout_valency_0p8194_LT_base_heldout_0p8457_neg0p0263_n419_"
    "floor_0p1122_trivial_DIAGNOSIS_auditor_independent_recompute_base_seed1_UAS_0p8103_bit_reproduces_disk_"
    "error_breakdown_by_gold_deprel_family_24444_dev_tokens_4637_errors_PP_nominal_mod_nmod_obl_case_18p5pct_"
    "punctuation_18p4pct_local_easy_16p2pct_clausal_acl_advcl_ccomp_xcomp_13p3pct_coordination_conj_cc_10p3pct_"
    "core_arg_valency_target_only_8p8pct_root_8p2pct_PP_plus_coord_28p8pct_PP_plus_coord_plus_clausal_semantic_"
    "attachment_42p1pct_highest_errrate_acl_0p623_parataxis_0p541_advcl_0p494_conj_0p423_all_semantic_clausal_"
    "core_arg_only_8p8pct_of_error_caps_any_perfect_valency_fix_at_plus0p017_overall_so_0p81_ceiling_is_"
    "DISTRIBUTED_SEMANTIC_limit_dominated_by_PP_attachment_coordination_clausal_that_need_semantic_world_"
    "knowledge_a_pure_syntactic_parser_lacks_motivates_INTEGRATING_MEANING_into_parsing_constraint_based_"
    "lexicalist_MacDonald_Trueswell_Kintsch_CI_the_brains_actual_architecture_SCOPE_bounds_standalone_"
    "syntactic_lexicalization_of_THIS_arceager_parser_feature_family_NOT_parsing_capped_forever_semantics_"
    "integrated_is_the_UNTESTED_path_composes_29451_baseline_reproduced_and_29458_search_bound_sibling_"
    "crossarc_overlap_only_wordnet_concept_homonyms_of_lexicalization_le_0p39_NONE_a_prior_parser_cell_"
    "targeted_extension_not_rediscovery_CERT_plus0_HARD_FAIL_cell_verdict_LOCAL_ONLY_2026-07-23")

assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; CERT +0; cell verdict HARD_FAIL = clean substantive negative). "
    "CLAIM: correctly-integrated (bug-fixed) LEARNED verb-valency/subcategorization features do NOT break the "
    "~0.81 arc-eager UAS ceiling. One variable = the valency feature block on the SAME glass-box arc-eager "
    "transition parser (29451), same UD-EWT split, 3 seeds. BASE=0.8109 (vals 0.8103/0.8104/0.8119) reproduces "
    "the cited 29451 dynamic UAS 0.8109 (Gate D positive control ok). VALENCY=0.8088 (vals 0.8072/0.8107/0.8085, "
    "SE 0.0008): real_lift=-0.0021 (2SE-clean=-0.0038) -- an OVERALL TIE (slightly negative), well below the "
    "pre-registered +0.03 HARD_PASS bar. SHUFFLED-frame control=0.8110 (shuffle_lift +0.0001). BUG TRULY FIXED "
    "(not masked): the buggy first run used ABSOLUTE-probability buckets that fired a constant attachment bias "
    "on every typical verb (valency 0.7930/0.7935/0.7942, ~-0.017 HURT); the fix (VAL_MODE=dev = lemma-vs-POS "
    "DEVIATION encoding: typical verbs contribute ~0, only atypical verbs deviate) recovers valency to a tie. "
    "The fix is NOT a zero-out -- the feature is ACTIVE: verbarg_lift=+0.0051 (distinct from base), arms differ "
    "bit-level, and the shuffle arm (0.8110) differs from the valency arm (0.8088), which it could not if the "
    "block were inert. The valency feature genuinely HELPS its TARGET but the target is too small a slice to "
    "move overall UAS: aggregate verb-argument arcs (n=4193) base 0.8601 -> valency 0.8652 (+0.0051); the "
    "seen-lemma verb-arg lift is ~+0.0086. BUT the backoff does NOT generalize to unseen verbs: held-out-verb "
    "valency=0.8194 is WORSE than base held-out 0.8457 (-0.0263, n=419) -- in dev-mode the feature returns "
    "nothing on unseen lemmas, so the different weights slightly hurt held-out. DIAGNOSIS (auditor independent "
    ".venv recompute; base seed-1 UAS=0.8103 bit-reproduces disk): dev error breakdown by gold-deprel family "
    "(24444 tokens, 4637 errors) -- PP/nominal-mod (nmod/obl/case) 18.5%, punctuation 18.4%, local-easy 16.2%, "
    "clausal (acl/advcl/ccomp/xcomp) 13.3%, coordination (conj/cc) 10.3%, core-arg (the valency target) only "
    "8.8%, root 8.2%. PP+coord=28.8%; PP+coord+clausal (semantic attachment)=42.1%. Highest per-family error "
    "rates are all semantic/clausal (acl 0.623, parataxis 0.541, advcl 0.494, conj 0.423). The valency target "
    "is only 8.8% of error, so even a PERFECT valency fix caps the overall lift at ~+0.017. Combined with the "
    "search bound (29458: more search does not break it) the ~0.81 ceiling is a DISTRIBUTED/SEMANTIC limit -- "
    "dominated by PP-attachment + coordination + clausal attachments that need semantic/world knowledge a "
    "pure-syntactic parser lacks -> motivates INTEGRATING MEANING into parsing (constraint-based lexicalist / "
    "Kintsch CI, the brain's actual architecture). SCOPE: bounds standalone-syntactic lexicalization of THIS "
    "arc-eager parser + feature family; does NOT claim parsing capped forever -- semantics-integrated parsing "
    "is the UNTESTED path.")

PLAIN = ("A dependency parser reads a sentence and draws the arrows saying which word attaches to which (who "
    "did what to whom). This one is a glass-box, brain-style incremental parser and it sits at 81% correct "
    "arrows (UAS). The question here: does teaching it about verb 'valency' -- the fact that 'eat' usually "
    "takes an object but 'sleep' does not -- push it past 81%? An earlier version of this feature had a "
    "sign/integration BUG and actually made the parser WORSE (79%). That bug was diagnosed and fixed (the fix "
    "encodes only how a specific verb DIFFERS from the average verb of its part-of-speech, so ordinary verbs "
    "add no noise). This is the fixed re-run. Result: the valency feature no longer hurts, but it does NOT "
    "help overall either -- it ties the plain parser (81.1% vs 80.9%, a wash). It DOES give a small real bump "
    "exactly where it should (attaching arguments to verbs it has seen before, +0.9%), proving the feature is "
    "genuinely active and not just switched off -- but that slice is too small to move the total, and the "
    "feature does not carry over to verbs it has never seen. The important part is the DIAGNOSIS of WHY 81% is "
    "the wall: I re-ran the parser myself and sorted its mistakes by type. The errors are spread out, and the "
    "biggest chunks are the classic HARD cases that genuinely need world/meaning knowledge, not more grammar "
    "rules: attaching prepositional phrases ('I saw the man WITH the telescope' -- who has the telescope?) is "
    "18.5% of all errors, coordination ('A and B or C') is 10.3%, and clausal attachment is 13.3% -- together "
    "42% of the mistakes. The verb-argument cases that valency targets are only 8.8% of the errors, so even a "
    "perfect valency feature could lift the total by at most ~1.7%. Punctuation (arbitrary annotation "
    "convention) is another 18.4%. The upshot: you cannot break this ceiling with more clever SYNTAX features; "
    "the remaining errors need MEANING folded into the parse (exactly how the brain does it -- constraint-based "
    "lexicalist parsing, Kintsch's construction-integration). That is the next move, and it is untested here. "
    "This banks as an honest, useful NEGATIVE with a clear diagnosis, not a failure: it tells us the lever.")

CERT_CLASS = ("depparse_transition_valency_subcat_cpu_v1_MEASURED_MECHANISM_FIXED_correctly_integrated_learned_"
    "verb_valency_features_do_not_break_0p81_arceager_uas_ceiling_overall_tie_real_lift_neg0p0021_2se_clean_"
    "neg0p0038_base_0p8109_valency_0p8088_shuffle_0p8110_bug_truly_fixed_abs_0p793_hurt_to_dev_deviation_tie_"
    "feature_active_verbarg_lift_plus0p0051_seen_lemma_plus0p0086_but_target_only_8p8pct_of_error_backoff_not_"
    "generalize_heldout_0p8194_lt_base_0p8457_diagnosis_error_breakdown_pp_18p5_punct_18p4_clausal_13p3_coord_"
    "10p3_corearg_8p8_pp_plus_coord_plus_clausal_semantic_42p1pct_ceiling_distributed_semantic_limit_motivates_"
    "constraint_based_lexicalist_kintsch_ci_composes_29451_29458_cert_plus0_hard_fail_cell_verdict")

atom = {
    "id": AID,
    "name": NAME,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("HIGH (strategic: this NEGATIVE + its diagnosis localizes the parser frontier and names the "
        "next lever). VALUE: (1) closes the standalone-syntactic-lexicalization lever -- correctly-integrated "
        "learned verb-valency features tie the base parser (real_lift -0.0021), so the ~0.81 ceiling is NOT a "
        "lexicalization gap. (2) Bug-fix VET: confirms the fix is legit (feature active, not zeroed) rather than "
        "a masked null. (3) The diagnosis (independent error breakdown) shows the ceiling is DISTRIBUTED and "
        "dominated by semantic-dependent attachment (PP 18.5% + coordination 10.3% + clausal 13.3% = 42%), while "
        "the valency target is only 8.8% of error -- so no concentrated syntactic lever remains, motivating "
        "meaning-integrated parsing (constraint-based lexicalist / Kintsch CI). +0 CERT (HARD_FAIL cell "
        "verdict; a proven bound, not a capability win)."),
    "description": NAME,
    "aliases": [
        "FIXED valency parser: learned verb-valency features do NOT break 0.81 arc-eager UAS ceiling (real_lift -0.0021, overall tie)",
        "bug truly fixed not masked: abs-mode 0.793 (HURT) -> dev-deviation-mode tie; feature ACTIVE (verbarg_lift +0.0051, shuffle 0.8110 != valency 0.8088)",
        "valency helps its TARGET only: aggregate verb-arg +0.0051 (seen-lemma +0.0086) but target is 8.8% of error; does NOT generalize to unseen verbs (held-out 0.8194 < base 0.8457)",
        "DIAGNOSIS error breakdown (auditor recompute, base seed1 0.8103 bit-repro): PP 18.5% + punct 18.4% + clausal 13.3% + coord 10.3% + core-arg(valency target) 8.8%",
        "0.81 ceiling is DISTRIBUTED/SEMANTIC: PP+coord+clausal = 42.1% of error (semantic/world-knowledge attachment a pure-syntactic parser cannot resolve)",
        "core-arg only 8.8% of error caps ANY perfect valency fix at ~+0.017 overall -- structural reason valency cannot move total UAS",
        "next lever = INTEGRATE MEANING into parsing (constraint-based lexicalist / Kintsch CI); semantics-integrated parsing is the UNTESTED path",
        "composes 29451 (base arc-eager reproduced, Gate D) + 29458 (search bound); scope = THIS parser+feature family, NOT parsing capped forever",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "serves_capability": ("learned_verb_valency_subcategorization_features_do_not_break_the_arceager_uas_ceiling_"
        "which_is_a_distributed_semantic_attachment_limit_pp_coordination_clausal_dominated_the_next_lever_is_"
        "integrating_meaning_into_parsing_constraint_based_lexicalist_kintsch_ci_not_more_syntactic_features"),
    "metadata": {
        "provenance_quality": ("independent_venv_offdisk_recompute + auditor_error_breakdown_recompute: all "
            "headline numbers re-asserted off metrics.json with .venv/Scripts/python (base=0.8109 valency=0.8088 "
            "real_lift=-0.0021 2SE-clean=-0.0038 shuffle=0.8110 verbarg_lift=+0.0051 held valency=0.8194 vs "
            "base_held=0.8457 floor=0.1122); 3-seed aggregates hand-re-derived and match to 1e-4. The DIAGNOSIS "
            "is an INDEPENDENT recompute: the auditor copied the cell's BASE parser path verbatim, trained one "
            "seed (EPOCHS=10) and decoded dev -- base seed-1 UAS=0.8103 reproduces base_uas_vals[0]=0.8103 "
            "BIT-EXACTLY (Gate D confirmed off-disk, not off verdict_msg), then bucketed all 4637 dev errors by "
            "gold deprel family. Bug-fix legitimacy confirmed by heartbeat (_heartbeat.jsonl): buggy first run "
            "valency 0.7930/0.7935/0.7942, fixed re-run 0.8072/0.8107/0.8085 -- and by source inspection of "
            "VAL_MODE='dev' (returns [] on typical/unseen lemmas, fires only on lemma-vs-POS deviation)."),
        "anchor": "exp_depparse_transition_valency_subcat_cpu_v1",
        "cell_commit": "sha256_c7edbf63b18edd91_at_repo_HEAD_6f5950d5a",
        "supersedes": None,
        "amends_atom_ids": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_depparse_transition_valency_subcat_cpu_v1/metrics.json",
        "verified_off_data": ("INDEP recompute (.venv Scripts/python; Fix #28, verify OFF DATA not verdict_msg). "
            "metrics.json off-disk: base_uas [0.8103,0.8104,0.8119] mean 0.8109 == cited 29451 (Gate D ok); "
            "valency [0.8072,0.8107,0.8085] mean 0.8088 SE 0.0008 2SE-lo 0.8071; real_lift -0.0021 (2SE-clean "
            "-0.0038); shuffle 0.8110 (lift +0.0001); verbarg base 0.8601 val 0.8652 lift +0.0051; held-out-verb "
            "val 0.8194 vs base 0.8457 (-0.0263, n_held=419) floor 0.1122; n_verbarg 4193 n_lemma_keys 6032; "
            "arms_differ True. AUDITOR ERROR-BREAKDOWN recompute (base seed1 UAS 0.8103 bit-repro): 24444 dev "
            "tokens, 4637 errors -- by gold-deprel family %of_all_err: PP_nominal_mod(nmod/obl/case) 18.5, "
            "punctuation 18.4, local_easy 16.2, clausal(acl/advcl/ccomp/xcomp/csubj/parataxis) 13.3, "
            "coordination(conj/cc) 10.3, core_arg(nsubj/obj/iobj = valency target) 8.8, root 8.2, advmod 4.0, "
            "other 2.4; top deprel error rates acl 0.623 parataxis 0.541 advcl 0.494 conj 0.423 obl 0.307 nmod "
            "0.277; PP+coord=28.8%, PP+coord+clausal=42.1%."),
        "honest_scope": ("Full run, 3 seeds, UD English-EWT, arc-eager dynamic-oracle transition parser (29451 "
            "family) with an averaged structured perceptron and hashed glass-box config features. Cell verdict "
            "HARD_FAIL = a clean SUBSTANTIVE negative (HF_STRUCTURAL_BOUND, not HF_TEST_DESIGN_FAILURE): the "
            "positive control reproduces cited 0.8109 (Gate D ok), the discriminator fired (n_verbarg=4193>0, "
            "6032 lemma keys), arms differ bit-level, and the valency feature is demonstrably ACTIVE. The bound "
            "is on STANDALONE-SYNTACTIC lexicalization of THIS parser+feature family -- it does NOT claim "
            "dependency parsing is capped forever; meaning-integrated (constraint-based lexicalist / Kintsch CI) "
            "parsing is the explicitly UNTESTED path. The 'semantic-attachment dominates' reading is a "
            "distributed one: PP alone (18.5%) roughly TIES punctuation (18.4%, a convention-dependent NOT "
            "semantic error mass), so no single semantic family exceeds ~18.5% -- the honest word is DISTRIBUTED, "
            "with the semantic-attachment families (PP+coord+clausal) summing to 42%."),
        "metrics": {
            "base_uas_mean": 0.8109, "base_uas_vals": [0.8103, 0.8104, 0.8119], "cited_base_uas": 0.8109,
            "valency_uas_mean": 0.8088, "valency_uas_vals": [0.8072, 0.8107, 0.8085], "valency_uas_se": 0.0008,
            "valency_uas_2se_lo": 0.8071, "real_lift": -0.0021, "real_lift_2se_clean": -0.0038,
            "shuffle_uas": 0.811, "shuffle_lift": 0.0001,
            "base_verbarg_uas": 0.8601, "valency_verbarg_uas": 0.8652, "verbarg_lift": 0.0051,
            "seen_lemma_verbarg_lift_derived": 0.0086,
            "held_verbarg_valency": 0.8194, "held_verbarg_base": 0.8457, "held_verbarg_delta": -0.0263,
            "held_linearprev_floor": 0.1122, "n_verbarg": 4193, "n_verbarg_held": 419, "n_lemma_keys": 6032,
            "n_train": 12329, "n_dev": 1989,
            "buggy_first_run_valency_vals": [0.7930, 0.7935, 0.7942],
            "err_breakdown_total_tokens": 24444, "err_breakdown_total_errors": 4637,
            "err_pct_PP_nominal_mod": 18.5, "err_pct_punctuation": 18.4, "err_pct_local_easy": 16.2,
            "err_pct_clausal": 13.3, "err_pct_coordination": 10.3, "err_pct_core_arg_valency_target": 8.8,
            "err_pct_root": 8.2, "err_pct_PP_plus_coord": 28.8, "err_pct_PP_coord_clausal_semantic": 42.1,
            "top_deprel_err_rate": {"acl": 0.623, "parataxis": 0.541, "advcl": 0.494, "conj": 0.423,
                "obl": 0.307, "punct": 0.285, "nmod": 0.277, "compound": 0.213, "root": 0.191, "nsubj": 0.153},
            "arms_differ": True, "gate_d_positive_control_ok": True, "n_seeds": 3, "verdict": "HARD_FAIL",
        },
        "over_reads_corrected": [
            ("DIRECTOR/CELL FRAMING CORRECTION (symmetric anti-negativity, honest DOWNWARD): the dispatch cited "
             "'held-out-verb valency=0.8194' as supporting the positive. Off-disk, this is WORSE than the base "
             "held-out 0.8457 (-0.0263, n=419): the backoff does NOT generalize to unseen verb lemmas -- in "
             "dev-mode the feature returns nothing on unseen lemmas, so the retrained weights slightly hurt "
             "held-out. The held>=floor(0.1122) pre-reg gate passes only against a TRIVIAL positional floor. "
             "The genuine positive is confined to SEEN-lemma verb-argument arcs (~+0.0086)."),
            ("DO NOT over-claim a single concentrated SEMANTIC lever. PP/nominal-mod (18.5%) roughly TIES "
             "punctuation (18.4%), which is convention/annotation-dependent, NOT semantic. The honest word is "
             "DISTRIBUTED: no single family exceeds ~18.5%. The SEMANTIC-attachment case rests on the SUM of "
             "PP+coordination+clausal = 42.1%, not on any one dominating family."),
            ("DO NOT read the overall tie as 'the feature does nothing / the fix zeroed it out'. The feature is "
             "ACTIVE: verbarg_lift=+0.0051 (distinct from base), arms differ bit-level, and the shuffle arm "
             "(0.8110) differs from the real-frame valency arm (0.8088). If the block were inert all three would "
             "collapse to base. The feature fires and carries a small real signal on its narrow target."),
            ("DO NOT read this as 'dependency parsing is capped at 0.81'. The bound is on standalone-syntactic "
             "LEXICALIZATION of THIS arc-eager parser + this feature family. Meaning-integrated parsing "
             "(constraint-based lexicalist / Kintsch construction-integration) is explicitly UNTESTED and is the "
             "named next lever."),
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "GENUINE, credited even inside a HARD_FAIL (symmetric anti-negativity): (1) the bug was TRULY fixed "
            "-- the buggy abs-mode feature that HURT (-0.017) was correctly re-engineered to a lemma-vs-POS "
            "deviation encoding that no longer harms; (2) the feature is demonstrably ACTIVE and helps its "
            "intended target (seen-lemma verb-argument attachments +~0.009), a real, correctly-localized "
            "mechanism effect; (3) the cell is a clean can-fail design (Gate D positive control reproduces "
            "0.8109, discriminator fired, anti-cheat shuffle present); (4) the auditor's independent error "
            "breakdown gives a crisp, actionable diagnosis of the ceiling. This is a HIGH-value negative: it "
            "converts 'valency didn't help' into 'the ceiling is a distributed semantic-attachment limit and the "
            "next lever is meaning-integrated parsing'."),
        "revival_criteria": [
            ("THE NAMED NEXT LEVER: integrate MEANING into the parse -- a constraint-based lexicalist / Kintsch "
             "construction-integration parser where PP-attachment / coordination / clausal attachment decisions "
             "are resolved by semantic/world-knowledge fit (selectional preference, argument-role plausibility), "
             "not syntax alone. Target the 42% of error that is semantic attachment. This is a SEPARATE cell, "
             "not a retune of the valency feature."),
            ("If pursuing valency further, gate it to RARE/unseen head lemmas where lexical features are weak "
             "(HDLAB_VAL_RAREGATE) AND make the backoff actually generalize to held-out verbs (the current "
             "dev-mode returns nothing on unseen lemmas -> held-out regressed). Bar: held-out-verb valency must "
             "BEAT base held-out (0.8457), not just the trivial positional floor."),
            ("Attack punctuation attachment (18.4% of error) separately -- it is convention-dependent, not "
             "semantic, and may yield to a dedicated punct-attachment rule; this would isolate the truly "
             "semantic residual for the meaning-integrated parser."),
        ],
        "cross_arc_overlap_check": (
            "substrate_query 'verb valency subcategorization lexicalization dependency parser feature ceiling' -> "
            "top hits are WordNet/concept-node HOMONYMS of 'lexicalization' (CN_lexicalization 0.390, wordnet "
            "lexicalization 0.373, 'Dependency verification' 0.354 = a prereg-verification note, denationalization "
            "0.334); NONE is a prior parser experiment cell above 0.30-relevance for the actual mechanism. "
            "CONFIRMED a TARGETED EXTENSION of the direct parser arc (29451 base, 29458 search bound), NOT a "
            "rediscovery -- this is the first learned-verb-valency lexicalization test on the arc-eager parser."),
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "every_negative_check_how_the_brain_does_it_proactively_USER",
            "design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
            "MacDonald_Pearlmutter_Seidenberg_1994_constraint_based_lexicalist_sentence_processing",
            "Trueswell_selectional_preference_immediate_effects_human_parsing",
            "Kintsch_construction_integration_model_comprehension",
            "Zeman_2002_COLING_subcategorization_driven_lexicalization_dependency_parsing",
        ],
        "composes_with": [
            ("29451 (depparse_transition_arceager_cpu_v1) -- the BASE arc-eager parser this reproduces exactly "
             "(ARM_BASE 0.8109 == cited dynamic UAS 0.8109, Gate D positive control, same code path)."),
            ("29458 (depparse_global_beam_earlyupdate_cpu_v1) -- the SEARCH bound sibling (global structured "
             "beam training does not break 0.81 either). Together these two atoms establish the ~0.81 ceiling is "
             "neither a SEARCH/training-regime limit (29458) nor a lexicalization/feature limit (this atom) -- "
             "it is a DISTRIBUTED SEMANTIC-attachment limit."),
        ],
        "strategic_implication": (
            "The ~0.81 arc-eager UAS ceiling is now bounded from two sides: more SEARCH does not break it (29458) "
            "and correctly-integrated learned verb-valency lexicalization does not break it (this atom). The "
            "auditor error breakdown shows WHY: the residual error is distributed and dominated by "
            "semantic-dependent attachment (PP 18.5% + coordination 10.3% + clausal 13.3% = 42%), plus "
            "convention-dependent punctuation (18.4%); the valency target (core args) is only 8.8% of error. No "
            "concentrated SYNTACTIC lever remains. The next move is to INTEGRATE MEANING into the parse -- a "
            "constraint-based lexicalist / Kintsch construction-integration architecture where PP/coordination/"
            "clausal attachment is resolved by semantic fit, the brain's actual method. This is the untested "
            "path and the highest-value direction for the reader frontier."),
        "atomized_by": "hdi_skunkworks",
        "atomized_date": "2026-07-23",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline='' prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

# ---- verify-load + CRLF-doubling guard ----
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling detected in atoms.jsonl after write"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29460, f"post-write expected 29460, got {len(v)}"
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} atoms (was 29459); new atom #29460 verified; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29459 -> 29460) ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "anchor": "exp_depparse_transition_valency_subcat_cpu_v1",
    "run_anchor": "depparse_transition_valency_subcat_cpu_v1",
    "cell_commit": "sha256_c7edbf63b18edd91_at_repo_HEAD_6f5950d5a",
    "supersedes_commit": None, "supersedes_atom_id": None, "amends_atom_id": None,
    "composes": ["29451", "29458"],
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True, "auditor": "hdi_skunkworks", "atomized_by": AID, "atom_id": AID,
    "decision": ("MEASURED_MECHANISM / proven-bound / CERT +0 (cell verdict HARD_FAIL = clean substantive "
        "negative). FIXED re-run of the learned verb-valency/subcat feature on the arc-eager parser. BASE=0.8109 "
        "reproduces cited 29451 (Gate D ok); VALENCY=0.8088 real_lift=-0.0021 (2SE-clean=-0.0038) = OVERALL TIE, "
        "below the +0.03 bar. BUG TRULY FIXED (not masked): buggy abs-mode 0.7930/0.7935/0.7942 (HURT -0.017) -> "
        "dev-mode lemma-vs-POS deviation ties; feature ACTIVE (verbarg_lift +0.0051 distinct, arms differ, "
        "shuffle 0.8110 != valency 0.8088). Valency helps its TARGET (seen-lemma verb-arg ~+0.0086; aggregate "
        "verb-arg +0.0051 on 4193 arcs) but the target is only 8.8% of error, and backoff does NOT generalize to "
        "unseen verbs (held-out valency 0.8194 < base 0.8457, -0.0263). DIAGNOSIS (auditor independent recompute, "
        "base seed1 UAS 0.8103 bit-reproduces disk; 24444 dev tokens, 4637 errors): error by gold-deprel family "
        "%of_all_err -- PP/nominal-mod 18.5, punctuation 18.4, local-easy 16.2, clausal 13.3, coordination 10.3, "
        "core-arg(valency target) 8.8, root 8.2; PP+coord=28.8%, PP+coord+clausal(semantic attachment)=42.1%. "
        "Core-arg only 8.8% of error caps any perfect valency fix at ~+0.017. Combined with 29458 (search bound), "
        "the ~0.81 ceiling is a DISTRIBUTED/SEMANTIC limit dominated by PP+coordination+clausal attachment that "
        "needs semantic/world knowledge a pure-syntactic parser lacks -> motivates INTEGRATING MEANING into "
        "parsing (constraint-based lexicalist / Kintsch CI). FRAMING CORRECTIONS: (a) held-out-verb 0.8194 is "
        "WORSE than base 0.8457, does NOT support 'positive' -- genuine positive is seen-lemma only; (b) "
        "'semantic ceiling' is DISTRIBUTED (PP 18.5% ~ punct 18.4%), rests on the 42% sum not one family. SCOPE: "
        "bounds standalone-syntactic lexicalization of THIS parser+feature family, NOT parsing capped forever "
        "(semantics-integrated is the untested path). Cross-arc: only WordNet/concept homonyms of 'lexicalization' "
        "<=0.39, NONE a prior parser cell -> targeted extension not rediscovery. Composes 29451, 29458. "
        "Local-only; needs orchestrator store sync."),
    "cert_delta": "+0 (MEASURED_MECHANISM proven-bound; HARD_FAIL cell verdict; standalone-syntactic valency lexicalization does not break the 0.81 ceiling; ceiling is distributed-semantic)",
    "net_cert_delta": "+0",
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
assert b"\r\n" not in rawl, "CRLF doubling detected in cert_ledger.jsonl after write"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == 29459, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq 29459 -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID:", AID[-70:])
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
