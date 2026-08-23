"""Three passes measured "how good is our meaning asset" and got three different numbers.

THIS FILE EXISTS BECAUSE THAT HAPPENED AND NOBODY NOTICED FOR A DAY. All three are on the same
benchmark (SimVerb-3500), the same asset, and the SAME 3,487 covered pairs. They differ only in
WHICH ENTRY POINT was used, and nothing said so:

    +0.3107   raw CSV, the 11 `.mean` columns              (strategy session, 2026-08-23)
    +0.2676   cosine over `grounded_vector` (12 z-scored)  (strategy session, 2026-08-22)
    +0.2463   `grounded_similarity()`                       <- WHAT THE SUBSTRATE ACTUALLY CALLS

**THE LOWEST NUMBER IS THE SHIPPED FUNCTION, AND IT IS LOWEST FOR A REASON THAT IS NOT ABOUT THE
ASSET.** `grounded_similarity` is double-clamped by design:

    return min(GROUNDED_CAP, max(0.0, raw))     # GROUNDED_CAP = 0.45

Negatives collapse to `0.0`; everything above `0.45` collapses to `0.45`. **Measured: 63.2% of pairs
land EXACTLY on the cap**, and 1,200 pairs yield only 301 distinct values. A rank correlation over a
column that is 63% one value is measuring the ties as much as the asset.

⚠️ **THE CAP IS DELIBERATE AND MUST NOT BE "FIXED".** Its docstring says it sits below
`lexical_similarity.SIMILARITY_LINK_THRESHOLD` so that grounded similarity can never, on its own,
create a link. That is a safety property. Removing it to make a number look better would be
adjusting the instrument to suit the reading.

**SO THE RULE THIS FILE PINS:**
  * To measure THE ASSET'S ceiling -> `grounded_vector` cosine (or the raw columns). It is
    unclamped and it is what a "can this channel carry meaning" question is asking.
  * To ask what the SUBSTRATE would see -> `grounded_similarity()`. Lower, on purpose.
  * **NEVER compare a number from one entry point against a number from the other.** That is this
    repo's own no-number-crosses-scorers rule, and it was violated by three passes in two days
    including both of mine.

    .venv/Scripts/python.exe verification/test_which_number_is_the_meaning_asset.py
"""
import csv
import io
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")
NORMS = os.path.join(REPO, "data", "grounding_testbed",
                     "Lancaster_sensorimotor_norms_for_39707_words.csv")
DIMS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
        "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]

# Landed values. Tolerances are tight because all three are deterministic -- no resampling.
EXPECT = {"raw_csv_11dim": 0.3107, "grounded_vector_cos": 0.2676, "grounded_similarity": 0.2463}
TOL = 0.005


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r
    rx, ry = np.array(ranks(x)), np.array(ranks(y))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return 0.0 if d == 0 else float((rx * ry).sum() / d)


def main():
    import hdlab.grounded_similarity as G
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-50s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    rows = []
    with io.open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            try:
                rows.append((p[0].strip().lower(), p[1].strip().lower(), float(p[3])))
            except ValueError:
                continue

    cov = [(a, b, g) for a, b, g in rows
           if G.in_grounded_lexicon(a) and G.in_grounded_lexicon(b)]
    print("[witness] SimVerb rows %d | covered by the shipped lexicon %d (%.1f%%)"
          % (len(rows), len(cov), 100.0 * len(cov) / len(rows)))

    norms = {}
    with io.open(NORMS, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            w = (row.get("Word") or "").strip().lower()
            try:
                norms[w] = np.array([float(row[c]) for c in DIMS])
            except (KeyError, TypeError, ValueError):
                continue

    ys = [g for _, _, g in cov]
    got = {}
    got["raw_csv_11dim"] = spearman(
        [cos(norms[a], norms[b]) if a in norms and b in norms else 0.0 for a, b, _ in cov], ys)
    got["grounded_vector_cos"] = spearman(
        [cos(np.asarray(G.grounded_vector(a)).ravel(),
             np.asarray(G.grounded_vector(b)).ravel()) for a, b, _ in cov], ys)
    got["grounded_similarity"] = spearman(
        [G.grounded_similarity(a, b) or 0.0 for a, b, _ in cov], ys)

    print()
    for k in ("raw_csv_11dim", "grounded_vector_cos", "grounded_similarity"):
        note = "  <-- WHAT THE SUBSTRATE CALLS" if k == "grounded_similarity" else ""
        print("[witness] %-22s rho %+.4f   (landed %+.4f)%s" % (k, got[k], EXPECT[k], note))
        chk("%s reproduces its landed value" % k, abs(got[k] - EXPECT[k]) < TOL,
            "(%+.4f vs %+.4f)" % (got[k], EXPECT[k]))

    # THE MECHANISM, not just the numbers: the shipped scorer is lowest because it TIES.
    vals = [G.grounded_similarity(a, b) for a, b, _ in cov]
    vals = [v for v in vals if v is not None]
    at_cap = sum(1 for v in vals if abs(v - G.GROUNDED_CAP) < 1e-9) / len(vals)
    at_zero = sum(1 for v in vals if v <= 1e-12) / len(vals)
    print()
    print("[witness] shipped scorer: %.1f%% of pairs sit EXACTLY on the %.2f cap, %.1f%% at 0.0;"
          % (100 * at_cap, G.GROUNDED_CAP, 100 * at_zero))
    print("[witness]                 %d distinct values across %d pairs."
          % (len(set(round(v, 9) for v in vals)), len(vals)))
    chk("the cap really is what ties them", at_cap > 0.3, "(%.1f%%)" % (100 * at_cap))
    chk("the shipped scorer reads LOWER than the unclamped one",
        got["grounded_similarity"] < got["grounded_vector_cos"],
        "(%+.4f < %+.4f)" % (got["grounded_similarity"], got["grounded_vector_cos"]))

    print()
    print("[witness] THE RULE:")
    print("  Measuring THE ASSET's ceiling      -> grounded_vector cosine / raw columns (unclamped)")
    print("  Asking what the SUBSTRATE will see -> grounded_similarity() (clamped ON PURPOSE)")
    print("  NEVER compare one against the other. Three passes in two days did, including two of")
    print("  mine, and that is why the same asset had three different numbers.")
    print("  ⚠️  The cap is a SAFETY property (it sits below the link threshold so grounded")
    print("     similarity alone cannot create a link). Do NOT remove it to improve a number.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
