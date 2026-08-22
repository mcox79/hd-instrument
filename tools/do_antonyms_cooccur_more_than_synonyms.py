"""THE FORK: is there ANY text-derived signal that separates OPPOSITES from SYNONYMS?

WHY IT MATTERS. Tonight's antonym test confirmed that propagating meaning by SECOND-ORDER similarity
(do two words appear in similar contexts?) cannot tell opposites from synonyms -- in our space
antonyms are the CLOSEST relation of all (cos 0.2062 vs synonyms 0.1727). If NO text signal separates
them, reading can never fix it and the grounded anchor must supply polarity itself. If one exists, we
are throwing it away.

THE HYPOTHESIS IS NOT MINE AND IT IS OLD. Charles & Miller (1989) and Justeson & Katz (1991): antonym
pairs CO-OCCUR IN THE SAME SENTENCE far above chance -- "buy and sell", "rise and fall", "hot and
cold" -- precisely because opposition is what makes them worth mentioning together. Synonyms are the
mirror image: substitutable in context, so rarely worth saying twice ("take and remove" is odd).

  SECOND ORDER (what we use)  do a and b appear in SIMILAR contexts?  -> antonyms and synonyms BOTH high
  FIRST ORDER  (what we drop) do a and b appear TOGETHER?             -> antonyms HIGH, synonyms LOW

`context_vector_masked` builds second-order profiles and deletes the target word, so this signal is
structurally invisible to our encoder. THAT IS THE POINT OF THE TEST.

MEASURED on the FULL shelf (286,069 sentences), not the 41-per-word sample, because co-occurrence of
a specific pair is rare and power is the whole risk here.
  PMI       log( p(a,b) / (p(a) p(b)) ) over sentences
  COORD     explicit "a and b" / "a or b" frames, either order -- the Justeson-Katz construction

THE GUARD THAT DECIDES WHETHER THIS IS READABLE AT ALL: the FRACTION OF PAIRS THAT NEVER CO-OCCUR,
reported per relation. If most antonym pairs never share a sentence in our corpus, the test is
underpowered and that is the finding, not a null.
POSITIVE CONTROL: unrelated pairs (relation NONE) must show the LOWEST PMI. If they do not, the
measure is broken and nothing else here may be read.
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
    print(f"SimVerb pairs {len(pairs)} (control row: {pairs[0]})", flush=True)

    sents = _sentences()
    N = len(sents)
    print(f"sentences {N}", flush=True)

    wanted = {w for a, b, _ in pairs for w in (a, b)}
    where: dict[str, set] = collections.defaultdict(set)
    raw_text: list[str] = []
    for i, s in enumerate(sents):
        lems = {normalize_lemma(w) for w in content_words(s)}
        hit = lems & wanted
        for w in hit:
            where[w].add(i)
        raw_text.append(s.lower() if hit else "")

    covered = {w for w in wanted if len(where[w]) >= 5}
    print(f"SimVerb words with >=5 sentences: {len(covered)} of {len(wanted)}", flush=True)

    rows = collections.defaultdict(list)
    zero = collections.Counter()
    tot = collections.Counter()
    for a, b, rel in pairs:
        if a not in covered or b not in covered or a == b:
            continue
        sa, sb = where[a], where[b]
        both = sa & sb
        tot[rel] += 1
        if not both:
            zero[rel] += 1
        pmi = math.log((max(len(both), 0.5) * N) / (len(sa) * len(sb)))
        coord = 0
        pat = re.compile(rf"\b{re.escape(a)}\w*\s+(?:and|or)\s+{re.escape(b)}\w*\b|"
                         rf"\b{re.escape(b)}\w*\s+(?:and|or)\s+{re.escape(a)}\w*\b")
        for i in both:
            if pat.search(raw_text[i]):
                coord += 1
        rows[rel].append((pmi, len(both), coord))

    print()
    print(f"{'relation':<18}{'n':>6}{'meanPMI':>10}{'medPMI':>10}{'%zero':>9}{'mean n_both':>13}{'%coord':>9}")
    print("-" * 76)
    out = {}
    for rel in RELS:
        r = rows.get(rel, [])
        if len(r) < 8:
            print(f"{rel:<18}{len(r):>6}  (too few)")
            continue
        pm = np.array([x[0] for x in r]); nb = np.array([x[1] for x in r])
        cd = np.array([x[2] for x in r])
        pz = 100.0 * zero[rel] / max(tot[rel], 1)
        pc = 100.0 * float((cd > 0).mean())
        out[rel] = (len(r), pm.mean(), float(np.median(pm)), pz, nb.mean(), pc)
        print(f"{rel:<18}{len(r):>6}{pm.mean():>10.4f}{np.median(pm):>10.4f}{pz:>9.1f}"
              f"{nb.mean():>13.2f}{pc:>9.1f}")

    print()
    if "NONE" in out and "ANTONYMS" in out and "SYNONYMS" in out:
        none_, ant, syn = out["NONE"], out["ANTONYMS"], out["SYNONYMS"]
        print(f"[POSITIVE CONTROL] unrelated pairs must have the LOWEST mean PMI: "
              f"NONE {none_[1]:.4f} vs ANT {ant[1]:.4f} vs SYN {syn[1]:.4f}")
        if none_[1] > min(ant[1], syn[1]):
            print("  MEASURE SUSPECT: unrelated pairs are not the lowest. Do not read the rest.")
            return 2
        print(f"[POWER GUARD]     %pairs that NEVER co-occur: "
              f"ANT {ant[3]:.1f}%  SYN {syn[3]:.1f}%  NONE {none_[3]:.1f}%")
        print(f"[THE FORK]        mean PMI  ANTONYMS {ant[1]:.4f} vs SYNONYMS {syn[1]:.4f} "
              f"(diff {ant[1]-syn[1]:+.4f})")
        print(f"[JUSTESON-KATZ]   %pairs in an explicit 'a and/or b' frame: "
              f"ANT {ant[5]:.1f}%  SYN {syn[5]:.1f}%  NONE {none_[5]:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
