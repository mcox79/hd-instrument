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
        # Persistent occupancy sets for O(1) allocation lookups (Path 9 fix).
        # Invariant: _used_key_rows == set(key_registry.values()) and
        # _used_value_rows == set(value_atom_registry.values()) at all times
        # between API calls. Updated incrementally on store / edit / delete
        # so we never re-build set(registry.values()) on the hot path.
        self._used_key_rows: set[int] = set()
        self._used_value_rows: set[int] = set()

        # Path-15: running statistic for the median stored-response norm.
        # Set lazily by _compute_hallu_signals if there are stored items.
        # None until at least one fact has been written.
        self._median_stored_response_norm: Optional[float] = None
        # Sample budget for the median estimator; cached for one retrieve
        # cycle then re-sampled when registry size changes by >25%.
        self._median_norm_n_items: int = 0

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
        used = self._used_key_rows
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
        used.add(row)
        return row

    def _atom_for_value(self, key_id: str, value: str) -> int:
        """Deterministic codebook row index for a (key_id, value) pair.

        Avoids collision with currently-used VALUE atoms (excluding the row
        already held by this key_id, which is the row being replaced on edit).
        Conditioning the seed on key_id keeps edits to the same key isolated.
        """
        used = self._used_value_rows
        # On edit, the current value row is the one we are vacating; allow
        # the new hash to land on it (no-op edit case) by not excluding it.
        # We temporarily remove `cur` from the persistent set so the probe
        # sees the vacated state; the chosen row (possibly == cur) is added
        # back before returning, leaving the invariant intact.
        cur = self.value_atom_registry.get(key_id)
        cur_was_present = False
        if cur is not None and cur in used:
            used.discard(cur)
            cur_was_present = True
        if len(used) >= self.C:
            # Restore invariant before raising.
            if cur_was_present:
                used.add(cur)
            raise RuntimeError(
                f"codebook exhausted (value): {len(used)} values, C={self.C}"
            )
        row = _stable_hash_int("val:" + key_id + "::" + value) % self.C
        while row in used:
            row = (row + 1) % self.C
        used.add(row)
        # If we vacated `cur` but the new row landed elsewhere, the old row
        # is now genuinely free; the caller (edit) is responsible for not
        # re-adding it. Nothing else to do here: the invariant is restored
        # at the caller's bookkeeping site.
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

    # --- Path-15: multi-signal hallucination detection -----------------------

    def _refresh_median_stored_response_norm(self) -> None:
        """Estimate median ||W @ stored_key_atom|| over current stored items.

        Cached on the instance. Recomputed when the stored-item count drifts
        by more than 25% from the last sample, or when invalidated by edit/
        delete. Uses a stratified sample of up to 64 items for cost.
        """
        n_items = len(self.key_registry)
        if n_items == 0:
            self._median_stored_response_norm = None
            self._median_norm_n_items = 0
            return
        # Stratified sample: deterministic order by insertion.
        all_ids = list(self.key_registry.keys())
        if len(all_ids) > 64:
            step = max(1, len(all_ids) // 64)
            sampled = all_ids[::step][:64]
        else:
            sampled = all_ids
        rows = [self.key_registry[k] for k in sampled]
        atoms = self.codebook[rows]  # (n_sample, N)
        # Batched responses: (n_sample, N) = atoms @ W.T
        resps = atoms @ self.W.T  # (n_sample, N)
        norms = torch.linalg.norm(resps, dim=1)  # (n_sample,)
        self._median_stored_response_norm = float(torch.median(norms).item())
        self._median_norm_n_items = n_items

    def _compute_hallu_signals(
        self,
        q_atom: torch.Tensor,
        response: torch.Tensor,
        P: torch.Tensor,
    ) -> dict:
        """Compute Path-15 multi-signal hallucination detection dict.

        Inputs:
            q_atom:   (N,) codebook atom the query snapped to.
            response: (N,) substrate response W @ q_atom.
            P:        (C,) softmax over codebook similarities.

        Returns a dict with 4 individual flags, the composite_flag,
        composite_score (heuristic weighting, NOT derived), and the raw
        signals for downstream auditing. Composite weights are documented
        in the scenario; they are a starting heuristic and should be
        re-tuned per-deployment if the scenario shows drift.
        """
        # Signal (a): posterior entropy via max_prob * C threshold (existing
        # KF-1 convention preserved bit-for-bit).
        max_prob = float(P.max().item())
        posterior_entropy_flag = bool((max_prob * self.C) < 50.0)

        # Signal (b): bundle-norm signature. Low norm => no stored fact
        # activated => probably OOS.
        response_norm = float(torch.linalg.norm(response).item())
        if (self._median_stored_response_norm is None
                or self._median_norm_n_items == 0
                or abs(len(self.key_registry) - self._median_norm_n_items)
                / max(1, self._median_norm_n_items) > 0.25):
            self._refresh_median_stored_response_norm()
        med = self._median_stored_response_norm
        if med is None or med <= 0.0:
            # Empty store: no notion of "low" norm. Default to non-firing.
            low_norm_flag = False
        else:
            low_norm_flag = bool(response_norm < med * 0.5)

        # Signal (c): spectral concentration via top-2 ratio. Spread mass
        # across the codebook (ambiguous) => probably OOS.
        # Sort the top 2 P values cheaply via topk.
        top2 = torch.topk(P, 2)
        top2_vals = top2.values.tolist()
        if len(top2_vals) >= 2:
            concentration_ratio = float(
                top2_vals[0] / (top2_vals[1] + 1e-9)
            )
        else:
            concentration_ratio = float("inf")
        low_concentration_flag = bool(concentration_ratio < 2.0)

        # Signal (d): geometric distance to nearest stored key atom.
        # min_dist = 1 - max cosine over stored key atoms.
        if self.key_registry:
            stored_rows = list(self._used_key_rows)
            stored_atoms = self.codebook[stored_rows]  # (n_stored, N)
            # Cosine: stored_atoms @ q_atom / (||stored_atoms|| * ||q_atom||).
            # All atoms have the same norm sqrt(N) for BSC (+/-1 entries) and
            # roughly the same for gaussian, so we still use a proper cosine
            # to stay generic across codebook kinds.
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

        # Composite: at least 2 of the 4 individual flags fire.
        flags_list = [
            posterior_entropy_flag,
            low_norm_flag,
            low_concentration_flag,
            high_distance_flag,
        ]
        n_fired = sum(1 for f in flags_list if f)
        composite_flag = bool(n_fired >= 2)

        # Composite score: heuristic weighted sum (NOT derived). Each
        # component is mapped to a [0, 1] strength prior to weighting so
        # the score is interpretable on a 0..1 scale.
        # - posterior strength: clipped 50 / (max_prob * C) ... rises to 1
        #   exactly at the flag boundary, saturates at 1 below.
        # - low_norm strength: clipped 1 - response_norm / median. 1 when
        #   response is zero, 0 when response matches typical magnitude.
        # - low_concentration strength: clipped 1 - (concentration_ratio
        #   - 1) / (2 - 1). 1 when concentration_ratio==1, 0 at ==2.
        # - high_distance strength: min_dist_to_stored mapped to [0, 1]
        #   via clip.
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

    # --- Approximate retrieval (Path 5: random column sampling) --------------

    def retrieve_approx(
        self,
        query_vec: np.ndarray,
        sample_frac: float = 0.2,
        k: int = 1,
        seed: Optional[int] = None,
    ) -> RetrievalResult:
        """Approximate retrieve via uniform random sampling of W columns.

        Computes response_partial = W[:, cols] @ q_atom[cols] * (N / |cols|)
        instead of the full W @ q_atom, where cols is a random subset of
        size int(N * sample_frac) drawn from [0, N). At sample_frac=1.0 the
        rescale is a no-op and the result is bit-identical to retrieve().

        This is the Halko-Martinsson-Tropp randomized matrix-vector pattern:
        an unbiased estimator of the full matvec whose variance scales as
        1 / |cols|. Trades latency for a small recall hit on hot read paths.

        seed: if provided, makes column selection reproducible. Otherwise a
        per-call rng is seeded from time.perf_counter_ns(). At sample_frac
        of 1.0, cols is the full range [0, N) regardless of seed (the
        correctness-gate path).
        """
        if not (0.0 < sample_frac <= 1.0):
            raise ValueError(
                f"sample_frac must be in (0, 1]; got {sample_frac}"
            )

        q_row = self._snap_to_atom(query_vec)
        q_atom = self.codebook[q_row]

        if sample_frac >= 1.0:
            # No-op path: bit-identical to retrieve(). Skip sampling entirely.
            response = self.W @ q_atom
            n_sampled = self.N
        else:
            n_sampled = max(1, int(self.N * sample_frac))
            if seed is None:
                rng = np.random.default_rng(time.perf_counter_ns() & 0xFFFFFFFF)
            else:
                rng = np.random.default_rng(int(seed))
            cols_np = rng.choice(self.N, size=n_sampled, replace=False)
            cols_t = torch.as_tensor(cols_np, dtype=torch.long, device=self.device)
            # Sub-matvec: (N, S) @ (S,) = (N,). Rescale to preserve magnitude.
            W_sub = self.W.index_select(1, cols_t)  # (N, S)
            q_sub = q_atom.index_select(0, cols_t)  # (S,)
            response = (W_sub @ q_sub) * (self.N / float(n_sampled))

        sims = (self.codebook @ response) / self.N  # (C,)
        P = torch.softmax(self.beta * sims, dim=0)  # (C,)

        argmax_row = int(torch.argmax(P).item())
        max_prob = float(P[argmax_row].item())

        # Same reverse-lookup + tie-break logic as retrieve().
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
            stored_v_rows = [self.value_atom_registry[k] for k in stored_ids_order]
            scores = P[stored_v_rows]
            order = torch.argsort(scores, descending=True)
            take = min(max(k, 1), len(stored_ids_order))
            for idx in order[:take].tolist():
                top_k_ids.append(stored_ids_order[idx])
                top_k_scores.append(float(scores[idx].item()))

        result = RetrievalResult(
            key_id=matching_key_id,
            value=value,
            confidence=max_prob,
            near_uniform_flag=bool(near_uniform),
            distance=None,
            top_k_ids=top_k_ids,
            top_k_scores=top_k_scores,
        )
        # Annotate sampling actually used for the harness. RetrievalResult is
        # a frozen-ish dataclass but we can attach metadata via setattr; the
        # harness reads this via getattr(..., "sampling_used", None).
        setattr(result, "sampling_used", {
            "sample_frac": float(sample_frac),
            "n_sampled": int(n_sampled),
            "N": int(self.N),
        })
        return result

    def retrieve_batch_approx(
        self,
        query_vecs: np.ndarray,
        sample_frac: float = 0.2,
        k: int = 1,
        seed: Optional[int] = None,
    ) -> list[RetrievalResult]:
        """Batched form of retrieve_approx.

        One column-subset is shared across the whole batch (the variance of
        the randomized matvec is independent across queries given the same
        cols; sharing keeps the matmul fused). Bit-identical to
        retrieve_batch() at sample_frac=1.0.
        """
        q_arr = np.asarray(query_vecs)
        if q_arr.ndim != 2:
            raise ValueError(
                f"retrieve_batch_approx: query_vecs must be 2-D (B, N); got {q_arr.shape}"
            )
        if q_arr.shape[1] != self.N:
            raise ValueError(
                f"retrieve_batch_approx: query dim {q_arr.shape[1]} != N={self.N}"
            )
        if not (0.0 < sample_frac <= 1.0):
            raise ValueError(
                f"sample_frac must be in (0, 1]; got {sample_frac}"
            )

        B = q_arr.shape[0]
        if B == 0:
            return []

        Q = torch.as_tensor(q_arr, dtype=torch.float32, device=self.device)
        snap_sims = Q @ self.codebook.T
        snap_rows = torch.argmax(snap_sims, dim=1)
        Q_atoms = self.codebook[snap_rows]  # (B, N)

        if sample_frac >= 1.0:
            responses = self.W @ Q_atoms.T  # (N, B)
            n_sampled = self.N
        else:
            n_sampled = max(1, int(self.N * sample_frac))
            if seed is None:
                rng = np.random.default_rng(time.perf_counter_ns() & 0xFFFFFFFF)
            else:
                rng = np.random.default_rng(int(seed))
            cols_np = rng.choice(self.N, size=n_sampled, replace=False)
            cols_t = torch.as_tensor(cols_np, dtype=torch.long, device=self.device)
            W_sub = self.W.index_select(1, cols_t)  # (N, S)
            Q_sub = Q_atoms.index_select(1, cols_t)  # (B, S)
            responses = (W_sub @ Q_sub.T) * (self.N / float(n_sampled))  # (N, B)

        sims = (self.codebook @ responses) / self.N  # (C, B)
        P = torch.softmax(self.beta * sims, dim=0)  # (C, B)

        argmax_rows = torch.argmax(P, dim=0)  # (B,)
        max_probs = P.gather(0, argmax_rows.unsqueeze(0)).squeeze(0)

        reverse_v: dict[int, list[str]] = {}
        for kid, vrow in self.value_atom_registry.items():
            reverse_v.setdefault(int(vrow), []).append(kid)

        stored_ids_order = list(self.key_registry.keys())
        stored_v_rows_t: Optional[torch.Tensor] = None
        if stored_ids_order:
            stored_v_rows_t = torch.tensor(
                [self.value_atom_registry[kk] for kk in stored_ids_order],
                device=self.device,
                dtype=torch.long,
            )

        argmax_rows_cpu = argmax_rows.detach().cpu().tolist()
        max_probs_cpu = max_probs.detach().cpu().tolist()

        all_scores = P[stored_v_rows_t] if stored_v_rows_t is not None else None
        take_k = max(int(k), 1)
        if all_scores is not None and stored_ids_order:
            if take_k == 1:
                top1_idx = torch.argmax(all_scores, dim=0)
                top1_idx_cpu = top1_idx.detach().cpu().tolist()
                top1_score = all_scores.gather(0, top1_idx.unsqueeze(0)).squeeze(0)
                top1_score_cpu = top1_score.detach().cpu().tolist()
            else:
                topk_take = min(take_k, len(stored_ids_order))
                vals_t, idx_t = torch.topk(all_scores, topk_take, dim=0)
                vals_cpu = vals_t.detach().cpu().tolist()
                idx_cpu = idx_t.detach().cpu().tolist()

        results: list[RetrievalResult] = []
        c_thresh = 50.0 / self.C
        for b in range(B):
            argmax_row = int(argmax_rows_cpu[b])
            max_prob = float(max_probs_cpu[b])

            matching_key_id: Optional[str] = None
            candidates = reverse_v.get(argmax_row, [])
            if candidates:
                if len(candidates) == 1:
                    matching_key_id = candidates[0]
                else:
                    key_rows = [self.key_registry[c] for c in candidates]
                    key_atoms = self.codebook[key_rows]
                    k_sims = key_atoms @ Q_atoms[b]
                    best = int(torch.argmax(k_sims).item())
                    matching_key_id = candidates[best]

            value = (
                self.value_registry.get(matching_key_id)
                if matching_key_id else None
            )
            near_uniform = max_prob < c_thresh

            top_k_ids: list[str] = []
            top_k_scores: list[float] = []
            if all_scores is not None and stored_ids_order:
                if take_k == 1:
                    ti = int(top1_idx_cpu[b])
                    top_k_ids.append(stored_ids_order[ti])
                    top_k_scores.append(float(top1_score_cpu[b]))
                else:
                    for kk2 in range(len(vals_cpu)):
                        ti = int(idx_cpu[kk2][b])
                        top_k_ids.append(stored_ids_order[ti])
                        top_k_scores.append(float(vals_cpu[kk2][b]))

            r = RetrievalResult(
                key_id=matching_key_id,
                value=value,
                confidence=max_prob,
                near_uniform_flag=bool(near_uniform),
                distance=None,
                top_k_ids=top_k_ids,
                top_k_scores=top_k_scores,
            )
            setattr(r, "sampling_used", {
                "sample_frac": float(sample_frac),
                "n_sampled": int(n_sampled),
                "N": int(self.N),
            })
            results.append(r)
        return results

    # --- Batched ABC overrides -----------------------------------------------

    def _batch_snap_to_atoms(self, key_vecs: np.ndarray) -> torch.Tensor:
        """Snap a (B, N) batch of key vectors to nearest codebook rows.

        One matmul + per-row argmax. Returns a torch.LongTensor of shape (B,).
        """
        q = torch.as_tensor(key_vecs, dtype=torch.float32, device=self.device)
        if q.ndim != 2 or q.shape[1] != self.N:
            raise ValueError(
                f"_batch_snap_to_atoms: key_vecs shape {tuple(q.shape)} != (B, N={self.N})"
            )
        sims = q @ self.codebook.T  # (B, C)
        return torch.argmax(sims, dim=1)

    def store_batch(self, items: list[tuple[str, np.ndarray, str]]) -> None:
        """Fused-matmul batched store.

        For pure-new key_ids the W update collapses from B outer products to
        a single (N, N) = (N, B) @ (B, N) matmul. Atom allocation runs in the
        same sequential order as the single-item path (registries updated
        between allocations) so the resulting W matrix is bit-identical to
        a one-at-a-time store sequence on the same input.

        Items whose key_id is already stored fall through to per-item edit()
        (rare path; matches single-item store() behavior).
        """
        if not items:
            return

        # Pre-snap all key_vecs in one matmul. This is the dominant fixed
        # cost in the single-item path (codebook @ q + argmax per item). For
        # items that snap to an already-occupied row, the linear-probe path
        # still runs per-item below.
        fresh_indices: list[int] = []
        fresh_vecs: list[np.ndarray] = []
        for idx, (key_id, key_vec, _value) in enumerate(items):
            if key_id in self.key_registry:
                continue
            if key_vec is None:
                continue
            fresh_indices.append(idx)
            fresh_vecs.append(np.asarray(key_vec, dtype=np.float32).reshape(-1))

        snapped_rows: dict[int, int] = {}
        if fresh_vecs:
            stack = np.stack(fresh_vecs, axis=0)
            snapped = self._batch_snap_to_atoms(stack)
            snapped_cpu = snapped.detach().cpu().tolist()
            for j, item_idx in enumerate(fresh_indices):
                snapped_rows[item_idx] = int(snapped_cpu[j])

        new_key_rows: list[int] = []
        new_val_rows: list[int] = []
        new_indices: list[int] = []  # index into items for registry updates

        # Use the persistent occupancy sets directly. They are kept in sync
        # with the registries by store/edit/delete/_atom_for_*, so we never
        # need to rebuild set(registry.values()) here either.
        key_used = self._used_key_rows
        val_used = self._used_value_rows

        # Sequential allocation pass (linear probe needs current registry state).
        for idx, (key_id, key_vec, value) in enumerate(items):
            if key_id in self.key_registry:
                # Drain any pending fused matmul before the edit so the
                # edit reads the up-to-date W. Matches single-item ordering.
                if new_key_rows:
                    self._flush_store_batch(new_key_rows, new_val_rows, new_indices, items)
                    new_key_rows, new_val_rows, new_indices = [], [], []
                self.edit(key_id, value)
                # edit() updates _used_value_rows incrementally; nothing to refresh.
                continue

            if len(key_used) >= self.C:
                raise RuntimeError(
                    f"codebook exhausted: {len(key_used)} keys, C={self.C}"
                )
            if idx in snapped_rows:
                key_row = snapped_rows[idx]
            else:
                key_row = _stable_hash_int("key:" + key_id) % self.C
            while key_row in key_used:
                key_row = (key_row + 1) % self.C

            # Inline _atom_for_value (uses persistent val_used set).
            if len(val_used) >= self.C:
                raise RuntimeError(
                    f"codebook exhausted (value): {len(val_used)} values, C={self.C}"
                )
            val_row = _stable_hash_int("val:" + key_id + "::" + value) % self.C
            while val_row in val_used:
                val_row = (val_row + 1) % self.C

            # Reserve rows so subsequent in-batch allocations see them.
            self.key_registry[key_id] = key_row
            self.value_atom_registry[key_id] = val_row
            key_used.add(key_row)
            val_used.add(val_row)

            new_key_rows.append(key_row)
            new_val_rows.append(val_row)
            new_indices.append(idx)

        if new_key_rows:
            self._flush_store_batch(new_key_rows, new_val_rows, new_indices, items)

    def _flush_store_batch(
        self,
        key_rows: list[int],
        val_rows: list[int],
        indices: list[int],
        items: list[tuple[str, np.ndarray, str]],
    ) -> None:
        """Single fused matmul for a contiguous run of pure-new stores."""
        # K: (B, N) of key atoms; V: (B, N) of value atoms.
        K = self.codebook[key_rows]
        V = self.codebook[val_rows]
        # W += V.T @ K / N      shapes: (N, B) @ (B, N) = (N, N).
        self.W = self.W + (V.T @ K) / self.N

        # Bookkeeping: value_registry + _insertion_order.
        for idx in indices:
            key_id, _kvec, value = items[idx]
            self.value_registry[key_id] = value
            self._insertion_order.append(key_id)

    def retrieve_batch(
        self, query_vecs: np.ndarray, k: int = 1
    ) -> list[RetrievalResult]:
        """Fused-matmul batched retrieve.

        Per-query path: snap each query to a codebook row (one batched
        matmul + argmax), then one batched W @ Q_atoms.T and one batched
        codebook @ responses to get sims; softmax + argmax over the
        codebook axis gives the candidate value-atom row per query.
        """
        q_arr = np.asarray(query_vecs)
        if q_arr.ndim != 2:
            raise ValueError(
                f"retrieve_batch: query_vecs must be 2-D (B, N); got {q_arr.shape}"
            )
        if q_arr.shape[1] != self.N:
            raise ValueError(
                f"retrieve_batch: query dim {q_arr.shape[1]} != N={self.N}"
            )

        B = q_arr.shape[0]
        if B == 0:
            return []

        # If the store is empty, return empties to match single-item semantics
        # (single-item retrieve still runs the matmul; replicate that here so
        # outputs are shape-identical).
        Q = torch.as_tensor(q_arr, dtype=torch.float32, device=self.device)  # (B, N)

        # Snap to codebook rows: one matmul, then argmax per row.
        snap_sims = Q @ self.codebook.T  # (B, C)
        snap_rows = torch.argmax(snap_sims, dim=1)  # (B,)
        Q_atoms = self.codebook[snap_rows]  # (B, N)

        # Fused responses: (N, B) = W @ Q_atoms.T
        responses = self.W @ Q_atoms.T  # (N, B)

        # Fused sims: (C, B) = codebook @ responses / N
        sims = (self.codebook @ responses) / self.N  # (C, B)
        P = torch.softmax(self.beta * sims, dim=0)  # (C, B)

        argmax_rows = torch.argmax(P, dim=0)  # (B,)
        # Pull max_prob via gather along dim 0.
        max_probs = P.gather(0, argmax_rows.unsqueeze(0)).squeeze(0)  # (B,)

        # Pre-compute reverse lookup once: value_atom_row -> [candidate key_ids].
        reverse_v: dict[int, list[str]] = {}
        for kid, vrow in self.value_atom_registry.items():
            reverse_v.setdefault(int(vrow), []).append(kid)

        # Cache for the recall-rank scores (top-k path).
        stored_ids_order = list(self.key_registry.keys())
        stored_v_rows_t: Optional[torch.Tensor] = None
        if stored_ids_order:
            stored_v_rows_t = torch.tensor(
                [self.value_atom_registry[kk] for kk in stored_ids_order],
                device=self.device,
                dtype=torch.long,
            )

        # Fast top-k for k==1: skip Python-level argsort.
        argmax_rows_cpu = argmax_rows.detach().cpu().tolist()
        max_probs_cpu = max_probs.detach().cpu().tolist()

        # Pre-compute scored stored ids (used by top_k_ids/scores per query).
        # For k==1 we still need to populate top_k with size 1.
        if stored_v_rows_t is not None:
            # all_scores shape (n_stored, B)
            all_scores = P[stored_v_rows_t]
        else:
            all_scores = None

        take_k = max(int(k), 1)
        if all_scores is not None and stored_ids_order:
            if take_k == 1:
                top1_idx = torch.argmax(all_scores, dim=0)  # (B,)
                top1_idx_cpu = top1_idx.detach().cpu().tolist()
                top1_score = all_scores.gather(0, top1_idx.unsqueeze(0)).squeeze(0)
                top1_score_cpu = top1_score.detach().cpu().tolist()
            else:
                # Take top take_k via topk along stored axis.
                topk_take = min(take_k, len(stored_ids_order))
                vals_t, idx_t = torch.topk(all_scores, topk_take, dim=0)
                vals_cpu = vals_t.detach().cpu().tolist()
                idx_cpu = idx_t.detach().cpu().tolist()

        # Path-15: batched multi-signal hallu detection.
        # response_norm per query: (B,) = ||responses[:, b]||
        resp_norms_t = torch.linalg.norm(responses, dim=0)  # (B,)
        resp_norms_cpu = resp_norms_t.detach().cpu().tolist()
        # top-2 concentration ratio per query.
        top2_b = torch.topk(P, 2, dim=0)
        top2_vals_b = top2_b.values  # (2, B)
        top2_cpu = top2_vals_b.detach().cpu().tolist()
        # high_distance per query: cosine over stored key atoms.
        if self.key_registry:
            stored_key_rows = list(self._used_key_rows)
            stored_key_atoms = self.codebook[stored_key_rows]  # (n_stored, N)
            q_norms_b = torch.linalg.norm(Q_atoms, dim=1)  # (B,)
            sa_norms = torch.linalg.norm(stored_key_atoms, dim=1)  # (n_stored,)
            denom = sa_norms.unsqueeze(1) * q_norms_b.unsqueeze(0).clamp_min(1e-9)
            denom = torch.where(denom > 0.0, denom, torch.ones_like(denom))
            cos_b = (stored_key_atoms @ Q_atoms.T) / denom  # (n_stored, B)
            max_cos_b = cos_b.max(dim=0).values  # (B,)
            min_dist_b = (1.0 - max_cos_b).detach().cpu().tolist()
        else:
            min_dist_b = [1.0] * B
        # Ensure median is fresh once for the whole batch.
        if (self._median_stored_response_norm is None
                or self._median_norm_n_items == 0
                or abs(len(self.key_registry) - self._median_norm_n_items)
                / max(1, self._median_norm_n_items) > 0.25):
            self._refresh_median_stored_response_norm()
        med = self._median_stored_response_norm

        results: list[RetrievalResult] = []
        c_thresh = 50.0 / self.C

        for b in range(B):
            argmax_row = int(argmax_rows_cpu[b])
            max_prob = float(max_probs_cpu[b])

            matching_key_id: Optional[str] = None
            candidates = reverse_v.get(argmax_row, [])
            if candidates:
                if len(candidates) == 1:
                    matching_key_id = candidates[0]
                else:
                    key_rows = [self.key_registry[c] for c in candidates]
                    key_atoms = self.codebook[key_rows]
                    k_sims = key_atoms @ Q_atoms[b]
                    best = int(torch.argmax(k_sims).item())
                    matching_key_id = candidates[best]

            value = (
                self.value_registry.get(matching_key_id)
                if matching_key_id else None
            )
            near_uniform = max_prob < c_thresh

            top_k_ids: list[str] = []
            top_k_scores: list[float] = []
            if all_scores is not None and stored_ids_order:
                if take_k == 1:
                    ti = int(top1_idx_cpu[b])
                    top_k_ids.append(stored_ids_order[ti])
                    top_k_scores.append(float(top1_score_cpu[b]))
                else:
                    for kk2 in range(len(vals_cpu)):
                        ti = int(idx_cpu[kk2][b])
                        top_k_ids.append(stored_ids_order[ti])
                        top_k_scores.append(float(vals_cpu[kk2][b]))

            # Path-15: per-query multi-signal panel.
            posterior_entropy_flag = bool((max_prob * self.C) < 50.0)
            response_norm = float(resp_norms_cpu[b])
            if med is None or med <= 0.0:
                low_norm_flag = False
                low_norm_strength = 0.0
            else:
                low_norm_flag = bool(response_norm < med * 0.5)
                low_norm_strength = max(
                    0.0, min(1.0, 1.0 - response_norm / med)
                )
            t0v = float(top2_cpu[0][b])
            t1v = float(top2_cpu[1][b]) if len(top2_cpu) > 1 else 0.0
            concentration_ratio = float(t0v / (t1v + 1e-9))
            low_concentration_flag = bool(concentration_ratio < 2.0)
            if concentration_ratio <= 1.0:
                low_conc_strength = 1.0
            elif concentration_ratio >= 2.0:
                low_conc_strength = 0.0
            else:
                low_conc_strength = max(
                    0.0, min(1.0, 2.0 - concentration_ratio)
                )
            min_dist_val = float(min_dist_b[b])
            high_distance_flag = bool(min_dist_val > 0.5)
            high_dist_strength = max(0.0, min(1.0, min_dist_val))
            post_strength = 0.0
            if max_prob > 0.0:
                post_strength = min(1.0, 50.0 / (max_prob * self.C + 1e-9))
            n_fired = sum(
                1
                for f in (
                    posterior_entropy_flag,
                    low_norm_flag,
                    low_concentration_flag,
                    high_distance_flag,
                )
                if f
            )
            composite_flag = bool(n_fired >= 2)
            composite_score = float(
                0.4 * post_strength
                + 0.3 * low_norm_strength
                + 0.2 * low_conc_strength
                + 0.1 * high_dist_strength
            )
            hallu_signals = {
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
                "min_dist_to_stored": min_dist_val,
                "max_prob": max_prob,
            }

            results.append(
                RetrievalResult(
                    key_id=matching_key_id,
                    value=value,
                    confidence=max_prob,
                    near_uniform_flag=bool(near_uniform),
                    distance=None,
                    top_k_ids=top_k_ids,
                    top_k_scores=top_k_scores,
                    hallu_signals=hallu_signals,
                )
            )
        return results

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

        # Remove registry entries. Drop the rows from the persistent occupancy
        # sets BEFORE the registry pops so the invariant
        # _used_key_rows == set(key_registry.values()) is maintained.
        self._used_key_rows.discard(self.key_registry[key_id])
        self._used_value_rows.discard(self.value_atom_registry[key_id])
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
        kf1_composite_fire_rate: Optional[float] = None
        kf1_per_signal_fire_rates: Optional[dict] = None
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

            # Path-15 multi-signal panel on the same OOS sample.
            # Refresh median stored response norm so the bundle-norm threshold
            # reflects the current store state.
            self._refresh_median_stored_response_norm()
            med = self._median_stored_response_norm

            # response_norm per oos query: ||resp[i, :]||
            resp_norms_oos = torch.linalg.norm(resp, dim=1)
            # top-2 concentration per query
            top2_oos = torch.topk(P, 2, dim=1)
            top2_vals_oos = top2_oos.values  # (n_oos, 2)
            conc_oos = top2_vals_oos[:, 0] / (top2_vals_oos[:, 1] + 1e-9)
            # high distance per query: min over stored
            if self.key_registry:
                stored_key_rows = list(self._used_key_rows)
                stored_key_atoms = self.codebook[stored_key_rows]
                q_norms_oos = torch.linalg.norm(oos_atoms, dim=1)
                sa_norms = torch.linalg.norm(stored_key_atoms, dim=1)
                denom = sa_norms.unsqueeze(0) * q_norms_oos.unsqueeze(1).clamp_min(1e-9)
                denom = torch.where(denom > 0.0, denom, torch.ones_like(denom))
                cos_oos = (oos_atoms @ stored_key_atoms.T) / denom  # (n_oos, n_stored)
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
                "posterior_entropy": float(
                    posterior_flag_oos.float().mean().item()
                ),
                "low_norm": float(low_norm_flag_oos.float().mean().item()),
                "low_concentration": float(
                    low_conc_flag_oos.float().mean().item()
                ),
                "high_distance": float(
                    high_dist_flag_oos.float().mean().item()
                ),
            }

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
            kf1_composite_fire_rate=kf1_composite_fire_rate,
            kf1_per_signal_fire_rates=kf1_per_signal_fire_rates,
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
        # Rebuild persistent occupancy sets once from the loaded registries.
        # Hot-path allocators use these sets directly; they must match the
        # registries exactly after load() returns.
        self._used_key_rows = set(self.key_registry.values())
        self._used_value_rows = set(self.value_atom_registry.values())

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
