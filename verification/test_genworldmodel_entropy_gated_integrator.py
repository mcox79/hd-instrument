"""Witness -- the ENTROPY ORGAN wired into the Competition-Model integrator (validity x per-item availability).
HONEST result, consistent with graded_competition's own MAP-optimality theorem ("cannot beat its own argmax on
accuracy; its value is the distribution/uncertainty, not the point estimate"): the entropy AVAILABILITY GATE
gives NO accuracy lift (neutral on TellMeWhy, slightly hurts GLUCOSE) -- because net_activation already zeroes an
absent cue, so an explicit gate is redundant. BUT the organ's ACTUAL value holds: the integrated
maintained-distribution entropy is a VALID gold-free CONFIDENCE signal -- CI-separated HIGHER on the items the
integrator gets wrong, on BOTH corpora. Correct use = uncertainty/abstention, not an accuracy gate.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_entropy_gated_integrator.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_entropy_gated_integrator_v1 as E


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = E.run(n_glu=3000, n_tmw=1500)
    glu = o["GLUCOSE"]; tmw = o["TellMeWhy"]
    oks = []

    oks.append(check(
        "W1 the entropy AVAILABILITY GATE gives NO accuracy lift on either corpus (net_activation already handles "
        "cue availability) -- consistent with the graded_competition MAP-optimality theorem",
        not glu["gated_vs_static"]["ci_sep"] and not tmw["gated_vs_static"]["ci_sep"],
        "GLUCOSE gate vs static %+.4f CI%s | TellMeWhy %+.4f CI%s" % (
            glu["gated_vs_static"]["delta"], glu["gated_vs_static"]["ci"],
            tmw["gated_vs_static"]["delta"], tmw["gated_vs_static"]["ci"])))

    oks.append(check(
        "W2 the entropy organ's ACTUAL value HOLDS: integrated entropy is a valid gold-free CONFIDENCE signal -- "
        "CI-sep HIGHER on error items than correct, on BOTH corpora",
        glu["entropy_error_gap"]["ci_sep"] and tmw["entropy_error_gap"]["ci_sep"],
        "GLUCOSE ent err/cor %.3f/%.3f gap %+.4f CI%s | TellMeWhy %.3f/%.3f gap %+.4f CI%s" % (
            glu["entropy_on_error"], glu["entropy_on_correct"], glu["entropy_error_gap"]["delta"], glu["entropy_error_gap"]["ci"],
            tmw["entropy_on_error"], tmw["entropy_on_correct"], tmw["entropy_error_gap"]["delta"], tmw["entropy_error_gap"]["ci"])))

    oks.append(check(
        "W3 the static integrator's synergy is preserved (the gate does not break Prototype A's win over the best "
        "single cue on TellMeWhy)",
        tmw["static_vs_best_cue"]["ci_sep"],
        "TellMeWhy static vs best_cue %+.4f CI%s" % (
            tmw["static_vs_best_cue"]["delta"], tmw["static_vs_best_cue"]["ci"])))

    oks.append(check(
        "W4 verdict = no accuracy lift but valid confidence signal",
        o["verdict"] == "ENTROPY_NO_ACCURACY_LIFT_BUT_VALID_CONFIDENCE_SIGNAL", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"]))
    print("=" * 92)
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
