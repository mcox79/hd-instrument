"""THE NEGATION FLOOR FOR OUTCOME-POLARITY TASKS -- the strongest simple baseline anyone has run.

WHY THIS IS A TOOL AND NOT A NOTE. Measured 2026-08-22: counting negation words in the RESOLVING
SENTENCE scores 0.8056 on the 36-item goal-bearing bank, where the four-tier structural cascade
scores 0.4722 and the majority floor is 0.6389. Every verdict on this line was graded against 0.6389.
The measurement bar says a gate is a margin over the STRONGEST FLOOR ACTUALLY RUN -- so the bar was
wrong, and a bar that lives in a note gets forgotten. This is the project's standing escalation: when
a caution has to hold, put it in the code path.

    from tools.negation_floor import negation_floor
    fl = negation_floor(texts, gold_is_met)      # -> {'accuracy', 'null_p95', 'clears_null', ...}

WHAT IT IS AND IS NOT.
  IS : a floor. A lexical cue detector with no model of goals, referents or verbs. Any mechanism on
       this task must BEAT it to have shown anything.
  NOT: a mechanism. It must never be shipped as the answer -- this project's recurring failure is
       word-counting beating the substrate, and the discipline is that such a result RAISES THE BAR.

WHY FITTING IT TO THE EVAL IS ADMISSIBLE HERE, AND ONLY HERE. The threshold and window were chosen on
the same 36 items, which for a TREATMENT would be fatal. For a FLOOR the bias runs the safe way: an
optimistically-fitted floor is a HARDER bar, so a mechanism that clears it has cleared something at
least this strong. The permutation null recomputes the best threshold INSIDE each permutation, so
threshold selection is priced; FEATURE and WINDOW selection are not, and the docstring says so rather
than the number pretending otherwise.

NEGATION IS NOT FAILURE -- BUT LOCALISATION HANDLES THE KNOWN CASE, WHICH IS WHY THE WINDOW IS 1.
`"I never was whipped in school"` appears in a gold-MET item in this bank. At the default window that
negation is OUT OF SCOPE (it is not the resolving sentence) and produces NO false positive; counting
the whole passage DOES pick it up. That is the mechanism behind the measured window ordering, it is
pinned by a self-test, and it is why the window may not be widened "to be safe" -- widening ADMITS
distractor negations. The floor is strong, not correct: an unseen distractor IN a resolving sentence
would still fool it.

*(The docstring previously claimed this trap was an active false positive. It is not. The self-test
written to pin the claim refuted it -- a control catching its own author's overstated caveat.)*
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
from typing import Dict, List, Sequence

import numpy as np

# Deliberately plain and frozen. If this list grows to chase a number it stops being a floor and
# becomes a tuned model -- which is exactly the thing it exists to guard against.
NEG = re.compile(
    r"\b(no|not|never|nothing|none|n't|cannot|refus\w*|fail\w*|won't|can't|didn't|hasn't|"
    r"wouldn't|couldn't|shan't|nor)\b", re.I)

DEFAULT_WINDOW = 1          # the RESOLVING sentence; 0.8056 measured, best of 1/2/3/4/all


def _tail(text: str, k: int) -> str:
    parts = re.split(r"(?<=[.!?]) +", text.strip())
    return " ".join(parts[-k:]) if k > 0 else text


def cue_count(text: str, window: int = DEFAULT_WINDOW) -> int:
    """Negation cues in the last `window` sentences (window<=0 means the whole passage)."""
    return len(NEG.findall(_tail(text, window)))


def negation_floor(texts: Sequence[str], gold_is_met: Sequence[int],
                   window: int = DEFAULT_WINDOW, n_perm: int = 2000,
                   seed: int = 4) -> Dict[str, float]:
    """Best-threshold accuracy of 'fewer negation cues -> MET', with a permutation null that
    recomputes the best threshold inside every permutation (so threshold selection is priced)."""
    g = np.asarray(list(gold_is_met), dtype=int)
    v = np.array([cue_count(t, window) for t in texts], dtype=int)
    if len(g) != len(v) or len(g) < 10:
        raise ValueError(f"need >=10 aligned items, got {len(v)} texts / {len(g)} labels")
    ts = range(0, int(v.max()) + 2)

    def best(labels):
        return max(float(((v < t).astype(int) == labels).mean()) for t in ts)

    acc = best(g)
    rs = np.random.default_rng(seed)
    null = np.array([best(rs.permutation(g)) for _ in range(n_perm)])
    p95 = float(np.percentile(null, 95))
    return {
        "accuracy": acc,
        "null_p95": p95,
        "clears_null": bool(acc > p95),
        "majority_floor": float(max(g.mean(), 1 - g.mean())),
        "mean_cues_met": float(v[g == 1].mean()) if (g == 1).any() else float("nan"),
        "mean_cues_unmet": float(v[g == 0].mean()) if (g == 0).any() else float("nan"),
        "window": window,
        "n": int(len(g)),
        "caveat": ("threshold selection is priced by the null; FEATURE and WINDOW selection are NOT "
                   "-- both were chosen after reading the items. Safe as a FLOOR (optimistic fitting "
                   "raises the bar), never as a treatment."),
    }


def _self_test() -> int:
    """Positive AND negative controls. A floor that cannot fail is not a measurement."""
    ok = True

    # POSITIVE: a bank where negation perfectly marks UNMET must score high and clear its null.
    texts = ([f"She wanted it. She got it and was glad number {i}." for i in range(20)] +
             [f"She wanted it. She did not get it, not ever, number {i}." for i in range(20)])
    gold = [1] * 20 + [0] * 20
    r = negation_floor(texts, gold, n_perm=400)
    if not (r["accuracy"] > 0.95 and r["clears_null"]):
        print(f"  FAIL positive control: {r['accuracy']:.4f} clears={r['clears_null']}")
        ok = False
    else:
        print(f"  PASS positive control: acc={r['accuracy']:.4f} clears null")

    # NEGATIVE: cues uncorrelated with the label must NOT clear. A guard that always fires is noise.
    texts2 = [f"She wanted it. She did not get it {i}." if i % 2 else f"She wanted it. She got it {i}."
              for i in range(40)]
    gold2 = [(i // 7) % 2 for i in range(40)]        # label deliberately unrelated to the cue
    r2 = negation_floor(texts2, gold2, n_perm=400)
    if r2["clears_null"]:
        print(f"  FAIL negative control: uncorrelated cues cleared the null ({r2['accuracy']:.4f})")
        ok = False
    else:
        print(f"  PASS negative control: acc={r2['accuracy']:.4f} does NOT clear its null")

    # WHY THE WINDOW IS 1, PINNED AS A TEST. This is the real gold-MET passage containing a negation
    # ("I never was whipped in school"). At the DEFAULT window that negation is OUT OF SCOPE -- it is
    # not in the resolving sentence -- so it does NOT produce a false positive. Counting the whole
    # passage DOES pick it up. That is the mechanism behind the measured window ordering
    # (0.8056 at the final sentence, inside the null at whole-passage), and it is the reason the
    # window may not be widened "to be safe": widening ADMITS distractor negations.
    #
    # This assertion replaced a WRONG one written minutes earlier, which asserted the trap fires at
    # the default window. It does not, and the self-test caught the author's own overstated caveat.
    trap = "I'll be whipped, and I never was whipped in school. Tom took the punishment for her."
    near, far = cue_count(trap, 1), cue_count(trap, 0)
    if near != 0 or far == 0:
        print(f"  FAIL window control: expected 0 cues in the resolving sentence and >0 across the "
              f"passage, got near={near} far={far}")
        ok = False
    else:
        print(f"  PASS window control: distractor negation is EXCLUDED by localisation "
              f"(resolving sentence {near}, whole passage {far})")

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(__doc__)
