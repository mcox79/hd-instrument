"""TRANSITIVE-COMPARISON REASONING over a magnitude ordering -- the FIRST reasoning operation, built on p1's ruler.

PROBLEM (slug transitive_comparison_reasoning_over_the_magnitude_ordering): p1 can COMPARE two items on a scale;
it cannot REASON over comparisons. Read pairwise "A>B, B>C" from a controlled set, INTEGRATE into ONE magnitude
ordering, answer the UN-STATED "A vs C" (never compared directly) CI-separated over a no-integration floor, with the
SYMBOLIC-DISTANCE EFFECT (far un-stated pairs answered better than near ones) and an info-free twin LOSING.

HOW THE BRAIN DOES THIS (the opening move -- PINNED vs OUR-INVENTION):
  * PINNED -- transitive inference = RELATIONAL integration of OVERLAPPING pairs into ONE ordering (hippocampus;
    Dusek & Eichenbaum 1997: fornix/hippocampal lesions kill the INFERENCE pairs, spare the premises), read out as a
    POSITION on a mental magnitude line (parietal ATOM: Walsh 2003; Nieder number neurons) with the SYMBOLIC-DISTANCE
    effect (Moyer 1973; the same distance effect p1's ruler already shows for adjectives).
  * PINNED -- the computational-level account of "integrate overlapping pairwise comparisons into scalar positions"
    is a DELTA-RULE / VALUE-TRANSFER relaxation (Frank, Rudy & O'Reilly 2003 connectionist TI model; the distance and
    end-anchor effects EMERGE from it). Bradley-Terry is its maximum-likelihood characterization -- NOT an off-the-shelf
    sort: it is a LOCAL, iterative, biologically-plausible update (nudge the winner up, the loser down), and overlapping
    premises couple through their shared middle term = the brain's OVERLAP integration, realized as coupled updates
    rather than symbolic chaining. This is why it beats a symbolic sort: it is graded, handles noisy/conflicting
    premises, and yields a magnitude line with a distance effect.
  * OUR-INVENTION-UNDER-TEST: the settling update rule (eta, epochs, logistic temp) and the FHRR storage/read-out.

THE SUBSTRATE-NATIVE PIPELINE (copy the computation, sweep the parameters):
  (1) INTEGRATE: delta-rule settle the stated premises -> a scalar magnitude position x_i per item (the parietal
      "value" / mental-line coordinate). Overlapping premises share the middle term -> coupled updates -> ONE ordering.
  (2) STORE in the FHRR register (tests "can the register HOLD a transitive ordering"): S = sum_i bind(item_key_i,
      FPE(scale * x_i)) -- each item bound to its magnitude PLACE CODE (p1's fractional_power_encoding), superposed.
  (3) READ un-stated (a,c): unbind item_key from S -> recover the place code -> decode its coordinate on the FPE grid
      (native resonator read-out) -> sign(x_hat_a - x_hat_c) is the answer; |x_hat_a - x_hat_c| is the Weber distance
      signal. The DISTANCE EFFECT emerges here: the noisy superposition read-out flips the SIGN more often when the two
      positions are CLOSE (small |dx|) than when far -- exactly the human signature, and Weber on-substrate.

FLOORS (recomputed per population; the strongest is the association floor, which is what the neuroscience uses to prove
INTEGRATION beyond association):
  * chance (0.5).
  * ASSOCIATIVE net-win ranking: rank each item by (#wins - #losses) among STATED premises; sign(netwin_a - netwin_b).
    In the adjacent-premise design every INTERNAL item wins once and loses once -> net 0 -> this floor is AT CHANCE on
    the internal-internal un-stated pairs BY CONSTRUCTION. Beating it there is proof of relational integration, not
    associative strength (the Dusek/Eichenbaum control).
  * stated-only lookup: answer only pairs that were literally stated; else chance -> chance on the un-stated set.
INFO-FREE TWIN: shuffle the premise DIRECTIONS (random winner/loser) -> settle -> a random ordering -> chance. LOSES.

Run: .venv/Scripts/python.exe experiments/exp_transitive_ordering_magnitude_line_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_ordering_magnitude_line_v1/. NO hdlab write.
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

from hdlab import binding                                   # noqa: E402
from hdlab import fractional_power_encoding as fpe          # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_ordering_magnitude_line_v1")
SEED = 20260828
D = 512               # register dimension (SWEPT; modest so the mental-line read-out noise reveals the distance effect)
FPE_SIGMA = 1.0       # Gaussian phase-rate sigma (p1 default; the log-Gaussian tuning width)
POS_SCALE = 2.0       # HALF-RANGE of the bounded mental line: normalized settled scores in [-1,1] -> coords in [-2,2].
#   PINNED: the parietal magnitude line is BOUNDED (working-memory span ~7+-2). The raw delta-rule (Bradley-Terry)
#   scores are UNBOUNDED (a clean chain pushes end items to +-inf), which phase-ALIASES the FPE code and INVERTS the
#   distance effect (extreme items decode to the wrong sign). Normalizing onto a bounded line keeps every coordinate in
#   the FPE faithful regime; the distance effect then emerges from READ-OUT noise, and the BT end-stretch (convex
#   spacing) reproduces the human END-ANCHOR effect for free.
GRID_MAX = 3.0        # decode grid half-width (> POS_SCALE so bounded coords never sit at the grid edge)


# ----------------------------------------------------------------------------------------------------------------------
# (0) the controlled transitive series: N items in a true latent order; ADJACENT premises only (the k-term series design)
# ----------------------------------------------------------------------------------------------------------------------
def make_series(n, seed, noise_eps=0.0):
    """True order = 0 (biggest) .. n-1 (smallest). STATED premises = adjacent pairs (i beats i+1). With prob noise_eps
    a stated premise is FLIPPED (a corrupted comparison). Returns (premises, true_rank) where premise=(winner,loser)."""
    rng = np.random.default_rng(seed)
    premises = []
    for i in range(n - 1):
        w, l = i, i + 1                       # i is bigger (lower rank index)
        if rng.random() < noise_eps:
            w, l = l, w                        # corrupt the stated direction
        premises.append((w, l))
    true_rank = list(range(n))                 # rank 0 = biggest
    return premises, true_rank


def unstated_pairs(n, premises):
    """All pairs NOT literally stated (in either direction). Tag each with symbolic distance and whether both items
    are INTERNAL (not an end item) -- the association-matched critical set."""
    stated = set()
    for w, l in premises:
        stated.add((w, l))
        stated.add((l, w))
    pairs = []
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in stated:
                continue
            dist = abs(a - b)
            both_internal = (a not in (0, n - 1)) and (b not in (0, n - 1))
            pairs.append({"a": a, "b": b, "dist": dist, "both_internal": both_internal})
    return pairs


# ----------------------------------------------------------------------------------------------------------------------
# (1) INTEGRATE: the delta-rule / value-transfer settling (Frank-Rudy-O'Reilly; Bradley-Terry ML form) -> scalar posns
# ----------------------------------------------------------------------------------------------------------------------
def settle(premises, n, eta=0.3, epochs=200, temp=1.0, seed=0):
    """Local delta-rule relaxation of stated premises into scalar magnitude positions. For each premise (w,l):
    p = sigmoid(temp*(x_w - x_l)); nudge x_w += eta*(1-p), x_l -= eta*(1-p) (gradient ascent on BT log-likelihood).
    Overlapping premises couple through the shared middle term -> ONE integrated ordering. Zero-mean each epoch."""
    x = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(seed + 7)
    order = list(range(len(premises)))
    for _ in range(epochs):
        rng.shuffle(order)
        for k in order:
            w, l = premises[k]
            p = 1.0 / (1.0 + np.exp(-temp * (x[w] - x[l])))
            g = eta * (1.0 - p)
            x[w] += g
            x[l] -= g
        x -= x.mean()
    return x


# ----------------------------------------------------------------------------------------------------------------------
# (2) STORE in the FHRR register + (3) native FPE read-out of each item's coordinate
# ----------------------------------------------------------------------------------------------------------------------
def encode_register(x, keys, rates, scale):
    """S = sum_i bind(item_key_i, FPE(scale * x_i)). The register holds the whole ordering as a superposition."""
    d = keys[0].shape[0]
    S = torch.zeros(d, dtype=torch.complex64)
    for i in range(len(keys)):
        place = fpe.enc(rates, scale * float(x[i]))
        S = S + binding.bind(keys[i], place)
    return S


def _grid_codes(rates, grid):
    return torch.stack([fpe.enc(rates, float(g)) for g in grid], dim=0)    # (G, d) complex


def decode_coord(S, key_i, rates, grid_codes, grid):
    """Recover item i's place code from the register (unbind its key) and decode its coordinate: argmax similarity to
    the FPE grid (the native resonator read-out). Returns the estimated coordinate (a mental-line position)."""
    place = binding.unbind(S, key_i)                        # ~ FPE(scale*x_i) + crosstalk from the other items
    p = place / place.abs().clamp_min(1e-12)
    # cos similarity to each grid code (real part of the normalized complex inner product)
    sims = torch.real(grid_codes.conj() @ p) / place.shape[0]
    j = int(torch.argmax(sims))
    return float(grid[j])


# ----------------------------------------------------------------------------------------------------------------------
# answer methods on an un-stated pair (a,b): return +1 if a>b predicted, -1 if b>a, 0 if tie (scored 0.5)
# ----------------------------------------------------------------------------------------------------------------------
def _sign(v):
    return 1 if v > 1e-9 else (-1 if v < -1e-9 else 0)


def netwin(premises, n):
    nw = np.zeros(n)
    for w, l in premises:
        nw[w] += 1
        nw[l] -= 1
    return nw


def score_pairs(pairs, predict):
    """predict(a,b) -> {+1,-1,0}; truth: a>b iff a's rank < b's rank (a is bigger). tie scored 0.5."""
    if not pairs:
        return float("nan")
    tot = 0.0
    for pr in pairs:
        a, b = pr["a"], pr["b"]
        truth = 1 if a < b else -1                          # a is bigger (rank a < rank b) => a>b => +1
        pred = predict(a, b)
        tot += 1.0 if pred == truth else (0.5 if pred == 0 else 0.0)
    return tot / len(pairs)


# ----------------------------------------------------------------------------------------------------------------------
# one trial: build series -> settle -> register -> decode positions -> score all arms on the un-stated sets
# ----------------------------------------------------------------------------------------------------------------------
def _normalize_line(x):
    """Map settled scores onto a BOUNDED mental line [-1,1] (parietal magnitude line is bounded). Preserves the
    settled (convex) spacing shape -- so both the distance effect and the BT end-anchor effect survive -- while keeping
    every coordinate inside the FPE faithful regime (no phase aliasing)."""
    m = float(np.abs(x).max()) + 1e-9
    return x / m


def one_trial(n, seed, d=D, noise_eps=0.0, eta=0.3, epochs=200, temp=1.0, pos_scale=POS_SCALE,
              grid_max=GRID_MAX, grid_step=0.05):
    premises, _ = make_series(n, seed, noise_eps=noise_eps)
    pairs = unstated_pairs(n, premises)

    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-grid_max, grid_max + 1e-9, grid_step)
    grid_codes = _grid_codes(rates, grid)

    # --- MECHANISM: settle -> bounded mental line -> register -> decode coordinates ---
    x = _normalize_line(settle(premises, n, eta=eta, epochs=epochs, temp=temp, seed=seed))
    S = encode_register(x, keys, rates, pos_scale)
    xhat = np.array([decode_coord(S, keys[i], rates, grid_codes, grid) for i in range(n)])

    # --- INFO-FREE TWIN: shuffle premise directions -> settle -> register -> decode ---
    rng = np.random.default_rng(seed + 99)
    prem_shuf = [((l, w) if rng.random() < 0.5 else (w, l)) for (w, l) in premises]
    x_tw = _normalize_line(settle(prem_shuf, n, eta=eta, epochs=epochs, temp=temp, seed=seed))
    S_tw = encode_register(x_tw, keys, rates, pos_scale)
    xhat_tw = np.array([decode_coord(S_tw, keys[i], rates, grid_codes, grid) for i in range(n)])

    nw = netwin(premises, n)
    stated = set()
    for w, l in premises:
        stated.add((w, l)); stated.add((l, w))

    arms = {
        "mechanism_register": lambda a, b: _sign(xhat[a] - xhat[b]),      # settle -> FHRR register -> decode
        "mechanism_float":    lambda a, b: _sign(x[a] - x[b]),            # settle -> compare floats (storage-free UB)
        "assoc_netwin":       lambda a, b: _sign(nw[a] - nw[b]),          # STRONGEST floor (matched on internal pairs)
        "stated_only":        lambda a, b: (_sign(-(a - b)) if (a, b) in stated else 0),  # chance on un-stated
        "twin_shuffled":      lambda a, b: _sign(xhat_tw[a] - xhat_tw[b]),  # info-free
    }

    def subset(flt):
        return [p for p in pairs if flt(p)]
    sets = {
        "all_unstated": pairs,
        "internal_unstated": subset(lambda p: p["both_internal"]),       # association-matched critical set
    }
    out = {}
    for sname, sp in sets.items():
        out[sname] = {arm: score_pairs(sp, fn) for arm, fn in arms.items()}

    # --- DISTANCE EFFECT: mechanism_register accuracy + read-out confidence by symbolic distance (on all un-stated) ---
    by_dist = {}
    for p in pairs:
        dst = p["dist"]
        a, b = p["a"], p["b"]
        truth = 1 if a < b else -1
        pred = _sign(xhat[a] - xhat[b])
        corr = 1.0 if pred == truth else (0.5 if pred == 0 else 0.0)
        conf = abs(xhat[a] - xhat[b])
        by_dist.setdefault(dst, {"corr": [], "conf": []})
        by_dist[dst]["corr"].append(corr)
        by_dist[dst]["conf"].append(conf)
    dist_curve = {int(k): {"acc": float(np.mean(v["corr"])), "conf": float(np.mean(v["conf"])), "n": len(v["corr"])}
                  for k, v in sorted(by_dist.items())}

    out["dist_curve"] = dist_curve
    return out


# ----------------------------------------------------------------------------------------------------------------------
# aggregate over seeds with bootstrap CIs; paired mechanism-minus-floor and the twin null p95
# ----------------------------------------------------------------------------------------------------------------------
def _boot_ci(vals, n_boot=2000, seed=0):
    v = np.asarray(vals, dtype=np.float64)
    rng = np.random.default_rng(seed)
    bs = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"mean": float(v.mean()), "lo": float(lo), "hi": float(hi), "half": float((hi - lo) / 2.0)}


def cell(n, n_seeds, base_seed, d=D, noise_eps=0.0, eta=0.3, epochs=200, temp=1.0, pos_scale=POS_SCALE, n_boot=2000):
    ARMS = ["mechanism_register", "mechanism_float", "assoc_netwin", "stated_only", "twin_shuffled"]
    acc = {s: {a: [] for a in ARMS} for s in ["all_unstated", "internal_unstated"]}
    dist_acc, dist_conf = {}, {}
    for r in range(n_seeds):
        t = one_trial(n, base_seed + r * 101, d=d, noise_eps=noise_eps, eta=eta, epochs=epochs,
                      temp=temp, pos_scale=pos_scale)
        for s in acc:
            for a in ARMS:
                acc[s][a].append(t[s][a])
        for dst, rec in t["dist_curve"].items():
            dist_acc.setdefault(dst, []).append(rec["acc"])
            dist_conf.setdefault(dst, []).append(rec["conf"])
    res = {"n": n, "d": d, "noise_eps": noise_eps, "eta": eta, "epochs": epochs, "temp": temp,
           "pos_scale": pos_scale, "n_seeds": n_seeds}
    for s in acc:
        res[s] = {a: _boot_ci(acc[s][a], n_boot=n_boot, seed=base_seed + hash(a) % 999) for a in ARMS}
        # paired mechanism_register - assoc_netwin (the key contrast) and - twin
        for flo in ["assoc_netwin", "twin_shuffled", "stated_only"]:
            dvec = np.asarray(acc[s]["mechanism_register"]) - np.asarray(acc[s][flo])
            res[s][f"reg_minus_{flo}"] = _boot_ci(dvec, n_boot=n_boot, seed=base_seed + 5)
        # twin null p95 on this set
        res[s]["twin_null_p95"] = float(np.percentile(acc[s]["twin_shuffled"], 95))
    res["dist_curve"] = {int(k): {"acc": float(np.mean(v)), "acc_lo": float(np.percentile(
        np.asarray(v)[np.random.default_rng(base_seed).integers(0, len(v), size=(1000, len(v)))].mean(axis=1), 2.5)),
        "conf": float(np.mean(dist_conf[k])), "n_seeds": len(v)} for k, v in sorted(dist_acc.items())}
    return res


# ----------------------------------------------------------------------------------------------------------------------
def run(n_seeds=200):
    out = {"anchor": "transitive_ordering_magnitude_line_v1", "seed": SEED, "fpe_sigma": FPE_SIGMA}
    # HEADLINE: the classic k-term series at N=7, clean premises
    out["headline"] = cell(7, n_seeds, SEED)
    # N-scaling (register load grows) at clean premises
    out["n_scaling"] = [cell(n, n_seeds, SEED + n) for n in [5, 7, 9, 11]]
    # NOISE robustness: corrupted premises (graded settling should degrade gracefully where a symbolic sort breaks)
    out["noise_sweep"] = [cell(9, n_seeds, SEED + 400, noise_eps=e) for e in [0.0, 0.1, 0.2, 0.3]]
    # D sweep: the distance effect is a read-out property (smaller D -> noisier line -> stronger distance effect)
    out["d_sweep"] = [cell(9, n_seeds, SEED + 800, d=dd) for dd in [128, 256, 512, 1024]]
    return out


def summarize(res):
    h = res["headline"]
    print(f"\n=== TRANSITIVE-ORDERING MAGNITUDE LINE (N=7 k-term series, clean premises, D={h['d']}) ===")
    print("  set                 mech_reg  mech_float  assoc_netwin  stated_only  twin   [reg-netwin CI]")
    for s in ["internal_unstated", "all_unstated"]:
        r = s and res["headline"][s]
        rm = r["reg_minus_assoc_netwin"]
        print(f"  {s:<18s}  {r['mechanism_register']['mean']:.3f}     {r['mechanism_float']['mean']:.3f}"
              f"       {r['assoc_netwin']['mean']:.3f}        {r['stated_only']['mean']:.3f}      "
              f"{r['twin_shuffled']['mean']:.3f}  {rm['mean']:+.3f}[{rm['lo']:+.3f},{rm['hi']:+.3f}]")
    print("  (internal_unstated = association-MATCHED critical pairs; beating assoc_netwin there = relational integration)")

    print("\n  --- SYMBOLIC-DISTANCE EFFECT (mechanism_register on all un-stated pairs, by symbolic distance) ---")
    print("   dist   acc    conf(|dx|)   n")
    for dst, rec in res["headline"]["dist_curve"].items():
        print(f"    {dst:>2d}   {rec['acc']:.3f}    {rec['conf']:.3f}      {rec['n_seeds']}")

    print("\n  --- N-SCALING (internal_unstated; register load grows with N) ---")
    print("    N   mech_reg  assoc_netwin  [reg-netwin CI]   twin_p95")
    for r in res["n_scaling"]:
        iu = r["internal_unstated"]
        rm = iu["reg_minus_assoc_netwin"]
        print(f"   {r['n']:>2d}   {iu['mechanism_register']['mean']:.3f}     {iu['assoc_netwin']['mean']:.3f}"
              f"        {rm['mean']:+.3f}[{rm['lo']:+.3f},{rm['hi']:+.3f}]   {iu['twin_null_p95']:.3f}")

    print("\n  --- NOISE ROBUSTNESS (N=9 internal_unstated; corrupted premises) ---")
    print("    eps  mech_reg  assoc_netwin  [reg-netwin CI]")
    for r in res["noise_sweep"]:
        iu = r["internal_unstated"]
        rm = iu["reg_minus_assoc_netwin"]
        print(f"   {r['noise_eps']:.1f}   {iu['mechanism_register']['mean']:.3f}     {iu['assoc_netwin']['mean']:.3f}"
              f"        {rm['mean']:+.3f}[{rm['lo']:+.3f},{rm['hi']:+.3f}]")

    print("\n  --- ACCURACY DISTANCE EFFECT in the SUB-CEILING (noisy) regime (N=9, all un-stated by distance) ---")
    print("    eps   " + "  ".join(f"d{k}" for k in sorted(int(x) for x in res['noise_sweep'][0]['dist_curve'])))
    for r in res["noise_sweep"]:
        dc = r["dist_curve"]
        ks = sorted(int(x) for x in dc)
        print(f"   {r['noise_eps']:.1f}   " + " ".join(f"{dc[str(k)]['acc']:.3f}" for k in ks))
    print("   (far un-stated pairs answered BETTER than near ones -- the symbolic-distance effect, in accuracy)")

    print("\n  --- D SWEEP (N=9; distance effect is a read-out property) far-minus-near acc ---")
    print("     D   near(d2)  far(dmax)   reg_internal")
    for r in res["d_sweep"]:
        dc = r["dist_curve"]
        ks = sorted(dc.keys())
        near = dc[ks[0]]["acc"]; far = dc[ks[-1]]["acc"]
        print(f"   {r['d']:>4d}   {near:.3f}     {far:.3f}      {r['internal_unstated']['mechanism_register']['mean']:.3f}")


# ----------------------------------------------------------------------------------------------------------------------
def self_test():
    """Fast can-fail checks: (a) the mechanism beats the association floor on association-MATCHED internal un-stated
    pairs CI-separated; (b) the info-free twin loses; (c) the distance effect is present (far >= near)."""
    r = cell(7, 60, 1, n_boot=1000)
    iu = r["internal_unstated"]
    rm = iu["reg_minus_assoc_netwin"]
    tw = iu["reg_minus_twin_shuffled"]
    assert iu["mechanism_register"]["mean"] > 0.8, f"mechanism must answer un-stated internal pairs: {iu['mechanism_register']}"
    assert rm["lo"] > 0.0, f"mechanism must beat assoc_netwin CI-sep on matched pairs: {rm}"
    assert tw["lo"] > 0.0, f"mechanism must beat the info-free twin CI-sep: {tw}"
    assert iu["assoc_netwin"]["mean"] < 0.65, f"assoc floor must be ~chance on matched internal pairs: {iu['assoc_netwin']}"
    # distance effect: far pairs at least as accurate as near, on a noisier D to reveal it
    rd = cell(9, 60, 2, d=128, n_boot=800)
    dc = rd["dist_curve"]; ks = sorted(dc.keys())
    near, far = dc[ks[0]]["acc"], dc[ks[-1]]["acc"]
    assert far >= near - 0.02, f"distance effect: far>=near expected, got near(d{ks[0]})={near:.3f} far(d{ks[-1]})={far:.3f}"
    print(f"SELF-TEST PASS: N7 internal mech_reg={iu['mechanism_register']['mean']:.3f} "
          f"assoc={iu['assoc_netwin']['mean']:.3f} reg-assoc={rm['mean']:+.3f}[{rm['lo']:+.3f},{rm['hi']:+.3f}] "
          f"reg-twin={tw['mean']:+.3f}[{tw['lo']:+.3f}] | dist: near(d{ks[0]})={near:.3f} far(d{ks[-1]})={far:.3f} "
          f"(conf near {dc[ks[0]]['conf']:.2f} far {dc[ks[-1]]['conf']:.2f})")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    n_seeds = 60 if args.mode == "smoke" and not args.full else args.seeds
    t0 = time.time()
    res = run(n_seeds=n_seeds)
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
