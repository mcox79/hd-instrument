# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC sibling seed=19.

Thin wrapper: sets HDLAB_SEED_OVERRIDE=19, then exec()s the core cell.
Per-seed-sibling dispatch convention (one dir per seed; lets
aggregate_partials reconstruct full ensemble after merge).

Sibling pair: seed_7, seed_13.

Authored by hdi_orchestrator 2026-06-28 because the core cell consumes
seed via env-var (HDLAB_SEED_OVERRIDE) but the queue runner does not
forward env-vars from queue_add; per-sibling wrapper is the established
dispatch pattern (see substrate_pc_encoder_family_phase_diagram_v1_seed_*).

ASCII-only.
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

SEED = 19
os.environ["HDLAB_SEED_OVERRIDE"] = str(SEED)

CORE = (
    Path(__file__).parent
    / "exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC.py"
)

if __name__ == "__main__":
    runpy.run_path(str(CORE), run_name="__main__")
