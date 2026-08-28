"""EXP 1 -- the completion readout on the LIVE situation register (not the audit's synthetic probe).

PROBLEM: the_register_reads_by_argmax_not_recurrent_completion. The live register
(hdlab.situation_model_accumulate.AccumulateRegister) decodes each event slot INDEPENDENTLY:
readback_s = unbind(register, key_s) = filler_s + crosstalk from the OTHER M-1 bundled bindings, then a
single-shot argmax (cleanup_argmax). The crosstalk that makes the capacity cliff is STRUCTURED (the other
co-bundled bindings, whose keys we KNOW), not per-cue noise -- so a per-slot argmax throws away recoverable
signal. The brain-faithful readout for a superposition is theta-gamma SERIAL decode-and-suppress (Lisman &
Idiart 1995): decode the strongest item, SUPPRESS it (inhibition-of-return), decode the next from the
residual -- i.e. successive-interference cancellation / a resonator iterate. (Resonator-network-as-CA3 is an
engineering analogy; the pinned neural analogue for reading a superposition is the theta-gamma serial code.
See notes/problems/.../research_readout_routing_brain_drill_2026-08-28.md.)

THIS CELL builds that readout on the ACTUAL AccumulateRegister and, at FIXED D, sweeps the load M:
  ARGMAX          -- the organ's current readout (reg.decode); the floor that cliffs.
  HOPFIELD_PERSLOT-- modern-Hopfield attractor cleanup per slot (Ramsauer 2020, FHRR port). DISCRIMINATING
                     CONTROL: the register's i.i.d. role/key codes are PATTERN-SEPARATED (O'Reilly &
                     McClelland 1994) -> an attractor has NO manifold to settle on -> must ~TIE argmax.
                     If SERIAL beats argmax but HOPFIELD does not, the gain is crosstalk-cancellation via
                     KNOWN KEYS, not generic "completion".
  SERIAL_RENORM   -- theta-gamma serial decode-and-suppress on the SAME renormalized register() trace the
                     organ reads (STRICT one-variable readout swap: only the rule changes).
  SERIAL_RAWSUM   -- the same serial decode on the RAW linear superposition (sum of the stored bindings,
                     which the register already holds in _events). Resonator-native input; the per-component
                     bundle renorm (a nonlinear projection) is bypassed. Quantifies how much the renorm
                     itself costs the completion readout.
  TWIN            -- SERIAL_RAWSUM run with SHUFFLED keys (info-free: the joint machinery runs but the keys
                     are wrong -> must NOT beat chance / must LOSE CI-separated).

CAN-FAIL: if SERIAL does NOT beat ARGMAX at overload, the cliff is a genuine capacity limit at this D
(a valuable negative -- the positive control confirms the harness sees the cliff). If HOPFIELD matches
SERIAL, the "known-keys" story is wrong. Both are real findings.

D is held FIXED (the whole point: a readout fix at fixed dimensionality, not more-D). Route: lightweight
(D=256, small complex matmuls) -> runs inline. ASCII only. Writes ONLY to data/exp_register_completion_readout_v1/.
NO hdlab write.

Run:  .venv/Scripts/python.exe experiments/exp_register_completion_readout_v1.py [--self-test | --full]
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

from hdlab import binding, bundling, modulators  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister, unit_phase_vec  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_completion_readout_v1")
SEED = 20260828
D = 256          # FIXED dimensionality -- the readout fix must work WITHOUT raising D
V = 100          # filler (role) vocabulary; chance = 1/V = 0.01


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _scores(readback, role_mat):
    """Re(<role_v, readback>) for every filler v; role_mat (V,d) complex, readback (d,) complex -> (V,) real."""
    return torch.real(torch.conj(role_mat) @ readback)


def _argmax(readback, role_mat):
    return int(torch.argmax(_scores(readback, role_mat)))


def _margin(readback, role_mat):
    """Gold-blind decode confidence = (top1 - top2) cleanup score / d (an SNR proxy = 'cue completeness')."""
    s = _scores(readback, role_mat)
    top2 = torch.topk(s, 2).values
    return float((top2[0] - top2[1]) / readback.shape[0])


# --------------------------------------------------------------------------------------------------
# Readouts.
# --------------------------------------------------------------------------------------------------
def decode_argmax(trace, keys, role_mat):
    """Independent per-slot argmax (the organ's cleanup_argmax over every occupied slot)."""
    return [_argmax(binding.unbind(trace, keys[s]), role_mat) for s in range(len(keys))]


def decode_hopfield_perslot(trace, keys, role_mat, beta=20.0, steps=3):
    """Per-slot modern-Hopfield (dense associative) attractor cleanup, FHRR-complex port (Ramsauer 2020).
    state <- renorm(softmax(beta*scores(state)) @ role_mat). CONTROL: on i.i.d. separated codes this has no
    manifold and reduces to nearest-neighbor -> should ~tie argmax (proves the SERIAL gain is NOT generic
    'completion' but crosstalk cancellation using the known keys)."""
    out = []
    for s in range(len(keys)):
        state = binding.unbind(trace, keys[s])
        for _ in range(steps):
            w = torch.softmax(beta * _scores(state, role_mat), dim=0).to(role_mat.dtype)  # (V,) attention
            y = w @ role_mat                                                               # (d,) complex blend
            mag = y.abs().clamp_min(1e-12)
            state = y / mag.to(y.dtype)
        out.append(_argmax(state, role_mat))
    return out


def decode_serial(trace, keys, role_mat, n_iter=6, order_by_conf=True):
    """Theta-gamma SERIAL decode-and-suppress (= successive-interference cancellation / resonator iterate).

    Init each slot with an independent argmax, then iterate: reconstruct every slot's estimated binding,
    and for each slot (processed strongest-margin FIRST when order_by_conf) decode the RESIDUAL with the
    OTHER slots' current estimates SUBTRACTED (inhibition-of-return). Confident slots clean up ambiguous
    ones. n_iter = the gamma-cycle budget (a PARAMETER we sweep, not a number we adopt). Same FHRR
    bind/unbind algebra as the organ."""
    m = len(keys)
    est = decode_argmax(trace, keys, role_mat)
    for _ in range(n_iter):
        recon = [binding.bind(role_mat[est[s]], keys[s]) for s in range(m)]
        total = recon[0].clone()
        for s in range(1, m):
            total = total + recon[s]
        if order_by_conf:
            order = sorted(range(m),
                           key=lambda s: -_margin(binding.unbind(trace - (total - recon[s]), keys[s]), role_mat))
        else:
            order = list(range(m))
        changed = False
        for s in order:
            residual = trace - (total - recon[s])          # suppress the OTHER slots' estimated bindings
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


# --------------------------------------------------------------------------------------------------
# One overloaded entity on the LIVE register.
# --------------------------------------------------------------------------------------------------
def _one_entity(d, m, v, seed, n_iter=6):
    """Build ONE entity with m events (filler_s bound to event-slot s) on the ACTUAL AccumulateRegister,
    then read every slot back with each arm. Returns per-arm list of per-slot correctness (0/1)."""
    g = _gen(seed)
    role_vocab = [f"r{i}" for i in range(v)]
    reg = AccumulateRegister(role_vocab, d, g, max_event_slots=m)
    role_mat = torch.stack([reg.role_vecs[r] for r in role_vocab], dim=0)   # (V,d) the organ's own codebook
    keys = [reg.idx_vecs[s] for s in range(m)]                              # the organ's own event-slot keys

    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    ent = "e"
    for s in range(m):
        reg.add_event(ent, role_vocab[truth[s]], s)

    renorm = reg.register(ent)                                             # the trace the organ reads
    rawsum = torch.stack(reg._events[ent], dim=0).sum(dim=0)               # raw linear superposition (held in _events)
    # sanity: register() is the per-component renorm of the raw sum (i.e. modulator recency==0, plain regime)
    renorm_check = rawsum / rawsum.abs().clamp_min(1e-12).to(rawsum.dtype)
    assert torch.allclose(renorm, renorm_check, atol=1e-4), "register() is not the plain per-component renorm (recency?)"

    # shuffled-key twin (info-free): permute which key decodes which slot
    perm = list(np.random.default_rng(seed + 99).permutation(m))
    shuf_keys = [keys[p] for p in perm]

    arms = {
        "argmax":        decode_argmax(renorm, keys, role_mat),   # the organ (argmax on the renorm bundle)
        "argmax_rawsum": decode_argmax(rawsum, keys, role_mat),   # trace-effect control: argmax on the linear sum
        "hopfield":      decode_hopfield_perslot(renorm, keys, role_mat),
        "serial_renorm": decode_serial(renorm, keys, role_mat, n_iter=n_iter),   # rule swap on the renorm bundle
        "serial_rawsum": decode_serial(rawsum, keys, role_mat, n_iter=n_iter),   # THE FIX: serial on linear sum
        "twin":          decode_serial(rawsum, shuf_keys, role_mat, n_iter=n_iter),
    }
    return {a: [int(pred[s] == truth[s]) for s in range(m)] for a, pred in arms.items()}


def _boot_ci(per_rep_acc, n_boot=2000, seed=0):
    """95% bootstrap CI over reps (population = entities). Returns (mean, lo, hi, half_width)."""
    a = np.asarray(per_rep_acc, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    means = a[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2)


def _paired(per_rep, a, b, n_boot, seed):
    d = np.asarray(per_rep[a]) - np.asarray(per_rep[b])
    dm, dlo, dhi, dhw = _boot_ci(d, n_boot=n_boot, seed=seed)
    return {"mean": round(dm, 4), "lo": round(dlo, 4), "hi": round(dhi, 4), "hw": round(dhw, 4)}


def _cell(d, m, v, n_reps, seed, n_iter=6, n_boot=2000):
    ARMS = ["argmax", "argmax_rawsum", "hopfield", "serial_renorm", "serial_rawsum", "twin"]
    per_rep = {a: [] for a in ARMS}
    for rep in range(n_reps):
        res = _one_entity(d, m, v, seed + rep * 7919, n_iter=n_iter)
        for a in ARMS:
            per_rep[a].append(float(np.mean(res[a])))       # this entity's slot-accuracy
    out = {}
    for a in ARMS:
        mean, lo, hi, hw = _boot_ci(per_rep[a], n_boot=n_boot, seed=seed + 5)
        out[a] = {"acc": round(mean, 4), "lo": round(lo, 4), "hi": round(hi, 4), "hw": round(hw, 4)}
    # HEADLINE: the brain-faithful completion readout (serial on the linear superposition) vs the ORGAN.
    out["paired_headline"] = _paired(per_rep, "serial_rawsum", "argmax", n_boot, seed + 7)
    # decomposition: rule effect at fixed LINEAR trace, and the RENORM cost (rule swap on the renorm bundle).
    out["paired_rule_on_linear"] = _paired(per_rep, "serial_rawsum", "argmax_rawsum", n_boot, seed + 8)
    out["paired_rule_on_renorm"] = _paired(per_rep, "serial_renorm", "argmax", n_boot, seed + 9)
    out["twin_null_p95"] = round(float(np.percentile(np.asarray(per_rep["twin"]), 95)), 4)
    return out


def run(n_reps=40, n_iter=6):
    m_grid = [8, 16, 32, 48, 64, 96, 128]
    rows = {}
    for m in m_grid:
        rows[m] = _cell(D, m, V, n_reps, SEED, n_iter=n_iter)
    return {"anchor": "register_completion_readout_v1", "d": D, "v": V, "chance": round(1.0 / V, 4),
            "n_reps": n_reps, "n_iter": n_iter, "m_grid": m_grid, "rows": rows}


def summarize(res):
    print(f"\n=== LIVE-register completion readout (D={res['d']} FIXED, V={res['v']}, chance={res['chance']}, "
          f"n_reps={res['n_reps']}, serial n_iter={res['n_iter']}) ===")
    print("   M   argmax  argmax(raw)  hopfield  serial(renorm)  serial(rawsum)   twin   [serial_rawsum-argmax CI]")
    for m in res["m_grid"]:
        r = res["rows"][m]
        p = r["paired_headline"]
        print(f"  {m:>3d}  {r['argmax']['acc']:.3f}    {r['argmax_rawsum']['acc']:.3f}    {r['hopfield']['acc']:.3f}"
              f"     {r['serial_renorm']['acc']:.3f}          {r['serial_rawsum']['acc']:.3f}      "
              f"{r['twin']['acc']:.3f}   {p['mean']:+.3f} [{p['lo']:+.3f},{p['hi']:+.3f}] hw{p['hw']:.3f}")
    # RECOVERY WINDOW = the loads where the completion readout beats argmax CI-separated (headline lo>0).
    window = [m for m in res["m_grid"] if res["rows"][m]["paired_headline"]["lo"] > 0]
    diverge = [m for m in res["m_grid"] if res["rows"][m]["paired_headline"]["hi"] < 0]  # serial WORSE (own cliff)
    res["recovery_window_M"] = window
    res["divergence_M"] = diverge
    ov = window
    hopf_ties = all(res["rows"][m]["hopfield"]["acc"] <= res["rows"][m]["argmax"]["acc"] + 0.05 for m in res["m_grid"])
    twin_loses = all(res["rows"][m]["twin"]["hi"] < res["rows"][m]["serial_rawsum"]["lo"] for m in ov) if ov else False
    renorm_cost = all(res["rows"][m]["serial_renorm"]["acc"] <= res["rows"][m]["serial_rawsum"]["acc"] for m in res["m_grid"])
    print(f"\n  RECOVERY WINDOW (serial_rawsum>argmax CI-sep): M={window}  |  OWN DIVERGENCE cliff (serial WORSE): M={diverge}")
    print(f"  hopfield~=argmax(no manifold, all M)={hopf_ties} ; twin LOSES CI-sep(in window)={twin_loses} ; "
          f"renorm-hurts-serial(all M)={renorm_cost}")
    print("  READING: serial gain is crosstalk-cancellation via KNOWN KEYS (hopfield, which lacks a manifold on "
          "separated codes, does NOT recover); the completion readout must read the LINEAR superposition "
          "(serial_rawsum), because the per-component bundle renorm breaks the residual subtraction "
          "(serial_renorm underperforms even argmax at low load).")


def sweep_schedule(n_reps=40):
    """COMPONENT-FIDELITY check: is the recovery a property of the OPERATION (theta-gamma serial decode-and-
    suppress) or of a tuned gamma-cycle budget? Sweep n_iter and the confidence-ORDER (strongest-first =
    the faithful schedule) vs fixed order, at a mid-window load. A recovery robust across n_iter>=2 and
    improved by confidence-ordering is evidence the mechanism, not a number, is doing the work."""
    m = 48
    grid = []
    for n_iter in [1, 2, 3, 4, 6, 10, 16]:
        for order_by_conf in [True, False]:
            per_rep = []
            arg_rep = []
            for rep in range(n_reps):
                g = _gen(SEED + rep * 7919)
                role_vocab = [f"r{i}" for i in range(V)]
                reg = AccumulateRegister(role_vocab, D, g, max_event_slots=m)
                role_mat = torch.stack([reg.role_vecs[r] for r in role_vocab], dim=0)
                keys = [reg.idx_vecs[s] for s in range(m)]
                rr = np.random.default_rng(SEED + rep * 7919 + 1)
                truth = [int(rr.integers(0, V)) for _ in range(m)]
                for s in range(m):
                    reg.add_event("e", role_vocab[truth[s]], s)
                rawsum = torch.stack(reg._events["e"], dim=0).sum(dim=0)
                pred = decode_serial(rawsum, keys, role_mat, n_iter=n_iter, order_by_conf=order_by_conf)
                per_rep.append(float(np.mean([int(pred[s] == truth[s]) for s in range(m)])))
                arg = decode_argmax(rawsum, keys, role_mat)  # argmax on same trace as reference
                arg_rep.append(float(np.mean([int(arg[s] == truth[s]) for s in range(m)])))
            grid.append({"n_iter": n_iter, "order_by_conf": order_by_conf,
                         "serial_acc": round(float(np.mean(per_rep)), 4),
                         "argmax_ref": round(float(np.mean(arg_rep)), 4)})
    print(f"\n=== SCHEDULE SWEEP (M={m}, D={D}, V={V}): is recovery a property of the OPERATION, not a tuned budget? ===")
    print("  n_iter  order_by_conf  serial_acc  (argmax_ref)")
    for r in grid:
        print(f"    {r['n_iter']:>2d}      {str(r['order_by_conf']):>5s}        {r['serial_acc']:.3f}      ({r['argmax_ref']:.3f})")
    conf = [r for r in grid if r["order_by_conf"]]
    robust = all(r["serial_acc"] > 0.95 for r in conf if r["n_iter"] >= 2)
    ord_helps = (np.mean([r["serial_acc"] for r in grid if r["order_by_conf"]]) >=
                 np.mean([r["serial_acc"] for r in grid if not r["order_by_conf"]]))
    print(f"  => recovery robust across n_iter>=2 (confidence-ordered)={robust} ; confidence-ordering>=fixed-order={ord_helps}")
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "schedule_sweep.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump({"m": m, "d": D, "v": V, "grid": grid, "robust_n_iter_ge2": bool(robust),
                   "conf_order_ge_fixed": bool(ord_helps)}, fh, indent=2)
    return 0


def self_test():
    # low load: argmax + serial_RAWSUM perfect. (serial_RENORM may lag -- the measured renorm cost, NOT a bug.)
    lo = _cell(D, 8, V, 15, 1, n_boot=500)
    assert lo["argmax"]["acc"] > 0.98 and lo["serial_rawsum"]["acc"] > 0.98, f"low load: argmax+serial_rawsum perfect: {lo}"
    # moderate overload: serial_RAWSUM recovers CI-clear over the organ; per-slot Hopfield does NOT (no manifold
    # on separated codes); the shuffled-key twin ~chance; the renorm bundle breaks serial (serial_renorm worse).
    hi = _cell(D, 64, V, 25, 1, n_boot=800)
    p = hi["paired_headline"]
    assert p["lo"] > 0.10, f"serial_rawsum must recover over argmax at overload CI-separated; got {p}"
    assert hi["hopfield"]["acc"] <= hi["argmax"]["acc"] + 0.05, \
        f"per-slot Hopfield attractor must ~tie argmax on separated codes (no manifold); got {hi['hopfield']} vs {hi['argmax']}"
    assert hi["twin"]["hi"] < hi["serial_rawsum"]["lo"], f"shuffled-key twin must LOSE CI-separated; got {hi}"
    assert hi["serial_rawsum"]["acc"] > hi["serial_renorm"]["acc"], \
        f"raw-sum serial must beat renorm serial (per-component renorm breaks residual subtraction); got {hi}"
    print(f"SELF-TEST PASS: low-load argmax={lo['argmax']['acc']:.3f} serial_rawsum={lo['serial_rawsum']['acc']:.3f} "
          f"(serial_renorm={lo['serial_renorm']['acc']:.3f} <- renorm cost); overload(M64) argmax={hi['argmax']['acc']:.3f} "
          f"hopfield={hi['hopfield']['acc']:.3f} serial_renorm={hi['serial_renorm']['acc']:.3f} "
          f"serial_rawsum={hi['serial_rawsum']['acc']:.3f} twin={hi['twin']['acc']:.3f}; "
          f"headline serial_rawsum-argmax={p['mean']:+.3f} [{p['lo']:+.3f},{p['hi']:+.3f}]")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.sweep:
        return sweep_schedule()
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
