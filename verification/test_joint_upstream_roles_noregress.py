"""Scaffold-free witness: FULL-STACK -- upstream parse UAS + the ROLE channel off the shared parse + no-regress.

U1 arc_parser UAS on UD-EWT test ~0.79 (the parse-quality number that GATES the spatial channel -- substantiates
   the located negative).
U2 the ROLE channel reads core roles (agent/patient/goal/...) off the SAME ONE parse the temporal + spatial
   channels use -- the brain-foundational joint property (one parse -> the whole local subgraph).
U3 NO-REGRESS: the joint front-end writes NOTHING to hdlab and the live SituationReader still reads intact
   (additive by construction).

Re-derives live from experiments.exp_joint_upstream_noregress_v1.run(). Requires data/corpora/ud_english_ewt + the
frontend assets + the litbank conll fixture.
Run: .venv/Scripts/python.exe verification/test_joint_upstream_roles_noregress.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible parse)

from experiments.exp_joint_upstream_noregress_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    uas = r["uas"]["uas"]
    chk("U1 arc_parser UAS ~0.79 on UD-EWT test (the spatial-channel gate)",
        uas is not None and 0.74 <= uas <= 0.84, "UAS %.4f on %d arcs" % (uas or 0, r["uas"].get("n_arcs", 0)))
    chk("U2 ROLE channel reads core roles off the shared parse",
        r["roles"]["n_fills"] >= 8, "%d core-role fills across the demo sentences" % r["roles"]["n_fills"])
    nr = r["no_regress"]
    reads = nr["live_reader_reads"]
    chk("U3 NO-REGRESS: joint front-end writes no hdlab + live reader reads intact",
        (nr["joint_frontend_touches_hdlab"] is False) and isinstance(reads, dict)
        and reads.get("ran") is True and reads.get("n_events", 0) and reads["n_events"] > 0,
        "hdlab_write=%s live_reader=%s" % (nr["joint_frontend_touches_hdlab"], reads))
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
