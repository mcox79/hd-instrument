"""substrate_narrative_q2_recency_sequence_log_v1 -- seed=7 chunk.

Chunked sibling for 3-seed full run. Thin shim that sets HDLAB_SEED=7 then
delegates to _q2_recency_sequence_log_v1_impl module.

Per drill `notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md`
and handoff Anchor 1.

PREREG: preregs/2026-06-28_substrate_narrative_q2_recency_sequence_log_v1.md

ASCII-only. CPU.
"""
import os
import sys

# Set seed BEFORE importing the impl module (module reads HDLAB_SEED at import)
os.environ["HDLAB_SEED"] = "7"

# Re-export ANCHOR for tooling that inspects this file
ANCHOR_NAME = "substrate_narrative_q2_recency_sequence_log_v1"

# Defer all heavy work to impl
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._q2_recency_sequence_log_v1_impl import main as _impl_main

if __name__ == "__main__":
    raise SystemExit(_impl_main())
