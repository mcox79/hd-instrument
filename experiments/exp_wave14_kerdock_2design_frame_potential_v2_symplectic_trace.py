"""Wave 14 — Kerdock 2-design frame-potential probe v2 (symplectic-rank trace formula).

Question
--------
Same as v1 (is the substrate's Kerdock subgroup a unitary 2-design, F_4 = 2,
or a 3-design, F_4 = 3?) but uses the Bravyi-Maslov 2020 / Hostens-Dehaene-
De Moor 2005 closed-form trace formula:

    |Tr(U_S)|^2 = d / 2^{rank_{F_2}(S - I)}   (when the lift exists; else 0)

For PSL(2, F_{2^m}) elements (the Kerdock-anchor sampler), the lift always
exists by the CCKS 1997 construction, so the existence indicator is trivially 1.

Therefore:

    F_4 = E_{S ~ uniform PSL(2, F_{2^m})} [ (d / 2^{rank(S - I)})^2 ]
        = E [ d^2 / 2^{2 * rank(S - I)} ]

This sidesteps the dense d x d Clifford unitary construction entirely — only
the symplectic block matrix S and the F_2 rank of (S - I) matter.

v1 -> v2 diff
-------------
- DROPS the dense unitary lift (Aaronson-Gottesman H/S/CNOT decomposition).
- DROPS the {H_all, diag(q_b)} random-word sampler (pathological).
- KEEPS the PSL(2, F_{2^m}) symplectic-block construction (M_a, M_b, M_c, M_d
  blocks over F_2) — this was correct in v1.
- KEEPS the trace-self-dual basis conjugation C = diag(I, T^{-1}).
- KEEPS the Haar baseline path (Mezzadri QR) as the smoke gate.
- ADDS an F_2 Gaussian-elimination rank routine.
- ADDS a d=8 (m=3, |PSL(2, F_8)| = 504) exact-enumeration self-test.

The d=8 self-test is MANDATORY before the d=4096 production estimator runs;
it catches rank-routine bugs that would silently produce wrong F_4 numbers.

Hard pass / hard fail (unchanged from drill / v1 prereg)
--------------------------------------------------------
- HARD PASS: F_4 within +/-5% of 2.0 (Haar)  OR  +/-5% of 3.0 (Clifford full).
- HARD FAIL: F_4 outside BOTH bands.

Refs
----
- Bravyi & Maslov, "Hadamard-free circuits expose the structure of the
  Clifford group", Phys. Rev. A 102, 022406 (2020) — Lemma 3 / Prop. 7.
- Hostens, Dehaene, De Moor, "Stabilizer states and Clifford operations for
  systems of arbitrary dimensions", Phys. Rev. A 71, 042315 (2005) — sec. 4-5.
- Calderbank, Cameron, Kantor, Seidel, "Z_4-Kerdock codes, orthogonal spreads,
  and extremal Euclidean line-sets", Proc. London Math. Soc. 75 (1997).
- Klappenecker, Roetteler, "Mutually unbiased bases are complex projective
  2-designs", ISIT 2005.

Pre-reg: preregs/2026-05-23_wave14_kerdock_2design_frame_potential_v2_symplectic_trace.md
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import itertools
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
# GF(2^m) arithmetic
# ---------------------------------------------------------------------------

PRIMITIVE_POLY = {
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


def gf2m_tables(m: int) -> tuple[np.ndarray, np.ndarray]:
    if m not in PRIMITIVE_POLY:
        raise ValueError(f"no primitive polynomial registered for GF(2^{m})")
    poly = PRIMITIVE_POLY[m]
    q = 1 << m
    period = q - 1
    antilog = np.zeros(period, dtype=np.int64)
    log_tab = -np.ones(q, dtype=np.int64)
    val = 1
    for i in range(period):
        antilog[i] = val
        log_tab[val] = i
        val <<= 1
        if val & q:
            val ^= poly
        val &= q - 1
    return log_tab, antilog


def gf_mul(a: int, b: int, log_tab: np.ndarray, antilog_tab: np.ndarray) -> int:
    if a == 0 or b == 0:
        return 0
    period = len(antilog_tab)
    return int(antilog_tab[(log_tab[a] + log_tab[b]) % period])


def gf_inv(a: int, log_tab: np.ndarray, antilog_tab: np.ndarray) -> int:
    if a == 0:
        raise ValueError("zero has no inverse in GF(2^m)")
    period = len(antilog_tab)
    return int(antilog_tab[(-log_tab[a]) % period])


# ---------------------------------------------------------------------------
# F_2 arithmetic on packed-bit matrices (uint8 entries in {0, 1})
# ---------------------------------------------------------------------------

def f2_rank(M: np.ndarray) -> int:
    """Rank over F_2 of a {0,1} matrix via Gaussian elimination.

    Operates on a copy in-place. Returns the integer rank.
    """
    A = M.copy().astype(np.uint8) & 1
    rows, cols = A.shape
    rank = 0
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        # Find pivot in column c at or below row r.
        pivot = -1
        for rr in range(r, rows):
            if A[rr, c] == 1:
                pivot = rr
                break
        if pivot == -1:
            continue
        if pivot != r:
            tmp = A[r].copy()
            A[r] = A[pivot]
            A[pivot] = tmp
        # Eliminate all OTHER rows with a 1 in column c.
        for rr in range(rows):
            if rr != r and A[rr, c] == 1:
                A[rr] ^= A[r]
        rank += 1
        r += 1
    return rank


def f2_rank_self_test() -> None:
    # Identity has full rank.
    I = np.eye(5, dtype=np.uint8)
    assert f2_rank(I) == 5, "f2_rank(I_5) should be 5"

    # Zero matrix has rank 0.
    Z = np.zeros((5, 5), dtype=np.uint8)
    assert f2_rank(Z) == 0, "f2_rank(0_5x5) should be 0"

    # Known rank: a 3x3 with one duplicated row -> rank 2.
    A = np.array([[1, 1, 0], [1, 1, 0], [0, 1, 1]], dtype=np.uint8)
    assert f2_rank(A) == 2, f"f2_rank for duplicate-row 3x3 should be 2, got {f2_rank(A)}"

    # A full-rank 4x4 over F_2 (verified by hand: det != 0 in F_2 means rank=4).
    # Use the identity itself with one row-add to keep it non-trivial but
    # provably full-rank.
    B = np.array([[1, 0, 0, 0],
                  [1, 1, 0, 0],
                  [0, 1, 1, 0],
                  [0, 0, 1, 1]], dtype=np.uint8)  # lower-triangular w/ unit diag
    assert f2_rank(B) == 4, f"f2_rank(B) should be 4, got {f2_rank(B)}"

    # A 4x4 with rank 3 (last row = sum of first three over F_2).
    C = np.array([[1, 0, 0, 1],
                  [0, 1, 0, 1],
                  [0, 0, 1, 1],
                  [1, 1, 1, 1]], dtype=np.uint8)
    assert f2_rank(C) == 3, f"f2_rank(C) should be 3, got {f2_rank(C)}"

    # Non-square (rectangular) consistency.
    D = np.array([[1, 0, 1], [0, 1, 1]], dtype=np.uint8)
    assert f2_rank(D) == 2, "f2_rank for 2x3 should be 2"


# ---------------------------------------------------------------------------
# PSL(2, F_{2^m}) -> Sp(2m, F_2) symplectic embedding (KEPT FROM V1)
# ---------------------------------------------------------------------------
# An element g = [[a, b], [c, d]] in PSL(2, F_{2^m}) acts on F_{2^m}^2.
# Identifying F_{2^m} ~= F_2^m via the polynomial basis, each F_{2^m}
# scalar multiplication "mul by x" becomes an m x m F_2 matrix M_x (the
# regular representation). The action g lifts to a 2m x 2m block matrix
#   S_g = [[M_a, M_b], [M_c, M_d]]   over F_2.
# This S_g is symplectic w.r.t. the trace-pairing form
#   J_T = [[0, T], [T, 0]]
# where T is the F_2 matrix of the trace bilinear form on F_{2^m}.
# To get the standard form J = [[0, I], [I, 0]], conjugate by
# C = diag(I, T^{-1})^T  (i.e. transform basis on the second component).
# After conjugation, S_g lives in the standard symplectic group Sp(2m, F_2).
#
# Reference: Calderbank-Cameron-Kantor-Seidel 1997, Lemma 5.1.

def mat_mul_in_basis(x: int, m: int,
                     log_tab: np.ndarray, antilog_tab: np.ndarray) -> np.ndarray:
    """Regular representation matrix of 'multiplication by x' in F_{2^m}
    over the polynomial basis {1, alpha, ..., alpha^{m-1}}.
    """
    M = np.zeros((m, m), dtype=np.uint8)
    for k in range(m):
        # Image of basis vector alpha^k = (1 << k).
        y = gf_mul(x, 1 << k, log_tab, antilog_tab)
        # Encode y as a column of M.
        for i in range(m):
            M[i, k] = (y >> i) & 1
    return M


def trace_form_matrix(m: int,
                      log_tab: np.ndarray, antilog_tab: np.ndarray) -> np.ndarray:
    """Matrix T of the bilinear form (x, y) -> Tr_{F_{2^m}/F_2}(x * y) on F_2^m.

    T[i, j] = Tr_{F_{2^m}/F_2}(alpha^i * alpha^j) = Tr(alpha^{i+j}).
    """
    q = 1 << m
    T = np.zeros((m, m), dtype=np.uint8)
    # Precompute Tr_{F_{2^m}/F_2} for each element.
    # Tr(x) = x + x^2 + x^4 + ... + x^{2^{m-1}}, computed mod F_2.
    tr = np.zeros(q, dtype=np.uint8)
    for x in range(q):
        s = 0
        v = x
        for _ in range(m):
            # Reduce s by XOR (we accumulate over F_2).
            s ^= v
            # square v in F_{2^m}.
            v = gf_mul(v, v, log_tab, antilog_tab)
        tr[x] = s & 1
    for i in range(m):
        ai = 1 << i  # alpha^i
        for j in range(m):
            aj = 1 << j
            ij = gf_mul(ai, aj, log_tab, antilog_tab)
            T[i, j] = tr[ij]
    return T


def f2_matrix_inverse(M: np.ndarray) -> np.ndarray:
    """Inverse over F_2 of a square invertible {0,1} matrix via Gauss-Jordan."""
    A = M.copy().astype(np.uint8) & 1
    n = A.shape[0]
    if A.shape[1] != n:
        raise ValueError("f2_matrix_inverse requires square input")
    Aug = np.hstack([A, np.eye(n, dtype=np.uint8)])
    for c in range(n):
        # Find pivot at or below row c.
        pivot = -1
        for r in range(c, n):
            if Aug[r, c] == 1:
                pivot = r
                break
        if pivot == -1:
            raise ValueError("matrix not invertible over F_2")
        if pivot != c:
            tmp = Aug[c].copy()
            Aug[c] = Aug[pivot]
            Aug[pivot] = tmp
        for r in range(n):
            if r != c and Aug[r, c] == 1:
                Aug[r] ^= Aug[c]
    return Aug[:, n:].astype(np.uint8) & 1


def build_psl2_element(a: int, b: int, c: int, d: int, m: int,
                       log_tab: np.ndarray, antilog_tab: np.ndarray,
                       T_inv: np.ndarray) -> np.ndarray:
    """Build the symplectic 2m x 2m F_2 matrix S corresponding to
    g = [[a, b], [c, d]] in PSL(2, F_{2^m}), in STANDARD symplectic form.

    Returns a (2m, 2m) uint8 matrix in {0, 1}.
    """
    Ma = mat_mul_in_basis(a, m, log_tab, antilog_tab)
    Mb = mat_mul_in_basis(b, m, log_tab, antilog_tab)
    Mc = mat_mul_in_basis(c, m, log_tab, antilog_tab)
    Md = mat_mul_in_basis(d, m, log_tab, antilog_tab)
    # Block matrix [[Ma, Mb], [Mc, Md]] is symplectic w.r.t. J_T.
    S_T = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    S_T[:m, :m] = Ma
    S_T[:m, m:] = Mb
    S_T[m:, :m] = Mc
    S_T[m:, m:] = Md
    # Conjugate to standard form: S = C @ S_T @ C^{-1}, C = diag(I, T^{-1}).
    # Working over F_2: matmul + mod 2.
    C_block_lo_right = T_inv
    C = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    C[:m, :m] = np.eye(m, dtype=np.uint8)
    C[m:, m:] = C_block_lo_right
    C_inv = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    C_inv[:m, :m] = np.eye(m, dtype=np.uint8)
    # T_inv inverse over F_2 == T (since T is involutive on its own column-space?
    # No — in general we need to invert T_inv to get T. We pre-build both.)
    raise NotImplementedError  # Replaced below: we just multiply at call site.


def build_psl2_S(a: int, b: int, c: int, d: int, m: int,
                 log_tab: np.ndarray, antilog_tab: np.ndarray,
                 C: np.ndarray, C_inv: np.ndarray) -> np.ndarray:
    """Build S = C @ S_T @ C_inv  (mod 2)  for g = [[a,b],[c,d]] in PSL(2, F_{2^m}).

    C and C_inv are precomputed once outside the loop.
    """
    Ma = mat_mul_in_basis(a, m, log_tab, antilog_tab)
    Mb = mat_mul_in_basis(b, m, log_tab, antilog_tab)
    Mc = mat_mul_in_basis(c, m, log_tab, antilog_tab)
    Md = mat_mul_in_basis(d, m, log_tab, antilog_tab)
    S_T = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    S_T[:m, :m] = Ma
    S_T[:m, m:] = Mb
    S_T[m:, :m] = Mc
    S_T[m:, m:] = Md
    # Conjugate: S = C @ S_T @ C_inv (mod 2).
    tmp = (C.astype(np.int64) @ S_T.astype(np.int64)) & 1
    S = (tmp @ C_inv.astype(np.int64)) & 1
    return S.astype(np.uint8)


def build_conjugation_matrices(m: int,
                               log_tab: np.ndarray,
                               antilog_tab: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (C, C_inv) where C = diag(I, T^{-1}) and C_inv = diag(I, T)
    in the (2m, 2m) F_2 setting.

    NOTE: this construction conjugates S_T (which is symplectic w.r.t. J_T)
    INTO standard symplectic form (w.r.t. J = [[0, I], [I, 0]]). The exact
    choice between T or T^{-1} in which block doesn't change F_4 (rank of
    S - I is preserved under any symplectic conjugation), but we keep the
    documented v1 convention.
    """
    T = trace_form_matrix(m, log_tab, antilog_tab)
    T_inv = f2_matrix_inverse(T)
    C = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    C[:m, :m] = np.eye(m, dtype=np.uint8)
    C[m:, m:] = T_inv
    C_inv = np.zeros((2 * m, 2 * m), dtype=np.uint8)
    C_inv[:m, :m] = np.eye(m, dtype=np.uint8)
    C_inv[m:, m:] = T
    return C, C_inv


# ---------------------------------------------------------------------------
# F_4 estimator via the symplectic-rank trace formula
# ---------------------------------------------------------------------------

def f4_contribution(rank_S_minus_I: int, d: int) -> float:
    """Per-sample contribution to E[|Tr(U_S)|^4] under the Bravyi-Maslov formula.

      |Tr(U_S)|^2 = d / 2^{rank(S - I)}
      |Tr(U_S)|^4 = d^2 / 2^{2 * rank(S - I)}
    """
    return (float(d) ** 2) / float(1 << (2 * rank_S_minus_I))


def sample_psl2_element(rng: np.random.Generator, m: int,
                        log_tab: np.ndarray, antilog_tab: np.ndarray
                        ) -> tuple[int, int, int, int]:
    """Sample a uniform PSL(2, F_{2^m}) element.

    PSL(2, q) for q=2^m has order q*(q^2 - 1) (== SL(2, q) since char-2
    eliminates the +/-1 quotient). Sampling: pick first row (a, b) != (0, 0);
    pick c uniformly; then d is determined by det == 1: a*d - b*c = 1, i.e.
    d = (1 + b*c) / a  if a != 0, else d is free given b != 0 (constrained
    by det = -b*c, so any c with b*c = 1, i.e. c = b^{-1}).

    Returns (a, b, c, d) with ad - bc = 1 in F_{2^m}.
    """
    q = 1 << m
    while True:
        a = int(rng.integers(0, q))
        b = int(rng.integers(0, q))
        if a == 0 and b == 0:
            continue
        break
    if a != 0:
        c = int(rng.integers(0, q))
        # d = (1 XOR b*c) / a  (in char 2, "+ 1" is "XOR 1"; subtraction = addition)
        bc = gf_mul(b, c, log_tab, antilog_tab)
        d = gf_mul(1 ^ bc, gf_inv(a, log_tab, antilog_tab),
                   log_tab, antilog_tab)
    else:
        # a == 0 means b != 0; then ad - bc = -bc = bc (char 2) = 1, so c = b^{-1}.
        c = gf_inv(b, log_tab, antilog_tab)
        d = int(rng.integers(0, q))
    return a, b, c, d


def enumerate_psl2(m: int,
                   log_tab: np.ndarray, antilog_tab: np.ndarray
                   ) -> list[tuple[int, int, int, int]]:
    """Enumerate ALL elements of PSL(2, F_{2^m}) (== SL(2, F_{2^m}) in char 2).

    Used by the d=8 (m=3, |PSL(2, F_8)| = 504) self-test.
    """
    q = 1 << m
    elements = []
    for a in range(q):
        for b in range(q):
            for c in range(q):
                # d determined by ad - bc = 1; in char 2: ad + bc = 1.
                # Hence ad = 1 + bc, so:
                # - if a == 0: need bc = 1 (else no d exists). Then any d.
                # - if a != 0: d = (1 + bc) / a, unique.
                bc = gf_mul(b, c, log_tab, antilog_tab)
                rhs = 1 ^ bc
                if a == 0:
                    if rhs == 0:
                        for d in range(q):
                            elements.append((a, b, c, d))
                    # else: no solution
                else:
                    d = gf_mul(rhs, gf_inv(a, log_tab, antilog_tab),
                               log_tab, antilog_tab)
                    elements.append((a, b, c, d))
    return elements


def f4_closed_form_psl2_2m(m: int) -> float:
    """Closed-form (rational) F_4 for PSL(2, F_{2^m}) via the rank formula.

    We compute it by enumerating ALL elements and applying the rank formula.
    This is the GROUND TRUTH the d=8 self-test compares to. The 'closed form'
    in the spec is just the exact value resulting from full enumeration —
    no sampling noise.

    Returns F_4 = (1 / |G|) * sum_{S in G} d^2 / 2^{2 * rank(S - I)}.
    """
    q = 1 << m
    d = q
    log_tab, antilog_tab = gf2m_tables(m)
    C, C_inv = build_conjugation_matrices(m, log_tab, antilog_tab)
    elements = enumerate_psl2(m, log_tab, antilog_tab)
    total = 0.0
    I2m = np.eye(2 * m, dtype=np.uint8)
    for (a, b, c, dval) in elements:
        S = build_psl2_S(a, b, c, dval, m, log_tab, antilog_tab, C, C_inv)
        SmI = (S ^ I2m) & 1  # S - I over F_2 == S XOR I
        r = f2_rank(SmI)
        total += f4_contribution(r, d)
    return total / len(elements)


# ---------------------------------------------------------------------------
# Haar baseline (Mezzadri 2007) — kept from v1 as the smoke gate
# ---------------------------------------------------------------------------

def sample_haar_unitary(rng: np.random.Generator, d: int) -> np.ndarray:
    Z = (rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))) / math.sqrt(2)
    Q, R = np.linalg.qr(Z)
    diag_R = np.diag(R)
    Lambda = diag_R / np.abs(diag_R)
    return Q * Lambda


def haar_f4_sample(rng: np.random.Generator, d: int, n_samples: int) -> tuple[float, float]:
    abs4 = np.empty(n_samples, dtype=np.float64)
    for i in range(n_samples):
        U = sample_haar_unitary(rng, d)
        tr = np.trace(U)
        abs4[i] = float(np.abs(tr) ** 4)
    F = float(abs4.mean())
    se = float(abs4.std(ddof=1) / math.sqrt(n_samples))
    return F, se


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test_d8_exact() -> tuple[float, dict]:
    """d=8 (m=3, |PSL(2, F_8)| = 504) exact enumeration. THE STRUCTURAL GATE.

    Returns the exact F_4 and a diagnostic dict.
    """
    m = 3
    d = 1 << m
    log_tab, antilog_tab = gf2m_tables(m)
    C, C_inv = build_conjugation_matrices(m, log_tab, antilog_tab)
    elements = enumerate_psl2(m, log_tab, antilog_tab)
    assert len(elements) == 504, f"|PSL(2, F_8)| should be 504, got {len(elements)}"
    print(f"[self-test] enumerated all {len(elements)} elements of PSL(2, F_8)", flush=True)

    rank_histogram = {}
    total = 0.0
    I2m = np.eye(2 * m, dtype=np.uint8)
    for (a, b, c, dval) in elements:
        S = build_psl2_S(a, b, c, dval, m, log_tab, antilog_tab, C, C_inv)
        SmI = (S ^ I2m) & 1
        r = f2_rank(SmI)
        rank_histogram[r] = rank_histogram.get(r, 0) + 1
        total += f4_contribution(r, d)
    F_4 = total / len(elements)
    diag = {
        "n_elements": len(elements),
        "d": d,
        "rank_histogram": rank_histogram,
        "F_4_d8_exact": F_4,
    }
    print(f"[self-test] d=8 F_4 (exact, 504 elements) = {F_4:.6f}", flush=True)
    print(f"[self-test] rank(S - I) histogram: {sorted(rank_histogram.items())}",
          flush=True)
    return F_4, diag


def self_test_full() -> dict:
    """Composite self-test. MUST run before any production estimator."""
    print("[self-test] f2_rank routine ...", flush=True)
    f2_rank_self_test()
    print("[self-test] f2_rank: OK", flush=True)

    print("[self-test] trace-form matrix invertible at m=3 and m=4 ...", flush=True)
    for m in (3, 4):
        log_tab, antilog_tab = gf2m_tables(m)
        T = trace_form_matrix(m, log_tab, antilog_tab)
        T_inv = f2_matrix_inverse(T)
        I_check = (T_inv.astype(np.int64) @ T.astype(np.int64)) & 1
        assert np.array_equal(I_check, np.eye(m, dtype=np.uint8)), (
            f"T * T^{-1} != I at m={m}: {I_check}"
        )
    print("[self-test] trace-form: OK", flush=True)

    print("[self-test] d=8 exact enumeration ...", flush=True)
    F_4_d8_exact, diag = self_test_d8_exact()

    # SANITY: the d=8 value must be RATIONAL and in a reasonable range.
    # For PSL(2, F_8) we don't have a published closed form (the formula is
    # ours, the closed-form value is the exact average of d^2 / 4^rank over
    # all 504 elements). What we CAN verify is:
    #   - F_4 is in [1, 8^2] = [1, 64] (trivially) and we expect it in [1.5, 4].
    #   - identity element contributes d^2 / 4^0 = 64 (rank(I - I) = 0).
    #   - non-identity elements have rank >= 1, contributing d^2 / 4^rank <= 16.
    #   - the rank histogram is a stable fingerprint we log for cross-checking.
    assert F_4_d8_exact >= 1.0, f"d=8 F_4 = {F_4_d8_exact} below sanity floor"
    assert F_4_d8_exact <= 64.0, f"d=8 F_4 = {F_4_d8_exact} above sanity ceiling"

    # GATE: the d=8 value should be in the [2, 3] +/- some-slack window if
    # the PSL(2, F_8) Clifford lift IS a 2-design (the central hypothesis).
    # For the d=8 SELF-TEST, we use a wider band to detect implementation
    # bugs that produce O(10) or O(100) values (v1's failure mode).
    # If d=8 lands outside [1.5, 4.5], the implementation is buggy and we STOP.
    if F_4_d8_exact < 1.5 or F_4_d8_exact > 4.5:
        raise AssertionError(
            f"[self-test FAIL] d=8 F_4 = {F_4_d8_exact:.4f} outside sanity band [1.5, 4.5]. "
            f"Rank routine likely buggy. Rank histogram: "
            f"{sorted(diag['rank_histogram'].items())}. "
            f"DO NOT proceed to d=4096 production run."
        )

    # Haar baseline sanity at d=16: should be ~2.0 +/- 0.3.
    print("[self-test] Haar baseline at d=16 ...", flush=True)
    rng = np.random.default_rng(42)
    F_haar, se_haar = haar_f4_sample(rng, 16, 1000)
    print(f"[self-test] d=16 Haar F_4 = {F_haar:.4f} +/- {se_haar:.4f} (n=1000)",
          flush=True)
    assert abs(F_haar - 2.0) < 0.3, f"Haar baseline broken: F_4 = {F_haar}"

    return {
        "F_4_d8_exact": F_4_d8_exact,
        "rank_histogram_d8": diag["rank_histogram"],
        "F_4_haar_d16_n1000": F_haar,
        "F_4_haar_d16_se": se_haar,
    }


# ---------------------------------------------------------------------------
# Production estimator
# ---------------------------------------------------------------------------

def estimate_f4_psl2(m: int, n_samples: int, rng: np.random.Generator
                     ) -> tuple[float, float, dict]:
    """Monte Carlo F_4 estimator for PSL(2, F_{2^m})."""
    d = 1 << m
    log_tab, antilog_tab = gf2m_tables(m)
    C, C_inv = build_conjugation_matrices(m, log_tab, antilog_tab)
    I2m = np.eye(2 * m, dtype=np.uint8)

    contribs = np.empty(n_samples, dtype=np.float64)
    rank_histogram = {}
    t_last = time.monotonic()
    for i in range(n_samples):
        a, b, c, dval = sample_psl2_element(rng, m, log_tab, antilog_tab)
        S = build_psl2_S(a, b, c, dval, m, log_tab, antilog_tab, C, C_inv)
        SmI = (S ^ I2m) & 1
        r = f2_rank(SmI)
        rank_histogram[r] = rank_histogram.get(r, 0) + 1
        contribs[i] = f4_contribution(r, d)
        if (i + 1) % max(1, n_samples // 10) == 0:
            now = time.monotonic()
            running = float(contribs[:i + 1].mean())
            print(f"  [{i + 1}/{n_samples}] running F_4 = {running:.5f} "
                  f"(+{now - t_last:.1f}s)", flush=True)
            t_last = now

    F = float(contribs.mean())
    se = float(contribs.std(ddof=1) / math.sqrt(n_samples))
    diag = {
        "rank_histogram": rank_histogram,
        "min_contrib": float(contribs.min()),
        "max_contrib": float(contribs.max()),
        "median_contrib": float(np.median(contribs)),
    }
    return F, se, diag


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(F_kerd: float, F_kerd_se: float,
                    F_haar: float) -> tuple[str, str]:
    haar_band = (1.90, 2.10)
    cliff_band = (2.85, 3.15)

    haar_sanity_ok = abs(F_haar - 2.0) < 0.30
    if not haar_sanity_ok:
        return (
            "KERDOCK_2DESIGN_INCONCLUSIVE",
            f"Sampling-sanity FAIL: empirical Haar F_4={F_haar:.4f} far from 2.0. "
            f"Cannot trust comparison. Kerdock-PSL F_4={F_kerd:.4f} +/- {F_kerd_se:.4f}."
        )

    in_haar = haar_band[0] <= F_kerd <= haar_band[1]
    in_cliff = cliff_band[0] <= F_kerd <= cliff_band[1]

    if in_haar:
        return (
            "KERDOCK_2DESIGN_MATCH_HAAR",
            f"HARD PASS: PSL(2, F_2^m) F_4={F_kerd:.4f} +/- {F_kerd_se:.4f} within "
            f"+/-5% of Haar 2.0. Substrate's Kerdock anchor IS a unitary 2-design. "
            f"Haar ref F_4={F_haar:.4f}."
        )
    if in_cliff:
        return (
            "KERDOCK_3DESIGN_MATCH_CLIFFORD",
            f"HARD PASS: PSL(2, F_2^m) F_4={F_kerd:.4f} +/- {F_kerd_se:.4f} within "
            f"+/-5% of Clifford 3.0. Substrate's Kerdock anchor inherits "
            f"Clifford 4-defect. Haar ref F_4={F_haar:.4f}."
        )
    return (
        "KERDOCK_ISOMORPHISM_BROKEN",
        f"HARD FAIL: PSL(2, F_2^m) F_4={F_kerd:.4f} +/- {F_kerd_se:.4f} outside "
        f"BOTH Haar band {haar_band} AND Clifford band {cliff_band}. "
        f"Either (a) the symplectic-block construction is off-canonical "
        f"(Gray-map orientation bug), or (b) rank-routine bug not caught by d=8 "
        f"self-test. Haar ref F_4={F_haar:.4f}."
    )


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


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------

def run_experiment(m: int, n_samples: int, seed: int,
                   smoke: bool = False) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        m = 4
        n_samples = 500
        seed = 42

    d = 1 << m
    rng = np.random.default_rng(seed)

    # 1) Self-test gate.
    print("\n=== SELF-TEST GATE ===", flush=True)
    selftest = self_test_full()

    # 2) Production-style estimator for PSL(2, F_{2^m}).
    print(f"\n=== F_4 ESTIMATOR: PSL(2, F_2^{m}) at d={d}, n={n_samples} ===", flush=True)
    F_kerd, se_kerd, diag_kerd = estimate_f4_psl2(m, n_samples, rng)
    print(f"\n[F_4 PSL(2, F_2^{m})] = {F_kerd:.5f} +/- {se_kerd:.5f}", flush=True)
    print(f"  rank histogram: {sorted(diag_kerd['rank_histogram'].items())}",
          flush=True)

    # 3) Haar baseline at the SAME d for direct comparison.
    print(f"\n=== HAAR BASELINE at d={d}, n={n_samples // 4} ===", flush=True)
    n_haar = max(200, n_samples // 4)
    F_haar, se_haar = haar_f4_sample(rng, d, n_haar)
    print(f"[F_4 Haar d={d}] = {F_haar:.5f} +/- {se_haar:.5f} (n={n_haar})", flush=True)

    config = {
        "m": m, "d": d, "n_samples": n_samples, "seed": seed, "smoke": smoke,
        "n_haar": n_haar,
        "haar_band": [1.90, 2.10],
        "cliff_band": [2.85, 3.15],
    }
    summary = {
        "F_4_psl2": F_kerd,
        "F_4_psl2_se": se_kerd,
        "F_4_haar": F_haar,
        "F_4_haar_se": se_haar,
        "rank_histogram_psl2": diag_kerd["rank_histogram"],
        "selftest": selftest,
    }
    verdict, msg = compute_verdict(F_kerd, se_kerd, F_haar)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def run_smoke() -> None:
    out_dir = get_output_dir("wave14_kerdock_2design_frame_potential_v2_symplectic_trace_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(m=4, n_samples=500, seed=42, smoke=True)
    assert "F_4_psl2" in summary
    assert abs(summary["F_4_haar"] - 2.0) < 0.5, (
        f"smoke FAIL: Haar F_4 = {summary['F_4_haar']:.3f} too far from 2.0"
    )
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: verdict={verdict}; "
          f"F_4 PSL(2,F_16)={summary['F_4_psl2']:.3f} "
          f"Haar d=16={summary['F_4_haar']:.3f}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="Run self-tests only (d=8 exact + Haar baseline at d=16).")
    ap.add_argument("--smoke", action="store_true",
                    help="Run a small smoke at m=4 (d=16, n=500).")
    ap.add_argument("--m", type=int, default=12,
                    help="qubit count (d = 2^m); default 12 (d=4096).")
    ap.add_argument("--n-samples", type=int, default=2000,
                    help="PSL(2, F_2^m) samples; default 2000.")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.self_test:
        self_test_full()
        return 0
    if args.smoke:
        run_smoke()
        return 0

    out_dir = get_output_dir("wave14_kerdock_2design_frame_potential_v2_symplectic_trace")
    summary, verdict, msg, elapsed, config = run_experiment(
        m=args.m, n_samples=args.n_samples, seed=args.seed, smoke=False
    )
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
