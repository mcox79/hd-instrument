"""Wrapper: seed_7 entry-point for cortex2 atom-consultation smoke v1.

Delegates to the core cell (exp_cortex2_atom_consultation_smoke_v1_core.py).
Kept as a separate file to match the CHUNKED single-seed-per-cell convention
(META_RULE_13) even though this probe is stateless and single-seed by design.
Downstream tooling (runner_status, verify_landing) scans for `_s<seed>.py`
suffix; a wrapper keeps that convention.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_CORE = Path(__file__).resolve().parent / "exp_cortex2_atom_consultation_smoke_v1_core.py"

if __name__ == "__main__":
    # Re-exec the core cell with the same argv (--self-test / --smoke / --full).
    sys.argv[0] = str(_CORE)
    runpy.run_path(str(_CORE), run_name="__main__")
