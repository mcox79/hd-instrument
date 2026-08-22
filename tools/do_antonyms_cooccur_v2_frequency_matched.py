"""v2 -- THE SAME FORK, WITH THE STATISTIC MY OWN CONTROL REJECTED IN v1 REPLACED.

WHAT HAPPENED IN v1. The positive control (unrelated pairs must show the LOWEST co-occurrence) FIRED
and the run refused to report. The cause is a real bug in the statistic, not a reason to reinterpret
it: I smoothed never-co-occurring pairs to a count of 0.5, and 54.1% of unrelated pairs never
co-occur. For a RARE pair, log(0.5*N / (n_a*n_b)) is LARGE, so the smoothing floor manufactured high
PMI for exactly the pairs that share no sentence at all. PMI was also frequency-confounded: antonym
verbs are common, so dividing by n_a*n_b deflates them.

v2 DROPS PMI AS A HEADLINE AND USES THREE STATISTICS THAT DO NOT SHARE THAT FLAW:
  1. %ZERO        share of pairs that NEVER share a sentence -- no smoothing, no normalisation
  2. FREQ-MATCHED for each antonym pair, synonym/unrelated pairs drawn from the SAME log-frequency
                  bin, so mean co-occurrence is compared at equal opportunity
  3. COND-COORD   coordination hits DIVIDED BY co-occurrences ("of the sentences containing both,
                  what share say 'a and b'?") -- conditioning on co-occurrence removes the frequency
                  advantage, because a frequent pair gets more chances at BOTH numerator and
                  denominator
POSITIVE CONTROL, unchanged and still able to abort: unrelated pairs must be LOWEST on the
frequency-matched comparison. If they are not, the measure is still wrong and nothing is read.
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
RELS = ("ANTONYMS", "SYNONYMS", "COHYPONYMS", "HYPER/HYPONYMS", "NONE")


def main() -> int:
    pairs = []
    with open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                pairs.append((p[0].strip().lower(), p[1].strip().lower(), p[4].strip()))

    sents = _sentences()
    N = len(sents)
    wanted = {w for a, b, _ in pairs for w in (a, b)}
    where: dict[str, set] = collections.defaultdict(set)
    low: list[str] = []
    for i, s in enumerate(sents):
        lems = {normalize_lemma(w) for w in content_words(s)}
        hit = lems & wanted
        for w in hit:
            where[w].add(i)
        low.append(s.lower() if hit else "")
    covered = {w for w in wanted if len(where[w]) >= 5}
    print(f"sentences {N} | SimVerb words covered {len(covered)}/{len(wanted)}", flush=True)

    recs = collections.defaultdict(list)
    for a, b, rel in pairs:
        if a not in covered or b not in covered or a == b:
            continue
        sa, sb = where[a], where[b]
        both = sa & sb
        pat = re.compile(rf"\b{re.escape(a)}\w*\s+(?:and|or)\s+{re.escape(b)}\w*\b|"
                         rf"\b{re.escape(b)}\w*\s+(?:and|or)\s+{re.escape(a)}\w*\b")
        coord = sum(1 for i in both if pat.search(low[i]))
        g = math.sqrt(len(sa) * len(sb))
        recs[rel].append({"n_both": len(both), "coord": coord, "g": g,
                          "bin": int(round(math.log10(max(g, 1.0)) * 3))})

    print()
    print(f"{'relation':<18}{'n':>6}{'%ZERO':>8}{'mean n_both':>13}{'COND-COORD':>12}")
    print("-" * 58)
    base = {}
    for rel in RELS:
        r = recs.get(rel, [])
        if len(r) < 8:
            continue
        nb = np.array([x["n_both"] for x in r], dtype=float)
        cd = sum(x["coord"] for x in r); tb = sum(x["n_both"] for x in r)
        pz = 100.0 * float((nb == 0).mean())
        cc = cd / tb if tb else float("nan")
        base[rel] = (len(r), pz, nb.mean(), cc)
        print(f"{rel:<18}{len(r):>6}{pz:>8.1f}{nb.mean():>13.2f}{cc:>12.4f}")

    # ---- frequency-matched: compare within the antonym pairs' own frequency bins ----
    ant_bins = collections.Counter(x["bin"] for x in recs["ANTONYMS"])
    print(f"\nFREQUENCY-MATCHED to the ANTONYM bins {dict(sorted(ant_bins.items()))}")
    print(f"{'relation':<18}{'n matched':>11}{'mean n_both':>13}{'%ZERO':>8}")
    print("-" * 52)
    matched = {}
    rng = np.random.default_rng(7)
    for rel in RELS:
        sel = []
        for b, k in ant_bins.items():
            pool = [x for x in recs.get(rel, []) if x["bin"] == b]
            if not pool:
                continue
            take = min(k, len(pool)) if rel != "ANTONYMS" else k
            idx = rng.choice(len(pool), size=min(take, len(pool)), replace=False)
            sel += [pool[i] for i in idx]
        if len(sel) < 8:
            continue
        nb = np.array([x["n_both"] for x in sel], dtype=float)
        matched[rel] = (len(sel), nb.mean(), 100.0 * float((nb == 0).mean()))
        print(f"{rel:<18}{len(sel):>11}{nb.mean():>13.2f}{100.0*(nb==0).mean():>8.1f}")

    print()
    if {"ANTONYMS", "SYNONYMS", "NONE"} <= set(matched):
        a, s, n_ = matched["ANTONYMS"], matched["SYNONYMS"], matched["NONE"]
        print(f"[POSITIVE CONTROL] unrelated must be LOWEST, frequency-matched: "
              f"NONE {n_[1]:.2f} vs SYN {s[1]:.2f} vs ANT {a[1]:.2f}")
        if n_[1] > min(a[1], s[1]):
            print("  MEASURE STILL SUSPECT -- not reading the rest.")
            return 2
        print(f"[THE FORK]  freq-matched mean co-occurrence  ANT {a[1]:.2f} vs SYN {s[1]:.2f} "
              f"= {a[1]/max(s[1],1e-9):.2f}x")
        print(f"[THE FORK]  %pairs that NEVER co-occur       ANT {a[2]:.1f}% vs SYN {s[2]:.1f}%")
        ca, cs = base["ANTONYMS"][3], base["SYNONYMS"][3]
        print(f"[JUSTESON-KATZ] conditional 'a and/or b' rate ANT {ca:.4f} vs SYN {cs:.4f} "
              f"= {ca/max(cs,1e-9):.2f}x  (NONE {base['NONE'][3]:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
