"""Scaffold-free witness for slug organ_abstains_on_two_thirds_of_v2.

Re-derives the diagnosis headline DIRECTLY from the production organ
(hdlab.goal_typing.congruence_with_lexicon_fallback) on the v2 bank -- it does not read any
experiment metrics.json, so it cannot pass vacuously off a stale artifact. Reproduces:

  * the landed measurement: 82 abstentions / 124, accuracy 0.2339
  * the PARTITION of the 82 by first point of failure (42 no-goal-recognized; 39 goal-found-but-
    still-abstained, of which 32 outcome-verb-class-unknown; 1 insufficient-sentences)
  * the SILENCE LINE: every abstention terminates at lexicon_predict -> "NONE"/"AMBIGUOUS"
  * the base rate on the 82 (0.5976) and the COMPOUNDING ceiling (only 7/82 have an outcome-side
    class candidate, so a goal-recognition fix is structurally capped)

  .venv/Scripts/python.exe verification/test_goal_abstention_diagnosis.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.goal_typing as gt
from hdlab import verb_lexical_similarity as _vls
from verification.goal_bearing_eval_v2_gates import _scorable

BANK = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v2.jsonl")


def _load():
    rows = [json.loads(l) for l in open(BANK, encoding="utf-8") if l.strip()]
    return _scorable(rows)


def _goal_recognized(text):
    for gs in gt._sentences(text)[:-1]:
        if gt.find_desired_state(gs) is not None:
            return True
    return False


def _outcome_has_candidate(text, window=4):
    sents = gt._sentences(text)
    for k in range(1, min(window, len(sents) - 1) + 1):
        if gt.find_actual_state_candidates(sents[-k], None):
            return True
    return False


def _partition_bucket(text):
    """First point of failure for an abstaining item."""
    sents = gt._sentences(text)
    if len(sents) < 2:
        return "A0_insufficient_sentences"
    if not _goal_recognized(text):
        return "A_no_goal_recognized"
    _, d1 = gt.congruence_outcome_valence_windowed(text)
    if d1.get("reason") == "actual_verb_class_unknown":
        return "B1_outcome_verb_class_unknown"
    return "B_other"


def main():
    _vls.clear_acquired_outcome()   # organ_base state -- the actually-deployed measurement
    scorable = _load()
    assert len(scorable) == 124, f"expected 124 scorable, got {len(scorable)}"

    n_correct = 0
    abst = []                       # (row, gold) for each abstaining item
    buckets = {}
    for r in scorable:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, detail = gt.congruence_with_lexicon_fallback(r["text"])
        n_correct += int(pred == gold)
        if pred in ("MET", "UNMET"):
            continue
        # ---- abstention: check the terminal SILENCE LINE, then partition ----
        assert detail.get("reason") == "abstain_fallback_to_lexicon", \
            f"abstention {r.get('id')} terminal reason={detail.get('reason')!r}, not the lexicon fallback"
        assert detail.get("lexicon_raw") in ("NONE", "AMBIGUOUS"), \
            f"abstention {r.get('id')} lexicon_raw={detail.get('lexicon_raw')!r}"
        abst.append((r, gold))
        b = _partition_bucket(r["text"])
        buckets[b] = buckets.get(b, 0) + 1

    acc = round(n_correct / len(scorable), 4)

    # headline + partition assertions -------------------------------------------------------------
    assert len(abst) == 82, f"expected 82 abstentions, got {len(abst)}"
    assert acc == 0.2339, f"expected accuracy 0.2339, got {acc}"
    assert buckets.get("A_no_goal_recognized", 0) == 42, f"Class A != 42: {buckets}"
    assert buckets.get("B1_outcome_verb_class_unknown", 0) == 32, f"Class B1 != 32: {buckets}"
    assert sum(buckets.values()) == 82, f"partition does not sum to 82: {buckets}"

    # base rate on the 82 + compounding ceiling ---------------------------------------------------
    nm = sum(1 for _, g in abst if g == "MET")
    base = round(max(nm, 82 - nm) / 82, 4)
    assert base == 0.5976, f"expected base rate 0.5976 on the 82, got {base}"
    reach82 = sum(1 for r, _ in abst if _outcome_has_candidate(r["text"]))
    assert reach82 == 7, f"expected 7/82 abstentions with an outcome-side candidate, got {reach82}"

    print("PASS: 82/124 abstain (acc 0.2339). partition:", buckets)
    print("      silence line = lexicon_predict->NONE/AMBIGUOUS for all 82; base rate 0.5976 on the 82;")
    print(f"      compounding ceiling = only {reach82}/82 have an outcome-side class candidate.")
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
