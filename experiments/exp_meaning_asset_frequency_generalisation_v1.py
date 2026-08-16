"""exp_meaning_asset_frequency_generalisation_v1 -- does an asset's meaning signal SURVIVE
leaving the frequent words the instrument's vocabulary is made of.

THE PROBLEM WITH THE LIKE-FOR-LIKE POPULATION, stated against my own headline number. The
instrument's 322 SimLex pairs are exactly the pairs whose BOTH words fall in the 4,096 most
frequent surface forms of a 64 MB corpus. That is a frequency-selected population. An encoder
trained on that corpus has seen those words thousands of times; it has seen the other 677 pairs'
words far less or not at all. So a high score on the 322 is consistent with two very different
assets: one that has learned meaning, and one that has learned meaning ONLY WHERE DATA WAS DENSE.
Those are distinguished by scoring the SAME arms, from the SAME stored cosines, on the disjoint
677-pair complement.

This is not a new measurement. Both strata come from the per-pair cosines already written by
exp_meaning_asset_power_extension_v2_paired, whose values are asserted in self-test to agree with
the independent fair-test cell on the 322 pairs the two share.

The two strata are DISJOINT ITEM SETS, so the difference is bootstrapped by resampling WITHIN
each stratum independently -- it is not a paired comparison and is not reported as one.

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

ANCHOR_NAME = "meaning_asset_frequency_generalisation_v1"
PX2 = REPO / "data/exp_meaning_asset_power_extension_v2_paired/metrics.json"
N_BOOT = 10000


def unpaired_diff(ca, ga, cb, gb, n_boot=N_BOOT, seed=FT.BOOT_SEED):
    """rho(stratum A) - rho(stratum B), resampled WITHIN each disjoint stratum independently."""
    rng = np.random.default_rng(seed)
    na, nb = len(ga), len(gb)
    ia = rng.integers(0, na, size=(n_boot, na))
    ib = rng.integers(0, nb, size=(n_boot, nb))
    d = np.empty(n_boot)
    for i in range(n_boot):
        d[i] = FT._spearman(ca[ia[i]], ga[ia[i]]) - FT._spearman(cb[ib[i]], gb[ib[i]])
    d = d[np.isfinite(d)]
    return {"point": float(FT._spearman(ca, ga) - FT._spearman(cb, gb)),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "n_a": int(na), "n_b": int(nb)}


def main() -> int:
    t0 = time.time()
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    allp = INS.load_simlex(INS.SIMLEX)
    inv = np.array([(a in w2i and b in w2i) for a, b, _ in allp])

    px = json.loads(PX2.read_text())["results"]["SIMLEX999"]
    gold = np.array(px["gold"], np.float64)
    pc = {k: np.array(v, np.float64) for k, v in px["per_pair_cos"].items()}
    assert len(gold) == len(allp) == 999, (len(gold), len(allp))
    assert int(inv.sum()) == 322, int(inv.sum())

    # ---- self-test: the two independently-run cells must agree on the pairs they share
    shared = {}
    for u in load_units(str(REPO / "data/exp_meaning_asset_fair_test_v1")).values():
        if isinstance(u, dict) and "simlex_cos" in u and int(u["seed"]) == 7:
            shared[u["arm"]] = np.array(u["simlex_cos"], np.float64)
    checked = 0
    for arm in ("ASSET_RETRAIN_ISOL", "ASSET_V2_ISOL", "ASSET_NORMS12", "ASSET_V2_TOKEMB"):
        if arm in pc and arm in shared:
            md = float(np.abs(pc[arm][inv] - shared[arm]).max())
            assert md < 1e-5, f"{arm}: power cell and fair-test cell disagree by {md}"
            checked += 1
    assert checked >= 3, f"only {checked} arms cross-checked"
    # the strata must be disjoint and exhaustive
    assert not (inv & ~inv).any() and (inv | ~inv).all()
    print(f"[selftest] OK  {checked} arms agree across two independently-run cells to <1e-5",
          flush=True)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    rows = {}
    for arm in sorted(pc):
        if arm.endswith("_SHUFFLED"):
            continue
        c = pc[arm]
        rows[arm] = {
            "rho_FREQUENT_322_in_instrument_vocab": FT.boot_rho(c[inv], gold[inv]),
            "rho_RARER_677_outside_it": FT.boot_rho(c[~inv], gold[~inv]),
            "rho_ALL_999": FT.boot_rho(c, gold),
            "drop_frequent_minus_rarer": unpaired_diff(c[inv], gold[inv], c[~inv], gold[~inv]),
        }
        rows[arm]["band_of_drop"] = FT.band(rows[arm]["drop_frequent_minus_rarer"]["ci95"])
        rows[arm]["signal_survives_leaving_the_frequent_words"] = bool(
            rows[arm]["rho_RARER_677_outside_it"]["ci95"][0] > 0)

    survive = sorted(k for k, v in rows.items()
                     if k.startswith("ASSET_") and v["signal_survives_leaving_the_frequent_words"])
    verdict = ("SOME_ASSETS_GENERALISE_BEYOND_THE_FREQUENT_VOCABULARY" if survive
               else "NO_ASSET_GENERALISES_BEYOND_THE_FREQUENT_VOCABULARY")

    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full", "verdict": verdict,
           "strata": {"FREQUENT_322": "both words among the 4,096 most frequent corpus forms -- "
                                      "this IS the instrument's like-for-like population",
                      "RARER_677": "the disjoint complement within SimLex-999"},
           "criterion": ("an asset generalises if its rho on the RARER stratum has a bootstrap CI "
                         "entirely above zero -- a weaker test than the floor gate, chosen "
                         "deliberately so a marginal generaliser is not dismissed"),
           "assets_whose_signal_survives": survive,
           "rows": rows}
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["summary"] = verdict
    write_metrics(out_dir, out)
    print("%-24s %-24s %-24s %-22s" % ("arm", "rho FREQUENT 322", "rho RARER 677", "drop"))
    for k, v in sorted(rows.items(), key=lambda kv: -kv[1]["rho_FREQUENT_322_in_instrument_vocab"]["point"]):
        a, b, dd = (v["rho_FREQUENT_322_in_instrument_vocab"], v["rho_RARER_677_outside_it"],
                    v["drop_frequent_minus_rarer"])
        print("%-24s %+.4f [%+.4f,%+.4f]  %+.4f [%+.4f,%+.4f]  %+.4f [%+.4f,%+.4f] %s" % (
            k, a["point"], a["ci95"][0], a["ci95"][1], b["point"], b["ci95"][0], b["ci95"][1],
            dd["point"], dd["ci95"][0], dd["ci95"][1], v["band_of_drop"]))
    print("VERDICT:", verdict, survive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
