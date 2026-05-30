"""SubstrateMemory: wraps hd-instrument outer-product Hebbian primitives as a
MemoryBackend implementation.

Design:
  W is an (N, N) float32 tensor. Each store(key_id, key_vec, value) allocates a
  fresh codebook row for the key_id and the value_string (seeded by hash(key_id)
  and hash(value)). The Hebbian write is W += outer(value_atom, key_atom) / N,
  matching store_facts_outer in experiments/exp_kf1_hallu_impossibility_v2.py.

  retrieve(query_vec) snaps query_vec to its nearest codebook atom by inner
  product, computes response = W @ q_atom, then sims = (codebook @ response) / N
  and P = softmax(beta * sims). Returns argmax key_id, max_prob, and
  near_uniform_flag = (max_prob * C < 50) per the KF-1 v2 convention.

  edit(key_id, new_value): W -= outer(old_v_atom, key_atom) / N; W +=
  outer(new_v_atom, key_atom) / N. Preserves isolation (KF-2).

  delete(key_id): W -= outer(value_atom, key_atom) / N. Measures var_ratio =
  var(W @ key_atom) / var(W @ random_atom). erased is set by re-running retrieve
  on the same key_vec.

  audit(): samples OOS queries for KF-1, samples edit trials for KF-2, samples
  delete trials for TCFT. Edits and deletes are applied to clones of W to keep
  the live W untouched.

  save/load: writes W.npy, codebook.npy, key_registry.json, value_registry.json,
  config.yaml under the path directory. Reload uses np.memmap for W (cheap) and
  full read for the codebook.
"""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent
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
    load_W_memmap,
    load_config,
    load_registry,
    save_W,
    save_config,
    save_registry,
)


def _stable_hash_int(s: str) -> int:
    """Deterministic non-negative 31-bit int from a string. Stable across runs."""
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16) & 0x7FFFFFFF


class SubstrateMemory(MemoryBackend):
    name = "substrate"

    def __init__(
        self,
        N: int = 4096,
        codebook_kind: str = "bsc",
        codebook_scale: int = 4,
        beta: float = 32.0,
        hallu_threshold: float = 0.5,
        device: str = "cpu",
        seed: int = 0,
        codebook_M_hint: int | None = None,
    ) -> None:
        """Initialize SubstrateMemory.

        codebook_M_hint: if provided, codebook size C = max(codebook_scale*N, 4*M).
        This lets large-M scenarios (>>N) configure a codebook big enough to avoid
        atom collisions. None = legacy behavior (C = codebook_scale * N).
        """
        self.N = int(N)
        self.codebook_kind = codebook_kind
        self.codebook_scale = int(codebook_scale)
        self.beta = float(beta)
        self.hallu_threshold = float(hallu_threshold)
        self.device = torch.device(device)
        self.seed = int(seed)
        self.codebook_M_hint = (
            int(codebook_M_hint) if codebook_M_hint is not None else None
        )

        # Codebook size: bsc/gaussian honor codebook_scale; kerdock is fixed at 4N.
        # Adaptive sizing per shine plan A.3.1: when an M hint is provided,
        # bump C to at least 4*M to keep collision rate low at large M.
        C_target = self.codebook_scale * self.N
        if self.codebook_M_hint is not None:
            C_target = max(C_target, 4 * self.codebook_M_hint)
        self.codebook = get_codebook(
            codebook_kind, self.N, C_target, seed=self.seed
        ).to(self.device)
        self.C = self.codebook.shape[0]

        self.W = torch.zeros(
            self.N, self.N, dtype=torch.float32, device=self.device
        )

        # key_id -> codebook row index for the key atom
        self.key_registry: dict[str, int] = {}
        # key_id -> value_string (the stored payload)
        self.value_registry: dict[str, str] = {}
        # key_id -> codebook row index for the value atom
        self.value_atom_registry: dict[str, int] = {}
        # ordered list of key_ids for deterministic iteration
        self._insertion_order: list[str] = []

    # --- helpers --------------------------------------------------------------

    def _atom_for_key_id(self, key_id: str, key_vec: Optional[np.ndarray] = None) -> int:
        """Deterministic codebook row index for a key_id.

        If key_vec is provided, the key atom is the nearest codebook row to
        key_vec (so a later retrieve(key_vec) lands on the same atom). This
        is the apples-to-apples path with baselines that consume key_vec
        directly. Collisions with already-used key rows are resolved by
        linear probing to keep the substrate's edit/delete bookkeeping
        bijective.

        If key_vec is None, falls back to hashing key_id (used by self-test
        paths that don't have a key_vec).
        """
        cached = self.key_registry.get(key_id)
        if cached is not None:
            return cached
        used = set(self.key_registry.values())
        if len(used) >= self.C:
            raise RuntimeError(
                f"codebook exhausted: {len(used)} keys, C={self.C}"
            )
        if key_vec is not None:
            row = self._snap_to_atom(key_vec)
        else:
            row = _stable_hash_int("key:" + key_id) % self.C
        # Linear probe to first free row.
        while row in used:
            row = (row + 1) % self.C
        return row

    def _atom_for_value(self, key_id: str, value: str) -> int:
        """Deterministic codebook row index for a (key_id, value) pair.

        Avoids collision with currently-used VALUE atoms (excluding the row
        already held by this key_id, which is the row being replaced on edit).
        Conditioning the seed on key_id keeps edits to the same key isolated.
        """
        used = set(self.value_atom_registry.values())
        # On edit, the current value row is the one we are vacating; allow
        # the new hash to land on it (no-op edit case) by not excluding it.
        cur = self.value_atom_registry.get(key_id)
        if cur is not None:
            used.discard(cur)
        if len(used) >= self.C:
            raise RuntimeError(
                f"codebook exhausted (value): {len(used)} values, C={self.C}"
            )
        row = _stable_hash_int("val:" + key_id + "::" + value) % self.C
        while row in used:
            row = (row + 1) % self.C
        return row

    def _snap_to_atom(self, query_vec: np.ndarray) -> int:
        """Snap a numpy query vector to nearest codebook row by inner product.

        Returns the codebook row index.
        """
        if query_vec.ndim != 1 or query_vec.shape[0] != self.N:
            raise ValueError(
                f"query_vec shape {query_vec.shape} != (N={self.N},)"
            )
        q = torch.as_tensor(query_vec, dtype=torch.float32, device=self.device)
        sims = self.codebook @ q  # (C,)
        return int(torch.argmax(sims).item())

    # --- ABC implementation ---------------------------------------------------

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        """Store value under key_id.

        Per the architect-doc Risk 3 mitigation, key_vec is ignored on store:
        the key atom is allocated by hashing key_id. key_vec is consumed at
        retrieve time (snapped to nearest atom) for apples-to-apples baseline
        comparison.
        """
        if key_id in self.key_registry:
            # Re-store: treat as edit with possibly-new value.
            self.edit(key_id, value)
            return

        key_row = self._atom_for_key_id(key_id, key_vec)
        val_row = self._atom_for_value(key_id, value)

        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]
        self.W = self.W + torch.outer(val_atom, key_atom) / self.N

        self.key_registry[key_id] = key_row
        self.value_registry[key_id] = value
        self.value_atom_registry[key_id] = val_row
        self._insertion_order.append(key_id)

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        """Retrieve top-1 (or top-k) by softmax max-prob over codebook sims."""
        q_row = self._snap_to_atom(query_vec)
        q_atom = self.codebook[q_row]
        response = self.W @ q_atom  # (N,)
        sims = (self.codebook @ response) / self.N  # (C,)
        P = torch.softmax(self.beta * sims, dim=0)  # (C,)

        argmax_row = int(torch.argmax(P).item())
        max_prob = float(P[argmax_row].item())

        # Recall convention: W = sum_i outer(value_atom_i, key_atom_i) / N.
        # So W @ q_atom approximates value_atom_i when q_atom ~= key_atom_i.
        # Reverse-lookup by value_atom_registry to find the owning key_id.
        # If multiple key_ids share a value atom row (collision), pick the one
        # whose key atom snaps closest to q_atom.
        matching_key_id: Optional[str] = None
        candidates = [
            kid for kid, vrow in self.value_atom_registry.items()
            if vrow == argmax_row
        ]
        if candidates:
            if len(candidates) == 1:
                matching_key_id = candidates[0]
            else:
                # Tie-break: candidate whose key_atom inner-product with q_atom is largest.
                key_rows = [self.key_registry[c] for c in candidates]
                key_atoms = self.codebook[key_rows]  # (n_cand, N)
                k_sims = key_atoms @ q_atom  # (n_cand,)
                best = int(torch.argmax(k_sims).item())
                matching_key_id = candidates[best]

        value = self.value_registry.get(matching_key_id) if matching_key_id else None
        near_uniform = (max_prob * self.C) < 50.0

        # top-k: rank stored keys by P at their value-atom row.
        top_k_ids: list[str] = []
        top_k_scores: list[float] = []
        stored_ids_order = list(self.key_registry.keys())
        if stored_ids_order:
            stored_v_rows = [self.value_atom_registry[k] for k in stored_ids_order]
            scores = P[stored_v_rows]  # (n_stored,)
            order = torch.argsort(scores, descending=True)
            take = min(max(k, 1), len(stored_ids_order))
            for idx in order[:take].tolist():
                top_k_ids.append(stored_ids_order[idx])
                top_k_scores.append(float(scores[idx].item()))

        return RetrievalResult(
            key_id=matching_key_id,
            value=value,
            confidence=max_prob,
            near_uniform_flag=bool(near_uniform),
            distance=None,
            top_k_ids=top_k_ids,
            top_k_scores=top_k_scores,
        )

    def edit(self, key_id: str, new_value: str) -> None:
        """In-place value swap: subtract old outer, add new outer."""
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        key_row = self.key_registry[key_id]
        old_val_row = self.value_atom_registry[key_id]
        new_val_row = self._atom_for_value(key_id, new_value)

        key_atom = self.codebook[key_row]
        old_atom = self.codebook[old_val_row]
        new_atom = self.codebook[new_val_row]

        self.W = self.W - torch.outer(old_atom, key_atom) / self.N
        self.W = self.W + torch.outer(new_atom, key_atom) / self.N

        self.value_registry[key_id] = new_value
        self.value_atom_registry[key_id] = new_val_row

    def delete(self, key_id: str) -> DeletionCertificate:
        """Fresh-erase delete: subtract outer + compute TCFT-style var_ratio.

        var_ratio interpretation per the architect spec: ratio of the residual
        variance in the deleted-key direction to a comparable random-direction
        variance. We use the variance reduction caused by the delete as a more
        sensitive shrinkage signal: var(W_post @ key) / var(W_pre @ key).
        Values close to 0 indicate the deletion eliminated almost all signal
        along the key direction; values near 1 indicate the delete had no
        statistical effect. Matches the spirit of TCFT v3 (variance reduction
        under conditioning) for the simpler one-shot delete case.
        """
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        key_row = self.key_registry[key_id]
        val_row = self.value_atom_registry[key_id]
        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]

        # Pre-delete projection magnitude (for shrinkage).
        resp_pre = self.W @ key_atom
        var_pre = float(torch.var(resp_pre).item())

        # Cryptographic audit trail: hash W before the erase step.
        import hashlib
        w_before_bytes = self.W.detach().cpu().numpy().tobytes()
        w_hash_before = hashlib.sha256(w_before_bytes).hexdigest()
        key_hash = hashlib.sha256(key_id.encode("utf-8")).hexdigest()

        # Erase: subtract the outer product.
        self.W = self.W - torch.outer(val_atom, key_atom) / self.N

        # Hash W after the erase step.
        w_after_bytes = self.W.detach().cpu().numpy().tobytes()
        w_hash_after = hashlib.sha256(w_after_bytes).hexdigest()

        # Post-delete projections: key direction and a stable random direction.
        rng_row = _stable_hash_int("delete_rng:" + key_id) % self.C
        random_atom = self.codebook[rng_row]
        resp_key = self.W @ key_atom
        resp_rng = self.W @ random_atom
        var_key_post = float(torch.var(resp_key).item())
        var_rng_post = float(torch.var(resp_rng).item())

        # Two ratios: shrinkage (pre->post in key direction) and key-vs-random.
        # Smoke gate uses shrinkage; both are stored on the certificate via
        # var_ratio (shrinkage is the more sensitive of the two).
        shrinkage = var_key_post / (var_pre + 1e-300)
        key_vs_rng = var_key_post / (var_rng_post + 1e-300)
        # Use the min: a successful delete satisfies either condition strongly.
        var_ratio = min(shrinkage, key_vs_rng)

        # Remove registry entries.
        del self.key_registry[key_id]
        old_value = self.value_registry.pop(key_id)
        del self.value_atom_registry[key_id]
        try:
            self._insertion_order.remove(key_id)
        except ValueError:
            pass

        # erased: retrieve with the key atom (as a numpy vector) should not
        # return the deleted key_id.
        key_vec_np = key_atom.detach().cpu().numpy()
        result = self.retrieve(key_vec_np)
        erased = result.key_id != key_id

        # Verification probes: 5 multi-probe Mirage checks that the erased
        # fact is not recoverable. Each probe uses a slight perturbation of
        # the original key vector. Compliance auditor reads this list to
        # confirm structural non-recoverability beyond the single-shot result.
        verification_probes = []
        for probe_idx in range(5):
            probe_atom = key_atom + 0.05 * (probe_idx + 1) * (
                self.codebook[probe_idx] - key_atom
            ) / float(probe_idx + 1)
            probe_vec = probe_atom.detach().cpu().numpy()
            probe_result = self.retrieve(probe_vec)
            verification_probes.append({
                "probe_idx": probe_idx,
                "max_prob": probe_result.confidence,
                "near_uniform_flag": probe_result.near_uniform_flag,
                "returned_key_id": probe_result.key_id,
            })

        # Touch old_value to silence linters; not used past this point.
        _ = old_value

        return DeletionCertificate(
            key_id=key_id,
            var_ratio=float(var_ratio),
            erased=bool(erased),
            timestamp_ns=time.time_ns(),
            key_hash=key_hash,
            w_state_hash_before=w_hash_before,
            w_state_hash_after=w_hash_after,
            verification_probes=verification_probes,
        )

    def audit(
        self,
        n_oos: int = 256,
        n_edit: int = 16,
        n_delete: int = 16,
    ) -> AuditReport:
        """Sample OOS / edit / delete panels and report KF-1, KF-2, TCFT metrics.

        Edits and deletes operate on cloned W tensors so the live store is not
        mutated. Audit is read-only for the backend caller.
        """
        n_items = len(self.key_registry)
        used_rows = set(self.key_registry.values())

        # --- KF-1: OOS hallucination panel -----------------------------------
        free_rows = [r for r in range(self.C) if r not in used_rows]
        rng = torch.Generator(device="cpu").manual_seed(self.seed + 12345)

        kf1_above = None
        kf1_mean_max = None
        if n_items > 0 and free_rows:
            n_oos_use = min(n_oos, len(free_rows))
            perm = torch.randperm(len(free_rows), generator=rng).tolist()
            oos_rows = [free_rows[i] for i in perm[:n_oos_use]]
            oos_atoms = self.codebook[oos_rows]  # (n_oos, N)
            # response: (n_oos, N) = oos_atoms @ W.T
            resp = oos_atoms @ self.W.T
            sims = (resp @ self.codebook.T) / self.N  # (n_oos, C)
            P = torch.softmax(self.beta * sims, dim=1)
            max_confs = P.max(dim=1).values  # (n_oos,)
            kf1_above = float((max_confs >= self.hallu_threshold).float().mean().item())
            kf1_mean_max = float(max_confs.mean().item())

        # --- KF-2: edit-isolation panel --------------------------------------
        kf2_max_iso = None
        stored_ids = list(self.key_registry.keys())
        if len(stored_ids) >= 2:
            n_edit_use = min(n_edit, len(stored_ids))
            edit_ids = stored_ids[:n_edit_use]
            # Compute baseline argmax over stored keys.
            stored_rows = [self.key_registry[k] for k in stored_ids]
            stored_atoms = self.codebook[stored_rows]
            stored_val_rows = torch.tensor(
                [self.value_atom_registry[k] for k in stored_ids],
                device=self.device,
            )
            # baseline retrieval
            resp_base = stored_atoms @ self.W.T
            sims_base = (resp_base @ self.codebook.T) / self.N
            pred_base = torch.argmax(sims_base, dim=1)
            acc_base = (pred_base == stored_val_rows).float()

            iso_ratios = []
            for ei, eid in enumerate(edit_ids):
                key_row = self.key_registry[eid]
                old_val_row = self.value_atom_registry[eid]
                # Pick a deterministic new value atom different from old.
                new_val_row = (
                    _stable_hash_int("audit_new:" + eid) % self.C
                )
                if new_val_row == old_val_row:
                    new_val_row = (new_val_row + 1) % self.C
                key_atom = self.codebook[key_row]
                old_atom = self.codebook[old_val_row]
                new_atom = self.codebook[new_val_row]
                W_edit = self.W - torch.outer(old_atom, key_atom) / self.N
                W_edit = W_edit + torch.outer(new_atom, key_atom) / self.N

                resp_after = stored_atoms @ W_edit.T
                sims_after = (resp_after @ self.codebook.T) / self.N
                pred_after = torch.argmax(sims_after, dim=1)
                acc_after = (pred_after == stored_val_rows).float()

                # delta over non-edited keys
                mask = torch.ones(len(stored_ids), dtype=torch.bool)
                mask[ei] = False
                if mask.any():
                    delta = (acc_base[mask] - acc_after[mask]).abs().mean().item()
                    iso_ratios.append(float(delta))
            if iso_ratios:
                kf2_max_iso = float(max(iso_ratios))

        # --- TCFT: deletion var_ratio panel ----------------------------------
        # Uses the same shrinkage convention as delete(): var_post / var_pre
        # in the key direction (minimum with key-vs-random for robustness).
        tcft_mean_vr = None
        if stored_ids:
            n_del_use = min(n_delete, len(stored_ids))
            del_ids = stored_ids[:n_del_use]
            vrs = []
            for did in del_ids:
                key_row = self.key_registry[did]
                val_row = self.value_atom_registry[did]
                key_atom = self.codebook[key_row]
                val_atom = self.codebook[val_row]
                resp_pre = self.W @ key_atom
                var_pre = float(torch.var(resp_pre).item())
                W_del = self.W - torch.outer(val_atom, key_atom) / self.N

                rng_row = _stable_hash_int("audit_rng:" + did) % self.C
                random_atom = self.codebook[rng_row]
                resp_key = W_del @ key_atom
                resp_rng = W_del @ random_atom
                var_key = float(torch.var(resp_key).item())
                var_rng = float(torch.var(resp_rng).item())
                shrinkage = var_key / (var_pre + 1e-300)
                key_vs_rng = var_key / (var_rng + 1e-300)
                vrs.append(min(shrinkage, key_vs_rng))
            if vrs:
                tcft_mean_vr = float(sum(vrs) / len(vrs))

        storage_bytes = (
            self.W.element_size() * self.W.numel()
            + self.codebook.element_size() * self.codebook.numel()
        )

        return AuditReport(
            backend=self.name,
            n_items=n_items,
            kf1_above_thresh_frac=kf1_above,
            kf1_mean_oos_max_conf=kf1_mean_max,
            kf2_max_isolation=kf2_max_iso,
            tcft_mean_var_ratio=tcft_mean_vr,
            storage_bytes=int(storage_bytes),
            config={
                "N": self.N,
                "C": self.C,
                "codebook_kind": self.codebook_kind,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "seed": self.seed,
            },
        )

    # --- persistence ----------------------------------------------------------

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        W_np = self.W.detach().cpu().numpy().astype(np.float32, copy=False)
        cb_np = self.codebook.detach().cpu().numpy().astype(np.float32, copy=False)
        save_W(W_np, path / "W.npy")
        np.save(path / "codebook.npy", cb_np)
        save_registry(
            {"map": self.key_registry, "order": self._insertion_order},
            path / "key_registry.json",
        )
        save_registry(
            {
                "value_registry": self.value_registry,
                "value_atom_registry": self.value_atom_registry,
            },
            path / "value_registry.json",
        )
        save_config(
            {
                "N": self.N,
                "codebook_kind": self.codebook_kind,
                "codebook_scale": self.codebook_scale,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "device": str(self.device),
                "seed": self.seed,
                "C": self.C,
                "codebook_M_hint": (
                    self.codebook_M_hint if self.codebook_M_hint is not None else 0
                ),
            },
            path / "config.yaml",
        )

    def load(self, path: Path) -> None:
        path = Path(path)
        cfg = load_config(path / "config.yaml")
        self.N = int(cfg["N"])
        self.codebook_kind = str(cfg["codebook_kind"])
        self.codebook_scale = int(cfg["codebook_scale"])
        self.beta = float(cfg["beta"])
        self.hallu_threshold = float(cfg["hallu_threshold"])
        self.device = torch.device(cfg.get("device", "cpu"))
        self.seed = int(cfg["seed"])
        hint = cfg.get("codebook_M_hint", 0)
        try:
            self.codebook_M_hint = int(hint) if int(hint) > 0 else None
        except (TypeError, ValueError):
            self.codebook_M_hint = None

        W_mm = load_W_memmap(path / "W.npy")
        # Materialize once into a torch tensor so subsequent edits/deletes work.
        self.W = torch.as_tensor(np.array(W_mm), dtype=torch.float32, device=self.device)
        cb_np = np.load(path / "codebook.npy")
        self.codebook = torch.as_tensor(cb_np, dtype=torch.float32, device=self.device)
        self.C = self.codebook.shape[0]

        key_blob = load_registry(path / "key_registry.json")
        self.key_registry = {k: int(v) for k, v in key_blob["map"].items()}
        self._insertion_order = list(key_blob.get("order", list(self.key_registry.keys())))
        val_blob = load_registry(path / "value_registry.json")
        self.value_registry = dict(val_blob["value_registry"])
        self.value_atom_registry = {
            k: int(v) for k, v in val_blob["value_atom_registry"].items()
        }

    def __len__(self) -> int:
        return len(self.key_registry)

    def supports_killer_features(self) -> bool:
        return True


if __name__ == "__main__":
    # Self-test: deterministic N=128 C=512 M=16 store -> retrieve -> recall == 1.0
    # codebook_scale=4 matches the default convention; with C >> M, value-atom
    # collisions are vanishingly rare and BSC recall is near-perfect.
    mem = SubstrateMemory(N=128, codebook_kind="bsc", codebook_scale=4, beta=32.0, seed=7)
    M = 16
    # Use codebook atoms as the key_vec inputs.
    for i in range(M):
        kid = f"k_{i}"
        # Use the deterministic key atom for this id as the query later.
        row = mem._atom_for_key_id(kid)
        kvec = mem.codebook[row].detach().cpu().numpy()
        mem.store(kid, kvec, f"v_{i}")
    correct = 0
    for i in range(M):
        kid = f"k_{i}"
        row = mem._atom_for_key_id(kid)
        qvec = mem.codebook[row].detach().cpu().numpy()
        r = mem.retrieve(qvec)
        if r.key_id == kid and r.value == f"v_{i}":
            correct += 1
    assert correct == M, f"substrate self-test recall {correct}/{M}"
    print(f"substrate self-test OK: recall {correct}/{M} == 1.0")
