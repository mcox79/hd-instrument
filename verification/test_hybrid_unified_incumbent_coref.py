"""Witness -- compose the unified referent with the incumbent graded-pick pool (a live coref gain?).

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain

Scaffold-free checks of the load-bearing claims (full GUM TEST he/she population, n~1240). Each check
asserts a DIRECTIONAL, CI-anchored claim, not a brittle exact number -- EXCEPT the faithfulness anchors,
which MUST reproduce the live substrate exactly (that is the whole point of the harness).

Run: .venv/Scripts/python.exe verification/test_hybrid_unified_incumbent_coref.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_hybrid_unified_incumbent_coref_gum_v1 as H


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []

    # W0: FAITHFULNESS -- the reimplemented 2x2 arms reproduce the LIVE substrate exactly.
    try:
        H.self_test()
        oks.append(check("W0 harness faithfulness (frag x incumbent == real reader; uni x isolation == real port)",
                         True, "exact reproduction on a 40-doc slice"))
    except AssertionError as e:
        oks.append(check("W0 harness faithfulness", False, str(e)))

    o = H.run()
    a = o["native_anchors"]; hd = o["HEADLINE_hybrid_vs_incumbent"]; tw = o["twin_control"]
    od = o["oracle_diagnostic"]; sw = o["phase_diagram_d_sweep_hybrid"]; pf = o["person_feature_lever"]
    x = o["twoxtwo"]["correct_lnc"]

    # W1: the audit anchors reproduce on the full population (0.5032 / ~0.4331).
    oks.append(check("W1 native anchors reproduce the audit (incumbent 0.5032, port ~0.4331)",
                     abs(a["incumbent_head_to_cluster"] - 0.5032) < 0.002 and abs(a["port_unified_isolation_dominant"] - 0.4331) < 0.003,
                     "incumbent=%.4f port=%.4f" % (a["incumbent_head_to_cluster"], a["port_unified_isolation_dominant"])))

    # W2: LOCATED NEGATIVE -- the HYBRID (unified pool -> incumbent scorer) does NOT beat the live incumbent.
    oks.append(check("W2 LOCATED NEGATIVE: hybrid does NOT beat the live incumbent CI-separated",
                     (not hd["ci_separated"]) and hd["delta"] <= 0.01,
                     "hybrid=%.4f incumbent=%.4f delta=%+.4f CI%s" % (hd["hybrid"], hd["incumbent"], hd["delta"], hd["ci"])))

    # W3: the info-free TWIN (shuffled grouping) LOSES -- so the real merges ARE load-bearing signal
    #     (the negative is 'subsumed', not 'any re-keying works').
    oks.append(check("W3 twin (shuffled grouping) LOSES CI-sep -- the unified grouping is real signal",
                     tw["twin_loses_ci_sep"] and tw["twin_acc"] < hd["hybrid"],
                     "twin=%.4f hybrid-twin=%+.4f CI%s" % (tw["twin_acc"], tw["hybrid_minus_twin"], tw["ci"])))

    # W4: ORACLE diagnostic -- even PERFECT unification does NOT beat the incumbent => SUBSUMPTION, not clustering.
    oks.append(check("W4 SUBSUMPTION: oracle (perfect unification) x incumbent does NOT beat the live incumbent",
                     (not od["ci_separated"]) and od["oracle_unified_x_incumbent"] < od["live_incumbent"] + 0.01,
                     "oracle=%.4f incumbent=%.4f delta=%+.4f" % (od["oracle_unified_x_incumbent"], od["live_incumbent"], od["oracle_minus_incumbent"])))

    # W5: MONOTONE ANTAGONISM -- unification HELPS the weak isolation scorer but HURTS the strong incumbent scorer.
    helps_iso = x["unified_x_isolation"] > x["fragmented_x_isolation"]
    hurts_inc = x["unified_x_incumbent"] < x["fragmented_x_incumbent"]
    oks.append(check("W5 antagonism: unification helps the isolation scorer but hurts the incumbent scorer",
                     helps_iso and hurts_inc,
                     "iso frag=%.4f->uni=%.4f (help); inc frag=%.4f->uni=%.4f (hurt)"
                     % (x["fragmented_x_isolation"], x["unified_x_isolation"], x["fragmented_x_incumbent"], x["unified_x_incumbent"])))

    # W6: the phase-diagram d-sweep does NOT recover the hybrid (no decay beats the incumbent on TEST).
    oks.append(check("W6 phase-diagram: no ACT-R decay d recovers the hybrid above the incumbent",
                     not sw["ci_separated"] and sw["test_at_best_d"] < sw["incumbent"] + 0.01,
                     "dev-best d=%s test=%.4f vs incumbent=%.4f" % (sw["dev_best_d"], sw["test_at_best_d"], sw["incumbent"])))

    # W7: THE LIVE GAIN (a DIFFERENT lever) -- wiring the DORMANT person-feature filter beats the live incumbent CI-sep.
    oks.append(check("W7 LIVE GAIN: person-feature filter (dormant phi_agreement_keep) beats the live incumbent CI-separated",
                     pf["ci_separated"] and pf["delta"] > 0.02,
                     "incumbent+phi=%.4f vs %.4f delta=%+.4f CI%s" % (pf["incumbent_plus_phi"], pf["live_incumbent"], pf["delta"], pf["ci"])))

    # W8: the phi gain is POLLUTION-removal -- the random-drop twin (same count, random which) LOSES CI-sep.
    oks.append(check("W8 phi removes person-feature POLLUTION not pool size (random-drop twin LOSES CI-sep)",
                     pf["twin_loses_ci_sep"] and pf["random_drop_twin"] < pf["incumbent_plus_phi"],
                     "random-drop twin=%.4f phi-twin=%+.4f CI%s" % (pf["random_drop_twin"], pf["phi_minus_twin"], pf["phi_minus_twin_ci"])))

    # W9: phi does NOT regress the named-antecedent subset (recall-safe person filter).
    nr = pf["no_regress_named"]
    oks.append(check("W9 phi no-regress on the named-antecedent subset",
                     nr["no_regress"], "incumbent=%.4f +phi=%.4f delta=%+.4f CI%s" % (nr["incumbent"], nr["incumbent_plus_phi"], nr["delta"], nr["ci"])))

    # W10: DEFINITIVE -- the phi gain reproduces on the ACTUAL EventCentralityReader (native head_to_cluster).
    rp = pf["real_reader_native"]
    oks.append(check("W10 DEFINITIVE: phi gain on the REAL EventCentralityReader (native scorer) is CI-separated",
                     rp["ci_separated"] and rp["delta"] > 0.02 and abs(rp["real_incumbent_native"] - 0.5032) < 0.002,
                     "real incumbent=%.4f +phi=%.4f delta=%+.4f CI%s" % (rp["real_incumbent_native"], rp["real_incumbent_phi_native"], rp["delta"], rp["ci"])))

    n = sum(oks)
    print("=" * 80)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 80)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
