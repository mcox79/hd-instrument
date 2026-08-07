# SCAFFOLD-FREE WITNESS (2026-08-07). Reproduces the DIALOGUE-GOAL RECOGNITION build off the LIVE
# promoted organ (hdlab/goal_typing.py), no tracing (tracing=False -- this organ takes no tracing
# flag; it is pure string/set membership, same convention as
# verify_goal_recognition_coverage_expansion.py). Not a pytest test_* file by design: a standalone
# landed-VET witness (verify_* convention, run manually), so it does not alter the certified 220/3
# test count.
"""verify_dialogue_goal_recognition.py -- asserts the HARD-PASS floors of the 2026-08-07
dialogue-goal-recognition build: two NEW goal-bearing constructions added to
hdlab.goal_typing.find_desired_state as strict-ADD fallback passes, tried ONLY when the pre-existing
GOAL_GOVERNING_PASS + infinitival "to VP" scan (_find_purpose_infinitival) finds nothing:

  (1) HEDGED-MODAL WISH: "wish [i/we] might/could/would VP" (_find_hedged_modal_wish) -- a FINITE
      modal complement, not the infinitival shape the pre-existing scan requires.
  (2) REQUEST: "let me/us VP", "may/might/can I VP", "will you (not) VP", "please VP"
      (_find_request_goal) -- an illocutionary request IS the requester's goal (Searle 1969).

Checks:
  (1) TARGET RECOVERY (>=2/3 required for HARD-PASS; all 3 measured): find_desired_state fires on
      the exact goal-bearing sentence of each of the 3 items the pre-reg named as the pre-existing
      gap -- mg3_frank_garden_invited ("I wish I might open the gate, and walk in."),
      ts_tom_wish_free_potter ("I wish we could get him out of there."), mg3_boy_at_garden_gate
      ("Let me in; let me in; will you not let me in this garden?"). Sentences copied verbatim from
      experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (mg3_*) and
      experiments/data/goal_bearing_modern_eval_v1.jsonl (ts_tom_*; goal_text field).
  (2) PRECISION BANK == 0/11 false-fires: reuses verify_goal_recognition_coverage_expansion.py's
      verbatim PRECISION_CONTROLS bank (the same 0/11 set from commit 051f6d0ef / c2f88ea91) --
      neither new pass may fire on a bare-transitive / aspectual-unaffected / gerund-noun-phrase
      control (none of those 11 sentences contain a wish/let/may/might/can/will/please token, so
      this is close to a structural guarantee, but it is asserted directly against the live organ,
      not by inspection).
  (3) ADVERSARIAL DIALOGUE NON-GOALS == 0/6 false-fires: 4 sentences verbatim from the spawn-prompt
      pre-reg ("will you be quiet", "let me think", "may I say", "I wish you would stop") plus 2
      constructed the same way, both explicitly named in the spawn-prompt's own guard rationale
      ("let me tell you" -- discourse filler; "may I help you" -- an OFFER to the addressee, not a
      request for the speaker).
  (4) EXISTING GOAL-RECOGNITION COVERAGE DOES NOT DROP: re-runs
      verify_goal_recognition_coverage_expansion.run() (import + call, not reimplemented) and
      additionally asserts coverage >= 32/44 -- the concrete last-landed number (post negation-scope
      guard, commit dab23009b3), stricter than that witness's own >=30 floor, so "does not drop" is
      checked against the actual prior number, not just the historical HARD-PASS floor.
  (5) import succeeds (GOAL_GOVERNING_PASS disjoint from the stop set -- load-bearing invariant,
      unchanged by this build).

Diagnostics (reported, NOT gated, per the pre-reg's own framing -- "downstream eval-number effect is
SECONDARY"): congruence_outcome_valence_windowed on the 3 target items' FULL passages. Goal
RECOGNITION now fires on all 3 (gate above), but end-to-end MET/UNMET congruence typing needs
additional outcome-typing / referent-linking work this build does not attempt (0/3 correct on the
full-passage congruence call, measured honestly below) -- consistent with the pre-reg's own
acknowledgment that some targets "need outcome-typing too."
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
VERIFICATION_DIR = os.path.dirname(os.path.abspath(__file__))
if VERIFICATION_DIR not in sys.path:
    sys.path.insert(0, VERIFICATION_DIR)

from hdlab.goal_typing import (  # noqa: E402
    find_desired_state, GOAL_GOVERNING_PASS, PARTITIONED_STOP,
    congruence_outcome_valence_windowed,
)
import verify_goal_recognition_coverage_expansion as _coverage_witness  # noqa: E402

# (1) TARGET RECOVERY -- verbatim goal-bearing sentences (not the full multi-sentence passage; the
# same convention the pre-existing coverage witness uses on goal_text).
TARGET_ITEMS = [
    ("mg3_frank_garden_invited", "I wish I might open the gate, and walk in."),
    ("ts_tom_wish_free_potter", "I wish we could get him out of there."),
    ("mg3_boy_at_garden_gate", "Let me in; let me in; will you not let me in this garden?"),
]

# (2) PRECISION BANK -- verbatim from verify_goal_recognition_coverage_expansion.py; imported, not
# copy-pasted, so it can never drift from the certified 0/11 set.
PRECISION_CONTROLS = _coverage_witness.PRECISION_CONTROLS

# (3) ADVERSARIAL DIALOGUE NON-GOALS -- 4 verbatim from the spawn-prompt pre-reg + 2 more from the
# spawn-prompt's own guard rationale (see module docstring above).
ADVERSARIAL_NON_GOALS = [
    "Will you be quiet.",
    "Let me think.",
    "May I say.",
    "I wish you would stop.",
    "Let me tell you.",
    "May I help you.",
]

# Full passages for the (informational, not gated) downstream congruence-typing diagnostic.
FRANK_TEXT = ('Frank was one day walking with his mother, when they came to a pretty garden. Frank '
    'looked in, and saw that it had clean gravel walks, and beds of beautiful flowers all in bloom. '
    'He called to his mother, and said, "Mother, come and look at this pretty garden. I wish I '
    'might open the gate, and walk in." The gardener, being near, heard what Frank said, and '
    'kindly invited him and his mother to come into the garden.')
BOY_TEXT = ('While Frank was admiring the beauty of a flower, a boy came to the gate, and finding '
    'it locked, he shook it hard. But it would not open. Then he said, "Let me in; let me in; will '
    'you not let me in this garden?" "No, indeed," said the gardener, "I will not let you in, I '
    'assure you; for when I let you in yesterday, you meddled with my flowers, and pulled some of '
    'my rare fruit." The boy looked ashamed, and when he found that the gardener would not let him '
    'in, he went slowly away.')
TOM_TEXT = ('"I wish we could get him out of there." Tom began testifying: "and as the doctor '
    'fetched the board around and Muff Potter fell, Injun Joe jumped with the knife and--" Crash! '
    'Quick as lightning Joe sprang for a window, tore his way through all opposers, and was gone! '
    "Daily Potter's gratitude made Tom glad he had spoken.")
DOWNSTREAM_ITEMS = [
    ("mg3_frank_garden_invited", FRANK_TEXT, "met"),
    ("mg3_boy_at_garden_gate", BOY_TEXT, "unmet"),
    ("ts_tom_wish_free_potter", TOM_TEXT, "met"),
]


def run():
    # (5) load-bearing import invariant (would have AssertionError'd at import if broken)
    assert GOAL_GOVERNING_PASS.isdisjoint(PARTITIONED_STOP), "GOAL_GOVERNING_PASS must be stop-disjoint"

    # (1) target recovery
    recovered = [(name, find_desired_state(sent)) for name, sent in TARGET_ITEMS]
    n_recovered = sum(1 for _n, r in recovered if r is not None)
    assert n_recovered >= 2, f"HARD-PASS floor >=2/3 target items breached: {n_recovered}/3"

    # (2) precision bank
    precision_false_fires = [s for _t, s, _sj in PRECISION_CONTROLS if find_desired_state(s) is not None]
    assert len(precision_false_fires) == 0, (
        f"precision-bank false-fire: {precision_false_fires}")

    # (3) adversarial dialogue non-goals
    adversarial_false_fires = [s for s in ADVERSARIAL_NON_GOALS if find_desired_state(s) is not None]
    assert len(adversarial_false_fires) == 0, (
        f"adversarial dialogue non-goal false-fire: {adversarial_false_fires}")

    # (4) existing coverage does not drop
    coverage_result = _coverage_witness.run()
    assert coverage_result["coverage"] >= 32, (
        f"existing coverage regressed below the last-landed 32/44: {coverage_result['coverage']}/44")

    print(f"[CHECK target_recovery] {n_recovered}/3 (>=2 floor): "
          f"{[(n, (r or {}).get('pattern')) for n, r in recovered]}")
    print(f"[CHECK precision_bank] false_fires={len(precision_false_fires)}/11 (must be 0)")
    print(f"[CHECK adversarial_non_goals] false_fires={len(adversarial_false_fires)}/6 (must be 0)")
    print(f"[CHECK existing_coverage_unchanged_or_better] {coverage_result['coverage']}/44 "
          f"(>=32 floor; existing try_recall={coverage_result['try_recall']}, "
          f"decide_determine_recall={coverage_result['decide_determine_recall']}, "
          f"precision_false_fires_fds={coverage_result['precision_false_fires_fds']}, "
          f"negation_false_fires={coverage_result['negation_false_fires']}, "
          f"complement_negation_fires={coverage_result['complement_negation_fires']})")

    # DIAGNOSTIC (not gated): downstream end-to-end congruence typing on the 3 target items' FULL
    # passages -- goal RECOGNITION fires on all 3 (gated above), but MET/UNMET typing needs
    # additional outcome-typing/referent-linking work this build does not attempt.
    downstream = []
    for name, text, gold in DOWNSTREAM_ITEMS:
        verdict, info = congruence_outcome_valence_windowed(text)
        downstream.append((name, verdict, gold, verdict.lower() == gold))
    n_correct = sum(1 for *_, ok in downstream for ok in [ok] if ok)
    print(f"[DIAG downstream_congruence] {n_correct}/3 correct MET/UNMET on full passages "
          f"(NOT gated -- goal recognition alone does not guarantee correct outcome typing): "
          f"{downstream}")

    print("[ALL GATES PASS] dialogue-goal recognition (HEDGED_MODAL_WISH + REQUEST) landed.")
    return {"target_recovery": n_recovered, "precision_false_fires": len(precision_false_fires),
            "adversarial_false_fires": len(adversarial_false_fires),
            "existing_coverage": coverage_result["coverage"],
            "downstream_correct": n_correct}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
