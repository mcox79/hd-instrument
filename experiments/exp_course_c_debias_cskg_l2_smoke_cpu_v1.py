"""SMOKE (small CSKG core, 2-seed) for the degree-debiased Course-C re-scoring. Exercises the FULL on-DATA path
end-to-end at reduced scale (SMOKE_CFG: k_core=3, max_nodes=3000, epochs=120, n_eval=2000) BEFORE the multi-hour
FULL seeds: proves the debias diagnostics (within-stratum / partial r + degree-matched candidate masking + POP
degree-matched ranking) run on real CSKG degree distributions without the archived-reference identity gate
(SMOKE has no archive). CPU-forced. See experiments/_course_c_debias_core_v1.py. ASCII-only."""

import os
import sys

os.environ.setdefault("HDLAB_DEVICE", "cpu")

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._course_c_debias_core_v1 import wrapper_run  # noqa: E402
# Belt-and-suspenders for remote dispatch: expose the transitive core deps to queue_add.sh's Pattern-6
# import-parser so they are force-SCPed fresh (guards against remote repo drift). Already imported by the core.
from experiments import (  # noqa: E402,F401
    _course_c_rotate_core_v1, exp_course_c_map_builder_cskg_l2_genuine_v1,
    exp_gt_induction_fb15k237_dense_v1, exp_cskg_dense_core_headroom_acceptance_v1,
)

ANCHOR_NAME = "course_c_debias_cskg_l2_smoke_cpu_v1"
SEEDS = [7, 17]
DEFAULT_RUN_MODE = "smoke"

if __name__ == "__main__":
    wrapper_run(ANCHOR_NAME, SEEDS, DEFAULT_RUN_MODE)
