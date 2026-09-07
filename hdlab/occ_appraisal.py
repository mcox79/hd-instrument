"""occ_appraisal -- the glass-box OCC APPRAISAL inference: infer a character's UNSTATED emotion by appraising a
recent EVENT against that character's active GOALS (goal-conduciveness x prospect -> OCC type + valence).

THE PROBLEM (infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence): the reader reads STATED
emotion (hdlab.affect_register) bound to a coref-resolved experiencer, and tracks GOALS + status
(hdlab.goal_register) and the causal/event stream, but never COMPOSES event-vs-goal into the emotion the text
leaves UNSAID (goal won -> satisfaction; goal thwarted -> disappointment; a feared prospect confirmed -> fear;
a feared prospect averted -> relief). This module is that composition -- the forward OCC appraisal, the exact
SIBLING of hdlab.theory_of_mind (believes x wants -> action): there the composition is belief x desire; here it
is EVENT x GOAL -> felt emotion. NO external LLM at inference; a transparent, hand-auditable table, not a
learned classifier.

THE BRAIN (PINNED, research-verified -- see notes/problems/.../research_occ_appraisal_brain_mechanism_2026-09-06.md):
- OCC (Ortony, Clore & Collins 1988): emotion TYPE is a structural decision over (a) DESIRABILITY of the event
  for the agent's goal, (b) PROSPECT (actual vs a still-prospective hoped/feared event, and did the outcome
  CONFIRM or DISCONFIRM it), [+ (c) agency/deservingness for the social types]. The prospect branch is the
  load-bearing one: it separates satisfaction (actual good) from RELIEF (a feared bad that did NOT happen) and
  disappointment (a hoped good that failed) from FEARS-CONFIRMED (a feared bad that did happen).
- Scherer component-process: goal-conduciveness is the FIRST/most load-bearing appraisal check.
- Barrett constructed emotion: core affect (valence) is CONSTRUCTED with situational knowledge into a category;
  here the "situational knowledge" that turns valence into satisfaction-vs-relief IS the goal status + prospect
  the goal register + affect register + event stream already carry. vmPFC/OFC goal-value + amygdala appraisal.
The load-bearing move: the OCC TYPE is computed from DESIRABILITY x PROSPECT, NOT a lexical emotion lookup.

REUSE, not rebuild (mirrors theory_of_mind.py): this composes the LIVE promoted registers --
  desirability  <- hdlab.goal_register goal STATUS (satisfied/failed), generalized upstream by
                   hdlab.goal_register.track_status_thwart (goal-FAILURE-by-thwart, the landed diff);
  prospect      <- hdlab.affect_register STATED fear/hope about a stimulus + whether the event stream
                   CONFIRMED or DISCONFIRMED that prospect (the second landed generalization, here).
It defines NO new register -- only the OCC composition rule + prospect detection. Glass-box, stdlib+hdlab only
(NO experiments/ import, NO torch), ASCII, deterministic. LANDED into hdlab (Q111,
infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence); the default-on sm.infer_emotion(char[,t])
read-out on SituationReader (hdlab.situation_reader._read_infer_emotion) drives this over the LIVE registers.
Promoted VERBATIM from experiments/_occ_appraisal.py; the ONLY change is the import (hdlab.goal_register instead
of experiments/) so the module is stdlib+hdlab only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# valence sign per OCC type (family from hdlab.affect_lexicon so the floors, which read STATED emotion words to
# families, are comparable at the type grain).
_TYPE_VALENCE = {
    "satisfaction": +1, "hope": +1, "relief": +1, "joy": +1,
    "disappointment": -1, "distress": -1, "fear": -1, "fears_confirmed": -1,
    # OCC ATTRIBUTION branch (agency + praiseworthiness) -- the social compounds:
    "gratitude": +1, "anger": -1, "pride": +1, "shame": -1, "admiration": +1, "reproach": -1,
}
_TYPE_FAMILY = {
    "satisfaction": "joy", "hope": "hope", "relief": "joy", "joy": "joy",
    "disappointment": "sadness", "distress": "sadness", "fear": "fear", "fears_confirmed": "fear",
    "gratitude": "gratitude", "anger": "anger", "pride": "pride", "shame": "shame",
    "admiration": "admiration", "reproach": "anger",
}

# ATTRIBUTION transform (OCC ch.7): a WELL-BEING type + AGENCY -> the compound SOCIAL emotion. desirable +
# another agent's action -> gratitude; undesirable + another's action -> anger; self-caused -> pride/shame (these
# also need a STANDARD/praiseworthiness judgement -- flagged: the coarse prototype maps self-agency structurally).
_SOCIAL_TRANSFORM = {
    # CLEAN STRUCTURAL SLICE: another agent caused the outcome -> gratitude / anger (the agency dimension alone).
    ("satisfaction", "other"): "gratitude", ("disappointment", "other"): "anger",
    # ("satisfaction","self")->pride / ("disappointment","self")->shame are DELIBERATELY OMITTED: pride/shame
    # require a PRAISEWORTHINESS / STANDARD judgement (OCC ch.7), a norms representation the substrate lacks --
    # the researched wall (see SOLVED). self/impersonal agency leaves the well-being type unchanged.
}
# animate-PERSON cue set (a blameworthy/praiseworthy OTHER must be an AGENT, not weather/an object). Closed cue
# set + capitalized-non-initial proper-name detection; a storm/frost/"it" is impersonal, not "other".
_ANIMATE_NOUNS = {"neighbour", "neighbor", "stranger", "boy", "girl", "man", "woman", "colleague", "partner",
                  "coworker", "co-worker", "teacher", "friend", "driver", "coach", "judge", "officer", "nurse",
                  "doctor", "clerk", "someone", "somebody", "people", "child", "kid", "lady", "gentleman",
                  "guy", "person", "thief", "waiter", "manager", "boss", "mother", "father", "brother", "sister"}
_STOP_CAP = {"the", "a", "an", "he", "she", "it", "they", "his", "her", "their", "mr", "mrs", "ms", "dr"}


def causing_agency(char, outcome_sents_raw):
    """Agency of the outcome cause: 'other' if an animate PERSON other than the goal-holder acted in the outcome
    clause (a named proper noun, capitalized non-initially, or an animate cue noun); else None (self/impersonal --
    left as the well-being type). Glass-box surface cue (the reader's coref/animacy would supply this live)."""
    cl = (char or "").lower()
    _ACCIDENTAL = {"accidentally", "mistakenly", "unintentionally", "inadvertently"}
    for s in outcome_sents_raw:
        toks = s.split()
        low = {t.strip(".,;:!?\"'").lower() for t in toks}
        if low & _ACCIDENTAL:
            return None                                # Tier-1 controllability: non-volitional -> not anger/gratitude
        for i, t in enumerate(toks):
            w = t.strip(".,;:!?\"'").lower()
            if w in _ANIMATE_NOUNS:
                return "other"
            if i > 0 and t[:1].isupper() and w and w != cl and w not in _STOP_CAP and w.isalpha():
                return "other"                         # a named VOLITIONAL person other than the goal-holder
    return None


def socialize(occ_type, agency):
    """Map a well-being OCC type to its ATTRIBUTION compound given the agency of the CAUSING event."""
    if agency is None:
        return occ_type
    return _SOCIAL_TRANSFORM.get((occ_type, agency), occ_type)


@dataclass
class AppraisedEmotion:
    occ_type: str                 # satisfaction|disappointment|distress|hope|fear|relief|fears_confirmed
    valence: int                  # +1 / -1
    family: str                   # affect-lexicon family (joy/sadness/fear/hope) -- for floor comparability
    source: str                   # which appraisal branch fired (goal_actual / prospect_confirm / ...)
    char: Optional[str] = None
    basis: Optional[str] = None    # the goal text / feared stimulus this was appraised against (audit)


# ===========================================================================
# (1) THE PURE OCC RULE -- desirability x prospect -> OCC type. Fixed A PRIORI from OCC (Ch. 4-6), authored
# BEFORE any gold item (the analog of theory_of_mind.forward_action / compose_action). Hand-auditable table.
# ===========================================================================
def appraise(desirability: Optional[int], prospect: str) -> Optional[str]:
    """desirability in {+1 goal-conducive, -1 goal-obstructive, None}; prospect in
    {"actual","prospective","confirmed","disconfirmed"}. Returns the OCC type, or None (no appraisal).

    OCC table:
      +1 actual        -> satisfaction     (goal met / desirable event occurred)
      -1 actual        -> disappointment   (goal thwarted / undesirable event occurred)   [distress if goal-less]
      +1 prospective   -> hope             (a hoped-for future event, unresolved)
      -1 prospective   -> fear             (a feared future event, unresolved)
      +1 confirmed     -> satisfaction     (a hope that came true)
      -1 confirmed     -> fears_confirmed  (a fear that came true)
      +1 disconfirmed  -> disappointment   (a hope that failed)
      -1 disconfirmed  -> relief           (a feared bad that did NOT happen)  <-- the load-bearing OCC case
    """
    if desirability is None or desirability == 0:
        return None
    pos = desirability > 0
    if prospect == "actual":
        return "satisfaction" if pos else "disappointment"
    if prospect == "prospective":
        return "hope" if pos else "fear"
    if prospect == "confirmed":
        return "satisfaction" if pos else "fears_confirmed"
    if prospect == "disconfirmed":
        return "disappointment" if pos else "relief"
    return None


def emotion_of(occ_type: Optional[str], source: str, char=None, basis=None) -> Optional[AppraisedEmotion]:
    if occ_type is None:
        return None
    return AppraisedEmotion(occ_type=occ_type, valence=_TYPE_VALENCE[occ_type],
                            family=_TYPE_FAMILY[occ_type], source=source, char=char, basis=basis)


# ===========================================================================
# (2) PROSPECT DETECTION (the second upstream generalization) -- read a FEARED/HOPED prospect off the STATED
# affect register (fear/hope family about a stimulus) + whether the EVENT STREAM confirmed/disconfirmed it.
# ===========================================================================
_FEAR_FAMILY = "fear"
_HOPE_FAMILIES = {"hope", "joy"}
# FAVORABLE-resolution cues (the feared bad did NOT happen / the hoped good DID) -> DISCONFIRM a fear (relief) /
# CONFIRM a hope (satisfaction). Takes PRIORITY when both fire ("no house was lost" -> favorable).
_FAVORABLE = {"benign", "safe", "fine", "spared", "survived", "healthy", "clear", "negative", "unharmed",
              "avoided", "averted", "escaped", "cured", "recovered", "okay", "alright", "unhurt", "intact",
              "false", "mistaken", "approved", "selected", "won", "accepted", "stopped", "saved", "well",
              "rescued", "clean", "passed"}
# ADVERSE-resolution cues (the feared bad DID happen) -> CONFIRM a fear (fears_confirmed) / DISCONFIRM a hope.
_ADVERSE = {"malignant", "cancer", "died", "dead", "crashed", "failed", "lost", "fired", "laid", "gone",
            "worst", "struck", "burned", "burnt", "flooded", "cancelled", "canceled", "rejected", "ruined",
            "destroyed", "disqualified", "terminal", "wrecked", "collapsed", "drowned", "denied", "cut"}
_NEGATORS = {"not", "n't", "never", "no", "none", "nobody", "nothing"}


def _toks(text) -> List[str]:
    if isinstance(text, (list, tuple)):
        text = " ".join(str(t) for t in text)
    return re.findall(r"[a-z']+", str(text).lower())


def _stem(w: str) -> str:
    """MINIMAL stem for the recurrence check (flood/flooded, cut/cut, drown/drowned)."""
    w = w.lower()
    for suf in ("ed", "ing", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def detect_prospect_sign(desir: int, feared_stimulus_words, outcome_texts) -> dict:
    """Given the prospect DESIRABILITY sign (+1 hoped / -1 feared) and the later OUTCOME sentence surfaces, decide
    the prospect branch (prospective / confirmed / disconfirmed). Returns {desirability, prospect, basis}.

    feared_stimulus_words: tokens naming the feared/hoped thing (affect.stimulus or the affect sentence).
    outcome_texts: surfaces of the sentences AFTER the prospect sentence (its resolution)."""
    basis = " ".join(feared_stimulus_words) if feared_stimulus_words else ""
    lt = [_toks(t) for t in (outcome_texts or [])]
    flat = [w for s in lt for w in s]
    if not flat:
        return {"desirability": desir, "prospect": "prospective", "basis": basis}
    fs = set(flat)
    favorable = bool(fs & _FAVORABLE)
    # the feared/hoped thing RECURRED as an event (stemmed), not inside a negated clause -> the prospect MATERIALIZED
    stim = {_stem(w) for w in (feared_stimulus_words or []) if len(w) > 2}
    stim_stems = {_stem(w) for w in flat}
    stim_recurs = bool(stim & stim_stems)
    adverse = bool(fs & _ADVERSE)
    negated_adverse = any((_stem(w) in _ADVERSE or w in _ADVERSE) and (set(sent[max(0, i - 3):i]) & _NEGATORS)
                          for sent in lt for i, w in enumerate(sent))
    # RESOLUTION. Three outcome signals, each mapped to confirm/disconfirm by the prospect's SIGN:
    #   stim_recurs = the prospect EVENT itself materialized -> the prospect is CONFIRMED (both signs).
    #   favorable   = a GOOD resolution -> a feared bad AVERTED (fear disconfirmed) / a hoped good CAME (hope
    #                 confirmed). Dominates a colliding adverse cue ("no house was lost" -> relief).
    #   adverse     = a BAD resolution (non-negated) -> a feared bad HAPPENED (fear confirmed) / a hoped good
    #                 FAILED (hope disconfirmed).
    if stim_recurs and not favorable:
        return {"desirability": desir, "prospect": "confirmed", "basis": basis}
    if favorable and not (adverse and not negated_adverse):
        return {"desirability": desir, "prospect": "disconfirmed" if desir < 0 else "confirmed", "basis": basis}
    if adverse and not negated_adverse:
        return {"desirability": desir, "prospect": "confirmed" if desir < 0 else "disconfirmed", "basis": basis}
    return {"desirability": desir, "prospect": "prospective", "basis": basis}


# ===========================================================================
# (3) THE LIVE READ-OUT -- compose the registers off a read SituationModel. sm must expose goal_register/affect_
# register/events (track_goals + track_affect default-on). Returns AppraisedEmotion or None (no appraisal fires:
# the honest gap). This is the shape of the default-on sm.infer_emotion(char) read-out (Q111).
# ===========================================================================
def infer_emotion(sm, char: str, *, sents=None, status_fn=None, canon=None,
                  prospect_first: bool = True, social: bool = False, attribution: bool = False) -> Optional[AppraisedEmotion]:
    """Infer char's UNSTATED emotion by appraising the event stream against char's goals + feared/hoped prospects.
    status_fn(goals, events, sents, canon) sets goal .status (default = the upstream thwart-aware generalization).
    canon(surface, si) is the reader's coref resolver (binds pronoun event-agents to the goal's named agent). The
    caller passes the reader's own sentence token-lists as `sents` (surface for thwart/prospect cue scanning)."""
    char_l = (char or "").lower()
    goal_reg = getattr(sm, "goal_register", None)
    affect_reg = getattr(sm, "affect_register", None)
    events = list(getattr(sm, "events", []) or [])
    sent_surfaces = [" ".join(str(t) for t in toks) for toks in sents] if sents is not None else None

    # ---- prospect branch (fear/hope + confirm/disconfirm) -- OCC's load-bearing separation ----
    prospect_em = None
    aff = _salient_prospect_affect(affect_reg, char_l) if affect_reg is not None else None
    prospect_si, prospect_desir, stim_words = None, None, []
    if aff is not None:
        prospect_si = getattr(aff, "sent_idx", None)
        fam = getattr(aff, "emotion_cat", None)
        prospect_desir = -1 if fam == _FEAR_FAMILY else (+1 if fam in _HOPE_FAMILIES else None)
        stim_words = _stimulus_words(aff, sents)
    if prospect_desir is None and sents is not None:
        # FALLBACK (composes with -- does NOT rebuild -- the affect register): scan the char's own clause for a
        # fear/hope cue the register missed ("dread"-verb is not a psych lexeme; a '?'-experiencer fear).
        fb = _prospect_cue_fallback(sents, char_l)
        if fb is not None:
            prospect_si, prospect_desir, stim_words = fb
    if prospect_desir is not None:
        outcome = _sentences_after(sent_surfaces, prospect_si if prospect_si is not None else -1)
        pr = detect_prospect_sign(prospect_desir, stim_words, outcome)
        occ = appraise(pr["desirability"], pr["prospect"])
        prospect_em = emotion_of(occ, "prospect_" + pr["prospect"], char=char, basis=pr.get("basis"))

    # ---- goal branch (satisfied/failed -> satisfaction/disappointment) ----
    goal_em = None
    if goal_reg is not None:
        goals = [g for g in goal_reg.goals
                 if (getattr(g, "agent_canonical", None) or getattr(g, "agent", "") or "").lower() in (char_l, "?", "")]
        if attribution and sent_surfaces is not None:
            # OCC ATTRIBUTION feeder: posit implicit MAINTAIN/OBTAIN goals from effort/possession (anger antecedent).
            from hdlab.goal_register import implicit_investment_goals
            goals = goals + implicit_investment_goals(sent_surfaces, char)
        if goals:
            if status_fn is not None:
                status_fn(goals, events, sents=sents, canon=canon)
            g = _most_recent_resolved(goals)
            if g is not None:
                desir = +1 if g.status == "satisfied" else (-1 if g.status == "failed" else None)
                occ = appraise(desir, "actual")
                # ATTRIBUTION branch (social=True): another agent caused the outcome -> gratitude / anger.
                if occ is not None and social and sent_surfaces is not None:
                    agency = causing_agency(char, sent_surfaces[getattr(g, "sent_idx", 0) + 1:])
                    occ = socialize(occ, agency)
                goal_em = emotion_of(occ, "goal_actual", char=char, basis=getattr(g, "goal_text", None))

    # SELECTION: a RESOLVED prospect (confirmed/disconfirmed -> relief/fears_confirmed, the OCC prospect emotions)
    # preempts the goal branch; a resolved GOAL (satisfied/failed) beats a merely PROSPECTIVE (unresolved)
    # prospect; else the prospective prospect (fear/hope). `prospect_first=False` forces goal-first (an ablation).
    resolved_prospect = prospect_em is not None and not prospect_em.source.endswith("prospective")
    if not prospect_first:
        return goal_em or prospect_em
    if resolved_prospect:
        return prospect_em
    return goal_em or prospect_em


# fear/hope prospect cue lexicon (for the fallback + for scoring the last-stated-word floor). fear-family +
# 'dread' (the register's psych set omits it); hope-family.
_FEAR_CUE = {"afraid", "scared", "terrified", "frightened", "anxious", "nervous", "worried", "feared",
             "fear", "fears", "terror", "panic", "apprehensive", "alarmed", "dread", "dreaded", "dreads",
             "petrified", "horrified", "uneasy"}
_HOPE_CUE = {"hopeful", "hoped", "hoping", "hope", "hopes", "eager", "eagerly"}
_PRON = {"he", "she", "they", "him", "her", "them", "his", "their", "hers", "i", "we"}


def _prospect_cue_fallback(sents, char_l):
    """Scan for a fear/hope cue in a sentence whose subject is the char (or a pronoun bound to it, single
    protagonist). Returns (sent_idx, desirability, stim_words) or None. Composes with the affect register."""
    for si, toks in enumerate(sents):
        low = [str(t).lower() for t in toks]
        if not low:
            continue
        subj_is_char = (char_l in low[:3]) or (low[0] in _PRON)
        if not subj_is_char:
            continue
        if any(w in _FEAR_CUE for w in low):
            return si, -1, [w for w in low if len(w) > 3 and w not in _FEAR_CUE]
        if any(w in _HOPE_CUE for w in low):
            return si, +1, [w for w in low if len(w) > 3 and w not in _HOPE_CUE]
    return None


# ---- helpers over the live registers ----
def _salient_prospect_affect(affect_reg, char_l):
    """The char's most salient FEAR/HOPE stated affect (the prospect emotion), most-recent first. Returns an
    Affect or None. A fear/dread word states the FEARED prospect whose resolution the appraisal reads."""
    try:
        affs = affect_reg.affects_of(char_l)
    except Exception:
        affs = []
    for a in affs:
        fam = getattr(a, "emotion_cat", None)
        if fam in ("fear",) or fam in _HOPE_FAMILIES:
            return a
    return None


def _stimulus_words(aff, sents):
    words = []
    st = getattr(aff, "stimulus", None)
    if st:
        words += _toks(st)
    si = getattr(aff, "sent_idx", None)
    if sents is not None and si is not None and 0 <= si < len(sents):
        words += [w for w in _toks(sents[si]) if len(w) > 3]
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); out.append(w)
    return out


def _sentences_after(sent_surfaces, si):
    if sent_surfaces is None or si is None or si < 0:
        return []
    return sent_surfaces[si + 1:]


def _most_recent_resolved(goals):
    """The most recent goal with a resolved (satisfied|failed) status -- that is the one the outcome appraises.
    Falls back to the most recent goal (active -> no appraisal)."""
    resolved = [g for g in goals if getattr(g, "status", "active") in ("satisfied", "failed")]
    pool = resolved or goals
    return sorted(pool, key=lambda g: (getattr(g, "sent_idx", 0), getattr(g, "verb_tok", 0)), reverse=True)[0] if pool else None


if __name__ == "__main__":
    # pure-rule smoke: the OCC table (the load-bearing rows are the prospect ones)
    cases = [(+1, "actual", "satisfaction"), (-1, "actual", "disappointment"),
             (+1, "prospective", "hope"), (-1, "prospective", "fear"),
             (-1, "confirmed", "fears_confirmed"), (-1, "disconfirmed", "relief"),
             (+1, "confirmed", "satisfaction"), (+1, "disconfirmed", "disappointment")]
    ok = True
    for des, pr, want in cases:
        got = appraise(des, pr)
        flag = "OK" if got == want else "FAIL"
        if got != want:
            ok = False
        print("  appraise(%+d,%-13s) = %-15s [%s]" % (des, pr, got, flag))
    print("PURE OCC RULE", "OK" if ok else "FAIL")
