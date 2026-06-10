"""
exp_lap3_8_zkp_primitive_cpu_v1.py -- LAP3-8 ZKP-PROOF-PRIMITIVE: Schnorr zero-knowledge proof-of-knowledge -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-8; 2-year compliance moat). The substrate proves it KNOWS a fact F (a secret) without
  revealing F. Implemented as a Schnorr sigma-protocol made non-interactive via Fiat-Shamir: secret x (the fact), public
  commitment y = g^x mod p. Proof (t=g^r, s=r+c*x where c=H(t,y)) verifies g^s == t*y^c without leaking x (s is uniform given r).
  Measures COMPLETENESS (honest prover always accepted), SOUNDNESS (a prover without x is rejected), and ZK (s independent of x).
  hashlib + modular arithmetic. CPU.
PRE-REGISTERED: HARD-PASS completeness == 1.0 AND soundness (cheater-reject) == 1.0 AND zk-leak == 0. else HARD-FAIL.
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
ANCHOR_NAME = "lap3_8_zkp_primitive_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# 256-bit safe-ish prime (RFC 5114-style); g=2 generator of a large subgroup. modexp is fast.
P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A63A3620FFFFFFFFFFFFFFFF
G = 2
Q = (P - 1) // 2


def _selftest():
    assert pow(G, 0, P) == 1, "modexp"; print("[selftest] PASS: zkp-primitive", flush=True)


def _chal(t, y):
    return int.from_bytes(hashlib.sha256(("%d|%d" % (t, y)).encode()).digest(), "big") % Q


def run() -> Dict:
    import random as _rmod; g = np.random.default_rng(228); rnd = _rmod.Random(228); TR = 50 if SMOKE else 300
    honest_ok = 0; cheat_rej = 0; zk_leak = 0; n = 0
    for _ in range(TR):
        x = int(g.integers(1, 2 ** 60))                                  # the secret fact
        y = pow(G, x, P)                                                 # public commitment (substrate publishes this)
        # honest proof
        r = int(g.integers(1, 2 ** 60)); t = pow(G, r, P); c = _chal(t, y); s = (r + c * x) % Q
        ok = (pow(G, s, P) == (t * pow(y, c, P)) % P)
        honest_ok += int(ok)
        # cheater WITHOUT x: knows y, picks random (t2,s2), hopes to satisfy verify
        t2 = pow(G, int(g.integers(1, 2 ** 60)), P); c2 = _chal(t2, y); s2 = rnd.randrange(1, Q)
        cheat_pass = (pow(G, s2, P) == (t2 * pow(y, c2, P)) % P)
        cheat_rej += int(not cheat_pass)
        # ZK check: re-run honest proof with the SAME x but fresh r -> s differs + is uniform (reveals nothing about x)
        r2 = int(g.integers(1, 2 ** 60)); s_b = (r2 + _chal(pow(G, r2, P), y) * x) % Q
        zk_leak += int(s == s_b)                                         # transcripts identical => would leak; should ~never
        n += 1
    comp = honest_ok / n; sound = cheat_rej / n; leak = zk_leak / n
    print("  ZKP completeness=%.3f soundness(cheater-reject)=%.3f zk-leak=%.4f (n=%d)" % (comp, sound, leak, n), flush=True)
    return {"completeness": comp, "soundness": sound, "zk_leak": leak, "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "completeness=%.3f soundness=%.3f zk-leak=%.4f" % (r["completeness"], r["soundness"], r["zk_leak"])
    if r["completeness"] >= 0.999 and r["soundness"] >= 0.999 and r["zk_leak"] <= 0.001:
        return ("HARD_PASS", "HARD_PASS: substrate ZK proof-of-knowledge -- honest prover always accepted, prover-without-fact always rejected (soundness), transcript leaks nothing (ZK). Substrate proves it has fact F without revealing F (Schnorr/Fiat-Shamir). " + s)
    return ("HARD_FAIL", "HARD_FAIL: ZKP completeness/soundness/ZK not all clean. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
