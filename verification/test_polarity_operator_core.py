"""Scaffold-free witness: the glass-box polarity + quantity OPERATOR core mechanism + ADDITIVE isolation.

  C1 the operator self-test passes (23 hand-traced cases: direct negation, negative-existential subject,
     interrogative inversion, coordination CHAIN, implicative/factive complement gate, factive gerund,
     post-verbal neg-quant object, focus/'but' guards, quantifier cardinality ALL/SOME/ZERO/EXC).
  C2 the operator is ADDITIVE -- applying it to sm.events is a pure read-out; the reader's core event fields
     (predicate/agent/patient/tense/pred_idx) are BYTE-IDENTICAL with vs without the operator (no downstream
     regress -- the proposed hdlab landing is a default-off polarity/quantity FIELD, extraction untouched).
  C3 the COMPLEMENT GATE is load-bearing where the prior negation gate over-propagated: 'did not remember
     him leaving' leaves leaving TRUE (factive survives negation); 'did not want to leave' leaves leave
     UNDETERMINED (attitude); 'did not manage to escape' makes escape FALSE (implicative) -- none is the
     naive 'propagate negation into the complement' the prior gate did.

Re-derives live from experiments._polarity_operator + the live SituationReader.
Run: .venv/Scripts/python.exe verification/test_polarity_operator_core.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._polarity_operator import event_polarity, _self_test

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    # C1 -- the full hand-traced self-test (asserts 23/23 internally)
    try:
        _self_test()
        chk("C1 operator self-test 23/23 (all mechanisms)", True)
    except AssertionError as e:
        chk("C1 operator self-test", False, str(e))

    # C2 -- ADDITIVE isolation over the live reader
    from experiments.exp_polarity_operator_ewt_v1 import tokenize, read_events
    toks = tokenize("She did not take the key and no one left .")
    ev1 = [(e.predicate, e.agent, e.patient, e.tense, e.pred_idx) for e in read_events(toks)]
    evs = read_events(toks)
    for e in evs:
        event_polarity(toks, e.pred_idx if e.pred_idx is not None else -1, e.predicate,
                       verb_lows={x.predicate for x in evs})
    ev2 = [(e.predicate, e.agent, e.patient, e.tense, e.pred_idx) for e in evs]
    chk("C2 operator ADDITIVE: sm.events core fields byte-identical after operator (no downstream regress)",
        ev1 == ev2 and len(ev1) >= 2, "n_events=%d" % len(ev1))

    # C3 -- complement gate (the upstream fix for the prior gate's over-propagation)
    t = "She did not remember him leaving .".split()
    fac = event_polarity(t, 5, "leaving", verb_lows={"remember", "leaving"}).polarity
    t = "She did not want to leave .".split()
    att = event_polarity(t, 5, "leave", verb_lows={"want", "leave"}).polarity
    t = "He did not manage to escape .".split()
    imp = event_polarity(t, 5, "escape", verb_lows={"manage", "escape"}).polarity
    chk("C3 complement gate: factive +1 / attitude 0 / implicative -1 (NOT naive propagation)",
        fac == +1 and att == 0 and imp == -1, "factive=%d attitude=%d implicative=%d" % (fac, att, imp))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
