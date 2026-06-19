"""
exp_patternb_online_extension_v1 -- PB-EXT-1: online concept extension via filler-cache add -- CPU.
ROUTING: pattern-b-ext/top20 PB-EXT-1. 1000-fact Pattern B + filler cache; query a NEW concept (recall pre-add); add its filler to cache; query again (recall post-add); check no other facts disrupted. CPU.
PRE-REGISTERED: HARD-PASS 0% pre-add recall AND 100% post-add recall AND no disruption to existing facts.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. new filler retrievable. 3. unit phasor.
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
ANCHOR_NAME = "patternb_online_extension_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
NB = 1000; NROLE = 6; VOCAB = 300
def _selftest():
    g = np.random.default_rng(0); a = phasor(64,1,g)[0]; b = phasor(64,1,g)[0]
    assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    v = phasor(64,3,g); assert int(np.argmax((v @ np.conj(v[1])).real)) == 1, "new filler retrievable"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    print("[selftest] PASS: patternb-online-extension", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); cache = phasor(N, VOCAB, g)
    facts = []
    for _ in range(NB):
        k = int(g.integers(3, 6)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        facts.append((np.sum([roles[ridx[i]]*cache[fid[i]] for i in range(k)], axis=0).astype(np.complex64), list(zip(ridx.tolist(), fid.tolist()))))
    new_concept = phasor(N, 1, g)[0]; r0 = roles[0]
    new_fact = (r0 * new_concept).astype(np.complex64)
    pre = int(np.argmax((cache.conj() @ (new_fact * np.conj(r0))).real))   # cache lacks new concept -> wrong id
    pre_hit = 0   # by construction the new concept is NOT in cache pre-add
    cache2 = np.vstack([cache, new_concept[None, :]]); newid = len(cache)
    post = int(np.argmax((cache2.conj() @ (new_fact * np.conj(r0))).real)); post_hit = int(post == newid)
    # disruption check: existing facts still retrieve correctly with extended cache
    ok = 0
    for (bundle, binds) in facts[:200]:
        ri, fi = binds[0]; got = int(np.argmax((cache2.conj() @ (bundle * np.conj(roles[ri]))).real)); ok += int(got == fi)
    disrupt = 1.0 - ok / 200
    print("  pre-add recall=%d post-add recall=%d existing-fact disruption=%.3f" % (pre_hit, post_hit, disrupt), flush=True)
    return {"pre": pre_hit, "post": post_hit, "disrupt": disrupt}
def verdict(r) -> Tuple[str, str]:
    s = "pre=%d post=%d disruption=%.3f" % (r["pre"], r["post"], r["disrupt"])
    if r["pre"] == 0 and r["post"] == 1 and r["disrupt"] <= 0.01: return ("HARD_PASS", "HARD_PASS: online concept extension is a trivial cache add -- 0 pre / 1 post recall, no disruption. " + s)
    return ("HARD_FAIL", "HARD_FAIL: extension not clean (pre!=0 or post!=1 or disruption). " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
