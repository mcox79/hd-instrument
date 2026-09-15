"""Witness -- the EDGE-CORRECTNESS fix + the SOT question, on GLUCOSE cause-selection (coalition subset). Answer:
SOT = STRUCTURE-OF-TIME (causes-precede-effects) IS load-bearing (the temporal position gate beats its own
SOT-shuffled twin CI-separated), BUT incorporating SOT + directed force/psych typing + state-of-things does NOT
beat the raw TOPICAL/participant connectivity baseline (Trabasso; Collins-Loftus): directed typing HURTS, the
TemporalReasoner organ gives no lift, and the best directed+SOT+state arm stays below topical. => the
edge-correctness wall is NOT closable by the landed causal-typing/temporal organs; raw associative connectivity
is the ceiling among available signals, and the fix requires correct causal KNOWLEDGE (the meaning-channel /
knowledge foundation, Q111).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_edge_correctness_fix.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_edge_correctness_fix_v1 as F


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = F.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 SOT (Structure-of-Time, causes-precede-effects position order) IS LOAD-BEARING: the SOT-gated arm beats its own SOT-shuffled twin CI-separated",
        cs["sot_pos_vs_twin"]["ci_sep"],
        "sot_pos %.3f vs SOT-shuffled twin %.3f (%+.4f CI%s)" % (
            ov["sot_pos"], ov["twin"], cs["sot_pos_vs_twin"]["delta"], cs["sot_pos_vs_twin"]["ci"])))

    oks.append(check(
        "W2 but SOT + directed typing + state does NOT beat raw TOPICAL/participant connectivity (topical is the strongest arm; no directed/SOT/state arm CI-beats it)",
        ov["topical"] >= ov["sot_pos"] and ov["topical"] >= ov["sot_state"]
        and not cs["sot_pos_vs_topical"]["ci_sep"] and not cs["sot_state_vs_topical"]["ci_sep"],
        "topical %.3f | sot_pos %.3f (%+.4f) | sot_state %.3f (%+.4f) | best=%s" % (
            ov["topical"], ov["sot_pos"], cs["sot_pos_vs_topical"]["delta"], ov["sot_state"],
            cs["sot_state_vs_topical"]["delta"], o["best_arm"])))

    oks.append(check(
        "W3 directed force/psych causal TYPING HURTS on real narrative (net noise, CI-sep BELOW topical) -- the generated causal typing is not correct enough to help",
        cs["directed_vs_topical"]["delta"] < 0 and cs["directed_vs_topical"]["ci"][1] < 0,
        "directed %.3f vs topical %.3f (%+.4f CI%s)" % (
            ov["directed"], ov["topical"], cs["directed_vs_topical"]["delta"], cs["directed_vs_topical"]["ci"])))

    oks.append(check(
        "W4 CONCLUSION: the edge-correctness wall is not closed by the landed causal-typing/temporal organs; topical/Trabasso connectivity is the ceiling among available signals -> the fix needs correct causal KNOWLEDGE (meaning channel / foundation, Q111)",
        o["best_arm"] == "topical",
        "best arm on the coalition subset = %s (verdict %s)" % (o["best_arm"], o["verdict"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  n_coalition_subset=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), cs["n"]))
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
