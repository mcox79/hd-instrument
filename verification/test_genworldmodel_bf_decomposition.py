"""Witness -- DECOMPOSITION of cause-selection accuracy by signal source, brain-foundational vs cheap, on the
meaningful instrument (TellMeWhy-GOAL pooled; GLUCOSE retired: position-degenerate + overlap-constructed gold).
Answers the owner's audit: NO, the chain is NOT fully brain-foundational. Of the full accuracy (over a
pick-first floor), the genuinely brain-foundational result-state contributes ~0.18; the single largest chunk is
an ASSOCIATIVE co-occurrence store (script_order ~0.35); and CHEAP non-brain-foundational proxies
(overlap/position/recency) add a further ~+0.15 CI-separated. A large residual (~0.44) is where accuracy is LOST
(no signal reaches it = the deep-explanation/world-knowledge gap). Because the GOLD itself is a crowd
best-explanation judgment (not brain-faithful), the cheap proxies partly 'win' by matching the gold's biases.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_bf_decomposition.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_bf_decomposition_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = D.run(cap=6000)
    sg = o["solo_group"]; oks = []

    oks.append(check(
        "W1 the accuracy leans MATERIALLY on CHEAP non-brain-foundational proxies (overlap/position/recency): "
        "they add a CI-separated marginal on top of brain-foundational + associative signals",
        o["cheap_marginal_over_bf_assoc"]["ci_sep"],
        "CHEAP marginal over BF+ASSOC %+.4f CI%s | ladder base %.3f -> BF %.3f -> BF+ASSOC %.3f -> ALL %.3f" % (
            o["cheap_marginal_over_bf_assoc"]["delta"], o["cheap_marginal_over_bf_assoc"]["ci"],
            o["base_pick_first"], o["cumulative"][0]["acc"], o["cumulative"][1]["acc"], o["cumulative"][2]["acc"])))

    oks.append(check(
        "W2 the genuinely brain-foundational signal (result-state) is NOT the dominant contributor -- the largest "
        "single chunk is the ASSOCIATIVE co-occurrence store (script_order solo > BF-group solo)",
        sg["ASSOC"] > sg["BF"],
        "solo BF %.3f vs ASSOC(script) %.3f vs CHEAP %.3f | full %.3f" % (sg["BF"], sg["ASSOC"], sg["CHEAP"], o["full_acc"])))

    oks.append(check(
        "W3 a large RESIDUAL remains (>0.3) -- gold causes NO signal reaches = where accuracy is LOST (deep "
        "explanation / world-knowledge gap)",
        o["residual_to_1"] > 0.3,
        "full %.3f residual %.3f" % (o["full_acc"], o["residual_to_1"])))

    oks.append(check(
        "W4 brain-foundational share of the accuracy-over-floor is a MINORITY (BF group alone recovers < half of "
        "the full lift) -> the chain is not yet fully brain-foundational",
        (sg["BF"] - o["base_pick_first"]) < 0.5 * (o["full_acc"] - o["base_pick_first"]),
        "BF-over-floor %.3f vs full-over-floor %.3f (bf_share %.3f)" % (
            sg["BF"] - o["base_pick_first"], o["full_acc"] - o["base_pick_first"], o.get("bf_share_of_full", float("nan")))))

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
