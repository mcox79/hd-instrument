#!/usr/bin/env python3
"""Scaffold-free witness for the GRADED-CONSUMER build on SCWS (the forward-direction confirmation).

Confirms the synthesis's FALSIFIABLE PREDICTION on human graded data (SCWS, Huang 2012, acquired by fetch_scws_v1.py):
  P1  the graded settled context-modulated vector IS sense-sensitive -- it beats the CONTEXT-FREE (unconditioned)
      vector on the polysemous slice CI-separated, AND the shuffled-context TWIN LOSES (context, not noise).
  P2  the DISCRETE taxonomic (Wu-Palmer) read is NOT helped by committing the context sense (committed does not beat
      MFS) -- the same signal that feeds the graded read is the wrong currency for the discrete type read.

Run: .venv/Scripts/python.exe verification/test_graded_consumer_scws.py
"""
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_context_modulated_scws_v1 as SCWS


def main():
    assert os.path.exists(SCWS.SCWS), "SCWS gold missing -- run experiments/fetch_scws_v1.py"
    r = SCWS.run(smoke=False)["result"]
    p1c = r["P1_graded_minus_ctxfree_POLY"]; p1t = r["P1_graded_minus_twin_POLY"]
    p2 = r["P2_discrete_committed_minus_mfs_POLY"]
    assert p1c["sep"], "graded must beat context-free on the polysemous slice CI-sep (sense-sensitive): %s" % p1c
    assert p1t["sep"], "the shuffled-context twin must LOSE (context-driven, not noise): %s" % p1t
    assert not (p2["sep"] and p2["delta"] > 0), \
        "the discrete taxonomic read must NOT be helped by committing the context sense: %s" % p2
    pa = r["rho_polysemous_slice"]
    print("WITNESS PASS")
    print("  P1 GRADED sense-sensitive: graded=%.4f vs ctxfree=%.4f (d=%s sep=%s); twin=%.4f (graded-twin sep=%s)"
          % (pa["GRADED_settled"], pa["CONTEXT_FREE"], p1c["delta"], p1c["sep"], pa["TWIN_shuffled"], p1t["sep"]))
    print("  P2 DISCRETE not-helped-by-sense: committed=%.4f vs mfs=%.4f (d=%s) -> context is the wrong currency here"
          % (pa["DISCRETE_committed_wup"], pa["DISCRETE_mfs_wup"], p2["delta"]))
    print("  => sense feeds the GRADED layer, not the discrete type layer -- CONFIRMED on human graded data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
