"""Witness -- the live coref gain from wiring the DORMANT person-feature filter, optimized + hardened.

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (follow-on).

Asserts the load-bearing claims of the OPTIMIZED person-feature prototype, all through the ACTUAL live
EventCentralityReader (native head_to_cluster scorer), full GUM TEST he/she population (n~1240).

Run: .venv/Scripts/python.exe verification/test_person_feature_coref_optimize.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_person_feature_coref_optimize_gum_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        P.self_test()
        oks.append(check("W0 filter=off is byte-identical to the live EventCentralityReader", True))
    except AssertionError as e:
        oks.append(check("W0 filter=off byte-identical", False, str(e)))

    o = P.run()
    v = o["variants_vs_off"]; mg = o["mechanism_by_genre"]; bk = o["no_regress_by_bucket"]

    oks.append(check("W1 LIVE GAIN: tier1 person-filter beats the live incumbent CI-separated",
                     v["tier1"]["ci_separated"] and v["tier1"]["delta_vs_off"] > 0.02,
                     "off=%.4f tier1=%.4f delta=%+.4f CI%s" % (o["test_acc"]["off"], v["tier1"]["test_acc"],
                                                               v["tier1"]["delta_vs_off"], v["tier1"]["ci"])))
    oks.append(check("W2 TIER2 (animacy from gender) is REDUNDANT with gender agreement (== tier1)",
                     abs(v["tier2"]["delta_vs_off"] - v["tier1"]["delta_vs_off"]) < 1e-6,
                     "tier1 delta=%+.4f tier2 delta=%+.4f" % (v["tier1"]["delta_vs_off"], v["tier2"]["delta_vs_off"])))
    oks.append(check("W3 random-drop TWIN does NOT beat off (removes pollution, not pool size)",
                     not v["twin"]["ci_separated"] and v["twin"]["delta_vs_off"] <= 0.001,
                     "twin=%.4f delta=%+.4f CI%s" % (v["twin"]["test_acc"], v["twin"]["delta_vs_off"], v["twin"]["ci"])))
    oks.append(check("W4 MECHANISM: first-person genres gain MORE than third-person (speaker-pollution removal)",
                     mg["first_person"]["delta"] > mg["third_person"]["delta"] and mg["first_person"]["ci_sep"],
                     "first-person=%+.4f CI%s (n=%d) vs third-person=%+.4f (n=%d)"
                     % (mg["first_person"]["delta"], mg["first_person"]["ci"], mg["first_person"]["n"],
                        mg["third_person"]["delta"], mg["third_person"]["n"])))
    oks.append(check("W5 NO-REGRESS by antecedent-distance bucket (no bucket regresses)",
                     all(b["delta"] >= -0.01 for b in bk.values()),
                     "deltas=%s" % {k: round(b["delta"], 3) for k, b in bk.items()}))

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
