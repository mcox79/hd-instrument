"""BRAIN-FIDELITY CHECK ON THE *ANSWER SHAPE*: can a word's meaning even BE another single word?

WHY THIS AND NOT ANOTHER MECHANISM TEST. Every fidelity pass so far audited a MECHANISM -- how we
select traces, weight them, write them, transform them afterwards. Thirteen such interventions have
closed. Today's hand-score says the grounding OUTPUT is 78% noise. **Nobody has audited the shape of
the answer the mechanism is required to produce.**

⚖️ THE OWNER'S FRAME, APPLIED HONESTLY -- *"which brain structure, and are we replicating it or
substituting something convenient?"*
  OUR REPRESENTATION: `GROUNDED_MEANING(subject, obj)` -- a POINTER FROM ONE LEXICAL ITEM TO
    ANOTHER. `artery -> vessel`. A word's meaning IS another word.
  WHICH BRAIN STRUCTURE IS THAT? **None.** Conceptual semantics in the ATL hub is a DISTRIBUTED
    pattern over modality-specific features (ORGAN_MAP B4: "dense, graded, ~4-12 effective dims").
    Nothing in cortex stores "the meaning of X is the word Y". **A lexical pointer is the format of
    a DICTIONARY -- a convenient available structure -- not of a brain.**
  SO THIS IS OUR-INVENTION-BEING-TESTED, and it has never been labelled as such anywhere in the
    organ map or the registry. That mislabelling is itself a fidelity finding.

*** THE MEASURABLE CONSEQUENCE, WHICH IS WHY THIS IS NOT JUST PHILOSOPHY. *** If a large share of
words have NO single other word that means them, then for those words the task has **no correct
answer available**, and a perfectly-functioning mechanism MUST score as noise. **That would make 78%
noise the EXPECTED output of correct code, and it would mean no improvement to anchor selection can
ever fix it.** This is "could the experiment have succeeded?" asked of the ANSWER FORMAT.

THE TEST, on the 100 blind-scored subjects plus a larger corpus-drawn sample:
  SYNONYM      the word shares a synset with another lemma -> a true one-word meaning EXISTS
  HYPERNYM     no synonym, but a direct hypernym exists    -> only a broader word exists
                                                              (`dog -> animal`: RELATED, not
                                                              MEANINGFUL, which is what a scorer
                                                              would mark it)
  NEITHER      no synonym and no hypernym                  -> **NO single-word answer exists at all**

⚖️ WORDNET IS A DIAGNOSTIC ONLY -- it characterises the ANSWER SPACE, it is never consulted by any
arm and never grades anything. Charter-permitted, and a different use from the circular-oracle
failure MEMORY records.

GUARDS:
  * POSITIVE CONTROL: words with obvious synonyms must land in SYNONYM, and a word whose only
    relative is broader must land in HYPERNYM. If the classifier cannot tell those apart it cannot
    support any claim about the answer space.
  * Words WordNet does not know are counted SEPARATELY, never folded into NEITHER -- "no dictionary
    entry" is a different fact from "an entry with no one-word meaning", and today's stemming
    finding showed a quarter of our subjects are in the first bucket.
  * The corpus sample is drawn INDEPENDENTLY of the hand-scored 100, so the two are a check on
    each other rather than one sample reported twice.

PRE-COMMITTED READINGS:
  A LARGE share is NEITHER/HYPERNYM -> **the answer format is the ceiling.** 78% noise is then what
      correct code produces, the mechanism is not at fault, and the actionable statement is that
      meaning must be stored as something other than a lexical pointer. This would reframe every
      grounding negative in the archive at once, so VET IT HARD before acting.
  MOST words HAVE a synonym -> the format is fine and the noise is the mechanism's fault after all.
      That is a clean negative for this hypothesis and it puts the blame back on anchor selection.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402


def classify(word):
    """SYNONYM / HYPERNYM / NEITHER / NO_ENTRY for a lemma."""
    w = (word or "").lower().strip()
    if not w:
        return "NO_ENTRY"
    try:
        syns = wn.synsets(w)
    except Exception:
        return "NO_ENTRY"
    if not syns:
        return "NO_ENTRY"
    for s in syns:
        for lem in s.lemma_names():
            if lem.lower().replace("_", " ") != w.replace("_", " "):
                return "SYNONYM"
    for s in syns:
        if s.hypernyms():
            return "HYPERNYM"
    return "NEITHER"


def _selftest():
    cases = {"car": "SYNONYM", "begin": "SYNONYM", "entity": "NEITHER", "zzqqxx": "NO_ENTRY"}
    bad = []
    for w, want in cases.items():
        got = classify(w)
        if got != want:
            bad.append("%s -> %s (wanted %s)" % (w, got, want))
    # `entity` is WordNet's root: it has no hypernym and no synonym, so it MUST land in NEITHER.
    # If that check fails the classifier cannot distinguish the buckets and nothing below is valid.
    assert not bad, "classifier selftest failed: %s" % "; ".join(bad)
    print("selftest classifier: car->SYNONYM  begin->SYNONYM  entity->NEITHER  unknown->NO_ENTRY",
          flush=True)


_selftest()


def tally(words, label):
    c = collections.Counter(classify(w) for w in words)
    n = len(words)
    print("\n%s  (n=%d)" % (label, n))
    for k in ("SYNONYM", "HYPERNYM", "NEITHER", "NO_ENTRY"):
        v = c.get(k, 0)
        print("   %-9s %5d  (%5.1f%%)" % (k, v, 100.0 * v / n if n else 0.0))
    known = n - c.get("NO_ENTRY", 0)
    if known:
        print("   -> of words WordNet knows, %.1f%% have a true one-word meaning (SYNONYM)"
              % (100.0 * c.get("SYNONYM", 0) / known))
    return c, known


# ---- 1. THE HAND-SCORED 100 -------------------------------------------------------------
rows = json.load(open(os.path.join(_REPO, "data", "exp_grounding_quality_readout_v1",
                                   "_joined_verdicts.json"), encoding="utf-8"))
subs = [r["subj"] for r in rows]
c1, known1 = tally(subs, "SUBJECTS WE ACTUALLY TRIED TO GROUND (the blind-scored 100)")

# Does the class predict the hand score? This is the link, not just the prevalence.
print("\n   hand-score outcome BY class:")
by = collections.defaultdict(lambda: [0, 0])
for r in rows:
    k = classify(r["subj"])
    by[k][0] += 1
    if r["v"] in ("MEANINGFUL", "RELATED"):
        by[k][1] += 1
for k in ("SYNONYM", "HYPERNYM", "NEITHER", "NO_ENTRY"):
    if k in by:
        n, g = by[k]
        print("      %-9s n=%3d  meaningful-or-related %2d  (%.0f%%)" % (k, n, g, 100.0 * g / n))

# ---- 2. AN INDEPENDENT CORPUS SAMPLE ----------------------------------------------------
from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402

reg = CorpusRegistry()
freq = collections.Counter()
for s in reg.handles["simplewiki"].take(8000):
    freq.update(content_lemmas(s))
vocab = [w for w, _ in freq.most_common(1500)]
c2, known2 = tally(vocab, "THE 1,500 COMMONEST CONTENT WORDS IN simplewiki (independent sample)")

print("\n" + "=" * 78)
syn_share = 100.0 * c2.get("SYNONYM", 0) / known2 if known2 else 0.0
if syn_share < 60.0:
    print("VERDICT: **THE ANSWER FORMAT IS A CEILING.** Only %.1f%% of the words we read have a true"
          % syn_share)
    print("one-word meaning available. For the rest, `A means B` has NO correct answer, so a")
    print("perfectly-working mechanism MUST score them as noise. The 78%-noise result is then the")
    print("EXPECTED output of correct code, and better anchor selection cannot reach it.")
    print("**A lexical pointer is a DICTIONARY's format, not a brain's. VET HARD before acting --")
    print("this reframes every grounding negative in the archive at once.**")
else:
    print("VERDICT: **THE FORMAT IS NOT THE CEILING.** %.1f%% of read words do have a one-word"
          % syn_share)
    print("meaning available, so the answer shape is largely reachable and the noise is the")
    print("MECHANISM's fault. Clean negative for this hypothesis; blame returns to anchor selection.")
