"""Per-event TEMPORAL-ORDER register: the queryable before/after layer over the
reconstructed chronological timeline.

This COMPOSES the already-landed discrete front-end (experiments/_temporal_ordering_multiframe:
tense/aspect + temporal connectives -> constraint graph -> topological sort) into a
PASSAGE-LEVEL register that answers `before(x, y)` / `order()`, and SWEEPS the order-register
REPRESENTATION (DISCRETE ordinal index vs CONTINUOUS magnitude line via the landed
hdlab.transitive_ordering) per the brain-foundational fork the bar asks for.

WHY THIS EXISTS (disk outranks brief): the mechanism is BUILT (_temporal_ordering[_multiframe],
both HARD_PASS) and even WIRED into hdlab.situation_reader as the TIME dimension -- but the live
wiring (`_read_timeline`) gates on `"had" in sentence` (drops connective-only reorderings) and runs
PER-SENTENCE (no cross-sentence flashback frame, no reference-time carried forward), and NOTHING
ever exposed a queryable before(x,y) or scored it on real prose with the narration-order floor +
info-free twin + CI + coverage. That measurement + representation sweep is what this module adds.

BRAIN GROUNDING (two-stage; research drill 2026-08-29, notes/problems/<slug>/research_*):
  STAGE 1 (linguistic front-end, DISCRETE -- PINNED-faithful): Reichenbach (1947) E/R/S -
    past-perfect (had+VBN) places the event PRIOR to reference time R; simple past AT it;
    temporal connectives impose discrete order constraints. Reference time R is a DISCOURSE
    variable carried ACROSS sentences (Past Discourse-Linking Hypothesis; Bastiaanse; Faroqi-Shah
    2015) -> the register runs over the WHOLE passage (fixes the per-sentence + had-gate wiring).
  STAGE 2 (the order register, REPRESENTATION SWEPT -- OUR-INVENTION-UNDER-TEST): the episodic
    substrate stores order on a CONTINUOUS drifting temporal-context / magnitude line (Howard &
    Kahana TCM 2002; MTL time cells, Eichenbaum 2014), which predicts a SYMBOLIC-DISTANCE EFFECT
    (far-apart events discriminated MORE reliably); a DISCRETE toposort predicts FLAT confidence.
    We build BOTH representations and let the real-prose data decide which the brain uses here.

Reuses (does NOT rebuild): _temporal_ordering_multiframe (extract + constraint edges + toposort),
_temporal_ordering (Event, text_order), hdlab.transitive_ordering (the continuous magnitude line).
ASCII-only. Deterministic given fixed seeds. Substrate-only (no LLM at inference).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_ordering as T            # noqa: E402  Event, text_order, extractor
from experiments import _temporal_ordering_multiframe as M  # noqa: E402  constraint graph + toposort

ABSTAIN = 0
BEFORE = -1   # x before y
AFTER = +1    # x after y


@dataclass
class OrderQuery:
    x: str
    y: str
    pred: int          # BEFORE / AFTER / ABSTAIN
    margin: float      # graded confidence (continuous line) or 1.0/0.0 (discrete/narration)
    distance: int      # |rank(x) - rank(y)| in the reconstructed chronology (for the distance effect)


# ---------------------------------------------------------------------------
# Front-end: extract events + constraint edges over a WHOLE passage.
# ---------------------------------------------------------------------------
def extract_passage(sents: Sequence[Sequence[str]], clause_pluperfect: bool = False):
    """Extract events + constraint edges over a full multi-sentence passage.

    Joins the passage into one punctuation-preserving stream so the multiframe mechanism's
    CROSS-SENTENCE tense-anteriority edges and connective edges fire (the live reader runs this
    per-sentence, which is the wiring gap). Returns (events, tagged, edges).

    clause_pluperfect=True applies the brain-faithful clause-level aux->participle binder
    (promote_clause_pluperfect) that recovers pluperfects the fixed-window extractor mistags."""
    text = " ".join(" ".join(s) for s in sents)
    ev, tg = M.extract_events_punct(text)
    if clause_pluperfect:
        ev = promote_clause_pluperfect(ev, tg)
    edges = M.build_constraint_edges(ev, tg, use_connectives=True, cross_sentence=True)
    return ev, tg, edges


# ---------------------------------------------------------------------------
# BRAIN-FAITHFUL pluperfect binding (drilled wall 2026-08-29): the perfect auxiliary 'had' binds
# to its past participle via a CLAUSE-LEVEL syntactic dependency (left-IFG parse of "have + V-en"),
# NOT a fixed 3-token window. The shared extractor's window misses "had the paragraph originally
# STOOD" (participle 4 tokens away, surface-tagged VBD) -> mis-typed SIMPLE_PAST -> wrong order.
# This additive promoter binds a 'had' to the NEXT content verb in its clause (bounded, with
# possession-'had' and finite-verb guards) so the pluperfect is recovered like the brain does.
# ---------------------------------------------------------------------------
_CLAUSE_BREAK = {".", "!", "?", ";", ":", ",", "--"}
_SUBORD = {"before", "after", "until", "till", "when", "while", "as", "because", "since",
           "though", "although", "if", "that", "which", "who", "where"}
_FINITE_VERB_POS = {"VBD", "VBZ", "VBP"}


def promote_clause_pluperfect(events: List[T.Event], tagged) -> List[T.Event]:
    """Additively promote events to PAST_PERFECT when a 'had' governs them across the clause (the
    brain's aux->participle dependency), fixing pluperfects the fixed-window extractor mistags.

    Rule (bounded, conservative): a content-verb event E is anterior (pp) if, scanning LEFT from E to
    the nearest clause break / subordinator, a 'had' is found with NO possession-object and NO other
    finite verb between the 'had' and E (so 'had' is the perfect auxiliary of E, not a possession verb
    or a different clause's aux). Only PROMOTES (never demotes) -> additive, cannot break a case the
    window already got right."""
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    idx_of_event = {e.idx: e for e in events}
    for e in events:
        if e.is_pp:
            continue
        i = e.idx
        had_pos = None
        j = i - 1
        while j >= 0:
            w, p = lows[j], poss[j]
            if w in _CLAUSE_BREAK or w in _SUBORD:
                break                     # clause boundary -> 'had' would be in another clause
            if w == "had":
                had_pos = j
                break
            if p in _FINITE_VERB_POS and j != i:
                break                     # an intervening finite verb -> 'had' governs THAT, not E
            j -= 1
        if had_pos is None:
            continue
        # possession guard: 'had' directly followed by a determiner/noun object with NO participle
        # before E would be a possession reading; require that E is the first content verb after 'had'
        # and nothing between them is itself a finite verb (already ensured) -> treat as perfect aux.
        between = lows[had_pos + 1:i]
        # reject obvious possession "had a/an/the/his ... <noun>" when E is far and looks like a new clause
        e.is_pp = True
        e.tense = T.TENSE_PAST_PERFECT
    return events


def _first_occurrence(events: Sequence[T.Event]) -> List[T.Event]:
    """Collapse duplicate lemmas to first occurrence (matches T.pairwise_accuracy / the toposort)."""
    seen, out = set(), []
    for e in sorted(events, key=lambda e: e.idx):
        if e.lemma not in seen:
            seen.add(e.lemma)
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# REPRESENTATION A -- DISCRETE ordinal toposort (the current mechanism).
# ---------------------------------------------------------------------------
class DiscreteOrderRegister:
    """Reconstructed chronology as a DISCRETE total order (constraint graph -> Kahn toposort).
    before(x,y) reads the ordinal ranks. Confidence is BINARY: 1.0 if a constraint path connects
    the pair (the mechanism has a cue), else it ABSTAINS (never confidently wrong)."""

    def __init__(self, events, tagged, edges):
        self.events = _first_occurrence(events)
        self.tagged = tagged
        self.edges = set(edges)
        text_lemmas = [e.lemma for e in self.events]
        self.order = M._toposort(text_lemmas, self.edges)          # chronological lemma order
        self.rank = {lem: i for i, lem in enumerate(self.order)}
        self.text_rank = {e.lemma: i for i, e in enumerate(self.events)}

    def _connected(self, x, y) -> bool:
        return M.confident_pair(self.edges, x, y)

    def before(self, x, y) -> OrderQuery:
        if x not in self.rank or y not in self.rank:
            return OrderQuery(x, y, ABSTAIN, 0.0, 0)
        dist = abs(self.rank[x] - self.rank[y])
        if not self._connected(x, y):
            # no cue -> abstain (the mechanism only commits where it has evidence)
            return OrderQuery(x, y, ABSTAIN, 0.0, dist)
        pred = BEFORE if self.rank[x] < self.rank[y] else (AFTER if self.rank[x] > self.rank[y] else ABSTAIN)
        return OrderQuery(x, y, pred, 1.0, dist)


# ---------------------------------------------------------------------------
# REPRESENTATION B -- CONTINUOUS magnitude line (the landed transitive_ordering primitive).
# ---------------------------------------------------------------------------
class ContinuousOrderRegister:
    """Reconstructed chronology on a CONTINUOUS bounded MAGNITUDE LINE (hdlab.transitive_ordering:
    delta-rule settling of pairwise precedence premises -> FHRR magnitude register -> native FPE
    read-out). Higher coordinate = LATER in time. before(x,y) = sign(coord(y)-coord(x)); the
    coordinate GAP is a GRADED confidence margin that (per TCM) should grow with temporal distance."""

    def __init__(self, events, tagged, edges, d: int = 1024, seed: int = 0):
        import torch
        from hdlab.transitive_ordering import TransitiveOrderingLine
        self.events = _first_occurrence(events)
        self.tagged = tagged
        self.edges = set(edges)
        self.lemmas = [e.lemma for e in self.events]
        self.idx = {lem: i for i, lem in enumerate(self.lemmas)}
        self.text_rank = dict(self.idx)
        n = len(self.lemmas)
        # premises: an edge (u earlier, v later) => v is 'bigger' on the time line => winner=v, loser=u.
        premises: List[Tuple[int, int]] = []
        for (u, v) in self.edges:
            if u in self.idx and v in self.idx and u != v:
                premises.append((self.idx[v], self.idx[u]))   # (winner=later, loser=earlier)
        self._degenerate = (n < 2 or not premises)
        self._coord: Dict[str, float] = {}
        # discrete toposort rank is used ONLY for the distance covariate (independent of the line's coord)
        self.order = M._toposort(self.lemmas, self.edges)
        self.rank = {lem: i for i, lem in enumerate(self.order)}
        if not self._degenerate:
            gen = torch.Generator().manual_seed(seed)
            line = TransitiveOrderingLine(n, d, gen, seed=seed)
            line.integrate(premises, seed=seed)
            self._coord = {lem: line.coord(self.idx[lem]) for lem in self.lemmas}

    def _connected(self, x, y) -> bool:
        return M.confident_pair(self.edges, x, y)

    def before(self, x, y) -> OrderQuery:
        if x not in self.idx or y not in self.idx:
            return OrderQuery(x, y, ABSTAIN, 0.0, 0)
        dist = abs(self.rank.get(x, 0) - self.rank.get(y, 0))
        if self._degenerate or not self._connected(x, y):
            return OrderQuery(x, y, ABSTAIN, 0.0, dist)
        cx, cy = self._coord.get(x, 0.0), self._coord.get(y, 0.0)
        gap = abs(cx - cy)
        pred = BEFORE if cx < cy else (AFTER if cx > cy else ABSTAIN)
        return OrderQuery(x, y, pred, gap, dist)


# ---------------------------------------------------------------------------
# FLOOR -- narration order (text order == event order). The thing to beat.
# ---------------------------------------------------------------------------
class NarrationOrderFloor:
    """The default reader hypothesis: chronological order == the order events are TOLD. Commits on
    EVERY pair (it has no notion of a missing cue) -> this is the strongest naive floor."""

    def __init__(self, events, tagged, edges=None):
        self.events = _first_occurrence(events)
        self.text_rank = {e.lemma: i for i, e in enumerate(self.events)}

    def before(self, x, y) -> OrderQuery:
        if x not in self.text_rank or y not in self.text_rank:
            return OrderQuery(x, y, ABSTAIN, 0.0, 0)
        rx, ry = self.text_rank[x], self.text_rank[y]
        pred = BEFORE if rx < ry else (AFTER if rx > ry else ABSTAIN)
        return OrderQuery(x, y, pred, 1.0, abs(rx - ry))


# ---------------------------------------------------------------------------
# COMPOSED register -- the ACTUAL brain-faithful reader: DEFAULT narration order,
# OVERRIDDEN by the cue mechanism where it has evidence (the bar's exact wording:
# "default narration order, OVERRIDDEN by the extracted tense/aspect + connectives").
# ---------------------------------------------------------------------------
class ComposedRegister:
    """DEFAULT = narration order; OVERRIDE = the cue mechanism (discrete or continuous) wherever it
    commits. This is the per-event temporal-ORDER register the bar asks for: it never abstains (like
    a real reader, it falls back to narration when it has no cue), so it is directly comparable to the
    narration floor on the FULL population -- equal on no-cue pairs, better on cue-bearing pairs."""

    def __init__(self, mechanism, floor):
        self.mech = mechanism
        self.floor = floor

    def before(self, x, y) -> OrderQuery:
        q = self.mech.before(x, y)
        if q.pred != ABSTAIN:
            return q
        f = self.floor.before(x, y)
        # tag the distance from the mechanism's chronology when available (for the distance effect)
        return OrderQuery(x, y, f.pred, f.margin, q.distance or f.distance)


# ---------------------------------------------------------------------------
# INFO-FREE TWIN -- same events + text positions, tense labels SHUFFLED (same shape,
# scrambled information). Should collapse to the narration floor if the win is real.
# ---------------------------------------------------------------------------
def make_twin_events(events: Sequence[T.Event], rng) -> List[T.Event]:
    """Permute the (tense, is_pp) labels across events -> destroys WHICH events are anterior while
    keeping the SAME NUMBER of past-perfect events and the SAME text positions (matched shape)."""
    evs = [T.Event(lemma=e.lemma, idx=e.idx, pos=e.pos, tense=e.tense, is_pp=e.is_pp) for e in events]
    labels = [(e.tense, e.is_pp) for e in evs]
    perm = list(range(len(labels)))
    rng.shuffle(perm)
    for i, e in enumerate(evs):
        e.tense, e.is_pp = labels[perm[i]]
    return evs


def make_twin_edges(edges, rng):
    """Info-free twin at the CONSTRAINT level: keep the SAME constrained pairs (identical coverage /
    which-pairs-committed) but RANDOMIZE each edge's DIRECTION (p=0.5 flip). Destroys BOTH the tense
    AND the connective information uniformly while matching the mechanism's shape, so a surviving win
    can only come from correctly-read cue DIRECTION, not from committing on these pairs. Returns a new
    edge set over the same nodes."""
    twin = set()
    for (u, v) in edges:
        if rng.random() < 0.5:
            twin.add((v, u))
        else:
            twin.add((u, v))
    return twin


def build_register(sents, kind: str = "discrete", d: int = 1024, seed: int = 0,
                   twin_rng=None):
    """Build an order register over a passage. kind in {discrete, continuous, narration, twin_discrete,
    twin_continuous}. twin_* shuffle the tense labels before rebuilding constraint edges (info-free)."""
    ev, tg, edges = extract_passage(sents)
    if kind in ("twin_discrete", "twin_continuous"):
        if twin_rng is None:
            import random
            twin_rng = random.Random(seed)
        ev = make_twin_events(ev, twin_rng)
        edges = M.build_constraint_edges(ev, tg, use_connectives=True, cross_sentence=True)
        kind = "discrete" if kind == "twin_discrete" else "continuous"
    if kind == "narration":
        return NarrationOrderFloor(ev, tg, edges)
    if kind == "discrete":
        return DiscreteOrderRegister(ev, tg, edges)
    if kind == "continuous":
        return ContinuousOrderRegister(ev, tg, edges, d=d, seed=seed)
    raise ValueError(f"unknown register kind {kind}")


# ---------------------------------------------------------------------------
# Scoring: before/after accuracy against gold (earlier, later) lemma pairs.
# ---------------------------------------------------------------------------
def score_pairs(reg, gold_pairs: Sequence[Tuple[str, str]]):
    """gold_pairs = (earlier_lemma, later_lemma). A prediction is CORRECT iff before(earlier, later)
    == BEFORE. Returns (n_correct, n_committed, n_abstain, per_pair) -- abstentions are NOT scored as
    errors (selective accuracy); the caller also reports COVERAGE = n_committed / n_total."""
    n_correct = n_committed = n_abstain = 0
    per_pair = []
    for earlier, later in gold_pairs:
        q = reg.before(earlier, later)
        if q.pred == ABSTAIN:
            n_abstain += 1
            per_pair.append({"pair": (earlier, later), "pred": "ABSTAIN", "margin": q.margin,
                             "distance": q.distance, "correct": None})
            continue
        n_committed += 1
        correct = (q.pred == BEFORE)
        n_correct += int(correct)
        per_pair.append({"pair": (earlier, later), "pred": ("BEFORE" if q.pred == BEFORE else "AFTER"),
                         "margin": q.margin, "distance": q.distance, "correct": correct})
    return n_correct, n_committed, n_abstain, per_pair
