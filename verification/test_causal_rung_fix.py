#!/usr/bin/env python3
"""Witness for the rung-1 -> rung-2 causal-necessity FIX (aggressive BF audit, 2026-09-09).

Asserts, on reproducible smoke-scale runs (fixed seeds), the two load-bearing results:
  A. exp_causal_rung_exposure_v1 -- the DEPLOYED reader's operation is rung-1 and the do-simulation fix is rung-2:
     - CONFOUND: rung-1 leave-one-out names the NON-cause (acc ~0), rung-2 do-sim is correct (acc ~1), twin loses.
     - CHAIN control: rung-1 is CORRECT (its failure is specific to confounding, not general incompetence).
     - POOLED: rung-2 beats rung-1 CI-separated (paired CI lower bound > 0).
     - OVER-DETERMINATION: Halpern-Pearl AC2 (is_actual_cause) > crude but-for (is_necessary).
  B. exp_causal_necessity_bf_reader_v1 -- the composed rung-2 reader on WIQA:
     - KNOWLEDGE test (store-only graph, no given order): bf beats the info-free shuffled-store twin CI-separated
       (mined causal knowledge is load-bearing for the necessity read).
     - the rung-2 necessity decision beats the rung-1 association floor (bf_dosim > assoc).

Standalone (no pytest). Run: .venv/Scripts/python.exe verification/test_causal_rung_fix.py  (exit 0 = all PASS).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_rung_exposure_v1 import run as run_exposure
from experiments.exp_causal_necessity_bf_reader_v1 import run as run_bf_reader
from experiments.exp_causal_engine_deepening_v1 import run as run_engine


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0

    # ---- A. rung exposure (controlled, ground truth known) ----
    ex = run_exposure(smoke=True)
    cf = ex["families"]["confound"]; ch = ex["families"]["chain"]; p = ex["pooled"]; od = ex["overdetermination"]
    n_fail += _check(cf["rung1"]["acc"] < 0.25,
                     "A1 CONFOUND rung-1 leave-one-out names the NON-cause (acc=%.3f < 0.25)" % cf["rung1"]["acc"])
    n_fail += _check(cf["rung2"]["acc"] > 0.90,
                     "A2 CONFOUND rung-2 do-sim is correct (acc=%.3f > 0.90)" % cf["rung2"]["acc"])
    n_fail += _check(cf["rung2"]["acc"] - cf["twin"]["acc"] > 0.3,
                     "A3 CONFOUND rung-2 beats its info-free shuffled-graph twin (%.3f vs %.3f)"
                     % (cf["rung2"]["acc"], cf["twin"]["acc"]))
    n_fail += _check(ch["rung1"]["acc"] > 0.90,
                     "A4 CHAIN control: rung-1 IS correct when unconfounded (acc=%.3f > 0.90) -- failure is rung-specific"
                     % ch["rung1"]["acc"])
    n_fail += _check(p["paired_rung2_minus_rung1"]["ci"][0] > 0.0,
                     "A5 POOLED rung-2 beats rung-1 CI-separated (paired %+.3f CI%s)"
                     % (p["paired_rung2_minus_rung1"]["delta"], p["paired_rung2_minus_rung1"]["ci"]))
    n_fail += _check(od["is_actual_cause_AC2"]["acc"] - od["is_necessary_butfor"]["acc"] > 0.5,
                     "A6 OVER-DETERMINATION AC2 %.3f > but-for %.3f (rung-3 actual causation)"
                     % (od["is_actual_cause_AC2"]["acc"], od["is_necessary_butfor"]["acc"]))

    # ---- B. composed rung-2 reader on WIQA ----
    bf = run_bf_reader(smoke=True)
    ne = bf["necessity_effect_vs_noeffect"]; kt = bf["knowledge_test_storeonly_no_given_order"]
    n_fail += _check(kt["paired_storeonly_bf_minus_twin"]["ci"][0] > 0.0,
                     "B1 KNOWLEDGE test: store-only rung-2 beats info-free twin CI-separated (paired %+.3f CI%s) -- "
                     "mined causal knowledge is load-bearing"
                     % (kt["paired_storeonly_bf_minus_twin"]["delta"], kt["paired_storeonly_bf_minus_twin"]["ci"]))
    n_fail += _check(kt["storeonly_bf"]["acc"] > kt["storeonly_twin"]["acc"],
                     "B2 store-only bf %.3f > twin %.3f" % (kt["storeonly_bf"]["acc"], kt["storeonly_twin"]["acc"]))
    n_fail += _check(ne["bf_dosim"]["acc"] > ne["assoc"]["acc"],
                     "B3 rung-2 necessity decision beats the rung-1 association floor (%.3f > %.3f)"
                     % (ne["bf_dosim"]["acc"], ne["assoc"]["acc"]))

    # ---- C. rung-3 abduction engine deepening ----
    en = run_engine(smoke=True)
    nv = en["necessity_vs_gold"]
    n_fail += _check(nv["abductive_fix"]["acc"] > 0.98,
                     "C1 abductive (rung-3) matches independent gold (acc=%.3f > 0.98)" % nv["abductive_fix"]["acc"])
    n_fail += _check(nv["paired_abductive_minus_fixed"]["ci"][0] > 0.0,
                     "C2 abduction beats the current fixed-root engine CI-separated (paired %+.3f CI%s; current engine "
                     "wrong on %.1f%% of evidence-conditioned counterfactuals)"
                     % (nv["paired_abductive_minus_fixed"]["delta"], nv["paired_abductive_minus_fixed"]["ci"],
                        100 * en["frac_where_current_engine_wrong"]))
    n_fail += _check(nv["paired_abductive_minus_twin"]["ci"][0] > 0.0,
                     "C3 abduction beats its info-free shuffled-graph twin CI-separated (paired %+.3f CI%s)"
                     % (nv["paired_abductive_minus_twin"]["delta"], nv["paired_abductive_minus_twin"]["ci"]))

    print("RESULT  %s" % ("all PASS" if n_fail == 0 else "%d FAIL" % n_fail))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
