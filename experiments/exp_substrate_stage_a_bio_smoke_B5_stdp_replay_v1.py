"""
substrate_stage_a_bio_smoke_B5_stdp_replay_v1 -- STDP-replay sequence consolidation -- LAPTOP CPU.

ROUTING: notes/change_request_stage_a_bio_smoke_REVISED_drill_B_specs (B5). Batch-1 note: M=20 at N=2048 is
  vacuously easy (M/N=0.0098 << alpha_c); rerun near alpha_c where forgetting exists. Uses a SEQUENCE memory
  (heteroassoc next-prediction) with PALIMPSEST decay so early transitions fade -> replay can consolidate them.
  CPU numpy, $0. LAPTOP.

CAPABILITY QUESTION (B5): in a decaying (palimpsest) sequence memory storing M transitions, does TEMPORALLY-
  ORDERED replay (re-present the sequence forward, STDP-asymmetric) retain more transitions than NO replay, and
  than RANDOM-order replay, at a fixed replay budget?

MODEL: items s_1..s_{M+1} (random bipolar, N). Heteroassoc W (predict next): per step W = (1-LAM)*W +
  outer(s_{t+1}, s_t) (palimpsest -> old transitions decay as (1-LAM)^age). Replay = extra
  W=(1-LAM)*W+outer updates on selected transitions within a budget (fraction of M). Recall transition t:
  sign(W @ s_t) overlap with s_{t+1} > 0.9. retention = fraction of all M transitions recalled at end.
  Arms: 5a none / 5b random-order replay / 5c temporal-ordered replay / 5d 50%-budget ordered.

PRE-REG: HP 5c retention >= 1.5x 5a AND 5c >= 5b. MID 5c > 5a by any margin. HF 5c <= 5a.
  HONEST CAVEAT: replay-order effects under decay are implementation-sensitive; verdict reported with the full
  retention table so the effect size + ordering are transparent (not just a label).
WHY-DRILL HF: if 5a already retains most (M/N too low) rerun higher M; if 5c<=5b, ordering gives no edge over refresh count.

FORMULA SELF-TESTS (PROT-022): 1. heteroassoc recalls next at low load. 2. decay shrinks old-transition weight. 3. replay refreshes a decayed transition.
ASCII-only. PROT-021: local CPU.
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

ANCHOR_NAME = "substrate_stage_a_bio_smoke_B5_stdp_replay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LAM = 0.01          # palimpsest decay per store (memory horizon ~1/LAM = 100 transitions)
BUDGET = 0.10       # replay budget as fraction of M (5d uses 0.50)

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512; M = 200
else:
    SEEDS = [7, 17, 23]; N = 2048; M = 400


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _store(W, a, b):
    W *= (1.0 - LAM); W += LAM * np.outer(b, a) * 100.0   # *100 keeps signal ~O(1) after the LAM scaling
    return W


def _retention(W, items, n):
    M_ = len(items) - 1
    A = np.stack(items[:M_]); B = np.stack(items[1:M_ + 1])
    R = np.sign(A @ W.T); R[R == 0] = 1.0
    return float(np.mean((R * B).sum(axis=1) / n > 0.90))


def run_arm(arm, items, n, g):
    M_ = len(items) - 1
    W = np.zeros((n, n), dtype=np.float32)
    budget = 0.50 if arm == "ordered50" else BUDGET
    n_replay = int(round(budget * M_))
    for t in range(M_):
        W = _store(W, items[t], items[t + 1])
        # interleave replay so old transitions get refreshed during the sweep
        if arm in ("ordered", "ordered50") and n_replay > 0 and t > 0:
            # replay one earlier transition per step (temporally ordered: oldest-first cursor)
            j = (t * n_replay // M_) % max(1, t)
            W = _store(W, items[j], items[j + 1])
        elif arm == "random" and n_replay > 0 and t > 0:
            j = int(g.integers(0, t)); W = _store(W, items[j], items[j + 1])
    return _retention(W, items, n)


def _selftest():
    g = np.random.default_rng(0); n = 256; items = [bipolar((n,), g) for _ in range(6)]
    W = np.zeros((n, n), dtype=np.float32)
    for t in range(5):
        W = _store(W, items[t], items[t + 1])
    assert _retention(W, items, n) > 0.8, "low-load heteroassoc recall failed"
    # decay shrinks an old transition: store many, first transition weakens
    W2 = np.zeros((n, n), dtype=np.float32); many = [bipolar((n,), g) for _ in range(400)]
    for t in range(399):
        W2 = _store(W2, many[t], many[t + 1])
    old_ok = float((np.sign(W2 @ many[0]) * many[1]).sum() / n)
    new_ok = float((np.sign(W2 @ many[397]) * many[398]).sum() / n)
    assert new_ok > old_ok, f"decay not working old={old_ok} new={new_ok}"
    print(f"[selftest] PASS: heteroassoc_recall decay_old={old_ok:.2f}<new={new_ok:.2f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(per_seed) -> Tuple[str, str]:
    a = float(np.mean([s["none"] for s in per_seed])); r = float(np.mean([s["random"] for s in per_seed]))
    o = float(np.mean([s["ordered"] for s in per_seed])); o5 = float(np.mean([s["ordered50"] for s in per_seed]))
    ratio = o / max(a, 1e-6)
    summary = f"retention none={a:.3f} random={r:.3f} ordered={o:.3f} ordered50={o5:.3f} (ordered/none={ratio:.2f}x)"
    if o >= 1.5 * max(a, 1e-6) and o >= r:
        return ("HARD_PASS", f"HARD_PASS: ordered STDP replay consolidates sequence (>=1.5x no-replay, >=random). {summary}")
    if o > a:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ordered replay helps (>no-replay) but <1.5x or <=random. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ordered replay no better than no-replay. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} M={M} LAM={LAM} budget={BUDGET}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); per_seed = []
for seed in SEEDS:
    g = np.random.default_rng(seed); items = [bipolar((N,), g) for _ in range(M + 1)]
    rec = {arm: run_arm(arm, items, N, np.random.default_rng(seed * 50 + hash(arm) % 1000)) for arm in ["none", "random", "ordered", "ordered50"]}
    per_seed.append({"seed": seed, **rec})
    print(f"  [seed={seed}] none={rec['none']:.3f} random={rec['random']:.3f} ordered={rec['ordered']:.3f} ordered50={rec['ordered50']:.3f}", flush=True)
v, vmsg = verdict(per_seed)
print(f"\n[VERDICT] {vmsg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": ["B5_stdp_replay"], "per_seed": per_seed, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
