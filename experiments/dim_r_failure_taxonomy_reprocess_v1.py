"""
dim_r_failure_taxonomy_reprocess_v1

REPROCESS cell (Hidden-Dims Drill Dim R): categorize every metrics.json under
d:/AI/hd-instrument/data/ into failure-mode buckets. Cheap taxonomy over
existing verdicts + verdict_msg + arm-recall fields. No new experiments,
no discriminator, no queue dispatch.

Failure-mode buckets (Dim R taxonomy):
  - SILENT_FAIL:        recall < 0.10 AND no explicit HF verdict AND no rail-breach signal
                        (substrate silently returned wrong answer; worst-case for M3 conversational).
  - LOUD_FAIL:          explicit HF_* verdict at appropriate discriminator regime
                        (substrate correctly signaled failure).
  - HALLUCINATION_FAIL: recall < 0.30 AND MAX_SIM_TO_NON_TARGET > 0.60
                        (substrate returned confident wrong answer; also worst-case).
  - REFUSE_FAIL:        verdict in {RUNNING, CELL_CRASHED, DISPATCH_FAILURE, TIMEOUT, KILLED}
                        (operational failure, not substrate failure).
  - HP_CORRECT:         recall >= 0.70 AND verdict starts with HARD_PASS or HP_
                        (substrate correctly answered).
  - UNCATEGORIZED:      landed but doesn't match any bucket rule (e.g. MIDDLE_BAND, PARTIAL,
                        or missing recall fields). Retained for honest audit.

Output:
  d:/AI/hd-instrument/data/exp_dim_r_failure_taxonomy_reprocess_v1/
      metrics.json                                   # summary: bucket counts + HP verdict
      failure_taxonomy_2026-07-02.jsonl              # per-anchor bucket + rationale

HP conditions:
  HP_LOUD_FAILURE_DOMINANT:  (SILENT_FAIL + HALLUCINATION_FAIL) / failures < 0.10
                             Substrate self-signals when it fails; good for M3.
  HF_SILENT_FAILURE_HIGH:    (SILENT_FAIL + HALLUCINATION_FAIL) / failures > 0.30
                             M3 threat model; external monitoring required.

Discipline:
  - ASCII only, no unicode.
  - Atomic write (tmp + os.replace).
  - Deterministic bucket assignment (no randomness).
  - Read-only over data/; only writes its own output dir.
  - No torch, no numpy, no external deps beyond stdlib.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

# Regex to extract recall-like numeric from verdict_msg strings.
# Matches e.g. "recall=0.65", "substrate_recall: 0.42", "acc 0.03", "top1=0.95".
_RECALL_PAT = re.compile(
    r"\b(recall|substrate_recall|acc|top1|top1_recall|fidelity|score|"
    r"cortex_recall|hp_recall|final_recall)[=:\s]+([01]?\.\d+|[01])\b",
    re.I,
)
# Match confusion / non-target sim in verdict_msg.
_NONTARGET_PAT = re.compile(
    r"\b(max_sim_to_non_target|max_nontarget|confusion_max|nontarget_sim)"
    r"[=:\s]+([01]?\.\d+|[01])\b",
    re.I,
)

REPO = Path("d:/AI/hd-instrument")
DATA_ROOT = REPO / "data"
OUT_DIR = DATA_ROOT / "exp_dim_r_failure_taxonomy_reprocess_v1"

# Verdict-string prefixes that mean explicit hard-fail (substrate signaled failure loudly).
LOUD_HF_PREFIXES = (
    "HARD_FAIL", "HF_", "MIDDLE_BAND_FAIL", "FAIL", "REJECTED",
    "SATURATED", "SATURATION", "NOT_REPLICATED", "REPLICATION_FAIL",
    "CEILING", "CLIFF", "SILENT_DROP",
)

# Verdicts meaning the cell never produced substrate-level results (operational).
REFUSE_VERDICTS = {
    "RUNNING",
    "CELL_CRASHED",
    "DISPATCH_FAILURE",
    "TIMEOUT",
    "KILLED",
    "ERROR",
    "CRASHED",
    "SCRIPT_ERROR",
    "SELFTEST_OK",  # cell only ran selftest, no substrate result
    "UNKNOWN",      # cell landed without producing verdict
    "",             # empty verdict
    "EMPTY",
}

# Verdict prefixes meaning substrate answered correctly.
HP_PREFIXES = (
    "HARD_PASS", "HP_", "PASS", "SMOKE_PASS", "BET_", "BURST_PASS",
    "V_PASS", "FOURSTAGE_HARD_PASS", "ON_ENVELOPE", "REPLICATED",
    "CONFIRMED", "STRONG", "R17_AREA_LAW_LIKE",
)

# Thresholds (per drill spec).
SILENT_RECALL_MAX = 0.10
HALLUC_RECALL_MAX = 0.30
HALLUC_NONTARGET_MIN = 0.60
HP_RECALL_MIN = 0.70


def _extract_recall(metrics):
    """Best-effort scan for a representative recall field.

    Path A: top-level scalar keys ('recall', 'substrate_recall', etc.)
    Path B: common array-of-rows keys with recall inside.
    Path C: regex parse over verdict_msg / summary strings.

    Returns the MAX substrate-arm recall found (worst-case-recall would
    flag silent-fail even when best arm is HP; we want peak-substrate).
    """
    for key in ("recall", "best_recall", "substrate_recall", "top1_recall",
                "cortex_recall", "final_recall", "substrate_acc",
                "positive_control_recall", "nc_recall_mean", "hm_recall_mean",
                "int8_recall_mean_at_M_nominal"):
        v = metrics.get(key)
        if isinstance(v, (int, float)):
            return float(v)

    # Scan common array fields.
    for arr_key in ("phase_map", "arms", "per_arm_rows", "arm_results",
                    "sweep", "results", "rows", "sweep_results"):
        arr = metrics.get(arr_key)
        if isinstance(arr, list) and arr:
            best = None
            for row in arr:
                if not isinstance(row, dict):
                    continue
                for k in ("substrate_recall", "recall", "top1_recall",
                          "cortex_recall", "substrate_acc"):
                    rv = row.get(k)
                    if isinstance(rv, (int, float)):
                        if best is None or rv > best:
                            best = float(rv)
            if best is not None:
                return best

    # Path C: parse verdict_msg / summary regex.
    for msg_key in ("verdict_msg", "summary"):
        msg = str(metrics.get(msg_key, ""))
        if not msg:
            continue
        best = None
        for _key, val in _RECALL_PAT.findall(msg):
            try:
                fv = float(val)
                if best is None or fv > best:
                    best = fv
            except ValueError:
                pass
        if best is not None:
            return best
    return None


def _extract_max_nontarget_sim(metrics):
    """Best-effort scan for MAX_SIM_TO_NON_TARGET style fields."""
    for key in ("max_sim_to_non_target", "MAX_SIM_TO_NON_TARGET",
                "max_nontarget_sim", "confusion_max"):
        v = metrics.get(key)
        if isinstance(v, (int, float)):
            return float(v)
    # Scan array rows.
    for arr_key in ("phase_map", "arms", "per_arm_rows", "arm_results",
                    "sweep", "results", "rows"):
        arr = metrics.get(arr_key)
        if isinstance(arr, list) and arr:
            best = None
            for row in arr:
                if not isinstance(row, dict):
                    continue
                for k in ("max_sim_to_non_target", "max_nontarget_sim"):
                    rv = row.get(k)
                    if isinstance(rv, (int, float)):
                        if best is None or rv > best:
                            best = float(rv)
            if best is not None:
                return best
    # Regex path.
    for msg_key in ("verdict_msg", "summary"):
        msg = str(metrics.get(msg_key, ""))
        if not msg:
            continue
        best = None
        for _key, val in _NONTARGET_PAT.findall(msg):
            try:
                fv = float(val)
                if best is None or fv > best:
                    best = fv
            except ValueError:
                pass
        if best is not None:
            return best
    return None


def _extract_rail_breach(metrics):
    """Detect any rail-breach or explicit warning flag in the metrics."""
    for key in ("rail_breach", "rail_breached", "invariant_breach",
                "hf_signal_fired"):
        v = metrics.get(key)
        if v is True:
            return True
        if isinstance(v, (int, float)) and v > 0:
            return True
    vm = str(metrics.get("verdict_msg", ""))
    if "RAIL_BREACH" in vm or "INVARIANT_BREACH" in vm:
        return True
    return False


def classify(metrics_path, metrics):
    """Deterministic bucket assignment. Returns (bucket, rationale)."""
    verdict = str(metrics.get("verdict", "")).strip().upper()
    verdict_msg = str(metrics.get("verdict_msg", ""))

    # REFUSE_FAIL: operational failure.
    if verdict in REFUSE_VERDICTS:
        return "REFUSE_FAIL", f"verdict={verdict}"
    for pref in ("CRASH", "DISPATCH_FAIL", "TIMEOUT", "KILL"):
        if pref in verdict:
            return "REFUSE_FAIL", f"verdict-contains-{pref}"

    recall = _extract_recall(metrics)
    max_nt = _extract_max_nontarget_sim(metrics)
    rail = _extract_rail_breach(metrics)

    # LOUD if verdict starts with a known HF prefix, OR contains _HARD_FAIL /
    # _HF_ / _FAIL / _SATURATION / _CEILING / _CLIFF as substring (cell-specific
    # verdict families like QE2_DD_HARD_FAIL, H_HARD_FAIL).
    is_hf_loud = (
        any(verdict.startswith(p) for p in LOUD_HF_PREFIXES)
        or "_HARD_FAIL" in verdict
        or "_HF_" in verdict
        or "_FAIL" in verdict
        or verdict.endswith("_FAIL")
        or verdict.endswith("_SATURATION")
        or verdict.endswith("_CEILING")
        or rail
    )
    is_hp = (
        any(verdict.startswith(p) for p in HP_PREFIXES)
        or "_HARD_PASS" in verdict
        or verdict.endswith("_PASS")
    )

    # HALLUCINATION_FAIL takes priority over SILENT_FAIL (confident-wrong is worst).
    if recall is not None and max_nt is not None:
        if recall < HALLUC_RECALL_MAX and max_nt > HALLUC_NONTARGET_MIN:
            return ("HALLUCINATION_FAIL",
                    f"recall={recall:.3f}<{HALLUC_RECALL_MAX} "
                    f"AND max_nontarget={max_nt:.3f}>{HALLUC_NONTARGET_MIN}")

    # LOUD_FAIL: explicit HF verdict.
    if is_hf_loud:
        return "LOUD_FAIL", f"verdict={verdict} (loud HF prefix or rail-breach)"

    # SILENT_FAIL: low recall, no loud signal.
    if recall is not None and recall < SILENT_RECALL_MAX and not is_hf_loud:
        return ("SILENT_FAIL",
                f"recall={recall:.3f}<{SILENT_RECALL_MAX}, "
                f"no HF verdict (verdict={verdict})")

    # HP_CORRECT.
    if is_hp and recall is not None and recall >= HP_RECALL_MIN:
        return "HP_CORRECT", f"verdict={verdict}, recall={recall:.3f}>={HP_RECALL_MIN}"
    if is_hp and recall is None:
        # HP declared but no extractable recall; still substrate-signaled success.
        return "HP_CORRECT", f"verdict={verdict}, recall=unextractable"

    return ("UNCATEGORIZED",
            f"verdict={verdict}, recall={recall}, max_nt={max_nt}")


def _atomic_write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _self_test():
    """Assert bucket rules fire on synthetic cases before scanning 5k files."""
    cases = [
        # (metrics, expected_bucket)
        ({"verdict": "RUNNING"}, "REFUSE_FAIL"),
        ({"verdict": "CELL_CRASHED"}, "REFUSE_FAIL"),
        ({"verdict": "HARD_PASS", "recall": 0.85}, "HP_CORRECT"),
        ({"verdict": "HARD_FAIL_saturation", "recall": 0.05}, "LOUD_FAIL"),
        ({"verdict": "PASS", "recall": 0.05,
          "max_sim_to_non_target": 0.75}, "HALLUCINATION_FAIL"),
        ({"verdict": "PARTIAL", "recall": 0.03}, "SILENT_FAIL"),
        ({"verdict": "MIDDLE_BAND", "recall": 0.35}, "UNCATEGORIZED"),
    ]
    for m, expected in cases:
        got, why = classify(Path("selftest"), m)
        assert got == expected, f"expected {expected}, got {got} for {m}: {why}"
    print("selftest: 7/7 OK", flush=True)


def main(argv):
    if "--self-test" in argv:
        _self_test()
        return 0

    t0 = time.time()
    _self_test()  # gate before real scan

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = OUT_DIR / "failure_taxonomy_2026-07-02.jsonl"
    metrics_path = OUT_DIR / "metrics.json"

    buckets = {
        "SILENT_FAIL": 0,
        "LOUD_FAIL": 0,
        "HALLUCINATION_FAIL": 0,
        "REFUSE_FAIL": 0,
        "HP_CORRECT": 0,
        "UNCATEGORIZED": 0,
    }
    worst_case_anchors = []  # SILENT_FAIL + HALLUCINATION_FAIL

    n_scanned = 0
    n_unreadable = 0
    n_recall_extracted = 0
    n_nontarget_extracted = 0

    # Enumerate all metrics.json 1 level deep under data/.
    with open(jsonl_path, "w", encoding="utf-8") as fout:
        for sub in DATA_ROOT.iterdir():
            if not sub.is_dir():
                continue
            mpath = sub / "metrics.json"
            if not mpath.exists():
                continue
            n_scanned += 1
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    m = json.load(f)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
                n_unreadable += 1
                fout.write(json.dumps({
                    "anchor_dir": sub.name,
                    "bucket": "UNCATEGORIZED",
                    "rationale": f"unreadable: {type(e).__name__}",
                }) + "\n")
                buckets["UNCATEGORIZED"] += 1
                continue

            # Track extraction coverage before classify (for honest reporting).
            if _extract_recall(m) is not None:
                n_recall_extracted += 1
            if _extract_max_nontarget_sim(m) is not None:
                n_nontarget_extracted += 1

            bucket, rationale = classify(mpath, m)
            buckets[bucket] += 1
            row = {
                "anchor_dir": sub.name,
                "anchor_name": m.get("anchor_name", sub.name),
                "verdict": m.get("verdict", ""),
                "verdict_msg": m.get("verdict_msg", "")[:200],
                "bucket": bucket,
                "rationale": rationale,
            }
            fout.write(json.dumps(row) + "\n")
            if bucket in ("SILENT_FAIL", "HALLUCINATION_FAIL"):
                worst_case_anchors.append({
                    "anchor_dir": sub.name,
                    "bucket": bucket,
                    "rationale": rationale,
                })

    # HP condition computation.
    failures = (buckets["SILENT_FAIL"] + buckets["LOUD_FAIL"]
                + buckets["HALLUCINATION_FAIL"])
    worst = buckets["SILENT_FAIL"] + buckets["HALLUCINATION_FAIL"]
    worst_frac = (worst / failures) if failures > 0 else 0.0

    if failures == 0:
        verdict = "UNCATEGORIZED"
        verdict_msg = (f"UNCATEGORIZED | no substrate failures in {n_scanned} "
                       f"anchors (HP_CORRECT={buckets['HP_CORRECT']})")
    elif worst_frac < 0.10:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP_LOUD_FAILURE_DOMINANT | worst_frac={worst_frac:.3f}"
                       f" < 0.10 across {failures} failures "
                       f"(SILENT={buckets['SILENT_FAIL']} "
                       f"HALLUC={buckets['HALLUCINATION_FAIL']} "
                       f"LOUD={buckets['LOUD_FAIL']}); "
                       f"substrate self-signals failures")
    elif worst_frac > 0.30:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_SILENT_FAILURE_HIGH | worst_frac={worst_frac:.3f}"
                       f" > 0.30 across {failures} failures "
                       f"(SILENT={buckets['SILENT_FAIL']} "
                       f"HALLUC={buckets['HALLUCINATION_FAIL']} "
                       f"LOUD={buckets['LOUD_FAIL']}); "
                       f"M3 threat model - external monitoring required")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND | worst_frac={worst_frac:.3f} in "
                       f"[0.10, 0.30] across {failures} failures "
                       f"(SILENT={buckets['SILENT_FAIL']} "
                       f"HALLUC={buckets['HALLUCINATION_FAIL']} "
                       f"LOUD={buckets['LOUD_FAIL']})")

    recall_coverage = (n_recall_extracted / n_scanned) if n_scanned else 0.0
    nontarget_coverage = (n_nontarget_extracted / n_scanned) if n_scanned else 0.0

    # If extraction coverage is very low, SILENT_FAIL / HALLUC counts are
    # NOT credible — flag verdict accordingly.
    if recall_coverage < 0.20:
        verdict = "UNCATEGORIZED"
        verdict_msg = (f"UNCATEGORIZED_EXTRACTION_LIMITED | recall extracted "
                       f"in only {recall_coverage:.1%} of {n_scanned} cells; "
                       f"SILENT_FAIL/HALLUC bucket counts NOT credible. "
                       f"Verdict-string buckets ARE credible: "
                       f"HP_CORRECT={buckets['HP_CORRECT']} "
                       f"LOUD_FAIL={buckets['LOUD_FAIL']} "
                       f"REFUSE_FAIL={buckets['REFUSE_FAIL']} "
                       f"UNCATEG={buckets['UNCATEGORIZED']}")

    summary = {
        "anchor_name": "dim_r_failure_taxonomy_reprocess_v1",
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "reprocess",
        "n_scanned": n_scanned,
        "n_unreadable": n_unreadable,
        "n_recall_extracted": n_recall_extracted,
        "n_nontarget_extracted": n_nontarget_extracted,
        "recall_extraction_coverage": round(recall_coverage, 4),
        "nontarget_extraction_coverage": round(nontarget_coverage, 4),
        "buckets": buckets,
        "failures_total": failures,
        "worst_case_total": worst,
        "worst_case_fraction": round(worst_frac, 4),
        "hp_conditions": {
            "HP_LOUD_FAILURE_DOMINANT_threshold": 0.10,
            "HF_SILENT_FAILURE_HIGH_threshold": 0.30,
        },
        "worst_case_anchors_sample": worst_case_anchors[:50],
        "worst_case_anchors_count": len(worst_case_anchors),
        "jsonl_path": str(jsonl_path).replace("\\", "/"),
        "config_version": ("ANCHOR=dim_r_failure_taxonomy_reprocess_v1,"
                           "mode=reprocess,SILENT_RECALL_MAX=0.10,"
                           "HALLUC_RECALL_MAX=0.30,"
                           "HALLUC_NONTARGET_MIN=0.60,HP_RECALL_MIN=0.70"),
    }

    _atomic_write_json(metrics_path, summary)
    print(f"scanned={n_scanned} unreadable={n_unreadable} "
          f"buckets={buckets} verdict={verdict}", flush=True)
    print(f"metrics: {metrics_path}", flush=True)
    print(f"jsonl:   {jsonl_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
