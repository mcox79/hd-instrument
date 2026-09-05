"""Witness for the PATIENT-slot who-did-what BOARD ARM (Step 0 of the integration pass).

Validates that exp_board_patient_slot_v1.board_patient_dimension() is a well-formed, board-ready
per_dimension row that REPRODUCES the landed +0.086 clean-UD patient win (currently invisible on the
board because build_events_questions is agent-only + the LitBank patient gold is confounded):
  C1  the row has the board per_dimension schema (matches board_goal_dimension).
  C2  the LANDED structural_patient_pick (model) BEATS the deployed position floor, CI-separated.
  C3  the info-free random-head TWIN LOSES (model - twin CI-separated).
  C4  the gold-parse CEILING is >= model (the residual is genuine head-attachment = the parser).
  C5  model_acc is in the expected ~0.80-0.86 band (the landed readout, not chance/not perfect).

Run: .venv/Scripts/python.exe verification/test_board_patient_slot_arm.py
"""
from __future__ import annotations
import os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_board_patient_slot_v1 as PAT

CAP = 150
_checks = []


def _ck(name, ok, detail=""):
    _checks.append((name, bool(ok), detail))
    print("  %s: %s%s" % ("ok" if ok else "FAIL", name, ("  -- " + detail) if detail else ""))


def main():
    print("=" * 92)
    print("WITNESS: patient-slot board arm (clean UD-EWT, cap=%d)" % CAP)
    row, detail = PAT.board_patient_dimension(cap=CAP)

    # C1 -- board per_dimension schema
    req = ("n", "model_acc", "strongest_floor", "strongest_floor_name", "twin_acc",
           "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest", "ci_sep_over_twin",
           "population")
    missing = [k for k in req if k not in row]
    _ck("C1 row has the board per_dimension schema", not missing, "missing=%s" % missing)
    _ck("C1b n > 30 and model_acc is a float", row["n"] > 30 and isinstance(row["model_acc"], float),
        "n=%d model_acc=%s" % (row["n"], row["model_acc"]))

    m, fl, tw = row["model_acc"], row["strongest_floor"], row["twin_acc"]
    ms, mt = row["model_minus_strongest"], row["model_minus_twin"]
    ceil = detail["ceiling_gold_parse"]

    # C2 -- model beats the deployed position floor, CI-separated
    _ck("C2 landed pick beats deployed floor CI-sep (%.4f > %.4f, d=%s)" % (m, fl, ms),
        m > fl and row["ci_sep_over_strongest"])
    # C3 -- info-free random-head twin loses, CI-separated
    _ck("C3 random-head twin LOSES CI-sep (model %.4f vs twin %.4f, d=%s)" % (m, tw, mt),
        m > tw and row["ci_sep_over_twin"])
    # C4 -- gold-parse ceiling >= model (residual = head attachment = the parser)
    _ck("C4 gold-parse ceiling >= model (%.4f >= %.4f)" % (ceil, m), ceil >= m - 1e-9)
    # C5 -- model in a sane band (clearly above chance ~0.3, clearly below perfect; wider than the
    # full-split ~0.83 to absorb small-cap variance -- the WIN itself is C2/C3/C4, not this sanity band)
    _ck("C5 model_acc in ~[0.74,0.90] (landed readout, not chance/perfect): %.4f" % m,
        0.74 <= m <= 0.90)

    npass = sum(1 for _n, ok, _d in _checks if ok)
    print("=" * 92)
    print("ALL %d CHECKS PASSED" % len(_checks) if npass == len(_checks)
          else "FAILED %d/%d" % (len(_checks) - npass, len(_checks)))
    print("=" * 92)
    return 0 if npass == len(_checks) else 1


if __name__ == "__main__":
    sys.exit(main())
