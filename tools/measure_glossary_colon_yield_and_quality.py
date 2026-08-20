"""Does GLOSSARY_COLON really run at 92%, and how much of it is there? Fresh extraction, current code.

THE CLAIM UNDER TEST. Scoring `exp_definitional_grounding_v5`'s 8-day-old blind sample tonight gave
**GLOSSARY_COLON 12/13 = 92% MEANINGFUL with zero noise**, against 44-50% for every other pattern.
**That is the single most actionable number of the day -- and it rests on THIRTEEN ROWS.**

WHY FRESH EXTRACTION RATHER THAN MORE OF THAT SAMPLE: the v5 cell kept only its 50-row sample, not
its 2,092 facts. Re-extracting is better anyway -- it tests the CODE AT HEAD (including today's
`_MEASURE_HEAD` fix), not an 8-day-old snapshot, so a confirmation here means the current system
does this, not that a past one did.

WHAT IS MEASURED, and the second question matters as much as the first:
  1. QUALITY -- is the head the extractor banks a meaningful definition of the term? (hand-scored)
  2. SUPPLY  -- how many glossary-colon definitions exist per 1,000 sentences, by corpus? **A 92%
     pattern that fires twice a book is a curiosity; one that fires constantly is a plan.** Today
     already killed one proposed fix on prevalence alone (the sentence-anchor defect fires 0 times
     in 438 real candidates), so prevalence is measured BEFORE anything is proposed.

CORPUS CHOICE, STATED SO IT IS NOT MISTAKEN FOR A GENERAL CLAIM: the v5 sample was `bio_new`-heavy,
so the textbook corpora are the comparable population. **simplewiki is included precisely because it
is the population every OTHER number in tonight's ledger was measured on** -- if glossary-colon
supply collapses there, the finding is scoped to textbooks and must be reported that way.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.definitional_extraction import definiens_head, extract_definitions  # noqa: E402

CORPORA = ["textbook_biology_2e", "textbook_psychology_2e", "openstax_common", "simplewiki"]
N_SENT = int(os.environ.get("DIAG_N_SENT", "6000"))

rows_by_corpus = {}
for name in CORPORA:
    try:
        reg = CorpusRegistry()
        h = reg.handles.get(name)
        # API CORRECTION: the handle exposes take(n) over a CURSOR, not a stream(). My first pass
        # guessed .stream() and every corpus silently yielded 0 sentences -- which printed as a
        # clean "0" and would have read as "no glossary lines exist" if I had not checked the API.
        # A zero from a wrong call looks exactly like a zero from the data.
        # `available` is a BOOL PROPERTY, `remaining`/`take` are METHODS. Two wrong guesses in a row
        # here (`.stream()`, then `.available()`), each of which produced a clean-looking ZERO.
        ok = h is not None and bool(h.available) and h.remaining() > 0
        sents = list(h.take(N_SENT)) if ok else []
    except Exception as exc:
        print("%-28s UNAVAILABLE (%s)" % (name, str(exc)[:60]))
        continue
    if not sents:
        print("%-28s yielded 0 sentences" % name)
        continue

    pats = collections.Counter()
    glos = []
    for s in sents:
        try:
            defs = extract_definitions(s) or []
        except Exception:
            continue
        for d in defs:
            p = getattr(d, "pattern", None)
            pats[p] += 1
            if p == "GLOSSARY_COLON":
                term = getattr(d, "term", None) or getattr(d, "definiendum_surface", "")
                dfs = getattr(d, "definiens", None) or getattr(d, "definiens_surface", "")
                head = ""
                try:
                    head = definiens_head(dfs) or ""
                except Exception:
                    pass
                glos.append({"term": str(term), "head": head, "definiens": str(dfs)[:90],
                             "sentence": s[:110]})
    rows_by_corpus[name] = (len(sents), pats, glos)
    per_k = 1000.0 * len(glos) / max(1, len(sents))
    print("%-28s %5d sents | all defs %4d | GLOSSARY_COLON %4d  (%.2f per 1,000 sentences)"
          % (name, len(sents), sum(pats.values()), len(glos), per_k))

print("\nPATTERN MIX PER CORPUS (supply is a property of the TEXT, not of the extractor):")
for name, (n, pats, glos) in rows_by_corpus.items():
    tot = sum(pats.values()) or 1
    mix = ", ".join("%s %d (%.0f%%)" % (k, v, 100.0 * v / tot) for k, v in pats.most_common(5))
    print("   %-26s %s" % (name, mix))

best = max(rows_by_corpus.items(), key=lambda kv: len(kv[1][2])) if rows_by_corpus else None
if best and best[1][2]:
    name, (n, pats, glos) = best
    rng = random.Random(20260820)
    samp = rng.sample(glos, min(30, len(glos)))
    print("\n" + "=" * 92)
    print("SCORE THESE -- %d GLOSSARY_COLON extractions from %s, fresh, code at HEAD" %
          (len(samp), name))
    print("Rubric: MEANINGFUL / RELATED / NOISE, identical to every other score tonight.")
    print("=" * 92)
    for i, g in enumerate(samp):
        print("%2d %-26s -> %-16s   [%s]" % (i, g["term"][:26], g["head"][:16], g["definiens"][:52]))
