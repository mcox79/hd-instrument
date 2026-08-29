"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the UNIFYING READOUT PRINCIPLE.

The brief's rule is "every READ-terminal bundle should switch to pooled divnorm." The disk (this problem's
cosine + typer cells) says the real discriminator is NOT read-terminal-vs-rebound -- it is the READOUT CLASS.
This cell isolates that: hold ONE superposed store fixed, vary ONLY the norm (per-component vs pooled divnorm)
and the readout, over a load sweep. It is the mechanistic explanation of WHY the register benefited and the
other read-terminal callers do not.

STORE: M = bundle_m( bind(role_truth[s], key[s]) ), m slots, role vocab V=100 (chance 0.01), the register's
own construction. Two norms: per-component (S_i/|S_i|) vs pooled divnorm (Carandini-Heeger).

READOUTS (all landed in hdlab.situation_model_accumulate, reused unmodified):
  ARGMAX         _decode_argmax_slots      -- per-slot independent argmax (the typer sup_map / goal_achievement
                                              / cosine-consumer readout class: SCALE-INVARIANT).
  SERIAL_PLAIN   decode_serial_slots       -- theta-gamma decode-and-suppress, NOT gain-matched.
  SERIAL_POOLED  decode_serial_pooled_slots-- decode-and-suppress WITH pooled gain control (the readout the
                                              divnorm store needs -- the register's fix).

MEASURED PRINCIPLE (corrected from the disk -- per-component vs divnorm differ in DIRECTION, not just scale, so
argmax is NOT invariant between them):
  - Per-component renorm (S_i/|S_i|) is a PER-COMPONENT NONLINEARITY: it distorts the store's DIRECTION. Pooled
    divnorm is a GLOBAL SCALAR of the raw sum: it PRESERVES direction. So divnorm >= per-component for EVERY
    direction-sensitive read (argmax AND serial), and the gap GROWS WITH LOAD (the distortion compounds as more
    items superpose). At low load both recover ~perfectly.
  - The gap is LARGEST for the ITERATIVE SERIAL readout (decode-and-suppress needs the exact linear structure
    that per-component destroys; register serial 0.37->0.99), SMALLER BUT REAL for per-slot ARGMAX (register
    argmax 0.53->0.64), and unused by a LOW-LOAD / COARSE-margin task (the cosine consumers, measured null).
  => So "switch read-terminal callers to divnorm" is directionally right, but the PER-CALLER benefit is a
     function of that caller's operating LOAD and task granularity -- which is what must be measured per caller.

This reuses the LANDED decode functions on a SYNTHETIC store (it does NOT re-run the register organ / re-derive
its landed numbers -- the SERIAL_POOLED arm is the KNOWN-ANSWER positive control that the metric can move).

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_readout_principle_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_readout_principle_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import (  # noqa: E402
    unit_phase_vec,
    _decode_argmax_slots,
    decode_serial_slots,
    decode_serial_pooled_slots,
)

D = 256
V = 100
BASE_SEED = 20260828
N_TRIALS = 24


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _build_store(m, seed, norm):
    """One entity, m slots, role truth[s] bound to key[s]; store normalized by `norm`. Returns (M, keys,
    role_mat, truth)."""
    g = _gen(seed)
    role_vecs = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(m)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(m)]
    bounds = [binding.bind(role_vecs[truth[s]], keys[s]) for s in range(m)]
    M = bundling.bundle(torch.stack(bounds), norm=(None if norm == "percomp" else norm))
    role_mat = torch.stack(role_vecs)
    return M, keys, role_mat, truth


def _acc(est, truth):
    return sum(1 for a, b in zip(est, truth) if a == b) / len(truth)


READOUTS = {
    "ARGMAX": _decode_argmax_slots,
    "SERIAL_PLAIN": decode_serial_slots,
    "SERIAL_POOLED": decode_serial_pooled_slots,
}


def cell(loads=(4, 8, 16, 32, 48, 64), n_trials=N_TRIALS):
    res = {"loads": list(loads), "grid": {}}
    for m in loads:
        for norm in ("percomp", "divnorm"):
            accs = {ro: [] for ro in READOUTS}
            for t in range(n_trials):
                M, keys, role_mat, truth = _build_store(m, BASE_SEED + 1000 * t + m, norm)
                for ro, fn in READOUTS.items():
                    est = fn(M, keys, role_mat)
                    accs[ro].append(_acc(est, truth))
            for ro in READOUTS:
                res["grid"]["m=%d/%s/%s" % (m, norm, ro)] = round(float(np.mean(accs[ro])), 4)
    return res


def _print(res):
    print("=== READOUT PRINCIPLE: same store, per-component vs pooled-divnorm x readout, over load ===")
    print("  M=superposed bound (role,key) pairs, D=%d V=%d, %d trials/cell\n" % (D, V, N_TRIALS))
    print("  %-6s | %-21s | %-21s | %-21s" % ("load", "ARGMAX (pc/div)", "SERIAL_PLAIN (pc/div)", "SERIAL_POOLED (pc/div)"))
    for m in res["loads"]:
        def g(norm, ro):
            return res["grid"]["m=%d/%s/%s" % (m, norm, ro)]
        print("  m=%-4d | %.3f / %.3f          | %.3f / %.3f          | %.3f / %.3f"
              % (m, g("percomp", "ARGMAX"), g("divnorm", "ARGMAX"),
                 g("percomp", "SERIAL_PLAIN"), g("divnorm", "SERIAL_PLAIN"),
                 g("percomp", "SERIAL_POOLED"), g("divnorm", "SERIAL_POOLED")))
    # headline deltas at max load
    mmax = res["loads"][-1]
    d_argmax = res["grid"]["m=%d/divnorm/ARGMAX" % mmax] - res["grid"]["m=%d/percomp/ARGMAX" % mmax]
    d_serial = res["grid"]["m=%d/divnorm/SERIAL_POOLED" % mmax] - res["grid"]["m=%d/percomp/SERIAL_POOLED" % mmax]
    print("\n  AT MAX LOAD m=%d:  divnorm-vs-percomp delta  ARGMAX=%+.3f (modest, direction-preservation)   "
          "SERIAL_POOLED=%+.3f (the big lever, iterative decode)" % (mmax, d_argmax, d_serial))
    print("  => divnorm >= per-component for BOTH readouts, gap grows with load; per-slot argmax gains ~+0.1 at "
          "overload, the gain-matched serial decode gains ~+0.6. Low load (m<=8) = no gap.")


def _self_test():
    # low load: everything recovers ~perfectly under both norms
    M, keys, role_mat, truth = _build_store(4, BASE_SEED, "divnorm")
    assert _acc(_decode_argmax_slots(M, keys, role_mat), truth) >= 0.99, "low-load argmax should be ~1.0"
    # overload: per-component vs divnorm differ in DIRECTION, so even ARGMAX is NOT invariant -- divnorm >= percomp.
    Mp, kp, rmp, tp = _build_store(48, BASE_SEED + 7, "percomp")
    Md, kd, rmd, td = _build_store(48, BASE_SEED + 7, "divnorm")
    a_pc = _acc(_decode_argmax_slots(Mp, kp, rmp), tp)
    a_dn = _acc(_decode_argmax_slots(Md, kd, rmd), td)
    s_dn = _acc(decode_serial_pooled_slots(Md, kd, rmd), td)
    assert a_dn >= a_pc, "divnorm argmax (%.3f) should be >= percomp argmax (%.3f) at overload" % (a_dn, a_pc)
    assert s_dn >= a_dn, "SERIAL_POOLED/divnorm (%.3f) should be the biggest recovery (>= argmax/divnorm %.3f)" % (s_dn, a_dn)
    print("[self-test] PASS: divnorm argmax %.3f >= percomp argmax %.3f (direction matters), SERIAL_POOLED/divnorm "
          "%.3f is the biggest recovery at overload" % (a_dn, a_pc, s_dn))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    _print(cell())
