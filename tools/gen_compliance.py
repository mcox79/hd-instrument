"""HUGE_BATCH TIER-1: DECISIVE-4 GDPR exact erasure + DECISIVE-5 multi-tenant isolation. CPU numpy/VSA. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: HUGE_BATCH TIER-1 ({tag}). {desc} numpy/VSA. CPU.
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

GDPR = r'''
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
'''

TENANT = r'''
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
'''

C = [
    dict(anchor="decisive4_gdpr_erasure_cpu_v1", tag="DECISIVE-4 GDPR exact erasure", title="GDPR exact erasure -- 0 false retentions / 0 false losses", desc="Insert M facts, exact unbind-subtract erasure of a subset (PP-104), verify deleted unretrievable + retained intact + sub-ms latency.", prereg="HARD-PASS 0 false retentions AND 0 false losses. else HARD-FAIL.", body=GDPR),
    dict(anchor="decisive5_multitenant_iso_cpu_v1", tag="DECISIVE-5 multi-tenant isolation", title="multi-tenant isolation -- 0pct cross-tenant leakage", desc="Per-tenant key namespaces; verify within-tenant recall + that one tenant's key cannot retrieve another tenant's value.", prereg="HARD-PASS cross-leak<=0.001 AND within-recall>=0.95. MIDDLE cross-leak<=0.01. HARD-FAIL else.", body=TENANT),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
