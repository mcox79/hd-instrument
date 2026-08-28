"""Factorized entity store -- the brain's two-system episodic memory: CONTENT x graded TEMPORAL CONTEXT x within-moment ORDER.

Landed 2026-08-28 as landing-step 2 of the FACTORIZED entity store (the proven-ready follow-on of the integrated
`the_entity_store_is_a_dense_bundle_that_fans`, SOLVED/EXCELLENT, owner-DONE; the factorized store was real-data validated
on LitBank -- fan slope 0.001 AND temporal contiguity 0.585, where a single key trades them -- and matches human single-unit
data, Bausch et al. 2026: content and context are SEPARATE populations bound by timing). Ports `UnifiedEntityStore` from
`exp_entity_store_unified_v1` to torch complex64 (FHRR-native), building on the landed `hdlab.graded_temporal_context`.

WHAT IS PINNED (copy the operation):
  * A trace FACTORISES into CONTENT ("what": a near-orthogonal / sparse verb code) x graded TEMPORAL CONTEXT ("when":
    `graded_temporal_context`, smooth contiguity) x WITHIN-MOMENT ORDER (theta-phase; a small ordinal code). Bound ONLY
    at storage; per-entity store = the FHRR bundle of traces; read the content back by UNBINDING the (context x order) key
    (Tolman-Eichenbaum Machine, Whittington & Behrens 2020; Bausch 2026 separate populations).
  * SET-RETURN by a RACE-TO-STOP (CMR; Polyn/Norman/Kahana): decode the top content at each order at the reinstated
    context, then accept the co-moment set = those within a factor of the winner's strength AND above the crosstalk floor
    -- a self-terminating competitive race, NO oracle set-size. This preserves TEMPORAL CONTIGUITY (retrieval reactivates
    neighbors graded by |t-t'|) -- the property a single orthogonal finer-key destroys.
  * SCHEMA / GIST routing (Radvansky; Gilboa & Marlatte): ROUTINE events (a verb that is the entity's running mode) go to
    a per-entity gist counter and do NOT crowd the episodic store; only ATYPICAL (memorable) events are stored episodically.

WHAT IS OUR-INVENTION-UNDER-TEST (honestly labelled): the race ratio (0.78), the gist thresholds, the order-code count --
parameters to SWEEP, not adopt. The content code here is FHRR near-orthogonal; the SPARSE DG k-WTA content (higher
exact-recall capacity at scale) is the next landing step (an optional higher-capacity `content=` backend).

DEFAULT-SAFE island: new module, nothing imports it. Reuses `hdlab.graded_temporal_context`, `hdlab.binding`,
`hdlab.situation_model_accumulate.unit_phase_vec`. The heavy LitBank-scale validation routes to the remote box.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import torch

from . import binding
from .graded_temporal_context import GradedTemporalContext
from .situation_model_accumulate import unit_phase_vec

DEFAULT_D = 1024


def _cleanup_scores(readback: torch.Tensor, atoms: torch.Tensor) -> torch.Tensor:
    """Re(<conj(atom), readback>)/d for each content atom row. atoms: (V, d) complex64 -> (V,) float."""
    d = readback.shape[0]
    return (torch.real(atoms.conj() @ readback) / d)


class FactorizedEntityStore:
    """Per-entity episodic store of CONTENT x graded CONTEXT x ORDER traces, read by unbinding the (context, order) key
    with a race-to-stop set-return + schema/gist routing. Runs on hdlab.binding + graded_temporal_context."""

    def __init__(self, verb_vocab: List[str], d: int = DEFAULT_D, n_orders: int = 8, seed: int = 20260828,
                 horizon: int = 1000, gist_route: bool = True, gist_min_count: int = 3, gist_frac: float = 0.5,
                 race_ratio: float = 0.78) -> None:
        self.verbs = list(verb_vocab)
        self.vidx = {v: i for i, v in enumerate(self.verbs)}
        self.d = int(d)
        self.n_orders = int(n_orders)
        self.race_ratio = float(race_ratio)
        self.gist_route = bool(gist_route)
        self.gist_min_count = int(gist_min_count)
        self.gist_frac = float(gist_frac)
        g = torch.Generator().manual_seed(int(seed))
        self.content = torch.stack([unit_phase_vec(d, g) for _ in range(len(self.verbs))]) if self.verbs \
            else torch.empty(0, d, dtype=torch.complex64)                                  # (V, d)
        self.order = torch.stack([unit_phase_vec(d, g) for _ in range(n_orders)])          # (O, d)
        self.clock = GradedTemporalContext(d=d, seed=seed + 1, horizon=float(horizon))
        self._bundle: Dict[str, torch.Tensor] = {}
        self._gist: Dict[str, Counter] = defaultdict(Counter)
        self._seen: Dict[str, int] = defaultdict(int)
        self._null_gen = torch.Generator().manual_seed(seed + 999)

    def _is_routine(self, entity: str, verb: str) -> bool:
        if not self.gist_route:
            return False
        g = self._gist[entity]
        if self._seen[entity] < self.gist_min_count or not g:
            return False
        return g[verb] >= self.gist_frac * g.most_common(1)[0][1] and g[verb] >= 2

    def add_event(self, entity: str, t: float, order: int, verb: str) -> str:
        """Store (entity, when=t, within-moment order, verb). ROUTINE verbs go to the gist; ATYPICAL verbs become
        episodic factorized traces. Returns 'gist' or 'episodic'. Bound only at storage."""
        self._seen[entity] += 1
        routed = "episodic"
        if self._is_routine(entity, verb):
            routed = "gist"
        else:
            trace = binding.bind(binding.bind(self.content[self.vidx[verb]], self.clock.ctx(t)),
                                 self.order[order % self.n_orders])
            self._bundle[entity] = trace if entity not in self._bundle else self._bundle[entity] + trace
        self._gist[entity][verb] += 1
        return routed

    def _null_floor(self, entity: str, t: float, k: int = 24) -> float:
        """CMR crosstalk floor: cleanup top-score from decoding UNUSED (t, random-order) keys -> the p95 non-event level."""
        if entity not in self._bundle:
            return 1.0
        b = self._bundle[entity]
        ctxt = self.clock.ctx(t)
        tops = []
        for _ in range(k):
            fake = unit_phase_vec(self.d, self._null_gen)
            sc = _cleanup_scores(binding.unbind(b, binding.bind(ctxt, fake)), self.content)
            tops.append(float(sc.max()))
        return float(torch.quantile(torch.tensor(tops), 0.95))

    def decode_set(self, entity: str, t: float, stop: str = "race",
                   oracle_m: Optional[int] = None, fixed_k: Optional[int] = None) -> List[str]:
        """Return the SET of verbs the entity did at time t. stop='race' (CMR self-terminating), 'oracle', or 'fixed'."""
        if entity not in self._bundle:
            return []
        b = self._bundle[entity]
        ctxt = self.clock.ctx(t)
        accepted = []
        for o in range(self.n_orders):
            sc = _cleanup_scores(binding.unbind(b, binding.bind(ctxt, self.order[o])), self.content)
            top = int(torch.argmax(sc))
            accepted.append((self.verbs[top], float(sc[top])))
        accepted.sort(key=lambda kv: -kv[1])
        if stop == "oracle":
            return [v for v, _ in accepted[:oracle_m]]
        if stop == "fixed":
            return [v for v, _ in accepted[:fixed_k]]
        # race-to-stop (CMR): keep the co-moment set within race_ratio of the winner AND above the crosstalk floor
        thr = max(self.race_ratio * accepted[0][1], self._null_floor(entity, t) * 1.3)
        out = []
        for v, s in accepted:
            if s > thr:
                out.append(v)
            else:
                break
        return out
