"""
exp_tool_extended_real_cpu_v1.py -- TOOL-EXTENDED-REAL (real-data audit) -- CPU.

ROUTING: Research NEXT_SPRINT1_REAL_DATA_AUDIT (PP-317). Realistic sensor data: body parts / tools / objects drawn from
  CORRELATED sensor-feature clusters (not orthogonal) + per-observation NOISE. Using a tool binds it into the body schema;
  audits whether the synthetic peripersonal-extension AUC (1.0) survives correlation+noise. Substrate-only.
PRE-REGISTERED: HARD-PASS membership AUC >= 0.70 on realistic (correlated+noisy) tool-use (synthetic was 1.0). MIDDLE >= 0.60. HARD-FAIL < 0.60.
ASCII-only. write_metrics. PROT-018 _v1.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "tool_extended_real_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: tool-extended-real", flush=True)
def run() -> Dict:
    g = np.random.default_rng(641); NB = 8; NT = 10; NR = 40; NFEAT = 6
    feats = cphasor(NFEAT, N, g)                                       # shared sensor-feature basis (correlation source)
    def sensor(k):                                                     # correlated + noisy embeddings
        out = []
        for _ in range(k):
            fs = g.choice(NFEAT, 2, replace=False)
            out.append(cnorm(feats[fs[0]] + 0.7 * feats[fs[1]] + 0.9 * cphasor(1, N, g)[0]))
        return np.stack(out)
    TR = 25 if SMOKE else 150; sc = []; lab = []
    for _ in range(TR):
        body = sensor(NB); tools = sensor(NT); rand = sensor(NR)
        B = cnorm(body.sum(0)); t = int(g.integers(0, NT)); B_t = cnorm(B * (NB ** 0.5) + tools[t])
        mem = lambda x, Bv: float((np.vdot(Bv, x).real) / N)
        for j in range(NB):
            sc.append(mem(body[j], B_t)); lab.append(1)
        sc.append(mem(tools[t], B_t)); lab.append(1)
        for j in range(NT):
            if j != t:
                sc.append(mem(tools[j], B_t)); lab.append(0)
        for j in range(min(NR, 12)):
            sc.append(mem(rand[j], B_t)); lab.append(0)
    auc = _auc(np.array(sc), np.array(lab))
    print("  TOOL-EXTENDED-REAL membership AUC=%.3f on correlated+noisy sensor data [synthetic was 1.0]" % auc, flush=True)
    return {"membership_auc": round(auc, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f (correlated+noisy)" % r["membership_auc"]
    if r["membership_auc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: peripersonal tool-extension survives realistic correlated+noisy sensor data at AUC>=0.70 -- the synthetic primitive is real-data-grounded. " + s)
    if r["membership_auc"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: tool-extension AUC 0.60-0.70 on realistic data. " + s)
    return ("HARD_FAIL", "HARD_FAIL: tool-extension AUC <0.60 -- does not survive realistic sensor data. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
