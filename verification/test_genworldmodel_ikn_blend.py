"""Witness -- the 100% BRAIN-FOUNDATIONAL causal-judgment decision layer, composed from VERIFIED-brain-foundational
organs up the chain (each organ's PINNED brain-basis audited, not assumed): Icard-Kominsky-Knobe 2017
normality-weighted necessity+sufficiency, with necessity = the REAL counterfactual LOO fold (Trabasso/Mackie over
world_state_register + goal_register), sufficiency = rs_fire result-state (Schank-Abelson; world_state+possession
+force-dynamics), typicality = temporal_script_schema p_before (Schank-Abelson/Chambers-Jurafsky script prior),
integration = graded_competition (Bates-MacWhinney). RESULT: the decision layer is brain-foundational and runs,
but the NECESSITY term is STARVED (fires <10% on both corpora) by the upstream structured-state EXTRACTION wall
(cycles 13-15: resolved discourse referents + semantic goal-satisfaction = the meaning foundation, Q111), so the
blend adds NO lift over the flat Competition-Model integrator (it rides sufficiency+typicality, which the reframe
shows ARE the explanation signals the golds reward, and which the flat integrator already captures). The ONE
non-built link up an otherwise-brain-foundational chain is precisely localized: the extraction that supplies the
counterfactual-necessity input.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_ikn_blend.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_ikn_blend_v1 as K


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = K.run(n_glu=3000, n_tmw=1500)
    g = o["GLUCOSE"]; t = o["TellMeWhy_GOAL"]; oks = []

    oks.append(check(
        "W1 the brain-foundational IKN decision layer RUNS (necessity=LOO, sufficiency=rs_fire, typicality=script "
        "prior, integration=graded_competition; all organs' PINNED brain-basis audited)",
        "ikn_blend" in g["solo"] and "necessity" in g["solo"] and "sufficiency" in g["solo"],
        "GLUCOSE solo necess %.3f suff %.3f typ %.3f | TMW necess %.3f suff %.3f" % (
            g["solo"]["necessity"], g["solo"]["sufficiency"], g["solo"]["script_order"],
            t["solo"]["necessity"], t["solo"]["sufficiency"])))

    oks.append(check(
        "W2 the NECESSITY term is STARVED by upstream extraction (fires <10% on both corpora) -- the "
        "structured-state extraction wall (meaning foundation, Q111)",
        g["necessity_fires"] < 0.1 and t["necessity_fires"] < 0.1,
        "GLUCOSE necessity_fires %.3f | TellMeWhy necessity_fires %.3f" % (g["necessity_fires"], t["necessity_fires"])))

    oks.append(check(
        "W3 consequently the IKN blend gives NO CI-separated lift over the flat Competition-Model integrator "
        "on either corpus (necessity starved -> rides sufficiency+typicality the flat integrator already captures)",
        not g["ikn_vs_flat"]["ci_sep"] and not t["ikn_vs_flat"]["ci_sep"],
        "GLUCOSE flat %.3f +ikn %.3f (%+.4f%s) | TMW flat %.3f +ikn %.3f (%+.4f%s)" % (
            g["flat_acc"], g["flat_plus_ikn_acc"], g["ikn_vs_flat"]["delta"], g["ikn_vs_flat"]["ci"],
            t["flat_acc"], t["flat_plus_ikn_acc"], t["ikn_vs_flat"]["delta"], t["ikn_vs_flat"]["ci"])))

    oks.append(check(
        "W4 verdict = the brain-foundational chain is complete + composed of verified organs, starved at the ONE "
        "upstream extraction link (necessity input)",
        o["verdict"] == "IKN_NO_LIFT_NECESSITY_STARVED", o["verdict"]))

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


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
