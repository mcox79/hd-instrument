"""Fix #29 -- preflight_check.py: machine-checkable 5-field PREFLIGHT SPEC gate.

Validates <cell_dir>/preflight_spec.yaml before dispatch.
Returns exit code 0 if all required sections + fields are present and structurally
valid; non-zero on any failure.

Integrates with tools/orchestrator/queue_add.sh: add --preflight <cell_dir> to
queue_add.sh to HARD_BLOCK dispatch on non-zero exit.

Usage:
    python tools/preflight_check.py <cell_dir> [--warn-only] [--smoke-metrics <metrics.json>]

    <cell_dir>          Directory containing preflight_spec.yaml (and optionally smoke
                        metrics.json for viability-gate checks).
    --warn-only         Emit warnings but exit 0 (use during WARN-mode ramp-up; per
                        handoff recommendation: run WARN-only for 3-5 cells before
                        enabling HARD_BLOCK).
    --smoke-metrics     Path to smoke metrics.json; if provided, runs viability-gate
                        checks (GATE_1..6 from neuroscience drill A1).

Background (sources):
    substrate-LM drill L3.1: 5-field preflight spec + retroactive falsifier (9/10 caught)
    neuroscience drill A1: 6 viability gates (slice-viability analog)
    handoff: Fix #29, load-bearing cert-discipline infrastructure

5 REQUIRED SECTIONS (all must be present; missing section = HARD_BLOCK):
    metric_scope        -- primary_metric, metric_class, appropriateness_justification
    baseline_provenance -- baseline_name, same_harness_as_arm, rerun_in_this_cell
    config_validity     -- required_resources (gpu_mem_gb/cpu_cores/wall_time_max_s),
                           oom_handling
    discriminator_ratio -- expected_arm_separation, null_arm_separation,
                           by_construction_saturation_check
    harm_prediction     -- setup_implies_metric_floor, what_would_falsify_setup_vs_mechanism,
                           fidelity_gap_documentation

VIABILITY GATES (run when --smoke-metrics provided):
    GATE_1: ARM_UNIGRAM_entropy reproduces expected vocab entropy log2(V) +/- 0.05
    GATE_2: ARM_RANDOM_W output is near-uniform (entropy > 0.90 * log2(V))
    GATE_3: ARM_BASELINE output entropy > 50% of log2(V) (non-degenerate)
    GATE_4: smoke_n_vs_full_n_ratio reported (smoke regime representativeness)
    GATE_5: per-arm runtime variance < 3x
    GATE_6: per-arm output magnitude L2 within 2x of baseline
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REQUIRED_TOP_LEVEL_SECTIONS = [
    "metric_scope",
    "baseline_provenance",
    "config_validity",
    "discriminator_ratio",
    "harm_prediction",
]

REQUIRED_FIELDS: dict[str, list[str]] = {
    "metric_scope": [
        "primary_metric",
        "metric_class",
        "appropriateness_justification",
    ],
    "baseline_provenance": [
        "baseline_name",
        "same_harness_as_arm",
        "rerun_in_this_cell",
    ],
    "config_validity": [
        "required_resources",
        "oom_handling",
    ],
    "discriminator_ratio": [
        "expected_arm_separation",
        "null_arm_separation",
        "by_construction_saturation_check",
    ],
    "harm_prediction": [
        "setup_implies_metric_floor",
        "what_would_falsify_setup_vs_mechanism",
        "fidelity_gap_documentation",
    ],
}

REQUIRED_RESOURCE_SUBFIELDS = ["gpu_mem_gb", "cpu_cores", "wall_time_max_s"]

VALID_METRIC_CLASSES = {
    "rank_based",
    "calibration_based",
    "embedding_geometry",
    "classification",
    "generation_quality",
    "information_theoretic",
    "other",
}

# Class-mismatch protection: mechanism classes that are rank-based by convention
RANK_BASED_MECHANISM_KEYWORDS = [
    "sparse",
    "retrieval",
    "associative",
    "pattern_completion",
    "vsa",
    "hyperdimensional",
    "hd",
    "top_1",
    "top_k",
    "recall",
]


def _load_yaml(path: Path) -> tuple[dict | None, str | None]:
    """Load YAML file. Returns (data, error_msg)."""
    if not _YAML_AVAILABLE:
        # Fallback: minimal YAML parser for flat structures
        return _load_yaml_fallback(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None, f"preflight_spec.yaml top level must be a mapping, got {type(data).__name__}"
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"
    except Exception as e:
        return None, f"File read error: {e}"


def _load_yaml_fallback(path: Path) -> tuple[dict | None, str | None]:
    """Minimal YAML key-detection when PyYAML is absent.
    Only checks top-level section presence -- structural validation is limited.
    Emits a warning that full validation requires PyYAML.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"File read error: {e}"
    data: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if ":" in stripped and not line.startswith(" ") and not line.startswith("\t"):
            key = stripped.split(":")[0].strip()
            rest = stripped[len(key) + 1:].strip()
            data[key] = rest or {}
    return data, None


def _is_nonempty(val: Any) -> bool:
    """Return True if the value is a non-empty string, non-empty dict, or non-empty list."""
    if val is None:
        return False
    if isinstance(val, bool):
        return True  # explicit True/False booleans are valid (e.g. same_harness_as_arm: true)
    if isinstance(val, str):
        return len(val.strip()) > 0
    if isinstance(val, (dict, list)):
        return len(val) > 0
    if isinstance(val, (int, float)):
        return True
    return False


def check_structural(spec: dict) -> list[str]:
    """Check 5-section + field presence. Returns list of error strings (empty = pass)."""
    errors: list[str] = []

    # 1. Top-level sections
    for sec in REQUIRED_TOP_LEVEL_SECTIONS:
        if sec not in spec:
            errors.append(f"MISSING_SECTION: '{sec}' is required but absent")
            continue
        sec_val = spec[sec]
        if not isinstance(sec_val, dict):
            errors.append(f"SECTION_NOT_MAPPING: '{sec}' must be a YAML mapping, got {type(sec_val).__name__}")
            continue

        # 2. Required fields within section
        for field in REQUIRED_FIELDS.get(sec, []):
            if field not in sec_val:
                errors.append(f"MISSING_FIELD: {sec}.{field} is required but absent")
            elif not _is_nonempty(sec_val[field]):
                errors.append(f"EMPTY_FIELD: {sec}.{field} is present but empty/null")

    # 3. config_validity.required_resources sub-fields
    if "config_validity" in spec and isinstance(spec["config_validity"], dict):
        rr = spec["config_validity"].get("required_resources")
        if isinstance(rr, dict):
            for sf in REQUIRED_RESOURCE_SUBFIELDS:
                if sf not in rr:
                    errors.append(
                        f"MISSING_SUBFIELD: config_validity.required_resources.{sf} is required"
                    )
        elif rr is not None:
            errors.append(
                "TYPE_ERROR: config_validity.required_resources must be a mapping"
                f" with keys {REQUIRED_RESOURCE_SUBFIELDS}"
            )

    # 4. metric_class validation
    if "metric_scope" in spec and isinstance(spec["metric_scope"], dict):
        mc = spec["metric_scope"].get("metric_class", "")
        if mc and isinstance(mc, str) and mc.lower() not in VALID_METRIC_CLASSES:
            errors.append(
                f"INVALID_METRIC_CLASS: '{mc}' not in {sorted(VALID_METRIC_CLASSES)}"
            )

    # 5. baseline_provenance: same_harness_as_arm and rerun_in_this_cell MUST be true
    if "baseline_provenance" in spec and isinstance(spec["baseline_provenance"], dict):
        bp = spec["baseline_provenance"]
        for bool_field in ["same_harness_as_arm", "rerun_in_this_cell"]:
            if bool_field in bp:
                val = bp[bool_field]
                if isinstance(val, bool) and val is False:
                    errors.append(
                        f"BASELINE_PROVENANCE_FAIL: {bool_field}=false -- "
                        f"baseline must be rerun in this cell under the same harness "
                        f"(Biderman 2024 'Lessons from Trenches'; REFORMS item 5.1)"
                    )
                elif isinstance(val, str) and val.lower() in ("false", "no", "0"):
                    errors.append(
                        f"BASELINE_PROVENANCE_FAIL: {bool_field}='{val}' -- "
                        f"must be true (no cross-cell baseline quoting)"
                    )

    # 6. discriminator_ratio: null_arm_separation must not exceed expected_arm_separation
    if "discriminator_ratio" in spec and isinstance(spec["discriminator_ratio"], dict):
        dr = spec["discriminator_ratio"]
        exp_sep = dr.get("expected_arm_separation")
        null_sep = dr.get("null_arm_separation")
        if (isinstance(exp_sep, (int, float)) and isinstance(null_sep, (int, float))
                and null_sep > exp_sep):
            errors.append(
                f"DISCRIMINATOR_RATIO_INVERSION: null_arm_separation ({null_sep}) > "
                f"expected_arm_separation ({exp_sep}) -- definitional inversion; "
                f"the null threshold should be lower than the expected signal threshold"
            )

    # 7. Class-mismatch protection: calibration_based metric on a rank-based mechanism
    if "metric_scope" in spec and isinstance(spec["metric_scope"], dict):
        ms = spec["metric_scope"]
        mc = str(ms.get("metric_class", "")).lower()
        justif = str(ms.get("appropriateness_justification", "")).lower()
        if mc == "calibration_based":
            # check if the justification mentions rank-based keywords without explicit justification
            has_rank_keyword = any(kw in justif for kw in RANK_BASED_MECHANISM_KEYWORDS)
            if has_rank_keyword:
                errors.append(
                    "CLASS_MISMATCH_WARN: metric_class='calibration_based' but "
                    "appropriateness_justification references rank-based mechanism keywords "
                    "(sparse/retrieval/vsa/etc). Verify CONSTRUCT-VALIDITY: "
                    "BPC/calibration cannot gate-fail a sparse top-1 retrieval mechanism. "
                    "Use metric_class='rank_based' or explicitly justify calibration choice."
                )

    return errors


def check_viability_gates(smoke_metrics: dict) -> list[tuple[str, str, bool]]:
    """Run 6 viability gates on smoke metrics. Returns list of (gate_id, msg, passed)."""
    results = []

    # Helper: pull from nested detail dict or top-level
    detail = smoke_metrics.get("detail", {})

    def get_val(*keys):
        for k in keys:
            if k in smoke_metrics:
                return smoke_metrics[k]
            if k in detail:
                return detail[k]
        return None

    by_arm = detail.get("by_arm_agg") or detail.get("by_arm") or {}

    # GATE_1: ARM_UNIGRAM reproduces vocab entropy log2(V) +/- 0.05
    unigram_entropy = get_val("arm_unigram_entropy", "unigram_entropy", "vocab_entropy")
    vocab_size = get_val("vocab_size", "V", "n_vocab")
    if unigram_entropy is not None and vocab_size is not None and vocab_size > 0:
        expected = math.log2(float(vocab_size))
        delta = abs(float(unigram_entropy) - expected)
        passed = delta <= 0.05
        results.append((
            "GATE_1",
            f"ARM_UNIGRAM entropy={unigram_entropy:.4f} expected=log2({vocab_size})={expected:.4f} "
            f"delta={delta:.4f} (threshold 0.05): {'PASS' if passed else 'FAIL'}",
            passed,
        ))
    else:
        # GATE_1 skipped if metrics not present -- emit info only
        results.append((
            "GATE_1",
            "ARM_UNIGRAM entropy not found in smoke metrics "
            "(keys: arm_unigram_entropy / unigram_entropy / vocab_entropy + vocab_size). SKIP.",
            True,  # skipped = not a failure
        ))

    # GATE_2: ARM_RANDOM_W produces near-uniform output (entropy > 0.90 * log2(V))
    random_entropy = get_val("arm_random_w_entropy", "random_w_entropy", "random_entropy")
    if random_entropy is not None and vocab_size is not None and vocab_size > 0:
        expected = math.log2(float(vocab_size))
        threshold = 0.90 * expected
        passed = float(random_entropy) >= threshold
        results.append((
            "GATE_2",
            f"ARM_RANDOM_W entropy={random_entropy:.4f} threshold=0.90*log2({vocab_size})={threshold:.4f}: "
            f"{'PASS' if passed else 'FAIL -- random-W arm is not near-uniform (rigged-harness risk)'}",
            passed,
        ))
    else:
        results.append((
            "GATE_2",
            "ARM_RANDOM_W entropy not found in smoke metrics. SKIP.",
            True,
        ))

    # GATE_3: ARM_BASELINE output entropy > 50% of log2(V)
    baseline_entropy = get_val("arm_baseline_entropy", "baseline_entropy")
    if baseline_entropy is not None and vocab_size is not None and vocab_size > 0:
        expected = math.log2(float(vocab_size))
        threshold = 0.50 * expected
        passed = float(baseline_entropy) >= threshold
        results.append((
            "GATE_3",
            f"ARM_BASELINE entropy={baseline_entropy:.4f} threshold=0.50*log2({vocab_size})={threshold:.4f}: "
            f"{'PASS' if passed else 'FAIL -- baseline output is degenerate (collapsed/non-discriminating)'}",
            passed,
        ))
    else:
        results.append((
            "GATE_3",
            "ARM_BASELINE entropy not found in smoke metrics. SKIP.",
            True,
        ))

    # GATE_4: smoke_n_vs_full_n ratio is present (smoke representativeness documented)
    smoke_n = get_val("smoke_n", "n_smoke", "N_smoke")
    full_n = get_val("full_n", "n_full", "N_full", "N")
    if smoke_n is not None and full_n is not None:
        ratio = float(smoke_n) / max(float(full_n), 1)
        # warn if ratio < 0.1 (smoke is < 10% of full N -- fidelity-gap risk)
        passed = ratio >= 0.01  # must be at least 1% to be a meaningful smoke
        results.append((
            "GATE_4",
            f"smoke_n={smoke_n} full_n={full_n} ratio={ratio:.3f}: "
            f"{'PASS' if passed else 'FAIL -- smoke N is <1% of full N (fidelity gap too large)'}"
            + (f" [WARN: smoke/full={ratio:.2f} < 0.10, fidelity-gap risk]" if passed and ratio < 0.10 else ""),
            passed,
        ))
    else:
        results.append((
            "GATE_4",
            "smoke_n / full_n not found in smoke metrics. SKIP.",
            True,
        ))

    # GATE_5: per-arm runtime variance < 3x (ISI-violation analog)
    arm_runtimes = get_val("per_arm_elapsed_s", "arm_elapsed_s", "arm_runtimes")
    if isinstance(arm_runtimes, dict) and len(arm_runtimes) >= 2:
        vals = [float(v) for v in arm_runtimes.values() if isinstance(v, (int, float)) and v > 0]
        if len(vals) >= 2:
            ratio = max(vals) / max(min(vals), 1e-9)
            passed = ratio < 3.0
            results.append((
                "GATE_5",
                f"per-arm runtime min={min(vals):.1f}s max={max(vals):.1f}s ratio={ratio:.2f}x "
                f"(threshold 3x): {'PASS' if passed else 'FAIL -- one arm is suspiciously fast/slow'}",
                passed,
            ))
        else:
            results.append(("GATE_5", "Insufficient per-arm timing values. SKIP.", True))
    else:
        results.append(("GATE_5", "per_arm_elapsed_s not found in smoke metrics. SKIP.", True))

    # GATE_6: per-arm output magnitude L2 within 2x of baseline
    arm_l2 = get_val("per_arm_output_l2", "arm_output_l2", "arm_l2_norms")
    if isinstance(arm_l2, dict) and "baseline" in arm_l2:
        baseline_l2 = float(arm_l2["baseline"])
        failures = []
        for arm, l2 in arm_l2.items():
            if arm == "baseline":
                continue
            ratio = float(l2) / max(baseline_l2, 1e-9)
            if ratio > 2.0 or ratio < 0.5:
                failures.append(f"{arm}: l2={l2:.4f} ratio_to_baseline={ratio:.2f}x")
        passed = len(failures) == 0
        results.append((
            "GATE_6",
            f"per-arm L2 magnitude vs baseline: "
            f"{'PASS' if passed else 'FAIL -- ' + '; '.join(failures) + ' (amplitude mismatch > 2x)'}",
            passed,
        ))
    else:
        results.append(("GATE_6", "per_arm_output_l2 not found in smoke metrics. SKIP.", True))

    return results


def run_check(
    cell_dir: Path,
    warn_only: bool = False,
    smoke_metrics_path: Path | None = None,
) -> tuple[bool, list[str], list[str]]:
    """
    Run the full preflight check.

    Returns (all_passed, errors_list, warnings_list).
    all_passed=True means exit 0.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Locate preflight_spec.yaml
    spec_path = cell_dir / "preflight_spec.yaml"
    if not spec_path.exists():
        errors.append(
            f"MISSING_SPEC: no preflight_spec.yaml found in {cell_dir}. "
            f"Every dispatched cell requires this file. "
            f"Use tools/preflight_spec_template.yaml as a starting point."
        )
        return False, errors, warnings

    # 2. Parse YAML
    spec, parse_err = _load_yaml(spec_path)
    if parse_err or spec is None:
        errors.append(f"PARSE_FAIL: {parse_err}")
        return False, errors, warnings

    if not _YAML_AVAILABLE:
        warnings.append(
            "YAML_FALLBACK: PyYAML not installed; using minimal section-detection only. "
            "Install PyYAML for full structural validation: pip install pyyaml"
        )

    # 3. Structural validation
    struct_errors = check_structural(spec)
    errors.extend(struct_errors)

    # 4. Viability gates (optional; only when smoke metrics provided)
    if smoke_metrics_path is not None:
        if not smoke_metrics_path.exists():
            warnings.append(
                f"SMOKE_METRICS_NOT_FOUND: {smoke_metrics_path} -- viability gates skipped"
            )
        else:
            try:
                smoke_data = json.loads(smoke_metrics_path.read_text(encoding="utf-8"))
            except Exception as e:
                warnings.append(f"SMOKE_METRICS_PARSE_ERROR: {e} -- viability gates skipped")
                smoke_data = None

            if smoke_data is not None:
                gate_results = check_viability_gates(smoke_data)
                for gate_id, msg, passed in gate_results:
                    if not passed:
                        errors.append(f"{gate_id}_FAIL: {msg}")
                    else:
                        warnings.append(f"{gate_id}_OK: {msg}")

    all_passed = len(errors) == 0
    return all_passed, errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Fix #29 preflight spec validator. Returns 0 if spec is valid, non-zero on errors."
    )
    parser.add_argument("cell_dir", help="Directory containing preflight_spec.yaml")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Emit errors as warnings but exit 0 (WARN-mode ramp-up period)",
    )
    parser.add_argument(
        "--smoke-metrics",
        metavar="METRICS_JSON",
        help="Path to smoke metrics.json for viability gate checks (optional)",
    )
    args = parser.parse_args()

    cell_dir = Path(args.cell_dir)
    if not cell_dir.exists():
        print(f"[preflight_check] ERROR: cell_dir not found: {cell_dir}", file=sys.stderr)
        sys.exit(2)

    smoke_path = Path(args.smoke_metrics) if args.smoke_metrics else None

    all_passed, errors, warnings = run_check(cell_dir, args.warn_only, smoke_path)

    print(f"[preflight_check] cell_dir={cell_dir}")

    if warnings:
        for w in warnings:
            print(f"  WARN: {w}")

    if errors:
        tag = "WARN" if args.warn_only else "ERROR"
        for e in errors:
            print(f"  {tag}: {e}")
    else:
        print("  STRUCTURAL_PASS: all required sections and fields present")
        if smoke_path:
            print("  VIABILITY_GATES: all executed gates passed")

    if args.warn_only:
        # In WARN-only mode, always exit 0 regardless of errors.
        # Used during the 3-5 cell ramp-up before enabling HARD_BLOCK.
        if errors:
            print(
                f"  WARN_MODE: {len(errors)} error(s) above would HARD_BLOCK in strict mode. "
                f"Fix before promoting to HARD_BLOCK."
            )
        sys.exit(0)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
