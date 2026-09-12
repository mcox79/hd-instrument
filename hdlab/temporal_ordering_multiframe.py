"""Backward-compatible SHIM: hdlab.temporal_ordering_multiframe was CONSOLIDATED (2026-09-11, consolidation audit action #3) into
hdlab.temporal_model as its LAYER 2 (running cross-sentence timeline: constraint graph + toposort).

The brain reuses ONE structure for many functions -- the three former temporal ORDER modules were layers of one
computation (Reichenbach reference time + Allen interval constraints + Vendler aspect; Zwaan-Radvansky time index),
not three structures. The code (and the original module docstring) now lives in hdlab/temporal_model.py under the
"LAYER 2" banner; this file only re-exports the SAME objects so every historical import keeps working
byte-identically. New code should import hdlab.temporal_model directly. ASCII-only.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'running cross-sentence timeline: anterior (past-perfect) ordering + connective contradiction + flashback frames; extension of temporal_ordering, pinned cue framework; SHIM (2026-09-11) of hdlab.temporal_model LAYER 2 -- code moved there verbatim, names re-exported unchanged'
__bf_corrections__ = []


import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import temporal_model as T  # noqa: E402,F401  (historical `M.T` attribute parity)
from hdlab.sequence_memory import SequenceMatrix  # noqa: E402,F401
from hdlab.temporal_model import (  # noqa: F401  re-exports: the SAME objects, byte-identical behaviour
    AUX_LEMMAS, CLAUSE_BREAK_SURFACE, COPULA_BE, Event, NEUTRAL, SENT_END_SURFACE, SUB_EARLIER, SUB_LATER,
    TEMPORAL_CONNECTIVES, _PUNC_POS, _TOK_RE, _WORD_RE, _clause_bounds, _connective_edges, _events_in,
    _find_connectives, _now_events, _sentence_ids, _tagger, _tense_edges, _toposort, _vec, bind_order,
    build_codebook, build_constraint_edges, chain_recover_depth, confident_pair, extract_events_punct,
    extract_events_shared, pairwise_accuracy, reconstruct_order_cell1cue, reconstruct_order_ppdemote,
    reconstruct_order_timeline, successor_prediction_correct, tag_punct, text_order,
)
