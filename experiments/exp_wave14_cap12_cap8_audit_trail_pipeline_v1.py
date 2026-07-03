"""Composition A audit-trail anchor: kappa_n divergence components vs.
Schur-Weyl irrep mass fractions across codebook families.

Motivation
----------
Composition A (Cap 12 routing + Cap 8 VAMP-on-chain audit-trail) was re-
affirmed at strategy cycle 197 post-Composition-B-kill. Research's
2026-05-24 audit (notes/research_antiRM_and_compA_audit_2026-05-24.md)
identified the shared mechanism as the **kappa_n algebra serving as
PROVENANCE VOCABULARY across a clean layer boundary** (pre-flight
diagnostic -> primitive readout), NOT a shared score (which is what
killed Composition B).

This anchor experiment makes that structural claim falsifiable by
quantitatively pairing two algebraic-label sets across the layer:

  - Cap 12 routing fingerprint = the n-th free cumulant divergence
    component  |kappa_n_emp - kappa_n_MP|  (n=2..5), measured on the
    (1/N) A^T A spectrum.
  - Cap 8 provenance receipt = the Schur-Weyl irrep mass fraction of
    the singular-spectrum tensors at n=2..5; specifically the mass
    of the totally-symmetric irrep (n) in the n-th symmetric tensor
    power of the singular spectrum (via the Schur polynomial s_(n)
    relative to the full s_lambda sum over lambda |= n).

Hypothesis
----------
If the kappa_n moments and the Schur-Weyl irrep masses index the SAME
representation-theoretic structure (free-probabilistic moments vs.
the n-th tensor representation of the singular spectrum), then their
component-wise divergence-from-MP should correlate across codebooks.

The pairing is anchored as follows.  For each codebook family C and
order n in {2,3,4,5}:
  x_n(C) = | kappa_n_emp(C) - kappa_n_MP |     (kappa divergence at order n)
  y_n(C) = | schur_mass_emp_(n)(C) - schur_mass_MP_(n) |
                                              (Schur-Weyl irrep (n) mass
                                               deviation from MP at order n)

We compute the Spearman rho between x and y across the 4 orders n=2..5
for each codebook family separately, then aggregate.

HARD PASS (Composition A licensed)
----------------------------------
  Spearman rho(x_n, y_n) >= 0.60 across >= 3 of 4 families
  AND no family with rho < 0.30.

HARD FAIL (Composition A killed; prose-only juxtaposition)
----------------------------------------------------------
  Spearman rho < 0.30 on >= 2 of 4 families.

MIDDLE BAND
-----------
  rho in [0.30, 0.60) on 1-2 families with the rest passing; weak
  structural sharing; composition stays plausible but does NOT
  elevate; per-family annotation language tightening required.

Codebook families
-----------------
  1. Kerdock 4-coset      (4N codewords, N=2^m)
  2. SRHT                 (subsampled randomized Hadamard transform)
  3. Hadamard             (plain row-subsampled Sylvester Hadamard)
  4. RM(1, m)             (Reed-Muller order-1: H rows union -H rows)

Gold sequences (length 2^m - 1) are excluded from the 4-family hard
band because RM(1,m) is the most direct overlap with the Cap 12
fingerprint set in v174 / v175.  If wallclock allows we also include
Gold as a 5th informational family but it does not count toward the
hard-pass / hard-fail tallies.

Method (operational definitions)
--------------------------------
Schur-Weyl irrep (lambda) mass fraction at order n.  Let
{lambda_1, ..., lambda_M} be the eigenvalues of (1/N) A^T A; define
power sums p_k = sum_i lambda_i^k.  By the Frobenius character
formula, the Schur polynomial in those eigenvalues is:

  s_lambda(p) = sum_{mu |= n} chi^lambda(mu) / z_mu  *  p_mu

where chi^lambda(mu) is the character of irrep lambda evaluated at
conjugacy class mu (partition of n) and p_mu = prod_i p_{mu_i};
z_mu = prod_k k^{m_k(mu)} * m_k(mu)! is the size of the centralizer.

The Schur-Weyl irrep mass fraction at lambda |= n is then

  schur_mass_lambda(C) = s_lambda(p(C))  /  sum_{lambda' |= n} s_lambda'(p(C))

For the "kappa_n vs irrep (n) mass" pairing we focus on lambda = (n)
(single-row partition), whose Schur polynomial is the complete
homogeneous symmetric polynomial h_n.  This is the "fully symmetric"
irrep mass.

Self-tests
----------
1. Newton-Girard sanity: for iid Gaussian at large N, p_n should match
   the MP moment closed form sum_k C(n,k)C(n,k-1)c^k/n within 5%.
2. Schur-Weyl character table sanity: chi^(2)(1,1)=1, chi^(2)(2)=1;
   chi^(1,1)(1,1)=1, chi^(1,1)(2)=-1; Schur polynomial closed-form
   s_(2)(p) = (p_1^2 + p_2) / 2 verified.
3. Schur-Weyl mass sums to 1 across all partitions of n.
4. Marchenko-Pastur Schur-Weyl masses computed analytically (using
   MP power-sum closed form) and used as the reference baseline.

Smoke
-----
N=512 (smaller Kerdock), 1 seed per codebook, n in {2,3,4} (skip 5 for
speed); the verdict will be INCONCLUSIVE on smoke (not enough seeds
for Spearman) but the metrics.json should contain valid Schur-Weyl
masses and the self-tests must pass.

Pre-reg: preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse cross-codebook builders for Kerdock, SRHT, Hadamard, RM(1,m), iid_gauss.
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_kerdock = _cc.build_kerdock
build_srht = _cc.build_srht
build_hadamard = _cc.build_hadamard
build_rm_1_m = _cc.build_rm_1_m
build_iid_gauss = _cc.build_iid_gauss

# Reuse the moment-to-free-cumulant inversion and MP reference.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
mp_reference_moments = _v1.mp_reference_moments
mp_reference_cumulants = _v1.mp_reference_cumulants


# ---------------------------------------------------------------------------
# Integer partitions of n
# ---------------------------------------------------------------------------

def _partitions(n: int, max_part: int | None = None):
    """Yield all integer partitions of n as tuples in weakly decreasing order."""
    if n == 0:
        yield ()
        return
    if max_part is None:
        max_part = n
    for first in range(min(n, max_part), 0, -1):
        for rest in _partitions(n - first, max_part=first):
            yield (first,) + rest


def integer_partitions(n: int) -> list[tuple[int, ...]]:
    """All partitions of n, weakly decreasing.  Cached for n<=10."""
    return list(_partitions(n))


# ---------------------------------------------------------------------------
# Schur-Weyl irrep characters (Murnaghan-Nakayama for small n)
# ---------------------------------------------------------------------------

def murnaghan_nakayama(lam: tuple[int, ...], mu: tuple[int, ...]) -> int:
    """Compute the symmetric-group character chi^lambda(mu).

    Implementation: Murnaghan-Nakayama rule.  chi^lambda(mu) =
    sum over rim hooks R of length mu[0] in lambda of
        (-1)^(height(R)) * chi^(lambda \\ R)(mu[1:])

    Base case: empty partition -> chi^()() = 1.
    """
    if sum(lam) != sum(mu):
        return 0
    if len(mu) == 0:
        # Both empty
        return 1 if len(lam) == 0 else 0

    # Choose the largest part of mu first (canonical Murnaghan-Nakayama).
    r = mu[0]
    mu_rest = mu[1:]

    total = 0
    # Find all rim hooks of length r in lam.
    # A rim hook is a connected set of border cells of length r whose removal
    # leaves a valid partition.
    # We use the bijection: rim hooks of length r in lambda correspond to
    # ways to subtract r from one entry of (lambda + delta) where delta =
    # (len(lam)-1, len(lam)-2, ..., 0), such that the result is still
    # strictly decreasing and >= 0, then sort and subtract delta.
    n = len(lam)
    if n == 0:
        return 0

    delta = list(range(n - 1, -1, -1))
    beta = [lam[i] + delta[i] for i in range(n)]  # strictly decreasing >= 0

    for i in range(n):
        new_beta_i = beta[i] - r
        if new_beta_i < 0:
            continue
        # Must not equal any other beta[j] (j != i) -- otherwise the resulting
        # "partition" via beta has a duplicate, which means the rim hook
        # crosses an invalid boundary.
        if any(new_beta_i == beta[j] for j in range(n) if j != i):
            continue
        # Compute new beta sequence and the "height" of the rim hook.
        # Height = number of beta[j] (j != i) such that new_beta_i < beta[j] < beta[i].
        height = sum(1 for j in range(n) if j != i and new_beta_i < beta[j] < beta[i])

        new_beta = beta.copy()
        new_beta[i] = new_beta_i
        new_beta_sorted = sorted(new_beta, reverse=True)
        new_lam = tuple(new_beta_sorted[j] - delta[j] for j in range(n))
        # Strip trailing zeros
        while new_lam and new_lam[-1] == 0:
            new_lam = new_lam[:-1]
        sign = (-1) ** height
        total += sign * murnaghan_nakayama(new_lam, mu_rest)

    return total


def z_mu(mu: tuple[int, ...]) -> int:
    """Centralizer size: z_mu = prod_k k^{m_k} * m_k!  where m_k = multiplicity of k."""
    from collections import Counter
    mults = Counter(mu)
    out = 1
    for k, m_k in mults.items():
        out *= (k ** m_k) * math.factorial(m_k)
    return out


# ---------------------------------------------------------------------------
# Schur polynomial via Frobenius character formula
# ---------------------------------------------------------------------------

def power_sums_from_eig(eig: np.ndarray, n_max: int) -> list[float]:
    """Normalized power sums p_k = (1/M) sum_i lambda_i^k = m_k.

    We use NORMALIZED (intensive) moments rather than raw (extensive) power
    sums because raw p_k scale as M (sum over M eigenvalues) while p_1^k
    scales as M^k -- which causes Schur-Weyl irrep mass fractions to be
    dominated by the all-singletons partition (1^n) in the M -> infinity
    limit (Plancherel concentration).  Using moments m_k = (1/M) p_k makes
    the Schur-Weyl mass fractions reflect the shape of the spectral measure
    (intensive), not the sample size (extensive), which is the appropriate
    "intensive provenance fingerprint" for the audit-trail comparison.

    This corresponds to evaluating the Schur polynomials in the EMPIRICAL
    SPECTRAL DENSITY's moments rather than the raw eigenvalue power sums.
    """
    M = len(eig)
    return [float(np.mean(eig ** k)) for k in range(1, n_max + 1)]


def schur_polynomial_in_power_sums(lam: tuple[int, ...],
                                    power_sums: list[float]) -> float:
    """s_lambda(p_1, ..., p_n) via Frobenius:
        s_lambda = sum_{mu |= n} chi^lambda(mu) / z_mu * p_mu
    where p_mu = prod_i p_{mu_i}.
    """
    n = sum(lam)
    total = 0.0
    for mu in integer_partitions(n):
        chi = murnaghan_nakayama(lam, mu)
        if chi == 0:
            continue
        z = z_mu(mu)
        p_mu = 1.0
        for part in mu:
            p_mu *= power_sums[part - 1]
        total += chi * p_mu / z
    return total


def schur_weyl_irrep_masses(eig: np.ndarray, n: int) -> dict:
    """For a given order n, compute s_lambda(power_sums(eig)) for all lambda |= n,
    then normalize to a probability distribution over partitions of n.

    Returns:
        {
          "partitions": [...],
          "s_lambda":   [...],  # raw Schur values
          "masses":     [...],  # normalized (sum to 1)
          "mass_n":     float,  # mass at the single-row partition (n,)
          "mass_111":   float,  # mass at the all-singletons partition (1,..,1)
        }
    """
    p = power_sums_from_eig(eig, n)
    parts = integer_partitions(n)
    s_vals = [schur_polynomial_in_power_sums(lam, p) for lam in parts]

    # Schur polynomials in non-negative reals (eigenvalues of A^T A >= 0)
    # are non-negative; we floor at 0 to avoid tiny-negative numerical noise.
    s_vals_pos = [max(0.0, v) for v in s_vals]
    s_total = sum(s_vals_pos)
    if s_total <= 0:
        masses = [0.0 for _ in parts]
    else:
        masses = [v / s_total for v in s_vals_pos]

    mass_n = 0.0
    mass_singletons = 0.0
    for i, lam in enumerate(parts):
        if lam == (n,):
            mass_n = masses[i]
        if all(x == 1 for x in lam):
            mass_singletons = masses[i]

    return {
        "partitions": [list(p) for p in parts],
        "s_lambda": s_vals,
        "masses": masses,
        "mass_n": mass_n,
        "mass_111": mass_singletons,
    }


def schur_weyl_irrep_masses_from_mp(c: float, n: int, M: int | None = None) -> dict:
    """Analytic baseline: Schur-Weyl masses computed from MP MOMENTS.

    Following the same convention as `schur_weyl_irrep_masses` (which feeds
    intensive moments m_k = (1/M) sum lambda_i^k into the Schur polynomials),
    we plug the MP closed-form moments m_k directly as the "power sums" of
    the Schur character formula.  This yields the Schur-Weyl mass of the
    MP-distributed empirical spectral measure -- the analytic reference
    against which empirical codebook spectra are compared.

    The M argument is accepted for backward compatibility but is not used
    (Schur-Weyl masses of moments are M-invariant once we work at the
    spectral-measure level).
    """
    del M  # backward compat; unused in intensive-moment convention
    moms = mp_reference_moments(c, n)
    parts = integer_partitions(n)
    s_vals = [schur_polynomial_in_power_sums(lam, moms) for lam in parts]
    s_vals_pos = [max(0.0, v) for v in s_vals]
    s_total = sum(s_vals_pos)
    if s_total <= 0:
        masses = [0.0 for _ in parts]
    else:
        masses = [v / s_total for v in s_vals_pos]

    mass_n = 0.0
    for i, lam in enumerate(parts):
        if lam == (n,):
            mass_n = masses[i]
    return {"partitions": [list(p) for p in parts], "masses": masses,
            "mass_n": mass_n}


# ---------------------------------------------------------------------------
# Spearman rank correlation (no scipy dependency in case CPU runner is bare)
# ---------------------------------------------------------------------------

def spearman_rho(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation; ties handled with average ranks."""
    n = len(x)
    if n < 2 or len(y) != n:
        return float("nan")

    def _ranks(arr: list[float]) -> list[float]:
        idx = sorted(range(n), key=lambda i: arr[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and arr[idx[j + 1]] == arr[idx[i]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[idx[k]] = avg_rank
            i = j + 1
        return ranks

    rx = _ranks(x)
    ry = _ranks(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx < 1e-12 or dy < 1e-12:
        return float("nan")
    return num / (dx * dy)


# ---------------------------------------------------------------------------
# Per-codebook measurement
# ---------------------------------------------------------------------------

def measure_codebook_audit_trail(name: str, builder, N: int, M: int,
                                  n_seeds: int, n_max: int) -> dict:
    """For one codebook family: compute kappa_n divergence components AND
    Schur-Weyl irrep (n)-mass deviations at orders n=2..n_max.

    Returns per-seed records and aggregate Spearman rho between the two
    fingerprint vectors.
    """
    c_ref = M / N
    mp_moms = mp_reference_moments(c_ref, n_max)
    mp_kappas = mp_reference_cumulants(c_ref, n_max)
    mp_mass_n_by_order = {}
    for n in range(2, n_max + 1):
        mp_info = schur_weyl_irrep_masses_from_mp(c_ref, n, M=M)
        mp_mass_n_by_order[n] = mp_info["mass_n"]

    per_seed = []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 13
        A = builder(N, M, seed_val)
        s = np.linalg.svd(A, compute_uv=False)
        eig = (s ** 2).astype(np.float64)

        # Empirical moments and free cumulants
        moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
        kappas = moments_to_free_cumulants_general(moms)

        # Kappa-n divergence components (relative to MP reference)
        kappa_div = []
        for n in range(2, n_max + 1):
            kappa_div.append(abs(kappas[n - 1] - mp_kappas[n - 1]))

        # Schur-Weyl irrep (n)-mass deviations from MP at orders n=2..n_max
        sw_mass_n = []
        sw_full = []
        for n in range(2, n_max + 1):
            sw = schur_weyl_irrep_masses(eig, n)
            mass_dev = abs(sw["mass_n"] - mp_mass_n_by_order[n])
            sw_mass_n.append(mass_dev)
            sw_full.append({"order": n, "mass_n": sw["mass_n"],
                            "mp_mass_n": mp_mass_n_by_order[n],
                            "mass_dev": mass_dev,
                            "masses_by_partition": dict(zip(
                                [tuple(p) for p in sw["partitions"]],
                                sw["masses"]
                            ))})

        # Per-seed Spearman rho across the n=2..n_max indices
        rho = spearman_rho(kappa_div, sw_mass_n)

        per_seed.append({
            "seed": seed_val,
            "kappas": kappas,
            "kappa_divergence_components": kappa_div,
            "schur_weyl_mass_n_deviations": sw_mass_n,
            "schur_weyl_full": [{"order": d["order"], "mass_n": d["mass_n"],
                                  "mp_mass_n": d["mp_mass_n"],
                                  "mass_dev": d["mass_dev"]}
                                 for d in sw_full],
            "rho_per_seed": rho,
        })
        print(f"    {name:10s} seed={seed} rho={rho:.4f} "
              f"kappa_div={[f'{v:.3f}' for v in kappa_div]} "
              f"sw_mass_n_dev={[f'{v:.3f}' for v in sw_mass_n]}", flush=True)

    # Aggregate Spearman rho via mean of per-seed Spearman rho values
    valid_rhos = [r["rho_per_seed"] for r in per_seed
                  if math.isfinite(r["rho_per_seed"])]
    rho_mean = float(np.mean(valid_rhos)) if valid_rhos else float("nan")
    rho_std = float(np.std(valid_rhos)) if len(valid_rhos) > 1 else 0.0

    # Also compute Spearman rho on the seed-averaged fingerprint vectors
    if per_seed:
        kappa_div_mean = np.mean([r["kappa_divergence_components"] for r in per_seed], axis=0).tolist()
        sw_mass_n_mean = np.mean([r["schur_weyl_mass_n_deviations"] for r in per_seed], axis=0).tolist()
        rho_aggregate = spearman_rho(kappa_div_mean, sw_mass_n_mean)
    else:
        kappa_div_mean = []
        sw_mass_n_mean = []
        rho_aggregate = float("nan")

    return {
        "name": name,
        "rho_mean_of_seeds": rho_mean,
        "rho_std_of_seeds": rho_std,
        "rho_aggregate": rho_aggregate,
        "kappa_div_mean": kappa_div_mean,
        "sw_mass_n_mean": sw_mass_n_mean,
        "per_seed": per_seed,
    }


# ---------------------------------------------------------------------------
# Codebook registry: 4 main families for hard band + Gold (informational)
# ---------------------------------------------------------------------------

# We re-implement a small Gold-family builder inline so we don't depend on
# the quickprobe script's exact API.  Length is 2^m - 1; we pad to N=power-of-2
# by truncating to M rows of length N (not padding zeros, which would distort
# the spectrum); since SRHT/Kerdock/Hadamard live at N=2^m, Gold's natural
# length 2^m - 1 makes direct M=N comparison tricky.  We therefore build Gold
# at N_gold = 2^m - 1 with M_gold = N_gold and treat it as a fifth, informational
# family with c_ref = 1.0 still applied.

def build_gold_m10(N_target: int, M: int, seed: int) -> np.ndarray:
    """Build a Gold-sequence codebook (M, N_gold) at m=10 (N_gold=1023).

    The N_target arg is IGNORED for Gold (its natural length is fixed by m).
    Caller must verify N_gold matches whatever c_ref it's comparing to.
    """
    _quick_path = REPO / "experiments" / "exp_wave14_kappa_gold_quickprobe_v1.py"
    spec = importlib.util.spec_from_file_location("gold_quick", _quick_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fam = mod.gold_sequence_family(m=10)  # (N_gold+2, N_gold) in {0,1}
    N_gold = fam.shape[1]
    rng = np.random.default_rng(seed)
    idx = rng.choice(fam.shape[0], size=M, replace=False)
    A = (1.0 - 2.0 * fam[idx]).astype(np.float32)  # bipolar map: 0 -> +1, 1 -> -1
    return (A / math.sqrt(N_gold)).astype(np.float32)


HARD_FAMILIES = [
    ("kerdock", build_kerdock),
    ("srht", build_srht),
    ("hadamard", build_hadamard),
    ("rm_1_m", build_rm_1_m),
]


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """HARD PASS: rho_aggregate >= 0.60 across >= 3 of 4 hard families AND
    no family with rho_aggregate < 0.30.

    HARD FAIL: rho_aggregate < 0.30 on >= 2 of 4 hard families.

    MIDDLE BAND: anything else.

    Family rho used here is the rho on the seed-averaged fingerprint vector
    (rho_aggregate) for stability; per-seed rho is reported but not used
    in the verdict (n_max - 1 = 3 points per seed gives high variance).
    """
    cbs = summary.get("codebook_results") or []
    hard_results = [c for c in cbs if c["name"] in [nm for nm, _ in HARD_FAMILIES]]
    if len(hard_results) < 4:
        return ("COMPA_AUDIT_INCONCLUSIVE",
                f"Composition A audit INCONCLUSIVE: only {len(hard_results)} of "
                f"4 hard families measured; need all of {[nm for nm,_ in HARD_FAMILIES]}.")

    rhos = {c["name"]: c["rho_aggregate"] for c in hard_results}
    summary["rho_by_family"] = rhos

    pass_count = sum(1 for v in rhos.values() if math.isfinite(v) and v >= 0.60)
    fail_count = sum(1 for v in rhos.values() if math.isfinite(v) and v < 0.30)
    any_low = any(math.isfinite(v) and v < 0.30 for v in rhos.values())

    if pass_count >= 3 and not any_low:
        return ("COMPA_AUDIT_LICENSED",
                f"Composition A LICENSED: Spearman rho(kappa_n_div, schur_weyl_mass_n_dev) "
                f">= 0.60 in {pass_count}/4 hard families, no family below 0.30. "
                f"kappa_n algebra and Schur-Weyl algebra share REAL structure across "
                f"the Cap 12 -> Cap 8 layer boundary, not prose-only. rhos={rhos}")

    if fail_count >= 2:
        return ("COMPA_AUDIT_KILLED",
                f"Composition A KILLED: Spearman rho < 0.30 on {fail_count}/4 hard "
                f"families. kappa_n vocabulary does NOT carry across the layer "
                f"boundary; the audit-trail framing is prose-only at the quantitative "
                f"level. Caps 12 and 8 remain independently OK; the composition story "
                f"does not elevate. rhos={rhos}")

    return ("COMPA_AUDIT_MIDDLE_BAND",
            f"Composition A MIDDLE BAND: weak structural sharing. "
            f"pass>=0.60 in {pass_count}/4 families; below-0.30 in {fail_count}/4. "
            f"Composition stays plausible per-family but the v169 closed-form "
            f"annotations should narrow to family-specific language. rhos={rhos}")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _self_test_partitions() -> None:
    """Partition counts must match p(n)."""
    expected = {0: 1, 1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 11}
    for n, e in expected.items():
        got = len(integer_partitions(n))
        assert got == e, f"partitions({n}) returned {got}, expected {e}"


def _self_test_characters() -> None:
    """Hand-computed Murnaghan-Nakayama character table sanity checks.

    Source: standard S_n irrep characters (e.g. Sagan 'The Symmetric Group' Ch.1).

    S_2 character table:
                (1,1)   (2)
        chi^(2)   1     1
        chi^(11)  1    -1

    S_3 character table:
                (1,1,1)  (2,1)  (3)
        chi^(3)    1       1     1
        chi^(21)   2       0    -1
        chi^(111)  1      -1     1

    S_4 character table (5 irreps x 5 classes (4), (3,1), (2,2), (2,1,1), (1,1,1,1)):
                (1,1,1,1)  (2,1,1)  (2,2)  (3,1)  (4)
        chi^(4)        1       1       1      1     1
        chi^(3,1)      3       1      -1      0    -1
        chi^(2,2)      2       0       2     -1     0
        chi^(2,1,1)   3      -1      -1      0     1
        chi^(1,1,1,1)  1      -1       1      1    -1
    """
    # S_2
    assert murnaghan_nakayama((2,), (1, 1)) == 1
    assert murnaghan_nakayama((2,), (2,)) == 1
    assert murnaghan_nakayama((1, 1), (1, 1)) == 1
    assert murnaghan_nakayama((1, 1), (2,)) == -1

    # S_3
    assert murnaghan_nakayama((3,), (1, 1, 1)) == 1
    assert murnaghan_nakayama((3,), (2, 1)) == 1
    assert murnaghan_nakayama((3,), (3,)) == 1
    assert murnaghan_nakayama((2, 1), (1, 1, 1)) == 2
    assert murnaghan_nakayama((2, 1), (2, 1)) == 0
    assert murnaghan_nakayama((2, 1), (3,)) == -1
    assert murnaghan_nakayama((1, 1, 1), (1, 1, 1)) == 1
    assert murnaghan_nakayama((1, 1, 1), (2, 1)) == -1
    assert murnaghan_nakayama((1, 1, 1), (3,)) == 1

    # S_4 spot checks
    assert murnaghan_nakayama((4,), (1, 1, 1, 1)) == 1
    assert murnaghan_nakayama((4,), (4,)) == 1
    assert murnaghan_nakayama((3, 1), (1, 1, 1, 1)) == 3
    assert murnaghan_nakayama((3, 1), (4,)) == -1
    assert murnaghan_nakayama((3, 1), (2, 2)) == -1
    assert murnaghan_nakayama((2, 2), (1, 1, 1, 1)) == 2
    assert murnaghan_nakayama((2, 2), (2, 2)) == 2
    assert murnaghan_nakayama((2, 2), (3, 1)) == -1
    assert murnaghan_nakayama((2, 1, 1), (1, 1, 1, 1)) == 3
    assert murnaghan_nakayama((2, 1, 1), (4,)) == 1
    assert murnaghan_nakayama((1, 1, 1, 1), (1, 1, 1, 1)) == 1
    assert murnaghan_nakayama((1, 1, 1, 1), (4,)) == -1


def _self_test_schur_closed_form() -> None:
    """Closed-form Schur polynomials in power sums (small partitions).

    s_(1)(p)         = p_1
    s_(2)(p)         = (p_1^2 + p_2) / 2
    s_(1,1)(p)       = (p_1^2 - p_2) / 2
    s_(3)(p)         = (p_1^3 + 3*p_1*p_2 + 2*p_3) / 6
    s_(2,1)(p)       = (p_1^3 - p_3) / 3
    s_(1,1,1)(p)     = (p_1^3 - 3*p_1*p_2 + 2*p_3) / 6

    Plus identity s_(n) + ... + s_(1,..,1) summed over partitions of n
    equals h_n + ... = sum_lambda s_lambda.  We use a test based on the
    column-sum identity in the character table: for the partition mu=(1^n)
    of n,  sum_lambda chi^lambda(mu) * dim(lambda) = n! * delta_{mu, (1^n)},
    where dim(lambda) = chi^lambda(1^n).  So sum_lambda chi^lambda(1^n)^2 = n!.
    """
    # Closed-form check for s_(2)
    p = [3.0, 5.0, 7.0]  # arbitrary positive power sums
    s_2 = schur_polynomial_in_power_sums((2,), p)
    expected_s2 = (p[0] ** 2 + p[1]) / 2.0
    assert abs(s_2 - expected_s2) < 1e-9, f"s_(2) closed form failed: {s_2} vs {expected_s2}"

    s_11 = schur_polynomial_in_power_sums((1, 1), p)
    expected_s11 = (p[0] ** 2 - p[1]) / 2.0
    assert abs(s_11 - expected_s11) < 1e-9, f"s_(1,1) closed form failed: {s_11} vs {expected_s11}"

    s_3 = schur_polynomial_in_power_sums((3,), p)
    expected_s3 = (p[0] ** 3 + 3.0 * p[0] * p[1] + 2.0 * p[2]) / 6.0
    assert abs(s_3 - expected_s3) < 1e-9, f"s_(3) closed form failed: {s_3} vs {expected_s3}"

    s_21 = schur_polynomial_in_power_sums((2, 1), p)
    expected_s21 = (p[0] ** 3 - p[2]) / 3.0
    assert abs(s_21 - expected_s21) < 1e-9, f"s_(2,1) closed form failed: {s_21} vs {expected_s21}"

    s_111 = schur_polynomial_in_power_sums((1, 1, 1), p)
    expected_s111 = (p[0] ** 3 - 3.0 * p[0] * p[1] + 2.0 * p[2]) / 6.0
    assert abs(s_111 - expected_s111) < 1e-9, f"s_(1,1,1) closed form failed: {s_111} vs {expected_s111}"

    # Column-sum check: sum_lambda dim(lambda)^2 = n!  (dim(lambda) = chi^lambda(1^n))
    for n in range(1, 6):
        ones = tuple([1] * n)
        total = 0
        for lam in integer_partitions(n):
            d = murnaghan_nakayama(lam, ones)
            total += d * d
        assert total == math.factorial(n), (
            f"Plancherel measure check failed at n={n}: sum dim^2 = {total} "
            f"!= n! = {math.factorial(n)}"
        )


def _self_test_mass_normalization() -> None:
    """For non-negative power sums (any positive spectrum), Schur-Weyl masses
    must sum to 1 and be in [0, 1].
    """
    rng = np.random.default_rng(42)
    eig = rng.uniform(0.1, 2.0, size=256)  # toy positive spectrum
    for n in range(2, 5):
        info = schur_weyl_irrep_masses(eig, n)
        s_total_pos = sum(max(0.0, v) for v in info["s_lambda"])
        assert s_total_pos > 0, f"Schur masses all zero at n={n}"
        mass_sum = sum(info["masses"])
        assert abs(mass_sum - 1.0) < 1e-6, f"Schur masses sum to {mass_sum} at n={n}"
        for m in info["masses"]:
            assert -1e-9 <= m <= 1.0 + 1e-9, f"mass out of [0,1] at n={n}: {m}"


def _self_test_spearman() -> None:
    """Spearman rho hand checks."""
    assert abs(spearman_rho([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9
    assert abs(spearman_rho([1, 2, 3, 4], [4, 3, 2, 1]) - (-1.0)) < 1e-9
    # Mixed
    rho = spearman_rho([1, 2, 3, 4, 5], [1, 3, 2, 4, 5])
    # ranks identical except 2&3 swapped: rho = 1 - 6*2/(5*24) = 1 - 12/120 = 0.9
    assert abs(rho - 0.9) < 1e-9, f"Spearman swap test rho={rho}"


def _self_test_mp_sanity() -> None:
    """For an iid Gaussian matrix at N=1024, M=1024, alpha=1, the empirical
    Schur-Weyl irrep masses at n=2..4 should match the MP analytic masses
    to within 5% (a generous tolerance for one seed at N=1024).
    """
    rng = np.random.default_rng(7)
    N = 1024
    M = N
    A = (rng.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    s = np.linalg.svd(A, compute_uv=False)
    eig = (s ** 2).astype(np.float64)
    for n in [2, 3, 4]:
        emp = schur_weyl_irrep_masses(eig, n)
        mp = schur_weyl_irrep_masses_from_mp(c=1.0, n=n, M=M)
        for lam, m_emp, m_mp in zip(emp["partitions"], emp["masses"], mp["masses"]):
            dev = abs(m_emp - m_mp)
            assert dev < 0.05, (
                f"iid Gaussian Schur-Weyl mass at n={n}, lam={lam}: "
                f"emp={m_emp:.4f} mp={m_mp:.4f} dev={dev:.4f} > 0.05"
            )


def self_test() -> None:
    _self_test_partitions()
    _self_test_characters()
    _self_test_schur_closed_form()
    _self_test_mass_normalization()
    _self_test_spearman()
    _self_test_mp_sanity()

    # Verdict branch tests
    # PASS branch
    summary_pass = {"codebook_results": [
        {"name": "kerdock",  "rho_aggregate": 0.85},
        {"name": "srht",     "rho_aggregate": 0.70},
        {"name": "hadamard", "rho_aggregate": 0.65},
        {"name": "rm_1_m",   "rho_aggregate": 0.55},  # in [0.30, 0.60)
    ]}
    v, _ = compute_verdict(summary_pass)
    # rho_aggregate >= 0.60 in 3/4 (kerdock, srht, hadamard), no family < 0.30
    assert v == "COMPA_AUDIT_LICENSED", f"PASS branch failed: {v}"

    summary_fail = {"codebook_results": [
        {"name": "kerdock",  "rho_aggregate": 0.85},
        {"name": "srht",     "rho_aggregate": 0.20},
        {"name": "hadamard", "rho_aggregate": 0.15},
        {"name": "rm_1_m",   "rho_aggregate": 0.55},
    ]}
    v, _ = compute_verdict(summary_fail)
    assert v == "COMPA_AUDIT_KILLED", f"FAIL branch failed: {v}"

    summary_middle = {"codebook_results": [
        {"name": "kerdock",  "rho_aggregate": 0.65},
        {"name": "srht",     "rho_aggregate": 0.45},
        {"name": "hadamard", "rho_aggregate": 0.40},
        {"name": "rm_1_m",   "rho_aggregate": 0.50},
    ]}
    v, _ = compute_verdict(summary_middle)
    assert v == "COMPA_AUDIT_MIDDLE_BAND", f"MIDDLE branch failed: {v}"

    summary_inconcl = {"codebook_results": [
        {"name": "kerdock", "rho_aggregate": 0.85},
        {"name": "srht",    "rho_aggregate": 0.70},
    ]}
    v, _ = compute_verdict(summary_inconcl)
    assert v == "COMPA_AUDIT_INCONCLUSIVE", f"INCONCLUSIVE branch failed: {v}"

    print("self_test passed (partitions, characters, closed-form Schur, mass-normalization, "
          "Spearman, iid MP sanity, all 4 verdict branches)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        # Smoke: small N, 1 seed, only Kerdock + iid_gauss; n_max=4 to keep
        # Schur-Weyl extraction cheap.  Verdict will be INCONCLUSIVE (missing
        # families) but the self-tests + Schur-Weyl extraction must pass.
        # Kerdock requires even log2(N) so we use N=1024.
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "n_max_order": 4,
            "codebooks": ["kerdock", "iid_gauss"],
            "include_gold": False,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N": 1.0,
            "n_seeds": 5,
            "n_max_order": 5,
            "codebooks": [nm for nm, _ in HARD_FAMILIES],
            "include_gold": True,
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    n_max = config["n_max_order"]
    n_seeds = config["n_seeds"]

    print(f"[setup] N={N} M={M} M/N={M/N:.3f} n_seeds={n_seeds} "
          f"n_max_order={n_max} codebooks={config['codebooks']} "
          f"include_gold={config['include_gold']}", flush=True)

    builder_map = {nm: b for nm, b in HARD_FAMILIES}
    builder_map["iid_gauss"] = build_iid_gauss

    codebook_results = []
    for nm in config["codebooks"]:
        builder = builder_map[nm]
        print(f"\n[codebook] {nm}", flush=True)
        result = measure_codebook_audit_trail(nm, builder, N, M, n_seeds, n_max)
        codebook_results.append(result)
        print(f"  AGG {nm}: rho_aggregate={result['rho_aggregate']:.4f} "
              f"rho_mean_seeds={result['rho_mean_of_seeds']:.4f} "
              f"kappa_div_mean={[f'{v:.3f}' for v in result['kappa_div_mean']]} "
              f"sw_mass_n_mean={[f'{v:.3f}' for v in result['sw_mass_n_mean']]}",
              flush=True)

    if config.get("include_gold"):
        # Gold uses N_gold = 1023; it's informational only.
        print(f"\n[codebook] gold_m10 (informational; N=1023)", flush=True)
        result = measure_codebook_audit_trail("gold_m10", build_gold_m10,
                                               N=1023, M=1023,
                                               n_seeds=n_seeds, n_max=n_max)
        codebook_results.append(result)
        print(f"  AGG gold_m10: rho_aggregate={result['rho_aggregate']:.4f}",
              flush=True)

    summary = {"codebook_results": codebook_results, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def _json_default(o):
    """Coerce numpy scalars + tuples and other non-JSON-serializable shapes."""
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return float(o)


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=_json_default))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks measured"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
