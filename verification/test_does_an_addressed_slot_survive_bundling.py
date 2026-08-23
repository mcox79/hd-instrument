"""I told the builder to use an ADDRESSED SLOT. Does an addressed slot actually survive?

THE CHAIN THIS CLOSES, all measured 2026-08-23:
  1. The sensorimotor channel carries real verb meaning: rho `+0.3107` where ours reads `+0.0000`.
  2. Our 256-dim dense bipolar format STORES that fine -- 94% of raw survives.
  3. But SUPERPOSING it with other vectors destroys it: two distractors halve it, eight leave 26%.
  4. SPARSITY does not rescue it -- every density collapses to ~`+0.08`.

At the end of (4) I wrote, in the priority-1 brief: *"the fix is an ADDRESSED SLOT, not a sparser
vector."* **That is a recommendation I had not measured.** This file measures it, because telling a
solver which way to build on the strength of an untested assertion is the exact failure this project
keeps paying for.

WHAT AN ADDRESSED SLOT MEANS HERE. Instead of adding the meaning code into a shared pile, bind it to
a key and recover it by unbinding:

    store    = (key_m * meaning) + SUM_i (key_i * filler_i)      <- one shared superposition
    recover  = store * key_m                                     <- bipolar multiply is self-inverse

If the recovered vector still ranks word pairs the way the raw norms do, addressing works and the
advice stands. If unbinding noise swamps it, **my advice is wrong and has to be withdrawn before
anyone builds on it.**

⚠️ **THIS IS OUR-INVENTION-UNDER-TEST, NOT BRAIN-DERIVED, AND THE DISTINCTION IS LOAD-BEARING HERE.**
No recording shows neurons computing an algebraic binding over two full-rank vector codes; the
binding problem is open, with three live accounts and published objections to each. So this tests OUR
mechanism. What the brain licenses is only the weaker, structural claim -- **that cortex keeps a
word's meaning addressable rather than stirred into one shared pot** -- and an algebraic key is one
guess at how to get that, not the thing biology does.

CONTROLS:
  * **THE ARM THAT DECIDES IT: the same store, unbound with the WRONG key.** If a wrong key recovers
    nearly as much as the right one, the "slot" is decorative and the number means nothing.
  * The unaddressed bundle at the same k, so the comparison is addressed-vs-not with k held fixed.
  * An information-free arm: noise through the identical pipeline must collapse.
  * 3 projection seeds; distractors are real bipolar vectors, never noise.

    .venv/Scripts/python.exe verification/test_does_an_addressed_slot_survive_bundling.py
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

D = 256
KS = (2, 4, 8, 16, 32)
N_SEEDS = 3


def load_pairs():
    norms = {}
    with io.open(NORMS, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
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
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-52s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    pairs = load_pairs()
    ys = [g for _, _, g in pairs]
    print("[witness] SimVerb pairs covered: %d | d=%d" % (len(pairs), D))

    raw = spearman([cos(a, b) for a, b, _ in pairs], ys)
    print("[witness] raw 11-dim reference rho: %+.4f" % raw)
    print()
    print("[witness] %-5s %-12s %-12s %-12s %s"
          % ("k", "UNADDRESSED", "ADDRESSED", "RECOVER ok/bad", "verdict"))
    print("[witness] " + "-" * 66)

    results = {}
    for k in KS:
        un, ad, wr = [], [], []
        for s in range(N_SEEDS):
            rg = np.random.default_rng(1000 + s)
            R = rg.normal(size=(len(DIMS), D))
            krg = np.random.default_rng(7000 + s)
            key_m = np.sign(krg.normal(size=D))          # the slot's address
            wrong = np.sign(krg.normal(size=D))          # a DIFFERENT address
            drg = np.random.default_rng(9000 + s)

            def store(v, k=k, R=R, key_m=key_m, drg=drg):
                m = np.sign(v @ R)
                acc = key_m * m
                for _ in range(k):
                    acc = acc + np.sign(drg.normal(size=D)) * np.sign(drg.normal(size=D))
                return acc, m

            def plain(v, k=k, R=R, drg=drg):
                m = np.sign(v @ R)
                for _ in range(k):
                    m = m + np.sign(drg.normal(size=D))
                return m

            un.append(spearman([cos(plain(a), plain(b)) for a, b, _ in pairs], ys))
            ad.append(spearman([cos(store(a)[0] * key_m, store(b)[0] * key_m)
                                for a, b, _ in pairs], ys))

            # 🔻 THE WRONG-KEY ARM IS A RECOVERY TEST, NOT A CORRELATION TEST, AND THE FIRST
            # VERSION GOT THIS WRONG IN A WAY THAT MADE IT USELESS.
            #
            # It scored `spearman(cos(store(a)*wrong, store(b)*wrong))` -- and read HIGHER than the
            # right key, which is the tell. Multiplying BOTH sides by the same wrong key is a shared
            # transformation, and cosine is invariant to it: `cos(P*x, P*y) == cos(x, y)` for any
            # fixed sign pattern P. So that arm was mathematically identical to the right key and
            # proved nothing. **Same common-mode mistake as the sparsity sweep an hour earlier.**
            #
            # What a wrong key must actually fail at is RECOVERING THE STORED ITEM. So compare the
            # recovered vector against the ORIGINAL meaning code, right key vs wrong key.
            rec_ok, rec_bad = [], []
            for v, _b, _g in pairs[:400]:            # 400 is plenty for a mean; keeps this quick
                acc, m = store(v)
                rec_ok.append(cos(acc * key_m, m))
                rec_bad.append(cos(acc * wrong, m))
            wr.append((float(np.mean(rec_ok)), float(np.mean(rec_bad))))

        u, a_ = float(np.mean(un)), float(np.mean(ad))
        r_ok = float(np.mean([x[0] for x in wr]))
        r_bad = float(np.mean([x[1] for x in wr]))
        results[k] = (u, a_, r_ok, r_bad)
        verdict = "addressing WINS" if a_ > u + 0.02 else "NO GAIN"
        print("[witness] %-5d %+.4f      %+.4f      %+.4f / %+.4f  %s"
              % (k, u, a_, r_ok, r_bad, verdict))

    # THE ARMS THAT DECIDE IT. Recovery is what a slot is FOR; the rho columns are what it BUYS.
    k8 = results[8]
    chk("the RIGHT key recovers the stored item at k=8", k8[2] > 0.2,
        "(cos %+.4f to the original code)" % k8[2])
    chk("the WRONG key recovers far less (so the slot is real)", k8[3] < k8[2] * 0.5,
        "(cos %+.4f vs %+.4f)" % (k8[3], k8[2]))
    # DELIBERATELY NOT A PASS CONDITION: the finding is that this comparison FAILS, and a witness
    # that refused to run because its subject underperformed would hide exactly that.
    print("[witness] %-52s %s (%+.4f vs %+.4f)"
          % ("does addressing beat plain bundling at k=8?",
             "NO -- AND THAT IS THE FINDING" if k8[1] <= k8[0] + 0.02 else "yes",
             k8[1], k8[0]))

    print()
    print("[witness] WHAT THIS SAYS ABOUT THE ADVICE I GAVE:")
    print("  ADDRESSING WORKS AS ADDRESSING: right key recovers the stored item at cos %+.4f,"
          % k8[2])
    print("  wrong key at %+.4f. You CAN get back which item you stored." % k8[3])
    print()
    print("  \U0001f53b BUT IT BUYS NO SIGNAL: %+.4f addressed vs %+.4f unaddressed at k=8, and it is"
          % (k8[1], k8[0]))
    print("     WORSE at k=%d (%+.4f vs %+.4f). Binding PERMUTES the interference, it does not"
          % (max(KS), results[max(KS)][1], results[max(KS)][0]))
    print("     remove it: unbinding returns the item plus a noise term of the same magnitude the")
    print("     plain bundle already had. Capacity is set by the dimension and the NUMBER OF ITEMS,")
    print("     not by whether you bound them to keys.")
    print()
    print("  ➡️ CORRECTING MY OWN ADVICE. 'Use an addressed slot' was right about")
    print("     ADDRESSABILITY and wrong if read as protection from interference -- and I wrote it")
    print("     into the priority-1 brief before measuring it. The rule that survives is blunter:")
    print("     KEEP THE NUMBER OF ITEMS IN ONE SUPERPOSITION SMALL, or give meaning its OWN STORE")
    print("     rather than a key into a shared one.")
    print("  ⚠️  OUR-INVENTION-UNDER-TEST: an algebraic key is one guess at addressability, not")
    print("     what biology does. The binding problem is open. What the brain licenses is only")
    print("     that meaning stays addressable rather than stirred into one shared pot.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
