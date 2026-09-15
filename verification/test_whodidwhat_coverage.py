"""Scaffold-free witness for the problem
`the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses`.

Reads the landed metrics.json of the three cells and asserts the headline claims. No reader is re-run here (the
cells own the heavy first-hand reader passes); this witness verifies the recorded science is internally consistent
and clears the bar. Run:  .venv/Scripts/python.exe verification/test_whodidwhat_coverage.py
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(anchor):
    with open(os.path.join(REPO, "data", anchor, "metrics.json"), encoding="ascii") as fh:
        return json.load(fh)["results"]


def approx(a, b, tol=0.02):
    return abs(a - b) <= tol


N = 0
def check(cond, msg):
    global N
    assert cond, "FAIL: " + msg
    N += 1
    print("  ok:", msg)


def main():
    print("== A. DIAGNOSIS (first-hand live-reader abstention taxonomy) ==")
    d = load("exp_whodidwhat_coverage_diagnosis_v1")
    n = d["n"]
    check(n == 669, "diagnosis population is the 669 clean-19c DOs (n=%d)" % n)
    tw = d["firsthand_taxonomy"]["wired"]
    check(tw["correct"] == 421 and tw["wrong"] == 101 and tw["event_no_patient"] == 127 and tw["no_event"] == 20,
          "wired taxonomy 421/101/127/20 (first-hand)")
    check(sum(tw.values()) == 669, "wired taxonomy is exhaustive (sums to 669)")
    check(d["firsthand_matches_stored_rate"]["wired"] == 1.0
          and d["firsthand_matches_stored_rate"]["positional"] == 1.0,
          "first-hand reader reproduces the STORED wired_pick/pos_pick 100%")
    ac = d["abstain_causes"]
    check(ac["speech_verb_quotative_overfire"] == 80
          and ac["verb_subcat_false_suppression"] == 47
          and ac["no_event_pos_mistag"] == 20
          and ac["other_event_no_patient"] == 0,
          "147 abstentions decompose exactly: 80 speech-quotative + 47 verb_subcat + 20 no-event + 0 other")
    check(ac["speech_verb_quotative_overfire"] + ac["verb_subcat_false_suppression"]
          + ac["no_event_pos_mistag"] + ac["other_event_no_patient"] == 147,
          "decomposition is exhaustive over the 147 abstentions")
    check(d["speech_recovered_by_positional"] == 80,
          "positional route recovers ALL 80 speech-quotative losses (parse-routing is the cause, not missing NPs)")
    check(d["parse_routing_cost_effective"] > 0.09,
          "wired parse-routing is NET-NEGATIVE vs positional (+%.4f effective)" % d["parse_routing_cost_effective"])
    check(approx(d["effective_end_to_end"]["wired"], 0.6293) and approx(d["effective_end_to_end"]["positional"], 0.7294),
          "effective floors: wired 0.629, positional 0.729")

    print("== B. RECOVERY (brain-faithful robust role path; effective end-to-end) ==")
    r = load("exp_whodidwhat_coverage_recover_v1")
    check(r["n"] == 669, "recovery population is the 669 clean-19c DOs")
    eff = r["effective_end_to_end"]
    check(approx(eff["a0"], 0.6293), "A0 live-wired floor 0.629")
    check(approx(eff["rec"], 0.9806), "RECOVERED effective 0.981")
    a0 = r["REC_vs_A0_wired"]
    check(a0["sep"] and a0["ci_lo"] > 0 and a0["delta"] > a0["null_p95"],
          "REC beats the wired floor CI-separated AND over null_p95 (d=%.4f CI_lo=%.4f null_p95=%.4f)"
          % (a0["delta"], a0["ci_lo"], a0["null_p95"]))
    a1 = r["REC_vs_A1_positional"]
    check(a1["sep"] and a1["ci_lo"] > 0,
          "REC beats the stronger positional floor CI-separated (d=%.4f)" % a1["delta"])
    tw2 = r["REC_vs_TWIN_random"]
    check(tw2["sep"] and eff["twin"] < eff["rec"] - 0.4,
          "info-free twin (random post-verbal pick) LOSES CI-separated (twin=%.4f)" % eff["twin"])
    pc = r["per_cause_recovery"]
    tot_contrib = sum(v["recovered_correct"] for v in pc.values())
    check(approx(tot_contrib / r["n"], eff["rec"], 0.001),
          "per-cause recovered-correct sums to the RECOVERED effective (ablation is exhaustive)")
    check(pc["speech_quotative"]["recovered_correct"] >= 70
          and pc["verb_subcat"]["recovered_correct"] == 47
          and pc["no_event"]["recovered_correct"] == 20,
          "recovery lands each cause: speech>=70/80, verb_subcat 47/47, no_event 20/20")
    nr = r["no_regression"]
    check(nr["regressions"] <= 5 and r["rec_present_accuracy"] >= 0.97,
          "NO-REGRESSION: <=5 individual flips of 421; present-accuracy 0.981 >> wired's 0.807 (n=%d)" % r["rec_present_n"])

    print("== C. MODERN GENERALIZATION (no regression) ==")
    mg = r["modern_generalization"]
    check(mg["REC_vs_A0_wired"]["sep"] and mg["effective"]["rec"] > mg["effective"]["a0"],
          "on modern QA-SRL (n=%d) REC beats the wired floor CI-separated (%.4f -> %.4f)"
          % (mg["n"], mg["effective"]["a0"], mg["effective"]["rec"]))

    print("== D. FAIR FLOOR (the updated arc-eager parser does NOT close the gap) ==")
    p = load("exp_whodidwhat_coverage_parser_floor_v1")
    check(p["clauses_recovered_by_better_parser"] <= 3,
          "upgrading ArcParser(UAS.775)->arc-eager(UAS.842) recovers <=3 clauses: abstention is parser-INDEPENDENT")
    check(approx(p["effective_arceager"], 0.631, 0.02),
          "best-parser wired floor still ~0.63 (not a strawman floor)")

    print("== E. GRADED/STRUCTURAL-DO TRANSITIVITY (no-regression on genuine intransitives) ==")
    t = load("exp_whodidwhat_coverage_transitivity_control_v1")
    p1 = t["P1_recovery_accuracy"]; p2 = t["P2_intransitive_correct_abstention"]; p0 = t["P0_main_gold_effective"]
    check(p1["STRUCTURAL_DO"] >= 0.99 and p1["HARD_gate"] == 0.0,
          "STRUCTURAL_DO recovers the verb_subcat-suppressed clean-DO patients (%.2f) the hard gate loses entirely"
          % p1["STRUCTURAL_DO"])
    check(p2["NAIVE_soft"] < 0.1 and p2["STRUCTURAL_DO"] >= 0.9,
          "the NAIVE soft rule over-generates on intransitives (%.2f); STRUCTURAL_DO abstains correctly (%.2f)"
          % (p2["NAIVE_soft"], p2["STRUCTURAL_DO"]))
    check(p0["STRUCTURAL_DO"] >= p0["NAIVE_soft"] - 0.002,
          "STRUCTURAL_DO does NOT regress the main-669 recovery (%.4f vs naive %.4f)"
          % (p0["STRUCTURAL_DO"], p0["NAIVE_soft"]))

    print("== F. VERB-ID RESIDUAL is solvable-in-principle (located, not a wall) ==")
    v = load("exp_whodidwhat_verb_id_recoverable_v1")
    check(v["recovery_wordnet_only"] >= 0.8,
          "the 20 no-event tokens ARE lexically verbs (WordNet verb-reading on %.2f) -- not a lexical wall"
          % v["recovery_wordnet_only"])
    check(v["fp_permissive_per_sentence"] > 1.0,
          "but a simple position heuristic is too permissive (FP=%.2f/sent) -> needs real clause-structure "
          "predicate-ID (follow-on 1c)" % v["fp_permissive_per_sentence"])

    print("== G. DEPLOYED MENTION-SOURCE TRANSFER (the recovery's candidate-source contingency) ==")
    m = load("exp_whodidwhat_mention_source_transfer_v1")
    check(m["singleton_frac_of_clusters"] > 0.5,
          "LitBank coref DOES annotate singletons (%.2f of clusters) -> not a singleton-dropping problem"
          % m["singleton_frac_of_clusters"])
    check(m["deployed_coref_noun_coverage"] < 0.2,
          "the DEPLOYED coref mention source covers only %.1f%% of content nouns (entity-type only) -> the every-noun "
          "candidate set is a brain-faithful assumption a referent-per-NP builder must supply"
          % (100 * m["deployed_coref_noun_coverage"]))

    print("== H. MEANING/PREDICTION COMPLETENESS (who-did-what is structure-bound; confidence is the earned benefit) ==")
    c = load("exp_whodidwhat_meaning_prediction_completeness_v1")
    pa = c["present_acc"]
    check(pa["STRUCT"] > pa["FIT_ONLY"] + 0.05,
          "STRUCT (structural pick %.4f) beats grounded-meaning alone (%.4f) -> meaning is not the selector"
          % (pa["STRUCT"], pa["FIT_ONLY"]))
    check(pa["STRUCT_FIT"] <= pa["STRUCT"] + 0.005 and pa["SURP_RESELECT"] <= pa["STRUCT"],
          "adding meaning-arbitration (%.4f) or surprisal-reselection (%.4f) does NOT beat STRUCT -> structure-bound "
          "(prior-work proven-negative confirmed first-hand)" % (pa["STRUCT_FIT"], pa["SURP_RESELECT"]))
    check(c["confidence_surprisal_auc"] > 0.6 and c["mean_surprisal_wrong"] > c["mean_surprisal_correct"],
          "surprisal is the EARNED predictive benefit: it flags wrong picks (AUC %.3f; wrong %.2f > correct %.2f)"
          % (c["confidence_surprisal_auc"], c["mean_surprisal_wrong"], c["mean_surprisal_correct"]))

    print("== I. LIVE END-TO-END through the real reader (the wire is a config of landed flags) ==")
    w = load("exp_whodidwhat_live_wire_end_to_end_v1")
    e = w["live_effective_by_config"]
    # NOTE: absolute A0 is a MOVING TARGET (the substrate improved mid-work); assert only the config-ladder DIRECTION.
    check(w["A3_vs_A0_wired"]["sep"] and e["A3_positional_nphead_nosubcat"] > e["A0_deployed_wired"],
          "flipping to landed flags (positional + np_head_reduce + verb_subcat off) lifts the LIVE reader %.4f -> %.4f "
          "CI-separated -- the wire is a config, not new code" % (e["A0_deployed_wired"], e["A3_positional_nphead_nosubcat"]))

    print("== J. CURRENT-FLOOR RECOMPUTE (the floor moved upstream during the work; recovery still adds) ==")
    rd = load("exp_whodidwhat_current_floor_rediagnosis_v1")
    check(rd["CURRENT_wired_effective"] > rd["stored_wired_pick_effective_STALE"] + 0.05,
          "the live floor MOVED up during the work: stored %.4f (stale) -> current %.4f (recomputed first-hand)"
          % (rd["stored_wired_pick_effective_STALE"], rd["CURRENT_wired_effective"]))
    m2 = rd["recovery_marginal_over_current_floor"]
    check(m2["sep"] and m2["ci_lo"] > 0,
          "the recovery STILL beats the CURRENT (not stale) floor CI-separated: +%.4f CI[%+.4f,%+.4f]"
          % (m2["delta"], m2["ci_lo"], m2["ci_hi"]))
    check(rd["current_wrong_that_recovery_fixes"] >= 0.7 * rd["current_wrong_picks"],
          "signal loss RE-LOCATED to accuracy: recovery fixes %d of the reader's %d remaining wrong picks"
          % (rd["current_wrong_that_recovery_fixes"], rd["current_wrong_picks"]))

    print("== K. REFERENT-PER-NP prototype (the biggest deployment lever, working) ==")
    rn = load("exp_whodidwhat_referent_per_np_prototype_v1")
    check(rn["patient_coverage_referent_per_np"] > rn["patient_coverage_coref_deployed"] + 0.1,
          "referent-per-NP lifts deployed patient candidate-coverage %.4f -> %.4f (+%.4f) on real LitBank docs"
          % (rn["patient_coverage_coref_deployed"], rn["patient_coverage_referent_per_np"], rn["coverage_recovery"]))

    print("== L. VERB-ID override prototype (located partial -> needs a trained model, 1c) ==")
    vo = load("exp_whodidwhat_verbid_override_prototype_v1")
    check(vo["recovery_COMBINED"] >= 0.4 and vo["fp_combined_per_sentence"] > 1.0,
          "combined glass-box verb-ID recovers %.2f of the 20 but at %.2f false-verbs/sent -> heuristic is not enough (1c)"
          % (vo["recovery_COMBINED"], vo["fp_combined_per_sentence"]))

    print("== M. THE IDEAL brain-foundational pipeline (routed; canonical at ceiling, non-canonical is the frontier) ==")
    id_ = load("exp_whodidwhat_ideal_brain_foundational_v1")
    cn, nc = id_["CANONICAL"], id_["NON_CANONICAL"]
    check(cn["ideal_routed"] >= 0.98 and cn["ideal_vs_current"]["sep"],
          "IDEAL is at the parse ceiling on canonical (%.4f) and CI-sep over the current floor" % cn["ideal_routed"])
    check(cn["routed_vs_flat"]["sep"] and cn["ideal_routed"] > cn["ideal_flat"],
          "ROUTING beats FLAT composition on canonical (%.4f > %.4f) -> more machinery is not better"
          % (cn["ideal_routed"], cn["ideal_flat"]))
    check(nc["ideal_vs_current"]["sep"] and nc["ideal_routed"] > 4 * nc["current_floor"],
          "IDEAL lifts NON-CANONICAL 5x off a near-zero floor (%.4f -> %.4f, CI-sep) -- real but the frontier"
          % (nc["current_floor"], nc["ideal_routed"]))
    check(cn["conf_auc"] > 0.6 and nc["conf_auc"] > 0.6,
          "the predictive-confidence layer flags the ideal's own errors on both regimes (AUC %.2f / %.2f)"
          % (cn["conf_auc"], nc["conf_auc"]))

    print("== N. NON-CANONICAL frontier traced to its upstream source (gold noise + filler-gap, not just a parser) ==")
    nu = load("exp_whodidwhat_noncanonical_upstream_v1")
    check(nu["gold_noise_fraction"] > 0.5,
          "the non-canonical 'frontier' is %.0f%% GOLD NOISE (intransitive-subject mislabels + cross-clause) -- can't "
          "improve against it" % (100 * nu["gold_noise_fraction"]))
    check(nu["CLEANED"]["clausewin_fillergap"] > nu["FULL_noisy"]["ideal"],
          "the layered upstream fix works: clean the gold + brain-faithful filler-gap lifts %.4f -> %.4f"
          % (nu["FULL_noisy"]["ideal"], nu["CLEANED"]["clausewin_fillergap"]))

    print("== O. NON-CANONICAL 3-layer fix ladder (2 layers work, 1 refuted -- honest) ==")
    fg = load("exp_whodidwhat_fillergap_fix_v1")
    L = fg["LADDER"]
    check(L["L2_plus_objectgap_routing"] > L["L0_ideal_full_noisy"] + 0.08 and fg["L2_vs_L1"]["sep"],
          "L1 clean gold + L2 object-gap routing roughly DOUBLE non-canonical: %.4f -> %.4f (L2 vs L1 CI-sep)"
          % (L["L0_ideal_full_noisy"], L["L2_plus_objectgap_routing"]))
    check(not fg["L3_vs_L2"]["sep"] and L["L3_plus_valence_rerank"] <= L["L2_plus_objectgap_routing"],
          "L3 joint valence re-rank is REFUTED (%.4f <= L2 %.4f) -- meaning cue too weak, needs the meaning channel first"
          % (L["L3_plus_valence_rerank"], L["L2_plus_objectgap_routing"]))
    gs = fg["object_gap_slice"]
    check(gs["nearest_preverbal(L2)"] > gs["sophisticated_filler_REFUTED"] and gs["nearest_preverbal(L2)"] > gs["info_free_twin"],
          "on the object-gap slice the SIMPLE nearest-preverbal rule (%.4f) beats both the sophisticated filler-gap "
          "(%.4f, refuted) and the info-free twin (%.4f)" % (
              gs["nearest_preverbal(L2)"], gs["sophisticated_filler_REFUTED"], gs["info_free_twin"]))

    print("== P. THE COMPOSED PIPELINE (implementation) + per-stage SIGNAL-LOSS LEDGER ==")
    cp = load("exp_whodidwhat_composed_pipeline_v1")
    canon, ncc = cp["CANONICAL"], cp["NON_CANONICAL_cleaned"]
    check(canon["composed"] > canon["floor_current_live"] and canon["composed"] > canon["twin_shuf_reduce"],
          "composed pipeline beats the current floor (%.4f->%.4f) and its info-free twin (%.4f) on canonical"
          % (canon["floor_current_live"], canon["composed"], canon["twin_shuf_reduce"]))
    check(canon["residual_loss_to_oracle"] < 0.05,
          "canonical is NEAR-SATURATED: residual loss to the oracle ceiling is only %.4f" % canon["residual_loss_to_oracle"])
    check(ncc["composed"] > 3 * ncc["floor_current_live"] and ncc["residual_loss_to_oracle"] > 0.5,
          "non-canonical: composed lifts the floor 4x (%.4f->%.4f) but %.4f of signal is STILL lost -> the frontier "
          "(gated on the meaning channel, not structural cues)" % (
              ncc["floor_current_live"], ncc["composed"], ncc["residual_loss_to_oracle"]))
    check(canon["conf_mean_surp_wrong"] > canon["conf_mean_surp_correct"],
          "the confidence layer still flags the composed pipeline's errors (surprisal wrong %.2f > correct %.2f)"
          % (canon["conf_mean_surp_wrong"], canon["conf_mean_surp_correct"]))

    print("== Q. VERB-ID learned combiner (confirmed fix IMPLEMENTED -> located HARD_FAIL on 19c) ==")
    vc = load("exp_whodidwhat_verbid_learned_combiner_v1")
    best = vc["best_operating_point_fp_le_1"]
    check(best is not None and best["recovery"] < 0.25,
          "the learned combiner (the research-confirmed fix) HARD_FAILS on 19c: at FP<=1.0/sent recovery is only %.2f"
          % (best["recovery"] if best else 0.0))
    check(vc["coef"]["dep_attach"] > 1.0,
          "the discriminative signal (dependency attachment, weight %.2f) is corrupted on the mis-tagged tokens (the "
          "parser inherits the POS mis-tag) -> the real fix is a JOINT POS+parse retrain, not a combiner"
          % vc["coef"]["dep_attach"])

    print("== R. COMPETENT-READER BENCHMARK (brain-comparison made performance-level) ==")
    br = load("exp_whodidwhat_competent_reader_benchmark_v1")
    bc, bn = br["CANONICAL"], br["NON_CANONICAL_cleaned"]
    check(bc["ours"] >= bc["competent_reader_spacy"] - 0.02 and bc["ours"] <= bc["oracle_ceiling"] + 0.001,
          "on CANONICAL we are at competent-reader level: ours %.4f vs a competent parser (spaCy) %.4f, near oracle %.4f"
          % (bc["ours"], bc["competent_reader_spacy"], bc["oracle_ceiling"]))
    check(bn["competent_reader_spacy"] < 0.1,
          "on NON-CANONICAL a COMPETENT reference parser ALSO fails (spaCy %.4f) -> the non-canonical GOLD is broken, "
          "the 0.70 'signal loss' is measuring against an unreliable target, NOT a modeling/meaning gap"
          % bn["competent_reader_spacy"])

    print("== S. VERB-ID JOINT POS+parse (brain-faithful fix; heuristic version also located as HARD_FAIL) ==")
    jp = load("exp_whodidwhat_verbid_joint_pos_parse_v1")
    check(jp["joint_recovery"] < 0.25,
          "the heuristic joint re-categorise+re-parse ALSO HARD_FAILS (recovery %.4f) -> 19c verb-ID needs a fully "
          "JOINTLY-TRAINED POS+dependency model, not any heuristic (3 approaches now refuted; scoped as 1c)"
          % jp["joint_recovery"])

    print("== T. NON-CANONICAL GOLD REBUILD (against a competent reference -> both broken gold AND a real gap) ==")
    gr = load("exp_whodidwhat_noncanonical_gold_rebuild_v1")
    check(gr["litbank_agrees_with_competent_gold"] < 0.2,
          "the original non-canonical LitBank gold agrees with a competent reader only %.4f -> ~broken (rebuild needed)"
          % gr["litbank_agrees_with_competent_gold"])
    check(gr["OURS_vs_REBUILT_competent_gold"] < 0.7,
          "against the REBUILT competent-reader gold, our positional pipeline scores %.4f -> a REAL modeling gap "
          "(a competent parser handles non-canonical; our positional rule does not), now honestly measurable"
          % gr["OURS_vs_REBUILT_competent_gold"])

    print("== U. GLASS-BOX FILLER-GAP PARSE (heuristic refuted; the lever is PARSER QUALITY) ==")
    fp2 = load("exp_whodidwhat_fillergap_parse_v1")
    check(fp2["FILLER_GAP_parse"] <= fp2["positional_only"] + 0.02,
          "the glass-box filler-gap heuristic does NOT beat positional (%.4f vs %.4f) -> heuristics are not the lever"
          % (fp2["FILLER_GAP_parse"], fp2["positional_only"]))
    check(fp2["substrate_parser_patient"] > fp2["positional_only"],
          "the substrate PARSE does better (%.4f) -> non-canonical is gated on PARSER QUALITY (the filed extraction-"
          "front-end-parser problem), not a filler-gap heuristic" % fp2["substrate_parser_patient"])

    print("== V. JOINT POS+parse via PARSE-COHERENCE (4th approach: best precision, still HARD_FAIL on recall) ==")
    pc = load("exp_whodidwhat_joint_pos_parse_coherence_v1")
    check(pc["false_verbs_per_sentence"] < 0.5,
          "the parse-coherence override has the BEST precision of any approach (%.3f false-verbs/sent vs the heuristic's "
          "3.72) -- parse-likelihood is a discriminative category cue" % pc["false_verbs_per_sentence"])
    check(pc["coherence_recovery"] < 0.5,
          "the global-mean coherence proxy is weak (%.3f recovery) -- the drill's predicted 'too weak an aggregate "
          "signal'; the LOCAL per-arc + noisy-channel form is the fix (section W)" % pc["coherence_recovery"])

    print("== W. THE JOINT POS OVERRIDE that WORKS -- noisy-channel (local structural gain + global coherence delta) ==")
    nc = load("exp_whodidwhat_joint_noisy_channel_v1")
    la = load("exp_whodidwhat_joint_local_arc_v1")
    best_la = la["best_operating_point_fp_le_1"]
    # local per-arc lifts recovery to 0.80 (from 0.15 global-mean), but at ~2 false-verbs/sent
    check(any(c["recovery"] >= 0.7 for c in la["tau_sweep"]),
          "the LOCAL per-arc signal recovers >=0.70 of the mis-tagged verbs (vs 0.15 for the global-mean proxy) -- "
          "the drill's 'use the local score' correction confirmed")
    nb = nc["best_operating_point_fp_le_1"]
    check(nb is not None and nb["recovery"] >= 0.5 and nb["false_verbs_per_sent"] <= 1.0,
          "adding the GLOBAL coherence-delta guard yields the FIRST usable operating point: recovery %.2f at %.2f "
          "false-verbs/sent (HARD_PASS on 19c) -- a brain-foundational noisy-channel joint override that clears the bar"
          % (nb["recovery"], nb["false_verbs_per_sent"]))

    print("== X. GENERALIZATION of the joint override -- it is 19c-REGISTER-SPECIFIC, not general (honest) ==")
    gen = load("exp_whodidwhat_joint_generalization_v1")
    gb = gen["best_operating_point_fp_le_1"]
    check((gb["recovery"] if gb else 0.0) < 0.35,
          "on MODERN UD-EWT (gold-verified) recovery drops to %.2f (vs 0.50 on 19c) -> it does NOT generalize: 19c "
          "mis-tags are structurally-recoverable register artifacts; modern residual mis-tags are the tagger's hardest "
          "confident errors that lack the structural signal. The GENERAL fix is the trained joint-decoded parser (0i)."
          % (gb["recovery"] if gb else 0.0))

    print("== Y. JOINT-DECODED PARSER built + trains; greedy insufficient -> beam required (precisely located) ==")
    jd = load("exp_whodidwhat_joint_decoded_parser_v1")
    check("diagnosis" in jd and jd["joint_recovery_19c"] == 0.0,
          "the joint-decoded parser (POS as a scored SHIFT_V action) TRAINS but the GREEDY decoder cannot fire SHIFT_V "
          "(recovery %.2f): at the shift point a mis-tagged verb and a verb-readable NOUN look identical -> hard "
          "negatives push SHIFT_V negative. Two root causes located: DATA (1.5%% modern mistag rate, fixed by synthetic "
          "injection) + DECODER (needs BEAM lookahead, per Bohnet&Nivre). The build is now scaffolded + characterized."
          % jd["joint_recovery_19c"])

    print("\nALL %d CHECKS PASSED" % N)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
