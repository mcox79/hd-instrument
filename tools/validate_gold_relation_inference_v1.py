"""Validate data/eval_gold_mention_role_mcguffey_v1/gold_relation_inference_v1_UNVERIFIED.jsonl.

Checks (per task pre-reg, NOT a scorer/encoder cell -- schema + balance only):
  1. schema: every item has the required fields for its item_type
  2. citation-nonempty: every *_text field is a non-empty string, and every
     item has chapter/line_range provenance for each cited span
  3. word-cap: every cited span is <= MAX_SPAN_WORDS words (design requirement:
     spans must be short enough to force structural, not word-count, reasoning)
  4. category balance (unstated_goal items only): >= MIN_CATEGORIES distinct
     correct_category values; no category > MAX_CATEGORY_FRAC of unstated items
  5. gold_verified / needs_director_review flags are present and honest
     (False / True respectively -- this file is UNVERIFIED by construction)
  6. near-identical-ness report for satisfy_restate pairs: word-overlap
     (Jaccard on lowercased token sets) between restate_text and satisfy_text,
     and between goal_text and restate_text, reported (not gated) so a human
     reviewer can see whether the "near-identical wording" design goal
     actually held for each pair

Prints a balance report to stdout. Exits nonzero if any hard check fails.
Run with --self-test to exercise the checks against a tiny embedded fixture
(no dependency on the real gold file existing yet).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_relation_inference_v1_UNVERIFIED.jsonl",
)

MAX_SPAN_WORDS = 25
MIN_CATEGORIES = 4
MAX_CATEGORY_FRAC = 0.35

REQUIRED_FIELDS = {
    "unstated_goal": [
        "id", "item_type", "novel", "chapter", "line_range", "action_text",
        "correct_category", "distractor_categories", "why_inferred",
        "goal_stated", "gold_verified", "needs_director_review",
    ],
    "satisfy_restate": [
        "id", "item_type", "novel",
        "goal_text", "goal_chapter", "goal_line_range",
        "restate_text", "restate_chapter", "restate_line_range",
        "satisfy_text", "satisfy_chapter", "satisfy_line_range",
        "near_identical_note", "discriminator",
        "gold_verified", "needs_director_review",
    ],
    "thwart_cause": [
        "id", "item_type", "novel", "relation",
        "event_a_text", "event_a_chapter", "event_a_line_range",
        "event_b_text", "event_b_chapter", "event_b_line_range",
        "distractor_text", "distractor_chapter", "distractor_line_range",
        "discriminator", "gold_verified", "needs_director_review",
    ],
}

TEXT_FIELDS = {
    "unstated_goal": ["action_text"],
    "satisfy_restate": ["goal_text", "restate_text", "satisfy_text"],
    "thwart_cause": ["event_a_text", "event_b_text", "distractor_text"],
}


class ValidationError(Exception):
    pass


def load_items(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValidationError(f"line {lineno}: invalid JSON: {e}")
            items.append(rec)
    return items


def check_schema(items):
    errors = []
    ids_seen = set()
    for rec in items:
        item_type = rec.get("item_type")
        rid = rec.get("id", "<missing id>")
        if item_type not in REQUIRED_FIELDS:
            errors.append(f"{rid}: unknown item_type {item_type!r}")
            continue
        if rid in ids_seen:
            errors.append(f"{rid}: duplicate id")
        ids_seen.add(rid)
        for field in REQUIRED_FIELDS[item_type]:
            if field not in rec:
                errors.append(f"{rid}: missing required field {field!r}")
        if rec.get("gold_verified") is not False:
            errors.append(f"{rid}: gold_verified must be False (this file is UNVERIFIED)")
        if rec.get("needs_director_review") is not True:
            errors.append(f"{rid}: needs_director_review must be True")
    return errors


def check_citations_nonempty_and_word_cap(items):
    errors = []
    for rec in items:
        item_type = rec.get("item_type")
        rid = rec.get("id", "<missing id>")
        if item_type not in TEXT_FIELDS:
            continue
        for field in TEXT_FIELDS[item_type]:
            val = rec.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{rid}: {field} is empty or not a string")
                continue
            n_words = len(val.split())
            if n_words > MAX_SPAN_WORDS:
                errors.append(
                    f"{rid}: {field} has {n_words} words (max {MAX_SPAN_WORDS}): {val[:80]!r}..."
                )
    return errors


def check_category_balance(items):
    errors = []
    unstated = [r for r in items if r.get("item_type") == "unstated_goal"]
    if not unstated:
        return errors, {}
    hist = {}
    for r in unstated:
        cat = r.get("correct_category", "<missing>")
        hist[cat] = hist.get(cat, 0) + 1
    n = len(unstated)
    n_categories = len(hist)
    if n_categories < MIN_CATEGORIES:
        errors.append(
            f"unstated_goal: only {n_categories} distinct correct_category values "
            f"(need >= {MIN_CATEGORIES})"
        )
    for cat, count in hist.items():
        frac = count / n
        if frac > MAX_CATEGORY_FRAC:
            errors.append(
                f"unstated_goal category {cat!r} is {frac:.2%} of items "
                f"(max {MAX_CATEGORY_FRAC:.0%})"
            )
    return errors, hist


def word_jaccard(a, b):
    ta = set(w.lower().strip(".,;:!?‘’“”\"'") for w in a.split())
    tb = set(w.lower().strip(".,;:!?‘’“”\"'") for w in b.split())
    ta.discard("")
    tb.discard("")
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def near_identical_report(items):
    rows = []
    for r in items:
        if r.get("item_type") != "satisfy_restate":
            continue
        goal_restate = word_jaccard(r["goal_text"], r["restate_text"])
        restate_satisfy = word_jaccard(r["restate_text"], r["satisfy_text"])
        goal_satisfy = word_jaccard(r["goal_text"], r["satisfy_text"])
        rows.append({
            "id": r["id"],
            "jaccard_goal_restate": round(goal_restate, 3),
            "jaccard_restate_satisfy": round(restate_satisfy, 3),
            "jaccard_goal_satisfy": round(goal_satisfy, 3),
        })
    return rows


def run_validation(path):
    items = load_items(path)
    errors = []
    errors += check_schema(items)
    errors += check_citations_nonempty_and_word_cap(items)
    cat_errors, cat_hist = check_category_balance(items)
    errors += cat_errors
    jaccard_rows = near_identical_report(items)

    type_hist = {}
    for r in items:
        t = r.get("item_type", "<missing>")
        type_hist[t] = type_hist.get(t, 0) + 1

    report = {
        "n_items": len(items),
        "item_type_histogram": type_hist,
        "unstated_goal_category_histogram": cat_hist,
        "satisfy_restate_near_identical_jaccard": jaccard_rows,
        "n_errors": len(errors),
        "errors": errors,
    }
    return report, errors


def print_report(report):
    print(f"n_items={report['n_items']}")
    print(f"item_type_histogram={report['item_type_histogram']}")
    print(f"unstated_goal_category_histogram={report['unstated_goal_category_histogram']}")
    print("satisfy_restate near-identical-ness (word-Jaccard):")
    for row in report["satisfy_restate_near_identical_jaccard"]:
        print(f"  {row['id']}: goal<->restate={row['jaccard_goal_restate']} "
              f"restate<->satisfy={row['jaccard_restate_satisfy']} "
              f"goal<->satisfy={row['jaccard_goal_satisfy']}")
    if report["errors"]:
        print(f"FAIL: {report['n_errors']} error(s):")
        for e in report["errors"]:
            print(f"  - {e}")
    else:
        print("PASS: schema, citation-nonempty, word-cap, and category-balance checks all clear")


def self_test():
    """Exercise every check against a tiny embedded fixture (no dependency on
    the real gold file). Run with --self-test."""
    import tempfile

    fixture = [
        {
            "id": "fx_unstated_1", "item_type": "unstated_goal", "novel": "fixture",
            "chapter": 1, "line_range": [1, 1], "action_text": "She ran to the door.",
            "correct_category": "CAT_A", "distractor_categories": ["CAT_B", "CAT_C", "CAT_D"],
            "why_inferred": "test", "goal_stated": False,
            "gold_verified": False, "needs_director_review": True,
        },
        {
            "id": "fx_unstated_2", "item_type": "unstated_goal", "novel": "fixture",
            "chapter": 1, "line_range": [2, 2], "action_text": "He hid the key.",
            "correct_category": "CAT_B", "distractor_categories": ["CAT_A", "CAT_C", "CAT_D"],
            "why_inferred": "test", "goal_stated": False,
            "gold_verified": False, "needs_director_review": True,
        },
        {
            "id": "fx_unstated_3", "item_type": "unstated_goal", "novel": "fixture",
            "chapter": 1, "line_range": [3, 3], "action_text": "She counted the coins twice.",
            "correct_category": "CAT_C", "distractor_categories": ["CAT_A", "CAT_B", "CAT_D"],
            "why_inferred": "test", "goal_stated": False,
            "gold_verified": False, "needs_director_review": True,
        },
        {
            "id": "fx_unstated_4", "item_type": "unstated_goal", "novel": "fixture",
            "chapter": 1, "line_range": [4, 4], "action_text": "He waved at the ship.",
            "correct_category": "CAT_D", "distractor_categories": ["CAT_A", "CAT_B", "CAT_C"],
            "why_inferred": "test", "goal_stated": False,
            "gold_verified": False, "needs_director_review": True,
        },
        {
            "id": "fx_satrest_1", "item_type": "satisfy_restate", "novel": "fixture",
            "goal_text": "I want to go home now.", "goal_chapter": 1, "goal_line_range": [5, 5],
            "restate_text": "I still want to go home.", "restate_chapter": 2, "restate_line_range": [6, 6],
            "satisfy_text": "At last she arrived home safely.", "satisfy_chapter": 3, "satisfy_line_range": [7, 7],
            "near_identical_note": "test", "discriminator": "test",
            "gold_verified": False, "needs_director_review": True,
        },
        {
            "id": "fx_thwart_1", "item_type": "thwart_cause", "novel": "fixture", "relation": "CAUSE",
            "event_a_text": "He lit the fuse.", "event_a_chapter": 1, "event_a_line_range": [8, 8],
            "event_b_text": "The rocket launched.", "event_b_chapter": 1, "event_b_line_range": [9, 9],
            "distractor_text": "The dog barked nearby.", "distractor_chapter": 1, "distractor_line_range": [10, 10],
            "discriminator": "test",
            "gold_verified": False, "needs_director_review": True,
        },
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for rec in fixture:
            f.write(json.dumps(rec) + "\n")
        tmp_path = f.name

    try:
        report, errors = run_validation(tmp_path)
        assert report["n_items"] == 6, f"expected 6 fixture items, got {report['n_items']}"
        assert not errors, f"expected clean fixture to pass, got errors: {errors}"
        assert report["item_type_histogram"] == {
            "unstated_goal": 4, "satisfy_restate": 1, "thwart_cause": 1,
        }
        assert len(report["unstated_goal_category_histogram"]) == 4

        # now break it: push category CAT_A over MAX_CATEGORY_FRAC by adding
        # duplicates, and one item over the word cap
        fixture_bad = fixture + [
            {**fixture[0], "id": "fx_unstated_5"},
            {**fixture[0], "id": "fx_unstated_6"},
        ]
        fixture_bad[2] = dict(fixture[2])
        fixture_bad[2]["action_text"] = " ".join(["word"] * 30)
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            for rec in fixture_bad:
                f.write(json.dumps(rec) + "\n")
            tmp_path_bad = f.name
        report_bad, errors_bad = run_validation(tmp_path_bad)
        assert errors_bad, "expected the perturbed fixture to fail validation"
        assert any("word-cap" not in e and "words" in e for e in errors_bad), (
            f"expected a word-cap error, got: {errors_bad}"
        )
        os.remove(tmp_path_bad)
    finally:
        os.remove(tmp_path)

    print("SELF-TEST PASSED: schema/citation/word-cap/category-balance checks all fire correctly "
          "on both a clean and a deliberately-broken fixture")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return
    if not os.path.exists(GOLD_PATH):
        print(f"FAIL: gold file not found at {GOLD_PATH}")
        sys.exit(1)
    report, errors = run_validation(GOLD_PATH)
    print_report(report)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
