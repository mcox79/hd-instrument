"""C2+CHTV cleanup-codebook tau calibration formula v1 (DECISION 15).

Per Research DECISIONS 15-16 note 2026-06-14: principled per-partition
tau formula reusing substrate's 9d spectral observability pillar.

Formula (Marchenko-Pastur + BBP spike + free cumulant):
  q_i           = N_i / d                       (shape ratio)
  G_i           = (1/N_i) sum_a a a^T            (local Gram matrix; provided)
  sigma_i^2     = trace(G_i) / d                 (spectral norm)
  lambda_plus_i = (1 + sqrt(q_i))^2 * sigma_i^2  (MP bulk edge / noise floor)
  theta_max_i   = largest eigenvalue of G_i      (BBP spike / cluster signature)
  kappa_4_i     = 4th free cumulant of G_i       (heavy-tail correction)
  alpha_i       = clip(1 + 0.5 * kappa_4_i, 1, 2)
  tau_i         = lambda_plus_i + alpha_i * sqrt(theta_max_i - lambda_plus_i)
  beta_i        = log(N_i) / (theta_max_i - lambda_plus_i)

Lane ownership per Research:
  Testbed PRIMARY: ship this formula module (this script)
  Exp-Dev: measure cleanup precision on 200 held-out queries
  Skunkworks: integrate cleanup_margin signal into PROACTIVE_GAP_LOOP v1

Reservations honored:
  R1 USER 11th rule: substrate-on-its-own (no LLM, no bge encoder use here)
  R2 USER 18th rule: tau is PRE-SCREEN; CHTV-1 still gates downstream
  R3 USER 22nd rule: external floor present (MP 1967 + Plate 1994 +
     Ramsauer 2020 + Lucibello-Mezard 2024)

Falsifier per Research:
  HARD-PASS: cleanup precision >=0.05 over 3 baselines on >=200/250 partitions
  HARD-FAIL: precision advantage <0.02 OR theta_max-lambda_plus degenerate
             on >10pct partitions

This module is pure numpy. Takes pre-computed spectral stats; does NOT
load bge / compute Gram matrices itself (laptop forbids torch model load).
Runner desktop computes Gram matrices + calls compute_tau_per_partition().

NO LLM. NO bge. NO torch. Pure math + numpy.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class PartitionSpectralStats:
    """Inputs the formula needs for one L1 partition.

    All fields are scalars or 1d arrays of small length (eigenvalues).
    Computed upstream from the partition's Gram matrix G_i = (1/N_i) sum a a^T.
    """
    partition_id: str
    N_i: int                                   # atom count in partition
    d: int                                     # embedding dim (typically 1024)
    trace_G_i: float                           # = sum of eigenvalues
    eigenvalues_G_i: list[float]               # spectrum (descending; len up to d)
    # Optional: precomputed 4th free cumulant. If not provided, computed
    # from eigenvalues via free-probability free-cumulant formula.
    kappa_4_precomputed: Optional[float] = None


@dataclass
class PartitionTauResult:
    partition_id: str
    N_i: int
    d: int
    q_i: float
    sigma_sq_i: float
    lambda_plus_i: float
    theta_max_i: float
    kappa_4_i: float
    alpha_i: float
    tau_i: float
    beta_i: float
    degenerate: bool  # True if theta_max - lambda_plus is too small
    notes: dict = field(default_factory=dict)


def compute_kappa_4_from_eigenvalues(eigs) -> float:
    """4th free cumulant kappa_4 from spectrum.

    Free cumulant relation: m_n = sum over non-crossing partitions of products
    of free cumulants. Inverting at order 4:
      kappa_4 = m_4 - 4 m_3 m_1 - 2 m_2^2 + 10 m_2 m_1^2 - 5 m_1^4

    Where m_n = E[lambda^n] = (1/N) sum_i lambda_i^n.

    This is the standard free-cumulant inversion (moment-cumulant relation
    for non-crossing partitions of size 4).
    """
    if not HAS_NUMPY:
        N = len(eigs)
        if N == 0:
            return 0.0
        m1 = sum(e for e in eigs) / N
        m2 = sum(e*e for e in eigs) / N
        m3 = sum(e*e*e for e in eigs) / N
        m4 = sum(e*e*e*e for e in eigs) / N
    else:
        a = np.asarray(eigs, dtype=float)
        if a.size == 0:
            return 0.0
        m1 = float(a.mean())
        m2 = float((a**2).mean())
        m3 = float((a**3).mean())
        m4 = float((a**4).mean())

    return m4 - 4.0 * m3 * m1 - 2.0 * m2 * m2 + 10.0 * m2 * m1 * m1 - 5.0 * (m1 ** 4)


def compute_tau_for_partition(stats: PartitionSpectralStats,
                              degenerate_eps: float = 1e-6) -> PartitionTauResult:
    """Apply the DECISION 15 formula to one partition's spectral stats."""
    N_i = stats.N_i
    d = stats.d
    if N_i <= 0 or d <= 0:
        raise ValueError(f"invalid N_i={N_i} or d={d}")

    q_i = N_i / d
    sigma_sq_i = stats.trace_G_i / d
    lambda_plus_i = (1.0 + math.sqrt(q_i)) ** 2 * sigma_sq_i

    if not stats.eigenvalues_G_i:
        raise ValueError(f"no eigenvalues provided for partition {stats.partition_id}")
    theta_max_i = float(max(stats.eigenvalues_G_i))

    kappa_4_i = (stats.kappa_4_precomputed
                 if stats.kappa_4_precomputed is not None
                 else compute_kappa_4_from_eigenvalues(stats.eigenvalues_G_i))

    # alpha_i clipped to [1, 2] per spec
    alpha_raw = 1.0 + 0.5 * kappa_4_i
    alpha_i = max(1.0, min(2.0, alpha_raw))

    # Degenerate check: theta_max - lambda_plus must be positive for sqrt
    spike_gap = theta_max_i - lambda_plus_i
    degenerate = spike_gap <= degenerate_eps

    if degenerate:
        # Fall back to Kanerva closed-form per Research HARD-FAIL 2 spec
        # r_c = N/2 - sqrt(N * ln M)
        # Here we set tau_i = lambda_plus_i and beta_i = 0 (no spike)
        tau_i = lambda_plus_i
        beta_i = 0.0
    else:
        tau_i = lambda_plus_i + alpha_i * math.sqrt(spike_gap)
        beta_i = math.log(N_i) / spike_gap if N_i > 1 else 0.0

    return PartitionTauResult(
        partition_id=stats.partition_id,
        N_i=N_i, d=d,
        q_i=q_i, sigma_sq_i=sigma_sq_i,
        lambda_plus_i=lambda_plus_i,
        theta_max_i=theta_max_i,
        kappa_4_i=kappa_4_i,
        alpha_i=alpha_i,
        tau_i=tau_i,
        beta_i=beta_i,
        degenerate=degenerate,
        notes={"alpha_raw": alpha_raw, "spike_gap": spike_gap},
    )


def compute_tau_per_partition(per_partition_stats: list[PartitionSpectralStats]) -> dict:
    """Batch over partitions; returns {partition_id: PartitionTauResult}."""
    out = {}
    degenerate_count = 0
    for stats in per_partition_stats:
        r = compute_tau_for_partition(stats)
        out[r.partition_id] = r
        if r.degenerate:
            degenerate_count += 1
    return {
        "results": out,
        "n_partitions": len(per_partition_stats),
        "degenerate_count": degenerate_count,
        "degenerate_fraction": degenerate_count / max(1, len(per_partition_stats)),
    }


def _self_test():
    """Synthetic self-test: random Gram-matrix-like spectrum + verify formula."""
    # Simulate a partition with N=64 atoms in d=1024 dim, MP-like spectrum.
    # bulk eigenvalues from MP distribution + 1 BBP spike at theta_max
    import random
    random.seed(0)
    N = 64
    d = 1024
    sigma_sq = 1.0
    q = N / d
    lambda_plus_expected = (1.0 + math.sqrt(q)) ** 2 * sigma_sq

    # bulk: spread eigenvalues between lambda_minus and lambda_plus
    lambda_minus = (1.0 - math.sqrt(q)) ** 2 * sigma_sq
    bulk = [random.uniform(lambda_minus, lambda_plus_expected) for _ in range(N - 1)]
    # spike well above bulk edge
    spike = lambda_plus_expected * 4.0
    eigs = bulk + [spike]
    trace_G = sum(eigs)

    stats = PartitionSpectralStats(
        partition_id="self_test_partition",
        N_i=N, d=d,
        trace_G_i=trace_G,
        eigenvalues_G_i=eigs,
    )
    r = compute_tau_for_partition(stats)

    # Soundness checks
    assert r.tau_i > r.lambda_plus_i, "tau must exceed MP bulk edge"
    assert r.tau_i < r.theta_max_i, "tau must be below BBP spike"
    assert 1.0 <= r.alpha_i <= 2.0, "alpha must be in [1, 2]"
    assert not r.degenerate, "non-degenerate synthetic should not flag degenerate"
    assert r.beta_i > 0, "beta must be positive"
    print(f"  [selftest PASS] tau={r.tau_i:.4f} lambda_plus={r.lambda_plus_i:.4f} theta_max={r.theta_max_i:.4f}")
    print(f"  [selftest PASS] alpha={r.alpha_i:.4f} kappa_4={r.kappa_4_i:.4f} beta={r.beta_i:.4f}")

    # Degenerate-case test: directly invoke compute_tau_for_partition with
    # eigenvalues whose max is just barely above lambda_plus.
    # Construct: all eigs equal at value X, then trace = N*X, sigma_sq = X*q,
    # lambda_plus = X*q*(1+sqrt q)^2. theta_max = X. Spike gap = X*(1 - q*(1+sqrt q)^2).
    # To get spike_gap below degen_eps, need q*(1+sqrt q)^2 -> 1, i.e. q -> 1.
    # Use N == d so q == 1; then lambda_plus = X*4 > theta_max = X. spike_gap negative => degenerate.
    N_d_eq = 256
    d_eq = 256
    X = 1.0
    eigs_eq = [X] * N_d_eq
    degen_stats = PartitionSpectralStats(
        partition_id="degenerate_test",
        N_i=N_d_eq, d=d_eq,
        trace_G_i=sum(eigs_eq),
        eigenvalues_G_i=eigs_eq,
    )
    degen_r = compute_tau_for_partition(degen_stats)
    assert degen_r.degenerate, f"N==d partition should flag degenerate (got tau={degen_r.tau_i}, lambda_plus={degen_r.lambda_plus_i}, theta_max={degen_r.theta_max_i})"
    assert degen_r.tau_i == degen_r.lambda_plus_i, "degenerate fallback should set tau = lambda_plus"
    print(f"  [selftest PASS] degenerate fallback: tau={degen_r.tau_i:.4f} = lambda_plus={degen_r.lambda_plus_i:.4f}")


def main():
    """CLI: self-test the formula. Real measurement requires Gram matrices."""
    print("=== substrate_tau_calibration_v1 ===")
    print("Per DECISION 15: per-partition tau formula module (Testbed PRIMARY).")
    print("Runs self-tests on synthetic spectra. Real measurement needs")
    print("Gram matrices computed upstream (runner-desktop / Exp-Dev).\n")
    _self_test()
    print("\nFormula ready for Exp-Dev integration with real per-partition Gram matrices.")


if __name__ == "__main__":
    main()
