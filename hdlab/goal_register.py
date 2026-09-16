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

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (reader CATALOG owner-DONE + BRAIN_FOUNDATIONAL_AUDIT §2b; strategy first-hand cross-ref)'
__bf_note__ = 'goal/subgoal register (admissible verb-class supply + a tracked graph); CAT admissible foundation'
__bf_corrections__ = []


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
    # --- THE GOAL'S CONTENT AND THE TIME ITS STATUS CLOSED (pri 135) -------------------------------
    # A goal is a state of an agent ABOUT AN OBJECT AT A TIME (Zwaan & Radvansky 1998 intentionality
    # index; Trabasso & van den Broek 1985 goal/outcome arcs).  The register used to carry only the
    # agent + the goal head, so "buy bread" was closed by "bought a car", and a question asked at time
    # t could read a closure that happens later.  These fields make the object and the time part of the
    # record -- filled by track_status / track_status_thwart, read by the t-bounded queries.
    goal_object: Optional[str] = None            # the goal's THEME head ("buy bread" -> "bread"); None = the
                                                 #   goal states no object -> it closes on agent+predicate and
                                                 #   status_evidence SAYS so
    satisfied_at: Optional[Tuple[int, int]] = None   # (sent_idx, within-sentence position) of the closing outcome
    failed_at: Optional[Tuple[int, int]] = None      # (sent_idx, position) of the thwart / negation
    object_source: Optional[str] = None          # argument_structure_organ | span_head_final (glass-box:
                                                 #   which rung decided the goal THEME)
    status_evidence: Optional[str] = None        # entity_identity | head_lemma | goal_states_no_object |
                                                 #   outcome_theme_unobserved | unresolved_pronoun_theme |
                                                 #   negated_construction | thwart:<cue> | converse | antonym
    status_conf: Optional[float] = None          # GRADED confidence of the status decision: 1.0 when the
                                                 #   outcome theme was observed and matched, else the ONLINE
                                                 #   validity of the agent+predicate cue (CONTENT_STATS)


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


# ADVCL PURPOSE FILTER (owner-DONE validate_the_ppmi_svd_means_end_bridge... §5): a bare 'to VP' is a PURPOSE
# adjunct (advcl) vs a COMPLEMENT (xcomp/ccomp/acl) -- a syntactic-structure decision read off the arc labeler.
_PURPOSE_DEPREL = frozenset({"advcl"})
_COMPLEMENT_DEPREL = frozenset({"xcomp", "ccomp", "acl", "acl:relcl", "relcl", "csubj"})


def extract_goals_sentence(toks: List[str], up: List[str], si: int, subcat=None, deprels=None,
                           heads=None) -> List[Goal]:
    """Extract explicit goals from ONE sentence (tokens + UPOS). Glass-box, rule-based, no LLM. When
    `subcat` (a SubcatFrames lexicalist frame) is provided, the bare-purpose branch uses the brain-
    foundational verb SUBCATEGORIZATION FRAME (complement-taker vs adjunct-host) + extraposition detection
    instead of the hardcoded NON_GOAL_TO list -- the upstream fix for the parse-gated over-firing.

    `deprels` (an optional {1-based idx -> arc-labeler deprel} for this sentence) applies the ADVCL PURPOSE
    FILTER: a bare 'to VP' is KEPT only if the infinitive's deprel is a purpose adjunct (advcl), a confirmed
    complement (xcomp/ccomp/acl) is REJECTED (upstream net-positive on why(): removes 131 wrong vs 24 genuine,
    5.5:1). An unlabeled/other deprel falls through to the subcat decision (no over-rejection)."""
    low = [t.lower() for t in toks]
    out: List[Goal] = []
    n = len(toks)

    def _bind_theme(g):
        """pri 135: the goal THEME is an ARGUMENT of the infinitive, read off the reader's OWN parse by the
        SAME organ that binds event patients. Falls back (goal_object) to the span's head-final reading."""
        if heads is not None and g.to_tok is not None and g.to_tok >= 0:
            th = organ_theme(toks, up, heads, g.to_tok + 1, goal_span_end(g))
            if th:
                g.goal_object, g.object_source = th, "argument_structure_organ"
                return g
        g.goal_object, g.object_source = goal_object(g), "span_head_final"
        return g

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
        out.append(_bind_theme(Goal(agent=agent, goal_head=head, goal_text=span or head, kind=kind,
                                    source_verb=lem, sent_idx=si, verb_tok=i, to_tok=to_i,
                                    negated=_negated_before(toks, i))))

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
                out.append(_bind_theme(Goal(agent=agent, goal_head=head, goal_text=span or head,
                                            kind="purpose_marked", source_verb="in_order_to", sent_idx=si,
                                            verb_tok=i, to_tok=trg, negated=_negated_before(toks, i))))

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
        # ADVCL PURPOSE FILTER: the infinitive verb is at 0-based i+1 (the VERB after 'to'); read its arc-labeler
        # deprel (1-based). REJECT a confirmed complement (xcomp/ccomp/acl); an unlabeled/other deprel falls
        # through (do not over-reject). This is the syntactic purpose-vs-complement decision (Friederici; UD advcl).
        if deprels is not None:
            inf = i + 1
            dep = deprels.get(inf + 1) or deprels.get(inf)
            if dep in _COMPLEMENT_DEPREL:
                continue
        head, span = _goal_span_after_to(toks, up, i)
        if not head:
            continue
        subj = _subject_before(toks, up, mvi)
        agent = subj[0] if subj else "?"
        out.append(_bind_theme(Goal(agent=agent, goal_head=head, goal_text=span or head, kind="purpose_bare",
                                    source_verb=mv, sent_idx=si, verb_tok=mvi, to_tok=i,
                                    negated=_negated_before(toks, mvi))))
    return out


def extract_goals(sents: List[List[str]], pos_tags: List[List[str]], subcat=None, deprels_by_sent=None,
                  heads_by_sent=None) -> List[Goal]:
    """Extract explicit goals across a passage. sents = [[token]], pos_tags = [[UPOS]] aligned. When
    `subcat` (a SubcatFrames lexicalist frame) is provided, the bare-purpose branch is gated by the
    brain-foundational verb subcategorization frame + extraposition detection (the upstream fix). When
    `deprels_by_sent` (an optional [{1-based idx -> arc-labeler deprel}] aligned to sents) is provided, the
    ADVCL PURPOSE FILTER additionally rejects bare-purpose 'to VP's whose infinitive is a confirmed complement.

    SOURCE OF THAT VERDICT (pri 129, 2026-09-15): it is no longer a frozen supervised perceptron's deprel.
    `SituationReader._purpose_deprels` fills this map from the Competition-Model organ's PURPOSE arm
    (`graded_role_assigner.purpose_complement_posterior` -- lexicalist frame + configuration cues, validities
    accrued from counts, plastic), which emits "xcomp" for a complement and "advcl" for a purpose adjunct."""
    goals: List[Goal] = []
    for si, toks in enumerate(sents):
        up = pos_tags[si] if si < len(pos_tags) else ["X"] * len(toks)
        dr = deprels_by_sent[si] if (deprels_by_sent is not None and si < len(deprels_by_sent)) else None
        hd = heads_by_sent[si] if (heads_by_sent is not None and si < len(heads_by_sent)) else None
        goals.extend(extract_goals_sentence(list(toks), list(up), si, subcat=subcat, deprels=dr, heads=hd))
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
# GOAL CLOSURE BY CONTENT, AGENT AND TIME  (pri 135 -- the three binding constraints)
# ---------------------------------------------------------------------------
# THE BRAIN (PINNED):
#   * A goal node is CLOSED by an outcome only when the outcome achieves the goal CONTENT -- the same
#     agent acting on the SAME THEME. Trabasso & van den Broek (1985) / Trabasso & Sperry (1985) build the
#     narrative causal network out of goal->attempt->OUTCOME arcs in which the outcome state IS the goal
#     state; Zwaan & Radvansky (1998) index each event on five dimensions and update an index only for the
#     event that matches on it -- the intentionality index is (agent, goal content), so an event sharing
#     the predicate but not the theme indexes a DIFFERENT goal.
#   * The THEME IS AN ENTITY, not a string: a discourse file card (Heim 1982 file-change semantics;
#     Kahneman & Treisman 1992 object files). So identity is decided through the reader OWN entity files
#     first (the canonicaliser) and by head lemma only as the fallback.
#   * ORDER IS (SENTENCE, WITHIN-SENTENCE POSITION): the reference time advances with every clause
#     (Reichenbach 1947; van Dijk & Kintsch 1983 incremental updating), so a later clause of the SAME
#     sentence is still later -- "she wanted to buy bread and bought the bread" closes the goal.
#   * A QUERY AT TIME t READS THE MODEL AS OF t (Altmann & Kamide 1999: anticipation is driven by what has
#     been heard so far; Kuperberg & Jaeger 2016). A goal stated after t is not evidence at t.
#   * STATUS IS GRADED, NEVER SILENTLY EQUATED (Lutz & Radvansky 1997 failed > completed > neutral): when
#     the outcome theme cannot be observed, the closure is recorded as agent+predicate-only and carries
#     the ONLINE validity of that cue instead of a frozen constant.
# OUR-INVENTION-UNDER-TEST: the theme-head extraction rule, the span-end ordering key, the accrual prior.
CONTENT_MATCH = "match"
CONTENT_MISMATCH = "mismatch"
CONTENT_UNKNOWN = "unknown"

# determiners / particles / prepositions that are never the THEME HEAD of an English NP (head-final)
_OBJ_STOP = {"the", "a", "an", "this", "that", "these", "those", "his", "her", "their", "my", "your", "our",
             "its", "some", "any", "no", "more", "much", "many", "own", "very", "just", "again", "back",
             "out", "up", "down", "away", "off", "over", "in", "on", "at", "to", "for", "with", "of", "from",
             "into", "about", "not", "never", "n't", "there", "here", "one", "thing", "things",
             # INDEFINITE / INTERROGATIVE PRO-FORMS: they denote no individual, so a goal whose span ends in
             # one states NO theme ("make something", "see what is available") and must close on
             # agent+predicate like any objectless goal -- not veto on a theme that was never named.
             "something", "anything", "nothing", "everything", "someone", "anyone", "everyone", "somebody",
             "anybody", "nobody", "everybody", "stuff", "what", "whatever", "which", "whichever"}
# a POST-MODIFIER boundary: everything from here on modifies the head, it is not the head
_THEME_BREAK = {"of", "in", "on", "at", "for", "with", "from", "into", "about", "by", "over", "under",
                "after", "before", "during", "through", "between", "against", "toward", "towards", "until",
                "because", "that", "which", "who", "whom", "whose", "when", "while", "where", "and", "but",
                "or", "so", "as", "than", "if"}


def _lemma_noun(w: str) -> str:
    """Stable noun-lemma key for a theme head ("loaves" -> "loaf"). hdlab.lexical_utils.head_lemma is the
    shipped light noun morphology (regex + irregular map, NO external asset at inference); a head that
    lemmatises to the empty string (a redaction, digits) keeps its lowered surface rather than collapsing."""
    wl = str(w or "").lower()
    try:
        from hdlab.lexical_utils import head_lemma as _hl
        return _hl(wl) or wl
    except Exception:
        return _lemma(wl)


def _theme_head(text) -> Optional[str]:
    """The HEAD of a theme surface: the last content token BEFORE any post-modifier (English NPs are
    head-final but a PP/clause after the head is a modifier, not the theme -- "go snorkeling on his second
    day" is about SNORKELLING, not about the DAY). A PRONOUN theme is returned as the pronoun -- it is
    resolved through the entity files, never dropped."""
    toks = [t for t in _tokset_raw(text) if t]
    cut = len(toks)
    for i, t in enumerate(toks):
        if i > 0 and t in _THEME_BREAK:
            cut = i
            break
    toks = toks[:cut]
    if not toks:
        return None
    if toks[-1] in PRONOUNS:
        return toks[-1]
    keep = [t for t in toks if t not in _OBJ_STOP]
    return keep[-1] if keep else None


def goal_object(g) -> Optional[str]:
    """The goal THEME, decided at extraction by the argument-structure organ when a parse was available
    (g.goal_object / g.object_source='argument_structure_organ'); otherwise the head of the goal span AFTER
    its head verb ("buy bread" -> "bread"), which is the fallback reading. None when
    the goal states no object ("escape", "get out") -- that goal closes on agent+predicate and the record
    SAYS so (status_evidence='goal_states_no_object'), which is what "treat missing target information as
    uncertainty rather than automatic equivalence" requires of the record."""
    pre = getattr(g, "goal_object", None)
    if pre:
        return pre
    toks = [t for t in _tokset_raw(getattr(g, "goal_text", "") or "") if t]
    ah = _norm_pred(getattr(g, "goal_head", "") or "")
    rest, dropped = [], False
    for t in toks:
        if not dropped and (_norm_pred(t) == ah or _lemma(t) == _lemma(ah)):
            dropped = True
            continue
        rest.append(t)
    return _theme_head(" ".join(rest)) if rest else None


_CLAUSE_BOUNDARY = {".", ",", ";", ":", "!", "?", "and", "but", "or", "because", "who", "which", "when",
                    "that", "while", "so"}


def organ_theme(toks, up, heads, inf_idx0, span_end=None) -> Optional[str]:
    """The goal THEME as an ARGUMENT of the infinitival predicate, decided by the SAME organ that decides the
    event patients -- hdlab.predicate_argument_frontend.structural_patient_pick over the reader OWN parse
    (obj / nsubj:pass off the labelled arc, valency-gated). ONE STRUCTURE, ONE ORGAN: "what the action
    targeted" is the Tier-0 agent->object binding (Woodward 1998), and the reader already computes it for
    every event; the goal clause is not a different kind of object. None when the organ binds nothing inside
    the goal's own clause -- the caller then falls back to the span's head-final reading.
    OUR-INVENTION-UNDER-TEST: the clause-boundary window that keeps the pick inside the goal clause."""
    if not heads:
        return None
    try:
        from hdlab.predicate_argument_frontend import structural_patient_pick
    except Exception:
        return None
    try:
        p = structural_patient_pick(list(toks), list(up), dict(heads), inf_idx0 + 1)
    except Exception:
        return None
    if not p:
        return None
    j = int(p) - 1
    if j <= inf_idx0 or j >= len(toks):
        return None
    # THE PICK MUST LIE INSIDE THE GOAL'S OWN SPAN. The extractor has already decided how far the goal's
    # content reaches; the patient organ is asked WHICH nominal inside that span is the theme, never to reach
    # past it. (Measured: without this bound it bound `summer` for "trying to fix the old motorbike ALL
    # SUMMER" and the theme test then vetoed a realization the passage reports.)
    if span_end is not None and j > int(span_end):
        return None
    if any(str(t).lower() in _CLAUSE_BOUNDARY for t in toks[inf_idx0 + 1:j]):
        return None                      # the organ reached past the goal clause -> not this goal's theme
    # THE ORGAN NAMES THE ARGUMENT; THE NP NAMES THE THEME. The two channels answer different questions and
    # their errors are complementary (measured on ROC: the organ recovers the argument where the span's
    # head-final reading takes a temporal -- "help her MOM this thanksgiving", "land some INTERVIEWS soon" --
    # while the span reading recovers the head where the organ takes a compound or possessive modifier --
    # "chicken pot PIE", "soap box car DERBY", "his TIRE"). So: the organ picks the phrase, then the phrase's
    # own head-final rule picks the token that names it -- one composition, both rungs used for what each
    # actually computes.
    k = j
    while (k + 1 < len(toks) and (span_end is None or (k + 1) <= int(span_end))
           and (k + 1) < len(up) and str(up[k + 1]) in ("NOUN", "PROPN", "NUM", "ADJ", "PART", "X")):
        k += 1
    while k > j and (k >= len(up) or str(up[k]) not in ("NOUN", "PROPN", "NUM", "X")):
        k -= 1
    return _theme_head(str(toks[k]))


def event_object(e) -> Optional[str]:
    """The outcome event THEME head (its bound patient). None = the reader bound no patient -> the theme is
    UNOBSERVED (uncertainty), which is NOT the same as a theme that conflicts."""
    p = str(getattr(e, "patient", "") or "").strip()
    if not p or p in ("?", "None", "none"):
        return None
    return _theme_head(p)


def content_verdict(goal_obj, ev_obj, canon=None, g_sent=0, e_sent=0, matcher=None):
    """Three-valued CONTENT comparison of a goal theme and an outcome theme -> (verdict, how):
    match / mismatch / unknown. The reader OWN entity files decide first (the theme is a file card, not a
    string); an unresolved PRONOUN theme is UNKNOWN (the recall loss there belongs to the clustering,
    pri 131, and must never be laundered into a silent match); head lemma is the fallback."""
    if not goal_obj:
        return CONTENT_UNKNOWN, "goal_states_no_object"
    if not ev_obj:
        return CONTENT_UNKNOWN, "outcome_theme_unobserved"
    ga = ea = None
    if canon is not None:
        try:
            ga = canon(goal_obj, g_sent)
        except Exception:
            ga = None
        try:
            ea = canon(ev_obj, e_sent)
        except Exception:
            ea = None
    if ga and ea:
        if _norm(str(ga)) == _norm(str(ea)):
            return CONTENT_MATCH, "entity_identity"
        # A DIFFERENCE is evidence ONLY BETWEEN TWO INDEPENDENTLY NAMED THEMES.  When either side is a
        # PRONOUN, the "identity" is an antecedent the coreference organ picked in a graded competition that
        # this register cannot re-run, and a disagreement with it is weak evidence, not a veto: on the OCC
        # gold the files resolved "won IT" to "weekend" and the goal's own "championship" was then read as a
        # DIFFERENT thing, blocking a realization that plainly happened.  The recall this leaves on the table
        # belongs to the entity files (pri 131/136) and is recorded, never laundered into a match.
        if goal_obj in PRONOUNS or ev_obj in PRONOUNS:
            return CONTENT_UNKNOWN, "anaphoric_theme_identity_unconfirmed"
        # TWO FILE CARDS CAN NAME ONE THING. The files are known to under-merge common nouns (pri 131/136),
        # and a TYPE relation between the two heads is exactly the evidence that would have merged them
        # ("buy the corner BAKERY" / "Tomas bought the SHOP": the structured store has bakery IS-A shop).
        # So a bare entity DIFFERENCE is not evidence when the structured store says the heads are
        # compatible -- abstain and hand the uncertainty down, never a veto and never a silent match.
        if matcher is not None:
            kg_, ke_ = _lemma_noun(goal_obj), _lemma_noun(ev_obj)
            try:
                if matcher.type_match(kg_, ke_)[0] > 0 or matcher.type_match(ke_, kg_)[0] > 0:
                    return CONTENT_UNKNOWN, "entity_difference_overruled_by_type_compatibility"
            except Exception:
                pass
        return CONTENT_MISMATCH, "entity_identity"
    if (goal_obj in PRONOUNS and not ga) or (ev_obj in PRONOUNS and not ea):
        return CONTENT_UNKNOWN, "unresolved_pronoun_theme"
    kg, ke = _lemma_noun(goal_obj), _lemma_noun(ev_obj)
    if kg == ke:
        return CONTENT_MATCH, "head_lemma"
    # THE COMPATIBLE THEME (opt-in): two different words can name the same thing ("the corner BAKERY" / "the
    # SHOP"), and deciding that is a TYPE/PART relation on the STRUCTURED relational store, not a string test
    # -- the separate combinatorial-semantics computation the polarity-blind distributional hub cannot do
    # (Binder & Desai 2011). Consulted ONLY when a matcher is injected; matcher=None -> byte-identical, and
    # the default reader reads no new asset at inference.
    if matcher is not None:
        try:
            sign, why, _score = matcher.type_match(kg, ke)
            if sign > 0:
                return CONTENT_MATCH, "structured_compatible:" + str(why)
            sign2, why2, _s2 = matcher.type_match(ke, kg)
            if sign2 > 0:
                return CONTENT_MATCH, "structured_compatible:" + str(why2)
        except Exception:
            pass
    return CONTENT_MISMATCH, "head_lemma"


def goal_span_end(g) -> int:
    """The token index of the LAST token of the goal stated span within its sentence. An outcome in the
    SAME sentence counts only if it lies AFTER this -- otherwise the goal own infinitive ("wanted to buy
    bread", which the event reader also records as an event) would instantly close the goal itself."""
    base = getattr(g, "to_tok", -1)
    if base is None or base < 0:
        base = getattr(g, "verb_tok", -1)
    if base is None or base < 0:
        return 10 ** 6                      # no position known -> no same-sentence outcome can be ordered
    n = len([t for t in str(getattr(g, "goal_text", "") or "").split() if t])
    return base + max(1, n)


def outcome_is_after(g, e_sent, e_pos) -> bool:
    """Discourse order: (sentence, within-sentence position). A later clause of the goal OWN sentence is
    still later; an event with no recorded position cannot be ordered within the sentence (abstain)."""
    gs = getattr(g, "sent_idx", 0)
    if e_sent > gs:
        return True
    if e_sent < gs:
        return False
    return e_pos is not None and e_pos > goal_span_end(g)


def _outcome_holds(pol) -> bool:
    """D01 polarity (pri 132): a NEGATED outcome does not realize a goal. polarity None/0 = not read /
    undetermined -> the incumbent positive reading (abstain, never a guess)."""
    try:
        return pol is None or int(pol) >= 0
    except Exception:
        return True


class ContentMatchAccrual:
    """THE ONLINE VALIDITY of the agent+predicate cue when the outcome theme is UNOBSERVABLE: P(the content
    matched | the theme was observable), accrued from the reader OWN decoded outcomes with a Laplace prior.
    Nothing here is frozen or fitted offline, and the STATUS DECISION NEVER READS IT -- it grades the
    confidence handed downstream, so the register stays deterministic while the signal stays graded (the
    brain is plastic, never frozen; a cue validity is a lifetime statistic accrued from counts)."""
    __slots__ = ("n_match", "n_mismatch")

    def __init__(self, n_match: int = 0, n_mismatch: int = 0):
        self.n_match = int(n_match)
        self.n_mismatch = int(n_mismatch)

    def observe(self, verdict) -> None:
        if verdict == CONTENT_MATCH:
            self.n_match += 1
        elif verdict == CONTENT_MISMATCH:
            self.n_mismatch += 1

    def p_match(self) -> float:
        return (self.n_match + 1.0) / (self.n_match + self.n_mismatch + 2.0)

    def as_dict(self) -> dict:
        return {"n_match": self.n_match, "n_mismatch": self.n_mismatch, "p_match": round(self.p_match(), 4)}


CONTENT_STATS = ContentMatchAccrual()      # the process-wide accrual (the observe path; no frozen number)


def _ev_tuples(events, norm, agent_fn=None):
    """[(sent_idx, position, normalized predicate, agent, theme head, polarity, theme PRECISION)].
    The precision is the reader's OWN calibrated reliability of the parse arc the patient was read off
    (EventRecord.patient_conf, Friston precision-weighting, already computed by the precision-weight wire and
    previously thrown away by the goal closure). None = not available -> the evidence is taken at face value."""
    out = []
    for e in events:
        si = getattr(e, "sent_idx", 0)
        ag = getattr(e, "agent", "")
        ag = agent_fn(ag, si) if agent_fn is not None else str(ag or "").lower()
        out.append((si, getattr(e, "pred_idx", None), norm(getattr(e, "predicate", "")), ag,
                    event_object(e), getattr(e, "polarity", None), getattr(e, "patient_conf", None)))
    return out


def closing_outcome(g, ga, ah, ev, canon=None, stats=None, p_prior=None, matcher=None):
    """The EARLIEST outcome in `ev` that closes goal g -- same agent, same predicate, content NOT in
    conflict, positive, and AFTER the goal in (sentence, position). Returns (sent, pos, evidence, conf) or
    None. This is the ONE goal-closure predicate; track_status, track_status_thwart and any other consumer
    of goal realization call it rather than re-deriving the rule (one structure, one organ)."""
    st = stats if stats is not None else CONTENT_STATS
    # the accrued validity is READ ONCE per call (the caller passes the snapshot it took before the pass), so
    # a single status pass is internally deterministic while the validity itself stays plastic across passes.
    p0 = st.p_match() if p_prior is None else float(p_prior)
    gobj = getattr(g, "goal_object", None)
    if gobj is None:
        gobj = goal_object(g)
        try:
            g.goal_object = gobj
        except Exception:
            pass
    best = None
    for row in ev:
        si, pos, pl, ea, th, pol = row[0], row[1], row[2], row[3], row[4], row[5]
        prec = row[6] if len(row) > 6 else None
        if not pl or pl != ah:
            continue
        if not (ea == ga or ga in ("?", "")):
            continue
        if not _outcome_holds(pol):
            continue
        if not outcome_is_after(g, si, pos):
            continue
        verdict, how = content_verdict(gobj, th, canon, getattr(g, "sent_idx", 0), si, matcher=matcher)
        st.observe(verdict)                                   # the observe path: only decidable pairs count
        if verdict == CONTENT_MISMATCH:
            # PRECISION-WEIGHTED VETO (Friston precision-weighting: the brain weights a cue by its
            # reliability instead of treating every cue as certain).  A conflicting theme is evidence only if
            # the reader believes the ARC it was read off is more likely right than wrong -- a MAP decision on
            # the arc's OWN calibrated probability (`EventRecord.patient_conf`, produced by the precision-
            # weight rung and previously thrown away here), with no tuned constant.  Measured case: "he
            # crossed the line and finished" binds `line` as the patient of `finished` with conf 0.27, and
            # that 0.27-reliable token was vetoing a goal the passage plainly realizes.  Precision
            # unavailable -> the evidence stands (the incumbent, stricter reading).
            if prec is not None and float(prec) <= 0.5:
                how, verdict = "low_precision_theme_conflict", CONTENT_UNKNOWN
            else:
                continue                                      # a different theme closes a DIFFERENT goal
        conf = 1.0 if verdict == CONTENT_MATCH else round(p0, 4)
        cand = (si, pos if pos is not None else 10 ** 6, how, conf)
        if best is None or (cand[0], cand[1]) < (best[0], best[1]):
            best = cand
    return best


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

    def goals_of(self, agent: str, t: Optional[int] = None) -> List[Goal]:
        """The agent goals, most recent first. `t` (a sentence index) BOUNDS the query: a goal STATED
        after t is not in the model at t (pri 135 R04 -- a question asked at t may not read the future)."""
        gs = self._by_agent.get((agent or "").lower(), [])
        if t is not None:
            gs = [g for g in gs if getattr(g, "sent_idx", 0) <= t]
        # reinstatement order: most recent first (Suh & Trabasso last-unsatisfied-superordinate priority)
        return sorted(gs, key=lambda g: (g.sent_idx, g.verb_tok), reverse=True)

    def status_of(self, g: Goal, t: Optional[int] = None) -> str:
        """The goal status AS OF sentence t. A goal FINAL achieved/failed status is not its status at an
        earlier point (pri 135 R04), so a t-bounded query recomputes it from the recorded closure TIMES and
        the EARLIEST closure wins. t=None -> the final `status` field (byte-identical to the incumbent, and
        the path any caller that sets `.status` directly -- e.g. an info-free twin -- keeps)."""
        if t is None:
            return g.status
        if getattr(g, "negated", False):
            return "failed"
        sa, fa = getattr(g, "satisfied_at", None), getattr(g, "failed_at", None)
        cands = []
        if sa is not None and sa[0] <= t:
            cands.append((tuple(sa), "satisfied"))
        if fa is not None and fa[0] <= t:
            cands.append((tuple(fa), "failed"))
        if cands:
            return min(cands)[1]
        if sa is None and fa is None and g.status in ("satisfied", "failed"):
            return g.status            # a status set with no recorded time -> untimed; report it unchanged
        return "active"

    def wants(self, agent: str, t: Optional[int] = None) -> Optional[Goal]:
        """The agent's CURRENT goal via Suh & Trabasso (1993) REINSTATEMENT: the most recent ACTIVE goal
        -- a completed (satisfied) subgoal DEACTIVATES and attention returns to the still-open superordinate
        goal (which may be OLDER). So skip satisfied/failed/negated goals and return the most recent OPEN
        one; fall back to the most recent non-negated goal, else the most recent.

        `t` bounds the read to goals STATED at or before t, with each status taken AS OF t (pri 135 R04)."""
        for g in self.goals_of(agent, t):             # goals_of is most-recent-first
            if not g.negated and self.status_of(g, t) == "active":
                return g
        for g in self.goals_of(agent, t):
            if not g.negated:
                return g
        gs = self.goals_of(agent, t)
        return gs[0] if gs else None

    def why(self, action_head: str, agent: Optional[str] = None, t: Optional[int] = None,
            with_provenance: bool = False):
        """The GOAL-based reason an agent performed `action_head`: the purpose adjunct whose matrix verb
        IS that action (goal-why, distinct from the physical cause). Falls back to the agent active goal.

        The IDENTITY constraint is BINDING (R02): when the requested agent has no purpose for that action
        the answer is that agent OWN current goal or NOTHING -- never another agent purpose. `t` bounds the
        read to purposes stated at or before t (R04). `with_provenance=True` returns (goal, provenance) so a
        consumer can tell a real purpose from the LABELLED same-agent fallback instead of having to assume:
        'purpose_construction' | 'same_agent_current_goal_fallback' | 'unavailable'."""
        ah = _lemma(action_head)
        cands = [g for g in self.goals if g.kind in ("purpose_marked", "purpose_bare")
                 and _lemma(g.source_verb) == ah
                 and (t is None or getattr(g, "sent_idx", 0) <= t)]
        if agent is not None:
            ca = (agent or "").lower()
            # R02 (follow-up review 2026-09-15): the agent constraint is BINDING -- no broadening to another
            # agent's purpose when the requested agent has none (the same-agent active-goal fallback below stays).
            cands = [g for g in cands if (g.agent_canonical or g.agent or "").lower() == ca]
        if cands:
            g = sorted(cands, key=lambda g: (g.sent_idx, g.verb_tok))[0]
            return (g, "purpose_construction") if with_provenance else g
        if agent is not None:
            w = self.wants(agent, t)
            if with_provenance:
                return (w, "same_agent_current_goal_fallback" if w is not None else "unavailable")
            return w
        return (None, "unavailable") if with_provenance else None

    def achieved(self, agent: str, goal_head: str, t: Optional[int] = None) -> str:
        """The status of the agent `goal_head` goal, AS OF t when t is given (R04)."""
        for g in self.goals_of(agent, t):
            if _lemma(g.goal_head) == _lemma(goal_head):
                return self.status_of(g, t)
        return "unknown"


# ---------------------------------------------------------------------------
# STATUS TRACKING: goal satisfaction / failure over the event stream (PINNED status field)
# ---------------------------------------------------------------------------
def track_status(goals: List[Goal], events, canon=None, stats=None) -> List[Goal]:
    """Set each goal STATUS (active/satisfied/failed) from the reader event stream (Lutz & Radvansky: a goal
    is satisfied when a LATER event by the SAME agent realizes the goal; failed when explicitly negated).
    `events` is an iterable with .predicate/.agent/.sent_idx/.pred_idx/.patient/.polarity. `canon(surface,
    si)` (optional) is the reader entity resolver, used to compare THEMES as entities rather than strings.

    SATISFACTION IS A CONTENT MATCH (pri 135 R03): the outcome must share the goal PREDICATE, AGENT and
    THEME and follow the goal in (sentence, within-sentence position) -- "buy bread" is no longer closed by
    "bought a car", and "she wanted to buy bread and bought the bread" now closes in its own sentence. When
    the outcome theme cannot be observed the closure still fires on agent+predicate but the record SAYS so
    (status_evidence) and carries the ONLINE validity of that cue (status_conf), never a silent equivalence.
    The closure TIME is recorded (satisfied_at / failed_at) so a query at time t can read the status AS OF t.
    Graded decay (not deletion) is still represented by keeping the goal in the register with the status."""
    ev = _ev_tuples(events, lambda w: _lemma(str(w)))
    _p0 = (stats if stats is not None else CONTENT_STATS).p_match()      # one snapshot for the whole pass
    for g in goals:
        g.goal_object = goal_object(g)          # returns the organ-decided theme when extraction bound one
        if g.negated:
            g.status = "failed"
            g.satisfied_at, g.failed_at = None, (getattr(g, "sent_idx", 0), goal_span_end(g))
            g.status_evidence, g.status_conf = "negated_construction", 1.0
            continue
        ah = _lemma(g.goal_head)
        ga = (g.agent_canonical or g.agent or "").lower()
        hit = closing_outcome(g, ga, ah, ev, canon=canon, stats=stats, p_prior=_p0)
        if hit is not None:
            g.status = "satisfied"
            g.satisfied_at, g.failed_at = (hit[0], hit[1]), None
            g.status_evidence, g.status_conf = hit[2], hit[3]
        else:
            g.status = "active"
            g.satisfied_at, g.failed_at = None, None
            g.status_evidence, g.status_conf = None, None
    return goals


# ===========================================================================
# GOAL-FAILURE-BY-THWART generalization (Q111, promoted VERBATIM from
# experiments/_occ_upstream_goal_status.track_status_thwart, thwart-branch focus). A STRICT SUPERSET of
# the baseline track_status above: it adds a FAILURE-by-thwart branch + two extraction generalizations
# the OCC-appraisal inference needs on modern prose -- (i) event-agent COREF canonicalization (an outcome
# clause with a PRONOUN subject binds to the goal's named agent) and (ii) IRREGULAR-PAST normalization of
# the realizing predicate ("won"->"win"). Every goal the baseline marked satisfied/failed KEEPS that
# verdict; the ONLY change is some baseline-'active' goals become 'satisfied' (pronoun/irregular outcome)
# or 'failed' (thwart). Gated behind the reader's track_goal_thwart flag (default-on); all_capabilities_off
# forces it False -> the baseline track_status is the byte-identity reference.
#
# THE BRAIN (PINNED -- Lutz & Radvansky 1997): narrative goal structure carries a STATUS field
# active/satisfied/FAILED; a failed goal is not deleted -- it is tracked and lingered on. track_status
# implemented satisfied + negated-construction but NOT thwart-by-event -- an INCOMPLETE realization of the
# PINNED status field, not a new mechanism. This completes it. Deterministic, glass-box, stdlib+hdlab. NO LLM.
# ===========================================================================
# THWART lexicon (OUR-INVENTION-UNDER-TEST -- swept, not adopted; the PRINCIPLE that a thwarting event sets
# failed is PINNED). Failure/thwart predicates + adverse-resultant cues.
FAILURE_VERBS = {
    "miss", "missed", "misses", "lose", "lost", "loses", "fail", "failed", "fails", "forfeit",
    "forfeited", "forfeits", "abandon", "abandoned", "abandons", "surrender", "surrendered",
    "flunk", "flunked", "botch", "botched", "blow", "blew", "blown",
}
_THWART_NEG = {"not", "n't", "never", "no", "n't.", "cannot", "couldn't", "wouldn't", "didn't", "doesn't",
               "won't", "can't", "failed"}
# adverse-resultant cues: the target state was lost / the deadline passed / access denied
ADVERSE_RESULTANT = {
    "gone", "closed", "shut", "empty", "late", "away", "last", "denied", "refused", "rejected",
    "cancelled", "canceled", "lost", "locked", "sold", "vanished", "slammed", "pulled", "escaped",
    "missed", "without", "unable", "impossible", "hopeless", "ruined", "spoiled", "wasted", "over",
    "withered", "died", "fell", "left", "off", "outside", "cloud",
}
# IRREGULAR PAST -> base (a standard morphology asset; _lemma only strips -ed/-s/-ing, so it leaves
# irregular past forms uncanonicalized -> a later "won"/"bought"/"lost" never matches the goal head
# "win"/"buy"/"lose"). Closed, high-frequency English strong-verb list. Foundation morphology.
IRREG_PAST = {
    "won": "win", "bought": "buy", "sold": "sell", "found": "find", "caught": "catch", "made": "make",
    "got": "get", "gotten": "get", "took": "take", "taken": "take", "ran": "run", "run": "run",
    "came": "come", "lost": "lose", "met": "meet", "paid": "pay", "built": "build", "held": "hold",
    "went": "go", "gone": "go", "left": "leave", "kept": "keep", "sent": "send", "spent": "spend",
    "brought": "bring", "taught": "teach", "wrote": "write", "written": "write", "drove": "drive",
    "rose": "rise", "chose": "choose", "chosen": "choose", "grew": "grow", "grown": "grow",
    "flew": "fly", "flown": "fly", "drew": "draw", "threw": "throw", "thrown": "throw", "knew": "know",
    "saw": "see", "seen": "see", "fell": "fall", "fallen": "fall", "swam": "swim", "swum": "swim",
    "sang": "sing", "sung": "sing", "began": "begin", "begun": "begin", "did": "do", "done": "do",
    "led": "lead", "read": "read", "fed": "feed", "shut": "shut", "hit": "hit", "cut": "cut", "put": "put",
    "forgot": "forget", "forgotten": "forget",
}
# IMPLICIT-GOAL / INVESTMENT feeder (the OCC ATTRIBUTION anger antecedent; consumed only by the default-off
# social/attribution branch of hdlab.occ_appraisal.infer_emotion -- ported so occ_appraisal has NO
# experiments/ dependency). Posits an unstated MAINTAIN/OBTAIN goal from effort/possession (Trabasso
# causal-necessity implicit goals; Liu et al. 2017 effort->goal-value; Friedman first-possession).
INVESTMENT_VERBS = {"saved", "prepared", "grown", "grew", "built", "queued", "trusted", "kept", "guarded",
                    "tended", "parked", "earned", "held", "owned", "planted", "packed", "arranged", "reserved",
                    "cooked", "made", "raised", "wrote", "written", "waited"}


def _norm_pred(w: str) -> str:
    """Normalize a predicate surface to its base: irregular map first, then the register's -ed/-s/-ing strip."""
    wl = str(w).lower()
    return IRREG_PAST.get(wl, _lemma(wl))


def _tokset(text: str) -> List[str]:
    return re.findall(r"[a-z']+", str(text).lower())


def _tokset_raw(text):
    return [t.strip(".,;:!?\"'").lower() for t in str(text).split()]


def _sent_texts(events, sents=None):
    """Best-effort per-sentence surface for cue scanning. If `sents` (a list of token-lists) is given, use
    it; else None -> the caller relies on event predicates only."""
    if sents is None:
        return None
    return [" ".join(str(t) for t in toks) for toks in sents]


def implicit_investment_goals(raw_sents, char):
    """Instantiate implicit MAINTAIN/OBTAIN goals for `char` from effort/possession patterns (the anger
    antecedent the explicit goal register misses). Returns a list of lightweight Goal objects routed into
    the same store. Used only by the default-off attribution branch of the OCC appraisal read-out."""
    cl = (char or "").lower()
    out = []
    for si, s in enumerate(raw_sents):
        toks = _tokset_raw(s)
        if not toks:
            continue
        subj_is_char = (cl in toks[:3]) or (toks[0] in ("he", "she", "they", "i", "we"))
        if not subj_is_char:
            continue
        vi = next((i for i, t in enumerate(toks) if t in INVESTMENT_VERBS), None)
        if vi is None:
            continue
        # object = the HEAD noun of the NP after the verb (skip det/poss/adjectives/adverbs; stop at a
        # preposition or clause boundary) -> "saved the front SEAT for..." -> "seat", not "front".
        tail = []
        for t in toks[vi + 1:vi + 8]:
            if t in ("for", "with", "within", "in", "at", "since", "to", "by", "and", "but", "all", "that", "who"):
                break
            if t in ("the", "a", "an", "her", "his", "their", "my", "our", "own", "some", "carefully", "quietly",
                     "quickly", "slowly", "just"):
                continue
            tail.append(t)
        obj = tail[-1] if tail else None
        if obj is None or len(obj) < 3:
            continue
        g = Goal(agent=cl, goal_head="keep", goal_text="keep " + obj, kind="implicit_investment",
                 source_verb=toks[vi], sent_idx=si, verb_tok=vi, to_tok=-1)
        g.agent_canonical = char
        out.append(g)
    return out


def track_status_thwart(goals: List[Goal], events, sents=None, canon=None, matcher=None,
                        stats=None) -> List[Goal]:
    """STRICT SUPERSET of track_status. Sets each goal's status in {active, satisfied, failed}, adding a
    FAILURE-by-thwart branch (Lutz & Radvansky failed status) + two extraction generalizations the OCC
    appraisal needs on modern prose: (i) event-agent COREF canonicalization (canon(surface, si) -> canonical
    entity, so an outcome clause with a PRONOUN subject -- "he passed" -- still binds to the goal's named
    agent), and (ii) IRREGULAR-PAST normalization of the realizing predicate ("won" -> "win"). `events`
    iterable of .predicate/.agent/.sent_idx; `sents` optional token-lists for cue scanning; `canon` optional
    coref resolver.

    `matcher` (optional) is an injected hdlab.structured_matcher.StructuredMatcher -- the two-store split's
    STRUCTURED relational store (SOLVED: structured_semantic_matching_for_event_goal...). When provided, a goal
    still 'active' after the branches below is signed by the matcher's STRUCTURED converse/antonym edges: a later
    same-agent CONVERSE outcome (a role-swap that keeps the goal-holder in their valued role -- wanted-to-SELL
    satisfied by a BUY) -> 'satisfied'; a pure ANTONYM outcome (the goal-holder's OWN opposite -- win/lose) ->
    'failed'. This is the signed relation the polarity-blind ATL hub cannot supply (rel(win,lose) ~= rel(sell,buy)).
    matcher=None (the default; all_capabilities_off injects none) -> this branch is skipped entirely.

    Baseline-identical for satisfied + negated-construction WHEN canon is None and no irregular/thwart/matcher
    applies; the additions only turn baseline-'active' goals into 'satisfied' (pronoun/irregular/converse outcome)
    or 'failed' (thwart/antonym) -- a strict superset (never flips an existing satisfied/failed; 0 wants()
    regressions, since wants() already skips satisfied/failed). BYTE-IDENTICAL when matcher is None or abstains
    (the matcher's hub fuzzy fallback is NOT consulted here -- only its structured edges)."""
    def _agent(surface, si):
        s = str(surface or "").lower()
        if canon is not None:
            c = canon(surface, si)
            if c:
                return str(c).lower()
        return s
    ev = _ev_tuples(events, _norm_pred, agent_fn=_agent)
    _p0 = (stats if stats is not None else CONTENT_STATS).p_match()      # one snapshot for the whole pass
    ev3 = [(row[0], row[2], row[3]) for row in ev]                   # the legacy 3-tuple view (matcher branch)
    stexts = _sent_texts(events, sents)
    for g in goals:
        g.goal_object = goal_object(g)
        # ---- baseline branch 1: negated goal construction -> failed (UNCHANGED) ----
        if g.negated:
            g.status = "failed"
            g.satisfied_at, g.failed_at = None, (getattr(g, "sent_idx", 0), goal_span_end(g))
            g.status_evidence, g.status_conf = "negated_construction", 1.0
            continue
        ah = _norm_pred(g.goal_head)
        # canonicalize the GOAL agent through the SAME resolver as the event agent (else a pronoun goal-agent
        # "we/they" mismatches an event-agent that canonicalized to the protagonist name).
        ga = _agent(g.agent_canonical or g.agent or "", getattr(g, "sent_idx", 0))
        # ---- baseline branch 2+3, now ORDERED IN TIME (pri 135 R03): satisfaction by CONTENT match
        # (agent-canon + irregular-normalized head + the goal THEME + (sentence, position) order) and
        # FAILURE by thwart are both TIMED, and THE EARLIEST CLOSING EVENT WINS -- the situation model is
        # updated in discourse order, so a thwart that happens BEFORE the realizing outcome closes the goal
        # as failed (the brief asks for the thwart check first; ordering by time subsumes that and stays
        # time-consistent with the t-bounded queries).  A tie keeps the realization, so the strict-superset
        # guarantee over the baseline holds wherever the two cues land in the same place. ----
        sat = closing_outcome(g, ga, ah, ev, canon=canon, stats=stats, p_prior=_p0, matcher=matcher)
        thw = thwart_position(g, ah, ga, ev, stexts)
        if sat is not None and (thw is None or (sat[0], sat[1]) <= (thw[0], thw[1])):
            g.status = "satisfied"
            g.satisfied_at, g.failed_at = (sat[0], sat[1]), None
            g.status_evidence, g.status_conf = sat[2], sat[3]
            continue
        if thw is not None:
            g.status = "failed"
            g.satisfied_at, g.failed_at = None, (thw[0], thw[1])
            g.status_evidence, g.status_conf = thw[2], 1.0
            continue
        # ---- NEW branch 4 (matcher injected): STRUCTURED converse/antonym SIGN via hdlab.structured_matcher ----
        # A later same-agent event whose predicate is a CONVERSE of the goal head SATISFIES it (a role-swap -- the
        # goal-holder keeps their valued role, sell/buy); a pure ANTONYM of the goal head THWARTS it (the goal-holder's
        # OWN opposite outcome, win/lose). CONVERSE is checked BEFORE ANTONYM (WordNet lists buy as an antonym of sell,
        # but for GOAL congruence sell/buy is converse-satisfy, not antonym-thwart; Cruse: converseness != antonymy).
        # Fires ONLY on goals still 'active' after branches 1-3, uses ONLY the structured edges (never the hub fuzzy
        # fallback) -> a STRICT SUPERSET, byte-identical when matcher is None or abstains.
        if matcher is not None:
            cv = _matcher_converse_antonym(g, ah, ga, ev3, stexts, matcher)
            if cv:
                g.status = cv
                # the structured converse/antonym branch scores a RELATION, not a timed closure -> no
                # satisfied_at/failed_at; status_of(t) reports it untimed and SAYS so via the evidence.
                g.satisfied_at, g.failed_at = None, None
                g.status_evidence = "structured_converse" if cv == "satisfied" else "structured_antonym"
                g.status_conf = None
                continue
        g.status = "active"
        g.satisfied_at, g.failed_at = None, None
        g.status_evidence, g.status_conf = None, None
    return goals


# theme stopwords for the role-filler overlap gate (mirrors _occ_upstream_goal_status._theme_tokens)
_THEME_STOP = {"the", "her", "his", "their", "for", "and", "with", "into", "over", "years", "this", "that",
               "a", "an", "our", "its", "was", "had", "has", "been", "will", "would", "could"}


def _matcher_converse_antonym(g, ah, ga, ev, stexts, matcher) -> Optional[str]:
    """STRUCTURED converse/antonym sign for goal g from a later outcome event, via an injected
    hdlab.structured_matcher.StructuredMatcher. Returns 'satisfied' (a converse role-swap realizes the goal),
    'failed' (a pure antonym is the goal-holder's own opposite outcome), or None (abstain -> the caller leaves the
    goal untouched -> byte-identical).

    GATE (mirrors the validated experiments/_occ_upstream_goal_status._converse_resolve role-filler layer): the
    outcome must share the goal's THEME (the goal-holder keeps their valued role over the SAME theme -- a converse
    BUY by ANOTHER agent still realizes a SELL goal over the SAME painting, so this is a THEME overlap, NOT an agent
    match). When no per-sentence text is available (stexts is None), fall back to requiring the SAME agent -- a
    conservative gate so we never fire on an unrelated later event.

    CONVERSE before ANTONYM, decided GLOBALLY over the candidate outcomes (a converse-satisfy ANYWHERE outranks an
    antonym-thwart -- the key correctness invariant: a role-swap keeps the goal-holder's role; only their OWN
    opposite is a thwart -- Cruse: converseness != antonymy). Only the STRUCTURED edges are consulted -- NEVER the
    hub fuzzy fallback -- so an abstain never depends on distributional relatedness (the byte-identity guarantee)."""
    theme = {t for t in _tokset(getattr(g, "goal_text", "") or "")
             if len(t) > 2 and t != ah and t not in _THEME_STOP}
    conv_hit = anto_hit = False
    for (si, pl, ea) in ev:
        if si <= g.sent_idx or not pl or pl == ah:
            continue
        if stexts is not None and si < len(stexts):
            gate_ok = (not theme) or bool(theme & set(_tokset(stexts[si])))
        else:
            gate_ok = (ea == ga or ga in ("?", ""))
        if not gate_ok:
            continue
        try:
            if matcher.converse(ah, pl):
                return "satisfied"          # converse-satisfy outranks any antonym-thwart -> commit immediately
            if matcher.antonym(ah, pl):
                anto_hit = True             # remember, but keep scanning for a converse elsewhere
        except Exception:
            continue
    return "failed" if anto_hit else None


def thwart_position(g, ah, ga, ev, stexts):
    """The EARLIEST (sentence, position, evidence) at which a later event/clause THWARTS goal g, or None.
    The same three cues as before, now TIMED (pri 135) so the caller can order a thwart against a realizing
    outcome instead of hard-coding which cue wins. `ev` accepts the 6-tuple event view (sent, pos, pred,
    agent, theme, polarity) or the legacy 3-tuple (sent, pred, agent). Cue (1) is an EVENT, so it carries the
    event within-sentence position; cues (2) and (3) are SENTENCE-level scans, so they are positioned at the
    end of their sentence (10**6) -- a sentence-level thwart therefore never displaces a realizing outcome
    inside the SAME sentence, which keeps the strict-superset guarantee over the baseline."""
    best = None

    def _take(cand):
        return cand if (best is None or cand[:2] < best[:2]) else best

    for row in ev:
        if len(row) >= 6:
            si, pos, pl, ea = row[0], row[1], row[2], row[3]
        else:
            si, pos, pl, ea = row[0], None, row[1], row[2]
        if not outcome_is_after(g, si, pos):
            continue
        if not (ea == ga or ga in ("?", "")):
            continue
        if pl in FAILURE_VERBS or _norm_pred(pl) in FAILURE_VERBS:
            best = _take((si, pos if pos is not None else 10 ** 6, "thwart:failure_verb"))
    if stexts is None:
        return best
    goal_obj = {t for t in _tokset(getattr(g, "goal_text", "") or "") if t != ah and len(t) > 2}
    for si in range(getattr(g, "sent_idx", 0) + 1, len(stexts)):
        toks = _tokset(stexts[si])
        ts = set(toks)
        # (2) later sentence NEGATES the goal head
        if ah in ts and (ts & _THWART_NEG):
            best = _take((si, 10 ** 6, "thwart:negated_goal_head"))
        # (3) the goal OBJECT + an adverse-resultant cue in the same later sentence
        if goal_obj and (goal_obj & ts) and (ts & ADVERSE_RESULTANT):
            best = _take((si, 10 ** 6, "thwart:adverse_resultant"))
    return best


def _is_thwarted(g, ah, ga, ev, stexts) -> bool:
    """A later event/clause thwarts goal g (the boolean view of thwart_position, kept for callers)."""
    return thwart_position(g, ah, ga, ev, stexts) is not None


# ===========================================================================
# READER-INTEGRATION HELPERS (ported VERBATIM from the validated QA cells so hdlab has NO dependency on
# experiments/): the canonical entity naming + agent canonicalization + passive-agent guard that
# experiments/exp_goal_register_qa_v1.py::read_doc runs around extract_goals. _norm / _PRONOUNS /
# _named_clusters come from experiments/exp_situation_model_qa_v1.py; make_canonicalizer /
# passive_agent_guard from experiments/exp_goal_register_qa_v1.py (there _passive_agent_guard). Consumes
# the reader's OWN accumulated SituationModel (sm.entities / sm.coref_resolutions) -- no re-reading.
# ===========================================================================
_PRONOUNS = {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "its",
             "himself", "herself", "themselves", "itself"}
_BE_AUX = {"is", "was", "are", "were", "be", "been", "being", "am", "'s", "'re", "'m"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _cluster_name(sm, cluster: int) -> Optional[str]:
    """Canonical NAME of a coref cluster read off the model's entities: the longest distinct
    non-pronoun head. None if the cluster is all-pronoun (no nameable answer)."""
    for e in sm.entities:
        if e.cluster == cluster:
            heads = [h for h in e.heads if _norm(h) and _norm(h) not in _PRONOUNS]
            if not heads:
                return None
            return max(heads, key=lambda h: len(_norm(h)))
    return None


def _named_clusters(sm) -> Dict[int, str]:
    """{cluster -> canonical name} for every cluster that has a nameable head."""
    out = {}
    for e in sm.entities:
        nm = _cluster_name(sm, e.cluster)
        if nm is not None:
            out[e.cluster] = nm
    return out


def make_canonicalizer(sm, commonnoun_canonical: bool = False):
    """Canonical-entity resolver read off sm.entities + sm.coref_resolutions: canon(surface, si) -> a stable
    entity label, or None (abstain).

    commonnoun_canonical (default False -> BYTE-IDENTICAL to the proper-name-centric behavior): when True,
    expose every COMMON-NOUN cluster with a STABLE head-lemma label (the wiring/reframe lever from the owner-DONE
    common-noun coref problem, Q111 §5.2). The reader already CLUSTERS common nouns, but a mention surface whose
    HEAD is a common noun ('the man', 'men') only bound when its whole normalized span matched a stored head --
    so multi-token / plural surfaces ABSTAINED. When on, each cluster head ALSO registers its head TOKEN and the
    head LEMMA (hdlab.commonnoun_binder.head_lemma) as keys -> the same canon, and canon() falls back to the
    surface's head-token/lemma, so 'the man felt afraid' binds to the tracked man where it previously abstained.
    Lazy import -> the default (OFF) path loads nothing new. NO external LLM."""
    names = _named_clusters(sm)                       # {cluster -> canonical name}
    _hl = None
    if commonnoun_canonical:
        from hdlab.lexical_utils import head_lemma as _hl   # light noun lemma (stable head-lemma label)
    head2canon: Dict[str, str] = {}
    for e in sm.entities:
        canon = names.get(e.cluster)
        if not canon:
            continue
        for h in e.heads:
            hn = _norm(h)
            if hn and hn not in _PRONOUNS:
                head2canon.setdefault(hn, canon)
                if commonnoun_canonical:
                    toks = [t for t in hn.split() if t and t not in _PRONOUNS]
                    if toks:
                        head2canon.setdefault(toks[-1], canon)                     # head token: 'the man' -> 'man'
                        head2canon.setdefault(_hl(toks[-1]) or toks[-1], canon)    # + its stable lemma: 'men' -> 'man'
    pron_by_sent: Dict[int, list] = defaultdict(list)
    for r in sm.coref_resolutions:
        # THE OWNER IS AN ENTITY, NOT A HEAD STRING OR A SENTINEL (pri 131, deep review D02).  This lookup
        # was `names.get(r.resolved_cluster)` while the graded pick set `resolved_cluster = -1` for EVERY
        # successful record -- and -1 is the reader's FIRST live entity (online ids are -(file+1)), so a
        # graded answer naming any head could canonicalise a goal's owner to the first file in the passage.
        # The answer is now the ENTITY the retrieval returned (`resolved_entity`); `resolved_cluster` stays
        # the fallback for the coref-column path, an unresolved reference (None) canonicalises nothing, and
        # strategy's 2026-09-15 head stopgap below is kept as the LAST resort -- with the entity present it
        # is reached only when the chosen file has no nameable head.
        if not getattr(r, "attempted", True):
            continue
        _ent = getattr(r, "resolved_entity", None)
        if _ent is None:
            _ent = r.resolved_cluster
        canon = names.get(_ent)
        if not canon and getattr(r, "resolved_head", None):
            # pri 125's graded pick returns the antecedent HEAD and no cluster (resolved_cluster=None since the D02
            # guard; the entity-id contract is pri 131): canonicalise through the head's named cluster, never
            # through a sentinel id (strategy 2026-09-15; test_goal_register_landing_organ).
            canon = head2canon.get(_norm(r.resolved_head))
        if canon:
            pron_by_sent[r.sent_idx].append((r.pronoun.lower(), canon))

    def canon(surface: str, si: int) -> Optional[str]:
        s = _norm(surface)
        if s in head2canon:
            return head2canon[s]
        if commonnoun_canonical:
            toks = [t for t in s.split() if t and t not in _PRONOUNS]
            if toks:
                for key in (toks[-1], (_hl(toks[-1]) or toks[-1])):
                    if key in head2canon:
                        return head2canon[key]
        if s in _PRONOUNS or surface.lower() in _PRONOUNS:
            for sj in range(si, -1, -1):
                for (p, c) in pron_by_sent.get(sj, []):
                    if p == surface.lower():
                        return c
        return None

    return canon, names


def passive_agent_guard(goals, sm, sents, pos):
    """BRAIN-FOUNDATIONAL agent binding (Lane 4 / McCourt et al. 2015): PRO binds to the matrix AGENT, which
    is the grammatical subject in ACTIVES but the IMPLICIT agent in PASSIVES ("the ship was sunk to collect
    the insurance" -> the collector is NOT 'ship', the patient). Targeted, low-regression: only in the
    PASSIVE case (a be-aux immediately before the matrix verb) do we correct the surface-subject binding --
    reuse the reader's voice-aware EVENT agent if it recovered a by-phrase agent, else mark the goal-agent
    IMPLICIT ('?') so it is never wrongly bound to the patient. Actives are untouched (subject = agent)."""
    from hdlab.thematic_role_labeler import lemma_verb
    ev_by_key = {}
    for e in sm.events:
        ev_by_key.setdefault((e.sent_idx, lemma_verb(str(e.predicate))), e)
    for g in goals:
        si, vt = g.sent_idx, g.verb_tok
        if not (0 <= si < len(sents)) or vt is None:
            continue
        toks = [t.lower() for t in sents[si]]
        up = pos[si] if si < len(pos) else []
        # passive cue: a form of BE within the 3 tokens before the matrix verb (aux) + verb is a participle-ish
        lo = max(0, vt - 3)
        be_before = any(toks[j] in _BE_AUX and j < len(up) and up[j] in ("AUX", "VERB") for j in range(lo, vt))
        if not be_before:
            continue                                   # ACTIVE -> keep the surface subject (= agent). untouched.
        ev = ev_by_key.get((si, lemma_verb(str(g.source_verb))))
        ea = str(getattr(ev, "agent", "") or "").strip() if ev is not None else ""
        if ea and ea not in ("?", "None") and _norm(ea):
            g.agent = ea                               # reader recovered the passive by-phrase agent -> use it
        else:
            g.agent = "?"                              # implicit agent (no by-phrase) -> do NOT bind the patient


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
