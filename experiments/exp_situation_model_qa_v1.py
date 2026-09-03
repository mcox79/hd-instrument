"""exp_situation_model_qa_v1 -- UNIFIED GLASS-BOX QA OVER THE LIVE SituationModel.

THE CAPSTONE: the reader builds a rich SituationModel (entities / coref_resolutions / events /
timeline_frames / causal_links) but there is NO way to ASK IT A QUESTION. The assembly proved ONE
dimension end-to-end (who-did-what). This cell builds a UNIFIED, glass-box "ask the model" interface:
route a structure-dependent question to the dimension that holds the answer, and READ THE ANSWER OFF
THE ACCUMULATED MODEL (never by re-reading the text), then measure it over a retrieval/word-overlap
floor with the info-free twin LOSING, per-dimension AND aggregate.

HOW THE BRAIN DOES THIS (opening move):
  PINNED (the computation): comprehension builds a situation model whose PURPOSE is inference/QA
    (Kintsch 1988 construction-integration; van Dijk & Kintsch 1983). A probe question is answered by
    CONSULTING the maintained model, not by re-reading (Zwaan & Radvansky 1998 event-indexing; the
    hippocampal/DMN situation model IS the queryable memory). A question SELECTS the dimension that
    holds the answer -- "who is she" -> the entity/coref index; "who did what" -> the event index;
    "before or after" -> the temporal index. Question-type -> dimension is the retrieval-cue-selects-
    the-store computation.
  OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the surface-question -> dimension ROUTER (glass-box
    wh-cue rules), the per-dimension READOUT format, and the abstain policy. We COPY the computation
    (route by question type; read off the accumulated model); we SWEEP the router/readout.
  NOT brain-faithful (this is the FLOOR, not the model): answering by RE-READING / word-overlap
    against the raw text; a monolithic classifier ignoring the dimension structure; an external LLM.

DISK-OUTRANKS-BRIEF (verified 2026-08-30): the brief lists location_register / belief_partition /
state_register / force_dynamics_typer as "integrated" dimensions to route to. They exist as ORGAN
FILES but are NOT fields on the live hdlab.situation_reader.SituationModel -- the reader never
populates SPACE / ToM-belief / entity-state. So the live model can only be QUERIED on the dimensions
it actually accumulates: ENTITIES (coref + salience), EVENTS (who-did-what), TIME (timeline_frames),
CAUSATION (causal_links). We build QA over THOSE, and we report where/who-believes as an HONEST
per-dimension NEGATIVE (the organ is an island, not wired into the reader) -- which is exactly the
kind of rigorous per-dimension diagnostic the brief asks for, and it names the next problem.

GLASS-BOX. NO external LLM (gold OR inference). Gold is EXISTING LitBank annotation (coref clusters,
who-did-what events) or a TRANSPARENT, auditable derivation (past-perfect anteriority; explicit
causal connectives). Writes only to data/exp_situation_model_qa_v1/. Does NOT modify hdlab/.

INSTRUMENT-COUPLING FIX (2026-08-31, strategy Q111 -- the CORRECT BASELINE every solver needs): the
instrument now scores the CAPABLE reader by default (build_reader: tense_agnostic_events + preserve_tense
+ timeline_register ON) and reads the TEMPORAL answer off the whole-passage register sm.timeline_order.
WHY: the original ran the DEFAULT (weak) reader and read temporal off sm.events tense, which the
tense_agnostic_events keystone rewrites to a placeholder -> temporal questions collapse 86->0 and the
readout degrades (an INSTRUMENT artifact, not a reader regression). sm.timeline_order is a tense-
independent constraint-graph toposort, so it survives the keystone. Pass capable=False to reproduce the
historical default-reader run. Causation stays tense-independent already (connective gold + sm.causal_links)
so it does not need the capable path; spaCy-requiring causation_typed is excluded (remote-safe).

Run: .venv/Scripts/python.exe experiments/exp_situation_model_qa_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_situation_model_qa_v1.py --run [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import SituationReader, SituationModel  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
import experiments.exp_name_entity_clustering_v1 as NC  # noqa: E402
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer  # noqa: E402

# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/litbank/coref/conll
OUTDIR = os.path.join(REPO, "data/exp_situation_model_qa_v1")
WDW_GOLD = os.path.join(REPO, "data/litbank/who_did_what_events.json")
CONLL_DIR = NC.CONLL_DIR

_PRONOUNS = {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "its",
             "himself", "herself", "themselves", "itself"}
_STOP = {"who", "what", "when", "where", "why", "did", "does", "do", "is", "was", "the", "a", "an",
         "in", "of", "to", "at", "on", "and", "or", "refer", "sentence", "happen", "before", "after",
         "caused", "cause", "character", "main", "most", "mentioned", "?"}


# ===========================================================================
# helpers: canonical entity naming off the accumulated model
# ===========================================================================
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _cluster_name(sm: SituationModel, cluster: int) -> Optional[str]:
    """Canonical NAME of a coref cluster read off the model's entities: the longest distinct
    non-pronoun head. None if the cluster is all-pronoun (no nameable answer)."""
    for e in sm.entities:
        if e.cluster == cluster:
            heads = [h for h in e.heads if _norm(h) and _norm(h) not in _PRONOUNS]
            if not heads:
                return None
            return max(heads, key=lambda h: len(_norm(h)))
    return None


def _named_clusters(sm: SituationModel) -> Dict[int, str]:
    """{cluster -> canonical name} for every cluster that has a nameable head."""
    out = {}
    for e in sm.entities:
        nm = _cluster_name(sm, e.cluster)
        if nm is not None:
            out[e.cluster] = nm
    return out


def _content(q_tokens: List[str]) -> List[str]:
    return [t for t in q_tokens if t not in _STOP and t not in _PRONOUNS and _norm(t)]


# ===========================================================================
# THE ROUTER: SOFT, PARALLEL, CUE-BASED dimension scoring (brain-faithful, not a keyword switch).
# ===========================================================================
# Research drill (research_situation_model_qa_brain_mechanism_2026-08-30.md) verdict: the brain has
# NO discrete router. Dimension->subsystem specialization is real (PPA=where, hippocampal time-cells=
# when, pSTS=who-did-what, mPFC=why, TPJ=who-believes) but the subsystems run IN PARALLEL, bound into
# ONE situation model, and the matching content wins a GRADED CUE-BASED RACE (Lewis & Vasishth 2005
# content-addressable retrieval; "there is no router, there is a cue and a race"). A question means
# WHAT WOULD COUNT AS AN ANSWER (Roberts 2012 QUD; Groenendijk & Stokhof answerhood), so paraphrases
# induce the SAME query -- generalization must be paraphrase-invariant, which a keyword switch is not.
#
# So route_scores() emits a GRADED activation PER DIMENSION from a transparent cue->dimension table
# over the question's FEATURE SET (wh-word + lemmatized relational cues + a pronoun-focus flag), NOT
# exact substrings. route() = argmax with a threshold (abstain if nothing clears = the FOK gate).
DIMENSIONS = ("coref", "events", "salience", "temporal", "causal", "location", "belief", "state")

# each cue votes for a dimension (soft weight). Multiple cues -> parallel votes -> multi-dim capable.
# These are RELATIONAL/QUD cues (lemmas), not fixed question phrasings -> paraphrase-robust by design.
CUE_DIM = {
    # TIME: before/after AND their paraphrases (earlier/later/precede/follow/prior/subsequently...)
    "before": "temporal", "after": "temporal", "earlier": "temporal", "later": "temporal",
    "precede": "temporal", "preceded": "temporal", "follow": "temporal", "followed": "temporal",
    "prior": "temporal", "subsequently": "temporal", "first": "temporal", "then": "temporal",
    "order": "temporal", "sequence": "temporal", "when": "temporal",
    # CAUSATION: because/so AND paraphrases (cause/reason/why/lead-to/result/on-account-of/owing...)
    "caused": "causal", "cause": "causal", "because": "causal", "reason": "causal", "why": "causal",
    "result": "causal", "led": "causal", "lead": "causal", "owing": "causal", "account": "causal",
    "due": "causal", "made": "causal", "prompted": "causal", "triggered": "causal",
    # ENTITY/coref reference: refer/denote/mean/who-is + a pronoun in the question
    "refer": "coref", "denote": "coref", "denotes": "coref", "mean": "coref", "means": "coref",
    "antecedent": "coref", "pronoun": "coref", "_haspron": "coref",
    # ENTITY salience / protagonist
    "main": "salience", "protagonist": "salience", "hero": "salience", "central": "salience",
    "most": "salience", "mentioned": "salience", "important": "salience", "focal": "salience",
    # SPACE (organ is an island, not in the live model -> will abstain at readout)
    "where": "location", "located": "location", "place": "location", "room": "location",
    "location": "location",
    # ToM belief (island)
    "believe": "belief", "believes": "belief", "think": "belief", "thinks": "belief",
    "thought": "belief", "know": "belief", "knows": "belief", "assume": "belief",
}
# wh-word prior (soft): who -> events/coref/salience; which -> coref; where/when/why route by cue.
WH_PRIOR = {
    "who": {"events": 0.6, "coref": 0.3, "salience": 0.2},
    "which": {"coref": 0.5},
    "what": {"events": 0.3, "causal": 0.2},
    "where": {"location": 0.9}, "when": {"temporal": 0.9}, "why": {"causal": 0.9},
}
ROUTE_THRESHOLD = 0.25   # FOK gate: below this the top dimension is not confidently selected


# --- the COPULAR-FRAME detector: a "what/who is X" / "is X a Y" question asks the entity's STATE ------------
# Brain-faithful (Higgins 1979; the copula is a functional carrier, the meaning is the predication of an
# ATTRIBUTE to the subject entity -> the entity-state dimension). Structural, not a cue word, so it generalizes
# to unseen holders/properties. Gated to NOT steal the existing dims: not 'where/when/why' (own dims), not a
# salience question ('who is the MAIN character'), not a pronoun holder ('who is he' = coref), not a question
# with another main/mental/causal/temporal verb ('what does X believe', 'what caused X').
_STATE_BE = {"is", "was", "are", "were", "be", "been", "being", "am", "'s", "'re", "'m"}
_SALIENCE_CUE = {"main", "most", "protagonist", "central", "hero", "focal", "important"}


def _is_state_frame(question: str) -> bool:
    toks = re.findall(r"[a-z']+", question.lower())
    if len(toks) < 3:
        return False
    if any(t in _SALIENCE_CUE for t in toks):
        return False                                   # 'who is the main character' -> salience
    if any(t in _MENTAL_VERBS or t in _CAUSAL_VERBS or t in _TEMPORAL_REL for t in toks):
        return False                                   # another dim owns it (believe/caused/before...)
    # WH copular frame: what/who + BE + (det)? + a holder, copula as the main predicate. The wh-word sets the
    # answer-type (Higgins): 'WHAT is X' asks a PROPERTY/is-a of X -> the entity-state store, for ANY holder
    # (incl. a pronoun: "what is it" -> the property bound to the discourse referent). 'WHO is X' asks IDENTITY;
    # a PRONOUN holder ("who is he") is a coreference question, NOT a state query -> defer to coref.
    if toks[0] in ("what", "who") and toks[1] in _STATE_BE:
        j = 2
        while j < len(toks) and toks[j] in ("the", "a", "an"):
            j += 1
        if j >= len(toks):
            return False
        holder = toks[j].strip("'")                   # strip quotes so 'he' is still caught as a pronoun
        if not holder:
            return False
        if toks[0] == "what":
            return True                               # property query -> state, any holder
        return holder not in _PRONOUNS                # 'who is <name>' -> state; 'who is he' -> coref
    # YES/NO copular frame: is/was/are/were + holder + a/an + property
    if toks[0] in _STATE_BE and any(t in ("a", "an") for t in toks[2:]):
        return True
    return False


def _q_features(question: str) -> Tuple[str, List[str]]:
    toks = re.findall(r"[a-z']+", question.lower())
    wh = next((t for t in toks if t in ("who", "what", "where", "when", "why", "which", "how")), "")
    cues = [t for t in toks if t in CUE_DIM]
    if any(t in _PRONOUNS for t in toks):
        cues.append("_haspron")
    return wh, cues


def route_scores(question: str, cue_dim: Dict[str, str] = None,
                 wh_prior: Dict[str, dict] = None) -> Dict[str, float]:
    """GRADED activation per dimension (the cue-based race). Soft + parallel: every cue votes; the
    wh-word adds a graded prior. cue_dim/wh_prior are injectable so the info-free twin can pass a
    SHUFFLED table (cues vote for the wrong dimension) and collapse routing."""
    cue_dim = CUE_DIM if cue_dim is None else cue_dim
    wh_prior = WH_PRIOR if wh_prior is None else wh_prior
    wh, cues = _q_features(question)
    act = defaultdict(float)
    for c in cues:
        act[cue_dim[c]] += 1.0
    for dim, w in wh_prior.get(wh, {}).items():
        act[dim] += w
    # normalize to a distribution (graded emphasis, not a hard gate)
    tot = sum(act.values())
    if tot > 0:
        for d in list(act):
            act[d] /= tot
    return dict(act)


def route(question: str, cue_dim: Dict[str, str] = None, wh_prior: Dict[str, dict] = None,
          threshold: float = ROUTE_THRESHOLD, state_frame: bool = True) -> Optional[str]:
    """argmax of the cue-based race, gated by a retrieval threshold (abstain -> None if nothing
    clears -- the feeling-of-knowing gate). The COPULAR frame ('what/who is X' / 'is X a Y') routes to
    the entity-STATE dim FIRST (structural, not cue-based); state_frame=False ablates it (the copular
    question then falls through to events -> misroutes, the routing control that proves the frame is load-bearing)."""
    if state_frame and _is_state_frame(question):
        return "state"
    act = route_scores(question, cue_dim, wh_prior)
    if not act:
        return None
    dim, a = max(act.items(), key=lambda kv: kv[1])
    return dim if a >= threshold else None


# ===========================================================================
# THE WH-ONTOLOGY ROUTER (the brain-faithful generalization engine -- 2nd drill,
# research_situation_model_qa_qud_paraphrase_2026-08-30.md).
# ===========================================================================
# STRONGLY PINNED: a question decomposes UNIVERSALLY into interrogative-force + an ontological
# ANSWER-TYPE carried by the wh-word (who->ENTITY, where->PLACE, when->TIME, why->CAUSE -- a language
# universal, present even in sign languages; Cysouw; Ginzburg co-propositionality). Paraphrases
# collapse because each INDEPENDENTLY yields the same answer-type -- so this generalizes to UNSEEN
# wordings, which a cue-table cannot. When the wh-word UNDERDETERMINES the type (what/which), the
# HEAD NOUN carries it (Li & Roth 2002; "in what SPOT" -> spot is a location hyponym) -- resolved here
# by WordNet lexname/hypernymy (glass-box, nltk, NO LLM), the drill's recommended head-noun resolver.
_WH_TYPE = {"who": "entity", "whom": "entity", "whose": "entity", "which": "entity",
            "where": "location", "when": "temporal", "why": "causal", "how": "manner", "what": None}
_LEXNAME_TYPE = {"noun.location": "location", "noun.time": "temporal", "noun.person": "entity",
                 "noun.group": "entity", "noun.motive": "causal", "noun.event": "events",
                 "noun.act": "events"}
_CAUSAL_VERBS = {"cause", "caused", "lead", "led", "result", "resulted", "because", "prompt",
                 "prompted", "trigger", "triggered", "made", "make", "led"}
_MENTAL_VERBS = {"believe", "believes", "think", "thinks", "thought", "know", "knows", "assume",
                 "suppose", "supposes", "reckon"}
_TEMPORAL_REL = {"before", "after", "earlier", "later", "precede", "preceded", "precedes", "follow",
                 "followed", "follows", "first", "then", "prior", "subsequently"}
_wn_cache: Dict[str, Optional[str]] = {}


def _wn_lexname_type(word: str) -> Optional[str]:
    """Ontological answer-type of a NOUN via WordNet lexname (glass-box, no LLM). 'spot'->location,
    'moment'->time, 'reason'->motive/cause, 'individual'->person. None if not a mapped noun."""
    if word in _wn_cache:
        return _wn_cache[word]
    t = None
    try:
        from nltk.corpus import wordnet as wn
        best = None
        for syn in wn.synsets(word, pos=wn.NOUN)[:3]:
            ln = syn.lexname()
            if ln in _LEXNAME_TYPE:
                best = _LEXNAME_TYPE[ln]; break
            # hypernym chain fallback for causal/place nouns
            names = {h.name().split(".")[0] for path in syn.hypernym_paths() for h in path}
            if {"reason", "cause", "motivation", "grounds"} & names:
                best = "causal"; break
            if {"location", "region", "point"} & names:
                best = "location"; break
        t = best
    except Exception:
        t = None
    _wn_cache[word] = t
    return t


def _type_to_dim(atype: str, question: str) -> Optional[str]:
    """Answer-type -> the SituationModel dimension. ENTITY sub-routes by structure (a pronoun focus ->
    coref/which-'she'; 'main/most' -> salience; else who-did-what events). manner -> None (no dim)."""
    if atype in ("location", "temporal", "causal", "events"):
        return atype
    if atype == "entity":
        ql = question.lower()
        if any(t in _PRONOUNS for t in re.findall(r"[a-z]+", ql)):   # [a-z]+ strips quotes: 'her'->her
            return "coref"
        if "main" in ql or "most" in ql or "protagonist" in ql:
            return "salience"
        return "events"
    return None


def _head_noun_type_after(toks: List[str], wh_i: int) -> Optional[str]:
    """The ontological type of the HEAD NOUN of the wh-phrase (Li & Roth 2002: for what/which the head
    noun determines the answer type -- 'what MOMENT'->time, 'which SITE'->location). The head noun is
    the token IMMEDIATELY after the wh-word (skipping a determiner); if that slot is a verb/stopword the
    question is verb-headed ('what CAUSED X') -> return None so the predicate frame handles it."""
    j = wh_i + 1
    while j < len(toks) and toks[j] in ("the", "a", "an"):
        j += 1
    if j < len(toks) and toks[j] not in _STOP and toks[j] not in _PRONOUNS:
        return _wn_lexname_type(toks[j])
    return None


def wh_ontology_scores(question: str) -> Dict[str, float]:
    """Soft dimension activation = wh-word answer-type (+ head-noun override for underdetermined
    what/which) + predicate/relational frames. Paraphrase-invariant by construction: keys on the
    ONTOLOGICAL answer-type, not cue phrases, so it generalizes to unseen wordings."""
    toks = re.findall(r"[a-z']+", question.lower())
    wh, wh_i = "", -1
    for i, t in enumerate(toks):
        if t in _WH_TYPE:
            wh, wh_i = t, i
            break
    act = defaultdict(float)
    at = _WH_TYPE.get(wh)
    if at in ("location", "temporal", "causal"):
        act[at] += 1.0
    elif at == "entity":                              # who/whom/whose/which
        if wh in ("who", "whom"):                     # unambiguously a person -> entity
            d = _type_to_dim("entity", question)      # (coref if pronoun / salience / events)
            if d:
                act[d] += 1.0
        else:                                         # which/whose -> the HEAD NOUN determines the type
            hn = _head_noun_type_after(toks, wh_i)    # (else defer to predicate frame / final default)
            if hn:
                d = _type_to_dim(hn, question)
                if d:
                    act[d] += 1.0
    elif wh == "what":                                # underdetermined -> head noun, else predicate frame
        hn = _head_noun_type_after(toks, wh_i)
        if hn:
            d = _type_to_dim(hn, question)
            if d:
                act[d] += 1.0
    # predicate/relational frames (the verb/relation evokes the dimension -- drill fix #5; handles
    # 'what does X believe' -> belief, 'X before/after Y' -> temporal, 'what caused X' -> causal)
    if any(t in _CAUSAL_VERBS for t in toks):
        act["causal"] += 1.0
    if any(t in _MENTAL_VERBS for t in toks):
        act["belief"] += 1.0
    if any(t in _TEMPORAL_REL for t in toks):
        act["temporal"] += 1.0
    # defaults: an unresolved what/which still routes (what -> event; which -> coref if a pronoun)
    if not act and wh in ("what", "which"):
        d = _type_to_dim("events" if wh == "what" else "entity", question)
        if d:
            act[d] += 0.5
    tot = sum(act.values())
    if tot > 0:
        for d in list(act):
            act[d] /= tot
    return dict(act)


def wh_ontology_route(question: str, threshold: float = ROUTE_THRESHOLD,
                      state_frame: bool = True) -> Optional[str]:
    if state_frame and _is_state_frame(question):     # the copular predication frame -> entity-state dim
        return "state"
    act = wh_ontology_scores(question)
    if not act:
        return None
    dim, a = max(act.items(), key=lambda kv: kv[1])
    return dim if a >= threshold else None


# ===========================================================================
# THE READOUTS: answer a question OFF THE ACCUMULATED MODEL (never re-reading)
# ===========================================================================
class SituationQA:
    """Glass-box QA interface over an already-built SituationModel. answer(q) routes q to a dimension
    and reads the answer off the accumulated model fields -- entities / coref_resolutions / events /
    timeline_frames / causal_links. Returns a string answer, or None to ABSTAIN (dimension not in the
    live model). This is the proposed situation_reader query API, proven here in experiments/."""

    def __init__(self, sm: SituationModel):
        self.sm = sm
        self.names = _named_clusters(sm)

    # -- ENTITIES / coref: "who does <pron> (sent N) refer to?" -> resolved cluster name --
    def _answer_coref(self, q: dict) -> Optional[str]:
        # q carries the pronoun-target index into sm.coref_resolutions (the accumulated resolution).
        i = q.get("res_idx")
        if i is None or not (0 <= i < len(self.sm.coref_resolutions)):
            return None
        rc = self.sm.coref_resolutions[i].resolved_cluster
        return self.names.get(rc)

    # -- EVENTS / who-did-what: "who <gov_verb>ed?" -> the event's agent (gov_verb gold is a LEMMA) --
    def _answer_events(self, q: dict) -> Optional[str]:
        pred = q.get("pred")
        want = q.get("slot", "agent")
        plem = lemma_verb(pred) if pred is not None else None
        best = None
        for ev in self.sm.events:
            if pred is not None and lemma_verb(ev.predicate) != plem and _norm(ev.predicate) != _norm(pred):
                continue
            head = ev.agent if want == "agent" else ev.patient
            if head and head != "?":
                best = head
        return best

    # -- ENTITIES / salience: "who is the main character?" -> most-mentioned cluster name --
    def _answer_salience(self, q: dict) -> Optional[str]:
        cand = [(e.n_mentions, e.cluster) for e in self.sm.entities
                if self.names.get(e.cluster)]
        if not cand:
            return None
        cand.sort(reverse=True)
        return self.names.get(cand[0][1])

    # -- TIME: "did <A> happen before or after <B>?" -> whole-passage chrono order --
    def _answer_temporal(self, q: dict) -> Optional[str]:
        a, b = q.get("a"), q.get("b")
        # PRIMARY (the CORRECT temporal field -- instrument-coupling fix, 2026-08-31): the whole-passage
        # chronological register sm.timeline_order (populated when the reader is built with
        # timeline_register=True). It is a constraint-graph toposort of {lemma, chrono_rank, text_rank}
        # INDEPENDENT of per-event tense, so it is NOT erased when tense_agnostic_events rewrites event
        # tense to a placeholder (the defect that collapses the naive event-tense readout to 0.36). It is
        # also strictly more complete than the had-gated per-sentence frames below (whole-passage + cross-
        # sentence + connective reorderings). ADDITIVE: when timeline_order is empty (default reader) this
        # branch is skipped -> byte-identical to the original frames/tense fallback.
        order = getattr(self.sm, "timeline_order", None)
        if order:
            rank: Dict[str, int] = {}
            for e in order:
                rank.setdefault(_norm(e.get("lemma")), e.get("chrono_rank"))
            ra, rb = rank.get(_norm(a)), rank.get(_norm(b))
            if ra is not None and rb is not None and ra != rb:
                return "before" if ra < rb else "after"
        # FALLBACK 1: the had-gated per-sentence flashback frame whose chrono_order contains both
        for fr in self.sm.timeline_frames:
            order = [_norm(x) for x in fr.chrono_order]
            if _norm(a) in order and _norm(b) in order:
                return "before" if order.index(_norm(a)) < order.index(_norm(b)) else "after"
        # FALLBACK 2: event-tense anteriority accumulated in events (past-perfect precedes past). This is
        # the path that DEGRADES under tense_agnostic_events alone (all events -> placeholder SIMPLE_PAST);
        # it is why the FIX reads sm.timeline_order first. Correct on the default reader / preserve_tense.
        rank = {"PAST_PERFECT": 0, "MODAL_SUBORDINATE": 1, "PARTICIPIAL": 1, "PAST": 2,
                "PRESENT": 3}
        ta = tb = None
        for ev in self.sm.events:
            if _norm(ev.predicate) == _norm(a):
                ta = rank.get(str(ev.tense), 2)
            if _norm(ev.predicate) == _norm(b):
                tb = rank.get(str(ev.tense), 2)
        if ta is None or tb is None:
            return None
        return "before" if ta < tb else ("after" if ta > tb else None)

    # -- CAUSATION: "what caused <outcome>?" -> the cause off causal_links --
    def _answer_causal(self, q: dict) -> Optional[str]:
        outcome = q.get("outcome")
        for cl in self.sm.causal_links:
            if _norm(cl.outcome) == _norm(outcome):
                return cl.cause
        return None

    # -- ENTITY STATE: "what/who is X" / "is X a Y" -> read the is-a/attribute off sm.state_register --
    def _answer_state(self, q: dict):
        """COPULAR is-a/attribute read-out (bind_entity_states): the set of state values HELD by the holder,
        off sm.state_register.state_at (never re-reading). None -> abstain (register absent = flag off, the
        base-reader zero). Keys on the holder SURFACE token (within-clause; cross-sentence canonical binding is
        the filed follow-on). From the owner-DONE the_reader_has_no_copular_is_a_binding_schema."""
        reg = getattr(self.sm, "state_register", None)
        holder = q.get("holder")
        if reg is None or holder is None:
            return None
        vals = reg.state_at(str(holder).lower())
        return set(vals) if vals else None

    # -- NOT IN THE LIVE MODEL: the organ exists but the reader populates no such field --
    def _answer_absent(self, q: dict) -> Optional[str]:
        return None

    def readout(self, dim: Optional[str], q: dict) -> Optional[str]:
        """Read the answer off the accumulated model for a routed dimension (None -> abstain)."""
        if dim is None:
            return None
        fn = {"coref": self._answer_coref, "events": self._answer_events,
              "salience": self._answer_salience, "temporal": self._answer_temporal,
              "causal": self._answer_causal, "location": self._answer_absent,
              "belief": self._answer_absent, "state": self._answer_state}.get(dim)
        return fn(q) if fn else None

    def answer(self, question: str, q: dict, cue_dim=None, wh_prior=None,
               threshold: float = ROUTE_THRESHOLD, router=None) -> Tuple[Optional[str], Optional[str]]:
        """Returns (routed_dimension, answer_or_None). dim=None or answer=None means ABSTAIN --
        distinguished downstream as never-tracked (location/belief) vs tracked-but-absent. `router`
        overrides the default cue-table route (used to compare cue-table vs wh-ontology end-to-end)."""
        dim = router(question) if router is not None else route(question, cue_dim, wh_prior, threshold)
        return dim, self.readout(dim, q)


# ===========================================================================
# THE FLOORS (re-reading, never the model) and the info-free TWIN
# ===========================================================================
def floor_wordoverlap(question: str, candidates: List[str]) -> Optional[str]:
    """RETRIEVAL floor (brief-specified): pick the candidate string with max token overlap with the
    QUESTION; ties broken by earliest candidate order (neutral, does NOT encode the answer)."""
    qtok = set(_content(re.findall(r"[a-z0-9]+", question.lower())))
    best, best_ov = None, -1
    for c in candidates:
        ov = len(qtok & set(_content(_norm(c).split())))
        if ov > best_ov:
            best, best_ov = c, ov
    return best


def _sm_qa_dim_fns(qa: "SituationQA"):
    return {"coref": qa._answer_coref, "events": qa._answer_events, "salience": qa._answer_salience,
            "temporal": qa._answer_temporal, "causal": qa._answer_causal,
            "location": qa._answer_absent, "belief": qa._answer_absent}


# ===========================================================================
# THE READER THE INSTRUMENT SCORES (the correct baseline -- capable by default)
# ===========================================================================
def build_reader(gaz, capable: bool = True) -> SituationReader:
    """Build the reader this QA instrument scores. AS OF 2026-09-03 the validated extraction dimensions are
    DEFAULT-ON in SituationReader (the owner-authorized flag flip: reader-QA agg 0.2903->0.3598), so
    `capable=True` (the DEFAULT) is simply the default reader = the fully-capable reader (tense_agnostic_events
    + preserve_tense + timeline_register [the temporal trio] + role_route='wired' + np_head_reduce + predict_revise
    + verb_subcat_gate + predict_surprisal + track_space + track_belief + track_world_state/densify + bind_event_tokens).
    `capable=False` = the HISTORICAL weak reader (every capability flag explicitly OFF), kept ONLY for the
    before/after comparison -- it must set the flags OFF explicitly now that they are default-ON.
    NOTE (temporal coupling, still true): temporal answers are read off sm.timeline_order (a tense-independent
    toposort), NOT the naive sm.events tense, because the keystone rewrites tense to a placeholder. spaCy-requiring
    causation_typed / spacy_pred_gate stay OFF (remote-safe invariant); parser_arceager stays OFF (19c-negative)."""
    if not capable:
        # the historical WEAK reader -- ONE canonical all-off factory (derives from SituationReader.
        # CAPABILITY_FLAGS, so a future default flip needs no change here).
        return SituationReader.all_capabilities_off(gaz=gaz)
    # bind_entity_states=True (this problem, wire_the_copular_state_qa_consumer_...): the consumer's reader now
    # populates sm.entity_states + sm.state_register so the STATE dimension can read "what is X" off the model.
    # ADDITIVE -- the copular read touches only entity_states/state_register (no other dimension changes), so the
    # 4 scored LitBank dims are byte-identical off vs on (no-regression, witnessed). +~5ms/read (measured).
    return SituationReader(gaz=gaz, bind_entity_states=True)


# ===========================================================================
# GOLD CONSTRUCTION (existing LitBank gold + transparent derivations)
# ===========================================================================
def load_docs(n: Optional[int]) -> List[str]:
    data = json.load(open(WDW_GOLD, encoding="utf-8"))
    docs = [rec["doc"] for rec in data]
    return docs[:n] if n else docs


def build_coref_questions(sm: SituationModel, min_sent_dist: int = 1) -> List[dict]:
    """WHICH-ENTITY questions from the reader's OWN accumulated coref_resolutions (existing LitBank
    coref gold). One question per cross-sentence pronoun target whose gold cluster is NAMEABLE."""
    names = _named_clusters(sm)
    qs = []
    for i, r in enumerate(sm.coref_resolutions):
        if r.sent_dist < min_sent_dist:
            continue
        gold_name = names.get(r.gold_cluster)
        if gold_name is None:
            continue
        qs.append({
            "dim": "coref", "res_idx": i,
            "question": f"Who does '{r.pronoun}' refer to ?",
            "gold": gold_name,
            "candidates": sorted(set(names.values())),
            "pron": r.pronoun, "sent_idx": r.sent_idx,
        })
    return qs


def build_salience_question(sm: SituationModel) -> List[dict]:
    """MAIN-ENTITY question: gold = the coref cluster with the MOST gold mentions (transparent from
    LitBank coref gold via the model's gold-cluster mention counts). One per doc."""
    names = _named_clusters(sm)
    # gold mention counts per cluster come from the model's entities (n_mentions is gold-cluster grain)
    gold_counts = [(e.n_mentions, e.cluster) for e in sm.entities if names.get(e.cluster)]
    if not gold_counts:
        return []
    gold_counts.sort(reverse=True)
    gold_name = names[gold_counts[0][1]]
    return [{
        "dim": "salience",
        "question": "Who is the main character ?",
        "gold": gold_name,
        "candidates": sorted(set(names.values())),
    }]


def build_events_questions(sm: SituationModel, rec: dict) -> List[dict]:
    """WHO-DID-WHAT questions from the LitBank who-did-what gold stream (existing gold). For each
    SUBJECT mention with a gov_verb, "Who <gov_verb>ed?" -> gold = the subject head."""
    names = _named_clusters(sm)
    qs = []
    for m in rec.get("stream", []):
        if m.get("role") != "SUBJECT" or not m.get("gov_verb"):
            continue
        gov = m["gov_verb"]
        gold = m["head_text"]
        qs.append({
            "dim": "events",
            "question": f"Who did {gov} ?",
            "pred": gov, "slot": "agent",
            "gold": gold,
            "candidates": sorted(set(list(names.values()) + [gold])),
        })
    return qs


def build_temporal_questions(sm: SituationModel) -> List[dict]:
    """WHEN / before-after questions from PAST-PERFECT ANTERIORITY (Reichenbach: 'had X-ed' denotes a
    time BEFORE the surrounding simple-past events -- a grammatical fact, transparent + auditable, NOT
    an LLM label). Gold pairs (P=past-perfect event, Q=simple-past event in the same passage): P
    happened BEFORE Q. HONEST CAVEAT: the model's timeline and this gold share the tense signal, so
    this tests the QA CLAIM (route a before/after question to the accumulated temporal index; the
    word-order floor mis-orders flashbacks) NOT an independent temporal-reasoning claim."""
    pp = [ev for ev in sm.events if str(ev.tense) == "PAST_PERFECT"]
    past = [ev for ev in sm.events if str(ev.tense) == "SIMPLE_PAST"]
    qs = []
    for p in pp:
        # pair each past-perfect event with its NEAREST simple-past event only (the local flashback
        # contrast) -- avoids a combinatorial blowup that would dominate the aggregate with redundant pairs
        cands = [q for q in past if _norm(q.predicate) != _norm(p.predicate)]
        if not cands:
            continue
        q = min(cands, key=lambda e: abs(e.global_idx - p.global_idx))
        # ask BOTH orders so text-position cannot trivially win; gold from past-perfect anteriority
        qs.append({"dim": "temporal", "question": f"Did {p.predicate} happen before or after {q.predicate} ?",
                   "a": p.predicate, "b": q.predicate, "gold": "before",
                   "p_gidx": p.global_idx, "q_gidx": q.global_idx})
        qs.append({"dim": "temporal", "question": f"Did {q.predicate} happen before or after {p.predicate} ?",
                   "a": q.predicate, "b": p.predicate, "gold": "after",
                   "p_gidx": p.global_idx, "q_gidx": q.global_idx})
    return qs


def build_state_questions(sm) -> List[dict]:
    """COPULAR is-a/attribute questions from the reader's OWN predicational entity_states (bind_entity_states).
    "What is {holder} ?" (gold = property) + "Is {holder} a {property} ?" (yes/no). CAVEAT: on LitBank there is
    NO independent copular gold (no gold deprels), so this gold is READER-DERIVED -> it measures COVERAGE /
    round-trip on real 19c prose (a live-fires demonstration), NOT a floor-beating capability claim. The
    powered, NON-CIRCULAR capability number is on the copular problem's UD-EWT gold (exp_situation_model_state_qa_v1
    / state_qa_dimension): gold from GOLD deprels, floor = most-recent-noun (0.503), shuffle twin (0.452)."""
    qs = []
    for s in getattr(sm, "entity_states", []) or []:
        if s.htype not in ("pred_adj", "pred_nom"):     # predicational only (identity -> coref-merge follow-on)
            continue
        qs.append({"dim": "state", "holder": s.holder, "gold": s.property,
                   "question": f"What is {s.holder} ?", "sent_idx": s.sent_idx})
    return qs


_CAUSE_AFTER = {"because", "since"}         # "X because Y" -> Y (after the connective) is the CAUSE
_CAUSE_BEFORE = {"so", "therefore", "thus", "hence", "consequently"}  # "X so Y" -> X (before) is CAUSE


def build_causal_questions(sm: SituationModel, sents: List[List[str]]) -> List[dict]:
    """WHY / cause questions with a TEXT-DERIVED, NON-CIRCULAR gold: the cause/outcome DIRECTION comes
    from the explicit connective's GRAMMAR (Reichenbach/discourse: 'X because Y' -> Y causes X; 'X so Y'
    -> X causes Y), read off the raw token stream -- NOT off the reader's causal_net (which is what the
    readout consults, so gold != readout source). The readout (_answer_causal) returns the reader's
    causal_link cause; scoring it against the grammar-direction gold is a real test of whether the
    reader assigns the right cause/outcome direction. HONEST CAVEAT: the reader's causal organ is
    connective-reducible (its own ORGAN_MAP caveat), so a high score here means it recovers the text's
    connective structure -- a connective detector, not force-dynamics reasoning."""
    ev_by_sent: Dict[int, list] = defaultdict(list)
    for ev in sm.events:
        ev_by_sent[ev.sent_idx].append(ev)
    qs = []
    for si, toks in enumerate(sents):
        low = [t.lower() for t in toks]
        for conn in (_CAUSE_AFTER | _CAUSE_BEFORE):
            if conn not in low:
                continue
            ci = low.index(conn)
            # EventRecord has no within-sentence token index; locate each predicate by its surface pos
            located = []
            for e in ev_by_sent.get(si, []):
                pl = str(e.predicate).lower()
                if pl in low:
                    located.append((low.index(pl), e))
            located.sort(key=lambda pe: pe[0])
            pre = [e for pos, e in located if pos < ci]
            post = [e for pos, e in located if pos > ci]
            if not pre or not post:
                continue
            preverb, postverb = pre[-1].predicate, post[0].predicate
            if _norm(preverb) == _norm(postverb):
                continue
            cause, outcome = (postverb, preverb) if conn in _CAUSE_AFTER else (preverb, postverb)
            qs.append({"dim": "causal", "question": f"What caused {outcome} ?",
                       "outcome": outcome, "gold": cause,
                       "candidates": sorted({e.predicate for _p, e in located})})
            break
    return qs


def floor_adjacency_causal(q: dict, sm: SituationModel) -> Optional[str]:
    """STRONGEST trivial causal floor: the event IMMEDIATELY BEFORE the outcome in the event stream
    (recency/adjacency 'the last thing that happened caused it'). The reader's connective link must
    beat this to show connective structure -- not mere adjacency -- carries the answer."""
    outcome = _norm(q["outcome"])
    prev = None
    for ev in sm.events:
        if _norm(ev.predicate) == outcome:
            return prev
        prev = ev.predicate
    return None


def build_absent_questions(sm: SituationModel) -> List[dict]:
    """NEVER-TRACKED dimensions (SPACE / ToM-belief): the organs exist as files but are NOT wired into
    the live SituationModel, so the faithful behavior is HARD ABSTAIN (Koriat FOK; never-tracked !=
    tracked-but-absent). One where + one believe per doc: correct behavior = the model ABSTAINS."""
    names = _named_clusters(sm)
    prot = None
    cand = [(e.n_mentions, e.cluster) for e in sm.entities if names.get(e.cluster)]
    if cand:
        cand.sort(reverse=True)
        prot = names[cand[0][1]]
    if prot is None:
        return []
    return [
        {"dim": "location", "question": f"Where is {prot} ?", "gold": None, "expect_abstain": True},
        {"dim": "belief", "question": f"What does {prot} believe ?", "gold": None, "expect_abstain": True},
    ]


# ===========================================================================
# STRONG per-dimension floors (the strongest trivial method actually run, re-reading only)
# ===========================================================================
def _conll_sents(path: str) -> List[List[str]]:
    """[[token per sentence]] from the CoNLL token column (col 3) -- same tokenization the reader uses."""
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
            continue
        cur.append(line.rstrip("\n").split("\t")[3])
    if cur:
        sents.append(cur)
    return sents


def floor_mostfreq_coref(mentions: List[dict], names: Dict[int, str]) -> Optional[str]:
    """STRONG coref floor #2: always answer the MOST-MENTIONED named entity (the protagonist) -- a
    pronoun in narrative most often refers to the protagonist, so this is a strong content-free
    baseline the accumulated coref must beat to show it uses the pronoun, not just base rate."""
    cnt = Counter(m["cluster"] for m in mentions if not m.get("is_pronoun"))
    for c, _n in cnt.most_common():
        if names.get(c):
            return names[c]
    return None


def floor_recency_coref(target_mention: dict, mentions: List[dict], names: Dict[int, str]) -> Optional[str]:
    """STRONGEST coref floor: the nearest PRECEDING non-pronoun mention (recency / proximity). This
    is the trivial re-reading heuristic the accumulated coref model must beat."""
    ts, tw = target_mention["sent_idx"], target_mention.get("wtok_start", 0)
    best = None
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        if (m["sent_idx"], m.get("wtok_start", 0)) <= (ts, tw):
            if best is None or (m["sent_idx"], m.get("wtok_start", 0)) > (best["sent_idx"], best.get("wtok_start", 0)):
                best = m
    if best is None:
        return None
    return names.get(best["cluster"])


def floor_textorder_temporal(q: dict, sm: SituationModel) -> Optional[str]:
    """WORD-ORDER floor for before/after: whichever predicate appears FIRST in the text (by event
    global order) is 'before'. This is what re-reading/word-position gives -- and it is WRONG on
    flashbacks (past-perfect appears later but happened earlier), which is the whole point."""
    a, b = _norm(q["a"]), _norm(q["b"])
    pa = pb = None
    for ev in sm.events:
        if _norm(ev.predicate) == a and pa is None:
            pa = ev.global_idx
        if _norm(ev.predicate) == b and pb is None:
            pb = ev.global_idx
    if pa is None or pb is None:
        return None
    return "before" if pa < pb else "after"


# ===========================================================================
# matching + the exact-keyword router (the brittle baseline for the generalization test)
# ===========================================================================
def _match(pred: Optional[str], gold, dim: str) -> bool:
    if gold in ("before", "after"):
        return pred == gold
    if pred is None or gold is None:
        return False
    pt = set(_content(_norm(pred).split())) or set(_norm(pred).split())
    gt = set(_content(_norm(gold).split())) or set(_norm(gold).split())
    return len(pt & gt) > 0


def hard_route(question: str) -> Optional[str]:
    """The BRITTLE exact-keyword switch (my first draft, the OUR-INVENTION the drill flagged) -- kept
    ONLY as the baseline the soft cue-based router must beat on paraphrases."""
    q = " " + question.lower().strip() + " "
    if " before " in q or " after " in q:
        return "temporal"
    if " caused " in q or q.strip().startswith("why"):
        return "causal"
    if " where " in q:
        return "location"
    if " believe " in q or " think " in q:
        return "belief"
    if "main character" in q or "most mentioned" in q:
        return "salience"
    if " refer " in q or " refer to " in q:
        return "coref"
    if q.strip().startswith("who"):
        return "events"
    return None


# ===========================================================================
# THE RUN: build all questions per doc, score every arm, bootstrap over docs
# ===========================================================================
def _shuffled_cue_dim(seed: int) -> Dict[str, str]:
    """Info-free TWIN table: a DERANGEMENT of the dimension LABELS -- every cue votes for a DIFFERENT
    dimension than its home (no fixed points), so the cue->dimension structure is destroyed and routing
    collapses. (A plain permutation can fix a dimension by chance -- that made the coref twin==model.)"""
    rng = np.random.default_rng(seed)
    dims = list(dict.fromkeys(CUE_DIM.values()))
    perm = list(dims)
    for _ in range(10000):
        perm = list(rng.permutation(dims))
        if all(perm[i] != dims[i] for i in range(len(dims))):
            break
    remap = {d: perm[i] for i, d in enumerate(dims)}
    return {c: remap[d] for c, d in CUE_DIM.items()}


def run(docs: List[str], seed: int = 20260830, capable: bool = True,
        with_state: bool = True, state_cap: Optional[int] = None) -> dict:
    """Score QA over the SituationModel per dimension vs floors + twin. `capable=True` (DEFAULT) scores
    the CAPABLE reader (build_reader) -- the correct baseline: extraction dimensions ON, temporal read off
    sm.timeline_order. `capable=False` reproduces the historical default-reader run for comparison.
    `with_state=True` adds the COPULAR entity-STATE dimension (the newly-wired consumer) as a per_dimension
    row, measured on the copular problem's NON-CIRCULAR UD-EWT gold (state_cap caps it for a fast self-test)."""
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets
    gaz = load_given_gazetteer()
    wdw = {rec["doc"]: rec for rec in json.load(open(WDW_GOLD, encoding="utf-8"))}
    twin_cue = _shuffled_cue_dim(seed)
    twin_wh = {}  # twin also loses the wh-prior

    rows: List[dict] = []           # one per (doc, question) with every arm's correctness
    route_rows: List[dict] = []     # routing accuracy (soft vs hard) on the gold questions
    for doc in docs:
        path = os.path.join(CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
        targets = build_pronoun_targets(mentions)
        reader = build_reader(gaz, capable=capable)
        sm = reader.read(path)
        sents = _conll_sents(path)
        names = _named_clusters(sm)
        qa = SituationQA(sm)
        mf_coref = floor_mostfreq_coref(mentions, names)

        qs: List[dict] = []
        cq = build_coref_questions(sm)
        for q in cq:                                  # attach the target mention for the recency floor
            q["target_mention"] = targets[q["res_idx"]]["target"] if q["res_idx"] < len(targets) else None
        qs += cq
        if doc in wdw:
            qs += build_events_questions(sm, wdw[doc])
        qs += build_temporal_questions(sm)
        qs += build_causal_questions(sm, sents)
        qs += build_absent_questions(sm)

        for q in qs:
            dim = q["dim"]
            gold = q.get("gold")
            question = q["question"]
            # -- MODEL (soft router + readout off the accumulated model) --
            routed, ans = qa.answer(question, q)
            # -- routing accuracy (soft vs hard keyword) --
            route_rows.append({"doc": doc, "dim": dim,
                               "soft_ok": int(routed == dim),
                               "hard_ok": int(hard_route(question) == dim),
                               "onto_ok": int(wh_ontology_route(question) == dim)})
            if q.get("expect_abstain"):
                # never-tracked dimension: CORRECT behavior is to abstain (ans is None)
                rows.append({"doc": doc, "dim": dim, "kind": "abstain",
                             "model_ok": int(ans is None), "overlap_ok": 0, "strong_ok": 0,
                             "twin_ok": 0})
                continue
            model_ok = int(_match(ans, gold, dim))
            # -- FLOOR: word-overlap retrieval (brief-specified) --
            cands = q.get("candidates", sorted(set(names.values())))
            ov = floor_wordoverlap(question, cands) if dim != "temporal" else None
            overlap_ok = int(_match(ov, gold, dim))
            # -- STRONGEST per-dimension floor(s) (the trivial methods actually run) --
            row = {"doc": doc, "dim": dim, "kind": "qa", "routed": routed,
                   "model_ok": model_ok, "overlap_ok": overlap_ok, "model_abstain": int(ans is None)}
            if dim == "coref":
                row["recency_ok"] = int(_match(floor_recency_coref(q.get("target_mention") or {},
                                                                   mentions, names), gold, dim))
                row["mostfreq_ok"] = int(_match(mf_coref, gold, dim))
                row["strong_ok"] = max(row["recency_ok"], row["mostfreq_ok"])  # display convenience
            elif dim == "temporal":
                row["textorder_ok"] = int(_match(floor_textorder_temporal(q, sm), gold, dim))
                row["strong_ok"] = row["textorder_ok"]
            elif dim == "causal":
                row["adjacency_ok"] = int(_match(floor_adjacency_causal(q, sm), gold, dim))
                row["strong_ok"] = max(row["adjacency_ok"], overlap_ok)
            else:
                row["strong_ok"] = overlap_ok     # events: word-overlap is the strong trivial floor
            # -- info-free TWIN (deranged cue->dim: routes to the wrong store) --
            t_routed, t_ans = qa.answer(question, q, cue_dim=twin_cue, wh_prior=twin_wh)
            row["twin_ok"] = int(_match(t_ans, gold, dim))
            rows.append(row)

    res = _aggregate(rows, route_rows, docs, seed)
    if with_state:
        # THE COPULAR STATE DIMENSION (this problem): a live per_dimension row on the copular problem's
        # NON-CIRCULAR UD-EWT gold, driven through the SAME router + a state_register readout. Lazy import
        # (avoids a module cycle: the state cell imports this harness for the router). Additive.
        try:
            import experiments.exp_situation_model_state_qa_v1 as STATE
            srow, sdetail = STATE.board_state_dimension(cap=state_cap, n_boot=1000, seed=seed)
            res["per_dimension"]["state"] = srow
            res["state_qa_detail"] = sdetail
            # aggregate INCLUDING the newly-answerable state dim: with the flag OFF the state questions score
            # 0 (base reader has no register), with it ON they score model_acc -> turning it on lifts the union
            # aggregate. Reported separately; res["aggregate"] stays the clean 4-dim LitBank number (no regression).
            a = res["aggregate"]; n4, ok4 = a["n"], a["model_acc"] * a["n"] if a["model_acc"] is not None else 0
            ns, oks = srow["n"], (srow["model_acc"] or 0) * srow["n"]
            res["aggregate_including_state"] = {
                "flag_off": round(ok4 / max(1, n4 + ns), 4),
                "flag_on": round((ok4 + oks) / max(1, n4 + ns), 4),
                "delta_from_turning_on": round(oks / max(1, n4 + ns), 4),
                "n": n4 + ns, "note": "union of the 4 LitBank dims + the UD-EWT state dim; state=0 when the flag is off"}
        except Exception as e:
            res["per_dimension"]["state"] = None
            res["state_qa_detail"] = {"error": f"{type(e).__name__}: {e}"}
    res["reader_config"] = {
        "capable": bool(capable),
        "flags": ("tense_agnostic_events+preserve_tense+timeline_register+bind_entity_states" if capable else "default(off)"),
        "temporal_readout": "sm.timeline_order (whole-passage register)",
    }
    return res


def _acc(rows, key):
    v = [r[key] for r in rows if key in r]
    return (sum(v) / len(v)) if v else None


def _aggregate(rows, route_rows, docs, seed, B=2000):
    rng = np.random.default_rng(seed + 1)
    doc_ids = [d for d in docs if any(r["doc"] == d for r in rows)]
    di = {d: i for i, d in enumerate(doc_ids)}
    nD = len(doc_ids)
    dims = ["coref", "events", "temporal", "causal", "location", "belief"]

    def per_doc_sums(dim, key):
        """(n_per_doc, ok_per_doc) numpy arrays over doc_ids for `dim`/`key`."""
        n = np.zeros(nD); ok = np.zeros(nD)
        for r in rows:
            if r["dim"] != dim or key not in r:
                continue
            j = di[r["doc"]]; n[j] += 1; ok[j] += r[key]
        return n, ok

    def boot_diff(dim, ka, kb):
        na, oa = per_doc_sums(dim, ka)
        nb, ob = per_doc_sums(dim, kb)
        diffs = np.empty(B)
        for b in range(B):
            s = rng.integers(0, nD, nD)
            Na, Oa = na[s].sum(), oa[s].sum()
            Nb, Ob = nb[s].sum(), ob[s].sum()
            diffs[b] = (Oa / Na if Na else 0) - (Ob / Nb if Nb else 0)
        diffs.sort()
        return diffs[int(0.025 * B)], diffs[int(0.975 * B)]

    # candidate STANDALONE floor columns per dimension (gate on the highest-accuracy one)
    FLOOR_COLS = {"coref": ["overlap_ok", "recency_ok", "mostfreq_ok"],
                  "events": ["overlap_ok"], "temporal": ["textorder_ok"],
                  "causal": ["overlap_ok", "adjacency_ok"]}
    per_dim = {}
    for dim in dims:
        sub = [r for r in rows if r["dim"] == dim]
        if not sub:
            continue
        n = len(sub)
        m = _acc(sub, "model_ok"); ov = _acc(sub, "overlap_ok"); tw = _acc(sub, "twin_ok")
        floor_accs = {c: _acc(sub, c) for c in FLOOR_COLS.get(dim, ["overlap_ok"]) if _acc(sub, c) is not None}
        # STRONGEST floor = the standalone method with the highest accuracy (discipline: gate on it)
        strong_col = max(floor_accs, key=floor_accs.get) if floor_accs else "overlap_ok"
        st = floor_accs.get(strong_col)
        lo, hi = boot_diff(dim, "model_ok", strong_col)
        tlo, thi = boot_diff(dim, "model_ok", "twin_ok")
        per_dim[dim] = {
            "n": n, "model_acc": round(m, 4) if m is not None else None,
            "overlap_floor": round(ov, 4) if ov is not None else None,
            "floor_accs": {k: round(v, 4) for k, v in floor_accs.items()},
            "strongest_floor_name": strong_col, "strongest_floor": round(st, 4) if st is not None else None,
            "twin_acc": round(tw, 4) if tw is not None else None,
            "model_minus_strongest": [round(float(lo), 4), round(float(hi), 4)],
            "model_minus_twin": [round(float(tlo), 4), round(float(thi), 4)],
            "ci_sep_over_strongest": bool(lo > 0),
            "ci_sep_over_twin": bool(tlo > 0),
        }

    # aggregate over the SCORED dimensions (exclude never-tracked abstain rows from the QA accuracy)
    qa_rows = [r for r in rows if r.get("kind") == "qa"]
    agg = {"n": len(qa_rows), "model_acc": round(_acc(qa_rows, "model_ok"), 4) if qa_rows else None,
           "overlap_floor": round(_acc(qa_rows, "overlap_ok"), 4) if qa_rows else None,
           "strongest_floor": round(_acc(qa_rows, "strong_ok"), 4) if qa_rows else None,
           "twin_acc": round(_acc(qa_rows, "twin_ok"), 4) if qa_rows else None}
    route_acc = {"soft_cue_table": round(_acc(route_rows, "soft_ok"), 4) if route_rows else None,
                 "hard_keyword": round(_acc(route_rows, "hard_ok"), 4) if route_rows else None,
                 "wh_ontology": round(_acc(route_rows, "onto_ok"), 4) if route_rows else None,
                 "n": len(route_rows)}
    # POSITIVE CONTROL: coref cases where the accumulated model is RIGHT but the recency re-reading
    # floor is WRONG -- the topic-shift / non-adjacent antecedents that REQUIRE the maintained model
    # (the floor's local proximity misses them). Model >> floor on this subset earns the "reads off the
    # model, not by re-reading" claim directly.
    cs = [r for r in rows if r["dim"] == "coref" and "recency_ok" in r]
    pos_ctrl = {"n_coref": len(cs),
                "model_right_recency_wrong": sum(1 for r in cs if r["model_ok"] and not r["recency_ok"]),
                "recency_right_model_wrong": sum(1 for r in cs if r["recency_ok"] and not r["model_ok"]),
                "both_right": sum(1 for r in cs if r["model_ok"] and r["recency_ok"])}
    return {"per_dimension": per_dim, "aggregate": agg, "routing_on_gold": route_acc,
            "positive_control_coref": pos_ctrl, "n_docs": len(doc_ids), "seed": seed}


# ===========================================================================
# PARAPHRASE GENERALIZATION (the brain-fidelity axis: QUD-invariance, not keywords)
# ===========================================================================
# (question, gold_dim, novel_cue): novel_cue=True means the DISCRIMINATING word is NOT in any cue
# table -- only the wh-ontology + WordNet head-noun resolver can route these. This is the generalization
# axis the drill named: the wh-ontology router generalizes to UNSEEN wordings; the cue-table cannot.
PARAPHRASE_BANK = [
    ("Who does she refer to ?", "coref", False),
    ("Which character does 'her' denote ?", "coref", False),
    ("Who is 'he' ?", "coref", False),
    ("She points back to which individual ?", "coref", True),      # 'individual'->person (WordNet)
    ("Did the fire happen before or after the storm ?", "temporal", False),
    ("Which came earlier, the fire or the storm ?", "temporal", False),
    ("At what moment did the fire start ?", "temporal", True),     # 'moment'->noun.time (WordNet)
    ("Did the arrival precede the departure ?", "temporal", False),
    ("What caused the fire ?", "causal", False),
    ("Why did the fire start ?", "causal", False),
    ("For what reason did the collapse occur ?", "causal", True),  # 'reason'->cause (WordNet hypernym)
    ("What led to the collapse ?", "causal", False),
    ("Where is John ?", "location", False),
    ("In which place is John ?", "location", False),
    ("In what spot is John ?", "location", True),                  # 'spot'->noun.location (WordNet)
    ("At which site is John standing ?", "location", True),        # 'site'->noun.location (WordNet)
    ("What does Mary believe ?", "belief", False),
    ("What does Mary think is true ?", "belief", False),
]


def paraphrase_generalization() -> dict:
    """Compare THREE routers on paraphrases and on the NOVEL-cue-word held-out subset: exact-keyword
    (brittle), soft cue-table (intermediate), wh-ontology+WordNet head-noun (brain-faithful). The
    faithful router must WIN on novel cues -- that is the whole point of QUD/answer-type generalization."""
    routers = {"exact_keyword": hard_route, "soft_cue_table": route, "wh_ontology": wh_ontology_route}
    detail = []
    agg = {name: {"all": 0, "novel": 0} for name in routers}
    n_novel = sum(1 for _q, _g, nv in PARAPHRASE_BANK if nv)
    n = len(PARAPHRASE_BANK)
    for q, gold, novel in PARAPHRASE_BANK:
        row = {"q": q, "gold": gold, "novel_cue": novel}
        for name, fn in routers.items():
            ok = int(fn(q) == gold)
            row[name] = fn(q)
            agg[name]["all"] += ok
            if novel:
                agg[name]["novel"] += ok
        detail.append(row)
    return {"n": n, "n_novel_cue": n_novel,
            "router_acc_all": {k: round(v["all"] / n, 4) for k, v in agg.items()},
            "router_acc_novel_cue": {k: round(v["novel"] / n_novel, 4) for k, v in agg.items()},
            "detail": detail}


def _paraphrase_of(q: dict) -> Optional[str]:
    """A NATURAL paraphrase that drops the cue-table's trigger word for the question's dimension (so the
    cue-table misroutes but a person would still recognise the question). None -> skip this dimension."""
    d = q["dim"]
    if d == "coref":
        return f"Who is '{q['pron']}' ?"                       # drops 'refer to'
    if d == "causal":
        return f"For what reason did {q['outcome']} happen ?"  # 'reason' not in the cue-table (WordNet->cause)
    if d == "events":
        return f"Which person performed {q['pred']} ?"         # 'person'->entity->events; cue-table -> which->coref
    return None                                                # temporal: before/after are inherent -> skip


def run_paraphrase_qa(docs: List[str]) -> dict:
    """END-TO-END payoff of the brain-faithful router ACROSS DIMENSIONS: does the router choice change
    ANSWER accuracy on REAL questions under a natural PARAPHRASE that drops the cue-table's trigger? The
    cue-table then MISROUTES -> wrong readout -> wrong answer; the wh-ontology router (answer-type +
    WordNet head noun) still routes -> preserves whatever the readout can do. This connects the router
    generalization to actual ANSWERING (not just routing on a toy bank), per dimension."""
    gaz = load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(WDW_GOLD, encoding="utf-8"))}
    arms: Dict[str, List[int]] = defaultdict(lambda: [0, 0])   # "dim|router|form" -> [ok, n]
    for doc in docs:
        path = os.path.join(CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        sm = SituationReader(gaz=gaz).read(path)
        sents = _conll_sents(path)
        qa = SituationQA(sm)
        qs = build_coref_questions(sm) + build_causal_questions(sm, sents)
        if doc in wdw:
            qs += build_events_questions(sm, wdw[doc])
        for q in qs:
            d = q["dim"]
            para = _paraphrase_of(q)
            if para is None:
                continue
            for rname, rfn in (("cue_table", route), ("wh_ontology", wh_ontology_route)):
                for fname, question in (("canonical", q["question"]), ("paraphrase", para)):
                    _dd, ans = qa.answer(question, q, router=rfn)
                    arms[f"{d}|{rname}|{fname}"][0] += int(_match(ans, q["gold"], d))
                    arms[f"{d}|{rname}|{fname}"][1] += 1
    by_dim = {}
    for dim in ("coref", "causal", "events"):
        sub = {k.split("|", 1)[1]: v for k, v in arms.items() if k.startswith(dim + "|")}
        if sub:
            by_dim[dim] = {k: round(v[0] / v[1], 4) if v[1] else None for k, v in sub.items()}
            by_dim[dim]["n"] = next((v[1] for v in sub.values()), 0)
    return by_dim


def run_wired_events_qa(docs: List[str]) -> dict:
    """PERFORMANCE CEILING for who-did-what: the events readout reads event.agent, which the DEFAULT
    reader extracts POSITIONALLY. The assembly landed a WIRED role path (parse -> router + quotative,
    +0.247 role accuracy). This re-answers the SAME who-did-what questions with role_route='wired' to
    see whether the QA interface inherits that lift -- the assembly's lever, measured inside the QA
    instrument. (The wired path loads the persisted parse frontend; heavier, so run on a subset.)"""
    gaz = load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(WDW_GOLD, encoding="utf-8"))}
    arms: Dict[str, List[int]] = {"positional": [0, 0], "wired": [0, 0]}
    for doc in docs:
        if doc not in wdw:
            continue
        path = os.path.join(CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        for mode in ("positional", "wired"):
            sm = SituationReader(gaz=gaz, role_route=mode).read(path)
            qa = SituationQA(sm)
            for q in build_events_questions(sm, wdw[doc]):
                _d, ans = qa.answer(q["question"], q)
                arms[mode][0] += int(_match(ans, q["gold"], "events"))
                arms[mode][1] += 1
    return {k: round(v[0] / v[1], 4) if v[1] else None for k, v in arms.items()} | \
           {"n": arms["positional"][1], "n_docs": len([d for d in docs if d in wdw])}


# ===========================================================================
# self-test + main
# ===========================================================================
def _selftest() -> dict:
    # 1) router generalization: wh-ontology >= cue-table on NOVEL cue words (the whole point), and
    #    both soft routers beat the exact-keyword switch overall
    par = paraphrase_generalization()
    assert par["router_acc_novel_cue"]["wh_ontology"] >= par["router_acc_novel_cue"]["soft_cue_table"], par
    assert par["router_acc_all"]["soft_cue_table"] >= par["router_acc_all"]["exact_keyword"], par
    assert par["router_acc_all"]["wh_ontology"] >= 0.7, par
    # 2) abstain gate: a never-tracked question routes to an island dim and the readout abstains
    #    build a tiny model to exercise the readout
    assert route("Where is John ?") == "location"
    assert route("What does Mary believe ?") == "belief"
    # 3) INSTRUMENT-COUPLING FIX (fast unit): _answer_temporal reads sm.timeline_order (chrono_rank),
    #    which is INDEPENDENT of per-event tense -- so it is not erased by the keystone. Constructed sm:
    #    chrono order is the REVERSE of text order, so a tense/text-position readout would answer the
    #    opposite -> proves the register field is consulted.
    _sm = SituationModel(passage_id="t", n_sentences=1)
    _sm.timeline_order = [{"lemma": "arrive", "chrono_rank": 0, "text_rank": 1},
                          {"lemma": "leave", "chrono_rank": 1, "text_rank": 0}]
    _qa = SituationQA(_sm)
    assert _qa._answer_temporal({"a": "arrive", "b": "leave"}) == "before", "timeline_order not consulted"
    assert _qa._answer_temporal({"a": "leave", "b": "arrive"}) == "after"
    # 4) end-to-end on 2 real LitBank docs (CAPABLE reader = the correct baseline), assert questions build
    #    + arms populate, AND the temporal dimension does NOT collapse under the keystone (preserve_tense
    #    restores the gold; timeline_register populates the readout field).
    # 2b) the COPULAR-FRAME router (this problem): 'what/who is X' / 'is X a Y' -> state; and the gates that
    #     keep it from stealing the existing dims (salience / coref-pronoun / where / believe).
    assert _is_state_frame("What is Ahab ?") and route("What is Ahab ?") == "state"
    assert _is_state_frame("Is the room a cold ?") is True   # yes/no copular frame
    assert route("Who is the main character ?") == "salience", "state frame must not steal salience"
    assert route("Who is 'he' ?") != "state", "a pronoun holder is coref, not state"
    assert route("Where is John ?") == "location" and route("What does Mary believe ?") == "belief"
    assert wh_ontology_route("What is Ahab ?") == "state"
    docs = load_docs(2)
    res = run(docs, state_cap=150)   # capable=True; small state_cap keeps the self-test fast
    assert res["aggregate"]["n"] >= 1, res
    assert res["per_dimension"].get("coref", {}).get("n", 0) >= 1, res["per_dimension"]
    td = res["per_dimension"].get("temporal")
    assert td and td["n"] > 0, ("temporal collapsed on the capable reader", res.get("per_dimension"))
    # routing on real gold questions: soft router should route the built questions well
    assert res["routing_on_gold"]["soft_cue_table"] >= 0.8, res["routing_on_gold"]
    # the wired STATE dimension: a live per_dimension row, base-reader-off zero, model beats the floor
    sd = res["per_dimension"].get("state")
    assert sd and sd["n"] > 10, ("state dim did not build", res.get("state_qa_detail"))
    assert res["state_qa_detail"]["base_reader_off_zero"] == 0.0, res["state_qa_detail"]
    assert sd["model_acc"] > sd["strongest_floor"], ("state model must beat floor", sd)
    return {"paraphrase": par, "route_smoke_ok": True, "reader_config": res["reader_config"],
            "real_docs_agg": res["aggregate"], "coref_n": res["per_dimension"]["coref"]["n"],
            "temporal_n": td["n"], "temporal_model_acc": td["model_acc"],
            "state_dim": sd, "aggregate_including_state": res.get("aggregate_including_state")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    if args.self_test:
        out = _selftest()
        print(json.dumps(out, indent=2)[:2500])
        print("SELF-TEST PASS")
        return

    docs = load_docs(args.docs)
    res = run(docs, seed=args.seed)
    res["paraphrase_generalization"] = paraphrase_generalization()
    res["paraphrase_qa_endtoend"] = run_paraphrase_qa(docs)
    res["wired_events_qa"] = run_wired_events_qa(docs[:25])   # heavier (parse) -> subset
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    # one-screen summary
    print("=" * 96)
    print("UNIFIED GLASS-BOX QA OVER THE LIVE SituationModel -- per-dimension vs floors + twin")
    print("=" * 96)
    rc = res.get("reader_config", {})
    print(f"docs={res['n_docs']}  aggregate QA n={res['aggregate']['n']}  "
          f"reader={'CAPABLE' if rc.get('capable') else 'default'} [{rc.get('flags')}]  "
          f"temporal readout={rc.get('temporal_readout')}")
    a = res["aggregate"]
    print(f"\nAGGREGATE  model={a['model_acc']}  overlap-floor={a['overlap_floor']}  "
          f"strongest-floor={a['strongest_floor']}  info-free-twin={a['twin_acc']}")
    print(f"\n{'dimension':10s} {'n':>4s} {'model':>7s} {'ovlp':>6s} {'strong':>7s} {'twin':>6s} "
          f"{'m-strong CI':>18s} {'sep>strong':>10s} {'sep>twin':>9s}")
    for dim, d in res["per_dimension"].items():
        print(f"{dim:10s} {d['n']:>4d} {str(d['model_acc']):>7s} {str(d['overlap_floor']):>6s} "
              f"{str(d['strongest_floor']):>7s} {str(d['twin_acc']):>6s} "
              f"{str(d['model_minus_strongest']):>18s} {str(d['ci_sep_over_strongest']):>10s} "
              f"{str(d['ci_sep_over_twin']):>9s}")
    p = res["paraphrase_generalization"]
    print(f"\nPARAPHRASE/QUD GENERALIZATION (router routing accuracy, n={p['n']}, novel-cue n={p['n_novel_cue']}):")
    print(f"  ALL paraphrases : {p['router_acc_all']}")
    print(f"  NOVEL-cue subset: {p['router_acc_novel_cue']}  <- only wh-ontology+WordNet can route these")
    r = res["routing_on_gold"]
    print(f"ROUTING on gold questions (n={r['n']}): soft-cue={r['soft_cue_table']} "
          f"hard-keyword={r['hard_keyword']} wh-ontology={r['wh_ontology']}")
    pc = res["positive_control_coref"]
    print(f"\nPOSITIVE CONTROL (coref, n={pc['n_coref']}): model-right & recency-wrong = "
          f"{pc['model_right_recency_wrong']}  vs recency-right & model-wrong = {pc['recency_right_model_wrong']}"
          f"  (the accumulated model resolves antecedents re-reading misses)")
    pq = res["paraphrase_qa_endtoend"]
    print(f"\nPARAPHRASE-QA END-TO-END (ANSWER accuracy: canonical -> natural paraphrase; cue-table MISROUTES):")
    for dim, d in pq.items():
        print(f"  {dim:8s} (n={d.get('n')}): cue-table {d.get('cue_table|canonical')}->{d.get('cue_table|paraphrase')}  "
              f"|  wh-ontology {d.get('wh_ontology|canonical')}->{d.get('wh_ontology|paraphrase')}")
    we = res["wired_events_qa"]
    print(f"\nWIRED-ROLE-PATH events QA (n={we.get('n')}, {we.get('n_docs')} docs): "
          f"positional={we.get('positional')}  ->  wired={we.get('wired')}  (the assembly's role lever in the QA instrument)")
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()

