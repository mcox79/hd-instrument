"""
substrate_stage_a_bio_b36_mixed_stream_v1 -- B36 on a MIXED (redundant + novel) stream -- remote CPU.

ROUTING: research_to_exp_dev_B36_refutation_acknowledged_refined_taxonomy (B36-mixed discriminator). On a
  single-stream fixed-vocab task B3b gating SUBSUMED B6 eviction. Hypothesis: on a MIXED stream (50% redundant
  repeats + 50% novel patterns) BOTH bind -- B3b skips redundant; B6 evicts to fit novel -> predicted SUPERADDITIVE.
  CPU numpy, $0. remote_cpu_queue.

MODEL: T arrivals; each REDUNDANT (repeat from small vocab V_red, prob 0.5) or NOVEL (fresh bipolar, prob 0.5).
  W + bank cap m_cap. GATE(B3b): skip write if recalled>0.9. EVICT(B6): drop lowest self-overlap when bank>m_cap.
  recall = frac of DISTINCT patterns seen recalled at end. arms none/gate/evict/both. m_cap=alpha_c*N.

PRE-REG (gain=recall(arm)-recall(none)): HARD-PASS gain(both)>gain(gate)+gain(evict) (SUPERADDITIVE on mixed).
  MIDDLE: gain(both)>max(gate,evict) additive. HARD-FAIL: subsumed.
SELF-TESTS (PROT-022): 1. stored recall. 2. eviction reduces ||W||. 3. alpha_c=0.138.
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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

ANCHOR_NAME = "substrate_stage_a_bio_b36_mixed_stream_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
GATE_THRESH = 0.90
RECALL_THRESH = 0.95
P_REDUNDANT = 0.5
ARMS = ["none", "gate", "evict", "both"]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512
else:
    SEEDS = [7, 17, 23]; N = 2048


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def _ov(W, x, n):
    r = np.sign(W @ x); r[r == 0] = 1.0
    return float((r * x).sum() / n)


def run_arm(arm, n, m_cap, g):
    V_red = max(2, m_cap // 2)
    vocab = bipolar((V_red, n), g)
    W = np.zeros((n, n), dtype=np.float32); bank = []
    distinct = {}                                  # key -> vec
    T = 6 * m_cap; novel_count = 0
    for t in range(T):
        if g.random() < P_REDUNDANT:
            vid = int(g.integers(0, V_red)); x = vocab[vid]; key = ("r", vid)
        else:
            x = bipolar((n,), g); key = ("n", novel_count); novel_count += 1
        if key not in distinct:
            distinct[key] = x
        if arm in ("gate", "both") and len(bank) > 0 and _ov(W, x, n) > GATE_THRESH:
            continue
        W += np.outer(x, x); np.fill_diagonal(W, 0.0); bank.append((key, x))
        if arm in ("evict", "both") and len(bank) > m_cap:
            ovs = np.array([_ov(W, v, n) for _, v in bank]); ev = int(np.argmin(ovs))
            _, xe = bank.pop(ev); W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    items = list(distinct.items())
    if len(items) > 400:
        sel = g.choice(len(items), 400, replace=False); items = [items[i] for i in sel]
    rec = np.mean([_ov(W, v, n) > RECALL_THRESH for _, v in items])
    return float(rec)


def _selftest():
    g = np.random.default_rng(0); n = 256; x = bipolar((n,), g); W = np.outer(x, x); np.fill_diagonal(W, 0.0)
    assert _ov(W, x, n) > GATE_THRESH, "stored recall"
    nb = float(np.abs(W).sum()); W2 = W - np.outer(x, x); np.fill_diagonal(W2, 0.0); assert float(np.abs(W2).sum()) < nb
    assert abs(ALPHA_C - 0.138) < 1e-6
    print("[selftest] PASS: gate_recall eviction_reduces_W", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    m_cap = max(8, int(round(ALPHA_C * N)))
    out = {arm: run_arm(arm, N, m_cap, np.random.default_rng(seed * 50 + i)) for i, arm in enumerate(ARMS)}
    return {"seed": seed, "N": N, "m_cap": m_cap, **out}


def verdict(ps) -> Tuple[str, str]:
    m = {arm: float(np.mean([p[arm] for p in ps])) for arm in ARMS}
    gg = m["gate"] - m["none"]; ge = m["evict"] - m["none"]; gb = m["both"] - m["none"]
    summary = "recall none=%.2f gate=%.2f evict=%.2f both=%.2f | gains gate=%+.2f evict=%+.2f both=%+.2f (sum=%+.2f)" % (
        m["none"], m["gate"], m["evict"], m["both"], gg, ge, gb, gg + ge)
    if gb > gg + ge + 0.02:
        return ("HARD_PASS", "HARD_PASS: B3b+B6 SUPERADDITIVE on mixed stream (both bind). " + summary)
    if gb > max(gg, ge) + 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: both > max single (additive). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: still subsumed on mixed stream. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] none=%.2f gate=%.2f evict=%.2f both=%.2f" % (seed, r["none"], r["gate"], r["evict"], r["both"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
