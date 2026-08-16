"""exp_meaning_asset_hardened_margins_v1 -- the HEADLINE table: every asset arm's SimLex margin
over max(ORTHOGRAPHIC, STRONGEST SEED-FREE FREQUENCY, that arm's own SCRAMBLE), paired-bootstrapped
on the identical 322 pairs.

Why this exists rather than being the main cell's number: the main cell's frequency floor lifts
log-frequency through a RANDOM projection, so its rho moves with a nuisance seed (0.0916 /
-0.0161 / -0.0047 at d=512). exp_meaning_asset_floor_hardening_v1 measured the SEED-FREE frequency
channels directly on the pair scores and found a STRONGER one. The standing rule says the floor is
the STRONGEST no-understanding baseline, so the hardened floor is the one that governs, and every
margin is recomputed against it here. This can only make the assets look WORSE, never better.

Reads the already-computed per-pair cosines out of the cells' units.jsonl; computes nothing new
about any arm.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
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

ANCHOR_NAME = "meaning_asset_hardened_margins_v1"
SRC = ["data/exp_meaning_asset_fair_test_v1", "data/exp_meaning_asset_fair_test_v1b_distributional"]


def main() -> int:
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs])
    lf = np.log(counts + 1.0)
    la = np.array([lf[w2i[a]] for a, _, _ in pairs])
    lb = np.array([lf[w2i[b]] for _, b, _ in pairs])
    freq_channels = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
                     "FREQ_MIN": np.minimum(la, lb),
                     "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    freq_rho = {k: FT._spearman(v, gold) for k, v in freq_channels.items()}
    best_freq = max(freq_rho, key=lambda k: freq_rho[k])

    cos = {}
    for s in SRC:
        for u in load_units(str(REPO / s)).values():
            if not isinstance(u, dict) or "simlex_cos" not in u:
                continue
            key = f"d{u['d']}|{u['arm']}"
            cos.setdefault(key, {})[int(u["seed"])] = np.array(u["simlex_cos"])
            if len(u["simlex_cos"]) != len(pairs):
                raise SystemExit(f"[fatal] pair-set mismatch for {key}: "
                                 f"{len(u['simlex_cos'])} vs {len(pairs)}")

    rows = {}
    for key, byseed in sorted(cos.items()):
        d, arm = key.split("|", 1)
        if arm.endswith("_SHUFFLED") or arm in ("A_COLLAPSE", "A_RANDOM_IID", "A_FREQUENCY"):
            continue
        c = byseed[min(byseed)]
        cands = {"HARDENED_FREQUENCY_" + best_freq: freq_channels[best_freq]}
        ortho = cos.get(f"{d}|A_ORTHOGRAPHIC")
        if ortho:
            cands["A_ORTHOGRAPHIC"] = ortho[min(ortho)]
        sh = cos.get(f"{d}|{arm}_SHUFFLED")
        if sh:
            cands["OWN_SCRAMBLE"] = sh[min(sh)]
        rho_f = {k: FT._spearman(v, gold) for k, v in cands.items()}
        bf = max(rho_f, key=lambda k: rho_f[k])
        diff = FT.boot_rho_diff(c, cands[bf], gold)
        rows[key] = {
            "arm_rho": FT.boot_rho(c, gold),
            "floor_rho_by_arm": {k: round(v, 4) for k, v in rho_f.items()},
            "strongest_floor": bf,
            "margin_over_strongest_floor": diff,
            "band": FT.band(diff["ci95"]),
            "clears_floor": bool(FT.band(diff["ci95"]) == "ABOVE"
                                 and diff["point"] >= FT.T_MARGIN_MIN),
        }

    clears = [k for k, v in rows.items() if v["clears_floor"] and "|ASSET_" in k]
    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full", "n_pairs": len(pairs),
           "hardened_frequency_floor": {"channel": best_freq, "rho": round(freq_rho[best_freq], 4),
                                        "all_channels": {k: round(v, 4)
                                                         for k, v in freq_rho.items()}},
           "predeclared_margin_min": FT.T_MARGIN_MIN,
           "verdict": ("ASSET_CLEARS_THE_HARDENED_FLOOR" if clears
                       else "NO_ASSET_CLEARS_THE_HARDENED_FLOOR"),
           "arms_clearing": clears, "rows": rows,
           "note": ("Every margin is a PAIRED bootstrap over the identical 322 SimLex pairs, "
                    "10,000 resamples. Hardening the floor can only lower a margin.")}
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, out)
    for k, v in sorted(rows.items(), key=lambda kv: -kv[1]["arm_rho"]["point"]):
        m = v["margin_over_strongest_floor"]
        print(f"{k:<44} rho={v['arm_rho']['point']:+.4f} "
              f"[{v['arm_rho']['ci95'][0]:+.4f},{v['arm_rho']['ci95'][1]:+.4f}]  "
              f"floor={v['strongest_floor']:<28} margin={m['point']:+.4f} "
              f"[{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] {v['band']}")
    print("VERDICT:", out["verdict"], clears)
    return 0


if __name__ == "__main__":
    sys.exit(main())
