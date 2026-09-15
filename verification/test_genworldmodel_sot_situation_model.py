"""Witness -- SOT = the SITUATION MODEL (state-of-mind, tracks story state across sentences) is the missing
piece: conditioning cause-selection on the ACCUMULATED situation model BEATS the pairwise topical baseline on
GLUCOSE, and is LOAD-BEARING (beats its proper info-free twin). `sot_accum` = the candidate whose addition to the
running situation state contributes the most NEW effect-relevant content = the event that introduces the effect's
preconditions (Gernsbacher structure-building; Zwaan-Radvansky situation model; Kintsch construction-integration).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_sot_situation_model.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_sot_situation_model_v1 as S


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = S.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 SITUATION-MODEL conditioning BEATS pairwise topical: sot_accum (marginal contribution to the running accumulated gist) beats the topical baseline CI-separated on the coalition subset",
        cs["sot_accum_vs_topical"]["ci_sep"] and ov["sot_accum"] > ov["topical"],
        "sot_accum %.3f vs topical %.3f (%+.4f CI%s)" % (
            ov["sot_accum"], ov["topical"], cs["sot_accum_vs_topical"]["delta"], cs["sot_accum_vs_topical"]["ci"])))

    oks.append(check(
        "W2 LOAD-BEARING: sot_accum beats its PROPER info-free twin (marginal values permuted across candidates) CI-separated -- the candidate->contribution mapping carries real situation-model information",
        cs["sot_accum_vs_infofree_twin"]["ci_sep"] and ov["sot_accum"] > ov["accum_infofree_twin"],
        "sot_accum %.3f vs info-free twin %.3f (%+.4f CI%s)" % (
            ov["sot_accum"], ov["accum_infofree_twin"], cs["sot_accum_vs_infofree_twin"]["delta"],
            cs["sot_accum_vs_infofree_twin"]["ci"])))

    oks.append(check(
        "W3 the situation-model SALIENCE + FOCAL arms also beat topical CI-sep (secondary confirmation the situation model helps)",
        cs["sot_salience_vs_topical"]["ci_sep"] and cs["sot_focal_vs_topical"]["ci_sep"],
        "sot_salience %+.4f CI%s | sot_focal %+.4f CI%s" % (
            cs["sot_salience_vs_topical"]["delta"], cs["sot_salience_vs_topical"]["ci"],
            cs["sot_focal_vs_topical"]["delta"], cs["sot_focal_vs_topical"]["ci"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s  n_coalition_subset=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"], cs["n"]))
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
