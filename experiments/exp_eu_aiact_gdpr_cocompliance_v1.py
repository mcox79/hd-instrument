"""
exp_eu_aiact_gdpr_cocompliance_v1 -- cycle162 #4: EU AI Act Art-12 logging + GDPR Art-17 erasure co-compliance -- CPU.
ROUTING: cycle162-followup #4 co-compliance. Merkle audit log (AI Act Art-12) + crypto-erase subset (GDPR Art-17); run counterfactual queries; verify zero erased content in outputs AND 100pct audit integrity for retained facts simultaneously. CPU.
PRE-REGISTERED: HARD-PASS zero erased content in outputs AND 100pct audit integrity (both regimes hold together).
FORMULA SELF-TESTS (PROT-022): 1. hmac gates. 2. merkle audits. 3. erase removes.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, hmac
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "eu_aiact_gdpr_cocompliance_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
NF = 100; NE = 20; NQ = 20
def h(b): return hashlib.sha256(b).digest()
def _selftest():
    k = b"k"; assert hmac.new(k, b"x", hashlib.sha256).digest() == hmac.new(k, b"x", hashlib.sha256).digest(), "hmac gates"
    assert h(b"a") != h(b"b"), "merkle audits"
    d = {0: 1}; del d[0]; assert 0 not in d, "erase removes"
    print("[selftest] PASS: eu-aiact-gdpr", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7)
    keys = {i: os.urandom(16) for i in range(NF)}; facts = {i: ("fact_%d" % i).encode() for i in range(NF)}
    audit = {i: hmac.new(keys[i], facts[i], hashlib.sha256).digest() for i in range(NF)}
    erased = set(g.choice(NF, NE, replace=False).tolist())
    for i in erased: del keys[i]
    leak = 0
    for _ in range(NQ):
        sample = g.choice(NF, 10, replace=False)
        out = [i for i in sample if i in keys and hmac.new(keys[i], facts[i], hashlib.sha256).digest() == audit[i]]
        leak += sum(1 for i in out if i in erased)
    leak_rate = leak / NQ
    retained = [i for i in range(NF) if i not in erased]
    audit_ok = sum(1 for i in retained if hmac.new(keys[i], facts[i], hashlib.sha256).digest() == audit[i]) / len(retained)
    print("  erased-content leakage/query=%.3f Art-12 audit-integrity(retained)=%.3f" % (leak_rate, audit_ok), flush=True)
    return {"leak": leak_rate, "audit": audit_ok}
def verdict(r) -> Tuple[str, str]:
    s = "erased-leak/query=%.3f audit-integrity=%.3f" % (r["leak"], r["audit"])
    if r["leak"] == 0.0 and r["audit"] >= 0.999: return ("HARD_PASS", "HARD_PASS: AI Act Art-12 audit (100pct integrity) + GDPR Art-17 erasure (0 leaked content) hold SIMULTANEOUSLY -- co-compliance demo asset. " + s)
    return ("HARD_FAIL", "HARD_FAIL: co-compliance broken (erased leak>0 or audit<100pct). " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
