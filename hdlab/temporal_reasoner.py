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

# --- IMPLICIT-EVENT script/schema override (Q111 p6 wire; Sec 4j/7.5 of the SOLVED). The story-internal
# timeline can only order events the text NARRATES; on an IMPLICIT-event query (an event not on the narrated
# timeline) the reader abstains (UNKNOWN). The LATENT hdlab.temporal_script_schema (177,800 Chambers-Jurafsky
# narrative-chain verb-pair orders mined from ROCStories, a STATIC ADMISSIBLE FOUNDATION asset) answers exactly
# those queries at its validated turf (TRACIE implicit-event 0.60 on the covered 29%, vs today's abstention).
# It is consulted ONLY in the abstention branch, gated on CONFIDENCE (enough evidence + a decisive margin), so
# the NARRATED path (cue/date/iconicity) is BYTE-IDENTICAL and an asset-less environment abstains as before.
# The thresholds are OUR-INVENTION-UNDER-TEST (swept in exp_temporal_script_override_v1; the validated confident
# subset is evidence>=30 / |p-0.5|>=0.1 at 0.625; E_MIN=10 is the permissive-but-confident operating point in the
# recommended 10-30 band).
SCRIPT_E_MIN = 10     # min two-directional co-occurrence evidence to trust the mined verb-pair order
SCRIPT_M_MIN = 0.1    # min |p_before - 0.5| margin (confidence) required to override the honest abstention

_SCRIPT_SCHEMA = None  # process-wide cache of the frozen script/schema organ (loaded at most once; ~3MB asset)


def _script_schema():
    """Lazily load + cache the frozen temporal_script_schema organ. Returns an EMPTY (abstaining) organ when the
    asset is absent -- so consulting it is asset-less-safe (every readout -> None -> the reasoner keeps UNKNOWN).
    PREFERS the BROADER tense-agnostic-mined store (454,129 verb-pairs; owner-DONE
    grow_a_broad_causal_event_order_store, Q111 landing 2026-09-08; +0.036 CI-sep on TRACIE implicit-event
    ordering over the 177,800-pair seed, coverage 0.29->0.607) when present, falling back to the seed, then empty.
    Same gitignored-asset posture as the seed (degrades gracefully; rebuild via
    experiments/exp_broaden_causal_order_store_v1.py). The NARRATED timeline path stays byte-identical either way --
    the store fires ONLY on off-timeline implicit-event queries, confident-gated (SCRIPT_E_MIN + SCRIPT_M_MIN);
    the swap enriches only the implicit-event branch (blast radius = that branch; test_temporal_reasoner_organ
    18/18 unchanged)."""
    global _SCRIPT_SCHEMA
    if _SCRIPT_SCHEMA is None:
        import os as _os
        from hdlab.temporal_script_schema import TemporalScriptSchema, CHAINS_ASSET
        _broad = _os.path.join(_os.path.dirname(_os.path.dirname(CHAINS_ASSET)),
                               "exp_broaden_causal_order_store_v1", "chains_broad.json")
        _SCRIPT_SCHEMA = (TemporalScriptSchema.load(_broad) if TemporalScriptSchema.available(_broad)
                          else TemporalScriptSchema.load())
    return _SCRIPT_SCHEMA


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
                 cue_adj: Dict[str, set], date_adj: Dict[str, set], span: float = 1.0,
                 use_script_schema: bool = True,
                 use_coherence: bool = False, coherence_reader=None) -> None:
        self.events = list(events)
        self.tagged = tagged
        self.rank = rank
        self.cue_adj = cue_adj
        self.date_adj = date_adj
        self.span = float(span)
        self._idx = {e.lemma: e.idx for e in self.events}
        # consult the latent script/schema organ on the IMPLICIT-event abstention branch (default-on; ADDITIVE +
        # narrated-path byte-identical). Pass False for the pure story-internal reasoner (or an asset-less witness).
        self.use_script_schema = bool(use_script_schema)
        # SDRT-lite COHERENCE OVERRIDE of the iconicity fallback (Q111 p7 wire; the SDRT discourse-coherence
        # reader). DEFAULT-OFF (the coherence channel lands off, per the SOLVED's measured not-yet-full-population
        # net-win): when off, before() is BYTE-IDENTICAL to the pre-wire reasoner (the entire override path is
        # gated + unreachable). When on, an ICONICITY judgment (and ONLY an iconicity judgment -- never a cue/date
        # judgment, never the p6 script/implicit-event branch) is REVERSED when hdlab.coherence_reader confidently
        # infers EXPLANATION (the later-narrated clause CAUSES the earlier -> event order reverses telling order).
        self.use_coherence = bool(use_coherence)
        self._coherence = coherence_reader   # a hdlab.coherence_reader.CoherenceReader; lazily default-built when on

    @classmethod
    def from_text(cls, text: str, lexical_aspect: bool = True,
                  date_anchors: Optional[Dict[str, float]] = None, span: float = 1.0,
                  use_script_schema: bool = True,
                  use_coherence: bool = False, coherence_reader=None) -> "TemporalReasoner":
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
        return cls(ev, tg, rank, cue_adj, date_adj, span=span, use_script_schema=use_script_schema,
                   use_coherence=use_coherence, coherence_reader=coherence_reader)

    def _script_order(self, la, lb) -> Optional[str]:
        """Consult the latent SCRIPT/SCHEMA organ for the typical order of two event TYPES (Chambers-Jurafsky
        narrative chains). Returns 'before'/'after' ONLY when the mined evidence is CONFIDENT (>= SCRIPT_E_MIN
        two-directional count AND |p_before-0.5| >= SCRIPT_M_MIN margin), else None (keep the honest abstention).
        Asset-less-safe: the organ abstains (p_before None) when the frozen counts are absent -> None."""
        org = _script_schema()
        p = org.p_before(la, lb)
        if p is None:
            return None
        if org.evidence(la, lb) < SCRIPT_E_MIN or abs(p - 0.5) < SCRIPT_M_MIN:
            return None
        return "before" if p >= 0.5 else "after"

    # -- BEFORE / AFTER (with glass-box signal-class provenance) --
    def before(self, a, b) -> Tuple[str, str]:
        """'Did A happen before or after B?' Returns (label, signal_class).
        label in {'before', 'after', UNKNOWN}; signal in {'cue','date','iconicity','coherence','script','vague'}.
        Priority: explicit tense/connective CUE path -> TIMEX DATE path -> iconicity (telling order)
        fallback. On an IMPLICIT-event query (an event not on the narrated timeline) the story-internal reader
        cannot place it -- it consults the latent script/schema organ (typical event-type order) and returns its
        verdict with signal 'script' when confident, else returns (UNKNOWN, 'vague'). The NARRATED path (both
        events on the timeline) is BYTE-IDENTICAL to the pre-wire reasoner when the coherence channel is off (the
        script consult + the coherence override are unreachable there); with use_coherence ON, an ICONICITY
        judgment (and ONLY an iconicity judgment) is reversed to signal 'coherence' when the SDRT-lite reader
        confidently infers EXPLANATION."""
        la, lb = _key(a), _key(b)
        if la is None or lb is None:
            return UNKNOWN, "vague"
        if la not in self._idx or lb not in self._idx:
            # IMPLICIT-EVENT path: at least one event is not on the narrated timeline. Consult the script/schema
            # organ (typical event-type order) when confident; else keep the honest abstention. ADDITIVE.
            if self.use_script_schema:
                so = self._script_order(la, lb)
                if so is not None:
                    return so, "script"
            return UNKNOWN, "vague"
        pred, sig = integrated_order(la, lb, self.cue_adj, self.date_adj)
        if pred == BEFORE:
            return "before", sig
        if pred == AFTER:
            return "after", sig
        # iconicity fallback: EXACT mention order (telling order == event order)
        label = "before" if self._idx[la] < self._idx[lb] else "after"
        # SDRT-lite COHERENCE OVERRIDE (default-OFF; ADDITIVE): on a NO-CUE narrated pair where the coherence
        # reader confidently infers EXPLANATION (later-narrated clause CAUSES the earlier), the event order is the
        # REVERSE of the telling order -> flip the iconicity label. Reachable ONLY here (never a cue/date judgment,
        # never the implicit-event/script branch above) -> BYTE-IDENTICAL to the pre-wire reasoner when off.
        if self.use_coherence:
            ov = self._coherence_override(la, lb, label)
            if ov is not None:
                return ov, "coherence"
        return label, "iconicity"

    def _clause_span(self, key):
        """(words, lemmas) of the clause/sentence containing the narrated event `key`, reconstructed from the
        (surface, low, pos) tagged token stream for the coherence reader. The tagged stream's `low` field is the
        lowercased surface form -- exactly the key space the reader's force/goal engines + self._idx use. Falls
        back to [key] when the stream is unavailable (matching the SOLVED's single-lemma no-regress spans)."""
        idx = self._idx.get(key)
        tagged = self.tagged
        if idx is None or not tagged or idx >= len(tagged):
            return [key], [key]
        _ends = (".", "!", "?", ";")
        lo = 0
        for i in range(idx - 1, -1, -1):
            if tagged[i][0] in _ends:
                lo = i + 1
                break
        hi = len(tagged)
        for i in range(idx, len(tagged)):
            if tagged[i][0] in _ends:
                hi = i
                break
        words = [tagged[i][0] for i in range(lo, hi) if str(tagged[i][0]).isalpha()]
        lemmas = [tagged[i][1] for i in range(lo, hi) if str(tagged[i][1]).isalpha()]
        if not words or not lemmas:
            return [key], [key]
        return words, lemmas

    def _coherence_override(self, la, lb, base_label) -> Optional[str]:
        """Consult the SDRT-lite hdlab.coherence_reader on the two NARRATED events (fed in TELLING order);
        if it confidently infers EXPLANATION (the later-narrated clause CAUSES the earlier -> the event order
        is the reverse of the telling order), return the FLIPPED before/after label; else None (keep iconicity).
        Reachable ONLY on the iconicity fallback of a narrated pair -- the cue/date + p6 script branches are
        never routed here. Degrades gracefully (returns None) if the coherence organ / its assets are absent."""
        try:
            from hdlab.coherence_reader import CoherenceReader, CoherenceConfig, PlausibilityConfig, EXPLANATION
            rd = self._coherence
            if rd is None:
                # the goal engine is default-ON WITHIN the coherence channel (the net-positive addition); the
                # channel itself is default-off (this whole path is gated on use_coherence).
                rd = CoherenceReader(CoherenceConfig(plaus=PlausibilityConfig(goal=True)))
                self._coherence = rd
            # feed the reader in TELLING order (first-narrated unit = the reader's `a`)
            first, second = (la, lb) if self._idx[la] <= self._idx[lb] else (lb, la)
            aw, al = self._clause_span(first)
            bw, bl = self._clause_span(second)
            rel = rd.relate(aw, al, bw, bl)
            if rel.label == EXPLANATION:
                return "after" if base_label == "before" else "before"
        except Exception:
            return None
        return None

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

    # (B2) NARRATED-path BYTE-IDENTITY under the script wire: when both events are on the timeline the script
    # consult is UNREACHABLE, so before() is identical whether the script organ is on or off.
    on_r = TemporalReasoner.from_text("He arrived . She had left .", use_script_schema=True)
    off_r = TemporalReasoner.from_text("He arrived . She had left .", use_script_schema=False)
    for pr in (("left", "arrived"), ("arrived", "left")):
        assert on_r.before(*pr) == off_r.before(*pr), \
            ("narrated path not byte-identical under script wire", pr, on_r.before(*pr), off_r.before(*pr))

    # (C) IMPLICIT-EVENT abstention (pure story-internal, script organ OFF): an event not on the narrated timeline
    # -> UNKNOWN / vague. The pre-wire behaviour, preserved under use_script_schema=False (asset-INDEPENDENT).
    tr2b = TemporalReasoner.from_text("He arrived . She had left .", use_script_schema=False)
    lbl3, sig3 = tr2b.before("left", "vanished")
    assert lbl3 == UNKNOWN and sig3 == "vague", f"implicit-event query not abstained: {lbl3}/{sig3}"

    # (C2) SCRIPT/SCHEMA wire (the NEW capability, Sec 4j/7.5): on an IMPLICIT-event query (neither event on the
    # timeline) the reasoner consults the latent temporal_script_schema and answers with signal 'script' when the
    # mined order is CONFIDENT; else it keeps the honest abstention. Asset-gated + graceful.
    from hdlab.temporal_script_schema import TemporalScriptSchema
    if TemporalScriptSchema.available():
        org = _script_schema()
        pa, pb = "offered", "accepted"                                 # a confident mined pair (offer BEFORE accept)
        p_ab = org.p_before(pa, pb)
        conf = (p_ab is not None and org.evidence(pa, pb) >= SCRIPT_E_MIN and abs(p_ab - 0.5) >= SCRIPT_M_MIN)
        tri = TemporalReasoner.from_text("It rained all day .")        # narrates neither pa nor pb -> implicit path
        lbl4, sig4 = tri.before(pa, pb)
        if conf:
            assert sig4 == "script" and lbl4 == org.order(pa, pb), \
                f"script wire did not fire on a confident pair: {lbl4}/{sig4} (expected {org.order(pa, pb)}/script)"
            lbl5, sig5 = TemporalReasoner.from_text("It rained all day .", use_script_schema=False).before(pa, pb)
            assert lbl5 == UNKNOWN and sig5 == "vague", f"script-off did not keep abstention: {lbl5}/{sig5}"
            print("[selftest] script wire: implicit before('%s','%s') = %s/%s (organ confident); off-switch "
                  "abstains -> %s/%s" % (pa, pb, lbl4, sig4, lbl5, sig5))
        else:
            print("[selftest] script wire: chosen pair not confident in this asset -> positive assertion skipped")
    else:
        print("[selftest] script asset absent -> implicit-event path abstains (asset-less safe)")

    # (C3) COHERENCE OVERRIDE wire (Q111 p7): default-OFF is BYTE-IDENTICAL to the pre-wire reasoner on every
    # narrated pair; ON reverses the iconicity fallback to signal 'coherence' when the SDRT-lite reader confidently
    # infers EXPLANATION. "Max fell . John pushed him ." -- no causal cue, so before() rides iconicity; the reader
    # infers EXPLANATION (pushed CAUSES fell) -> event order reverses telling order -> before(fell,pushed)='after'.
    coh_text = "Max fell . John pushed him ."
    off_c = TemporalReasoner.from_text(coh_text, use_coherence=False)
    on_c = TemporalReasoner.from_text(coh_text, use_coherence=True)
    for pr in (("fell", "pushed"), ("pushed", "fell")):
        assert off_c.before(*pr)[1] == "iconicity", f"expected iconicity base for {pr}, got {off_c.before(*pr)}"
    # OFF byte-identical to a from_text reasoner with NO coherence kwarg at all:
    plain_c = TemporalReasoner.from_text(coh_text)
    for pr in (("fell", "pushed"), ("pushed", "fell")):
        assert off_c.before(*pr) == plain_c.before(*pr), \
            ("coherence-OFF not byte-identical", pr, off_c.before(*pr), plain_c.before(*pr))
    # ON fires: the iconicity verdict is REVERSED to 'coherence' on this Explanation pair.
    lbl_c, sig_c = on_c.before("fell", "pushed")
    base_lbl, _ = off_c.before("fell", "pushed")
    assert sig_c == "coherence" and lbl_c != base_lbl, \
        f"coherence override did not fire/reverse: on={lbl_c}/{sig_c} base={base_lbl}"
    # a NON-causal narrated pair is NOT overridden even with the channel on (stays iconicity) -> selective.
    nn = TemporalReasoner.from_text("Max walked in . He sat down .", use_coherence=True)
    assert nn.before("walked", "sat")[1] == "iconicity", "coherence over-fired on a non-causal Narration pair"
    print("[selftest] coherence override: OFF byte-identical; ON reverses before('fell','pushed') -> %s/%s "
          "(base %s/iconicity); non-causal pair keeps iconicity (selective)" % (lbl_c, sig_c, base_lbl))

    # (D) RELATIVE DURATION: an adjacent chain integrates transitively; an un-stated pair reads correctly.
    items = ["blink", "sip", "song", "meal", "movie", "flight", "war", "era"]
    prem = [(items[i + 1], items[i]) for i in range(len(items) - 1)]   # each next lasts longer
    line = RelativeDurationLine(items).integrate(prem)
    assert line.longer("era", "blink") is True, "un-stated transitive relative-duration failed"
    assert line.longer("blink", "war") is False, "un-stated transitive relative-duration failed (reverse)"

    print("[hdlab.temporal_reasoner] self-test PASS: overlap + before/after(provenance) + narrated byte-identity "
          "+ implicit-event abstain + script/schema wire + relative-duration magnitude line")


if __name__ == "__main__":
    _selftest()
