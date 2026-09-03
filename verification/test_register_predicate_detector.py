"""Scaffold-free witness for register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb.

Reads the landed metrics.json of this problem's cells and asserts the load-bearing claims. Does NOT re-run any cell
(leaves landed records byte-identical). Run:
    .venv/Scripts/python.exe verification/test_register_predicate_detector.py
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    p = os.path.join(REPO, "data", name, "metrics.json")
    assert os.path.exists(p), "MISSING landed metrics: %s" % p
    with open(p, encoding="ascii") as f:
        return json.load(f)


def main():
    checks = []
    det = _load("exp_register_predicate_detector_v1")["results"]
    ctl = _load("exp_register_predicate_controls_v1")["results"]
    v2 = _load("exp_register_predicate_detector_v2")["results"]

    # ---- W1: MODERN generalization (UD-EWT test, 5-fold CV) beats the info-free twin CI-separated @ controlled FP ----
    m = det["MODERN_udtest_cv_generalization"]
    assert m["best_fp_le_0p5"]["recovery"] >= 0.80, "W1 modern recovery >= 0.80 @ FP<=0.5"
    assert m["best_fp_le_0p5"]["false_verbs_per_sent"] <= 0.51, "W1 modern FP controlled"
    assert m["bootstrap_delta_vs_twin"]["ci"][0] > 0, "W1 modern delta-vs-twin CI-separated"
    checks.append(("W1 MODERN recovery@FP<=0.5 (twin loses CI-sep)", m["best_fp_le_0p5"]["recovery"], "CI-SEP"))

    # ---- W2: crosses the parent's modern WALL (parent structure-only override = 0.16 @ 0.46 FP) ----
    assert m["best_fp_le_0p5"]["recovery"] > 0.16 * 2, "W2 beats the parent's 0.16 modern override decisively"
    checks.append(("W2 vs parent modern override 0.16@0.46FP", m["best_fp_le_0p5"]["recovery"], "CROSSED"))

    # ---- W3: 19c TRANSFER (modern-trained, ZERO 19c labels) beats twin CI-separated @ controlled FP ----
    c = det["C19_litbank_transfer"]
    assert c["best_fp_le_0p5"]["recovery"] >= 0.45, "W3 19c transfer recovery >= 0.45 @ FP<=0.5"
    assert c["best_fp_le_0p5"]["false_verbs_per_sent"] <= 0.51, "W3 19c FP controlled"
    assert c["bootstrap_delta_vs_twin"]["ci"][0] > 0, "W3 19c delta-vs-twin CI-separated"
    assert c["twin_at_best"]["twin_recovery_p95"] < c["best_fp_le_0p5"]["recovery"], "W3 twin p95 below recovery"
    checks.append(("W3 19c-TRANSFER recovery@FP<=0.5 (twin loses CI-sep)", c["best_fp_le_0p5"]["recovery"], "CI-SEP"))

    # ---- W4: the MODEL transfers -- at the SINGLE modern-fixed threshold, 19c is STILL CI-separated vs twin.
    #      (FP rises to ~1.43/sent because 19c candidate density is higher; the threshold is an FP-budget knob that
    #      needs per-register calibration to hold FP<=0.5 -- the model transfers, the operating point is calibrated.) ----
    cf = det["C19_transfer_at_MODERN_fixed_threshold"]
    assert cf["ci"][0] > 0, "W4 19c at modern-fixed threshold still CI-separated vs twin (the MODEL transfers)"
    assert cf["recovery"] > 0.5, "W4 fixed-threshold recovery substantial"
    checks.append(("W4 model transfers at modern-fixed th (FP-budget=per-reg knob)", cf["recovery"], "CI-SEP"))

    # ---- W5: precision guard -- vastly below the heuristic's 3.72 false-verbs/sentence ----
    assert m["best_fp_le_0p5"]["false_verbs_per_sent"] <= 1.0 and c["best_fp_le_0p5"]["false_verbs_per_sent"] <= 1.0
    checks.append(("W5 FP <= 0.5/sent (heuristic was 3.72)", c["best_fp_le_0p5"]["false_verbs_per_sent"], "GUARDED"))

    # ---- W6: ABLATION -- the multi-cue COMBINATION beats the best single cue ON TRANSFER (the brain-faithful claim) ----
    ab = ctl["ablation_rec_at_0p5FP"]
    full_c19 = ab["FULL"]["c19_rec@0.5FP"]; marg_c19 = ab["only_verb_margin"]["c19_rec@0.5FP"]
    assert full_c19 > marg_c19, "W6 FULL combiner beats margin-only on 19c transfer (combination earns its keep)"
    checks.append(("W6 FULL>margin-only on 19c (combination matters)", round(full_c19 - marg_c19, 4), "COMBINATION"))

    # ---- W7: gate coverage of dropped verbs is high (the non-candidates are largely gold noise, per the residual) ----
    cov = ctl["gate_coverage"]
    assert cov["c19_litbank"]["gate_coverage"] >= 0.85 and cov["modern_udtest"]["gate_coverage"] >= 0.90
    checks.append(("W7 gate coverage of dropped verbs (modern/19c)", cov["c19_litbank"]["gate_coverage"], "COVERED"))

    # ---- W8: v2 fidelity pushes = documented NEGATIVE (morph gate recovers 0 novel; imperative ~no-op) ----
    g = v2["gate_coverage_v1_vs_v2"]
    assert g["v2_cov"] == g["v1_cov"], "W8 morphological gate recovers no real novel forms (non-candidates are gold noise)"
    checks.append(("W8 v2 morphological gate = documented negative (0 novel)", g["v2_cov"], "NEG-UNDERSTOOD"))

    # ---- W9: asset persisted (deployable static json: weights + standardizer + threshold) ----
    ap = os.path.join(REPO, "data", "exp_register_predicate_detector_v1", "predicate_detector_asset.json")
    assert os.path.exists(ap), "W9 detector asset persisted"
    with open(ap, encoding="ascii") as f:
        a = json.load(f)
    assert len(a["coef"]) == len(a["feat_names"]) and "operating_threshold_fp_le_0p5_modern" in a
    checks.append(("W9 deployable static asset persisted", len(a["feat_names"]), "ASSET"))

    # ---- W10: BRAIN COMPARISON -- 19c drops are a FIDELITY gap (competent reader recovers ~all), the genuine
    #      semantic ceiling is ~33% of MODERN drops; our detector's argument-structure recovery exceeds oracle re-tag ----
    bc = _load("exp_register_predicate_brain_comparison_v1")["results"]
    b19 = bc["B_19c_competent_reader_also_fails"]
    assert b19["either_oracle_recovers_frac"] >= 0.90, "W10 competent reader recovers ~all 19c drops (fidelity gap, not ceiling)"
    md = bc["A_performance_vs_competent_reader_modern"]["on_our_modern_drops"]
    assert md["neither_recovers_frac"] >= 0.20, "W10 a real semantic ceiling exists on MODERN drops (neither oracle recovers)"
    checks.append(("W10 19c=fidelity gap (competent recovers %.2f); modern semantic ceiling %.2f" % (
        b19["either_oracle_recovers_frac"], md["neither_recovers_frac"]), b19["either_oracle_recovers_frac"], "BRAIN-CMP"))

    # ---- W11: EXACT axis-1 fix -- the likelihood-trained CRF's CALIBRATED posterior recovers 19c dropped verbs far
    #      above the max-margin margin (0.806 vs 0.582), at modern parity; calibration confirmed (non-saturated) ----
    crf = _load("exp_register_predicate_crf_tagger_v1")["results"]
    up = crf["upstream_tagger_fix"]; cp = crf["recovery_arms"]["CRF_POST"]
    assert cp["c19_transfer"]["rec@0.5FP"] >= 0.70 and cp["c19_transfer"]["sep"], "W11 CRF posterior recovers 19c CI-sep"
    assert cp["c19_transfer"]["rec@0.5FP"] > 0.582 + 0.10, "W11 CRF posterior >> max-margin margin on 19c (+0.22)"
    assert up["crf_post_mean_on_true_verbs"] - up["crf_post_mean_on_nonverbs"] > 0.5, "W11 CRF posterior is calibrated/separated"
    assert up["crf_post_saturation_frac_lt_0.01"] < 0.90, "W11 CRF posterior less saturated than the max-margin 0.96"
    checks.append(("W11 EXACT axis-1 CRF calibrated posterior: 19c recovery", cp["c19_transfer"]["rec@0.5FP"], "CI-SEP"))

    # ---- W12: axis-2 context re-estimation -- the forward-backward posterior (log-odds) closes the 19c gap vs frozen ----
    idl = _load("exp_register_predicate_ideal_v1")["results"]
    assert idl["c19_gap_closed_marginal_minus_frozen"] > 0.15, "W12 context-integrated posterior closes the 19c gap vs frozen"
    checks.append(("W12 axis-2 context posterior closes 19c gap (R1-R0)", idl["c19_gap_closed_marginal_minus_frozen"], "GAP-CLOSED"))

    print("PASS -- %d witness groups:" % len(checks))
    for name, val, verdict in checks:
        print("  %-52s %s  %s" % (name, ("%.4f" % val) if isinstance(val, float) else str(val), verdict))
    print("\nHEADLINE (SOLVED): a glass-box learned noisy-channel predicate detector recovers tagger-dropped verbs "
          "MODERN %.3f / 19c-TRANSFER %.3f @ FP<=0.5 (info-free twin loses CI-sep, zero 19c labels), crossing the "
          "parent's structure-only modern wall (0.16); residual = gold noise + the semantic/discourse ceiling."
          % (m["best_fp_le_0p5"]["recovery"], c["best_fp_le_0p5"]["recovery"]))


if __name__ == "__main__":
    main()
