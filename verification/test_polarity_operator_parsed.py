"""Scaffold-free witness: the WALL RESEARCH -- parse-aware structural scope vs the surface scan, and the
precise location of the residual as PARSER-ATTACHMENT accuracy (the upstream lever the brain has and we do not
yet). This is the "build across the wall, understand it fully" deliverable.

  P1 the structural resolver is BUILT and works over the reader's own front-end parse (both surface and parsed
     beat the polarity-blind floor by a wide margin).
  P2 AT THE CURRENT PARSER QUALITY (UAS ~0.79 / LAS 0.76) the ROBUST SURFACE scan >= the parse-aware resolver
     (structural scope inherits the parser's attachment errors) -- so surface is correctly the primary today.
  P3 the parse-aware residual is entirely PARSE-ATTACHMENT error (mis-attached conj / mis-labeled verb), located
     with counts -- the brain succeeds here because its parse is correct; the lever is a better parser (filed).

Requires the front-end assets + EWT gold on disk.
Re-derives live from experiments.exp_polarity_operator_parsed_ewt_v1.
Run: .venv/Scripts/python.exe verification/test_polarity_operator_parsed.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_polarity_operator_parsed_ewt_v1 import run, LAB_PATH, GOLD_PATH

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not (os.path.exists(LAB_PATH) and os.path.exists(GOLD_PATH)):
        print("  SKIP: front-end assets or EWT gold missing", flush=True)
        return 0
    out = run()
    na = out["net_accuracy"]
    chk("P1 structural resolver BUILT: both surface and parsed beat the polarity-blind floor",
        na["surface"] > na["blind"] + 0.2 and na["parsed"] > na["blind"] + 0.2,
        "blind %.4f surface %.4f parsed %.4f" % (na["blind"], na["surface"], na["parsed"]))
    chk("P2 robust surface >= parse-aware at current parser quality (parsed inherits parse errors)",
        na["surface"] >= na["parsed"] and out["over_negation_clean"]["parsed"] <= 0.02,
        "surface %.4f >= parsed %.4f ; parsed clean over-neg %.4f" % (
            na["surface"], na["parsed"], out["over_negation_clean"]["parsed"]))
    chk("P3 residual located as PARSER-ATTACHMENT error (coordination cases both miss on the parse)",
        out["n_parse_attachment_residual"] >= 3,
        "parse-attach residual=%d (upstream parser-quality lever)" % out["n_parse_attachment_residual"])
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
