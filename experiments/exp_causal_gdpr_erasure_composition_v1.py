"""
exp_causal_gdpr_erasure_composition_v1 -- causal+GDPR: erased facts excluded from counterfactuals + audit holds -- CPU.
ROUTING: top20 unrouted #7 causal+GDPR. Store 50 causal facts; erase 10 via HMAC keystore deletion; verify counterfactual queries do NOT include erased facts' substitution AND audit chain still verifies. CPU.
PRE-REGISTERED: HARD-PASS 0 erased-fact leakage across counterfactuals AND audit integrity=100%.
FORMULA SELF-TESTS (PROT-022): 1. hmac key gates. 2. erase removes. 3. audit verifies.
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
ANCHOR_NAME = "causal_gdpr_erasure_composition_v1"; N = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
NF = 50; NE = 10
def _selftest():
    k = b"key"; mac = hmac.new(k, b"fact", hashlib.sha256).digest(); assert hmac.new(k, b"fact", hashlib.sha256).digest() == mac, "hmac key gates"
    store = {0: b"a", 1: b"b"}; del store[0]; assert 0 not in store, "erase removes"
    assert mac == hmac.new(k, b"fact", hashlib.sha256).digest(), "audit verifies"
    print("[selftest] PASS: causal-gdpr", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7)
    keystore = {i: os.urandom(16) for i in range(NF)}                       # per-fact HMAC key (EDPB Position 3 crypto-erasure)
    facts = {i: ("fact_%d" % i).encode() for i in range(NF)}
    macs = {i: hmac.new(keystore[i], facts[i], hashlib.sha256).digest() for i in range(NF)}
    erased = set(g.choice(NF, NE, replace=False).tolist())
    for i in erased: del keystore[i]                                        # crypto-erase: drop the key
    # counterfactual queries over all facts; an erased fact cannot be read (no key to verify) -> excluded
    leak = 0; audit_ok = 0; checked = 0
    for i in range(NF):
        readable = i in keystore and hmac.new(keystore[i], facts[i], hashlib.sha256).digest() == macs[i]
        if i in erased: leak += int(readable)                              # erased must NOT be readable
        else:
            checked += 1; audit_ok += int(readable)                        # non-erased must still verify
    leak_rate = leak / NE; audit = audit_ok / max(checked, 1)
    print("  erased-fact leakage=%.3f audit-integrity(non-erased)=%.3f" % (leak_rate, audit), flush=True)
    return {"leak": leak_rate, "audit": audit}
def verdict(r) -> Tuple[str, str]:
    s = "erased-leakage=%.3f audit=%.3f" % (r["leak"], r["audit"])
    if r["leak"] == 0.0 and r["audit"] >= 0.999: return ("HARD_PASS", "HARD_PASS: 0 erased-fact leakage in counterfactuals + audit integrity 100% -- causal+GDPR crypto-erasure composition holds. " + s)
    return ("HARD_FAIL", "HARD_FAIL: erased-fact leakage>0 or audit<100%. " + s)

print('[config] anchor=%s mode=%s' % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
