"""DIMENSIONAL PHASE DIAGRAM -- the situation-model register (hdlab.situation_model_accumulate).

THE ONLY organ of the four in the brief that is a VSA SUPERPOSITION code, so the ONLY one with a
sqrt(D/M) capacity cliff -- ACT-R salience is a scalar activation, the ATL meaning hub is a sparse
EXACT cosine, the Competition-Model role assigner is an 8-cue logistic (none has a "D" to under-
dimension). This cell measures the register's phase diagram directly on the REAL organ primitives.

Two parts, both on the LANDED organ (make_situation_register / AccumulateRegister /
MultiBankAccumulateRegister -- read-only import, no hdlab write):

  PART A -- SYNTHETIC CAPACITY PHASE DIAGRAM + POSITIVE CONTROL (the harness demonstrably SEES a cliff).
    Task matched to the organ EXACTLY: per entity, add_event(verb_s, slot=s) for s in 0..M-1 with one
    random true verb per slot from a V-verb vocab; decode(entity, s) must recover verb_s (unbind by
    idx[s], cleanup-argmax over the V verbs). Load M = events bundled per entity (flat) or per bank
    (multibank). Sweep D and M. Floors recomputed AT EACH CELL: chance = 1/V, and an INFO-FREE twin
    (decode by a RANDOM key vector -> pure cross-talk, no signal). The POSITIVE CONTROL is that
    accuracy COLLAPSES toward chance at high M / low D and RECOVERS at high D -- if it does, a "flat"
    verdict elsewhere is a real saturation, not a blind harness.

  PART B -- THE TWO LEVERS (more-D vs sparse-code). At FIXED D, flat vs multibank(n_banks=8): multibank
    routes the M events across 8 banks so per-bank load is ~M/8. If multibank recovers accuracy at a D
    where flat has fallen off its cliff, SPARSITY/ROUTING is a lever DISTINCT from raising D (this is
    exactly p2's DG+CA3 sparse-store fix vs "just add dimensions").

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_register_v1.py [--quick] [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_register_v1/. NO hdlab/ write.
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

from hdlab.situation_model_accumulate import (  # noqa: E402
    AccumulateRegister, unit_phase_vec, cleanup_argmax,
)
from hdlab.situation_model_multibank import MultiBankAccumulateRegister  # noqa: E402
from hdlab import binding  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_register_v1")
SEED = 20260828


def _fast_cleanup_idx(readback, role_mat):
    """Vectorised FHRR cleanup: argmax_v Re(sum(conj(role_v) * readback)) -- IDENTICAL math to
    hdlab.situation_model_accumulate.cleanup_argmax, but one matmul over a stacked [V, d] role matrix
    instead of a Python loop over V (the organ's per-item loop is O(V) torch calls -> the D=8192
    bottleneck). Returns the argmax index into role_mat's rows."""
    scores = torch.real(torch.conj(role_mat) @ readback)     # [V]
    return int(torch.argmax(scores))

D_GRID = [256, 512, 1024, 2048, 4096, 8192]
M_GRID = [2, 4, 8, 16, 32, 64]     # events bundled per entity (the load / fan); flat decode is O(M^2), keep <=64
V_DEFAULT = 100                    # verb-vocab size (cleanup discrimination width; calibrated so the cliff
                                   # sits inside the D x M grid -- flat(256,64)=0.53 -> flat(1024,64)=0.99)


def _gen(seed):
    return torch.Generator().manual_seed(int(seed) % (2**31))


def _one_cell(d, m, v, backend, n_reps, seed, n_banks=8):
    """Decode accuracy for a V-verb vocab, M events/entity at dim d, averaged over n_reps entities.

    Returns (acc, twin_acc). acc = mean over all M slots of (decode==true verb). twin_acc = decode by a
    RANDOM key vector (info-free: correct binding present but queried by the wrong key -> pure cross-talk).

    Computation is IDENTICAL to the organ's decode() -- bundle -> unbind(idx) -> cleanup_argmax over the
    role vocab -- but each entity's bundle is formed ONCE per rep (the organ's AccumulateRegister.decode()
    re-bundles the whole register on every call, which is O(M^2); this is the same math at O(M))."""
    role_vocab = [f"v{i}" for i in range(v)]
    ok = tot = 0
    twin_ok = twin_tot = 0
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        if backend == "flat":
            reg = AccumulateRegister(role_vocab, d, g, max_event_slots=m)
        else:
            reg = MultiBankAccumulateRegister(role_vocab, d, g, max_event_slots=m, n_banks=n_banks)
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [role_vocab[int(rr.integers(0, v))] for _ in range(m)]
        for s in range(m):
            reg.add_event("e", truth[s], s)
        # form the bundle(s) ONCE, then decode each slot against the precomputed bundle (faithful, O(M))
        role_names = list(reg.role_vecs.keys())
        role_mat = torch.stack([reg.role_vecs[nm] for nm in role_names], dim=0)   # [V, d], for vectorised cleanup
        if backend == "flat":
            reg_full = reg.register("e")
            bank_of = {s: reg_full for s in range(m)}
        else:
            from hdlab.situation_model_multibank import stable_bank_id
            bank_of = {s: reg._bank_register("e", stable_bank_id(s, n_banks)) for s in range(m)}
        gtw = _gen(seed + rep * 7919 + 555)                          # info-free twin: random-key decode
        reg_full = reg.register("e")
        tb = role_names[_fast_cleanup_idx(binding.unbind(reg_full, unit_phase_vec(d, gtw)), role_mat)]
        for s in range(m):
            best = role_names[_fast_cleanup_idx(binding.unbind(bank_of[s], reg.idx_vecs[s]), role_mat)]
            ok += int(best == truth[s]); tot += 1
            twin_ok += int(tb == truth[s]); twin_tot += 1
    return ok / tot, twin_ok / twin_tot


def part_a(quick=False):
    """Synthetic phase diagram + positive control: accuracy(D, M) for flat and multibank."""
    v = V_DEFAULT
    n_reps = 20 if quick else 30
    d_grid = [256, 1024, 4096] if quick else D_GRID
    m_grid = [2, 8, 32] if quick else M_GRID
    chance = 1.0 / v
    grid = {"flat": {}, "multibank": {}}
    twin = {"flat": {}, "multibank": {}}
    for backend in ("flat", "multibank"):
        for d in d_grid:
            for m in m_grid:
                acc, tw = _one_cell(d, m, v, backend, n_reps, SEED)
                grid[backend][f"D{d}_M{m}"] = round(acc, 4)
                twin[backend][f"D{d}_M{m}"] = round(tw, 4)
    return {"v": v, "chance": round(chance, 4), "n_reps": n_reps, "d_grid": d_grid, "m_grid": m_grid,
            "accuracy": grid, "info_free_twin": twin}


def _critical_load(d_grid, m_grid, accgrid, thresh=0.90):
    """Largest M at which flat decode stays >= thresh, per D -- the empirical critical load M*(D).
    A rising M*(D) with D is the sqrt(D/M) signature."""
    out = {}
    for d in d_grid:
        best_m = 0
        for m in m_grid:
            if accgrid.get(f"D{d}_M{m}", 0.0) >= thresh:
                best_m = m
        out[d] = best_m
    return out


def summarize_a(a):
    d_grid, m_grid = a["d_grid"], a["m_grid"]
    flat = a["accuracy"]["flat"]; mb = a["accuracy"]["multibank"]
    mstar = _critical_load(d_grid, m_grid, flat, thresh=0.90)
    print(f"\n=== PART A: synthetic register phase diagram (V={a['v']} verbs, chance={a['chance']}, "
          f"n_reps={a['n_reps']}) ===")
    print("  FLAT decode accuracy  (rows=D, cols=M):")
    header = "    D\\M  " + "".join(f"{m:>8d}" for m in m_grid)
    print(header)
    for d in d_grid:
        print(f"  {d:>6d}  " + "".join(f"{flat[f'D{d}_M{m}']:>8.3f}" for m in m_grid))
    print("  MULTIBANK(8) decode accuracy  (rows=D, cols=M):")
    print(header)
    for d in d_grid:
        print(f"  {d:>6d}  " + "".join(f"{mb[f'D{d}_M{m}']:>8.3f}" for m in m_grid))
    print(f"  info-free twin (random-key decode), flat, mean = "
          f"{np.mean([v for v in a['info_free_twin']['flat'].values()]):.4f}  (should ~= chance {a['chance']})")
    print(f"  critical load M*(D) at flat acc>=0.90 : {mstar}   (RISING with D => sqrt(D/M) cliff seen)")
    # POSITIVE CONTROL verdict: does the harness see a cliff at all? Two independent signatures:
    #   (i) at the highest load, accuracy RISES with D (a phase transition), and
    #   (ii) the critical load M*(D) RISES with D (the sqrt(D/M) scaling law).
    lo_d, hi_d = d_grid[0], d_grid[-1]
    hi_m = m_grid[-1]
    collapsed = flat.get(f"D{lo_d}_M{hi_m}", 1.0)
    recovered = flat.get(f"D{hi_d}_M{hi_m}", 0.0)
    mstar_rises = mstar[hi_d] > mstar[lo_d]
    sees_cliff = (recovered - collapsed > 0.25) and mstar_rises
    print(f"  POSITIVE CONTROL: flat acc at (D={lo_d},M={hi_m})={collapsed:.3f} -> "
          f"(D={hi_d},M={hi_m})={recovered:.3f} (rise {recovered-collapsed:+.3f}); M*(D) rises {mstar[lo_d]}->{mstar[hi_d]}"
          f"  => harness {'SEES' if sees_cliff else 'does NOT see'} a cliff")
    return {"m_star": mstar, "sees_cliff": bool(sees_cliff),
            "collapsed_acc": collapsed, "recovered_acc": recovered}


def part_b(quick=False):
    """Two-lever isolation: at a FIXED D on the flat cliff, does multibank(8) recover accuracy that
    only more-D would otherwise buy? (multibank routes load across banks -> per-bank load M/8, so it is
    the SPARSE-CODE lever, distinct from raising D). We probe where flat has fallen off its cliff."""
    v = V_DEFAULT
    n_reps = 20 if quick else 30
    d_probe = [256, 512, 1024] if not quick else [256, 1024]
    m_probe = [32, 64] if not quick else [32]
    rows = []
    for d in d_probe:
        for m in m_probe:
            fa, _ = _one_cell(d, m, v, "flat", n_reps, SEED + 1)
            ma, _ = _one_cell(d, m, v, "multibank", n_reps, SEED + 1)
            rows.append({"D": d, "M": m, "flat": round(fa, 4), "multibank": round(ma, 4),
                         "sparsity_gain": round(ma - fa, 4)})
    return {"v": v, "n_reps": n_reps, "rows": rows}


def part_b2_multibank_cliff(quick=False):
    """CONFIRM multibank is the SAME mechanism, just shifted: push per-bank load up (large M at fixed D)
    until multibank ALSO cliffs. If its cliff sits at ~n_banks x the flat cliff, routing buys a factor of
    n_banks, not immunity (it is not a blind harness that always reads 1.0). multibank decode is O(M) not
    O(M^2), so larger M is safe here."""
    v = V_DEFAULT
    n_reps = 12 if quick else 15
    d = 256
    m_probe = [64, 128, 256] if not quick else [64, 128]
    rows = []
    for m in m_probe:
        ma, tw = _one_cell(d, m, v, "multibank", n_reps, SEED + 2)
        rows.append({"D": d, "M": m, "per_bank": m // 8, "multibank": round(ma, 4), "twin": round(tw, 4)})
    return {"v": v, "d": d, "n_reps": n_reps, "rows": rows}


def summarize_b(b):
    print(f"\n=== PART B: two levers -- more-D vs sparse-code (multibank routing), FIXED D (V={b['v']}) ===")
    print("     D     M     flat  multibank  sparsity_gain")
    for r in b["rows"]:
        print(f"  {r['D']:>5d} {r['M']:>5d}  {r['flat']:>7.3f}   {r['multibank']:>7.3f}     {r['sparsity_gain']:>+7.3f}")
    gains = [r["sparsity_gain"] for r in b["rows"]]
    print(f"  => sparse-code (multibank) recovers up to {max(gains):+.3f} at FIXED D "
          f"=> SPARSITY is a lever DISTINCT from adding dimensions (p2's DG+CA3, not 'more D')")


def summarize_b2(b2):
    print(f"\n=== PART B2: multibank's OWN cliff (D={b2['d']}, push per-bank load) -- routing shifts the "
          f"cliff ~n_banks x, it is not immunity ===")
    print("     M   per_bank  multibank   twin")
    for r in b2["rows"]:
        print(f"  {r['M']:>5d}  {r['per_bank']:>7d}   {r['multibank']:>7.3f}  {r['twin']:>6.3f}")


def self_test():
    """Cheap fixtures pinning the mechanism (V=100, chance=0.01): (1) generous D + tiny load -> perfect;
    (2) small D + high load -> flat decode falls WELL below the low-load value (the cliff); (3) more D at
    the same load RECOVERS it (dimensionality is the lever for flat); (4) the info-free random-key twin is
    ~chance; (5) multibank at the same high load beats flat (routing lowers per-bank load = the sparse lever)."""
    v = 100
    perfect, _ = _one_cell(4096, 8, v, "flat", 20, 1)
    assert perfect > 0.98, f"generous D, load 8 must decode ~perfectly; got {perfect}"
    collapsed, twin = _one_cell(256, 64, v, "flat", 25, 1)
    assert collapsed < 0.75, f"high load at small D must fall off the plateau; got {collapsed}"
    recovered, _ = _one_cell(1024, 64, v, "flat", 25, 1)
    assert recovered - collapsed > 0.2, f"more D must recover the flat cliff; 256={collapsed} 1024={recovered}"
    assert twin < 0.06, f"info-free random-key twin must be ~chance (1/{v}=0.01); got {twin}"
    mb, _ = _one_cell(256, 64, v, "multibank", 25, 1)
    assert mb > collapsed + 0.1, f"multibank routing must beat flat at high load; flat={collapsed} mb={mb}"
    print(f"SELF-TEST PASS: flat(4096,M8)={perfect:.3f}  flat(256,M64)={collapsed:.3f} -> flat(1024,M64)={recovered:.3f} "
          f"(more-D recovers); twin={twin:.3f}(chance {1/v:.3f}); multibank(256,M64)={mb:.3f}>{collapsed:.3f} (sparse lever)")


def main():
    quick = "--quick" in sys.argv
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    a = part_a(quick=quick)
    sa = summarize_a(a)
    b = part_b(quick=quick)
    summarize_b(b)
    b2 = part_b2_multibank_cliff(quick=quick)
    summarize_b2(b2)
    os.makedirs(OUTDIR, exist_ok=True)
    out = {"anchor": "dim_phase_diagram_register_v1", "seed": SEED, "quick": quick,
           "part_a": a, "part_a_summary": sa, "part_b": b, "part_b2": b2,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUTDIR, "metrics_quick.json" if quick else "metrics.json"), "w",
              encoding="utf-8", newline="") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote {OUTDIR}  (elapsed {out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
