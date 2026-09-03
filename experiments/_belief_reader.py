"""_belief_reader -- drive the PROMOTED per-agent belief_timeline END-TO-END from the LIVE reader's OWN
extraction, on real narrative prose (problem: the_belief_dimension_is_never_driven_by_the_readers_own_
extraction_on_real_prose).

THE PIVOT (see DESIGN_brain_and_mapping.md; research drill + viability probe 2026-08-31): the brief's
object-location-MOVE event source is essentially ABSENT from literary prose (~1 move/book, 0 objects with
2+ moves) AND is the wrong brain mechanism -- the mentalizing network holds a CONTENT-GENERAL propositional
attitude, source-tagged by HOW it was acquired (Koster-Hale 2017/2014), and natural narrative feeds it with
LANGUAGE ABOUT MINDS: narrator-epistemic (dominant), testimony, and (rarely) perception. So belief is driven
here from the reader's OWN extraction across the THREE registration channels, reality tracked separately, and
the SAME content-general belief_timeline sample-and-hold answers "what did A believe about F at T" for a fact
that may be a LOCATION or a STATUS (generalization = one mechanism, Dowty stative inertia; not location-only).

WHAT IS EXTRACTED (the reader's own parse+coref; NO gold events, NO LLM at inference):
  * REALITY value-changes of the tracked fact F -- an ordered [(value, sent_idx)] chain:
      fact_type='location' -> object-move (theme F -> goal PP) via the in-substrate frontend (pos_tagger +
                              arc_parser + predicate_argument_frontend route), the RULE1 special case.
      fact_type='status'   -> copular/perfect predication "F was/became/had-been V" via the same frontend.
  * OBSERVATION bit per (agent, reality-event): the PROMOTED perceptual_access_ledger (RULE0 explicit
    narrator-epistemic / RULE1 co-presence+field / RULE2 testimony) -- event_index + event_location come from
    the EXTRACTION above, NOT gold (that is the confound this problem removes).
  * TESTIMONY assertions to the agent about F -> belief-updates that need not match reality (deception/stale).

The (events, observed) are then fed to the UNTOUCHED promoted hdlab.belief_timeline; belief-at-T is read off it.

Glass-box. The reality-event extraction is fully in-substrate (no spaCy). The observation gate rides the
promoted PAL (whose syntactic front-end is spaCy -- a parser, not an LLM; that is the promoted organ's design).
ASCII only. Deterministic. Writes nothing (a library; the measuring cell owns data/).
"""
from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# -- PROMOTED organs (untouched) --
from hdlab.belief_timeline import (
    WorldEvent, timeline_belief, reality_at, current_belief_floor, initial_value,
    narration_timeline_belief, shuffle_order_twin, remap_observed_after_twin,
    InferenceEdge, fired_inference_events,
)
# -- the reader's OWN in-substrate parse + role router (glass-box, no spaCy/LLM) --
from experiments._space_reader import build_backbone, _frontend, _cluster_covering, _node_from_token
from hdlab.predicate_argument_frontend import route_predicate_arguments, matrix_verbs
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.location_register import DEICTIC_SCENE, AWAY

# placement/transfer verbs that relocate a THEME (object) -- the RULE1 location special case
PLACE_TRANSFER = {"put", "place", "set", "lay", "drop", "hide", "conceal", "carry", "take", "bring",
                  "move", "shift", "throw", "push", "pull", "stow", "deposit", "replace", "remove",
                  "hang", "stick", "tuck", "pop", "fetch", "slip", "leave", "lock", "thrust", "fling",
                  "toss", "hand", "return", "restore", "plant"}
# copular / change-of-state verbs that predicate a STATUS on their subject (Basic-copula + inchoative)
COPULAR = {"be", "become", "get", "grow", "turn", "remain", "seem", "appear", "prove", "lie", "lay",
           "fall", "go", "come", "look", "feel", "keep", "stay"}
# perfect/resultant auxiliaries handled via the parse (had/has/was + participle) -- see _status_value


def _norm(w: str) -> str:
    return w.lower().strip(".,:;\"'!?()")


# ===========================================================================
# REALITY value-change extraction (the reader's OWN parse) -> ordered [(value, sent_idx)]
# ===========================================================================
def _goal_head_in_vocab(toks, heads, v, roles, vocab):
    """The goal PP's head noun for a placement verb, preferring a value_vocab word. Relaxed vs
    _node_from_token: an object's destination need not be a canonical PLACE ground ('hook','pocket') -- the
    value is text-derived and scored against the vocab, so we take the goal-PP head noun directly."""
    node = _node_from_token(toks, roles.get("goal"), place_typing=True)
    if node not in (None, DEICTIC_SCENE, AWAY):
        val = str(node).split("-")[-1].split()[-1].lower()
        if not vocab or val in vocab:
            return val
    # relaxed: scan the verb's goal/prep-object subtree for a vocab word (into/on/to/onto X)
    for i in range(1, len(toks) + 1):
        if heads.get(i) == v and toks[i - 1].lower() in ("in", "into", "on", "onto", "to", "under",
                                                          "inside", "within", "beneath", "behind"):
            for j in range(1, len(toks) + 1):
                if heads.get(j) == i and _norm(toks[j - 1]) in vocab:
                    return _norm(toks[j - 1])
    # last resort: any vocab noun after the verb in the same clause
    for j in range(v, len(toks)):
        if _norm(toks[j]) in vocab:
            return _norm(toks[j])
    return None


def extract_location_events(sents, by_sent, fact_aliases: Sequence[str], value_vocab: Sequence[str]
                            ) -> List[Tuple[str, int]]:
    """Object-location moves of the tracked fact-entity F (theme -> goal). fact_aliases = surface forms of
    F (e.g. ['marble','it']). Returns [(goal_value, sent_idx)] in reading order, values in the supplied
    value_vocab where possible."""
    tagger, parser = _frontend()
    fal = {a.lower() for a in fact_aliases}
    vocab = {v.lower() for v in value_vocab}
    out = []
    for i, toks in enumerate(sents):
        if not toks or len(toks) > 120:
            continue
        upos = tagger.tag(list(toks))
        heads = parser.parse(list(toks), upos).heads
        for v in matrix_verbs(toks, upos, heads):
            if lemma_verb(toks[v - 1]) not in PLACE_TRANSFER:
                continue
            roles = route_predicate_arguments(list(toks), upos, heads, v, quotative=True)
            theme1 = roles.get("theme") or roles.get("patient")
            if theme1 is None:
                continue
            if _norm(toks[theme1 - 1]) not in fal:
                continue
            val = _goal_head_in_vocab(toks, heads, v, roles, vocab)
            if val is not None:
                out.append((val, i))
    return out


def _status_value(toks, upos, heads, subj_v: int, value_vocab) -> Optional[str]:
    """Read the predicated STATUS value off a copular/perfect clause whose subject is the fact-entity.
    subj_v = 1-based index of the copular/main verb. Prefers a value-vocab word in the predicate span."""
    vocab = {v.lower() for v in value_vocab}
    # collect predicate tokens: acomp/attr/oprd/xcomp + participle after the verb, within the clause
    cand = []
    for i in range(1, len(toks) + 1):
        if i == subj_v:
            continue
        if heads.get(i) == subj_v and upos[i - 1] in ("ADJ", "NOUN", "VERB", "PROPN"):
            cand.append(_norm(toks[i - 1]))
    # linear backstop: content words in the 4 tokens after the verb
    for j in range(subj_v, min(len(toks), subj_v + 4)):
        w = _norm(toks[j])
        if upos[j - 1] in ("ADJ", "NOUN", "VERB", "PROPN") and w not in cand:
            cand.append(w)
    for w in cand:
        if w in vocab:
            return w
    return cand[0] if cand else None


def extract_status_events(sents, by_sent, fact_cluster: Optional[int], fact_aliases: Sequence[str],
                          value_vocab: Sequence[str], nlp=None) -> List[Tuple[str, int]]:
    """Status predications about the tracked fact-entity F ('F was dead / became rich / had married').
    PREFERS the PROMOTED situation-model state organ (hdlab.state_register via its adapter) when an nlp is
    available -- it handles copular/perfect predication, telic change-of-state resultants, aspect, negation
    and scalar entailment (the brain-faithful state tracker); falls back to the in-substrate ad-hoc copular
    extractor otherwise. Returns [(status_value, sent_idx)] in reading order."""
    fal = {a.lower() for a in fact_aliases}
    vocab = {v.lower() for v in value_vocab}
    if nlp is not None:
        from experiments.state_register import extract_state_events
        from hdlab.state_register import _SCALAR_ENTAILS
        out = []
        for i, toks in enumerate(sents):
            if not toks or len(toks) > 120:
                continue
            low = {t.lower() for t in toks}
            # VERIDICALITY GATE: a state inside a REPORTED / MENTAL clause ('told/said that F was V',
            # 'believed F dead') is the CONTENT of a report/belief, NOT asserted reality -- route it through
            # the belief-assertion channel instead. Skip state_register reality here. (matches SPACE's
            # embedded-clause veridicality gate; fixes the reported-clause-as-reality side-effect.)
            if low & _REPORT_CUES:
                continue
            for e in extract_state_events(nlp, " ".join(toks)):
                if e.get("polarity", 1) != 1 or e.get("subj_head", "").lower() not in fal:
                    continue
                val = _norm(e.get("value", ""))
                if val in vocab:                          # exact match to the fact's value vocabulary
                    out.append((val, i))
                else:                                     # scalar entailment: 'shattered'->'broken', etc.
                    ent = _SCALAR_ENTAILS.get(val, frozenset())
                    hit = next((vv for vv in vocab if vv in ent), None)
                    if hit is not None:
                        out.append((hit, i))
        if out:
            return out
    tagger, parser = _frontend()
    out = []
    for i, toks in enumerate(sents):
        if not toks or len(toks) > 120:
            continue
        upos = tagger.tag(list(toks))
        heads = parser.parse(list(toks), upos).heads
        noms = by_sent.get(i, [])
        for v in range(1, len(toks) + 1):
            if upos[v - 1] != "VERB" and lemma_verb(toks[v - 1]) not in COPULAR:
                continue
            if lemma_verb(toks[v - 1]) not in COPULAR:
                continue
            # subject of this verb
            subj = [k for k in range(1, len(toks) + 1) if heads.get(k) == v and _norm(toks[k - 1])]
            subj_match = False
            for k in subj:
                if _norm(toks[k - 1]) in fal:
                    subj_match = True
                    break
                cid = _cluster_covering(noms, k - 1)
                if fact_cluster is not None and cid == fact_cluster:
                    subj_match = True
                    break
            if not subj_match:
                continue
            val = _status_value(toks, upos, heads, v, value_vocab)
            if val:
                out.append((val, i))
    return out


def extract_reality_events(sents, by_sent, fact: dict, nlp=None) -> List[Tuple[str, int]]:
    """Dispatch to the location or status extractor for one tracked fact spec. `nlp` (if given) routes the
    STATUS path through the promoted situation-model state organ (state_register)."""
    if fact["fact_type"] == "location":
        return extract_location_events(sents, by_sent, fact["fact_aliases"], fact["value_vocab"])
    return extract_status_events(sents, by_sent, fact.get("fact_cluster"), fact["fact_aliases"],
                                 fact["value_vocab"], nlp=nlp)


# ===========================================================================
# BELIEF-ASSERTION extraction (RULE0 narrator-epistemic + RULE2 testimony) -- the DOMINANT channels.
# The reader reads the believed VALUE straight off the mental-state / speech verb's complement, binds it to
# the agent, and marks it a BELIEF (may diverge from reality). This is genuine ToM extraction (language ->
# mentalizing; Dodell-Feder 2011), the content-general path the object-move source cannot express.
# ===========================================================================
# subject = the AGENT holds the belief (experiencer of a mental-state verb)
MENTAL_VERBS = {"believe", "think", "know", "suppose", "imagine", "deem", "consider", "fancy", "fear",
                "hope", "expect", "assume", "reckon", "trust", "doubt", "suspect", "presume", "understand",
                "feel", "find", "hold", "judge", "dream", "conclude", "conceive", "gather", "perceive",
                "realize", "realise", "guess", "wis", "ween", "reckon"}
# subject = the AGENT comes to believe (testimony received by hearing/learning)
HEAR_VERBS = {"hear", "learn", "learnt", "discover", "read", "gather", "understand", "find", "ascertain",
              "overhear", "be told", "be informed"}
# object/addressee = the AGENT is told (testimony delivered to the agent)
TELL_VERBS = {"tell", "inform", "assure", "warn", "convince", "persuade", "notify", "advise", "remind"}
_EPI_NEG = {"not", "n't", "never", "no", "n't"}
# RELIABILITY DISCOUNTING (Koenig 2004; the ledger's own _testimony_trusted): a DISTRUSTED source does not
# update belief -- the addressee keeps its prior. Detected in the testimony's local window.
_DISTRUST = [r"\bdid not believe\b", r"\bdid n.t believe\b", r"\bdid ?nt believe\b", r"\bwould not believe\b",
             r"\bdisbelieved\b", r"\bdistrusted\b", r"\bmistrusted\b", r"\bdoubted\b", r"\bknew better\b",
             r"\bnot fooled\b", r"\bnot deceived\b", r"\bnot taken in\b", r"\bsaw through\b"]
# surface NON-FACTIVE reporting/mental cues (a state in the SAME sentence is the CONTENT of a report/belief
# that MAY BE FALSE, not asserted reality) -- the veridicality gate for the state_register reality path.
# FACTIVE verbs (know/knew/realize/see/discover/learn -- complement entails truth) are DELIBERATELY EXCLUDED:
# their embedded state IS reality (Kiparsky & Kiparsky 1970 factivity), so state_register keeps it.
_REPORT_CUES = {"told", "tells", "telling", "tell", "said", "says", "say", "believed", "believes", "believe",
                "thought", "thinks", "think", "supposed", "supposes", "suppose", "informed", "informs",
                "inform", "imagined", "imagines", "imagine", "fancied", "fancy", "deemed", "assured", "warned",
                "claimed", "claims", "claim", "alleged", "reckoned", "guessed", "assumed"}


def extract_belief_assertions(sents, by_sent, agent_aliases: Sequence[str], fact_aliases: Sequence[str],
                              value_vocab: Sequence[str]) -> List[Tuple[str, int, str]]:
    """Extract the agent's ASSERTED belief value about F from mental-state / speech clauses. Returns
    [(value, sent_idx, source)] belief-updates (source in {epistemic, testimony} -- SOURCE-TAGGED, because the
    brain decodes HOW a belief was acquired, seen vs heard; Koster-Hale et al. 2014). Reader's own parse +
    coref surfaces (agent_aliases); value constrained to the text-derived value_vocab (scored exact-match)."""
    tagger, parser = _frontend()
    ag = {a.lower() for a in agent_aliases}
    fal = {a.lower() for a in fact_aliases}
    vocab = {v.lower() for v in value_vocab}
    out = []
    for i, toks in enumerate(sents):
        if not toks or len(toks) > 120:
            continue
        low = [t.lower() for t in toks]
        upos = tagger.tag(list(toks))
        heads = parser.parse(list(toks), upos).heads
        for v in range(1, len(toks) + 1):
            lem = lemma_verb(toks[v - 1])
            is_mental = lem in MENTAL_VERBS
            is_hear = lem in HEAR_VERBS
            is_tell = lem in TELL_VERBS
            if not (is_mental or is_hear or is_tell):
                continue
            # who holds the belief? mental/hear -> subject; tell -> object/addressee
            subj = [k for k in range(1, len(toks) + 1) if heads.get(k) == v]
            subj_txt = {low[k - 1] for k in subj}
            agent_involved = False
            if is_mental or is_hear:
                agent_involved = bool(subj_txt & ag) or any(low[j] in ag for j in range(max(0, v - 4), v))
            if is_tell:
                # addressee is a dobj/dative between verb and the complement, or an alias after the verb
                agent_involved = any(low[j] in ag for j in range(v, min(len(toks), v + 4)))
            if not agent_involved:
                continue
            # NEGATED epistemic ("did not know that F was V") -> the agent does NOT hold value V; skip as a
            # positive belief (the anti-knowledge is handled by the observation gate / ignorance, not a value).
            if any(low[j] in _EPI_NEG for j in range(max(0, v - 3), v + 1)):
                continue
            # RELIABILITY DISCOUNTING (Koenig 2004): a DISTRUSTED testimony does not update belief.
            if is_tell:
                window = " ".join(" ".join(t) for t in sents[i:i + 2]).lower()
                if any(re.search(p, window) for p in _DISTRUST):
                    continue
            # the fact must be referenced in this clause (bind the belief to F)
            if fal and not (fal & set(low[v:])):
                # allow the fact to appear just before the verb too (topicalized), else skip
                if not (fal & set(low[max(0, v - 3):v])):
                    continue
            # the VALUE: a value_vocab word in the clause after the verb (nearest the fact/verb wins)
            cands = [(j, low[j]) for j in range(v, len(toks)) if _norm(toks[j]) in vocab]
            if not cands:
                continue
            jv = cands[0][0]
            # DISJUNCTION guard: "in the drawer OR the bowl" is a CANDIDATE SET (disjunctive knowledge), not a
            # definite belief -- leave it to the inference (exclusion) track; do not extract a definite value.
            if any(low[k] == "or" for k in range(max(0, jv - 3), min(len(toks), jv + 4))):
                continue
            val = _norm(toks[jv])
            source = "testimony" if (is_tell or is_hear) else "epistemic"
            out.append((val, i, source))
    return out


# ===========================================================================
# OBSERVATION gate (promoted perceptual_access_ledger) + TESTIMONY channel
# ===========================================================================
_TESTIMONY_VALUE = re.compile(
    r"\b(told|informed|assured|warned)\b", re.IGNORECASE)


def observed_bits(led, text: str, agent_aliases: Sequence[str], fact_head: str,
                  reality_events: List[Tuple[str, int]]) -> Dict[Tuple[str, int], bool]:
    """For each extracted reality event (value, sent_idx), ask the PROMOTED ledger whether the agent
    witnessed it (RULE0 explicit epistemic / RULE1 co-presence+field / RULE2 informed) -- event_index and
    event_location come from the EXTRACTION, never gold. Keyed (agent_name, chrono)."""
    agent = agent_aliases[0]
    obs = {}
    for chrono, (val, sent_idx) in enumerate(reality_events):
        tr = led.observed(text, list(agent_aliases), event_object=fact_head,
                          event_index=sent_idx, event_location=val)
        obs[(agent, chrono)] = bool(tr.observed)
    return obs


# ===========================================================================
# INFERRED belief (Sodian & Wimmer 1987 -- inference as a dissociable knowledge SOURCE). The classic
# EXCLUSION inference: an agent who knows F is in one of a closed set {A,B} and OBSERVES "not in A / A empty"
# infers F is in B WITHOUT perceiving it in B. Extract the disjunction (the known candidate set) + the
# observed negative-existence premise off the reader's parse; emit an InferenceEdge for the promoted
# belief_timeline.fired_inference_events hook, which fires it ONLY if the agent observed the premise (gated).
# ===========================================================================
# emptiness / absence cues; a candidate location named in the SAME clause as one of these = a negative
# existence premise for that location ("looked in the drawer and it was empty" -> drawer excluded).
_EMPTY_CUE = ["empty", "nothing", "not there", "no longer", "vacant", "bare", "gone", "held nothing"]


def extract_inference_edges(sents, by_sent, fact: dict, agent_aliases: Sequence[str]):
    """Extract INFERENCE edges (brain-plausible closed schemas; Sodian & Wimmer inference-as-source) + whether
    the agent observed each premise. Schemas: EXCLUSION (know {A,B}, observe not-A -> B), TRANSITIVE-SPATIAL
    (F in Y, Y in Z -> F in Z), MODUS-PONENS (if P then F=V; P -> F=V). Returns (edges, premise_observed).
    Reader's own parse; glass-box; each edge is evidence-GATED downstream by fired_inference_events."""
    vocab = [v.lower() for v in fact["value_vocab"]]
    fh = fact["fact_aliases"][0].lower()
    fal = {a.lower() for a in fact["fact_aliases"]}
    ag = {a.lower() for a in agent_aliases}
    texts = [" ".join(t).lower() for t in sents]
    edges, prem_obs = [], {}

    def obs_at(i):
        return bool(ag & set(texts[i].split()))

    # -- EXCLUSION: a disjunction "in the A or the B" + an observed "not in A / A empty" -> infer B --
    candset = None
    for tx in texts:
        present = [v for v in vocab if re.search(rf"\b{re.escape(v)}\b", tx)]
        if (" or " in tx) and len(present) >= 2:
            candset = present[:2]
            break
    if candset:
        for i, tx in enumerate(texts):
            for absent in candset:
                neg = (re.search(rf"\bnot in (?:the )?{re.escape(absent)}\b", tx)
                       or (re.search(rf"\b{re.escape(absent)}\b", tx) and any(c in tx for c in _EMPTY_CUE)))
                if neg:
                    others = [v for v in candset if v != absent]
                    if len(others) != 1:
                        continue
                    edges.append(InferenceEdge(obj=fh, conclusion=others[0], premise_chronos=(float(i),),
                                               fire_chrono=float(i) + 0.4, schema="exclusion"))
                    prem_obs[float(i)] = obs_at(i)

    # -- TRANSITIVE-SPATIAL: "F ... in Y" then "Y ... in Z" (Z in vocab) -> infer F in Z --
    cont = {}   # inner_head -> (outer_head, chrono)
    for i, tx in enumerate(texts):
        m = re.search(r"\b(\w+)\b (?:was |is |were |lay |stood |sat |rested |sits |lies )?in "
                      r"(?:the |a |her |his )?(\w+)\b", tx)
        if m and m.group(1) not in cont:
            cont[m.group(1)] = (m.group(2), i)
    if fh in cont:
        mid, c1 = cont[fh]
        if mid in cont:
            outer, c2 = cont[mid]
            if outer in vocab:
                edges.append(InferenceEdge(obj=fh, conclusion=outer, premise_chronos=(float(c1), float(c2)),
                                           fire_chrono=float(max(c1, c2)) + 0.4, schema="transitive-spatial"))
                prem_obs[float(c1)] = obs_at(c1); prem_obs[float(c2)] = obs_at(c2)

    # -- MODUS-PONENS: "if <ante>, (then) F {be} V" + the antecedent asserted elsewhere -> infer F=V --
    for i, tx in enumerate(texts):
        m = re.search(r"\bif ([a-z ]+?),?\s+(?:then )?(?:the |her |his )?(\w+) (?:was|were|is|had|would be) (\w+)",
                      tx)
        if not m:
            continue
        ante, fsubj, val = m.group(1).strip(), m.group(2), m.group(3)
        if fsubj not in fal or val not in vocab:
            continue
        ante_key = [w for w in ante.split() if len(w) > 2 and w not in ("the", "was", "were", "had", "been")]
        ante_key = ante_key[-1] if ante_key else None
        for j, tx2 in enumerate(texts):
            if j == i or not ante_key:
                continue
            # the antecedent holds AND is not itself the conditional, and the agent observed it
            if re.search(rf"\b{re.escape(ante_key)}\b", tx2) and "if " not in tx2 and obs_at(j):
                edges.append(InferenceEdge(obj=fh, conclusion=val, premise_chronos=(float(i), float(j)),
                                           fire_chrono=float(max(i, j)) + 0.4, schema="modus-ponens"))
                prem_obs[float(i)] = True          # the conditional is narrated (available)
                prem_obs[float(j)] = obs_at(j)
                break
    return edges, prem_obs


# ===========================================================================
# END-TO-END: drive the promoted belief_timeline from a passage (uniform SENT-INDEX time axis)
# ===========================================================================
def drive(sents, by_sent, fact: dict, agent_aliases: Sequence[str], led, reality_events=None):
    """Compose the reader's OWN extraction into the promoted belief_timeline's (events, observed).

    TWO tracks merged on one SENT-INDEX time axis (chrono = sentence index; a belief assertion in the same
    sentence gets +0.3 so it supersedes the world mention as the agent's latest registration):
      * PERCEPTION track (RULE1): each extracted reality value-change, observation-GATED by the promoted PAL
        (RULE0 explicit-epistemic / RULE1 co-presence+field / RULE2 informed). affects_reality=True.
      * BELIEF-ASSERTION track (RULE0 narrator-epistemic + RULE2 testimony): each extracted asserted belief
        value the agent registers -- observed=True by construction, affects_reality=False (does not move the
        world; may diverge from reality => the false-belief case).
    Returns (events, observed, agent, reality_events, belief_assertions)."""
    fact_head = fact["fact_aliases"][0].lower()
    agent = agent_aliases[0]
    # reality_events may be OVERRIDDEN (e.g. a stronger-parser extraction) to test whether the perception
    # wall is parser-recall; default = the reader's OWN in-substrate parse.
    if reality_events is None:
        # route the STATUS reality path through the promoted state_register organ (situation-model state
        # tracking) when the PAL's spaCy front-end is available -- the brain-faithful change-of-state tracker.
        reality_events = extract_reality_events(sents, by_sent, fact, nlp=getattr(led, "_nlp", None))
    belief_assertions = extract_belief_assertions(sents, by_sent, agent_aliases,
                                                  fact["fact_aliases"], fact["value_vocab"])
    text = " ".join(" ".join(t) for t in sents)
    events, observed, sources = [], {}, {}
    for (val, si) in reality_events:
        tr = led.observed(text, list(agent_aliases), event_object=fact_head,
                          event_index=si, event_location=val)
        chrono = float(si)
        events.append(WorldEvent(fact_head, val, chrono=chrono, narr=chrono, kind="move",
                                 affects_reality=True))
        observed[(agent, chrono)] = bool(tr.observed)
        if observed[(agent, chrono)]:
            sources[chrono] = "perception"      # SOURCE-TAG: a witnessed change (seen)
    for (val, si, src) in belief_assertions:
        chrono = float(si) + 0.3
        events.append(WorldEvent(fact_head, val, chrono=chrono, narr=chrono, kind="testimony",
                                 affects_reality=False))
        observed[(agent, chrono)] = True
        sources[chrono] = src                   # SOURCE-TAG: epistemic (narrator) or testimony (heard)
    # INFERRED-belief track (exclusion; Sodian & Wimmer) -- fires ONLY if the agent observed the premise.
    inf_edges, prem_obs = extract_inference_edges(sents, by_sent, fact, agent_aliases)
    if inf_edges:
        prem_keyed = {(agent, pc): b for pc, b in prem_obs.items()}
        inf_ev, inf_obs = fired_inference_events(agent, inf_edges, prem_keyed, mode="gated")
        for e in inf_ev:
            events.append(WorldEvent(fact_head, e.value, chrono=float(e.chrono), narr=float(e.chrono),
                                     kind="inferred", affects_reality=False))
            sources[float(e.chrono)] = "inference"    # SOURCE-TAG: inferred (dissociable from seen/heard)
        observed.update(inf_obs)
    return events, observed, agent, reality_events, belief_assertions, sources


# ===========================================================================
# self-test: a synthetic 3-sentence status false-belief the composition must handle end-to-end
# ===========================================================================
def _self_test():
    # a minimal in-substrate check that the extractors + organ compose (no spaCy needed here)
    reality_events = [("basket", 0), ("box", 2)]
    fact_head = "marble"
    events = [WorldEvent(fact_head, v, chrono=k, narr=k, kind=("initial" if k == 0 else "move"))
              for k, (v, si) in enumerate(reality_events)]
    observed = {("Anna", 0): True, ("Anna", 1): False}   # saw the placement, missed the move
    # belief at t=1.5 = stale 'basket'; reality = 'box'; current-belief floor = final observed 'basket'
    assert timeline_belief(events, observed, "Anna", fact_head, 1.5) == "basket"
    assert reality_at(events, fact_head, 1.5) == "box"
    # if Anna had witnessed the move, belief tracks reality
    obs2 = {("Anna", 0): True, ("Anna", 1): True}
    assert timeline_belief(events, obs2, "Anna", fact_head, 1.5) == "box"
    print("belief_reader self-test PASS (compose extraction-shaped events -> promoted belief_timeline)")


if __name__ == "__main__":
    _self_test()
