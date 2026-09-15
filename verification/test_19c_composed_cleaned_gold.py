"""Witness for the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold.

Reads the three landed metrics.json (scaffold-free -- does NOT re-run the cells, does NOT rewrite landed
records) and recomputes two facts directly on the population. Establishes the LOCATED NEGATIVE:
  W1  the 19c who-did-what gold is majority oblique-contaminated (clean direct-object share <= 0.30)
  W2  the parser-free surface cleaner is precise (wordlist-vs-tagger-ADP agreement >= 0.95)
  W3  POSITION DOMINATES: on the cleaned gold POS_NEAR >= 0.90 and COMPOSED loses to it CI-separated (NEG)
  W4  COMPOSITION DOES NOT POWER UP: COMPOSED ties its AGENT-SHUFFLE twin (ci_lo <= 0) at n>=600 (all-grounded)
  W5  ... and also ties the MARGINAL store (ci straddles 0) -- the agent x verb conjunction is null here
  W6  POWER CURVE: at the parent's n=171 the COMPOSED-vs-AGENTSHUF margin CI-separates <= 15% of the time
      (the parent's +0.076 CI-sep at n=171 was small-sample noise)
  W7  what SURVIVES is verb-keying: COMPOSED beats BAG and VERB-SHUFFLE CI-separated (a real but
      position-dominated signal) -- so the null in W4/W5 is agent-composition specifically, not a dead store
  W8  THE REAL LEVER IS STRUCTURAL: NP-head chunking beats nearest-position CI-separated (ci_lo > 0)
  W9  the position-ambiguous patient regime is ABSENT from the 19c gold: 0 passive items (recomputed)
  W10 cleaner spot-check recompute: clean-DO share on a population subsample matches the landed number
"""
import json, os, sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
D = os.path.join(_REPO, "data")


def _load(p):
    with open(p) as f:
        return json.load(f)


def main():
    cg = _load(os.path.join(D, "exp_19c_composed_cleaned_gold_v1", "metrics.json"))["results"]
    pw = _load(os.path.join(D, "exp_19c_composition_powered_v1", "metrics.json"))["results"]
    tax = _load(os.path.join(D, "exp_19c_whodidwhat_residual_taxonomy_v1", "metrics.json"))["results"]
    pr = _load(os.path.join(D, "exp_19c_composition_as_prediction_v1", "metrics.json"))["results"]
    up = _load(os.path.join(D, "exp_predictive_reader_composition_upgrade_v1", "metrics.json"))["results"]
    opt = _load(os.path.join(D, "exp_composition_representation_optimization_v1", "metrics.json"))["results"]
    idl = _load(os.path.join(D, "exp_ideal_composed_predictor_v1", "metrics.json"))["results"]
    dg = _load(os.path.join(D, "exp_composition_diagnosticity_v1", "metrics.json"))["results"]
    pwt = _load(os.path.join(D, "exp_composition_precision_weighted_v1", "metrics.json"))["results"]
    full = cg["FULL_CLEAN_DO"]; C = full["contrasts"]
    checks = []

    def chk(name, cond, detail):
        checks.append((name, bool(cond), detail))

    # W1 contamination
    cs = cg["contamination"]["clean_share"]
    chk("W1_gold_majority_oblique", cs <= 0.30, "clean direct-object share=%.3f (<=0.30)" % cs)
    # W2 cleaner precision
    ag = cg["contamination"]["cleaner_wordlist_vs_taggerADP_agree"]
    chk("W2_cleaner_precise", ag >= 0.95, "wordlist-vs-taggerADP agreement=%.3f (>=0.95)" % ag)
    # W3 position dominates
    pn = full["acc"]["POS_NEAR"]; cvpn = C["COMPOSED_vs_POS_NEAR"]
    chk("W3_position_dominates", pn >= 0.90 and cvpn["ci_hi"] < 0,
        "POS_NEAR=%.3f ; COMPOSED-vs-POS_NEAR d=%+.3f CI[%+.3f,%+.3f] NEG" % (pn, cvpn["delta"], cvpn["ci_lo"], cvpn["ci_hi"]))
    # W4 composition ties agent-shuffle (all-grounded, n>=600)
    cva = C["COMPOSED_vs_AGENTSHUF"]
    chk("W4_composition_ties_agentshuffle", full["n"] >= 600 and cva["ci_lo"] <= 0,
        "n=%d COMPOSED-vs-AGENTSHUF d=%+.4f CI[%+.4f,%+.4f] (ci_lo<=0 => ns)" % (full["n"], cva["delta"], cva["ci_lo"], cva["ci_hi"]))
    # W5 composition ties marginal
    cvm = C["COMPOSED_vs_MARGINAL"]
    chk("W5_composition_ties_marginal", cvm["ci_lo"] <= 0 <= cvm["ci_hi"],
        "COMPOSED-vs-MARGINAL d=%+.4f CI[%+.4f,%+.4f] straddles 0" % (cvm["delta"], cvm["ci_lo"], cvm["ci_hi"]))
    # W6 power curve
    ss = pw["power_subsample"]
    chk("W6_parent_n171_was_noise", ss and ss["frac_CI_sep_COMPOSED_vs_AGENTSHUF"] <= 0.15,
        "at n=171 CI-separates %.0f%% of the time (mean d=%+.4f)" % (100 * ss["frac_CI_sep_COMPOSED_vs_AGENTSHUF"], ss["mean_delta"]))
    # W7 verb-keying survives
    cvb = C["COMPOSED_vs_BAG"]; cvv = C["COMPOSED_vs_VERBSHUF"]
    chk("W7_verbkeying_real", cvb["ci_lo"] > 0 and cvv["ci_lo"] > 0,
        "COMPOSED-vs-BAG d=%+.4f CI-sep ; COMPOSED-vs-VERBSHUF d=%+.4f CI-sep" % (cvb["delta"], cvv["delta"]))
    # W8 structural lever
    nh = tax["NPHEAD_vs_NEAR"]
    chk("W8_structural_lever_npHead", nh["ci_lo"] > 0 and tax["acc_POS_NPHEAD"] > tax["acc_POS_NEAR"],
        "POS_NPHEAD=%.3f vs POS_NEAR=%.3f  NPHEAD-vs-NEAR d=%+.4f CI[%+.4f,%+.4f] CI-sep" % (
            tax["acc_POS_NPHEAD"], tax["acc_POS_NEAR"], nh["delta"], nh["ci_lo"], nh["ci_hi"]))

    # W9 recompute: 0 passive in the 19c gold
    LB = json.load(open(os.path.join(D, "predict_revise_recall_v1", "_population_litbank.json")))["pop"]
    n_passive = sum(1 for r in LB if r.get("voice") == "passive")
    chk("W9_no_position_ambiguous_regime", n_passive == 0,
        "19c gold passive items=%d of %d (position-ambiguous patient regime absent)" % (n_passive, len(LB)))

    # W10 cleaner spot-check recompute on a subsample (independent of the landed count)
    import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
    import experiments.exp_19c_composed_cleaned_gold_v1 as CG
    from experiments.exp_19c_copula_disambiguation_v1 import COP_AUX
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(D, "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    npv = 0; ncl = 0
    for r in LB[:1500]:
        toks = r["sent"].split(); vi = r["verb_idx"]; gi = r.get("gold_idx"); gh = r.get("gold_head")
        if not toks or gi is None or not (0 <= vi < len(toks)) or not (0 <= gi < len(toks)):
            continue
        if toks[vi].lower() in COP_AUX:
            continue
        gc = CG.grounded_cands(r)
        if len(gc) < 2 or gh not in [h for h, _ in gc] or not (gi > vi):
            continue
        npv += 1
        pos = tg.tag(toks)
        clean, _ = CG.is_clean_do(r, pos)
        ncl += int(clean)
    share = ncl / max(1, npv)
    chk("W10_cleaner_recompute", 0.15 <= share <= 0.35 and abs(share - cs) < 0.10,
        "recomputed clean-DO share on 1500-subsample=%.3f (landed=%.3f)" % (share, cs))

    # W11/W12 -- composition IS real on the BRAIN'S instrument (forward prediction), the fair positive test
    pc = pr["contrasts"]; cvm = pc["COMPOSED_vs_MARGINAL_mrr"]; cva = pc["COMPOSED_vs_AGENTSHUF_mrr"]
    chk("W11_composition_real_as_prediction", cvm["ci_lo"] > 0 and pr["n_eval"] >= 1000,
        "held-out MRR (n=%d): COMPOSED-vs-MARGINAL d=%+.4f CI[%+.4f,%+.4f] CI-sep" % (pr["n_eval"], cvm["delta"], cvm["ci_lo"], cvm["ci_hi"]))
    chk("W12_prediction_agent_signal_real", cva["ci_lo"] > 0,
        "COMPOSED-vs-AGENT-SHUFFLE MRR d=%+.4f CI[%+.4f,%+.4f] CI-sep (agent-conditioning carries signal)" % (cva["delta"], cva["ci_lo"], cva["ci_hi"]))

    # W13/W14 -- adjacent-component fidelity: the composition mechanism is REPRESENTATION-bounded (the precise brain-differ)
    gnd = up["GROUNDED_12d_organ_space"]["contrasts"]; ppmi = up["PPMI_SVD_register_native"]["contrasts"]
    chk("W13_grounded_space_too_coarse_for_composition", gnd["composed_vs_agentshuffle"]["ci_lo"] <= 0,
        "12-d grounded (organ's space): COMPOSED-vs-AGENTSHUF d=%+.4f CI[%+.4f,%+.4f] ns (composition dead in coarse space)" % (
            gnd["composed_vs_agentshuffle"]["delta"], gnd["composed_vs_agentshuffle"]["ci_lo"], gnd["composed_vs_agentshuffle"]["ci_hi"]))
    up_c = ppmi["UPGRADE_composedExemplar_vs_organCentroidMarginal"]
    chk("W14_richer_space_enables_upgrade", ppmi["composed_vs_agentshuffle"]["ci_lo"] > 0 and up_c["ci_lo"] > 0,
        "100-d PPMI: COMPOSED-vs-AGENTSHUF %+.4f CI-sep ; composed-exemplar UPGRADE over organ centroid-marginal %+.4f CI-sep" % (
            ppmi["composed_vs_agentshuffle"]["delta"], up_c["delta"]))

    # W15 -- OPTIMIZATION: the composition margin GROWS with representational capacity (dose-response confirms
    # representation is the bottleneck). dim-300 margin CI-sep AND strictly larger than the dim-25 margin.
    dc = opt["dim_curve"]; d25 = dc["25"]["composed_vs_agentshuf"]; d300 = dc["300"]["composed_vs_agentshuf"]
    spoke = opt["hub_spoke"]["SPOKE_grounded12d"]["composed_vs_agentshuf"]
    chk("W15_composition_margin_grows_with_capacity",
        d300["ci_lo"] > 0 and d300["delta"] > d25["delta"] > 0 and spoke["ci_lo"] <= 0,
        "margin dim25=%+.4f -> dim300=%+.4f (both CI-sep, grows); 12-d spoke=%+.4f ns (dose-response: representation is the lever)" % (
            d25["delta"], d300["delta"], spoke["delta"]))

    # W16 -- THE IDEAL predictor beats the organ 2x on held-out prediction, and the REPRESENTATION is the dominant
    # lever (hub increment >> composition's net increment over the best marginal). Honest decomposition.
    inc = idl["increments"]; tot = inc["IDEAL_vs_ORGAN_total"]; hub = inc["R1-R0_hub_representation"]
    net = inc["R3-R1_composition_net_over_best_marginal"]; vs = idl["increments"]["IDEAL_vs_verb_shuffle"]
    chk("W16_ideal_predictor_representation_is_the_lever",
        tot["ci_lo"] > 0 and hub["ci_lo"] > 0 and vs["ci_lo"] > 0 and hub["delta"] > 5 * abs(net["delta"]),
        "IDEAL vs ORGAN %+.4f CI-sep (%.2fx MRR); hub swap %+.4f CI-sep is the lever; composition net over best marginal %+.4f (small); verb-shuffle twin loses %+.4f" % (
            tot["delta"], idl["mrr"]["R3_IDEAL_hub_exemplar_composed"] / max(1e-9, idl["mrr"]["R0_ORGAN_spoke_centroid_marginal"]),
            hub["delta"], net["delta"], vs["delta"]))

    # W17 -- the composition net-gain wall was an ESTIMATOR under-regularization, not a ceiling: raw composition
    # HURTS on high-agent-shift items; PRECISION-WEIGHTING (Friston) removes the damage and beats the verb-prior
    # centroid base net CI-sep (where raw composition was ns).
    hi_raw = dg["terciles_by_agent_shift"]["HIGH_shift(agent~diagnostic)"]
    pwc = pwt["contrasts"]["PRECISION_BLEND_vs_CENTROID"]; pwr = pwt["contrasts"]["PRECISION_BLEND_vs_COMPOSED_raw"]
    hi_fixed = pwt["blend_vs_centroid_by_shift_tercile"]["HIGH_shift"]
    chk("W17_precision_weighting_crosses_the_wall",
        hi_raw["gain"] < 0 and pwc["ci_lo"] > 0 and pwr["ci_lo"] > 0 and hi_fixed["ci_lo"] >= hi_raw["ci_lo"],
        "raw composition HURTS high-shift %+.4f; PRECISION_BLEND beats centroid net %+.4f CI-sep (vs raw +%.4f CI-sep); high-shift damage removed (%+.4f)" % (
            hi_raw["gain"], pwc["delta"], pwr["delta"], hi_fixed["gain"]))

    # W18 -- THE ASSEMBLED IDEAL RECIPE, proven end-to-end: beats the organ CI-sep (>2x MRR), both info-free twins
    # lose CI-sep, precision-composition is a real net add on the FULL set, and the precision term earns its place.
    rc = _load(os.path.join(D, "exp_ideal_recipe_v1", "metrics.json"))["results"]["contrasts"]
    e2e = rc["IDEAL_vs_ORGAN_end_to_end"]; ash = rc["IDEAL_vs_agent_shuffle_twin"]; vsh = rc["IDEAL_vs_verb_shuffle_twin"]
    pcn = rc["precisionComposition_net_IDEAL_vs_HUBCENTROID_full"]; pterm = rc["precision_term_IDEAL_vs_RAW"]
    chk("W18_ideal_recipe_proven_end_to_end",
        e2e["ci_lo"] > 0 and ash["ci_lo"] > 0 and vsh["ci_lo"] > 0 and pcn["ci_lo"] > 0 and pterm["ci_lo"] > 0,
        "IDEAL vs ORGAN %+.4f CI-sep; twins lose (agent %+.4f, verb %+.4f); precision-composition net (full) %+.4f CI-sep; precision term %+.4f CI-sep" % (
            e2e["delta"], ash["delta"], vsh["delta"], pcn["delta"], pterm["delta"]))

    # W19 -- the FULLY FUNCTIONAL system: NP-head chunking lifts SELECTION CI-sep, thematic fit adds ZERO to
    # selection (best fit-weight = 0 -> the prediction lever does NOT translate to selection), and the SAME system
    # predicts >2x the organ. One system, both jobs, each cue where it is valid.
    sysr = _load(os.path.join(D, "exp_whodidwhat_full_system_v1", "metrics.json"))["results"]
    s = sysr["selection"]; pr2 = sysr["prediction"]["IDEAL_vs_ORGAN"]
    fit_sel_zero = (float(s["best_w_fit"]) == 0.0) or (s["FITbest_vs_NPHEAD_full"]["ci_hi"] <= 0.0001)
    chk("W19_full_system_selection_and_prediction",
        s["NPHEAD_vs_POS"]["ci_lo"] > 0 and fit_sel_zero and pr2["ci_lo"] > 0,
        "NP-head lifts selection %+.4f CI-sep (->%.3f); thematic-fit selection value=0 (best w_fit=%s); SAME system predicts %.2fx organ (%+.4f CI-sep)" % (
            s["NPHEAD_vs_POS"]["delta"], s["acc_NPHEAD"], s["best_w_fit"],
            sysr["prediction"]["mrr_IDEAL"] / max(1e-9, sysr["prediction"]["mrr_ORGAN"]), pr2["delta"]))

    # W20 -- the MORE-IDEAL system, faithfully implemented (Bayesian multiplicative cue integration, accuracy-
    # calibrated reliability, dense-kNN coverage) does NOT beat the hub-only ideal, and the measured reason is cue
    # QUALITY not integration op: the secondary streams are far weaker and non-complementary. Coverage does rise.
    mo = _load(os.path.join(D, "exp_more_ideal_system_v1", "metrics.json"))["results"]
    sc = mo["standalone_cue_mrr"]; moc = mo["contrasts"]
    weaker = sc["hub"] > 2 * sc["spoke"] and sc["hub"] > 1.5 * sc["context"]
    no_beat = moc["MORE_IDEAL_CALIB_vs_IDEAL"]["ci_lo"] <= 0 and moc["FUSE_BAYES_vs_IDEAL"]["ci_hi"] < 0
    cov_up = mo["agent_coverage"]["with_knn_proxy"] > 0.9 and mo["agent_coverage"]["hub_only"] < 0.5
    twins = moc["MORE_IDEAL_CALIB_vs_verbshuffle"]["ci_lo"] > 0
    chk("W20_more_ideal_bounded_by_cue_quality_not_integration",
        weaker and no_beat and cov_up and twins,
        "standalone hub=%.3f >> spoke=%.3f/context=%.3f; faithful integration does NOT beat hub-only (MORE_IDEAL_CALIB %+.4f, Bayesian fusion %+.4f NEG); coverage %.2f->%.2f; twins lose" % (
            sc["hub"], sc["spoke"], sc["context"], moc["MORE_IDEAL_CALIB_vs_IDEAL"]["delta"],
            moc["FUSE_BAYES_vs_IDEAL"]["delta"], mo["agent_coverage"]["hub_only"], mo["agent_coverage"]["with_knn_proxy"]))

    # W21 -- the RIGHT metric (graded thematic-fit 2AFC, frequency-controlled) shows the model is competent where
    # exact-match hid it: strong verb-level fit; richer representation helps; agent-composition is real+small,
    # isolated on verb-typical foils (the clean Bicknell test).
    tf = _load(os.path.join(D, "exp_thematic_fit_2afc_v1", "metrics.json"))["results"]["foil_types"]
    va = tf["verb_atypical"]; vt = tf["verb_typical"]
    chk("W21_graded_metric_reveals_real_competence",
        va["VEC_MARGINAL"]["acc"] > 0.65 and va["dim200_vs_dim50"]["ci_lo"] > 0 and vt["COMPOSED_vs_MARGINAL"]["ci_lo"] > 0,
        "verb-atypical 2AFC=%.3f (strong verb-level fit); richer-rep helps +%.4f CI-sep; agent-composition real on verb-typical foils +%.4f CI-sep (exact-match hid all this)" % (
            va["VEC_MARGINAL"]["acc"], va["dim200_vs_dim50"]["delta"], vt["COMPOSED_vs_MARGINAL"]["delta"]))

    # W22 -- the structured situation model (Sentence-Gestalt): a CARICATURE on single sentences (research), but on
    # MULTI-PARTICIPANT events a SECOND bound participant adds patient-prediction signal beyond agent+verb (graded
    # 2AFC), with an oblique-shuffle twin losing. The richer/structured stream earns its keep where it has extra terms.
    sg = _load(os.path.join(D, "exp_sentence_gestalt_multiparticipant_v1", "metrics.json"))["results"]
    chk("W22_situation_model_adds_on_multiparticipant",
        sg["AVO_vs_AV"]["ci_lo"] > 0 and sg["AVO_vs_oblshuf"]["ci_lo"] > 0 and sg["acc"]["AV"]["acc"] < 0.52,
        "multi-participant 2AFC: agent-only=%.3f (chance) -> +2nd participant=%.3f (AVO-vs-AV %+.4f CI-sep; oblique-shuffle loses %+.4f CI-sep, n=%d)" % (
            sg["acc"]["AV"]["acc"], sg["acc"]["AVO"]["acc"], sg["AVO_vs_AV"]["delta"], sg["AVO_vs_oblshuf"]["delta"], sg["n_multiparticipant_test"]))

    npass = sum(1 for _, ok, _ in checks if ok)
    print("=" * 78)
    for name, ok, detail in checks:
        print("[%s] %-34s %s" % ("PASS" if ok else "FAIL", name, detail))
    print("=" * 78)
    print("%d/%d checks pass" % (npass, len(checks)))
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
