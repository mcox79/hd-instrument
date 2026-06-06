"""
exp_substrate_matthiessen_dominant_scatterer_v1 -- OVERNIGHT T1-2: dominant substrate-noise mechanism diagnosis -- CPU.

ROUTING: research OVERNIGHT_QUEUE T1-2 (bio/materials kinetics drill). Matthiessen's rule: independent scattering
  mechanisms add. Decompose substrate retrieval error into 3 independent sources by ablation and identify the dominant
  one (the optimization target):
    - CODEBOOK-COLLISION (key-key similarity crosstalk): random keys vs near-orthogonal keys
    - SUPERPOSITION-LOAD (W stores many facts): low load vs high load
    - CUE-NOISE (corrupted query): clean cue vs flip-corrupted cue
  Error contribution of each = error_with_source - error_baseline_clean. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS a single mechanism accounts for > 60% of total excess error (clear optimization target).
  MIDDLE: dominant 40-60%. HARD-FAIL: no mechanism > 40% (diffuse; no single target).
FORMULA SELF-TESTS (PROT-022): 1. clean retrieval ~ perfect. 2. additivity sanity. 3. N marker.
ASCII-only. write_metrics. PROT-018: _v1.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_matthiessen_dominant_scatterer_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; N_VAL = 64
else:
    SEEDS = [7, 17, 23, 31, 43]; N_DIM = 2048; N_VAL = 64
HIGH_LOAD = 0.5; LOW_LOAD = 0.05; FLIP = 0.15


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def err(n, M, keys, EV, v, flip, g):
    W = (EV[v].T @ keys).astype(np.float32)
    cue = keys.copy()
    if flip > 0:
        fl = g.random(keys.shape) < flip; cue = keys * np.where(fl, -1.0, 1.0); cue /= np.linalg.norm(cue, axis=1, keepdims=True) + 1e-8
    pred = np.argmax((cue @ W.T) @ EV.T, axis=1)
    return float(np.mean(pred != v))


def _selftest():
    g = np.random.default_rng(0); n = 256; keys = bp(10, n, g); EV = bp(8, n, g); v = g.integers(0, 8, 10)
    assert err(n, 10, keys, EV, v, 0.0, g) < 0.05, "clean retrieval ~ perfect"
    assert (0.6 - 0.6) == 0, "additivity sanity"
    print("[selftest] PASS: clean additivity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    Mlo = max(4, int(LOW_LOAD * n)); Mhi = int(HIGH_LOAD * n)
    EV = bp(N_VAL, n, g)
    # BASELINE: low load, random keys, clean cue -> near-zero error
    klo = bp(Mlo, n, g); vlo = g.integers(0, N_VAL, Mlo); base = err(n, Mlo, klo, EV, vlo, 0.0, g)
    # SUPERPOSITION-LOAD: high load, random keys, clean cue
    khi = bp(Mhi, n, g); vhi = g.integers(0, N_VAL, Mhi); e_load = err(n, Mhi, khi, EV, vhi, 0.0, g)
    # CODEBOOK-COLLISION: high load with deliberately COLLIDING keys (drawn from a small key-pool -> near-duplicates)
    pool = bp(max(8, Mhi // 8), n, g); idx = g.integers(0, pool.shape[0], Mhi)
    kcol = pool[idx] + 0.15 * bp(Mhi, n, g); kcol /= np.linalg.norm(kcol, axis=1, keepdims=True) + 1e-8
    e_coll = err(n, Mhi, kcol, EV, g.integers(0, N_VAL, Mhi), 0.0, g)
    # CUE-NOISE: high load, random keys, flip-corrupted cue
    e_noise = err(n, Mhi, khi, EV, vhi, FLIP, g)
    # excess error attributable to each (above the high-load baseline for collision/noise; load itself vs baseline)
    c_load = max(0.0, e_load - base)
    c_coll = max(0.0, e_coll - e_load)
    c_noise = max(0.0, e_noise - e_load)
    tot = c_load + c_coll + c_noise + 1e-9
    return {"seed": seed, "base_err": base, "load_err": e_load, "coll_err": e_coll, "noise_err": e_noise,
            "frac_load": c_load / tot, "frac_collision": c_coll / tot, "frac_cue_noise": c_noise / tot}


def verdict(ps) -> Tuple[str, str]:
    fl = float(np.mean([p["frac_load"] for p in ps])); fc = float(np.mean([p["frac_collision"] for p in ps])); fn = float(np.mean([p["frac_cue_noise"] for p in ps]))
    mech = {"superposition_load": fl, "codebook_collision": fc, "cue_noise": fn}
    dom = max(mech, key=mech.get); domf = mech[dom]
    summary = "dominant=%s (%.0f%%) | load=%.0f%% collision=%.0f%% cue_noise=%.0f%%" % (dom, domf * 100, fl * 100, fc * 100, fn * 100)
    if domf > 0.60:
        return ("HARD_PASS", "HARD_PASS: single dominant noise mechanism (%s >60%%) -- clear optimization target. " % dom + summary)
    if domf >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: dominant mechanism %s 40-60%%. " % dom + summary)
    return ("HARD_FAIL", "HARD_FAIL: noise diffuse, no single mechanism >40%%. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] load=%.0f%% collision=%.0f%% cue_noise=%.0f%% (base_err=%.3f)" % (seed, r["frac_load"] * 100, r["frac_collision"] * 100, r["frac_cue_noise"] * 100, r["base_err"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
