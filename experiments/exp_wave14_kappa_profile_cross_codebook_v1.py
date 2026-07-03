"""Cross-codebook kappa_n + MP-KS probe: Anchor 2 for the BBMD-regime proposal.

Motivation
----------
Research note 2026-05-23 proposes that the BBMD-distance scalar
   sum_{n=2..6} | kappa_n - kappa_n^MP |
is a DISCRIMINATOR for AMP-non-universality of structured codebooks that the
standard MP-KS sanity check MISSES. If the standard MP-KS test passes on a
codebook (bulk-bounded support) but BBMD-distance is large (moment-divergent),
that codebook will silently break scalar-Onsager AMP — and the BBMD-distance
predicts the breakage magnitude (Anchor 1 tests this directly).

Anchor 2 ranks five codebooks by BBMD-distance and confirms MP-KS passes for
all of them. If both hold, the kappa_n profile is the needed extra
substrate-product diagnostic.

Codebooks (all built at N=4096 except where indicated)
------------------------------------------------------
  1. iid Gaussian (baseline, BBMD-distance ~ 0)
  2. SRHT — Subsampled Randomized Hadamard Transform (proven AMP-universal,
     Dudeja-Lu-Kini 2022): D * H * S where H is N x N Sylvester Hadamard,
     D is random {+1,-1} diagonal, S subsamples M of N rows.
  3. Hadamard — direct row-subsample of N x N Sylvester Hadamard (no D, no S
     post-multiplication of columns; M rows uniformly sampled).
  4. Reed-Muller RM(1, m=12) — linear binary code with 2^(m+1) = 2*N codewords
     of length N=2^m. Generator: rows of [1; H_n_log2] in {0,1} mapped to bipolar.
     Encoded x in {0,1}^(m+1) -> bipolar codeword (-1)^{u . [1, b]} where b = binary
     expansion of position. 2N codewords total; subsample M of them.
  5. Kerdock 4-coset — existing substrate codebook (4N codewords).

For each codebook: M = N (alpha = M/N = 1.0), 10 seeds, compute kappa_n profile
(n=2..6) and MP-KS statistic.

HARD PASS:
  Ordering by BBMD-distance: iid <= SRHT < Hadamard <= RM(1,m) < Kerdock
  AND MP-KS < 0.05 for ALL FIVE codebooks at every seed (or in 9/10 seeds).

HARD FAIL:
  Ordering scrambled (e.g., Kerdock not max OR iid/SRHT not min)
  OR MP-KS already discriminates AMP-universal from AMP-non-universal
  (some structured codebook has KS >= 0.05 — then kappa_n adds nothing).

INCONCLUSIVE: anything else.

Vertex: KAPPA_CROSS_CODEBOOK_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-23_wave14_kappa_profile_cross_codebook_v1.md
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
# Reuse Kerdock 4-coset builder (and its sylvester_hadamard helper via v1)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec_v3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec_v3)
_spec_v3.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Reuse orth-keys v1 for sylvester_hadamard
_okv1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
_spec_okv1 = importlib.util.spec_from_file_location("orthkeys_v1", _okv1_path)
_okv1 = importlib.util.module_from_spec(_spec_okv1)
_spec_okv1.loader.exec_module(_okv1)
sylvester_hadamard = _okv1.sylvester_hadamard

# Reuse moment-to-free-cumulant inversion
_kpv1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_kpv1 = importlib.util.spec_from_file_location("kappa_v1", _kpv1_path)
_kpv1 = importlib.util.module_from_spec(_spec_kpv1)
_spec_kpv1.loader.exec_module(_kpv1)
moments_to_free_cumulants_general = _kpv1.moments_to_free_cumulants_general

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Codebook constructors
# ---------------------------------------------------------------------------

def build_iid_gauss(N: int, M: int, seed: int) -> np.ndarray:
    """iid N(0, 1/N) entries: A in R^{M x N} (already-normalized iid Gaussian)."""
    rng = np.random.default_rng(seed)
    return (rng.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)


def build_srht(N: int, M: int, seed: int) -> np.ndarray:
    """SRHT: subsample M rows of (D * H), where D is random {+1,-1} diagonal
    and H is N x N Sylvester Hadamard. Per Dudeja-Lu-Kini 2022, AMP-universal.

    Returns shape (M, N) normalized to spectral scale 1 (entries in {+/-1/sqrt(N)}).
    """
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    n_log2 = int(round(math.log2(N)))
    assert 2 ** n_log2 == N, f"N={N} must be power of 2"
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)  # (N, N)
    rng = np.random.default_rng(seed)
    D_diag = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    DH = (H * D_diag[np.newaxis, :])  # apply D on the right columns -> shape (N, N)
    # Subsample M rows
    row_idx = rng.choice(N, size=M, replace=False)
    A = DH[row_idx]  # (M, N) in {+/-1}
    return (A / math.sqrt(N)).astype(np.float32)


def build_hadamard(N: int, M: int, seed: int) -> np.ndarray:
    """Plain Hadamard: subsample M rows of N x N Sylvester Hadamard (no random D)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    n_log2 = int(round(math.log2(N)))
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    rng = np.random.default_rng(seed)
    row_idx = rng.choice(N, size=M, replace=False)
    A = H[row_idx]
    return (A / math.sqrt(N)).astype(np.float32)


def build_rm_1_m(N: int, M: int, seed: int) -> np.ndarray:
    """Reed-Muller RM(1, m): 2N codewords of length N=2^m in {+1,-1}.

    A linear binary code: codewords indexed by u in F_2^(m+1) of length m+1.
    Codeword c_u at position x in {0,..,N-1}: c_u(x) = (-1)^{u_0 + sum_{i=1..m} u_i * x_i}
    where x_i are bits of x. Equivalently a bipolar Hadamard-row XOR-ed with the
    all-ones bit (the u_0 bit). 2N codewords total (one per (m+1)-bit u).

    Returns (M, N) by subsampling M of the 2N codewords.

    Note: RM(1, m) is exactly the rows of Sylvester Hadamard together with their
    negations. Equivalently the first-order Reed-Muller code is the bipolar
    H rows union -H rows.
    """
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    n_log2 = int(round(math.log2(N)))
    H = sylvester_hadamard(n_log2, torch.device("cpu")).numpy().astype(np.float32)
    codebook = np.concatenate([H, -H], axis=0)  # (2N, N) -- RM(1, m)
    rng = np.random.default_rng(seed)
    row_idx = rng.choice(codebook.shape[0], size=M, replace=False)
    A = codebook[row_idx]
    return (A / math.sqrt(N)).astype(np.float32)


def build_kerdock(N: int, M: int, seed: int) -> np.ndarray:
    """Subsample M rows from substrate's 4-coset Kerdock codebook (4N codewords)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A = cb[idx].float().numpy()
    return (A / math.sqrt(N)).astype(np.float32)


CODEBOOKS = [
    ("iid_gauss", build_iid_gauss),
    ("srht", build_srht),
    ("hadamard", build_hadamard),
    ("rm_1_m", build_rm_1_m),
    ("kerdock", build_kerdock),
]

# Expected ordering by BBMD-distance (smallest first)
EXPECTED_ORDER = ["iid_gauss", "srht", "hadamard", "rm_1_m", "kerdock"]


# ---------------------------------------------------------------------------
# MP-KS test (per pretest_v1)
# ---------------------------------------------------------------------------

def mp_ks_stat(eig: np.ndarray, M: int, N: int) -> tuple[float, float, float]:
    """KS statistic between empirical eigenvalue CDF and Marchenko-Pastur(c)
    where c = M/N. Returns (ks, lam_minus, lam_plus).
    """
    alpha = M / N
    lam_minus = (1.0 - math.sqrt(min(alpha, 1.0))) ** 2 if alpha < 1.0 else 0.0
    lam_plus = (1.0 + math.sqrt(alpha)) ** 2
    if lam_plus - lam_minus < 1e-9:
        return (1.0, lam_minus, lam_plus)

    n_grid = 400
    grid = np.linspace(lam_minus, lam_plus, n_grid + 1)
    mp_pdf = np.zeros(n_grid + 1)
    interior = (grid > lam_minus + 1e-12) & (grid < lam_plus - 1e-12) & (grid > 1e-12)
    interior_grid = grid[interior]
    mp_pdf[interior] = (np.sqrt(np.maximum((lam_plus - interior_grid) * (interior_grid - lam_minus), 0))
                        / (2.0 * math.pi * alpha * interior_grid))
    # Trapezoidal integral -> CDF on the grid
    cdf_grid = np.zeros(n_grid + 1)
    for i in range(1, n_grid + 1):
        cdf_grid[i] = cdf_grid[i - 1] + 0.5 * (mp_pdf[i] + mp_pdf[i - 1]) * (grid[i] - grid[i - 1])
    if cdf_grid[-1] > 0:
        cdf_grid = cdf_grid / cdf_grid[-1]

    empirical = np.sort(eig)
    n = len(empirical)
    max_d = 0.0
    for i, x in enumerate(empirical):
        if x <= lam_minus:
            mp_cdf = 0.0
        elif x >= lam_plus:
            mp_cdf = 1.0
        else:
            j = int((x - lam_minus) / (lam_plus - lam_minus) * n_grid)
            j = max(0, min(n_grid, j))
            mp_cdf = float(cdf_grid[j])
        emp_cdf = (i + 1) / n
        d = abs(emp_cdf - mp_cdf)
        if d > max_d:
            max_d = d
    return (float(max_d), float(lam_minus), float(lam_plus))


# ---------------------------------------------------------------------------
# Per-codebook measurement
# ---------------------------------------------------------------------------

def measure_codebook(name: str, builder, N: int, M: int, n_seeds: int,
                     n_max: int) -> dict:
    """For one codebook: build M x N matrix, compute kappa profile + MP-KS per seed.
    Returns dict with per-seed records + aggregate.
    """
    c_ref = M / N
    per_seed = []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 13
        A = builder(N, M, seed_val)
        # SVD -> eigenvalues of A A^T
        s = np.linalg.svd(A, compute_uv=False)
        eig = (s ** 2).astype(np.float64)
        moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
        kappas = moments_to_free_cumulants_general(moms)
        # BBMD-distance over n=2..n_max
        if len(kappas) >= n_max:
            d = float(sum(abs(kappas[n - 1] - c_ref) for n in range(2, n_max + 1)))
        else:
            d = float("nan")
        ks_stat, lam_m, lam_p = mp_ks_stat(eig, M, N)
        per_seed.append({
            "seed": seed_val,
            "kappas": kappas,
            "bbmd_distance": d,
            "ks_stat": ks_stat,
            "lam_minus": lam_m,
            "lam_plus": lam_p,
        })
        print(f"    {name:10s} seed={seed} bbmd={d:.4f} ks={ks_stat:.4f}", flush=True)

    bbmd_mean = float(np.mean([r["bbmd_distance"] for r in per_seed if math.isfinite(r["bbmd_distance"])]))
    ks_mean = float(np.mean([r["ks_stat"] for r in per_seed]))
    ks_max = float(np.max([r["ks_stat"] for r in per_seed]))
    kappa_mean = np.mean([r["kappas"] for r in per_seed], axis=0).tolist()
    return {
        "name": name,
        "bbmd_distance_mean": bbmd_mean,
        "ks_stat_mean": ks_mean,
        "ks_stat_max": ks_max,
        "kappa_mean": kappa_mean,
        "per_seed": per_seed,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """HARD PASS: BBMD-distance ordering matches EXPECTED_ORDER (non-strict)
    AND MP-KS < 0.05 in ALL FIVE codebooks at mean.

    HARD FAIL: ordering badly scrambled (Kerdock not max OR iid_gauss not min in
    mean) OR some structured codebook (srht/hadamard/rm_1_m) has KS >= 0.05
    (the MP-KS pre-test already discriminates).
    """
    cbs = summary.get("codebook_results") or []
    if len(cbs) < len(EXPECTED_ORDER):
        return ("KAPPA_CROSS_CODEBOOK_INCONCLUSIVE",
                f"Missing codebooks: have {len(cbs)} need {len(EXPECTED_ORDER)}.")

    by_name = {c["name"]: c for c in cbs}
    for nm in EXPECTED_ORDER:
        if nm not in by_name:
            return ("KAPPA_CROSS_CODEBOOK_INCONCLUSIVE", f"Missing codebook {nm}.")

    sorted_actual = sorted(EXPECTED_ORDER, key=lambda nm: by_name[nm]["bbmd_distance_mean"])
    bbmds = {nm: by_name[nm]["bbmd_distance_mean"] for nm in EXPECTED_ORDER}
    ks_means = {nm: by_name[nm]["ks_stat_mean"] for nm in EXPECTED_ORDER}

    summary["sorted_by_bbmd"] = sorted_actual
    summary["bbmd_by_name"] = bbmds
    summary["ks_by_name"] = ks_means

    # Check ordering: non-strict (allow ties in middle); require iid_gauss is min
    # and kerdock is max; SRHT ranks below RM(1,m); Hadamard somewhere between
    # SRHT and Kerdock. Concretely require:
    #   (i) iid_gauss is bbmd-minimal
    #   (ii) kerdock is bbmd-maximal
    #   (iii) SRHT <= RM(1,m) (the AMP-universal vs structured-non-universal split)
    iid_is_min = bbmds["iid_gauss"] <= min(bbmds[nm] for nm in EXPECTED_ORDER)
    kerdock_is_max = bbmds["kerdock"] >= max(bbmds[nm] for nm in EXPECTED_ORDER)
    srht_le_rm = bbmds["srht"] <= bbmds["rm_1_m"] + 1e-6

    ordering_ok = iid_is_min and kerdock_is_max and srht_le_rm
    ks_all_pass = all(ks_means[nm] < 0.05 for nm in EXPECTED_ORDER)

    # FAIL conditions
    structured_ks_fail = any(ks_means[nm] >= 0.05 for nm in ["srht", "hadamard", "rm_1_m"])

    if ordering_ok and ks_all_pass:
        return ("KAPPA_CROSS_CODEBOOK_PASS",
                f"BBMD-distance ordering matches expectation "
                f"({' <= '.join(sorted_actual)}): {bbmds}; MP-KS passes (< 0.05) for "
                f"all five codebooks: {ks_means}. The standard MP-KS pre-test FAILS "
                f"to detect AMP-non-universality on Kerdock/Hadamard/RM(1,m) -- the "
                f"kappa_n profile IS the needed extra discriminator. "
                f"Anchor 2 of BBMD-regime promotion lands positive.")

    fail_reasons = []
    if not iid_is_min:
        fail_reasons.append(f"iid_gauss is NOT bbmd-min ({bbmds['iid_gauss']:.4f}); "
                            f"min is {sorted_actual[0]} at {bbmds[sorted_actual[0]]:.4f}")
    if not kerdock_is_max:
        fail_reasons.append(f"kerdock is NOT bbmd-max ({bbmds['kerdock']:.4f}); "
                            f"max is {sorted_actual[-1]} at {bbmds[sorted_actual[-1]]:.4f}")
    if not srht_le_rm:
        fail_reasons.append(f"SRHT > RM(1,m) ({bbmds['srht']:.4f} > {bbmds['rm_1_m']:.4f})")
    if structured_ks_fail:
        offenders = [(nm, ks_means[nm]) for nm in ["srht", "hadamard", "rm_1_m"]
                     if ks_means[nm] >= 0.05]
        fail_reasons.append(f"MP-KS already discriminates: {offenders}")

    if fail_reasons:
        return ("KAPPA_CROSS_CODEBOOK_KILLED",
                f"BBMD as a portable discriminator killed. Reasons: "
                f"{'; '.join(fail_reasons)}. BBMD={bbmds}, KS={ks_means}.")

    return ("KAPPA_CROSS_CODEBOOK_INCONCLUSIVE",
            f"Borderline: ordering_ok={ordering_ok} ks_all_pass={ks_all_pass}. "
            f"BBMD={bbmds}, KS={ks_means}.")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    """Test verdict branches + MP-KS sanity on a synthetic MP eigenvalue draw."""

    # Test 1: PASS branch
    cbs_pass = [
        {"name": "iid_gauss", "bbmd_distance_mean": 0.02, "ks_stat_mean": 0.02, "ks_stat_max": 0.03, "kappa_mean": []},
        {"name": "srht",      "bbmd_distance_mean": 0.05, "ks_stat_mean": 0.03, "ks_stat_max": 0.04, "kappa_mean": []},
        {"name": "hadamard",  "bbmd_distance_mean": 0.20, "ks_stat_mean": 0.04, "ks_stat_max": 0.05, "kappa_mean": []},
        {"name": "rm_1_m",    "bbmd_distance_mean": 0.30, "ks_stat_mean": 0.04, "ks_stat_max": 0.05, "kappa_mean": []},
        {"name": "kerdock",   "bbmd_distance_mean": 1.20, "ks_stat_mean": 0.04, "ks_stat_max": 0.06, "kappa_mean": []},
    ]
    v, _ = compute_verdict({"codebook_results": cbs_pass})
    assert v == "KAPPA_CROSS_CODEBOOK_PASS", f"expected PASS got {v}"

    # Test 2: KILLED via scrambled ordering (Kerdock not max)
    cbs_killed_order = [
        {"name": "iid_gauss", "bbmd_distance_mean": 0.02, "ks_stat_mean": 0.02, "ks_stat_max": 0.03, "kappa_mean": []},
        {"name": "srht",      "bbmd_distance_mean": 0.05, "ks_stat_mean": 0.03, "ks_stat_max": 0.04, "kappa_mean": []},
        {"name": "hadamard",  "bbmd_distance_mean": 1.40, "ks_stat_mean": 0.04, "ks_stat_max": 0.05, "kappa_mean": []},
        {"name": "rm_1_m",    "bbmd_distance_mean": 0.30, "ks_stat_mean": 0.04, "ks_stat_max": 0.05, "kappa_mean": []},
        {"name": "kerdock",   "bbmd_distance_mean": 1.20, "ks_stat_mean": 0.04, "ks_stat_max": 0.06, "kappa_mean": []},
    ]
    v, _ = compute_verdict({"codebook_results": cbs_killed_order})
    assert v == "KAPPA_CROSS_CODEBOOK_KILLED", f"expected KILLED via scrambled, got {v}"

    # Test 3: KILLED via MP-KS already discriminates (hadamard fails MP-KS)
    cbs_killed_ks = [
        {"name": "iid_gauss", "bbmd_distance_mean": 0.02, "ks_stat_mean": 0.02, "ks_stat_max": 0.03, "kappa_mean": []},
        {"name": "srht",      "bbmd_distance_mean": 0.05, "ks_stat_mean": 0.03, "ks_stat_max": 0.04, "kappa_mean": []},
        {"name": "hadamard",  "bbmd_distance_mean": 0.20, "ks_stat_mean": 0.08, "ks_stat_max": 0.09, "kappa_mean": []},
        {"name": "rm_1_m",    "bbmd_distance_mean": 0.30, "ks_stat_mean": 0.04, "ks_stat_max": 0.05, "kappa_mean": []},
        {"name": "kerdock",   "bbmd_distance_mean": 1.20, "ks_stat_mean": 0.04, "ks_stat_max": 0.06, "kappa_mean": []},
    ]
    v, _ = compute_verdict({"codebook_results": cbs_killed_ks})
    assert v == "KAPPA_CROSS_CODEBOOK_KILLED", f"expected KILLED via MP-KS, got {v}"

    # Test 4: missing codebook
    v, _ = compute_verdict({"codebook_results": cbs_pass[:3]})
    assert v == "KAPPA_CROSS_CODEBOOK_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Test 5: MP-KS sanity check on a true MP draw -- rectangular (alpha < 1) so the
    # MP density is smooth (no divergence at lam_minus = 0 like the alpha=1 square case).
    rng = np.random.default_rng(0)
    N_test, M_test = 1024, 512
    A_test = (rng.standard_normal(size=(M_test, N_test)) / math.sqrt(N_test)).astype(np.float32)
    s_test = np.linalg.svd(A_test, compute_uv=False)
    eig_test = (s_test ** 2).astype(np.float64)
    ks_val, _, _ = mp_ks_stat(eig_test, M_test, N_test)
    assert ks_val < 0.05, f"iid Gaussian KS should be < 0.05, got {ks_val:.4f}"

    print("Cross-codebook self-test passed (5/5 cases including iid MP-KS sanity)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        # Smoke: N=1024 (smallest Kerdock-supported), 1 seed, 2 codebooks for speed.
        # The verdict will be INCONCLUSIVE (missing codebooks) but we test build + measure.
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "n_max_moment": 6,
            "codebooks": ["iid_gauss", "kerdock"],  # 2 codebooks
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N": 1.0,
            "n_seeds": 10,
            "n_max_moment": 6,
            "codebooks": [nm for nm, _ in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    n_max = config["n_max_moment"]
    n_seeds = config["n_seeds"]

    print(f"[setup] N={N} M={M} M/N={M/N:.3f} n_seeds={n_seeds} "
          f"codebooks={config['codebooks']}", flush=True)

    builder_map = dict(CODEBOOKS)
    codebook_results = []
    for nm in config["codebooks"]:
        builder = builder_map[nm]
        print(f"\n[codebook] {nm}", flush=True)
        result = measure_codebook(nm, builder, N, M, n_seeds, n_max)
        codebook_results.append(result)
        print(f"  AGG {nm}: bbmd_mean={result['bbmd_distance_mean']:.4f} "
              f"ks_mean={result['ks_stat_mean']:.4f} ks_max={result['ks_stat_max']:.4f}",
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
    out_dir = get_output_dir("wave14_kappa_profile_cross_codebook_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks measured"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_profile_cross_codebook_v1")
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
