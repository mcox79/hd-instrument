#!/usr/bin/env python3
"""Witness for LEVEL (b) influence resolution (2026-09-09) -- the net-sign resolver.

The two-tier resolver (Levins press-perturbation sign((-A^-1)[Y,X]) + magnitude-resample forward-sim) resolves the net
more/less sign at confluences/loops where pure qualitative propagation (causal_reasoner conflict->0) abstains, and
abstains honestly on the genuinely magnitude-undecidable set. Proven on controlled signed graphs (known gold net).
Cell is numpy (fast) -> witness runs full.
  RB1  full resolver beats rung-0 (conflict->0) CI-sep on the RESOLVED subset (the ladder adds signal over abstain).
  RB2  SIGN-SCRAMBLE control collapses (flip edge signs -> resolver gets the opposite sign) => uses the edge signs.
  RB3  TOPOLOGY-PERMUTE control collapses to chance => uses the graph STRUCTURE.
  RB4  the honest resolve/abstain split is present (large structural tier + a real true-abstain tier).

Run: .venv/Scripts/python.exe verification/test_causal_influence_resolution.py  (exit 0 = level-b confirmed).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_influence_resolution_v1 import run as run_b


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = run_b(smoke=False)
    rs = r["on_RESOLVED_subset"]; ts = r["tier_split"]
    n_fail += _check(rs["paired_full_minus_rung0"]["ci"][0] > 0.0,
                     "RB1 full resolver beats conflict->0 CI-sep on RESOLVED subset (full %.3f vs rung0 %.3f, paired "
                     "%+.3f CI%s)" % (rs["full"]["acc"], rs["rung0_conflict_to_0"]["acc"],
                     rs["paired_full_minus_rung0"]["delta"], rs["paired_full_minus_rung0"]["ci"]))
    n_fail += _check(rs["sign_scramble_ctrl"]["acc"] < 0.45,
                     "RB2 sign-scramble control collapses (%.3f < 0.45) => resolver uses the edge signs"
                     % rs["sign_scramble_ctrl"]["acc"])
    n_fail += _check(0.42 < rs["topology_permute_ctrl"]["acc"] < 0.58,
                     "RB3 topology-permute control at chance (%.3f) => resolver uses the STRUCTURE"
                     % rs["topology_permute_ctrl"]["acc"])
    n_fail += _check(ts["structural_pct"] > 30 and ts["abstain_pct"] > 10,
                     "RB4 honest resolve/abstain split (structural %.0f%% / magnitude %.0f%% / true-abstain %.0f%%)"
                     % (ts["structural_pct"], ts["resolved_pct"] - ts["structural_pct"], ts["abstain_pct"]))
    print("RESULT  %s (level-b resolver: resolves net sign at confluence/loops, abstains honestly on '?')"
          % ("all PASS" if n_fail == 0 else "%d FAIL" % n_fail))
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
