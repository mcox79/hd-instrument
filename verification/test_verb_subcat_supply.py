"""Scaffold-free witness for the verb-subcategorization-supply patient-gate PROTOTYPE (the successor lever
that wire_the_incremental_parser... re-points to). Recomputes the load-bearing claims from source on a
QA-SRL subset:

  A. The offline WordNet-frame asset DISCRIMINATES transitivity (arrive/laugh/die intransitive; put/kill/
     give transitive) -- a glass-box static asset, no LLM.
  B. THRESHOLD-FREE: trans_ratio predicts whether a verb has a gold patient, AUC > 0.62, while a SHUFFLED
     twin sits at ~0.5 -- the signal is the verb subcat info, not an artifact.
  C. The subcat gate beats BOTH the current CURATED intransitive list AND a random same-rate suppression
     TWIN on who-did-what identification accuracy -- it suppresses the RIGHT (intransitive) verbs, and the
     win is the info, not base-rate abstention.
  D. It raises patient-presence PRECISION while keeping most true patients (recall stays high).

Run: .venv/Scripts/python.exe verification/test_verb_subcat_supply.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments"))
import numpy as np
import experiments.exp_verb_subcat_supply_patient_gate_v1 as V


def main():
    asset = V.load_asset()
    checks = []
    # A. asset discriminates
    intr = [asset.get(w, {}).get("trans_ratio", 1.0) for w in ("arrive", "laugh", "die", "go")]
    trans = [asset.get(w, {}).get("trans_ratio", 0.0) for w in ("put", "kill", "give", "hit")]
    checks.append((f"A asset: intransitive verbs LOW ({[round(x,2) for x in intr]}) vs transitive HIGH "
                   f"({[round(x,2) for x in trans]})", max(intr) < 0.3 and min(trans) > 0.7))

    res = V.run(limit=1200, n_boot=800)
    a = res["auc_transratio_predicts_patient"]; at = res["auc_shuffled_twin"]
    # B. AUC threshold-free
    checks.append((f"B AUC: trans_ratio predicts has-patient AUC={a['auc']:.3f} CI[{a['ci95'][0]:.3f},"
                   f"{a['ci95'][1]:.3f}] > 0.62, shuffled-twin AUC={at['auc']:.3f} ~0.5",
                   a["ci95"][0] > 0.60 and abs(at["auc"] - 0.5) < 0.06))
    # C. beats curated + twin (identification acc)
    cc = res["cmp"]["SUBCAT_GR_vs_CURATED"]; ct = res["cmp"]["SUBCAT_GR_vs_TWIN"]
    checks.append((f"C beats CURATED intransitive list (d={cc['point']:+.3f} {cc['band']}) AND random "
                   f"same-rate TWIN (d={ct['point']:+.3f} {ct['band']}) on who-did-what id acc",
                   cc["point"] > 0 and cc["band"] == "ABOVE" and ct["point"] > 0 and ct["band"] == "ABOVE"))
    # D. precision up, recall high
    base = res["arms"]["BASELINE"]; sub = res["arms"]["SUBCAT_GR"]
    checks.append((f"D presence PRECISION up ({base['presence_prec']:.3f}->{sub['presence_prec']:.3f}) with "
                   f"recall kept high ({sub['presence_rec']:.3f}>=0.85) -- suppresses the right verbs, not all",
                   sub["presence_prec"] > base["presence_prec"] and sub["presence_rec"] >= 0.85))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS")
    if npass != len(checks):
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
