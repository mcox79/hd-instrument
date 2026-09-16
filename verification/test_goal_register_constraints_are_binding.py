"""Scaffold-free witness: THE AGENT, OBJECT AND TIME CONSTRAINTS ARE BINDING IN THE GOAL REGISTER.

problem: the_goal_register_answers_why_with_another_agents_purpose_marks_a_goal_satisfied_by_verb_and_agent_
         alone_and_reads_future_goals_into_time_limited_prediction_make_agent_object_and_time_constraints_binding
         (pri 135; substrate-evaluation findings R02 / R03 / R04, appendix A11)

WHAT IT PINS (claims, not numbers). The review's own controlled fixtures, run against the LIVE hdlab modules:

  W1  IDENTITY (R02): an agent-constrained purpose query never returns another agent's purpose -- it returns
      that agent's own goal or nothing -- and the same-agent fallback is LABELLED, so a consumer can tell a
      purpose from a fallback instead of assuming ("why(...)" with provenance).
  W2  CONTENT (R03): a goal is closed by an outcome that achieves its CONTENT. "buy bread" is satisfied by
      buying bread and NOT by buying a car; a negated outcome does not close it; where the outcome's theme
      cannot be observed the closure still fires but the record SAYS which evidence it stands on.
  W3  ORDER (R03): a realization LATER IN THE GOAL'S OWN SENTENCE closes the goal, and an event BEFORE the
      goal is stated does not -- discourse order is (sentence, within-sentence position), not sentence alone.
  W4  TIME (R04): every goal query is bounded by t -- a goal stated after t is not in the model at t, a goal
      closed after t is still active at t, and the forward-prediction closure's GOAL EVIDENCE at t is
      prefix-invariant (the reproduced leak: goal evidence [buy, yacht] at t=0 for a goal stated at s5).
  W5  NO REGRESSION on the goal organ's own authored golds -- the satisfaction gold (test_goal_register.py W7,
      model 1.0 vs the always-active floor 0.3333) and the Suh-Trabasso reinstatement gold (W8, model 1.0 vs
      the recency floor 0.0) -- recomputed here under the repaired closure, not read from a landed metrics file.

LANDED-STATE CONTRACT (the point of this file): the fixtures are asserted GREEN against whichever
implementation is under test, and the LIVE tree is asserted to have the DEFECT while the proposal is
unlanded and to be FREE of it once it lands. Before landing, "under test" is the proposal built in memory
from notes/problems/<slug>/goal_constraints_patch.diff by experiments/exp_goal_constraints_v1.py; after
landing, "under test" IS hdlab (no materialize, no git apply, no monkeypatch), and W6 additionally asserts
that the live tree passes every fixture. So this witness is green in both states and its MEANING flips.

    .venv/Scripts/python.exe verification/test_goal_register_constraints_are_binding.py
"""
import os
import sys
from types import SimpleNamespace as N

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _reader_goal_evidence(SRmod, GR, goals, events, sents, t):
    """The GOAL EVIDENCE the forward-prediction closure hands the projector at time t, captured with a
    recording projector (the review's A11 probe, run on the module under test -- no store asset loaded)."""

    class Rec:
        def available(self):
            return True

        def project(self, context, goals_, candidates, gain=2.0):
            return N(context=list(context), goals=list(goals_))

    reg = GR.GoalRegister(goals)
    sm = N(events=events, wants=reg.wants, forward_prediction=None)
    SRmod.SituationReader._read_prediction(N(_gek_org=Rec()), sm, sents)
    fp = sm.predict_next_event(["a", "b"], t=t)
    return list(fp.goals)


def main():
    import hdlab.goal_register as GR_live
    from experiments.exp_goal_constraints_v1 import fixtures, load_impl, arm_authored, _ev

    landed = hasattr(GR_live, "closing_outcome") and hasattr(GR_live, "content_verdict")
    GR, SR, _l = load_impl(need_reader=True)
    checks = []

    # ---- W1-W4: the review's fixtures against the implementation under test ----
    fx = fixtures(GR)
    bad = [c for c in fx if not c["ok"]]
    assert not bad, ("fixtures must be green under the implementation being landed", bad)
    groups = {"W1 identity": [c for c in fx if c["name"].startswith(("F1", "F6"))],
              "W2 content": [c for c in fx if c["name"].startswith(("F2", "F5"))],
              "W3 order": [c for c in fx if c["name"].startswith("F3")],
              "W4 time": [c for c in fx if c["name"].startswith("F4")]}
    for g, rows in groups.items():
        assert rows and all(c["ok"] for c in rows), (g, rows)
        checks.append(("%s -- %d fixtures green" % (g, len(rows)), "BINDING"))

    # ---- W4b: the reader's forward-prediction goal evidence is prefix-invariant at t ----
    future = GR.Goal(agent="alice", goal_head="buy", goal_text="buy yacht", kind="desire",
                     source_verb="want", sent_idx=5, verb_tok=1, to_tok=2)
    sents = [["alice", "arrived"], ["later", "plans"], ["x"], ["y"], ["z"],
             ["alice", "wanted", "to", "buy", "a", "yacht"]]
    events = [_ev(0, 1, "arrive", "alice")]
    full = _reader_goal_evidence(SR, GR, [future], events, sents, t=0)
    prefix = _reader_goal_evidence(SR, GR, [], events, sents[:1], t=0)
    assert full == prefix == [], ("a t=0 prediction must not read a goal stated at sentence 5", full, prefix)
    checks.append(("W4b forward-prediction goal evidence at t=0 is prefix-invariant (was ['buy','yacht'])",
                   "PREFIX-INVARIANT"))

    # ---- W5: the goal organ's own authored golds do not move ----
    a = arm_authored(GR, n_twin=40)
    sat, rei = a["authored_satisfaction_W7"], a["authored_reinstatement_W8"]
    assert sat["model_acc"] >= 0.9 and sat["model_acc"] > sat["floor_always_active_acc"], sat
    assert set(sat["by_status"].keys()) >= {"satisfied", "active", "failed"}, sat
    assert rei["model_reinstatement_acc"] >= 0.9 and rei["floor_recency_acc"] <= 0.1, rei
    assert rei["model_reinstatement_acc"] > rei["twin_status_shuffle_p95"], rei
    checks.append(("W5 authored golds hold: satisfaction %.3f (floor %.3f), reinstatement %.3f (floor %.3f, "
                   "twin p95 %.3f)" % (sat["model_acc"], sat["floor_always_active_acc"],
                                       rei["model_reinstatement_acc"], rei["floor_recency_acc"],
                                       rei["twin_status_shuffle_p95"]), "NO-REGRESSION"))

    # ---- W6: THE LANDED-STATE FLIP -- the defect is present before landing and absent after ----
    live = fixtures(GR_live)
    live_bad = [c for c in live if not c["ok"]]
    if landed:
        assert not live_bad, ("on the landed tree the LIVE modules must pass every fixture", live_bad)
        checks.append(("W6 LANDED: the live hdlab modules pass all %d fixtures (the defect is ABSENT)"
                       % len(live), "LANDED-GREEN"))
    else:
        names = " | ".join(c["name"] for c in live_bad)
        assert live_bad, "pre-landing, the live tree must still REPRODUCE the defect (else the patch is stale)"
        assert any("bought car" in c["name"] for c in live_bad), ("R03 content must reproduce", names)
        assert any(c["name"].startswith("F3 ") for c in live_bad), ("R03 order must reproduce", names)
        assert any(c["name"].startswith("F4") for c in live_bad), ("R04 time must reproduce", names)
        checks.append(("W6 PRE-LANDING: the live tree reproduces the defect on %d/%d fixtures; the proposal "
                       "under test is green on all %d" % (len(live_bad), len(live), len(fx)), "REPRODUCED"))

    print("PASS -- %d witness groups (landed=%s):" % (len(checks), landed))
    for name, verdict in checks:
        print("  %-96s %s" % (name, verdict))
    print("\nHEADLINE: the goal register's three dropped constraints are binding. An agent-constrained WHY "
          "returns that agent's goal or nothing, with the fallback labelled; a goal is closed only by an "
          "outcome that achieves its CONTENT (same theme, decided through the reader's own entity files, "
          "graded when the theme is unobservable) and only by an outcome that comes AFTER it in (sentence, "
          "position); and every goal read is bounded by the query time, so a prediction at t can no longer "
          "be conditioned on a goal stated later in the document. The organ's authored satisfaction and "
          "reinstatement golds are unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
