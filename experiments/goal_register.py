"""goal_register: a glass-box GOAL/INTENTION dimension for the narrative situation model.

THE MISSING 5th Zwaan-Radvansky event-indexing dimension (intentionality). The reader tracks
who/what/when/where, physical causation, belief, state, possession -- but NOT what each agent is
TRYING to achieve. This builds a per-agent GOAL REGISTER, populated from EXPLICIT purpose/desire/
intention constructions (the Tier-1 reliable anchors) bound to the resolved agent, with a STATUS
field (active/satisfied/failed). NO spaCy at the extraction core (UPOS from the reader's frontend
tagger), NO external LLM (the invariant). Proven in experiments/; the proposed hdlab wire is in the
SOLVED.md (Q111, strategy lands it).

BRAIN-FOUNDATIONAL (research drill research_goal_intention_brain_mechanism_2026-09-04.md):
- PINNED: goal/intention is a distinct dmPFC-anchored mentalizing computation (Spunt/Lieberman
  Why>How, 4 studies), SEPARATE from belief (TPJ) though sharing mentalizing infrastructure, and
  DECISIVELY SEPARATE from physical causation (Malle 1999/2004 reason-vs-cause: the generic
  cause/effect categories give null effects while reason/belief categories give d=0.4-0.7 on the
  same data; the 'in order to / so that' construction family is reason-specific). DESIRE is folded
  INTO the goal/intention register (weakest-evidenced for its own register; Liu et al. 2009 ERP
  'shared core + belief-specific add-on').
- PINNED: narrative goal structure carries a STATUS field (active/satisfied/failed); satisfaction is
  graded decay, not deletion (Lutz & Radvansky 1997: failed > completed > neutral); reinstatement =
  last-unsatisfied-superordinate priority (Suh & Trabasso 1993, four methodologies).
- PINNED: the reliable explicit anchor is the 'in order to'/'so as to' purpose class + the Levin
  desiderative/intention verb classes (want/wish/hope/intend/plan/aim/decide/resolve/try/seek),
  with PropBank ARGM-PRP (distinct from ARGM-CAU at corpus scale) as the existence proof.
- PINNED tiering: Tier-0 'what the action targeted' (agent->object binding, Woodward 1998) is
  structurally recoverable; Tier-2 'why THIS action over the alternatives' (Baker/Jara-Ettinger
  inverse planning) REQUIRES the world-knowledge/meaning channel -> the located negative.
- OUR-INVENTION-UNDER-TEST: the exact cue set, the subject-attachment rule, the goal-span extent,
  the satisfaction-match rule, the register data structure. Swept, not adopted.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# THE RELIABLE EXPLICIT ANCHORS (Tier-1, Lane-4 research verdict)
# ---------------------------------------------------------------------------
# Levin desiderative/volition/intention/try matrix verbs (the matrix VERB, not the infinitive, is the
# unambiguous marker -> reliable). Folded: DESIRE + INTEND collapse into the one goal/intention register.
DESIRE_VERBS = {"want", "wanted", "wants", "wish", "wished", "wishes", "desire", "desired", "desires",
                "hope", "hoped", "hopes", "long", "longed", "longs", "crave", "craved", "craves",
                "yearn", "yearned", "yearns", "care", "cared", "would-like"}
INTEND_VERBS = {"intend", "intended", "intends", "mean", "meant", "means", "plan", "planned", "plans",
                "aim", "aimed", "aims", "propose", "proposed", "proposes", "resolve", "resolved",
                "resolves", "decide", "decided", "decides", "determine", "determined", "determines",
                "purpose", "purposed", "design", "designed", "meant-to"}
TRY_VERBS = {"try", "tried", "tries", "attempt", "attempted", "attempts", "seek", "sought", "seeks",
             "strive", "strove", "striven", "strives", "endeavor", "endeavored", "endeavour",
             "endeavoured", "endeavors", "undertake", "undertook", "undertakes", "struggle",
             "struggled", "struggles"}
GOAL_VERBS = {v: "desire" for v in DESIRE_VERBS}
GOAL_VERBS.update({v: "intend" for v in INTEND_VERBS})
GOAL_VERBS.update({v: "try" for v in TRY_VERBS})

# raising / aspectual / implicative verbs that ALSO take 'to VP' but do NOT encode a goal (the
# ambiguous tail the 'in order to' substitution test rejects). Used to FILTER bare 'to VP' adjuncts.
NON_GOAL_TO = {"begin", "began", "begun", "begins", "start", "started", "starts", "happen", "happened",
               "happens", "seem", "seemed", "seems", "appear", "appeared", "appears", "come", "came",
               "comes", "get", "got", "gets", "use", "used", "uses", "cease", "ceased", "ceases",
               "continue", "continued", "continues", "manage", "managed", "manages", "fail", "failed",
               "fails", "chance", "chanced", "tend", "tended", "tends", "prove", "proved", "turn",
               "turned", "grow", "grew", "grown", "prepare", "prepared", "ought", "have", "has", "had",
               "seemed-to", "is", "was", "are", "were", "be", "been", "going"}

PRONOUNS = {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "its", "i", "me",
            "my", "we", "us", "our", "you", "your", "who"}
_ANIM_PRON = {"he", "she", "they", "i", "we", "you", "who", "him", "her", "them", "us", "me"}
NOMINAL_UPOS = {"NOUN", "PROPN", "PRON"}
STOPVP = {"to", "not", "n't", "never", "be", "been", "being", "have", "has", "had", "the", "a", "an",
          "his", "her", "their", "my", "your", "our", "its", "it", "them", "him", "up", "out", "back",
          "down", "away", "off", "in", "on", "at", "for", "with", "and", "or", "so", "as", "that"}


@dataclass
class Goal:
    """One extracted goal: an agent is trying to bring about goal_head (the infinitival head + object)."""
    agent: str                 # the syntactic-subject head (surface); canonicalized downstream
    goal_head: str             # the goal's infinitive head verb (lemma-ish), e.g. 'buy', 'leave'
    goal_text: str             # the goal span text, e.g. 'buy bread', 'get out'
    kind: str                  # desire | intend | try | purpose_marked | purpose_bare
    source_verb: str           # the matrix/anchor verb or connective
    sent_idx: int
    verb_tok: int              # token index of the matrix verb (or connective) in the sentence
    to_tok: int                # token index of the infinitival 'to' (or -1)
    negated: bool = False      # 'did NOT want to', 'failed to' -> a thwarted/abandoned goal
    status: str = "active"     # active | satisfied | failed  (set by track_status)
    agent_canonical: Optional[str] = None   # filled by bind_agents


def _lemma(tok: str) -> str:
    t = tok.lower()
    t = re.sub(r"(ied)$", "y", t)
    t = re.sub(r"(ed|es|s|ing)$", "", t) if len(t) > 4 else t
    return t


def _subject_before(toks: List[str], up: List[str], vi: int) -> Optional[Tuple[str, int]]:
    """Nearest preceding nominal head (the syntactic subject of the matrix verb). Skips an intervening
    complementizer/relative. Returns (head_surface_lower, idx) or None."""
    for j in range(vi - 1, -1, -1):
        if j >= len(up):
            continue
        if up[j] in NOMINAL_UPOS:
            return toks[j].lower(), j
        # stop at a clause boundary that would cross into a different subject
        if toks[j] in (".", ";", ":", "!", "?"):
            break
    return None


def _goal_span_after_to(toks: List[str], up: List[str], to_i: int, max_len: int = 6) -> Tuple[str, str]:
    """The goal VP after an infinitival 'to': the head infinitive VERB + up to a few following content
    tokens (its object/particle), stopping at a clause boundary or a new finite verb. Returns
    (head_lemma, span_text)."""
    head = None
    span = []
    j = to_i + 1
    end = min(len(toks), to_i + 1 + max_len)
    while j < end:
        w = toks[j]
        if w in (".", ",", ";", ":", "!", "?", "and", "but", "or", "because", "who", "which", "when"):
            break
        if head is None:
            # skip an adverb/negation between 'to' and the infinitive ('to quickly leave')
            if j < len(up) and up[j] == "VERB":
                head = _lemma(w)
                span.append(w)
                j += 1
                continue
            if w in ("not", "never", "n't") or (j < len(up) and up[j] == "ADV"):
                j += 1
                continue
            # a non-verb where the infinitive should be -> give up (not a clean 'to VINF')
            break
        else:
            # collect the object/complement content tokens (nouns/adj/det) but stop at a new finite verb
            if j < len(up) and up[j] == "VERB":
                break
            span.append(w)
        j += 1
    return (head or ""), " ".join(span).strip()


def _negated_before(toks: List[str], vi: int, window: int = 3) -> bool:
    lo = max(0, vi - window)
    seg = [t.lower() for t in toks[lo:vi + 1]]
    return any(t in ("not", "n't", "never", "no", "hardly", "scarcely") for t in seg)


def _is_extraposed(toks: List[str], up: List[str], to_i: int, subcat) -> bool:
    """Expletive-it / predicate-hosted extraposition ("it would be wonderful [to meet]", "hard [to say]",
    "a way [to go]", "time [to leave]"): the infinitive is an extraposed SUBJECT/complement of a predicate
    adjective/noun, NOT a purpose adjunct of a preceding action verb. Brain-foundational surface cue
    (Lane 5): expletive it + copula + an extraposition predicate, OR the token governing 'to' is itself an
    extraposition predicate (ADJ/NOUN that hosts an infinitival subject)."""
    if subcat is None:
        return False
    lo = [t.lower() for t in toks]
    # (a) governor immediately before 'to' is an extraposition predicate ("hard to", "a way to", "time to")
    j = to_i - 1
    while j >= 0 and lo[j] in ("the", "a", "an", "no", "any", "his", "her", "their", "my", "your", "our"):
        j -= 1
    if j >= 0 and subcat.is_extraposition_predicate(lo[j]):
        return True
    # (b) expletive 'it' + copula (BE) + an extraposition predicate somewhere before 'to' in the clause
    start = to_i
    for k in range(to_i - 1, -1, -1):
        if lo[k] in (".", ";", ":", "!", "?"):
            break
        start = k
    seg = lo[start:to_i]
    if "it" in seg and any(w in ("is", "was", "be", "been", "'s", "are", "were", "seems", "seemed") for w in seg) \
            and any(subcat.is_extraposition_predicate(w) for w in seg):
        return True
    return False


def extract_goals_sentence(toks: List[str], up: List[str], si: int, subcat=None) -> List[Goal]:
    """Extract explicit goals from ONE sentence (tokens + UPOS). Glass-box, rule-based, no LLM. When
    `subcat` (a SubcatFrames lexicalist frame) is provided, the bare-purpose branch uses the brain-
    foundational verb SUBCATEGORIZATION FRAME (complement-taker vs adjunct-host) + extraposition detection
    instead of the hardcoded NON_GOAL_TO list -- the upstream fix for the parse-gated over-firing."""
    low = [t.lower() for t in toks]
    out: List[Goal] = []
    n = len(toks)

    # (1) DESIRE/INTEND/TRY matrix verb + 'to VINF' complement (reliable: the matrix verb is the marker)
    for i in range(n):
        lem = low[i]
        base = _lemma(low[i])
        kind = GOAL_VERBS.get(lem) or GOAL_VERBS.get(base)
        if kind is None:
            continue
        # find the infinitival 'to VERB' after the matrix verb, within a short window (allows 'wanted
        # very much to go'); the matrix verb must be a VERB (skip the noun 'a plan', 'no design')
        if i < len(up) and up[i] not in ("VERB", "AUX", "X"):
            # allow 'meant'/'longed' even if mistagged, but skip clear nouns like 'the plan'
            if i > 0 and low[i - 1] in ("a", "the", "his", "her", "their", "no", "any", "some"):
                continue
        to_i = None
        for j in range(i + 1, min(n, i + 5)):
            if low[j] == "to" and j + 1 < n and (j + 1 < len(up) and up[j + 1] in ("VERB", "ADV", "AUX")):
                to_i = j
                break
            if low[j] in (".", ";", "!", "?"):
                break
        if to_i is None:
            continue
        head, span = _goal_span_after_to(toks, up, to_i)
        if not head:
            continue
        subj = _subject_before(toks, up, i)
        agent = subj[0] if subj else "?"
        out.append(Goal(agent=agent, goal_head=head, goal_text=span or head, kind=kind,
                        source_verb=lem, sent_idx=si, verb_tok=i, to_tok=to_i,
                        negated=_negated_before(toks, i)))

    # (2) EXPLICIT purpose markers: 'in order to', 'so as to' (Tier-1); 'so that' (Tier-2, gated animate)
    for i in range(n - 2):
        trg = None
        if low[i] == "in" and low[i + 1] == "order" and low[i + 2] == "to":
            trg = i + 2
        elif low[i] == "so" and low[i + 1] == "as" and low[i + 2] == "to":
            trg = i + 2
        if trg is not None:
            head, span = _goal_span_after_to(toks, up, trg)
            if head:
                # the goal-holder is the matrix clause subject (nearest preceding nominal before 'in order')
                subj = _subject_before(toks, up, i)
                agent = subj[0] if subj else "?"
                out.append(Goal(agent=agent, goal_head=head, goal_text=span or head,
                                kind="purpose_marked", source_verb="in_order_to", sent_idx=si,
                                verb_tok=i, to_tok=trg, negated=_negated_before(toks, i)))

    # (3) BARE 'to VINF' purpose ADJUNCT, attached to the nearest preceding finite ACTION verb (the
    #     matrix action). The 'in order to' substitution test is applied ONLY when that verb is ADJACENT
    #     to 'to' (the control/complement position): a raising/aspectual/desire/try verb there is NOT a
    #     purpose adjunct ('began to rain', 'seemed to know'). When material intervenes ('went to the
    #     market to buy'), it is unambiguously an adjunct. This is the Tier-2-with-filter slice.
    captured_to = {g.to_tok for g in out}
    for i in range(1, n - 1):
        if low[i] != "to" or i in captured_to:
            continue
        if not (i + 1 < len(up) and up[i + 1] == "VERB"):
            continue
        if low[i - 1] in ("order", "as"):
            continue                                  # part of an 'in order to' / 'so as to' (handled in (2))
        # nearest preceding finite VERB in the clause = the matrix action this purpose adjunct serves
        mvi = None
        for j in range(i - 1, -1, -1):
            if j < len(up) and up[j] == "VERB":
                mvi = j
                break
            if low[j] in (".", ";", ":", "!", "?"):
                break
        if mvi is None:
            continue                                  # no matrix verb (e.g. 'a plan to leave') -> skip
        mv = low[mvi]
        mvl = _lemma(mv)
        adjacent = (mvi == i - 1)
        # EXTRAPOSITION (brain-foundational, Lane 5): 'it would be wonderful to meet' / 'hard to say' /
        # 'a way to go' -- the infinitive is an extraposed subject of a predicate, not a purpose adjunct.
        if _is_extraposed(toks, up, i, subcat):
            continue
        if subcat is not None:
            # BRAIN-FOUNDATIONAL lexicalist filter (MacDonald/Seidenberg; Vosse-Kempen): the governing verb's
            # SUBCATEGORIZATION FRAME decides complement vs adjunct. A complement-taker (want/begin/seem/manage)
            # takes an adjacent 'to VP' as a COMPLEMENT -> not purpose; an adjunct-host (go/come/stand) forces
            # the 'to VP' to attach as a purpose ADJUNCT.
            if mv in GOAL_VERBS or mvl in GOAL_VERBS:
                continue                              # captured as a desire/intend/try complement in (1)
            if adjacent and (subcat.is_complement_taker(mv) or subcat.is_complement_taker(mvl)):
                continue                              # lexical complement (began to rain / seemed to know)
        else:
            # fallback (no frame asset): the hardcoded raising/desire list
            if adjacent and (mv in NON_GOAL_TO or mvl in NON_GOAL_TO or mv in GOAL_VERBS or mvl in GOAL_VERBS):
                continue
        head, span = _goal_span_after_to(toks, up, i)
        if not head:
            continue
        subj = _subject_before(toks, up, mvi)
        agent = subj[0] if subj else "?"
        out.append(Goal(agent=agent, goal_head=head, goal_text=span or head, kind="purpose_bare",
                        source_verb=mv, sent_idx=si, verb_tok=mvi, to_tok=i,
                        negated=_negated_before(toks, mvi)))
    return out


def extract_goals(sents: List[List[str]], pos_tags: List[List[str]], subcat=None) -> List[Goal]:
    """Extract explicit goals across a passage. sents = [[token]], pos_tags = [[UPOS]] aligned. When
    `subcat` (a SubcatFrames lexicalist frame) is provided, the bare-purpose branch is gated by the
    brain-foundational verb subcategorization frame + extraposition detection (the upstream fix)."""
    goals: List[Goal] = []
    for si, toks in enumerate(sents):
        up = pos_tags[si] if si < len(pos_tags) else ["X"] * len(toks)
        goals.extend(extract_goals_sentence(list(toks), list(up), si, subcat=subcat))
    return goals


# ---------------------------------------------------------------------------
# AGENT BINDING: resolve each goal's surface subject to a canonical entity name.
# ---------------------------------------------------------------------------
def bind_agents(goals: List[Goal], canonicalize) -> List[Goal]:
    """Resolve each goal.agent (surface subject) to a canonical entity via `canonicalize(surface, si)`
    (supplied by the caller -- the reader's entity/coref model). Pronoun subjects are resolved to their
    antecedent's canonical name; a name maps to itself. Sets goal.agent_canonical. This binding is the
    load-bearing step the info-free twin SHUFFLES."""
    for g in goals:
        g.agent_canonical = canonicalize(g.agent, g.sent_idx) or g.agent
    return goals


# ---------------------------------------------------------------------------
# THE PER-AGENT GOAL REGISTER (the situation-model dimension)
# ---------------------------------------------------------------------------
class GoalRegister:
    """A per-agent register of goals read off a passage's explicit purpose/desire/intention
    constructions. Answers goal-QA off the ACCUMULATED register (never re-reading):
      goals_of(agent)      -> the agent's goals, most recent first (reinstatement order)
      wants(agent)         -> the agent's current (last unsatisfied, non-negated) goal head/text
      why(action, agent)   -> the GOAL purpose behind an action (distinct from a physical cause)
      achieved(agent,goal) -> status (active/satisfied/failed)
    """

    def __init__(self, goals: List[Goal]):
        self.goals = goals
        self._by_agent: Dict[str, List[Goal]] = defaultdict(list)
        for g in goals:
            self._by_agent[(g.agent_canonical or g.agent or "?").lower()].append(g)

    def agents(self) -> List[str]:
        return [a for a in self._by_agent if a and a != "?"]

    def goals_of(self, agent: str) -> List[Goal]:
        gs = self._by_agent.get((agent or "").lower(), [])
        # reinstatement order: most recent first (Suh & Trabasso last-unsatisfied-superordinate priority)
        return sorted(gs, key=lambda g: (g.sent_idx, g.verb_tok), reverse=True)

    def wants(self, agent: str) -> Optional[Goal]:
        """The agent's CURRENT goal via Suh & Trabasso (1993) REINSTATEMENT: the most recent ACTIVE goal
        -- a completed (satisfied) subgoal DEACTIVATES and attention returns to the still-open superordinate
        goal (which may be OLDER). So skip satisfied/failed/negated goals and return the most recent OPEN
        one; fall back to the most recent non-negated goal, else the most recent."""
        for g in self.goals_of(agent):                # goals_of is most-recent-first
            if not g.negated and g.status == "active":
                return g
        for g in self.goals_of(agent):
            if not g.negated:
                return g
        gs = self.goals_of(agent)
        return gs[0] if gs else None

    def why(self, action_head: str, agent: Optional[str] = None) -> Optional[Goal]:
        """The GOAL-based reason an agent performed `action_head`: the purpose adjunct whose matrix verb
        IS that action (goal-why, distinct from the physical cause). Falls back to the agent's active goal."""
        ah = _lemma(action_head)
        cands = [g for g in self.goals if g.kind in ("purpose_marked", "purpose_bare")
                 and _lemma(g.source_verb) == ah]
        if agent is not None:
            ca = (agent or "").lower()
            cands = [g for g in cands if (g.agent_canonical or g.agent or "").lower() == ca] or cands
        if cands:
            return sorted(cands, key=lambda g: (g.sent_idx, g.verb_tok))[0]
        if agent is not None:
            return self.wants(agent)
        return None

    def achieved(self, agent: str, goal_head: str) -> str:
        for g in self.goals_of(agent):
            if _lemma(g.goal_head) == _lemma(goal_head):
                return g.status
        return "unknown"


# ---------------------------------------------------------------------------
# STATUS TRACKING: goal satisfaction / failure over the event stream (PINNED status field)
# ---------------------------------------------------------------------------
def track_status(goals: List[Goal], events) -> List[Goal]:
    """Set each goal's STATUS (active/satisfied/failed) from the reader's event stream (Lutz & Radvansky:
    a goal is satisfied when a LATER event by the SAME agent realizes the goal head; failed when explicitly
    negated/thwarted). `events` is an iterable with .predicate/.agent/.sent_idx/.global_idx. Glass-box:
    satisfaction = a later same-agent event whose predicate lemma matches the goal head. Graded decay
    (not deletion) is represented by keeping the goal in the register with status=satisfied."""
    ev = [(getattr(e, "sent_idx", 0), getattr(e, "global_idx", 0), _lemma(str(getattr(e, "predicate", ""))),
           str(getattr(e, "agent", "") or "").lower()) for e in events]
    for g in goals:
        if g.negated:
            g.status = "failed"
            continue
        ah = _lemma(g.goal_head)
        ga = (g.agent_canonical or g.agent or "").lower()
        realized = any(si > g.sent_idx and pl == ah and (ea == ga or ga in ("?", ""))
                       for (si, _gi, pl, ea) in ev)
        g.status = "satisfied" if realized else "active"
    return goals


if __name__ == "__main__":
    # tiny smoke on a constructed passage (no reader needed)
    sents = [["Mary", "wanted", "to", "buy", "bread", "."],
             ["She", "went", "to", "the", "market", "to", "buy", "it", "."],
             ["John", "tried", "to", "escape", "but", "failed", "."]]
    pos = [["PROPN", "VERB", "PART", "VERB", "NOUN", "PUNCT"],
           ["PRON", "VERB", "ADP", "DET", "NOUN", "PART", "VERB", "PRON", "PUNCT"],
           ["PROPN", "VERB", "PART", "VERB", "CCONJ", "VERB", "PUNCT"]]
    gs = extract_goals(sents, pos)
    for g in gs:
        print(g.kind, "| agent=", g.agent, "| goal=", g.goal_text, "| src=", g.source_verb)
