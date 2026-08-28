"""DEEPENING -- WHERE REASONING ADDS VALUE: transitive integration DENOISES independent noisy comparisons and answers
NEVER-OBSERVED pairs, beating a reader that only remembers each comparison LOCALLY.

Resolves the honest boundary found in the grounded arm (exp_transitive_grounded_p1_reader_v1 ARM B): on a single FIXED
magnitude axis (p1's embedding read) integration does NOT beat reading a pair directly -- there is no independent
evidence to aggregate. But TEXT does not present a fixed axis; it presents SCATTERED, NOISY, OVERLAPPING comparative
statements ("A>B" in one sentence, "B>C" in another, each an INDEPENDENT noisy observation -- Thurstonian). That is the
regime where the hippocampal relational integration earns its keep: it POOLS the independent evidence across the shared
structure, and it answers pairs the text NEVER stated.

MODEL (faithful to how a reader meets comparisons): N items with true magnitudes; a "text" states K comparative
sentences, each an INDEPENDENT observation of a random pair (i,j) whose winner is correct with probability
Phi(|m_i - m_j| / sigma_obs) (close pairs stated less reliably; independent noise per sentence). Arms:
  * integration    -- settle ALL K observations (delta-rule) -> ONE ordering -> answer every query pair.
  * local_majority -- remember each pair's OWN observations; majority-vote them; chance if the pair was never stated
                      (the no-integration reader: it cannot pool across the structure or infer un-stated pairs).
  * assoc_netwin   -- rank by net wins among observations (association, no ordering integration).
  * twin           -- shuffle the observation directions (info-free) -> LOSES.
Query set = ALL pairs, split into OBSERVED (>=1 sentence) and UNOBSERVED (0 sentences, the transitive-inference pairs).

PREDICTION (the reasoning value): integration >> local_majority, driven by (a) UNOBSERVED pairs (local = chance,
integration infers them) and (b) OBSERVED-but-noisy pairs (integration aggregates independent evidence across the chain
-> denoises). Info-free twin LOSES.

Run: .venv/Scripts/python.exe experiments/exp_transitive_integration_denoises_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_integration_denoises_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import fractional_power_encoding as fpe          # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_transitive_ordering_magnitude_line_v1 import (  # noqa: E402
    settle, _normalize_line, encode_register, decode_coord, _grid_codes, netwin, _sign, _boot_ci,
    FPE_SIGMA, POS_SCALE, GRID_MAX)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_integration_denoises_v1")
SEED = 20260828


def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def one_trial(n, k_obs, sigma_obs, seed, d=512):
    """N items, true magnitudes m_i = (n-1-rank). K independent Thurstonian observations of random pairs. Score arms
    on ALL pairs, split OBSERVED / UNOBSERVED."""
    rng = np.random.default_rng(seed)
    m = np.arange(n - 1, -1, -1, dtype=np.float64)               # m[rank] decreasing; rank 0 = biggest
    obs = []                                                     # (winner, loser) observed premises
    counts = {}                                                  # (min,max) -> [wins_for_min, total]
    for _ in range(k_obs):
        i, j = rng.choice(n, size=2, replace=False)
        p_correct = _phi(abs(m[i] - m[j]) / sigma_obs)
        true_w, true_l = (i, j) if m[i] > m[j] else (j, i)
        if rng.random() < p_correct:
            w, l = true_w, true_l
        else:
            w, l = true_l, true_w
        obs.append((w, l))
        key = (min(i, j), max(i, j))
        rec = counts.setdefault(key, [0, 0])
        rec[1] += 1
        if w == key[0]:
            rec[0] += 1

    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05); gc = _grid_codes(rates, grid)
    x = _normalize_line(settle(obs, n, seed=seed))
    S = encode_register(x, keys, rates, POS_SCALE)
    xhat = np.array([decode_coord(S, keys[i], rates, gc, grid) for i in range(n)])
    rs = np.random.default_rng(seed + 99)
    obs_tw = [((l, w) if rs.random() < 0.5 else (w, l)) for (w, l) in obs]
    xtw = _normalize_line(settle(obs_tw, n, seed=seed))
    nw = netwin(obs, n)

    def truth(a, b):
        return 1 if a < b else -1                                # rank a < b => a bigger
    tally = {sp: {"integration": 0.0, "local_majority": 0.0, "assoc": 0.0, "twin": 0.0, "n": 0}
             for sp in ["all", "observed", "unobserved"]}
    for a in range(n):
        for b in range(a + 1, n):
            t = truth(a, b)
            integ = 1.0 if _sign(xhat[a] - xhat[b]) == t else (0.5 if _sign(xhat[a] - xhat[b]) == 0 else 0.0)
            asc_s = _sign(nw[a] - nw[b]); asc = 1.0 if asc_s == t else (0.5 if asc_s == 0 else 0.0)
            tw = 1.0 if _sign(xtw[a] - xtw[b]) == t else (0.5 if _sign(xtw[a] - xtw[b]) == 0 else 0.0)
            rec = counts.get((a, b))
            if rec is None:
                loc = 0.5; bucket = "unobserved"
            else:
                wins_a = rec[0]; tot = rec[1]
                loc_s = 1 if wins_a > tot / 2 else (-1 if wins_a < tot / 2 else 0)
                loc = 1.0 if loc_s == t else (0.5 if loc_s == 0 else 0.0)
                bucket = "observed"
            for sp in ["all", bucket]:
                tally[sp]["integration"] += integ
                tally[sp]["local_majority"] += loc
                tally[sp]["assoc"] += asc
                tally[sp]["twin"] += tw
                tally[sp]["n"] += 1
    return tally


def cell(n, k_obs, sigma_obs, n_trials, base_seed, d=512, n_boot=1500):
    ARMS = ["integration", "local_majority", "assoc", "twin"]
    per = {sp: {a: [] for a in ARMS} for sp in ["all", "observed", "unobserved"]}
    frac_unobs = []
    for tr in range(n_trials):
        t = one_trial(n, k_obs, sigma_obs, base_seed + tr * 101, d=d)
        for sp in per:
            if t[sp]["n"] == 0:
                continue
            for a in ARMS:
                per[sp][a].append(t[sp][a] / t[sp]["n"])
        tot = t["all"]["n"]
        frac_unobs.append(t["unobserved"]["n"] / tot if tot else 0.0)
    out = {"n": n, "k_obs": k_obs, "sigma_obs": sigma_obs, "d": d, "n_trials": n_trials,
           "frac_unobserved": float(np.mean(frac_unobs))}
    for sp in per:
        out[sp] = {a: _boot_ci(per[sp][a], n_boot=n_boot, seed=base_seed + hash(sp + a) % 977) if per[sp][a]
                   else {"mean": float("nan")} for a in ARMS}
        if per[sp]["integration"] and per[sp]["local_majority"]:
            dv = np.asarray(per[sp]["integration"]) - np.asarray(per[sp]["local_majority"])
            out[sp]["integ_minus_local"] = _boot_ci(dv, n_boot=n_boot, seed=base_seed + 7)
    return out


def run(n_trials=150):
    out = {"anchor": "transitive_integration_denoises_v1", "seed": SEED}
    # HEADLINE: N=12, moderate density + noise
    out["headline"] = cell(12, 40, 2.5, n_trials, SEED)
    # density sweep (sparse -> dense text) at fixed noise
    out["k_sweep"] = [cell(12, k, 2.5, n_trials, SEED + 100 + k) for k in [20, 40, 80, 160]]
    # noise sweep (per-observation reliability) at fixed density
    out["sigma_sweep"] = [cell(12, 60, s, n_trials, SEED + 500 + int(s * 10)) for s in [1.5, 2.5, 4.0, 6.0]]
    return out


def summarize(res):
    h = res["headline"]
    print(f"\n=== TRANSITIVE INTEGRATION DENOISES independent noisy comparisons (N={h['n']}, K={h['k_obs']} obs, "
          f"sigma={h['sigma_obs']}, {h['frac_unobserved']*100:.0f}% pairs never stated) ===")
    print("   split        integration  local_majority  assoc  twin   [integ - local]")
    for sp in ["all", "observed", "unobserved"]:
        r = h[sp]
        im = r.get("integ_minus_local", {"mean": float('nan'), "lo": float('nan'), "hi": float('nan')})
        print(f"   {sp:<11s}  {r['integration']['mean']:.3f}       {r['local_majority']['mean']:.3f}"
              f"          {r['assoc']['mean']:.3f}  {r['twin']['mean']:.3f}   "
              f"{im['mean']:+.3f}[{im['lo']:+.3f},{im['hi']:+.3f}]")
    print("   (UNOBSERVED = pairs the text never stated: local_majority is at chance; integration INFERS them.)")

    print("\n  --- DENSITY SWEEP (sigma=2.5): integration vs local_majority on ALL pairs ---")
    print("     K   %unobs  integ  local  [integ-local]")
    for r in res["k_sweep"]:
        im = r["all"]["integ_minus_local"]
        print(f"   {r['k_obs']:>3d}   {r['frac_unobserved']*100:>4.0f}%  {r['all']['integration']['mean']:.3f}  "
              f"{r['all']['local_majority']['mean']:.3f}  {im['mean']:+.3f}[{im['lo']:+.3f},{im['hi']:+.3f}]")

    print("\n  --- NOISE SWEEP (K=60): integration vs local_majority on OBSERVED pairs (aggregation denoising) ---")
    print("   sigma  integ_obs  local_obs  [integ-local]")
    for r in res["sigma_sweep"]:
        ro = r["observed"]
        im = ro.get("integ_minus_local", {"mean": float('nan'), "lo": float('nan'), "hi": float('nan')})
        print(f"   {r['sigma_obs']:>4.1f}   {ro['integration']['mean']:.3f}      {ro['local_majority']['mean']:.3f}"
              f"      {im['mean']:+.3f}[{im['lo']:+.3f},{im['hi']:+.3f}]")


def self_test():
    r = cell(12, 40, 2.5, 50, 1, n_boot=800)
    un = r["unobserved"]; im = un["integ_minus_local"]
    assert r["all"]["integration"]["mean"] > r["all"]["local_majority"]["mean"], \
        f"integration must beat local reading overall: {r['all']}"
    assert im["lo"] > 0.0, f"on UNOBSERVED pairs integration must beat chance-local CI-sep: {im}"
    assert r["all"]["twin"]["mean"] < r["all"]["integration"]["mean"] - 0.1, f"twin must lose: {r['all']}"
    print(f"SELF-TEST PASS: ALL integ={r['all']['integration']['mean']:.3f} local={r['all']['local_majority']['mean']:.3f} "
          f"twin={r['all']['twin']['mean']:.3f} | UNOBSERVED integ={un['integration']['mean']:.3f} "
          f"local={un['local_majority']['mean']:.3f} (integ-local={im['mean']:+.3f}[{im['lo']:+.3f}]) "
          f"| %unobs={r['frac_unobserved']*100:.0f}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--trials", type=int, default=150)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    n_trials = 50 if args.mode == "smoke" and not args.full else args.trials
    t0 = time.time()
    res = run(n_trials=n_trials)
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
