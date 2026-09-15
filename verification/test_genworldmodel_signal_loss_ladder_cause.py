"""Witness -- CONSOLIDATED signal-loss ladder for real-narrative cause-selection. Puts every load-bearing signal
(position, overlap/topical, result-state means_end, script-order) on one integrator instrument (no-leak split)
and measures where signal is lost. Findings: (1) the dominant signal is DATASET-DEPENDENT -- position is the
ceiling on GLUCOSE, result-state on TellMeWhy-GOAL (position useless there); (2) on GLUCOSE the semantic cues do
NOT add over position (additive integration slightly dilutes the dominant cue); (3) a large IRREDUCIBLE RESIDUAL
remains -- ~0.29 (GLUCOSE) / ~0.70 (TellMeWhy-GOAL) of gold causes are identified by NO combination of the
current signals = the deep semantic/world-knowledge gap (meaning foundation, Q111).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_signal_loss_ladder_cause.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_signal_loss_ladder_cause_v1 as L


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = L.run(n_glu=3000, n_tmw=1500)
    g = o["GLUCOSE"]; t = o["TellMeWhy_GOAL"]; oks = []

    oks.append(check(
        "W1 the dominant signal is DATASET-DEPENDENT: position is the best solo signal on GLUCOSE, result-state "
        "(means_end) on TellMeWhy-GOAL (position ~0 there)",
        g["best_signal"] == "position" and t["best_signal"] == "means_end" and t["solo"]["position"] < 0.05,
        "GLUCOSE best=%s solo=%s | TMW best=%s solo=%s" % (g["best_signal"], g["solo"], t["best_signal"], t["solo"])))

    oks.append(check(
        "W2 on GLUCOSE the semantic cues do NOT beat position: the full cumulative integrator does not exceed "
        "position-solo (ceiling == position)",
        g["ceiling"] <= g["solo"]["position"] + 1e-9,
        "GLUCOSE ceiling %.3f vs position-solo %.3f (final cumulative %.3f)" % (
            g["ceiling"], g["solo"]["position"], g["final_acc"])))

    oks.append(check(
        "W3 a large IRREDUCIBLE RESIDUAL remains on both corpora (>0.25) -- gold causes NO current signal "
        "identifies = the deep semantic/world-knowledge gap",
        g["residual_from_ceiling"] > 0.25 and t["residual_from_ceiling"] > 0.25,
        "GLUCOSE ceiling %.3f residual %.3f | TMW ceiling %.3f residual %.3f" % (
            g["ceiling"], g["residual_from_ceiling"], t["ceiling"], t["residual_from_ceiling"])))

    oks.append(check(
        "W4 on TellMeWhy-GOAL the result-state is the load-bearing rung: cumulative accuracy jumps when means_end "
        "is added (position+overlap alone near-zero)",
        t["ceiling"] >= t["solo"]["means_end"] - 1e-9 and t["solo"]["means_end"] > t["solo"]["overlap"],
        "TMW cumulative %s" % [(c["cues"][-1], c["acc"]) for c in t["cumulative"]]))

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
