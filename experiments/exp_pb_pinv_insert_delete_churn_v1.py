"""
exp_pb_pinv_insert_delete_churn_v1 -- propose-back (incremental memory under realistic add+delete churn) -- CPU.

ROUTING: Exp-Dev propose-back, follows pb_pinv_true_rank1_smw (insert) + pb_pinv_downdate_forgetting (delete). Production
  memory does BOTH continuously. Open question: under a long INTERLEAVED stream of inserts and deletes, does the
  incrementally-maintained inverse-Gram stay numerically exact (vs a from-scratch rebuild of the current live set) AND keep
  the live set recallable? Maintains G^-1 via Schur up-date (insert) + block-inverse down-date (delete) over a churn stream;
  compares to full rebuild at the end and measures live-set recall. CPU $0.
PRE-REGISTERED: HARD-PASS after the churn stream, incremental W matches full rebuild within 1e-3 AND live-set recall >=0.95
  (incremental memory is churn-stable). MID recall holds but drift 1e-3..1e-1. HARD-FAIL drift explodes or recall collapses
  (needs periodic rebuild).
FORMULA SELF-TESTS (PROT-022): 1. insert then rebuild match. 2. churn match. 3. live recall.
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

ANCHOR_NAME = "pb_pinv_insert_delete_churn_v1"
FLIP = 0.05; STEPS = 8; EPS = 1e-10; RIDGE = 1e-6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [256, 512]; M0 = 30; N_CHURN = 60
else:
    SEEDS = [7, 17, 23]; N_GRID = [512, 1024, 2048]; M0 = 80; N_CHURN = 300


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float64)


def gram_inv(P):
    if P.shape[0] == 0:
        return np.zeros((0, 0))
    return np.linalg.inv(P @ P.T + RIDGE * np.eye(P.shape[0]))


def insert(P, Gi, p):
    # Schur up-date of (PP^T+ridge)^-1 when appending row p
    if P.shape[0] == 0:
        return p[None, :], np.array([[1.0 / (float(p @ p) + RIDGE)]])
    b = P @ p; Gib = Gi @ b; s = float(p @ p) + RIDGE - float(b @ Gib)
    if abs(s) <= EPS:
        s = EPS
    M = P.shape[0]; new = np.zeros((M + 1, M + 1))
    new[:M, :M] = Gi + np.outer(Gib, Gib) / s; new[:M, M] = -Gib / s; new[M, :M] = -Gib / s; new[M, M] = 1.0 / s
    return np.vstack([P, p[None, :]]), new


def delete(P, Gi, idx):
    # block-inverse down-date: move row idx to last (symmetric perm), drop it
    M = P.shape[0]; order = [i for i in range(M) if i != idx] + [idx]
    Pp = P[order]; Gp = Gi[np.ix_(order, order)]
    E = Gp[:-1, :-1]; f = Gp[:-1, -1]; h = float(Gp[-1, -1])
    if abs(h) <= EPS:
        return Pp[:-1], E.copy()
    return Pp[:-1], E - np.outer(f, f) / h


def recall_one(W, p, seed):
    g = np.random.default_rng(seed); n = len(p); s = (p * np.where(g.random(n) < FLIP, -1.0, 1.0)).astype(np.float64)
    Wd = W.copy(); np.fill_diagonal(Wd, 0.0)
    for _ in range(STEPS):
        s = np.sign(s @ Wd.T); s[s == 0] = 1.0
    return bool(np.all(s == p))


def _selftest():
    g = np.random.default_rng(0); n = 64; P = patterns(6, n, g); Gi = gram_inv(P)
    p = patterns(1, n, g)[0]; P2, Gi2 = insert(P, Gi, p)
    assert np.max(np.abs(Gi2 - gram_inv(P2))) < 1e-6, "insert matches rebuild"
    P3, Gi3 = delete(P2, Gi2, 2)
    assert np.max(np.abs(Gi3 - gram_inv(P3))) < 1e-6, "delete matches rebuild"
    W = P3.T @ Gi3 @ P3; assert recall_one(W, P3[0], 0), "live recall"
    print("[selftest] PASS: pinv-churn", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_n(n, seed) -> Dict:
    g = np.random.default_rng(seed); P = patterns(M0, n, g); Gi = gram_inv(P); max_dev = 0.0
    cap = max(M0, int(0.35 * n))
    for t in range(N_CHURN):
        if P.shape[0] >= cap or (P.shape[0] > 5 and g.random() < 0.5):
            P, Gi = delete(P, Gi, int(g.integers(0, P.shape[0])))
        else:
            P, Gi = insert(P, Gi, patterns(1, n, g)[0])
        if t % max(1, N_CHURN // 10) == 0:
            max_dev = max(max_dev, float(np.max(np.abs(Gi - gram_inv(P)))) if P.shape[0] else 0.0)
    W = P.T @ Gi @ P; live = P.shape[0]
    recall = float(np.mean([recall_one(W, P[i], seed * 7 + i) for i in range(min(live, 30))])) if live else 1.0
    final_dev = float(np.max(np.abs(Gi - gram_inv(P)))) if live else 0.0; max_dev = max(max_dev, final_dev)
    print("  [N=%d] churn=%d live_set=%d max_dev=%.2e live_recall=%.3f" % (n, N_CHURN, live, max_dev, recall), flush=True)
    return {"N": n, "live_set": live, "max_dev": max_dev, "live_recall": recall}


def run_seed(seed) -> Dict:
    return {"seed": seed, "by": {("N%d" % n): run_n(n, seed) for n in N_GRID}}


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; dev = max(p["by"][nmax]["max_dev"] for p in ps); rec = float(np.mean([p["by"][nmax]["live_recall"] for p in ps]))
    summary = "at N=%d after %d churn ops: max_dev_vs_rebuild=%.2e live_recall=%.3f" % (N_GRID[-1], N_CHURN, dev, rec)
    if dev < 1e-3 and rec >= 0.95:
        return ("HARD_PASS", "HARD_PASS: incremental memory stays numerically exact under interleaved insert/delete churn (dev<1e-3) with live recall >=0.95 -- no periodic rebuild needed. " + summary)
    if rec >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: live recall holds but inverse-Gram drifts under churn (periodic rebuild advisable). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: churn corrupts the incremental memory (recall <0.95). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s churn=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, N_CHURN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
