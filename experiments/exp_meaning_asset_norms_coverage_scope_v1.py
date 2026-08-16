"""exp_meaning_asset_norms_coverage_scope_v1 -- how far can the norm asset speak, and how much
of its score is dilution from the words it does not cover.

WHY. ASSET_NORMS12 is scored on the instrument's 4,096-word vocabulary, but hdlab/grounded_similarity
only has 36,810 words and 1,474 of the instrument's 4,096 are NOT among them. The fair-test cell
gives every missing word a tiny random vector (fair: no signal), so the arm's headline rho mixes a
real signal on covered pairs with noise on uncovered ones. Two things follow that a single number
cannot express, and both are decision-relevant if the question is "is this asset the ceiling":

  1. the SCOPE-RESTRICTED score -- what the asset is worth on the pairs it actually covers;
  2. the COVERAGE itself -- the fraction of items it can say anything at all about, which caps any
     downstream architecture built on it no matter how good the covered-subset score is.

The scope-restricted number is on a DIFFERENT ITEM POPULATION and is NOT the like-for-like
instrument number. It is labelled as such everywhere and must never be quoted as the headline.
Every floor is recomputed on each restricted population so no comparison crosses populations.

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

ANCHOR_NAME = "meaning_asset_norms_coverage_scope_v1"
SRC = "data/exp_meaning_asset_fair_test_v1"
SCOPE_NOTE = ("SCOPE-RESTRICTED. The COVERED_BOTH population is the subset of the instrument's 322 "
              "SimLex pairs where BOTH words are in the norm table. It is NOT the like-for-like "
              "instrument population and its numbers may not be quoted as the headline result.")


def main() -> int:
    t0 = time.time()
    from hdlab import grounded_similarity as GS
    tab = GS._table()

    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)
    assert len(pairs) == 322, len(pairs)

    cov = np.array([(a.lower() in tab and b.lower() in tab) for a, b, _ in pairs])
    # coverage of the whole SimLex-999, independent of the instrument's vocabulary
    all_simlex = INS.load_simlex(INS.SIMLEX)
    cov_all = sum(1 for a, b, _ in all_simlex if a.lower() in tab and b.lower() in tab)

    cos = {}
    for u in load_units(str(REPO / SRC)).values():
        if isinstance(u, dict) and "simlex_cos" in u and u["d"] == 12:
            cos.setdefault(u["arm"], {})[int(u["seed"])] = np.array(u["simlex_cos"], np.float64)

    lf = np.log(counts + 1.0)
    la = np.array([lf[w2i[a]] for a, _, _ in pairs])
    lb = np.array([lf[w2i[b]] for _, b, _ in pairs])
    freq_channels = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
                     "FREQ_MIN": np.minimum(la, lb),
                     "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}

    # MEASURED, not assumed: whether the mask splits the population at all. It does NOT --
    # all 322 instrument pairs are covered by the norm table, so the headline norms number
    # carries NO out-of-vocabulary dilution. Recorded rather than asserted, because the fact
    # itself is the result; an assertion here would have failed on a true finding.
    fully_covered = bool(cov.all())
    n_miss_vocab = sum(1 for w in words if w.lower() not in tab)
    recorded = json.loads((REPO / "data/exp_meaning_asset_fair_test_v1/metrics.json").read_text())
    assert n_miss_vocab == recorded["norms_missing_in_vocab"], (
        f"vocab miss {n_miss_vocab} != recorded {recorded['norms_missing_in_vocab']}")
    assert abs(FT._spearman(cos["ASSET_NORMS12"][7], gold)
               - recorded["per_arm"]["d12|ASSET_NORMS12"]["simlex_rho"]) < 1e-12
    print("[selftest] OK", flush=True)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    pops = {"ALL_322_like_for_like": np.ones(len(pairs), bool)}
    if not fully_covered:
        pops["COVERED_BOTH"] = cov
        pops["AT_LEAST_ONE_UNCOVERED"] = ~cov
    out_pops = {}
    for pname, m in pops.items():
        g = gold[m]
        if m.sum() < 10:
            out_pops[pname] = {"n_pairs": int(m.sum()), "skipped": "under 10 pairs"}
            continue
        fr = {k: FT._spearman(v[m], g) for k, v in freq_channels.items()}
        bfk = max(fr, key=lambda k: fr[k])
        cands = {"HARDENED_FREQUENCY_" + bfk: freq_channels[bfk][m]}
        for fl in ("A_ORTHOGRAPHIC", "ASSET_NORMS12_SHUFFLED"):
            if fl in cos:
                bs = max(cos[fl], key=lambda s: FT._spearman(cos[fl][s][m], g))
                cands["OWN_SCRAMBLE" if "SHUF" in fl else fl] = cos[fl][bs][m]
        rho_f = {k: FT._spearman(v, g) for k, v in cands.items()}
        bf = max(rho_f, key=lambda k: rho_f[k])
        arms = {}
        for arm in ("ASSET_NORMS12", "CTRL_CONCRETENESS_ONLY", "P_LIVE_WORD"):
            if arm not in cos:
                continue
            c = cos[arm][7][m]
            d = FT.boot_rho_diff(c, cands[bf], g)
            arms[arm] = {"rho": FT.boot_rho(c, g), "margin_over_strongest_floor": d,
                         "band": FT.band(d["ci95"]),
                         "clears_floor": bool(FT.band(d["ci95"]) == "ABOVE"
                                              and d["point"] >= FT.T_MARGIN_MIN)}
        out_pops[pname] = {"n_pairs": int(m.sum()),
                           "frequency_channels_rho": {k: round(v, 4) for k, v in fr.items()},
                           "floor_rho_by_arm": {k: round(v, 4) for k, v in rho_f.items()},
                           "strongest_floor": bf, "arms": arms}

    key = "COVERED_BOTH" if not fully_covered else "ALL_322_like_for_like"
    covered = out_pops.get(key, {}).get("arms", {}).get("ASSET_NORMS12")
    verdict = ("NORMS_SIGNAL_IS_REAL_ON_THE_WORDS_IT_COVERS"
               if covered and covered["clears_floor"]
               else "NORMS_DO_NOT_CLEAR_ON_THE_POPULATION_THEY_COVER")

    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full", "scope_disclaimer": SCOPE_NOTE,
           "verdict": verdict,
           "coverage": {
               "norm_table_words": len(tab),
               "instrument_vocab": len(words),
               "instrument_vocab_covered": len(words) - n_miss_vocab,
               "instrument_vocab_covered_fraction": round(1 - n_miss_vocab / len(words), 4),
               "instrument_pairs_total": len(pairs),
               "instrument_pairs_both_covered": int(cov.sum()),
               "instrument_pairs_both_covered_fraction": round(float(cov.mean()), 4),
               "instrument_pairs_FULLY_covered_so_no_OOV_dilution": fully_covered,
               "whole_simlex999_pairs_both_covered": cov_all,
               "whole_simlex999_pairs_both_covered_fraction": round(cov_all / len(all_simlex), 4),
               "oov_policy_in_the_fair_test": ("missing words get a 1e-3 gaussian vector, then L2 "
                                               "normalised -- a random direction, i.e. no signal"),
           },
           "populations": out_pops,
           "reading_rule": ("COVERED_BOTH says what the asset is worth WHERE IT SPEAKS. Coverage "
                            "says how often it speaks at all. A ceiling claim needs both: a high "
                            "covered-subset score on a low-coverage asset still caps the system.")}
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["summary"] = verdict
    write_metrics(out_dir, out)
    for pname, pv in out_pops.items():
        print(f"--- {pname} n={pv['n_pairs']} floor={pv.get('strongest_floor')}")
        for a, v in pv.get("arms", {}).items():
            m = v["margin_over_strongest_floor"]
            print(f"    {a:<24} rho={v['rho']['point']:+.4f} "
                  f"[{v['rho']['ci95'][0]:+.4f},{v['rho']['ci95'][1]:+.4f}] "
                  f"margin={m['point']:+.4f} [{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] {v['band']}")
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
