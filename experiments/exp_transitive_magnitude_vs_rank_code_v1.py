"""DEEPENING / FINER BRAIN-FOUNDATIONAL DRILL -- which stored code produces the ordering AND the distance effect?
The brief (S3) names the OUR-INVENTION as "a magnitude-code placement, a relational-register integration, or a graded
settling" and asks whether a substrate-native mechanism produces the ordering + THE DISTANCE EFFECT. This isolates the
storage CODE, holding the integration (delta-rule settling) fixed.

TWO CANDIDATE STORES for the settled ordering:
  * MAGNITUDE (parietal, our mechanism): bind(item_key, FPE(scale * continuous_settled_position)). The position is the
    CONTINUOUS settled value -- NO argsort. Near positions have SIMILAR codes (a magnitude manifold), and the read-out
    gives a GRADED Weber confidence (continuous |dx|).
  * DISCRETE-RANK (a relational-binding alternative): bind(item_key, orthogonal_rank_code[argsort_rank]). Requires an
    explicit ARGSORT to assign each item a rank slot; the rank codes are mutually ORTHOGONAL (no magnitude manifold).

MEASURED RESULT (the disk overturned my prediction -- recorded honestly): BOTH stores answer the un-stated pairs, and
BOTH show an ACCURACY distance effect. The distance effect is therefore NOT diagnostic between them -- it is a property
of NOISY READ-OUT OF AN ORDER (bounded read-out error flips the sign of NEAR pairs more than FAR pairs), for a continuous
magnitude OR discrete ranks alike. That is a deeper, more correct statement of the Moyer signature than "the magnitude
metric causes it." What DOES distinguish the magnitude code: (a) it is SORT-FREE -- it encodes the continuous settled
position directly, whereas the discrete-rank store needs an explicit ARGSORT to assign slots (a symbolic step, less
brain-faithful); (b) it yields a GRADED Weber confidence (the human RT signature), not an integer rank gap. The
orthogonal discrete ranks buy some CAPACITY (less crosstalk) -- the honest trade-off. So the parietal magnitude-line is
preferred on FAITHFULNESS (no sort) and the graded confidence signal, not on a monopoly over the distance effect.

Run: .venv/Scripts/python.exe experiments/exp_transitive_magnitude_vs_rank_code_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_magnitude_vs_rank_code_v1/. NO hdlab write.
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
from experiments.exp_transitive_ordering_magnitude_line_v1 import (  # noqa: E402
    make_series, unstated_pairs, settle, _normalize_line, encode_register, decode_coord, _grid_codes,
    _sign, _boot_ci, FPE_SIGMA, POS_SCALE, GRID_MAX)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_magnitude_vs_rank_code_v1")
SEED = 20260828


def _decode_rank(S, key_i, rank_codes):
    """Recover item i's discrete rank slot: unbind its key, argmax similarity to the orthogonal rank codebook."""
    place = binding.unbind(S, key_i)
    p = place / place.abs().clamp_min(1e-12)
    sims = torch.real(rank_codes.conj() @ p) / place.shape[0]
    return int(torch.argmax(sims))


def one_trial(n, seed, d=512, noise_eps=0.0):
    premises, _ = make_series(n, seed, noise_eps=noise_eps)
    pairs = unstated_pairs(n, premises)
    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rank_codes = torch.stack([unit_phase_vec(d, g) for _ in range(n)], dim=0)   # orthogonal rank slots
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05); gc = _grid_codes(rates, grid)

    x = settle(premises, n, seed=seed)
    xn = _normalize_line(x)

    # MAGNITUDE store: continuous position -> FPE code (NO argsort)
    S_mag = encode_register(xn, keys, rates, POS_SCALE)
    xhat = np.array([decode_coord(S_mag, keys[i], rates, gc, grid) for i in range(n)])

    # DISCRETE-RANK store: argsort the settled scores -> orthogonal rank code per item (REQUIRES a sort)
    order = np.argsort(-x)                              # descending: rank 0 = biggest settled score
    item_rank = np.empty(n, dtype=int)
    for r, it in enumerate(order):
        item_rank[it] = r
    S_rank = torch.zeros(d, dtype=torch.complex64)
    for i in range(n):
        S_rank = S_rank + binding.bind(keys[i], rank_codes[item_rank[i]])
    rhat = np.array([_decode_rank(S_rank, keys[i], rank_codes) for i in range(n)])

    def truth(a, b):
        return 1 if a < b else -1
    rec = {"mag_acc": 0.0, "rank_acc": 0.0, "n": 0,
           "mag_by_dist": {}, "rank_by_dist": {}, "mag_conf_by_dist": {}}
    for p in pairs:
        a, b = p["a"], p["b"]; t = truth(a, b); dst = p["dist"]
        mag = 1.0 if _sign(xhat[a] - xhat[b]) == t else (0.5 if _sign(xhat[a] - xhat[b]) == 0 else 0.0)
        # rank: smaller rank index = bigger; so a>b iff item_rank_hat[a] < item_rank_hat[b]
        rk_s = _sign(rhat[b] - rhat[a])                # +1 if rank_a<rank_b => a bigger
        rk = 1.0 if rk_s == t else (0.5 if rk_s == 0 else 0.0)
        rec["mag_acc"] += mag; rec["rank_acc"] += rk; rec["n"] += 1
        rec["mag_by_dist"].setdefault(dst, [0.0, 0]); rec["mag_by_dist"][dst][0] += mag; rec["mag_by_dist"][dst][1] += 1
        rec["rank_by_dist"].setdefault(dst, [0.0, 0]); rec["rank_by_dist"][dst][0] += rk; rec["rank_by_dist"][dst][1] += 1
        rec["mag_conf_by_dist"].setdefault(dst, [0.0, 0]); rec["mag_conf_by_dist"][dst][0] += abs(xhat[a] - xhat[b]); rec["mag_conf_by_dist"][dst][1] += 1
    return rec


def cell(n, n_seeds, base_seed, d=512, noise_eps=0.0, n_boot=1500):
    mag, rank = [], []
    md, rd, mc = {}, {}, {}
    for s in range(n_seeds):
        t = one_trial(n, base_seed + s * 101, d=d, noise_eps=noise_eps)
        mag.append(t["mag_acc"] / t["n"]); rank.append(t["rank_acc"] / t["n"])
        for dct, key in [(md, "mag_by_dist"), (rd, "rank_by_dist"), (mc, "mag_conf_by_dist")]:
            for dst, (tot, cnt) in t[key].items():
                a = dct.setdefault(dst, [0.0, 0]); a[0] += tot; a[1] += cnt
    out = {"n": n, "d": d, "noise_eps": noise_eps, "n_seeds": n_seeds,
           "magnitude": _boot_ci(mag, n_boot=n_boot, seed=base_seed + 1),
           "discrete_rank": _boot_ci(rank, n_boot=n_boot, seed=base_seed + 2)}
    out["mag_dist"] = {int(k): round(v[0] / v[1], 4) for k, v in sorted(md.items())}
    out["rank_dist"] = {int(k): round(v[0] / v[1], 4) for k, v in sorted(rd.items())}
    out["mag_conf_dist"] = {int(k): round(v[0] / v[1], 4) for k, v in sorted(mc.items())}
    return out


def _slope(dist_map):
    """Sign of the correlation between distance and accuracy (positive = distance effect present)."""
    ks = sorted(dist_map)
    if len(ks) < 2:
        return 0.0
    xs = np.array(ks, float); ys = np.array([dist_map[k] for k in ks], float)
    return float(np.corrcoef(xs, ys)[0, 1]) if ys.std() > 1e-9 else 0.0


def run(n_seeds=150):
    out = {"anchor": "transitive_magnitude_vs_rank_code_v1", "seed": SEED}
    out["clean"] = cell(11, n_seeds, SEED, noise_eps=0.0)
    out["noisy"] = cell(11, n_seeds, SEED + 200, noise_eps=0.2)          # sub-ceiling: reveals the accuracy distance effect
    out["capacity"] = [cell(n, n_seeds, SEED + 400 + n, d=256) for n in [12, 20, 30]]  # honest capacity trade-off
    return out


def summarize(res):
    print("\n=== MAGNITUDE place-code vs DISCRETE-RANK binding (which produces the ordering AND the distance effect?) ===")
    for key in ["clean", "noisy"]:
        c = res[key]
        print(f"\n  [{key}] N={c['n']} eps={c['noise_eps']}: magnitude acc={c['magnitude']['mean']:.3f} "
              f"[{c['magnitude']['lo']:.3f},{c['magnitude']['hi']:.3f}]  discrete_rank acc={c['discrete_rank']['mean']:.3f} "
              f"[{c['discrete_rank']['lo']:.3f},{c['discrete_rank']['hi']:.3f}]")
        print(f"     magnitude accuracy by distance : {c['mag_dist']}   (slope {_slope(c['mag_dist']):+.2f})")
        print(f"     discrete  accuracy by distance : {c['rank_dist']}   (slope {_slope(c['rank_dist']):+.2f})")
        print(f"     magnitude Weber conf by distance: {c['mag_conf_dist']}")
    print("\n  --- CAPACITY (D=256; orthogonal ranks crosstalk less -> honest trade-off) ---")
    print("     N   magnitude  discrete_rank")
    for c in res["capacity"]:
        print(f"    {c['n']:>2d}   {c['magnitude']['mean']:.3f}      {c['discrete_rank']['mean']:.3f}")
    print("\n  READING (measured; overturned the naive prediction): BOTH stores answer the un-stated pairs and BOTH show")
    print("  the SAME accuracy distance effect -> the Moyer distance effect is a property of NOISY READ-OUT OF AN ORDER,")
    print("  not of the magnitude metric. The magnitude place-code is preferred because it is SORT-FREE (encodes the")
    print("  continuous settled position; the discrete store needs an explicit ARGSORT) and yields a GRADED Weber")
    print("  confidence (the human RT signature). The orthogonal discrete ranks buy CAPACITY (less manifold crosstalk)")
    print("  -- the honest trade-off: faithfulness + graded signal (magnitude) vs raw capacity (discrete rank).")


def self_test():
    c = cell(11, 60, 1, noise_eps=0.2, n_boot=800)
    ms = _slope(c["mag_dist"]); rs = _slope(c["rank_dist"])
    cs = _slope(c["mag_conf_dist"])
    assert c["magnitude"]["mean"] > 0.6, f"magnitude must answer un-stated pairs: {c['magnitude']}"
    assert c["discrete_rank"]["mean"] > 0.6, f"discrete-rank must also answer un-stated pairs: {c['discrete_rank']}"
    # CORRECTED finding: the distance effect is a read-out-noise property of ANY ordered code -> BOTH show it.
    assert ms > 0.5, f"MAGNITUDE must show an accuracy distance effect: {ms} {c['mag_dist']}"
    assert rs > 0.5, f"DISCRETE-RANK ALSO shows a distance effect (it is a read-out property, not magnitude-specific): {rs} {c['rank_dist']}"
    assert cs > 0.5, f"MAGNITUDE must give a graded Weber confidence rising with distance: {cs} {c['mag_conf_dist']}"
    print(f"SELF-TEST PASS: [noisy N11] magnitude acc={c['magnitude']['mean']:.3f} (dist slope {ms:+.2f}) "
          f"discrete_rank acc={c['discrete_rank']['mean']:.3f} (dist slope {rs:+.2f}) -> BOTH show the distance effect "
          f"(a read-out-noise property of any ordered code). Magnitude adds a graded Weber-confidence gradient "
          f"(slope {cs:+.2f}) and is SORT-FREE; discrete-rank needs an argsort.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--seeds", type=int, default=150)
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
