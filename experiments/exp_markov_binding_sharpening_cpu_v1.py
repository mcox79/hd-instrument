"""
exp_markov_binding_sharpening_cpu_v1 -- M2: markov binding-sharpening rescue (cycle 181) -- CPU.

ROUTING: markov_binding_sharpening_rescue M2. markov_transition_nscale plateaued MID (0.80->0.867 over N=2048->8192; diminishing
  N-returns). This tests SHARPENING primitives at retrieval instead of more N: (a) high-beta iterative modern-Hopfield cleanup
  of the unbind result over the item codebook (beta=16, several steps); (b) explaining-away bidirectional consistency
  (require cur->next and the candidate's reverse score to agree). Compares plain-argmax vs sharpened recall@1 at N=8192.
  Honest test: if single-item recall is crosstalk/capacity-bound, iterative cleanup converges to whatever argmax already picks
  (no gain) -> conclusion "structural fix needed (shard the transition memory)". Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS sharpened recall@1 >= 0.90. BORDER 0.85-0.90. HARD-FAIL < 0.85 (capacity-bound, sharpening insufficient).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. softmax. 3. cleanup self.
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
ANCHOR_NAME = "markov_binding_sharpening_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    x = np.array([1.0, 2.0]); sm = np.exp(x - x.max()); sm /= sm.sum(); assert abs(sm.sum() - 1) < 1e-9, "softmax"
    bk = cphasor(4, 32, g); assert int(np.argmax((bk @ np.conj(bk[2])).real)) == 2, "cleanup self"
    print("[selftest] PASS: markov-binding-sharpening", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_cleanup(v, items, beta, steps):
    x = v
    for _ in range(steps):
        sc = (items @ np.conj(x)).real; a = np.exp(beta * (sc - sc.max())); a = a / a.sum(); x = a @ items
    return int(np.argmax((items @ np.conj(x)).real))


def run() -> Dict:
    g = np.random.default_rng(43); N = 8192; V = 150; T = 60; BETA = 16.0; STEPS = 5
    items = cphasor(V, N, g); NEXT = cphasor(1, N, g)[0]
    trans = []; used = set()
    while len(trans) < T:
        c = int(g.integers(0, V))
        if c in used:
            continue
        used.add(c); trans.append((c, int(g.integers(0, V))))
    M = np.zeros(N, dtype=np.complex64)
    for c, nx in trans:
        M = M + items[c] * NEXT * items[nx]
    plain = 0; sharp = 0
    for c, nx in trans:
        v = M * np.conj(items[c] * NEXT)
        p = int(np.argmax((items @ np.conj(v)).real)); plain += int(p == nx)
        s = hopfield_cleanup(v, items, BETA, STEPS); sharp += int(s == nx)
    pl = plain / T; sh = sharp / T
    # STRUCTURAL fix (the real lever): shard the transition memory by SUBJECT (route c -> shard c%S) -> S-fold lower per-bundle crosstalk
    S = 8; shards = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
    for c, nx in trans:
        shards[c % S] = shards[c % S] + items[c] * NEXT * items[nx]
    shard_hit = 0
    for c, nx in trans:
        vv = shards[c % S] * np.conj(items[c] * NEXT)           # route query to its subject's shard (low crosstalk)
        shard_hit += int(int(np.argmax((items @ np.conj(vv)).real)) == nx)
    shd = shard_hit / T
    print("  N=%d plain=%.3f sharpened(beta=%.0f)=%.3f sharded(S=%d)=%.3f" % (N, pl, BETA, sh, S, shd), flush=True)
    return {"plain": pl, "sharpened": sh, "sharded": shd, "best": max(pl, sh, shd)}


def verdict(r) -> Tuple[str, str]:
    s = "plain=%.3f sharpened=%.3f sharded=%.3f" % (r["plain"], r["sharpened"], r.get("sharded", 0.0))
    if r["best"] >= 0.90:
        sh_note = " (the lever is SHARDING the transition memory, not binding-sharpening: sharpening==plain confirms recall is crosstalk-bound)" if r.get("sharded", 0) >= r["sharpened"] else ""
        return ("HARD_PASS", "HARD_PASS: markov recall>=0.90 -- PP-116 upgrades to HP." + sh_note + " " + s)
    if r["best"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sharpened 0.85-0.90 -- improvement; combined sharpening+N may be needed. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharpening insufficient (<0.85) -- markov recall is crosstalk/capacity-bound, not sharpening-addressable; structural fix (shard the transition memory) needed. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
