"""Scaffold-free witness for the_reader_has_no_copular_is_a_binding_schema.

Recomputes every headline in memory by driving the glass-box extractors directly (imports the experiment
cells' run() functions, which return dicts and write NOTHING to the landed data dirs). No landed cell is
re-run in place. NO external LLM. Deterministic.

  W1  base is-a/attribute binding READ-BACK beats the most-recent-noun FLOOR CI-separated (the bar's core).
  W2  base read-back beats the info-free SHUFFLE twin CI-separated (the twin LOSES).
  W3  PROCESS MAP: detection is the dominant capability loss (detected < gold; binding ~lossless given detect).
  W4  capability-loss GRADIENT by Higgins type: identity < is-a < adjectival (the weak point is identity).
  W5  THE FIX (label-robust copula-anchored detection) raises read-back recall CI-separated over base.
  W6  the FIX beats its own SHUFFLE twin CI-separated (recall AND precision).
  W7  the FIX recovers the IDENTITY weak point the most (largest per-type gain).
  W8  the glass-box Higgins TYPE classifier (surface cues) is accurate (> 0.90 coarse).
  W9  REGISTER-INDEPENDENCE: the fix works on BOTH modern and archaic controlled sets (fix >= base each).
  W10 NO-REGRESSION: state_register self-test passes AND the typed binding feeds it + round-trips a read-back.
Run: .venv/Scripts/python.exe verification/test_copular_is_a_binding_organ.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_copular_is_a_binding_readout_v1 as E1
import experiments.exp_copular_is_a_binding_register_and_noregress_v1 as E2

FAILS = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    res = E1.run(cap=None, n_boot=1500)                 # full UD-EWT gold cop clauses, in memory
    b = res["bind"]; f = res["fix"]; pt = res["per_type"]

    d_floor = res["bind_vs_floor_recall"]
    check("W1 base read-back beats most-recent-noun FLOOR CI-sep",
          d_floor["CI_sep"] and d_floor["delta"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_floor["delta"], d_floor["lo"], d_floor["hi"]))

    d_twin = res["bind_vs_twin_recall"]
    check("W2 base read-back beats info-free SHUFFLE twin CI-sep",
          d_twin["CI_sep"] and d_twin["delta"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_twin["delta"], d_twin["lo"], d_twin["hi"]))

    sm = res["stage_map"]
    gold, det, bound = sm["0_gold_clause"], sm["1_detected_predicate"], sm["2_bound_holder"]
    check("W3 process map: DETECTION is the dominant loss (detected<gold; binding~lossless)",
          det < gold and bound >= 0.90 * det,
          "gold=%d detected=%d bound=%d (bound/detect=%.3f)" % (gold, det, bound, bound / max(det, 1)))

    check("W4 capability-loss gradient: identity < is-a < adjectival",
          pt["ident"]["bind_recall"] < pt["pred_nom"]["bind_recall"] < pt["pred_adj"]["bind_recall"],
          "adj=%.3f nom=%.3f ident=%.3f" % (pt["pred_adj"]["bind_recall"], pt["pred_nom"]["bind_recall"],
                                            pt["ident"]["bind_recall"]))

    fb = res["fix_vs_bind_recall"]
    check("W5 THE FIX raises read-back recall CI-sep over base", fb["CI_sep"] and fb["delta"] > 0,
          "recall %.4f->%.4f d=%+.4f CI[%+.4f,%+.4f]" % (b["recall"], f["recall"], fb["delta"], fb["lo"], fb["hi"]))

    ft = res["fix_vs_twin_recall"]; fp = res["fix_vs_twin_precision"]
    check("W6 the FIX beats its SHUFFLE twin CI-sep (recall AND precision)",
          ft["CI_sep"] and fp["CI_sep"],
          "recall d=%+.4f prec d=%+.4f" % (ft["delta"], fp["delta"]))

    gains = {t: pt[t]["fix_recall"] - pt[t]["bind_recall"] for t in ("pred_adj", "pred_nom", "ident")}
    check("W7 the FIX recovers the IDENTITY weak point the most",
          gains["ident"] == max(gains.values()) and gains["ident"] > 0,
          "gains adj=%+.3f nom=%+.3f ident=%+.3f" % (gains["pred_adj"], gains["pred_nom"], gains["ident"]))

    check("W8 glass-box Higgins TYPE classifier accurate (>0.90 coarse)",
          res["type_classifier_acc"] > 0.90, "acc=%.4f" % res["type_classifier_acc"])

    r = E2.run()
    mod, arc = r["modern"], r["archaic"]
    check("W9 register-INDEPENDENCE: fix works on BOTH modern and archaic (fix>=base each)",
          mod["fix_recall"] >= mod["base_recall"] and arc["fix_recall"] >= arc["base_recall"]
          and arc["fix_recall"] > 0.5,
          "modern %.3f->%.3f  archaic %.3f->%.3f" % (mod["base_recall"], mod["fix_recall"],
                                                     arc["base_recall"], arc["fix_recall"]))

    nr = r["no_regression"]
    check("W10 NO-REGRESSION: state_register self-test passes AND typed binding composes+round-trips",
          nr["state_register_selftest"] == "PASS" and nr["compose_ok"] is True,
          "selftest=%s compose=%s readback_state_at=%s" % (nr["state_register_selftest"], nr["compose_ok"],
                                                           nr["readback_state_at"]))

    print("\n==== WITNESS: %d/%d ====" % (10 - len(FAILS), 10))
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
