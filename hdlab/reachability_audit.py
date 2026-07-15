"""Reachability-audit: a cheap graph-traversal tool certifying each entity's reachability to grounded/measured
content (mode A) OR, on the current metadata-empty substrate, its connectivity to rich relational structure
(mode B). Doubles as a PREDICTIVE DIAGNOSTIC for where relational reasoning underperforms.

Motivation (drill_grounding_scoping_is_it_subsumed_by_foundation_hub_or_separate_2026-07-15): grounding is largely
SUBSUMED by the measured-attribute foundation, with ONE residual gap -- identity != grounding. A bare canonical id
with no reachable measured/grounded content is an ungrounded name-tag (a closed-relational-island). This tool is
the cheap certification of measured-reachability that also predicts relational-inference failure.

TWO MODES:
  (a) MEASURED-REACHABILITY (`measured_reachability`): per-entity count of GROUNDED entities reachable within k hops.
      On the current substrate the grounded set is EMPTY (metadata 100% empty) so this returns all zeros -- inert but
      READY to run against Costanzo/BioGRID/measured-attribute modules the moment they land (pass a non-empty
      grounded_mask). The self-test exercises it with a synthetic grounded set to prove the traversal is correct.
  (b) RELATIONAL-REACHABILITY (`k_hop_reachable_mass`, `distance_to_hub`, `mean_neighbor_degree`): runs NOW on the
      existing reduced-CSKG. Proxy anchors for "reaches rich relational structure": how many distinct entities an
      entity can reach within k hops, and how far it sits from the high-degree relational core (hubs).

Plus the correlation machinery to VALIDATE the diagnostic claim (does reachability predict per-entity relational
accuracy BEYOND a raw-degree/frequency confound): `partial_spearman` (degree-controlled rank correlation) and
`perm_p_partial_stratified` (a within-degree-stratum permutation null -- the decisive beyond-degree control).

Glass-box, NO LLM. Pure numpy + stdlib BFS. ASCII-only. No emojis. Deterministic (fixed seeds; sorted iteration).
"""

from collections import deque
from typing import List, Optional, Sequence, Tuple

import numpy as np

Adj = List[np.ndarray]


# ---------------------------------------------------------------------------
# Graph construction (undirected; built ONLY from train edges by the caller -> no query leakage).
# ---------------------------------------------------------------------------

def build_undirected_adj(edges_int: np.ndarray, n_ent: int) -> Adj:
    """edges_int: (E,3) int64 [h,r,t]. Returns per-entity neighbor arrays (undirected, self-loops dropped, deduped).

    Deterministic: neighbor arrays are sorted ascending."""
    nbr = [set() for _ in range(n_ent)]
    if edges_int.shape[0]:
        h = edges_int[:, 0].astype(np.int64)
        t = edges_int[:, 2].astype(np.int64)
        for a, b in zip(h.tolist(), t.tolist()):
            if a != b:
                nbr[a].add(b)
                nbr[b].add(a)
    return [np.array(sorted(s), dtype=np.int64) for s in nbr]


def degree_vector(adj: Adj) -> np.ndarray:
    """Per-entity undirected degree (distinct neighbor count). (N,) int64."""
    return np.array([a.shape[0] for a in adj], dtype=np.int64)


# ---------------------------------------------------------------------------
# Mode (b): relational-reachability proxies.
# ---------------------------------------------------------------------------

def k_hop_reachable_mass(adj: Adj, k: int, cap: Optional[int] = None) -> np.ndarray:
    """Per-entity count of DISTINCT entities reachable within k undirected hops (excludes self). (N,) int64.

    The primary relational-reachability anchor: 'how much relational structure this entity can reach'. cap bounds the
    seen-set growth for extreme hubs (BFS stops early once |seen| >= cap; the recorded mass is then a floor)."""
    n = len(adj)
    out = np.zeros(n, dtype=np.int64)
    for s in range(n):
        seen = {s}
        frontier = [s]
        for _ in range(k):
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    vi = int(v)
                    if vi not in seen:
                        seen.add(vi)
                        nxt.append(vi)
            frontier = nxt
            if cap is not None and len(seen) >= cap:
                break
        out[s] = len(seen) - 1
    return out


def distance_to_hub(adj: Adj, hub_ids: Sequence[int], max_dist: int = 8) -> np.ndarray:
    """Per-entity shortest-path hop distance to the NEAREST hub (multi-source BFS). Unreachable -> max_dist+1. (N,).

    'How far from the rich relational core.' Higher = more peripheral (LOWER reachability). Hubs are at distance 0."""
    n = len(adj)
    dist = np.full(n, max_dist + 1, dtype=np.int64)
    dq = deque()
    for h in sorted(set(int(x) for x in hub_ids)):
        if 0 <= h < n:
            dist[h] = 0
            dq.append(h)
    while dq:
        u = dq.popleft()
        du = dist[u]
        if du >= max_dist:
            continue
        for v in adj[u]:
            vi = int(v)
            if dist[vi] > du + 1:
                dist[vi] = du + 1
                dq.append(vi)
    return dist


def mean_neighbor_degree(adj: Adj, deg: Optional[np.ndarray] = None) -> np.ndarray:
    """Per-entity mean degree of its neighbors (0 for isolated). (N,) float64. 'Do I connect to hubs?'"""
    if deg is None:
        deg = degree_vector(adj)
    n = len(adj)
    out = np.zeros(n, dtype=np.float64)
    for s in range(n):
        a = adj[s]
        if a.shape[0]:
            out[s] = float(deg[a].mean())
    return out


def top_degree_hubs(deg: np.ndarray, frac: float) -> np.ndarray:
    """Entity ids of the top-`frac` by degree (the relational core). (H,) int64. Deterministic tie-break by id."""
    n = deg.shape[0]
    n_hub = max(1, int(round(frac * n)))
    order = np.lexsort((np.arange(n), -deg))  # primary: -deg (desc); secondary: id (asc) for determinism
    return np.sort(order[:n_hub]).astype(np.int64)


# ---------------------------------------------------------------------------
# Mode (a): measured-reachability certification (STUB-READY; inert on metadata-empty substrate).
# ---------------------------------------------------------------------------

def measured_reachability(adj: Adj, grounded_mask: np.ndarray, k: int) -> np.ndarray:
    """Per-entity count of GROUNDED entities reachable within k undirected hops (self counts if grounded). (N,) int64.

    grounded_mask: (N,) bool -- True where the entity carries measured/grounded content. On the CURRENT substrate this
    is all-False (metadata 100% empty) -> returns all zeros (mode (a) is inert but wired). Pass a real grounded_mask
    (e.g. Costanzo/BioGRID-linked entities) to certify measured-reachability. Certified-grounded iff out[e] > 0."""
    n = len(adj)
    out = np.zeros(n, dtype=np.int64)
    gm = np.asarray(grounded_mask, dtype=bool)
    if not gm.any():
        return out  # inert: no grounded content exists yet; ready for measured-attribute modules.
    for s in range(n):
        seen = {s}
        frontier = [s]
        for _ in range(k):
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    vi = int(v)
                    if vi not in seen:
                        seen.add(vi)
                        nxt.append(vi)
            frontier = nxt
        idx = np.fromiter(seen, dtype=np.int64, count=len(seen))
        out[s] = int(gm[idx].sum())
    return out


# ---------------------------------------------------------------------------
# Rank-correlation machinery (degree-controlled). NO scipy dependency.
# ---------------------------------------------------------------------------

def rankdata_avg(a: np.ndarray) -> np.ndarray:
    """Average ranks (ties share the mean rank). 1-based. (N,) float64. Deterministic (stable sort)."""
    a = np.asarray(a, dtype=np.float64)
    n = a.shape[0]
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    sa = a[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean()
    y = y - y.mean()
    denom = float(np.sqrt(float((x * x).sum()) * float((y * y).sum())))
    return float((x * y).sum() / denom) if denom > 0 else float("nan")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (Pearson of average-ranks). float."""
    return _pearson(rankdata_avg(x), rankdata_avg(y))


def _residualize(r: np.ndarray, on_rank: np.ndarray) -> np.ndarray:
    """OLS residual of r regressed on [1, on_rank]."""
    A = np.vstack([np.ones_like(on_rank), on_rank]).T
    coef, _res, _rank, _sv = np.linalg.lstsq(A, r, rcond=None)
    return r - A @ coef


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Partial Spearman correlation of x,y CONTROLLING for z (rank-residualization). float.

    Positive => x and y move together AFTER removing everything z (degree) linearly explains on the rank scale."""
    rx, ry, rz = rankdata_avg(x), rankdata_avg(y), rankdata_avg(z)
    ex, ey = _residualize(rx, rz), _residualize(ry, rz)
    return _pearson(ex, ey)


def quantile_strata(z: np.ndarray, n_bins: int) -> np.ndarray:
    """Assign each element to a quantile bin of z (0..n_bins-1). (N,) int64. Robust to ties (unique-edge dedupe)."""
    z = np.asarray(z, dtype=np.float64)
    n = z.shape[0]
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    qs = np.quantile(z, np.linspace(0.0, 1.0, n_bins + 1))
    edges = np.unique(qs)
    if edges.shape[0] < 2:
        return np.zeros(n, dtype=np.int64)
    b = np.digitize(z, edges[1:-1], right=False)
    return b.astype(np.int64)


def perm_p_partial_stratified(x: np.ndarray, y: np.ndarray, z: np.ndarray, strata: np.ndarray,
                              n_perm: int, seed: int) -> Tuple[float, float, float, float]:
    """Two-sided permutation p for partial_spearman(x,y|z) under a WITHIN-degree-stratum shuffle of x.

    Shuffling x only among entities of SIMILAR degree preserves the degree distribution under the null, so a real
    partial-rho that exceeds this null is signal BEYOND degree. Returns (real_rho, p_two_sided, null_mean, null_std)."""
    x = np.asarray(x, dtype=np.float64)
    real = partial_spearman(x, y, z)
    if not (real == real):
        return real, float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    strata = np.asarray(strata)
    idx_by = [np.where(strata == s)[0] for s in np.unique(strata)]
    nulls = np.empty(n_perm, dtype=np.float64)
    for p in range(n_perm):
        xp = x.copy()
        for ids in idx_by:
            if ids.shape[0] > 1:
                xp[ids] = x[ids][rng.permutation(ids.shape[0])]
        nulls[p] = partial_spearman(xp, y, z)
    cnt = int(np.sum(np.abs(nulls) >= abs(real)))
    p_two = (cnt + 1) / (n_perm + 1)
    return float(real), float(p_two), float(np.mean(nulls)), float(np.std(nulls))
