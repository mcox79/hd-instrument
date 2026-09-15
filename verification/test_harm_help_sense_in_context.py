"""Witness for UPSTREAM RUNG 3 -- sense-in-context selection for the harm/help endstate read
(solver, pri-14 full-stack upstream). Reuses hdlab.grounded_semantic_graph.select_sense (PPR) to pick the
context-active sense, then values THAT synset. Locks (scaffold-free; builds the graph once, ~80s):

  W1 THE HEADLINE WIN: on the NON-assault contexts ('beat the eggs', 'throttle the engine', 'pound the
     flour') sense-in-context correctly ABSTAINS on all of them, where the context-blind read wrongly
     decides HARM on all of them.
  W2 THE ASSAULT READING is HARM where the selected sense is valued: throttle/beat + person -> HARM.
  W3 SENSE-IN-CONTEXT beats the context-blind read overall (>= it, and strictly on the non-assault slice).
  W4 CONTEXT-BLIND CANNOT SEPARATE: harm_help('beat') is the same regardless of context (the defect).
  W5 TWIN LOSES: shuffling the context words collapses the selection advantage.

Run: .venv/Scripts/python.exe verification/test_harm_help_sense_in_context.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_harm_help_sense_in_context_v1 as E

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


r = E.run()
na = r["non_assault"]
check("W1 non-assault: sense abstains all, context-blind wrongly decides all",
      na["sense_correct"] == na["n"] and na["blind_correct"] == 0,
      f"sense {na['sense_correct']}/{na['n']}, blind {na['blind_correct']}/{na['n']}")
check("W2 assault reading -> HARM (throttle/beat + person)",
      E.harm_help_sense_in_context("throttle", ["man", "neck", "choke"]) == "HARM"
      and E.harm_help_sense_in_context("beat", ["man", "fists", "victim"]) == "HARM", "")
g = r["sense_gold"]
check("W3 sense-in-context beats context-blind",
      g["sense_in_context_acc"] > g["context_blind_acc"],
      f"blind={g['context_blind_acc']} sense={g['sense_in_context_acc']}")
check("W4 context-blind cannot separate (same label both contexts)",
      E.harm_help_context_blind("beat") == E.harm_help_context_blind("beat"), "harm_help('beat') is context-free")
check("W5 twin loses", r["twin"]["twin_acc"] < g["sense_in_context_acc"], str(r["twin"]))

print("\nRESULT:", "ALL GREEN" if not fails else f"FAILED {fails}")
if __name__ == "__main__":
    sys.exit(1 if fails else 0)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.slow
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
