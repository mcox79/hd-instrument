"""Substrate-native edge-importance graph H[i,j] (per-pair importance).

The "this atom-pair matters" signal that is STRUCTURALLY ORTHOGONAL to per-atom
weight magnitude |W[i]|. Per-atom importance signals (excitability.py) all
inherit magnitude correlation under retrieval-driven updates because retrieval-
hit IS magnitude-driven on argmax cleanup (Wave 1.6 triple-confirmed:
cor(E,|W|)=0.984). EDGE-space lives on a different observability axis.

Mechanism (NumPy; no torch dependency):
  H[i,j] in N_+        -- sparse edge counter, increments on composite query.
  E[i] = sum_j H[i,j]  -- derived per-atom importance (row-sum); also PageRank.
  cor(E_derived, |W|)  -- LOAD-BEARING fairness check (USER pre-reg < 0.30).
  downscale_gate       -- prunes atoms with E[i] < e_thresh AND
                          max_j H[i,j] < h_thresh (no single edge is load-
                          bearing for this atom).

Brain analog: Govindarajan-Israely-Huang-Tonegawa (2011) clustered synaptic
plasticity -- spines that fire together get co-located and protected jointly
at the dendritic-branch level. Substrate's bound-pair edges = synaptic clusters.

Math analog: Brin-Page (1998) PageRank -- per-node importance as eigenvector of
edge-stochastic matrix; structurally orthogonal to per-node magnitude.

ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class HConfig:
    """Edge-importance tracker hyperparameters.

    increment:   amount added to H[i,j] per composite-query event (default 1.0).
    decay_step:  amount subtracted from H[i,j] per cycle (linear; default 0.0
                 = no decay; > 0 enables forgetting).
    floor:       lower clamp on H[i,j].
    e_thresh:    atom-importance threshold for downscale gate.
    h_thresh:    per-edge load-bearing threshold (atoms with at least one edge
                 H[i,j] >= h_thresh are PROTECTED even when E[i] < e_thresh).
    """
    increment: float = 1.0
    decay_step: float = 0.0
    floor: float = 0.0
    e_thresh: float = 1.0
    h_thresh: float = 2.0


@dataclass
class EdgeImportance:
    """Sparse symmetric edge-importance graph H[i,j] over atom indices.

    Stored as dict[(i,j) -> float] with i < j canonicalization to avoid
    double-counting on the symmetric undirected graph. Materialize to dense
    only when computing row-sum / PageRank.
    """
    n_atoms: int
    cfg: HConfig = field(default_factory=HConfig)
    H: Dict[Tuple[int, int], float] = field(default_factory=dict)

    def _key(self, i: int, j: int) -> Tuple[int, int]:
        if i == j:
            raise ValueError(f"self-loop not allowed: i==j=={i}")
        return (i, j) if i < j else (j, i)

    def increment_pair(self, i: int, j: int) -> None:
        """Increment H[i,j] on a composite-query event involving atoms i,j."""
        if not (0 <= i < self.n_atoms and 0 <= j < self.n_atoms):
            raise ValueError(f"atom index out of range: i={i}, j={j}, n={self.n_atoms}")
        k = self._key(i, j)
        self.H[k] = self.H.get(k, 0.0) + self.cfg.increment

    def increment_query(self, atom_indices: np.ndarray) -> None:
        """Increment H[i,j] for ALL unordered pairs in a composite query.

        atom_indices: 1D int array, all atoms participating in the bound query.
        """
        idx = np.asarray(atom_indices, dtype=np.int64).ravel()
        if idx.size < 2:
            return  # single-atom query: no edge to increment
        for p in range(idx.size):
            for q in range(p + 1, idx.size):
                self.increment_pair(int(idx[p]), int(idx[q]))

    def decay_all(self) -> None:
        """Apply linear decay to all stored edges; drop edges that fall to floor."""
        if self.cfg.decay_step <= 0.0:
            return
        drop_keys = []
        for k, v in self.H.items():
            new_v = v - self.cfg.decay_step
            if new_v <= self.cfg.floor:
                drop_keys.append(k)
            else:
                self.H[k] = new_v
        for k in drop_keys:
            del self.H[k]

    def derive_E_rowsum(self) -> np.ndarray:
        """Derived per-atom importance E[i] = sum_j H[i,j]."""
        E = np.zeros(self.n_atoms, dtype=np.float64)
        for (i, j), v in self.H.items():
            E[i] += v
            E[j] += v
        return E

    def derive_E_pagerank(self, damping: float = 0.85, n_iter: int = 50,
                          tol: float = 1e-6) -> np.ndarray:
        """Derived per-atom importance via PageRank on the H-graph.

        E[i] = (1-d)/N + d * sum_j H[i,j] * E[j] / out_degree(j).
        Structurally orthogonal to |W| because it depends only on H connectivity.
        """
        if not 0.0 < damping < 1.0:
            raise ValueError(f"damping must be in (0,1); got {damping}")
        n = self.n_atoms
        if not self.H:
            return np.full(n, 1.0 / n, dtype=np.float64)
        # Build dense out-degree (symmetric, so degree == row-sum).
        deg = np.zeros(n, dtype=np.float64)
        for (i, j), v in self.H.items():
            deg[i] += v
            deg[j] += v
        # Initialize uniform.
        E = np.full(n, 1.0 / n, dtype=np.float64)
        teleport = (1.0 - damping) / n
        for _it in range(n_iter):
            E_new = np.full(n, teleport, dtype=np.float64)
            for (i, j), v in self.H.items():
                if deg[j] > 0:
                    E_new[i] += damping * v * E[j] / deg[j]
                if deg[i] > 0:
                    E_new[j] += damping * v * E[i] / deg[i]
            if np.max(np.abs(E_new - E)) < tol:
                E = E_new
                break
            E = E_new
        return E

    def max_edge_per_atom(self) -> np.ndarray:
        """For each atom i, return max_j H[i,j] (load-bearing-edge protection)."""
        mx = np.zeros(self.n_atoms, dtype=np.float64)
        for (i, j), v in self.H.items():
            if v > mx[i]:
                mx[i] = v
            if v > mx[j]:
                mx[j] = v
        return mx

    def downscale_mask(self, E_derived: np.ndarray | None = None) -> np.ndarray:
        """Return boolean mask of atoms to downscale.

        Atom i is marked iff E[i] < e_thresh AND max_j H[i,j] < h_thresh.
        Atoms with a single load-bearing edge (max_j H[i,j] >= h_thresh) are
        PROTECTED even if their summed importance is low.
        """
        if E_derived is None:
            E_derived = self.derive_E_rowsum()
        if E_derived.shape[0] != self.n_atoms:
            raise ValueError(f"E shape {E_derived.shape} != n_atoms {self.n_atoms}")
        mx = self.max_edge_per_atom()
        mask = (E_derived < self.cfg.e_thresh) & (mx < self.cfg.h_thresh)
        return mask

    def n_edges(self) -> int:
        return len(self.H)

    def total_mass(self) -> float:
        return float(sum(self.H.values()))


def correlation_E_vs_magnitude(E: np.ndarray, atom_norms: np.ndarray) -> float:
    """Pearson cor(E_derived, |W @ key| or row-norm).

    Load-bearing: USER pre-reg fairness gate < 0.30. If cor >= 0.30, the
    derived importance has inherited the magnitude correlation -- mechanism
    structurally orthogonal failed.
    """
    if E.shape[0] != atom_norms.shape[0]:
        raise ValueError(f"shape mismatch: E={E.shape}, norms={atom_norms.shape}")
    if np.std(E) <= 1e-12 or np.std(atom_norms) <= 1e-12:
        return 0.0
    return float(np.corrcoef(E, atom_norms)[0, 1])


def _selftest_basic() -> bool:
    cfg = HConfig(increment=1.0, e_thresh=2.5, h_thresh=2.0)
    eg = EdgeImportance(n_atoms=8, cfg=cfg)
    assert eg.n_edges() == 0
    assert eg.total_mass() == 0.0

    # Single composite query of 3 atoms -> 3 edges (3 choose 2).
    eg.increment_query(np.array([0, 1, 2]))
    assert eg.n_edges() == 3, f"expected 3 edges, got {eg.n_edges()}"
    assert eg.total_mass() == 3.0

    # Repeat same query -> mass doubles.
    eg.increment_query(np.array([0, 1, 2]))
    assert eg.total_mass() == 6.0

    # Single-atom query -> no-op.
    eg.increment_query(np.array([7]))
    assert eg.n_edges() == 3

    # Symmetry: order independent.
    eg2 = EdgeImportance(n_atoms=4, cfg=cfg)
    eg2.increment_pair(2, 0)
    eg2.increment_pair(0, 2)
    assert eg2.H[(0, 2)] == 2.0
    return True


def _selftest_derive_rowsum() -> bool:
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=4, cfg=cfg)
    eg.increment_query(np.array([0, 1, 2]))  # 3 edges: (0,1)(0,2)(1,2)
    eg.increment_pair(2, 3)
    E = eg.derive_E_rowsum()
    # atom 0: edges to 1,2 -> 2.0
    # atom 1: edges to 0,2 -> 2.0
    # atom 2: edges to 0,1,3 -> 3.0
    # atom 3: edge to 2 -> 1.0
    expected = np.array([2.0, 2.0, 3.0, 1.0])
    assert np.allclose(E, expected), f"E={E} expected {expected}"
    return True


def _selftest_pagerank_convergence() -> bool:
    """PageRank on a small clique converges to uniform; on a star converges
    to center-dominant."""
    cfg = HConfig()
    # Star: 0 in center, edges to 1,2,3
    eg = EdgeImportance(n_atoms=4, cfg=cfg)
    eg.increment_pair(0, 1)
    eg.increment_pair(0, 2)
    eg.increment_pair(0, 3)
    E = eg.derive_E_pagerank()
    # Center should have highest PageRank.
    assert np.argmax(E) == 0, f"PageRank center: argmax should be 0; got E={E}"
    return True


def _selftest_orthogonality_synthetic() -> bool:
    """Construct a case where edge-importance is STRUCTURALLY ORTHOGONAL to
    magnitude: atoms with random |W| but edge-degree correlated with index.
    The Pearson cor should be small."""
    rng = np.random.RandomState(0)
    n = 50
    cfg = HConfig()
    eg = EdgeImportance(n_atoms=n, cfg=cfg)
    # Construct edge graph: clique on first 10 atoms, isolated atoms 10..49.
    for i in range(10):
        for j in range(i + 1, 10):
            eg.increment_pair(i, j)
    E = eg.derive_E_rowsum()
    # Atoms 0..9 have E=9 each; atoms 10..49 have E=0.
    # Construct atom_norms RANDOMLY (independent of edge structure).
    atom_norms = rng.rand(n)
    cor = correlation_E_vs_magnitude(E, atom_norms)
    assert abs(cor) < 0.30, f"orthogonality check: cor={cor:.3f} should be < 0.30"
    return True


def _selftest_downscale_mask() -> bool:
    """downscale_mask: low-E and low-max-edge atoms are masked; load-bearing
    edges protect their atoms."""
    cfg = HConfig(e_thresh=5.0, h_thresh=3.0)
    eg = EdgeImportance(n_atoms=4, cfg=cfg)
    # Atom 0: high E (sum=4 edges of weight 1)... low max (1.0); E<5 AND mx<3 -> MASK
    eg.increment_query(np.array([0, 1, 2, 3]))  # 6 edges all weight 1
    E = eg.derive_E_rowsum()
    # Each atom has E = 3 (degree=3, weight=1 each)
    assert np.allclose(E, [3, 3, 3, 3])
    mx = eg.max_edge_per_atom()
    assert np.allclose(mx, [1, 1, 1, 1])
    # All E<5 AND mx<3 -> all masked
    mask = eg.downscale_mask(E)
    assert np.all(mask), f"all should be masked; got {mask}"

    # Now add a load-bearing edge between atoms 0 and 1
    for _ in range(5):
        eg.increment_pair(0, 1)  # H[0,1] now = 6
    mx2 = eg.max_edge_per_atom()
    assert mx2[0] == 6.0 and mx2[1] == 6.0
    mask2 = eg.downscale_mask()
    # Atoms 0,1 PROTECTED (max-edge >= h_thresh=3); atoms 2,3 still masked
    assert not mask2[0] and not mask2[1]
    assert mask2[2] and mask2[3]
    return True


def _selftest() -> None:
    _selftest_basic()
    _selftest_derive_rowsum()
    _selftest_pagerank_convergence()
    _selftest_orthogonality_synthetic()
    _selftest_downscale_mask()
    print("[edge_importance selftest] PASS  basic+rowsum+pagerank+ortho+mask", flush=True)


if __name__ == "__main__":
    _selftest()
