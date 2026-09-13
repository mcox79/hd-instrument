"""build_manner_intensity_asset.py -- OFFLINE foundation asset for the MANNER-INTENSITY read of harm/help.

WHY (the problem). For verbs like brutalize / manhandle / maltreat / tyrannize / subjugate / gore the harm does
not live in the verb's result state (VerbNet names none) nor in its superordinate category (WordNet troponymy
gives the affect-NEUTRAL 'treat' / 'handle'): it lives in a MANNER expression -- "treat BRUTALLY", "handle
ROUGHLY", "in a CRUEL manner". Every parse-FREE read of the definition leaks (drilled: 4-8 neutral leaks and
3-6 wrong signs per 4 verbs recovered). The missing input is not a threshold; it is the DECOMPOSITION of the
verb concept into its manner / means / result components, plus a grounded reading of HOW FORCEFUL the manner is.

THE BRAIN (what this asset supplies, and why it is the brain's computation).
  1. MANNER / RESULT COMPLEMENTARITY (Talmy 1985/2000; Levin & Rappaport Hovav 2010, PINNED as a lexicalisation
     universal): a verb root lexicalises either the MANNER of an action or its RESULT state, never both. The
     comprehension of a manner verb therefore has to value the MANNER component -- there is no result state to
     value. This asset stores that decomposition per verb SENSE.
  2. GROUNDED SIMULATION OF THE MANNER (Barsalou 1999 perceptual symbols; Zwaan immersed experiencer;
     Pulvermuller action-word somatotopy, PINNED): understanding "brutally" re-enacts a forceful bodily action.
     The FORCE MAGNITUDE of that simulation is read from the sensorimotor spokes (Lancaster action/haptic
     strength) and from core-affect ACTIVATION (Warriner arousal = Russell's circumplex arousal axis / Osgood's
     Activity, PINNED as the second core-affect dimension).
  3. OUTCOME VALUATION WITH THE SIGN FROM VALENCE (OFC/vmPFC value coding; Barrett core affect, PINNED):
     value(patient endstate) = sign(valence(manner)) scaled by the simulated force intensity. Sign and magnitude
     come from DIFFERENT channels, which is why a high-arousal POSITIVE manner ("thrill", "excitedly") reads HELP
     and a high-arousal NEGATIVE manner ("brutally") reads HARM -- the 2x2 the parse-free proxies collapsed.
  4. WHERE THE MANNER WORD COMES FROM: at read time from the reader's own parse of the sentence (the adverb bound
     to the predicate). For a LEXICALISED manner verb the manner is inside the stored lexical concept; this asset
     recovers it by parsing the verb's WordNet definition WITH THE READER'S OWN GLASS-BOX PARSE STACK
     (hdlab.frontend = the count-based category organ + the attachment arm) -- no spaCy, no supervised parser,
     nothing external, and nothing at inference: the parse happens HERE, at build time, and a dict is shipped.
     WordNet's definitions are an admissible offline foundation asset (the same standing as the VerbNet result
     predicates the landed arm already reads).

WHAT IS SHIPPED (data/frontend_assets/manner_intensity_v1.json):
  words:    filler word -> {v: valence [-1,1], a: arousal [0,1], d: dominance [0,1], g: grounded action strength
            [0,1], stem: the adjective the manner adverb is derived from}   (norm SUPPLY; never a decision)
  evidence: verb lemma -> [[synset, slot, filler, count], ...]   COUNTS, so the table is plastic: the online
            `observe_manner(verb, filler, slot)` path increments the same counts when the reader meets a manner
            adverb bound to that verb in running prose. Strengths are one pure function of the counts.

SLOTS (each is a CONSTRUCTION detected over the reader's own tags + heads, not a regex over raw text):
  ADVMOD    de-adjectival ADV whose parsed head is the definition's head predicate      ("treat BRUTALLY")
  MANNER_PP the ADJ inside "in a/an ADJ ... manner|way|fashion"                          ("in a CRUEL manner")
  MEANS_PP  the content word governed by by/with/through under the head predicate        ("by FORCE")
  RESULT_ADJ the ADJ predicated by make/render/leave/cause                               ("make SUBSERVIENT")
  GENUS     the head predicate of the definition itself (the definitional superordinate)  ("WOUND by piercing")
The de-adjectival test on ADVMOD (a WordNet pertainym, else -ly stripping with a lexical check = Taft's affix
strip + lexical check, PINNED) is what keeps verb particles ("put DOWN") out of the manner slot.

Run:  .venv/Scripts/python.exe tools/build_manner_intensity_asset.py
      .venv/Scripts/python.exe tools/build_manner_intensity_asset.py --limit 400     (smoke)
Deterministic, glass-box, ASCII. Build-time only -- the organ reads the JSON.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import csv
import json
import sys
import time
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

WARRINER = os.path.join(REPO, "data", "frontend_assets", "Ratings_Warriner_et_al.csv")
LANCASTER = os.path.join(REPO, "data", "grounding_testbed",
                         "Lancaster_sensorimotor_norms_for_39707_words.csv")
OUT = os.path.join(REPO, "data", "frontend_assets", "manner_intensity_v1.json")

MANNER_NOUNS = {"manner", "way", "fashion", "style"}
MEANS_ADP = {"by", "with", "through"}
RESULT_VERBS = {"make", "render", "leave", "cause", "turn"}
# glosses name the object with these placeholders; they are never the manner filler
PLACEHOLDERS = {"someone", "somebody", "something", "one", "sb", "sth", "person", "people"}


# --------------------------------------------------------------------------------------------------
# 1. NORM SUPPLY (offline; valence = sign channel, arousal/dominance/grounded action = intensity channels)
# --------------------------------------------------------------------------------------------------
def load_warriner() -> Dict[str, Tuple[float, float, float]]:
    """word -> (valence [-1,1], arousal [0,1], dominance [0,1]). Warriner et al. 2013 (Osgood E/A/P)."""
    out: Dict[str, Tuple[float, float, float]] = {}
    with open(WARRINER, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            try:
                v = float(row["V.Mean.Sum"]); a = float(row["A.Mean.Sum"]); d = float(row["D.Mean.Sum"])
            except (KeyError, ValueError):
                continue
            out[w] = (round((v - 5.0) / 4.0, 4), round((a - 1.0) / 8.0, 4), round((d - 1.0) / 8.0, 4))
    return out


def load_lancaster() -> Dict[str, float]:
    """word -> grounded ACTION/CONTACT strength in [0,1] = max(haptic, hand_arm, torso, foot_leg)/5.
    The sensorimotor spokes that a forceful manner re-enacts (Lancaster norms, Lynott et al. 2020)."""
    out: Dict[str, float] = {}
    if not os.path.exists(LANCASTER):
        return out
    with open(LANCASTER, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            try:
                vals = [float(row["Haptic.mean"]), float(row["Hand_arm.mean"]),
                        float(row["Torso.mean"]), float(row["Foot_leg.mean"])]
            except (KeyError, ValueError):
                continue
            out[w] = round(max(vals) / 5.0, 4)
    return out


# --------------------------------------------------------------------------------------------------
# 2. DE-ADJECTIVAL MANNER ADVERBS (morpho-orthographic decomposition; Rastle & Davis, Taft: strip + check)
# --------------------------------------------------------------------------------------------------
def adverb_stem(word: str, wn) -> Optional[str]:
    """The ADJECTIVE a manner adverb is derived from ('brutally'->'brutal'), or None when the word is not a
    de-adjectival adverb (verb particles 'down'/'up'/'off' fail here). Route 1 = the stored derivational link
    (WordNet pertainym = the mental lexicon's morphological family); route 2 = -ly stripping with a LEXICAL
    CHECK (the candidate must exist as an adjective). Dual route, Pinker-Ullman / Taft 1979."""
    w = word.lower()
    for s in wn.synsets(w, "r"):
        for lm in s.lemmas():
            if lm.name().lower() == w:
                for p in lm.pertainyms():
                    return p.name().lower()
    if w.endswith("ly") and len(w) > 4:
        for cand in (w[:-2], w[:-1] + "e", w[:-3] + "y" if w.endswith("ily") else None):
            if cand and wn.synsets(cand, "a"):
                return cand
    return None


# --------------------------------------------------------------------------------------------------
# 3. THE GLOSS DECOMPOSITION, read with the READER'S OWN parse (no external parser at any point)
# --------------------------------------------------------------------------------------------------
def head_predicate(tokens: List[str], pos: List[str], heads: Dict[int, int], wn) -> Optional[int]:
    """0-based index of the definition's head predicate. A definition of a verb is a verb phrase, so: the
    parsed ROOT if it is a VERB; else the first token the mental lexicon knows as a verb (the lexical check
    that repairs the category organ's known miss on a gloss-initial bare verb: 'rule ...' tagged NOUN)."""
    for i in range(len(tokens)):
        if heads.get(i + 1, -1) == 0 and pos[i] == "VERB":
            return i
    for i, (t, p) in enumerate(zip(tokens, pos)):
        if p == "VERB":
            return i
    for i, t in enumerate(tokens[:2]):
        if t.isalpha() and wn.synsets(t.lower(), "v"):
            return i
    return None


def decompose_clause(tokens, pos, heads, wn) -> List[Tuple[str, str]]:
    """(slot, filler) pairs for ONE definition clause, over the reader's own categories + heads."""
    out: List[Tuple[str, str]] = []
    hp = head_predicate(tokens, pos, heads, wn)
    if hp is None:
        return out
    low = [t.lower() for t in tokens]
    # -- GENUS: the head predicate itself (the definitional superordinate) --
    out.append(("GENUS", low[hp]))
    for i, t in enumerate(low):
        if not t.isalpha():
            continue
        h = heads.get(i + 1, -1) - 1
        # -- ADVMOD: a DE-ADJECTIVAL adverb bound to the head predicate --
        if pos[i] == "ADV" and h == hp:
            st = adverb_stem(t, wn)
            if st:
                out.append(("ADVMOD", st))
        # -- MANNER_PP: "in a/an [ADJ ...] manner|way|fashion" --
        if t in MANNER_NOUNS and i >= 2:
            j = i - 1
            adjs = []
            while j >= 0 and (pos[j] in ("ADJ", "CCONJ", "PUNCT", "ADV") or low[j] in ("a", "an", "the")):
                if pos[j] == "ADJ":
                    adjs.append(low[j])
                if low[j] in ("a", "an", "the"):
                    break
                j -= 1
            if j >= 1 and low[j - 1] == "in" and adjs:
                out.extend(("MANNER_PP", a) for a in adjs)
        # -- MEANS_PP: by/with/through + the first following content word --
        if t in MEANS_ADP and pos[i] == "ADP":
            for k in range(i + 1, min(i + 4, len(low))):
                if pos[k] in ("NOUN", "VERB", "ADJ") and low[k] not in PLACEHOLDERS:
                    out.append(("MEANS_PP", low[k]))
                    break
        # -- RESULT_ADJ: make/render/leave/cause + ADJ (an ADJ run, "make brutal, unfeeling, or inhuman") --
        if t in RESULT_VERBS and i == hp:
            for k in range(i + 1, min(i + 6, len(low))):
                if pos[k] == "ADJ":
                    out.append(("RESULT_ADJ", low[k]))
                elif pos[k] in ("PUNCT", "CCONJ", "ADV") or low[k] in PLACEHOLDERS:
                    continue
                else:
                    break
    return out


def parse_gloss(defn: str, tagger, parser, wn) -> List[Tuple[str, str]]:
    """Decompose a WordNet definition. Semicolon-separated definitions are separate statements of the same
    concept (WordNet convention) -- each is parsed on its own; parenthetical usage notes are dropped."""
    import re
    from hdlab import frontend as FE
    body = re.sub(r"\([^)]*\)", " ", defn)
    pairs: List[Tuple[str, str]] = []
    for clause in body.split(";"):
        toks = FE.tokenize(clause)[:28]
        if not toks:
            continue
        try:
            p, post = tagger.tag_with_posterior(toks)
            heads = dict(parser.parse(toks, p, post).heads)
        except Exception:
            continue
        pairs.extend(decompose_clause(toks, p, heads, wn))
    return pairs


# --------------------------------------------------------------------------------------------------
# 4. BUILD
# --------------------------------------------------------------------------------------------------
def build(limit: Optional[int] = None) -> Dict:
    from nltk.corpus import wordnet as wn
    from hdlab import frontend as FE
    import hdlab.force_dynamics_valence as FDV

    tagger, parser = FE.Tagger(), FE.Parser()
    war, lan = load_warriner(), load_lancaster()

    # the population: exactly the senses the harm/help arm is allowed to read -- AFFECTING supersense with an
    # ANIMATE-OBJECT frame (the same gate the landed result-state and superordinate reads use).
    syns = [s for s in wn.all_synsets("v")
            if s.lexname().split(".")[1] in FDV.AFFECTING_SUPERSENSES
            and (set(s.frame_ids()) & FDV.ANIMATE_OBJECT_FRAMES)]
    if limit:
        syns = syns[:limit]

    evidence: Dict[str, Dict[Tuple[str, str], int]] = {}
    words: Dict[str, Dict[str, float]] = {}
    t0 = time.time()
    for n, ss in enumerate(syns):
        if n and n % 500 == 0:
            print("  %d/%d synsets  %.0fs" % (n, len(syns), time.time() - t0), flush=True)
        pairs = parse_gloss(ss.definition(), tagger, parser, wn)
        if not pairs:
            continue
        for lm in ss.lemmas():
            v = lm.name().lower()
            if "_" in v:
                continue
            slot_map = evidence.setdefault(v, {})
            for slot, filler in pairs:
                if filler == v:            # a definition that names the verb itself carries no new signal
                    continue
                slot_map[(ss.name(), slot, filler)] = slot_map.get((ss.name(), slot, filler), 0) + 1

    for slot_map in evidence.values():
        for (_syn, _slot, filler) in slot_map:
            if filler in words:
                continue
            v, a, d = war.get(filler, (None, None, None))
            g = lan.get(filler)
            if v is None and g is None:
                continue
            words[filler] = {k: x for k, x in
                             (("v", v), ("a", a), ("d", d), ("g", g)) if x is not None}

    out = {
        "meta": {
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "WordNet verb definitions (affecting supersense x animate-object frames), parsed with "
                      "hdlab.frontend (count-based category organ + attachment arm); Warriner 2013 V/A/D; "
                      "Lancaster sensorimotor action strength",
            "tag_source": tagger.source, "heads_source": parser.source,
            "n_synsets": len(syns), "n_verbs": len(evidence), "n_words": len(words),
            "slots": ["ADVMOD", "MANNER_PP", "MEANS_PP", "RESULT_ADJ", "GENUS"],
            "plastic": "evidence entries carry COUNTS; the organ's observe_manner(verb, filler, slot) "
                       "increments them from running prose (same units, one pure function of counts)",
        },
        "words": words,
        "evidence": {v: sorted([[s, sl, f, c] for (s, sl, f), c in m.items()])
                     for v, m in sorted(evidence.items())},
    }
    return out


def main() -> None:
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    asset = build(limit)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(asset, f, separators=(",", ":"), sort_keys=True)
    os.replace(tmp, OUT)
    print("wrote %s" % OUT)
    print("  verbs=%d words=%d synsets=%d" % (
        asset["meta"]["n_verbs"], asset["meta"]["n_words"], asset["meta"]["n_synsets"]))
    for v in ("brutalize", "manhandle", "maltreat", "tyrannize", "subjugate", "gore"):
        print("  %-11s %s" % (v, asset["evidence"].get(v, [])[:6]))


if __name__ == "__main__":
    main()
