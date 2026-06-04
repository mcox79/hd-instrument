"""
substrate_stage_a_bio_b36_composition_v1 -- B3b gating x B6 D-ECR eviction composition -- LAPTOP CPU.

ROUTING: notes/research_to_exp_dev_B3b_mechanism_B36_prediction_2026-06-04 + round2_response_plan (Priority 1).
  B3b = input-side capacity management (gate writes by surprise -> keep alpha sub-critical); B6 D-ECR =
  output-side capacity management (evict lowest energy-contribution when full). Complementary mechanisms on the
  SAME capacity axis. Predicted SUPERADDITIVE at near-capacity, ADDITIVE at low load. CPU numpy, $0. LAPTOP.

UNIFIED CAPACITY-PRESSURE TASK: a pattern VOCABULARY of V distinct bipolar patterns (N) streamed with Zipf
  repetition (T=5V arrivals). Substrate W (auto-assoc Hopfield) + bank (for eviction). Per arrival x:
    GATE (B3b): if already well-recalled (overlap(x, sign(Wx)) > 0.9) -> SKIP write (don't waste capacity on
                known patterns). else write W += xx^T, register in bank.
    EVICT (B6): if |bank| > m_cap -> remove lowest self-overlap pattern (W -= xx^T).
  m_cap = alpha_c * N (the single-substrate capacity). recall = frac of the V distinct vocab patterns with
  overlap(x, sign(Wx)) > 0.95 at end.

ARMS: none (write-all, no-evict) / gate (B3b only) / evict (B6 only) / both (B36).
LOADS (V relative to m_cap): low V=0.5*m_cap / near V=0.9*m_cap / over V=1.5*m_cap.

PRE-REG (per drill): gain(arm) = recall(arm) - recall(none).
  HARD-PASS: at NEAR load, gain(both) > gain(gate)+gain(evict) (superadditive) AND at LOW load both ~ additive.
  MIDDLE: near-load additive only (gain(both) ~ gain(gate)+gain(evict)).
  HARD-FAIL: near-load gain(both) < max(gain(gate), gain(evict)) (composition collapse).

FORMULA SELF-TESTS (PROT-022): 1. gate skips an already-stored pattern. 2. eviction reduces ||W||. 3. zipf stream repeats. 4. alpha_c=0.138.
ASCII-only. PROT-021: local CPU. anchor _b36_composition_v1.
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

ANCHOR_NAME = "substrate_stage_a_bio_b36_composition_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
GATE_THRESH = 0.90       # skip writing if current recall overlap exceeds this (already known)
RECALL_THRESH = 0.95
LOADS = {"low": 0.5, "near": 0.9, "over": 1.5}

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512
else:
    SEEDS = [7, 17, 23]; N = 2048


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _recall_overlap(W, x, n):
    r = np.sign(W @ x); r[r == 0] = 1.0
    return float((r * x).sum() / n)


def run_arm(arm, vocab, stream, n, m_cap):
    W = np.zeros((n, n), dtype=np.float32)
    bank = {}            # vocab_id -> True (currently stored)
    for vid in stream:
        x = vocab[vid]
        if arm in ("gate", "both") and len(bank) > 0:
            if _recall_overlap(W, x, n) > GATE_THRESH:   # already known -> skip (B3b prevention)
                continue
        W += np.outer(x, x); np.fill_diagonal(W, 0.0); bank[vid] = True
        if arm in ("evict", "both") and len(bank) > m_cap:   # B6 D-ECR correction
            ids = list(bank.keys())
            ov = np.array([_recall_overlap(W, vocab[i], n) for i in ids])
            ev = ids[int(np.argmin(ov))]
            W -= np.outer(vocab[ev], vocab[ev]); np.fill_diagonal(W, 0.0); del bank[ev]
    # recall over the full vocabulary
    rec = np.mean([_recall_overlap(W, vocab[i], n) > RECALL_THRESH for i in range(len(vocab))])
    return float(rec)


def _zipf_stream(V, T, g):
    ranks = 1.0 / np.arange(1, V + 1); p = ranks / ranks.sum()
    return g.choice(V, size=T, p=p)


def run_load(n, load_mult, g):
    m_cap = max(4, int(round(ALPHA_C * n)))
    V = max(4, int(round(load_mult * m_cap))); T = 5 * V
    vocab = bipolar((V, n), g); stream = _zipf_stream(V, T, g)
    return {arm: run_arm(arm, vocab, stream, n, m_cap) for arm in ["none", "gate", "evict", "both"]}


def _selftest():
    g = np.random.default_rng(0); n = 256
    x = bipolar((n,), g); W = np.outer(x, x); np.fill_diagonal(W, 0.0)
    assert _recall_overlap(W, x, n) > GATE_THRESH, "stored pattern not recalled (gate skip needs this)"
    nb = float(np.abs(W).sum()); W2 = W - np.outer(x, x); np.fill_diagonal(W2, 0.0); assert float(np.abs(W2).sum()) < nb
    s = _zipf_stream(10, 200, g); assert len(s) == 200 and len(set(s.tolist())) <= 10 and len(s) > len(set(s.tolist())), "stream not repeating"
    assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: gate_recall eviction_reduces_W zipf_repeats", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    def mean(load, arm):
        return float(np.mean([s[load][arm] for s in per_seed]))
    out = {}
    for load in LOADS:
        none = mean(load, "none"); g = mean(load, "gate") - none; e = mean(load, "evict") - none; b = mean(load, "both") - none
        out[load] = (none, g, e, b)
    nl = out["near"]; superad_near = nl[3] > nl[1] + nl[2] + 1e-6
    low = out["low"]; additive_low = abs(low[3] - (low[1] + low[2])) <= 0.05 + 1e-6
    collapse = nl[3] < max(nl[1], nl[2])
    summary = " | ".join(f"{ld}: none={out[ld][0]:.2f} gain[gate={out[ld][1]:+.2f} evict={out[ld][2]:+.2f} both={out[ld][3]:+.2f}]" for ld in LOADS)
    if superad_near and additive_low:
        return ("HARD_PASS", f"HARD_PASS: B36 superadditive at near-capacity, additive at low (clean composition). {summary}")
    if superad_near:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: B36 superadditive at near-cap but low-load not cleanly additive. {summary}")
    if collapse:
        return ("HARD_FAIL", f"HARD_FAIL: B36 composition collapse at near-cap (both < max single). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: B36 additive (not superadditive) at near-cap. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} loads={LOADS} gate_thresh={GATE_THRESH}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    res = {load: run_load(N, mult, np.random.default_rng(seed * 30 + i)) for i, (load, mult) in enumerate(LOADS.items())}
    per_seed.append(res)
    print(f"  [seed={seed}] " + " | ".join(f"{ld}:none={res[ld]['none']:.2f}/gate={res[ld]['gate']:.2f}/evict={res[ld]['evict']:.2f}/both={res[ld]['both']:.2f}" for ld in LOADS), flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B36_low", "B36_near", "B36_over"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
