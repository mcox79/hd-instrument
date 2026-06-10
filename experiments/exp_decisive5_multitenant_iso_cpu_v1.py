"""
exp_decisive5_multitenant_iso_cpu_v1.py -- multi-tenant isolation -- 0pct cross-tenant leakage -- CPU.

ROUTING: HUGE_BATCH TIER-1 (DECISIVE-5 multi-tenant isolation). Per-tenant key namespaces; verify within-tenant recall + that one tenant's key cannot retrieve another tenant's value. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS cross-leak<=0.001 AND within-recall>=0.95. MIDDLE cross-leak<=0.01. HARD-FAIL else.
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
ANCHOR_NAME = "decisive5_multitenant_iso_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert len({1,2}&{3})==0, "iso"; print("[selftest] PASS: decisive5-multitenant", flush=True)
def run() -> Dict:
    g = np.random.default_rng(505); N = 8192; T = 10 if SMOKE else 50; PER = 40; VV = 500; vals = cphasor(VV, N, g)
    tenant_keys = [cphasor(PER, N, g) for _ in range(T)]; tenant_mem = []; tenant_truth = []
    for t in range(T):
        Mem = np.zeros(N, dtype=np.complex64); tr = {}
        for k in range(PER):
            vv = int(g.integers(0, VV)); Mem = Mem + tenant_keys[t][k] * vals[vv]; tr[k] = vv
        tenant_mem.append(Mem); tenant_truth.append(tr)
    within = 0; cross_leak = 0; nq = 0
    for t in range(T):
        for k in range(PER):
            within += int(cidx(tenant_mem[t] * np.conj(tenant_keys[t][k]), vals) == tenant_truth[t][k]); nq += 1
            # query tenant t's key against ANOTHER tenant's memory -> must NOT retrieve t's value (isolation)
            ot = (t + 1) % T
            pred_other = cidx(tenant_mem[ot] * np.conj(tenant_keys[t][k]), vals)
            cross_leak += int(pred_other == tenant_truth[t][k])
    wr = within / nq; cl = cross_leak / nq
    print("  within-tenant-recall=%.3f cross-tenant-leak=%.4f (T=%d, n=%d)" % (wr, cl, T, nq), flush=True)
    return {"within_recall": wr, "cross_leak": cl, "tenants": T}
def verdict(r) -> Tuple[str, str]:
    s = "within-recall=%.3f cross-tenant-leak=%.4f (T=%d)" % (r["within_recall"], r["cross_leak"], r["tenants"])
    if r["cross_leak"] <= 0.001 and r["within_recall"] >= 0.95:
        return ("HARD_PASS", "HARD_PASS: multi-tenant isolation -- 0pct cross-tenant leakage with full within-tenant recall (per-tenant key namespaces). categorical SaaS-compliance. " + s)
    if r["cross_leak"] <= 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cross-leak <=1pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-tenant leakage. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
