"""Shared synthetic relation-graph builder for multi-hop experiments.

Used by:
  - exp_continuous_output_multi_hop_v1_n4096   (Path B: state-propagation)
  - exp_path_probability_propagation_v1_n4096   (Path D: posterior-product)
  - exp_spectral_path_identification_v1_n4096   (Path E: spectral coherence)

Single source of truth: each anchor builds coherent d-step paths in the
SAME way so cross-anchor verdicts are by-construction comparable.

Conventions:
  - codebook   : (C, N) torch.Tensor, the substrate codebook (Kerdock 4-coset).
  - n_facts    : M stored facts. Each fact is a (key_idx, val_idx) pair.
  - Coherent path of depth d:
        idx_0 -> idx_1 -> idx_2 -> ... -> idx_d
    where each consecutive pair (idx_i, idx_{i+1}) corresponds to a STORED
    relation (val_idx[fact_j] = idx_{i+1} when key_idx[fact_j] = idx_i).
  - Incoherent path of depth d:
        idx_0 -> j_1 -> j_2 -> ... -> j_d
    where (idx_0, j_1) is NOT a stored fact -- random codebook indices.

ASCII-only. Self-test included.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from typing import Dict, List, Tuple

import torch


def build_relation_facts(
    n_idx: int,
    M: int,
    seed: int,
    device: torch.device,
    closed: bool = True,
) -> Tuple[torch.Tensor, torch.Tensor, Dict[int, int]]:
    """Sample M (key_idx, val_idx) pairs from {0..n_idx-1}, no repeated keys.

    Returns:
      key_idx  : (M,) int64 codebook indices for keys
      val_idx  : (M,) int64 codebook indices for values
      relation : dict mapping key_idx -> val_idx (Python int).

    The relation is functional (each key has exactly one value), which is
    what's needed for the multi-hop path concept.

    closed (default True): val_idx is drawn from the SAME pool as key_idx
      so multi-hop walks have non-trivial probability of remaining inside
      the relation. With closed=False, val_idx is sampled from {0..n_idx-1}
      uniformly and depth>=2 paths are rare.
    """
    gen = torch.Generator(device=device).manual_seed(seed + 5000)
    perm = torch.randperm(n_idx, generator=gen, device=device)
    key_idx = perm[:M].to(torch.long)
    if closed:
        # val_idx is a (different) permutation of the same key pool
        gen_v = torch.Generator(device=device).manual_seed(seed + 5500)
        val_perm = torch.randperm(M, generator=gen_v, device=device)
        val_idx_raw = key_idx[val_perm].clone()
    else:
        val_idx_raw = torch.randint(0, n_idx, (M,), generator=gen, device=device,
                                     dtype=torch.long)
    relation = {int(k.item()): int(v.item())
                for k, v in zip(key_idx, val_idx_raw)}
    return key_idx, val_idx_raw, relation


def coherent_path(
    relation: Dict[int, int],
    depth: int,
    start_key: int,
) -> List[int]:
    """Walk the relation graph for `depth` hops starting at start_key.

    Returns a (depth+1)-list of codebook indices [idx_0, idx_1, ..., idx_d].
    If the walk falls off the relation (some intermediate idx has no
    outgoing fact), returns the partial path (length may be < depth+1).
    """
    path = [int(start_key)]
    cur = int(start_key)
    for _ in range(depth):
        nxt = relation.get(cur)
        if nxt is None:
            break
        path.append(int(nxt))
        cur = int(nxt)
    return path


def sample_coherent_starts(
    relation: Dict[int, int],
    depth: int,
    n_paths: int,
    seed: int,
) -> List[List[int]]:
    """Sample n_paths coherent walks of length depth.

    Walks that fall off the relation are discarded; resamples until n_paths
    full-length paths are found OR 10*n_paths attempts are exhausted.
    """
    gen = torch.Generator(device='cpu').manual_seed(seed + 6000)
    keys = list(relation.keys())
    if not keys:
        return []
    paths: List[List[int]] = []
    attempts = 0
    max_attempts = max(1000, 20 * n_paths)
    while len(paths) < n_paths and attempts < max_attempts:
        attempts += 1
        i = int(torch.randint(0, len(keys), (1,), generator=gen).item())
        start = keys[i]
        p = coherent_path(relation, depth, start)
        if len(p) == depth + 1:
            paths.append(p)
    return paths


def sample_incoherent_paths(
    n_idx: int,
    depth: int,
    n_paths: int,
    seed: int,
    relation: Dict[int, int] | None = None,
) -> List[List[int]]:
    """Sample n_paths random walks of length depth.

    These are negative controls: random codebook indices, NOT walks of the
    relation. If `relation` is supplied, any sampled walk that happens to
    coincide with a coherent prefix is rejected.
    """
    gen = torch.Generator(device='cpu').manual_seed(seed + 7000)
    paths: List[List[int]] = []
    attempts = 0
    max_attempts = max(2000, 20 * n_paths)
    while len(paths) < n_paths and attempts < max_attempts:
        attempts += 1
        indices = torch.randint(0, n_idx, (depth + 1,), generator=gen,
                                 dtype=torch.long).tolist()
        if relation is not None:
            # Reject if it accidentally IS a coherent path
            is_coherent = True
            for i in range(depth):
                if relation.get(int(indices[i])) != int(indices[i + 1]):
                    is_coherent = False
                    break
            if is_coherent:
                continue
        paths.append([int(x) for x in indices])
    return paths


def _selftest() -> None:
    """Validate relation-graph builder at small scale."""
    device = torch.device('cpu')
    n_idx = 256
    M = 32
    seed = 17
    key_idx, val_idx, relation = build_relation_facts(n_idx, M, seed, device)
    assert key_idx.shape == (M,), f"key_idx shape: {key_idx.shape}"
    assert val_idx.shape == (M,), f"val_idx shape: {val_idx.shape}"
    assert len(relation) == M, f"relation size: {len(relation)} != {M}"
    # Walk one coherent path
    keys = list(relation.keys())
    p = coherent_path(relation, depth=2, start_key=keys[0])
    assert 1 <= len(p) <= 3, f"path length: {len(p)}"
    assert p[0] == keys[0], f"path start mismatch"
    # Sample several
    coh = sample_coherent_starts(relation, depth=2, n_paths=4, seed=seed)
    assert isinstance(coh, list), "coherent samples not a list"
    # Incoherent
    inc = sample_incoherent_paths(n_idx, depth=2, n_paths=4,
                                   seed=seed, relation=relation)
    assert len(inc) == 4 and all(len(p) == 3 for p in inc), (
        f"incoherent paths: {len(inc)} of length 3 each")
    print("[selftest] _relation_graph PASS", flush=True)


_selftest()


__all__ = [
    "build_relation_facts",
    "coherent_path",
    "sample_coherent_starts",
    "sample_incoherent_paths",
]
