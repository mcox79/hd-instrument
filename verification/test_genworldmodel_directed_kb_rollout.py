"""Witness -- SWEEP of existing directed causal-knowledge for the frontier-raising (load-bearing) lift. Result =
an honest LOCATED NEGATIVE: swapping the associative densifier for the LANDED directed causal-precedence store
(CausalKnowledgeStore, 65k CSKG ConceptNet Causes/HasPrerequisite pairs) does NOT make graph-reachability
load-bearing on TellMeWhy non-adjacent GOAL -- BOTH associative and directed-causal densification MATCH their
own same-density random-edge twin. The causal-KB beats topical CI-sep (adds reach/coverage) but not base, and not
its random twin. => existing causal-GRAPH stores do not supply the item-specific correct structure real-narrative
cause-ID needs; the load-bearing correct-structure signal we have is the RESULT-STATE achievement check (rs_fire;
world_state+possession+force-dynamics), which is coverage-bound = the result-state-schema frontier (Q111), NOT a
denser causal graph. (Stronger-impl caveat: this fires a coarse hop-decay constant; an evidence-weighted path
score, or combining the KB with the result-state channel, is the next option -- not a proof of impossibility.)

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_directed_kb_rollout.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_directed_kb_rollout_v1 as R


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = R.run(n=1500)
    a = o["associative"]; c = o["directed_causal_KB"]
    oks = []

    oks.append(check(
        "W1 associative densification is NOT load-bearing (reproduces cycle-10): does not CI-beat its random-edge twin",
        not a["vs_twin_test"]["ci_sep"],
        "assoc %.3f vs twin %.3f (%+.4f CI%s)" % (
            a["acc_test"], a["twin_acc_test"], a["vs_twin_test"]["delta"], a["vs_twin_test"]["ci"])))

    oks.append(check(
        "W2 the DIRECTED CAUSAL-KB is ALSO NOT load-bearing: does not CI-beat its random-DIRECTED twin",
        not c["vs_twin_test"]["ci_sep"],
        "causal %.3f vs twin %.3f (%+.4f CI%s)" % (
            c["acc_test"], c["twin_acc_test"], c["vs_twin_test"]["delta"], c["vs_twin_test"]["ci"])))

    oks.append(check(
        "W3 the causal-KB adds reach/COVERAGE (beats topical CI-sep) but that is not correct STRUCTURE "
        "(twin matches) -- a coverage effect, not the frontier-raising lever",
        c["vs_topical_test"]["ci_sep"],
        "causal vs topical %+.4f CI%s | vs base %+.4f CI%s" % (
            c["vs_topical_test"]["delta"], c["vs_topical_test"]["ci"],
            c["vs_base_test"]["delta"], c["vs_base_test"]["ci"])))

    oks.append(check(
        "W4 verdict: the existing causal-graph stores do not supply the load-bearing correct structure",
        o["verdict"] in ("DIRECTED_CAUSAL_KB_NO_LIFT", "DIRECTED_CAUSAL_KB_LIFTS_NOT_LOAD_BEARING")
        and not o["causal_kb_load_bearing"], o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  GOAL n=%d test n=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["n_goal"], o["n_test"]))
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
