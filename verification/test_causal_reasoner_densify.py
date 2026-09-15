"""Scaffold-free witness: LAYER 4 -- the brain-foundational UPSTREAM densification builds across the
sparsity wall (fixes the density decisively) AND the honest diagnosis of the residual wall.

  D1 DENSITY FIXED: the Trabasso contiguity+plausibility densification lifts multi-hop-chain support
     from ~3% (the live sparse reader) to the large majority of stories, and mean chain depth from ~0
     to >=2 -- the reasoner now has chains to traverse. (Additive: it does NOT touch the reader's
     connective/mental links, so nothing downstream regresses -- a new inferred-edge layer.)
  D2 HONEST RESIDUAL WALL: the associative plausibility signal is TOPICAL, not directed-causal, so on
     Story Cloze the dense reasoner does NOT beat the controls CI-separated; AND Story Cloze itself is
     AFFECT-dominated -- a topical baseline is also chance -- so it is the wrong instrument to validate
     causal-chain reasoning. The correctness of narrative causal edges needs a DIRECTED causal-knowledge
     prior (the world-knowledge wall), enumerated as the next problem.

Re-derives live from experiments.exp_causal_reasoner_densify_v1 (runs the LIVE SituationReader).
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_densify.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_densify_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    out = run(n_density=400, n_cloze=600)
    d = out["density"]
    chk("D1a densification lifts multi-hop-chain support from ~3% (sparse) to the large majority",
        d["pct_dense_multihop"] >= 60.0 and d["pct_dense_multihop"] > 5 * max(d["pct_sparse_multihop"], 0.1),
        "dense %.1f%% vs sparse %.1f%% multihop-support" % (d["pct_dense_multihop"], d["pct_sparse_multihop"]))
    chk("D1b dense mean chain depth >=2 vs sparse ~0",
        d["dense_depth_mean"] >= 2.0 and d["sparse_depth_mean"] < 1.0,
        "dense depth %.3f vs sparse %.3f" % (d["dense_depth_mean"], d["sparse_depth_mean"]))
    # D2: the honest residual wall -- Story Cloze is affect-dominated (topical also chance) and the
    # dense signal does NOT beat the controls CI-separated. This is the located sub-negative.
    ca = out["cloze_acc"]
    affect_dominated = (abs(ca["topical"] - 0.5) < 0.05 and abs(ca["dense"] - 0.5) < 0.06)
    not_cisep = not out["dense_beats_all_controls"]
    chk("D2 residual wall diagnosed: Story Cloze affect-dominated (topical~chance) + dense not CI-sep",
        affect_dominated and not_cisep,
        "dense %.4f topical %.4f twin %.4f | dense_beats_all_controls=%s" % (
            ca["dense"], ca["topical"], ca["twin"], out["dense_beats_all_controls"]))
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
