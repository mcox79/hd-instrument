"""MULTI-FRAME temporal-ordering mechanism: a RUNNING TIMELINE that reconstructs the
chronological order of MULTIPLE events across sentences -- ordering multiple anterior
(past-perfect) events AMONG THEMSELVES via temporal connectives, handling connectives
that CONTRADICT past-perfect demotion, and tracking flashback frames across sentences.

This is a PLUGGABLE EXTENSION of experiments/_temporal_ordering.py (cell 1, banked MM
29508). It REUSES that module's shared extractor (extract_events / Event / tense tags),
its SequenceMatrix wiring, and its pairwise_accuracy scorer UNCHANGED -- nothing in the
banked module is edited, so cell-1's single-frame behavior is bit-identical. The new
mechanism lives here.

WHY (cell-1 auditor lesson, 29509): cell-1 proved SINGLE-FRAME past-perfect ordering but
was CONSTRUCTION-AIDED-CLEAN -- with one pp event "demote pp before narrative-now" is
trivially exactly right, so it could not separate genuine chronological reasoning from
simple pp-tagging+demotion. The real event-indexing TIME dimension is MULTI-FRAME.

The two heuristics this mechanism must BEAT on the hard subset:
  TEXT       chronological order == text order (fails on any reordering).
  PP_DEMOTE  cell-1's core heuristic: all past-perfect events before all narrative-now
             events, stable TEXT order within each group. STRONG on natural prose (authors
             usually write pp events in chronological text order), so the hard subset must
             contain cases where it provably fails:
             (a) two pp events reordered by a connective ("had mailed AFTER had written"
                 -> written before mailed; PP_DEMOTE keeps text order within the pp group);
             (b) a connective that CONTRADICTS anteriority ("She rose BEFORE he had
                 finished" -> rose before finished; PP_DEMOTE over-demotes the pp);
             (c) cross-sentence flashback frames.

MECHANISM (glass-box constraint graph + topological sort; NO per-item rules):
  1. Tokenize KEEPING punctuation (cell-1's ORC tagger strips it, so a running timeline had
     no clause/sentence structure to read). Same NLTK tagger + same event rules -> the
     extracted event set (lemma+tense) is IDENTICAL to cell-1's shared extractor (asserted).
  2. SOFT tense-anteriority edges: each past-perfect event p is anterior to the nearest
     narrative-now event before it AND after it in text (generalizes cell-1's same-sentence
     demotion across sentence boundaries -> flashback frames). Soft = a connective overrides.
  3. HARD connective edges (override soft): a subordinating temporal connective splits its
     sentence into a subordinate clause S (right of the connective) and the adjacent main
     clause M. Relation by connective:
       after / since / earlier : S is EARLIER than M      (edges S -> M)
       before / until / then / later : M is EARLIER than S (edges M -> S)
       when : simultaneous boundary, no strict edge (abstain)
     Connective edges apply to ALL pairs including pp-pp (the case-a lever) and can reverse
     a tense edge (the case-b lever). A hard edge contradicting a soft edge drops the soft.
  4. Topological sort (Kahn) with TEXT index as the stable tiebreak -> default narrative
     advance for unconstrained events; never reorders a pair with no cue (abstain -> never
     confidently wrong). Binds the full multi-event chronology into hdlab.SequenceMatrix.

Brain grounding (event-indexing model, Zwaan-Radvansky 1998; Kintsch/van-Dijk situation
model): readers maintain a RUNNING timeline, updating at temporal-shift boundaries; they
order anterior events among themselves using explicit temporal markers, not tense alone.

ASCII-only. Deterministic given a fixed codebook seed. Substrate-only (no LLM at runtime).
"""
from __future__ import annotations

import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_ordering as T  # noqa: E402  (shared extractor + SM wiring)
from experiments.exp_oracle_mention_upperbound_reader_v1 import _tagger  # noqa: E402

Event = T.Event
AUX_LEMMAS = T.AUX_LEMMAS
COPULA_BE = T.COPULA_BE

# Connective classes for the running-timeline mechanism (a superset of cell-1's, which
# only reordered ADJACENT simple-past pairs on {after, earlier}).
# SUB_EARLIER: the subordinate clause the connective introduces is chronologically EARLIER.
# SUB_LATER:   the subordinate clause is chronologically LATER (main is earlier).
# NEUTRAL:     boundary/simultaneity marker -> no strict order edge (abstain).
SUB_EARLIER = {"after", "since", "earlier"}
SUB_LATER = {"before", "until", "till", "then", "later"}
NEUTRAL = {"when", "while", "as"}
TEMPORAL_CONNECTIVES = SUB_EARLIER | SUB_LATER  # only these produce strict edges

SENT_END_SURFACE = {".", "!", "?", ";"}
CLAUSE_BREAK_SURFACE = {",", ";", ":"}

# Word OR punctuation token (words match cell-1's ORC _TOKEN_RE exactly; punctuation kept).
_WORD_RE = r"[A-Za-z]+(?:'[A-Za-z]+)?"
_TOK_RE = re.compile(_WORD_RE + r"|--|[.,;:!?]")
_PUNC_POS = "PUNC"


def tag_punct(text):
    """Tokenize KEEPING punctuation and POS-tag the word tokens with the same NLTK tagger
    cell-1 uses. Returns list of (surface, low, pos); punctuation tokens carry pos=PUNC.
    Words are tagged word-only (identical to ORC.pos_tag_sentence) then punctuation is spliced
    back by position, so word POS tags -- and therefore extracted events -- are identical."""
    raw = [m.group(0) for m in _TOK_RE.finditer(text)]
    words = [w for w in raw if not re.fullmatch(r"--|[.,;:!?]", w)]
    wtags = dict()
    tagged_words = _tagger().tag(words)
    wi = 0
    out = []
    for surf in raw:
        if re.fullmatch(r"--|[.,;:!?]", surf):
            out.append((surf, surf, _PUNC_POS))
        else:
            _, pos = tagged_words[wi]
            low = surf.lower().strip(".,'\"!?;:")
            out.append((surf, low, pos))
            wi += 1
    return out


def extract_events_punct(text):
    """Extract content-verb events with tense from a punctuation-preserving tag stream.

    Applies the SAME rules as cell-1's T.extract_events (VBD->SIMPLE_PAST; had+VBN->PAST_PERFECT;
    be+VBN->PASSIVE; bare VBN skipped), with the had/be lookback taken over WORD tokens only
    (punctuation does not consume lookback distance) so the event set matches cell-1 exactly.
    Event.idx indexes into the returned punctuation-preserving token list."""
    tagged = tag_punct(text)
    word_positions = [i for i, t in enumerate(tagged) if t[2] != _PUNC_POS]
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    # word-rank of each token position (for word-only lookback)
    wrank = {}
    r = 0
    for i, t in enumerate(tagged):
        if t[2] != _PUNC_POS:
            wrank[i] = r
            r += 1
    word_low_by_rank = [lows[p] for p in word_positions]
    events = []
    for i, (low, pos) in enumerate(zip(lows, poss)):
        if pos == _PUNC_POS:
            continue
        if low in AUX_LEMMAS:
            continue
        wr = wrank[i]
        if pos == "VBD":
            events.append(Event(lemma=low, idx=i, pos=pos, tense=T.TENSE_SIMPLE_PAST, is_pp=False))
        elif pos == "VBN":
            had = any(word_low_by_rank[j] == "had" for j in range(max(0, wr - 3), wr))
            be = any(word_low_by_rank[j] in COPULA_BE for j in range(max(0, wr - 3), wr))
            if had:
                events.append(Event(lemma=low, idx=i, pos=pos, tense=T.TENSE_PAST_PERFECT, is_pp=True))
            elif be:
                events.append(Event(lemma=low, idx=i, pos=pos, tense=T.TENSE_PASSIVE, is_pp=False))
    return events, tagged


def _sentence_ids(tagged):
    sid = 0
    ids = []
    for surf, low, pos in tagged:
        ids.append(sid)
        if surf in SENT_END_SURFACE:
            sid += 1
    return ids


def _clause_bounds(tagged, i):
    """(lo, hi) token indices of the clause containing i: span between nearest clause-break /
    sentence-boundary punctuation on each side (breaks excluded)."""
    n = len(tagged)
    lo = i
    while lo - 1 >= 0:
        surf = tagged[lo - 1][0]
        if surf in CLAUSE_BREAK_SURFACE or surf in SENT_END_SURFACE:
            break
        lo -= 1
    hi = i
    while hi + 1 < n:
        surf = tagged[hi][0]
        if surf in CLAUSE_BREAK_SURFACE or surf in SENT_END_SURFACE:
            break
        hi += 1
    return lo, hi


def _events_in(events, lo, hi):
    return [e for e in events if lo <= e.idx < hi]


def _now_events(events):
    return [e for e in events if not e.is_pp]


def _find_connectives(tagged):
    return [(k, low) for k, (surf, low, pos) in enumerate(tagged) if low in TEMPORAL_CONNECTIVES]


def _connective_edges(events, tagged):
    """HARD directed edges (u, v): u strictly earlier than v, from temporal connectives.
    The connective token splits its sentence: subordinate clause S = the clause immediately
    to its RIGHT; main clause M = the clause immediately to its LEFT (medial) or, if the
    connective is clause-leading, the clause to the RIGHT of S (leading)."""
    edges = set()
    sids = _sentence_ids(tagged)
    n = len(tagged)
    for k, lemma in _find_connectives(tagged):
        r_lo, r_hi = _clause_bounds(tagged, min(k + 1, n - 1))
        sub = _events_in(events, k + 1, r_hi)
        l_lo, l_hi = _clause_bounds(tagged, max(k - 1, 0))
        main = _events_in(events, l_lo, k)
        if not main:  # leading connective: main is the clause after the subordinate span
            m_lo, m_hi = _clause_bounds(tagged, min(r_hi + 1, n - 1))
            main = _events_in(events, r_hi + 1, m_hi)
        if not sub or not main:
            continue
        for s in sub:
            for m in main:
                if sids[s.idx] != sids[m.idx]:
                    continue
                if s.lemma == m.lemma:
                    continue
                if lemma in SUB_EARLIER:
                    edges.add((s.lemma, m.lemma))
                elif lemma in SUB_LATER:
                    edges.add((m.lemma, s.lemma))
    return edges


def _tense_edges(events, tagged, cross_sentence=True):
    """SOFT anteriority edges: each pp event is earlier than the now-events of its FRAME.

    Frame = the pp event's own sentence: p is anterior to ALL now-events in that sentence
    (this reproduces cell-1's pp-demotion within a sentence -> no single-frame regression).
    With cross_sentence=True, p is ALSO anterior to the nearest now-event before it and after
    it ACROSS sentence boundaries (flashback frames span sentences). cross_sentence=False
    restricts to same-sentence now-events == the P2 ablation (reduces to pp-demotion)."""
    edges = set()
    sids = _sentence_ids(tagged)
    nows = _now_events(events)
    for p in events:
        if not p.is_pp:
            continue
        cands = [q for q in nows if sids[q.idx] == sids[p.idx]]   # all now in same sentence
        if cross_sentence:
            before = [q for q in nows if q.idx < p.idx and sids[q.idx] != sids[p.idx]]
            after = [q for q in nows if q.idx > p.idx and sids[q.idx] != sids[p.idx]]
            if before:
                cands.append(max(before, key=lambda q: q.idx))
            if after:
                cands.append(min(after, key=lambda q: q.idx))
        for q in cands:
            if p.lemma != q.lemma:
                edges.add((p.lemma, q.lemma))
    return edges


def _toposort(lemmas_in_text_order, edges):
    """Kahn's algorithm with text-index tiebreak. Duplicate lemmas collapse to first
    occurrence. On any residual cycle, leftovers append in text order (deterministic)."""
    nodes, seen = [], set()
    for lem in lemmas_in_text_order:
        if lem not in seen:
            seen.add(lem)
            nodes.append(lem)
    rank = {lem: i for i, lem in enumerate(nodes)}
    adj = {n: set() for n in nodes}
    indeg = {n: 0 for n in nodes}
    for u, v in edges:
        if u in adj and v in adj and v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1
    ready = sorted([n for n in nodes if indeg[n] == 0], key=lambda x: rank[x])
    out = []
    while ready:
        nn = ready.pop(0)
        out.append(nn)
        for m in adj[nn]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort(key=lambda x: rank[x])
    if len(out) < len(nodes):
        for nn in nodes:
            if nn not in out:
                out.append(nn)
    return out


def build_constraint_edges(events, tagged, use_connectives=True, cross_sentence=True):
    """Return the final edge set (hard connective edges override contradicting soft ones)."""
    soft = _tense_edges(events, tagged, cross_sentence=cross_sentence)
    hard = _connective_edges(events, tagged) if use_connectives else set()
    edges = set(hard)
    for (a, b) in soft:
        if (b, a) in hard:
            continue  # connective overrides contradicting tense edge
        edges.add((a, b))
    return edges


def reconstruct_order_timeline(events, tagged, use_connectives=True, cross_sentence=True):
    """Return (ordered_events, edges) via the running-timeline mechanism.
    use_connectives=False AND cross_sentence=False reduces to pp-demotion (the P2 ablation)."""
    edges = build_constraint_edges(events, tagged, use_connectives, cross_sentence)
    text_lemmas = [e.lemma for e in sorted(events, key=lambda e: e.idx)]
    order_lemmas = _toposort(text_lemmas, edges)
    by_lemma = {}
    for e in sorted(events, key=lambda e: e.idx):
        by_lemma.setdefault(e.lemma, []).append(e)
    ordered = []
    for lem in order_lemmas:
        ordered.extend(by_lemma.get(lem, []))
    return ordered, edges


def confident_pair(edges, x, y):
    """True iff a directed path connects x and y (either direction): the mechanism has a CUE
    for this pair, not merely a text-order default. Pairs with no path are ABSTAINED for the
    never-confidently-wrong accounting."""
    adj = {}
    for u, v in edges:
        adj.setdefault(u, set()).add(v)

    def reach(a, b):
        stack, seen = [a], {a}
        while stack:
            nn = stack.pop()
            if nn == b:
                return True
            for m in adj.get(nn, ()):
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        return False

    return reach(x, y) or reach(y, x)


# Baselines + shared substrate re-exports (all IDENTICAL to cell-1's shared module).
text_order = T.text_order
pairwise_accuracy = T.pairwise_accuracy
extract_events_shared = T.extract_events


def reconstruct_order_ppdemote(ev, tg):
    return T.reconstruct_order(ev, tg, use_tense=True, use_connective=False)


def reconstruct_order_cell1cue(ev, tg):
    return T.reconstruct_order(ev, tg, use_tense=True, use_connective=True)


build_codebook = T.build_codebook
bind_order = T.bind_order
chain_recover_depth = T.chain_recover_depth
successor_prediction_correct = T.successor_prediction_correct
SequenceMatrix = T.SequenceMatrix
_vec = T._vec
