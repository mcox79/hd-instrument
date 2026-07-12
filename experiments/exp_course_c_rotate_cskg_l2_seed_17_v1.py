"""FULL seed-17 wrapper for the decisive ROTATION-score reasoning cell (per-seed PROCESS isolation). See
experiments/_course_c_rotate_core_v1.py for the full design + PP-275 rotation-primitive citation. ASCII-only."""

import os
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._course_c_rotate_core_v1 import wrapper_run  # noqa: E402
from experiments._validity_preflight import run_validity_preflight as _vp_ship  # noqa: E402,F401
from experiments._seed_checkpoint import get_output_dir as _sc_ship  # noqa: E402,F401

ANCHOR_NAME = "course_c_rotate_cskg_l2_seed_17_v1"
SEEDS = [17]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
