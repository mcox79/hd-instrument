"""sharded_fhrr_topology_free_multi_f_dag_v1 seed=13 entry point.

Pre-reg: preregs/2026-07-02_sharded_fhrr_topology_free_multi_f_dag_v1.md
Core: exp_sharded_fhrr_topology_free_multi_f_dag_v1.py

ASCII only.
"""
from __future__ import annotations

import os
os.environ["HDLAB_SEED"] = "13"

import torch  # PROT-020 GPU-queue routing gate marker
import runpy
from pathlib import Path

_CORE = Path(__file__).with_name("exp_sharded_fhrr_topology_free_multi_f_dag_v1.py")
runpy.run_path(str(_CORE), run_name="__main__")
