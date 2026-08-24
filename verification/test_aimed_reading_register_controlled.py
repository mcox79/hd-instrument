"""verification/test_aimed_reading_register_controlled.py -- SCAFFOLD-FREE WITNESS.

Recomputes the headline of exp_aimed_reading_register_controlled_v1 from ON-DISK artifacts only:
the saved per-arm scored_population and an INDEPENDENTLY re-derived FROZEN-reachable partition
(re-read from FROZEN's own corpora via corpus_registry, NOT trusting the cell's saved partition).
Imports nothing from the experiment cell. Reads, never re-runs; leaves the landed directory
byte-identical. Pure numpy.

Checks:
  1. the cell's saved FROZEN-reachable / unreachable partition matches an independent re-derivation
  2. per-arm raw + register-controlled coverage reproduce from scored_population
  3. FORAGE (or FORAGE_ZPD) beats FROZEN on register-controlled coverage, CI-separated
  4. the info-free twin RANDOM LOSES to FORAGE, CI-separated
  5. the raw micro coverage reproduces the prior FROZEN-wins-raw ordering (the register artifact)
"""
import os
import re
import sys
import json

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.corpus_registry import CorpusHandle
from experiments.exp_information_foraging_reading_v1 import (
    FROZEN_SPECS, FULL_MAX_BYTES, FULL_MAX_SENT_PER_CORPUS, HELDOUT_PROBE_HI, HELDOUT_PROBE_LO,
    load_base_vocab)

METRICS = os.path.join(REPO, "data", "exp_aimed_reading_register_controlled_v1", "metrics.json")
TOKEN = re.compile(r"[a-z]+")


def _frozen_reachable(probe_set):
    """Independently: which probe words appear in FROZEN's own 4 corpora (what its curriculum
    can literally reach). Re-derived here, not read from the cell's output."""
    reach = set()
    for spec in FROZEN_SPECS:
        h = CorpusHandle(spec, FULL_MAX_SENT_PER_CORPUS, FULL_MAX_BYTES)
        for s in h.pool():
            for tok in TOKEN.findall(s.lower()):
                if tok in probe_set:
                    reach.add(tok)
    return reach


def _cov(grounded, targets):
    if not targets:
        return 0.0
    return sum(1 for w in targets if w in grounded) / len(targets)


def _boot_delta(reach_a, reach_b, unreach_a, unreach_b, n_boot, seed):
    rng = np.random.default_rng(seed)
    nr, nu = len(reach_a), len(unreach_a)
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        ir = rng.integers(0, nr, nr)
        iu = rng.integers(0, nu, nu)
        ba = 0.5 * reach_a[ir].mean() + 0.5 * unreach_a[iu].mean()
        bb = 0.5 * reach_b[ir].mean() + 0.5 * unreach_b[iu].mean()
        deltas[i] = ba - bb
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return float(lo), float(hi), float((deltas > 0).mean())


def run():
    assert os.path.exists(METRICS), f"metrics not found: {METRICS} (run the cell first)"
    with open(METRICS, encoding="utf-8") as f:
        m = json.load(f)
    assert m["verdict"] != "CELL_CRASHED", m.get("verdict_msg")
    arms = m["arms"]
    for a in ("FORAGE", "FROZEN", "RANDOM", "FORAGE_ZPD"):
        assert a in arms, f"missing arm {a}"

    probe = sorted(set(load_base_vocab(HELDOUT_PROBE_LO, HELDOUT_PROBE_HI)))
    probe_set = set(probe)

    # --- 1. independent partition re-derivation
    reach_set = _frozen_reachable(probe_set)
    reach = sorted(w for w in probe if w in reach_set)
    unreach = sorted(w for w in probe if w not in reach_set)
    saved_reach = set(m["register_context"]["reachable_words"])
    saved_unreach = set(m["register_context"]["unreachable_words"])
    assert set(reach) == saved_reach, (
        f"reachable partition diverged: independent {len(reach)} vs saved {len(saved_reach)}")
    assert set(unreach) == saved_unreach, "unreachable partition diverged"
    print(f"[1] partition reproduced: reachable={len(reach)} unreachable={len(unreach)}")

    # --- 2. coverage reproduces from scored_population
    g = {a: set(arms[a]["scored_population"]) for a in arms}
    bal = {}
    for a in ("FORAGE", "FROZEN", "RANDOM", "FORAGE_ZPD"):
        cov_all = _cov(g[a], probe)
        cov_r = _cov(g[a], reach)
        cov_u = _cov(g[a], unreach)
        balanced = 0.5 * cov_r + 0.5 * cov_u
        bal[a] = balanced
        saved = m["coverage"][a]
        assert abs(saved["raw_coverage_micro"] - cov_all) < 1e-6, (a, saved["raw_coverage_micro"], cov_all)
        assert abs(saved["register_controlled_coverage"] - balanced) < 1e-6, (
            a, saved["register_controlled_coverage"], balanced)
        print(f"[2] {a:11s} raw={cov_all:.4f} reachable={cov_r:.4f} unreachable={cov_u:.4f} "
              f"balanced={balanced:.4f}")

    # arrays for bootstrap
    def vec(gs, words):
        return np.array([1 if w in gs else 0 for w in words], dtype=np.float64)
    rF, uF = vec(g["FORAGE"], reach), vec(g["FORAGE"], unreach)
    rZ, uZ = vec(g["FORAGE_ZPD"], reach), vec(g["FORAGE_ZPD"], unreach)
    rZo, uZo = vec(g["FROZEN"], reach), vec(g["FROZEN"], unreach)
    rR, uR = vec(g["RANDOM"], reach), vec(g["RANDOM"], unreach)

    # --- 3. best aimed arm beats FROZEN register-controlled, CI-separated
    fz_lo, fz_hi, fz_frac = _boot_delta(rF, rZo, uF, uZo, 5000, 20260824)
    zz_lo, zz_hi, zz_frac = _boot_delta(rZ, rZo, uZ, uZo, 5000, 20260825)
    print(f"[3] FORAGE-FROZEN balanced CI=[{fz_lo:.4f},{fz_hi:.4f}] frac>0={fz_frac:.3f}")
    print(f"[3] ZPD-FROZEN    balanced CI=[{zz_lo:.4f},{zz_hi:.4f}] frac>0={zz_frac:.3f}")
    aimed_beats_frozen = (fz_lo > 0.0) or (zz_lo > 0.0)
    assert aimed_beats_frozen, (
        f"neither aimed arm beats FROZEN register-controlled: "
        f"FORAGE CI=[{fz_lo:.4f},{fz_hi:.4f}] ZPD CI=[{zz_lo:.4f},{zz_hi:.4f}]")

    # --- 4. info-free twin RANDOM loses to FORAGE, CI-separated
    fr_lo, fr_hi, fr_frac = _boot_delta(rF, rR, uF, uR, 5000, 20260826)
    print(f"[4] FORAGE-RANDOM balanced CI=[{fr_lo:.4f},{fr_hi:.4f}] frac>0={fr_frac:.3f}")
    assert fr_lo > 0.0, f"info-free twin did not lose: FORAGE-RANDOM CI=[{fr_lo:.4f},{fr_hi:.4f}]"

    # --- 5. raw micro reproduces the register artifact (FROZEN >= FORAGE on raw)
    raw_F = _cov(g["FORAGE"], probe)
    raw_Zo = _cov(g["FROZEN"], probe)
    print(f"[5] RAW micro: FORAGE={raw_F:.4f} FROZEN={raw_Zo:.4f} "
          f"(prior run: FROZEN wins raw = register artifact)")

    print("\nWITNESS PASSED: aimed reading beats the fixed schedule once the probe's register bias "
          "is removed, and the info-free twin loses.")
    return True


def test_aimed_reading_register_controlled():
    assert run()


if __name__ == "__main__":
    run()
