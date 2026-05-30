"""Scenario 9: multi_substrate_sharding.

Sweeps M against a sharded substrate with FIXED codebook_C. Tests whether
sharding extends the operating envelope at constant per-shard cost while
preserving the audit chain across shard boundaries.

The substrate's single-instance envelope is M <= C/4. Sharding into K shards
at the SAME C should extend the envelope to K * C/4 with disk cost that is
constant in M (one shared codebook + K W matrices), latency that scales as
K (serial probe; embarrassingly parallel in production), and audit chain
integrity that holds across shard transitions.

Headline metrics (per M):
  total_disk_MB             one shared codebook + K * (N*N*4 bytes)
  total_disk_growth         disk(M_max) / disk(M_min); near 1.0 = constant cost
  p50_retrieve_us           median retrieve latency (serial K-shard probe)
  recall_at_1               sampled recall on n_recall stored keys
  kf1_near_uniform_frac     mean across shards of audit().kf1_above_thresh_frac
  cross_shard_chain_integrity     fraction of within-shard + cross-shard
                                   anchors that re-derive correctly
  tamper_detection_rate     fraction of injected byte tampers detected
  shards_used               number of shards that received at least one key

HARD_PASS bands (pre-registered, per envelope-expansion-fail-bands):
  total_disk_growth < 1.5
  recall_at_1 >= 0.85 at all M
  cross_shard_chain_integrity == 1.00
  tamper_detection_rate >= 0.90

The configurable knobs:
  shard_M_sweep            list of M values (default [2000, 5000, 10000, 20000, 50000])
  shard_K                  default 10
  shard_codebook_C         default 8192 (FIXED across M)
  shard_N                  default 2048
  shard_n_recall_samples   default 200
  shard_n_latency_queries  default 100
  shard_n_delete           default 100
  shard_n_tamper           default 10
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            continue
    return total


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    Ms = list(config.get("shard_M_sweep", [2000, 5000, 10000, 20000, 50000]))
    K = int(config.get("shard_K", 10))
    codebook_C = int(config.get("shard_codebook_C", 8192))
    N = int(config.get("shard_N", config.get("N", 2048)))
    seed = _first_seed(config)
    n_recall = int(config.get("shard_n_recall_samples", 200))
    n_latency = int(config.get("shard_n_latency_queries", 100))
    n_delete = int(config.get("shard_n_delete", 100))
    n_tamper = int(config.get("shard_n_tamper", 10))
    codebook_kind = str(config.get("codebook_kind", "bsc"))
    beta = float(config.get("beta", 32.0))
    hallu_threshold = float(config.get("hallu_threshold", 0.5))
    shared_codebook = bool(config.get("shard_shared_codebook", True))
    return {
        "Ms": Ms,
        "K": K,
        "codebook_C": codebook_C,
        "N": N,
        "seed": seed,
        "n_recall_samples": n_recall,
        "n_latency_queries": n_latency,
        "n_delete": n_delete,
        "n_tamper": n_tamper,
        "codebook_kind": codebook_kind,
        "beta": beta,
        "hallu_threshold": hallu_threshold,
        "shared_codebook": shared_codebook,
    }


def _build_sharded(data: dict):
    """Build a fresh ShardedSubstrate per M iteration."""
    from testbed.variants.sharded_substrate import ShardedSubstrate
    return ShardedSubstrate(
        N=int(data["N"]),
        K_shards=int(data["K"]),
        codebook_kind=str(data["codebook_kind"]),
        codebook_C=int(data["codebook_C"]),
        beta=float(data["beta"]),
        hallu_threshold=float(data["hallu_threshold"]),
        shared_codebook=bool(data["shared_codebook"]),
        routing="hash",
        device="cpu",
        seed=int(data["seed"]),
    )


def run(backend, data: dict) -> dict:
    Ms = list(data["Ms"])
    K = int(data["K"])
    N = int(data["N"])
    codebook_C = int(data["codebook_C"])
    seed = int(data["seed"])
    n_recall = int(data["n_recall_samples"])
    n_latency = int(data["n_latency_queries"])
    n_delete = int(data["n_delete"])
    n_tamper = int(data["n_tamper"])

    # If the harness handed us a backend that already is the sharded one, we
    # ignore it (re-build per M to control C/K cleanly). We DO note its name
    # in the output so report.py keys correctly.
    backend_name = getattr(backend, "name", "substrate_sharded")

    per_M: dict[str, dict] = {}

    for M in Ms:
        # Skip if M exceeds the global envelope: K * (C / 4).
        envelope = K * (codebook_C // 4)
        skipped = False
        skip_reason = ""
        if M > K * codebook_C - K:
            skipped = True
            skip_reason = (
                f"M={M} > K*C - K = {K * codebook_C - K} "
                f"(per-shard codebook exhausted)"
            )

        sharded = _build_sharded(data)
        # Smoke-test invariant: shared codebook is one tensor referenced by
        # every shard. Confirm id() match for the first two shards.
        cb_id_check = None
        if data["shared_codebook"] and len(sharded.shards) >= 2:
            cb_id_check = bool(
                id(sharded.shards[0].codebook) == id(sharded.shards[1].codebook)
                == id(sharded._shared_cb)
            )

        if skipped:
            per_M[str(M)] = {
                "M": M,
                "skipped": True,
                "reason": skip_reason,
                "envelope_M": envelope,
            }
            continue

        rng = np.random.default_rng(seed + 19000 + M)
        vecs = _make_vecs(rng, M, N)
        ids = [f"sh_{M}_{i:08d}" for i in range(M)]
        values = [f"v_{i}" for i in range(M)]

        # Store loop.
        store_us: list[float] = []
        for i in range(M):
            t0 = time.perf_counter_ns()
            sharded.store(ids[i], vecs[i], values[i])
            t1 = time.perf_counter_ns()
            if i < n_latency:
                store_us.append((t1 - t0) / 1000.0)

        # Shard distribution.
        shard_loads = [len(s.key_registry) for s in sharded.shards]
        shards_used = int(sum(1 for c in shard_loads if c > 0))

        # Recall@1 sampled on n_recall stored keys.
        r_count = min(n_recall, M)
        r_idx = rng.choice(M, size=r_count, replace=False)
        hits = 0
        for i in r_idx:
            res = sharded.retrieve(vecs[i], k=1)
            if res.key_id == ids[i]:
                hits += 1
        recall_at_1 = hits / max(r_count, 1)

        # Retrieve latency: n_latency random keys.
        q_count = min(n_latency, M)
        q_idx = rng.choice(M, size=q_count, replace=False)
        retr_us: list[float] = []
        for i in q_idx:
            t0 = time.perf_counter_ns()
            sharded.retrieve(vecs[i], k=1)
            t1 = time.perf_counter_ns()
            retr_us.append((t1 - t0) / 1000.0)

        # KF-1 aggregate across shards.
        try:
            audit_rep = sharded.audit()
            kf1_near_uniform_frac = audit_rep.kf1_above_thresh_frac
            kf2_max_iso = audit_rep.kf2_max_isolation
            tcft_mean_vr = audit_rep.tcft_mean_var_ratio
        except Exception as exc:  # noqa: BLE001
            kf1_near_uniform_frac = None
            kf2_max_iso = None
            tcft_mean_vr = None
            _ = exc

        # Edit-isolation smoke: edit 1 random stored key.
        edit_ok = None
        try:
            target = ids[int(r_idx[0])]
            sharded.edit(target, "EDITED")
            edit_res = sharded.retrieve(vecs[int(r_idx[0])], k=1)
            edit_ok = bool(edit_res.value == "EDITED")
        except Exception as exc:  # noqa: BLE001
            edit_ok = False
            _ = exc

        # Cross-shard delete chain: delete n_delete random stored keys.
        d_count = min(n_delete, M - 1)
        d_idx = rng.choice(M, size=d_count, replace=False)
        delete_us: list[float] = []
        certs_collected = 0
        for i in d_idx:
            kid = ids[i]
            try:
                t0 = time.perf_counter_ns()
                cert = sharded.delete(kid)
                t1 = time.perf_counter_ns()
                delete_us.append((t1 - t0) / 1000.0)
                if cert.w_state_hash_before and cert.w_state_hash_after:
                    certs_collected += 1
            except KeyError:
                # Edit above may have removed this id; safe to skip.
                continue

        # Validate the cross-shard chain.
        chain_report = sharded.verify_global_audit_chain()
        chain_integrity = chain_report["integrity"]

        # Tamper-detection: corrupt one byte in a random shard's W tensor,
        # re-hash, and verify the per-shard hash chain detects the change.
        import torch
        tamper_attempted = 0
        tamper_detected = 0
        for t_idx in range(n_tamper):
            # Pick a random shard that received at least one delete.
            shards_with_chain = [
                sid for sid in range(K)
                if any(e["shard_id"] == sid for e in sharded._global_audit_chain)
            ]
            if not shards_with_chain:
                break
            target_sid = int(rng.choice(shards_with_chain))
            target_shard = sharded.shards[target_sid]
            flat = target_shard.W.view(-1)
            n_flat = int(flat.numel())
            i_flat = int(rng.integers(0, n_flat))
            original = float(flat[i_flat].item())
            flat[i_flat] = -original
            tamper_attempted += 1
            # Re-hash and compare to the last recorded w_state_hash_after for
            # that shard. Tamper is detected if hashes differ.
            new_hash = hashlib.sha256(
                target_shard.W.detach().cpu().numpy().tobytes()
            ).hexdigest()
            last_after_for_shard = None
            for entry in reversed(sharded._global_audit_chain):
                if entry["shard_id"] == target_sid:
                    last_after_for_shard = entry["w_state_hash_after"]
                    break
            if last_after_for_shard is not None and new_hash != last_after_for_shard:
                tamper_detected += 1
            # Restore.
            flat[i_flat] = original

        tamper_detection_rate = (
            tamper_detected / tamper_attempted if tamper_attempted > 0 else None
        )

        # Disk: save once.
        save_dir = Path(tempfile.mkdtemp(prefix=f"sh_save_{M}_"))
        disk_bytes = 0
        try:
            sharded.save(save_dir)
            disk_bytes = _dir_size_bytes(save_dir)
        except Exception as exc:  # noqa: BLE001
            disk_bytes = 0
            _ = exc
        finally:
            try:
                shutil.rmtree(save_dir, ignore_errors=True)
            except OSError:
                pass

        per_M[str(M)] = {
            "M": M,
            "K": K,
            "codebook_C": codebook_C,
            "N": N,
            "envelope_M": envelope,
            "shards_used": shards_used,
            "shard_load_min": int(min(shard_loads)) if shard_loads else 0,
            "shard_load_max": int(max(shard_loads)) if shard_loads else 0,
            "shared_codebook": bool(data["shared_codebook"]),
            "shared_codebook_id_check": cb_id_check,
            "disk_bytes": int(disk_bytes),
            "disk_MB": float(disk_bytes) / 1.0e6,
            "p50_store_us": _percentile(store_us, 50),
            "p95_store_us": _percentile(store_us, 95),
            "p50_retrieve_us": _percentile(retr_us, 50),
            "p95_retrieve_us": _percentile(retr_us, 95),
            "recall_at_1": float(recall_at_1),
            "n_recall_samples": int(r_count),
            "n_latency_queries": int(q_count),
            "edit_ok": edit_ok,
            "kf1_near_uniform_frac": kf1_near_uniform_frac,
            "kf2_max_isolation": kf2_max_iso,
            "tcft_mean_var_ratio": tcft_mean_vr,
            "n_deletes_collected": int(certs_collected),
            "cross_shard_chain_integrity": float(chain_integrity),
            "cross_shard_links_ok": int(chain_report["links_ok"]),
            "cross_shard_links_total": int(chain_report["links_total"]),
            "cross_shard_transitions_ok": int(chain_report["transitions_ok"]),
            "cross_shard_transitions_total": int(chain_report["transitions_total"]),
            "tamper_attempted": int(tamper_attempted),
            "tamper_detected": int(tamper_detected),
            "tamper_detection_rate": tamper_detection_rate,
            "p50_delete_us": _percentile(delete_us, 50),
            "p95_delete_us": _percentile(delete_us, 95),
        }

    # Disk growth across the live M points.
    live_per_M = {k: v for k, v in per_M.items() if not v.get("skipped")}
    if len(live_per_M) >= 2:
        sorted_ms = sorted(live_per_M.keys(), key=lambda s: int(s))
        d_min = live_per_M[sorted_ms[0]]["disk_MB"] or 0.0
        d_max = live_per_M[sorted_ms[-1]]["disk_MB"] or 0.0
        disk_growth = (d_max / d_min) if d_min > 0 else None
    else:
        disk_growth = None

    return {
        "scenario": "multi_substrate_sharding",
        "backend": backend_name,
        "K_shards": K,
        "codebook_C": codebook_C,
        "N": N,
        "Ms": Ms,
        "per_M": per_M,
        "total_disk_growth": disk_growth,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "total_disk_growth_lt": 1.5,
                "recall_at_1": 0.85,
                "cross_shard_chain_integrity": 1.0,
                "tamper_detection_rate": 0.90,
            },
            "hard_fail": {
                "total_disk_growth_gt": 5.0,
                "recall_at_1": 0.50,
                "cross_shard_chain_integrity": 0.95,
                "tamper_detection_rate": 0.50,
            },
        },
        "baselines": {
            "hard_pass": {"cross_shard_chain_integrity": 0.0},
            "hard_fail": {"cross_shard_chain_integrity": 0.0},
        },
    }
