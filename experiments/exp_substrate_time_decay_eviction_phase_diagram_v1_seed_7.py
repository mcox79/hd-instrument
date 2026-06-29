# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""Seed=7 wrapper for substrate_time_decay_eviction_phase_diagram_v1.

Forces SEED_DEFAULT=7 via env var BEFORE importing the core cell module.
The runner sets HDLAB_EXP_NAME to this script's entry name; the core uses
get_output_dir(ANCHOR_NAME) which honors HDLAB_EXP_NAME.

ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations

import os
import sys

# Force seed BEFORE the core module imports it.
os.environ["HDLAB_SEED_OVERRIDE"] = "7"

# Run the core cell as if it were the main module.
HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "exp_substrate_time_decay_eviction_phase_diagram_v1.py")
if not os.path.exists(CORE):
    print(f"FATAL: core cell not found at {CORE}", file=sys.stderr)
    sys.exit(2)

# Execute core in __main__ scope so its top-level runner runs.
with open(CORE, "r", encoding="utf-8") as f:
    code = f.read()
exec(compile(code, CORE, "exec"), {"__name__": "__main__", "__file__": CORE})
