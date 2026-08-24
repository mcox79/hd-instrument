"""verification/test_aimed_reading_learning_progress.py -- SCAFFOLD-FREE WITNESS.

Recomputes the headline of exp_aimed_reading_learning_progress_v2 from ON-DISK artifacts only,
importing nothing from the experiment cell's decision logic. Covers all 5 arms (FORAGE, FROZEN,
RANDOM reused from v1; FORAGE_RANDTARGET, FORAGE_LP new). Reads, never re-runs.

DATA-DRIVEN: it does NOT assume the result is positive. For every check the cell reports, it
INDEPENDENTLY recomputes the register-controlled delta + a fresh bootstrap CI and asserts the sign
of that CI matches the cell's own `pass` flag. So it verifies the cell's claims whether they are
SOLVED or a clean negative. It also re-derives the FROZEN partition from FROZEN's own corpora
rather than trusting the cell's saved partition.
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

METRICS = os.path.join(REPO, "data", "exp_aimed_reading_learning_progress_v2", "metrics.json")
TOKEN = re.compile(r"[a-z]+")
ARMS = ["FORAGE", "FROZEN", "RANDOM", "FORAGE_RANDTARGET", "FORAGE_LP"]


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
    assert os.path.exists(METRICS), f"metrics not found: {METRICS} (run the cell first)"
    with open(METRICS, encoding="utf-8") as f:
        m = json.load(f)
    assert m["verdict"] not in ("CELL_CRASHED", "HARD_FAIL_ARM_CRASHED"), m.get("verdict_msg")
    arms = m["arms"]
    for a in ARMS:
        assert a in arms, f"missing arm {a}"

    probe = sorted(set(load_base_vocab(HELDOUT_PROBE_LO, HELDOUT_PROBE_HI)))
    probe_set = set(probe)
    reach_set = _frozen_reachable(probe_set)
    reach = sorted(w for w in probe if w in reach_set)
    unreach = sorted(w for w in probe if w not in reach_set)
    assert set(reach) == set(m["register_context"]["reachable_words"]), "partition diverged"
    print(f"[1] partition reproduced independently: reachable={len(reach)} unreachable={len(unreach)}")

    g = {a: set(arms[a]["scored_population"]) for a in ARMS}
    print(f"\n{'arm':17s} {'nground':>7s} {'raw':>7s} {'balanced':>9s}")
    for a in ARMS:
        cr, cu = _cov(g[a], reach), _cov(g[a], unreach)
        bal = 0.5 * cr + 0.5 * cu
        raw = _cov(g[a], probe)
        saved = m["coverage"][a]
        assert abs(saved["raw_coverage_micro"] - raw) < 1e-6, (a, saved["raw_coverage_micro"], raw)
        assert abs(saved["register_controlled_coverage"] - bal) < 1e-6, (a, bal)
        print(f"{a:17s} {len(g[a]):7d} {raw:7.4f} {bal:9.4f}")

    # LP firing correctness: the LP branch must actually be doing the work, not silently falling back
    lp_frac = arms["FORAGE_LP"]["lp_diag"]["lp_target_frac"]
    print(f"\n[2] LP target fired on {lp_frac:.2%} of FORAGE_LP's corpus choices "
          f"(n_lp_target={arms['FORAGE_LP']['lp_diag']['n_lp_target']}, "
          f"n_lp_fallback={arms['FORAGE_LP']['lp_diag']['n_lp_fallback']})")
    assert lp_frac > 0.5, f"LP branch fired <50% of the time ({lp_frac}); arm is mostly the fallback"

    # data-driven: recompute each check's CI and assert its sign matches the cell's own pass flag
    checks = m["checks"]
    pairs = {
        "C1_LP_beats_FROZEN_register_controlled": ("FORAGE_LP", "FROZEN", 1),
        "C2_LP_signal_informative_vs_random_target": ("FORAGE_LP", "FORAGE_RANDTARGET", 2),
        "C3_LP_beats_frequency_target_FORAGE": ("FORAGE_LP", "FORAGE", 3),
        "C4_info_free_corpus_twin_loses": ("FORAGE_LP", "RANDOM", 4),
    }
    print("\n[3] independent recompute of each check vs the cell's own pass flag:")
    for name, (a, b, seed) in pairs.items():
        lo, hi = _boot_delta(reach, unreach, g[a], g[b], 90000 + seed)
        indep_pass = lo > 0.0
        cell_pass = checks[name]["pass"]
        status = "OK" if indep_pass == cell_pass else "MISMATCH"
        print(f"    {name:44s} indep CI[{lo:.4f},{hi:.4f}] pass={indep_pass} "
              f"cell_pass={cell_pass}  [{status}]")
        assert indep_pass == cell_pass, f"{name}: independent pass {indep_pass} != cell {cell_pass}"

    print(f"\n[4] cell verdict: {m['verdict']}")
    print("WITNESS PASSED: coverage, partition, LP-firing, and every check's pass flag reproduce "
          "independently from the saved populations.")
    return True


def test_aimed_reading_learning_progress():
    assert run()


if __name__ == "__main__":
    run()
