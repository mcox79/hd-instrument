"""belief_timeline core PROMOTED 2026-08-30 -> hdlab/belief_timeline.py.

Thin re-export so verification/test_belief_timeline.py and the exp_belief_timeline_* cells import
the SAME promoted core (no two-copy drift). The organ lives in hdlab now; this file is the
experiment-side alias.
"""
from hdlab.belief_timeline import *          # noqa: F401,F403
from hdlab import belief_timeline as _bt
import sys as _sys

_self = _sys.modules[__name__]
for _n in dir(_bt):
    if not _n.startswith("__") and not hasattr(_self, _n):
        setattr(_self, _n, getattr(_bt, _n))
