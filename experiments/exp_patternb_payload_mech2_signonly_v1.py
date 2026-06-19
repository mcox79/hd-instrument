"""
exp_patternb_payload_mech2_signonly_v1 -- Pattern B Mechanism 2: bipolar sign-only payload (backup) -- CPU.

ROUTING: pattern_b_payload_mech1_authorize, Anchor 2 (BACKUP to Mechanism 1). If post-bind L2 norm borders/fails, the
  fallback is bipolar sign-only encoding: represent fillers/payloads as real +-1 vectors with elementwise-product (XOR-like)
  binding, which is magnitude-free BY CONSTRUCTION (no payload can dominate). Compares chain-k composition accuracy at
  K=2,3,4 (payload regime) for complex-phasor baseline vs bipolar sign-only. CPU.
PRE-REGISTERED: HARD-PASS sign-only chain_k234 acc >= 0.85 at K=2,3,4. MID 0.70-0.85 at K=4. HARD-FAIL <0.70 at any K.
FORMULA SELF-TESTS (PROT-022): 1. sign bind/unbind inverse. 2. cleanup self. 3. bipolar values.
ASCII-only. write_metrics. PROT-018 _v1.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "patternb_payload_mech2_signonly_v1"; D = 64; PAYLOAD_W = 2.0; N_FILL = 64
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TRIALS = 40 if RUN_MODE == "smoke" else 300


def bipolar(m, d, g):
    return np.sign(g.standard_normal((m, d))).astype(np.float64)


def sbind(a, b):
    return a * b              # elementwise product of +-1 vectors (self-inverse: sbind(sbind(a,b),b)=a)


def cleanup_idx(v, book):
    return int(np.argmax(book @ v))


def _selftest():
    g = np.random.default_rng(0); a = bipolar(1, 32, g)[0]; b = bipolar(1, 32, g)[0]
    assert np.allclose(sbind(sbind(a, b), b), a), "sign bind/unbind inverse"
    book = bipolar(5, 32, g); assert cleanup_idx(book[2], book) == 2, "cleanup self"
    assert set(np.unique(a)) <= {-1.0, 1.0}, "bipolar values"
    print("[selftest] PASS: patternb-payload-mech2-signonly", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def recovery_signonly(K, g, trials):
    # bipolar sign-only: bundle = majority-sign over K bound pairs + K payload terms (all unit-magnitude by construction)
    book = bipolar(N_FILL, D, g); hit = 0; total = 0
    for _ in range(trials):
        roles = bipolar(K, D, g); fidx = g.choice(N_FILL, size=K, replace=False)
        terms = []
        for i in range(K):
            terms.append(sbind(roles[i], book[fidx[i]]))
            prole = bipolar(1, D, g)[0]; payload = bipolar(1, D, g)[0]; terms.append(sbind(prole, payload))
        B = np.sign(np.sum(terms, axis=0))   # majority-sign bundle (magnitude-free)
        for i in range(K):
            rec = sbind(B, roles[i]); hit += int(cleanup_idx(rec, book) == fidx[i]); total += 1
    return hit / total


def recovery_phasor_baseline(K, w, g, trials):
    bk = np.exp(1j * g.uniform(-np.pi, np.pi, (N_FILL, D))).astype(np.complex64); hit = 0; total = 0
    for _ in range(trials):
        roles = np.exp(1j * g.uniform(-np.pi, np.pi, (K, D))).astype(np.complex64); fidx = g.choice(N_FILL, size=K, replace=False)
        terms = []
        for i in range(K):
            terms.append(roles[i] * bk[fidx[i]])
            pr = np.exp(1j * g.uniform(-np.pi, np.pi, D)).astype(np.complex64); pl = np.exp(1j * g.uniform(-np.pi, np.pi, D)).astype(np.complex64); terms.append(w * pr * pl)
        B = np.sum(terms, axis=0)
        for i in range(K):
            rec = B * np.conj(roles[i]); hit += int(int(np.argmax((bk @ np.conj(rec)).real)) == fidx[i]); total += 1
    return hit / total


def run() -> Dict:
    g = np.random.default_rng(62)
    base = {("K%d" % K): recovery_phasor_baseline(K, PAYLOAD_W, g, TRIALS) for K in (2, 3, 4)}
    sgn = {("K%d" % K): recovery_signonly(K, g, TRIALS) for K in (2, 3, 4)}
    print("  phasor baseline (payload w=%.1f): " % PAYLOAD_W + " ".join("%s=%.3f" % (k, v) for k, v in base.items()), flush=True)
    print("  Mechanism 2 (bipolar sign-only):  " + " ".join("%s=%.3f" % (k, v) for k, v in sgn.items()), flush=True)
    return {"base": base, "signonly": sgn, "w": PAYLOAD_W}


def verdict(r) -> Tuple[str, str]:
    sv = r["signonly"]; minK = min(sv.values()); k4 = sv["K4"]
    summary = "sign-only: %s | phasor-baseline: %s (payload w=%.1f)" % ({k: round(v, 3) for k, v in sv.items()}, {k: round(v, 3) for k, v in r["base"].items()}, r["w"])
    if minK >= 0.85:
        return ("HARD_PASS", "HARD_PASS: bipolar sign-only recovers chain-k234 to >=0.85 at K=2,3,4 -- viable fallback if Mechanism 1 underperforms. " + summary)
    if k4 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sign-only partial recovery (0.70<=acc<0.85 at K=4). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sign-only does not recover chain-k234 to 0.70 at all K. " + summary)


print("[config] anchor=%s mode=%s D=%d payload_w=%.1f trials=%d" % (ANCHOR_NAME, RUN_MODE, D, PAYLOAD_W, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
