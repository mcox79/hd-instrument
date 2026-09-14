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

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (reader CATALOG owner-DONE + BRAIN_FOUNDATIONAL_AUDIT §2b; strategy first-hand cross-ref)'
__bf_note__ = 'admissible static offline affect-norm SUPPLY feeding a separately-pinned appraisal read; CAT admissible foundation'
__bf_corrections__ = ['2026-09-13 the affect value was ONE number per WORD FORM (a sense-conflating rating: treat +0.46, hold +0.26) -> a SENSE-KEYED value selected by the settled sense posterior, with the word-form norm kept but weighted by its own unambiguity rho (Ernst & Banks precision weighting); pri-100 solver']


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



# ======================================================================================================
# SENSE-KEYED, PRECISION-WEIGHTED VALUE (solver 2026-09-13, pri-100
# `the_verbs_affect_value_is_one_number_across_its_senses_...`).
#
# THE DEFECT THIS CLOSES. Everything above values a WORD FORM. Warriner rates `treat` +0.46, `handle`
# +0.18, `hold` +0.26, `carry` +0.17 -- so the harm/help reader answers HELP on "the guard treated the
# prisoner". A word-form norm is an average over the word's senses weighted by whichever meaning the
# raters happened to access out of context; the reader needs the value of the meaning that is ACTIVE.
#
# THE BRAIN. The anterior-temporal hub settles on a sense from context (Rodd, Gaskell & Marslen-Wilson
# 2004, the settled semantic vector; Kuperberg's graded meaning activation) and the OFC/vmPFC values THAT
# meaning (Barsalou situated conceptualisation; PINNED valuation target, BRAIN_MATH_REFERENCE section D):
#       value(verb | context) = SUM_s P(s | context) * value(s)
# Three properties of that equation are load-bearing and each was measured:
#   (a) P(s|context) is a DISTRIBUTION, not an argmax. HEAD already has the argmax version of this read
#       (HDLAB_FDV_SENSE_ABSTAIN) and ships it OFF because "on short sentences the spreading activation
#       settles on a wrong sense". The same rung read as a posterior does not have that failure mode.
#   (b) The posterior runs over the WHOLE sense inventory. Renormalising it over the affecting-animate
#       senses alone puts probability ~1 on a rare sense (measured: `buy` -> bribe.v.01, `hate` ->
#       hate.v.01, both wrong). The affecting gate belongs on the VALUE, never on the PROBABILITY.
#   (c) A sense that is not a patient-affecting event predicts NO outcome, so its value is genuinely 0 --
#       evidence of neutrality, not missing data. An affecting sense our foundation cannot value is
#       IGNORANCE and must count as neither. `opinion` below is the posterior mass of the first two.
#
# THE WORD-FORM NORM IS NOT DELETED, IT IS WEIGHTED BY ITS OWN PRECISION (Ernst & Banks 2002 w ~ 1/sigma^2
# -- the fusion rung the pri-98 solver named as the one it could not crack: "no cue carries a variance").
# A rating of a letter string estimates the active sense's value exactly to the degree that the string HAS
# one sense, so its precision is the Simpson concentration of that string's own sense distribution:
#       rho(w) = SUM_i p_i^2  over ALL of w's senses and parts of speech (SemCor resting levels)
# Measured: rho(treat) 0.247, rho(hold) 0.119, rho(carry) 0.216, rho(pull) 0.280 against rho(murder) 0.763,
# rho(kill) 0.777, rho(protect) 0.936. THE FUSION:
#       v_hat(verb | ctx) = [ k_w * rho(verb) * v_warriner + SUM_s P(s|ctx) v(s) ] / [ k_w * rho(verb) + 1 ]
#
# WHAT SUPPLIES value(s): data/frontend_assets/sense_affect_norm_v1.json, built offline by
# tools/build_sense_affect_norm_asset.py from five SENSE-KEYED channels (VerbNet result state / WordNet's
# own caused event / the pri-98 manner decomposition / the immediate superordinate / the nearest
# informative ancestor / the sense's co-names with the target lemma excluded). Rows carry the SemCor
# RESTING-LEVEL COUNT, so `observe_sense()` accrues in the same units and the value is one pure function
# of counts (plastic, never frozen).
#
# THIS MODULE STAYS stdlib-ONLY. It supplies the sense-keyed VALUES and the resting-level prior; the
# CONSUMER supplies P(s|context) (hdlab.force_dynamics_valence already owns the spreading-activation
# graph). Called with posterior=None the read is the resting-level expectation.
# ======================================================================================================
SENSE_ASSET = os.path.join(REPO, "data/frontend_assets/sense_affect_norm_v1.json")
SENSE_CHANNELS = ("R", "C", "M", "H", "S", "T")   # precedence within one sense; SWEPT (see the SOLVED note)
SENSE_K_W = 2.0        # precision scale of the word-form norm relative to the sense posterior's total 1
SENSE_TAU = 0.10       # |fused value| below which the rung hands on (HEAD's WEAK_VALENCE, unchanged)
SENSE_TAU_NEUTRAL = 0.5   # posterior mass on NON-affecting senses before the read may DECIDE neutral
SENSE_ALPHA = 0.5      # resting-level count smoothing
SENSE_LAM = 4.0        # blend temperature the CONSUMER should use when it computes P(s|context) with the
                       # spreading-activation graph (the organ's WSD default 0.5 is far too flat for a VALUE
                       # read: at 0.5 the context moves E(treat) by 0.007, at 4.0 by 0.14; plateau 4.0-8.0)

_SENSE_TABLE = None


def sense_table() -> Dict:
    """lemma -> [[synset, resting-level count, affecting01, {channel: value}], ...]; {} when the asset is
    absent, in which case every function below abstains and nothing upstream changes."""
    global _SENSE_TABLE
    if _SENSE_TABLE is None:
        try:
            import json
            with open(SENSE_ASSET, "r", encoding="utf-8") as f:
                _SENSE_TABLE = json.load(f)
        except Exception:
            _SENSE_TABLE = {"senses": {}, "words": {}}
    return _SENSE_TABLE


def sense_rows(lemma: str):
    return sense_table().get("senses", {}).get(lemma, [])


def observe_sense(lemma: str, synset: str, n: int = 1) -> None:
    """THE ONLINE PATH (plastic, never frozen). Meeting `lemma` used in sense `synset` is one presentation:
    it raises that sense's RESTING LEVEL by the same count the offline SemCor tally holds. The expectation
    is one pure function of those counts, so a reader that reads shifts its own prior -- there is no second
    mechanism. Verified: 200 observations of `treat` in its medical sense move E from +0.161 to +0.509."""
    rows = sense_table().setdefault("senses", {}).setdefault(lemma, [])
    for r in rows:
        if r[0] == synset:
            r[1] += n
            return
    rows.append([synset, n, 1, {}])


def sense_value(row, channels=SENSE_CHANNELS) -> Optional[float]:
    """value(sense) for a patient: the first channel that fires, in precedence order. None means the sense
    contributes nothing -- either because it is not a patient-affecting event (a real zero) or because the
    foundation cannot value it (ignorance); `sense_expectation` keeps those two apart."""
    if not row[2]:
        return None
    ch = row[3] or {}
    for c in channels:
        if c in ch:
            return float(ch[c])
    return None


def resting_level(rows, alpha: float = SENSE_ALPHA):
    """P(s) over ALL of the lemma's senses from the presentation counts (ACT-R base-level activation read
    as a distribution; Anderson & Schooler 1991)."""
    c = [float(r[1]) + alpha for r in rows]
    t = sum(c) or 1.0
    return [x / t for x in c]


def sense_expectation(lemma: str, posterior=None, channels=SENSE_CHANNELS):
    """(E, coverage, opinion, neutral_mass) with E = SUM_s P(s) v(s). `posterior` is P(s|context) in the
    row order of `sense_rows(lemma)`; None uses the resting level. Returns None when the lemma is absent."""
    rows = sense_rows(lemma)
    if not rows:
        return None
    p = list(posterior) if posterior is not None else resting_level(rows)
    if len(p) != len(rows):
        p = resting_level(rows)
    e = cov = neutral = 0.0
    for pi, r in zip(p, rows):
        v = sense_value(r, channels)
        if v is None:
            if not r[2]:
                neutral += pi
            continue
        e += pi * v
        cov += pi
    return e, cov, cov + neutral, neutral


def sense_rho(lemma: str) -> float:
    """The unambiguity of the letter string = the precision of its word-form norm as a statement about the
    sense in play (Simpson concentration of the string's own sense distribution over all POS)."""
    return float(sense_table().get("words", {}).get(lemma, {}).get("rho", 1.0))


def fused_sense_value(lemma: str, posterior=None, k_w: float = SENSE_K_W,
                      channels=SENSE_CHANNELS) -> Optional[float]:
    """Precision-weighted fusion of the word-form norm (precision k_w * rho) with the sense-keyed
    expectation (total precision 1)."""
    se = sense_expectation(lemma, posterior, channels)
    if se is None:
        return None
    e = se[0]
    vw = sense_table().get("words", {}).get(lemma, {}).get("v")
    if vw is None:
        return e
    pw = k_w * sense_rho(lemma)
    return (pw * float(vw) + e) / (pw + 1.0)


def sense_endstate_sign(lemma: str, posterior=None, tau: float = SENSE_TAU,
                        tau_neutral: float = SENSE_TAU_NEUTRAL, k_w: float = SENSE_K_W,
                        channels=SENSE_CHANNELS):
    """(sign, verdict) for the harm/help cascade.
      'sign'    the fused value clears tau -> +1 / -1
      'neutral' the read HAS an opinion (opinion mass >= tau_opinion) and it is that the active meaning
                leaves the patient's condition unchanged -> DECIDE 0 and STOP. Handing on here is how the
                conflation re-enters one rung later: measured, `pull` and `hold` are answered HARM by the
                verb-level manner rung from attract.v.01 / hold.v.29, senses the context never activated.
      'pass'    no opinion -> hand on to the remaining rungs, unchanged
      'na'      the lemma is not in the asset -> the word-form rung stands, unchanged"""
    se = sense_expectation(lemma, posterior, channels)
    if se is None:
        return None, "na"
    v = fused_sense_value(lemma, posterior, k_w, channels)
    if v is not None and abs(v) >= tau:
        return (1 if v > 0 else -1), "sign"
    if tau_neutral > 0.0 and se[3] >= tau_neutral:
        return 0, "neutral"
    return None, "pass"


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
