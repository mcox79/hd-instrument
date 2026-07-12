"""GPU MEMORY SMOKE (>=2 seeds) for the decisive ROTATION cell. Runs at FULL memory footprint (full N +
fpe_dim + n_neg + the FPE-median readout = the OOM driver) but few epochs + 2 seeds IN-PROCESS, so it proves
no CUDA OOM and that per-seed empty_cache holds across seeds (the family OOM'd 3x) BEFORE the multi-hour FULL.
Route to overnight_queue (GPU) so it actually exercises the CUDA memory path. See
experiments/_course_c_rotate_core_v1.py for the full design. ASCII-only."""

import os
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._course_c_rotate_core_v1 import wrapper_run  # noqa: E402
from experiments._validity_preflight import run_validity_preflight as _vp_ship  # noqa: E402,F401
from experiments._seed_checkpoint import get_output_dir as _sc_ship  # noqa: E402,F401

ANCHOR_NAME = "course_c_rotate_cskg_l2_memsmoke_v1"
SEEDS = [7, 17]
DEFAULT_RUN_MODE = "memsmoke"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
