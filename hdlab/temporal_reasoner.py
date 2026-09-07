"""hdlab/temporal_reasoner.py -- a glass-box TEMPORAL REASONER over an extracted timeline
(integrated BEFORE/AFTER + Allen OVERLAP + RELATIVE duration), the TIME-channel inference organ.

Promoted (owner-DONE reason_over_event_time_order_and_duration_on_a_modern_gold, Q111 strategy landing
2026-09-06) from the solver cells experiments/exp_temporal_reason_integrated_v1 (the integrated
before/after reasoner: cue + TIMEX event-LOCAL date anchoring + transitive closure + per-judgment
SIGNAL-CLASS provenance) and experiments/exp_temporal_reason_overlap_v1 / _duration_v1 (Allen overlap
and the relative-duration magnitude line). The load-bearing primitives `_reach` and `integrated_order`
are UNCHANGED (byte-identical; the landing witness verification/test_temporal_reasoner_landing.py asserts
inspect.getsource identity against exp_temporal_reason_integrated_v1). This module is the REUSABLE
reasoning core -- the corpus-measurement harnesses (TB-Dense parse/align/bootstrap) stay in experiments.

This is the SECOND inference organ over the situation model (after hdlab.causal_reasoner /
hdlab.spatial_relational_model). It CONSUMES the reader's OWN extracted timeline (the aspect events +
constraint edges over the passage) and REASONS over it; it does NOT re-extract or re-type events.

BRAIN GROUNDING (all PINNED -- copy the COMPUTATION):
  * BEFORE/AFTER: Reichenbach (1947) E/R/S tense-place; TIMEX reference-time anchoring is tense-as-anaphora
    / discourse reference time (Partee 1973; Webber 1988) -- an event binds to a date in its OWN clause
    (event-LOCAL, not carried-forward -- the probe showed carry-forward HURTS). Transitive CLOSURE =
    relational integration (Frank/Rudy/O'Reilly; the same settling that builds the magnitude line).
  * OVERLAP: Allen (1983) interval algebra over aspect-derived START/END intervals (Smith 1991 viewpoint
    aspect: perfective=closed, imperfective/progressive=open) + a while/during co-temporal frame. Delegated
    to hdlab.aspect_interval (the promoted UPSTREAM aspect->interval extractor).
  * RELATIVE DURATION: the parietal MAGNITUDE LINE (Walsh 2003 ATOM) -- REUSES the landed glass-box
    reasoning primitive hdlab.transitive_ordering.TransitiveOrderingLine (integrate stated 'X lasted longer
    than Y' premises, read the UN-STATED 'which lasted longer' pair off the settled line).
  * GLASS-BOX PROVENANCE (source-monitoring, Johnson 1993): every before/after judgment reports the SIGNAL
    CLASS that resolved it (cue / date / iconicity-fallback / vague), so the reasoner reports WHY, not one
    opaque number -- and returns "unknown -- needs world knowledge" on an implicit-event query it cannot
    place from the narrated timeline.

OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the event-local date-anchoring window, the edge-construction
from dates, the ongoing-interval half-width `span`, the magnitude-line settling params.

DEPENDENCY NOTE (honest deviation, reported at landing): imports the SHARED temporal front-end
experiments._temporal_ordering_multiframe (M) + experiments._temporal_order_register (R) -- the SAME
experiments modules hdlab.situation_reader itself imports; promoting them is a separate larger landing and
OUT OF SCOPE for this ADDITIVE promotion. Introduces NO new cross-layer edge (the reader already has it).
Glass-box, deterministic, stdlib+numpy+torch (via transitive_ordering) -- NO external LLM (the invariant).
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import aspect_interval as AI                       # noqa: E402  aspect -> interval + Allen overlap
from experiments import _temporal_ordering_multiframe as M    # noqa: E402  build_constraint_edges (shared front-end)
from experiments import _temporal_order_register as R         # noqa: E402  DiscreteOrderRegister + BEFORE/AFTER/ABSTAIN

BEFORE, AFTER, ABSTAIN = R.BEFORE, R.AFTER, R.ABSTAIN

UNKNOWN = "unknown -- needs world knowledge"   # the honest implicit-event abstention (glass-box)


# ---------------------------------------------------------------------------
# BEFORE/AFTER core -- promoted VERBATIM from exp_temporal_reason_integrated_v1
# (byte-identical; the landing witness asserts inspect.getsource identity).
# ---------------------------------------------------------------------------
def _reach(adj, a, b):
    """Directed reachability a->b (transitive closure by DFS)."""
    stack, seen = [a], {a}
    while stack:
        n = stack.pop()
        if n == b:
            return True
        for m in adj.get(n, ()):
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return False


def integrated_order(lemma_a, lemma_b, cue_adj, date_adj):
    """Read order off the INTEGRATED closed graph. Returns (pred, signal_class).
    Priority: an explicit tense/connective CUE path -> a TIMEX DATE path -> abstain (caller falls back
    to iconicity). Closure is the reachability itself (a path of length>1 = transitive inference)."""
    # cue closure
    if _reach(cue_adj, lemma_a, lemma_b):
        return BEFORE, "cue"
    if _reach(cue_adj, lemma_b, lemma_a):
        return AFTER, "cue"
    # date closure (integrates cue+date edges)
    if _reach(date_adj, lemma_a, lemma_b):
        return BEFORE, "date"
    if _reach(date_adj, lemma_b, lemma_a):
        return AFTER, "date"
    return ABSTAIN, "none"


def _key(x):
    """Normalise a query arg to the event key space (rightmost token, lowercased) -- the aspect events'
    keys are surface tokens (Event.lemma=low). A caller may pass the surface token directly."""
    if x is None:
        return None
    tok = str(x).strip().split()
    return tok[-1].lower() if tok else None


# ---------------------------------------------------------------------------
# THE TEMPORAL REASONER (over the reader's OWN extracted timeline)
# ---------------------------------------------------------------------------
class TemporalReasoner:
    """Glass-box reasoner over an extracted timeline. Built from the reader's OWN aspect events + the
    passage constraint graph. Answers before/after (with signal-class provenance), Allen overlap, and --
    given stated duration premises -- relative duration off the magnitude line. Never re-extracts."""

    def __init__(self, events: Sequence["AI.AspectualEvent"], tagged, rank: Dict[str, int],
                 cue_adj: Dict[str, set], date_adj: Dict[str, set], span: float = 1.0) -> None:
        self.events = list(events)
        self.tagged = tagged
        self.rank = rank
        self.cue_adj = cue_adj
        self.date_adj = date_adj
        self.span = float(span)
        self._idx = {e.lemma: e.idx for e in self.events}

    @classmethod
    def from_text(cls, text: str, lexical_aspect: bool = True,
                  date_anchors: Optional[Dict[str, float]] = None, span: float = 1.0) -> "TemporalReasoner":
        """Build the reasoner from raw passage text. `date_anchors` (optional) maps an event key -> a
        comparable event-LOCAL date value (Reichenbach R via TIMEX); when absent, the date channel is
        empty and before/after rides on cue closure + the iconicity fallback (the reader has no TIMEX
        extractor today -- the honest gap, same shape as the spatial reasoner's projective-position gap).
        lexical_aspect=True adds Vendler durative situation-type intervals for OVERLAP -- it changes ONLY
        the interval character, never the point-order tense set (aspect_interval byte-identity guarantee)."""
        ev, tg = AI.extract_events_aspect(text, lexical_aspect=lexical_aspect)
        rank = AI.build_rank(ev, tg)
        ev_point = [e.as_event() for e in ev]
        cue_edges = M.build_constraint_edges(ev_point, tg, use_connectives=True, cross_sentence=True)
        cue_adj: Dict[str, set] = defaultdict(set)
        date_adj: Dict[str, set] = defaultdict(set)
        for (u, v) in cue_edges:
            cue_adj[u].add(v)
            date_adj[u].add(v)          # integrate cue edges into the date graph (union closure)
        if date_anchors:
            local = {k: d for k, d in date_anchors.items() if d is not None}
            lems = list(local)
            for i in range(len(lems)):
                for j in range(len(lems)):
                    if i == j:
                        continue
                    if local[lems[i]] < local[lems[j]]:
                        date_adj[lems[i]].add(lems[j])
        return cls(ev, tg, rank, cue_adj, date_adj, span=span)

    # -- BEFORE / AFTER (with glass-box signal-class provenance) --
    def before(self, a, b) -> Tuple[str, str]:
        """'Did A happen before or after B?' Returns (label, signal_class).
        label in {'before', 'after', UNKNOWN}; signal in {'cue', 'date', 'iconicity', 'vague'}.
        Priority: explicit tense/connective CUE path -> TIMEX DATE path -> iconicity (telling order)
        fallback. Returns (UNKNOWN, 'vague') when either event is not on the narrated timeline (an
        implicit-event query the story-internal reader cannot place)."""
        la, lb = _key(a), _key(b)
        if la is None or lb is None or la not in self._idx or lb not in self._idx:
            return UNKNOWN, "vague"
        pred, sig = integrated_order(la, lb, self.cue_adj, self.date_adj)
        if pred == BEFORE:
            return "before", sig
        if pred == AFTER:
            return "after", sig
        # iconicity fallback: EXACT mention order (telling order == event order)
        return ("before" if self._idx[la] < self._idx[lb] else "after"), "iconicity"

    def order_signal(self, a, b) -> str:
        """The signal class that resolved (or would resolve) the before/after judgment, without the label."""
        return self.before(a, b)[1]

    # -- OVERLAP (Allen interval intersection over aspect-derived endpoints) --
    def overlaps(self, a, b) -> Optional[bool]:
        """Boolean overlap: True (co-temporal / inclusion), False (strict precedence), None (abstain)."""
        return AI.overlaps(_key(a), _key(b), self.events, self.tagged, self.rank, span=self.span)

    def allen(self, a, b) -> str:
        """The coarsened Allen relation (before/after/includes/is_included/overlaps/simultaneous/abstain)."""
        return AI.allen_overlap(_key(a), _key(b), self.events, self.tagged, self.rank, span=self.span)

    def event_keys(self) -> List[str]:
        """The event key space (surface tokens) the reasoner can answer over -- enumerate before querying."""
        return [e.lemma for e in self.events]


# ---------------------------------------------------------------------------
# RELATIVE DURATION -- the magnitude-line reasoning primitive (reuses transitive_ordering)
# ---------------------------------------------------------------------------
class RelativeDurationLine:
    """'Which of two events lasted longer?' off the landed hdlab.transitive_ordering MAGNITUDE LINE.
    Integrate stated pairwise 'X lasted longer than Y' premises; read the UN-STATED pair off the settled
    line by native FPE read-out (NOT a symbolic sort). PROVEN 1.0 on un-stated transitive pairs; the
    info-free twin (shuffled durations) collapses to chance. torch is imported LAZILY inside integrate()."""

    def __init__(self, items: Sequence[str], d: int = 1024, seed: int = 3) -> None:
        self.items = list(items)
        self.index = {it: i for i, it in enumerate(self.items)}
        self._d = int(d)
        self._seed = int(seed)
        self._line = None

    def integrate(self, premises: Sequence[Tuple[str, str]]) -> "RelativeDurationLine":
        """premises = [(longer_item, shorter_item), ...] -- possibly a partial/overlapping adjacent chain;
        relational integration fills the un-stated comparisons. Returns self."""
        import torch
        from hdlab.transitive_ordering import TransitiveOrderingLine
        gen = torch.Generator().manual_seed(self._seed)
        L = TransitiveOrderingLine(len(self.items), self._d, gen, seed=self._seed)
        idxp = [(self.index[a], self.index[b]) for (a, b) in premises
                if a in self.index and b in self.index]
        L.integrate(idxp, seed=self._seed)
        self._line = L
        return self

    def longer(self, a, b) -> Optional[bool]:
        """True iff a lasted longer than b (read off the integrated line), False iff shorter, None if
        undecidable / an item was never integrated."""
        if self._line is None or a not in self.index or b not in self.index:
            return None
        c = self._line.compare(self.index[a], self.index[b])
        return True if c > 0 else (False if c < 0 else None)


# ---------------------------------------------------------------------------
# Self-test: before/after + overlap over a real doc, relative-duration primitive.
# ---------------------------------------------------------------------------
def _selftest() -> None:
    # (A) OVERLAP over a real passage: the ongoing 'cooking' CONTAINS the bounded 'argued'.
    tr = TemporalReasoner.from_text("She was cooking dinner . They argued .")
    assert tr.overlaps("cooking", "argued") is True, "aspect-only overlap not detected"

    # (B) BEFORE/AFTER with a cue: past-perfect 'had left' precedes 'arrived'; provenance = cue.
    tr2 = TemporalReasoner.from_text("He arrived . She had left .")
    lbl, sig = tr2.before("left", "arrived")
    assert lbl == "before" and sig in ("cue", "date"), f"cue before/after failed: {lbl}/{sig}"

    # (C) IMPLICIT-EVENT abstention: an event not on the narrated timeline -> UNKNOWN / vague.
    lbl3, sig3 = tr2.before("left", "vanished")
    assert lbl3 == UNKNOWN and sig3 == "vague", f"implicit-event query not abstained: {lbl3}/{sig3}"

    # (D) RELATIVE DURATION: an adjacent chain integrates transitively; an un-stated pair reads correctly.
    items = ["blink", "sip", "song", "meal", "movie", "flight", "war", "era"]
    prem = [(items[i + 1], items[i]) for i in range(len(items) - 1)]   # each next lasts longer
    line = RelativeDurationLine(items).integrate(prem)
    assert line.longer("era", "blink") is True, "un-stated transitive relative-duration failed"
    assert line.longer("blink", "war") is False, "un-stated transitive relative-duration failed (reverse)"

    print("[hdlab.temporal_reasoner] self-test PASS: overlap + before/after(provenance) + implicit-event "
          "abstain + relative-duration magnitude line")


if __name__ == "__main__":
    _selftest()
