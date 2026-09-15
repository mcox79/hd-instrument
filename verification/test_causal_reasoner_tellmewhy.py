"""Scaffold-free witness: the causal-network reasoner validated on DIRECTED, MODERN, NARRATIVE human
gold (TellMeWhy why-questions; the RIGHT instrument the affect-dominated Story Cloze pointed to).

  T1 MULTI-HOP TRAVERSAL LOAD-BEARING on directed human gold: on the NON-ADJACENT-cause subset (the
     cause is not the immediately-prior sentence -- exactly where a position floor must fail), the
     dense causal network finds the human-annotated cause CI-separated over the adjacency floor (0.000
     by construction), the recency floor, AND the shuffled-edge twin.
  T2 the reasoner beats a non-causal LEXICAL-overlap baseline CI-separated overall.
  T3 HONEST BOUND: overall the cause is the ADJACENT prior sentence ~70% of the time, and the
     topical-relatedness densification cannot beat that globally (its edges are not cause-correct) --
     the directed event-type gate does NOT help either (worse than topical) -> the residual is the
     directed causal-knowledge / world-knowledge wall, quantified.

Re-derives live from experiments.exp_causal_reasoner_tellmewhy_v1 (runs the LIVE reader + reasoner).
Requires data/corpora/tellmewhy (fetch: experiments/fetch_tellmewhy_v1.py).
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_tellmewhy.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_tellmewhy_v1 import run, TMW_TEST

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not os.path.exists(TMW_TEST):
        print("  SKIP: TellMeWhy not fetched (run experiments/fetch_tellmewhy_v1.py)", flush=True)
        return 0
    out = run(n=1500)
    cm = out["contrasts_multihop"]
    ca = out["contrasts_all"]
    am = out["acc_multihop"]
    chk("T1 multi-hop cause-ID load-bearing: dense beats adjacency+recency+twin CI-sep on non-adjacent causes",
        cm["dense_vs_adjacency"]["ci_sep"] and cm["dense_vs_recency"]["ci_sep"] and cm["dense_vs_twin"]["ci_sep"]
        and am["adjacency"] <= 0.01,
        "multihop n=%d | dense %.4f vs adjacency %.4f (+%.4f CI%s) vs twin %.4f (+%.4f CI%s)" % (
            cm["dense_vs_adjacency"]["n"], am["dense"], am["adjacency"], cm["dense_vs_adjacency"]["delta"],
            cm["dense_vs_adjacency"]["ci"], am["twin"], cm["dense_vs_twin"]["delta"], cm["dense_vs_twin"]["ci"]))
    chk("T2 reasoner beats a non-causal lexical-overlap baseline CI-sep overall",
        ca["dense_vs_lexical"]["ci_sep"],
        "dense %.4f vs lexical %.4f (+%.4f CI%s)" % (
            out["acc_all"]["dense"], out["acc_all"]["lexical"], ca["dense_vs_lexical"]["delta"],
            ca["dense_vs_lexical"]["ci"]))
    chk("T3 honest bound: cause is adjacency-dominated overall (topical densification not globally cause-correct)",
        out["acc_all"]["adjacency"] > out["acc_all"]["dense"] + 0.2
        and out["acc_all"]["directed"] <= out["acc_all"]["dense"] + 0.01,
        "adjacency %.4f >> dense %.4f ; directed %.4f (event-type gate does not help)" % (
            out["acc_all"]["adjacency"], out["acc_all"]["dense"], out["acc_all"]["directed"]))
    ci = out["contrasts_all"]["integrated_vs_dense"]
    cim = out["contrasts_multihop_integrated"]["integrated_vs_adjacency"]
    chk("T4 cue INTEGRATION (recency prior refined by the network) improves the readout + load-bearing on non-adjacent",
        ci["ci_sep"] and cim["ci_sep"] and out["acc_all"]["integrated"] < out["acc_all"]["adjacency"] + 0.01,
        "integrated %.4f (dense %.4f, +%.4f CI%s) ; integrated-adj(multihop) +%.4f CI%s ; ceiling=adjacency %.4f (world-knowledge wall)" % (
            out["acc_all"]["integrated"], out["acc_all"]["dense"], ci["delta"], ci["ci"],
            cim["delta"], cim["ci"], out["acc_all"]["adjacency"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
