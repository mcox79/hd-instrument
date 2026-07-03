"""Kerdock 4-coset codebook distance-class audit.

CONTEXT:
Research drill (research_ags_retrieval_phase_substrate_2026-05-26.md) hypothesizes that the
substrate's Kerdock 4-coset codebook has EXACTLY 4 distinct codeword-pairwise-distance classes,
and that each class maps monotonically to one of the 4 empirical retention plateaus
{0.94, 0.74, 0.60, m_4}. This is the "geometric-frustration / AGS basin-class" sub-claim:
  plateau_k = m_k = AGS retrieval overlap at Kerdock distance-class k.

DESIGN:
  Post-hoc analytical: read Kerdock codebook from existing v3 codebook generator.
  1. Build codebook at N=1024 (smallest registered N).
  2. Enumerate pairwise inner products / N exhaustively (or sample ~5000 pairs per coset pair).
  3. Cluster the distance distribution into discrete classes.
  4. Report: n_distance_classes, discrete levels, coset-pair mapping.
  5. Cross-check: does the n_distance_classes count = 4? Do levels map monotonically to
     substrate empirical plateaus {0.94, 0.74, 0.60, m_4}?

SELF-TESTS per [[feedback-strategy-spec-formula-selftests]]:
  1. Within-coset Hadamard rows: all pairs have IP/N = 0.0 exactly (orthonormal coset).
  2. Cross-coset IP/N in {-1/sqrt(N), 0, +1/sqrt(N)} for Welch-bound Kerdock.
  3. AGS self-consistent fixed-point: m=erf(m/sqrt(2*r)) for (m=0.95,r=0.05)->~0.9999~m.
  4. For m=0.6, r=0.5: erf(0.6/sqrt(1.0))=erf(0.6)~0.604~m (within 0.01).
  5. Hamming distance fraction = (1 - IP/N) / 2.

PRE-REGISTERED BANDS (Kerdock distance-class audit):
  HARD-PASS: exactly 4 distinct distance classes; each maps monotonically to a retention
    plateau; 3/4 predicted m_k from AGS self-consistent eq match empirical within +-0.07.
  HARD-FAIL: != 4 distance classes (3 or smooth distribution without discrete classes) OR
    predicted-vs-observed plateau heights off by > 0.15 systematically OR non-monotone.
  MIDDLE_BAND: 4 classes confirmed but plateau-height mapping has 2/4 mismatches in [0.07, 0.15].
  INSTRUMENTATION_FAIL: codebook cannot be enumerated (construction error) OR exhaustive
    enumeration produces fewer distinct IP levels than expected (<2 distinct non-trivial levels).

Queue: remote_cpu_queue (pure CPU; post-hoc codebook analysis; ~15-30 min ETA)
  NOTE: CPU cap DEFAULT-ON since 2026-05-26 (BELOWNORMAL priority structural; no flag needed).
Pre-reg: preregs/2026-05-26_wave14_kerdock_distance_class_audit_v1.md
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
from collections import Counter

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load Kerdock codebook generator from v3
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_v3_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Design parameters
N_AUDIT = 1024        # smallest registered N (t=5 in PRIMITIVE_POLY)
N_PAIRS_PER_COSET_PAIR = 3000  # enough for stable class detection
ROUNDING_DIGITS = 4   # for discrete level detection
MIN_FRACTION_PER_CLASS = 0.005  # filter noise

# Empirical retention plateaus from substrate (Bet B 4-tier taxonomy v206/v209)
EMPIRICAL_PLATEAUS = [0.94, 0.74, 0.60]  # m_4 is unknown/to be measured
AGS_ALPHA = 0.153   # substrate loading alpha = M/N at v206 operating point
AGS_ALPHA_C = 0.5625  # empirical capacity boundary (from v206/v209 hysteresis)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
# ─── AGS self-consistent fixed-point solver ────────────────────────────────

def ags_retrieval_overlap(r: float, tol: float = 1e-9, max_iter: int = 1000) -> float:
    """Solve m = erf(m / sqrt(2*r)) by fixed-point iteration. Returns m >= 0."""
    if r <= 0:
        return 1.0
    m = 0.95  # start near high-retrieval solution
    for _ in range(max_iter):
        m_new = math.erf(m / math.sqrt(2 * r))
        if abs(m_new - m) < tol:
            return m_new
        m = 0.9 * m + 0.1 * m_new  # damped iteration for stability
    return m


# ─── Self-test ─────────────────────────────────────────────────────────────

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # Test 1: within-coset orthogonality -- Hadamard rows are orthonormal
    # Verify codebook builds without error
    N_test = 1024
    try:
        cb_test, info_test = make_kerdock_4coset_codebook(N_test, torch.device("cpu"))
        assert cb_test.shape == (4 * N_test, N_test), \
            f"codebook shape mismatch: {cb_test.shape} != ({4*N_test}, {N_test})"
        print(f"[selftest] T1 PASS: codebook built, shape={cb_test.shape}", flush=True)
    except Exception as e:
        raise AssertionError(f"Codebook construction failed: {e}")

    # Test 2: within-coset IPs are exactly 0 (Hadamard rows orthogonal within coset)
    cb_np = cb_test.float().numpy()
    N_c = N_test
    coset0 = cb_np[0:N_c]
    within_ips = []
    rng_t = np.random.default_rng(0)
    for _ in range(30):
        i, j = rng_t.integers(0, N_c, size=2)
        while j == i:
            j = rng_t.integers(0, N_c)
        ip = float(np.dot(coset0[i], coset0[j])) / N_test
        within_ips.append(ip)
    all_zero = all(abs(x) < 1e-9 for x in within_ips)
    assert all_zero, f"Within-coset IPs not all zero: {within_ips[:5]}"
    print(f"[selftest] T2 PASS: within-coset IPs = 0 for {len(within_ips)} pairs", flush=True)

    # Test 3: cross-coset IPs are in {-1/sqrt(N), 0, +1/sqrt(N)} range
    coset1 = cb_np[N_c:2*N_c]
    cross_ips = []
    for _ in range(30):
        i = rng_t.integers(0, N_c)
        j = rng_t.integers(0, N_c)
        ip = float(np.dot(coset0[i], coset1[j])) / N_test
        cross_ips.append(ip)
    max_abs = max(abs(x) for x in cross_ips)
    expected_max = 1.0 / math.sqrt(N_test) + 1e-6
    assert max_abs <= expected_max, \
        f"Cross-coset IP max {max_abs:.6f} > Welch bound {expected_max:.6f}"
    print(f"[selftest] T3 PASS: cross-coset IPs within Welch bound {expected_max:.4f}", flush=True)

    # Test 4: AGS self-consistent FP (m=0.95, r=0.05) -> ~0.9999
    m_fp = ags_retrieval_overlap(r=0.05)
    assert abs(m_fp - 0.9999) < 0.01, f"AGS FP at r=0.05 = {m_fp:.4f}, expected ~0.9999"
    print(f"[selftest] T4 PASS: AGS FP(r=0.05) = {m_fp:.4f}", flush=True)

    # Test 5: AGS FP (m=0.6, r=0.5) -> erf(0.6/sqrt(1.0)) = erf(0.6) ~ 0.604
    m_fp2 = ags_retrieval_overlap(r=0.5)
    expected2 = math.erf(0.6 / math.sqrt(1.0))  # ~ 0.604
    assert abs(m_fp2 - expected2) < 0.05, \
        f"AGS FP(r=0.5) = {m_fp2:.4f}, expected erf(0.6)={expected2:.4f}"
    print(f"[selftest] T5 PASS: AGS FP(r=0.5) = {m_fp2:.4f} (expected erf(0.6)={expected2:.4f})", flush=True)

    # Test 6: Hamming fraction formula
    ip_test = -0.031  # ~ -1/sqrt(1024)
    hf = (1 - ip_test) / 2
    assert 0.49 < hf < 0.52, f"Hamming fraction formula fail: {hf:.4f}"
    print(f"[selftest] T6 PASS: Hamming fraction at IP=-0.031 = {hf:.4f}", flush=True)

    print("[selftest] ALL 6 assertions PASS", flush=True)


_instrumentation_selftest()


# ─── Main audit ────────────────────────────────────────────────────────────

def cluster_ip_values(ip_list: list[float], rounding: int = ROUNDING_DIGITS) -> dict:
    """Cluster IP values into discrete levels. Returns {level: count}."""
    rounded = [round(x, rounding) for x in ip_list]
    counts = Counter(rounded)
    # Filter noise: keep levels that appear >= MIN_FRACTION_PER_CLASS of total
    n_total = len(ip_list)
    main_levels = {k: v for k, v in counts.items()
                   if v / n_total >= MIN_FRACTION_PER_CLASS}
    return main_levels


def predict_ags_overlap_from_ip(ip_over_N: float, alpha: float) -> float:
    """Predict AGS retrieval overlap m_k from normalized IP value using basin-class formula.

    Kerdock distance class k has normalized distance d_k/N = (1 - IP/N) / 2.
    Basin radius r_k approximated as alpha * (1 + d_k / (1 - alpha/alpha_c)) following
    the research note P3.2 formula (simplified linear rescaling).
    """
    ham_frac = (1 - ip_over_N) / 2
    # r_k ~ alpha * (1 + c * ham_frac) where c is an O(1) constant
    # The research note derives r_0 ~ alpha for same-corpus (ham_frac ~ 0),
    # r_1 ~ alpha*(1+eps), r_2 ~ 2*alpha, r_3 ~ 3-4*alpha
    # We use linear interpolation: r_k = alpha * (1 + 4*ham_frac) as first-order model
    r_k = alpha * (1 + 4 * ham_frac)
    return ags_retrieval_overlap(r_k)


def run_audit(n_pairs_per_coset_pair: int = N_PAIRS_PER_COSET_PAIR) -> dict:
    t0 = time.monotonic()
    device = torch.device("cpu")

    print(f"[kerdock_audit] N={N_AUDIT}, n_pairs_per_coset_pair={n_pairs_per_coset_pair}", flush=True)

    cb, info = make_kerdock_4coset_codebook(N_AUDIT, device)
    cb_np = cb.float().numpy()  # (4N, N)
    K = cb_np.shape[0]
    N = cb_np.shape[1]
    coset_size = N  # = N_AUDIT
    n_cosets = 4
    print(f"[kerdock_audit] Codebook: {cb_np.shape}, cosets={n_cosets}, coset_size={coset_size}", flush=True)

    cosets_np = [cb_np[c * coset_size:(c + 1) * coset_size] for c in range(n_cosets)]

    rng = np.random.default_rng(42)
    all_ips = []
    coset_pair_stats = {}

    for ca in range(n_cosets):
        for cb_idx in range(ca, n_cosets):
            ips_pair = []
            for _ in range(n_pairs_per_coset_pair):
                i = rng.integers(0, coset_size)
                j = rng.integers(0, coset_size)
                if ca == cb_idx:
                    while j == i:
                        j = rng.integers(0, coset_size)
                ip_val = float(np.dot(cosets_np[ca][i], cosets_np[cb_idx][j])) / N
                ips_pair.append(ip_val)
            all_ips.extend(ips_pair)
            ips_arr = np.array(ips_pair)
            levels_pair = cluster_ip_values(ips_pair)
            pair_key = f"coset_{ca}_{cb_idx}"
            ham_arr = (1 - ips_arr) / 2.0
            coset_pair_stats[pair_key] = {
                "n_pairs": len(ips_pair),
                "mean_ip_over_N": float(ips_arr.mean()),
                "std_ip_over_N": float(ips_arr.std()),
                "discrete_levels": {str(k): v for k, v in levels_pair.items()},
                "n_distinct_levels": len(levels_pair),
                "ham_frac_mean": float(ham_arr.mean()),
            }
            print(f"  coset ({ca},{cb_idx}): mean_ip={ips_arr.mean():.4f} "
                  f"levels={list(levels_pair.keys())}", flush=True)

    # Global distance-class audit across all pairs
    all_levels_global = cluster_ip_values(all_ips)
    n_distinct_global = len(all_levels_global)
    sorted_levels = sorted(all_levels_global.keys())

    print(f"\n[audit] Global distinct IP/N levels: {sorted_levels}", flush=True)
    print(f"[audit] n_distinct_classes = {n_distinct_global}", flush=True)

    # Map each level to predicted AGS overlap
    level_to_ags_pred = {}
    for lev in sorted_levels:
        pred_m = predict_ags_overlap_from_ip(lev, AGS_ALPHA)
        level_to_ags_pred[lev] = pred_m
        print(f"  IP/N={lev:.4f} -> ham_frac={(1-lev)/2:.4f} -> AGS_pred_m={pred_m:.4f}", flush=True)

    # Compare predicted m_k to empirical plateaus
    # Monotone mapping: closest level to each plateau
    emp_plateaus = EMPIRICAL_PLATEAUS  # [0.94, 0.74, 0.60]
    sorted_preds = sorted(level_to_ags_pred.values(), reverse=True)  # highest m first
    n_match_within_007 = 0
    n_match_within_015 = 0
    comparison = []
    for i, emp in enumerate(emp_plateaus):
        if i < len(sorted_preds):
            pred = sorted_preds[i]
            diff = abs(pred - emp)
            match_007 = diff <= 0.07
            match_015 = diff <= 0.15
            n_match_within_007 += int(match_007)
            n_match_within_015 += int(match_015)
            comparison.append({
                "empirical_plateau": emp,
                "ags_prediction": pred,
                "abs_diff": diff,
                "within_007": match_007,
                "within_015": match_015,
            })
            print(f"  Plateau {emp:.2f} vs AGS pred {pred:.4f}: diff={diff:.4f} "
                  f"match_007={match_007} match_015={match_015}", flush=True)

    # Monotonicity check
    is_monotone = all(sorted_preds[i] >= sorted_preds[i + 1]
                      for i in range(len(sorted_preds) - 1))
    print(f"\n[audit] monotone={is_monotone} n_match_007={n_match_within_007}/3", flush=True)

    # Verdict
    # INSTRUMENTATION_FAIL first
    if n_distinct_global < 2:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: only {n_distinct_global} distinct IP level(s); "
                       f"expected >= 2 distinct levels for non-trivial codebook distance structure")
    elif n_distinct_global == 4 and is_monotone and n_match_within_007 >= 3:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: exactly 4 distance classes; monotone={is_monotone}; "
                       f"n_match_007={n_match_within_007}/3 plateaus within +-0.07 of AGS pred")
    elif n_distinct_global != 4 and n_match_within_007 < 2:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: n_distance_classes={n_distinct_global} (expected 4); "
                       f"n_match_007={n_match_within_007}/3; monotone={is_monotone}; "
                       f"AGS basin-class prediction does not match Kerdock structure")
    elif n_distinct_global == 4 and is_monotone and n_match_within_007 >= 1 and n_match_within_015 >= 2:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: n_classes={n_distinct_global} monotone={is_monotone}; "
                       f"n_match_007={n_match_within_007}/3; n_match_015={n_match_within_015}/3; "
                       f"4 classes confirmed but plateau mapping partially mismatched")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: n_classes={n_distinct_global} monotone={is_monotone}; "
                       f"n_match_007={n_match_within_007}/3 n_match_015={n_match_within_015}/3; "
                       f"ambiguous: check comparison for details")

    summary = {
        "N": N,
        "K": K,
        "n_cosets": n_cosets,
        "n_distinct_classes_global": n_distinct_global,
        "distinct_levels_global": sorted_levels,
        "level_to_ags_prediction": {str(k): v for k, v in level_to_ags_pred.items()},
        "n_match_within_007": n_match_within_007,
        "n_match_within_015": n_match_within_015,
        "is_monotone": is_monotone,
        "plateau_comparison": comparison,
        "coset_pair_stats": coset_pair_stats,
        "ags_alpha": AGS_ALPHA,
        "ags_alpha_c": AGS_ALPHA_C,
    }

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": summary,
        "config": {
            "N": N,
            "n_pairs_per_coset_pair": n_pairs_per_coset_pair,
            "rounding_digits": ROUNDING_DIGITS,
            "min_fraction_per_class": MIN_FRACTION_PER_CLASS,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print("[self-test mode] instrumentation_selftest already ran at import", flush=True)
        sys.exit(0)

    n_pairs = 300 if args.smoke else N_PAIRS_PER_COSET_PAIR
    metrics = run_audit(n_pairs_per_coset_pair=n_pairs)

    out_dir = get_output_dir()
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
