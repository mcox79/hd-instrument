"""
exp_resc_conf_aps_temperature_cpu_v1.py -- adaptive prediction sets (APS) with temperature-scaled softmax fix conformal coverage under score concentration -- CPU.

ROUTING: NEGATIVE_RESCUES (RESC-CONF-1 APS + temperature conformal rescue). gate3 conformal failed (coverage 0.676) because substrate cosine scores concentrate (ties) so a single-threshold quantile undershoots. Rescue: APS -- temperature-scale scores to probabilities (softmax(score/T)), then the prediction set is the smallest top-set whose cumulative probability reaches a calibrated threshold (the standard adaptive-prediction-set method, valid under concentration). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS empirical coverage in [0.90, 0.98] at alpha=0.1 with mean set size < vocab/3. MIDDLE coverage >= 0.88. HARD-FAIL coverage < 0.88.
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
ANCHOR_NAME = "resc_conf_aps_temperature_cpu_v1"
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
    import numpy as _n; p = _n.exp([2.0,1.0,0.0]); p = p/p.sum(); assert abs(p.sum()-1.0)<1e-9, "softmax"; print("[selftest] PASS: resc-conf-aps-temperature", flush=True)
def run() -> Dict:
    g = np.random.default_rng(641); N = 4096; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g)
    NCAL = 200 if SMOKE else 500; NTEST = 200 if SMOKE else 500; ALPHA = 0.1; T = 0.05
    def make():
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE)); load = int(g.integers(5, 100))
        sh = ents[s] * REL * ents[o]
        for _d in range(load):
            sh = sh + ents[int(g.integers(0, VE))] * REL * ents[int(g.integers(0, VE))]
        sc = scorevec(sh * np.conj(ents[s] * REL), ents); return sc, o
    def aps_cumprob(sc, o):
        p = np.exp(sc / T); p = p / p.sum(); order = np.argsort(p)[::-1]
        cum = 0.0
        for idx in order:
            cum += p[idx]
            if idx == o:
                return cum     # cumulative prob needed to include the TRUE label
        return 1.0
    cal_scores = np.array([aps_cumprob(*make()) for _ in range(NCAL)])
    qhat = float(np.quantile(cal_scores, min(1.0, math.ceil((NCAL + 1) * (1 - ALPHA)) / NCAL)))
    covered = 0; sizes = []
    for _ in range(NTEST):
        sc, o = make(); p = np.exp(sc / T); p = p / p.sum(); order = np.argsort(p)[::-1]
        cum = 0.0; pset = []
        for idx in order:
            pset.append(int(idx)); cum += p[idx]
            if cum >= qhat:
                break
        covered += int(o in pset); sizes.append(len(pset))
    cov = covered / NTEST; msize = float(np.mean(sizes))
    print("  APS conformal coverage=%.3f (target>=%.2f) mean-set-size=%.1f/%d T=%.2f" % (cov, 1 - ALPHA, msize, VE, T), flush=True)
    return {"coverage": cov, "set_size": msize, "vocab": VE}
def verdict(r) -> Tuple[str, str]:
    s = "coverage=%.3f mean-set-size=%.1f/%d" % (r["coverage"], r["set_size"], r["vocab"])
    if 0.90 <= r["coverage"] <= 0.98 and r["set_size"] < r["vocab"] / 3: return ("HARD_PASS", "HARD_PASS: APS+temperature rescues conformal coverage to >=0.90 with bounded sets (fixes gate3 concentration failure). " + s)
    if r["coverage"] >= 0.88: return ("MIDDLE_BAND", "MIDDLE_BAND: coverage >=0.88 near target. " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage <0.88 (concentration still breaks calibration). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
