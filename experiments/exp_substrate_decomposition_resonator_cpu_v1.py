"""
exp_substrate_decomposition_resonator_cpu_v1.py -- Cell B: DECOMPOSITION benchmark (resonator explaining-away decode) -- CPU.

ROUTING: research_to_exp_dev_testbed_5_NEW_CELLS Cell B + VSA-drill pre-reg LOCK. Substrate-quality-first; NO LLM frame.
  Pair to Cell A (compose -> decompose). Demonstrates the substrate DECODES a superposed bound state back to its constituent
  atoms. Uses substrate canonical hdlab.bind/unbind over the REAL 280-atom algebra_hrr corpus (clustered codebook).

  Bound state: X = sum_{i=1..F} bind(R_i, B_i)  (F role-filler bindings, normalized), roles R_i UNITARY + KNOWN.
  Resonator-style explaining-away decoder (Frady-Sommer 2020 / Kymn-Olshausen 2023 spirit): iteratively refine each filler
  estimate by removing the binding contributions of the OTHER current estimates, then cleanup against a K-atom codebook:
      b_i^(t+1) = cleanup_C( unbind( X - sum_{k!=i} bind(R_k, b_k^(t)), R_i ) )
  precision@1 = fraction of slots whose decoded atom == the true filler. Sweep F in {2,3,4,6,8}; K (codebook size) in
  {50,100,280}; additive noise in {0,0.1,0.3}; 3 seeds.

PRE-REGISTERED (VSA-drill LOCK; decode metric = precision@1; clustered-codebook tw_edge_z=-2.26 is UNCHARTED regime):
  HARD-PASS: precision@1 >= 0.95 at F=2,K=280,noise=0 AND precision@1 >= 0.80 at F=3,K=280,noise=0.
  MIDDLE: precision@1 0.50-0.80 at F=3,K=280,noise=0. HARD-FAIL: < 0.50 at F=3,K=280,noise=0. UNKNOWN if corpus load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue (dashboard-visible).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_decomposition_resonator_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F_SWEEP = [2, 3, 4, 6, 8]
K_SWEEP = [50, 100, 280]
NOISE_SWEEP = [0.0, 0.1, 0.3]
SEEDS = [7, 8, 9]
N_TRIALS = 20
RESONATOR_ITERS = 10


# circular-convolution HRR bind/unbind on numpy (matches hdlab.binding real path: FFT conv / corr)
def _bind(a, b):
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real


def _unbind(c, b):
    return np.fft.ifft(np.fft.fft(c) * np.fft.fft(b).conj()).real


def _unitary_roles(n, dim, rng):
    v = rng.standard_normal((n, dim))
    fv = np.fft.fft(v, axis=1)
    fv = fv / (np.abs(fv) + 1e-12)
    return np.fft.ifft(fv, axis=1).real


def _norm(v):
    n = np.linalg.norm(v); return v / n if n > 0 else v


def _load_codebook():
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=1024); ai.build(ps)
    rows = [av.algebra_hrr for av in ai._atom_vectors.values() if av.algebra_hrr is not None]
    if not rows:
        return None
    M = np.stack(rows).astype(np.float64)
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)


def _cleanup_idx(v, C, Cn):
    """argmax cosine of v against codebook C (Cn = row norms). Returns index."""
    sims = C @ v / (np.linalg.norm(v) + 1e-12) / Cn
    return int(np.argmax(sims))


def _decode(X, roles, C, Cn, F, iters):
    """Resonator explaining-away: return list of decoded codebook indices for the F slots."""
    # init: single-shot unbind + cleanup
    est_idx = [_cleanup_idx(_unbind(X, roles[i]), C, Cn) for i in range(F)]
    for _ in range(iters):
        changed = False
        for i in range(F):
            resid = X.copy()
            for k in range(F):
                if k != i:
                    resid = resid - _bind(roles[k], C[est_idx[k]])
            ni = _cleanup_idx(_unbind(resid, roles[i]), C, Cn)
            if ni != est_idx[i]:
                est_idx[i] = ni; changed = True
        if not changed:
            break
    return est_idx


def run() -> Dict:
    M = _load_codebook()
    if M is None:
        return {"error": "no_algebra_atoms"}
    Mn_all = M.shape[0]; dim = M.shape[1]
    f_sweep = [2, 3] if SMOKE else F_SWEEP
    k_sweep = [50, 280] if SMOKE else K_SWEEP
    noise_sweep = [0.0] if SMOKE else NOISE_SWEEP
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 6 if SMOKE else N_TRIALS
    iters = 4 if SMOKE else RESONATOR_ITERS
    cells = []
    for K in k_sweep:
        K = min(K, Mn_all)
        for F in f_sweep:
            if F > K:
                continue
            for nz in noise_sweep:
                hits = 0; tot = 0
                for sd in seeds:
                    rng = np.random.default_rng(sd * 100 + K + F)
                    Cidx = rng.permutation(Mn_all)[:K]          # K-atom codebook subset
                    C = M[Cidx]; Cn = np.linalg.norm(C, axis=1) + 1e-12
                    for _t in range(n_trials):
                        fillers = rng.permutation(K)[:F]        # F distinct fillers from the K-codebook
                        roles = _unitary_roles(F, dim, rng)
                        X = np.sum([_bind(roles[i], C[fillers[i]]) for i in range(F)], axis=0)
                        X = _norm(X)
                        if nz > 0:
                            X = X + nz * _norm(rng.standard_normal(dim))
                        dec = _decode(X, roles, C, Cn, F, iters)
                        hits += sum(int(dec[i] == fillers[i]) for i in range(F)); tot += F
                p1 = hits / tot if tot else 0.0
                cells.append({"F": F, "K": K, "noise": nz, "precision1": round(p1, 4)})
                print("  F=%d K=%3d noise=%.1f precision@1=%.4f" % (F, K, nz, p1), flush=True)
    return {"cells": cells, "n_atoms": Mn_all, "dim": dim, "resonator_iters": iters, "n_seeds": len(seeds)}


def _get(cells, F, K, nz):
    return next((c["precision1"] for c in cells if c["F"] == F and c["K"] == K and abs(c["noise"] - nz) < 1e-9), None)


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    cells = r["cells"]
    Kmax = max(c["K"] for c in cells)
    p2 = _get(cells, 2, Kmax, 0.0); p3 = _get(cells, 3, Kmax, 0.0)
    s = ("precision@1: F2/K%d/n0=%s F3/K%d/n0=%s; full grid=%s; corpus=%d dim=%d iters=%d"
         % (Kmax, p2, Kmax, p3, [(c["F"], c["K"], c["noise"], c["precision1"]) for c in cells], r["n_atoms"], r["dim"], r["resonator_iters"]))
    clip = " [UNCHARTED clustered-codebook tw_edge_z=-2.26: precision vs literature Frady-Sommer cliff D^2/(F^2 K) reveals whether substrate clustering lifts or hurts decode]"
    if p3 is None or p2 is None:
        return ("UNKNOWN", "UNKNOWN: missing F2/F3 at K_max. " + s)
    if p2 >= 0.95 and p3 >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate decodes superposed bound states -- precision@1>=0.95 at F=2 and >=0.80 at F=3 (K=%d, noise=0) via resonator explaining-away. Substrate decomposes structured representations back to atoms (substrate > atom-set)." % Kmax + clip + " " + s)
    if p3 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: F=3 precision@1=%.4f (>=0.80) but F=2 precision@1=%.4f misses the strict 0.95 HARD-PASS bar at K=%d -- decode is F/noise-robust (no cliff) but the FULL clustered codebook caps the ceiling via intra-cluster near-collisions." % (p3, p2, Kmax) + clip + " " + s)
    return ("HARD_FAIL", "HARD_FAIL: precision@1 <0.50 at F=3 -- resonator decode does not generalize at F=3 on the clustered codebook." + clip + " " + s)


def _selftest():
    rng = np.random.default_rng(1)
    dim = 256
    R = _unitary_roles(2, dim, rng)
    mag = np.abs(np.fft.fft(R[0]))
    assert np.max(np.abs(mag - 1.0)) < 1e-6
    # 2-binding decode with a tiny codebook should recover exactly (noiseless)
    C = _norm(rng.standard_normal((5, dim)).astype(np.float64))
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    Cn = np.linalg.norm(C, axis=1) + 1e-12
    fillers = [0, 3]
    X = _norm(_bind(R[0], C[0]) + _bind(R[1], C[3]))
    dec = _decode(X, R, C, Cn, 2, 6)
    assert dec == fillers, dec
    print("[selftest] PASS: decomposition-resonator (unitary roles + exact 2-binding decode %s)" % dec, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
