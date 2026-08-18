#!/usr/bin/env python
"""Report load-bearing artifacts that exist ONLY as untracked files on one disk.

WHY THIS EXISTS (2026-08-18, measured, not hypothetical). In a single night this project
nearly lost three separate results to bookkeeping rather than to science:

  - notes/LONG_TERM_PLAN.md      32,823 B, DIRECTOR-OWNED, empty git log, single copy.
  - notes/one_upstream_cause_findings_2026-08-17.md   44,019 B, untracked.
  - experiments/exp_verb_event_salient_population_matched_rescore_v1.py + its metrics.json
    -- THE PROGRAMME'S ONLY PROPERLY-CONTROLLED POSITIVE RESULT -- untracked.

Each was found by accident while looking for something else. That is the defect this tool
closes: the loss was silent, and nothing on disk announced it.

WHAT COUNTS AS LOAD-BEARING, and why each:
  experiments/*.py     an experiment cell IS the provenance of its numbers. Without the cell,
                       a metrics.json is an unreproducible assertion.
  data/**/metrics.json the result itself. This is the artifact every claim cites.
  notes/*.md           the reasoning and the verdicts. A number with no note is uninterpretable.
  tools/*.py           durable, reusable machinery other work imports.
  verification/*.py    the witnesses. An untracked witness proves nothing durably.

WHAT THIS TOOL DELIBERATELY DOES NOT DO:
  - It does NOT commit anything. Bulk-committing hundreds of files is a judgement call with
    real review cost, and it belongs to the operator, not to a script.
  - It does NOT touch .gitignore. Some exclusions are DELIBERATE (data/foundation/** has no
    backup and is excluded on purpose; data/encoder_eval_benchmarks/** is re-downloadable
    with a recorded checksum). Respecting a deliberate exclusion is correct behaviour, so
    anything gitignored is reported SEPARATELY and never mixed into the actionable count.
  - It does NOT rank by importance. It cannot know which result matters; it reports scale and
    lets a human look.

USAGE
  python tools/untracked_results_audit.py            # summary
  python tools/untracked_results_audit.py --list     # every path, grouped
  python tools/untracked_results_audit.py --strict   # exit 1 if anything untracked (for hooks)
  python tools/untracked_results_audit.py --self-test
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# (label, git pathspec, filename suffix filter)
CLASSES = [
    ("experiment cells", "experiments/", ".py"),
    ("results (metrics.json)", "data/", "metrics.json"),
    ("notes", "notes/", ".md"),
    ("tools", "tools/", ".py"),
    ("verification witnesses", "verification/", ".py"),
]


def _git(args: list) -> list:
    """Run git and return stdout lines. Empty list on failure -- never raises."""
    try:
        out = subprocess.run(
            ["git"] + args, cwd=str(REPO_ROOT),
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def untracked(pathspec: str, suffix: str) -> list:
    """Untracked files under pathspec matching suffix, RESPECTING .gitignore.

    --exclude-standard is what makes a deliberate exclusion invisible here, which is the
    intended behaviour: data/foundation/** is excluded on purpose and must not be reported
    as a hazard every run, or the report becomes noise and stops being read.
    """
    return [p for p in _git(["ls-files", "--others", "--exclude-standard", "--", pathspec])
            if p.endswith(suffix)]


def ignored(pathspec: str, suffix: str) -> list:
    """Files under pathspec that ARE gitignored -- reported separately, never as actionable."""
    return [p for p in _git(["ls-files", "--others", "--ignored", "--exclude-standard",
                             "--", pathspec])
            if p.endswith(suffix)]


def audit() -> dict:
    report = {}
    for label, spec, suffix in CLASSES:
        report[label] = {
            "untracked": untracked(spec, suffix),
            "gitignored": ignored(spec, suffix),
        }
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print every path, grouped by class")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is untracked")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        # The guard that matters: a deliberate exclusion must NOT be reported as actionable.
        rep = audit()
        ok = True
        for label, d in rep.items():
            overlap = set(d["untracked"]) & set(d["gitignored"])
            if overlap:
                print(f"[self-test] FAIL {label}: {len(overlap)} path(s) counted BOTH untracked "
                      f"and gitignored -- a deliberate exclusion is being reported as a hazard")
                ok = False
        if _git(["rev-parse", "--git-dir"]) == []:
            print("[self-test] FAIL git is not usable from this directory")
            ok = False
        else:
            print("[self-test] PASS git is reachable")
        print(f"[self-test] PASS deliberate exclusions are not double-counted" if ok else "")
        print(f"[self-test] OVERALL: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1

    rep = audit()
    total = sum(len(d["untracked"]) for d in rep.values())

    print("== UNTRACKED LOAD-BEARING ARTIFACTS ==")
    print("   (exists on ONE disk, no git history, no backup)")
    print()
    for label, d in rep.items():
        n = len(d["untracked"])
        flag = "  <-- " + ("nothing at risk" if n == 0 else "AT RISK") if True else ""
        print(f"   {label:<28} {n:>5}{flag}")
    print()
    print(f"   TOTAL AT RISK: {total}")
    print()
    print("   Gitignored (DELIBERATE exclusions, not hazards, listed for completeness):")
    for label, d in rep.items():
        if d["gitignored"]:
            print(f"     {label:<26} {len(d['gitignored']):>5}")
    print()
    print("   This tool does not commit and does not edit .gitignore -- both are operator calls.")

    if args.list:
        for label, d in rep.items():
            if not d["untracked"]:
                continue
            print()
            print(f"-- {label} ({len(d['untracked'])}) --")
            for p in sorted(d["untracked"]):
                print(f"   {p}")

    if args.strict and total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
