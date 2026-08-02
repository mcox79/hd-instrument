"""Per-entity situation-model register: FHRR bind(role, event-slot) accumulated via
bundle, decoded via unbind + cleanup argmax.

Promotion of the VET-CONFIRMED accumulate-vs-overwrite organ (atom 29609,
experiments/exp_situation_model_accumulate_vs_overwrite_v1.py ARM B, capability_registry.jsonl
id situation_model_accumulate_register_organ) into a reusable hdlab/ module. Same algebra,
same decode as the validated cell -- reimplemented on torch complex64 tensors via the
canonical hdlab.binding.bind/unbind + hdlab.bundling.bundle primitives (the experiment cell
used bare numpy at its declared numpy/CPU pre-reg scope; this module follows CLAUDE.md's
torch-tensor-at-API-boundary convention instead, not a mechanism change).

ACCUMULATE (default, validated: accumulate=1.0000 vs overwrite=0.4600 vs floor=0.2100 on
real McGuffey multiclause entity-tracking gold, atom 29609, chain length 2-3): each entity's
register is the FHRR-bundle of ALL its (role, event-slot) bindings -- Kintsch C-I / Zwaan
multi-event indexing. Bounded by bundling capacity beyond the validated chain-length scope.

OVERWRITE (reserved mode, per Finding 3 of notes/wire_extraction_wm_real_text_entity_
tracking_design_2026-08-02.md): each entity's register is REPLACED by only the newest
binding -- genuine state-replacement (e.g. "the cup is now empty"), not multi-event history.
Structurally recovers only the last-written event (the Finding-3 too-simple negative control).
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import torch

from . import binding, bundling


def unit_phase_vec(d: int, generator: torch.Generator) -> torch.Tensor:
    """Random unit-magnitude complex64 vector of dim d (FHRR atomic symbol)."""
    theta = torch.rand(d, generator=generator) * (2.0 * math.pi)
    return torch.polar(torch.ones(d), theta).to(torch.complex64)


def cleanup_argmax(
    readback: torch.Tensor, vocab: Dict[str, torch.Tensor]
) -> Tuple[str, Dict[str, float]]:
    """FHRR cleanup readout: argmax over vocab of Re(sum(conj(vocab_v) * readback)) / d."""
    d = readback.shape[0]
    scores: Dict[str, float] = {}
    for name, v in vocab.items():
        scores[name] = float(torch.real(torch.sum(torch.conj(v) * readback))) / d
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, scores


class AccumulateRegister:
    """FHRR situation-model register: bind(role_vec, event_idx_vec) per event, accumulate via bundle.

    overwrite=False (default): register = bundle of ALL bound events for the entity (validated
    ACCUMULATE organ, atom 29609). overwrite=True: register = only the most recently bound
    event (reserved OVERWRITE / state-replacement mode, Finding 3).
    """

    def __init__(
        self,
        role_vocab: List[str],
        d: int,
        generator: torch.Generator,
        max_event_slots: int = 8,
        overwrite: bool = False,
    ) -> None:
        self.role_vocab = list(role_vocab)
        self.d = int(d)
        self.overwrite = bool(overwrite)
        self.max_event_slots = int(max_event_slots)
        self.role_vecs: Dict[str, torch.Tensor] = {
            r: unit_phase_vec(self.d, generator) for r in self.role_vocab
        }
        self.idx_vecs: List[torch.Tensor] = [
            unit_phase_vec(self.d, generator) for _ in range(self.max_event_slots)
        ]
        self._events: Dict[str, List[torch.Tensor]] = {}

    def add_event(self, entity: str, role: str, event_idx: int) -> None:
        """Bind role_vec to idx_vec at event_idx; accumulate (bundle) or overwrite entity's register."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        if not (0 <= event_idx < self.max_event_slots):
            raise ValueError(f"event_idx {event_idx} out of range [0, {self.max_event_slots})")
        bound = binding.bind(self.role_vecs[role], self.idx_vecs[event_idx])
        if self.overwrite:
            self._events[entity] = [bound]
        else:
            self._events.setdefault(entity, []).append(bound)

    def register(self, entity: str) -> torch.Tensor:
        """Entity's current register: bundle of all accumulated events, or the sole event if one."""
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        if len(events) == 1:
            return events[0]
        return bundling.bundle(torch.stack(events, dim=0))

    def decode(self, entity: str, event_idx: int) -> Tuple[str, Dict[str, float]]:
        """Unbind entity's register by event_idx's key, then cleanup-argmax over role_vocab."""
        reg = self.register(entity)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_argmax(readback, self.role_vecs)

    def entities(self) -> List[str]:
        """Entity ids with at least one recorded event."""
        return list(self._events.keys())
