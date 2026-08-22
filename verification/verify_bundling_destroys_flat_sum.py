"""verify_bundling_destroys_flat_sum.py -- honest verification of the "adding destroys the code"
claim for problem slug `flat_store_destroys_the_code`.

PROBLEM.md quotes an UNVERIFIED relay: "Adding vectors destroys 6.93 of 7 bits of the real concept
codes, while squashing them to signs destroys ZERO; permuting the codes does not help, so it is the
GEOMETRY of the codes and not their content." The brief says: check this FIRST, and do not carry
`6.93 of 7 bits` into a write-up until reproduced.

WHAT THIS SCRIPT ESTABLISHES (two parts, both can-fail):

(A) INDEPENDENT computation with the validated ruler's own functions (imported unmodified from
    experiments/exp_encoding_quality_instrument_v2.py): summing B=8 near-ORTHOGONAL dense codes and
    recovering each in the bundle's top-B is LOSS-FREE (retains the full 7.000-bit ceiling). So
    "adding" is NOT intrinsically destructive -- destruction is a property of the code's GEOMETRY
    (correlated codes crosstalk; orthogonal ones do not), exactly as the brief's own "it is the
    GEOMETRY of the codes and not their content" phrasing says.

(B) The REAL concept codes' numbers, read from the validated ruler's landed FULL metrics
    (data/exp_meaning_lift_population_code_v1/metrics.json, ruler at 542e1fc0d, 8/10 gates passed),
    NOT re-derived:
      INC_SIMHASH@d1024   (the incumbent live code) retains 0.8744 / 7 bits through the sum
                          -> ADDING destroys 6.126 / 7 for the real incumbent code.
      C1_KCAP_GRD@d1024   (a SPARSE graded code)     retains 3.5264 / 7 bits (4.03x the incumbent).
      C4_PHASOR@d1024                                retains 0.0097 / 7 bits (dies in bundling).

CONCLUSION for the slug: the exact figure `6.93` is a PHANTOM (grepped data/ experiments/ notes/
preregs/ -- absent). The phenomenon it gestures at is real: the incumbent flat-store code loses
~6.1 of 7 bits under the sum. But the survivable-superposition FIX is CODE FORMAT (a sparse graded
code retains 4x more), a Phase-1 change -- NOT the addressed storage PROBLEM.md proposes. Addressing
does not change how many bits survive a superposition; the code's sparsity/geometry does.

Run: .venv/Scripts/python.exe verification/verify_bundling_destroys_flat_sum.py
ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_encoding_quality_instrument_v2 import (  # noqa: E402  imported UNMODIFIED
    fano_bits_list, bundle_survival, recoverability_topb, BUNDLE_B, SIGMA_GATE,
)

RULER_METRICS = os.path.join(_REPO, "data", "exp_meaning_lift_population_code_v1", "metrics.json")


def _l2n(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return (M / n).astype(np.float32)


def orthogonal_stage_bits(d=1024, n_gate=1024, b=BUNDLE_B, seed=7):
    """Independent computation: random dense +/-1 codes (near-orthogonal at d>>b)."""
    rng = np.random.default_rng(seed)
    codes = rng.choice([-1.0, 1.0], size=(n_gate, d)).astype(np.float32)
    signed = _l2n(np.sign(codes).astype(np.float32))
    ceiling = float(np.log2(n_gate / b))
    s2 = recoverability_topb(signed, n_gate, SIGMA_GATE, seed, b)          # sign, no bundling
    s3 = bundle_survival(codes, n_gate, b, False, seed)                     # SUM (the flat-store op)
    return ceiling, fano_bits_list(s2, n_gate, b), fano_bits_list(s3, n_gate, b)


def disk_real_code_bits():
    """Read the REAL concept codes' bundling-retention from the ruler's landed FULL metrics."""
    m = json.load(open(RULER_METRICS, encoding="utf-8"))
    per_arm = m["by_d"]["1024"]["per_arm"]
    out = {}
    for arm in ("INC_SIMHASH", "C1_KCAP_GRD_f005_BOOST", "C4_PHASOR"):
        out[arm] = float(per_arm[arm]["BUNDLING"]["bits_retained_after_the_sum"])
    return out, float(m["by_d"]["1024"]["per_arm"]["INC_SIMHASH"]["BUNDLING"]["ceiling_bits"])


def main() -> int:
    ceiling, sign_bits, add_bits_orth = orthogonal_stage_bits()
    print("=" * 78)
    print("(A) INDEPENDENT computation, near-ORTHOGONAL dense +/-1 codes, ruler functions unmodified")
    print("    d=1024  N_GATE=1024  BUNDLE_B=%d  ceiling=%.3f bits" % (BUNDLE_B, ceiling))
    print("    sign a code, no bundling : retains %.3f bits (destroys %.3f) -> signing is loss-free"
          % (sign_bits, ceiling - sign_bits))
    print("    SUM B=8 codes (flat store): retains %.3f bits (destroys %.3f) -> superposition of"
          % (add_bits_orth, ceiling - add_bits_orth))
    print("      ORTHOGONAL codes is loss-free; destruction is a GEOMETRY property, not 'adding'.")

    real, real_ceiling = disk_real_code_bits()
    print("\n(B) REAL concept codes, read from the validated ruler's landed FULL metrics (NOT re-run)")
    print("    %s" % RULER_METRICS.replace(_REPO + os.sep, ""))
    print("    INC_SIMHASH (incumbent live) retains %.4f / %.1f  -> adding destroys %.4f"
          % (real["INC_SIMHASH"], real_ceiling, real_ceiling - real["INC_SIMHASH"]))
    print("    C1_KCAP_GRD (sparse graded)  retains %.4f / %.1f  -> %.2fx the incumbent"
          % (real["C1_KCAP_GRD_f005_BOOST"], real_ceiling,
             real["C1_KCAP_GRD_f005_BOOST"] / real["INC_SIMHASH"]))
    print("    C4_PHASOR                    retains %.4f / %.1f  -> dies in bundling"
          % (real["C4_PHASOR"], real_ceiling))
    print("\n" + "-" * 78)
    print("VERDICT for the slug:")
    print("  * '6.93 of 7 bits' is a PHANTOM (absent from data/ experiments/ notes/ preregs/).")
    print("  * The incumbent flat-store code DOES lose ~%.1f of 7 bits under the sum (real, on disk)."
          % (real_ceiling - real["INC_SIMHASH"]))
    print("  * The survivable-superposition lever is CODE FORMAT (sparse graded retains %.2fx more),"
          % (real["C1_KCAP_GRD_f005_BOOST"] / real["INC_SIMHASH"]))
    print("    a Phase-1 change -- NOT the addressed storage the brief proposes.")
    print("-" * 78)

    # can-fail assertions
    assert ceiling - sign_bits < 0.5, "signing should be loss-free; destroyed %.3f" % (ceiling - sign_bits)
    assert ceiling - add_bits_orth < 0.5, \
        "orthogonal-code superposition should be loss-free; destroyed %.3f" % (ceiling - add_bits_orth)
    assert real["INC_SIMHASH"] < real["C1_KCAP_GRD_f005_BOOST"], \
        "sparse-graded should retain MORE than the incumbent (the code-format lever)"
    assert real["C4_PHASOR"] < 0.5, "C4_PHASOR should die in bundling"
    print("VERIFICATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
