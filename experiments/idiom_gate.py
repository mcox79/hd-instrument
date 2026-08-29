"""idiom_gate -- a glass-box, offline STORED-UNIT idiom / multiword-expression (MWE) lexicon.

BRAIN MECHANISM (the piece this supplies):
The mental lexicon stores non-compositional multiword expressions as UNITS and retrieves them
HOLISTICALLY, before (and instead of) literal word-by-word composition (Jackendoff's construction
lexicon; Cutting & Bock 1997 -- idioms are accessed directly, faster than their literal control
phrases). This is exactly the residual that caps a compositional verb-sense disambiguator: "pass a
law" is NOT motion, "pass away" is dying (a change of state), "make sense" is cognition, "go off" is
a change/discharge. A construction cue built from the realized syntax cannot recover these because
the non-compositionality is LEXICALIZED, not structural. So we store them as units and retrieve the
stored coarse event-frame directly.

WHAT THIS IS: a static, committed data asset (data/idiom_foundation_v1/idioms.json) built OFFLINE
from glass-box sources -- WordNet's multiword verb inventory + a PMI-mined corpus pass + a small
hand-vetted institutional/abstract-object table. NO LLM at inference (a static asset is admissible;
the runtime lookup is a dict get). The asset has two maps:
    phrasal : "verb|particle"   -> coarse frame   (pass|away -> change, go|off -> motion, ...)
    vobj    : "verb|objecthead" -> coarse frame   (make|sense -> cognition, take|place -> stative)

BUILD SOURCES (glass-box, no LLM):
  1. PHRASAL VERBS  -- every WordNet verb synset whose lemma is a two-token "verb_particle"
     (pass_away, go_off, give_up, take_off, break_down, come_across, make_out, ...). key=(base,
     particle), value = lexname_to_frame(synset.lexname()), keeping the HIGHEST-count sense per key.
     Captures phrasal-verb non-compositionality straight from WordNet.
  2a. VERB+OBJECT MWEs (WordNet) -- two-token "verb_noun" verb lemmas (take_place, make_love,
      make_sense, ...) -> frame from the synset lexname (highest-count sense per key).
  2b. VERB+OBJECT MWEs (PMI-mined) -- parse a chunk of a corpus, collect (verb_lemma, dobj_head)
      bigrams, compute PMI, keep high-PMI pairs, and MARK a pair non-compositional iff EITHER
      (i)  WordNet has a dedicated "verb_noun" sense whose frame DIFFERS from the verb's dominant
           frame (a lexicalised, non-literal reading exists), OR
      (ii) the object is a strong institutional/abstract object for a bleached light/motion/contact
           verb (pass+law -> social, hold+meeting -> social, take+place -> stative).
      Precision over recall: only pairs justifiable by (i) or (ii) are kept.
  A small hand-vetted CURATED_VOBJ table (the "top ~40 institutional/abstract objects" the brief
  names) is applied LAST and OVERRIDES the derived entries -- it is the authoritative frame for the
  clearest legislative/eventive/cognitive light-verb collocations.

The build guards a missing corpus gracefully: the WordNet + curated asset still works without 2b.

ASCII only. No hdlab writes. No preregs.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ---------------------------------------------------------------------------
# Coarse event-FRAME inventory -- MUST match frame_sense_disambiguator.COARSE_FRAMES (the WordNet
# verb lexnames / Ciaramita-Altun supersenses). Replicated locally (a 15-item list + a 3-line pure
# function) to keep this module import-light and to avoid a circular import: the disambiguator
# imports idiom_gate, so idiom_gate must NOT import the disambiguator.
# ---------------------------------------------------------------------------
COARSE_FRAMES = ["motion", "possession", "communication", "perception", "cognition",
                 "change", "contact", "stative", "creation", "body", "emotion",
                 "consumption", "social", "competition", "weather"]
_FRAMESET = set(COARSE_FRAMES)


def lexname_to_frame(lexname: Optional[str]) -> Optional[str]:
    """WordNet verb lexname ('verb.motion') -> coarse frame ('motion'). None if not a verb lexname."""
    if not lexname or not lexname.startswith("verb."):
        return None
    return lexname.split(".", 1)[1]


# Standard phrasal-verb particles (adverbial/prepositional). A two-token verb lemma whose tail is
# here is treated as a phrasal verb; a tail NOT here (and that is a noun) is treated as verb+object.
PARTICLES = {"away", "off", "out", "up", "down", "in", "on", "over", "back", "across", "around",
             "about", "along", "apart", "aside", "forth", "forward", "through", "together", "under",
             "by", "upon", "ahead", "round", "past", "away"}

# Objects that are so strongly institutional/eventive that, combined with a bleached light / motion /
# contact verb, the phrase is non-compositional and the OBJECT fixes the frame (robust across which
# bleached verb governs it). Used by PMI gate (ii). Deliberately narrow (legislative + eventive) --
# cognition/communication light-verb objects are handled only via the explicit CURATED_VOBJ pairs.
INSTITUTIONAL_OBJ2FRAME = {
    "law": "social", "bill": "social", "act": "social", "legislation": "social",
    "resolution": "social", "amendment": "social", "ordinance": "social", "statute": "social",
    "referendum": "social", "election": "social", "vote": "social", "ballot": "social",
    "meeting": "social", "hearing": "social", "summit": "social", "office": "social",
    "place": "stative", "war": "competition",
}

# Bleached light / motion / contact verbs eligible for gate (ii) -- their literal frame is not the
# phrase's frame ("pass"/"hold"/"take" are not motion/possession in "pass a law", "hold a meeting").
LIGHT_MOTION_CONTACT = {"pass", "hold", "take", "make", "call", "put", "win", "lose", "carry",
                        "wage", "declare", "veto", "sign", "bring", "stand", "run"}

# The authoritative hand-vetted institutional/abstract-object table (the brief's "top ~40"). Applied
# LAST; overrides WordNet-derived + PMI-derived entries. Each entry is a non-compositional collocation
# whose stored frame differs from the literal verb reading. Every value is in COARSE_FRAMES.
CURATED_VOBJ: Dict[str, str] = {
    # --- legislation / governance (social) ---
    "pass|law": "social", "pass|bill": "social", "pass|act": "social",
    "pass|legislation": "social", "pass|resolution": "social", "pass|amendment": "social",
    "pass|motion": "social", "pass|ordinance": "social", "pass|statute": "social",
    "sign|bill": "social", "sign|law": "social", "veto|bill": "social",
    "hold|election": "social", "hold|meeting": "social", "hold|vote": "social",
    "hold|referendum": "social", "hold|hearing": "social", "hold|session": "social",
    "hold|conference": "social", "hold|ceremony": "social", "hold|office": "social",
    "take|office": "social", "call|election": "social",
    # --- eventive (stative) ---
    "take|place": "stative",
    # --- cognition (make/take/reach a decision; draw a conclusion) ---
    "make|sense": "cognition", "make|decision": "cognition", "take|decision": "cognition",
    "reach|decision": "cognition", "reach|conclusion": "cognition", "draw|conclusion": "cognition",
    "make|mistake": "cognition", "reach|agreement": "cognition",
    # --- communication (give a speech; make a point; raise a question) ---
    "give|speech": "communication", "give|talk": "communication", "give|lecture": "communication",
    "make|point": "communication", "make|announcement": "communication",
    "make|statement": "communication", "make|remark": "communication",
    "raise|question": "communication", "raise|issue": "communication", "pose|question": "communication",
    # --- other lexicalised light-verb collocations ---
    "take|part": "social", "play|role": "stative", "play|part": "stative",
    "make|war": "competition", "wage|war": "competition", "make|peace": "social",
}

_ASSET_DIR = os.path.join(REPO, "data", "idiom_foundation_v1")
_ASSET_PATH = os.path.join(_ASSET_DIR, "idioms.json")
_CORPUS_DEFAULT = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

_CACHE: Optional[Dict[str, Dict[str, str]]] = None


# ===========================================================================
# RUNTIME (inference): a dict lookup, no LLM.
# ===========================================================================
def _load() -> Dict[str, Dict[str, str]]:
    """Load the committed asset once (cached). Missing/corrupt asset -> empty maps (idiom_sense
    then always returns None; the disambiguator degrades to pure composition)."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        with open(_ASSET_PATH, "r", encoding="ascii") as f:
            obj = json.load(f)
        _CACHE = {"phrasal": dict(obj.get("phrasal", {})), "vobj": dict(obj.get("vobj", {}))}
    except Exception:
        _CACHE = {"phrasal": {}, "vobj": {}}
    return _CACHE


def idiom_sense(verb_lemma: str, particle: Optional[str],
                dobj_head: Optional[str]) -> Optional[str]:
    """Stored-unit lookup: return the coarse frame (in COARSE_FRAMES) if (verb [+particle]
    [+object head]) is a stored non-compositional MWE, else None.

    Order: the phrasal (verb+particle) unit is the stronger stored cue and is checked first; the
    verb+object unit second. LITERAL cases (leave+room, leave+key) are simply absent -> None."""
    if not verb_lemma:
        return None
    data = _load()
    v = verb_lemma.strip().lower()
    if particle:
        fr = data["phrasal"].get(v + "|" + particle.strip().lower())
        if fr is not None:
            return fr
    if dobj_head:
        fr = data["vobj"].get(v + "|" + dobj_head.strip().lower())
        if fr is not None:
            return fr
    return None


# ===========================================================================
# OFFLINE BUILD (glass-box; not called at inference).
# ===========================================================================
def _lemma_sense_frame(lemma_name: str) -> Optional[str]:
    """Highest-count coarse frame for a multiword verb lemma (e.g. 'pass_away'), across its synsets.
    WordNet returns synsets frequency-ranked, so a strict '>' keeps the lowest-rank sense on a tie."""
    from nltk.corpus import wordnet as wn
    best_fr, best_c = None, -1
    for s in wn.synsets(lemma_name, "v"):
        fr = lexname_to_frame(s.lexname())
        if fr is None:
            continue
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == lemma_name)
        if best_fr is None or c > best_c:
            best_c, best_fr = c, fr
    return best_fr


def _verb_dominant_frame(lemma: str) -> Optional[str]:
    """The verb's dominant (most-frequent-sense) coarse frame, aggregated by lexname over its verb
    synsets with a rank-decayed floor (WordNet order = frequency proxy)."""
    from nltk.corpus import wordnet as wn
    counts: Dict[str, float] = defaultdict(float)
    for rank, s in enumerate(wn.synsets(lemma, "v")):
        fr = lexname_to_frame(s.lexname())
        if fr is None:
            continue
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == lemma.lower())
        counts[fr] += c + 1.0 / (rank + 1.0)
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def build_phrasal_from_wordnet() -> Dict[str, str]:
    """Source 1: WordNet two-token 'verb_particle' lemmas -> {'verb|particle': frame}."""
    from nltk.corpus import wordnet as wn
    names = set()
    for syn in wn.all_synsets("v"):
        for lm in syn.lemmas():
            nm = lm.name().lower()
            if nm.count("_") != 1:
                continue
            base, tail = nm.split("_")
            if tail in PARTICLES and base.isalpha():
                names.add(nm)
    out: Dict[str, str] = {}
    for nm in names:
        base, tail = nm.split("_")
        fr = _lemma_sense_frame(nm)
        if fr is not None:
            out[base + "|" + tail] = fr
    return out


def build_vobj_from_wordnet() -> Dict[str, str]:
    """Source 2a: WordNet two-token 'verb_noun' lemmas (tail is a noun, base is a verb) ->
    {'verb|objecthead': frame}."""
    from nltk.corpus import wordnet as wn
    names = set()
    for syn in wn.all_synsets("v"):
        for lm in syn.lemmas():
            nm = lm.name().lower()
            if nm.count("_") != 1:
                continue
            base, tail = nm.split("_")
            if tail in PARTICLES or not base.isalpha() or not tail.isalpha():
                continue
            # tail must be a noun and base a verb -> a genuine verb+object MWE (excludes verb_adverb
            # / verb_adjective lemmas like act_reflexively, fall_asleep).
            if wn.synsets(tail, "n") and wn.synsets(base, "v"):
                names.add(nm)
    out: Dict[str, str] = {}
    for nm in names:
        base, tail = nm.split("_")
        fr = _lemma_sense_frame(nm)
        if fr is not None:
            out[base + "|" + tail] = fr
    return out


def mine_pmi_pairs(corpus_path: str, max_sents: int, min_pair: int = 4,
                   min_pmi: float = 2.0, batch_size: int = 128) -> List[Tuple[str, str, int, float]]:
    """Source 2b (discovery): parse up to max_sents lines with spaCy, collect (verb_lemma,
    dobj_head) counts, return high-PMI pairs [(verb, obj, count, pmi)] sorted by PMI desc.

    Glass-box PMI = log( c(v,o) * N / (c(v) * c(o)) ). spaCy runs INLINE (en_core_web_sm)."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    pair: Counter = Counter()
    vc: Counter = Counter()
    oc: Counter = Counter()
    total = 0

    def _gen():
        with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
            n = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield line
                n += 1
                if n >= max_sents:
                    break

    for doc in nlp.pipe(_gen(), batch_size=batch_size):
        for tok in doc:
            if tok.pos_ != "VERB":
                continue
            v = tok.lemma_.lower()
            if not v.isalpha():
                continue
            for ch in tok.children:
                if ch.dep_ in ("dobj", "obj") and ch.pos_ in ("NOUN", "PROPN"):
                    o = ch.lemma_.lower()
                    if not o.isalpha():
                        continue
                    pair[(v, o)] += 1
                    vc[v] += 1
                    oc[o] += 1
                    total += 1
    rows: List[Tuple[str, str, int, float]] = []
    if total == 0:
        return rows
    for (v, o), c in pair.items():
        if c < min_pair:
            continue
        pmi = math.log((c * total) / (vc[v] * oc[o]))
        if pmi >= min_pmi:
            rows.append((v, o, c, pmi))
    rows.sort(key=lambda r: -r[3])
    return rows


def _pmi_noncompositional_frame(v: str, o: str) -> Tuple[Optional[str], Optional[str]]:
    """Gate a mined (verb, object) pair. Returns (frame, reason) if non-compositional, else (None,
    None). (i) a dedicated WordNet verb_noun sense whose frame differs from the verb's dominant
    frame; (ii) an institutional object for a bleached light/motion/contact verb."""
    from nltk.corpus import wordnet as wn
    dom = _verb_dominant_frame(v)
    lemma = v + "_" + o
    if wn.synsets(lemma, "v"):
        fr = _lemma_sense_frame(lemma)
        if fr is not None and fr != dom:
            return fr, "wn_sense"
    if v in LIGHT_MOTION_CONTACT and o in INSTITUTIONAL_OBJ2FRAME:
        fr = INSTITUTIONAL_OBJ2FRAME[o]
        if fr != dom:
            return fr, "institutional"
    return None, None


def _atomic_write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    data = json.dumps(obj, ensure_ascii=True, indent=1, sort_keys=True)
    with open(tmp, "w", encoding="ascii", newline="") as f:
        f.write(data)
    os.replace(tmp, path)


def build_asset(corpus_path: Optional[str] = None, max_sents: int = 80000,
                out_path: Optional[str] = None, verbose: bool = True) -> Dict:
    """Build the full asset offline and write it atomically. Returns a stats dict.
    Guards a missing corpus: WordNet + curated asset still builds (2b skipped)."""
    corpus_path = corpus_path or _CORPUS_DEFAULT
    out_path = out_path or _ASSET_PATH

    phrasal = build_phrasal_from_wordnet()
    vobj = build_vobj_from_wordnet()
    n_wn_vobj = len(vobj)

    pmi_added = 0
    pmi_by_reason: Counter = Counter()
    pmi_rows_kept: List[Tuple[str, str, int, float, str]] = []
    corpus_used = False
    if os.path.exists(corpus_path):
        corpus_used = True
        if verbose:
            print(f"[build] PMI-mining up to {max_sents} lines of {os.path.basename(corpus_path)} ...")
        rows = mine_pmi_pairs(corpus_path, max_sents=max_sents)
        if verbose:
            print(f"[build] {len(rows)} high-PMI (verb,dobj) candidate pairs; gating for non-compositionality ...")
        for v, o, c, pmi in rows:
            key = v + "|" + o
            if key in vobj or key in CURATED_VOBJ:
                continue  # WordNet-2a and curated take precedence; don't double-count
            fr, reason = _pmi_noncompositional_frame(v, o)
            if fr is not None:
                vobj[key] = fr
                pmi_added += 1
                pmi_by_reason[reason] += 1
                pmi_rows_kept.append((v, o, c, pmi, reason + ":" + fr))
    elif verbose:
        print(f"[build] corpus MISSING ({corpus_path}) -- WordNet+curated asset only (2b skipped).")

    # curated overrides EVERYTHING (authoritative).
    vobj.update(CURATED_VOBJ)

    # validate every stored frame is a legal coarse frame.
    for m, name in ((phrasal, "phrasal"), (vobj, "vobj")):
        for k, fr in m.items():
            if fr not in _FRAMESET:
                raise ValueError("non-coarse frame %r for %s key %r" % (fr, name, k))

    asset = {
        "meta": {
            "source": "wordnet_phrasal+wordnet_vobj+pmi_mined+curated",
            "corpus": os.path.basename(corpus_path) if corpus_used else None,
            "corpus_used": corpus_used,
            "max_sents": max_sents if corpus_used else 0,
            "n_phrasal": len(phrasal),
            "n_vobj": len(vobj),
            "n_vobj_wordnet": n_wn_vobj,
            "n_vobj_pmi_added": pmi_added,
            "n_vobj_curated": len(CURATED_VOBJ),
            "pmi_by_reason": dict(pmi_by_reason),
        },
        "phrasal": phrasal,
        "vobj": vobj,
    }
    _atomic_write_json(out_path, asset)
    # drop the runtime cache so a subsequent idiom_sense() reads the fresh asset.
    global _CACHE
    _CACHE = None
    if verbose:
        print(f"[build] wrote {out_path}")
        print(f"[build] phrasal={len(phrasal)}  vobj={len(vobj)} "
              f"(wordnet={n_wn_vobj}, pmi_added={pmi_added} {dict(pmi_by_reason)}, "
              f"curated={len(CURATED_VOBJ)})")
    asset["_pmi_rows_kept"] = pmi_rows_kept
    return asset


# ---------------------------------------------------------------------------
def _self_test(rebuild: bool = True) -> bool:
    if rebuild or not os.path.exists(_ASSET_PATH):
        stats = build_asset()
    else:
        stats = {"meta": _load_meta()}
    global _CACHE
    _CACHE = None
    data = _load()

    checks = [
        ("pass|away -> {change,stative,body}", idiom_sense("pass", "away", None) in {"change", "stative", "body"}),
        ("go|off is not None",                 idiom_sense("go", "off", None) is not None),
        ("make+sense == cognition/communication", idiom_sense("make", None, "sense") in {"cognition", "communication"}),
        ("pass+law -> {social,communication}", idiom_sense("pass", None, "law") in {"social", "communication"}),
        ("take+place -> {stative,social}",     idiom_sense("take", None, "place") in {"stative", "social"}),
        ("leave+room is None",                 idiom_sense("leave", None, "room") is None),
        ("leave+key is None",                  idiom_sense("leave", None, "key") is None),
    ]
    npass = 0
    print("\nSELF-TEST idiom_gate:")
    for name, ok in checks:
        npass += int(bool(ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  -> got "
              f"{_probe(name)}")

    # report: counts + example entries
    ph, vo = data["phrasal"], data["vobj"]
    print(f"\n  phrasal entries: {len(ph)}")
    print(f"  vobj entries:    {len(vo)}")
    print("\n  ~15 example entries (key -> frame):")
    examples = ["pass|away", "go|off", "give|up", "take|off", "break|down", "come|across",
                "make|out", "leave|off", "pass|out", "run|away"]
    for k in examples:
        if k in ph:
            print(f"    phrasal  {k:16s} -> {ph[k]}")
    for k in ["make|sense", "take|place", "pass|law", "hold|meeting", "make|decision",
              "give|speech", "raise|question", "take|part", "wage|war", "make|love"]:
        if k in vo:
            print(f"    vobj     {k:16s} -> {vo[k]}")

    print(f"\nSELF-TEST idiom_gate: {npass}/{len(checks)} checks correct")
    return npass == len(checks)


def _probe(name: str):
    m = {
        "pass|away -> {change,stative,body}": idiom_sense("pass", "away", None),
        "go|off is not None": idiom_sense("go", "off", None),
        "make+sense == cognition/communication": idiom_sense("make", None, "sense"),
        "pass+law -> {social,communication}": idiom_sense("pass", None, "law"),
        "take+place -> {stative,social}": idiom_sense("take", None, "place"),
        "leave+room is None": idiom_sense("leave", None, "room"),
        "leave+key is None": idiom_sense("leave", None, "key"),
    }
    return m.get(name)


def _load_meta():
    try:
        with open(_ASSET_PATH, "r", encoding="ascii") as f:
            return json.load(f).get("meta", {})
    except Exception:
        return {}


if __name__ == "__main__":
    args = set(sys.argv[1:])
    if "--build" in args:
        build_asset()
    elif "--self-test" in args:
        ok = _self_test(rebuild=("--no-rebuild" not in args))
        sys.exit(0 if ok else 1)
    else:
        print("usage: python -m experiments.idiom_gate [--build | --self-test [--no-rebuild]]")
