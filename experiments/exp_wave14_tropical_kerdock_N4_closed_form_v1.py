"""Tropical R2: analytical N=4 closed-form margin certificate for 4-coset Kerdock.

Motivation
----------
F-14 rescue path: prior wave14 tropical-margin probes on Kerdock (N=1024,
N=4096) used empirical Monte Carlo to estimate the tropical margin. R2 is
the analytical-closed-form rescue: derive the tropical max-plus margin for
the N=4 4-coset Kerdock codebook in closed form, then VERIFY against an
exhaustive enumeration. If the closed form matches enumeration to floating-
point precision, R2 is a structurally CONFIRMED route for the F-14 row.

Scientific question
-------------------
For N=4 Kerdock 4-coset codebook, is the tropical max-plus inner-product
margin
    gamma_trop = min_{c != c'} ( max_i (c_i + c'_i) - max_i (c_i' + c_i) )
analytically computable from the algebraic structure of the codebook, and
does the closed form agree with exhaustive enumeration?

Vertices: TROP_R2_CLOSED_FORM_VERIFIED / TROP_R2_DISAGREE / TROP_R2_INCONCLUSIVE.

Pre-reg: preregs/2026-05-24_wave14_tropical_kerdock_N4_closed_form_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, importlib.util, json, math, os, time
from pathlib import Path
from itertools import combinations

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def make_n4_kerdock_codebook() -> np.ndarray:
    """Construct the N=4 4-coset Kerdock codebook by enumeration.

    For N=4, the 4-coset Kerdock codebook over GF(2) has 4N = 16 codewords.
    Since the substrate uses bipolar +/-1 entries and N=4 is small enough,
    we enumerate the N=4 Sylvester Hadamard rows union with sign-shifted cosets:

    Coset 0: H (Hadamard rows of N=4)              -> 4 codewords
    Coset 1: H with column 0 negated               -> 4 codewords
    Coset 2: H with column 1 negated               -> 4 codewords
    Coset 3: H with columns 0+1 negated            -> 4 codewords

    Total = 16 codewords in {+1, -1}^4.
    """
    H4 = np.array([
        [ 1,  1,  1,  1],
        [ 1, -1,  1, -1],
        [ 1,  1, -1, -1],
        [ 1, -1, -1,  1],
    ], dtype=np.float32)
    cosets = []
    for s0, s1 in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        sign_diag = np.array([s0, s1, 1, 1], dtype=np.float32)
        cosets.append(H4 * sign_diag[np.newaxis, :])
    return np.concatenate(cosets, axis=0)  # (16, 4)


def tropical_pair_margin(c: np.ndarray, c_prime: np.ndarray) -> float:
    """Tropical inner-product (max-plus) score difference between c and c'.

    score(c, c) = max_i (c_i + c_i) = max_i 2 c_i
    score(c, c') = max_i (c_i + c'_i)
    margin = score(c, c) - score(c, c')
    """
    self_score = float(np.max(c + c))
    cross_score = float(np.max(c + c_prime))
    return self_score - cross_score


def tropical_margin_exhaustive(codebook: np.ndarray) -> tuple[float, dict]:
    """Compute min pairwise tropical margin over all codeword pairs."""
    K = codebook.shape[0]
    min_margin = float("inf")
    arg_pair = (-1, -1)
    n_pairs = 0
    margins = []
    for i, j in combinations(range(K), 2):
        m = tropical_pair_margin(codebook[i], codebook[j])
        margins.append(m)
        n_pairs += 1
        if m < min_margin:
            min_margin = m
            arg_pair = (i, j)
    return min_margin, {"min": min_margin, "arg": arg_pair, "n_pairs": n_pairs,
                         "median": float(np.median(margins)) if margins else 0.0}


# Analytical closed-form prediction
#
# For bipolar c, c' in {-1, +1}^N (no constraint c != -c'):
#   self_score(c) = max_i(c_i + c_i) = max_i 2 c_i
#                 = 2 if any c_i = +1, else -2 (only the all-negative codeword)
#   cross_score(c, c') = max_i(c_i + c'_i)
#                      = 2 if c and c' agree on at least one position with both = +1
#                      = 0 if they share no double-+1 position but share some +1/-1 or -1/+1
#                      = -2 if both are all-negative (c = c' = -1's)
#   margin(c, c') = self_score(c) - cross_score(c, c')
#
# The 4-coset Kerdock at N=4 has 16 codewords, closed under negation. It contains:
#   - The all-positive codeword [+1,+1,+1,+1] (self_score = 2)
#   - The all-negative codeword [-1,-1,-1,-1] (self_score = -2)
#   - 14 mixed-sign codewords (self_score = 2)
#
# The minimum margin is achieved when c = [-1,-1,-1,-1] (self_score = -2) and
# c' has at least one +1 (so cross_score = 0), giving margin = -2 - 0 = -2.
#
# Closed form: min_margin = -2 for the N=4 4-coset Kerdock codebook.
def closed_form_min_margin(N: int = 4) -> float:
    """Closed-form prediction for the min pairwise tropical margin of the
    N=4 4-coset Kerdock codebook.

    Derivation (see comment block above):
      min over (c != c') of (max_i(c_i + c_i) - max_i(c_i + c'_i))
      is achieved at c = all-negative, c' = any codeword with a +1.
      = max_i(-2) - max_i(c_i + c'_i)
      = -2 - 0 = -2.
    """
    return -2.0


def self_test() -> None:
    cb = make_n4_kerdock_codebook()
    assert cb.shape == (16, 4), f"expected (16,4), got {cb.shape}"
    # All entries +/-1
    assert np.all((cb == 1.0) | (cb == -1.0))
    # Closed under negation
    cb_set = set(tuple(c) for c in cb.tolist())
    for c in cb:
        assert tuple((-c).tolist()) in cb_set
    print("  cell 1: N=4 codebook shape (16,4), bipolar, neg-closed — OK", flush=True)

    # Pair margin sanity
    c = np.array([1, 1, 1, 1], dtype=np.float32)
    cn = -c
    assert tropical_pair_margin(c, cn) == 2.0
    co = np.array([1, -1, 1, -1], dtype=np.float32)
    # max(c+co) = max(2, 0, 2, 0) = 2; self=2; margin=0
    assert tropical_pair_margin(c, co) == 0.0
    print("  cell 2: pair-margin sanity OK", flush=True)

    m_emp, meta = tropical_margin_exhaustive(cb)
    m_cf = closed_form_min_margin(4)
    diff = abs(m_emp - m_cf)
    print(f"  cell 3: empirical_min={m_emp}, closed_form={m_cf}, diff={diff}", flush=True)
    assert diff < 1e-6, f"closed-form disagrees with enumeration by {diff}"
    print("self-tests passed", flush=True)


def compute_verdict(summary: dict) -> tuple[str, str]:
    diff = summary.get("diff_closed_vs_emp", float("inf"))
    if diff < 1e-6:
        return ("TROP_R2_CLOSED_FORM_VERIFIED",
                f"Closed-form N=4 tropical margin matches enumeration to {diff:.2e}. "
                f"R2 is a structurally confirmed rescue route for the F-14 row.")
    if diff > 1e-3:
        return ("TROP_R2_DISAGREE",
                f"Closed-form differs from enumeration by {diff:.4f}. "
                f"Closed-form derivation is wrong; R2 rescue route fails.")
    return ("TROP_R2_INCONCLUSIVE",
            f"Closed-form differs from enumeration by {diff:.6f}; ambiguous regime.")


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    cb = make_n4_kerdock_codebook()
    m_emp, meta = tropical_margin_exhaustive(cb)
    m_cf = closed_form_min_margin(4)
    diff = abs(m_emp - m_cf)
    print(f"  empirical min margin: {m_emp}", flush=True)
    print(f"  closed-form min margin: {m_cf}", flush=True)
    print(f"  diff: {diff}", flush=True)
    print(f"  meta: {meta}", flush=True)

    # Also enumerate pair-margin distribution for context
    K = cb.shape[0]
    margins = []
    for i, j in combinations(range(K), 2):
        margins.append(tropical_pair_margin(cb[i], cb[j]))
    margins = np.array(margins)

    summary = {
        "diff_closed_vs_emp": diff,
        "empirical_min_margin": float(m_emp),
        "closed_form_min_margin": float(m_cf),
        "pair_count": int(len(margins)),
        "margin_histogram": {
            "values_unique": sorted(set(float(x) for x in margins)),
            "counts_per_value": {float(v): int(np.sum(margins == v)) for v in set(margins)},
        },
        "meta": meta,
    }
    cfg = {"N": 4, "K": int(K), "mode": "smoke" if smoke else "full"}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def get_output_dir(name: str) -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    self_test()
    out_dir = get_output_dir("wave14_tropical_kerdock_N4_closed_form_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test()
    out_dir = get_output_dir("wave14_tropical_kerdock_N4_closed_form_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
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
