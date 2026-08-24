"""verification/test_aimed_reading_register_controlled.py -- SCAFFOLD-FREE WITNESS (v1 core finding).

Witnesses the standalone register-controlled result from the three banked arms of
exp_aimed_reading_register_controlled_v1 (FORAGE, FROZEN, RANDOM), read directly from the on-disk
checkpoint (no metrics.json required; the cell's 4th arm was superseded before completion). Imports
nothing from the cell's decision logic; re-derives the FROZEN partition from FROZEN's own corpora.

Establishes, independently:
  1. the FROZEN-reachable / unreachable probe partition
  2. per-arm raw + register-controlled coverage from each arm's saved scored_population
  3. aimed reading (FORAGE, surprise-driven) does NOT beat the FIXED schedule even with the register
     bias removed -- FORAGE-FROZEN register-controlled CI lies BELOW zero (the refutation)
  4. the info-free CORPUS twin (RANDOM) LOSES to FORAGE, CI-separated (aiming beats random)
"""
import os
import re
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.corpus_registry import CorpusHandle
from experiments.exp_information_foraging_reading_v1 import (
    FROZEN_SPECS, FULL_MAX_BYTES, FULL_MAX_SENT_PER_CORPUS, HELDOUT_PROBE_HI, HELDOUT_PROBE_LO,
    load_base_vocab)
from tools import exp_checkpoint

CKPT_DIR = os.path.join(REPO, "data", "exp_aimed_reading_register_controlled_v1")
TOKEN = re.compile(r"[a-z]+")


def _frozen_reachable(probe_set):
    reach = set()
    for spec in FROZEN_SPECS:
        for s in CorpusHandle(spec, FULL_MAX_SENT_PER_CORPUS, FULL_MAX_BYTES).pool():
            for tok in TOKEN.findall(s.lower()):
                if tok in probe_set:
                    reach.add(tok)
    return reach


def _cov(g, T):
    return sum(1 for w in T if w in g) / len(T) if T else 0.0


def _boot_delta(reach, unreach, ga, gb, seed, n_boot=5000):
    ra = np.array([1 if w in ga else 0 for w in reach], float)
    rb = np.array([1 if w in gb else 0 for w in reach], float)
    ua = np.array([1 if w in ga else 0 for w in unreach], float)
    ub = np.array([1 if w in gb else 0 for w in unreach], float)
    rng = np.random.default_rng(seed)
    nr, nu = len(reach), len(unreach)
    d = np.empty(n_boot)
    for i in range(n_boot):
        ir, iu = rng.integers(0, nr, nr), rng.integers(0, nu, nu)
        d[i] = (0.5 * ra[ir].mean() + 0.5 * ua[iu].mean()) - (0.5 * rb[ir].mean() + 0.5 * ub[iu].mean())
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(lo), float(hi)


def run():
    u = exp_checkpoint.load_units(CKPT_DIR)
    arms = {k.split("|")[-1]: v for k, v in u.items()}
    for a in ("FORAGE", "FROZEN", "RANDOM"):
        assert a in arms and "scored_population" in arms[a], f"arm {a} not banked in {CKPT_DIR}"

    probe = sorted(set(load_base_vocab(HELDOUT_PROBE_LO, HELDOUT_PROBE_HI)))
    reach_set = _frozen_reachable(set(probe))
    reach = sorted(w for w in probe if w in reach_set)
    unreach = sorted(w for w in probe if w not in reach_set)
    print(f"[1] partition: reachable={len(reach)} unreachable={len(unreach)}")

    g = {a: set(arms[a]["scored_population"]) for a in ("FORAGE", "FROZEN", "RANDOM")}
    for a in ("FORAGE", "FROZEN", "RANDOM"):
        cr, cu = _cov(g[a], reach), _cov(g[a], unreach)
        print(f"[2] {a:8s} n={len(g[a]):4d} raw={_cov(g[a],probe):.4f} reach={cr:.4f} "
              f"unreach={cu:.4f} balanced={0.5*cr+0.5*cu:.4f}")

    fz_lo, fz_hi = _boot_delta(reach, unreach, g["FORAGE"], g["FROZEN"], 4242)
    fr_lo, fr_hi = _boot_delta(reach, unreach, g["FORAGE"], g["RANDOM"], 4243)
    print(f"\n[3] FORAGE-FROZEN register-controlled CI=[{fz_lo:.4f},{fz_hi:.4f}] "
          f"-> {'FROZEN wins (refutation)' if fz_hi < 0 else 'not below zero'}")
    print(f"[4] FORAGE-RANDOM register-controlled CI=[{fr_lo:.4f},{fr_hi:.4f}] "
          f"-> {'twin loses' if fr_lo > 0 else 'twin does not lose'}")

    assert fz_hi < 0.0, (
        f"expected FROZEN to beat FORAGE even register-controlled (CI hi<0); got [{fz_lo},{fz_hi}]")
    assert fr_lo > 0.0, f"expected info-free twin RANDOM to lose; got [{fr_lo},{fr_hi}]"
    print("\nWITNESS PASSED: surprise-driven aimed reading does NOT beat the fixed schedule even "
          "with the register bias removed; the info-free corpus twin loses.")
    return True


def test_aimed_reading_register_controlled():
    assert run()


if __name__ == "__main__":
    run()
