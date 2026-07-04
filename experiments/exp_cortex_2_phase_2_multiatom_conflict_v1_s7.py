"""Wrapper: seed_7 entry-point for cortex_2 Phase 2 multi-atom conflict v1.

Delegates to `exp_cortex_2_phase_2_multiatom_conflict_v1_core.py`.
Kept as a separate file to match the CHUNKED single-seed-per-cell convention
(META_RULE_13) even though this probe is stateless and single-seed by design.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_CORE = Path(__file__).resolve().parent / "exp_cortex_2_phase_2_multiatom_conflict_v1_core.py"

if __name__ == "__main__":
    sys.argv[0] = str(_CORE)
    runpy.run_path(str(_CORE), run_name="__main__")
