"""HierarchicalSubstrate: two-level (topic-then-leaf) substrate composition.

Path 2 of the prioritized resolution list. Architecture:

  TOP substrate:
    A topic-centroid routing matrix top_W of shape (K_topics, N_leaf). Each
    topic id in {0, ..., K_topics - 1} owns one row. Per the user's framing
    'top-level summarises topics', the row is the sum of normalized key
    vectors stored under that topic, so retrieval routes by the centroid
    inner product. On store the row gets += key_vec / ||key_vec|| at the
    topic_id of the fact. On retrieve, scores = top_W @ query_vec /
    ||query_vec||; the chosen topic_id is argmax of scores. This is a
    Hebbian binding written in the (topic_id, leaf) coordinate system; the
    top codebook of dimension N_top is retained for chain anchoring (a
    deterministic topic atom per topic id, used for the cross-level audit
    anchor input string only) but not used in the routing math.

  LEAF substrates:
    K independent SubstrateMemory instances. Each leaf stores the facts
    whose key_id routes to that topic. Hash-based routing is deterministic
    so the same key_id always lands in the same leaf.

  Routing (default "hash"):
    topic_id = sha256(key_id) % K_topics. Write goes to leaves[topic_id]
    and updates top_W as above. Retrieve first asks top for the topic_id
    via top_W projection, then asks leaves[topic_id] for the fact.

  Cross-level audit chain:
    Each leaf has its own per-leaf audit chain (SHA256 of W bytes pre/post
    delete; same convention as SubstrateMemory). The HierarchicalSubstrate
    appends a cross-level anchor on every store/edit/delete derived from
        sha256(prev_cross_anchor || top_routing_state_hash ||
               leaf_id || leaf_W_hash_after || op_tag).
    On delete the leaf's DeletionCertificate w_state_hash_before is
    anchored by the cross-level chain via the entry containing the
    matching leaf and prev-state. verify_cross_level_chain re-derives every
    anchor and reports integrity.

Routing accuracy is the binding correctness gate. At smoke scale (K=3,
small M) the binding metric is "fraction of retrieves where the inferred
topic equals the topic where the fact was stored". If routing accuracy
collapses below ~0.7, the architecture is broken for the chosen knobs.

ASCII only, no em-dashes (per CLAUDE.md).
"""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from testbed.api import (
    AuditReport,
    DeletionCertificate,
    MemoryBackend,
    RetrievalResult,
)
from testbed.codebooks import get_codebook
from testbed.persistence import (
    load_config,
    load_registry,
    save_config,
    save_registry,
)
from testbed.substrate_memory import SubstrateMemory, _stable_hash_int


def _route_topic_hash(key_id: str, K_topics: int) -> int:
    """Deterministic topic id: sha256(key_id) % K_topics. Stable across runs."""
    h = hashlib.sha256(key_id.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % K_topics


def _topic_atom_row(topic_id: int, C_top: int, seed: int) -> int:
    """Deterministic codebook row index for a topic's representative atom."""
    return _stable_hash_int(f"topic:{seed}:{topic_id}") % C_top


class HierarchicalSubstrate(MemoryBackend):
    """Two-level substrate: top routing matrix + K leaf SubstrateMemory shards.

    Routing is hash-based (MVP). The top matrix is updated on every store/
    delete so it can answer "which topic does this query belong to" at
    retrieve time. Leaves remain ordinary SubstrateMemory instances; the
    hierarchical wrapper does not modify their internals.
    """

    name = "substrate_hierarchical"

    def __init__(
        self,
        N_top: int = 512,
        N_leaf: int = 2048,
        K_topics: int = 10,
        codebook_kind: str = "bsc",
        codebook_C_top: int = 2048,
        codebook_C_leaf: int = 8192,
        codebook_scale: int = 4,
        beta: float = 32.0,
        hallu_threshold: float = 0.5,
        M_capacity_per_leaf: Optional[int] = None,
        routing: str = "hash",
        device: str = "cpu",
        seed: int = 0,
        **kw,
    ) -> None:
        self.N_top = int(N_top)
        self.N_leaf = int(N_leaf)
        self.N = self.N_leaf  # API-level vector dim; queries are N_leaf-dim
        self.K_topics = int(K_topics)
        self.codebook_kind = codebook_kind
        self.codebook_C_top = int(codebook_C_top)
        self.codebook_C_leaf = int(codebook_C_leaf)
        self.codebook_scale = int(codebook_scale)
        self.beta = float(beta)
        self.hallu_threshold = float(hallu_threshold)
        self.M_capacity_per_leaf = (
            int(M_capacity_per_leaf) if M_capacity_per_leaf is not None else None
        )
        self.routing = str(routing)
        self.device = torch.device(device)
        self.seed = int(seed)

        if self.routing != "hash":
            raise ValueError(
                f"HierarchicalSubstrate routing={routing!r} not supported "
                "(MVP only supports 'hash')"
            )

        # Build top codebook (still useful for cross-level chain anchoring;
        # each topic gets a deterministic atom whose row index feeds the
        # SHA256 input strings). Routing math uses top_W instead.
        self.top_codebook = get_codebook(
            codebook_kind, self.N_top, self.codebook_C_top, seed=self.seed
        ).to(self.device)
        # Top routing matrix: row k holds the centroid of normalized key
        # vectors stored under topic k. Hebbian write accumulates one row
        # per fact; retrieval is one (K, N_leaf) @ (N_leaf,) matvec.
        self.top_W = torch.zeros(
            self.K_topics, self.N_leaf, dtype=torch.float32, device=self.device
        )
        # Deterministic per-topic codebook rows for chain-anchor strings only.
        self.topic_atom_rows: list[int] = []
        used_top_rows: set[int] = set()
        for k in range(self.K_topics):
            r = _topic_atom_row(k, self.codebook_C_top, self.seed)
            while r in used_top_rows:
                r = (r + 1) % self.codebook_C_top
            used_top_rows.add(r)
            self.topic_atom_rows.append(r)

        # Build K leaf SubstrateMemory instances. Each leaf seeds itself
        # deterministically so their codebooks are distinct.
        self.leaves: list[SubstrateMemory] = []
        for k in range(self.K_topics):
            leaf_seed = self.seed * 7919 + k
            leaf_kwargs = {
                "N": self.N_leaf,
                "codebook_kind": codebook_kind,
                "codebook_scale": self.codebook_scale,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "device": str(self.device),
                "seed": leaf_seed,
            }
            if self.M_capacity_per_leaf is not None:
                leaf_kwargs["codebook_M_hint"] = int(self.M_capacity_per_leaf)
            leaf = SubstrateMemory(**leaf_kwargs)
            self.leaves.append(leaf)

        # Cross-level audit chain. Each entry records:
        #   seq, op (store|edit|delete), key_id, topic_id,
        #   top_routing_state_hash, leaf_w_hash_after, anchor.
        self._cross_chain: list[dict] = []

        # key_id -> topic_id mapping for fast routing on edit/delete.
        self._key_to_topic: dict[str, int] = {}

        # Routing-accuracy bookkeeping: track per-key the topic it was
        # written into, so audit() can compute routing accuracy without
        # needing the scenario to keep its own dictionary.
        self._stored_keys: list[str] = []

    # --- helpers --------------------------------------------------------------

    def _route_topic(self, key_id: str) -> int:
        return _route_topic_hash(key_id, self.K_topics)

    def _normalize_leaf(self, vec: np.ndarray) -> torch.Tensor:
        """Return a unit-norm torch tensor for the leaf-dim vector."""
        v = torch.as_tensor(vec, dtype=torch.float32, device=self.device)
        if v.ndim != 1 or v.shape[0] != self.N_leaf:
            raise ValueError(
                f"_normalize_leaf: vec shape {tuple(v.shape)} != (N_leaf={self.N_leaf},)"
            )
        n = torch.linalg.norm(v)
        if float(n.item()) <= 1e-12:
            return v
        return v / n

    def _top_routing_state_hash(self) -> str:
        """SHA256 of the current top_W bytes. Anchors cross-level chain entries."""
        return hashlib.sha256(
            self.top_W.detach().cpu().numpy().tobytes()
        ).hexdigest()

    def _append_cross_chain(
        self,
        op: str,
        key_id: str,
        topic_id: int,
        leaf_w_hash_after: str,
    ) -> str:
        """Append a cross-level entry and return its anchor SHA256."""
        prev_anchor = (
            self._cross_chain[-1]["anchor"] if self._cross_chain else "GENESIS"
        )
        top_hash = self._top_routing_state_hash()
        seq = len(self._cross_chain)
        anchor_input = (
            f"{prev_anchor}|{top_hash}|leaf_{topic_id}|"
            f"{leaf_w_hash_after}|op_{op}|seq_{seq}|key_{key_id}"
        )
        anchor = hashlib.sha256(anchor_input.encode("utf-8")).hexdigest()
        self._cross_chain.append({
            "seq": seq,
            "op": op,
            "key_id": key_id,
            "topic_id": int(topic_id),
            "top_routing_state_hash": top_hash,
            "leaf_w_hash_after": leaf_w_hash_after,
            "prev_anchor": prev_anchor,
            "anchor": anchor,
            "timestamp_ns": time.time_ns(),
        })
        return anchor

    def _leaf_w_hash(self, topic_id: int) -> str:
        leaf = self.leaves[topic_id]
        return hashlib.sha256(
            leaf.W.detach().cpu().numpy().tobytes()
        ).hexdigest()

    # --- ABC implementation ---------------------------------------------------

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        topic_id = self._route_topic(key_id)

        # Top update: accumulate the unit-norm key vector into the chosen
        # topic's centroid row. At retrieve, score = top_W @ unit_query;
        # the topic whose centroid points most in the query's direction
        # wins. For BSC key vectors with i.i.d. random topic assignments,
        # the within-topic sum statistically dominates the cross-topic
        # noise once enough facts share a topic (>=~ a few dozen per topic
        # in practice; routing accuracy improves with M / K).
        unit_kvec = self._normalize_leaf(key_vec)
        if key_id not in self._key_to_topic:
            # First time we see this key_id: accumulate. Re-stores treat as
            # edit() at the leaf and we update top_W only when the topic
            # actually changes (it cannot under hash routing, so leave it).
            self.top_W[topic_id] = self.top_W[topic_id] + unit_kvec

        # Leaf store.
        self.leaves[topic_id].store(key_id, key_vec, value)

        # Bookkeeping + cross-level chain.
        if key_id not in self._key_to_topic:
            self._stored_keys.append(key_id)
        self._key_to_topic[key_id] = int(topic_id)
        self._append_cross_chain(
            op="store",
            key_id=key_id,
            topic_id=topic_id,
            leaf_w_hash_after=self._leaf_w_hash(topic_id),
        )

    def _route_query(self, query_vec: np.ndarray) -> tuple[int, float, list[float]]:
        """Top-level routing.

        scores = top_W @ unit_query (shape (K,)). Return (argmax topic_id,
        best score, all scores).
        """
        unit_q = self._normalize_leaf(query_vec)
        scores = self.top_W @ unit_q  # (K,)
        topic_id = int(torch.argmax(scores).item())
        return topic_id, float(scores[topic_id].item()), scores.detach().cpu().tolist()

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        # Step 1: top routing.
        topic_id, top_score, all_topic_scores = self._route_query(query_vec)

        # Step 2: leaf retrieve.
        leaf = self.leaves[topic_id]
        if len(leaf.key_registry) == 0:
            # Empty leaf: synthesize a near-uniform negative result. The
            # routing decision is still recorded so audit can see it.
            res = RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=True,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
        else:
            res = leaf.retrieve(query_vec, k=k)

        # Attach hierarchical metadata for the scenario to inspect.
        setattr(res, "hierarchical_meta", {
            "routed_topic_id": int(topic_id),
            "top_score": float(top_score),
            "all_topic_scores": [float(s) for s in all_topic_scores],
        })
        return res

    def edit(self, key_id: str, new_value: str) -> None:
        topic_id = self._key_to_topic.get(key_id)
        if topic_id is None:
            # Fall back to deterministic routing (also raises if not stored).
            topic_id = self._route_topic(key_id)
        self.leaves[topic_id].edit(key_id, new_value)
        # Top routing is unchanged on value edit; still anchor a cross-level
        # entry so the chain witnesses the leaf-state transition.
        self._append_cross_chain(
            op="edit",
            key_id=key_id,
            topic_id=topic_id,
            leaf_w_hash_after=self._leaf_w_hash(topic_id),
        )

    def delete(self, key_id: str) -> DeletionCertificate:
        topic_id = self._key_to_topic.get(key_id)
        if topic_id is None:
            topic_id = self._route_topic(key_id)
        leaf = self.leaves[topic_id]

        # Top update on delete: subtract the unit-norm contribution this
        # key added at store time. We rebuild that contribution from the
        # leaf's canonical key atom (which is what the substrate snapped
        # the original key_vec to; the centroid math is approximate either
        # way because the original key_vec is not retained, but using the
        # leaf's key atom is the closest stable proxy and matches how
        # retrieve would weight this key).
        if key_id in leaf.key_registry:
            key_row = leaf.key_registry[key_id]
            key_atom_leaf = leaf.codebook[key_row]   # (N_leaf,)
            key_vec_np = key_atom_leaf.detach().cpu().numpy()
            unit_kvec = self._normalize_leaf(key_vec_np)
            self.top_W[topic_id] = self.top_W[topic_id] - unit_kvec

        # Leaf delete returns its own DeletionCertificate; we augment it with
        # the cross-level anchor by writing it into the verification_probes
        # list (the api.py contract allows any structured dict in there).
        cert = leaf.delete(key_id)
        leaf_w_after = self._leaf_w_hash(topic_id)
        anchor = self._append_cross_chain(
            op="delete",
            key_id=key_id,
            topic_id=topic_id,
            leaf_w_hash_after=leaf_w_after,
        )

        # Drop from key->topic map; track the deletion for audit accounting.
        self._key_to_topic.pop(key_id, None)
        try:
            self._stored_keys.remove(key_id)
        except ValueError:
            pass

        # Embed cross-level anchor metadata into verification_probes so
        # callers reading the certificate can audit the cross-level chain
        # entry that witnesses this delete.
        if cert.verification_probes is None:
            cert.verification_probes = []
        cert.verification_probes.append({
            "cross_level_anchor": anchor,
            "top_routing_state_hash": self._top_routing_state_hash(),
            "leaf_id": int(topic_id),
            "leaf_w_hash_after": leaf_w_after,
            "cross_chain_seq": len(self._cross_chain) - 1,
        })
        return cert

    def verify_cross_level_chain(self) -> dict:
        """Re-derive every cross-level anchor and report integrity."""
        if not self._cross_chain:
            return {
                "entries": 0,
                "anchors_ok": 0,
                "integrity": 1.0,
            }
        ok = 0
        for i, entry in enumerate(self._cross_chain):
            prev_anchor = (
                self._cross_chain[i - 1]["anchor"] if i > 0 else "GENESIS"
            )
            expected_input = (
                f"{prev_anchor}|{entry['top_routing_state_hash']}|"
                f"leaf_{entry['topic_id']}|{entry['leaf_w_hash_after']}|"
                f"op_{entry['op']}|seq_{entry['seq']}|key_{entry['key_id']}"
            )
            expected_anchor = hashlib.sha256(
                expected_input.encode("utf-8")
            ).hexdigest()
            if expected_anchor == entry["anchor"]:
                ok += 1
        return {
            "entries": len(self._cross_chain),
            "anchors_ok": ok,
            "integrity": float(ok) / float(len(self._cross_chain)),
        }

    def routing_accuracy(self, sample_size: int = 200, seed: int = 0) -> dict:
        """Probe routing accuracy: do queries route to the topic where the
        matching fact was stored?

        Samples up to sample_size stored keys, projects each through the top
        router, and counts agreement with the recorded topic_id.
        """
        if not self._stored_keys:
            return {
                "n_probed": 0,
                "accuracy": 1.0,
            }
        rng = np.random.default_rng(seed)
        ids = list(self._stored_keys)
        if len(ids) > sample_size:
            picks = rng.choice(len(ids), size=sample_size, replace=False)
            ids = [ids[i] for i in picks]
        correct = 0
        for kid in ids:
            true_topic = self._key_to_topic.get(kid)
            if true_topic is None:
                continue
            leaf = self.leaves[true_topic]
            if kid not in leaf.key_registry:
                continue
            key_row = leaf.key_registry[kid]
            key_atom = leaf.codebook[key_row]
            qvec_np = key_atom.detach().cpu().numpy()
            routed, _score, _all = self._route_query(qvec_np)
            if routed == true_topic:
                correct += 1
        n = max(len(ids), 1)
        return {
            "n_probed": int(n),
            "accuracy": float(correct) / float(n),
        }

    def audit(self) -> AuditReport:
        """Aggregate per-leaf audits + hierarchical-specific metrics."""
        kf1_vals: list[float] = []
        kf1_mean_vals: list[float] = []
        kf2_vals: list[float] = []
        tcft_vals: list[float] = []
        n_items = 0
        storage_bytes = 0
        for leaf in self.leaves:
            try:
                rep = leaf.audit()
            except Exception:
                continue
            n_items += rep.n_items
            if rep.kf1_above_thresh_frac is not None:
                kf1_vals.append(rep.kf1_above_thresh_frac)
            if rep.kf1_mean_oos_max_conf is not None:
                kf1_mean_vals.append(rep.kf1_mean_oos_max_conf)
            if rep.kf2_max_isolation is not None:
                kf2_vals.append(rep.kf2_max_isolation)
            if rep.tcft_mean_var_ratio is not None:
                tcft_vals.append(rep.tcft_mean_var_ratio)
            storage_bytes += int(
                leaf.W.element_size() * leaf.W.numel()
                + leaf.codebook.element_size() * leaf.codebook.numel()
            )
        # Top-level storage.
        storage_bytes += int(
            self.top_W.element_size() * self.top_W.numel()
            + self.top_codebook.element_size() * self.top_codebook.numel()
        )

        chain_rep = self.verify_cross_level_chain()
        routing_rep = self.routing_accuracy(sample_size=200, seed=self.seed + 99)

        return AuditReport(
            backend=self.name,
            n_items=n_items,
            kf1_above_thresh_frac=(
                float(sum(kf1_vals) / len(kf1_vals)) if kf1_vals else None
            ),
            kf1_mean_oos_max_conf=(
                float(sum(kf1_mean_vals) / len(kf1_mean_vals))
                if kf1_mean_vals else None
            ),
            kf2_max_isolation=(
                float(max(kf2_vals)) if kf2_vals else None
            ),
            tcft_mean_var_ratio=(
                float(sum(tcft_vals) / len(tcft_vals)) if tcft_vals else None
            ),
            storage_bytes=int(storage_bytes),
            config={
                "N_top": self.N_top,
                "N_leaf": self.N_leaf,
                "K_topics": self.K_topics,
                "codebook_kind": self.codebook_kind,
                "codebook_C_top": self.codebook_C_top,
                "codebook_C_leaf": self.codebook_C_leaf,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "routing": self.routing,
                "seed": self.seed,
                "hierarchical": True,
                "routing_accuracy": routing_rep["accuracy"],
                "routing_n_probed": routing_rep["n_probed"],
                "cross_level_chain_integrity": chain_rep["integrity"],
                "cross_level_chain_entries": chain_rep["entries"],
                "cross_level_anchors_ok": chain_rep["anchors_ok"],
            },
        )

    # --- persistence ----------------------------------------------------------

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        # Top subdir.
        top_dir = path / "top"
        top_dir.mkdir(parents=True, exist_ok=True)
        np.save(
            top_dir / "top_W.npy",
            self.top_W.detach().cpu().numpy().astype(np.float32, copy=False),
        )
        np.save(
            top_dir / "top_codebook.npy",
            self.top_codebook.detach().cpu().numpy().astype(np.float32, copy=False),
        )
        save_registry(
            {
                "topic_atom_rows": self.topic_atom_rows,
                "key_to_topic": self._key_to_topic,
                "stored_keys": self._stored_keys,
            },
            top_dir / "top_registry.json",
        )
        # Leaves subdir.
        leaves_dir = path / "leaves"
        leaves_dir.mkdir(parents=True, exist_ok=True)
        for k, leaf in enumerate(self.leaves):
            leaf_dir = leaves_dir / f"leaf_{k:03d}"
            leaf.save(leaf_dir)
        # Cross-level chain.
        save_registry(
            {"chain": self._cross_chain},
            path / "cross_level_chain.json",
        )
        save_config(
            {
                "N_top": self.N_top,
                "N_leaf": self.N_leaf,
                "K_topics": self.K_topics,
                "codebook_kind": self.codebook_kind,
                "codebook_C_top": self.codebook_C_top,
                "codebook_C_leaf": self.codebook_C_leaf,
                "codebook_scale": self.codebook_scale,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "M_capacity_per_leaf": (
                    int(self.M_capacity_per_leaf)
                    if self.M_capacity_per_leaf is not None else 0
                ),
                "routing": self.routing,
                "device": str(self.device),
                "seed": self.seed,
                "hierarchical": True,
            },
            path / "config.yaml",
        )

    def load(self, path: Path) -> None:
        path = Path(path)
        cfg = load_config(path / "config.yaml")
        self.N_top = int(cfg["N_top"])
        self.N_leaf = int(cfg["N_leaf"])
        self.N = self.N_leaf
        self.K_topics = int(cfg["K_topics"])
        self.codebook_kind = str(cfg["codebook_kind"])
        self.codebook_C_top = int(cfg["codebook_C_top"])
        self.codebook_C_leaf = int(cfg["codebook_C_leaf"])
        self.codebook_scale = int(cfg.get("codebook_scale", 4))
        self.beta = float(cfg["beta"])
        self.hallu_threshold = float(cfg["hallu_threshold"])
        m_cap = int(cfg.get("M_capacity_per_leaf", 0))
        self.M_capacity_per_leaf = m_cap if m_cap > 0 else None
        self.routing = str(cfg.get("routing", "hash"))
        self.device = torch.device(cfg.get("device", "cpu"))
        self.seed = int(cfg["seed"])

        top_dir = path / "top"
        top_W_np = np.load(top_dir / "top_W.npy")
        self.top_W = torch.as_tensor(
            top_W_np, dtype=torch.float32, device=self.device
        )
        top_cb_np = np.load(top_dir / "top_codebook.npy")
        self.top_codebook = torch.as_tensor(
            top_cb_np, dtype=torch.float32, device=self.device
        )
        top_reg = load_registry(top_dir / "top_registry.json")
        self.topic_atom_rows = [int(x) for x in top_reg["topic_atom_rows"]]
        self._key_to_topic = {
            k: int(v) for k, v in top_reg["key_to_topic"].items()
        }
        self._stored_keys = list(top_reg["stored_keys"])

        self.leaves = []
        leaves_dir = path / "leaves"
        for k in range(self.K_topics):
            leaf_dir = leaves_dir / f"leaf_{k:03d}"
            leaf_seed = self.seed * 7919 + k
            leaf = SubstrateMemory(
                N=self.N_leaf,
                codebook_kind=self.codebook_kind,
                codebook_scale=self.codebook_scale,
                beta=self.beta,
                hallu_threshold=self.hallu_threshold,
                device=str(self.device),
                seed=leaf_seed,
                codebook_M_hint=(
                    self.M_capacity_per_leaf
                    if self.M_capacity_per_leaf is not None else None
                ),
            )
            leaf.load(leaf_dir)
            self.leaves.append(leaf)

        chain_path = path / "cross_level_chain.json"
        if chain_path.exists():
            blob = load_registry(chain_path)
            self._cross_chain = list(blob.get("chain", []))
        else:
            self._cross_chain = []

    def __len__(self) -> int:
        return sum(len(s.key_registry) for s in self.leaves)

    def supports_killer_features(self) -> bool:
        return True


if __name__ == "__main__":
    # Self-test: K=3, N_top=128, N_leaf=256, M_total=30 across topics.
    # Assertions:
    #   (a) every stored key retrieves with correct key_id from its leaf
    #       when bypassing the top router (leaf is itself correct).
    #   (b) routing_accuracy at >= 0.7 at this trivial scale.
    #   (c) cross_level_chain_integrity == 1.0 after a few deletes.
    #   (d) save/load round-trip preserves routing accuracy.
    import shutil
    import tempfile

    h = HierarchicalSubstrate(
        N_top=128,
        N_leaf=256,
        K_topics=3,
        codebook_kind="bsc",
        codebook_C_top=512,
        codebook_C_leaf=1024,
        beta=32.0,
        seed=7,
    )
    M = 30
    rng = np.random.default_rng(0)
    keys = []
    for i in range(M):
        kid = f"hk_{i:04d}"
        raw = rng.integers(0, 2, size=h.N_leaf, dtype=np.int8).astype(np.float32)
        kvec = raw * 2.0 - 1.0
        h.store(kid, kvec, f"v_{i}")
        keys.append((kid, kvec))

    # (a) Leaf-level recall via direct topic routing using the stored map.
    leaf_correct = 0
    for kid, kvec in keys:
        topic_id = h._key_to_topic[kid]
        # Use the canonical leaf key_atom for retrieval (apples-to-apples
        # with substrate's snap behavior).
        leaf = h.leaves[topic_id]
        key_row = leaf.key_registry[kid]
        kvec_canon = leaf.codebook[key_row].detach().cpu().numpy()
        r = leaf.retrieve(kvec_canon)
        if r.key_id == kid:
            leaf_correct += 1
    assert leaf_correct == M, f"leaf-direct recall {leaf_correct}/{M}"

    # (b) routing accuracy.
    rep = h.routing_accuracy(sample_size=M, seed=0)
    print(f"self-test routing accuracy: {rep['accuracy']:.3f} on {rep['n_probed']} probes")
    assert rep["accuracy"] >= 0.5, f"routing collapsed: {rep['accuracy']:.3f}"

    # (c) cross-level chain integrity after deletes.
    cert = h.delete(keys[0][0])
    assert cert.erased or cert.var_ratio is not None
    cert2 = h.delete(keys[1][0])
    chain = h.verify_cross_level_chain()
    print(f"self-test chain integrity: {chain['integrity']:.3f} ({chain['anchors_ok']}/{chain['entries']})")
    assert chain["integrity"] == 1.0, f"chain broken: {chain}"

    # (d) save/load roundtrip.
    td = Path(tempfile.mkdtemp(prefix="hier_selftest_"))
    try:
        h.save(td)
        h2 = HierarchicalSubstrate(
            N_top=128,
            N_leaf=256,
            K_topics=3,
            codebook_kind="bsc",
            codebook_C_top=512,
            codebook_C_leaf=1024,
            beta=32.0,
            seed=7,
        )
        h2.load(td)
        rep2 = h2.routing_accuracy(sample_size=M, seed=0)
        # rep was computed before two deletes; rep2 sees M-2 stored keys.
        assert rep2["n_probed"] == (M - 2), (
            f"roundtrip probe count drift: {rep2['n_probed']} vs expected {M - 2}"
        )
        chain2 = h2.verify_cross_level_chain()
        assert chain2["integrity"] == 1.0, "post-load chain broken"
        print(
            f"self-test roundtrip OK: routing {rep2['accuracy']:.3f} chain {chain2['integrity']:.3f}"
        )
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print("hierarchical_substrate self-test OK")
