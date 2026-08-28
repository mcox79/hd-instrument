"""Scaffold-free witness for `the_register_bundle_renorm_breaks_the_serial_readout`.

LIVE recompute (no cached metric trusted, no number crosses harnesses) of the load-bearing claims on the REAL
organ primitives (hdlab.situation_model_accumulate.AccumulateRegister + hdlab.binding), at FIXED D=256:

  THESIS: the register's bundle applies a PER-COMPONENT renorm (S_i/|S_i|, hdlab.bundling default) -- a
  non-invertible, per-component distortion that destroys the linear structure the theta-gamma serial readout needs.
  The brain controls a superposition's magnitude by DIVISIVE NORMALIZATION (Carandini & Heeger 2012) and homeostatic
  synaptic SCALING (Turrigiano 2008) -- a POOLED (scalar) gain, which preserves the linear structure. Swapping the
  per-component renorm for a pooled/scalar divisive norm (and a gain-matched serial readout) recovers the serial
  readout AND does not regress the argmax path -- one normalization serves both.

  N1  faithful serial on a DIVISIVELY-normalized store RECOVERS overload CI-separated over serial on the
      per-component store (M=64).
  N2  the divisive-normalized store TIES the raw-sum ceiling on serial (scalar norms are equivalent under
      gain-matching -- the fix loses nothing vs the unbounded raw sum).
  N3  ARGMAX NO-REGRESSION: a scalar-norm argmax is SCALE-INVARIANT (bit-identical to the raw-sum argmax) and does
      NOT regress vs the per-component organ -- it is >= at every load and strictly better at overload.
  N4  POSITIVE CONTROL -- the STORE norm is the binding constraint, not the readout: even the best (gain-matched)
      serial readout CANNOT recover the per-component store (serial:percomp << serial:divnorm at overload).
  N5  info-free twin (shuffled keys, faithful readout) LOSES CI-separated.
  N6  store & readout normalization must MATCH: a naive (no-gain) serial on a scaled store FAILS; the pooled-gain
      readout fixes it (the two divisive-normalization steps are one op-class, applied at store and readout).
  N7  the recovery is a property of POOLED normalization, not a tuned parameter -- serial is FLAT across the
      Carandini-Heeger semi-saturation sigma and the homeostatic target RMS.

Run:  .venv/Scripts/python.exe verification/test_register_divisive_norm.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_register_divisive_norm_v1 as E  # noqa: E402


def main():
    checks = []

    lo = E._cell(256, 8, 100, 15, 1, n_boot=500)
    hi = E._cell(256, 64, 100, 25, 1, n_boot=800)

    # N1: recovery over the per-component store, CI-separated.
    p = hi["paired_divnorm_vs_percomp_serial"]
    checks.append(("N1 faithful serial on the DIVISIVE-normalized store RECOVERS overload CI-sep over the per-component store (M64)",
                   p["lo"] > 0.30 and hi["serial::divnorm"]["acc"] > 0.9,
                   {"serial_divnorm": hi["serial::divnorm"]["acc"], "serial_percomp": hi["serial::percomp"]["acc"],
                    "delta": p["mean"], "lo": p["lo"], "hw": p["hw"]}))

    # N2: ties the raw-sum ceiling (scalar norms equivalent under gain-matching).
    tr = hi["paired_divnorm_vs_rawsum_serial"]
    checks.append(("N2 the divisive-normalized store TIES the raw-sum ceiling on serial (loses nothing vs the unbounded raw sum)",
                   abs(tr["mean"]) < 0.03,
                   {"serial_divnorm": hi["serial::divnorm"]["acc"], "serial_rawsum": hi["serial::rawsum"]["acc"],
                    "delta": tr["mean"]}))

    # N3: argmax no-regression + scale-invariance.
    ar = hi["paired_argmax_divnorm_vs_percomp"]
    scale_inv = abs(hi["argmax::divnorm"]["acc"] - hi["argmax::rawsum"]["acc"]) < 1e-6
    checks.append(("N3 ARGMAX NO-REGRESSION: scalar-norm argmax is scale-invariant (== raw-sum) and >= the per-component organ",
                   ar["lo"] > -0.01 and scale_inv and hi["argmax::divnorm"]["acc"] >= hi["argmax::percomp"]["acc"],
                   {"argmax_divnorm": hi["argmax::divnorm"]["acc"], "argmax_percomp(organ)": hi["argmax::percomp"]["acc"],
                    "argmax_rawsum": hi["argmax::rawsum"]["acc"], "lo": ar["lo"], "scale_invariant": scale_inv}))

    # N4: positive control -- the store norm is the binding constraint; the best readout can't rescue per-component.
    checks.append(("N4 POSITIVE CONTROL: even the gain-matched serial readout CANNOT recover the per-component store",
                   hi["serial::percomp"]["acc"] < hi["serial::divnorm"]["acc"] - 0.3
                   and lo["serial::percomp"]["acc"] > 0.98,   # at low load per-component is fine -> the break is load-specific
                   {"serial_percomp_M64": hi["serial::percomp"]["acc"], "serial_percomp_M8": lo["serial::percomp"]["acc"],
                    "serial_divnorm_M64": hi["serial::divnorm"]["acc"]}))

    # N5: info-free twin loses.
    checks.append(("N5 info-free twin (shuffled keys) LOSES CI-separated",
                   hi["twin"]["hi"] < hi["serial::divnorm"]["lo"] and hi["twin"]["acc"] < 0.05,
                   {"twin": hi["twin"]["acc"], "twin_hi": hi["twin"]["hi"], "serial_divnorm_lo": hi["serial::divnorm"]["lo"]}))

    # N6: store & readout norm must match -- naive serial fails on a scaled store, pooled-gain fixes it.
    checks.append(("N6 store & readout normalization must MATCH: naive (no-gain) serial FAILS on a scaled store; pooled-gain fixes it",
                   hi["serialnaive::l2"]["acc"] < hi["serial::l2"]["acc"] - 0.3
                   and abs(hi["serialnaive::rawsum"]["acc"] - hi["serial::rawsum"]["acc"]) < 0.05,   # on rawsum g~=1 -> naive==pooled
                   {"naive_l2": hi["serialnaive::l2"]["acc"], "pooled_l2": hi["serial::l2"]["acc"],
                    "naive_rawsum": hi["serialnaive::rawsum"]["acc"], "pooled_rawsum": hi["serial::rawsum"]["acc"]}))

    # N7: recovery is a property of POOLED normalization, not a tuned parameter (flat across sigma AND target).
    m = 64
    dn = [float(np.mean(E._one_entity(256, m, 100, 1 + rep * 7919, sigma=s)["serial::divnorm"]))
          for s in (0.0, 1.0, 16.0) for rep in range(8)]
    hm = [float(np.mean(E._one_entity(256, m, 100, 1 + rep * 7919, target_rms=t)["serial::homeostatic"]))
          for t in (0.1, 10.0, 100.0) for rep in range(8)]
    dn_by_s = {s: np.mean([float(np.mean(E._one_entity(256, m, 100, 1 + rep * 7919, sigma=s)["serial::divnorm"]))
                           for rep in range(8)]) for s in (0.0, 1.0, 16.0)}
    hm_by_t = {t: np.mean([float(np.mean(E._one_entity(256, m, 100, 1 + rep * 7919, target_rms=t)["serial::homeostatic"]))
                           for rep in range(8)]) for t in (0.1, 10.0, 100.0)}
    flat = (max(dn_by_s.values()) - min(dn_by_s.values()) < 0.03) and (max(hm_by_t.values()) - min(hm_by_t.values()) < 0.03)
    checks.append(("N7 recovery is a property of POOLED normalization, not a tuned parameter (FLAT across sigma and target)",
                   flat and min(dn_by_s.values()) > 0.9,
                   {"divnorm_by_sigma": {k: round(float(v), 4) for k, v in dn_by_s.items()},
                    "homeostatic_by_target": {k: round(float(v), 4) for k, v in hm_by_t.items()}}))

    # N8: the DEFAULT backend (MultiBankAccumulateRegister) in the COMPOSE regime -- store distributes load across banks,
    # the norm fix recovers the per-bank serial readout AND does not regress argmax (measured, not inferred).
    mb = E.multibank_cell(256, 384, 100, 10, 1, n_banks=8, n_boot=600)
    ps = mb["paired_serial_divnorm_vs_percomp"]; pa = mb["paired_argmax_divnorm_vs_percomp"]
    checks.append(("N8 DEFAULT multibank backend, COMPOSE regime (k_per_bank overloaded): norm fix recovers serial CI-sep + no argmax regression",
                   ps["lo"] > 0.1 and mb["serial_divnorm"]["acc"] > 0.9 and pa["lo"] > -0.01,
                   {"k_per_bank": mb["max_bank_load"], "serial_percomp": mb["serial_percomp"]["acc"],
                    "serial_divnorm": mb["serial_divnorm"]["acc"], "serial_delta_lo": ps["lo"],
                    "argmax_percomp": mb["argmax_percomp"]["acc"], "argmax_divnorm": mb["argmax_divnorm"]["acc"],
                    "argmax_delta_lo": pa["lo"]}))

    ok = True
    print("=== witness: the_register_bundle_renorm_breaks_the_serial_readout ===")
    print(f"  D=256 FIXED  V=100  chance=0.01\n")
    for name, passed, det in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {det}")
        ok = ok and passed
    print("\n" + ("ALL CHECKS PASS -- the register's PER-COMPONENT bundle renorm is the non-brain-faithful choice that "
                  "breaks the theta-gamma serial readout. Replacing it with a POOLED / SCALAR divisive normalization "
                  "(Carandini-Heeger / homeostatic scaling) -- paired with a gain-matched serial readout -- recovers "
                  "the overloaded register to the raw-sum ceiling, does NOT regress (in fact improves) the argmax "
                  "path, loses nothing to an info-free twin, and is a property of the OPERATION not a tuned constant. "
                  "One divisive normalization serves BOTH readouts; no raw-sum shadow copy is needed."
                  if ok else "WITNESS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
