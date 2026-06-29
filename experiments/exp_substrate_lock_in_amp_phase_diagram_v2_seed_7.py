# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""Seed=7 wrapper for substrate_lock_in_amp_phase_diagram_v2.

Forces SEED_DEFAULT=7 via env var BEFORE importing the core cell module.

ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations

import os
import sys

os.environ["HDLAB_SEED_OVERRIDE"] = "7"

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "exp_substrate_lock_in_amp_phase_diagram_v2.py")
if not os.path.exists(CORE):
    print(f"FATAL: core cell not found at {CORE}", file=sys.stderr)
    sys.exit(2)

with open(CORE, "r", encoding="utf-8") as f:
    code = f.read()
exec(compile(code, CORE, "exec"), {"__name__": "__main__", "__file__": CORE})
