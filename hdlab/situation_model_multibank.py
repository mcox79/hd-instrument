"""Multi-bank sub-bundled situation-model register: capacity fix for the flat-bundle wall.

CONTEXT (Director-assigned, atom 29629): hdlab.situation_model_accumulate.AccumulateRegister
stores an entity's WHOLE event history as ONE flat FHRR bundle of bind(role, event_idx)
terms (max_event_slots=8). As events/entity grows, that single superposition hits the HD
bundle-capacity wall -- cross-talk from co-superposed items degrades cleanup-argmax decode.
This IS the reported decode self-consistency regression 89.8% -> 67.2% on the Anne
consolidation-ledger scenes: too many events crammed into one register.

hdlab.state_of_mind.py explicitly names hdlab.working_memory's multi-bank (K-capacity,
k_per_bank>=64 chain-grade at K=4096/n_banks=64) as the durable-memory upgrade path. This
module is that upgrade applied to the situation-model register: instead of superposing an
entity's whole history into one bundle, its events are ROUTED across n_banks independent
sub-bundles, so per-bundle load (and therefore cross-talk) is k_per_bank = events_per_entity
/ n_banks rather than the full event count.

ROUTING DIFFERS FROM hdlab.working_memory's validated regime -- BE HONEST ABOUT IT:
hdlab.working_memory's chain-grade guarantee (recall>=0.95 at k_per_bank>=64, N_DIM=8192,
FEATURE_OVERLAP_FRAC<=0.20) covers NOISY-CUE bank routing (the reader doesn't know which
bank an item lives in and must recover it from an imperfect cue via argmax over bank tags).
Here, decode(entity, event_idx) is called WITH event_idx known exactly, so bank routing is
a deterministic hash lookup (stable_bank_id), not a noisy-cue argmax -- routing accuracy is
1.0 by construction and is NOT the thing being tested. The thing being tested is purely
whether a SMALLER per-bank bundle (lower k_per_bank) keeps FHRR cleanup-argmax decode
accurate, which is the same physical mechanism (superposition cross-talk vs bundle size)
hdlab.working_memory's per-bank cleanup exercises, but on FHRR complex64 bind/bundle/cleanup-
argmax rather than their BSC bipolar sum-quantize/cleanup. The BSC chain-grade envelope
constants (k_per_bank>=64 at N_DIM=8192) do NOT numerically transfer to this FHRR mechanism
at whatever d this module is run at -- call assert_k_per_bank_in_discriminating_regime() for
scope-declaration honesty (it will typically no-op below N_DIM=8192 per its own docstring),
but the actual evidence for whether THIS module's regime is discriminating is the empirical
flat-vs-multibank crossover sweep in experiments/exp_situation_model_multibank_capacity_v1.py,
not a borrowed numeric threshold from a different primitive family.

API: same add_event(entity, role, event_idx) / decode(entity, event_idx) / entities() surface
as AccumulateRegister -- drop-in replacement, only the routing (bank_id = hash(event_idx) %
n_banks) and per-bank storage (dict of bank_id -> bundle) differ from the flat single bundle.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

import torch

from . import binding, bundling
from .situation_model_accumulate import cleanup_argmax, unit_phase_vec
from .working_memory import assert_k_per_bank_in_discriminating_regime  # noqa: F401 (re-export for callers)


def stable_bank_id(event_idx: int, n_banks: int) -> int:
    """Deterministic content-anchored bank routing: sha256(event_idx) % n_banks.

    Deterministic (not RNG-seeded) so the same event_idx always routes to the same bank
    across add_event calls and the matching decode call -- this is the "content-anchored
    bank-id derivation" hdlab.working_memory's docstring names as the multi-bank routing
    scheme, specialized here to route on the (known-at-decode-time) event_idx key.
    """
    if n_banks < 1:
        raise ValueError(f"n_banks must be >= 1; got {n_banks}")
    h = hashlib.sha256(str(int(event_idx)).encode("ascii")).digest()
    return int.from_bytes(h[:8], "big") % n_banks


class MultiBankAccumulateRegister:
    """Drop-in multi-bank replacement for AccumulateRegister.

    Same add_event/decode/entities API. Each entity's events are routed across n_banks
    independent FHRR bundles by stable_bank_id(event_idx, n_banks) instead of superposed
    into one flat bundle -- capacity scales with n_banks (per-bank load falls as n_banks
    grows) instead of being fixed by one bundle's cross-talk floor.
    """

    def __init__(
        self,
        role_vocab: List[str],
        d: int,
        generator: torch.Generator,
        max_event_slots: int = 8,
        n_banks: int = 8,
    ) -> None:
        if n_banks < 1:
            raise ValueError(f"n_banks must be >= 1; got {n_banks}")
        self.role_vocab = list(role_vocab)
        self.d = int(d)
        self.max_event_slots = int(max_event_slots)
        self.n_banks = int(n_banks)
        self.role_vecs: Dict[str, torch.Tensor] = {
            r: unit_phase_vec(self.d, generator) for r in self.role_vocab
        }
        self.idx_vecs: List[torch.Tensor] = [
            unit_phase_vec(self.d, generator) for _ in range(self.max_event_slots)
        ]
        # entity -> {bank_id: [bound events]}
        self._events: Dict[str, Dict[int, List[torch.Tensor]]] = {}

    def add_event(self, entity: str, role: str, event_idx: int) -> None:
        """Bind role_vec to idx_vec at event_idx; accumulate into the entity's routed bank."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        if not (0 <= event_idx < self.max_event_slots):
            raise ValueError(f"event_idx {event_idx} out of range [0, {self.max_event_slots})")
        bound = binding.bind(self.role_vecs[role], self.idx_vecs[event_idx])
        bank_id = stable_bank_id(event_idx, self.n_banks)
        bank_map = self._events.setdefault(entity, {})
        bank_map.setdefault(bank_id, []).append(bound)

    def _bank_register(self, entity: str, bank_id: int) -> torch.Tensor:
        events = self._events.get(entity, {}).get(bank_id)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r} in bank {bank_id}")
        if len(events) == 1:
            return events[0]
        return bundling.bundle(torch.stack(events, dim=0))

    def decode(self, entity: str, event_idx: int) -> Tuple[str, Dict[str, float]]:
        """Route to entity's bank by event_idx, unbind, cleanup-argmax over role_vocab."""
        bank_id = stable_bank_id(event_idx, self.n_banks)
        reg = self._bank_register(entity, bank_id)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_argmax(readback, self.role_vecs)

    def entities(self) -> List[str]:
        """Entity ids with at least one recorded event."""
        return list(self._events.keys())

    def bank_loads(self, entity: str) -> Dict[int, int]:
        """Per-bank event count for an entity (diagnostic: capacity load per bank)."""
        return {b: len(v) for b, v in self._events.get(entity, {}).items()}

    def max_bank_load(self, entity: str) -> int:
        """Max events landed in any single bank for an entity (the effective k_per_bank)."""
        loads = self.bank_loads(entity)
        return max(loads.values()) if loads else 0
