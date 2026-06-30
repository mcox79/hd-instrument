"""Seed=13 wrapper for substrate_higher_order_tom_recursive_v5_d5_isolated.

ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "exp_substrate_higher_order_tom_recursive_v5_d5_isolated.py")
if not os.path.exists(CORE):
    print(f"FATAL: core cell not found at {CORE}", file=sys.stderr)
    sys.exit(2)

if not any(a == "--seed" for a in sys.argv):
    sys.argv.extend(["--seed", "13"])

with open(CORE, "r", encoding="utf-8") as f:
    code = f.read()
exec(compile(code, CORE, "exec"), {"__name__": "__main__", "__file__": CORE})
