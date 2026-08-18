"""substrate_narrative_q2_recency_sequence_log_v1 -- seed=13 chunk.

Chunked sibling for 3-seed full run. Thin shim that sets HDLAB_SEED=13 then
delegates to _q2_recency_sequence_log_v1_impl module.

Per drill `notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md`
and handoff Anchor 1.

PREREG: preregs/2026-06-28_substrate_narrative_q2_recency_sequence_log_v1.md

ASCII-only. CPU.
"""
import os
import sys

os.environ["HDLAB_SEED"] = "13"

ANCHOR_NAME = "substrate_narrative_q2_recency_sequence_log_v1"

from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._q2_recency_sequence_log_v1_impl import main as _impl_main

if __name__ == "__main__":
    raise SystemExit(_impl_main())
