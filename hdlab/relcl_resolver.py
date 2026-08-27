"""Relative-clause filler-gap resolver -- reversible-sentence role assignment the brain's way (NO arc graph).

Landed 2026-08-27 (consolidation phase) from the integrated `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment`
(SOLVED/EXCELLENT, owner-DONE; witness `verify_relcl_incremental_fillergap_parser.py` 8/8 PASS, re-verified first-hand).
On sentences where WORD ORDER underdetermines who-did-what-to-whom -- "the doctor that the lawyer chased" -- the
post-verbal-object heuristic and the general arc parser both fail (the arc parser is MEASURABLY HARMFUL here, 0.198 <
its info-free twin 0.305). This organ is the brain's specialised circuit for exactly those cases.

WHAT IS PINNED (copy the operation):
  * The ACTIVE-FILLER strategy (Frazier & Flores d'Arcais 1989; Clifton & Frazier): on encountering a fronted filler
    (a relative-clause antecedent), posit a GAP as soon as one is licensed. The pinned computation: a relative clause's
    verb takes the fronted antecedent as its PATIENT exactly when the OBJECT slot is empty (the gap) and a SUBJECT
    nominal already intervenes (the subject slot is filled). Everything else (subject-gap, filled object,
    complementizer, canonical matrix clause) falls back to the word-order rule.
  * Glass-box over UPOS + a closed class of relativizers ({that, which, who, whom}) -- NO dependency graph, NO arc
    heads. The relativizer must be ATTACHED (its immediately preceding token is a nominal antecedent), which rules out
    the complementizer 'that' ('said that ...', follows a verb) and interrogatives.
  * VALIDATED: beats the precise-voice two-line floor CI-separated on a powered balanced held-out reversible set
    (0.9533 vs 0.4994 at n=4800, ties the oracle 0.9981); the resolver takes NO `heads` arg and is invariant to
    permuting arc heads (the win is function-words+position, not laundered parser output). HONEST real-text bound: it
    fires on ~0.75% of QA-SRL (genuine reversibles are <1% of text) -- the value is CORRECTNESS on the rare hard
    sentences a situation model needs, not an aggregate headline.

BRAIN-FOUNDATIONAL COHERENCE (one operation): the discrete filler-gap rule is the NOISE->0 COMPETENCE LIMIT of graded
additive cue-based content-addressable RETRIEVAL (Lewis & Vasishth 2005; McElree 2000; the active-filler strategy
EMERGES from it, Dotlacil 2021) -- the SAME retrieval/competition primitive as the parser role competition
(hdlab.graded_competition) and the episodic store. Reversible role binding localises to POSTERIOR-TEMPORAL / pMTG /
inferior-parietal (Beber et al. 2025; Matchin & Hickok 2020), NOT a BA44 "movement" operator.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour. `resolve_patient` is a pure function
of (tokens, UPOS, verb index). It leaves CANONICAL clauses untouched (the construction gate is net-positive: on
non-reversible clauses it == the two-line rule). Wire as the reversible-case route AFTER the role assigner; route to
it only when the object-gap gate fires (or expose the two competing scorers + a conflict term, NOT an if/else -- the
route-CONFLICT is a gold-free difficulty signal). MEASURE on the live reader before any capability claim.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from hdlab.thematic_role_labeler import _is_participle   # participle test for the precise voice cue

NOMINAL = {"NOUN", "PROPN", "PRON"}
BE_AUX = {"is", "are", "was", "were", "be", "been", "being", "am"}
RELATIVIZERS = {"that", "which", "who", "whom"}


def _cands(pos: Sequence[str]) -> List[int]:
    """1-based indices of the nominal tokens (candidate arguments)."""
    return [i for i in range(1, len(pos) + 1) if pos[i - 1] in NOMINAL]


def precise_passive(toks: Sequence[str], pos: Sequence[str], v: int) -> bool:
    """Precise voice cue: a BE-aux in the 3 tokens before v AND the verb token is a past participle."""
    lo = max(1, v - 3)
    has_be = any(toks[j - 1].lower() in BE_AUX for j in range(lo, v))
    vtag = pos[v - 1] if v - 1 < len(pos) else None
    return has_be and _is_participle(toks[v - 1], vtag)


def two_line_patient(toks: Sequence[str], pos: Sequence[str], v: int,
                     cands: Optional[List[int]] = None, prec_voice: Optional[bool] = None) -> Optional[int]:
    """The word-order + participle-voice baseline: passive -> nearest nominal before v; active -> nearest after."""
    if cands is None:
        cands = _cands(pos)
    if prec_voice is None:
        prec_voice = precise_passive(toks, pos, v)
    if prec_voice:
        before = [i for i in cands if i < v]
        return before[-1] if before else (cands[0] if cands else None)
    after = [i for i in cands if i > v]
    return after[0] if after else (cands[-1] if cands else None)


def _nearest_attached_relativizer_left(pos: Sequence[str], low: Sequence[str], v: int):
    """The active-filler construction gate. Returns (relativizer_idx, antecedent_idx) for the nearest relativizer
    strictly left of v whose IMMEDIATELY PRECEDING token is a nominal (the antecedent it attaches to -- the defining
    property of a relative clause; rules out the complementizer 'that' and interrogatives). (None, None) if none."""
    for i in range(v - 1, 0, -1):
        if low[i - 1] in RELATIVIZERS and (i - 2) >= 0 and pos[i - 2] in NOMINAL:
            return i, i - 1
    return None, None


def _has_post_object(pos: Sequence[str], low: Sequence[str], v: int) -> bool:
    """Is v's object slot FILLED by an overt nominal in its OWN clause? Scans right from v, stopping at the next
    clause boundary (a finite VERB, punctuation, or a relativizer). The active-filler strategy posits an object GAP
    only where this is FALSE (the object position is empty)."""
    n = len(pos)
    for j in range(v + 1, n + 1):
        t = pos[j - 1]
        if t == "VERB" or t == "PUNCT" or low[j - 1] in RELATIVIZERS:
            break
        if t in NOMINAL:
            return True
    return False


def is_object_gap(toks: Sequence[str], pos: Sequence[str], v: int) -> bool:
    """Glass-box: does the active-filler OBJECT-gap construction fire at verb v? (an attached relativizer left of v,
    an overt subject nominal intervening, and NO overt object in v's clause)."""
    low = [t.lower() for t in toks]
    r, filler = _nearest_attached_relativizer_left(pos, low, v)
    if r is None or filler is None:
        return False
    interveners = [j for j in range(r + 1, v) if pos[j - 1] in NOMINAL]
    return bool(interveners) and not _has_post_object(pos, low, v)


def resolve_patient(toks: Sequence[str], pos: Sequence[str], v: int,
                    cands: Optional[List[int]] = None, prec_voice: Optional[bool] = None) -> Optional[int]:
    """The active-filler filler-gap resolver (THE DELIVERABLE). Returns the 1-based index of verb v's PATIENT:
      (1) passive (aux+participle) -> the pre-aux subject is the patient (ventral voice route);
      (2) an attached relative-clause OBJECT gap (subject filled, object empty) -> the fronted filler is the patient;
      (3) otherwise (subject-gap / filled object / canonical) -> the word-order (two-line) rule.
    Takes NO arc heads -- glass-box over UPOS + closed-class relativizers."""
    if cands is None:
        cands = _cands(pos)
    if prec_voice is None:
        prec_voice = precise_passive(toks, pos, v)
    low = [t.lower() for t in toks]
    if prec_voice:                                              # (1) passive
        before = [i for i in cands if i < v]
        return before[-1] if before else (cands[0] if cands else None)
    r, filler = _nearest_attached_relativizer_left(pos, low, v)  # (2) object-gap relative clause / cleft
    if r is not None and filler is not None:
        interveners = [j for j in range(r + 1, v) if pos[j - 1] in NOMINAL]
        if interveners and not _has_post_object(pos, low, v):
            return filler
    after = [i for i in cands if i > v]                          # (3) canonical / subject-gap: two-line
    return after[0] if after else (cands[-1] if cands else None)


__all__ = ["resolve_patient", "two_line_patient", "is_object_gap", "precise_passive",
           "NOMINAL", "RELATIVIZERS", "BE_AUX"]
