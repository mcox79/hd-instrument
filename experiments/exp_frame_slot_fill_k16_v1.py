"""
exp_frame_slot_fill_k16_v1 -- Batch A Rank 4: multi-attribute entity (k=16 slot-fillers) interference -- CPU.

ROUTING: Research Batch A. How many attributes a single stored entity carries without inter-frame interference.
  entity = sign(sum_{j=1..k} slot_j * value_j) (bipolar bind=product, bundle=sign-sum). Retrieve slot_j: argmax over
  value codebook of (entity * slot_j) . value. Retrieval accuracy across k=16 slots. KG multi-attribute use case.
PRE-REGISTERED: HARD-PASS retrieval accuracy >= 0.95 at k=16, N=8192. MID 0.85-0.95. HF < 0.85.
FORMULA SELF-TESTS (PROT-022): 1. k=1 exact. 2. bind product.
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

ANCHOR_NAME = "frame_slot_fill_k16_v1"
K = 16
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; N_VAL = 200; N_ENT = 100
else:
    SEEDS = [7, 17, 23]; N = 8192; N_VAL = 500; N_ENT = 300


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); s = bp(1, 256, g); v = bp(1, 256, g); ent = np.sign(s * v)
    assert np.array_equal(np.sign(ent * s), v), "k=1 exact"
    print("[selftest] PASS: slot fill", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); slots = bp(K, N, g); VAL = bp(N_VAL, N, g); correct = 0; total = 0
    for _ in range(N_ENT):
        vids = g.choice(N_VAL, K, replace=False)
        ent = np.sign((slots * VAL[vids]).sum(0)); ent[ent == 0] = 1.0
        for j in range(K):
            pred = np.argmax((ent * slots[j]) @ VAL.T)
            correct += int(pred == vids[j]); total += 1
    return {"seed": seed, "N": N, "k": K, "retrieval_accuracy": correct / total}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["retrieval_accuracy"] for p in ps]))
    summary = "retrieval_accuracy=%.3f at k=%d, N=%d" % (a, K, ps[0]["N"])
    if a >= 0.95:
        return ("HARD_PASS", "HARD_PASS: single entity carries k=16 attributes at >=0.95 retrieval -- KG multi-attribute binding works. " + summary)
    if a >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: k=16 retrieval 0.85-0.95 (some interference). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: k=16 too many attributes (<0.85 retrieval). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d k=%d N_val=%d N_ent=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, K, N_VAL, N_ENT), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] retrieval_accuracy=%.3f" % (seed, r["retrieval_accuracy"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
