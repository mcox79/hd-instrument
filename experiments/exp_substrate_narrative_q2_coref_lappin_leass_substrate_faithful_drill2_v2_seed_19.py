"""substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2 -- seed=19 chunk."""
import os
import sys

os.environ["HDLAB_SEED"] = "19"

ANCHOR_NAME = "substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2"

from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._q2_lappin_leass_drill2_v2_impl import main as _impl_main

if __name__ == "__main__":
    raise SystemExit(_impl_main())
