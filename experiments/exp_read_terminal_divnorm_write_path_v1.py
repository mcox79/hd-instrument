"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the WRITE/ENCODE-path limitation (the real gap).

The whole read_terminal family tested normalization only at the READ side of the register, and it came back mostly
null -- because at read time, once events are summed past the store's capacity, the information is already gone (a
read-time normalization cannot un-mix a saturated sum). Buschman, Siegel, Roy & Miller 2011 (PNAS 108:11252) MEASURED
that the brain's multi-item suppression happens at ENCODING, not readout. This cell asks whether that is a real
limitation of our `AccumulateRegister` write path: it accumulates a FLAT running sum (recency modulator OFF by
default), so every event has equal weight and the store degrades UNIFORMLY at overload -- it has no write-time gain
control to keep RECENT context recoverable past the raw-sum capacity wall.

THE MEASUREMENT (which read-time normalization provably CANNOT fix):
  Accumulate N events (role bound to a per-event slot key). Read back each event by unbind + argmax cleanup.
  Arms:
    RAW+ARGMAX     : flat running sum (the current write path), argmax read.
    RAW+DIVNORM    : flat running sum, gain-matched pooled read (the BEST read-terminal fix, already landed).
    LEAKY+ARGMAX   : WRITE-TIME leaky/suppressive accumulation S_j = (1-a) S_{j-1} + bind(role_j, key_j)
                     (the Buschman encoding-stage suppression analog; a>0 keeps the effective active set bounded).
  Metrics vs N (swept well past capacity):
    - UNIFORM recovery (all N events): raw-sum has a hard CAPACITY WALL; read-time divnorm does NOT move it.
    - RECENCY recovery (the most-recent k events -- what a reader actually needs): LEAKY keeps recent events
      recoverable at ANY total N, where RAW (any read norm) collapses -> graceful degradation vs a hard wall.
  Info-free twin: shuffled keys (read at the wrong slots) -> collapses to chance.

If LEAKY+ARGMAX preserves recent-event recovery past the N where RAW+DIVNORM has collapsed, then the write/encode
path is a real capacity lever that NO read-terminal normalization can provide -- the limitation strategy should solve.

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_write_path_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_write_path_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax  # noqa: E402

D = 256                 # small enough that N in the sweep goes WELL PAST the flat-sum capacity wall (~0.1-0.15*D)
V = 100                 # role vocabulary; chance = 1/V = 0.01
BASE_SEED = 20260829
N_TRIALS = 20


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


def _accumulate(n, seed, leak):
    """Accumulate n events; return (store, keys, role_mat, truth). leak=0 -> flat running sum (current write path);
    leak>0 -> write-time suppressive/leaky accumulation (Buschman encoding-stage suppression analog)."""
    g = _gen(seed)
    role_vecs = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(n)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(n)]
    S = torch.zeros(D, dtype=torch.complex64)
    for j in range(n):
        S = (1.0 - leak) * S + binding.bind(role_vecs[truth[j]], keys[j])
    return S, keys, torch.stack(role_vecs), truth


def _decode(S, keys, role_mat, norm=None):
    """Per-event argmax cleanup. norm='divnorm' applies the gain-matched pooled read (scale-invariant for argmax, so
    it does not change argmax -- included to SHOW read-time norm cannot move the raw-sum wall)."""
    read = S
    if norm == "divnorm":
        pooled = S.abs().mean().clamp_min(1e-12)
        read = S / pooled
    est = []
    for k in keys:
        rb = binding.unbind(read, k)
        best, _ = cleanup_argmax(rb, {i: role_mat[i] for i in range(role_mat.shape[0])})
        est.append(int(best))
    return est


def _acc_uniform(est, truth):
    return sum(1 for a, b in zip(est, truth) if a == b) / len(truth)


def _acc_recent(est, truth, k):
    """Recovery of the k MOST-RECENT events (the reader-relevant quantity)."""
    k = min(k, len(truth))
    idx = range(len(truth) - k, len(truth))
    return sum(1 for i in idx if est[i] == truth[i]) / k


# ---- FIDELITY DRILL: the write-gain FORM (my leak is a placeholder; Buschman's suppression is DIVISIVE) ----
def _accumulate_form(n, seed, form, a=0.25, cap=8, target=8.0):
    """Write-time gain-control VARIANTS, to test whether the FORM matters for the recency/capacity trade:
      flat            : S = S + new                                   (current write path; hard wall)
      leaky_fixed     : S = (1-a) S + new                             (fixed geometric decay -- my W9 model)
      leaky_adaptive  : leak scales with CURRENT load (suppress more when the store is fuller) -- closer to an
                        activity-dependent (Buschman divisive) suppression
      divnorm_write   : S = (S + new); then S = target * S / (mean|S|) each step -- a SYMMETRIC pooled divisive
                        rescale (bounds magnitude but preserves RELATIVE weights -> predicted NOT to create recency)
      queue           : keep only the last `cap` events (hard displacement / bounded buffer)
    """
    g = _gen(seed)
    role_vecs = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(n)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(n)]
    S = torch.zeros(D, dtype=torch.complex64)
    recent = []
    for j in range(n):
        add = binding.bind(role_vecs[truth[j]], keys[j])
        if form == "flat":
            S = S + add
        elif form == "leaky_fixed":
            S = (1.0 - a) * S + add
        elif form == "leaky_adaptive":
            # leak proportional to how far over an effective-capacity target the store magnitude sits
            mag = float(S.abs().mean())
            aj = min(0.9, max(0.0, 1.0 - target / (mag + 1e-9))) if mag > target else 0.0
            S = (1.0 - aj) * S + add
        elif form == "divnorm_write":
            S = S + add
            m = S.abs().mean().clamp_min(1e-12)
            S = (target * S / m).to(torch.complex64)
        elif form == "queue":
            recent.append(add)
            recent = recent[-cap:]
            S = torch.stack(recent).sum(0)
        else:
            raise ValueError(form)
    return S, keys, torch.stack(role_vecs), truth


def graded_vs_step_drill(n=64, lam=0.9, cap=6, n_trials=40, max_pos=16):
    """The research drill's graded-vs-discrete discriminator (Warden-Miller/Konecky recency gradient vs Luck-Vogel
    slots). At total load N (past capacity), measure recovery accuracy AS A FUNCTION OF RECENCY POSITION (0=newest)
    for a CONTINUOUS exponential leak (S=lam*S+event) vs a HARD bounded QUEUE (last-`cap` events). Literature predicts
    the continuous leak yields a GRADED monotonic decline (intermediate positions -> intermediate recovery, like
    66/45/39%), while the hard queue yields a STEP (perfect for positions < cap, chance for >= cap)."""
    from collections import defaultdict
    leak = defaultdict(list); queue = defaultdict(list)
    for t in range(n_trials):
        seed = BASE_SEED + 7 * t + n
        Sl, kl, rml, tl = _accumulate_form(n, seed, "leaky_fixed", a=1.0 - lam)
        Sq, kq, rmq, tq = _accumulate_form(n, seed, "queue", cap=cap)
        el = _decode(Sl, kl, rml); eq = _decode(Sq, kq, rmq)
        for j in range(n):
            p = n - 1 - j
            if p < max_pos:
                leak[p].append(int(el[j] == tl[j])); queue[p].append(int(eq[j] == tq[j]))
    leak_curve = [round(float(np.mean(leak[p])), 3) for p in range(max_pos)]
    queue_curve = [round(float(np.mean(queue[p])), 3) for p in range(max_pos)]
    # graded-vs-step classifier: count INTERMEDIATE positions (recovery in [0.2, 0.8]) -- a step function has ~none
    # (each position is ~1 or ~chance); a graded curve has several.
    leak_inter = sum(1 for v in leak_curve if 0.2 <= v <= 0.8)
    queue_inter = sum(1 for v in queue_curve if 0.2 <= v <= 0.8)
    return {"lam": lam, "cap": cap, "n": n, "leak_curve": leak_curve, "queue_curve": queue_curve,
            "leak_intermediate_positions": leak_inter, "queue_intermediate_positions": queue_inter}


def gain_form_drill(n=192, recent_k=4, n_trials=16):
    forms = ["flat", "leaky_fixed", "leaky_adaptive", "divnorm_write", "queue"]
    out = {}
    for form in forms:
        rec, uni = [], []
        for t in range(n_trials):
            S, keys, rm, truth = _accumulate_form(n, BASE_SEED + 100 * t + n, form)
            est = _decode(S, keys, rm)
            rec.append(_acc_recent(est, truth, recent_k))
            uni.append(_acc_uniform(est, truth))
        out[form] = {"recent": round(float(np.mean(rec)), 3), "uniform": round(float(np.mean(uni)), 3)}
    return {"n": n, "recent_k": recent_k, "forms": out}


def cell(loads=(8, 16, 32, 64, 128, 192, 256), leak=0.25, recent_k=4, n_trials=N_TRIALS):
    res = {"loads": list(loads), "leak": leak, "recent_k": recent_k, "rows": {}}
    for n in loads:
        acc = {"raw_uniform": [], "divnorm_uniform": [], "leaky_uniform": [],
               "raw_recent": [], "divnorm_recent": [], "leaky_recent": [], "twin_recent": []}
        for t in range(n_trials):
            seed = BASE_SEED + 100 * t + n
            Sr, keys, rm, truth = _accumulate(n, seed, leak=0.0)
            Sl, klk, rml, trl = _accumulate(n, seed, leak=leak)
            er = _decode(Sr, keys, rm, norm=None)
            ed = _decode(Sr, keys, rm, norm="divnorm")
            el = _decode(Sl, klk, rml, norm=None)
            # info-free twin: read the LEAKY store at shuffled keys
            rng = np.random.default_rng(seed + 7); perm = list(rng.permutation(n))
            et = _decode(Sl, [klk[p] for p in perm], rml, norm=None)
            acc["raw_uniform"].append(_acc_uniform(er, truth))
            acc["divnorm_uniform"].append(_acc_uniform(ed, truth))
            acc["leaky_uniform"].append(_acc_uniform(el, trl))
            acc["raw_recent"].append(_acc_recent(er, truth, recent_k))
            acc["divnorm_recent"].append(_acc_recent(ed, truth, recent_k))
            acc["leaky_recent"].append(_acc_recent(el, trl, recent_k))
            acc["twin_recent"].append(_acc_recent(et, trl, recent_k))
        res["rows"]["n=%d" % n] = {k: round(float(np.mean(v)), 3) for k, v in acc.items()}
    return res


def _print(res):
    print("=== WRITE/ENCODE-path limitation: flat running sum vs write-time leaky/suppressive gain (Buschman) ===")
    print("  D=%d V=%d, leak=%.2f, recent_k=%d, %d trials/cell; chance=%.2f\n"
          % (D, V, res["leak"], res["recent_k"], N_TRIALS, 1.0 / V))
    print("  UNIFORM recovery (ALL events) -- does read-time divnorm move the raw-sum capacity wall? (no)")
    print("    load    raw     divnorm   leaky")
    for n, r in res["rows"].items():
        print("    %-7s %.3f   %.3f     %.3f" % (n, r["raw_uniform"], r["divnorm_uniform"], r["leaky_uniform"]))
    print("\n  RECENCY recovery (the %d MOST-RECENT events -- what a reader needs):" % res["recent_k"])
    print("    load    raw     divnorm   leaky     twin")
    for n, r in res["rows"].items():
        print("    %-7s %.3f   %.3f     %.3f     %.3f" % (n, r["raw_recent"], r["divnorm_recent"], r["leaky_recent"], r["twin_recent"]))
    nmax = res["loads"][-1]
    rr = res["rows"]["n=%d" % nmax]
    print("\n  AT N=%d: recent-event recovery  raw=%.3f  divnorm=%.3f  LEAKY=%.3f  (chance=%.2f)"
          % (nmax, rr["raw_recent"], rr["divnorm_recent"], rr["leaky_recent"], 1.0 / V))
    print("  => read-time divnorm ~= raw (argmax scale-invariant); a WRITE-time leaky gain keeps RECENT events")
    print("     recoverable where the flat sum has collapsed -- a capacity lever no read-terminal norm can provide.")


def _self_test():
    # capacity wall: raw uniform recovery collapses at high N; write-time leaky keeps the most-recent event.
    Sr, keys, rm, truth = _accumulate(192, BASE_SEED, leak=0.0)
    Sl, kl, rml, trl = _accumulate(192, BASE_SEED, leak=0.25)
    raw_recent = _acc_recent(_decode(Sr, keys, rm), truth, 4)
    div_recent = _acc_recent(_decode(Sr, keys, rm, norm="divnorm"), truth, 4)
    leaky_recent = _acc_recent(_decode(Sl, kl, rml), trl, 4)
    assert abs(raw_recent - div_recent) < 1e-9, "read-time divnorm must not change argmax recovery: %.3f vs %.3f" % (raw_recent, div_recent)
    assert leaky_recent > raw_recent, "WRITE-time leaky must beat the flat sum on recent-event recovery at overload: %.3f vs %.3f" % (leaky_recent, raw_recent)
    # twin collapses
    rng = np.random.default_rng(BASE_SEED + 7); perm = list(rng.permutation(192))
    tw = _acc_recent(_decode(Sl, [kl[p] for p in perm], rml), trl, 4)
    assert tw < leaky_recent - 0.3, "info-free twin (shuffled keys) must collapse: %.3f vs %.3f" % (tw, leaky_recent)
    print("[self-test] PASS: read-time divnorm==raw on argmax (%.3f); WRITE-time leaky recovers recent events %.3f > "
          "raw %.3f at overload; twin collapses %.3f" % (div_recent, leaky_recent, raw_recent, tw))


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
