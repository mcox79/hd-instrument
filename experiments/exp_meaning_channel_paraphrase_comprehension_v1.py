"""Does the LANDED conceptual meaning channel earn its keep in COMPREHENSION (recognize-not-recite)?

The front-end (who-did-what) and entity (character-tracking) axes are validated end-to-end. The MEANING axis is only
shown in isolation (synonyms >> unrelated). This tests its COMPREHENSION contribution: answer a PARAPHRASED question
("what did X PURSUE?" when the story said "chased") -- which requires recognising chase==pursue (ATL conceptual identity),
something exact-word matching structurally cannot do.

TASK (per LitBank document): the story records events as (entity, VERB). A question asks about an event using a
PARAPHRASE verb (a WordNet synonym of the true verb, a DIFFERENT lemma). Retrieve the correct event among the document's
verbs.
  * OFF  exact-match      : retrieve the verb that string-equals the query -> STRUCTURALLY FAILS on a paraphrase (0).
  * ON   conceptual_meaning: argmax similarity(query_verb, candidate_verb) -> should recover the synonym.
  * TWIN random           : a random candidate verb -> info-free, must lose.
Brain-foundational: ATL conceptual/definitional identity (Controlled Semantic Cognition) underlies recognise-not-recite.

Run:  .venv/Scripts/python.exe experiments/exp_meaning_channel_paraphrase_comprehension_v1.py [--docs N]
"""
from __future__ import annotations

import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H  # LitBank streams (gov_verb per mention)
from hdlab.conceptual_meaning import ConceptualChannel  # THE LANDED ORGAN
from nltk.corpus import wordnet as wn

SEED = 20260827


def _verb_synonym(verb):
    """A WordNet synonym of `verb` (verb sense) that is a DIFFERENT lemma -- the paraphrase query. None if none."""
    for syn in wn.synsets(verb, pos="v"):
        for ln in syn.lemma_names():
            cand = ln.replace("_", " ").lower()
            if cand != verb and " " not in cand and cand.isalpha():
                return cand
    return None


def main():
    docs = 80
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = H.load_cache()[:docs]
    chan = ConceptualChannel()   # landed organ (loads cached global IDF)
    rng = np.random.default_rng(SEED)

    off, on, twin = [], [], []
    n_items = 0
    for rec in recs:
        verbs = sorted({m["gov_verb"] for m in rec["stream"] if m.get("gov_verb")})
        cand = [v for v in verbs if v.isalpha() and len(v) >= 3]
        if len(cand) < 3:
            continue
        for target in cand:
            q = _verb_synonym(target)
            if q is None or q in cand:      # need a TRUE paraphrase: a synonym NOT already a candidate string
                continue
            # ON: conceptual-meaning similarity of the paraphrase query to each candidate verb; argmax
            sims = [(chan.similarity(q, "V", v, "V") or -1.0) for v in cand]
            if max(sims) <= -1.0:
                continue
            pred_on = cand[int(np.argmax(sims))]
            n_items += 1
            on.append(int(pred_on == target))
            off.append(int(q == target))                       # exact match -> 0 by construction (q != target)
            twin.append(int(cand[int(rng.integers(0, len(cand)))] == target))

    n = len(on)
    if n == 0:
        print("no paraphrase items constructed"); return 1

    def ci(a, s):
        a = np.asarray(a, float); r = np.random.default_rng(s); nb = len(a)
        b = [a[r.integers(0, nb, nb)].mean() for _ in range(2000)]
        return a.mean(), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    def diff(a, b, s):
        a = np.asarray(a, float); b = np.asarray(b, float); r = np.random.default_rng(s); nb = len(a)
        d = [(a[i].mean() - b[i].mean()) for i in (r.integers(0, nb, nb) for _ in range(2000))]
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        return {"delta": round(float(a.mean() - b.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    chance = 1.0 / np.mean([1]) if False else None
    print(f"=== MEANING CHANNEL in PARAPHRASE COMPREHENSION (LitBank, n={n} paraphrase items) ===")
    for name, arr in (("OFF exact-match", off), ("ON conceptual_meaning", on), ("TWIN random", twin)):
        acc, lo, hi = ci(arr, SEED + 1)
        print(f"  {name:24s} {acc:.4f}  CI[{lo:.4f},{hi:.4f}]")
    print(f"  ON - OFF  : {diff(on, off, SEED+2)}  (does meaning recover paraphrases exact-match cannot?)")
    print(f"  ON - TWIN : {diff(on, twin, SEED+3)}  (info-free twin must lose)")
    print("\n[meaning axis] if ON beats OFF (exact) + TWIN CI-sep, the landed conceptual channel earns its keep in")
    print("comprehension: it recovers who-did-what when the question is PARAPHRASED (recognise-not-recite).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
