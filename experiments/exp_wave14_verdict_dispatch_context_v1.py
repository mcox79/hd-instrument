"""Verdict pattern mining DEEPER: which dispatch contexts produce lower pass rates?

Context: wave14_verdict_pattern_mining_v1 found a significant multi-agent vs
single-agent gap (pass rates 0.36 vs 0.69, p=0.019, V=0.32). The interpretation
was "selection bias" (complex hypotheses go multi-agent). This follow-up drills into:

1. WHICH dispatch sub-patterns drive the gap?
   - inline-via-main-thread vs proper wrapper dispatch
   - verdict_handler:opus-dispatched vs inline strategy
   - Empty sub_agents (no agent logged) -- what pass rate?
   - Single-agent verdict_handler vs multi-agent combinations

2. HYPOTHESIS CLASS within multi-agent: which topic + dispatch-type combos fail?
   E.g., does 1RSB/spin-glass with multi-agent dispatch fail systematically?

3. ROUTING-NOTE ORIGIN signal: does the plain_language field contain patterns
   that predict pass/fail independent of the sub_agent field?
   Keywords: "hypothesis", "mechanism", "framework" (abstract) vs
   "formula", "formula predicts", "specific prediction" (concrete).
   Hypothesis: concrete-prediction verdicts have higher pass rates than
   framework-consistency verdicts.

4. TEMPORAL STABILITY: is the multi-agent gap stable across sub-intervals (first
   third / middle third / last third of the verdict log)?
   If the gap reverses in the last third, it may reflect pipeline maturation
   (wrappers were introduced mid-session and improved routing quality).

Pre-registered outcomes:
  DISPATCH_PATTERN_FOUND: >= 1 dispatch sub-pattern has chi-sq p < 0.05 AND
    Cramer's V >= 0.25. Identifies a specific refinable signal.
  HYPOTHESIS_CLASS_SIGNAL: topic x dispatch combination has p < 0.05.
    Identifies which experiment classes are under-powered.
  KEYWORD_SIGNAL: concrete-prediction keyword presence has p < 0.05 AND V >= 0.20.
  TEMPORAL_REVERSAL: multi-agent gap reverses direction in last-third vs first-third.
    Interpretation: pipeline improved; gap is an artifact of early dispatch style.
  NO_REFINEMENT: no sub-pattern improves on the base multi-agent finding (V < 0.20
    or p > 0.10 for all sub-tests). Multi-agent gap is unresolvable with available
    metadata.

Queue: local_cpu_queue (pure JSONL re-analysis, <10s)
Pre-reg: preregs/2026-05-25_verdict_dispatch_context_v1.md
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
    """Assert chi-sq computations are non-null at small scale."""
    table_strong = [[10, 1], [1, 10]]
    chi2, p, v = chi_sq_2x2(table_strong)
    assert chi2 is not None and not math.isnan(chi2), "chi2 null"
    assert p < 0.01, f"expected p<0.01 for strong association, got {p}"
    assert v > 0.4, f"expected V>0.4, got {v}"

    table_indep = [[5, 5], [5, 5]]
    chi2_0, p_0, v_0 = chi_sq_2x2(table_indep)
    assert abs(chi2_0) < 1e-9, f"expected chi2=0 for independent table, got {chi2_0}"

    # Verify classify_dispatch works on canonical inputs
    assert classify_dispatch([]) == "empty"
    assert classify_dispatch(["inline-via-main-thread"]) == "inline_main"
    assert classify_dispatch(["verdict_handler:opus"]) == "vh_only"
    assert classify_dispatch(["strategy:opus", "visibility:haiku"]) == "multi_wrapper"
    print("[self-test] chi-sq and dispatch classification OK")


# called after helpers are defined below


# ---------------------------------------------------------------------------
# Statistical helpers (copied from v1, kept local for independence)
# ---------------------------------------------------------------------------

def chi_sq_2x2(table: List[List[int]]) -> Tuple[float, float, float]:
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
            if abs(d) < abs(s) * 1e-10:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - _log_gamma(a))
    else:
        b = x + 1.0 - a
        c_val = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, 301):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c_val = b + an / c_val
            if abs(c_val) < 1e-30:
                c_val = 1e-30
            d = 1.0 / d
            delta = d * c_val
            h *= delta
            if abs(delta - 1.0) < 1e-10:
                break
        return math.exp(-x + a * math.log(x) - _log_gamma(a)) * h


def _log_gamma(z: float) -> float:
    cof = [76.18009172947146, -86.50532032941677, 24.01409824083091,
           -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
    y = x = z
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in cof:
        y += 1.0
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


# ---------------------------------------------------------------------------
# Dispatch context classifier
# ---------------------------------------------------------------------------

def classify_dispatch(sub_agents: List[str]) -> str:
    """Classify dispatch style from sub_agents list."""
    sa_str = " ".join(sub_agents).lower()

    if not sub_agents:
        return "empty"
    if "inline-via-main-thread" in sa_str or "inline_main" in sa_str:
        return "inline_main"
    if "verdict_handler-inline" in sa_str or "verdict_handler:opus" in sa_str.replace("inline", ""):
        # Has dedicated verdict_handler
        has_strategy = "strategy" in sa_str
        has_visibility = "visibility" in sa_str
        if has_strategy and has_visibility:
            return "full_wrapper"
        elif has_strategy or has_visibility:
            return "partial_wrapper"
        else:
            return "vh_only"
    if "strategy" in sa_str and "visibility" in sa_str:
        return "multi_wrapper"
    if "strategy" in sa_str or "visibility" in sa_str:
        return "partial_wrapper"
    return "other"


# ---------------------------------------------------------------------------
# Outcome classifier
# ---------------------------------------------------------------------------

def classify_outcome(summary: str) -> str:
    s = summary.upper()
    if any(x in s for x in ["PASS", "CONFIRMED", "VERIFIED", "HARD-PASS"]):
        return "PASS"
    if any(x in s for x in ["FAIL", "REJECTED", "REFUTED", "HARD-FAIL"]):
        return "FAIL"
    return "OTHER"


# ---------------------------------------------------------------------------
# Keyword / concreteness classifier
# ---------------------------------------------------------------------------

def classify_concreteness(plain_language: str, summary: str) -> str:
    """Classify whether verdict tests a concrete formula or an abstract framework."""
    text = (plain_language + " " + summary).lower()
    concrete_kws = ["formula predicts", "predicted value", "specific prediction",
                    "r^2", "r2", "bic", "threshold", "formula", "closed-form",
                    "within tolerance", "matches", "measured value"]
    abstract_kws = ["framework", "consistent with", "mechanism", "hypothesis",
                    "theory", "interpretation", "suggests", "indicates"]
    concrete_score = sum(1 for kw in concrete_kws if kw in text)
    abstract_score = sum(1 for kw in abstract_kws if kw in text)
    if concrete_score >= 2 and concrete_score > abstract_score:
        return "concrete"
    if abstract_score >= 2 and abstract_score > concrete_score:
        return "abstract"
    return "mixed"


# ---------------------------------------------------------------------------
# Topic classifier
# ---------------------------------------------------------------------------

def classify_topic(summary: str, plain_language: str) -> str:
    text = (summary + " " + plain_language).lower()
    if any(x in text for x in ["1rsb", "spin-glass", "replica", "parisi", "ultrametric"]):
        return "1rsb_spinglass"
    if any(x in text for x in ["pac-bayes", "pac bayes", "kl", "posterior", "laplace"]):
        return "pac_bayes"
    if any(x in text for x in ["bet b", "continual", "retention", "corpus", "replay"]):
        return "bet_b_continual"
    if any(x in text for x in ["spectral", "rmt", "marchenko", "wishart", "eigenvalue", "singular"]):
        return "spectral_rmt"
    if any(x in text for x in ["moe", "expert", "mixture"]):
        return "moe_expert"
    if any(x in text for x in ["capacity", "k-series", "k=", "k series"]):
        return "capacity_k"
    if any(x in text for x in ["geometry", "topology", "manifold"]):
        return "geometry_topo"
    if any(x in text for x in ["optimization", "flow", "sgd", "gradient"]):
        return "optimization"
    return "other"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

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
# Analysis
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_verdict_dispatch_context_v1")

    _instrumentation_selftest()

    verdicts = load_verdicts()
    print(f"Loaded {len(verdicts)} verdict events")

    # Classify each verdict
    for v in verdicts:
        v["_dispatch"] = classify_dispatch(v.get("sub_agents", []))
        v["_outcome"] = classify_outcome(v.get("summary", ""))
        v["_concreteness"] = classify_concreteness(
            v.get("plain_language", ""), v.get("summary", ""))
        v["_topic"] = classify_topic(v.get("summary", ""), v.get("plain_language", ""))

    pass_fail = [v for v in verdicts if v["_outcome"] in ("PASS", "FAIL")]
    print(f"PASS/FAIL subset: {len(pass_fail)} events")

    # -----------------------------------------------------------------------
    # Analysis 1: Dispatch sub-pattern breakdown
    # -----------------------------------------------------------------------
    print("\n--- DISPATCH CONTEXT BREAKDOWN ---")
    dispatch_stats: Dict[str, Dict] = defaultdict(lambda: {"PASS": 0, "FAIL": 0, "OTHER": 0})
    for v in verdicts:
        dispatch_stats[v["_dispatch"]][v["_outcome"]] += 1

    dispatch_results = {}
    for ctx in sorted(dispatch_stats.keys()):
        d = dispatch_stats[ctx]
        total = sum(d.values())
        pf = d["PASS"] + d["FAIL"]
        pass_rate = d["PASS"] / pf if pf > 0 else float("nan")
        pr_str = f"{pass_rate:.2f}" if not math.isnan(pass_rate) else "NaN"
        print(f"  {ctx}: n={total} (P={d['PASS']},F={d['FAIL']},O={d['OTHER']}), "
              f"pass_rate={pr_str}")
        dispatch_results[ctx] = {
            "n_total": total, "n_pass": d["PASS"], "n_fail": d["FAIL"],
            "n_other": d["OTHER"], "pass_rate": pass_rate if not math.isnan(pass_rate) else None
        }

    # Chi-sq: inline_main vs full_wrapper (most interpretable 2x2)
    inline_pass = dispatch_stats.get("inline_main", {}).get("PASS", 0)
    inline_fail = dispatch_stats.get("inline_main", {}).get("FAIL", 0)
    wrapper_pass = (dispatch_stats.get("full_wrapper", {}).get("PASS", 0) +
                    dispatch_stats.get("multi_wrapper", {}).get("PASS", 0))
    wrapper_fail = (dispatch_stats.get("full_wrapper", {}).get("FAIL", 0) +
                    dispatch_stats.get("multi_wrapper", {}).get("FAIL", 0))

    chi2_inline, p_inline, v_inline = chi_sq_2x2([[inline_pass, inline_fail], [wrapper_pass, wrapper_fail]])
    print(f"\n  Chi-sq (inline_main vs wrapper, PASS/FAIL): chi2={chi2_inline:.3f}, p={p_inline:.4f}, V={v_inline:.3f}")

    # Chi-sq: empty (no agents logged) vs rest
    empty_pass = dispatch_stats.get("empty", {}).get("PASS", 0)
    empty_fail = dispatch_stats.get("empty", {}).get("FAIL", 0)
    rest_pass = sum(dispatch_stats[k].get("PASS", 0) for k in dispatch_stats if k != "empty")
    rest_fail = sum(dispatch_stats[k].get("FAIL", 0) for k in dispatch_stats if k != "empty")
    chi2_empty, p_empty, v_empty = chi_sq_2x2([[empty_pass, empty_fail], [rest_pass, rest_fail]])
    print(f"  Chi-sq (empty vs rest, PASS/FAIL): chi2={chi2_empty:.3f}, p={p_empty:.4f}, V={v_empty:.3f}")

    # -----------------------------------------------------------------------
    # Analysis 2: Topic x Dispatch combination
    # -----------------------------------------------------------------------
    print("\n--- TOPIC x DISPATCH BREAKDOWN ---")
    topic_dispatch_stats: Dict[Tuple, Dict] = defaultdict(lambda: {"PASS": 0, "FAIL": 0})
    for v in pass_fail:
        key = (v["_topic"], v["_dispatch"])
        topic_dispatch_stats[key][v["_outcome"]] += 1

    # Find highest-failure combos
    combo_rates = []
    for (topic, disp), d in topic_dispatch_stats.items():
        pf = d["PASS"] + d["FAIL"]
        if pf >= 3:  # minimum cell size
            pr = d["PASS"] / pf
            combo_rates.append({"topic": topic, "dispatch": disp, "n": pf,
                                "pass_rate": pr, "PASS": d["PASS"], "FAIL": d["FAIL"]})
    combo_rates.sort(key=lambda x: x["pass_rate"])
    print("  Lowest pass-rate combos (n>=3):")
    for c in combo_rates[:8]:
        print(f"    {c['topic']} x {c['dispatch']}: n={c['n']}, pass={c['PASS']}, fail={c['FAIL']}, rate={c['pass_rate']:.2f}")

    # -----------------------------------------------------------------------
    # Analysis 3: Concreteness keyword signal
    # -----------------------------------------------------------------------
    print("\n--- CONCRETENESS KEYWORD SIGNAL ---")
    conc_stats: Dict[str, Dict] = defaultdict(lambda: {"PASS": 0, "FAIL": 0})
    for v in pass_fail:
        conc_stats[v["_concreteness"]][v["_outcome"]] += 1

    for cls in ["concrete", "abstract", "mixed"]:
        d = conc_stats.get(cls, {"PASS": 0, "FAIL": 0})
        pf = d["PASS"] + d["FAIL"]
        pr = d["PASS"] / pf if pf > 0 else float("nan")
        pr_str2 = f"{pr:.2f}" if not math.isnan(pr) else "NaN"
        print(f"  {cls}: n={pf}, PASS={d['PASS']}, FAIL={d['FAIL']}, pass_rate={pr_str2}")

    conc_pass = conc_stats.get("concrete", {}).get("PASS", 0)
    conc_fail = conc_stats.get("concrete", {}).get("FAIL", 0)
    abst_pass = (conc_stats.get("abstract", {}).get("PASS", 0) +
                 conc_stats.get("mixed", {}).get("PASS", 0))
    abst_fail = (conc_stats.get("abstract", {}).get("FAIL", 0) +
                 conc_stats.get("mixed", {}).get("FAIL", 0))
    chi2_conc, p_conc, v_conc = chi_sq_2x2([[conc_pass, conc_fail], [abst_pass, abst_fail]])
    print(f"  Chi-sq (concrete vs abstract+mixed): chi2={chi2_conc:.3f}, p={p_conc:.4f}, V={v_conc:.3f}")

    # -----------------------------------------------------------------------
    # Analysis 4: Temporal stability of multi-agent gap
    # -----------------------------------------------------------------------
    print("\n--- TEMPORAL STABILITY OF MULTI-AGENT GAP ---")
    n = len(pass_fail)
    thirds = [pass_fail[:n // 3], pass_fail[n // 3: 2 * n // 3], pass_fail[2 * n // 3:]]
    third_labels = ["first_third", "mid_third", "last_third"]
    temporal_stats = {}
    for label, chunk in zip(third_labels, thirds):
        multi = [v for v in chunk if v["_dispatch"] in
                 ("full_wrapper", "multi_wrapper", "partial_wrapper", "vh_only")]
        single = [v for v in chunk if v["_dispatch"] in ("inline_main", "empty", "other")]
        m_pass = sum(1 for v in multi if v["_outcome"] == "PASS")
        m_fail = sum(1 for v in multi if v["_outcome"] == "FAIL")
        s_pass = sum(1 for v in single if v["_outcome"] == "PASS")
        s_fail = sum(1 for v in single if v["_outcome"] == "FAIL")
        m_rate = m_pass / (m_pass + m_fail) if (m_pass + m_fail) > 0 else float("nan")
        s_rate = s_pass / (s_pass + s_fail) if (s_pass + s_fail) > 0 else float("nan")
        print(f"  {label}: multi_pass={m_rate:.2f} ({m_pass}/{m_pass+m_fail}), single_pass={s_rate:.2f} ({s_pass}/{s_pass+s_fail})")
        temporal_stats[label] = {
            "multi_pass_rate": m_rate if not math.isnan(m_rate) else None,
            "single_pass_rate": s_rate if not math.isnan(s_rate) else None,
            "n_multi": m_pass + m_fail, "n_single": s_pass + s_fail,
        }

    # Check for gap reversal between first and last third
    first_gap = (temporal_stats["first_third"].get("single_pass_rate") or 0) - \
                (temporal_stats["first_third"].get("multi_pass_rate") or 0)
    last_gap = (temporal_stats["last_third"].get("single_pass_rate") or 0) - \
               (temporal_stats["last_third"].get("multi_pass_rate") or 0)
    gap_reversal = (first_gap > 0 and last_gap < 0) or (first_gap < 0 and last_gap > 0)
    print(f"  First-third single-multi gap: {first_gap:.2f}, Last-third: {last_gap:.2f}")
    print(f"  Gap reversal: {gap_reversal}")

    # -----------------------------------------------------------------------
    # Verdict synthesis
    # -----------------------------------------------------------------------
    signals = []
    if p_inline < 0.05 and v_inline >= 0.25:
        signals.append(f"inline_main_vs_wrapper (p={p_inline:.3f}, V={v_inline:.3f})")
    if p_conc < 0.05 and v_conc >= 0.20:
        signals.append(f"concreteness (p={p_conc:.3f}, V={v_conc:.3f})")
    if p_empty < 0.05 and v_empty >= 0.20:
        signals.append(f"empty_dispatch (p={p_empty:.3f}, V={v_empty:.3f})")

    if gap_reversal:
        verdict = "TEMPORAL_REVERSAL"
        verdict_msg = (
            f"TEMPORAL_REVERSAL: multi-agent gap reverses between first ({first_gap:.2f}) "
            f"and last third ({last_gap:.2f}). Pipeline improvement visible in data."
        )
    elif signals:
        verdict = "DISPATCH_PATTERN_FOUND"
        verdict_msg = (
            f"DISPATCH_PATTERN_FOUND: {len(signals)} sub-signal(s): {'; '.join(signals)}. "
            f"inline_main vs wrapper: V={v_inline:.3f}. "
            f"concreteness: V={v_conc:.3f}."
        )
    elif p_inline < 0.10 or p_conc < 0.10:
        verdict = "WEAK_DISPATCH_SIGNAL"
        verdict_msg = (
            f"WEAK_DISPATCH_SIGNAL: inline_main vs wrapper p={p_inline:.3f} V={v_inline:.3f}; "
            f"concreteness p={p_conc:.3f} V={v_conc:.3f}. Suggestive but below threshold."
        )
    else:
        verdict = "NO_REFINEMENT"
        verdict_msg = (
            f"NO_REFINEMENT: no dispatch sub-pattern improves on base multi-agent finding. "
            f"inline_main V={v_inline:.3f}, concreteness V={v_conc:.3f}. "
            f"Multi-agent gap is not explained by dispatch style or concreteness."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": {
            "n_verdicts": len(verdicts),
            "n_pass_fail": len(pass_fail),
            "dispatch_pass_rates": {
                ctx: r.get("pass_rate") for ctx, r in dispatch_results.items()
            },
            "chi2_inline_vs_wrapper": {
                "chi2": round(chi2_inline, 3), "p": round(p_inline, 4), "v": round(v_inline, 3),
            },
            "chi2_concreteness": {
                "chi2": round(chi2_conc, 3), "p": round(p_conc, 4), "v": round(v_conc, 3),
            },
            "temporal_gap": {
                "first_third_gap": round(first_gap, 3),
                "last_third_gap": round(last_gap, 3),
                "reversal": gap_reversal,
            },
            "top_failing_combos": combo_rates[:5],
            "signals_found": signals,
        },
        "dispatch_breakdown": dispatch_results,
        "temporal_stability": temporal_stats,
        "config": {},
    }

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
