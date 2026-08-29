"""sense_selprefs -- an offline, SENSE-keyed SELECTIONAL-PREFERENCE table (route c of the thematic-fit bakeoff).

WHY THIS EXISTS (brain + method):
The frame-sense disambiguator combines cues by additive-activation -> softmax, which IS the FLMP/Bayesian
posterior ONLY IF the cues are conditionally independent and calibrated log-likelihoods (McClelland 2013). Its
current thematic-fit contribution is read straight off the CONSTRUCTION rules (_TYPE_FRAME_SUPPORT), so it is NOT
independent of the construction cue -- combining them double-counts one signal. This module supplies a GENUINELY
SEPARATE thematic-fit cue: how typical is the object's semantic TYPE as the patient of an event of each candidate
coarse frame, estimated from human sense-tagged text (SemCor), NOT from the construction rules.

WHAT IT COMPUTES:
  fit(verb_lemma, coarse_frame, dobj_head) -> a z-scored thematic-fit score, roughly in [-1.5, 1.5].
    ~+1.5  the object type is much MORE typical of `coarse_frame` than of the verb's other candidate frames
    ~0     no signal / unknown object / verb has one frame  (returns EXACTLY 0.0 -> no effect on the combiner)
    ~-1.5  the object type is much LESS typical of `coarse_frame` than of the verb's other candidate frames

THE TABLE (built offline from SemCor, human sense-tagged running text):
  * For each gold VERB token (synset -> coarse frame = its WordNet verb lexname), find the nearest following gold
    NOUN object within WINDOW tokens, stopping the scan at an intervening preposition / complementizer / verb /
    punctuation so the noun approximates a DIRECT object rather than a PP/adjunct head (measured: the raw window
    conflates caused-motion PP objects into every frame and destroys the signal).
  * Record (coarse_frame, object_supersense, object_head_lemma) and aggregate counts[frame][supersense].
  * P(object_supersense | frame) with add-alpha smoothing over the supersense vocabulary.
  Keyed by COARSE FRAME (not by verb lemma) ON PURPOSE: a place-typed object fits 'motion', a communication/
  cognition-typed object fits 'communication', etc. -- so the cue generalizes across verbs.

fit() SCORING (faithful to the disambiguator's JOINT (verb,noun)-sense co-selection, NOT a single hard label):
  the object's dominant-plus-subordinate noun supersenses form a frequency-WEIGHTED profile (WordNet order =
  frequency proxy; a PLACE sense is retyped to noun.location via hypernyms, matching the ATL place typing the
  disambiguator already uses). For each of the verb's candidate coarse frames f, score(f) = sum_ss w_ss *
  log P(ss | f); the returned value is score(coarse_frame) z-scored ACROSS the verb's candidate frames so the cue
  is comparable frame-to-frame and centered at 0. Using the weighted profile (not just the single dominant
  supersense) is what lets a polysemous object like 'key' (artifact + a crucial-thing / musical sense) or 'fact'
  (cognition + a stated-assertion sense) resolve to the intended frame -- exactly the co-selection the brain does.

Glass-box, no LLM. NLTK WordNet + SemCor only, loaded lazily. ASCII only. Atomic writes. No hdlab writes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import sys
from collections import defaultdict
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

DATA_DIR = os.path.join(REPO, "data", "sense_selprefs_v1")
TABLE_JSON = os.path.join(DATA_DIR, "table.json")
TABLE_PKL = os.path.join(DATA_DIR, "table.pkl")

ALPHA = 0.5          # add-alpha smoothing of P(object_supersense | frame)
WINDOW = 4           # look ahead this many tokens past the verb for its object

# Function words / complementizers that terminate the object scan (a preposition head -> PP object/adjunct, not a
# direct object; a complementizer -> a clause, not an object). Determiners are NOT here (they precede the object).
_STOP = {"to", "into", "onto", "toward", "towards", "from", "for", "at", "in", "on", "of", "with", "by",
         "about", "over", "under", "through", "across", "between", "among", "against", "around",
         "that", "which", "who", "whom", "whose", "where", "when", "because",
         "and", "or", "but", "as", "than", "not", "never"}

# A noun SENSE is a PLACE iff its hypernyms are locations -- mirrors frame_sense_disambiguator._PLACE_HYPERNYMS so
# 'room' (a noun.artifact whose hypernyms include structure/area) types as a place, consistent with the ATL typing
# the disambiguator applies. Applied identically at BUILD time and QUERY time.
_PLACE_HYPERNYMS = {"location", "region", "tract", "geographical_area", "structure", "way", "room",
                    "building", "land", "body_of_water"}


def lexname_to_frame(lexname):
    """WordNet verb lexname ('verb.motion') -> coarse frame ('motion'). None if not a verb lexname.
    Defined locally (NOT imported from frame_sense_disambiguator) to avoid a circular import that would silently
    disable this cue (the disambiguator imports this module before it defines lexname_to_frame)."""
    if not lexname or not lexname.startswith("verb."):
        return None
    return lexname.split(".", 1)[1]


def effective_supersense(syn):
    """Object supersense for one noun synset: its WordNet lexname, except a PLACE sense (location hypernyms) is
    retyped to 'noun.location' so 'room'/'field'/'house' count as places rather than raw artifacts."""
    lex = syn.lexname()
    if lex and lex.startswith("noun."):
        names = set()
        for path in syn.hypernym_paths():
            for h in path:
                names.add(h.name().split(".")[0])
        if names & _PLACE_HYPERNYMS:
            return "noun.location"
    return lex


# ---------------------------------------------------------------------------
# Asset load (cached)
# ---------------------------------------------------------------------------
_TABLE = None
_LOADED = False


def _load():
    global _TABLE, _LOADED
    if _LOADED:
        return _TABLE
    _LOADED = True
    _TABLE = None
    try:
        if os.path.exists(TABLE_JSON):
            with open(TABLE_JSON, "r", encoding="ascii") as f:
                _TABLE = json.load(f)
        elif os.path.exists(TABLE_PKL):
            with open(TABLE_PKL, "rb") as f:
                _TABLE = pickle.load(f)
    except Exception:
        _TABLE = None
    return _TABLE


def _logP(table, frame, ss):
    """log P(object_supersense ss | coarse frame). None if the frame is not in the table."""
    counts = table["counts"].get(frame)
    if counts is None:
        return None
    tot = table["frame_totals"][frame]
    V = table["n_supersenses"]
    alpha = table.get("alpha", ALPHA)
    c = counts.get(ss, 0.0)
    return math.log((c + alpha) / (tot + alpha * V))


# ---------------------------------------------------------------------------
# WordNet lookups for the query side (cached)
# ---------------------------------------------------------------------------
_PROFILE_CACHE = {}
_CANDFR_CACHE = {}


def _noun_supersense_profile(word):
    """The object noun's frequency-WEIGHTED supersense profile: {supersense -> weight in [0,1]} over its top noun
    senses (WordNet order = frequency proxy, rank-decayed floor), with the place retyping applied."""
    if not word:
        return {}
    w = str(word).lower()
    if w in _PROFILE_CACHE:
        return _PROFILE_CACHE[w]
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(w, pos="n")[:6]
    except Exception:
        syns = []
    freqs, sss = [], []
    for rank, s in enumerate(syns):
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == w)
        freqs.append(c + 1.0 / (rank + 1.0))
        sss.append(effective_supersense(s))
    tot = sum(freqs)
    prof = defaultdict(float)
    for ss, f in zip(sss, freqs):
        if ss and tot > 0:
            prof[ss] += f / tot
    out = dict(prof)
    _PROFILE_CACHE[w] = out
    return out


def _verb_candidate_frames(lemma):
    """The verb's distinct coarse frames (its WordNet verb lexnames), order preserved. The z-score normalization
    is taken across THIS set -- the same candidate set the disambiguator scores over."""
    if not lemma:
        return []
    w = str(lemma).lower()
    if w in _CANDFR_CACHE:
        return _CANDFR_CACHE[w]
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(w, pos="v")
    except Exception:
        syns = []
    frames, seen = [], set()
    for s in syns:
        fr = lexname_to_frame(s.lexname())
        if fr and fr not in seen:
            seen.add(fr)
            frames.append(fr)
    _CANDFR_CACHE[w] = frames
    return frames


# ---------------------------------------------------------------------------
# THE CUE
# ---------------------------------------------------------------------------
def fit(verb_lemma, coarse_frame, dobj_head):
    """Thematic-fit score for `dobj_head` as the object of `verb_lemma` in its `coarse_frame` sense.

    z-scored log P(object supersense | coarse_frame) across the verb's candidate frames, roughly in [-1.5, 1.5].
    Returns EXACTLY 0.0 (no effect) when: the asset is missing; the object has no WordNet noun sense; the verb has
    fewer than two candidate coarse frames in the table (nothing to normalize against); or the frames tie."""
    table = _load()
    if table is None:
        return 0.0
    prof = _noun_supersense_profile(dobj_head)
    if not prof:
        return 0.0
    frames = _verb_candidate_frames(verb_lemma)
    # candidate set = verb's frames plus the queried frame, restricted to frames the table knows about
    fset = [f for f in dict.fromkeys(list(frames) + [coarse_frame]) if f in table["counts"]]
    if coarse_frame not in fset or len(fset) < 2:
        return 0.0

    def score(f):
        s = 0.0
        for ss, w in prof.items():
            lp = _logP(table, f, ss)
            if lp is not None:
                s += w * lp
        return s

    vals = [score(f) for f in fset]
    mu = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals))
    if sd < 1e-9:
        return 0.0
    z = (score(coarse_frame) - mu) / sd
    return max(-1.5, min(1.5, z))


# ---------------------------------------------------------------------------
# Offline asset builder (from SemCor)
# ---------------------------------------------------------------------------
def _sent_tokens(sent, Tree):
    """Flatten a SemCor tagged sentence to [(surface_first_word_lower, synset_or_None), ...]."""
    toks = []
    for ch in sent:
        if isinstance(ch, Tree):
            lab = ch.label()
            syn = None
            if hasattr(lab, "synset"):
                try:
                    syn = lab.synset()
                except Exception:
                    syn = None
            w = ch.leaves()
            toks.append((w[0].lower() if w else "", syn))
        else:
            for w in (ch if isinstance(ch, list) else [ch]):
                toks.append((str(w).lower(), None))
    return toks


def _atomic_write(table):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = TABLE_JSON + ".tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(table, f, indent=1, sort_keys=True, ensure_ascii=True)
    os.replace(tmp, TABLE_JSON)


def build(max_sents=None, verbose=True):
    """Build data/sense_selprefs_v1/table.json from SemCor. Returns the table dict, or None if SemCor is absent."""
    try:
        from nltk.corpus import semcor
        from nltk.tree import Tree
    except Exception as e:
        print("SemCor / NLTK unavailable:", e)
        return None
    try:
        sents = semcor.tagged_sents(tag="sem")
        n_total = len(sents)
    except Exception as e:
        print("Could not load SemCor tagged_sents:", e)
        print("Install with: python -c \"import nltk; nltk.download('semcor'); "
              "nltk.download('wordnet'); nltk.download('omw-1.4')\"")
        return None

    N = n_total if max_sents is None else min(max_sents, n_total)
    counts = defaultdict(lambda: defaultdict(float))       # frame -> supersense -> count
    head_counts = defaultdict(lambda: defaultdict(float))  # frame -> object head lemma -> count (auxiliary)
    n_pairs = 0
    for i in range(N):
        toks = _sent_tokens(sents[i], Tree)
        for j, (surf, syn) in enumerate(toks):
            if syn is None or syn.pos() != "v":
                continue
            frame = lexname_to_frame(syn.lexname())
            if frame is None:
                continue
            for k in range(j + 1, min(j + 1 + WINDOW, len(toks))):
                surf2, s2 = toks[k]
                if s2 is not None:
                    if s2.pos() == "n":
                        counts[frame][effective_supersense(s2)] += 1.0
                        head_counts[frame][surf2] += 1.0
                        n_pairs += 1
                        break
                    elif s2.pos() == "v":
                        break                       # another verb -> no direct object for this verb
                    else:
                        continue                    # tagged adjective/adverb -> skip
                else:
                    if (surf2 in _STOP) or (not surf2.isalnum()):
                        break                       # preposition / complementizer / punctuation -> stop
                    continue                        # determiner / other function word -> skip

    supersenses = sorted({ss for d in counts.values() for ss in d})
    frame_totals = {fr: sum(d.values()) for fr, d in counts.items()}
    # prune the auxiliary head-lemma table to count >= 2 to bound the asset size
    head_pruned = {fr: {h: c for h, c in d.items() if c >= 2} for fr, d in head_counts.items()}
    table = {
        "version": "sense_selprefs_v1",
        "source": "SemCor (nltk corpus, tag=sem); human sense-tagged running text",
        "built_ts": datetime.now(timezone.utc).isoformat(),
        "window": WINDOW,
        "alpha": ALPHA,
        "semcor_sents_scanned": N,
        "n_pairs": n_pairs,
        "n_frames": len(counts),
        "n_supersenses": len(supersenses),
        "supersenses": supersenses,
        "frame_totals": frame_totals,
        "counts": {fr: dict(d) for fr, d in counts.items()},
        "head_counts": head_pruned,
    }
    _atomic_write(table)
    # refresh the module cache so a subsequent fit() in the same process uses the fresh table
    global _TABLE, _LOADED
    _TABLE, _LOADED = table, True
    if verbose:
        print(f"built {TABLE_JSON}: {len(counts)} frames x {len(supersenses)} supersenses, "
              f"{n_pairs} (verb,object) pairs from {N} SemCor sentences")
    return table


# ---------------------------------------------------------------------------
# Reporting + self-test
# ---------------------------------------------------------------------------
def _report_top(table, frames=("motion", "possession", "communication", "perception"), k=5):
    for fr in frames:
        d = table["counts"].get(fr)
        if not d:
            print(f"  [{fr}] (not in table)")
            continue
        tot = table["frame_totals"][fr]
        V = table["n_supersenses"]
        alpha = table.get("alpha", ALPHA)
        top = sorted(d.items(), key=lambda kv: -kv[1])[:k]
        print(f"  [{fr}] total_objects={int(tot)}")
        for ss, c in top:
            p = (c + alpha) / (tot + alpha * V)
            print(f"      {ss:20s} count={int(c):4d}  P(ss|frame)={p:.4f}")


_SELF_TEST_CASES = [
    # (verb, higher_frame, object, lower_frame) -- fit(verb, higher, obj) must exceed fit(verb, lower, obj)
    ("leave", "motion", "room", "possession"),
    ("leave", "possession", "key", "motion"),
    ("observe", "communication", "fact", "perception"),
]


def _self_test():
    table = _load()
    if table is None:
        print("no asset found -- building from SemCor first ...")
        table = build()
        if table is None:
            print("SELF-TEST sense_selprefs: SKIPPED (SemCor unavailable)")
            return False
    print(f"table size: {table['n_frames']} frames x {table['n_supersenses']} supersenses "
          f"({table['n_pairs']} verb-object pairs)")
    print("top-5 P(object_supersense | frame):")
    _report_top(table)
    print("ordering self-test:")
    ok_all = True
    for v, fa, ob, fb in _SELF_TEST_CASES:
        a = fit(v, fa, ob)
        b = fit(v, fb, ob)
        ok = a > b
        ok_all = ok_all and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] fit({v!r},{fa!r},{ob!r})={a:+.3f} > "
              f"fit({v!r},{fb!r},{ob!r})={b:+.3f}")
    assert ok_all, "selectional-preference ordering self-test FAILED"
    print("SELF-TEST sense_selprefs: PASS")
    return True


def main():
    ap = argparse.ArgumentParser(description="SENSE-keyed selectional-preference table (thematic-fit cue).")
    ap.add_argument("--build", action="store_true", help="build the asset from SemCor")
    ap.add_argument("--self-test", action="store_true", help="build if needed, then assert fit orderings")
    ap.add_argument("--max-sents", type=int, default=None, help="cap SemCor sentences (debug)")
    args = ap.parse_args()
    if args.build:
        build(max_sents=args.max_sents)
    if args.self_test or not args.build:
        _self_test()


if __name__ == "__main__":
    main()
