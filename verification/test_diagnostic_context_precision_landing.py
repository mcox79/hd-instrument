"""Landing witness: the P9 precision-weighting (gamma/topk) is BYTE-IDENTICAL at default + verbatim to the cell.

Problem: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader (P9, owner-DONE).
The landable win is precision-weighting (Friston selective gain) on the biased-competition diagnostic readout:
gamma (sharpening exponent) + topk (hard selective gain). Landed into hdlab/diagnostic_context_wsd with a
DEFAULT (gamma=1.0, topk=None) that must be BYTE-IDENTICAL to the pre-P9 readout (so no consumer changes unless
it opts in). This witness proves:
  1. default gamma=1.0, topk=None -> scores BIT-IDENTICAL to the no-arg call (np.array_equal), many random cases.
  2. gamma>1 and topk change the query (the parameter is live), toward the most-diagnostic context words.
  3. VERBATIM to the reference: the landed diagnostic_query matches exp_atl_hubspoke_query_side_readout_v1's
     precision-sharpen construction (topk mask + diag**gamma) on a synthetic case.
Cheap + deterministic (no SemCor); the a_s +0.023 gain is the heavy W-witness (test_atl_hubspoke_meaning_channel).
NO LLM. numpy only. Run: .venv/Scripts/python.exe verification/test_diagnostic_context_precision_landing.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
from hdlab.diagnostic_context_wsd import diagnostic_context_scores, diagnostic_query, diagnosticity, _unit

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok
    FAIL += (not ok)
    return ok


def _rand_unit(rng, k, d):
    M = rng.standard_normal((k, d))
    return M / np.linalg.norm(M, axis=1, keepdims=True)


def main():
    rng = np.random.default_rng(20260904)

    # 1) default byte-identity across many random cases
    ident = True
    for _ in range(200):
        W = int(rng.integers(2, 12)); S = int(rng.integers(2, 6)); D = 16
        C = _rand_unit(rng, W, D); G = _rand_unit(rng, S, D)
        base = diagnostic_context_scores(C, G)
        deflt = diagnostic_context_scores(C, G, gamma=1.0, topk=None)
        if not np.array_equal(base, deflt):
            ident = False
            break
    chk("default (gamma=1.0, topk=None) is BIT-IDENTICAL to the no-arg readout (200 random cases)", ident)

    # 2) the parameters are LIVE (gamma>1 and topk change the query)
    W, S, D = 8, 3, 16
    C = _rand_unit(rng, W, D); G = _rand_unit(rng, S, D)
    q1 = diagnostic_query(C, G)
    qg = diagnostic_query(C, G, gamma=3.0)
    qk = diagnostic_query(C, G, topk=2)
    chk("gamma>1 changes the query (precision sharpening is live)", not np.array_equal(q1, qg))
    chk("topk changes the query (hard selective gain is live)", not np.array_equal(q1, qk))

    # 3) VERBATIM to the reference construction (topk mask then diag**gamma, weighted context mean)
    def ref_query(C, G, gamma, topk):
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0.0, None)
        if topk is not None and topk < len(diag):
            thr = np.sort(diag)[-topk]
            diag = np.where(diag >= thr, diag, 0.0)
        w = diag ** gamma
        if float(w.sum()) <= 1e-9:
            return _unit(C.mean(0))
        return _unit((w[:, None] * C).sum(0))
    match = True
    for g, k in [(1.0, None), (2.0, None), (3.0, None), (1.0, 2), (2.0, 3), (4.0, 1)]:
        if not np.allclose(diagnostic_query(C, G, gamma=g, topk=k), ref_query(C, G, g, k), atol=0, rtol=0):
            match = False
            break
    chk("landed diagnostic_query VERBATIM-matches the reference readout_pick construction (6 gamma/topk configs)", match)

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
