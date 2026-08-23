"""WITNESS: the sensorimotor channel carries VERB meaning, and the motor dimensions carry it.

Pins `notes/THE_SENSORIMOTOR_CHANNEL_COVERS_OUR_VERB_HOLE_2026-08-23.md`, whose finding is now
quoted in the priority-1 brief (`notes/problems/reader_meaning_channel/PROBLEM.md`) and in stage 2
of the substrate status tab. A finding that steers a build should fail loudly if it stops
reproducing.

WHY IT LIVES HERE AND NOT IN `scratch/`: `scratch/` is gitignored, so the note's citation would have
pointed at a file nobody else can open -- a claim wearing a citation's clothes, which is exactly what
`tools/substrate_progress.py` refuses on the status tab. If a measurement is load-bearing it has to
be re-runnable by someone who is not me.

WHAT IT ASSERTS, and all three can fail:
  1. The channel CLEARS its permutation null on SimVerb-3500 verbs.
  2. ACTION dimensions beat PERCEPTUAL ones on verbs, CI-separated (the somatotopy prediction).
  3. An information-free constant vector reads ~0 -- without which (1) proves only that the scorer
     returns big numbers.

DELIBERATELY NOT ASSERTED: the double dissociation. On nouns the same paired test includes zero, so
"motor for verbs, perceptual for nouns" is NOT established and this file must not imply it.

    .venv/Scripts/python.exe verification/test_sensorimotor_covers_the_verb_hole.py
"""
import csv
import io
import os
import random
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMS = os.path.join(REPO, "data", "grounding_testbed",
                     "Lancaster_sensorimotor_norms_for_39707_words.csv")
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")

PERCEPTUAL = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean",
              "Olfactory.mean", "Visual.mean"]
ACTION = ["Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]
ALL11 = PERCEPTUAL + ACTION

# Bands from the landed measurement. Loose enough to survive resampling noise, tight enough that a
# broken pipeline or a swapped column set fails them.
MIN_RHO_ALL11 = 0.25
MIN_ACTION_MINUS_PERCEPTUAL = 0.02
MIN_COVERAGE = 3400


def _rng():
    return random.Random(31)


def load_norms():
    out = {}
    with io.open(NORMS, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            try:
                out[w] = {c: float(row[c]) for c in ALL11}
            except (KeyError, TypeError, ValueError):
                continue
    return out


def load_pairs(norms):
    pairs = []
    with io.open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            w1, w2 = p[0].strip().lower(), p[1].strip().lower()
            try:
                g = float(p[3])
            except ValueError:
                continue
            if w1 in norms and w2 in norms:
                pairs.append((w1, w2, g))
    return pairs


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
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = np.array(ranks(x)), np.array(ranks(y))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return 0.0 if d == 0 else float((rx * ry).sum() / d)


def scores(pairs, norms, dims):
    xs, ys = [], []
    for w1, w2, g in pairs:
        xs.append(cos(np.array([norms[w1][c] for c in dims]),
                      np.array([norms[w2][c] for c in dims])))
        ys.append(g)
    return xs, ys


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    norms = load_norms()
    pairs = load_pairs(norms)
    print("[witness] SimVerb pairs covered by the norms: %d of 3500" % len(pairs))
    chk("coverage is what the note claims", len(pairs) >= MIN_COVERAGE, "(>=%d)" % MIN_COVERAGE)

    rng = _rng()
    xs, ys = scores(pairs, norms, ALL11)
    rho = spearman(xs, ys)
    idx = list(range(len(xs)))
    nulls = []
    for _ in range(300):
        sh = ys[:]
        rng.shuffle(sh)
        nulls.append(abs(spearman(xs, sh)))
    p95 = float(np.percentile(nulls, 95))
    chk("the channel CLEARS its null on verbs", rho > p95 and rho >= MIN_RHO_ALL11,
        "(rho %+.4f vs null p95 %.4f)" % (rho, p95))

    # THE SOMATOTOPY ARM. Paired -- the same resample scores both dimension sets, so the difference
    # is not inflated by the pairs happening to be easy in one draw.
    ap, _ = scores(pairs, norms, ACTION)
    pp, _ = scores(pairs, norms, PERCEPTUAL)
    diffs = []
    for _ in range(400):
        s = [rng.choice(idx) for _ in idx]
        diffs.append(spearman([ap[i] for i in s], [ys[i] for i in s])
                     - spearman([pp[i] for i in s], [ys[i] for i in s]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    chk("ACTION beats PERCEPTUAL on verbs, CI-separated", lo > 0 and lo >= MIN_ACTION_MINUS_PERCEPTUAL,
        "(%+.4f [%+.4f,%+.4f])" % (float(np.mean(diffs)), lo, hi))

    # THE CONTROL WITHOUT WHICH THE ABOVE PROVES ONLY THAT THE SCORER RETURNS BIG NUMBERS.
    const = {w: {c: 1.0 for c in ALL11} for w in norms}
    cxs, cys = scores(pairs, const, ALL11)
    chk("INFO-FREE twin reads ~0", abs(spearman(cxs, cys)) < 0.02,
        "(%+.4f)" % spearman(cxs, cys))

    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
