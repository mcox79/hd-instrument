"""Scaffold-free witness: the LOCATED NEGATIVE -- the live reader's extracted narrative causal
network is too SPARSE for multi-hop reasoning. The reasoner is sound (Layer 1) and load-bearing
(Layer 2); the bottleneck is UPSTREAM extraction on implicit-causation narrative.

  N1 over ROCStories the reader extracts <1 causal edge/story on average, median 0.
  N2 cross-sentence edges are near-zero and the longest causal chain has median depth 0.
  N3 fewer than 10% of stories support ANY >=2-hop chain -> the multi-hop readouts have no population.

Re-derives live from experiments.exp_causal_reasoner_narrative_v1 (runs the LIVE SituationReader).
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_narrative.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_narrative_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    out = run(n=800)
    e = out["edges_per_story"]
    d = out["longest_chain_depth"]
    chk("N1 reader extracts <1 causal edge/story on average, median 0",
        e["mean"] < 1.0 and e["median"] == 0,
        "edges/story mean %.3f median %.0f max %d" % (e["mean"], e["median"], e["max"]))
    chk("N2 cross-sentence edges near-zero AND longest-chain median depth 0",
        out["cross_sentence_edges_per_story"]["mean"] < 0.3 and d["median"] == 0,
        "cross-sent/story %.3f | depth mean %.3f median %.0f max %d" % (
            out["cross_sentence_edges_per_story"]["mean"], d["mean"], d["median"], d["max"]))
    chk("N3 <10%% of stories support ANY >=2-hop chain (no population for multi-hop)",
        out["pct_stories_supporting_multihop_chain_depth>=2"] < 10.0,
        "%.1f%% support >=2-hop | verdict %s" % (
            out["pct_stories_supporting_multihop_chain_depth>=2"], out["verdict"]))
    chk("N4 verdict NETWORK_TOO_SPARSE_FOR_MULTIHOP", out["verdict"] == "NETWORK_TOO_SPARSE_FOR_MULTIHOP")
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
