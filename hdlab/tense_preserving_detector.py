"""tense_preserving_detector.py -- the COMPOSITIONAL Reichenbach tense reader, promoted VERBATIM (2026-09-03)
from experiments/exp_tense_preserving_event_detector_v1.py (the validated preserve_tense detector).

Promoted so hdlab.situation_reader (the default-ON `preserve_tense` flag) does not depend on the untracked
experiment cell at inference. Pure stdlib, NO spaCy / NO LLM. `assign_sentence(toks, upos, mode="surface")`
assigns every UPOS==VERB a Reichenbach triple (tense/aspect/voice + is_pp + finite + effective_tense via
mark-and-inherit for non-finite events). Byte-faithful to the experiment (witness:
test_preserve_tense_landing_organ.py -- promotion-faithful check).
"""
from __future__ import annotations

from typing import Dict, List, Optional

# Closed-class auxiliaries by SURFACE FORM (English morphology -- a lexicon parameter).
HAVE_FORMS = {"have", "has", "had", "having", "'ve"}
BE_FORMS = {"be", "been", "being", "am", "is", "are", "was", "were", "'re", "'m"}
WILL_FORMS = {"will", "shall", "'ll", "wo"}          # wo(n't) = will
MODAL_FORMS = {"would", "could", "should", "might", "may", "must", "can", "ca"}   # ca(n't)=can
DO_FORMS = {"do", "does", "did"}
AUX_PAST = {"had", "was", "were", "did", "would", "could", "should", "might"}
AUX_PRES = {"have", "has", "am", "is", "are", "do", "does", "can", "may", "shall", "ca"}
SKIP_LEFT = {"not", "n't", "never", "always", "also", "just", "only", "really", "still",
             "already", "not", "even", "ever", "so", "then", "now", "often", "sometimes",
             "usually", "generally", "certainly", "probably", "quickly", "slowly", "carefully",
             "all", "both", "long", "newly", "merely", "therefore", "fully", "quite", "once",
             "hastily", "rather", "previously", "thereupon", "first", "before", "but", "much",
             "nearly", "almost", "recently", "finally", "suddenly", "soon"}

# Small irregular-inflection lists (surface mode only): forms whose -ed/-en shape is opaque.
IRREG_PART = {"been", "done", "gone", "seen", "written", "taken", "given", "known", "shown",
              "grown", "thrown", "drawn", "spoken", "broken", "chosen", "frozen", "stolen",
              "driven", "risen", "eaten", "beaten", "hidden", "bitten", "fallen", "forgotten",
              "gotten", "become", "come", "run", "made", "found", "held", "kept", "left",
              "meant", "sent", "spent", "built", "lost", "told", "sold", "heard", "led",
              "read", "put", "set", "cut", "let", "brought", "bought", "caught", "taught",
              "thought", "sought", "understood", "stood", "won", "begun", "sung", "swung"}
IRREG_PAST = {"was", "were", "went", "ran", "saw", "ate", "took", "gave", "knew", "grew",
              "threw", "drew", "spoke", "broke", "chose", "froze", "stole", "drove", "rose",
              "came", "became", "found", "held", "kept", "left", "meant", "sent", "spent",
              "built", "lost", "told", "sold", "heard", "led", "brought", "bought", "caught",
              "taught", "thought", "sought", "understood", "stood", "won", "began", "sang",
              "swam", "fell", "felt", "got", "made", "said", "did", "had", "wrote", "rode",
              "hid", "bit", "sat", "met", "paid", "laid", "flew", "drank", "sank", "shrank"}

# label constants (Reichenbach)
PAST, PRES, FUT, NONE_T = "PAST", "PRESENT", "FUTURE", "NONE"
SIMPLE, PERF, PROG, PERF_PROG = "SIMPLE", "PERFECT", "PROGRESSIVE", "PERF_PROG"
ACTIVE, PASSIVE = "ACTIVE", "PASSIVE"


def _main_form(tok: str, i: int, toks: List[str], has_have: bool, has_be: bool,
               prev_to: bool, prev_modal: bool, xpos: Optional[List[str]], mode: str) -> str:
    """Return a coarse PTB form for the main verb: VBD/VBN/VBZ/VBP/VBG/VB."""
    if mode == "finetag" and xpos is not None:
        xp = xpos[i]
        if xp in ("VBD", "VBN", "VBZ", "VBP", "VBG", "VB"):
            return xp
    w = tok.lower()
    if w.endswith("ing") and len(w) > 4:
        return "VBG"
    if w in IRREG_PART:
        if has_have or has_be:
            return "VBN"
        if w in IRREG_PAST:
            return "VBD"
        return "VBN"
    if w in IRREG_PAST:
        return "VBD"
    if w.endswith("ed") or w.endswith("d"):
        return "VBN" if (has_have or has_be) else "VBD"
    if prev_to or prev_modal:
        return "VB"
    if w.endswith("s") and not w.endswith("ss"):
        return "VBZ"
    return "VBP"


def _left_aux_chain(toks: List[str], upos: List[str], i: int, window: int = 5) -> List[str]:
    """Collect the contiguous auxiliary lemmas immediately governing the verb at i (scan left,
    skipping adverbs/negation)."""
    chain: List[str] = []
    j = i - 1
    steps = 0
    while j >= 0 and steps < window:
        w = toks[j].lower()
        if w in (".", ",", ";", ":", "!", "?", "--", "(", ")", '"', "''", "``"):
            break
        is_aux = (upos[j] == "AUX") or (w in HAVE_FORMS or w in BE_FORMS or w in WILL_FORMS
                                        or w in MODAL_FORMS or w in DO_FORMS)
        if is_aux:
            chain.append(w)
            j -= 1
            steps += 1
            continue
        if w in SKIP_LEFT or upos[j] in ("ADV", "PART"):
            j -= 1
            steps += 1
            continue
        break
    chain.reverse()
    return chain


def assign(toks: List[str], upos: List[str], i: int, xpos: Optional[List[str]] = None,
           mode: str = "surface") -> Dict[str, object]:
    """COMPOSITIONAL Reichenbach reader for the main verb at index i (upos[i]=='VERB'). Returns
    dict(word_tense, tense, aspect, voice, is_pp, finite, form)."""
    chain = _left_aux_chain(toks, upos, i)
    has_have = any(a in HAVE_FORMS for a in chain)
    has_be = any(a in BE_FORMS for a in chain)
    has_will = any(a in WILL_FORMS for a in chain)
    has_modal = any(a in MODAL_FORMS for a in chain)
    prev_to = i > 0 and toks[i - 1].lower() == "to"
    prev_modal = has_modal or has_will
    form = _main_form(toks[i], i, toks, has_have, has_be, prev_to, prev_modal, xpos, mode)

    if form in ("VBD", "VBN"):
        word_tense = PAST
    elif form in ("VBZ", "VBP"):
        word_tense = PRES
    elif form == "VBG":
        word_tense = PRES
    else:
        word_tense = NONE_T

    aspect = SIMPLE
    voice = ACTIVE
    if has_have and form == "VBN" and has_be:
        aspect = PERF
    elif has_have and form in ("VBN", "VBD"):
        aspect = PERF
    if has_be and form == "VBG":
        aspect = PERF_PROG if has_have else PROG
    if has_be and form == "VBN":
        voice = PASSIVE

    if has_will:
        tense = FUT
    elif chain:
        first = chain[0]
        if first in AUX_PAST:
            tense = PAST
        elif first in AUX_PRES:
            tense = PRES
        elif first in MODAL_FORMS:
            tense = PRES
        else:
            tense = PRES
    else:
        if form == "VBD":
            tense = PAST
        elif form in ("VBZ", "VBP"):
            tense = PRES
        else:
            tense = NONE_T
    finite = tense in (PAST, PRES, FUT) and not (prev_to)
    is_pp = (tense == PAST and aspect in (PERF, PERF_PROG))
    return {"word_tense": word_tense, "tense": tense, "aspect": aspect, "voice": voice,
            "is_pp": is_pp, "finite": finite, "form": form}


def assign_sentence(toks: List[str], upos: List[str], xpos: Optional[List[str]] = None,
                    mode: str = "surface") -> Dict[int, Dict[str, object]]:
    """Assign every UPOS==VERB in a sentence, then resolve MARK-AND-INHERIT for non-finite events
    (a non-finite verb inherits its Reference time from the nearest controlling finite verb;
    Ogihara/Abusch sequence-of-tense)."""
    res: Dict[int, Dict[str, object]] = {}
    for i in range(len(toks)):
        if upos[i] == "VERB":
            res[i] = assign(toks, upos, i, xpos=xpos, mode=mode)
    fin = sorted(i for i in res if res[i]["finite"])
    for i, a in res.items():
        if a["finite"]:
            a["inherit_from"] = None
            a["effective_tense"] = a["tense"]
        else:
            anchor = None
            best = 10 ** 9
            for j in fin:
                d = abs(j - i) * 2 + (1 if j > i else 0)
                if d < best:
                    best, anchor = d, j
            a["inherit_from"] = anchor
            a["effective_tense"] = res[anchor]["tense"] if anchor is not None else a["tense"]
    return res
