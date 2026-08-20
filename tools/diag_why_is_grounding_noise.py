"""WHY IS 78% OF GROUNDING NOISE? Test whether the FREQUENCY-DOMINATED HUB is the cause.

THE SETUP. A blind hand-score of 100 GROUNDED_MEANING rows (done 2026-08-12, found unread
2026-08-20) reads 3 MEANINGFUL / 19 RELATED / 78 NOISE. Eyeballing the noise rows suggests two
things at once:
    baffin -> isolate      tesco -> situation      abdullah -> totally
    publisher -> head      parachute -> ride       remote -> boat
(a) the SUBJECTS are often proper nouns with no dictionary meaning to ground; and
(b) the ASSIGNED MEANINGS look like generic, high-frequency words.

**(b) IS THE ONE THAT MATTERS, because it would close a causal loop that is currently only a
correlation.** Today's fidelity pass found the one surviving gap: our hub carries FREQUENCY at
R^2 0.4819 against 0.01-0.05 for a typical sensorimotor dimension -- roughly 20x. If the grounding
step picks its anchor by similarity in that hub, then **a frequency-dominated hub should
systematically hand out FREQUENT words as meanings**, and those should be the NOISE ones. That
turns "our code is a frequency detector" from a geometric observation into a measured CAUSE of a
scored quality failure.

THE TEST. Corpus frequency is computed from `simplewiki` INDEPENDENTLY of the sample, then:
  H2 (the claim)     assigned OBJECT frequency, NOISE vs (MEANINGFUL + RELATED)
  H1 (the rival)     SUBJECT properties -- proper-noun rate and frequency, same split
**BOTH ARE MEASURED, because if the SUBJECTS also differ then this is a POPULATION effect (we try to
ground ungroundable things) rather than an ANCHOR effect (we assign bad meanings), and those imply
completely different fixes.** Reporting only the one I expect would make the other invisible.

GUARDS:
  * POSITIVE CONTROL on the frequency measure itself -- it must rank known-common words above
    known-rare ones, or every number below is meaningless.
  * The comparison group is MEANINGFUL+RELATED pooled, because MEANINGFUL alone is n=3 and no
    statistic survives that. Stated up front rather than discovered later.
  * Bootstrap CIs, and the n for every cell printed. **With 22 non-noise rows this is UNDERPOWERED
    BY CONSTRUCTION** -- the pre-committed reading below says what that permits.

PRE-COMMITTED READINGS:
  OBJECT frequency higher for NOISE, CI-separated, while SUBJECT properties do NOT differ ->
      **the frequency-dominated hub is handing out frequent words as meanings.** A measured causal
      link from the fidelity gap to a quality failure, and it names the fix: fix the anchor
      selection, not the input population.
  SUBJECT properties differ too -> **population effect.** We are trying to ground things that have
      no groundable meaning (proper nouns, inflections). Different fix entirely: filter the target
      population upstream. Say so plainly rather than claiming the anchor result.
  NEITHER separates -> underpowered at n=22, which is the honest and expected outcome. Report it as
      UNTESTABLE AT THIS n, **not** as evidence of no effect, and say what n would be needed.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402

ROWS = os.path.join(_REPO, "data", "exp_grounding_quality_readout_v1", "_joined_verdicts.json")
N_FREQ = 20000


def main():
    rows = json.load(open(ROWS, encoding="utf-8"))
    print("hand-scored rows: %d" % len(rows))

    reg = CorpusRegistry()
    sents = reg.handles["simplewiki"].take(N_FREQ)
    freq = collections.Counter()
    for s in sents:
        freq.update(content_lemmas(s))
    print("frequency table: %d sentences, %d distinct lemmas" % (len(sents), len(freq)))

    # POSITIVE CONTROL on the frequency measure.
    common = ["people", "year", "world", "time"]
    rare = ["metaphase", "homologous", "parachute"]
    cm = np.median([freq.get(w, 0) for w in common])
    rr = np.median([freq.get(w, 0) for w in rare])
    print("selftest freq: common %s median %.0f | rare %s median %.0f" % (common, cm, rare, rr))
    assert cm > rr, "frequency measure does not rank common above rare -- refusing to run"

    def logf(w):
        return math.log(freq.get(w, 0) + 1)

    noise = [r for r in rows if r["v"] == "NOISE"]
    good = [r for r in rows if r["v"] in ("MEANINGFUL", "RELATED")]
    print("\nNOISE n=%d | MEANINGFUL+RELATED n=%d" % (len(noise), len(good)))
    print("(MEANINGFUL alone is n=%d -- pooled with RELATED because no statistic survives n=3)"
          % sum(1 for r in rows if r["v"] == "MEANINGFUL"))

    rng = np.random.default_rng(0)

    def compare(label, fn):
        a = np.array([fn(r) for r in noise], dtype=float)
        b = np.array([fn(r) for r in good], dtype=float)
        d = float(np.median(a) - np.median(b))
        bb = np.array([np.median(a[rng.integers(0, a.size, a.size)])
                       - np.median(b[rng.integers(0, b.size, b.size)]) for _ in range(4000)])
        lo, hi = np.percentile(bb, [2.5, 97.5])
        sep = not (lo <= 0 <= hi)
        print("   %-34s NOISE %7.3f | GOOD %7.3f | diff %+7.3f CI [%+.3f, %+.3f] %s"
              % (label, np.median(a), np.median(b), d, lo, hi,
                 "SEPARATED" if sep else "not separated"))
        return d, sep

    print("\nH2 -- THE ANCHOR: is the assigned MEANING more frequent when the row is NOISE?")
    d_obj, s_obj = compare("log freq of assigned OBJECT", lambda r: logf(r["obj"]))

    print("\nH1 -- THE RIVAL: do the SUBJECTS differ too? (would mean a POPULATION effect)")
    d_sub, s_sub = compare("log freq of SUBJECT", lambda r: logf(r["subj"]))
    d_len, s_len = compare("SUBJECT length (proxy for rarity)", lambda r: len(r["subj"]))
    # proper-noun proxy: a subject absent from a 20k-sentence corpus is very likely a name
    d_oov, s_oov = compare("SUBJECT unseen in corpus (0/1)",
                           lambda r: 1.0 if freq.get(r["subj"], 0) == 0 else 0.0)

    print("\nSEGMENT BREAKDOWN (the charter predicted the technical segment grounds better):")
    seg = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        seg[r["seg"]][0] += 1
        if r["v"] in ("MEANINGFUL", "RELATED"):
            seg[r["seg"]][1] += 1
    for k in sorted(seg, key=lambda k: -seg[k][0]):
        n, g = seg[k]
        print("   %-12s n=%3d  meaningful-or-related %2d  (%.0f%%)" % (k, n, g, 100.0 * g / n))

    print()
    if s_obj and d_obj > 0 and not (s_sub or s_oov):
        print("VERDICT: **THE FREQUENCY-DOMINATED HUB IS HANDING OUT FREQUENT WORDS AS MEANINGS.**")
        print("NOISE rows get significantly MORE FREQUENT anchors while their SUBJECTS are")
        print("indistinguishable from the good rows. That is a measured causal link from the")
        print("fidelity gap (hub carries frequency ~20x sensorimotor) to a scored quality failure,")
        print("and it names the fix: anchor SELECTION, not the input population.")
    elif s_sub or s_oov:
        print("VERDICT: **POPULATION EFFECT -- the SUBJECTS differ.** We are trying to ground things")
        print("that may have no groundable meaning. The fix is upstream filtering of the target")
        print("population, NOT the anchor rule. Do not claim the anchor result.")
    else:
        print("VERDICT: **UNTESTABLE AT THIS n, NOT A NULL.** With %d non-noise rows the CIs cannot"
              % len(good))
        print("exclude the effect sizes in play. This is the expected outcome and it is worth")
        print("saying: the hand-score answers WHETHER quality is poor, and cannot answer WHY.")
        print("A WHY answer needs a purpose-built sample, stratified on the hypothesis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
