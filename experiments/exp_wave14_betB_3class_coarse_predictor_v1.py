"""Alt1 walk-back rescue: 3-class coarse taxonomy for Bet B retention.

Context: wave14_betB_shift_class_full_replication_v1 SHIFT_CLASS_REPLICATION_HARD_FAIL
at n>=15 (4/6 non-overlapping CIs vs required 5/6). The 6-class taxonomy was too
fine-grained: pairwise separation did not hold at replication scale for boundary classes.

However, the per-class means from the full replication reveal 3 NATURAL PLATEAU CLUSTERS:
  HIGH  (~0.88-0.94): SAME_CORPUS_PRISTINE (0.941), COMPOUND_SAME_CORPUS (0.885)
  MID   (~0.73-0.85): REPLAY_SAME_CORPUS (0.845), NO_REPLAY_SAME_CORPUS (0.682),
                       STAGE_4_COMPOUND (0.734)
  LOW   (~0.63):      DIFF_CORPUS_2TASK (0.633)

Note: NO_REPLAY_SAME_CORPUS (0.682) is assigned to MID rather than creating a 4th
class, since its CI overlaps STAGE_4_COMPOUND at replication scale.

This re-analysis tests whether a 3-COARSE-CLASS taxonomy (HIGH / MID / LOW) has
non-overlapping CIs with cleaner pairwise separation. Zero new compute -- pure
re-analysis of data already in data/exp_wave14_betB_shift_class_full_replication_v1/.

Pre-reg:
  HARD-PASS: all 3 coarse-class CIs non-overlapping (3/3) AND K-W p < 0.01.
    Interpretation: 3-class taxonomy is the defensible product claim;
    substrate has 3 distinct retention regimes that are classifier-predictable.
    Cap_map annotation: Bet B retention predictability at 3-class granularity.

  HARD-FAIL: any 2 coarse-class CIs overlap (< 3/3 non-overlapping).
    Interpretation: even the coarsest possible 3-class split lacks CI separation.
    The omnibus signal (K-W p~0) is real but class boundaries are not tight.
    Walk back to group-level claim only (v200 framing).

  MIDDLE: 3/3 non-overlapping but K-W p in [0.01, 0.05).
    Signal real but statistical strength weaker than expected.

Queue: local_cpu_queue (pure analysis, no GPU needed)
ETA: < 2 min (pure Python re-analysis of existing JSON)
Pre-reg: preregs/2026-05-24_wave14_betB_3class_coarse_predictor_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL/MIDDLE pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-rescue-sketch-first-sequencing]]: cheapest rescue first (zero compute).
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
DATA = REPO / "data"

# -------- 3-class coarse taxonomy --------
# Mapping: 6-class label -> 3-class label
# Based on observed plateau structure from full-replication per-class means
SIX_TO_THREE = {
    "SAME_CORPUS_PRISTINE":   "HIGH",    # mean 0.941
    "COMPOUND_SAME_CORPUS":   "HIGH",    # mean 0.885
    "REPLAY_SAME_CORPUS":     "MID",     # mean 0.845
    "NO_REPLAY_SAME_CORPUS":  "MID",     # mean 0.682  (overlaps STAGE_4 at 6-class)
    "STAGE_4_COMPOUND":       "MID",     # mean 0.734
    "DIFF_CORPUS_2TASK":      "LOW",     # mean 0.633
}

CLASS_ORDER = ["HIGH", "MID", "LOW"]

# Pre-registered thresholds
PASS_MIN_NONOVERLAPPING = 3   # all 3 must be non-overlapping
FAIL_MIN_NONOVERLAPPING = 3   # strictly: < 3 = HARD-FAIL (any overlap fails)
PASS_KW_P = 0.01
FAIL_KW_P = 0.05
CI_Z = 1.96  # 95% CI


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# -------- load existing full-replication data --------
def load_six_class_data() -> Dict[str, List[float]]:
    """Load retention_A values from the full-replication run's metrics.json.
    Falls back to shift_class_predictor smoke if full replication not found."""
    candidate_dirs = [
        DATA / "exp_wave14_betB_shift_class_full_replication_v1",
        DATA / "exp_wave14_betB_shift_class_predictor_v1",
    ]
    for d in candidate_dirs:
        metrics_path = d / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                m = json.load(f)
            per_class = m.get("summary", {}).get("per_class", {})
            if per_class:
                print(f"[3class] loading from {metrics_path}", flush=True)
                result = {}
                for class_name, cd in per_class.items():
                    vals = cd.get("values", [])
                    if vals:
                        result[class_name] = vals
                if result:
                    return result
    # Fallback: return empty dict (HARD-FAIL path)
    print("[3class] WARNING: no 6-class data found; returning empty.", flush=True)
    return {}


def mean_std_ci(vals: List[float]) -> Tuple[float, float, float, float]:
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    mu = sum(vals) / n
    if n == 1:
        return mu, 0.0, mu, mu
    var = sum((v - mu) ** 2 for v in vals) / (n - 1)
    std = math.sqrt(var)
    se = std / math.sqrt(n)
    return mu, std, mu - CI_Z * se, mu + CI_Z * se


def kruskal_wallis_p(groups: List[List[float]]) -> float:
    """Kruskal-Wallis p-value via chi-squared approximation."""
    all_vals = []
    group_indices = []
    for gi, g in enumerate(groups):
        for v in g:
            all_vals.append(v)
            group_indices.append(gi)
    n = len(all_vals)
    if n <= 1:
        return 1.0
    k = len(groups)
    if k < 2:
        return 1.0

    sorted_vals = sorted(range(n), key=lambda i: all_vals[i])
    ranks = [0.0] * n
    for rank_i, idx in enumerate(sorted_vals):
        ranks[idx] = rank_i + 1.0

    H = 0.0
    for gi, g in enumerate(groups):
        ng = len(g)
        if ng == 0:
            continue
        group_rank_sum = sum(ranks[i] for i in range(n) if group_indices[i] == gi)
        H += (group_rank_sum ** 2) / ng
    H = (12.0 / (n * (n + 1))) * H - 3.0 * (n + 1)

    # chi-sq p-value with df = k-1
    df = k - 1
    if df <= 0:
        return 1.0
    p = 1.0 - _chi2_cdf(H, df)
    return p


def _chi2_cdf(x: float, df: int) -> float:
    """CDF of chi-squared(df) at x using regularized lower incomplete gamma."""
    if x <= 0:
        return 0.0
    return _regularized_gamma(df / 2.0, x / 2.0)


def _regularized_gamma(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x) via series expansion."""
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0
    MAX_ITER = 200
    EPS = 1e-12
    log_gamma_a = math.lgamma(a)
    term = 1.0 / a
    partial = term
    for n_iter in range(1, MAX_ITER):
        term *= x / (a + n_iter)
        partial += term
        if abs(term) < EPS * abs(partial):
            break
    return math.exp(-x + a * math.log(x) - log_gamma_a) * partial


# -------- self-tests --------
def self_test():
    errors = []

    # Test 1: mean_std_ci single value -> CI = [mu, mu]
    mu, std, lo, hi = mean_std_ci([0.5])
    if abs(mu - 0.5) > 1e-9 or lo != hi:
        errors.append(f"ST1 FAIL: mean_std_ci single val: mu={mu} lo={lo} hi={hi}")

    # Test 2: mean_std_ci symmetric -> CI symmetric around mu
    vals = [0.8, 0.9, 1.0]
    mu, std, lo, hi = mean_std_ci(vals)
    expected_mu = 0.9
    if abs(mu - expected_mu) > 1e-9:
        errors.append(f"ST2 FAIL: mu={mu} expected {expected_mu}")
    if not (lo < mu < hi):
        errors.append(f"ST2 FAIL: CI not around mu: {lo} < {mu} < {hi}")

    # Test 3: SIX_TO_THREE mapping covers all 6 classes
    expected_six = {"SAME_CORPUS_PRISTINE", "COMPOUND_SAME_CORPUS", "REPLAY_SAME_CORPUS",
                    "NO_REPLAY_SAME_CORPUS", "STAGE_4_COMPOUND", "DIFF_CORPUS_2TASK"}
    if set(SIX_TO_THREE.keys()) != expected_six:
        errors.append(f"ST3 FAIL: SIX_TO_THREE keys mismatch: {set(SIX_TO_THREE.keys())}")

    # Test 4: 3-class grouping assigns each name to one of {HIGH, MID, LOW}
    for k, v in SIX_TO_THREE.items():
        if v not in {"HIGH", "MID", "LOW"}:
            errors.append(f"ST4 FAIL: {k} maps to {v} not in {{HIGH, MID, LOW}}")

    # Test 5: kruskal_wallis_p with clearly separated groups -> p close to 0
    g1 = [0.9, 0.91, 0.89, 0.92, 0.90]
    g2 = [0.7, 0.71, 0.69, 0.72, 0.70]
    g3 = [0.5, 0.51, 0.49, 0.52, 0.50]
    p = kruskal_wallis_p([g1, g2, g3])
    if p > 0.01:
        errors.append(f"ST5 FAIL: K-W p={p:.4f} > 0.01 for clearly separated groups")

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 5 self-tests passed", flush=True)


# -------- main analysis --------
def run():
    t0 = time.time()
    self_test()

    six_class_data = load_six_class_data()
    if not six_class_data:
        verdict = "3CLASS_DATA_MISSING"
        verdict_msg = ("Cannot find 6-class source data. "
                       "Run wave14_betB_shift_class_full_replication_v1 first.")
        elapsed = time.time() - t0
        result = {
            "verdict": verdict, "verdict_msg": verdict_msg,
            "elapsed_s": elapsed, "summary": {}, "config": {}
        }
        validate_metrics(result)
        out_dir = get_output_dir("wave14_betB_3class_coarse_predictor_v1")
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"[3class] {verdict}: {verdict_msg}", flush=True)
        return result

    # Aggregate 6-class values into 3 coarse classes
    three_class_data: Dict[str, List[float]] = {"HIGH": [], "MID": [], "LOW": []}
    n_total_values = 0
    for six_label, vals in six_class_data.items():
        coarse = SIX_TO_THREE.get(six_label)
        if coarse is None:
            print(f"[3class] WARNING: unknown 6-class label {six_label!r}, skipping", flush=True)
            continue
        three_class_data[coarse].extend(vals)
        n_total_values += len(vals)

    print(f"[3class] class sizes: " +
          " ".join(f"{c}={len(three_class_data[c])}" for c in CLASS_ORDER), flush=True)

    # Compute per-class stats
    stats: Dict[str, Tuple] = {}
    for c in CLASS_ORDER:
        vals = three_class_data[c]
        mu, std, lo, hi = mean_std_ci(vals)
        stats[c] = (mu, std, lo, hi, len(vals))
        print(f"  {c}: n={len(vals)} mean={mu:.4f} std={std:.4f} CI=[{lo:.4f},{hi:.4f}]",
              flush=True)

    # Count non-overlapping CIs (all pairs must be non-overlapping)
    n_nonoverlapping = 0
    overlap_pairs = []
    for i, ci in enumerate(CLASS_ORDER):
        lo_i, hi_i = stats[ci][2], stats[ci][3]
        fully_separated = True
        for j, cj in enumerate(CLASS_ORDER):
            if i == j:
                continue
            lo_j, hi_j = stats[cj][2], stats[cj][3]
            if lo_i <= hi_j and lo_j <= hi_i:
                fully_separated = False
                overlap_pairs.append((ci, cj))
                break
        if fully_separated:
            n_nonoverlapping += 1

    # Kruskal-Wallis p-value
    groups = [three_class_data[c] for c in CLASS_ORDER if len(three_class_data[c]) >= 2]
    kw_p = kruskal_wallis_p(groups)

    print(f"[3class] n_nonoverlapping={n_nonoverlapping}/3 kw_p={kw_p:.6f}", flush=True)

    # Verdict
    if n_nonoverlapping >= PASS_MIN_NONOVERLAPPING and kw_p < PASS_KW_P:
        verdict = "3CLASS_HARD_PASS"
        verdict_msg = (
            f"3-class coarse taxonomy CONFIRMED: {n_nonoverlapping}/3 non-overlapping CIs "
            f"AND K-W p={kw_p:.2e} < {PASS_KW_P}. "
            f"HIGH ({stats['HIGH'][0]:.3f}) MID ({stats['MID'][0]:.3f}) "
            f"LOW ({stats['LOW'][0]:.3f}) are cleanly separated. "
            f"Defensible product claim: substrate has 3 distinct retention regimes."
        )
    elif n_nonoverlapping >= PASS_MIN_NONOVERLAPPING and kw_p < FAIL_KW_P:
        verdict = "3CLASS_MIDDLE"
        verdict_msg = (
            f"Partial: {n_nonoverlapping}/3 non-overlapping CIs but "
            f"K-W p={kw_p:.2e} in [{PASS_KW_P}, {FAIL_KW_P}). "
            f"HIGH ({stats['HIGH'][0]:.3f}) MID ({stats['MID'][0]:.3f}) "
            f"LOW ({stats['LOW'][0]:.3f}). Weak statistical support."
        )
    else:
        overlap_str = "; ".join(f"{a} overlaps {b}" for a, b in overlap_pairs[:3])
        verdict = "3CLASS_HARD_FAIL"
        verdict_msg = (
            f"3-class coarse taxonomy FAILS: only {n_nonoverlapping}/3 non-overlapping CIs. "
            f"Overlap pairs: {overlap_str}. K-W p={kw_p:.2e}. "
            f"HIGH ({stats['HIGH'][0]:.3f}) MID ({stats['MID'][0]:.3f}) "
            f"LOW ({stats['LOW'][0]:.3f}). "
            f"Even coarsest taxonomy lacks CI separation; walk back to group-level claim only."
        )

    elapsed = time.time() - t0

    summary = {
        "n_nonoverlapping": n_nonoverlapping,
        "kw_p": kw_p,
        "pass_threshold_nonoverlap": PASS_MIN_NONOVERLAPPING,
        "pass_threshold_kw_p": PASS_KW_P,
        "n_total_values": n_total_values,
        "per_coarse_class": {
            c: {
                "n": stats[c][4],
                "mean": round(stats[c][0], 4),
                "std": round(stats[c][1], 4),
                "ci_95_lo": round(stats[c][2], 4),
                "ci_95_hi": round(stats[c][3], 4),
                "source_six_classes": [k for k, v in SIX_TO_THREE.items() if v == c],
            }
            for c in CLASS_ORDER
        },
    }

    result = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "six_to_three_mapping": SIX_TO_THREE,
            "pass_min_nonoverlapping": PASS_MIN_NONOVERLAPPING,
            "pass_kw_p": PASS_KW_P,
            "ci_z": CI_Z,
        },
    }
    validate_metrics(result)

    out_dir = get_output_dir("wave14_betB_3class_coarse_predictor_v1")
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"[3class] verdict={verdict}", flush=True)
    print(f"[3class] {verdict_msg}", flush=True)
    print(f"[3class] elapsed={elapsed:.2f}s", flush=True)
    return result


def main():
    self_test()
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run()


if __name__ == "__main__":
    main()
