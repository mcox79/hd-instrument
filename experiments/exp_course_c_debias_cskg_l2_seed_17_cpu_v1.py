"""Degree-debiased fair re-scoring of the Course-C rotation win, seed 17 (REMOTE CPU, process-isolated).
Refits ONLY ONESHOT_ROTATE (+ recomputes POP) on the reproduced seed-17 split, then computes the degree-debiased
diagnostics (within-stratum / partial correlation + degree-matched candidate margin) against the archived
gpu1024 seed-17 reference. CPU-forced (task lock: no GPU) -> cross-device from the CUDA archive, so ONESHOT
faithfulness is a tolerance check while POP + split identity are the device-independent HARD gates. See
experiments/_course_c_debias_core_v1.py for the full design. ASCII-only."""

import os
import sys

os.environ.setdefault("HDLAB_DEVICE", "cpu")  # force CPU on the remote host (which also has a GPU); no-GPU lock

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._course_c_debias_core_v1 import wrapper_run  # noqa: E402
from experiments._seed_checkpoint import get_output_dir as _sc_gate  # noqa: E402,F401  PROT-021: fit-checkpoint resumability wired in core
# Belt-and-suspenders for remote dispatch: expose the transitive core deps to queue_add.sh's Pattern-6
# import-parser so they are force-SCPed fresh (guards against remote repo drift). Already imported by the core.
from experiments import (  # noqa: E402,F401
    _course_c_rotate_core_v1, exp_course_c_map_builder_cskg_l2_genuine_v1,
    exp_gt_induction_fb15k237_dense_v1, exp_cskg_dense_core_headroom_acceptance_v1,
)

ANCHOR_NAME = "course_c_debias_cskg_l2_seed_17_cpu_v1"
SEEDS = [17]
DEFAULT_RUN_MODE = "full"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
