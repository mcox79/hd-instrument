"""Ablation context managers for causal probing of the connection layer.

Three kinds of ablation are supported:
- edges(relation, edges): mask specific (src, dst) pairs in a named relation
- relation(name): disable a whole named relation channel
- modulator(name): pin a modulator to its default value, neutralizing its effect

The active ablations are stored in a thread-local registry. Connection code consults
`is_edge_ablated(...)`, `is_relation_ablated(...)`, `is_modulator_ablated(...)` before
firing. Each entry into an ablation scope emits a semantic.ablation_active event.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable, Iterator

from . import semantic


_relations: set[str] = set()
_edges: set[tuple[str, str, str]] = set()  # (relation, src, dst)
_modulators: set[str] = set()


def is_relation_ablated(name: str) -> bool:
    return name in _relations


def is_edge_ablated(relation: str, src: str, dst: str) -> bool:
    if relation in _relations:
        return True
    return (relation, src, dst) in _edges or (relation, dst, src) in _edges


def is_modulator_ablated(name: str) -> bool:
    return name in _modulators


def active() -> dict[str, list]:
    """Snapshot of all currently active ablations (read-only)."""
    return {
        "relations": sorted(_relations),
        "edges": sorted(_edges),
        "modulators": sorted(_modulators),
    }


@contextmanager
def relation(name: str) -> Iterator[str]:
    """Disable an entire named relation channel for the duration of the block."""
    added = name not in _relations
    _relations.add(name)
    semantic.ablation_active("relation", name)
    try:
        yield name
    finally:
        if added:
            _relations.discard(name)


@contextmanager
def edges(relation_name: str, pairs: Iterable[tuple[str, str]]) -> Iterator[list[tuple[str, str]]]:
    """Mask specific (src, dst) edges in a named relation. Symmetric: both directions blocked."""
    added: list[tuple[str, str, str]] = []
    listed = list(pairs)
    for src, dst in listed:
        key = (relation_name, src, dst)
        if key not in _edges:
            _edges.add(key)
            added.append(key)
        semantic.ablation_active("edge", f"{relation_name}:{src}->{dst}")
    try:
        yield listed
    finally:
        for key in added:
            _edges.discard(key)


@contextmanager
def modulator(name: str) -> Iterator[str]:
    """Pin a modulator to its default (neutralize its influence) for the block."""
    added = name not in _modulators
    _modulators.add(name)
    semantic.ablation_active("modulator", name)
    try:
        yield name
    finally:
        if added:
            _modulators.discard(name)
