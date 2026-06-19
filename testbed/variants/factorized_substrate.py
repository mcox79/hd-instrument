"""Substrate factorized: store W as the sum of rank-1 outer products.

Path 1 of the prioritized resolution list. Instead of materializing the dense
N x N matrix W = sum_k (val_atom_k outer key_atom_k) / N, this variant keeps
two tall matrices

    U: (N, M_capacity)  -- column k holds val_atom_k / N
    V: (N, M_capacity)  -- column k holds key_atom_k

and the equivalent dense matrix is W_equiv = U[:, :n_stored] @ V[:, :n_stored].T.
The /N normalization is parked entirely on U so V is a clean key codebook
slice. This choice is symmetric to "put /N on V" or "put /sqrt(N) on both";
all three are mathematically equivalent. Putting /N on U keeps store cheap
(one column write + one divide on the value atom) and keeps the V columns
identical to codebook rows for easier audit reasoning.

Math identity (the load-bearing correctness gate):
    dense_W == U[:, :n_stored] @ V[:, :n_stored].T   (bit-exact for fp32 ops
    issued in the same order; tiny last-bit drift may appear when the
    summation order differs, e.g. the dense path accumulates outer-by-outer
    while the matmul flushes one fused reduction. The factorized_vs_dense
    scenario measures ||delta||_inf and gates at < 1e-5.)

Retrieve cost flips from O(N^2) (dense matvec) to O(N * n_stored)
(two N x n_stored matvecs). At n_stored <= N/4 this is a 2-4x speedup; at
n_stored ~ N it matches dense; above n_stored = N the factorized form is a
loss (still mathematically equivalent though).

Memory cost:
    dense:      N * N * 4 bytes
    factorized: 2 * N * M_capacity * 4 bytes
At M_capacity < N/2 factorized is cheaper. M_capacity is the cap on
n_stored; the scenario sweeps the M_capacity / N ratio.

Edit identity: substrate's edit math is
    W' = W - outer(old_val_atom, key_atom) / N + outer(new_val_atom, key_atom) / N
       = W + outer((new_val_atom - old_val_atom), key_atom) / N
In factorized form at the slot for this key, the V column is unchanged (same
key atom) and U[:, slot] was (old_val_atom / N). The replacement
    U[:, slot] := new_val_atom / N
yields exactly U @ V.T = W', so a single column overwrite is the correct
edit. Same proof as the dense path: the factor W += outer(new_val - old_val,
key) / N is reproduced exactly.

Delete identity: dense path is W -= outer(val_atom, key_atom) / N. In
factorized form, zeroing BOTH U[:, slot] and V[:, slot] makes that slot's
contribution zero, so U @ V.T loses exactly the deleted rank-1 term. The
slot is then added to a _free_slots list and reused on the next store
(LIFO; deterministic).

Persistence: writes U.npy + V.npy instead of W.npy. SHA256 of (U bytes ||
V bytes) supplies the audit-chain hash. The audit chain is then verifiable
across factorized substrate states without ever materializing the dense W.
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
from testbed.substrate_memory import _stable_hash_int


class FactorizedSubstrate(MemoryBackend):
    """Tensor-factorized substrate. W is stored as U @ V.T.

    Implements the full MemoryBackend ABC without inheriting SubstrateMemory
    (the dense W field would defeat the memory savings). Re-uses the
    codebook + key/value registries + occupancy sets logic. All numerical
    semantics (snapping, softmax, tie-break) match SubstrateMemory exactly.
    """

    name = "substrate_factorized"

    def __init__(
        self,
        N: int = 4096,
        codebook_kind: str = "bsc",
        codebook_scale: int = 4,
        beta: float = 32.0,
        hallu_threshold: float = 0.5,
        M_capacity: Optional[int] = None,
        device: str = "cpu",
        seed: int = 0,
        codebook_M_hint: Optional[int] = None,
    ) -> None:
        """Initialize FactorizedSubstrate.

        M_capacity: upper bound on n_stored. Defaults to N (so memory tied
        to dense path). For interesting wins set M_capacity = N/4 to N/2.
        codebook_M_hint: forwarded to codebook sizing (matches v1 reference).
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
        self.M_capacity = int(M_capacity) if M_capacity is not None else self.N

        C_target = self.codebook_scale * self.N
        if self.codebook_M_hint is not None:
            C_target = max(C_target, 4 * self.codebook_M_hint)
        self.codebook = get_codebook(
            codebook_kind, self.N, C_target, seed=self.seed
        ).to(self.device)
        self.C = self.codebook.shape[0]

        # Factorized state: U @ V.T == dense_W.
        self.U = torch.zeros(
            self.N, self.M_capacity, dtype=torch.float32, device=self.device
        )
        self.V = torch.zeros(
            self.N, self.M_capacity, dtype=torch.float32, device=self.device
        )
        # n_stored is the high-water mark of occupied columns (free slots
        # below this index are tracked in _free_slots).
        self.n_stored: int = 0
        self._free_slots: list[int] = []

        # Same registries as SubstrateMemory.
        self.key_registry: dict[str, int] = {}
        self.value_registry: dict[str, str] = {}
        self.value_atom_registry: dict[str, int] = {}
        # NEW for factorized: key_id -> column slot in U/V.
        self.slot_registry: dict[str, int] = {}
        self._insertion_order: list[str] = []
        self._used_key_rows: set[int] = set()
        self._used_value_rows: set[int] = set()

        # Median-norm cache for hallu signal (b). Identical to v1.
        self._median_stored_response_norm: Optional[float] = None
        self._median_norm_n_items: int = 0

    # --- atom allocators (mirror SubstrateMemory) ---------------------------

    def _atom_for_key_id(self, key_id: str, key_vec: Optional[np.ndarray] = None) -> int:
        cached = self.key_registry.get(key_id)
        if cached is not None:
            return cached
        used = self._used_key_rows
        if len(used) >= self.C:
            raise RuntimeError(f"codebook exhausted: {len(used)} keys, C={self.C}")
        if key_vec is not None:
            row = self._snap_to_atom(key_vec)
        else:
            row = _stable_hash_int("key:" + key_id) % self.C
        while row in used:
            row = (row + 1) % self.C
        used.add(row)
        return row

    def _atom_for_value(self, key_id: str, value: str) -> int:
        used = self._used_value_rows
        cur = self.value_atom_registry.get(key_id)
        cur_was_present = False
        if cur is not None and cur in used:
            used.discard(cur)
            cur_was_present = True
        if len(used) >= self.C:
            if cur_was_present:
                used.add(cur)
            raise RuntimeError(
                f"codebook exhausted (value): {len(used)} values, C={self.C}"
            )
        row = _stable_hash_int("val:" + key_id + "::" + value) % self.C
        while row in used:
            row = (row + 1) % self.C
        used.add(row)
        return row

    def _snap_to_atom(self, query_vec: np.ndarray) -> int:
        if query_vec.ndim != 1 or query_vec.shape[0] != self.N:
            raise ValueError(
                f"query_vec shape {query_vec.shape} != (N={self.N},)"
            )
        q = torch.as_tensor(query_vec, dtype=torch.float32, device=self.device)
        sims = self.codebook @ q
        return int(torch.argmax(sims).item())

    def _allocate_slot(self) -> int:
        """Return an unused U/V column. Reuses _free_slots LIFO before extending."""
        if self._free_slots:
            return self._free_slots.pop()
        if self.n_stored >= self.M_capacity:
            raise RuntimeError(
                f"factorized substrate capacity exhausted: "
                f"n_stored={self.n_stored} M_capacity={self.M_capacity}"
            )
        slot = self.n_stored
        self.n_stored += 1
        return slot

    # --- ABC implementation -------------------------------------------------

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        """Store value under key_id. Identical contract to SubstrateMemory."""
        if key_id in self.key_registry:
            self.edit(key_id, value)
            return

        key_row = self._atom_for_key_id(key_id, key_vec)
        val_row = self._atom_for_value(key_id, value)
        slot = self._allocate_slot()

        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]

        # Math identity choice: park entire /N on U, leave V as raw key atom.
        # Then sum_k U[:, k] outer V[:, k] = sum_k (val_atom_k / N) outer key_atom_k
        # = sum_k outer(val_atom_k, key_atom_k) / N = dense substrate's W.
        self.U[:, slot] = val_atom / self.N
        self.V[:, slot] = key_atom

        self.key_registry[key_id] = key_row
        self.value_registry[key_id] = value
        self.value_atom_registry[key_id] = val_row
        self.slot_registry[key_id] = slot
        self._insertion_order.append(key_id)

    def _factorized_matvec(self, q_atom: torch.Tensor) -> torch.Tensor:
        """response = U @ (V.T @ q_atom), the O(N * n_stored) cost retrieve.

        Operates only over the active prefix [:, :n_stored]. Free slots
        contribute zeros (we zero both U[:, slot] and V[:, slot] on delete)
        so they are mathematically inert; the matmul does the right thing.
        """
        if self.n_stored == 0:
            return torch.zeros(self.N, dtype=torch.float32, device=self.device)
        Vp = self.V[:, : self.n_stored]
        Up = self.U[:, : self.n_stored]
        vt_q = Vp.T @ q_atom        # (n_stored,)
        return Up @ vt_q             # (N,)

    def _materialize_W(self) -> torch.Tensor:
        """Build the equivalent dense W = U @ V.T. Only used by self-test paths
        and the factorized_vs_dense parity check. Not called on the hot path.
        """
        if self.n_stored == 0:
            return torch.zeros(self.N, self.N, dtype=torch.float32, device=self.device)
        Up = self.U[:, : self.n_stored]
        Vp = self.V[:, : self.n_stored]
        return Up @ Vp.T

    def _refresh_median_stored_response_norm(self) -> None:
        n_items = len(self.key_registry)
        if n_items == 0:
            self._median_stored_response_norm = None
            self._median_norm_n_items = 0
            return
        all_ids = list(self.key_registry.keys())
        if len(all_ids) > 64:
            step = max(1, len(all_ids) // 64)
            sampled = all_ids[::step][:64]
        else:
            sampled = all_ids
        rows = [self.key_registry[k] for k in sampled]
        atoms = self.codebook[rows]  # (n_sample, N)
        # Batched factorized matvec: (n_sample, N) = atoms @ W.T.
        # W.T = V @ U.T (transpose of U @ V.T), so:
        # atoms @ W.T = atoms @ V @ U.T.
        if self.n_stored == 0:
            self._median_stored_response_norm = 0.0
            self._median_norm_n_items = n_items
            return
        Vp = self.V[:, : self.n_stored]
        Up = self.U[:, : self.n_stored]
        resps = (atoms @ Vp) @ Up.T  # (n_sample, N)
        norms = torch.linalg.norm(resps, dim=1)
        self._median_stored_response_norm = float(torch.median(norms).item())
        self._median_norm_n_items = n_items

    def _compute_hallu_signals(self, q_atom, response, P) -> dict:
        max_prob = float(P.max().item())
        posterior_entropy_flag = bool((max_prob * self.C) < 50.0)

        response_norm = float(torch.linalg.norm(response).item())
        if (self._median_stored_response_norm is None
                or self._median_norm_n_items == 0
                or abs(len(self.key_registry) - self._median_norm_n_items)
                / max(1, self._median_norm_n_items) > 0.25):
            self._refresh_median_stored_response_norm()
        med = self._median_stored_response_norm
        if med is None or med <= 0.0:
            low_norm_flag = False
        else:
            low_norm_flag = bool(response_norm < med * 0.5)

        top2 = torch.topk(P, 2)
        top2_vals = top2.values.tolist()
        if len(top2_vals) >= 2:
            concentration_ratio = float(top2_vals[0] / (top2_vals[1] + 1e-9))
        else:
            concentration_ratio = float("inf")
        low_concentration_flag = bool(concentration_ratio < 2.0)

        if self.key_registry:
            stored_rows = list(self._used_key_rows)
            stored_atoms = self.codebook[stored_rows]
            q_norm = float(torch.linalg.norm(q_atom).item())
            sa_norms = torch.linalg.norm(stored_atoms, dim=1)
            denom = sa_norms * max(q_norm, 1e-9)
            denom = torch.where(denom > 0.0, denom, torch.ones_like(denom))
            cos_sims = (stored_atoms @ q_atom) / denom
            max_cos = float(cos_sims.max().item())
            min_dist_to_stored = float(1.0 - max_cos)
        else:
            min_dist_to_stored = 1.0
        high_distance_flag = bool(min_dist_to_stored > 0.5)

        flags = [
            posterior_entropy_flag,
            low_norm_flag,
            low_concentration_flag,
            high_distance_flag,
        ]
        n_fired = sum(1 for f in flags if f)
        composite_flag = bool(n_fired >= 2)

        post_strength = 0.0
        if max_prob > 0.0:
            post_strength = min(1.0, 50.0 / (max_prob * self.C + 1e-9))
        if med is not None and med > 0.0:
            low_norm_strength = max(0.0, min(1.0, 1.0 - response_norm / med))
        else:
            low_norm_strength = 0.0
        if concentration_ratio <= 1.0:
            low_conc_strength = 1.0
        elif concentration_ratio >= 2.0:
            low_conc_strength = 0.0
        else:
            low_conc_strength = max(0.0, min(1.0, 2.0 - concentration_ratio))
        high_dist_strength = max(0.0, min(1.0, min_dist_to_stored))
        composite_score = float(
            0.4 * post_strength
            + 0.3 * low_norm_strength
            + 0.2 * low_conc_strength
            + 0.1 * high_dist_strength
        )

        return {
            "posterior_entropy_flag": posterior_entropy_flag,
            "low_norm_flag": low_norm_flag,
            "low_concentration_flag": low_concentration_flag,
            "high_distance_flag": high_distance_flag,
            "composite_flag": composite_flag,
            "composite_score": composite_score,
            "response_norm": response_norm,
            "median_stored_response_norm": (
                float(med) if med is not None else None
            ),
            "concentration_ratio": concentration_ratio,
            "min_dist_to_stored": min_dist_to_stored,
            "max_prob": max_prob,
        }

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        q_row = self._snap_to_atom(query_vec)
        q_atom = self.codebook[q_row]
        response = self._factorized_matvec(q_atom)            # (N,)
        sims = (self.codebook @ response) / self.N            # (C,)
        P = torch.softmax(self.beta * sims, dim=0)            # (C,)

        argmax_row = int(torch.argmax(P).item())
        max_prob = float(P[argmax_row].item())

        matching_key_id: Optional[str] = None
        candidates = [
            kid for kid, vrow in self.value_atom_registry.items()
            if vrow == argmax_row
        ]
        if candidates:
            if len(candidates) == 1:
                matching_key_id = candidates[0]
            else:
                key_rows = [self.key_registry[c] for c in candidates]
                key_atoms = self.codebook[key_rows]
                k_sims = key_atoms @ q_atom
                best = int(torch.argmax(k_sims).item())
                matching_key_id = candidates[best]

        value = self.value_registry.get(matching_key_id) if matching_key_id else None
        near_uniform = (max_prob * self.C) < 50.0

        top_k_ids: list[str] = []
        top_k_scores: list[float] = []
        stored_ids_order = list(self.key_registry.keys())
        if stored_ids_order:
            stored_v_rows = [self.value_atom_registry[kk] for kk in stored_ids_order]
            scores = P[stored_v_rows]
            order = torch.argsort(scores, descending=True)
            take = min(max(k, 1), len(stored_ids_order))
            for idx in order[:take].tolist():
                top_k_ids.append(stored_ids_order[idx])
                top_k_scores.append(float(scores[idx].item()))

        hallu_signals = self._compute_hallu_signals(q_atom, response, P)

        return RetrievalResult(
            key_id=matching_key_id,
            value=value,
            confidence=max_prob,
            near_uniform_flag=bool(near_uniform),
            distance=None,
            top_k_ids=top_k_ids,
            top_k_scores=top_k_scores,
            hallu_signals=hallu_signals,
        )

    def edit(self, key_id: str, new_value: str) -> None:
        """Edit identity: replace U[:, slot] with new_val_atom / N.

        This works because at the slot for this key, V[:, slot] is still the
        same key_atom and old_val_atom contribution is U[:, slot] @ V[:,
        slot].T. Overwriting U[:, slot] with new_val_atom / N replaces the
        rank-1 contribution outer(old_val, key)/N with outer(new_val, key)/N
        in U @ V.T, matching the dense substrate's
        W += outer(new_val - old_val, key) / N.
        """
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        slot = self.slot_registry[key_id]
        new_val_row = self._atom_for_value(key_id, new_value)
        new_atom = self.codebook[new_val_row]

        self.U[:, slot] = new_atom / self.N
        # V[:, slot] (the key atom) is unchanged.

        self.value_registry[key_id] = new_value
        self.value_atom_registry[key_id] = new_val_row

    def delete(self, key_id: str) -> DeletionCertificate:
        """Delete identity: zero U[:, slot] AND V[:, slot]; release the slot.

        Both columns are zeroed even though zeroing either one alone would
        kill the rank-1 contribution to U @ V.T. Zeroing both keeps the
        free-slot invariant honest (V[:, slot] being zero means subsequent
        reads of V never accidentally include a stale key atom in some
        future debug path) and keeps the SHA256 deterministic.
        """
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        slot = self.slot_registry[key_id]
        key_row = self.key_registry[key_id]
        val_row = self.value_atom_registry[key_id]
        key_atom = self.codebook[key_row]

        # Pre-delete variance in key direction.
        resp_pre = self._factorized_matvec(key_atom)
        var_pre = float(torch.var(resp_pre).item())

        # Audit hash BEFORE: SHA256 of U bytes concatenated with V bytes.
        # The full M_capacity-wide tensors are hashed (not just the active
        # prefix) so a tampering attempt at slot >= n_stored is also caught.
        u_before = self.U.detach().cpu().numpy().tobytes()
        v_before = self.V.detach().cpu().numpy().tobytes()
        h_before = hashlib.sha256()
        h_before.update(u_before)
        h_before.update(v_before)
        w_hash_before = h_before.hexdigest()
        key_hash = hashlib.sha256(key_id.encode("utf-8")).hexdigest()

        # Erase: zero both columns.
        self.U[:, slot] = 0.0
        self.V[:, slot] = 0.0

        # Audit hash AFTER.
        u_after = self.U.detach().cpu().numpy().tobytes()
        v_after = self.V.detach().cpu().numpy().tobytes()
        h_after = hashlib.sha256()
        h_after.update(u_after)
        h_after.update(v_after)
        w_hash_after = h_after.hexdigest()

        # Post-delete projections.
        rng_row = _stable_hash_int("delete_rng:" + key_id) % self.C
        random_atom = self.codebook[rng_row]
        resp_key = self._factorized_matvec(key_atom)
        resp_rng = self._factorized_matvec(random_atom)
        var_key_post = float(torch.var(resp_key).item())
        var_rng_post = float(torch.var(resp_rng).item())

        shrinkage = var_key_post / (var_pre + 1e-300)
        key_vs_rng = var_key_post / (var_rng_post + 1e-300)
        var_ratio = min(shrinkage, key_vs_rng)

        # Drop registry entries; release the slot.
        self._used_key_rows.discard(self.key_registry[key_id])
        self._used_value_rows.discard(self.value_atom_registry[key_id])
        del self.key_registry[key_id]
        old_value = self.value_registry.pop(key_id)
        del self.value_atom_registry[key_id]
        del self.slot_registry[key_id]
        try:
            self._insertion_order.remove(key_id)
        except ValueError:
            pass
        self._free_slots.append(slot)

        # erased: a retrieve on the key atom should not return key_id.
        key_vec_np = key_atom.detach().cpu().numpy()
        result = self.retrieve(key_vec_np)
        erased = result.key_id != key_id

        # Verification probes: 5 perturbed retrievals (same shape as v1).
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
        """KF-1 / KF-2 / TCFT sampling. Identical math to SubstrateMemory.audit;
        every place that used W is routed through factorized matvec helpers.
        """
        n_items = len(self.key_registry)
        used_rows = set(self.key_registry.values())

        free_rows = [r for r in range(self.C) if r not in used_rows]
        rng = torch.Generator(device="cpu").manual_seed(self.seed + 12345)

        kf1_above = None
        kf1_mean_max = None
        kf1_composite_fire_rate: Optional[float] = None
        kf1_per_signal_fire_rates: Optional[dict] = None
        if n_items > 0 and free_rows:
            n_oos_use = min(n_oos, len(free_rows))
            perm = torch.randperm(len(free_rows), generator=rng).tolist()
            oos_rows = [free_rows[i] for i in perm[:n_oos_use]]
            oos_atoms = self.codebook[oos_rows]  # (n_oos, N)
            # Factorized batched matvec: resp = oos_atoms @ W.T = oos_atoms @ V @ U.T.
            Vp = self.V[:, : self.n_stored]
            Up = self.U[:, : self.n_stored]
            if self.n_stored == 0:
                resp = torch.zeros(n_oos_use, self.N, dtype=torch.float32,
                                   device=self.device)
            else:
                resp = (oos_atoms @ Vp) @ Up.T
            sims = (resp @ self.codebook.T) / self.N
            P = torch.softmax(self.beta * sims, dim=1)
            max_confs = P.max(dim=1).values
            kf1_above = float((max_confs >= self.hallu_threshold).float().mean().item())
            kf1_mean_max = float(max_confs.mean().item())

            self._refresh_median_stored_response_norm()
            med = self._median_stored_response_norm

            resp_norms_oos = torch.linalg.norm(resp, dim=1)
            top2_oos = torch.topk(P, 2, dim=1)
            top2_vals_oos = top2_oos.values
            conc_oos = top2_vals_oos[:, 0] / (top2_vals_oos[:, 1] + 1e-9)
            if self.key_registry:
                stored_key_rows = list(self._used_key_rows)
                stored_key_atoms = self.codebook[stored_key_rows]
                q_norms_oos = torch.linalg.norm(oos_atoms, dim=1)
                sa_norms = torch.linalg.norm(stored_key_atoms, dim=1)
                denom = sa_norms.unsqueeze(0) * q_norms_oos.unsqueeze(1).clamp_min(1e-9)
                denom = torch.where(denom > 0.0, denom, torch.ones_like(denom))
                cos_oos = (oos_atoms @ stored_key_atoms.T) / denom
                max_cos_oos = cos_oos.max(dim=1).values
                min_dist_oos = 1.0 - max_cos_oos
            else:
                min_dist_oos = torch.ones(n_oos_use)

            posterior_flag_oos = (max_confs * self.C) < 50.0
            if med is None or med <= 0.0:
                low_norm_flag_oos = torch.zeros_like(posterior_flag_oos)
            else:
                low_norm_flag_oos = resp_norms_oos < (med * 0.5)
            low_conc_flag_oos = conc_oos < 2.0
            high_dist_flag_oos = min_dist_oos > 0.5

            n_fired_oos = (
                posterior_flag_oos.int()
                + low_norm_flag_oos.int()
                + low_conc_flag_oos.int()
                + high_dist_flag_oos.int()
            )
            composite_flag_oos = n_fired_oos >= 2
            kf1_composite_fire_rate = float(
                composite_flag_oos.float().mean().item()
            )
            kf1_per_signal_fire_rates = {
                "posterior_entropy": float(posterior_flag_oos.float().mean().item()),
                "low_norm": float(low_norm_flag_oos.float().mean().item()),
                "low_concentration": float(low_conc_flag_oos.float().mean().item()),
                "high_distance": float(high_dist_flag_oos.float().mean().item()),
            }

        # KF-2: edit isolation panel. We simulate an edit on a clone of U
        # (V is unchanged) and measure accuracy on non-edited keys.
        kf2_max_iso = None
        stored_ids = list(self.key_registry.keys())
        if len(stored_ids) >= 2:
            n_edit_use = min(n_edit, len(stored_ids))
            edit_ids = stored_ids[:n_edit_use]
            stored_rows = [self.key_registry[kk] for kk in stored_ids]
            stored_atoms = self.codebook[stored_rows]
            stored_val_rows = torch.tensor(
                [self.value_atom_registry[kk] for kk in stored_ids],
                device=self.device,
            )
            # Baseline batched factorized response: stored_atoms @ V @ U.T.
            Vp = self.V[:, : self.n_stored]
            Up = self.U[:, : self.n_stored]
            resp_base = (stored_atoms @ Vp) @ Up.T
            sims_base = (resp_base @ self.codebook.T) / self.N
            pred_base = torch.argmax(sims_base, dim=1)
            acc_base = (pred_base == stored_val_rows).float()

            iso_ratios = []
            for ei, eid in enumerate(edit_ids):
                slot = self.slot_registry[eid]
                old_val_row = self.value_atom_registry[eid]
                new_val_row = _stable_hash_int("audit_new:" + eid) % self.C
                if new_val_row == old_val_row:
                    new_val_row = (new_val_row + 1) % self.C
                new_atom = self.codebook[new_val_row]
                # Clone U, apply edit, re-evaluate. V unchanged.
                U_edit = Up.clone()
                U_edit[:, slot] = new_atom / self.N
                resp_after = (stored_atoms @ Vp) @ U_edit.T
                sims_after = (resp_after @ self.codebook.T) / self.N
                pred_after = torch.argmax(sims_after, dim=1)
                acc_after = (pred_after == stored_val_rows).float()

                mask = torch.ones(len(stored_ids), dtype=torch.bool)
                mask[ei] = False
                if mask.any():
                    delta = (acc_base[mask] - acc_after[mask]).abs().mean().item()
                    iso_ratios.append(float(delta))
            if iso_ratios:
                kf2_max_iso = float(max(iso_ratios))

        # TCFT: deletion var_ratio panel. Simulate a delete on cloned U+V.
        tcft_mean_vr = None
        if stored_ids:
            n_del_use = min(n_delete, len(stored_ids))
            del_ids = stored_ids[:n_del_use]
            vrs = []
            for did in del_ids:
                slot = self.slot_registry[did]
                key_row = self.key_registry[did]
                key_atom = self.codebook[key_row]
                resp_pre = self._factorized_matvec(key_atom)
                var_pre = float(torch.var(resp_pre).item())
                # Clone, zero the slot.
                U_del = self.U[:, : self.n_stored].clone()
                V_del = self.V[:, : self.n_stored].clone()
                U_del[:, slot] = 0.0
                V_del[:, slot] = 0.0
                # Compute resp on cloned factors.
                vt_key = V_del.T @ key_atom
                resp_key = U_del @ vt_key
                rng_row = _stable_hash_int("audit_rng:" + did) % self.C
                random_atom = self.codebook[rng_row]
                vt_rng = V_del.T @ random_atom
                resp_rng = U_del @ vt_rng
                var_key = float(torch.var(resp_key).item())
                var_rng = float(torch.var(resp_rng).item())
                shrinkage = var_key / (var_pre + 1e-300)
                key_vs_rng = var_key / (var_rng + 1e-300)
                vrs.append(min(shrinkage, key_vs_rng))
            if vrs:
                tcft_mean_vr = float(sum(vrs) / len(vrs))

        storage_bytes = (
            self.U.element_size() * self.U.numel()
            + self.V.element_size() * self.V.numel()
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
                "M_capacity": self.M_capacity,
                "n_stored": self.n_stored,
                "codebook_kind": self.codebook_kind,
                "beta": self.beta,
                "hallu_threshold": self.hallu_threshold,
                "seed": self.seed,
                "factorized": True,
            },
            kf1_composite_fire_rate=kf1_composite_fire_rate,
            kf1_per_signal_fire_rates=kf1_per_signal_fire_rates,
        )

    # --- persistence --------------------------------------------------------

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        U_np = self.U.detach().cpu().numpy().astype(np.float32, copy=False)
        V_np = self.V.detach().cpu().numpy().astype(np.float32, copy=False)
        cb_np = self.codebook.detach().cpu().numpy().astype(np.float32, copy=False)
        np.save(path / "U.npy", U_np)
        np.save(path / "V.npy", V_np)
        np.save(path / "codebook.npy", cb_np)
        save_registry(
            {
                "map": self.key_registry,
                "order": self._insertion_order,
                "slots": self.slot_registry,
                "n_stored": self.n_stored,
                "free_slots": self._free_slots,
            },
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
                "M_capacity": self.M_capacity,
                "device": str(self.device),
                "seed": self.seed,
                "C": self.C,
                "codebook_M_hint": (
                    self.codebook_M_hint if self.codebook_M_hint is not None else 0
                ),
                "factorized": True,
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
        self.M_capacity = int(cfg.get("M_capacity", self.N))
        self.device = torch.device(cfg.get("device", "cpu"))
        self.seed = int(cfg["seed"])
        hint = cfg.get("codebook_M_hint", 0)
        try:
            self.codebook_M_hint = int(hint) if int(hint) > 0 else None
        except (TypeError, ValueError):
            self.codebook_M_hint = None

        U_np = np.load(path / "U.npy")
        V_np = np.load(path / "V.npy")
        self.U = torch.as_tensor(U_np, dtype=torch.float32, device=self.device)
        self.V = torch.as_tensor(V_np, dtype=torch.float32, device=self.device)
        cb_np = np.load(path / "codebook.npy")
        self.codebook = torch.as_tensor(cb_np, dtype=torch.float32, device=self.device)
        self.C = self.codebook.shape[0]

        key_blob = load_registry(path / "key_registry.json")
        self.key_registry = {k: int(v) for k, v in key_blob["map"].items()}
        self._insertion_order = list(key_blob.get("order", list(self.key_registry.keys())))
        self.slot_registry = {k: int(v) for k, v in key_blob.get("slots", {}).items()}
        self.n_stored = int(key_blob.get("n_stored", len(self.key_registry)))
        self._free_slots = [int(x) for x in key_blob.get("free_slots", [])]
        val_blob = load_registry(path / "value_registry.json")
        self.value_registry = dict(val_blob["value_registry"])
        self.value_atom_registry = {
            k: int(v) for k, v in val_blob["value_atom_registry"].items()
        }
        self._used_key_rows = set(self.key_registry.values())
        self._used_value_rows = set(self.value_atom_registry.values())

    def __len__(self) -> int:
        return len(self.key_registry)

    def supports_killer_features(self) -> bool:
        return True


if __name__ == "__main__":
    # Self-test: math identity vs dense substrate at N=128, M=16.
    from testbed.substrate_memory import SubstrateMemory

    N = 128
    M = 16
    dense = SubstrateMemory(
        N=N, codebook_kind="bsc", codebook_scale=4, beta=32.0, seed=7
    )
    fact = FactorizedSubstrate(
        N=N, codebook_kind="bsc", codebook_scale=4, beta=32.0,
        M_capacity=M, seed=7
    )
    # Codebooks must match (same seed + same kind + same C).
    assert torch.allclose(dense.codebook, fact.codebook), "codebook mismatch"

    # Use direct codebook-row indexing for query vectors so both backends
    # snap-allocate identical key rows. We pick distinct rows manually so
    # there is no hash + snap interaction that diverges across backends.
    for i in range(M):
        kid = f"k_{i}"
        # Pick row i * (C // M) so rows are spread and distinct.
        target_row = (i * (dense.C // M)) % dense.C
        kvec = dense.codebook[target_row].detach().cpu().numpy()
        dense.store(kid, kvec, f"v_{i}")
        fact.store(kid, kvec, f"v_{i}")

    # Math identity: dense.W == fact.U @ fact.V.T.
    W_dense = dense.W
    W_fact = fact._materialize_W()
    delta = float((W_dense - W_fact).abs().max().item())
    assert delta < 1e-5, f"math identity failed: max abs delta {delta}"

    # Recall.
    correct_dense = 0
    correct_fact = 0
    for i in range(M):
        kid = f"k_{i}"
        target_row = (i * (dense.C // M)) % dense.C
        qvec = dense.codebook[target_row].detach().cpu().numpy()
        r_dense = dense.retrieve(qvec)
        r_fact = fact.retrieve(qvec)
        if r_dense.key_id == kid:
            correct_dense += 1
        if r_fact.key_id == kid:
            correct_fact += 1
    assert correct_dense == M, f"dense recall {correct_dense}/{M}"
    assert correct_fact == M, f"fact recall {correct_fact}/{M}"

    # Edit identity.
    dense.edit("k_3", "v_3_new")
    fact.edit("k_3", "v_3_new")
    W_dense = dense.W
    W_fact = fact._materialize_W()
    delta_edit = float((W_dense - W_fact).abs().max().item())
    assert delta_edit < 1e-5, f"edit identity failed: {delta_edit}"

    # Delete identity.
    cert_dense = dense.delete("k_5")
    cert_fact = fact.delete("k_5")
    W_dense = dense.W
    W_fact = fact._materialize_W()
    delta_del = float((W_dense - W_fact).abs().max().item())
    assert delta_del < 1e-5, f"delete identity failed: {delta_del}"

    print(f"factorized_substrate self-test OK: parity store={delta:.2e} "
          f"edit={delta_edit:.2e} delete={delta_del:.2e} "
          f"recall {correct_fact}/{M}")
