"""
substrate_posbind_x_b2_sparse_sequence_capacity_v1_n8192 -- P4: position-binding x B2 sparse capacity -- remote CPU.

ROUTING: research_to_exp_dev_priority_1_compositions_routing (Cell P4). Compose position-binding (Bundle E roll-bind
  sequence encoding) x B2 (DG sparse-expansion). Does SPARSE item coding store much longer/more sequence positions
  in a single bundle than DENSE coding at the same N (less crosstalk)? CPU numpy, $0. remote_cpu_queue.

MODEL: a sequence of S items encoded as ONE bundle b = sum_{j=1..S} roll(item_j, j). Read position j:
  cleanup(roll(b,-j)) vs the item codebook (nearest by cosine). DENSE items = bipolar(N). SPARSE items = DG codes
  (k-WTA, f=0.02, in N). S_crit = max S with position-read accuracy >= 0.90. Compare sparse vs dense.

PRE-REG bands: HARD-PASS sparse_S_crit >= 10x dense_S_crit (sparse stores >=10x sequence positions). MIDDLE 2-10x. HARD-FAIL <2x.
SELF-TESTS (PROT-022): 1. roll-bind/unbind round-trips one item. 2. sparse codes are k-sparse. 3. N=8192.
ASCII-only. write_metrics. PROT-018 _n8192 -> N=8192.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_posbind_x_b2_sparse_sequence_capacity_v1_n8192"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

F_SPARSE = 0.02; VOCAB = 256
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; S_GRID = [4, 8, 16, 32, 64]
else:
    SEEDS = [7, 17, 23]; N_DIM = N; S_GRID = [8, 16, 32, 64, 128, 256]


def dense_codebook(V, n, g):
    cb = (g.integers(0, 2, size=(V, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def sparse_codebook(V, n, g):
    k = max(1, int(round(F_SPARSE * n))); cb = np.zeros((V, n), dtype=np.float32)
    for i in range(V):
        cb[i, g.choice(n, size=k, replace=False)] = 1.0
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def s_crit(cb, n, g):
    V = cb.shape[0]; mc = 0
    for S in S_GRID:
        seq = g.integers(0, V, size=S)
        b = np.zeros(n, dtype=np.float32)
        for j in range(S):
            b += np.roll(cb[seq[j]], j + 1)
        hits = 0
        for j in range(S):
            probe = np.roll(b, -(j + 1)); hits += (int(np.argmax(cb @ probe)) == seq[j])
        if hits / S >= 0.90:
            mc = S
        else:
            break
    return mc


def _selftest():
    g = np.random.default_rng(0); n = 512; cb = dense_codebook(10, n, g)
    b = np.roll(cb[3], 2); assert int(np.argmax(cb @ np.roll(b, -2))) == 3, "roll round-trip"
    sc = sparse_codebook(10, n, g); k = max(1, int(round(F_SPARSE * n)))
    assert int((sc[0] != 0).sum()) == k, "k-sparse"
    assert N == 8192; print("[selftest] PASS: roll_roundtrip k_sparse", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    ds = s_crit(dense_codebook(VOCAB, n, g), n, np.random.default_rng(seed + 1))
    ss = s_crit(sparse_codebook(VOCAB, n, g), n, np.random.default_rng(seed + 2))
    return {"seed": seed, "N": n, "dense_S_crit": ds, "sparse_S_crit": ss, "ratio": float(ss / max(ds, 1))}


def verdict(ps) -> Tuple[str, str]:
    ds = float(np.mean([p["dense_S_crit"] for p in ps])); ss = float(np.mean([p["sparse_S_crit"] for p in ps]))
    r = ss / max(ds, 1); note = "" if ss < S_GRID[-1] else " (sparse hit grid ceiling; ratio is LOWER BOUND)"
    summary = "dense_S_crit=%.0f sparse_S_crit=%.0f ratio=%.1fx%s" % (ds, ss, r, note)
    if r >= 10.0:
        return ("HARD_PASS", "HARD_PASS: sparse coding stores >=10x sequence positions vs dense. " + summary)
    if r >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse 2-10x dense sequence capacity. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse <2x dense. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d f=%.3f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, F_SPARSE), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] dense_S_crit=%d sparse_S_crit=%d ratio=%.1fx" % (seed, r["dense_S_crit"], r["sparse_S_crit"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
