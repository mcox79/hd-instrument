"""affect_lexicon: the BRAIN-FOUNDATIONAL affect foundation for the character-emotion register.

THE BRAIN'S MODEL (PINNED -- research_affect_emotion_brain_mechanism_2026-09-04.md): emotion is
represented as CORE AFFECT (valence + arousal; Barrett constructed emotion; Russell circumplex;
Lindquist et al. 2012) then CONCEPTUALIZED into discrete categories. So VALENCE is primary and
CATEGORY secondary.

THE GATE (what counts as an emotion word) -- PINNED denotation-vs-association distinction
(research_emotion_term_denotation_and_experiencer_coref_2026-09-04.md): an emotion word DENOTES a
stage-level (Carlson 1977) affective STATE OF AN EXPERIENCER ("afraid", "joy", "delighted"), distinct
from (a) an evaluative property of an object ("excellent", "wonderful"), and (b) an emotion-ASSOCIATED
concept ("war", "death", "money", "friends"). The literature calls this emotion-LABEL vs emotion-LADEN
words (Pavlenko 2008; Altarriba & Bauer 2004), and it dissociates neurally (Zhang et al. 2017:
larger N170/LPC for label than laden words). A signal-loss study confirmed the NRC Emotion Lexicon is
an ASSOCIATION lexicon and over-fires on laden concepts, so we do NOT gate on it. We gate on a CURATED
emotion-DENOTING term inventory (a closed affective vocabulary; WordNet-Affect-style, organized by
family x POS), and take VALENCE from the Warriner et al. (2013) norms (an admissible offline asset).
Causative/stimulus forms ("frightening", "delightful") and pure evaluatives ("excellent") are EXCLUDED.

Glass-box, deterministic, NO LLM. ASCII.

LANDED into hdlab (Q111, the_situation_model_has_no_affect_emotion_dimension). Promoted VERBATIM from
experiments/affect_lexicon.py; the ONLY change is the asset path -- the Warriner CSV is read from the
SHIPPED frontend asset (data/frontend_assets/Ratings_Warriner_et_al.csv), mirroring the goal register's
verb_subcat_frames landing. stdlib only -- NO experiments/ dependency.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import csv
import re
from typing import Dict, Optional, Set

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# KB_REFERENT: data/frontend_assets/Ratings_Warriner_et_al.csv  (shipped Q111 frontend asset)
WARRINER = os.path.join(REPO, "data/frontend_assets/Ratings_Warriner_et_al.csv")

# ---------------------------------------------------------------------------
# THE CURATED EMOTION-DENOTING TERM INVENTORY (the gate). Family x POS, from the WordNet-Affect-grounded
# research inventory (CORE = denotes an experiencer's felt state). OUR-INVENTION-under-test as an
# inventory; the denotation principle + families are PINNED. Causative "-ing"/evaluative forms EXCLUDED.
# ---------------------------------------------------------------------------
_FAMILY_TERMS: Dict[str, str] = {}


def _fam(family: str, *terms: str):
    for t in terms:
        _FAMILY_TERMS[t] = family


_fam("fear", "afraid", "fearful", "scared", "frightened", "terrified", "petrified", "horrified",
     "anxious", "apprehensive", "nervous", "uneasy", "tense", "alarmed", "aghast", "spooked",
     "panicked", "fear", "fright", "terror", "dread", "horror", "panic", "alarm", "anxiety",
     "apprehension", "trepidation", "angst", "fearfulness")
_fam("anger", "angry", "mad", "furious", "irate", "enraged", "incensed", "livid", "indignant",
     "outraged", "annoyed", "irritated", "exasperated", "cross", "resentful", "vexed", "sullen",
     "wrathful", "anger", "rage", "fury", "wrath", "ire", "indignation", "outrage", "annoyance",
     "irritation", "exasperation", "resentment")
_fam("sadness", "sad", "unhappy", "miserable", "sorrowful", "mournful", "heartbroken", "downcast",
     "dejected", "despondent", "gloomy", "glum", "forlorn", "wretched", "melancholy", "woeful",
     "disconsolate", "crestfallen", "desolate", "despairing", "tearful", "sadness", "sorrow", "grief",
     "misery", "despair", "gloom", "dejection", "despondency", "woe", "heartache")
_fam("joy", "happy", "glad", "joyful", "joyous", "cheerful", "delighted", "elated", "ecstatic",
     "thrilled", "jubilant", "merry", "gleeful", "blissful", "content", "contented", "gratified",
     "pleased", "overjoyed", "radiant", "exultant", "relieved", "joy", "happiness", "delight",
     "elation", "glee", "cheer", "bliss", "jubilation", "ecstasy", "contentment", "gladness", "relief")
_fam("disgust", "disgusted", "revolted", "repulsed", "nauseated", "sickened", "disgust", "revulsion",
     "repugnance", "loathing", "distaste", "aversion")
_fam("surprise", "surprised", "astonished", "amazed", "astounded", "stunned", "shocked", "startled",
     "dumbfounded", "flabbergasted", "surprise", "astonishment", "amazement", "shock")
_fam("love", "loving", "affectionate", "fond", "devoted", "adoring", "smitten", "enamored", "love",
     "affection", "adoration", "fondness", "devotion", "infatuation", "tenderness")
_fam("shame", "ashamed", "guilty", "embarrassed", "humiliated", "mortified", "remorseful", "contrite",
     "shamefaced", "sheepish", "shame", "guilt", "embarrassment", "humiliation", "remorse",
     "contrition", "mortification")
_fam("pride", "proud", "triumphant", "pride", "triumph")
_fam("jealousy", "jealous", "envious", "jealousy", "envy")
_fam("longing", "lonely", "homesick", "loneliness", "homesickness", "longing", "forlorn")
_fam("calm", "calm", "relaxed", "serene", "bored", "serenity", "boredom", "composed")
_fam("hope", "hopeful", "eager", "hope", "eagerness")
# rounding out clear emotion nouns/adjectives (psych VERBS like hate/fear/love fire via the frame; their
# NOUN forms and a few common state terms need the gate). Conservative -- only unambiguous felt states.
_fam("anger", "hate", "hatred", "dislike", "contempt", "disdain", "scorn", "frustration", "frustrated", "bitterness", "bitter")
_fam("sadness", "disappointment", "disappointed", "distress", "distressed", "anguish", "grief-stricken", "regret", "regretful", "hopeless", "melancholic")
_fam("fear", "worry", "worried", "terror-stricken", "trembling", "aghast")
_fam("love", "pity", "compassion", "sympathy", "warmth", "tender")
_fam("joy", "amusement", "amused", "satisfaction", "satisfied", "rapture", "rapturous")

# valence sign per family (surprise is valence-ambiguous)
FAMILY_VALENCE = {"fear": -1, "anger": -1, "sadness": -1, "disgust": -1, "shame": -1, "jealousy": -1,
                  "longing": -1, "joy": 1, "love": 1, "pride": 1, "calm": 1, "hope": 1, "surprise": 0}


def _lemma(tok: str) -> str:
    t = tok.lower()
    t = re.sub(r"(ied)$", "y", t)
    if len(t) > 4:
        t = re.sub(r"(ed|es|ing|s)$", "", t)
    return t


def _stem_candidates(word: str):
    """Inflection-robust lemma candidates, MINIMAL strips first (hated->hate before 'hat')."""
    w = word.lower()
    c = [w]
    if w.endswith("ied") and len(w) > 4:
        c.append(w[:-3] + "y")
    if w.endswith("ing") and len(w) > 5:
        c.append(w[:-3] + "e"); c.append(w[:-3])
    if w.endswith("ed") and len(w) > 3:
        c.append(w[:-1]); c.append(w[:-2])
    if w.endswith("es") and len(w) > 3:
        c.append(w[:-1]); c.append(w[:-2])
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        c.append(w[:-1])
    out = []
    for x in c:
        if x and x not in out:
            out.append(x)
    return out


class AffectLexicon:
    """Word -> is-emotion (curated DENOTATION gate) + family/category + valence (Warriner-centered,
    primary). is_emotion_word() gates extraction on the closed affective vocabulary; the valence VALUE
    is the continuous Warriner norm. Glass-box dict lookup, no model at inference."""
    _cache = None

    def __init__(self, valence: Dict[str, float], arousal: Dict[str, float]):
        self.val = valence            # word -> centered valence in [-1,+1]
        self.aro = arousal            # word -> arousal in [0,1]
        self.terms = _FAMILY_TERMS    # term -> family (the gate)

    @classmethod
    def load(cls) -> "AffectLexicon":
        if cls._cache is not None:
            return cls._cache
        valence: Dict[str, float] = {}
        arousal: Dict[str, float] = {}
        with open(WARRINER, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                w = (row.get("Word") or "").strip().lower()
                if not w:
                    continue
                try:
                    v = float(row["V.Mean.Sum"]); a = float(row["A.Mean.Sum"])
                except (KeyError, ValueError):
                    continue
                valence[w] = round((v - 5.0) / 4.0, 4)
                arousal[w] = round((a - 1.0) / 8.0, 4)
        cls._cache = cls(valence, arousal)
        return cls._cache

    def _family(self, word: str) -> Optional[str]:
        for c in _stem_candidates(word):
            if c in self.terms:
                return self.terms[c]
        return None

    def is_emotion_word(self, word: str) -> bool:
        """DENOTATION gate: the word is in the curated emotion-denoting vocabulary (a felt state)."""
        return self._family(word) is not None

    def category(self, word: str) -> Optional[str]:
        """The emotion CATEGORY = the curated family (clean; not NRC's promiscuous association flags)."""
        return self._family(word)

    def categories(self, word: str) -> Set[str]:
        f = self._family(word)
        return {f} if f else set()

    def _warriner(self, word: str):
        for c in _stem_candidates(word):
            if c in self.val:
                return self.val[c]
        return None

    def valence(self, word: str) -> Optional[float]:
        """Continuous valence [-1,+1] (Warriner, primary); falls back to the family polarity sign."""
        v = self._warriner(word)
        if v is not None:
            return v
        f = self._family(word)
        if f is not None and FAMILY_VALENCE.get(f):
            return 0.5 * FAMILY_VALENCE[f]
        return None

    def valence_sign(self, word: str) -> Optional[int]:
        v = self.valence(word)
        if v is None:
            f = self._family(word)
            return FAMILY_VALENCE.get(f) if f else None
        if v > 0.0625:
            return 1
        if v < -0.0625:
            return -1
        # near-neutral Warriner value but a known-polarity family -> trust the family sign
        f = self._family(word)
        return FAMILY_VALENCE.get(f, 0) if f else 0

    def arousal(self, word: str) -> Optional[float]:
        for c in _stem_candidates(word):
            if c in self.aro:
                return self.aro[c]
        return None


if __name__ == "__main__":
    lex = AffectLexicon.load()
    print("warriner words:", len(lex.val), "| curated emotion terms:", len(lex.terms))
    for w in ("afraid", "happy", "angry", "delighted", "terror", "joy", "loved", "hated", "scared",
              # the NRC over-fires that must now be EXCLUDED:
              "war", "death", "money", "friends", "married", "excellent", "time", "legal", "father",
              # causative/-ing that must be EXCLUDED:
              "frightening", "delightful", "amazing"):
        print("  %-11s emotion=%-5s sign=%s cat=%s" % (
            w, lex.is_emotion_word(w), lex.valence_sign(w), lex.category(w)))
