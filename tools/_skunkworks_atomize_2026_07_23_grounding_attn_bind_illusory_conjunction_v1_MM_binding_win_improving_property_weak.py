"""
A5-gated LOCAL-ONLY atomize: exp_grounding_attn_bind_illusory_conjunction_v1.
tier=MEASURED_MECHANISM / proven-bound / CERT +0. Strong brain-faithful binding WIN
(attention solves the Treisman illusory-conjunction problem where a fair flat baseline fails),
held at MM because the pre-registered IMPROVING-property gate (learn_rise) genuinely MISSED.
Independent .venv off-disk recompute: full-run re-executed, all headline numbers reproduce
BIT-IDENTICAL (deterministic). BINARY-SAFE write (newline="") to avoid CRLF doubling.
LOCAL WRITE ONLY -- no origin push, no remote persist.
"""
import json, os, time, tempfile, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29456, f"expected 29456 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("id") for o in parsed if o.get("id")}
print("PRE-GATE: 29456 atoms load-valid; last id tail ...", parsed[-1]["id"][-46:])
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
assert last_seq == 29456, f"expected ledger last seq 29456, got {last_seq}"
NEW_SEQ = 29457

# ---- off-disk recompute confirmation (re-assert key numbers off metrics.json) ----
m = json.load(open("data/exp_grounding_attn_bind_illusory_conjunction_v1/metrics.json", encoding="utf-8"))
g = m["gates"]
assert m["verdict"] == "MIDDLE_BAND"
assert abs(g["attn_illusory_2afc"] - 0.8145413542233952) < 1e-9
assert abs(g["flat_illusory_2afc"] - 0.5149449122366051) < 1e-9
assert abs(g["scram_illusory_2afc"] - 0.43857435102565173) < 1e-9
assert abs(g["illusory_margin"] - 0.29959644198679014) < 1e-9
assert abs(g["attn_color_of_shape"] - 0.6971077533577533) < 1e-9
assert abs(g["flat_color_of_shape"] - 0.28791208791208794) < 1e-9
assert abs(g["learn_rise"] - 0.04169489285221528) < 1e-9 and g["learn_ok"] is False
assert abs(g["label_shuffle_illusory"] - 0.4988852593210391) < 1e-9 and g["label_shuffle_collapsed"] is True
assert g["flat_in_band"] is True and g["scramble_collapsed"] is True and g["front_end_ok"] is True
assert abs(g["free_novel_conjunction"] - 1.0) < 1e-12
assert m["n_seeds"] == 3 and m["seeds"] == [7, 13, 17]
print("OFF-DISK OK: ATTN=0.8145 FLAT=0.5149 SCRAM=0.4386 margin=0.2996 learn_rise=0.0417(<0.06) "
      "label_shuffle=0.4989 front(0.782/0.887) free=1.000 verdict=MIDDLE_BAND")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::grounding_attn_bind_illusory_conjunction_v1_MEASURED_MECHANISM_brain_faithful_ATTENTION_"
    "gated_VSA_bind_SOLVES_the_TREISMAN_illusory_conjunction_binding_problem_where_a_FAIR_flat_baseline_"
    "FAILS_illusory2afc_M4_ATTN_0p815_vs_FLAT_0p515_chance_0p5_margin_plus0p300_3seed_7_13_17_bit_"
    "deterministic_FLAT_uses_SAME_per_window_kNN_classifications_only_variable_is_binding_pairing_ATTN_"
    "sumk_colork_bind_shapek_vs_FLAT_all_cross_conjunctions_cset_x_sset_color_of_shape_cleanup_ATTN_0p697_"
    "vs_FLAT_0p288_ANTICHEAT_scramble_wrong_localization_collapses_0p439_below_chance_LABELSHUFFLE_permuted_"
    "exemplar_labels_collapses_ATTN_0p499_cos0p176_front_end_is_LEARNED_from_data_front_end_nondeg_color_"
    "0p782_shape_0p887_floor0p75_BRAIN_COMPLETE_all3_components_present_and_loadbearing_parallel_independent_"
    "feature_maps_meanRGB_kNN_plus_HOG29438_kNN_serial_attention_spotlight_per_slot_plus_FHRR_bind_SCALE_"
    "sweep_attn_ill_stays_0p79to0p82_M3to6_FLAT_0p52_no_crosstalk_wall_reached_by_M6_FHRR_robust_wall_far_"
    "attn_cos_slow_decline_0p727_M3_to_0p661_M6_FREE_BY_CONSTRUCTION_novel_conjunction_1p000_UNGATED_NOT_"
    "headline_HELD_at_MM_because_IMPROVING_property_gate_MISSED_learn_rise_0p042_lt_prereg_0p06_curve_"
    "NONMONOTONIC_seed13_DROPS_0p641to0p623_kNN_exemplar_frontend_sample_efficient_near_saturated_from_"
    "n_train_1_so_learned_from_data_label_shuffle_is_SHOWN_but_improves_with_exposure_curve_is_WEAK_these_"
    "are_DIFFERENT_properties_path_to_HP_is_a_frontend_that_demonstrably_improves_a_SEPARATE_cell_NOT_a_"
    "retune_localization_idealized_objects_at_fixed_slots_segmentation_assumed_not_solved_composes_NOVEL_"
    "in_arc_crossarc_overlap_top_cosine_0p346_lexical_GO_homonyms_of_conjunction_NONE_visual_binding_test_"
    "CERT_plus0_LOCAL_ONLY_2026-07-23")

assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; strong brain-faithful binding WIN, improving-property gate "
    "genuinely missed). CLAIM: an ATTENTION spotlight + VSA (FHRR) bind SOLVES the Treisman binding problem "
    "(illusory conjunctions) in cluttered feature-sharing multi-object scenes where a FAIR pre-attentive flat "
    "baseline fails. On rendered noisy colored-shape scenes (6 colors x 6 shapes, per-instance color jitter + "
    "shape deformation + pixel noise), illusory-conjunction 2AFC at M=4 objects: ATTN=0.815 vs FLAT=0.515 "
    "(chance 0.5; margin +0.300), 3 seeds, bit-deterministic re-run. The flat baseline is FAIR (not a "
    "strawman): it uses the SAME learned per-window k-NN classifications; the ONLY variable is whether "
    "attention BINDS each object's own features (ATTN: sum_k color_k (x) shape_k) or the pre-attentive "
    "parallel maps form ALL cross-conjunctions (FLAT: sum over cset x sset -> illusory conjunctions). "
    "Color-of-shape cleanup ATTN=0.697 vs FLAT=0.288. ANTI-CHEAT scramble (attention at WRONG locations) "
    "collapses to 0.439 (below chance -- wrong bindings actively favor the illusory foil), so "
    "attention-localization is load-bearing. LABEL-SHUFFLE (permuted exemplar labels) collapses ATTN to "
    "0.499 (cos 0.176), so the front-end competence is LEARNED-FROM-DATA, not hand-installed. Front-end "
    "non-degenerate (color 0.782, shape 0.887). Brain-complete: all THREE Feature-Integration-Theory "
    "components present and load-bearing (parallel independent feature maps = mean-RGB k-NN + HOG-29438 "
    "k-NN; serial attention spotlight; FHRR bind). SCALE sweep: ATTN illusory-2AFC stays 0.79-0.82 across "
    "M=3..6 while FLAT stays ~0.52 -- no crosstalk wall reached by M=6 (FHRR robust; wall is far). HELD AT "
    "MM because the pre-registered HARD_PASS required an IMPROVING learning curve and it genuinely MISSED: "
    "learn_rise=0.042 < 0.06, and the per-seed curve is NON-MONOTONIC (seed13 DROPS 0.641->0.623). The k-NN "
    "exemplar front-end is sample-efficient and near-saturated from n_train=1, so 'learned-from-data' "
    "(label-shuffle) is demonstrated but 'improves-with-exposure' (the curve) is only weakly shown -- these "
    "are DIFFERENT properties. Novel-conjunction generalization (=1.000) is FREE-BY-CONSTRUCTION, reported "
    "un-gated, NOT the headline.")

PLAIN = ("Can a model avoid the brain's classic binding failure -- 'illusory conjunctions', where you glimpse "
    "a red circle and a blue square in a cluttered scene and mis-report a 'red square'? The brain's answer "
    "(Treisman's Feature Integration Theory) is a spotlight of ATTENTION that visits each object's location "
    "and binds THAT object's colour to THAT object's shape; without attention the colour and shape maps float "
    "free and mis-combine. This cell replicates all three brain parts fairly: independent LEARNED feature "
    "detectors (a colour detector from average pixels, a shape detector from oriented-gradient HOG features, "
    "both trained as nearest-neighbour exemplars from real rendered pixels), a serial attention spotlight, and "
    "a vector-symbolic bind. The key test is a 2-way choice: given a scene, is the TRUE pairing (red, circle) "
    "or the ILLUSORY pairing (blue, circle -- blue is present, circle is present, but that pairing was never a "
    "real object) actually in the scene? With attention the model gets 0.815; the no-attention 'flat' version "
    "-- which sees the SAME colours and shapes but doesn't pair them -- sits at chance 0.515. That is the win, "
    "and it is fair (only the binding step differs) and robust (holds from 3 to 6 objects; the vector algebra "
    "does not break down). Two controls prove it is real: pointing attention at the WRONG locations collapses "
    "it to 0.439, and scrambling the detector's training labels collapses it to 0.499 -- so the competence is "
    "genuinely learned and genuinely needs correct localization. WHY IT IS NOT A FULL PASS: the USER asked to "
    "demonstrate the substrate's FLEXIBLE / IMPROVING property via a learning curve -- does the model get "
    "better as it sees MORE training examples? It barely does (rise +0.042, below the pre-registered +0.06, "
    "and on one of three seeds it actually gets slightly WORSE). The nearest-neighbour front-end is so "
    "sample-efficient that it is already near its ceiling after a single example, so the curve is flat. "
    "'Learned from data' (proven by the label-shuffle collapse) and 'improves with exposure' (the curve) are "
    "different claims; the first is shown, the second is not. So this banks as a solid, honest MIDDLE result: "
    "a real, fair, brain-complete binding win, with the improving-property left for a separate experiment "
    "using a front-end that demonstrably learns gradually (not a retune of this one).")

CERT_CLASS = ("grounding_attn_bind_illusory_conjunction_v1_MEASURED_MECHANISM_attention_gated_vsa_bind_solves_"
    "treisman_illusory_conjunction_ATTN_0p815_vs_FAIR_FLAT_0p515_chance0p5_margin_plus0p300_same_perwindow_"
    "knn_classifications_only_variable_is_binding_pairing_color_of_shape_0p697_vs_0p288_scramble_collapse_"
    "0p439_labelshuffle_collapse_0p499_frontend_learned_color0p782_shape0p887_brain_complete_3components_"
    "parallel_maps_meanRGB_plus_HOG29438_serial_spotlight_FHRR_bind_scale_M3to6_attn_0p79to0p82_flat_0p52_"
    "no_crosstalk_wall_by_M6_free_by_construction_1p000_ungated_HELD_MM_improving_gate_missed_learn_rise_"
    "0p042_lt_0p06_curve_nonmonotonic_seed13_drops_knn_sample_efficient_near_saturated_learned_shown_"
    "improves_weak_localization_idealized_fixed_slots_novel_in_arc_NOT_chain_grade_cert_plus0")

atom = {
    "id": AID,
    "name": NAME,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("MEDIUM-HIGH (strong, fair, brain-complete binding WIN; a proven mechanism with a clean "
        "characterized bound). VALUE: (1) demonstrates that an attention spotlight + VSA bind replicates the "
        "brain's solution to the Treisman binding problem -- avoids illusory conjunctions in feature-sharing "
        "scenes where a FAIR pre-attentive flat baseline (same per-window classifications, no pairing) sits at "
        "chance; margin +0.300, 3 seeds, bit-deterministic. (2) Two must-fail controls fire (scramble 0.439, "
        "label-shuffle 0.499), so the win is attention-localization + learned front-end, NOT algebra alone. "
        "(3) Robust across M=3..6 (FHRR crosstalk wall not reached). LIMIT of value: the pre-registered "
        "IMPROVING-property (learning curve) MISSED (learn_rise 0.042 < 0.06, non-monotonic across seeds) -- "
        "so this must NOT be propagated as a HARD_PASS or as 'the flexible/improving property is demonstrated'. "
        "+0 CERT (non-win; MIDDLE_BAND cell verdict)."),
    "description": NAME,
    "aliases": [
        "attention-gated VSA bind solves Treisman illusory conjunction: ATTN 0.815 vs FAIR FLAT 0.515 (chance 0.5, +0.300)",
        "FLAT is fair: SAME per-window k-NN classifications, only variable = binding pairing (ATTN sum_k c_k(x)s_k vs FLAT cset x sset)",
        "controls fire: scramble->0.439 (localization load-bearing), label-shuffle->0.499 (front-end learned-from-data)",
        "brain-complete: parallel maps (meanRGB k-NN + HOG29438 k-NN) + serial spotlight + FHRR bind, all load-bearing",
        "robust M=3..6 (attn 0.79-0.82, flat ~0.52); no crosstalk wall by M=6 (FHRR); wall is far",
        "HELD at MM: improving-property gate MISSED (learn_rise 0.042 < 0.06, seed13 drops); k-NN sample-efficient/near-saturated",
        "novel-conjunction=1.000 is FREE-BY-CONSTRUCTION, reported un-gated, NOT headline (no leak into verdict)",
        "path to HP = a front-end that demonstrably IMPROVES with exposure (separate clean cell), not a retune of this one",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "serves_capability": ("attention_gated_vsa_binding_solves_the_multi_object_feature_binding_illusory_"
        "conjunction_problem_where_a_fair_preattentive_flat_baseline_fails_brain_faithful_FIT_replication_"
        "attention_localization_and_learned_frontend_both_load_bearing_improving_with_exposure_property_"
        "remains_weakly_shown_and_is_the_open_path_to_a_hard_pass"),
    "metadata": {
        "provenance_quality": ("independent_venv_offdisk_recompute: the FULL run was re-executed by the auditor "
            "with .venv/Scripts/python (deterministic fixed-seed cell); ALL headline numbers reproduce "
            "BIT-IDENTICAL to metrics.json -- ATTN@M4=0.815 FLAT=0.515 SCRAM=0.439 margin=0.300, color-of-shape "
            "ATTN=0.697 FLAT=0.288, learn_rise=0.042, label_shuffle=0.499, front-end color=0.782 shape=0.887, "
            "free_novel_conjunction=1.000, per-seed curves match. Aggregates independently recomputed from "
            "per_seed by hand and match gates to 1e-9. Arm fairness confirmed by SOURCE inspection of "
            "encode_scene: ATTN and FLAT and SCRAM all consume the SAME `preds` (per-window k-NN "
            "classifications); the ONLY difference is the binding structure (paired vs full cross-product vs "
            "deranged pairing). free_novel_conjunction appears only in gates, NOT in any verdict branch."),
        "anchor": "exp_grounding_attn_bind_illusory_conjunction_v1",
        "cell_commit": "UNCOMMITTED_sha256_a57b99652fe842e3_at_repo_HEAD_524baa8b2",
        "supersedes": None,
        "amends_atom_ids": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_grounding_attn_bind_illusory_conjunction_v1/metrics.json",
        "verified_off_data": ("INDEP recompute (.venv Scripts/python; Fix #28, verify OFF DATA not verdict_msg). "
            "Full-run re-executed: seed7 ATTN@M4=0.843 FLAT=0.528 SCRAM=0.451 shuf=0.566; seed13 0.811/0.541/"
            "0.443 shuf=0.479; seed17 0.790/0.476/0.422 shuf=0.451 -- aggregate ATTN=0.8145 FLAT=0.5149 "
            "SCRAM=0.4386 margin=0.2996 (bit-identical to disk). learn_rise=0.0417 (<0.06); per-seed "
            "color-of-shape curve NON-MONOTONIC (seed7 0.630->0.730 rise; seed13 0.641->0.623 DROP; seed17 "
            "0.606->0.650 mild). label_shuffle aggregate=0.4989 cos=0.176 (collapse). front-end color=0.782 "
            "shape=0.887. scale attn_ill by M {2:0.0(illusory_n=0 non-measurement), 3:0.795, 4:0.815, 6:0.788}; "
            "flat_ill {3:0.532,4:0.515,6:0.520}; attn_cos declines 0.727(M3)->0.697(M4)->0.661(M6). "
            "discriminator_selftest ok=True. 3 seeds [7,13,17], N=1024."),
        "honest_scope": ("Full run, 3 seeds, rendered synthetic colored-shape scenes (real pixels with noise/"
            "jitter/deformation, NOT one-hots). The 'attention spotlight' is IDEALIZED: objects sit at fixed, "
            "known SLOT positions so windows are pre-segmented -- the model does NOT have to SEARCH for object "
            "locations in clutter; spatial individuation/segmentation is ASSUMED, not solved. The claim tested "
            "is the binding half (given correct per-object feature reads, does binding avoid cross-"
            "conjunctions), which is genuinely won. This is a MIDDLE_BAND cell verdict = a POSITIVE mechanism "
            "with a real bound (the improving-property gate), NOT 'the substrate cannot bind'."),
        "metrics": {
            "attn_illusory_2afc_M4": 0.8145413542233952, "flat_illusory_2afc_M4": 0.5149449122366051,
            "scram_illusory_2afc_M4": 0.43857435102565173, "illusory_margin_M4": 0.29959644198679014,
            "attn_color_of_shape_M4": 0.6971077533577533, "flat_color_of_shape_M4": 0.28791208791208794,
            "learn_rise": 0.04169489285221528, "learn_rise_gate": 0.06, "learn_ok": False,
            "curve_cos_lo": 0.6257077150556343, "curve_cos_hi": 0.6674026079078496,
            "curve_ill_lo": 0.7628787878787878, "curve_ill_hi": 0.7941903746949618,
            "label_shuffle_illusory": 0.4988852593210391, "label_shuffle_cos": 0.176329185520362,
            "label_shuffle_collapsed": True, "front_color_acc": 0.7822222222222223,
            "front_shape_acc": 0.8866666666666667, "front_end_ok": True,
            "flat_in_band": True, "scramble_collapsed": True, "free_novel_conjunction": 1.0,
            "scale_attn_ill": {"2": 0.0, "3": 0.7945362708354317, "4": 0.8145413542233952, "6": 0.7883267607582676},
            "scale_flat_ill": {"2": 0.0, "3": 0.5320484853946562, "4": 0.5149449122366051, "6": 0.519728102947281},
            "scale_attn_cos": {"2": 0.7182815255731922, "3": 0.7268048003272524, "4": 0.6971077533577533, "6": 0.6605176284049173},
            "n_seeds": 3, "seeds": [7, 13, 17], "N_DIM": 1024, "M_primary": 4, "verdict": "MIDDLE_BAND",
        },
        "over_reads_corrected": [
            ("DO NOT flip this to HARD_PASS by arguing label-shuffle subsumes the learning curve. Those are "
             "DIFFERENT properties: label-shuffle proves the front-end is LEARNED-FROM-DATA (destroying the "
             "labels collapses it); the learning curve tests whether it IMPROVES-WITH-EXPOSURE. The USER "
             "explicitly mandated the improving property via the curve, and the curve MISSED (learn_rise 0.042 "
             "< 0.06, non-monotonic; seed13 drops). Collapsing the two is goalpost-moving. MIDDLE_BAND stands."),
            ("DO NOT report novel-conjunction=1.000 as a capability result. It is FREE-BY-CONSTRUCTION (a single "
             "bound pair is always recoverable), reported un-gated, and it enters NO verdict branch. The "
             "headline rests ONLY on the non-free illusory-conjunction avoidance in feature-sharing scenes."),
            ("DO NOT read the flat baseline as a strawman. It is a FAIR pre-attentive failure mode: it consumes "
             "the SAME per-window k-NN classifications as ATTN; the only variable is whether attention binds "
             "each object's features (paired) or the parallel maps form all cross-conjunctions. One variable."),
            ("DO NOT read this as having solved the FULL binding problem. Object localization is IDEALIZED "
             "(fixed known slots; windows pre-segmented). The spatial-individuation / search-in-clutter half of "
             "Treisman's problem is ASSUMED. The tested-and-won half is feature-binding given correct reads."),
            ("DO NOT read the M=2 scale entry (attn_ill=0.0) as a failure. At M=2 there are no valid illusory "
             "probes (illusory_n=0); 0.0 is a non-measurement placeholder, not a score. The wall is NOT reached "
             "at any tested M<=6 (attn stays 0.79-0.82, flat ~0.52); the crosstalk wall is genuinely far."),
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "GENUINE, credited (symmetric anti-negativity -- this is a real WIN held honestly at MM, not a "
            "deflated negative): (1) A brain-faithful, FAIR, one-variable demonstration that attention-gated "
            "VSA binding SOLVES the Treisman illusory-conjunction problem where a fair flat baseline sits at "
            "chance -- margin +0.300, 3 seeds, bit-deterministic. (2) All THREE Feature-Integration-Theory "
            "components are present AND load-bearing (both must-fail controls fire: scramble 0.439, label-shuffle "
            "0.499). (3) The result is robust across scale (M=3..6, FHRR crosstalk wall not reached). (4) The "
            "design is a clean can-fail cell: the flat baseline genuinely could have matched ATTN and did not; "
            "the controls genuinely could have failed to collapse and did. This is a strong grounding-binding "
            "result; ONLY the improving-with-exposure property is weakly shown, which is what holds it at MM."),
        "revival_criteria": [
            ("THE PATH TO HARD_PASS: demonstrate the IMPROVING-with-exposure property with a front-end that is "
             "NOT already sample-saturated -- e.g. a slower-learning detector (prototype/parametric or a "
             "capacity-limited exemplar set on a harder appearance manifold) whose downstream illusory-2AFC "
             "shows a monotonic rise >= +0.06 across the exemplar-count curve on >=3 seeds. This is a SEPARATE "
             "clean experiment, NOT a retune of this cell (retuning noise thresholds to force a rise would be "
             "gaming the gate)."),
            ("Locate the crosstalk wall: extend the M-sweep beyond 6 (M in {8,12,16,...}) until ATTN "
             "illusory-2AFC degrades toward FLAT; report the M at which illusory conjunctions win -> would "
             "characterize the FHRR capacity envelope for multi-object binding (currently: wall not reached "
             "by M=6, attn_cos slowly declining 0.727->0.661)."),
            ("Remove the idealized-localization assumption: an attention mechanism that must SEARCH for / "
             "segment object locations in clutter (not fixed slots) would test the spatial-individuation half "
             "of the binding problem currently assumed."),
        ],
        "cross_arc_overlap_check": (
            "substrate_query 'attention spotlight binding illusory conjunction color shape multi-object Treisman "
            "feature integration' -> top-5 are all lexical/Gene-Ontology HOMONYMS of 'conjunction' (entity "
            "'conjunction' 0.346, 'Conjunction introduction' 0.339, 'CN_conjunction' 0.333, 'contention' 0.331, "
            "GO conjugation 0.329); NONE is the visual illusory-conjunction / attention-binding test, all below "
            "0.30-relevance for the actual mechanism. CONFIRMED GENUINELY NOVEL in the arc (matches the cell's "
            "own prereg dedup, which found only biology/GO homonyms at 0.33-0.38 and differentiated from "
            "exp_cortex_attention_binding_router_v2 (MEMORY routing), grounding_bind_chain_systematicity "
            "(free-by-construction role-filler), and attention salience/reliability gates). No full "
            "rediscovery; this is the FIRST multi-object visual feature-binding / illusory-conjunction cell."),
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "every_negative_check_how_the_brain_does_it_proactively_USER",
            "vet_every_base_ingredient_fair_correct_brain_faithful_USER",
            "design_gate_can_fail_real_baseline_difficulty_on_before_full_run",
            "Treisman_Gelade_1980_feature_integration_theory_illusory_conjunctions",
            "Barsalou_perceptual_symbol_systems_convergence_zones",
            "Nosofsky_exemplar_categorization_GCM",
        ],
        "composes_with": [
            ("NOVEL standalone in the arc (no direct parent atom rediscovered). Adjacent (not superseded, not a "
             "formal parent): grounding_bind_chain_systematicity (free-by-construction role-filler) -- this cell "
             "explicitly SEPARATES its own free-by-construction result (novel-conjunction=1.000, un-gated) from "
             "the NON-free headline; and the attention reliability/salience-gate atoms -- this cell uses "
             "attention as a LOCALIZATION spotlight for binding, a different function than reliability gating. "
             "Reuses the 29438 HOG shape front-end VERBATIM (feat_hog) as the parallel shape feature map."),
        ],
        "strategic_implication": (
            "Attention-gated VSA binding is a proven, fair, brain-complete solution to the multi-object "
            "feature-binding (illusory-conjunction) problem: attention avoids the cross-conjunctions that a "
            "pre-attentive flat baseline cannot, replicating Treisman's Feature Integration Theory. The result "
            "is robust to M=6. The OPEN item is the flexible/IMPROVING property: the k-NN exemplar front-end is "
            "too sample-efficient to show a learning curve, so the path to a chain-grade binding result runs "
            "through a slower-learning front-end whose downstream binding demonstrably improves with exposure -- "
            "a separate clean experiment, not a retune. The crosstalk-wall envelope (M>6) is also unmapped."),
        "atomized_by": "hdi_skunkworks",
        "atomized_date": "2026-07-23",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline="" prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
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
assert len(v) == 29457, f"post-write expected 29457, got {len(v)}"
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} atoms (was 29456); new atom #29457 verified; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29456 -> 29457) ----
ledger = {
    "seq": NEW_SEQ,
    "op": "landed_vet_atomize",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "anchor": "exp_grounding_attn_bind_illusory_conjunction_v1",
    "run_anchor": "grounding_attn_bind_illusory_conjunction_v1",
    "cell_commit": "UNCOMMITTED_sha256_a57b99652fe842e3_at_repo_HEAD_524baa8b2",
    "supersedes_commit": None,
    "supersedes_atom_id": None,
    "amends_atom_id": None,
    "composes": ["NOVEL_standalone_reuses_29438_HOG_front_end_adjacent_grounding_bind_chain_systematicity_and_attention_reliability_gates"],
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": AID,
    "atom_id": AID,
    "decision": ("MEASURED_MECHANISM / proven-bound. Strong brain-faithful binding WIN held honestly at MM. "
        "Attention-gated VSA (FHRR) bind SOLVES the Treisman illusory-conjunction problem: illusory-2AFC @M=4 "
        "ATTN=0.815 vs FAIR FLAT=0.515 (chance 0.5; margin +0.300), 3 seeds, bit-deterministic re-run. FLAT "
        "uses the SAME per-window k-NN classifications; the only variable is binding pairing (verified by "
        "source inspection of encode_scene). Both must-fail controls fire (scramble 0.439, label-shuffle "
        "0.499); front-end non-degenerate (0.782/0.887); brain-complete (parallel maps + serial spotlight + "
        "FHRR bind, all load-bearing); robust to M=6 (no crosstalk wall). HELD AT MM because the "
        "pre-registered IMPROVING-property gate MISSED: learn_rise=0.042 < 0.06 and the per-seed curve is "
        "non-monotonic (seed13 drops) -- the k-NN exemplar front-end is sample-efficient / near-saturated, so "
        "'learned-from-data' (label-shuffle) is shown but 'improves-with-exposure' (the curve) is not. These "
        "are DIFFERENT properties; NOT flipped to HP. novel-conjunction=1.000 is FREE-BY-CONSTRUCTION, un-gated, "
        "not headline (no verdict leak). Object localization idealized (fixed slots). VET: full-run re-executed, "
        "all headline numbers bit-identical; aggregates recomputed from per_seed match to 1e-9; arm fairness "
        "confirmed by source. Cross-arc overlap: only lexical/GO homonyms of 'conjunction' at <=0.346 -- NOVEL "
        "in arc. CERT +0 (non-win). Local-only; needs orchestrator store sync."),
    "cert_delta": "+0 (MEASURED_MECHANISM proven-bound; strong binding win, improving-property gate missed; MIDDLE_BAND cell verdict)",
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
assert vl[-2]["seq"] == 29456, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq 29456 -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID:", AID)
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
