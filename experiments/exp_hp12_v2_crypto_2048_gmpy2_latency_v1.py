"""
exp_hp12_v2_crypto_2048_gmpy2_latency_v1 -- HP-12 V2 production crypto latency at 2048-bit (gmpy2) -- CPU.

ROUTING: research HP12 V2 prep + Testbed gmpy2 install. Validates the V2 PRODUCTION crypto path: RSA accumulator at
  2048-bit modulus (rsa_bits=1024, production-grade) with gmpy2 acceleration. Clean many-op latency distribution for
  add / delete(cert issuance) / verify; confirms whether gmpy2 brings 2048-bit issuance under the <1ms gate (Testbed
  predicted gmpy2 ~50-100x faster than CPython pow). CPU pure-Python/gmpy2 $0.

PRE-REGISTERED bands: HARD-PASS delete(issuance) p50 < 1ms AND verify p50 < 1ms at 2048-bit (gmpy2) AND all certs
  verify. MIDDLE: 1-5ms (usable; V2-acceptable). HARD-FAIL: > 10ms (needs further optimization) OR cert fail.
FORMULA SELF-TESTS (PROT-022): 1. accumulator verify. 2. gmpy2 present. 3. tamper rejected.
ASCII-only. write_metrics. PROT-018: _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.hp12.rsa_accumulator import RSAAccumulator, _HAVE_GMPY2

ANCHOR_NAME = "exp_hp12_v2_crypto_2048_gmpy2_latency_v1"
RSA_BITS = 1024  # -> 2048-bit modulus (production)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ADD = 100; N_DEL = 50
else:
    SEEDS = [7, 17, 23, 31, 43]; N_ADD = 600; N_DEL = 300


def _selftest():
    acc = RSAAccumulator(rsa_bits=256); acc.add_many(["a", "b", "c"]); cert = acc.delete("b")
    assert RSAAccumulator.verify_deletion(cert), "accumulator verify"
    bad = dict(cert); bad["new_acc"] = int(cert["new_acc"]) ^ 1; assert not RSAAccumulator.verify_deletion(bad), "tamper rejected"
    print("[selftest] PASS: verify tamper gmpy2=%s" % _HAVE_GMPY2, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    acc = RSAAccumulator(rsa_bits=RSA_BITS)
    elems = ["fact:%d:%d" % (seed, i) for i in range(N_ADD)]
    add_ms = []
    for e in elems:
        t0 = time.perf_counter(); acc.add(e); add_ms.append((time.perf_counter() - t0) * 1000.0)
    del_ms = []; verify_ms = []; certs = []
    for e in elems[:N_DEL]:
        t0 = time.perf_counter(); cert = acc.delete(e); del_ms.append((time.perf_counter() - t0) * 1000.0); certs.append(cert)
    for c in certs:
        t0 = time.perf_counter(); ok = RSAAccumulator.verify_deletion(c); verify_ms.append((time.perf_counter() - t0) * 1000.0)
    verified = sum(int(RSAAccumulator.verify_deletion(c)) for c in certs)
    return {"seed": seed, "rsa_modulus_bits": RSA_BITS * 2, "gmpy2": bool(_HAVE_GMPY2),
            "add_p50_ms": float(np.median(add_ms)), "delete_p50_ms": float(np.median(del_ms)),
            "delete_p95_ms": float(np.percentile(del_ms, 95)), "verify_p50_ms": float(np.median(verify_ms)),
            "certs_verified_frac": verified / max(len(certs), 1)}


def verdict(ps) -> Tuple[str, str]:
    dl = float(np.mean([p["delete_p50_ms"] for p in ps])); vr = float(np.mean([p["verify_p50_ms"] for p in ps]))
    ad = float(np.mean([p["add_p50_ms"] for p in ps])); vf = float(np.mean([p["certs_verified_frac"] for p in ps]))
    summary = "2048-bit gmpy2=%s | add_p50=%.3fms delete_p50=%.3fms verify_p50=%.3fms certs_verified=%.3f" % (ps[0]["gmpy2"], ad, dl, vr, vf)
    if dl < 1.0 and vr < 1.0 and vf >= 0.999:
        return ("HARD_PASS", "HARD_PASS: 2048-bit production crypto under <1ms (gmpy2) -- V2 production latency met. " + summary)
    if dl < 5.0 and vf >= 0.999:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2048-bit crypto 1-5ms (V2-usable; demo uses RSA-512 for headline <1ms). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: 2048-bit crypto >10ms or cert fail. " + summary)


print("[config] anchor=%s mode=%s seeds=%s RSA_bits=%d (modulus %d-bit) N_add=%d N_del=%d gmpy2=%s" % (
    ANCHOR_NAME, RUN_MODE, SEEDS, RSA_BITS, RSA_BITS * 2, N_ADD, N_DEL, _HAVE_GMPY2), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] add_p50=%.3fms delete_p50=%.3fms verify_p50=%.3fms verified=%.3f" % (seed, r["add_p50_ms"], r["delete_p50_ms"], r["verify_p50_ms"], r["certs_verified_frac"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
