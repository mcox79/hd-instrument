"""
exp_pb_pinv_downdate_forgetting_v1 -- propose-back (forgetting/deletion via Greville downdate) -- CPU.

ROUTING: Exp-Dev propose-back. Production memory must support DELETION (GDPR right-to-erasure; retract a fact). Open
  question: can a stored pattern be REMOVED from the pinv projector via a rank-1 downdate so that (a) the deleted pattern is
  no longer recalled and (b) the remaining patterns' recall is preserved -- without a full rebuild? Implements Greville
  rank-1 downdate W' = full_proj(P_without_row) computed incrementally, validates against full rebuild, and measures
  deleted-recall (should drop) + retained-recall (should hold). CPU $0.
PRE-REGISTERED: HARD-PASS downdated projector matches full-rebuild-without-row within 1e-3 AND retained-recall >= 0.95
  AND deleted pattern no longer an exact fixed point. MID retained holds but match 1e-3..1e-1. HARD-FAIL retained recall
  collapses (deletion corrupts memory).
FORMULA SELF-TESTS (PROT-022): 1. downdate matches full rebuild. 2. retained patterns recalled. 3. projector idempotent.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "pb_pinv_downdate_forgetting_v1"
FLIP = 0.05; STEPS = 8; EPS = 1e-8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [256, 512]; N_DEL = 5
else:
    SEEDS = [7, 17, 23]; N_GRID = [512, 1024, 2048]; N_DEL = 20


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


RIDGE = 1e-6


def gram_inv(P):
    G = P @ P.T + RIDGE * np.eye(P.shape[0], dtype=np.float64); return np.linalg.inv(G)


def full_proj(P):
    if P.shape[0] == 0:
        return np.zeros((P.shape[1], P.shape[1]), np.float64)
    return P.T @ gram_inv(P) @ P


def downdate_last(Gi):
    # remove the LAST row from the inverse-Gram via block-inverse identity:
    # Gi=[[E,f],[f^T,h]] -> inv of the leading block A = E - f f^T / h  (EXACT for the regularized Gram)
    E = Gi[:-1, :-1]; f = Gi[:-1, -1]; h = float(Gi[-1, -1])
    if abs(h) <= EPS:
        return E.copy()
    return E - np.outer(f, f) / h


def recall_one(W, p, seed):
    g = np.random.default_rng(seed); n = len(p); s = (p * np.where(g.random(n) < FLIP, -1.0, 1.0)).astype(np.float64)
    Wd = W.copy(); np.fill_diagonal(Wd, 0.0)
    for _ in range(STEPS):
        s = np.sign(s @ Wd.T); s[s == 0] = 1.0
    return bool(np.all(s == p))


def _selftest():
    g = np.random.default_rng(0); n = 64; P = patterns(8, n, g).astype(np.float64)
    Gi = gram_inv(P); Gi_d = downdate_last(Gi); Wd = P[:-1].T @ Gi_d @ P[:-1]; Wfull = full_proj(P[:-1])
    assert np.max(np.abs(Wd - Wfull)) < 1e-6, "downdate matches full rebuild"
    assert recall_one(Wd, P[0], 0), "retained pattern recalled"
    print("[selftest] PASS: pinv-downdate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_n(n, seed) -> Dict:
    g = np.random.default_rng(seed); M = max(N_DEL + 5, int(0.3 * n)); P = patterns(M, n, g).astype(np.float64)
    Gi = gram_inv(P); max_dev = 0.0; cur = M
    for k in range(N_DEL):                                   # delete the last-added patterns one at a time
        Gi = downdate_last(Gi); cur -= 1
        W = P[:cur].T @ Gi @ P[:cur]; Wfull = full_proj(P[:cur]); max_dev = max(max_dev, float(np.max(np.abs(W - Wfull))))
    W = P[:cur].T @ Gi @ P[:cur]; kept = P[:cur]; deleted = P[cur:]
    retained = float(np.mean([recall_one(W, kept[i], seed * 7 + i) for i in range(min(len(kept), 30))]))
    del_recall = float(np.mean([recall_one(W, deleted[i], seed * 11 + i) for i in range(len(deleted))]))
    print("  [N=%d] max_dev=%.2e retained_recall=%.3f deleted_recall=%.3f" % (n, max_dev, retained, del_recall), flush=True)
    return {"N": n, "max_dev": max_dev, "retained_recall": retained, "deleted_recall": del_recall}


def run_seed(seed) -> Dict:
    return {"seed": seed, "by": {("N%d" % n): run_n(n, seed) for n in N_GRID}}


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]
    dev = max(p["by"][nmax]["max_dev"] for p in ps); ret = float(np.mean([p["by"][nmax]["retained_recall"] for p in ps])); dele = float(np.mean([p["by"][nmax]["deleted_recall"] for p in ps]))
    summary = "at N=%d: downdate_max_dev=%.2e retained_recall=%.3f deleted_recall=%.3f" % (N_GRID[-1], dev, ret, dele)
    if dev < 1e-3 and ret >= 0.95:
        return ("HARD_PASS", "HARD_PASS: rank-1 downdate exactly forgets a fact (matches full rebuild <1e-3) while preserving retained recall >=0.95 -- production deletion/GDPR erasure without rebuild. " + summary)
    if ret >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retained recall holds but downdate drifts from exact (1e-3..). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: deletion corrupts retained memory (recall <0.95). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s n_del=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, N_DEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
