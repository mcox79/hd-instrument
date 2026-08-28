"""Witness for hdlab.fractional_power_encoding (landed 2026-08-28, landing-step 1 of the p1 scalar-magnitude channel).

Self-contained construction proof of the log-Weber magnitude code (no data):
  [1] WEBER / scale-invariance: with the LOG code, fixed-RATIO pairs (x, 2x) have a SCALE-INVARIANT kernel (CV ~0
      across magnitudes) where the LINEAR code (encoding x directly) does NOT -- the log-encoding is what makes it Weber.
  [2] NATIVE COMPARATOR: unbind(log_encode(x), log_encode(ref)) == log_encode(x/ref) -- the ratio is decoded by one
      substrate unbind (cos with log_encode(x/ref) ~ 1.0), the directional Weber comparison signal.
  [3] LOG-GAUSSIAN tuning: the kernel peaks at the self coordinate and decreases monotonically with ratio distance.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab import binding  # noqa: E402
from hdlab.fractional_power_encoding import phase_rates, enc, log_encode, kern  # noqa: E402
from hdlab.lexical_similarity import _cos_complex  # noqa: E402

D = 4096
SEED = 20260827


def _cv(vals):
    v = np.asarray(vals, float)
    return float(v.std() / abs(v.mean())) if abs(v.mean()) > 1e-9 else float("inf")


def main() -> int:
    rates = phase_rates("gauss", D, SEED, sigma=1.0)
    xs = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]

    # [1] WEBER: fixed-RATIO kernel scale-invariant in the LOG code, NOT in the LINEAR code
    log_ratio = [kern(rates, math.log(x), math.log(2.0 * x)) for x in xs]     # log code, fixed ratio 2x
    lin_ratio = [kern(rates, x, 2.0 * x) for x in xs]                          # linear code, fixed ratio 2x
    cv_log, cv_lin = _cv(log_ratio), _cv(lin_ratio)
    print(f"[1] Weber: LOG fixed-ratio kernel CV={cv_log:.4f} (scale-invariant) vs LINEAR CV={cv_lin:.4f}")
    assert cv_log < 0.03, f"the LOG code's fixed-ratio kernel must be scale-invariant (CV {cv_log:.4f})"
    assert cv_lin > cv_log + 0.05, f"the LINEAR code must NOT be scale-invariant on fixed ratios (CV {cv_lin:.4f})"

    # [2] NATIVE COMPARATOR: unbind(log x, log ref) == log(x/ref)
    ok = 0
    pairs = [(64.0, 8.0), (100.0, 10.0), (27.0, 3.0), (50.0, 200.0)]
    for x, ref in pairs:
        decoded = binding.unbind(log_encode(rates, x), log_encode(rates, ref))
        target = log_encode(rates, x / ref)
        sim = float(_cos_complex(decoded, target))
        ok += int(sim > 0.99)
    print(f"[2] comparator: unbind(log x, log ref) ~= log(x/ref) on {ok}/{len(pairs)} pairs (cos>0.99)")
    assert ok == len(pairs), "the unbind comparator must decode the log-ratio (Weber comparison signal)"

    # [3] LOG-GAUSSIAN: kernel peaks at self, decreases monotonically with ratio distance
    x0 = 16.0
    ks = [kern(rates, math.log(x0), math.log(x0 * r)) for r in (1.0, 1.5, 2.0, 4.0, 8.0)]
    print(f"[3] log-Gaussian tuning (ratio 1..8x from {x0}): {[round(k,3) for k in ks]}")
    assert abs(ks[0] - 1.0) < 1e-6, "kernel must be 1.0 at the self coordinate"
    assert all(ks[i] > ks[i + 1] for i in range(len(ks) - 1)), "kernel must decrease monotonically with ratio distance"

    print("\nALL WITNESS ASSERTIONS PASSED -- FPE log-encoding gives a Weber (scale-invariant on fixed ratios) magnitude")
    print("code with log-Gaussian tuning, and its ratio comparator is a single native substrate unbind.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
