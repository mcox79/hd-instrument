"""
substrate_b5_escapeB_cfrpe_weighted_replay_v1_n2048 -- B5 Escape B: cf-RPE non-commutative replay -- remote CPU.

ROUTING: exp_dev_handoff_research_substrate_negative_results_structural_analysis_2x (Escape #3, B5). B5 negative
  (palimpsest + bounded both HF) root cause: ADDITIVE-W is COMMUTATIVE -> replay ORDER algebraically irrelevant.
  Escape B: use cf-RPE DELTA-RULE writes (W += (LR/n)(s_next - W@s_cur)s_cur^T) which are NON-COMMUTATIVE (each
  write depends on current W) -> replay order CAN matter (Wright-Fisher: earlier items shift the baseline). Test:
  does ORDERED cf-RPE replay now beat RANDOM-order? CPU numpy, $0. remote_cpu_queue.

MODEL: sequence of M transitions s_t->s_{t+1} (N=2048); palimpsest decay alpha=0.003 on main writes; replay
  (10% budget) re-applies cf-RPE delta updates either in temporal ORDER (5c) or RANDOM order (5b), vs none (5a).
  cf-RPE write is order-dependent. retention = frac transitions recalled (sign(W@s_t) overlap s_{t+1} > 0.9).

CELLS (3 seeds): retention {none, random, ordered, ordered50}. M=333 (~alpha_c regime).
PRE-REGISTERED bands (per handoff): HARD-PASS ordered/none >= 1.15 AND ordered >= random (cf-RPE rescues replay
  via non-commutativity). MIDDLE: ordered/none in [1.02, 1.15). HARD-FAIL: < 1.02 (B5 FULLY FUNDAMENTAL; no
  in-substrate Hebbian-write rescue).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks transition error (normalized). 2. cf-RPE write is order-dependent (W differs by order). 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
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

ANCHOR_NAME = "substrate_b5_escapeB_cfrpe_weighted_replay_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA = 0.003
LR = 0.5
BUFFER = 50
BATCH_END = 10
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; M = 200
else:
    SEEDS = [7, 17, 23]; N_DIM = N; M = 333


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def cfrpe_write(W, a, b, n):
    W += (LR / n) * np.outer(b - W @ a, a)     # non-commutative delta rule


def retention(W, items, n):
    M_ = len(items) - 1
    A = np.stack(items[:M_]); B = np.stack(items[1:M_ + 1])
    R = np.sign(A @ W.T); R[R == 0] = 1.0
    return float(np.mean((R * B).sum(axis=1) / n > 0.90))


def run_arm(arm, items, n, g):
    M_ = len(items) - 1; W = np.zeros((n, n), dtype=np.float32); buf = []
    budget = 0.50 if arm == "ordered50" else (0.10 if arm in ("ordered", "random") else 0.0)
    total = int(round(budget * M_)); done = 0
    per_event = max(1, total // max(1, M_ // BATCH_END)) if total else 0
    for t in range(M_):
        W *= (1.0 - ALPHA)                       # palimpsest decay
        cfrpe_write(W, items[t], items[t + 1], n)
        buf.append(t)
        if len(buf) > BUFFER:
            buf.pop(0)
        if per_event and (t + 1) % BATCH_END == 0 and done < total:
            k = min(per_event, total - done)
            if arm == "random":
                sel = [buf[int(g.integers(0, len(buf)))] for _ in range(k)]
            else:
                sel = [buf[i % len(buf)] for i in range(k)]    # ordered sweep (oldest-first)
            for j in sel:
                cfrpe_write(W, items[j], items[j + 1], n)       # cf-RPE replay (order-dependent, no decay)
            done += k
    return retention(W, items, n)


def _selftest():
    g = np.random.default_rng(0); n = 256; a, b = bipolar((n,), g), bipolar((n,), g)
    W = np.zeros((n, n), dtype=np.float32); eb = float(np.linalg.norm(b - W @ a)); cfrpe_write(W, a, b, n)
    assert float(np.linalg.norm(b - W @ a)) < eb, "cf-RPE shrinks"
    # order-dependence: two writes in different order -> different W
    c, d = bipolar((n,), g), bipolar((n,), g)
    W1 = np.zeros((n, n), dtype=np.float32); cfrpe_write(W1, a, b, n); cfrpe_write(W1, c, d, n)
    W2 = np.zeros((n, n), dtype=np.float32); cfrpe_write(W2, c, d, n); cfrpe_write(W2, a, b, n)
    assert float(np.abs(W1 - W2).sum()) > 1e-3, "cf-RPE write not order-dependent"
    assert N == 2048
    print("[selftest] PASS: cfrpe_shrinks order_dependent", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([s["none"] for s in ps])); r = float(np.mean([s["random"] for s in ps]))
    o = float(np.mean([s["ordered"] for s in ps])); o5 = float(np.mean([s["ordered50"] for s in ps]))
    ratio = o / max(a, 1e-6)
    summary = "retention none=%.3f random=%.3f ordered=%.3f ordered50=%.3f (ordered/none=%.2fx)" % (a, r, o, o5, ratio)
    if ratio >= 1.15 and o >= r:
        return ("HARD_PASS", "HARD_PASS: cf-RPE non-commutative replay RESCUES B5 (ordered>=1.15x none). " + summary)
    if ratio >= 1.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial cf-RPE replay benefit (1.02-1.15x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: B5 FULLY FUNDAMENTAL -- no Hebbian-write replay rescue. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d alpha=%.3f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M, ALPHA), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    g = np.random.default_rng(seed); items = [bipolar((N_DIM,), g) for _ in range(M + 1)]
    rec = {arm: run_arm(arm, items, N_DIM, np.random.default_rng(seed * 50 + i)) for i, arm in enumerate(["none", "random", "ordered", "ordered50"])}
    ps.append({"seed": seed, **rec})
    print("  [seed=%d] none=%.3f random=%.3f ordered=%.3f ordered50=%.3f" % (seed, rec["none"], rec["random"], rec["ordered"], rec["ordered50"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
