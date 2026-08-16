"""exp_meaning_asset_vs_production_v1 -- the comparison that decides "would wiring this help?".

Clearing a zero-meaning floor is necessary and not sufficient. The operational question is whether
a built-but-unwired asset beats WHAT WE ALREADY RUN. The live concept profile P_LIVE_CONCEPT (the
graded accumulated context_vector_masked sum that canonicalize_fast actually reads) is the
incumbent, and the parent instrument scored it at SimLex rho 0.1048 with a CI touching zero.

This cell paired-bootstraps every asset arm against the INCUMBENT on the identical 322 SimLex
pairs, reusing the parent instrument's OWN cached concept profiles
(data/exp_encoding_quality_instrument_v2/concept_profiles_d256_V4096_B64000000.npz, built by the
instrument run itself with a byte-equality assertion against the live context_vector_masked) so
the incumbent arm is not a reimplementation.

Gate on the incumbent's reproduction: the recomputed P_LIVE_CONCEPT SimLex rho must equal the
published 0.10477736169182189 to 1e-9, or nothing here is reported.

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

ANCHOR_NAME = "meaning_asset_vs_production_v1"
CACHE = (REPO / "data" / "exp_encoding_quality_instrument_v2"
         / "concept_profiles_d256_V4096_B64000000.npz")
PUBLISHED_RHO = 0.10477736169182189
SRC = ["data/exp_meaning_asset_fair_test_v1", "data/exp_meaning_asset_fair_test_v1b_distributional"]


def main() -> int:
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs])

    if not CACHE.exists():
        raise SystemExit(f"[fatal] the instrument's concept-profile cache is missing: {CACHE}")
    z = np.load(CACHE, allow_pickle=True)
    prof = INS._l2n(z["profiles"])
    collide = z["collide"]
    inc_cos = np.array([float(prof[w2i[a]] @ prof[w2i[b]]) for a, b, _ in pairs])
    inc_rho = FT._spearman(inc_cos, gold)
    if abs(inc_rho - PUBLISHED_RHO) > 1e-9:
        raise SystemExit(f"[fatal] incumbent reproduction failed: {inc_rho} vs {PUBLISHED_RHO}")
    print(f"[incumbent] P_LIVE_CONCEPT rho={inc_rho:.10f} reproduces published to 1e-9", flush=True)

    # the incumbent's own scramble, same construction as the instrument's C_CONCEPT_SHUFFLED
    sh = prof[np.random.default_rng(7 ^ 0xC0FFEE).permutation(len(words))]
    sh_cos = np.array([float(sh[w2i[a]] @ sh[w2i[b]]) for a, b, _ in pairs])

    rows = {}
    for s in SRC:
        for u in load_units(str(REPO / s)).values():
            if not isinstance(u, dict) or "simlex_cos" not in u:
                continue
            if int(u["seed"]) != 7 or u["arm"].endswith("_SHUFFLED"):
                continue
            key = f"d{u['d']}|{u['arm']}"
            if key in rows:
                continue
            c = np.array(u["simlex_cos"])
            if len(c) != len(pairs):
                raise SystemExit(f"[fatal] pair-set mismatch for {key}")
            d = FT.boot_rho_diff(c, inc_cos, gold)
            rows[key] = {"arm_rho": round(FT._spearman(c, gold), 4),
                         "incumbent_rho": round(inc_rho, 4),
                         "difference_vs_incumbent": d, "band": FT.band(d["ci95"]),
                         "beats_incumbent_CI_separated": FT.band(d["ci95"]) == "ABOVE"}

    beats = sorted(k for k, v in rows.items() if v["beats_incumbent_CI_separated"])
    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full", "n_pairs": len(pairs),
           "incumbent": {"arm": "P_LIVE_CONCEPT", "d": 256, "rho": inc_rho,
                         "published_rho": PUBLISHED_RHO,
                         "rho_bootstrap": FT.boot_rho(inc_cos, gold),
                         "own_scramble_rho": round(FT._spearman(sh_cos, gold), 4),
                         "lemma_collisions_in_vocab": int(collide.sum()),
                         "source": str(CACHE.relative_to(REPO)).replace("\\", "/")},
           "verdict": ("AN_ASSET_BEATS_THE_INCUMBENT" if beats
                       else "NO_ASSET_BEATS_THE_INCUMBENT_CI_SEPARATED"),
           "arms_beating_incumbent": beats, "rows": rows,
           "reading_rule": ("beating the incumbent is NOT the same as clearing the zero-meaning "
                            "floor; the incumbent itself does not clear it. Both must hold before "
                            "'wire it' is an evidenced recommendation.")}
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, out)
    for k, v in sorted(rows.items(), key=lambda kv: -kv[1]["arm_rho"]):
        d = v["difference_vs_incumbent"]
        print(f"{k:<44} rho={v['arm_rho']:+.4f}  vs incumbent {inc_rho:+.4f}: "
              f"{d['point']:+.4f} [{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}] {v['band']}")
    print("VERDICT:", out["verdict"], beats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
