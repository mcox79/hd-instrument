"""Witness for the UPSTREAM event-realization JOIN (solver, pri-14 full-stack upstream).

The harm/help arithmetic accepts endstate_reached but the live path never supplies it, so it decides HARM
on events that did not happen. The pinned hdlab.polarity_operator.event_polarity (negation + implicative/
factive veridicality) already computes realization; this rung JOINS it in (non-PREVENT verbs only). Locks
(scaffold-free; CommitmentBank is the INDEPENDENT human check, never consulted at inference):

  W1 THE JOIN LIFTS realization-conditioned accuracy far above the realization-blind live path (joined
     >= 0.90, live <= 0.50 on the realized/unrealized harm-help gold).
  W2 UNREALIZED -> NEUTRAL: 'did not stab' / 'failed to stab' / 'never stabbed' -> abstain (not HARM).
  W3 REALIZED -> label kept: 'stabbed' -> HARM, 'managed to heal' -> HELP.
  W4 NO REGRESSION BY IDENTITY: endstate_reached=True == the live default (None) for every realized
     non-PREVENT verb -> realized text decides byte-identically; no realized item flips vs live.
  W5 TWIN LOSES: scrambling the implicative table drops the unrealized-case accuracy.
  W6 INDEPENDENT HUMAN GOLD: the reused veridicality table agrees with CommitmentBank human judgement on
     the negation subset it knows (>= 0.80).
  W7 PREVENT IS NOT MIS-MAPPED: the join abstains from setting endstate_reached for a PREVENT verb (save)
     -- the verb's polarity is not the prevented-endstate's realization (left to the complement path).

Run: .venv/Scripts/python.exe experiments/fetch_commitmentbank_v1.py && \
     .venv/Scripts/python.exe verification/test_harm_help_endstate_realization_join.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_harm_help_endstate_realization_v1 as E

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


r = E.run()
A = r["partA_realization_gold"]
check("W1 join lifts realization accuracy (joined>=0.90, live<=0.50)",
      A["joined_acc"] >= 0.90 and A["live_acc"] <= 0.50,
      f"live={A['live_acc']} joined={A['joined_acc']}")

j = E.harm_help_joined
check("W2 unrealized -> neutral",
      j("stab", "The man did not stab the boy .", "stabbed") is None
      and j("stab", "The man failed to stab the boy .", "stabbed") is None
      and j("stab", "The man never stabbed the boy .", "stabbed") is None, "")
check("W3 realized -> label kept",
      j("stab", "The man stabbed the boy .", "stabbed") == "HARM"
      and j("heal", "The nurse managed to heal the boy .", "healed") == "HELP", "")

C = r["partC_no_regression"]
check("W4 no regression by identity", not C["realized_flips_vs_live"] and C["er_true_equals_default_for_all_realized"],
      str(C))

B = r["partB_twin"]
check("W5 twin loses on unrealized", B["twin_correct"] < B["joined_correct"],
      f"twin {B['twin_correct']} < joined {B['joined_correct']}")

D = r["partD_commitmentbank"]
ok_d = "agreement" in D and D["agreement"][1] >= 3 and D["agreement"][2] >= 0.80
check("W6 CommitmentBank human agreement >= 0.80", ok_d, str(D.get("agreement", D)))

check("W7 PREVENT not mis-mapped (join abstains for save)",
      E.realized_from_polarity("save", "The nurse did not save the child .", "saved") is None, "")

print("\nRESULT:", "ALL GREEN" if not fails else f"FAILED {fails}")
if __name__ == "__main__":
    sys.exit(1 if fails else 0)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
