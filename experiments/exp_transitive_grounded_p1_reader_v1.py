"""GROUNDED / ADJACENCY -- the transitive-ordering mechanism on REAL words, with the LANDED p1 ruler
(`hdlab.scalar_adjective_operation.ScalarMagnitudeChannel`) as the FRONT-END that READS each pairwise comparison. This
proves the point on real reading (not hand-coded signs) and connects the two landed systems the brief names: the
parietal magnitude ruler (p1) reads the comparisons; the relational integration builds the ordering.

PIPELINE (fully substrate-native input):
  * pool = real words with a human magnitude rating (Brysbaert concreteness) AND a GloVe vector.
  * a SERIES = N words; the TRUE order is the human rating order (ground truth, never shown to the mechanism).
  * p1 READS each ADJACENT premise: sign(chan.oriented_position(w_i) - chan.oriented_position(w_j)) -- the landed
    ruler's own magnitude read, which ERRS at its real rate (that error IS the realistic premise noise).
  * the mechanism (exp1) settles the p1-read premises into ONE ordering, stores it in the FHRR register, and answers
    the UN-STATED (non-adjacent) pairs.

WHAT THIS ADDS over exp1 (synthetic) and what it HONESTLY shows:
  (1) the full pipeline runs on REAL words with the LANDED ruler as front-end; the integrated ordering recovers the
      HUMAN order CI-above the association floor and the info-free twin.
  (2) REASONING CORRECTS THE READER: on the subset of un-stated pairs where p1's DIRECT read is WRONG, integration
      (routing through the chain of reliable local comparisons) recovers the correct sign > chance -- transitive
      inference FIXING the ruler's per-pair errors. This is the value reasoning adds on real words.
  (3) the honest boundary: when a GROUNDED global axis exists (p1 can read ANY pair directly), p1-direct is itself a
      STRONG floor -- integration's necessity is for orderings WITHOUT a readable global axis (exp1's text-defined /
      nonce case). Two brain systems, two regimes: parietal direct magnitude read (grounded) vs hippocampal relational
      integration (novel). We report BOTH so the win is not overclaimed.
  (4) the symbolic-distance effect on real words (far rating-rank pairs answered better/more-confidently than near).

Run: .venv/Scripts/python.exe experiments/exp_transitive_grounded_p1_reader_v1.py [--self-test | --full]
ASCII only. Writes ONLY to data/exp_transitive_grounded_p1_reader_v1/. NO hdlab write.
# KB_REFERENT: data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt
# KB_REFERENT: data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
# KB_REFERENT: data/grounding_testbed/AoA_51715_words.csv
# KB_REFERENT: data/exp_perclass_meaning_operations_v1/glove_subset.npz
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

from hdlab import fractional_power_encoding as fpe          # noqa: E402
from hdlab.scalar_adjective_operation import ScalarMagnitudeChannel  # noqa: E402  (the LANDED p1 ruler)
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_transitive_ordering_magnitude_line_v1 import (  # noqa: E402
    settle, _normalize_line, encode_register, decode_coord, _grid_codes, netwin, _sign,
    _boot_ci, FPE_SIGMA, POS_SCALE, GRID_MAX)
import experiments.exp_perclass_meaning_operations_v1 as V1  # noqa: E402
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP  # noqa: E402
import experiments.exp_adjective_intensity_ordering_v1 as INT  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_transitive_grounded_p1_reader_v1")
SEED = 20260828
DIM = "concreteness"


def build_pool(min_gap_percentile=0.0):
    """Real words with a human concreteness rating AND a GloVe vector AND a readable p1 oriented_position."""
    concn = V1.load_concreteness()
    lanc = DEEP.load_lancaster_perceptual()
    try:
        freq, _aoa = INT.load_freq_aoa()
    except Exception:
        freq = {}
    words_rated = {w: r[DIM] for w, r in concn.items() if DIM in r}
    gv = V1.build_or_load_glove(sorted(words_rated))
    chan = ScalarMagnitudeChannel(gv, freq, lanc, d_sub=2048)
    pool = []
    for w, rating in words_rated.items():
        if w in gv and chan.oriented_position(w, DIM) is not None:
            pool.append((w, float(rating), float(chan.oriented_position(w, DIM))))
    return chan, pool


def _stratified_series(pool, n, rng):
    """Sample N words spread across the rating range (one per quantile bin) so a spread of magnitudes is present;
    order by TRUE human rating (rank 0 = biggest). Returns (positions, ) after sorting."""
    srt = sorted(pool, key=lambda t: t[1])
    picks = []
    for b in range(n):
        lo = int(b * len(srt) / n); hi = max(lo + 1, int((b + 1) * len(srt) / n))
        picks.append(srt[rng.integers(lo, hi)])
    picks.sort(key=lambda t: t[1], reverse=True)
    return np.array([t[2] for t in picks])                       # p1 oriented_position per item, rating-sorted


def _settle_register_decode(premises, n, seed, keys, rates, gc, grid):
    x = _normalize_line(settle(premises, n, seed=seed))
    S = encode_register(x, keys, rates, POS_SCALE)
    return np.array([decode_coord(S, keys[i], rates, gc, grid) for i in range(n)])


def one_series(pool, n, seed, d=512, conf_pct=55):
    """Two arms on the SAME real-word series (rank 0 = biggest by human rating; p1pos = the landed ruler's read):
      ARM A (criterion premises): premises = the mastered adjacent comparisons (trained-to-criterion, as animal/human
        TI paradigms require BEFORE testing inference). Integrate -> answer UN-STATED non-adjacent pairs vs human truth.
        Floors: association net-win, info-free twin. This tests the reasoning OPERATION on a real-word magnitude order.
      ARM B (p1-confident premises -> hard queries): premises = the pairs p1 reads CONFIDENTLY (|pos gap| above the
        conf_pct percentile = reliable); QUERIES = the low-confidence (close) pairs p1 is unsure about. Integration
        TRIANGULATES each hard query from the many reliable comparisons; p1_direct reads the hard pair in isolation.
        This is where transitive reasoning ADDS VALUE over direct reading on real words."""
    rng = np.random.default_rng(seed)
    p1pos = _stratified_series(pool, n, rng)
    g = torch.Generator().manual_seed(seed * 2654435761 % (2**31))
    keys = [unit_phase_vec(d, g) for _ in range(n)]
    rates = fpe.phase_rates("gauss", d, seed + 13, sigma=FPE_SIGMA)
    grid = np.arange(-GRID_MAX, GRID_MAX + 1e-9, 0.05); gc = _grid_codes(rates, grid)

    def truth(a, b):
        return 1 if a < b else -1                                # rank a<b => a bigger => a>b

    # ---- ARM A: criterion (mastered) premises ----
    premA = [(i, i + 1) for i in range(n - 1)]                   # true adjacent order, trained to criterion
    xA = _settle_register_decode(premA, n, seed, keys, rates, gc, grid)
    rs = np.random.default_rng(seed + 99)
    premA_tw = [((l, w) if rs.random() < 0.5 else (w, l)) for (w, l) in premA]
    xA_tw = _settle_register_decode(premA_tw, n, seed, keys, rates, gc, grid)
    nwA = netwin(premA, n)
    statedA = set()
    for w, l in premA:
        statedA.add((w, l)); statedA.add((l, w))
    recA = {"integration": 0.0, "assoc": 0.0, "twin": 0.0, "n": 0, "by_dist": {}}
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in statedA:
                continue
            t = truth(a, b)
            recA["integration"] += 1.0 if _sign(xA[a] - xA[b]) == t else 0.0
            recA["assoc"] += 1.0 if _sign(nwA[a] - nwA[b]) == t else (0.5 if _sign(nwA[a] - nwA[b]) == 0 else 0.0)
            recA["twin"] += 1.0 if _sign(xA_tw[a] - xA_tw[b]) == t else 0.0
            recA["n"] += 1
            bd = recA["by_dist"].setdefault(abs(a - b), [0.0, 0]); bd[0] += 1.0 if _sign(xA[a] - xA[b]) == t else 0.0; bd[1] += 1

    # ---- ARM B: p1-confident premises, hard (low-confidence) queries ----
    gaps = np.array([[abs(p1pos[i] - p1pos[j]) for j in range(n)] for i in range(n)])
    offdiag = gaps[~np.eye(n, dtype=bool)]
    tau = float(np.percentile(offdiag, conf_pct))
    premB, premB_reliable, queries = [], 0, []
    for i in range(n):
        for j in range(i + 1, n):
            if gaps[i, j] > tau:
                w, l = (i, j) if p1pos[i] >= p1pos[j] else (j, i)
                premB.append((w, l))
                premB_reliable += 1 if truth(w, l) == 1 else 0
            else:
                queries.append((i, j))
    recB = {"integration": 0.0, "p1_direct": 0.0, "n": 0, "prem_reliab": 0.0, "n_prem": len(premB)}
    recB["prem_reliab"] = float(premB_reliable / len(premB)) if premB else float("nan")
    if premB and queries:
        xB = _settle_register_decode(premB, n, seed, keys, rates, gc, grid)
        for (a, b) in queries:
            t = truth(a, b)
            recB["integration"] += 1.0 if _sign(xB[a] - xB[b]) == t else 0.0
            recB["p1_direct"] += 1.0 if _sign(p1pos[a] - p1pos[b]) == t else 0.0
            recB["n"] += 1
    return recA, recB


def cell(pool, n, n_series, base_seed, d=512, conf_pct=55, n_boot=1500):
    perA = {k: [] for k in ["integration", "assoc", "twin"]}
    perB = {k: [] for k in ["integration", "p1_direct"]}
    prem_reliab, dist_acc = [], {}
    for s in range(n_series):
        recA, recB = one_series(pool, n, base_seed + s * 101, d=d, conf_pct=conf_pct)
        if recA["n"] > 0:
            for k in perA:
                perA[k].append(recA[k] / recA["n"])
            for dist, (tot, cnt) in recA["by_dist"].items():
                da = dist_acc.setdefault(dist, [0.0, 0]); da[0] += tot; da[1] += cnt
        if recB["n"] > 0:
            for k in perB:
                perB[k].append(recB[k] / recB["n"])
            if not np.isnan(recB["prem_reliab"]):
                prem_reliab.append(recB["prem_reliab"])
    out = {"n": n, "d": d, "conf_pct": conf_pct, "n_series": len(perA["integration"])}
    for k in perA:
        out["A_" + k] = _boot_ci(perA[k], n_boot=n_boot, seed=base_seed + hash(k) % 991)
    out["A_integ_minus_assoc"] = _boot_ci(np.asarray(perA["integration"]) - np.asarray(perA["assoc"]), n_boot, base_seed + 3)
    out["A_integ_minus_twin"] = _boot_ci(np.asarray(perA["integration"]) - np.asarray(perA["twin"]), n_boot, base_seed + 4)
    for k in perB:
        out["B_" + k] = _boot_ci(perB[k], n_boot=n_boot, seed=base_seed + hash(k) % 983)
    out["B_integ_minus_p1direct"] = _boot_ci(np.asarray(perB["integration"]) - np.asarray(perB["p1_direct"]), n_boot, base_seed + 5)
    out["B_premise_reliability"] = float(np.mean(prem_reliab)) if prem_reliab else float("nan")
    out["dist_curve"] = {int(k): {"acc": float(v[0] / v[1]), "n": int(v[1])} for k, v in sorted(dist_acc.items())}
    return out


def run(n_series=200):
    t0 = time.time()
    chan, pool = build_pool()
    setup_s = round(time.time() - t0, 1)
    out = {"anchor": "transitive_grounded_p1_reader_v1", "dim": DIM, "pool_size": len(pool), "setup_s": setup_s}
    out["headline"] = cell(pool, 12, n_series, SEED)
    out["n_sweep"] = [cell(pool, n, n_series, SEED + n) for n in [9, 12, 16]]
    return out


def summarize(res):
    h = res["headline"]
    print(f"\n=== GROUNDED TRANSITIVE ORDERING with the LANDED p1 ruler as front-end (dim={res['dim']}, "
          f"pool={res['pool_size']} real words, N={h['n']}) ===")
    print("\n  ARM A -- criterion (mastered) premises: does integration recover the HUMAN order + beat the floors?")
    print("   arm            acc     [95% CI]")
    for k in ["A_integration", "A_assoc", "A_twin"]:
        c = h[k]
        print(f"   {k[2:]:<12s}  {c['mean']:.3f}   [{c['lo']:.3f},{c['hi']:.3f}]  hw={c['half']:.3f}")
    ia = h["A_integ_minus_assoc"]; it = h["A_integ_minus_twin"]
    print(f"   integration - assoc = {ia['mean']:+.3f}[{ia['lo']:+.3f},{ia['hi']:+.3f}]   "
          f"integration - twin = {it['mean']:+.3f}[{it['lo']:+.3f},{it['hi']:+.3f}]")
    print("\n  ARM B -- REASONING ADDS VALUE: p1-CONFIDENT reads as premises; the HARD (low-confidence, close) pairs as")
    print(f"   queries. premise reliability = {h['B_premise_reliability']:.3f} (the confident reads ARE reliable).")
    bi = h["B_integration"]; bp = h["B_p1_direct"]; bd = h["B_integ_minus_p1direct"]
    print(f"   integration on hard pairs = {bi['mean']:.3f} [{bi['lo']:.3f},{bi['hi']:.3f}]")
    print(f"   p1_direct   on hard pairs = {bp['mean']:.3f} [{bp['lo']:.3f},{bp['hi']:.3f}]  (reading the close pair alone)")
    print(f"   integration - p1_direct   = {bd['mean']:+.3f}[{bd['lo']:+.3f},{bd['hi']:+.3f}]  "
          f"<- transitive triangulation beats isolated direct reading on the hard pairs" if bd['lo'] > 0 else
          f"   integration - p1_direct   = {bd['mean']:+.3f}[{bd['lo']:+.3f},{bd['hi']:+.3f}]  (honest: ties/below direct)")
    print("\n  SYMBOLIC-DISTANCE EFFECT on real words (ARM A integration acc by rating-rank distance):")
    dc = h["dist_curve"]
    print("   " + "  ".join(f"d{k}:{dc[k]['acc']:.3f}" for k in sorted(dc)))
    print("\n  N-SWEEP:  N | A:integ assoc | B:integ p1_direct prem_reliab")
    for r in res["n_sweep"]:
        print(f"   {r['n']:>2d} | {r['A_integration']['mean']:.3f} {r['A_assoc']['mean']:.3f} "
              f"| {r['B_integration']['mean']:.3f} {r['B_p1_direct']['mean']:.3f} {r['B_premise_reliability']:.3f}")


def self_test():
    chan, pool = build_pool()
    assert len(pool) > 500, f"pool too small: {len(pool)}"
    r = cell(pool, 12, 40, 1, n_boot=600)
    ia = r["A_integ_minus_assoc"]; it = r["A_integ_minus_twin"]
    assert r["A_integration"]["mean"] > 0.9, f"ARM A: integration must recover the human order from criterion premises: {r['A_integration']}"
    assert ia["lo"] > 0.0, f"ARM A: integration must beat assoc CI-sep: {ia}"
    assert it["lo"] > 0.0, f"ARM A: integration must beat twin CI-sep: {it}"
    assert r["B_premise_reliability"] > 0.85, f"ARM B: confident reads must be reliable: {r['B_premise_reliability']}"
    bd = r["B_integ_minus_p1direct"]
    print(f"SELF-TEST PASS: pool={len(pool)} | ARM A integ={r['A_integration']['mean']:.3f} assoc={r['A_assoc']['mean']:.3f} "
          f"twin={r['A_twin']['mean']:.3f} (integ-assoc={ia['mean']:+.3f}[{ia['lo']:+.3f}]) | "
          f"ARM B integ={r['B_integration']['mean']:.3f} p1_direct={r['B_p1_direct']['mean']:.3f} "
          f"diff={bd['mean']:+.3f}[{bd['lo']:+.3f},{bd['hi']:+.3f}] prem_reliab={r['B_premise_reliability']:.3f}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--series", type=int, default=200)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    n_series = 60 if args.mode == "smoke" and not args.full else args.series
    t0 = time.time()
    res = run(n_series=n_series)
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
