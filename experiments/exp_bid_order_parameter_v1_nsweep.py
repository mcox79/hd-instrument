"""BID order parameter N-sweep v1 -- wrapper for HP3 stability gate.

This is a thin wrapper around exp_bid_order_parameter_v1 that forces --n-sweep mode.
It tests BID stability across N in {1024, 2048, 4096} to gate HP3 (thermodynamic
quantity vs finite-N artifact).

Pre-reg: preregs/2026-05-27_bid_order_parameter_v1_nsweep.md
Queue: remote_cpu_queue
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import the parent module to inherit _instrumentation_selftest at module scope.
# The selftest runs when the parent module is imported.
import importlib.util

_parent_spec = importlib.util.spec_from_file_location(
    "exp_bid_order_parameter_v1",
    str(REPO / "experiments" / "exp_bid_order_parameter_v1.py"),
)
_parent = importlib.util.module_from_spec(_parent_spec)
# Temporarily suppress argv to avoid triggering argparse in the parent
_saved_argv = sys.argv
sys.argv = [sys.argv[0], "--self-test"]
_parent_spec.loader.exec_module(_parent)  # This runs _instrumentation_selftest() at module scope
sys.argv = _saved_argv

# Re-export the main function
main_with_nsweep = _parent.main


def main():
    parser = argparse.ArgumentParser(description="BID N-sweep wrapper (forces --n-sweep)")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)  # selftests already ran at module scope above

    # Force n-sweep mode: inject --n-sweep into argv before calling parent main
    # The parent reads sys.argv via argparse
    if args.smoke:
        sys.argv = [sys.argv[0], "--smoke", "--n-sweep"]
    else:
        sys.argv = [sys.argv[0], "--n-sweep"]

    main_with_nsweep()


if __name__ == "__main__":
    main()
