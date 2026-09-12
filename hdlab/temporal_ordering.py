"""Backward-compatible SHIM: hdlab.temporal_ordering was CONSOLIDATED (2026-09-11, consolidation audit action #3) into
hdlab.temporal_model as its LAYER 1 (single-frame cue ordering + SequenceMatrix binding).

The brain reuses ONE structure for many functions -- the three former temporal ORDER modules were layers of one
computation (Reichenbach reference time + Allen interval constraints + Vendler aspect; Zwaan-Radvansky time index),
not three structures. The code (and the original module docstring) now lives in hdlab/temporal_model.py under the
"LAYER 1" banner; this file only re-exports the SAME objects so every historical import keeps working
byte-identically. New code should import hdlab.temporal_model directly. ASCII-only.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'tense/aspect + temporal-connective cues -> chronological constraint order -> SequenceMatrix (Reichenbach-ish discourse ordering); pinned cue framework; POS via the separate NOT_BF tagger; SHIM (2026-09-11) of hdlab.temporal_model LAYER 1 -- code moved there verbatim, names re-exported unchanged'
__bf_corrections__ = []


import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from dataclasses import dataclass, field  # noqa: F401  (historical namespace parity)
from hdlab.memory import Codebook  # noqa: E402,F401
from hdlab.sequence_memory import SequenceMatrix  # noqa: E402,F401
from hdlab.temporal_model import (  # noqa: F401  re-exports: the SAME objects, byte-identical behaviour
    AUX_LEMMAS, CONNECTIVE_PRESERVE, CONNECTIVE_REORDER, COORD_LEMMAS, COPULA_BE, Event, MODAL_LEMMAS,
    TENSE_MODAL_SUBORD, TENSE_OTHER, TENSE_PARTICIPIAL, TENSE_PASSIVE, TENSE_PAST_PERFECT,
    TENSE_SIMPLE_PAST, _TOKEN_RE, _connective_between, _coord_source_event, _first_pos, _perceptron_tagger,
    _tokenize, _vec, bind_order, build_codebook, chain_recover_depth, default_tagger, extract_events,
    pairwise_accuracy, pos_tag_sentence, reconstruct_order, successor_prediction_correct, text_order,
)
