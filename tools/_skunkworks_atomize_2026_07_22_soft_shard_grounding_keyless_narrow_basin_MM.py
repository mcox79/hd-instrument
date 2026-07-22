"""
A5-gated LOCAL-ONLY atomize: exp_reader_perception_meaning_grounding_soft_shard_v1
(cell working-tree uncommitted; content sha256[:12]=ef012300bdf2).
tier=MEASURED_MECHANISM / proven-bound / CERT +0. A robust, KEYLESS, NARROW-BASIN positive.
Independent .venv per-seed off-disk recompute (aggregates reproduce bit-exact; per-seed spread
computed independently since metrics.json stores only seed-means). BINARY-SAFE write (newline="").
LOCAL WRITE ONLY -- no origin push, no remote persist. save_atoms single-banker.
"""
import json, os, time, tempfile, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29443, f"expected 29443 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("id") for o in parsed if o.get("id")}
print("PRE-GATE: 29443 atoms load-valid; last id ends ...", parsed[-1]["id"][-40:])

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
assert last_seq == 29443, f"expected ledger last seq 29443, got {last_seq}"
NEW_SEQ = 29444

assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"

COMPOSE_29438 = ("math::reader_perception_meaning_grounding_v1_MEASURED_MECHANISM_glassbox_content_aware_HOG_"
    "grounding_genuinely_USES_image_content_pixel_shuffle_sensitive_BOTH_datasets_olivetti_aware_sens_0p188_"
    "digits_0p330_gt_0p15_content_blind_raw_shuffle_INVARIANT_minus0p030_minus0p014_lt_0p12_contrast_0p218_"
    "0p344_gg_0p10_a_REAL_perception_MEANING_step_vision_analog_of_compgen_sign_flip_no_CNN_glassbox_BUT_"
    "content_aware_gives_NO_grounding_accuracy_lift_through_the_ADDITIVE_bind_store_olivetti_hog_0p232_lt_raw_"
    "0p317_aware_over_blind_minus0p085_digits_tied_plus0p008_lt_0p05_HONEST_NEGATIVE_blind_saturated_flag_"
    "FALSE_far_from_0p95_cap_same_store_same_split_ONE_variable_encoder_arms_differ_verified_distinct_digests_"
    "scramble_base_rate_control_FIRES_collapse_to_chance_all_arms_oli_scr_0p018_0p038_near_chance_0p025_dig_"
    "0p114_0p124_near_0p10_STORE_BOTTLENECK_HYPOTHESIS_SPECULATIVE_pending_sharded_probe_inversion_"
    "EMPIRICALLY_EARNED_29431_direct_LOO_hog_0p927_gt_raw_0p794_plus0p133_here_bundled_hog_0p232_lt_raw_0p317_"
    "minus0p085_SIGN_FLIP_verified_cross_atom_BUT_no_sharded_store_arm_so_additive_crosstalk_attribution_NOT_"
    "isolated_alt_confounds_unexcluded_leading_hypothesis_not_proven_mechanism_recurring_theme_additive_"
    "superposition_crosstalk_same_capacity_bottleneck_as_settling_and_compgen_29437_composes_29431_29428_"
    "CERT_plus0_LOCAL_ONLY_2026-07-22")
COMPOSE_29442 = ("math::reader_perception_meaning_grounding_sharded_v1_MEASURED_MECHANISM_per_class_SHARDED_"
    "bind_store_RECOVERS_perception_meaning_grounding_lift_lost_to_additive_crosstalk_29438_olivetti_40class_"
    "ADDITIVE_aob_minus0p085_repro_29438_EXACT_raw0p317_hog0p232_SHARDED_aob_plus0p123_raw0p823_hog0p947_"
    "recovery_delta_plus0p208_hog_shufsens0p248_raw_invariant_minus0p013_scr_collapse0p922_NO_LABEL_LEAKAGE_"
    "argmax_over_ALL_classes_test_heldout_never_bound_MECHANISM_sharded_score_reduces_to_per_class_prototype_"
    "similarity_classifier_word_bind_cancels_removes_crosstalk_lifts_BOTH_arms_the_plus0p123_is_HOG_content_"
    "residual_near_ceiling_digits_secondary_aob_plus0p074_but_shufsens_weak_0p026_GROUNDING_not_CG_cert_delta0")

# ---- off-disk recompute confirmation ----
m = json.load(open("data/exp_reader_perception_meaning_grounding_soft_shard_v1/metrics.json", encoding="utf-8"))
d = m["probe_detail_olivetti"]
assert m["verdict"] == "SOFT_SHARD_RECOVERS_GROUNDING_LIFT_STRONG"
assert d["additive_reproduced_29438"] is True and d["hard_shard_reproduced_29442"] is True
assert abs(d["additive_aware_over_blind"] - (-0.085)) < 1e-3
assert abs(d["hard_shard_aware_over_blind"] - 0.1233) < 1e-3
assert d["sparse_headline_cfg"] == "center_E4_f0p20"
assert abs(d["sparse_headline_aware_over_blind"] - 0.0933) < 1e-3
assert d["keyless_single_shot_verified"] is True and d["soft_shard_hard_pass"] is True
hl = d["sparse_headline_gates"]
assert abs(hl["aware_shuffle_sensitivity"] - 0.4717) < 1e-3 and abs(hl["blind_shuffle_sensitivity"] - 0.0033) < 1e-3
assert abs(hl["aware_scramble_collapse"] - 0.8033) < 1e-3 and hl["controls_ok"] is True
# rand E4 f0.20 genuinely fails (content-dependence required)
assert d["sparse_sweep_table"]["rand_E4_f0p20"]["aware_over_blind"] < 0
print("OFF-DISK OK: add=-0.085 hard=+0.123 soft[center_E4_f0p20]=+0.093 keyless=True controls_ok=True "
      "rand_E4_f0p20 aob<0")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::reader_perception_meaning_grounding_soft_shard_v1_MEASURED_MECHANISM_SPARSE_learned_"
    "separated_SINGLE_KEYLESS_store_soft_sharding_RECOVERS_76pct_of_hard_shard_grounding_lift_WITHOUT_"
    "routing_key_or_per_class_partition_olivetti_40class_ADDITIVE_DENSE_aob_minus0p085_repro_29438_EXACT_"
    "raw0p317_hog0p232_HARD_SHARD_aob_plus0p123_repro_29442_EXACT_raw0p823_hog0p947_SOFT_SHARD_best_"
    "center_E4_f0p20_aob_plus0p093_raw0p732_hog0p825_recovery_0p093_over_0p123_eq_75p6pct_KEYLESS_uses_"
    "EXACT_GRD_build_store_i2w_heldout_single_store_argmax_over_word_codebook_callable_identity_verified_"
    "no_routing_no_partition_test_heldout_never_bound_ROBUST_across_5_seeds_all_POSITIVE_perseed_plus0p125_"
    "0p125_0p083_0p100_0p033_min_plus0p033_std_0p034_4of5_clear_plus0p05_NOT_seed_luck_NOT_max_of_noisy_"
    "draws_MECHANISM_sparse_quasi_orthogonal_kWTA_supports_drop_off_diagonal_cross_class_crosstalk_"
    "substituting_for_partition_NARROW_BASIN_requires_LEARNED_train_mean_center_PLUS_E4_expansion_PLUS_"
    "modest_sparsity_f0p20_fixed_RANDOM_sparse_FAILS_everywhere_rand_E4_f0p20_aob_minus0p123_perseed_4of5_"
    "negative_center_monotone_rise_with_f_at_E4_minus0p268_minus0p083_plus0p015_plus0p093_center_E4_f0p10_"
    "only_plus0p015_below_bar_center_E1_no_expand_all_negative_LEARNED_not_leakage_center_eq_codes_trainmask_"
    "mean_TRAIN_only_label_free_content_use_real_hog_shufsens_0p472_raw_invariant_0p003_scr_collapse_0p803_"
    "controls_ok_secondary_digits_10class_soft_best_aob_only_plus0p032_near_null_consistent_crosstalk_scales_"
    "with_n_classes_GROUNDING_store_architecture_capacity_NOT_CG_composes_29438_29442_cert_delta0_LOCAL_ONLY_"
    "2026-07-22")

assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; ROBUST + KEYLESS positive, NARROW BASIN). CLAIM: a SPARSE, "
    "LEARNED-separated, content-dependent code in a SINGLE content-addressable store ('soft sharding') "
    "recovers ~76% of the hard-shard perception-meaning grounding lift KEYLESSLY -- with NO routing key and "
    "NO per-class partition. Olivetti 40-class (chance 0.025): additive-DENSE aob = -0.085 (reproduces atom "
    "29438 EXACT: raw 0.317 / hog 0.232), hard-SHARD aob = +0.123 (reproduces atom 29442 EXACT: raw 0.823 / "
    "hog 0.947), SOFT-SHARD best config center_E4_f0p20 aob = +0.093 (raw 0.732 / hog 0.825) = 0.093/0.123 = "
    "75.6% of the hard-shard ceiling, achieved through the EXACT GRD.build_store / GRD.i2w_heldout single-"
    "store keyless one-shot path (callable-identity verified; retrieval is q = M*code then argmax over the "
    "word codebook; test images never bound). ROBUST, not sweep-luck: independent per-seed recompute gives "
    "aob = [+0.125, +0.125, +0.083, +0.100, +0.033] -- ALL 5 seeds positive (min +0.033), 4/5 clear the "
    "+0.05 bar, std 0.034. MECHANISM: sparse quasi-orthogonal k-WTA supports drop the off-diagonal cross-"
    "class crosstalk terms that mask the hog lift in the dense store, substituting for a discrete partition. "
    "NARROW BASIN (the honest limit): recovery needs ALL THREE of learned train-mean centering + expansion "
    "(E=4) + modest sparsity (f=0.20). Fixed-RANDOM sparse FAILS everywhere (rand_E4_f0p20 aob -0.123, 4/5 "
    "seeds negative); learned-center rises monotonically with f at E4 (-0.268 -> -0.083 -> +0.015 -> +0.093); "
    "center_E4_f0p10 is only +0.015 (below the +0.05 bar); center_E1 (no expansion) is negative everywhere. "
    "Centering is label-free (train-mask mean only). SECONDARY digits (10-class): soft best aob only +0.032 "
    "(near-null) -- consistent with the mechanism (additive crosstalk scales with n_classes; the 40-class "
    "olivetti regime is where it bites). GROUNDING store-architecture capacity, NOT compositional "
    "generalization. CERT +0.")

PLAIN = ("Background: an earlier probe (atom 29438) showed that when the substrate stores many image->word "
    "associations by ADDING them all into ONE vector, the 'content-aware' HOG features stop helping -- the "
    "many overlapping memories create crosstalk that drowns out the useful signal (aob -0.085, a null). A "
    "follow-up (atom 29442) fixed this by giving EACH class its OWN separate mini-store (hard sharding), "
    "recovering the lift (+0.123) -- but that needs a routing key to know which shard to look in, which is a "
    "cost. THIS cell asks the USER's question: can you get the benefit of separation WITHOUT the separate "
    "bins -- keeping ONE store with no routing key -- just by making each memory's code SPARSE and spread out "
    "so different classes barely overlap (the brain's dentate-gyrus 'pattern separation' trick)? ANSWER: YES, "
    "partially. The best sparse code recovers about three-quarters of the hard-shard benefit (+0.093 vs "
    "+0.123) while staying in ONE keyless store -- you query it the exact same one-shot way as the dense "
    "store, no routing, no partition (verified in code). And it is a REAL effect, not a lucky sweep pick: "
    "re-running each of the 5 random seeds separately, EVERY seed is positive (+0.125, +0.125, +0.083, "
    "+0.100, +0.033), four of five clear the pass bar. HONEST LIMITS: it only works in a narrow corner of the "
    "knobs -- you need a LEARNED separation step (subtract the average training code, which is label-free), "
    "AND expand the code to a bigger space, AND keep the sparsity modest. A purely RANDOM sparse code fails "
    "everywhere (it goes negative), which confirms the codes have to be content-dependent, not random. And on "
    "the easier 10-class digits data the effect nearly vanishes (+0.032) -- because the crosstalk this fixes "
    "only gets bad when there are many classes. So: soft sharding is a genuine, keyless, mechanistically-"
    "understood way to recover most of the crosstalk-suppression benefit -- inside a narrow, learned, "
    "expansion-plus-modest-sparsity basin. This is a memory-store capacity mechanism, not a reasoning/"
    "generalization capability, so it counts as a proven mechanism (+0 to the cert chain).")

CERT_CLASS = ("reader_perception_meaning_grounding_soft_shard_v1_MEASURED_MECHANISM_sparse_learned_separated_"
    "single_keyless_store_soft_sharding_recovers_75p6pct_hard_shard_grounding_lift_no_routing_no_partition_"
    "olivetti_40class_add_dense_aob_neg0p085_repro_29438_hard_shard_aob_plus0p123_repro_29442_soft_best_"
    "center_E4_f0p20_aob_plus0p093_raw0p732_hog0p825_keyless_grd_build_store_i2w_heldout_callable_identity_"
    "robust_5seed_all_positive_perseed_0p125_0p125_0p083_0p100_0p033_min0p033_std0p034_4of5_clear_0p05_not_"
    "luck_mechanism_sparse_quasi_orthogonal_kwta_drops_offdiagonal_crosstalk_narrow_basin_needs_learned_"
    "center_plus_E4_expand_plus_modest_f0p20_rand_fails_neg0p123_center_monotone_f_at_E4_center_E4_f0p10_only_"
    "0p015_center_E1_negative_learned_not_leakage_train_mean_only_label_free_content_use_real_hog_shufsens_"
    "0p472_raw_inv_0p003_scr_collapse_0p803_digits_10class_soft_only_0p032_near_null_crosstalk_scales_"
    "nclasses_grounding_store_architecture_not_cg_composes_29438_29442_cert_delta0")

atom = {
    "id": AID,
    "name": NAME,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("MEDIUM-HIGH (robust, keyless, mechanistically-clean recovery of a store-architecture "
        "benefit; closes the soft-sharding question the USER posed). VALUE: (1) shows the hard-shard "
        "routing/partition cost is ~75% AVOIDABLE -- sparse pattern-separation in ONE keyless store recovers "
        "most of the crosstalk-suppression lift with no routing key; (2) the effect is seed-robust (5/5 "
        "positive) and mechanistically understood (sparse quasi-orthogonality drops off-diagonal crosstalk). "
        "LIMIT of value: NARROW BASIN -- needs learned-separation + expansion + modest sparsity together; "
        "fixed-random sparse fails; near-null on 10-class digits. This is a GROUNDING store-capacity "
        "mechanism, NOT compositional generalization; must NOT be propagated as a reasoning/CG win. +0 CERT."),
    "description": NAME,
    "aliases": [
        "soft-shard grounding: sparse learned-separated single KEYLESS store recovers 76% of hard-shard lift",
        "olivetti 40-class: add-dense aob -0.085 (repro 29438) / hard-shard +0.123 (repro 29442) / soft-shard +0.093",
        "ROBUST: per-seed aob [+0.125,+0.125,+0.083,+0.100,+0.033] all 5 positive, 4/5 clear +0.05, std 0.034 (not luck)",
        "NARROW BASIN: needs learned-center + E4 expand + modest f0.20; fixed-random sparse fails (-0.123); center_E1 negative",
        "keyless verified (GRD.build_store/i2w_heldout callable identity, argmax over word codebook, test never bound)",
        "learned-not-leakage: center = train-mask mean only (label-free); digits 10-class near-null +0.032 (crosstalk scales with n_classes)",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "serves_capability": ("keyless_soft_sharding_sparse_pattern_separation_in_a_single_content_addressable_"
        "store_recovers_most_of_the_hard_shard_crosstalk_suppression_grounding_lift_without_a_routing_key_or_"
        "per_class_partition_in_a_narrow_learned_separation_plus_expansion_plus_modest_sparsity_basin_"
        "grounding_store_architecture_capacity_not_compositional_generalization"),
    "metadata": {
        "provenance_quality": ("independent_venv_offdisk_recompute_PER_SEED: metrics.json stores only seed-"
            "MEANS, so the auditor independently RE-RAN olivetti per-seed (reusing the cell's VERBATIM GRD/SHD "
            "primitives + sparse code, looping the 5 seeds in auditor code) to get the per-seed spread that "
            "attacks the flagged multiple-comparisons/seed-luck risk. All aggregates reproduce bit-exact: "
            "additive mean -0.0850 (raw 0.3167/hog 0.2317), sharded mean +0.1233 (raw 0.8233/hog 0.9467), "
            "soft center_E4_f0p20 mean +0.0933 (raw 0.7317/hog 0.8250). Keyless + no-test-leakage verified by "
            "source inspection of GRD.build_store (sums over train_mask only) and GRD.i2w_heldout (q=M*code, "
            "argmax over full word codebook, no routing key/partition) and sparse_encode center (codes"
            "[train_mask].mean, label-free)."),
        "anchor": "exp_reader_perception_meaning_grounding_soft_shard_v1",
        "cell_commit": "working_tree_uncommitted_sha256_ef012300bdf2",
        "supersedes": None,
        "amends_atom_ids": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_reader_perception_meaning_grounding_soft_shard_v1/metrics.json",
        "verified_off_data": ("INDEP per-seed recompute (.venv Scripts/python; Fix #28, verify OFF DATA not "
            "verdict_msg). POSITIVE CONTROLS reproduce EXACT: additive per-seed aob [-0.200,-0.108,-0.042,"
            "-0.067,-0.008] mean -0.0850 (=29438); sharded per-seed [+0.100,+0.133,+0.125,+0.125,+0.133] mean "
            "+0.1233 std 0.0122 (=29442). WINNER center_E4_f0p20 per-seed aob [+0.125,+0.125,+0.083,+0.100,"
            "+0.033] mean +0.0933 std 0.0339 min +0.0333 -> ALL 5 seeds positive, 4/5 clear +0.05 = ROBUST, "
            "NOT one-seed luck, NOT max-of-noisy-draws. RAND counterpart rand_E4_f0p20 per-seed [+0.033,-0.142,"
            "-0.200,-0.217,-0.092] mean -0.1233 = genuinely FAILS (content-dependence required). center_E4_"
            "f0p10 per-seed [-0.033,+0.067,+0.000,+0.025,+0.017] mean +0.0150 = below +0.05 bar. Content-use "
            "real (metrics.json center_E4_f0p20): hog shuffle-sens 0.4717, raw shuffle-invariant 0.0033, hog "
            "scramble-collapse 0.8033, controls_ok=True."),
        "honest_scope": ("Full run, 5 seeds, olivetti 40-class PRIMARY (280 train / 120 test) + digits 10-class "
            "SECONDARY. 16-config sweep (2 methods {rand,center} x E {1,4} x f {0.02,0.05,0.10,0.20}). Headline "
            "= best controls-valid non-saturated config on olivetti (center_E4_f0p20). The soft-shard code is "
            "glass-box (fixed random expand + train-mean center + k-WTA; no gradient training, no external "
            "LLM). This is a POSITIVE result (recovers the lift) but a NARROW-BASIN one; it is a GROUNDING "
            "store-architecture capacity mechanism, NOT compositional generalization."),
        "metrics": {
            "dataset_primary": "olivetti_40class", "chance": 0.025, "seeds": [0, 1, 2, 3, 4], "N": 8192,
            "additive_dense_aob": -0.085, "additive_raw": 0.3167, "additive_hog": 0.2317,
            "additive_repro_29438": True, "additive_perseed_aob": [-0.200, -0.108, -0.042, -0.067, -0.008],
            "hard_shard_aob": 0.1233, "hard_shard_raw": 0.8233, "hard_shard_hog": 0.9467,
            "hard_shard_repro_29442": True, "hard_shard_perseed_aob": [0.100, 0.133, 0.125, 0.125, 0.133],
            "soft_shard_best_cfg": "center_E4_f0p20", "soft_shard_best_aob": 0.0933,
            "soft_shard_best_raw": 0.7317, "soft_shard_best_hog": 0.8250,
            "soft_shard_perseed_aob": [0.125, 0.125, 0.083, 0.100, 0.033],
            "soft_shard_perseed_mean": 0.0933, "soft_shard_perseed_std": 0.0339, "soft_shard_perseed_min": 0.0333,
            "recovery_fraction_of_hard": 0.756, "keyless_single_shot_verified": True,
            "hog_shuffle_sensitivity": 0.4717, "raw_shuffle_invariant": 0.0033, "hog_scramble_collapse": 0.8033,
            "controls_ok": True, "D_dim": 32768, "sparsity_frac": 0.20,
            "rand_E4_f0p20_aob": -0.1233, "rand_E4_f0p20_perseed_aob": [0.033, -0.142, -0.200, -0.217, -0.092],
            "center_E4_f0p10_aob": 0.015, "center_E4_monotone_f": [-0.268, -0.083, 0.015, 0.093],
            "center_E1_all_negative": True,
            "digits_10class_soft_best_aob": 0.032,
        },
        "over_reads_corrected": [
            ("DO NOT read this as compositional generalization or a reasoning win. It is a GROUNDING STORE-"
             "ARCHITECTURE capacity result: sparse pattern-separation suppresses additive cross-class crosstalk "
             "in one store. Tier is MEASURED_MECHANISM (proven-bound), CERT +0."),
            ("DO NOT drop the NARROW-BASIN caveat. The +0.093 recovery exists ONLY with learned train-mean "
             "centering + E4 expansion + modest sparsity (f=0.20) together. Fixed-RANDOM sparse fails everywhere "
             "(rand_E4_f0p20 aob -0.123, 4/5 seeds negative); center_E4_f0p10 is only +0.015 (below the +0.05 "
             "bar); center_E1 (no expansion) is negative everywhere. It is a single grid corner, not a plateau."),
            ("DO NOT overstate robustness beyond what was shown: 4/5 seeds clear +0.05 but the min seed is "
             "+0.033 (below the bar though still positive). The HARD-PASS is on the seed-AGGREGATE best-config "
             "aob (+0.093) plus all-seeds-positive -- legitimate and robust, but not every seed individually "
             "clears +0.05."),
            ("DO NOT generalize the lift beyond many-class regimes. On 10-class digits the soft best aob is only "
             "+0.032 (near-null). The mechanism (additive crosstalk) scales with n_classes, so the effect is "
             "an olivetti-40class-scale phenomenon, not a universal store win."),
            ("DO NOT read 'center' as label leakage. Centering subtracts codes[train_mask].mean() -- TRAIN-only, "
             "LABEL-FREE unsupervised decorrelation. Test items are never bound into the store; retrieval scores "
             "argmax over the full word codebook. Keyless verified by callable identity."),
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "GENUINE, credited: (1) The recovery is REAL and SEED-ROBUST -- independent per-seed recompute puts "
            "all 5 seeds positive (min +0.033), decisively defeating the flagged sweep-selection/seed-luck risk; "
            "the +0.093 is not the max of noisy draws around zero. (2) It is genuinely KEYLESS -- structurally "
            "guaranteed by running the EXACT dense single-store path (GRD.build_store/i2w_heldout, callable "
            "identity), so it cannot be hard-sharding in disguise. (3) The rand-vs-center split is systematic and "
            "mechanistically coherent (learned centering monotonically improves with f at E4; random sparse fails "
            "everywhere), which is exactly the content-dependent-codes prediction. (4) Positive controls reproduce "
            "BIT-EXACT off independent recompute (29438 add -0.085, 29442 hard +0.123), so the soft delta is "
            "measured against faithful, not strawmanned, floor and ceiling."),
        "revival_criteria": [
            ("BASIN-WIDENING: if a future variant recovers the lift at LOWER sparsity or WITHOUT the learned "
             "centering step (e.g. a content-adaptive expansion that makes fixed-random sparse work), or holds "
             "the +0.05 lift on 10-class digits, that would broaden this from a narrow corner toward a general "
             "keyless-store mechanism -> re-VET for possible upgrade."),
            ("CG BOUNDARY: this is store-capacity, not generalization. A cell that uses soft-shard separation to "
             "achieve compositional/relational generalization (not just crosstalk-suppressed grounding accuracy) "
             "on held-out structure would be a different, higher-tier claim -- not covered here."),
        ],
        "cross_arc_overlap_check": (
            "substrate_query 'sparse pattern separation soft sharding keyless single store crosstalk suppression "
            "grounding perception meaning' -> top cosine 0.333 (a WordNet gloss, irrelevant); 0.328/0.316/0.312 "
            "are the DG/sparse-coding biological PRIOR-ART NOTES the cell explicitly cites and builds on "
            "(hippocampal DG pattern separation, B2 sparse coding). NO prior EXPERIMENT atom at cosine>0.30 "
            "duplicating this soft-shard-store finding. CONFIRMED genuinely novel as the 3rd arm of the "
            "29438(additive-dense-null)/29442(hard-shard-recovery) grounding-store family -- a targeted keyless "
            "extension, not a rediscovery."),
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "multiple_comparisons_sweep_selection_luck_check_per_seed_robustness",
            "Dasgupta_Stevens_Navlakha_2017_fly_hashing_expand_then_WTA",
            "dentate_gyrus_pattern_separation_sparse_coding_5pct_active",
            "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
        ],
        "composes_with": [
            ("COMPOSES (does NOT supersede) 29438 reader_perception_meaning_grounding_v1: that atom established "
             "the additive-DENSE crosstalk NULL (aob -0.085) that this cell reproduces EXACT as its floor. THIS "
             "atom is the keyless resolution: sparse pattern-separation suppresses the same crosstalk in one "
             "store."),
            ("COMPOSES (does NOT supersede) 29442 reader_perception_meaning_grounding_sharded_v1: that atom "
             "established the hard-SHARD CEILING (aob +0.123, reproduced EXACT here) that required a routing "
             "key/per-class partition. THIS atom shows ~76% of that ceiling is recoverable KEYLESSLY via sparse "
             "codes in a single store -- dissolving most of the routing/partition cost, in a narrow basin."),
        ],
        "strategic_implication": (
            "The hard-shard grounding recovery (29442) does NOT strictly require a routing key or per-class "
            "partition: a sparse, learned-separated code in ONE keyless content-addressable store recovers ~76% "
            "of the lift, seed-robustly, by dropping off-diagonal cross-class crosstalk. The catch is a narrow "
            "basin (learned-center + expansion + modest sparsity; random sparse fails; near-null at 10 classes). "
            "This is a store-capacity mechanism, not compositional generalization -- it improves grounding "
            "ACCURACY under crosstalk, it does not confer relational/held-out-structure generalization."),
        "atomized_by": "hdi_skunkworks",
        "atomized_date": "2026-07-22",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline="" prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
dd = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=dd, suffix=".tmp")
os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

# ---- verify-load + CRLF-doubling guard ----
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling detected in atoms.jsonl after write"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29444, f"post-write expected 29444, got {len(v)}"
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} atoms (was 29443); new atom #29444 verified; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29443 -> 29444) ----
ledger = {
    "seq": NEW_SEQ,
    "op": "landed_vet_atomize",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "anchor": "exp_reader_perception_meaning_grounding_soft_shard_v1",
    "run_anchor": "reader_perception_meaning_grounding_soft_shard_v1",
    "cell_commit": "working_tree_uncommitted_sha256_ef012300bdf2",
    "supersedes_commit": None,
    "supersedes_atom_id": None,
    "amends_atom_id": None,
    "composes": [COMPOSE_29438, COMPOSE_29442],
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": AID,
    "atom_id": AID,
    "decision": ("MEASURED_MECHANISM / proven-bound (robust, keyless, NARROW-BASIN positive). Soft-sharding -- a "
        "SPARSE, LEARNED-separated code in a SINGLE keyless content-addressable store -- recovers ~76% of the "
        "hard-shard grounding lift (soft center_E4_f0p20 aob +0.093 vs hard +0.123) with NO routing key and NO "
        "per-class partition (GRD.build_store/i2w_heldout callable identity; test never bound). VET decisive "
        "check (flagged multiple-comparisons/seed-luck): independent PER-SEED recompute -> aob [+0.125,+0.125,"
        "+0.083,+0.100,+0.033], ALL 5 seeds positive (min +0.033), 4/5 clear +0.05, std 0.034 = ROBUST, not "
        "luck. Positive controls reproduce EXACT (add -0.085=29438; hard +0.123=29442). NARROW BASIN: needs "
        "learned-center + E4 expansion + modest f0.20; fixed-random sparse FAILS (rand_E4_f0p20 -0.123, 4/5 "
        "seeds negative); center_E4_f0p10 only +0.015; center_E1 negative; digits 10-class near-null +0.032 "
        "(crosstalk scales with n_classes). Learned-not-leakage: center = train-mask mean only (label-free). "
        "Content-use real (hog shufsens 0.472, raw invariant 0.003, scr collapse 0.803). GROUNDING store-"
        "architecture capacity, NOT compositional generalization. COMPOSES (not supersedes) 29438 + 29442. "
        "CERT +0. Local-only; needs orchestrator store sync."),
    "cert_delta": "+0 (MEASURED_MECHANISM proven-bound / robust keyless narrow-basin grounding-store mechanism; not chain-grade)",
    "net_cert_delta": "+0",
    "ts_iso": ts_iso,
    "ts": ts,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}
json.loads(json.dumps(ledger))
new_led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in new_led_line and "\n" not in new_led_line
new_ledger_text = "\n".join(ledger_lines + [new_led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp")
os.close(fd2)
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
assert vl[-2]["seq"] == 29443, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq 29443 -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID:", AID[:80], "...")
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
