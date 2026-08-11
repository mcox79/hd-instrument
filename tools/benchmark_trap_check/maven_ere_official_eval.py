"""Faithful port of ONE function from the OFFICIAL MAVEN-ERE evaluator
(THU-KEG/MAVEN-ERE `evaluate.py`): the `evaluate(golden, res, type)`
relation-classification scorer used for the causal and subevent relation
tasks. (The coreference/temporal scorers in the same file are out of scope
for this trap-check and are not ported.)

SOURCE (fetched 2026-08-10 via `git clone --depth 1
https://github.com/THU-KEG/MAVEN-ERE.git` into a scratch dir, ported by hand,
arithmetic/control-flow identical, only file-IO/argv stripped):
  https://github.com/THU-KEG/MAVEN-ERE/blob/main/evaluate.py
  (the REL2ID dict + the `evaluate()` function body)

Ported 1:1, same control flow:
  1. Candidate-pair space = EVERY ORDERED PAIR (m1, m2), m1 != m2, of EVENT
     MENTIONS in the document (`event['mention']` entries; for causal/
     subevent this does NOT include TIMEX -- TIMEX is temporal-task-only in
     the official code).
  2. Every candidate pair initialized to label 0 (NONE).
  3. Gold labels are annotated at the EVENT (coreference-chain) level in
     `causal_relations` / `subevent_relations`; the official code expands
     each event-level edge to EVERY mention-pair inside the two events'
     mention lists -- ported exactly. This is why the mention-pair count of
     positive labels exceeds the raw event-level edge count reported in the
     paper's README (57,992 causal / 15,841 subevent event-level edges).
  4. Metric = sklearn precision_score/recall_score/f1_score with
     labels=[1, 2, ...] (POSITIVE classes only, NONE=0 EXCLUDED) and
     average='micro', reported *100 (percentage points) -- same call, same
     args, as the official script.

LOAD-BEARING STRUCTURAL PROPERTY (not a bug in this port -- a property of
the metric the dataset authors chose, mirrored faithfully here): because
NONE is excluded from the positive-label averaging, a prediction stream
that NEVER predicts a positive label (e.g. a naive "always predict the
single most frequent label", when that label is NONE) scores EXACTLY 0.0 by
construction -- precision has an empty predicted-positive denominator,
recall has zero true positives against the gold positive count. This bears
directly on the trap-check verdict: the SAME class imbalance that would
make a majority baseline deceptively STRONG under plain accuracy (~97-98%
given the skew measured on the dev split) makes it trivially, structurally
WEAK (0.0) under the dataset's own official metric. Both numbers (official
positive-only micro-F1, plus a macro-F1-over-all-labels and raw accuracy)
are reported by the trap-check script so this structural fact is visible
rather than silently inherited.

Self-test: no bit-exact published regression fixture exists for this
evaluator (unlike ProPara's aristo-leaderboard tests) -- self_test()
instead (a) verifies gold-vs-itself scores perfect P/R/F1=100.0, (b)
hand-computes expected P/R/F1 on a tiny synthetic 2-mention-pair example
with a known TP/FP/FN and asserts an exact match, exercising the REAL
candidate-pair-construction + event-level-to-mention-level expansion +
sklearn-scoring code path this module uses at full scale.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

REL2ID = {
    "causal": {"NONE": 0, "PRECONDITION": 1, "CAUSE": 2},
    "subevent": {"NONE": 0, "subevent": 1},
}


def event_mentions_and_eid(doc: dict) -> Tuple[List[str], Dict[str, list]]:
    """mention_ids: list of every event-mention id in the doc (duplicates
    possible only if the source data is malformed); eid: event_id -> list of
    that event's mention dicts (id/sent_id/offset/trigger_word)."""
    mention_ids: List[str] = []
    eid: Dict[str, list] = {}
    for event in doc["events"]:
        eid[event["id"]] = event["mention"]
        for m in event["mention"]:
            mention_ids.append(m["id"])
    return mention_ids, eid


def candidate_pairs(doc: dict) -> Tuple[List[Tuple[str, str]], Dict[str, list]]:
    """Every ORDERED pair of distinct event-mention ids in the doc -- the
    official evaluator's candidate-pair space (mirrors evaluate.py's
    `for m1 in mentions: for m2 in mentions: if m1 != m2` loop)."""
    mention_ids, eid = event_mentions_and_eid(doc)
    keys = [(m1, m2) for m1 in mention_ids for m2 in mention_ids if m1 != m2]
    return keys, eid


def official_gold_labels(doc: dict, rel_type: str) -> Dict[Tuple[str, str], int]:
    """{(m1_id, m2_id): label_int} for every ordered pair of distinct event
    mentions in doc. Mirrors evaluate.py's pair_mp construction + the
    event-level-relation-to-mention-pair label backfill exactly."""
    keys, eid = candidate_pairs(doc)
    labels: Dict[Tuple[str, str], int] = {k: 0 for k in keys}
    if rel_type != "subevent":
        for rel, pairs in doc[f"{rel_type}_relations"].items():
            for e1, e2 in pairs:
                for m1 in eid[e1]:
                    for m2 in eid[e2]:
                        labels[(m1["id"], m2["id"])] = REL2ID[rel_type][rel]
    else:
        for e1, e2 in doc["subevent_relations"]:
            for m1 in eid[e1]:
                for m2 in eid[e2]:
                    labels[(m1["id"], m2["id"])] = REL2ID["subevent"]["subevent"]
    return labels


def official_prf(gold: List[int], pred: List[int], rel_type: str) -> dict:
    """THE official metric: micro P/R/F1 over POSITIVE labels only (NONE
    excluded from both the label set and hence the denominators), *100 --
    identical call signature to evaluate.py's own precision_score/
    recall_score/f1_score(labels=pos_labels, average='micro')*100.0."""
    positive_labels = list(range(1, len(REL2ID[rel_type])))
    gold_a, pred_a = np.asarray(gold), np.asarray(pred)
    p = precision_score(gold_a, pred_a, labels=positive_labels, average="micro", zero_division=0)
    r = recall_score(gold_a, pred_a, labels=positive_labels, average="micro", zero_division=0)
    f1 = f1_score(gold_a, pred_a, labels=positive_labels, average="micro", zero_division=0)
    return {"precision": float(p) * 100.0, "recall": float(r) * 100.0, "f1": float(f1) * 100.0}


def macro_f1_all_labels(gold: List[int], pred: List[int], rel_type: str) -> float:
    """NOT the official metric -- our own addition (per task instruction:
    "report both their headline metric and, if different, macro-F1").
    Macro-F1 across ALL labels including NONE, *100."""
    all_labels = list(range(len(REL2ID[rel_type])))
    return float(f1_score(gold, pred, labels=all_labels, average="macro", zero_division=0)) * 100.0


def accuracy_pct(gold: List[int], pred: List[int]) -> float:
    gold_a, pred_a = np.asarray(gold), np.asarray(pred)
    return float((gold_a == pred_a).mean()) * 100.0


def self_test() -> dict:
    """Real-code-path fidelity check (no published bit-exact fixture exists
    for this evaluator, unlike ProPara's aristo-leaderboard tests)."""
    # ---- (a) gold-vs-itself must be perfect, exercising candidate_pairs +
    # official_gold_labels + the event-to-mention-pair expansion at once.
    doc = {
        "events": [
            {"id": "e1", "type": "Rain", "mention": [{"id": "m1", "sent_id": 0, "offset": [1, 2]}]},
            {"id": "e2", "type": "Flood", "mention": [{"id": "m2", "sent_id": 1, "offset": [1, 2]}]},
            {"id": "e3", "type": "Sound", "mention": [{"id": "m3", "sent_id": 1, "offset": [5, 6]}]},
        ],
        "causal_relations": {"CAUSE": [["e1", "e2"]], "PRECONDITION": []},
        "subevent_relations": [["e1", "e3"]],
    }
    gold = official_gold_labels(doc, "causal")
    assert len(gold) == 6, f"expected 6 ordered pairs over 3 mentions, got {len(gold)}: {gold}"
    assert gold[("m1", "m2")] == 2, f"expected CAUSE(2) for (m1,m2), got {gold}"
    assert gold[("m2", "m1")] == 0, f"expected NONE(0) for reverse (m2,m1), got {gold}"
    assert gold[("m1", "m3")] == 0 and gold[("m3", "m1")] == 0

    g_list = list(gold.values())
    self_prf = official_prf(g_list, g_list, "causal")
    assert self_prf["precision"] == 100.0 and self_prf["recall"] == 100.0 and self_prf["f1"] == 100.0, (
        f"GOLD_VS_ITSELF_NOT_100: {self_prf}"
    )

    # subevent path
    sub_gold = official_gold_labels(doc, "subevent")
    assert sub_gold[("m1", "m3")] == 1, f"expected subevent(1) for (m1,m3), got {sub_gold}"
    assert sub_gold[("m3", "m1")] == 0

    # ---- (b) hand-computed imperfect prediction: 1 TP, 1 FN (miss), 1 FP
    # (wrong-direction/spurious positive) -> precision=recall=f1=50.0 exactly.
    pred = dict(gold)  # causal gold: {(m1,m2):2, (m2,m1):0, (m1,m3):0, (m3,m1):0, (m2,m3):0, (m3,m2):0}
    # keep the TP at (m1,m2); introduce a FN by mis-predicting (m1,m2) as... no:
    # to get exactly 1 TP + 1 FN + 1 FP we need TWO gold-positive pairs. Extend:
    doc2 = dict(doc)
    doc2["events"] = doc["events"] + [{"id": "e4", "type": "Wind", "mention": [{"id": "m4", "sent_id": 0, "offset": [4, 5]}]}]
    doc2["causal_relations"] = {"CAUSE": [["e1", "e2"], ["e4", "e2"]], "PRECONDITION": []}
    gold2 = official_gold_labels(doc2, "causal")
    assert gold2[("m1", "m2")] == 2 and gold2[("m4", "m2")] == 2, f"expected 2 CAUSE gold pairs: {gold2}"
    pred2 = dict(gold2)
    pred2[("m4", "m2")] = 0   # miss one true CAUSE -> FN
    pred2[("m3", "m1")] = 2   # invent a spurious CAUSE where gold is NONE -> FP
    g2, p2 = list(gold2.values()), [pred2[k] for k in gold2.keys()]
    hand_prf = official_prf(g2, p2, "causal")
    assert abs(hand_prf["precision"] - 50.0) < 1e-6, f"expected precision=50.0 (TP=1,FP=1), got {hand_prf}"
    assert abs(hand_prf["recall"] - 50.0) < 1e-6, f"expected recall=50.0 (TP=1,FN=1), got {hand_prf}"
    assert abs(hand_prf["f1"] - 50.0) < 1e-6, f"expected f1=50.0, got {hand_prf}"

    # ---- (c) structural property: an all-NONE prediction stream scores
    # EXACTLY 0.0 on the official metric even though it's the majority label
    # and would score high on plain accuracy -- this is the load-bearing
    # claim the module docstring makes; assert it directly.
    all_none_pred = [0] * len(g2)
    none_prf = official_prf(g2, all_none_pred, "causal")
    assert none_prf["precision"] == 0.0 and none_prf["recall"] == 0.0 and none_prf["f1"] == 0.0, (
        f"STRUCTURAL_PROPERTY_VIOLATED: all-NONE prediction should score exactly 0.0, got {none_prf}"
    )
    none_acc = accuracy_pct(g2, all_none_pred)
    assert none_acc > 50.0, f"expected all-NONE accuracy to be well above chance given class skew, got {none_acc}"

    return {
        "gold_vs_itself_prf": self_prf,
        "hand_computed_prf": hand_prf,
        "all_none_official_f1": none_prf["f1"],
        "all_none_accuracy_pct": none_acc,
    }


if __name__ == "__main__":
    import json

    out = self_test()
    print(json.dumps(out, indent=2))
    print("[SELF-TEST] PASS -- MAVEN-ERE official-eval port (causal + subevent, positive-only micro-F1) verified")
