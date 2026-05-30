"""CachedSubstrate: read-through cache atop SubstrateMemory.

Goal (per Tier 2 Test T4 user spec):
  - Hot queries below 1 ms (FAISS-competitive).
  - Cache hit rate above 80 percent on realistic Zipfian workloads.
  - Cached results verifiable against substrate state at the time of caching
    (audit chain integrity preserved).

Mechanism:
  - Cache is keyed by the codebook-row index that query_vec snaps to.
    Reason: substrate retrieve() is invariant to anything but the snapped
    atom; two queries that snap to the same row produce identical results
    for a fixed W. The atom-row hash is a CHEAP exact identity check.
  - Cache value is (RetrievalResult, w_version_at_cache_time).
  - Each store/edit/delete bumps self._w_version (uint64 counter). The
    expensive SHA256 audit chain on actual W bytes stays in place for the
    deletion certificate path; the version counter is an O(1) cache-side
    fence ONLY.
  - On retrieve(): snap to atom row, look up cache. If hit AND cached
    w_version == self._w_version, return cached result; else fall through
    to substrate retrieve() and store (result, w_version) under the atom
    row. Bounded LRU eviction.

Audit-integrity property (LOAD-BEARING):
  A cache hit returns the same RetrievalResult that the substrate would
  have returned at w_version_at_cache_time. The substrate operation log
  is the authoritative reconstruction of w_version. Cached responses
  satisfy: cache_response == substrate_response(at w_version=v).
  Verification happens in audit(): for a sample of cached entries, we
  re-run the substrate retrieve at current w_version on a clone, and
  compare key_id + value. Mismatches mark cache_audit_passes=False and
  surface n_cache_audit_failures in the AuditReport's config dict.

Configuration (cached subdict of harness/CLI config):
  cache_size: int (default 1000) - max number of entries before LRU eviction
  eviction_policy: "lru" (default; only "lru" supported in v1)

This file is ASCII only. No em-dashes.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import numpy as np
import torch

from testbed.api import AuditReport, DeletionCertificate, RetrievalResult
from testbed.substrate_memory import SubstrateMemory


class CachedSubstrate(SubstrateMemory):
    """SubstrateMemory plus a bounded LRU read-through cache.

    All mutating ops (store/edit/delete) bump a uint64 version counter; the
    cache binds each cached result to the version at insert time so any
    later W-mutation is naturally invalidated on the next lookup. The
    explicit pop-style invalidation on edit/delete is the dominant path
    (cheap O(1) cache.clear() per mutation); version check is the
    defense-in-depth guard for state-restore / load paths.
    """

    name = "substrate_cached"

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
        cache_size: int = 1000,
        eviction_policy: str = "lru",
    ) -> None:
        super().__init__(
            N=N,
            codebook_kind=codebook_kind,
            codebook_scale=codebook_scale,
            beta=beta,
            hallu_threshold=hallu_threshold,
            device=device,
            seed=seed,
            codebook_M_hint=codebook_M_hint,
        )
        if cache_size <= 0:
            raise ValueError(f"cache_size must be > 0, got {cache_size}")
        if eviction_policy != "lru":
            raise ValueError(
                f"only 'lru' eviction is supported in v1, got {eviction_policy!r}"
            )
        self.cache_size = int(cache_size)
        self.eviction_policy = eviction_policy

        # Cache: ordered dict atom_row -> (RetrievalResult, w_version).
        # OrderedDict gives O(1) LRU promotion via move_to_end.
        self._cache: "OrderedDict[int, tuple[RetrievalResult, int]]" = OrderedDict()

        # uint64 monotonic version counter. Bumped on every W-mutation entry
        # point (store, edit, delete, store_batch). Reset to 0 on __init__
        # so a fresh substrate starts at version 0.
        self._w_version: int = 0

        # Stats for audit panel.
        self._n_hits: int = 0
        self._n_misses: int = 0
        self._n_invalidations: int = 0
        self._n_evictions: int = 0
        self._last_invalidation_version: int = 0

    # --- internal cache helpers ----------------------------------------------

    def _bump_version_and_invalidate(self) -> None:
        """Increment w_version and clear cache.

        Cheap O(cache_size) clear; the alternative (keep-and-version-check
        on retrieve) is also correct but produces stale-flagged misses that
        we'd evict on the next access anyway. Explicit clear keeps the
        cache compact and avoids occupying LRU slots with dead entries.
        """
        self._w_version = (self._w_version + 1) & 0xFFFFFFFFFFFFFFFF
        if self._cache:
            self._n_invalidations += 1
            self._last_invalidation_version = self._w_version
            self._cache.clear()

    def _cache_get(self, atom_row: int) -> Optional[RetrievalResult]:
        entry = self._cache.get(atom_row)
        if entry is None:
            return None
        result, cached_version = entry
        # Defense in depth: even if invalidate-on-mutate is bypassed
        # somehow (state restore, load), version mismatch rejects.
        if cached_version != self._w_version:
            # Stale: drop it.
            self._cache.pop(atom_row, None)
            return None
        # LRU touch.
        self._cache.move_to_end(atom_row)
        return result

    def _cache_put(self, atom_row: int, result: RetrievalResult) -> None:
        self._cache[atom_row] = (result, self._w_version)
        self._cache.move_to_end(atom_row)
        while len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)
            self._n_evictions += 1

    # --- ABC overrides --------------------------------------------------------

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        # Bump version + invalidate BEFORE the W mutation so any concurrent
        # cache read in a debugger / observer sees the not-yet-mutated
        # state with a fresh empty cache. Sequential single-threaded users
        # see the same result either way.
        self._bump_version_and_invalidate()
        super().store(key_id, key_vec, value)

    def store_batch(self, items: list[tuple[str, np.ndarray, str]]) -> None:
        if not items:
            return
        self._bump_version_and_invalidate()
        super().store_batch(items)

    def edit(self, key_id: str, new_value: str) -> None:
        self._bump_version_and_invalidate()
        super().edit(key_id, new_value)

    def delete(self, key_id: str) -> DeletionCertificate:
        self._bump_version_and_invalidate()
        return super().delete(key_id)

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        # We need the snapped atom row. _snap_to_atom does the same matmul
        # the parent uses, so we pay it once here and the parent path also
        # pays it on miss. That's roughly a 2x cost for the snap on miss
        # only; for hits the parent path is skipped entirely.
        # For k > 1, do NOT cache: top-k results are query-frequency-rare
        # in our workload and the cache value would be size-variant.
        if k != 1:
            self._n_misses += 1
            return super().retrieve(query_vec, k=k)

        atom_row = self._snap_to_atom(query_vec)
        cached = self._cache_get(atom_row)
        if cached is not None:
            self._n_hits += 1
            return cached
        self._n_misses += 1
        # Compute via parent path.
        result = super().retrieve(query_vec, k=1)
        self._cache_put(atom_row, result)
        return result

    def retrieve_batch(
        self, query_vecs: np.ndarray, k: int = 1
    ) -> list[RetrievalResult]:
        # Batched cache: hit-or-miss per row. On miss we still need to run
        # the substrate matmul on the miss subset; for simplicity and to
        # keep latency-vs-cache-rate analysis clean, we delegate misses to
        # the parent's batched path on the miss-subset.
        q_arr = np.asarray(query_vecs)
        if q_arr.ndim != 2:
            raise ValueError(
                f"retrieve_batch: query_vecs must be 2-D (B, N); got {q_arr.shape}"
            )
        if q_arr.shape[1] != self.N:
            raise ValueError(
                f"retrieve_batch: query dim {q_arr.shape[1]} != N={self.N}"
            )
        if k != 1:
            # No batched cache for top-k > 1; fall through to parent.
            self._n_misses += int(q_arr.shape[0])
            return super().retrieve_batch(q_arr, k=k)

        B = int(q_arr.shape[0])
        if B == 0:
            return []

        # One batched snap, then per-query cache lookup.
        Q = torch.as_tensor(q_arr, dtype=torch.float32, device=self.device)
        snap_sims = Q @ self.codebook.T
        snap_rows_t = torch.argmax(snap_sims, dim=1)
        snap_rows = snap_rows_t.detach().cpu().tolist()

        results: list[Optional[RetrievalResult]] = [None] * B
        miss_indices: list[int] = []
        miss_queries: list[np.ndarray] = []
        for b in range(B):
            row = int(snap_rows[b])
            cached = self._cache_get(row)
            if cached is not None:
                results[b] = cached
                self._n_hits += 1
            else:
                miss_indices.append(b)
                miss_queries.append(q_arr[b])
                self._n_misses += 1

        if miss_queries:
            miss_arr = np.stack(miss_queries, axis=0)
            miss_results = super().retrieve_batch(miss_arr, k=1)
            for j, b in enumerate(miss_indices):
                results[b] = miss_results[j]
                # Cache by snap row, not by raw query.
                self._cache_put(int(snap_rows[b]), miss_results[j])

        # All results are populated by construction.
        return [r for r in results if r is not None]

    # --- audit ----------------------------------------------------------------

    def _verify_cache_consistency(self, max_check: int = 8) -> tuple[bool, int]:
        """Verify a sample of cached results match a fresh substrate retrieve.

        Returns (cache_audit_passes, n_failures). On any failure, returns
        False + the count of mismatched entries. Up to max_check entries
        are checked (cheap audit).
        """
        if not self._cache:
            return True, 0
        # Sample up to max_check most-recent entries.
        sample = list(self._cache.items())[-max_check:]
        failures = 0
        for atom_row, (cached_result, cached_version) in sample:
            # Build the codebook atom and run the un-cached substrate path.
            atom = self.codebook[atom_row].detach().cpu().numpy()
            fresh = SubstrateMemory.retrieve(self, atom, k=1)
            if fresh.key_id != cached_result.key_id:
                failures += 1
                continue
            if fresh.value != cached_result.value:
                failures += 1
                continue
            # Confidence may drift in float ULPs; compare with tolerance.
            if cached_version == self._w_version:
                # No mutations since cache: confidence must be exact.
                if abs(fresh.confidence - cached_result.confidence) > 1e-6:
                    failures += 1
        return (failures == 0), failures

    def audit(
        self,
        n_oos: int = 256,
        n_edit: int = 16,
        n_delete: int = 16,
    ) -> AuditReport:
        rep = super().audit(n_oos=n_oos, n_edit=n_edit, n_delete=n_delete)
        # Cache panel: extend AuditReport.config with cache stats.
        cache_audit_passes, n_cache_audit_failures = self._verify_cache_consistency()
        total = self._n_hits + self._n_misses
        hit_rate = float(self._n_hits / total) if total > 0 else 0.0
        cache_stats = {
            "cache_size_current": int(len(self._cache)),
            "cache_size_max": int(self.cache_size),
            "n_hits": int(self._n_hits),
            "n_misses": int(self._n_misses),
            "hit_rate_since_init": hit_rate,
            "n_invalidations": int(self._n_invalidations),
            "n_evictions": int(self._n_evictions),
            "last_invalidation_version": int(self._last_invalidation_version),
            "current_w_version": int(self._w_version),
            "cache_audit_passes": bool(cache_audit_passes),
            "n_cache_audit_failures": int(n_cache_audit_failures),
        }
        # Merge into the existing config dict (non-destructive).
        merged = dict(rep.config) if rep.config else {}
        merged["cache"] = cache_stats
        # Build a new AuditReport with merged config; AuditReport is a
        # dataclass so we re-construct it.
        return AuditReport(
            backend=rep.backend,
            n_items=rep.n_items,
            kf1_above_thresh_frac=rep.kf1_above_thresh_frac,
            kf1_mean_oos_max_conf=rep.kf1_mean_oos_max_conf,
            kf2_max_isolation=rep.kf2_max_isolation,
            tcft_mean_var_ratio=rep.tcft_mean_var_ratio,
            storage_bytes=rep.storage_bytes,
            config=merged,
            kf1_composite_fire_rate=rep.kf1_composite_fire_rate,
            kf1_per_signal_fire_rates=rep.kf1_per_signal_fire_rates,
        )

    # --- persistence ----------------------------------------------------------

    def save(self, path: Path) -> None:
        """Persist substrate state plus cache state.

        Cache is serialized as a list of (atom_row, key_id, value,
        confidence, near_uniform_flag, w_version). RetrievalResult.top_k
        and hallu_signals are dropped on save to keep the file compact;
        on reload they re-populate naturally on the next retrieve miss.
        """
        super().save(path)
        path = Path(path)
        import json
        cache_blob = {
            "w_version": int(self._w_version),
            "n_hits": int(self._n_hits),
            "n_misses": int(self._n_misses),
            "n_invalidations": int(self._n_invalidations),
            "n_evictions": int(self._n_evictions),
            "last_invalidation_version": int(self._last_invalidation_version),
            "cache_size": int(self.cache_size),
            "eviction_policy": str(self.eviction_policy),
            "entries": [
                {
                    "atom_row": int(row),
                    "key_id": r.key_id,
                    "value": r.value,
                    "confidence": float(r.confidence),
                    "near_uniform_flag": bool(r.near_uniform_flag),
                    "w_version": int(v),
                }
                for row, (r, v) in self._cache.items()
            ],
        }
        with open(path / "cache.json", "w", encoding="utf-8") as f:
            json.dump(cache_blob, f, indent=2)

    def load(self, path: Path) -> None:
        super().load(path)
        path = Path(path)
        cache_file = path / "cache.json"
        # Reset cache state to defaults; only override from file if present.
        self._cache = OrderedDict()
        self._n_hits = 0
        self._n_misses = 0
        self._n_invalidations = 0
        self._n_evictions = 0
        self._last_invalidation_version = 0
        self._w_version = 0
        if not cache_file.exists():
            return
        import json
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                blob = json.load(f)
        except (OSError, ValueError):
            return
        self._w_version = int(blob.get("w_version", 0))
        self._n_hits = int(blob.get("n_hits", 0))
        self._n_misses = int(blob.get("n_misses", 0))
        self._n_invalidations = int(blob.get("n_invalidations", 0))
        self._n_evictions = int(blob.get("n_evictions", 0))
        self._last_invalidation_version = int(
            blob.get("last_invalidation_version", 0)
        )
        # cache_size and eviction_policy already set by __init__.
        for entry in blob.get("entries", []):
            row = int(entry["atom_row"])
            r = RetrievalResult(
                key_id=entry.get("key_id"),
                value=entry.get("value"),
                confidence=float(entry.get("confidence", 0.0)),
                near_uniform_flag=bool(entry.get("near_uniform_flag", False)),
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
                hallu_signals=None,
            )
            v = int(entry.get("w_version", self._w_version))
            self._cache[row] = (r, v)


if __name__ == "__main__":
    # Tiny self-test: hit/miss/edit/delete behavior.
    mem = CachedSubstrate(
        N=128, codebook_kind="bsc", codebook_scale=4, beta=32.0,
        seed=7, cache_size=32,
    )
    M = 16
    for i in range(M):
        kid = f"k_{i}"
        row = mem._atom_for_key_id(kid)
        kvec = mem.codebook[row].detach().cpu().numpy()
        mem.store(kid, kvec, f"v_{i}")

    # Each store bumped version + invalidated cache; cache empty.
    assert len(mem._cache) == 0, "cache should be empty after stores"

    # First retrieve: miss.
    row = mem._atom_for_key_id("k_3")
    qvec = mem.codebook[row].detach().cpu().numpy()
    r1 = mem.retrieve(qvec)
    assert r1.key_id == "k_3", f"got {r1.key_id}"
    assert mem._n_hits == 0 and mem._n_misses == 1

    # Second retrieve: hit.
    r2 = mem.retrieve(qvec)
    assert r2.key_id == "k_3"
    assert mem._n_hits == 1 and mem._n_misses == 1

    # Edit invalidates cache.
    mem.edit("k_3", "new_v_3")
    r3 = mem.retrieve(qvec)
    assert r3.value == "new_v_3", f"got {r3.value}"
    assert mem._n_misses == 2

    # Audit gate.
    rep = mem.audit(n_oos=16, n_edit=4, n_delete=4)
    cache_stats = rep.config.get("cache") or {}
    assert cache_stats.get("cache_audit_passes"), cache_stats
    print(f"cached_substrate self-test OK: hits={mem._n_hits} misses={mem._n_misses}")
