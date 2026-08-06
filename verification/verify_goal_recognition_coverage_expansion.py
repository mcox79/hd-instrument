# SCAFFOLD-FREE WITNESS (2026-08-06). Reproduces the landed goal-recognition coverage-expansion
# numbers off the LIVE promoted organ (hdlab/goal_typing.py), no tracing (tracing=False -- this
# organ takes no tracing flag; it is pure string/set membership). Not a pytest test_* file by
# design: it is a standalone landed-VET witness (verify_* convention, run manually), so it does not
# alter the certified 220/3 test count. Pre-reg:
# preregs/2026-08-06_goal_recognition_coverage_expansion_v1.md
"""verify_goal_recognition_coverage_expansion.py -- asserts the HARD-PASS floors of the conative +
intention pass-class expansion against the real edited hdlab.goal_typing (not a monkeypatched
simulation):

  (1) coverage  >= 30/44 on the goal_bearing_modern_eval_v1 held-out eval (find_desired_state fires
      on the goal_text field). Verified baseline was 19/44; simulated + landed ceiling 33/44.
  (2) precision_control_false_fires == 0/11 on the verbatim bare-transitive/aspectual/gerund-NP
      control set (find_desired_state -- the gated goal-CONTENT recognizer -- must return None).
  (3) try_family recall >= 6/8 ; decide/determine recall >= 3/5 (by goal_verb_lemma).
  (4) import succeeds (GOAL_GOVERNING_PASS disjoint from the stop set -- the load-bearing invariant).

Diagnostics (reported, NOT gated): the pre-existing negation false-fire rate (widened surface area,
the Director's separately-named negation-scope increment) and the one has_goal-only control fire via
the pre-existing c3 EXPERIENCER psych-verb signal (edit-independent).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import (  # noqa: E402
    find_desired_state, has_goal, action_frame_feats, GOAL_GOVERNING_PASS, PARTITIONED_STOP,
)

EVAL_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

# Verbatim from the pre-reg precision-guard control set (do NOT substitute other sentences).
PRECISION_CONTROLS = [
    ("bare_transitive", "She tried the cake before dinner.", "she"),
    ("bare_transitive", "He decided the matter without delay.", "he"),
    ("bare_transitive", "She liked the cake very much.", "she"),
    ("bare_transitive", "He loved the old garden behind the house.", "he"),
    ("bare_transitive", "The judges determined the outcome of the contest.", "judges"),
    ("bare_transitive", "They tried the door but it was locked.", "they"),
    ("aspectual_unaffected", "Dawn began to open the gate.", "dawn"),
    ("aspectual_unaffected", "Fay started to close the shop.", "fay"),
    ("aspectual_unaffected", "He managed to escape the room.", "he"),
    ("gerund_noun_phrase", "She was hoping for rain.", "she"),
    ("gerund_noun_phrase", "He was wanting attention all day.", "he"),
]

NEGATION_SET = [
    "She did not try to escape from the tower.",
    "He never decided to leave the village.",
    "She did not mean to intoxicate Diana.",
    "He did not like to disturb her.",
]


def _load_eval():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run():
    # (4) load-bearing import invariant (would have AssertionError'd at import if broken)
    assert GOAL_GOVERNING_PASS.isdisjoint(PARTITIONED_STOP), "GOAL_GOVERNING_PASS must be stop-disjoint"

    items = _load_eval()
    assert len(items) == 44, f"expected 44 eval items, got {len(items)}"

    # (1) coverage
    fired = [it["id"] for it in items if find_desired_state(it["goal_text"]) is not None]
    coverage = len(fired)
    assert coverage >= 30, f"HARD-PASS coverage floor 30/44 breached: {coverage}/44"

    # (3) per-class recall
    def recall(lemmas):
        rel = [it for it in items if it.get("goal_verb_lemma") in lemmas]
        hit = sum(1 for it in rel if find_desired_state(it["goal_text"]) is not None)
        return hit, len(rel)
    try_hit, try_n = recall({"try"})
    dd_hit, dd_n = recall({"decide", "determine"})
    assert try_hit >= 6, f"HARD-PASS try recall floor 6/8 breached: {try_hit}/{try_n}"
    assert dd_hit >= 3, f"HARD-PASS decide/determine recall floor 3/5 breached: {dd_hit}/{dd_n}"

    # (2) precision guard -- find_desired_state (the GATED goal-CONTENT recognizer) must NOT fire
    fds_false = [s for _t, s, _sj in PRECISION_CONTROLS if find_desired_state(s) is not None]
    feat_false = [s for _t, s, _sj in PRECISION_CONTROLS if "purpose_to_no_det" in action_frame_feats(s)]
    assert len(fds_false) == 0, f"precision guard breached (find_desired_state fired): {fds_false}"
    assert len(feat_false) == 0, f"precision guard breached (purpose_to_no_det fired): {feat_false}"

    # DIAGNOSTIC (not gated): has_goal-only fires (pre-existing c3 EXPERIENCER psych-verb signal,
    # edit-independent -- e.g. "He was wanting attention" reads a genuine desire state).
    hg_only = [s for _t, s, sj in PRECISION_CONTROLS
               if has_goal(s, sj) and find_desired_state(s) is None]

    # DIAGNOSTIC (not gated): pre-existing negation false-fire surface area.
    neg_fires = [s for s in NEGATION_SET if find_desired_state(s) is not None]

    print(f"[CHECK coverage] {coverage}/44 (>=30 floor; baseline 19/44) fired={sorted(fired)}")
    print(f"[CHECK try_recall] {try_hit}/{try_n} (>=6 floor)")
    print(f"[CHECK decide_determine_recall] {dd_hit}/{dd_n} (>=3 floor)")
    print(f"[CHECK precision_guard] find_desired_state false-fires={len(fds_false)}/11 ; "
          f"purpose_to_no_det false-fires={len(feat_false)}/11 (both must be 0)")
    print(f"[DIAG has_goal_only_fires] {len(hg_only)}/11 (pre-existing c3 psych signal, "
          f"edit-independent): {hg_only}")
    print(f"[DIAG negation_false_fires] {len(neg_fires)}/4 (PRE-EXISTING negation-scope gap, "
          f"widened surface area, NOT gated): {neg_fires}")
    print("[ALL GATES PASS] goal-recognition coverage expansion (conative + intention) landed.")
    return {"coverage": coverage, "try_recall": [try_hit, try_n],
            "decide_determine_recall": [dd_hit, dd_n],
            "precision_false_fires_fds": len(fds_false),
            "precision_false_fires_feat": len(feat_false),
            "has_goal_only_fires": len(hg_only), "negation_false_fires": len(neg_fires)}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
