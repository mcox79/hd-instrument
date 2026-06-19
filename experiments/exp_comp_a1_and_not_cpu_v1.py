"""
exp_comp_a1_and_not_cpu_v1.py -- conjunctive-with-exclusion query: subjects with property P AND NOT property Q -- CPU.

ROUTING: POST-CYCLE192 Group A composition (A1 AND-NOT composition (PP-162 x PP-163)). 1000-subject KB; each property has an inverted shard (sum of subjects having it). 'P AND NOT Q' ranks subjects high on shard[P] and low on shard[Q]. Validates AND-NOT precision composes from the individual primitives. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AND-NOT precision >= 0.95 on 1000-subject KB. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "comp_a1_and_not_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(2, 64, g); s = a[0] + a[1]; assert (np.stack([a[0], a[1]]) @ np.conj(s)).real.min() / 64 > 0.4, "shard cleanup"; print("[selftest] PASS: comp-a1-and-not", flush=True)
def run() -> Dict:
    g = np.random.default_rng(401); N = 8192; NSUBJ = 1000 if not SMOKE else 300; NPROP = 30; TR = 30 if SMOKE else 80
    subs = cphasor(NSUBJ, N, g)
    precs = []
    for _ in range(TR):
        has = (g.random((NSUBJ, NPROP)) < 0.25)
        shard = np.zeros((NPROP, N), dtype=np.complex64)
        for p in range(NPROP):
            idx = np.where(has[:, p])[0]
            if len(idx):
                shard[p] = subs[idx].sum(0)
        P, Q = 0, 1
        gold = set(int(i) for i in range(NSUBJ) if has[i, P] and not has[i, Q])
        if not gold:
            continue
        sP = (subs @ np.conj(shard[P])).real / N; sQ = (subs @ np.conj(shard[Q])).real / N
        score = sP - 1e3 * (sQ > 0.5)                                          # exclude Q-members
        top = set(np.argsort(score)[::-1][:len(gold)].tolist())
        precs.append(len(top & gold) / len(top))
    prec = float(np.mean(precs)); print("  AND-NOT precision=%.3f (%d subjects)" % (prec, NSUBJ), flush=True)
    return {"precision": prec, "nsubj": NSUBJ}
def verdict(r) -> Tuple[str, str]:
    s = "AND-NOT precision=%.3f (%d subj)" % (r["precision"], r["nsubj"])
    if r["precision"] >= 0.95: return ("HARD_PASS", "HARD_PASS: AND-NOT composition precision >=0.95 -- conjunction + negation compose. " + s)
    if r["precision"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AND-NOT 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AND-NOT <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
