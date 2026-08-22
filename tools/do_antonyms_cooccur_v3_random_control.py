"""v3 -- THE SAME FORK, WITH A CONTROL THAT IS ACTUALLY CORRECT.

WHY A THIRD VERSION. My positive control fired twice and was right to, but for two different reasons.
  v1  the STATISTIC was broken -- PMI with a 0.5 smoothing floor manufactured high scores for rare
      pairs that never co-occur, and 54% of the baseline never co-occurs.
  v2  the CONTROL ITSELF was wrong. It required SimVerb's NONE pairs to co-occur least. But NONE
      means "no WordNet relation", NOT "topically unassociated" -- drive/park and cook/serve carry no
      lexical relation and co-occur constantly. NONE IS NOT A NEGATIVE CONTROL, so demanding it come
      last was demanding something false.

v3 BUILDS THE NEGATIVE CONTROL THAT WAS MISSING: RANDOM PAIRS drawn from the same covered verb
vocabulary, frequency-matched to the antonym pairs' own bins. Random pairs genuinely have no reason
to co-occur, so they must come last. If they do not, the instrument is wrong for a third time and
nothing is read.

THE HYPOTHESIS UNDER TEST (Charles & Miller 1989; Justeson & Katz 1991): antonyms CO-OCCUR far above
chance because opposition is what makes a pair worth mentioning together -- "buy and sell", "rise and
fall". Synonyms are substitutable and so rarely worth saying twice.

HEADLINE STATISTIC IS COND-COORD, and the reason matters: coordination hits DIVIDED BY co-occurrences.
A frequent pair gets more chances at the numerator AND the denominator, so the ratio is not inflated
by frequency the way a raw count is.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import math
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hdlab.reading_grounding_loop import content_words, normalize_lemma   # noqa: E402
from which_norm_dimensions_can_text_recover import _sentences             # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")


def main() -> int:
    pairs = []
    with open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                pairs.append((p[0].strip().lower(), p[1].strip().lower(), p[4].strip()))

    sents = _sentences()
    wanted = {w for a, b, _ in pairs for w in (a, b)}
    where: dict[str, set] = collections.defaultdict(set)
    low: list[str] = []
    for i, s in enumerate(sents):
        lems = {normalize_lemma(w) for w in content_words(s)}
        hit = lems & wanted
        for w in hit:
            where[w].add(i)
        low.append(s.lower() if hit else "")
    covered = sorted(w for w in wanted if len(where[w]) >= 5)
    print(f"sentences {len(sents)} | covered verbs {len(covered)}", flush=True)

    gold = {(a, b) for a, b, _ in pairs} | {(b, a) for a, b, _ in pairs}

    def score(a, b):
        sa, sb = where[a], where[b]
        both = sa & sb
        pat = re.compile(rf"\b{re.escape(a)}\w*\s+(?:and|or)\s+{re.escape(b)}\w*\b|"
                         rf"\b{re.escape(b)}\w*\s+(?:and|or)\s+{re.escape(a)}\w*\b")
        coord = sum(1 for i in both if pat.search(low[i]))
        g = math.sqrt(len(sa) * len(sb))
        return {"n_both": len(both), "coord": coord, "bin": int(round(math.log10(max(g, 1.0)) * 3))}

    recs = collections.defaultdict(list)
    for a, b, rel in pairs:
        if a in where and b in where and a != b and len(where[a]) >= 5 and len(where[b]) >= 5:
            recs[rel].append(score(a, b))

    # ---- THE MISSING NEGATIVE CONTROL: random pairs, no gold relation of any kind ----
    rng = np.random.default_rng(7)
    ant_bins = collections.Counter(x["bin"] for x in recs["ANTONYMS"])
    want_total = sum(ant_bins.values()) * 6
    tries = 0
    while len(recs["RANDOM"]) < want_total and tries < 400000:
        tries += 1
        a, b = covered[rng.integers(len(covered))], covered[rng.integers(len(covered))]
        if a == b or (a, b) in gold:
            continue
        recs["RANDOM"].append(score(a, b))
    print(f"RANDOM pairs built: {len(recs['RANDOM'])} (gold pairs excluded)", flush=True)

    def matched(rel):
        sel = []
        for b, k in ant_bins.items():
            pool = [x for x in recs.get(rel, []) if x["bin"] == b]
            if not pool:
                continue
            idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
            sel += [pool[i] for i in idx]
        return sel

    print()
    print(f"{'relation':<16}{'n':>6}{'%ZERO':>8}{'mean n_both':>13}{'COND-COORD':>12}")
    print("-" * 56)
    res = {}
    for rel in ("ANTONYMS", "SYNONYMS", "COHYPONYMS", "HYPER/HYPONYMS", "NONE", "RANDOM"):
        sel = matched(rel)
        if len(sel) < 8:
            continue
        nb = np.array([x["n_both"] for x in sel], dtype=float)
        cd = sum(x["coord"] for x in sel); tb = sum(x["n_both"] for x in sel)
        cc = cd / tb if tb else 0.0
        res[rel] = (len(sel), 100.0 * float((nb == 0).mean()), nb.mean(), cc)
        print(f"{rel:<16}{len(sel):>6}{res[rel][1]:>8.1f}{nb.mean():>13.2f}{cc:>12.4f}")

    print()
    a, s, r = res["ANTONYMS"], res["SYNONYMS"], res["RANDOM"]
    print(f"[NEGATIVE CONTROL] RANDOM pairs must co-occur LEAST: RANDOM {r[2]:.2f} "
          f"vs SYN {s[2]:.2f} vs ANT {a[2]:.2f}")
    if r[2] > min(a[2], s[2]):
        print("  INSTRUMENT STILL WRONG -- not reading the rest.")
        return 2
    print(f"[NEGATIVE CONTROL] RANDOM cond-coord {r[3]:.4f} (must be lowest or near it)")
    print(f"[THE FORK] co-occurrence  ANT {a[2]:.2f} vs SYN {s[2]:.2f} = {a[2]/max(s[2],1e-9):.2f}x "
          f"| vs RANDOM = {a[2]/max(r[2],1e-9):.2f}x")
    print(f"[THE FORK] %never co-occur ANT {a[1]:.1f}% vs SYN {s[1]:.1f}% vs RANDOM {r[1]:.1f}%")
    print(f"[JUSTESON-KATZ] cond 'a and/or b' ANT {a[3]:.4f} vs SYN {s[3]:.4f} "
          f"= {a[3]/max(s[3],1e-9):.2f}x | vs RANDOM {r[3]:.4f} = {a[3]/max(r[3],1e-9):.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
