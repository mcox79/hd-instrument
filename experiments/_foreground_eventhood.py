"""Graded FOREGROUND / EVENT-HOOD gate for causal encoding -- Stage-1 precision filter.

PROBLEM: causal_encoding_over_fires_without_a_foreground_event_hood_gate. The p2 within-clause
force typer (wire_the_causation_typer..., owner-DONE) is accurate on its curated causative domain
(0.833) but on real OPEN TEXT it OVER-FIRES: it tries to read a causal link off almost any clause
whose verb is force-lexicon-listed, so on descriptive/stative/background prose it invents causal
links that are not there ("the court HAS its houses", "call myself Pip", "fog ... MAKING a
drizzle").

BRAIN MECHANISM (PINNED -- inherited from the p2 drill research_discourse_decision_to_encode_
causation_2026-08-30.md): causal encoding is a BY-PRODUCT of EVENT-MODEL construction; only a
FOREGROUNDED EVENT is a causal-arc candidate (Zwaan & Radvansky 1998 event-indexing -- causation is
indexed over EVENT nodes; Zacks 2007 event segmentation; Hopper 1979 / Hopper & Thompson 1980
grounding -- foreground = high-TRANSITIVITY main-line dynamic bounded realis clauses; background =
stative/descriptive/generic/subordinate). The brain is causal-by-DEFAULT between foregrounded
segments (Sanders 2005), so the fix is a PRECISION FILTER ON EVENT-HOOD, not a suppressor on
causation.

WHAT THE p2 STOPGAP GATE DID, AND WHY IT REGRESSED RECALL: it operationalized ONLY the dependency-
attachment sub-part (B3) as a HARD KILL -- veto any verb heading a relcl/acl/appos or a bare
participial advcl, plus a naming frame (B2). Measured: it cut Bleak-House over-fire 22->17 but
regressed the curated within-clause headline 0.833->0.810, because some genuine foreground
causatives sit in subordinate clauses (a finite advcl in a because/so chain, a relative clause that
still asserts a bounded action). A dep-label alone is a blunt proxy for grounding.

THIS MODULE -- the more brain-faithful replication: Hopper & Thompson (1980) transitivity is a
GRADIENT (a cluster of ~10 co-varying parameters -- kinesis, aspect/telicity, punctuality,
volitionality, affirmation/realis, individuation & affectedness of the object) that PREDICTS
foregrounding; high transitivity clusters with foreground, low with background. We replace the
single-signal hard kill with a GRADED event-hood SCORE over that cluster read off the parse, so a
HIGH-transitivity causative in a subordinate clause still passes (recall held) while a LOW-
transitivity stative/generic/backgrounded clause is vetoed (precision raised) -- exactly where the
dep-label gate could not separate them.

PINNED: causal encoding over foregrounded EVENT nodes; transitivity-gradient -> foregrounding;
aspect as an online foreground signal. OUR-INVENTION (built + swept here): the exact feature legs,
their weights, and the engage threshold theta. Glass-box, structure-read, NO external LLM.
"""
from __future__ import annotations

import bisect
import os
import sys
from typing import Dict, List, Optional

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_wire_causation_typer_live_reader_v1 as W  # the p2 wired reader + helpers

TYPES = W.TYPES

# ---------------------------------------------------------------------------
# LEG 1 -- DYNAMICITY / KINESIS (Hopper&Thompson param A; Vendler states; Levin stative classes).
# A state that HOLDS is not a foreground event. Closed, auditable stoplist of stative / relational /
# perception / cognition / possession / measure verbs whose force-lexicon membership is a polysemy
# accident on real prose. (Superset of the p2 _STATIVE_VERBS, which was tuned for the SENSE leg.)
# ---------------------------------------------------------------------------
_STATIVE_RELATIONAL = {
    "be", "have", "own", "possess", "contain", "hold", "comprise", "consist", "belong", "constitute",
    "represent", "include", "involve", "lack", "concern", "regard", "resemble", "remain", "exist",
    "stay", "seem", "appear", "look", "sound", "equal", "measure", "weigh", "cost", "matter", "count",
    "depend", "range", "extend", "stand", "sit", "lie", "occupy", "surround", "face", "border",
    # perception / cognition (stative senses -- LitBank tags these O)
    "know", "believe", "think", "understand", "realize", "realise", "suppose", "imagine", "doubt",
    "mean", "see", "hear", "feel", "notice", "perceive", "recognize", "recognise", "wonder", "expect",
    "want", "wish", "need", "prefer", "love", "hate", "like", "dislike", "fear", "hope", "mind",
    "deserve", "owe", "require",
}

# ---------------------------------------------------------------------------
# LEG 4 -- REALIS / affirmation & mode (Hopper&Thompson params I mode, J affirmation). A negated or
# hypothetical clause is not an asserted foreground event (LitBank annotates REALIS events only).
# ---------------------------------------------------------------------------
_IRREALIS_MODALS = {"would", "could", "might", "should", "may", "must", "shall", "can", "ca"}

# ---------------------------------------------------------------------------
# LEG 2 -- GROUNDING (Hopper 1979 foreground/background via the parse). GRADED, not a hard kill.
# main-line assertion (ROOT / coordinate) = foreground; noun-modifying or bare-participial adjunct =
# background; a FINITE subordinate clause (advcl/ccomp/xcomp with its own subject or aux or mark) is
# NEUTRAL -- it can carry a foreground event (because/so chains, reported events), so it is NOT
# killed (this is the fix for the p2 recall regression).
# ---------------------------------------------------------------------------
_BG_NOUN_MOD = {"acl", "relcl", "appos"}          # noun-modifying clauses = background
_MAINLINE = {"ROOT", "conj", "parataxis"}


def _leg_dynamicity(vlem: str) -> int:
    return -2 if vlem in _STATIVE_RELATIONAL else 1


def _leg_grounding(vtok) -> int:
    dep = vtok.dep_
    if dep in _MAINLINE:
        return 1
    if dep in _BG_NOUN_MOD:
        return -2
    if dep == "advcl":
        # bare participial free adjunct (VBG/VBN, no subject/aux/mark) = background; finite advcl = neutral
        finite = any(c.dep_ in ("aux", "auxpass", "nsubj", "nsubjpass", "mark") for c in vtok.children)
        if vtok.tag_ in ("VBG", "VBN") and not finite:
            return -2
        return 0
    if dep in ("ccomp", "xcomp", "pcomp"):
        return 0                                    # complement clause -- neutral (can be an event)
    return 0                                         # conj-less / other -- neutral


def _leg_aspect(vtok) -> int:
    """Hopper: perfective/bounded = foreground; imperfective/progressive/gnomic-present = background.
    Read off the tense/aspect morphology + aux children."""
    tag = vtok.tag_
    auxlemmas = {c.lemma_.lower() for c in vtok.children if c.dep_ in ("aux", "auxpass")}
    if tag == "VBG":
        # progressive (be + VBG) = imperfective/backgroundable; bare VBG handled by grounding
        return -1 if ("be" in auxlemmas) else 0
    if tag == "VBN":
        return 1 if ("have" in auxlemmas) else 0    # perfect = bounded/foreground; bare passive = neutral
    if tag == "VBD":
        return 1                                     # simple past = the canonical foreground tense
    if tag in ("VBZ", "VBP"):
        return -1                                    # gnomic/habitual present = description (downweight)
    return 0                                          # VB base / infinitive


def _leg_individuation(ptok, patient: str) -> int:
    """Hopper&Thompson param individuation of O: a SPECIFIC referential patient is transitive/
    foreground; a GENERIC / bare-plural / kind-referring object is a description. Read off the
    object token's determiner + POS."""
    if ptok is None:
        return 0                                      # no object (intransitive) -- neutral, not penalized
    if ptok.pos_ == "PROPN":
        return 1
    if ptok.pos_ == "PRON":
        # a wh-/relative/indefinite/expletive pro-form (do WHAT, make WHO) is NON-referential = a
        # light/pro-verb frame, not an affected individuated patient (-1); a referentially-OPEN pronoun
        # (it/that/this) needs coref -> NEUTRAL (0, as the p2 gate found); a bound personal pronoun
        # (him/her/them...) is individuated (+1). Hopper&Thompson individuation of O.
        pl = ptok.lemma_.lower()
        if pl in ("what", "who", "whom", "whose", "which", "there", "something", "anything", "nothing"):
            return -1
        if pl in ("it", "that", "this", "these", "those"):
            return 0
        return 1                                      # he/she/they/him/her/us/me... referential
    dets = {c.lemma_.lower() for c in ptok.children if c.dep_ in ("det", "poss")}
    if dets & {"the", "this", "that", "these", "those", "my", "his", "her", "its", "their", "our", "your"}:
        return 1                                      # definite / demonstrative / possessive = specific
    if ptok.tag_ == "NNS" and not dets:
        return -1                                     # bare plural = kind/generic reference
    if ptok.tag_ == "NN" and not dets:
        return -1                                     # bare mass/generic
    return 0


def eventhood_legs(vtok, affector: str, patient: str, ptok, vlem: str) -> Dict[str, int]:
    """Every leg, transparently, for auditing/ablation."""
    neg = any(c.dep_ == "neg" or c.lemma_.lower() in ("not", "never", "no") for c in vtok.children)
    auxlemmas = {c.lemma_.lower() for c in vtok.children if c.dep_ in ("aux", "auxpass")}
    marks = {c.lemma_.lower() for c in vtok.children if c.dep_ == "mark"}
    irrealis = bool(auxlemmas & _IRREALIS_MODALS) or ("if" in marks)
    realis = -2 if neg else (-1 if irrealis else 0)
    return {
        "dyn": _leg_dynamicity(vlem),                                  # kinesis (B1)
        "ground": _leg_grounding(vtok),                               # foreground grounding (B3, graded)
        "aspect": _leg_aspect(vtok),                                  # boundedness (B4/Hopper)
        "indiv": _leg_individuation(ptok, patient),                   # individuation of O (B4)
        "affect": W._leg_patient_affectedness(patient),              # affectedness of O (Dowty; shared leg)
        "realis": realis,                                            # affirmation/mode (Hopper)
    }


# the discourse legs that are NEW relative to the p2 argument SENSE gate (which already reads
# dynamicity/affectedness). Used for the ablation that isolates the foreground gate's marginal lift.
_DISCOURSE_LEGS = ("ground", "aspect", "indiv", "realis")

# THE DEFAULT GATE (chosen by the INDEPENDENT leg-alignment measurement + held-out validation, NOT by the
# precision outcome): the three CLEANEST Hopper transitivity parameters -- ASPECT (the dominant online
# foreground signal, event-rate 0.43 fg vs 0.10 bg), INDIVIDUATION of O, and REALIS/affirmation. The
# graded GROUNDING leg (dep-attachment) is DROPPED: it is the weakest separator (event-rate 0.35 vs 0.34)
# and is exactly the single signal the p2 dep-label stopgap hard-killed on -- measured NET-HARMFUL even as
# a categorical veto. DYNAMICITY and AFFECTEDNESS are DROPPED from the SCORE (they duplicate the upstream
# force-SENSE gate already applied to these candidates; kinesis survives as the categorical STATIVE veto).
# This leaner gate MORE THAN DOUBLES the precision lift (+0.080 vs +0.034 for the full 6-leg cluster) while
# holding the within-clause recall EXACTLY, and generalizes across a held-out doc split. Full-6 and
# discourse-4 remain COMPUTED for ablation.
DEFAULT_LEGS = ("aspect", "indiv", "realis")


def eventhood_score(vtok, affector: str, patient: str, ptok, vlem: str,
                    legs: Optional[List[str]] = None) -> int:
    d = eventhood_legs(vtok, affector, patient, ptok, vlem)
    keys = legs if legs is not None else list(d.keys())
    return sum(d[k] for k in keys)


def is_naming_frame(vtok) -> bool:
    return W.is_naming_frame(vtok)                    # B2 -- categorical hard veto (equative/labelling)


def caused_event_token(vtok, construction):
    """Which token's event-hood DEFINES this causal link? For a PERIPHRASTIC/letting causative
    ('let me GO', 'made her LAUGH', 'had the students REWRITE') the caused happening -- and thus the
    event node -- is the COMPLEMENT verb, not the light causer verb (which LitBank's single-token
    realis scheme tags O). For a lexical/resultative/caused-motion causative the trigger IS the event.
    Returns the complement-verb token for periphrastics (if found), else vtok."""
    if construction == "periphrastic":
        comp = next((c for c in vtok.children
                     if c.dep_ in ("xcomp", "ccomp", "advcl") and c.pos_ in ("VERB", "AUX")), None)
        if comp is not None:
            return comp
    return vtok


# ---------------------------------------------------------------------------
# char-offset alignment: the typing path re-parses " ".join(toks) with spaCy, so a trigger token's
# spaCy .idx (char offset into the joined sentence) maps deterministically back to the source-token
# index (single-space join). Robust to spaCy re-tokenization (splits/merges) -- we locate the source
# token whose [start,end) char span contains the trigger's start char.
# ---------------------------------------------------------------------------
def build_char_index(toks: List[str]):
    starts, ends = [], []
    off = 0
    for t in toks:
        starts.append(off)
        off += len(t)
        ends.append(off)
        off += 1                                      # the single join space
    return starts, ends


def char_to_tok(idx: int, starts: List[int], ends: List[int]) -> int:
    j = bisect.bisect_right(starts, idx) - 1
    if j < 0:
        j = 0
    if j < len(ends) and idx >= ends[j] and j + 1 < len(starts):
        j += 1                                        # trigger start sits in the join gap -> next token
    return max(0, min(j, len(starts) - 1))


# ---------------------------------------------------------------------------
# The gated reader: runs the p2 base pipeline ONCE per sentence and records, per causative candidate,
# every signal needed to score EACH config analytically (ungated / p2-stopgap / graded / shuffled
# twin) -- so we never re-run the reader per config. Inherits ALL p2 machinery (detect/bind/endstate/
# type/sense-gate); only the recording + the graded event-hood signal are added here.
# ---------------------------------------------------------------------------
class ForegroundGatedReader(W.WiredCausationReader):
    def __init__(self, *a, eh_legs: Optional[List[str]] = None, **kw):
        kw.setdefault("causation_typed", True)
        super().__init__(*a, **kw)
        self.eh_legs = eh_legs                        # None = all legs; or a subset for ablation
        self.candidate_records: List[dict] = []

    def _read_causation_typed(self, sents, sm=None):
        nlp = self._nlp_or_load()
        gate = self._gate_or_load()
        links: List[W.TypedCausalLink] = []
        self.candidate_records = []
        for si, toks in enumerate(sents):
            starts, ends = build_char_index(toks)
            text = " ".join(toks)
            doc = nlp(text)
            for sent in doc.sents:
                for vtok in sent:
                    is_verb = vtok.pos_ == "VERB"
                    misparsed_verb = (vtok.pos_ in ("NOUN", "PROPN")
                                      and self._lex.get(vtok.lemma_.lower()) is not None
                                      and any(c.dep_ in ("dobj", "obj") for c in vtok.children))
                    if not (is_verb or misparsed_verb):
                        continue
                    cand = self._causative_candidate(sent, vtok)
                    if cand is None:
                        continue
                    affector, patient, ptok = cand["affector"], cand["patient"], cand["ptok"]
                    from_comp, construction, result_xp = cand["from_comp"], cand["construction"], cand["result_xp"]
                    vlem = vtok.lemma_.lower()
                    ctx = self._clause_context(vtok, ptok)
                    endstate = self._read_endstate(sent, vtok, ptok, from_comp, construction, result_xp)

                    # -- p2 base pipeline (the UNGATED result): literalness label + force-sense gate --
                    label = "ENGAGE_PHYSICAL"
                    base_ctype = None
                    sense_veto = False
                    if self.use_gate:
                        r = gate.assess(sent, vtok, affector, patient, ctx)
                        label = r["label"]
                        allowed = (("ENGAGE_PHYSICAL", "FORCE_NONPHYSICAL")
                                   if self.gate_mode == "force" else ("ENGAGE_PHYSICAL",))
                        gate_applies = (self.sense_gate and from_comp is None
                                        and construction != "periphrastic")
                        force_veto = (gate_applies
                                      and W.force_engagement_score(affector, vlem, patient) < self.sense_tau)
                        if label not in allowed or force_veto:
                            sense_veto = True
                            base_ctype = "ABSTAIN"
                    if base_ctype is None:
                        base_ctype = self._type_clause(affector, vlem, patient, ctx, endstate,
                                                       construction, result_xp)

                    # -- event-hood signals (all configs computed from these) --
                    legs = eventhood_legs(vtok, affector, patient, ptok, vlem)
                    eh_all = sum(legs.values())
                    eh_disc = sum(legs[k] for k in _DISCOURSE_LEGS)
                    eh_clean = sum(legs[k] for k in DEFAULT_LEGS)   # the DEFAULT gate (aspect+indiv+realis)
                    naming = is_naming_frame(vtok)
                    # p2 stopgap veto = B3 hard-kill (not foregrounded) OR B2 naming
                    stopgap_veto = (not W.is_foregrounded_event(vtok)) or naming
                    # LEG 1 as a CATEGORICAL veto (Hopper kinesis is DEFINITIONAL to foreground): a
                    # stative/perception/cognition head is never a foreground event -- UNLESS it is a
                    # genuine periphrastic causer ('have X do Y') or a PREVENT-from construction, which
                    # are syntactically-marked real causatives (bypass, as the sense gate does).
                    stative_veto = (vlem in _STATIVE_RELATIONAL and construction != "periphrastic"
                                    and from_comp is None)
                    trigger_tok_i = char_to_tok(vtok.idx, starts, ends)
                    ev_tok = caused_event_token(vtok, construction)
                    event_tok_i = char_to_tok(ev_tok.idx, starts, ends)

                    self.candidate_records.append({
                        "sent_idx": si, "trigger_tok_i": trigger_tok_i, "event_tok_i": event_tok_i,
                        "verb": vlem, "affector": affector, "patient": patient,
                        "base_ctype": base_ctype, "sense_veto": sense_veto,
                        "fires_ungated": base_ctype in TYPES,   # would the ungated reader emit a link?
                        "legs": legs, "eh_score": eh_clean,       # eh_score = the DEFAULT clean gate
                        "eh_full6_score": eh_all, "eh_disc_score": eh_disc,
                        "naming": naming, "stopgap_veto": stopgap_veto, "stative_veto": stative_veto,
                        "periph": construction == "periphrastic",
                        # the FROM-complement PREVENT construction ("saved/kept X FROM Ving") is a
                        # syntactically-marked causative -- its causal event structure is carried by the
                        # construction (Goldberg), so it is a foreground event by construction and bypasses
                        # the transitivity gate (as the p2 SENSE gate bypasses it). PERIPHRASTICS
                        # (make/have/let) are NOT bypassed: their event-hood lives on the COMPLEMENT, which
                        # the precision instrument already scores (event_tok_i), so they are gated normally.
                        "construction_marked": (from_comp is not None),
                        "construction": construction, "endstate": endstate, "label": label,
                    })
                    links.append(W.TypedCausalLink(si, affector, vlem, patient, base_ctype,
                                                   endstate, label, source=construction))
        return links
