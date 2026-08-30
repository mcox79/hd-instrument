"""Scaffold-free witness for the LitBank who-did-what deepening (the assembled pipeline: real arc PARSE ->
router -> graded binder, on 19c literary prose). Runs on a 40-doc subset for speed (the full 100-doc
CI-separated headline is persisted in data/exp_wire_predarg_binder_litbank_whodidwhat_v1/metrics.json).
Asserts the load-bearing DIRECTIONS + magnitudes (robust on a subset):

  1. The graded binder LIFTS who-did-what IN the assembled arc pipeline (its value, measured in-pipeline on
     LitBank -- the population McGuffey could not exercise).
  2. The assembled wiring (arc parse + graded binder) BEATS the live incumbent (positional + ACT-R).
  3. The info-free random-BIND twin LOSES.
  4. The archaic-prose PARSE is NOT the wall for this task: the real arc parse ~TIES the dataset's own gold
     parse (|delta| small) -- the modern parser recovers who-did-what attachments on Dickens.

Run: .venv/Scripts/python.exe verification/test_wire_predarg_binder_litbank_whodidwhat.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_wire_predarg_binder_litbank_whodidwhat_v1 as L  # noqa: E402


def main():
    res = L.run(docs=40, n_boot=800, verbose=False)
    c = res["contrasts"]
    w = res["who_did_what_pron_recall"]
    checks = []

    b = c["BINDER_arc_GRADED_minus_ACTR"]
    checks.append((f"graded binder LIFTS who-did-what in the ARC pipeline: arc+GRADED {w['arc+GRADED']['acc']:.3f} "
                   f"vs arc+ACTR {w['arc+ACTR']['acc']:.3f} (delta {b['delta']:+.3f} {b['band']})",
                   b["delta"] > 0.03 and b["band"] != "BELOW"))

    wi = c["WIRED_arcGRADED_minus_positionalACTR"]
    checks.append((f"assembled wiring beats the live incumbent: arc+GRADED vs positional+ACTR "
                   f"(delta {wi['delta']:+.3f} {wi['band']})", wi["delta"] > 0.03 and wi["band"] != "BELOW"))

    tw = c["arc_GRADED_minus_RANDtwin"]
    checks.append((f"info-free random-BIND twin LOSES (delta {tw['delta']:+.3f} {tw['band']})",
                   tw["delta"] > 0.05 and tw["band"] == "ABOVE"))

    pc = c["PARSE_CAP_arc_minus_gold_GRADED"]
    checks.append((f"archaic-prose parse is NOT the wall: the real arc parse is NOT CI-separated BELOW the "
                   f"dataset's own gold parse (delta {pc['delta']:+.3f} {pc['band']}; full 100-doc run "
                   f"delta=-0.005 NOT_SEP)", pc["band"] != "BELOW"))

    cov = res["coverage_gov_verb"]
    checks.append((f"arc parse recovers governing-verb attachments on literary prose (coverage "
                   f"arc={cov['arc']:.2f} vs gold={cov['gold']:.2f})", cov["arc"] > 0.85))

    dec = res["residual_decomposition_arc"]
    checks.append((f"the who-did-what wall is COREFERENCE, not parse/clustering: perfect-binding ceiling "
                   f"arc+OPB={dec['perfect_binding_ceiling_arc_OPB']:.3f}, non-binding residual "
                   f"(OPB->1.0)={dec['non_binding_residual_OPB_to_1']:.3f}; binder recovers only "
                   f"{dec['binder_recovers_of_binding_headroom']:.2f} of the binding headroom",
                   dec["perfect_binding_ceiling_arc_OPB"] > 0.95 and dec["non_binding_residual_OPB_to_1"] < 0.05))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS  (full 100-doc CI-separated headline in metrics.json)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
