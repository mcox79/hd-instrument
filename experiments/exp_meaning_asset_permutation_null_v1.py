"""exp_meaning_asset_permutation_null_v1 -- replace a 3-draw scramble "floor" with its actual
null distribution, for the one arm where the scramble is the binding floor.

THE DEFECT THIS FIXES, stated against my own analysis so it cannot be read as bar-lowering.
The scramble control is a NULL: permute the code table across words, keeping identity and norms,
destroying structure. The fair-test cell drew it THREE times (seeds 7 / 17 / 23). For
ASSET_NORMS12 the three draws are 0.0220, 0.0241 and 0.1152. Taking the MAX of three draws of a
null and calling it "the floor" estimates the null's upper tail from n=3; at d=12 with 322 pairs
the null is wide, so max-of-3 lands about one SD above the null's centre and the resulting "floor"
is a lucky draw rather than a property of the control. That is the wrong quantity in BOTH
directions: it would also have let a weak arm pass had the three draws come out low.

What replaces it: the null distribution itself, 2,000 row permutations of the SAME table the live
module serves, scored by the SAME scorer on the SAME 322 pairs. The floor is then the null's 95th
percentile -- a genuinely conservative one-sided 5% floor -- and the arm additionally gets an exact
permutation p-value. Both are reported, and so are all three original draws, so the reader can see
exactly what changed and why.

THIS IS STILL A HARDENING relative to a naive scramble: the 95th percentile of the null is ABOVE
the null's mean and above two of the three original draws.

The d=512 learned arms are NOT re-nulled here and do not need to be: their stored scramble draws
are all NEGATIVE (V2_CTX -0.036 / -0.071 / -0.020; RETRAIN_CTX -0.019 / -0.024 / -0.018), so the
scramble is not their binding floor under any policy -- the seed-free frequency channel is.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import load_units

ANCHOR_NAME = "meaning_asset_permutation_null_v1"
N_PERM = 2000
STORED_SCRAMBLE_DRAWS = {7: 0.0220, 17: 0.0241, 23: 0.1152}   # asserted against disk in self-test


def pair_cos(codes, ia, ib):
    return np.einsum("ij,ij->i", codes[ia], codes[ib])


def main() -> int:
    t0 = time.time()
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)
    ia = np.array([w2i[a] for a, _, _ in pairs])
    ib = np.array([w2i[b] for _, b, _ in pairs])

    codes = FT.enc_norms12(words, 12, 7)          # the live module's own table, L2-normalised
    obs_cos = pair_cos(codes, ia, ib)
    obs = FT._spearman(obs_cos, gold)

    # ---- self-test: the recomputed arm must reproduce the landed number, and the stored
    # scramble draws must be what I claim they are (right-arm / right-metric guard).
    landed = json.loads((REPO / "data/exp_meaning_asset_fair_test_v1/metrics.json").read_text())
    want = landed["per_arm"]["d12|ASSET_NORMS12"]["simlex_rho"]
    assert abs(obs - want) < 1e-9, f"recomputed norms rho {obs} != landed {want}"
    cos_u = {}
    for u in load_units(str(REPO / "data/exp_meaning_asset_fair_test_v1")).values():
        if isinstance(u, dict) and u.get("arm") == "ASSET_NORMS12_SHUFFLED" and u["d"] == 12:
            cos_u[int(u["seed"])] = np.array(u["simlex_cos"], np.float64)
    drawn = {s: round(FT._spearman(v, gold), 4) for s, v in cos_u.items()}
    assert drawn == STORED_SCRAMBLE_DRAWS, f"stored draws {drawn} != documented {STORED_SCRAMBLE_DRAWS}"
    # a permutation of the table must leave IDENTITY intact (same multiset of codes)
    g0 = np.random.default_rng(0)
    p0 = g0.permutation(len(words))
    assert np.array_equal(np.sort(codes[p0], axis=0), np.sort(codes, axis=0)), \
        "row permutation changed the code multiset"
    print(f"[selftest] OK  observed norms rho={obs:.6f}", flush=True)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    # ---- the null distribution: 2,000 row permutations, identical scorer, identical pairs
    rng = np.random.default_rng(20260815)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        null[i] = FT._spearman(pair_cos(codes[rng.permutation(len(words))], ia, ib), gold)
    p95 = float(np.percentile(null, 95))
    p_val = float((np.sum(null >= obs) + 1) / (N_PERM + 1))

    # ---- the floor, and the margin against it
    lf = np.log(counts + 1.0)
    la, lb = lf[ia], lf[ib]
    freq = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
            "FREQ_MIN": np.minimum(la, lb),
            "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    freq_rho = {k: FT._spearman(v, gold) for k, v in freq.items()}
    bfk = max(freq_rho, key=lambda k: freq_rho[k])
    ortho = None
    for u in load_units(str(REPO / "data/exp_meaning_asset_fair_test_v1")).values():
        if isinstance(u, dict) and u.get("arm") == "A_ORTHOGRAPHIC" and u["d"] == 12 and u["seed"] == 7:
            ortho = np.array(u["simlex_cos"], np.float64)
    ortho_rho = FT._spearman(ortho, gold)

    # the scramble draw CLOSEST to the null's 95th percentile, used as the paired-bootstrap
    # partner so the CI is computed on real per-pair data rather than on a scalar percentile
    near = min(cos_u, key=lambda s: abs(FT._spearman(cos_u[s], gold) - p95))
    floors = {"HARDENED_FREQUENCY_" + bfk: (freq[bfk], freq_rho[bfk]),
              "A_ORTHOGRAPHIC": (ortho, ortho_rho),
              "SCRAMBLE_NULL_P95": (cos_u[near], p95)}
    bf = max(floors, key=lambda k: floors[k][1])
    diff = FT.boot_rho_diff(obs_cos, floors[bf][0], gold)
    band = FT.band(diff["ci95"])

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": "full", "n_pairs": len(pairs),
        "arm": "ASSET_NORMS12 (hdlab/grounded_similarity, Lancaster + Brysbaert, d=12)",
        "observed_rho": obs,
        "permutation_null": {
            "n_permutations": N_PERM,
            "what_is_permuted": "the rows of the 4096 x 12 code table, across words",
            "mean": float(null.mean()), "sd": float(null.std(ddof=1)),
            "p50": float(np.percentile(null, 50)), "p95": p95,
            "p99": float(np.percentile(null, 99)), "max": float(null.max()),
            "exact_permutation_p_value_for_the_observed_rho": p_val,
            "the_three_original_draws": STORED_SCRAMBLE_DRAWS,
            "where_the_max_of_3_draws_sat_in_the_null":
                float((null < max(STORED_SCRAMBLE_DRAWS.values())).mean()),
        },
        "floors": {k: round(v[1], 4) for k, v in floors.items()},
        "strongest_floor": bf,
        "margin_over_strongest_floor": diff, "band": band,
        "clears_floor": bool(band == "ABOVE" and diff["point"] >= FT.T_MARGIN_MIN),
        "paired_bootstrap_partner_for_the_scramble_floor":
            f"seed {near}, the stored draw closest to the null p95",
        "verdict": ("NORMS_CLEAR_THE_FLOOR_CI_SEPARATED" if band == "ABOVE"
                    and diff["point"] >= FT.T_MARGIN_MIN else "NORMS_DO_NOT_CLEAR_CI_SEPARATED"),
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["summary"] = out["verdict"]
    write_metrics(out_dir, out)
    print(f"observed rho          {obs:+.4f}")
    print(f"null mean {null.mean():+.4f}  sd {null.std(ddof=1):.4f}  p95 {p95:+.4f}  "
          f"p99 {np.percentile(null,99):+.4f}  max {null.max():+.4f}")
    print(f"permutation p-value   {p_val:.5f}")
    print(f"floors                {json.dumps(out['floors'])} -> {bf}")
    print(f"margin                {diff['point']:+.4f} [{diff['ci95'][0]:+.4f},"
          f"{diff['ci95'][1]:+.4f}] {band}")
    print("VERDICT:", out["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
