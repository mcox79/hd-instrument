"""hdlab/content_addressable_retrieval.py -- cue-based content-addressable retrieval (ADDITIVE Lewis-Vasishth).

THE MISSING ORGAN the content_addressable_retrieval problem identified (integrated SOLVED/EXCELLENT
2026-08-26). Our situation-model register looks memories up by an EXACT key (a hash of the known
key); the brain retrieves by a PARTIAL DESCRIPTION and finds the closest match, so a fuzzy/incomplete
cue still works. This organ is that retrieval, as a self-contained, importable module -- it does NOT
modify the live register (extending the register's storage to keep per-feature codes matchable is the
separate downstream wiring); it is the ALGORITHM, ready to compose.

THE COMPUTATION, AND WHY ADDITIVE (the load-bearing fidelity point). An item is a set of per-feature
codes {feature: FHRR vector} (e.g. entity, event, role) plus a payload (e.g. the filler). Retrieval
scores each item by the SUM of per-feature cue matches and returns the argmax:

    activation(item) = SUM over the cue's KNOWN features f of  w_f * sim(cue_f, item.f)
    retrieve = argmax_item activation(item)          (Lewis & Vasishth 2005; ACT-R; audit E3)

This is ADDITIVE, NOT a multiplicative single-composite-key match. The register's current op binds all
cue features into ONE key and matches that composite; because FHRR bind is elementwise MULTIPLY, ONE
wrong or missing feature ORTHOGONALISES the whole composite (its similarity to the target collapses to
~0), so a partial or competitor-dominated cue COLLAPSES. Additive integration drops ONE term instead
and degrades GRACEFULLY -- measured: additive 0.33-0.70 vs composite 0.03-0.04 under a dropped/interfering
feature (near-orthogonal codes).

HONEST SCOPE (measured, do not oversell). With the substrate's REAL graded features (dog~cat~wolf) the
additive-vs-composite gap is mostly a TIE -- the composite's catastrophic collapse only appears under
near-orthogonal (truly-dissimilar or dropped) corruption, which real similarity makes rare. So additive
is the RIGHT DEFAULT (never worse, natively serves a partial cue, no unphysical collapse) but NOT a big
everyday accuracy lift. It does NOT and SHOULD NOT confer immunity to similarity interference: with
genuinely similar competitors, additive is fooled too -- that is the fan effect, real human behaviour a
faithful model must EXHIBIT (false-memory intrusions). The ACT-R fan penalty is regime-specific (helped
near-orthogonal codes, HURT graded ones) -- DEFAULT OFF. Interference RESOLUTION is a separate open problem.

BRAIN FRAME -- PINNED vs OUR-INVENTION.
  PINNED    cue-based retrieval is content-addressable and ADDITIVE over cue features, retrieve the max
            (Lewis & Vasishth 2005 activation-based retrieval; ACT-R; the E3 coreference mechanism).
  OUR-INVENTION-UNDER-TEST  the per-feature weights w_f, whether to apply a fan penalty (default OFF),
            and the similarity kernel (here FHRR sim = Re<conj a, b>/d, the live register's own metric).

STATUS: OFF-PATH / WIRE_CANDIDATE. Importing this changes NO existing behaviour. Composing it into the
live reader (feed it the register's per-feature slot codes) + measuring end-to-end is the wire-and-measure
step -- MEASURE on the live task before any capability claim (the isolation win is a construction proof).

USAGE
  python -m hdlab.content_addressable_retrieval      # self-test
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import torch


def fhrr_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    """FHRR similarity Re(sum conj(a)*b)/d -- the live register's own metric (a unit-phase FHRR dot)."""
    return float(torch.real(torch.sum(torch.conj(a) * b)).item()) / a.shape[-1]


@dataclass
class _Item:
    item_id: object
    features: Dict[str, torch.Tensor]     # feature name -> FHRR complex64 code
    payload: object = None                # e.g. the filler code / value to return


@dataclass
class Retrieval:
    """Outcome of a cue-based retrieval."""
    item_id: object
    payload: object
    activation: float                     # the winning additive activation (the retrieval confidence)
    margin: float                         # winner activation minus runner-up (separation / competition)
    n_features_matched: int


class AdditiveCueRetrieval:
    """Content-addressable store: add items as per-feature FHRR codes, retrieve by a partial cue via
    ADDITIVE Lewis-Vasishth activation (argmax). No index/hash -- the match is parallel over all items.

    fan_penalty=False by default (regime-specific -- helps near-orthogonal codes, hurts graded ones)."""

    def __init__(self, *, fan_penalty: bool = False,
                 weights: Optional[Dict[str, float]] = None) -> None:
        self.fan_penalty = bool(fan_penalty)
        self.weights = dict(weights) if weights else {}
        self._items: List[_Item] = []

    def add(self, item_id, features: Dict[str, torch.Tensor], payload=None) -> None:
        if not features:
            raise ValueError("an item needs at least one per-feature code")
        self._items.append(_Item(item_id, dict(features), payload))

    def __len__(self) -> int:
        return len(self._items)

    def _fan(self, feature: str, cue_vec: torch.Tensor) -> int:
        """ACT-R fan of a cue feature: how many stored items this cue value matches well (>0.5). Only
        computed when fan_penalty is on; a large fan divides that feature's contribution down."""
        n = 0
        for it in self._items:
            v = it.features.get(feature)
            if v is not None and fhrr_sim(cue_vec, v) > 0.5:
                n += 1
        return max(1, n)

    def retrieve(self, cue: Dict[str, Optional[torch.Tensor]]) -> Optional[Retrieval]:
        """Score every item by the additive sum of its KNOWN cue-feature matches; return the argmax.
        `cue` maps feature -> vector (a known/partial cue) or None (unknown -> that feature is dropped,
        it contributes nothing rather than orthogonalising the match). None if the store is empty or the
        cue names no known feature."""
        known = {f: v for f, v in cue.items() if v is not None}
        if not self._items or not known:
            return None
        fan = {f: self._fan(f, v) for f, v in known.items()} if self.fan_penalty else None
        best_i, best_act, runner = -1, float("-inf"), float("-inf")
        n_matched = 0
        for i, it in enumerate(self._items):
            act = 0.0
            m = 0
            for f, cv in known.items():
                iv = it.features.get(f)
                if iv is None:
                    continue
                w = self.weights.get(f, 1.0)
                s = fhrr_sim(cv, iv)
                act += (w * s / fan[f]) if fan is not None else (w * s)
                m += 1
            if act > best_act:
                runner = best_act
                best_act, best_i, n_matched = act, i, m
            elif act > runner:
                runner = act
        if best_i < 0:
            return None
        it = self._items[best_i]
        margin = best_act - (runner if runner != float("-inf") else best_act)
        return Retrieval(it.item_id, it.payload, float(best_act), float(margin), n_matched)


# -------------------------------------------------------------------------------------------
# SELF-TESTS. Each can fail.
# -------------------------------------------------------------------------------------------

def _fhrr(n: int, g: torch.Generator) -> torch.Tensor:
    import math
    ph = torch.rand(n, generator=g) * (2.0 * math.pi)
    return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)


def _build(d=256, M=32, seed=7):
    g = torch.Generator().manual_seed(seed)
    ents = [_fhrr(d, g) for _ in range(M)]
    evs = [_fhrr(d, g) for _ in range(M)]
    roles = [_fhrr(d, g) for _ in range(M)]
    fills = [_fhrr(d, g) for _ in range(M)]
    store = AdditiveCueRetrieval()
    for i in range(M):
        store.add(i, {"entity": ents[i], "event": evs[i], "role": roles[i]}, payload=i)
    return store, ents, evs, roles, fills, g


def _selftest_full_cue_recovers():
    store, ents, evs, roles, _, _ = _build()
    ok = sum(store.retrieve({"entity": ents[i], "event": evs[i], "role": roles[i]}).payload == i
             for i in range(len(store)))
    assert ok == len(store), f"full cue must recover every item: {ok}/{len(store)}"
    print(f"PASS full_cue_recovers ({ok}/{len(store)})")


def _selftest_partial_cue_still_works():
    # drop the event feature (None): additive drops the term; a 2-of-3 cue should still mostly recover
    store, ents, evs, roles, _, _ = _build()
    ok = sum(store.retrieve({"entity": ents[i], "event": None, "role": roles[i]}).payload == i
             for i in range(len(store)))
    assert ok >= 0.8 * len(store), f"partial (2/3) cue should still recover most items: {ok}/{len(store)}"
    print(f"PASS partial_cue_still_works ({ok}/{len(store)} on a 2-of-3 cue)")


def _selftest_additive_beats_composite_under_a_dropped_feature():
    # the load-bearing fidelity point: with a DROPPED feature, additive recovers where a multiplicative
    # composite-key match orthogonalises. Reproduce the composite arm inline (bind the 2 known features).
    from . import binding
    store, ents, evs, roles, _, _ = _build()
    add_ok, comp_ok = 0, 0
    for i in range(len(store)):
        # additive: 2-of-3 known
        if store.retrieve({"entity": ents[i], "event": None, "role": roles[i]}).payload == i:
            add_ok += 1
        # composite: bind the 2 known cue features, argmax against each item's bound 3-feature composite
        cue_comp = binding.bind(ents[i], roles[i])
        best, arg = float("-inf"), -1
        for j in range(len(store)):
            item_comp = binding.bind(binding.bind(ents[j], evs[j]), roles[j])
            s = fhrr_sim(cue_comp, item_comp)
            if s > best:
                best, arg = s, j
        comp_ok += (arg == i)
    assert add_ok > comp_ok, f"additive must beat composite under a dropped feature: {add_ok} vs {comp_ok}"
    print(f"PASS additive_beats_composite_under_a_dropped_feature (additive {add_ok} > composite {comp_ok})")


def _selftest_shuffled_cue_twin_loses():
    store, ents, evs, roles, _, g = _build()
    # info-free twin: cue with a DIFFERENT item's codes -> should not systematically recover the target
    perm = torch.randperm(len(store), generator=g).tolist()
    ok = sum(store.retrieve({"entity": ents[perm[i]], "event": evs[perm[i]], "role": roles[perm[i]]}).payload == i
             for i in range(len(store)) if perm[i] != i)
    assert ok <= 1, f"a deranged cue must not recover the target: {ok}"
    print("PASS shuffled_cue_twin_loses")


def run_selftests() -> dict:
    _selftest_full_cue_recovers()
    _selftest_partial_cue_still_works()
    _selftest_additive_beats_composite_under_a_dropped_feature()
    _selftest_shuffled_cue_twin_loses()
    return {"ok": True}


if __name__ == "__main__":
    run_selftests()
    print("CONTENT-ADDRESSABLE RETRIEVAL SELF-TEST PASS")
