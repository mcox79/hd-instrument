"""Witness -- the STRONGER brain version of the LOO mechanism (resolve cross-sentence object identity before
folding): reusing the LANDED ACT-R object-anaphora resolver (Lewis-Vasishth 2005) and a semantic-relatedness
bridging arm. Result: resolution does NOT unblock LOO -- ACT-R pronoun coref raises cross-sentence object-match
only marginally (~0.07->0.09) and neither ACT-R nor semantic bridging yields a CI-separated integrator lift. The
fair test of the stronger version rules OUT pronoun-coref as the blocker; the census cell shows the real blocker
is the physical world-state ONTOLOGY (causation is ~88% psychological/goal). Located negative, dependency named.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_loo_resolved.py
"""
from __future__ import annotations
import os, sys
import numpy as np
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_loo_resolved_v1 as R


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = R.run(n_glu=3000, n_tmw=1500)
    g = o["GLUCOSE"]["arms"]; t = o["TellMeWhy_GOAL"]["arms"]; oks = []

    oks.append(check(
        "W1 the STRONGER version RAN: ACT-R object-anaphora resolution + semantic-relatedness bridging both wired "
        "and folded (arms present, fire rates computed)",
        all(k in g for k in ("surface", "resolved", "twin", "semantic")),
        "GLUCOSE fires surf %.2f actr %.2f sem %.2f" % (g["surface"]["fires"], g["resolved"]["fires"], g["semantic"]["fires"])))

    oks.append(check(
        "W2 resolution does NOT unblock LOO: NO resolution strategy (ACT-R or semantic) yields a CI-separated "
        "integrator lift on either corpus",
        not g["resolved"]["vs_base"]["ci_sep"] and not g["semantic"]["vs_base"]["ci_sep"]
        and not t["resolved"]["vs_base"]["ci_sep"] and not t["semantic"]["vs_base"]["ci_sep"],
        "GLUCOSE actr %+.4f%s sem %+.4f%s | TMW actr %+.4f%s sem %+.4f%s" % (
            g["resolved"]["vs_base"]["delta"], g["resolved"]["vs_base"]["ci"],
            g["semantic"]["vs_base"]["delta"], g["semantic"]["vs_base"]["ci"],
            t["resolved"]["vs_base"]["delta"], t["resolved"]["vs_base"]["ci"],
            t["semantic"]["vs_base"]["delta"], t["semantic"]["vs_base"]["ci"])))

    oks.append(check(
        "W3 pronoun-coref is RULED OUT as the blocker: ACT-R raises cross-sentence object-match only marginally "
        "(< +0.1 absolute) and coverage stays low",
        (g["resolved"]["obj_match"] - g["surface"]["obj_match"]) < 0.1 and g["resolved"]["fires"] < 0.15,
        "GLUCOSE obj_match surf %.3f -> actr %.3f | fires actr %.2f" % (
            g["surface"]["obj_match"], g["resolved"]["obj_match"], g["resolved"]["fires"])))

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
