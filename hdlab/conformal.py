"""Split-conformal prediction. Distribution-free coverage guarantees from a calibration set.

Standard split-conformal: given calibration nonconformity scores and a significance level
alpha, return the (1-alpha) quantile threshold q. Any test instance whose nonconformity
score s satisfies s <= q is included in the prediction set; coverage is >= 1-alpha
(marginal, exchangeable test/cal).

This is the substrate's calibration-set primitive complementing refuse_gate (which solves
threshold-from-paired-distributions); conformal solves threshold-for-coverage-from-single-set.

Prior art credited (learn-from + build-on, never claim as own):
  - Vovk, Gammerman, Shafer, "Algorithmic Learning in a Random World" (2005): split-conformal;
    Mondrian / label-conditional conformal (Vovk et al 2003) = per-partition quantiles.
  - Angelopoulos & Bates, "A Gentle Introduction to Conformal Prediction" (2021); Angelopoulos
    et al, "Conformal Risk Control" (2022).
  - Gibbs & Candes, "Adaptive Conformal Inference Under Distribution Shift" (NeurIPS 2021):
    online adaptive-alpha update.
  - Chow, "On Optimum Recognition Error and Reject Tradeoff" (IEEE IT 1970): reject option =
    the set-size -> abstain decision rule.
"""

from __future__ import annotations

import math

import torch


def calibrate_quantile(
    nonconformity_scores: torch.Tensor,
    alpha: float,
) -> float:
    """Split-conformal threshold from calibration nonconformity scores.

    Args:
        nonconformity_scores: 1-D tensor of calibration nonconformity scores
            (e.g. 1 - top-1 softmax prob; or distance-to-nearest; lower = more conformal).
        alpha: significance level in (0, 1). Coverage target is 1 - alpha.

    Returns:
        threshold q (float). At test time, include label y in the prediction set iff
        nonconformity_score(x, y) <= q. Marginal coverage >= 1 - alpha.
    """
    if nonconformity_scores.numel() == 0:
        raise ValueError("calibrate_quantile requires non-empty nonconformity_scores")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1); got {alpha}")

    n = int(nonconformity_scores.numel())
    rank = math.ceil((n + 1) * (1.0 - alpha))
    rank = min(max(rank, 1), n)
    sorted_scores, _ = torch.sort(nonconformity_scores)
    return float(sorted_scores[rank - 1])


def predict_set(
    test_scores: torch.Tensor,
    q: float,
) -> torch.Tensor:
    """Boolean mask: True where test_scores[i] <= q (i.e. included in prediction set)."""
    return test_scores <= q


def empirical_coverage(
    test_nonconformity_scores: torch.Tensor,
    q: float,
) -> float:
    """Fraction of test points with true-label nonconformity <= q.

    Marginal coverage should be approximately >= 1 - alpha when test and calibration
    sets are exchangeable.
    """
    if test_nonconformity_scores.numel() == 0:
        raise ValueError("empirical_coverage requires non-empty test_nonconformity_scores")
    return float((test_nonconformity_scores <= q).float().mean())


# ----------------------------------------------------------------------------------------------
# Closed-form additions (the pieces the self-monitoring scour flagged conformal.py was missing).
# All three are cheap, distribution-free, and credited above.
# ----------------------------------------------------------------------------------------------
def calibrate_quantile_mondrian(
    nonconformity_scores: torch.Tensor,
    groups,
    alpha: float,
    min_group: int = 2,
    pooled_fallback: bool = True,
) -> dict:
    """Mondrian (group-conditional) split-conformal (Vovk et al 2003).

    Calibrate a SEPARATE (1-alpha) quantile per group so coverage holds conditionally on the
    group (not merely marginally). Groups with fewer than `min_group` calibration members fall
    back to the pooled quantile (if pooled_fallback) else raise.

    Args:
        nonconformity_scores: 1-D tensor of calibration nonconformity scores.
        groups: sequence (len == n) of hashable group labels aligned with scores.
        alpha: significance level in (0, 1); per-group coverage target is 1 - alpha.
        min_group: minimum per-group calibration count to trust a group-specific quantile.
        pooled_fallback: small groups use the pooled quantile instead of raising.

    Returns:
        dict {group_label: threshold q_g}. Includes a "_pooled" key with the marginal quantile.
    """
    n = int(nonconformity_scores.numel())
    if n == 0:
        raise ValueError("calibrate_quantile_mondrian requires non-empty scores")
    if len(groups) != n:
        raise ValueError(f"groups length {len(groups)} != n_scores {n}")
    pooled_q = calibrate_quantile(nonconformity_scores, alpha)
    out = {"_pooled": pooled_q}
    uniq = []
    for g in groups:
        if g not in uniq:
            uniq.append(g)
    for g in uniq:
        idx = [i for i, gg in enumerate(groups) if gg == g]
        if len(idx) < min_group:
            if pooled_fallback:
                out[g] = pooled_q
                continue
            raise ValueError(f"group {g!r} has {len(idx)} < min_group={min_group} members")
        out[g] = calibrate_quantile(nonconformity_scores[torch.as_tensor(idx, dtype=torch.long)], alpha)
    return out


def adaptive_alpha_update(
    alpha_prev: float,
    miscovered: float,
    target_alpha: float,
    gamma: float = 0.05,
    eps: float = 1e-6,
) -> float:
    """Online adaptive-alpha update (Adaptive Conformal Inference; Gibbs & Candes 2021).

    err_t = miscovered (1 if the just-observed label was NOT in the set, else 0).
    alpha_{t+1} = alpha_t + gamma * (target_alpha - err_t), clipped to [eps, 1-eps].

    Sustained miscoverage (err > target) drives alpha DOWN -> larger sets -> more coverage,
    restoring long-run coverage under distribution shift without exchangeability.
    """
    if not (0.0 < target_alpha < 1.0):
        raise ValueError(f"target_alpha must be in (0,1); got {target_alpha}")
    a = alpha_prev + gamma * (target_alpha - float(miscovered))
    return float(min(max(a, eps), 1.0 - eps))


def predict_set_sizes(candidate_scores_per_item, q: float):
    """Per-item conformal set size = count of candidates whose nonconformity <= q.

    Args:
        candidate_scores_per_item: sequence of 1-D tensors (nonconformity per candidate label).
        q: conformal threshold.
    Returns:
        list[int] set sizes.
    """
    sizes = []
    for cs in candidate_scores_per_item:
        cs = torch.as_tensor(cs, dtype=torch.float64)
        sizes.append(int((cs <= q).sum().item()))
    return sizes


def abstain_by_set_size(set_size: int, keep_size: int = 1) -> bool:
    """Chow (1970) reject option mapped onto conformal set size.

    Return True (PREDICT / keep) iff the conformal set is an unambiguous singleton
    (set_size == keep_size); else False (ABSTAIN) because the set is empty (size 0 =
    no confident label) or ambiguous (size > 1 = rival labels not separated at level alpha).
    """
    return set_size == keep_size


def _self_test():
    """Scaffold-free witnesses for the closed-form additions (run: python -m hdlab.conformal)."""
    g = torch.Generator().manual_seed(0)
    # --- base quantile coverage sanity ---
    cal = torch.rand(2000, generator=g)
    test = torch.rand(5000, generator=g)
    q = calibrate_quantile(cal, alpha=0.1)
    cov = empirical_coverage(test, q)
    assert 0.86 < cov < 0.94, f"base coverage off: {cov}"

    # --- Mondrian: per-group coverage tighter than pooled when a group is shifted ---
    n = 3000
    grp = (["A"] * (n // 2)) + (["B"] * (n - n // 2))
    sc = torch.cat([torch.rand(n // 2, generator=g), 2.0 + torch.rand(n - n // 2, generator=g)])
    qs = calibrate_quantile_mondrian(sc, grp, alpha=0.1)
    assert qs["A"] < 1.0 < qs["B"], f"Mondrian did not separate shifted groups: {qs}"
    # group-B pooled quantile would UNDER-cover group B; group-specific must cover it
    tB = 2.0 + torch.rand(4000, generator=g)
    cov_pool_B = empirical_coverage(tB, qs["_pooled"])
    cov_mond_B = empirical_coverage(tB, qs["B"])
    assert cov_mond_B > 0.86 and cov_mond_B > cov_pool_B + 0.08, \
        f"Mondrian must restore group-B coverage to ~target: pool={cov_pool_B} mond={cov_mond_B}"

    # --- adaptive alpha: sustained miscoverage drives alpha down; over-coverage drives it up ---
    a = 0.1
    for _ in range(200):
        a = adaptive_alpha_update(a, miscovered=1.0, target_alpha=0.1, gamma=0.05)
    assert a < 0.05, f"adaptive alpha should shrink under sustained miscoverage: {a}"
    a2 = 0.1
    for _ in range(200):
        a2 = adaptive_alpha_update(a2, miscovered=0.0, target_alpha=0.1, gamma=0.05)
    assert a2 > 0.15, f"adaptive alpha should grow under sustained over-coverage: {a2}"

    # --- set-size / Chow reject: empty -> abstain, singleton -> predict, ambiguous -> abstain ---
    items = [torch.tensor([0.1, 0.9, 0.95]),   # 1 below q=0.5 -> singleton -> predict
             torch.tensor([0.8, 0.9]),          # 0 below q -> empty -> abstain
             torch.tensor([0.1, 0.2, 0.9])]     # 2 below q -> ambiguous -> abstain
    sizes = predict_set_sizes(items, q=0.5)
    assert sizes == [1, 0, 2], f"set sizes wrong: {sizes}"
    decisions = [abstain_by_set_size(s) for s in sizes]
    assert decisions == [True, False, False], f"Chow reject rule wrong: {decisions}"
    print("[conformal self-test] PASS: base_cov=%.3f mondrian(A=%.3f,B=%.3f,pool=%.3f) "
          "alpha_down=%.3f alpha_up=%.3f setsizes=%s" %
          (cov, qs["A"], qs["B"], qs["_pooled"], a, a2, sizes))


if __name__ == "__main__":
    _self_test()
