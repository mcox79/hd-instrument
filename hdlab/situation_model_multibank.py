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
from .situation_model_accumulate import (
    cleanup_argmax,
    cleanup_set,
    decode_serial_pooled_slots,
    unit_phase_vec,
)
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
        bundle_norm: str = "percomp",
    ) -> None:
        if n_banks < 1:
            raise ValueError(f"n_banks must be >= 1; got {n_banks}")
        self.role_vocab = list(role_vocab)
        self.d = int(d)
        self.max_event_slots = int(max_event_slots)
        self.n_banks = int(n_banks)
        # bundle_norm="percomp" (DEFAULT) -> per-component renorm (norm=None), BYTE-IDENTICAL to prior behavior.
        # "divnorm" -> pooled Carandini-Heeger divisive norm at each per-bank bundle, so an OVERLOADED bank stays
        # serially readable (via decode_serial_pooled). Mirrors AccumulateRegister; opt-in, nothing changes until a
        # caller passes bundle_norm="divnorm". Landed 2026-08-28 from `the_register_bundle_renorm_breaks_the_serial_readout`.
        self.bundle_norm = str(bundle_norm)
        self._bundle_norm_arg = None if self.bundle_norm == "percomp" else self.bundle_norm
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
        return bundling.bundle(torch.stack(events, dim=0), norm=self._bundle_norm_arg)

    def decode(self, entity: str, event_idx: int) -> Tuple[str, Dict[str, float]]:
        """Route to entity's bank by event_idx, unbind, cleanup-argmax over role_vocab."""
        bank_id = stable_bank_id(event_idx, self.n_banks)
        reg = self._bank_register(entity, bank_id)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_argmax(readback, self.role_vecs)

    def decode_set(self, entity: str, event_idx: int, rel_margin: float = 0.5) -> Tuple[List[str], Dict[str, float]]:
        """SET-return decode (CA3 context-cued reactivation): route to the entity's bank, unbind, and return
        ALL roles whose cleanup score clears the margin instead of the single argmax -- the fix for the
        addressing-collision fan (a coarse key holding >1 role). Additive / default-safe: decode() unchanged.
        See hdlab.situation_model_accumulate.cleanup_set for the mechanism + provenance."""
        bank_id = stable_bank_id(event_idx, self.n_banks)
        reg = self._bank_register(entity, bank_id)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_set(readback, self.role_vecs, rel_margin=rel_margin)

    def register(self, entity: str) -> torch.Tensor:
        """Full API-parity with AccumulateRegister.register(): bundle of ALL of the entity's
        events across ALL banks. NOT used by decode() (which routes to the single relevant
        bank for capacity reasons) -- provided only so callers that read .register(entity)
        directly (e.g. a whole-entity gist query) see the same surface as the flat register."""
        if entity not in self._events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        all_events: List[torch.Tensor] = []
        for bank_events in self._events[entity].values():
            all_events.extend(bank_events)
        if len(all_events) == 1:
            return all_events[0]
        return bundling.bundle(torch.stack(all_events, dim=0), norm=self._bundle_norm_arg)

    def decode_serial_bank(self, entity: str, bank_id: int, n_iter: int = 6) -> List[str]:
        """Theta-gamma serial (gain-matched) readout of ALL events in ONE bank, reading the bank's NORMALIZED
        register. On a `bundle_norm="divnorm"` register this recovers an OVERLOADED bank that per-slot argmax loses to
        crosstalk (mirrors AccumulateRegister.decode_serial_pooled at the bank level -- the compose regime the p5
        witness N8 measured: k_per_bank~60, serial 0.733->1.000). ADDITIVE / default-safe: decode()/decode_set()
        byte-unchanged. Returns the decoded role per event stored in the bank (bank-local event order). event slots
        are the idx_vecs the bank's stored events were bound with, in stored order (bank-local)."""
        events = self._events.get(entity, {}).get(bank_id)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r} in bank {bank_id}")
        m = len(events)
        trace = self._bank_register(entity, bank_id)                # the NORMALIZED per-bank register
        keys = [self.idx_vecs[s] for s in range(m)]                 # bank-local sequential slots
        role_mat = torch.stack([self.role_vecs[r] for r in self.role_vocab], dim=0)
        est = decode_serial_pooled_slots(trace, keys, role_mat, n_iter=n_iter)
        return [self.role_vocab[i] for i in est]

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
