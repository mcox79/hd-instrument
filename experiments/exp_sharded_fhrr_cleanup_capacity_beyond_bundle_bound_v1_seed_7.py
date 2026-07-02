"""sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1 seed=7 entry point.

Pre-reg: preregs/2026-07-02_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.md
Core: exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py

Sets HDLAB_SEED then runs the core (single-file cell reads HDLAB_SEED env at
module init line 65). Runner does not inject per-entry env; this wrapper is
the standard per-META_RULE_H CHUNKED single-seed-per-cell convention.

ASCII only.
"""
from __future__ import annotations

import os
os.environ["HDLAB_SEED"] = "7"

import runpy
from pathlib import Path

_CORE = Path(__file__).with_name("exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py")
runpy.run_path(str(_CORE), run_name="__main__")
