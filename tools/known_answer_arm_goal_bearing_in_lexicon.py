"""KNOWN-ANSWER ARM: score the consequence organ on the 8 in-lexicon sanity controls nobody runs.

WHY THIS EXISTS
---------------
`experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py:126` filters the
44-item `goal_bearing_modern_eval_v1` down to `outcome_in_lexicon is False` -> the 36 items
every consequence-learning number on this line rests on. ENUMERATED, not searched: grepping
every *.py in the repo for `outcome_in_lexicon` returns 7 hits, and every one of them filters
to `is False`. Within THIS cell the 8 in-lexicon items are leak-exclusion territory only (they
enter `_read_corpus_blocks` / `_exclusion_integrity` via `all_rows`) and are never scored.

CORRECTION, made before this was committed: an earlier draft said "SCORED BY NOBODY" and that
is FALSE. `exp_verbclass_backoff_coverage_v1`/`v2` load the bank with NO filter at all, read
`gold_outcome_polarity`, and score through this same `congruence_with_lexicon_fallback` -- so
the 8 ARE scored, inside an undifferentiated 44-item aggregate. I had enumerated a FIELD NAME
and drawn a conclusion about SELECTION; those cells do not filter by that field because they
do not filter. WHAT SURVIVES, and this half IS properly enumerated (the split requires that
field, and all 7 of its uses filter `is False`): no cell ISOLATES the 8 as a known-answer arm,
and none reports an in-lexicon vs OOV CONTRAST.

Their construction note (`notes/research_goal_bearing_modern_eval_2026-08-06.md`) calls them
"deliberately in-lexicon as sanity-check controls". Standing discipline 6 says a FLOOR tells
you whether the EFFECT is real and a KNOWN-ANSWER arm tells you whether the INSTRUMENT is --
run both. The known-answer arm has been sitting in the bank unrun since 2026-08-06.

ONE VARIABLE. Same bank, same gold field (`gold_outcome_polarity`), same scorer -- the LIVE
production `hdlab.goal_typing.congruence_with_lexicon_fallback`, IMPORTED not reimplemented.
The only thing that changes is whether the item's outcome verb is in the organ's own lexicon.

POWER, DECLARED BEFORE THE RUN (discipline 18: decide what n the instrument needs first)
----------------------------------------------------------------------------------------
The 8 in-lexicon items are 4 MET / 4 UNMET -- BALANCED, so chance and the majority floor are
both 0.500 here, unlike the OOV 36 where the floor is 0.639. Exact two-sided binomial vs 0.5:
    8/8 -> p = 0.0078    7/8 -> p = 0.0703    6/8 -> p = 0.2891
so ONLY 8/8 clears p<0.05, and 7/8 does not. THIS ARM CAN DEMONSTRATE COMPETENCE AND CANNOT
DEMONSTRATE INCOMPETENCE: a middling score is UNINFORMATIVE and will be reported as such, not
as a negative. That asymmetry is stated here so it cannot be discovered after seeing the number.

PREDICTIONS, WRITTEN BEFORE RUNNING (they differ per-item, so this is a can-fail discriminator)
-----------------------------------------------------------------------------------------------
H1  THE WALL IS OPEN VOCABULARY (the cell's own framing -- it is named `oov_outcome_verb`).
    Supplying the lexicon entry is exactly what these 8 items do, so the organ should get most
    of them: >= 6/8, with MET and UNMET both above half.
H2  THE WALL IS THE `UNMET` BIAS IN `congruence_with_lexicon_fallback` (the plan's current only
    live lead: MET recall 8/23 invariant, system says UNMET 21x of 36).
    Then the organ answers UNMET on most of the 8 REGARDLESS of the lexicon, scoring ~4/8 by
    getting the 4 UNMET right and the 4 MET wrong. THE PER-ITEM PATTERN SEPARATES THIS FROM H1
    even at n=8: H2 predicts a specific 4-right/4-wrong SPLIT BY CLASS, not a middling scatter.

POSITIVE CONTROL, AND THE ARM IS REFUSED IF IT FAILS
----------------------------------------------------
Arm A rescores the OOV 36 through the same import and MUST reproduce a documented number of
this cell to four digits. If it does not, this harness is not scoring what the cell scored and
the 8-item result means nothing -- the script refuses rather than printing it anyway.
("Make the arithmetic close to the reported number" -- three stories died to that check.)

⚠️ WHICH documented number, and this correction is load-bearing. The FIRST version of this
script targeted the landed primary `0.4722` and REFUSED, reading `0.3889`. The refusal was
right and my constant was wrong: **`0.3889` is EXACTLY the cell's documented EMPTY-map arm**
(plan: "EMPTY `0.3889` / AND-gate 18 words BALANCED `0.3056` / SOFT-COMBINE 125 words 96% NEG
`0.4722` (BEST)"). `0.4722` is the SOFT-COMBINE condition, which scores through
`_score_with_overlay` after registering ~125 lemmas LEARNED by reading the corpus.

**SO THIS PROBE RUNS THE EMPTY-OVERLAY CONDITION AND SAYS NOTHING ABOUT THE OVERLAY ONE.**
That is the right condition for THIS question and it is not a convenience: the overlay supplies
ACQUIRED outcome lemmas for verbs the base lexicon LACKS, and the 8 in-lexicon items have their
outcome verb in the BASE lexicon by construction -- so the comparison "in-lexicon vs OOV" is
exactly the one variable the empty condition isolates. State the condition beside any number
from here; do NOT place these against `0.4722`.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import math
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import congruence_with_lexicon_fallback  # noqa: E402

EVAL_REL = os.path.join("experiments", "data", "goal_bearing_modern_eval_v1.jsonl")
EMPTY_MAP_REF = 0.3889           # the cell's documented EMPTY-overlay arm (NOT the 0.4722 soft-combine)
LANDED_TOL = 0.0002              # it is quoted to four digits and reproduced to four digits


def fisher_exact_2x2(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]] (sum of tables no likelier than observed)."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def prob(x):
        return (math.comb(r1, x) * math.comb(n - r1, c1 - x)) / math.comb(n, c1)

    obs = prob(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= obs + 1e-12))


def two_sided_binomial(k, n, p=0.5):
    """Exact two-sided binomial p-value (sum of outcomes no more likely than the observed)."""
    def pmf(i):
        return math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12))


def load_rows():
    path = os.path.join(REPO_ROOT, EVAL_REL)
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def score(rows):
    """Score rows through the LIVE production function. Returns (n_correct, details)."""
    details = []
    for r in rows:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, detail = congruence_with_lexicon_fallback(r["text"])
        details.append({
            "id": r["id"],
            "outcome_lemma": r["outcome_verb_lemma"],
            "in_lexicon": r["outcome_in_lexicon"],
            "gold": gold,
            "pred": pred,
            "reason": (detail or {}).get("reason"),
            "correct": pred == gold,
        })
    return sum(d["correct"] for d in details), details


def report(name, details):
    n = len(details)
    k = sum(d["correct"] for d in details)
    gold_c = Counter(d["gold"] for d in details)
    pred_c = Counter(d["pred"] for d in details)
    majority = max(gold_c.values()) / n
    print(f"\n--- {name}  (n={n}) ---")
    print(f"  accuracy      : {k}/{n} = {k / n:.4f}")
    print(f"  majority floor: {majority:.4f}  (gold {dict(gold_c)})")
    print(f"  PREDICTIONS   : {dict(pred_c)}   <- the UNMET-bias check")
    for cls in ("MET", "UNMET"):
        sub = [d for d in details if d["gold"] == cls]
        if sub:
            ck = sum(d["correct"] for d in sub)
            print(f"  recall {cls:5s} : {ck}/{len(sub)} = {ck / len(sub):.4f}")
    return k, n


def main():
    rows = load_rows()
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    inlex = [r for r in rows if r.get("outcome_in_lexicon") is True]
    print(f"bank: {len(rows)} items = {len(oov)} OOV + {len(inlex)} in-lexicon")

    # ---- ARM A: positive control. Must reproduce the landed number or nothing below is readable.
    k_a, det_a = score(oov)
    acc_a = k_a / len(oov)
    report("ARM A  POSITIVE CONTROL: the OOV 36, EMPTY overlay (the landed population)", det_a)
    ok = abs(acc_a - EMPTY_MAP_REF) <= LANDED_TOL
    print(f"  reproduces documented EMPTY-map {EMPTY_MAP_REF}? {'YES' if ok else 'NO'}"
          f"  (got {acc_a:.4f}, delta {acc_a - EMPTY_MAP_REF:+.4f})")
    if not ok:
        print("\nREFUSING TO REPORT ARM B: this harness does not reproduce a documented number,")
        print("so it is not scoring what the cell scored. Fix that first.")
        return 1

    # ---- ARM B: the known-answer arm nobody has run.
    _, det_b = score(inlex)
    k_b, _ = report("ARM B  KNOWN-ANSWER: the 8 in-lexicon sanity controls", det_b)
    p_b = two_sided_binomial(k_b, len(inlex))
    print(f"  exact two-sided binomial vs chance 0.5: p = {p_b:.4f}"
          f"   -> {'CLEARS' if p_b < 0.05 else 'DOES NOT CLEAR'} p<0.05")
    print("\n  per item:")
    for d in det_b:
        flag = "ok " if d["correct"] else "MISS"
        print(f"    {flag} {d['id'][:38]:38s} lemma={d['outcome_lemma']:12s} "
              f"gold={d['gold']:5s} pred={str(d['pred']):5s} reason={d['reason']}")

    # ---- the column I was not reading: ABSTENTION. Not pre-registered; flagged as post-hoc.
    def abstains(det):
        return sum(1 for d in det if d["pred"] in (None, "NONE"))

    ab_oov, ab_in = abstains(det_a), abstains(det_b)
    p_ab = fisher_exact_2x2(ab_oov, len(det_a) - ab_oov, ab_in, len(det_b) - ab_in)
    print("\n--- ABSTENTION (post-hoc, NOT pre-registered -- read as a lead, not a result) ---")
    print(f"  OOV 36       : {ab_oov}/{len(det_a)} = {ab_oov / len(det_a):.4f} return NONE")
    print(f"  in-lexicon 8 : {ab_in}/{len(det_b)} = {ab_in / len(det_b):.4f} return NONE")
    print(f"  Fisher exact two-sided: p = {p_ab:.4f}")
    print(f"  accuracy AMONG NON-ABSTENTIONS  OOV: "
          f"{sum(1 for d in det_a if d['correct'])}/{len(det_a) - ab_oov} = "
          f"{sum(1 for d in det_a if d['correct']) / max(1, len(det_a) - ab_oov):.4f}"
          f"   |  in-lexicon: {k_b}/{len(det_b) - ab_in} = "
          f"{k_b / max(1, len(det_b) - ab_in):.4f}")

    # ---- decompose by REASON, because "pred != NONE" is NOT the same event as "the cascade fired".
    # The plan records the cascade firing at 10/19 = 0.5263 in the OVERLAY condition; this is the
    # EMPTY condition and a different event, so the two may not be placed side by side without this.
    print("\n--- OOV 36 BY REASON (empty overlay). `abstain_fallback_to_lexicon` is NOT the cascade ---")
    by_reason = {}
    for d in det_a:
        by_reason.setdefault(d["reason"], []).append(d)
    for reason, sub in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
        c = sum(1 for d in sub if d["correct"])
        none_n = sum(1 for d in sub if d["pred"] in (None, "NONE"))
        print(f"  {str(reason):34s} n={len(sub):2d}  correct={c:2d} ({c / len(sub):.4f})  NONE={none_n}")

    # ---- what does the ABSTENTION ACCOUNTING cost? A policy, not a mechanism -- and it FITS the bank.
    maj = "MET" if sum(1 for d in det_a if d["gold"] == "MET") * 2 >= len(det_a) else "UNMET"
    filled = sum(1 for d in det_a
                 if (maj if d["pred"] in (None, "NONE") else d["pred"]) == d["gold"])
    print(f"\n--- ABSTENTION ACCOUNTING (OOV 36, empty overlay) ---")
    print(f"  as scored (NONE counts WRONG)      : {sum(1 for d in det_a if d['correct'])}/36 = {acc_a:.4f}")
    print(f"  if every NONE became the majority '{maj}': {filled}/36 = {filled / 36:.4f}"
          f"   (floor {0.6389})")
    print("  NOT A MECHANISM: this policy is FITTED to this bank's majority. Reported as a")
    print("  FLOOR-style observation about the SCORING, never as an organ capability.")
    n_err = len(det_a) - sum(1 for d in det_a if d["correct"])
    n_none = sum(1 for d in det_a if d["pred"] in (None, "NONE"))
    print(f"  ERROR COMPOSITION, which needs no fitted policy at all: of {n_err} errors, "
          f"{n_none} are NON-ANSWERS and {n_err - n_none} are WRONG ANSWERS.")

    # ---- adjudicate the two pre-registered hypotheses
    met = [d for d in det_b if d["gold"] == "MET"]
    unmet = [d for d in det_b if d["gold"] == "UNMET"]
    met_r = sum(d["correct"] for d in met) / len(met) if met else float("nan")
    unmet_r = sum(d["correct"] for d in unmet) / len(unmet) if unmet else float("nan")
    unmet_share = sum(1 for d in det_b if d["pred"] == "UNMET") / len(det_b)
    print("\n--- ADJUDICATION against the pre-registered predictions ---")
    print(f"  MET recall {met_r:.3f} | UNMET recall {unmet_r:.3f} | share predicted UNMET {unmet_share:.3f}")
    if k_b == len(det_b):
        print("  -> H1 SUPPORTED and it clears p<0.05: supplying the lexicon entry fixes the item.")
    elif unmet_share >= 0.75 and met_r <= 0.25:
        print("  -> H2 SUPPORTED: the organ answers UNMET regardless of the lexicon. The wall is")
        print("     the UNMET bias, NOT open vocabulary -- and this is on items it has the word for.")
    else:
        print("  -> NEITHER pattern cleanly. At n=8 this is UNINFORMATIVE, which was declared")
        print("     before the run. Report as inconclusive; do NOT read it as a negative.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
