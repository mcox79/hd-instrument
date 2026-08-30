"""Witness for the LANDED hdlab.distilled_substitutability organ (the meaning-channel Route A landing).

Landed 2026-08-30 from the integrated `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`
(owner-DONE, EXCELLENT). Confirms the MECHANISM on the actual hdlab organ, SCAFFOLD-FREE: it scores the
licensed substitutability instrument (its 484 covered pairs are saved IN the committed asset) through
hdlab.distilled_substitutability and recomputes the AUC from scratch -- NO load_everything / gitignored-cache
dependency (that dependency is exactly the bit-rot that blocked this fix for a week).

Asserts:
  1. COVERAGE: the consolidated distributional space has the expected vocabulary (~5491 words, 100 dims).
  2. THE CHANNEL SEPARATES SUBSTITUTABLES FROM ASSOCIATES: AUC over the instrument (substitutable positives
     vs mere-associate negatives), scored via the organ, clears the validated headline (>= 0.80, the CI
     lower bound of the reverified 0.8388) -- where grounded_similarity's 0.45 cap cannot separate them at all.
  3. INFO-FREE TWIN LOSES: the SAME phi space with a RANDOM direction (the distilled direction destroyed)
     collapses to chance; the real channel beats the twin's MAX over seeds, CI-separated in spirit.
  4. ORDERING: substitutable pairs score HIGHER on average than associate pairs (the sign is correct).

Run: .venv/Scripts/python.exe verification/test_distilled_substitutability_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402

import hdlab.distilled_substitutability as DS  # noqa: E402

ASSET = os.path.join(REPO_ROOT, "data", "grounded_distilled_substitutability_v1", "asset.npz")


def _auc(pos, neg) -> float:
    """AUC = P(score(pos) > score(neg)) via the rank-sum (ties count 0.5)."""
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(len(order), float); ranks[order] = np.arange(1, len(order) + 1)
    # average ranks for ties
    allv = np.concatenate([pos, neg])
    for v in np.unique(allv):
        m = allv == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def main() -> int:
    checks = []
    z = np.load(ASSET, allow_pickle=True)
    pos_pairs = z["pos_pairs"]; neg_pairs = z["neg_pairs"]
    phi = z["phi"]; sign = float(z["sign"])
    words = [str(x) for x in z["words"]]
    row = {w: i for i, w in enumerate(words)}

    # (1) coverage
    cov = DS.coverage_stats()
    checks.append((cov["n_words"] == len(words) and cov["n_dims"] == phi.shape[1] and cov["n_words"] > 4000,
                   f"[1] COVERAGE: {cov['n_words']} words x {cov['n_dims']} dims consolidated"))

    # (2) the channel separates substitutables from associates -- scored THROUGH the organ
    pos = [DS.distilled_substitutability(a, b) for a, b in pos_pairs]
    neg = [DS.distilled_substitutability(a, b) for a, b in neg_pairs]
    pos = [p for p in pos if p is not None]; neg = [n for n in neg if n is not None]
    auc = _auc(pos, neg)
    checks.append((auc >= 0.80,
                   f"[2] SUBSTITUTABILITY AUC through the organ = {auc:.4f} (>= 0.80, the reverified "
                   f"0.8388 CI lower; grounded_similarity's 0.45 cap separates these 0)"))

    # (3) info-free twin: SAME phi, RANDOM direction -> chance; real beats the twin's MAX over seeds
    def twin_auc(seed):
        rng = np.random.default_rng(seed)
        w_t = rng.standard_normal(phi.shape[1]).astype(np.float32)
        def sc(a, b):
            ia = row.get(str(a)) if row.get(str(a)) is not None else row.get(str(a).lower())
            ib = row.get(str(b)) if row.get(str(b)) is not None else row.get(str(b).lower())
            if ia is None or ib is None:
                return None
            return sign * float((phi[ia] * phi[ib]) @ w_t)
        p = [sc(a, b) for a, b in pos_pairs]; n = [sc(a, b) for a, b in neg_pairs]
        return _auc([x for x in p if x is not None], [x for x in n if x is not None])
    twins = [twin_auc(s) for s in range(8)]
    twin_max = max(abs(t - 0.5) for t in twins) + 0.5    # worst-case twin separation from chance
    checks.append((auc > twin_max and max(twins) < 0.65,
                   f"[3] INFO-FREE TWIN LOSES: real {auc:.4f} > twin MAX {max(twins):.4f} "
                   f"(random directions, 8 seeds, mean {np.mean(twins):.4f} ~= chance)"))

    # (4) ordering: substitutables score higher on average than associates
    checks.append((np.mean(pos) > np.mean(neg),
                   f"[4] ORDERING: substitutable mean {np.mean(pos):+.4f} > associate mean {np.mean(neg):+.4f}"))

    print("=== witness: hdlab.distilled_substitutability (the taught distributional meaning channel) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
