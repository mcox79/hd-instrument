"""encoder_cocktail_composition_v1 seed=7 entry point.

Pre-reg: preregs/2026-07-01_encoder_cocktail_composition_v1.md
Shared core: experiments/_encoder_cocktail_composition_v1_core.py
ASCII only.
"""
from __future__ import annotations

import sys

from _encoder_cocktail_composition_v1_core import ANCHOR_NAME_BASE, cell_main

ANCHOR_NAME = ANCHOR_NAME_BASE  # dispatch anchor slug (seed suffix in dir name)


if __name__ == "__main__":
    sys.exit(cell_main(ANCHOR_NAME, seed=7, argv=sys.argv[1:]))
