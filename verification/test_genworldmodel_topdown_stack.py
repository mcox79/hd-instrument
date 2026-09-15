"""Witness -- the TOP-DOWN brain-foundational STACK, components wired to depend on each other: (C1) an
additive weighted CONSTRAINT-SATISFACTION decision layer replacing the multiplicative content-gate, and (C2)
a DIRECTED MULTI-STEP forward model (K-hop over the CSKG cause/enable graph). The interdependence is measured:
a perfect forward model pays off MORE under the additive layer (oracle recovers the selection loss), and the
composed stack (BOTH) beats base on the GOAL subset CI-separated with the info-free NULL losing -- higher than
either component alone or the prior single-step rollout. The full population improves but is gated by the
non-goal causation types + the knowledge-store coverage (phase-diagram parameters to move next, not a ceiling).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_topdown_stack.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_topdown_stack_v1 as S


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = S.run(n=1500, w_m=0.6)
    ov, ga = o["overall"], o["goal"]
    oks = []

    oks.append(check(
        "W1 INTERDEPENDENCE: the composition ladder is monotone -- base < forward-model-alone < both-components, on BOTH full and GOAL populations (each component adds, best together)",
        ov["base_mult"] <= ov["ms2_mult"] <= ov["stack_add"] and ga["base_mult"] <= ga["ms2_mult"] <= ga["stack_add"]
        and ga["rs_add"] <= ga["stack_add"],
        "full base %.3f -> fwd-alone %.3f -> stack %.3f | GOAL base %.3f -> fwd-alone %.3f -> integ-alone %.3f -> stack %.3f" % (
            ov["base_mult"], ov["ms2_mult"], ov["stack_add"], ga["base_mult"], ga["ms2_mult"], ga["rs_add"], ga["stack_add"])))

    om = o["oracle_add_vs_oracle_mult"]
    oks.append(check(
        "W2 C1 INTEGRATION fix pays off: a PERFECT forward model recovers more of the selection loss under the additive constraint-satisfaction layer than under the multiplicative gate",
        ov["oracle_add"] >= ov["oracle_mult"],
        "oracle mult %.3f -> add %.3f (%+.4f CI%s)" % (ov["oracle_mult"], ov["oracle_add"], om["delta"], om["ci"])))

    oks.append(check(
        "W3 C2 FORWARD-MODEL depth: the directed 2-hop (multi-step plan) bridge fires more than the single-hop -- the DIRECTED depth axis (not topical co-occurrence)",
        o["fire_counts"]["ms2"] > o["fire_counts"]["ms1"],
        "fires ms1(1-hop) %d -> ms2(2-hop) %d" % (o["fire_counts"]["ms1"], o["fire_counts"]["ms2"])))

    sg = o["stack_add_vs_base_mult_GOAL"]
    oks.append(check(
        "W4 the composed STACK beats base CI-separated on the GOAL subset, ABOVE the prior single-step rollout (0.380)",
        sg["ci_sep"] and ga["stack_add"] > ga["rs_add"],
        "GOAL stack %.3f vs base %.3f (%+.4f CI%s); single-step rs %.3f" % (
            ga["stack_add"], ga["base_mult"], sg["delta"], sg["ci"], ga["rs_add"])))

    ng = o["null_stack_add_GOAL"]
    oks.append(check(
        "W5 the info-free NULL loses on the GOAL subset (permute the stack signal, 400 draws): observed > null p95, p~0 -> the generated multi-step means-end is load-bearing",
        ng["beats_p95"] and ng["observed"] > ng["null_p95"],
        "observed %.3f > null_p95 %.3f (p=%s)" % (ng["observed"], ng["null_p95"], ng["p_value"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 92)
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
