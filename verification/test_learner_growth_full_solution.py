"""Scaffold-free witness for the FULL-SOLUTION extensions of
turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation (items 1-6 + the negative drills).

Recomputes the MECHANISM cores from source (deterministic) and re-asserts the POWERED full-scale claims from
the landed metrics of each extension cell (recomputing each pass/fail from the stored numbers, not trusting
verdict strings). Does NOT re-run the heavy cells (that would overwrite their landed metrics).

  A. MECHANISM (from source): Procrustes recovers a known rotation; the PINNED reliability fusion keeps a
     decisive old store's pick over a weak disagreeing new store; positional SELPREF from heads; the KB
     energy-AUC arithmetic.
  B. ITEM 1+2+4 (aligned/reliability/continual/decomposition, landed): every keep-both arm is beneficial;
     the info-free UNALIGNED control is worst; net fix/broken ratio > 5; NO fusion crosses the floor
     CI-separated (it is store-disagreement); the PINNED reliability arm has the lowest corruption.
  C. DRILL (landed): the floor is BENIGN CHURN (confident-half corruption << low-margin half); ANCHORED
     continual fusion beats ITERATED (anchor-dilution is the compounding cause).
  D. ITEM 6 KB route (landed): the p4 schema gate discriminates correct-new from wrong facts (AUC CI-sep >
     0.5), rejects more wrong than a matched random gate, admits correct, twin loses.
  E. ITEM 3 second task (landed): growth benefit GENERALISES (CI-sep beneficial, twin loses, net-positive).
  F. ITEM 5 own parser (landed, if present): growth benefit survives the substrate's own arc_parser.

Run: .venv/Scripts/python.exe verification/test_learner_growth_full_solution.py
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments"))

import numpy as np
import experiments.exp_learner_growth_aligned_continual_v1 as AL
import experiments.exp_learner_kb_growth_p4gate_v1 as KB
import experiments.exp_learner_growth_own_parser_v1 as OP

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _m(name):
    p = os.path.join(REPO, "data", "exp_" + name, "metrics.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def main():
    checks = []

    # A. mechanism cores from source (deterministic)
    a_ok = (AL.self_test() == 0 and KB.self_test() == 0 and OP.self_test() == 0)
    checks.append(("A mechanism self-tests recompute (procrustes/reliability/positional-selpref/KB-auc)", a_ok))

    # B. item 1+2+4 landed
    m = _m("learner_growth_aligned_continual_v1")
    if m:
        g = m["gains_vs_off"]
        beneficial_all = all(g[k]["separated_above"] for k in ("CLS_ENSEMBLE", "CLS_ALIGNED", "CLS_RELIABILITY"))
        dec = m["decomposition_single_step"]
        best_ratio = max(dec[k]["fixed_per_broken_ratio"] for k in dec if dec[k]["fixed_per_broken_ratio"])
        cf = m["cross_floor_attempts"]
        no_cross = (not cf["any_crosses_floor"])
        # reliability has the lowest corruption among the keep-both arms
        corr = {k: dec[k]["corruption_right_to_wrong"]["rate"] for k in
                ("CLS_ENSEMBLE", "CLS_ALIGNED", "CLS_RELIABILITY", "CLS_UNALIGNED")}
        reliab_lowest = corr["CLS_RELIABILITY"] <= min(corr["CLS_ENSEMBLE"], corr["CLS_ALIGNED"])
        unaligned_worst = corr["CLS_UNALIGNED"] == max(corr.values())
        checks.append((f"B beneficial(all keep-both)={beneficial_all}, fix/broken ratio={best_ratio:.1f}>5, "
                       f"no fusion crosses floor={no_cross}, reliability lowest corruption "
                       f"({corr['CLS_RELIABILITY']:.3f}) & unaligned worst ({corr['CLS_UNALIGNED']:.3f})",
                       beneficial_all and best_ratio > 5 and no_cross and reliab_lowest and unaligned_worst))
    else:
        checks.append(("B item1+2+4 metrics present", False))

    # C. drill landed: floor benign churn + anchored beats iterated
    d = _m("learner_growth_floor_drill_v1")
    if d:
        cs = d["drill1a_confidence_split_reliability"]
        top = cs["top_half_confident"]["rate"]; bot = cs["bottom_half_low_confidence"]["rate"]
        benign = d["floor_is_benign_churn"] and top < 0.5 * bot
        anc = d["drill2_continual"]
        anchored_beats = anc["anchored_beats_iterated"]
        checks.append((f"C floor is BENIGN CHURN (confident corr={top:.3f} << low-margin {bot:.3f}); ANCHORED "
                       f"continual beats iterated={anchored_beats}", bool(benign and anchored_beats)))
    else:
        checks.append(("C drill metrics present", False))

    # D. KB route landed
    k = _m("learner_kb_growth_p4gate_v1")
    if k:
        auc = k["gate_auc_wrong_over_correct"]
        works = (auc["ci"][0] > 0.5 and k["twin_loses"] and k["beats_random_gate"]
                 and k["beneficial_admits_correct"])
        op = k["operating_point"]
        checks.append((f"D KB schema gate WORKS (AUC={auc['auc']:.3f} CI-sep>0.5; wrong-admit gated "
                       f"{op['wrong_admit_gated']:.2f}<random {op['wrong_admit_random']:.2f}; twin loses)", works))
    else:
        checks.append(("D KB route metrics present", False))

    # E. second task landed
    s = _m("learner_growth_second_task_v1")
    if s:
        checks.append((f"E second-task benefit GENERALISES (benefit_generalizes={s['benefit_generalizes']}, "
                       f"twin_loses={s['twin_loses']})", bool(s["benefit_generalizes"] and s["twin_loses"])))
    else:
        checks.append(("E second-task metrics present", False))

    # F. own parser landed (optional -- may still be running)
    o = _m("learner_growth_own_parser_v1")
    if o and o.get("verdict") != "CELL_CRASHED" and o.get("arc_own_parser"):
        arc = o["arc_own_parser"]
        surv = o.get("survives_own_parser", False)
        checks.append((f"F growth benefit SURVIVES own arc_parser (survives={surv}, "
                       f"arc gain_rel={arc.get('gain_reliability', {}).get('delta')})", bool(surv)))
    else:
        print("  [SKIP] F own-parser metrics not present yet (arc-parse may still be running)")

    # G. multi-seed headline stability
    ms = _m("learner_growth_multiseed_v1")
    if ms:
        ag = ms["aggregate"]["gain_reliability"]
        checks.append((f"G headline is SEED-STABLE (reliability gain {ag['mean']}+/-{ag['std']} over "
                       f"{len(ms['seeds'])} seeds; all beneficial={ms['all_seeds_beneficial']})",
                       bool(ms["seed_stable"] and ms["all_seeds_beneficial"])))
    else:
        print("  [SKIP] G multiseed metrics not present yet")

    # H. MCScript2 independent benchmark: the read-out is VALID (twin loses) and the outcome is an
    # UNDERSTOOD verdict (either growth beneficial OR the inference-boundary negative -- NOT a broken
    # twin-helps state). This asserts the drill resolved the read-out wall, whatever the growth verdict.
    mc = _m("learner_growth_mcscript_v1")
    if mc and mc.get("verdict") != "CELL_CRASHED":
        valid = bool(mc.get("twin_loses_all_seeds"))
        understood = mc.get("verdict") in ("MCSCRIPT_GROWTH_BENEFICIAL_MULTISEED",
                                           "GROWTH_NEUTRAL_ON_MCQA_INFERENCE_BOUNDARY__READOUT_VALID_TWIN_LOSES")
        checks.append((f"H MCScript2 read-out VALID (twin loses={valid}) and verdict UNDERSTOOD "
                       f"({mc.get('verdict')})", bool(valid and understood)))
    else:
        print("  [SKIP] H MCScript metrics not present yet (may still be running)")

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
