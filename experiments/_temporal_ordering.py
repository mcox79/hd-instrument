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
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.memory import Codebook  # noqa: E402
from hdlab.sequence_memory import SequenceMatrix  # noqa: E402

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


def default_tagger(text):
    """Reader POS pipeline: NLTK PerceptronTagger via the ORC reader helper.

    Returns list of (surface, low, pos). Imported lazily so the module has no hard
    import-time dependency on the reader cell (keeps it pluggable / testable).
    """
    from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC
    return ORC.pos_tag_sentence(text)


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
