"""
exp_patternb_payload_mech1_l2norm_v1 -- Pattern B Mechanism 1: post-bind L2 normalization rescues chain-k234 -- CPU.

ROUTING: pattern_b_payload_mech1_authorize, Anchor 1 (PRIMARY). My chain_k234 diagnostic found payload-MAGNITUDE is the
  dominant interference factor. Mechanism 1 = normalize each bound term to unit L2 norm BEFORE bundling, so a large payload
  cannot dominate the superposition. Compares chain-k composition accuracy at K=2,3,4 (payload-bound chains, failing regime
  payload w=2) WITHOUT vs WITH post-bind L2 normalization. FHRR phasors. CPU.
PRE-REGISTERED: HARD-PASS chain_k234_acc_normalized >= 0.85 at K=2,3,4 simultaneously. MID 0.70-0.85 at K=4. HARD-FAIL <0.70
  at any K (-> fall back to Mechanism 2 sign-only).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. normalization is unit-norm.
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

ANCHOR_NAME = "patternb_payload_mech1_l2norm_v1"; D = 64; PAYLOAD_W = 2.0; N_FILL = 64
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TRIALS = 40 if RUN_MODE == "smoke" else 300


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def bind(a, b):
    return a * b


def unbind(c, b):
    return c * np.conj(b)


def l2norm(v):
    return v / (np.linalg.norm(v) + 1e-12)


def cleanup_idx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(unbind(bind(a, b), b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(5, 32, g); assert cleanup_idx(book[2], book) == 2, "cleanup self"
    assert abs(np.linalg.norm(l2norm(phasor(1, 32, g)[0] * 5.0)) - 1.0) < 1e-5, "normalization is unit-norm"
    print("[selftest] PASS: patternb-payload-mech1-l2norm", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def recovery(K, w, normalize, g, trials):
    book = phasor(N_FILL, D, g); hit = 0; total = 0
    for _ in range(trials):
        roles = phasor(K, D, g); fidx = g.choice(N_FILL, size=K, replace=False)
        terms = []
        for i in range(K):
            t1 = bind(roles[i], book[fidx[i]])
            terms.append(l2norm(t1) if normalize else t1)
            if w > 0:
                prole = phasor(1, D, g)[0]; payload = phasor(1, D, g)[0]; t2 = w * bind(prole, payload)
                terms.append(l2norm(t2) if normalize else t2)
        B = np.sum(terms, axis=0)
        for i in range(K):
            rec = unbind(B, roles[i]); hit += int(cleanup_idx(rec, book) == fidx[i]); total += 1
    return hit / total


def run() -> Dict:
    g = np.random.default_rng(61)
    base = {("K%d" % K): recovery(K, PAYLOAD_W, False, g, TRIALS) for K in (2, 3, 4)}
    norm = {("K%d" % K): recovery(K, PAYLOAD_W, True, g, TRIALS) for K in (2, 3, 4)}
    print("  baseline (payload w=%.1f, no norm): " % PAYLOAD_W + " ".join("%s=%.3f" % (k, v) for k, v in base.items()), flush=True)
    print("  Mechanism 1 (post-bind L2 norm):    " + " ".join("%s=%.3f" % (k, v) for k, v in norm.items()), flush=True)
    return {"base": base, "norm": norm, "w": PAYLOAD_W}


def verdict(r) -> Tuple[str, str]:
    nv = r["norm"]; minK = min(nv.values()); k4 = nv["K4"]
    summary = "normalized: %s | baseline: %s (payload w=%.1f)" % ({k: round(v, 3) for k, v in nv.items()}, {k: round(v, 3) for k, v in r["base"].items()}, r["w"])
    if minK >= 0.85:
        return ("HARD_PASS", "HARD_PASS: post-bind L2 normalization recovers chain-k234 to >=0.85 at K=2,3,4 -- Mechanism 1 is the v1.1 fix (ship in next release). " + summary)
    if k4 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial recovery (0.70<=acc<0.85 at K=4) -- Mechanism 1 helps but not full; acceptable if HP tests pass. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: L2 normalization does not recover chain-k234 to 0.70 at all K -- fall back to Mechanism 2 (sign-only). " + summary)


print("[config] anchor=%s mode=%s D=%d payload_w=%.1f trials=%d" % (ANCHOR_NAME, RUN_MODE, D, PAYLOAD_W, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
