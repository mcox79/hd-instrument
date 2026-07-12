"""FULL seed-7 wrapper for the decisive ROTATION-score reasoning cell (per-seed PROCESS isolation; section-13
chunked single-seed-per-cell + OOM discipline). All design, arms, bands, self-test, and the PP-275
rotation-primitive citation live in experiments/_course_c_rotate_core_v1.py. Runner invokes with no argv ->
run_mode defaults to full (section-16 run_mode-verification safe). ASCII-only."""

import os
import sys

import torch  # noqa: F401  top-level GPU-device visibility (torch used via _course_c_rotate_core_v1); routes to overnight_queue

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# queue_add Pattern-6 (AST import parse) ships the core; Pattern-5 ships the shared framework modules the
# core needs (these direct imports are the ship-triggers even though the wrapper only calls wrapper_run).
from experiments._course_c_rotate_core_v1 import wrapper_run  # noqa: E402
from experiments._validity_preflight import run_validity_preflight as _vp_ship  # noqa: E402,F401
from experiments._seed_checkpoint import get_output_dir as _sc_ship  # noqa: E402,F401

ANCHOR_NAME = "course_c_rotate_cskg_l2_seed_7_v1"
SEEDS = [7]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
