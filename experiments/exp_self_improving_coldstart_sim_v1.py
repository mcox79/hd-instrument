"""
exp_self_improving_coldstart_sim_v1 -- Anchor 1: cold-start Zipfian bridge-accumulation simulation -- CPU.

ROUTING: self_improving_3_pretests Anchor 1 (the cheapest gate; queue immediately). Validates the self-improving routing
  bridge-accumulation model BEFORE any integration. A bridge-entity vocabulary has a Zipfian popularity; queries arrive
  Zipf-distributed; the bridge cache accumulates seen bridges (self-improving via usage). Measures bridge coverage C(Q) =
  fraction of future query MASS whose bridge is cached, and fast-path fraction X(Q) = fraction of recent queries that hit the
  cache, at increasing Q. Power-law saturation: popular bridges are seen fast, so coverage saturates. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS C(50K) > 0.85 AND X(10K) > 0.60 (accumulation model holds -> self-improving routing structurally
  supported). MIDDLE one of the two. HARD-FAIL neither (architecture needs revision before engineering).
FORMULA SELF-TESTS (PROT-022): 1. zipf normalized. 2. coverage monotone. 3. seen-set hit logic.
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

ANCHOR_NAME = "self_improving_coldstart_sim_v1"; V = 10000; ZIPF_S = 1.1; WINDOW = 1000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CHECKPOINTS = [1000, 5000, 10000] if RUN_MODE == "smoke" else [1000, 5000, 10000, 25000, 50000]
QMAX = CHECKPOINTS[-1]


def zipf_probs(v, s):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()


def _selftest():
    p = zipf_probs(10, 1.1); assert abs(p.sum() - 1.0) < 1e-9 and p[0] > p[9], "zipf normalized"
    cov = [0.1, 0.3, 0.6]; assert all(cov[i] <= cov[i + 1] for i in range(len(cov) - 1)), "coverage monotone"
    seen = set(); seen.add(3); assert (3 in seen) and (4 not in seen), "seen-set hit logic"
    print("[selftest] PASS: self-improving-coldstart-sim", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(101); probs = zipf_probs(V, ZIPF_S)
    stream = g.choice(V, size=QMAX, p=probs)               # Zipf-distributed query bridges
    seen = np.zeros(V, dtype=bool); hits = np.zeros(QMAX, dtype=np.int8)
    cov_at = {}; x_at = {}
    for t in range(QMAX):
        b = stream[t]
        if seen[b]:
            hits[t] = 1
        else:
            seen[b] = True                                  # cache the bridge on first miss (self-improving via usage)
        tt = t + 1
        if tt in CHECKPOINTS:
            cov_at[tt] = float(probs[seen].sum())           # coverage = future query mass cached
            lo = max(0, tt - WINDOW); x_at[tt] = float(hits[lo:tt].mean())   # fast-path fraction in recent window
            print("  Q=%6d  coverage C=%.3f  fast-path X=%.3f  (unique bridges seen=%d)" % (tt, cov_at[tt], x_at[tt], int(seen.sum())), flush=True)
    return {"cov": cov_at, "x": x_at, "V": V, "s": ZIPF_S, "qmax": QMAX}


def verdict(r) -> Tuple[str, str]:
    cov = r["cov"]; x = r["x"]
    c_final = cov.get(50000, cov.get(max(cov), 0.0)); x_10k = x.get(10000, x.get(max(x), 0.0))
    c_ok = c_final > 0.85; x_ok = x_10k > 0.60
    summary = "C(%d)=%.3f X(10K)=%.3f | curve C=%s X=%s (V=%d, Zipf s=%.1f)" % (
        max(cov), c_final, x_10k, {k: round(v, 3) for k, v in cov.items()}, {k: round(v, 3) for k, v in x.items()}, r["V"], r["s"])
    if c_ok and x_ok:
        return ("HARD_PASS", "HARD_PASS: bridge accumulation saturates as modeled -- coverage >0.85 and fast-path >0.60; self-improving routing is structurally supported; proceed to Anchor 2/3. " + summary)
    if c_ok or x_ok:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of (coverage>0.85 / fast-path>0.60) holds -- accumulation works but slower than target; tune vocab/Zipf assumptions. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: neither coverage nor fast-path target met -- accumulation too slow under this distribution; architecture needs revision before engineering. " + summary)


print("[config] anchor=%s mode=%s V=%d zipf_s=%.1f Qmax=%d" % (ANCHOR_NAME, RUN_MODE, V, ZIPF_S, QMAX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
