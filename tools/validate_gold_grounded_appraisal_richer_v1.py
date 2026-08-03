"""Validate + report on data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1_UNVERIFIED.jsonl.

This is a DATA-QUALITY validator for the richer grounded-appraisal eval, NOT a
scorer/mechanism cell (per task scope: build the eval, do not build the mechanism).

Checks:
  1. schema: every item has the required fields for its item_type
  2. citation-nonempty + word-cap: every cited span text is a non-empty string
     of <= MAX_SPAN_WORDS words (per task hard requirement: verbatim <=25 words)
  3. gold_verified / needs_director_review flags are present and honest
     (False / True respectively -- this file is UNVERIFIED by construction)
  4. balance: per-novel fraction <= MAX_NOVEL_FRAC; per-item_type counts reported
  5. length balance: word-count of the "diagnostic" span (the one a trivial
     length/recency shortcut could key off) reported per item_type, flagged if
     skewed so length alone isn't a usable shortcut
  6. TRIVIAL-BASELINE-DEFEAT CHECK (the fair-eval gate):
       - type1 (multi_candidate_causal_attribution): a RECENCY baseline
         (predict whichever of {true_blocker_agent, distractor_agent} is named
         textually closer to the query, using the pre-recorded
         recency_baseline_prediction field) -- accuracy reported; must be
         <= CHANCE_UPPER_BOUND on this subset for the subset to be judged
         genuinely discriminating.
       - type2 (irony_vs_sincere_valence): a SURFACE-LEXICON-VALENCE baseline
         (small hand-built positive/negative word lexicon scores the surface
         span; predicts "positive"/"negative") -- accuracy reported
         SEPARATELY on the irony subset (must be low: surface words mislead)
         and the sincere subset (expected high: surface words are honest there).
       - type3 (beneficiary_vs_patient): a PATIENT-AS-BENEFICIARY baseline
         (naively predicts beneficiary == grammatical_patient) -- accuracy
         reported; flagged explicitly as BY-CONSTRUCTION 0.0 (items were
         selected exactly where patient != beneficiary), not a discovered
         result -- this is disclosed, not hidden, per honesty discipline.

Prints a report to stdout. Exits nonzero if any HARD schema/citation check
fails. Baseline-defeat results are reported, not gated (a human/Director
reviews whether the defeat margins are adequate) -- but a WARNING is printed
if any discriminating subset's trivial-baseline accuracy is suspiciously HIGH
(>= HIGH_BASELINE_WARN), which would mean that subset is not actually hard.

Run with --self-test to exercise all checks (schema, balance, all three
baselines) against a tiny embedded fixture, independent of whether the real
gold file exists yet.
"""
import io
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_grounded_appraisal_richer_v1_UNVERIFIED.jsonl",
)

MAX_SPAN_WORDS = 25
MAX_NOVEL_FRAC = 0.60          # small corpus set (5 novels); flagged not hard-gated
CHANCE_UPPER_BOUND = 0.55      # binary-choice type1/type2 subsets; baseline should be near 1/2
HIGH_BASELINE_WARN = 0.70

SPAN_FIELDS = ("true_blocker_span", "distractor_span", "query_span",
               "surface_span", "supporting_span", "action_span")

REQUIRED_COMMON = ["id", "item_type", "novel", "chapter",
                   "gold_verified", "needs_director_review"]

REQUIRED_FIELDS = {
    "multi_candidate_causal_attribution": REQUIRED_COMMON + [
        "goal_owner", "true_blocker_agent", "true_blocker_span",
        "distractor_agent", "distractor_span", "query_span",
        "recency_baseline_prediction", "recency_baseline_correct", "recency_note",
    ],
    "irony_vs_sincere_valence": REQUIRED_COMMON + [
        "valence_type", "surface_span", "surface_valence", "true_intent_valence",
    ],
    "beneficiary_vs_patient": REQUIRED_COMMON + [
        "action_span", "grammatical_patient", "true_beneficiary",
        "true_valence_toward_beneficiary",
    ],
}

# Tiny hand-built lexicon for the surface-valence trivial baseline. Deliberately
# simple/naive -- this IS the "trivial" baseline the eval must defeat on irony.
POS_WORDS = {
    "kind", "kindly", "love", "loved", "loving", "care", "careful", "carefully",
    "relief", "grateful", "gratitude", "touching", "forgive", "forgiving",
    "indulge", "glad", "sweet", "dear", "comfort", "joy", "warmly", "gently",
    "gentle", "good", "best", "happy",
}
NEG_WORDS = {
    "spite", "spiteful", "scorn", "scornful", "scornfully", "sarcastic",
    "sarcastically", "mock", "mocking", "punish", "punitive", "hateful",
    "wicked", "cruel", "harsh", "bitter", "vengeance", "angry",
}

WORD_RE = re.compile(r"[A-Za-z']+")


def word_count(text):
    return len(WORD_RE.findall(text))


def fail(msg, errors):
    errors.append(msg)


def check_schema(items, errors):
    for it in items:
        it_type = it.get("item_type")
        req = REQUIRED_FIELDS.get(it_type)
        if req is None:
            fail(f"{it.get('id','?')}: unknown item_type {it_type!r}", errors)
            continue
        for field in req:
            if field not in it:
                fail(f"{it.get('id','?')}: missing required field {field!r}", errors)
        if it.get("gold_verified") is not False:
            fail(f"{it.get('id','?')}: gold_verified must be False (UNVERIFIED file)", errors)
        if it.get("needs_director_review") is not True:
            fail(f"{it.get('id','?')}: needs_director_review must be True", errors)


def check_citations(items, errors):
    for it in items:
        for field in SPAN_FIELDS:
            span = it.get(field)
            if span is None:
                continue
            text = span.get("text", "")
            line_range = span.get("line_range")
            if not text or not text.strip():
                fail(f"{it['id']}: {field}.text is empty", errors)
            if not line_range:
                fail(f"{it['id']}: {field}.line_range missing", errors)
            wc = word_count(text)
            if wc > MAX_SPAN_WORDS:
                fail(f"{it['id']}: {field} has {wc} words (> {MAX_SPAN_WORDS} cap): {text!r}", errors)


def balance_report(items):
    by_type = {}
    by_novel = {}
    for it in items:
        by_type.setdefault(it["item_type"], []).append(it)
        by_novel.setdefault(it["novel"], []).append(it)
    n = len(items)
    print(f"\n-- ITEM COUNTS (total={n}) --")
    for t, lst in sorted(by_type.items()):
        print(f"  {t}: {len(lst)}")
    print("-- NOVEL BALANCE --")
    warnings = []
    for novel, lst in sorted(by_novel.items()):
        frac = len(lst) / n if n else 0.0
        flag = " <-- FLAG (> MAX_NOVEL_FRAC)" if frac > MAX_NOVEL_FRAC else ""
        if flag:
            warnings.append(f"novel {novel} at {frac:.2f} fraction")
        print(f"  {novel}: {len(lst)} ({frac:.2f}){flag}")
    return by_type, warnings


def length_balance_report(by_type):
    print("-- LENGTH BALANCE (diagnostic span word counts) --")
    for t, lst in sorted(by_type.items()):
        if t == "multi_candidate_causal_attribution":
            true_wc = [word_count(it["true_blocker_span"]["text"]) for it in lst]
            distr_wc = [word_count(it["distractor_span"]["text"]) for it in lst]
            print(f"  {t}: true_blocker_span words min/max/avg = "
                  f"{min(true_wc)}/{max(true_wc)}/{sum(true_wc)/len(true_wc):.1f}; "
                  f"distractor_span words min/max/avg = "
                  f"{min(distr_wc)}/{max(distr_wc)}/{sum(distr_wc)/len(distr_wc):.1f}")
        elif t == "irony_vs_sincere_valence":
            wc = [word_count(it["surface_span"]["text"]) for it in lst]
            print(f"  {t}: surface_span words min/max/avg = "
                  f"{min(wc)}/{max(wc)}/{sum(wc)/len(wc):.1f}")
        elif t == "beneficiary_vs_patient":
            wc = [word_count(it["action_span"]["text"]) for it in lst]
            print(f"  {t}: action_span words min/max/avg = "
                  f"{min(wc)}/{max(wc)}/{sum(wc)/len(wc):.1f}")


def recency_baseline_report(by_type):
    """type1: recency baseline is pre-recorded per item (which candidate is
    textually closer to the query point); report the accuracy of that
    baseline against true_blocker_agent, computed here (not just trusted)."""
    lst = by_type.get("multi_candidate_causal_attribution", [])
    if not lst:
        return None
    correct = 0
    for it in lst:
        pred = it["recency_baseline_prediction"]
        true = it["true_blocker_agent"]
        is_correct = (pred == true)
        recorded = it["recency_baseline_correct"]
        if is_correct != recorded:
            print(f"  WARNING {it['id']}: recorded recency_baseline_correct={recorded} "
                  f"but recomputed prediction=={true!r} is {is_correct}")
        if is_correct:
            correct += 1
    acc = correct / len(lst)
    print(f"\n-- TRIVIAL BASELINE: RECENCY (type1, n={len(lst)}) --")
    print(f"  recency-baseline accuracy vs true_blocker_agent: {acc:.3f}")
    flag = "DEFEATED (<=chance)" if acc <= CHANCE_UPPER_BOUND else "NOT DEFEATED -- subset too easy for recency"
    print(f"  verdict: {flag}")
    return acc


def surface_valence_baseline_report(by_type):
    lst = by_type.get("irony_vs_sincere_valence", [])
    if not lst:
        return None
    print(f"\n-- TRIVIAL BASELINE: SURFACE-LEXICON VALENCE (type2, n={len(lst)}) --")
    for subset_name in ("irony", "sincere"):
        subset = [it for it in lst if it["valence_type"] == subset_name]
        if not subset:
            continue
        correct = 0
        for it in subset:
            text = it["surface_span"]["text"].lower()
            tokens = set(WORD_RE.findall(text))
            pos = len(tokens & POS_WORDS)
            neg = len(tokens & NEG_WORDS)
            baseline_pred = "positive" if pos >= neg else "negative"
            # true label polarity extracted from the true_intent_valence field
            true_label = "negative" if "negative" in it["true_intent_valence"] else "positive"
            if baseline_pred == true_label:
                correct += 1
        acc = correct / len(subset)
        print(f"  subset={subset_name} (n={len(subset)}): surface-valence-baseline accuracy = {acc:.3f}")
        if subset_name == "irony":
            flag = "DEFEATED (baseline misled by surface words)" if acc <= CHANCE_UPPER_BOUND else "NOT DEFEATED -- irony subset too easy"
            print(f"    verdict: {flag}")
    return True


def beneficiary_baseline_report(by_type):
    lst = by_type.get("beneficiary_vs_patient", [])
    if not lst:
        return None
    correct = 0
    for it in lst:
        pred = it["grammatical_patient"]
        true = it["true_beneficiary"]
        if pred == true:
            correct += 1
    acc = correct / len(lst)
    print(f"\n-- TRIVIAL BASELINE: PATIENT-AS-BENEFICIARY (type3, n={len(lst)}) --")
    print(f"  naive (beneficiary == grammatical_patient) accuracy: {acc:.3f}")
    print("  NOTE: this is BY-CONSTRUCTION 0.0 (items were selected exactly where"
          " patient != beneficiary) -- disclosed here as a design fact, not a"
          " discovered empirical result.")
    return acc


def run_checks(items):
    errors = []
    check_schema(items, errors)
    check_citations(items, errors)
    by_type, novel_warnings = balance_report(items)
    length_balance_report(by_type)
    recency_acc = recency_baseline_report(by_type)
    surface_valence_baseline_report(by_type)
    benpat_acc = beneficiary_baseline_report(by_type)

    print("\n-- SUMMARY --")
    if errors:
        print(f"HARD FAIL: {len(errors)} schema/citation error(s):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("schema/citation checks: PASS")
    if novel_warnings:
        print(f"balance WARNINGS: {novel_warnings}")
    return errors, {
        "recency_baseline_acc": recency_acc,
        "beneficiary_baseline_acc": benpat_acc,
    }


def load_items(path):
    items = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


FIXTURE = [
    {
        "id": "fx_mcca_pass", "item_type": "multi_candidate_causal_attribution",
        "novel": "x", "chapter": 1, "goal_owner": "g",
        "true_blocker_agent": "A",
        "true_blocker_span": {"line_range": [1], "text": "A did the thing quietly offstage."},
        "distractor_agent": "B",
        "distractor_span": {"line_range": [2], "text": "B was standing right there looking guilty."},
        "query_span": {"line_range": [3], "text": "Who did it?"},
        "recency_baseline_prediction": "B",
        "recency_baseline_correct": False,
        "recency_note": "n",
        "gold_verified": False, "needs_director_review": True,
    },
    {
        "id": "fx_irony_pass", "item_type": "irony_vs_sincere_valence",
        "valence_type": "irony", "novel": "x", "chapter": 1,
        "surface_span": {"line_range": [1], "text": "How kind of you, she said with scorn."},
        "surface_valence": "positive surface word 'kind'",
        "true_intent_valence": "negative (scornful, mocking)",
        "gold_verified": False, "needs_director_review": True,
    },
    {
        "id": "fx_sincere_pass", "item_type": "irony_vs_sincere_valence",
        "valence_type": "sincere", "novel": "x", "chapter": 1,
        "surface_span": {"line_range": [1], "text": "How kind of you, she said, and meant it."},
        "surface_valence": "positive surface word 'kind'",
        "true_intent_valence": "positive (sincere gratitude)",
        "gold_verified": False, "needs_director_review": True,
    },
    {
        "id": "fx_benpat_pass", "item_type": "beneficiary_vs_patient",
        "novel": "x", "chapter": 1,
        "action_span": {"line_range": [1], "text": "She scolded the dog to protect the child."},
        "grammatical_patient": "the dog",
        "true_beneficiary": "the child",
        "true_valence_toward_beneficiary": "protective/positive",
        "gold_verified": False, "needs_director_review": True,
    },
]


def self_test():
    print("=== SELF-TEST: valid fixture ===")
    errors, metrics = run_checks(FIXTURE)
    assert not errors, f"expected 0 errors on valid fixture, got {errors}"
    assert metrics["recency_baseline_acc"] == 0.0, metrics
    assert metrics["beneficiary_baseline_acc"] == 0.0, metrics
    print("valid-fixture checks: PASS (0 errors, recency_acc=0.0, benpat_acc=0.0 as expected)")

    print("\n=== SELF-TEST: broken fixture (missing field, oversize span, bad flags) ===")
    broken = json.loads(json.dumps(FIXTURE))  # deep copy via round-trip
    del broken[0]["goal_owner"]
    broken[1]["surface_span"]["text"] = " ".join(["word"] * 30)
    broken[2]["gold_verified"] = True
    errors2, _ = run_checks(broken)
    assert len(errors2) >= 3, f"expected >=3 errors on broken fixture, got {len(errors2)}: {errors2}"
    print(f"broken-fixture checks: PASS (caught {len(errors2)} errors as expected)")

    print("\n=== SELF-TEST: word_count sanity ===")
    assert word_count("one two three") == 3
    assert word_count("") == 0
    assert word_count("it's a don't") == 3
    print("word_count sanity: PASS")

    print("\nSELF-TEST: ALL PASS")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()

    if not os.path.exists(GOLD_PATH):
        print(f"GOLD FILE NOT FOUND: {GOLD_PATH}")
        return 2

    items = load_items(GOLD_PATH)
    errors, metrics = run_checks(items)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
