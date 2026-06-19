"""Substrate sharded variant: K independent SubstrateMemory instances at fixed C.

Hypothesis (locked 2026-05-29): sharding the substrate across K shards at a
FIXED codebook_C preserves the per-shard recall window (M_per_shard <= C/4)
while extending the operating envelope to M_total = K * (C/4). Killer features
remain per-shard intact. The cross-shard audit chain is built by anchoring
each per-shard deletion certificate into a global sequence and appending a
shard-transition hash whenever consecutive deletes cross shard boundaries.

Routing: hash(key_id) % K_shards. Deterministic; no learning state.

Shared codebook: when shared_codebook=True (default), a single (C, N) torch
tensor is built once and the SAME REFERENCE is handed to each shard. Memory
savings: one C*N codebook plus K * N*N W matrices vs. K * (C*N + N*N) for
the independent case. At C=8192, N=2048, K=10: 1*8192*2048*4 = 64 MB shared
vs. K=10 * (64 + 16) = 800 MB independent.

Cross-shard audit chain anchor format (each transition):
    sha256("shard_<src_shard>_to_<dst_shard>_at_seq_<global_seq>_"
           "<src_w_hash_after>_<dst_w_hash_before>")
The global chain is the ordered concatenation of (per-shard cert hash) and
(shard-transition anchor) elements. Validation re-derives every transition
anchor and checks equality byte-for-byte.

Override surface: __init__, store, retrieve, edit, delete, audit, save, load.
"""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

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
from testbed.substrate_memory import SubstrateMemory


def _route_shard(key_id: str, K_shards: int) -> int:
    """Deterministic shard id: hash(key_id) % K_shards. Stable across runs."""
    h = hashlib.sha256(key_id.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % K_shards


class _SharedCodebookSubstrate(SubstrateMemory):
    """SubstrateMemory subclass that accepts a pre-built shared codebook.

    Skips the codebook construction in __init__ when codebook_override is
    passed. This is how shared-codebook sharding avoids K copies of the
    codebook tensor.
    """

    def __init__(
        self,
        N: int,
        codebook_kind: str,
        codebook_C: int,
        beta: float,
        hallu_threshold: float,
        device: str,
        seed: int,
        codebook_override: Optional[torch.Tensor] = None,
    ) -> None:
        self.N = int(N)
        self.codebook_kind = codebook_kind
        self.codebook_scale = 1  # not used; C is fixed
        self.beta = float(beta)
        self.hallu_threshold = float(hallu_threshold)
        self.device = torch.device(device)
        self.seed = int(seed)
        self.codebook_M_hint = None

        if codebook_override is not None:
            self.codebook = codebook_override
        else:
            self.codebook = get_codebook(
                codebook_kind, self.N, int(codebook_C), seed=self.seed
            ).to(self.device)
        self.C = self.codebook.shape[0]

        self.W = torch.zeros(
            self.N, self.N, dtype=torch.float32, device=self.device
        )
        self.key_registry: dict[str, int] = {}
        self.value_registry: dict[str, str] = {}
        self.value_atom_registry: dict[str, int] = {}
        self._insertion_order: list[str] = []


class ShardedSubstrate(MemoryBackend):
    """Multi-substrate sharded backend at fixed codebook C.

    K independent SubstrateMemory shards, each with its own W matrix.
    Shared codebook by default. Routing is hash(key_id) % K_shards.
    """

    name = "substrate_sharded"

    def __init__(
        self,
        N: int = 2048,
        K_shards: int = 10,
        codebook_kind: str = "bsc",
        codebook_C: int = 8192,
        beta: float = 32.0,
        hallu_threshold: float = 0.5,
        shared_codebook: bool = True,
        routing: str = "hash",
        device: str = "cpu",
        seed: int = 0,
        **kw,
    ) -> None:
        self.N = int(N)
        self.K_shards = int(K_shards)
        self.codebook_kind = codebook_kind
        self.codebook_C = int(codebook_C)
        self.C = int(codebook_C)
        self.beta = float(beta)
        self.hallu_threshold = float(hallu_threshold)
        self.shared_codebook = bool(shared_codebook)
        self.routing = str(routing)
        self.device = torch.device(device)
        self.seed = int(seed)

        if self.routing != "hash":
            raise ValueError(
                f"ShardedSubstrate routing={routing!r} not supported "
                "(MVP only supports 'hash'; learned routing is Phase 2)"
            )

        # Build the shared codebook once if requested.
        self._shared_cb: Optional[torch.Tensor] = None
        if self.shared_codebook:
            self._shared_cb = get_codebook(
                codebook_kind, self.N, self.codebook_C, seed=self.seed
            ).to(self.device)

        # Build K shards. Each shard's seed is offset so independent codebooks
        # (when shared_codebook=False) are distinct.
        self.shards: list[_SharedCodebookSubstrate] = []
        for s in range(self.K_shards):
            shard_seed = self.seed * 1009 + s
            shard = _SharedCodebookSubstrate(
                N=self.N,
                codebook_kind=codebook_kind,
                codebook_C=self.codebook_C,
                beta=self.beta,
                hallu_threshold=self.hallu_threshold,
                device=str(self.device),
                seed=shard_seed,
                codebook_override=self._shared_cb if self.shared_codebook else None,
            )
            self.shards.append(shard)

        # Global cross-shard audit-chain state.
        # Each entry: dict(seq, shard_id, key_id, key_hash, w_before, w_after,
        # transition_anchor_or_None).
        self._global_audit_chain: list[dict] = []
        self._last_delete_shard: Optional[int] = None

    # --- routing --------------------------------------------------------------

    def _shard_for_key(self, key_id: str) -> int:
        return _route_shard(key_id, self.K_shards)

    # --- ABC implementation ---------------------------------------------------

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        sid = self._shard_for_key(key_id)
        self.shards[sid].store(key_id, key_vec, value)

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        """Serial K-shard probe; return best (max-confidence) shard result.

        In production this is embarrassingly parallel across shards (one
        thread per shard); the serial MVP is honest about that and the
        benchmark reports the serial cost.
        """
        best_conf = -1.0
        best_result: Optional[RetrievalResult] = None
        agg_top_ids: list[str] = []
        agg_top_scores: list[float] = []
        for shard in self.shards:
            if len(shard.key_registry) == 0:
                continue
            r = shard.retrieve(query_vec, k=k)
            if r.confidence > best_conf:
                best_conf = r.confidence
                best_result = r
            agg_top_ids.extend(r.top_k_ids)
            agg_top_scores.extend(r.top_k_scores)

        if best_result is None:
            # No shards have data: synthesize a near-uniform negative.
            return RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=True,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )

        # Re-rank aggregate top-k by score, keep top k overall.
        order = sorted(
            range(len(agg_top_scores)),
            key=lambda i: agg_top_scores[i],
            reverse=True,
        )
        take = min(max(k, 1), len(order))
        top_k_ids = [agg_top_ids[i] for i in order[:take]]
        top_k_scores = [agg_top_scores[i] for i in order[:take]]

        return RetrievalResult(
            key_id=best_result.key_id,
            value=best_result.value,
            confidence=best_result.confidence,
            near_uniform_flag=best_result.near_uniform_flag,
            distance=best_result.distance,
            top_k_ids=top_k_ids,
            top_k_scores=top_k_scores,
        )

    def edit(self, key_id: str, new_value: str) -> None:
        sid = self._shard_for_key(key_id)
        self.shards[sid].edit(key_id, new_value)

    def delete(self, key_id: str) -> DeletionCertificate:
        """Delete the key from its owning shard and extend the cross-shard chain.

        Returns the per-shard DeletionCertificate verbatim. The cross-shard
        chain state (anchors, seq, last_shard) is tracked internally and
        exposed via global_audit_chain() for the scenario validator.
        """
        sid = self._shard_for_key(key_id)
        cert = self.shards[sid].delete(key_id)

        seq = len(self._global_audit_chain)
        transition_anchor: Optional[str] = None
        if self._last_delete_shard is not None and self._last_delete_shard != sid:
            prev_entry = self._global_audit_chain[-1]
            anchor_input = (
                f"shard_{self._last_delete_shard}_to_{sid}_at_seq_{seq}_"
                f"{prev_entry['w_state_hash_after']}_{cert.w_state_hash_before}"
            )
            transition_anchor = hashlib.sha256(
                anchor_input.encode("utf-8")
            ).hexdigest()

        self._global_audit_chain.append({
            "seq": seq,
            "shard_id": sid,
            "key_id": cert.key_id,
            "key_hash": cert.key_hash,
            "w_state_hash_before": cert.w_state_hash_before,
            "w_state_hash_after": cert.w_state_hash_after,
            "transition_anchor": transition_anchor,
            "timestamp_ns": cert.timestamp_ns,
        })
        self._last_delete_shard = sid
        return cert

    def global_audit_chain(self) -> list[dict]:
        """Return the cross-shard audit chain (read-only view)."""
        return list(self._global_audit_chain)

    def verify_global_audit_chain(self) -> dict:
        """Re-derive every shard-transition anchor and verify per-shard links.

        Returns dict with:
          links_ok: per-shard consecutive-link matches w_after -> w_before.
          links_total: total expected per-shard consecutive links checked.
          transitions_ok: cross-shard transition-anchor SHA256 matches.
          transitions_total: total transition anchors expected.
          integrity: (links_ok + transitions_ok) / (links_total + transitions_total).
        """
        entries = self._global_audit_chain
        per_shard_chains: dict[int, list[dict]] = {}
        for e in entries:
            per_shard_chains.setdefault(e["shard_id"], []).append(e)

        links_ok = 0
        links_total = 0
        for sid, chain in per_shard_chains.items():
            for i in range(len(chain) - 1):
                links_total += 1
                if chain[i]["w_state_hash_after"] == chain[i + 1]["w_state_hash_before"]:
                    links_ok += 1

        transitions_ok = 0
        transitions_total = 0
        for i in range(1, len(entries)):
            prev = entries[i - 1]
            cur = entries[i]
            if prev["shard_id"] == cur["shard_id"]:
                continue
            transitions_total += 1
            expected_input = (
                f"shard_{prev['shard_id']}_to_{cur['shard_id']}_at_seq_{cur['seq']}_"
                f"{prev['w_state_hash_after']}_{cur['w_state_hash_before']}"
            )
            expected_anchor = hashlib.sha256(
                expected_input.encode("utf-8")
            ).hexdigest()
            if cur["transition_anchor"] == expected_anchor:
                transitions_ok += 1

        denom = links_total + transitions_total
        integrity = (links_ok + transitions_ok) / denom if denom > 0 else 1.0
        return {
            "links_ok": links_ok,
            "links_total": links_total,
            "transitions_ok": transitions_ok,
            "transitions_total": transitions_total,
            "integrity": float(integrity),
        }

    def audit(self) -> AuditReport:
        """Aggregate per-shard audits: total n_items, mean KF-1, max KF-2, mean TCFT."""
        kf1_vals: list[float] = []
        kf1_mean_vals: list[float] = []
        kf2_vals: list[float] = []
        tcft_vals: list[float] = []
        n_items = 0
        storage_bytes = 0
        for shard in self.shards:
            rep = shard.audit()
            n_items += rep.n_items
            if rep.kf1_above_thresh_frac is not None:
                kf1_vals.append(rep.kf1_above_thresh_frac)
            if rep.kf1_mean_oos_max_conf is not None:
                kf1_mean_vals.append(rep.kf1_mean_oos_max_conf)
            if rep.kf2_max_isolation is not None:
                kf2_vals.append(rep.kf2_max_isolation)
            if rep.tcft_mean_var_ratio is not None:
                tcft_vals.append(rep.tcft_mean_var_ratio)
            # Per-shard storage: W matrix always; codebook only if not shared.
            storage_bytes += int(
                shard.W.element_size() * shard.W.numel()
            )
            if not self.shared_codebook:
                storage_bytes += int(
                    shard.codebook.element_size() * shard.codebook.numel()
                )
        if self.shared_codebook and self._shared_cb is not None:
            storage_bytes += int(
                self._shared_cb.element_size() * self._shared_cb.numel()
            )

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
                "N": self.N,
                "C": self.C,
                "K_shards": self.K_shards,
                "codebook_kind": self.codebook_kind,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "seed": self.seed,
                "shared_codebook": self.shared_codebook,
                "routing": self.routing,
            },
        )

    # --- persistence ----------------------------------------------------------

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        # Save shared codebook once at the top level (if shared).
        if self.shared_codebook and self._shared_cb is not None:
            cb_np = self._shared_cb.detach().cpu().numpy().astype(
                np.float32, copy=False
            )
            np.save(path / "shared_codebook.npy", cb_np)
        # Save each shard to its own subdir; skip codebook to avoid K copies.
        for sid, shard in enumerate(self.shards):
            shard_dir = path / f"shard_{sid:03d}"
            shard_dir.mkdir(parents=True, exist_ok=True)
            W_np = shard.W.detach().cpu().numpy().astype(np.float32, copy=False)
            np.save(shard_dir / "W.npy", W_np)
            if not self.shared_codebook:
                cb_np = shard.codebook.detach().cpu().numpy().astype(
                    np.float32, copy=False
                )
                np.save(shard_dir / "codebook.npy", cb_np)
            save_registry(
                {"map": shard.key_registry, "order": shard._insertion_order},
                shard_dir / "key_registry.json",
            )
            save_registry(
                {
                    "value_registry": shard.value_registry,
                    "value_atom_registry": shard.value_atom_registry,
                },
                shard_dir / "value_registry.json",
            )
        save_config(
            {
                "N": self.N,
                "K_shards": self.K_shards,
                "codebook_kind": self.codebook_kind,
                "codebook_C": self.codebook_C,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "shared_codebook": self.shared_codebook,
                "routing": self.routing,
                "device": str(self.device),
                "seed": self.seed,
            },
            path / "config.yaml",
        )
        # Persist the global audit chain for cross-shard validation.
        save_registry(
            {"chain": self._global_audit_chain,
             "last_delete_shard": self._last_delete_shard},
            path / "global_audit_chain.json",
        )

    def load(self, path: Path) -> None:
        path = Path(path)
        cfg = load_config(path / "config.yaml")
        self.N = int(cfg["N"])
        self.K_shards = int(cfg["K_shards"])
        self.codebook_kind = str(cfg["codebook_kind"])
        self.codebook_C = int(cfg["codebook_C"])
        self.C = self.codebook_C
        self.beta = float(cfg["beta"])
        self.hallu_threshold = float(cfg["hallu_threshold"])
        self.shared_codebook = bool(cfg.get("shared_codebook", True))
        self.routing = str(cfg.get("routing", "hash"))
        self.device = torch.device(cfg.get("device", "cpu"))
        self.seed = int(cfg["seed"])

        self._shared_cb = None
        if self.shared_codebook:
            cb_np = np.load(path / "shared_codebook.npy")
            self._shared_cb = torch.as_tensor(
                cb_np, dtype=torch.float32, device=self.device
            )

        self.shards = []
        for sid in range(self.K_shards):
            shard_dir = path / f"shard_{sid:03d}"
            shard_seed = self.seed * 1009 + sid
            shard = _SharedCodebookSubstrate(
                N=self.N,
                codebook_kind=self.codebook_kind,
                codebook_C=self.codebook_C,
                beta=self.beta,
                hallu_threshold=self.hallu_threshold,
                device=str(self.device),
                seed=shard_seed,
                codebook_override=self._shared_cb if self.shared_codebook else None,
            )
            if not self.shared_codebook:
                cb_np = np.load(shard_dir / "codebook.npy")
                shard.codebook = torch.as_tensor(
                    cb_np, dtype=torch.float32, device=self.device
                )
                shard.C = shard.codebook.shape[0]
            W_np = np.load(shard_dir / "W.npy")
            shard.W = torch.as_tensor(
                W_np, dtype=torch.float32, device=self.device
            )
            key_blob = load_registry(shard_dir / "key_registry.json")
            shard.key_registry = {k: int(v) for k, v in key_blob["map"].items()}
            shard._insertion_order = list(
                key_blob.get("order", list(shard.key_registry.keys()))
            )
            val_blob = load_registry(shard_dir / "value_registry.json")
            shard.value_registry = dict(val_blob["value_registry"])
            shard.value_atom_registry = {
                k: int(v) for k, v in val_blob["value_atom_registry"].items()
            }
            self.shards.append(shard)

        chain_path = path / "global_audit_chain.json"
        if chain_path.exists():
            blob = load_registry(chain_path)
            self._global_audit_chain = list(blob.get("chain", []))
            self._last_delete_shard = blob.get("last_delete_shard")
        else:
            self._global_audit_chain = []
            self._last_delete_shard = None

    def __len__(self) -> int:
        return sum(len(s.key_registry) for s in self.shards)

    def supports_killer_features(self) -> bool:
        return True
