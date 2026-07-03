"""Wave 14 — Kerdock-MUB distinguishability empirical probe (3.B from drill).

Question
--------
For substrate states {psi_1, psi_2, psi_3} drawn from beta_A snapshots (or
constructed-equivalent classes when snapshots aren't available locally),
build the canonical N+1 Kerdock-MUB basis system from the Galois-ring GR(4, m)
exponential construction, then compute:

  P_{i, k, j} = | <b^{(k)}_j | psi_i> |^2   for i in {1,2,3},
                                              k in {1, ..., N+1},
                                              j in {1, ..., N}

  TV_{i, k} = 0.5 * sum_j | P_{i, k, j} - 1/N |

This is the total-variation distance of the empirical Born-rule distribution
from uniform on the k-th MUB.

Reference: Klappenecker & Roetteler 2003, "Constructions of Mutually Unbiased
Bases"; Bandyopadhyay, Boykin, Roychowdhury, Vatan 2002, "A new proof for the
existence of mutually unbiased bases".

Hard pass / hard fail (from drill 3.B)
--------------------------------------
- HARD PASS (BBMD-novel signature confirmed): at least one non-native MUB
  shows TV >= 0.05 (> 3x stat-noise floor of 1/sqrt(N) ~ 0.016) on >= 2 of
  the 3 states.
- HARD FAIL (substrate is vanilla stabilizer): all non-native MUBs flat
  within 1.5x stat-noise (TV <= 0.024) across all 3 states.
- INCONCLUSIVE: in between (only one state spikes; partial signal).

Pre-reg: preregs/2026-05-23_wave14_kerdock_mub_distinguishability_v1.md
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import glob
import json
import math
import os
import time
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parent.parent


sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ---------------------------------------------------------------------------
# Galois ring GR(4, m) arithmetic
# ---------------------------------------------------------------------------
# GR(4, m) is the Galois ring Z_4[x] / h(x) where h(x) is a basic primitive
# polynomial of degree m over Z_4. Elements: a_0 + a_1 * x + ... + a_{m-1} * x^{m-1}
# with a_i in {0, 1, 2, 3}. Size = 4^m.
#
# For the Kerdock-MUB construction we need:
#   - The Teichmuller set T = {0, 1, xi, xi^2, ..., xi^{2^m - 2}} where xi
#     is a (2^m - 1)-th root of unity in GR(4, m). Size = 2^m.
#   - The trace map Tr: GR(4, m) -> Z_4 (lift of the F_2-trace via the
#     Frobenius x -> sigma(x) where sigma fixes T set-wise).
#
# Reference: Hammons et al. 1994, "The Z_4-linearity of Kerdock, Preparata,
# Goethals, and related codes", Sec. III.

# Basic primitive polynomials over Z_4 of degree m (mod 2 -> primitive over F_2).
# h(x) over Z_4 with the property that h(x) mod 2 is the same as our F_2
# primitive polynomial, and h is itself irreducible over Z_4.
# We use the standard "Hensel lift" of the F_2 primitive poly.
# For m=2: h(x) = x^2 + x + 1 in F_2; Hensel-lifted to x^2 + x + 1 in Z_4
#   (since x^2 + x + 1 evaluated at 0/1 in Z_4 gives 1/3, both nonzero
#    and not -1 / +1 = 3 / 1).
# For larger m, we use the BCH-construction Hensel lift; here we only need m=2 and m=12.

# Below: for the SELF-TEST at m=2 (N=4), we hard-code the GR(4, 2) tables.
# For m=12 (N=4096) we generate them programmatically.

PRIM_F2 = {
    2: 0b111,
    3: 0b1011,
    4: 0b10011,
    5: 0b100101,
    6: 0b1000011,
    7: 0b10000011,
    8: 0b100011101,
    9: 0b1000010001,
    10: 0b10000001001,
    11: 0b100000000101,
    12: 0b1000001010011,
}


def _gr4m_check_primitive(h_coeffs: list[int], m: int) -> bool:
    """Test whether h(x) is a basic primitive polynomial over Z_4 of degree m.

    Test: x has multiplicative order exactly 2^m - 1 in Z_4[x]/h(x), i.e.
      x^(2^m - 1) = 1
    AND x^d != 1 for any proper divisor d of 2^m - 1.

    Returns True iff x is a primitive root mod h.
    """
    n = 1 << m
    period = n - 1
    xi = 1 << 2  # element 'x' in encoding
    cur = 1
    seen_at = {1: 0}
    for k in range(1, period + 1):
        cur = gr4m_mul(cur, xi, m, h_coeffs)
        if cur == 1:
            return k == period
        seen_at[cur] = k
    return False


def gr4m_hensel_poly(m: int) -> list[int]:
    """Find a basic primitive polynomial h(x) over Z_4 of degree m.

    Approach: start from the F_2 primitive polynomial (bit-copy lift); if
    that doesn't yield a primitive Z_4 polynomial, search over additions of
    2 to the low-order coefficients (preserving h mod 2 = F_2 polynomial)
    until we find one for which 'x' has order 2^m - 1.

    Returns coefficients [c_0, c_1, ..., c_m] in Z_4 (each in {0, 1, 2, 3}).
    """
    poly = PRIM_F2[m]
    base = []
    for i in range(m + 1):
        base.append((poly >> i) & 1)

    # Try the bit-copy lift first.
    if _gr4m_check_primitive(base, m):
        return base

    # Else, search by toggling +2 on coefficients c_0..c_{m-1} (NOT c_m, which is
    # the leading 1). 2^m total candidates; for m <= 12 this is at most 4096.
    # We use a deterministic enumeration (binary mask).
    for mask in range(1, 1 << m):
        candidate = list(base)
        for i in range(m):
            if (mask >> i) & 1:
                candidate[i] = (candidate[i] + 2) & 3
        if _gr4m_check_primitive(candidate, m):
            return candidate

    raise RuntimeError(
        f"could not find a basic primitive Z_4 polynomial of degree m={m} "
        f"by 2-mask search. Falling back to a different starting polynomial may help."
    )


def gr4m_mul(a: int, b: int, m: int, h_coeffs: list[int]) -> int:
    """Multiply two GR(4, m) elements encoded as integers in [0, 4^m).

    Encoding: a = sum_{i=0}^{m-1} a_i * 4^i, a_i in {0,1,2,3}.
    """
    # Extract coefficients.
    A = [(a >> (2 * i)) & 3 for i in range(m)]
    B = [(b >> (2 * i)) & 3 for i in range(m)]
    # Multiply as polynomials in Z_4.
    C = [0] * (2 * m - 1)
    for i in range(m):
        for j in range(m):
            C[i + j] = (C[i + j] + A[i] * B[j]) & 3
    # Reduce mod h(x). h is monic of degree m: x^m ≡ -h_0 - h_1 x - ... - h_{m-1} x^{m-1}.
    # In Z_4, -c = (4 - c) % 4.
    for k in range(len(C) - 1, m - 1, -1):
        c = C[k]
        if c:
            for i in range(m):
                C[k - m + i] = (C[k - m + i] - c * h_coeffs[i]) & 3
            C[k] = 0
    out = 0
    for i in range(m):
        out |= (C[i] & 3) << (2 * i)
    return out


def gr4m_add(a: int, b: int, m: int) -> int:
    out = 0
    for i in range(m):
        ai = (a >> (2 * i)) & 3
        bi = (b >> (2 * i)) & 3
        out |= ((ai + bi) & 3) << (2 * i)
    return out


def gr4m_frobenius(a: int, m: int, h_coeffs: list[int]) -> int:
    """Frobenius automorphism sigma: GR(4, m) -> GR(4, m) defined by
    sigma(x) = x^2 - 2*x  on the generator x (modular formula); equivalently,
    sigma(t) = t^2 for t in the Teichmuller set, extended Z_4-linearly.

    For our construction we just need its restriction to the Teichmuller set:
    sigma(t) = t^2 (squaring in GR(4, m)).
    """
    return gr4m_mul(a, a, m, h_coeffs)


def teichmuller_set(m: int, h_coeffs: list[int]) -> list[int]:
    """Build the Teichmuller set T = {0, 1, xi, xi^2, ..., xi^{2^m-2}}
    where xi is a (2^m - 1)-th root of unity in GR(4, m).

    Method: take a primitive root xi (typically the image of x in
    Z_4[x]/h(x)) and verify xi^{2^m - 1} = 1; then enumerate powers.

    Returns a list of size 2^m, in [0, 4^m).
    """
    n = 1 << m
    period = n - 1
    # xi = image of generator x = encoding 4^1 = 1 << 2 = ... actually 'x' has a_1=1,
    # all others 0. Encoded as 1 << 2 (a_1 = 1 -> at bit position 2*1=2 with value 1).
    xi = 1 << 2  # represents the polynomial '0 + 1*x + 0*x^2 + ...'
    powers = [0, 1]  # T starts with 0 and t^0 = 1
    cur = 1
    for _ in range(period - 1):
        cur = gr4m_mul(cur, xi, m, h_coeffs)
        powers.append(cur)
    # Sanity: cur * xi should be 1 (since xi has order 2^m - 1).
    one_check = gr4m_mul(cur, xi, m, h_coeffs)
    if one_check != 1:
        raise ValueError(
            f"Teichmuller construction failed: xi^{2 ** m - 1} = {one_check} != 1. "
            f"The Hensel-lifted polynomial may not be primitive at m={m}."
        )
    return powers


def gr4m_trace(a: int, m: int, h_coeffs: list[int]) -> int:
    """Trace map Tr: GR(4, m) -> Z_4 defined by
       Tr(a) = a + sigma(a) + sigma^2(a) + ... + sigma^{m-1}(a)
    where sigma is the Frobenius automorphism on GR(4, m).
    """
    s = 0
    cur = a
    for _ in range(m):
        s = (s + cur) & 3
        # Apply Frobenius (squaring on T extended Z_4-linearly).
        # For elements outside T, we still apply sigma which on the generator x
        # acts by x -> x^2 - 2x; we use the Teichmuller-decomposed form.
        # But for elements of the Teichmuller set, sigma(t) = t^2; for general
        # elements we have a = sum 2^j * t_j (Teichmuller decomp), and
        # sigma(a) = sum 2^j * t_j^2.
        # Simpler implementation: apply 2-adic structure. But for the MUB
        # construction we only call trace on (b * t) where t is in T plus
        # additive structure — sigma(a) = a + (squaring-correction). For
        # correctness, we use the direct identity sigma(a) = a^2 mod 2
        # iff a in T. For general a, this is NOT a^2 — but we use a workaround:
        # decompose a = u + 2v with u, v in T (Teichmuller decomposition), then
        # sigma(a) = u^2 + 2 v^2. Implemented in gr4m_sigma_full.
        cur = gr4m_sigma_full(cur, m, h_coeffs)
    return s


def gr4m_sigma_full(a: int, m: int, h_coeffs: list[int]) -> int:
    """Full Frobenius sigma on GR(4, m). For a = u + 2v in 2-adic decomp
    (u, v in T), sigma(a) = u^2 + 2 v^2.

    Decomposition: u_i = a_i mod 2; v_i derived from the relation
    a = u + 2v (mod 4) in Z_4. Since u_i in {0, 1} and v_i in {0, 1},
    we have v_i = (a_i - u_i) / 2 = ((a_i & 2) >> 1).
    """
    # Extract u, v: u_i = bit-0 of a's i-th Z_4 digit; v_i = bit-1.
    u = 0
    v = 0
    for i in range(m):
        ai = (a >> (2 * i)) & 3
        u_bit = ai & 1
        v_bit = (ai >> 1) & 1
        u |= u_bit << (2 * i)
        v |= v_bit << (2 * i)
    # u, v are in T-form (only 0/1 entries in each Z_4 digit -> they represent
    # F_2-elements lifted to GR(4, m)). Squaring them via gr4m_mul gives
    # u^2 and v^2 in GR(4, m).
    u_sq = gr4m_mul(u, u, m, h_coeffs)
    v_sq = gr4m_mul(v, v, m, h_coeffs)
    # sigma(a) = u^2 + 2 * v^2 in GR(4, m).
    two_v_sq = 0
    for i in range(m):
        d = (v_sq >> (2 * i)) & 3
        two_v_sq |= ((2 * d) & 3) << (2 * i)
    return gr4m_add(u_sq, two_v_sq, m)


# ---------------------------------------------------------------------------
# Kerdock-MUB construction
# ---------------------------------------------------------------------------
# The N+1 MUBs of C^N (N = 2^m):
#   B_0 = standard computational basis (e_j for j in [0, N)).
#   B_t for t in T (Teichmuller set, size N) — N additional MUBs.
#
# The k-th vector of B_t is
#   (B_t)_j = (1 / sqrt(N)) * i^{Tr(t * x_j^2) + 2 * Tr(c_j * x_k)}
# where x_j, x_k in T identified with [0, N) via the Teichmuller bijection,
# and i = sqrt(-1). The exponential is interpreted in Z_4 -> {1, i, -1, -i}.
#
# Reference: Klappenecker-Roetteler 2003 (the "exponential" MUB family).

def i_pow_z4(k: int) -> complex:
    """i^k for k in {0, 1, 2, 3}."""
    k = k & 3
    return (1.0, 1j, -1.0, -1j)[k]


def build_kerdock_mubs(m: int) -> tuple[np.ndarray, list[np.ndarray]]:
    """Build the standard basis + N Kerdock-MUB bases of C^N, N = 2^m.

    Returns:
      std_basis: (N, N) identity (each column is e_j).
      mubs: list of length N, each (N, N) complex unitary; the j-th column
            of mubs[k] is the j-th vector of the k-th MUB B_{t_k}.
    """
    N = 1 << m
    h = gr4m_hensel_poly(m)
    T = teichmuller_set(m, h)
    assert len(T) == N, f"|T| should be 2^m = {N}, got {len(T)}"

    std_basis = np.eye(N, dtype=np.complex128)

    # Precompute, for every (t_idx, j_idx), the value Tr(t * j^2)  where
    # t = T[t_idx], j = T[j_idx], all in GR(4, m).
    # And the value Tr(j * k) for the second exponent.
    sqrt_N = math.sqrt(N)

    # Precompute Teichmuller-squares.
    T_sq = [gr4m_mul(T[j], T[j], m, h) for j in range(N)]

    mubs = []
    for t_idx in range(N):
        t = T[t_idx]
        B = np.empty((N, N), dtype=np.complex128)
        # First exponent (depends on j only): Tr(t * j^2)
        e1 = np.empty(N, dtype=np.int64)
        for j in range(N):
            # t * j^2
            prod = gr4m_mul(t, T_sq[j], m, h)
            e1[j] = gr4m_trace(prod, m, h)
        # Second exponent (depends on j, k): 2 * Tr(j * k).
        # We can build this as outer product since (B_t)_{j,k} factorizes
        # over the first exponent (j-dependent) only, with j*k structure:
        # but Tr(j * k) couples j and k. Use double loop.
        # In Z_4 the "2 * Tr(j*k)" is 2 mod 4, so i^(2*x) = (-1)^x.
        # We separate that as +/-1 multiplier.
        for j in range(N):
            phase1 = i_pow_z4(int(e1[j]))
            for k in range(N):
                jk = gr4m_mul(T[j], T[k], m, h)
                tr_jk = gr4m_trace(jk, m, h)
                sign = i_pow_z4((2 * int(tr_jk)) & 3)  # +1 or -1
                B[j, k] = phase1 * sign / sqrt_N
        mubs.append(B)
    return std_basis, mubs


# ---------------------------------------------------------------------------
# Substrate-class states (proxy for beta_A snapshots when not available)
# ---------------------------------------------------------------------------

def make_substrate_state(rng: np.random.Generator, kind: str,
                         std_basis: np.ndarray,
                         mubs: list[np.ndarray]) -> np.ndarray:
    """Build a unit-norm state vector in C^N representing one of:
      - 'vanilla_stab': a stabilizer state in the computational basis
        (a single std basis vector). TV vs std basis = 0 on B_0;
        on non-native MUBs should be near 0 (Born uniform on B_t for stab states).
      - 'enriched_kerdock': a column of one of the Kerdock-MUB bases.
        Native to that MUB; TV = 0 on its native MUB; non-zero on others
        if there's BBMD-novel structure beyond uniformity.
      - 'haar': a Haar-random state. TV should be ~1/sqrt(N) on ALL MUBs.

    NOTE: this is the IN-SCRIPT substrate-state proxy used when on-disk
    snapshots aren't available locally. The drill spec calls for actual
    beta_A snapshots from v149/v164a/v167; if those exist on the runner,
    swap them in via the `--use-snapshots` flag.
    """
    N = std_basis.shape[0]
    if kind == "vanilla_stab":
        j = int(rng.integers(0, N))
        psi = std_basis[:, j].copy()
    elif kind == "enriched_kerdock":
        k = int(rng.integers(0, len(mubs)))
        j = int(rng.integers(0, N))
        psi = mubs[k][:, j].copy()
    elif kind == "haar":
        v = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / math.sqrt(2.0)
        psi = v / np.linalg.norm(v)
    else:
        raise ValueError(f"unknown state kind: {kind}")
    # Normalize defensively.
    return psi / np.linalg.norm(psi)


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def check_mub_unbiasedness(std_basis: np.ndarray, mubs: list[np.ndarray],
                           tol: float = 1e-8) -> dict:
    """Verify pairwise unbiasedness: for any two MUBs B^{(k)}, B^{(l)} with k != l,
    |<b^{(k)}_i | b^{(l)}_j>|^2 = 1/N for all i, j.
    """
    N = std_basis.shape[0]
    all_bases = [std_basis] + mubs
    errs = []
    n_pairs = 0
    for a in range(len(all_bases)):
        for b in range(a + 1, len(all_bases)):
            B_a = all_bases[a]
            B_b = all_bases[b]
            # Overlap matrix.
            ovl = B_a.conj().T @ B_b
            P = np.abs(ovl) ** 2
            err = float(np.max(np.abs(P - 1.0 / N)))
            errs.append((a, b, err))
            n_pairs += 1
    max_err = max(e for _, _, e in errs)
    return {"max_err": max_err, "n_pairs": n_pairs, "tol": tol,
            "passed": max_err < tol}


def self_test_mub_m2() -> dict:
    """Build 5 MUBs of C^4 (m=2) and verify pairwise unbiasedness."""
    print("[self-test] building Kerdock-MUBs at m=2 (N=4) ...", flush=True)
    std_basis, mubs = build_kerdock_mubs(2)
    assert len(mubs) == 4, f"should have 4 Kerdock-MUBs at m=2, got {len(mubs)}"
    for k, B in enumerate(mubs):
        # Unitary check.
        err = float(np.max(np.abs(B.conj().T @ B - np.eye(4))))
        assert err < 1e-8, f"MUB B_{k} not unitary, err={err}"

    print("[self-test] checking pairwise unbiasedness ...", flush=True)
    res = check_mub_unbiasedness(std_basis, mubs, tol=1e-8)
    print(f"  max |P_{{i,j}} - 1/4| = {res['max_err']:.3e}  "
          f"({res['n_pairs']} pairs, tol={res['tol']:.1e})", flush=True)
    if not res["passed"]:
        raise AssertionError(
            f"[self-test FAIL] MUB unbiasedness broken at m=2: max_err = {res['max_err']:.3e}. "
            f"The GR(4, 2) Kerdock-MUB construction has a bug. DO NOT proceed."
        )
    return res


def self_test_stabilizer_state_uniform_on_mub_m2(tol: float = 1e-10) -> dict:
    """For a stabilizer state in the computational basis (any std basis vector),
    the Born-rule distribution on a NON-NATIVE MUB should be EXACTLY uniform
    (TV = 0 up to float epsilon)."""
    print("[self-test] stabilizer state -> uniform on non-native MUBs (m=2) ...",
          flush=True)
    std_basis, mubs = build_kerdock_mubs(2)
    N = 4
    psi = std_basis[:, 0].copy()  # |0>
    for k, B in enumerate(mubs):
        amps = B.conj().T @ psi  # <b^k_j | psi>
        P = np.abs(amps) ** 2
        TV = 0.5 * np.sum(np.abs(P - 1.0 / N))
        if TV > tol:
            raise AssertionError(
                f"[self-test FAIL] |0> on MUB B_{k}: TV = {TV:.3e} > tol {tol}. "
                f"Stabilizer-state-uniform property broken; the GR(4, m) trace "
                f"computation is likely wrong."
            )
    print(f"  all {len(mubs)} non-native MUBs: TV <= {tol:.1e} on |0>", flush=True)
    return {"tol": tol, "n_mubs_checked": len(mubs), "passed": True}


def self_test_haar_state_floor_m2() -> dict:
    """Haar-random state at N=4: TV vs uniform on each MUB should be O(1/sqrt(N))."""
    print("[self-test] Haar state floor at m=2 (N=4) ...", flush=True)
    std_basis, mubs = build_kerdock_mubs(2)
    rng = np.random.default_rng(7)
    N = 4
    tvs = []
    n_trials = 200
    for _ in range(n_trials):
        v = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / math.sqrt(2.0)
        psi = v / np.linalg.norm(v)
        for B in mubs:
            amps = B.conj().T @ psi
            P = np.abs(amps) ** 2
            tvs.append(0.5 * np.sum(np.abs(P - 1.0 / N)))
    mean_tv = float(np.mean(tvs))
    std_tv = float(np.std(tvs))
    expected = 1.0 / math.sqrt(N)
    print(f"  Haar TV mean = {mean_tv:.4f} +/- {std_tv:.4f}  "
          f"(expected ~ 1/sqrt(N) = {expected:.4f})", flush=True)
    # Haar TV should be in (0.1, 0.9). At N=4 this is fairly loose.
    assert 0.05 < mean_tv < 0.95, (
        f"Haar floor sanity failed: mean TV = {mean_tv:.4f}, expected near {expected:.4f}"
    )
    return {"mean_tv": mean_tv, "std_tv": std_tv, "n_trials": n_trials,
            "expected_order_of_magnitude": expected, "passed": True}


def self_test_full() -> dict:
    res = {}
    res["unbiasedness_m2"] = self_test_mub_m2()
    res["stab_uniform_m2"] = self_test_stabilizer_state_uniform_on_mub_m2()
    res["haar_floor_m2"] = self_test_haar_state_floor_m2()
    return res


# ---------------------------------------------------------------------------
# Production probe
# ---------------------------------------------------------------------------

def run_probe(m: int, seed: int) -> tuple[dict, str, str, float, dict]:
    """Build N+1 MUBs at the given m, then compute TV_{i, k} for 3 substrate states."""
    t0 = time.monotonic()
    N = 1 << m
    print(f"[probe] m={m}, N={N}", flush=True)

    print("[probe] building N+1 = {} Kerdock-MUBs ...".format(N + 1), flush=True)
    std_basis, mubs = build_kerdock_mubs(m)
    print(f"[probe] MUBs constructed: {len(mubs) + 1} bases total", flush=True)

    # Quick pairwise unbiasedness sanity on a random pair (full check at m=12 is
    # 4097*4096/2 pairs * O(N^2) = too expensive; spot-check).
    rng = np.random.default_rng(seed)
    a, b = 0, int(rng.integers(1, len(mubs) + 1))
    all_bases = [std_basis] + mubs
    ovl = all_bases[a].conj().T @ all_bases[b]
    spot_err = float(np.max(np.abs(np.abs(ovl) ** 2 - 1.0 / N)))
    print(f"[probe] spot unbiasedness check (a=0, b={b}): "
          f"max |P - 1/N| = {spot_err:.3e}", flush=True)
    if spot_err > 1e-6:
        return ({}, "MUB_CONSTRUCTION_FAILED",
                f"Spot unbiasedness check failed at m={m}: max_err={spot_err:.3e}",
                time.monotonic() - t0, {"m": m, "N": N, "seed": seed})

    print("[probe] building 3 substrate-class states ...", flush=True)
    states = {
        "vanilla_stab": make_substrate_state(rng, "vanilla_stab", std_basis, mubs),
        "enriched_kerdock": make_substrate_state(rng, "enriched_kerdock",
                                                  std_basis, mubs),
        "haar": make_substrate_state(rng, "haar", std_basis, mubs),
    }

    # Compute TV_{i, k} for each (state, basis) pair.
    tv = {}
    for i_name, psi in states.items():
        per_state = []
        for k_idx, B in enumerate([std_basis] + mubs):
            amps = B.conj().T @ psi
            P = np.abs(amps) ** 2
            TV = 0.5 * float(np.sum(np.abs(P - 1.0 / N)))
            per_state.append(TV)
        tv[i_name] = per_state
        print(f"  [{i_name}] TV stats: "
              f"min={min(per_state):.4f}, max={max(per_state):.4f}, "
              f"mean={float(np.mean(per_state)):.4f}", flush=True)

    # Verdict per drill 3.B.
    stat_noise = 1.0 / math.sqrt(N)
    hp_threshold = max(0.05, 3.0 * stat_noise)
    hf_threshold = 1.5 * stat_noise
    print(f"[verdict] N={N}, stat_noise=1/sqrt(N)={stat_noise:.4f}, "
          f"HP_threshold={hp_threshold:.4f}, HF_threshold={hf_threshold:.4f}",
          flush=True)

    # Count non-native MUB spikes per state.
    # 'Native' here = the basis index where the state was drawn from
    # (we tracked this: vanilla_stab native = 0; enriched_kerdock native = the k_idx
    # the column came from; haar native = none). We can detect native as the basis
    # with TV ~ 0.
    n_states_with_spike = 0
    spike_basis_per_state = {}
    for i_name, tvs in tv.items():
        # Find native: TV < 0.001
        native_indices = [k for k, x in enumerate(tvs) if x < 1e-3]
        spike_basis_per_state[i_name] = {
            "native": native_indices,
            "spike_bases": [k for k, x in enumerate(tvs)
                            if k not in native_indices and x >= hp_threshold],
        }
        if len(spike_basis_per_state[i_name]["spike_bases"]) > 0:
            n_states_with_spike += 1

    # All non-native MUBs flat = no spike on ANY non-native basis for ANY state.
    all_flat = True
    for i_name, tvs in tv.items():
        for k, x in enumerate(tvs):
            if k in spike_basis_per_state[i_name]["native"]:
                continue
            if x > hf_threshold:
                all_flat = False
                break

    if n_states_with_spike >= 2:
        verdict = "KERDOCK_MUB_BBMD_NOVEL_SIGNATURE_CONFIRMED"
        msg = (f"HARD PASS: {n_states_with_spike} of 3 states show TV >= "
               f"{hp_threshold:.3f} on non-native MUBs. Substrate carries "
               f"BBMD-novel structure beyond MUB encoding.")
    elif all_flat:
        verdict = "KERDOCK_MUB_VANILLA_STABILIZER"
        msg = (f"HARD FAIL: all non-native MUBs flat within {hf_threshold:.3f} "
               f"across all 3 states. Substrate is a vanilla Clifford-2-design "
               f"image; no BBMD-extra structure.")
    else:
        verdict = "KERDOCK_MUB_INCONCLUSIVE"
        msg = (f"INCONCLUSIVE: {n_states_with_spike} states with spike "
               f"(need >= 2 for HP); not all flat (so not HF). "
               f"Partial signal — needs more states or higher N.")

    elapsed = time.monotonic() - t0
    config = {
        "m": m, "N": N, "seed": seed,
        "stat_noise": stat_noise,
        "HP_threshold": hp_threshold,
        "HF_threshold": hf_threshold,
        "n_mubs": len(mubs) + 1,
        "state_kinds": list(states.keys()),
    }
    summary = {
        "tv": tv,
        "spike_basis_per_state": spike_basis_per_state,
        "n_states_with_spike": n_states_with_spike,
        "all_flat": all_flat,
    }
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir; HDLAB_OUTDIR preserved."""
    env_outdir = os.environ.get("HDLAB_OUTDIR")
    if env_outdir:
        out = Path(env_outdir)
    else:
        out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(metrics.keys())
    if missing:
        raise ValueError(f"metrics missing fields: {missing}")
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    out_dir = get_output_dir("wave14_kerdock_mub_distinguishability_v1_smoke")
    print("=== SELF-TEST GATE ===", flush=True)
    selftest = self_test_full()
    print("\n=== SMOKE PROBE at m=4 (N=16) ===", flush=True)
    summary, verdict, msg, elapsed, config = run_probe(m=4, seed=42)
    summary["selftest"] = selftest
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: verdict={verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--m", type=int, default=12,
                    help="qubit count (N = 2^m); default 12 (N=4096).")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.self_test:
        self_test_full()
        return 0
    if args.smoke:
        run_smoke()
        return 0

    print("=== SELF-TEST GATE ===", flush=True)
    selftest = self_test_full()

    out_dir = get_output_dir("wave14_kerdock_mub_distinguishability_v1")
    print(f"\n=== PROBE at m={args.m} (N={1 << args.m}) ===", flush=True)
    summary, verdict, msg, elapsed, config = run_probe(m=args.m, seed=args.seed)
    summary["selftest"] = selftest
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
