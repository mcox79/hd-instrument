"""Backward-compatible SHIM: hdlab.temporal_order_register was CONSOLIDATED (2026-09-11, consolidation audit action #3) into
hdlab.temporal_model as its LAYER 3 (passage-level queryable before/after register).

The brain reuses ONE structure for many functions -- the three former temporal ORDER modules were layers of one
computation (Reichenbach reference time + Allen interval constraints + Vendler aspect; Zwaan-Radvansky time index),
not three structures. The code (and the original module docstring) now lives in hdlab/temporal_model.py under the
"LAYER 3" banner; this file only re-exports the SAME objects so every historical import keeps working
byte-identically. New code should import hdlab.temporal_model directly. ASCII-only.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'DiscreteOrderRegister/ContinuousOrderRegister queryable before/after over the toposorted timeline; composes the pinned discrete front-end; magnitude-line params swept; SHIM (2026-09-11) of hdlab.temporal_model LAYER 3 -- code moved there verbatim, names re-exported unchanged'
__bf_corrections__ = []


import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from dataclasses import dataclass  # noqa: F401  (historical namespace parity)
from typing import Dict, List, Optional, Sequence, Tuple  # noqa: F401
from hdlab import temporal_model as T  # noqa: E402,F401  (historical `R.T` / `R.M` attribute parity)
from hdlab import temporal_model as M  # noqa: E402,F401
from hdlab.temporal_model import (  # noqa: F401  re-exports: the SAME objects, byte-identical behaviour
    ABSTAIN, AFTER, BEFORE, ComposedRegister, ContinuousOrderRegister, DiscreteOrderRegister,
    NarrationOrderFloor, OrderQuery, _CLAUSE_BREAK, _FINITE_VERB_POS, _SUBORD, _first_occurrence,
    build_register, extract_passage, make_twin_edges, make_twin_events, promote_clause_pluperfect,
    score_pairs,
)
