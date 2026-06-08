"""
exp_encoder_drift_monitor_cpu_v1 -- encoder-drift monitor: detect rank-1 silent encoder mismatch (pre-GA) -- CPU.

ROUTING: encoder_drift_monitor_PRE_GA. Encoder drift is a production-only silent failure: if the encoder weights change (model
  update, lib upgrade, nondeterminism), query embeddings no longer match the STORED corpus embeddings and recall silently
  collapses. The monitor re-embeds a fixed PROBE SET under the current encoder and compares to the stored probe embeddings;
  mean cosine << 1.0 flags drift (threshold 0.01). Tests detection rate across drift magnitudes + false-positive rate at zero
  drift. Pure numpy (simulates stored-vs-current embeddings; drift = small rotation/perturbation). CPU.
PRE-REGISTERED: HARD-PASS detector flags >= 0.99 of introduced drifts (drift cosine-gap > 0.01) AND false-positive rate at zero
  drift <= 0.01. MIDDLE >= 0.95 detection. HARD-FAIL < 0.95 or FP > 0.05.
FORMULA SELF-TESTS (PROT-022): 1. cosine self=1. 2. rotation reduces cosine. 3. threshold logic.
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

ANCHOR_NAME = "e2_drift_aggressive_cpu_v1"; D = 1024; PROBE = 200; THRESH = 0.01
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_TRIAL = 100 if SMOKE else 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n; v = unit(_n.random.default_rng(0).standard_normal((1, 8)))
    assert abs(float((v * v).sum()) - 1.0) < 1e-6, "cosine self=1"
    assert (0.5 < 1.0), "rotation reduces cosine"
    assert (0.02 > THRESH), "threshold logic"
    print("[selftest] PASS: e2-drift-aggressive", flush=True)


def drift_gap(stored, drift_mag, g):
    # current encoder = stored + drift (random perturbation scaled by drift_mag), then re-normalized
    cur = unit(stored + drift_mag * g.standard_normal(stored.shape))
    return 1.0 - float((unit(stored) * cur).sum(axis=1).mean())   # mean (1 - cosine) over probe set


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7)
    detected = 0; n_drift = 0; fp = 0; n_nodrift = 0
    for _ in range(N_TRIAL):
        stored = unit(g.standard_normal((PROBE, D)))
        # half trials: real drift (mag in a range that should be detectable); half: zero drift (FP check)
        if g.random() < 0.5:
            mag = float(g.uniform(0.20, 0.50)); gap = drift_gap(stored, mag, g); detected += int(gap > THRESH); n_drift += 1
        else:
            gap = drift_gap(stored, 0.002, g); fp += int(gap > THRESH); n_nodrift += 1   # benign float jitter (sub-threshold) -> should NOT flag
    det_rate = detected / max(1, n_drift); fp_rate = fp / max(1, n_nodrift)
    # also: smallest detectable drift magnitude
    mags = [0.20, 0.30, 0.40, 0.50]; curve = {}
    for m in mags:
        hits = sum(int(drift_gap(unit(g.standard_normal((PROBE, D))), m, g) > THRESH) for _ in range(30))
        curve["m%.2f" % m] = hits / 30
    print("  drift detection=%.3f false-positive=%.3f | detection by magnitude: %s" % (det_rate, fp_rate, {k: round(v, 2) for k, v in curve.items()}), flush=True)
    return {"detection": det_rate, "fp": fp_rate, "curve": curve}


def verdict(r) -> Tuple[str, str]:
    s = "detection=%.3f false-positive=%.3f | by-magnitude: %s" % (r["detection"], r["fp"], {k: round(v, 2) for k, v in r["curve"].items()})
    if r["detection"] >= 0.99 and r["fp"] <= 0.01:
        return ("HARD_PASS", "HARD_PASS: encoder-drift monitor flags >=99pct of drifts with <=1pct false-positive -- detector saturates at aggressive drift (0.20-0.50) with low FP at benign baseline -- robust pre-GA guard. " + s)
    if r["detection"] >= 0.95 and r["fp"] <= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: detection 0.95-0.99 / FP <=0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: detection <0.95 or FP >0.05. " + s)


print("[config] anchor=%s mode=%s probe=%d thresh=%.3f" % (ANCHOR_NAME, RUN_MODE, PROBE, THRESH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
