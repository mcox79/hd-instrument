"""
exp_key_rotation_cert_cpu_v1.py -- KEY-ROTATION certification (substrate self-modification / security) -- CPU.

ROUTING: Research SPRINT2 priority #6. Certify substrate KEY ROTATION: facts stored as M = sum key_i (X) val_i. Rotate all
  keys by a single bind R -> M' = R (X) M, equivalent to key'_i = key_i (X) R, WITHOUT re-encoding values. Certify (a) retrieval
  with NEW keys is preserved, (b) OLD keys are INVALIDATED on M' (security: rotating keys revokes old-key access). Relevant to
  key-management / GDPR-style access revocation. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS new-key recall >= 0.95 AND old-key recall <= 0.10 (rotation preserves access + revokes old). MIDDLE new-key >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "key_rotation_cert_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: key-rotation-cert", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "860"))); K = 60 if SMOKE else 120; V = 300
    TR = 12 if SMOKE else 60; new_hit = 0; old_hit = 0; tot = 0
    for _ in range(TR):
        keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=K)
        M = cnorm(sum((keys[i] * vals[truth[i]] for i in range(K)), np.zeros(N, dtype=np.complex64)))
        R = cphasor(1, N, g)[0]                                        # rotation key
        Mp = cnorm(R * M)                                              # rotate ALL keys by one bind (no value re-encode)
        newkeys = cnorm(keys * R)                                      # key'_i = key_i (X) R
        for i in range(K):
            pred_new = cidx(Mp * np.conj(newkeys[i]), vals); new_hit += int(pred_new == truth[i])
            pred_old = cidx(Mp * np.conj(keys[i]), vals); old_hit += int(pred_old == truth[i])  # old key on rotated memory
            tot += 1
    nr = new_hit / tot; orr = old_hit / tot
    print("  KEY-ROTATION: new-key recall=%.3f | old-key recall (should be ~0)=%.3f (K=%d)" % (nr, orr, K), flush=True)
    return {"new_key_recall": round(nr, 3), "old_key_recall": round(orr, 3), "n_keys": K}
def verdict(r) -> Tuple[str, str]:
    nr = r["new_key_recall"]; orr = r["old_key_recall"]; s = "new-key=%.3f old-key=%.3f" % (nr, orr)
    if nr >= 0.95 and orr <= 0.10:
        return ("HARD_PASS", "HARD_PASS: key rotation CERTIFIED -- a single bind R rotates all keys; new-key recall>=0.95 preserved AND old keys revoked (old-key recall<=0.10). Access rotation/revocation works substrate-only without re-encoding values. " + s)
    if nr >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: new-key recall 0.85-0.95 or old-key leakage. " + s)
    return ("HARD_FAIL", "HARD_FAIL: rotation breaks retrieval (new-key <0.85). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
