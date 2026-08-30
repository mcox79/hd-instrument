"""Scaffold-free witness for the FULL PATIENT-TENDENCY estimator feeding the Wolff force-dynamic typer.
   problem: causation_typing_needs_a_patient_tendency_estimator

Recomputes every headline from source (no landed metrics.json trusted). Asserts:
  1. Cue ISOLATION + faithful reuse of the proven affector-magnitude term (the cell self-test).
  2. On COMBINED, the full estimator beats the lexicon-only floor (0.500) CI-separated.
  3. On COMBINED, it beats the PROVEN affector-magnitude-only floor CI-separated (the sharp floor -- the
     added terms are NOT redundant with the first term).
  4. The added terms recover the MAGNITUDE-SILENT populations: SET_A (affordance) and SET_D (directional)
     beat magnitude-only CI-separated; and -- HONESTLY -- on SET_M (magnitude present) the full estimator
     does NOT beat magnitude-only (the first term already suffices there).
  5. The info-free TWIN (cue contributions permuted across items) LOSES on COMBINED.
  6. HELD-OUT (fresh affectors/patients/cues) beats magnitude-only CI-separated (generalization).
  7. POSITIVE-CONTROL minimal pairs the estimator gets and the verb lexicon cannot (ball-vs-crate,
     down-vs-up, nudge-vs-shove); the brief's key-vs-wind is reported (a measured finer bound, not asserted).
  8. Per-term ABLATION: no single term reaches the full accuracy (the terms COMBINE) on COMBINED.

Run: .venv/Scripts/python.exe verification/test_patient_tendency_estimator.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_patient_tendency_estimator_v1 as E  # noqa: E402
from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402


def main():
    lex = build_force_lexicon()
    w = {"m": 1, "a": 1, "d": 1}
    checks = []

    # 1. cell self-test (isolation, faithful reuse, 0.5 cap, full=1.0)
    try:
        E.self_test()
        checks.append(("cue isolation + faithful reuse of proven magnitude term + 0.5 cap + full=1.0", True))
    except AssertionError as e:
        checks.append((f"cell self-test: {e}", False))

    def full(s):
        return E.acc_full(s, lex, w)

    def lexo(s):
        return E.acc_lexicon_only(s, lex)

    def mago(s):
        return E.acc_magnitude_only(s, lex)

    # 2. COMBINED beats lexicon-only CI-sep
    vs_lex = E.paired_delta_ci(E.COMBINED, full, lexo)
    checks.append((f"COMBINED full beats lexicon-only 0.500 CI-sep (delta {vs_lex['delta']:+.3f} {vs_lex['band']})",
                   vs_lex["band"] == "ABOVE"))

    # 3. COMBINED beats affector-magnitude-only CI-sep (sharp floor)
    vs_mag = E.paired_delta_ci(E.COMBINED, full, mago)
    checks.append((f"COMBINED full beats the PROVEN affector-magnitude-only CI-sep (delta {vs_mag['delta']:+.3f} "
                   f"{vs_mag['band']}; magnitude-only floor {mago(E.COMBINED):.3f})", vs_mag["band"] == "ABOVE"))

    # 4. magnitude-silent recovery + honest no-lift where magnitude present
    a_vs_mag = E.paired_delta_ci(E.SET_A, full, mago)
    d_vs_mag = E.paired_delta_ci(E.SET_D, full, mago)
    m_vs_mag = E.paired_delta_ci(E.SET_M, full, mago)
    checks.append((f"SET_A (affordance, magnitude-silent) recovers vs magnitude-only ({a_vs_mag['delta']:+.3f} "
                   f"{a_vs_mag['band']})", a_vs_mag["band"] == "ABOVE"))
    checks.append((f"SET_D (directional, magnitude-silent) recovers vs magnitude-only ({d_vs_mag['delta']:+.3f} "
                   f"{d_vs_mag['band']})", d_vs_mag["band"] == "ABOVE"))
    checks.append((f"HONEST: SET_M (magnitude present) full does NOT beat magnitude-only ({m_vs_mag['delta']:+.3f} "
                   f"{m_vs_mag['band']}) -- the proven first term already suffices there", m_vs_mag["band"] != "ABOVE"))

    # 5. info-free twin loses on COMBINED
    _, full_lo, _, _ = E.boot_ci(E.COMBINED, full)
    tw_mean, tw_p95 = E.twin_stats(E.COMBINED, lex, w)
    checks.append((f"info-free twin LOSES on COMBINED (full_lo {full_lo:.3f} > twin_p95 {tw_p95:.3f}; twin mean "
                   f"{tw_mean:.3f})", full_lo > tw_p95))

    # 6. held-out generalization vs magnitude-only
    ho_vs_mag = E.paired_delta_ci(E.HELDOUT, full, mago)
    checks.append((f"HELD-OUT beats magnitude-only CI-sep (delta {ho_vs_mag['delta']:+.3f} {ho_vs_mag['band']}; "
                   f"full {full(E.HELDOUT):.3f})", ho_vs_mag["band"] == "ABOVE"))

    # 7. positive-control minimal pairs
    from experiments._patient_tendency import type_with_full_tendency
    from experiments._force_dynamics_lexicon import force_dynamic_type
    clean = ["affordance_ball_vs_crate", "directional_down_vs_up", "magnitude_nudge_vs_shove"]
    for name in clean:
        pair = E.POS_CONTROL[name]
        full_ok = all(type_with_full_tendency(a, v, p, c, True, lex) == g for (a, v, p, c, g) in pair)
        lex_ok = all(force_dynamic_type(v, True, lex) == g for (a, v, p, c, g) in pair)
        checks.append((f"positive control {name}: estimator correct={full_ok}, lexicon correct={lex_ok}",
                       full_ok and not lex_ok))

    # 8. ablation -- no single term reaches full on COMBINED
    abl = E.ablation(E.COMBINED, lex)
    singles = max(abl["m_only"], abl["a_only"], abl["d_only"])
    checks.append((f"per-term ABLATION: best single term {singles:.3f} < full {abl['full_m+a+d+e']:.3f} "
                   f"(the terms COMBINE)", singles < abl["full_m+a+d+e"] - 1e-9))

    # 9. COMBINATION RULE is ADDITIVE (Wolff vector sum), not winner-take-all: on CONFLICT (2-vs-1 cue
    #    disagreement, minority rotating), the force-sum beats EVERY single-cue-priority rule CI-separated.
    wta_best = max(E.acc_wta(E.CONFLICT, lex, c) for c in ("m", "a", "d"))
    fs = E.acc_full(E.CONFLICT, lex, w)
    for c in ("m", "a", "d"):
        vs = E.paired_delta_ci(E.CONFLICT, lambda s: E.acc_full(s, lex, w),
                               lambda s, c=c: E.acc_wta(s, lex, c))
        checks.append((f"CONFLICT: force-sum {fs:.3f} beats single-cue-{c} WTA {E.acc_wta(E.CONFLICT, lex, c):.3f} "
                       f"CI-sep ({vs['delta']:+.3f} {vs['band']}) -> combination is ADDITIVE not WTA",
                       vs["band"] == "ABOVE"))
    checks.append((f"CONFLICT: no single-cue rule exceeds 8/12 ({wta_best:.3f}) while force-sum = {fs:.3f}",
                   wta_best <= 8.0 / 12 + 1e-9 and fs > 0.99))

    # 10. THE 4th CUE -- CAUSING vs LETTING (Talmy 1988). On SET_L the restraint-remover (letting) ENABLEs
    #     are recovered; dropping the letting cue collapses them; onset-cause instruments never fire ENABLE.
    wl = {"m": 1, "a": 1, "d": 1, "e": 1}
    sl_full = E.acc_full(E.SET_L, lex, wl)
    sl_drop = E.acc_full(E.SET_L, lex, {"m": 1, "a": 1, "d": 1, "e": 0})
    sl_lex = E.acc_lexicon_only(E.SET_L, lex)
    vs_lex_l = E.paired_delta_ci(E.SET_L, lambda s: E.acc_full(s, lex, wl), lambda s: E.acc_lexicon_only(s, lex))
    checks.append((f"LETTING (Talmy 4th cue): SET_L full {sl_full:.3f} beats lexicon-only {sl_lex:.3f} CI-sep "
                   f"({vs_lex_l['delta']:+.3f} {vs_lex_l['band']})", vs_lex_l["band"] == "ABOVE"))
    checks.append((f"LETTING is the cue that carries it: dropping the letting term collapses SET_L "
                   f"{sl_full:.3f}->{sl_drop:.3f} (lift {sl_full - sl_drop:+.3f})", sl_full - sl_drop >= 0.4))
    onset_none_enable = all(type_with_full_tendency(a, v, p, c, True, lex) != "ENABLE"
                            for (a, v, p, c) in E.ONSET_CAUSE_NEGCTRL)
    checks.append((f"ONSET-CAUSE guard: switch/trigger/lever/button are NEVER typed ENABLE (causing, not "
                   f"letting)", onset_none_enable))
    # letting cue does not perturb the validated COMBINED result (e=0 there -> drop_e identical to full)
    checks.append((f"the letting cue does NOT perturb COMBINED (drop_e {abl['drop_e']:.3f} == full "
                   f"{abl['full_m+a+d+e']:.3f})", abs(abl["drop_e"] - abl["full_m+a+d+e"]) < 1e-9))

    # 11. LEMMATIZATION -- the estimator fires on INFLECTED real-text verbs, not only base-form lemmas.
    #     Without this it abstains on 100% of real narrative (measured); this is age-INDEPENDENT.
    from experiments._patient_tendency import lemmatize_verb
    infl_ok = (lemmatize_verb("moved") == "move" and lemmatize_verb("rolled") == "roll"
               and lemmatize_verb("turned") == "turn" and lemmatize_verb("opened") == "open")
    fires_inflected = (type_with_full_tendency("nudge", "moved", "keg", [], True, lex) == "ENABLE"
                       and type_with_full_tendency("shove", "moved", "keg", [], True, lex) == "CAUSE"
                       and type_with_full_tendency("machine", "rolled", "ball", ["down", "slope"], True, lex) == "ENABLE")
    checks.append((f"LEMMATIZATION: inflected verbs lemmatize (moved->move) AND the estimator FIRES on them "
                   f"(nudge/moved/keg -> ENABLE) -- fires on real inflected text", infl_ok and fires_inflected))

    # the brief's flagship: BARE key-vs-wind is under-determined (both fall back -- honest); once the
    # construed force magnitude is stated, the estimator RESOLVES it (breeze->ENABLE, blast->CAUSE).
    dis = E.POS_CONTROL["gate_breeze_vs_blast"]
    dis_full = [type_with_full_tendency(a, v, p, c, True, lex) for (a, v, p, c, g) in dis]
    dis_ok = all(type_with_full_tendency(a, v, p, c, True, lex) == g for (a, v, p, c, g) in dis)
    checks.append((f"gate breeze-vs-blast (magnitude-disambiguated flagship): estimator={dis_full} "
                   f"gold={[g for *_, g in dis]}", dis_ok))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    kw = E.POS_CONTROL["brief_key_vs_wind_bare"]
    kw_full = [type_with_full_tendency(a, v, p, c, True, lex) for (a, v, p, c, g) in kw]
    print(f"  [INFO] brief key-vs-wind BARE: estimator={kw_full} (under-determined -> verb fallback, honest)")
    print(f"\n{npass}/{len(checks)} checks PASS  (full 40-item + held-out CI headline in "
          f"data/exp_patient_tendency_estimator_v1/metrics.json)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
