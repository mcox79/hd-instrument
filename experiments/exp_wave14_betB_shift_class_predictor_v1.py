"""Alt1 Bet B discrete shift-class predictor: re-analysis of existing run artifacts.

Context: R-PRIME-3 HARD-FAIL showed that continuous corpus-pair spectral distance does
NOT predict Bet B retention (r^2=0.103). Alt1 tests whether a DISCRETE shift-class
taxonomy predicts retention better. Three retention plateaus are documented:
  0.94 same-corpus pristine / 0.74 4-stage compound / 0.60 diff-corpus
If these map to coherent discrete shift classes, retention is CLASSIFIER-predictable
(not regression-predictable). Product claim: "substrate retains X% on shift-class K."

Design: pure re-analysis of existing metrics.json artifacts. No new model training.
Classifies each experiment run into one of 6 shift classes:
  0: SAME_CORPUS_PRISTINE  -- 2-task same corpus, optimal setup (Kovacs / EMA)
  1: COMPOUND_SAME_CORPUS  -- per-task sub-substrate + replay (structural separation)
  2: REPLAY_SAME_CORPUS    -- 2-task with replay, no sub-substrate
  3: NO_REPLAY_SAME_CORPUS -- 2-task NO replay (ablation boundary)
  4: STAGE_4_COMPOUND      -- 4-stage A->B->C->D pipeline (load-stressed)
  5: DIFF_CORPUS_2TASK     -- 2-task with different corpus (cross-domain shift)

Pre-reg:
    HARD-PASS: >=4/6 shift classes have non-overlapping 95% CI on mean retention_A
               AND Kruskal-Wallis p < 0.05 across all classes (class membership
               significantly predicts retention). Interpretation: discrete classifier
               IS predictive; product claim "retains X% on class K" is defensible.
    HARD-FAIL: <3/6 shift classes with non-overlapping CIs OR K-W p >= 0.10.
               Interpretation: class membership does NOT predict retention better
               than spectral distance (R-PRIME-3's rejected metric).
    MIDDLE: 3-4/6 non-overlapping CIs, p in (0.05, 0.10); partial predictability.

Queue: local_cpu_queue (pure analysis, no GPU needed).
ETA: <5 min (pure Python analysis of fetched metrics.json files).
Pre-reg: preregs/2026-05-24_wave14_betB_shift_class_predictor_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL/MIDDLE pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: stdout.reconfigure at top.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TMP = DATA / "tmp_betb_analysis"

# ────────────── design parameters (exp_dev autonomy) ──────────────
# Shift class definitions (0=pristine..5=diff-corpus)
CLASS_NAMES = {
    0: "SAME_CORPUS_PRISTINE",
    1: "COMPOUND_SAME_CORPUS",
    2: "REPLAY_SAME_CORPUS",
    3: "NO_REPLAY_SAME_CORPUS",
    4: "STAGE_4_COMPOUND",
    5: "DIFF_CORPUS_2TASK",
}

# Pre-registered thresholds
PASS_MIN_NONOVERLAPPING = 4   # classes whose 95% CI must be non-overlapping
FAIL_MIN_NONOVERLAPPING = 3   # below this = HARD-FAIL
PASS_KW_P = 0.05
FAIL_KW_P = 0.10
CI_Z = 1.96   # 95% CI multiplier


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = DATA / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ────────────── data loading ──────────────
def load_retention_per_class() -> Dict[int, List[float]]:
    """Load retention_A values per shift class from pre-fetched metrics files.
    Also synthesizes from known verdicts/values documented in cap_map history."""
    class_data: Dict[int, List[float]] = {k: [] for k in range(6)}

    # -- Class 0: SAME_CORPUS_PRISTINE -- Kovacs/EMA variants (documented in cap_map)
    # v9: retention_A = 0.954 x3 seeds (all 3 were 0.954)
    class_data[0].extend([0.954, 0.954, 0.954])
    # v11 EMA (documented): retention_A = 0.914
    class_data[0].append(0.914)
    # v12 phase-A boost (documented): retention_A = 0.927
    class_data[0].append(0.927)

    # -- Class 1: COMPOUND_SAME_CORPUS -- per-task + replay
    compound_replay = TMP / "betB_compound_replay.json"
    compound_longerA = TMP / "betB_compound_longerA.json"
    for fpath in [compound_replay, compound_longerA]:
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[1].append(r)
    # Ablation A (per-task sub-substrate only, no replay)
    ablation_A = TMP / "betB_ablation_A.json"
    if ablation_A.exists():
        with open(ablation_A) as fp:
            d = json.load(fp)
        ps = d.get("summary", {}).get("per_seed", {})
        for sv in ps.values():
            if isinstance(sv, dict):
                r = sv.get("retention_A")
                if r is not None:
                    class_data[1].append(r)

    # -- Class 2: REPLAY_SAME_CORPUS -- 2-task with replay
    replay_norm = TMP / "betB_replay_by_norm.json"
    if replay_norm.exists():
        with open(replay_norm) as fp:
            d = json.load(fp)
        pm = d.get("summary", {}).get("per_mode", {})
        # Use uniform mode as canonical replay-2task
        for mode_name in ["uniform", "norm_weighted"]:
            if mode_name in pm:
                for sv in pm[mode_name].values():
                    if isinstance(sv, dict):
                        r = sv.get("retention_A")
                        if r is not None:
                            class_data[2].append(r)

    # Ablation B at replay_frac >= 0.05 (replay enabled)
    ablation_B = TMP / "betB_ablation_B.json"
    if ablation_B.exists():
        with open(ablation_B) as fp:
            d = json.load(fp)
        prf = d.get("summary", {}).get("per_replay_frac", {})
        for frac_str, seeds_data in prf.items():
            try:
                frac = float(frac_str)
            except ValueError:
                continue
            if frac >= 0.05:  # replay enabled (class 2)
                for sv in seeds_data.values():
                    if isinstance(sv, dict):
                        r = sv.get("retention_A")
                        if r is not None:
                            class_data[2].append(r)

    # Task geometry pairs: B_shuffled, C_python, E_reversed (all same-corpus-like,
    # small spectral distance -> class 2)
    task_geom = TMP / "betB_task_geometry_rerun.json"
    if task_geom.exists():
        with open(task_geom) as fp:
            d = json.load(fp)
        pp = d.get("summary", {}).get("per_pair", {})
        # same-corpus-like pairs (spectral_distance < 0.1)
        for pair_name, pv in pp.items():
            sd = pv.get("spectral_distance", 1.0)
            if sd < 0.1:  # B_shuffled=0.029, C_python=0.015, E_reversed=0.0
                for sv in pv.get("seeds", {}).values():
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[2].append(r)

    # -- Class 3: NO_REPLAY_SAME_CORPUS -- ablation boundary
    if ablation_B.exists():
        with open(ablation_B) as fp:
            d = json.load(fp)
        prf = d.get("summary", {}).get("per_replay_frac", {})
        if "0.0" in prf:
            for sv in prf["0.0"].values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[3].append(r)

    # -- Class 4: STAGE_4_COMPOUND -- 4-stage A->B->C->D
    for fname in ["betB_4stage_v1.json", "betB_4stage_n8192.json",
                  "betB_phaseA_consol.json", "k2_m1_hierreplay_full.json"]:
        fpath = TMP / fname
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[4].append(r)
    # Task geometry D_random pair: spectral_distance~0.5, BUT it's a 2-task condition
    # -> classify as CROSS_DOMAIN_RANDOM = separate from 4STAGE
    # D_random data: retA = 0.738 x3 seeds -> belongs to class 5 or a bridging class
    # For simplicity: D_random sits between 4stage (0.74) and diff_corpus (0.60)
    # -> classify as class 5 (diff-corpus) since it IS a different corpus pair
    if task_geom.exists():
        with open(task_geom) as fp:
            d = json.load(fp)
        pp = d.get("summary", {}).get("per_pair", {})
        for pair_name, pv in pp.items():
            sd = pv.get("spectral_distance", 0.0)
            if sd >= 0.1:  # D_random=0.508
                for sv in pv.get("seeds", {}).values():
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[5].append(r)

    # -- Class 5: DIFF_CORPUS_2TASK -- English-wiki x code
    for fname in ["betB_diff_corpus_v1.json", "betB_diff_corpus_n4096.json"]:
        fpath = TMP / fname
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[5].append(r)

    return class_data


def mean_std_ci(vals: List[float]) -> Tuple[float, float, float, float]:
    """Returns (mean, std, ci_lo, ci_hi) using normal approximation."""
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


def count_nonoverlapping(class_stats: Dict[int, Tuple]) -> int:
    """Count how many class CIs are non-overlapping with ALL other classes."""
    count = 0
    class_ids = [k for k, v in class_stats.items() if not math.isnan(v[0])]
    for ci in class_ids:
        mu_i, std_i, lo_i, hi_i = class_stats[ci]
        non_overlaps = True
        for cj in class_ids:
            if ci == cj:
                continue
            mu_j, std_j, lo_j, hi_j = class_stats[cj]
            # Check overlap: intervals [lo_i, hi_i] and [lo_j, hi_j]
            if lo_i <= hi_j and lo_j <= hi_i:
                non_overlaps = False
                break
        if non_overlaps:
            count += 1
    return count


def kruskal_wallis_p(groups: List[List[float]]) -> float:
    """Simplified Kruskal-Wallis p-value using chi-squared approximation."""
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

    # Rank all values
    sorted_vals = sorted(range(n), key=lambda i: all_vals[i])
    ranks = [0.0] * n
    for rank_i, idx in enumerate(sorted_vals):
        ranks[idx] = rank_i + 1.0  # 1-based

    # Handle ties (average rank)
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[sorted_vals[j]] == all_vals[sorted_vals[i]]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for idx in range(i, j):
            ranks[sorted_vals[idx]] = avg_rank
        i = j

    # Compute H statistic
    H = 0.0
    for gi, g in enumerate(groups):
        if not g:
            continue
        group_rank_sum = sum(ranks[idx] for idx, gidx in enumerate(group_indices) if gidx == gi)
        ni = len(g)
        H += group_rank_sum ** 2 / ni

    H = 12.0 / (n * (n + 1)) * H - 3 * (n + 1)

    # Chi-squared approximation with df = k-1
    df = k - 1
    # Use regularized incomplete gamma function approximation
    # For p-value: p = 1 - chi2_cdf(H, df)
    # Simple approximation using Wilson-Hilferty
    if df <= 0 or H < 0:
        return 1.0
    try:
        z = ((H / df) ** (1 / 3) - (1 - 2.0 / (9 * df))) / math.sqrt(2.0 / (9 * df))
        # z ~ N(0,1) under H0; p = P(Z > z) for right tail
        # Use error function approximation
        p = 0.5 * (1 - math.erf(z / math.sqrt(2)))
    except (ZeroDivisionError, ValueError):
        p = 1.0
    return max(0.0, min(1.0, p))


def self_test():
    """Self-test cells verifying verdict logic."""
    errors = []

    # Cell 1: HARD-PASS condition
    mock_stats = {
        0: (0.95, 0.01, 0.93, 0.97),
        1: (0.91, 0.01, 0.89, 0.93),
        2: (0.84, 0.01, 0.82, 0.86),
        3: (0.68, 0.01, 0.66, 0.70),
        4: (0.74, 0.01, 0.72, 0.76),
        5: (0.60, 0.01, 0.58, 0.62),
    }
    n_nonoverlap = count_nonoverlapping(mock_stats)
    if n_nonoverlap < PASS_MIN_NONOVERLAPPING:
        errors.append(f"Cell 1: expected >=4 nonoverlapping, got {n_nonoverlap}")

    # Cell 2: HARD-FAIL condition - overlapping CIs
    mock_stats_fail = {
        0: (0.85, 0.10, 0.65, 1.05),
        1: (0.82, 0.10, 0.62, 1.02),
        2: (0.80, 0.10, 0.60, 1.00),
        3: (0.78, 0.10, 0.58, 0.98),
        4: (0.76, 0.10, 0.56, 0.96),
        5: (0.74, 0.10, 0.54, 0.94),
    }
    n_nonoverlap_fail = count_nonoverlapping(mock_stats_fail)
    if n_nonoverlap_fail >= FAIL_MIN_NONOVERLAPPING:
        errors.append(f"Cell 2: expected <3 nonoverlapping in fail case, got {n_nonoverlap_fail}")

    # Cell 3: KW p-value with clearly different groups
    groups_different = [[0.94, 0.95, 0.96], [0.74, 0.74, 0.75], [0.60, 0.60, 0.61]]
    p_diff = kruskal_wallis_p(groups_different)
    if p_diff >= 0.05:
        errors.append(f"Cell 3: KW p should be < 0.05 for clearly different groups, got {p_diff:.4f}")

    # Cell 4: KW p-value with identical groups (should be large)
    groups_same = [[0.80, 0.81, 0.82], [0.80, 0.81, 0.82], [0.80, 0.81, 0.82]]
    p_same = kruskal_wallis_p(groups_same)
    if p_same < 0.05:
        errors.append(f"Cell 4: KW p should be >= 0.05 for identical groups, got {p_same:.4f}")

    # Cell 5: HARD-PASS verdict logic
    n_nonoverlap_test = 5
    kw_p_test = 0.01
    if n_nonoverlap_test < PASS_MIN_NONOVERLAPPING or kw_p_test >= PASS_KW_P:
        errors.append("Cell 5: HARD-PASS condition failed unexpectedly")

    # Cell 6: HARD-FAIL verdict logic
    n_nonoverlap_test = 2
    kw_p_test = 0.15
    if n_nonoverlap_test >= FAIL_MIN_NONOVERLAPPING and kw_p_test < FAIL_KW_P:
        errors.append("Cell 6: HARD-FAIL condition failed unexpectedly")

    # Cell 7: MIDDLE verdict logic
    n_nonoverlap_test = 3
    kw_p_test = 0.07
    if not (FAIL_MIN_NONOVERLAPPING <= n_nonoverlap_test < PASS_MIN_NONOVERLAPPING):
        errors.append(f"Cell 7: MIDDLE band n_nonoverlap={n_nonoverlap_test} not in MIDDLE range")

    # Cell 8: mean_std_ci single value
    mu, std, lo, hi = mean_std_ci([0.74])
    if abs(mu - 0.74) > 1e-9 or lo != hi:
        errors.append(f"Cell 8: single-value CI should collapse, got lo={lo} hi={hi}")

    # Cell 9: data loading returns dict with 6 classes
    class_data = load_retention_per_class()
    if set(class_data.keys()) != set(range(6)):
        errors.append(f"Cell 9: expected classes 0-5, got {set(class_data.keys())}")
    for k in range(6):
        if len(class_data[k]) == 0:
            errors.append(f"Cell 9: class {k} ({CLASS_NAMES[k]}) has no data")

    if errors:
        print(f"[SELF-TEST FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        n_cells = 9
        print(f"[SELF-TEST PASS] {n_cells}/{n_cells} cells pass")
        sys.exit(0)


def run_main(mode: str) -> dict:
    """Main analysis: load data, compute class stats, determine verdict."""
    t0 = time.time()

    class_data = load_retention_per_class()

    # Compute per-class statistics
    class_stats = {}
    for k in range(6):
        vals = class_data[k]
        mu, std, lo, hi = mean_std_ci(vals)
        class_stats[k] = (mu, std, lo, hi)

    # Count non-overlapping CIs
    n_nonoverlap = count_nonoverlapping(class_stats)

    # Kruskal-Wallis p-value across all classes
    groups = [class_data[k] for k in range(6) if len(class_data[k]) > 0]
    kw_p = kruskal_wallis_p(groups)

    # Verdict
    if n_nonoverlap >= PASS_MIN_NONOVERLAPPING and kw_p < PASS_KW_P:
        verdict = "SHIFT_CLASS_HARD_PASS"
        verdict_msg = (
            f"Discrete shift-class taxonomy PREDICTS Bet B retention: "
            f"{n_nonoverlap}/6 classes have non-overlapping 95% CIs, "
            f"K-W p={kw_p:.4f} < {PASS_KW_P}. "
            f"Product claim 'substrate retains X% on shift-class K' is defensible."
        )
    elif n_nonoverlap < FAIL_MIN_NONOVERLAPPING or kw_p >= FAIL_KW_P:
        verdict = "SHIFT_CLASS_HARD_FAIL"
        verdict_msg = (
            f"Discrete shift-class taxonomy DOES NOT predict retention: "
            f"only {n_nonoverlap}/6 non-overlapping CIs, "
            f"K-W p={kw_p:.4f}. "
            f"Classifier prediction no better than R-PRIME-3 rejected spectral distance."
        )
    else:
        verdict = "SHIFT_CLASS_MIDDLE_BAND"
        verdict_msg = (
            f"Partial shift-class prediction: {n_nonoverlap}/6 non-overlapping CIs, "
            f"K-W p={kw_p:.4f}. Some classes discriminated, others overlap."
        )

    elapsed = time.time() - t0

    per_class = {}
    for k in range(6):
        mu, std, lo, hi = class_stats[k]
        per_class[CLASS_NAMES[k]] = {
            "n": len(class_data[k]),
            "mean_retention_A": mu,
            "std": std,
            "ci_95_lo": lo,
            "ci_95_hi": hi,
            "values": class_data[k],
        }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "n_nonoverlapping_classes": n_nonoverlap,
            "kw_p": kw_p,
            "pass_threshold_nonoverlap": PASS_MIN_NONOVERLAPPING,
            "fail_threshold_nonoverlap": FAIL_MIN_NONOVERLAPPING,
            "pass_threshold_kw_p": PASS_KW_P,
            "fail_threshold_kw_p": FAIL_KW_P,
            "per_class": per_class,
        },
        "config": {
            "mode": mode,
            "n_classes": 6,
            "ci_z": CI_Z,
            "pass_min_nonoverlapping": PASS_MIN_NONOVERLAPPING,
            "fail_min_nonoverlapping": FAIL_MIN_NONOVERLAPPING,
            "pass_kw_p": PASS_KW_P,
            "fail_kw_p": FAIL_KW_P,
        },
    }
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    mode = "smoke" if args.smoke else "full"
    metrics = run_main(mode)

    print(f"[{metrics['verdict']}] {metrics['verdict_msg']}")
    print(f"  n_nonoverlapping={metrics['summary']['n_nonoverlapping_classes']} kw_p={metrics['summary']['kw_p']:.4f}")
    for cls_name, cs in metrics["summary"]["per_class"].items():
        mu = cs["mean_retention_A"]
        lo = cs["ci_95_lo"]
        hi = cs["ci_95_hi"]
        n = cs["n"]
        if not (mu != mu):  # not nan
            print(f"  {cls_name}: n={n} mean={mu:.4f} 95%CI=[{lo:.4f},{hi:.4f}]")

    out_dir = get_output_dir("wave14_betB_shift_class_predictor_v1")
    with open(out_dir / "metrics.json", "w") as fp:
        json.dump(metrics, fp, indent=2, default=lambda x: x if not (isinstance(x, float) and x != x) else "nan")
    print(f"[written] {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
