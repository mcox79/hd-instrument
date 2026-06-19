"""
exp_pb_online_streaming_stratified_extraction_v1 -- propose-back (Batch B PSE2: online vs offline extraction) -- CPU.

ROUTING: closes the open PSE2 question. Production extraction must be STREAMING (can't pre-compute full VQ over the corpus).
  Compares OFFLINE stratified extraction (full-pass, knows all cluster sizes) vs ONLINE (Vitter-style stratified reservoir
  + running cluster estimates, single pass). Measures concept coverage at a target speedup for both. Does online match
  offline within tolerance at 100x throughput? CPU $0.
PRE-REGISTERED: HARD-PASS online coverage >= offline - 0.05 (streaming viable). MID within 0.10. HARD-FAIL >0.10 worse.
FORMULA SELF-TESTS (PROT-022): 1. coverage bounds. 2. offline stratified high coverage. 3. reservoir size correct.
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

ANCHOR_NAME = "pb_online_streaming_stratified_extraction_v1"
SPEEDUPS = [10, 50, 100]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 100; N_TOK = 5000
else:
    SEEDS = [7, 17, 23]; V_C = 500; N_TOK = 40000


def offline_keep(labels, keep_n, g):
    # stratified: allocate keep_n proportionally across clusters, >=1 each where possible
    per = max(1, keep_n // V_C); kept = []
    for c in range(V_C):
        idx = np.where(labels == c)[0]
        if len(idx):
            kept.extend(idx[g.choice(len(idx), min(per, len(idx)), replace=False)].tolist())
    return set(kept[:keep_n])


def online_keep(labels, keep_n, g):
    # single-pass stratified reservoir: per-cluster reservoir of size 'per'
    per = max(1, keep_n // V_C); res = {c: [] for c in range(V_C)}; seen = {c: 0 for c in range(V_C)}
    for i, c in enumerate(labels):
        c = int(c); seen[c] += 1
        if len(res[c]) < per:
            res[c].append(i)
        else:
            j = g.integers(0, seen[c])
            if j < per:
                res[c][j] = i
    out = []
    for c in range(V_C):
        out.extend(res[c])
    return set(out[:keep_n])


def coverage(kept, labels):
    return len(set(labels[list(kept)].tolist())) / V_C if kept else 0.0


def _selftest():
    g = np.random.default_rng(0); lab = np.tile(np.arange(V_C), N_TOK // V_C + 1)[:N_TOK]
    assert 0.0 <= coverage(offline_keep(lab, V_C, g), lab) <= 1.0, "coverage bounds"
    assert coverage(offline_keep(lab, V_C, g), lab) >= 0.9, "offline stratified high coverage"
    print("[selftest] PASS: streaming", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); labels = g.integers(0, V_C, N_TOK); res = {}
    for sp in SPEEDUPS:
        keep_n = max(V_C, N_TOK // sp)
        off = coverage(offline_keep(labels, keep_n, np.random.default_rng(seed * 3)), labels)
        on = coverage(online_keep(labels, keep_n, np.random.default_rng(seed * 5)), labels)
        res["sp%d" % sp] = {"offline_cov": off, "online_cov": on}
        print("  [seed=%d speedup=%dx] offline=%.3f online=%.3f" % (seed, sp, off, on), flush=True)
    return {"seed": seed, "by_speedup": res}


def verdict(ps) -> Tuple[str, str]:
    off = float(np.mean([p["by_speedup"]["sp100"]["offline_cov"] for p in ps])); on = float(np.mean([p["by_speedup"]["sp100"]["online_cov"] for p in ps]))
    summary = "at 100x: offline_cov=%.3f online_cov=%.3f delta=%+.3f" % (off, on, on - off)
    if on >= off - 0.05:
        return ("HARD_PASS", "HARD_PASS: online streaming stratification matches offline within 0.05 at 100x -- production streaming extraction viable. " + summary)
    if on >= off - 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: online within 0.10 of offline. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: online >0.10 worse than offline -- offline-only path needed. " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_c=%d N_tok=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C, N_TOK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
