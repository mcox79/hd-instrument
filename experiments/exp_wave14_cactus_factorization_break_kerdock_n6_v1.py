"""Cactus factorization break test on Kerdock-Hebbian W (spectral moment n=6).

Falsification anchor for the partial-thermalization (PFK) interpretation of
the substrate. From `notes/research_eth_thermalization_drill_2026-05-23.md`
Anchor #2.

PFK 2023 / Pappalardi et al. hard-pass criterion: "full ETH" holds when the
cyclic n-point moment of the operator matrix-element distribution is
captured by the FACTORIZED cactus expansion using ONLY LOWER-ORDER free
cumulants kappa_2..kappa_{n-1}; the full-block kappa_n contribution is
exponentially suppressed in Hilbert dimension. If kappa_n contributes a
non-trivial fraction of m_n at finite N, the substrate is in the
partial-thermalization regime where higher cumulants encode structure.

Operator and observable. On the substrate, the operator A is the Hebbian
weight matrix at sub-sampled measurement ratio alpha = M/N < 4 (so that W
is non-trivially structured rather than proportional to identity):

  W_alpha = (1/N) C_sub^T C_sub
  where C_sub is M = alpha * N randomly subsampled codewords from the full
  4N-row Kerdock 4-coset codebook.

The "cyclic n-product moment" m_n is the n-th spectral moment of W_alpha:

  m_n := E_lambda [ lambda^n ] = (1/N) sum_i lambda_i^n
  where lambda_i are the eigenvalues of W_alpha. This is exactly v167's
  hierarchy.

Free cumulants kappa_n inverted from m_1..m_n via the moment-to-free-cumulant
recursion on the non-crossing partition lattice (same machinery as v167).

By the moment-cumulant identity, m_n = sum_{pi in NC(n)} kappa_pi EXACTLY.
The cactus factorization break test isolates the FULL-BLOCK partition
contribution (the kappa_n atom) versus the FACTORIZED (>=2 blocks)
contribution:

  cactus_factorized_n  := sum over pi in NC(n) with |pi| >= 2 of
                          product over B in pi of kappa_{|B|}
                       == sum over PROPER non-crossing partitions
  R_n                  := m_n_empirical / cactus_factorized_n
                       == 1 + kappa_n / cactus_factorized_n

PFK / Pappalardi 2023 expectation: at thermalization, kappa_n / cactus_factorized_n
-> 0 as N grows; equivalently R_n -> 1. At partial thermalization, kappa_n
stays a non-trivial fraction of cactus_factorized_n and R_n stays bounded
away from 1.

The PFK cyclic-product test on an actual operator on codeword pairs is
hopeless at this N: Kerdock 4-coset is a tight frame so the full W is
4*I, and the matrix-element-on-codewords cyclic product is sign-cancelled
near zero. We work with the SUB-SAMPLED Gram spectral moments, which is
v167's exact setup, where the kappa cascade has been measured to grow
with n (the original substrate-novel finding being interpreted here).

Hypotheses (PFK partial-thermalization vs full-ETH bulk-non-Gaussian):
  HARD PASS  R_6 > 1.20 in >= 8/10 seeds   -> crossing partitions contribute
                                              > 20%; substrate is partial-ETH.
  HARD FAIL  R_6 in [0.95, 1.05] in >= 8/10 seeds -> cactus dominates; full-ETH.
  ANOMALY    R_6 < 0.80 (different failure mode; flag for investigation).

Operator "A" is the Kerdock-Hebbian W on codeword basis. Per the drill's
Section 2 mapping:
   "matrix element A_{ij}"  <-> <c_i, W c_j>
where c_i are Kerdock 4-coset codewords (orthonormal under (1/N) inner
product after bipolar normalization) and W is the Hebbian weight matrix
W = (1/N) sum_i c_i c_i^T (i.e. (1/N) C^T C with C the (4N, N) codebook).

Empirical M_6: sample S random codeword index sextuples (i1,...,i6),
compute the cyclic-6 product, average.

Empirical kappa_2..kappa_6: same machinery as v167 / exp_wave14_kappa_n_profile_v1.py
applied at alpha = 4 (M=4N=full codebook) since the codeword inner product
distribution is what the cyclic-product test samples.

Why kappa from the same run rather than v167 cached:
  - Self-consistency: ratio R_6 must compare like-with-like.
  - v167 N=4096 full-run metrics.json not available on desktop; smoke is
    N=1024.
  - kappa enumeration is cheap (Catalan C_6 = 132 partitions).

Vertex: PFK_PARTIAL_ETH_CONFIRMED / PFK_FULL_ETH_BULK / PFK_R6_ANOMALY /
        PFK_R6_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_cactus_factorization_break_kerdock_n6_v1.md
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
from functools import lru_cache
from pathlib import Path
from typing import Iterator

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import Kerdock 4-coset codebook builder
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Import NCP enumeration + moment-to-free-cumulant inversion from v167 script
_kappa_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_k = importlib.util.spec_from_file_location("kappa_v167", _kappa_path)
_kappa_mod = importlib.util.module_from_spec(_spec_k)
_spec_k.loader.exec_module(_kappa_mod)
_enumerate_ncp = _kappa_mod._enumerate_ncp
_ncp_block_sizes = _kappa_mod._ncp_block_sizes
moments_to_free_cumulants_general = _kappa_mod.moments_to_free_cumulants_general
spectral_moments = _kappa_mod.spectral_moments

import torch


# ---------------------------------------------------------------------------
# Sub-sampled Kerdock Hebbian W (matches v167 setup at alpha=M/N)
# ---------------------------------------------------------------------------

def build_kerdock_codebook(N: int) -> np.ndarray:
    """Build Kerdock 4-coset codebook C (4N, N) as float32 numpy."""
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    return cb.float().numpy()


def build_subsampled_W(C: np.ndarray, M: int, seed: int) -> np.ndarray:
    """Sub-sample M rows of C; return W_alpha = (1/N) C_sub^T C_sub."""
    rng = np.random.default_rng(seed)
    n_cw, N = C.shape
    idx = rng.choice(n_cw, size=M, replace=False)
    C_sub = C[idx]
    W = (C_sub.T @ C_sub) / float(N)
    return W


def spectral_moments_from_W(W: np.ndarray, n_max: int) -> tuple[list[float], np.ndarray]:
    """Eigendecompose W; return (m_1..m_{n_max}, eigvals)."""
    eigs = np.linalg.eigvalsh(W).astype(np.float64)
    moms = [float(np.mean(eigs ** n)) for n in range(1, n_max + 1)]
    return moms, eigs


# ---------------------------------------------------------------------------
# Empirical cyclic-6 product M_6
# ---------------------------------------------------------------------------

def cyclic_product_M_n(W: np.ndarray, C: np.ndarray, n: int, n_samples: int,
                       rng: np.random.Generator) -> tuple[float, float]:
    """Estimate the cyclic-n product

        M_n = E_{(i_1,...,i_n) iid uniform} [ a_{i_1 i_2} a_{i_2 i_3} ...
                                              a_{i_{n-1} i_n} a_{i_n i_1} ]

    where a_{ij} = <c_i, W c_j> / N (codeword-basis "matrix element").

    The normalization /N is chosen so that for W = (1/N) C^T C and codewords
    that are orthonormal under (1/N) ip, a_{ii} ~ O(1) and a_{ij} (i!=j) is
    the Kerdock inner-product residual O(1/sqrt(N)).

    Returns mean and standard error of the per-sample products.
    """
    n_cw = C.shape[0]  # 4N
    # Pre-compute W @ c_i for each sampled codeword
    # We sample n_samples n-tuples of codeword indices and compute the
    # cyclic product. For memory we batch.

    # Approach: sample one big batch of indices, build per-tuple chain.
    # Index array shape (n_samples, n).
    idx = rng.integers(0, n_cw, size=(n_samples, n))

    # For each tuple, compute a_{i_k i_{k+1}} = (C[i_k] @ W @ C[i_{k+1}]) / N
    # Vectorize: precompute v_k = W @ C[idx[:,k]].T (N, n_samples) for each k.
    products = np.ones(n_samples, dtype=np.float64)
    N = W.shape[0]
    for k in range(n):
        k_next = (k + 1) % n
        # c_lo: (n_samples, N), c_hi: (n_samples, N)
        c_lo = C[idx[:, k]]
        c_hi = C[idx[:, k_next]]
        # a_k = (c_lo @ W @ c_hi^T)_{diagonal} for each sample
        # = einsum: 's i, i j, s j -> s'
        # = sum_{i,j} c_lo[s,i] W[i,j] c_hi[s,j]
        Wc = c_hi @ W.T  # (n_samples, N); since W symmetric, W.T == W
        a_k = np.einsum('si,si->s', c_lo, Wc) / float(N)
        products *= a_k

    mean = float(np.mean(products))
    se = float(np.std(products, ddof=1) / math.sqrt(n_samples))
    return mean, se


# ---------------------------------------------------------------------------
# Cactus-sum prediction from empirical kappa_2..kappa_n
# ---------------------------------------------------------------------------

def cactus_sum(kappas: list[float], n: int) -> float:
    """Compute sum_{pi in NC(n)} kappa_pi where kappa_pi = product_{B in pi}
    kappa_{|B|}, using empirical kappa_2..kappa_n from the substrate.

    kappas is 1-indexed conceptually but passed as a list [kappa_1, kappa_2, ...].
    NC(n) has Catalan(n) elements; for n=6 that's 132 partitions.
    """
    assert len(kappas) >= n, f"need at least kappa_1..kappa_{n}, got {len(kappas)}"
    partitions = _ncp_block_sizes(n)
    total = 0.0
    for sizes in partitions:
        prod = 1.0
        for s in sizes:
            prod *= kappas[s - 1]  # kappas is 0-indexed -> kappa_s at index s-1
        total += prod
    return total


def cactus_sum_excluding_full_block(kappas: list[float], n: int) -> float:
    """Cactus sum but excluding the singleton-partition pi = {{1..n}} that
    contributes kappa_n. Useful diagnostic."""
    partitions = _ncp_block_sizes(n)
    total = 0.0
    for sizes in partitions:
        if len(sizes) == 1:
            continue  # the full block contributes kappa_n
        prod = 1.0
        for s in sizes:
            prod *= kappas[s - 1]
        total += prod
    return total


# ---------------------------------------------------------------------------
# Empirical cyclic-moment hierarchy m_1..m_n -- the PFK "matrix-element"
# cumulant cascade. kappa_n inverted from m_1..m_n via NC-partition lattice.
# ---------------------------------------------------------------------------

def cyclic_moments_hierarchy(W: np.ndarray, C: np.ndarray, n_max: int,
                              n_samples: int, rng: np.random.Generator
                              ) -> tuple[list[float], list[float]]:
    """For each n in 1..n_max, compute m_n = E[ cyclic-n product of a_{i_k i_{k+1}} ].

    Uses the SAME index sample for all n simultaneously: draw a single
    (n_samples, n_max) index array, compute the running product of
    a_{i_k i_{k+1}} where the cycle closes at the n-th step (for partial
    products, the cycle closes at i_n -> i_1). For n < n_max we use the
    first n indices as their own cycle (independent samples per n) to
    keep estimators unbiased.

    Returns (means, ses) lists of length n_max.
    """
    N = W.shape[0]
    n_cw = C.shape[0]
    means = []
    ses = []
    for n in range(1, n_max + 1):
        idx = rng.integers(0, n_cw, size=(n_samples, n))
        # cyclic product
        products = np.ones(n_samples, dtype=np.float64)
        for k in range(n):
            k_next = (k + 1) % n
            c_lo = C[idx[:, k]]
            c_hi = C[idx[:, k_next]]
            Wc = c_hi @ W  # (n_samples, N); W symmetric
            a_k = np.einsum('si,si->s', c_lo, Wc) / float(N)
            products *= a_k
        mn = float(np.mean(products))
        se = float(np.std(products, ddof=1) / math.sqrt(n_samples))
        means.append(mn)
        ses.append(se)
    return means, ses


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(R_per_seed: list[float], n_seeds: int) -> tuple[str, str]:
    """Apply HARD-PASS / HARD-FAIL thresholds per the prereg."""
    n = len(R_per_seed)
    if n == 0:
        return "PFK_R6_INCONCLUSIVE", "no seeds produced"

    n_pass = sum(1 for r in R_per_seed if r > 1.20)
    n_fail = sum(1 for r in R_per_seed if 0.95 <= r <= 1.05)
    n_anom = sum(1 for r in R_per_seed if r < 0.80)

    median = float(np.median(R_per_seed))
    mean = float(np.mean(R_per_seed))

    if n_pass >= 8 and n >= 10:
        return (
            "PFK_PARTIAL_ETH_CONFIRMED",
            f"R_6 > 1.20 in {n_pass}/{n} seeds (median={median:.4f}, mean={mean:.4f}). "
            f"Crossing partitions contribute > 20% of the cyclic-6 product; "
            f"substrate is empirically a partial-thermalization regime in the "
            f"Pappalardi-Foini-Kurchan sense. PFK framing of BBMD as "
            f"partial-thermalization SURVIVES this anchor."
        )
    if n_fail >= 8 and n >= 10:
        return (
            "PFK_FULL_ETH_BULK",
            f"R_6 in [0.95, 1.05] in {n_fail}/{n} seeds (median={median:.4f}, mean={mean:.4f}). "
            f"Cactus factorization dominates; substrate is full-ETH-class with "
            f"non-Gaussian bulk shape but standard thermalization. "
            f"PFK partial-thermalization framing KILLED at the n=6 cactus level."
        )
    if n_anom >= 8 and n >= 10:
        return (
            "PFK_R6_ANOMALY",
            f"R_6 < 0.80 in {n_anom}/{n} seeds (median={median:.4f}, mean={mean:.4f}). "
            f"Empirical 6-product is BELOW the cactus prediction -- a different "
            f"failure mode of the PFK mapping; framing is wrong in a way that "
            f"needs investigation (possibly a sign/normalization mismatch, or "
            f"substrate has destructive crossing-partition interference)."
        )
    return (
        "PFK_R6_INCONCLUSIVE",
        f"No threshold reached. R_6 distribution across {n} seeds: "
        f"median={median:.4f}, mean={mean:.4f}, "
        f"PASS(>1.20)={n_pass} FAIL([0.95,1.05])={n_fail} ANOMALY(<0.80)={n_anom}."
    )


# ---------------------------------------------------------------------------
# Smoke self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    # 1) cactus_sum on Marchenko-Pastur (all kappa_n = c) reproduces MP m_n
    for c in [0.5, 1.0, 2.0, 4.0]:
        kappas = [c] * 8
        # MP moments via direct formula (matches v167)
        mp_moms = []
        for nn in range(1, 9):
            total = 0.0
            for k in range(1, nn + 1):
                total += math.comb(nn, k) * math.comb(nn, k - 1) * (c ** k) / nn
            mp_moms.append(total)
        for n_test in range(1, 9):
            csum = cactus_sum(kappas, n_test)
            assert abs(csum - mp_moms[n_test - 1]) < 1e-9, (
                f"MP(c={c}) n={n_test}: cactus={csum} vs mp_m={mp_moms[n_test - 1]}"
            )

    # 2) verdict logic
    v, _ = compute_verdict([1.30] * 10, 10)
    assert v == "PFK_PARTIAL_ETH_CONFIRMED", v
    v, _ = compute_verdict([1.00] * 10, 10)
    assert v == "PFK_FULL_ETH_BULK", v
    v, _ = compute_verdict([0.70] * 10, 10)
    assert v == "PFK_R6_ANOMALY", v
    v, _ = compute_verdict([1.15, 1.10, 1.05, 1.00, 0.90], 5)
    assert v == "PFK_R6_INCONCLUSIVE", v

    print("self-test passed (cactus_sum reproduces MP; verdict branches all reachable)",
          flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "n_seeds": 1,
            "alpha": 1.0,
            "n_max_cumulant": 6,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "n_seeds": 10,
            "alpha": 1.0,  # v167 central case where kappa_n GROWS with n
            "n_max_cumulant": 6,
        }

    N = config["N"]
    n_seeds = config["n_seeds"]
    alpha = config["alpha"]
    M = int(alpha * N)
    n_max = config["n_max_cumulant"]

    # Build Kerdock codebook once (deterministic)
    print(f"[build] Kerdock 4-coset codebook at N={N} (4N={4*N} codewords)",
          flush=True)
    t_build = time.monotonic()
    C = build_kerdock_codebook(N)
    print(f"[build] C shape={C.shape} in {time.monotonic()-t_build:.1f}s",
          flush=True)
    print(f"[setup] alpha={alpha}, M={M}, c_ref={alpha} (MP reference)",
          flush=True)

    per_seed = []
    R_per_seed = []
    for seed in range(n_seeds):
        t_seed = time.monotonic()

        # Sub-sample M codewords per seed; build W; compute spectral moments
        W = build_subsampled_W(C, M, seed=1000 + seed)
        m_list, eigs = spectral_moments_from_W(W, n_max)

        # Invert to kappa_1..kappa_n via NC-partition lattice (matches v167)
        kappas = moments_to_free_cumulants_general(m_list)

        # Cactus prediction at n_max using ONLY lower kappas (factorized,
        # |pi| >= 2 partitions). The full-block partition contributes
        # kappa_n, which is the "atom" being tested.
        pred_factorized = cactus_sum_excluding_full_block(kappas, n_max)
        # Sanity (identity): cactus_sum INCLUDING the kappa_n atom equals m_n.
        pred_full_cactus = cactus_sum(kappas, n_max)

        m_n_emp = m_list[n_max - 1]
        kappa_n = kappas[n_max - 1]
        if abs(pred_factorized) < 1e-18:
            R_n = float('nan')
        else:
            R_n = m_n_emp / pred_factorized

        # MP reference for context (all kappa_n = alpha)
        mp_factorized = sum(
            1.0 if len(s) == 1 else float(np.prod([alpha for _ in s]))
            for s in _ncp_block_sizes(n_max) if len(s) >= 2
        )

        per_seed.append({
            "seed": seed,
            "M": M,
            "m_list": m_list,
            "kappa_list": kappas,
            "m_n_emp": m_n_emp,
            "kappa_n": kappa_n,
            "cactus_factorized_n": pred_factorized,
            "cactus_full_NC_n": pred_full_cactus,
            "mp_cactus_factorized_n": mp_factorized,
            "R_n": R_n,
            "elapsed_s": time.monotonic() - t_seed,
        })
        R_per_seed.append(R_n)
        print(f"  seed={seed}: m_6={m_n_emp:+.4e}  kappa_6={kappa_n:+.4e}  "
              f"cactus_factorized={pred_factorized:+.4e}  "
              f"identity_check(full_cactus-m_n)={pred_full_cactus-m_n_emp:+.3e}  "
              f"R_6={R_n:+.4f}  ({time.monotonic()-t_seed:.1f}s)", flush=True)
        if seed == 0:
            print(f"           kappas={[f'{k:+.4e}' for k in kappas]}", flush=True)
            print(f"           moments={[f'{x:+.4e}' for x in m_list]}", flush=True)

    verdict, msg = compute_verdict(R_per_seed, n_seeds)

    summary = {
        "config": config,
        "per_seed": per_seed,
        "R_6_per_seed": R_per_seed,
        "R_6_median": float(np.median(R_per_seed)) if R_per_seed else None,
        "R_6_mean": float(np.mean(R_per_seed)) if R_per_seed else None,
        "R_6_std": float(np.std(R_per_seed, ddof=1)) if len(R_per_seed) > 1 else None,
    }
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
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


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cactus_factorization_break_kerdock_n6_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["per_seed"]) >= 1, "smoke FAIL: no per-seed entries"
    assert len(summary["R_6_per_seed"]) >= 1, "smoke FAIL: no R_6 samples"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cactus_factorization_break_kerdock_n6_v1")
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
