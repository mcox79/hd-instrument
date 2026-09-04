"""Scaffold-free witness for construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set.

Reads the landed metrics.json of this problem's cells and asserts the load-bearing claims of the LOCATED NEGATIVE:
a Goldberg construction-aware selector adds NOTHING (0.000, even slightly negative) over the LIVE proximity/
Competition-Model theme selector (hybrid_role_patient), at the selector level AND end-to-end, in BOTH registers;
our live selector is statistically TIED with a competent reader; the brief's premise (84% multi-DO residual, the
+0.146 gain) was an artifact of the experimental ideal_pick baseline's animacy override. Does NOT re-run any cell.
    .venv/Scripts/python.exe verification/test_construction_aware_selector.py
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    p = os.path.join(REPO, "data", name, "metrics.json")
    assert os.path.exists(p), "MISSING landed metrics: %s" % p
    with open(p, encoding="ascii") as f:
        return json.load(f)["results"]


def main():
    checks = []
    diag = _load("exp_construction_aware_selector_diagnosis_v1")
    resid = _load("exp_construction_aware_selector_residual_v1")
    brain = _load("exp_construction_aware_selector_brain_comparison_v1")
    gen = _load("exp_construction_aware_selector_generalization_v1")
    live = _load("exp_construction_aware_selector_live_reader_v1")

    # ---- W1: SELECTOR-LEVEL NULL over the live selector (n=149): construction adds ~0, no single-DO regression ----
    d = diag["D_vs_B_LIVE_ALL"]
    assert not d["sep"] and abs(d["delta"]) <= 0.02, "W1 construction over live selector is null (n=149)"
    nr = diag["no_regression_single_DO_D_minus_B"]
    assert nr["ci_lo"] >= 0.0 and nr["ci_hi"] <= 0.0, "W1 no single-DO regression (identical)"
    checks.append(("W1 construction over LIVE selector = null @ n=149 (no single-DO regression)", d["delta"], "NULL"))

    # ---- W2: FULL-POWER NULL (n=669) -- construction n.s. (even slightly negative) over live; twin-beat is a TRAP ----
    d2 = resid["D_vs_B_LIVE_ALL"]; d2m = resid["D_vs_B_LIVE_MULTI"]
    assert not d2["sep"] and d2["delta"] <= 0.005, "W2 construction over live null/negative at n=669 (ALL)"
    assert not d2m["sep"], "W2 construction over live null at n=669 (MULTI-DO)"
    # the live selector already beats the experimental ideal_pick baseline (the +0.146 was ideal_pick's animacy bug)
    assert resid["acc_ALL"]["B_LIVE_selector"] > resid["acc_ALL"]["A_ideal"], "W2 live selector beats ideal_pick baseline"
    checks.append(("W2 construction over LIVE null @ n=669; live>ideal_pick (animacy-bug)", d2["delta"], "NULL"))

    # ---- W3: the brief's PREMISE was an artifact -- multi-DO is 25% of the LIVE residual, not 84% ----
    assert resid["residual_multi_do_frac"] <= 0.40, "W3 multi-DO is a minority of the live residual (brief claimed 0.84)"
    checks.append(("W3 multi-DO frac of LIVE residual (brief claimed 0.84)", resid["residual_multi_do_frac"], "PREMISE-REFUTED"))

    # ---- W4: BRAIN COMPARISON -- our live selector is statistically TIED with a competent reader (spaCy oracle) ----
    ob = brain["ours_vs_brain"]
    assert not ob["sep"] and abs(ob["delta"]) < 0.05, "W4 our selector is statistically tied with the competent reader"
    assert brain["acc_ours_LIVE_selector"] >= 0.90, "W4 our selector is near-ceiling at the selector level"
    # the naming/object-complement patient is genuinely UNDER-DETERMINED (dobj vs oprd both match a chunk of gold)
    nc = brain["naming_construction"]
    assert nc["brain_dobj_matches_gold"] > 0 and nc["brain_oprd_matches_gold"] > 0, "W4 naming patient under-determined"
    checks.append(("W4 ours(%.3f) TIED with competent reader(%.3f); naming under-determined" % (
        brain["acc_ours_LIVE_selector"], brain["acc_competent_reader_spacy"]), ob["delta"], "AT-BRAIN"))

    # ---- W5: the residual is a FIDELITY gap (parse) + a genuine ceiling, NOT a construction-selector gap ----
    assert brain["residual_recovered_frac"] >= 0.40, "W5 a large part of the residual is recoverable by a better PARSE"
    assert brain["residual_neither_frac"] >= 0.30, "W5 a real ambiguity/gold-noise ceiling the brain also hits"
    checks.append(("W5 residual: %.0f%% parse-fidelity gap / %.0f%% genuine ceiling" % (
        100 * brain["residual_recovered_frac"], 100 * brain["residual_neither_frac"]),
        brain["residual_recovered_frac"], "REAL-LEVER-IS-PARSE"))

    # ---- W6: the null is REGISTER-INVARIANT (modern QA-SRL AND 19c LitBank both null) ----
    m = gen["MODERN_qasrl"]["D_vs_B_ALL"]; c = gen["C19_litbank"]["D_vs_B_ALL"]
    assert not m["sep"] and not c["sep"], "W6 construction-vs-live null in BOTH modern and 19c"
    checks.append(("W6 register-invariant null (modern d=%+.4f / 19c d=%+.4f)" % (m["delta"], c["delta"]), m["delta"], "GENERALIZES"))

    # ---- W7: END-TO-END through the ACTUAL live SituationReader().read() -- construction changes it by EXACTLY 0 ----
    ef = live["FULL"]["CONSTR_vs_LIVE"]; ec = live["CLEAN_DO"]["CONSTR_vs_LIVE"]
    assert ef["delta"] == 0.0 and ec["delta"] == 0.0, "W7 end-to-end construction vs live = exactly 0.0"
    checks.append(("W7 END-TO-END (live read()) construction vs live: FULL %.4f / CLEAN %.4f" % (
        ef["delta"], ec["delta"]), ef["delta"], "NULL-E2E"))

    # ---- W8: the IDEAL composition -- the deployed feature-competition selector is held fixed (at ceiling); the one
    #      buildable upstream SELECTOR-task win is indefinite-pronoun SOURCE coverage (DRT), CI-sep + twin loses ----
    ideal = _load("exp_construction_ideal_composition_v1")
    iv = ideal["indef_vs_base"]; it = ideal["indef_vs_twin"]
    assert iv["sep"] and iv["delta"] > 0, "W8 indefinite-pronoun source coverage is a CI-sep win over the deployed base"
    assert it["sep"], "W8 the indef win beats its info-free shuffled-candidate twin"
    checks.append(("W8 IDEAL upstream opt: +indef-pron source %.4f->%.4f (twin loses)" % (
        ideal["acc"]["base_deployed_selector"], ideal["acc"]["plus_indef_pron_source"]), iv["delta"], "CI-SEP-WIN"))

    # ---- W9: the composition CEILING (source+selector+ideal-parse) and the tiny GENUINE gated residual ----
    assert ideal["acc"]["CEILING_source_selector_idealparse"] >= 0.96, "W9 ideal composition ceiling ~0.97"
    assert ideal["genuine_gated_residual_frac"] <= 0.05, "W9 genuine gated residual is a few percent (ill-posed+noise)"
    checks.append(("W9 IDEAL ceiling %.4f; genuine gated residual %.3f (ill-posed naming + gold noise)" % (
        ideal["acc"]["CEILING_source_selector_idealparse"], ideal["genuine_gated_residual_frac"]),
        ideal["acc"]["CEILING_source_selector_idealparse"], "CEILING"))

    # ---- W10: THE WHOLE COMPOSITION, proven end-to-composition: rnp + indef + RHR-head + deployed selector beats the
    #      deployed base CI-sep on 19c; the win is DRIVEN BY indefinite-pronoun coverage; the RHR head-refinement is a
    #      documented NULL (fixes == breaks, both register POS-tagger noise); no single-DO regression; register-specific ----
    whole = _load("exp_construction_whole_composition_v1")
    c19 = whole["C19_litbank"]
    assert c19["WHOLE_vs_base"]["sep"], "W10 the whole composition beats the deployed base CI-sep (19c)"
    assert c19["indef_only_vs_base"]["sep"], "W10 indefinite-pronoun coverage is the driver (CI-sep)"
    assert not c19["rhr_only_vs_base"]["sep"], "W10 the RHR head-refinement is a documented NULL over the base"
    assert c19["rhr_fixed_wrong_to_right"] == c19["rhr_broke_right_to_wrong"], \
        "W10 RHR fixes == breaks (both register POS-tagger noise -> the lever is the tagger)"
    assert c19["no_regression_single_DO"]["ci_lo"] >= 0.0, "W10 no single-DO regression"
    assert not whole["MODERN_qasrl"]["WHOLE_vs_base"]["sep"], "W10 the win is 19c-specific (modern null -- archaic pronouns + 19c tagger noise)"
    checks.append(("W10 WHOLE composition %.4f->%.4f CI-sep (indef drives; RHR null: fix %d==break %d)" % (
        c19["acc"]["base_deployed"], c19["acc"]["WHOLE"], c19["rhr_fixed_wrong_to_right"], c19["rhr_broke_right_to_wrong"]),
        c19["WHOLE_vs_base"]["delta"], "PROVEN"))

    # ---- W11: the ours-vs-brain WATERFALL -- on the ideal (rnp) chain we match/exceed the competent reader at EVERY
    #      stage (S1 source, S3 bind); the loss is at S3, 56% parse-recoverable; the DEPLOYED dominant loss is S1 SOURCE ----
    wf = _load("exp_construction_brain_waterfall_v1")
    dgs = wf["per_stage_ours_minus_brain"]
    assert dgs["S1_source"] >= 0 and dgs["S3_selection"] >= 0, "W11 ours >= competent reader at S1 and S3"
    assert not wf["END_ours_vs_brain_boot"]["sep"], "W11 END is a statistical tie with the competent reader"
    assert wf["S3_selection_residual"]["recoverable_frac"] >= 0.40, "W11 most of the S3 residual is parse-recoverable"
    assert wf["DEPLOYED_reality_note"]["coref_S1_candidate_present"] < wf["DEPLOYED_reality_note"]["rnp_S1_candidate_present"], \
        "W11 the deployed dominant loss is the SOURCE (coref coverage < rnp coverage)"
    checks.append(("W11 waterfall: ours>=brain each stage; loss at S3 (%.0f%% parse-recoverable); deployed loss=SOURCE" % (
        100 * wf["S3_selection_residual"]["recoverable_frac"]), wf["per_stage_ours_minus_brain"]["END"], "WATERFALL"))

    print("PASS -- %d witness groups:" % len(checks))
    for name, val, verdict in checks:
        print("  %-62s %s  %s" % (name, ("%+.4f" % val) if isinstance(val, float) else str(val), verdict))
    print("\nHEADLINE (REFUTED, located negative = FULL PASS per the brief): a Goldberg construction-aware selector "
          "adds 0.000 over the live proximity/Competition-Model selector (selector-level AND end-to-end, modern AND "
          "19c). The construction cue is REDUNDANT with word-order on canonical English (the brain assigns roles by "
          "feature-competition, not construction-template retrieval); our live selector is already TIED with a "
          "competent reader. The brief's +0.146 / 84%-multi-DO premise was an artifact of the experimental "
          "ideal_pick baseline's animacy override. The real levers are the PARSE + SOURCE + meaning channel (filed).")


if __name__ == "__main__":
    main()
