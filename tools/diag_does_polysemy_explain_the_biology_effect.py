"""DOES POLYSEMY EXPLAIN WHY BIOLOGY GROUNDS 3.4x BETTER? Decompose the one confounded result.

WHAT IS BEING DECOMPOSED. A blind hand-score of 100 GROUNDED_MEANING rows gives
`bio_new` 9/17 (52.9%) meaningful-or-related vs all other segments 13/83 (15.7%) --
diff +0.373, CI [+0.124, +0.620], Fisher exact p = 0.00204. **But `bio_new` differs from the others
in corpus, domain, vocabulary AND definition density at once, so "dense expository text grounds
better" is true and useless until we know WHICH property is doing the work.**

THE HYPOTHESIS, AND IT IS MECHANICAL RATHER THAN VAGUE. Our grounding assigns **ONE meaning per
word**. For a MONOSEMOUS word that can be right. **For a POLYSEMOUS word it CANNOT be right -- there
is no single meaning to assign**, so the mechanism is being scored on a task it is structurally
unable to pass. Technical vocabulary is overwhelmingly monosemous (`metaphase`: 2 senses) and
general vocabulary is not (`head`: 42). **If that is the story, the biology advantage is not about
biology at all -- it is about being handed words that HAVE one answer.**
*This is not a new idea in this repo: context-conditioned sense selection already HARD_FAILed twice.
What is new is testing whether it explains a measured QUALITY difference.*

⚖️ WORDNET IS USED AS A DIAGNOSTIC ONLY -- TO CHARACTERISE THE TEST ITEMS, NEVER AS PART OF THE
MECHANISM AND NEVER AS A GRADER. The charter permits borrowed resources for diagnosis and forbids
them in the meaning organ. **This is a different use from the circular-WordNet-oracle failure MEMORY
records** (that one used WordNet to ANSWER the task, which is why it read 0.8787 at the exact key);
here it only counts senses of words the hand-scorer already judged, and it touches no arm.

THREE MEASUREMENTS, and the third is the one that decides:
  A. SEGMENT -> POLYSEMY   are `bio_new` subjects actually more monosemous? (no scores needed, and
                           if this fails the whole hypothesis dies immediately)
  B. POLYSEMY -> QUALITY   do monosemous subjects ground better, pooled across segments?
  C. WITHIN NON-BIO ONLY   **does polysemy still predict quality when biology is REMOVED?** If yes,
                           polysemy is the operative variable rather than a marker for "biology".
                           If it vanishes, polysemy is a CORRELATE of the segment and nothing more.

GUARDS:
  * POSITIVE CONTROL on the sense measure -- known-polysemous words must outrank known-technical
    ones, or every number is meaningless.
  * Words WordNet does not know are reported separately, never silently scored as 0 senses -- a
    proper noun (`baffin`, `tesco`) is "no entry", not "one meaning", and conflating those would
    manufacture the result.
  * n printed for every cell. **22 non-noise rows is underpowered and measurement C is smaller
    still**; the pre-committed reading says what that permits.

PRE-COMMITTED READINGS:
  A holds AND B holds AND C holds -> **polysemy is the operative variable.** The biology advantage
      is a proxy for "words that have one answer", and the actionable statement is not "use
      textbooks" but "our mechanism needs monosemous targets, or it needs sense selection".
  A holds, C fails -> polysemy MARKS the segment without explaining it. Report as a correlate and
      say the confound is unresolved.
  A fails -> the hypothesis is dead on arrival and biology's advantage is something else
      (definition density, sentence form, domain coherence). Say so and name the next candidate.
  nothing separates -> UNTESTABLE AT THIS n, not a null. State the n that would be needed.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(_REPO, "data", "exp_grounding_quality_readout_v1", "_joined_verdicts.json")

from nltk.corpus import wordnet as wn  # noqa: E402


def senses(w):
    """Sense count, or None when WordNet has NO entry. None is not zero -- a proper noun is
    'no entry', and scoring it as 'one meaning' would invent the result this script tests for."""
    try:
        s = wn.synsets(w)
    except Exception:
        return None
    return len(s) if s else None


def _selftest_sense_measure():
    poly = ["head", "line", "run", "point"]
    tech = ["metaphase", "chromosome", "mitosis"]
    p = np.median([senses(w) or 0 for w in poly])
    t = np.median([senses(w) or 0 for w in tech])
    assert p > t, "sense measure does not rank polysemous above technical (%s vs %s)" % (p, t)
    assert senses("zzqqxx") is None, "unknown word must return None, not 0"
    print("selftest senses: polysemous median %.0f | technical median %.0f | unknown -> None"
          % (p, t), flush=True)


_selftest_sense_measure()

rows = json.load(open(ROWS, encoding="utf-8"))
for r in rows:
    r["sen"] = senses(r["subj"])
    r["good"] = 1.0 if r["v"] in ("MEANINGFUL", "RELATED") else 0.0

known = [r for r in rows if r["sen"] is not None]
unknown = [r for r in rows if r["sen"] is None]
print("\nrows %d | WordNet KNOWS the subject in %d | NO ENTRY (likely proper nouns etc) in %d"
      % (len(rows), len(known), len(unknown)))
print("   no-entry rows: %.0f%% good  vs  known rows: %.0f%%"
      % (100 * np.mean([r["good"] for r in unknown]) if unknown else float("nan"),
         100 * np.mean([r["good"] for r in known])))

rng = np.random.default_rng(0)


def boot_diff(a, b, label, n_boot=20000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size < 3 or b.size < 3:
        print("   %-46s n too small (%d vs %d) -- SKIPPED" % (label, a.size, b.size))
        return 0.0, False
    d = float(np.mean(a) - np.mean(b))
    bb = np.array([a[rng.integers(0, a.size, a.size)].mean()
                   - b[rng.integers(0, b.size, b.size)].mean() for _ in range(n_boot)])
    lo, hi = np.percentile(bb, [2.5, 97.5])
    sep = not (lo <= 0 <= hi)
    print("   %-46s %+7.3f  CI [%+.3f, %+.3f]  n=%d/%d  %s"
          % (label, d, lo, hi, a.size, b.size, "SEPARATED" if sep else "not separated"))
    return d, sep


print("\nA. SEGMENT -> POLYSEMY  (are bio subjects more monosemous? no hand-scores needed)")
bio_s = [r["sen"] for r in known if r["seg"] == "bio_new"]
oth_s = [r["sen"] for r in known if r["seg"] != "bio_new"]
print("   bio median senses %.1f (n=%d) | other median %.1f (n=%d)"
      % (np.median(bio_s) if bio_s else float("nan"), len(bio_s),
         np.median(oth_s) if oth_s else float("nan"), len(oth_s)))
dA, sA = boot_diff(bio_s, oth_s, "mean senses, bio - other")

print("\nB. POLYSEMY -> QUALITY  (pooled across all segments)")
g = [r["sen"] for r in known if r["good"] > 0]
n_ = [r["sen"] for r in known if r["good"] == 0]
dB, sB = boot_diff(g, n_, "mean senses, GOOD - NOISE")

print("\nC. THE DECIDER: same test with BIOLOGY REMOVED")
nb = [r for r in known if r["seg"] != "bio_new"]
g2 = [r["sen"] for r in nb if r["good"] > 0]
n2 = [r["sen"] for r in nb if r["good"] == 0]
dC, sC = boot_diff(g2, n2, "mean senses, GOOD - NOISE (non-bio only)")

print("\nSENSE-COUNT BANDS (descriptive; bands chosen before looking at outcomes):")
band = collections.defaultdict(lambda: [0, 0])
for r in known:
    k = "1 (monosemous)" if r["sen"] == 1 else ("2-4" if r["sen"] <= 4 else ("5-9" if r["sen"] <= 9
                                                                             else "10+"))
    band[k][0] += 1
    band[k][1] += int(r["good"])
for k in ("1 (monosemous)", "2-4", "5-9", "10+"):
    if k in band:
        n, gg = band[k]
        print("   %-16s n=%3d  good %2d  (%.0f%%)" % (k, n, gg, 100.0 * gg / n))

print()
if not sA:
    print("VERDICT: **HYPOTHESIS DEAD ON ARRIVAL -- bio subjects are NOT more monosemous.**")
    print("Biology's 3.4x advantage is something else: definition density, sentence form, or domain")
    print("coherence. Name the next candidate and test that instead.")
elif sA and sB and sC:
    print("VERDICT: **POLYSEMY IS THE OPERATIVE VARIABLE.** It predicts grounding quality even with")
    print("biology removed, so the biology advantage is a PROXY for 'words that have one answer'.")
    print("The actionable statement is NOT 'use textbooks' -- it is that our one-meaning-per-word")
    print("mechanism is structurally unable to ground polysemous vocabulary, and needs either")
    print("monosemous targets or real sense selection. VET before quoting.")
elif sA and not sC:
    print("VERDICT: **POLYSEMY MARKS THE SEGMENT BUT DOES NOT EXPLAIN IT.** bio subjects ARE more")
    print("monosemous, but with biology removed polysemy stops predicting quality. Report it as a")
    print("correlate; THE CONFOUND REMAINS UNRESOLVED. Do not claim the mechanism.")
else:
    print("VERDICT: **UNTESTABLE AT THIS n, NOT A NULL.** Report the n needed rather than a null.")
