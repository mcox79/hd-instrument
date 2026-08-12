"""Verify a landing is genuinely a FULL run completion — NOT selftest or partial.

Anti-Fix-#28-recurrence infrastructure (2026-07-01).

Root cause it prevents: Orchestrator reports "landed"/"completed" based on queue.json
status (which fires after self-test gate), and Director propagates the claim without
verifying metrics.json off-disk. This tool reads metrics.json directly and returns a
crisp OK/FAIL with reason.

Usage:
    python tools/verify_landing.py <anchor>
    python tools/verify_landing.py --anchor <name> [--strict]
    python tools/verify_landing.py <anchor> --expect-mode smoke   # allow smoke as OK
    python tools/verify_landing.py <anchor1> <anchor2> ...        # batch

Exit codes:
    0 = OK (all requested anchors satisfy the mode/verdict gate)
    1 = FAIL (at least one anchor fails; per-anchor reason printed)
    2 = usage / internal error

Output lines (one per anchor):
    OK   <anchor>  run_mode=full verdict=HARD_PASS wall_s=42.1
    FAIL <anchor>  metrics_path_missing: <path>
    FAIL <anchor>  run_mode=selftest (expected full)
    FAIL <anchor>  verdict=RUNNING (partial/crash)
    FAIL <anchor>  verdict=STARTED (never advanced)
    FAIL <anchor>  verdict=SELFTEST_OK (never ran FULL)

References:
    ~/.claude/projects/d--AI/memory/feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md
    ~/.claude/projects/d--AI/memory/feedback_metrics_path_disambiguation_selftest_smoke_full_2026-06-27.md
    ~/.claude/projects/d--AI/memory/feedback_orchestrator_selftest_vs_full_disambiguation_2026-07-01.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# Verdicts that indicate the FULL run did NOT complete meaningfully
NON_TERMINAL_VERDICTS = {
    "RUNNING",       # cell mid-flight or crash-partial
    "STARTED",       # never advanced past init
    "SELFTEST_OK",   # only self-test gate passed; FULL never ran
    "IMPORT_CRASH",  # cell died on import
    "",              # empty verdict = never written
}


def _find_metrics_path(anchor: str) -> tuple[Path, bool]:
    """Return (path, exists). Try the canonical location, then SH-4 double-prefix."""
    canonical = DATA / f"exp_{anchor}" / "metrics.json"
    if canonical.exists():
        return canonical, True
    # SH-4 cosmetic double-prefix variant
    double = DATA / f"exp_exp_{anchor}" / "metrics.json"
    if double.exists():
        return double, True
    # If anchor already starts with 'exp_', try naked
    if anchor.startswith("exp_"):
        naked = DATA / anchor / "metrics.json"
        if naked.exists():
            return naked, True
    return canonical, False


def verify_one(anchor: str, expected_mode: str = "full", strict: bool = False) -> dict:
    """Verify a single anchor. Returns dict with 'ok' bool + 'reason' + fields.

    expected_mode: 'full' (default), 'smoke', or 'any' (accept smoke or full;
                   selftest still fails).
    strict: also require elapsed_s > 0 and cardinality_ok == True.
    """
    path, exists = _find_metrics_path(anchor)
    if not exists:
        return {
            "ok": False,
            "anchor": anchor,
            "reason": f"metrics_path_missing: {path}",
            "run_mode": None,
            "verdict": None,
            "wall_s": None,
        }
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {
            "ok": False,
            "anchor": anchor,
            "reason": f"metrics_json_unreadable: {e}",
            "run_mode": None,
            "verdict": None,
            "wall_s": None,
        }

    run_mode = d.get("run_mode")
    verdict = d.get("verdict", "")
    elapsed_s = d.get("elapsed_s", 0)
    cardinality_ok = d.get("cardinality_ok")

    # Normalize
    run_mode_s = str(run_mode) if run_mode is not None else ""
    verdict_s = str(verdict) if verdict is not None else ""

    # Gate 1: run_mode matches expectation
    if expected_mode == "any":
        if run_mode_s not in ("smoke", "full"):
            return {
                "ok": False, "anchor": anchor,
                "reason": f"run_mode={run_mode_s!r} (expected smoke or full)",
                "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
            }
    else:
        if run_mode_s != expected_mode:
            return {
                "ok": False, "anchor": anchor,
                "reason": f"run_mode={run_mode_s!r} (expected {expected_mode})",
                "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
            }

    # Gate 2: verdict is terminal
    if verdict_s in NON_TERMINAL_VERDICTS:
        return {
            "ok": False, "anchor": anchor,
            "reason": f"verdict={verdict_s!r} (non-terminal)",
            "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
        }

    # Gate 3 (strict): elapsed_s > 0
    if strict:
        try:
            if float(elapsed_s) <= 0.0:
                return {
                    "ok": False, "anchor": anchor,
                    "reason": f"strict: elapsed_s={elapsed_s} (expected >0)",
                    "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
                }
        except (TypeError, ValueError):
            return {
                "ok": False, "anchor": anchor,
                "reason": f"strict: elapsed_s unreadable ({elapsed_s!r})",
                "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
            }
        if cardinality_ok is not True:
            return {
                "ok": False, "anchor": anchor,
                "reason": f"strict: cardinality_ok={cardinality_ok!r} (expected True)",
                "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
            }

    return {
        "ok": True, "anchor": anchor,
        "reason": "",
        "run_mode": run_mode_s, "verdict": verdict_s, "wall_s": elapsed_s,
    }


def _fmt_line(r: dict) -> str:
    if r["ok"]:
        return (f"OK   {r['anchor']}  run_mode={r['run_mode']} "
                f"verdict={r['verdict']} wall_s={r['wall_s']}")
    return f"FAIL {r['anchor']}  {r['reason']}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Verify a landing is a genuine FULL run completion (not selftest/partial).")
    p.add_argument("anchors", nargs="*", help="one or more anchor names")
    p.add_argument("--anchor", action="append", default=[],
                   help="anchor name (repeatable; alternative to positional)")
    p.add_argument("--strict", action="store_true",
                   help="also require elapsed_s > 0 and cardinality_ok == True")
    p.add_argument("--expect-mode", default="full",
                   choices=["full", "smoke", "any"],
                   help="expected run_mode (default 'full')")
    p.add_argument("--json", action="store_true",
                   help="emit JSON output instead of human-readable lines")
    args = p.parse_args(argv)

    anchors = list(args.anchors) + list(args.anchor)
    if not anchors:
        p.print_usage()
        print("error: at least one anchor required", file=sys.stderr)
        return 2

    results = [verify_one(a, expected_mode=args.expect_mode, strict=args.strict)
               for a in anchors]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(_fmt_line(r))

    all_ok = all(r["ok"] for r in results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
