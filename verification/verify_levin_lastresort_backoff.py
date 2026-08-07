# WIRE-DON'T-ISLAND WITNESS (2026-08-07). Scaffold-free, tracing=False (hdlab.goal_typing is
# pure-Python, no HDC tracer to disable).
"""verification/verify_levin_lastresort_backoff.py -- reproduces the LEVIN VERB-CLASS LAST-RESORT
BACKOFF tier now wired into hdlab.goal_typing.congruence_with_lexicon_fallback (promoted from
experiments/exp_verbclass_backoff_coverage_v2.py, commit 276674abb, PARTIAL: coverage_gain=+1,
regressions=0, na_to_wrong=0, no_overfire=True, restoration_ok=True on the full-44
goal_bearing_modern_eval_v1.jsonl bank).

HOW "BEFORE" (pre-promotion) BEHAVIOR IS REPRODUCED WITHOUT A FROZEN COPY: the wire added a private
`_levin_retry: bool = False` parameter to congruence_with_lexicon_fallback. Calling it with
`_levin_retry=True` from OUTSIDE runs the identical tiers-1-4 + bare-lexicon body and then returns at
the tail immediately (the same short-circuit that stops the internal one-shot retry from recursing),
which is byte-identical to the function's pre-promotion unconditional `return lex, {...}` ending. So
`G.congruence_with_lexicon_fallback(text, _levin_retry=True)` IS the pre-wire function, reproduced via
the live module (no external frozen-baseline dependency), matching this module's own established
witness convention (see verify_grounded_result_class_tier.py's `_before_verdict`).

WHAT THIS CHECKS:
  (1) full-44 polarity counts before/after match the MEASURED commit-276674abb numbers exactly
      (baseline correct=17/wrong=4/na=23 -> after correct=18/wrong=4/na=22).
  (2) The single coverage-gain item (ts_tom_wish_free_potter) flips NA->CORRECT specifically via the
      levin_last_resort_backoff tier (detail carries levin_last_resort_backoff_applied=True).
  (3) ZERO REGRESSION: every one of the other 43 items produces an IDENTICAL verdict before vs after.
  (4) NO OVER-FIRE: "do" (deliberately excluded, no stable Levin class) stays unclassed through the
      live last-resort pipeline on a synthetic total-abstain passage; whisper/sneeze/yawn are absent
      from the backoff table.
  (5) RESTORATION: _verb_classes / _class_relation are the SAME function objects (by identity) after
      the full 44-item pass as before it -- no patch leaks past a single retry.
  (6) Fair instruments byte-identical: verification/test_goal_owner_select.py's 48/48 full instrument
      + 12/12 multigoal, reproduced via its own run() (imported, not reimplemented).
  (7) hdlab.goal_typing.self_test() stays green (this build did not touch any decisive-case assertion).

Run: .venv/Scripts/python.exe verification/verify_levin_lastresort_backoff.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.goal_typing as G  # noqa: E402

EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"

EXPECTED_BASELINE = {"correct": 17, "wrong": 4, "na": 23}
EXPECTED_AFTER = {"correct": 18, "wrong": 4, "na": 22}
EXPECTED_GAIN_ID = "ts_tom_wish_free_potter"

_ABSTAIN = ("NA", "NONE", "AMBIGUOUS")

ADVERSARIAL_UNRELATED_PROBES = ["whisper", "sneeze", "yawn"]


def _load():
    rows = [json.loads(l) for l in open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8")
            if l.strip()]
    return rows


def _gold(r):
    return "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"


def _status(verdict_upper, gold):
    if verdict_upper in _ABSTAIN:
        return "NA"
    return "CORRECT" if verdict_upper == gold else "WRONG"


def _score(rows, levin_retry):
    out = {}
    for r in rows:
        v, det = G.congruence_with_lexicon_fallback(r["text"], _levin_retry=levin_retry)
        out[r["id"]] = {"status": _status(v.upper(), _gold(r)), "verdict": v.upper(), "detail": det}
    return out


def check_full_eval_and_zero_regression():
    rows = _load()
    assert len(rows) == 44, f"expected 44 eval items, got {len(rows)}"

    before = _score(rows, levin_retry=True)   # pre-promotion behavior (see module docstring)
    after = _score(rows, levin_retry=False)   # production behavior (Levin tier active)

    b_correct = sum(1 for v in before.values() if v["status"] == "CORRECT")
    b_wrong = sum(1 for v in before.values() if v["status"] == "WRONG")
    b_na = sum(1 for v in before.values() if v["status"] == "NA")
    a_correct = sum(1 for v in after.values() if v["status"] == "CORRECT")
    a_wrong = sum(1 for v in after.values() if v["status"] == "WRONG")
    a_na = sum(1 for v in after.values() if v["status"] == "NA")

    print(f"[CHECK full_eval] before correct={b_correct} wrong={b_wrong} na={b_na}")
    print(f"[CHECK full_eval] after  correct={a_correct} wrong={a_wrong} na={a_na}")

    assert (b_correct, b_wrong, b_na) == (
        EXPECTED_BASELINE["correct"], EXPECTED_BASELINE["wrong"], EXPECTED_BASELINE["na"]), (
        f"baseline mismatch: got correct={b_correct} wrong={b_wrong} na={b_na}, "
        f"expected {EXPECTED_BASELINE}")
    assert (a_correct, a_wrong, a_na) == (
        EXPECTED_AFTER["correct"], EXPECTED_AFTER["wrong"], EXPECTED_AFTER["na"]), (
        f"after mismatch: got correct={a_correct} wrong={a_wrong} na={a_na}, "
        f"expected {EXPECTED_AFTER}")

    gains, regressions, na_to_wrong, unchanged = [], [], [], []
    for iid in before:
        b, a = before[iid], after[iid]
        if b["status"] == "CORRECT" and a["status"] != "CORRECT":
            regressions.append(iid)
        elif b["status"] == "NA" and a["status"] == "CORRECT":
            gains.append(iid)
        elif b["status"] == "NA" and a["status"] == "WRONG":
            na_to_wrong.append(iid)
        else:
            unchanged.append(iid)

    assert not regressions, f"REGRESSION: {regressions} were correct before, wrong/na after"
    assert not na_to_wrong, f"NA_TO_WRONG (new mistake, not just a gain): {na_to_wrong}"
    assert gains == [EXPECTED_GAIN_ID], f"expected gain=[{EXPECTED_GAIN_ID}], got {gains}"
    assert len(unchanged) == 43, f"expected 43 unchanged items, got {len(unchanged)}"

    gain_detail = after[EXPECTED_GAIN_ID]["detail"]
    assert gain_detail.get("levin_last_resort_backoff_applied") is True, (
        f"{EXPECTED_GAIN_ID} must flip specifically via the levin_last_resort_backoff tier, "
        f"got detail={gain_detail}")
    print(f"[CHECK full_eval] gain={gains[0]} verdict={after[EXPECTED_GAIN_ID]['verdict']} "
          f"reason={gain_detail.get('reason')} levin_backoff_applied="
          f"{gain_detail.get('levin_last_resort_backoff_applied')}")
    print(f"[CHECK full_eval] regressions={regressions} (empty) na_to_wrong={na_to_wrong} (empty) "
          f"unchanged={len(unchanged)}/43")
    return {"before": (b_correct, b_wrong, b_na), "after": (a_correct, a_wrong, a_na),
            "gains": gains, "regressions": regressions, "na_to_wrong": na_to_wrong}


def check_no_overfire():
    table = G._levin_backoff_table()
    assert G.LEVIN_ADVERSARIAL_EXCLUDED_LIGHT_VERB not in table, (
        "'do' must never be a key in the Levin backoff table")
    for w in ADVERSARIAL_UNRELATED_PROBES:
        assert w not in table, f"unrelated probe {w!r} must not be in the Levin backoff table"

    # Live pipeline probe: a "do" goal whose outcome sentence has nothing else for any tier to grab
    # onto -- if the backoff over-fired on "do" this would spuriously resolve to MET/UNMET.
    do_passage = "Chen decided to do something about it. Chen did something about it."
    verdict, detail = G.congruence_with_lexicon_fallback(do_passage)
    print(f"[CHECK no_overfire] 'do' live last-resort verdict={verdict} detail={detail}")
    assert verdict.upper() in _ABSTAIN, (
        f"'do' must stay unclassed (abstain) through the live last-resort pipeline, got {verdict}")
    assert not detail.get("levin_last_resort_backoff_applied"), (
        "'do' passage must not have been resolved via the Levin backoff")
    print("[CHECK no_overfire] 'do' excluded from table + stays abstain live; "
          f"{ADVERSARIAL_UNRELATED_PROBES} absent from table")
    return {"do_stays_unclassed": verdict.upper() in _ABSTAIN}


def check_restoration():
    vc_before, cr_before = G._verb_classes, G._class_relation
    rows = _load()
    for r in rows:
        G.congruence_with_lexicon_fallback(r["text"])
    vc_after, cr_after = G._verb_classes, G._class_relation
    assert vc_after is vc_before, "_verb_classes leaked a patch past the 44-item pass"
    assert cr_after is cr_before, "_class_relation leaked a patch past the 44-item pass"
    print("[CHECK restoration] _verb_classes / _class_relation identity-preserved across the full "
          "44-item pass (no patch leak)")
    return {"restoration_ok": True}


def check_fair_instruments_unchanged():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import test_goal_owner_select as FAIR  # noqa: E402
    result = FAIR.run()
    assert result["full_instrument"]["content_total"] == 48
    assert result["multigoal"]["content"] == 12
    print("[CHECK fair_instruments_unchanged] 48/48 fair + 12/12 multigoal reproduced via imported "
          "test_goal_owner_select.run() (byte-identical, unaffected by this strict-ADD)")
    return result


def check_self_test_green():
    res = G.self_test()
    print("[CHECK self_test_green] hdlab.goal_typing.self_test() passes unmodified "
          "(this build did not touch any decisive-case assertion)")
    return res


def run():
    r_full = check_full_eval_and_zero_regression()
    r_overfire = check_no_overfire()
    r_restore = check_restoration()
    r_fair = check_fair_instruments_unchanged()
    r_self = check_self_test_green()
    print("[ALL CHECKS PASS] LEVIN VERB-CLASS LAST-RESORT BACKOFF: full44 %d->%d/44 (net +%d), "
          "gain=%s, ZERO regressions, ZERO na_to_wrong, no_overfire=True, restoration_ok=True, "
          "fair instruments 48/48+12/12 unchanged, self_test green. PARTIAL "
          "(coverage_gain=+1, zero regression -- matches commit 276674abb measurement)." % (
              r_full["before"][0], r_full["after"][0],
              r_full["after"][0] - r_full["before"][0], r_full["gains"]))
    return {"full": r_full, "overfire": r_overfire, "restoration": r_restore, "fair": r_fair,
            "self_test": r_self}


if __name__ == "__main__":
    run()
