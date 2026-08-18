"""exp_hub_spoke_correlation_cliff_v1 -- WHERE DOES WITHIN-ITEM FACET CORRELATION ACTUALLY BREAK
ADDRESSING, AND DOES IT BREAK IT AT ALL?

DIAGNOSTIC CELL, NOT A GATED ONE. No pre-registered PASS/FAIL band. Durable (not scratch/)
because a report cites its numbers.

WHY
---
exp_hub_spoke_word_representation_v1's X_CORRSTRESS arm sweeps a nominal flip parameter of
[0.25, 0.50, 0.75, 0.90], whose top MEASURED within-word spoke cosine is about 0.81, and facet
recovery there is still ~0.99. That top of the grid is not a cliff, it is the edge of the grid,
so the grid cannot distinguish "correlation does not hurt" from "we never pushed hard enough".
One of the four standing explanations for the STRUCTURE_HURTS reconciliation problem is exactly
"real facets are CORRELATED, not independent as the synthetic arms were". This cell pushes the
sweep to where the measure must collapse, so the explanation can be tested rather than assumed.

The v1 cell is IMPORTED and NOT MODIFIED: `corr_spokes`, `facet_recovery`, `boot_mean` and
`HubSpokeWord` are the v1/hdlab functions, called as-is. Only the sweep range is new, and it
EXTENDS rather than replaces: the four v1 grid points are re-run here and must reproduce.

Reported: MEASURED within-item cosine (never the nominal flip parameter -- two independently
flipped copies of a shared base have E[cos] = (1-2p)^2, not (1-2p)), facet recovery with CI, and
the same measure with a SHUFFLED key so a collapse from correlation is distinguishable from a
read-out that was never addressed. Also swept: the number of facets F, because the pool a facet
is scored against is the item's own other facets and correlation between MORE of them is harder.

ASCII-only. CPU. No external LLM. data/foundation/** never opened.
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
import exp_hub_spoke_word_representation_v1 as HS      # IMPORTED, NEVER EDITED
from hdlab.hub_spoke_word import HubSpokeWord
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hub_spoke_correlation_cliff_v1"
CODE_VERSION = "v1.0"

# the four v1 grid points (reproduction check) PLUS the extension to where it must break
RHOS = [0.25, 0.50, 0.75, 0.90, 0.95, 0.98, 0.99, 0.995, 1.0]
F_SWEEP = [2, 4, 8]
SEEDS = [7, 17, 23]
N_ITEMS = 1024
D = 1024


def one(rho: float, f: int, seed: int) -> dict:
    codes = HS.corr_spokes(rho, N_ITEMS, D, seed, f=f)
    names = tuple(sorted(codes.keys()))
    codec = HubSpokeWord(D, names, seed, quantize=False)
    vecs = codec.bundle(codes)
    pw = HS.facet_recovery(vecs, codec, names, codes, "X_CORRSTRESS", seed, return_per_word=True)
    perm = HS.derangement(f, seed)
    pw_s = HS.facet_recovery(vecs, codec, names, codes, "X_CORRSTRESS", seed, key_perm=perm,
                             return_per_word=True)
    A = INS._l2n(codes[names[0]])
    B = INS._l2n(codes[names[1]])
    meas = float(np.mean(np.sum(A[:256] * B[:256], axis=1)))
    return {"nominal_flip_parameter_1_minus_2p": rho, "F": f, "seed": seed,
            "measured_within_item_cos": meas, "chance": 1.0 / f,
            "facet_recovery": HS.boot_mean(pw, n_boot=2000),
            "facet_recovery_shuffled_key": HS.boot_mean(pw_s, n_boot=2000)}


def main() -> int:
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in F_SWEEP:
        for rho in RHOS:
            for seed in SEEDS:
                rows.append(one(rho, f, seed))
        print(f"  F={f} done ({time.time()-t0:.1f}s)", flush=True)

    grid = {}
    for f in F_SWEEP:
        for rho in RHOS:
            sub = [r for r in rows if r["F"] == f and
                   r["nominal_flip_parameter_1_minus_2p"] == rho]
            grid[f"F{f}_rho{rho:g}"] = {
                "measured_within_item_cos": float(np.mean([r["measured_within_item_cos"]
                                                           for r in sub])),
                "facet_recovery": float(np.mean([r["facet_recovery"]["point"] for r in sub])),
                "facet_recovery_sd": float(np.std([r["facet_recovery"]["point"] for r in sub])),
                "shuffled_key": float(np.mean([r["facet_recovery_shuffled_key"]["point"]
                                               for r in sub])),
                "chance": 1.0 / f}
    # where does it break: first measured cosine at which recovery drops below 0.95
    cliffs = {}
    for f in F_SWEEP:
        cliff = None
        for rho in RHOS:
            g = grid[f"F{f}_rho{rho:g}"]
            if g["facet_recovery"] < 0.95:
                cliff = {"nominal": rho, "measured_cos": g["measured_within_item_cos"],
                         "facet_recovery": g["facet_recovery"]}
                break
        cliffs[f"F{f}"] = cliff or "NO CLIFF ANYWHERE ON THIS GRID (recovery >= 0.95 throughout)"

    vmsg = ("Within-item facet correlation swept past the v1 grid to identity. Cliff (first grid "
            "point with facet recovery < 0.95) per facet count: " + json.dumps(cliffs) +
            ". DIAGNOSTIC: synthetic codes, within-item read-out with the key in hand; says "
            "nothing about any cross-item or downstream metric.")
    metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "run_mode": "full",
               "cell_class": "DIAGNOSTIC -- no pre-registered PASS/FAIL band",
               "config": {"RHOS": RHOS, "F_SWEEP": F_SWEEP, "SEEDS": SEEDS,
                          "N_ITEMS": N_ITEMS, "D": D},
               "grid": grid, "cliffs": cliffs, "per_config": rows,
               "verdict": "MEASURED", "verdict_msg": vmsg, "summary": vmsg,
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics)
    print(json.dumps({"grid": grid, "cliffs": cliffs}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
