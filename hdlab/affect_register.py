"""affect_register: a glass-box AFFECT/EMOTION dimension for the narrative situation model.

THE MISSING EMOTION DIMENSION. The reader tracks the five classic Zwaan-Radvansky dimensions
(time/space/causation/protagonist+belief/intentionality) but NOT how each character FEELS. This builds
a per-character AFFECT REGISTER, populated from EXPLICIT emotion constructions (the reliable Tier-1
anchors) bound to the resolved EXPERIENCER, carrying VALENCE (primary) + emotion CATEGORY (secondary).
NO spaCy at the extraction core (UPOS from the reader's frontend tagger), NO external LLM (the invariant).

BRAIN-FOUNDATIONAL (research_affect_emotion_brain_mechanism + research_experiencer_psych_verb_brain_
mechanism, both 2026-09-04):
- PINNED: emotion is a DISTINCT appraisal/affect system (amygdala/vmPFC/insula), dissociated from
  mentalizing (goal/belief = dmPFC/TPJ) and physical causation -- Campanella et al. 2022 triple
  dissociation on the SAME patients/stories (F(4,168)=5.907, p<.001). So affect is a SEPARATE dimension.
- PINNED: core affect = VALENCE + arousal (Barrett constructed emotion; Russell circumplex), with the
  discrete CATEGORY a secondary conceptualization. Valence stored primary (Warriner), category secondary
  (NRC EmoLex). Online reading recovers valence but not exact-lexical specificity (Gygax 2003/2004).
- PINNED: the EXPERIENCER is bound by the verb's stored linking (psych-verb split: fear-type exp=subject,
  frighten-type exp=object) -- the upstream hdlab-portable psych_verb_frames component.
- PINNED: affect UPDATES BY OVERWRITE -- a superseded emotion stops mattering (de Vega et al. 1996),
  UNLIKE goals which persist (Lutz & Radvansky 1997). So feels() returns the MOST RECENT active affect
  (not a reinstatement of an older one -- the deliberate asymmetry vs the goal register).
- OUR-INVENTION-UNDER-TEST: the exact construction cue set, the adverb subject-orientation rule, the
  emotion-noun binding, the overwrite rule. Swept, not adopted.
- LOCATED NEGATIVE: INFERRED (unstated) emotion ("she slammed the door" -> anger) needs the OCC-appraisal
  meaning channel over the causation+goal registers -- the explicit-vs-inferred split (same as goals).

LANDED into hdlab (Q111, the_situation_model_has_no_affect_emotion_dimension). Promoted VERBATIM from
experiments/affect_register.py; the ONLY change is the imports (hdlab.goal_register / hdlab.affect_lexicon
/ hdlab.psych_verb_frames instead of the experiments/ modules). SELF-CONTAINED: stdlib + hdlab only, NO
experiments/ dependency. The reader-integration (extract->canon->experiencer-link->register) is driven by
hdlab.situation_reader._read_affect (mirroring _read_goals).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# reader-integration helpers are dimension-agnostic -> REUSE the goal register's (make_canonicalizer /
# _norm / _PRONOUNS) rather than re-deriving; the affect register only adds its own extraction + query.
from hdlab import goal_register as GR
from hdlab.affect_lexicon import AffectLexicon, _lemma
from hdlab.psych_verb_frames import is_psych_lexeme, OBJ_EXP_VERBS

# ---------------------------------------------------------------------------
# construction cue sets
# ---------------------------------------------------------------------------
COPULA = {"be", "is", "was", "are", "were", "been", "being", "am", "'s", "'re", "'m",
          "seem", "seemed", "seems", "look", "looked", "looks", "appear", "appeared", "appears",
          "become", "became", "becomes", "grow", "grew", "grown", "get", "got", "gotten", "gets",
          "remain", "remained", "remains", "sound", "sounded", "sounds"}
FEEL_VERBS = {"feel", "felt", "feels", "have", "had", "has", "experience", "experienced", "experiences"}
# light "affect" verbs for the metaphor construction ("terror swept over him", "joy filled her")
AFFECT_LIGHT_VERBS = {"sweep", "swept", "grip", "gripped", "seize", "seized", "overcome", "overcame",
                      "fill", "filled", "wash", "washed", "strike", "struck", "overwhelm", "overwhelmed",
                      "consume", "consumed", "take", "took", "flood", "flooded", "creep", "crept",
                      "come", "came", "rise", "rose", "well", "welled"}
LOC_PREP = {"over", "upon", "through", "on", "into", "in", "across", "through"}
POSSESSIVE_PRON = {"her", "his", "their", "my", "your", "our", "its"}
_BE_AUX = {"is", "was", "are", "were", "be", "been", "being", "am", "'s", "'re", "'m"}
NOMINAL_UPOS = {"NOUN", "PROPN", "PRON"}
# object-experiencer participle adverbs are STIMULUS-oriented, not subject-oriented (research SS4b) --
# "she spoke frighteningly" != she is frightened. Exclude these -ly adverbs from the subject-bind rule.
STIMULUS_ADV_STEMS = {"frighten", "surprise", "amaze", "annoy", "please", "disgust", "shock", "alarm",
                      "astonish", "amuse", "delight", "worry", "terrify", "horrify", "charm", "fascinate"}
_NEG = {"not", "n't", "never", "no", "hardly", "scarcely", "nor"}


@dataclass
class Affect:
    """One extracted emotion: an EXPERIENCER feels emotion_word (valence/category), optionally ABOUT a stimulus."""
    experiencer: str            # surface subject/possessor head (canonicalized downstream)
    emotion_word: str           # the emotion lexeme (adj/verb/noun/adverb base)
    emotion_cat: Optional[str]  # NRC basic-emotion category (secondary)
    valence: Optional[float]    # Warriner continuous valence [-1,+1] (primary)
    valence_sign: Optional[int] # +1/-1/0
    kind: str                   # copular_adj | felt_noun | psych_verb | adverb | to_poss | noun_poss | noun_metaphor
    stimulus: Optional[str]     # what the emotion is about (object/subject/of-PP), where recoverable
    source: str                 # the construction cue token (copula / psych verb / marker)
    sent_idx: int
    tok: int                    # token index of the emotion word
    negated: bool = False
    experiencer_canonical: Optional[str] = None


def _subject_before(toks: List[str], up: List[str], vi: int) -> Optional[Tuple[str, int]]:
    """Nearest preceding nominal head (the clause subject). Stops at a clause boundary."""
    for j in range(vi - 1, -1, -1):
        if j >= len(up):
            continue
        if up[j] in NOMINAL_UPOS:
            return toks[j].lower(), j
        if toks[j] in (".", ";", ":", "!", "?"):
            break
    return None


def _object_after(toks: List[str], up: List[str], vi: int, window: int = 5) -> Optional[Tuple[str, int, bool]]:
    """The nearest post-verbal argument. Returns (head_low, idx, is_direct_object). is_direct_object is
    True if it is a bare NP object (no preceding preposition), False if it sits inside a PP (about/of/at/
    over/for) -> the frame-shape cue for alternating psych verbs."""
    j = vi + 1
    end = min(len(toks), vi + 1 + window)
    saw_prep = None
    while j < end:
        w = toks[j].lower()
        if w in (".", ";", ":", "!", "?", "and", "but", "or", "because", "who", "which", "that"):
            break
        if j < len(up) and up[j] == "ADP":
            saw_prep = w
            j += 1
            continue
        if j < len(up) and up[j] in NOMINAL_UPOS:
            return w, j, (saw_prep is None)
        j += 1
    return None


def _negated_near(toks: List[str], vi: int, window: int = 3) -> bool:
    lo = max(0, vi - window)
    seg = [t.lower() for t in toks[lo:vi + 2]]
    return any(t in _NEG for t in seg)


def _be_aux_before(toks: List[str], up: List[str], vi: int, window: int = 3) -> bool:
    lo = max(0, vi - window)
    return any(toks[j].lower() in _BE_AUX and j < len(up) and up[j] in ("AUX", "VERB")
              for j in range(lo, vi))


def _mk(experiencer, word, lex, kind, stimulus, source, si, tok, negated):
    lw = word.lower()
    return Affect(experiencer=experiencer or "?", emotion_word=lw,
                  emotion_cat=lex.category(lw), valence=lex.valence(lw),
                  valence_sign=lex.valence_sign(lw), kind=kind, stimulus=stimulus,
                  source=source, sent_idx=si, tok=tok, negated=negated)


def extract_affect_sentence(toks: List[str], up: List[str], si: int, lex: AffectLexicon,
                            pvf=None) -> List[Affect]:
    """Extract explicit affect from ONE sentence (tokens + UPOS). Glass-box, rule-based, no LLM.
    `pvf` (a PsychVerbFrames) drives the experiencer-position of psych verbs (the upstream brain-
    foundational component); None -> the subject-experiencer default (the A/B baseline)."""
    low = [t.lower() for t in toks]
    n = len(toks)
    out: List[Affect] = []
    used_tok = set()

    # (1) COPULAR + emotion ADJ  ("Mary was afraid", "she felt happy", "he seemed delighted")
    #     + FEEL/HAVE + emotion NOUN ("she felt joy", "he had a great fear")  -> experiencer = SUBJECT.
    #     Covers passive-participle adjectives (frightened/delighted/pleased) too: the copula subject is
    #     the experiencer regardless of the adjective's source verb class (research SS4a, highest confidence).
    for i in range(n):
        lem = _lemma(low[i])
        is_cop = low[i] in COPULA or lem in COPULA
        is_feel = low[i] in FEEL_VERBS or lem in FEEL_VERBS
        if not (is_cop or is_feel):
            continue
        if i < len(up) and up[i] not in ("VERB", "AUX"):
            continue
        # scan a short window after the copula/feel verb for an emotion ADJ or NOUN
        found = None
        j = i + 1
        end = min(n, i + 6)
        while j < end:
            w = low[j]
            if w in (".", ";", ":", "!", "?", "and", "but", "because", "that", "who", "which"):
                break
            uj = up[j] if j < len(up) else "X"
            if uj in ("ADJ", "VERB") and lex.is_emotion_word(w) and (is_cop or is_feel):
                found = (w, j, "copular_adj"); break        # 'was afraid' / 'felt happy' -> subject exp
            if uj == "NOUN" and lex.is_emotion_word(w) and is_feel:
                found = (w, j, "felt_noun"); break          # 'felt joy' / 'had a great fear'
            # allow a determiner/adverb/degree word between (a/an/very/so/quite/rather/really)
            if uj in ("DET", "ADV", "PART") or w in ("a", "an", "the", "very", "so", "quite", "rather",
                                                     "really", "most", "more", "too", "such", "of", "great"):
                j += 1
                continue
            if uj in ("ADJ", "NOUN", "VERB"):     # a non-emotion predicate -> not an affect copula
                break
            j += 1
        if not found:
            continue
        w, wj, kind = found
        # '-ing' adjective of an object-experiencer verb is STIMULUS-oriented ('the storm was terrifying'
        # -> the subject is the stimulus, not the experiencer). Skip -- mirrors the adverb caveat (SS4b).
        if w.endswith("ing") and (w in OBJ_EXP_VERBS or _lemma(w) in OBJ_EXP_VERBS):
            continue
        subj = _subject_before(toks, up, i)
        neg = _negated_near(toks, i)
        # stimulus: an "of/at/about/with" PP after the emotion word ("afraid OF the dog")
        stim = None
        st = _object_after(toks, up, wj, window=4)
        if st and not st[2]:
            stim = st[0]
        out.append(_mk(subj[0] if subj else "?", w, lex, kind, stim, low[i], si, wj, neg))
        used_tok.add(wj)

    # (2) PSYCH VERB  ("Mary feared the dog" -> exp=subject; "the dog frightened Mary" -> exp=object).
    #     Experiencer position from the upstream psych_verb_frames (per-occurrence frame shape for the
    #     alternating class). PASSIVE ("was frightened by X") is handled in (1) as copular_adj (exp=subject),
    #     so here we take ACTIVE occurrences only (skip when a be-aux immediately precedes).
    for i in range(n):
        if i in used_tok:
            continue
        if not (i < len(up) and up[i] == "VERB"):
            continue
        lem = _lemma(low[i])
        # GATE on gold psych-verb LEXEME membership (arm-independent: both frame and naive use the same set,
        # only the POSITION differs). This avoids valence-only over-fires ('stared'->'star') and non-emotion
        # perception/motion verbs -- only the VerbNet/PropBank emotion-verb classes fire here.
        if not is_psych_lexeme(low[i]):
            continue
        if low[i] in GR.GOAL_VERBS or lem in GR.GOAL_VERBS:
            continue                                # desire/intend/try -> the GOAL register, not affect
        if low[i].endswith("ing"):
            continue                                # participle/gerund is stimulus-oriented ('frightening'), not a finite predication
        if _be_aux_before(toks, up, i):
            continue                                # passive -> handled by (1)
        subj = _subject_before(toks, up, i)
        if subj is None:
            continue                                # no clause subject -> attributive participle / fragment, skip
        obj = _object_after(toks, up, i)
        has_object = (obj is not None and obj[2])
        # experiencer position: the upstream psych-verb frame (per-occurrence frame shape for alternators)
        if pvf is not None:
            alt = pvf.klass(low[i]) == "alternating"
            pos = pvf.experiencer_position(low[i], has_object=has_object if alt else None)
        else:
            pos = "subject"                         # A/B BASELINE: naive subject=experiencer
        if pos == "object":
            exp = obj[0] if obj else "?"
            stim = subj[0] if subj else None
        elif pos == "oblique":
            # experiencer = object of "to"; stimulus = subject
            exp = "?"
            for j in range(i + 1, min(n, i + 5)):
                if low[j] == "to" and j + 1 < n and (j + 1 < len(up) and up[j + 1] in NOMINAL_UPOS):
                    exp = low[j + 1]; break
            stim = subj[0] if subj else None
        else:
            exp = subj[0] if subj else "?"
            stim = obj[0] if obj else None
        # the emotion word for a psych verb is the verb itself
        out.append(_mk(exp, low[i], lex, "psych_verb", stim, low[i], si, i, _negated_near(toks, i)))
        used_tok.add(i)

    # (3) AFFECTIVE ADVERB  ("she spoke angrily") -> experiencer = clause subject. Skip stimulus-oriented
    #     adverbs from object-experiencer stems (frighteningly/surprisingly) -- research SS4b.
    for i in range(n):
        if i in used_tok or not (i < len(up) and up[i] == "ADV"):
            continue
        w = low[i]
        if not w.endswith("ly") or len(w) < 5:
            continue
        base = w[:-2]
        # adjective from the -ly adverb: angrily->angry (i->y), happily->happy, sadly->sad,
        # nervously->nervous, gently->gentle (add e), fearfully->fearful.
        cands = [base, re.sub(r"i$", "y", base), base + "e", re.sub(r"il$", "le", base)]
        if _lemma(base) in STIMULUS_ADV_STEMS or base in STIMULUS_ADV_STEMS:
            continue
        emo = next((c for c in cands if lex.is_emotion_word(c)), None)
        if emo is None:
            continue
        subj = _subject_before(toks, up, i)
        out.append(_mk(subj[0] if subj else "?", emo, lex, "adverb", None, w, si, i, _negated_near(toks, i)))
        used_tok.add(i)

    # (4) "to X's N"  ("to her delight", "to his horror") -> experiencer = the possessor.
    for i in range(n - 2):
        if low[i] != "to":
            continue
        # to + possessive + emotion NOUN  (allow "to Mary's horror": PROPN + 's)
        j = i + 1
        poss = None
        if low[j] in POSSESSIVE_PRON:
            poss = low[j]; k = j + 1
        elif j + 1 < n and low[j + 1] in ("'s", "s") and (j < len(up) and up[j] in ("PROPN", "NOUN")):
            poss = low[j]; k = j + 2
        else:
            continue
        if k < n and (k < len(up) and up[k] == "NOUN") and lex.is_emotion_word(low[k]):
            out.append(_mk(poss, low[k], lex, "to_poss", None, "to", si, k, False))
            used_tok.add(k)

    # (5) EMOTION NOUN with POSSESSOR  ("her fear", "his joy", "Mary's dread") -> experiencer = possessor.
    for i in range(1, n):
        if i in used_tok or not (i < len(up) and up[i] == "NOUN"):
            continue
        if not lex.is_emotion_word(low[i]):
            continue
        prev = low[i - 1]
        poss = None
        if prev in POSSESSIVE_PRON:
            poss = prev
        elif prev in ("'s", "s") and i - 2 >= 0 and (i - 2 < len(up) and up[i - 2] in ("PROPN", "NOUN")):
            poss = low[i - 2]
        if poss is None:
            continue
        # stimulus: "her fear OF the dog"
        stim = None
        st = _object_after(toks, up, i, window=4)
        if st and not st[2]:
            stim = st[0]
        out.append(_mk(poss, low[i], lex, "noun_poss", stim, "poss", si, i, _negated_near(toks, i)))
        used_tok.add(i)

    # (6) EMOTION-NOUN METAPHOR  ("a wave of terror swept over him", "joy filled her") -> experiencer =
    #     the PP object of a locative / the object of a light affect verb (research SS4d; Landau locative).
    for i in range(n):
        if i in used_tok or not (i < len(up) and up[i] == "NOUN") or not lex.is_emotion_word(low[i]):
            continue
        # find a light affect verb after the emotion noun
        for j in range(i + 1, min(n, i + 6)):
            lj = low[j]
            if j < len(up) and up[j] == "VERB" and (lj in AFFECT_LIGHT_VERBS or _lemma(lj) in AFFECT_LIGHT_VERBS):
                exp = None
                # over/upon/through + PRON/NOUN  OR  a bare object pronoun
                for k in range(j + 1, min(n, j + 4)):
                    if low[k] in LOC_PREP and k + 1 < n and (k + 1 < len(up) and up[k + 1] in NOMINAL_UPOS):
                        exp = low[k + 1]; break
                    if k < len(up) and up[k] in NOMINAL_UPOS and low[k] not in LOC_PREP:
                        exp = low[k]; break
                if exp:
                    out.append(_mk(exp, low[i], lex, "noun_metaphor", None, lj, si, i, _negated_near(toks, i)))
                    used_tok.add(i)
                break
    return out


def extract_affect(sents: List[List[str]], pos_tags: List[List[str]], lex=None, pvf=None) -> List[Affect]:
    """Extract explicit affect across a passage. sents=[[token]], pos_tags=[[UPOS]] aligned. `pvf` (a
    PsychVerbFrames) drives psych-verb experiencer-position (the upstream fix); None -> subject default."""
    lex = lex or AffectLexicon.load()
    affects: List[Affect] = []
    for si, toks in enumerate(sents):
        up = pos_tags[si] if si < len(pos_tags) else ["X"] * len(toks)
        affects.extend(extract_affect_sentence(list(toks), list(up), si, lex, pvf=pvf))
    return affects


# ---------------------------------------------------------------------------
# EXPERIENCER BINDING (resolve each affect's surface experiencer to a canonical entity)
# ---------------------------------------------------------------------------
def bind_experiencers(affects: List[Affect], canonicalize) -> List[Affect]:
    """Resolve each affect.experiencer (surface) to a canonical entity via canonicalize(surface, si)
    (the reader's coref/entity model). This binding is the load-bearing step the info-free twin SHUFFLES."""
    for a in affects:
        a.experiencer_canonical = canonicalize(a.experiencer, a.sent_idx) or a.experiencer
    return affects


# ---------------------------------------------------------------------------
# THE PER-CHARACTER AFFECT REGISTER (the situation-model emotion dimension)
# ---------------------------------------------------------------------------
class AffectRegister:
    """A per-character register of emotions read off a passage's explicit affect constructions. Answers
    off the ACCUMULATED register (never re-reading):
      feels(char)          -> the character's CURRENT emotion (most recent active -- overwrite dynamics)
      valence_of(char)     -> the sign/value of the current emotion
      feels_about(char, y) -> how char felt about stimulus y (psych-verb / of-PP)
      affects_of(char)     -> the character's emotions, most recent first
    """

    def __init__(self, affects: List[Affect]):
        self.affects = affects
        self._by_exp: Dict[str, List[Affect]] = defaultdict(list)
        for a in affects:
            self._by_exp[(a.experiencer_canonical or a.experiencer or "?").lower()].append(a)

    def experiencers(self) -> List[str]:
        return [c for c in self._by_exp if c and c != "?"]

    def affects_of(self, char: str) -> List[Affect]:
        lst = self._by_exp.get((char or "").lower(), [])
        return sorted(lst, key=lambda a: (a.sent_idx, a.tok), reverse=True)   # most recent first

    def feels(self, char: str) -> Optional[Affect]:
        """The character's CURRENT emotion (de Vega OVERWRITE: the most recent NON-negated affect; the
        older emotion has been superseded). Falls back to the most recent affect if all are negated."""
        for a in self.affects_of(char):
            if not a.negated:
                return a
        lst = self.affects_of(char)
        return lst[0] if lst else None

    def valence_of(self, char: str) -> Optional[int]:
        a = self.feels(char)
        return a.valence_sign if a is not None else None

    def feels_about(self, char: str, stimulus: str) -> Optional[Affect]:
        st = _norm(stimulus)
        cands = [a for a in self.affects_of(char)
                 if a.stimulus and (_norm(a.stimulus) == st or st in _norm(a.stimulus))]
        return cands[0] if cands else None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


if __name__ == "__main__":
    from hdlab.psych_verb_frames import PsychVerbFrames
    lex = AffectLexicon.load()
    pvf = PsychVerbFrames.load()
    sents = [["Mary", "was", "afraid", "of", "the", "dog", "."],
             ["The", "dog", "frightened", "her", "."],
             ["John", "feared", "the", "storm", "."],
             ["She", "spoke", "angrily", "."],
             ["To", "his", "delight", ",", "the", "sun", "rose", "."],
             ["Her", "joy", "was", "great", "."]]
    pos = [["PROPN", "AUX", "ADJ", "ADP", "DET", "NOUN", "PUNCT"],
           ["DET", "NOUN", "VERB", "PRON", "PUNCT"],
           ["PROPN", "VERB", "DET", "NOUN", "PUNCT"],
           ["PRON", "VERB", "ADV", "PUNCT"],
           ["ADP", "PRON", "NOUN", "PUNCT", "DET", "NOUN", "VERB", "PUNCT"],
           ["PRON", "NOUN", "AUX", "ADJ", "PUNCT"]]
    for a in extract_affect(sents, pos, lex, pvf):
        print("%-13s exp=%-6s emo=%-9s cat=%-6s val=%s stim=%s" % (
            a.kind, a.experiencer, a.emotion_word, a.emotion_cat, a.valence_sign, a.stimulus))
