"""Scaffold-free witness: the VALENCE-signed (evaluative-dimension) antonymy is the more brain-faithful mechanism and
GENERALIZES the thwart sign beyond WordNet's antonym LIST.

VA1 GENERALIZATION: on high-related OPPOSITE-VALENCE verb pairs that the symbolic WordNet/ConceptNet edge MISSES
    (abstains on, by construction), the valence dimension recovers the thwart sign at ~1.0 -- the coverage residual the
    lookup leaves, recovered by the signed axis the brain actually uses (Osgood evaluative / vmPFC valence).
VA2 the polarity-blind HUB cannot sign EITHER set (0.0) -- the sign is the evaluative axis, not the magnitude.
VA3 the two sources are COMPLEMENTARY (union covers both sets ~1.0; valence agrees with only ~half of WordNet
    antonyms because antonymy spans multiple dimensions and valence is the evaluative one) -- so the union is the organ.

Re-derives live from experiments.exp_structured_matcher_valence_antonym_v1.run(). Requires nltk WordNet + Warriner norms + hub.
Run: .venv/Scripts/python.exe verification/test_structured_matcher_valence_antonym.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_structured_matcher_valence_antonym_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    miss, cov = r["symb_miss"], r["covered"]
    chk("VA1 valence dimension GENERALIZES the thwart sign on pairs the symbolic edge misses (>=0.9)",
        miss["symbolic"] <= 0.01 and miss["valence"] >= 0.9,
        "symb-miss set: symbolic %.3f -> valence %.3f (union %.3f)" % (miss["symbolic"], miss["valence"], miss["union"]))
    chk("VA2 hub cannot sign either set (polarity-blind)",
        miss["hub"] <= 0.01 and cov["hub"] <= 0.01,
        "hub covered %.3f / symb-miss %.3f" % (cov["hub"], miss["hub"]))
    chk("VA3 sources complementary: union covers both ~1.0; valence agrees ~half of WordNet antonyms",
        cov["union"] >= 0.95 and miss["union"] >= 0.95 and 0.3 <= r["agreement_on_covered"]["rate"] <= 0.8,
        "union cov %.3f miss %.3f | valence~WordNet agreement %.3f" % (
            cov["union"], miss["union"], r["agreement_on_covered"]["rate"]))
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
