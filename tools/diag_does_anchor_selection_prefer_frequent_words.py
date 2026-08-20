"""DOES ANCHOR SELECTION SYSTEMATICALLY PREFER FREQUENT WORDS? Full scale, no hand-scoring needed.

THE HYPOTHESIS AND WHY IT IS NOW THE LEADING ONE. Today's fidelity pass left exactly one surviving
gap: our hub carries FREQUENCY at R^2 0.4819 against 0.01-0.05 for a typical sensorimotor dimension
-- roughly 20x. `canonicalize` picks a word's meaning by taking the NEAREST ANCHOR BY COSINE in that
hub. **If the hub is dominated by frequency, the nearest anchor should systematically be a FREQUENT
word rather than a correct one.** Separately measured today: subjects that DO have a correct
one-word meaning available are still grounded correctly only ~21% of the time. So the answer exists
and we do not pick it. This asks whether frequency is why.

*** THE KEY REALISATION: THIS NEEDS NO QUALITY LABELS. *** This morning the same question was
attempted on the 100 hand-scored rows and came back UNTESTABLE at n=22. But the hypothesis is about
the MECHANISM'S BEHAVIOUR, not about quality -- "does selection prefer frequent words" is answerable
against a RANDOM-DRAW-FROM-THE-SAME-POOL null on every fact in the store, thousands of them, with no
scoring at all.

TWO MEASUREMENTS:
  A. PREFERENCE   frequency of the CHOSEN anchor vs frequency of a RANDOM anchor from the same pool.
                  The null is the pool itself, so "frequent words get chosen because frequent words
                  are what is available" is controlled for BY CONSTRUCTION.
  B. THE COSTLY CASE, and it is the one that matters: restrict to subjects where a TRUE SYNONYM was
                  present in the pool -- i.e. **a correct answer was available** -- and ask whether
                  the word we actually chose is MORE FREQUENT than that available correct one.
                  *Picking a more-frequent wrong word over an available right one is the failure
                  mode the hypothesis predicts, stated so it can be counted.*

⚠️ ONE APPROXIMATION, STATED BECAUSE IT CUTS IN MY OWN FAVOUR. The anchor pool at the moment of each
grounding was SMALLER than the final store (anchors accumulate as reading proceeds). Reconstructing
the per-moment pool needs temporal state the store does not keep, so the FINAL pool is used. That
OVERSTATES what was available, which makes measurement B a GENEROUS test of my own hypothesis --
it can only inflate "a correct answer was available and we missed it". **A positive result here is
therefore an upper bound, not a point estimate, and must be reported as one.**

⚖️ WordNet is a DIAGNOSTIC only: it identifies which pool members are true synonyms. It grades
nothing and appears in no arm.

GUARDS:
  * positive control on the frequency measure (common words must outrank rare ones)
  * the random-draw null is drawn from the SAME pool, many times, so it carries a CI
  * n reported at every restriction, because B narrows the population twice

PRE-COMMITTED READINGS:
  CHOSEN anchors clearly more frequent than random pool draws -> **selection IS frequency-biased**,
      which converts the geometric observation (hub carries frequency 20x) into a measured
      behaviour of the mechanism that assigns meaning.
  AND we pick a more-frequent word over an AVAILABLE correct synonym at a high rate -> that is the
      failure named precisely, and the fix is the selection rule, not the data.
  CHOSEN indistinguishable from random draws -> **the frequency story is dead** even though the
      geometry is real, and the last surviving fidelity hypothesis of the day closes. Say so
      plainly; it would mean the hub's frequency loading does not reach the selection step.
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

from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402

STORE = os.environ.get("DIAG_STORE", "reading_grounding_v1")


def synonyms(w):
    out = set()
    try:
        for s in wn.synsets((w or "").lower()):
            for lem in s.lemma_names():
                out.add(lem.lower().replace("_", " "))
    except Exception:
        pass
    out.discard((w or "").lower())
    return out


def main():
    # ---- frequency table, built independently of the store ------------------------------
    reg = CorpusRegistry()
    freq = collections.Counter()
    for s in reg.handles["simplewiki"].take(20000):
        freq.update(content_lemmas(s))
    cm = np.median([freq.get(w, 0) for w in ("people", "year", "world", "time")])
    rr = np.median([freq.get(w, 0) for w in ("metaphase", "homologous", "parachute")])
    assert cm > rr, "frequency measure does not rank common above rare"
    print("selftest freq: common median %.0f | rare median %.0f" % (cm, rr), flush=True)

    def lf(w):
        return math.log(freq.get((w or "").lower(), 0) + 1)

    p = os.path.join(_REPO, "data", "foundation", STORE, "store", "store_facts.json")
    facts = json.load(open(p, encoding="utf-8"))
    if isinstance(facts, dict):
        facts = facts.get("facts", list(facts.values()))
    gm = [f for f in facts
          if isinstance(f, dict) and str(f.get("relation", "")).upper() == "GROUNDED_MEANING"
          and f.get("obj")]
    print("\nstore %s: %d GROUNDED_MEANING facts with an object" % (STORE, len(gm)))

    # the pool = every word ever used as an anchor (an approximation -- see the docstring)
    pool = sorted({str(f["obj"]).lower() for f in gm})
    print("anchor pool (approximated by every object ever chosen): %d distinct words" % len(pool))
    pool_lf = np.array([lf(w) for w in pool])

    # ---- A. PREFERENCE: chosen vs a random draw from the same pool ----------------------
    chosen_lf = np.array([lf(str(f["obj"])) for f in gm])
    rng = np.random.default_rng(0)
    draws = np.array([pool_lf[rng.integers(0, pool_lf.size, chosen_lf.size)].mean()
                      for _ in range(4000)])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    obs = float(chosen_lf.mean())
    print("\nA. PREFERENCE -- log-frequency of the CHOSEN anchor")
    print("   chosen mean            %.3f  (n=%d)" % (obs, chosen_lf.size))
    print("   random draw from pool  %.3f   95%% CI [%.3f, %.3f]" % (draws.mean(), lo, hi))
    pref = obs > hi
    print("   -> %s" % ("CHOSEN ARE MORE FREQUENT THAN THE POOL" if pref else
                        ("chosen are LESS frequent than the pool" if obs < lo
                         else "indistinguishable from a random draw")))

    # ---- B. THE COSTLY CASE ------------------------------------------------------------
    pool_set = set(pool)
    n_avail = n_missed = n_more_freq = 0
    gaps = []
    for f in gm:
        subj, obj = str(f.get("subject", "")).lower(), str(f.get("obj", "")).lower()
        syns = synonyms(subj) & pool_set
        if not syns:
            continue
        n_avail += 1
        if obj in syns:
            continue                       # we picked a correct one
        n_missed += 1
        best = max(syns, key=lf)           # the most findable correct answer available
        if lf(obj) > lf(best):
            n_more_freq += 1
            gaps.append(lf(obj) - lf(best))
    print("\nB. THE COSTLY CASE -- a correct synonym WAS in the pool")
    print("   subjects with a correct answer available : %d" % n_avail)
    if n_avail:
        print("   ...where we chose something else         : %d  (%.1f%%)"
              % (n_missed, 100.0 * n_missed / n_avail))
    if n_missed:
        print("   ...and what we chose was MORE FREQUENT   : %d  (%.1f%% of misses)"
              % (n_more_freq, 100.0 * n_more_freq / n_missed))
        print("   median log-frequency gap (chosen - best available correct): %+.3f"
              % float(np.median(gaps)) if gaps else "")
        print("   ** UPPER BOUND: the pool is the FINAL pool, so availability is overstated. **")

    print()
    if pref and n_missed and (n_more_freq / n_missed) > 0.5:
        print("VERDICT: **SELECTION IS FREQUENCY-BIASED, AND IT COSTS US CORRECT ANSWERS.** The")
        print("chosen anchor is more frequent than the pool it was drawn from, and where a correct")
        print("synonym was available we usually took a MORE FREQUENT word instead. That converts")
        print("the geometric finding (hub carries frequency ~20x sensorimotor) into a measured")
        print("behaviour of the step that assigns meaning. VET before acting -- and remember B is")
        print("an UPPER BOUND because the final anchor pool overstates what was available.")
    elif pref:
        print("VERDICT: **SELECTION PREFERS FREQUENT WORDS, but the costly case is NOT established.**")
        print("Report the preference; do not claim it costs correct answers.")
    else:
        print("VERDICT: **THE FREQUENCY STORY IS DEAD AT THE SELECTION STEP.** The chosen anchors")
        print("are not more frequent than a random draw from the same pool, so the hub's frequency")
        print("loading -- which is real and measured -- does not reach the choice. The last")
        print("surviving fidelity hypothesis of the day closes, and it closes on evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
