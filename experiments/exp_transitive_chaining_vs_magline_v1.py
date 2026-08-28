"""FINER BRAIN-FOUNDATIONAL DRILL -- WHY the magnitude line and not serial chaining? The distance-effect DIRECTION is
the decisive discriminator (Eichenbaum 1997; Frank-Rudy-O'Reilly 2003's two routes).

The brief (S3) names TWO candidate integrations: the parietal MAGNITUDE LINE (our mechanism) and a "relational-register
integration". The classic hippocampal alternative is the RECALL / SERIAL-CHAINING route: answer "A vs C" by traversing
the premise graph through the shared middle terms (A>B, B>C => A>C). This drill asks which route the brain actually uses
-- and the answer is settled by a signature we can measure on-substrate:

  * SERIAL CHAINING must traverse the chain: a query at symbolic distance d needs ~d hops. Under noisy premises, a longer
    path is more likely to cross a corrupted edge -> FAR pairs are HARDER. Chaining predicts a FLAT-or-INVERSE distance
    effect (and, on latency, far = SLOWER). This is Eichenbaum's argument against chaining.
  * MAGNITUDE-LINE integration places every item on ONE line and compares POSITIONS in parallel (O(1)); the read-out is
    noisier for CLOSE positions -> FAR pairs are EASIER. It predicts the POSITIVE (human) distance effect and, on
    latency, far = FASTER.

HUMANS/ANIMALS show the POSITIVE distance effect (far judged faster and more accurately; Moyer 1973; the fast-BD
finding). So IF our chaining route shows a flat/inverse distance effect while our magnitude line shows the positive
(human) one, we have MEASURED why the magnitude-line integration is the faithful mechanism and pure serial chaining is
not -- on the same premises, the same substrate.

Both routes are given the SAME noisy premises (adjacent k-term series). Chaining = exact directed BFS over the premise
graph (no read-out noise -- a STRONG chaining baseline). Magnitude = settle -> FHRR magnitude-line register -> decode.

Run: .venv/Scripts/python.exe experiments/exp_transitive_chaining_vs_magline_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_chaining_vs_magline_v1/. NO hdlab write.
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
from collections import defaultdict, deque

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import fractional_power_encoding as fpe          # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_transitive_ordering_magnitude_line_v1 import (  # noqa: E402
    make_series, unstated_pairs, settle, _normalize_line, encode_register, decode_coord, _grid_codes,
    _sign, _boot_ci, FPE_SIGMA, POS_SCALE, GRID_MAX)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_chaining_vs_magline_v1")
SEED = 20260828


def _reach(adj, s, t):
    """Directed reachability s -> t and the hop-count of the found path (BFS). Returns (reachable, hops)."""
    if s == t:
        return True, 0
    seen = {s}; dq = deque([(s, 0)])
    while dq:
        u, h = dq.popleft()
        for v in adj[u]:
            if v == t:
                return True, h + 1
            if v not in seen:
                seen.add(v); dq.append((v, h + 1))
    return False, -1


def chain_answer(adj, a, b):
    """Serial-chaining answer: +1 if a>...>b reachable, -1 if b>...>a, 0 if neither (guess). Also return hops used."""
    ra, ha = _reach(adj, a, b)
    if ra:
        return 1, ha
    rb, hb = _reach(adj, b, a)
    if rb:
        return -1, hb
    return 0, -1


def one_trial(n, seed, d=512, noise_eps=0.15):
    premises, _ = make_series(n, seed, noise_eps=noise_eps)
    pairs = unstated_pairs(n, premises)
    adj = defaultdict(set)
    for w, l in premises:
        adj[w].add(l)

    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05); gc = _grid_codes(rates, grid)
    x = _normalize_line(settle(premises, n, seed=seed))
    S = encode_register(x, keys, rates, POS_SCALE)
    xhat = np.array([decode_coord(S, keys[i], rates, gc, grid) for i in range(n)])

    def truth(a, b):
        return 1 if a < b else -1
    rec = {"mag": {}, "chain": {}, "chain_hops": {}}
    for p in pairs:
        a, b = p["a"], p["b"]; t = truth(a, b); dst = p["dist"]
        mag = 1.0 if _sign(xhat[a] - xhat[b]) == t else (0.5 if _sign(xhat[a] - xhat[b]) == 0 else 0.0)
        cs, hops = chain_answer(adj, a, b)
        ch = 1.0 if cs == t else (0.5 if cs == 0 else 0.0)
        for dct, val in [("mag", mag), ("chain", ch)]:
            rec[dct].setdefault(dst, [0.0, 0]); rec[dct][dst][0] += val; rec[dct][dst][1] += 1
        if hops > 0:
            rec["chain_hops"].setdefault(dst, [0, 0]); rec["chain_hops"][dst][0] += hops; rec["chain_hops"][dst][1] += 1
    return rec


def _slope(dm):
    ks = sorted(dm)
    if len(ks) < 2:
        return 0.0
    xs = np.array(ks, float); ys = np.array([dm[k] for k in ks], float)
    return float(np.corrcoef(xs, ys)[0, 1]) if ys.std() > 1e-9 else 0.0


def cell(n, n_seeds, base_seed, d=512, noise_eps=0.15, n_boot=1200):
    magd, chd, hopd = {}, {}, {}
    mag_all, ch_all = [], []
    for s in range(n_seeds):
        t = one_trial(n, base_seed + s * 101, d=d, noise_eps=noise_eps)
        mtot = ctot = ntot = 0.0
        for dct_src, dct in [(t["mag"], magd), (t["chain"], chd)]:
            for k, (tot, cnt) in dct_src.items():
                a = dct.setdefault(k, [0.0, 0]); a[0] += tot; a[1] += cnt
        for k, (tot, cnt) in t["chain_hops"].items():
            a = hopd.setdefault(k, [0, 0]); a[0] += tot; a[1] += cnt
        for k, (tot, cnt) in t["mag"].items():
            mtot += tot; ntot += cnt
        for k, (tot, cnt) in t["chain"].items():
            ctot += tot
        mag_all.append(mtot / ntot); ch_all.append(ctot / ntot)
    magc = {int(k): round(v[0] / v[1], 4) for k, v in sorted(magd.items())}
    chc = {int(k): round(v[0] / v[1], 4) for k, v in sorted(chd.items())}
    hopc = {int(k): round(v[0] / v[1], 2) for k, v in sorted(hopd.items())}
    return {"n": n, "noise_eps": noise_eps, "d": d, "n_seeds": n_seeds,
            "mag_overall": _boot_ci(mag_all, n_boot=n_boot, seed=base_seed + 1),
            "chain_overall": _boot_ci(ch_all, n_boot=n_boot, seed=base_seed + 2),
            "mag_dist": magc, "chain_dist": chc, "chain_hops": hopc,
            "mag_slope": round(_slope(magc), 3), "chain_slope": round(_slope(chc), 3)}


def end_anchor_cell(n, n_seeds, base_seed, d=384, noise_eps=0.2):
    """Second human TI signature -- the END-ANCHOR / serial-position effect: at a MATCHED symbolic distance, pairs
    INVOLVING an end item are judged more reliably than all-internal pairs (emerges from the BT convex end-stretch)."""
    acc = {}                                                # (dist, is_end) -> [hit, tot]
    for s in range(n_seeds):
        seed = base_seed + s * 101
        premises, _ = make_series(n, seed, noise_eps=noise_eps)
        pairs = unstated_pairs(n, premises)
        g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
        keys = [unit_phase_vec(d, g) for _ in range(n)]
        rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
        grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05); gc = _grid_codes(rates, grid)
        x = _normalize_line(settle(premises, n, seed=seed))
        S = encode_register(x, keys, rates, POS_SCALE)
        xh = np.array([decode_coord(S, keys[i], rates, gc, grid) for i in range(n)])
        for p in pairs:
            a, b = p["a"], p["b"]; t = 1 if a < b else -1
            is_end = (a in (0, n - 1)) or (b in (0, n - 1))
            pred = _sign(xh[a] - xh[b]); hit = 1.0 if pred == t else (0.5 if pred == 0 else 0.0)
            r = acc.setdefault((p["dist"], is_end), [0.0, 0]); r[0] += hit; r[1] += 1
    rows, deltas = [], []
    for dst in sorted(set(dd for dd, _ in acc)):
        ki, ke = (dst, False), (dst, True)
        if ki in acc and ke in acc and acc[ki][1] >= 20 and acc[ke][1] >= 20:
            ai = acc[ki][0] / acc[ki][1]; ae = acc[ke][0] / acc[ke][1]
            rows.append({"dist": dst, "internal": round(ai, 4), "end": round(ae, 4), "delta": round(ae - ai, 4)})
            deltas.append(ae - ai)
    return {"n": n, "noise_eps": noise_eps, "rows": rows, "mean_end_anchor_delta": round(float(np.mean(deltas)), 4),
            "frac_dist_with_positive_delta": round(float(np.mean([dd > 0 for dd in deltas])), 3)}


def run(n_seeds=200):
    out = {"anchor": "transitive_chaining_vs_magline_v1", "seed": SEED}
    out["headline"] = cell(11, n_seeds, SEED, noise_eps=0.15)
    out["noise_sweep"] = [cell(11, n_seeds, SEED + 300 + int(e * 100), noise_eps=e) for e in [0.0, 0.1, 0.2, 0.3]]
    out["end_anchor"] = end_anchor_cell(13, n_seeds, SEED + 700)
    return out


def summarize(res):
    h = res["headline"]
    print(f"\n=== SERIAL-CHAINING vs MAGNITUDE-LINE: the distance-effect DIRECTION (N={h['n']}, eps={h['noise_eps']}) ===")
    print(f"  overall: magnitude={h['mag_overall']['mean']:.3f}[{h['mag_overall']['lo']:.3f},{h['mag_overall']['hi']:.3f}]"
          f"  chaining={h['chain_overall']['mean']:.3f}[{h['chain_overall']['lo']:.3f},{h['chain_overall']['hi']:.3f}]")
    print("   dist:    " + "  ".join(f"d{k}" for k in sorted(h["mag_dist"])))
    print("   magnitude " + " ".join(f"{h['mag_dist'][k]:.2f}" for k in sorted(h["mag_dist"])) + f"   slope {h['mag_slope']:+.2f} (POSITIVE = human)")
    print("   chaining  " + " ".join(f"{h['chain_dist'][k]:.2f}" for k in sorted(h["chain_dist"])) + f"   slope {h['chain_slope']:+.2f}")
    print("   hops(BFS) " + " ".join(f"{h['chain_hops'].get(k, 0):.1f}" for k in sorted(h["mag_dist"])) + "   (far pairs need MORE hops)")
    print("\n  --- NOISE SWEEP: distance-effect SLOPE by route (positive=human distance effect; chaining goes NEGATIVE) ---")
    print("    eps   mag_slope  chain_slope   mag_overall  chain_overall")
    for r in res["noise_sweep"]:
        print(f"   {r['noise_eps']:.1f}    {r['mag_slope']:+.2f}      {r['chain_slope']:+.2f}       "
              f"{r['mag_overall']['mean']:.3f}        {r['chain_overall']['mean']:.3f}")
    print("\n  READING: the human POSITIVE distance effect (far EASIER) is produced by the MAGNITUDE LINE and CONTRADICTED")
    print("  by serial chaining (far pairs need more hops -> more likely to cross a corrupted edge -> HARDER, a flat/")
    print("  negative slope). Eichenbaum's argument, measured on-substrate: the distance effect PINS magnitude-line")
    print("  integration and RULES OUT pure serial chaining as the mechanism.")

    ea = res["end_anchor"]
    print(f"\n  --- SECOND HUMAN SIGNATURE: END-ANCHOR effect (N={ea['n']}, eps={ea['noise_eps']}); "
          f"mean delta {ea['mean_end_anchor_delta']:+.3f}, positive at {ea['frac_dist_with_positive_delta']*100:.0f}% of distances ---")
    print("   dist  internal  end-involving  delta")
    for r in ea["rows"]:
        print(f"   {r['dist']:>3d}   {r['internal']:.3f}     {r['end']:.3f}       {r['delta']:+.3f}")
    print("   (end-involving pairs easier at MATCHED distance -> the serial-position effect, from the BT end-stretch)")


def self_test():
    c = cell(11, 80, 1, noise_eps=0.2, n_boot=600)
    assert c["mag_slope"] > 0.4, f"magnitude line must show POSITIVE distance effect: {c['mag_slope']} {c['mag_dist']}"
    assert c["chain_slope"] < c["mag_slope"] - 0.3, \
        f"chaining distance-slope must be well BELOW magnitude's (flat/inverse): chain={c['chain_slope']} mag={c['mag_slope']}"
    # far pairs need more hops than near pairs (the mechanistic reason)
    hops = c["chain_hops"]; ks = sorted(hops)
    assert hops[ks[-1]] > hops[ks[0]] + 1, f"far pairs must need MORE chaining hops: {hops}"
    ea = end_anchor_cell(13, 60, 2)
    assert ea["mean_end_anchor_delta"] > 0.0 and ea["frac_dist_with_positive_delta"] > 0.7, \
        f"END-ANCHOR effect must be present (end-involving pairs easier at matched distance): {ea['mean_end_anchor_delta']}"
    print(f"SELF-TEST PASS: [eps0.2 N11] magnitude slope={c['mag_slope']:+.2f} (POSITIVE, human) vs chaining slope="
          f"{c['chain_slope']:+.2f} | hops near(d{ks[0]})={hops[ks[0]]:.1f} far(d{ks[-1]})={hops[ks[-1]]:.1f} "
          f"| END-ANCHOR mean delta={ea['mean_end_anchor_delta']:+.3f} (pos at {ea['frac_dist_with_positive_delta']*100:.0f}% of dists)")
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
    n_seeds = 80 if args.mode == "smoke" and not args.full else args.seeds
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
