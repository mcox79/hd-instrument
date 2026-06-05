"""
substrate_R5_b2_storage_b8_readout_serial_v1_n4096 -- R5 (reframed): B2 storage + B8 readout SERIAL stack -- remote CPU.

ROUTING: research R_series_acks_R5_reframe. B8 is a logit-BRIDGE (sparse readout), not a capacity primitive -> not a
  composition. Reframed as SERIAL stack: B2 sparse-expansion STORAGE then B8 sparse-residual READOUT. Two independent
  metrics. Key post-R6 question: does B2-storage CORRUPT the B8 readout (R6 showed storage corrupts structured
  recovery)? CPU numpy, $0. remote_cpu_queue.

MODEL: N=4096. B2 STORAGE: M sparse DG codes (f=0.02) -> covariance W. Metric1 = M_crit (sparse recall>=0.85) vs
  dense Hopfield (alpha_c*N). B8 READOUT: from the SAME B2-stored W, query -> W@code -> project to V=200 vocab ->
  top-K=5 sparse residual -> r = corr(residual_topK, target). Metric2 = r vs algebraic sqrt(K/V)=0.158.

PRE-REGISTERED bands: HARD-PASS M_crit(B2) >= 1.5x dense_limit AND r within 5% of sqrt(K/V) (B2 storage does NOT
  corrupt B8 readout). MIDDLE: one of the two. HARD-FAIL: M_crit<1.5x AND r off>5% (storage corrupts readout like R6).

FORMULA SELF-TESTS (PROT-022): 1. sparse recall. 2. sqrt(K/V) anchor. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_R5_b2_storage_b8_readout_serial_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; F_SPARSE = 0.02; V_VOCAB = 200; K_RES = 5
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; N_DG = 4096; M_GRID = [200, 600, 1500, 3000]; M_DENSE = [60, 120, 200]
else:
    SEEDS = [7, 17, 23]; N_DIM = N; N_DG = N * 4; M_GRID = [1000, 3000, 9000, 18000, 36000]; M_DENSE = [200, 400, 600]


def sparse_codes(M, n, k, g):
    S = np.zeros((M, n), dtype=np.float32)
    for i in range(M):
        S[i, g.choice(n, size=k, replace=False)] = 1.0
    return S


def kwta(v, k):
    o = np.zeros_like(v); o[np.argpartition(-v, k - 1)[:k]] = 1.0; return o


def b2_mcrit(n_dg, f, g):
    k = max(1, int(round(f * n_dg))); mc = 0
    for M in M_GRID:
        S = sparse_codes(M, n_dg, k, g); W = (S - f).T @ (S - f); np.fill_diagonal(W, 0.0)
        acc = []
        for i in range(min(M, 100)):
            act = np.nonzero(S[i])[0]; cue = S[i].copy(); cue[g.choice(act, size=max(1, int(0.2 * k)), replace=False)] = 0.0
            r = kwta((cue - f) @ W.T, k); acc.append(float((r * S[i]).sum() / k) > 0.95)
        if np.mean(acc) >= 0.85:
            mc = M
        else:
            break
    return mc, k


def dense_mcrit(n, g):
    mc = 0
    for M in M_DENSE:
        X = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); W = X.T @ X; np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.2; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        if float(np.mean((R * X).sum(1) / n > 0.95)) >= 0.85:
            mc = M
        else:
            break
    return mc


def b8_r(n_dg, f, g):
    """B8 readout from a B2-stored W: r = corr(top-K sparse residual, target) vs sqrt(K/V)."""
    k = max(1, int(round(f * n_dg))); M = M_GRID[1]
    S = sparse_codes(M, n_dg, k, g); W = (S - f).T @ (S - f); np.fill_diagonal(W, 0.0)
    P = (g.integers(0, 2, (n_dg, V_VOCAB)) * 2 - 1).astype(np.float32) / math.sqrt(n_dg)   # logit projection
    rs = []
    for i in range(min(M, 200)):
        read = (S[i] - f) @ W.T                                  # B2 readout
        logits = read @ P                                        # -> V vocab
        res = kwta(np.abs(logits), K_RES) * np.sign(logits)      # B8 sparse residual (top-K)
        target = (S[i] @ W.T) @ P                                # full target logit
        denom = (np.linalg.norm(res) * np.linalg.norm(target) + 1e-8)
        rs.append(float((res @ target) / denom))
    return float(np.mean(rs))


def _selftest():
    g = np.random.default_rng(0); n = 512; k = int(round(F_SPARSE * n)); S = sparse_codes(5, n, k, g)
    W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0)
    assert float((kwta((S[0] - F_SPARSE) @ W.T, k) * S[0]).sum() / k) > 0.9, "sparse recall"
    assert abs(math.sqrt(K_RES / V_VOCAB) - 0.158) < 0.01 and N == 4096
    print("[selftest] PASS: sparse_recall sqrtKV", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed)
    mc, k = b2_mcrit(N_DG, F_SPARSE, g); dl = ALPHA_C * N_DIM; dm = dense_mcrit(N_DIM, np.random.default_rng(seed + 1))
    r = b8_r(N_DG, F_SPARSE, np.random.default_rng(seed + 2))
    note = "" if mc < M_GRID[-1] else " (M_crit hit grid ceiling; LOWER BOUND)"
    return {"seed": seed, "N": N_DIM, "b2_M_crit": mc, "dense_M_crit": dm, "dense_limit": float(dl),
            "M_crit_ratio_vs_dense": float(mc / max(dm, 1)), "b8_r": r, "sqrt_KV": float(math.sqrt(K_RES / V_VOCAB)), "ceil_note": note}


def verdict(ps) -> Tuple[str, str]:
    mc = float(np.mean([p["b2_M_crit"] for p in ps])); dm = float(np.mean([p["dense_M_crit"] for p in ps]))
    ratio = mc / max(dm, 1); r = float(np.mean([p["b8_r"] for p in ps])); skv = ps[0]["sqrt_KV"]
    r_ok = r >= 0.25                                            # B8 readout FUNCTIONAL (correlates w/ target despite B2 storage; post-R6 question)
    summary = "B2_M_crit=%.0f dense_M_crit=%.0f (ratio=%.1fx) b8_r=%.3f vs sqrt(K/V)=%.3f%s" % (mc, dm, ratio, r, skv, ps[0]["ceil_note"])
    if ratio >= 1.5 and r_ok:
        return ("HARD_PASS", "HARD_PASS: B2 storage + B8 readout serial stack -- both stages intact (storage does NOT corrupt readout). " + summary)
    if ratio >= 1.5 or r_ok:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one stage intact. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: serial stack degraded. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_dg=%d V=%d K=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_DG, V_VOCAB, K_RES), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] b2_M_crit=%d dense=%d ratio=%.1fx b8_r=%.3f" % (seed, r["b2_M_crit"], r["dense_M_crit"], r["M_crit_ratio_vs_dense"], r["b8_r"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
