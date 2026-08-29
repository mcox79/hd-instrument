"""the_register_write_path_has_a_hard_capacity_wall -- the WRITE-path capacity lever (leaky/recency write).

The reader's working-memory register (`hdlab.situation_model_accumulate.AccumulateRegister`) writes every event
into ONE flat running sum `S = S + bind(role, item)`. Past ~0.2-0.25*D events that superposition saturates and
recovery collapses for ALL events -- INCLUDING the most recent. The parent problem
(`read_terminal_bundle_stores_normalize_per_component_not_pooled`, W9/W10/W11) proved read-time normalization CANNOT
move this wall (capacity is set at WRITE). The brain does NOT flat-sum: sequential WM encoding uses an ASYMMETRIC/
LEAKY recency gain (new events partially suppress old), keeping recent context recoverable at ANY load (Warden &
Miller 2007 Cereb Cortex; Konecky, Smith & Olson 2017 J Neurophysiol -- MEASURED/PINNED-WEAK, a monotonic recency
gradient 66/45/39% newest/middle/oldest). This cell builds that write path and shows it lifts a capacity-bound
downstream task (recent-event recovery at high store load) CI-separated over the STRONGEST flat-write floor.

THE HONEST FLOOR: the flat sum is not just read by argmax. `decode_serial` (LANDED) recovers the RAW flat sum via
theta-gamma crosstalk cancellation to ~0.98 @ M=64 (D=256). So the floor is flat+SERIAL, not flat+argmax. The
crux probe (scratchpad) showed flat+serial ALSO collapses once M exceeds ~0.25*D (recent-4: 1.00@64 -> 0.25@128
-> 0.17@256 -> ~0@384+), while a leaky write holds recent-4 = 1.000 at every load to M=768. So the write mechanism
is a genuine capability lever OVER the strong readout, in exactly the book-scale regime where the brain uses
recency+consolidation rather than joint cancellation over hundreds of items.

ARMS (all read the same population, floors recomputed per population):
  FLAT_ARGMAX   : S=S+new, per-event argmax cleanup (the naive current path).
  FLAT_SERIAL   : S=S+new, decode_serial crosstalk-cancellation readout -- the STRONGEST flat floor (landed).
  LEAKY_ARGMAX  : S=(1-leak)*S+new (sweep leak), argmax cleanup -- the write-time asymmetric recency gain.
  LEAKY_ADAPTIVE: leak scales with buffer magnitude (divisive-normalization-like activity-adaptive suppression) --
                  the higher-fidelity FORM flagged by the salience-gate research drill; sweep the target.
  QUEUE         : keep only the last `cap` events (hard bounded buffer) -- the DISCRETE-slot form; used ONLY for
                  the graded-vs-step FORM-fidelity drill (W11: a continuous leak is more brain-faithful than a step).
  TWIN_SHUF     : read the leaky store at SHUFFLED keys (info-free) -> chance.

METRICS vs load N (swept into the extreme regime past D):
  recent-k recovery (the reader-relevant quantity), uniform recovery (shows the fundamental recent-vs-old trade),
  and the per-recency-POSITION recovery curve (graded vs step -- the primate-gradient FORM check).

Run:
  .venv/Scripts/python.exe experiments/exp_register_leaky_write_capacity_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_register_leaky_write_capacity_v1.py --run          # default = FULL
  .venv/Scripts/python.exe experiments/exp_register_leaky_write_capacity_v1.py --smoke
"""
from __future__ import annotations

import argparse
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import (  # noqa: E402
    unit_phase_vec, cleanup_argmax, decode_serial_slots,
)

D = 256                    # small enough that the sweep goes WELL past the flat-sum wall (~0.2-0.25*D)
V = 100                    # role vocabulary; chance = 1/V = 0.01
BASE_SEED = 20260829
RESULTS = os.path.join(REPO, "data", "exp_register_leaky_write_capacity_v1")


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


# ---------------------------------------------------------------------------------------------------
# The proposed hdlab diff, mirrored here (strategy lands the hdlab change; I build+validate in experiments/).
# A leaky write is the byte-identical flat sum at leak=0.0; leak>0 gives the asymmetric recency gain.
# Read the RAW (weighted) sum with argmax cleanup -- argmax is scale-invariant, and per-component renorm
# distorts direction (parent's measured rule), so the faithful recent readout is raw-sum argmax.
# ---------------------------------------------------------------------------------------------------
def _write_store(n, seed, form, leak=0.25, cap=8, target=8.0):
    """Accumulate n (role, slot-key) events; return (store_S, events_list, keys, role_mat, truth).

    form:
      flat            S = S + new                                   (leak=0; current write path)
      leaky           S = (1-leak) S + new                          (fixed asymmetric recency gain)
      leaky_adaptive  leak grows when |S| exceeds an effective-capacity target (divisive-norm-like)
      queue           keep only the last `cap` events               (discrete bounded buffer; step form)
    """
    g = _gen(seed)
    role_vecs = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(n)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(n)]
    S = torch.zeros(D, dtype=torch.complex64)
    events = []
    recent = []
    for j in range(n):
        add = binding.bind(role_vecs[truth[j]], keys[j])
        events.append(add)
        if form == "flat":
            S = S + add
        elif form == "leaky":
            S = (1.0 - leak) * S + add
        elif form == "leaky_adaptive":
            mag = float(S.abs().mean())
            aj = min(0.95, max(0.0, 1.0 - target / (mag + 1e-9))) if mag > target else 0.0
            S = (1.0 - aj) * S + add
        elif form == "queue":
            recent.append(add)
            recent = recent[-cap:]
            S = torch.stack(recent).sum(0)
        else:
            raise ValueError(form)
    return S, events, keys, torch.stack(role_vecs), truth


def _argmax_decode(S, keys, role_mat):
    """Per-event argmax cleanup, VECTORIZED: for each key unbind S then score the whole role codebook at once
    (Re(conj(role_mat) @ readback) -- the same cleanup as cleanup_argmax, /d omitted as argmax-invariant).
    Byte-equivalent argmax to the reference cleanup_argmax loop; ~100x faster (one matmul vs V python calls)."""
    conj_rm = torch.conj(role_mat)                       # (V, d)
    est = []
    for k in keys:
        rb = binding.unbind(S, k)                        # (d,)
        scores = torch.real(conj_rm @ rb)                # (V,)
        est.append(int(torch.argmax(scores)))
    return est


def _acc_recent(est, truth, k):
    k = min(k, len(truth))
    idx = range(len(truth) - k, len(truth))
    return sum(1 for i in idx if est[i] == truth[i]) / k


def _acc_uniform(est, truth):
    return sum(1 for a, b in zip(est, truth) if a == b) / len(truth)


# ---------------------------------------------------------------------------------------------------
# Bootstrap CI helpers (over independent trials -- each trial is a fresh register population).
# ---------------------------------------------------------------------------------------------------
def _boot_mean_ci(per_trial, n_boot, seed, lo=2.5, hi=97.5):
    a = np.asarray(per_trial, dtype=float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    means = a[idx].mean(axis=1)
    return float(a.mean()), float(np.percentile(means, lo)), float(np.percentile(means, hi))


def _boot_paired_ci(a_trials, b_trials, n_boot, seed, lo=2.5, hi=97.5):
    """Paired bootstrap of (a-b) over trials -> mean delta and CI. CI excluding 0 => CI-separated."""
    a = np.asarray(a_trials, float); b = np.asarray(b_trials, float)
    d = a - b
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    boot = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(boot, lo)), float(np.percentile(boot, hi))


# ---------------------------------------------------------------------------------------------------
# Main capacity sweep.
# ---------------------------------------------------------------------------------------------------
def capacity_sweep(loads, leak=0.25, recent_k=4, n_trials=30, n_boot=2000):
    rows = {}
    for n in loads:
        arms = {"flat_argmax": [], "flat_serial": [], "leaky_argmax": [],
                "leaky_adaptive": [], "twin_shuf": [],
                "flat_argmax_uni": [], "leaky_argmax_uni": []}
        for t in range(n_trials):
            seed = BASE_SEED + 131 * t + n
            Sf, ev_f, keys, rm, truth = _write_store(n, seed, "flat")
            Sl, ev_l, kl, rml, trl = _write_store(n, seed, "leaky", leak=leak)
            Sa, ev_a, ka, rma, tra = _write_store(n, seed, "leaky_adaptive")
            est_fa = _argmax_decode(Sf, keys, rm)
            est_la = _argmax_decode(Sl, kl, rml)
            est_aa = _argmax_decode(Sa, ka, rma)
            # strong floor: serial crosstalk cancellation on the RAW flat sum
            raw = torch.stack(ev_f).sum(0)
            est_fs = decode_serial_slots(raw, keys, rm, n_iter=6)
            # info-free twin: read the leaky store at shuffled keys
            rng = np.random.default_rng(seed + 7); perm = list(rng.permutation(n))
            est_tw = _argmax_decode(Sl, [kl[p] for p in perm], rml)
            arms["flat_argmax"].append(_acc_recent(est_fa, truth, recent_k))
            arms["flat_serial"].append(_acc_recent(est_fs, truth, recent_k))
            arms["leaky_argmax"].append(_acc_recent(est_la, trl, recent_k))
            arms["leaky_adaptive"].append(_acc_recent(est_aa, tra, recent_k))
            arms["twin_shuf"].append(_acc_recent(est_tw, trl, recent_k))
            arms["flat_argmax_uni"].append(_acc_uniform(est_fa, truth))
            arms["leaky_argmax_uni"].append(_acc_uniform(est_la, trl))
        row = {}
        for name, vals in arms.items():
            m, lo, hi = _boot_mean_ci(vals, n_boot, seed=BASE_SEED + n)
            row[name] = {"mean": round(m, 4), "ci": [round(lo, 4), round(hi, 4)],
                         "half": round((hi - lo) / 2, 4)}
        # paired lift vs the STRONGEST floor (flat_serial) and null p95 from the twin
        d, dlo, dhi = _boot_paired_ci(arms["leaky_argmax"], arms["flat_serial"], n_boot, BASE_SEED + 5 + n)
        row["lift_vs_flat_serial"] = {"delta": round(d, 4), "ci": [round(dlo, 4), round(dhi, 4)],
                                      "sep": bool(dlo > 0)}
        row["null_p95_twin"] = round(float(np.percentile(arms["twin_shuf"], 95)), 4)
        rows["n=%d" % n] = row
    return {"D": D, "V": V, "leak": leak, "recent_k": recent_k, "n_trials": n_trials,
            "n_boot": n_boot, "chance": 1.0 / V, "loads": list(loads), "rows": rows}


# ---------------------------------------------------------------------------------------------------
# Lambda sweep at a fixed high load: the recent-vs-old FRONTIER (the fundamental single-store trade).
# ---------------------------------------------------------------------------------------------------
def lambda_frontier(n=256, lams=(1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.6, 0.5), recent_k=4, n_trials=24):
    out = {}
    for lam in lams:
        rec, uni = [], []
        for t in range(n_trials):
            seed = BASE_SEED + 211 * t + n
            leak = 1.0 - lam
            S, ev, keys, rm, truth = _write_store(n, seed, "flat" if leak == 0 else "leaky", leak=leak)
            est = _argmax_decode(S, keys, rm)
            rec.append(_acc_recent(est, truth, recent_k))
            uni.append(_acc_uniform(est, truth))
        out["lam=%.2f" % lam] = {"recent": round(float(np.mean(rec)), 4),
                                 "uniform": round(float(np.mean(uni)), 4)}
    return {"n": n, "recent_k": recent_k, "frontier": out}


# ---------------------------------------------------------------------------------------------------
# FORM fidelity (W11 / the drill's graded-vs-step discriminator): the primate recency GRADIENT is
# GRADED/monotonic (intermediate positions), the discrete queue is a STEP. Report the curve.
# ---------------------------------------------------------------------------------------------------
def graded_vs_step(n=64, lam=0.75, cap=6, n_trials=40, max_pos=12, window=9):
    """lam=0.75 @N=64 gives a clean monotonic transition over the readable window (positions ~0-8):
    a smooth graded decline (the primate 66/45/39 recency-gradient SHAPE) vs the queue's hard STEP.
    Also reports a coarse 3-BIN (newest/middle/oldest third of the readable `window`) to compare
    directly to the primate newest>middle>oldest monotonic ordering (the shape, not the numbers)."""
    from collections import defaultdict
    leak_pos = defaultdict(list); queue_pos = defaultdict(list)
    for t in range(n_trials):
        seed = BASE_SEED + 313 * t + n
        Sl, evl, kl, rml, tl = _write_store(n, seed, "leaky", leak=1.0 - lam)
        Sq, evq, kq, rmq, tq = _write_store(n, seed, "queue", cap=cap)
        el = _argmax_decode(Sl, kl, rml); eq = _argmax_decode(Sq, kq, rmq)
        for j in range(n):
            p = n - 1 - j                     # 0 = newest
            if p < max_pos:
                leak_pos[p].append(int(el[j] == tl[j]))
                queue_pos[p].append(int(eq[j] == tq[j]))
    leak_curve = [round(float(np.mean(leak_pos[p])), 3) for p in range(max_pos)]
    queue_curve = [round(float(np.mean(queue_pos[p])), 3) for p in range(max_pos)]
    leak_inter = sum(1 for v in leak_curve if 0.15 <= v <= 0.85)   # graded => several intermediate positions
    queue_inter = sum(1 for v in queue_curve if 0.15 <= v <= 0.85)  # step => ~none
    # coarse 3-bin over the readable window (newest/middle/oldest third) -- the primate 66/45/39 analog
    b = window // 3
    def binmean(curve, a, z):
        return round(float(np.mean(curve[a:z])), 3)
    leak_bins = [binmean(leak_curve, 0, b), binmean(leak_curve, b, 2 * b), binmean(leak_curve, 2 * b, 3 * b)]
    queue_bins = [binmean(queue_curve, 0, b), binmean(queue_curve, b, 2 * b), binmean(queue_curve, 2 * b, 3 * b)]
    # monotonic non-increasing over the readable window (the primate gradient shape)
    mono = all(leak_curve[i] >= leak_curve[i + 1] - 0.06 for i in range(window - 1))
    leak_graded = leak_bins[0] > leak_bins[1] > leak_bins[2]      # strict newest>middle>oldest (graded)
    queue_step = (queue_bins[0] == queue_bins[1]) and (queue_bins[1] - queue_bins[2] > 0.5)  # flat then cliff
    return {"lam": lam, "cap": cap, "n": n, "window": window,
            "leak_curve": leak_curve, "queue_curve": queue_curve,
            "leak_3bin_newest_mid_oldest": leak_bins, "queue_3bin_newest_mid_oldest": queue_bins,
            "leak_intermediate_positions": leak_inter, "queue_intermediate_positions": queue_inter,
            "leak_monotonic_graded": bool(mono), "leak_is_graded": bool(leak_graded),
            "queue_is_step": bool(queue_step)}


# ---------------------------------------------------------------------------------------------------
# Positive control (the metric CAN move): a high-load register where a specific RECENT event query is
# recovered by the leaky write and MISSED by the flat sum (both argmax and serial). Paired, can-fail.
# ---------------------------------------------------------------------------------------------------
def positive_control(n=256, leak=0.25, n_trials=30):
    flat_hit = leaky_hit = 0
    for t in range(n_trials):
        seed = BASE_SEED + 417 * t
        Sf, evf, keys, rm, truth = _write_store(n, seed, "flat")
        Sl, evl, kl, rml, trl = _write_store(n, seed, "leaky", leak=leak)
        # query the SINGLE most-recent event (position n-1)
        j = n - 1
        vocab = {i: rm[i] for i in range(rm.shape[0])}
        fa = int(cleanup_argmax(binding.unbind(Sf, keys[j]), vocab)[0])
        # flat + serial too (strongest flat readout)
        raw = torch.stack(evf).sum(0)
        fs = decode_serial_slots(raw, keys, rm, n_iter=6)[j]
        la = int(cleanup_argmax(binding.unbind(Sl, kl[j]), {i: rml[i] for i in range(rml.shape[0])})[0])
        flat_ok = (fa == truth[j]) or (fs == truth[j])
        flat_hit += int(flat_ok)
        leaky_hit += int(la == trl[j])
    return {"n": n, "leak": leak, "n_trials": n_trials,
            "flat_recovers_newest": round(flat_hit / n_trials, 3),
            "leaky_recovers_newest": round(leaky_hit / n_trials, 3),
            "moves": bool(leaky_hit > flat_hit)}


# ---------------------------------------------------------------------------------------------------
def _self_test():
    # 1. capacity: at overload the leaky write beats flat+argmax AND flat+serial on recent recovery.
    n = 192
    Sf, evf, keys, rm, truth = _write_store(n, BASE_SEED, "flat")
    Sl, evl, kl, rml, trl = _write_store(n, BASE_SEED, "leaky", leak=0.25)
    fa = _acc_recent(_argmax_decode(Sf, keys, rm), truth, 4)
    fs = _acc_recent(decode_serial_slots(torch.stack(evf).sum(0), keys, rm, n_iter=6), truth, 4)
    la = _acc_recent(_argmax_decode(Sl, kl, rml), trl, 4)
    assert la > fa + 0.3, "leaky must beat flat+argmax on recent recovery at overload: %.3f vs %.3f" % (la, fa)
    assert la > fs + 0.3, "leaky must beat the STRONG floor flat+serial at overload: %.3f vs %.3f" % (la, fs)
    # 2. the fundamental trade: leaky UNIFORM recovery is worse than its recent recovery (old decays out).
    lu = _acc_uniform(_argmax_decode(Sl, kl, rml), trl)
    assert lu < la - 0.3, "leaky must decay OLD events (single-store trade): uniform %.3f vs recent %.3f" % (lu, la)
    # 3. info-free twin (shuffled keys) collapses.
    rng = np.random.default_rng(BASE_SEED + 7); perm = list(rng.permutation(n))
    tw = _acc_recent(_argmax_decode(Sl, [kl[p] for p in perm], rml), trl, 4)
    assert tw < la - 0.3, "twin (shuffled keys) must collapse: %.3f vs %.3f" % (tw, la)
    # 4. FORM: the leaky recency curve is graded/monotonic; the queue is a step.
    gv = graded_vs_step(n_trials=12)
    assert gv["leak_intermediate_positions"] > gv["queue_intermediate_positions"], \
        "leaky curve must be GRADED (more intermediate positions) vs the STEP queue: %r" % gv
    # 5. positive control moves.
    pc = positive_control(n_trials=12)
    assert pc["moves"], "positive control must move: %r" % pc
    print("[self-test] PASS  leaky_recent=%.3f > flat_argmax=%.3f, flat_serial=%.3f (overload N=%d); "
          "leaky_uniform=%.3f (old decays); twin=%.3f; graded_pos=%d vs step_pos=%d; pos_ctrl moves"
          % (la, fa, fs, n, lu, tw, gv["leak_intermediate_positions"], gv["queue_intermediate_positions"]))


def _print(res):
    r = res["capacity"]
    print("=== WRITE-path capacity: flat sum (argmax + STRONG serial floor) vs write-time leaky recency gain ===")
    print("  D=%d V=%d leak=%.2f recent_k=%d, %d trials, %d boot; chance=%.3f\n"
          % (r["D"], r["V"], r["leak"], r["recent_k"], r["n_trials"], r["n_boot"], r["chance"]))
    print("  RECENT-%d recovery (the reader-relevant quantity):" % r["recent_k"])
    print("  %-8s %-16s %-16s %-16s %-10s  lift vs flat_serial (CI)   null_p95" %
          ("load", "flat_argmax", "flat_SERIAL(floor)", "LEAKY_argmax", "twin"))
    for n in r["loads"]:
        row = r["rows"]["n=%d" % n]
        lift = row["lift_vs_flat_serial"]
        print("  %-8d %-16s %-16s %-16s %-10.3f  %+.3f [%+.3f,%+.3f] %-3s  %.3f" % (
            n, "%.3f" % row["flat_argmax"]["mean"], "%.3f" % row["flat_serial"]["mean"],
            "%.3f" % row["leaky_argmax"]["mean"], row["twin_shuf"]["mean"],
            lift["delta"], lift["ci"][0], lift["ci"][1], "SEP" if lift["sep"] else "ns",
            row["null_p95_twin"]))
    print("\n  The fundamental single-store trade (leaky buys RECENT by decaying OLD):")
    print("  %-8s %-18s %-18s" % ("load", "leaky_recent", "leaky_UNIFORM(all)"))
    for n in r["loads"]:
        row = r["rows"]["n=%d" % n]
        print("  %-8d %-18.3f %-18.3f" % (n, row["leaky_argmax"]["mean"], row["leaky_argmax_uni"]["mean"]))
    fr = res["frontier"]["frontier"]
    print("\n  LAMBDA frontier @N=%d (recent vs uniform):" % res["frontier"]["n"])
    for k, v in fr.items():
        print("    %-9s recent=%.3f  uniform=%.3f" % (k, v["recent"], v["uniform"]))
    gv = res["graded"]
    print("\n  FORM fidelity (graded primate 66/45/39 gradient vs discrete step); lam=%.2f cap=%d:" % (gv["lam"], gv["cap"]))
    print("    leaky  curve (0=newest): %s  intermediate=%d monotonic=%s"
          % (gv["leak_curve"][:10], gv["leak_intermediate_positions"], gv["leak_monotonic_graded"]))
    print("    queue  curve (0=newest): %s  intermediate=%d" % (gv["queue_curve"][:10], gv["queue_intermediate_positions"]))
    print("    leaky 3-bin newest/mid/oldest = %s (graded=%s) ; queue = %s (step=%s)"
          % (gv["leak_3bin_newest_mid_oldest"], gv["leak_is_graded"],
             gv["queue_3bin_newest_mid_oldest"], gv["queue_is_step"]))
    pc = res["positive_control"]
    print("\n  POSITIVE CONTROL @N=%d: leaky recovers newest %.3f vs flat(argmax|serial) %.3f -> moves=%s"
          % (pc["n"], pc["leaky_recovers_newest"], pc["flat_recovers_newest"], pc["moves"]))


def run(smoke=False):
    if smoke:
        loads = (16, 64, 256); n_trials, n_boot = 8, 500
        cap = capacity_sweep(loads, n_trials=n_trials, n_boot=n_boot)
        fr = lambda_frontier(n_trials=8)
        gv = graded_vs_step(n_trials=12)
        pc = positive_control(n_trials=10)
    else:
        loads = (16, 32, 64, 128, 256, 384, 512, 768)
        cap = capacity_sweep(loads, n_trials=30, n_boot=2000)
        fr = lambda_frontier(n_trials=24)
        gv = graded_vs_step(n_trials=40)
        pc = positive_control(n_trials=30)
    res = {"capacity": cap, "frontier": fr, "graded": gv, "positive_control": pc}
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "metrics.json"), "w") as f:
        json.dump(res, f, indent=2)
    _print(res)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    run(smoke=bool(args.smoke) or args.mode == "smoke")
