"""ANALYTIC DEMONSTRATION of the fidelity audit's core claim, independent of any corpus, any
dataset and any of our code paths: `sign()` applied to `shared + distinctive` is a PROTOTYPE
OPERATOR that ANNIHILATES the distinctive component.

Setup: two near-neighbours (goat / sheep) share a category component S and differ only in a small
distinctive component D_1 vs D_2, with |D| / |S| = ratio. Measures, over 4000 random trials at
d=256 (the substrate's live context dimensionality):
  - cos(a_1, a_2) under sign() vs graded -- how confusable the pair is;
  - the fraction of trials in which the two sign codes are BIT-IDENTICAL, i.e. the pair has become
    literally indistinguishable;
  - D-recovery: cos(a_1 - a_2, D_1 - D_2) -- how much of the true distinctive difference survives
    the code. Graded is 1.0 by construction; sign() is the measurement of interest.

Cited by notes/comparator_component_fidelity_audit_2026-08-13.md.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json

import numpy as np

D_DIM = 256
N_TRIALS = 4000
RATIOS = (0.02, 0.05, 0.10, 0.20, 0.40, 0.80)
SEED = 7


def _cos(x, y):
    nx, ny = float(np.linalg.norm(x)), float(np.linalg.norm(y))
    if nx < 1e-12 or ny < 1e-12:
        return None
    return float(x @ y / (nx * ny))


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for ratio in RATIOS:
        cs_s = cs_g = 0.0
        rec_s, n_rec = 0.0, 0
        n_identical = 0
        for _ in range(N_TRIALS):
            S = rng.normal(size=D_DIM) * 3.0
            D1 = rng.normal(size=D_DIM) * 3.0 * ratio
            D2 = rng.normal(size=D_DIM) * 3.0 * ratio
            a1g, a2g = S + D1, S + D2
            a1s, a2s = np.sign(a1g), np.sign(a2g)
            cs_s += _cos(a1s, a2s)
            cs_g += _cos(a1g, a2g)
            if np.array_equal(a1s, a2s):
                n_identical += 1
            else:
                r = _cos(a1s - a2s, D1 - D2)
                if r is not None:
                    rec_s += r
                    n_rec += 1
        rows.append({
            "distinctive_to_shared_ratio": ratio,
            "cos_pair_SIGN": round(cs_s / N_TRIALS, 4),
            "cos_pair_GRADED": round(cs_g / N_TRIALS, 4),
            "frac_pairs_BIT_IDENTICAL_under_sign": round(n_identical / N_TRIALS, 4),
            "D_recovery_SIGN": round(rec_s / max(n_rec, 1), 4),
            "D_recovery_GRADED": 1.0})
    print("%-8s %-14s %-16s %-26s %-16s %s"
          % ("ratio", "cos_pair_SIGN", "cos_pair_GRADED", "frac_BIT_IDENTICAL_sign",
             "D_recov_SIGN", "D_recov_GRADED"))
    for r in rows:
        print("%-8.2f %-14.4f %-16.4f %-26.4f %-16.4f %.1f"
              % (r["distinctive_to_shared_ratio"], r["cos_pair_SIGN"], r["cos_pair_GRADED"],
                 r["frac_pairs_BIT_IDENTICAL_under_sign"], r["D_recovery_SIGN"],
                 r["D_recovery_GRADED"]))
    print(json.dumps({"d": D_DIM, "n_trials": N_TRIALS, "seed": SEED, "rows": rows}))


if __name__ == "__main__":
    main()
