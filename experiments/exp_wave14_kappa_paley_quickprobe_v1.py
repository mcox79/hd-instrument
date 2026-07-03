"""Quick scoping probe: kappa_n profile on a Paley Type-I Hadamard codebook.

Motivation
----------
Anchor 2 (wave14_kappa_profile_cross_codebook_v1) tests 5 codebooks
{iid_gauss, srht, hadamard, rm_1_m, kerdock} for BBMD-distance ordering.
A natural follow-up question is whether ANOTHER algebraic family --
Paley conference / Paley-Hadamard matrices, built from quadratic residues
mod a prime -- also produces a non-MP kappa_n profile.

If Paley shows non-trivial |delta_n| comparable to Kerdock, it widens
the BBMD-regime hypothesis: the divergence is not Kerdock-specific but a
property of structured-Hadamard algebraic codebooks generally. If Paley
sits near MP (like iid_gauss), then Kerdock's 4-coset combinatorics
specifically drives the deviation.

This is a SCOPING PROBE (single config, single seed, N~1024, n_max=6)
designed to decide whether Paley belongs in a future expanded codebook
battery -- NOT a verdict-ship experiment.

Construction
------------
Paley Type-I Hadamard at prime p with p ~= 3 (mod 4):
  Q[i,j] = chi(i - j) where chi is the Legendre symbol mod p
           (chi(0)=0, chi(QR)=+1, chi(NQR)=-1)
  S = Q - I_p   (now S[i,i] = -1, S is symmetric ish; for p=3 mod 4 Q is
                 anti-symmetric, so S = I + Q gives the Paley construction)
Standard form: H = block matrix
  [[ 1,    1...1 ],
   [ 1^T,  Q - I ]]
which is Hadamard of order p+1 for p = 3 (mod 4). Entries are +/-1.

We use p=1019 (prime, 1019 mod 4 = 3) -> H is (1020, 1020) bipolar.
M = N = 1020. Bipolar matrix normalized as A/sqrt(N).

Verdict
-------
Scoping output only -- prints |delta_n| for n=2..6 and a one-liner
classification (MP_LIKE if all <0.05, NEAR_KERDOCK if delta_2 in [0.15,0.35]
matching Kerdock's known range, NOVEL if otherwise non-trivial).
metrics.json is written with the kappa profile for downstream comparison.

Pre-reg: preregs/2026-05-23_wave14_kappa_paley_quickprobe_v1.md
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
# Re-use the moment-to-free-cumulant inversion and MP reference from v1.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
mp_reference_cumulants = _v1.mp_reference_cumulants
spectral_moments = _v1.spectral_moments


# ---------------------------------------------------------------------------
# Paley Type-I Hadamard construction
# ---------------------------------------------------------------------------

def _legendre_table(p: int) -> np.ndarray:
    """Legendre symbol chi(x) for x in 0..p-1; chi(0)=0, chi(QR)=+1, chi(NQR)=-1."""
    chi = np.zeros(p, dtype=np.int8)
    # Quadratic residues mod p (excluding 0)
    qr = set()
    for k in range(1, p):
        qr.add((k * k) % p)
    for x in range(1, p):
        chi[x] = 1 if x in qr else -1
    return chi


def make_paley_type1_hadamard(p: int) -> np.ndarray:
    """Paley Type-I Hadamard of order p+1 for prime p with p = 3 (mod 4)."""
    assert p % 4 == 3, f"p={p} must be 3 mod 4 for Paley Type-I"
    chi = _legendre_table(p)
    # Q[i,j] = chi(i - j mod p)
    diffs = (np.arange(p)[:, None] - np.arange(p)[None, :]) % p
    Q = chi[diffs]  # (p, p)
    # Paley H = block matrix
    # [[ 1, 1...1 ],
    #  [ 1^T, Q - I_p ]]
    # giving order p+1, all entries +/-1.
    H = np.ones((p + 1, p + 1), dtype=np.int8)
    H[1:, 0] = 1
    H[0, 1:] = 1
    # Diagonal of Q is chi(0) = 0; replace by -1, so Q - I gives 0 - 1 = -1
    # on diagonal as required. Off-diagonal: chi(i-j) in {+1,-1}.
    # Construct Q - I directly:
    QmI = Q.astype(np.int8)
    np.fill_diagonal(QmI, -1)
    H[1:, 1:] = QmI
    # Sanity (cheap): H H^T should be (p+1) * I for Hadamard.
    return H.astype(np.float32)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Tiny Paley with p=3 (3 mod 4 = 3) -> order 4 Hadamard.
    H4 = make_paley_type1_hadamard(3)
    assert H4.shape == (4, 4)
    # Hadamard property: H H^T = 4*I
    G = H4 @ H4.T
    assert np.allclose(G, 4 * np.eye(4)), f"Paley(p=3) not Hadamard:\n{G}"

    # p=7 -> order 8 Hadamard
    H8 = make_paley_type1_hadamard(7)
    assert H8.shape == (8, 8)
    G = H8 @ H8.T
    assert np.allclose(G, 8 * np.eye(8)), f"Paley(p=7) not Hadamard:\n{G}"

    # p=11 -> order 12 Hadamard
    H12 = make_paley_type1_hadamard(11)
    assert H12.shape == (12, 12)
    G = H12 @ H12.T
    assert np.allclose(G, 12 * np.eye(12)), f"Paley(p=11) not Hadamard:\n{G}"

    # Verify Legendre table for p=7: QR = {1, 2, 4}; NQR = {3, 5, 6}
    chi = _legendre_table(7)
    assert chi[0] == 0
    for q in [1, 2, 4]:
        assert chi[q] == 1, f"chi({q}) should be +1, got {chi[q]}"
    for nq in [3, 5, 6]:
        assert chi[nq] == -1, f"chi({nq}) should be -1, got {chi[nq]}"

    print("paley quickprobe self-test passed (Hadamard property p in {3,7,11}, Legendre table p=7)", flush=True)


# ---------------------------------------------------------------------------
# Main probe
# ---------------------------------------------------------------------------

def classify_profile(kappas: list[float], c_ref: float) -> str:
    """One-liner scoping verdict from kappa profile and aspect ratio c=M/N.

    kappas is kappa_1..kappa_{n_max} computed from the *empirical M-eigenvalue*
    spectral moments (per the v1 path: numpy mean over min(M,N) singular
    values squared).

    Special case PERFECT_ISOMETRY: when all M singular values equal sqrt(D/N)
    (rows are mutually orthogonal of equal norm), the empirical spectrum is
    a delta function at sigma**2. moments_n = sigma**(2n) constant; in free
    probability this is kappa_1 = sigma**2, kappa_n = 0 for n>=2. This is
    the *opposite* of MP (which is full bulk); it is the fully-deterministic
    fixed-point of an algebraic Hadamard sub-block. We label it explicitly.
    """
    if not kappas or len(kappas) < 2:
        return "INCONCLUSIVE"

    # Perfect isometry: kappa_n = 0 for n>=2 within tight tolerance, kappa_1 > 0
    tol = 1e-3
    if all(abs(kappas[i]) < tol for i in range(1, len(kappas))) and kappas[0] > 0.5:
        return "PERFECT_ISOMETRY"

    # Otherwise compare to MP via |delta_n| = |kappa_n / c - 1| for n=2..n_max
    if c_ref <= 0:
        return "INCONCLUSIVE"
    devs = [abs(kappas[i] / c_ref - 1.0) for i in range(1, len(kappas))]
    if all(d < 0.05 for d in devs):
        return "MP_LIKE"
    d2 = devs[0]
    if 0.15 <= d2 <= 0.35:
        return "NEAR_KERDOCK"
    if d2 > 0.35:
        return "STRONGER_THAN_KERDOCK"
    return "WEAKER_NON_MP"


def run_probe() -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    config = {
        "mode": "quickprobe",
        # Paley Type-I Hadamard has only p+1 rows. M=N (square) makes the
        # Hadamard isometric -> spectrum is a delta at 1 and all moments = 1.
        # To get a non-trivial spectrum comparable to Kerdock at alpha=0.5,
        # we use Paley dimension D = p+1 = 1020, then SAMPLE N=510 of the
        # 1020 rows. M_over_N relative to the reduced space.
        #
        # Equivalently: we use the (M=1020, N=510) tall Paley as the
        # measurement matrix; alpha_eff = M/N = 2.0. To match the Kerdock
        # alpha=0.5 setting (M=N/2 of 4N total = 2N rows of N-dim, alpha=0.5),
        # we transpose viewpoint: use sub-block size M=510, N=1020 -> alpha=0.5.
        "p": 1019,
        "D": 1020,            # Paley order p+1
        "M": 510,             # rows used  (alpha = M/N = 0.5)
        "N": 1020,            # columns
        "n_seeds": 1,
        "n_max_moment": 6,
        "seed": 0,
    }
    p = config["p"]
    D = config["D"]
    N = config["N"]
    M = config["M"]
    n_max = config["n_max_moment"]

    print(f"[paley quickprobe] p={p} -> Paley Type-I Hadamard order D={D}; sampling M={M} rows, N={N} cols (alpha={M/N:.2f})", flush=True)

    H = make_paley_type1_hadamard(p)  # (D, D) bipolar
    assert H.shape == (D, D), f"H shape {H.shape} != ({D},{D})"

    # Sample M rows out of D=p+1 (deterministic Paley, seed permutes row choice)
    # and use the first N columns of the (D, D) matrix. For D=N=1020 the
    # column subset is the full set; the M-of-D row subset gives a (M, N)
    # bipolar measurement matrix at alpha = M/N.
    rng = np.random.default_rng(config["seed"])
    row_perm = rng.permutation(D)
    A = H[row_perm[:M], :N]  # (M, N) bipolar
    A_norm = A / math.sqrt(N)

    # SVD on CPU (numpy LAPACK); for 1020x1020 this is <5s on laptop CPU.
    t_svd = time.monotonic()
    s = np.linalg.svd(A_norm, compute_uv=False)
    elapsed_svd = time.monotonic() - t_svd
    eig = s ** 2  # eigenvalues of (1/N) A^T A
    print(f"  SVD on ({M},{N}) bipolar took {elapsed_svd:.2f}s", flush=True)

    moms = spectral_moments(eig, n_max)
    kappas = moments_to_free_cumulants_general(moms)
    c_ref = float(M) / float(N)  # 1.0
    kappa_mp = mp_reference_cumulants(c_ref, n_max)

    # Relative deviations (n=1..n_max). Skip n=1 in classification (mean).
    dev_rel = [kappas[i] / c_ref - 1.0 for i in range(n_max)]
    devs_abs = [abs(d) for d in dev_rel[1:]]  # n=2..n_max

    growth_class = classify_profile(kappas, c_ref)

    cell = {
        "p": p, "D": D, "N": N, "M": M, "c_ref": c_ref,
        "moments_emp": moms,
        "kappa_emp": kappas,
        "kappa_mp": kappa_mp,
        "dev_rel": dev_rel,
        "dev_abs_n2plus": devs_abs,
        "growth_class": growth_class,
        "svd_seconds": elapsed_svd,
    }

    print(f"  moments  m_1..m_{n_max} = {[f'{m:.4f}' for m in moms]}", flush=True)
    print(f"  kappas   k_1..k_{n_max} = {[f'{k:+.4f}' for k in kappas]}", flush=True)
    print(f"  MP ref   = {[f'{k:.4f}' for k in kappa_mp]}", flush=True)
    print(f"  dev_rel  = {[f'{d:+.4f}' for d in dev_rel]}", flush=True)
    print(f"  growth_class = {growth_class}", flush=True)

    summary = {"cells": [cell], "config": config}

    if growth_class == "PERFECT_ISOMETRY":
        msg = (
            f"Paley Type-I Hadamard (p={p}, D={D}) sub-block (M={M}, N={N}) is a PERFECT ISOMETRY: "
            f"all M singular values equal (rows mutually orthogonal). Empirical spectrum is a delta "
            f"function; kappa_1 ~ {kappas[0]:.3f}, kappa_n ~ 0 for n>=2. This is the deterministic "
            f"OPPOSITE of MP (which is full bulk). Implication for BBMD: Paley sub-blocks are TOO "
            f"structured -- they collapse the spectrum entirely, not deviate from MP within a bulk. "
            f"Recommendation: a Paley codebook in the Anchor-2 battery would test a DIFFERENT axis "
            f"(isometric vs spread spectrum) than Kerdock's algebraic-bulk deviation. Include only "
            f"if BBMD-distance is generalized to handle delta-spectra; otherwise SKIP."
        )
    elif growth_class == "MP_LIKE":
        msg = (
            f"Paley Type-I Hadamard (p={p}, N={N}) shows MP-like spectrum at n=2..{n_max}: "
            f"max |delta_n| = {max(devs_abs):.3f} < 0.05. Suggests Paley algebraic structure "
            f"does NOT broadly trigger BBMD-regime deviation; Kerdock's 4-coset combinatorics "
            f"may be required. Recommendation: DO NOT prioritize Paley in Anchor-2 expansion."
        )
    elif growth_class == "NEAR_KERDOCK":
        msg = (
            f"Paley Type-I Hadamard (p={p}, N={N}) shows non-MP kappa_n profile in the Kerdock band: "
            f"|delta_2|={devs_abs[0]:.3f} matches Kerdock's [0.15, 0.35] range. Suggests "
            f"BBMD-regime deviation is GENERIC across algebraic Hadamard families, not "
            f"Kerdock-specific. Recommendation: include Paley in expanded codebook battery."
        )
    elif growth_class == "STRONGER_THAN_KERDOCK":
        msg = (
            f"Paley Type-I Hadamard (p={p}, N={N}) shows STRONGER non-MP deviation than Kerdock: "
            f"|delta_2|={devs_abs[0]:.3f} > 0.35. Surprising; Paley combinatorics may have "
            f"larger algebraic signature. Recommendation: include Paley in expanded battery as "
            f"a high-priority probe."
        )
    elif growth_class == "WEAKER_NON_MP":
        msg = (
            f"Paley Type-I Hadamard (p={p}, N={N}) shows mild non-MP deviation: "
            f"|delta_2|={devs_abs[0]:.3f} < 0.15. Substrate-novel-ish but weaker than Kerdock. "
            f"Recommendation: optional Anchor-2 inclusion; not high-priority."
        )
    else:
        msg = f"Paley quickprobe inconclusive: devs_abs = {devs_abs}"

    verdict = f"PALEY_QUICKPROBE_{growth_class}"
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
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_paley_quickprobe_v1")
    summary, verdict, msg, elapsed, config = run_probe()
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict} ({elapsed:.1f}s)", flush=True)


def run_smoke() -> None:
    self_test()
    # Smoke is the same probe -- it's <60s; we don't have a smaller variant.
    out_dir = get_output_dir("wave14_kappa_paley_quickprobe_v1_smoke")
    summary, verdict, msg, elapsed, config = run_probe()
    assert len(summary["cells"]) == 1, "smoke FAIL: missing cell"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict} ({elapsed:.1f}s)", flush=True)


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
