"""
exp_fp16_recall_parity_1M_v1 -- 1M sign-key recall: fp16 vs fp32 parity (production dtype gate) -- CPU.

ROUTING: scale-gap / production dtype validation. The 1M recall gate passed in fp32; production runs fp16/bf16 for memory.
  Validates that 1M-scale sign-key recall@1 in fp16 matches fp32 (no parity loss from half precision at scale). Stores N
  sign keys, queries noisy versions, recall@1 via chunked matmul in fp16 vs fp32. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS fp16 recall@1 within 0.01 of fp32 AND fp16 recall@1 >= 0.99 at N=1M (fp16 production-safe at scale).
  MIDDLE within 0.03. HARD-FAIL fp16 degrades > 0.03 vs fp32 (half precision loses recall at scale).
FORMULA SELF-TESTS (PROT-022): 1. self-recall. 2. sign keys exact in fp16. 3. chunked == full.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "fp16_recall_parity_1M_v1"; D = 1024; NOISE_FLIP = 0.15; NQ = 500; CHUNK = 50000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_KEYS = 50000 if RUN_MODE == "smoke" else 1000000


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.int8)


def recall(query_idx, queries, keys, chunk, dtype):
    nq = queries.shape[0]; best = np.full(nq, -1, np.int64); best_sc = np.full(nq, -1e9, np.float32)
    qf = queries.astype(dtype)
    for c0 in range(0, keys.shape[0], chunk):
        c1 = min(c0 + chunk, keys.shape[0]); blk = keys[c0:c1].astype(dtype)
        sc = (qf @ blk.T).astype(np.float32); bidx = np.argmax(sc, axis=1); bsc = sc[np.arange(nq), bidx]
        upd = bsc > best_sc; best[upd] = c0 + bidx[upd]; best_sc[upd] = bsc[upd]
    return float((best == query_idx).mean())


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g)
    assert recall(np.array([5]), K[5:6], K, 8, np.float32) == 1.0, "self-recall"
    assert np.array([1, -1], np.int8).astype(np.float16).tolist() == [1.0, -1.0], "sign keys exact in fp16"
    assert recall(np.array([3]), K[3:4], K, 4, np.float16) == recall(np.array([3]), K[3:4], K, 20, np.float16), "chunked == full"
    print("[selftest] PASS: fp16-recall-parity-1M", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(111)
    print("  allocating %d sign keys (D=%d)..." % (N_KEYS, D), flush=True)
    keys = sign_keys(N_KEYS, D, g); qidx = g.choice(N_KEYS, size=NQ, replace=False)
    flips = g.random((NQ, D)) < NOISE_FLIP; queries = keys[qidx].copy(); queries[flips] *= -1
    r32 = recall(qidx, queries, keys, CHUNK, np.float32); r16 = recall(qidx, queries, keys, CHUNK, np.float16)
    print("  N=%d recall@1 fp32=%.4f fp16=%.4f (delta=%.4f, noise=%.2f)" % (N_KEYS, r32, r16, abs(r32 - r16), NOISE_FLIP), flush=True)
    return {"n_keys": N_KEYS, "r32": r32, "r16": r16, "delta": abs(r32 - r16)}


def verdict(r) -> Tuple[str, str]:
    s = "fp32=%.4f fp16=%.4f delta=%.4f at N=%d" % (r["r32"], r["r16"], r["delta"], r["n_keys"])
    if r["delta"] <= 0.01 and r["r16"] >= 0.99:
        return ("HARD_PASS", "HARD_PASS: fp16 recall matches fp32 within 0.01 and >=0.99 at 1M -- half precision production-safe at scale (2x memory saving). " + s)
    if r["delta"] <= 0.03:
        return ("MIDDLE_BAND", "MIDDLE_BAND: fp16 within 0.03 of fp32 -- usable with minor loss. " + s)
    return ("HARD_FAIL", "HARD_FAIL: fp16 degrades >0.03 vs fp32 at scale -- keep fp32 for recall. " + s)


print("[config] anchor=%s mode=%s N_keys=%d D=%d noise=%.2f" % (ANCHOR_NAME, RUN_MODE, N_KEYS, D, NOISE_FLIP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
