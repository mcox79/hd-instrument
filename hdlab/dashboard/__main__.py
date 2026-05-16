"""CLI entry point: python -m hdlab.dashboard --trace <path> --output <pdf>."""

from __future__ import annotations

import argparse
from pathlib import Path

from hdlab import store
from hdlab.dashboard.report import generate_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PDF dashboard from a TraceStore.")
    parser.add_argument("--trace", type=Path, required=True, help="Path to DuckDB trace file")
    parser.add_argument("--output", type=Path, default=None, help="Output PDF (default: <trace>.pdf)")
    parser.add_argument("--name", type=str, default="session", help="Run name shown in the report header")
    args = parser.parse_args()

    output = args.output or args.trace.with_suffix(".pdf")
    with store.TraceStore(args.trace) as ts:
        events = ts.all_events()
    out = generate_report(events, output, run_name=args.name)
    print(f"Wrote: {out} ({len(events)} events)")


if __name__ == "__main__":
    main()
