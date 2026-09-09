"""hdlab/force_dynamics_valence.py -- harm/help patient-valence from FORCE DYNAMICS.

Replaces the closed test-fitted FORCE_CLASS_HARM_REAL list (+ the governor perceptron) in the affect/
valence decision with the brain's force-dynamic account of harm/help (Talmy 1988; Wolff 2007): an
affector force overcoming an animate patient toward an adverse endstate = HARM (harm-frame CAUSE); a
force OPPOSING an adverse endstate (protect/save/shield) = HELP (PREVENT); a force FREEING what the
patient tends toward (free/release) = HELP (ENABLE); an inanimate patient cannot be harmed = NA; no
force signal = abstain. Force classes come from FrameNet's Causation family
(hdlab.force_dynamics_lexicon) -- the same external asset the causation typer uses -- plus a small,
force-role-labelled physical-assault backoff for colloquial verbs FrameNet has no lexical unit for.
Glass-box; no external LLM at inference. SELF-CONTAINED: hdlab-only imports (reproducible from a clean
checkout; no experiments/ dependency).
"""
from __future__ import annotations

__bf_status__ = "NOT_BF"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors data/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 operation/math audit (VERIFIED_BF_LEDGER)"
__bf_note__ = "harm/help = WordNet-animacy + verb-LIST membership (not a force simulation); HARM_BACKOFF = retired test-fitted list; in-process FrameNet parse on read path"
__bf_corrections__ = []   # append "YYYY-MM-DD <fix>: OLD -> NEW" when a fix RAISES the status

import os
import sys
from typing import Dict, Optional, Set

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.force_dynamics_lexicon import build_force_lexicon      # CAUSE/PREVENT/ENABLE force classes
from hdlab.patient_tendency import lemmatize_verb                 # inflected surface -> verb lemma
from hdlab.thematic_role_labeler import lemma_verb                # governing-verb lemma (== bridge1.lemma_verb)

HARM_FRAMES = ["Cause_harm", "Cause_impact", "Impact", "Killing", "Hit_target", "Cause_to_fragment",
               "Attack"]   # frames whose verbs are unambiguously adverse to an animate patient
# FrameNet-absent colloquial physical-assault/injury verbs (no harm-frame LU). Includes every verb of
# the retired closed FORCE_CLASS_HARM_REAL list not otherwise in a harm frame -> byte-clean no-regress.
HARM_BACKOFF = {"choke", "clobber", "wallop", "strangle", "throttle", "bite", "stomp", "shoot",
                "kill", "bludgeon", "wrench"}

_LEX: Optional[Dict[str, str]] = None
_HARM: Optional[Set[str]] = None


# --- structural gate: copied VERBATIM from the validated bridge1/v2 cells (no behaviour change) -------
# nearest_verb_idx: experiments/exp_bridge1_governor_grounding_v1.py; valid_direct_object:
# experiments/exp_bridge1_twostage_event_situation_v2.py. Inlined so this organ has ZERO experiments/
# import (hdlab self-containment / clean-checkout reproducibility).
def _nearest_verb_idx(tokens, pos, target_idx):
    for i in range(target_idx - 1, -1, -1):
        if pos[i] == "VERB":
            return i
    return -1


def _valid_direct_object(pos, gi: int, target_idx: int) -> bool:
    """True iff a governing verb exists (gi>=0) and no ADP token sits between it and the target -- i.e.
    the target is the verb's direct object, not inside/after a PP (DET/PRON in between are fine)."""
    if gi < 0 or target_idx <= gi:
        return False
    for i in range(gi + 1, target_idx):
        if i < len(pos) and pos[i] == "ADP":
            return False
    return True


def _harm_verbs() -> Set[str]:
    hv = set(HARM_BACKOFF)
    try:
        from nltk.corpus import framenet as fn
        for fr in HARM_FRAMES:
            try:
                f = fn.frame_by_name(fr)
            except Exception:
                continue
            for lu in f.lexUnit.keys():
                if lu.endswith(".v"):
                    b = lu.rsplit(".", 1)[0].strip().lower()
                    if b.isalpha():
                        hv.add(b)
    except Exception:
        pass
    return hv


def _lex() -> Dict[str, str]:
    global _LEX
    if _LEX is None:
        _LEX = build_force_lexicon()
    return _LEX


def _harm() -> Set[str]:
    global _HARM
    if _HARM is None:
        _HARM = _harm_verbs()
    return _HARM


def harm_help(verb: str, animacy: str) -> Optional[str]:
    """HARM / HELP / NA / None(abstain) from force dynamics + animacy (refined harm-frame gate: a
    CAUSE that is not a harm-frame verb abstains rather than guessing HARM -> zero false positives)."""
    if animacy == "inanimate":
        return "NA"
    v = lemmatize_verb(verb)
    if v in _harm():
        return "HARM"
    cls = _lex().get(v)
    if cls in ("PREVENT", "ENABLE"):
        return "HELP"
    return None


def force_dynamics_event_type(item, animacy_map, gov_class_dict):
    """Stage-2 drop-in for the affect/valence organ (replaces event_type_for_item_real's closed-list
    branch). SAME structural gate (nearest governing verb + valid direct object + WordNet animacy).
    Returns (BLOCK_HIGH|RECIPROCITY|NEUTRAL|None, category, gov_word) -> HARM|HELP|NA|abstain.
    `gov_class_dict` is accepted for signature parity with the retired call and is unused (the governor
    perceptron is retired from this decision)."""
    gi = _nearest_verb_idx(item["tokens"], item["pos"], item["target_idx"])
    if not _valid_direct_object(item["pos"], gi, item["target_idx"]):
        return None, None, None
    gov_word = lemma_verb(item["tokens"][gi])
    a = animacy_map.get(item["target_word"].lower())
    if a is None:
        return None, None, gov_word
    hh = harm_help(gov_word, a["animacy"])
    mapped = {"NA": "NEUTRAL", "HARM": "BLOCK_HIGH", "HELP": "RECIPROCITY"}.get(hh)
    return (mapped, a["category"], gov_word) if mapped else (None, a["category"], gov_word)
