"""Scaffold-free witness: the JOINT temporal survival result GENERALIZES to MAVEN-ERE (modern Wikipedia, no LDC
caveat), at power. Uses a 120-doc subset (~50s); the full 710-doc run reproduces the same separation.

M1 event recall: incumbent tense-gated ~0.47 -> joint (tense-agnostic + copular) ~0.76 (the starve is not a TB-Dense
   artifact -- it holds on 100x-larger modern gold).
M2 whole-subgraph survival (over the transitive REDUCTION of the near-closed BEFORE graph): joint beats the incumbent
   floor CI-separated by a wide margin.
M3 the info-free TWIN loses CI-separated (here the twin is a stronger control -- denser event pool -> ~0.37, not ~0 --
   and the joint still separates above it).

Re-derives live from experiments.exp_joint_temporal_survival_maven_v1.run(ndocs=120). Requires data/benchmark_trap_check/maven_ere.
Run: .venv/Scripts/python.exe verification/test_joint_temporal_survival_maven.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_joint_temporal_survival_maven_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run(ndocs=120)
    sv = r["survival"]
    mg = r["margins"]
    chk("M1 event recall generalizes (incumbent<0.55 -> joint_cop>0.70) on modern Wikipedia",
        r["recall"]["incumbent"] < 0.55 and r["recall"]["joint_cop"] > 0.70,
        "%.3f -> %.3f" % (r["recall"]["incumbent"], r["recall"]["joint_cop"]))
    chk("M2 whole-subgraph survival: joint beats incumbent CI-separated (wide)",
        mg["joint_cop_vs_incumbent"]["ci_sep"] and mg["joint_cop_vs_incumbent"]["delta"] > 0.2,
        "%.4f->%.4f +%.4f CI%s" % (sv["incumbent"]["rate"], sv["joint_cop"]["rate"],
                                   mg["joint_cop_vs_incumbent"]["delta"], mg["joint_cop_vs_incumbent"]["ci"]))
    chk("M3 info-free TWIN loses CI-separated (stronger twin here, still separates)",
        mg["joint_cop_vs_twin"]["ci_sep"],
        "twin %.4f vs joint %.4f +%.4f CI%s" % (sv["twin"]["rate"], sv["joint_cop"]["rate"],
                                                mg["joint_cop_vs_twin"]["delta"], mg["joint_cop_vs_twin"]["ci"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
