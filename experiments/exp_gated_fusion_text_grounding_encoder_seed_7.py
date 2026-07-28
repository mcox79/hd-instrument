"""Wrapper: cash-in the gated_fusion capability on seed_7's saved text+grounding reps.
See experiments/_gated_fusion_text_grounding_encoder_core.py for the full mechanism + docstring.
CHUNKED single-seed-per-cell (exp_dev.md #13): this file = seed 7 ONLY. Sibling: _seed_13.py.
"""
import os
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _gated_fusion_text_grounding_encoder_core as _core

SEED = 7
ANCHOR_NAME = "gated_fusion_text_grounding_encoder_seed_7"

if __name__ == "__main__":
    _core.main(SEED, ANCHOR_NAME)
