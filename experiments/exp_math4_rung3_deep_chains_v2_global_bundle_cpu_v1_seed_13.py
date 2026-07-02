"""math4_rung3_deep_chains_v2_global_bundle_cpu_v1 seed=13 entry point.

Pre-reg: preregs/2026-07_math4_rung3_deep_chains_v2_global_bundle_cpu_v1.md
Core: exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1.py

Sets HDLAB_SEED then runs the core (single-file cell reads HDLAB_SEED env at
module init). Runner does not inject per-entry env; this wrapper is the
standard per-META_RULE_H CHUNKED single-seed-per-cell convention.

ASCII only.
"""
from __future__ import annotations

import os
os.environ["HDLAB_SEED"] = "13"

import torch  # PROT-020 GPU-queue routing gate marker; core cell also imports torch
import runpy
from pathlib import Path

_CORE = Path(__file__).with_name("exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1.py")
runpy.run_path(str(_CORE), run_name="__main__")
