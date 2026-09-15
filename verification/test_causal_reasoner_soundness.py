"""Scaffold-free witness: the causal-network REASONER is SOUND and its multi-hop TRAVERSAL +
counterfactual SIMULATION are LOAD-BEARING on constructed graphs with known ground truth.

  S1 ULTIMATE CAUSE (root ancestor) recovered ~1.00; the ADJACENCY floor (immediate predecessor)
     LOSES CI-separated on the multi-hop subset (its multihop accuracy is ~0 -- the immediate
     predecessor is never the root when depth>=2); the shuffled-edge twin LOSES.
  S2 COUNTERFACTUAL NECESSITY by simulated node-removal recovered ~1.00; the 1-hop adjacency floor
     and the shuffled-edge twin both LOSE CI-separated; the null p95 is below the observed delta.
  S3 GRADED necessity reproduces the ground-truth path-strength ORDERING (PINNED Trabasso/vdB/Suh);
     mediating-cause + chain-of-consequence are definitionally exact; the general Pearl intervention
     agrees with node-removal on the boolean did-not-happen query on the large majority of probes.

Re-derives every headline live from experiments._causal_reasoner (does NOT trust the landed metrics).
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_soundness.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._causal_reasoner import CausalGraph, AdjacencyFloor
from experiments.exp_causal_reasoner_soundness_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    # --- canonical hand cases (the algorithm is correct, not just separated) ---
    chain = CausalGraph.from_edges([("r", "a"), ("a", "b"), ("b", "z")])
    chk("C0a chain ultimate cause = root (not the immediate predecessor)",
        chain.ultimate_cause("z") == "r" and AdjacencyFloor(chain).ultimate_cause("z") == "b",
        "reasoner=%s adjacency=%s" % (chain.ultimate_cause("z"), AdjacencyFloor(chain).ultimate_cause("z")))
    chk("C0b chain: every node is counterfactually necessary (removal disconnects z)",
        chain.is_necessary("a", "z") and chain.is_necessary("r", "z") and chain.is_necessary("b", "z"))
    dia = CausalGraph.from_edges([("r", "a"), ("a", "z"), ("r", "b"), ("b", "z")])
    chk("C0c diamond bypass: a is NOT necessary (removal leaves z via b); the sole root r IS",
        (not dia.is_necessary("a", "z")) and dia.is_necessary("r", "z"))
    sg = CausalGraph.from_edges([("r", "a", 1), ("a", "z", -1)])
    chk("C0d signed: promote r -> z 'less'; a disconnected node -> 'no_effect' (reachability)",
        sg.signed_effect("r", "z", 1) == "less" and sg.signed_effect("z", "r") == "no_effect")
    od = CausalGraph.from_edges([("r1", "z"), ("r2", "z"), ("q", "dead")])
    chk("C0e Halpern-Pearl ACTUAL causation: over-determined causes are actual though NOT but-for necessary",
        (not od.is_necessary("r1", "z")) and (not od.is_necessary("r2", "z"))
        and od.is_actual_cause("r1", "z") and od.is_actual_cause("r2", "z")
        and not od.is_actual_cause("q", "z"),
        "r1/r2 necessary=%s/%s actual=%s/%s ; q actual=%s" % (
            od.is_necessary("r1", "z"), od.is_necessary("r2", "z"),
            od.is_actual_cause("r1", "z"), od.is_actual_cause("r2", "z"), od.is_actual_cause("q", "z")))

    # --- population run (re-derived live) ---
    res = run(n_graphs=4000, seed=7)
    r1 = res["R1_ultimate_cause"]
    r2 = res["R2_necessity"]

    chk("S1 ultimate-cause reasoner ~1.00 AND adjacency LOSES CI-sep on multihop AND twin LOSES",
        r1["reasoner_acc"] >= 0.999
        and r1["reasoner_vs_adjacency_multihop"]["ci_sep"]
        and r1["reasoner_vs_twin_multihop"]["ci_sep"]
        and r1["adjacency_multihop_acc"] <= 0.05,
        "reasoner %.3f | adj_multihop %.3f | r-adj %s | r-twin %s" % (
            r1["reasoner_acc"], r1["adjacency_multihop_acc"],
            r1["reasoner_vs_adjacency_multihop"]["ci"], r1["reasoner_vs_twin_multihop"]["ci"]))

    chk("S2 necessity reasoner ~1.00 AND adjacency+twin both LOSE CI-sep AND delta > null p95",
        r2["reasoner_acc"] >= 0.99
        and r2["reasoner_vs_adjacency"]["ci_sep"]
        and r2["reasoner_vs_twin"]["ci_sep"]
        and r2["reasoner_vs_twin"]["delta"] > r2["null_p95_reasoner_vs_twin"],
        "reasoner %.3f | r-adj %s | r-twin %s | null_p95 %.4f" % (
            r2["reasoner_acc"], r2["reasoner_vs_adjacency"]["ci"], r2["reasoner_vs_twin"]["ci"],
            r2["null_p95_reasoner_vs_twin"]))

    r3, r4, r5 = res["R3_mediating_chain"], res["R4_graded_necessity_ordering"], res["R5_pearl_intervention"]
    chk("S3 graded ordering ~1.00 + mediating/chain definitionally exact + pearl agrees >0.85",
        r4["ordering_agreement"] >= 0.99 and r3["mediating_definitional_ok"] >= 0.999
        and r3["chain_of_consequence_ok"] >= 0.999 and r5["agreement_with_node_removal"] >= 0.85,
        "graded %.3f | mediating %.3f | chain %.3f | pearl %.3f" % (
            r4["ordering_agreement"], r3["mediating_definitional_ok"],
            r3["chain_of_consequence_ok"], r5["agreement_with_node_removal"]))

    chk("S4 overall verdict SOUND_AND_LOAD_BEARING", res["verdict"] == "SOUND_AND_LOAD_BEARING",
        res["verdict"])

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
