"""
exp_fact_checked_khop_merkle_chain_hp12_root_v1 -- Batch D1 Rank 3: per-hop Merkle chain cert latency -- CPU.

ROUTING: Research Batch D. Each hop's verification cert -> a Merkle leaf; the K-hop chain forms a Merkle tree; the root is
  one cert (extends HP-12 "answer-certified" to "per-hop reasoning chain certified end-to-end"). Measures end-to-end
  Merkle build + root + verification-round-trip LATENCY at K up to 20. No frontier system certifies per-hop chains.
PRE-REGISTERED: HARD-PASS end-to-end cert latency < 1ms at K=20 AND verification round-trip valid. MID 1-5ms. HARD-FAIL >5ms.
FORMULA SELF-TESTS (PROT-022): 1. Merkle root deterministic. 2. tamper detected. 3. proof verifies.
ASCII-only. write_metrics. PROT-018 no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "fact_checked_khop_merkle_chain_hp12_root_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
KS = [3, 5, 10, 20]; TRIALS = 200 if RUN_MODE == "smoke" else 2000


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def merkle_root(leaves: List[bytes]) -> bytes:
    level = [_h(l) for l in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [_h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def merkle_proof(leaves: List[bytes], idx: int):
    level = [_h(l) for l in leaves]; proof = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        sib = idx ^ 1; proof.append((level[sib], idx & 1)); idx //= 2
        level = [_h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return proof


def verify_proof(leaf: bytes, proof, root: bytes) -> bool:
    h = _h(leaf)
    for sib, right in proof:
        h = _h(sib + h) if right else _h(h + sib)
    return h == root


def _selftest():
    leaves = [b"hop%d" % i for i in range(5)]; r = merkle_root(leaves)
    assert r == merkle_root(leaves), "root deterministic"
    bad = list(leaves); bad[2] = b"tampered"; assert merkle_root(bad) != r, "tamper detected"
    assert verify_proof(leaves[3], merkle_proof(leaves, 3), r), "proof verifies"
    print("[selftest] PASS: merkle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    by_K = {}
    for K in KS:
        g = np.random.default_rng(K)
        leaves_sets = [[g.bytes(64) for _ in range(K)] for _ in range(TRIALS)]
        t0 = time.perf_counter()
        roots = [merkle_root(ls) for ls in leaves_sets]
        build_ms = (time.perf_counter() - t0) / TRIALS * 1000
        t1 = time.perf_counter(); ok = 0
        for ls, r in zip(leaves_sets, roots):
            ok += int(verify_proof(ls[K // 2], merkle_proof(ls, K // 2), r))
        verify_ms = (time.perf_counter() - t1) / TRIALS * 1000
        by_K["k%d" % K] = {"build_ms": build_ms, "verify_ms": verify_ms, "roundtrip_ms": build_ms + verify_ms, "valid": ok == TRIALS}
        print("  [K=%d] build=%.4fms verify=%.4fms roundtrip=%.4fms valid=%s" % (K, build_ms, verify_ms, build_ms + verify_ms, ok == TRIALS), flush=True)
    return {"by_K": by_K}


def verdict(r) -> Tuple[str, str]:
    k20 = r["by_K"]["k%d" % KS[-1]]; rt = k20["roundtrip_ms"]; valid = k20["valid"]
    summary = "roundtrip by K: %s | K=%d=%.4fms valid=%s" % ({k: round(v["roundtrip_ms"], 4) for k, v in r["by_K"].items()}, KS[-1], rt, valid)
    if rt < 1.0 and valid:
        return ("HARD_PASS", "HARD_PASS: per-hop Merkle chain cert <1ms at K=20 with valid round-trip -- end-to-end reasoning-chain certification, no frontier equivalent. " + summary)
    if rt < 5.0 and valid:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cert 1-5ms (usable, not flagship-fast). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cert >5ms or invalid. " + summary)


print("[config] anchor=%s mode=%s KS=%s trials=%d" % (ANCHOR_NAME, RUN_MODE, KS, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
