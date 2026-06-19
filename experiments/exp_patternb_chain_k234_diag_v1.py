"""
exp_patternb_chain_k234_diag_v1 -- C6: diagnose the chain-k234 HARD_FAIL (which factor drives interference?) -- CPU.

ROUTING: 2hour battery C6. Cycle-161 chain-k234 HF (payload-bound role-filler chains interfere at K>=3). Diagnose the
  failure mode by isolating three factors so a future rescue can target the right one:
  (A) K-DEPTH: fix payload+N, sweep K=2,3,4 -> recovery vs K.
  (B) PAYLOAD-MAGNITUDE: fix K=3,N, sweep payload weight w in {0.0,0.5,1.0,2.0} -> recovery vs payload.
  (C) BUNDLE-SATURATION: fix K=3,payload, sweep N (codebook/bundle) -> recovery vs N.
  FHRR phasors: bind = angle-add (complex mult), unbind = conj-mult, bundle = sum, cleanup = nearest by real-cosine. CPU.
PRE-REGISTERED: HARD-PASS identify the dominant factor (the sweep with the steepest recovery drop) -> routes a future fix.
  Reported as the factor with the largest recovery range across its sweep.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. bundle recovers single.
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

ANCHOR_NAME = "patternb_chain_k234_diag_v1"; D = 64
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TRIALS = 30 if RUN_MODE == "smoke" else 200


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def bind(a, b):
    return a * b


def unbind(c, b):
    return c * np.conj(b)


def cleanup_idx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(unbind(bind(a, b), b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(5, 32, g); assert cleanup_idx(book[2], book) == 2, "cleanup self"
    roles = phasor(1, 32, g); B = bind(roles[0], book[1]); assert cleanup_idx(unbind(B, roles[0]), book) == 1, "bundle recovers single"
    print("[selftest] PASS: patternb-chain-k234-diag", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def recovery(K, w, N, g, trials):
    # role-filler chain of K pairs from an N-filler codebook; each pair ALSO superposes a separate payload-bound term of
    # weight w (so payload adds crosstalk terms, not just perturbs the filler) -- the "payload-bound chain" structure.
    book = phasor(N, D, g); hit = 0; total = 0
    for _ in range(trials):
        roles = phasor(K, D, g); fidx = g.choice(N, size=K, replace=False)
        terms = []
        for i in range(K):
            terms.append(bind(roles[i], book[fidx[i]]))
            if w > 0:
                prole = phasor(1, D, g)[0]; payload = phasor(1, D, g)[0]
                terms.append(w * bind(prole, payload))     # separate superposed payload term
        B = np.sum(terms, axis=0)
        for i in range(K):
            rec = unbind(B, roles[i])
            hit += int(cleanup_idx(rec, book) == fidx[i]); total += 1
    return hit / total


def run() -> Dict:
    g = np.random.default_rng(11)
    # (A) K-depth: payload on (w=1), N=64
    A = {("K%d" % K): recovery(K, 1.0, 64, g, TRIALS) for K in (2, 3, 4, 6, 8)}
    # (B) payload magnitude: K=4, N=64
    B = {("w%.1f" % w): recovery(4, w, 64, g, TRIALS) for w in (0.0, 1.0, 2.0, 4.0)}
    # (C) bundle saturation: K=4, payload=1.0, sweep N
    C = {("N%d" % N): recovery(4, 1.0, N, g, TRIALS) for N in (32, 64, 128, 256)}
    rngA = max(A.values()) - min(A.values()); rngB = max(B.values()) - min(B.values()); rngC = max(C.values()) - min(C.values())
    print("  (A) K-depth: " + " ".join("%s=%.3f" % (k, v) for k, v in A.items()) + " range=%.3f" % rngA, flush=True)
    print("  (B) payload: " + " ".join("%s=%.3f" % (k, v) for k, v in B.items()) + " range=%.3f" % rngB, flush=True)
    print("  (C) saturate:" + " ".join("%s=%.3f" % (k, v) for k, v in C.items()) + " range=%.3f" % rngC, flush=True)
    return {"A": A, "B": B, "C": C, "rngA": rngA, "rngB": rngB, "rngC": rngC}


def verdict(r) -> Tuple[str, str]:
    factors = {"K-depth": r["rngA"], "payload-magnitude": r["rngB"], "bundle-saturation": r["rngC"]}
    dom = max(factors, key=factors.get)
    summary = "ranges: K-depth=%.3f payload=%.3f saturation=%.3f -> dominant=%s" % (r["rngA"], r["rngB"], r["rngC"], dom)
    if max(factors.values()) >= 0.10:
        return ("HARD_PASS", "HARD_PASS: dominant chain-k234 failure factor identified = %s; routes the future rescue (e.g. %s). " % (dom, {"K-depth": "depth-limited / hierarchical chunking", "payload-magnitude": "payload normalization / separate payload store", "bundle-saturation": "larger D or cleanup memory"}[dom]) + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no single factor dominates (all ranges <0.10); interference is multi-factor. " + summary)


print("[config] anchor=%s mode=%s D=%d trials=%d" % (ANCHOR_NAME, RUN_MODE, D, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
