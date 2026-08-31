"""Re-export shim -> hdlab.force_dynamics_lexicon (promoted 2026-08-31)."""
from hdlab.force_dynamics_lexicon import *  # noqa: F401,F403
from hdlab.force_dynamics_lexicon import (  # noqa: F401
    build_force_lexicon, force_dynamic_type, detect_endstate_reached,
    _lemmatize_lu, CACHE_DIR, CACHE_PATH,
    CAUSE_FRAMES, PREVENT_FRAMES, PREVENT_FRAMES_SWEEP_EXTRA, MIXED_FRAMES,
    ENABLE_LUS, NARRATIVE_BACKOFF, NEG_CUES, POS_REACHED_HINTS,
)
