"""
exp_ensemble_vote_cpu_v1.py -- majority vote across independent substrates beats a single one under noise -- CPU.

ROUTING: CPU substrate capability characterization (ensemble majority vote). Store the same items in R independent random-sign substrates; recall a noisy query in each; majority-vote the predicted index. Vote accuracy should exceed single-substrate accuracy (error averaging). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS vote accuracy >= single + 0.05 at heavy noise. MIDDLE >= single. HARD-FAIL vote < single.
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
ANCHOR_NAME = "ensemble_vote_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    from collections import Counter; assert Counter([1, 1, 2]).most_common(1)[0][0] == 1, "vote"; print("[selftest] PASS: ensemble-vote-cpu", flush=True)
def run() -> Dict:
    from collections import Counter
    g = np.random.default_rng(35); N = 3000 if SMOKE else 8000; D = 256; R = 5; NQ = 400; FLIP = 0.40
    base = np.sign(g.standard_normal((N, D))).astype(np.float32)
    projs = [g.standard_normal((D, D)) for _ in range(R)]; subs = [np.sign(base @ P) for P in projs]
    qi = g.choice(N, NQ, replace=False); single_hits = 0; vote_hits = 0
    for n, i in enumerate(qi):
        preds = []
        for ridx in range(R):
            q = subs[ridx][i].copy(); fl = g.random(D) < FLIP; q[fl] *= -1; preds.append(int(np.argmax(q @ subs[ridx].T)))
        single_hits += int(preds[0] == i); vote_hits += int(Counter(preds).most_common(1)[0][0] == i)
    single = single_hits / NQ; vote = vote_hits / NQ; print("  single=%.3f vote(R=%d)=%.3f gain=%.3f (flip=%.2f)" % (single, R, vote, vote - single, FLIP), flush=True)
    return {"single": single, "vote": vote, "gain": vote - single}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f vote=%.3f gain=%.3f" % (r["single"], r["vote"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: ensemble majority vote beats single substrate by >=0.05 -- error-averaging redundancy improves recall. " + s)
    if r["gain"] >= 0.0: return ("MIDDLE_BAND", "MIDDLE_BAND: vote >= single but gain <0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: vote worse than single. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
