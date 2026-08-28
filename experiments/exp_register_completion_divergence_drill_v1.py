"""DEEPENING / WALL DRILL -- is the serial read-out's divergence at extreme overload (M>=96 at D=256) a TRUE
capacity bound, or a limitation of HARD-COMMIT decoding that a more brain-faithful GRADED/STOCHASTIC
resonator pushes past? (owner: "if the brain can do it, so can we -- drill the wall").

exp_register_completion_readout_v1 found serial recovers M in [16,64] at D=256 then DIVERGES (M>=96): the
hard per-slot argmax init is <40% correct, hard-commit SIC subtracts WRONG reconstructions, and the iteration
locks into a spurious fixed point. The brain does NOT read with hard per-item commits -- it uses graded
population codes and stochastic (noisy) settling, and resonator networks (Frady/Kent 2020) keep GRADED factor
estimates (a superposition of candidates), committing only at the end. Two faithful upgrades to test:
  * GRADED resonator: keep a soft (softmax-weighted) blend per slot instead of a hard argmax each iteration,
    so low-confidence slots contribute LESS corruption to the residual (no premature lock-in).
  * STOCHASTIC RESTARTS: run from R noisy inits and keep the estimate with the lowest reconstruction residual
    (the CA1-comparator certifier from exp3) -- escapes a single spurious basin.

ARMS at D=256 FIXED, sweeping M across and past the divergence: argmax, serial (hard), resonator_graded,
resonator_graded+restarts. HONEST outcome either way:
  * if graded/restarts recover M>=96 -> the wall was a READ-OUT limitation, drilled (brain-faithful graded
    resonance does it, so can we).
  * if they plateau at the SAME M as hard serial -> it is a TRUE capacity bound at this D (info-theoretic SNR
    floor), which the brain also has and handles with the STORE (exp2), not the read-out. State the reason.

Run: .venv/Scripts/python.exe experiments/exp_register_completion_divergence_drill_v1.py [--self-test|--full]
ASCII only. Writes ONLY to data/exp_register_completion_divergence_drill_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_register_completion_readout_v1 import decode_argmax, decode_serial, _gen, _scores  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_completion_divergence_drill_v1")
SEED = 20260828
D = 256
V = 100


def _soft_cleanup(v, role_mat, temp):
    """Graded cleanup: softmax-weighted blend toward the codebook (a superposition of candidate codewords),
    renormalised to a unit-modulus phasor. temp -> inf recovers hard argmax (a single codeword)."""
    w = torch.softmax(temp * _scores(v, role_mat), dim=0).to(role_mat.dtype)
    y = w @ role_mat
    return y / y.abs().clamp_min(1e-12).to(y.dtype)


def decode_resonator_graded(S, keys, role_mat, n_iter=12, temp=6.0, x0=None):
    """Frady-style GRADED resonator over per-slot keys: keep a soft blend per slot; commit (argmax) only at
    the end. Optional x0 = list of init estimates (for restarts)."""
    m = len(keys)
    if x0 is None:
        x = [_soft_cleanup(binding.unbind(S, keys[s]), role_mat, temp) for s in range(m)]
    else:
        x = [t.clone() for t in x0]
    recon = [binding.bind(x[s], keys[s]) for s in range(m)]
    total = recon[0].clone()
    for s in range(1, m):
        total = total + recon[s]
    for _ in range(n_iter):
        for s in range(m):
            resid = S - (total - recon[s])
            xn = _soft_cleanup(binding.unbind(resid, keys[s]), role_mat, temp)
            total = total - recon[s]
            recon[s] = binding.bind(xn, keys[s])
            total = total + recon[s]
            x[s] = xn
    return [int(torch.argmax(_scores(x[s], role_mat))) for s in range(m)]


def _residual_of(est, keys, role_mat, S):
    recon = binding.bind(role_mat[est[0]], keys[0]).clone()
    for s in range(1, len(keys)):
        recon = recon + binding.bind(role_mat[est[s]], keys[s])
    return float(torch.linalg.vector_norm(S - recon) / torch.linalg.vector_norm(S).clamp_min(1e-12))


def decode_resonator_restart(S, keys, role_mat, n_iter=12, temp=6.0, n_restart=4, seed=0):
    """Multi-restart graded resonator: run from n_restart noisy inits, keep the lowest-residual solution
    (CA1-comparator certifier). Escapes a single spurious basin."""
    m = len(keys)
    best, best_res = None, 1e9
    g = torch.Generator().manual_seed(int(seed) % (2 ** 31))
    for r in range(n_restart):
        if r == 0:
            x0 = None
        else:
            # noisy init: perturb each slot's readback with a random phasor before soft cleanup
            x0 = []
            for s in range(m):
                noise = unit_phase_vec(role_mat.shape[1], g)
                x0.append(_soft_cleanup(binding.unbind(S, keys[s]) * (0.7 + 0.3 * noise), role_mat, temp))
        est = decode_resonator_graded(S, keys, role_mat, n_iter=n_iter, temp=temp, x0=x0)
        res = _residual_of(est, keys, role_mat, S)
        if res < best_res:
            best, best_res = est, res
    return best


def _one(d, m, v, seed, temp=6.0, n_restart=4):
    g = _gen(seed)
    role_list = [unit_phase_vec(d, g) for _ in range(v)]
    role_mat = torch.stack(role_list, dim=0)
    keys = [unit_phase_vec(d, g) for _ in range(m)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    S = binding.bind(role_list[truth[0]], keys[0])
    for s in range(1, m):
        S = S + binding.bind(role_list[truth[s]], keys[s])
    arg = decode_argmax(S, keys, role_mat)
    ser = decode_serial(S, keys, role_mat, n_iter=6)
    grd = decode_resonator_graded(S, keys, role_mat, temp=temp)
    rst = decode_resonator_restart(S, keys, role_mat, temp=temp, n_restart=n_restart, seed=seed)
    acc = lambda e: float(np.mean([e[s] == truth[s] for s in range(m)]))
    return {"argmax": acc(arg), "serial": acc(ser), "graded": acc(grd), "graded_restart": acc(rst)}


def _cell(m, n_reps, seed, temp=6.0, n_restart=4):
    ARMS = ["argmax", "serial", "graded", "graded_restart"]
    acc = {a: [] for a in ARMS}
    for rep in range(n_reps):
        r = _one(D, m, V, seed + rep * 7919, temp=temp, n_restart=n_restart)
        for a in ARMS:
            acc[a].append(r[a])
    return {a: round(float(np.mean(acc[a])), 4) for a in ARMS}


def run(n_reps=30):
    m_grid = [64, 80, 96, 112, 128, 160]
    rows = [{"m": m, **_cell(m, n_reps, SEED)} for m in m_grid]
    # analytic capacity reference
    from hdlab.k_cliff_scaling import k_cliff
    return {"anchor": "register_completion_divergence_drill_v1", "d": D, "v": V, "n_reps": n_reps,
            "k_cliff": k_cliff(D), "m_grid": m_grid, "rows": rows}


def summarize(res):
    print(f"\n=== DIVERGENCE DRILL (D={res['d']} FIXED, V={res['v']}, k_cliff={res['k_cliff']}): "
          f"does a GRADED/STOCHASTIC resonator push past M>=96? ===")
    print("    M   argmax  serial(hard)  graded  graded+restart")
    for r in res["rows"]:
        print(f"  {r['m']:>4d}   {r['argmax']:.3f}     {r['serial']:.3f}       {r['graded']:.3f}     {r['graded_restart']:.3f}")
    # did graded/restart push the boundary? compare recovery at M=96,112 vs hard serial
    push = any(res["rows"][i]["graded_restart"] > res["rows"][i]["serial"] + 0.1
               for i, r in enumerate(res["rows"]) if r["m"] >= 96)
    print(f"\n  graded/restart PUSHES past hard-serial at M>=96: {push}")
    print("  READING: if pushed -> the divergence was a HARD-COMMIT read-out limitation (graded resonance is more "
          "brain-faithful and recovers more). If NOT -> it is a TRUE capacity bound at this D (SNR floor near "
          "k_cliff), which the brain also has and handles with the STORE (exp2), not a smarter read-out.")


def self_test():
    lo = _cell(64, 12, 1, n_restart=2)
    assert lo["serial"] > 0.9 and lo["graded"] > 0.9, f"in-window all recover: {lo}"
    hi = _cell(112, 12, 1, n_restart=3)   # past hard-serial's window
    print(f"SELF-TEST PASS: M64 serial={lo['serial']:.3f} graded={lo['graded']:.3f}; "
          f"M112 argmax={hi['argmax']:.3f} serial={hi['serial']:.3f} graded={hi['graded']:.3f} "
          f"graded_restart={hi['graded_restart']:.3f} (drill: does graded push past serial?)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
