"""exp_meaning_asset_floor_hardening_v1 -- make the FREQUENCY floor as strong as it can be.

The A_FREQUENCY arm in exp_meaning_asset_fair_test_v1 lifts log-frequency into d dims through a
RANDOM projection, so its SimLex rho carries projection noise (measured: 0.0916 / -0.0161 /
-0.0047 across the three seeds at d=512). A floor that moves with a nuisance seed is a weak floor,
and the standing rule wants the STRONGEST floor. This cell computes the SEED-FREE frequency
floors directly on the pair scores:

  FREQ_NEG_ABS_DIFF   sim(a,b) = -|log f_a - log f_b|      (frequency-band similarity)
  FREQ_MIN_OVER_MAX   sim(a,b) =  min(log f)/max(log f)    (a scale-free variant)
  FREQ_SUM            sim(a,b) =  log f_a + log f_b        (a pure popularity channel)

and reports the LARGEST of them, which is the number the fair test must be held against on the
semantic gold. Same vocabulary, same SimLex pairs, same Spearman, same bootstrap as the main cell.

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

ANCHOR_NAME = "meaning_asset_floor_hardening_v1"


def main() -> int:
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    lf = np.log(counts + 1.0)
    gold = np.array([s for _, _, s in pairs])
    la = np.array([lf[w2i[a]] for a, _, _ in pairs])
    lb = np.array([lf[w2i[b]] for _, b, _ in pairs])

    chans = {
        "FREQ_NEG_ABS_DIFF": -np.abs(la - lb),
        "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12),
        "FREQ_SUM": la + lb,
        "FREQ_MIN": np.minimum(la, lb),
    }
    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full",
           "n_pairs": len(pairs), "vocab": INS.V, "corpus_bytes": INS.CORPUS_BYTES,
           "channels": {}}
    for k, v in chans.items():
        out["channels"][k] = FT.boot_rho(v, gold)
    best = max(out["channels"], key=lambda k: out["channels"][k]["point"])
    out["strongest_seed_free_frequency_floor"] = {"channel": best,
                                                  **out["channels"][best]}
    out["note"] = ("These are STANDALONE zero-meaning channels computed directly on the pair "
                   "scores, with no random projection and no seed. The largest of them is the "
                   "number a meaning asset must beat on the semantic gold, alongside the "
                   "orthographic and scramble floors.")
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, out)
    print(json.dumps({"n_pairs": out["n_pairs"],
                      "channels": {k: [round(v["point"], 4), [round(x, 4) for x in v["ci95"]]]
                                   for k, v in out["channels"].items()},
                      "strongest": best}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
