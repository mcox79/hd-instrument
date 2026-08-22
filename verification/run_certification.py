"""Run the full verification suite and produce a markdown certification report.

Usage: python verification/run_certification.py [--output data/certification.md]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _verdict(result) -> tuple[str, str]:
    """(verdict, detail) derived from pytest's own summary -- never from a test's printed text.

    Distinguishes the three states that matter, because two of them look alike in raw output:
      PASS          tests ran and all passed
      FAIL          tests ran and some failed
      DID_NOT_RUN   the session aborted (collection error / INTERNALERROR) -- the failure mode that
                    hid for two days, because a report saying "0 failed" reads like success
    """
    out = (result.stdout or "") + (result.stderr or "")
    def n(pat: str) -> int:
        m = re.search(pat, out)
        return int(m.group(1)) if m else 0

    passed, failed, errors = n(r"(\d+) passed"), n(r"(\d+) failed"), n(r"(\d+) error")
    collected = n(r"(\d+) tests? collected")
    aborted = ("INTERNALERROR" in out) or ("Interrupted:" in out)

    if aborted or (collected and passed == 0 and failed == 0):
        return ("DID NOT RUN -- THE SESSION ABORTED",
                f"**{collected} tests were collected and {passed + failed} ran.** "
                f"{'An INTERNALERROR or collection error aborted the session. ' if aborted else ''}"
                f"**This is NOT a pass.** Nothing below may be read as evidence, including any "
                f"`RESULT: PASS` line printed by a test at import time.")
    if failed or errors or result.returncode != 0:
        return ("FAIL", f"**{passed} passed, {failed} failed, {errors} errors** "
                        f"(exit {result.returncode}).")
    return ("PASS", f"**{passed} passed, 0 failed** (exit {result.returncode}), "
                    f"{collected} collected.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/certification.md"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "verification/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    timestamp = datetime.now().isoformat(timespec="seconds")
    verdict, detail = _verdict(result)

    # THE VERDICT BLOCK GOES FIRST, AND IT IS NOT OPTIONAL (added 2026-08-22).
    # WHY: from 2026-08-20 this gate exited 3 having run ZERO of 456 collected tests -- a
    # script-style file under a test_* name raised SystemExit at module level, which pytest reports
    # as INTERNALERROR and which aborts the session. Nobody noticed for two days, because that
    # script's own `print("RESULT: PASS ...")` ran BEFORE the crash and landed at the top of the
    # raw output below. The exit code was in the report all along and was read past.
    # A report whose first line can be produced by a test's stray print is not a report.
    body = (
        "# hd-instrument certification report\n\n"
        f"## VERDICT: {verdict}\n\n"
        f"{detail}\n\n"
        f"Generated: {timestamp}\n"
        f"Exit code: {result.returncode}\n\n"
        "## pytest output\n\n"
        "```\n"
        f"{result.stdout}\n"
        "```\n\n"
        "## stderr\n\n"
        "```\n"
        f"{result.stderr}\n"
        "```\n"
    )
    args.output.write_text(body)
    # Print the VERDICT, not just the filename. The previous version printed only "Wrote <path>",
    # so an operator who did not open the file saw nothing at all about whether it passed -- which
    # is how a gate that ran zero tests was mistaken for a healthy one.
    print(f"VERDICT: {verdict}")
    print(re.sub(r"\*\*", "", detail))
    print(f"Wrote {args.output}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
