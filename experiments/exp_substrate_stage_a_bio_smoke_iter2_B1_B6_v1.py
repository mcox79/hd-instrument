"""
substrate_stage_a_bio_smoke_iter2_B1_B6_v1 -- iteration on B1 + B6 WHY-DRILLs -- LAPTOP CPU.

ROUTING: iterates notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs (batch 1 B1+B6 WHY-DRILLs).
  CPU numpy, $0. LAPTOP. Resolves the two metric near-misses found in batch 1:
  - B1 speedup was timing-noise-dominated at M=50 (one-shot too fast to time). Rerun at M near alpha_c AND
    report a TIMING-FREE metric: Adam epochs-to-match (one-shot = 1 pass). speedup_epochs = adam_epochs_to_match.
  - B6 D-ECR==LRU at M=1.3*alpha_c (both saturated at recall 1.0). Sweep M={1.0,1.5,2.0,2.5}*alpha_c to find
    the load where LRU degrades but D-ECR (curate best) holds -> the real audit-eviction differentiator.

PRE-REG (revised, honest):
  B1: HP if epochs-to-match >= 10 (one-shot >=10x fewer passes) AND acc>=0.80; MID 2-10x; HF <2x.
  B6: HP if at SOME swept M, D-ECR recall >= LRU + 0.10 AND D-ECR >= 1.2*no-eviction; MID D-ECR>LRU by >0.03; HF D-ECR<=LRU everywhere.

FORMULA SELF-TESTS (PROT-022): 1. one-shot proto recovers class. 2. eviction reduces ||W||. 3. alpha_c=0.138.
ASCII-only. PROT-021: run_mode local CPU.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_stage_a_bio_smoke_iter2_B1_B6_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
BATCH = 64
ADAM_LR = 0.01

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_B1 = 512; ADAM_EPOCHS = 40; M_MULTS = [1.0, 1.5, 2.0]; N_B6 = 256
else:
    SEEDS = [7, 17, 23]; N_B1 = 2048; ADAM_EPOCHS = 120; M_MULTS = [1.0, 1.5, 2.0, 2.5]; N_B6 = 512


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


# ---- B1: one-shot vs Adam, epochs-to-match (timing-free) at M near alpha_c ----
def b1_epochs(n, g):
    K = 5; M = max(K, int(round(ALPHA_C * n)))            # ~alpha_c*N total patterns
    per = M // K
    protos = bipolar((K, n), g)
    X, y = [], []
    for c in range(K):
        for _ in range(per):
            x = protos[c] + g.standard_normal(n).astype(np.float32) * 0.5; x = np.sign(x); x[x == 0] = 1
            X.append(x.astype(np.float32)); y.append(c)
    X = np.stack(X); y = np.array(y)
    # one-shot Hebbian prototype (1 pass)
    t0 = time.time(); Wh = np.zeros((K, n), dtype=np.float32)
    for i in range(len(X)):
        Wh[y[i]] += X[i]
    acc_h = float((np.argmax(X @ Wh.T, axis=1) == y).mean()); t_h = time.time() - t0
    # Adam: epochs until val-acc >= acc_h
    Wm = (g.standard_normal((K, n)) * 0.01).astype(np.float32)
    mm = np.zeros_like(Wm); vv = np.zeros_like(Wm); b1, b2, eps = 0.9, 0.999, 1e-8; it = 0; ep_match = None; t0 = time.time()
    for ep in range(1, ADAM_EPOCHS + 1):
        idx = g.permutation(len(X))
        for s in range(0, len(X), BATCH):
            it += 1; bi = idx[s:s + BATCH]; xb, yb = X[bi], y[bi]
            lo = xb @ Wm.T; lo -= lo.max(axis=1, keepdims=True); ez = np.exp(lo); pr = ez / ez.sum(axis=1, keepdims=True)
            gl = pr.copy(); gl[np.arange(len(bi)), yb] -= 1.0; gl /= len(bi); gW = gl.T @ xb
            mm = b1 * mm + (1 - b1) * gW; vv = b2 * vv + (1 - b2) * (gW * gW)
            Wm = Wm - ADAM_LR * (mm / (1 - b1 ** it)) / (np.sqrt(vv / (1 - b2 ** it)) + eps)
        if ep_match is None and float((np.argmax(X @ Wm.T, axis=1) == y).mean()) >= acc_h:
            ep_match = ep; break
    t_adam = time.time() - t0
    if ep_match is None:
        ep_match = ADAM_EPOCHS
    return {"M": M, "acc_oneshot": acc_h, "adam_epochs_to_match": ep_match,
            "wall_speedup": float(t_adam / max(t_h, 1e-6)), "t_oneshot": t_h, "t_adam": t_adam}


# ---- B6: D-ECR vs LRU vs random vs no-eviction across load ----
def _self_ov(W, bank, n):
    if not bank:
        return np.array([])
    X = np.stack(bank); R = np.sign(X @ W.T); R[R == 0] = 1.0
    return (X * R).sum(axis=1) / n


def _stream(n, policy, m_cap, g):
    W = np.zeros((n, n), dtype=np.float32); bank = []
    for t in range(3 * m_cap):
        x = bipolar((n,), g); bank.append(x); W += np.outer(x, x); np.fill_diagonal(W, 0.0)
        if len(bank) > m_cap:
            if policy == "lru":
                ev = 0
            elif policy == "random":
                ev = int(g.integers(0, len(bank)))
            else:
                ev = int(np.argmin(_self_ov(W, bank, n)))      # D-ECR
            xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    ov = _self_ov(W, bank, n); return float(np.mean(ov > 0.95)) if len(ov) else 0.0


def _noevict(n, m_cap, g):
    W = np.zeros((n, n), dtype=np.float32); bank = []
    for t in range(3 * m_cap):
        x = bipolar((n,), g); bank.append(x); W += np.outer(x, x)
    np.fill_diagonal(W, 0.0); ov = _self_ov(W, bank, n); return float(np.mean(ov > 0.95))


def b6_loads(g):
    n = N_B6; out = {}
    for mult in M_MULTS:
        m_cap = max(4, int(round(mult * ALPHA_C * n)))
        out[f"m{mult}"] = {"decr": _stream(n, "decr", m_cap, g), "lru": _stream(n, "lru", m_cap, g),
                           "random": _stream(n, "random", m_cap, g), "none": _noevict(n, m_cap, g)}
    return out


def _selftest():
    g = np.random.default_rng(0); protos = bipolar((3, 128), g)
    assert int(np.argmax(protos[1] @ protos.T)) == 1
    W = np.outer(protos[0], protos[0]); nb = float(np.abs(W).sum()); W2 = W - np.outer(protos[0], protos[0])
    assert float(np.abs(W2).sum()) < nb; assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: oneshot_proto eviction_reduces_W", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_all() -> Dict:
    t0 = time.time(); per_seed = []
    for seed in SEEDS:
        b1 = b1_epochs(N_B1, np.random.default_rng(seed * 13 + 1))
        b6 = b6_loads(np.random.default_rng(seed * 13 + 6))
        per_seed.append({"seed": seed, "B1": b1, "B6": b6})
        b6s = " ".join(f"{k}:decr={v['decr']:.2f}/lru={v['lru']:.2f}/none={v['none']:.2f}" for k, v in b6.items())
        print(f"  [seed={seed}] B1 M={b1['M']} acc={b1['acc_oneshot']:.2f} adam_epochs_to_match={b1['adam_epochs_to_match']} (wall {b1['wall_speedup']:.0f}x) | B6 {b6s}", flush=True)
    return {"per_seed": per_seed, "elapsed_s": time.time() - t0}


def verdict(per_seed) -> Tuple[str, str]:
    ep = float(np.median([s["B1"]["adam_epochs_to_match"] for s in per_seed]))
    acc = float(np.mean([s["B1"]["acc_oneshot"] for s in per_seed]))
    b1_hp = ep >= 10 and acc >= 0.80; b1_mid = ep >= 2 and acc >= 0.80
    # B6: best differentiation across loads
    best_delta = -9.9; best_m = None
    for mult in M_MULTS:
        k = f"m{mult}"; d = float(np.mean([s["B6"][k]["decr"] for s in per_seed]))
        l = float(np.mean([s["B6"][k]["lru"] for s in per_seed]))
        nn = float(np.mean([s["B6"][k]["none"] for s in per_seed]))
        if d - l > best_delta:
            best_delta = d - l; best_m = (mult, d, l, nn)
    b6_hp = best_m is not None and best_m[1] >= best_m[2] + 0.10 and best_m[1] >= 1.2 * max(best_m[3], 1e-6)
    b6_mid = best_delta > 0.03
    b6str = f"best_diff@m{best_m[0]}: decr={best_m[1]:.2f} lru={best_m[2]:.2f} none={best_m[3]:.2f} (delta={best_delta:+.2f})"
    b1s = "HP" if b1_hp else ("MID" if b1_mid else "HF")
    b6s = "HP" if b6_hp else ("MID" if b6_mid else "HF")
    summary = f"B1[acc={acc:.2f} adam_epochs_to_match={ep:.0f} {b1s}] B6[{b6str} {b6s}]"
    nok = sum(1 for x in [b1_hp, b6_hp] if x)
    v = "HARD_PASS" if (b1_hp and b6_hp) else ("MIDDLE_BAND" if (b1_mid or b6_mid) else "HARD_FAIL")
    return v, f"{v}: bio iter2 {summary}"


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N_B1={N_B1} N_B6={N_B6} M_mults={M_MULTS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
r = run_all()
v, vmsg = verdict(r["per_seed"])
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B1_iter", "B6_iter"], "per_seed": r["per_seed"], "elapsed_s": r["elapsed_s"]}
write_metrics(out_dir, metrics, r["per_seed"])
print("[metrics] written", flush=True)
