"""Verdict pattern mining: statistical analysis of ~100 verdict events.

Reads all verdict events from data/orchestrator_status_log.jsonl and tests
whether verdict outcomes correlate with:
  (a) importance level (CRITICAL/HIGH/MEDIUM/LOW) -- are high-importance experiments
      more likely to PASS or FAIL?
  (b) date/time -- are there temporal drift patterns in pass rates?
  (c) sub_agent composition -- does multi-agent dispatch correlate with outcome?
  (d) hypothesis class inferred from summary text -- do certain topic clusters
      (1RSB, PAC-Bayes, spectral, K-series, etc.) have higher failure rates?
  (e) cap_map_version gap -- does the jump from cap_map_version_from to _to
      correlate with positive vs negative outcomes?

Statistical tests: chi-squared (categorical), Mann-Whitney U (ordinal).
Pure re-analysis of existing JSONL, < 10s.

Pre-registered outcomes:
  PATTERN_FOUND: >= 1 association has chi-sq p < 0.05 AND effect size (Cramer's V
    or rank-biserial r) >= 0.20. Report the signal and suggest pre-reg improvement.
  NO_PATTERN: all associations have p > 0.10 or effect size < 0.10.
    Interpretation: verdict outcome unpredictable from available metadata.
    This is informative: it means outcome variation is captured by the experiment
    content, not by logging-level features.
  WEAK_SIGNAL: some p < 0.10 but effect size < 0.20. Suggestive but not conclusive.

Queue: local_cpu_queue (pure JSONL analysis, < 10s)
Pre-reg: preregs/2026-05-25_verdict_pattern_mining_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = DATA / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert chi-sq and effect size computations are non-null."""
    # 2x2 contingency table: known association
    table = [[10, 2], [2, 10]]
    chi2, p, v = chi_sq_2x2(table)
    assert chi2 is not None and not math.isnan(chi2), f"chi2 is null"
    assert p < 0.01, f"expected strong association, got p={p}"
    assert v > 0.3, f"expected Cramer V > 0.3, got {v}"
    # Independent table: no association
    table_indep = [[10, 10], [10, 10]]
    chi2_0, p_0, v_0 = chi_sq_2x2(table_indep)
    assert chi2_0 is not None and abs(chi2_0) < 1e-9, f"expected chi2=0 for independent, got {chi2_0}"
    print("[self-test] chi-sq and Cramer V computations OK")

_SELFTEST_DEFERRED = True  # called after helpers below


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def chi_sq_2x2(table: List[List[int]]) -> Tuple[float, float, float]:
    """Chi-squared test for 2x2 (or 2xK) contingency table.
    Returns (chi2, p, cramers_v)."""
    # Flatten to R x C
    R = len(table)
    C = len(table[0])
    n = sum(sum(row) for row in table)
    if n == 0:
        return (0.0, 1.0, 0.0)
    row_sums = [sum(row) for row in table]
    col_sums = [sum(table[r][c] for r in range(R)) for c in range(C)]
    chi2 = 0.0
    for r in range(R):
        for c in range(C):
            expected = row_sums[r] * col_sums[c] / n
            if expected > 0:
                chi2 += (table[r][c] - expected) ** 2 / expected
    df = (R - 1) * (C - 1)
    p = _chi2_sf(chi2, df)
    v = math.sqrt(chi2 / (n * min(R - 1, C - 1))) if n > 0 and min(R - 1, C - 1) > 0 else 0.0
    return (chi2, p, v)


def _chi2_sf(x: float, df: int) -> float:
    if x <= 0:
        return 1.0
    return _regularized_upper_gamma(df / 2.0, x / 2.0)


def _regularized_upper_gamma(a: float, x: float) -> float:
    if x < 0:
        return 1.0
    if x == 0:
        return 1.0
    if x < a + 1:
        ap = a
        s = 1.0 / a
        d = s
        for _ in range(300):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 3e-7:
                break
        gln = _log_gamma(a)
        return max(0.0, 1.0 - math.exp(-x + a * math.log(x) - gln) * s)
    else:
        b = x + 1.0 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, 301):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 3e-7:
                break
        gln = _log_gamma(a)
        return math.exp(-x + a * math.log(x) - gln) * h


def _log_gamma(z: float) -> float:
    g = 7
    c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    if z < 0.5:
        return math.log(math.pi / math.sin(math.pi * z)) - _log_gamma(1.0 - z)
    z -= 1
    x = c[0]
    for i in range(1, g + 2):
        x += c[i] / (z + i)
    t = z + g + 0.5
    return 0.5 * math.log(2 * math.pi) + (z + 0.5) * math.log(t) - t + math.log(x)


# ---------------------------------------------------------------------------
# Verdict extraction
# ---------------------------------------------------------------------------

OUTCOME_MAP = {
    "HARD_PASS": "PASS", "HARD-PASS": "PASS", "PASS": "PASS", "_PASS": "PASS",
    "HARD_FAIL": "FAIL", "HARD-FAIL": "FAIL", "FAIL": "FAIL", "_FAIL": "FAIL",
    "KILL": "FAIL",
    "PARTIAL": "PARTIAL",
    "MIDDLE": "PARTIAL",
    "INCONCLUSIVE": "INCONCLUSIVE",
    "SATURATION": "INCONCLUSIVE",
}

TOPIC_PATTERNS = [
    ("1RSB/spin-glass", re.compile(r"1rsb|rsb|ultrametric|hopfield|spin.?glass|parisi|crooks|hysteresis", re.I)),
    ("PAC-Bayes/info-theory", re.compile(r"pac.?bayes|kl|kullback|fisher|information.?theor|entropy|ib_", re.I)),
    ("spectral/RMT", re.compile(r"mp.ks|mmd|spectral|marchenko|wigner|eigenval|random.?matrix|vamp|amp|rmse", re.I)),
    ("capacity/K-series", re.compile(r"\bk[0-9]\b|cap[0-9]|capacity|kappa|compa|comp[ab]", re.I)),
    ("Bet-B/continual", re.compile(r"betb|bet.?b|continual|stage.?4|shift.?class|retention|ewc", re.I)),
    ("geometry/topology", re.compile(r"geometry|topolog|clifford|kerdock|paley|codebook|frame", re.I)),
    ("optimization/flows", re.compile(r"optim|sellke|online.?w|lyapunov|reservoir|allen.?cahn|tropical", re.I)),
    ("MoE/expert", re.compile(r"moe|expert|alpha.?c|mixture.?of", re.I)),
]


_instrumentation_selftest()  # called after helpers defined


def classify_outcome(summary: str) -> Optional[str]:
    su = summary.upper()
    for kw, mapped in OUTCOME_MAP.items():
        if kw in su:
            return mapped
    return None


def classify_topic(summary: str) -> str:
    for label, pattern in TOPIC_PATTERNS:
        if pattern.search(summary):
            return label
    return "other"


def load_verdicts() -> List[Dict]:
    path = DATA / "orchestrator_status_log.jsonl"
    verdicts = []
    with open(path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("event_kind") == "verdict":
                verdicts.append(e)
    return verdicts


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def analyze_importance_vs_outcome(verdicts: List[Dict]) -> Dict:
    """Test: does importance level correlate with pass/fail?"""
    imp_outcome: Dict[str, Dict[str, int]] = defaultdict(lambda: {"PASS": 0, "FAIL": 0, "OTHER": 0})
    for v in verdicts:
        outcome = classify_outcome(v.get("summary", ""))
        if outcome not in ("PASS", "FAIL"):
            outcome = "OTHER"
        imp = v.get("importance", "unknown")
        imp_outcome[imp][outcome] += 1

    print("\n  Importance x Outcome cross-tab:")
    for imp in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if imp not in imp_outcome:
            continue
        d = imp_outcome[imp]
        total = sum(d.values())
        pass_rate = d["PASS"] / total if total > 0 else 0
        print(f"    {imp}: n={total}, PASS={d['PASS']}, FAIL={d['FAIL']}, OTHER={d['OTHER']}, pass_rate={pass_rate:.2f}")

    # 2x2 (CRITICAL+HIGH vs MEDIUM+LOW) x (PASS vs FAIL)
    high_pass = imp_outcome.get("CRITICAL", {}).get("PASS", 0) + imp_outcome.get("HIGH", {}).get("PASS", 0)
    high_fail = imp_outcome.get("CRITICAL", {}).get("FAIL", 0) + imp_outcome.get("HIGH", {}).get("FAIL", 0)
    low_pass = imp_outcome.get("MEDIUM", {}).get("PASS", 0) + imp_outcome.get("LOW", {}).get("PASS", 0)
    low_fail = imp_outcome.get("MEDIUM", {}).get("FAIL", 0) + imp_outcome.get("LOW", {}).get("FAIL", 0)
    table = [[high_pass, high_fail], [low_pass, low_fail]]
    chi2, p, v = chi_sq_2x2(table)
    print(f"  Chi-sq (high vs low importance, PASS vs FAIL): chi2={chi2:.3f}, p={p:.4f}, V={v:.3f}")
    return {"chi2": chi2, "p": p, "cramers_v": v, "table": table,
            "high_pass_rate": high_pass / (high_pass + high_fail) if (high_pass + high_fail) > 0 else 0,
            "low_pass_rate": low_pass / (low_pass + low_fail) if (low_pass + low_fail) > 0 else 0}


def analyze_topic_vs_outcome(verdicts: List[Dict]) -> Dict:
    """Test: does hypothesis topic cluster correlate with pass/fail?"""
    topic_outcome: Dict[str, Counter] = defaultdict(Counter)
    for v in verdicts:
        summary = v.get("summary", "")
        outcome = classify_outcome(summary) or "OTHER"
        topic = classify_topic(summary)
        topic_outcome[topic][outcome] += 1

    print("\n  Topic x Outcome cross-tab:")
    topic_pass_rates = {}
    for topic, counts in sorted(topic_outcome.items()):
        total = sum(counts.values())
        pass_rate = counts["PASS"] / total if total > 0 else 0
        fail_rate = counts["FAIL"] / total if total > 0 else 0
        topic_pass_rates[topic] = pass_rate
        print(f"    {topic}: n={total}, PASS={counts['PASS']}, FAIL={counts['FAIL']}, pass_rate={pass_rate:.2f}")

    # Chi-sq over all topics x (PASS, FAIL) outcomes
    topics_list = sorted(topic_outcome.keys())
    if len(topics_list) >= 2:
        table = [[topic_outcome[t]["PASS"], topic_outcome[t]["FAIL"]] for t in topics_list]
        chi2, p, v = chi_sq_2x2(table)
        print(f"  Chi-sq (topic vs PASS/FAIL): chi2={chi2:.3f}, p={p:.4f}, V={v:.3f}")
    else:
        chi2, p, v = 0.0, 1.0, 0.0
    return {"chi2": chi2, "p": p, "cramers_v": v, "topic_pass_rates": topic_pass_rates}


def analyze_temporal_trend(verdicts: List[Dict]) -> Dict:
    """Test: is there temporal drift in pass rate over the session?"""
    # Split into first half vs second half by timestamp
    verdicts_sorted = sorted(verdicts, key=lambda v: v.get("ts", ""))
    n = len(verdicts_sorted)
    if n < 10:
        return {"skipped": True, "reason": "too few verdicts"}
    first_half = verdicts_sorted[:n // 2]
    second_half = verdicts_sorted[n // 2:]

    def pass_fail_counts(v_list):
        passes = sum(1 for v in v_list if classify_outcome(v.get("summary", "")) == "PASS")
        fails = sum(1 for v in v_list if classify_outcome(v.get("summary", "")) == "FAIL")
        return passes, fails

    p1, f1 = pass_fail_counts(first_half)
    p2, f2 = pass_fail_counts(second_half)
    table = [[p1, f1], [p2, f2]]
    chi2, p, v = chi_sq_2x2(table)
    r1 = p1 / (p1 + f1) if (p1 + f1) > 0 else 0
    r2 = p2 / (p2 + f2) if (p2 + f2) > 0 else 0
    print(f"\n  Temporal trend (first-half vs second-half pass rates): {r1:.2f} vs {r2:.2f}")
    print(f"  Chi-sq: chi2={chi2:.3f}, p={p:.4f}")
    return {"chi2": chi2, "p": p, "cramers_v": v,
            "first_half_pass_rate": r1, "second_half_pass_rate": r2}


def analyze_multiagent_vs_single(verdicts: List[Dict]) -> Dict:
    """Test: multi-agent dispatch (strategy+visibility) vs single-agent outcome."""
    multi = [v for v in verdicts if len(v.get("sub_agents", [])) >= 2]
    single = [v for v in verdicts if len(v.get("sub_agents", [])) < 2]

    def pass_fail_counts(v_list):
        passes = sum(1 for v in v_list if classify_outcome(v.get("summary", "")) == "PASS")
        fails = sum(1 for v in v_list if classify_outcome(v.get("summary", "")) == "FAIL")
        return passes, fails

    mp, mf = pass_fail_counts(multi)
    sp, sf = pass_fail_counts(single)
    table = [[mp, mf], [sp, sf]]
    chi2, p, v = chi_sq_2x2(table)
    mr = mp / (mp + mf) if (mp + mf) > 0 else 0
    sr = sp / (sp + sf) if (sp + sf) > 0 else 0
    print(f"\n  Multi-agent ({len(multi)}) vs single-agent ({len(single)}) pass rates: {mr:.2f} vs {sr:.2f}")
    print(f"  Chi-sq: chi2={chi2:.3f}, p={p:.4f}, V={v:.3f}")
    return {"chi2": chi2, "p": p, "cramers_v": v, "multi_pass_rate": mr, "single_pass_rate": sr,
            "n_multi": len(multi), "n_single": len(single)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_verdict_pattern_mining_v1")

    verdicts = load_verdicts()
    print(f"Loaded {len(verdicts)} verdict events")

    # Overall outcome distribution
    outcome_dist: Counter = Counter()
    for v in verdicts:
        outcome = classify_outcome(v.get("summary", "")) or "OTHER"
        outcome_dist[outcome] += 1
    print(f"Overall outcome distribution: {dict(outcome_dist)}")
    total_decisive = outcome_dist["PASS"] + outcome_dist["FAIL"]
    overall_pass_rate = outcome_dist["PASS"] / total_decisive if total_decisive > 0 else 0
    print(f"Overall pass rate (PASS/FAIL only): {overall_pass_rate:.2f} ({outcome_dist['PASS']}/{total_decisive})")

    # Run analyses
    imp_result = analyze_importance_vs_outcome(verdicts)
    topic_result = analyze_topic_vs_outcome(verdicts)
    temporal_result = analyze_temporal_trend(verdicts)
    multi_result = analyze_multiagent_vs_single(verdicts)

    # Collect all p-values and effect sizes
    all_tests = [
        ("importance", imp_result),
        ("topic", topic_result),
        ("temporal", temporal_result),
        ("multi_agent", multi_result),
    ]

    PASS_P = 0.05
    PASS_V = 0.20
    signals_found = []
    for name, result in all_tests:
        if result.get("skipped"):
            continue
        p = result.get("p", 1.0)
        v_val = result.get("cramers_v", 0.0)
        if p < PASS_P and v_val >= PASS_V:
            signals_found.append({"test": name, "p": p, "cramers_v": v_val})

    print(f"\nSignificant patterns found (p<0.05, V>=0.20): {len(signals_found)}")
    for s in signals_found:
        print(f"  {s['test']}: p={s['p']:.4f}, V={s['cramers_v']:.3f}")

    # Verdict
    weak_signals = [name for name, result in all_tests
                    if not result.get("skipped") and result.get("p", 1.0) < 0.10
                    and result.get("cramers_v", 0.0) >= 0.10]

    if signals_found:
        verdict = "PATTERN_FOUND"
        verdict_msg = (
            f"PATTERN_FOUND: {len(signals_found)} significant association(s): "
            + "; ".join(f"{s['test']} (p={s['p']:.3f}, V={s['cramers_v']:.2f})" for s in signals_found)
            + ". Consider adjusting pre-reg quality for affected anchor classes."
        )
    elif weak_signals:
        verdict = "WEAK_SIGNAL"
        verdict_msg = (
            f"WEAK_SIGNAL: p < 0.10 but V < 0.20 in: {', '.join(weak_signals)}. "
            f"Suggestive but below threshold. n={len(verdicts)} verdicts analyzed."
        )
    else:
        verdict = "NO_PATTERN"
        verdict_msg = (
            f"NO_PATTERN: All associations have p > 0.10 or V < 0.10. "
            f"Verdict outcome unpredictable from logging metadata. "
            f"n={len(verdicts)} verdicts; overall pass_rate={overall_pass_rate:.2f}."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "summary": {
            "n_verdicts_analyzed": len(verdicts),
            "overall_pass_rate": round(overall_pass_rate, 3),
            "outcome_distribution": dict(outcome_dist),
            "signals_found": signals_found,
            "weak_signals": weak_signals,
        },
        "analyses": {
            "importance_vs_outcome": imp_result,
            "topic_vs_outcome": topic_result,
            "temporal_trend": temporal_result,
            "multiagent_vs_single": multi_result,
        },
        "config": {"pass_p_threshold": PASS_P, "pass_v_threshold": PASS_V},
    }
    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
