"""THE CLEANUP-RULE AXIS -- is the register's capacity cliff a fundamental limit, or an ARGMAX-READOUT
artifact the brain's CA3 attractor completion would push back?

The register (situation_model_accumulate) decodes each slot INDEPENDENTLY: readback_s = unbind(bundle, key_s)
= verb_s + crosstalk from the OTHER M-1 bound terms, then a single-shot argmax over the codebook. The crosstalk
that makes the cliff is the co-superposed slots. But the brain's hippocampal CA3 does not read one item at a
time -- it SETTLES the whole conjunctive trace jointly (recurrent attractor completion; Marr 1971, Treves & Rolls
1994; Norman & O'Reilly 2003). The VSA analog of joint settling over a FACTORED code is a RESONATOR / successive-
interference-cancellation (SIC) decode (Frady/Kent/Olshausen/Sommer 2020 resonator networks; matching pursuit):
knowing all the keys, iteratively estimate every slot, reconstruct its binding, and SUBTRACT the other slots'
estimated contributions before re-decoding -- so confident slots clean up the ambiguous ones.

THIS CELL: at and past the flat register's cliff (D=256, M swept up), compare
  * ARGMAX    -- the organ's current independent per-slot readout (the floor that cliffs).
  * SIC/JOINT -- Gauss-Seidel resonator iteration (brain-faithful joint completion), same bind/bundle algebra.
  * TWIN      -- SIC run with SHUFFLED keys (info-free: joint structure present but keys wrong -> must NOT help).
CAN-FAIL: if SIC does NOT beat ARGMAX, the cliff is a genuine capacity limit (not a readout artifact) -- itself a
valuable, publishable negative. If SIC DOES beat it, the register's decode is leaving capacity on the table and
the brain-faithful CA3-style readout is the fix (an hdlab proposal, not a D change).

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_cleanup_rule_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_cleanup_rule_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

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

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_cleanup_rule_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _argmax(readback, role_mat):
    return int(torch.argmax(torch.real(torch.conj(role_mat) @ readback)))


def _decode_argmax(bundle, keys, role_mat):
    """Independent per-slot argmax (the organ's current readout)."""
    return [_argmax(binding.unbind(bundle, keys[s]), role_mat) for s in range(len(keys))]


def _decode_sic(bundle, keys, role_mat, n_iter=6):
    """Resonator / SIC joint decode (brain-faithful CA3 joint completion analog). Init with independent
    argmax, then iterate: reconstruct all slots' estimated bindings, and for each slot decode the residual
    with the OTHER slots' estimates removed (Gauss-Seidel). Same FHRR bind/unbind algebra as the organ."""
    m = len(keys)
    est = _decode_argmax(bundle, keys, role_mat)
    for _ in range(n_iter):
        changed = False
        # reconstruct every slot's current estimated binding once
        recon = [binding.bind(role_mat[est[s]], keys[s]) for s in range(m)]
        total = recon[0].clone()
        for s in range(1, m):
            total = total + recon[s]
        for s in range(m):
            residual = bundle - (total - recon[s])       # remove OTHER slots' estimated contributions
            new = _argmax(binding.unbind(residual, keys[s]), role_mat)
            if new != est[s]:
                total = total - recon[s]
                recon[s] = binding.bind(role_mat[new], keys[s])
                total = total + recon[s]
                est[s] = new
                changed = True
        if not changed:
            break
    return est


def _one(d, m, v, n_reps, seed, shuffle_keys=False, n_iter=6):
    """Accuracy of ARGMAX and SIC over n_reps entities (m slots, vocab v, dim d)."""
    a_ok = s_ok = tot = 0
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        role_list = [unit_phase_vec(d, g) for _ in range(v)]
        role_mat = torch.stack(role_list, dim=0)
        keys = [unit_phase_vec(d, g) for _ in range(m)]
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [int(rr.integers(0, v)) for _ in range(m)]
        bundle = binding.bind(role_list[truth[0]], keys[0])
        for s in range(1, m):
            bundle = bundle + binding.bind(role_list[truth[s]], keys[s])
        dec_keys = keys
        if shuffle_keys:                                  # info-free twin: SIC with wrong keys
            perm = list(np.random.default_rng(seed + rep + 99).permutation(m))
            dec_keys = [keys[p] for p in perm]
        a = _decode_argmax(bundle, keys, role_mat)
        s_ = _decode_sic(bundle, dec_keys, role_mat, n_iter=n_iter)
        for s in range(m):
            a_ok += int(a[s] == truth[s]); s_ok += int(s_[s] == truth[s]); tot += 1
    return a_ok / tot, s_ok / tot


def run():
    d, v = 256, 100
    m_grid = [16, 32, 48, 64, 96, 128]
    n_reps = 40
    rows = []
    for m in m_grid:
        a, s = _one(d, m, v, n_reps, SEED)
        _, tw = _one(d, m, v, max(n_reps // 2, 15), SEED + 1, shuffle_keys=True)
        rows.append({"D": d, "M": m, "argmax": round(a, 4), "sic": round(s, 4),
                     "sic_gain": round(s - a, 4), "sic_shuffled_twin": round(tw, 4)})
    return {"anchor": "dim_phase_diagram_cleanup_rule_v1", "d": d, "v": v, "n_reps": n_reps,
            "chance": round(1.0 / v, 4), "rows": rows}


def summarize(res):
    print(f"\n=== CLEANUP-RULE axis: argmax vs SIC/joint (CA3 completion analog) at D={res['d']}, V={res['v']}, "
          f"chance={res['chance']} ===")
    print("     M   argmax    SIC   gain   SIC(shuffled-key twin)")
    for r in res["rows"]:
        print(f"  {r['M']:>4d}  {r['argmax']:.3f}  {r['sic']:.3f}  {r['sic_gain']:+.3f}   {r['sic_shuffled_twin']:.3f}")
    gains = [r["sic_gain"] for r in res["rows"]]
    verdict = ("SIC BEATS argmax -> the cliff is partly a READOUT artifact; CA3-style joint completion is the fix"
               if max(gains) > 0.05 else
               "SIC does NOT beat argmax -> the cliff is a GENUINE capacity limit, not a readout artifact")
    print(f"  max SIC gain = {max(gains):+.3f}  => {verdict}")


def self_test():
    # low load: both perfect. In the MODERATE-overload window (argmax off the plateau but >50% right), the
    # brain-faithful SIC/joint completion RECOVERS accuracy CI-clear; the shuffled-key twin stays at chance.
    # (At EXTREME overload the resonator diverges -- <50% init-correct -- a real, known failure mode, not a bug.)
    a, s = _one(256, 8, 100, 15, 1)
    assert a > 0.98 and s > 0.98, f"low load both perfect; argmax={a} sic={s}"
    a2, s2 = _one(256, 64, 100, 25, 1)                 # moderate overload: argmax off plateau (~0.64)
    assert (s2 - a2) > 0.15, f"SIC/CA3-completion must recover accuracy in the overload window; argmax={a2} sic={s2}"
    _, tw = _one(256, 64, 100, 15, 1, shuffle_keys=True)
    assert tw < 0.2, f"shuffled-key SIC (info-free twin) must be ~chance; got {tw}"
    print(f"SELF-TEST PASS: low-load argmax={a:.3f} sic={s:.3f}; overload(M64) argmax={a2:.3f} -> sic={s2:.3f} "
          f"(+{s2-a2:.3f} recovery); shuffled-key twin={tw:.3f}")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
