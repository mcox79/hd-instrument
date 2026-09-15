"""Scaffold-free witness: the PHASE DIAGRAM (owner insight -- density is a free knob). Separates the
two independent axes and shows CORRECTNESS is the binding one:

  P1 at r=0 (every cause is the adjacent prior event) the recency/adjacency floor is UNBEATABLE --
     the reasoner offers no advantage regardless of edge density/correctness (advantage <= ~0).
  P2 on the NON-ADJACENT-cause subset (where the adjacency floor structurally fails) the reasoner's
     accuracy EQUALS the extraction correctness c, independent of the non-adjacency rate r -- so
     density/topology alone does nothing; CORRECTNESS is the sole determinant of the reasoner's success.
  P3 the reasoner's overall advantage is monotone increasing in c and reaches ~+0.8 at (high r, c=1).

Re-derives live from experiments.exp_causal_reasoner_phase_v1.
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_phase.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_phase_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    out = run(n_narratives=500)
    g = out["grid"]
    chk("P1 at r=0 (all-adjacent causes) the adjacency floor is unbeatable (max advantage <= 0.02)",
        out["adjacency_unbeatable_at_r0"],
        "max r0 advantage = %.4f" % max(g["r0.0_c%s" % c]["advantage"] for c in (0.2, 0.5, 0.8, 1.0)))
    # P2: on the non-adjacent subset, reasoner_acc is set by CORRECTNESS c, NOT by density r:
    # (a) r-INDEPENDENT (the r=0.2 and r=0.8 rows match), and (b) TRACKS c (monotone; ~c at high c).
    na = {(g[k]["r"], g[k]["c"]): g[k]["nonadj_reasoner_acc"] for k in g}
    r_independent = all(abs(na[(0.8, c)] - na[(0.2, c)]) < 0.06 for c in (0.2, 0.5, 0.8, 1.0))
    tracks_c = (na[(0.8, 1.0)] >= 0.97 and abs(na[(0.8, 0.8)] - 0.8) < 0.06
                and na[(0.8, 0.2)] < na[(0.8, 0.5)] < na[(0.8, 0.8)] < na[(0.8, 1.0)])
    chk("P2 non-adjacent reasoner_acc set by CORRECTNESS c, NOT density r (r-independent + tracks c)",
        r_independent and tracks_c,
        "acc@r0.8 = %s ; acc@r0.2 = %s (c=[0.2,0.5,0.8,1.0])" % (
            [na[(0.8, c)] for c in (0.2, 0.5, 0.8, 1.0)], [na[(0.2, c)] for c in (0.2, 0.5, 0.8, 1.0)]))
    acc_by_c = out["reasoner_acc_by_c_at_high_r"]
    cs = ["0.2", "0.5", "0.8", "1.0"]
    monotone = all(acc_by_c[cs[i]] <= acc_by_c[cs[i + 1]] + 1e-9 for i in range(len(cs) - 1))
    chk("P3 reasoner advantage monotone in c; ~+0.8 at (high r, c=1) -> correctness is the binding axis",
        monotone and g["r0.8_c1.0"]["advantage"] >= 0.6 and out["correctness_is_the_binding_axis"],
        "acc_by_c@high_r = %s ; adv@(r0.8,c1) = %.4f" % (
            [acc_by_c[c] for c in cs], g["r0.8_c1.0"]["advantage"]))
    chk("P4 verdict PHASE_DIAGRAM_CORRECTNESS_IS_BINDING", out["verdict"] == "PHASE_DIAGRAM_CORRECTNESS_IS_BINDING")
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
