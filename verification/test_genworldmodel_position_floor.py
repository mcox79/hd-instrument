"""Witness -- the POSITION FLOOR on GLUCOSE cause-selection (the floor cycles 6/7/8 missed). `earliest` (pick the
first story sentence; brain-foundational = causes-precede-effects iconicity + narrative primacy) is the STRONGEST
arm, and adding ANY semantic signal on top of position via additive constraint satisfaction only DEGRADES it.
=> GLUCOSE non-adjacent cause-selection is POSITION-DEGENERATE; the SOT/distinct win over topical does NOT beat
the strongest floor. A rigorous located negative that corrects the headline.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_position_floor.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_position_floor_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 `earliest` (pure position) is the STRONGEST arm on the coalition subset -- above overlap_count and "
        "every combo",
        ov["earliest"] >= max(ov[a] for a in ov) - 1e-9,
        "earliest %.3f | overlap_count %.3f early_then_ov %.3f | combos %s" % (
            ov["earliest"], ov["overlap_count"], ov["early_then_ov"],
            {k: ov[k] for k in ov if k.startswith("combo")})))

    oks.append(check(
        "W2 semantic is REDUNDANT: the best semantic arm does NOT CI-beat earliest (best_semantic <= earliest)",
        not cs["best_semantic_vs_earliest"]["ci_sep"],
        "best_semantic=%s vs earliest %+.4f CI%s" % (
            cs["best_semantic_arm"], cs["best_semantic_vs_earliest"]["delta"],
            cs["best_semantic_vs_earliest"]["ci"])))

    oks.append(check(
        "W3 adding semantic weight on top of position via additive constraint satisfaction DEGRADES it "
        "(best combo CI-sep BELOW earliest)",
        cs["best_combo_vs_earliest"]["ci"][1] < 0,
        "best_combo=%s vs earliest %+.4f CI%s" % (
            cs["best_combo"], cs["best_combo_vs_earliest"]["delta"], cs["best_combo_vs_earliest"]["ci"])))

    oks.append(check(
        "W4 verdict = POSITION_DOMINATES_SEMANTIC_REDUNDANT",
        o["verdict"] == "POSITION_DOMINATES_SEMANTIC_REDUNDANT", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  n=%d" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), cs["n"]))
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
