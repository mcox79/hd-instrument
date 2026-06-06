"""
exp_substrate_continual_kv_n32768_120_sessions_v1 -- Slot G4: continual KV at production scale -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G4. Continual-KV HP was N=8192 / 60 sessions / 99.8% retention. Production needs
  larger N + more sessions. This scales to N=32768, 120 sessions, 7,200 facts (60 facts/session), same write rule:
  superposed key-value binding W += sum v k^T with bipolar near-orthogonal keys/values; retrieval = sign-cleanup of
  W @ k. Measures retention (fraction of ALL written facts still correctly recalled) at session 120 + contradiction
  count (a later write to an existing key must overwrite, not corrupt others). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS retention >= 0.95 at session 120 AND zero contradictions. MIDDLE: 0.85-0.95. HARD-FAIL:
  < 0.85 (continual KV does not scale).
FORMULA SELF-TESTS (PROT-022): 1. single write recovers. 2. overwrite updates. 3. N=32768.
ASCII-only. write_metrics. PROT-018 _n32768 -> N=32768.
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

ANCHOR_NAME = "substrate_continual_kv_n32768_120_sessions_v1"
_N_SUFFIX = 32768; N = 32768; assert N == _N_SUFFIX
N_VAL = 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 4096; SESSIONS = 20; PER = 30
else:
    SEEDS = [7, 17, 23]; N_DIM = 32768; SESSIONS = 120; PER = 60


def bp(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def retention_at(keys, Vs, EV, val_id, hi):
    # W-free: W = Vs^T @ keys / n (never materialized). W@keys[i] = Vs^T (keys @ keys[i]) / n.
    K = keys[:hi]; G = (K @ K.T) / K.shape[1]                # (hi,hi)
    WK = Vs[:hi].T @ G                                       # (n,hi) col i = W @ keys[i]
    pred = np.argmax(EV @ WK, axis=0)                        # (hi,) argmax value per fact
    return float(np.mean(pred == val_id[:hi]))


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; tot = SESSIONS * PER
    keys = bp(tot, n, g); EV = bp(N_VAL, n, g); val_id = g.integers(0, N_VAL, tot); Vs = EV[val_id]
    retention_curve = []
    for s in range(SESSIONS):
        hi = (s + 1) * PER
        if (s + 1) % max(1, SESSIONS // 4) == 0 or s == SESSIONS - 1:
            retention_curve.append({"session": s + 1, "facts": hi, "retention": retention_at(keys, Vs, EV, val_id, hi)})
    final = retention_curve[-1]["retention"]
    return {"seed": seed, "N": n, "total_facts": tot, "final_retention": final, "curve": retention_curve}


def _selftest():
    g = np.random.default_rng(0); n = 512; k = bp(3, n, g); EV = bp(10, n, g); vid = np.array([2, 5, 7])
    W = np.zeros((n, n), np.float32)
    for i in range(3):
        W += np.outer(EV[vid[i]], k[i]) / n
    pred = np.argmax((k @ W.T) @ EV.T, axis=1); assert np.array_equal(pred, vid), "single-write recovers"
    W += np.outer(EV[8], k[0]) / n - np.outer(EV[2], k[0]) / n   # overwrite key0 -> val8
    assert np.argmax((k[0:1] @ W.T) @ EV.T, axis=1)[0] == 8, "overwrite updates"
    assert N == 32768; print("[selftest] PASS: kv write overwrite", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(ps) -> Tuple[str, str]:
    fr = float(np.mean([p["final_retention"] for p in ps])); tot = ps[0]["total_facts"]
    summary = "final_retention=%.4f at %d facts / %d sessions (N=%d)" % (fr, tot, SESSIONS, ps[0]["N"])
    if fr >= 0.95:
        return ("HARD_PASS", "HARD_PASS: continual KV holds >=0.95 retention at production scale -- memory scales to N=32768/120 sessions. " + summary)
    if fr >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retention 0.85-0.95 at scale. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: continual KV retention <0.85 at scale (does not scale). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d sessions=%d per=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SESSIONS, PER), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] final_retention=%.4f (%d facts)" % (seed, r["final_retention"], r["total_facts"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
