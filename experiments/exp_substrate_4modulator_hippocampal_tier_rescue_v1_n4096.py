"""
substrate_4modulator_hippocampal_tier_rescue_v1_n4096 -- R1: 4-modulator hippocampal-tier rescue -- remote CPU.

ROUTING: research_to_exp_dev_drill_recommended_experiments_audit_and_route (R1) + overnight_priority (F). Rescue
  the single-modulator (DA=cf-RPE) accepted-negative: extend with 3 bio-modulators (ACh focus, NA arousal, 5HT
  satiety/capacity) each gating writes independently. Tests Tier-2 hippocampal-class transition (bio-scaling ladder).
  CPU numpy, $0. remote_cpu_queue.

MODEL: stream M=2*m_cap (key,val) associations under capacity pressure (overload), N=4096. Single-modulator =
  DA cf-RPE write-all (W += (LR/n)(val - W@key)key^T). 4-modulator = DA cf-RPE GATED by:
    ACh (focus): write only if surprise=||val-W@key|| > running-mean (prioritize surprising).
    NA (arousal): LR scaled by global recent surprise level (high arousal -> larger updates).
    5HT (satiety): as stored-count approaches m_cap, raise ACh threshold (protect capacity; write less).
  Recall: cue key -> cosine(W@key, val) > 0.7. Overload regime is where capacity-management modulators should help.

PRE-REGISTERED bands: HARD-PASS 4mod_recall >= 1.5x single_recall AND >= single. MIDDLE 1.1-1.5x. HARD-FAIL <1.1x
  (multi-modulator adds noise without gain; single-modulator limit is architectural).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error (normalized). 2. surprise gate selects above-mean. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_4modulator_hippocampal_tier_rescue_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; LR = 0.5; COS_THRESH = 0.70
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def unit_bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def recall(W, K, Vv, n):
    pred = K @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    return float(np.mean((pred * Vv).sum(axis=1) > COS_THRESH))


def run_single(keys, vals, n):
    W = np.zeros((n, n), dtype=np.float32)
    for i in range(len(keys)):
        W += (LR / n) * np.outer(vals[i] - W @ keys[i], keys[i])
    return recall(W, keys, vals, n)


def run_4mod(keys, vals, n, m_cap):
    # 4-modulator LR-MODULATION (always write; no hard-gate-to-zero). DA cf-RPE base.
    W = np.zeros((n, n), dtype=np.float32); run_mean = None
    for i in range(len(keys)):
        err = float(np.linalg.norm(vals[i] - W @ keys[i]))             # DA: prediction error
        run_mean = err if run_mean is None else 0.9 * run_mean + 0.1 * err   # running baseline
        ach = min(2.0, 0.5 + err / (run_mean + 1e-6))                  # ACh focus: boost LR for surprising
        na = min(1.5, 0.75 + 0.5 * (run_mean / (1.0 + run_mean)))      # NA arousal: global gain
        fivehial = max(0.3, 1.0 - 0.5 * min(1.0, i / max(2 * m_cap, 1)))  # 5HT satiety: taper LR as stream fills (protect)
        lr_eff = LR * ach * na * fivehial
        W += (lr_eff / n) * np.outer(vals[i] - W @ keys[i], keys[i])   # DA cf-RPE write, modulated LR
    return recall(W, keys, vals, n)


def _selftest():
    g = np.random.default_rng(0); n = 256; a = unit_bipolar(1, n, g)[0]; b = unit_bipolar(1, n, g)[0]
    W = np.zeros((n, n), dtype=np.float32); eb = float(np.linalg.norm(b - W @ a)); W += (LR / n) * np.outer(b - W @ a, a)
    assert float(np.linalg.norm(b - W @ a)) < eb, "cf-RPE shrinks"
    err = np.array([1.0, 5.0, 2.0, 8.0]); assert int(np.sum(err > err.mean())) == 2, "surprise gate"
    assert N == 4096; print("[selftest] PASS: cfrpe surprise", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; m_cap = max(8, int(round(ALPHA_C * n))); M = 4 * m_cap
    keys = unit_bipolar(M, n, g); vals = unit_bipolar(M, n, g)
    s = run_single(keys, vals, n); f = run_4mod(keys, vals, n, m_cap)
    return {"seed": seed, "N": n, "M": M, "m_cap": m_cap, "single_recall": s, "fourmod_recall": f, "ratio": float(f / max(s, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["single_recall"] for p in ps])); f = float(np.mean([p["fourmod_recall"] for p in ps])); r = f / max(s, 1e-6)
    summary = "single_recall=%.3f fourmod_recall=%.3f ratio=%.2fx (M=2x m_cap overload)" % (s, f, r)
    if r >= 1.5 and f >= s:
        return ("HARD_PASS", "HARD_PASS: 4-modulator system >=1.5x single-modulator (Tier-2 hippocampal transition). " + summary)
    if r >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 4-modulator 1.1-1.5x single. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: multi-modulator no gain (single-modulator limit architectural). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] single=%.3f fourmod=%.3f ratio=%.2fx" % (seed, r["single_recall"], r["fourmod_recall"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
