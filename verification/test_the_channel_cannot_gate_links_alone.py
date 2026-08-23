"""The meaning channel carries real signal and still cannot DECIDE whether two words link.

WHY THIS MATTERS MORE THAN THE OTHER MEASUREMENTS IN THIS SERIES. The priority-1 brief asks to *"make
the system get meaning from that channel INSTEAD"* of co-occurrence. Everything measured so far said
the channel is good (rho `+0.27` to `+0.31`, the only channel we have that says anything about verbs
at all). **This file measures whether it can do the JOB the brief assigns it -- gate links -- and it
cannot, structurally rather than by tuning.**

THREE FACTS, EACH ASSERTED BELOW:

  1. **AS SHIPPED IT CONTRIBUTES EXACTLY ZERO.** `GROUNDED_CAP = 0.45` sits below
     `lexical_similarity.SIMILARITY_LINK_THRESHOLD = 0.5`. So `grounded_similarity()` can never reach
     the link threshold. On SimVerb-3500's genuinely-similar verb pairs: **0 linked.**
  2. **UNCAPPING IS NOT THE FIX.** At the same threshold the unclamped channel links 66% of
     genuinely-similar pairs -- and **37% of genuinely-DISSIMILAR ones.** The cap is not paranoia.
  3. **NO THRESHOLD RESCUES IT.** Swept 0.30->0.95, the best hit-minus-false-alarm margin is
     `+0.287` and it occurs AT `0.50` -- where the threshold already sits. The design put it in the
     right place. Threshold-free, AUC is `0.70`: real signal, nowhere near separable.

➡️ **THE CONCLUSION THE BUILD NEEDS: this channel is a CONTRIBUTOR, not a DECIDER.** Wiring it in as
a drop-in replacement for the co-occurrence gate yields either nothing (capped) or one link in three
wrong (uncapped).

⚠️ **THIS IS NOT AN ARGUMENT FOR RAISING THE CAP.** The 0.05 gap to the link threshold is precisely
what makes "contribute, do not decide" enforceable in code rather than hoped for in prose. Raising it
to improve a number would be adjusting the instrument to suit the reading.

POPULATIONS: "genuinely similar" = top quartile of human SimLex/SimVerb ratings, "genuinely
dissimilar" = bottom quartile, both drawn from the SAME covered set, so the two arms differ only in
the human label.

    .venv/Scripts/python.exe verification/test_the_channel_cannot_gate_links_alone.py
"""
import io
import os
import random
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")

SWEEP = (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))


def main():
    import hdlab.grounded_similarity as G
    import hdlab.lexical_similarity as L

    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-52s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    cap = G.GROUNDED_CAP
    thr = L.SIMILARITY_LINK_THRESHOLD
    print("[witness] GROUNDED_CAP=%.2f  SIMILARITY_LINK_THRESHOLD=%.2f  (gap %.2f)"
          % (cap, thr, thr - cap))
    chk("the cap sits BELOW the link threshold", cap < thr, "(%.2f < %.2f)" % (cap, thr))

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
    gs = sorted(g for _, _, g in cov)
    q75, q25 = gs[int(0.75 * len(gs))], gs[int(0.25 * len(gs))]
    sim = [(a, b) for a, b, g in cov if g >= q75]
    dis = [(a, b) for a, b, g in cov if g <= q25]
    print("[witness] covered %d | similar (>=%.2f) %d | dissimilar (<=%.2f) %d"
          % (len(cov), q75, len(sim), q25, len(dis)))

    def unclamped(a, b):
        return cos(np.asarray(G.grounded_vector(a)).ravel(),
                   np.asarray(G.grounded_vector(b)).ravel())

    linked_shipped = sum(1 for a, b in sim if (G.grounded_similarity(a, b) or 0.0) >= thr)
    chk("as shipped it links ZERO genuinely-similar pairs", linked_shipped == 0,
        "(%d of %d)" % (linked_shipped, len(sim)))

    S = [unclamped(a, b) for a, b in sim]
    Dd = [unclamped(a, b) for a, b in dis]
    hit = sum(1 for v in S if v >= thr) / len(S)
    fa = sum(1 for v in Dd if v >= thr) / len(Dd)
    print("[witness] unclamped at %.2f: hit %.1f%%, false alarm %.1f%%" % (thr, 100 * hit, 100 * fa))
    chk("uncapping links a large share of DISSIMILAR pairs too", fa > 0.25,
        "(%.1f%%)" % (100 * fa))

    print()
    print("[witness] %-8s %-10s %-12s %s" % ("thresh", "hit", "false alarm", "margin"))
    best = None
    for t in SWEEP:
        h = sum(1 for v in S if v >= t) / len(S)
        f = sum(1 for v in Dd if v >= t) / len(Dd)
        if best is None or h - f > best[1]:
            best = (t, h - f, h, f)
        print("[witness] %-8.2f %-10.3f %-12.3f %+.3f" % (t, h, f, h - f))
    print("[witness] best margin %+.3f at threshold %.2f" % (best[1], best[0]))
    chk("NO threshold separates the two populations usefully", best[1] < 0.5,
        "(best margin %+.3f)" % best[1])

    rng = random.Random(5)
    draws = [(rng.choice(S), rng.choice(Dd)) for _ in range(20000)]
    auc = (sum(1 for s, d in draws if s > d) + 0.5 * sum(1 for s, d in draws if s == d)) / len(draws)
    print("[witness] threshold-free AUC %.4f (0.5 = chance)" % auc)
    chk("...yet the channel DOES carry real signal", auc > 0.6, "(AUC %.4f)" % auc)

    print()
    print("[witness] THE CONCLUSION FOR THE BUILD:")
    print("  This channel is a CONTRIBUTOR, not a DECIDER. It carries real meaning (AUC %.2f, and it"
          % auc)
    print("  is the only channel we have that says anything about verbs) but it cannot be what")
    print("  decides whether two words link: capped it links nothing, uncapped one link in three is")
    print("  wrong, and no threshold in between does better than where the threshold already is.")
    print("  ⚠️  NOT an argument for raising the cap. The %.2f gap is what makes 'contribute, do"
          % (thr - cap))
    print("     not decide' enforceable in code instead of hoped for in prose.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
