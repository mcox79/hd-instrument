"""substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2 -- seed=7 chunk.

DRILL 2 v2 (substrate-faithful post Skunkworks invalidation f60880f7 of v1).

Chunked sibling for 3-seed full run. Thin shim that sets HDLAB_SEED=7 then
delegates to _q2_lappin_leass_drill2_v2_impl module.

PREREG: preregs/2026-06-28_substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2.md
Prior:
  - drill 1 (HARD_FAIL): substrate_narrative_q2_recency_sequence_log_v1
  - drill 2 v1 (INVALID): substrate_narrative_q2_coref_lappin_leass_drill2_v1 (oracle leak)

ASCII-only. CPU. numpy only.
"""
import os
import sys

os.environ["HDLAB_SEED"] = "7"

ANCHOR_NAME = "substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2"

from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._q2_lappin_leass_drill2_v2_impl import main as _impl_main

if __name__ == "__main__":
    raise SystemExit(_impl_main())
