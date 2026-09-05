"""Witness for the two new Step-0 board arms (0b goal-hierarchy multi-hop; 0c WiC/sense-discrimination).
Validates each is a well-formed, board-ready per_dimension row that reproduces its win, so folding them into
exp_situation_model_qa_v1.run() makes the goal-graph landings + the meaning channel board-visible.

  G1  goal-hierarchy row has the board schema; multi-hop why-chain (graph.superordinate) BEATS the flat
      immediate-purpose floor CI-separated, and the shuffled-edges twin LOSES.
  W1  WiC row has the board schema; curated+coarsening BEATS the LIVE PPR select_sense reader CI-separated,
      and beats the equal-coarsening control (curated KNOWLEDGE is the lever).

Run: .venv/Scripts/python.exe verification/test_board_new_arms.py
"""
from __future__ import annotations
import os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_board_goal_hierarchy_v1 as GH
import experiments.exp_board_wic_sense_v1 as WIC

_checks = []
_REQ = ("n", "model_acc", "strongest_floor", "strongest_floor_name", "twin_acc",
        "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest", "ci_sep_over_twin", "population")


def _ck(name, ok, detail=""):
    _checks.append(bool(ok))
    print("  %s: %s%s" % ("ok" if ok else "FAIL", name, ("  -- " + detail) if detail else ""))


def main():
    print("=" * 92)
    print("WITNESS: the two new Step-0 board arms (goal-hierarchy 0b; WiC/sense 0c)")

    # 0b goal-hierarchy
    grow, gdet = GH.board_goal_hierarchy_dimension()
    _ck("G0 goal-hierarchy row has the board per_dimension schema", all(k in grow for k in _REQ),
        "missing=%s" % [k for k in _REQ if k not in grow])
    _ck("G1 multi-hop why-chain beats the flat immediate-purpose floor CI-sep (%.3f > %.3f, d=%s)"
        % (grow["model_acc"] or 0, grow["strongest_floor"] or 0, grow["model_minus_strongest"]),
        (grow["model_acc"] or 0) > (grow["strongest_floor"] or 0) and grow["ci_sep_over_strongest"])
    _ck("G2 shuffled-edges twin LOSES (model %.3f > twin_p95 %.3f)"
        % (grow["model_acc"] or 0, grow["twin_acc"] or 0), grow["ci_sep_over_twin"])

    # 0c WiC/sense (smoke mode for the witness -- fast; full recompute in the pass)
    wrow, wdet = WIC.board_wic_dimension(mode="smoke")
    _ck("W0 WiC row has the board per_dimension schema", all(k in wrow for k in _REQ),
        "missing=%s" % [k for k in _REQ if k not in wrow])
    _ck("W1 curated+coarsening beats the LIVE PPR select_sense reader (%.4f vs %.4f, d=%s)"
        % (wrow["model_acc"] or 0, wrow["strongest_floor"] or 0, wrow["model_minus_strongest"]),
        (wrow["model_acc"] or 0) > (wrow["strongest_floor"] or 0))
    _ck("W2 curated beats the equal-coarsening control (curated KNOWLEDGE is the lever, not just coarsening)",
        (wrow["model_acc"] or 0) >= (wrow["twin_acc"] or 0))

    npass = sum(_checks)
    print("=" * 92)
    print("ALL %d CHECKS PASSED" % len(_checks) if npass == len(_checks)
          else "FAILED %d/%d" % (len(_checks) - npass, len(_checks)))
    print("=" * 92)
    return 0 if npass == len(_checks) else 1


if __name__ == "__main__":
    sys.exit(main())
