"""MULTI-AXIS phase diagram of the FHRR memory algebra -- the dimensions BEYOND N (owner: "there is
definitely more than n").

The register cell (exp_dim_phase_diagram_register_v1) sweeps the two obvious axes D and load M. But an
FHRR superposition store's fidelity is governed by SEVERAL parameters, and every hdlab superposition organ
(register, working_memory, context_retention, cortex, event_bundle, content_addressable_retrieval, the
encoders) inherits the SAME algebra -> the SAME axes. This cell sweeps them, each on the shared
bind/bundle/cleanup primitive, recomputing chance + an info-free twin at every point:

  AXIS V  -- cleanup / vocabulary width (how many items must be told apart). More competitors = harder.
  AXIS B  -- n_banks routing sparsity (k_per_bank = M / n_banks; hdlab.working_memory's discriminating
             regime is k_per_bank >= 64 @ N_DIM=8192). The sparse-store lever, swept as a first-class axis.
  AXIS R  -- CODE ORTHOGONALITY / feature-overlap: the brain's atomic codes are NOT iid-random; they share
             structure. We mix each atom with a shared background phasor by fraction rho and sweep rho. This
             is working_memory's FEATURE_OVERLAP_FRAC axis -- the one that MOVES the whole capacity threshold
             (RANDOM 0.993 vs ADVERSARIAL overlap-0.20 0.980 there). Brain-critical: correlated codes cliff earlier.
  AXIS Q  -- numeric PRECISION: quantize the unit phasor's angle to q levels (q=inf = complex64 FHRR; q=2 =
             sign/BSC-like). Bits-per-component is a capacity axis (int8/ternary stores exist in hdlab).
  AXIS K  -- composition/binding DEPTH: recover a filler bound under a CHAIN of d keys (nested bind). Cleanup
             degrades with depth even at fixed load.

Each axis holds the others at a fixed operating point (D=1024, M=32, V=100, n_banks=8, rho=0, full precision,
depth=1) and moves ONE variable -- the one-variable discipline. Verdict per axis: does accuracy stay flat
(that axis is not the lever at our operating point) or CI-separated-move (it is a lever)?

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_axes_v1.py [--quick] [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_axes_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import math
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax  # noqa: E402
from hdlab.situation_model_multibank import stable_bank_id  # noqa: E402
import experiments.exp_dim_phase_diagram_register_v1 as R  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_axes_v1")
SEED = 20260828

# operating point (the register's current live config unless the axis under test moves it)
OP = {"d": 1024, "m": 32, "v": 100, "n_banks": 8, "rho": 0.0, "q": 0, "depth": 1}


def _phasor(d, g):
    return unit_phase_vec(d, g)


def _corr_phasor(d, g, background, rho):
    """A unit phasor correlated with a shared `background` by fraction rho: angle = (1-rho)*own + rho*bg,
    renormalised to unit magnitude. rho=0 -> iid random; rho->1 -> all atoms collapse onto the background
    (maximal feature overlap). Models the brain's NON-orthogonal codes."""
    if rho <= 0.0:
        return _phasor(d, g)
    own = torch.angle(_phasor(d, g))
    bg = torch.angle(background)
    # circular mean of the two angles weighted by (1-rho), rho
    x = (1 - rho) * torch.cos(own) + rho * torch.cos(bg)
    y = (1 - rho) * torch.sin(own) + rho * torch.sin(bg)
    ang = torch.atan2(y, x)
    return torch.polar(torch.ones(d), ang).to(torch.complex64)


def _quantize(vec, q):
    """Quantize a unit phasor's angle to q equally-spaced levels (q<=0 -> unchanged full precision).
    q=2 = {0, pi} = a real sign code (BSC/bipolar-like); q=4 = QPSK; larger q -> finer."""
    if q is None or q <= 0:
        return vec
    ang = torch.angle(vec)
    step = 2.0 * math.pi / q
    qang = torch.round(ang / step) * step
    return torch.polar(torch.ones_like(ang), qang).to(torch.complex64)


def _cell(d, m, v, n_banks, rho, q, depth, n_reps, seed):
    """One (axes) cell: build m events (verb bound under a depth-chain of keys) at dim d with vocab v,
    optional code correlation rho and quantization q, routed across n_banks; decode each and score.
    Returns (acc, twin_acc, chance)."""
    ok = tot = tw_ok = tw_tot = 0
    chance = 1.0 / v
    for rep in range(n_reps):
        g = R._gen(seed + rep * 7919)
        background = _phasor(d, g) if rho > 0 else None
        role_list = [_quantize(_corr_phasor(d, g, background, rho), q) for _ in range(v)]
        role_mat = torch.stack(role_list, dim=0)                # [V, d] for vectorised cleanup
        idx_vecs = [_quantize(_corr_phasor(d, g, background, rho), q) for _ in range(m)]
        depth_keys = [_quantize(_corr_phasor(d, g, background, rho), q) for _ in range(max(depth - 1, 0))]
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [int(rr.integers(0, v)) for _ in range(m)]
        # bind the filler under idx[s] AND the depth-chain of extra keys; route to a bank
        banks = {}
        for s in range(m):
            bound = role_list[truth[s]]
            for k in [idx_vecs[s]] + depth_keys:
                bound = binding.bind(bound, k)
            b = stable_bank_id(s, n_banks)
            banks.setdefault(b, []).append(bound)
        bank_reg = {b: (bundling.bundle(torch.stack(e)) if len(e) > 1 else e[0]) for b, e in banks.items()}
        # info-free twin: decode an existing bank by a random key
        gtw = R._gen(seed + rep * 7919 + 555)
        any_reg = next(iter(bank_reg.values()))
        tb = int(torch.argmax(torch.real(torch.conj(role_mat) @ binding.unbind(any_reg, _phasor(d, gtw)))))
        for s in range(m):
            read = bank_reg[stable_bank_id(s, n_banks)]
            for k in [idx_vecs[s]] + depth_keys:      # unbind the whole chain
                read = binding.unbind(read, k)
            best = int(torch.argmax(torch.real(torch.conj(role_mat) @ read)))
            ok += int(best == truth[s]); tot += 1
            tw_ok += int(tb == truth[s]); tw_tot += 1
    return ok / tot, tw_ok / tw_tot, chance


def _axis(name, key, values, n_reps, seed, fixed=None):
    cfg = dict(OP);
    if fixed:
        cfg.update(fixed)
    rows = []
    for val in values:
        c = dict(cfg); c[key] = val
        acc, tw, ch = _cell(c["d"], c["m"], c["v"], c["n_banks"], c["rho"], c["q"], c["depth"], n_reps, seed)
        rows.append({key: val, "acc": round(acc, 4), "twin": round(tw, 4), "chance": round(ch, 4),
                     "k_per_bank": c["m"] // max(c["n_banks"], 1) if key == "n_banks" or name == "B" else None})
    return {"axis": name, "var": key, "fixed": cfg, "rows": rows}


def run(quick=False):
    nr = 20 if quick else 40
    axes = []
    axes.append(_axis("V_cleanup_width", "v", [20, 50, 100, 200, 500, 1000] if not quick else [20, 100, 500], nr, SEED))
    # n_banks: at higher load so routing matters (k_per_bank = m/n_banks)
    axes.append(_axis("B_routing_sparsity", "n_banks", [1, 2, 4, 8, 16, 32] if not quick else [1, 8, 32], nr,
                      SEED, fixed={"m": 64}))
    axes.append(_axis("R_code_orthogonality", "rho", [0.0, 0.1, 0.2, 0.4, 0.6, 0.8] if not quick else [0.0, 0.4, 0.8],
                      nr, SEED, fixed={"m": 32}))
    axes.append(_axis("Q_precision", "q", [0, 2, 3, 4, 8, 16] if not quick else [0, 2, 4], nr, SEED, fixed={"m": 32}))
    axes.append(_axis("K_binding_depth", "depth", [1, 2, 3, 4, 5] if not quick else [1, 3, 5], nr, SEED,
                      fixed={"m": 16}))
    return {"anchor": "dim_phase_diagram_axes_v1", "op": OP, "n_reps": nr, "axes": axes}


def _verdict(axis):
    accs = [r["acc"] for r in axis["rows"]]
    spread = max(accs) - min(accs)
    return "LEVER (accuracy moves >0.1 across axis)" if spread > 0.1 else "not a lever at operating point (flat)"


def summarize(res):
    for ax in res["axes"]:
        print(f"\n=== AXIS {ax['axis']} (vary {ax['var']}; others at operating point "
              f"D={ax['fixed']['d']} M={ax['fixed']['m']} V={ax['fixed']['v']} banks={ax['fixed']['n_banks']} "
              f"rho={ax['fixed']['rho']} q={ax['fixed']['q']} depth={ax['fixed']['depth']}) ===")
        for r in ax["rows"]:
            extra = f"  k/bank={r['k_per_bank']}" if r.get("k_per_bank") is not None else ""
            print(f"  {ax['var']}={r[ax['var']]:<6} acc={r['acc']:.3f}  twin={r['twin']:.3f}  chance={r['chance']:.3f}{extra}")
        print(f"  -> {_verdict(ax)}")


def self_test():
    # depth-1, low load, generous D decodes ~perfectly; sign-quantized (q=2) is worse than full at load
    a1, tw, ch = _cell(2048, 4, 50, 1, 0.0, 0, 1, 15, 1)
    assert a1 > 0.95, f"generous D low load must decode; got {a1}"
    assert tw < 3 * ch + 0.02, f"twin must be ~chance; got {tw} vs {ch}"
    hi, _, _ = _cell(256, 48, 50, 1, 0.0, 0, 1, 15, 1)          # full precision at load
    lo, _, _ = _cell(256, 48, 50, 1, 0.0, 2, 1, 15, 1)          # sign-quantized at same load
    assert lo <= hi + 0.02, f"sign quantization should not IMPROVE over full precision; full={hi} q2={lo}"
    corr, _, _ = _cell(256, 48, 50, 1, 0.8, 0, 1, 15, 1)        # highly-correlated codes
    assert corr <= hi + 0.02, f"correlated codes should not beat orthogonal; ortho={hi} rho0.8={corr}"
    print(f"SELF-TEST PASS: clean(2048,M4)={a1:.3f} twin={tw:.3f}(ch {ch:.3f}); "
          f"precision full={hi:.3f}>=q2={lo:.3f}; orthogonal={hi:.3f}>=corr0.8={corr:.3f}")


def main():
    quick = "--quick" in sys.argv
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run(quick=quick)
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics_quick.json" if quick else "metrics.json"), "w",
              encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
