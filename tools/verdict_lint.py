"""Fix #30 -- verdict_lint.py: WHAT_THIS_DOES_NOT_SHOW lint for verdict_msg.

Enforces the mandatory HONEST_NEGATIVE_FRAMING clause on every verdict_msg.
Missing clause = lint_error. Can be used as a pre-commit hook.

Usage:
    python tools/verdict_lint.py <metrics.json> [more.json ...]
    python tools/verdict_lint.py --dir <experiment_dir>
    python tools/verdict_lint.py --stdin    (reads verdict_msg text from stdin)

Returns:
    exit code 0 if all checked verdict_msgs pass the lint.
    exit code 1 if any verdict_msg is missing the required clause.

Pre-commit hook integration:
    Add to .git/hooks/pre-commit:
        python tools/verdict_lint.py --staged-metrics
    or use pre-commit framework with:
        - id: verdict-lint
          name: verdict-lint
          entry: python tools/verdict_lint.py
          language: python
          files: metrics.json$

Background (sources):
    substrate-LM drill L3.2 (FIX #2: MANDATORY HONEST_NEGATIVE_FRAMING line)
    neuroscience drill A3 (Kriegeskorte structural blinding)
    Fix #28 recurrence: 4x over-claiming in one session despite explicit cultural awareness.
    The fix is structural cost-gradient inversion -- the honest framing MUST be cheaper
    than the omitted framing (because omission triggers lint failure, which is more
    expensive to fix than writing 2-3 honest bullets).

REQUIRED CLAUSE FORMAT (in verdict_msg field of metrics.json):
    WHAT_THIS_DOES_NOT_SHOW:
    - <does not compare to X baseline because Y>
    - <does not generalize beyond Z corpus>
    [1-3 bullets minimum]

See tools/verdict_template.txt for the full template.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


REQUIRED_CLAUSE = "WHAT_THIS_DOES_NOT_SHOW"
MIN_BULLETS = 1   # minimum number of "- " bullets required after the clause header
RECOMMENDED_BULLETS = 2  # issue a warning if fewer than this many bullets


def _extract_verdict_msg(data: dict) -> str | None:
    """Extract verdict_msg from metrics.json data."""
    # Try common locations
    for key in ("verdict_msg", "verdict", "summary"):
        if key in data:
            val = data[key]
            if isinstance(val, str):
                return val
    # Check nested detail
    detail = data.get("detail", {})
    for key in ("verdict_msg", "verdict", "summary"):
        if key in detail:
            val = detail[key]
            if isinstance(val, str):
                return val
    return None


def lint_verdict_msg(text: str) -> tuple[bool, list[str], list[str]]:
    """
    Lint a verdict_msg string.

    Returns (passed, errors, warnings).
    passed=True means the lint check passes.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Check for the required clause header
    upper = text.upper()
    clause_start = upper.find(REQUIRED_CLAUSE)
    if clause_start == -1:
        errors.append(
            f"MISSING_CLAUSE: '{REQUIRED_CLAUSE}:' clause is absent from verdict_msg. "
            f"Every verdict_msg MUST end with this clause listing 1-3 bullets describing "
            f"what the result does NOT show (Munafoo 2017 manifesto; Fix #30). "
            f"Use tools/verdict_template.txt as a template."
        )
        return False, errors, warnings

    # 2. Extract the clause body (everything after the clause header)
    clause_body = text[clause_start + len(REQUIRED_CLAUSE):]
    # Strip optional ":"
    clause_body = clause_body.lstrip(":")

    # 3. Count bullets (lines starting with "- ")
    bullets = []
    for line in clause_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and len(stripped) > 3:
            bullets.append(stripped)
        elif stripped.startswith("-") and len(stripped) > 2:
            # Handle "- " with extra content even if no space
            bullets.append(stripped)

    # 4. Validate bullet count
    if len(bullets) < MIN_BULLETS:
        errors.append(
            f"INSUFFICIENT_BULLETS: {REQUIRED_CLAUSE}: clause found but has {len(bullets)} "
            f"non-empty bullet(s); minimum is {MIN_BULLETS}. "
            f"Write at least {MIN_BULLETS} bullet(s) describing what the verdict does not show "
            f"(e.g. 'does not compare to X because Y', 'does not generalize to Z', "
            f"'does not establish W mechanism is responsible')."
        )
        return False, errors, warnings

    if len(bullets) < RECOMMENDED_BULLETS:
        warnings.append(
            f"LOW_BULLET_COUNT: {REQUIRED_CLAUSE}: clause has {len(bullets)} bullet(s); "
            f"recommended minimum is {RECOMMENDED_BULLETS} for honest coverage. "
            f"Consider adding more scope-limiting bullets."
        )

    # 5. Check for cargo-cult empty bullets (just "- " with no content)
    empty_bullets = [b for b in bullets if len(b.strip("- ").strip()) < 5]
    if empty_bullets:
        errors.append(
            f"EMPTY_BULLETS: {len(empty_bullets)} bullet(s) appear to be placeholder / empty: "
            f"{empty_bullets}. Bullets must contain substantive scope-limiting text."
        )
        return False, errors, warnings

    # 6. Check for placeholder text (cargo-cult fill)
    placeholder_markers = [
        "replace_me",
        "todo",
        "tbd",
        "placeholder",
        "example text",
        "does not compare to x",  # literal template text
        "does not generalize beyond z",  # literal template text
        "does not establish w",  # literal template text
    ]
    for bullet in bullets:
        bl = bullet.lower()
        for marker in placeholder_markers:
            if marker in bl:
                warnings.append(
                    f"PLACEHOLDER_BULLET: bullet appears to contain unedited template text: "
                    f"'{bullet[:80]}'. Replace with specific scope-limiting text for this cell."
                )
                break

    return True, errors, warnings


def lint_file(metrics_path: Path) -> tuple[bool, list[str], list[str]]:
    """Lint a single metrics.json file."""
    errors: list[str] = []
    warnings: list[str] = []

    if not metrics_path.exists():
        errors.append(f"FILE_NOT_FOUND: {metrics_path}")
        return False, errors, warnings

    try:
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"PARSE_ERROR: {metrics_path}: {e}")
        return False, errors, warnings

    verdict_msg = _extract_verdict_msg(data)
    if verdict_msg is None:
        errors.append(
            f"NO_VERDICT_MSG: {metrics_path} has no verdict_msg / verdict / summary field. "
            f"All metrics.json files must include a verdict_msg. "
            f"Use tools/verdict_template.txt."
        )
        return False, errors, warnings

    passed, v_errors, v_warnings = lint_verdict_msg(verdict_msg)
    errors.extend(v_errors)
    warnings.extend(v_warnings)
    return passed, errors, warnings


def lint_staged_metrics() -> list[tuple[Path, bool, list[str], list[str]]]:
    """Find git-staged metrics.json files and lint them."""
    import subprocess
    results = []
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            text=True,
        )
        for line in out.splitlines():
            line = line.strip()
            if line.endswith("metrics.json"):
                p = Path(line)
                passed, errors, warnings = lint_file(p)
                results.append((p, passed, errors, warnings))
    except subprocess.CalledProcessError:
        pass
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fix #30 verdict_lint: enforce WHAT_THIS_DOES_NOT_SHOW clause in verdict_msg"
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="metrics.json",
        help="One or more metrics.json files to lint",
    )
    parser.add_argument(
        "--dir",
        metavar="DIR",
        help="Recursively lint all metrics.json in a directory",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read verdict_msg text directly from stdin",
    )
    parser.add_argument(
        "--staged-metrics",
        action="store_true",
        help="Lint git-staged metrics.json files (for pre-commit hook use)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Emit errors as warnings but exit 0 (ramp-up period)",
    )
    args = parser.parse_args()

    all_passed = True
    any_checked = False

    if args.stdin:
        text = sys.stdin.read()
        passed, errors, warnings = lint_verdict_msg(text)
        any_checked = True
        print("[verdict_lint] stdin verdict_msg")
        for w in warnings:
            print(f"  WARN: {w}")
        if errors:
            for e in errors:
                tag = "WARN" if args.warn_only else "ERROR"
                print(f"  {tag}: {e}")
            if not args.warn_only:
                all_passed = False
        else:
            print("  PASS: WHAT_THIS_DOES_NOT_SHOW clause present and valid")

    if args.staged_metrics:
        staged_results = lint_staged_metrics()
        for fpath, passed, errors, warnings in staged_results:
            any_checked = True
            print(f"[verdict_lint] {fpath}")
            for w in warnings:
                print(f"  WARN: {w}")
            if errors:
                for e in errors:
                    tag = "WARN" if args.warn_only else "ERROR"
                    print(f"  {tag}: {e}")
                if not args.warn_only:
                    all_passed = False
            else:
                print("  PASS")

    if args.dir:
        dir_path = Path(args.dir)
        for mpath in sorted(dir_path.rglob("metrics.json")):
            any_checked = True
            passed, errors, warnings = lint_file(mpath)
            print(f"[verdict_lint] {mpath}")
            for w in warnings:
                print(f"  WARN: {w}")
            if errors:
                for e in errors:
                    tag = "WARN" if args.warn_only else "ERROR"
                    print(f"  {tag}: {e}")
                if not args.warn_only:
                    all_passed = False
            else:
                print("  PASS")

    for farg in args.files:
        fpath = Path(farg)
        any_checked = True
        passed, errors, warnings = lint_file(fpath)
        print(f"[verdict_lint] {fpath}")
        for w in warnings:
            print(f"  WARN: {w}")
        if errors:
            for e in errors:
                tag = "WARN" if args.warn_only else "ERROR"
                print(f"  {tag}: {e}")
            if not args.warn_only:
                all_passed = False
        else:
            print("  PASS")

    if not any_checked:
        parser.print_help()
        sys.exit(0)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
