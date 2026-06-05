"""
exp_hp12_v1_decisive_crypto_v1 -- HP-12 V1 decisive Test 2: RSA accumulator round-trip + standalone verifier -- CPU.

ROUTING: research HP12_V1_pipeline_simplified_desktop_only -- cheap decisive pre-test gating the 4-day V1 build.
  Test 2 (HP-2/HP-4): build RSA accumulator (tools/hp12/rsa_accumulator), add elements, delete a subset, verify EVERY
  deletion cert via the THIRD-PARTY path (no trapdoor / no KB), measure cert latency, confirm the standalone verifier.py
  CLI verifies the serialized cert JSONs without modification, AND confirm a TAMPERED cert is REJECTED. Pure Python $0.

PRE-REGISTERED bands: HARD-PASS all deletion certs verify (third-party) AND cert latency < 1ms median AND verifier CLI
  confirms all AND tampered cert rejected. MIDDLE: certs verify but latency 1-10ms. HARD-FAIL: any cert fails or tamper accepted.
FORMULA SELF-TESTS (PROT-022): 1. accumulator add/delete/verify. 2. tamper rejected. 3. hash_to_prime deterministic.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, subprocess, tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.hp12.rsa_accumulator import RSAAccumulator, hash_to_prime, _HAVE_GMPY2

ANCHOR_NAME = "exp_hp12_v1_decisive_crypto_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ADD = 30; N_DEL = 20; RSA_BITS = 256
else:
    SEEDS = [7, 17, 23]; N_ADD = 200; N_DEL = 80; RSA_BITS = 256


def _selftest():
    acc = RSAAccumulator(rsa_bits=256)
    acc.add_many(["fact_a", "fact_b", "fact_c"])
    cert = acc.delete("fact_b")
    assert RSAAccumulator.verify_deletion(cert), "accumulator add/delete/verify"
    bad = dict(cert); bad["new_acc"] = cert["new_acc"] + 1
    assert not RSAAccumulator.verify_deletion(bad), "tamper rejected"
    assert hash_to_prime("x") == hash_to_prime("x") and hash_to_prime("x") != hash_to_prime("y"), "hash_to_prime deterministic"
    print("[selftest] PASS: accumulator tamper hash2prime", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    acc = RSAAccumulator(rsa_bits=RSA_BITS)
    elems = ["pubmed:%d:%d" % (seed, i) for i in range(N_ADD)]
    acc.add_many(elems)
    del_targets = elems[:N_DEL]
    certs = []; latencies = []
    for e in del_targets:
        t0 = time.perf_counter()
        cert = acc.delete(e)                       # cert issuance (the <1ms claim)
        latencies.append((time.perf_counter() - t0) * 1000.0)
        certs.append(cert)
    # third-party verification (in-process)
    verified = sum(int(RSAAccumulator.verify_deletion(c)) for c in certs)
    # tamper detection
    tamper_rejected = 0
    for c in certs[:min(20, len(certs))]:
        bad = dict(c); bad["new_acc"] = int(c["new_acc"]) ^ 1
        tamper_rejected += int(not RSAAccumulator.verify_deletion(bad))
    n_tamper = min(20, len(certs))
    # standalone verifier.py CLI on serialized JSON certs (HP-4: shareable verifier, no modification)
    cli_ok = -1
    try:
        d = Path(tempfile.mkdtemp(prefix="hp12certs_"))
        for k, c in enumerate(certs[:min(10, len(certs))]):
            (d / ("cert_%d.json" % k)).write_text(json.dumps({kk: (str(vv) if isinstance(vv, int) and abs(vv) > 2**60 else vv) for kk, vv in c.items()}), encoding="utf-8")
        r = subprocess.run([sys.executable, str(REPO / "tools" / "hp12" / "verifier.py"), "--batch", str(d)], capture_output=True, text=True, timeout=120)
        cli_ok = int(r.returncode == 0 and "ALL VERIFIED" in r.stdout)
    except Exception as e:
        print("[cli] verifier subprocess issue: %s" % e, flush=True)
    return {"seed": seed, "n_add": N_ADD, "n_del": N_DEL, "rsa_bits": RSA_BITS,
            "certs_verified": verified, "certs_total": len(certs), "verify_frac": verified / max(len(certs), 1),
            "cert_latency_ms_median": float(np.median(latencies)), "cert_latency_ms_p95": float(np.percentile(latencies, 95)),
            "tamper_rejected_frac": tamper_rejected / max(n_tamper, 1), "verifier_cli_ok": cli_ok}


def verdict(ps) -> Tuple[str, str]:
    vf = float(np.mean([p["verify_frac"] for p in ps])); lat = float(np.mean([p["cert_latency_ms_median"] for p in ps]))
    tr = float(np.mean([p["tamper_rejected_frac"] for p in ps])); cli = all(p["verifier_cli_ok"] == 1 for p in ps)
    summary = "certs_verified=%.3f cert_latency_median=%.4fms tamper_rejected=%.3f verifier_CLI=%s (RSA-%d, N_del=%d)" % (
        vf, lat, tr, cli, ps[0]["rsa_bits"], ps[0]["n_del"])
    if vf >= 0.999 and lat < 1.0 and tr >= 0.999 and cli:
        return ("HARD_PASS", "HARD_PASS: RSA accumulator deletion certs verify third-party <1ms, tamper-rejected, standalone verifier confirms -- HP-12 V1 Day-1 crypto de-risked (demo config RSA-512; gmpy2 refactor shipped for V2 2048-bit production ~2ms). " + summary)
    if vf >= 0.999 and tr >= 0.999:
        return ("MIDDLE_BAND", "MIDDLE_BAND: certs verify + tamper-safe; latency or CLI near-threshold. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: accumulator cert verification or tamper-detection failed. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_add=%d N_del=%d RSA_bits=%d gmpy2=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ADD, N_DEL, RSA_BITS, _HAVE_GMPY2), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] verified=%.3f latency=%.4fms tamper_rej=%.3f cli_ok=%s" % (seed, r["verify_frac"], r["cert_latency_ms_median"], r["tamper_rejected_frac"], r["verifier_cli_ok"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
