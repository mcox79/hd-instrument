"""Higher free cumulants kappa_n profile (n=2..8) on substrate's Kerdock spectrum.

Motivation
----------
Verdict 3 (KERDOCK_SPECTRUM_BULK_BOUNDED, 2026-05-23) established that the
substrate's spectral support stays inside MP -- the divergence is moment-based
only, not outlier-driven. Verdict 2 (FREE_CUMULANTS_DIVERGE = KERDOCK_OVERLAPS_NON_GAUSSIAN)
identified that the kappa_n profile up through n=4 deviates from MP.

This experiment extends the kappa_n profile through n=8, asking: does the
substrate-MP deviation grow / decay / saturate with n? That is the moment-
based fingerprint of how the substrate's algebraic structure (4-coset Kerdock
codebook, GF(2^t) Maiorana-McFarland quadratic form) writes itself onto the
free-probabilistic spectrum.

Scientific question
-------------------
Define the per-cumulant deviation
    delta_n(alpha) = kappa_n_empirical / c - 1,   c = M/N
where MP has kappa_n = c for all n. From Verdict 2 we know delta_n is
significantly non-zero for n in {2,3,4}. Three hypotheses for n>4:

  (a) GROWS: |delta_n| increases with n. Substrate-novel structure
      asymptotically dominates the spectrum at high moments. Mechanism:
      the codebook's combinatorial richness shows up at higher cumulants.
  (b) DECAYS: |delta_n| decreases with n. The substrate-MP deviation is
      bounded; high moments are MP-like. Mechanism: only low-order
      free-cumulants encode the algebraic structure.
  (c) SATURATES: |delta_n| plateaus at non-zero value. Substrate has a
      structural "kappa offset" -- a constant signature at all orders.

Method
------
Compute empirical spectral moments m_1..m_8 of (1/N) A^T A where A is M
rows from the Kerdock 4-coset codebook. Invert moments to free cumulants
kappa_1..kappa_8 using the moment-to-free-cumulant recursion (Mobius
inversion on the non-crossing partition lattice, Nica-Speicher 2006).

For n in {1..4} use the closed forms (verified in v1). For n in {5..8}
use the general recursion:

  m_n = sum over non-crossing partitions pi of {1..n} of
        product over blocks B in pi of kappa_|B|

Equivalently the Speicher recursion:
  m_n = sum_{k=1..n} kappa_k * sum_{(b_1,..,b_k) : sum b_i = n-k, b_i >= 0}
                              product m_{b_i}
which gives a triangular system: m_n = kappa_n + (polynomial in
kappa_1..kappa_{n-1} and m_1..m_{n-1}). We solve by direct iteration:
  kappa_n = m_n - sum over NON-trivial non-crossing partitions pi of {1..n}
                  product over blocks B in pi of kappa_|B|.

We enumerate non-crossing partitions of {1..n} for n <= 8 via the standard
recursive algorithm; this is O(C_n * n) where C_n is the n-th Catalan
number (C_8 = 1430). Trivial at this scale.

GPU
---
SVD of (M x N) Kerdock submatrix at N=4096 with alpha in {0.5, 1, 2, 4}
is the dominant cost. Run on torch.cuda for batched SVD across seeds, then
copy eigenvalues to CPU for moment computation.

Vertex: KAPPA_PROFILE_GROWS / KAPPA_PROFILE_DECAYS / KAPPA_PROFILE_SATURATES /
        KAPPA_PROFILE_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_kappa_n_profile_v1.md
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

# Import Kerdock codebook builder from v3 (proven substrate codebook)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
    _CUDA_OK = torch.cuda.is_available()
except ImportError:
    _TORCH_OK = False
    _CUDA_OK = False


# ---------------------------------------------------------------------------
# Non-crossing partitions of {1..n} (Catalan-many)
# ---------------------------------------------------------------------------

def _enumerate_ncp(n: int) -> Iterator[list[list[int]]]:
    """Yield all non-crossing partitions of {0,..,n-1} as lists of blocks.

    Uses the standard recursive characterization: a non-crossing partition pi
    of {0,..,n-1} is built by choosing the block B containing 0; B = {0=i_0 <
    i_1 < .. < i_k}, then independently choosing non-crossing partitions of
    each gap {i_j+1, .., i_{j+1}-1} (closed under {i_k+1,..,n-1}).

    For n=0 yields a single empty partition. C_n = Catalan(n).
    """
    if n == 0:
        yield []
        return

    # Choose the block containing 0: a strictly increasing subset of {0,..,n-1}
    # starting with 0. For each block, recurse on the gaps.

    def _rec(elements: list[int]) -> Iterator[list[list[int]]]:
        if not elements:
            yield []
            return
        first = elements[0]
        rest = elements[1:]
        # Block must contain `first`. Choose a subset of `rest` to also include.
        # The remaining elements are partitioned into "gaps" between consecutive
        # chosen elements (and after the last chosen element).
        # Use bitmask over rest indices.
        m = len(rest)
        for mask in range(1 << m):
            block = [first] + [rest[j] for j in range(m) if (mask >> j) & 1]
            # Identify the gaps. Block is sorted; rest elements not in block
            # fall into gaps between consecutive block elements.
            block_set = set(block)
            gap_groups: list[list[int]] = []
            current: list[int] = []
            block_pos = 0
            # walk through elements in order, splitting by block membership
            all_elems = [first] + rest
            for e in all_elems:
                if e in block_set:
                    if current:
                        gap_groups.append(current)
                        current = []
                else:
                    current.append(e)
            if current:
                gap_groups.append(current)

            # Recurse on each gap independently, then combine
            def combine_gaps(idx: int) -> Iterator[list[list[int]]]:
                if idx == len(gap_groups):
                    yield []
                    return
                for sub in _rec(gap_groups[idx]):
                    for rest_p in combine_gaps(idx + 1):
                        yield sub + rest_p

            for gap_part in combine_gaps(0):
                yield [block] + gap_part

    yield from _rec(list(range(n)))


@lru_cache(maxsize=10)
def _ncp_block_sizes(n: int) -> list[list[int]]:
    """Cache: list of block-size lists (sorted) for each non-crossing partition of {1..n}."""
    out = []
    for p in _enumerate_ncp(n):
        sizes = tuple(sorted(len(b) for b in p))
        out.append(list(sizes))
    return out


def moments_to_free_cumulants_general(moments: list[float]) -> list[float]:
    """Convert spectral moments m_1..m_n to free cumulants kappa_1..kappa_n for any n.

    Uses the recursive Mobius inversion on the non-crossing partition lattice:

      m_n = sum_{pi non-crossing partition of {1..n}}
              product_{B in pi} kappa_{|B|}

    The unique partition pi = {{1,2,..,n}} (the full block) contributes
    kappa_n. All other partitions contribute products of kappa_k for k < n.
    Rearranging:

      kappa_n = m_n - sum_{pi != {{1..n}}}
                       product_{B in pi} kappa_{|B|}.

    Solves the triangular system top-down: kappa_1, kappa_2, ..., kappa_n.
    """
    n_max = len(moments)
    if n_max < 1:
        return []

    kappa = [0.0] * (n_max + 1)  # 1-indexed; kappa[0] unused

    for n in range(1, n_max + 1):
        # Sum over all non-crossing partitions of {1..n} except the full block.
        partitions = _ncp_block_sizes(n)
        contribution = 0.0
        for sizes in partitions:
            if len(sizes) == 1:
                # Full block {1..n}: contributes kappa_n, which we're solving for
                continue
            prod = 1.0
            for s in sizes:
                prod *= kappa[s]
            contribution += prod

        kappa[n] = moments[n - 1] - contribution

    return kappa[1:]


def _closed_form_kappas(moments: list[float]) -> list[float]:
    """Sanity check: closed form for kappa_1..kappa_4."""
    if len(moments) < 1:
        return []
    m1 = moments[0]
    out = [m1]
    if len(moments) >= 2:
        m2 = moments[1]
        out.append(m2 - m1 * m1)
    if len(moments) >= 3:
        m3 = moments[2]
        out.append(m3 - 3.0 * m1 * m2 + 2.0 * m1 ** 3)
    if len(moments) >= 4:
        m4 = moments[3]
        out.append(m4 - 4.0 * m1 * m3 - 2.0 * m2 ** 2 + 10.0 * m1 ** 2 * m2 - 5.0 * m1 ** 4)
    return out


# ---------------------------------------------------------------------------
# Marchenko-Pastur reference
# ---------------------------------------------------------------------------

def mp_reference_moments(c: float, n_max: int) -> list[float]:
    """Marchenko-Pastur moments m_n = (1/n) sum_{k=1..n} C(n,k) C(n,k-1) c^k."""
    moments = []
    for n in range(1, n_max + 1):
        total = 0.0
        for k in range(1, n + 1):
            term = math.comb(n, k) * math.comb(n, k - 1) * (c ** k) / n
            total += term
        moments.append(total)
    return moments


def mp_reference_cumulants(c: float, n_max: int) -> list[float]:
    return [c] * n_max


# ---------------------------------------------------------------------------
# Spectrum extraction (GPU when available)
# ---------------------------------------------------------------------------

def get_kerdock_eigenvalues(N: int, M: int, seed: int, device: str) -> np.ndarray:
    """Build Kerdock 4-coset codebook, subsample M rows, return eigenvalues of (1/N) A^T A."""
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch

    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))  # (4N, N) bipolar
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A_t = cb[idx].float()
    A_norm = A_t / math.sqrt(N)  # (M, N)

    if device == "cuda" and _CUDA_OK:
        A_gpu = A_norm.to("cuda")
        # SVD on GPU; convert singular values to eigenvalues of A^T A
        try:
            _, s, _ = torch.linalg.svd(A_gpu, full_matrices=False)
        except RuntimeError as e:
            print(f"  [warn] GPU SVD failed ({e}); falling back to CPU", flush=True)
            _, s, _ = torch.linalg.svd(A_norm, full_matrices=False)
        eig = (s ** 2).cpu().numpy()
        del A_gpu
        torch.cuda.empty_cache()
    else:
        _, s, _ = torch.linalg.svd(A_norm, full_matrices=False)
        eig = (s ** 2).numpy()

    return eig


def spectral_moments(eigenvalues: np.ndarray, n_max: int) -> list[float]:
    """Empirical spectral moments m_n = (1/K) sum lambda_i^n."""
    return [float(np.mean(eigenvalues ** n)) for n in range(1, n_max + 1)]


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def _classify_growth(devs_by_n: list[float]) -> str:
    """Given |delta_n| for n=2..n_max, classify growth pattern.

    Use n=2..n_max to avoid n=1 (mean, always close to c by construction).
    Categories:
      GROWS: |delta_n| nondecreasing on average, with |delta_{n_max}| > 1.5 * |delta_2|
      DECAYS: |delta_n| nonincreasing on average, with |delta_{n_max}| < 0.5 * |delta_2|
      SATURATES: ratio in [0.5, 1.5] and all |delta_n| > 0.05
      UNCLEAR: not a clean fit (mixed or all near zero)
    """
    if not devs_by_n or len(devs_by_n) < 2:
        return "UNCLEAR"
    if all(d < 0.05 for d in devs_by_n):
        return "MP_LIKE"  # not substrate-novel; very rare given v1 result

    first = devs_by_n[0]
    last = devs_by_n[-1]
    if first < 1e-6:
        return "UNCLEAR"
    ratio = last / first

    if ratio > 1.5:
        return "GROWS"
    if ratio < 0.5:
        return "DECAYS"
    if 0.5 <= ratio <= 1.5:
        return "SATURATES"
    return "UNCLEAR"


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Aggregate across alpha cells; verdict reflects dominant growth pattern."""
    if not summary.get("cells"):
        return ("KAPPA_PROFILE_INCONCLUSIVE", "No cells computed.")

    per_cell = []
    for cell in summary["cells"]:
        kappas = cell.get("kappa_mean", [])
        c_ref = cell.get("alpha")
        if not kappas or c_ref is None or c_ref <= 0 or len(kappas) < 4:
            continue
        # Absolute deviations |kappa_n - c| / c for n=2..n_max
        devs = [abs(kappas[n - 1] / c_ref - 1.0) for n in range(2, len(kappas) + 1)]
        cell["dev_abs"] = devs
        cell["growth_class"] = _classify_growth(devs)
        per_cell.append(cell["growth_class"])

    if not per_cell:
        return ("KAPPA_PROFILE_INCONCLUSIVE", "No valid cells.")

    grows = per_cell.count("GROWS")
    decays = per_cell.count("DECAYS")
    saturates = per_cell.count("SATURATES")
    mp_like = per_cell.count("MP_LIKE")
    unclear = per_cell.count("UNCLEAR")
    n = len(per_cell)

    # Majority rule
    dom_count = max(grows, decays, saturates)
    if grows == dom_count and grows >= max(1, n // 2):
        return (
            "KAPPA_PROFILE_GROWS",
            f"Higher free cumulants kappa_n diverge from MP with INCREASING magnitude in n. "
            f"{grows}/{n} alpha cells show |kappa_n/c - 1| growing with n through n=8. "
            f"Substrate-novel finding: the Kerdock algebraic structure's signature on the "
            f"free-probabilistic spectrum becomes more prominent at higher cumulants. "
            f"Per-cell classes: GROWS={grows} DECAYS={decays} SATURATES={saturates} "
            f"MP_LIKE={mp_like} UNCLEAR={unclear}.",
        )
    if decays == dom_count and decays >= max(1, n // 2):
        return (
            "KAPPA_PROFILE_DECAYS",
            f"Higher free cumulants kappa_n diverge from MP at n=2..4 but DECAY toward MP "
            f"as n increases through n=8. {decays}/{n} alpha cells show this pattern. "
            f"Substrate-novel structure encodes itself in LOW-ORDER cumulants; high moments "
            f"are essentially MP. Per-cell classes: GROWS={grows} DECAYS={decays} "
            f"SATURATES={saturates} MP_LIKE={mp_like} UNCLEAR={unclear}.",
        )
    if saturates == dom_count and saturates >= max(1, n // 2):
        return (
            "KAPPA_PROFILE_SATURATES",
            f"Higher free cumulants kappa_n plateau at a substrate-novel constant offset "
            f"from MP. {saturates}/{n} alpha cells show |kappa_n/c - 1| approximately "
            f"constant in n through n=8. The substrate's algebraic signature is an "
            f"all-orders constant kappa shift. Per-cell classes: GROWS={grows} DECAYS={decays} "
            f"SATURATES={saturates} MP_LIKE={mp_like} UNCLEAR={unclear}.",
        )

    return (
        "KAPPA_PROFILE_INCONCLUSIVE",
        f"No dominant growth pattern across alpha cells. Per-cell classes: GROWS={grows} "
        f"DECAYS={decays} SATURATES={saturates} MP_LIKE={mp_like} UNCLEAR={unclear}.",
    )


def self_test() -> None:
    """Verify (1) NCP enumeration counts = Catalan, (2) inversion math matches closed
    forms for n<=4, (3) MP cumulants come out exactly equal to c for n=1..8, (4) verdict
    classifier handles edge cases."""

    # Test 1: NCP counts = Catalan numbers
    catalan = [1, 1, 2, 5, 14, 42, 132, 429, 1430]
    for n in range(0, 8):
        count = sum(1 for _ in _enumerate_ncp(n))
        assert count == catalan[n], f"NCP({n}) = {count}, expected {catalan[n]}"

    # Test 2: closed form == general for n<=4 on a random moment list
    rng = np.random.default_rng(0)
    moms = rng.uniform(0.1, 2.0, size=4).tolist()
    k_closed = _closed_form_kappas(moms)
    k_general = moments_to_free_cumulants_general(moms)
    for i in range(4):
        assert abs(k_closed[i] - k_general[i]) < 1e-9, (
            f"n={i+1}: closed={k_closed[i]}, general={k_general[i]}"
        )

    # Test 3: MP(c) -> all kappa_n = c for n=1..8
    for c in [0.5, 1.0, 2.0]:
        moms = mp_reference_moments(c, 8)
        kappas = moments_to_free_cumulants_general(moms)
        for n, k in enumerate(kappas, start=1):
            assert abs(k - c) < 1e-7, f"MP({c}): kappa_{n}={k}, expected {c}"

    # Test 4: verdict GROWS
    summary = {"cells": [
        {"alpha": 1.0, "kappa_mean": [1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0, 2.3]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KAPPA_PROFILE_GROWS", f"expected GROWS got {v}"

    # Test 5: verdict DECAYS
    summary = {"cells": [
        {"alpha": 1.0, "kappa_mean": [1.0, 1.5, 1.3, 1.15, 1.08, 1.04, 1.02, 1.01]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KAPPA_PROFILE_DECAYS", f"expected DECAYS got {v}"

    # Test 6: verdict SATURATES
    summary = {"cells": [
        {"alpha": 1.0, "kappa_mean": [1.0, 1.2, 1.18, 1.22, 1.19, 1.21, 1.18, 1.20]},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "KAPPA_PROFILE_SATURATES", f"expected SATURATES got {v}"

    # Test 7: verdict INCONCLUSIVE on empty
    v, _ = compute_verdict({"cells": []})
    assert v == "KAPPA_PROFILE_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("kappa_n profile self-test passed (NCP counts, closed-form match, MP exact, verdict branches)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N_list": [0.5, 1.0],
            "n_seeds": 2,
            "n_max_moment": 6,  # n=6 keeps smoke cheap; full uses 8
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.5, 1.0, 2.0, 4.0],
            "n_seeds": 5,
            "n_max_moment": 8,
        }

    N = config["N"]
    n_max = config["n_max_moment"]
    device = "cuda" if (_CUDA_OK and not smoke) else "cpu"
    print(f"[device] {device} (cuda_available={_CUDA_OK})", flush=True)

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N={4*N}, skipping", flush=True)
            continue

        c_ref = float(alpha)
        print(f"\n[alpha={alpha:.2f}] N={N} M={M} c_ref={c_ref:.4f}", flush=True)

        kappa_per_seed = []
        moms_per_seed = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            eigenvalues = get_kerdock_eigenvalues(N, M, seed=seed_val, device=device)
            moms = spectral_moments(eigenvalues, n_max)
            kappas = moments_to_free_cumulants_general(moms)
            kappa_per_seed.append(kappas)
            moms_per_seed.append(moms)
            print(
                f"  seed={seed} m={[f'{m:.3f}' for m in moms]} "
                f"kappa={[f'{k:+.3f}' for k in kappas]}",
                flush=True,
            )

        kappa_arr = np.array(kappa_per_seed)
        kappa_mean = kappa_arr.mean(axis=0).tolist()
        kappa_std = kappa_arr.std(axis=0).tolist()
        moms_arr = np.array(moms_per_seed)
        moms_mean = moms_arr.mean(axis=0).tolist()

        kappa_mp = mp_reference_cumulants(c_ref, n_max)
        moms_mp = mp_reference_moments(c_ref, n_max)

        dev_per_n = [
            (kappa_mean[i] / c_ref - 1.0) if c_ref > 0 else 0.0
            for i in range(n_max)
        ]

        cell = {
            "alpha": float(alpha),
            "N": N, "M": M, "c_ref": c_ref,
            "kappa_mean": kappa_mean,
            "kappa_std": kappa_std,
            "kappa_mp": kappa_mp,
            "moments_mean": moms_mean,
            "moments_mp": moms_mp,
            "kappa_dev_relative": dev_per_n,
        }
        cells.append(cell)

        print(
            f"  AGGREGATE alpha={alpha:.2f}: dev_rel n=1..{n_max} = "
            f"{[f'{d:+.3f}' for d in dev_per_n]}",
            flush=True,
        )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
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
    out_dir = get_output_dir("wave14_kappa_n_profile_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_n_profile_v1")
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
