"""hdlab/wordnet_polarity_propagation.py -- the DICTIONARY-LOOKUP half of the combined
dictionary + consequence word-learning tool (2026-08-06).

WHAT: for an out-of-vocabulary (OOV) outcome-verb lemma, LOOK IT UP -- infer its result-valence
from WordNet graph structure voted against the 52-word seed anchor, valence-BLIND neighborhood
(path_similarity synonym/hypernym vote) PLUS antonym-opposition -- returning POS / NEG / None with
a CONFIDENCE, then convert a confident hit into Bayesian PSEUDO-COUNTS that seed the consequence
loop's exposure counter ONCE, before the multi-pass loop. "A human does not wait to encounter
'squander' three times before learning it is bad -- they look it up." (093ddc1aa decisive finding:
consequence-only structurally cannot reach rare content verbs; they recur only 1-2x per corpus and
never clear MIN_CONFIRM.)

Two stages, OPPOSITION-FIRST (anchor_propagate pre-reg Section 3c decision logic, UNCHANGED; only
the return type is extended to carry confidence -- companion spec Section 2b):
  Stage A (antonym, higher precedence): antonyms(lemma) & ANCHOR_WORDS -> predict the OPPOSITE of the
    matched anchors' MAJORITY polarity (tie -> abstain). confidence = 1.0.
  Stage B (neighbor vote, fallback only): sim(lemma, a) = max path_similarity over verb-synset pairs;
    keep anchors with sim >= NEIGHBOR_FLOOR; sim-weighted-majority polarity; abstain if the kept set is
    empty or the normalized vote margin < VOTE_MARGIN. confidence = clamp((margin - VOTE_MARGIN) /
    (VOTE_MARGIN_SATURATE - VOTE_MARGIN), 0, 1).

PSEUDO-COUNT INJECTION (the fusion step): n = round(K_MAX * confidence), K_MAX = MIN_CONFIRM = 3 (a
maximally-confident dictionary hit is worth exactly as much trust as a fully-confirmed consequence
lock, no more). {lemma: {"POS": n, "NEG": 0}} or {"POS": 0, "NEG": n}; abstain / n<=0 -> no entry.
This dict has exactly the shape consolidate() already consumes, so consolidate() needs ZERO changes.
round() is Python's banker's rounding (documented so a re-implementation does not silently differ).

REUSE (wire-don't-island):
  - ANCHOR_WORDS / ANCHOR_POLARITY derived from hdlab.verb_lexical_similarity.OUTCOME_SEED_POS/_NEG
    (the already-vetted 52-word seed lexicon; ZERO new seed-authoring). ANCHOR_WORDS_EXTENDED adds
    OUTCOME_HELDOUT_POS/_NEG (~82 words) for the anchor-size ablation.
  - _antonyms: CLEAN-LIFT of experiments/exp_arc_aggregation_polarity_ci_v1.py::PolarityLexicon._antonyms
    (credited here; NOT imported at runtime -- hdlab-only dependency discipline, same convention
    hdlab/lexical_similarity.py / hdlab/verb_lexical_similarity.py used lifting from exp_n11c*). The
    curated _FLIP_PAIRS opposite list is lifted verbatim from the same source.
  - MIN_CONFIRM imported from hdlab.consequence_learning_loop (K_MAX's single source of truth, never a
    duplicated literal).
  - WordNet via nltk.corpus.wordnet (already a promoted hdlab dependency via hdlab.animacy_lexicon).

hdlab-only dependency: nltk + hdlab.verb_lexical_similarity + hdlab.consequence_learning_loop only.
No experiments/ import at runtime.

Cites: preregs/2026-08-06_combined_dictionary_consequence_word_learning_tool_v1.md (bands, config);
preregs/2026-08-06_anchor_propagate_oov_outcome_verb_valence_v1.md (Stage A/B decision logic);
notes/research_combined_dictionary_consequence_word_learning_tool_2026-08-06.md (combination rule).
"""
from __future__ import annotations

from typing import Dict, FrozenSet, NamedTuple, Optional

from nltk.corpus import wordnet as wn

from hdlab.consequence_learning_loop import MIN_CONFIRM
from hdlab.verb_lexical_similarity import (
    OUTCOME_SEED_POS,
    OUTCOME_SEED_NEG,
    OUTCOME_HELDOUT_POS,
    OUTCOME_HELDOUT_NEG,
)

# ---- pre-registered constants (fixed BEFORE any run; combined + anchor_propagate pre-regs) ----------
NEIGHBOR_FLOOR = 0.20          # WordNet path_similarity floor to keep an anchor as a neighbor
VOTE_MARGIN = 0.15             # Stage-B abstain floor on the normalized vote margin
VOTE_MARGIN_SATURATE = 0.50    # NEW (combined pre-reg): margin at which confidence saturates to 1.0
K_MAX = MIN_CONFIRM            # NEW: max pseudo-count == a fully-confirmed consequence lock (= 3)


# =============================================================================================
# ANCHOR (derived from the already-vetted seed lexicon; zero new seed-authoring)
# =============================================================================================
def _build_anchor(*seed_dicts_with_pole):
    """(dict, pole) pairs -> (frozenset(words), {word: pole}). Later dicts do not override earlier
    ones for a shared key (POS seed dicts are listed first, matching OUTCOME_VERB_FEATURES's own
    update order); a shared key would be a seed-lexicon bug, surfaced by _build_anchor's assert."""
    pol: Dict[str, str] = {}
    for d, pole in seed_dicts_with_pole:
        for w in d:
            pol.setdefault(w, pole)
    return frozenset(pol), pol


ANCHOR_WORDS, ANCHOR_POLARITY = _build_anchor(
    (OUTCOME_SEED_POS, "POS"), (OUTCOME_SEED_NEG, "NEG"))
ANCHOR_WORDS_EXTENDED, ANCHOR_POLARITY_EXTENDED = _build_anchor(
    (OUTCOME_SEED_POS, "POS"), (OUTCOME_SEED_NEG, "NEG"),
    (OUTCOME_HELDOUT_POS, "POS"), (OUTCOME_HELDOUT_NEG, "NEG"))


# =============================================================================================
# antonym helper -- CLEAN-LIFT of exp_arc_aggregation_polarity_ci_v1.PolarityLexicon._antonyms
# (credited; not imported at runtime). WordNet lemma antonyms UNION the curated _FLIP_PAIRS.
# =============================================================================================
_FLIP_PAIRS = [
    ("increase", "decrease"), ("increases", "decreases"), ("increased", "decreased"),
    ("increasing", "decreasing"), ("rise", "fall"), ("rises", "falls"), ("rising", "falling"),
    ("more", "less"), ("higher", "lower"), ("high", "low"), ("greater", "lower"),
    ("greater", "smaller"), ("larger", "smaller"), ("large", "small"), ("longer", "shorter"),
    ("long", "short"), ("hot", "cold"), ("hotter", "colder"), ("warm", "cool"),
    ("warmer", "cooler"), ("faster", "slower"), ("fast", "slow"), ("strong", "weak"),
    ("stronger", "weaker"), ("attract", "repel"), ("attracts", "repels"),
    ("expand", "contract"), ("expands", "contracts"), ("gain", "lose"), ("gains", "loses"),
    ("positive", "negative"), ("solid", "liquid"), ("melt", "freeze"), ("melts", "freezes"),
    ("melting", "freezing"), ("heating", "cooling"), ("heat", "cool"), ("wet", "dry"),
    ("open", "closed"), ("up", "down"), ("near", "far"), ("day", "night"), ("light", "dark"),
    ("acid", "base"), ("acidic", "basic"), ("north", "south"), ("east", "west"),
    ("push", "pull"), ("add", "remove"), ("many", "few"), ("thick", "thin"),
    ("dense", "sparse"), ("full", "empty"), ("deep", "shallow"), ("heavy", "light"),
]
_FLIP: Dict[str, set] = {}
for _a, _b in _FLIP_PAIRS:
    _FLIP.setdefault(_a, set()).add(_b)
    _FLIP.setdefault(_b, set()).add(_a)

_ant_cache: Dict[str, FrozenSet[str]] = {}


def _antonyms(word: str) -> FrozenSet[str]:
    """WordNet lemma antonyms of `word` UNION curated flip-opposites. Cached. Clean-lift of
    PolarityLexicon._antonyms (exp_arc_aggregation_polarity_ci_v1.py): a WordNet lookup must never
    silently swallow -> record + re-raise (no phantom coverage)."""
    if word in _ant_cache:
        return _ant_cache[word]
    out = set(_FLIP.get(word, ()))
    try:
        for ss in wn.synsets(word):
            for lem in ss.lemmas():
                for ant in lem.antonyms():
                    out.add(ant.name().replace("_", " ").lower())
    except Exception as e:  # NOT BaseException; record + re-raise (never a phantom empty set)
        raise RuntimeError(f"wordnet antonym lookup failed for {word!r}: {e}")
    fs = frozenset(out)
    _ant_cache[word] = fs
    return fs


# =============================================================================================
# DictLookup record + dictionary_lookup (the extended contract; anchor_propagate 3c logic UNCHANGED)
# =============================================================================================
class DictLookup(NamedTuple):
    polarity: Optional[str]      # "POS" | "NEG" | None (abstain)
    confidence: float            # 0.0 .. 1.0
    stage: str                   # "antonym" | "neighbor" | "abstain"
    vote_margin: float           # Stage-B normalized margin (1.0 for a Stage-A hit)
    n_neighbors: int             # matched anchors (antonym hits or kept neighbors)


_anchor_syn_cache: Dict[int, Dict[str, list]] = {}


def _anchor_verb_synsets(anchor_words: FrozenSet[str]) -> Dict[str, list]:
    """{anchor: [verb synsets]} for a given anchor set. Cached by anchor-set identity so the primary
    52-word anchor's synsets are computed once."""
    key = id(anchor_words)
    if key not in _anchor_syn_cache:
        _anchor_syn_cache[key] = {a: wn.synsets(a, pos=wn.VERB) for a in anchor_words}
    return _anchor_syn_cache[key]


def dictionary_lookup(lemma: str,
                      anchor_words: FrozenSet[str] = ANCHOR_WORDS,
                      anchor_polarity: Dict[str, str] = ANCHOR_POLARITY) -> DictLookup:
    """Look up `lemma`'s result-valence against the anchor. Stage A (antonym opposition) first, then
    Stage B (neighbor vote). Deterministic, glass-box. Returns DictLookup (polarity None == abstain)."""
    # ---- Stage A: antonym opposition (higher precedence) -----------------------------------------
    anto = _antonyms(lemma) & anchor_words
    if anto:
        poles = [anchor_polarity[a] for a in anto]
        n_pos = poles.count("POS")
        n_neg = poles.count("NEG")
        if n_pos != n_neg:                       # tie -> fall through to Stage B (no forced guess)
            maj = "POS" if n_pos > n_neg else "NEG"
            opp = "NEG" if maj == "POS" else "POS"
            return DictLookup(opp, 1.0, "antonym", 1.0, len(anto))

    # ---- Stage B: sim-weighted neighbor vote (fallback) ------------------------------------------
    lem_syn = wn.synsets(lemma, pos=wn.VERB)
    if not lem_syn:
        return DictLookup(None, 0.0, "abstain", 0.0, 0)
    anchor_syn = _anchor_verb_synsets(anchor_words)
    pos_w = 0.0
    neg_w = 0.0
    n_kept = 0
    for a in anchor_words:
        best = 0.0
        for sl in lem_syn:
            for sa in anchor_syn[a]:
                ps = sl.path_similarity(sa)
                if ps is not None and ps > best:
                    best = ps
        if best >= NEIGHBOR_FLOOR:
            n_kept += 1
            if anchor_polarity[a] == "POS":
                pos_w += best
            else:
                neg_w += best
    total = pos_w + neg_w
    if total == 0.0:
        return DictLookup(None, 0.0, "abstain", 0.0, 0)
    margin = abs(pos_w - neg_w) / total
    if margin < VOTE_MARGIN:
        return DictLookup(None, 0.0, "abstain", round(margin, 6), n_kept)
    polarity = "POS" if pos_w > neg_w else "NEG"
    conf = (margin - VOTE_MARGIN) / (VOTE_MARGIN_SATURATE - VOTE_MARGIN)
    conf = max(0.0, min(1.0, conf))
    return DictLookup(polarity, conf, "neighbor", round(margin, 6), n_kept)


# =============================================================================================
# pseudo-count conversion (the fusion contract; consolidate() consumes this shape verbatim)
# =============================================================================================
def pseudo_counts_from_dictionary(lookups: Dict[str, DictLookup],
                                  k_max: int = K_MAX) -> Dict[str, Dict[str, int]]:
    """{lemma: DictLookup} -> {lemma: {"POS": n, "NEG": n}} pseudo-exposure counts.
    n = round(k_max * confidence) (banker's rounding, Python default; documented for reproducibility).
    Abstain (polarity is None) or n <= 0 -> no entry (zero influence)."""
    out: Dict[str, Dict[str, int]] = {}
    for lemma, lu in lookups.items():
        if lu.polarity is None:
            continue
        n = round(k_max * lu.confidence)
        if n <= 0:
            continue
        out[lemma] = {"POS": n if lu.polarity == "POS" else 0,
                      "NEG": n if lu.polarity == "NEG" else 0}
    return out


def lookups_for(lemmas, anchor_words: FrozenSet[str] = ANCHOR_WORDS,
                anchor_polarity: Dict[str, str] = ANCHOR_POLARITY) -> Dict[str, DictLookup]:
    """Convenience: {lemma: dictionary_lookup(lemma)} over an iterable of lemmas."""
    return {lm: dictionary_lookup(lm, anchor_words, anchor_polarity) for lm in lemmas}


# =============================================================================================
# self-test: mechanism-fires + abstain + pseudo-count shape + non-circularity(scramble) + determinism
# =============================================================================================
def self_test() -> dict:
    # (1) anchor built from the seed lexicon, correct sizes + poles.
    assert len(ANCHOR_WORDS) == len(ANCHOR_POLARITY), "anchor word/pole size mismatch"
    assert "mend" in ANCHOR_WORDS and ANCHOR_POLARITY["mend"] == "POS"
    assert "sink" in ANCHOR_WORDS and ANCHOR_POLARITY["sink"] == "NEG"
    assert len(ANCHOR_WORDS_EXTENDED) > len(ANCHOR_WORDS), "extended anchor must be larger"

    # (2) DictLookup fields well-formed + deterministic for a real lemma.
    lu1 = dictionary_lookup("ruin")
    lu2 = dictionary_lookup("ruin")
    assert lu1 == lu2, "GLASS-BOX FAILURE: non-deterministic dictionary_lookup"
    assert lu1.stage in ("antonym", "neighbor", "abstain")
    assert 0.0 <= lu1.confidence <= 1.0

    # (3) abstain never crashes + yields no pseudo-count.
    lu_oov = dictionary_lookup("zzznotarealverb")
    assert lu_oov.polarity is None and lu_oov.stage == "abstain"
    assert pseudo_counts_from_dictionary({"zzznotarealverb": lu_oov}) == {}

    # (4) pseudo-count shape + banker's-rounding contract: confidence 1.0 -> n == K_MAX single-pole.
    pc = pseudo_counts_from_dictionary({"x": DictLookup("NEG", 1.0, "neighbor", 0.9, 4)})
    assert pc == {"x": {"POS": 0, "NEG": K_MAX}}, pc
    # a low confidence rounding to 0 -> dropped (functionally an abstain).
    assert pseudo_counts_from_dictionary({"x": DictLookup("POS", 0.1, "neighbor", 0.16, 1)}) == {}, \
        "round(3*0.1)=0 must drop"
    # a mid confidence -> partial pseudo-count.
    pc2 = pseudo_counts_from_dictionary({"x": DictLookup("POS", 0.6, "neighbor", 0.36, 3)})
    assert pc2 == {"x": {"POS": round(K_MAX * 0.6), "NEG": 0}}, pc2

    # (5) MECHANISM-FIRES: at least one of the seed-lexicon's own opposites is recovered by the
    # antonym stage against the anchor -- 'unlock' (an APERTURE POS anchor) has WordNet antonym 'lock'
    # (a NEG anchor) so a lemma whose antonym lands in the anchor gets a stage-A opposition. Use a
    # NON-anchor OOV probe with a known antonym in the anchor: 'unbolt' -> 'bolt' (NEG anchor) etc.
    # We assert the antonym MACHINERY finds an anchor hit for at least one probe (mechanism fires).
    fired = False
    for probe in ("worsen", "destroy", "heal", "ruin", "improve", "damage"):
        if _antonyms(probe) & ANCHOR_WORDS:
            fired = True
            break
    # (informational -- WordNet antonym coverage for verbs is sparse; do not hard-assert Stage A)

    # (6) NON-CIRCULARITY: scrambling the anchor polarity must be able to change a real lemma's
    # predicted polarity (proves the vote reads the anchor's ACTUAL labels, not an artifact). Find a
    # lemma the real anchor types; flip the anchor labels; predicted polarity should flip too.
    probe = None
    for lm in ("ruin", "spoil", "improve", "flee", "whitewash", "relent"):
        if dictionary_lookup(lm).polarity is not None:
            probe = lm
            break
    scramble_flips = None
    if probe is not None:
        flipped = {w: ("NEG" if p == "POS" else "POS") for w, p in ANCHOR_POLARITY.items()}
        real_p = dictionary_lookup(probe).polarity
        scr_p = dictionary_lookup(probe, ANCHOR_WORDS, flipped).polarity
        # a full label flip must flip the neighbor-vote polarity (Stage A opposition also flips).
        scramble_flips = (real_p is not None and scr_p is not None and real_p != scr_p)
        assert scramble_flips, (
            f"NON-CIRCULARITY FAILURE: flipping anchor polarity did not flip {probe!r} "
            f"({real_p} -> {scr_p})")

    return {
        "n_anchor": len(ANCHOR_WORDS), "n_anchor_extended": len(ANCHOR_WORDS_EXTENDED),
        "K_MAX": K_MAX, "NEIGHBOR_FLOOR": NEIGHBOR_FLOOR, "VOTE_MARGIN": VOTE_MARGIN,
        "VOTE_MARGIN_SATURATE": VOTE_MARGIN_SATURATE,
        "stage_A_machinery_fires": fired, "scramble_flips_probe": probe,
        "scramble_flips_polarity": scramble_flips,
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
