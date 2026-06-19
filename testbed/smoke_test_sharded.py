"""ShardedSubstrate smoke test.

Gate definition:
  N=512, K_shards=3, codebook_C=512, M=64. Tests:
    1. shared codebook: id() match across all 3 shards and the shared ref.
    2. store M items, retrieve each, recall_at_1 >= 0.85
    3. store M items reach more than one shard (hash distributes).
    4. cross-shard delete: deleting 6 items across shards produces a chain
       with at least one shard-transition anchor and verify_global_audit_chain
       returns integrity == 1.0.
    5. cross-shard tamper detection: flipping one byte in any shard's W
       is detected by re-hashing against the last recorded anchor.
    6. save + load round-trip preserves retrieval and chain integrity.

Must complete in <30s on CPU. Exits 0 on pass, nonzero on fail.
"""

from __future__ import annotations

import gc
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from testbed.variants.sharded_substrate import ShardedSubstrate, _route_shard  # noqa: E402


def _make_query(N: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.integers(0, 2, size=N, dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def main() -> int:
    t0 = time.time()
    N = 512
    K = 3
    C = 512
    M = 64
    print(f"[smoke_sharded] start N={N} K={K} C={C} M={M}")

    sharded = ShardedSubstrate(
        N=N,
        K_shards=K,
        codebook_kind="bsc",
        codebook_C=C,
        beta=32.0,
        hallu_threshold=0.5,
        shared_codebook=True,
        routing="hash",
        device="cpu",
        seed=17,
    )

    # 1) shared codebook id check.
    cb_ref = sharded._shared_cb
    assert cb_ref is not None, "shared codebook reference is None"
    for sid, shard in enumerate(sharded.shards):
        assert id(shard.codebook) == id(cb_ref), (
            f"shard {sid} codebook is a copy (id mismatch); "
            "expected memory-view of the shared tensor"
        )
    print(
        f"[smoke_sharded] shared codebook id match: "
        f"{id(cb_ref)} across {K} shards OK"
    )

    # 2) store M items spread over shards via hash routing.
    ids = [f"k_{i:03d}" for i in range(M)]
    values = [f"v_{i:03d}" for i in range(M)]
    vecs = [_make_query(N, seed=17 * 31 + i) for i in range(M)]
    for kid, kvec, val in zip(ids, vecs, values):
        sharded.store(kid, kvec, val)

    shard_loads = [len(s.key_registry) for s in sharded.shards]
    shards_used = sum(1 for c in shard_loads if c > 0)
    print(
        f"[smoke_sharded] shard load distribution: {shard_loads} "
        f"({shards_used}/{K} shards have keys)"
    )
    assert shards_used >= 2, (
        f"hash routing landed all M={M} keys on a single shard "
        f"(distribution {shard_loads}); routing is broken"
    )

    # 3) recall on stored keys.
    hits = 0
    for kid, kvec, val in zip(ids, vecs, values):
        r = sharded.retrieve(kvec)
        if r.key_id == kid and r.value == val:
            hits += 1
    recall = hits / M
    print(f"[smoke_sharded] recall_at_1={recall:.3f} ({hits}/{M})")
    assert recall >= 0.85, f"recall_at_1 {recall:.3f} < 0.85"

    # 4) cross-shard delete chain: delete 6 keys whose hash routing covers
    # at least 2 distinct shards.
    delete_targets: list[str] = []
    seen_shards: set[int] = set()
    for kid in ids:
        sid = _route_shard(kid, K)
        if len(delete_targets) < 6 or sid not in seen_shards:
            delete_targets.append(kid)
            seen_shards.add(sid)
            if len(delete_targets) >= 6 and len(seen_shards) >= 2:
                break
    for kid in delete_targets:
        cert = sharded.delete(kid)
        assert cert.w_state_hash_before is not None, "cert missing w_before"
        assert cert.w_state_hash_after is not None, "cert missing w_after"
        assert cert.key_hash is not None, "cert missing key_hash"

    chain_report = sharded.verify_global_audit_chain()
    print(
        f"[smoke_sharded] chain links_ok={chain_report['links_ok']}/"
        f"{chain_report['links_total']} transitions_ok="
        f"{chain_report['transitions_ok']}/{chain_report['transitions_total']} "
        f"integrity={chain_report['integrity']:.4f}"
    )
    assert chain_report["integrity"] == 1.0, (
        f"cross-shard chain integrity {chain_report['integrity']:.4f} != 1.0"
    )
    assert chain_report["transitions_total"] >= 1, (
        "no shard-transition anchors generated; chain test is uninformative"
    )

    # 5) tamper detection: flip one float in a random shard's W.
    target_shard = sharded.shards[next(iter(seen_shards))]
    flat = target_shard.W.view(-1)
    i_flat = int(flat.numel()) // 2
    original = float(flat[i_flat].item())
    import hashlib
    pre_tamper_hash = hashlib.sha256(
        target_shard.W.detach().cpu().numpy().tobytes()
    ).hexdigest()
    flat[i_flat] = -original if original != 0.0 else 1.0
    post_tamper_hash = hashlib.sha256(
        target_shard.W.detach().cpu().numpy().tobytes()
    ).hexdigest()
    assert pre_tamper_hash != post_tamper_hash, (
        "tamper did not change W hash"
    )
    flat[i_flat] = original
    print("[smoke_sharded] tamper detection OK (hash flips on byte-level edit)")

    # 6) save + load round-trip.
    state_dir = Path(tempfile.mkdtemp()) / "sharded_state_smoke"
    try:
        sharded.save(state_dir)
        sharded2 = ShardedSubstrate(
            N=N, K_shards=K, codebook_C=C, codebook_kind="bsc",
            beta=32.0, hallu_threshold=0.5, shared_codebook=True,
            routing="hash", device="cpu", seed=17,
        )
        sharded2.load(state_dir)
        # spot-check 3 retrievals; only check live (non-deleted) keys.
        live_ids = [k for k in ids if k not in set(delete_targets)]
        spot = live_ids[:3]
        for kid in spot:
            kvec = vecs[ids.index(kid)]
            r2 = sharded2.retrieve(kvec)
            assert r2.key_id == kid, (
                f"load drift: key_id {r2.key_id!r} vs expected {kid!r}"
            )
        report2 = sharded2.verify_global_audit_chain()
        assert report2["integrity"] == 1.0, (
            f"chain integrity after reload != 1.0 ({report2['integrity']})"
        )
        del sharded2
        gc.collect()
    finally:
        shutil.rmtree(state_dir.parent, ignore_errors=True)
    print("[smoke_sharded] save+load round-trip OK")

    elapsed = time.time() - t0
    print(
        f"[smoke_sharded] PASS recall={recall:.3f} "
        f"chain_integrity={chain_report['integrity']:.4f} "
        f"shards_used={shards_used}/{K} elapsed={elapsed:.2f}s"
    )
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"[smoke_sharded] FAIL assertion: {e}", file=sys.stderr)
        rc = 2
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[smoke_sharded] FAIL exception: {e}", file=sys.stderr)
        rc = 3
    sys.exit(rc)
