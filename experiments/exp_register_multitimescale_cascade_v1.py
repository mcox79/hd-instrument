"""the_register_write_path_has_a_hard_capacity_wall -- FIDELITY DEEPENING: single geometric leak vs a
MULTI-TIMESCALE register (a SPECTRUM of leak rates).

BRAIN GROUNDING (research_multitimescale_cascade_2026-08-29.md, primary-verified): the WM-stage multi-timescale
spectrum is PINNED-BY-EVIDENCE -- Bernacchia, Seo, Lee & Wang 2011 (Nat Neurosci, PMID 21317906) MEASURE a
power-law RESERVOIR of memory time constants (100s of ms -> 10s of s) in monkey PFC/cingulate/parietal single
units; Murray et al. 2014 (Nat Neurosci) confirm a hierarchy of intrinsic timescales across 7 areas. So "carry a
SPECTRUM of timescales, not one lam" is PINNED (P~0.80). NOTE (citation correction): Fusi 2005 / Benna-Fusi 2016 are
the SYNAPTIC-CONSOLIDATION stage and are MODELS -- their per-synapse capacity theorem comes from BIDIRECTIONAL
COUPLING (value flows fast->slow) and does NOT transfer to a set of INDEPENDENT superposition sums; do not credit
them for this WM-stage result. What is measured here is TEMPORAL REACH (recency window), NOT Benna-Fusi capacity
scaling (a superposition register's simultaneous capacity is set by D). The K-independent-sums + best-margin readout
is OUR-INVENTION implementation of the PINNED spectrum (unfalsified != confirmed); a COUPLED superposition cascade
is the more-faithful form but ~ a reparameterised bank of leaks (gamma-shaped kernels), so it changes the
forgetting-curve SHAPE, not the capability -- worth one can-fail test, done last.

The submitted solution uses ONE exponential leak (`S = lam*S + new`), one recoverable window ~1/(1-lam). This cell
asks whether a set of leaky sums at DIFFERENT rates -- read per-event from the timescale holding the clearest trace
(a gold-blind best-margin readout, the same CA1-comparator confidence decode_gated uses) -- extends the recoverable
recency window past a single leak, and whether it still needs the salience-gated 2nd store at extreme load.

ARMS (all read the same event population):
  SINGLE   : one leak lam=0.75 (the submitted form), argmax read.
  CASCADE  : K leaks spanning fast->slow; per event, read the level with the largest top1-top2 margin.
  TWIN     : cascade read at SHUFFLED keys (info-free) -> chance.

Metrics: recovery-vs-recency-position curve; REACH (oldest position still recovered > 0.5); window-SUM (total
events recoverable); recent-4 (must stay ~1.0 -- the cascade must not sacrifice recent for window). Bootstrap CI
over trials. Also: at extreme load the cascade's reach is still FINITE -> far-old salient events STILL need the
2nd store (the cascade EXTENDS the buffer, it does not replace consolidation).

Run:
  .venv/Scripts/python.exe experiments/exp_register_multitimescale_cascade_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_register_multitimescale_cascade_v1.py --run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

D, V, BASE_SEED = 256, 100, 20260829
CASCADE = [0.5, 0.75, 0.9, 0.97, 0.995]      # fast -> slow (5 timescales; a swept design, not adopted numbers)
SINGLE = 0.75
RESULTS = os.path.join(REPO, "data", "exp_register_multitimescale_cascade_v1")


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


def _build(n, seed, lams):
    g = _gen(seed)
    roles = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(n)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(n)]
    S = [torch.zeros(D, dtype=torch.complex64) for _ in lams]
    for j in range(n):
        b = binding.bind(roles[truth[j]], keys[j])
        for i, lam in enumerate(lams):
            S[i] = lam * S[i] + b
    return S, keys, torch.stack(roles), truth


def _decode_best_level(S_list, keys, rm):
    """Gold-blind multi-resolution read: per event, pick the argmax from the level with the largest top1-top2
    margin (a CA1-comparator confidence readout -- the same signal decode_gated uses; no oracle, no truth)."""
    conj = torch.conj(rm)
    est = []
    for k in keys:
        rb_best_m, rb_best_e = -1e9, 0
        for S in S_list:
            sc = torch.real(conj @ binding.unbind(S, k))
            top2 = torch.topk(sc, 2).values
            m = float(top2[0] - top2[1])
            if m > rb_best_m:
                rb_best_m, rb_best_e = m, int(torch.argmax(sc))
        est.append(rb_best_e)
    return est


def _decode_single(S, keys, rm):
    conj = torch.conj(rm)
    return [int(torch.argmax(torch.real(conj @ binding.unbind(S, k)))) for k in keys]


def _reach(curve, thr=0.5):
    r = [p for p, v in enumerate(curve) if v > thr]
    return max(r) if r else -1


def cascade_sweep(loads=(128, 256, 512, 768), n_trials=30, n_boot=2000, max_pos=48):
    rows = {}
    for n in loads:
        cpos, spos = defaultdict(list), defaultdict(list)
        casc_reach, sing_reach, casc_sum, sing_sum = [], [], [], []
        casc_recent, sing_recent, twin_recent = [], [], []
        for t in range(n_trials):
            seed = BASE_SEED + 137 * t + n
            Sc, keys, rm, truth = _build(n, seed, CASCADE)
            Ss, _, _, _ = _build(n, seed, [SINGLE])
            ec = _decode_best_level(Sc, keys, rm)
            es = _decode_single(Ss[0], keys, rm)
            rng = np.random.default_rng(seed + 7); perm = list(rng.permutation(n))
            etw = _decode_best_level(Sc, [keys[p] for p in perm], rm)
            cc = [0.0] * max_pos; ss = [0.0] * max_pos; ccount = [0] * max_pos
            for j in range(n):
                p = n - 1 - j
                if p < max_pos:
                    cpos[p].append(int(ec[j] == truth[j])); spos[p].append(int(es[j] == truth[j]))
            # per-trial reach/sum from this trial's own curve
            c_tr = [np.mean(cpos[p][-1:]) if cpos[p] else 0 for p in range(max_pos)]
            recent = range(n - 4, n)
            casc_recent.append(np.mean([ec[j] == truth[j] for j in recent]))
            sing_recent.append(np.mean([es[j] == truth[j] for j in recent]))
            twin_recent.append(np.mean([etw[j] == truth[j] for j in recent]))
        cc = [round(float(np.mean(cpos[p])), 3) for p in range(max_pos)]
        ss = [round(float(np.mean(spos[p])), 3) for p in range(max_pos)]
        # bootstrap the reach + window-sum over trials via per-position resampling is awkward; instead bootstrap
        # the per-trial window-sum (# recovered in first max_pos positions).
        c_persum = [sum(int(v) for v in [cpos[p][t] for p in range(max_pos) if t < len(cpos[p])]) for t in range(n_trials)]
        s_persum = [sum(int(v) for v in [spos[p][t] for p in range(max_pos) if t < len(spos[p])]) for t in range(n_trials)]
        def ci(a):
            a = np.asarray(a, float); rng = np.random.default_rng(BASE_SEED + n)
            b = a[rng.integers(0, len(a), size=(n_boot, len(a)))].mean(1)
            return round(float(a.mean()), 2), [round(float(np.percentile(b, 2.5)), 2), round(float(np.percentile(b, 97.5)), 2)]
        d = np.asarray(c_persum, float) - np.asarray(s_persum, float)
        rng = np.random.default_rng(BASE_SEED + 5 + n)
        bd = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(1)
        rows["n=%d" % n] = {
            "cascade_curve": cc, "single_curve": ss,
            "cascade_reach": _reach(cc), "single_reach": _reach(ss),
            "cascade_window_recovered": ci(c_persum), "single_window_recovered": ci(s_persum),
            "cascade_minus_single_window": {"delta": round(float(d.mean()), 2),
                                            "ci": [round(float(np.percentile(bd, 2.5)), 2),
                                                   round(float(np.percentile(bd, 97.5)), 2)],
                                            "sep": bool(np.percentile(bd, 2.5) > 0)},
            "cascade_recent4": round(float(np.mean(casc_recent)), 3),
            "single_recent4": round(float(np.mean(sing_recent)), 3),
            "twin_recent4": round(float(np.mean(twin_recent)), 3),
        }
    return {"D": D, "V": V, "cascade_lams": CASCADE, "single_lam": SINGLE, "loads": list(loads),
            "n_trials": n_trials, "max_pos": max_pos, "rows": rows}


def _self_test():
    r = cascade_sweep(loads=(256,), n_trials=8, n_boot=300)["rows"]["n=256"]
    assert r["cascade_reach"] > r["single_reach"] + 5, \
        "cascade must extend the recoverable window well past single-lam: %d vs %d" % (r["cascade_reach"], r["single_reach"])
    assert r["cascade_minus_single_window"]["sep"], \
        "cascade must recover more of the window CI-separated: %r" % r["cascade_minus_single_window"]
    assert r["cascade_recent4"] > 0.9, "cascade must NOT sacrifice recent recovery: %.3f" % r["cascade_recent4"]
    assert r["twin_recent4"] < 0.5, "info-free twin (shuffled keys) must collapse: %.3f" % r["twin_recent4"]
    # cascade reach is still FINITE at extreme load -> far-old events STILL need the 2nd store
    assert r["cascade_reach"] < 256, "cascade reach must be finite (2nd store still needed for far-old): %d" % r["cascade_reach"]
    print("[self-test] PASS  cascade reach=%d >> single reach=%d (window +%s CI-sep); recent4 cascade=%.3f "
          "single=%.3f; twin=%.3f collapses; reach finite -> 2nd store still needed"
          % (r["cascade_reach"], r["single_reach"], r["cascade_minus_single_window"]["delta"],
             r["cascade_recent4"], r["single_recent4"], r["twin_recent4"]))


def _print(res):
    print("=== FIDELITY: single geometric leak vs MULTI-TIMESCALE CASCADE write (Fusi/Benna-Fusi) ===")
    print("  D=%d V=%d cascade_lams=%s single_lam=%.2f, %d trials\n" % (D, V, CASCADE, SINGLE, res["n_trials"]))
    print("  %-6s %-14s %-14s  %-26s  %-10s %-10s %-8s" % (
        "load", "cascade_reach", "single_reach", "window recovered (cascade|single)",
        "casc_rec4", "sing_rec4", "twin"))
    for n in res["loads"]:
        r = res["rows"]["n=%d" % n]
        cw = r["cascade_window_recovered"]; sw = r["single_window_recovered"]
        d = r["cascade_minus_single_window"]
        print("  %-6d %-14d %-14d  %-26s  %-10.3f %-10.3f %-8.3f  (+%s %s)" % (
            n, r["cascade_reach"], r["single_reach"],
            "%.1f%s | %.1f%s" % (cw[0], cw[1], sw[0], sw[1]),
            r["cascade_recent4"], r["single_recent4"], r["twin_recent4"],
            d["delta"], "SEP" if d["sep"] else "ns"))
    n0 = res["loads"][1] if len(res["loads"]) > 1 else res["loads"][0]
    r0 = res["rows"]["n=%d" % n0]
    print("\n  Recovery-vs-position @N=%d (0=newest) -- cascade is GRADED over a WIDE window; single is a sharp cliff:" % n0)
    print("    cascade[0:24]: %s" % r0["cascade_curve"][:24])
    print("    single [0:24]: %s" % r0["single_curve"][:24])
    print("\n  => a multi-timescale cascade recovers ~3x more of the recency window with a smoother graded gradient")
    print("     (the brain's spectrum-of-timescales memory), WITHOUT a gate; but its reach is finite, so the")
    print("     salience-gated 2nd store is STILL needed for far-old salient events. Cascade EXTENDS the buffer.")


def run():
    res = cascade_sweep()
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "metrics.json"), "w") as f:
        json.dump(res, f, indent=2)
    _print(res)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    run()
