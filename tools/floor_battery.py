"""RUN A BATTERY OF TRIVIAL BASELINES AGAINST A BINARY TASK, AND REPORT THE STRONGEST.

WHY THIS EXISTS. The measurement bar says a gate is a CI-separated margin over the STRONGEST FLOOR
ACTUALLY RUN. "Actually run" is the weak point: on 2026-08-22 the consequence-learning line had been
grading itself against a majority floor of 0.6389 for weeks, while a one-line negation counter over
the final sentence scored 0.8056 -- and the organ under test scored 0.4722. Nobody had run the
counter. The gap was found by accident, and accident does not scale.

This makes the floor search MECHANICAL: give it items and labels, it runs every cheap baseline it
knows and tells you which one you actually have to beat.

    from tools.floor_battery import run_battery
    rep = run_battery(texts, labels)          # labels: 1/0
    rep["strongest"]        -> ("negation_cue_last_sentence", 0.8056)

WHAT A FLOOR IS FOR, AND THE ASYMMETRY THAT MAKES THIS SAFE. Every baseline here picks its best
threshold ON THE DATA IT IS SCORING. For a TREATMENT that would be fatal; for a FLOOR the bias runs
the safe way -- an optimistically-fitted floor is a HARDER bar, so a mechanism that clears it has
cleared something at least this strong. The permutation null recomputes the best threshold INSIDE
each permutation, so threshold selection is priced.

WHAT THIS IS NOT. It is not a model, not a proposal, and nothing here should ever be shipped as a
mechanism. A trivial baseline beating an organ is a statement about the ORGAN'S EVIDENCE, not a
recommendation to use the baseline. This project's recurring result is word-counting beating the
substrate, and the discipline is that such a result RAISES THE BAR rather than becoming the answer.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import math
import re
import sys
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

# ------------------------------------------------------------------------------------------------
# COMPAT RE-EXPORT (2026-08-30): this filename was REPLACED by the text-eval battery above (commit
# b500e06d7), which wholesale clobbered an UNRELATED retrieval-floor battery (as_constant_matrix /
# constant_prototype_floor / frequency_floor / ...) that ~7 meaning+retrieval cells still import from
# `tools.floor_battery`. The two APIs are DISJOINT. The retrieval-floor battery is restored VERBATIM to
# tools/retrieval_floor_battery.py (recovered from commit 03fee68cf) and re-exported here so those cells
# import again WITHOUT edits -- unblocking the meaning-channel landing's reproduction chain. This does NOT
# touch the text-eval `run_battery` API above. See STATUS meaning-channel bit-rot note.
from tools.retrieval_floor_battery import (  # noqa: E402,F401
    l2n, as_constant_matrix, constant_prototype_floor, frequency_floor, scramble_null,
    oracle_constant_scores, balanced_candidate_sets, pool_admits_a_winning_constant,
    matched_candidate_sets, hit_at_1_both_tie_conventions, rank_of_best_gold,
    paired_bootstrap_ci, margin,
)

NEG = re.compile(
    r"\b(no|not|never|nothing|none|n't|cannot|refus\w*|fail\w*|won't|can't|didn't|hasn't|"
    r"wouldn't|couldn't|shan't|nor)\b", re.I)
POS = re.compile(r"\b(yes|glad|happy|success\w*|final(?:ly)?|at last|manag\w*|manage[ds]?)\b", re.I)


def _last_sentence(t: str) -> str:
    parts = re.split(r"(?<=[.!?]) +", t.strip())
    return parts[-1] if parts else t


# Each feature returns a NUMBER; the battery finds the best threshold in BOTH directions, so a
# feature that is anti-correlated is still credited (a floor does not care about sign).
FEATURES: Dict[str, Callable[[str], float]] = {
    "constant":                    lambda t: 0.0,
    "text_length_chars":           lambda t: float(len(t)),
    "text_length_words":           lambda t: float(len(t.split())),
    "last_sentence_length":        lambda t: float(len(_last_sentence(t).split())),
    "negation_cue_whole_text":     lambda t: float(len(NEG.findall(t))),
    "negation_cue_last_sentence":  lambda t: float(len(NEG.findall(_last_sentence(t)))),
    "positive_cue_last_sentence":  lambda t: float(len(POS.findall(_last_sentence(t)))),
    "question_marks":              lambda t: float(t.count("?")),
    "exclamations":                lambda t: float(t.count("!")),
    "quote_marks":                 lambda t: float(t.count('"') + t.count("'")),
    "comma_count":                 lambda t: float(t.count(",")),
    "n_sentences":                 lambda t: float(len(re.split(r"(?<=[.!?]) +", t.strip()))),
}


def _best_threshold_acc(x: np.ndarray, y: np.ndarray) -> float:
    """Best accuracy over every threshold AND both polarities. A floor may use either direction."""
    best = max(float((y == (y == y).astype(int)).mean()), 0.0)  # placeholder, replaced below
    best = 0.0
    for t in np.unique(x):
        for pred in ((x < t).astype(int), (x >= t).astype(int)):
            best = max(best, float((pred == y).mean()))
    return best


def run_battery(texts: Sequence[str], labels: Sequence[int], n_perm: int = 500,
                seed: int = 3) -> dict:
    """Every cheap baseline vs `labels` (1/0), each with a permutation null."""
    y = np.asarray(list(labels), dtype=int)
    if len(y) != len(texts) or len(y) < 20:
        raise ValueError(f"need >=20 aligned items, got {len(texts)} texts / {len(y)} labels")
    majority = float(max(y.mean(), 1 - y.mean()))
    rs = np.random.default_rng(seed)

    rows = []
    for name, fn in FEATURES.items():
        x = np.array([fn(t) for t in texts], dtype=float)
        if len(np.unique(x)) < 2:
            rows.append({"floor": name, "accuracy": majority, "null_p95": majority,
                         "clears_majority": False, "clears_own_null": False,
                         "margin_over_null": 0.0, "note": "degenerate (constant feature)"})
            continue
        acc = _best_threshold_acc(x, y)
        null = np.array([_best_threshold_acc(x, rs.permutation(y)) for _ in range(n_perm)])
        p95 = float(np.percentile(null, 95))
        # BOTH comparisons are reported, because they answer different questions and one of them
        # flatters. `clears_majority` alone marked `quote_marks` (0.7222) and `question_marks`
        # (0.6667) as beating the majority floor on a real bank while each sat EXACTLY AT ITS OWN
        # NULL -- i.e. that accuracy is reachable by fitting a threshold to noise on 36 items.
        # A baseline at its null is a fitting artifact, not a signal.
        rows.append({"floor": name, "accuracy": acc, "null_p95": p95,
                     "clears_majority": bool(acc > majority),
                     "clears_own_null": bool(acc > p95),
                     "margin_over_null": round(acc - p95, 4), "note": ""})

    rows.sort(key=lambda r: -r["accuracy"])
    strongest = (rows[0]["floor"], rows[0]["accuracy"])
    real = [r for r in rows if r["clears_own_null"]]
    strongest_real = (real[0]["floor"], real[0]["accuracy"]) if real else None
    return {
        "n": len(y), "majority_floor": majority,
        "strongest": strongest,
        # The bar a mechanism must clear: the highest accuracy reachable by a trivial baseline,
        # INCLUDING one that is only fitting noise -- because that accuracy is reachable.
        "strongest_that_clears_its_own_null": strongest_real,
        # ...and the strongest baseline that is an actual SIGNAL. If these two differ, the gap is
        # what threshold-fitting buys on this sample size, which is worth knowing on its own.
        "strongest_beats_majority": bool(rows[0]["accuracy"] > majority),
        "rows": rows,
        "caveat": ("Thresholds are fitted on the scored data. Safe for a FLOOR (optimistic fitting "
                   "RAISES the bar), fatal for a treatment. A baseline beating an organ is a "
                   "statement about the organ's evidence, never a recommendation to ship the "
                   "baseline."),
    }


def _self_test() -> int:
    ok = True
    rng = np.random.default_rng(1)

    # POSITIVE: a signal the battery MUST find -- negation in the last sentence marks the label.
    #
    # THE FIRST VERSION OF THIS FIXTURE WAS CONFOUNDED AND THE BATTERY CAUGHT IT. Its negative class
    # read "It did not work out, not at all, number {i}" against a shorter positive class, so
    # `text_length_chars` separated the labels PERFECTLY (1.0000) and beat the planted negation
    # signal. That is the tool working: it found a stronger floor than the one I intended, in my own
    # test. Fixed here by matching word count and letting the index digits vary so raw length
    # OVERLAPS between classes.
    texts = ([f"She tried hard. It really worked out in the end, number {i}." for i in range(60)] +
             [f"She tried hard. It never worked out in the end, number {i}." for i in range(40)])
    labels = [1] * 60 + [0] * 40
    rep = run_battery(texts, labels, n_perm=120)
    name, acc = rep["strongest"]
    if not (name.startswith("negation") and acc > 0.95):
        print(f"  FAIL positive control: strongest={name} acc={acc:.4f}")
        ok = False
    else:
        print(f"  PASS positive control: found {name} at {acc:.4f}")

    # NEGATIVE: labels unrelated to the text -- nothing may beat majority by much.
    texts2 = [f"A sentence about item {i}. Another clause here." for i in range(100)]
    labels2 = list(rng.integers(0, 2, 100))
    rep2 = run_battery(texts2, labels2, n_perm=120)
    over = rep2["strongest"][1] - rep2["majority_floor"]
    if over > 0.20:
        print(f"  FAIL negative control: unrelated labels beat majority by {over:.3f}")
        ok = False
    else:
        print(f"  PASS negative control: best exceeds majority by only {over:.3f}")

    # The MAJORITY floor must always be reported, since it is the one everyone quotes.
    if not (0.5 <= rep["majority_floor"] <= 1.0):
        print("  FAIL: majority floor out of range")
        ok = False
    else:
        print(f"  PASS majority floor reported: {rep['majority_floor']:.4f}")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_self_test() if "--self-test" in sys.argv else (print(__doc__) or 0))
