"""PARALLEL GPU shot (seed 17, fpe_dim=1024) for the decisive ROTATION-score reasoning cell. Identical recipe
to exp_course_c_rotate_cskg_l2_seed_17_v1 EXCEPT the SECONDARY FPE-readout projection dim is reduced 4096->1024
via HDLAB_FPE_DIM, set here at import top. The fpe_dim=2048 GPU variant OOM'd at FULL N (the (N, fpe_dim) complex
phasor bank + conj-transpose peaks >8GiB on the 8GiB card at full concept count); halving to 1024 halves that
bank (~1.55GiB driver) so peak fits with margin. fpe_dim reduces ONLY the S_all (N, fpe_dim) phasor bank and is
orthogonal to the KGE embed dim k; the PRIMARY direct-distance win metric is UNAFFECTED. Now RESUMABLE via the
periodic fit-checkpoint in _course_c_rotate_core_v1 (commit c140054e1) so an outage/timeout wastes nothing.
Writes to its own isolated anchor dir; the CPU definitive seeds (default fpe_dim=4096) are untouched. See
experiments/_course_c_rotate_core_v1.py for the full design + PP-275 citation. ASCII-only."""

import os
import sys

import torch  # noqa: F401  top-level GPU-device visibility (torch used via _course_c_rotate_core_v1); routes to overnight_queue

os.environ.setdefault("HDLAB_FPE_DIM", "1024")  # memory-safe GPU fpe_dim at full N; respects an explicit override if pre-set

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._course_c_rotate_core_v1 import wrapper_run  # noqa: E402
from experiments._validity_preflight import run_validity_preflight as _vp_ship  # noqa: E402,F401
from experiments._seed_checkpoint import get_output_dir as _sc_ship  # noqa: E402,F401

ANCHOR_NAME = "course_c_rotate_cskg_l2_seed_17_gpu1024_v1"
SEEDS = [17]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
