"""Witness -- the causal-DIRECTION signal on DIRECTION-SENSITIVE golds where association is neutralized by
construction. This is the one causal-SPECIFIC signal the mined testimony store carries (direction from causal
MARKING), demonstrated where a similarity/association model is at chance.

  W1 BCOPA-CE floors AT CHANCE by construction: direction_blind, lexical, and the twin all ~0.50 (the instrument
     fully neutralizes association -- the two alternatives are the true cause AND true effect of the same premise).
  W2 BCOPA-CE: causal_directed beats DIRECTION-BLIND CI-sep on the covered subset -- the store's DIRECTION signal is
     load-bearing where association cannot help.
  W3 e-CARE gold causal pairs: causal-direction beats the shuffled twin CI-sep (a modern human-annotated gold;
     association = 0.5 by construction).
  W4 HONEST BOUND: the direction signal is WEAK in absolute terms (BCOPA-CE causal_directed ~0.52), consistent with
     the ~0.60 held-out direction ceiling -- text-derived causal strength is fundamentally rung-1 (Causal Hierarchy
     Theorem) + reporting/explanation-selection biased; the rung-2 unlock is the counterfactual-necessity SIMULATION.

Run: .venv/Scripts/python.exe verification/test_causal_direction_signal.py
"""
from __future__ import annotations
import os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_causal_bcopa_ce_v1 as B
from experiments import exp_causal_direction_ecare_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    b = B.run(smoke=False)
    f = b["full"]
    oks.append(check(
        "W1 BCOPA-CE floors AT CHANCE by construction (assoc neutralized): direction_blind/lexical/twin ~0.50",
        abs(f["direction_blind"]["acc"] - 0.5) < 0.03 and abs(f["lexical"]["acc"] - 0.5) < 0.03
        and abs(f["causal_twin"]["acc"] - 0.5) < 0.03,
        "blind %.3f lexical %.3f twin %.3f" % (f["direction_blind"]["acc"], f["lexical"]["acc"], f["causal_twin"]["acc"])))
    oks.append(check(
        "W2 BCOPA-CE: causal_directed beats DIRECTION-BLIND CI-sep on the covered subset (direction is load-bearing)",
        b["paired_directed_minus_blind_covered"]["ci"][0] > 0,
        "covered causal %.3f vs blind | paired(directed-blind) covered %+.4f CI%s (full %+.4f CI%s)" % (
            b["covered_subset"]["causal_directed"]["acc"], b["paired_directed_minus_blind_covered"]["delta"],
            b["paired_directed_minus_blind_covered"]["ci"], b["paired_directed_minus_blind_full"]["delta"],
            b["paired_directed_minus_blind_full"]["ci"])))
    d = D.run(smoke=False)
    oks.append(check(
        "W3 e-CARE gold causal pairs: causal-direction beats the shuffled twin CI-sep (modern human gold)",
        d["paired_causal_minus_twin_full"]["ci"][0] > 0,
        "causal-direction %.3f vs twin %.3f | paired %+.4f CI%s" % (
            d["causal_full"]["acc"], d["twin_full"]["acc"], d["paired_causal_minus_twin_full"]["delta"],
            d["paired_causal_minus_twin_full"]["ci"])))
    oks.append(check(
        "W4 HONEST BOUND: the direction signal is WEAK in absolute terms (BCOPA-CE causal_directed < 0.56), "
        "consistent with the rung-1/scale ceiling -- the rung-2 unlock is the necessity SIMULATION, not a text score",
        f["causal_directed"]["acc"] < 0.56,
        "BCOPA-CE causal_directed %.3f | e-CARE causal-direction %.3f" % (
            f["causal_directed"]["acc"], d["causal_full"]["acc"])))
    n = sum(oks)
    print("=" * 100)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 100)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
