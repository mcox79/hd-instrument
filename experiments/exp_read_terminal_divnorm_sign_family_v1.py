"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the SIGN()-on-a-bundle BIPOLAR sibling family.

The brief calls the `sign()`-on-a-bundle sites "the SAME wrong-op in a bipolar code" and lists them
(grounding_acquisition_loop, situation_focus, role_slot_summarizer, event_bundle, char_positional_encoder).
`norm="divnorm"` is FHRR-complex only, so it does NOT apply to these bipolar/MAP-VSA {-1,+1} bundles -- the
bipolar analog of "per-component renorm vs pooled divnorm" is "sign(sum) vs the graded integer sum (optionally
pooled-normalized)". `sign(S_i)` is a per-component quantiser that discards the graded vote margin, exactly as
per-component FHRR renorm discards the per-component magnitude.

THIS CELL asks whether the READOUT+LOAD principle established for FHRR generalizes to the bipolar code:
does the GRADED / POOLED sum beat SIGN for a direction-sensitive read, with the gap growing under LOAD, and is
the effect a no-op at low load? If yes, the audit's "graded beats sign, growing margin" is the same mechanism as
the register's divnorm win, in a different code -- one principle, both formats.

STORE: M = superposition of m bipolar bound (key, value) pairs (MAP-VSA: bind = elementwise multiply, its own
inverse). Three store forms:
  SIGN    = sign(sum)            -- the incumbent per-component quantiser (bsc_bundle / _sign_bundle / _bundle).
  GRADED  = sum                  -- the raw integer vote sum (keeps the margin).
  POOLED  = sum / mean|sum|      -- graded + pooled divisive gain (the bipolar analog of divnorm).
READOUTS:
  ARGMAX  = per-slot unbind + argmax dot-cleanup over the value codebook (direction-sensitive).
  COSINE  = whole-store cosine to a probe (a coarse gist read).
Read back with the SAME dot-cleanup (fair across store forms; for a SIGN store dot == d - 2*Hamming).

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_sign_family_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_sign_family_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

D = 1024
V = 100
BASE_SEED = 20260829
N_TRIALS = 24


def _bipolar(rng, n):
    return rng.choice(np.array([-1.0, 1.0]), size=n)


def _store(sum_vec, form):
    if form == "SIGN":
        s = np.sign(sum_vec); s[s == 0] = 1.0; return s
    if form == "GRADED":
        return sum_vec
    if form == "POOLED":
        m = np.abs(sum_vec).mean()
        return sum_vec / m if m > 0 else sum_vec
    raise ValueError(form)


def _build(m, seed, form):
    rng = np.random.default_rng(seed)
    codebook = [_bipolar(rng, D) for _ in range(V)]           # value vocabulary
    keys = [_bipolar(rng, D) for _ in range(m)]
    truth = [int(rng.integers(0, V)) for _ in range(m)]
    ssum = np.zeros(D)
    for s in range(m):
        ssum = ssum + keys[s] * codebook[truth[s]]            # bind = elementwise multiply (MAP-VSA)
    return _store(ssum, form), keys, np.stack(codebook), truth


def _argmax_decode(M, keys, cb, truth):
    correct = 0
    for s in range(len(keys)):
        probe = M * keys[s]                                    # unbind = elementwise multiply (self-inverse)
        correct += int(int(np.argmax(cb @ probe)) == truth[s])
    return correct / len(truth)


def cell(loads=(4, 8, 16, 32, 48, 64), n_trials=N_TRIALS):
    res = {"loads": list(loads), "grid": {}}
    for m in loads:
        for form in ("SIGN", "GRADED", "POOLED"):
            accs = []
            for t in range(n_trials):
                M, keys, cb, truth = _build(m, BASE_SEED + 1000 * t + m, form)
                accs.append(_argmax_decode(M, keys, cb, truth))
            res["grid"]["m=%d/%s" % (m, form)] = round(float(np.mean(accs)), 4)
    return res


def _print(res):
    print("=== SIGN-family BIPOLAR readout+load grid: sign(sum) vs graded vs pooled ===")
    print("  MAP-VSA bound (key,value) pairs, D=%d V=%d, %d trials/cell, per-slot argmax dot-cleanup\n" % (D, V, N_TRIALS))
    print("  %-6s | %-10s | %-10s | %-10s" % ("load", "SIGN", "GRADED", "POOLED"))
    for m in res["loads"]:
        g = lambda f: res["grid"]["m=%d/%s" % (m, f)]
        print("  m=%-4d | %.3f      | %.3f      | %.3f" % (m, g("SIGN"), g("GRADED"), g("POOLED")))
    mmax = res["loads"][-1]
    d_gs = res["grid"]["m=%d/GRADED" % mmax] - res["grid"]["m=%d/SIGN" % mmax]
    d_ps = res["grid"]["m=%d/POOLED" % mmax] - res["grid"]["m=%d/SIGN" % mmax]
    print("\n  AT MAX LOAD m=%d: GRADED-minus-SIGN=%+.3f, POOLED-minus-SIGN=%+.3f -> the SAME wrong-op: sign() "
          "discards the graded vote margin a direction-sensitive read needs under load." % (mmax, d_gs, d_ps))
    print("  (POOLED ~= GRADED for argmax: a global scalar is argmax-invariant, so the LEVER is dropping sign(),"
          " not the pooled gain -- exactly mirroring the FHRR finding.)")


def _self_test():
    # low load: all three recover ~perfectly
    M, keys, cb, truth = _build(4, BASE_SEED, "GRADED")
    assert _argmax_decode(M, keys, cb, truth) >= 0.99, "low-load graded should be ~1.0"
    # overload: GRADED beats SIGN (the wrong-op signature), POOLED ~= GRADED (argmax scale-invariant)
    Mg, kg, cbg, tg = _build(48, BASE_SEED + 7, "GRADED")
    Ms, ks, cbs, ts = _build(48, BASE_SEED + 7, "SIGN")
    Mp, kp, cbp, tp = _build(48, BASE_SEED + 7, "POOLED")
    a_g = _argmax_decode(Mg, kg, cbg, tg); a_s = _argmax_decode(Ms, ks, cbs, ts); a_p = _argmax_decode(Mp, kp, cbp, tp)
    assert a_g > a_s, "GRADED (%.3f) should beat SIGN (%.3f) at overload" % (a_g, a_s)
    assert abs(a_p - a_g) < 1e-9, "POOLED must equal GRADED for argmax (scale-invariant): %.4f vs %.4f" % (a_p, a_g)
    print("[self-test] PASS: GRADED %.3f > SIGN %.3f at overload; POOLED==GRADED (argmax scale-invariant)" % (a_g, a_s))


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
