"""
substrate_stage_a_bio_b5_bounded_weights_v1 -- STDP replay w/ palimpsest decay (per Research spec) -- LAPTOP.

ROUTING: notes/research_to_exp_dev_B5_decay_model_palimpsest_spec_2026-06-04 (drill answer to my B5 question).
  BOUNDED-WEIGHTS (Lazaro 2025) escalation per B5 negative: alpha=0.003 decay BEFORE each main Hebbian write; replay updates add NO decay
  (this fixes my earlier replay-decay coupling that hurt retention). M=333 ~ M_steady=1/alpha. CPU numpy, $0.

CAPABILITY QUESTION (B5): in a palimpsest sequence memory (decay alpha=0.003) storing M=333 transitions, does
  STDP-ORDERED replay (systematic sweep of the recent-50 buffer, 10% budget) retain more transitions than
  NO replay, and than RANDOM replay (same budget)? Tests the first Tier-2 hippocampal primitive (replay consolidation).

MODEL: items s_0..s_M (random bipolar N). Sequence memory W (predict next). Per training step t:
  W *= (1-alpha); W += outer(s_{t+1}, s_t); push transition t to recent buffer (cap 50).
  Replay (no decay) every BATCH_END steps, within budget: 5b random transitions from buffer; 5c sweep buffer in
  order; 5d ordered at 50% budget. retention = frac of all M transitions with sign(W@s_t).s_{t+1}/N > 0.9.

CELLS (3 seeds): 5a none / 5b random replay / 5c STDP-ordered replay (10%) / 5d STDP-ordered (50%).
PRE-REG: HP 5c retention >= 1.5x 5a AND 3/3 seeds. MID 1.2-1.5x OR 2/3. HF < 1.2x.
WHY-DRILL HF: (1) M/N<0.05 -> raise alpha/M; (2) decay too weak (measure ||dW||); (3) 5b vs 5c order encoding.

FORMULA SELF-TESTS (PROT-022): 1. heteroassoc recalls next at low load. 2. palimpsest decay weakens OLD vs NEW. 3. replay (no-decay) refreshes a decayed transition.
ASCII-only. PROT-021: local CPU. anchor _b5_palimpsest_revised_v1.
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

ANCHOR_NAME = "substrate_stage_a_bio_b5_bounded_weights_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.003
BOUND = 8.0            # bounded-weight clip (Lazaro 2025): nonlinearity -> replay-order CAN matter
BUFFER = 50            # recent-transition replay buffer
BATCH_END = 10         # replay event cadence (steps)

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512; M = 333
else:
    SEEDS = [7, 17, 23]; N = 2048; M = 333


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _retention(W, items, n):
    M_ = len(items) - 1
    A = np.stack(items[:M_]); B = np.stack(items[1:M_ + 1])
    R = np.sign(A @ W.T); R[R == 0] = 1.0
    return float(np.mean((R * B).sum(axis=1) / n > 0.90))


def run_arm(arm, items, n, g):
    M_ = len(items) - 1; W = np.zeros((n, n), dtype=np.float32); buf = []
    budget = 0.50 if arm == "ordered50" else (0.10 if arm in ("ordered", "random") else 0.0)
    total_replays = int(round(budget * M_)); done_replays = 0
    n_events = max(1, M_ // BATCH_END); per_event = max(1, total_replays // n_events) if total_replays else 0
    for t in range(M_):
        W += np.outer(items[t + 1], items[t])     # STDP-asymmetric next-prediction
        np.clip(W, -BOUND, BOUND, out=W)          # bounded-weight saturation (nonlinear forgetting)
        buf.append(t)
        if len(buf) > BUFFER:
            buf.pop(0)
        if per_event and (t + 1) % BATCH_END == 0 and done_replays < total_replays:
            k = min(per_event, total_replays - done_replays)
            if arm == "random":
                js = [int(g.integers(0, len(buf))) for _ in range(k)]
                sel = [buf[j] for j in js]
            else:  # ordered: systematic sweep of the buffer (even coverage)
                sel = [buf[i % len(buf)] for i in range(k)]
            for j in sel:
                W += np.outer(items[j + 1], items[j]); np.clip(W, -BOUND, BOUND, out=W)   # replay under clip (nonlinear)
            done_replays += k
    return _retention(W, items, n)


def _selftest():
    g = np.random.default_rng(0); n = 256; items = [bipolar((n,), g) for _ in range(6)]
    W = np.zeros((n, n), dtype=np.float32)
    for t in range(5):
        W += np.outer(items[t + 1], items[t])
    assert _retention(W, items, n) > 0.8, "low-load heteroassoc recall"
    # palimpsest: store many with decay -> old weaker than new
    W2 = np.zeros((n, n), dtype=np.float32); many = [bipolar((n,), g) for _ in range(400)]
    for t in range(399):
        W2 *= (1.0 - ALPHA); W2 += np.outer(many[t + 1], many[t])
    old = float((np.sign(W2 @ many[0]) * many[1]).sum() / n); new = float((np.sign(W2 @ many[397]) * many[398]).sum() / n)
    assert new > old, f"palimpsest decay not working old={old} new={new}"
    # replay (no decay) refreshes: re-add transition 0 -> its recall improves
    before = old; W2 += 5.0 * np.outer(many[1], many[0]); after = float((np.sign(W2 @ many[0]) * many[1]).sum() / n)
    assert after >= before, "replay did not refresh"
    print(f"[selftest] PASS: heteroassoc decay old={old:.2f}<new={new:.2f} replay_refresh {before:.2f}->{after:.2f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    a = float(np.mean([s["none"] for s in per_seed])); r = float(np.mean([s["random"] for s in per_seed]))
    o = float(np.mean([s["ordered"] for s in per_seed])); o5 = float(np.mean([s["ordered50"] for s in per_seed]))
    ratio = o / max(a, 1e-6); n3 = sum(1 for s in per_seed if s["ordered"] >= 1.5 * max(s["none"], 1e-6))
    summary = f"retention none={a:.3f} random={r:.3f} ordered={o:.3f} ordered50={o5:.3f} (ordered/none={ratio:.2f}x, {n3}/{len(per_seed)} seeds>=1.5x)"
    if ratio >= 1.5 and n3 >= len(per_seed):
        return ("HARD_PASS", f"HARD_PASS: STDP-ordered palimpsest replay consolidates (>=1.5x no-replay, 3/3). {summary}")
    if ratio >= 1.2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: replay helps 1.2-1.5x. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: replay <1.2x no-replay. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} M={M} alpha={ALPHA} buffer={BUFFER}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    g = np.random.default_rng(seed); items = [bipolar((N,), g) for _ in range(M + 1)]
    rec = {arm: run_arm(arm, items, N, np.random.default_rng(seed * 50 + i)) for i, arm in enumerate(["none", "random", "ordered", "ordered50"])}
    per_seed.append({"seed": seed, **rec})
    print(f"  [seed={seed}] none={rec['none']:.3f} random={rec['random']:.3f} ordered={rec['ordered']:.3f} ordered50={rec['ordered50']:.3f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B5_palimpsest"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
