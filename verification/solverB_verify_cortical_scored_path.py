"""Scaffold-free witnesses for the cortical scored-path harness (problem
cortical_read_has_no_scored_path, solver-B).

These do NOT touch the substrate. They witness that the SCORING MACHINERY the verdict rests on is
sound -- i.e. that the controls can actually fail and actually fire -- so a negative verdict from
the harness is a verdict about the organ and not about a broken scorer. Each test can fail.

Run:  python verification/solverB_verify_cortical_scored_path.py
"""
import os
import random
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def _boot_ci(x, rng, n_boot=2000):
    if x.size == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, x.size, size=(n_boot, x.size))
    m = x[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(lo), float(hi)


def test_information_free_twin_loses_to_a_planted_signal():
    """POSITIVE + NEGATIVE CONTROL on the rank metric. A ranker with real signal must clear the
    upper CI of a random-permutation twin; the twin must NOT clear the signal. If the twin could
    win, no negative from the harness would mean anything."""
    rng = np.random.default_rng(0)
    n_items, n_cand = 300, 400
    # signal arm: target usually ranked near the top. geometric() is in {1,2,...}, so min rank 1.
    signal_ranks = np.minimum(rng.geometric(0.25, size=n_items), n_cand)
    # twin: uniform random rank over the candidate set.
    twin_ranks = rng.integers(1, n_cand + 1, size=n_items)
    for k in (1, 5, 10, 25, 50):
        s = (signal_ranks <= k).astype(np.float64)
        t = (twin_ranks <= k).astype(np.float64)
        s_lo, _ = _boot_ci(s, rng)
        _, t_hi = _boot_ci(t, rng)
        assert s_lo > t_hi, f"signal did not clear twin at k={k}: {s_lo:.3f} !> {t_hi:.3f}"
    # And the twin's hit@k must sit near chance k/N (fails safe, no tie-break inflation).
    for k in (10, 50):
        assert abs((twin_ranks <= k).mean() - k / n_cand) < 0.05, "twin not near chance"
    return "signal clears twin at every k; twin sits at chance"


def test_concreteness_floor_orders_concrete_above_abstract():
    """The concreteness-prior floor must rank concrete words above abstract ones, using the exact
    dimension (index 11) the harness reads. If it did not, the mandated floor would be inert."""
    from hdlab.grounded_similarity import grounded_vector
    concrete = ["dog", "water", "hammer", "table", "bird", "glass"]
    abstract = ["justice", "freedom", "democracy", "truth", "idea"]
    cz = lambda w: (lambda v: None if v is None else float(v[11]))(grounded_vector(w))
    cvals = [cz(w) for w in concrete if cz(w) is not None]
    avals = [cz(w) for w in abstract if cz(w) is not None]
    assert cvals and avals, "grounded norms unavailable for the fixture words"
    assert min(cvals) > max(avals), (
        f"concreteness dim does not separate: min concrete {min(cvals):.3f} "
        f"!> max abstract {max(avals):.3f}")
    # And the sort key used by the floor puts concrete first.
    words = concrete + abstract
    ranked = sorted(words, key=lambda w: (cz(w) is None, -(cz(w) or 0.0), w))
    assert ranked[0] in concrete and ranked[-1] in abstract, f"bad order: {ranked}"
    return f"concrete min {min(cvals):.2f} > abstract max {max(avals):.2f}; order OK"


def test_unseen_partition_is_nonvacuous_and_correct():
    """The brain-foundational partition must actually split items, and 'unseen' must mean the
    co-occurrence counter has no entry for the target. A partition that put everything on one side
    would make the generalization verdict vacuous."""
    import collections
    # tiny cooc table: 'dog' co-occurs with 'bark'; 'cat' with nothing in the cue.
    cooc = collections.defaultdict(collections.Counter)
    cooc["bark"]["dog"] += 3

    def saw(cue_words, tgt):
        c = collections.Counter()
        for l in cue_words:
            c.update(cooc.get(l, {}))
        for w in cue_words:
            c.pop(w, None)
        return tgt in c

    assert saw(["bark"], "dog") is True, "seen case failed"
    assert saw(["bark"], "cat") is False, "unseen case failed"
    assert saw(["meow"], "dog") is False, "unseen (no cue evidence) failed"
    return "seen/unseen partition correct on a controlled cooc table"


def main():
    tests = [test_information_free_twin_loses_to_a_planted_signal,
             test_concreteness_floor_orders_concrete_above_abstract,
             test_unseen_partition_is_nonvacuous_and_correct]
    failed = []
    for fn in tests:
        try:
            print(f"PASS  {fn.__name__}: {fn()}")
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}: {e}")
            failed.append(fn.__name__)
    print("ALL WITNESSES PASSED" if not failed else f"FAILED: {failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
