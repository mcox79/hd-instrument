"""Cortex keeps separate populations instead of superposing. At EQUAL dimension budget, does that win?

WHERE THIS COMES FROM. Measured 2026-08-23, three times over: our 256-dim bipolar format stores a
real meaning signal fine (94% of raw survives), but **combining it with other vectors destroys it** --
two distractors halve it, eight leave 26%. **Sparsity does not rescue that** (every density collapses
to ~+0.08) and **neither does an addressed slot** (binding permutes interference rather than removing
it; +0.0536 addressed vs +0.0670 plain at k=8).

Each of those investigated a way to make SUPERPOSITION survive. **The brain's answer appears to be
not to superpose at all** -- cortex represents different attributes in different populations and
addresses them anatomically. But that is not free, and the free version is not the interesting
claim:

    ⚠️ OF COURSE separate storage has no interference -- there is nothing to interfere WITH.
       Stated that way it is a tautology, not a finding.

**SO THE ONLY HONEST FORM OF THE QUESTION FIXES THE BUDGET.** Cortex is large but finite. Give both
schemes the SAME total number of dimensions `D` and ask which carries more meaning through a
k-item combination:

    SUPERPOSED   all k items summed into D dims          (interference, full resolution per item)
    SEGREGATED   each item in its own D/k dims           (no interference, 1/k the resolution)

**That is a real trade and it can go either way.** Superposition spends its budget on resolution and
pays in crosstalk; segregation spends it on isolation and pays in dimensionality. Which wins is an
empirical question about THIS signal at THESE sizes, and nothing in the archive has asked it.

WHAT THE BRAIN LICENSES, STATED CAREFULLY. **Anatomical segregation of attributes is PINNED** --
cortex does have distinct populations for distinct properties. **The algebra we would use to imitate
either scheme is NOT** -- VSA binding is unpinned, with three live accounts and published objections
to each. So this measures two ENGINEERING options against a brain-motivated question; it does not
claim either is what neurons do.

CONTROLS:
  * the SAME signal (Lancaster sensorimotor over SimVerb-3500) both arms, so only the scheme changes;
  * an information-free arm at every budget -- noise through the identical pipeline must collapse;
  * the k=1 column, where the two schemes are identical BY CONSTRUCTION, as an internal check that
    the harness is not favouring one.

    .venv/Scripts/python.exe verification/test_segregated_beats_superposed_at_equal_budget.py
"""
import csv
import io
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMS = os.path.join(REPO, "data", "grounding_testbed",
                     "Lancaster_sensorimotor_norms_for_39707_words.csv")
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")
DIMS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
        "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]

D_TOTAL = 256            # the substrate's actual budget
# Swept to k=256 (a ONE-dimension slot) looking for the crossover where superposition wins back.
# THERE ISN'T ONE. Segregation leads at every k. What DOES change is whether either is useful:
#   k=32  ->  8d slots  segregated +0.1537  superposed -0.0011   <- last USEFUL slot width
#   k=64  ->  4d slots  segregated +0.0752  superposed -0.0019
#   k=256 ->  1d slot   segregated +0.0387  superposed +0.0139   (info-free is +0.0233)
# So below ~8 dims/slot segregation wins a race BOTH schemes are losing, and 8 dims still
# carries over half the full-resolution signal (+0.1537 vs +0.2983). That is the design number.
KS = (1, 2, 4, 8, 16, 32)
N_SEEDS = 3


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


def load_pairs():
    norms = {}
    with io.open(NORMS, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            w = (row.get("Word") or "").strip().lower()
            try:
                norms[w] = np.array([float(row[c]) for c in DIMS])
            except (KeyError, TypeError, ValueError):
                continue
    pairs = []
    with io.open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            a, b = p[0].strip().lower(), p[1].strip().lower()
            try:
                g = float(p[3])
            except ValueError:
                continue
            if a in norms and b in norms:
                pairs.append((norms[a], norms[b], g))
    return pairs


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-54s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    pairs = load_pairs()
    ys = [g for _, _, g in pairs]
    print("[witness] SimVerb pairs %d | TOTAL budget D=%d, held fixed for both schemes"
          % (len(pairs), D_TOTAL))
    print()
    print("[witness] %-4s %-14s %-14s %-10s %s"
          % ("k", "SUPERPOSED", "SEGREGATED", "winner", "segregated slot width"))
    print("[witness] " + "-" * 72)

    results = {}
    for k in KS:
        d_slot = max(1, D_TOTAL // k)
        sup, seg = [], []
        for s in range(N_SEEDS):
            rg = np.random.default_rng(400 + s)
            R_full = rg.normal(size=(len(DIMS), D_TOTAL))
            R_slot = rg.normal(size=(len(DIMS), d_slot))
            drg = np.random.default_rng(900 + s)

            def superposed(v, k=k, R=R_full, drg=drg):
                """All k items summed into the full D dims -- full resolution, crosstalk."""
                acc = np.sign(v @ R)
                for _ in range(k - 1):
                    acc = acc + np.sign(drg.normal(size=D_TOTAL))
                return acc

            def segregated(v, R=R_slot):
                """Our item alone in its own D/k slot -- no crosstalk, 1/k the resolution.
                The other k-1 slots exist but are never compared, which is the whole point:
                anatomical addressing means you read the slot, not the sum."""
                return np.sign(v @ R)

            sup.append(spearman([cos(superposed(a), superposed(b)) for a, b, _ in pairs], ys))
            seg.append(spearman([cos(segregated(a), segregated(b)) for a, b, _ in pairs], ys))

        u, g = float(np.mean(sup)), float(np.mean(seg))
        results[k] = (u, g, d_slot)
        win = "SEGREGATED" if g > u + 0.005 else ("superposed" if u > g + 0.005 else "tie")
        print("[witness] %-4d %+.4f        %+.4f        %-10s %d dims" % (k, u, g, win, d_slot))

    # INTERNAL CHECK: at k=1 the two schemes are the same thing, so they must agree.
    u1, g1, _ = results[1]
    chk("k=1: the two schemes agree (harness favours neither)", abs(u1 - g1) < 0.03,
        "(%+.4f vs %+.4f)" % (u1, g1))

    # INFO-FREE ARM at the hardest budget.
    rg = np.random.default_rng(400)
    R_slot = rg.normal(size=(len(DIMS), max(1, D_TOTAL // max(KS))))
    nz = {}

    def noisy(v):
        key = v.tobytes()
        if key not in nz:
            nz[key] = np.random.default_rng(abs(hash(key)) % (2 ** 31)).normal(size=len(DIMS))
        return nz[key]

    info_free = spearman([cos(np.sign(noisy(a) @ R_slot), np.sign(noisy(b) @ R_slot))
                          for a, b, _ in pairs], ys)
    chk("info-free arm collapses at the narrowest slot", abs(info_free) < 0.05,
        "(%+.4f)" % info_free)

    seg_wins = [k for k in KS if results[k][1] > results[k][0] + 0.005]
    print()
    print("[witness] WHAT THIS SAYS ABOUT THE BRAIN'S ARRANGEMENT:")
    if seg_wins:
        print("  SEGREGATION wins at k = %s, on the SAME total budget." % seg_wins)
        print("  Splitting %d dims into %d narrow slots beats spending all %d on one superposed"
              % (D_TOTAL, max(seg_wins), D_TOTAL))
        print("  code -- **isolation is worth more than resolution here**, which is the")
        print("  arrangement cortex actually uses.")
    else:
        print("  SUPERPOSITION holds at every k tested. Segregation's loss of resolution costs")
        print("  more than its freedom from crosstalk buys, at this budget and this signal.")
    print("  ⚠️  ENGINEERING, NOT BIOLOGY: anatomical segregation of attributes is pinned; the")
    print("     ALGEBRA either scheme uses here is not. This compares two of OUR options against")
    print("     a brain-motivated question -- it does not claim either is what neurons do.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
