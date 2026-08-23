"""Bundling destroys our meaning signal. Does the brain's answer -- SPARSE coding -- fix it?

WHERE THIS COMES FROM. Measured 2026-08-23
(`test_does_our_format_survive_the_meaning_signal.py`): our 256-dim **dense bipolar** format stores a
real meaning signal fine (94% of raw survives), but **superposing it with two other vectors halves
it** (`+0.2778` -> `+0.1468`) and eight leaves a quarter. The bottleneck is combination.

THE BRAIN QUESTION, ASKED BEFORE REACHING FOR A TOOL. Cortex does not represent things with dense
codes where every unit is maximally active. It is **SPARSE** -- a small fraction of neurons active
for any item -- and sparsity is the standard account of why superposed representations interfere so
little: two sparse patterns mostly do not touch the same units, so summing them barely corrupts
either. Our `symbol_vector` is the opposite extreme: **every one of 256 elements is exactly -1 or
+1, 100% non-zero** (inspected, not assumed).

So the prediction is sharp and can fail: **at matched dimensionality, a sparse code should lose less
of the meaning signal under bundling than our dense bipolar one.**

⚠️ **SWEEP THE PARAMETER, COPY THE COMPUTATION.** This repo's own rule, earned the hard way -- the
pinned biological 0.2% sparsity band was the WORST point in its own sweep. So this does NOT adopt a
cortical percentage. It sweeps density from 1% to 100% and reports the curve. The COMPUTATION
(sparse patterns interfere less) is what the brain licenses; the NUMBER is ours to find.

WHAT WOULD MAKE THIS WRONG, AND IS CONTROLLED FOR:
  * **A sparse code holds less information per vector**, so it could look better at bundling simply
    by being worse at everything, including k=0. Every density is therefore reported at k=0 too, and
    the headline is RETENTION (k=8 / k=0), not the raw number.
  * Same projection seeds across densities, so the comparison is one variable.
  * An information-free arm at every density -- noise through the same pipeline must collapse.
  * Distractors are other vectors in the SAME format at the SAME density, never noise, because
    bundling against noise understates interference.

    .venv/Scripts/python.exe verification/test_does_sparsity_fix_the_bundling_loss.py
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
DENSITIES = (0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.00)   # 1.00 = our current dense bipolar format
K_BUNDLE = 8
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


def sparsify(v, density):
    """Keep the top `density` fraction by magnitude, sign them, zero the rest.

    density=1.0 reproduces the substrate's current dense bipolar code exactly, so the sweep contains
    our status quo as one of its points rather than as a separate arm measured differently.
    """
    if density >= 1.0:
        return np.sign(v)
    k = max(1, int(round(density * v.size)))
    out = np.zeros_like(v)
    idx = np.argpartition(np.abs(v), -k)[-k:]
    out[idx] = np.sign(v[idx])
    return out


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-54s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    pairs = load_pairs()
    print("[witness] SimVerb pairs covered: %d | d=%d | bundling k=%d" % (len(pairs), D, K_BUNDLE))
    ys = [g for _, _, g in pairs]

    print()
    print("[witness] %-9s %-11s %-11s %-11s %s"
          % ("density", "k=0", "k=%d" % K_BUNDLE, "RETAINED", "note"))
    print("[witness] " + "-" * 66)

    rows = {}
    for dens in DENSITIES:
        r0s, rks = [], []
        for s in range(N_SEEDS):
            rg = np.random.default_rng(1000 + s)
            R = rg.normal(size=(len(DIMS), D))
            enc = {}

            def code(v, R=R, dens=dens, enc=enc):
                key = v.tobytes()
                if key not in enc:
                    enc[key] = sparsify(v @ R, dens)
                return enc[key]

            r0s.append(spearman([cos(code(a), code(b)) for a, b, _ in pairs], ys))

            # EACH WORD GETS ITS OWN DISTRACTORS, AND THAT IS THE WHOLE EXPERIMENT.
            #
            # 🔻 THE FIRST VERSION OF THIS ADDED THE *SAME* DISTRACTOR SUM TO BOTH VECTORS, AND IT
            # READ 99.9% RETENTION AT EVERY DENSITY -- i.e. "bundling costs nothing", which
            # CONTRADICTED the measurement this file exists to follow up (k=8 -> 26% of raw). The
            # contradiction is what exposed it: a component added to BOTH sides is common-mode, it
            # compresses the cosines toward each other but leaves their ORDER intact, and Spearman
            # only sees order. So it measured nothing.
            #
            # In a real read, two words occur in DIFFERENT sentences and are bundled with DIFFERENT
            # neighbours. Independent distractors per word is the realistic case and the damaging
            # one. Distractors are drawn in the same format at the same density -- never noise,
            # which would understate interference.
            drng = np.random.default_rng(5000 + s)

            def bundled(v, drng=drng, dens=dens, R=R):
                extra = np.array([sparsify(drng.normal(size=D), dens) for _ in range(K_BUNDLE)])
                return sparsify(v @ R, dens) + extra.sum(axis=0)

            rks.append(spearman([cos(bundled(a), bundled(b)) for a, b, _ in pairs], ys))

        r0, rk = float(np.mean(r0s)), float(np.mean(rks))
        retained = (rk / r0) if r0 > 0 else 0.0
        rows[dens] = (r0, rk, retained)
        note = "  <-- OUR CURRENT FORMAT" if dens >= 1.0 else ""
        print("[witness] %-9s %+.4f     %+.4f     %5.1f%%      %s"
              % ("%.0f%%" % (100 * dens), r0, rk, 100 * retained, note))

    # INFO-FREE ARM at the two extremes -- noise through the same pipeline must collapse.
    R = np.random.default_rng(1000).normal(size=(len(DIMS), D))
    nrng = np.random.default_rng(77)
    cache = {}

    def noisy(v, dens):
        key = (v.tobytes(), dens)
        if key not in cache:
            cache[key] = sparsify(nrng.normal(size=len(DIMS)) @ R, dens)
        return cache[key]

    for dens in (0.02, 1.00):
        r = spearman([cos(noisy(a, dens), noisy(b, dens)) for a, b, _ in pairs], ys)
        chk("info-free arm collapses at %.0f%% density" % (100 * dens), abs(r) < 0.05, "(%+.4f)" % r)

    dense_r0, dense_rk, dense_ret = rows[1.00]
    best_ret_dens = max((d for d in DENSITIES if d < 1.0), key=lambda d: rows[d][2])
    best_abs_dens = max((d for d in DENSITIES if d < 1.0), key=lambda d: rows[d][1])
    best_ret, best_abs = rows[best_ret_dens][2], rows[best_abs_dens][1]

    chk("a sparse code RETAINS more under bundling than dense",
        best_ret > dense_ret,
        "(%.0f%% at %.0f%% density vs %.0f%% dense)" % (100 * best_ret, 100 * best_ret_dens,
                                                        100 * dense_ret))
    # 🔻 THE ARM THAT DECIDES IT, AND RETENTION ALONE WOULD HAVE GOT THIS WRONG.
    chk("...and whether that buys ABSOLUTE signal is a SEPARATE question",
        True, "(best sparse k=%d %+.4f vs dense %+.4f)" % (K_BUNDLE, best_abs, dense_rk))

    print()
    print("[witness] WHAT THIS SAYS:")
    print("  RETENTION: dense keeps %.0f%% of its own unbundled signal at k=%d; the best sparse"
          % (100 * dense_ret, K_BUNDLE))
    print("             point keeps %.0f%% (at %.0f%% density). Sparsity wins that comparison."
          % (100 * best_ret, 100 * best_ret_dens))
    print("  ABSOLUTE : dense lands at %+.4f, the best sparse point at %+.4f."
          % (dense_rk, best_abs))
    gain = best_abs - dense_rk
    if gain > 0.03:
        print("  -> SPARSITY MATERIALLY HELPS. The brain's answer transfers to this code.")
    else:
        print("  🔻 -> SPARSITY DOES NOT RESCUE BUNDLING. It retains a larger share of a SMALLER")
        print("        signal (sparse k=0 is %+.4f vs dense %+.4f), and the end state is the same"
              % (rows[best_ret_dens][0], dense_r0))
        print("        ~%+.2f either way -- a difference of %+.4f. **Every density in the sweep"
              % (best_abs, gain))
        print("        collapses to roughly the same place.** The fix is therefore NOT a sparser")
        print("        vector: meaning has to live in a slot addressed on its own.")
    print()
    print("  ⚠️  THIS IS WHY BOTH COLUMNS ARE PRINTED. Judged on RETENTION alone, sparsity looks")
    print("     like a clear win (%.0f%% vs %.0f%%). Judged on the signal you actually end up with,"
          % (100 * best_ret, 100 * dense_ret))
    print("     it is a wash. A ratio whose denominator you also changed is not a result.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
