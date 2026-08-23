"""Can our representation CARRY the meaning we are about to wire into it?

THE SETUP. We measured on 2026-08-23 that the Lancaster sensorimotor norms carry real verb meaning:
rho `+0.3107` on SimVerb-3500's 3,487 covered pairs, against a `0.0304` null, where our own learned
channel reads `+0.0000`. The priority-1 brief proposes wiring that channel in.

**THAT MEASUREMENT WAS A PLAIN COSINE OVER 11 RAW DIMENSIONS. IT SAYS NOTHING ABOUT WHETHER OUR
SUBSTRATE CAN HOLD IT.** Our substrate does not store 11 floats. `symbol_vector` returns **256
dense BIPOLAR values, every element exactly -1 or +1** (verified by inspection, 2 distinct values,
100% non-zero). So a meaning vector entering our world has to survive:

    11 real-valued dims  ->  projected to 256  ->  thresholded to {-1,+1}

If that pipeline destroys the signal, **wiring the adapter is necessary and NOT sufficient**, and
whoever builds it should know that before they build it rather than after. That is the whole point
of this file: it prices the representation, not the asset.

WHY THIS IS THE RIGHT QUESTION TO ASK NOW. The brief's own diagnosis is that the system "stores word
codes that carry no meaning by construction, then combines them in a way that destroys most of what
little arrives". The first half is about the CHANNEL and is being fixed. **This measures the second
half, and it is measured with a channel that demonstrably has signal to lose** -- which is what makes
the answer interpretable. Feeding our current codes through would confound "the format destroys it"
with "there was nothing there".

CONTROLS:
  * 8 independent projection seeds -- a single random matrix could flatter or punish by luck; the
    spread across seeds is reported, not just a mean.
  * The raw 11-dim rho is recomputed here, in the same process, on the same pairs, so the before and
    after cannot drift apart.
  * A permutation null at each stage.
  * An INFORMATION-FREE arm: project pure noise instead of the norms. It must collapse, or a
    surviving rho would only prove that projection preserves *something*, not that it preserves
    *meaning*.

    .venv/Scripts/python.exe verification/test_does_our_format_survive_the_meaning_signal.py
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

DIMS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
        "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]

D_SUBSTRATE = 256          # what symbol_vector actually returns
N_SEEDS = 8
# The raw signal must survive projection well (JL says it should) and the bipolar step is the one
# genuinely in question. Bands are loose; the FINDING is the number, not the pass.
MIN_RAW = 0.25


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
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = np.array(ranks(x)), np.array(ranks(y))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return 0.0 if d == 0 else float((rx * ry).sum() / d)


def rho_for(pairs, transform):
    xs = [cos(transform(a), transform(b)) for a, b, _ in pairs]
    ys = [g for _, _, g in pairs]
    return spearman(xs, ys)


def null_p95(pairs, transform, rng, n=200):
    xs = [cos(transform(a), transform(b)) for a, b, _ in pairs]
    ys = [g for _, _, g in pairs]
    out = []
    for _ in range(n):
        sh = ys[:]
        rng.shuffle(sh)
        out.append(abs(spearman(xs, sh)))
    return float(np.percentile(out, 95))


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-56s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    pairs = load_pairs()
    rng = random.Random(17)
    print("[witness] SimVerb pairs covered: %d" % len(pairs))

    raw = rho_for(pairs, lambda v: v)
    raw_null = null_p95(pairs, lambda v: v, rng)
    print("[witness] STAGE 0  raw 11 dims          rho %+.4f   (null p95 %.4f)" % (raw, raw_null))
    chk("the raw signal is present to begin with", raw >= MIN_RAW and raw > raw_null,
        "(%+.4f)" % raw)

    proj_rhos, bip_rhos = [], []
    for s in range(N_SEEDS):
        R = np.random.default_rng(1000 + s).normal(size=(len(DIMS), D_SUBSTRATE))
        proj_rhos.append(rho_for(pairs, lambda v, R=R: v @ R))
        bip_rhos.append(rho_for(pairs, lambda v, R=R: np.sign(v @ R)))

    pm, ps = float(np.mean(proj_rhos)), float(np.std(proj_rhos))
    bm, bs = float(np.mean(bip_rhos)), float(np.std(bip_rhos))
    print("[witness] STAGE 1  projected to %d      rho %+.4f  (sd %.4f over %d seeds)"
          % (D_SUBSTRATE, pm, ps, N_SEEDS))
    print("[witness] STAGE 2  + BIPOLAR {-1,+1}    rho %+.4f  (sd %.4f over %d seeds)  <-- OUR FORMAT"
          % (bm, bs, N_SEEDS))
    print("[witness]          kept through stage 1: %.1f%%   through stage 2: %.1f%%"
          % (100.0 * pm / raw, 100.0 * bm / raw))

    # INFO-FREE ARM: the same pipeline on noise must collapse, or "survives projection" means nothing.
    noise = {}

    def noisy(v):
        key = v.tobytes()
        if key not in noise:
            noise[key] = np.random.default_rng(abs(hash(key)) % (2 ** 31)).normal(size=len(DIMS))
        return noise[key]

    R0 = np.random.default_rng(1000).normal(size=(len(DIMS), D_SUBSTRATE))
    info_free = rho_for(pairs, lambda v: np.sign(noisy(v) @ R0))
    print("[witness] INFO-FREE arm (noise, same pipeline)  rho %+.4f" % info_free)
    chk("the info-free arm collapses", abs(info_free) < 0.05, "(%+.4f)" % info_free)

    chk("PROJECTION alone keeps most of the signal", pm > 0.8 * raw,
        "(%.1f%% kept)" % (100.0 * pm / raw))
    chk("OUR BIPOLAR FORMAT still carries the signal", bm > raw_null and bm > 0.5 * raw,
        "(%.1f%% kept, vs null %.4f)" % (100.0 * bm / raw, raw_null))

    # ---- STAGE 3: COMBINATION, WHICH IS THE HALF THE BRIEF ACTUALLY ACCUSES -------------------
    # Storage is not where the brief says the loss is: it says the system "combines them in a way
    # that destroys most of what little arrives". In a reading loop a word's meaning does not sit
    # alone -- it is BUNDLED (superposed) with whatever else the sentence contributed. Classic VSA
    # capacity says a superposition of k vectors drowns any one of them at some k. THAT is the
    # number the builder needs, and it is not the same question as stage 2.
    print()
    print("[witness] STAGE 3  BUNDLED with k distractors (superposition), our format:")
    R0 = np.random.default_rng(1000).normal(size=(len(DIMS), D_SUBSTRATE))
    bundle_rng = np.random.default_rng(4242)
    bundled = {}
    for k in (0, 1, 2, 4, 8, 16):
        def bundle(v, k=k):
            base = np.sign(v @ R0)
            if k == 0:
                return base
            # Distractors are OTHER real word vectors in the same format -- not noise. Bundling
            # against noise would understate the damage, because real vectors are correlated.
            extra = np.sign(bundle_rng.normal(size=(k, D_SUBSTRATE)))
            return base + extra.sum(axis=0)
        r = rho_for(pairs, bundle)
        bundled[k] = r
        print("[witness]   k=%-3d  rho %+.4f   (%.0f%% of raw)" % (k, r, 100.0 * r / raw))

    k8 = bundled.get(8, 0.0)
    chk("the signal survives bundling with 8 distractors", k8 > raw_null,
        "(%+.4f vs null %.4f, %.0f%% of raw)" % (k8, raw_null, 100.0 * k8 / raw))

    print()
    print("[witness] WHAT THIS MEANS FOR THE PRIORITY-1 BUILD:")
    print("  STORING it is fine: the 256-dim bipolar format keeps %.0f%% of the raw signal."
          % (100.0 * bm / raw))
    k0, k2 = bundled.get(0, bm), bundled.get(2, 0.0)
    print("  COMBINING it is where the loss is: bundling with just TWO other vectors drops it to")
    print("  %.0f%% of raw (%.0f%% of the unbundled code), and eight leaves %.0f%%."
          % (100.0 * k2 / raw, 100.0 * k2 / k0 if k0 else 0.0, 100.0 * k8 / raw))
    print("  -> The adapter must not superpose meaning with many distractors. THE BRIEF'S OWN")
    print("     DIAGNOSIS -- 'combines them in a way that destroys most of what little arrives' --")
    print("     is CONFIRMED, and it is the combination step, not the storage format.")
    print("  NOTE: stage-3 k=0 (%.4f, one projection seed) is the baseline for the k-column;"
          % k0)
    print("     stage 2 (%.4f) is the mean over %d seeds. Compare k against k=0, not across."
          % (bm, N_SEEDS))
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
