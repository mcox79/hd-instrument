"""Witness for the science-slice GROUNDING BRIDGE prototype (option a): a runnable grounded physical model queried by
simulated do() BEATS the text-mined store on necessity (grounded > text), but -- held to the same control battery as the
store -- TIES the density-matched topology twin on the (direction-insensitive) necessity axis and the sign-scrambled
twin on the 3-way at loose coverage. An honest located result: grounded simulation > text; the clean grounded win needs
the passage-context gate (causal_sign_channel, landed) + a direction-sensitive instrument WIQA does not provide.
Run: .venv/Scripts/python.exe verification/test_causal_bridge_science_slice.py
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
    from experiments.exp_causal_bridge_science_slice_v1 import run
    o = run(smoke=True)
    ne = o["necessity_effect_vs_noeffect_on_covered"]; tw = o["three_way_with_sign_on_covered"]
    # NOTE: CI-separation of grounded-store is the FULL-scale headline (+0.111 CI[0.077,0.145], n=1541 covered);
    # the witness runs smoke (covered ~72) so it asserts the point-estimate direction (grounded > text) here.
    check("W1 the runnable grounded model beats the text-mined store on necessity (grounded > text; +0.111 CI-sep full)",
          ne["grounded_dosim"]["acc"] > ne["store_textmined"]["acc"] + 0.03,
          "grounded=%.3f store=%.3f (full-scale paired +0.111 CI[0.077,0.145])" % (
              ne["grounded_dosim"]["acc"], ne["store_textmined"]["acc"]))
    check("W2 (honest) grounded does NOT beat the density-matched topology twin on the existence axis (direction inert)",
          ne["paired_grounded_minus_twin"]["ci"][0] <= 0,
          "paired(grounded-twin)=%s" % ne["paired_grounded_minus_twin"]["ci"])
    check("W3 (honest) at loose coverage the SIGN is not load-bearing (grounded ~= sign-scrambled twin on 3-way)",
          abs(tw["paired_grounded_minus_signscram"]["delta"]) < 0.02,
          "grounded=%.3f signscram=%.3f paired=%s" % (tw["grounded_dosim"]["acc"], tw["sign_scrambled_twin"]["acc"],
                                                      tw["paired_grounded_minus_signscram"]["delta"]))
    check("W4 the bridge runs on a real science slice (coverage > 10%)", o["coverage_frac"] > 0.10,
          "coverage=%.1f%%" % (100 * o["coverage_frac"]))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
