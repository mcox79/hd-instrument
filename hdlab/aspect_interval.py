"""hdlab/aspect_interval.py -- ASPECT -> INTERVAL-ENDPOINT extraction + ALLEN interval reasoning.

Promoted VERBATIM (owner-DONE reason_over_event_time_order_and_duration_on_a_modern_gold, Q111 strategy
landing 2026-09-06) from experiments/_aspect_interval.py -- the extract_events_aspect / event_intervals /
allen_overlap / overlaps / build_rank / AspectualEvent bodies are UNCHANGED (byte-identical; the landing
witness verification/test_temporal_reasoner_landing.py asserts inspect.getsource identity against the
reference AND a byte-identical point-order event set on a real doc). Only this provenance paragraph is
prepended to the module header.

DEPENDENCY NOTE (honest deviation, reported at landing): this module imports the SHARED temporal front-end
experiments._temporal_ordering (T) + experiments._temporal_ordering_multiframe (M) -- the SAME modules
hdlab.situation_reader itself imports at module top (lines 135-136), and one of 48 hdlab modules that
import from experiments. Those front-end extractors LIVE in experiments (T pulls torch + hdlab.memory /
hdlab.sequence_memory; M pulls T + the shared tagger); promoting them is a separate, much larger landing
and OUT OF SCOPE for this ADDITIVE promotion. So aspect_interval is NOT literally stdlib+hdlab-only -- it
inherits exactly the reader's existing experiments dependency and introduces NO new cross-layer edge.

--- original module docstring (unchanged) ---

ASPECT -> INTERVAL-ENDPOINT extraction + ALLEN interval reasoning.

The UPSTREAM brain-foundational component for the temporal OVERLAP reasoner
(problem: reason_over_event_time_order_and_duration_on_a_modern_gold).

WHY THIS EXISTS (the upstream fidelity gap, found by reading the disk):
  The landed temporal front-end (experiments/_temporal_ordering[_multiframe]) extracts events
  for POINT ORDER only. `extract_events_punct` emits exactly three tenses -- VBD (simple past),
  had+VBN (past perfect), be+VBN (passive) -- and DROPS the finite PROGRESSIVE ("was cooking",
  "were arguing") entirely (the VBG branch of the sibling `extract_events` only keeps a *bare*
  participle; the multiframe extractor keeps no VBG at all). And "while/during/as/when" sit in the
  multiframe NEUTRAL connective set -> NO edge -> the point-order register ABSTAINS. So OVERLAP is
  genuinely absent: the very aspect that supplies an ONGOING interval is thrown away, and the very
  connective that marks co-temporality produces no relation.

BRAIN GROUNDING (research drill 2026-09-06, PINNED unless noted):
  VIEWPOINT ASPECT -> INTERVAL (PINNED -- it is the published linguistic computation, not a bridge
  we invented): Smith (1991) "The Parameter of Aspect" two-component model = situation type
  (Vendler 1957: state/activity/accomplishment/achievement) x viewpoint aspect (Comrie 1976):
    - PERFECTIVE (simple past, telic) presents a BOUNDED/CLOSED interval [t, t] (viewed from outside).
    - IMPERFECTIVE / PROGRESSIVE (be + V-ing) presents an OPEN/ONGOING interval viewed from inside --
      it spans the reference time and can CONTAIN a bounded event (Moens & Steedman 1988 nucleus;
      aspectual coercion). This is the interval the current extractor discards.
    - PERFECT (had + V-en) = anterior event + a consequent state at reference time.
  EVENTS AS BOUNDED INTERVALS is convergently brain-real (Zacks & Tversky 2001 event segmentation;
  Zacks et al. 2001 event-boundary brain response).
  ALLEN (1983) interval algebra = the correct COMPUTATIONAL-LEVEL (Marr) target for overlap:
  13 mutually-exclusive, jointly-exhaustive interval relations. PINNED-as-representation; the
  endpoint-comparison IMPLEMENTATION is OUR-SYNTHESIS (no claim humans enumerate 13 relations).

WHAT THIS MODULE ADDS (all ADDITIVE -- it is a strict SUPERSET of extract_events_punct):
  1. `extract_events_aspect(text)` -- every event extract_events_punct emits, byte-identical
     (asserted in the self-test), PLUS the dropped finite PROGRESSIVE (be+VBG -> IMPERFECTIVE), each
     event carrying a viewpoint-aspect label.
  2. `event_intervals(...)` -- maps each event's aspect + timeline rank to (start, end) endpoints.
  3. `allen_overlap(...)` / `overlaps(...)` -- the Allen relation over a pair, combining the OVERLAP
     connective ("while/during/as/meanwhile/...") with the aspect-derived intervals. Returns an
     inclusion/overlap/simultaneous relation where the point-order control can only abstain or guess
     precedence -- the load-bearing separation.

Reuses (does NOT rebuild): _temporal_ordering_multiframe (tag_punct, extract_events_punct as the
byte-identity oracle, build_constraint_edges, _toposort), _temporal_ordering (Event, tense tags).
ASCII-only. Deterministic. Substrate-only (NO LLM at inference -- the invariant).
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'Vendler/Smith-1991 viewpoint aspect (perfective=closed, imperfective=open) -> Allen-1983 interval algebra overlap; pinned framework, endpoint/span heuristics swept; byte-faithful owner-DONE promotion'
__bf_corrections__ = []


import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import temporal_ordering as T            # noqa: E402  Event + tense tags (self-contained)
from hdlab import temporal_ordering_multiframe as M  # noqa: E402  tag_punct / extract / edges / toposort (self-contained)

# ---- Viewpoint aspect (Smith 1991) -> interval character --------------------------------------
ASP_PERFECTIVE = "PERFECTIVE"     # bounded closed interval  (simple past / passive; telic default)
ASP_IMPERFECTIVE = "IMPERFECTIVE" # open ongoing interval    (progressive be+V-ing) -- the DROPPED one
ASP_PERFECT = "PERFECT"           # anterior + consequent state (had+V-en)
ASP_STATIVE = "STATIVE"           # extended state interval  (copular; reserved -- not extracted here)
ASP_DURATIVE = "DURATIVE"         # open interval from LEXICAL situation type (Vendler state/activity)

# Progressive auxiliaries that license an IMPERFECTIVE reading of a following V-ing (keeps "been" so
# perfect-progressive "had been running" is still recovered).
_PROG_BE = T.COPULA_BE
# The three GRAMMATICALIZED AUXILIARY V-ings that never head an eventive progressive (a principled
# closed-class distinction, PINNED -- not a gold-tuned stoplist): "being" (passive aux, "was being
# held"), "going" (future aux, "was going to leave"), "having" (perfect aux). Excluding these as the
# V-ING lifts precision without dropping lexical progressive events ("was beginning/running/...").
_GERUND_STOP = {"being", "going", "having"}

# LEXICAL situation type (Smith 1991's SECOND component; Vendler 1957 STATE/ACTIVITY). A durative
# predicate (state or atelic activity) presents an OPEN interval EVEN WITHOUT the progressive -- it
# can contain a bounded event. This is a pre-committed linguistic stative/atelic list (NOT peeked from
# the gold): copular/possession/existence STATES + canonically atelic ACTIVITIES. Telic-capable verbs
# are deliberately EXCLUDED (they default perfective) to protect precision.
DURATIVE_LEMMAS = {
    # states (Vendler): copular/existence/possession/relational
    "remain", "remained", "stay", "stayed", "continue", "continued", "last", "lasted",
    "live", "lived", "exist", "existed", "own", "owned", "hold", "held", "contain", "contained",
    "include", "included", "involve", "involved", "consist", "consisted", "belong", "belonged",
    "depend", "depended", "rule", "ruled", "control", "controlled", "lead", "led", "head", "headed",
    "serve", "served", "wait", "waited", "expect", "expected", "seek", "sought", "face", "faced",
    "want", "wanted", "know", "knew", "believe", "believed",
    # atelic activities (durative process readings)
    "negotiate", "negotiated", "discuss", "discussed", "fight", "fought", "search", "searched",
    "work", "worked", "grow", "grew", "rise", "rose", "fall", "fell", "travel", "travelled",
    "monitor", "monitored", "patrol", "patrolled", "watch", "watched", "guard", "guarded",
}


def _is_open(aspect: str) -> bool:
    """An OPEN/ongoing interval (can contain a bounded neighbour): progressive OR lexical durative."""
    return aspect in (ASP_IMPERFECTIVE, ASP_DURATIVE)

# OVERLAP connectives: co-temporality markers. Allen inclusion/overlap, NOT precedence.
# The multiframe register files these under NEUTRAL {when, while, as} -> no edge -> it abstains.
OVERLAP_STRONG = {"while", "during", "meanwhile", "simultaneously", "amid", "amidst",
                  "throughout", "whilst", "midst"}
OVERLAP_WEAK = {"as", "when"}     # ambiguous (can be sequential); overlap only if aspect agrees


@dataclass
class AspectualEvent:
    """An extracted event carrying viewpoint aspect (superset of T.Event)."""
    lemma: str
    idx: int
    pos: str
    tense: str
    aspect: str
    is_pp: bool = field(default=False)

    def as_event(self) -> T.Event:
        return T.Event(lemma=self.lemma, idx=self.idx, pos=self.pos, tense=self.tense, is_pp=self.is_pp)


def _aspect_of(tense: str) -> str:
    if tense == T.TENSE_PAST_PERFECT:
        return ASP_PERFECT
    return ASP_PERFECTIVE   # simple past / passive default to bounded/perfective


def extract_events_aspect(text: str, lexical_aspect: bool = False) -> Tuple[List[AspectualEvent], list]:
    """ADDITIVE superset of M.extract_events_punct: same VBD / had+VBN / be+VBN events, byte-identical,
    PLUS the finite PROGRESSIVE (be + VBG -> IMPERFECTIVE) the point-order extractor drops. Each event
    carries a viewpoint aspect. Event.idx indexes the punctuation-preserving tag stream (same as M).

    lexical_aspect=True ALSO applies Vendler LEXICAL situation type: a simple-past event whose lemma is
    a durative state/activity (DURATIVE_LEMMAS) is tagged ASP_DURATIVE (an OPEN interval) -- Smith 1991's
    second aspect component, needed for real-prose overlap where most inclusions ride on lexical
    duration, not the progressive. (Kept OFF by default so the byte-identity / no-regression guarantee
    on the order register is preserved: this changes only the OVERLAP interval character.)"""
    tagged = M.tag_punct(text)
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    # word-only rank (punctuation does not consume lookback distance -- matches M.extract_events_punct)
    word_low_by_rank: List[str] = []
    wrank: Dict[int, int] = {}
    for i, t in enumerate(tagged):
        if t[2] != M._PUNC_POS:
            wrank[i] = len(word_low_by_rank)
            word_low_by_rank.append(t[1])
    events: List[AspectualEvent] = []
    for i, (low, pos) in enumerate(zip(lows, poss)):
        if pos == M._PUNC_POS or low in T.AUX_LEMMAS:
            continue
        wr = wrank[i]
        if pos == "VBD":
            asp = ASP_DURATIVE if (lexical_aspect and low in DURATIVE_LEMMAS) else ASP_PERFECTIVE
            events.append(AspectualEvent(low, i, pos, T.TENSE_SIMPLE_PAST, asp, False))
        elif pos == "VBN":
            had = any(word_low_by_rank[j] == "had" for j in range(max(0, wr - 3), wr))
            be = any(word_low_by_rank[j] in T.COPULA_BE for j in range(max(0, wr - 3), wr))
            if had:
                events.append(AspectualEvent(low, i, pos, T.TENSE_PAST_PERFECT, ASP_PERFECT, True))
            elif be:
                events.append(AspectualEvent(low, i, pos, T.TENSE_PASSIVE, ASP_PERFECTIVE, False))
        elif pos == "VBG":
            # THE UPSTREAM FIX: a finite progressive (be + V-ing) is an IMPERFECTIVE event -- an
            # ongoing/open interval. The point-order extractor drops this entirely. Guard precision:
            # require a FINITE be-aux and exclude auxiliary/prepositional gerunds.
            prog = any(word_low_by_rank[j] in _PROG_BE for j in range(max(0, wr - 3), wr))
            if prog and low not in _GERUND_STOP:
                events.append(AspectualEvent(low, i, pos, T.TENSE_SIMPLE_PAST, ASP_IMPERFECTIVE, False))
    return events, tagged


# ---------------------------------------------------------------------------
# Interval endpoints over the reconstructed timeline (aspect -> [start, end]).
# ---------------------------------------------------------------------------
def event_intervals(events: Sequence[AspectualEvent], rank: Dict[str, int],
                    span: float = 1.0) -> Dict[str, Tuple[float, float]]:
    """Map each event to an (start, end) interval on the reconstructed timeline.

    PINNED shape (Smith 1991): perfective/perfect = a bounded point [r, r]; imperfective = an OPEN
    interval (r-span, r+span) that spans the reference time and can CONTAIN a bounded neighbour.
    `span` is OUR-INVENTION-UNDER-TEST (the ongoing-frame half-width) -- SWEEP it, never adopt it."""
    iv: Dict[str, Tuple[float, float]] = {}
    for e in events:
        r = float(rank.get(e.lemma, e.idx))
        if _is_open(e.aspect):
            iv[e.lemma] = (r - span, r + span)
        else:
            iv[e.lemma] = (r, r)
    return iv


# Allen relations we distinguish (coarsened to what narrative overlap needs).
REL_BEFORE = "before"
REL_AFTER = "after"
REL_INCLUDES = "includes"        # a contains b (a during-inverse b)
REL_IS_INCLUDED = "is_included"  # a during b
REL_OVERLAPS = "overlaps"        # partial overlap / equals
REL_SIMULTANEOUS = "simultaneous"
REL_ABSTAIN = "abstain"

_OVERLAP_RELS = {REL_INCLUDES, REL_IS_INCLUDED, REL_OVERLAPS, REL_SIMULTANEOUS}


def _interval_relation(ia: Tuple[float, float], ib: Tuple[float, float]) -> str:
    """Coarsened Allen relation between two intervals by endpoint comparison."""
    a0, a1 = ia
    b0, b1 = ib
    if a1 < b0:
        return REL_BEFORE
    if b1 < a0:
        return REL_AFTER
    # they touch/overlap
    if a0 <= b0 and a1 >= b1 and (a0 < b0 or a1 > b1):
        return REL_INCLUDES
    if b0 <= a0 and b1 >= a1 and (b0 < a0 or b1 > a1):
        return REL_IS_INCLUDED
    if a0 == b0 and a1 == b1:
        return REL_SIMULTANEOUS
    return REL_OVERLAPS


def _connective_between(tagged, idx_a: int, idx_b: int) -> Optional[str]:
    lo, hi = (idx_a, idx_b) if idx_a < idx_b else (idx_b, idx_a)
    for k in range(lo + 1, hi):
        w = tagged[k][1]
        if w in OVERLAP_STRONG or w in OVERLAP_WEAK:
            return w
    # a clause-leading overlap connective before the earlier event ("While she cooked, they argued")
    for k in range(max(0, lo - 6), lo):
        w = tagged[k][1]
        if w in OVERLAP_STRONG or w in OVERLAP_WEAK:
            return w
    return None


def allen_overlap(a: str, b: str, events: Sequence[AspectualEvent], tagged,
                  rank: Dict[str, int], span: float = 1.0) -> str:
    """The overlap reasoner: does a OVERLAP b? Combines (1) an OVERLAP connective linking the two
    events' clauses (co-temporality; Allen inclusion, not precedence) with (2) the aspect-derived
    intervals (an imperfective ongoing interval CONTAINS a bounded neighbour). Returns an Allen
    relation. This is what the point-order control cannot produce -- it treats while/as/when as
    NEUTRAL and abstains, or falls back to telling-order precedence."""
    ea = next((e for e in events if e.lemma == a), None)
    eb = next((e for e in events if e.lemma == b), None)
    if ea is None or eb is None:
        return REL_ABSTAIN
    iv = event_intervals(events, rank, span=span)
    # (1) connective signal -- strongest for narrative overlap
    conn = _connective_between(tagged, ea.idx, eb.idx)
    if conn in OVERLAP_STRONG or (conn in OVERLAP_WEAK and (_is_open(ea.aspect) or _is_open(eb.aspect))):
        # co-temporal frame; aspect decides inclusion vs simultaneity
        if _is_open(ea.aspect) and not _is_open(eb.aspect):
            return REL_INCLUDES
        if _is_open(eb.aspect) and not _is_open(ea.aspect):
            return REL_IS_INCLUDED
        return REL_SIMULTANEOUS if ea.aspect == eb.aspect else REL_OVERLAPS
    # (2) aspect-only signal -- an ongoing (imperfective/durative) interval containing a bounded
    #     neighbour, available because we now extract the progressive AND (with lexical_aspect) the
    #     durative situation type the point-order extractor drops.
    if _is_open(ea.aspect) or _is_open(eb.aspect):
        return _interval_relation(iv[a], iv[b])
    # (3) both bounded, no overlap marker -> the DEFAULT narrative reading is a SEQUENCE (precedence),
    #     NOT overlap. Commit to precedence by text order (never 'simultaneous' on a tie) so the reasoner
    #     correctly answers "not overlap" on sequential pairs instead of abstaining.
    return REL_BEFORE if ea.idx <= eb.idx else REL_AFTER


def overlaps(a: str, b: str, events, tagged, rank, span: float = 1.0) -> Optional[bool]:
    """Boolean overlap judgement: True (overlap), False (strict precedence), None (abstain)."""
    rel = allen_overlap(a, b, events, tagged, rank, span=span)
    if rel in _OVERLAP_RELS:
        return True
    if rel in (REL_BEFORE, REL_AFTER):
        return False
    return None


def build_rank(events: Sequence[AspectualEvent], tagged) -> Dict[str, int]:
    """Reconstructed-chronology rank per lemma (reuses the landed constraint-graph + toposort over the
    aspect events' point projection). Perfective events order as before; imperfective events take part
    in the graph via their text position, then receive an ongoing interval around their rank."""
    pt = [e.as_event() for e in events]
    edges = M.build_constraint_edges(pt, tagged, use_connectives=True, cross_sentence=True)
    lemmas_text = [e.lemma for e in sorted(pt, key=lambda e: e.idx)]
    order = M._toposort(lemmas_text, edges)
    return {lem: i for i, lem in enumerate(order)}


# ---------------------------------------------------------------------------
# Self-test: byte-identity with the point-order extractor + the can-fail overlap cases.
# ---------------------------------------------------------------------------
def _selftest() -> None:
    # (A) ADDITIVITY / byte-identity: on text with NO progressive, the perfective/perfect/passive event
    #     set must be IDENTICAL to M.extract_events_punct (lemma, idx, tense) -- we only ADD progressives.
    checks = [
        "She won the marathon . She had trained for months .",
        "The bridge collapsed . The flood had weakened it .",
        "He arrived . She had already left .",
    ]
    for txt in checks:
        base, _ = M.extract_events_punct(txt)
        asp, _ = extract_events_aspect(txt)
        base_key = sorted((e.lemma, e.idx, e.tense) for e in base)
        # restrict aspect events to the point-order tenses for the identity comparison
        asp_pt = sorted((e.lemma, e.idx, e.tense) for e in asp if e.aspect != ASP_IMPERFECTIVE)
        assert base_key == asp_pt, f"ADDITIVITY BROKEN on {txt!r}:\n base={base_key}\n asp ={asp_pt}"

    # (B) THE DROPPED PROGRESSIVE is now recovered as an IMPERFECTIVE event. (Note: this pipeline uses
    #     the SURFACE token as the event key -- no lemmatiser -- so the progressive key is "cooking".)
    txt = "She was cooking dinner . They argued ."
    base, _ = M.extract_events_punct(txt)
    asp, tg = extract_events_aspect(txt)
    base_lemmas = {e.lemma for e in base}
    asp_lemmas = {e.lemma for e in asp}
    assert "cooking" not in base_lemmas, f"point-order extractor unexpectedly kept the progressive: {base_lemmas}"
    assert "cooking" in asp_lemmas, f"upstream fix FAILED to recover the progressive: {asp_lemmas}"
    imperf = [e for e in asp if e.aspect == ASP_IMPERFECTIVE]
    assert any(e.lemma == "cooking" for e in imperf), f"progressive not tagged IMPERFECTIVE: {imperf}"

    # (C) ASPECT-ONLY OVERLAP (no connective): the ongoing cooking CONTAINS the bounded arguing.
    rank = build_rank(asp, tg)
    assert overlaps("cooking", "argued", asp, tg, rank) is True, "aspect-only overlap not detected"

    # (D) CONNECTIVE OVERLAP: "While she cooked, they argued." -> overlap (co-temporal), not precedence.
    txt2 = "While she cooked dinner , they argued ."
    asp2, tg2 = extract_events_aspect(txt2)
    rank2 = build_rank(asp2, tg2)
    assert overlaps("cooked", "argued", asp2, tg2, rank2) is True, "connective overlap not detected"

    # (E) SEQUENTIAL CONTROL (must NOT be read as overlap): "She cooked dinner. Then they argued."
    txt3 = "She cooked dinner . Then they argued ."
    asp3, tg3 = extract_events_aspect(txt3)
    rank3 = build_rank(asp3, tg3)
    ov3 = overlaps("cooked", "argued", asp3, tg3, rank3)
    assert ov3 is not True, f"sequential pair wrongly read as overlap: {ov3}"

    print("[hdlab.aspect_interval] self-test PASS: additivity + progressive recovery + aspect/connective "
          "overlap + sequential control")


if __name__ == "__main__":
    _selftest()
