"""THE STORAGE-REGIME axis: EXACT-KEY read vs PARTIAL-CUE completion (the audit's #1 memory defect).

BRAIN_FOUNDATIONAL_AUDIT's single biggest memory defect: "we ask every question of the WRONG memory ... the read
path is EXACT-KEY, no partial-cue completion." The hippocampus (CA3) is a pattern-completion device: give it a
DEGRADED / PARTIAL cue and it settles onto the full stored trace (Marr 1971; Rolls 2013). Our register decode
unbinds by the EXACT key and argmaxes -- so how gracefully does it degrade when the retrieval cue is only
partially correct, and does CA3-style attractor completion extend the tolerable degradation?

SETUP: store the register bundle S = SUM_s bind(v_s, k_s) (D dims, M slots, V-vocab). Query slot s with a cue k'
that is the true key k_s with a fraction f of its D components REPLACED by random phase (f=0 exact, f=1 useless
-> a partial cue). Decode via (a) ARGMAX (the organ) and (b) CA3-ITER attractor completion. Sweep f at the
register's operating point (D=1024, M=8) and near the cliff (D=256, M=48). FLOOR = chance 1/V; TWIN = fully
random cue (f=1). VERDICT: if accuracy holds to large f, the read IS partial-cue-robust (audit defect overstated
for THIS store); if it collapses fast, the read is exact-key brittle and CA3 completion is the needed fix.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_partialcue_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_partialcue_v1/. NO hdlab write.
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

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_partialcue_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _argmax(readback, role_mat):
    return int(torch.argmax(torch.real(torch.conj(role_mat) @ readback)))


def _iter_complete(readback, role_mat, steps=5):
    d = readback.shape[0]; tau = float(np.sqrt(d)); x = readback; idx = _argmax(x, role_mat)
    for _ in range(steps):
        w = torch.softmax(torch.real(torch.conj(role_mat) @ x) / tau, dim=0).to(role_mat.dtype)
        x = w @ role_mat
        ni = int(torch.argmax(torch.real(torch.conj(role_mat) @ x)))
        if ni == idx:
            break
        idx = ni
    return idx


def _degrade(key, f, g):
    """Replace a fraction f of the key's D components with fresh random phase (a PARTIAL cue: (1-f) correct)."""
    if f <= 0:
        return key
    d = key.shape[0]
    noise = unit_phase_vec(d, g)
    mask = (torch.rand(d, generator=g) < f)
    out = key.clone()
    out[mask] = noise[mask]
    return out


def _one(d, m, v, f, n_reps, seed, readout="argmax"):
    ok = tot = 0
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        role_list = [unit_phase_vec(d, g) for _ in range(v)]
        role_mat = torch.stack(role_list, dim=0)
        keys = [unit_phase_vec(d, g) for _ in range(m)]
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [int(rr.integers(0, v)) for _ in range(m)]
        S = binding.bind(role_list[truth[0]], keys[0])
        for s in range(1, m):
            S = S + binding.bind(role_list[truth[s]], keys[s])
        for s in range(m):
            kq = _degrade(keys[s], f, _gen(seed + rep * 7919 + 100 + s))
            rb = binding.unbind(S, kq)
            ci = _iter_complete(rb, role_mat) if readout == "iter" else _argmax(rb, role_mat)
            ok += int(ci == truth[s]); tot += 1
    return ok / tot


def run():
    v = 100
    f_grid = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    n_reps = 50
    points = {"operating_D1024_M8": (1024, 8), "nearcliff_D256_M48": (256, 48)}
    out = {}
    for name, (d, m) in points.items():
        out[name] = {"d": d, "m": m,
                     "argmax": {str(f): round(_one(d, m, v, f, n_reps, SEED, "argmax"), 4) for f in f_grid},
                     "iter": {str(f): round(_one(d, m, v, f, n_reps, SEED, "iter"), 4) for f in f_grid}}
    return {"anchor": "dim_phase_diagram_partialcue_v1", "v": v, "chance": round(1.0 / v, 4),
            "f_grid": f_grid, "n_reps": n_reps, "points": out}


def summarize(res):
    print(f"\n=== PARTIAL-CUE completion (exact-key read vs degraded cue; V={res['v']}, chance={res['chance']}) ===")
    print(f"  cue degradation f (0=exact key, 1=useless); accuracy holding = partial-cue robustness")
    for name, p in res["points"].items():
        print(f"  [{name}]  f: " + " ".join(f"{f:.1f}" for f in res["f_grid"]))
        print(f"     argmax:  " + " ".join(f"{p['argmax'][str(f)]:.2f}" for f in res["f_grid"]))
        print(f"     CA3iter: " + " ".join(f"{p['iter'][str(f)]:.2f}" for f in res["f_grid"]))
    # verdict from operating point
    op = res["points"]["operating_D1024_M8"]["argmax"]
    half_f = next((f for f in res["f_grid"] if op[str(f)] < 0.5), 1.0)
    print(f"  => the exact-key read tolerates cue degradation up to f~{half_f} before falling below 0.5 "
          f"(operating point). Partial-cue robustness is {'GOOD' if half_f >= 0.5 else 'LIMITED (exact-key brittle)'}.")


def self_test():
    a0 = _one(1024, 8, 100, 0.0, 20, 1, "argmax")
    assert a0 > 0.98, f"exact key (f=0) must decode; got {a0}"
    a1 = _one(1024, 8, 100, 1.0, 20, 1, "argmax")
    assert a1 < 0.1, f"useless cue (f=1) must be ~chance; got {a1}"
    amid = _one(1024, 8, 100, 0.5, 20, 1, "argmax")
    assert a1 - 1e-9 <= amid <= a0 + 1e-9, f"accuracy must fall monotonically-ish with degradation; {a0} {amid} {a1}"
    print(f"SELF-TEST PASS: f=0 {a0:.3f} -> f=0.5 {amid:.3f} -> f=1 {a1:.3f} (chance 0.01)")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run(); res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
