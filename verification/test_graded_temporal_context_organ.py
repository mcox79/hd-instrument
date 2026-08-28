"""Witness for hdlab.graded_temporal_context (landed 2026-08-28, landing-step 1 of the factorized entity store).

Self-contained construction proof of the graded temporal-context primitive (no corpus):
  [1] TEMPORAL CONTIGUITY: the context kernel is 1.0 at zero lag and DECREASES smoothly/monotonically with |t - t'|
      (adjacent moments are more similar -> retrieved together). An ORTHOGONAL sub-slot key (the cheap finer-key fix)
      has NO such gradient -- this graded clock restores it.
  [2] UNIT MAGNITUDE: every ctx(t) is a unit-magnitude phasor (a valid FHRR atom).
  [3] FHRR-BINDABLE: unbind(bind(x, ctx(t)), ctx(t)) recovers x -- so content x context compose + read back.
"""
from __future__ import annotations

import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab import binding  # noqa: E402
from hdlab.graded_temporal_context import GradedTemporalContext  # noqa: E402
from hdlab.lexical_similarity import _cos_complex  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

D = 1024


def _kernel(clk, ta, tb):
    return float(_cos_complex(clk.ctx(ta), clk.ctx(tb)))


def main() -> int:
    clk = GradedTemporalContext(d=D, seed=20260828)

    # [1] temporal contiguity: kernel peaks at zero lag, decreases monotonically with the lag
    lags = [0, 1, 2, 4, 8, 16, 32]
    ks = [_kernel(clk, 100.0, 100.0 + L) for L in lags]
    print(f"[1] contiguity kernel by lag {lags}: {[round(k,3) for k in ks]}")
    assert abs(ks[0] - 1.0) < 1e-6, "kernel must be 1.0 at zero lag"
    assert all(ks[i] > ks[i + 1] - 1e-6 for i in range(len(ks) - 1)), "kernel must decrease with lag (temporal contiguity)"
    assert ks[-1] < 0.5, f"kernel must decay substantially by lag 32 (got {ks[-1]:.3f}) -- graded, not flat"
    # contrast: an ORTHOGONAL sub-slot key has no gradient (each slot ~iid) -> contiguity ~0 across distinct slots
    g = torch.Generator().manual_seed(1)
    ortho = [unit_phase_vec(D, g) for _ in range(3)]
    ortho_k = float(_cos_complex(ortho[0], ortho[1]))
    print(f"[1] contrast: orthogonal-slot cross-similarity {ortho_k:.3f} (~0, NO contiguity gradient)")
    assert abs(ortho_k) < 0.15, "orthogonal slots carry no contiguity"

    # [2] unit magnitude
    c = clk.ctx(42.0)
    mag = c.abs()
    assert torch.allclose(mag, torch.ones_like(mag), atol=1e-4), "ctx must be unit-magnitude (a valid FHRR atom)"
    print(f"[2] unit magnitude PASS (max |mag-1| = {float((mag-1).abs().max()):.2e})")

    # [3] FHRR-bindable: unbind(bind(x, ctx(t)), ctx(t)) == x
    gx = torch.Generator().manual_seed(7)
    x = unit_phase_vec(D, gx)
    ctxt = clk.ctx(55.0)
    recovered = binding.unbind(binding.bind(x, ctxt), ctxt)
    sim = float(_cos_complex(recovered, x))
    print(f"[3] bindable: unbind(bind(x, ctx(t)), ctx(t)) ~= x, cos={sim:.4f}")
    assert sim > 0.99, "the temporal context must be a clean FHRR bind/unbind key"

    print("\nALL WITNESS ASSERTIONS PASSED -- the graded temporal context carries a smooth temporal-contiguity kernel")
    print("(peaks at zero lag, decays with |dt|; an orthogonal slot key does not), is unit-magnitude, and binds/unbinds")
    print("cleanly as an FHRR key -- the 'when' half the factorized store composes with content + order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
