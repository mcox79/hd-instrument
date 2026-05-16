"""Run the full verification suite and produce a markdown certification report.

Usage: python verification/run_certification.py [--output data/certification.md]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


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
    body = (
        "# hd-instrument certification report\n\n"
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
    print(f"Wrote {args.output}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
