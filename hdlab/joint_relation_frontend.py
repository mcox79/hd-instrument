"""JOINT glass-box relation front-end: parse each sentence ONCE (hdlab.pos_tagger + hdlab.arc_parser) and read
ALL relation channels off the SAME dependency structure -- the brain-foundational property (PROBLEM sec.3, PINNED):
the brain extracts a clause's relations JOINTLY in one structural pass; it does NOT run N independent per-relation
classifiers. The incumbent substrate does the opposite -- three SEPARATE front-ends, two of which throw the parse
away (spatial_relation_extractor loads the parser then does a linear nearest-noun scan; _temporal_ordering uses a
separate NLTK tagger and tense-gates events) -- so within-clause edges fail INDEPENDENTLY and multi-hop chains die
at the exponent rate (edge_recall ^ chain_len).

This module parses once and exposes per channel:
  parse_sentence(words)            -> (upos, heads)          ONE parse, cached per word-tuple
  joint_event_ranks(words, ...)    -> {rank: provenance}     TENSE-AGNOSTIC events + the DROPPED copular/stative
                                                             channel (be + ADJ/NOUN predicate = a STATE event),
                                                             read off the parse (copula attaches to its predicate)
  joint_spatial_edges(words)       -> [(fig, rel, gnd, ...)] figure/ground bound by the PARSE (the prep's object is
                                                             the ground; the prep's HEAD is the figure) not by
                                                             linear nearest-noun

Brain grounding: Reichenbach/Bach neo-Davidsonian event variable (a STATE is an event the brain represents, not a
tense pattern); Talmy/Jackendoff Figure-Ground bound at the syntax-semantics interface (left IFG structure-building
-> pMTG/ATL role binding, Friederici 2017; Frankland & Greene 2015). The tense-gate and the linear nearest-noun
attachment are OUR-INVENTION implementation artifacts of the incumbent, NOT the brain's mechanism. ASCII, NO LLM.

PROMOTED (owner-DONE extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck, Q111
strategy landing 2026-09-07) VERBATIM from experiments/_joint_relation_frontend.py -- the detection core is
byte-identical (parse_sentence / joint_event_ranks / joint_spatial_edges / joint_spatial_frames). The ONLY
deltas vs the solver cell: (1) the experiments/_hashseed_guard import is DROPPED -- an hdlab organ must NOT
os.execv on import; the PYTHONHASHSEED=0 determinism pin lives in the WITNESSES + board arm (which run as
standalone scripts and import it FIRST), and the LIVE reader's lazy temporal reasoner tolerates the ~+-5-chain
hash-seed drift (a new-island read-time capability, not a stored asset). (2) this docstring note. stdlib + hdlab
(pos_tagger / arc_parser) + optional nltk.wordnet ONLY -- NO experiments import, NO external LLM (the invariant).
The joint TEMPORAL REASONER wire (feeding this event set to hdlab.temporal_reasoner) lives in
hdlab.situation_reader._build_joint_temporal_reasoner, which already imports the shared temporal front-end.
"""
from __future__ import annotations
import os
import sys
from typing import Dict, List, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser

_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_cache = {}
_parse_cache = {}

_BE = {"be", "is", "am", "are", "was", "were", "been", "being", "'s", "'re", "'m"}
_AUX_LEMMAS = {"be", "is", "am", "are", "was", "were", "been", "being", "have", "has", "had",
               "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may",
               "might", "must", "'s", "'re", "'m", "'ve", "'ll", "'d", "get", "got"}
# EVENTIVE-NOMINAL detection. Brain-foundational (lexical-semantic event knowledge): a nominalization denotes the
# EVENT of its source verb (Grimshaw 1990 argument-structure nominals; the ATL codes it as an event frame). We test
# this in WordNet, glass-box: a noun is eventive iff it has an ACT/EVENT/PROCESS sense AND is DEVERBAL (linked to a
# verb) -- so 'construction/arrival/attack' fire and 'nation/station/region/nurse' do not. The old suffix rule
# (_EVENT_NOUN_SUFFIX) is kept only for the ablation.
_EVENT_NOUN_SUFFIX = ("tion", "sion", "ment", "ance", "ence", "ancy", "ency", "al", "ure", "age", "ing")
_EVENT_LEXNAMES = {"noun.act", "noun.event", "noun.process", "noun.phenomenon"}
_wn_event_cache = {}


def _is_event_noun(word, wordnet_gated=True):
    """True iff `word` is an eventive nominal. wordnet_gated=True: an ACT/EVENT/PROCESS sense (top-3) AND a
    derivationally-related VERB (deverbal). wordnet_gated=False: the old suffix heuristic (ablation)."""
    w = word.lower()
    if not wordnet_gated:
        return len(w) >= 5 and w.endswith(_EVENT_NOUN_SUFFIX)
    if w in _wn_event_cache:
        return _wn_event_cache[w]
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        _wn_event_cache[w] = False
        return False
    syns = wn.synsets(w, pos="n")[:3]
    res = False
    if syns and any(s.lexname() in _EVENT_LEXNAMES for s in syns):
        for s in syns:
            for l in s.lemmas():
                if any(d.synset().pos() == "v" for d in l.derivationally_related_forms()):
                    res = True
                    break
            if res:
                break
    _wn_event_cache[w] = res
    return res

_PUNCT = set(".,;:!?()\"'`")
_LOC_PREPS = {"in": "in", "inside": "in", "within": "in", "into": "in",
              "on": "on", "at": "at",
              "above": "above", "over": "above", "below": "below", "under": "below",
              "underneath": "below", "beneath": "below", "behind": "behind",
              "near": "near", "beside": "near", "by": "near"}
_CONTAIN_RELS = {"in"}


def _frontend():
    if "t" not in _cache:
        _cache["t"] = PosTagger.load(_POS)
        _cache["p"] = ArcParser.load(_ARC)
    return _cache["t"], _cache["p"]


def parse_sentence(words: Sequence[str]) -> Tuple[List[str], Dict[int, int]]:
    """Parse a word list ONCE -> (upos list, heads dict {dep1based: head1based, head 0 = ROOT}). Cached."""
    key = tuple(words)
    if key in _parse_cache:
        return _parse_cache[key]
    t, p = _frontend()
    if not words or len(words) > 160:
        res = ([t.tag(list(words))[i] if words else "X" for i in range(len(words))], {})
        _parse_cache[key] = res
        return res
    upos = t.tag(list(words))
    # P4 (extract_spatial_and_causal owner-DONE, §7 diff 2): route the shared relation-front-end parse through the
    # exact-MAP graded decode (Chu-Liu/Edmonds MAP over the SAME globally-normalized arc-factored scorer) instead of
    # the greedy decode that yields an invalid non-tree parse on ~7.2% of sentences. More brain-foundational (the
    # exact global MAP the greedy approximates); the temporal event set is byte-identical (verified no-regress).
    pr = p.parse(list(words), list(upos), decode="exact")
    heads = dict(pr.heads)  # dep(1based) -> head(1based)
    _parse_cache[key] = (upos, heads)
    return upos, heads


def _is_word(tok: str) -> bool:
    return tok not in _PUNCT


def joint_event_ranks(words: Sequence[str], upos=None, heads=None,
                      copular=True, nominal=False, nominal_wordnet=True) -> Dict[int, str]:
    """TENSE-AGNOSTIC event detection off ONE parse. Returns {word_index0: provenance-tag}.
    Channels:
      VERB    -- any UPOS==VERB token (present/progressive/infinitive/past alike; excludes AUX copulas)
      COP     -- copular/stative: an AUX 'be' whose PARSE HEAD is an ADJ/NOUN/PROPN predicate -> that predicate is
                 a STATE event (the DROPPED channel; the copula binds a nonverbal state predicate)
      NOM     -- (optional) a deverbal-nominalization NOUN (suffix-gated, stoplisted) = an eventive nominal
    'words' is punct-free word indices when called from the temporal harness (so an index IS the word-rank)."""
    if upos is None or heads is None:
        upos, heads = parse_sentence(words)
    lows = [w.lower() for w in words]
    ev: Dict[int, str] = {}
    for i, (low, pos) in enumerate(zip(lows, upos)):
        if pos == "VERB" and low not in _AUX_LEMMAS:
            ev[i] = "VERB"
    if copular:
        for i, (low, pos) in enumerate(zip(lows, upos)):
            if low in _BE and pos in ("AUX", "VERB"):
                h = heads.get(i + 1, 0)  # 1-based head of the copula
                if h and 1 <= h <= len(words):
                    hp = upos[h - 1]
                    if hp in ("ADJ", "NOUN", "PROPN") and (h - 1) not in ev:
                        ev[h - 1] = "COP"
    if nominal:
        for i, (low, pos) in enumerate(zip(lows, upos)):
            if pos == "NOUN" and i not in ev and _is_event_noun(low, wordnet_gated=nominal_wordnet):
                ev[i] = "NOM"
    return ev


def _subtree_head_noun(words, upos, heads, idx1):
    """Return the surface span (compound noun run) whose head is the token at 1-based idx1, else the token."""
    # gather a small compound run: preceding ADJ/NOUN/PROPN modifiers of a NOUN/PROPN head
    i0 = idx1
    start = i0
    while start - 1 >= 1 and upos[start - 2] in ("ADJ", "NOUN", "PROPN"):
        start -= 1
    end = i0
    while end + 1 <= len(words) and upos[end] in ("NOUN", "PROPN"):
        end += 1
    return " ".join(words[start - 1:end])


def _subject_of(children, upos, verb1):
    """Nearest PRECEDING NOUN/PROPN child of the verb (nsubj-like); backstop = nearest preceding noun in the child
    set overall, else None."""
    subj = None
    for c in children.get(verb1, []):
        if c < verb1 and upos[c - 1] in ("NOUN", "PROPN"):
            subj = c  # take the last (closest) preceding nominal child
    return subj


def joint_spatial_edges(words: Sequence[str], upos=None, heads=None, of_containment=True):
    """Figure/Ground edges bound by the PARSE, following the parser's UD convention (verified on disk):
    a locative ADP (case) attaches to its OBJECT NOUN (the GROUND); the ground noun attaches to the FIGURE/anchor.
      ground = heads[prep]                       (the noun the preposition governs)
      anchor = heads[ground]
        anchor is NOUN/PROPN  -> figure = anchor            ('book in the box' -> box->book)
        anchor is VERB/AUX    -> figure = subject(anchor)   ('apple ... in the basket' -> basket->is->apple)
    'of' between two nouns is region-nesting -> containment ('town of Madrid' -> town in Madrid), place-gated.
    This is the attachment the incumbent's LINEAR nearest-noun scan gets wrong. Returns [(figure, rel, ground,
    prep_index0)]."""
    if upos is None or heads is None:
        upos, heads = parse_sentence(words)
    lows = [w.lower() for w in words]
    n = len(words)
    children = {}
    for dep in range(1, n + 1):
        h = heads.get(dep, 0)
        children.setdefault(h, []).append(dep)
    edges = []

    def _fig_from_ground(gnd1):
        anchor = heads.get(gnd1, 0)
        if not (1 <= anchor <= n):
            return None
        if upos[anchor - 1] in ("NOUN", "PROPN"):
            return anchor
        if upos[anchor - 1] in ("VERB", "AUX"):
            return _subject_of(children, upos, anchor)
        return None

    for i in range(n):
        low = lows[i]
        p1 = i + 1
        if low in _LOC_PREPS and upos[i] in ("ADP", "ADV"):
            rel = _LOC_PREPS[low]
            gnd1 = heads.get(p1, 0)
            if not (1 <= gnd1 <= n) or upos[gnd1 - 1] not in ("NOUN", "PROPN"):
                # backstop: nearest noun to the right (parse missed the case attachment)
                gnd1 = None
                for k in range(p1 + 1, min(p1 + 6, n + 1)):
                    if upos[k - 1] in ("NOUN", "PROPN"):
                        gnd1 = k
                        break
                    if words[k - 1] in (".", ";", "!", "?"):
                        break
            if not gnd1:
                continue
            fig1 = _fig_from_ground(gnd1)
            if fig1 and fig1 != gnd1:
                fig = _subtree_head_noun(words, upos, heads, fig1)
                gnd = _subtree_head_noun(words, upos, heads, gnd1)
                if fig and gnd and fig != gnd:
                    edges.append((fig, rel, gnd, i))
        elif of_containment and low == "of" and upos[i] == "ADP":
            # 'X of Y' region-nesting: ground = heads[of] (=Y), figure = heads[Y] if NOUN (=X). place-gated on Y.
            y1 = heads.get(p1, 0)
            if 1 <= y1 <= n and upos[y1 - 1] in ("NOUN", "PROPN"):
                x1 = heads.get(y1, 0)
                if 1 <= x1 <= n and upos[x1 - 1] in ("NOUN", "PROPN"):
                    if upos[y1 - 1] == "PROPN" or lows[y1 - 1] in _PLACEISH:
                        fig = _subtree_head_noun(words, upos, heads, x1)
                        gnd = _subtree_head_noun(words, upos, heads, y1)
                        if fig and gnd and fig != gnd:
                            edges.append((fig, "in", gnd, i))
    return edges


_POSSESS_CONTAIN = {"contain", "contains", "hold", "holds", "have", "has", "had", "enclose", "encloses",
                    "house", "houses"}
_LOCATIVE_VERB = {"located", "situated", "lies", "lie", "sits", "sit", "stands", "stand", "nestled",
                  "perched", "housed", "found", "set", "positioned", "placed", "rests", "rest"}


def joint_spatial_frames(words, upos=None, heads=None):
    """UNIFIED Figure-Ground frame binder (brain-foundational: Talmy/Jackendoff Place-function -- a spatial RELATOR
    evokes ONE Figure-Ground frame; the incumbent's N separate constructions are relator-specific role mappings of the
    SAME frame, NOT N independent rules). All roles bound by the PARSE:
      PREPOSITION  in/on/... : ground = heads[prep], figure = heads[ground]        (joint_spatial_edges)
      POSSESSION   'A contains/has X' : ground = subject(verb) [=container], figure = object(verb) [=contained]
      LOCATIVE-VB  'X is located in Y' : figure = subject(verb), ground = object of the following locative prep
    Returns [(figure, rel, ground, idx)] with rel='in' for containment frames (+ the projective prep edges)."""
    if upos is None or heads is None:
        upos, heads = parse_sentence(words)
    lows = [w.lower() for w in words]
    n = len(words)
    children = {}
    for dep in range(1, n + 1):
        children.setdefault(heads.get(dep, 0), []).append(dep)
    edges = list(joint_spatial_edges(words, upos, heads))  # prep + of frames

    def _obj_of(verb1):
        for c in children.get(verb1, []):
            if c > verb1 and upos[c - 1] in ("NOUN", "PROPN"):
                return c
        return None

    def _subj_of(verb1):
        cand = None
        for c in children.get(verb1, []):
            if c < verb1 and upos[c - 1] in ("NOUN", "PROPN"):
                cand = c
        return cand

    for i in range(n):
        low = lows[i]
        v1 = i + 1
        if low in _POSSESS_CONTAIN and upos[i] in ("VERB", "AUX"):
            cont = _subj_of(v1)      # container = subject
            obj = _obj_of(v1)        # contained = object
            if cont and obj and cont != obj:
                fig = _subtree_head_noun(words, upos, heads, obj)
                gnd = _subtree_head_noun(words, upos, heads, cont)
                if fig and gnd and fig != gnd:
                    edges.append((fig, "in", gnd, i))
        elif low in _LOCATIVE_VERB and upos[i] in ("VERB", "AUX", "ADJ"):
            subj = _subj_of(v1)
            gnd1 = None
            for k in range(v1 + 1, min(v1 + 6, n + 1)):
                if lows[k - 1] in _LOC_PREPS or lows[k - 1] in ("of",):
                    g = heads.get(k, 0)
                    if 1 <= g <= n and upos[g - 1] in ("NOUN", "PROPN"):
                        gnd1 = g
                    else:
                        for kk in range(k + 1, min(k + 4, n + 1)):
                            if upos[kk - 1] in ("NOUN", "PROPN"):
                                gnd1 = kk
                                break
                    break
            if subj and gnd1 and subj != gnd1:
                fig = _subtree_head_noun(words, upos, heads, subj)
                gnd = _subtree_head_noun(words, upos, heads, gnd1)
                if fig and gnd and fig != gnd:
                    edges.append((fig, "in", gnd, i))
    return edges


_PLACEISH = {"city", "town", "district", "quarter", "area", "region", "country", "street", "road", "square",
             "park", "temple", "museum", "palace", "garden", "river", "hall", "building", "house", "room",
             "station", "market", "center", "centre", "village", "island", "valley", "mountain", "hill", "lake",
             "sea", "bay", "harbor", "harbour", "corner", "edge", "side", "top", "bottom", "end", "heart",
             "middle", "north", "south", "east", "west", "part", "block", "box", "drawer", "table", "shelf",
             "cabinet", "container", "bag", "basket", "yard", "field", "floor", "wall", "roof"}


def clear_cache():
    _parse_cache.clear()


if __name__ == "__main__":
    for sent in ["she is a nurse who knew the answer and is helping now",
                 "the door was open",
                 "the cat that was hiding under the box slept on the mat",
                 "the book in the box on the shelf fell"]:
        ws = sent.split()
        up, hd = parse_sentence(ws)
        ev = joint_event_ranks(ws, up, hd, copular=True, nominal=True)
        sp = joint_spatial_edges(ws, up, hd)
        print("\n" + sent)
        print("  events:", {ws[i]: p for i, p in sorted(ev.items())})
        print("  spatial:", [(f, r, g) for (f, r, g, _) in sp])
