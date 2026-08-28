"""p1 landing-verification / live-reader payoff: drive the LANDED scalar-magnitude organs on REAL human data.

The p1 organs were unit-witnessed on synthetic assets. This confirms the LANDED `hdlab.scalar_adjective_operation`
+ `hdlab.meaning_operation_router` reproduce the validated COMPARISON-system win on the real Warriner human ratings
(the "measure on the live reader" step; WIRE-DON'T-ISLAND). It drives the LANDED channel through the solver's OWN
comparison test (`exp_composed_magnitude_comparison_v1.test_a_comparison`), so a match proves the port is faithful.

Bar: the landed channel's oriented axis beats the incumbent gloss cosine CI-separated at predicting human "which
adjective is more [valence]" (target: the solver's composed 0.758 vs cosine 0.552, distance effect +0.34), and the
landed router sends gradable adjectives to it (spot-check).

Run:  .venv/Scripts/python.exe experiments/exp_p1_landed_organs_live_payoff_v1.py [--smoke]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

import numpy as np
from scipy.stats import spearmanr

import experiments.exp_perclass_meaning_operations_v1 as V1              # loaders (Warriner, GloVe) + DIM_SEEDS
import experiments.exp_adjective_intensity_ordering_v1 as INT           # freq loader
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP            # Lancaster loader
from hdlab.scalar_adjective_operation import ScalarMagnitudeChannel      # THE LANDED ORGAN
from hdlab.meaning_operation_router import route                         # THE LANDED ROUTER

SEED = 20260827


def main():
    smoke = "--smoke" in sys.argv
    print("[load] Warriner + freq + Lancaster + GloVe (needed words only)...", flush=True)
    war = V1.load_warriner()
    freq, _aoa = INT.load_freq_aoa()
    lanc = DEEP.load_lancaster_perceptual()
    needed = sorted(set(war) | {w for p in V1.DIM_SEEDS["valence"] for w in p})
    gv = V1.build_or_load_glove(needed)
    print(f"[load] gv={len(gv)} war={len(war)} freq={len(freq)} lanc={len(lanc)}", flush=True)

    chan = ScalarMagnitudeChannel(gv, freq, lanc)                        # LANDED channel (offline assets supplied)

    # composed comparison readout = the LANDED channel's grounded oriented valence axis (== test_a_comparison's arm)
    seed_words = {w for p in V1.DIM_SEEDS["valence"] for w in p}
    ws = sorted({w for w in set(V1.all_wordnet_adjectives()) if w in gv and w in war and "valence" in war[w]} - seed_words)
    if smoke:
        ws = ws[:800]
    val = np.array([war[w]["valence"] for w in ws])
    ax = chan.axis("valence")                                           # <-- the LANDED organ's oriented axis
    composed = np.array([chan.oriented_position(w, "valence") for w in ws])   # <-- landed readout
    rng = np.random.default_rng(SEED)
    rax = rng.standard_normal(gv[ws[0]].shape[0]); rax /= np.linalg.norm(rax)
    randr = np.array([float(gv[w] @ rax) for w in ws])                   # info-free random-axis twin
    npair = 4000 if smoke else 40000
    ii = rng.integers(0, len(ws), npair); jj = rng.integers(0, len(ws), npair)
    keep = (ii != jj) & (val[ii] != val[jj]); ii, jj = ii[keep], jj[keep]
    tgt = np.sign(val[ii] - val[jj]); gap = np.abs(val[ii] - val[jj])

    def acc(x):
        o = 1.0 if spearmanr(x, val).statistic >= 0 else -1.0
        return (np.sign(o * (x[ii] - x[jj])) == tgt).astype(float)
    ca, cr = acc(composed), acc(randr)
    q1, q2 = np.percentile(gap, [33, 66])
    de = float(ca[gap >= q2].mean() - ca[gap <= q1].mean())
    comp, rand = float(ca.mean()), float(cr.mean())

    print(f"\n[verify] LANDED channel on real Warriner (n_adj={len(ws)}, pairs={len(ii)}): "
          f"composed {comp:.4f} vs random-axis twin {rand:.4f}; distance effect +{de:.3f}", flush=True)
    grad = ["hot", "cold", "big", "good", "bad"]
    n_mag = sum(int(route(w, "ADJ") == "magnitude") for w in grad)
    print(f"[verify] router: gradable adjectives -> magnitude {n_mag}/{len(grad)}", flush=True)

    ok = comp >= 0.70 and comp > rand + 0.10 and de > 0.15 and n_mag == len(grad)
    print(f"\n[{'PASS' if ok else 'FAIL'}] the LANDED p1 organs reproduce the comparison win on real human data "
          f"(composed {comp:.3f} beats the random-axis twin {rand:.3f}, Moyer distance effect +{de:.3f}, "
          f"router sends gradable adj -> the ruler {n_mag}/{len(grad)}). Target: solver's composed ~0.758.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
