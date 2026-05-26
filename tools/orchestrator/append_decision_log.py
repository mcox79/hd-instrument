#!/usr/bin/env python
"""Append content to a decision-log file while preserving its existing EOL convention.

Why this exists: direct Edit-tool appends to CRLF-line-ending files may normalize them
to LF, producing thousands of lines of git-diff churn that mask the ~60 lines of actual
content change. This helper:

  1. Reads target file bytes, detects existing EOL convention (CRLF vs LF).
  2. Re-encodes the appended content using the same EOL.
  3. Writes atomically via .tmp + os.replace.
  4. Prints the EOL convention and bytes written so the caller can confirm.

Usage:

  python append_decision_log.py <file_path> --content "<content>"
  python append_decision_log.py <file_path> --content-file <path>

If --content-file is given, the file's bytes are read literally (no decoding), then
re-encoded under the target's EOL convention.

Exit codes:
  0 — wrote successfully
  1 — bad arguments or target unreadable
  2 — target does not exist (helper does not create files)

See [[feedback-decision-log-eol-handling]] and [[feedback-cap-map-update-protocol]].
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys


def detect_eol(data: bytes) -> bytes:
    """Detect the dominant EOL convention in `data`.

    Returns b'\\r\\n' if CRLF is present in the majority, else b'\\n'.
    Empty files default to LF (the platform-neutral choice for new content).
    """
    if not data:
        return b"\n"
    crlf = data.count(b"\r\n")
    # Count standalone LFs (LF not preceded by CR).
    lf_total = data.count(b"\n")
    lf_only = lf_total - crlf
    if crlf >= lf_only:
        return b"\r\n"
    return b"\n"


def normalize_to_eol(content: str | bytes, eol: bytes) -> bytes:
    """Re-encode `content` so all line endings match `eol`."""
    if isinstance(content, str):
        # str → bytes via utf-8; first normalize all to \n then expand to target eol.
        b = content.encode("utf-8")
    else:
        b = content
    # Normalize: \r\n → \n, then any remaining \r → \n.
    b = b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if eol == b"\n":
        return b
    return b.replace(b"\n", b"\r\n")


def append_atomic(target: pathlib.Path, payload: bytes) -> None:
    """Write target_existing_bytes + payload to a .tmp sibling, then os.replace.

    Atomic on POSIX and on Windows (Python 3.3+ os.replace is atomic).
    """
    existing = target.read_bytes()
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_bytes(existing + payload)
    os.replace(tmp, target)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file_path", help="Target decision-log file (must exist).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--content", help="Content to append (string).")
    g.add_argument(
        "--content-file",
        help="Read content from this file (treated as utf-8 text; EOLs renormalized).",
    )
    p.add_argument(
        "--ensure-leading-newline",
        action="store_true",
        help="If target does not already end with a newline, prepend one to the payload.",
    )
    args = p.parse_args(argv)

    target = pathlib.Path(args.file_path)
    if not target.exists():
        print(f"ERROR: target does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_file():
        print(f"ERROR: target is not a file: {target}", file=sys.stderr)
        return 1

    raw = target.read_bytes()
    eol = detect_eol(raw)
    eol_label = "crlf" if eol == b"\r\n" else "lf"

    if args.content is not None:
        content_bytes = args.content.encode("utf-8")
    else:
        content_bytes = pathlib.Path(args.content_file).read_bytes()

    payload = normalize_to_eol(content_bytes, eol)

    # If the existing file doesn't end with a newline, prepend one so the appended
    # block doesn't graft onto the last line.
    if args.ensure_leading_newline and raw and not raw.endswith(eol):
        payload = eol + payload

    append_atomic(target, payload)

    print(f"appended {len(payload)} bytes preserving EOL={eol_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
