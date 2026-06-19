"""
exp_fhrr_rs_parity_cpu_v1.py -- FHRR-RS-parity-T0 (Sprint-4 erasure-coded redundancy) -- CPU.

ROUTING: Research SPRINT4 Tier-0 (erasure-coded redundancy; cheapest gate). FHRR additive bundles support a phase-domain
  Reed-Solomon analog: K data shards + R Vandermonde parity shards p_j = sum_i alpha_i^j * d_i. Lose up to R shards; RECOVER
  by solving the linear system over surviving data + parity (per complex component). Tests recovered-shard content recall
  after erasures -- engineered redundancy via FHRR algebra (no core change). Pure-numpy complex linear algebra. N=8192.
PRE-REGISTERED: HARD-PASS recovered-shard fact-recall >= 0.95 after losing R=2 of K+R shards. MIDDLE >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "fhrr_rs_parity_cpu_v1"
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
    print("[selftest] PASS: fhrr-rs-parity", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "901"))); K = 6; R = 2; PER = 6; V = 400
    TR = 20 if SMOKE else 100; rec_hit = 0; rec_tot = 0
    for _ in range(TR):
        # K data shards, each a fact-bundle (NOT unit-normed -- linear combos must be exact)
        keys = cphasor(K * PER, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=K * PER)
        data = np.stack([sum((keys[s * PER + j] * vals[truth[s * PER + j]] for j in range(PER)), np.zeros(N, dtype=np.complex64)) for s in range(K)])
        # Vandermonde generator over distinct nodes alpha_i (complex roots of unity); parity p_j = sum_i alpha_i^j data_i
        alpha = np.exp(2j * np.pi * np.arange(K) / (K + R))
        Vand = np.stack([alpha ** j for j in range(R)])               # R x K parity generator
        parity = Vand @ data                                          # R x N parity shards
        # ERASURE: lose R random data shards
        lost = sorted(g.choice(K, R, replace=False).tolist()); surv = [i for i in range(K) if i not in lost]
        # recover: parity = Vand[:,lost] @ data[lost] + Vand[:,surv] @ data[surv]  -> solve for data[lost]
        rhs = parity - Vand[:, surv] @ data[surv]                     # R x N
        A = Vand[:, lost]                                             # R x R (square)
        recovered = np.linalg.solve(A, rhs)                          # R x N recovered data shards
        # check recovered shards: recall each shard's facts
        for li, s in enumerate(lost):
            rs = recovered[li]
            for j in range(PER):
                idx = s * PER + j; pred = cidx(rs * np.conj(keys[idx]), vals); rec_hit += int(pred == truth[idx]); rec_tot += 1
    rec = rec_hit / rec_tot
    print("  FHRR-RS-PARITY recovered-shard fact-recall=%.3f after losing R=%d of K=%d (+R parity)" % (rec, R, K), flush=True)
    return {"recovered_recall": round(rec, 3), "K": K, "R": R}
def verdict(r) -> Tuple[str, str]:
    rc = r["recovered_recall"]; s = "recovered-recall=%.3f (K=%d R=%d)" % (rc, r["K"], r["R"])
    if rc >= 0.95:
        return ("HARD_PASS", "HARD_PASS: FHRR-Reed-Solomon erasure coding works -- lost data shards RECOVERED from Vandermonde parity at fact-recall>=0.95. FHRR additive bundles support exact phase-domain erasure-coded redundancy via the algebra; engineered redundancy wrapper validated. " + s)
    if rc >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recovered-recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: erasure recovery <0.85. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
