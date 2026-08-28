"""EXP 2 -- LEVER SEPARATION: the READOUT fix vs p2's SPARSE-STORE fix vs BOTH, at FIXED D.

PROBLEM: the_register_reads_by_argmax_not_recurrent_completion, bar item 3. There are two DISTINCT
brain-faithful levers against the register's superposition-crosstalk cliff, and strategy needs to know what
each buys:
  * READOUT lever (THIS problem): swap the per-slot argmax for theta-gamma SERIAL decode-and-suppress on the
    linear superposition (exp_register_completion_readout_v1). Roughly DOUBLES the usable per-bundle load
    (argmax off-plateau ~M/2 -> serial ~M), but has its OWN divergence cliff at extreme overload.
  * STORE lever (p2, the_entity_store_is_a_dense_bundle_that_fans): route each entity's events across
    n_banks sub-bundles (hdlab.situation_model_multibank), so per-bank load = M/n_banks -> DIVIDES the
    crosstalk by n_banks. This is a STORE-STRUCTURE change, orthogonal to the readout rule.

They should COMPOSE MULTIPLICATIVELY: store divides load by n_banks; readout ~doubles per-bank capacity ->
combined usable load ~ 2 * n_banks * the flat-argmax capacity. D is held FIXED (dimensionality is ruled out
as the fix -- the audit already showed that).

FOUR arms at each total load M (D fixed):
  flat_argmax      -- the ORGAN (AccumulateRegister + argmax). Baseline that cliffs.
  flat_serial      -- READOUT-fix alone (serial on the flat linear superposition).
  multibank_argmax -- STORE-fix alone (MultiBankAccumulateRegister + per-bank argmax).
  multibank_serial -- BOTH (multibank store + serial decode WITHIN each bank).

CAN-FAIL / honest: flat_serial diverges past its window (computed only where meaningful); the interesting
claim is multibank_serial > multibank_argmax at the load where per-bank load itself reaches the argmax cliff.
Info-free twin (shuffled keys) is inherited from exp1's mechanism (measured there); here the discriminator is
the four-way lever comparison, so the control is the argmax arms themselves (the readout can only help where
crosstalk is the bottleneck; unique-key decode is 1.0 by construction, tested in p2).

D FIXED. Route: moderate (serial is O(per-bundle-load^2)); multibank keeps per-bank load small so it stays
light. ASCII only. Writes ONLY to data/exp_register_readout_vs_store_lever_v1/. NO hdlab write.

Run:  .venv/Scripts/python.exe experiments/exp_register_readout_vs_store_lever_v1.py [--self-test | --full]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from hdlab.situation_model_multibank import MultiBankAccumulateRegister, stable_bank_id  # noqa: E402
from experiments.exp_register_completion_readout_v1 import decode_argmax, decode_serial, _gen  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_readout_vs_store_lever_v1")
SEED = 20260828
D = 256
V = 100
N_BANKS = 8


def _decode_flat(reg, ent, m, role_mat, keys, arm, n_iter):
    rawsum = torch.stack(reg._events[ent], dim=0).sum(dim=0)
    if arm == "argmax":
        return decode_argmax(rawsum, keys, role_mat)
    return decode_serial(rawsum, keys, role_mat, n_iter=n_iter)


def _decode_multibank(reg, ent, event_idxs, role_mat, arm, n_iter):
    """Decode each event by routing to its bank; within a bank, argmax (per-slot) or serial (joint over the
    bank's events). Returns predicted role index per event_idx (aligned to event_idxs)."""
    # group event_idxs by bank
    banks = {}
    for e in event_idxs:
        banks.setdefault(stable_bank_id(e, reg.n_banks), []).append(e)
    pred = {}
    for bank_id, es in banks.items():
        raw = torch.stack(reg._events[ent][bank_id], dim=0).sum(dim=0)
        keys = [reg.idx_vecs[e] for e in es]
        if arm == "argmax":
            out = decode_argmax(raw, keys, role_mat)
        else:
            out = decode_serial(raw, keys, role_mat, n_iter=n_iter)
        for e, o in zip(es, out):
            pred[e] = o
    return [pred[e] for e in event_idxs]


def _one(d, m, v, seed, n_iter=6, do_flat_serial=True):
    """One entity with m events at distinct event-slots 0..m-1; decode every slot with all four arms."""
    g = _gen(seed)
    role_vocab = [f"r{i}" for i in range(v)]
    flat = AccumulateRegister(role_vocab, d, torch.Generator().manual_seed(int(seed) % (2**31)),
                              max_event_slots=m)
    # multibank shares the SAME role/idx vectors for a fair store-only comparison
    mb = MultiBankAccumulateRegister(role_vocab, d, torch.Generator().manual_seed(int(seed) % (2**31)),
                                     max_event_slots=m, n_banks=N_BANKS)
    role_mat = torch.stack([flat.role_vecs[r] for r in role_vocab], dim=0)
    # align idx vectors between the two stores (independent draws otherwise) by copying flat's into mb
    mb.role_vecs = flat.role_vecs
    mb.idx_vecs = flat.idx_vecs
    keys = [flat.idx_vecs[s] for s in range(m)]

    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    ent = "e"
    for s in range(m):
        flat.add_event(ent, role_vocab[truth[s]], s)
        mb.add_event(ent, role_vocab[truth[s]], s)

    out = {}
    fa = _decode_flat(flat, ent, m, role_mat, keys, "argmax", n_iter)
    out["flat_argmax"] = [int(fa[s] == truth[s]) for s in range(m)]
    if do_flat_serial:
        fs = _decode_flat(flat, ent, m, role_mat, keys, "serial", n_iter)
        out["flat_serial"] = [int(fs[s] == truth[s]) for s in range(m)]
    ma = _decode_multibank(mb, ent, list(range(m)), role_mat, "argmax", n_iter)
    out["multibank_argmax"] = [int(ma[s] == truth[s]) for s in range(m)]
    ms = _decode_multibank(mb, ent, list(range(m)), role_mat, "serial", n_iter)
    out["multibank_serial"] = [int(ms[s] == truth[s]) for s in range(m)]
    out["_max_bank_load"] = mb.max_bank_load(ent)
    return out


def _boot(per_rep, n_boot=2000, seed=0):
    a = np.asarray(per_rep, float)
    rng = np.random.default_rng(seed)
    means = a[rng.integers(0, len(a), size=(n_boot, len(a)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return round(float(a.mean()), 4), round(float(lo), 4), round(float(hi), 4)


def _cell(d, m, v, n_reps, seed, n_iter=6, flat_serial_cap=160):
    do_fs = m <= flat_serial_cap
    arms = ["flat_argmax", "flat_serial", "multibank_argmax", "multibank_serial"]
    per_rep = {a: [] for a in arms}
    bank_loads = []
    for rep in range(n_reps):
        r = _one(d, m, v, seed + rep * 7919, n_iter=n_iter, do_flat_serial=do_fs)
        for a in arms:
            if a in r:
                per_rep[a].append(float(np.mean(r[a])))
        bank_loads.append(r["_max_bank_load"])
    out = {"max_bank_load": int(round(float(np.mean(bank_loads))))}
    for a in arms:
        if per_rep[a]:
            mean, lo, hi = _boot(per_rep[a], seed=seed + 3)
            out[a] = {"acc": mean, "lo": lo, "hi": hi}
        else:
            out[a] = None
    return out


def run(n_reps=25):
    m_grid = [32, 64, 128, 256, 384, 512]
    rows = {}
    for m in m_grid:
        rows[m] = _cell(D, m, V, n_reps, SEED)
    return {"anchor": "register_readout_vs_store_lever_v1", "d": D, "v": V, "n_banks": N_BANKS,
            "chance": round(1.0 / V, 4), "n_reps": n_reps, "m_grid": m_grid, "rows": rows}


def summarize(res):
    print(f"\n=== LEVER SEPARATION (D={res['d']} FIXED, V={res['v']}, n_banks={res['n_banks']}, chance={res['chance']}) ===")
    print("    M  bank_load  flat_argmax  flat_serial  multibank_argmax  multibank_serial")
    for m in res["m_grid"]:
        r = res["rows"][m]
        def s(a):
            return f"{r[a]['acc']:.3f}" if r[a] else "  -  "
        print(f"  {m:>4d}   {r['max_bank_load']:>4d}     {s('flat_argmax')}        {s('flat_serial')}"
              f"        {s('multibank_argmax')}            {s('multibank_serial')}")
    print("\n  READING: store-fix (multibank) divides crosstalk by n_banks; readout-fix (serial) ~doubles per-"
          "bundle capacity; BOTH compose -- multibank_serial holds where multibank_argmax has begun to cliff "
          "(per-bank load past the argmax knee). Each lever is DISTINCT and at FIXED D.")


def self_test():
    # In the readout's RECOVERY window (M=64): each lever helps, both are best.
    r = _cell(D, 64, V, 15, 1, n_iter=6)
    fa, fs = r["flat_argmax"]["acc"], r["flat_serial"]["acc"]
    ma, ms = r["multibank_argmax"]["acc"], r["multibank_serial"]["acc"]
    assert fs > fa + 0.1, f"readout-fix alone must beat flat argmax at M=64; {fa}->{fs}"
    assert ma > fa + 0.1, f"store-fix alone must beat flat argmax at M=64; {fa}->{ma}"
    assert ms >= max(fs, ma) - 0.02, f"both should be >= each lever alone; flat_serial={fs} mb_argmax={ma} both={ms}"
    # At a HIGH load where per-bank load reaches the argmax knee, BOTH should beat store-fix alone.
    r2 = _cell(D, 384, V, 12, 1, n_iter=6, flat_serial_cap=0)  # skip flat_serial (diverged + expensive)
    ma2, ms2 = r2["multibank_argmax"]["acc"], r2["multibank_serial"]["acc"]
    assert ms2 > ma2, f"at high load both-levers must beat store-fix alone (per-bank overload); mb_argmax={ma2} both={ms2}"
    print(f"SELF-TEST PASS: M64 flat_argmax={fa:.3f} -> readout {fs:.3f} / store {ma:.3f} / both {ms:.3f}; "
          f"M384 (per-bank load {r2['max_bank_load']}) store {ma2:.3f} -> both {ms2:.3f}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
