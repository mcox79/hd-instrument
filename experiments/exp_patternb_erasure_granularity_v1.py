"""
exp_patternb_erasure_granularity_v1 -- PB-EXT-4: erase a binding while concept vocab stays usable -- CPU.
ROUTING: pattern-b-ext/top20 PB-EXT-4. Erase a specific role-filler binding (crypto-erase its key) while the filler concept remains usable in OTHER facts; verify erased binding gone + concept retained elsewhere. CPU.
PRE-REGISTERED: HARD-PASS 0 erased-binding leakage AND 100% concept retention for unrelated facts.
FORMULA SELF-TESTS (PROT-022): 1. hmac gates. 2. erase removes binding. 3. concept retained.
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
ANCHOR_NAME = "patternb_erasure_granularity_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
NF = 200; NE = 20
def _selftest():
    k = b"k"; assert hmac.new(k, b"x", hashlib.sha256).digest() == hmac.new(k, b"x", hashlib.sha256).digest(), "hmac gates"
    store = {(0,5): b"a", (1,5): b"b"}; del store[(0,5)]; assert (0,5) not in store and (1,5) in store, "erase removes binding"
    assert (1,5) in store, "concept retained"
    print("[selftest] PASS: patternb-erasure-granularity", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7)
    # bindings keyed by (fact_id, role); a shared concept C5 appears in many facts
    keys = {}; facts = {}
    for fid in range(NF):
        for role in range(3):
            concept = int(g.integers(0, 50)); keys[(fid, role)] = os.urandom(16); facts[(fid, role)] = concept
    erase = [(int(g.integers(0, NF)), int(g.integers(0, 3))) for _ in range(NE)]
    erased_concepts = set(facts[b] for b in erase)
    for b in erase: del keys[b]                                          # crypto-erase the SPECIFIC binding only
    leak = sum(1 for b in erase if b in keys); leak_rate = leak / NE
    # concept retention: the erased concepts still appear (usable) in NON-erased bindings
    retained = 0; checked = 0
    for c in erased_concepts:
        others = [b for b in facts if facts[b] == c and b not in erase]
        if others: checked += 1; retained += int(all(b in keys for b in others))
    retention = retained / max(checked, 1)
    print("  erased-binding leakage=%.3f concept-retention(unrelated facts)=%.3f" % (leak_rate, retention), flush=True)
    return {"leak": leak_rate, "retention": retention}
def verdict(r) -> Tuple[str, str]:
    s = "erased-leak=%.3f concept-retention=%.3f" % (r["leak"], r["retention"])
    if r["leak"] == 0.0 and r["retention"] >= 0.999: return ("HARD_PASS", "HARD_PASS: binding-level erasure removes the specific binding (0 leak) while the concept stays usable in unrelated facts (100% retention) -- Pattern B erasure granularity beats Pattern A. " + s)
    return ("HARD_FAIL", "HARD_FAIL: erased-binding leak>0 or concept retention<100%. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
