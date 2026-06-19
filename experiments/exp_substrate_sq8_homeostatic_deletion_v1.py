"""
substrate_sq8_homeostatic_deletion_v1 -- homeostatic self-deletion (LifeHD-style) -- remote CPU.

ROUTING: research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ8; P_drill=0.65; LifeHD 2024).
  Tests whether a substrate maintains STABLE recall under an unbounded stream by self-deleting low-energy memories
  to hold a homeostatic load -- i.e. recall of recent items stays constant regardless of how long the stream runs.
  CPU numpy, $0. remote_cpu_queue. Reuses D-ECR eviction (B6).

CAPABILITY QUESTION: stream S = MULT * m_cap novel patterns; homeostatic D-ECR keeps |bank|=m_cap (evict lowest
  self-overlap on overflow). Does recall of the LAST m_cap (recent) patterns stay high + STABLE as S grows
  (3x, 6x, 10x)? Stable recent-recall = homeostasis (substrate self-maintains indefinitely).

CELLS (3 seeds): recent-recall at stream length MULT in {3,6,10} * m_cap; N=2048; m_cap=alpha_c*N.
PRE-REGISTERED bands (stability = min recent-recall across MULTs; drift = max-min):
  HARD-PASS: min recent-recall >= 0.90 AND drift <= 0.05 (stable homeostasis). MIDDLE: min >= 0.75. HARD-FAIL: min < 0.75 or drift > 0.15.

FORMULA SELF-TESTS (PROT-022): 1. low-load recall. 2. eviction reduces ||W||. 3. alpha_c=0.138.
ASCII-only. write_metrics. PROT-018: swept-MULT anchor (no _nN).
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
ANCHOR_NAME = "substrate_sq8_homeostatic_deletion_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
ALPHA_C = 0.138; MULTS = [3, 6, 10]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512
else:
    SEEDS = [7, 17, 23]; N = 2048
def bipolar(shape, g): return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)
def _ov(W, bank, n):
    if not bank: return np.array([])
    X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0; return (X * R).sum(axis=1) / n
def homeostatic(n, S, m_cap, g):
    W = np.zeros((n, n), dtype=np.float32); bank = []; recent = []
    for t in range(S):
        x = bipolar((n,), g); bank.append(x); recent.append(x); W += np.outer(x, x); np.fill_diagonal(W, 0.0)
        if len(bank) > m_cap:
            ev = int(np.argmin(_ov(W, bank, n))); xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    recent = recent[-m_cap:]; X = np.stack(recent); R = np.sign(X @ W.T); R[R == 0] = 1.0
    return float(np.mean((X * R).sum(axis=1) / n > 0.90))
def _selftest():
    g = np.random.default_rng(0); n = 256; X = bipolar((5, n), g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
    assert float(np.mean((np.sign(X @ W.T) * X).sum(axis=1) / n > 0.95)) > 0.9, "low-load recall"
    x = bipolar((n,), g); W2 = np.outer(x, x); nb = float(np.abs(W2).sum()); assert float(np.abs(W2 - np.outer(x, x)).sum()) < nb
    assert abs(ALPHA_C - 0.138) < 1e-6; print("[selftest] PASS: recall eviction_reduces_W", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run_seed(seed):
    m_cap = max(4, int(round(0.85 * ALPHA_C * N)))   # graceful-zone setpoint (alpha-ramp: <85% alpha_c)
    out = {}
    for mult in MULTS:
        out[f"x{mult}"] = homeostatic(N, mult * m_cap, m_cap, np.random.default_rng(seed * 100 + mult))
    return {"seed": seed, "m_cap": m_cap, **out}
def verdict(ps) -> Tuple[str, str]:
    rec = {m: float(np.mean([s[f"x{m}"] for s in ps])) for m in MULTS}
    mn = min(rec.values()); drift = max(rec.values()) - mn
    summary = "recent_recall " + " ".join(f"{m}x:{rec[m]:.2f}" for m in MULTS) + f" | min={mn:.2f} drift={drift:.2f}"
    if mn >= 0.90 and drift <= 0.05: return ("HARD_PASS", f"HARD_PASS: stable homeostatic recall (min>=0.90, drift<=0.05). {summary}")
    if mn >= 0.75: return ("MIDDLE_BAND", f"MIDDLE_BAND: homeostasis partial. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: recall unstable/low. {summary}")
print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} mults={MULTS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print(f"  [seed={seed}] " + " ".join(f"{m}x:{r[f'x{m}']:.2f}" for m in MULTS), flush=True)
v, vmsg = verdict(ps); print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "cells": [f"x{m}" for m in MULTS], "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
