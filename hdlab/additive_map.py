"""AdditiveKGMap: the additive inductive map-builder promoted to a maintained, persistent live substrate capability.

A COEXISTING second memory mode (CLS cortical-schema analog) alongside the multiplicative KGStore -- it touches
NOTHING KGStore/CERT-584/585 multi-hop depends on. Owns entity coordinates X [N,k] (structure-derived, low-dim),
relation displacements D [n_rel,k] (relations = directions), and the two index maps. Readout is closed-form
Euclidean distance; the compose op is a zero-training degree-invariant arithmetic mean of per-edge tail estimates.

Provenance (VET-confirmed FULL, held-out-ENTITY MRR 0.1282, HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE):
  - fit           : experiments/_kge_anchor1_fit.py::fit_kge_anchor1 (imported by the default coord source; single
                    source of truth for the 150-line SGD recipe incl. checkpoint/neg-chunk/reciprocal levers).
  - score readout : experiments/_course_c_rotate_core_v1.py::additive_direct_scores (copied verbatim below; small,
                    keeps this live module free of that helper's heavy import chain).
  - compose op    : experiments/exp_anchor_compose_inductive_entity_cskg_v1.py::build_anchor_compose_codes (copied
                    verbatim below; the only genuinely novel op with no analog in KGStore).

COORD-SOURCE SEAM: the entity-coordinate SOURCE is a swappable component (CoordinateSource). LearnedSGDCoordinateSource
(default) fits X,D by Adam SGD. A future closed-form / rule-derived / structured-code source is a drop-in that reuses
the SAME compose/score/persist/API without touching this class. The learned source imports the experiments recipe
LAZILY (inside fit) so importing this module never requires experiments/ to be importable and a rule-derived source
carries zero experiments coupling.

ASCII-only. No emojis. Explicit dtypes (float32). torch.Generator seeded. Terse.
"""

import json
import os
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import torch

SCORE_CHUNK = 256
FORMAT_VERSION = 1
LabelTriple = Tuple[str, str, str]
IndexSpace = Union[Dict[str, int], Sequence[str], None]


# ---------------------------------------------------------------------------
# Coord-source seam. Default = learned SGD; swap for a rule-derived source without touching AdditiveKGMap.
# ---------------------------------------------------------------------------

class CoordinateSource:
    """Interface: produce entity coords X [N,k] and relation displacements D [n_rel,k] from int triples."""

    name: str = "abstract"

    def fit(self, train_int: np.ndarray, n_ent: int, n_rel: int, k: int,
            device: torch.device, seed: int, epochs: int, **kwargs) -> Tuple[torch.Tensor, torch.Tensor]:
        """train_int: (E,3) int64 [h,r,t]. Returns (X [n_ent,k] float32, D [n_rel,k] float32) on device."""
        raise NotImplementedError


class LearnedSGDCoordinateSource(CoordinateSource):
    """Default coord source: Adam-SGD self-adversarial-CE + N3 + reciprocal fit (experiments/_kge_anchor1_fit)."""

    name = "learned_sgd_kge_anchor1"

    def fit(self, train_int: np.ndarray, n_ent: int, n_rel: int, k: int,
            device: torch.device, seed: int, epochs: int, **kwargs) -> Tuple[torch.Tensor, torch.Tensor]:
        """Lazy import keeps this module load-light + decoupled; a rule-derived source needs zero experiments dep."""
        from experiments._kge_anchor1_fit import fit_kge_anchor1  # noqa: E402
        X, D = fit_kge_anchor1(train_int, n_ent, n_rel, k, device, seed, epochs, **kwargs)
        return X.to(torch.float32), D.to(torch.float32)


# ---------------------------------------------------------------------------
# Proven primitives copied VERBATIM (see module provenance). Kept in-module to avoid the experiments import chain.
# ---------------------------------------------------------------------------

def additive_direct_scores(X: torch.Tensor, D: torch.Tensor, hold_edges: np.ndarray,
                           device: torch.device, chunk: int = SCORE_CHUNK) -> torch.Tensor:
    """Native additive (TransE) readout: score(t) = -||X_h + D_r - X_t||. Query-chunked. Returns (nq,N) CPU float32.

    VERBATIM from experiments/_course_c_rotate_core_v1.py::additive_direct_scores."""
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    pred = X[h] + D[r]                                              # (nq,k)
    Xsq = (X * X).sum(dim=1)                                        # (N,)
    nq = pred.shape[0]; n_ent = X.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    XT = X.T                                                        # (k,N)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        pc = pred[s:e]                                              # (b,k)
        d2 = (pc * pc).sum(dim=1, keepdim=True) + Xsq.unsqueeze(0) - 2.0 * (pc @ XT)
        sc = -torch.sqrt(torch.clamp(d2, min=0.0))                 # (b,N), higher=better
        out[s:e] = sc.detach().to("cpu")
        del pc, d2, sc
    del XT
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def build_anchor_compose_codes(X: torch.Tensor, D: torch.Tensor, support_int: np.ndarray,
                               device: torch.device,
                               rel_perm: Optional[np.ndarray] = None) -> Tuple[torch.Tensor, np.ndarray]:
    """Zero-training degree-invariant bundle: patched-row t = mean_i(X[h_i]+D[r_i]) over t's support edges.

    Returns (patched entity table Xp [N,k], support_deg [N]). VERBATIM from
    experiments/exp_anchor_compose_inductive_entity_cskg_v1.py::build_anchor_compose_codes."""
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    h = torch.from_numpy(support_int[:, 0]).long().to(device)
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]                       # scramble: map each support relation id -> a shuffled id
    r = torch.from_numpy(r_np).long().to(device)
    t = torch.from_numpy(support_int[:, 2]).long().to(device)
    est = X[h] + D[r]                               # (S,k) per-edge TransE tail estimate
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, t, est)                       # sum of estimates per tail
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, t, torch.ones(t.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)   # MEAN = degree-invariant bundle
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


# ---------------------------------------------------------------------------
# The live capability.
# ---------------------------------------------------------------------------

class AdditiveKGMap:
    """Persistent additive inductive map: fit -> compose_entity -> insert_entity -> score_all, save/load."""

    def __init__(self, coord_source: Optional[CoordinateSource] = None,
                 device: Union[str, torch.device] = "cpu") -> None:
        """coord_source defaults to LearnedSGDCoordinateSource (swappable seam)."""
        self.coord_source: CoordinateSource = coord_source or LearnedSGDCoordinateSource()
        self.device: torch.device = torch.device(device) if isinstance(device, str) else device
        self.X: Optional[torch.Tensor] = None            # (N,k) float32
        self.D: Optional[torch.Tensor] = None            # (n_rel,k) float32
        self.entity_to_idx: Dict[str, int] = {}
        self.relation_to_idx: Dict[str, int] = {}
        self.k: int = 0
        self.meta: Dict[str, object] = {}

    # ---- properties -------------------------------------------------------
    @property
    def num_entities(self) -> int:
        """Row count of X (index universe, includes reserved/composed rows)."""
        return 0 if self.X is None else int(self.X.shape[0])

    @property
    def num_relations(self) -> int:
        """Row count of D."""
        return 0 if self.D is None else int(self.D.shape[0])

    # ---- index helpers ----------------------------------------------------
    @staticmethod
    def _to_index_map(space: IndexSpace, labels_in_order: List[str]) -> Dict[str, int]:
        """Pin an index space: dict passes through; sequence enumerates; None -> sorted(labels) for determinism."""
        if isinstance(space, dict):
            return dict(space)
        if space is not None:
            return {str(lbl): i for i, lbl in enumerate(space)}
        return {lbl: i for i, lbl in enumerate(sorted(set(labels_in_order)))}

    def _eidx(self, entity: Union[str, int]) -> int:
        """Resolve an entity label (or pass through an int index)."""
        if isinstance(entity, (int, np.integer)):
            return int(entity)
        if entity not in self.entity_to_idx:
            raise KeyError("unknown entity label: %r" % entity)
        return self.entity_to_idx[entity]

    def _ridx(self, relation: Union[str, int]) -> int:
        """Resolve a relation label (or pass through an int index)."""
        if isinstance(relation, (int, np.integer)):
            return int(relation)
        if relation not in self.relation_to_idx:
            raise KeyError("unknown relation label: %r" % relation)
        return self.relation_to_idx[relation]

    # ---- fit (map-builder) ------------------------------------------------
    def fit(self, train_triples: Sequence[LabelTriple], *, entities: IndexSpace = None,
            relations: IndexSpace = None, k: int = 24, epochs: int = 500, seed: int = 7,
            **coord_kwargs) -> "AdditiveKGMap":
        """Fit X,D on label triples via the coord source. entities/relations pin the index universe (reserve rows
        for held-out entities scored/composed later); None derives a sorted-deterministic map from the triples."""
        heads = [str(h) for (h, _r, _t) in train_triples]
        tails = [str(t) for (_h, _r, t) in train_triples]
        rels = [str(r) for (_h, r, _t) in train_triples]
        self.entity_to_idx = self._to_index_map(entities, heads + tails)
        self.relation_to_idx = self._to_index_map(relations, rels)
        n_ent = len(self.entity_to_idx)
        n_rel = len(self.relation_to_idx)
        train_int = np.array([[self.entity_to_idx[str(h)], self.relation_to_idx[str(r)],
                               self.entity_to_idx[str(t)]] for (h, r, t) in train_triples], dtype=np.int64)
        X, D = self.coord_source.fit(train_int, n_ent, n_rel, k, self.device, seed, epochs, **coord_kwargs)
        self.X = X.to(self.device, torch.float32)
        self.D = D.to(self.device, torch.float32)
        self.k = int(self.X.shape[1])
        self.meta = dict(coord_source=self.coord_source.name, k=self.k, epochs=int(epochs), seed=int(seed),
                         n_train_edges=int(train_int.shape[0]), n_ent=n_ent, n_rel=n_rel,
                         coord_kwargs={kk: (vv if isinstance(vv, (int, float, str, bool)) else str(vv))
                                       for kk, vv in coord_kwargs.items()})
        return self

    def set_coords(self, X: torch.Tensor, D: torch.Tensor, entity_to_idx: Dict[str, int],
                   relation_to_idx: Dict[str, int]) -> "AdditiveKGMap":
        """Inject pre-fit coordinates (e.g. from a persisted fit or an alternate coord source) without re-fitting."""
        self.X = X.to(self.device, torch.float32)
        self.D = D.to(self.device, torch.float32)
        self.entity_to_idx = dict(entity_to_idx)
        self.relation_to_idx = dict(relation_to_idx)
        self.k = int(self.X.shape[1])
        return self

    # ---- query-time API ---------------------------------------------------
    def compose_entity(self, support_edges: Sequence[Tuple[Union[str, int], Union[str, int]]]) -> torch.Tensor:
        """Zero-training code for a novel entity from its support edges: mean_i(X[h_i]+D[r_i]). Returns (k,) float32.

        support_edges: iterable of (anchor_head, relation) reaching the novel entity. Unknown labels are skipped."""
        if self.X is None or self.D is None:
            raise RuntimeError("map is not fit; call fit() or load()/set_coords() first")
        hs, rs = [], []
        for h, r in support_edges:
            try:
                hs.append(self._eidx(h)); rs.append(self._ridx(r))
            except KeyError:
                continue
        if not hs:
            raise ValueError("no valid support edges (all anchor/relation labels unknown)")
        h = torch.tensor(hs, dtype=torch.long, device=self.device)
        r = torch.tensor(rs, dtype=torch.long, device=self.device)
        est = self.X[h] + self.D[r]                      # (S,k) per-edge tail estimate
        return est.mean(dim=0).detach()                  # (k,) degree-invariant bundle

    def insert_entity(self, code: torch.Tensor, name: Optional[str] = None) -> int:
        """Append a coordinate row to X (trivial [N,k] cat -- no fixed-codebook limit). Returns the new row index."""
        if self.X is None:
            raise RuntimeError("map is not fit; call fit() or load()/set_coords() first")
        row = code.detach().to(self.device, torch.float32).reshape(1, -1)
        if row.shape[1] != self.X.shape[1]:
            raise ValueError("code dim %d != map k %d" % (row.shape[1], self.X.shape[1]))
        self.X = torch.cat([self.X, row], dim=0)
        new_idx = int(self.X.shape[0] - 1)
        if name is not None:
            self.entity_to_idx[str(name)] = new_idx
        return new_idx

    def score_all(self, head: Union[str, int], relation: Union[str, int]) -> torch.Tensor:
        """Direct-distance ranking of every candidate tail for (head, relation): score(t) = -||X_h+D_r-X_t||. (N,)."""
        edges = np.array([[self._eidx(head), self._ridx(relation), 0]], dtype=np.int64)
        return self.score_edges(edges)[0]

    def score_edges(self, edges_int: np.ndarray) -> torch.Tensor:
        """Batched direct-distance readout over query edges (nq,3) [h,r,*]. Returns (nq,N) CPU float32."""
        if self.X is None or self.D is None:
            raise RuntimeError("map is not fit; call fit() or load()/set_coords() first")
        return additive_direct_scores(self.X, self.D, edges_int, self.device)

    def compose_into_table(self, support_int: np.ndarray,
                           rel_perm: Optional[np.ndarray] = None) -> Tuple[torch.Tensor, np.ndarray]:
        """Bulk zero-training compose: patched X table with each held-out row replaced by its support-edge bundle.

        Reuses the verbatim novel op; used for bulk induction + acceptance-gate reproduction. rel_perm scrambles
        the support relation ids (the must-fail control). Returns (Xp [N,k], support_deg [N])."""
        if self.X is None or self.D is None:
            raise RuntimeError("map is not fit; call fit() or load()/set_coords() first")
        return build_anchor_compose_codes(self.X, self.D, support_int, self.device, rel_perm=rel_perm)

    # ---- persistence (the load-bearing gap) -------------------------------
    def save(self, path: Union[str, os.PathLike]) -> str:
        """Persist X,D (safetensors) + index maps + meta (json) to a directory. Returns the directory path."""
        if self.X is None or self.D is None:
            raise RuntimeError("nothing to save; map is not fit")
        from safetensors.torch import save_file  # local import; keeps module import light
        d = str(path)
        os.makedirs(d, exist_ok=True)
        coords_tmp = os.path.join(d, "coords.safetensors.tmp")
        coords = os.path.join(d, "coords.safetensors")
        save_file({"X": self.X.detach().cpu().contiguous().to(torch.float32),
                   "D": self.D.detach().cpu().contiguous().to(torch.float32)}, coords_tmp)
        os.replace(coords_tmp, coords)
        index = dict(format_version=FORMAT_VERSION, k=self.k, coord_source=self.coord_source.name,
                     entity_to_idx=self.entity_to_idx, relation_to_idx=self.relation_to_idx, meta=self.meta)
        idx_tmp = os.path.join(d, "index.json.tmp")
        idx = os.path.join(d, "index.json")
        with open(idx_tmp, "w", encoding="utf-8") as f:
            json.dump(index, f)
        os.replace(idx_tmp, idx)
        return d

    @classmethod
    def load(cls, path: Union[str, os.PathLike], device: Union[str, torch.device] = "cpu",
             coord_source: Optional[CoordinateSource] = None) -> "AdditiveKGMap":
        """Load a persisted map (no re-fit). coord_source only matters for a subsequent fit()/re-fit."""
        from safetensors.torch import load_file  # local import; keeps module import light
        d = str(path)
        with open(os.path.join(d, "index.json"), "r", encoding="utf-8") as f:
            index = json.load(f)
        tensors = load_file(os.path.join(d, "coords.safetensors"))
        obj = cls(coord_source=coord_source, device=device)
        obj.X = tensors["X"].to(obj.device, torch.float32)
        obj.D = tensors["D"].to(obj.device, torch.float32)
        obj.entity_to_idx = {str(kk): int(vv) for kk, vv in index["entity_to_idx"].items()}
        obj.relation_to_idx = {str(kk): int(vv) for kk, vv in index["relation_to_idx"].items()}
        obj.k = int(index.get("k", obj.X.shape[1]))
        obj.meta = index.get("meta", {})
        return obj
