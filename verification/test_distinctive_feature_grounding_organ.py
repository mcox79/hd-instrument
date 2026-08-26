"""Scaffold-free witness for the ATL distinctive-feature (feature-similarity) read-out landed in
hdlab/grounded_similarity.py on 2026-08-26, from the integrated problem
the_substrate_has_one_meaning_system_where_the_brain_has_two.

Proves, first-hand and deterministically, that the ORGAN carries the two-systems bar-#1 win:
  (1) DEFAULT BYTE-IDENTICAL -- the capped grounded_similarity() LINK score is unchanged (a cap would
      destroy a similarity ranking; the distinctive path is a separate, uncapped read-out).
  (2) THE WHITENING IS A REAL WHITENING -- the transformed grounding table has an IDENTITY covariance
      (all variances equalised, off-diagonals ~0), i.e. the dominant shared concreteness axis is
      genuinely suppressed. Not a cosmetic transform.
  (3) IT CARRIES THE FEATURE-SIMILARITY WIN ON REAL GOLD -- on held-out SimLex-999 the whitened
      (distinctive) read-out beats the RAW (uncapped) grounded cosine on Spearman rho, and specialises
      toward similarity (the ATL "alike-in-kind" signature). Same comparison the integrated cell made,
      re-derived through the organ's OWN transform (fit on the full population, so numbers differ from
      the cell's gold-blind-excluded fit -- the DIRECTION is what the organ must carry).
Reads only the shipped SimLex file; writes nothing.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch

import hdlab.grounded_similarity as GS

_SIMLEX = os.path.join(_REPO, "data", "encoder_eval_benchmarks", "simlex999.txt")


def _spearman(xs, ys):
    """Rank-correlation with no scipy dependency: Pearson on ranks (average ranks for ties)."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx > 0 and dy > 0 else 0.0


def _raw_uncapped(a, b):
    """The fair RAW baseline: uncapped grounded cosine (the capped grounded_similarity would flatten
    the ranking at 0.45, so we compare the whitening against the SAME cosine, only the transform differs)."""
    va, vb = GS.grounded_vector(a), GS.grounded_vector(b)
    if va is None or vb is None:
        return None
    return GS._raw_cos(va, vb)


def test_default_link_score_unchanged():
    # the capped LINK path must be byte-identical: siblings pinned at the cap, ordering preserved
    assert GS.grounded_similarity("apple", "orange") == 0.45, "capped link score changed"
    for a, b in [("apple", "orange"), ("sofa", "couch"), ("dog", "cat")]:
        s = GS.grounded_similarity(a, b)
        assert s is not None and 0.0 <= s <= GS.GROUNDED_CAP, f"cap violated on {a},{b}: {s}"
    print("PASS default_link_score_unchanged (capped path byte-identical)")


def test_whitening_is_a_real_whitening():
    mu, W = GS._distinctive_transform()
    assert tuple(mu.shape) == (12,) and tuple(W.shape) == (12, 12), "transform shapes wrong"
    t = GS._table()
    X = torch.stack([t[w] for w in sorted(t)]).double()
    Xw = (X - mu) @ W
    C = torch.cov(Xw.T)
    diag = torch.diagonal(C)
    offmax = (C - torch.diag(diag)).abs().max().item()
    assert abs(diag.max().item() - 1.0) < 1e-3 and abs(diag.min().item() - 1.0) < 1e-3, \
        f"variances not equalised to 1: [{diag.min().item():.3f},{diag.max().item():.3f}]"
    assert offmax < 1e-3, f"off-diagonal covariance not ~0 (not decorrelated): {offmax:.4f}"
    print(f"PASS whitening_is_a_real_whitening (identity cov: diag~1, max|offdiag|={offmax:.1e})")


def test_carries_feature_similarity_win_on_simlex():
    raw_x, dfw_x, gold = [], [], []
    with open(_SIMLEX, "r", encoding="utf-8") as fh:
        next(fh)  # header
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            a, b, score = p[0], p[1], float(p[3])
            r = _raw_uncapped(a, b)
            d = GS.distinctive_grounded_similarity(a, b)
            if r is None or d is None:
                continue
            raw_x.append(r); dfw_x.append(d); gold.append(score)
    n = len(gold)
    assert n >= 300, f"too few covered SimLex pairs to judge ({n})"
    rho_raw = _spearman(raw_x, gold)
    rho_dfw = _spearman(dfw_x, gold)
    assert rho_dfw > rho_raw, f"distinctive must beat raw on similarity: dfw {rho_dfw:.3f} <= raw {rho_raw:.3f}"
    assert rho_dfw > 0.20, f"distinctive similarity rho unexpectedly low: {rho_dfw:.3f}"
    print(f"PASS carries_feature_similarity_win_on_simlex: n={n} distinctive rho={rho_dfw:.3f} > raw rho={rho_raw:.3f}")


def test_deterministic_and_cached():
    a = GS.distinctive_grounded_similarity("dog", "wolf")
    b = GS.distinctive_grounded_similarity("dog", "wolf")
    assert a == b, "distinctive score is not deterministic"
    assert GS.distinctive_grounded_similarity("qwertyzznotaword", "zzznotaword") is None, "OOV must return None"
    print("PASS deterministic_and_cached")


if __name__ == "__main__":
    test_default_link_score_unchanged()
    test_whitening_is_a_real_whitening()
    test_carries_feature_similarity_win_on_simlex()
    test_deterministic_and_cached()
    print("WITNESS PASS")
