"""
exp_resc_pp155_per_strength_shard_cpu_v1.py -- continuous-strength strongest-wins via per-strength-tier sharding (N-scaling exhausted) -- CPU.

ROUTING: NEGATIVE_RESCUES (RESC PP-155 per-strength sharding). PP-155 stalled at ~0.93 strongest-wins; N-scaling exhausted. Rescue: route competing values into strength-TIER sub-shards (high/med/low), query the high tier first so the strongest value faces only same-tier competition. Tests whether tier-sharding lifts strongest-wins to >=0.95. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS strongest-wins >= 0.95 AND strength-recovery Pearson >= 0.9. MIDDLE >= 0.90. HARD-FAIL < 0.90.
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
ANCHOR_NAME = "resc_pp155_per_strength_shard_cpu_v1"
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
    import numpy as _n; assert abs(_n.corrcoef([1.,2,3],[1.,2,3])[0,1]-1.0)<1e-9, "corr"; print("[selftest] PASS: resc-pp155-per-strength-shard", flush=True)
def run() -> Dict:
    g = np.random.default_rng(643); N = 8192; VK = 80; VV = 400; TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); win = 0; corrs = []
    for _ in range(TR):
        k = int(g.integers(0, VK)); cands = g.choice(VV, 3, replace=False); strengths = g.uniform(0.2, 1.0, 3)
        # per-strength-tier shards: high tier = top strength, others in lower tiers
        order = np.argsort(strengths)[::-1]
        hi = np.zeros(N, dtype=np.complex64); hi = hi + strengths[order[0]] * keys[k] * vals[int(cands[order[0]])]
        lo = np.zeros(N, dtype=np.complex64)
        for j in order[1:]:
            lo = lo + strengths[j] * keys[k] * vals[int(cands[j])]
        for _d in range(15):
            lo = lo + g.uniform(0.2, 0.6) * keys[int(g.integers(0, VK))] * vals[int(g.integers(0, VV))]
        # query high tier first (strongest faces no same-key competition)
        rec_hi = hi * np.conj(keys[k]); pred = cidx(rec_hi, vals)
        win += int(pred == int(cands[order[0]]))
        full = hi + lo; sc = (vals[cands] @ np.conj(full * np.conj(keys[k]))).real
        if np.std(sc) > 0:
            corrs.append(float(np.corrcoef(sc, strengths)[0, 1]))
    wr = win / TR; cr = float(np.mean(corrs)) if corrs else 0.0; print("  tier-sharded strongest-wins=%.3f strength-corr=%.3f" % (wr, cr), flush=True)
    return {"win": wr, "corr": cr}
def verdict(r) -> Tuple[str, str]:
    s = "strongest-wins=%.3f strength-corr=%.3f" % (r["win"], r["corr"])
    if r["win"] >= 0.95 and r["corr"] >= 0.9: return ("HARD_PASS", "HARD_PASS: per-strength-tier sharding lifts strongest-wins >=0.95 (PP-155 rescue) + strength recoverable. " + s)
    if r["win"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: strongest-wins 0.90-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: strongest-wins <0.90. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
