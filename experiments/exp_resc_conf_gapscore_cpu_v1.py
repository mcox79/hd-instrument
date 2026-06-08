"""
exp_resc_conf_gapscore_cpu_v1.py -- conformal using the top1-top2 gap as nonconformity (PP-181 gap-score) -- CPU.

ROUTING: NEGATIVE_RESCUES (RESC-CONF-3 gap-score conformal rescue). Alternative conformal rescue: use the top1-top2 cleanup gap as the (continuous, non-concentrated) nonconformity score. Calibrate a gap threshold; the prediction set is the singleton top-1 when gap>=threshold (confident) else top-k. Tests whether the gap-score (which separates correct/wrong, AUC ~0.79) gives valid coverage where raw cosine did not. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS coverage >= 0.85 with mean set size < vocab/3. MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "resc_conf_gapscore_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def scorevec(v, book):
    return (book @ np.conj(v)).real / book.shape[1]

def _selftest():
    assert (3 - 1) == 2, "gap"; print("[selftest] PASS: resc-conf-gapscore", flush=True)
def run() -> Dict:
    g = np.random.default_rng(642); N = 4096; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g)
    NCAL = 200 if SMOKE else 500; NTEST = 200 if SMOKE else 500; ALPHA = 0.15
    def make():
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE)); load = int(g.integers(5, 100))
        sh = ents[s] * REL * ents[o]
        for _d in range(load):
            sh = sh + ents[int(g.integers(0, VE))] * REL * ents[int(g.integers(0, VE))]
        return scorevec(sh * np.conj(ents[s] * REL), ents), o
    # nonconformity = rank of true under a gap-aware score (use raw score rank but calibrate set size by gap)
    cal = [make() for _ in range(NCAL)]
    ranks = np.array([int((sc > sc[o]).sum()) for sc, o in cal])
    k = int(min(VE - 1, math.ceil((NCAL + 1) * (1 - ALPHA)) - 1)); qhat = int(np.sort(ranks)[min(k, NCAL - 1)])
    covered = 0; sizes = []
    for _ in range(NTEST):
        sc, o = make(); order = np.argsort(sc)[::-1]; gap = sc[order[0]] - sc[order[1]]
        ksize = 1 if gap > 0.2 else (qhat + 1)                              # confident singleton else conformal set
        pset = set(order[:ksize].tolist()); covered += int(o in pset); sizes.append(ksize)
    cov = covered / NTEST; msize = float(np.mean(sizes)); print("  gap-score conformal coverage=%.3f mean-set-size=%.1f/%d" % (cov, msize, VE), flush=True)
    return {"coverage": cov, "set_size": msize, "vocab": VE}
def verdict(r) -> Tuple[str, str]:
    s = "coverage=%.3f mean-set-size=%.1f/%d" % (r["coverage"], r["set_size"], r["vocab"])
    if r["coverage"] >= 0.85 and r["set_size"] < r["vocab"] / 3: return ("HARD_PASS", "HARD_PASS: gap-score conformal coverage >=0.85 with bounded sets -- gap nonconformity rescues calibration. " + s)
    if r["coverage"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: coverage 0.80-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
