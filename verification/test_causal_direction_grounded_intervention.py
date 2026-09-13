"""Witness for the GROUNDED-INTERVENTION DIRECTION prototype (the bigger lever past the ~0.61 text-store ceiling):
grounded interventional direction-recovery >> the text ceiling AND >> observation-under-confounding (twin losing),
and it lifts CAUSE SELECTION through the live causal_reasoner. Micro-world proof-of-mechanism; the grounding bridge to
real narrative remains the gap. Run: .venv/Scripts/python.exe verification/test_causal_direction_grounded_intervention.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("OMP_NUM_THREADS", "3")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (("  " + detail) if detail else ""))
    return bool(cond)


def main():
    from experiments.exp_causal_direction_grounded_intervention_v1 import run, TEXT_STORE_CEILING
    out = run(smoke=True)
    d = out["direction_recovery"]; s = out["cause_selection_via_causal_reasoner"]

    check("W1 grounded interventional direction-recovery beats the ~0.61 text-store ceiling by >=0.1",
          d["grounded_intervention"]["acc"] >= TEXT_STORE_CEILING + 0.1,
          "grounded=%.3f ceiling=%.2f (delta %+.3f)" % (d["grounded_intervention"]["acc"], TEXT_STORE_CEILING,
                                                        d["grounded_intervention"]["acc"] - TEXT_STORE_CEILING))
    check("W2 grounded beats observational (text-analog) CI-sep",
          d["paired_grounded_minus_observational"]["ci"][0] > 0,
          "paired=%s obs=%.3f" % (d["paired_grounded_minus_observational"]["ci"], d["observational_textanalog"]["acc"]))
    check("W3 grounded beats the random twin CI-sep",
          d["paired_grounded_minus_twin"]["ci"][0] > 0, "paired=%s" % d["paired_grounded_minus_twin"]["ci"])
    check("W4 observation is at/below chance under confounding (text-analog cannot orient)",
          d["observational_textanalog"]["acc"] <= 0.55, "obs=%.3f" % d["observational_textanalog"]["acc"])
    check("W5 grounded direction LIFTS cause selection through the live causal_reasoner CI-sep",
          s["paired_grounded_minus_observational"]["ci"][0] > 0,
          "grounded=%.3f obs=%.3f paired=%s" % (s["grounded"]["acc"], s["observational"]["acc"],
                                                s["paired_grounded_minus_observational"]["ci"]))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
