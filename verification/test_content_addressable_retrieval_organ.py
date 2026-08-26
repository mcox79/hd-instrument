"""Scaffold-free witness for hdlab/content_addressable_retrieval.py (ADDITIVE Lewis-Vasishth cue-based
retrieval), landed 2026-08-26 from the integrated problem content_addressable_retrieval_over_a_separated_store.

Proves first-hand + deterministically that the ORGAN carries the win: (1) a PARTIAL (2-of-3) cue still
recovers (additive drops the missing term, does not orthogonalise); (2) additive BEATS a multiplicative
composite-key match under a dropped feature (the fidelity point -- one wrong/missing feature collapses the
composite but only drops one additive term); (3) a deranged (info-free) cue does not recover the target.
Writes nothing.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import math

import torch

from hdlab import binding
from hdlab.content_addressable_retrieval import AdditiveCueRetrieval, fhrr_sim


def _fhrr(n, g):
    ph = torch.rand(n, generator=g) * (2.0 * math.pi)
    return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)


def _pop(d=256, M=32, seed=13):
    g = torch.Generator().manual_seed(seed)
    ents = [_fhrr(d, g) for _ in range(M)]
    evs = [_fhrr(d, g) for _ in range(M)]
    roles = [_fhrr(d, g) for _ in range(M)]
    store = AdditiveCueRetrieval()
    for i in range(M):
        store.add(i, {"entity": ents[i], "event": evs[i], "role": roles[i]}, payload=i)
    return store, ents, evs, roles, g


def test_module_selftests_pass():
    from hdlab.content_addressable_retrieval import run_selftests
    assert run_selftests()["ok"]
    print("PASS module_selftests_pass")


def test_partial_cue_and_additive_beats_composite():
    store, ents, evs, roles, _ = _pop()
    M = len(store)
    add_ok, comp_ok = 0, 0
    for i in range(M):
        # additive, 2-of-3 known (event dropped)
        r = store.retrieve({"entity": ents[i], "event": None, "role": roles[i]})
        add_ok += (r is not None and r.payload == i)
        # multiplicative composite: bind the two known features, argmax over the 3-feature item composites
        cue = binding.bind(ents[i], roles[i])
        best, arg = float("-inf"), -1
        for j in range(M):
            item = binding.bind(binding.bind(ents[j], evs[j]), roles[j])
            s = fhrr_sim(cue, item)
            if s > best:
                best, arg = s, j
        comp_ok += (arg == i)
    assert add_ok >= 0.8 * M, f"additive partial-cue recovery too low: {add_ok}/{M}"
    assert add_ok > comp_ok + 5, f"additive must clearly beat composite under a dropped feature: {add_ok} vs {comp_ok}"
    print(f"PASS partial_cue_and_additive_beats_composite (additive {add_ok}/{M} >> composite {comp_ok}/{M})")


def test_deranged_cue_loses():
    store, ents, evs, roles, g = _pop()
    M = len(store)
    perm = torch.randperm(M, generator=g).tolist()
    hits = sum(store.retrieve({"entity": ents[perm[i]], "event": evs[perm[i]], "role": roles[perm[i]]}).payload == i
               for i in range(M) if perm[i] != i)
    assert hits <= 1, f"a deranged cue must not recover the target: {hits}"
    print("PASS deranged_cue_loses")


if __name__ == "__main__":
    test_module_selftests_pass()
    test_partial_cue_and_additive_beats_composite()
    test_deranged_cue_loses()
    print("WITNESS PASS")
