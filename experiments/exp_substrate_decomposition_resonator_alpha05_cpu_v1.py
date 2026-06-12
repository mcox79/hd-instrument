"""
exp_substrate_decomposition_resonator_alpha05_cpu_v1.py -- PP-407 alpha=0.5 verification: identity-augmented resonator decode -- CPU.

ROUTING: strategy_request_to_exp_dev_2026-06-12_PP407_alpha_0.5_verification_cell (Cycle 250, v588 PP-410 follow-on).
  Substrate-quality-first; NO LLM frame. PP-410 showed alpha=0.5 identity-augmentation recovers PP-406 COMPOSITION cleanup
  0.889 -> 1.0 (+82pct structural clustering retained). PP-407 (resonator DECOMPOSITION) sits at the same clustered-codebook
  ceiling (precision@1 K=241/F=3/noise=0 = 0.911). Same mechanism -> same fix should apply. This cell verifies it: run the
  resonator decode with atoms encoded as identity-augmented vectors (algebra_hrr + 0.5 * name_token_HRR) vs plain algebra_hrr.

PRE-REGISTERED (strict-HP target from PP-407 row):
  HARD-PASS: augmented precision@1 at K=241/F=3/noise=0 >= 0.95. MIDDLE: [0.90, 0.95) (lift but doesn't clear strict bar).
  HARD-FAIL: < 0.90 (encoding fix does NOT generalize to resonator-iteration cleanup). UNKNOWN if corpus load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, hashlib, re
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_decomposition_resonator_alpha05_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DIM = 1024
ALPHA = 0.5
GRID = [(2, 241, 0.0), (3, 241, 0.0), (3, 241, 0.1), (4, 241, 0.0), (6, 241, 0.0), (8, 241, 0.0), (3, 50, 0.0), (3, 100, 0.0)]
SEEDS = [7, 8, 9]
N_TRIALS = 20
ITERS = 10
_TOK = re.compile(r"[a-z0-9]+")


def _bind(a, b): return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real
def _unbind(c, b): return np.fft.ifft(np.fft.fft(c) * np.fft.fft(b).conj()).real


def _unitary_roles(n, dim, rng):
    v = rng.standard_normal((n, dim)); fv = np.fft.fft(v, axis=1)
    fv = fv / (np.abs(fv) + 1e-12); return np.fft.ifft(fv, axis=1).real


def _tok_vec(t):
    h = int(hashlib.sha256(("nametok::" + t).encode()).hexdigest(), 16); rng = np.random.default_rng(h % (2 ** 63 - 1))
    v = rng.standard_normal(DIM); return v / (np.linalg.norm(v) + 1e-12)


def _name_vec(aid):
    toks = _TOK.findall(aid.lower())
    if not toks: return np.zeros(DIM)
    s = np.sum([_tok_vec(t) for t in toks], axis=0); n = np.linalg.norm(s); return s / n if n > 0 else s


def _load(alpha):
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=DIM); ai.build(ps)
    A, N = [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None:
            A.append(av.algebra_hrr); N.append(_name_vec(aid))
    if not A:
        return None
    A = np.stack(A).astype(np.float64); A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    N = np.stack(N).astype(np.float64)
    M = A + alpha * N
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)


def _cleanup_idx(v, C, Cn):
    return int(np.argmax((C @ v) / (np.linalg.norm(v) + 1e-12) / Cn))


def _decode(X, roles, C, Cn, F, iters):
    est = [_cleanup_idx(_unbind(X, roles[i]), C, Cn) for i in range(F)]
    for _ in range(iters):
        changed = False
        for i in range(F):
            resid = X.copy()
            for k in range(F):
                if k != i: resid = resid - _bind(roles[k], C[est[k]])
            ni = _cleanup_idx(_unbind(resid, roles[i]), C, Cn)
            if ni != est[i]: est[i] = ni; changed = True
        if not changed: break
    return est


def _precision(M, F, K, noise, seeds, n_trials, iters):
    hits = 0; tot = 0
    for sd in seeds:
        rng = np.random.default_rng(sd * 100 + K + F)
        Cidx = rng.permutation(M.shape[0])[:K]; C = M[Cidx]; Cn = np.linalg.norm(C, axis=1) + 1e-12
        for _ in range(n_trials):
            fillers = rng.permutation(K)[:F]; roles = _unitary_roles(F, DIM, rng)
            X = np.sum([_bind(roles[i], C[fillers[i]]) for i in range(F)], axis=0); X = X / (np.linalg.norm(X) + 1e-12)
            if noise > 0: X = X + noise * (rng.standard_normal(DIM) / (np.linalg.norm(rng.standard_normal(DIM)) + 1e-12))
            dec = _decode(X, roles, C, Cn, F, iters)
            hits += sum(int(dec[i] == fillers[i]) for i in range(F)); tot += F
    return hits / tot if tot else 0.0


def run() -> Dict:
    M_aug = _load(ALPHA); M_plain = _load(0.0)
    if M_aug is None:
        return {"error": "no_algebra_atoms"}
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 6 if SMOKE else N_TRIALS
    iters = 4 if SMOKE else ITERS
    grid = [(3, 241, 0.0), (3, 50, 0.0)] if SMOKE else GRID
    cells = []
    for (F, K, nz) in grid:
        K = min(K, M_aug.shape[0])
        p_plain = _precision(M_plain, F, K, nz, seeds, n_trials, iters)
        p_aug = _precision(M_aug, F, K, nz, seeds, n_trials, iters)
        cells.append({"F": F, "K": K, "noise": nz, "precision1_plain": round(p_plain, 4), "precision1_alpha05": round(p_aug, 4), "lift": round(p_aug - p_plain, 4)})
        print("  F=%d K=%3d noise=%.1f  plain=%.4f  alpha0.5=%.4f  lift=%+.4f" % (F, K, nz, p_plain, p_aug, p_aug - p_plain), flush=True)
    return {"cells": cells, "alpha": ALPHA, "n_atoms": M_aug.shape[0], "n_seeds": len(seeds), "iters": iters}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    tgt = next((c for c in r["cells"] if c["F"] == 3 and c["K"] == min(241, r["n_atoms"]) and c["noise"] == 0.0), None)
    if tgt is None:
        return ("UNKNOWN", "UNKNOWN: target cell F=3/K=241/noise=0 missing.")
    p = tgt["precision1_alpha05"]
    s = ("target F=3/K=%d/noise=0: plain=%.4f alpha0.5=%.4f lift=%+.4f; full grid=%s" %
         (tgt["K"], tgt["precision1_plain"], p, tgt["lift"], [(c["F"], c["K"], c["noise"], c["precision1_plain"], c["precision1_alpha05"]) for c in r["cells"]]))
    if p >= 0.95:
        return ("HARD_PASS", "HARD_PASS: alpha=0.5 identity-augmented resonator decode reaches precision@1>=0.95 at K=241/F=3/noise=0 -- the encoding fix GENERALIZES from composition cleanup to resonator decomposition (two-vector architecture confirmed 2nd appearance). " + s)
    if p >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha=0.5 precision@1 in [0.90,0.95) -- lift demonstrated but doesn't fully clear strict bar; alpha sweep may help. " + s)
    return ("HARD_FAIL", "HARD_FAIL: alpha=0.5 precision@1 <0.90 -- the encoding fix does NOT generalize to resonator-iteration cleanup; decomposition needs a different lever. " + s)


def _selftest():
    rng = np.random.default_rng(1)
    assert abs(np.dot(_name_vec("a/b_c"), _name_vec("a/b_c")) - 1.0) < 1e-6
    R = _unitary_roles(2, 256, rng); assert np.max(np.abs(np.abs(np.fft.fft(R[0])) - 1.0)) < 1e-6
    print("[selftest] PASS: resonator-alpha05", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
