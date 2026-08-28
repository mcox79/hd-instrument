"""exp_register_divisive_norm_v1 -- the brain-faithful bundle NORMALIZATION for a superposition register.

PROBLEM: the_register_bundle_renorm_breaks_the_serial_readout.

STARTING MEASUREMENT (on disk, exp_register_completion_readout_v1): the theta-gamma SERIAL decode-and-suppress
readout recovers the overloaded register on the RAW linear sum (serial_rawsum 0.983 @M=64) but COLLAPSES on the
register's stored trace (serial_renorm 0.119). The stored trace differs by ONE thing: the organ's bundle applies a
PER-COMPONENT renorm S_i/|S_i| (hdlab.bundling.bundle, the FHRR unit-torus projection). That is a non-invertible,
per-component distortion -- it destroys the linear/additive structure the serial residual-subtraction needs.

BRAIN (PINNED, Carandini & Heeger 2012; Turrigiano 2008): a cortical/hippocampal population SUMS its inputs (linear
superposition on the dendrite) and controls magnitude by DIVISIVE NORMALIZATION -- dividing the summed response by a
POOLED gain (one scalar over the normalization pool), and by homeostatic synaptic SCALING (a slow global multiplicative
rescale toward a target activity). BOTH are POOLED / SCALAR gains. A scalar divisor is a GLOBAL rescaling: it preserves
the relative/linear structure exactly, so the strongest component stays largest and suppress-and-repeat still works. The
PER-COMPONENT renorm is the one member of the family that is NOT the brain's op -- it divides each dimension by its own
magnitude, which is a nonlinear projection with no biological analogue for a stored superposition (its only role is
torus-closure for RE-BINDING an atom, and a register trace is never re-bound; it is a terminal readout).

THE FIX = TWO MATCHED POOLED-NORMALIZATION STEPS (the brain applies divisive normalization at BOTH store and readout):
  STORE  : bundle -> S / g_pooled  (g = a scalar: L2 / RMS / Carandini-Heeger pooled / homeostatic-target), NOT S_i/|S_i|.
  READOUT: theta-gamma serial decode-and-suppress with POOLED GAIN CONTROL -- estimate ONE scalar gain matching the
           trace to the current reconstruction (least squares), then subtract the gain-matched other-slot estimates.
A scalar store-norm + a gain-matched readout is SCALE-EQUIVARIANT: it reads any scalar-normalized store identically to
the raw sum. The argmax cleanup is already SCALE-INVARIANT, so a scalar store-norm gives the argmax path IDENTICAL
decisions to the raw sum (>= the per-component organ; prior the_core_binding_operator_may_not_be_brain_faithful:
L2/raw-sum beat per-component 32/32, wins zero). => ONE divisive normalization serves BOTH readouts; no raw-sum shadow.

ARMS (normalization of the SAME stored bindings, then read by the SAME readouts -- one-variable store-norm swap):
  rawsum       -- S (g=1). The linear-structure reference (but magnitude is UNBOUNDED in M -> not a legit stored state).
  percomp      -- S_i/|S_i|. THE INCUMBENT organ (hdlab.bundling default). POSITIVE CONTROL: breaks the serial readout.
  l2           -- S/||S||           (whole-vector; pooled scalar).
  rms          -- S/RMS(S)          (pooled scalar; RMS = ||S||/sqrt(d)).
  divnorm      -- S/(sigma+mean|S|)  (Carandini-Heeger pooled, n=1; sigma = semi-saturation, SWEPT not adopted).
  homeostatic  -- S*target/RMS(S)   (Turrigiano synaptic scaling toward a target RMS; target SWEPT).
READOUTS:
  argmax        -- per-slot argmax cleanup (the organ's decode; scale-INVARIANT -> same for every scalar norm).
  serial_pooled -- theta-gamma serial with POOLED gain control (scale-EQUIVARIANT; the faithful readout).
  serial_naive  -- the raw-sum serial with NO gain control (E1.decode_serial). Shows a scaled store needs a gain-matched
                   readout: naive serial FAILS on l2/divnorm (trace scale != reconstruction scale) -- store & readout
                   normalization must MATCH. On percomp it is the 0.119 break; on rawsum it is the 0.983 reference.
TWIN (info-free): serial_pooled on a scalar-normalized store with SHUFFLED keys -> must LOSE CI-separated.

CAN-FAIL: if serial_pooled on a divisively-normalized store does NOT recover over the per-component store, the renorm is
not the cause (a valuable negative). If a scalar norm regresses the argmax path, divisive normalization does not serve
both readouts and a raw-sum shadow copy is required (the brief's principled either/or).

D FIXED (=256). Lightweight complex matmuls -> runs inline. ASCII only. Writes ONLY to data/exp_register_divisive_norm_v1/.
NO hdlab write (solver scope: propose the hdlab diff in SOLVED.md; strategy lands it, Q111).

Run:  .venv/Scripts/python.exe experiments/exp_register_divisive_norm_v1.py [--self-test | --full | --sweep]
# KB_REFERENT: (none -- fully synthetic, controlled-load)
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

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
# Reuse the PARENT readout cell's primitives verbatim so the rawsum reference is byte-identical to the landed result.
import experiments.exp_register_completion_readout_v1 as E1  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_divisive_norm_v1")
SEED = 20260828
D = 256          # FIXED dimensionality -- the fix must work WITHOUT raising D
V = 100          # filler (role) vocabulary; chance = 1/V = 0.01

NORMS = ["rawsum", "percomp", "l2", "rms", "divnorm", "homeostatic"]
SCALAR_NORMS = ["rawsum", "l2", "rms", "divnorm", "homeostatic"]   # everything EXCEPT per-component


# --------------------------------------------------------------------------------------------------
# The normalization family. Every member operates on the RAW linear superposition S = sum_s b_s.
# All are POOLED / SCALAR divisions EXCEPT `percomp`, which divides each component by its OWN magnitude.
# --------------------------------------------------------------------------------------------------
def apply_norm(S: torch.Tensor, kind: str, sigma: float = 1.0, target_rms: float = 1.0) -> torch.Tensor:
    """Normalize the raw superposition S (complex64, (d,)) by one member of the divisive-normalization family."""
    if kind == "rawsum":
        return S
    if kind == "percomp":                                   # THE INCUMBENT: per-component unit-torus (hdlab.bundling)
        mag = S.abs().clamp_min(1e-12)
        return S / mag.to(S.dtype)
    if kind == "l2":                                        # whole-vector L2 (pooled scalar)
        n = S.norm().clamp_min(1e-12)
        return S / n.to(S.dtype)
    if kind == "rms":                                       # pooled scalar; RMS = ||S||/sqrt(d)
        rms = torch.sqrt(torch.mean(S.abs() ** 2)).clamp_min(1e-12)
        return S / rms.to(S.dtype)
    if kind == "divnorm":                                   # Carandini-Heeger pooled (n=1): S/(sigma + mean|S|)
        pooled = torch.mean(S.abs())
        return S / (float(sigma) + pooled).clamp_min(1e-12).to(S.dtype)
    if kind == "homeostatic":                               # Turrigiano synaptic scaling toward target RMS
        rms = torch.sqrt(torch.mean(S.abs() ** 2)).clamp_min(1e-12)
        return S * (float(target_rms) / rms).to(S.dtype)
    raise ValueError(f"unknown norm {kind!r}")


# --------------------------------------------------------------------------------------------------
# The brain-faithful readout: theta-gamma serial decode-and-suppress WITH pooled gain control.
# --------------------------------------------------------------------------------------------------
def _pooled_gain(trace: torch.Tensor, total: torch.Tensor) -> torch.Tensor:
    """Least-squares complex scalar g minimizing ||total - g*trace||^2 = <trace,total>/<trace,trace>.
    total ~ sum of unit reconstructions; g*trace then lands on the reconstruction scale so the linear
    residual subtraction isolates one slot. This IS a pooled divisive-normalization step at readout
    (one scalar over the whole vector) -- the same op-class as the store norm, by design."""
    num = torch.sum(torch.conj(trace) * total)
    den = torch.sum(torch.conj(trace) * trace)
    if float(den.real) <= 1e-12:
        return torch.ones((), dtype=trace.dtype)
    return num / den


def decode_serial_pooled(trace, keys, role_mat, n_iter=6, order_by_conf=True):
    """Theta-gamma SERIAL decode-and-suppress, made SCALE-EQUIVARIANT by pooled gain control.

    Identical to E1.decode_serial EXCEPT each iteration re-estimates ONE scalar gain g matching the trace
    to the current reconstruction and subtracts gain-matched estimates. On the raw sum g~=1 -> reduces to
    E1.decode_serial (verified: it TIES serial_rawsum). On any scalar-normalized store g~=the stored scale
    -> reads it identically. On the per-component store NO single scalar g matches (the distortion is
    per-component) -> the residual stays contaminated and the readout fails (the positive control)."""
    m = len(keys)
    est = E1.decode_argmax(trace, keys, role_mat)          # scale-invariant init
    for _ in range(n_iter):
        recon = [binding.bind(role_mat[est[s]], keys[s]) for s in range(m)]
        total = recon[0].clone()
        for s in range(1, m):
            total = total + recon[s]
        g = _pooled_gain(trace, total)
        gtrace = g * trace                                 # trace lifted onto the reconstruction scale
        if order_by_conf:
            order = sorted(range(m),
                           key=lambda s: -E1._margin(binding.unbind(gtrace - (total - recon[s]), keys[s]), role_mat))
        else:
            order = list(range(m))
        changed = False
        for s in order:
            residual = gtrace - (total - recon[s])         # suppress the OTHER slots' gain-matched estimates
            new = E1._argmax(binding.unbind(residual, keys[s]), role_mat)
            if new != est[s]:
                total = total - recon[s]
                recon[s] = binding.bind(role_mat[new], keys[s])
                total = total + recon[s]
                est[s] = new
                changed = True
        if not changed:
            break
    return est


# --------------------------------------------------------------------------------------------------
# One overloaded entity on the LIVE register; read every slot with each (norm x readout).
# --------------------------------------------------------------------------------------------------
def _one_entity(d, m, v, seed, sigma=1.0, target_rms=1.0, n_iter=6):
    g = E1._gen(seed)
    role_vocab = [f"r{i}" for i in range(v)]
    reg = AccumulateRegister(role_vocab, d, g, max_event_slots=m)
    role_mat = torch.stack([reg.role_vecs[r] for r in role_vocab], dim=0)   # (V,d) the organ's own codebook
    keys = [reg.idx_vecs[s] for s in range(m)]                              # the organ's own event-slot keys

    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    ent = "e"
    for s in range(m):
        reg.add_event(ent, role_vocab[truth[s]], s)

    S = torch.stack(reg._events[ent], dim=0).sum(dim=0)                     # raw linear superposition
    # sanity: the organ's register() IS the per-component renorm of S (recency==0 default)
    percomp_check = S / S.abs().clamp_min(1e-12).to(S.dtype)
    assert torch.allclose(reg.register(ent), percomp_check, atol=1e-4), "register() != per-component renorm (recency?)"

    perm = list(np.random.default_rng(seed + 99).permutation(m))
    shuf_keys = [keys[perm[i]] for i in range(m)]

    traces = {kind: apply_norm(S, kind, sigma=sigma, target_rms=target_rms) for kind in NORMS}
    out = {}
    # argmax on every norm (scale-invariant on the scalar norms; the organ on percomp)
    for kind in NORMS:
        pred = E1.decode_argmax(traces[kind], keys, role_mat)
        out[f"argmax::{kind}"] = [int(pred[s] == truth[s]) for s in range(m)]
    # serial_pooled (faithful readout) on every norm
    for kind in NORMS:
        pred = decode_serial_pooled(traces[kind], keys, role_mat, n_iter=n_iter)
        out[f"serial::{kind}"] = [int(pred[s] == truth[s]) for s in range(m)]
    # serial_naive (no gain control) on rawsum/percomp/l2 -- shows store & readout norm must MATCH
    for kind in ["rawsum", "percomp", "l2"]:
        pred = E1.decode_serial(traces[kind], keys, role_mat, n_iter=n_iter)
        out[f"serialnaive::{kind}"] = [int(pred[s] == truth[s]) for s in range(m)]
    # info-free twin: faithful readout on a scalar store with shuffled keys
    pred = decode_serial_pooled(traces["rms"], shuf_keys, role_mat, n_iter=n_iter)
    out["twin"] = [int(pred[s] == truth[s]) for s in range(m)]
    return out


ARMS = ([f"argmax::{k}" for k in NORMS] + [f"serial::{k}" for k in NORMS]
        + [f"serialnaive::{k}" for k in ["rawsum", "percomp", "l2"]] + ["twin"])


def _cell(d, m, v, n_reps, seed, sigma=1.0, target_rms=1.0, n_iter=6, n_boot=2000):
    per_rep = {a: [] for a in ARMS}
    for rep in range(n_reps):
        res = _one_entity(d, m, v, seed + rep * 7919, sigma=sigma, target_rms=target_rms, n_iter=n_iter)
        for a in ARMS:
            per_rep[a].append(float(np.mean(res[a])))
    out = {}
    for a in ARMS:
        mean, lo, hi, hw = E1._boot_ci(per_rep[a], n_boot=n_boot, seed=seed + 5)
        out[a] = {"acc": round(mean, 4), "lo": round(lo, 4), "hi": round(hi, 4), "hw": round(hw, 4)}
    # HEADLINE: faithful serial on the divisive-normalized store vs on the per-component store (one-variable store swap).
    out["paired_divnorm_vs_percomp_serial"] = E1._paired(per_rep, "serial::divnorm", "serial::percomp", n_boot, seed + 7)
    # end-to-end gain over the CURRENT organ (argmax on the per-component renorm).
    out["paired_divnorm_serial_vs_organ"] = E1._paired(per_rep, "serial::divnorm", "argmax::percomp", n_boot, seed + 8)
    # divisive serial vs the raw-sum ceiling (should TIE -- scalar norms are equivalent under gain-matching).
    out["paired_divnorm_vs_rawsum_serial"] = E1._paired(per_rep, "serial::divnorm", "serial::rawsum", n_boot, seed + 9)
    # ARGMAX NO-REGRESSION: scalar-norm argmax vs the per-component organ argmax (>= per the 32/32 prior).
    out["paired_argmax_divnorm_vs_percomp"] = E1._paired(per_rep, "argmax::divnorm", "argmax::percomp", n_boot, seed + 10)
    out["twin_null_p95"] = round(float(np.percentile(np.asarray(per_rep["twin"]), 95)), 4)
    return out


def run(n_reps=30, n_iter=6):
    m_grid = [8, 16, 32, 48, 64, 96, 128]
    rows = {m: _cell(D, m, V, n_reps, SEED, n_iter=n_iter) for m in m_grid}
    return {"anchor": "register_divisive_norm_v1", "d": D, "v": V, "chance": round(1.0 / V, 4),
            "n_reps": n_reps, "n_iter": n_iter, "m_grid": m_grid, "rows": rows}


# --------------------------------------------------------------------------------------------------
# The DEFAULT backend: MultiBankAccumulateRegister. decode() routes each event to ONE bank and reads
# that BANK's bundle (bundling.bundle = per-component renorm) at a smaller per-bank load. So the fix
# must be shown ON THE DEFAULT BACKEND, in the COMPOSE regime (sparse store distributes load -> the
# norm fix + serial readout recovers each overloaded bank). This is why the problem matters (brief 2).
# --------------------------------------------------------------------------------------------------
def _one_entity_multibank(d, m, v, seed, n_banks=8, n_iter=6):
    """One entity with m events on the LIVE MultiBankAccumulateRegister (the make_situation_register default).
    Read each bank's bundle with (norm x readout); aggregate per-slot correctness across banks."""
    from collections import defaultdict
    from hdlab.situation_model_multibank import MultiBankAccumulateRegister, stable_bank_id
    g = E1._gen(seed)
    role_vocab = [f"r{i}" for i in range(v)]
    reg = MultiBankAccumulateRegister(role_vocab, d, g, max_event_slots=m, n_banks=n_banks)
    role_mat = torch.stack([reg.role_vecs[r] for r in role_vocab], dim=0)
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    for s in range(m):
        reg.add_event("e", role_vocab[truth[s]], s)

    bank_slots = defaultdict(list)
    for s in range(m):
        bank_slots[stable_bank_id(s, n_banks)].append(s)

    out = {"argmax_percomp": [], "serial_percomp": [], "serial_divnorm": [], "argmax_divnorm": []}
    max_bank = 0
    for bank_id, slots in bank_slots.items():
        events = reg._events["e"][bank_id]          # bound vecs, add-order == slot-order within the bank
        max_bank = max(max_bank, len(slots))
        keys = [reg.idx_vecs[s] for s in slots]
        gold = [truth[s] for s in slots]
        S = torch.stack(events, dim=0).sum(dim=0)
        percomp = S / S.abs().clamp_min(1e-12).to(S.dtype)
        divnorm = apply_norm(S, "divnorm")
        for arm, trace, dec in [("argmax_percomp", percomp, E1.decode_argmax),
                                ("argmax_divnorm", divnorm, E1.decode_argmax),
                                ("serial_percomp", percomp, decode_serial_pooled),
                                ("serial_divnorm", divnorm, decode_serial_pooled)]:
            pred = dec(trace, keys, role_mat) if dec is E1.decode_argmax else dec(trace, keys, role_mat, n_iter=n_iter)
            out[arm].extend([int(pred[i] == gold[i]) for i in range(len(slots))])
    return out, max_bank


def multibank_cell(d, m, v, n_reps, seed, n_banks=8, n_iter=6, n_boot=2000):
    ARMS_MB = ["argmax_percomp", "argmax_divnorm", "serial_percomp", "serial_divnorm"]
    per_rep = {a: [] for a in ARMS_MB}
    max_bank = 0
    for rep in range(n_reps):
        res, mb = _one_entity_multibank(d, m, v, seed + rep * 7919, n_banks=n_banks, n_iter=n_iter)
        max_bank = max(max_bank, mb)
        for a in ARMS_MB:
            per_rep[a].append(float(np.mean(res[a])))
    out = {"n_banks": n_banks, "max_bank_load": max_bank}
    for a in ARMS_MB:
        mean, lo, hi, hw = E1._boot_ci(per_rep[a], n_boot=n_boot, seed=seed + 5)
        out[a] = {"acc": round(mean, 4), "lo": round(lo, 4), "hi": round(hi, 4), "hw": round(hw, 4)}
    out["paired_serial_divnorm_vs_percomp"] = E1._paired(per_rep, "serial_divnorm", "serial_percomp", n_boot, seed + 7)
    out["paired_argmax_divnorm_vs_percomp"] = E1._paired(per_rep, "argmax_divnorm", "argmax_percomp", n_boot, seed + 8)
    return out


def multibank_probe(n_reps=15, n_iter=6):
    """PROVE the fix on the DEFAULT backend in the COMPOSE regime: high total load M distributed across n_banks=8
    so each bank is itself overloaded (k_per_bank ~ M/8). The norm fix must recover the per-bank serial readout."""
    rows = {}
    for m in [128, 384]:
        rows[m] = multibank_cell(D, m, V, n_reps, SEED, n_banks=8, n_iter=n_iter)
    print(f"\n=== DEFAULT backend (MultiBankAccumulateRegister, n_banks=8): the norm fix in the COMPOSE regime ===")
    print("   M(total)  k_per_bank | argmax:percomp argmax:divnorm | serial:percomp serial:divnorm | [serial divnorm-percomp CI]")
    for m in [128, 384]:
        r = rows[m]
        p = r["paired_serial_divnorm_vs_percomp"]
        print(f"   {m:>4d}      {r['max_bank_load']:>3d}       | {r['argmax_percomp']['acc']:.3f}          "
              f"{r['argmax_divnorm']['acc']:.3f}        | {r['serial_percomp']['acc']:.3f}          "
              f"{r['serial_divnorm']['acc']:.3f}        | {p['mean']:+.3f} [{p['lo']:+.3f},{p['hi']:+.3f}] hw{p['hw']:.3f}")
    print("  READING: on the DEFAULT multibank backend the norm fix recovers the per-bank serial readout CI-sep over the "
          "per-component renorm AND does not regress the argmax path -- the store lever (p2) and the norm fix COMPOSE.")
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "multibank_probe.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(rows, fh, indent=2)
    return 0


def summarize(res):
    print(f"\n=== brain-faithful bundle NORMALIZATION for the register (D={res['d']} FIXED, V={res['v']}, "
          f"chance={res['chance']}, n_reps={res['n_reps']}, serial n_iter={res['n_iter']}) ===")
    print("  READ: serial_pooled on a POOLED/SCALAR-normalized store recovers overload like the raw sum; the "
          "per-component renorm store is the one that breaks it (even under the best readout).")
    print("\n   M | argmax:percomp(organ) argmax:divnorm | serial:percomp serial:rms serial:divnorm serial:rawsum | "
          "twin | [divnorm-percomp serial CI]")
    for m in res["m_grid"]:
        r = res["rows"][m]
        p = r["paired_divnorm_vs_percomp_serial"]
        print(f"  {m:>3d} | {r['argmax::percomp']['acc']:.3f}            {r['argmax::divnorm']['acc']:.3f}       | "
              f"{r['serial::percomp']['acc']:.3f}         {r['serial::rms']['acc']:.3f}      "
              f"{r['serial::divnorm']['acc']:.3f}        {r['serial::rawsum']['acc']:.3f}      | "
              f"{r['twin']['acc']:.3f} | {p['mean']:+.3f} [{p['lo']:+.3f},{p['hi']:+.3f}] hw{p['hw']:.3f}")
    # windows
    recover = [m for m in res["m_grid"] if res["rows"][m]["paired_divnorm_vs_percomp_serial"]["lo"] > 0]
    ties_raw = all(abs(res["rows"][m]["paired_divnorm_vs_rawsum_serial"]["mean"]) < 0.03 for m in res["m_grid"])
    no_regress = all(res["rows"][m]["paired_argmax_divnorm_vs_percomp"]["lo"] > -0.01 for m in res["m_grid"])
    twin_loses = all(res["rows"][m]["twin"]["hi"] < res["rows"][m]["serial::divnorm"]["lo"] for m in recover) if recover else False
    naive_needs_gain = all(res["rows"][m]["serialnaive::l2"]["acc"] < res["rows"][m]["serial::l2"]["acc"] - 0.1
                           for m in res["m_grid"] if res["rows"][m]["serial::l2"]["acc"] > 0.5)
    res["recovery_window_M"] = recover
    res["divnorm_ties_rawsum_all_M"] = bool(ties_raw)
    res["argmax_no_regression_all_M"] = bool(no_regress)
    res["twin_loses_in_window"] = bool(twin_loses)
    res["naive_serial_needs_gain_matching"] = bool(naive_needs_gain)
    print(f"\n  RECOVERY WINDOW (serial:divnorm > serial:percomp CI-sep): M={recover}")
    print(f"  divnorm~=rawsum(scalar norms equivalent under gain-match, all M)={ties_raw} ; "
          f"argmax NO-REGRESSION vs organ(all M)={no_regress} ; twin LOSES(in window)={twin_loses} ; "
          f"naive-serial-needs-gain(store&readout norm must match)={naive_needs_gain}")


def sweep_param(n_reps=30, m=64, n_iter=6):
    """PARAMETER SWEEP (copy the COMPUTATION, sweep the PARAMETER): the recovery must be a property of POOLED
    normalization, not of a tuned sigma/target. Because a gain-matched readout removes ANY global scalar, serial
    accuracy must be ~FLAT across the Carandini-Heeger semi-saturation sigma and the homeostatic target RMS."""
    grid = []
    for sigma in [0.0, 0.25, 1.0, 4.0, 16.0, 64.0]:
        acc = np.mean([np.mean(_one_entity(D, m, V, SEED + rep * 7919, sigma=sigma, n_iter=n_iter)["serial::divnorm"])
                       for rep in range(n_reps)])
        grid.append({"param": "divnorm_sigma", "value": sigma, "serial_acc": round(float(acc), 4)})
    for target in [0.1, 1.0, 10.0, 100.0]:
        acc = np.mean([np.mean(_one_entity(D, m, V, SEED + rep * 7919, target_rms=target, n_iter=n_iter)["serial::homeostatic"])
                       for rep in range(n_reps)])
        grid.append({"param": "homeostatic_target_rms", "value": target, "serial_acc": round(float(acc), 4)})
    dn = [r["serial_acc"] for r in grid if r["param"] == "divnorm_sigma"]
    hm = [r["serial_acc"] for r in grid if r["param"] == "homeostatic_target_rms"]
    flat = (max(dn) - min(dn) < 0.03) and (max(hm) - min(hm) < 0.03)
    print(f"\n=== PARAMETER SWEEP (M={m}, D={D}): is recovery a property of POOLED normalization, not a tuned constant? ===")
    for r in grid:
        print(f"   {r['param']:>24s} = {r['value']:>7.2f} -> serial_acc {r['serial_acc']:.3f}")
    print(f"  => recovery FLAT across sigma AND target (gain-matching removes any scalar) = {flat}")
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "param_sweep.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump({"m": m, "d": D, "grid": grid, "flat_across_param": bool(flat)}, fh, indent=2)
    return 0


def self_test():
    # LOW load: the per-component store already lags the raw sum on serial (the renorm cost); scalar norms + faithful
    # readout are perfect and TIE the raw sum.
    lo = _cell(D, 8, V, 15, 1, n_boot=500)
    assert lo["serial::divnorm"]["acc"] > 0.98 and lo["serial::rms"]["acc"] > 0.98, f"low load scalar-norm serial perfect: {lo}"
    assert lo["serial::rawsum"]["acc"] > 0.98, f"low load raw-sum serial perfect: {lo}"
    # OVERLOAD: faithful serial on the divisive-normalized store RECOVERS CI-separated over the per-component store,
    # and TIES the raw-sum ceiling; the per-component store is the one that breaks it.
    hi = _cell(D, 64, V, 25, 1, n_boot=800)
    p = hi["paired_divnorm_vs_percomp_serial"]
    assert p["lo"] > 0.30, f"serial:divnorm must recover over serial:percomp CI-sep at overload; got {p}"
    assert hi["serial::divnorm"]["acc"] > 0.9, f"divnorm serial must recover overload; got {hi['serial::divnorm']}"
    assert hi["serial::percomp"]["acc"] < 0.4, f"per-component store must break serial (positive control); got {hi['serial::percomp']}"
    assert abs(hi["paired_divnorm_vs_rawsum_serial"]["mean"]) < 0.03, \
        f"divnorm serial must TIE raw-sum (scalar norms equivalent under gain-match); got {hi['paired_divnorm_vs_rawsum_serial']}"
    # ARGMAX NO-REGRESSION: scalar-norm argmax == raw-sum argmax (scale-invariant) and >= the per-component organ.
    ar = hi["paired_argmax_divnorm_vs_percomp"]
    assert ar["lo"] > -0.01, f"argmax must NOT regress vs the per-component organ; got {ar}"
    assert abs(hi["argmax::divnorm"]["acc"] - hi["argmax::rawsum"]["acc"]) < 1e-6, \
        f"scalar-norm argmax must be scale-invariant (== raw-sum argmax); got {hi['argmax::divnorm']} vs {hi['argmax::rawsum']}"
    # info-free twin loses; naive serial on a scaled store fails without gain-matching (store & readout norm must match).
    assert hi["twin"]["hi"] < hi["serial::divnorm"]["lo"], f"shuffled-key twin must LOSE CI-sep; got {hi}"
    assert hi["serialnaive::l2"]["acc"] < hi["serial::l2"]["acc"] - 0.1, \
        f"naive serial on L2 store must fail without gain-matching; got naive={hi['serialnaive::l2']} pooled={hi['serial::l2']}"
    print(f"SELF-TEST PASS: overload(M64) organ(argmax:percomp)={hi['argmax::percomp']['acc']:.3f} "
          f"serial:percomp={hi['serial::percomp']['acc']:.3f} serial:divnorm={hi['serial::divnorm']['acc']:.3f} "
          f"serial:rawsum={hi['serial::rawsum']['acc']:.3f} twin={hi['twin']['acc']:.3f} ; "
          f"divnorm-percomp={p['mean']:+.3f}[{p['lo']:+.3f},{p['hi']:+.3f}] ; "
          f"argmax no-regress lo={ar['lo']:+.3f} ; naive:l2={hi['serialnaive::l2']['acc']:.3f}<pooled:l2={hi['serial::l2']['acc']:.3f}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--multibank", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.sweep:
        return sweep_param()
    if args.multibank:
        return multibank_probe()
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
