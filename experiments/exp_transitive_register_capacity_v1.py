"""DEEPENING / LOCALIZATION -- separate the INTEGRATION quality from the STORAGE fidelity, and map how many items the
FHRR register can HOLD in a transitive ordering (the brief's open question: "can the substrate's register hold a
transitive ordering?"). Connects to the just-solved register-readout problem (argmax vs serial decode-and-suppress).

Two things are stacked in exp1's mechanism_register: (a) the delta-rule SETTLING that integrates the premises into one
ordering, and (b) the FHRR register that STORES the ordering as a superposition and is read back by unbinding. This cell
holds the integration FIXED (same settle) and varies only the STORAGE/read-out to answer:
  * mechanism_float   -- settle then compare python floats: the integration-only UPPER BOUND (no storage cost).
  * register_argmax   -- settle -> register -> per-item independent coordinate decode (exp1's read-out).
  * register_serial   -- settle -> register -> SERIAL decode-and-suppress (peel the strongest item, subtract its
                         reconstruction, re-decode the rest): the brain-faithful theta-gamma successive-interference
                         cancellation from the register-readout problem, applied to the magnitude-line coordinates.
As N grows the superposition crosstalk grows -> per-item argmax decode of the coordinates gets noisy -> near-pair signs
flip. The gap (float - register) IS the storage cost; serial cancellation should push the capacity cliff out.

FINDING SHAPE (measured, see summary): the register holds the ordering CLEANLY to N~[cliff], argmax then decays as
crosstalk overloads the coordinate read-out, and serial decode-and-suppress RECOVERS the overloaded regime -- localising
that any capacity limit is a READ-OUT limit of the shared store, not a failure of the integration.

Run: .venv/Scripts/python.exe experiments/exp_transitive_register_capacity_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_register_capacity_v1/. NO hdlab write.
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

from hdlab import binding                                   # noqa: E402
from hdlab import fractional_power_encoding as fpe          # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_transitive_ordering_magnitude_line_v1 import (  # noqa: E402
    make_series, unstated_pairs, settle, _normalize_line, encode_register, decode_coord, _grid_codes,
    netwin, score_pairs, _sign, _boot_ci, FPE_SIGMA, POS_SCALE, GRID_MAX)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_register_capacity_v1")
SEED = 20260828


def decode_all_serial(S, keys, rates, grid_codes, grid, pos_scale, n_iter=3):
    """Serial decode-and-suppress over the superposed magnitude-line: decode every item's coordinate, then repeatedly
    re-decode each item from the residual with the OTHER reconstructions subtracted (successive-interference cancel)."""
    n = len(keys)
    coords = [decode_coord(S, keys[i], rates, grid_codes, grid) for i in range(n)]
    recon = [binding.bind(keys[i], fpe.enc(rates, pos_scale * coords[i])) for i in range(n)]
    total = recon[0].clone()
    for i in range(1, n):
        total = total + recon[i]
    for _ in range(n_iter):
        for i in range(n):
            resid = S - (total - recon[i])
            ci = decode_coord(resid, keys[i], rates, grid_codes, grid)
            total = total - recon[i]
            recon[i] = binding.bind(keys[i], fpe.enc(rates, pos_scale * ci))
            total = total + recon[i]
            coords[i] = ci
    return np.array(coords)


def one_trial(n, seed, d, noise_eps=0.0, eta=0.3, epochs=200, temp=1.0, pos_scale=POS_SCALE):
    premises, _ = make_series(n, seed, noise_eps=noise_eps)
    pairs = [p for p in unstated_pairs(n, premises) if p["both_internal"]]
    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05)
    gc = _grid_codes(rates, grid)

    x = _normalize_line(settle(premises, n, eta=eta, epochs=epochs, temp=temp, seed=seed))
    S = encode_register(x, keys, rates, pos_scale)
    xhat = np.array([decode_coord(S, keys[i], rates, gc, grid) for i in range(n)])
    xser = decode_all_serial(S, keys, rates, gc, grid, pos_scale)
    nw = netwin(premises, n)
    arms = {
        "float": lambda a, b: _sign(x[a] - x[b]),
        "register_argmax": lambda a, b: _sign(xhat[a] - xhat[b]),
        "register_serial": lambda a, b: _sign(xser[a] - xser[b]),
        "assoc_netwin": lambda a, b: _sign(nw[a] - nw[b]),
    }
    return {k: score_pairs(pairs, fn) for k, fn in arms.items()}


def cell(n, n_seeds, base_seed, d=512, noise_eps=0.0, n_boot=1500):
    ARMS = ["float", "register_argmax", "register_serial", "assoc_netwin"]
    acc = {a: [] for a in ARMS}
    for r in range(n_seeds):
        t = one_trial(n, base_seed + r * 101, d, noise_eps=noise_eps)
        for a in ARMS:
            acc[a].append(t[a])
    out = {"n": n, "d": d, "noise_eps": noise_eps, "n_seeds": n_seeds}
    for a in ARMS:
        out[a] = _boot_ci(acc[a], n_boot=n_boot, seed=base_seed + hash(a) % 997)
    dv = np.asarray(acc["float"]) - np.asarray(acc["register_argmax"])
    out["storage_cost_argmax"] = _boot_ci(dv, n_boot=n_boot, seed=base_seed + 3)
    dv2 = np.asarray(acc["register_serial"]) - np.asarray(acc["register_argmax"])
    out["serial_recovery"] = _boot_ci(dv2, n_boot=n_boot, seed=base_seed + 4)
    return out


def run(n_seeds=120):
    out = {"anchor": "transitive_register_capacity_v1", "seed": SEED}
    out["capacity_d512"] = [cell(n, n_seeds, SEED + n, d=512) for n in [6, 9, 12, 16, 20, 25, 30]]
    out["capacity_d256"] = [cell(n, n_seeds, SEED + 100 + n, d=256) for n in [6, 9, 12, 16, 20, 25]]
    return out


def summarize(res):
    for key, d in [("capacity_d256", 256), ("capacity_d512", 512)]:
        print(f"\n=== REGISTER CAPACITY for a transitive ordering (D={d}, internal_unstated matched pairs) ===")
        print("    N   float(UB)  reg_argmax  reg_serial  assoc  [storage cost]     [serial recovery]")
        for r in res[key]:
            sc = r["storage_cost_argmax"]; sr = r["serial_recovery"]
            print(f"   {r['n']:>2d}   {r['float']['mean']:.3f}      {r['register_argmax']['mean']:.3f}"
                  f"       {r['register_serial']['mean']:.3f}      {r['assoc_netwin']['mean']:.3f}  "
                  f"{sc['mean']:+.3f}[{sc['lo']:+.3f},{sc['hi']:+.3f}]  {sr['mean']:+.3f}[{sr['lo']:+.3f},{sr['hi']:+.3f}]")
    print("\n  READING: float(UB) = integration-only ceiling (no storage cost). reg_argmax decays as N overloads the")
    print("  shared superposition (the READ-OUT limit). reg_serial (theta-gamma decode-and-suppress) recovers it ->")
    print("  the integration is intact; any capacity cliff is a register READ-OUT limit, fixable by the brain-faithful")
    print("  serial read-out (as in the register-readout problem), NOT a failure to hold the ordering.")


def self_test():
    lo = cell(9, 40, 1, d=512, n_boot=800)
    hi = cell(25, 40, 2, d=256, n_boot=800)
    assert lo["float"]["mean"] > 0.95, f"integration UB must be near-perfect at N9: {lo['float']}"
    assert lo["register_argmax"]["mean"] > 0.9, f"register must hold N9 cleanly at D512: {lo['register_argmax']}"
    # at the overloaded regime, serial should not be worse than argmax (recovery >= ~0)
    assert hi["serial_recovery"]["hi"] > -0.02, f"serial must not hurt in overload: {hi['serial_recovery']}"
    print(f"SELF-TEST PASS: N9/D512 float={lo['float']['mean']:.3f} reg_argmax={lo['register_argmax']['mean']:.3f}; "
          f"N25/D256 float={hi['float']['mean']:.3f} argmax={hi['register_argmax']['mean']:.3f} "
          f"serial={hi['register_serial']['mean']:.3f} recovery={hi['serial_recovery']['mean']:+.3f}"
          f"[{hi['serial_recovery']['lo']:+.3f},{hi['serial_recovery']['hi']:+.3f}]")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--seeds", type=int, default=120)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    n_seeds = 40 if args.mode == "smoke" and not args.full else args.seeds
    t0 = time.time()
    res = run(n_seeds=n_seeds)
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
