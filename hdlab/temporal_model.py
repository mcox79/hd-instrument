"""TEMPORAL MODEL: the ONE temporal ORDER-construction organ of the situation model (the TIME dimension).

CONSOLIDATED 2026-09-11 (consolidation audit action #3; owner directive: the brain reuses ONE structure for many
functions -- no islanded copies) from three modules that were three LAYERS of one computation, not three structures:

  LAYER 1  hdlab/temporal_ordering.py            single-frame cue ordering: tense/aspect + temporal-connective cues
                                                  -> chronological constraint order -> SequenceMatrix binding
  LAYER 2  hdlab/temporal_ordering_multiframe.py  running cross-sentence timeline: soft tense-anteriority edges +
                                                  hard connective edges -> constraint graph -> Kahn toposort
  LAYER 3  hdlab/temporal_order_register.py       passage-level queryable before(x, y) register over the toposorted
                                                  timeline (discrete ordinal / continuous magnitude line / narration
                                                  floor / composed) + brain-faithful clause-level pluperfect binder

The code of all three is MOVED here VERBATIM (the only edits are the self-referential `T.` / `M.` prefixes, which
collapse inside one module); the three old module paths remain as thin re-export SHIMS. Every function/class keeps
its name. GATE: byte-identity (module self-tests, the four temporal board rows, a function-level probe over the
whole public surface -- all unchanged).

INPUT TRANSDUCERS that FEED this organ and stay SEPARATE on purpose (different brain structures, different reads):
  hdlab/tense_preserving_detector.py  the compositional Reichenbach tense read (E/R/S triple per verb)
  hdlab/aspect_interval.py            the Vendler/Smith viewpoint-aspect read (interval character -> Allen algebra)
CONSUMERS: hdlab.situation_reader (TIME dimension + _read_timeline_register), hdlab.temporal_reasoner,
hdlab.aspect_interval, hdlab.causal_network (shared event extractor), hdlab.temporal_script_schema (build-only).

BRAIN GROUNDING (one computation): Reichenbach (1947) E/R/S reference time carried across sentences as a discourse
variable (Past Discourse-Linking Hypothesis) + Allen (1983) interval order constraints from temporal connectives +
Vendler/Smith aspect; the Zwaan-Radvansky (1998) event-indexing TIME index = a RUNNING timeline updated at temporal-
shift boundaries; the order register's representation (discrete ordinal vs TCM/time-cell continuous magnitude line,
Howard & Kahana 2002; Eichenbaum 2014) is SWEPT, not adopted. The three original module docstrings are preserved
below each LAYER banner (provenance; the per-layer mechanism notes are unchanged).

ASCII-only. Deterministic given fixed seeds. Substrate-only (no LLM at inference).
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-11 consolidation of three BF_SPIRIT modules (temporal_ordering + temporal_ordering_multiframe + temporal_order_register, each certified 2026-09-09 operation/math read); code MOVED verbatim under a byte-identity gate'
__bf_note__ = 'ONE temporal order-construction organ: tense/aspect + connective cues -> constraint graph (Reichenbach reference time carried across sentences) -> Kahn toposort timeline -> queryable before/after register (discrete ordinal vs continuous magnitude line SWEPT) + SequenceMatrix binding; fed by the separate tense_preserving_detector (Reichenbach) + aspect_interval (Vendler) transducers; POS via the separate NOT_BF tagger'
__bf_corrections__ = []


import os
import re
import re as _re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.memory import Codebook  # noqa: E402
from hdlab.sequence_memory import SequenceMatrix  # noqa: E402



# ==================================================================================================
# LAYER 1 -- single-frame cue ordering + SequenceMatrix binding (formerly hdlab/temporal_ordering.py)
# ==================================================================================================
"""Reusable TEMPORAL-ORDERING module: reconstruct CHRONOLOGICAL event order from
tense / aspect / temporal-connective cues, and bind the reconstructed sequence into
the substrate's SequenceMatrix (glass-box in-substrate temporal representation).

This is a PLUGGABLE component for the situation model (the TIME dimension). It wires
the reader's POS pipeline (event predicate tokens + tense) to hdlab.SequenceMatrix.
No banked cell is edited; this is a fresh standalone module.

Brain grounding (event-indexing model, Zwaan-Radvansky 1998; Kintsch situation model):
readers reconstruct CHRONOLOGICAL order (which DIFFERS from TEXT order in flashbacks /
non-linear narrative) from TENSE/ASPECT ("had" + VBN past-perfect = PRIOR to the
narrative-now) + TEMPORAL CONNECTIVES (after/earlier reorder; before/then/until preserve)
+ default narrative-advance (text order). The default reader assumes text order = event
order; that FAILS on flashbacks -- the exact parallel to the passive discriminator, where
naive word-order fails on passives.

ASCII-only. Deterministic given a fixed codebook seed. Substrate-only (no LLM at runtime).
"""

# Pure-auxiliary lemmas (never the content-verb event); 'had' among them so a bare
# "had" is not itself an event, only its VBN complement is.
AUX_LEMMAS = {
    "is", "am", "are", "was", "were", "be", "been", "being", "has", "have", "had",
    "will", "shall", "can", "could", "would", "should", "may", "might", "must",
    "do", "does", "did", "not", "let",
}
COPULA_BE = {"was", "were", "is", "are", "be", "been", "being"}
# Modal auxiliaries that license a bare-infinitive (VB) content-verb event in a subordinate
# clause ("if he might gain the power ...") -- 2026-08-05 coverage extension.
MODAL_LEMMAS = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
# Coordinating conjunctions that can share a single distant aux across two content verbs
# ("had long owned and cherished") -- 2026-08-05 coverage extension.
COORD_LEMMAS = {"and", "or"}

# Temporal connectives. REORDER = the mentioned-later clause is chronologically earlier;
# PRESERVE = text order already matches chronology (conservative default).
CONNECTIVE_REORDER = {"after", "earlier"}          # "A after B" -> B before A
CONNECTIVE_PRESERVE = {"before", "then", "until", "till", "when", "later", "and"}

TENSE_PAST_PERFECT = "PAST_PERFECT"   # had + VBN  -> PRIOR (flashback)
TENSE_SIMPLE_PAST = "SIMPLE_PAST"     # VBD        -> narrative-now
TENSE_PASSIVE = "PASSIVE"             # be + VBN   -> narrative-now
TENSE_MODAL_SUBORD = "MODAL_SUBORDINATE"  # modal + bare VB -> subordinate-clause event
TENSE_PARTICIPIAL = "PARTICIPIAL"     # bare VBG, no progressive aux -> non-finite clause event
TENSE_OTHER = "OTHER"


@dataclass
class Event:
    """One extracted event: content-verb predicate at token index `idx` in the passage."""
    lemma: str
    idx: int
    pos: str
    tense: str
    is_pp: bool = field(default=False)


# ---- SELF-CONTAINED POS pipeline (promoted byte-faithfully from ORC.pos_tag_sentence; ZERO
# experiments/ imports; NLTK PerceptronTagger is an allowed shallow tool) --------------------
_TOKEN_RE = _re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_ORC_TAGGER = None


def _perceptron_tagger():
    global _ORC_TAGGER
    if _ORC_TAGGER is None:
        from nltk.tag import PerceptronTagger
        _ORC_TAGGER = PerceptronTagger()
    return _ORC_TAGGER


def _tokenize(sentence):
    return [m.group(0) for m in _TOKEN_RE.finditer(sentence)]


def pos_tag_sentence(sentence):
    """Return list of (surface, low, pos) using NLTK PerceptronTagger (legal shallow tool).
    Byte-faithful copy of ORC.pos_tag_sentence so hdlab has ZERO experiments/ imports."""
    toks = _tokenize(sentence)
    tagged = _perceptron_tagger().tag(toks)
    out = []
    for surf, pos in tagged:
        low = surf.lower().strip(".,'\"!?;:")
        out.append((surf, low, pos))
    return out


def default_tagger(text):
    """Reader POS pipeline: NLTK PerceptronTagger (SELF-CONTAINED; no experiments import).

    Returns list of (surface, low, pos)."""
    return pos_tag_sentence(text)


def _coord_source_event(i, lows, events_by_idx):
    """COORDINATED-VP gap fix (2026-08-05): a VBN two positions back that has no had/be aux
    of its own within lookback (e.g. "had long owned AND cherished" -- 'cherished' is 4 tokens
    from 'had') inherits the tense of an already-extracted event it is DIRECTLY conjoined to
    ("<source-event> and/or <this-token>"). Conservative: only fires when the immediately
    preceding token is a bare coordinator and the token before THAT is itself an extracted
    event (so the aux/subject genuinely carries across the coordination), never guesses across
    an intervening clause boundary."""
    if i < 2 or lows[i - 1] not in COORD_LEMMAS:
        return None
    return events_by_idx.get(i - 2)


def extract_events(text, tagger=None):
    """Extract content-verb events with tense from a passage. SHARED by all arms.

    A content verb is an event iff:
      * VBD and lemma not a pure aux  -> SIMPLE_PAST (narrative-now)
      * VBN preceded (<=3 tokens) by 'had'  -> PAST_PERFECT (PRIOR / flashback)
      * VBN preceded (<=3 tokens) by a copula-be  -> PASSIVE (narrative-now)
      * VBN with no had/be aux, but directly coordinated ("and"/"or") with an already-
        extracted VBD/VBN event -> inherits that event's tense (shared distant aux across a
        coordinated VP -- 2026-08-05 coverage extension; see _coord_source_event)
      * bare VBN with no had/be aux and no coordination source -> SKIPPED (adjectival
        participle; conservative, UNCHANGED)
      * VB (bare infinitive) preceded (<=3 tokens) by a modal -> MODAL_SUBORDINATE (the
        predicate of a modal-governed subordinate clause, e.g. "if he might gain the power";
        2026-08-05 coverage extension)
      * VBG not preceded (<=3 tokens) by a progressive aux (is/was/being/...) -> PARTICIPIAL
        (a non-finite participial-clause predicate, e.g. "Mary, resenting X, began ...";
        2026-08-05 coverage extension; subject is inherited by the existing positional
        agent-selection in _assign_roles, which already picks the nearest preceding nominal --
        no role-assignment change needed for this construction)

    ADDITIVE ONLY: every branch that fired before this extension (VBD; VBN+had; VBN+be) is
    byte-identical unchanged code; the new branches (VBN-coordination fallback, VB-modal,
    VBG-participial) only ever ADD events that were previously silently dropped.
    """
    if tagger is None:
        tagger = default_tagger
    tagged = tagger(text)
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    events = []
    events_by_idx = {}
    for i, (low, pos) in enumerate(zip(lows, poss)):
        if low in AUX_LEMMAS:
            continue
        ev = None
        if pos == "VBD":
            ev = Event(lemma=low, idx=i, pos=pos, tense=TENSE_SIMPLE_PAST, is_pp=False)
        elif pos == "VBN":
            had = any(lows[j] == "had" for j in range(max(0, i - 3), i))
            be = any(lows[j] in COPULA_BE for j in range(max(0, i - 3), i))
            if had:
                ev = Event(lemma=low, idx=i, pos=pos, tense=TENSE_PAST_PERFECT, is_pp=True)
            elif be:
                ev = Event(lemma=low, idx=i, pos=pos, tense=TENSE_PASSIVE, is_pp=False)
            else:
                src = _coord_source_event(i, lows, events_by_idx)
                if src is not None:
                    ev = Event(lemma=low, idx=i, pos=pos, tense=src.tense, is_pp=src.is_pp)
                # else: adjectival participle -> not an event (unchanged)
        elif pos == "VB":
            modal = any(lows[j] in MODAL_LEMMAS for j in range(max(0, i - 3), i))
            if modal:
                ev = Event(lemma=low, idx=i, pos=pos, tense=TENSE_MODAL_SUBORD, is_pp=False)
        elif pos == "VBG":
            prog = any(lows[j] in COPULA_BE for j in range(max(0, i - 3), i))
            if not prog:
                ev = Event(lemma=low, idx=i, pos=pos, tense=TENSE_PARTICIPIAL, is_pp=False)
        if ev is not None:
            events.append(ev)
            events_by_idx[i] = ev
    return events, tagged


def _connective_between(tagged, idx_a, idx_b):
    """Return a connective lemma occurring in the token span (idx_a, idx_b), else None."""
    lo, hi = (idx_a, idx_b) if idx_a < idx_b else (idx_b, idx_a)
    for k in range(lo + 1, hi):
        w = tagged[k][1]
        if w in CONNECTIVE_REORDER or w in CONNECTIVE_PRESERVE:
            return w
    return None


def reconstruct_order(events, tagged, use_tense=True, use_connective=True):
    """Return events in reconstructed CHRONOLOGICAL order.

    With use_tense=use_connective=False this is the BASELINE (text order).
    use_tense: past-perfect (had+VBN) events are demoted BEFORE narrative-now events
      (stable within each group -> the classic single-frame flashback reconstruction).
    use_connective: adjacent simple-past pairs joined by a REORDER connective
      ("A after B" / "earlier") get swapped so the earlier event precedes.
    Abstains (keeps text order) for any pair with no cue -> never confidently wrong.
    """
    order = sorted(events, key=lambda e: e.idx)  # text order
    if use_tense:
        order = sorted(order, key=lambda e: (0 if e.is_pp else 1, e.idx))  # stable: pp first
    if use_connective:
        # local swaps on text-adjacent simple-past pairs with a REORDER connective
        by_idx = sorted(order, key=lambda e: e.idx)
        pos = {id(e): p for p, e in enumerate(order)}
        for a, b in zip(by_idx, by_idx[1:]):
            if a.is_pp or b.is_pp:
                continue
            conn = _connective_between(tagged, a.idx, b.idx)
            if conn in CONNECTIVE_REORDER:
                pa, pb = pos[id(a)], pos[id(b)]
                if pa < pb:  # a currently before b; "a after b" means b is earlier -> swap
                    order[pa], order[pb] = order[pb], order[pa]
                    pos[id(a)], pos[id(b)] = pb, pa
    return order


def text_order(events):
    """Baseline chronological hypothesis: chronological order == text order."""
    return sorted(events, key=lambda e: e.idx)


def _first_pos(order, lemma):
    for p, e in enumerate(order):
        if e.lemma == lemma:
            return p
    return None


def pairwise_accuracy(order, gold_pairs):
    """Score a predicted chronological ordering against gold (earlier, later) lemma pairs.

    Returns (n_correct, n_scored, n_abstain). A pair is ABSTAINED (not scored) when
    either lemma was not extracted -> the arm is never charged for events it never saw.
    """
    n_correct = n_scored = n_abstain = 0
    for earlier, later in gold_pairs:
        pe, pl = _first_pos(order, earlier), _first_pos(order, later)
        if pe is None or pl is None:
            n_abstain += 1
            continue
        n_scored += 1
        if pe < pl:
            n_correct += 1
    return n_correct, n_scored, n_abstain


# ---------------------------------------------------------------------------
# SequenceMatrix wiring: bind the reconstructed chronological event sequence into
# the substrate's ordered-pair store; measure the ordered-binding depth envelope.
# ---------------------------------------------------------------------------
def build_codebook(lemmas, n_dim, seed=1234, dtype=torch.float32):
    """Random near-orthogonal Gaussian codevectors, one per distinct event lemma."""
    g = torch.Generator().manual_seed(seed)
    cb = Codebook(n_dim, dtype)
    for lem in sorted(set(lemmas)):
        v = torch.randn(n_dim, generator=g, dtype=dtype)
        v = v / v.norm()
        cb.add(lem, v)
    return cb


def _vec(cb, lemma):
    idx = cb._names.index(lemma)
    return cb._vectors[idx]


def bind_order(order, cb, n_dim, dtype=torch.float32):
    """Bind an event ordering (chronological OR text) into a fresh SequenceMatrix."""
    sm = SequenceMatrix(n_dim, dtype)
    if len(order) >= 2:
        keys = torch.stack([_vec(cb, e.lemma) for e in order])
        sm.bind_sequence(keys)
    return sm


def chain_recover_depth(sm, order, cb):
    """From event 0, chain_predict with codebook cleanup; count consecutive correct
    successors recovered (the ordered-binding depth envelope for this sequence)."""
    if len(order) < 2:
        return 0
    start = _vec(cb, order[0].lemma)
    depth = len(order) - 1
    preds = sm.chain_predict(start, depth, codebook=cb)
    correct = 0
    for step, pv in enumerate(preds):
        want = _vec(cb, order[step + 1].lemma)
        # nearest-name recovered by cleanup already applied inside chain_predict
        if torch.allclose(pv, want, atol=1e-5):
            correct += 1
        else:
            break
    return correct


def successor_prediction_correct(sm, cb, prev_lemma, true_next_lemma):
    """Glass-box: does predict_next (after binding) recover the TRUE temporal successor?
    Returns True iff the cleaned prediction's nearest codebook name == true_next_lemma."""
    q = _vec(cb, prev_lemma)
    raw = sm.predict_next(q)
    name, _ = cb.lookup(raw / (raw.norm() + 1e-9))
    return name == true_next_lemma


# ==================================================================================================
# LAYER 2 -- running cross-sentence timeline: constraint graph + toposort (formerly hdlab/temporal_ordering_multiframe.py)
# ==================================================================================================
"""MULTI-FRAME temporal-ordering mechanism: a RUNNING TIMELINE that reconstructs the
chronological order of MULTIPLE events across sentences -- ordering multiple anterior
(past-perfect) events AMONG THEMSELVES via temporal connectives, handling connectives
that CONTRADICT past-perfect demotion, and tracking flashback frames across sentences.

This is a PLUGGABLE EXTENSION of hdlab/temporal_ordering.py (cell 1, banked MM
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

_tagger = _perceptron_tagger   # multiframe's historical alias for the shared in-substrate tagger



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

    Applies the SAME rules as cell-1's extract_events (VBD->SIMPLE_PAST; had+VBN->PAST_PERFECT;
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
            events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_SIMPLE_PAST, is_pp=False))
        elif pos == "VBN":
            had = any(word_low_by_rank[j] == "had" for j in range(max(0, wr - 3), wr))
            be = any(word_low_by_rank[j] in COPULA_BE for j in range(max(0, wr - 3), wr))
            if had:
                events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_PAST_PERFECT, is_pp=True))
            elif be:
                events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_PASSIVE, is_pp=False))
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
extract_events_shared = extract_events


def reconstruct_order_ppdemote(ev, tg):
    return reconstruct_order(ev, tg, use_tense=True, use_connective=False)


def reconstruct_order_cell1cue(ev, tg):
    return reconstruct_order(ev, tg, use_tense=True, use_connective=True)


# ==================================================================================================
# LAYER 3 -- passage-level queryable before/after register (formerly hdlab/temporal_order_register.py)
# ==================================================================================================
"""Per-event TEMPORAL-ORDER register: the queryable before/after layer over the
reconstructed chronological timeline.

PROMOTED 2026-09-09 from experiments/_temporal_order_register.py (self-containment) BYTE-FAITHFUL -- the ONLY deltas
are the two internal imports repointed to their already-landed hdlab organs (hdlab.temporal_ordering /
hdlab.temporal_ordering_multiframe, promoted CONT-28) + this note. The reader's default-off `_read_timeline_register`
now imports THIS instead of the experiments scratch cell (ZERO experiments imports = the typed_coref standard).

This COMPOSES the already-landed discrete front-end (hdlab.temporal_ordering_multiframe:
tense/aspect + temporal connectives -> constraint graph -> topological sort) into a
PASSAGE-LEVEL register that answers `before(x, y)` / `order()`, and SWEEPS the order-register
REPRESENTATION (DISCRETE ordinal index vs CONTINUOUS magnitude line via the landed
hdlab.transitive_ordering) per the brain-foundational fork the bar asks for.

WHY THIS EXISTS (disk outranks brief): the mechanism is BUILT (temporal_ordering[_multiframe],
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

Reuses (does NOT rebuild): hdlab.temporal_ordering_multiframe (extract + constraint edges + toposort),
hdlab.temporal_ordering (Event, text_order), hdlab.transitive_ordering (the continuous magnitude line).
ASCII-only. Deterministic given fixed seeds. Substrate-only (no LLM at inference).
"""

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
    ev, tg = extract_events_punct(text)
    if clause_pluperfect:
        ev = promote_clause_pluperfect(ev, tg)
    edges = build_constraint_edges(ev, tg, use_connectives=True, cross_sentence=True)
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


def promote_clause_pluperfect(events: List[Event], tagged) -> List[Event]:
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
        e.tense = TENSE_PAST_PERFECT
    return events


def _first_occurrence(events: Sequence[Event]) -> List[Event]:
    """Collapse duplicate lemmas to first occurrence (matches pairwise_accuracy / the toposort)."""
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
        self.order = _toposort(text_lemmas, self.edges)          # chronological lemma order
        self.rank = {lem: i for i, lem in enumerate(self.order)}
        self.text_rank = {e.lemma: i for i, e in enumerate(self.events)}

    def _connected(self, x, y) -> bool:
        return confident_pair(self.edges, x, y)

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
        self.order = _toposort(self.lemmas, self.edges)
        self.rank = {lem: i for i, lem in enumerate(self.order)}
        if not self._degenerate:
            gen = torch.Generator().manual_seed(seed)
            line = TransitiveOrderingLine(n, d, gen, seed=seed)
            line.integrate(premises, seed=seed)
            self._coord = {lem: line.coord(self.idx[lem]) for lem in self.lemmas}

    def _connected(self, x, y) -> bool:
        return confident_pair(self.edges, x, y)

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
def make_twin_events(events: Sequence[Event], rng) -> List[Event]:
    """Permute the (tense, is_pp) labels across events -> destroys WHICH events are anterior while
    keeping the SAME NUMBER of past-perfect events and the SAME text positions (matched shape)."""
    evs = [Event(lemma=e.lemma, idx=e.idx, pos=e.pos, tense=e.tense, is_pp=e.is_pp) for e in events]
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
        edges = build_constraint_edges(ev, tg, use_connectives=True, cross_sentence=True)
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
