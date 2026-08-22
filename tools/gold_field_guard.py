"""WHICH GOLD FIELD IS THE RIGHT ONE? -- a guard for the category error I made TWICE in one session.

WHY THIS EXISTS. Scoring an organ needs a gold column, and a bank often ships several that look
interchangeable. On 2026-08-22 I got it wrong twice against the same bank:

  1. `find_desired_state(...)["referent"]` scored against `goal_owner`. `referent` returns the THING
     DESIRED ("wanted", "courage", "piano"); `goal_owner` is the PERSON. Result: a flat 0/44.
     Caught immediately -- an exactly-zero score with 28 non-empty predictions is obviously a
     category error, and this repo already has a rule for it.

  2. `select_outcome_owner` scored against `goal_owner` instead of `gold_outcome_owner`. The two
     differ on only 3 of 44 rows, so the wrong field produced 0.5682 instead of 0.6136 -- A PLAUSIBLE
     NUMBER THAT FITTED THE STORY I WAS ALREADY TELLING. It also manufactured an exact tie with the
     recency baseline, on which I then built an "is the organ just recency in disguise?" analysis.
     Nothing would have caught it except asking what the field means.

**THE SECOND KIND IS THE DANGEROUS ONE.** A wrong field that is wildly wrong announces itself. A
wrong field that is NEARLY right does not, and it biases every downstream comparison silently.

WHAT THIS DOES. Given the bank's rows and a REFERENCE set of gold values -- typically the `gold`
column of an existing baselines file, i.e. what previously-published numbers were scored against --
it reports how well each candidate field matches, and REFUSES when the choice is ambiguous.

    from tools.gold_field_guard import pick_gold_field
    pick_gold_field(rows, reference)   # -> {"field": "gold_outcome_owner", "match": 1.0, ...}

USE THE REFERENCE FROM WHATEVER YOU ARE COMPARING AGAINST. The point is not to find "the true gold"
in the abstract -- it is to score YOUR arm against the SAME column the numbers you are comparing to
were scored against. That is this project's standing rule (no number crosses populations) applied to
the column rather than the rows.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
from typing import Dict, List, Sequence


def _norm(v) -> str:
    return str(v if v is not None else "").strip().lower()


def field_match_rates(rows: Sequence[dict], reference: Sequence[str]) -> Dict[str, float]:
    """For every field present in the rows, the fraction of rows whose value equals the reference."""
    if len(rows) != len(reference):
        raise ValueError(f"{len(rows)} rows but {len(reference)} reference values")
    ref = [_norm(r) for r in reference]
    fields = sorted({k for r in rows for k in r.keys()})
    out = {}
    for f in fields:
        vals = [_norm(r.get(f)) for r in rows]
        if not any(vals):
            continue
        out[f] = sum(1 for a, b in zip(vals, ref) if a == b) / len(ref)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def pick_gold_field(rows: Sequence[dict], reference: Sequence[str],
                    min_match: float = 0.99, ambiguity_margin: float = 0.05) -> dict:
    """The field the reference was scored against, or a refusal.

    REFUSES on ambiguity rather than guessing: if the runner-up is within `ambiguity_margin`, the
    choice is not determined by the data and picking silently is exactly the failure this guards."""
    rates = field_match_rates(rows, reference)
    if not rates:
        raise AssertionError("no field in these rows matches the reference at all -- wrong bank?")
    items = list(rates.items())
    best_f, best_r = items[0]
    second = items[1] if len(items) > 1 else (None, 0.0)

    if best_r < min_match:
        raise AssertionError(
            f"NO field matches the reference well enough (best: {best_f} at {best_r:.4f} < "
            f"{min_match}). The reference was probably scored against a column this bank does not "
            f"carry, or against a different row order.")
    if second[0] is not None and (best_r - second[1]) < ambiguity_margin and second[1] >= min_match:
        raise AssertionError(
            f"AMBIGUOUS: {best_f} ({best_r:.4f}) and {second[0]} ({second[1]:.4f}) both match. "
            f"Choosing silently is how a nearly-right column produces a plausible wrong number.")
    return {"field": best_f, "match": best_r,
            "runner_up": second[0], "runner_up_match": second[1],
            "all_rates": rates,
            "note": ("Score your arm against THIS column -- the one the numbers you are comparing "
                     "to were scored against.")}


def _self_test() -> int:
    ok = True
    # The real 2026-08-22 shape: two near-identical owner columns differing on a few rows.
    rows = ([{"goal_owner": "jo", "gold_outcome_owner": "jo", "other": "x"}] * 41 +
            [{"goal_owner": "meg", "gold_outcome_owner": "amy", "other": "x"}] * 3)
    reference = ["jo"] * 41 + ["amy"] * 3          # what the baselines actually scored against

    got = pick_gold_field(rows, reference)
    if got["field"] != "gold_outcome_owner":
        print(f"  FAIL: picked {got['field']!r}, expected 'gold_outcome_owner'")
        ok = False
    else:
        print(f"  PASS picks the right column: {got['field']} at {got['match']:.4f} "
              f"(runner-up {got['runner_up']} at {got['runner_up_match']:.4f})")

    # AMBIGUITY must REFUSE, not guess -- two columns that agree everywhere.
    rows2 = [{"a": "x", "b": "x"}] * 30
    try:
        pick_gold_field(rows2, ["x"] * 30)
        print("  FAIL: identical columns were resolved silently")
        ok = False
    except AssertionError as e:
        print(f"  PASS refuses on ambiguity: {str(e)[:70]}...")

    # NO match must REFUSE loudly rather than returning the least-bad column.
    try:
        pick_gold_field([{"a": "x"}] * 30, ["zzz"] * 30)
        print("  FAIL: a reference matching nothing was accepted")
        ok = False
    except AssertionError as e:
        print(f"  PASS refuses when nothing matches: {str(e)[:60]}...")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_self_test() if "--self-test" in sys.argv else (print(__doc__) or 0))
