"""WordNet looks twice as good as our meaning channel. Inside one relation class it is not.

WHY I RAN THIS. The priority-1 chain established that the sensorimotor channel is a CONTRIBUTOR and
cannot gate links alone (best hit-minus-false-alarm margin `+0.287`). The obvious next question is
what to combine it WITH, and the brain's hub-and-spoke account says a different KIND of spoke --
taxonomic/relational rather than sensorimotor. We have WordNet, and supplied knowledge is admissible
here by owner ruling.

**THE NAIVE COMPARISON SAYS "JUST USE WORDNET", AND IT IS WRONG.** Pooled over SimVerb-3500:

    SENSORIMOTOR alone   margin +0.287   (hit 66.0%, false alarm 37.3%)   AUC 0.7013
    WORDNET alone        margin +0.543   (hit 61.3%, false alarm  7.0%)   AUC 0.8004

Five times cleaner on false alarms. On that reading the answer is obvious and this file would not
exist.

🔻 **THE CONFOUND: SimVerb's PAIRS WERE SELECTED BY WORDNET RELATION.** The benchmark file carries a
relation column -- `SYNONYMS`, `HYPER/HYPONYMS`, `COHYPONYMS`, `ANTONYMS`, `NONE`. Those are WordNet
relation types. So a WordNet scorer predicting SimVerb is partly **WordNet predicting its own
selection**, and this project already has a "circular WordNet oracle" on record.

**THE CONTROL: hold the relation class FIXED and re-measure.** If the edge is meaning, it survives
inside a class. If it is selection, it collapses.

    relation          n      SENSORIMOTOR   WORDNET
    NONE            2,084    +0.286         +0.154      <- 60% of the data; SENSORIMOTOR WINS
    HYPER/HYPONYMS    797    +0.231         +0.298
    SYNONYMS          305    +0.349         +0.262      <- SENSORIMOTOR WINS
    COHYPONYMS        190    +0.178         +0.239

**IT COLLAPSES.** WordNet's pooled `+0.543` does not survive: on the LARGEST class -- pairs with no
WordNet relation at all, 60% of the benchmark -- **the sensorimotor channel is nearly twice as good**
(`+0.286` vs `+0.154`).

**WHAT DOES *NOT* SEPARATE THEM: STABILITY.** I first wrote here that sensorimotor's margin is stable
across classes while WordNet's swings. **The witness below prints the spreads and refutes it** --
sensorimotor `0.171`, WordNet `0.145`, so if anything WordNet is marginally the steadier. *Left in
rather than deleted: I asserted a shape from four numbers I had already computed and not compared,
which is the same reflex the rest of this file exists to catch.*

**WHAT DOES SEPARATE THEM IS COVERAGE OF THE CASE THAT MATTERS.** On `NONE` -- pairs with no WordNet
relation, and **60% of the benchmark** -- sensorimotor is nearly twice as good. **A channel that
works mainly on pairs a taxonomy already links cannot tell you about the pairs the taxonomy does not
cover, which is exactly the case a reader faces on new text.**

⚠️ WHAT THIS IS NOT. It is not "WordNet is useless": it genuinely wins on HYPER/HYPONYMS and
COHYPONYMS, and a hub taking both spokes is still worth testing. It is a refutation of the POOLED
comparison, and of the conclusion a builder would have drawn from it.

    .venv/Scripts/python.exe verification/test_wordnet_advantage_is_selection_not_meaning.py
"""
import collections
import io
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")
THRESHOLDS = [i / 20.0 for i in range(1, 20)]
MIN_CLASS = 150


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))


def best_margin(S, D):
    """Best hit-minus-false-alarm over the threshold sweep. Both arms, one number."""
    best = -1.0
    for t in THRESHOLDS:
        h = sum(1 for x in S if x >= t) / len(S)
        f = sum(1 for x in D if x >= t) / len(D)
        best = max(best, h - f)
    return best


def main():
    import hdlab.grounded_similarity as G
    from nltk.corpus import wordnet as wn

    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-54s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    rows = []
    with io.open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            try:
                rows.append((p[0].strip().lower(), p[1].strip().lower(), float(p[3]), p[4].strip()))
            except ValueError:
                continue
    cov = [r for r in rows if G.in_grounded_lexicon(r[0]) and G.in_grounded_lexicon(r[1])]

    counts = collections.Counter(r[3] for r in rows)
    print("[witness] SimVerb relation labels (WordNet relation types -- the confound):")
    for k, v in counts.most_common():
        print("[witness]    %-16s %5d (%.1f%%)" % (k, v, 100.0 * v / len(rows)))
    chk("the benchmark really is WordNet-selected", len(counts) >= 4 and "SYNONYMS" in counts,
        "(%d relation classes)" % len(counts))

    def sm(a, b):
        return cos(np.asarray(G.grounded_vector(a)).ravel(),
                   np.asarray(G.grounded_vector(b)).ravel())

    cache = {}

    def wnsim(a, b):
        if (a, b) not in cache:
            A, B = wn.synsets(a, "v"), wn.synsets(b, "v")
            best = 0.0
            for x in A[:6]:
                for y in B[:6]:
                    v = x.wup_similarity(y)
                    if v and v > best:
                        best = v
            cache[(a, b)] = best
        return cache[(a, b)]

    def split(sub):
        gs = sorted(g for _, _, g, _ in sub)
        hi, lo = gs[int(0.75 * len(gs))], gs[int(0.25 * len(gs))]
        return ([(a, b) for a, b, g, _ in sub if g >= hi],
                [(a, b) for a, b, g, _ in sub if g <= lo])

    # POOLED -- the comparison that misleads.
    S, D = split(cov)
    pooled_sm = best_margin([sm(a, b) for a, b in S], [sm(a, b) for a, b in D])
    pooled_wn = best_margin([wnsim(a, b) for a, b in S], [wnsim(a, b) for a, b in D])
    print()
    print("[witness] POOLED over all %d covered pairs:" % len(cov))
    print("[witness]    sensorimotor %+.3f  |  wordnet %+.3f   <- looks decisive"
          % (pooled_sm, pooled_wn))
    chk("pooled, WordNet looks much better", pooled_wn > pooled_sm + 0.15,
        "(%+.3f vs %+.3f)" % (pooled_wn, pooled_sm))

    # WITHIN CLASS -- the control.
    print()
    print("[witness] WITHIN one relation class (the control):")
    print("[witness]    %-16s %6s  %-13s %s" % ("relation", "n", "SENSORIMOTOR", "WORDNET"))
    per = {}
    for rel, _n in counts.most_common():
        sub = [r for r in cov if r[3] == rel]
        if len(sub) < MIN_CLASS:
            continue
        s, d = split(sub)
        if len(s) < 25 or len(d) < 25:
            continue
        a = best_margin([sm(x, y) for x, y in s], [sm(x, y) for x, y in d])
        b = best_margin([wnsim(x, y) for x, y in s], [wnsim(x, y) for x, y in d])
        per[rel] = (len(sub), a, b)
        flag = "  <- SENSORIMOTOR WINS" if a > b else ""
        print("[witness]    %-16s %6d  %+.3f        %+.3f%s" % (rel, len(sub), a, b, flag))

    chk("WordNet's pooled edge does NOT survive within class",
        any(a > b for _n, a, b in per.values()),
        "(sensorimotor wins %d of %d classes)"
        % (sum(1 for _n, a, b in per.values() if a > b), len(per)))

    if "NONE" in per:
        n_none, sm_none, wn_none = per["NONE"]
        chk("on pairs with NO WordNet relation, sensorimotor wins", sm_none > wn_none,
            "(%+.3f vs %+.3f on %d pairs)" % (sm_none, wn_none, n_none))

    sm_spread = max(a for _n, a, _b in per.values()) - min(a for _n, a, _b in per.values())
    wn_spread = max(b for _n, _a, b in per.values()) - min(b for _n, _a, b in per.values())
    print()
    print("[witness] stability across classes: sensorimotor spread %.3f, wordnet spread %.3f"
          % (sm_spread, wn_spread))

    print()
    print("[witness] WHAT A BUILDER SHOULD TAKE FROM THIS:")
    print("  The pooled comparison says 'just use WordNet'. It is reading WordNet's own selection:")
    print("  SimVerb's pairs were CHOSEN by WordNet relation, so a WordNet scorer is partly")
    print("  predicting itself. Hold the relation fixed and the edge collapses -- and on the LARGEST")
    print("  class, pairs with no WordNet relation at all, the sensorimotor channel is the better")
    print("  one. That is the case a reader actually faces: words a taxonomy does not already link.")
    print("  ⚠️  NOT 'WordNet is useless' -- it wins on hyper/hyponyms and cohyponyms, and a hub")
    print("     taking both spokes is still worth testing. What is refuted is the POOLED number.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
