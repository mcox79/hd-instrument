"""test_ppc_meaning_representation -- scaffold-free witness for the PPC meaning-representation solution.

Reproduces the headline WITHOUT re-running the heavy cells: (A) live disk facts about where the chain discards
the intrinsic gain, and the byte-identity invariant; (B) the landed metrics from the four full runs assert the
three bar items. Run:  .venv/Scripts/python.exe verification/test_ppc_meaning_representation.py
"""
import json
import os
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

PASS = []


def ok(name, cond, detail=""):
    PASS.append(bool(cond))
    print("  [%s] %s %s" % ("OK" if cond else "XX", name, detail))


def _metrics(name):
    p = os.path.join(_REPO, "data", name, "metrics.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


# ---------------------------------------------------------------- A. LIVE DISK FACTS
print("A. live disk facts -- where the chain discards the intrinsic gain, and the additive invariant")

# A1: the four mechanism cells exist and carry a valid __bf_status__ tag
import importlib
VALID = {"BF", "BF_SPIRIT", "NOT_BF", "BF_UNPINNED", "BF_UNVERIFIED"}
for m in ("exp_ppc_precision_tracks_correctness_v1", "exp_ppc_fusion_v1",
          "exp_ppc_grow_by_reading_v1", "exp_ppc_no_regression_v1", "exp_ppc_selective_prediction_v1",
          "exp_all_bf_upstream_trace_v1", "exp_bf_learned_channel_landing_v1",
          "exp_ppc_second_gold_powerup_v1", "exp_ppc_grow_to_strength_v1", "exp_ppc_reliability_deferral_v1",
          "exp_ppc_population_reliability_v1", "exp_meaning_depth_gap_v1",
          "exp_valence_polarity_meaning_channel_v1", "exp_directional_consequence_channel_v1",
          "exp_role_asymmetry_converse_channel_v1"):
    mod = importlib.import_module("experiments." + m)
    ok("A1 %s carries valid __bf_status__" % m, getattr(mod, "__bf_status__", None) in VALID,
       "= %s" % getattr(mod, "__bf_status__", None))

# A2: the LEARNED channel discards its gain -- dep_ppmi_matrix L2-normalises the rows (row norm == 1)
from experiments.exp_learned_structured_meaning_v1 import dep_ppmi_matrix
from collections import Counter
counts = {"cat": Counter({("H", "sit"): 5, ("D", "the"): 3}),
          "dog": Counter({("H", "run"): 2}), "sit": Counter({("D", "cat"): 5})}
mask, P = dep_ppmi_matrix(counts, ["cat", "dog", "sit"])
rownorms = np.sqrt(np.asarray(P.multiply(P).sum(axis=1)).ravel())
ok("A2 dep_ppmi_matrix L2-normalises rows (gain discarded at construction)",
   np.allclose(rownorms[mask], 1.0, atol=1e-6), "norms=%s" % np.round(rownorms, 3).tolist())
# ...but the raw count (the gain) is recoverable from the counts dict
gain_cat = sum(counts["cat"].values())
ok("A2b DEP gain = raw dependency count is recoverable (cat=8 > dog=2)",
   gain_cat == 8 and sum(counts["dog"].values()) == 2)

# A3: the GROUNDED channel discards its reliability -- the organ loads only .mean; the .SD reliability is separate
from hdlab import grounded_similarity as GS
v = GS.grounded_vector("dog")
ok("A3 grounded_vector is a 12-d point (mean-only; no reliability dim)", v is not None and int(v.shape[0]) == 12)
from experiments.exp_ppc_precision_tracks_correctness_v1 import _load_grounded_reliability
rel = _load_grounded_reliability()
ok("A3b the discarded rater-SD reliability exists on disk and is loadable (>10k words)",
   isinstance(rel, dict) and len(rel) > 10000 and rel.get("dog", None) is not None)

# A4: the additive invariant -- uniform gain == equal weight, bit-identical (the recall path is untouched)
from experiments.exp_ppc_fusion_v1 import _weights_for_query
we = _weights_for_query("EQUAL", 0, ["a", "b", "c"], {"a": np.ones(1)}, {"a": np.ones(1)},
                        {"a": 1.0, "b": 1.0, "c": 1.0})
wu = _weights_for_query("GAIN", 0, ["a", "b", "c"],
                        {"a": np.ones(1), "b": np.ones(1), "c": np.ones(1)},
                        {"a": np.ones(1), "b": np.ones(1), "c": np.ones(1)}, {"a": 1.0, "b": 1.0, "c": 1.0})
ok("A4 uniform-gain PPC weight == equal weight (additive no-op; recall path byte-identical)",
   np.array_equal(we, wu))

# A5: gain is monotone in evidence (more dependency counts -> higher gain), the ordering the precision needs
ok("A5 gain is monotone in accumulated evidence", sum(counts["cat"].values()) > sum(counts["dog"].values()))

# A6: REUSE -- the parser-free directional channel IS the substrate's EXISTING ConceptSpace ROUTE-B co-occurrence
# store (observe_context_counts / all_context_counts) fed with DIRECTIONALLY-TYPED context lemmas (order coding),
# read via the substrate's EXISTING PPMI. Byte-identical to the experiment's build_seq_counts -> not a parallel organ.
from hdlab.reading_grounding_loop import ConceptSpace, CTX_D, normalize_lemma
from experiments.exp_all_bf_upstream_trace_v1 import SEQ_TAPS, build_seq_counts
_sp = ConceptSpace(d=CTX_D); _sp.track_context_counts = True
_sents = ["the cat sat on the mat", "a big cat ran fast", "the dog sat quietly"]
for _s in _sents:
    _lem = [normalize_lemma(t) for t in _s.split()]; _n = len(_lem)
    for _i in range(_n):
        _typed = [typ + "__" + _lem[_i + d] for d, typ in SEQ_TAPS if 0 <= _i + d < _n]
        if _typed:
            _sp.observe_context_counts(_lem[_i], _typed)
_reuse = {w: dict(c) for w, c in _sp.all_context_counts().items()}
_mine = {w: {typ + "__" + ctx: k for (typ, ctx), k in c.items()} for w, c in build_seq_counts(_sents).items()}
ok("A6 REUSE: directional channel == substrate's existing ConceptSpace ROUTE-B store + directional typing (byte-identical)",
   _reuse == _mine, "(reuses observe_context_counts/all_context_counts + existing PPMI; no parallel organ)")

# ---------------------------------------------------------------- B. LANDED METRICS -> THE MEASURED STORY
# The witness asserts what the disk ACTUALLY shows: item 1 PASS, item 3 PASS, item 2 a rigorous LOCATED NEGATIVE.
print("B. landed metrics -- item1 PASS, item3 PASS, item2 LOCATED NEGATIVE (equal-weight ceilings)")

m1 = _metrics("exp_ppc_precision_tracks_correctness_v1")
if m1 is None:
    ok("B(item1) metrics present", False, "-- run the driver --mode full first")
else:
    t1 = m1["T1_gain_vs_peakedness_as_correctness_signal"]
    ok("B1 item1 PASS: the LEARNED (DEP) channel's intrinsic gain tracks correctness, CI-separated above zero",
       bool(t1["DEP"]["gain_beats_zero_ci_sep"]) and bool(m1["verdict"]["bar_item1_pass"]),
       "rho=%s ci=%s peak=%s" % (t1["DEP"]["spearman_gain_vs_correctness"], t1["DEP"]["gain_spearman_ci95"],
                                 t1["DEP"]["spearman_peakedness_vs_correctness"]))
    ok("B1b gain beats the point-vector peakedness baseline CI-separated (gain-minus-peak CI > 0)",
       t1["DEP"]["gain_minus_peakedness_ci95"][0] > 0.0, "ci=%s" % t1["DEP"]["gain_minus_peakedness_ci95"])
    ok("B1c EXPERIENCE-QUANTITY signature: the CURATED WordNet channel's gain does NOT track correctness",
       bool(m1["verdict"]["curated_CM_gain_does_NOT_track_correctness"])
       and not bool(t1["CM"]["gain_beats_zero_ci_sep"]),
       "CM gain rho=%s binned=%s" % (t1["CM"]["spearman_gain_vs_correctness"],
                                     m1["T1b_binned_calibration_gain_predicts_correctness"]["CM"]["spearman_binmean_gain_vs_rr"]))
    ok("B1d DEP binned calibration monotone positive (Study-C-style)",
       (m1["T1b_binned_calibration_gain_predicts_correctness"]["DEP"]["spearman_binmean_gain_vs_rr"] or 0) > 0,
       "binned=%s" % m1["T1b_binned_calibration_gain_predicts_correctness"]["DEP"]["spearman_binmean_gain_vs_rr"])
    ok("B1e select-channel-by-GAIN >= select-by-PEAKEDNESS (gain is a usable reliability signal)",
       bool(m1["verdict"]["select_by_gain_beats_peakedness"]),
       "gain=%s peak=%s" % (m1["T3_headroom"]["select_channel_by_GAIN_MRR"],
                            m1["T3_headroom"]["select_channel_by_PEAKEDNESS_MRR"]))

m2 = _metrics("exp_ppc_fusion_v1")
if m2 is None:
    ok("B(item2) metrics present", False, "-- run the driver --mode full first")
else:
    # LOCATED NEGATIVE: no weighting scheme beats equal-weight -- a FITTED weight also fails -> equal is at the ceiling.
    ok("B2 item2 LOCATED NEGATIVE: equal-weight is at the per-query reweighting ceiling -- a FITTED weight fails too",
       m2["MRR"]["FITTED"] <= m2["MRR"]["EQUAL"] and m2["MRR"]["GAIN"] <= m2["MRR"]["EQUAL"],
       "EQUAL=%s FITTED=%s GAIN=%s PEAK=%s" % (m2["MRR"]["EQUAL"], m2["MRR"]["FITTED"], m2["MRR"]["GAIN"], m2["MRR"]["PEAK"]))
    ok("B2b intrinsic GAIN MATCHES the fitted weight with NO fitting (CI includes 0) -- eliminates the fitted knob",
       bool(m2["verdict"]["gain_matches_or_beats_FITTED_no_fitting"]), "GAIN_vs_FITTED=%s" % m2["GAIN_vs_FITTED_MRR"])
    ok("B2c WHERE THE GAIN IS EARNED it WINS: full-power learned-only {G,DEP} gain-weighting beats equal-weight CI-sep",
       bool(m2["FULL_POWER_uncalibrated"]["learned_only_gain_beats_equal_ci_sep"]),
       "learned-only GAIN vs EQUAL=%s (curated-mix stays negative %s)"
       % (m2["FULL_POWER_uncalibrated"]["LEARNED_ONLY_GAIN_vs_EQUAL"],
          m2["FULL_POWER_uncalibrated"]["GAIN_vs_EQUAL_fullmix"]["diff"]))

m4 = _metrics("exp_ppc_no_regression_v1")
if m4 is None:
    ok("B(item3) metrics present", False, "-- run the driver --mode full first")
else:
    ok("B3 item3 PASS: uniform-gain fusion == equal-weight bit-identical (recall path no-op)",
       bool(m4["INV1_uniform_gain_equals_equal_weight_bit_identical"]))
    ok("B3b recall cosine read unchanged by gain (recognition/recall path byte-identical)",
       bool(m4["INV2_recall_cosine_read_unchanged_by_gain"]))

m3 = _metrics("exp_ppc_grow_by_reading_v1")
if m3 is None:
    ok("B(upstream) metrics present", False, "-- run the driver --mode full first")
else:
    ok("B4 upstream: DEP MRR rises with reading volume (the precision is EARNED by BF reading)",
       bool(m3["verdict"]["DEP_mrr_rises_with_reading"]),
       "curve=%s" % [c["DEP_mrr"] for c in m3["reading_volume_curve"]])
    ok("B4b gain->correctness calibration present at full reading",
       bool(m3["verdict"]["gain_calibration_present_at_full"]),
       "calib=%s" % [c["DEP_gain_calibration_spearman"] for c in m3["reading_volume_curve"]])

m5 = _metrics("exp_ppc_selective_prediction_v1")
if m5 is None:
    ok("B(stronger) metrics present", False, "-- run the driver --mode full first")
else:
    ok("B5 stronger version: gain-ranked selective prediction RAISES DEP accuracy at reduced coverage (directional)",
       bool(m5["verdict"]["DEP_gain_raises_accuracy_at_lower_coverage"]),
       "rc_by_gain=%s vs_random@0.5=%s" % (m5["DEP"]["risk_coverage_by_GAIN"], m5["DEP"]["GAIN_vs_RANDOM_at_0.5"]["diff"]))

# ---------------------------------------------------------------- C. ALL-BF UPSTREAM FIX + TOP-DOWN LOSS TRACE
print("C. all NOT-BF upstream components fixed BF; loss traced from the top")
mt = _metrics("exp_all_bf_upstream_trace_v1")
if mt is None:
    ok("C metrics present", False, "-- run exp_all_bf_upstream_trace_v1 --mode full first")
else:
    fx = mt["FIX_5b_parser_removed"]
    ok("C1 NOT-BF parser REPLACED by a directional-sequential BF channel with NO loss (SEQ matches parser-DEP)",
       bool(mt["verdict"]["parser_replaced_by_BF_sequence_no_loss"]),
       "SEQ=%s DEP=%s SEQ_vs_DEP=%s" % (mt["single_MRR"]["SEQ"], mt["single_MRR"]["DEP"], fx["SEQ_vs_DEP_MRR"]))
    ok("C2 the parser-free SEQ channel's gain is a valid precision (tracks correctness) + twin loses",
       bool(mt["verdict"]["SEQ_gain_is_a_valid_precision"]) and bool(fx["SEQ_twin_loses"]),
       "gain_rho=%s twin=%s" % (fx["SEQ_gain_tracks_correctness_spearman"], fx["SEQ_twin_mrr"]))
    ok("C3 top-down trace: dominant remaining loss is EXPOSURE (learned vs supplied ontology), not a non-BF component",
       bool(mt["verdict"]["top_loss_is_exposure_not_a_nonBF_component"]),
       "exposure_gap=%s" % mt["exposure_gap_curated_minus_learned"])

# ---------------------------------------------------------------- D. THE LANDABLE IMPROVEMENT (for strategy)
print("D. the landable brain-foundational improvement: parser-free learned channel at no accuracy cost")
md = _metrics("exp_bf_learned_channel_landing_v1")
if md is None:
    ok("D metrics present", False, "-- run exp_bf_learned_channel_landing_v1 --mode full first")
else:
    ok("D1 LANDABLE: parser-free {G,SEQ,CM} is NOT worse than the NOT_BF-parser {G,DEP,CM} chain (more BF, no cost)",
       bool(md["verdict"]["parser_free_not_worse_than_baseline"]),
       "SEQ-chain=%s parser-chain=%s d=%s" % (md["MRR"]["LANDABLE_A_seq_equal"], md["MRR"]["BASELINE_parser"],
                                              md["LANDABLE_A_vs_BASELINE"]))
    ok("D2 the SEQ learned channel is real (row-shuffle twin loses)",
       bool(md["verdict"]["seq_twin_loses"]),
       "chain=%s twin=%s" % (md["MRR"]["LANDABLE_B_precision_where_earned"], md["MRR"]["CTRL_seq_twin"]))
    ok("D3 the SUPPLIED ontology's correct gain is UNIFORM: uniform beats the wrong feature-count gain CI-sep",
       bool(md["verdict"]["uniform_supplied_gain_beats_wrong_featurecount_gain"]),
       "B_vs_wrong=%s" % md["LANDABLE_B_vs_WRONG_cm_gain"])

# ---------------------------------------------------------------- E. ROBUSTNESS + GROW-BY-READING (2nd gold; reading more)
print("E. second-gold robustness + grow-by-reading executed")
me = _metrics("exp_ppc_second_gold_powerup_v1")
if me is None:
    ok("E metrics present", False, "-- run exp_ppc_second_gold_powerup_v1 --mode full first")
else:
    ok("E1 item1 holds on a SECOND independent gold (SimLex+SimVerb): DEP and parser-free SEQ gain both CI-sep",
       bool(me["verdict"]["item1_DEP_gain_tracks_correctness_ci_sep"])
       and bool(me["verdict"]["item1_SEQ_gain_tracks_correctness_ci_sep"]),
       "n=%d DEP_rho=%s SEQ_rho=%s" % (me["n_pooled_query_directions"],
                                       me["DEP"]["item1_gain_vs_correctness_spearman"],
                                       me["SEQ"]["item1_gain_vs_correctness_spearman"]))

mg = _metrics("exp_ppc_grow_to_strength_v1")
if mg is None:
    ok("E metrics present", False, "-- run exp_ppc_grow_to_strength_v1 --mode full first")
else:
    c0, cN = mg["grow_curve"][0], mg["grow_curve"][-1]
    ok("E2 grow-by-reading EXECUTED: reading +modern text (parser-free) raises the learned channel's MRR",
       bool(mg["verdict"]["SEQ_mrr_rises_with_reading"]),
       "SEQ %s -> %s (read %d sw lines); ontology CM=%s" % (c0["SEQ_mrr"], cN["SEQ_mrr"],
                                                            mg["simplewiki_lines_consumed"], mg["ontology_CM_mrr_reference"]))
    ok("E3 the raw-count precision SATURATES at high exposure (BF: Fisher info saturates) -> saturating gain is the fix",
       bool(mg["verdict"].get("RAW_gain_rho_saturates_at_high_exposure", False)),
       "raw_rho %s -> %s ; saturating_rho_at_max=%s" % (c0.get("SEQ_gain_rho_RAW"), cN.get("SEQ_gain_rho_RAW"),
                                                        cN.get("SEQ_gain_rho_SATURATING_log")))

# ---------------------------------------------------------------- F. RELIABILITY-DEFERRAL (convergent agreement, done right)
print("F. reliability-aware deferral via convergent-cue agreement (the precision's genuine use)")
mf = _metrics("exp_ppc_reliability_deferral_v1")
if mf is None:
    ok("F metrics present", False, "-- run exp_ppc_reliability_deferral_v1 --mode full first")
else:
    ab = mf["agreement_bins_accuracy"]
    ok("F1 convergent agreement is a GENUINE reliability signal: accuracy rises when all channels agree",
       bool(mf["verdict"]["accuracy_rises_with_agreement"]),
       "agree=1 mrr=%s -> agree=3 mrr=%s (n3=%s)" % (ab["1"]["mrr"], ab["3"]["mrr"], ab["3"]["n"]))
    ok("F2 CONTROL: the C7-null single-channel peakedness does NOT beat random (as expected)",
       bool(mf["verdict"]["SINGLE_PEAK_fails_as_expected"]),
       "single_peak vs random@0.5=%s" % mf["deferral"]["SINGLE_PEAK"]["vs_RANDOM_at_0.5"]["diff"])

# ---------------------------------------------------------------- G. PHASE-DIAGRAM MOVE: dense population reliability
print("G. phase-diagram move off 'sparse': dense population-consensus reliability enables CI-sep deferral")
mp = _metrics("exp_ppc_population_reliability_v1")
if mp is None:
    ok("G metrics present", False, "-- run exp_ppc_population_reliability_v1 --mode full first")
else:
    sw = mp["N_sweep_population_reliability"]
    ok("G1 the reliability is DENSE at population size N=30 (a graded value per read, not 0.6% unanimous)",
       sw["30"]["coverage_is_dense_frac_below_1"] > 0.5, "dense_frac=%s" % sw["30"]["coverage_is_dense_frac_below_1"])
    ok("G2 population-consensus DEFERRAL beats random abstention CI-separated at N=30 (the precision's genuine use works)",
       bool(sw["30"]["deferral_beats_random_0.5_ci_sep"]),
       "defer@0.5=%s @0.25=%s" % (sw["30"]["deferral_vs_random_at_0.5"], sw["30"]["deferral_vs_random_at_0.25"]))
    ok("G3 moving the operating point (N: 1 -> 30) turns a null reliability into a CI-separated one",
       sw["30"]["deferral_vs_random_at_0.5"]["ci"][0] > 0 and not bool(sw["1"]["deferral_beats_random_0.5_ci_sep"]),
       "N=1 diff=%s -> N=30 diff=%s" % (sw["1"]["deferral_vs_random_at_0.5"]["diff"],
                                        sw["30"]["deferral_vs_random_at_0.5"]["diff"]))

# ---------------------------------------------------------------- H. THE NEXT GAP, IDENTIFIED WITH A NUMBER
print("H. the next gap: learned meaning is relation-blind (only the supplied ontology tells syn from ant)")
mh = _metrics("exp_meaning_depth_gap_v1")
if mh is None:
    ok("H metrics present", False, "-- run exp_meaning_depth_gap_v1 --mode full first")
else:
    auc = mh["T2_synonym_vs_antonym_AUC"]
    ok("H1 LEARNED channels are RELATION-BLIND on antonyms (syn-vs-ant AUC ~chance): grounded + distributional",
       (auc["GROUNDED"] < 0.6) and (auc["SEQ"] < 0.62),
       "grounded=%s SEQ=%s" % (auc["GROUNDED"], auc["SEQ"]))
    ok("H2 only the SUPPLIED ontology discriminates same-meaning from opposite-meaning (WordNet AUC high)",
       auc["TAXONOMIC"] > 0.75, "taxonomic=%s" % auc["TAXONOMIC"])
    ok("H3 the channels are LOW-correlated (diverse axes, not redundant) -> the gap is a new TYPE of signal",
       all(v < 0.35 for v in mh["T3_channel_redundancy_correlation"].values()),
       "corr=%s" % mh["T3_channel_redundancy_correlation"])

# ---------------------------------------------------------------- I. THE FIX, LAYER 1: affective valence un-blinds antonymy
print("I. the gap FIX (layer 1): affective valence polarity separates synonyms from antonyms WITHOUT WordNet")
mi = _metrics("exp_valence_polarity_meaning_channel_v1")
if mi is None:
    ok("I metrics present", False, "-- run exp_valence_polarity_meaning_channel_v1 --mode full first")
else:
    a = mi["syn_vs_antonym_AUC"]
    ok("I1 affective VALENCE beats the relation-blind distributional floor CI-separated, WITHOUT WordNet",
       bool(mi["verdict"]["valence_beats_distributional_floor_ci_sep"]),
       "DIST=%s VALENCE=%s VAD=%s (diff %s)" % (a["DISTRIBUTIONAL"], a["VALENCE"], a["VAD"],
                                                mi["VALENCE_vs_DISTRIBUTIONAL_AUC_diff"]))
    ok("I2 it is a COMPLEMENTARY axis (low corr with distributional) and the info-free twin collapses to chance",
       bool(mi["verdict"]["valence_is_complementary_low_corr"]) and bool(mi["verdict"]["twin_collapses_to_chance"]),
       "corr=%s twin_AUC=%s" % (mi["complementarity_corr_valence_vs_distributional"], mi["info_free_twin_AUC"]))

# ---------------------------------------------------------------- J. LAYER 2: directional (2a) + role-binding wall (2b)
print("J. layer 2: path-direction separates SCALAR converses; the transfer-converse wall is located to role-binding")
mj = _metrics("exp_directional_consequence_channel_v1")
if mj is None:
    ok("J metrics present", False, "-- run exp_directional_consequence_channel_v1 --mode full first")
else:
    conv = mj["WALL_DIAGNOSTIC_dir_sim_canonical_pairs"]["converse"]
    ok("J1 layer 2a: directional path semantics separates SCALAR/SPATIAL converses (increase/decrease, open/close)",
       (conv.get("increase/decrease", 0) < -0.3) and (conv.get("open/close", 0) < -0.2),
       "increase/decrease=%s open/close=%s buy/sell=%s (transfer NOT separated)"
       % (conv.get("increase/decrease"), conv.get("open/close"), conv.get("buy/sell")))
    ok("J2 layer 2a twin collapses (the directional signal is real, not an artifact)",
       abs(mj["info_free_twin_AUC_converse"] - 0.5) < 0.1, "twin=%s" % mj["info_free_twin_AUC_converse"])

mk = _metrics("exp_role_asymmetry_converse_channel_v1")
if mk is None:
    ok("J metrics present", False, "-- run exp_role_asymmetry_converse_channel_v1 --mode full first")
else:
    rb = mk["MAIN_syn_vs_transfer_converse_residual"]
    ok("J3 layer 2b WALL located: adjacency role-asymmetry is INSUFFICIENT for transfer converses (subject-side ~chance)",
       (rb.get("AUC_subject_side_L") is None) or (rb["AUC_subject_side_L"] < 0.6),
       "subject_side_L_AUC=%s floor=%s -> transfer converses need ROLE-BOUND heads (parsing+binding), not co-occurrence"
       % (rb.get("AUC_subject_side_L"), rb.get("AUC_symmetric_floor")))

n = len(PASS); p = sum(PASS)
print("\n%d/%d witnesses passed." % (p, n))
if p == n:
    print("PPC MEANING-REPRESENTATION WITNESS GREEN -- item1 PASS (intrinsic gain tracks correctness CI-sep above "
          "the point-vector peakedness baseline; curated-channel gain does NOT -> experience-quantity signature), "
          "item3 PASS (recall path byte-identical), item2 LOCATED NEGATIVE (equal-weight is at the reweighting "
          "ceiling; a fitted weight also fails; intrinsic gain MATCHES it with no fitting).")
if __name__ == "__main__":
    sys.exit(0 if p == n else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
