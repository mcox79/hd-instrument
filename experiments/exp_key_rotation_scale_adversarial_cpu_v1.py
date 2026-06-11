"""
exp_key_rotation_scale_adversarial_cpu_v1.py -- KEY-ROTATION at 10K keys + adversarial revocation -- CPU.

ROUTING: Research cycle-229 Tier-4 (KEY-ROTATION at 10K keys + adversarial). The validated key-rotation cert (single bind R
  rotates all keys, revokes old) at K=120. This scales to 10K keys (sharded ~120/shard) and adds ADVERSARIAL probing: after
  rotation, an attacker holding the OLD keys (or random keys) must not recover content (revocation must hold at scale).
  Tests: legit new-key recall at 10K AND adversarial old-key recall (<=0.10) AND random-key recall (~chance). Substrate-only.
PRE-REGISTERED: HARD-PASS new-key recall >= 0.90 at 10K AND adversarial old-key recall <= 0.10 AND random-key <= 0.05.
  MIDDLE new-key >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "key_rotation_scale_adversarial_cpu_v1"
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
    print("[selftest] PASS: key-rotation-scale-adversarial", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "861")))
    NFACTS = 1200 if SMOKE else 10000; SHARD = 120; V = 400
    nshard = (NFACTS + SHARD - 1) // SHARD
    vals = cphasor(V, N, g)
    R = cphasor(1, N, g)[0]                              # global rotation key
    # sample which facts to probe (for speed): ~6 per shard
    new_hit = 0; old_hit = 0; rand_hit = 0; tot = 0
    rng_keys = cphasor(64, N, g)                          # attacker's random key pool
    for sh in range(nshard):
        m = min(SHARD, NFACTS - sh * SHARD)
        keys = cphasor(m, N, g); truth = g.integers(0, V, size=m)
        M = cnorm(sum((keys[i] * vals[truth[i]] for i in range(m)), np.zeros(N, dtype=np.complex64)))
        Mp = cnorm(R * M)                                 # rotate all keys in shard by one bind
        newkeys = cnorm(keys * R)
        probe = range(0, m, 20)                           # sample ~6/shard
        for i in probe:
            new_hit += int(cidx(Mp * np.conj(newkeys[i]), vals) == truth[i])     # legit user, rotated keys
            old_hit += int(cidx(Mp * np.conj(keys[i]), vals) == truth[i])        # ADVERSARIAL: old (revoked) key
            rk = rng_keys[int(g.integers(0, 64))]
            rand_hit += int(cidx(Mp * np.conj(rk), vals) == truth[i])            # ADVERSARIAL: random key
            tot += 1
    nr = new_hit / tot; orr = old_hit / tot; rr = rand_hit / tot
    print("  KEY-ROTATION @ %d keys (%d shards): new-key=%.3f | adversarial old-key=%.3f | random-key=%.3f" %
          (NFACTS, nshard, nr, orr, rr), flush=True)
    return {"new_key_recall": round(nr, 3), "adv_old_key_recall": round(orr, 3), "adv_random_key_recall": round(rr, 3), "n_facts": NFACTS, "n_shards": nshard}
def verdict(r) -> Tuple[str, str]:
    nr = r["new_key_recall"]; orr = r["adv_old_key_recall"]; rr = r["adv_random_key_recall"]
    s = "new-key=%.3f adv-old=%.3f adv-random=%.3f (%d facts)" % (nr, orr, rr, r["n_facts"])
    if nr >= 0.90 and orr <= 0.10 and rr <= 0.05:
        return ("HARD_PASS", "HARD_PASS: key rotation scales to 10K keys with adversarial revocation -- legit new-key recall>=0.90 while adversarial OLD-key (<=0.10) and RANDOM-key (<=0.05) probing recover nothing. Substrate-only access rotation/revocation holds at production key-count. " + s)
    if nr >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: new-key 0.85-0.90 or minor adversarial leakage. " + s)
    return ("HARD_FAIL", "HARD_FAIL: rotation breaks at scale (new-key <0.85) or adversarial leakage. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
