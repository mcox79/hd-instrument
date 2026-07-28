"""Wrapper: cash-in the gated_fusion capability on seed_13's saved text+grounding reps.
See experiments/_gated_fusion_text_grounding_encoder_core.py for the full mechanism + docstring.
CHUNKED single-seed-per-cell (exp_dev.md #13): this file = seed 13 ONLY. Sibling: _seed_7.py.
DO NOT dispatch until data/exp_scale_meaning_learn_arc_heldout_v3_grounding/evalreps_seed_13.npz
has landed (the grounding cell's seed_13 GPU run was still in progress at authoring time) -- the
core's run_one_seed() raises FileNotFoundError (failure_class=NPZ_NOT_LANDED) loud rather than
silently waiting if dispatched too early.
"""
import os
import sys

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _gated_fusion_text_grounding_encoder_core as _core

SEED = 13
ANCHOR_NAME = "gated_fusion_text_grounding_encoder_seed_13"

if __name__ == "__main__":
    _core.main(SEED, ANCHOR_NAME)
