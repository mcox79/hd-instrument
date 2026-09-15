"""Witness -- the brain-mechanism probe: fusing the parser marginal (syntax) with the landed McRae thematic-fit
organ HELPS over the marginal alone but does NOT recover the two-valid slice -> the missing cue is TOP-DOWN discourse.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (mechanism probe).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_thematic_fusion.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_thematic_fusion_v1 as TF


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = TF.run(smoke=True)
    g = o["gated_recovery_absolute"]
    fus = g["fusion_marginal_x_thematicfit"]; marg = g["marginal_only (located negative baseline)"]
    twin = g["twin_random_gate"]; cls = o["recovery_by_wrongpick_class"]
    tv = cls.get("TWO_VALID", {"n": 1, "recovered_by_fusion": 0})
    tv_frac = tv["recovered_by_fusion"] / max(tv["n"], 1)

    oks.append(check("W1 thematic FIT carries signal: the syntax x fit fusion beats the marginal-alone override AND the random-gate twin",
                     fus["delta"] > marg["delta"] and fus["delta"] > twin["delta"],
                     "fusion delta %s vs marginal-only %s vs twin %s (blanket %s, fit-coverage %s)"
                     % (fus["delta"], marg["delta"], twin["delta"], o["blanket_patient_acc"], o["thematic_fit_coverage"])))
    oks.append(check("W2 but fusing the two BOTTOM-UP cues does NOT beat the strong labeled reader (still a located negative)",
                     fus["delta"] <= 0.005,
                     "fusion delta %s CI %s (overriding the labeled reader on low-marginal picks is net non-positive)" % (fus["delta"], fus["ci"])))
    oks.append(check("W3 the TWO-VALID slice is barely recovered by thematic fit (<30%) -> it needs TOP-DOWN discourse, not verb-object fit",
                     tv_frac < 0.30,
                     "two-valid recovered %d/%d (%.0f%%); rankable %s buried %s"
                     % (tv["recovered_by_fusion"], tv["n"], 100 * tv_frac, cls.get("RANKABLE"), cls.get("BURIED"))))

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


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
