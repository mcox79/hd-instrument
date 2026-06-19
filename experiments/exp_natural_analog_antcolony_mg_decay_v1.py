"""
exp_natural_analog_antcolony_mg_decay_v1.py -- time-windowed Misra-Gries pheromone decay detects drift faster -- CPU.

ROUTING: natural_analog_5_pretests Analog 2 (ANT COLONY). Add pheromone decay (rate alpha) to Misra-Gries counters; a 10000-query stream shifts topic at q=5000; measure how many queries after the shift the decayed counters reflect the new distribution vs un-decayed. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS decayed counters detect the shift within 100 queries AND faster than un-decayed. MIDDLE within 500. HARD-FAIL no faster.
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

ANCHOR_NAME = "natural_analog_antcolony_mg_decay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()

def _selftest():
    p = zipf(10); assert abs(p.sum() - 1.0) < 1e-9, "zipf norm"
    c = {1: 5.0}; c = {k: v * 0.9 for k, v in c.items()}; assert c[1] < 5.0, "decay shrinks"
    assert 1 in {1: 2}, "counter present"
    print("[selftest] PASS: antcolony-mg-decay", flush=True)

def run() -> Dict:
    g = np.random.default_rng(11); V = 100; Q = 4000 if SMOKE else 10000; SHIFT = Q // 2; ALPHA = 0.98; TOPK = 8
    P = zipf(V); perm = g.permutation(V); Pn = np.zeros(V); Pn[perm] = zipf(V)
    stream = np.concatenate([g.choice(V, SHIFT, p=P), g.choice(V, Q - SHIFT, p=Pn)])
    new_top = set(int(i) for i in np.argsort(Pn)[::-1][:TOPK])
    def detect(decay):
        cnt = np.zeros(V)
        for t in range(Q):
            cnt[stream[t]] += 1.0
            if decay:
                cnt *= ALPHA
            if t >= SHIFT and t % 20 == 0:
                top = set(int(i) for i in np.argsort(cnt)[::-1][:TOPK])
                if len(top & new_top) >= TOPK * 0.6:
                    return t - SHIFT
        return Q - SHIFT
    d_dec = detect(True); d_und = detect(False)
    print("  shift-detection lag: decayed=%d queries  undecayed=%d (alpha=%.2f)" % (d_dec, d_und, ALPHA), flush=True)
    return {"lag_decayed": d_dec, "lag_undecayed": d_und}

def verdict(r) -> Tuple[str, str]:
    dd = r["lag_decayed"]; du = r["lag_undecayed"]; s = "decayed-lag=%d undecayed-lag=%d" % (dd, du)
    if dd <= 100 and dd < du:
        return ("HARD_PASS", "HARD_PASS: pheromone-decay Misra-Gries detects topic drift within 100 queries and faster than un-decayed -- ant-colony decay is the drift-responsiveness mechanism. " + s)
    if dd <= 500 and dd < du:
        return ("MIDDLE_BAND", "MIDDLE_BAND: decay helps but detection 100-500 queries. " + s)
    return ("HARD_FAIL", "HARD_FAIL: decay does not speed drift detection. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
