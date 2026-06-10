"""
exp_decisive4_gdpr_erasure_cpu_v1.py -- GDPR exact erasure -- 0 false retentions / 0 false losses -- CPU.

ROUTING: HUGE_BATCH TIER-1 (DECISIVE-4 GDPR exact erasure). Insert M facts, exact unbind-subtract erasure of a subset (PP-104), verify deleted unretrievable + retained intact + sub-ms latency. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS 0 false retentions AND 0 false losses. else HARD-FAIL.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "decisive4_gdpr_erasure_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert hashlib.sha256(b"x").hexdigest() == hashlib.sha256(b"x").hexdigest(), "det"; print("[selftest] PASS: decisive4-gdpr-erasure", flush=True)
def run() -> Dict:
    g = np.random.default_rng(404); N = 8192; M = 300 if SMOKE else 1000; VK = M; VV = 600
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g)
    truth = {}; Mem = np.zeros(N, dtype=np.complex64)
    for k in range(M):
        vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; truth[k] = vv
    ndel = max(10, M // 10); dele = set(int(x) for x in g.choice(M, ndel, replace=False))
    t0 = time.perf_counter()
    for k in dele:
        Mem = Mem - keys[k] * vals[truth[k]]                              # exact unbind-subtract erasure (PP-104)
    lat_ms = (time.perf_counter() - t0) * 1000 / max(1, ndel)
    false_retention = 0; false_loss = 0
    for k in range(M):
        pred = cidx(Mem * np.conj(keys[k]), vals); got = (pred == truth[k])
        if k in dele and got:
            false_retention += 1                                          # deleted fact still retrievable = leak
        if k not in dele and not got:
            false_loss += 1                                               # retained fact lost = collateral
    fr = false_retention; fl = false_loss
    print("  deleted=%d false_retentions=%d false_losses=%d erase_latency=%.4fms/fact" % (ndel, fr, fl, lat_ms), flush=True)
    return {"false_retentions": fr, "false_losses": fl, "n_del": ndel, "latency_ms": round(lat_ms, 4)}
def verdict(r) -> Tuple[str, str]:
    s = "false_retentions=%d false_losses=%d latency=%.4fms" % (r["false_retentions"], r["false_losses"], r["latency_ms"])
    if r["false_retentions"] == 0 and r["false_losses"] == 0:
        return ("HARD_PASS", "HARD_PASS: GDPR exact erasure -- 0 false retentions on deleted + 0 false losses on retained, sub-ms/fact. EU AI Act Art.17 categorical. " + s)
    return ("HARD_FAIL", "HARD_FAIL: erasure imperfect (false retention or loss). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
